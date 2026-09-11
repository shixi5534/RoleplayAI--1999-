/* ============================================================
   布局交互模块:分栏拖拽 / HUD 折叠 / 窄屏侧边抽屉
   ------------------------------------------------------------
   设计原则:
   1) 纯增量——不修改任何现有 JS,只新增行为;CSS 类名与 id 全部沿用约定
   2) 舞台宽度写入 CSS 变量 --stage-w,由 css/index.css 的栅格消费
   3) 拖拽后 Live2D 自动重算:依赖 js/live2d.js 的 ResizeObserver(阶段1)
   4) 所有 localStorage 访问都包 try/catch(隐私模式下不抛错)
   5) HUD 折叠只给容器加 class,不动内部 .hud-chip 结构
      (js/chat.js 的 closest(".hud-chip") 依赖该结构)
   ============================================================ */
(function (global) {
  "use strict";
  var doc = global.document;
  var LS_SPLIT = "roleplay_layout_split";   // 独立 key,不污染 roleplay_ui_state
  var LS_HUD = "roleplay_layout_hud";

  var MIN_PCT = 24;   // 舞台最小宽度占比
  var MAX_PCT = 72;   // 舞台最大宽度占比
  var DEFAULT_PCT = 38;

  function ready(fn) {
    if (doc.readyState === "loading") doc.addEventListener("DOMContentLoaded", fn);
    else fn();
  }

  function lsGet(key) {
    try { return global.localStorage.getItem(key); } catch (_) { return null; }
  }
  function lsSet(key, val) {
    try { global.localStorage.setItem(key, val); } catch (_) { /* 隐私模式忽略 */ }
  }
  function lsDel(key) {
    try { global.localStorage.removeItem(key); } catch (_) {}
  }

  /* ── 1. 舞台 / 聊天 分栏可拖拽 ───────────────────────────── */
  function initSplitter() {
    var app = doc.getElementById("app");
    var sp = doc.getElementById("splitter");
    if (!app || !sp) return;

    function applySplit(pct) {
      var v = parseFloat(pct);
      if (!isFinite(v)) return;
      if (v < MIN_PCT) v = MIN_PCT;
      if (v > MAX_PCT) v = MAX_PCT;
      app.style.setProperty("--stage-w", v.toFixed(2) + "%");
    }

    // 恢复上次比例
    var saved = lsGet(LS_SPLIT);
    if (saved !== null && saved !== "") applySplit(saved);

    var dragging = false;
    function onDown(e) {
      dragging = true;
      sp.classList.add("dragging");
      doc.body.classList.add("splitting");
      if (e.pointerId !== undefined && sp.setPointerCapture) {
        try { sp.setPointerCapture(e.pointerId); } catch (_) {}
      }
      if (e.preventDefault) e.preventDefault();
    }
    function onMove(e) {
      if (!dragging) return;
      var r = app.getBoundingClientRect();
      if (!r.width) return;
      applySplit(((e.clientX - r.left) / r.width) * 100);
    }
    function onUp() {
      if (!dragging) return;
      dragging = false;
      sp.classList.remove("dragging");
      doc.body.classList.remove("splitting");
      var cur = app.style.getPropertyValue("--stage-w");
      if (cur) lsSet(LS_SPLIT, parseFloat(cur));
    }

    sp.addEventListener("pointerdown", onDown);
    global.addEventListener("pointermove", onMove);
    global.addEventListener("pointerup", onUp);
    global.addEventListener("pointercancel", onUp);

    // 双击复位
    sp.addEventListener("dblclick", function () {
      app.style.removeProperty("--stage-w");
      lsDel(LS_SPLIT);
    });

    // 键盘可达性:左右方向键微调
    sp.addEventListener("keydown", function (e) {
      var cur = parseFloat(app.style.getPropertyValue("--stage-w")) || DEFAULT_PCT;
      if (e.key === "ArrowLeft") { applySplit(cur - 2); e.preventDefault(); }
      else if (e.key === "ArrowRight") { applySplit(cur + 2); e.preventDefault(); }
    });
  }

  /* ── 2. HUD 变量面板可折叠 ─────────────────────────────── */
  function initHud() {
    var hud = doc.getElementById("stage-hud");
    var btn = doc.getElementById("hud-toggle");
    if (!hud || !btn) return;

    var collapsed = lsGet(LS_HUD) === "1";
    function apply() {
      hud.classList.toggle("hud-collapsed", collapsed);
      btn.setAttribute("aria-expanded", collapsed ? "false" : "true");
    }
    apply();

    btn.addEventListener("click", function (e) {
      // 阻止冒泡:避免被舞台的指针逻辑误判为互动
      if (e.stopPropagation) e.stopPropagation();
      collapsed = !collapsed;
      apply();
      lsSet(LS_HUD, collapsed ? "1" : "0");
    });
  }

  /* ── 3. 窄屏侧边抽屉 ───────────────────────────────────── */
  function initDrawer() {
    var btn = doc.getElementById("btn-menu");
    var nav = doc.getElementById("topbar-nav");
    if (!btn || !nav) return;

    function setOpen(open) {
      doc.body.classList.toggle("drawer-open", open);
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    }

    btn.addEventListener("click", function (e) {
      if (e.stopPropagation) e.stopPropagation();
      setOpen(!doc.body.classList.contains("drawer-open"));
    });

    // 点击抽屉内任一按钮后自动收起(保持原有按钮行为不变)
    nav.addEventListener("click", function (e) {
      var t = e.target;
      if (t && t.closest && t.closest("button")) setOpen(false);
    });

    // Esc 关闭。注意:knowledge.js 以 capture 方式监听 Esc 并 stopPropagation,
    // 因此弹层打开时 Esc 只关弹层,不会误关抽屉——层级符合预期。
    doc.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && doc.body.classList.contains("drawer-open")) setOpen(false);
    });

    // 视口变宽(回到桌面断点)时自动收起,避免残留遮罩
    global.addEventListener("resize", function () {
      if (global.innerWidth >= 860) setOpen(false);
    });
  }

  ready(function () {
    initSplitter();
    initHud();
    initDrawer();
    if (global.console && global.console.info) {
      global.console.info("[layout] 布局交互已初始化(分栏/HUD/抽屉)");
    }
  });

  global.RoleplayLayout = { splitter: initSplitter, hud: initHud, drawer: initDrawer };
})(window);
