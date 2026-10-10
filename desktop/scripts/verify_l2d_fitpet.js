/*
 * verify_l2d_fitpet.js —— 验证桌面宠物分支 _fitPet() 在改用内容盒后的摆放
 *
 * 背景：pet.html 目前把渲染器锁死为 spine（pet.js P0），并不加载 live2d.js，
 *   所以 _fitPet 在现有页面上【没有调用方】。本次修复把它的基准从
 *   getLocalBounds()（布局框）换成了真实内容盒，属于"同一根因的另一处"，
 *   但它没有现成的 UI 入口可点 —— 因此这里直接驱动该分支本身来验收，
 *   避免留一段没人验证过的代码。
 *
 * 做法：起一个最小页面加载真实的 live2d.js，把 _fixedModel 置为 true 调 init()，
 *   对三套模型分别读回渲染像素 + _contentBox，检查：
 *     完整可见 / 水平居中 / 底边贴地（12px 留白）/ 不超框。
 *
 * 前置：后端已在 http://127.0.0.1:8000 运行。
 * 运行： desktop\node_modules\electron\dist\electron.exe desktop\scripts\verify_l2d_fitpet.js
 */
"use strict";
const { app, BrowserWindow } = require("electron");
const path = require("path");
const fs = require("fs");

const BASE = process.env.APP_URL || "http://127.0.0.1:8000";
const OUT = path.join(__dirname, "out");
const wait = (ms) => new Promise((r) => setTimeout(r, ms));
app.disableHardwareAcceleration();

// 最小宿主页：只加载真实前端脚本，容器尺寸模拟宠物窗。
// 必须由应用同源托管（相对路径的 ./assets/... 与 ./js/... 才解析得到）；
// 用 data: URL 会得到不透明源，fetch 全部失败、init 静默降级。
const HARNESS = `<!DOCTYPE html><html><head><meta charset="utf-8">
<style>html,body{margin:0;background:#111}
#pet-stage{position:relative;width:356px;height:520px;overflow:hidden}</style></head>
<body>
<div id="pet-stage"></div>
<script src="./assets/lib/live2dcubismcore.min.js"></script>
<script src="./assets/lib/pixi.min.js"></script>
<script src="./assets/lib/pixi-live2d-display-cubism4.min.js"></script>
<script src="./shared/pet-core.js"></script>
<script src="./js/live2d.js"></script>
</body></html>`;
// 注意：应用启用了 CSP（script-src 'self'），【内联脚本会被拦截】，
// 所以这里不能靠页面内的 <script> 设标志；就绪判定一律在主进程侧做。

