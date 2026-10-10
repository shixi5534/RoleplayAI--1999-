/*
 * pet-subtitle.js —— 宠物语音双语字幕组件 + 配音语言常驻切换徽章
 *
 * 监听 RoleplayPetVoice 广播的事件，在宠物脚下显示游戏风格双语字幕：
 *   - pet:voice-line    detail:{clip, slot, lang, subtitle:{zh,en}}  → 显示字幕
 *   - pet:voice-playing detail:{clip, slot}                           → 重置兜底计时
 *   - pet:voice-ended   detail:{clip, slot}                           → 安排隐藏
 *   - pet:voice-stopped detail:{clip, slot, reason}                   → 立即隐藏
 *   - pet:voice-lang    detail:{lang}                                 → 刷新语言徽章
 * 兜底计时不依赖 clip.dur，用 clip.end - clip.start 计算；
 * 音频真实结束时（pet:voice-ended）再进入收尾停留计时，保证音画同步。
 *
 * 语言切换徽章（#pet-lang-badge）独立于字幕条、常驻窗口右上角：
 * 不播放语音时也能随时切换中/英配音（旧版徽章藏在字幕条上，只有播放时
 * 才出现，用户在聊天页/待机时无从切换——已废弃该设计）。
 *
 * 依赖：pet-voice.js（只依赖其事件与 toggleLang；语音模块不在也能安全降级）。
 * 降级：DOM 注入失败则整体静默。
 */
