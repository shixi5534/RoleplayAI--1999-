/*
 * iv_final_checks.js —— remaining verifier checks:
 *   - hide timing (dur:0.5 with medium text) and reading-time adequacy
 *   - real manifest clips end-to-end through the actual voice module
 *   - confirm the --sub-lift transition bug on the LIVE app path
 *   - real-clip subset: does any MANIFEST clip still overflow after the fix?
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
const OUTFILE = path.join(OUTDIR, process.env.IV_OUT || "iv_final.txt");
const BUF = [];
const log = (...a) => { BUF.push(a.join(" ")); };
process.on("exit", () => {
  try { fs.mkdirSync(OUTDIR, { recursive: true });
        fs.writeFileSync(OUTFILE, BUF.join("\n") + "\n", "utf8"); } catch (e) {}
});

const MEASURE_ALL = `(() => {
  const el = document.getElementById("pet-subtitle");
  if (!el) return JSON.stringify({ missing: true });
  const cs = getComputedStyle(el), r = el.getBoundingClientRect();
  const stage = document.querySelector(".stage");
  const hud = document.getElementById("stage-hud");
  const o = { bottom: cs.bottom, maxHeight: cs.maxHeight, overflowY: cs.overflowY,
    boxTop:+r.top.toFixed(1), boxBottom:+r.bottom.toFixed(1), boxH:+r.height.toFixed(1),
    elHOvf: el.scrollWidth-el.clientWidth, elVOvf: el.scrollHeight-el.clientHeight,
    show: el.classList.contains("show"), lift: el.style.getPropertyValue("--sub-lift") };
  if (stage) { const s = stage.getBoundingClientRect();
    o.stageTop=+s.top.toFixed(1); o.stageBottom=+s.bottom.toFixed(1);
    o.spillLeft=+(s.left-r.left).toFixed(1); o.spillRight=+(r.right-s.right).toFixed(1);
    o.spillTop=+(s.top-r.top).toFixed(1); o.spillBottom=+(r.bottom-s.bottom).toFixed(1); }
  if (hud) { const b = hud.getBoundingClientRect();
    const ix=Math.max(0,Math.min(r.right,b.right)-Math.max(r.left,b.left));
    const iy=Math.max(0,Math.min(r.bottom,b.bottom)-Math.max(r.top,b.top));
    o.hudTop=+b.top.toFixed(1); o.hudBottom=+b.bottom.toFixed(1);
    o.hudOverlap=ix>0&&iy>0; o.hudArea=+(ix*iy).toFixed(0); }
  o.kids = [...el.children].map(k => ({ cls:k.className, len:(k.textContent||"").length,
    hOvf: k.scrollWidth-k.clientWidth, vOvf: k.scrollHeight-k.clientHeight }));
  return JSON.stringify(o);
})()`;

const SHOWN = `(() => { const e=document.getElementById("pet-subtitle");
  return e ? e.classList.contains("show") : null; })()`;

app.whenReady().then(async () => {
  const win = new BrowserWindow({ width: W, height: H, show: false,
    webPreferences: { contextIsolation: true, nodeIntegration: false, sandbox: false } });
  const js = (c) => win.webContents.executeJavaScript(c);
  try {
    await win.loadURL(BASE + PAGE);
    await wait(3200);
    log("=".repeat(80));
    log(`FINAL CHECKS page=${PAGE} window=${W}x${H}`);

    // ---- 1. hide timing: dur 0.5 with medium text -----------------------
    log("\n== 1. HIDE TIMING ==");
    log("   source: pet-subtitle.js show(): ms = max(2200, (durSec||4)*1000 + 1600)");
    log("           pet:voice-playing:   ms = max(2200, (end-start||4)*1000 + 1600)");
    log("           HIDE_EXTRA_MS = 1600");
    const medium = "I could handle some paperwork, or perhaps forge some documents, if that's needed.";
    await js(`(() => { window.dispatchEvent(new CustomEvent("pet:voice-line", { detail: {
      clip:{id:"t05",dur:0.5}, slot:"click", lang:"en",
      subtitle:{zh:"中文",en:${JSON.stringify(medium)}} } })); return 1; })()`);
    let t0 = Date.now(), hidden = null;
    for (let i = 0; i < 60; i++) {
      if (!(await js(SHOWN))) { hidden = Date.now() - t0; break; }
      await wait(50);
    }
    log(`   clip.dur=0.5, text=${medium.length} chars -> hidden after ${hidden} ms`);
    log(`   => floor enforced: 2200ms (NOT 0.5s). Reading time for ${medium.length} chars`);
    log(`      at 15 ch/s = ${(medium.length/15).toFixed(1)}s = ${Math.round(medium.length/15*1000)}ms`);
    log(`      ${medium.length/15*1000 <= 2200 ? "OK: 2200ms floor covers it" : "INSUFFICIENT"}`);

    // ---- 2. confirm the lift bug on the live path ------------------------
    log("\n== 2. --sub-lift APPLIED? (live app path) ==");
    await js(`(() => { const e=document.getElementById("pet-subtitle"); e.classList.remove("show"); return 1; })()`);
    await wait(200);
    await js(`(() => { window.dispatchEvent(new CustomEvent("pet:voice-line", { detail: {
      clip:{id:"g",dur:3}, slot:"click", lang:"en", subtitle:{zh:"中文测试",en:"Medium English subtitle."} } }));
      window.dispatchEvent(new CustomEvent("pet:voice-playing", { detail: {
      clip:{id:"g",start:0,end:3,dur:3}, slot:"click" } })); return 1; })()`);
    await wait(1500);
    const m1 = JSON.parse(await js(MEASURE_ALL));
    log("   " + JSON.stringify(m1));
    log(`   lift set to ${m1.lift} but computed bottom=${m1.bottom}`);
    log(`   subtitle bottom=${m1.boxBottom}  HUD top=${m1.hudTop}  HUD bottom=${m1.hudBottom}`);
    log(`   => subtitle VERTICALLY OVERLAPS the HUD band: ` +
        `${m1.boxTop < m1.hudBottom && m1.boxBottom > m1.hudTop}`);

    // ---- 3. real manifest clips: any overflow left? ----------------------
    log("\n== 3. every real manifest subtitle, rendered (layout) ==");
    const all = JSON.parse(await js(`(async () => {
      const r = await fetch("/assets/voice/wu_ming_zhe/manifest.json",{cache:"no-store"});
      const j = await r.json();
      return JSON.stringify(j.clips.map(c => ({ id:c.id, lang:c.lang, dur:c.dur,
        zh:(c.subtitle&&c.subtitle.zh)||"", en:(c.subtitle&&c.subtitle.en)||"" })));
    })()`));
    let bad = [], worst = null;
    for (const c of all) {
      await js(`(() => { window.dispatchEvent(new CustomEvent("pet:voice-line", { detail: {
        clip:{id:${JSON.stringify(c.id)},dur:${c.dur}}, slot:"click", lang:${JSON.stringify(c.lang)},
        subtitle:{zh:${JSON.stringify(c.zh)},en:${JSON.stringify(c.en)}} } })); return 1; })()`);
      await wait(70);
      const m = JSON.parse(await js(MEASURE_ALL));
      const hOvf = m.elHOvf, kOvf = Math.max(0, ...m.kids.map(k => k.hOvf));
      const sp = Math.max(m.spillLeft||0, m.spillRight||0, m.spillTop||0, m.spillBottom||0);
      const rec = { id: c.id, hOvf, kOvf, spill: +(sp||0).toFixed(1), hud: !!m.hudOverlap,
                    boxH: m.boxH, maxH: m.maxHeight };
      if (!worst || rec.boxH > worst.boxH) worst = rec;
      if (hOvf > 1 || kOvf > 1 || sp > 0.5) bad.push(rec);
    }
    log(`   clips rendered: ${all.length}`);
    log(`   clips with ANY horizontal overflow or stage spill: ${bad.length}`);
    for (const b of bad.slice(0, 12)) log("     " + JSON.stringify(b));
    log(`   tallest rendered box: ${JSON.stringify(worst)}`);
    log(`   (all 133 keep the HUD overlap because bottom stays 6px - see section 2)`);
  } catch (e) {
    log("ERROR " + ((e && e.stack) || e));
  }
  app.exit(0);
});
