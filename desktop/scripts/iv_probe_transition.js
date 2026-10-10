/*
 * iv_probe_transition.js —— is the `bottom` transition really the blocker, and
 * does a top-level var change animate right when only the VAR changes (not the
 * element's own bottom declaration)?
 *
 * The previous probe proved: with the transition live, computed bottom NEVER
 * leaves 6px; with transition:none it is 117px immediately. Confirm the ordering
 * hypothesis: var() substitution in the .show rule happens while .show is being
 * added, so the transition starts from the un-shown value and the end value is
 * then re-resolved -> sticking.
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
const OUTFILE = path.join(OUTDIR, process.env.IV_OUT || "iv_transition.txt");
const BUF = [];
const log = (...a) => { BUF.push(a.join(" ")); };
process.on("exit", () => {
  try { fs.mkdirSync(OUTDIR, { recursive: true });
        fs.writeFileSync(OUTFILE, BUF.join("\n") + "\n", "utf8"); } catch (e) {}
});

const SNAP = (tag) => `(() => {
  const el = document.getElementById("pet-subtitle");
  const cs = getComputedStyle(el);
  const r = el.getBoundingClientRect();
  const stage = document.querySelector(".stage").getBoundingClientRect();
  return JSON.stringify({ tag: ${JSON.stringify(tag)}, bottom: cs.bottom,
    boxTop:+r.top.toFixed(1), boxBottom:+r.bottom.toFixed(1), boxH:+r.height.toFixed(1),
    stageTop:+stage.top.toFixed(1), stageBottom:+stage.bottom.toFixed(1),
    show: el.classList.contains("show"), maxHeight: cs.maxHeight,
    overflowY: cs.overflowY, scrollH: el.scrollHeight, clientH: el.clientHeight });
})()`;

const DRIVE = `(() => {
  window.dispatchEvent(new CustomEvent("pet:voice-line", { detail: {
    clip: { id:"g", dur:3 }, slot:"click", lang:"en",
    subtitle: { zh:"中文测试", en:"Medium English subtitle." } } }));
  window.dispatchEvent(new CustomEvent("pet:voice-playing", { detail: {
    clip: { id:"g", start:0, end:3, dur:3 }, slot:"click" } }));
  return 1; })()`;

app.whenReady().then(async () => {
  const win = new BrowserWindow({ width: W, height: H, show: false,
    webPreferences: { contextIsolation: true, nodeIntegration: false, sandbox: false } });
  const js = (c) => win.webContents.executeJavaScript(c);
  try {
    await win.loadURL(BASE + PAGE);
    await wait(3200);
    log("=".repeat(78));
    log(`TRANSITION PROBE page=${PAGE}`);

    // (1) baseline: the app's own path
    await js(DRIVE);
    await wait(1200);
    log("(1) app path (voice-line/playing): " + await js(SNAP("app-path")));

    // (2) same but the CSS transition disabled BEFORE showing -> should lift
    await js(`(() => { const e=document.getElementById("pet-subtitle");
      e.classList.remove("show"); e.style.transition="none"; return 1; })()`);
    await wait(200);
    await js(DRIVE);
    await wait(600);
    log("(2) transition disabled before show: " + await js(SNAP("no-transition")));

    // (3) restore the transition and re-toggle -> does it stick again?
    await js(`(() => { const e=document.getElementById("pet-subtitle");
      e.classList.remove("show"); e.style.transition=""; return 1; })()`);
    await wait(200);
    await js(DRIVE);
    await wait(1200);
    log("(3) transition restored, re-shown: " + await js(SNAP("restored")));

    // (4) does the OVERFLOW/MaxHeight work now that we know it is at bottom:6px?
    log("\n(4) long text while the lift is broken (measures real user-visible placement)");
    for (const [nm, en] of [["250ch", "x".repeat(250)], ["1000ch", "y".repeat(1000)]]) {
      await js(`(() => { const e=document.getElementById("pet-subtitle"); e.classList.remove("show"); return 1; })()`);
      await wait(150);
      await js(`(() => { window.dispatchEvent(new CustomEvent("pet:voice-line", { detail: {
        clip:{id:"g2",dur:3}, slot:"click", lang:"en",
        subtitle:{zh:"中文测试", en:${JSON.stringify(en)}} } }));
        window.dispatchEvent(new CustomEvent("pet:voice-playing", { detail: {
        clip:{id:"g2",start:0,end:3,dur:3}, slot:"click" } })); return 1; })()`);
      await wait(700);
      log("   " + nm + ": " + await js(SNAP(nm)));
    }

    // (5) HUD overlap with the real (broken) placement
    log("\n(5) HUD overlap under real placement");
    log(await js(`(() => {
      const el=document.getElementById("pet-subtitle"), hud=document.getElementById("stage-hud");
      const a=el.getBoundingClientRect(), b=hud.getBoundingClientRect();
      const ix = Math.max(0, Math.min(a.right,b.right)-Math.max(a.left,b.left));
      const iy = Math.max(0, Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top));
      return JSON.stringify({ subtitle:{t:+a.top.toFixed(1),b:+a.bottom.toFixed(1)},
        hud:{t:+b.top.toFixed(1),b:+b.bottom.toFixed(1)},
        overlapX:+ix.toFixed(1), overlapY:+iy.toFixed(1), area:+(ix*iy).toFixed(0),
        intersects: ix>0 && iy>0, hudZ:getComputedStyle(hud).zIndex,
        subZ:getComputedStyle(el).zIndex });
    })()`));
  } catch (e) {
    log("ERROR " + ((e && e.stack) || e));
  }
  app.exit(0);
});
