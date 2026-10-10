/*
 * diag_zoom_offset.js —— 复现「缩放 170% + 自定义位置」下的摆放
 *
 * 用户截图里 HUD 显示「缩放 170%」「位置 自定义」，而我的验收一直是默认 100%/居中，
 *   所以从没复现过。这里按真实持久化状态（localStorage: roleplay_chat_state）复现：
 *   对比 100% / 170% 以及带拖拽偏移时，角色是否超出 canvas 上边缘（=肉眼看到的"头被切"）。
 *
 * 前置：后端已在 http://127.0.0.1:8000 运行。
 * 运行： desktop\node_modules\electron\dist\electron.exe desktop\scripts\diag_zoom_offset.js
 */
"use strict";
const { app, BrowserWindow } = require("electron");
const path = require("path");
const fs = require("fs");

const BASE = process.env.APP_URL || "http://127.0.0.1:8000";
const OUT = path.join(__dirname, "out");
const wait = (ms) => new Promise((r) => setTimeout(r, ms));
app.disableHardwareAcceleration();

const GRAB = `(() => {
  const L = window.RoleplayLive2D, app = L._pixiApp;
  app.renderer.render(app.stage);
  const gl = app.renderer.gl, w = gl.drawingBufferWidth, h = gl.drawingBufferHeight;
  const res = app.renderer.resolution || 1;
  const pix = new Uint8Array(w*h*4);
  gl.readPixels(0,0,w,h,gl.RGBA,gl.UNSIGNED_BYTE,pix);
  let n=0, minX=w, minY=h, maxX=-1, maxY=-1;
  for (let y=0;y<h;y++) for (let x=0;x<w;x++) if (pix[(y*w+x)*4+3]>10) { n++;
    if(x<minX)minX=x; if(x>maxX)maxX=x; if(y<minY)minY=y; if(y>maxY)maxY=y; }
  // readPixels 原点左下 -> 翻成距顶部的 CSS 像素
  const cTop = (h-1-maxY)/res, cBot = (h-1-minY)/res;
  const cL = minX/res, cR = maxX/res;
  const sw = app.screen.width, sh = app.screen.height;
  // 另存一张 canvas PNG 便于看图
  const c = document.createElement("canvas"); c.width=w; c.height=h;
  const ctx = c.getContext("2d"), img = ctx.createImageData(w,h);
  for (let y=0;y<h;y++) for (let x=0;x<w;x++) {
    const s=((h-1-y)*w+x)*4, d=(y*w+x)*4;
    img.data[d]=pix[s]; img.data[d+1]=pix[s+1]; img.data[d+2]=pix[s+2]; img.data[d+3]=pix[s+3];
  }
  ctx.putImageData(img,0,0);
  return JSON.stringify({
    zoom: L._zoomMult, offset: [L._userOffsetX, L._userOffsetY],
    canvasCss: [sw, sh], contentCss: [+cL.toFixed(0), +cTop.toFixed(0), +cR.toFixed(0), +cBot.toFixed(0)],
    visiblePx: n,
    clippedTop: cTop <= 0.5, clippedBottom: cBot >= sh - 1.5,
    clippedLeft: cL <= 0.5, clippedRight: cR >= sw - 1.5,
    png: c.toDataURL("image/png"),
  });
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

    for (const id of ["314701", "314704"]) {
      log("=".repeat(78));
      log("模型 " + id);
      // 按用户截图的状态组合逐项验证
      const cases = [
        ["默认 100% / 居中", 1.0, 0, 0],
        ["缩放 170% / 居中", 1.7, 0, 0],
        ["缩放 170% / 自定义偏移(截图状态)", 1.7, null, null],
      ];
      for (const [label, z, ox, oy] of cases) {
        await js(`window.RoleplayLive2D.switchModel("${id}")`);
        await wait(1200);
        await js(`window.RoleplayLive2D.setZoom(${z})`);
        if (ox === null) {
          // 模拟用户拖拽后的持久化偏移（截图里"位置 自定义"）
          await js(`window.RoleplayLive2D.setOffset(-40, 120)`);
        } else {
          await js(`window.RoleplayLive2D.setOffset(${ox}, ${oy})`);
        }
        await wait(500);
        const r = JSON.parse(await js(GRAB));
        const [l, t, rr, b] = r.contentCss;
        const [cw, ch] = r.canvasCss;
        const cuts = [];
        if (r.clippedTop) cuts.push("顶部(头顶被切)");
        if (r.clippedBottom) cuts.push("底部");
        if (r.clippedLeft) cuts.push("左");
        if (r.clippedRight) cuts.push("右");
        log("  " + label.padEnd(34)
            + " zoom=" + r.zoom + " 内容 y " + t + ".." + b + " / 画布高 " + ch
            + "  -> " + (cuts.length ? "!! " + cuts.join("、") : "完整可见"));
        const f = path.join(OUT, `zoom_${id}_${String(z).replace(".", "")}_${ox === null ? "custom" : "center"}.png`);
        fs.writeFileSync(f, Buffer.from(r.png.split(",")[1], "base64"));
      }
    }
    log("\n截图已写入 " + OUT);
  } catch (e) {
    console.error("失败: " + ((e && e.message) || e));
  }
  app.exit(0);
});
