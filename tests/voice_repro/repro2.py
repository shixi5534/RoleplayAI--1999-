# -*- coding: utf-8 -*-
"""复现第二轮：定位宠物页点击链路 + 补齐关键测量"""
from __future__ import annotations

import json
from pathlib import Path

from playwright.sync_api import sync_playwright

CHROME = r"C:/Users/Lenovo/AppData/Local/ms-playwright/chromium-1217/chrome-win64/chrome.exe"
BASE = "http://127.0.0.1:18080"
OUT = Path("/tmp/rp_voice_repro")

INSTRUMENT = """() => {
  window.__t0 = performance.now();
  window.__log = [];
  const ts = () => Math.round(performance.now() - window.__t0);
  window.__ts = ts;
  if (!window.__origPlay) {
    window.__origPlay = Audio.prototype.play;
    Audio.prototype.play = function () {
      const src = String(this.src || '').split('/').pop();
      window.__log.push({ts: ts(), type: 'play()', src: src});
      const p = window.__origPlay.call(this);
      if (p && p.then) p.catch((e) => window.__log.push(
        {ts: ts(), type: 'play:rejected', src: src,
         err: String((e && e.name) || e)}));
      return p;
    };
  }
  ['pet:voice-line','pet:voice-playing','pet:voice-ended','pet:voice-stopped']
    .forEach((n) => window.addEventListener(n, (e) => {
      const d = e.detail || {};
      window.__log.push({ts: ts(), type: n.replace('pet:voice-',''),
        id: d.clip && d.clip.id, slot: d.slot, reason: d.reason});
    }));
  ['click','motion','emotion','drag','menu'].forEach((n) =>
    window.addEventListener('pet:intent:' + n, (e) => window.__log.push(
      {ts: ts(), type: 'intent:' + n, slot: e.detail && (e.detail.pose || e.detail.emotion)})));
  window.addEventListener('live2d:interact', (e) => window.__log.push(
    {ts: ts(), type: 'live2d:interact', region: e.detail && e.detail.region}));
}"""


def since(page, t):
    return page.evaluate(
        "(t) => window.__log.filter(r => r.ts >= t).map("
        "r => r.type + (r.src ? ':' + r.src : '') + (r.id ? '#' + r.id : '')"
        " + (r.slot ? '@' + r.slot : ''))", t)


# ── P1：宠物页点击为什么完全没反应 ──
def probe_pet(browser):
    page = browser.new_page(viewport={"width": 1280, "height": 800})
    page.on("pageerror", lambda e: print("   pageerror:", str(e)[:160]))
    page.goto(f"{BASE}/pet.html")
    page.wait_for_selector("#pet-canvas canvas", timeout=20000)
    page.wait_for_function(
        "window.RoleplayPetVoice && window.RoleplayPetVoice.ready()", timeout=20000)
    page.evaluate(INSTRUMENT)
    box = page.locator("#pet-canvas").bounding_box()
    print(f"  #pet-canvas box = {box}")
    cx, cy = box["x"] + box["width"] / 2, box["y"] + box["height"] * 0.75
    hit = page.evaluate(
        "([x,y]) => { const e = document.elementFromPoint(x,y);"
        " return e ? e.tagName + '#' + e.id + '.' + e.className : 'null'; }",
        [cx, cy])
    info = page.evaluate("""() => {
      const c = document.getElementById('pet-canvas');
      return {rect: c.getBoundingClientRect().toJSON(),
              kids: [...c.children].map(k => k.tagName + '#' + k.id),
              hasPetObj: typeof window.RoleplaySpine,
              onboarding: (() => { const o = document.getElementById('pet-onboarding');
                return o ? o.classList.contains('open') || o.classList.contains('show') : null; })(),
              bodyClass: document.body.className};
    }""")
    print(f"  elementFromPoint({cx:.0f},{cy:.0f}) = {hit}")
    print(f"  #pet-canvas = {info}")
    # 试着直接点击 canvas 子元素
    page.mouse.click(cx, cy)
    page.wait_for_timeout(600)
    print(f"  直接 canvas 点击 → {since(page, 0)}")
    # 用 dispatch 走 pet.js 的 pointer 序列验证链路本身
    page.evaluate("""() => {
      const c = document.querySelector('#pet-canvas canvas');
      const r = c.getBoundingClientRect();
      const opt = (x, y) => ({bubbles:true, cancelable:true, composed:true,
        pointerId:1, pointerType:'mouse', isPrimary:true, button:0, buttons:1,
        clientX:x, clientY:y, screenX:x, screenY:y, view:window});
      const x = r.left + r.width/2, y = r.top + r.height*0.7;
      c.dispatchEvent(new PointerEvent('pointerdown', opt(x,y)));
      document.dispatchEvent(new PointerEvent('pointerup', opt(x,y)));
    }""")
    page.wait_for_timeout(600)
    print(f"  手工 PointerEvent（canvas 上）→ {since(page, 0)}")
    page.close()


