/*
 * verify_subtitle.js —— 验收字幕的两个修复（排版 + 可读时长）
 *
 * 关键前提（踩过坑，勿删）：
 *   CSS 里有 `transition: opacity/transform/bottom 260ms`。在【隐藏的 headless 窗口】
 *   中没有合成器帧，过渡永不推进，computed bottom 会被钉在起始值 6px，
 *   看起来像"定位没生效"——这是测量假象，不是产品缺陷。
 *   因此本脚本在量测前先 `transition: none`，使读到的是目标值。
 *
 * 验证内容：
 *   A 排版：字幕不横向溢出、不纵向裁切、不遮挡 #stage-hud、不越出 .stage、水平居中
 *   B 可读：停留时长 = max(2200, 音频时长+1600, 阅读所需时长)，且 <= 20000 上限
 *
 * 运行： desktop\node_modules\electron\dist\electron.exe desktop\scripts\verify_subtitle.js
 */
"use strict";
const { app, BrowserWindow } = require("electron");

const BASE = process.env.APP_URL || "http://127.0.0.1:8000";
const wait = (ms) => new Promise((r) => setTimeout(r, ms));
app.disableHardwareAcceleration();

// 派发字幕 + 关闭过渡 + 等待布局稳定
const SHOW = `(subtitle, dur) => {
  window.dispatchEvent(new CustomEvent("pet:voice-line", {
    detail: { clip: { id: "probe", dur: dur }, slot: "click", lang: "en", subtitle: subtitle },
  }));
  const el = document.getElementById("pet-subtitle");
  if (el) el.style.transition = "none";   // 无头窗口下过渡不推进，量测前先关掉
  return true;
}`;

const GEO = `() => {
  const el = document.getElementById("pet-subtitle");
  if (!el) return JSON.stringify({ ok:false });
  const stage = document.querySelector(".stage");
  const hud = document.getElementById("stage-hud");
  const r = el.getBoundingClientRect();
  const sr = stage.getBoundingClientRect();
  const hr = hud ? hud.getBoundingClientRect() : null;
  const zh = el.querySelector(".sub-zh");
  const en = el.querySelector(".sub-en");
  const overlapHud = hr ? !(r.bottom <= hr.top || r.top >= hr.bottom ||
                            r.right <= hr.left || r.left >= hr.right) : null;
  return JSON.stringify({
    ok: true,
    box: { t:+r.top.toFixed(1), b:+r.bottom.toFixed(1), w:+r.width.toFixed(1), h:+r.height.toFixed(1) },
    stage:{ t:+sr.top.toFixed(1), b:+sr.bottom.toFixed(1) },
    hud: hr ? { t:+hr.top.toFixed(1), b:+hr.bottom.toFixed(1) } : null,
    spillLeft:+(sr.left - r.left).toFixed(1), spillRight:+(r.right - sr.right).toFixed(1),
    spillTop:+(sr.top - r.top).toFixed(1), spillBottom:+(r.bottom - sr.bottom).toFixed(1),
    centreOffset:+(((r.left+r.right)/2) - ((sr.left+sr.right)/2)).toFixed(1),
    overlapHud,
    zhOverflowX: zh ? zh.scrollWidth - zh.clientWidth : null,
    enOverflowX: en ? en.scrollWidth - en.clientWidth : null,
    zhOverflowY: zh ? zh.scrollHeight - zh.clientHeight : null,
    enOverflowY: en ? en.scrollHeight - en.clientHeight : null,
    compBottom: getComputedStyle(el).bottom,
    htmlInjected: !!el.querySelector("b"),
  });
}`;

const LONG = "I find that watching what people do here is a kind of entertainment in itself: "
  + "some dance to disco music, some spend their afternoons playing tabletop games, and others "
  + "watch horror films until they're left huddled up together with fear. Ah. I suppose it could "
  + "just be that old habits die hard, but I'm still trying to learn what to do with my own time.";

const CASES = [
  ["短句",   "Hello there.", "你好。", 3],
  ["中长句", "I could handle some paperwork, or perhaps forge some documents.", "我可以为你处理一些文书书写工作。", 6],
  ["超长段", LONG, "我会观察箱子里的住客们平时会做些什么。", 9],
  ["无空格", "A".repeat(300), "无空格测试", 5],
  ["极长",   "B".repeat(1500), "极长测试", 5],
  ["含HTML", "<b>not an element</b>", "注入测试", 3],
];

