/*
 * windows.js —— 窗口管理：宠物悬浮窗（透明/无边框/置顶/非穿透 hover 命中）+ 设置窗（P2）
 *
 * 宠物窗加载网页版自己的页面 pet.html（同源复用全部资产与后端接口）。
 * 后端不可用时切换为本地 fallback 引导页，后端恢复后自动切回。
 */
"use strict";

const path = require("path");
const { BrowserWindow, screen, shell } = require("electron");

const FALLBACK_FILE = path.join(__dirname, "..", "renderer", "fallback.html");

let petWin = null;
let settingsWin = null;
let showingFallback = false;
let latestBackendState = null;
let hoverTimer = null;
let lastHoverState = null;
let sizeWatchTimer = null;
let modelShape = null; // setShape 用：模型全动画包络盒（窗口坐标，保守矩形，永不裁到模型像素）
let hoverMask = null;  // hover 命中判定用：alpha 像素矩形（精确，但不参与 setShape 裁渲染）

/**
 * 窗口尺寸看门狗：任何异常路径（渲染器手势缩放、系统 DPI 变化、
 * 切换骨骼时的瞬时布局抖动）都不允许宠物窗偏离配置档位。
 * 每 1s 与 config.pet.width/height 对齐一次，偏差 >2px 才回写，
 * 避免与正常 resize IPC 互相打架。
 */
function startSizeWatchdog(win) {
  if (sizeWatchTimer) clearInterval(sizeWatchTimer);
  sizeWatchTimer = setInterval(() => {
    if (!win || win.isDestroyed()) return;
    try {
      const { loadConfig } = require("./config");
      const cfg = loadConfig();
      const [w, h] = win.getSize();
      if (Math.abs(w - cfg.pet.width) > 2 || Math.abs(h - cfg.pet.height) > 2) {
        win.setSize(Math.round(cfg.pet.width), Math.round(cfg.pet.height), false);
      }
    } catch (_) {}
  }, 1000);
}

function stopSizeWatchdog() {
  if (sizeWatchTimer) {
    clearInterval(sizeWatchTimer);
    sizeWatchTimer = null;
  }
}

/**
 * P2 · PetAI 范式：不使用 setIgnoreMouseEvents 全局穿透。
 * 主进程每 90ms 轮询屏幕光标是否落在宠物窗矩形内，状态变化时经
 * `pet:hover-state` 通知渲染层显隐 UI。宠物窗本身保持可交互，无穿透竞态。
 */
function isPointInBounds(pt, bounds) {
  return (
    pt.x >= bounds.x &&
    pt.x <= bounds.x + bounds.width &&
    pt.y >= bounds.y &&
    pt.y <= bounds.y + bounds.height
  );
}

/**
 * 渲染层上报模型包络盒/alpha 矩形（窗口坐标）后的处理：
 * - setShape 只允许使用「全动画包络盒」这类保守矩形。setShape 在 Windows 上
 *   走 SetWindowRgn，会直接裁剪窗口渲染：若使用跟随逐帧姿态的 alpha 剪影，
 *   形状必然滞后于动画（渲染层 1s 同步一次 + IPC 延迟），动作/待机中超出旧
 *   形状的像素会被系统整块裁掉（表现为模型缺胳膊少头发、像素丢失）。
 *   包络盒覆盖模型所有姿态且与姿态无关，可以安全裁剪窗口外沿。
 * - alpha 矩形（payload.modelRects）只用于 hover 命中判定（不裁渲染），
 *   让悬停在透明孔洞上时不算命中。
 * - 空模型数据时恢复矩形窗口（模型尚未就绪/数据无效）。
 */
