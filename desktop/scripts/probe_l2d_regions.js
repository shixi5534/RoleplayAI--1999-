/*
 * probe_l2d_regions.js —— 测出「头 / 身 / 下摆」在模型局部坐标里的真实位置
 *
 * 为什么需要：用户反馈「定位有问题」。已确认根因是两处都拿【布局框】当角色本体：
 *   1) _fit() 用 getLocalBounds()(=布局框) 居中 -> 角色被摆到画布上方并截顶；
 *   2) _handleClick() 用 _srcW/_srcH(=布局框) 归一化 -> interact_map 的 0..1 矩形
 *      与角色实际所在范围对不上。
 * 要把矩形改对，就必须先知道角色各部位到底在哪，而不是靠肉眼估。
 *
 * 方法（靠参数响应，不靠猜）：Cubism 里「头部转动」参数(ParamAngleX/Y/Z)只会驱动
 *   头与头发相关的 drawable，「呼吸」参数(ParamBreath)主要驱动躯干。于是：
 *     头 = 对 ParamAngle* 敏感的 drawable 顶点并集
 *     身 = 对 ParamBreath 敏感、且不属于头的 drawable 顶点并集
 *   下摆 = 内容底部区域
 *   这样得到的是模型作者自己定义的部位边界。
 *
 * 运行： desktop\node_modules\electron\dist\electron.exe desktop\scripts\probe_l2d_regions.js
 */
"use strict";
const { app, BrowserWindow } = require("electron");
const path = require("path");
const fs = require("fs");

const REPO = path.resolve(__dirname, "..", "..");
const FRONTEND = path.join(REPO, "frontend");
const OUT = path.join(__dirname, "out");

const MODELS = [
  ["314701", "./assets/live2d/wmz/314701/v3a7_314701_wmz.model3.json"],
  ["314702", "./assets/live2d/wmz/314702/v3a7_314702_wmz.model3.json"],
  ["314704", "./assets/live2d/wmz/314704/314704.model3.json"],
];

const PAGE = `<!DOCTYPE html><html><head><meta charset="utf-8"></head>
<body style="margin:0;background:#000"><div id="stage"></div>
<script src="./assets/lib/pixi.min.js"></script>
<script src="./assets/lib/live2dcubismcore.min.js"></script>
<script src="./assets/lib/pixi-live2d-display-cubism4.min.js"></script>
<script>
window.__ready=false; window.__err=null;
window.__app=null; window.__cur=null;
(async () => {
 try {
  const L=window.PIXI.live2d; L.startUpCubism4();
  const app=new PIXI.Application({width:900,height:1200,backgroundAlpha:0,antialias:false,autoDensity:true,resolution:1});
  document.getElementById("stage").appendChild(app.view);
  window.__app=app;
  window.__ready=true;
 } catch(e){ window.__err=String(e&&e.stack||e); }
})();

window.__load = async (url) => {
  const L=window.PIXI.live2d;
  if (window.__cur) { try{ window.__app.stage.removeChild(window.__cur); window.__cur.destroy(); }catch(e){} }
  const model = await L.Live2DModel.from(url,{autoInteract:false});
  window.__app.stage.addChild(model);
  const im=model.internalModel, cm=im.coreModel;
  window.__cur=model; window.__model=model; window.__im=im; window.__cm=cm;
  window.__ids=Array.from(cm._model.parameters.ids);
  window.__defs=[]; for(let i=0;i<window.__ids.length;i++) window.__defs.push(cm.getParameterDefaultValue(i));
  window.__n=cm.getDrawableCount();
  model.anchor.set(0,0); model.cullable=false;
  model.autoUpdate=false;                 // 由脚本手动驱动，保证时序可控
  im.updateFocus=()=>{}; im.updateNaturalMovements=()=>{};
  try{ im.eyeBlink=null; }catch(e){}
  try{ im.physics=null; }catch(e){}
  try{ im.pose=null; }catch(e){}
  try{ im.motionManager.stopAllMotions(); }catch(e){}
  try{ im.expressionManager=null; }catch(e){}
  // 布局框（_fit 与 _handleClick 当前使用的基准）
  const b=model.getLocalBounds();
  window.__layout=[b.x,b.y,b.width,b.height];
  window.__imWH=[im.width, im.height];
  return { layout: window.__layout, imWH: window.__imWH, drawables: window.__n };
};

window.__reset = () => {
  const cm=window.__cm, im=window.__im;
  for(let i=0;i<window.__ids.length;i++) cm.setParameterValueByIndex(i, window.__defs[i]);
  for(let f=0;f<3;f++) im.update(16.7, 0);
};
/** 每个 drawable 的顶点包围盒（局部坐标） */
window.__boxes = () => {
  const im=window.__im, out=[];
  for(let i=0;i<window.__n;i++){
    let v; try{ v=im.getDrawableVertices(i); }catch(e){ out.push(null); continue; }
    if(!v||!v.length){ out.push(null); continue; }
    let a=1e18,b=1e18,c=-1e18,d=-1e18;
    for(let j=0;j<v.length;j+=2){ const x=v[j],y=v[j+1];
      if(x<a)a=x; if(x>c)c=x; if(y<b)b=y; if(y>d)d=y; }
    let opa=1; try{ opa=window.__cm.getDrawableOpacity(i); }catch(e){}
    out.push([a,b,c,d,opa]);
  }
  return out;
};
/** 设置参数 -> 推进 -> 返回顶点盒（与基准比较即可找出被驱动的 drawable） */
window.__withParams = (pairs) => {
  const cm=window.__cm, im=window.__im;
  window.__reset();
  for(let f=0;f<4;f++){
    for(const [id,v] of pairs){ const i=window.__ids.indexOf(id); if(i>=0) cm.setParameterValueByIndex(i,v); }
    im.update(16.7, 0);
  }
  for(const [id,v] of pairs){ const i=window.__ids.indexOf(id); if(i>=0) cm.setParameterValueByIndex(i,v); }
  return window.__boxes();
};
window.__base = () => { window.__reset(); return window.__boxes(); };
<\/script></body></html>`;

