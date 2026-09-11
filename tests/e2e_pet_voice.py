# -*- coding: utf-8 -*-
"""E2E：宠物页语音台词模块（pet-voice.js）验收。

前置：前端静态服务器已运行（默认 http://127.0.0.1:18080，指向 frontend/）。
验收点：
  A. 模块加载：window.RoleplayPetVoice 存在且 manifest 加载完成
  B. 槽位播放：playForSlot('click') 返回片段且 Audio 真实进入播放状态
  C. 事件广播：pet:voice-line 事件携带片段文本
  D. 冷却：同槽位连续触发不打断当前播放
  E. 静音：setMuted(true) 后 playForSlot 返回 null
  F. 无新增 console/page 错误（语音模块相关）
  G. 双语字幕：字幕条同时显示中英两行
  H. 切英配：播放 en_ 前缀片段，字幕双语，徽章高亮 EN
  I. 切回中配
  J. manifest schema：每条 clip 有 dur>0，顶层有 version
  K. 字幕随音频结束消失：播 dur 最小片段，等 (end-start)+2s 后字幕隐藏
  L. 播放中切语言：字幕立即隐藏
  M. 勿扰拦截：body.dnd 下 playForSlot 返回 null，移除后恢复
  N. tts:started 自停：广播 TTS 开始事件后原声停止
  O. 字幕宽度：320×480 视口下 .show 字幕宽度 ≥ 视口 60%
  P. click 打断：播放中（>2s）触发 click 槽位可打断换句

用法（项目根目录，需先起前端静态服务器）：
  .venv/Scripts/python.exe tests/e2e_pet_voice.py
"""
from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

CHROME = r"C:/Users/Lenovo/AppData/Local/ms-playwright/chromium-1217/chrome-win64/chrome.exe"
URL = "http://127.0.0.1:18080/pet.html"


