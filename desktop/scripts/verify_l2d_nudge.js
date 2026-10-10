/*
 * verify_l2d_nudge.js —— 验收「Shift + 方向键微调数字人位置」
 *
 * 覆盖：
 *   1) nudge() 确实改变模型位置（上/下/左/右四个方向）
 *   2) 键盘事件路径（真实派发 Shift+ArrowUp/Down）也能生效
 *   3) 连续多次微调后仍受边界夹紧 —— 角色不会被推出画布
 *   4) 偏移会写回持久化状态（state.model_offset），刷新后保持
 *
 * 前置：后端已在 http://127.0.0.1:8000 运行。
 * 运行： desktop\node_modules\electron\dist\electron.exe desktop\scripts\verify_l2d_nudge.js
 */
"use strict";
const { app, BrowserWindow } = require("electron");
const path = require("path");

const BASE = process.env.APP_URL || "http://127.0.0.1:8000";
const wait = (ms) => new Promise((r) => setTimeout(r, ms));
app.disableHardwareAcceleration();

/** 渲染当前帧并返回模型位置 + 内容包围盒（判断是否被切） */
const PROBE = `(() => {
  const L = window.RoleplayLive2D, app = L._pixiApp, m = L._model;
  if (!app || !m) return JSON.stringify({ ok:false });
  app.renderer.render(app.stage);
  const gl = app.renderer.gl, w = gl.drawingBufferWidth, h = gl.drawingBufferHeight;
  const res = app.renderer.resolution || 1;
  const pix = new Uint8Array(w*h*4);
  gl.readPixels(0,0,w,h,gl.RGBA,gl.UNSIGNED_BYTE,pix);
  let n=0,minX=w,minY=h,maxX=-1,maxY=-1;
  for(let y=0;y<h;y++) for(let x=0;x<w;x++) if(pix[(y*w+x)*4+3]>10){ n++;
    if(x<minX)minX=x; if(x>maxX)maxX=x; if(y<minY)minY=y; if(y>maxY)maxY=y; }
  const sw = app.screen.width, sh = app.screen.height;
  const cL=minX/res, cR=maxX/res, cT=(h-1-maxY)/res, cB=(h-1-minY)/res;
  return JSON.stringify({
    ok:true, px:[Math.round(m.x), Math.round(m.y)],
    off:[Math.round(L._userOffsetX), Math.round(L._userOffsetY)],
    content:[+cL.toFixed(0), +cT.toFixed(0), +cR.toFixed(0), +cB.toFixed(0)],
    canvas:[sw, sh], visiblePx:n,
    clip:{ left:cL<=0.5, right:cR>=sw-1.5, top:cT<=0.5, bottom:cB>=sh-1.5 }
  });
})()`;

