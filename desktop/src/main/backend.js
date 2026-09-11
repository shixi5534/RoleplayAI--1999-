/*
 * backend.js —— 网页版后端（FastAPI :8000）探活与拉起
 *
 * 桌面壳加载的就是网页版自己的页面，因此后端不可用时：
 *   1. 探活失败 → 宠物窗显示 fallback 引导页（启动/重试按钮）
 *   2. autoStart 开启时自动 spawn「<repoPath>/.venv/Scripts/python.exe -m uvicorn …」
 *   3. 后端恢复后主进程自动把窗口切回 pet.html
 * 所有网络请求仅限 127.0.0.1。
 */
"use strict";

const { spawn } = require("child_process");
const http = require("http");
const fs = require("fs");
const path = require("path");

let child = null;
let state = { ok: false, launching: false, error: "", port: 8000 };

function healthCheck(port, timeoutMs) {
  return new Promise((resolve) => {
    const req = http.request(
      { host: "127.0.0.1", port: Number(port) || 8000, path: "/health", method: "GET", timeout: timeoutMs || 2000 },
      (res) => {
        res.resume();
        resolve(res.statusCode === 200);
      }
    );
    req.on("timeout", () => { req.destroy(); resolve(false); });
    req.on("error", () => resolve(false));
    req.end();
  });
}

function backendUrl(port) {
  return "http://127.0.0.1:" + (Number(port) || 8000);
}

/** 拉起后端；返回是否已发起启动。已运行 / 已启动中 / 配置缺失时返回 false。 */
async function startBackend(cfg) {
  const port = Number(cfg.backend.port) || 8000;
  state.port = port;
  if (await healthCheck(port)) { state.ok = true; state.launching = false; return false; }
  if (state.launching) return false; // 已有一次启动在途

  const repoPath = cfg.backend.repoPath;
  const python = cfg.backend.python;
  if (!repoPath || !python || !fs.existsSync(python)) {
    state.ok = false;
    state.error = !repoPath
      ? "未配置网页版仓库路径（desktop/config.json → backend.repoPath）"
      : "未找到 Python（" + python + "），请先在 roleplay-ai 下创建 .venv";
    return false;
  }

  state.launching = true;
  state.error = "";
  console.info("[backend] 拉起:", python, "-m uvicorn roleplay.main:app --port", port, "cwd=", repoPath);
  child = spawn(
    python,
    ["-m", "uvicorn", "roleplay.main:app", "--host", "127.0.0.1", "--port", String(port)],
    {
      cwd: repoPath,
      windowsHide: true,
      stdio: ["ignore", "pipe", "pipe"],
      // 网页版为 src 布局：与 start_server.bat 一致，注入 PYTHONPATH=src
      env: Object.assign({}, process.env, { PYTHONPATH: path.join(repoPath, "src") }),
    }
  );
  child.stdout.on("data", (d) => { /* 后端日志量大，默认不透传；debug 时打开 */ });
  child.stderr.on("data", (d) => {
    const line = String(d).trim();
    if (line) console.warn("[backend]", line.slice(0, 300));
  });
  child.on("exit", (code) => {
    console.info("[backend] 进程退出 code=", code);
    child = null;
    state.launching = false;
    state.ok = false;
  });
  child.on("error", (err) => {
    console.warn("[backend] 启动失败:", err.message);
    child = null;
    state.launching = false;
    state.ok = false;
    state.error = String(err.message || err);
  });
  // 等待最多 15s 探活，成功即标记 ok
  for (let i = 0; i < 15; i++) {
    await new Promise((r) => setTimeout(r, 1000));
    if (await healthCheck(port)) { state.ok = true; state.launching = false; return true; }
    if (!child) return false; // 进程已退
  }
  state.launching = false;
  state.error = "后端启动超时（15s），请查看终端日志";
  return false;
}

/** 轮询探活（3s 间隔），状态变化时经回调推送。 */
async function pollBackend(cfg, onState) {
  const port = Number(cfg.backend.port) || 8000;
  state.port = port;
  while (true) {
    const ok = await healthCheck(port);
    const changed = ok !== state.ok || state.error;
    state.ok = ok;
    if (ok) state.error = "";
    if (changed && typeof onState === "function") onState(getState());
    if (!ok && cfg.backend.autoStart && !state.launching) {
      // 后端消失且开了自动拉起：尝试补拉（函数内部有防重入）
      startBackend(cfg).then(() => { if (typeof onState === "function") onState(getState()); });
    }
    await new Promise((r) => setTimeout(r, 3000));
  }
}

function getState() {
  return Object.assign({}, state);
}

module.exports = { startBackend, pollBackend, healthCheck, getState, backendUrl };