app.whenReady().then(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const win = new BrowserWindow({
    width: 420, height: 620, show: false,
    webPreferences: { contextIsolation: true, nodeIntegration: false, sandbox: false },
  });
  const js = (c) => win.webContents.executeJavaScript(c);
  const log = (...a) => console.log(a.join(" "));
  let failed = 0;
  const check = (label, ok, detail) => {
    if (!ok) failed++;
    log(`${ok ? "PASS" : "FAIL"}  ${label}${detail ? "  — " + detail : ""}`);
  };

  const HARNESS_PATH = path.join(
    path.resolve(__dirname, "..", ".."), "frontend", "_fitpet_harness.html");

  try {
    // 由应用同源托管宿主页（相对路径才能解析）
    fs.writeFileSync(HARNESS_PATH, HARNESS, "utf8");
    win.webContents.on("did-fail-load", (_e, code, desc, url) => {
      log(`  [warn] 资源加载失败 ${code} ${desc} ${url}`);
    });
    await win.loadURL(BASE + "/_fitpet_harness.html");
    // 就绪判定在主进程侧轮询（页面内联脚本被 CSP 拦截，无法设标志）
    const READY_EXPR = "!!(window.RoleplayLive2D && typeof window.RoleplayLive2D.init === 'function')";
    for (let i = 0; i < 50; i++) {
      if (await js(READY_EXPR)) break;
      await wait(200);
    }
    const diag = await js(`JSON.stringify({
      hasL2D: !!window.RoleplayLive2D,
      hasInit: !!(window.RoleplayLive2D && window.RoleplayLive2D.init),
      hasPIXI: typeof window.PIXI !== "undefined",
      hasCore: typeof window.Live2DCubismCore !== "undefined",
      hasCoreShared: !!window.RoleplayPetCore
    })`);
    const l2dOk = await js(READY_EXPR);
    check("宿主页已加载 live2d.js", l2dOk, diag);
    if (!l2dOk) throw new Error("live2d.js 未加载: " + diag);

    // 以宠物模式（_fixedModel=true）初始化 —— 走的正是 _fitPet 分支
    // 注意：init() 内部 try/catch 会【返回 false】而不是抛错，必须看返回值
    const initRes = await js(`(async () => {
      try {
        window.RoleplayLive2D._fixedModel = true;
        const ok = await window.RoleplayLive2D.init({ containerId: "pet-stage" });
        return JSON.stringify({ ok: !!ok, model: !!window.RoleplayLive2D._model,
          ready: !!window.RoleplayLive2D.ready,
          cur: window.RoleplayLive2D._currentModelId });
      } catch (e) { return JSON.stringify({ threw: String(e && e.stack || e) }); }
    })()`);
    const ir = JSON.parse(initRes);
    check("宠物模式初始化（_fitPet 分支）", ir.ok === true && ir.model === true,
          JSON.stringify(ir));
    if (ir.ok !== true || ir.model !== true) {
      throw new Error("init 未成功: " + initRes);
    }

    const probe = `(() => {
      const L = window.RoleplayLive2D, app = L._pixiApp;
      if (!app || !L._model) return JSON.stringify({ ok:false });
      app.renderer.render(app.stage);
      const gl = app.renderer.gl, w = gl.drawingBufferWidth, h = gl.drawingBufferHeight;
      const res = app.renderer.resolution || 1;
      const pix = new Uint8Array(w*h*4);
      gl.readPixels(0,0,w,h,gl.RGBA,gl.UNSIGNED_BYTE,pix);
      let n=0,minX=w,minY=h,maxX=-1,maxY=-1;
      for (let y=0;y<h;y++) for (let x=0;x<w;x++) if (pix[(y*w+x)*4+3]>10) { n++;
        if(x<minX)minX=x; if(x>maxX)maxX=x; if(y<minY)minY=y; if(y>maxY)maxY=y; }
      return JSON.stringify({ ok:true, id:L.getCurrentModelId(),
        canvasCss:[app.screen.width, app.screen.height],
        contentCss:[minX/res, (h-1-maxY)/res, maxX/res, (h-1-minY)/res],
        visiblePx:n, boxMeasured: !!(L._contentBox && L._contentBox.measured),
        contentBox: L._contentBox ? {x:Math.round(L._contentBox.x),y:Math.round(L._contentBox.y),
                                    w:Math.round(L._contentBox.w),h:Math.round(L._contentBox.h)} : null });
    })()`;

    for (const id of ["314701", "314702", "314704"]) {
      await js(`window.RoleplayLive2D.switchModel(${JSON.stringify(id)})`);
      await wait(1200);
      const st = JSON.parse(await js(probe));
      log("\n--- 宠物模式 " + id + " ---");
      if (!st.ok) { check(id + " 渲染探针", false, "no model"); continue; }
      const [l, t, r, b] = st.contentCss;
      const [cw, ch] = st.canvasCss;
      check(id + " 内容盒已量测", st.boxMeasured === true, JSON.stringify(st.contentBox));
      check(id + " 有可见像素", st.visiblePx > 2000,
            `${st.visiblePx}px 画布 ${cw.toFixed(0)}x${ch.toFixed(0)}`);
      check(id + " 未超出窗口", l >= -1 && r <= cw + 1 && t >= -1 && b <= ch + 1,
            `内容 x ${l.toFixed(0)}..${r.toFixed(0)} y ${t.toFixed(0)}..${b.toFixed(0)} / 画布 ${cw.toFixed(0)}x${ch.toFixed(0)}`);
      const devX = Math.abs((l + r) / 2 - cw / 2) / cw;
      check(id + " 水平居中", devX < 0.06, `偏差 ${(devX*100).toFixed(1)}%`);
      const gapBottom = ch - b;
      check(id + " 底边贴地（留白≈12px）", gapBottom >= -3 && gapBottom <= 28,
            `距底 ${gapBottom.toFixed(0)}px`);
      // 顶部不截断即可：topZone 只是"预留"，当模型受宽度约束时剩余高度会用不满，
      // 内容自然上移，因此这里只要求留出不压头的余量（>10px），不硬性要求 110px。
      check(id + " 头顶未被裁切且留有余量", t >= 10 && t < ch * 0.5,
            `顶部留白 ${t.toFixed(0)}px`);
    }

    const shot = await win.webContents.capturePage();
    fs.writeFileSync(path.join(OUT, "pet_fitpet.png"), shot.toPNG());
    log("\n截图: " + path.join(OUT, "pet_fitpet.png"));
  } catch (e) {
    check("宠物模式验收执行", false, String((e && e.message) || e));
  }
  try { fs.unlinkSync(HARNESS_PATH); } catch (_) {}
  log("\n" + "=".repeat(66));
  log(failed ? `结果: ${failed} 项未通过` : "结果: 全部通过");
  app.exit(0);
});
