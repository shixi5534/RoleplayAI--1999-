/*
 * index.js —— 桌面宠物主进程入口
 *
 * 职责：单实例锁 · 权限白名单 · IPC 注册 · 窗口创建 · 后端探活/拉起 · 全局状态推送。
 * 宠物渲染进程 = 网页版自己的 pet.html（同源，全部业务逻辑在网页版）。
 */
"use strict";

const path = require("path");
const fs = require("fs");
const { app, BrowserWindow, ipcMain, session, globalShortcut, dialog, screen } = require("electron");

// ── EPIPE 免疫：从带管道的终端启动（或管道被关闭）时，console 写入会抛 broken pipe ──
// 导致主进程崩溃。包装 console 并吞掉 stdio error，保证日志写入永不抛异常。
for (const m of ["log", "info", "warn", "error"]) {
  const orig = console[m];
  console[m] = function (...args) {
    try { orig.apply(console, args); } catch (_) { /* 管道断开：静默丢弃 */ }
  };
}
if (process.stdout && process.stdout.on) process.stdout.on("error", () => {});
if (process.stderr && process.stderr.on) process.stderr.on("error", () => {});

// ── 主进程未捕获异常：落盘 userData/pet-crash.log 便于排查（随后退出，避免僵死 Error 弹窗） ──
process.on("uncaughtException", (e) => {
  try {
    const dir = app.getPath("userData");
    fs.mkdirSync(dir, { recursive: true });
    fs.appendFileSync(
      path.join(dir, "pet-crash.log"),
      "[" + new Date().toISOString() + "] " + (e && e.stack ? e.stack : String(e)) + "\n\n",
      "utf8"
    );
  } catch (_) {}
  app.quit();
});
const { loadConfig, saveConfig } = require("./config");
const { createPetWindow, loadPetPage, loadFallback, pushBackendState, getBackendState, moveBy, setPetSize, setModelBounds, listDisplays, moveToDisplay, resetPosition, createSettingsWindow, getPetWindow, defaultPosition } = require("./windows");
const { startBackend, pollBackend } = require("./backend");
const { createPhysics } = require("./physics");
const { createWalker } = require("./behavior");

// ── IPC 发送者校验：只接受宠物窗/设置窗（本地页面）发来的消息 ──
function isTrustedIpcSender(event) {
  const frame = event && event.senderFrame;
  let url = (frame && frame.url) || "";
  if (!url && event && event.sender && typeof event.sender.getURL === "function") {
    url = event.sender.getURL() || "";
  }
  return (
    url.startsWith("http://127.0.0.1:") ||
    url.startsWith("http://localhost:") ||
    url.startsWith("file:")
  );
}

function onTrusted(channel, listener) {
  ipcMain.on(channel, (event, ...args) => {
    if (!isTrustedIpcSender(event)) {
      console.warn("[ipc] 拒绝不可信发送者的消息:", channel);
      return;
    }
    listener(event, ...args);
  });
}

function handleTrusted(channel, listener) {
  ipcMain.handle(channel, (event, ...args) => {
    if (!isTrustedIpcSender(event)) {
      throw new Error("IPC 发送者不可信");
    }
    return listener(event, ...args);
  });
}

