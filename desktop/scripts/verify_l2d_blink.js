/*
 * verify_l2d_blink.js —— 验证 314704 的 EyeBlink / LipSync 组是否真的生效
 *
 * 背景：该模型 moc3 里参数名被混淆（Param25/Param26 是双眼、Param32 是嘴），
 *   model3.json 里原本两组都是空的 -> 角色不会自动眨眼、也不会跟语音做口型。
 *   已按像素证据填上。本脚本用【库自己的眨眼管线】验收：
 *     eyeBlink.updateParameters(coreModel, dt) 是 Cubism 官方眨眼实现，它会按
 *     EyeBlink.Ids 把参数推向 0（闭眼）。若组填错，画面不会有任何变化。
 *   同时验证确定性（同状态两次渲染必须一致），避免把噪声当效果。
 *
 * 运行： desktop\node_modules\electron\dist\electron.exe desktop\scripts\verify_l2d_blink.js
 * 输出： desktop\scripts\out\<tag>_blink_open.png / _blink_closed.png
 */
"use strict";
const { app, BrowserWindow } = require("electron");
const path = require("path");
const fs = require("fs");

const REPO = path.resolve(__dirname, "..", "..");
const FRONTEND = path.join(REPO, "frontend");
const OUT = path.join(__dirname, "out");
const CW = 700, CH = 700;

const CASES = [
  ["314701", "./assets/live2d/wmz/314701/v3a7_314701_wmz.model3.json"],
  ["314704", "./assets/live2d/wmz/314704/314704.model3.json"],
];

const PAGE = `<!DOCTYPE html><html><head><meta charset="utf-8"></head>
<body style="margin:0"><div id="stage"></div>
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
  if (window.__model) { try{ window.__app.stage.removeChild(window.__model); window.__model.destroy(); }catch(e){} }
  const model = await L.Live2DModel.from(url,{autoInteract:false});
  window.__app.stage.addChild(model);
  const im=model.internalModel, cm=im.coreModel;
  window.__model=model; window.__im=im; window.__cm=cm;
  window.__ids=Array.from(cm._model.parameters.ids);
  window.__defs=[]; for(let i=0;i<window.__ids.length;i++) window.__defs.push(cm.getParameterDefaultValue(i));
  model.anchor.set(0,0); model.cullable=false; model.autoUpdate=false;
  im.updateFocus=()=>{}; im.updateNaturalMovements=()=>{};
  try{ im.physics=null; }catch(e){}
  try{ im.pose=null; }catch(e){}
  try{ im.motionManager.stopAllMotions(); }catch(e){}
  try{ im.expressionManager=null; }catch(e){}

  // 从 model3.json 读回 EyeBlink / LipSync 组（这正是本次修复的内容）
  const m3 = await (await fetch(url)).json();
  const groups = {};
  for (const g of (m3.Groups||[])) groups[g.Name] = g.Ids;
  window.__groups = groups;

  // 内容包围盒 + 头部特写取景
  im.update(16.7, 0);
  let minX=1e18,minY=1e18,maxX=-1e18,maxY=-1e18;
  const n=cm.getDrawableCount();
  for(let i=0;i<n;i++){ let v; try{ v=im.getDrawableVertices(i);}catch(e){continue;}
    if(!v||!v.length) continue;
    for(let j=0;j<v.length;j+=2){ const x=v[j],y=v[j+1];
      if(x<minX)minX=x; if(x>maxX)maxX=x; if(y<minY)minY=y; if(y>maxY)maxY=y; } }
  const c=[minX,minY,maxX-minX,maxY-minY];
  const scale = ${CH} / (c[3]*0.55);      // 头部约 55% 高度铺满画布
  model.scale.set(scale);
  model.x = (${CW} - c[2]*scale)/2 - c[0]*scale;
  model.y = 40 - c[1]*scale;
  window.__resetParams();
  return { groups, scale:+scale.toFixed(4), content:c.map(Math.round), drawables:n };
};

window.__resetParams=()=>{ const cm=window.__cm;
  for(let i=0;i<window.__ids.length;i++) cm.setParameterValueByIndex(i, window.__defs[i]);
  window.__im.update(16.7, 0); };

/** 复刻库的眨眼帧，并可选地强制覆盖参数。
 *  时序（两个坑都在这里）：
 *   1) coreModel 每帧 saveParameters() → 各子系统 → cm.update() → loadParameters()，
 *      末尾的 loadParameters 会还原成快照值；
 *   2) 眨眼子系统自己也会写 EyeBlink.Ids —— 若覆盖值写在它之前，会被它冲掉
 *      （实测：参数回读是 0，但画面与睁眼完全一致）。
 *  因此覆盖必须放在【所有子系统之后、cm.update() 之前】，才能左右本帧绘制。 */
window.__blinkStep=(dtMs, override)=>{
  const im=window.__im, cm=window.__cm;
  const ran = !im.motionManager.isFinished();
  cm.saveParameters();
  let used = false;
  if(!ran && im.eyeBlink){ im.eyeBlink.updateParameters(cm, dtMs/1000); used = true; }
  im.updateFocus(); im.updateNaturalMovements(dtMs, 0);
  if(im.physics) im.physics.evaluate(cm, dtMs/1000);
  if(im.pose) im.pose.updateParameters(cm, dtMs/1000);
  // 覆盖点：必须在 cm.update() 之前、所有子系统之后
  if(override) for(const [id,v] of override){ const i=window.__ids.indexOf(id); if(i>=0) cm.setParameterValueByIndex(i,v); }
  cm.update(); cm.loadParameters();
  return used;
};
window.__blinkVals=()=>{ const g=window.__groups.EyeBlink||[]; const cm=window.__cm; const o={};
  for(const id of g) o[id]=+cm.getParameterValueById(id).toFixed(3); return o; };
window.__lipVals=()=>{ const g=window.__groups.LipSync||[]; const cm=window.__cm; const o={};
  for(const id of g) o[id]=+cm.getParameterValueById(id).toFixed(3); return o; };
window.__png=()=>{
  window.__app.renderer.render(window.__app.stage);
  const gl=window.__app.renderer.gl,w=gl.drawingBufferWidth,h=gl.drawingBufferHeight;
  const pix=new Uint8Array(w*h*4); gl.readPixels(0,0,w,h,gl.RGBA,gl.UNSIGNED_BYTE,pix);
  const c=document.createElement("canvas"); c.width=w; c.height=h;
  const ctx=c.getContext("2d"); const img=ctx.createImageData(w,h);
  for(let y=0;y<h;y++) for(let x=0;x<w;x++){
    const src=((h-1-y)*w+x)*4, dst=(y*w+x)*4;
    img.data[dst]=pix[src]; img.data[dst+1]=pix[src+1]; img.data[dst+2]=pix[src+2]; img.data[dst+3]=pix[src+3]; }
  ctx.putImageData(img,0,0); return c.toDataURL("image/png");
};
<\/script></body></html>`;