function setModelBounds(payload) {
  if (!petWin || petWin.isDestroyed()) return;
  modelShape = null;
  hoverMask = null;
  try {
    const model = payload && payload.model ? payload.model : null;
    const modelRects = payload && Array.isArray(payload.modelRects) ? payload.modelRects : null;
    const uiRects = payload && Array.isArray(payload.ui) ? payload.ui : [];
    const [w, h] = petWin.getSize();
    const shapeRects = [];
    const hoverRects = [];

    const pushRect = (r, sink) => {
      if (!r || !Number.isFinite(r.left) || !Number.isFinite(r.top) ||
          !Number.isFinite(r.width) || !Number.isFinite(r.height) ||
          r.width <= 0 || r.height <= 0) {
        return;
      }
      const left = Math.max(0, Math.min(w, Math.round(Number(r.left) || 0)));
      const top = Math.max(0, Math.min(h, Math.round(Number(r.top) || 0)));
      const right = Math.max(left + 1, Math.min(w, Math.round((Number(r.left) || 0) + (Number(r.width) || 0))));
      const bottom = Math.max(top + 1, Math.min(h, Math.round((Number(r.top) || 0) + (Number(r.height) || 0))));
      sink.push({ x: left, y: top, width: right - left, height: bottom - top });
    };

    // setShape：仅模型包络盒（姿态无关）+ 可见 UI（气泡/菜单/设置/输入条/折叠钮/状态 chip，
    // 后者是全窗浮层，必须并入，否则会被 setShape 裁掉）。
    if (model && Number.isFinite(model.left) && Number.isFinite(model.top) &&
        Number.isFinite(model.width) && Number.isFinite(model.height) &&
        model.width > 0 && model.height > 0) {
      pushRect(model, shapeRects);
    }
    for (const u of uiRects) pushRect(u, shapeRects);

    // hover 判定：用精确 alpha 矩形（拿不到时退回包络盒）；可见 UI 始终并入，
    // 悬停在气泡/菜单上时必须算「在内」，否则 UI 会在光标下被隐藏。
    if (modelRects && modelRects.length) {
      for (const r of modelRects) pushRect(r, hoverRects);
    } else {
      hoverRects.push(...shapeRects);
    }
    for (const u of uiRects) pushRect(u, hoverRects);

    modelShape = shapeRects.length ? shapeRects : null;
    hoverMask = hoverRects.length ? hoverRects : null;
    petWin.setShape(modelShape || []);
  } catch (e) {
    console.warn("[window] setShape 失败（当前平台可能不支持）:", e && e.message);
  }
}

function startHoverWatch(win) {
  if (hoverTimer) clearInterval(hoverTimer);
  lastHoverState = null;
  hoverTimer = setInterval(() => {
    if (!win || win.isDestroyed()) return;
    try {
      const cursor = screen.getCursorScreenPoint();
      const bounds = win.getBounds();
      let inside = isPointInBounds(cursor, bounds);
      // 渲染层已上报 alpha 矩形：hover 也只认真实模型区域，避免透明区仍触发 UI
      if (inside && hoverMask && hoverMask.length) {
        inside = hoverMask.some((r) =>
          cursor.x >= bounds.x + r.x &&
          cursor.x <= bounds.x + r.x + r.width &&
          cursor.y >= bounds.y + r.y &&
          cursor.y <= bounds.y + r.y + r.height
        );
      }
      if (inside !== lastHoverState) {
        lastHoverState = inside;
        win.webContents.send("pet:hover-state", inside);
      }
    } catch (_) {}
  }, 90);
}

function stopHoverWatch() {
  if (hoverTimer) {
    clearInterval(hoverTimer);
    hoverTimer = null;
  }
  lastHoverState = null;
}

/**
 * 主屏右下角初始位置（留边距），null=由系统摆放。
 * 存盘位置若因显示器变更失效（拔屏/分辨率变化），钳制到最近显示器工作区内。
 */
