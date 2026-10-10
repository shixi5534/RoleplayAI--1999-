/*
 * audit_l2d_fit.js —— 审计三套模型的「布局框 vs 真实内容」与 _fit() 摆放结果
 *
 * 目的：live2d.js 的 _fit() 用 getLocalBounds() 做居中、用 internalModel 尺寸做缩放。
 *   如果某个模型的 getLocalBounds() 与真实绘制内容对不上（内容跑到布局框之外），
 *   _fit() 会把模型摆到画布外，表现为「舞台空白」。本脚本对三套模型逐一比较：
 *     - internalModel 尺寸 / getLocalBounds()
 *     - 真实内容包围盒（由 drawable 顶点并集算出，模型空间）
 *     - 按 _fit() 公式算出的摆放，以及该摆放下的实际可见像素
 *
 * 运行： desktop\node_modules\electron\dist\electron.exe desktop\scripts\audit_l2d_fit.js
 */
"use strict";
const { app, BrowserWindow } = require("electron");
const path = require("path");
const fs = require("fs");

const REPO = path.resolve(__dirname, "..", "..");
const FRONTEND = path.join(REPO, "frontend");
const CW = 360, CH = 480;   // 与聊天页舞台接近的尺寸

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
(async () => {
 try {
  const L=window.PIXI.live2d; L.startUpCubism4();
  const app=new PIXI.Application({width:${CW},height:${CH},backgroundAlpha:0,antialias:false,autoDensity:true,resolution:1});
  document.getElementById("stage").appendChild(app.view);
  window.__app=app;
  window.__ready=true;
 } catch(e){ window.__err=String(e&&e.stack||e); }
})();

window.__load = async (url) => {
  const L=window.PIXI.live2d;
  const model = await L.Live2DModel.from(url, {autoInteract:false});
  window.__app.stage.addChild(model);
  const im=model.internalModel, cm=im.coreModel;
  im.updateFocus=()=>{}; im.updateNaturalMovements=()=>{};
  try{ im.eyeBlink=null; }catch(e){}
  try{ im.physics=null; }catch(e){}
  try{ im.pose=null; }catch(e){}
  try{ im.motionManager.stopAllMotions(); }catch(e){}
  if (window.__prev) { window.__app.stage.removeChild(window.__prev); try{window.__prev.destroy();}catch(e){} }
  window.__prev = model;

  const b = model.getLocalBounds();
  const imW = im.width, imH = im.height;

  // 真实内容包围盒：并集所有 drawable 的顶点（模型局部坐标，已含 PixelsPerUnit 换算）
  let cminX=1e18,cminY=1e18,cmaxX=-1e18,cmaxY=-1e18, any=false;
  const n = cm.getDrawableCount();
  for (let i=0;i<n;i++) {
    let v;
    try { v = im.getDrawableVertices(i); } catch(e) { continue; }
    if (!v || !v.length) continue;
    for (let j=0;j<v.length;j+=2) {
      any=true;
      const x=v[j], y=v[j+1];
      if(x<cminX)cminX=x; if(x>cmaxX)cmaxX=x; if(y<cminY)cminY=y; if(y>cmaxY)cmaxY=y;
    }
  }
  window.__cur = model;
  return { imW, imH,
           localBounds:[b.x,b.y,b.width,b.height],
           content: any ? [cminX,cminY,cmaxX-cminX,cmaxY-cminY] : null,
           drawables:n };
};

