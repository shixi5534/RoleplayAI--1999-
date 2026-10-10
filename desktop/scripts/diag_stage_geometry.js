/*
 * diag_stage_geometry.js —— 量「canvas 尺寸 vs 舞台可见区域」是否一致
 *
 * 关键假设（待验证）：模型在 canvas 内摆放其实是正确的（四周都有留白），
 *   但 canvas 本身比舞台容器【高】，于是顶部（头顶）被容器/布局裁掉 ——
 *   这正好解释「包围盒没贴边，但肉眼看到头被切」。
 *
 * 量什么：
 *   - 容器 clientWidth/Height 与 getBoundingClientRect()
 *   - canvas 元素的 CSS 尺寸与 backing store 尺寸
 *   - _pixiApp.screen 尺寸（_fit 用的量纲）
 *   - canvas 相对容器的实际位置（偏移=错位/溢出）
 *   - 容器与各祖先的 overflow / 尺寸约束
 *
 * 前置：后端已在 http://127.0.0.1:8000 运行。
 * 运行： desktop\node_modules\electron\dist\electron.exe desktop\scripts\diag_stage_geometry.js
 */
"use strict";
const { app, BrowserWindow } = require("electron");
const path = require("path");

const BASE = process.env.APP_URL || "http://127.0.0.1:8000";
const wait = (ms) => new Promise((r) => setTimeout(r, ms));
app.disableHardwareAcceleration();

const PROBE = `(() => {
  const L = window.RoleplayLive2D;
  const el = L._container, app = L._pixiApp;
  const view = app && app.view;
  const r = el.getBoundingClientRect();
  const vr = view.getBoundingClientRect();
  const cs = getComputedStyle(el);
  const vcs = view ? getComputedStyle(view) : null;
  // 往上找会裁剪的祖先
  const clippers = [];
  let p = el.parentElement, depth = 0;
  while (p && depth < 6) {
    const c = getComputedStyle(p);
    const pr = p.getBoundingClientRect();
    clippers.push({
      tag: p.tagName + (p.id ? "#" + p.id : "") + (p.className && typeof p.className === "string" ? "." + p.className.trim().split(/\\s+/).slice(0,2).join(".") : ""),
      size: [Math.round(pr.width), Math.round(pr.height)],
      overflow: c.overflow + "/" + c.overflowY,
      position: c.position,
    });
    p = p.parentElement; depth++;
  }
  return JSON.stringify({
    container: {
      client: [el.clientWidth, el.clientHeight],
      rect: [Math.round(r.left), Math.round(r.top), Math.round(r.width), Math.round(r.height)],
      overflow: cs.overflow + "/" + cs.overflowY,
      position: cs.position,
    },
    canvas: view ? {
      cssSize: [Math.round(vr.width), Math.round(vr.height)],
      cssPos: [Math.round(vr.left), Math.round(vr.top)],
      attrSize: [view.width, view.height],
      styleWH: [view.style.width, view.style.height],
      position: vcs.position,
      top: vcs.top,
      marginTop: vcs.marginTop,
    } : null,
    pixiScreen: app ? [Math.round(app.screen.width), Math.round(app.screen.height)] : null,
    pixiResolution: app ? app.renderer.resolution : null,
    modelScale: L._model ? +L._model.scale.x.toFixed(6) : null,
    modelPos: L._model ? [Math.round(L._model.x), Math.round(L._model.y)] : null,
    contentBox: L._contentBox ? { x:Math.round(L._contentBox.x), y:Math.round(L._contentBox.y),
                                  w:Math.round(L._contentBox.w), h:Math.round(L._contentBox.h) } : null,
    modelWH: L._model ? [Math.round(L._model.width), Math.round(L._model.height)] : null,
    ancestors: clippers,
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
    for (const id of ["314701", "314704"]) {
      await js(`window.RoleplayLive2D.switchModel("${id}")`);
      await wait(1400);
      const g = JSON.parse(await js(PROBE));
      log("=".repeat(78));
      log("模型 " + id);
      log("  容器 client   " + JSON.stringify(g.container.client)
          + "  rect " + JSON.stringify(g.container.rect)
          + "  overflow=" + g.container.overflow + " position=" + g.container.position);
      log("  canvas CSS    " + JSON.stringify(g.canvas.cssSize)
          + "  @ " + JSON.stringify(g.canvas.cssPos)
          + "  attr " + JSON.stringify(g.canvas.attrSize)
          + "  style " + JSON.stringify(g.canvas.styleWH));
      log("  canvas 定位   top=" + g.canvas.top + " marginTop=" + g.canvas.marginTop
          + " position=" + g.canvas.position);
      log("  pixi screen   " + JSON.stringify(g.pixiScreen) + "  resolution " + g.pixiResolution);
      log("  模型 scale/pos " + g.modelScale + " " + JSON.stringify(g.modelPos)
          + "  model.wh " + JSON.stringify(g.modelWH));
      log("  内容盒        " + JSON.stringify(g.contentBox));
      // 关键判据：canvas 是否高于容器 / 是否偏离容器原点
      const dH = g.canvas.cssSize[1] - g.container.client[1];
      const dy = g.canvas.cssPos[1] - g.container.rect[1];
      log("  >> canvas 高 - 容器高 = " + dH + (Math.abs(dH) > 2 ? "   <<< 尺寸不一致" : "  (一致)"));
      log("  >> canvas top - 容器 top = " + dy + (Math.abs(dy) > 2 ? "   <<< 位置偏移" : "  (对齐)"));
      log("  祖先链:");
      for (const a of g.ancestors) {
        log("     " + a.tag.padEnd(34) + " " + JSON.stringify(a.size)
            + "  overflow=" + a.overflow + "  position=" + a.position);
      }
    }
  } catch (e) {
    console.error("失败: " + ((e && e.message) || e));
  }
  app.exit(0);
});