// ── 单实例：二次启动时聚焦已有宠物窗 ──
const gotLock = app.requestSingleInstanceLock();
if (!gotLock) {
  app.quit();
} else {
  // P4：roleplaypet:// 协议注册（网页按钮唤起）
  if (process.defaultApp) {
    if (process.argv.length >= 2) {
      app.setAsDefaultProtocolClient("roleplaypet", process.execPath, [path.resolve(process.argv[1])]);
    }
  } else {
    app.setAsDefaultProtocolClient("roleplaypet");
  }

  app.on("second-instance", (_e, argv) => {
    const win = getPetWindow();
    if (win && !win.isDestroyed()) {
      win.show();
      win.focus();
    }
    // roleplaypet://launch 经浏览器二次启动 → 同样视为唤起
    const url = (argv || []).find((a) => String(a).startsWith("roleplaypet://"));
    if (url) console.info("[protocol] 唤起:", url);
  });

  app.whenReady().then(async () => {
    const cfg = loadConfig();

    // ── 安全：权限只放行麦克风（录音），其余一律拒绝 ──
    session.defaultSession.setPermissionRequestHandler((_wc, permission, cb) => {
      cb(permission === "media");
    });
    // 兜底：主进程网络仅回环（后续 P3 截图/OCR 也遵守此约定）
    session.defaultSession.webRequest.onBeforeRequest({ urls: ["*://*/*"] }, (details, cb) => {
      let host = "";
      try { host = new URL(details.url).hostname; } catch (_) {}
      const loopback = host === "127.0.0.1" || host === "localhost" || host === "::1" || host === "[::1]";
      cb({ cancel: !loopback });
    });

    // ── 宠物窗（后端未启动时先显示 fallback 引导页） ──
    createPetWindow(cfg);

    // ── P2：拖拽动量物理 + 自主漫步调度 ──
    const physics = createPhysics(getPetWindow());
    const walker = createWalker(getPetWindow(), cfg);
    walker.start();

    // ── P3：屏幕识别（截图 + 本地 OCR → 渲染层发评论） ──
    const { setup: setupOcr } = require("./ocr");
    setupOcr(cfg, (result) => {
      const win = getPetWindow();
      if (win && !win.isDestroyed()) {
        win.webContents.send("pet:ocr-result", { text: result.text });
      }
    });

    // ── P4：回环控制服务（网页按钮探测/唤起/指令） ──
    const { createControlServer } = require("./control-server");
    createControlServer(cfg, {
      onLaunch() {
        const win = getPetWindow();
        if (win && !win.isDestroyed()) {
          win.show();
          win.setAlwaysOnTop(true, loadConfig().pet.alwaysOnTopLevel || "floating");
          // 网页按钮“唤起”同时也唤醒宠物页（睡眠/待机 → 互动动画）
          try { win.webContents.send("pet:wake"); } catch (_) {}
        }
        // 重置主进程漫步计时，避免刚被网页唤起就去散步
        walker.notifyInteract();
        // 从“隐藏宠物”恢复时，若没有锁位/勿扰/忙碌则恢复自主漫步
        const petCfg = loadConfig().pet || {};
        if (busyCount <= 0 && !petCfg.dnd && !petCfg.locked) walker.resume();
      },
      onTalk(text) {
        const win = getPetWindow();
        if (win && !win.isDestroyed()) win.webContents.send("pet:talk", { text });
      },
    });

    // ── P4：按住说话全局快捷键（默认 Alt+Space；按下=开始录音，再按=结束） ──
    function registerPtt() {
      const c = loadConfig();
      const key = (c.ptt && c.ptt.key) || "Alt+Space";
      try {
        const ok = globalShortcut.register(key, () => {
          const win = getPetWindow();
          if (win && !win.isDestroyed()) win.webContents.send("pet:ptt", { down: true });
        });
        if (!ok) console.warn("[shortcut] 注册失败（可能被占用）:", key);
      } catch (e) {
        console.warn("[shortcut] 注册异常:", e.message);
      }
    }
    registerPtt();

    // ── IPC：窗口移动 / 拖拽结束 / 互动通知 / 忙碌状态 / 退出 / 设置 / 配置 ──
    // P2：不再使用 pet:interactive / setIgnoreMouseEvents 穿透切换；
    // hover 命中由 windows.js 的 startHoverWatch 轮询并推送 pet:hover-state。
    let lastMoveByAt = 0;

    /** 把当前窗口位置写回配置（重启后回到原处；仅用户显式摆位/拖拽后调用）。 */
    function persistPosition() {
      const win = getPetWindow();
      if (!win || win.isDestroyed()) return;
      const [x, y] = win.getPosition();
      saveConfig({ pet: { x, y } });
    }

    onTrusted("pet:move-by", (_e, d) => {
      lastMoveByAt = Date.now();
      moveBy(d && d.dx, d && d.dy);
      physics.recordMove(d && d.dx, d && d.dy); // 采样速度供释放后动量使用
    });
    onTrusted("pet:drag-end", () => {
      physics.startMomentum(); // 惯性滑动 + 边缘回弹
      persistPosition();       // 用户摆位 → 持久化（重启恢复）
      walker.notifyInteract(); // 拖拽算一次用户互动
    });
    onTrusted("pet:interact", () => walker.notifyInteract());
    // P2：渲染层上报 Spine 模型 bbox → 主进程 setShape 点击穿透 + hover 精确命中
    onTrusted("pet:model-bounds", (_e, bounds) => setModelBounds(bounds));

    // 忙碌引用计数：对话/录音/拖拽可能叠加（如录音中再发消息），
    // 任一生效即暂停漫步；全部结束且 600ms 无新忙碌才恢复，避免交错时过早乱跑。
    let busyCount = 0;
    let busyResumeTimer = null;
    onTrusted("pet:busy", (_e, busy) => {
      busyCount = Math.max(0, busyCount + (busy ? 1 : -1));
      if (busyResumeTimer) { clearTimeout(busyResumeTimer); busyResumeTimer = null; }
      if (busyCount > 0) {
        walker.pause();
      } else {
        busyResumeTimer = setTimeout(() => {
          busyResumeTimer = null;
          if (busyCount <= 0 && !loadConfig().pet.dnd && !loadConfig().pet.locked) walker.resume();
        }, 600);
      }
    });

    onTrusted("pet:resize", (_e, d) => {
      const r = setPetSize(d && d.w, d && d.h);
      if (r) saveConfig({ pet: { width: r.w, height: r.h } }); // 档位持久化（重启恢复）
    });
    // P1：勿扰 / 锁位（写 config 持久化 + 联动漫步）
    onTrusted("pet:dnd", (_e, dnd) => {
      saveConfig({ pet: { dnd: !!dnd } });
      if (dnd) {
        walker.pause();
        if (busyResumeTimer) { clearTimeout(busyResumeTimer); busyResumeTimer = null; }
      } else if (busyCount <= 0 && !loadConfig().pet.locked) {
        walker.resume();
      }
    });
    onTrusted("pet:locked", (_e, locked) => {
      saveConfig({ pet: { locked: !!locked } });
      // 锁位 = 位置固定：立即停漫步；解锁且无忙碌/勿扰才恢复
      if (locked) walker.pause();
      else if (busyCount <= 0 && !loadConfig().pet.dnd) walker.resume();
    });
    // P1-7：多屏摆位
    handleTrusted("pet:get-displays", () => listDisplays());
    onTrusted("pet:move-to-display", (_e, id) => moveToDisplay(id));
    onTrusted("pet:reset-position", () => resetPosition());

    // P2-6：截图分享（人偶+气泡合成图，经系统保存对话框落盘，零自动保存）
    handleTrusted("pet:export-image", async (_e, dataUrl) => {
      const win = getPetWindow();
      try {
        const r = await dialog.showSaveDialog(win, {
          title: "导出宠物截图",
          defaultPath: "pet-snapshot.png",
          filters: [{ name: "PNG", extensions: ["png"] }],
        });
        if (r.canceled || !r.filePath) return { ok: false, canceled: true };
        const base64 = String(dataUrl || "").split(",")[1] || "";
        fs.writeFileSync(r.filePath, Buffer.from(base64, "base64"));
        return { ok: true, path: r.filePath };
      } catch (e) {
        return { ok: false, error: String(e.message || e) };
      }
    });

    // P2-4：跟随光标（followMode=cursor 时每 200ms lerp；拖拽后 1.5s 内不跟随）
    setInterval(() => {
      const cfg = loadConfig();
      if (cfg.pet.followMode !== "cursor" || cfg.pet.locked) return;
      const win = getPetWindow();
      if (!win || win.isDestroyed() || Date.now() - lastMoveByAt < 1500) return;
      const [w, h] = win.getSize();
      const [x, y] = win.getPosition();
      const pt = screen.getCursorScreenPoint();
      const wa = screen.getDisplayNearestPoint(pt).workArea;
      const tx = Math.max(wa.x, Math.min(pt.x - w - 28, wa.x + wa.width - w));
      const ty = Math.max(wa.y, Math.min(pt.y - h + 60, wa.y + wa.height - h));
      if (Math.hypot(tx - x, ty - y) < 8) return;
      win.setPosition(Math.round(x + (tx - x) * 0.15), Math.round(y + (ty - y) * 0.15));
    }, 200);

    onTrusted("pet:quit", () => app.quit());
    // 隐藏宠物窗口：不退出应用，保留控制服务与后台进程；网页按钮 /launch 可再次 show
    onTrusted("pet:hide", () => {
      const win = getPetWindow();
      if (win && !win.isDestroyed()) {
        win.hide();
        walker.pause(); // 隐藏时暂停自主漫步，避免窗口在后台乱跑
      }
    });
    onTrusted("pet:open-settings", () => createSettingsWindow());
    handleTrusted("pet:get-config", () => loadConfig());
    handleTrusted("pet:set-config", (_e, patch) => saveConfig(patch));
    handleTrusted("backend:get-state", () => getBackendState());
    handleTrusted("backend:launch", async () => {
      await startBackend(loadConfig());
      pushBackendState(getBackendState());
      return getBackendState();
    });

    // ── 后端探活 + 自动拉起（状态推给渲染层） ──
    pollBackend(cfg, (st) => pushBackendState(st)).catch((e) => console.warn("[backend] 轮询异常:", e.message));

    app.on("activate", () => {
      if (BrowserWindow.getAllWindows().length === 0) createPetWindow(loadConfig());
    });

    // 退出前保存窗口位置（配合 pet:drag-end 的持久化，重启回到原处）
    app.on("before-quit", () => {
      try { persistPosition(); } catch (_) {}
    });
  });

  app.on("window-all-closed", () => {
    globalShortcut.unregisterAll();
    app.quit(); // 宠物关闭即退出（托盘形态在 P4 引入）
  });
}
