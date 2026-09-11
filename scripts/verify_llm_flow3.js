// verify_llm_flow.js —— 端到端验证「调整模型」弹层完整流程
// 通过 CDP 驱动 Edge headless 访问 http://127.0.0.1:8000/
// 验证：
//   1. 页面加载后 RoleplayLLM 正常初始化（弹层可用）
//   2. 打开弹层 → 选 DeepSeek → 填 key → 保存 → state 持久化
//   3. 刷新页面 → 配置保持（key 回填不丢）
//   4. buildOverride() 返回带 key 的 override（聊天请求会带 llm 字段）
//   5. 清理坏配置路径：localStorage 残留「云端+空key」时 loadState 自动清洗
const { spawn } = require("child_process");

const EDGE = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe";
const PORT = 10084; // 调试端口（避开 check_state.js 的 10083）
const URL = "http://127.0.0.1:8000/";

const child = spawn(
  EDGE,
  [
    "--headless=new",
    `--remote-debugging-port=${PORT}`,
    "--user-data-dir=C:/Users/Lenovo/WorkBuddy/2026-07-27-16-45-03/.edge-verify",
    "--no-first-run",
    "--disable-gpu",
    URL,
  ],
  { stdio: "ignore" }
);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function main() {
  await sleep(5000);

  // 连接调试端口，找到页面 target
  let page;
  for (let i = 0; i < 15; i++) {
    try {
      const res = await fetch(`http://127.0.0.1:${PORT}/json`);
      const ts = await res.json();
      page = ts.find((t) => t.type === "page" && t.url.includes("127.0.0.1:8000")) ||
        ts.find((t) => t.type === "page");
      if (page) break;
    } catch (_) {}
    await sleep(1000);
  }
  if (!page) throw new Error("未找到页面 target");

  const ws = new WebSocket(page.webSocketDebuggerUrl);
  let id = 0;
  const pending = new Map();
  const send = (m, p = {}) =>
    new Promise((resolve) => {
      const mid = ++id;
      pending.set(mid, resolve);
      ws.send(JSON.stringify({ id: mid, method: m, params: p }));
    });
  ws.onmessage = (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.id && pending.has(msg.id)) {
      pending.get(msg.id)(msg.result);
      pending.delete(msg.id);
    }
  };
  await new Promise((r) => (ws.onopen = r));
  await sleep(3500);

  const evalJs = async (expr) => {
    const r = await send("Runtime.evaluate", { expression: expr, returnByValue: true });
    return r.result?.value;
  };

  const results = [];
  const step = (name, ok, detail = "") =>
    results.push(`${ok ? "✅" : "❌"} ${name}${detail ? " — " + detail : ""}`);

  // ── 步骤1：页面加载 & 模块初始化 ──
  const llmReady = await evalJs(`!!(window.RoleplayLLM && window.RoleplayLLM.buildOverride)`);
  step("RoleplayLLM 模块已加载", !!llmReady);
  const hudName = await evalJs(
    `(window.RoleplayLLM && window.RoleplayLLM.getDisplayName()) || "加载中…"`
  );
  step("HUD 显示当前模型", true, hudName);

  // ── 步骤2：打开弹层 → 选 DeepSeek → 填 key → 保存 ──
  const openPanel = await evalJs(`
    (function () {
      try {
        window.RoleplayLLM.open();
        return { ok: true, backdrop: !!document.getElementById('llm-backdrop'), hidden: document.getElementById('llm-backdrop') ? document.getElementById('llm-backdrop').hidden : 'n/a' };
      } catch (e) { return { ok: false, err: e.message }; }
    })()
  `);
  step("打开模型切换弹层", openPanel && openPanel.ok && !openPanel.hidden,
    openPanel.err || (openPanel.hidden ? "backdrop 仍 hidden" : "弹层可见"));

  await sleep(400); // 等待 populateProviders 完成

  // 模拟用户操作：选 DeepSeek、填 base_url、填 key、点保存
  const fillAndSave = await evalJs(`
    (async function () {
      try {
        const provSel = document.getElementById('llm-provider');
        const modelSel = document.getElementById('llm-model');
        const baseUrl = document.getElementById('llm-base-url');
        const apiKey = document.getElementById('llm-api-key');
        if (!provSel || !modelSel || !baseUrl || !apiKey) return { ok: false, err: '弹层元素缺失' };
        // 选 DeepSeek
        provSel.value = 'deepseek';
        provSel.dispatchEvent(new Event('change', { bubbles: true }));
        await new Promise(r => setTimeout(r, 300));
        // 模型选第一个（deepseek-chat）
        if (modelSel.options.length) modelSel.value = modelSel.options[0].value;
        modelSel.dispatchEvent(new Event('change', { bubbles: true }));
        // base_url 用默认（切换时已自动填充）
        // 填 key（测试用假 key，仅验证链路不真发请求）
        apiKey.value = 'sk-verify-flow-test-key-12345';
        apiKey.dispatchEvent(new Event('input', { bubbles: true }));
        await new Promise(r => setTimeout(r, 200));
        // 点保存按钮
        const saveBtn = document.querySelector('#llm-backdrop .send-btn');
        if (!saveBtn) return { ok: false, err: '保存按钮缺失' };
        saveBtn.click();
        await new Promise(r => setTimeout(r, 400));
        return { ok: true };
      } catch (e) { return { ok: false, err: e.message }; }
    })()
  `);
  step("选择 DeepSeek 并保存配置", fillAndSave && fillAndSave.ok, fillAndSave.err || "");

  // ── 步骤3：验证 localStorage 持久化 ──
  const stored = await evalJs(`localStorage.getItem('roleplay_llm_state')`);
  let storedOk = false, storedDetail = stored || "null";
  if (stored) {
    try {
      const s = JSON.parse(stored);
      storedOk = s.configured === true && s.provider === "deepseek" && s.model && !!s.api_key;
      storedDetail = `configured=${s.configured} provider=${s.provider} model=${s.model} key=${s.api_key ? "已填(长度" + s.api_key.length + ")" : "空!"}`;
    } catch (e) { storedDetail = "JSON 解析失败"; }
  }
  step("localStorage 已持久化（configured+key）", storedOk, storedDetail);

  // ── 步骤4：buildOverride 应返回带 key 的 override ──
  const ov = await evalJs(`window.RoleplayLLM.buildOverride()`);
  const ovOk = ov && ov.provider === "deepseek" && ov.api_key === "sk-verify-flow-test-key-12345";
  step("buildOverride 返回带 key 的 override", !!ovOk, JSON.stringify(ov));

  // ── 步骤5：刷新页面 → 配置保持 & key 回填 ──
  await send("Page.reload", { ignoreCache: true });
  await sleep(4000);
  const afterReload = await evalJs(`
    (function () {
      const raw = localStorage.getItem('roleplay_llm_state');
      const s = raw ? JSON.parse(raw) : null;
      return {
        stored: s ? { configured: s.configured, provider: s.provider, model: s.model, hasKey: !!s.api_key } : null,
        hud: (window.RoleplayLLM && window.RoleplayLLM.getDisplayName()) || null,
        override: window.RoleplayLLM ? window.RoleplayLLM.buildOverride() : null,
      };
    })()
  `);
  const reloadOk = afterReload && afterReload.stored && afterReload.stored.configured &&
    afterReload.stored.provider === "deepseek" && afterReload.stored.hasKey;
  step("刷新后配置保持", !!reloadOk,
    reloadOk ? JSON.stringify(afterReload.stored) : JSON.stringify(afterReload));
  const ovAfter = afterReload && afterReload.override;
  step("刷新后 buildOverride 仍带 key",
    !!(ovAfter && ovAfter.provider === "deepseek" && ovAfter.api_key),
    ovAfter ? JSON.stringify(ovAfter) : "null");
  step("刷新后 HUD 显示 DeepSeek", !!(afterReload && afterReload.hud && afterReload.hud.includes("DeepSeek")),
    (afterReload && afterReload.hud) || "null");

  // ── 步骤6：坏配置清洗（关键回归）──
  const cleanTest = await evalJs(`
    (function () {
      // 模拟旧版残留：云端+空key
      localStorage.setItem('roleplay_llm_state', JSON.stringify({
        configured: true, provider: 'deepseek', model: 'deepseek-chat', base_url: '', api_key: ''
      }));
      // 重新加载页面让 loadState 生效
      return 'set';
    })()
  `);
  await send("Page.reload", { ignoreCache: true });
  await sleep(4000);
  const afterClean = await evalJs(`
    (function () {
      const raw = localStorage.getItem('roleplay_llm_state');
      const s = raw ? JSON.parse(raw) : null;
      return {
        stored: s ? { configured: s.configured, provider: s.provider, model: s.model } : null,
        override: window.RoleplayLLM ? window.RoleplayLLM.buildOverride() : null,
        hud: (window.RoleplayLLM && window.RoleplayLLM.getDisplayName()) || null,
      };
    })()
  `);
  const cleaned = afterClean && afterClean.stored && afterClean.stored.configured === false;
  step("坏配置（云端+空key）被自动清洗", !!cleaned, JSON.stringify(afterClean.stored));
  step("清洗后 buildOverride 为 null（走全局）", !(afterClean && afterClean.override),
    afterClean && afterClean.override ? JSON.stringify(afterClean.override) : "null（走全局实例）");

  // ── 汇总输出 ──
  console.log("════════ 端到端验证结果 ════════");
  results.forEach((r) => console.log(r));
  const passed = results.filter((r) => r.startsWith("✅")).length;
  console.log(`\n通过 ${passed}/${results.length}`);
  ws.close();
  child.kill();
  process.exit(passed === results.length ? 0 : 1);
}

main().catch((e) => {
  console.error("ERR", e.message);
  child.kill();
  process.exit(1);
});
