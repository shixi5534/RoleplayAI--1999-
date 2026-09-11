/*
 * pet-core.js —— 桌面宠物共享核心（Phase 3）
 *
 * 定位：Web 端（pet.html / index.html 聊天页）与 Electron 壳共用的一份
 * 「动作库 + 意图事件」约定。本模块只定义数据与事件，不触碰任何系统 API；
 * 具体渲染/窗口能力由各自壳适配。
 *
 * 数据格式借鉴 PetAI skin.json 的 states 结构，并兼容本项目 Spine 的
 * animation_map.json 的 slots 结构。
 */
(function (global) {
  "use strict";

  // 意图事件：壳之间只通过这些语义事件通信，不耦合具体实现。
  const INTENTS = Object.freeze({
    DRAG: "drag",
    CLICK: "click",
    MENU: "menu",
    MOTION: "motion",
    WALK: "walk",
    EMOTION: "emotion",
  });

  // 预设动作库（姿态名 → 动画名）。缺项一律回退 idle，支持中文姿态名。
  const DEFAULT_STATES = Object.freeze({
    idle: "idle",
    walk: "target",
    click: "djc1",
    emotion: "happy",
    listen: "cs2",
    rest: "x_ls_he_gai1",
  });

  /** PetAI skin.json `states` 结构 → 本模块统一结构（缺项回退 idle）。 */
  function normalizeStates(states, fallback) {
    const base = fallback || DEFAULT_STATES;
    const out = Object.assign({}, base);
    if (!states || typeof states !== "object") return out;
    Object.keys(states).forEach((k) => {
      const v = states[k];
      if (v && typeof v === "string") out[k] = v;
    });
    if (!out.idle) out.idle = DEFAULT_STATES.idle;
    return out;
  }

  /** 兼容本项目 Spine animation_map.json 的 `slots` 结构。 */
  function normalizeSlots(slots) {
    const out = { states: Object.assign({}, DEFAULT_STATES), slots: {} };
    if (!slots || typeof slots !== "object") return out;
    out.slots = slots;
    // 常用姿态优先取 slots 第一候选，缺失回退 idle。
    ["idle", "walk", "click", "emotion", "listen", "rest"].forEach((pose) => {
      const list = Array.isArray(slots[pose]) ? slots[pose] : [];
      if (list.length) out.states[pose] = list[0];
    });
    if (!out.states.idle) out.states.idle = DEFAULT_STATES.idle;
    return out;
  }

  /**
   * 姿态 → 动画名解析。
   * @param {Object} states 归一化后的 states
   * @param {string} pose 姿态名（支持中文别名）
   * @returns {string} 动画名，永远返回一个可用值
   */
  function resolveMotion(states, pose) {
    const map = (states && states.states) || states || DEFAULT_STATES;
    const key = String(pose || "").trim();
    return map[key] || map.idle || DEFAULT_STATES.idle;
  }

  /** 发出一个意图事件（detail 原样透传，不序列化、不依赖 DOM 之外的系统）。 */
  function emitIntent(name, detail) {
    if (typeof CustomEvent !== "function") return false;
    try {
      global.dispatchEvent(new CustomEvent("pet:intent:" + name, {
        detail: detail || {},
      }));
      return true;
    } catch (_) {
      return false;
    }
  }

  /** 订阅意图事件，返回取消函数。 */
  function onIntent(name, cb) {
    if (typeof cb !== "function") return () => {};
    const handler = (ev) => {
      try { cb(ev && ev.detail); } catch (_) { /* 意图订阅错误不冒泡 */ }
    };
    global.addEventListener("pet:intent:" + name, handler);
    return () => global.removeEventListener("pet:intent:" + name, handler);
  }

  global.RoleplayPetCore = Object.freeze({
    INTENTS,
    DEFAULT_STATES,
    normalizeStates,
    normalizeSlots,
    resolveMotion,
    emitIntent,
    onIntent,
  });
})(window);
