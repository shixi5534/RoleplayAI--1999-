// 验证：保存 DeepSeek 配置后，聊天请求体确实携带 llm override
const { spawn } = require("child_process");
const EDGE = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe";
const PORT = 10095;
const child = spawn(EDGE, [
  "--headless=new", `--remote-debugging-port=${PORT}`,
  "--user-data-dir=C:/Users/Lenovo/WorkBuddy/2026-07-27-16-45-03/.edge-chat",
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

  // 拦截 fetch，捕获聊天请求体
  await evalJs(`
    (function () {
      window.__capturedBodies = [];
      const origFetch = window.fetch;
      window.fetch = function (url, opts) {
        try {
          if (typeof url === 'string' && url.indexOf('/chat/stream') !== -1 && opts && opts.body) {
            window.__capturedBodies.push({ url, body: opts.body });
          }
        } catch (_) {}
        return origFetch.apply(this, arguments);
      };
      return 'fetch 已拦截';
    })()
  `);

  // 配置 DeepSeek（分步）
  await evalJs("window.RoleplayLLM.open()");
  await sleep(400);
  await evalJs("(() => { const s = document.getElementById('llm-provider'); s.value='deepseek'; s.dispatchEvent(new Event('change',{bubbles:true})); })()");
  await sleep(400);
  await evalJs("(() => { const m = document.getElementById('llm-model'); m.value = m.options[0].value; m.dispatchEvent(new Event('change',{bubbles:true})); })()");
  await sleep(300);
  await evalJs("(() => { const k = document.getElementById('llm-api-key'); k.value='sk-chat-verify-key'; k.dispatchEvent(new Event('input',{bubbles:true})); })()");
  await sleep(200);
  await evalJs("document.querySelector('#llm-backdrop .send-btn').click()");
  await sleep(500);

  // 发一条消息（消息框 + 发送按钮）
  await evalJs(`
    (function () {
      const input = document.getElementById('message-input');
      if (!input) return 'NO INPUT: ' + Array.from(document.querySelectorAll('input,textarea')).map(e => e.id || e.className).join(',');
      input.value = '你好';
      input.dispatchEvent(new Event('input', { bubbles: true }));
      return 'input ok';
    })()
  `);
  await sleep(300);
  await evalJs(`
    (function () {
      const btn = document.getElementById('send-btn');
      if (!btn) return 'NO BTN';
      btn.click();
      return 'clicked';
    })()
  `);
  await sleep(2000);

  const bodies = await evalJs("window.__capturedBodies || []");
  console.log("捕获的聊天请求体:", bodies.length ? bodies.map(b => b.body) : "无（消息框/按钮选择器可能不对）");

  const llmField = bodies.length && bodies[0] && bodies[0].body ? JSON.parse(bodies[0].body).llm : null;
  console.log("请求体 llm 字段:", JSON.stringify(llmField));
  const ok = llmField && llmField.provider === "deepseek" && llmField.api_key === "sk-chat-verify-key";
  console.log(ok ? "✅ 聊天请求确实携带云端 override（含 key）" : "❌ 请求体未携带 override");
  ws.close(); child.kill(); process.exit(ok ? 0 : 1);
}
main().catch(e => { console.error("ERR", e.message); child.kill(); process.exit(1); });
