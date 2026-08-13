/*
 * live2d.js —— 角色数字人渲染层（基于素材包 viewer/app.js 验证过的逻辑移植）
 *
 * 与后端 SSE event:emotion 对接：情绪标签 → 表情/动作。
 * 依赖（必须在前文以正确顺序加载）：live2dcubismcore → pixi → pixi-live2d-display
 *
 * 关键约束（来自已验证的 viewer）：
 *  - Live2DModel.from 之前必须 PIXI.live2d.startUpCubism4()
 *  - Live2DModel.from(url, { autoInteract:true }) 自带鼠标跟随
 *  - 表情用 model3.json 的 Expressions 索引驱动（两套模型顺序不同，动态读取）
 *
 * 本版增强：
 *  - 多模型注册表 MODELS + switchModel()（PIXI App 复用，避免 ticker 泄漏 / 尺寸污染）
 *  - 拖拽：鼠标按住拖动模型，松手持久化偏移，双击复位
 *  - 显示修复：_fit 用 0.95 padding + y +0.12，更贴合舞台
 */
(function (global) {
  "use strict";

  // 模型注册表：新增模型只需在数组里加一项（url 指向对应 model3.json）。
  // 表情顺序差异已由 live2d.js 的动态 _exprIndex（按 name 建表）天然兼容，无需额外处理。
  const MODELS = [
    {
      id: "314701",
      name: "无名·初见",
      url: "./assets/live2d/wmz/314701/v3a7_314701_wmz.model3.json",
    },
    {
      id: "314702",
      name: "无名·无尽路",
      url: "./assets/live2d/wmz/314702/v3a7_314702_wmz.model3.json",
    },
  ];

  // ── 待机/互动调度配置（优化版：权重池 + 随机间隔 + 空闲分级）──
  // 待机权重池：轻动作高权重、重动作低权重，观感「活的」而非「躁的」。
  // 模型动作集差异由 _motionKeys 在运行时过滤兜底。
  const IDLE_POOL = [
    { name: "b_idle", w: 40 },    // 轻微呼吸，最常用
    { name: "t_idle", w: 20 },    // 轻微待机
    { name: "b_shanzi", w: 15 },  // 摇扇（中轻）
    { name: "b_diantou", w: 10 }, // 点头（轻）
    { name: "b_liaofa", w: 8 },   // 撩发（重）
    { name: "b_yaotou", w: 5 },   // 摇头（重）
    { name: "b_taishou", w: 2 },  // 抬手（重）
  ];
  // 扇子类动作变体（P2-7：模型自带 6 个扇子变体，触发扇子时随机选一个）
  const FAN_VARIANTS = ["b_shanzi", "b_shanzi1", "b_shanzi2", "b_shanzi3", "b_shanzi2_1", "b_shanzi2_2"];
  // 点击互动池：仅点击专属动作（与待机池语义分离，P2-8）
  const CLICK_POOL = [
    { name: "b_taishou", w: 30 }, // 抬手（点击专属感强）
    { name: "b_yaotou", w: 25 },  // 摇头
    { name: "b_zhelian", w: 20 }, // 遮脸（互动专属）
    { name: "b_diantou", w: 15 }, // 点头
    { name: "b_liaofa", w: 10 },  // 撩发
  ];
  // 待机调度：随机间隔范围（ms）——消除固定 12s 节拍感（P1-4）
  const IDLE_INTERVAL_MIN = 8000;
  const IDLE_INTERVAL_MAX = 18000;
  // 空闲分级（P2-6）：用户长时间无操作时降频，模拟「安静/犯困」状态
  const IDLE_SLEEP_AFTER = 90 * 1000;    // 90s 无互动 → 进入低频态
  const IDLE_DEEP_AFTER = 5 * 60 * 1000; // 5min 无互动 → 播一次「犯困」后进超低频
  const IDLE_SLEEP_MIN = 25000;          // 低频态间隔 25~40s
  const IDLE_SLEEP_MAX = 40000;
  // 表情超时自动恢复 neutral（P0-2）：情绪表情保持时长，超时无新情绪则回 e_idle
  const EMOTION_HOLD_MS = 10000;
  // 说话中/结束后动作联动（P1-5）
  const TTS_TAIL_GESTURES = ["b_diantou", "b_taishou", "b_shanzi"]; // 说完话收尾微动作池

  const RoleplayLive2D = {
    _ready: false,
    _model: null,
    _pixiApp: null,
    _container: null,
    _mapper: null,
    _exprIndex: {}, // expression name(lower) -> index
    _currentEmotion: null,
    _onResize: null,
    _tickFn: null, // ticker 回调引用（_ensureStage 内赋值，便于排查残留）
    _switching: false, // 模型加载中锁（并发切换时使用）
    _internalModel: null, // 缓存 Live2D internalModel 引用（避免每次重读）
    _srcW: 0, // 模型原始像素尺寸（被 _fit 多次调用时不会缩小）
    _srcH: 0,
    _lastMotionAt: 0, // 上次动作真实播完时间（由 motionfinish 事件驱动更新，P0-1）
    _idleTimer: null, // 待机调度 setTimeout 句柄（随机间隔自递归）
    // ── 待机/互动调度新状态（P1-3/P1-4/P2-6）──
    _lastIdleKey: null,      // 上次待机动作名（防连续重复）
    _lastUserInteractAt: 0,  // 用户最近互动时间（空闲分级依据）
    _sleepAnnounced: false,  // 是否已播过「犯困」过渡动作（5min 时）
    _busySince: 0,           // 当前忙碌动作开始时间（情绪/手势/区域互动置位）
    // ── 表情恢复（P0-2）──
    _emotionHoldTimer: null, // 情绪表情超时恢复定时器
    _lastEmotionAt: 0,       // 最近一次情绪事件时间
    // ── 说话联动（P1-5）──
    _speakingSince: 0,       // TTS 开始时间（说话中待机让位判断）
    _ttsFinishedAt: 0,       // 上次 TTS 自然播完时间（说完话收尾动作）
    // 点击互动模式轮换（0=随机动作，1=随机表情，2=两者同时），连续点击时轮换避免单调
    _clickMode: 0,
    _lastClickAt: 0,
    // ── 点击交换（区域互动）：纯前端坐标分区，见 interact_map.json ──
    _regionMap: null,      // interact_map.json 内容
    _regionCounts: {},     // 各区域当前 stage 索引 { head: 0, body: 0, lower: 0 }
    _regionLastAt: {},     // 各区域上次触发时间（冷却用）
    _motionKeys: {},       // 当前模型的动作组名集合（存在性检查缓存）
    _zoomMult: 1, // 用户快捷键缩放倍率（叠加在 _fit 基准上）
    _emotionThreshold: null, // 运行时覆盖的情绪阈值（null 则用映射表默认）
    _modelVisible: true, // 数字人显隐状态

    // ── 拖拽相关字段 ──
    _userOffsetX: 0, // 用户拖拽后的偏移（叠加在 _fit 居中基准上）
    _userOffsetY: 0,
    _baseX: 0, // 最近一次 _fit 算出的居中基准 x（拖拽时作为参考）
    _baseY: 0,
    _dragStart: null, // { px, py, offX, offY }
    _dragging: false,
    _dragBound: false, // 拖拽监听器是否已绑定（防 init 重复调用叠加）
    _currentModelId: MODELS[0].id,

    async init(opts) {
      opts = opts || {};
      this._container = document.getElementById(opts.containerId || "live2d-canvas");
      if (!this._container) {
        console.warn("[live2d] 容器缺失");
        try {
          global.dispatchEvent(new CustomEvent("live2d:init-done", {
            detail: { ok: false, error: "容器缺失: " + (opts.containerId || "live2d-canvas") }
          }));
        } catch (_) {}
        return false;
      }
      console.info("[live2d] init 开始，PIXI.live2d =", !!(global.PIXI && global.PIXI.live2d));

      // 情绪映射表（与后端 emotion_map.json 同构）
      try {
        const r = await fetch(opts.mapUrl || "./assets/live2d/emotion_map.json");
        this._mapper = await r.json();
      } catch (e) {
        console.warn("[live2d] 情绪映射表加载失败，使用内置降级", e);
      }

      // 点击交换（区域互动）配置：失败仅告警，退化为原有随机互动
      try {
        const r = await fetch("./assets/live2d/interact_map.json");
        this._regionMap = await r.json();
      } catch (e) {
        console.warn("[live2d] interact_map.json 加载失败，点击区域互动降级", e);
        this._regionMap = null;
      }

      // 运行时库缺失 → 降级（聊天仍可用，仅无数字人）
      if (typeof global.PIXI === "undefined" || !global.PIXI.live2d) {
        console.info("[live2d] 运行时库未加载，进入无数字人降级模式");
        try {
          global.dispatchEvent(new CustomEvent("live2d:init-done", {
            detail: { ok: false, error: "运行时库未加载（PIXI.live2d 不存在），请检查脚本加载顺序" }
          }));
        } catch (_) {}
        return false;
      }

      // PIXI App / ticker / resize 只建一次（见 BUG-1：避免切换模型叠加 ticker）
      this._ensureStage();
      // 绑定拖拽（绑定到容器，不依赖模型命中区）
      this._bindDrag();

      const modelUrl =
        opts.modelUrl ||
        (MODELS.find((m) => m.id === this._currentModelId) || MODELS[0]).url;

      return await this._loadModel(modelUrl);
    },

    /** 一次性创建 PIXI Application + ticker（命名函数，便于排查）+ resize 监听。 */
    _ensureStage() {
      if (this._pixiApp) return; // 已存在则直接复用（切换模型不重建）
      const dpr = Math.min(global.devicePixelRatio || 1, 1.5);
      const cw = this._container.clientWidth || 360;
      const ch = this._container.clientHeight || 480;
      this._pixiApp = new global.PIXI.Application({
        width: cw,
        height: ch,
        backgroundAlpha: 0,
        antialias: true,
        autoDensity: true,
        resolution: dpr,
        resizeTo: this._container,
      });
      this._container.appendChild(this._pixiApp.view);

      // 命名 ticker 回调，始终操作「当前」model，避免切换模型后残留旧引用
      this._tickFn = () => {
        if (this._model) this._model.update(this._pixiApp.ticker.deltaMS / 1000);
      };
      this._pixiApp.ticker.add(this._tickFn);

      this._onResize = () => this._fit();
      global.addEventListener("resize", this._onResize);
    },

    /** 加载（或重载）一个模型。销毁旧模型、清空缓存、读新表情索引、加载、fit、起待机。 */
    async _loadModel(modelUrl) {
      if (this._switching) return false; // 防止并发加载导致模型竞争/泄漏（快速连按切换时）
      this._switching = true;
      try {
        // ① 销毁旧模型（切换场景）
        if (this._model) {
          try { this._pixiApp.stage.removeChild(this._model); } catch (_) {}
          try {
            this._model.destroy({ children: true, texture: true, baseTexture: true });
          } catch (_) {}
          this._model = null;
        }
        if (this._idleTimer) { clearTimeout(this._idleTimer); this._idleTimer = null; }
        if (this._emotionHoldTimer) { clearTimeout(this._emotionHoldTimer); this._emotionHoldTimer = null; }

        // ② 清空旧模型缓存（BUG-2：守卫 if (_srcW<=0) 会让第二个模型读到旧尺寸）
        this._internalModel = null;
        this._srcW = 0;
        this._srcH = 0;
        this._exprIndex = {};
        this._currentEmotion = null;

        // ③ Cubism4 初始化（关键，必须在 from 之前；失败仅告警，不阻断）
        try {
          if (
            typeof global.PIXI.live2d.startUpCubism4 === "function" &&
            !global.PIXI.live2d.cubism4Ready
          ) {
            global.PIXI.live2d.startUpCubism4();
          }
        } catch (e) {
          console.warn("[live2d] startUpCubism4 初始化告警（不影响后续）", e);
        }

        // ④ 读 model3.json 建立 表情名→索引 映射（两套模型顺序不同，动态读取）
        try {
          const m3 = await (await fetch(modelUrl)).json();
          const exprs = (m3.FileReferences && m3.FileReferences.Expressions) || [];
          exprs.forEach((e, i) => {
            this._exprIndex[(e.Name || "").toLowerCase()] = i;
          });
          // 缓存动作组名集合（区域互动存在性检查；314702 独有的 b_feie 不配置但可被待机池过滤）
          this._motionKeys = {};
          const motions = (m3.FileReferences && m3.FileReferences.Motions) || {};
          Object.keys(motions).forEach((k) => { this._motionKeys[k] = true; });
        } catch (e) {
          console.warn("[live2d] 读取 model3.json 失败", e);
        }

        // 切换模型后重置区域互动计数/冷却（不同模型区域坐标独立）
        this._regionCounts = {};
        this._regionLastAt = {};

        // ⑤ 加载模型（autoInteract 自带鼠标跟随）
        this._model = await global.PIXI.live2d.Live2DModel.from(modelUrl, {
          autoInteract: true,
        });
        this._pixiApp.stage.addChild(this._model);
        // 模型加载完毕就打印一帧真实尺寸，便于 F12 排查 _fit
        console.info(
          "[live2d] model loaded → model.width=",
          this._model.width,
          "model.height=",
          this._model.height,
          "| internalModel.width=",
          this._model.internalModel && this._model.internalModel.width,
          "internalModel.height=",
          this._model.internalModel && this._model.internalModel.height,
          "| screen=",
          this._pixiApp.screen.width + "x" + this._pixiApp.screen.height
        );
        // 缓存模型原始尺寸与 internalModel 引用，避免被 _fit 自身的缩放影响
        this._internalModel = this._model.internalModel;
        if (this._srcW <= 0 || this._srcH <= 0) {
          this._srcW = this._internalModel && this._internalModel.width || this._model.width || 1024;
          this._srcH = this._internalModel && this._internalModel.height || this._model.height || 1024;
        }
        // 切换模型时按当前显隐状态复原
        this._model.visible = this._modelVisible;
        this._fit();

        // ⑥ 初始待机动作（从待机池按权重随机选，优先轻动作）
        try {
          if (this._model.motion) {
            const initial = this._pickWeightedIdle();
            if (initial) this._model.motion(initial, 0, 1);
          }
        } catch (e) {}
        this._lastMotionAt = Date.now();
        this._lastIdleKey = null;

        // ⑥.1 动作播完感知（P0-1）：motionfinish 时刷新让位时间戳，并尝试恢复待机。
        // 关键：Cubism 动作播完不会自动回 idle，必须在此手动恢复。
        if (this._model && !this._model._roleplayMotionBound) {
          this._model._roleplayMotionBound = true;
          this._model.on("motionfinish", () => {
            this._lastMotionAt = Date.now();
            this._busySince = 0; // 忙碌动作结束，让位恢复
            this._maybeResumeIdle();
          });
        }

        // ⑥.2 TTS 联动监听（P1-5）：说话中待机让位；说完话播收尾微动作。
        // 全局只绑定一次（不随模型重载叠加）。
        if (!this._ttsBound) {
          this._ttsBound = true;
          try {
            global.addEventListener("tts:started", () => {
              this._speakingSince = Date.now();
            });
            global.addEventListener("tts:finished", () => {
              this._speakingSince = 0;
              this._ttsFinishedAt = Date.now();
              this._playTtsTail();
            });
          } catch (_) {}
        }

        // ⑦ 待机多样性：随机间隔自递归调度（P1-4），消除固定 12s 节拍感
        this._scheduleIdle();

        // 重置空闲分级状态（切换模型视为新起点）
        this._lastUserInteractAt = Date.now();
        this._sleepAnnounced = false;

        // 记录当前模型 id（与 modelUrl 反查）
        const found = MODELS.find((m) => m.url === modelUrl);
        this._currentModelId = found ? found.id : modelUrl;

        this._ready = true;
        try {
          global.dispatchEvent(new CustomEvent("live2d:init-done", { detail: { ok: true } }));
        } catch (_) {}
        try {
          global.dispatchEvent(new CustomEvent("live2d:model-changed", {
            detail: { id: this._currentModelId, name: (found && found.name) || this._currentModelId }
          }));
        } catch (_) {}
        return true;
      } catch (e) {
        console.warn("[live2d] 初始化失败，降级为无数字人", e);
        // 加载失败时重置就绪状态与当前模型标记，否则 switchModel(旧id) 会命中
        // 282 行短路（_ready 仍是 true + _currentModelId 仍是旧 id）而不再重载，
        // 舞台永久空白且无法通过切换恢复。
        this._ready = false;
        this._currentModelId = null;
        if (this._idleTimer) { clearTimeout(this._idleTimer); this._idleTimer = null; }
        if (this._emotionHoldTimer) { clearTimeout(this._emotionHoldTimer); this._emotionHoldTimer = null; }
        try {
          global.dispatchEvent(new CustomEvent("live2d:init-done", {
            detail: { ok: false, error: (e && e.message) || String(e) }
          }));
        } catch (_) {}
        return false;
      } finally {
        this._switching = false; // 无论成功/失败都解锁，允许后续切换
      }
    },

    /** 切换模型（复用现有 PIXI App，不重建 ticker / resize 监听）。返回 Promise<boolean>。 */
    async switchModel(idOrUrl) {
      let url = idOrUrl;
      const byId = MODELS.find((m) => m.id === String(idOrUrl));
      if (byId) url = byId.url;
      if (!url) return false;
      if (this._currentModelId === (byId ? byId.id : url) && this._ready) {
        // 已是当前模型，无需重载（但保留显隐/缩放置）
        return true;
      }
      try {
        await this._loadModel(url);
        // 重载后应用持久化缩放 / 阈值（显隐已在 _loadModel 里复原）
        this._model && this.setZoom(this._zoomMult);
        return true;
      } catch (e) {
        console.warn("[live2d] 切换模型失败", e);
        return false;
      }
    },

    _fit() {
      if (!this._pixiApp || !this._model) return;
      // 画布尺寸优先用 app.screen；若未就绪（0 尺寸）则回退到容器实测尺寸
      let w = this._pixiApp.screen.width || 0;
      let h = this._pixiApp.screen.height || 0;
      if (!w || !h) {
        w = this._container.clientWidth || 360;
        h = this._container.clientHeight || 480;
      }
      // 模型原始像素尺寸：只用缓存的源尺寸（不会因 _fit 自身缩放而缩小），
      // 第一次 model 还未就绪时回退到当前 model.width 与 1024 兜底。
      let iw = this._srcW || this._model.width || 1024;
      let ih = this._srcH || this._model.height || 1024;
      if (!isFinite(iw) || !isFinite(ih) || iw <= 0 || ih <= 0) {
        iw = 1024;
        ih = 1024;
      }
      // 显示修复：留 8% 余量，确保整张模型（头/脚）完整可见；
      // 关键——垂直方向必须对称居中，原来额外下移 12% 会把模型底部推出舞台导致裁切。
      let s = Math.min(w / iw, h / ih) * 0.92;
      if (!isFinite(s) || s <= 0) s = 0.38;
      s *= this._zoomMult; // 叠加用户快捷键缩放
      this._model.scale.set(s);
      const baseX = (w - iw * s) / 2;
      const baseY = (h - ih * s) / 2;
      this._baseX = baseX;
      this._baseY = baseY;
      // 拖拽偏移叠加在居中基准上
      this._model.x = baseX + this._userOffsetX;
      this._model.y = baseY + this._userOffsetY;
      console.info(
        "[live2d] fit -> screen",
        Math.round(w) + "x" + Math.round(h),
        "| model",
        Math.round(iw) + "x" + Math.round(ih),
        "| scale",
        s.toFixed(3),
        "| offset",
        this._userOffsetX + "," + this._userOffsetY
      );
    },

    /** 重置拖拽位置到居中（F 键 / 双击 / 按钮触发）。 */
    resetPosition() {
      this._userOffsetX = 0;
      this._userOffsetY = 0;
      this._fit();
      this._announceOffset();
    },

    /** 拖拽：绑在容器上（不依赖模型命中区，更稳）。 */
    _bindDrag() {
      const el = this._container;
      if (!el) return;
      if (this._dragBound) return; // 防止 init() 重复调用导致监听器叠加
      this._dragBound = true;
      el.style.touchAction = "none";

      const onDown = (e) => {
        if (!this._model || !this._model.visible) return;
        // 仅左键 / 触摸 / 笔
        if (e.button != null && e.button !== 0) return;
        this._dragStart = {
          px: e.clientX,
          py: e.clientY,
          offX: this._userOffsetX,
          offY: this._userOffsetY,
        };
        this._dragging = false; // 超过阈值才真正开始拖
        try { el.setPointerCapture(e.pointerId); } catch (_) {}
      };

      const onMove = (e) => {
        if (!this._dragStart || !this._model) return;
        const dx = e.clientX - this._dragStart.px;
        const dy = e.clientY - this._dragStart.py;
        if (!this._dragging) {
          if (Math.hypot(dx, dy) <= 5) return; // 小于阈值：视为点击，保留头部跟随
          this._dragging = true;
          this._model.autoInteract = false; // 拖拽时停掉头部跟随
          if (this._container.parentElement) this._container.parentElement.classList.add("dragging");
        }
        this._userOffsetX = this._dragStart.offX + dx;
        this._userOffsetY = this._dragStart.offY + dy;
        this._model.x = this._baseX + this._userOffsetX;
        this._model.y = this._baseY + this._userOffsetY;
      };

      const onUp = (e) => {
        if (!this._dragStart) return;
        const wasDragging = this._dragging;
        this._dragStart = null;
        this._dragging = false;
        if (wasDragging) {
          if (this._model) this._model.autoInteract = true; // 恢复头部跟随
          if (this._container.parentElement) this._container.parentElement.classList.remove("dragging");
          this._announceOffset(); // 持久化偏移
        } else {
          // 未拖拽 → 视为点击，触发随机互动（命中区域走区域交换，未命中回退三态轮换）
          const rect = el.getBoundingClientRect();
          this._handleClick(e.clientX - rect.left, e.clientY - rect.top);
        }
        try { el.releasePointerCapture(e.pointerId); } catch (_) {}
      };

      const onDbl = () => {
        this.resetPosition(); // 内部已 _announceOffset()，无需再手动广播
      };

      el.addEventListener("pointerdown", onDown);
      el.addEventListener("pointermove", onMove);
      // pointerup / pointercancel 可能发生在容器外，挂到 window 更稳
      global.addEventListener("pointerup", onUp);
      global.addEventListener("pointercancel", onUp);
      el.addEventListener("dblclick", onDbl);
    },

    /** 拖拽结束 / 复位后，把当前偏移广播给 chat.js 做持久化。 */
    _announceOffset() {
      try {
        global.dispatchEvent(new CustomEvent("live2d:offset", {
          detail: { x: this._userOffsetX, y: this._userOffsetY }
        }));
      } catch (_) {}
    },

    onEmotionEvent(data) {
      if (!data) return;
      const score = data.score != null ? data.score : 1.0;
      const thr =
        this._emotionThreshold != null
          ? this._emotionThreshold
          : (this._mapper && this._mapper.score_threshold) || 0.3;
      if (score < thr) return;
      const map = this._mapper || {};
      // 前端父类回退（双保险）：map.emotions[emotion] → map.emotions[parent] → map.default。
      // 后端 resolve() 已做同构回退，此处幂等；未知 emotion 直接落 default。
      const EMOTION_PARENT = {
        love: "happy", grateful: "happy", excited: "happy",
        disappointed: "sad", lonely: "sad",
        embarrassed: "anxious", confused: "anxious", sleepy: "neutral",
      };
      let entry =
        (map.emotions && map.emotions[data.emotion]) ||
        (map.emotions && map.emotions[EMOTION_PARENT[data.emotion]]) ||
        map.default;
      if (!entry) return;
      if (this._currentEmotion === data.emotion) return; // 防止重复触发
      this._currentEmotion = data.emotion;
      this._lastEmotionAt = Date.now();
      if (!this._ready || !this._model) return; // 降级模式静默
      try {
        const idx = this._exprIndex[(entry.expression || "").toLowerCase()];
        if (idx != null) this._model.expression(idx);
        if (entry.motion) {
          this._model.motion(entry.motion, 0, entry.priority || 1);
          this._busySince = Date.now(); // 情绪动作视为「忙碌」，待机让位
        }
        // 表情超时自动恢复 neutral（P0-2）：10s 内无新情绪则回 e_idle
        if (this._emotionHoldTimer) clearTimeout(this._emotionHoldTimer);
        this._emotionHoldTimer = setTimeout(() => {
          this._emotionHoldTimer = null;
          if (this._currentEmotion === data.emotion) {
            this._currentEmotion = null;
            this._resetToNeutralExpression();
          }
        }, EMOTION_HOLD_MS);
      } catch (e) {
        console.warn("[live2d] 表情/动作切换失败", e);
      }
    },

    /** 播放一个具名动作组（如聊天关键词触发的手势）。返回是否成功触发。 */
    playGesture(name, priority) {
      if (!name || !this._ready || !this._model) return false;
      try {
        this._model.motion(name, 0, priority || 2);
        this._busySince = Date.now();
        this.notifyUserInteract(); // 手势也算用户互动，刷新空闲分级
        return true;
      } catch (e) {
        console.warn("[live2d] 手势播放失败", name, e);
        return false;
      }
    },

    /** 播放一个具名表情（按 expression name 查索引）。返回是否成功触发。 */
    playExpression(name) {
      if (!name || !this._ready || !this._model) return false;
      try {
        const idx = this._exprIndex[(name || "").toLowerCase()];
        if (idx == null) return false;
        this._model.expression(idx);
        return true;
      } catch (e) {
        console.warn("[live2d] 表情切换失败", name, e);
        return false;
      }
    },

    /**
     * 点击数字人时的互动：
     * ① 命中「点击交换」区域（头/身/下摆）→ 播放该区域专属动作+表情，并广播 live2d:interact
     *    供 chat.js 显示气泡 + TTS（参考汤姆猫/崩坏3 的区域分层互动）。
     * ② 未命中区域（模型外空白）→ 回退三态轮换（纯动作 / 纯表情 / 动作+表情）。
     * 防连击：800ms 内的重复点击仅更新时间戳不触发（避免快速连点刷屏动作）。
     * @param {number} cx 容器内点击 x（clientX - rect.left）
     * @param {number} cy 容器内点击 y
     */
    _handleClick(cx, cy) {
      if (!this._ready || !this._model || !this._model.visible) return;
      const now = Date.now();
      if (now - this._lastClickAt < 800) return; // 防连击
      this._lastClickAt = now;
      this.notifyUserInteract(); // 点击数字人即视为用户互动，刷新空闲分级

      // ① 点击交换：坐标 → 模型归一化坐标 → 命中区域优先
      if (this._regionMap && cx != null && cy != null && this._srcW > 0 && this._srcH > 0) {
        const rx = (cx - this._model.x) / (this._model.scale.x || 1) / this._srcW;
        const ry = (cy - this._model.y) / (this._model.scale.y || 1) / this._srcH;
        // 仅在模型包围盒内（0~1）才做区域判定，模型外点击不触发区域互动
        if (rx >= 0 && rx <= 1 && ry >= 0 && ry <= 1) {
          const region = this._resolveRegion(rx, ry);
          if (region) {
            this._playRegion(region, now);
            return;
          }
        }
      }

      // ② 未命中区域 → 回退三态轮换（点击专属权重池 P2-8）
      const avail = CLICK_POOL.filter((it) => this._motionKeys[it.name]);
      const pick = () => {
        if (!avail.length) return "b_idle";
        const it = this._pickWeighted(avail);
        return it ? it.name : "b_idle";
      };

      const mode = this._clickMode % 3;
      this._clickMode++;
      try {
        if (mode === 0) {
          // 纯动作
          const m = pick();
          this._model.motion(m, 0, 2);
          this._busySince = now;
        } else if (mode === 1) {
          // 纯表情：从已注册的表情索引中随机选一个
          const exprNames = Object.keys(this._exprIndex);
          if (exprNames.length > 0) {
            const randExpr = exprNames[Math.floor(Math.random() * exprNames.length)];
            this._model.expression(this._exprIndex[randExpr]);
          } else {
            // 无表情则回退到动作
            this._model.motion(pick(), 0, 2);
            this._busySince = now;
          }
        } else {
          // 动作 + 表情组合
          const m = pick();
          this._model.motion(m, 0, 2);
          this._busySince = now;
          const exprNames = Object.keys(this._exprIndex);
          if (exprNames.length > 0) {
            const randExpr = exprNames[Math.floor(Math.random() * exprNames.length)];
            this._model.expression(this._exprIndex[randExpr]);
          }
        }
        this.notifyUserInteract(); // 点击互动刷新空闲分级
      } catch (e) {
        console.warn("[live2d] 点击互动失败", e);
      }
    },

    /** 坐标判定：按 interact_map.json regions 数组顺序，命中即返回区域定义（先头后身）。 */
    _resolveRegion(rx, ry) {
      const map = this._regionMap;
      if (!map || !map.regions || !map.regions.length) return null;
      for (const r of map.regions) {
        const rect = r.rect;
        if (!rect || rect.length < 4) continue;
        const [x, y, w, h] = rect;
        if (rx >= x && rx <= x + w && ry >= y && ry <= y + h) return r;
      }
      return null;
    },

    /**
     * 播放区域互动：冷却检查 → stage 递进轮换 → 动作(priority 3 最高) + 表情（各自存在性检查）
     * → 广播 live2d:interact 事件（chat.js 监听后显示气泡 + TTS）。
     */
    _playRegion(region, now) {
      if (!this._ready || !this._model) return;
      const cd = region.cooldown || 2500;
      if (now - (this._regionLastAt[region.id] || 0) < cd) return; // 区域冷却
      this._regionLastAt[region.id] = now;

      const stages = region.stages || [];
      if (!stages.length) return;
      const idx = (this._regionCounts[region.id] || 0) % stages.length;
      this._regionCounts[region.id] = idx + 1;
      const s = stages[idx];
      if (!s) return;

      try {
        // 动作（存在性检查：两套模型动作集可能不同）
        if (s.motion && this._motionKeys[s.motion]) {
          this._model.motion(s.motion, 0, 3); // 最高优先级，压过情绪(2)/待机(1)
          this._busySince = now;
        }
        // 表情（存在性检查）
        if (s.expression) {
          const ei = this._exprIndex[String(s.expression).toLowerCase()];
          if (ei != null) this._model.expression(ei);
        }
        this.notifyUserInteract(); // 点击互动刷新空闲分级
      } catch (e) {
        console.warn("[live2d] 区域互动播放失败", e);
      }

      // 广播给 chat.js：气泡 + TTS（解耦，live2d.js 不直接依赖 chat.js/voice.js）
      try {
        global.dispatchEvent(new CustomEvent("live2d:interact", {
          detail: { region: region.id, text: s.text || "", tts: s.tts || "", stage: idx }
        }));
      } catch (_) {}
    },

    /** 随机间隔自递归调度（P1-4）：消除固定 12s 节拍感，间隔随空闲程度变化。 */
    _scheduleIdle() {
      if (this._idleTimer) { clearTimeout(this._idleTimer); this._idleTimer = null; }
      const now = Date.now();
      let min = IDLE_INTERVAL_MIN, max = IDLE_INTERVAL_MAX;
      // 空闲分级（P2-6）：用户 90s+ 无操作 → 低频态；5min+ → 超低频（先播一次犯困过渡）
      const idleSince = now - (this._lastUserInteractAt || now);
      if (idleSince >= IDLE_DEEP_AFTER) {
        min = IDLE_SLEEP_MIN; max = IDLE_SLEEP_MAX;
        if (!this._sleepAnnounced) {
          this._sleepAnnounced = true;
          this._playSleepGesture(); // 5min 时播一次「犯困」过渡，之后进入超低频
        }
      } else if (idleSince >= IDLE_SLEEP_AFTER) {
        min = IDLE_SLEEP_MIN; max = IDLE_SLEEP_MAX;
      }
      const delay = min + Math.random() * (max - min);
      this._idleTimer = setTimeout(() => {
        this._idleTick();
        this._scheduleIdle(); // 自递归续约
      }, delay);
    },

    /** 待机调度主逻辑：满足条件才播，否则让位（P0-1/P1-3/P1-5/P2-6）。 */
    _idleTick() {
      if (!this._ready || !this._model) return;
      const now = Date.now();
      // 让位规则（任一命中则不播待机）：
      //  ① 近期有动作（由 motionfinish 驱动，动作真实播完才算「近期」）
      //  ② 说话中（TTS 播放中不插播无关动作）
      //  ③ 当前有忙碌动作（情绪/手势/区域互动，_busySince 置位中）
      if (now - this._lastMotionAt < 9000) return;
      if (now - this._speakingSince < 1500) return; // 说话中/刚说完，让位
      if (this._busySince && now - this._busySince < 4000) return;
      const g = this._pickWeightedIdle();
      if (!g) return;
      try {
        this._model.motion(g, 0, 1); // IDLE 优先级，可被情绪(2)/互动(3)打断
      } catch (e) {
        /* 忽略待机动作异常 */
      }
    },

    /** 动作播完后尝试恢复待机（motionfinish 回调里调用；忙碌中不抢）。 */
    _maybeResumeIdle() {
      if (!this._ready || !this._model) return;
      const now = Date.now();
      if (now - this._speakingSince < 1500) return; // 刚说完话，留给收尾动作
      if (this._busySince && now - this._busySince < 4000) return; // 忙碌窗口内不抢
      const g = this._pickWeightedIdle();
      if (!g) return;
      try {
        this._model.motion(g, 0, 1);
      } catch (_) {}
    },

    /** 从待机权重池加权随机选一个动作（按当前模型动作集过滤 + 防连续重复）。 */
    _pickWeightedIdle() {
      const avail = IDLE_POOL.filter((it) => this._motionKeys[it.name]);
      if (!avail.length) return null;
      // 扇子类变体展开（P2-7）：b_shanzi 命中时随机选一个扇子变体，观感更丰富
      const expand = (it) => {
        if (it.name === "b_shanzi") {
          const fans = FAN_VARIANTS.filter((k) => this._motionKeys[k]);
          if (fans.length) return { name: fans[Math.floor(Math.random() * fans.length)], w: it.w };
        }
        return it;
      };
      const expanded = avail.map(expand);
      let pick = this._pickWeighted(expanded);
      // 防连续重复（P1-3）：重抽一次，仍相同则接受（池子太小时避免死循环）
      if (pick && pick.name === this._lastIdleKey) {
        const again = this._pickWeighted(expanded);
        if (again && again.name !== pick.name) pick = again;
      }
      this._lastIdleKey = pick ? pick.name : null;
      return pick ? pick.name : null;
    },

    /** 通用加权随机：按权重 w 抽取一个元素。 */
    _pickWeighted(items) {
      if (!items || !items.length) return null;
      const total = items.reduce((s, it) => s + (it.w || 1), 0);
      let r = Math.random() * total;
      for (const it of items) {
        r -= (it.w || 1);
        if (r <= 0) return it;
      }
      return items[items.length - 1];
    },

    /** 空闲 5min 的「犯困」过渡动作：闭眼/低姿态微动作，之后进入超低频。 */
    _playSleepGesture() {
      if (!this._ready || !this._model) return;
      // 用「点头+遮面」等低能耗动作示意犯困；t_bizui(闭口) 若有则更贴切
      const sleepy = ["b_diantou", "b_zhelian", "b_yaotou"].filter((k) => this._motionKeys[k]);
      if (!sleepy.length) return;
      try {
        this._model.motion(sleepy[Math.floor(Math.random() * sleepy.length)], 0, 2);
        this._lastMotionAt = Date.now();
      } catch (_) {}
    },

    /** TTS 自然播完的收尾微动作（P1-5）：说完话轻点头/抬手/摇扇，角色「收得住」。 */
    _playTtsTail() {
      if (!this._ready || !this._model) return;
      const now = Date.now();
      if (now - this._lastMotionAt < 2500) return; // 刚有动作则让位
      // 恢复默认表情（说完话情绪表情也回落，配合 P0-2）
      this._resetToNeutralExpression();
      const avail = TTS_TAIL_GESTURES.filter((k) => this._motionKeys[k]);
      if (!avail.length) return;
      try {
        this._model.motion(avail[Math.floor(Math.random() * avail.length)], 0, 2);
        this._lastMotionAt = now;
      } catch (_) {}
    },

    /** 用户互动通知（chat.js 发送消息 / 点击模型时调用）：退出空闲分级，刷新计时。 */
    notifyUserInteract() {
      this._lastUserInteractAt = Date.now();
      if (this._sleepAnnounced) this._sleepAnnounced = false; // 被唤醒，重置犯困标记
      this._scheduleIdle(); // 立即按高频间隔重排
    },

    /** 恢复默认表情（e_idle）。 */
    _resetToNeutralExpression() {
      if (!this._model) return;
      const idx = this._exprIndex["e_idle"];
      if (idx != null) {
        try { this._model.expression(idx); } catch (_) {}
      }
    },

    /** 运行时覆盖情绪触发阈值（前端快捷键调节「情绪灵敏度」）。null 回复用映射表默认。 */
    setEmotionThreshold(v) {
      this._emotionThreshold = v == null ? null : Number(v);
    },

    /** 用户快捷键缩放：在 _fit 基准上叠加倍率（0.5–2.0），立即重排。 */
    setZoom(mult) {
      this._zoomMult = Math.max(0.5, Math.min(2.0, Number(mult) || 1));
      this._fit();
    },

    /** 显隐数字人（前端快捷键切换）。 */
    setVisible(v) {
      this._modelVisible = !!v;
      if (this._model) this._model.visible = this._modelVisible;
    },

    /** 设置拖拽偏移（由 chat.js 从持久化状态恢复）。 */
    setOffset(x, y) {
      this._userOffsetX = Number(x) || 0;
      this._userOffsetY = Number(y) || 0;
      this._fit();
    },

    getModels() {
      return MODELS;
    },

    getCurrentModelId() {
      return this._currentModelId;
    },

    get ready() {
      return this._ready;
    },
  };

  global.RoleplayLive2D = RoleplayLive2D;
})(window);