/** 复刻 live2d.js 的 _fit() 公式，返回摆放 + 该摆放下的可见像素 */
window.__fitLike = () => {
  const app=window.__app, model=window.__cur;
  const w=app.screen.width, h=app.screen.height;
  const im=model.internalModel, cm=im.coreModel;
  const iw=im.width, ih=im.height;
  let s=Math.min(w/iw, h/ih)*0.92;
  model.scale.set(s);
  const b=model.getLocalBounds();
  const bw=(b&&isFinite(b.width)&&b.width>0)?b.width:iw;
  const bh=(b&&isFinite(b.height)&&b.height>0)?b.height:ih;
  const bx=(b&&isFinite(b.x))?b.x:0, by=(b&&isFinite(b.y))?b.y:0;
  model.x=(w-bw*s)/2 - bx*s;
  model.y=(h-bh*s)/2 - by*s;
  const px=window.__stats();
  return { scale:+s.toFixed(6), x:+model.x.toFixed(1), y:+model.y.toFixed(1),
           iw, ih, bw:+bw.toFixed(0), bh:+bh.toFixed(0), bx:+bx.toFixed(0), by:+by.toFixed(0),
           visiblePx:px.n, bbox:px.bbox, canvas:[px.w,px.h] };
};
window.__stats = () => {
  const app=window.__app; app.renderer.render(app.stage);
  const gl=app.renderer.gl,w=gl.drawingBufferWidth,h=gl.drawingBufferHeight;
  const pix=new Uint8Array(w*h*4); gl.readPixels(0,0,w,h,gl.RGBA,gl.UNSIGNED_BYTE,pix);
  let n=0,minX=w,minY=h,maxX=-1,maxY=-1;
  for(let i=0;i<w*h;i++) if(pix[i*4+3]>10){n++; const x=i%w,y=(i/w)|0;
    if(x<minX)minX=x; if(x>maxX)maxX=x; if(y<minY)minY=y; if(y>maxY)maxY=y;}
  return {n,bbox:[minX,minY,maxX,maxY],w,h};
};
/** 穷举搜索：是否存在任何摆放能让整只完整入画（判断"是否只是 _fit 的问题"） */
window.__searchFit = () => {
  const app=window.__app, model=window.__cur;
  const w=app.screen.width,h=app.screen.height;
  const im=model.internalModel;
  model.cullable=false;
  for (const s of [0.02,0.04,0.06,0.08,0.12]) {
    for (let y=-8000; y<=20000; y+=2000) {
      model.scale.set(s); model.x=0; model.y=y;
      const st=window.__stats();
      if (st.n<300) continue;
      const [a0,a1,b0,b1]=st.bbox;
      if (a0>0&&a1>0&&b0<st.w-1&&b1<st.h-1) return {found:true,scale:s,y,x:0,bbox:st.bbox,n:st.n};
    }
  }
  return {found:false};
};
<\/script></body></html>`;

const wait = (ms) => new Promise((r) => setTimeout(r, ms));
app.disableHardwareAcceleration();

app.whenReady().then(async () => {
  const p = path.join(FRONTEND, "_audit_fit.html");
  fs.writeFileSync(p, PAGE, "utf8");
  const win = new BrowserWindow({ width: CW + 80, height: CH + 120, show: false,
    webPreferences: { contextIsolation: false, nodeIntegration: false, webSecurity: false } });
  const js = (c) => win.webContents.executeJavaScript(c);
  const log = (...a) => console.log(a.join(" "));
  try {
    await win.loadURL("file:///" + p.replace(/\\/g, "/"));
    for (let i = 0; i < 80; i++) { if (await js("window.__ready===true")) break;
      if (await js("window.__err")) break; await wait(150); }
    const e = await js("window.__err"); if (e) throw new Error(e);

    for (const [id, url] of MODELS) {
      log("=".repeat(80));
      log("模型 " + id + "   画布 " + CW + "x" + CH);
      const info = await js(`window.__load(${JSON.stringify(url)}).then(r=>JSON.stringify(r))`);
      const ij = JSON.parse(info);
      log("  internalModel 尺寸      : " + ij.imW + " x " + ij.imH);
      log("  getLocalBounds()        : " + JSON.stringify(ij.localBounds));
      log("  真实内容包围盒(模型空间): " + JSON.stringify(ij.content && ij.content.map(v=>Math.round(v))));
      log("  drawable 数             : " + ij.drawables);
      if (ij.content) {
        const [cx, cy, cw, chh] = ij.content;
        const [lx, ly, lw, lh] = ij.localBounds;
        const insideX = cx >= lx - 1 && cx + cw <= lx + lw + 1;
        const insideY = cy >= ly - 1 && cy + chh <= ly + lh + 1;
        log("  内容是否落在布局框内    : x=" + insideX + " y=" + insideY
            + (insideX && insideY ? "   (一致)" : "   <<< 不一致，_fit 会摆错"));
      }
      const fit = await js("JSON.stringify(window.__fitLike())");
      const fj = JSON.parse(fit);
      log("  _fit() 结果             : scale=" + fj.scale + " pos=(" + fj.x + "," + fj.y + ")"
          + "  bw=" + fj.bw + " bh=" + fj.bh + " bx=" + fj.bx + " by=" + fj.by);
      log("  _fit() 后可见像素       : " + fj.visiblePx + "  bbox=" + JSON.stringify(fj.bbox));
      log("  => 舞台上" + (fj.visiblePx > 2000 ? "可见" : "<<< 空白/几乎不可见"));
      const sf = await js("JSON.stringify(window.__searchFit())");
      log("  是否存在其它可见摆放    : " + sf);
    }
  } catch (err) { console.error("失败: " + (err && err.message || err)); }
  try { fs.unlinkSync(p); } catch (_) {}
  app.exit(0);
});
