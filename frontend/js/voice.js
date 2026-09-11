/*
 * voice.js —— 语音输入/输出前端模块
 *
 * 职责：
 *   1. 录音（MediaRecorder，采集 webm/opus）
 *   2. 上传到 /voice/stt → 返回识别文本，回填输入框
 *   3. 拉取 /voice/tts → 播放 MP3 音频流（Audio 元素）
 *   4. 维护语音设置（音色/语速），localStorage 持久化
 *
 * 对外暴露：window.RoleplayVoice
 *   - init()                绑定按钮
 *   - startRecording()      开始录音
 *   - stopRecording()       停止并上传识别
 *   - speak(text, opts)     合成并播放语音
 *   - stopSpeaking()        停止播放
 *   - getSettings()         读取语音设置
 *   - isRecording()         是否正在录音
 *   - isSpeaking()          是否正在播放
 *
 * 依赖：无第三方库，纯原生 API。后端需启用 STT/TTS（见 voice.py）。
 * 降级：浏览器不支持 MediaRecorder 或后端未启用时，麦克风按钮自动隐藏。
 */
(function () {
  "use strict";

  const API_BASE = ""; // 同源；跨域时改为后端地址

  // ───────────────────────── 默认设置 + 持久化 ─────────────────────────
  const DEFAULT_VOICE_STATE = {
    voice_enabled: true,       // 语音功能总开关
    auto_tts: false,           // AI 回复后自动朗读
    voice_id: "",              // 音色 ID（留空用后端默认）
    tts_speed: 1.0,            // 语速 0.5-2.0
    tts_volume: 100,           // 音量 0-100
  };

  function loadVoiceState() {
    const state = Object.assign({}, DEFAULT_VOICE_STATE);
    try {
      const raw = localStorage.getItem("roleplay_voice_state");
      if (raw) {
        const parsed = JSON.parse(raw);
        Object.assign(state, parsed);
        // 数值字段类型校验：localStorage 中若为字符串/NaN（旧版本/手改），
        // 第 385 行 voiceState.tts_speed.toFixed(1) 会抛 TypeError，语音面板打不开。
        const num = (v, fallback) => {
          const n = Number(v);
          return Number.isFinite(n) ? n : fallback;
        };
        state.tts_speed = num(state.tts_speed, DEFAULT_VOICE_STATE.tts_speed);
        state.tts_volume = num(state.tts_volume, DEFAULT_VOICE_STATE.tts_volume);
        // 值域约束：与面板 min/max 对齐
        state.tts_speed = Math.min(2.0, Math.max(0.5, state.tts_speed));
        state.tts_volume = Math.min(100, Math.max(0, state.tts_volume));
      }
    } catch (_) {}
    return state;
  }

  function saveVoiceState() {
    try { localStorage.setItem("roleplay_voice_state", JSON.stringify(voiceState)); } catch (_) {}
  }

  const voiceState = loadVoiceState();

  // ───────────────────────── 内部状态 ─────────────────────────
  let mediaRecorder = null;
  let audioChunks = [];
  let recordingStream = null;
  let recordingTimer = null;
  let currentAudio = null;     // 正在播放的 Audio 元素
  let speakGen = 0;            // speak() 代际令牌：防并发竞态导致音频重叠
  let starting = false;        // startRecording 并发锁：防快速连点导致 getUserMedia 流泄漏
  let micGen = 0;              // 麦克风会话代际：stop 后使 await 中的 startRecording 失效并释放流
  let micBtn = null;
  let voicePanelBtn = null;
  let voicePanel = null;
  let initialized = false;

  // ───────────────────────── 工具 ─────────────────────────
  function toast(icon, label, value) {
    const toastEl = document.getElementById("toasts");
    if (!toastEl) return;
    const t = document.createElement("div");
    t.className = "toast";
    const iconSpan = document.createElement("span");
    iconSpan.className = "t-icon";
    iconSpan.textContent = icon;
    const labelSpan = document.createElement("span");
    labelSpan.textContent = label;
    t.appendChild(iconSpan);
    t.appendChild(labelSpan);
    if (value != null) {
      const valSpan = document.createElement("span");
      valSpan.className = "t-val";
      valSpan.textContent = value;
      t.appendChild(valSpan);
    }
    toastEl.appendChild(t);
    setTimeout(() => t.remove(), 1900);
  }

  /** 检测浏览器是否支持录音 */
  function isRecordingSupported() {
    return !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia && window.MediaRecorder);
  }

  // ───────────────────────── 录音（STT） ─────────────────────────
  async function startRecording() {
    if (!isRecordingSupported()) {
      toast("⚠️", "浏览器不支持录音");
      return;
    }
    if (mediaRecorder && mediaRecorder.state === "recording") return;
    // 并发锁：getUserMedia 是异步的，await 期间再次点击会重复申请流，
    // 前一个流无人释放（麦克风指示灯常亮、页面 title 显示"正在使用麦克风"）。
    if (starting) return;
    starting = true;
    const gen = ++micGen;

    let stream = null;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch (e) {
      starting = false;
      toast("⚠️", "麦克风权限被拒");
      return;
    }
    // 代际校验：await 期间 stopRecording() 已被调用，本次会话作废，
    // 立即释放刚拿到的流，避免泄漏。
    if (gen !== micGen) {
      stream.getTracks().forEach((t) => t.stop());
      starting = false;
      return;
    }
    recordingStream = stream;
    starting = false;

    // 优先使用 webm/opus，Safari 回退到 mp4
    let mimeType = "audio/webm;codecs=opus";
    if (!MediaRecorder.isTypeSupported(mimeType)) {
      mimeType = "audio/webm";
      if (!MediaRecorder.isTypeSupported(mimeType)) {
        mimeType = "audio/mp4";
        if (!MediaRecorder.isTypeSupported(mimeType)) mimeType = "";
      }
    }

    // ── 录音会话封装（F3）：stream/chunks/startTs 按「本次会话」捕获 ──
    // 旧实现 onstop 闭包读模块级 recordingStream/audioChunks：
    // 「停止后立刻重录」时旧 onstop 会停掉新录音的音轨并上传新会话的空/混合数据。
    // 现在每个会话持有自己的本地引用，onstop 只操作本会话资源。
    const sessionStream = stream;
    const sessionChunks = [];
    const sessionStartTs = Date.now();
    audioChunks = sessionChunks;
    mediaRecorder = mimeType
      ? new MediaRecorder(sessionStream, { mimeType })
      : new MediaRecorder(sessionStream);

    mediaRecorder.ondataavailable = (e) => {
      if (e.data && e.data.size > 0) sessionChunks.push(e.data);
    };

    mediaRecorder.onstop = async () => {
      // 只停本会话的音轨（模块级 recordingStream 可能已被新会话替换）
      sessionStream.getTracks().forEach((t) => t.stop());
      if (recordingStream === sessionStream) recordingStream = null;
      const duration = Date.now() - sessionStartTs;
      // 太短的录音直接忽略（<300ms 多为误触）
      if (duration < 300) {
        toast("ℹ️", "录音太短，已忽略");
        return;
      }
      await uploadForSTT(sessionChunks);
    };

    mediaRecorder.start();
    if (micBtn) {
      micBtn.classList.add("recording");
      micBtn.title = "正在录音…再次点击结束";
    }
    // 超时保护：最长 60 秒自动停止
    recordingTimer = setTimeout(() => {
      if (mediaRecorder && mediaRecorder.state === "recording") {
        stopRecording();
      }
    }, 60000);
    toast("🎙️", "开始录音");
  }

  function stopRecording() {
    // 代际推进：使 await 中的 startRecording() 作废（拿到流后立即释放）
    micGen++;
    if (recordingTimer) { clearTimeout(recordingTimer); recordingTimer = null; }
    if (mediaRecorder && mediaRecorder.state === "recording") {
      mediaRecorder.stop();
    }
    if (micBtn) {
      micBtn.classList.remove("recording");
      micBtn.title = "按住或点击录音（语音输入）";
    }
  }

  function toggleRecording() {
    if (mediaRecorder && mediaRecorder.state === "recording") {
      stopRecording();
    } else {
      startRecording();
    }
  }

  /** 上传录音到后端 STT，回填输入框（chunks 为本录音会话的分片，避免跨会话串数据） */
  async function uploadForSTT(chunks) {
    chunks = chunks || audioChunks;
    if (!chunks.length) return;
    const blob = new Blob(chunks, { type: chunks[0].type || "audio/webm" });
    const formData = new FormData();
    // 后端按 UploadFile 接收，文件名后缀帮助 Ollama Whisper 识别格式
    const ext = (blob.type || "").includes("mp4") ? "mp4" : "webm";
    formData.append("audio", blob, "recording." + ext);

    toast("⏳", "识别中…");
    try {
      const resp = await fetch(API_BASE + "/voice/stt", {
        method: "POST",
        body: formData,
      });
      if (!resp.ok) {
        const txt = await resp.text().catch(() => "");
        toast("⚠️", "语音识别失败", "HTTP " + resp.status);
        console.error("[voice] STT error:", resp.status, txt);
        return;
      }
      const data = await resp.json();
      const text = (data.text || "").trim();
      if (!text) {
        toast("ℹ️", "未识别到内容");
        return;
      }
      // 回填到输入框（追加模式，不覆盖已有内容）
      const inputEl = document.getElementById("message-input");
      if (inputEl) {
        const existing = inputEl.value.trim();
        inputEl.value = existing ? existing + " " + text : text;
        inputEl.focus();
        // 光标移到末尾
        inputEl.setSelectionRange(inputEl.value.length, inputEl.value.length);
      }
      // 桌面宠物钩子：宠物页接管识别结果（自动作为对话发送）。
      // 聊天页没有 RoleplayPet，此分支为 no-op，行为完全不变。
      if (window.RoleplayPet && typeof window.RoleplayPet.onVoiceInput === "function") {
        window.RoleplayPet.onVoiceInput(text);
      }
      toast("✅", "已识别", text.length > 12 ? text.slice(0, 12) + "…" : text);
    } catch (e) {
      toast("⚠️", "网络错误", e.message);
      console.error("[voice] STT fetch error:", e);
    }
  }

  // ───────────────────────── 播放（TTS） ─────────────────────────
  /**
   * 合成并播放语音。
   * @param {string} text 要朗读的文本
   * @param {object} opts { voice_id?, speed?, volume?, on_end?, on_error? }
   */
  async function speak(text, opts) {
    opts = opts || {};
    if (!text || !text.trim()) return;
    // 代际令牌：本次 speak 的唯一标识；fetch 完成后若令牌已变（期间有新 speak），
    // 说明已被更新的调用取代，直接丢弃本次结果，避免旧音频与新音频重叠播放。
    const gen = ++speakGen;
    // 停止当前正在播放的
    stopSpeaking();

    const params = new URLSearchParams();
    // 用 FormData 因为后端是 Form 参数
    const formData = new FormData();
    formData.append("text", text);
    const voiceId = opts.voice_id != null ? opts.voice_id : voiceState.voice_id;
    const speed = opts.speed != null ? opts.speed : voiceState.tts_speed;
    const volume = opts.volume != null ? opts.volume : voiceState.tts_volume;
    if (voiceId) formData.append("voice_id", voiceId);
    if (speed != null) formData.append("speed", String(speed));
    formData.append("volume", String(volume));

    try {
      const resp = await fetch(API_BASE + "/voice/tts", {
        method: "POST",
        body: formData,
      });
      if (!resp.ok) {
        const txt = await resp.text().catch(() => "");
        toast("⚠️", "语音合成失败", "HTTP " + resp.status);
        console.error("[voice] TTS error:", resp.status, txt);
        if (opts.on_error) opts.on_error(new Error("TTS HTTP " + resp.status));
        return;
      }
      const blob = await resp.blob();
      // 并发竞态守卫：fetch 完成时若已有更新的 speak（令牌变了），丢弃本次结果
      if (gen !== speakGen) return;
      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);
      audio._blobUrl = url; // 挂到实例上，供 stopSpeaking 中断时 revoke（pause 不触发 onended）
      currentAudio = audio;
      currentAudio.onended = () => {
        URL.revokeObjectURL(url);
        currentAudio = null;
        // 自然播完广播 tts:finished（live2d 待机调度监听：说完话播收尾微动作 + 恢复表情）。
        // 主动 stopSpeaking() 中断走 pause 路径不会触发 onended，因此不会误报「说完」。
        try {
          window.dispatchEvent(new CustomEvent("tts:finished", { detail: {} }));
        } catch (_) {}
        if (opts.on_end) opts.on_end();
      };
      currentAudio.onerror = (e) => {
        URL.revokeObjectURL(url);
        currentAudio = null;
        console.error("[voice] Audio playback error:", e);
        // 提示可读的错误原因（如 CSP 拦截 blob: 音频 / 解码失败），而非裸 ErrorEvent
        const msg = friendlyPlaybackError(e);
        if (msg) toast("⚠️", "播放失败", msg);
        if (opts.on_error) opts.on_error(e);
      };
      try {
        await currentAudio.play();
        // 播放正式开始才广播 tts:started（live2d 待机调度：说话中不插播待机动作）
        try {
          window.dispatchEvent(new CustomEvent("tts:started", { detail: {} }));
        } catch (_) {}
      } catch (playErr) {
        // play() 被 autoplay 策略拒绝（NotAllowedError）等：必须清理 blob URL 与
        // currentAudio 引用，否则 url 泄漏 + isSpeaking() 恒 true（状态假阳性）。
        URL.revokeObjectURL(url);
        if (currentAudio) {
          currentAudio.onended = null;
          currentAudio.onerror = null;
        }
        currentAudio = null;
        throw playErr;
      }
    } catch (e) {
      const msg = friendlyPlaybackError(e);
      toast("⚠️", "播放失败", msg || e.message);
      console.error("[voice] TTS fetch error:", e);
      if (opts.on_error) opts.on_error(e);
    }
  }

  /** 把音频播放异常转为可读的提示（CSP 拦截 / 格式不支持等）。 */
  function friendlyPlaybackError(e) {
    if (!e) return null;
    const n = (e.name || "") + (e.message || "");
    if (/NotSupportedError|MEDIA_ERR_SRC_NOT_SUPPORTED|no supported source/i.test(n)) {
      return "音频格式不支持或被浏览器安全策略拦截（CSP），请检查后端 TTS 是否返回有效 MP3";
    }
    if (/AbortError/i.test(n)) return null; // 主动 stopSpeaking 中断，不提示
    return e.message || null;
  }

  function stopSpeaking() {
    if (currentAudio) {
      const url = currentAudio._blobUrl;
      currentAudio.pause();
      currentAudio.onended = null;
      currentAudio.onerror = null;
      currentAudio = null;
      if (url) URL.revokeObjectURL(url); // 中断播放必须 revoke，否则 blob URL 泄漏
    }
  }

  // ───────────────────────── 语音设置面板 ─────────────────────────
  function buildVoicePanel() {
    // 面板已存在则不重建
    if (document.getElementById("voice-panel")) return;

    const panel = document.createElement("div");
    panel.id = "voice-panel";
    panel.className = "voice-panel";
    panel.hidden = true;
    panel.innerHTML = `
      <div class="voice-panel-header">
        <span>🔊 语音设置</span>
        <button type="button" id="voice-panel-close" class="voice-panel-close" title="关闭">×</button>
      </div>
      <div class="voice-panel-body">
        <label class="voice-row">
          <span class="voice-label">自动朗读回复</span>
          <input type="checkbox" id="voice-auto-tts" />
        </label>
        <label class="voice-row">
          <span class="voice-label">音色 ID</span>
          <input type="text" id="voice-voice-id" placeholder="留空用默认" />
        </label>
        <label class="voice-row">
          <span class="voice-label">语速 <span id="voice-speed-val">1.0</span>×</span>
          <input type="range" id="voice-speed" min="0.5" max="2.0" step="0.1" />
        </label>
        <label class="voice-row">
          <span class="voice-label">音量 <span id="voice-volume-val">100</span></span>
          <input type="range" id="voice-volume" min="0" max="100" step="5" />
        </label>
        <button type="button" id="voice-test-btn" class="voice-test-btn">试听</button>
      </div>
    `;
    document.body.appendChild(panel);

    // 绑定面板事件
    const closeBtn = document.getElementById("voice-panel-close");
    if (closeBtn) closeBtn.addEventListener("click", () => toggleVoicePanel(false));

    const autoTtsEl = document.getElementById("voice-auto-tts");
    const voiceIdEl = document.getElementById("voice-voice-id");
    const speedEl = document.getElementById("voice-speed");
    const speedVal = document.getElementById("voice-speed-val");
    const volumeEl = document.getElementById("voice-volume");
    const volumeVal = document.getElementById("voice-volume-val");

    // 初始化面板控件值
    autoTtsEl.checked = !!voiceState.auto_tts;
    voiceIdEl.value = voiceState.voice_id || "";
    speedEl.value = String(voiceState.tts_speed);
    speedVal.textContent = voiceState.tts_speed.toFixed(1);
    volumeEl.value = String(voiceState.tts_volume);
    volumeVal.textContent = voiceState.tts_volume;

    autoTtsEl.addEventListener("change", () => {
      voiceState.auto_tts = autoTtsEl.checked;
      saveVoiceState();
    });
    voiceIdEl.addEventListener("change", () => {
      voiceState.voice_id = voiceIdEl.value.trim();
      saveVoiceState();
    });
    speedEl.addEventListener("input", () => {
      voiceState.tts_speed = parseFloat(speedEl.value);
      speedVal.textContent = voiceState.tts_speed.toFixed(1);
      saveVoiceState();
    });
    volumeEl.addEventListener("input", () => {
      voiceState.tts_volume = parseInt(volumeEl.value, 10);
      volumeVal.textContent = voiceState.tts_volume;
      saveVoiceState();
    });

    const testBtn = document.getElementById("voice-test-btn");
    if (testBtn) {
      testBtn.addEventListener("click", () => {
        speak("你好，这是语音试听测试。", {});
      });
    }

    // 点击面板外部关闭
    panel.addEventListener("click", (e) => {
      if (e.target === panel) toggleVoicePanel(false);
    });

    voicePanel = panel;
  }

  function toggleVoicePanel(force) {
    if (!voicePanel) buildVoicePanel();
    const show = force != null ? force : voicePanel.hidden;
    voicePanel.hidden = !show;
  }

  // ───────────────────────── 初始化 ─────────────────────────
  function init() {
    if (initialized) return;
    initialized = true;

    micBtn = document.getElementById("mic-btn");
    voicePanelBtn = document.getElementById("voice-panel-btn");

    // 浏览器不支持录音时隐藏麦克风按钮
    if (micBtn && !isRecordingSupported()) {
      micBtn.style.display = "none";
    }

    if (micBtn) {
      micBtn.addEventListener("click", toggleRecording);
    }
    if (voicePanelBtn) {
      voicePanelBtn.addEventListener("click", () => toggleVoicePanel());
    }

    // 构建设置面板（延迟构建，首次打开时才填充）
    buildVoicePanel();

    console.log("[voice] 语音模块已初始化");
  }

  // ───────────────────────── 对外接口 ─────────────────────────
  window.RoleplayVoice = {
    init,
    startRecording,
    stopRecording,
    toggleRecording,
    speak,
    stopSpeaking,
    isRecording: () => !!(mediaRecorder && mediaRecorder.state === "recording"),
    isSpeaking: () => !!currentAudio,
    getSettings: () => Object.assign({}, voiceState),
    toggleVoicePanel,
  };

  // DOMContentLoaded 后自动初始化（若 chat.js 尚未提供 DOM 则等待）
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
