/*
 * config.js —— 桌面壳配置（userData/config.json，原子写 + 默认值合并）
 *
 * 只保存「桌面端特有」的配置；LLM/语音/会话等仍以网页版 localStorage/后端为准。
 */
"use strict";

const fs = require("fs");
const path = require("path");
const { app } = require("electron");

// 开发态默认仓库根：desktop/src/main → 上溯三级即 roleplay-ai 仓库根
// 打包态该路径不存在，由用户在配置里显式指定（fallback 亦支持环境变量）。
const DEV_REPO_ROOT = path.resolve(__dirname, "..", "..", "..");

const DEFAULTS = {
  petUrl: "http://127.0.0.1:8000/pet.html",
  backend: {
    autoStart: true,          // 桌面壳是否自动拉起网页版后端
    port: 8000,
    repoPath: "",             // 留空：开发态自动探测；打包态需配置
    python: "",               // 留空：<repoPath>/.venv/Scripts/python.exe
  },
  pet: {
    width: 320,                // v0.3 默认档 S（320×420）；M=420×560，L=480×640
    height: 420,
    alwaysOnTopLevel: "floating", // floating | screen-saver
    x: null,                  // 窗口初始位置（null=主屏右下角）
    y: null,
    // P2：自主漫步
    walkEnabled: true,        // 是否开启自动漫步
    walkMinMs: 10000,         // 漫步触发间隔下限
    walkMaxMs: 30000,         // 漫步触发间隔上限
    walkIdleGraceMs: 30000,   // 最近一次交互后多久才允许漫步
    // P1：修饰态（持久化，重启恢复）
    dnd: false,               // 勿扰：透明 0.55 + 禁声 + 漫步暂停
    locked: false,            // 锁位：拖拽失效，长按 1.5s 解锁
    // P2-4：陪伴模式
    followMode: "off",        // off | cursor（跟随光标，偏移在右下不遮挡）
  },
  ptt: {
    key: "Alt+Space",         // 按住说话快捷键（P4 启用）
  },
    control: {
      port: 39231,              // 回环控制服务起始端口（被占用会自动 +1）
    },
  // P3：屏幕识别（截图/OCR 仅在内存流转，零落盘）
  ocr: {
    enabled: true,            // 手动「识别屏幕」开关
    autoMode: "off",          // off | keyword（关键词触发） | timer（定时评论）
    autoIntervalMs: 60000,    // 自动模式轮询间隔（下限 30s）
    region: "cursor",         // cursor（光标附近） | screen（全屏）
    regionSize: { w: 1200, h: 800 },
    lang: "chi_sim+eng",      // OCR 语言
    minIntervalMs: 2000,      // 手动触发最小间隔
    keywords: ["error", "错误", "失败", "exception", "警告", "warning", "崩溃"],
  },
};

// 配置白名单 + 类型约束：渲染进程传上来的 patch 只允许这些键，未知键/错误类型一律丢弃。
const CONFIG_SCHEMA = {
  petUrl: "string",
  backend: {
    autoStart: "boolean",
    port: "number",
    repoPath: "string",
    python: "string",
  },
  pet: {
    width: "number",
    height: "number",
    alwaysOnTopLevel: "string",
    x: "number",
    y: "number",
    walkEnabled: "boolean",
    walkMinMs: "number",
    walkMaxMs: "number",
    walkIdleGraceMs: "number",
    dnd: "boolean",
    locked: "boolean",
    followMode: "string",
  },
  ptt: { key: "string" },
  control: { port: "number" },
  ocr: {
    enabled: "boolean",
    autoMode: "string",
    autoIntervalMs: "number",
    region: "string",
    regionSize: { w: "number", h: "number" },
    lang: "string",
    minIntervalMs: "number",
    keywords: "array",
  },
};

function sanitizeConfigObject(input, schema) {
  const out = {};
  if (!input || typeof input !== "object" || Array.isArray(input)) return out;
  for (const key of Object.keys(schema)) {
    if (!(key in input)) continue;
    const rule = schema[key];
    const value = input[key];
    if (rule && typeof rule === "object" && !Array.isArray(rule)) {
      const nested = sanitizeConfigObject(value, rule);
      if (Object.keys(nested).length) out[key] = nested;
    } else if (rule === "array") {
      if (Array.isArray(value)) out[key] = value.slice();
    } else if (typeof value === rule) {
      out[key] = value;
    }
  }
  return out;
}


function configPath() {
  return path.join(app.getPath("userData"), "config.json");
}

function loadConfig() {
  const file = configPath();
  let saved = {};
  try {
    if (fs.existsSync(file)) {
      saved = sanitizeConfigObject(
        JSON.parse(fs.readFileSync(file, "utf8")),
        CONFIG_SCHEMA
      );
    }
  } catch (e) {
    console.warn("[config] 读取失败，使用默认配置:", e.message);
  }
  // 浅合并（嵌套对象按层合并）
  const merged = JSON.parse(JSON.stringify(DEFAULTS));
  for (const k of Object.keys(saved)) {
    if (merged[k] && typeof merged[k] === "object" && !Array.isArray(merged[k])) {
      Object.assign(merged[k], saved[k] || {});
    } else if (saved[k] !== undefined) {
      merged[k] = saved[k];
    }
  }
  // 开发态自动探测仓库根
  if (!merged.backend.repoPath && fs.existsSync(DEV_REPO_ROOT)) {
    merged.backend.repoPath = DEV_REPO_ROOT;
  }
  if (!merged.backend.python && merged.backend.repoPath) {
    const py = path.join(merged.backend.repoPath, ".venv", "Scripts", "python.exe");
    if (fs.existsSync(py)) merged.backend.python = py;
  }
  return merged;
}

function saveConfig(patch) {
  const cleanPatch = sanitizeConfigObject(patch || {}, CONFIG_SCHEMA);
  const current = loadConfig();
  const next = JSON.parse(JSON.stringify(current));
  for (const k of Object.keys(cleanPatch)) {
    if (next[k] && typeof next[k] === "object" && !Array.isArray(next[k])) {
      Object.assign(next[k], cleanPatch[k] || {});
    } else {
      next[k] = cleanPatch[k];
    }
  }
  const file = configPath();
  try {
    fs.mkdirSync(path.dirname(file), { recursive: true });
    const tmp = file + ".tmp";
    fs.writeFileSync(tmp, JSON.stringify(next, null, 2), "utf8");
    fs.renameSync(tmp, file); // 原子替换，避免写一半损坏
  } catch (e) {
    console.warn("[config] 保存失败:", e.message);
  }
  return loadConfig();
}

module.exports = { loadConfig, saveConfig, DEFAULTS };
