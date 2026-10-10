/*
 * measure_subtitle_baseline.js —— 独立量测字幕条的排版（不依赖子代理的结论）
 *
 * 用途：在真实页面上强制显示字幕，用 getBoundingClientRect / scrollWidth 等
 *   数字指标判断是否有溢出、裁切、遮挡 HUD、是否居中。测完输出 PASS/FAIL 与数值。
 *
 * 为什么不用肉眼：本会话无法直接看图，排版问题必须靠数值判定。
 *
 * 运行： desktop\node_modules\electron\dist\electron.exe desktop\scripts\measure_subtitle_baseline.js
 */
"use strict";
const { app, BrowserWindow } = require("electron");
const path = require("path");

const BASE = process.env.APP_URL || "http://127.0.0.1:8000";
const wait = (ms) => new Promise((r) => setTimeout(r, ms));
app.disableHardwareAcceleration();

// 在页面里：派发 pet:voice-line 强制显示字幕，然后量测
const MEASURE = `(testEn, testZh, dur) => {
  // 组件监听的是 window 上的 pet:voice-line
  window.dispatchEvent(new CustomEvent("pet:voice-line", {
    detail: {
      clip: { id: "probe", dur: dur, text: testEn },
      slot: "click", lang: "en",
      subtitle: { zh: testZh, en: testEn },
    },
  }));
  window.dispatchEvent(new CustomEvent("pet:voice-playing", {
    detail: { clip: { id: "probe", dur: dur, start: 0, end: dur } },
  }));
  // 注意：这里只是派发事件就立刻量测；显示后的第二次 syncGeometry 与 CSS 过渡
  // 需要一点时间才生效，所以调用方必须等一小段再读数值（否则测到的是过渡中的中间态）。
  return "dispatched";
}`;

/** 单独的量测函数：在事件派发 + 等待之后再调用，读到的是稳定态 */
const READOUT = `() => {
  const el = document.getElementById("pet-subtitle");
  if (!el) return JSON.stringify({ ok: false, reason: "no #pet-subtitle" });
  const stage = document.querySelector(".stage") || document.body;
  const hud = document.getElementById("stage-hud") || document.querySelector(".stage-hud");
  const r = el.getBoundingClientRect();
  const sr = stage.getBoundingClientRect();
  const hr = hud ? hud.getBoundingClientRect() : null;
  const zh = el.querySelector(".sub-zh");
  const en = el.querySelector(".sub-en");
  const cs = getComputedStyle(el);
  const csEn = en ? getComputedStyle(en) : null;
  const zr = zh ? zh.getBoundingClientRect() : null;
  const er = en ? en.getBoundingClientRect() : null;

  const overlapHud = hr ? !(r.bottom <= hr.top || r.top >= hr.bottom ||
                            r.right <= hr.left || r.left >= hr.right) : null;
  return JSON.stringify({
    ok: true,
    box:   { l: +r.left.toFixed(1), t: +r.top.toFixed(1), r: +r.right.toFixed(1), b: +r.bottom.toFixed(1),
             w: +r.width.toFixed(1), h: +r.height.toFixed(1) },
    stage: { l: +sr.left.toFixed(1), t: +sr.top.toFixed(1), r: +sr.right.toFixed(1), b: +sr.bottom.toFixed(1),
             w: +sr.width.toFixed(1), h: +sr.height.toFixed(1) },
    hud: hr ? { t: +hr.top.toFixed(1), b: +hr.bottom.toFixed(1), h: +hr.height.toFixed(1) } : null,
    spill: { left: +(sr.left - r.left).toFixed(1), right: +(r.right - sr.right).toFixed(1),
             top: +(sr.top - r.top).toFixed(1), bottom: +(r.bottom - sr.bottom).toFixed(1) },
    centreOffset: +(((r.left + r.right) / 2) - ((sr.left + sr.right) / 2)).toFixed(1),
    overlapHud: overlapHud,
    liftVar: cs.getPropertyValue("--sub-lift").trim(),
    maxhVar: cs.getPropertyValue("--sub-maxh").trim(),
    zh: zr ? { w: +zr.width.toFixed(1), h: +zr.height.toFixed(1),
               sw: zh.scrollWidth, cw: zh.clientWidth,
               sh: zh.scrollHeight, ch: zh.clientHeight } : null,
    en: er ? { w: +er.width.toFixed(1), h: +er.height.toFixed(1),
               sw: en.scrollWidth, cw: en.clientWidth,
               sh: en.scrollHeight, ch: en.clientHeight } : null,
    css: { overflowY: cs.overflowY, maxHeight: cs.maxHeight, width: cs.width, maxWidth: cs.maxWidth },
    cssEn: csEn ? { overflowWrap: csEn.overflowWrap, wordBreak: csEn.wordBreak,
                    whiteSpace: csEn.whiteSpace, display: csEn.display } : null,
    // 注入检查：文本里的 <b> 不应变成真实元素
    htmlInjected: !!el.querySelector("b"),
  });
}`;