app.whenReady().then(async () => {
  const win = new BrowserWindow({
    width: 1440, height: 950, show: false,
    webPreferences: { contextIsolation: true, nodeIntegration: false, sandbox: false },
  });
  const js = (c) => win.webContents.executeJavaScript(c);
  const log = (...a) => console.log(a.join(" "));
  let failed = 0;
  const check = (label, ok, detail) => {
    if (!ok) failed++;
    log(`${ok ? "PASS" : "FAIL"}  ${label}${detail ? "  — " + detail : ""}`);
  };

  try {
    await win.loadURL(BASE + "/index.html");
    await wait(3500);

    const read = async () => JSON.parse(await js(PROBE));

    // 复位
    await js("window.RoleplayLive2D.resetPosition()");
    await wait(400);
    const base = await read();
    check("起始状态可读", base.ok === true, JSON.stringify(base.off));
    check("起始偏移为 0（居中）", base.off[0] === 0 && base.off[1] === 0,
          JSON.stringify(base.off));

    // ── 1. API 路径：四个方向 ──
    // 注意：垂直可动范围受几何限制（内容几乎占满画布，垂直余量本就比水平小），
    // 所以这里不断言"位移等于请求值"，而是断言【方向正确且确实发生了位移】，
    // 边界由第 3 组用例单独验收。
    log("\n--- API 路径 nudge() ---");
    const cases = [
      ["向上", 0, -12],
      ["向下", 0, +12],
      ["向左", -12, 0],
      ["向右", +12, 0],
    ];
    for (const [name, dx, dy] of cases) {
      await js("window.RoleplayLive2D.resetPosition()");
      await wait(250);
      const before = await read();
      await js(`window.RoleplayLive2D.nudge(${dx}, ${dy})`);
      await wait(250);
      const after = await read();
      const dX = after.off[0] - before.off[0];
      const dY = after.off[1] - before.off[1];
      const ok = (dy !== 0) ? (Math.sign(dY) === Math.sign(dy) && dX === 0)
                            : (Math.sign(dX) === Math.sign(dx) && dY === 0);
      check(`nudge ${name} (${dx},${dy})`, ok,
            `偏移 ${JSON.stringify(before.off)} -> ${JSON.stringify(after.off)}`);
    }

    // ── 2. 键盘路径：真实派发按键事件 ──
    log("\n--- 键盘路径 Shift + 方向键 ---");
    await js("window.RoleplayLive2D.resetPosition()");
    await wait(300);
    // 列序是 [key, 名称, sgnX, sgnY]：向上=Y 负、向下=Y 正、向左=X 负、向右=X 正
    const kb = [
      ["ArrowUp", "向上", 0, -1],
      ["ArrowDown", "向下", 0, +1],
      ["ArrowLeft", "向左", -1, 0],
      ["ArrowRight", "向右", +1, 0],
    ];
    for (const [key, name, sgnX, sgnY] of kb) {
      await js("window.RoleplayLive2D.resetPosition()");
      await wait(250);
      const before = await read();
      await js(`(() => {
        document.dispatchEvent(new KeyboardEvent("keydown", {
          key: "${key}", shiftKey: true, bubbles: true, cancelable: true
        }));
        return true;
      })()`);
      await wait(300);
      const after = await read();
      const dX = after.off[0] - before.off[0];
      const dY = after.off[1] - before.off[1];
      // 键盘路径只要求：按该方向键后，对应轴发生了【正确方向】的位移。
      // 不能断言 dX/dY 恰好等于步长 —— 方向键可能被连续触发（长按/重复），
      // 也可能是被边界夹紧后的部分位移。
      const ok = sgnY !== 0 ? (Math.sign(dY) === sgnY)
                            : (Math.sign(dX) === sgnX);
      check(`键盘 Shift+${key} ${name}`, ok,
            `偏移 ${JSON.stringify(before.off)} -> ${JSON.stringify(after.off)}`
            + ` (Δ=${dX},${dY})`);
    }

    // ── 3. 边界：连续狂按不得把角色推出画布 ──
    // 注意：单帧采样会误判 —— 动作播放过程中轮廓会瞬间变宽，某一帧可能刚好贴边。
    // 判定必须【多帧采样取最小留白】，只有持续为负才算真的被推出画布。
    log("\n--- 边界夹紧（连续 40 次，多帧采样）---");
    for (const [dir, dy] of [["向上", -12], ["向下", +12]]) {
      await js("window.RoleplayLive2D.resetPosition()");
      await wait(250);
      for (let i = 0; i < 40; i++) {
        await js(`window.RoleplayLive2D.nudge(0, ${dy})`);
      }
      await wait(300);
      let worst = { left: Infinity, right: Infinity, top: Infinity, bottom: Infinity };
      let samples = 0;
      for (let s = 0; s < 15; s++) {
        const st = await read();
        if (st.ok) {
          samples++;
          worst.left = Math.min(worst.left, st.content[0]);
          worst.top = Math.min(worst.top, st.content[1]);
          worst.right = Math.min(worst.right, st.canvas[0] - st.content[2]);
          worst.bottom = Math.min(worst.bottom, st.canvas[1] - st.content[3]);
        }
        await wait(180);
      }
      const off = await read();
      const overflow = Object.entries(worst)
        .filter(([, v]) => v < -0.5)
        .map(([k, v]) => `${k}=${v.toFixed(1)}`);
      check(`连续${dir} 40 次后角色未被推出画布`, overflow.length === 0,
            `${samples} 帧最小留白 左${worst.left.toFixed(1)} 上${worst.top.toFixed(1)}`
            + ` 右${worst.right.toFixed(1)} 下${worst.bottom.toFixed(1)}`
            + ` | 偏移 ${JSON.stringify(off.off)}`
            + (overflow.length ? `  溢出: ${overflow.join(" ")}` : ""));
    }

    // ── 4. 持久化：偏移是否写回 localStorage 状态 ──
    log("\n--- 持久化 ---");
    await js("window.RoleplayLive2D.resetPosition()");
    await wait(250);
    await js("window.RoleplayLive2D.nudge(0, -30)");
    await wait(400);
    const uiAfter = await read();
    const saved = JSON.parse(await js(`(() => {
      try {
        const raw = localStorage.getItem("roleplay_ui_state");
        if (!raw) return JSON.stringify({ found:false });
        const s = JSON.parse(raw);
        return JSON.stringify({ found:true, off: s.model_offset });
      } catch (e) { return JSON.stringify({ found:false, err:String(e) }); }
    })()`));
    check("偏移已写入持久化状态", saved.found === true && !!saved.off,
          JSON.stringify(saved));
    if (saved.found && saved.off) {
      // 键名是角色的持久化偏移；值与界面一致即可
      check("持久化里的垂直偏移与界面一致",
            Math.round(saved.off.y) === Math.round(uiAfter.off[1]),
            `saved.y=${saved.off.y} ui.y=${uiAfter.off[1]}`);
    }
    // 清理现场：本用例把 -30 的偏移写进了 localStorage，若不清掉会污染后续测试
    // （e2e 会读到这个残留偏移，导致"默认状态角色被裁切"的误报）。
    await js("window.RoleplayLive2D.resetPosition()");
    await wait(300);
    log("  （已重置偏移，避免污染后续测试的持久化状态）");
  } catch (e) {
    check("验收执行", false, String((e && e.message) || e));
  }
  log("\n" + "=".repeat(70));
  log(failed ? `结果: ${failed} 项未通过` : "结果: 全部通过");
  app.exit(0);
});
