/*
 * control-server.js —— 回环 HTTP 控制服务（P4）
 *
 * 让网页版（http://127.0.0.1:8000）能探测/唤起桌面宠物：
 *   GET  /ping   → {ok, version, port}
 *   POST /launch → 唤出并置顶宠物窗
 *   POST /talk   → 让宠物说一句话（body: {text}）
 *
 * 只监听 127.0.0.1；CORS 仅回显回环源（127.0.0.1 与 localhost 的任意端口）。
 * 端口默认 39231，占用则自动 +1 探测，实际端口写入 userData/control-port.txt。
 */
"use strict";

const http = require("http");
const fs = require("fs");
const path = require("path");
const { app } = require("electron");

// 版本号以 package.json 为准（避免手改 IPC 响应里的硬编码版本漂移）
let APP_VERSION = "0.1.0";
try {
  const pkg = require("../../package.json");
  if (pkg && pkg.version) APP_VERSION = pkg.version;
} catch (_) {}

function isLoopbackOrigin(origin) {
  if (!origin) return true;
  try {
    const u = new URL(origin);
    return u.hostname === "127.0.0.1" || u.hostname === "localhost" || u.hostname === "::1";
  } catch (_) {
    return false;
  }
}

function createControlServer(cfg, hooks) {
  hooks = hooks || {};
  const handlers = {
    "GET /ping": () => ({ ok: true, version: APP_VERSION, state: "running" }),
    "GET /state": () => ({
      ok: true,
      version: APP_VERSION,
      state: "running",
      hint: "右键宠物打开菜单 · Alt+Space 按住说话 · Ctrl+Enter 打字",
    }),
    "POST /launch": () => {
      if (hooks.onLaunch) hooks.onLaunch();
      return { ok: true };
    },
    "POST /talk": (body) => {
      if (hooks.onTalk && body && typeof body.text === "string") hooks.onTalk(body.text);
      return { ok: true };
    },
  };

  const server = http.createServer((req, res) => {
    // CORS：仅回显回环源
    const origin = req.headers.origin;
    if (origin) {
      if (!isLoopbackOrigin(origin)) {
        res.writeHead(403);
        return res.end("forbidden origin");
      }
      res.setHeader("Access-Control-Allow-Origin", origin);
      res.setHeader("Vary", "Origin");
    }
    res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
    res.setHeader("Access-Control-Allow-Headers", "Content-Type");
    if (req.method === "OPTIONS") {
      res.writeHead(204);
      return res.end();
    }

    const route = req.method + " " + (req.url || "/").split("?")[0];
    const handler = handlers[route];
    if (!handler) {
      res.writeHead(404, { "Content-Type": "application/json" });
      return res.end(JSON.stringify({ ok: false, error: "not found" }));
    }

    let body = "";
    req.on("data", (c) => {
      body += c;
      if (body.length > 64 * 1024) req.destroy(); // 防御：请求体上限 64KB
    });
    req.on("end", () => {
      let parsed = null;
      if (body) {
        try { parsed = JSON.parse(body); } catch (_) {}
      }
      try {
        const result = handler(parsed);
        res.writeHead(200, { "Content-Type": "application/json" });
        res.end(JSON.stringify(result));
      } catch (e) {
        res.writeHead(500, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ ok: false, error: String(e.message || e) }));
      }
    });
  });

  let port = (cfg.control && cfg.control.port) || 39231;
  function listen() {
    return new Promise((resolve) => {
      const onError = (err) => {
        if (err.code === "EADDRINUSE" && port < 39251) {
          port += 1;
          server.removeListener("error", onError);
          server.close(() => resolve(listen()));
        } else {
          resolve(null);
        }
      };
      server.once("error", onError);
      server.listen(port, "127.0.0.1", () => {
        server.removeListener("error", onError);
        resolve(port);
      });
    });
  }

  listen().then((p) => {
    if (!p) return;
    port = p;
    // 端口落盘，供网页版按钮探测（找不到文件时按默认 39231 逐个 ping）
    try {
      const dir = app.getPath("userData");
      fs.mkdirSync(dir, { recursive: true });
      fs.writeFileSync(path.join(dir, "control-port.txt"), String(port), "utf8");
    } catch (_) {}
  });

  return { getPort: () => port, close: () => server.close() };
}

module.exports = { createControlServer, isLoopbackOrigin };