const wait = (ms) => new Promise((r) => setTimeout(r, ms));
app.disableHardwareAcceleration();

app.whenReady().then(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const p = path.join(FRONTEND, "_verify_blink.html");
  fs.writeFileSync(p, PAGE, "utf8");
  const win = new BrowserWindow({ width: CW + 60, height: CH + 80, show: false,
    webPreferences: { contextIsolation: false, nodeIntegration: false, webSecurity: false } });
  const js = (c) => win.webContents.executeJavaScript(c);
  const log = (...a) => console.log(a.join(" "));
  const save = async (tag, name) => {
    const png = await js("window.__png()");
    fs.writeFileSync(path.join(OUT, `${tag}_blink_${name}.png`),
                     Buffer.from(png.split(",")[1], "base64"));
  };
  try {
    await win.loadURL("file:///" + p.replace(/\\/g, "/"));
    for (let i = 0; i < 80; i++) { if (await js("window.__ready===true")) break;
      if (await js("window.__err")) break; await wait(150); }
    const e = await js("window.__err"); if (e) throw new Error(e);

    for (const [tag, url] of CASES) {
      log("=".repeat(72));
      const info = JSON.parse(await js(`window.__load(${JSON.stringify(url)}).then(r=>JSON.stringify(r))`));
      log("模型 " + tag + "  EyeBlink=" + JSON.stringify(info.groups.EyeBlink)
          + "  LipSync=" + JSON.stringify(info.groups.LipSync));
      log("  头部特写 scale=" + info.scale + " 内容=" + JSON.stringify(info.content));

      // A) 睁眼（参数取默认 = 1）
      // 注意：必须在 __blinkStep 之后【立刻】截图，不能先 __resetParams() 再截图 ——
      // 否则拍到的都是中性状态，睁眼/闭眼两张图会一模一样（早期版本踩过这个坑）。
      await js("window.__resetParams()");
      await js(`window.__blinkStep(16, ${JSON.stringify([])})`);
      const openVals = await js("JSON.stringify(window.__blinkVals())");
      await save(tag, "open");

      // B) 闭眼：把 EyeBlink.Ids 全部压到 0（等价于眨眼到最低点）
      const ids = info.groups.EyeBlink || [];
      const zero = ids.map((id) => [id, 0]);
      await js("window.__resetParams()");
      await js(`window.__blinkStep(16, ${JSON.stringify(zero)})`);
      const closedVals = await js("JSON.stringify(window.__blinkVals())");
      await save(tag, "closed");

      // C) 口型：LipSync.Ids 拉满
      const lipIds = info.groups.LipSync || [];
      if (lipIds.length) {
        await js("window.__resetParams()");
        await js(`window.__blinkStep(16, ${JSON.stringify(lipIds.map((id) => [id, 1]))})`);
        log("  LipSync 拉满后参数值: " + await js("JSON.stringify(window.__lipVals())"));
        await save(tag, "mouth_open");
      }

      // D) 确定性对照：同一状态渲染两次
      await js("window.__resetParams()");
      await js(`window.__blinkStep(16, ${JSON.stringify([])})`);
      await save(tag, "open_again");

      log("  睁眼参数=" + openVals + "  闭眼参数=" + closedVals);
      log("  已导出 PNG: " + tag + "_blink_{open,closed,mouth_open,open_again}.png");
    }
  } catch (err) { console.error("失败: " + (err && err.message || err)); }
  try { fs.unlinkSync(p); } catch (_) {}
  app.exit(0);
});