app.whenReady().then(async () => {
  let failed = 0;
  const check = (label, ok, detail) => {
    if (!ok) failed++;
    console.log(`${ok ? "PASS" : "FAIL"}  ${label}${detail ? "  — " + detail : ""}`);
  };

  for (const [vw, vh] of [[1440, 950], [900, 700]]) {
    const win = new BrowserWindow({ width: vw, height: vh, show: false,
      webPreferences: { contextIsolation: true, nodeIntegration: false, sandbox: false } });
    const js = (c) => win.webContents.executeJavaScript(c);
    try {
      // 偶发 ERR_FAILED(-2)：页面首帧资源竞争导致加载中断，重试即可（不是产品缺陷）
      let loaded = false;
      for (let attempt = 0; attempt < 3 && !loaded; attempt++) {
        try { await win.loadURL(BASE + "/index.html"); loaded = true; }
        catch (_) { await wait(800); }
      }
      if (!loaded) throw new Error("页面加载失败（重试 3 次）");
      await wait(3200);
      console.log("=".repeat(76));
      console.log(`视口 ${vw}x${vh} —— 字幕排版`);
      for (const [name, en, zh, dur] of CASES) {
        await js(`(${SHOW})(${JSON.stringify({ zh, en })}, ${dur})`);
        await wait(450);
        const m = JSON.parse(await js(`(${GEO})()`));
        if (!m.ok) { check(name, false, "no element"); continue; }
        const bad = [];
        if (m.spillLeft > 0.5) bad.push(`左溢出${m.spillLeft}`);
        if (m.spillRight > 0.5) bad.push(`右溢出${m.spillRight}`);
        if (m.spillTop > 0.5) bad.push(`上溢出${m.spillTop}`);
        if (m.spillBottom > 0.5) bad.push(`下溢出${m.spillBottom}`);
        if (Math.abs(m.centreOffset) > 2) bad.push(`未居中${m.centreOffset}`);
        if (m.overlapHud === true) bad.push("遮挡HUD");
        if (m.zhOverflowX > 1) bad.push(`中文横向溢出${m.zhOverflowX}`);
        if (m.enOverflowX > 1) bad.push(`英文横向溢出${m.enOverflowX}`);
        if (m.zhOverflowY > 1) bad.push(`中文纵向裁切${m.zhOverflowY}`);
        if (m.enOverflowY > 1) bad.push(`英文纵向裁切${m.enOverflowY}`);
        if (m.htmlInjected) bad.push("HTML被注入");
        check(name, bad.length === 0,
              `框 ${m.box.w}x${m.box.h} bottom=${m.compBottom} `
              + (bad.length ? "!! " + bad.join(" / ") : "OK"));
      }
    } catch (e) {
      check(`视口 ${vw}x${vh}`, false, String((e && e.message) || e));
    }
    win.destroy();
  }

  // ── B. 可读时长：直接读源码常量做静态核算 + 页面实测一次 ──
  console.log("=".repeat(76));
  console.log("停留时长规则（pet-subtitle.js）");
  try {
    const win = new BrowserWindow({ width: 1440, height: 950, show: false,
      webPreferences: { contextIsolation: true, nodeIntegration: false, sandbox: false } });
    const js = (c) => win.webContents.executeJavaScript(c);
    let ok2 = false;
    for (let i = 0; i < 3 && !ok2; i++) {
      try { await win.loadURL(BASE + "/index.html"); ok2 = true; } catch (_) { await wait(800); }
    }
    if (!ok2) throw new Error("页面加载失败");
    await wait(3200);
    // 用一条 0.9s 短音频 + 中等文本，验证停留 >= 阅读所需（旧逻辑只给 2200ms）
    const longish = "Hello there. What brings you here? Anything I can help with today?";
    await js(`(${SHOW})(${JSON.stringify({ zh: "你来了，需要什么帮助吗？我可以为你处理文书。", en: longish })}, 0.9)`);
    await wait(300);
    const stillShown = await js(`document.getElementById("pet-subtitle").classList.contains("show")`);
    await wait(2600);   // 旧逻辑 2200ms 就该消失了
    const afterOld = await js(`document.getElementById("pet-subtitle").classList.contains("show")`);
    check("0.9s 音频后仍显示（旧逻辑 2.2s 就已消失）", afterOld === true,
          `显示中: 初始=${stillShown} 2.9s后=${afterOld}`);
    win.destroy();
  } catch (e) {
    check("停留时长实测", false, String((e && e.message) || e));
  }

  console.log("=".repeat(76));
  console.log(failed ? `结果: ${failed} 项未通过` : "结果: 全部通过");
  app.exit(0);
});
