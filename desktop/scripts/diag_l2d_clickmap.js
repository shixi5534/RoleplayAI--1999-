/*
 * diag_l2d_clickmap.js —— 端到端量测「点击哪儿 -> 命中哪个区域」是否与画面一致
 *
 * 起因：用户反馈「定位有问题」。上面 diag_l2d_placement.js 已证明：模型真实绘制内容
 *   只占据 _handleClick 归一化空间的 x 0.15..0.90 / y -0.04..0.50（理想应为 0..1），
 *   也就是说 interact_map.json 里按 0..1 定义的头部/身体/下摆矩形，和角色实际所在的
 *   位置对不上（头部矩形甚至落在角色上方之外）。
 *
 * 本脚本走【真实点击路径】_handleClick(cssX, cssY)，在画布上打网格，记录每个点命中
 * 的区域，用来直观看出错位程度；同时给出内容在模型局部坐标里的真实包围盒，
 * 作为修复 _fit / 点击换算的依据。
 *
 * 前置：后端已在 http://127.0.0.1:8000 运行。
 * 运行： desktop\node_modules\electron\dist\electron.exe desktop\scripts\diag_l2d_clickmap.js
 */
"use strict";
const { app, BrowserWindow } = require("electron");
const path = require("path");
const fs = require("fs");

const BASE = process.env.APP_URL || "http://127.0.0.1:8000";
const wait = (ms) => new Promise((r) => setTimeout(r, ms));
app.disableHardwareAcceleration();

const SETUP = `(() => {
  const L = window.RoleplayLive2D;
  if (!window.__clickProbeBound) {
    window.__clickProbeBound = true;
    window.__clickHits = [];
    window.addEventListener("live2d:interact", (e) => {
      window.__clickHits.push(e.detail && e.detail.region);
    });
    // 屏蔽语音/气泡副作用，避免干扰与卡顿
    if (window.RoleplayPetCore) window.RoleplayPetCore.emitIntent = () => {};
  }
  return true;
})()`;

/** 单次点击：清冷却 -> 调 _handleClick -> 取本次命中的区域 */
const CLICK = `(cssX, cssY) => {
  const L = window.RoleplayLive2D;
  L._lastClickAt = 0;
  L._regionLastAt = {};
  L._regionCounts = {};
  const before = window.__clickHits.length;
  window.__clickHits.length = before;
  L._handleClick(cssX, cssY);
  const hits = window.__clickHits.slice(before);
  return JSON.stringify({ region: hits.length ? hits[0] : null });
}`;

/** 内容在模型局部坐标里的真实包围盒（drawable 顶点并集） */
const CONTENT = `(() => {
  const L = window.RoleplayLive2D;
  const im = L._model && L._model.internalModel;
  if (!im || !im.coreModel) return JSON.stringify({ ok:false });
  const cm = im.coreModel;
  let minX=1e18,minY=1e18,maxX=-1e18,maxY=-1e18, any=false;
  const n = cm.getDrawableCount();
  for (let i=0;i<n;i++) {
    let v; try { v = im.getDrawableVertices(i); } catch(e) { continue; }
    if (!v || !v.length) continue;
    for (let j=0;j<v.length;j+=2) { any=true;
      const x=v[j], y=v[j+1];
      if(x<minX)minX=x; if(x>maxX)maxX=x; if(y<minY)minY=y; if(y>maxY)maxY=y; }
  }
  if (!any) return JSON.stringify({ ok:false });
  const p = im.pixelsPerUnit || 1;
  return JSON.stringify({
    ok:true, pixelsPerUnit:p,
    displayWH:[im.width, im.height],
    contentLocal:[+minX.toFixed(1), +minY.toFixed(1), +(maxX-minX).toFixed(1), +(maxY-minY).toFixed(1)],
    // 转为 _handleClick 使用的归一化空间（相对 _fit 的 0.._srcW / 0.._srcH）
    contentNorm:[+(minX/L._srcW).toFixed(4), +(minY/L._srcH).toFixed(4),
                 +(maxX/L._srcW).toFixed(4), +(maxY/L._srcH).toFixed(4)],
    srcWH:[L._srcW, L._srcH],
  });
})()`;

app.whenReady().then(async () => {
  const win = new BrowserWindow({
    width: 1440, height: 950, show: false,
    webPreferences: { contextIsolation: true, nodeIntegration: false, sandbox: false },
  });
  const js = (c) => win.webContents.executeJavaScript(c);
  const log = (...a) => console.log(a.join(" "));

  try {
    await win.loadURL(BASE + "/index.html");
    await wait(3500);
    await js(SETUP);

    for (const id of ["314701", "314704"]) {
      await js(`window.RoleplayLive2D.switchModel("${id}")`);
      await wait(1300);

      const c = JSON.parse(await js(CONTENT));
      log("=".repeat(80));
      log("模型 " + id);
      log("  pixelsPerUnit=" + c.pixelsPerUnit + "  display=" + JSON.stringify(c.displayWH)
          + "  _srcWH=" + JSON.stringify(c.srcWH));
      log("  内容(局部坐标)   " + JSON.stringify(c.contentLocal));
      log("  内容(归一化空间) x " + c.contentNorm[0] + ".." + c.contentNorm[2]
          + "   y " + c.contentNorm[1] + ".." + c.contentNorm[3] + "   (理想 0..1)");

      // 画布 CSS 尺寸
      const dim = JSON.parse(await js(`JSON.stringify({
        w: window.RoleplayLive2D._container.clientWidth,
        h: window.RoleplayLive2D._container.clientHeight })`));
      log("  画布 CSS " + dim.w + "x" + dim.h);

      // 网格点击：把画布按 10x10 打点，标注命中区域
      const COLS = 12, ROWS = 14;
      const grid = [];
      for (let r = 0; r < ROWS; r++) {
        const row = [];
        for (let cc = 0; cc < COLS; cc++) {
          const x = (cc + 0.5) * dim.w / COLS;
          const y = (r + 0.5) * dim.h / ROWS;
          const res = JSON.parse(await js(`(${CLICK})(${x.toFixed(1)}, ${y.toFixed(1)})`));
          row.push(res.region);
        }
        grid.push(row);
      }
      const sym = { head: "H", body: "B", lower: "L", null: "." };
      log("  网格点击命中（H=头 B=身 L=下摆 .=无区域，画布 12x14，上->下）:");
      log("     " + "-".repeat(COLS));
      grid.forEach((row, r) => {
        log("     " + row.map((g) => sym[g] || "?").join(""));
      });
      log("     " + "-".repeat(COLS));

      // 统计
      const cnt = {};
      for (const row of grid) for (const g of row) cnt[g || "none"] = (cnt[g || "none"] || 0) + 1;
      log("  命中统计: " + JSON.stringify(cnt));
    }
  } catch (e) {
    console.error("失败: " + ((e && e.message) || e));
  }
  app.exit(0);
});
