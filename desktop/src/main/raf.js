/*
 * raf.js —— 主进程帧循环垫片
 *
 * Electron 主进程是 Node 环境，没有浏览器 requestAnimationFrame。
 * 用 setTimeout(16ms) 模拟 60fps 帧循环，接口对齐 rAF：
 *   requestFrame(cb) → 句柄；cancelFrame(句柄) 取消。
 */
"use strict";

function requestFrame(cb) {
  return setTimeout(() => cb(Date.now()), 16);
}

function cancelFrame(id) {
  if (id) clearTimeout(id);
}

module.exports = { requestFrame, cancelFrame };