# ── P2：聊天页连续点击 60s，测出真实「可再次发声」间隔 ──
def probe_index_long(browser, interval_ms=3000, total_ms=60000):
    page = browser.new_page(viewport={"width": 1280, "height": 800})
    page.goto(f"{BASE}/index.html")
    page.wait_for_timeout(6000)
    page.wait_for_function(
        "!!(window.RoleplayLive2D && window.RoleplayLive2D._ready)", timeout=20000)
    page.evaluate(INSTRUMENT)
    box = page.locator("#live2d-canvas").bounding_box()
    cx, cy = box["x"] + box["width"] / 2, box["y"] + box["height"] * 0.35
    rows = []
    n = int(total_ms / interval_ms)
    for i in range(n):
        t0 = page.evaluate("window.__ts()")
        page.mouse.click(cx, cy)
        page.wait_for_timeout(500)
        hit = since(page, t0)
        voiced = [h for h in hit if h.startswith("play()") or h.startswith("line")]
        rows.append((i + 1, round(t0 / 1000, 2), voiced, hit))
        page.wait_for_timeout(interval_ms - 500)
    print("\n  === 聊天页每 3s 真实点击，共 %d 次 ===" % n)
    for i, t, v, hit in rows:
        tag = "✅ 发声 " + str(v) if v else "❌ 无声（intent 已送达，语音被拦截）"
        print(f"   第{i:2d}次 t={t:6.2f}s  {tag}")
    (OUT / "e2_long.json").write_text(
        json.dumps(page.evaluate("window.__log"), ensure_ascii=False, indent=1),
        encoding="utf-8")
    page.close()
    return rows


# ── P3：长音频期间点击被全局互斥吞掉（click 需 currentTime>2 才能打断）──
def probe_mutex(browser):
    page = browser.new_page()
    page.goto(f"{BASE}/pet.html")
    page.wait_for_function(
        "window.RoleplayPetVoice && window.RoleplayPetVoice.ready()", timeout=20000)
    r = page.evaluate("""async () => {
      const v = window.RoleplayPetVoice;
      const m = await fetch('./assets/voice/wu_ming_zhe/manifest.json').then(r=>r.json());
      const ids = m.slots.happy || [];
      const pool = m.clips.filter(c => ids.indexOf(c.id) >= 0 && c.lang === 'zh');
      const longest = pool.reduce((a,b) => a.dur >= b.dur ? a : b);
      const wait = (ms) => new Promise(r => setTimeout(r, ms));
      const out = {clip: longest.id, dur: longest.dur, probes: []};
      v.playClip(longest.id, 'happy');
      for (const at of [500, 1500, 2500, 4000, 8000]) {
        await wait(at === 500 ? 500 : 0);
        if (at !== 500) await wait(0);
        const c = v.playForSlot('click');   // click 槽：currentTime>2 才允许打断
        out.probes.push({after_ms: at, result: c && c.id,
                         curTime: null});
        await wait(at === 500 ? 1000 : 1500);
      }
      return out;
    }""")
    print(f"\n  === P3 长音频（happy {r['clip']} dur={r['dur']}s）期间点 click ===")
    for p in r["probes"]:
        print(f"   +{p['after_ms']}ms → {p['result'] or '❌ 被全局互斥拦截'}")
    page.close()


# ── P4：宠物页（无 live2d）纯语音层叠加限制 ──
def probe_pet_voice_layer(browser, interval_ms=3000, total_ms=60000):
    page = browser.new_page()
    page.goto(f"{BASE}/pet.html")
    page.wait_for_function(
        "window.RoleplayPetVoice && window.RoleplayPetVoice.ready()", timeout=20000)
    page.evaluate(INSTRUMENT)
    n = int(total_ms / interval_ms)
    rows = []
    for i in range(n):
        t0 = page.evaluate("window.__ts()")
        page.evaluate(
            "window.RoleplayPetCore.emitIntent('click', {})")  # 等价于真实点击的语音触发
        page.wait_for_timeout(400)
        hit = since(page, t0)
        voiced = [h for h in hit if h.startswith("play()") or h.startswith("line")]
        rows.append((i + 1, round(t0 / 1000, 2), voiced))
        page.wait_for_timeout(interval_ms - 400)
    print("\n  === 宠物页：每 3s 一次 emitIntent('click')（语音层纯链路）===")
    for i, t, v in rows:
        print(f"   第{i:2d}次 t={t:6.2f}s  "
              f"{'✅ 发声 ' + str(v) if v else '❌ 无声'}")
    (OUT / "e4_pet_layer.json").write_text(
        json.dumps(page.evaluate("window.__log"), ensure_ascii=False, indent=1),
        encoding="utf-8")
    page.close()
    return rows


def main():
    with sync_playwright() as p:
        b = p.chromium.launch(
            executable_path=CHROME, headless=True,
            args=["--autoplay-policy=no-user-gesture-required",
                  "--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        print("=" * 72); print("P1 宠物页点击链路探测"); print("=" * 72)
        probe_pet(b)
        print("\n" + "=" * 72); print("P2 聊天页 60s 连续点击"); print("=" * 72)
        probe_index_long(b)
        print("\n" + "=" * 72); print("P3 长音频期间的全局互斥"); print("=" * 72)
        probe_mutex(b)
        print("\n" + "=" * 72); print("P4 宠物页语音层 60s"); print("=" * 72)
        probe_pet_voice_layer(b)
        b.close()


if __name__ == "__main__":
    main()
