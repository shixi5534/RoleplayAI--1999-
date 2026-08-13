/*
 * llm-switch.js —— 模型切换前端模块（本地 Ollama ↔ 云端 OpenAI/DeepSeek）
 *
 * 职责：
 *   1. 顶栏「模型」按钮 + 弹层：provider / model / base_url / api_key 配置
 *   2. Ollama 本地模型列表实时拉取（/api/llm/ollama/models），云端预设来自 /api/llm/config
 *   3. 连通性测试（/api/llm/test，api_key 仅本次请求，后端不落盘）
 *   4. localStorage 持久化；聊天请求携带 llm 覆盖字段（buildOverride）
 *
 * 对外暴露：window.RoleplayLLM
 *   - init()              绑定顶栏按钮、拉取全局配置、渲染 HUD
 *   - toggle()/open()/close()/isOpen()  弹层控制
 *   - buildOverride()     生成聊天请求的 llm 覆盖字段（与全局一致时返回 null 走全局实例）
 *   - getDisplayName()    HUD 显示用：当前生效的 provider · model
 *   - onChanged(cb)       配置变化回调（chat.js 用于刷新 HUD）
 *
 * 设计约束：
 *   - 无第三方依赖，纯原生 JS；所有 DOM 动态创建（与 voice.js 一致）。
 *   - CSP 兼容：无内联脚本；样式类复用 index.html 内既有定义。
 *   - api_key 仅存 localStorage（浏览器侧），后端不落盘、不进日志。
 */