const CASES = [
  ["短", "Hello there.", "你好。", 3],
  ["中", "I could handle some paperwork, or perhaps forge some documents, if that's needed.", "我可以为你处理一些文书书写工作，或者文书伪造工作。", 6],
  ["长(356字)", "I find that watching what people do here is a kind of entertainment in itself: some dance to disco music, some spend their afternoons playing tabletop games, and others watch horror films until they're left huddled up together with fear. Ah. I suppose it could just be that old habits die hard, but I'm still trying to learn what to do with my own time.", "我会观察箱子里的住客们平时会做些什么。", 9],
  ["无空格200", "A".repeat(200), "无空格测试", 5],
  ["超长1000", "B".repeat(1000), "超长测试", 5],
  ["含HTML", "<b>should not be an element</b>", "注入测试", 3],
];

app.whenReady().then(async () => {
  for (const [vw, vh] of [[1440, 950], [800, 600]]) {
    const win = new BrowserWindow({
      width: vw, height: vh, show: false,
      webPreferences: { contextIsolation: true, nodeIntegration: false, sandbox: false },
    });
    const js = (c) => win.webContents.executeJavaScript(c);
    const log = (...a) => console.log(a.join(" "));
    try {
      await win.loadURL(BASE + "/index.html");
      await wait(3200);
      log("=".repeat(78));
      log(`视口 ${vw}x${vh}`);
      // 确保字幕宿主存在
      const has = await js("!!document.getElementById('pet-subtitle')");
      log("  #pet-subtitle 存在: " + has);
      if (!has) { win.destroy(); continue; }

      for (const [name, en, zh, dur] of CASES) {
        // 先派发事件，等布局稳定（CSS 过渡 260ms + 第二次 syncGeometry）后再量测
        await js(`(${MEASURE})(${JSON.stringify(en)}, ${JSON.stringify(zh)}, ${dur})`);
        await wait(550);
        const raw = await js(`(${READOUT})()`);
        const m = JSON.parse(raw);
        if (!m.ok) { log("  " + name + " -> " + m.reason); continue; }
        const problems = [];
        if (m.spill.left > 0.5) problems.push(`左溢出${m.spill.left}`);
        if (m.spill.right > 0.5) problems.push(`右溢出${m.spill.right}`);
        if (m.spill.top > 0.5) problems.push(`上溢出${m.spill.top}`);
        if (m.spill.bottom > 0.5) problems.push(`下溢出${m.spill.bottom}`);
        if (Math.abs(m.centreOffset) > 2) problems.push(`未居中(偏移${m.centreOffset})`);
        if (m.overlapHud === true) problems.push("遮挡HUD");
        if (m.zh && m.zh.sw > m.zh.cw + 1) problems.push(`中文横向溢出${m.zh.sw}>${m.zh.cw}`);
        if (m.en && m.en.sw > m.en.cw + 1) problems.push(`英文横向溢出${m.en.sw}>${m.en.cw}`);
        if (m.zh && m.zh.sh > m.zh.ch + 1) problems.push(`中文纵向裁切${m.zh.sh}>${m.zh.ch}`);
        if (m.en && m.en.sh > m.en.ch + 1) problems.push(`英文纵向裁切${m.en.sh}>${m.en.ch}`);
        if (m.htmlInjected) problems.push("HTML被注入成元素");
        log(`  ${name.padEnd(10)} 框 ${m.box.w}x${m.box.h}  高 ${m.box.h}  ` +
            (problems.length ? "!! " + problems.join(" / ") : "OK"));
        if (problems.length) {
          log(`      详情: spill=${JSON.stringify(m.spill)} centre=${m.centreOffset} ` +
              `hud=${JSON.stringify(m.hud)} en=${JSON.stringify(m.en)}`);
        }
      }
    } catch (e) {
      log("  失败: " + ((e && e.message) || e));
    }
    win.destroy();
  }
  app.exit(0);
});
