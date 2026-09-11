/*
 * chat.js —— 聊天前端：自实现 SSE 解析，对接后端 /chat/stream。
 * 消费 event: chunk（流式文本）/ emotion（情绪→数字人 + 标签）/ done（追问）。
 * 仅依赖原生 JS；数字人缺失时优雅降级。
 *
 * 新增：关键变量实时调节（温度/灵敏度/速度/缩放/主题/显隐）+ 键盘快捷键 + 视觉反馈。
 * 快捷键设计参考业界惯例：
 *   - Ctrl/⌘+K 聚焦输入（Slack / Linear / Notion / Gmail）
 *   - Enter 发送、Esc 关闭弹层（通用）
 *   - ? 打开快捷键帮助（GitHub / Slack）
 *   - Alt+方向键 微调数值（系统音量/亮度、Figma 微移）
 *   - 单字母切换状态（m/t/c），且仅在「非输入态」生效，避免打断打字
 */
(function () {
  "use strict";

  const API_BASE = ""; // 同源；跨域时改为后端地址
  // 桌面宠物页（pet.html）复用本文件的对话核心（window.RoleplayChat.send），
  // 但宠物页没有聊天 DOM：body[data-mode="pet"] 或缺少 #send-btn 时，
  // 跳过全部「页面级」DOM 绑定与初始化（index.html 行为完全不变）。
  const PET_MODE = document.body.dataset.mode === "pet" || !document.getElementById("send-btn");
  const WELCOME = "（面具微微偏了偏）……来了啊。坐吧，想说什么都行，我在这儿听着。";

  const EMOTION_CN = {
    happy: "开心",
    sad: "难过",
    angry: "生气",
    anxious: "焦虑",
    surprise: "惊讶",
    fear: "害怕",
    neutral: "平静",
    // 新增 8 类（15 类全链路穿透，父类分组见 EMOTION_GROUP）
    love: "爱意",
    grateful: "感激",
    excited: "兴奋",
    disappointed: "失望",
    lonely: "孤独",
    embarrassed: "害羞",
    confused: "困惑",
    sleepy: "困倦",
  };

  // 情绪父类分组（chip 着色用）：happy 系 / sad 系 / anxious 系 / neutral 系
  const EMOTION_GROUP = {
    love: "happy", grateful: "happy", excited: "happy",
    disappointed: "sad", lonely: "sad",
    embarrassed: "anxious", confused: "anxious", sleepy: "neutral",
  };
  const GROUP_CLASS = { happy: "emotion-chip-happy", sad: "emotion-chip-sad", anxious: "emotion-chip-anxious", neutral: "emotion-chip-neutral" };

  // 关键词 → Live2D 动作组（用户发言时即时触发一个手势，让角色反应更活）
  const GESTURES = {
    谢谢: "b_diantou", 感谢: "b_diantou", 多谢: "b_diantou",
    再见: "b_shanzi", 拜拜: "b_shanzi", 晚安: "b_shanzi",
    你好: "b_taishou", 在吗: "b_taishou", 嗨: "b_taishou",
    笑: "b_liaofa", 开心: "b_liaofa", 喜欢: "t_weixiao", 爱: "t_weixiao",
    难过: "t_nanguo", 伤心: "t_nanguo", 哭: "t_nanguo",
    生气: "b_yaotou", 讨厌: "b_yaotou", 烦: "b_yaotou",
    怕: "b_zhelian", 害怕: "b_zhelian", 吓: "b_zhelian",
    天哪: "t_yihuo", 不敢相信: "t_yihuo", 居然: "t_yihuo", 竟然: "t_yihuo",
    为什么: "b_shanzi", 什么: "b_shanzi", 怎么: "b_shanzi", 如何: "b_shanzi",
  };

  /** 每个浏览器分配稳定且唯一的会话 id（localStorage 持久化），实现跨轮次记忆。 */
  function getSessionId() {
    let id = null;
    try { id = localStorage.getItem("roleplay_session_id"); } catch (_) {}
    if (!id) {
      id =
        (window.crypto && crypto.randomUUID && crypto.randomUUID()) ||
        "sess-" + Date.now() + "-" + Math.random().toString(16).slice(2);
      try { localStorage.setItem("roleplay_session_id", id); } catch (_) {}
    }
    return id;
  }

  /** 从用户发言里挑出第一个命中的手势关键词，返回动作组名或 null。 */
  function detectGesture(text) {
    for (const key in GESTURES) {
      if (text.indexOf(key) !== -1) return GESTURES[key];
    }
    return null;
  }

  /**
   * 解析文本中的 {动作：动作名} / {动作:动作名} / {action:motion} 指令。
   * 支持全角/半角冒号、中英文关键词，一次可含多个指令。
   * 返回 { motions: string[], clean: string } —— motions 为动作名数组，clean 为剥离指令后的纯文本。
   *
   * 示例：
   *   "你好呀{动作：b_shanzi}" → { motions: ["b_shanzi"], clean: "你好呀" }
   *   "{action:t_weixiao}很高兴见到你{动作：b_diantou}" → { motions: ["t_weixiao","b_diantou"], clean: "很高兴见到你" }
   */
  function parseActionCommands(text) {
    const motions = [];
    let clean = text;
    // 匹配 {动作：xxx} {动作:xxx} {action:xxx} {Action:xxx}，容错全角/半角冒号、首尾空格
    const re = /\{[ \t]*(?:动作|action|Action)[ \t]*[:：][ \t]*([^}]+?)[ \t]*\}/g;
    clean = clean.replace(re, (_, name) => {
      const m = String(name).trim();
      if (m) motions.push(m);
      return ""; // 从显示文本中剥离指令标记
    });
    // 清理剥离后可能残留的多余空格（连续空格合并为单个）
    // 注意：只剥首尾的空格/制表符，**不能用 trim()**——trim 会把换行一起吃掉，
    // 而后端是逐 token 流式，换行几乎总是独立 chunk，一旦被吃掉，
    // onChunk 里「按 \n 分成多条气泡」的逻辑就永远收不到分隔符（分条失效 + 句子粘连）。
    clean = clean.replace(/[ \t]{2,}/g, " ").replace(/^[ \t]+|[ \t]+$/g, "");
    return { motions, clean };
  }

  // ───────────────────────── 关键变量状态（带持久化） ─────────────────────────
  // 这些就是「最常调整的参数」：温度（创意度）、情绪灵敏度、打字速度、数字人缩放、主题、显隐。
  const STEP = { temperature: 0.05, emotion_threshold: 0.05, typing_speed: 1, zoom: 0.1 };
  const RANGE = {
    temperature: [0, 1.5],
    emotion_threshold: [0, 1],
    typing_speed: [1, 10],
    zoom: [0.5, 2.0],
  };
  const DEFAULT_STATE = {
    temperature: 0.85,
    emotion_threshold: 0.30,
    typing_speed: 5,
    zoom: 1.0,
    model_visible: true,
    theme: "dark",
    model_id: "314701", // 当前加载的 Live2D 模型
    model_offset: { x: 0, y: 0 }, // 用户拖拽偏移（持久化）
  };

  function loadState() {
    try {
      const raw = localStorage.getItem("roleplay_ui_state");
      if (raw) {
        const parsed = JSON.parse(raw);
        const merged = Object.assign({}, DEFAULT_STATE, parsed);
        // 类型校正：防止 localStorage 被旧版本/手改写入字符串等非数值类型，
        // 导致 renderHUD() 里 state.temperature.toFixed() 抛 TypeError、首屏崩溃。
        // 对每个数值型字段：非法值回退 DEFAULT_STATE 对应值。
        const NUMERIC_KEYS = ["temperature", "emotion_threshold", "typing_speed", "zoom"];
        NUMERIC_KEYS.forEach((k) => {
          const v = merged[k];
          if (typeof v !== "number" || !isFinite(v)) merged[k] = DEFAULT_STATE[k];
        });
        // 对象字段同样校验：model_offset 非 {x,y} 数值对象、model_id 非字符串时
        // 若直接使用会在 renderHUD()（fmt("position")）抛 TypeError，
        // 并连带跳过 loadCharacters/restoreHistory/initLive2D 整个首屏初始化链。
        const off = merged.model_offset;
        if (
          !off || typeof off !== "object" || Array.isArray(off) ||
          !isFinite(Number(off.x)) || !isFinite(Number(off.y))
        ) {
          merged.model_offset = Object.assign({}, DEFAULT_STATE.model_offset);
        } else {
          merged.model_offset = { x: Number(off.x), y: Number(off.y) };
        }
        if (typeof merged.model_id !== "string" || !merged.model_id) {
          merged.model_id = DEFAULT_STATE.model_id;
        }
        return merged;
      }
    } catch (_) {}
    return Object.assign({}, DEFAULT_STATE);
  }
  function saveState() {
    try { localStorage.setItem("roleplay_ui_state", JSON.stringify(state)); } catch (_) {}
  }
  const state = loadState();

  // 单条回复最多拆成几个气泡。角色对话一般 2-4 条，给到 6 留余量；
  // 超出的换行不再拆气泡（代码块/长列表会刷屏），改由 pre-wrap 原样呈现。
  const MAX_BUBBLES_PER_REPLY = 6;

  // ───────────────────────── DOM 引用 ─────────────────────────
  const messagesEl = document.getElementById("messages");

  // 滚动跟随：只有用户仍贴着底部（距底 <80px）时才自动滚动。
  // 否则流式生成期间用户向上翻看历史会被强行拽回底部。发送新消息时重置为跟随。
  // 注意：#messages 仅聊天页存在（宠物页 PET_MODE 没有该元素），
  // 必须判空挂载——此前无条件 addEventListener 会在宠物页抛 TypeError，
  // 中断整个 IIFE，window.RoleplayChat 永不暴露，宠物对话全链路失效。
  state._following = true;
  if (messagesEl) {
    messagesEl.addEventListener(
      "scroll",
      () => {
        const distance =
          messagesEl.scrollHeight - messagesEl.scrollTop - messagesEl.clientHeight;
        state._following = distance < 80;
      },
      { passive: true }
    );
  }

  const inputEl = document.getElementById("message-input");
  const sendBtn = document.getElementById("send-btn");
  const loadingEl = document.getElementById("live2d-loading");
  const toastEl = document.getElementById("toasts");
  const helpBackdrop = document.getElementById("help-backdrop");
  const hud = {
    temp: document.getElementById("hud-temp"),
    sens: document.getElementById("hud-sens"),
    speed: document.getElementById("hud-speed"),
    zoom: document.getElementById("hud-zoom"),
    model: document.getElementById("hud-model"),
    theme: document.getElementById("hud-theme"),
    modelName: document.getElementById("hud-model-name"),
    pos: document.getElementById("hud-pos"),
    llm: document.getElementById("hud-llm"),
  };

  // 情绪事件通常先于首个文本分片到达；先暂存，待气泡就绪时补挂芯片，
  // 避免被后续 textContent 覆盖（修复：芯片不显示 + 被清空的问题）
  let pendingEmotion = null;

  // ───────────────────────── 视觉反馈：Toast + HUD 闪烁 ─────────────────────────
  function toast(icon, label, value) {
    const t = document.createElement("div");
    t.className = "toast";
    // 全部用 textContent 拼接，避免任何注入（icon/label/value 即便将来传入用户文本也安全）
    const iconSpan = document.createElement("span");
    iconSpan.className = "t-icon";
    iconSpan.textContent = icon;
    const labelSpan = document.createElement("span");
    labelSpan.textContent = label;
    t.appendChild(iconSpan);
    t.appendChild(labelSpan);
    if (value != null) {
      const valSpan = document.createElement("span");
      valSpan.className = "t-val";
      valSpan.textContent = value;
      t.appendChild(valSpan);
    }
    toastEl.appendChild(t);
    // 动画结束后移除（toast-out 1.5s 后）
    setTimeout(() => t.remove(), 1900);
  }

  function flashHud(key) {
    const el = hud[key];
    if (!el) return;
    const chip = el.closest(".hud-chip");
    if (!chip) return;
    chip.classList.add("flash");
    setTimeout(() => chip.classList.remove("flash"), 420);
  }

  function fmt(key) {
    switch (key) {
      case "temperature": return state.temperature.toFixed(2);
      case "emotion_threshold": return state.emotion_threshold.toFixed(2);
      case "typing_speed": return state.typing_speed + "×";
      case "zoom": return Math.round(state.zoom * 100) + "%";
      case "model_visible": return state.model_visible ? "显示" : "隐藏";
      case "theme": return state.theme === "dark" ? "暗" : "亮";
      case "model_name": {
        const ms = (window.RoleplayLive2D && window.RoleplayLive2D.getModels()) || [];
        const cur = ms.find((m) => m.id === state.model_id) || {};
        return cur.name || state.model_id;
      }
      case "position":
        return (state.model_offset.x === 0 && state.model_offset.y === 0) ? "居中" : "自定义";
      default: return "";
    }
  }

  function renderHUD() {
    hud.temp.textContent = fmt("temperature");
    hud.sens.textContent = fmt("emotion_threshold");
    hud.speed.textContent = fmt("typing_speed");
    hud.zoom.textContent = fmt("zoom");
    hud.model.textContent = fmt("model_visible");
    hud.theme.textContent = fmt("theme");
    if (hud.modelName) hud.modelName.textContent = fmt("model_name");
    if (hud.pos) hud.pos.textContent = fmt("position");
    // LLM 当前生效模型（本地 Ollama ↔ 云端），由 llm-switch.js 提供
    if (hud.llm && window.RoleplayLLM) hud.llm.textContent = window.RoleplayLLM.getDisplayName();
  }

  // ───────────────────────── 状态变更（含副作用下发到 Live2D / 主题） ─────────────────────────
  function applyValue(key, announce) {
    renderHUD();
    flashHud(key);
    if (key === "zoom") window.RoleplayLive2D && window.RoleplayLive2D.setZoom(state.zoom);
    if (key === "model_visible") window.RoleplayLive2D && window.RoleplayLive2D.setVisible(state.model_visible);
    if (key === "emotion_threshold") window.RoleplayLive2D && window.RoleplayLive2D.setEmotionThreshold(state.emotion_threshold);
    if (key === "theme") document.body.dataset.theme = state.theme;
    saveState();
    if (announce) toast(announce.icon, announce.label, announce.value);
  }

  function adjust(key, dir) {
    const step = STEP[key] || 1;
    let v = (state[key] != null ? state[key] : 0) + dir * step;
    const [lo, hi] = RANGE[key] || [-Infinity, Infinity];
    // 浮点容差，避免 0.85+0.05 累积误差
    v = Math.round(v / step) * step;
    v = Math.max(lo, Math.min(hi, v));
    state[key] = v;
    const meta = {
      temperature: { icon: dir > 0 ? "🌡️▲" : "🌡️▼", label: "温度", value: fmt("temperature") },
      emotion_threshold: { icon: dir > 0 ? "💡▲" : "💡▼", label: "情绪灵敏度", value: fmt("emotion_threshold") },
      typing_speed: { icon: dir > 0 ? "⚡▲" : "⚡▼", label: "打字速度", value: fmt("typing_speed") },
      zoom: { icon: dir > 0 ? "🔍▲" : "🔍▼", label: "缩放", value: fmt("zoom") },
    }[key];
    applyValue(key, meta);
  }

  function toggleModel() {
    state.model_visible = !state.model_visible;
    applyValue("model_visible", {
      icon: state.model_visible ? "🧍" : "🚫",
      label: "数字人",
      value: fmt("model_visible"),
    });
  }

  function toggleTheme() {
    state.theme = state.theme === "dark" ? "light" : "dark";
    const icon = document.getElementById("btn-theme-icon");
    if (icon) icon.textContent = state.theme === "dark" ? "暗" : "亮";
    applyValue("theme", {
      icon: state.theme === "dark" ? "暗" : "亮",
      label: "主题",
      value: fmt("theme"),
    });
  }

  // ───────────────────────── 模型切换（314701 / 314702 …） ─────────────────────────
  // 切换代际号：快速连按 1/2 时，慢的旧请求后完成会覆盖用户最后意图，只认最后一次。
  let modelSwitchGen = 0;
  async function switchModel(id) {
    const ms = (window.RoleplayLive2D && window.RoleplayLive2D.getModels()) || [];
    const cur = ms.find((m) => m.id === String(id));
    if (!cur) return;
    const gen = ++modelSwitchGen;
    const ok = await window.RoleplayLive2D.switchModel(cur.id);
    if (gen !== modelSwitchGen) return; // 期间又有新切换请求，本次结果作废
    if (!ok) {
      toast("⚠️", "切换失败", cur.name);
      return;
    }
    // 成功：state.model_id / HUD / tabs 统一由 live2d:model-changed 事件刷新，
    // 此处不再提前写 state，避免切换失败时记录到未能加载的模型。
    toast("🔄", "已切换到", cur.name);
  }

  // 高亮当前模型对应的 tab
  function updateModelTabs() {
    const tabs = document.querySelectorAll(".model-tab");
    tabs.forEach((t) => {
      const sel = t.getAttribute("data-model") === state.model_id;
      t.setAttribute("aria-selected", sel ? "true" : "false");
      t.classList.toggle("active", sel);
    });
  }

  // ───────────────────────── 重置模型位置（F / Shift+R / 双击 / 按钮） ─────────────────────────
  function resetModelPos() {
    state.model_offset = { x: 0, y: 0 };
    saveState();
    if (window.RoleplayLive2D) window.RoleplayLive2D.resetPosition();
    renderHUD();
    toast("📍", "位置已重置", "居中");
  }

  // ───────────────────────── 快捷键帮助弹层 ─────────────────────────
  // 弹层竞态（F9）：close 用 200ms 延迟隐藏，若期间重新 open，旧定时器会把新弹层藏掉。
  let helpCloseTimer = null;
  function openHelp() {
    if (helpCloseTimer) { clearTimeout(helpCloseTimer); helpCloseTimer = null; }
    helpBackdrop.hidden = false;
    // 强制回流后加 open 类以触发过渡
    void helpBackdrop.offsetWidth;
    helpBackdrop.classList.add("open");
  }
  function closeHelp() {
    helpBackdrop.classList.remove("open");
    if (helpCloseTimer) clearTimeout(helpCloseTimer);
    helpCloseTimer = setTimeout(() => { helpCloseTimer = null; helpBackdrop.hidden = true; }, 200);
  }
  function toggleHelp() {
    if (helpBackdrop.classList.contains("open")) closeHelp();
    else openHelp();
  }

  // ───────────────────────── 清空记忆（复用为顶部按钮 + 快捷键） ─────────────────────────
  async function clearMemory() {
    const sid = getSessionId();
    try {
      await fetch(API_BASE + "/chat/clear", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sid }),
      });
    } catch (_) {}
    try { localStorage.removeItem("roleplay_session_id"); } catch (_) {}
    // 先收束打字机：否则旧 tick 会继续向已脱离 DOM 的节点写文本并抢滚动
    hideTyping();
    messagesEl.innerHTML = "";
    appendBubble("assistant", WELCOME);
    toast("🧹", "已清空记忆");
  }

  // ───────────────────────── 聊天气泡 / 流式渲染 ─────────────────────────
  function appendBubble(role, text) {
    const bubble = document.createElement("div");
    bubble.className = "bubble " + role;
    const span = document.createElement("span");
    span.className = "bubble-text";
    span.textContent = text || "";
    bubble.appendChild(span);
    messagesEl.appendChild(bubble);
    messagesEl.scrollTop = messagesEl.scrollHeight;
    return { bubble, span };
  }

  function appendEmotionChip(bubble, emotion) {
    const chip = document.createElement("span");
    // 按父类分组着色；未知 emotion 兜底显示原文（不崩）
    const group = EMOTION_GROUP[emotion] || emotion;
    chip.className = "emotion-chip " + (GROUP_CLASS[group] || "");
    chip.textContent = EMOTION_CN[emotion] || emotion;
    bubble.appendChild(chip);
  }

  function renderFollowUps(bubble, followUps) {
    const wrap = document.createElement("div");
    wrap.className = "follow-ups";
    followUps.forEach((text) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "suggestion-chip";
      btn.textContent = text;
      btn.addEventListener("click", () => {
        inputEl.value = text;
        sendMessage();
      });
      wrap.appendChild(btn);
    });
    bubble.appendChild(wrap);
  }

  function showTyping() {
    const wrap = document.createElement("div");
    wrap.className = "bubble assistant";
    wrap.id = "__typing";
    wrap.innerHTML = '<span class="typing"><span></span><span></span><span></span></span>';
    messagesEl.appendChild(wrap);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }
  let activeTyper = null; // 当前打字机实例（错误/失败路径需显式 stop，防 interval 空转）
  function hideTyping() {
    if (activeTyper && typeof activeTyper.stop === "function") activeTyper.stop();
    activeTyper = null;
    const t = document.getElementById("__typing");
    if (t) t.remove();
  }

  /**
   * 打字机式逐字显现：后端推送的整段目标文本，按当前「打字速度」逐字刷新。
   * 这样「打字速度」变量才有真实体感（而非一次性吐出）。
   */
  function makeTyper(span) {
    let full = "";
    let shown = 0;
    let timer = null;
    const stepN = () => Math.max(1, Math.round(state.typing_speed));
    function tick() {
      if (shown < full.length) {
        shown = Math.min(full.length, shown + stepN());
        span.textContent = full.slice(0, shown);
        // 仅在用户仍贴着底部时才跟随滚动，否则生成期间无法回看历史。
        // 之前是无条件 scrollTop，长回复流式期间会把用户强行拽回底部。
        if (shown < full.length && state._following) {
          messagesEl.scrollTop = messagesEl.scrollHeight;
        }
      }
      if (shown >= full.length) { clearInterval(timer); timer = null; }
    }
    return {
      push(text) {
        full += text;
        if (!timer) timer = setInterval(tick, 18);
      },
      stop() {
        if (timer) { clearInterval(timer); timer = null; }
        if (shown < full.length) { shown = full.length; span.textContent = full; }
      },
      /** 当前这条是否已收到内容（用于换行分条时跳过空气泡） */
      hasContent() {
        return full.length > 0;
      },
    };
  }

  async function initLive2D() {
    try {
      if (window.RoleplayLive2D) {
        const ms = window.RoleplayLive2D.getModels();
        const cur = ms.find((m) => m.id === state.model_id) || ms[0];
        await window.RoleplayLive2D.init({
          containerId: "live2d-canvas",
          modelUrl: cur.url,
          mapUrl: "./assets/live2d/emotion_map.json",
        });
        // 首屏把当前 UI 状态同步给数字人（缩放/显隐/灵敏度/拖拽偏移）
        window.RoleplayLive2D.setEmotionThreshold(state.emotion_threshold);
        window.RoleplayLive2D.setZoom(state.zoom);
        window.RoleplayLive2D.setVisible(state.model_visible);
        window.RoleplayLive2D.setOffset(state.model_offset.x, state.model_offset.y);
        updateModelTabs();
      }
    } catch (e) {
      console.warn("[chat] Live2D 初始化异常", e);
    } finally {
      if (loadingEl) loadingEl.classList.add("hidden");
    }
  }

  // ───────────────────────── 共享对话核心（index.html 与 pet.html 共用） ─────────────────────────
  /**
   * 发起一次 SSE 流式对话（POST /chat/stream）。
   * opts：
   *   temperature / useWeb / sessionId / llmOverride（请求级覆盖，与全局一致时可省略）
   *   buildBody(body)  - 发送前最后改写请求体的机会
   *   onStart()        - 请求发出前
   *   onFirstChunk()   - 收到首个 chunk（AI 回复才真正开始）
   *   onChunk(text)    - 增量文本（已剥离 {动作：xx} 指令）
   *   onMotion(names)  - 文本中的动作指令数组
   *   onEmotion(d)     - emotion 事件（{emotion, score}）
   *   onDone(payload)  - done 事件（follow_ups 等）
   *   onError(detail)  - SSE error 事件（detail 为可读错误）
   *   onComplete(fullReply, sawChunk) - 流正常结束
   *   onFail(message)  - 网络/HTTP 失败
   * 返回 { fullReply, sawChunk }。
   */
  async function streamChat(text, opts) {
    opts = opts || {};
    const bodyObj = {
      session_id: opts.sessionId || getSessionId(),
      message: text,
      temperature: opts.temperature != null ? opts.temperature : state.temperature,
      use_web: opts.useWeb != null ? opts.useWeb : !!(webToggle && webToggle.checked),
    };
    if (opts.llmOverride) {
      bodyObj.llm = opts.llmOverride;
    } else if (window.RoleplayLLM) {
      const llmOverride = window.RoleplayLLM.buildOverride();
      if (llmOverride) bodyObj.llm = llmOverride;
    }
    if (opts.buildBody) opts.buildBody(bodyObj);

    if (opts.onStart) opts.onStart();
    let fullReply = "";
    let sawChunk = false;
    let firstChunkFired = false;
    // 超时/中止保护（F2）：后端任一环节挂起（连接建立后不再发数据）时，
    // 若无兜底，读取循环永不结束 → 发送按钮永久禁用、typing 气泡永驻。
    // 空闲超时（60s 无任何数据）与总超时（120s）双保险，命中即 abort 走 onFail。
    const controller = new AbortController();
    const IDLE_MS = 60 * 1000;
    const TOTAL_MS = 120 * 1000;
    let idleTimer = null;
    const armIdle = () => {
      if (idleTimer) clearTimeout(idleTimer);
      idleTimer = setTimeout(() => controller.abort("idle-timeout"), IDLE_MS);
    };
    armIdle();
    const totalTimer = setTimeout(() => controller.abort("total-timeout"), TOTAL_MS);
    try {
      const resp = await fetch(API_BASE + "/chat/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(bodyObj),
        signal: controller.signal,
      });
      if (!resp.ok) {
        // 尝试读取后端统一错误结构 {error:{message}}，给用户可读的错误原因
        let detail = "HTTP " + resp.status;
        try {
          const errJson = await resp.json();
          const err = errJson && errJson.error;
          if (err && err.message) detail = err.message;
          else if (errJson && errJson.detail) detail = errJson.detail;
        } catch (_) { /* 非 JSON 错误体，保留 HTTP 状态 */ }
        throw new Error(detail);
      }

      const reader = resp.body.getReader();
      const decoder = new TextDecoder();
      let buf = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        if (value && value.byteLength) armIdle(); // 收到数据即刷新空闲计时
        buf += decoder.decode(value, { stream: true });
        const blocks = buf.split("\n\n");
        buf = blocks.pop();
        for (const block of blocks) {
          let dataLine = null;
          // event 是块级状态：每块解析前重置，避免「某块只含 data: 无 event:」时
          // 沿用上一块的 event 名被误解析（如把 emotion 数据当 chunk 吞掉）
          let event = "";
          for (const line of block.split("\n")) {
            if (line.startsWith("event:")) event = line.slice(6).trim();
            else if (line.startsWith("data:")) dataLine = line.slice(5).trim();
          }
          if (!dataLine) continue;
          if (event === "chunk") {
            sawChunk = true;
            if (!firstChunkFired) {
              firstChunkFired = true;
              if (opts.onFirstChunk) opts.onFirstChunk();
            }
            let piece;
            try {
              piece = JSON.parse(dataLine);
            } catch (e) {
              // 畸形 chunk（网络截断/服务端异常）：跳过不中断整条流
              console.warn("[chat] 畸形 chunk 跳过:", dataLine.slice(0, 80));
              continue;
            }
            // 解析 {动作：xxx} 指令：从显示文本中剥离并触发对应 Live2D 动作
            const parsed = parseActionCommands(piece);
            if (parsed.motions.length && opts.onMotion) opts.onMotion(parsed.motions);
            if (opts.onChunk) opts.onChunk(parsed.clean);
            fullReply += parsed.clean;
          } else if (event === "emotion") {
            let d;
            try {
              d = JSON.parse(dataLine);
            } catch (e) {
              console.warn("[chat] 畸形 emotion 跳过:", dataLine.slice(0, 80));
              continue;
            }
            if (opts.onEmotion) opts.onEmotion(d);
          } else if (event === "done") {
            let payload;
            try {
              payload = JSON.parse(dataLine);
            } catch (e) {
              payload = null;
            }
            if (opts.onDone) opts.onDone(payload);
          } else if (event === "error") {
            // 后端 SSE 中途异常（LLM 调用失败等）：显示具体错误而非永久卡在「生成中」
            let payload;
            try {
              payload = JSON.parse(dataLine);
            } catch (e) {
              payload = null;
            }
            if (payload && opts.onError) opts.onError(payload.detail || "生成失败，请稍后重试");
          }
        }
      }
      if (opts.onComplete) opts.onComplete(fullReply, sawChunk);
    } catch (e) {
      // AbortError：映射为可读的超时/取消提示，保证 UI 一定能恢复（按钮/typing）
      if (e && e.name === "AbortError") {
        if (opts.onFail) opts.onFail("响应超时，请重试（生成时间过长或服务无响应）");
      } else if (opts.onFail) {
        opts.onFail(e && e.message ? e.message : String(e));
      }
    } finally {
      if (idleTimer) clearTimeout(idleTimer);
      clearTimeout(totalTimer);
    }
    return { fullReply, sawChunk };
  }

  // 对外 API（桌面宠物页 pet.js 等复用同一套对话逻辑）
  window.RoleplayChat = {
    send: (text, opts) => streamChat(text, opts),
    getSessionId,
  };

  async function sendMessage() {
    const text = inputEl.value.trim();
    if (!text || sendBtn.disabled) return;
    inputEl.value = "";
    appendBubble("user", text);
    showTyping();
    sendBtn.disabled = true;
    pendingEmotion = null;
    // 新一轮开始：恢复底部跟随（上一轮若手动上滚过，这里重新贴底），并清掉中止标记
    state._following = true;
    state._aborted = false;
    state._bubbleCount = 1; // 首个气泡由 onFirstChunk 创建

    // 用户发言即时触发一个手势（如「谢谢」→ 点头），让角色反应更鲜活
    const gesture = detectGesture(text);
    if (gesture && window.RoleplayLive2D) window.RoleplayLive2D.playGesture(gesture);
    // 通知 live2d：用户产生互动（退出空闲睡眠态、刷新空闲计时）
    if (window.RoleplayLive2D) window.RoleplayLive2D.notifyUserInteract();

    let aiBubble = null;
    let typer = null;

    await streamChat(text, {
      onFirstChunk() {
        hideTyping();
        aiBubble = appendBubble("assistant", "");
        typer = makeTyper(aiBubble.span);
        activeTyper = typer; // 登记当前打字机，供 onError/onFail/兜底清理时 stop
        // 气泡就绪后补挂此前到达的情绪芯片
        if (pendingEmotion) {
          appendEmotionChip(aiBubble.bubble, pendingEmotion.emotion);
          pendingEmotion = null;
        }
      },
      onMotion(names) {
        names.forEach((m) => {
          if (window.RoleplayLive2D) window.RoleplayLive2D.playGesture(m, 3);
        });
      },
      onChunk(clean) {
        if (!typer) return;
        // 换行 = 换一条：角色按「一条一行」输出多条短回复，这里逐条开新气泡，
        // 还原真人连发几条消息的观感（而非挤在一个气泡里的一段长文）。
        //
        // 上限保护：代码块/列表类回答可能有几十个换行，逐个拆气泡会刷屏
        // （实测一段 Python 快排是 20 行）。超过上限后保留换行但不拆气泡，
        // 由 .bubble 的 white-space:pre-wrap 原样呈现。
        const parts = String(clean).split("\n");
        for (let i = 0; i < parts.length; i++) {
          if (i > 0) {
            // 当前条为空说明是连续换行/行首换行，跳过，避免产生空气泡
            if (!typer.hasContent()) continue;
            if (state._bubbleCount >= MAX_BUBBLES_PER_REPLY) {
              // 已达上限：不再开新气泡，把换行与内容一起塞回当前条（pre-wrap 渲染）。
              // 换行必须无条件保留：独立 chunk 就是 "\n" 时 parts=["",""]，
              // 若按"末尾空 part"跳过，换行会丢失、代码行粘连（换行与内容在不同
              // chunk 时无法在单 chunk 内判断它是不是真正的结尾）。
              // 由此可能多出的尾部空行，在 onComplete 统一裁掉。
              typer.push("\n");
              if (parts[i]) typer.push(parts[i]);
              continue;
            }
            typer.stop();
            aiBubble = appendBubble("assistant", "");
            typer = makeTyper(aiBubble.span);
            activeTyper = typer; // 重新登记，供 onError/onFail 清理
            state._bubbleCount++;
          }
          if (parts[i]) typer.push(parts[i]);
        }
      },
      onEmotion(d) {
        // 情绪标签：气泡未就绪则暂存，就绪时补挂
        if (aiBubble) {
          appendEmotionChip(aiBubble.bubble, d.emotion);
        } else {
          pendingEmotion = d;
        }
        // 驱动数字人（阈值受快捷键「情绪灵敏度」控制）
        if (window.RoleplayLive2D) window.RoleplayLive2D.onEmotionEvent(d);
      },
      onDone(payload) {
        const followUps = (payload && payload.follow_ups) || [];
        if (followUps.length && aiBubble) {
          renderFollowUps(aiBubble.bubble, followUps);
        }
      },
      onError(detail) {
        // 标记中止：error 事件不中断读循环，EOF 后仍会走到 onComplete，
        // 若不拦住，自动朗读会把这条被中断的半截回复念出来。
        state._aborted = true;
        if (typer && typeof typer.stop === "function") typer.stop();
        typer = null;
        hideTyping();
        appendBubble("assistant", "⚠️ " + detail);
      },
      onComplete(fullReply, sawChunk) {
        // 流结束必须收束打字机：否则积压的 tick 会跨轮次继续抢滚动
        if (activeTyper && typeof activeTyper.stop === "function") activeTyper.stop();
        activeTyper = null;
        typer = null;
        // 裁掉尾部空行：分条时为保证换行不丢失是无条件 push 的，
        // 回复若以换行结尾会让气泡底部多一条空行（pre-wrap 下可见）。
        if (aiBubble && aiBubble.span) {
          aiBubble.span.textContent = aiBubble.span.textContent.replace(/\s+$/, "");
        }
        // 流式已结束；若开启自动朗读，调用语音模块播放完整 AI 回复
        if (fullReply && !state._aborted && window.RoleplayVoice) {
          const vs = window.RoleplayVoice.getSettings();
          if (vs.auto_tts && vs.voice_enabled) {
            window.RoleplayVoice.speak(fullReply, {});
          }
        }
        // typing 残留清理：若后端仅返回 emotion+done（空回复）或直接 EOF，
        // hideTyping 不会在 chunk/error/catch 任何分支被调用，需在此兜底
        if (!sawChunk) hideTyping();
      },
      onFail(message) {
        state._aborted = true;
        if (activeTyper && typeof activeTyper.stop === "function") activeTyper.stop();
        activeTyper = null;
        typer = null;
        hideTyping();
        appendBubble("assistant", "（连接失败：" + message + "）");
      },
    });
    sendBtn.disabled = false;
    inputEl.focus();
  }

  // ───────────────────────── 事件绑定（仅聊天页；宠物页无此 DOM） ─────────────────────────
  if (!PET_MODE) {
  sendBtn.addEventListener("click", sendMessage);
  inputEl.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey && !e.ctrlKey && !e.metaKey) sendMessage();
  });

  // 顶部按钮
  const btnHelp = document.getElementById("btn-help");
  const btnTheme = document.getElementById("btn-theme");
  const btnClear = document.getElementById("btn-clear");
  const clearBtn = document.getElementById("clear-btn");
  const helpClose = document.getElementById("help-close");
  if (btnHelp) btnHelp.addEventListener("click", toggleHelp);
  if (btnTheme) btnTheme.addEventListener("click", toggleTheme);
  if (btnClear) btnClear.addEventListener("click", clearMemory);
  if (clearBtn) clearBtn.addEventListener("click", clearMemory);
  if (helpClose) helpClose.addEventListener("click", closeHelp);
  if (helpBackdrop) helpBackdrop.addEventListener("click", (e) => {
    if (e.target === helpBackdrop) closeHelp();
  });

  // 模型切换 tabs（放在 stage-overlay，带 pointer-events:auto）
  document.querySelectorAll(".model-tab").forEach((t) => {
    t.addEventListener("click", () => switchModel(t.getAttribute("data-model")));
  });
  const resetPosBtn = document.getElementById("reset-pos-btn");
  if (resetPosBtn) resetPosBtn.addEventListener("click", resetModelPos);

  // ── Live2D 反向事件：拖拽 / 切换后把状态同步回前端（持久化 + HUD） ──
  window.addEventListener("live2d:offset", (e) => {
    const d = (e && e.detail) || {};
    state.model_offset = { x: Number(d.x) || 0, y: Number(d.y) || 0 };
    saveState();
    renderHUD();
  });
  window.addEventListener("live2d:model-changed", (e) => {
    const d = (e && e.detail) || {};
    if (d.id) state.model_id = d.id;
    saveState();
    renderHUD();
    updateModelTabs();
  });

  // ── 点击交换（区域互动）：live2d.js 命中头/身/下摆区域后广播，
  //    这里负责显示气泡台词 + 原声/TTS（用户主动点击优先，天然打断当前朗读）。
  //    原声触发已统一上移到 live2d.js 的 _handleClick（emitIntent("click")，
  //    不受区域冷却影响）；这里只判断"原声刚接管"则跳过 TTS 电子音兜底。
  //    台词统一以 pet-voice 的字幕为准（pet:voice-line 注入），气泡与字幕天然一致；
  //    原声被拒/失败时退回 canned bubble+TTS，避免"点了没反应"。 ──
  let _lastClickVoiceAt = 0;   // 最近一次「用户点击 → 原声起播」时间，用于 live2d:interact 去重
  window.addEventListener("pet:voice-line", (e) => {
    const d = (e && e.detail) || {};
    // 仅「用户主动点击」(slot=click) 注入气泡：happy/sad 等姿态槽由聊天驱动，注入会刷屏
    if (!d || d.slot !== "click") return;
    const sub = d.subtitle
      || (d.clip && { zh: d.clip.text || "", en: d.clip.text || "" })
      || null;
    if (!sub) return;
    const pv = window.RoleplayPetVoice;
    const lang = (pv && pv.getLang && pv.getLang()) || "zh";
    const text = sub[lang] || sub.zh || sub.en || "";
    if (!text || typeof appendBubble !== "function") return;
    _lastClickVoiceAt = Date.now();
    appendBubble("assistant", text);
  });
  window.addEventListener("live2d:interact", (e) => {
    const d = (e && e.detail) || {};
    const pv = window.RoleplayPetVoice;
    const st = pv && pv.getState ? pv.getState() : null;
    // 原声正在接管发声（loading/playing）→ 跳过 canned bubble+TTS，避免音画不一致
    const voiceJustTook =
      !!(st && (st.phase === "playing" || st.phase === "loading"))
      || (Date.now() - _lastClickVoiceAt < 1500);
    if (!voiceJustTook && d.text) appendBubble("assistant", d.text);
    if (!voiceJustTook && d.tts && window.RoleplayVoice) {
      const vs = window.RoleplayVoice.getSettings();
      if (vs.voice_enabled) {
        window.RoleplayVoice.speak(d.tts, {});
      }
    }
  });

  // ───────────────────────── 键盘快捷键（单键 + 组合键） ─────────────────────────
  document.addEventListener("keydown", (e) => {
    const inInput = e.target === inputEl;
    const mod = e.ctrlKey || e.metaKey;

    // Ctrl/⌘+K：聚焦输入框（即使正在打字也生效，业界通用「聚焦/命令」快捷键）
    if (mod && !e.shiftKey && (e.key === "k" || e.key === "K")) {
      e.preventDefault();
      inputEl.focus();
      return;
    }
    // Ctrl/⌘+Enter：发送（聊天软件通用）
    if (mod && e.key === "Enter") {
      e.preventDefault();
      sendMessage();
      return;
    }
    // Esc：关闭弹层（模型 > 人设 > 帮助）；否则若正在输入则取消焦点
    if (e.key === "Escape") {
      if (window.RoleplayLLM && window.RoleplayLLM.isOpen()) { window.RoleplayLLM.close(); return; }
      if (charBackdrop && charBackdrop.classList.contains("open")) { closeCharPanel(); return; }
      if (helpBackdrop && helpBackdrop.classList.contains("open")) { closeHelp(); return; }
      if (inInput) { inputEl.blur(); return; }
    }

    // 以下快捷键在输入框聚焦时一律忽略，避免打断用户打字（最佳实践的「输入态豁免」）
    if (inInput) return;

    // 修饰键守卫：Ctrl/⌘ 组合已在上方处理完（K/Enter），剩余单键一律不响应组合键——
    // 否则 Ctrl+C（复制）会触发 case "c" 清空对话记忆（数据破坏），
    // Ctrl+F/T/1/2/= 还会劫持浏览器原生快捷键。
    if (mod) return;

    // 组合键：Alt+方向键 微调数值（系统音量/亮度、Figma 微移的同类惯例）
    if (e.altKey) {
      if (!e.shiftKey) {
        switch (e.key) {
          case "ArrowUp": adjust("temperature", +1); e.preventDefault(); return;
          case "ArrowDown": adjust("temperature", -1); e.preventDefault(); return;
          case "ArrowLeft": adjust("emotion_threshold", -1); e.preventDefault(); return;
          case "ArrowRight": adjust("emotion_threshold", +1); e.preventDefault(); return;
        }
      } else {
        switch (e.key) {
          case "ArrowUp": adjust("typing_speed", +1); e.preventDefault(); return;
          case "ArrowDown": adjust("typing_speed", -1); e.preventDefault(); return;
          case "ArrowLeft": adjust("zoom", -1); e.preventDefault(); return;
          case "ArrowRight": adjust("zoom", +1); e.preventDefault(); return;
        }
      }
      return;
    }

    // 单键操作：数值 − / + 与状态切换
    switch (e.key) {
      case "-": case "_": adjust("temperature", -1); return;
      case "=": case "+": adjust("temperature", +1); return;
      case "[": adjust("emotion_threshold", -1); return;
      case "]": adjust("emotion_threshold", +1); return;
      case ",": case "<": adjust("typing_speed", -1); return;
      case ".": case ">": adjust("typing_speed", +1); return;
      case "(": adjust("zoom", -1); return;
      case ")": adjust("zoom", +1); return;
      case "1": switchModel("314701"); return;
      case "2": switchModel("314702"); return;
      case "f": case "F": resetModelPos(); return;
      case "r": case "R": if (e.shiftKey) { resetModelPos(); return; } break;
      case "m": case "M": toggleModel(); return;
      case "t": case "T": toggleTheme(); return;
      case "c": case "C": clearMemory(); return;
      case "h": case "H": case "?": toggleHelp(); return;
    }
  });
  } // end if (!PET_MODE) 事件绑定

  // ───────────────────────── 角色人设管理 + 联网 + 历史恢复 ─────────────────────────
  const charBackdrop = document.getElementById("char-backdrop");
  const charListEl = document.getElementById("char-list");
  const charForm = document.getElementById("char-form");
  const charFormTitle = document.getElementById("char-form-title");
  const charFormErr = document.getElementById("char-form-err");
  const charNewBtn = document.getElementById("char-new");
  const charSaveBtn = document.getElementById("char-save");
  const charCancelBtn = document.getElementById("char-cancel");
  const charWebBtn = document.getElementById("char-web");
  const charClose = document.getElementById("char-close");
  const webToggle = document.getElementById("web-toggle");
  const webWrap = document.getElementById("web-toggle-wrap");

  const charState = { active_id: null, characters: [], editingId: null };

  async function apiJSON(url, opts) {
    const resp = await fetch(url, opts);
    if (!resp.ok) {
      // 解析后端统一错误结构 {error:{message}}，避免裸 HTTP 状态码
      let detail = "HTTP " + resp.status;
      try {
        const errJson = await resp.json();
        const err = errJson && errJson.error;
        if (err && err.message) detail = err.message;
        else if (errJson && errJson.detail) detail = errJson.detail;
      } catch (_) { /* 非 JSON 错误体，保留 HTTP 状态 */ }
      throw new Error(detail);
    }
    return resp.json();
  }

  let charCloseTimer = null;
  function openCharPanel() {
    if (charCloseTimer) { clearTimeout(charCloseTimer); charCloseTimer = null; }
    charBackdrop.hidden = false;
    void charBackdrop.offsetWidth;
    charBackdrop.classList.add("open");
    loadCharacters();
  }
  function closeCharPanel() {
    charBackdrop.classList.remove("open");
    if (charCloseTimer) clearTimeout(charCloseTimer);
    charCloseTimer = setTimeout(() => { charCloseTimer = null; charBackdrop.hidden = true; }, 200);
    charForm.hidden = true;
  }
  function toggleCharPanel() {
    if (charBackdrop.classList.contains("open")) closeCharPanel();
    else openCharPanel();
  }

  async function loadCharacters() {
    try {
      const data = await apiJSON(API_BASE + "/api/characters");
      charState.characters = data.characters || [];
      charState.active_id = data.active_id || null;
      renderCharList();
      await refreshActiveCharacter();
    } catch (e) {
      toast("⚠️", "人设加载失败", e.message);
    }
  }

  function renderCharList() {
    charListEl.innerHTML = "";
    if (!charState.characters.length) {
      const empty = document.createElement("div");
      empty.className = "c-desc";
      empty.textContent = "暂无角色，点「新建角色」创建一个吧。";
      charListEl.appendChild(empty);
      return;
    }
    charState.characters.forEach((c) => {
      const row = document.createElement("div");
      row.className = "char-row";
      const name = document.createElement("span");
      name.className = "c-name";
      name.textContent = c.name;
      const desc = document.createElement("span");
      desc.className = "c-desc";
      desc.textContent = c.description || "";
      row.appendChild(name);
      row.appendChild(desc);
      if (c.active) {
        const badge = document.createElement("span");
        badge.className = "c-active";
        badge.textContent = "当前";
        row.appendChild(badge);
      }
      const switchBtn = document.createElement("button");
      switchBtn.textContent = c.active ? "使用中" : "切换";
      switchBtn.disabled = c.active;
      switchBtn.addEventListener("click", () => activateCharacter(c.id));
      row.appendChild(switchBtn);
      const editBtn = document.createElement("button");
      editBtn.textContent = "编辑";
      editBtn.addEventListener("click", () => openCharForm(c.id));
      row.appendChild(editBtn);
      const delBtn = document.createElement("button");
      delBtn.className = "danger";
      delBtn.textContent = "删除";
      delBtn.addEventListener("click", () => deleteCharacter(c.id));
      row.appendChild(delBtn);
      charListEl.appendChild(row);
    });
  }

  async function refreshActiveCharacter() {
    try {
      const data = await apiJSON(API_BASE + "/api/characters/active");
      const name = data.name || "无名者";
      const chatName = document.getElementById("chat-name");
      const avatar = document.getElementById("chat-avatar");
      const stageName = document.getElementById("stage-name");
      if (chatName) chatName.textContent = name;
      if (avatar) avatar.textContent = (name || "无").slice(0, 1);
      if (stageName) stageName.textContent = name;
    } catch (_) {}
  }

  function openCharForm(id) {
    charState.editingId = id || null;
    charFormErr.textContent = "";
    if (id) {
      charFormTitle.textContent = "编辑角色";
      apiJSON(API_BASE + "/api/characters/" + id)
        .then((d) => fillForm(d.card || {}))
        .catch(() => fillForm({}));
    } else {
      charFormTitle.textContent = "新建角色";
      fillForm({});
    }
    charForm.hidden = false;
  }
  function fillForm(card) {
    document.getElementById("f-name").value = card.name || "";
    document.getElementById("f-description").value = card.description || "";
    document.getElementById("f-personality").value = card.personality || "";
    document.getElementById("f-background").value = card.background || "";
    document.getElementById("f-behavior_rules").value = card.behavior_rules || "";
    // P0-2 锚点：数组 ↔ 每行一条
    document.getElementById("f-core_anchors").value = Array.isArray(card.core_anchors)
      ? card.core_anchors.join("\n") : "";
    // P0-3 策略表：对象 ↔ 每行 "标签: 策略"
    document.getElementById("f-emotion_strategies").value =
      card.emotion_strategies && typeof card.emotion_strategies === "object"
        ? Object.keys(card.emotion_strategies)
            .map((k) => k + ": " + card.emotion_strategies[k])
            .join("\n")
        : "";
    // P1-3 情感层次：对象 ↔ JSON 文本（留空表示不启用）
    const layers = card.emotional_layers;
    document.getElementById("f-emotional_layers").value =
      layers && typeof layers === "object" && Object.keys(layers).length
        ? JSON.stringify(layers, null, 2)
        : "";
    document.getElementById("f-scenario").value = card.scenario || "";
    document.getElementById("f-tone").value = card.tone || "";
    document.getElementById("f-first_mes").value = card.first_mes || "";
    document.getElementById("f-mes_example").value = card.mes_example || "";
    document.getElementById("f-system_prompt").value = card.system_prompt || "";
  }
  // P0-2：核心锚点文本域 → 数组（每行一条，空行丢弃；清空 → [] 表示"清掉该字段"）
  function readAnchors() {
    return document
      .getElementById("f-core_anchors")
      .value.split("\n")
      .map((s) => s.trim())
      .filter(Boolean);
  }
  // P0-3：策略表文本域 → 对象（每行 "标签: 策略"；无冒号的行忽略，标签小写归一）
  function readEmotionStrategies() {
    const out = {};
    document
      .getElementById("f-emotion_strategies")
      .value.split("\n")
      .forEach((ln) => {
        const i = ln.indexOf(":");
        if (i <= 0) return;
        const k = ln.slice(0, i).trim().toLowerCase();
        const v = ln.slice(i + 1).trim();
        if (k && v) out[k] = v;
      });
    return out;
  }
  // P1-3：情感层次 JSON 文本域 → 对象。
  // 留空 → null（不覆盖该字段）；内容非法 → 抛出，由 saveCharacter 拦下提示。
  function readEmotionalLayers() {
    const raw = document.getElementById("f-emotional_layers").value.trim();
    if (!raw) return null;
    let parsed;
    try {
      parsed = JSON.parse(raw);
    } catch (e) {
      throw new Error("情感节奏 / 防备层不是合法 JSON");
    }
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
      throw new Error("情感节奏 / 防备层必须是 JSON 对象");
    }
    return parsed;
  }
  function readForm() {
    return {
      name: document.getElementById("f-name").value.trim(),
      description: document.getElementById("f-description").value.trim(),
      personality: document.getElementById("f-personality").value.trim(),
      background: document.getElementById("f-background").value.trim(),
      behavior_rules: document.getElementById("f-behavior_rules").value.trim(),
      core_anchors: readAnchors(),
      emotion_strategies: readEmotionStrategies(),
      emotional_layers: readEmotionalLayers(),
      scenario: document.getElementById("f-scenario").value.trim(),
      tone: document.getElementById("f-tone").value.trim(),
      first_mes: document.getElementById("f-first_mes").value.trim(),
      mes_example: document.getElementById("f-mes_example").value.trim(),
      system_prompt: document.getElementById("f-system_prompt").value.trim() || null,
    };
  }
  async function saveCharacter() {
    let payload;
    try {
      payload = readForm();
    } catch (e) {
      charFormErr.textContent = (e && e.message) || "表单内容有误";
      return;
    }
    if (!payload.name) { charFormErr.textContent = "名称不能为空"; return; }
    try {
      if (charState.editingId) {
        await apiJSON(API_BASE + "/api/characters/" + charState.editingId, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        toast("✅", "已更新", payload.name);
      } else {
        const d = await apiJSON(API_BASE + "/api/characters", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        toast("✅", "已新建", payload.name);
        if (d.id) await activateCharacter(d.id, true);
      }
      charForm.hidden = true;
      await loadCharacters();
    } catch (e) {
      charFormErr.textContent = "保存失败：" + e.message;
    }
  }
  async function activateCharacter(id, silent) {
    try {
      await apiJSON(API_BASE + "/api/characters/" + id + "/activate", { method: "POST" });
      charState.active_id = id;
      await refreshActiveCharacter();
      await loadCharacters();
      if (!silent) toast("🔄", "已切换角色", "");
    } catch (e) {
      toast("⚠️", "切换失败", e.message);
    }
  }
  async function deleteCharacter(id) {
    if (!window.confirm("确定删除该角色？此操作不可撤销。")) return;
    try {
      await apiJSON(API_BASE + "/api/characters/" + id, { method: "DELETE" });
      toast("🗑️", "已删除角色");
      await loadCharacters();
    } catch (e) {
      toast("⚠️", "删除失败", e.message);
    }
  }
  async function webIngest() {
    const q = window.prompt("联网检索并入知识库，输入查询词：", "");
    if (!q || !q.trim()) return;
    try {
      const d = await apiJSON(API_BASE + "/api/knowledge/web-ingest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: q.trim(), max_results: 5 }),
      });
      toast("🌐", "联网入库", (d.stored || 0) + " 段 / " + (d.sources || []).length + " 源");
    } catch (e) {
      toast("⚠️", "联网失败", e.message);
    }
  }

  const btnCharacters = document.getElementById("btn-characters");
  if (btnCharacters) btnCharacters.addEventListener("click", toggleCharPanel);
  if (charClose) charClose.addEventListener("click", closeCharPanel);
  if (charBackdrop) charBackdrop.addEventListener("click", (e) => {
    if (e.target === charBackdrop) closeCharPanel();
  });
  if (charNewBtn) charNewBtn.addEventListener("click", () => openCharForm(null));
  if (charSaveBtn) charSaveBtn.addEventListener("click", saveCharacter);
  if (charCancelBtn) charCancelBtn.addEventListener("click", () => { charForm.hidden = true; });
  if (charWebBtn) charWebBtn.addEventListener("click", webIngest);

  function syncWebToggle() {
    if (webToggle && webWrap) webWrap.classList.toggle("on", !!webToggle.checked);
  }
  if (webToggle) webToggle.addEventListener("change", syncWebToggle);

  // 历史恢复：会话中断/重启后无缝恢复上下文显示
  async function restoreHistory() {
    const sid = getSessionId();
    try {
      const data = await apiJSON(API_BASE + "/api/sessions/" + encodeURIComponent(sid) + "/history");
      const hist = (data && data.history) || [];
      if (hist.length) {
        // 竞态守卫：await 期间用户可能已发送首条消息（appendBubble 已挂到 messagesEl）。
        // 此时不能再清空重建，否则用户刚发的消息会从界面消失（后端已收到）。
        // 已存在新气泡时跳过历史渲染（后端上下文不受影响，刷新即可见完整历史）。
        if (messagesEl.childElementCount === 0) {
          messagesEl.innerHTML = "";
          hist.forEach((m) => appendBubble(m.role === "user" ? "user" : "assistant", m.content || ""));
        }
        return;
      }
    } catch (_) {}
    if (messagesEl.childElementCount === 0) {
      appendBubble("assistant", WELCOME);
    }
  }

  // ───────────────────────── 首屏初始化（仅聊天页） ─────────────────────────
  if (!PET_MODE) {
  document.body.dataset.theme = state.theme;
  const themeIcon = document.getElementById("btn-theme-icon");
  if (themeIcon) themeIcon.textContent = state.theme === "dark" ? "暗" : "亮";
  renderHUD();
  loadCharacters();   // 拉取角色列表 + 激活角色名（顶栏/头像即时反映）
  restoreHistory();   // 会话中断/重启后无缝恢复上下文显示
  initLive2D();

  // 模型切换模块（本地 Ollama ↔ 云端）：初始化后拉取全局配置并刷新 HUD；
  // 用户在弹层保存/恢复默认时同步刷新 HUD 与顶栏按钮文本。
  if (window.RoleplayLLM) {
    window.RoleplayLLM.onChanged(() => {
      renderHUD();
      const llmBtnName = document.getElementById("btn-llm-name");
      if (llmBtnName) llmBtnName.textContent = window.RoleplayLLM.getDisplayName();
    });
    window.RoleplayLLM.init();
  }
  } // end if (!PET_MODE) 首屏初始化
})();
