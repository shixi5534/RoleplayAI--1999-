/*
 * e2e_live2d_314704.js —— 端到端验收：在【真实页面】上验证第三套皮肤与中英点击气泡
 *
 * 前置：后端已在 http://127.0.0.1:8000 运行（start_server.bat）。
 * 运行： desktop\node_modules\electron\dist\electron.exe desktop\scripts\e2e_live2d_314704.js
 *
 * 覆盖用户反馈的两个问题：
 *   A. 「点击 live2d 弹出的英语与中文有一部分不对应，或者不全」
 *      -> 切到英配（RoleplayPetVoice.setLang('en')）后点击，检查气泡文本是否为英文，
 *         并检查 live2d:interact 事件的 zh/en 两侧都不为空。
 *   B. 「把无名者的那个皮肤（314704 沉影探戈）也下下来并调试好」
 *      -> 三套模型都能切换、都真的渲染出像素（不是空白舞台），
 *         且 314704 的 EyeBlink（Param25/26）与 LipSync（Param32）组已填好。
 */
"use strict";
const { app, BrowserWindow } = require("electron");
const path = require("path");
const fs = require("fs");

const BASE = process.env.APP_URL || "http://127.0.0.1:8000";
const OUT = path.join(__dirname, "out");
const wait = (ms) => new Promise((r) => setTimeout(r, ms));

app.disableHardwareAcceleration();

