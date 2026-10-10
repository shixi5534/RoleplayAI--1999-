/*
 * diag_l2d_placement.js —— 量测三套模型在真实舞台上的「摆放位置」与「点击区域映射」
 *
 * 起因：用户反馈「定位有问题」。本项目里有两处都依赖同一个假设 ——
 *   「模型内容在局部坐标里正好铺满 0.._srcW × 0.._srcH」：
 *     1) live2d.js 的 _fit()     用 _srcW/_srcH + getLocalBounds() 计算缩放与居中；
 *     2) live2d.js 的 _handleClick() 用
 *          rx = (cx - model.x) / scale / _srcW
 *          ry = (cy - model.y) / scale / _srcH
 *        把点击位置换算成 interact_map.json 里的归一化坐标。
 *   如果实际绘制内容并不铺满这个矩形，那么【模型会摆偏】且【点击区域会错位】。
 *   本脚本用「真实渲染像素」测出内容实际占据的归一化范围，据此判断假设是否成立。
 *
 * 前置：后端已在 http://127.0.0.1:8000 运行。
 * 运行： desktop\node_modules\electron\dist\electron.exe desktop\scripts\diag_l2d_placement.js
 */
"use strict";
const { app, BrowserWindow } = require("electron");
const path = require("path");
const fs = require("fs");

const BASE = process.env.APP_URL || "http://127.0.0.1:8000";
const OUT = path.join(__dirname, "out");
const wait = (ms) => new Promise((r) => setTimeout(r, ms));

app.disableHardwareAcceleration();

