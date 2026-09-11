# -*- coding: utf-8 -*-
"""点击触发语音播放 —— Bug 复现脚本（只观测，不改项目文件）

实验：
  E1 桌面宠物页真实点击（pet.html / #pet-canvas），3s 一次，共 14 次
  E2 聊天页真实点击（index.html / #live2d-canvas），3s 一次，共 10 次
  E3 冷却窗口精确测量（API 层，1s 轮询探测）
  E4 异常路径：404 / 加载挂起 / 播放中 stop()，检测 audio 引用残留（全局互斥假死）
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

CHROME = r"C:/Users/Lenovo/AppData/Local/ms-playwright/chromium-1217/chrome-win64/chrome.exe"
BASE = "http://127.0.0.1:18080"
OUT = Path("/tmp/rp_voice_repro")

INSTRUMENT = """() => {
  window.__t0 = performance.now();
  window.__log = [];          // {ts, type, src?, id?, slot?, extra?}
  const ts = () => Math.round(performance.now() - window.__t0);
  window.__ts = ts;
  window.__plays = [];
  if (!window.__origPlay) {
    window.__origPlay = Audio.prototype.play;
    Audio.prototype.play = function () {
      const src = String(this.src || '').split('/').pop();
      const rec = {ts: ts(), src: src, state: this.readyState};
      window.__plays.push(rec);
      window.__log.push({ts: ts(), type: 'play()', src: src});
      const p = window.__origPlay.call(this);
      if (p && p.then) {
        p.then(() => window.__log.push(
          {ts: ts(), type: 'play:resolved', src: src}))
         .catch((e) => window.__log.push(
          {ts: ts(), type: 'play:rejected', src: src,
           err: String((e && e.name) || e)}));
      }
      return p;
    };
  }
  ['pet:voice-line','pet:voice-playing','pet:voice-ended','pet:voice-stopped']
    .forEach((n) => window.addEventListener(n, (e) => {
      const d = e.detail || {};
      window.__log.push({ts: ts(), type: n.replace('pet:voice-',''),
        id: d.clip && d.clip.id, slot: d.slot, reason: d.reason});
    }));
  window.addEventListener('pet:intent:click',
    () => window.__log.push({ts: ts(), type: 'intent:click'}));
  window.addEventListener('live2d:interact', (e) => window.__log.push(
    {ts: ts(), type: 'live2d:interact', region: e.detail && e.detail.region}));
}"""


def dump_log(page, tag):
    lg = page.evaluate("window.__log")
    (OUT / f"{tag}.json").write_text(
        json.dumps(lg, ensure_ascii=False, indent=1), encoding="utf-8")
    return lg


def print_log(lg, title):
    print(f"\n--- {title} ---")
    for r in lg:
        extra = " ".join(
            f"{k}={v}" for k, v in r.items()
            if k not in ("ts", "type") and v is not None)
        print(f"  t={r['ts']/1000:7.2f}s  {r['type']:<14} {extra}")


# ───────────────────────── E1 宠物页真实点击 ─────────────────────────
def e1(browser, click_interval_ms=3000, clicks=14):
    page = browser.new_page(viewport={"width": 1280, "height": 800})
    errs = []
    page.on("pageerror", lambda e: errs.append(str(e)))
    page.goto(f"{BASE}/pet.html")
    page.wait_for_selector("#pet-canvas canvas", timeout=20000)
    page.wait_for_function(
        "window.RoleplayPetVoice && window.RoleplayPetVoice.ready()",
        timeout=20000)
    page.evaluate(INSTRUMENT)
    box = page.locator("#pet-canvas").bounding_box()
    cx, cy = box["x"] + box["width"] / 2, box["y"] + box["height"] * 0.75

    marks = []
    for i in range(clicks):
        page.mouse.click(cx, cy)
        t_click = page.evaluate("window.__ts()")
        page.wait_for_timeout(450)
        after = page.evaluate(
            "(t) => window.__log.filter(r => r.ts >= t && "
            "(r.type==='play()'||r.type==='line')).map(r=>r.type+':'+(r.src||r.id||''))",
            t_click)
        marks.append((i + 1, round(t_click / 1000, 2), after))
        page.wait_for_timeout(click_interval_ms - 450)

    lg = dump_log(page, "e1_pet_clicks")
    print_log(lg, "E1 宠物页真实点击 · 事件流")
    print("\n  === E1 每次点击是否发声 ===")
    for n, t, after in marks:
        print(f"   第{n:2d}次点击 t={t:6.2f}s  → "
              f"{'发声 ' + str(after) if after else '❌ 静默（无任何反应）'}")
    # 关掉 onboarding / locked 干扰说明
    st = page.evaluate("""() => ({
      locked: !!(window.__petState && window.__petState.locked),
      dnd: document.body.classList.contains('dnd'),
      muted: window.RoleplayPetVoice.isMuted(),
      lang: window.RoleplayPetVoice.getLang(),
    })""")
    print(f"  页面状态: {st}  pageerror={errs[:3]}")
    page.close()
    return marks


# ───────────────────────── E2 聊天页真实点击 ─────────────────────────
def e2(browser, click_interval_ms=3000, clicks=10):
    page = browser.new_page(viewport={"width": 1280, "height": 800})
    errs = []
    page.on("pageerror", lambda e: errs.append(str(e)))
    page.goto(f"{BASE}/index.html")
    page.wait_for_timeout(6000)
    ready = page.evaluate(
        "!!(window.RoleplayLive2D && window.RoleplayLive2D._ready)")
    print(f"\n  [E2] live2d _ready={ready}")
    page.evaluate(INSTRUMENT)
    box = page.locator("#live2d-canvas").bounding_box()
    if not box:
        print("  [E2] 找不到 #live2d-canvas，跳过")
        page.close()
        return []
    cx, cy = box["x"] + box["width"] / 2, box["y"] + box["height"] * 0.35
    marks = []
    for i in range(clicks):
        page.mouse.click(cx, cy)
        t_click = page.evaluate("window.__ts()")
        page.wait_for_timeout(450)
        after = page.evaluate(
            "(t) => window.__log.filter(r => r.ts >= t && "
            "(r.type==='play()'||r.type==='line'||r.type==='intent:click'"
            "||r.type==='interact')).map(r=>r.type+':'+(r.src||r.id||r.region||''))",
            t_click)
        marks.append((i + 1, round(t_click / 1000, 2), after))
        page.wait_for_timeout(click_interval_ms - 450)
    lg = dump_log(page, "e2_index_clicks")
    print_log(lg, "E2 聊天页真实点击 · 事件流")
    print("\n  === E2 每次点击链路 ===")
    for n, t, after in marks:
        print(f"   第{n:2d}次点击 t={t:6.2f}s  → {after or '❌ 链路无反应'}")
    print(f"  pageerror={errs[:3]}")
    page.close()
    return marks


# ───────────────────────── E3 冷却窗口精确测量 ─────────────────────────
def e3(browser):
    page = browser.new_page()
    page.goto(f"{BASE}/pet.html")
    page.wait_for_function(
        "window.RoleplayPetVoice && window.RoleplayPetVoice.ready()",
        timeout=20000)
    page.evaluate(INSTRUMENT)
    # 起播一次 click
    first = page.evaluate(
        "() => { const c = window.RoleplayPetVoice.playForSlot('click');"
        " return c && {id:c.id, dur:c.dur, sub:(c.subtitle||{}).zh}; }")
    print(f"\n  [E3] 首次 playForSlot('click') → {first}")
    if not first:
        page.close()
        return
    # 等 ended
    page.wait_for_function(
        "window.__log.some(r => r.type === 'ended')", timeout=30000)
    t_end = page.evaluate(
        "window.__log.filter(r=>r.type==='ended').slice(-1)[0].ts")
    print(f"       音频结束于 t={t_end/1000:.2f}s（clip dur={first['dur']}s）")

    # 每 1s 探测一次，直到成功（最多 60s）
    ok_at = None
    for k in range(1, 61):
        page.wait_for_timeout(1000)
        r = page.evaluate(
            "() => { const c = window.RoleplayPetVoice.playForSlot('click');"
            " return c && c.id; }")
        t = page.evaluate("window.__ts()")
        if r:
            ok_at = t
            print(f"       探测 +{k:2d}s (t={t/1000:6.2f}s) → 成功播放 {r}")
            break
        if k % 5 == 0:
            print(f"       探测 +{k:2d}s (t={t/1000:6.2f}s) → 仍被拦截")
    if ok_at:
        print(f"  >>> E3 结论：音频结束后 { (ok_at - t_end)/1000:.1f}s 才允许再次发声"
              f"（= 25s 冷却，从 ended 起算）")
    else:
        print("  >>> E3 结论：60s 内都无法再次发声 —— 疑似永久假死！")
    dump_log(page, "e3_cooldown")
    page.close()


# ───────────────────────── E4 异常路径 ─────────────────────────
def e4(browser):
    results = {}

    # E4-a：404（mp3 不存在）
    page = browser.new_page()
    page.goto(f"{BASE}/pet.html")
    page.wait_for_function(
        "window.RoleplayPetVoice && window.RoleplayPetVoice.ready()",
        timeout=20000)
    page.evaluate(INSTRUMENT)
    page.route("**/assets/voice/wu_ming_zhe/zh/*.mp3",
               lambda route: route.fulfill(status=404, body="nope"))
    page.evaluate(
        "() => { window.__r = window.RoleplayPetVoice.playForSlot('click'); }")
    page.wait_for_timeout(2500)
    r = page.evaluate("""() => {
      // 用未使用过的槽位探测全局互斥：若 audio 残留，非 force 调用一律返回 null
      const probe = window.RoleplayPetVoice.playForSlot('surprise');
      return {first: window.__r && window.__r.id, probe: probe && probe.id,
              log: window.__log};
    }""")
    results["404"] = r
    print("\n  [E4-a] mp3 全部 404：")
    print(f"        首次 playForSlot('click') → {r['first']}")
    print(f"        2.5s 后 playForSlot('surprise')（新槽位，探测全局互斥）→ "
          f"{r['probe']}  → {'✅ 互斥已释放' if r['probe'] else '❌ 互斥残留（假死）'}")
    print_log(r["log"], "E4-a 事件流")
    page.close()

    # E4-b：请求挂起（永不返回）——模拟弱网/ stalled
    page = browser.new_page()
    page.goto(f"{BASE}/pet.html")
    page.wait_for_function(
        "window.RoleplayPetVoice && window.RoleplayPetVoice.ready()",
        timeout=20000)
    page.evaluate(INSTRUMENT)
    hung = {"n": 0}

    def hang(route):
        hung["n"] += 1
        # 不 fulfill / 不 abort / 不 continue → 请求悬挂
    page.route("**/assets/voice/wu_ming_zhe/zh/*.mp3", hang)
    page.evaluate(
        "() => { window.__r = window.RoleplayPetVoice.playForSlot('click'); }")
    page.wait_for_timeout(4000)
    r = page.evaluate("""() => {
      const probe = window.RoleplayPetVoice.playForSlot('surprise');
      return {first: window.__r && window.__r.id, probe: probe && probe.id,
              log: window.__log};
    }""")
    results["hang"] = r
    print("\n  [E4-b] mp3 请求永久挂起（弱网 stalled）：")
    print(f"        首次 playForSlot('click') → {r['first']}")
    print(f"        4s 后 playForSlot('surprise') → {r['probe']}"
          f"  → {'✅ 互斥已释放' if r['probe'] else '❌ 互斥残留（假死，直到刷新页面）'}")
    print_log(r["log"], "E4-b 事件流")
    page.close()

    # E4-c：播放中 tts:started（stop() 打断）后，冷却是否写入？
    page = browser.new_page()
    page.goto(f"{BASE}/pet.html")
    page.wait_for_function(
        "window.RoleplayPetVoice && window.RoleplayPetVoice.ready()",
        timeout=20000)
    page.evaluate(INSTRUMENT)
    page.evaluate("window.RoleplayPetVoice.playForSlot('click')")
    page.wait_for_timeout(1200)
    page.evaluate(
        "window.dispatchEvent(new CustomEvent('tts:started', {detail:{}}))")
    page.wait_for_timeout(300)
    r = page.evaluate("""() => {
      // 打断后立刻再点同一槽位：若冷却未写入（ended 没触发），应能立刻重播
      const again = window.RoleplayPetVoice.playForSlot('click');
      return {again: again && again.id, log: window.__log};
    }""")
    results["interrupt"] = r
    print("\n  [E4-c] 播放 1.2s 时被 tts:started 打断（stop()）：")
    print(f"        打断后立即 playForSlot('click') → {r['again']}"
          f"  → {'⚠️ 立刻重播（冷却被跳过）' if r['again'] else '静默'}")
    print_log(r["log"], "E4-c 事件流")
    page.close()

    # E4-d：pickFromSlot 槽位池耗尽（currentClipId 未清空时）
    page = browser.new_page()
    page.goto(f"{BASE}/pet.html")
    page.wait_for_function(
        "window.RoleplayPetVoice && window.RoleplayPetVoice.ready()",
        timeout=20000)
    r = page.evaluate("""() => {
      const v = window.RoleplayPetVoice;
      const out = {};
      // enter 槽 zh 只有 1 条，连续 force 播放看是否出现 null
      const a = v.playForSlot('enter', {force:true});
      const b = v.playForSlot('enter', {force:true});
      const c = v.playForSlot('enter', {force:true});
      out.enter = [a && a.id, b && b.id, c && c.id];
      return out;
    }""")
    results["pool"] = r
    print("\n  [E4-d] 同一槽位连续 force 播放（enter 槽 zh 只有 1 条）：")
    print(f"        {r['enter']}")
    page.close()
    return results


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=CHROME, headless=True,
            args=["--autoplay-policy=no-user-gesture-required",
                  "--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        print("=" * 72)
        print("E1 桌面宠物页 · 真实点击")
        print("=" * 72)
        try:
            e1(browser)
        except Exception as ex:
            print("  E1 失败:", type(ex).__name__, ex)
        print("\n" + "=" * 72)
        print("E2 聊天页 · 真实点击")
        print("=" * 72)
        try:
            e2(browser)
        except Exception as ex:
            print("  E2 失败:", type(ex).__name__, ex)
        print("\n" + "=" * 72)
        print("E3 冷却窗口精确测量")
        print("=" * 72)
        try:
            e3(browser)
        except Exception as ex:
            print("  E3 失败:", type(ex).__name__, ex)
        print("\n" + "=" * 72)
        print("E4 异常路径")
        print("=" * 72)
        try:
            e4(browser)
        except Exception as ex:
            print("  E4 失败:", type(ex).__name__, ex)
        browser.close()


if __name__ == "__main__":
    main()
