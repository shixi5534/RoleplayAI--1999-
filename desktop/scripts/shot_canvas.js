/*
 * shot_canvas.js —— 只截 PIXI canvas 本身（不含任何页面 UI），用于判断角色是否被切
 *
 * 上一版 shot_stage.js 用 capturePage 截的是【合成后的页面区域】，把舞台的边框、
 *   tabs、HUD 等 UI 一起截进去了 —— 分析时那圈 UI 被当成"角色像素"，于是"贴边=被切"
 *   的判据全部误报为"是"，把真正的裁切问题盖住了。
 *   这里改成从页面内把 canvas 的像素读出来（toDataURL / readPixels），
 *   得到的是【纯模型画面】，背景透明，可以干净地量包围盒。
 *
 * 前置：后端已在 http://127.0.0.1:8000 运行。
 * 运行： desktop\node_modules\electron\dist\electron.exe desktop\scripts\shot_canvas.js
 * 输出： desktop\scripts\out\canvas_<model>.png
 */
"use strict";
const { app, BrowserWindow } = require("electron");
const path = require("path");
const fs = require("fs");

const BASE = process.env.APP_URL || "http://127.0.0.1:8000";
const OUT = path.join(__dirname, "out");
const wait = (ms) => new Promise((r) => setTimeout(r, ms));
app.disableHardwareAcceleration();

// 在页面里把 canvas 像素转成 PNG（WebGL 原点在左下，需翻转）
const GRAB = `(() => {
  const L = window.RoleplayLive2D, app = L._pixiApp;
  if (!app) return null;
  app.renderer.render(app.stage);
  const gl = app.renderer.gl;
  const w = gl.drawingBufferWidth, h = gl.drawingBufferHeight;
  const pix = new Uint8Array(w*h*4);
  gl.readPixels(0,0,w,h,gl.RGBA,gl.UNSIGNED_BYTE,pix);
  const c = document.createElement("canvas"); c.width = w; c.height = h;
  const ctx = c.getContext("2d"); const img = ctx.createImageData(w,h);
  for (let y=0;y<h;y++) for (let x=0;x<w;x++) {
    const src = ((h-1-y)*w+x)*4, dst = (y*w+x)*4;
    img.data[dst]=pix[src]; img.data[dst+1]=pix[src+1];
    img.data[dst+2]=pix[src+2]; img.data[dst+3]=pix[src+3];
  }
  ctx.putImageData(img,0,0);
  return c.toDataURL("image/png");
})()`;

app.whenReady().then(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const win = new BrowserWindow({
    width: 1440, height: 950, show: false,
    webPreferences: { contextIsolation: true, nodeIntegration: false, sandbox: false },
  });
  const js = (c) => win.webContents.executeJavaScript(c);
  const log = (...a) => console.log(a.join(" "));

  try {
    await win.loadURL(BASE + "/index.html");
    await wait(3500);
    for (const id of ["314701", "314702", "314704"]) {
      await js(`window.RoleplayLive2D.switchModel("${id}")`);
      await wait(1500);
      const png = await js(GRAB);
      if (!png) { log(id + " 取像素失败"); continue; }
      const f = path.join(OUT, `canvas_${id}.png`);
      fs.writeFileSync(f, Buffer.from(png.split(",")[1], "base64"));
      log(id + " -> " + f);
    }
  } catch (e) {
    console.error("失败: " + ((e && e.message) || e));
  }
  app.exit(0);
});