function defaultPosition(cfg) {
  let x = cfg.pet.x;
  let y = cfg.pet.y;
  const wa = screen.getPrimaryDisplay().workArea;
  if (x == null || y == null) {
    x = wa.x + wa.width - cfg.pet.width - 24;
    y = wa.y + wa.height - cfg.pet.height - 24;
  }
  const d = screen.getDisplayNearestPoint({ x, y });
  const w = d.workArea;
  return {
    x: Math.max(w.x, Math.min(Math.round(x), w.x + w.width - cfg.pet.width)),
    y: Math.max(w.y, Math.min(Math.round(y), w.y + w.height - cfg.pet.height)),
  };
}

function createPetWindow(cfg) {
  const preload = path.join(__dirname, "..", "preload", "pet.js");
  const pos = defaultPosition(cfg);
  petWin = new BrowserWindow({
    width: cfg.pet.width,
    height: cfg.pet.height,
    x: pos.x,
    y: pos.y,
    transparent: true,          // 悬浮窗关键：窗口透明
    frame: false,               // 无边框
    alwaysOnTop: true,          // 始终置顶
    skipTaskbar: true,          // 不占任务栏
    hasShadow: false,
    resizable: false,
    maximizable: false,
    fullscreenable: false,
    show: false,
    webPreferences: {
      preload,
      contextIsolation: true,
      sandbox: true,
      nodeIntegration: false,
      spellcheck: false,
    },
  });

  // P2：窗口保持非穿透（默认），由 startHoverWatch 主进程轮询 hover 命中。
  startHoverWatch(petWin);
  startSizeWatchdog(petWin);
  petWin.setAlwaysOnTop(true, cfg.pet.alwaysOnTopLevel || "floating");

  // 安全：禁止导航离开本地页面、禁止新窗口
  petWin.webContents.setWindowOpenHandler(() => ({ action: "deny" }));
  petWin.webContents.on("will-navigate", (e, url) => {
    const ok = url.startsWith("http://127.0.0.1:") || url.startsWith("http://localhost:");
    if (!ok) e.preventDefault();
  });

  // 后端挂掉时切 fallback；恢复时切回 pet.html
  petWin.webContents.on(
    "did-fail-load",
    (_e, code, desc, url) => {
      if (code === -3) return; // ABORTED（正常切换）
      console.warn("[window] 加载失败", code, desc, url);
      loadFallback();
    }
  );

  // 页面 zoom 必须永远保持 1：触屏长按/快捷键导致 zoomFactor 偏离会让整个宠物“变大”。
  petWin.webContents.on("did-finish-load", () => {
    try {
      if (Math.abs(petWin.webContents.getZoomFactor() - 1) > 0.01) petWin.webContents.setZoomFactor(1);
    } catch (_) {}
  });

  petWin.once("ready-to-show", () => petWin.show());
  petWin.on("closed", () => {
    petWin = null;
    stopHoverWatch();
    stopSizeWatchdog();
  });

  loadPetPage();
  return petWin;
}

function loadPetPage() {
  if (!petWin) return;
  const { loadConfig } = require("./config");
  const cfg = loadConfig();
  showingFallback = false;
  petWin.loadURL(cfg.petUrl).catch((err) => {
    console.warn("[window] petUrl 加载失败，切 fallback:", err.message);
    loadFallback();
  });
}

function loadFallback() {
  if (!petWin || showingFallback) return;
  showingFallback = true;
  // fallback 是全窗 UI，必须恢复矩形可点击区域，否则残留的模型 bbox 会切掉按钮
  modelShape = null;
  try { petWin.setShape([]); } catch (_) {}
  petWin.loadFile(FALLBACK_FILE).catch((err) => console.warn("[window] fallback 加载失败:", err.message));
}

/** 后端状态推送（pet 页与 fallback 页共用）。 */
function pushBackendState(state) {
  latestBackendState = state;
  if (petWin && !petWin.isDestroyed()) {
    petWin.webContents.send("backend:state", state);
  }
  // 后端恢复且当前在 fallback → 自动切回宠物页
  if (state && state.ok && showingFallback) loadPetPage();
}

function getBackendState() {
  return latestBackendState;
}

