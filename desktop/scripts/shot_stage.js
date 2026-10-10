/*
 * shot_stage.js —— 只截【数字人舞台】区域，用于肉眼核对摆放（而不是只看数字指标）
 *
 * 起因：上一轮我用 readPixels 量了"内容盒归一化范围"和"垂直居中偏差"，都通过，
 *   但用户截图显示模型的头被切掉了。说明"渲染像素的包围盒居中"并不等于
 *   "角色看起来摆放正常" —— 必须真的看图。
 *
 * 前置：后端已在 http://127.0.0.1:8000 运行。
 * 运行： desktop\node_modules\electron\dist\electron.exe desktop\scripts\shot_stage.js
 * 输出： desktop\scripts\out\stage_<model>.png（舞台区域原图）
 */
"use strict";
const { app, BrowserWindow } = require("electron");
const path = require("path");
const fs = require("fs");

const BASE = process.env.APP_URL || "http://127.0.0.1:8000";
const OUT = path.join(__dirname, "out");
const wait = (ms) => new Promise((r) => setTimeout(r, ms));
app.disableHardwareAcceleration();

app.whenReady().then(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const win = new BrowserWindow({
    width: 1440, height: 950, show: false,
    webPreferences: { contextIsolation: true, nodeIntegration: false, sandbox: false },
  });
  const js = (c) => win.webContents.executeJavaScript(c);
  const log = (...a) => console.log(a.join(" "));

  try {
    await win.loadURL(BASE + "/index.html");
    await wait(3500);

    // 关掉 HUD/overlay，避免截图里混入面板，便于看模型本体
    await js(`(() => {
      const h = document.getElementById("stage-hud"); if (h) h.style.display = "none";
      return true;
    })()`);

    for (const id of ["314701", "314702", "314704"]) {
      await js(`window.RoleplayLive2D.switchModel("${id}")`);
      await wait(1500);

      // 取舞台容器的屏幕坐标
      const rect = JSON.parse(await js(`(() => {
        const el = window.RoleplayLive2D._container;
        const r = el.getBoundingClientRect();
        return JSON.stringify({ x: Math.round(r.left), y: Math.round(r.top),
                                w: Math.round(r.width), h: Math.round(r.height) });
      })()`));
      log(id + " 舞台容器: " + JSON.stringify(rect));

      const img = await win.webContents.capturePage({
        x: rect.x, y: rect.y, width: rect.w, height: rect.h,
      });
      const f = path.join(OUT, `stage_${id}.png`);
      fs.writeFileSync(f, img.toPNG());
      log("  截图 -> " + f + "  (" + img.getSize().width + "x" + img.getSize().height + ")");
    }
  } catch (e) {
    console.error("失败: " + ((e && e.message) || e));
  }
  app.exit(0);
});
