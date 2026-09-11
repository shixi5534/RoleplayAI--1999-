/*
 * ocr.js —— 屏幕截图 + 本地 OCR + 关键词/定时触发（P3）
 *
 * 隐私承诺：截图与识别文本仅在内存流转，不落盘、不上传；
 * 日志只记录字符数，不记录内容。OCR 语言包随安装包分发（resources/ocr/traineddata）。
 */
"use strict";

const path = require("path");
const { app, desktopCapturer, screen, ipcMain } = require("electron");

// 开发态：desktop/resources/ocr/traineddata；打包态：extraResources → resourcesPath/ocr/traineddata
const TRAINEDDATA_DIR = app.isPackaged
  ? path.join(process.resourcesPath, "ocr", "traineddata")
  : path.join(__dirname, "..", "..", "resources", "ocr", "traineddata");

let worker = null;       // tesseract.js worker（懒加载，复用）
let workerLang = "";
let busy = false;        // 全局互斥：截图+识别串行
let lastRunAt = 0;

/** 加载/复用 tesseract worker（语言切换时重建）。 */
async function ensureWorker(lang) {
  if (worker && workerLang === lang) return worker;
  if (worker) {
    try { await worker.terminate(); } catch (_) {}
    worker = null;
  }
  const { createWorker } = require("tesseract.js");
  // gzip:false —— 随包分发的是未压缩 .traineddata；langPath 用绝对路径（worker 按 process.cwd 解析相对路径）
  worker = await createWorker(lang || "chi_sim+eng", 1, {
    langPath: TRAINEDDATA_DIR,
    gzip: false,
  });
  workerLang = lang || "chi_sim+eng";
  return worker;
}

/**
 * 截取光标所在显示器（screen=该显示器全图；cursor=光标附近区域），返回 PNG Buffer（仅内存）。
 * 多显示器修正：按 display_id 匹配光标所在显示器的屏幕源，裁剪坐标也以该显示器
 * 工作区为基准（旧实现固定取主屏源 + 主屏尺寸，副屏上光标区域会错位）。
 */
async function captureRegion(mode, regionSize) {
  const pt = screen.getCursorScreenPoint();
  const cur = screen.getDisplayNearestPoint(pt);
  const sources = await desktopCapturer.getSources({
    types: ["screen"],
    thumbnailSize: { width: 0, height: 0 }, // 0 = 全分辨率
    fetchWindowIcons: false,
  });
  if (!sources.length) throw new Error("未找到屏幕源");
  // Windows 每屏一个 screen source，display_id 与 screen API 的 id 对应
  const src = sources.find((s) => String(s.display_id) === String(cur.id)) || sources[0];
  const img = src.thumbnail;
  const size = img.getSize();
  const b = cur.bounds;
  if (size.width <= 0 || size.height <= 0) throw new Error("屏幕截图失败（空图像）");
  // 源像素尺寸 vs 显示器逻辑尺寸 → DPI 缩放系数（裁剪坐标换算用）
  const sx = size.width / b.width;
  const sy = size.height / b.height;

  if (mode === "screen") {
    // 全屏：直接取该显示器源全图（Windows 单屏一个源；合成源场景下取全图即可）
    return img.crop({ x: 0, y: 0, width: size.width, height: size.height }).toPNG();
  }

  // cursor：围绕光标在该显示器内裁剪（逻辑坐标 → 源像素坐标）
  const w = Math.min((regionSize && regionSize.w) || 1200, b.width);
  const h = Math.min((regionSize && regionSize.h) || 800, b.height);
  const cx = pt.x - b.x;
  const cy = pt.y - b.y;
  const x = Math.max(0, Math.min(cx - Math.round(w / 2), b.width - w));
  const y = Math.max(0, Math.min(cy - Math.round(h / 2), b.height - h));
  return img
    .crop({
      x: Math.round(x * sx),
      y: Math.round(y * sy),
      width: Math.round(w * sx),
      height: Math.round(h * sy),
    })
    .toPNG();
}

/** OCR 识别：返回 { text, durationMs }。 */
async function recognize(pngBuf, lang) {
  const w = await ensureWorker(lang);
  const t0 = Date.now();
  const { data } = await w.recognize(pngBuf);
  return { text: (data && data.text || "").trim(), durationMs: Date.now() - t0 };
}

/**
 * 完整流程：截图 → OCR → 按策略决定是否回传。
 * opts: { mode: "cursor"|"screen", lang, minIntervalMs, manual }
 *   manual=true（右键「识别屏幕」）：无论是否命中关键词都把文本回传宠物评论；
 *   自动模式（keyword/timer）仅命中关键词才回传。
 * 返回 { text, triggered, reason, durationMs }（text 仅在触发/手动时带内容）。
 */
async function runOnce(cfg, opts) {
  opts = opts || {};
  if (busy) return { text: "", triggered: false, reason: "busy", durationMs: 0 };
  busy = true;
  try {
    const ocr = cfg.ocr || {};
    const minMs = opts.minIntervalMs || ocr.minIntervalMs || 2000;
    if (Date.now() - lastRunAt < minMs) {
      return { text: "", triggered: false, reason: "throttled", durationMs: 0 };
    }
    lastRunAt = Date.now();

    const png = await captureRegion(opts.mode || ocr.region || "cursor", ocr.regionSize);
    const lang = opts.lang || ocr.lang || "chi_sim+eng";
    const { text, durationMs } = await recognize(png, lang);

    const manual = !!opts.manual;
    const keywords = (ocr.keywords || ["error", "错误", "失败", "exception", "警告", "warning", "崩溃"]);
    const lower = text.toLowerCase();
    const hit = manual || keywords.some((k) => lower.includes(String(k).toLowerCase()));
    console.info("[ocr] 识别", text.length, "字符 /", durationMs, "ms / 命中:", hit, "/ manual:", manual);
    return {
      text: hit ? text : "",
      triggered: hit,
      reason: manual ? "manual" : hit ? "keyword" : "no-keyword",
      durationMs,
    };
  } finally {
    busy = false;
  }
}

/**
 * 注册 IPC 与自动触发（模块级副作用，主进程启动时调用一次）。
 * onResult: 把结果推给渲染层（宠物页据此发评论）。
 */
function setup(cfg, onResult) {
  // 手动触发：右键菜单「识别屏幕」（manual=true：无关键词也回传，评论权交给用户）
  ipcMain.handle("pet:screen-comment", async () => {
    try {
      const r = await runOnce(cfg, { minIntervalMs: 2000, manual: true });
      if (onResult) onResult(r);
      return { ok: true, triggered: r.triggered, textLength: r.text.length, durationMs: r.durationMs };
    } catch (e) {
      console.warn("[ocr] 手动触发失败:", e.message);
      return { ok: false, error: String(e.message || e) };
    }
  });

  // 自动触发：keyword / timer（低频，默认关）
  const ocr = cfg.ocr || {};
  if (ocr.autoMode === "keyword" || ocr.autoMode === "timer") {
    const interval = Math.max(30000, ocr.autoIntervalMs || 60000);
    setInterval(async () => {
      // 自动路径必须吞错：截图源缺失/OCR worker 失败等一次拒绝若外抛，
      // 主进程会按未捕获异常退出，整个宠物应用被一次自动触发杀死。
      try {
        const r = await runOnce(cfg, {});
        if (r.triggered && onResult) onResult(r);
      } catch (e) {
        console.warn("[ocr] 自动触发失败（下个周期重试）:", e && e.message ? e.message : e);
      }
    }, interval);
  }
}

module.exports = { setup, runOnce, captureRegion, recognize };
