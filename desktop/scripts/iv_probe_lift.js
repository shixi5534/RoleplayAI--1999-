/*
 * iv_probe_lift.js —— pin down WHY computed bottom is 6px while
 * --sub-lift=117px and the .stage #pet-subtitle.show rule matches.
 *
 * Hypotheses:
 *  H1 transition on `bottom` never lands (stuck mid-animation / never triggered)
 *  H2 the var resolves but the declaration is dropped (invalid at computed-value time)
 *  H3 the rule applies but something else overrides it
 */
"use strict";
const { app, BrowserWindow } = require("electron");
const path = require("path");
const fs = require("fs");

const BASE = process.env.APP_URL || "http://127.0.0.1:8000";
const PAGE = process.env.PAGE || "/index.html";
const W = parseInt(process.env.WIN_W || "1440", 10);
const H = parseInt(process.env.WIN_H || "950", 10);
const wait = (ms) => new Promise((r) => setTimeout(r, ms));
app.disableHardwareAcceleration();
app.setPath("userData", path.join(__dirname, "out", ".electron-iv-" + process.pid));

const OUTDIR = path.join(__dirname, "out");
const OUTFILE = path.join(OUTDIR, process.env.IV_OUT || "iv_lift.txt");
const BUF = [];
const log = (...a) => { BUF.push(a.join(" ")); };
process.on("exit", () => {
  try { fs.mkdirSync(OUTDIR, { recursive: true });
        fs.writeFileSync(OUTFILE, BUF.join("\n") + "\n", "utf8"); } catch (e) {}
});

const DRIVE = `(() => {
  window.dispatchEvent(new CustomEvent("pet:voice-line", { detail: {
    clip: { id:"g", dur:3 }, slot:"click", lang:"en",
    subtitle: { zh:"中文测试", en:"Medium English subtitle." } } }));
  window.dispatchEvent(new CustomEvent("pet:voice-playing", { detail: {
    clip: { id:"g", start:0, end:3, dur:3 }, slot:"click" } }));
  return 1; })()`;

const SNAP = (tag) => `(() => {
  const el = document.getElementById("pet-subtitle");
  const cs = getComputedStyle(el);
  const r = el.getBoundingClientRect();
  const stage = document.querySelector(".stage").getBoundingClientRect();
  return JSON.stringify({ tag: ${JSON.stringify(tag)},
    inlineLift: el.style.getPropertyValue("--sub-lift"),
    computedLift: cs.getPropertyValue("--sub-lift").trim(),
    bottom: cs.bottom, bottomRaw: cs.getPropertyValue("bottom"),
    transition: cs.transitionProperty + " / " + cs.transitionDuration,
    boxBottom: +r.bottom.toFixed(1), boxTop: +r.top.toFixed(1), boxH: +r.height.toFixed(1),
    stageBottom: +stage.bottom.toFixed(1),
    gapToStageBottom: +(stage.bottom - r.bottom).toFixed(1),
    show: el.classList.contains("show"),
    maxHeight: cs.maxHeight, maxHeightRaw: cs.getPropertyValue("max-height") });
})()`;

app.whenReady().then(async () => {
  const win = new BrowserWindow({ width: W, height: H, show: false,
    webPreferences: { contextIsolation: true, nodeIntegration: false, sandbox: false } });
  const js = (c) => win.webContents.executeJavaScript(c);
  try {
    await win.loadURL(BASE + PAGE);
    await wait(3200);
    log("=".repeat(78));
    log(`LIFT PROBE page=${PAGE} window=${W}x${H}`);

    await js(DRIVE);
    for (const t of [50, 150, 300, 600, 1200, 2400, 4000]) {
      await wait(t === 50 ? 50 : 200);
      log(await js(SNAP(`t≈${t}ms`)));
    }

    log("\n--- H1: force a reflow / re-add .show ---");
    await js(`(() => { const e=document.getElementById("pet-subtitle");
      e.classList.remove("show"); void e.offsetHeight; e.classList.add("show"); return 1; })()`);
    await wait(700);
    log(await js(SNAP("after re-add .show")));

    log("\n--- H1b: kill the transition and re-measure ---");
    await js(`(() => { const e=document.getElementById("pet-subtitle");
      e.style.transition="none"; e.classList.remove("show"); void e.offsetHeight;
      e.classList.add("show"); return 1; })()`);
    await wait(400);
    log(await js(SNAP("transition:none")));

    log("\n--- H2: does the declaration survive if we set bottom directly? ---");
    await js(`(() => { const e=document.getElementById("pet-subtitle");
      e.style.bottom="117px"; return 1; })()`);
    await wait(300);
    log(await js(SNAP("inline bottom:117px")));

    log("\n--- H3: what is --sub-lift on the PARENT vs the element? ---");
    log(await js(`(() => {
      const e = document.getElementById("pet-subtitle");
      const st = document.querySelector(".stage");
      const r = {};
      r.elInline = e.style.getPropertyValue("--sub-lift");
      r.elComputed = getComputedStyle(e).getPropertyValue("--sub-lift").trim();
      r.stageInline = st.style.getPropertyValue("--sub-lift");
      r.stageComputed = getComputedStyle(st).getPropertyValue("--sub-lift").trim();
      r.rootComputed = getComputedStyle(document.documentElement).getPropertyValue("--sub-lift").trim();
      // resolve a fresh test element to see if the var substitution works at all
      const t = document.createElement("div");
      t.style.cssText = "position:absolute;bottom:var(--sub-lift,134px)";
      st.appendChild(t);
      r.testBottom = getComputedStyle(t).bottom;
      t.remove();
      return JSON.stringify(r);
    })()`));
  } catch (e) {
    log("ERROR " + ((e && e.stack) || e));
  }
  app.exit(0);
});
