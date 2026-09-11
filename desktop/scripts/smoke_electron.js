/*
 * smoke_electron.js —— 桌面壳真实启动冒烟测试（Phase 4）
 *
 * 运行：node scripts/smoke_electron.js
 * 前置：127.0.0.1:8000 后端已启动（pet.html 可访问）。
 *
 * 行为：启动 desktop/ 的 Electron（--enable-logging），等待 18s 后
 * 用 taskkill /T 结束进程树，再检查渲染层控制台日志：
 *   - 出现 "[spine] fit ->"     → Spine 骨骼实际加载并完成 fit；
 *   - 不出现 Spine 初始化异常/失败 → P0 Spine-only 链路健康。
 */
"use strict";

const { spawn, spawnSync } = require("child_process");
const path = require("path");

const DESKTOP = path.resolve(__dirname, "..");
const electronPath = require("electron"); // npm 包导出本机 electron.exe 路径
const WAIT_MS = Number(process.env.PET_SMOKE_WAIT_MS || 18000);

function start() {
  const child = spawn(electronPath, [".", "--enable-logging", "--v=1"], {
    cwd: DESKTOP,
    windowsHide: false,
    stdio: ["ignore", "pipe", "pipe"],
  });
  let out = "";
  let err = "";
  child.stdout.on("data", (d) => { out += d.toString(); });
  child.stderr.on("data", (d) => { err += d.toString(); });
  return { child, logs: () => out + "\n" + err };
}

function killTree(pid) {
  try {
    spawnSync("taskkill", ["/PID", String(pid), "/T", "/F"], { windowsHide: true, stdio: "ignore" });
  } catch (_) {}
}

async function main() {
  // 单实例锁预检：宠物已在运行时，冒烟实例会因 requestSingleInstanceLock
  // 拿不到锁而秒退、日志全空，表现为"未观察到 Spine fit"的误导性失败。
  const running = spawnSync("tasklist", ["/FI", "IMAGENAME eq electron.exe"], {
    windowsHide: true, encoding: "utf8",
  });
  if ((running.stdout || "").includes("electron.exe")) {
    console.error("SKIP: 检测到 electron.exe 正在运行（桌面宠物已开启）。");
    console.error("       单实例锁会让冒烟实例秒退；请先关闭正在运行的宠物再跑本冒烟。");
    process.exit(2);
  }
  const { child, logs } = start();
  await new Promise((r) => setTimeout(r, WAIT_MS));
  killTree(child.pid);
  await new Promise((r) => setTimeout(r, 1500));

  const all = logs();
  const spineFit = /\[spine\] fit ->/.test(all);
  const spineFail = /\[spine\][^\n]*(初始化异常|加载失败|创建失败)/.test(all);
  const petFail = /\[pet\][^\n]*(初始化异常|失败)/.test(all);

  console.log("── Electron 冒烟日志摘录 ──");
  const spineLines = all.split(/\r?\n/).filter((l) => /\[spine\]|\[pet\]|\[window\]|\[ipc\]/.test(l));
  (spineLines.length ? spineLines : all.split(/\r?\n/).slice(0, 30)).forEach((l) => console.log(l.trim()));

  if (!spineFit) {
    console.error("\nFAIL: 未观察到 Spine fit 日志（骨骼未成功加载）");
    process.exit(1);
  }
  if (spineFail || petFail) {
    console.error("\nFAIL: 日志中出现 Spine/Pet 初始化异常");
    process.exit(1);
  }
  console.log("\nPASS: Electron 桌面壳启动，Spine 唯一渲染器加载成功（" + WAIT_MS + "ms 冒烟）");
  process.exit(0);
}

main().catch((e) => {
  console.error("SMOKE TEST FAILED:", e && e.stack ? e.stack : e);
  process.exit(1);
});
