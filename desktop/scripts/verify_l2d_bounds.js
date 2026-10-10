/*
 * verify_l2d_bounds.js —— 拖拽/缩放行为验收（限制已按用户要求放开）
 *
 * 契约（用户明确要求：取消左右与上下拖动的限制）
 * -------------------------------------------------
 *   1) 拖拽偏移【不夹紧】：请求多大就生效多大，包括把角色拖出画面。
 *   2) 缩放不被封顶：请求倍率如实生效（setZoom 的 0.5~2.0 就是范围）。
 *   3) 可恢复：按 F / 双击 / resetPosition() 能一键回到居中，角色必定重新可见。
 *   4) 默认状态（offset=0）下角色完整可见 —— 这是"打开就是好的"的保证。
 *
 * 历史：本脚本原来断言"任何缩放/拖拽组合下角色都不得越出画布"，
 *   那是旧契约（限制存在时）。限制一旦放开，把角色拖到 (9999,9999)
 *   本来就该跑出画面，旧断言必然失败 —— 因此改为验证上面 4 条。
 *
 * 运行： desktop\node_modules\electron\dist\electron.exe desktop\scripts\verify_l2d_bounds.js
 */
"use strict";
const { app, BrowserWindow } = require("electron");

const BASE = process.env.APP_URL || "http://127.0.0.1:8000";
const wait = (ms) => new Promise((r) => setTimeout(r, ms));
app.disableHardwareAcceleration();

const GRAB = `(() => {
  const L = window.RoleplayLive2D, a = L._pixiApp;
  if (!a || !L._model) return JSON.stringify({ ok:false });
  a.renderer.render(a.stage);
  const gl = a.renderer.gl, w = gl.drawingBufferWidth, h = gl.drawingBufferHeight;
  const res = a.renderer.resolution || 1;
  const p = new Uint8Array(w*h*4);
  gl.readPixels(0,0,w,h,gl.RGBA,gl.UNSIGNED_BYTE,p);
  let n=0,minX=w,minY=h,maxX=-1,maxY=-1;
  for(let y=0;y<h;y++) for(let x=0;x<w;x++) if(p[(y*w+x)*4+3]>10){ n++;
    if(x<minX)minX=x; if(x>maxX)maxX=x; if(y<minY)minY=y; if(y>maxY)maxY=y; }
  return JSON.stringify({ ok:true, visiblePx:n,
    content:[+(minX/res).toFixed(1), +((h-1-maxY)/res).toFixed(1),
             +(maxX/res).toFixed(1), +((h-1-minY)/res).toFixed(1)],
    canvas:[Math.round(a.screen.width), Math.round(a.screen.height)],
    off:[Math.round(L._userOffsetX), Math.round(L._userOffsetY)],
    applied:+L.getAppliedZoom().toFixed(3) });
})()`;

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
      console.log("=".repeat(76));
      console.log("模型 " + id);
      await js(`window.RoleplayLive2D.switchModel("${id}")`);
      await wait(1200);

      // (1) 默认状态完整可见
      await js("window.RoleplayLive2D.setZoom(1); window.RoleplayLive2D.setOffset(0,0)");
      await wait(400);
      const base = JSON.parse(await js(GRAB));
      const inside = base.content[0] > 0 && base.content[1] > 0
                  && base.content[2] < base.canvas[0] && base.content[3] < base.canvas[1];
      check(`${id} 默认状态角色完整可见`, base.ok && base.visiblePx > 3000 && inside,
            `可见 ${base.visiblePx}px 内容 ${base.content.join(",")} / 画布 ${base.canvas.join("x")}`);

      // (2) 拖拽不夹紧：请求即生效（含拖出画面）
      for (const [dx, dy] of [[120, 0], [-120, 0], [0, 120], [0, -120], [9999, 9999], [-9999, -9999]]) {
        await js(`window.RoleplayLive2D.setOffset(${dx}, ${dy})`);
        await wait(250);
        const g = JSON.parse(await js(GRAB));
        check(`${id} 拖拽(${dx},${dy}) 未被夹紧`,
              Math.abs(g.off[0] - dx) < 2 && Math.abs(g.off[1] - dy) < 2,
              `生效偏移 ${JSON.stringify(g.off)}${g.visiblePx === 0 ? "（已拖出画面，符合放开后的预期）" : ""}`);
      }

      // (3) 可恢复：resetPosition 后必定重新可见
      await js("window.RoleplayLive2D.resetPosition()");
      await wait(500);
      const rec = JSON.parse(await js(GRAB));
      check(`${id} 拖出画面后 F/重置可恢复可见`,
            rec.ok && rec.visiblePx > 3000 && rec.off[0] === 0 && rec.off[1] === 0,
            `重置后偏移 ${JSON.stringify(rec.off)} 可见 ${rec.visiblePx}px`);

      // (4) 缩放不封顶：请求倍率如实生效
      for (const z of [0.5, 1.0, 1.7, 2.0]) {
        await js(`window.RoleplayLive2D.setZoom(${z}); window.RoleplayLive2D.setOffset(0,0)`);
        await wait(300);
        const g = JSON.parse(await js(GRAB));
        check(`${id} 缩放 ${z}x 如实生效`, Math.abs(g.applied - z) < 0.01,
              `实际 ${g.applied}x，可见 ${g.visiblePx}px`);
      }
      await js("window.RoleplayLive2D.setZoom(1); window.RoleplayLive2D.setOffset(0,0)");
    }
  } catch (e) {
    check("验收执行", false, String((e && e.message) || e));
  }
  console.log("=".repeat(76));
  console.log(failed ? `结果: ${failed} 项未通过` : "结果: 全部通过");
  app.exit(0);
});