(function () {
  "use strict";

  const API_BASE = ""; // 同源；跨域时改为后端地址

  // 与后端 openai_like._DEFAULT_BASE_URLS / llm_config.CLOUD_PRESETS 保持一致的前端镜像
  const DEFAULT_BASE_URLS = {
    openai: "https://api.openai.com/v1",
    deepseek: "https://api.deepseek.com/v1",
    ollama: "http://localhost:11434/v1",
  };
  const OLLAMA_DEFAULT_URL = "http://localhost:11434";
  const DEFAULT_OLLAMA_MODELS = ["qwen2.5:1.5b", "qwen2.5:7b", "qwen2.5:14b", "llama3.1:8b", "deepseek-r1:7b"];

  // ───────────────────────── 状态 + 持久化 ─────────────────────────
  const DEFAULT_LLM_STATE = {
    configured: false, // 用户是否显式配置过（false 时聊天请求不带 llm 字段，走全局配置）
    provider: "ollama",
    model: "",
    base_url: "",
    api_key: "",
  };

  function loadState() {
    let st = Object.assign({}, DEFAULT_LLM_STATE);
    let raw = null;
    try {
      raw = localStorage.getItem("roleplay_llm_state");
      if (raw) st = Object.assign({}, DEFAULT_LLM_STATE, JSON.parse(raw));
    } catch (_) {}
    // 存量配置清洗：云端 provider（openai/deepseek）无 api_key 属坏配置——
    // 旧版本无「云端必填 key」校验，可能残留 configured=true 但 key 为空的记录，
    // 会导致 HUD 显示云端、实际 buildOverride 发出无 key override、后端必失败。
    // 一律视为未配置（走全局），避免「显示与实际不符」。
    if (st.configured && st.provider !== "ollama" && !st.api_key) {
      st = Object.assign({}, DEFAULT_LLM_STATE);
      // 干净配置回写 localStorage：根治「每次刷新重新清洗、坏值永远残留」，
      // 避免未来逻辑变更后坏值重新生效。
      try { localStorage.setItem("roleplay_llm_state", JSON.stringify(st)); } catch (_) {}
    }
    return st;
  }
  function saveState() {
    try { localStorage.setItem("roleplay_llm_state", JSON.stringify(state)); } catch (_) {}
  }

  const state = loadState();

  // 后端全局配置缓存（脱敏）：{provider, model, base_url, has_api_key, cloud_presets, ollama_default_url}
  let serverConfig = null;
  // provider 标签（HUD / 下拉）
  const PROVIDER_LABELS = {
    ollama: "本地 Ollama",
    openai: "OpenAI",
    deepseek: "DeepSeek",
    mock: "内置模拟",
  };
  // 变更回调（chat.js 刷新 HUD）
  const changeCallbacks = [];
  function onChanged(cb) { changeCallbacks.push(cb); }
  function emitChanged() { changeCallbacks.forEach((cb) => { try { cb(); } catch (_) {} }); }

  // ───────────────────────── DOM 引用（init 时填充） ─────────────────────────
  let backdrop = null;
  let providerSel = null;
  let modelSel = null;
  let baseUrlInput = null;
  let apiKeyInput = null;
  let testBtn = null;
  let testResultEl = null;
  let saveBtn = null;
  let resetBtn = null;
  let initialized = false;

  function toast(icon, label, value) {
    const toastEl = document.getElementById("toasts");
    if (!toastEl) return;
    const t = document.createElement("div");
    t.className = "toast";
    const i = document.createElement("span");
    i.className = "t-icon";
    i.textContent = icon;
    const l = document.createElement("span");
    l.textContent = label;
    t.appendChild(i);
    t.appendChild(l);
    if (value != null) {
      const v = document.createElement("span");
      v.className = "t-val";
      v.textContent = value;
      t.appendChild(v);
    }
    toastEl.appendChild(t);
    setTimeout(() => t.remove(), 1900);
  }

  // ───────────────────────── 弹层构建（动态注入，与 voice.js 面板一致） ─────────────────────────
  function buildPanel() {
    if (backdrop) return;
    backdrop = document.createElement("div");
    backdrop.className = "modal-backdrop";
    backdrop.id = "llm-backdrop";
    backdrop.hidden = true;

    const panel = document.createElement("div");
    panel.className = "modal-panel";
    panel.style.width = "min(520px, 94vw)";
    panel.setAttribute("role", "dialog");
    panel.setAttribute("aria-modal", "true");
    panel.setAttribute("aria-label", "模型切换");

    const closeX = document.createElement("button");
    closeX.className = "close-x";
    closeX.type = "button";
    closeX.title = "关闭 (Esc)";
    closeX.textContent = "×";
    closeX.addEventListener("click", close);

    const h2 = document.createElement("h2");
    h2.textContent = "🤖 模型切换";
    const sub = document.createElement("p");
    sub.className = "sub";
    sub.textContent = "在本地 Ollama 与云端模型之间切换；配置仅保存在浏览器（localStorage），API Key 不落盘、不进日志。";

    // 接入方式
    providerSel = document.createElement("select");
    providerSel.id = "llm-provider";
    providerSel.addEventListener("change", onProviderChange);

    const providerWrap = makeField("接入方式", providerSel, "本地 Ollama：完全离线，免 Key；云端：需填入对应 API Key");

    // 模型下拉
    modelSel = document.createElement("select");
    modelSel.id = "llm-model";
    const modelWrap = makeField("模型", modelSel, "Ollama 会实时拉取本地已安装模型；云端为官方预设");

    // Base URL
    baseUrlInput = document.createElement("input");
    baseUrlInput.id = "llm-base-url";
    baseUrlInput.type = "text";
    baseUrlInput.placeholder = DEFAULT_BASE_URLS.ollama;
    baseUrlInput.addEventListener("input", () => { clearTestResult(); });
    // 手填过 base_url 后标记 touched，切换 provider 时不再被自动填充覆盖。
    // 必须在 buildPanel() 里绑定（panel 未构建时 init() 里 baseUrlInput 为 null，
    // 之前 init() 里的绑定被守卫跳过，导致 touched 永不生效、手填值必被覆盖）。
    baseUrlInput.addEventListener("input", () => { baseUrlInput.dataset.touched = "1"; });
    const baseUrlWrap = makeField("Base URL", baseUrlInput, "OpenAI 兼容地址，切换预设时自动填充");

    // API Key
    apiKeyInput = document.createElement("input");
    apiKeyInput.id = "llm-api-key";
    apiKeyInput.type = "password";
    apiKeyInput.placeholder = "sk-…（云端必填，本地 Ollama 可留空）";
    apiKeyInput.addEventListener("input", () => { clearTestResult(); });
    const apiKeyWrap = makeField("API Key", apiKeyInput, "仅保存在本浏览器；后端只在本请求使用一次，绝不落盘");

    // 操作行：刷新本地模型 / 测试连通
    const actions1 = document.createElement("div");
    actions1.className = "llm-actions";
    const refreshBtn = document.createElement("button");
    refreshBtn.type = "button";
    refreshBtn.className = "clear-btn";
    refreshBtn.textContent = "🔄 刷新本地模型";
    refreshBtn.addEventListener("click", () => refreshOllamaModels(true));
    testBtn = document.createElement("button");
    testBtn.type = "button";
    testBtn.className = "clear-btn";
    testBtn.textContent = "🧪 测试连通";
    testBtn.addEventListener("click", testConnection);
    testResultEl = document.createElement("span");
    testResultEl.className = "llm-test-result";
    testResultEl.textContent = "";
    actions1.appendChild(refreshBtn);
    actions1.appendChild(testBtn);
    actions1.appendChild(testResultEl);

    // 操作行：恢复默认 / 保存
    const actions2 = document.createElement("div");
    actions2.className = "llm-actions";
    actions2.style.justifyContent = "flex-end";
    resetBtn = document.createElement("button");
    resetBtn.type = "button";
    resetBtn.className = "clear-btn";
    resetBtn.textContent = "恢复默认";
    resetBtn.title = "取消自定义模型，恢复使用后端全局配置";
    resetBtn.addEventListener("click", resetOverride);
    saveBtn = document.createElement("button");
    saveBtn.type = "button";
    saveBtn.className = "send-btn";
    saveBtn.textContent = "保存并应用";
    saveBtn.addEventListener("click", saveConfig);
    actions2.appendChild(resetBtn);
    actions2.appendChild(saveBtn);

    panel.appendChild(closeX);
    panel.appendChild(h2);
    panel.appendChild(sub);
    panel.appendChild(providerWrap);
    panel.appendChild(modelWrap);
    panel.appendChild(baseUrlWrap);
    panel.appendChild(apiKeyWrap);
    panel.appendChild(actions1);
    panel.appendChild(actions2);
    backdrop.appendChild(panel);

    // 点遮罩关闭（与角色弹层一致：仅当点击 backdrop 本身）
    backdrop.addEventListener("click", (e) => {
      if (e.target === backdrop) close();
    });
    document.body.appendChild(backdrop);
  }

  function makeField(labelText, control, hint) {
    const label = document.createElement("label");
    label.className = "llm-field";
    const span = document.createElement("span");
    span.textContent = labelText;
    label.appendChild(span);
    label.appendChild(control);
    if (hint) {
      const em = document.createElement("em");
      em.textContent = hint;
      label.appendChild(em);
    }
    return label;
  }

  // ───────────────────────── 拉取后端全局配置（脱敏） ─────────────────────────
  async function loadServerConfig() {
    try {
      const resp = await fetch(API_BASE + "/api/llm/config");
      if (!resp.ok) return null;
      const data = await resp.json();
      serverConfig = data;
      return data;
    } catch (_) {
      serverConfig = null;
      return null;
    }
  }

  function labelOf(provider) {
    return PROVIDER_LABELS[provider] || provider || "未知";
  }

  /** HUD 显示名：自定义配置优先；否则显示全局配置。 */
  function getDisplayName() {
    if (state.configured && state.model) {
      return labelOf(state.provider) + " · " + state.model;
    }
    if (serverConfig) {
      const p = serverConfig.provider || "mock";
      const m = serverConfig.model || "";
      if (p === "mock") return "内置模拟 · " + m;
      return labelOf(p) + " · " + m;
    }
    return "加载中…";
  }

  /**
   * 生成聊天请求的 llm 覆盖字段。
   * - 未配置过 → null（走全局配置，零开销）。
   * - 与全局配置一致（provider/model/base_url 均同、无 api_key）→ null（复用全局实例）。
   * - 否则返回 { provider, model, base_url?, api_key? }，后端按请求级 override 构建一次性客户端。
   */
  function buildOverride() {
    if (!state.configured || !state.model) return null;
    const effectiveServerBase = (serverConfig && serverConfig.base_url) ||
      DEFAULT_BASE_URLS[(serverConfig && serverConfig.provider) || ""] || "";
    const effectiveUserBase = state.base_url || DEFAULT_BASE_URLS[state.provider] || "";
    const sameAsGlobal = serverConfig &&
      state.provider === serverConfig.provider &&
      state.model === serverConfig.model &&
      effectiveUserBase === effectiveServerBase &&
      !state.api_key;
    if (sameAsGlobal) return null;
    const o = { provider: state.provider, model: state.model };
    if (effectiveUserBase) o.base_url = effectiveUserBase;
    if (state.api_key) o.api_key = state.api_key;
    return o;
  }

  // ───────────────────────── 弹层开关 ─────────────────────────
  function open() {
    buildPanel();
    backdrop.hidden = false;
    void backdrop.offsetWidth; // 强制回流触发过渡
    backdrop.classList.add("open");
    populateProviders();
    // 仅本地 Ollama 模式才拉取本地模型列表；云端预设（DeepSeek/OpenAI）绝不能被 Ollama 列表污染
    if (providerSel && providerSel.value === "ollama") {
      refreshOllamaModels(false); // 静默刷新本地模型列表（失败回退默认）
    }
    clearTestResult();
  }
  function close() {
    if (!backdrop || backdrop.hidden) return;
    backdrop.classList.remove("open");
    setTimeout(() => { backdrop.hidden = true; }, 200);
  }
  function isOpen() {
    return !!(backdrop && !backdrop.hidden && backdrop.classList.contains("open"));
  }
  function toggle() {
    if (isOpen()) close();
    else open();
  }

  // ───────────────────────── 表单填充 ─────────────────────────
  function populateProviders() {
    // provider 下拉：本地 Ollama + 后端云端预设
    providerSel.innerHTML = "";
    const addOpt = (value, text) => {
      const opt = document.createElement("option");
      opt.value = value;
      opt.textContent = text;
      providerSel.appendChild(opt);
    };
    addOpt("ollama", "🖥️ " + PROVIDER_LABELS.ollama);
    const presets = (serverConfig && serverConfig.cloud_presets) || {};
    Object.keys(presets).forEach((key) => {
      const p = presets[key];
      addOpt(key, "☁️ " + (p.label || key));
    });
    // 全局 provider 不在候选里（如 mock）时仍允许显示，避免表单状态丢失
    if (!["ollama"].concat(Object.keys(presets)).includes(state.provider)) {
      addOpt(state.provider, labelOf(state.provider));
    }
    providerSel.value = state.provider;
    onProviderChange(false);
    // 回填已保存的 api_key（仅当前 provider 与已配置 provider 相同时回填，
    // 避免切换到其它 provider 时把旧 key 残留到新表单里；敏感字段只读回填，
    // 不触发任何事件、不改 placeholder）。
    if (apiKeyInput) {
      apiKeyInput.value =
        state.configured && state.provider === providerSel.value ? state.api_key : "";
    }
  }

  function defaultBaseUrlFor(provider) {
    if (serverConfig && serverConfig.provider === provider && serverConfig.base_url) {
      return serverConfig.base_url;
    }
    const presets = (serverConfig && serverConfig.cloud_presets) || {};
    const preset = presets[provider];
    if (preset && preset.base_url) return preset.base_url;
    return DEFAULT_BASE_URLS[provider] || "";
  }

  function defaultModelsFor(provider) {
    const presets = (serverConfig && serverConfig.cloud_presets) || {};
    const preset = presets[provider];
    if (preset && Array.isArray(preset.models) && preset.models.length) return preset.models;
    if (provider === "ollama") return DEFAULT_OLLAMA_MODELS;
    return [];
  }

  /** provider 变化时刷新模型下拉 + base_url。silent=true 时不重置用户已填的 api_key。 */
  async function onProviderChange(autoFetchModels) {
    const provider = providerSel.value;
    // base_url：用户改过才填充默认，避免覆盖手填值
    const presetBase = defaultBaseUrlFor(provider);
    if (!baseUrlInput.dataset.touched) baseUrlInput.value = presetBase;
    apiKeyInput.placeholder = provider === "ollama"
      ? "本地 Ollama 可留空"
      : "sk-…（云端必填）";
    // api_key：仅当切换回「已配置的同一 provider」时才回填；否则清空，
    // 避免把 A provider 的 key 误带到 B provider 的表单里，保存时串 key。
    if (apiKeyInput && state.configured && state.provider === provider) {
      apiKeyInput.value = state.api_key;
    } else if (apiKeyInput) {
      apiKeyInput.value = "";
    }

    // 模型下拉
    modelSel.innerHTML = "";
    const models = defaultModelsFor(provider);
    const currentModel = (state.configured && state.provider === provider && state.model) ||
      (serverConfig && serverConfig.provider === provider && serverConfig.model) || "";
    let hasCurrent = false;
    const candidates = models.length ? models : (currentModel ? [currentModel] : []);
    candidates.forEach((m) => {
      const opt = document.createElement("option");
      opt.value = m;
      opt.textContent = m;
      modelSel.appendChild(opt);
      if (m === currentModel) { modelSel.value = m; hasCurrent = true; }
    });
    if (!hasCurrent && currentModel) {
      const opt = document.createElement("option");
      opt.value = currentModel;
      opt.textContent = currentModel;
      modelSel.appendChild(opt);
      modelSel.value = currentModel;
    }
    if (!modelSel.value && candidates.length) modelSel.value = candidates[0];

    if (provider === "ollama" && autoFetchModels !== false) {
      await refreshOllamaModels(false);
    }
  }

  /** 拉取本地 Ollama 模型列表；失败回退默认清单并提示（不阻塞 UI）。
   *  守卫：仅当当前 provider 为 ollama 时才允许刷新模型下拉，
   *  防止云端（DeepSeek/OpenAI）面板被本地模型名（如 nomic-embed-text）污染。 */
  async function refreshOllamaModels(announce) {
    // 守卫：非 ollama 模式直接忽略（保护云端 model 下拉不被覆盖）
    if (!providerSel || providerSel.value !== "ollama") return;
    try {
      const resp = await fetch(API_BASE + "/api/llm/ollama/models");
      if (!resp.ok) {
        let detail = "HTTP " + resp.status;
        try {
          const errJson = await resp.json();
          const err = errJson && errJson.error;
          if (err && err.message) detail = err.message;
          else if (errJson && errJson.detail) detail = errJson.detail;
        } catch (_) { /* 保留 HTTP 状态 */ }
        throw new Error(detail);
      }
      const data = await resp.json();
      const models = (data && data.models) || [];
      if (!models.length) {
        if (announce) toast("⚠️", "Ollama 无模型", data.error || "未安装模型");
        return;
      }
      // 当前选中值优先保留
      const keep = modelSel ? modelSel.value : "";
      modelSel.innerHTML = "";
      models.forEach((m) => {
        const opt = document.createElement("option");
        opt.value = m;
        opt.textContent = m;
        modelSel.appendChild(opt);
      });
      if (keep && models.includes(keep)) modelSel.value = keep;
      else if (state.configured && state.provider === "ollama" && models.includes(state.model)) modelSel.value = state.model;
      else if (serverConfig && serverConfig.provider === "ollama" && models.includes(serverConfig.model)) modelSel.value = serverConfig.model;
      else if (models.length) modelSel.value = models[0];
      if (announce) toast("🔄", "已刷新本地模型", models.length + " 个");
    } catch (e) {
      if (announce) toast("⚠️", "无法连接 Ollama", e.message);
    }
  }

  // ───────────────────────── 连通性测试 ─────────────────────────
  function clearTestResult() {
    if (testResultEl) testResultEl.textContent = "";
  }

  async function testConnection() {
    const payload = collectForm();
    if (!payload.model) { toast("⚠️", "请先选择模型"); return; }
    testBtn.disabled = true;
    testBtn.textContent = "⏳ 测试中…";
    testResultEl.textContent = "";
    testResultEl.classList.remove("ok", "fail");
    try {
      const resp = await fetch(API_BASE + "/api/llm/test", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!resp.ok) {
        let detail = "HTTP " + resp.status;
        try {
          const errJson = await resp.json();
          const err = errJson && errJson.error;
          if (err && err.message) detail = err.message;
          else if (errJson && errJson.detail) detail = errJson.detail;
        } catch (_) { /* 保留 HTTP 状态 */ }
        throw new Error(detail);
      }
      const data = await resp.json();
      if (data.ok) {
        testResultEl.textContent = "✅ 连通成功：" + (data.detail || "ok");
        testResultEl.classList.add("ok");
      } else {
        testResultEl.textContent = "❌ " + (data.detail || "连接失败");
        testResultEl.classList.add("fail");
      }
    } catch (e) {
      testResultEl.textContent = "❌ 请求失败：" + e.message;
      testResultEl.classList.add("fail");
    } finally {
      testBtn.disabled = false;
      testBtn.textContent = "🧪 测试连通";
    }
  }

  // ───────────────────────── 保存 / 重置 ─────────────────────────
  function collectForm() {
    return {
      provider: providerSel.value,
      model: modelSel.value,
      base_url: baseUrlInput.value.trim(),
      api_key: apiKeyInput.value.trim(),
    };
  }

  function saveConfig() {
    const f = collectForm();
    if (!f.model) { toast("⚠️", "请选择模型"); return; }
    // 云端必须带 key（含纯空格 key 视为未填写），双保险防止写入「云端+空key」坏配置
    if (f.provider !== "ollama" && !f.api_key.trim()) {
      toast("⚠️", "云端需填写 API Key");
      return;
    }
    state.configured = true;
    state.provider = f.provider;
    state.model = f.model;
    state.base_url = f.base_url;
    state.api_key = f.api_key;
    saveState();
    close();
    emitChanged();
    toast("🤖", "已切换模型", getDisplayName());
  }

  /** 恢复默认：取消自定义，走后端全局配置。 */
  function resetOverride() {
    state.configured = false;
    state.provider = "ollama";
    state.model = "";
    state.base_url = "";
    state.api_key = "";
    saveState();
    close();
    emitChanged();
    toast("♻️", "已恢复默认", serverConfig ? getDisplayName() : "全局配置");
  }

  // ───────────────────────── 初始化 ─────────────────────────
  async function init() {
    if (initialized) return;
    initialized = true;
    // 拉取全局配置（脱敏），用于 HUD 显示与「与全局一致走全局实例」判定
    await loadServerConfig();
    // 顶栏按钮
    const btn = document.getElementById("btn-llm");
    if (btn) btn.addEventListener("click", toggle);
    // touched 绑定已移到 buildPanel()（panel 构建时 baseUrlInput 才存在），此处不再重复
    emitChanged(); // 首屏让 chat.js 刷新 HUD（此时 serverConfig 已就绪）
  }

  // 暴露全局 API
  window.RoleplayLLM = {
    init,
    toggle,
    open,
    close,
    isOpen,
    buildOverride,
    getDisplayName,
    onChanged,
  };
})();
