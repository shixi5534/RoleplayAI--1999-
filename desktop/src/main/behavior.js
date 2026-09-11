/*
 * behavior.js —— 自主漫步调度（P2）
 *
 * 桌面宠物在「空闲且无交互」时随机在屏幕内漫步：
 *   目标点 = 当前显示器工作区内的随机点（离当前位置 200~800px）
 *   移动   = 60fps lerp 移动窗口（主进程），期间通知渲染层进入 walk 状态
 *   频率   = 可配（默认 10~30s 随机一次），对话/录音/拖拽期间暂停
 *
 * 注：Live2D 素材无行走循环，「行走」= 窗口滑动 + 渲染层伴随机轻动作；
 *     接入 Spine 小模型（target* 移动动画）后由渲染层替换伴随动作即可。
 */
"use strict";

const { screen } = require("electron");
const { requestFrame, cancelFrame } = require("./raf"); // 主进程无 requestAnimationFrame，用垫片

function createWalker(win, cfg, hooks) {
  hooks = hooks || {};
  let timer = null;
  let anim = null;
  let paused = false;
  let lastInteractAt = Date.now();

  /** 实时读取配置（设置抽屉修改即时生效；初次 cfg 仅作兜底）。 */
  function petCfg() {
    try {
      return require("./config").loadConfig().pet || {};
    } catch (_) {
      return cfg.pet || {};
    }
  }

  function pause() { paused = true; stopWalk(); }
  function resume() { paused = false; schedule(); }

  /** 用户互动（对话/拖拽/点击由渲染层经 IPC 通知）→ 重置计时。 */
  function notifyInteract() { lastInteractAt = Date.now(); }

  function schedule() {
    if (timer) clearTimeout(timer);
    if (paused) return;
    const p = petCfg();
    if (p.walkEnabled === false) return;
    const min = (p.walkMinMs || 10000) + Math.random() * ((p.walkMaxMs || 30000) - (p.walkMinMs || 10000));
    timer = setTimeout(() => {
      const idleFor = Date.now() - lastInteractAt;
      // 最近有交互（默认 30s 内）则再等等，避免用户操作时乱跑
      if (idleFor < (p.walkIdleGraceMs || 30000)) { schedule(); return; }
      startWalk();
    }, min);
  }

  function startWalk() {
    if (!win || win.isDestroyed() || paused) return;
    const p = petCfg();
    // 锁位 / 跟随光标模式下不自主移动（锁位时 moveBy 也守卫；跟随模式与漫步目标互相打架）
    if (p.locked || p.followMode === "cursor") { schedule(); return; }
    const [x, y] = win.getPosition();
    const [w, h] = win.getSize();
    const wa = screen.getDisplayNearestPoint({ x, y }).workArea;
    // 随机目标点：离当前位置 200~800px，且整窗留在工作区内
    const ang = Math.random() * Math.PI * 2;
    const dist = 200 + Math.random() * 600;
    const tx = Math.max(wa.x, Math.min(x + Math.cos(ang) * dist, wa.x + wa.width - w));
    const ty = Math.max(wa.y, Math.min(y + Math.sin(ang) * dist, wa.y + wa.height - h));
    if (Math.hypot(tx - x, ty - y) < 40) { schedule(); return; } // 目标太近，放弃本轮

    const dur = 1800 + Math.random() * 2200; // 1.8~4s 到达（速度观感）
    const start = performance.now();
    const sx = x, sy = y;
    notifyWalk("start", { dx: tx - sx, dy: ty - sy }); // 带移动方向，渲染层据此镜像朝向
    const step = (now) => {
      if (!win || win.isDestroyed() || paused) { anim = null; return; }
      const t = Math.min(1, (now - start) / dur);
      const ease = t * t * (3 - 2 * t); // smoothstep
      win.setPosition(Math.round(sx + (tx - sx) * ease), Math.round(sy + (ty - sy) * ease));
      if (t < 1) {
        anim = requestFrame(step);
      } else {
        anim = null;
        notifyWalk("end");
        schedule();
      }
    };
    anim = requestFrame(step);
  }

  function stopWalk() {
    if (anim) cancelFrame(anim);
    anim = null;
    notifyWalk("end");
  }

  function notifyWalk(phase, extra) {
    if (!win || win.isDestroyed()) return;
    try {
      win.webContents.send("pet:walk", Object.assign({ phase }, extra || {}));
    } catch (_) {}
    if (hooks.onWalk) hooks.onWalk(phase, extra);
  }

  function start() { schedule(); }
  function stop() {
    if (timer) clearTimeout(timer);
    stopWalk();
  }

  return { start, stop, pause, resume, notifyInteract, startWalk, stopWalk };
}

module.exports = { createWalker };
