/*
 * smoke_render.js —— 桌面宠物渲染冒烟（Phase 4 像素级验证）
 *
 * 运行：electron scripts/smoke_render.js
 * 前置：127.0.0.1:8000 后端已启动。
 */
"use strict";

const { app, BrowserWindow } = require("electron");
const path = require("path");
const os = require("os");
const fs = require("fs");

// 独立 userData：避免此前运行残留的 spine_model 污染冒烟测试。
const USER_DATA = path.join(os.tmpdir(), "roleplay-pet-smoke-render-" + process.pid);
app.setPath("userData", USER_DATA);

const REPO = path.resolve(__dirname, "..", "..");
const PRELOAD = path.join(REPO, "desktop", "src", "preload", "pet.js");
const PET_URL = process.env.PET_URL || "http://127.0.0.1:8000/pet.html";
const MODEL_IDS = ["314701_s", "314701", "314702"];

const wait = (ms) => new Promise((r) => setTimeout(r, ms));

app.whenReady().then(async () => {
  const win = new BrowserWindow({
    width: 320,
    height: 420,
    transparent: true,
    frame: false,
    show: false,
    hasShadow: false,
    webPreferences: {
      preload: PRELOAD,
      contextIsolation: true,
      sandbox: true,
      nodeIntegration: false,
    },
  });

  const rendererErrors = [];
  win.webContents.on("console-message", (_e, level, message) => {
    if (level >= 3) rendererErrors.push(String(message || ""));
  });

  async function evalJs(expression) {
    return win.webContents.executeJavaScript(expression);
  }

  try {
    await win.loadURL(PET_URL);
    await evalJs(`
      localStorage.setItem("roleplay_pet_state", JSON.stringify({
        renderer: "spine", spine_model: "314701_s", onboarded: true,
        browser_seen: true, zoom: 1.0, muted: false, dnd: false, locked: false
      }));
      true;
    `);
    const reloaded = new Promise((r) => win.webContents.once("did-finish-load", r));
    win.reload();
    await reloaded;

    async function waitModel(modelId) {
      for (let i = 0; i < 120; i++) {
        const ready = await evalJs(
          `!!(window.RoleplaySpine && window.RoleplaySpine.ready && window.RoleplaySpine.getModel() && window.RoleplaySpine.getModel().id === "${modelId}")`
        ).catch(() => false);
        if (ready) return;
        await wait(200);
      }
      const diag = await evalJs(`JSON.stringify({
        hasSpine: !!window.RoleplaySpine,
        ready: !!(window.RoleplaySpine && window.RoleplaySpine.ready),
        model: window.RoleplaySpine && window.RoleplaySpine.getModel ? window.RoleplaySpine.getModel() : null,
        models: window.RoleplaySpine && window.RoleplaySpine.getModels ? window.RoleplaySpine.getModels() : null,
        state: window.RoleplayPet ? window.RoleplayPet.getState() : null,
        errorHidden: document.getElementById("pet-error") ? document.getElementById("pet-error").hidden : null,
        errorText: document.getElementById("pet-error") ? document.getElementById("pet-error").textContent : null
      })`).catch((e) => "DIAG_ERR " + e.message);
      throw new Error("模型未在超时时间内就绪: " + modelId + " | " + diag);
    }

    const renderProbe = `(() => {
      const s = window.RoleplaySpine;
      if (!s || !s._app) return { ok: false, error: "no renderer" };
      s._onRender(s._app);
      const gl = s._app.gl;
      const w = gl.drawingBufferWidth;
      const h = gl.drawingBufferHeight;
      const pix = new Uint8Array(w * h * 4);
      gl.readPixels(0, 0, w, h, gl.RGBA, gl.UNSIGNED_BYTE, pix);
      let nontrans = 0;
      let colored = 0;
      let minX = w, minY = h, maxX = -1, maxY = -1;
      for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
        const i = y * w + x;
        const r = pix[i * 4], g = pix[i * 4 + 1], b = pix[i * 4 + 2], a = pix[i * 4 + 3];
        if (a > 10) {
          nontrans++;
          minX = Math.min(minX, x); maxX = Math.max(maxX, x);
          minY = Math.min(minY, y); maxY = Math.max(maxY, y);
          if (r + g + b > 90) colored++;
        }
      }
      const errEl = document.getElementById("pet-error");
      return {
        ok: true,
        modelId: s.getModel().id,
        drawingBuffer: [w, h],
        nontrans,
        colored,
        bbox: [minX, minY, maxX, maxY],
        bboxHeight: maxY >= minY ? maxY - minY + 1 : 0,
        bboxWidth: maxX >= minX ? maxX - minX + 1 : 0,
        errorDisplay: errEl ? getComputedStyle(errEl).display : "missing",
        errorHidden: errEl ? errEl.hidden : null,
        renderer: (window.RoleplayPet && window.RoleplayPet.getState().renderer) || "unknown"
      };
    })()`;

    const animProbe = `(() => {
      const s = window.RoleplaySpine;
      const gl = s._app.gl;
      const w = gl.drawingBufferWidth, h = gl.drawingBufferHeight;
      const read = () => {
        const pix = new Uint8Array(w * h * 4);
        gl.readPixels(0, 0, w, h, gl.RGBA, gl.UNSIGNED_BYTE, pix);
        return pix;
      };
      s._onUpdate(s._app, 0);
      s._onRender(s._app);
      const a = read();
      s._onUpdate(s._app, 0.5);
      s._onRender(s._app);
      const b = read();
      let diff = 0;
      for (let i = 0; i < a.length; i += 16) {
        if (Math.abs(a[i] - b[i]) + Math.abs(a[i+1] - b[i+1]) + Math.abs(a[i+2] - b[i+2]) + Math.abs(a[i+3] - b[i+3]) > 24) diff++;
      }
      return { diffSamples: diff };
    })()`;

    for (let mi = 0; mi < MODEL_IDS.length; mi++) {
      const modelId = MODEL_IDS[mi];
      if (mi === 0) {
        await waitModel(modelId);
      } else {
        const switched = await evalJs(`window.RoleplayPet.switchSpineModel("${modelId}")`).catch(() => false);
        if (!switched) throw new Error("模型切换失败: " + modelId);
        await waitModel(modelId);
        await wait(300);
      }

      const info = await evalJs(renderProbe);
      const animInfo = await evalJs(animProbe);
      console.log("MODEL " + modelId + " RENDER", JSON.stringify(info));
      console.log("MODEL " + modelId + " ANIM", JSON.stringify(animInfo));

      if (!info.ok) throw new Error(info.error || "render probe failed");
      const total = info.drawingBuffer[0] * info.drawingBuffer[1];
      if (info.modelId !== modelId) throw new Error(`当前模型 id 不一致: ${info.modelId}`);
      if (info.errorDisplay !== "none") throw new Error("pet-error 错误层未隐藏，全窗会被黑底覆盖");
      if (info.renderer !== "spine") throw new Error("渲染器不是 spine");
      if (info.nontrans < total * 0.015) throw new Error(`模型非透明像素过少: ${info.nontrans}/${total}`);
      if (info.colored < total * 0.003) throw new Error(`模型彩色像素过少: ${info.colored}/${total}`);
      if (info.bboxHeight < 50) throw new Error(`模型包围盒高度异常: ${info.bboxHeight}px（可能只露出脚底一条边）`);
      if (!animInfo || animInfo.diffSamples < 80) throw new Error(`动画帧差异过小: ${animInfo && animInfo.diffSamples}（骨骼动画未推进）`);
    }

    // 长按窗口/模型：按住 1.8s 再松开，窗口尺寸必须不变。
    await evalJs(`(() => {
      const c = document.getElementById('pet-canvas');
      c.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true, button: 0, pointerId: 91, clientX: 160, clientY: 210, screenX: 160, screenY: 210 }));
      return true;
    })()`);
    await wait(1800);
    await evalJs(`(() => {
      const c = document.getElementById('pet-canvas');
      c.dispatchEvent(new PointerEvent('pointerup', { bubbles: true, button: 0, pointerId: 91, clientX: 160, clientY: 210, screenX: 160, screenY: 210 }));
      return true;
    })()`);
    await wait(400);
    const longPressInfo = JSON.parse(await evalJs(`JSON.stringify({
      outer: [outerWidth, outerHeight],
      ready: window.RoleplaySpine.ready,
      canvases: document.querySelectorAll('#pet-canvas canvas').length
    })`));
    console.log("LONG_PRESS", JSON.stringify(longPressInfo));
    if (longPressInfo.outer[0] !== 320 || longPressInfo.outer[1] < 420 || longPressInfo.outer[1] > 430) {
      throw new Error("长按后窗口尺寸发生变化: " + longPressInfo.outer.join("x"));
    }

    // 右键连点切换：连续两次 cycle，最终应落在第二次请求的模型，且只留一个 canvas。
    await evalJs("window.RoleplayPet.cycleSpineModel(); window.RoleplayPet.cycleSpineModel(); true");
    await waitModel(MODEL_IDS[1]);
    const rapidInfo = await evalJs(`JSON.stringify({
      model: window.RoleplaySpine.getModel().id,
      ready: window.RoleplaySpine.ready,
      canvases: document.querySelectorAll('#pet-canvas canvas').length,
      outer: [outerWidth, outerHeight]
    })`);
    console.log("RAPID_SWITCH", rapidInfo);
    const rapid = JSON.parse(rapidInfo);
    if (rapid.model !== MODEL_IDS[1] || !rapid.ready || rapid.canvases !== 1) {
      throw new Error("右键连点切换未收敛到单一模型");
    }
    if (rapid.outer[0] !== 320 || rapid.outer[1] < 420 || rapid.outer[1] > 430) {
      throw new Error("右键连点切换后窗口尺寸漂移: " + rapid.outer.join("x"));
    }

    // 对话气泡链路：mock RoleplayChat.send 驱动完整 chunk 流，验证回复真正出现在气泡里。
    const chatInfo = await evalJs(`(async () => {
      window.RoleplayChat.send = async (text, opts) => {
        opts.onFirstChunk && opts.onFirstChunk();
        opts.onChunk && opts.onChunk("你好，无名者。");
        opts.onComplete && opts.onComplete("你好，无名者。", true);
        return { fullReply: "你好，无名者。", sawChunk: true };
      };
      await window.RoleplayPet.send("测试");
      const bubble = document.getElementById("pet-bubble");
      const text = document.getElementById("pet-bubble-text");
      window.RoleplayPet.changeBubbleSize(0.2);
      window.RoleplayPet.changeZoom(-0.1);
      window.RoleplayPet.setLocked(true);
      const locked = window.RoleplayPet.isLocked();
      window.RoleplayPet.setLocked(false);
      return {
        text: text ? text.textContent : null,
        show: bubble ? bubble.classList.contains("show") : false,
        bubbleScale: document.body.style.getPropertyValue("--bubble-scale"),
        zoom: window.RoleplayPet.getState().zoom,
        locked
      };
    })()`);
    console.log("CHAT_AND_SIZE", JSON.stringify(chatInfo));
    if (!chatInfo.text || !chatInfo.text.includes("你好，无名者")) throw new Error("对话回复未写入气泡");
    if (!chatInfo.show) throw new Error("对话后气泡未显示");
    if (Number(chatInfo.bubbleScale) <= 1) throw new Error("气泡大小调节未生效");
    if (!(chatInfo.zoom < 1)) throw new Error("模型大小调节未生效");
    if (!chatInfo.locked) throw new Error("位置锁定未生效");

    const fatal = rendererErrors.filter((m) => /physics is undefined|\[spine\][^\n]*(异常|失败|加载失败)/.test(m));
    if (fatal.length) throw new Error("渲染进程异常日志: " + fatal.slice(0, 3).join(" | "));

    console.log("PASS: 三模型渲染/热切换 + 连点防抖 + 对话气泡 + 模型/气泡大小 + 位置锁定");
    try { fs.rmSync(USER_DATA, { recursive: true, force: true }); } catch (_) {}
    app.exit(0);
  } catch (e) {
    console.error("SMOKE_RENDER_FAIL:", e && e.stack ? e.stack : e);
    console.error("RENDERER_ERRORS:", rendererErrors.slice(0, 10));
    try { fs.rmSync(USER_DATA, { recursive: true, force: true }); } catch (_) {}
    app.exit(1);
  }
});
