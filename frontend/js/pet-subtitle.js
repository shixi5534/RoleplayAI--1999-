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

  function hide() {
    if (!el) return;
    el.classList.remove("show");
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
    el.classList.add("show");
    // 状态样式：loading 半透明（正在加载音频）、replay 冷却回显（弱化闪现）
    el.classList.toggle("is-loading", !!o.loading);
    el.classList.toggle("is-replay", !!o.replay);
    try { el.setAttribute("aria-busy", o.loading ? "true" : "false"); } catch (_) {}
    if (hideTimer) clearTimeout(hideTimer);
    const ms = Math.max(o.replay ? 700 : 2200,
                        (durSec || 4) * 1000 + HIDE_EXTRA_MS);
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

  // DOM 就绪即注入容器（pet.html 引入位置在 body 末尾，body 必已存在）
  build();
})();
