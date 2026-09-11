/*
 * pet-voice.js —— 角色原声台词播放模块（v4：状态机 + 可稳定重复触发）
 *
 * 数据来源：frontend/assets/voice/wu_ming_zhe/manifest.json
 *   （faster-whisper 听录官方语音视频 → 按时间戳切分的中/英双配音切片，
 *     每条带 subtitle:{zh,en} 双语字幕文本）
 *
 * v4 解决的问题（详见 docs/语音点击交互设计.md 与 docs/调研-点击触发语音交互规范.md）：
 *   1. 旧版 25s 冷却从"音频结束"起算 → 台词越短惩罚越重（1.84s 台词死等 26.8s），
 *      且冷却期零反馈。v4：冷却从"起播"起算、分层取值（click 抢占 1.5s 可换播 /
 *      被动槽 8s / battle·enter 60s），冷却命中时广播 pet:voice-blocked 供 UI 反馈
 *   2. 音频引用残留导致永久假死（mp3 挂起时必须刷新页面）。v4：单一收口 _finish，
 *      六条退出路径（ended/error/play拒绝/起播超时/看门狗/stop）全部经过它，
 *      pause + 清定时器 + 清 src 只在此处发生
 *   3. 每次 new Audio() 在 Safari 上需重新判定自动播放许可（WebKit：per-element
 *      授予）。v4：单 <audio> 实例复用，切 src + load()
 *   4. 打断判定用 currentTime 在加载慢时为 0 → 改用 startedAt 经过时间
 *   5. pickFromSlot 去重导致单条槽位（enter zh）恒返回 null → pool 只剩当前句时允许重复
 *   6. 播放失败语义倒置（404 秒重播 / 成功等 25s）→ 错误统一 1.5s 短冷却 + 重试 1 次
 *
 * 对外暴露：window.RoleplayPetVoice
 *   - init() / ready()
 *   - playForSlot(slot, opts) / playClip(id, slot, opts) / stop()
 *   - getState() / canPlay(slot, opts) / justPlayed(withinMs)
 *   - setLang('zh'|'en') / getLang() / toggleLang()
 *   - setMuted(bool) / toggleMuted() / isMuted()
 *
 * 事件契约（detail 结构与 v3 完全兼容）：
 *   pet:voice-line    {clip, slot, lang, subtitle}          → 字幕显示
 *   pet:voice-playing {clip, slot}                          → 真实起播
 *   pet:voice-ended   {clip, slot}                          → 自然播完
 *   pet:voice-stopped {clip, slot, reason}                  → 中断（error/切语言）
 *   pet:voice-lang    {lang}                                → 配音语言切换
 *   pet:voice-state   {phase, slot, clipId, startedAt,
 *                      cooldownRemainingMs, canPreempt, reason} → 状态机转移（新增）
 *   pet:voice-blocked {slot, reason, retryInMs}             → 触发被拒（新增）
 *
 * 依赖：shared/pet-core.js（onIntent）。无第三方库。
 */
