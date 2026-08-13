// 最终端到端验证（分步执行，模拟真实用户操作）
// 验证：弹层操作 → 保存 → 持久化 → 刷新保持 → 坏配置清洗
const { spawn } = require("child_process");
const EDGE = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe";
const PORT = 10094;
const child = spawn(EDGE, [
  "--headless=new", `--remote-debugging-port=${PORT}`,
  "--user-data-dir=C:/Users/Lenovo/WorkBuddy/2026-07-27-16-45-03/.edge-final",
  "--no-first-run", "--no-default-browser-check", "--disable-sync",
  "--disable-features=msEdgeSyncConfirmation", "--disable-component-update",
  "http://127.0.0.1:8000/",
], { stdio: "ignore" });
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
async function main() {
  await sleep(6000);
  let pages;
  for (let i = 0; i < 15; i++) {
    try { const res = await fetch(`http://127.0.0.1:${PORT}/json`); pages = await res.json(); if (pages.length) break; } catch (_) {}
    await sleep(1000);
  }
  const page = pages.find(t => t.type === "page" && t.url.includes("8000")) || pages.find(t => t.type === "page");
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  let id = 0; const pending = new Map();
  const send = (m, p = {}) => new Promise(r => { const mid = ++id; pending.set(mid, r); ws.send(JSON.stringify({ id: mid, method: m, params: p })); });
  ws.onmessage = (ev) => { const msg = JSON.parse(ev.data); if (msg.id && pending.has(msg.id)) { pending.get(msg.id)(msg.result); pending.delete(msg.id); } };
  await new Promise(r => ws.onopen = r);
  await sleep(3500);
  const evalJs = async (expr) => { const r = await send("Runtime.evaluate", { expression: expr, returnByValue: true, awaitPromise: true }); return r.result?.value; };

  const results = [];
  const step = (name, ok, detail) =>
    results.push((ok ? "✅ " : "❌ ") + name + (detail ? " — " + detail : ""));

  // 1. 模块加载 & HUD
  step("RoleplayLLM 模块已加载", await evalJs("!!(window.RoleplayLLM && window.RoleplayLLM.buildOverride)"), "");
  const hud0 = await evalJs("window.RoleplayLLM.getDisplayName()");
  step("HUD 初始显示全局模型", !!hud0, hud0);

  // 2. 打开弹层
  await evalJs("window.RoleplayLLM.open()");
  await sleep(400);
  const opened = await evalJs("!document.getElementById('llm-backdrop').hidden");
  step("打开模型切换弹层", opened, "");

  // 3. 切 DeepSeek + 填 key（分步）
  await evalJs("(() => { const s = document.getElementById('llm-provider'); s.value='deepseek'; s.dispatchEvent(new Event('change',{bubbles:true})); })()");
  await sleep(400);
  await evalJs("(() => { const m = document.getElementById('llm-model'); m.value = m.options[0].value; m.dispatchEvent(new Event('change',{bubbles:true})); })()");
  await sleep(300);
  await evalJs("(() => { const k = document.getElementById('llm-api-key'); k.value='sk-e2e-final-key-888'; k.dispatchEvent(new Event('input',{bubbles:true})); })()");
  await sleep(200);
  const formState = await evalJs("({ provider: document.getElementById('llm-provider').value, model: document.getElementById('llm-model').value, baseUrl: document.getElementById('llm-base-url').value, key: document.getElementById('llm-api-key').value })");
  step("表单已选 DeepSeek 并填 key", formState.provider === "deepseek" && formState.key === "sk-e2e-final-key-888", JSON.stringify(formState));

  // 4. 保存
  await evalJs("document.querySelector('#llm-backdrop .send-btn').click()");
  await sleep(600);
  const stored = await evalJs("JSON.parse(localStorage.getItem('roleplay_llm_state'))");
  step("保存后 localStorage 持久化（含 key）", stored && stored.configured === true && stored.provider === "deepseek" && stored.api_key === "sk-e2e-final-key-888", stored ? JSON.stringify({ configured: stored.configured, provider: stored.provider, model: stored.model, keyLen: stored.api_key ? stored.api_key.length : 0 }) : "null");

  // 5. buildOverride 带 key
  const ov = await evalJs("window.RoleplayLLM.buildOverride()");
  step("buildOverride 返回带 key 的 override", !!(ov && ov.provider === "deepseek" && ov.api_key === "sk-e2e-final-key-888"), ov ? JSON.stringify(ov) : "null");

  // 6. 刷新保持
  await send("Page.reload", { ignoreCache: true });
  await sleep(4500);
  const afterReload = await evalJs("(() => { const s = JSON.parse(localStorage.getItem('roleplay_llm_state')); return { stored: s ? { configured: s.configured, provider: s.provider, hasKey: !!s.api_key } : null, hud: window.RoleplayLLM.getDisplayName(), ov: window.RoleplayLLM.buildOverride() }; })()");
  step("刷新后配置保持（key 未丢）", !!(afterReload.stored && afterReload.stored.configured && afterReload.stored.hasKey), JSON.stringify(afterReload.stored));
  step("刷新后 buildOverride 仍带 key", !!(afterReload.ov && afterReload.ov.api_key), afterReload.ov ? JSON.stringify(afterReload.ov) : "null");
  step("刷新后 HUD 显示 DeepSeek", !!(afterReload.hud && afterReload.hud.includes("DeepSeek")), afterReload.hud);

  // 7. 坏配置清洗（关键回归）
  await evalJs("localStorage.setItem('roleplay_llm_state', JSON.stringify({configured:true, provider:'deepseek', model:'deepseek-chat', base_url:'', api_key:''}))");
  await send("Page.reload", { ignoreCache: true });
  await sleep(4500);
  const afterClean = await evalJs("(() => { const s = JSON.parse(localStorage.getItem('roleplay_llm_state')); return { stored: s, ov: window.RoleplayLLM.buildOverride(), hud: window.RoleplayLLM.getDisplayName() }; })()");
  step("坏配置（云端+空key）被自动清洗为未配置", !!(afterClean.stored && afterClean.stored.configured === false), JSON.stringify(afterClean.stored));
  step("清洗后 buildOverride 为 null（走全局）", !(afterClean.ov && afterClean.ov.api_key), afterClean.ov ? JSON.stringify(afterClean.ov) : "null（走全局实例）");

  // 汇总
  console.log("════════ 最终端到端验证 ════════");
  results.forEach(r => console.log(r));
  const passed = results.filter(r => r.indexOf("✅") === 0).length;
  console.log("\n通过 " + passed + "/" + results.length);
  ws.close(); child.kill(); process.exit(passed === results.length ? 0 : 1);
}
main().catch(e => { console.error("ERR", e.message); child.kill(); process.exit(1); });
