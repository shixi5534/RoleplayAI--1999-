/*
 * physics.js —— 窗口拖拽动量/回弹物理（P2）
 *
 * 渲染层拖拽期间高频发来 pet:move-by 增量；这里维护最近 ~150ms 的速度样本。
 * pet:drag-end 时启动动量循环：摩擦衰减 + 屏幕边缘阻尼反弹 + 停止（贴边）。
 * 纯函数式设计，便于单测。
 */
"use strict";

const { screen } = require("electron");
const { requestFrame, cancelFrame } = require("./raf"); // 主进程无 requestAnimationFrame，用垫片

/** 创建物理状态机。 */
function createPhysics(win) {
  const samples = []; // {t, dx, dy}
  let running = false;
  let vx = 0;
  let vy = 0;
  let raf = null;

  const FRICTION = 0.92;   // 每帧摩擦系数
  const BOUNCE = 0.45;     // 撞边反弹系数
  const STOP_V = 0.4;      // 速度低于此值停止（px/frame）

  function recordMove(dx, dy) {
    const now = performance.now();
    samples.push({ t: now, dx: dx || 0, dy: dy || 0 });
    while (samples.length && now - samples[0].t > 150) samples.shift();
  }

  /** 由样本估计当前速度（px/frame，假设 60fps）。 */
  function estimateVelocity() {
    const now = performance.now();
    const recent = samples.filter((s) => now - s.t <= 150);
    if (recent.length < 2) return { vx: 0, vy: 0 };
    const dt = (now - recent[0].t) / 1000;
    if (dt <= 0) return { vx: 0, vy: 0 };
    let dx = 0;
    let dy = 0;
    for (const s of recent) { dx += s.dx; dy += s.dy; }
    return { vx: (dx / dt) / 60, vy: (dy / dt) / 60 }; // 归一化到 1/60s 每帧
  }

  /** 窗口所在显示器的工作区。 */
  function workAreaOf() {
    const [x, y] = win.getPosition();
    const d = screen.getDisplayNearestPoint({ x, y });
    return d.workArea;
  }

  /** 位置钳制到显示器工作区（把整个窗口收进可见范围）。 */
  function clampPosition(x, y) {
    const wa = workAreaOf();
    const [w, h] = win.getSize();
    return {
      x: Math.max(wa.x, Math.min(x, wa.x + wa.width - w)),
      y: Math.max(wa.y, Math.min(y, wa.y + wa.height - h)),
      hitX: x < wa.x || x > wa.x + wa.width - w,
      hitY: y < wa.y || y > wa.y + wa.height - h,
    };
  }

  function startMomentum() {
    if (running) return;
    const v = estimateVelocity();
    vx = v.vx;
    vy = v.vy;
    samples.length = 0;
    if (Math.hypot(vx, vy) < STOP_V) return; // 基本没甩出去，不启动
    running = true;
    const step = () => {
      if (!running || win.isDestroyed()) { running = false; return; }
      let [x, y] = win.getPosition();
      x += vx;
      y += vy;
      const r = clampPosition(x, y);
      // 撞边：位置反弹 + 速度反向衰减（贴边吸附由摩擦自然收敛）
      if (r.hitX) vx = -vx * BOUNCE;
      if (r.hitY) vy = -vy * BOUNCE;
      win.setPosition(Math.round(r.x), Math.round(r.y));
      vx *= FRICTION;
      vy *= FRICTION;
      if (Math.hypot(vx, vy) < STOP_V) { running = false; return; }
      raf = requestFrame(step);
    };
    raf = requestFrame(step);
  }

  function stop() {
    running = false;
    if (raf) cancelFrame(raf);
    raf = null;
  }

  return { recordMove, estimateVelocity, startMomentum, stop, clampPosition, workAreaOf };
}

module.exports = { createPhysics };