def main() -> int:
    ok = True
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=CHROME, headless=True,
            args=["--autoplay-policy=no-user-gesture-required"])
        page = browser.new_page()
        errors: list[str] = []
        page.on("console",
                lambda m: errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: errors.append(str(e)))

        page.goto(URL)
        page.wait_for_timeout(3500)

        # A. 模块加载
        ready = page.evaluate(
            "window.RoleplayPetVoice ? window.RoleplayPetVoice.ready() : null")
        print(f"[{'PASS' if ready else 'FAIL'}] A. 模块加载 ready={ready}")
        ok &= bool(ready)

        # 事件捕获（pet:voice-line）+ Audio play hook（new Audio 不进 DOM，
        # querySelectorAll 查不到，只能从原型层观察真实播放）
        page.evaluate("""() => {
          window.__voiceEvents = [];
          window.__audioPlayCalls = [];
          window.__lastPlayOk = false;
          window.__lastPlayErr = null;
          window.addEventListener('pet:voice-line', (e) => {
            window.__voiceEvents.push(e.detail && e.detail.clip && e.detail.clip.id);
          });
          const origPlay = Audio.prototype.play;
          Audio.prototype.play = function () {
            window.__audioPlayCalls.push(this.src);
            const p = origPlay.call(this);
            if (p && p.then) {
              p.then(() => { window.__lastPlayOk = true; })
               .catch((e) => { window.__lastPlayErr = String(e && e.name || e); });
            } else { window.__lastPlayOk = true; }
            return p;
          };
        }""")

        # B. 槽位播放
        clip = page.evaluate("""() => {
          const c = window.RoleplayPetVoice.playForSlot('click');
          return c ? {id: c.id, text: c.text} : null;
        }""")
        page.wait_for_timeout(800)
        play_state = page.evaluate(
            "({calls: window.__audioPlayCalls.length, ok: window.__lastPlayOk,"
            " err: window.__lastPlayErr})")
        playing = (bool(clip) and play_state["calls"] == 1
                   and play_state["ok"] and not play_state["err"])
        print(f"[{'PASS' if playing else 'FAIL'}] B. 槽位播放 clip={clip and clip['id']} "
              f"play_calls={play_state['calls']} ok={play_state['ok']} err={play_state['err']}")
        print(f"       文本：{(clip and clip['text'] or '')[:50]}")
        ok &= playing

        # C. 事件广播
        events = page.evaluate("window.__voiceEvents")
        got_event = bool(events) and clip and events[0] == clip["id"]
        print(f"[{'PASS' if got_event else 'FAIL'}] C. pet:voice-line 事件 events={events}")
        ok &= bool(got_event)

        # D. 冷却：播放中再次触发 click，不应发起新的 Audio.play()
        page.evaluate("window.RoleplayPetVoice.playForSlot('click')")
        page.wait_for_timeout(300)
        calls2 = page.evaluate("window.__audioPlayCalls.length")
        cooldown_ok = calls2 == 1
        print(f"[{'PASS' if cooldown_ok else 'FAIL'}] D. 冷却不打断 play_calls={calls2}")
        ok &= cooldown_ok

        # E. 静音
        page.evaluate("window.RoleplayPetVoice.setMuted(true)")
        r = page.evaluate("window.RoleplayPetVoice.playForSlot('enter', {force:true})")
        muted_ok = r is None
        page.evaluate("window.RoleplayPetVoice.setMuted(false)")
        print(f"[{'PASS' if muted_ok else 'FAIL'}] E. 静音拦截 play={r}")
        ok &= muted_ok

        # F. 错误检查（只关心语音相关的新错误）
        voice_errs = [e for e in errors
                      if "pet-voice" in e or "voice/wu_ming_zhe" in e
                      or "manifest.json" in e]
        print(f"[{'PASS' if not voice_errs else 'FAIL'}] F. 语音模块错误 {voice_errs}")
        ok &= not voice_errs

        # G. 双语字幕：触发 idle 槽位，字幕条应同时显示中英两行
        page.evaluate("window.RoleplayPetVoice.playForSlot('idle', {force:true})")
        page.wait_for_timeout(500)
        sub = page.evaluate("""() => {
          const el = document.getElementById('pet-subtitle');
          if (!el) return null;
          return {shown: el.classList.contains('show'),
                  zh: el.querySelector('.sub-zh') && el.querySelector('.sub-zh').textContent,
                  en: el.querySelector('.sub-en') && el.querySelector('.sub-en').textContent};
        }""")
        sub_ok = bool(sub and sub["shown"] and sub["zh"] and sub["en"])
        print(f"[{'PASS' if sub_ok else 'FAIL'}] G. 双语字幕同显 zh={bool(sub and sub['zh'])} en={bool(sub and sub['en'])}")
        print(f"       中：{(sub and sub['zh'] or '')[:40]}")
        print(f"       EN: {(sub and sub['en'] or '')[:60]}")
        ok &= sub_ok

        # H. 切英配：播放的 clip 应为 en_ 前缀，字幕仍双语，常驻徽章高亮 EN
        page.evaluate("window.RoleplayPetVoice.setLang('en')")
        clip_en = page.evaluate(
            "(() => { const c = window.RoleplayPetVoice.playForSlot('enter', {force:true});"
            " return c ? {id: c.id, lang: c.lang, sub: c.subtitle} : null; })()")
        page.wait_for_timeout(400)
        sub2 = page.evaluate("""() => {
          const el = document.getElementById('pet-subtitle');
          const badge = document.getElementById('pet-lang-badge');
          return el ? {shown: el.classList.contains('show'),
                       zh: el.querySelector('.sub-zh').textContent,
                       en: el.querySelector('.sub-en').textContent,
                       badge: badge ? badge.textContent : null} : null;
        }""")
        en_ok = (bool(clip_en and clip_en["lang"] == "en"
                  and clip_en["id"].startswith("en_"))
                 and bool(sub2 and sub2["shown"] and sub2["zh"] and sub2["en"])
                 and "EN" in (sub2["badge"] or ""))
        print(f"[{'PASS' if en_ok else 'FAIL'}] H. 英配切换 clip={clip_en and clip_en['id']} badge={sub2 and sub2['badge']}")
        print(f"       中：{(sub2 and sub2['zh'] or '')[:40]}")
        print(f"       EN: {(sub2 and sub2['en'] or '')[:60]}")
        ok &= en_ok

        # I. 切回中配
        back = page.evaluate(
            "window.RoleplayPetVoice.toggleLang()")
        print(f"[{'PASS' if back == 'zh' else 'FAIL'}] I. 切回中配 lang={back}")
        ok &= (back == "zh")

        # J. manifest schema：每条 clip 有 dur>0 且顶层有 version
        m = page.evaluate(
            "fetch('./assets/voice/wu_ming_zhe/manifest.json')"
            ".then((r) => r.json())")
        bad_dur = [c["id"] for c in m.get("clips", [])
                   if not (c.get("dur") or 0) > 0]
        j_ok = ("version" in m) and not bad_dur
        print(f"[{'PASS' if j_ok else 'FAIL'}] J. manifest schema "
              f"version={'version' in m} bad_dur={bad_dur[:5]}")
        ok &= j_ok

        # K. 字幕随音频结束消失：播 dur 最小的中文 clip，等 (end-start)+2.5s
        shortest = min((c for c in m["clips"] if c["lang"] == "zh"),
                       key=lambda c: c["dur"])
        shown_k = page.evaluate(
            "(id) => !!window.RoleplayPetVoice.playClip(id, 'click')",
            shortest["id"]) and page.evaluate(
            "document.getElementById('pet-subtitle')"
            ".classList.contains('show')")
        page.wait_for_timeout(int(shortest["dur"] * 1000) + 2500)
        hidden_k = page.evaluate(
            "!document.getElementById('pet-subtitle').classList.contains('show')")
        k_ok = bool(shown_k) and bool(hidden_k)
        print(f"[{'PASS' if k_ok else 'FAIL'}] K. 字幕随音频结束消失 "
              f"clip={shortest['id']} dur={shortest['dur']} "
              f"shown={shown_k} hidden={hidden_k}")
        ok &= k_ok

        # L. 播放中切语言字幕立即隐藏（此时为中配，切到 en）
        page.evaluate(
            "window.RoleplayPetVoice.playForSlot('enter', {force:true})")
        page.wait_for_timeout(800)
        page.evaluate("window.RoleplayPetVoice.setLang('en')")
        page.wait_for_timeout(200)
        l_hidden = page.evaluate(
            "!document.getElementById('pet-subtitle').classList.contains('show')")
        page.evaluate("window.RoleplayPetVoice.setLang('zh')")  # 恢复中配
        print(f"[{'PASS' if l_hidden else 'FAIL'}] L. 切语言字幕立即隐藏 hidden={l_hidden}")
        ok &= l_hidden

        # M. dnd 拦截：body.dnd 下返回 null，移除后恢复
        page.evaluate("document.body.classList.add('dnd')")
        r_m = page.evaluate(
            "window.RoleplayPetVoice.playForSlot('click', {force:true})")
        page.evaluate("document.body.classList.remove('dnd')")
        r_m2 = page.evaluate(
            "window.RoleplayPetVoice.playForSlot('click', {force:true})")
        m_ok = r_m is None and r_m2 is not None
        print(f"[{'PASS' if m_ok else 'FAIL'}] M. 勿扰拦截 dnd={r_m} 恢复={r_m2 and r_m2['id']}")
        ok &= m_ok

        # N. tts:started 自停（从 Audio.prototype.pause hook 观察）
        page.evaluate("""() => {
          if (!window.__pauseHooked) {
            window.__pauseHooked = true;
            window.__audioPauseCalls = 0;
            const origPause = Audio.prototype.pause;
            Audio.prototype.pause = function () {
              window.__audioPauseCalls += 1;
              return origPause.call(this);
            };
          }
        }""")
        page.evaluate(
            "window.RoleplayPetVoice.playForSlot('idle', {force:true})")
        page.wait_for_timeout(400)
        pause_before = page.evaluate("window.__audioPauseCalls")
        page.evaluate(
            "window.dispatchEvent(new CustomEvent('tts:started', {detail:{}}))")
        page.wait_for_timeout(300)
        pause_after = page.evaluate("window.__audioPauseCalls")
        n_ok = pause_after > pause_before
        print(f"[{'PASS' if n_ok else 'FAIL'}] N. tts:started 自停 "
              f"pause {pause_before}→{pause_after}")
        ok &= n_ok

        # O. 字幕宽度+溢出：320×480 视口下 .show 字幕 ≥ 视口 60%，且不溢出视口
        page.set_viewport_size({"width": 320, "height": 480})
        longest = max(m["clips"], key=lambda c: len(
            (c.get("subtitle") or {}).get("zh") or ""))
        page.evaluate(
            "(id) => window.RoleplayPetVoice.playClip(id, 'idle')",
            longest["id"])
        page.wait_for_timeout(500)
        sub_w = page.evaluate("""() => {
          const el = document.getElementById('pet-subtitle');
          if (!el || !el.classList.contains('show')) return {w: 0, r: null};
          const r = el.getBoundingClientRect();
          return {w: el.offsetWidth,
                  r: {left: r.left, right: r.right, vw: innerWidth}};
        }""")
        o_ok = (sub_w["w"] >= 320 * 0.6 and sub_w["r"]
                and sub_w["r"]["left"] >= 0
                and sub_w["r"]["right"] <= sub_w["r"]["vw"] + 0.5)
        print(f"[{'PASS' if o_ok else 'FAIL'}] O. 小视口字幕宽度+无溢出 "
              f"width={sub_w['w']}px 阈值={int(320 * 0.6)}px "
              f"rect=({sub_w['r']['left']:.0f},{sub_w['r']['right']:.0f}) vw={sub_w['r']['vw']}")
        ok &= o_ok

        # O2. 常驻语言徽章：不播放语音时也存在于右上角且可点击切换
        page.wait_for_timeout(2500)   # 等字幕自然隐藏
        badge_state = page.evaluate("""() => {
          const b = document.getElementById('pet-lang-badge');
          if (!b) return null;
          const r = b.getBoundingClientRect();
          const st = getComputedStyle(b);
          return {text: b.textContent,
                  visible: r.width > 0 && r.height > 0
                    && st.display !== 'none' && st.visibility !== 'hidden',
                  pe: st.pointerEvents,
                  pos: {top: r.top, right: innerWidth - r.right}};
        }""")
        badge_ok = bool(badge_state and badge_state["visible"]
                        and badge_state["pe"] != "none"
                        and badge_state["pos"]["top"] >= 0
                        and badge_state["pos"]["right"] >= 0
                        and "中" in badge_state["text"])
        print(f"[{'PASS' if badge_ok else 'FAIL'}] O2. 常驻语言徽章 "
              f"text={badge_state and badge_state['text']} visible={badge_state and badge_state['visible']}")
        ok &= badge_ok
        page.set_viewport_size({"width": 1280, "height": 720})
        ok &= o_ok

        # P. click 打断：播 enter 长台词 2.5s 后触发 click 槽位应换句
        #    （打断路径经 playForSlot('click') 驱动；用新页面保证 click 槽无冷却残留）
        page_p = browser.new_page()
        page_p.on("console",
                  lambda m: errors.append(m.text) if m.type == "error" else None)
        page_p.on("pageerror", lambda e: errors.append(str(e)))
        page_p.goto(URL)
        page_p.wait_for_timeout(3500)
        page_p.evaluate("""() => {
          window.__audioPlayCalls = [];
          const origPlay = Audio.prototype.play;
          Audio.prototype.play = function () {
            window.__audioPlayCalls.push(this.src);
            return origPlay.call(this);
          };
        }""")
        enter_clip = page_p.evaluate("""() => {
          return fetch('./assets/voice/wu_ming_zhe/manifest.json')
            .then((r) => r.json())
            .then((mm) => {
              const ids = mm.slots.enter || [];
              const pool = mm.clips.filter(
                (c) => ids.indexOf(c.id) >= 0 && c.lang === 'zh');
              return pool.reduce((a, b) => (a.dur >= b.dur ? a : b));
            });
        }""")
        page_p.evaluate(
            "(id) => window.RoleplayPetVoice.playClip(id, 'enter')",
            enter_clip["id"])
        page_p.wait_for_timeout(2500)
        p_result = page_p.evaluate("""() => {
          const before = window.__audioPlayCalls.length;
          const clip = window.RoleplayPetVoice.playForSlot('click');
          return {before, after: window.__audioPlayCalls.length,
                  clip: clip && clip.id};
        }""")
        p_ok = (p_result["after"] == 2 and p_result["clip"]
                and p_result["clip"] != enter_clip["id"])
        print(f"[{'PASS' if p_ok else 'FAIL'}] P. click 打断 enter={enter_clip['id']} "
              f"→ click={p_result['clip']} play_calls={p_result['before']}→{p_result['after']}")
        page_p.close()
        ok &= p_ok

        # ── v4 新增：Q/R/S/T（重复触发机制验收） ──
        HOOK_JS = """() => {
          window.__audioPlayCalls = [];
          window.__blocked = 0;
          const op = Audio.prototype.play;
          Audio.prototype.play = function () {
            window.__audioPlayCalls.push(this.src);
            return op.call(this);
          };
          window.addEventListener('pet:voice-blocked',
            () => { window.__blocked += 1; });
        }"""

        def fresh_page():
            """新开页面（无冷却残留），跳过引导浮层。"""
            pgx = browser.new_page()
            pgx.goto(URL)
            pgx.wait_for_timeout(3500)
            try:
                pgx.click("#onb-skip", timeout=3000)
            except Exception:
                pass
            pgx.wait_for_timeout(600)
            return pgx

        # Q. 冷却时长：click 起播后保护期内被拒，8~9.5s 恢复（v4 冷却从起播起算）
        page_q = fresh_page()
        page_q.evaluate(HOOK_JS)
        q1 = page_q.evaluate("window.RoleplayPetVoice.playForSlot('click')")
        q2 = page_q.evaluate("window.RoleplayPetVoice.playForSlot('click')")
        page_q.wait_for_timeout(8600)   # 起播 8s 冷却 + 余量
        q3 = page_q.evaluate("window.RoleplayPetVoice.playForSlot('click')")
        q_ok = bool(q1) and q2 is None and bool(q3)
        print(f"[{'PASS' if q_ok else 'FAIL'}] Q. 冷却时长 q1={q1 and q1['id']} "
              f"立即再点={'拒' if q2 is None else '放行'} 8.6s后={'可播' if q3 else '仍拒'}")
        page_q.close()
        ok &= q_ok

        # R. 弱网不自锁：mp3 挂起（route 不响应）→ 起播超时收口 → 其他槽位可播
        #    （回归根因 4：旧版此处 audio 引用残留，永久假死直到刷新）
        page_r = browser.new_page()
        page_r.route("**/zh/00.mp3", lambda route: None)   # 挂起不响应
        page_r.goto(URL)
        page_r.wait_for_timeout(3500)
        try:
            page_r.click("#onb-skip", timeout=2000)
        except Exception:
            pass
        page_r.evaluate(HOOK_JS)
        page_r.evaluate(
            "window.RoleplayPetVoice.playForSlot('enter', {force:true})")  # zh_00 挂起
        page_r.wait_for_timeout(5000)   # 起播超时 4s + 余量
        r_ok = page_r.evaluate(
            "!!window.RoleplayPetVoice.playForSlot('surprise', {force:true})")
        print(f"[{'PASS' if r_ok else 'FAIL'}] R. 弱网挂起不自锁 "
              f"挂起5s后其他槽位={'可播' if r_ok else '仍被锁'}")
        page_r.close()
        ok &= r_ok

        # S. 失败可重试：404 走 1.5s 短冷却（修复"失败反而秒重播/成功等 25s"倒置）
        page_s = browser.new_page()
        page_s.route("**/assets/voice/wu_ming_zhe/zh/*.mp3",
                     lambda route: route.fulfill(status=404, body="nf"))
        page_s.goto(URL)
        page_s.wait_for_timeout(3500)
        page_s.evaluate(HOOK_JS)
        page_s.evaluate("window.RoleplayPetVoice.playForSlot('click')")  # 404
        page_s.wait_for_timeout(400)
        s_mid = page_s.evaluate("window.RoleplayPetVoice.playForSlot('click')")
        page_s.wait_for_timeout(1600)   # 距首次 ~2s > ERR_COOLDOWN 1.5s
        s_after = page_s.evaluate("window.RoleplayPetVoice.playForSlot('click')")
        s_ok = s_mid is None and s_after is not None
        print(f"[{'PASS' if s_ok else 'FAIL'}] S. 失败可重试 "
              f"0.4s时={'拒' if s_mid is None else '放行'} 2s时={'可播' if s_after else '仍拒'}")
        page_s.close()
        ok &= s_ok

        # T. 冷却期有反馈：被拒必须广播 pet:voice-blocked（不再无声静默）
        page_t = fresh_page()
        page_t.evaluate(HOOK_JS)
        page_t.evaluate("window.RoleplayPetVoice.playForSlot('click')")
        page_t.wait_for_timeout(200)
        page_t.evaluate("window.RoleplayPetVoice.playForSlot('click')")
        page_t.wait_for_timeout(200)
        t_n = page_t.evaluate("window.__blocked")
        t_ok = t_n >= 1
        print(f"[{'PASS' if t_ok else 'FAIL'}] T. 冷却期有反馈 blocked={t_n}")
        page_t.close()
        ok &= t_ok

        browser.close()

    print("\n结果：", "全部通过" if ok else "存在失败项")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