(function () {
  "use strict";

  const HIDE_EXTRA_MS = 1600;   // 音频结束后字幕多停留的时间
  const HUD_GAP_PX = 12;        // 字幕与 HUD 之间的最小间距
  const TOP_SAFE_PX = 12;       // 字幕顶部与舞台顶部的安全边距
  const MIN_LIFT_PX = 64;       // 抬升量下限（不得贴到底边）
  const LIFT_MAX_RATIO = 0.4;   // 抬升量上限：不超过舞台高的 40%

  // 字幕可读性下限（用户反馈「英语读不完」）
  const MIN_DWELL_MS = 2200;    // 最短停留：再短也让人看不清
  const READ_CPS_ZH = 6;        // 中文阅读速度（字/秒，保守）
  const READ_CPS_EN = 14;       // 英文阅读速度（字符/秒，保守）
  const READ_SLACK = 1.15;      // 宽放系数：留出扫视与反应时间
  const MAX_DWELL_MS = 20000;   // 上限：避免长句霸屏太久

  /**
   * 估算读完整条字幕所需秒数。
   * 字幕同时显示中英两行，取更慢的那一行（两行都要读），再乘宽放系数。
   * 不计空格以外的复杂度：这是保守下界，够用来兜住"读不完"。
   */
  function readingSeconds(zh, en) {
    const secZh = ((zh || "").length) / READ_CPS_ZH;
    const secEn = ((en || "").length) / READ_CPS_EN;
    return Math.max(secZh, secEn) * READ_SLACK;
  }

  let el = null;
  let elZh = null;
  let elEn = null;
  let elBadge = null;     // 常驻语言切换徽章（独立于字幕条）
  let hideTimer = null;
  let curClipId = null;   // 当前字幕对应的片段 id（音画同步过滤用）
  let lastShown = null;   // 上一句字幕（冷却被拒时闪现回显用）

  function build() {
    if (!document.body) return false;
    // 挂载点：聊天页挂进角色舞台 .stage（字幕/徽章随舞台定位、随舞台裁剪），
    // 宠物页（无 .stage）挂 body —— 两页共用同一套组件与样式
    const host = document.querySelector(".stage") || document.body;
    if (!el) {
      el = document.createElement("div");
      el.id = "pet-subtitle";
      el.setAttribute("role", "status");
      el.setAttribute("aria-live", "polite");

      elZh = document.createElement("div");
      elZh.className = "sub-zh";

      elEn = document.createElement("div");
      elEn.className = "sub-en";

      el.appendChild(elZh);
      el.appendChild(elEn);
      host.appendChild(el);
    }
    if (!elBadge) {
      elBadge = document.createElement("div");
      elBadge.id = "pet-lang-badge";
      elBadge.setAttribute("role", "button");
      elBadge.setAttribute("tabindex", "0");          // 键盘可达（无障碍）
      elBadge.setAttribute("aria-pressed", "false");
      elBadge.title = "切换配音（中配 / 英配）";
      const toggle = (e) => {
        e.stopPropagation();          // 不触发宠物点击
        e.preventDefault();
        const v = window.RoleplayPetVoice;
        if (v && typeof v.toggleLang === "function") v.toggleLang();
        refreshLangBadge();
      };
      elBadge.addEventListener("click", toggle);
      elBadge.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") toggle(e); // 键盘激活
      });
      host.appendChild(elBadge);
    }
    refreshLangBadge();
    return true;
  }

  function refreshLangBadge() {
    if (!elBadge) return;
    let lang = "zh";
    const v = window.RoleplayPetVoice;
    if (v && typeof v.getLang === "function") lang = v.getLang();
    // 当前配音高亮：<b>中</b>/<i>EN</i>（aria-pressed 暴露当前是否英配）
    elBadge.innerHTML = lang === "zh"
      ? "<b>中</b><i>/EN</i>"
      : "<i>中/</i><b>EN</b>";
    try { elBadge.setAttribute("aria-pressed", lang === "en" ? "true" : "false"); } catch (_) {}
  }

  /*
   * 排版修复（P0）：让字幕条在任意舞台尺寸下都"不碰 HUD、不出舞台"。
   *
   * 原来 bottom 写死 134px（按 HUD 两行 ~80px 估算），但 .stage 高度随视口
   * 变化极大（1440x950 ≈ 857px；800x600 ≈ 240px），固定值在矮舞台上会把
   * 字幕顶到贴着顶部，长文本几乎没有可用行数。
   *
   * 这里实测 HUD 与舞台尺寸，把两个结果写进 CSS 变量：
   *   --sub-lift : 字幕底边距舞台底部的距离 = HUD 高 + 底距 + 间距（夹紧）
   *   --sub-maxh : 字幕最大高度 = 舞台高 - lift - 顶部安全边距
   * 都不满足时（无 .stage / 无 HUD / 元素不可见）直接移除变量，回退 CSS 默认值。
   */
  function syncGeometry() {
    if (!el) return;
    const stage = el.parentElement;
    if (!stage || !stage.classList || !stage.classList.contains("stage")) {
      el.style.removeProperty("--sub-lift");
      el.style.removeProperty("--sub-maxh");
      return;
    }
    const stageH = stage.clientHeight;
    if (!stageH) return;
    const hud = stage.querySelector(".stage-hud") || stage.querySelector("#stage-hud");
    let lift = MIN_LIFT_PX;
    if (hud) {
      const hudRect = hud.getBoundingClientRect();
      const stageRect = stage.getBoundingClientRect();
      // HUD 底边距舞台底部的距离 + HUD 高 + 间距 = 字幕底边应处的抬升量
      const hudBottomGap = stageRect.bottom - hudRect.bottom;
      lift = hudRect.height + Math.max(0, hudBottomGap) + HUD_GAP_PX;
      if (!hudRect.height) lift = MIN_LIFT_PX;   // HUD 折叠/隐藏时用下限
    }
    // 夹紧：不低于下限，也不超过舞台高的 40%（矮舞台上避免顶到顶部）
    lift = Math.max(MIN_LIFT_PX, Math.min(lift, stageH * LIFT_MAX_RATIO));
    const maxH = Math.max(40, stageH - lift - TOP_SAFE_PX);
    // 写 CSS 变量即可：`.stage #pet-subtitle.show { bottom: var(--sub-lift) }` 会消费它。
    //
    // 排查记录（重要，避免后人重复踩坑）：在【隐藏的 headless 窗口】里量测时，
    // computed bottom 恒为基线 6px，看起来像"变量没生效"。真实原因是 CSS 里
    // `transition: ... bottom 260ms` —— 隐藏窗口没有合成器帧，过渡永不推进，
    // 于是 bottom 被钉在起始值。把 transition 关掉后立刻读到 117px（正确）。
    // 也就是说：这是【无头测量假象】，不是产品缺陷。真实浏览器里过渡正常完成。
    // 因此这里不要为了"让测量数字好看"去叠加 transform 之类的二次抬升 ——
    // 那会在真实环境里造成双倍位移（实测 bottom 511 而非 622）。
    el.style.setProperty("--sub-lift", Math.round(lift) + "px");
    el.style.setProperty("--sub-maxh", Math.round(maxH) + "px");
  }

  function hide() {
    if (!el) return;
    el.classList.remove("show");
    // 隐藏时保留变量即可（下次 show 会重算）；这里只清类，避免残留内联定位。
    el.style.removeProperty("transform");
  }

  function show(subtitle, durSec, opts) {
    if (!build()) return;
    const o = opts || {};
    const zh = (subtitle && subtitle.zh) || "";
    const en = (subtitle && subtitle.en) || "";
    if (!zh && !en) return;
    elZh.textContent = zh;
    elEn.textContent = en;
    elEn.style.display = en ? "" : "none";
    syncGeometry();               // 先按当前舞台/HUD 实测尺寸夹紧几何
    el.classList.add("show");
    syncGeometry();               // 显示后（bottom 生效）再校正一次
    // 状态样式：loading 半透明（正在加载音频）、replay 冷却回显（弱化闪现）
    el.classList.toggle("is-loading", !!o.loading);
    el.classList.toggle("is-replay", !!o.replay);
    try { el.setAttribute("aria-busy", o.loading ? "true" : "false"); } catch (_) {}
    if (hideTimer) clearTimeout(hideTimer);
    // 停留时长必须同时满足两件事：
    //   1) 至少覆盖音频播放（dur + 尾巴），否则话没说完字幕就消失了；
    //   2) 至少够把字读完 —— 这是用户反馈「英语读不完」的直接成因。
    //      实测：en_78 音频 0.92s 却显示 19 字英文 + 大量中文，旧逻辑取
    //      max(2200, 0.92*1000+1600) = 2200ms，根本读不完。
    // 阅读速度取保守值：中文 6 字/秒、英文 14 字符/秒；字幕同时显示两行，
    // 以更慢的那行为准，再乘一个宽放系数避免边缘情况。
    const readSec = readingSeconds(zh, en);
    let ms = o.replay
      ? 700
      : Math.max(MIN_DWELL_MS, (durSec || 4) * 1000 + HIDE_EXTRA_MS, readSec * 1000);
    // 上限：个别片段显示的是整段台词（如 zh_44 显示 281 字英文），
    // 若完全按阅读速度给时间会算出 60s+ 的停留，明显霸屏。
    // 这种情况靠"缩短显示文本"根治（见 manifest 片段化），这里只做兜底夹紧。
    ms = Math.min(ms, MAX_DWELL_MS);
    hideTimer = setTimeout(hide, ms);
  }

  // ── 事件接入（语音模块自初始化，晚于此脚本加载也能收到后续事件） ──
  window.addEventListener("pet:voice-line", (ev) => {
    const d = ev && ev.detail;
    if (!d) return;
    curClipId = d.clip && d.clip.id;
    lastShown = { subtitle: d.subtitle || null, durSec: d.clip && d.clip.dur };
    show(d.subtitle || { zh: d.clip && d.clip.text, en: "" },
         d.clip && d.clip.dur, { loading: true });   // 起播先以加载态呈现
  });

  // 音频真实起播 → 字幕全亮 + 重置兜底计时（用 end-start，不依赖 clip.dur）
  window.addEventListener("pet:voice-playing", (ev) => {
    const c = ev && ev.detail && ev.detail.clip;
    if (!c || !el || !el.classList.contains("show")) return;
    if (curClipId && c.id !== curClipId) return; // 只同步当前字幕对应的音频
    el.classList.remove("is-loading", "is-replay");
    try { el.setAttribute("aria-busy", "false"); } catch (_) {}
    const durMs = Math.max(2200, ((c.end - c.start) || 4) * 1000 + HIDE_EXTRA_MS);
    if (hideTimer) clearTimeout(hideTimer);
    hideTimer = setTimeout(hide, durMs);
  });

  // P0-1：音频自然播完 → 立即进入收尾停留计时
  window.addEventListener("pet:voice-ended", (ev) => {
    const c = ev && ev.detail && ev.detail.clip;
    if (c && curClipId && c.id !== curClipId) return;
    if (hideTimer) clearTimeout(hideTimer);
    hideTimer = setTimeout(hide, HIDE_EXTRA_MS);
  });

  // P0-1/P1-7：播放中断（出错/切语言等）→ 立即隐藏字幕
  // 带 clip 过滤：旧片段的 error 事件晚到时不得误隐新片段的字幕；
  // setLang 广播的 clip 是被中断的当前片段（与 curClipId 一致），不会被误过滤
  window.addEventListener("pet:voice-stopped", (ev) => {
    const c = ev && ev.detail && ev.detail.clip;
    if (c && curClipId && c.id !== curClipId) return;
    hide();
  });

  // v4：状态机转移 —— loading 态已在 voice-line 处理；idle 由 ended/stopped
  // 的收尾计时隐藏，这里不再重复隐藏（避免打断 ended 后的收尾停留）。
  // 附带：徽章播放态呼吸光圈（.is-playing）
  window.addEventListener("pet:voice-state", (ev) => {
    const d = ev && ev.detail;
    if (!d || !elBadge) return;
    if (d.phase === "playing") elBadge.classList.add("is-playing");
    else elBadge.classList.remove("is-playing");
  });

  // v4：触发被拒（冷却/忙碌）→ 闪现上一句字幕 700ms（60% 透明），
  // 让"点了没反应"变成"点到了、她在冷却"。busy/protect 等高频理由不闪现防刷屏
  window.addEventListener("pet:voice-blocked", (ev) => {
    const d = ev && ev.detail;
    if (!d || d.reason !== "cooldown") return;
    if (!lastShown || !lastShown.subtitle) return;
    show(lastShown.subtitle, lastShown.durSec, { replay: true });
  });

  window.addEventListener("pet:voice-lang", () => refreshLangBadge());

  // 窗口/舞台尺寸变化（含分栏拖拽）→ 重新夹紧字幕几何，避免字幕压住 HUD
  window.addEventListener("resize", () => { if (el && el.classList.contains("show")) syncGeometry(); });

  /*
   * HUD 折叠/展开（#hud-toggle）也会改变 HUD 高度，而它不触发 resize。
   * 用 ResizeObserver 盯住 HUD 与舞台，任何尺寸变化都重新夹紧——这样
   * 用户折叠 HUD 后字幕会自然下移贴合，展开后自动让开，不会压住它。
   */
  function observeGeometry() {
    if (typeof ResizeObserver !== "function") return;
    const host = (el && el.parentElement) || document.querySelector(".stage");
    if (!host) return;
    const ro = new ResizeObserver(() => {
      if (el && el.classList.contains("show")) syncGeometry();
    });
    const hud = host.querySelector(".stage-hud") || host.querySelector("#stage-hud");
    if (hud) ro.observe(hud);
    ro.observe(host);
  }

  // DOM 就绪即注入容器（pet.html 引入位置在 body 末尾，body 必已存在）
  build();
  observeGeometry();
})();
