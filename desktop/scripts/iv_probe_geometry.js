/*
 * iv_probe_geometry.js —— why is the subtitle using bottom:6px though the CSS
 * says bottom:var(--sub-lift) for .stage #pet-subtitle.show, and why is .stage
 * only ~517px wide in a 1440px window?
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
const OUTFILE = path.join(OUTDIR, process.env.IV_OUT || "iv_geometry.txt");
const BUF = [];
const log = (...a) => { BUF.push(a.join(" ")); };
process.on("exit", () => {
  try { fs.mkdirSync(OUTDIR, { recursive: true });
        fs.writeFileSync(OUTFILE, BUF.join("\n") + "\n", "utf8"); } catch (e) {}
});

const PROBE = `(() => {
  const o = {};
  const el = document.getElementById("pet-subtitle");
  const stage = document.querySelector(".stage");
  const hud = document.getElementById("stage-hud") || document.querySelector(".stage-hud");
  o.vw = innerWidth; o.vh = innerHeight;
  o.docCW = document.documentElement.clientWidth;
  o.docCH = document.documentElement.clientHeight;
  o.readyState = document.readyState;
  if (stage) {
    const s = stage.getBoundingClientRect(), cs = getComputedStyle(stage);
    o.stage = { l:s.left, t:s.top, r:s.right, b:s.bottom, w:s.width, h:s.height,
                pos:cs.position, display:cs.display, width:cs.width, height:cs.height,
                maxWidth:cs.maxWidth, flex:cs.flex, cls:stage.className };
  }
  if (hud) {
    const h = hud.getBoundingClientRect(), hcs = getComputedStyle(hud);
    o.hud = { l:h.left, t:h.top, r:h.right, b:h.bottom, w:h.width, h:h.height,
              pos:hcs.position, display:hcs.display, z:hcs.zIndex, cls:hud.className, id:hud.id };
  }
  if (el) {
    const r = el.getBoundingClientRect(), cs = getComputedStyle(el);
    o.el = { l:r.left, t:r.top, r:r.right, b:r.bottom, w:r.width, h:r.height,
             bottom:cs.bottom, maxHeight:cs.maxHeight, overflow:cs.overflow,
             inlineLift: el.style.getPropertyValue("--sub-lift"),
             inlineMaxh: el.style.getPropertyValue("--sub-maxh"),
             computedLift: cs.getPropertyValue("--sub-lift"),
             computedMaxh: cs.getPropertyValue("--sub-maxh"),
             show: el.classList.contains("show"), parent: el.parentElement.className };
  } else { o.el = null; }
  // which CSS rules match?
  const matched = [];
  try {
    for (const ss of document.styleSheets) {
      let rules; try { rules = ss.cssRules; } catch(e) { continue; }
      if (!rules) continue;
      for (const r of rules) {
        if (r.selectorText && /#pet-subtitle/.test(r.selectorText)) {
          matched.push({ href: (ss.href||"inline").split("/").pop(), sel: r.selectorText,
                         bottom: r.style.bottom || "", maxHeight: r.style.maxHeight || "",
                         matches: (() => { try { return el ? el.matches(r.selectorText) : null; } catch(e){ return "ERR"; } })() });
        }
      }
    }
  } catch (e) { o.cssErr = String(e); }
  o.matchedRules = matched;
  o.stageCount = document.querySelectorAll(".stage").length;
  o.subtitleCount = document.querySelectorAll("#pet-subtitle").length;
  return JSON.stringify(o);
})()`;

app.whenReady().then(async () => {
  const win = new BrowserWindow({ width: W, height: H, show: false,
    webPreferences: { contextIsolation: true, nodeIntegration: false, sandbox: false } });
  const js = (c) => win.webContents.executeJavaScript(c);
  try {
    await win.loadURL(BASE + PAGE);
    await wait(3200);
    log("=".repeat(78));
    log(`GEOMETRY page=${PAGE} window=${W}x${H}`);
    log("--- BEFORE any subtitle ---");
    log(await js(PROBE));
    // drive it
    await js(`(() => {
      window.dispatchEvent(new CustomEvent("pet:voice-line", { detail: {
        clip: { id:"g", dur:3 }, slot:"click", lang:"en",
        subtitle: { zh:"中文测试", en:"Medium length English subtitle for geometry probing." } } }));
      window.dispatchEvent(new CustomEvent("pet:voice-playing", { detail: {
        clip: { id:"g", start:0, end:3, dur:3 }, slot:"click" } }));
      return 1; })()`);
    await wait(600);
    log("--- AFTER show (600ms settle) ---");
    log(await js(PROBE));
    await wait(1500);
    log("--- AFTER 2100ms settle ---");
    log(await js(PROBE));
  } catch (e) {
    log("ERROR " + ((e && e.stack) || e));
  }
  app.exit(0);
});
