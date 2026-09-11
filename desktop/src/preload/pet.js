/*
 * pet.js (preload) —— contextBridge 白名单桥：window.petApi
 *
 * 渲染进程（网页版 pet.html / fallback 页）只能接触这里暴露的能力，
 * 与网页版「纯前端」完全解耦：浏览器打开时 petApi 不存在，页面自动降级。
 */
"use strict";

const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("petApi", {
  /** P2：主进程 hover 命中订阅（90ms 轮询，PetAI 范式），返回取消函数 */
  onHoverState: (cb) => {
    const handler = (_e, inside) => { try { cb(!!inside); } catch (_) {} };
    ipcRenderer.on("pet:hover-state", handler);
    return () => ipcRenderer.removeListener("pet:hover-state", handler);
  },

  /** P2：渲染层上报 Spine 模型实际包围盒（窗口坐标），主进程据此 setShape 点击穿透 */
  updateModelBounds: (bounds) => ipcRenderer.send("pet:model-bounds", bounds),

  /** 拖拽增量（screen 坐标 delta → 窗口跟随） */
  moveBy: (dx, dy) => ipcRenderer.send("pet:move-by", { dx, dy }),

  /** 拖拽结束（主进程做动量/回弹物理） */
  dragEnd: () => ipcRenderer.send("pet:drag-end"),

  /** 用户互动通知（点击/对话等，主进程据此刷新漫步计时） */
  notifyInteract: () => ipcRenderer.send("pet:interact"),

  /** 忙碌状态（对话/录音期间暂停自主漫步） */
  setBusy: (busy) => ipcRenderer.send("pet:busy", !!busy),

  /** P0-T4：窗口档位缩放（S 320×420 / M 420×560 / L 480×640） */
  setSize: (w, h) => ipcRenderer.send("pet:resize", { w, h }),

  /** P1：勿扰（主进程持久化 + 漫步暂停） */
  setDnd: (dnd) => ipcRenderer.send("pet:dnd", !!dnd),

  /** P1：锁位（主进程持久化 + moveBy 守卫） */
  setLocked: (locked) => ipcRenderer.send("pet:locked", !!locked),

  /** 隐藏宠物窗口（应用/控制服务保持运行，网页按钮可再次唤起） */
  hidePet: () => ipcRenderer.send("pet:hide"),

  /** P1-7：显示器列表 [{id,label,primary,bounds,workArea}] */
  getDisplays: () => ipcRenderer.invoke("pet:get-displays"),

  /** P1-7：摆到指定显示器 */
  moveToDisplay: (id) => ipcRenderer.send("pet:move-to-display", id),

  /** P1-7：回到默认位置 */
  resetPosition: () => ipcRenderer.send("pet:reset-position"),

  /** P2-6：导出截图（dataUrl → 系统保存对话框，仅用户确认后落盘） */
  exportImage: (dataUrl) => ipcRenderer.invoke("pet:export-image", dataUrl),

  /** 漫步状态订阅：cb({phase: "start"|"end"}) */
  onWalk: (cb) => {
    const handler = (_e, d) => { try { cb(d); } catch (_) {} };
    ipcRenderer.on("pet:walk", handler);
    return () => ipcRenderer.removeListener("pet:walk", handler);
  },

  /** 退出应用 */
  quit: () => ipcRenderer.send("pet:quit"),

  /** 打开设置窗口（P2） */
  openSettings: () => ipcRenderer.send("pet:open-settings"),

  /** 桌面端配置读写 */
  getConfig: () => ipcRenderer.invoke("pet:get-config"),
  setConfig: (patch) => ipcRenderer.invoke("pet:set-config", patch),

  /** 后端状态订阅：cb({ok, launching, error, port})；返回取消函数 */
  onBackendState: (cb) => {
    const handler = (_e, state) => { try { cb(state); } catch (_) {} };
    ipcRenderer.on("backend:state", handler);
    ipcRenderer.invoke("backend:get-state").then((s) => { if (s) handler(null, s); });
    return () => ipcRenderer.removeListener("backend:state", handler);
  },

  /** 拉起后端（fallback 页按钮） */
  launchBackend: () => ipcRenderer.invoke("backend:launch"),

  /** P3：手动识别屏幕（截图+OCR，结果经 onScreenText 回调） */
  captureScreen: () => ipcRenderer.invoke("pet:screen-comment"),

  /** 屏幕识别结果订阅：cb({text}) —— 关键词自动触发与手动触发共用此通道 */
  onScreenText: (cb) => {
    const handler = (_e, d) => { try { cb(d); } catch (_) {} };
    ipcRenderer.on("pet:ocr-result", handler);
    return () => ipcRenderer.removeListener("pet:ocr-result", handler);
  },

  /** P4：按住说话快捷键事件（Alt+Space 按下） */
  onPtt: (cb) => {
    const handler = (_e, d) => { try { cb(d); } catch (_) {} };
    ipcRenderer.on("pet:ptt", handler);
    return () => ipcRenderer.removeListener("pet:ptt", handler);
  },

  /** P4：网页版经回环服务让宠物说话 */
  onTalk: (cb) => {
    const handler = (_e, d) => { try { cb(d); } catch (_) {} };
    ipcRenderer.on("pet:talk", handler);
    return () => ipcRenderer.removeListener("pet:talk", handler);
  },

  /** P4：网页按钮唤起时通知宠物页（睡眠/待机 → 互动动画） */
  onWake: (cb) => {
    const handler = (_e, d) => { try { cb(d); } catch (_) {} };
    ipcRenderer.on("pet:wake", handler);
    return () => ipcRenderer.removeListener("pet:wake", handler);
  },
});
