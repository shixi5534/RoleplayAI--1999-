/* Live2D 引导：监听 init-done 事件，失败时展示可读错误与正确启动方式；兜底超时。
 * 独立为外部文件以符合 CSP script-src 'self'（禁止内联脚本）。
 */
(function () {
  var loading = document.getElementById("live2d-loading");
  var statusEl = document.getElementById("live2d-status");
  var fallbackTimer = setTimeout(function () {
    if (!loading || !statusEl) return;
    loading.classList.add("hidden");
    if (statusEl.hidden) {
      statusEl.hidden = false;
      statusEl.textContent = "Live2D 加载超时，请确认模型文件存在或改用 HTTP 服务器打开。";
    }
  }, 8000);

  // 静态提示（固定结构）可用 innerHTML；动态错误文本（来自异常/服务器，不可信）
  // 必须用 textContent 防 XSS 注入。
  function showStaticError(html) {
    clearTimeout(fallbackTimer);
    if (loading) loading.classList.add("hidden");
    if (statusEl) {
      statusEl.hidden = false;
      statusEl.innerHTML = html; // 仅用于固定结构的静态提示
    }
  }
  function showErrorText(prefix, errorText) {
    clearTimeout(fallbackTimer);
    if (loading) loading.classList.add("hidden");
    if (statusEl) {
      statusEl.hidden = false;
      statusEl.textContent = prefix + (errorText || "未知错误"); // 动态文本用 textContent 防注入
    }
  }

  window.addEventListener("live2d:init-done", function (ev) {
    var d = ev.detail || {};
    if (d.ok) {
      clearTimeout(fallbackTimer);
      if (loading) loading.classList.add("hidden");
      return;
    }
    if (location.protocol === "file:") {
      showStaticError(
        '⚠️ 当前是 <code>file://</code> 协议，浏览器禁止加载本地 Live2D 模型（fetch 被 CORS 阻止）。' +
        '<br>请改用 HTTP 服务器打开，例如：' +
        '<br><code>cd roleplay-ai &amp;&amp; python -m http.server 8000</code>' +
        '<br>然后访问 <code>http://localhost:8000/frontend/index.html</code>'
      );
    } else {
      showErrorText("Live2D 初始化失败：", d.error);
    }
  });
})();