const wait = (ms) => new Promise((r) => setTimeout(r, ms));
app.disableHardwareAcceleration();

/** 把若干 drawable 的盒子并成一个 */
function union(boxes, idxs) {
  let a = Infinity, b = Infinity, c = -Infinity, d = -Infinity, n = 0;
  for (const i of idxs) {
    const x = boxes[i];
    if (!x) continue;
    n++;
    if (x[0] < a) a = x[0];
    if (x[1] < b) b = x[1];
    if (x[2] > c) c = x[2];
    if (x[3] > d) d = x[3];
  }
  return n ? { x: a, y: b, w: c - a, h: d - b, n } : null;
}

function moved(base, now, thr) {
  const out = [];
  for (let i = 0; i < base.length; i++) {
    const A = base[i], B = now && now[i];
    if (!A || !B) continue;
    const d = Math.max(Math.abs(A[0] - B[0]), Math.abs(A[1] - B[1]),
                       Math.abs(A[2] - B[2]), Math.abs(A[3] - B[3]));
    if (d > thr) out.push(i);
  }
  return out;
}

app.whenReady().then(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const p = path.join(FRONTEND, "_probe_regions.html");
  fs.writeFileSync(p, PAGE, "utf8");
  const win = new BrowserWindow({ width: 960, height: 1260, show: false,
    webPreferences: { contextIsolation: false, nodeIntegration: false, webSecurity: false } });
  const js = (c) => win.webContents.executeJavaScript(c);
  const log = (...a) => console.log(a.join(" "));
  const report = {};

  try {
    await win.loadURL("file:///" + p.replace(/\\/g, "/"));
    for (let i = 0; i < 80; i++) { if (await js("window.__ready===true")) break;
      if (await js("window.__err")) break; await wait(150); }
    const e = await js("window.__err"); if (e) throw new Error(e);

    for (const [id, url] of MODELS) {
      log("=".repeat(84));
      const info = JSON.parse(await js(`window.__load(${JSON.stringify(url)}).then(r=>JSON.stringify(r))`));
      log("模型 " + id + "  布局框=" + JSON.stringify(info.layout.map(Math.round))
          + "  internalModel=" + JSON.stringify(info.imWH) + "  drawable=" + info.drawables);

      const base = JSON.parse(await js("JSON.stringify(window.__base())"));
      // 头：头转参数驱动
      const headNow = JSON.parse(await js(`JSON.stringify(window.__withParams([["ParamAngleX",30],["ParamAngleY",20],["ParamAngleZ",20]]))`));
      const headIdx = moved(base, headNow, 0.5);
      // 躯干：呼吸驱动，去掉头
      const brNow = JSON.parse(await js(`JSON.stringify(window.__withParams([["ParamBreath",1]]))`));
      const brIdx = moved(base, brNow, 0.5);
      const headSet = new Set(headIdx);
      const bodyIdx = brIdx.filter((i) => !headSet.has(i));

      const allIdx = [];
      const opaqueIdx = [];
      for (let i = 0; i < base.length; i++) {
        if (!base[i]) continue;
        allIdx.push(i);
        if ((base[i][4] || 0) >= 0.5) opaqueIdx.push(i);
      }
      const content = union(base, allIdx);
      const opaque = union(base, opaqueIdx);
      const head = union(base, headIdx);
      const body = union(base, bodyIdx);

      log("  全部 drawable 内容盒 " + JSON.stringify(content && {x:Math.round(content.x),y:Math.round(content.y),w:Math.round(content.w),h:Math.round(content.h)}));
      log("  不透明(op>=.5) 内容盒 " + JSON.stringify(opaque && {x:Math.round(opaque.x),y:Math.round(opaque.y),w:Math.round(opaque.w),h:Math.round(opaque.h)}));
      log("  头部盒 (头转驱动 " + headIdx.length + " 个) " + JSON.stringify(head && {x:Math.round(head.x),y:Math.round(head.y),w:Math.round(head.w),h:Math.round(head.h)}));
      log("  躯干盒 (呼吸驱动 " + bodyIdx.length + " 个) " + JSON.stringify(body && {x:Math.round(body.x),y:Math.round(body.y),w:Math.round(body.w),h:Math.round(body.h)}));

      if (content && head && body) {
        const f = (v, o, s) => +((v - o) / s).toFixed(4);
        log("  --- 相对【内容盒】的归一化矩形（interact_map 应该用的值）---");
        log("    head  rect = [" + f(head.x, content.x, content.w) + ", " + f(head.y, content.y, content.h)
            + ", " + (head.w / content.w).toFixed(4) + ", " + (head.h / content.h).toFixed(4) + "]");
        log("    body  rect = [" + f(body.x, content.x, content.w) + ", " + f(body.y, content.y, content.h)
            + ", " + (body.w / content.w).toFixed(4) + ", " + (body.h / content.h).toFixed(4) + "]");
        log("    lower rect = [" + f(body.x, content.x, content.w) + ", "
            + ((body.y + body.h - content.y) / content.h).toFixed(4) + ", " + (body.w / content.w).toFixed(4)
            + ", " + ((content.y + content.h - (body.y + body.h)) / content.h).toFixed(4) + "]");
        log("  --- 相对【布局框】的归一化（当前 interact_map 实际使用的空间）---");
        const L = info.layout;
        log("    内容盒落在布局框空间的 x " + f(content.x, L[0], L[2]).toFixed(3) + ".." + f(content.x + content.w, L[0], L[2]).toFixed(3)
            + "   y " + f(content.y, L[1], L[3]).toFixed(3) + ".." + f(content.y + content.h, L[1], L[3]).toFixed(3));
      }
      report[id] = { layout: info.layout, content, opaque, head, body };
    }
    fs.writeFileSync(path.join(OUT, "regions.json"), JSON.stringify(report, null, 1), "utf8");
    log("\n写入 " + path.join(OUT, "regions.json"));
  } catch (err) { console.error("失败: " + (err && err.message || err)); }
  try { fs.unlinkSync(p); } catch (_) {}
  app.exit(0);
});