(function () {
  "use strict";

  const MANIFEST_URL = "./assets/voice/wu_ming_zhe/manifest.json";
  const LS_MUTE_KEY = "rp_pet_voice_muted";
  const LS_LANG_KEY = "rp_pet_voice_lang";

  // ── 交互参数（取值依据：docs/调研-点击触发语音交互规范.md §3/§7
  //    与 docs/语音点击交互设计.md「参数定稿」，调整前先读推导链） ──
  const SLOT_COOLDOWN_MS = 8000;      // 被动槽冷却，从起播起算（旧值 25s 从结束起算）
  const SLOT_COOLDOWN_OVERRIDE = {    // 长叙事/被动槽差异化：防待机刷屏、长台词防打断刷屏
    idle: 12000, battle: 60000, enter: 60000,
  };
  const PREEMPT_SLOTS = ["click"];    // 可打断换播的槽位（用户主动点击）
  const PREEMPT_COOLDOWN_MS = 1500;   // 抢占槽重复触发间隔（Apple：>500ms 即被视为卡死，1.5s 取行业上沿）
  const MIN_INTERRUPT_MS = 800;       // 起播后多久才允许被打断（避免刚出声就被切碎）
  const LOAD_TIMEOUT_MS = 4000;       // 起播超时：根治 mp3 挂起导致的永久假死
  const WATCHDOG_EXTRA_MS = 8000;     // 看门狗 = clip.dur + 该值，兜住 ended 不触发的极端场景
  const ERR_COOLDOWN_MS = 1500;       // 出错后的短冷却（修正"失败反而秒重播"的语义倒置）
  const ERR_RETRY = 1;                // 起播失败自动换一条重试的次数
  const ERR_RETRY_DELAY_MS = 300;
  const VOLUME = 0.9;

  // PetCore 姿态名 → 语音槽位名
  const POSE_TO_SLOT = {
    happy: "happy", love: "happy", grateful: "happy", excited: "happy",
    sad: "sad", angry: "sad",
    surprise: "surprise", confused: "surprise",
    sleepy: "sleep", sleep_in: "sleep", sleep_deep: "sleep", sleep_wake: "idle",
    idle: "idle", anxious: "idle", embarrassed: "idle",
    egg: "click", listen: "idle", rest: "idle",
  };

  // ── 模块状态 ──
  let manifest = null;
  let lang = "zh";
  let muted = false;
  let ttsHooked = false;

  // 播放状态机：idle → loading → playing → idle（异常经 error 后回 idle）
  let phase = "idle";
  let curSlot = null;      // 当前播放归属的槽位
  let curClip = null;      // 当前播放的 clip 对象
  let startedAt = 0;       // 本次起播时刻（冷却/打断判定的基准）
  let retryUsed = 0;       // 本轮起播失败已重试次数
  let loadTimer = 0;       // 起播超时定时器
  let watchdogTimer = 0;   // 播放看门狗定时器
  const lastStartAt = {};  // slot -> 上次起播时刻（冷却从起播起算）
  const lastErrorAt = {};  // slot -> 上次出错时刻（错误短冷却，优先级高于抢占）

  // 单 <audio> 实例：Safari 的自动播放许可按元素授予，复用元素只切 src
  // （WebKit 官方："Change the source of the media element instead of creating
  //   multiple media elements"）
  const el = new Audio();
  el.volume = 0.9;
  el.preload = "auto";

  try {
    muted = localStorage.getItem(LS_MUTE_KEY) === "1";
    const saved = localStorage.getItem(LS_LANG_KEY);
    if (saved === "zh" || saved === "en") lang = saved;
  } catch (_) { /* 隐私模式等场景忽略 */ }

  function log(...args) {
    if (window.RP_PET_VOICE_DEBUG) console.log("[pet-voice]", ...args);
  }

  function dnd() { return document.body.classList.contains("dnd"); }

  function cooldownMs(slot) {
    return (slot && SLOT_COOLDOWN_OVERRIDE[slot]) || SLOT_COOLDOWN_MS;
  }
  function cooldownRemaining(slot) {
    const last = lastStartAt[slot] || 0;
    return Math.max(0, last + cooldownMs(slot) - Date.now());
  }
  function canPreempt(slot) {
    return PREEMPT_SLOTS.indexOf(slot) >= 0;
  }

  /** 状态机转移唯一入口：改 phase 并广播 pet:voice-state。 */
  function _setPhase(p, reason) {
    phase = p;
    try {
      window.dispatchEvent(new CustomEvent("pet:voice-state", {
        detail: {
          phase, slot: curSlot, clipId: curClip ? curClip.id : null,
          startedAt, cooldownRemainingMs: curSlot ? cooldownRemaining(curSlot) : 0,
          canPreempt: curSlot ? canPreempt(curSlot) : false,
          reason: reason || "",
        },
      }));
    } catch (_) { /* ignore */ }
  }

  /**
   * 生命周期唯一收口：所有退出路径（ended / error / play拒绝 / 起播超时 /
   * 看门狗 / stop）都必须经过这里。el 的 pause 与 src 清理只发生在这一处——
   * 这是"音频引用残留导致永久假死"的结构性根治。
   */
  function _finish(reason) {
    if (loadTimer) { clearTimeout(loadTimer); loadTimer = 0; }
    if (watchdogTimer) { clearTimeout(watchdogTimer); watchdogTimer = 0; }
    try { el.pause(); } catch (_) { /* ignore */ }
    try { el.removeAttribute("src"); el.load(); } catch (_) { /* ignore */ }
    const slot = curSlot;
    // 冷却写入：从起播起算（修正"台词越短惩罚越重"）
    if (slot) {
      if (reason === "error") {
        // 失败走短冷却（修正"404 秒重播 / 成功等 25s"的语义倒置）。
        // 用独立 lastErrorAt 记录：错误冷却必须覆盖 click 抢占路径，
        // 否则抢占判定（看 lastStartAt）会把 1.5s 错误冷却整个绕过
        lastErrorAt[slot] = Date.now();
      } else if (reason === "ended" || reason === "watchdog") {
        lastStartAt[slot] = startedAt || Date.now();
      }
      // preempt（打断换播）不写：新 clip 起播时会覆盖为当前时刻
      // stop / lang-change 不写：用户主动停止，应立即可再次触发
    }
    curSlot = null;
    curClip = null;
    startedAt = 0;
    _setPhase("idle", reason);
  }

  // ───────────────────────── 初始化 ─────────────────────────
  function init() {
    if (manifest) return Promise.resolve(manifest);
    return fetch(MANIFEST_URL, { cache: "no-store" })
      .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
      .then((m) => {
        manifest = m;
        if (m.langs && m.langs.indexOf(lang) < 0) lang = m.langs[0];
        log("manifest loaded:", manifest.clips.length, "clips, lang=", lang);
        bindIntents();
        if (!ttsHooked) {
          ttsHooked = true;
          // TTS 开始朗读时让位（AI 回复优先于原声）
          window.addEventListener("tts:started", () => { stop(); });
        }
        return manifest;
      })
      .catch((e) => {
        console.warn("[pet-voice] manifest 加载失败，语音功能停用", e);
        return null;
      });
  }

  function ready() { return !!manifest; }

  // ───────────────────────── 槽位选择 ─────────────────────────
  function pickFromSlot(slot) {
    if (!manifest || !slot) return null;
    const ids = (manifest.slots && manifest.slots[slot]) || [];
    const pool = (manifest.clips || []).filter(
      (c) => ids.indexOf(c.id) >= 0 && c.lang === lang);
    if (!pool.length) return null;
    const fresh = pool.filter((c) => !curClip || c.id !== curClip.id);
    // pool 只剩当前正在播的这句（如 enter 槽 zh 仅 1 条）→ 允许重复，
    // 否则该槽位会被去重逻辑永久卡死
    const list = fresh.length ? fresh : pool;
    return list[Math.floor(Math.random() * list.length)];
  }

  // ───────────────────────── 准入判定 ─────────────────────────
  /**
   * 判定 slot 是否可播。返回 {ok, mode?, reason?, retryInMs?}。
   * mode='preempt' 表示打断当前播放换播；'normal' 表示常规起播。
   */
  function canPlay(slot, opts) {
    const o = opts || {};
    if (!ready()) return { ok: false, reason: "not-ready" };
    if (dnd()) return { ok: false, reason: "dnd" };
    if (muted) return { ok: false, reason: "muted" };
    if (o.force) return { ok: true, mode: "normal" }; // force 只绕冷却/互斥，不绕 dnd/muted
    // 错误短冷却：优先级最高，覆盖抢占路径（连续 404 时不能无限刷请求）
    const sinceErr = Date.now() - (lastErrorAt[slot] || 0);
    if (sinceErr < ERR_COOLDOWN_MS && lastErrorAt[slot]) {
      return { ok: false, reason: "cooldown",
               retryInMs: ERR_COOLDOWN_MS - sinceErr };
    }
    if (phase === "loading") return { ok: false, reason: "busy" };
    if (phase === "playing") {
      if (!canPreempt(slot)) return { ok: false, reason: "busy" };
      const elapsed = Date.now() - startedAt; // 用经过时间判定，不用 currentTime（加载慢时为 0）
      if (elapsed < MIN_INTERRUPT_MS) {
        return { ok: false, reason: "protect",
                 retryInMs: MIN_INTERRUPT_MS - elapsed };
      }
      const sinceStart = Date.now() - (lastStartAt[slot] || 0);
      if (sinceStart < PREEMPT_COOLDOWN_MS) {
        return { ok: false, reason: "cooldown",
                 retryInMs: PREEMPT_COOLDOWN_MS - sinceStart };
      }
      return { ok: true, mode: "preempt" };
    }
    // idle：检查槽位冷却
    const rem = cooldownRemaining(slot);
    if (rem > 0) {
      if (canPreempt(slot)) {
        const sinceStart = Date.now() - (lastStartAt[slot] || 0);
        if (sinceStart < PREEMPT_COOLDOWN_MS) {
          return { ok: false, reason: "cooldown",
                   retryInMs: PREEMPT_COOLDOWN_MS - sinceStart };
        }
        // 冷却未走完但已过抢占间隔 → 允许打断换播（用户主动点击优先）
        return { ok: true, mode: "normal" };
      }
      return { ok: false, reason: "cooldown", retryInMs: rem };
    }
    return { ok: true, mode: "normal" };
  }

  // ───────────────────────── 播放 ─────────────────────────
  function stop() {
    if (phase !== "idle") _finish("stop");
  }

  function scheduleRetry(slot) {
    if (retryUsed >= ERR_RETRY) return;
    retryUsed += 1;
    setTimeout(() => {
      if (phase !== "idle") return;   // 期间被其他触发占用则放弃
      const c = pickFromSlot(slot);
      if (c) playClip(c.id, slot, { isRetry: true });
    }, ERR_RETRY_DELAY_MS);
  }

  function dispatchStopped(clip, slot, reason) {
    try {
      window.dispatchEvent(new CustomEvent("pet:voice-stopped", {
        detail: { clip, slot, reason },
      }));
    } catch (_) { /* ignore */ }
  }

  function playClip(id, slot, opts) {
    const o = opts || {};
    if (dnd() || !manifest || muted) return null;
    const clip = (manifest.clips || []).find((c) => c.id === id);
    if (!clip) return null;
    // 正在播 → 先收口（打断换播走 'preempt'，常规覆盖走 'stop'）
    if (phase !== "idle") _finish(o.preempt ? "preempt" : "stop");
    if (!o.isRetry) retryUsed = 0;

    curSlot = slot || null;
    curClip = clip;
    startedAt = Date.now();
    lastStartAt[curSlot || ""] = startedAt; // 冷却从起播起算（修正"短台词惩罚重"）
    _setPhase("loading", "start");

    // 单实例复用：切 src + load（Safari per-element 自动播放许可）
    el.src = "./assets/voice/wu_ming_zhe/" + clip.file;
    try { el.load(); } catch (_) { /* ignore */ }

    // 起播超时看门狗（根治 mp3 挂起导致的永久假死）
    if (loadTimer) clearTimeout(loadTimer);
    loadTimer = setTimeout(() => {
      if (phase === "loading") {
        log("load timeout:", clip.id);
        dispatchStopped(clip, curSlot, "load-timeout");
        _finish("load-timeout");
        scheduleRetry(slot);
      }
    }, LOAD_TIMEOUT_MS);

    // 播放看门狗（ended 因极端场景不触发时兜底收口）
    const durMs = ((clip.dur || (clip.end - clip.start) || 5) * 1000) + WATCHDOG_EXTRA_MS;
    if (watchdogTimer) clearTimeout(watchdogTimer);
    watchdogTimer = setTimeout(() => {
      if (phase === "playing" && curClip && curClip.id === clip.id) {
        log("watchdog fired:", clip.id);
        _finish("watchdog");
      }
    }, durMs);

    // 生命周期事件（属性赋值为覆盖式：单实例每次播放重新绑定当前 clip/slot）
    el.onplaying = () => {
      if (loadTimer) { clearTimeout(loadTimer); loadTimer = 0; }
      retryUsed = 0; // 起播成功即清零重试计数
      _setPhase("playing", "playing");
      try {
        window.dispatchEvent(new CustomEvent("pet:voice-playing",
          { detail: { clip, slot } }));
      } catch (_) { /* ignore */ }
    };
    el.onended = () => {
      if (phase === "idle") return; // 已被收口（如 stop 清 src 后的残留事件）
      try {
        window.dispatchEvent(new CustomEvent("pet:voice-ended",
          { detail: { clip, slot } }));
      } catch (_) { /* ignore */ }
      _finish("ended");
    };
    el.onerror = () => {
      if (phase === "idle") return; // 清 src + load() 引发的空源错误，忽略
      try {
        window.dispatchEvent(new CustomEvent("pet:voice-stopped",
          { detail: { clip, slot, reason: "error" } }));
      } catch (_) { /* ignore */ }
      _finish("error");
      scheduleRetry(slot);
    };

    const p = el.play();
    if (p && typeof p.catch === "function") {
      p.catch((e) => {
        const name = e && e.name;
        if (name === "AbortError") return; // 主动打断（如紧接着换播），静默忽略
        // NotAllowedError 等：自动播放被拒（Safari 未激活等），通知 UI 并走错误冷却
        log("play rejected:", name);
        try {
          window.dispatchEvent(new CustomEvent("pet:voice-blocked", {
            detail: { slot, reason: "autoplay-blocked", retryInMs: ERR_COOLDOWN_MS },
          }));
        } catch (_) { /* ignore */ }
        if (phase !== "idle") _finish("play-rejected");
        scheduleRetry(slot);
      });
    }

    // 广播给字幕组件等（subtitle 恒为双语：{zh, en}）
    try {
      window.dispatchEvent(new CustomEvent("pet:voice-line", {
        detail: {
          clip, slot,
          lang: clip.lang,
          subtitle: clip.subtitle
            || { zh: clip.text || "", en: clip.text || "" },
        },
      }));
    } catch (_) { /* ignore */ }
    log("play", clip.id, "slot=", slot, (clip.subtitle || {}).zh);
    return clip;
  }

  function playForSlot(slot, opts) {
    if (!slot) return null;
    const o = opts || {};
    const verdict = canPlay(slot, o);
    if (!verdict.ok) {
      // 冷却/忙碌等被拒：广播给字幕/按钮层做反馈（不再是无声的静默拒绝）
      try {
        window.dispatchEvent(new CustomEvent("pet:voice-blocked", {
          detail: { slot, reason: verdict.reason, retryInMs: verdict.retryInMs || 0 },
        }));
      } catch (_) { /* ignore */ }
      return null;
    }
    const clip = pickFromSlot(slot);
    return clip ? playClip(clip.id, slot, { preempt: verdict.mode === "preempt" }) : null;
  }

  // ───────────────────────── 状态查询 ─────────────────────────
  function getState() {
    return {
      phase, slot: curSlot, clipId: curClip ? curClip.id : null,
      startedAt,
      elapsedMs: startedAt ? Date.now() - startedAt : 0,
      cooldownRemainingMs: curSlot ? cooldownRemaining(curSlot) : 0,
      canPreempt: curSlot ? canPreempt(curSlot) : false,
      muted, lang, dnd: dnd(),
    };
  }

  /** 原声是否正在接管发声（loading/playing）：聊天页据此跳过 TTS 兜底。 */
  function justPlayed() {
    return phase === "playing" || phase === "loading";
  }

  // ───────────────────────── 配音语言 ─────────────────────────
  function setLang(v) {
    if (v !== "zh" && v !== "en") return lang;
    const changed = v !== lang;
    lang = v;
    try { localStorage.setItem(LS_LANG_KEY, lang); } catch (_) {}
    if (changed) {
      const prev = curClip;
      const wasPlaying = phase !== "idle";
      stop(); // 换语言时停掉当前播放，下次触发即用新配音
      if (wasPlaying) {
        dispatchStopped(prev, null, "lang-change");
      }
      try {
        window.dispatchEvent(new CustomEvent("pet:voice-lang",
          { detail: { lang } }));
      } catch (_) { /* ignore */ }
    }
    return lang;
  }
  function getLang() { return lang; }
  function toggleLang() { return setLang(lang === "zh" ? "en" : "zh"); }

  // ───────────────────────── 意图绑定 ─────────────────────────
  function bindIntents() {
    const core = window.RoleplayPetCore;
    if (!core || !core.onIntent) return;
    // 点击宠物：随机一句互动原声
    core.onIntent("click", () => { playForSlot("click"); });
    // 姿态变化：happy/sad/sleep 等映射到语音槽位
    core.onIntent("motion", (detail) => {
      const pose = (detail && (detail.pose || detail.emotion)) || "";
      // pose:"click" 是 pet.js 给 Spine 的动画指令，点击语义已由 click 意图单独处理
      if (pose === "click") return;
      const slot = POSE_TO_SLOT[String(pose).trim()];
      if (slot) playForSlot(slot);
    });
    core.onIntent("emotion", (detail) => {
      const emotion = (detail && (detail.emotion || detail.pose)) || "";
      const slot = POSE_TO_SLOT[String(emotion).trim()];
      if (slot) playForSlot(slot);
    });
  }

  // ───────────────────────── 静音 ─────────────────────────
  function setMuted(v) {
    muted = !!v;
    if (muted) stop();
    try { localStorage.setItem(LS_MUTE_KEY, muted ? "1" : "0"); } catch (_) {}
    return muted;
  }
  function toggleMuted() { return setMuted(!muted); }
  function isMuted() { return muted; }

  window.RoleplayPetVoice = {
    init, ready, playForSlot, playClip, stop,
    getState, canPlay, justPlayed,
    setLang, getLang, toggleLang,
    setMuted, toggleMuted, isMuted,
  };

  // pet.js 未必主动调用 init；脚本加载后自初始化（异步、失败静默）
  init();
})();
