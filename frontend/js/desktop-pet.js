/*
 * desktop-pet.js —— 网页版 ↔ 桌面宠物 桥接（顶栏「🖥️ 桌面宠物」按钮）
 *
 * 双通道唤起，互为兜底：
 *   通道 B（优先）：桌面端常驻回环 HTTP 服务（127.0.0.1:39231±）
 *     GET  /ping  → 探测是否在运行；POST /launch → 唤出
 *   通道 A（兜底）：自定义协议 roleplaypet://launch 唤起未运行的应用
 *
 * 本脚本与后端无关，纯前端；桌面端未安装时展示安装引导。
 * 隐私：全部请求仅指向 127.0.0.1，不访问任何外部地址。
 */
(function () {
  "use strict";

  const PROTOCOL_URL = "roleplaypet://launch";
  const BASE_PORT = 39231;
  const PROBE_PORTS = 21; // 39231 ~ 39251（与桌面端 control-server 自动 +1 上限对齐）

  const btn = document.getElementById("btn-desktop-pet");
  const dot = document.getElementById("pet-status-dot");
  if (!btn) return;

  function setDot(state) {
    if (!dot) return;
    dot.className = "pet-dot" + (state === "on" ? " on" : state === "off" ? " off" : "");
    dot.title = state === "on"
      ? "桌面宠物运行中 · 点击唤出"
      : state === "off"
        ? "未检测到桌面宠物（需安装 desktop/ 并启动）"
        : "桌面宠物状态未知";
  }

  // 探测结果缓存：悬停/加载共用，避免每次鼠标悬停都串行等 800ms×5（F8）
  let probeCache = { base: null, at: 0 };
  const PROBE_TTL_MS = 5000; // 缓存 5s；点击按钮时强制重探

  /** 探测可用端口（并发 Promise.all，与桌面端端口自动 +1 策略对齐），返回可用基址。 */
  async function probe(force) {
    if (!force && probeCache.base !== undefined && Date.now() - probeCache.at < PROBE_TTL_MS) {
      return probeCache.base;
    }
    const tasks = [];
    for (let i = 0; i < PROBE_PORTS; i++) {
      const base = "http://127.0.0.1:" + (BASE_PORT + i);
      tasks.push(
        new Promise((resolve) => {
          const ctrl = new AbortController();
          const t = setTimeout(() => ctrl.abort(), 800);
          fetch(base + "/ping", { signal: ctrl.signal, cache: "no-store" })
            .then((resp) => {
              resolve(resp.ok ? base : null);
            })
            .catch(() => resolve(null))
            .finally(() => clearTimeout(t)); // 失败路径也清理定时器（旧实现 catch 里漏清）
        })
      );
    }
    const results = await Promise.all(tasks);
    const base = results.find((b) => b) || null;
    probeCache = { base, at: Date.now() };
    return base;
  }

  /** 通道 A：协议唤起（隐藏 iframe 优先，避免导航走当前聊天页）。 */
  function triggerProtocol() {
    try {
      const iframe = document.createElement("iframe");
      iframe.style.display = "none";
      iframe.src = PROTOCOL_URL;
      document.body.appendChild(iframe);
      setTimeout(() => { try { iframe.remove(); } catch (_) {} }, 1500);
    } catch (_) {}
  }

  /** 后端已拉起/协议已触发后，轮询等待桌面端控制服务真正可用（最多约 10s）。 */
  async function waitForDesktop(maxTries, intervalMs) {
    for (let i = 0; i < maxTries; i++) {
      const base = await probe(true);
      if (base) return base;
      await new Promise((r) => setTimeout(r, intervalMs));
    }
    return null;
  }

  // 复查定时器去重（F8）：连点按钮时只保留一个复查，避免弹出多个安装引导 confirm
  let recheckTimer = null;
  async function launch() {
    // 关键：自定义协议必须在任何 await 之前同步触发，否则 Chrome 会因用户手势失效而拦截。
    // 每次点击都直接触发协议，保证“网页点击即唤起”；若回环服务可用，随后再走 /launch 置顶/唤醒。
    triggerProtocol();

    // 通道 B：已运行 → 唤出（点击按钮强制重探，避免旧缓存误判）
    const base = await probe(true);
    if (base) {
      setDot("on");
      try {
        await fetch(base + "/launch", { method: "POST" });
      } catch (_) {}
      return;
    }

    setDot("off");

    // 通道 C：本地后端兜底拉起（开发态/协议未注册时可靠）
    let backendOk = false;
    try {
      const r = await fetch("/api/desktop-pet/launch", { method: "POST" });
      if (r.ok) {
        const j = await r.json().catch(() => ({}));
        backendOk = !!(j && j.ok);
      }
    } catch (_) {}

    // 后端已尝试拉起：给 Electron 启动留更长时间复查（轮询 8~10s，避免启动慢被误报“未安装”）
    const retryMs = backendOk ? 1500 : 1200;
    if (recheckTimer) return;
    recheckTimer = setTimeout(async () => {
      recheckTimer = null;
      const base2 = backendOk
        ? await waitForDesktop(9, 1000) // 最多再等 ~9s
        : await waitForDesktop(3, 1000); // 协议可能已拉起，短等 3s
      if (base2) {
        setDot("on");
        try { await fetch(base2 + "/launch", { method: "POST" }); } catch (_) {}
        return;
      }
      showInstallHint();
    }, retryMs);
  }

  function showInstallHint() {
    const ok = window.confirm(
      "未检测到桌面宠物正在运行。\n\n" +
      "桌面宠物是网页版的附属形态（Electron 悬浮窗），\n" +
      "安装与启动方法：\n" +
      "1. cd roleplay-ai/desktop && npm install && npm start\n" +
      "2. 打包安装：npm run dist（NSIS 安装包，随后可用协议唤起）\n\n" +
      "现在前往使用说明？"
    );
    if (ok) window.open("./docs/DESKTOP_PET_DESIGN.md", "_blank");
  }

  btn.addEventListener("click", () => {
    setDot("");
    launch();
  });

  // P2-5：悬停弹出宠物状态小卡（文本态；缩略图需桌面端截图接口，暂为状态文案）
  let cardEl = null;
  function ensureCard() {
    if (cardEl) return cardEl;
    cardEl = document.createElement("div");
    cardEl.style.cssText =
      "position:fixed;z-index:9999;display:none;max-width:260px;" +
      "background:rgba(16,22,28,0.96);border:1px solid rgba(201,168,106,0.28);" +
      "border-radius:8px;padding:10px 12px;font-size:12px;line-height:1.6;" +
      "color:#e8e2d4;box-shadow:0 10px 32px rgba(0,0,0,0.55);font-family:Georgia,'Songti SC',serif;";
    document.body.appendChild(cardEl);
    return cardEl;
  }
  btn.addEventListener("mouseenter", async () => {
    const base = await probe();
    const card = ensureCard();
    if (base) {
      try {
        const r = await fetch(base + "/state");
        const s = await r.json();
        card.innerHTML =
          "<div style='color:#c9a86a;letter-spacing:0.2em;margin-bottom:4px'>无名者 · 桌面宠物</div>" +
          "<div>● 运行中（v" + (s.version || "0.1.0") + "）</div>" +
          "<div style='color:#9a968a'>" + escText(s.hint || "") + "</div>";
      } catch (_) {
        card.innerHTML = "运行中";
      }
    } else {
      card.innerHTML =
        "<div style='color:#c9a86a;letter-spacing:0.2em;margin-bottom:4px'>无名者 · 桌面宠物</div>" +
        "<div style='color:#c96a6a'>● 未运行</div>" +
        "<div style='color:#9a968a'>点击按钮唤起；未安装请先运行 desktop 目录（npm start / 安装包）。</div>";
    }
    const r = btn.getBoundingClientRect();
    card.style.display = "block";
    card.style.left = Math.max(8, Math.min(r.left, window.innerWidth - 270)) + "px";
    card.style.top = r.bottom + 8 + "px";
  });
  btn.addEventListener("mouseleave", () => {
    if (cardEl) cardEl.style.display = "none";
  });
  function escText(s) {
    const d = document.createElement("div");
    d.textContent = s == null ? "" : String(s);
    return d.innerHTML;
  }

  // 页面加载时静默探测一次，展示状态点
  probe().then((base) => setDot(base ? "on" : "off"));
})();
