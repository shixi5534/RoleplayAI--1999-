/*
 * verify_l2d_zoom.js —— 验收「缩放真的能放大/缩小」，防回归
 *
 * 背景（我踩过的坑，务必守住）：
 *   我曾用「放大后角色必须完整放进画布」反推上限：
 *       zoomCap = ZOOM_FIT_MARGIN / max(iw*fit/w, ih*fit/h)
 *   默认适配下 need ≈ 0.92，算出 zoomCap = 1.0 —— 结果是
 *   【缩放被彻底锁死在 100%】：请求 1.5/2/3/5 倍全部只给 1.0，用户放大不了。
 *   用户反馈："模型大小，你干嘛给我锁了？"
 *   已改为：不封顶缩放（setZoom 的 0.5~2.0 就是范围），
 *           放大后由 _clampOffset 把角色稳在画面中央。
 *
 * 本脚本守住两条不变量：
 *   1) 请求倍率必须如实生效（不再有第二道封顶）
 *   2) 放大后角色主体仍在画面内（不会跑丢）
 *
 * 运行： desktop\node_modules\electron\dist\electron.exe desktop\scripts\verify_l2d_zoom.js
 */
"use strict";
const { app, BrowserWindow } = require("electron");

const BASE = process.env.APP_URL || "http://127.0.0.1:8000";
const wait = (ms) => new Promise((r) => setTimeout(r, ms));
app.disableHardwareAcceleration();

const GEO = `() => {
  const L = window.RoleplayLive2D, a = L._pixiApp;
  a.renderer.render(a.stage);
  const gl = a.renderer.gl, w = gl.drawingBufferWidth, h = gl.drawingBufferHeight;
  const res = a.renderer.resolution || 1;
  const p = new Uint8Array(w*h*4);
  gl.readPixels(0,0,w,h,gl.RGBA,gl.UNSIGNED_BYTE,p);
  let n=0,minX=w,minY=h,maxX=-1,maxY=-1;
  for(let y=0;y<h;y++) for(let x=0;x<w;x++) if(p[(y*w+x)*4+3]>10){ n++;
    if(x<minX)minX=x; if(x>maxX)maxX=x; if(y<minY)minY=y; if(y>maxY)maxY=y; }
  return JSON.stringify({ visiblePx:n,
    contentCss:[+(minX/res).toFixed(0), +((h-1-maxY)/res).toFixed(0),
                +(maxX/res).toFixed(0), +((h-1-minY)/res).toFixed(0)],
    canvas:[Math.round(a.screen.width), Math.round(a.screen.height)],
    requested:+L._zoomMult.toFixed(3), applied:+(L.getAppliedZoom? L.getAppliedZoom():1).toFixed(3) });
}`;

app.whenReady().then(async () => {
  const win = new BrowserWindow({ width: 1440, height: 950, show: false,
    webPreferences: { contextIsolation: true, nodeIntegration: false, sandbox: false } });
  const js = (c) => win.webContents.executeJavaScript(c);
  let failed = 0;
  const check = (label, ok, detail) => {
    if (!ok) failed++;
    console.log(`${ok ? "PASS" : "FAIL"}  ${label}${detail ? "  — " + detail : ""}`);
  };
  try {
    let ok = false;
    for (let i = 0; i < 3 && !ok; i++) {
      try { await win.loadURL(BASE + "/index.html"); ok = true; } catch (_) { await wait(900); }
    }
    if (!ok) throw new Error("页面加载失败");
    await wait(3500);

    for (const id of ["314701", "314702", "314704"]) {
      console.log("=".repeat(74));
      console.log("模型 " + id);
      await js(`window.RoleplayLive2D.switchModel("${id}")`);
      await wait(1500);

      // 1) 倍率如实生效（这是被锁过的地方）
      for (const z of [0.5, 0.8, 1.0, 1.5, 2.0]) {
        await js(`window.RoleplayLive2D.setZoom(${z})`);
        await wait(300);
        const g = JSON.parse(await js(`(${GEO})()`));
        // setZoom 会把范围夹在 0.5~2.0；在范围内的请求必须原样生效
        const expect = Math.max(0.5, Math.min(2.0, z));
        check(`${id} 请求 ${z}x -> 实际 ${g.applied}x`,
              Math.abs(g.applied - expect) < 0.01,
              `请求=${g.requested} 实际=${g.applied} 期望=${expect}`);
      }

      // 2) 放大后主体仍在画面内（不跑丢）
      for (const z of [1.5, 2.0]) {
        await js(`window.RoleplayLive2D.setZoom(${z}); window.RoleplayLive2D.setOffset(0,0)`);
        await wait(400);
        let minPx = Infinity;
        let g = null;
        for (let i = 0; i < 6; i++) {
          g = JSON.parse(await js(`(${GEO})()`));
          minPx = Math.min(minPx, g.visiblePx);
          await wait(150);
        }
        check(`${id} ${z}x 放大后主体仍在画面内`, minPx > 20000,
              `6 帧最小可见像素 ${minPx}  内容 ${g.contentCss.join(",")} / 画布 ${g.canvas.join("x")}`);
      }
      await js("window.RoleplayLive2D.setZoom(1)");
    }
  } catch (e) {
    check("缩放验收执行", false, String((e && e.message) || e));
  }
  console.log("=".repeat(74));
  console.log(failed ? `结果: ${failed} 项未通过` : "结果: 全部通过");
  app.exit(0);
});
