/*
 * rain.js —— 「暴雨」母题装饰:细线雨滴坠落(纯装饰,失败不影响主流程)。
 * 遵循项目 CSP 约束:script-src 'self',故独立成文件,不在 HTML 内联。
 * prefers-reduced-motion 时跳过(尊重系统减少动效偏好)。
 */
(function () {
  "use strict";
  try {
    var rain = document.getElementById("rain-layer");
    if (!rain) return;
    if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    var N = 18;
    var frag = document.createDocumentFragment();
    for (var i = 0; i < N; i++) {
      var drop = document.createElement("i");
      drop.style.left = (Math.random() * 100).toFixed(1) + "%";
      drop.style.animationDuration = (4 + Math.random() * 5).toFixed(1) + "s";
      drop.style.animationDelay = (-Math.random() * 8).toFixed(1) + "s";
      drop.style.opacity = (0.3 + Math.random() * 0.5).toFixed(2);
      frag.appendChild(drop);
    }
    rain.appendChild(frag);
  } catch (_) {
    /* 纯装饰层,任何异常都静默忽略 */
  }
})();
