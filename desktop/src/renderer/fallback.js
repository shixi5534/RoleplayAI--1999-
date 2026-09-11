/*
 * fallback.js —— 后端引导页逻辑（仅此页使用，经 preload 的 petApi 与主进程通信）
 */
(function () {
  "use strict";
  const api = window.petApi;
  const $ = (id) => document.getElementById(id);
  const stateEl = $("state");
  const errEl = $("err");
  const dotEl = $("dot");
  const btnLaunch = $("btn-launch");
  const btnRetry = $("btn-retry");

  function render(s) {
    if (!s) return;
    dotEl.className = s.ok ? "ok" : "";
    if (s.ok) {
      stateEl.textContent = "后端已恢复，正在进入宠物…";
      btnLaunch.disabled = true;
      btnRetry.disabled = true;
      return;
    }
    btnLaunch.disabled = !!s.launching;
    btnRetry.disabled = !!s.launching;
    if (s.launching) {
      stateEl.textContent = "正在启动后端（最多等待 15s）…";
      errEl.hidden = true;
    } else if (s.error) {
      stateEl.textContent = "启动失败";
      errEl.textContent = s.error;
      errEl.hidden = false;
    } else {
      stateEl.textContent = "未检测到后端（127.0.0.1:" + (s.port || 8000) + "）";
      errEl.hidden = true;
    }
  }

  if (api) {
    api.onBackendState(render);
    btnLaunch.addEventListener("click", () => {
      render({ ok: false, launching: true });
      api.launchBackend().then(render);
    });
    btnRetry.addEventListener("click", () => {
      render({ ok: false, launching: false });
      api.launchBackend().then(render);
    });
    $("btn-quit").addEventListener("click", () => api.quit());
  } else {
    stateEl.textContent = "未检测到桌面壳（petApi 缺失）";
    btnLaunch.disabled = true;
    btnRetry.disabled = true;
  }
})();
