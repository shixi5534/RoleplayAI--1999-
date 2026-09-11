/*
 * pet.js —— 桌面宠物页逻辑（P0：强制 Spine-only；P1：暗色高对比；P2：非穿透点击范式）
 *
 * 定位：桌面宠物是网页版的附属形态。本文件只做「拼装」——
 *   Spine 渲染/待机调度/点击互动/情绪表情  → 复用 window.RoleplaySpine（spine.js）
 *   动作库与意图事件                        → 复用 window.RoleplayPetCore（shared/pet-core.js）
 *   对话 SSE 核心                            → 复用 window.RoleplayChat（chat.js，宠物模式仅暴露 API）
 *   语音 输入/输出                            → 复用 window.RoleplayVoice（voice.js）
 *   Electron 窗口能力（hover/移动/快捷键/截图）→ 经 preload 注入的 window.petApi
 *
 * petApi 不存在（普通浏览器打开本页）时自动降级为「网页内嵌预览模式」。
 */
(function () {
  "use strict";

  const api = window.petApi || null; // Electron preload 注入；浏览器下为 null

  // ───────────────────────── 状态与持久化 ─────────────────────────
  const DEFAULT_STATE = {
    zoom: 1.0,
    muted: false,
    browser_seen: false,
    onboarded: false, // P0-3：首次启动引导气泡是否已播放
    renderer: "spine", // P0：渲染器锁定为 spine（仅保留字段兼容历史 localStorage）
    spine_model: "314701_s", // P1.1：当前骨骼动画模型（314701_s / 314701 / 314702）
    bubble_size: 1.0, // 气泡/弹窗大小倍率（0.75–1.6）
    dnd: false, // P1-3：勿扰（正交修饰态）
    locked: false, // P1-4：锁位（正交修饰态）
    dnd_auto_release: true, // 勿扰 30 分钟后自动解除
    voice_enabled: true, // 宠物侧语音开关（写回 roleplay_voice_state 共享）
    voice_speed: 1.0,
    voice_volume: 100,
    // P1：对话（桌面宠物强制本地 Ollama，不调用任何远程 API）
    ollama_model: "qwen2.5:1.5b",
    ollama_base_url: "http://127.0.0.1:11434/v1",
    temperature: 0.85,
    auto_tts: true,
  };
  function loadState() {
    const s = Object.assign({}, DEFAULT_STATE);
    try {
      const raw = localStorage.getItem("roleplay_pet_state");
      if (raw) Object.assign(s, JSON.parse(raw));
    } catch (_) {}
    return s;
  }
  function saveState() {
    try { localStorage.setItem("roleplay_pet_state", JSON.stringify(state)); } catch (_) {}
  }
  const state = loadState();

  // ── P0 启动迁移：清除历史持久化的 Live2D 渲染器选择，强制 Spine-only ──
  if (state.renderer !== "spine") {
    state.renderer = "spine";
    saveState();
  }
  if ("model_id" in state) {
    delete state.model_id; // Live2D 模型选择字段已废弃，清理历史残留
    saveState();
  }
  // P1.1：校验持久化的骨骼模型 id，失效时回退默认。
  const spineModels =
    window.RoleplaySpine && typeof window.RoleplaySpine.getModels === "function"
      ? window.RoleplaySpine.getModels()
      : [];
  if (!spineModels.length || !spineModels.some((m) => m.id === state.spine_model)) {
    state.spine_model = DEFAULT_STATE.spine_model;
    saveState();
  }

  // ───────────────────────── DOM ─────────────────────────
  const $ = (id) => document.getElementById(id);
  // 注意：宠物页的舞台容器是 #pet-canvas，Spine 画布动态挂载到该容器内。
  const canvasEl = $("pet-canvas");
  const bubbleEl = $("pet-bubble");
  const menuEl = $("pet-menu");
  const settingsEl = $("pet-settings");
  const inputBarEl = $("pet-inputbar");
  const inputEl = $("pet-input");
  const hintEl = $("browser-hint");
  const chips = { backend: $("chip-backend"), ollama: $("chip-ollama"), mic: $("chip-mic") };

  let bubbleTimer = null;
  let bubbleSticky = false;
  let chatBusy = false; // 对话进行中（流式/思考），期间不重复发起

  // 点击反馈台词池（P2 起可与 LLM 闲话合并）
  const CLICK_LINES = [
    "嗯？怎么了。",
    "我在。",
    "…有事说事。",
    "别戳。",
    "嗯。",
    "说吧，我在听。",
  ];
  // 「说话」菜单的随机开场（轻量，避免每次打 Ollama）
  const TALK_STARTERS = [
    "你在忙什么？",
    "陪我说说话吧。",
    "今天过得怎么样？",
    "有什么想聊的吗？",
  ];

  // 用户发言关键词 → 手势（与 chat.js detectGesture 同思路的轻量版）
  const GESTURES = [
    ["谢谢", "b_diantou"], ["感谢", "b_diantou"], ["再见", "b_shanzi"], ["晚安", "b_shanzi"],
    ["你好", "b_taishou"], ["在吗", "b_taishou"], ["开心", "t_weixiao"], ["难过", "t_nanguo"],
    ["生气", "b_yaotou"], ["为什么", "t_yihuo"], ["什么", "t_yihuo"], ["怎么", "t_yihuo"],
  ];
  function detectGesture(text) {
    for (const [kw, motion] of GESTURES) {
      if (String(text || "").indexOf(kw) !== -1) return motion;
    }
    return null;
  }

  // ───────────────────────── 气泡 ─────────────────────────
  // 打字机：流式 chunk 进入队列，逐字揭示（18ms/字），流结束 flush
  let typeQueue = "";
  let typeTimer = null;
  let caretEl = null;
  const bubbleTextEl = $("pet-bubble-text");
  // 气泡历史（P2-3：最近 20 条，↑/↓ 翻页）
  const BUBBLE_HISTORY = [];
  let bubbleHistIdx = -1;

  function ensureCaret() {
    if (caretEl && caretEl.parentElement) return caretEl;
    caretEl = document.createElement("span");
    caretEl.className = "caret";
    caretEl.textContent = "▍";
    bubbleTextEl.appendChild(caretEl);
    return caretEl;
  }
  function removeCaret() {
    if (caretEl && caretEl.parentElement) caretEl.parentElement.removeChild(caretEl);
    caretEl = null;
  }
  function tickType() {
    if (!typeQueue) { typeTimer = null; return; }
    const step = Math.min(2, typeQueue.length);
    const piece = typeQueue.slice(0, step);
    typeQueue = typeQueue.slice(step);
    // 光标前插入（caret 若在末尾会自动跟随）
    if (caretEl && caretEl.parentElement) {
      caretEl.before(document.createTextNode(piece));
    } else {
      bubbleTextEl.appendChild(document.createTextNode(piece));
    }
    schedulePositionBubble(); // 气泡随内容长高，节流重判顶部/翻转态
    typeTimer = setTimeout(tickType, 18);
  }
  function flushType() {
    if (typeTimer) { clearTimeout(typeTimer); typeTimer = null; }
    if (typeQueue) {
      bubbleTextEl.appendChild(document.createTextNode(typeQueue));
      typeQueue = "";
    }
  }

  function setBubbleText(text) {
    flushType();
    removeCaret();
    bubbleTextEl.textContent = text || "";
  }
  function showBubble(text, opts) {
    opts = opts || {};
    setBubbleText(text);
    bubbleEl.classList.remove("flipped");
    bubbleEl.classList.remove("done");
    bubbleEl.classList.add("show");
    bubbleSticky = !!opts.sticky;
    if (bubbleTimer) { clearTimeout(bubbleTimer); bubbleTimer = null; }
    if (!bubbleSticky) {
      const ms = Math.max(3000, Math.min(9000, 2200 + String(text || "").length * 90));
      bubbleTimer = setTimeout(hideBubble, ms);
    }
    positionBubble(); // 内容定形后立即决定顶部/翻转态，避免盖住模型头
    pushModelBounds(); // 气泡显示时并入可点击区，避免 setShape 把它裁掉
  }
  function appendBubbleText(text) {
    // 流式打字机：进队列逐字揭示 + 光标闪烁
    if (!bubbleEl.classList.contains("show")) bubbleEl.classList.add("show");
    ensureCaret();
    typeQueue += text;
    if (!typeTimer) tickType();
  }
  function finishBubble(fullText) {
    // 流结束：flush 余量、移除光标、入历史、显示操作行、转非粘性自动收起
    flushType();
    removeCaret();
    bubbleSticky = false;
    bubbleEl.classList.add("done");
    positionBubble(); // 操作行加入后高度定型，重判顶部/翻转态
    if (fullText) {
      BUBBLE_HISTORY.push(fullText);
      if (BUBBLE_HISTORY.length > 20) BUBBLE_HISTORY.shift();
    }
    bubbleHistIdx = BUBBLE_HISTORY.length;
    if (bubbleTimer) { clearTimeout(bubbleTimer); bubbleTimer = null; }
    const ms = Math.max(3000, Math.min(9000, 2200 + String(fullText || "").length * 90));
    bubbleTimer = setTimeout(hideBubble, ms);
  }
  function hideBubble() {
    flushType();
    removeCaret();
    bubbleEl.classList.remove("show");
    bubbleEl.classList.remove("flipped");
    bubbleEl.style.top = ""; // 清掉翻转定位，回到 CSS 默认顶部态
    bubbleSticky = false;
    if (bubbleTimer) { clearTimeout(bubbleTimer); bubbleTimer = null; }
    pushModelBounds();
  }

  // ── 气泡智能定位：按模型 bbox 决定顶部/翻转态（完成设计稿 .flipped 态的接线） ──
  // 默认态：贴窗口顶居中，小尾巴指向模型头顶。注意当前舞台是脚底锚定
  // （spine._fit 落地线 = 窗高 −16px），模型下方几乎没有空间，所以头部顶进
  // 气泡区时通常维持顶部叠放（面板不透明，可读性优先）；翻转分支是给未来
  // 舞台几何（加大落地间距 / 非底部锚定）预留的安全路径，平时不触发。
  const BUBBLE_GAP = 10;        // 气泡与模型的呼吸间隙
  const BUBBLE_MIN_BELOW = 90;  // 翻转到下方所需的最小可视高度，不足则维持顶部叠放
  function positionBubble() {
    if (!bubbleEl.classList.contains("show")) return;
    const spine = window.RoleplaySpine;
    const sb = spine && spine.ready && typeof spine.getShapeBounds === "function"
      ? spine.getShapeBounds()
      : null;
    if (!sb || !(sb.height > 0)) {
      bubbleEl.style.top = "";
      bubbleEl.classList.remove("flipped");
      return;
    }
    void bubbleEl.offsetWidth;
    const bh = bubbleEl.offsetHeight;
    const roomAbove = sb.top - BUBBLE_GAP - bh;
    if (roomAbove >= 8) {
      bubbleEl.style.top = "";
      bubbleEl.classList.remove("flipped");
      return;
    }
    const feetY = sb.top + sb.height;
    const flipTop = feetY + BUBBLE_GAP;
    const hasRoomBelow = window.innerHeight - flipTop >= Math.min(bh, BUBBLE_MIN_BELOW);
    if (hasRoomBelow && feetY < window.innerHeight) {
      bubbleEl.style.top = flipTop + "px";
      bubbleEl.classList.add("flipped");
    } else {
      bubbleEl.style.top = "";
      bubbleEl.classList.remove("flipped");
    }
  }
  let bubblePosTimer = null;
  /** 打字机流式期间节流重定位（150ms），避免逐字符触发强制布局。 */
  function schedulePositionBubble() {
    if (bubblePosTimer) return;
    bubblePosTimer = setTimeout(() => {
      bubblePosTimer = null;
      positionBubble();
    }, 150);
  }
  bubbleEl.addEventListener("click", (e) => {
    if (e.target.closest(".bubble-actions")) return; // 操作行按钮不触发整体关闭
    hideBubble();
  });

  // 气泡操作行（P2-3）
  $("pet-bubble-actions").addEventListener("click", (e) => {
    const btn = e.target.closest("button[data-bact]");
    if (!btn) return;
    const act = btn.dataset.bact;
    const text = bubbleTextEl.textContent || "";
    if (act === "close") {
      hideBubble();
    } else if (act === "copy") {
      navigator.clipboard.writeText(text).then(() => petToast("已复制")).catch(() => petToast("复制失败"));
    } else if (act === "speak") {
      speakReply(text);
    } else if (act === "prev" && BUBBLE_HISTORY.length) {
      if (bubbleHistIdx > 0) bubbleHistIdx--;
      showBubble(BUBBLE_HISTORY[bubbleHistIdx] || text, { sticky: true });
      bubbleEl.classList.add("done");
      schedulePositionBubble(); // 历史文本长度不同，操作行展开后重判定位
    } else if (act === "next" && BUBBLE_HISTORY.length) {
      if (bubbleHistIdx < BUBBLE_HISTORY.length - 1) bubbleHistIdx++;
      showBubble(BUBBLE_HISTORY[bubbleHistIdx] || text, { sticky: true });
      bubbleEl.classList.add("done");
      schedulePositionBubble(); // 历史文本长度不同，操作行展开后重判定位
    }
  });
  // ↑/↓ 气泡历史翻页（P2-3；非输入态）
  document.addEventListener("keydown", (e) => {
    if (!bubbleEl.classList.contains("show")) return;
    const t = e.target;
    if (t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.tagName === "SELECT")) return;
    if (e.key === "ArrowUp" && BUBBLE_HISTORY.length) {
      e.preventDefault();
      if (bubbleHistIdx > 0) bubbleHistIdx--;
      showBubble(BUBBLE_HISTORY[bubbleHistIdx], { sticky: true });
      bubbleEl.classList.add("done");
      schedulePositionBubble(); // 同上：↑/↓ 翻页后内容高度变化重判定位
    } else if (e.key === "ArrowDown" && BUBBLE_HISTORY.length) {
      e.preventDefault();
      if (bubbleHistIdx < BUBBLE_HISTORY.length - 1) bubbleHistIdx++;
      showBubble(BUBBLE_HISTORY[bubbleHistIdx], { sticky: true });
      bubbleEl.classList.add("done");
      schedulePositionBubble(); // 同上：↑/↓ 翻页后内容高度变化重判定位
    }
  });

  // ───────────────────────── 渲染器初始化（P0：Spine 唯一渲染器） ─────────────────────────
  let renderer = null; // 当前渲染器实例：RoleplaySpine

  async function initRenderer() {
    // P0：永远 Spine，不提供 Live2D 回落分支。
    return initSpine();
  }

  async function initSpine() {
    try {
      if (!window.RoleplaySpine) return false;
      const model =
        (typeof window.RoleplaySpine.getModelById === "function" && window.RoleplaySpine.getModelById(state.spine_model)) ||
        (typeof window.RoleplaySpine.getModels === "function" && window.RoleplaySpine.getModels()[0]) ||
        {
          id: DEFAULT_STATE.spine_model,
          skelUrl: "./assets/spine/314701_wmz_s_room.skel",
          atlasUrl: "./assets/spine/314701_wmz_s.atlas",
          animationMapUrl: "./assets/spine/animation_map.json",
          expressionMapUrl: "./assets/spine/expression_map.json",
        };
      const ok = await window.RoleplaySpine.init({
        containerId: "pet-canvas",
        modelId: model.id,
        skelUrl: model.skelUrl,
        atlasUrl: model.atlasUrl,
        animationMapUrl: model.animationMapUrl,
        expressionMapUrl: model.expressionMapUrl,
      });
      if (ok) {
        renderer = window.RoleplaySpine;
        state.spine_model = model.id;
        saveState();
        window.RoleplaySpine.setZoom(state.zoom);
        window.RoleplaySpine.enter(); // 入场动画
        applySpineMenuLabel();
        pushModelBounds(); // 首次就绪后立即把真实模型 bbox 同步给主进程做点击穿透
      }
      return ok;
    } catch (e) {
      console.warn("[pet] Spine 初始化异常", e);
      return false;
    }
  }

  // ───────────────────────── P1.1：骨骼动画模型切换 ─────────────────────────
  function getSpineModels() {
    return window.RoleplaySpine && typeof window.RoleplaySpine.getModels === "function"
      ? window.RoleplaySpine.getModels()
      : [];
  }
  function getSpineModel() {
    return window.RoleplaySpine && typeof window.RoleplaySpine.getModelById === "function"
      ? window.RoleplaySpine.getModelById(state.spine_model)
      : null;
  }
  function applySpineMenuLabel() {
    const el = $("menu-spine-label");
    if (!el) return;
    const m = getSpineModel();
    el.textContent = m ? m.name : "骨骼动画";
  }

  /** 收集当前可见且可交互的 UI 包围盒，与模型 bbox 合并后作为窗口可点击区域。 */
  function collectUiRects() {
    const rects = [];
    const add = (el) => {
      if (!el) return;
      void el.offsetWidth; // 强制 reflow，确保刚 open 的菜单/抽屉能拿到真实尺寸
      const r = el.getBoundingClientRect();
      if (r && isFinite(r.left) && isFinite(r.top) && r.width > 0 && r.height > 0) {
        rects.push({ left: r.left, top: r.top, width: r.width, height: r.height });
      }
    };
    try {
      if (bubbleEl && bubbleEl.classList.contains("show")) add(bubbleEl);
      if (menuEl && menuEl.classList.contains("open")) add(menuEl);
      if (settingsEl && settingsEl.classList.contains("open")) add(settingsEl);
      if (inputBarEl && inputBarEl.classList.contains("open")) add(inputBarEl);
      if (onbEl && onbEl.classList.contains("open")) add(onbEl);
      const uiVisible = document.body.classList.contains("ui-visible") || document.body.classList.contains("pet-ui");
      if (uiVisible) {
        if (foldBtn && foldBtn.classList.contains("show")) add(foldBtn);
        const statusEl = $("pet-status");
        if (statusEl && statusEl.classList.contains("show")) add(statusEl);
      }
    } catch (_) {}
    return rects;
  }

  /** 把模型包络盒 + 可见 UI 包围盒同步给主进程：setShape 只用包络盒（永不裁到
   *  模型像素）；alpha 矩形仅作为 hover 精确命中数据（主进程不得用它裁渲染）。 */
  function pushModelBounds() {
    if (!api || typeof api.updateModelBounds !== "function") return;
    if (!window.RoleplaySpine || !window.RoleplaySpine.ready) return; // 模型未就绪不发默认 bbox，避免误裁剪 fallback
    try {
      // 优先使用像素级 alpha 矩形：hover 判定更精准（bbox 内的透明孔洞不算命中）
      const alphaRects = window.RoleplaySpine && typeof window.RoleplaySpine.getAlphaRects === "function"
        ? window.RoleplaySpine.getAlphaRects()
        : null;
      // setShape 必须用全动画包络盒：它覆盖模型任何姿态，不存在逐帧滞后裁剪
      const env = window.RoleplaySpine && typeof window.RoleplaySpine.getEnvelopeBounds === "function"
        ? window.RoleplaySpine.getEnvelopeBounds()
        : null;
      const b = env || (window.RoleplaySpine && typeof window.RoleplaySpine.getShapeBounds === "function"
          ? window.RoleplaySpine.getShapeBounds()
          : (window.RoleplaySpine && typeof window.RoleplaySpine.getBounds === "function"
              ? window.RoleplaySpine.getBounds()
              : null));
      const payload = { ui: collectUiRects() };
      if (alphaRects && alphaRects.length) {
        payload.modelRects = alphaRects;
      }
      if (b && isFinite(b.left) && isFinite(b.top) && isFinite(b.width) && isFinite(b.height)) {
        payload.model = { left: b.left, top: b.top, width: b.width, height: b.height };
      }
      if (payload.model) {
        api.updateModelBounds(payload);
      }
    } catch (_) {}
  }
  let spineSwitchBusy = false;
  let spineSwitchPending = null;
  async function stabilizeWindowSize() {
    // 切换骨骼后按桌面端配置把窗口尺寸钉回当前档位，防止渲染器重建期间窗口尺寸漂移。
    if (!api || typeof api.getConfig !== "function" || typeof api.setSize !== "function") return;
    try {
      const cfg = await api.getConfig();
      if (cfg && cfg.pet && cfg.pet.width && cfg.pet.height) {
        api.setSize(cfg.pet.width, cfg.pet.height);
      }
    } catch (_) {}
  }
  async function switchSpineModel(modelId) {
    const model =
      window.RoleplaySpine &&
      typeof window.RoleplaySpine.getModelById === "function" &&
      window.RoleplaySpine.getModelById(modelId);
    if (!model) return false;
    if (state.spine_model === model.id && renderer === window.RoleplaySpine && window.RoleplaySpine.ready) {
      showBubble("已经是：" + model.name);
      return true;
    }
    // 防止右键连点导致多个 init 并发：切换期间新请求只记录“最后一个目标”，
    // 当前切换完成后再补一次，避免重叠的 SpineCanvas 造成动画错乱。
    if (spineSwitchBusy) {
      spineSwitchPending = model.id;
      showBubble("正在切换，稍候…");
      return false;
    }
    spineSwitchBusy = true;
    try {
      // 切换 = 销毁旧上下文 → 用新 skel/atlas 重新初始化（避免双 WebGL 并存）。
      if (renderer && typeof renderer.destroy === "function") {
        try { renderer.destroy(); } catch (_) {}
      }
      renderer = null;
      state.spine_model = model.id;
      saveState();
      noteActivity();
      if (api) api.notifyInteract();
      showBubble("切换骨骼：" + model.name + " …", { sticky: true });
      let ok = await initSpine();
      if (ok) {
        await stabilizeWindowSize();
        pushModelBounds(); // 切换后同步新模型 bbox，避免点击热区仍停留在旧模型
        showBubble("已切换：" + model.name);
        if (window.RoleplayPetCore) window.RoleplayPetCore.emitIntent("menu", { act: "spine", modelId: model.id });
        return true;
      }
      // 加载失败回退默认模型，避免把宠物留在空白状态。
      showBubble("⚠️ 骨骼动画加载失败，已回退默认：" + model.name);
      state.spine_model = DEFAULT_STATE.spine_model;
      saveState();
      ok = await initSpine();
      if (ok) {
        await stabilizeWindowSize();
        pushModelBounds();
        showBubble("已回退：" + getSpineModel().name);
      }
      return ok;
    } finally {
      spineSwitchBusy = false;
      if (spineSwitchPending && spineSwitchPending !== model.id) {
        const pending = spineSwitchPending;
        spineSwitchPending = null;
        switchSpineModel(pending); // 补切到连点最后选中的模型
      } else {
        spineSwitchPending = null;
      }
    }
  }
  function cycleSpineModel() {
    const models = getSpineModels();
    if (!models.length) return;
    const idx = models.findIndex((m) => m.id === state.spine_model);
    const next = models[(idx + 1) % models.length] || models[0];
    switchSpineModel(next.id);
  }

  // ───────────────────────── 模型/气泡大小调节 ─────────────────────────
  function changeZoom(delta) {
    const next = Math.max(0.5, Math.min(2.0, Math.round((state.zoom + delta) * 100) / 100));
    state.zoom = next;
    saveState();
    if (window.RoleplaySpine && typeof window.RoleplaySpine.setZoom === "function") {
      window.RoleplaySpine.setZoom(next);
    }
    pushModelBounds(); // 缩放后同步命中包围盒，避免点击热区与视觉大小脱节
    petToast("模型大小 " + Math.round(next * 100) + "%");
    if (window.RoleplayPetCore) window.RoleplayPetCore.emitIntent("menu", { act: "zoom", zoom: next });
  }
  function changeBubbleSize(delta) {
    const next = Math.max(0.75, Math.min(1.6, Math.round((state.bubble_size + delta) * 100) / 100));
    state.bubble_size = next;
    saveState();
    applyBubbleSize();
    petToast("气泡大小 " + Math.round(next * 100) + "%");
    if (window.RoleplayPetCore) window.RoleplayPetCore.emitIntent("menu", { act: "bubble-size", bubbleSize: next });
  }
  function applyBubbleSize() {
    const scale = Math.max(0.75, Math.min(1.6, Number(state.bubble_size) || 1));
    document.body.style.setProperty("--bubble-scale", String(scale));
    if (bubbleEl.classList.contains("show")) positionBubble(); // 缩放改变高度后重判翻转态
    const el = $("menu-bubble-label");
    if (el) el.textContent = Math.round(scale * 100) + "%";
  }

  // ───────────────────────── 主进程漫步状态（Spine target* 行走，方向镜像） ─────────────────────────
  if (api && typeof api.onWalk === "function") {
    api.onWalk((d) => {
      if (!d || !window.RoleplaySpine) return;
      if (d.phase === "start") {
        window.RoleplaySpine.walk((d.dx || 0) >= 0 ? "right" : "left");
        if (window.RoleplayPetCore) window.RoleplayPetCore.emitIntent("walk", d);
      } else {
        window.RoleplaySpine.stopWalk();
      }
    });
  }

  // ───────────────────────── 拖拽/点击（AHaldner delta 范式 + PetAI 非穿透） ─────────────────────────
  // pointerdown/up 位移 <5px 判点击 → RoleplaySpine.click()；否则用 screen 坐标增量经 api.moveBy 跟随窗口。
  // P2/R5：按钮/浮层命中时直接 return，避免拖拽吞掉控件点击。
  const NO_DRAG_SELECTOR =
    "button, input, select, textarea, a, #pet-bubble, #pet-menu, #pet-settings, #pet-inputbar, #pet-onboarding, #pet-input-fold, .chip";
  let spineDrag = null; // { pointerId, startScreenX, startScreenY, lastScreenX, lastScreenY, moved, busySet, lockWarned }

  function dragTarget(e) {
    const t = e && e.target;
    if (t && typeof t.closest === "function" && t.closest(NO_DRAG_SELECTOR)) return false;
    return !!(canvasEl && t && (t === canvasEl || canvasEl.contains(t)));
  }

  document.addEventListener("pointerdown", (e) => {
    if (e.button !== 0 || !dragTarget(e)) return;
    const sx = typeof e.screenX === "number" ? e.screenX : e.clientX;
    const sy = typeof e.screenY === "number" ? e.screenY : e.clientY;
    spineDrag = {
      pointerId: e.pointerId,
      startScreenX: sx,
      startScreenY: sy,
      lastScreenX: sx,
      lastScreenY: sy,
      moved: false,
      busySet: false,
      lockWarned: false,
    };
    document.body.classList.add("dragging");
    if (canvasEl && typeof canvasEl.setPointerCapture === "function") {
      try { canvasEl.setPointerCapture(e.pointerId); } catch (_) {}
    }
  });
  document.addEventListener("pointermove", (e) => {
    if (!spineDrag || e.pointerId !== spineDrag.pointerId) return;
    const sx = typeof e.screenX === "number" ? e.screenX : e.clientX;
    const sy = typeof e.screenY === "number" ? e.screenY : e.clientY;
    const dx = sx - spineDrag.lastScreenX;
    const dy = sy - spineDrag.lastScreenY;
    spineDrag.lastScreenX = sx;
    spineDrag.lastScreenY = sy;
    if (Math.hypot(sx - spineDrag.startScreenX, sy - spineDrag.startScreenY) > 5) {
      if (!spineDrag.moved) {
        spineDrag.moved = true;
        if (window.RoleplayPetCore) window.RoleplayPetCore.emitIntent("drag", { phase: "start" });
      }
      noteActivity(); // 拖拽即互动
      if (state.locked) {
        // 锁位：拖拽尝试 → 摇头反馈 + 提示（主进程 moveBy 亦守卫）
        if (!spineDrag.lockWarned) {
          spineDrag.lockWarned = true;
          if (window.RoleplaySpine) window.RoleplaySpine.click();
          petToast("已锁定，长按 1.5s 解锁");
        }
        return;
      }
      if (api) {
        // busy 只置位一次（主进程按引用计数暂停漫步，重复 true 会泄漏计数）
        if (!spineDrag.busySet) {
          spineDrag.busySet = true;
          api.setBusy(true);
        }
        api.notifyInteract();
        if (typeof api.moveBy === "function") api.moveBy(dx, dy);
      }
      if (window.RoleplayPetCore) window.RoleplayPetCore.emitIntent("drag", { phase: "move", dx, dy });
    }
  });
  document.addEventListener("pointerup", (e) => {
    if (!spineDrag || e.pointerId !== spineDrag.pointerId) return;
    const wasDrag = spineDrag.moved;
    const upX = typeof e.clientX === "number" ? e.clientX : 0;
    const upY = typeof e.clientY === "number" ? e.clientY : 0;
    spineDrag = null;
    document.body.classList.remove("dragging");
    if (canvasEl && typeof canvasEl.releasePointerCapture === "function" && typeof e.pointerId === "number") {
      try { canvasEl.releasePointerCapture(e.pointerId); } catch (_) {}
    }
    if (wasDrag) {
      if (api) {
        api.setBusy(false);
        if (typeof api.dragEnd === "function") api.dragEnd(); // 主进程动量/回弹
      }
      if (window.RoleplayPetCore) window.RoleplayPetCore.emitIntent("drag", { phase: "end" });
    } else {
      // 单击：命中反馈 + Spine 互动 + 台词气泡
      noteActivity(); // 点击即互动
      flashUi(3200);
      pulseModel();
      spawnFeedback(upX, upY);
      if (api) api.notifyInteract();
      if (window.RoleplaySpine) window.RoleplaySpine.click();
      if (window.RoleplayPetCore) window.RoleplayPetCore.emitIntent("click", { x: upX, y: upY });
      if (!bubbleEl.classList.contains("show")) {
        showBubble(CLICK_LINES[Math.floor(Math.random() * CLICK_LINES.length)]);
      }
    }
  });

  // pointercancel 也要清理拖拽状态，避免 busy 计数泄漏
  document.addEventListener("pointercancel", (e) => {
    if (!spineDrag || e.pointerId !== spineDrag.pointerId) return;
    if (spineDrag.busySet && api) api.setBusy(false);
    spineDrag = null;
    document.body.classList.remove("dragging");
  });

  // ───────────────────────── P2 点击反馈层（CSS class + animationend 自清理） ─────────────────────────
  const FX_COLORS = ["#7F77DD", "#1D9E75", "#D4537E", "#EDEDED"];
  function spawnFeedback(x, y) {
    const layer = $("pet-feedback") || document.body;
    if (!layer) return;
    try {
      const ripple = document.createElement("span");
      ripple.className = "fx-ripple";
      ripple.style.left = x + "px";
      ripple.style.top = y + "px";
      layer.appendChild(ripple);
      const removeRipple = () => { try { ripple.remove(); } catch (_) {} };
      ripple.addEventListener("animationend", removeRipple);
      setTimeout(removeRipple, 900);

      for (let i = 0; i < 6; i++) {
        const p = document.createElement("span");
        p.className = "fx-particle";
        const ang = (Math.PI * 2 * i) / 6 + Math.random() * 0.5;
        const dist = 22 + Math.random() * 18;
        p.style.left = x + "px";
        p.style.top = y + "px";
        p.style.setProperty("--fx-dx", Math.cos(ang) * dist + "px");
        p.style.setProperty("--fx-dy", Math.sin(ang) * dist + "px");
        p.style.setProperty("--fx-clr", FX_COLORS[i % FX_COLORS.length]);
        layer.appendChild(p);
        const removeP = () => { try { p.remove(); } catch (_) {} };
        p.addEventListener("animationend", removeP);
        setTimeout(removeP, 1100);
      }
    } catch (_) {}
  }
  function pulseModel() {
    if (!canvasEl) return;
    canvasEl.classList.remove("pulse");
    void canvasEl.offsetWidth; // 强制 reflow，使连续点击也能重播动画
    canvasEl.classList.add("pulse");
  }

  // ───────────────────────── P2 hover 显隐（PetAI 范式：主进程 90ms 轮询 + 浏览器自兜底） ─────────────────────────
  let hoveringWindow = false;
  let uiFlashTimer = null;

  function setHoverUi(v) {
    hoveringWindow = !!v;
    document.body.classList.toggle("ui-visible", hoveringWindow);
    document.body.classList.toggle("ui-hidden", !hoveringWindow);
    pushModelBounds(); // hover 显隐直接影响 UI 可点击区，立即同步给主进程 setShape
  }
  /** 交互时短暂唤出 UI；hover 仍持续时保持可见。 */
  function flashUi(ms) {
    document.body.classList.add("pet-ui", "ui-visible");
    document.body.classList.remove("ui-hidden");
    if (uiFlashTimer) clearTimeout(uiFlashTimer);
    uiFlashTimer = setTimeout(() => {
      uiFlashTimer = null;
      document.body.classList.remove("pet-ui");
      if (!hoveringWindow) setHoverUi(false);
    }, ms || 2600);
    pushModelBounds();
  }
  if (api && typeof api.onHoverState === "function") {
    api.onHoverState((inside) => setHoverUi(!!inside));
  }
  document.addEventListener("mousemove", (e) => {
    window.__lastMouse = { x: e.clientX, y: e.clientY };
    if (!hoveringWindow) setHoverUi(true);
  });
  window.addEventListener("mouseout", (e) => {
    // 仅真正移出窗口（relatedTarget 为空）才隐藏 UI；进入子元素造成的 mouseout 不处理。
    if (!e.relatedTarget) setHoverUi(false);
  });
  // 防止触屏长按/双指手势或 Ctrl+滚轮把整个页面 zoom 放大（表现为“窗口内容变大”）。
  document.addEventListener("gesturestart", (e) => { try { e.preventDefault(); } catch (_) {} });
  document.addEventListener("gesturechange", (e) => { try { e.preventDefault(); } catch (_) {} });
  window.addEventListener("wheel", (e) => {
    if (e.ctrlKey) { try { e.preventDefault(); } catch (_) {} }
  }, { passive: false });
  window.addEventListener("resize", schedulePositionBubble); // 窗口/档位变化时气泡重定位
  window.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && ["+", "-", "=", "0"].includes(e.key)) {
      try { e.preventDefault(); } catch (_) {}
    }
  });

  // ───────────────────────── 对话核心（P1：强制本地 Ollama） ─────────────────────────
  /**
   * 发送一条消息：经 window.RoleplayChat.send 走与聊天页完全相同的
   * /chat/stream SSE 链路（chunk / emotion / done / error），
   * 但 llmOverride 强制 provider=ollama + 本地地址，杜绝远程 API。
   */
  async function send(text) {
    text = String(text || "").trim();
    if (!text) return false;
    if (chatBusy) {
      showBubble("（还在想上一句…）");
      return false;
    }
    if (!window.RoleplayChat || typeof window.RoleplayChat.send !== "function") {
      showBubble("⚠️ 对话模块未就绪");
      return false;
    }
    chatBusy = true;
    noteActivity(); // 对话即互动（唤醒/重置睡眠）
    if (api) {
      api.setBusy(true); // 对话期间暂停自主漫步
      api.notifyInteract();
    }

    // 用户发言即时手势（Spine 播放手势对应的真实动画，而非随机 click）
    const gesture = detectGesture(text);
    if (gesture && window.RoleplaySpine) window.RoleplaySpine.playMotion(gesture);
    if (window.RoleplayPetCore) window.RoleplayPetCore.emitIntent("motion", { pose: gesture || "click" });

    showBubble("…", { sticky: true });
    let full = "";
    let saw = false;

    try {
      await window.RoleplayChat.send(text, {
        temperature: state.temperature,
        useWeb: false, // 宠物不联网检索
        // 关键：请求级覆盖强制本地 Ollama（后端 build_llm_from_config 已支持）
        llmOverride: {
          provider: "ollama",
          model: state.ollama_model,
          base_url: state.ollama_base_url,
        },
        onFirstChunk() {
          // 只能清空文本节点容器；清 bubbleEl 会把 #pet-bubble-text 一并移除，
          // 导致后续 typewriter 写进已脱离 DOM 的节点，气泡永远空白。
          bubbleTextEl.textContent = "";
        },
        onChunk(t) {
          saw = true;
          appendBubbleText(t);
        },
        onMotion(names) {
          // LLM {动作：xxx} 指令：按名字播放对应动画（未知名字在 spine 内部回落互动池）
          names.forEach((name) => {
            if (window.RoleplaySpine) window.RoleplaySpine.playMotion(name);
            if (window.RoleplayPetCore) window.RoleplayPetCore.emitIntent("motion", { pose: name });
          });
        },
        onEmotion(d) {
          // 情感事件：Spine 播放表达情绪的动画
          if (window.RoleplaySpine) window.RoleplaySpine.emotion(d.emotion);
          if (window.RoleplayPetCore) window.RoleplayPetCore.emitIntent("emotion", d);
        },
        onDone() { /* follow_ups 宠物页暂不展示（P2） */ },
        onError(detail) {
          showBubble("⚠️ " + detail);
        },
        onComplete(fullReply, sawChunk) {
          full = fullReply;
          saw = sawChunk;
        },
        onFail(message) {
          showBubble("（连接失败：" + message + "）");
        },
      });
    } catch (e) {
      // 无论 SSE 还是 RoleplayChat 内部异常，都不能让 chatBusy 卡死。
      if (!saw) showBubble("⚠️ 对话失败：" + (e && e.message ? e.message : e));
    } finally {
      chatBusy = false;
      if (api) api.setBusy(false);
    }

    // 流结束：flush 打字机余量、移除光标、转非粘性自动收起；按设置朗读
    if (saw && full) {
      finishBubble(full);
      speakReply(full);
    } else if (saw) {
      finishBubble("");
    }
    return { full, saw };
  }

  /** 按设置朗读回复（复用 voice.js 的 TTS；静音/关闭/勿扰时跳过）。 */
  function speakReply(text) {
    if (state.muted || !state.auto_tts || state.dnd || !state.voice_enabled) return; // P1-3：勿扰禁声
    if (!window.RoleplayVoice || typeof window.RoleplayVoice.speak !== "function") return;
    try {
      window.RoleplayVoice.speak(text, {
        speed: state.voice_speed,
        volume: state.voice_volume,
      });
    } catch (e) {
      console.warn("[pet] TTS 失败", e);
    }
  }

  // ───────────────────────── Ollama 探活 ─────────────────────────
  async function checkOllama() {
    try {
      const resp = await fetch("/api/llm/ollama/models", { cache: "no-store" });
      setDot("ollama", resp.ok); // 后端成功代理即视为 Ollama 在线
    } catch (_) {
      setDot("ollama", false);
    }
  }

  // ───────────────────────── 语音钩子（P4 接入按键/持续模式） ─────────────────────────
  // voice.js 识别完成 → 这里接管（聊天页无 RoleplayPet，行为不变）
  // 注：语音识别走后端 /voice/stt（本地 faster-whisper），与网页版一致。

  // ───────────────────────── 屏幕识别（P3：OCR 结果 → Ollama 评论） ─────────────────────────
  if (api && typeof api.onScreenText === "function") {
    api.onScreenText((d) => {
      const text = (d && d.text || "").trim();
      if (!text) {
        showBubble("屏幕上没识别到什么文字。");
        return;
      }
      // P1-6：气泡先显首句摘要 +「详细」折叠（点击展开全文），随后自动发评论
      const firstLine = text.split("\n")[0].slice(0, 40);
      flashUi(5000);
      showBubble("🔍 " + firstLine + (text.length > firstLine.length ? "…" : "") + "（正在点评…）", { sticky: true });
      // 隐私：识别文本只在本机流转，作为对话消息发给本地 Ollama
      const snippet = text.length > 1500 ? text.slice(0, 1500) + "…" : text;
      send("我在看你的屏幕，上面写着（节选）：\n" + snippet + "\n请用一句话点评或提醒我。");
    });
  }

  // ───────────────────────── 语音聆听（菜单「语音对话」与 Alt+Space 共用） ─────────────────────────
  // 统一管理：聆听表情 + busy 引用计数置位一次 + 轮询检测结束恢复（stopRecording 无回调）
  let listenWatcher = null;
  function startListening() {
    if (!window.RoleplayVoice) {
      showBubble("⚠️ 语音模块未就绪");
      return;
    }
    if (window.RoleplayVoice.isRecording()) return; // 已在聆听
    showBubble("（正在听…再按一次结束）");
    if (window.RoleplaySpine) window.RoleplaySpine.emotion("confused");
    if (api) api.setBusy(true); // 聆听期间暂停自主漫步（只置位一次）
    try {
      window.RoleplayVoice.startRecording();
    } catch (e) {
      console.warn("[pet] 录音启动失败", e);
    }
    if (listenWatcher) clearInterval(listenWatcher);
    listenWatcher = setInterval(() => {
      if (!window.RoleplayVoice.isRecording()) {
        clearInterval(listenWatcher);
        listenWatcher = null;
        if (api) api.setBusy(false);
        // 恢复中性表情
        if (window.RoleplaySpine) window.RoleplaySpine.emotion("neutral");
      }
    }, 400);
  }
  function stopListening() {
    if (window.RoleplayVoice && window.RoleplayVoice.isRecording()) {
      window.RoleplayVoice.stopRecording();
    }
  }

  // 按住说话：主进程全局快捷键（Alt+Space）触发；按下=开始录音，再按=结束
  if (api && typeof api.onPtt === "function") {
    api.onPtt(() => {
      if (window.RoleplayVoice && window.RoleplayVoice.isRecording()) stopListening();
      else startListening();
    });
  }
  // 网页版经回环服务 → 宠物说一句话（气泡 + 朗读，不进对话上下文）
  if (api && typeof api.onTalk === "function") {
    api.onTalk((d) => {
      if (d && d.text) say(String(d.text));
    });
  }
  // 网页按钮唤起（回环服务 /launch）→ 视为一次互动，把宠物从睡眠中唤醒
  if (api && typeof api.onWake === "function") {
    api.onWake(() => noteActivity());
  }

  /** 宠物直接说一句话（气泡 + 按设置朗读）。 */
  function say(text) {
    noteActivity(); // 外部让宠物说话也算一次互动（唤醒/重置睡眠计时）
    flashUi(3200);
    showBubble(text);
    speakReply(text);
  }

  // ───────────────────────── 浮层定位（测量→钳制→落位） ─────────────────────────
  /**
   * 把绝对定位浮层摆到 (x, y) 并钳制在视口内，返回落位后的矩形。
   * el 必须已参与布局（调用方先挂 .open 等类或以 visibility:hidden 预显示），
   * 否则 display:none 下 offsetWidth/Height 为 0，只能靠猜——旧实现正因此把
   * 高约 600px 的菜单按 300px 钳制，下半截永远落在窗外不可点。
   */
  function placeFloating(el, x, y, pad) {
    pad = pad == null ? 4 : pad;
    void el.offsetWidth; // 强制 reflow，取真实尺寸
    const w = el.offsetWidth;
    const h = el.offsetHeight;
    const left = Math.max(pad, Math.min(x, window.innerWidth - w - pad));
    const top = Math.max(pad, Math.min(y, window.innerHeight - h - pad));
    el.style.left = left + "px";
    el.style.top = top + "px";
    return { left, top, width: w, height: h };
  }

  // ───────────────────────── 右键菜单 ─────────────────────────
  function openMenu(x, y) {
    menuEl.classList.add("open");
    menuEl.style.visibility = "hidden"; // 参与布局但不可见：先量后摆，规避错位闪烁
    placeFloating(menuEl, x, y);
    menuEl.style.visibility = "";
    pushModelBounds(); // 右键菜单打开时并入可点击区
    setTimeout(() => pushModelBounds(), 50); // 等菜单完成布局后再补一次，避免 setShape 把菜单裁掉
  }
  function closeMenu() {
    menuEl.classList.remove("open");
    pushModelBounds();
  }

  document.addEventListener("contextmenu", (e) => {
    e.preventDefault();
    openMenu(e.clientX, e.clientY);
  });
  document.addEventListener("pointerdown", (e) => {
    if (menuEl.classList.contains("open") && !menuEl.contains(e.target)) closeMenu();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      // 逐层退出：引导 → 设置 → 菜单 → 输入条 → 气泡
      if (onbEl && onbEl.classList.contains("open")) { finishOnboarding(); return; }
      if (settingsEl.classList.contains("open")) { closeSettings(); return; }
      if (menuEl.classList.contains("open")) { closeMenu(); return; }
      if (inputBarEl.classList.contains("open")) { closeInputBar(); return; }
      if (bubbleEl.classList.contains("show")) { hideBubble(); return; }
    }
  });

  menuEl.addEventListener("click", (e) => {
    const btn = e.target.closest("button[data-act]");
    if (!btn) return;
    const act = btn.dataset.act;
    closeMenu();
    handleMenuAction(act);
  });

  function handleMenuAction(act) {
    noteActivity(); // 任何菜单操作都算互动（唤醒/重置睡眠计时）
    flashUi(3200);
    if (window.RoleplayPetCore) window.RoleplayPetCore.emitIntent("menu", { act });
    switch (act) {
      case "talk":
        send(TALK_STARTERS[Math.floor(Math.random() * TALK_STARTERS.length)]);
        break;
      case "type":
        // P0-4：打开底部输入栏（打字聊天）
        openInputBar();
        break;
      case "motion":
        // 随机动作：Spine 点击互动池（共享动作库 motion 意图）
        if (window.RoleplaySpine) window.RoleplaySpine.click();
        if (window.RoleplayPetCore) window.RoleplayPetCore.emitIntent("motion", { pose: "click" });
        break;
      case "zoom-in":
        changeZoom(0.1);
        break;
      case "zoom-out":
        changeZoom(-0.1);
        break;
      case "bubble-bigger":
        changeBubbleSize(0.1);
        break;
      case "bubble-smaller":
        changeBubbleSize(-0.1);
        break;
      case "screen":
        if (api && typeof api.captureScreen === "function") {
          showBubble("让我看看屏幕上有什么…");
          api.captureScreen();
        } else {
          showBubble("屏幕识别仅在桌面端可用。");
        }
        break;
      case "spine":
        // P1.1：循环切换 314701_s → 314701 → 314702 → …
        cycleSpineModel();
        break;
      case "voice":
        // 语音对话：点一次开始聆听，再点一次结束（识别结果经 onVoiceInput 自动发送）
        if (window.RoleplayVoice && window.RoleplayVoice.isRecording()) stopListening();
        else startListening();
        break;
      case "mute":
        state.muted = !state.muted;
        saveState();
        applyMuteMenu();
        // P0-6：菜单静音与原声模块（RoleplayPetVoice）联动
        if (window.RoleplayPetVoice) window.RoleplayPetVoice.setMuted(state.muted);
        break;
      case "dnd":
        setDnd(!state.dnd);
        break;
      case "dnd-exit":
        setDnd(false);
        break;
      case "lock":
        setLocked(!state.locked);
        break;
      case "settings":
        openSettings();
        break;
      case "share":
        // P2-6：人偶+气泡合成图 → 系统保存对话框（仅用户确认后落盘）
        exportSnapshot();
        break;
      case "hide":
        // 隐藏宠物：窗口隐藏但应用/控制服务保持运行，网页按钮可再次唤起
        if (api && typeof api.hidePet === "function") api.hidePet();
        else petToast("仅桌面端支持隐藏宠物");
        break;
      case "quit":
        if (api && typeof api.quit === "function") api.quit();
        else window.close();
        break;
    }
  }

  // ───────────────────────── P1：勿扰 / 锁位 / toast / 帮助 ─────────────────────────
  let dndAutoTimer = null;

  function petToast(msg) {
    const t = document.createElement("div");
    t.className = "toast";
    t.textContent = msg;
    document.body.appendChild(t);
    setTimeout(() => { try { t.remove(); } catch (_) {} }, 2200);
  }

  function applyMuteMenu() {
    const label = $("menu-mute-label");
    const ico = $("ico-mute");
    if (label) label.textContent = state.muted ? "取消静音" : "静音";
    if (ico) ico.setAttribute("href", state.muted ? "#i-volume-2" : "#i-volume-x");
  }

  /** P1-3 勿扰：透明度 0.55、禁声、漫步暂停、chip 呼吸、菜单顶部解除行、30min 自动解除。 */
  function setDnd(on) {
    state.dnd = !!on;
    saveState();
    if (state.dnd) {
      document.body.classList.add("dnd");
      $("chip-dnd").classList.add("show");
      $("pet-menu").classList.add("dnd");
      $("menu-dnd-label").textContent = "取消勿扰";
      if (api && typeof api.setDnd === "function") api.setDnd(true);
      if (dndAutoTimer) clearTimeout(dndAutoTimer);
      if (state.dnd_auto_release) {
        dndAutoTimer = setTimeout(() => setDnd(false), 30 * 60 * 1000); // 30 分钟自动解除
      }
      if (window.RoleplayVoice && typeof window.RoleplayVoice.stopSpeaking === "function") {
        window.RoleplayVoice.stopSpeaking(); // 立即禁声
      }
    } else {
      document.body.classList.remove("dnd");
      $("chip-dnd").classList.remove("show");
      $("pet-menu").classList.remove("dnd");
      $("menu-dnd-label").textContent = "勿扰";
      if (dndAutoTimer) { clearTimeout(dndAutoTimer); dndAutoTimer = null; }
      if (api && typeof api.setDnd === "function") api.setDnd(false);
    }
  }

  /** P1-4 锁位：拖拽失效（主进程 moveBy 守卫）、虚线框、锁位 chip、长按人偶 1.5s 解锁。 */
  function setLocked(on) {
    state.locked = !!on;
    saveState();
    $("pet-lockframe").classList.toggle("show", state.locked);
    $("chip-lock").classList.toggle("show", state.locked);
    $("menu-lock-label").textContent = state.locked ? "取消锁位" : "锁位";
    if (api && typeof api.setLocked === "function") api.setLocked(state.locked);
    flashUi(3200);
    petToast(state.locked ? "位置已锁定（长按模型 1.5s 解锁）" : "位置已解锁");
  }

  // 长按人偶 1.5s 解锁（按下起算，抬起取消；浮层上按下不触发）
  let lockPressTimer = null;
  document.addEventListener("pointerdown", (e) => {
    if (!state.locked || e.button !== 0) return;
    if (e.target.closest("#pet-bubble, #pet-menu, #pet-settings, #pet-inputbar, #pet-onboarding")) return;
    lockPressTimer = setTimeout(() => {
      lockPressTimer = null;
      setLocked(false);
      petToast("已解锁");
    }, 1500);
  });
  document.addEventListener("pointerup", () => {
    if (lockPressTimer) { clearTimeout(lockPressTimer); lockPressTimer = null; }
  });

  // 锁位中的拖拽尝试反馈：由 spine 拖拽逻辑检查（见 pointermove 处）
  /** P2-6：合成「人偶 + 气泡」PNG → 桌面端系统保存对话框（零自动落盘）。 */
  function exportSnapshot() {
    try {
      const cv = canvasEl.querySelector("canvas") || canvasEl;
      const w = window.innerWidth;
      const h = window.innerHeight;
      const off = document.createElement("canvas");
      off.width = w;
      off.height = h;
      const ctx = off.getContext("2d");
      ctx.clearRect(0, 0, w, h);
      // 画布未开 preserveDrawingBuffer：合成后 backbuffer 已清空，
      // drawImage 前必须先重渲染一帧，否则分享截图是全透明图。
      if (window.RoleplaySpine && typeof window.RoleplaySpine.renderNow === "function") {
        window.RoleplaySpine.renderNow();
      }
      try { ctx.drawImage(cv, 0, 0, w, h); } catch (_) {}
      // 气泡（有文本才绘制）
      const text = bubbleTextEl.textContent || "";
      if (bubbleEl.classList.contains("show") && text) {
        const r = bubbleEl.getBoundingClientRect();
        const pad = 12;
        const bw = Math.min(r.width, w - 16);
        ctx.font = "14px Georgia, SimSun, serif";
        const lines = [];
        let line = "";
        for (const ch of text) {
          if (ctx.measureText(line + ch).width > bw - pad * 2) { lines.push(line); line = ch; }
          else line += ch;
        }
        lines.push(line);
        const bh = lines.length * 22 + pad * 2;
        const bx = Math.max(8, r.left);
        const by = Math.max(8, r.top);
        ctx.fillStyle = "rgba(16,22,28,0.92)";
        ctx.strokeStyle = "rgba(201,168,106,0.28)";
        roundRectPath(ctx, bx, by, bw, bh, 10);
        ctx.fill();
        ctx.stroke();
        ctx.fillStyle = "#e8e2d4";
        lines.forEach((ln, i) => ctx.fillText(ln, bx + pad, by + pad + 20 + i * 22));
      }
      const dataUrl = off.toDataURL("image/png");
      if (api && typeof api.exportImage === "function") {
        api.exportImage(dataUrl).then((res) => {
          if (res && res.ok) petToast("已保存：" + res.path);
          else if (!res || !res.canceled) petToast("导出失败");
        }).catch(() => petToast("导出失败"));
      } else {
        // 浏览器预览模式：直接下载
        const a = document.createElement("a");
        a.href = dataUrl;
        a.download = "pet-snapshot.png";
        a.click();
      }
    } catch (e) {
      console.warn("[pet] 截图合成失败", e);
      petToast("截图合成失败");
    }
  }
  function roundRectPath(ctx, x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + w, y, x + w, y + h, r);
    ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r);
    ctx.arcTo(x, y, x + w, y, r);
    ctx.closePath();
  }
  // ── P1-5 睡眠分级（闲置 90s 浅睡 / 5min 深睡；任意交互唤醒；勿扰中不睡） ──
  let sleepLevel = 0; // 0=醒 1=浅睡 2=深睡
  let lastActivityAt = Date.now();
  function noteActivity() {
    const wasAsleep = sleepLevel > 0;
    lastActivityAt = Date.now();
    if (wasAsleep) {
      sleepLevel = 0;
      if (renderer && typeof renderer.sleep === "function") {
        try { renderer.sleep(0); } catch (_) {}
      }
    }
  }
  setInterval(() => {
    const idle = Date.now() - lastActivityAt;
    const busyNow = chatBusy || !!spineDrag || state.dnd || settingsEl.classList.contains("open") || onbEl.classList.contains("open");
    if (busyNow) return;
    if (sleepLevel === 0 && idle >= 90 * 1000) {
      sleepLevel = 1; // 浅睡
      if (renderer && typeof renderer.sleep === "function") { try { renderer.sleep(1); } catch (_) {} }
    } else if (sleepLevel === 1 && idle >= 5 * 60 * 1000) {
      sleepLevel = 2; // 深睡
      if (renderer && typeof renderer.sleep === "function") { try { renderer.sleep(2); } catch (_) {} }
    }
  }, 15000);

  // 网页按钮/系统唤起：窗口重新可见/聚焦时视为一次互动，把宠物从睡眠中唤醒
  window.addEventListener("focus", noteActivity);
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible") noteActivity();
  });

  // 帮助气泡（P1-8：? 快捷键一览）
  document.addEventListener("keydown", (e) => {
    if (e.key === "?" && !e.ctrlKey && !e.metaKey && !e.altKey) {
      const target = e.target;
      if (target && (target.tagName === "INPUT" || target.tagName === "TEXTAREA")) return; // 输入态豁免
      e.preventDefault();
      showBubble(
        "快捷键：拖我移动 · 右键菜单 · 单击互动\n" +
        (api ? "Alt+Space 按住说话 · " : "") +
        "Ctrl+Enter 打字 · Esc 逐层关闭 · ? 本提示",
        { sticky: true }
      );
    }
  });

  // ───────────────────────── 底部输入栏（P0-T6：折叠圆钮 + Ctrl+Enter + 8s 自动收起） ─────────────────────────
  const foldBtn = $("pet-input-fold");
  if (foldBtn) foldBtn.classList.add("show"); // 折叠圆钮常驻（收起态），展开时隐藏
  let inputAutoCloseTimer = null;
  const INPUT_AUTO_CLOSE_MS = 8000; // 8s 无操作自动收起（§4.5，Q1 已接受的取舍）

  function armAutoClose() {
    if (inputAutoCloseTimer) clearTimeout(inputAutoCloseTimer);
    inputAutoCloseTimer = setTimeout(closeInputBar, INPUT_AUTO_CLOSE_MS);
  }
  function openInputBar() {
    inputBarEl.classList.add("open");
    foldBtn.classList.remove("show"); // 展开时收起圆钮
    flashUi(8000); // 输入期间保持 UI 可见
    setTimeout(() => { try { inputEl.focus(); } catch (_) {} }, 30);
    armAutoClose();
    pushModelBounds();
  }
  function closeInputBar() {
    inputBarEl.classList.remove("open");
    foldBtn.classList.add("show");
    inputEl.value = "";
    if (inputAutoCloseTimer) { clearTimeout(inputAutoCloseTimer); inputAutoCloseTimer = null; }
    try { inputEl.blur(); } catch (_) {}
    flashUi(1200);
    pushModelBounds();
  }
  function submitInput() {
    const text = inputEl.value.trim();
    closeInputBar();
    if (text) send(text);
  }
  foldBtn.addEventListener("click", openInputBar);
  $("pet-input-send").addEventListener("click", submitInput);
  $("pet-input-voice").addEventListener("click", () => {
    // 语音切换：与菜单「语音对话」同逻辑（按住说话由 Alt+Space 全局快捷键驱动）
    handleMenuAction("voice");
  });
  inputEl.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey && !e.ctrlKey && !e.metaKey) {
      e.preventDefault();
      submitInput();
    }
    if (e.key === "Escape") {
      e.preventDefault();
      e.stopPropagation(); // 避免触发全局逐层退出（只收起输入条）
      closeInputBar();
    }
  });
  inputEl.addEventListener("input", armAutoClose);
  // 全局 Ctrl+Enter：任意位置展开输入条并聚焦（§5.2）
  document.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      if (!inputBarEl.classList.contains("open")) {
        e.preventDefault();
        openInputBar();
      }
    }
  });
  // 输入栏打开时点舞台其他区域 → 收起
  document.addEventListener("pointerdown", (e) => {
    if (inputBarEl.classList.contains("open") && !inputBarEl.contains(e.target) && !foldBtn.contains(e.target)) {
      // 正在拖拽模型时不收起（避免拖拽时误关）
      if (!e.target.closest("#pet-canvas")) closeInputBar();
    }
  });
  // ───────────────────────── 设置抽屉（P1-2：五 tab 卡片化） ─────────────────────────
  let settingsTab = "model";
  let desktopCfg = null; // api.getConfig() 缓存（桌面端 tab 用）
  const SETTINGS_TABS = ["model", "chat", "voice", "ocr", "desktop"];
  const SETTINGS_TAB_NAMES = { model: "模型", chat: "对话", voice: "语音", ocr: "屏幕识别", desktop: "桌面端" };

  function openSettings() {
    if (api && typeof api.getConfig === "function") {
      api.getConfig().then((cfg) => {
        desktopCfg = cfg;
        if (settingsTab === "desktop") renderSettings();
      }).catch(() => {});
    }
    renderSettings();
    settingsEl.classList.add("open");
    pushModelBounds(); // 设置抽屉全窗 UI 必须立即恢复可点击
  }
  function closeSettings() {
    settingsEl.classList.remove("open");
    pushModelBounds();
  }
  $("settings-close").addEventListener("click", closeSettings);

  function card(title, inner) {
    return `<div class="card"><h4>${title}</h4>${inner}</div>`;
  }
  function row(label, html) {
    return `<div class="row"><label>${label}</label>${html}</div>`;
  }
  function rangeRow(label, id, min, max, step, value) {
    return row(label, `<input type="range" id="${id}" min="${min}" max="${max}" step="${step}" value="${value}" /><span class="v" id="${id}-v">${value}</span>`);
  }
  function bindRange(id, fn) {
    const el = $(id);
    if (!el) return;
    const v = $(id + "-v");
    const apply = () => { if (v) v.textContent = el.value; fn(Number(el.value)); };
    el.addEventListener("input", apply);
  }

  function renderSettings() {
    const tabsEl = $("settings-tabs");
    tabsEl.innerHTML = SETTINGS_TABS.map((t) =>
      `<button type="button" data-tab="${t}" class="${t === settingsTab ? "on" : ""}" role="tab">${SETTINGS_TAB_NAMES[t]}</button>`
    ).join("");
    tabsEl.querySelectorAll("button").forEach((b) => {
      b.addEventListener("click", () => { settingsTab = b.dataset.tab; renderSettings(); });
    });
    const body = $("settings-body");
    body.innerHTML = "";
    body.appendChild(buildTabPanel(settingsTab));
    bindTabPanel(settingsTab);
  }

  function buildTabPanel(tab) {
    const holder = document.createElement("div");
    let html = "";

    if (tab === "model") {
      // P0：Spine 唯一渲染器；P1.1：骨骼动画可切换。
      const spineModels = getSpineModels();
      html = card("呈现（Spine 人偶）",
        row("骨骼动画", `<select id="set-spine-model">${spineModels.map((m) =>
          `<option value="${m.id}"${m.id === state.spine_model ? " selected" : ""}>${esc(m.name)}</option>`).join("")}</select>`) +
        row("渲染器", `<span class="hintline" style="margin:0">Spine（已锁定）</span>`) +
        rangeRow("缩放", "set-zoom", 0.5, 2, 0.05, state.zoom)
      );
    } else if (tab === "chat") {
      html = card("本地 Ollama（宠物强制本地，不走远程 API）",
        row("模型", `<input type="text" id="set-ollama-model" value="${esc(state.ollama_model)}" placeholder="qwen2.5:1.5b" />`) +
        row("地址", `<input type="text" id="set-ollama-url" value="${esc(state.ollama_base_url)}" placeholder="http://127.0.0.1:11434/v1" />`) +
        rangeRow("温度", "set-temp", 0.2, 1.5, 0.05, state.temperature)
      );
      html += card("朗读",
        row("自动朗读", `<input type="checkbox" id="set-auto-tts"${state.auto_tts ? " checked" : ""} />`) +
        row("静音", `<input type="checkbox" id="set-muted"${state.muted ? " checked" : ""} />`)
      );
      html += card("气泡/弹窗",
        rangeRow("气泡大小", "set-bubble-size", 0.75, 1.6, 0.05, state.bubble_size)
      );
    } else if (tab === "voice") {
      html = card("语音（宠物侧设置，写回 roleplay_voice_state 与聊天页共享）",
        row("语音开关", `<input type="checkbox" id="set-v-on"${state.voice_enabled ? " checked" : ""} />`) +
        rangeRow("语速", "set-v-speed", 0.5, 2, 0.05, state.voice_speed) +
        rangeRow("音量", "set-v-vol", 0, 100, 5, state.voice_volume)
      );
      html += `<div class="hintline">按住说话：${api ? "Alt+Space（全局快捷键）" : "仅桌面端可用"}。识别走本地 faster-whisper（/voice/stt），多语言自动。</div>`;
    } else if (tab === "ocr") {
      const ocrCfg = (desktopCfg && desktopCfg.ocr) || {};
      html = card("屏幕识别（截图+本地 OCR，零落盘）",
        row("触发档位", `<select id="set-ocr-mode">
          <option value="off"${(ocrCfg.autoMode || "off") === "off" ? " selected" : ""}>手动</option>
          <option value="keyword"${ocrCfg.autoMode === "keyword" ? " selected" : ""}>关键词自动</option>
          <option value="timer"${ocrCfg.autoMode === "timer" ? " selected" : ""}>定时</option>
        </select>`) +
        row("关键词(逗号分隔)", `<input type="text" id="set-ocr-keywords" value="${esc((ocrCfg.keywords || []).join(","))}" />`) +
        row("OCR 语言", `<select id="set-ocr-lang">
          <option${(ocrCfg.lang || "chi_sim+eng") === "chi_sim+eng" ? " selected" : ""}>chi_sim+eng</option>
          <option${ocrCfg.lang === "chi_sim" ? " selected" : ""}>chi_sim</option>
          <option${ocrCfg.lang === "eng" ? " selected" : ""}>eng</option>
        </select>`)
      );
      html += `<div class="hintline">节流：手动 ≥2s / 关键词 ≥30s / 定时 ≥60s。</div>`;
    } else if (tab === "desktop") {
      const pet = (desktopCfg && desktopCfg.pet) || {};
      const walkMin = Math.round((pet.walkMinMs || 10000) / 1000);
      const walkMax = Math.round((pet.walkMaxMs || 30000) / 1000);
      html = card("窗口",
        row("档位", api ? `<select id="set-size-tier">
            <option value="S">S · 320×420</option>
            <option value="M">M · 420×560</option>
            <option value="L">L · 480×640</option>
          </select>` : "仅桌面端") +
        row("置顶层级", api ? `<select id="set-top-level">
            <option value="floating"${(pet.alwaysOnTopLevel || "floating") === "floating" ? " selected" : ""}>普通置顶</option>
            <option value="screen-saver"${pet.alwaysOnTopLevel === "screen-saver" ? " selected" : ""}>压全屏</option>
          </select>` : "") +
        row("漫步频率(秒)", api ? `<input type="text" id="set-walk-range" value="${esc(walkMin + "-" + walkMax)}" style="width:90px" />` : "") +
        row("跟随光标", api ? `<select id="set-follow">
            <option value="off"${(pet.followMode || "off") === "off" ? " selected" : ""}>关闭</option>
            <option value="cursor"${pet.followMode === "cursor" ? " selected" : ""}>跟随光标</option>
          </select>` : "")
      );
      html += card("摆位（P1-7 多屏）",
        row("显示器", api ? `<select id="set-display"><option value="">加载中…</option></select>` : "") +
        row("重置位置", api ? `<button type="button" id="set-reset-pos" class="navbtn ghost" style="height:28px">回到默认位置</button>` : "")
      );
      html += card("修饰态",
        row("勿扰", `<input type="checkbox" id="set-dnd"${state.dnd ? " checked" : ""} />`) +
        row("勿扰 30 分钟自动解除", `<input type="checkbox" id="set-dnd-auto"${state.dnd_auto_release ? " checked" : ""} />`) +
        row("锁位", `<input type="checkbox" id="set-locked"${state.locked ? " checked" : ""} />`) +
        row("重看引导", `<button type="button" id="set-reonboard" class="navbtn ghost" style="height:28px">播放引导</button>`)
      );
      if (!api) html = `<div class="hintline">桌面端能力仅在 Electron 壳中可用（浏览器预览模式）。</div>` + html;
    }
    holder.innerHTML = html;
    return holder;
  }

  function bindTabPanel(tab) {
    if (tab === "model") {
      const spineSel = $("set-spine-model");
      if (spineSel) {
        spineSel.addEventListener("change", (e) => {
          closeSettings();
          switchSpineModel(e.target.value);
        });
      }
      bindRange("set-zoom", (v) => {
        state.zoom = v;
        saveState();
        if (renderer && typeof renderer.setZoom === "function") renderer.setZoom(v);
      });
    } else if (tab === "chat") {
      $("set-ollama-model").addEventListener("change", (e) => { state.ollama_model = e.target.value.trim() || DEFAULT_STATE.ollama_model; saveState(); });
      $("set-ollama-url").addEventListener("change", (e) => { state.ollama_base_url = e.target.value.trim() || DEFAULT_STATE.ollama_base_url; saveState(); });
      bindRange("set-temp", (v) => { state.temperature = v; saveState(); });
      $("set-auto-tts").addEventListener("change", (e) => { state.auto_tts = e.target.checked; saveState(); });
      $("set-muted").addEventListener("change", (e) => {
        state.muted = e.target.checked; saveState(); applyMuteMenu();
        // P0-6：设置抽屉静音与原声模块（RoleplayPetVoice）联动
        if (window.RoleplayPetVoice) window.RoleplayPetVoice.setMuted(state.muted);
      });
      bindRange("set-bubble-size", (v) => { state.bubble_size = v; saveState(); applyBubbleSize(); });
    } else if (tab === "voice") {
      $("set-v-on").addEventListener("change", (e) => { state.voice_enabled = e.target.checked; saveState(); syncVoiceState(); });
      bindRange("set-v-speed", (v) => { state.voice_speed = v; saveState(); syncVoiceState(); });
      bindRange("set-v-vol", (v) => { state.voice_volume = v; saveState(); syncVoiceState(); });
    } else if (tab === "ocr") {
      const applyOcr = () => {
        if (!api || typeof api.setConfig !== "function") return;
        const mode = $("set-ocr-mode").value;
        const kws = $("set-ocr-keywords").value.split(/[,，]/).map((s) => s.trim()).filter(Boolean);
        const lang = $("set-ocr-lang").value;
        api.setConfig({ ocr: { autoMode: mode, keywords: kws.length ? kws : undefined, lang } });
      };
      $("set-ocr-mode").addEventListener("change", applyOcr);
      $("set-ocr-keywords").addEventListener("change", applyOcr);
      $("set-ocr-lang").addEventListener("change", applyOcr);
    } else if (tab === "desktop") {
      const pet = (desktopCfg && desktopCfg.pet) || {};
      const sizeEl = $("set-size-tier");
      if (sizeEl) sizeEl.value = (pet.width || 320) >= 460 ? "L" : (pet.width || 320) >= 380 ? "M" : "S";
      if (sizeEl && api && typeof api.setSize === "function") {
        sizeEl.addEventListener("change", (e) => {
          const SIZES = { S: [320, 420], M: [420, 560], L: [480, 640] };
          const s = SIZES[e.target.value] || SIZES.S;
          api.setSize(s[0], s[1]);
        });
      }
      const topEl = $("set-top-level");
      if (topEl) topEl.addEventListener("change", (e) => {
        if (api) api.setConfig({ pet: { alwaysOnTopLevel: e.target.value } });
      });
      const walkEl = $("set-walk-range");
      if (walkEl) walkEl.addEventListener("change", (e) => {
        const m = String(e.target.value).match(/^(\d+)\s*-\s*(\d+)$/);
        if (m && api) {
          api.setConfig({ pet: { walkMinMs: Math.max(5000, Number(m[1]) * 1000), walkMaxMs: Math.max(Number(m[1]) * 1000 + 5000, Number(m[2]) * 1000) } });
        }
      });
      const followEl = $("set-follow");
      if (followEl) followEl.addEventListener("change", (e) => {
        if (api) api.setConfig({ pet: { followMode: e.target.value } });
      });
      const dispEl = $("set-display");
      if (dispEl && api && typeof api.getDisplays === "function") {
        api.getDisplays().then((list) => {
          dispEl.innerHTML = "";
          (list || []).forEach((d) => {
            const opt = document.createElement("option");
            opt.value = String(d.id);
            opt.textContent = (d.primary ? "主屏 · " : "") + d.label + " (" + d.bounds.width + "×" + d.bounds.height + ")";
            dispEl.appendChild(opt);
          });
          dispEl.addEventListener("change", (e2) => {
            if (api.moveToDisplay) api.moveToDisplay(e2.target.value);
          });
        }).catch(() => {});
      }
      const resetEl = $("set-reset-pos");
      if (resetEl && api && typeof api.resetPosition === "function") {
        resetEl.addEventListener("click", () => api.resetPosition());
      }
      $("set-dnd").addEventListener("change", (e) => setDnd(e.target.checked));
      $("set-dnd-auto").addEventListener("change", (e) => { state.dnd_auto_release = e.target.checked; saveState(); });
      $("set-locked").addEventListener("change", (e) => setLocked(e.target.checked));
      $("set-reonboard").addEventListener("click", () => { closeSettings(); startOnboarding(); });
    }
  }

  /** 写回 voice.js 共享的 localStorage（roleplay_voice_state），保持字段兼容。 */
  function syncVoiceState() {
    try {
      const cur = JSON.parse(localStorage.getItem("roleplay_voice_state") || "{}");
      cur.voice_enabled = !!state.voice_enabled;
      cur.tts_speed = state.voice_speed;
      cur.tts_volume = state.voice_volume;
      localStorage.setItem("roleplay_voice_state", JSON.stringify(cur));
    } catch (_) {}
  }
  function esc(s) {
    const div = document.createElement("div");
    div.textContent = s == null ? "" : String(s);
    return div.innerHTML;
  }

  // ───────────────────────── 状态 chips（后端 / Ollama / 录音） ─────────────────────────
  function setDot(name, v) {
    const el = chips[name];
    if (!el) return;
    el.classList.remove("ok", "bad");
    if (v === true) el.classList.add("ok");
    else if (v === false) el.classList.add("bad");
    $("pet-status").classList.add("show");
  }
  if (api && typeof api.onBackendState === "function") {
    api.onBackendState((s) => setDot("backend", !!s && s.ok));
  }
  // 同源页也可直接探后端（浏览器预览模式）
  function checkBackend() {
    fetch("/health", { cache: "no-store" })
      .then((r) => setDot("backend", r.ok))
      .catch(() => setDot("backend", false));
  }
  // 录音指示灯：轮询 voice.js 状态
  setInterval(() => {
    if (window.RoleplayVoice && typeof window.RoleplayVoice.isRecording === "function") {
      setDot("mic", window.RoleplayVoice.isRecording());
    }
  }, 600);

  // ───────────────────────── 浏览器预览模式提示 ─────────────────────────
  if (!api && !state.browser_seen) {
    hintEl.textContent = "浏览器预览模式 · 用桌面端可获得悬浮/置顶/快捷键能力";
    hintEl.classList.add("show");
    state.browser_seen = true;
    saveState();
  }

  // ───────────────────────── 对外 API ─────────────────────────
  window.RoleplayPet = {
    showBubble,
    hideBubble,
    send,
    say,
    isMuted: () => state.muted,
    isBusy: () => chatBusy,
    getState: () => state,
    setDot,
    playMotion: (name) => {
      // 语义动作入口：手势名/槽位名/情绪名/动画名统一交给 spine 解析
      window.RoleplaySpine && window.RoleplaySpine.playMotion(name);
      if (window.RoleplayPetCore) window.RoleplayPetCore.emitIntent("motion", { pose: name });
    },
    setEmotion: (emotion) => {
      window.RoleplaySpine && window.RoleplaySpine.emotion(emotion);
      if (window.RoleplayPetCore) window.RoleplayPetCore.emitIntent("emotion", { emotion });
    },
    notifyInteract: () => {
      noteActivity();
      if (api) api.notifyInteract();
    },
    getSpineModels,
    getSpineModel,
    switchSpineModel,
    cycleSpineModel,
    changeZoom,
    changeBubbleSize,
    setLocked,
    isLocked: () => state.locked,
    hasDesktop: () => !!api,
    // voice.js 识别完成钩子：识别文本自动作为对话发送
    onVoiceInput: (text) => {
      if (text) send(text);
    },
  };

  // ───────────────────────── 启动 ─────────────────────────
  window.addEventListener("DOMContentLoaded", () => {
    // 渲染器就绪事件：Spine 唯一渲染器广播 spine:init-done
    const onRendererReady = (ev) => {
      const d = (ev && ev.detail) || {};
      const loading = $("pet-loading");
      if (loading) loading.classList.add("hidden");
      if (d.ok) {
        // 切换成功时清掉上次失败留下的错误层，避免黑底覆盖窗口。
        const statusEl = $("pet-error");
        if (statusEl) {
          statusEl.hidden = true;
          statusEl.textContent = "";
        }
        if (!state.onboarded) startOnboarding(); // P0-3：首次启动引导
      } else {
        const statusEl = $("pet-error");
        if (statusEl && !statusEl.textContent) {
          statusEl.hidden = false;
          statusEl.textContent = "骨骼动画加载失败：" + (d.error || "未知错误");
        }
      }
    };
    window.addEventListener("spine:init-done", onRendererReady);

    initRenderer().then((ok) => {
      if (!ok) {
        const statusEl = $("pet-error");
        if (statusEl && !statusEl.textContent) {
          statusEl.hidden = false;
          statusEl.textContent = "骨骼动画加载失败，请检查 spine-player.js 与 .skel/.atlas 素材。";
        }
        const loading = $("pet-loading");
        if (loading) loading.classList.add("hidden");
      }
    });
    checkBackend();
    checkOllama();
    setInterval(checkOllama, 10000); // Ollama 状态每 10s 刷新
    setInterval(pushModelBounds, 1000); // 动画/表情引起的 bbox 变化低频同步给主进程
    applySpineMenuLabel(); // 骨骼动画菜单初始文案
    applyBubbleSize(); // 气泡大小恢复（写 --bubble-scale）
    applyMuteMenu(); // 菜单静音/取消静音初始文案与图标
    // P1：修饰态恢复（主进程 config 为权威持久化源）
    if (api && typeof api.getConfig === "function") {
      api.getConfig()
        .then((cfg) => {
          if (cfg && cfg.pet) {
            if (!!cfg.pet.dnd !== state.dnd) setDnd(!!cfg.pet.dnd);
            if (!!cfg.pet.locked !== state.locked) setLocked(!!cfg.pet.locked);
          }
        })
        .catch(() => {});
    } else {
      if (state.dnd) setDnd(true);
      if (state.locked) setLocked(true);
    }
  });

  // ───────────────────────── 新手引导滑层（P0-T8：5 步，替换旧气泡式） ─────────────────────────
  const onbEl = $("pet-onboarding");
  const ONB_STEPS = [
    { title: "拖我移动", desc: "按住我，拖到桌面任何角落。", pic: "拖拽手势示意" },
    { title: "右键看菜单", desc: "右键点我，说话、动作、识别屏幕都在这里。", pic: "右键菜单示意" },
    {
      title: api ? "按住 Alt+Space 说话" : "点底部 ✎ 打字",
      desc: api ? "按住快捷键，直接对我讲话。" : "点底部 ✎ 展开输入框，打字跟我聊天。",
      pic: "语音/输入示意",
    },
    { title: "识别屏幕", desc: "我可以看一眼你的屏幕，聊聊你在做什么。全程本地，不落盘。", pic: "屏幕识别示意" },
    { title: "设置抽屉", desc: "骨骼动画、声音、漫步频率，都在设置里。祝你与无名者相处愉快。", pic: "设置示意" },
  ];
  let onbIndex = 0;

  function renderOnbStep() {
    const s = ONB_STEPS[onbIndex];
    $("onb-title").textContent = s.title;
    $("onb-desc").textContent = s.desc;
    $("onb-pic").textContent = s.pic;
    const dots = $("onb-steps").querySelectorAll("span");
    dots.forEach((d, i) => d.classList.toggle("on", i === onbIndex));
    $("onb-prev").style.visibility = onbIndex === 0 ? "hidden" : "visible";
    $("onb-next").textContent = onbIndex === ONB_STEPS.length - 1 ? "完成" : "下一步";
  }
  function openOnboarding() {
    onbIndex = 0;
    renderOnbStep();
    onbEl.classList.add("open");
    flashUi(12000); // 引导期间 UI 保持可见
  }
  function finishOnboarding() {
    onbEl.classList.remove("open");
    state.onboarded = true;
    saveState();
    flashUi(1200);
  }
  function startOnboarding() {
    openOnboarding();
  }
  $("onb-next").addEventListener("click", () => {
    if (onbIndex < ONB_STEPS.length - 1) {
      onbIndex++;
      renderOnbStep();
    } else {
      finishOnboarding();
    }
  });
  $("onb-prev").addEventListener("click", () => {
    if (onbIndex > 0) {
      onbIndex--;
      renderOnbStep();
    }
  });
  $("onb-skip").addEventListener("click", finishOnboarding);
})();
