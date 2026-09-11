# -*- coding: utf-8 -*-
"""复现第三轮：宠物页真实点击（关闭新手引导）+ 404 冷却竞态 + 静默期是否有反馈"""
from __future__ import annotations

import json
from pathlib import Path

from playwright.sync_api import sync_playwright

CHROME = r"C:/Users/Lenovo/AppData/Local/ms-playwright/chromium-1217/chrome-win64/chrome.exe"
BASE = "http://127.0.0.1:18080"

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
      return window.__origPlay.call(this);
    };
  }
  ['pet:voice-line','pet:voice-playing','pet:voice-ended','pet:voice-stopped']
    .forEach((n) => window.addEventListener(n, (e) => {
      const d = e.detail || {};
      window.__log.push({ts: ts(), type: n.replace('pet:voice-',''),
        id: d.clip && d.clip.id, slot: d.slot, reason: d.reason});
    }));
  window.__subStates = [];
  const mo = new MutationObserver(() => {
    const el = document.getElementById('pet-subtitle');
    window.__subStates.push({ts: ts(),
      show: el ? el.classList.contains('show') : null});
  });
  mo.observe(document.documentElement, {subtree: true, attributes: true,
    attributeFilter: ['class']});
}"""


def pet_real_clicks(browser, interval_ms=3000, total_ms=66000):
    page = browser.new_page(viewport={"width": 1280, "height": 800})
    page.goto(f"{BASE}/pet.html")
    page.wait_for_selector("#pet-canvas canvas", timeout=20000)
    page.wait_for_function(
        "window.RoleplayPetVoice && window.RoleplayPetVoice.ready()", timeout=20000)
    # 关掉新手引导（真实用户首次点"开始"后即消失）
    page.evaluate("""() => {
      const o = document.getElementById('pet-onboarding');
      if (o) { o.classList.remove('open'); o.classList.add('hidden');
               o.style.display = 'none'; }
      try { localStorage.setItem('rp_pet_onboarded', '1'); } catch (_) {}
    }""")
    page.evaluate(INSTRUMENT)
    box = page.locator("#pet-canvas").bounding_box()
    cx, cy = box["x"] + box["width"] / 2, box["y"] + box["height"] * 0.78
    n = int(total_ms / interval_ms)
    rows = []
    for i in range(n):
        t0 = page.evaluate("window.__ts()")
        page.mouse.click(cx, cy)
        page.wait_for_timeout(450)
        hit = page.evaluate(
            "(t) => window.__log.filter(r => r.ts >= t).map("
            "r => r.type + (r.src ? ':' + r.src : '') + (r.id ? '#' + r.id : ''))", t0)
        rows.append((i + 1, round(t0 / 1000, 2), hit))
        page.wait_for_timeout(interval_ms - 450)
    print(f"\n  === 宠物页真实点击（关闭引导）每 {interval_ms/1000}s 一次，共 {n} 次 ===")
    for i, t, hit in rows:
        voiced = [h for h in hit if h.startswith("play()")]
        print(f"   第{i:2d}次 t={t:6.2f}s  "
              f"{'✅ 发声 ' + str(voiced) if voiced else '❌ 无声（点击已送达，语音被拦截）'}")
    lg = page.evaluate("window.__log")
    Path(r"C:/tmp/rp_voice_repro/e5_pet_real.json").write_text(
        json.dumps(lg, ensure_ascii=False, indent=1), encoding="utf-8")
    page.close()
    return rows


def cooldown_race_404(browser):
    """404 时 onerror 写冷却、play().catch 又删冷却 —— 顺序竞态"""
    print("\n  === 404 冷却竞态（重复 6 次观察顺序是否稳定）===")
    for k in range(6):
        page = browser.new_page()
        page.goto(f"{BASE}/pet.html")
        page.wait_for_function(
            "window.RoleplayPetVoice && window.RoleplayPetVoice.ready()", timeout=20000)
        page.route("**/assets/voice/wu_ming_zhe/zh/*.mp3",
                   lambda route: route.fulfill(status=404, body="nope"))
        r = page.evaluate("""async () => {
          const v = window.RoleplayPetVoice;
          const order = [];
          const t = (n) => order.push(n);
          window.addEventListener('pet:voice-stopped', () => t('stopped(error)'));
          v.playForSlot('click');
          await new Promise(r => setTimeout(r, 800));
          // 404 之后同一槽位能否立刻重播？（冷却是否被写入）
          const again = v.playForSlot('click');
          return {order, again: again && again.id};
        }""")
        print(f"   第{k+1}轮: 事件顺序={r['order']}  "
              f"404 后立即重播 click → {r['again'] or '❌ 被 25s 冷却拦截'}")
        page.close()


def silent_feedback(browser):
    """静默点击期间，页面给了用户什么反馈？"""
    page = browser.new_page(viewport={"width": 1280, "height": 800})
    page.goto(f"{BASE}/index.html")
    page.wait_for_timeout(6000)
    page.wait_for_function(
        "!!(window.RoleplayLive2D && window.RoleplayLive2D._ready)", timeout=20000)
    box = page.locator("#live2d-canvas").bounding_box()
    cx, cy = box["x"] + box["width"] / 2, box["y"] + box["height"] * 0.35
    print("\n  === 冷却静默期间用户可见反馈 ===")
    # 先触发一次，播完进入冷却
    page.mouse.click(cx, cy)
    page.wait_for_function(
        "window.RoleplayPetVoice && !window.__x", timeout=5000)
    page.wait_for_timeout(12000)  # 等它播完 + 落进冷却
    for i in range(3):
        before = page.evaluate("""() => ({
          bubble: (document.querySelectorAll('.bubble, #chat-messages .msg').length),
          subtitle: (() => { const e = document.getElementById('pet-subtitle');
            return e ? e.classList.contains('show') : null; })(),
          badge: (() => { const b = document.getElementById('pet-lang-badge');
            return b ? b.textContent : null; })(),
        })""")
        page.mouse.click(cx, cy)
        page.wait_for_timeout(800)
        after = page.evaluate("""() => ({
          bubble: (document.querySelectorAll('.bubble, #chat-messages .msg').length),
          subtitle: (() => { const e = document.getElementById('pet-subtitle');
            return e ? e.classList.contains('show') : null; })(),
          hasAudioPlaying: !!(window.RoleplayPetVoice),
        })""")
        print(f"   静默期第{i+1}次点击：气泡数 {before['bubble']}→{after['bubble']}，"
              f"字幕显示 {before['subtitle']}→{after['subtitle']}"
              f"  → {'角色有反应但不发声（用户判为"坏了"）' if after['bubble'] != before['bubble'] else '完全无反应'}")
        page.wait_for_timeout(2200)
    page.close()


def main():
    with sync_playwright() as p:
        b = p.chromium.launch(
            executable_path=CHROME, headless=True,
            args=["--autoplay-policy=no-user-gesture-required",
                  "--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        # pet_real_clicks(b)  # 已完成
        cooldown_race_404(b)
        silent_feedback(b)
        b.close()


if __name__ == "__main__":
    main()