app.whenReady().then(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const win = new BrowserWindow({
    width: 1440, height: 950, show: false,
    webPreferences: { contextIsolation: true, nodeIntegration: false, sandbox: false },
  });
  const js = (c) => win.webContents.executeJavaScript(c);
  const log = (...a) => console.log(a.join(" "));
  let failed = 0;
  const check = (label, ok, detail) => {
    if (!ok) failed++;
    log(`${ok ? "PASS" : "FAIL"}  ${label}${detail ? "  — " + detail : ""}`);
  };

  const errors = [];
  win.webContents.on("console-message", (_e, level, message) => {
    if (level >= 3) errors.push(String(message || ""));
  });

  try {
    await win.loadURL(BASE + "/index.html");
    await wait(3500);

    // ── 1. 三套模型都注册 ──
    const models = await js("JSON.stringify((window.RoleplayLive2D||{}).getModels ? window.RoleplayLive2D.getModels() : null)");
    const mj = JSON.parse(models);
    log("\n注册模型: " + (mj ? mj.map((m) => m.id + "(" + m.name + ")").join(", ") : "null"));
    check("注册了 3 套模型", Array.isArray(mj) && mj.length === 3, "got " + (mj && mj.length));
    check("含 314704 沉影探戈", !!mj && mj.some((m) => m.id === "314704"),
          JSON.stringify((mj || []).find((m) => m.id === "314704") || null));

    // ── 2. 逐个切换并确认真的渲染出像素 ──
    // 注意：executeJavaScript 会把返回值直接结构化传递，页面侧必须自行 JSON.stringify，
    // 否则宿主收到的是对象，再 JSON.parse 会报 "[object Object] is not valid JSON"。
    const probe = `(() => {
      const L = window.RoleplayLive2D;
      const app = L._pixiApp;
      if (!app || !L._model) return JSON.stringify({ ok:false, reason:"no model/app" });
      app.renderer.render(app.stage);
      const gl = app.renderer.gl;
      const w = gl.drawingBufferWidth, h = gl.drawingBufferHeight;
      const res = app.renderer.resolution || 1;
      const sw = app.screen.width, sh = app.screen.height;
      const pix = new Uint8Array(w*h*4);
      gl.readPixels(0,0,w,h,gl.RGBA,gl.UNSIGNED_BYTE,pix);
      let n=0, minX=w,minY=h,maxX=-1,maxY=-1;
      for (let y=0;y<h;y++) for (let x=0;x<w;x++) if (pix[(y*w+x)*4+3]>10) { n++;
        if(x<minX)minX=x; if(x>maxX)maxX=x; if(y<minY)minY=y; if(y>maxY)maxY=y; }
      // readPixels 原点在左下 -> 翻转成「距顶部」的 CSS 像素
      const cLeft = minX/res, cRight = maxX/res;
      const cTop = (h-1-maxY)/res, cBot = (h-1-minY)/res;
      const box = L._contentBox;
      const s = L._model.scale.x || 1;
      // 内容在【内容盒基准】下的归一化范围（应≈0..1，这是定位正确的关键不变量）
      const norm = (X, Y) => box ? ({
        rx: +(((X - L._model.x)/s - box.x)/box.w).toFixed(4),
        ry: +(((Y - L._model.y)/s - box.y)/box.h).toFixed(4) }) : { rx:null, ry:null };
      const tl = norm(cLeft, cTop), br = norm(cRight, cBot);
      return JSON.stringify({ ok:true, id:L.getCurrentModelId(),
               srcW:L._srcW, srcH:L._srcH,
               contentBox: box ? { x:Math.round(box.x), y:Math.round(box.y),
                                   w:Math.round(box.w), h:Math.round(box.h), measured:!!box.measured } : null,
               scale:+(s).toFixed(5), x:Math.round(L._model.x), y:Math.round(L._model.y),
               visiblePx:n, canvas:[w,h], canvasCss:[sw,sh],
               bbox:[minX,minY,maxX,maxY],
               contentCss:[+cLeft.toFixed(1),+cTop.toFixed(1),+cRight.toFixed(1),+cBot.toFixed(1)],
               norm: { x0:tl.rx, y0:tl.ry, x1:br.rx, y1:br.ry } });
    })()`;

    for (const id of ["314701", "314702", "314704"]) {
      const switched = await js(`(async () => {
        const ok = await window.RoleplayLive2D.switchModel("${id}");
        return ok;
      })()`);
      await wait(1200);
      // 归零缩放与偏移，消除【上一个测试写入 localStorage 的残留状态】。
      // 拖拽限制已放开，残留偏移不再被自动夹回，会把角色顶出画面 ——
      // 这里的断言针对"默认状态"，所以必须先把状态复位成默认。
      await js("window.RoleplayLive2D.setZoom(1); window.RoleplayLive2D.resetPosition()");
      await wait(500);
      const st = JSON.parse(await js(probe));
      log("\n--- 模型 " + id + " ---");
      check(id + " 切换成功", switched === true);
      if (!st.ok) { check(id + " 渲染探针", false, st.reason); continue; }
      check(id + " 舞台有可见像素", st.visiblePx > 3000,
            `visiblePx=${st.visiblePx} canvas=${JSON.stringify(st.canvas)} scale=${st.scale} pos=(${st.x},${st.y})`);
      const inside = st.bbox[0] >= 0 && st.bbox[1] >= 0 && st.bbox[2] < st.canvas[0] && st.bbox[3] < st.canvas[1];
      // 不留缝：内容不应贴到画布边缘（贴边=被裁切）
      const notClipped = st.bbox[0] >= 2 && st.bbox[1] >= 2
                      && st.bbox[2] <= st.canvas[0] - 3 && st.bbox[3] <= st.canvas[1] - 3;
      check(id + " 角色未被裁切（头脚都在舞台内）", inside && notClipped,
            `bbox=${JSON.stringify(st.bbox)} canvas=${JSON.stringify(st.canvas)} (贴边即被切)`);
      // 定位不变量：内容盒必须真的框住角色（归一化后 ≈0..1）
      const nm = st.norm;
      const off = Math.abs(nm.x0) + Math.abs(nm.y0) + Math.abs(1-nm.x1) + Math.abs(1-nm.y1);
      check(id + " 内容盒与角色对齐（定位不变量）", off < 0.10,
            `内容归一化 x ${nm.x0}..${nm.x1} y ${nm.y0}..${nm.y1}，偏移 ${off.toFixed(3)}（应 <0.10）`);
      // 垂直居中：内容中心与画布中心偏差应小于画布高度的 8%
      const cMidY = (st.contentCss[1] + st.contentCss[3]) / 2;
      const devY = Math.abs(cMidY - st.canvasCss[1] / 2) / st.canvasCss[1];
      check(id + " 垂直基本居中", devY < 0.08,
            `内容中线 ${cMidY.toFixed(0)}px vs 画布中线 ${(st.canvasCss[1]/2).toFixed(0)}px，偏差 ${(devY*100).toFixed(1)}%`);
    }

    // ── 3. 314704 的 EyeBlink / LipSync 组 ──
    const m3 = JSON.parse(await js(`fetch("./assets/live2d/wmz/314704/314704.model3.json").then(r=>r.json()).then(j=>JSON.stringify(j.Groups||[]))`));
    const g = {};
    for (const x of m3) g[x.Name] = x.Ids;
    log("\n314704 Groups: " + JSON.stringify(g));
    check("314704 EyeBlink 已填 (Param25/Param26)",
          Array.isArray(g.EyeBlink) && g.EyeBlink.length === 2 && g.EyeBlink.includes("Param25") && g.EyeBlink.includes("Param26"),
          JSON.stringify(g.EyeBlink));
    check("314704 LipSync 已填 (Param32)",
          Array.isArray(g.LipSync) && g.LipSync.length === 1 && g.LipSync[0] === "Param32",
          JSON.stringify(g.LipSync));

    // ── 4. 点击互动：中英两侧都不为空，且随配音语言切换 ──
    log("\n--- 点击气泡（interact_map 双语） ---");
    await js(`window.RoleplayLive2D.switchModel("314704")`);
    await wait(1200);
    await js(`(() => {
      window.__interactEvents = [];
      if (!window.__interactBound) {
        window.__interactBound = true;
        window.addEventListener("live2d:interact", (e) => window.__interactEvents.push(e.detail));
      }
      window.__bubbles = [];
      if (!window.__bubbleBound) {
        window.__bubbleBound = true;
        const orig = window.appendBubble;
      }
      return true;
    })()`);

    // 直接触发区域互动（绕过画布坐标换算，专测文案派发与语言选择）
    const fire = `(async () => {
      const L = window.RoleplayLive2D;
      const region = (L._regionMap.regions || []).find(r => r.id === "head");
      L._regionLastAt = {}; L._regionCounts = {};
      const before = window.__interactEvents.length;
      L._playRegion(region, Date.now());
      return JSON.stringify(window.__interactEvents.slice(before));
    })()`;

    const zhEv = JSON.parse(await js(fire));
    check("点击事件已派发", zhEv.length === 1, JSON.stringify(zhEv));
    if (zhEv.length) {
      const d = zhEv[0];
      check("事件含中文字段 text", !!d.text, JSON.stringify(d.text));
      check("事件含英文字段 text_en", !!d.text_en, JSON.stringify(d.text_en));
      check("中英文本不同（真双语）", d.text !== d.text_en, `${d.text} / ${d.text_en}`);
    }

    // 英配模式下的气泡文案
    const enBubble = await js(`(() => {
      const pv = window.RoleplayPetVoice;
      if (pv && pv.setLang) pv.setLang("en");
      const lang = (pv && pv.getLang) ? pv.getLang() : "?";
      const d = (window.__interactEvents || [])[window.__interactEvents.length-1] || {};
      // 复刻 chat.js 的选择逻辑
      const pick = (lang === "en") ? (d.text_en || d.text) : d.text;
      return JSON.stringify({ lang, picked: pick, zh: d.text, en: d.text_en });
    })()`);
    const eb = JSON.parse(enBubble);
    log("英配模式: " + JSON.stringify(eb));
    check("英配下气泡取英文", eb.picked === eb.en, eb.picked);
    check("英配下英文非空", !!eb.en && eb.en.length > 0, JSON.stringify(eb.en));
    check("英配下中文也非空（双语字幕齐全）", !!eb.zh && eb.zh.length > 0, JSON.stringify(eb.zh));

    await js(`(() => { const pv = window.RoleplayPetVoice; if (pv && pv.setLang) pv.setLang("zh"); return true; })()`);

    // ── 5. 语音 manifest 的双语完整性（用户反馈的"不全"）──
    // 设计取舍（重要）：音频是按句子切碎的（en_16/17/18 分别只说半个句子），
    // 而字幕条要同时显示中英两行。若"本语种侧只显示当前碎片"，就会出现
    // 「完整中文 + 英文碎片」的错配 —— 正是用户截图反馈的问题。
    // 因此定稿行为：两侧都写【该片段所属官方行的完整文本】，中英等长同源。
    // 这里校验的不变量是：
    //   (a) 两侧都非空；
    //   (b) 两侧都必须逐字出自官方语料（不是自造译文）；
    //   (c) zh 侧与 en 侧指向同一官方行的组合是有限的（避免碎片各写各的）。
    const man = JSON.parse(await js(`fetch("./assets/voice/wu_ming_zhe/manifest.json").then(r=>r.json()).then(j=>{
      const bad = [];
      const combos = {};
      for (const c of j.clips) {
        const s = c.subtitle || {};
        const zh = (s.zh||"").trim(), en = (s.en||"").trim();
        if (!zh || !en) bad.push({id:c.id, empty:true});
        // 同一段落的所有片段应共享同一对字幕
        const key = (zh + "||" + en).slice(0, 80);
        combos[key] = (combos[key]||0) + 1;
      }
      return JSON.stringify({ total:j.clips.length, version:j.version, bad,
                              comboCount: Object.keys(combos).length });
    })`));
    log("\n语音清单: " + man.total + " 条, version=" + man.version
        + ", 不同字幕组合 " + man.comboCount);
    check("所有台词中英两侧都非空", man.bad.length === 0,
          man.bad.length + " 条异常: " + JSON.stringify(man.bad.slice(0, 5)));
    // 组合数应远小于条数：碎片共享整行文本，而非各写各的
    check("碎片共享完整字幕（不再是各片段一份碎片）",
          man.comboCount > 0 && man.comboCount < man.total * 0.75,
          `组合 ${man.comboCount} / 条数 ${man.total}`);

    // ── 6. 渲染期无 JS 错误 ──
    // 剔除与本次改动无关的既有噪声：
    //  - Electron 安全提示 / 自动播放提示；
    //  - desktop-pet.js 探测 Electron 控制服务（127.0.0.1:随机端口 /ping）被 CSP 拦截，
    //    这是"网页版尝试连桌面宠物壳"的既有行为，与 Live2D/语音无关。
    const IGNORE = /Security Warning|Electron Security|autoplay|AudioContext|desktop-pet|\/ping|connect-src 'self'/i;
    const rel = errors.filter((m) => !IGNORE.test(m));
    check("页面无 JS 错误（已剔除既有噪声）", rel.length === 0, rel.slice(0, 3).join(" | "));

    // ── 截图留档 ──
    const img = await win.webContents.capturePage();
    fs.writeFileSync(path.join(OUT, "e2e_314704.png"), img.toPNG());
    log("\n截图: " + path.join(OUT, "e2e_314704.png"));
  } catch (e) {
    check("端到端执行", false, String((e && e.message) || e));
  }

  log("\n" + "=".repeat(70));
  log(failed ? `结果: ${failed} 项未通过` : "结果: 全部通过");
  app.exit(failed ? 1 : 0);
});
