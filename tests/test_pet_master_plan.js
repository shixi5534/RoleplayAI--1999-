/*
 * test_pet_master_plan.js —— 桌面宠物重构（P0–P4）无头冒烟测试
 *
 * 运行：node tests/test_pet_master_plan.js
 *
 * 覆盖：
 *   1. 静态质量门：pet.html 移除 Live2D 运行时、方向 C token、非穿透 hover 范式；
 *   2. pet-core.js 共享动作库/意图事件单元测试；
 *   3. 用最小 DOM mock 加载 pet.js，验证：
 *      - 历史 localStorage renderer=live2d 强制迁移为 spine；
 *      - DOMContentLoaded 后 Spine 唯一渲染器启动成功；
 *      - 点击产生反馈层 + Spine click + click 意图事件；
 *      - 拖拽 delta 经 petApi.moveBy 转发（AHaldner 范式）。
 */
"use strict";

const fs = require("fs");
const path = require("path");
const vm = require("vm");
const assert = require("assert");

const ROOT = path.resolve(__dirname, "..");
const FRONTEND = path.join(ROOT, "frontend");
const DESKTOP = path.join(ROOT, "desktop");

function read(rel) {
  return fs.readFileSync(path.join(ROOT, rel), "utf8");
}

// ───────────────────────── 1. 静态质量门 ─────────────────────────
function staticChecks() {
  const petHtml = read("frontend/pet.html");
  const petJs = read("frontend/js/pet.js");
  const spineJs = read("frontend/js/spine.js");
  const windowsJs = read("desktop/src/main/windows.js");
  const indexJs = read("desktop/src/main/index.js");
  const preloadJs = read("desktop/src/preload/pet.js");
  const checks = [
    ["pet.html 不加载 Live2D 运行时", !/assets\/lib\/live2d|js\/live2d\.js|live2d-bootstrap\.js/.test(petHtml)],
    ["pet.html 加载 Spine-only 脚本", /spine-player\.js/.test(petHtml) && /js\/spine\.js/.test(petHtml) && !/js\/live2d\.js/.test(petHtml)],
    ["pet.html 移除 Live2D「切换模型」菜单", !petHtml.includes('data-act="renderer"')],
    ["pet.html 含骨骼动画切换菜单", petHtml.includes('data-act="spine"') && petHtml.includes('id="menu-spine-label"')],
    ["pet.html 含模型/气泡大小与锁位菜单", ["zoom-in", "zoom-out", "bubble-bigger", "bubble-smaller", "lock"].every((a) => petHtml.includes(`data-act="${a}"`)) && petHtml.includes("--bubble-scale")],
    ["pet.html 应用方向 C token", ["#0E1116", "#7F77DD", "#1D9E75", "#D4537E", "#EDEDED"].every((c) => petHtml.includes(c))],
    ["pet.html 含点击反馈层", petHtml.includes('id="pet-feedback"') && petHtml.includes("fx-ripple") && petHtml.includes("pet-pulse")],
    ["pet.html 无重复 id=pet-status", (petHtml.match(/id="pet-status"/g) || []).length === 1],
    ["pet.html 全文档无重复 id", (() => {
      const ids = [...petHtml.matchAll(/id="([^"]+)"/g)].map((m) => m[1]);
      return new Set(ids).size === ids.length;
    })()],
    ["pet.html 含共享 pet-core", /shared\/pet-core\.js/.test(petHtml)],
    ["pet.js 无 RoleplayLive2D 调用", !petJs.includes("RoleplayLive2D")],
    ["pet.js 无 initLive2D 残留", !petJs.includes("initLive2D")],
    ["pet.js 启动迁移强制 Spine", /renderer !== "spine"[\s\S]*renderer = "spine"/.test(petJs)],
    ["pet.js 无 setInteractive 旧穿透链路", !petJs.includes("setInteractive")],
    ["pet.js 含骨骼模型状态与切换函数", petJs.includes('spine_model: "314701_s"') && petJs.includes("async function switchSpineModel") && petJs.includes("function cycleSpineModel")],
    ["pet.js 含模型/气泡大小与锁位功能", petJs.includes("function changeZoom") && petJs.includes("function changeBubbleSize") && petJs.includes("function setLocked") && petJs.includes("bubble_size: 1.0")],
    ["pet.js 切换有防抖与会话隔离", petJs.includes("spineSwitchBusy") && petJs.includes("spineSwitchPending") && spineJs.includes("_session += 1") && spineJs.includes("session !== self._session")],
    ["spine.js setZoom 支持 0.5–2.0", spineJs.includes("Math.max(0.5, Math.min(2.0")],
    ["spine.js 注册 314701/314701_s/314702 三个模型", spineJs.includes('id: "314701_s"') && spineJs.includes('id: "314701"') && spineJs.includes('id: "314702"') && spineJs.includes("getModels()")],
    ["spine 素材文件齐全", ["314701_wmz_s_room.skel", "314701_wmz_room.skel", "314702_wmz_room.skel", "314701_wmz.atlas", "314702_wmz.atlas", "314701_wmz.png", "314702_wmz.png"].every((f) => fs.existsSync(path.join(FRONTEND, "assets", "spine", f)))],
    ["spine.js getBounds 按 fitScale 校正", /_natW[\s\S]*getBounds/.test(spineJs) && spineJs.includes("padX")],
    ["spine.js 修正 spine-player 4.2 loadAssets 签名", /loadAssets:\s*\(app\)/.test(spineJs) && spineJs.includes("app.assetManager.loadBinary") && spineJs.includes("app.assetManager.loadTextureAtlas")],
    // 注：原断言绑定了注释文本 `// 起待机池`，spine.js 重构后注释改为
    // `// 重置后回到待机池`，行为未变（仍为 this.idle()，无 this._idle() 残留）。
    // 断言回归到行为本身，避免再次因注释措辞漂移误报。
    ["spine.js 修正 idle 调用（无 _idle 残留）", /this\.idle\(\);/.test(spineJs) && !spineJs.includes("this._idle()")],
    ["spine.js 传入 Physics.update（无 physics undefined）", spineJs.includes("global.spine.Physics.update") && spineJs.includes("updateWorldTransform(physics)")],
    ["spine.js 待机槽有兜底且循环播放（不再静止）", spineJs.includes("_validAnimations(\"idle\")") && spineJs.includes("_playSlot(\"idle_pool\", { loop: true })") && spineJs.includes("avail.length <= 1")],
    // 注：原断言要求「逐帧按 AABB 动态取景」，但 spine.js 已刻意改为「稳定相机
    // 锚定 setup pose + 全动画包络盒缩放 _fit()」——旧实现每帧重算 AABB 会导致
    // 模型平移抖动与边缘裁剪。断言同步到新设计：相机锚定 setup pose（非 -this._h/2
    // 旧式硬编码），且 _fit() 用包络 reach/up 保证任何姿态不超出画布。
    ["spine.js 稳定相机锚定 setup pose + 包络盒缩放（不再压到屏幕外）",
      spineJs.includes("cam.position.y = this._setupBottom * s + this._h / 2 - this._groundMargin") &&
      !spineJs.includes("cam.position.y = -this._h / 2") &&
      spineJs.includes("_envReachX") && spineJs.includes("_envUp")],
    ["pet.html 错误层 hidden 时 display:none（防全窗黑底）", /\.pet-error\[hidden\]\s*\{\s*display:\s*none/.test(petHtml)],
    ["windows.js 含 startHoverWatch + 90ms 轮询", /startHoverWatch/.test(windowsJs) && /90/.test(windowsJs) && /pet:hover-state/.test(windowsJs)],
    ["windows.js 含窗口尺寸看门狗与 zoom 复位", windowsJs.includes("startSizeWatchdog") && windowsJs.includes("setZoomFactor(1)") && windowsJs.includes("cfg.pet.width")],
    ["pet.js 屏蔽触屏/快捷键页面缩放", petJs.includes("gesturestart") && petJs.includes("e.ctrlKey") && petJs.includes('"0"')],
    ["windows.js 无 setIgnoreMouseEvents 调用", !/setIgnoreMouseEvents\s*\(/.test(windowsJs)],
    ["index.js 无 setIgnoreMouseEvents 调用", !/setIgnoreMouseEvents\s*\(/.test(indexJs)],
    ["preload 提供 onHoverState 且移除 setInteractive", /onHoverState/.test(preloadJs) && !preloadJs.includes("setInteractive")],
    ["index.html 同源共享 pet-core", read("frontend/index.html").includes("shared/pet-core.js")],
    ["smoke_render 覆盖三模型/气泡/大小/锁位/连点", (() => {
      const s = read("desktop/scripts/smoke_render.js");
      return ["314701_s", "314701", "314702"].every((id) => s.includes(id)) &&
        s.includes("switchSpineModel") && s.includes("CHAT_AND_SIZE") && s.includes("RAPID_SWITCH") &&
        s.includes("LONG_PRESS");
    })()],
  ];
  let failed = 0;
  for (const [name, ok] of checks) {
    console.log((ok ? "  PASS  " : "  FAIL  ") + name);
    if (!ok) failed++;
  }
  assert.strictEqual(failed, 0, failed + " 个静态检查未通过");
}

// ───────────────────────── 2. pet-core 单元测试 ─────────────────────────
function testPetCore() {
  const events = [];
  const global = {
    dispatchEvent(ev) { events.push([ev.type, ev.detail]); return true; },
    addEventListener() {},
    removeEventListener() {},
  };
  global.window = global;
  global.CustomEvent = class {
    constructor(type, init) { this.type = type; this.detail = (init && init.detail) || {}; }
  };
  vm.runInNewContext(read("frontend/shared/pet-core.js"), global);
  const core = global.RoleplayPetCore;
  assert(core, "RoleplayPetCore 未暴露");

  assert.strictEqual(
    JSON.stringify(core.normalizeStates({ idle: "a", click: "b", 中文: "c" })),
    JSON.stringify({ idle: "a", walk: "target", click: "b", emotion: "happy", listen: "cs2", rest: "x_ls_he_gai1", 中文: "c" }),
    "normalizeStates 应补默认态并保留中文姿态"
  );
  assert.strictEqual(core.resolveMotion(core.normalizeStates({}), "click"), "djc1");
  assert.strictEqual(core.resolveMotion(core.normalizeStates({}), "不存在"), "idle");
  assert.strictEqual(core.resolveMotion(core.normalizeSlots({ walk: ["target", "target2"] }), "walk"), "target");
  assert.strictEqual(core.emitIntent("click", { x: 1 }), true);
  assert.strictEqual(JSON.stringify(events[0]), JSON.stringify(["pet:intent:click", { x: 1 }]));
  console.log("  PASS  pet-core 动作库归一化/回退/意图事件");
}

// ───────────────────────── 3. pet.js DOM mock 冒烟 ─────────────────────────
class FakeClassList {
  constructor() { this.set = new Set(); }
  add(...names) { names.forEach((n) => this.set.add(String(n))); }
  remove(...names) { names.forEach((n) => this.set.delete(String(n))); }
  contains(name) { return this.set.has(name); }
  toggle(name, force) {
    if (force === undefined) { this.set.has(name) ? this.set.delete(name) : this.set.add(name); }
    else if (force) this.set.add(name); else this.set.delete(name);
    return this.set.has(name);
  }
}

class FakeElement {
  constructor(tagName) {
    this.tagName = String(tagName || "div").toUpperCase();
    this.classList = new FakeClassList();
    this.style = { setProperty() {}, removeProperty() {} };
    this._attrs = {};
    this.children = [];
    this.parentElement = null;
    this.textContent = "";
    this.innerHTML = "";
    this.hidden = false;
    this.value = "";
    this.dataset = {};
    this.offsetWidth = 172;
    this.offsetHeight = 300;
    this.clientWidth = 320;
    this.clientHeight = 420;
    this._handlers = {};
  }
  appendChild(c) { this.children.push(c); c.parentElement = this; return c; }
  removeChild(c) { const i = this.children.indexOf(c); if (i >= 0) this.children.splice(i, 1); c.parentElement = null; return c; }
  addEventListener(type, fn) { (this._handlers[type] = this._handlers[type] || []).push(fn); }
  removeEventListener() {}
  dispatchEvent(ev) {
    ev.target = ev.target || this;
    (this._handlers[ev.type] || []).forEach((fn) => fn(ev));
    return true;
  }
  querySelectorAll() { return []; }
  querySelector() { return null; }
  contains(node) {
    if (node === this) return true;
    return this.children.some((c) => c.contains && c.contains(node));
  }
  remove() {
    if (this.parentElement) this.parentElement.removeChild(this);
  }
  setPointerCapture() {}
  releasePointerCapture() {}
  setAttribute(k, v) { this._attrs[k] = String(v); }
  getAttribute(k) { return this._attrs[k]; }
  focus() {}
  blur() {}
  closest() { return null; }
  before() {}
  getContext() { return null; }
}

class FakeEvent {
  constructor(type, init) {
    this.type = type;
    init = init || {};
    this.detail = init.detail;
    this.target = init.target || null;
    this.relatedTarget = init.relatedTarget === undefined ? null : init.relatedTarget;
    this.button = init.button === undefined ? 0 : init.button;
    this.clientX = init.clientX || 0;
    this.clientY = init.clientY || 0;
    this.screenX = init.screenX === undefined ? (init.clientX || 0) : init.screenX;
    this.screenY = init.screenY === undefined ? (init.clientY || 0) : init.screenY;
    this.pointerId = init.pointerId === undefined ? 1 : init.pointerId;
    this.key = init.key || "";
    this.ctrlKey = !!init.ctrlKey;
    this.metaKey = !!init.metaKey;
    this.altKey = !!init.altKey;
  }
  preventDefault() {}
  stopPropagation() {}
}

function makeDom() {
  const elements = {};
  const getById = (id) => {
    if (!elements[id]) elements[id] = new FakeElement("div");
    return elements[id];
  };
  const document = {
    body: new FakeElement("body"),
    documentElement: new FakeElement("html"),
    visibilityState: "visible",
    _handlers: {},
    getElementById: getById,
    createElement: (tag) => new FakeElement(tag),
    createTextNode: (text) => {
      const t = new FakeElement("#text");
      t.textContent = String(text);
      return t;
    },
    addEventListener(type, fn) { (this._handlers[type] = this._handlers[type] || []).push(fn); },
    removeEventListener() {},
    fire(type, init) {
      const ev = new FakeEvent(type, init);
      (this._handlers[type] || []).forEach((fn) => fn(ev));
      return ev;
    },
  };
  return { document, elements, getById };
}

function loadPetPage() {
  const { document, getById } = makeDom();
  const storage = new Map();
  // 模拟历史 Live2D 残留：应被 P0 启动迁移重置。
  storage.set("roleplay_pet_state", JSON.stringify({ renderer: "live2d", model_id: "314702" }));

  const spineCalls = { click: 0, emotion: [] };
  const apiCalls = { moveBy: [], notifyInteract: 0, busy: [] };
  const windowListeners = {};
  const window = {
    document,
    localStorage: {
      getItem: (k) => (storage.has(k) ? storage.get(k) : null),
      setItem: (k, v) => storage.set(k, String(v)),
      removeItem: (k) => storage.delete(k),
    },
    navigator: {},
    console,
    setTimeout,
    clearTimeout,
    setInterval,
    clearInterval,
    fetch: async () => ({ ok: false }),
    CustomEvent: class {
      constructor(type, init) { this.type = type; this.detail = (init && init.detail) || {}; }
    },
    dispatchEvent() { return true; },
    addEventListener(type, fn) { (windowListeners[type] = windowListeners[type] || []).push(fn); },
    removeEventListener() {},
    __lastMouse: null,
    innerWidth: 320,
    innerHeight: 420,
    petApi: {
      onHoverState(cb) { window._hoverCb = cb; return () => {}; },
      onWalk(cb) { return () => {}; },
      onPtt(cb) { return () => {}; },
      onTalk(cb) { return () => {}; },
      onWake(cb) { return () => {}; },
      onBackendState(cb) { return () => {}; },
      onScreenText(cb) { return () => {}; },
      moveBy(dx, dy) { apiCalls.moveBy.push([dx, dy]); },
      dragEnd() {},
      notifyInteract() { apiCalls.notifyInteract++; },
      setBusy(v) { apiCalls.busy.push(v); },
      setSize() {},
      setDnd() {},
      setLocked() {},
      captureScreen() {},
      getConfig: async () => ({ pet: { dnd: false, locked: false, width: 320, height: 420 } }),
      setConfig: async () => ({}),
      getDisplays: async () => [],
      exportImage: async () => ({ ok: false, canceled: true }),
      quit() {},
      openSettings() {},
    },
    RoleplaySpine: {
      async init() { return true; },
      setZoom() {},
      enter() {},
      click() { spineCalls.click++; },
      emotion(tag) { spineCalls.emotion.push(tag); },
      sleep() {},
      walk() {},
      stopWalk() {},
      getBounds() { return { left: 0, top: 0, width: 100, height: 200 }; },
      destroy() {},
    },
    RoleplayChat: { send: async () => ({ full: "", saw: false }) },
    RoleplayVoice: { isRecording: () => false, startRecording() {}, stopRecording() {}, speak() {}, stopSpeaking() {} },
  };
  window.window = window;
  window._listeners = windowListeners;

  const context = vm.createContext(window);
  vm.runInContext(read("frontend/shared/pet-core.js"), context, { filename: "pet-core.js" });
  vm.runInContext(read("frontend/js/pet.js"), context, { filename: "pet.js" });

  // pet.js 监听的是 window.DOMContentLoaded。
  (windowListeners["DOMContentLoaded"] || []).forEach((fn) => fn(new FakeEvent("DOMContentLoaded", {})));
  document.fire("DOMContentLoaded", {});
  document.fire("mousemove", { clientX: 160, clientY: 210 });

  // 点击：pointerdown + pointerup（screen/client 坐标不动 → 判定为 click）
  const canvas = getById("pet-canvas");
  const pointerId = 7;
  document.fire("pointerdown", { target: canvas, pointerId, button: 0, clientX: 150, clientY: 200, screenX: 150, screenY: 200 });
  document.fire("pointerup", { target: canvas, pointerId, button: 0, clientX: 150, clientY: 200, screenX: 150, screenY: 200 });

  // 拖拽：screen 坐标移动 > 5px → moveBy 转发
  document.fire("pointerdown", { target: canvas, pointerId: 8, button: 0, clientX: 100, clientY: 100, screenX: 100, screenY: 100 });
  document.fire("pointermove", { target: canvas, pointerId: 8, button: 0, clientX: 118, clientY: 104, screenX: 118, screenY: 104 });
  document.fire("pointerup", { target: canvas, pointerId: 8, button: 0, clientX: 118, clientY: 104, screenX: 118, screenY: 104 });

  return { document, window, storage, getById, spineCalls, apiCalls };
}

async function testPetJs() {
  const { document, window, storage, getById, spineCalls, apiCalls } = loadPetPage();

  // 等 initRenderer 的 Promise 完成。
  await new Promise((r) => setImmediate(r));
  await new Promise((r) => setImmediate(r));

  const saved = JSON.parse(storage.get("roleplay_pet_state"));
  assert.strictEqual(saved.renderer, "spine", "历史 renderer=live2d 应迁移为 spine");
  assert.ok(!("model_id" in saved), "历史 model_id 应被清理");
  assert.ok(window.RoleplayPet, "RoleplayPet 未暴露");
  assert.strictEqual(window.RoleplayPet.getState().renderer, "spine");

  // hover UI：mousemove 后应出现 ui-visible
  assert.ok(document.body.classList.contains("ui-visible"), "mousemove 后应显示极简 UI");

  // 点击反馈：ripple + 粒子 + Spine click + 意图事件
  const feedback = getById("pet-feedback");
  assert.ok(feedback.children.length >= 2, "点击应产生 ripple + 粒子（实际 " + feedback.children.length + "）");
  assert.ok(document.body.classList.contains("pet-ui"), "点击交互应短暂唤出 UI");
  assert.strictEqual(spineCalls.click, 1, "单击应触发一次 RoleplaySpine.click");

  // 拖拽：delta 应经 moveBy 转发（>5px 后累计增量 18/4）
  assert.ok(apiCalls.moveBy.length >= 1, "拖拽应经 petApi.moveBy 转发");
  const [dx, dy] = apiCalls.moveBy[apiCalls.moveBy.length - 1];
  assert.strictEqual(dx, 18, "拖拽 dx 应为 screen delta");
  assert.strictEqual(dy, 4, "拖拽 dy 应为 screen delta");
  assert.ok(apiCalls.notifyInteract >= 1, "拖拽应通知主进程互动");

  // 模拟 Spine ready：onboarding 能正常打开（说明错误分支无残留）
  const beforeOnb = getById("pet-onboarding").classList.contains("open");
  ((window._listeners && window._listeners["spine:init-done"]) || []).forEach((fn) =>
    fn(new FakeEvent("spine:init-done", { detail: { ok: true } }))
  );
  assert.ok(beforeOnb || getById("pet-onboarding").classList.contains("open"), "spine:init-done 后引导层应打开");

  // 拖拽锁位尝试不泄漏：locked 状态下 moveBy 不应继续转发（P1-4）
  const apiBefore = apiCalls.moveBy.length;
  window.RoleplayPet.getState().locked = true;
  document.fire("pointerdown", { target: getById("pet-canvas"), pointerId: 9, button: 0, clientX: 10, clientY: 10, screenX: 10, screenY: 10 });
  document.fire("pointermove", { target: getById("pet-canvas"), pointerId: 9, button: 0, clientX: 60, clientY: 60, screenX: 60, screenY: 60 });
  assert.strictEqual(apiCalls.moveBy.length, apiBefore, "锁位时不应继续转发 moveBy");

  console.log("  PASS  pet.js 启动迁移 / Spine 启动 / hover UI / 点击反馈 / 拖拽 delta / 锁位守卫");
}

async function main() {
  console.log("[1/3] 静态质量门");
  staticChecks();
  console.log("[2/3] pet-core 共享模块");
  testPetCore();
  console.log("[3/3] pet.js DOM mock 冒烟");
  await testPetJs();
  console.log("\nALL TESTS PASSED");
}

main().then(() => {
  process.exit(0); // pet.js 会注册真实 setInterval，测试完成后显式退出。
}).catch((e) => {
  console.error("\nTEST FAILED:", e && e.stack ? e.stack : e);
  process.exit(1);
});