// 这个探针在页面里跑：返回真实渲染包围盒 + 按 _handleClick 公式换算的归一化坐标
const PROBE = `(() => {
  const L = window.RoleplayLive2D;
  const app = L._pixiApp, m = L._model;
  if (!app || !m) return JSON.stringify({ ok:false, reason:"no model/app" });
  app.renderer.render(app.stage);

  const gl = app.renderer.gl;
  const dbw = gl.drawingBufferWidth, dbh = gl.drawingBufferHeight;
  const res = app.renderer.resolution || 1;
  const sw = app.screen.width, sh = app.screen.height;   // CSS 像素（_fit 用的量纲）

  const pix = new Uint8Array(dbw*dbh*4);
  gl.readPixels(0,0,dbw,dbh,gl.RGBA,gl.UNSIGNED_BYTE,pix);
  let n=0, minX=dbw, minY=dbh, maxX=-1, maxY=-1;
  for (let y=0;y<dbh;y++) for (let x=0;x<dbw;x++)
    if (pix[(y*dbw+x)*4+3] > 10) { n++;
      if(x<minX)minX=x; if(x>maxX)maxX=x; if(y<minY)minY=y; if(y>maxY)maxY=y; }

  // 注意：readPixels 的 y 原点在【左下】，而 _handleClick 收到的是容器左上原点的点击坐标
  const toCssX = (px) => px / res;
  const toCssYtop = (pxBottom) => (dbh - 1 - pxBottom) / res;   // 翻成「距顶部」

  const cLeft = toCssX(minX), cRight = toCssX(maxX);
  const cTop  = toCssYtop(maxY), cBottom = toCssYtop(minY);

  const s = m.scale.x || 1;
  const srcW = L._srcW, srcH = L._srcH, mx = m.x, my = m.y;
  const box = L._contentBox;   // 真实内容盒（修复后的基准）

  // 复刻 _handleClick 的归一化公式（以内容盒为基准）
  const norm = (cssX, cssY) => box ? ({
    rx: +(((cssX - mx) / s - box.x) / box.w).toFixed(4),
    ry: +(((cssY - my) / s - box.y) / box.h).toFixed(4),
  }) : { rx: null, ry: null };
  // 旧基准（布局框）的换算，用于对比错位程度
  const normOld = (cssX, cssY) => ({
    rx: +((cssX - mx) / s / srcW).toFixed(4),
    ry: +((cssY - my) / s / srcH).toFixed(4),
  });
  const tl = norm(cLeft, cTop), br = norm(cRight, cBottom);
  const tlOld = normOld(cLeft, cTop);

  return JSON.stringify({
    ok: true,
    id: L.getCurrentModelId(),
    canvasCss: [sw, sh], drawingBuffer: [dbw, dbh], resolution: res,
    scale: +s.toFixed(6), pos: [+mx.toFixed(1), +my.toFixed(1)],
    srcWH: [srcW, srcH],
    localBounds: (() => { const b = m.getLocalBounds();
      return [+b.x.toFixed(0), +b.y.toFixed(0), +b.width.toFixed(0), +b.height.toFixed(0)]; })(),
    visiblePx: n,
    contentCss: { left:+cLeft.toFixed(1), top:+cTop.toFixed(1),
                  right:+cRight.toFixed(1), bottom:+cBottom.toFixed(1),
                  w:+(cRight-cLeft).toFixed(1), h:+(cBottom-cTop).toFixed(1) },
    contentBox: box ? { x:+box.x.toFixed(1), y:+box.y.toFixed(1),
                        w:+box.w.toFixed(1), h:+box.h.toFixed(1), measured: !!box.measured } : null,
    // 内容在【修复后基准(内容盒)】里应恰好占据 0..1
    contentNorm: { x0: tl.rx, y0: tl.ry, x1: br.rx, y1: br.ry },
    // 内容在【旧基准(布局框)】里的位置，用来量化旧实现的错位
    contentNormOld: { x0: tlOld.rx, y0: tlOld.ry },
    clipped: { left: cLeft<=0, top: cTop<=0, right: cRight>=sw-1, bottom: cBottom>=sh-1 },
    regions: (L._regionMap && L._regionMap.regions || []).map(r => {
      // 区域矩形在画布上的实际像素范围（修复后：以内容盒换算）
      const bx = mx + (box ? (box.x + r.rect[0]*box.w) : r.rect[0]*srcW) * s;
      const by = my + (box ? (box.y + r.rect[1]*box.h) : r.rect[1]*srcH) * s;
      const brx = mx + (box ? (box.x + (r.rect[0]+r.rect[2])*box.w) : (r.rect[0]+r.rect[2])*srcW) * s;
      const bry = my + (box ? (box.y + (r.rect[1]+r.rect[3])*box.h) : (r.rect[1]+r.rect[3])*srcH) * s;
      return { id: r.id, rect: r.rect,
               cssBox: [ +bx.toFixed(0), +by.toFixed(0), +brx.toFixed(0), +bry.toFixed(0) ] };
    }),
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

    for (const id of ["314701", "314702", "314704"]) {
      await js(`window.RoleplayLive2D.switchModel("${id}")`);
      await wait(1300);
      const r = JSON.parse(await js(PROBE));
      log("=".repeat(78));
      if (!r.ok) { log(id + " 探针失败: " + r.reason); continue; }
      log("模型 " + r.id);
      log("  画布(CSS) " + JSON.stringify(r.canvasCss) + "  drawingBuffer " + JSON.stringify(r.drawingBuffer)
          + "  resolution " + r.resolution);
      log("  scale=" + r.scale + "  pos=" + JSON.stringify(r.pos) + "  _srcWH=" + JSON.stringify(r.srcWH));
      log("  getLocalBounds()  " + JSON.stringify(r.localBounds));
      log("  真实内容(CSS 像素, 左上原点)  " + JSON.stringify(r.contentCss));
      log("  可见像素 " + r.visiblePx);
      const cn = r.contentNorm;
      log("  内容在【归一化空间】占据  x " + cn.x0 + ".." + cn.x1 + "   y " + cn.y0 + ".." + cn.y1
          + "   (理想应为 0..1)");
      const off = Math.abs(cn.x0) + Math.abs(cn.y0) + Math.abs(1-cn.x1) + Math.abs(1-cn.y1);
      log("  归一化偏移量合计 " + off.toFixed(3) + (off > 0.1 ? "   <<< 点击区域会错位" : "   (可接受)"));
      log("  裁切 " + JSON.stringify(r.clipped)
          + ((r.clipped.top||r.clipped.bottom||r.clipped.left||r.clipped.right) ? "   <<< 有内容被切掉" : ""));
      for (const g of r.regions) {
        log("    区域 " + g.id.padEnd(6) + " rect=" + JSON.stringify(g.rect)
            + "  -> 画布像素 " + JSON.stringify(g.cssBox));
      }
      // 另存一张舞台截图
      const shot = await win.webContents.capturePage();
      fs.writeFileSync(path.join(OUT, `placement_${r.id}.png`), shot.toPNG());
    }
    log("\n截图: " + OUT + "\\placement_*.png");
  } catch (e) {
    console.error("失败: " + ((e && e.message) || e));
  }
  app.exit(0);
});