/** 按增量移动窗口（渲染层 live2d:drag 事件驱动）。锁位时 no-op（P1-4）。 */
function moveBy(dx, dy) {
  if (!petWin || petWin.isDestroyed()) return;
  const { loadConfig } = require("./config");
  if (loadConfig().pet.locked) return; // 锁位守卫
  const [x, y] = petWin.getPosition();
  petWin.setPosition(Math.round(x + (Number(dx) || 0)), Math.round(y + (Number(dy) || 0)));
}

/**
 * P0-T4：窗口档位缩放（钳制 320×420 ~ 480×640）。
 * 返回钳制后的 {w,h}（供调用方持久化），窗口不存在返回 false。
 */
function setPetSize(w, h) {
  if (!petWin || petWin.isDestroyed()) return false;
  const cw = Math.max(320, Math.min(480, Math.round(Number(w) || 320)));
  const ch = Math.max(420, Math.min(640, Math.round(Number(h) || 420)));
  petWin.setSize(cw, ch, false);
  return { w: cw, h: ch };
}

/** P1-7：显示器列表摘要（仅本地 screen API，不外传）。 */
function listDisplays() {
  const primary = screen.getPrimaryDisplay();
  return screen.getAllDisplays().map((d, i) => ({
    id: String(d.id),
    label: "显示器 " + (i + 1),
    primary: d.id === primary.id,
    bounds: { x: d.bounds.x, y: d.bounds.y, width: d.bounds.width, height: d.bounds.height },
    workArea: { x: d.workArea.x, y: d.workArea.y, width: d.workArea.width, height: d.workArea.height },
  }));
}

/** 当前窗口位置写回配置（用户显式摆位后调用；漫步/动量移动不调用）。 */
function persistPosition() {
  try {
    if (!petWin || petWin.isDestroyed()) return;
    const { saveConfig } = require("./config");
    const [x, y] = petWin.getPosition();
    saveConfig({ pet: { x, y } });
  } catch (_) {}
}

/** P1-7：把宠物窗摆到指定显示器工作区右下角。 */
function moveToDisplay(displayId) {
  if (!petWin || petWin.isDestroyed()) return false;
  const d = screen.getAllDisplays().find((x) => String(x.id) === String(displayId));
  if (!d) return false;
  const wa = d.workArea;
  const [w, h] = petWin.getSize();
  petWin.setPosition(Math.round(wa.x + wa.width - w - 24), Math.round(wa.y + wa.height - h - 24));
  persistPosition(); // 显式摆位 → 持久化
  return true;
}

/** P1-7：回到默认位置（主屏右下角）。 */
function resetPosition() {
  if (!petWin || petWin.isDestroyed()) return;
  const { loadConfig } = require("./config");
  const pos = defaultPosition(loadConfig());
  petWin.setPosition(pos.x, pos.y);
  persistPosition(); // 显式摆位 → 持久化
}

function createSettingsWindow() {
  if (settingsWin && !settingsWin.isDestroyed()) {
    settingsWin.focus();
    return settingsWin;
  }
  settingsWin = new BrowserWindow({
    width: 520,
    height: 640,
    title: "桌面宠物 · 设置",
    autoHideMenuBar: true,
    backgroundColor: "#10161c",
    webPreferences: { contextIsolation: true, sandbox: true, nodeIntegration: false },
  });
  settingsWin.on("closed", () => { settingsWin = null; });
  settingsWin.loadFile(path.join(__dirname, "..", "renderer", "settings.html")).catch(() => {});
  return settingsWin;
}

function getPetWindow() { return petWin; }

module.exports = {
  createPetWindow,
  loadPetPage,
  loadFallback,
  pushBackendState,
  getBackendState,
  moveBy,
  setPetSize,
  setModelBounds,
  listDisplays,
  moveToDisplay,
  resetPosition,
  createSettingsWindow,
  getPetWindow,
  defaultPosition,
  startHoverWatch,
  stopHoverWatch,
  startSizeWatchdog,
  stopSizeWatchdog,
};
