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
  // 动作集差异（314704 无 b_shanzi*/b_zhelian/t_mianju，另有 b_huashu 等）由运行期
  // _motionKeys 过滤 + CLICK_POOL/IDLE_POOL 存在性检查兜底，不需要按模型分支。
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
    {
      id: "314704",
      name: "无名·沉影探戈",
      url: "./assets/live2d/wmz/314704/314704.model3.json",
    },
  ];

  // 待机/扇子池按模型过滤：314704 没有扇子动作，命中即回落（见 _pickWeightedIdle）。

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
    // 314704（沉影探戈）独有动作：为第三套皮肤增加待机变化。
    // 其余模型没有这些动作组，_pickWeightedIdle 的存在性过滤会自动剔除，无副作用。
    { name: "b_fuxiong", w: 12 },  // 抚胸（轻）
    { name: "b_gongsheng", w: 8 }, // 共生（中）
    { name: "b_huashu", w: 8 },    // 花束（中）
    { name: "b_huazhang", w: 4 },  // 花掌（重）
  ];
  // 扇子类动作变体（P2-7：模型自带 6 个扇子变体，触发扇子时随机选一个）
  const FAN_VARIANTS = ["b_shanzi", "b_shanzi1", "b_shanzi2", "b_shanzi3", "b_shanzi2_1", "b_shanzi2_2"];
  // 点击互动池：仅点击专属动作（与待机池语义分离，P2-8）
  // b_zhelian（遮脸）仅 314701/314702 有，314701 缺失时该条目被过滤，池子仍非空。
  const CLICK_POOL = [
    { name: "b_taishou", w: 30 }, // 抬手（点击专属感强）
    { name: "b_yaotou", w: 25 },  // 摇头
    { name: "b_zhelian", w: 20 }, // 遮脸（互动专属）
    { name: "b_diantou", w: 15 }, // 点头
    { name: "b_liaofa", w: 10 },  // 撩发
    { name: "b_huashu", w: 10 },  // 花束（314704 专属，其余模型过滤）
  ];
  // 待机调度：随机间隔范围（ms）——消除固定 12s 节拍感（P1-4）
  const IDLE_INTERVAL_MIN = 8000;
  const IDLE_INTERVAL_MAX = 18000;
  const CLICK_THROTTLE_MS = 350;   // 点击防连击节流（调研建议 leading-edge 150~300ms，取 350ms 兼顾防误触）
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
    // 真实内容边界（由 drawable 顶点并集算出，见 _measureContent）。
    // 关键：Live2D 的 getLocalBounds() / internalModel 尺寸给的是【布局框】，
    // 角色实际绘制内容常常只占其中一部分、甚至溢出到框外（实测 314704 内容
    // y 在 -0.44..0.50、x 在 0.11..1.04）。旧代码把布局框当角色本体，导致：
    //   · 缩放偏小、角色被摆到画布上方并截掉头顶；
    //   · 点击换算用 _srcW/_srcH 归一化，而 interact_map 的矩形是按内容定义的，
    //     两者基准不一致 -> 点身体却命中"空白/下摆"（用户反馈的"定位有问题"）。
    // 因此统一改用内容盒作为缩放、居中与点击换算的唯一基准。
    _contentBox: null, // { x, y, w, h } 局部坐标
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
    _posLocked: false,     // 位置锁定：开启后拖拽禁用、双击不重置（防连点误触复位）
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
    // ── 空闲分级省电（宠物页驱动 sleep(0|1|2)）──
    _sleepLevel: 0,       // 0=醒 1=浅睡 2=深睡（深睡降帧 + 停待机动作）
    _lastSleepFps: 0,     // 上次生效的 ticker.maxFPS（防重复设置）

    async init(opts) {
      opts = opts || {};
      this._container = document.getElementById(opts.containerId || "live2d-canvas");
      // 桌面宠物模式（fixedModel）：拖拽不再移动模型本身，而是广播 live2d:drag 增量事件，
      // 由外层（pet.js → Electron 窗口）跟随移动。网页版不传此选项，行为完全不变。
      this._fixedModel = !!opts.fixedModel;
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

      // 容器尺寸变化（分栏拖拽 / 栅格重排 / 面板展开收起）时同步重算模型缩放与居中。
      // 此前只监听 window.resize：任何不触发窗口缩放的布局变化都不会重算，
      // 模型会错位、溢出或留白。参照 js/spine.js 已有的 ResizeObserver 写法。
      // 纯增量：原 window 监听保留，这里只是多一个触发时机。
      if (typeof global.ResizeObserver === "function") {
        this._fitPending = false;
        this._onContainerResize = () => {
          if (this._fitPending) return;   // rAF 节流：拖拽时每帧最多重算一次
          this._fitPending = true;
          global.requestAnimationFrame(() => {
            this._fitPending = false;
            // 先让 PIXI 重新读取容器尺寸并调整 renderer，
            // 否则 _fit 仍用旧的 app.screen 尺寸，等于没重算
            if (this._pixiApp && typeof this._pixiApp.resize === "function") {
              try { this._pixiApp.resize(); } catch (_) { /* 该 PIXI 版本无此方法则跳过 */ }
            }
            this._fit();
          });
        };
        this._resizeObserver = new global.ResizeObserver(this._onContainerResize);
        this._resizeObserver.observe(this._container);
      }
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
        this._contentBox = null;
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
        // ④.5 量出【真实内容边界】：Live2D 的布局框只是画布规格，不等于角色本体。
        // 实测三套模型的角色内容在布局框里的占比差异很大（x 0.08~1.04 / y -0.44~0.51），
        // 拿布局框做缩放与点击换算会让角色摆偏、点击区域与身体对不上。
        this._measureContent();
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
        this._injectLockButton(); // 位置锁定按钮（舞台右上角，模型就绪后注入）
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
    /**
     * 量出模型【真实内容边界】（局部坐标），写入 this._contentBox。
     *
     * 为什么不能直接用 getLocalBounds()：它返回的是模型【布局框】（= internalModel
     * 尺寸），那是 Cubism 的画布规格，不是角色本体。实测三套模型角色都只占布局框的
     * 一部分、甚至溢出框外（314701 内容 y -0.33..0.51，314704 内容 y -0.44..0.50）。
     * 用布局框做缩放/居中会让角色摆偏并截顶；做点击归一化会让 interact_map 的矩形
     * 与身体对不上（用户反馈的"定位有问题"）。
     *
     * 做法：并集全部 drawable 的顶点包围盒（getDrawableVertices 已是含
     * pixelsPerUnit 与原点换算的模型局部坐标），并剔除不可见 drawable。
     *
     * 关键（踩过坑）：只量【静止姿态】是不够的 —— 实测 314704 播放动作时轮廓宽度
     * 在 222~421 CSS px 之间摆动（抬手/扇子会把手臂伸出去），按静止姿态算出的
     * 边界余量会被伸出去的手臂吃掉，出现"偶发贴边被切"。所以这里额外把模型的
     * 动作采样一遍，取【所有姿态的并集】作为内容盒。
     *
     * 取不到时回退布局框，保证调用方永远拿到可用值。
     */
    _measureContent() {
      const fallback = () => ({
        x: 0, y: 0, w: this._srcW || 1024, h: this._srcH || 1024, measured: false,
      });
      const im = this._internalModel;
      if (!im || typeof im.getDrawableVertices !== "function") {
        this._contentBox = fallback();
        return this._contentBox;
      }

      let minX = Infinity;
      let minY = Infinity;
      let maxX = -Infinity;
      let maxY = -Infinity;
      let count = 0;

      // 累积当前姿态下所有 drawable 的顶点范围
      const sweep = () => {
        try {
          const n = im.coreModel.getDrawableCount();
          for (let i = 0; i < n; i++) {
            // 完全透明的 drawable 不计入（模型常有隐藏备用件）
            let opa = 1;
            try { opa = im.coreModel.getDrawableOpacity(i); } catch (_) { /* 无该 API 则视为可见 */ }
            if (opa != null && opa < 0.5) continue;
            let v;
            try { v = im.getDrawableVertices(i); } catch (_) { continue; }
            if (!v || !v.length) continue;
            for (let j = 0; j < v.length; j += 2) {
              const x = v[j];
              const y = v[j + 1];
              if (!isFinite(x) || !isFinite(y)) continue;
              if (x < minX) minX = x;
              if (x > maxX) maxX = x;
              if (y < minY) minY = y;
              if (y > maxY) maxY = y;
            }
            count++;
          }
        } catch (e) {
          console.warn("[live2d] 内容边界量测失败", e);
        }
      };

      // ① 静止姿态
      sweep();
      const rest = { minX, minY, maxX, maxY };

      // ② 动作姿态不再单独采样：
      //    实测走 motionManager.createMotion() 与 model.motion() 两条路都拿不到姿态
      //    （settings.motions 里只有 File；手动 update 与库的 save/loadParameters
      //    时序打架，量出来与静止姿态一模一样），继续做只会留下脆弱且无用的代码。
      //    改为在 _clampOffset / 缩放上限里统一预留【动作余量】——
      //    实测动作过程中轮廓宽度可在静止值上下浮动约 6%（314704: 222~421px），
      //    预留 8% 即可确定性地覆盖，不依赖任何采样是否成功。

      // 复位到静止姿态，避免把采样姿态留在模型上
      try { im.coreModel.loadParameters(); im.coreModel.update(); } catch (_) {}

      if (!isFinite(minX) || !isFinite(minY) || !isFinite(maxX) || !isFinite(maxY)
          || maxX <= minX || maxY <= minY || !count) {
        this._contentBox = fallback();
        return this._contentBox;
      }
      this._contentBox = {
        x: minX, y: minY, w: maxX - minX, h: maxY - minY, measured: true,
      };
      console.info(
        "[live2d] content box", Math.round(minX) + "," + Math.round(minY),
        Math.round(maxX - minX) + "x" + Math.round(maxY - minY),
        "(rest", Math.round(rest.maxX - rest.minX) + "x" + Math.round(rest.maxY - rest.minY) + ")",
        "| layout", (this._srcW || 0) + "x" + (this._srcH || 0),
        "| drawables", count
      );
      return this._contentBox;
    },

    /**
     * 拖拽偏移【不做任何限制】（按用户要求放开左右与上下边界）。
     *
     * 历史：这里曾把偏移夹在「角色仍完整可见」的范围内（先按画布 8%，后改 8px），
     * 但用户明确要求取消这个限制 —— 希望能把角色拖到任意位置，包括拖出画面。
     * 因此现在只做数值归一化（保证是有限数），不再夹紧。
     *
     * 仍然保留的方法壳：调用方（_fit / 拖拽 / _fitPet）依赖它写回 _userOffsetX/Y，
     * 保证拖拽事件与持久化状态拿到的是同一个值。若将来要恢复限制，在这里加即可。
     *
     * @returns {{x:number,y:number}} 原样返回的偏移
     */
    _clampOffset(s, box, w, h) {
      let ox = Number(this._userOffsetX) || 0;
      let oy = Number(this._userOffsetY) || 0;
      if (!isFinite(ox)) ox = 0;
      if (!isFinite(oy)) oy = 0;
      this._userOffsetX = ox;
      this._userOffsetY = oy;
      return { x: ox, y: oy };
    },

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
      // 桌面宠物模式：专用适配（顶部预留气泡区、底部贴地、内容整体可见）。
      // 原因：网页版逻辑用「画布尺寸」算缩放、用「内容边界」算位置，两者量纲不一致时
      // 模型 y 变负、头顶出窗（审查报告 P0-1）。宠物模式统一按内容边界适配。
      if (this._fixedModel) {
        this._fitPet(w, h);
        return;
      }
      // 缩放与居中都以【真实内容盒】为准（见 _measureContent）。
      // 旧实现用布局框（_srcW/_srcH + getLocalBounds）当角色本体，导致缩放偏小、
      // 且角色被摆到画布上方并截掉头顶 —— 实测内容只占布局框的一部分。
      const box = this._contentBox
        || { x: 0, y: 0, w: this._srcW || 1024, h: this._srcH || 1024 };
      let iw = box.w;
      let ih = box.h;
      if (!isFinite(iw) || !isFinite(ih) || iw <= 0 || ih <= 0) {
        iw = 1024;
        ih = 1024;
      }
      // 基准缩放：留 8% 余量，确保整张模型（头/脚）完整可见
      const fitScale = Math.min(w / iw, h / ih) * 0.92;
      let s = fitScale;
      if (!isFinite(s) || s <= 0) s = 0.38;
      // 缩放：尊重用户的倍率（setZoom 已把范围夹在 0.5~2.0），不再额外封顶。
      //
      // 这里踩过一次坑（重要，勿回退）：
      //   我曾用「放大后角色必须完整放进画布」反推上限：
      //     zoomCap = ZOOM_FIT_MARGIN / max(iw*s/w, ih*s/h)
      //   但默认适配下 need 恰好 ≈ 0.92，算出来 zoomCap = 1.0 ——
      //   结果是【缩放被彻底锁死在 100%】，请求 1.5/2/3/5 倍全部只给 1.0，
      //   用户根本没法把模型放大（用户反馈："模型大小，你干嘛给我锁了？"）。
      //   "放大"本来就允许角色超出画框（那正是放大的意义），
      //   真正该防的是【跑出画面找不着】，由下面的 _clampOffset 负责。
      const zoom = this._zoomMult;
      this._zoomApplied = zoom; // 实际生效倍率（供 HUD/诊断读取）
      s *= zoom;
      this._model.scale.set(s);
      // 按内容盒居中：把内容盒中心对到画布中心
      const baseX = w / 2 - (box.x + iw / 2) * s;
      let baseY = h / 2 - (box.y + ih / 2) * s;
      // 放大到「角色比画布高」时，不再按整体居中 —— 那会把头顶和脚同时切掉，
      // 而用户放大通常是想看清脸。改为锚定【内容顶部】（头部所在处），
      // 让头部始终在画面里；想看下半身再用 Shift+↓ / 拖拽往下挪。
      // （放大到角色比画布宽时，水平仍居中 —— 人物是纵向的，水平方向居中即可。）
      const topMargin = 12; // 头顶与画布顶部的安全距离
      if (ih * s > h) {
        baseY = topMargin - box.y * s;
      }
      this._baseX = baseX;
      this._baseY = baseY;
      // 拖拽偏移：限制在「角色不会完全跑出画面」的范围内（超出即夹住）。
      // 放大后角色会超出画布，此时余量为负、偏移被夹到 0 —— 即保持居中，
      // 保证放大后仍能看到角色主体（而不是滑到画外）。
      const off = this._clampOffset(s, box, w, h);
      this._model.x = baseX + off.x;
      this._model.y = baseY + off.y;
      console.info(
        "[live2d] fit -> screen",
        Math.round(w) + "x" + Math.round(h),
        "| contentBox",
        Math.round(iw) + "x" + Math.round(ih) + "@(" + Math.round(box.x) + "," + Math.round(box.y) + ")",
        "| layout",
        (this._srcW || 0) + "x" + (this._srcH || 0),
        "| scale",
        s.toFixed(3),
        "| offset",
        this._userOffsetX + "," + this._userOffsetY
      );
    },

    /**
     * 桌面宠物模式专用适配：
     * - 缩放与位置统一使用【真实内容盒】（见 _measureContent），量纲一致，杜绝头顶出窗；
     *   旧实现用 getLocalBounds()（布局框），宠物页同样会截顶 + 缩放偏小。
     * - 顶部预留气泡区（避免气泡压头）、底部贴地（宠物站姿观感）；
     * - 水平居中，叠加用户缩放与拖拽偏移。
     */
    _fitPet(w, h) {
      const box = this._contentBox || {
        x: 0, y: 0, w: this._srcW || 1024, h: this._srcH || 1024,
      };
      let bw = box.w;
      let bh = box.h;
      let bx = box.x;
      let by = box.y;
      if (!isFinite(bw) || !isFinite(bh) || bw <= 0 || bh <= 0) { bw = 1024; bh = 1024; }
      if (!isFinite(bx)) bx = 0;
      if (!isFinite(by)) by = 0;

      const topZone = Math.min(110, h * 0.2);   // 顶部气泡区
      const bottomMargin = 12;                   // 底部贴地留白
      const availW = w * 0.94;
      const availH = h - topZone - bottomMargin;
      let s = Math.min(availW / bw, availH / bh);
      if (!isFinite(s) || s <= 0) s = 0.3;
      // 与网页版一致：不再封顶缩放（那会把缩放锁死在 100%，见 _fit 里的踩坑记录）。
      // 放大后角色超出可用区域是正常语义，由 _clampOffset 保证不跑出画面。
      const zoom = this._zoomMult;
      this._zoomApplied = zoom;
      s *= zoom;

      this._model.scale.set(s);
      // 水平按内容居中；垂直让内容底边贴地（bottomMargin）
      const baseX = w / 2 - (bx + bw / 2) * s;
      const baseY = h - bottomMargin - (by + bh) * s;
      this._baseX = baseX;
      this._baseY = baseY;
      const off = this._clampOffset(s, { x: bx, y: by, w: bw, h: bh }, w, h);
      this._model.x = baseX + off.x;
      this._model.y = baseY + off.y;
      console.info(
        "[live2d] pet-fit -> screen",
        Math.round(w) + "x" + Math.round(h),
        "| contentBox",
        Math.round(bw) + "x" + Math.round(bh) + "@(" + Math.round(bx) + "," + Math.round(by) + ")",
        "| scale",
        s.toFixed(3)
      );
    },

    /** 重置拖拽位置到居中（F 键 / 双击 / 按钮触发）。 */
    resetPosition() {
      this._userOffsetX = 0;
      this._userOffsetY = 0;
      this._fit();
      this._announceOffset();
    },

    /**
     * 按方向键微调数字人位置（键盘可达：不依赖鼠标拖拽）。
     *
     * 偏移量与拖拽共用同一套状态（_userOffsetX/Y）与边界夹紧（_clampOffset），
     * 所以键盘微调同样受"角色不得移出画布"约束，且与拖拽/持久化完全一致。
     *
     * @param {number} dx 水平位移（px，正=右）
     * @param {number} dy 垂直位移（px，正=下）
     * @returns {{x:number,y:number}} 夹紧后的实际偏移
     */
    nudge(dx, dy) {
      if (!this._model) return { x: this._userOffsetX, y: this._userOffsetY };
      this._userOffsetX = (Number(this._userOffsetX) || 0) + (Number(dx) || 0);
      this._userOffsetY = (Number(this._userOffsetY) || 0) + (Number(dy) || 0);
      // 复用 _fit 的边界逻辑：它会夹紧并把结果写回 _userOffsetX/Y
      this._fit();
      this._announceOffset();
      return { x: this._userOffsetX, y: this._userOffsetY };
    },

    /**
     * 位置锁定：开启后拖拽禁用、双击不重置——连续点击角色不再误触复位。
     * 状态持久化到 localStorage（rp_live2d_poslock），广播 live2d:poslock 事件。
     */
    togglePosLocked() {
      this._posLocked = !this._posLocked;
      try {
        global.localStorage.setItem("rp_live2d_poslock", this._posLocked ? "1" : "0");
      } catch (_) {}
      this._applyLockVisual();
      try {
        global.dispatchEvent(new CustomEvent("live2d:poslock",
          { detail: { locked: this._posLocked } }));
      } catch (_) {}
      return this._posLocked;
    },

    /** 注入位置锁定按钮（聊天页舞台右上角，与语言徽章并排）。 */
    _injectLockButton() {
      const stage = global.document.querySelector(".stage");
      if (!stage || global.document.getElementById("live2d-lock-btn")) return;
      try {
        this._posLocked = global.localStorage.getItem("rp_live2d_poslock") === "1";
      } catch (_) { this._posLocked = false; }
      const btn = global.document.createElement("div");
      btn.id = "live2d-lock-btn";
      btn.setAttribute("role", "button");
      btn.title = "锁定 / 解锁立绘位置（锁定后拖拽与双击复位失效）";
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        e.preventDefault();
        this.togglePosLocked();
      });
      btn.addEventListener("dblclick", (e) => e.stopPropagation()); // 防按钮双击冒泡触发复位
      stage.appendChild(btn);
      this._lockBtn = btn;
      this._applyLockVisual();
    },

    _applyLockVisual() {
      const btn = this._lockBtn;
      if (!btn) return;
      btn.textContent = this._posLocked ? "🔒 已固定" : "📍 固定位置";
      btn.classList.toggle("locked", this._posLocked);
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
        this._dragLast = { x: e.clientX, y: e.clientY }; // fixedModel 模式的增量采样
        this._dragging = false; // 超过阈值才真正开始拖
        try { el.setPointerCapture(e.pointerId); } catch (_) {}
      };

      const onMove = (e) => {
        if (!this._dragStart || !this._model) return;
        if (this._posLocked) return; // 位置锁定：拖拽失效（点击互动不受影响）
        const dx = e.clientX - this._dragStart.px;
        const dy = e.clientY - this._dragStart.py;
        if (!this._dragging) {
          if (Math.hypot(dx, dy) <= 5) return; // 小于阈值：视为点击，保留头部跟随
          this._dragging = true;
          this._model.autoInteract = false; // 拖拽时停掉头部跟随
          if (this._container.parentElement) this._container.parentElement.classList.add("dragging");
        }
        if (this._fixedModel) {
          // 桌面宠物模式：广播增量位移，让窗口跟随指针（模型保持原位）
          const incX = e.clientX - this._dragLast.x;
          const incY = e.clientY - this._dragLast.y;
          this._dragLast = { x: e.clientX, y: e.clientY };
          this._userOffsetX = this._dragStart.offX + dx;
          this._userOffsetY = this._dragStart.offY + dy;
          try {
            global.dispatchEvent(new CustomEvent("live2d:drag", {
              detail: { dx: incX, dy: incY, dragging: true },
            }));
          } catch (_) {}
          return;
        }
        this._userOffsetX = this._dragStart.offX + dx;
        this._userOffsetY = this._dragStart.offY + dy;
        // 偏移不再夹紧（用户要求放开限制），_clampOffset 现在只做归一化并写回状态
        const off = this._clampOffset(
          this._model.scale.x || 1,
          this._contentBox || { x: 0, y: 0, w: this._srcW || 1024, h: this._srcH || 1024 },
          this._pixiApp.screen.width, this._pixiApp.screen.height
        );
        this._model.x = this._baseX + off.x;
        this._model.y = this._baseY + off.y;
      };

      const onUp = (e) => {
        if (!this._dragStart) return;
        const wasDragging = this._dragging;
        this._dragStart = null;
        this._dragging = false;
        if (wasDragging) {
          if (this._model) this._model.autoInteract = true; // 恢复头部跟随
          if (this._container.parentElement) this._container.parentElement.classList.remove("dragging");
          if (this._fixedModel) {
            // 桌面宠物模式：广播拖拽结束（含累计偏移，供窗口动量物理使用）
            try {
              global.dispatchEvent(new CustomEvent("live2d:dragend", {
                detail: { x: this._userOffsetX, y: this._userOffsetY },
              }));
            } catch (_) {}
            // 固定模式下不把“窗口移动”写回模型偏移，模型保持居中
            this._userOffsetX = 0;
            this._userOffsetY = 0;
            return;
          }
          this._announceOffset(); // 持久化偏移
        } else {
          // 未拖拽 → 视为点击，触发随机互动（命中区域走区域交换，未命中回退三态轮换）
          const rect = el.getBoundingClientRect();
          this._handleClick(e.clientX - rect.left, e.clientY - rect.top);
        }
        try { el.releasePointerCapture(e.pointerId); } catch (_) {}
      };

      const onDbl = () => {
        if (this._posLocked) return; // 位置锁定：双击不再重置位置
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
     * 防连击：CLICK_THROTTLE_MS 内的重复点击仅更新时间戳不触发（避免快速连点刷屏动作）。
     * @param {number} cx 容器内点击 x（clientX - rect.left）
     * @param {number} cy 容器内点击 y
     */
    _handleClick(cx, cy) {
      if (!this._ready || !this._model || !this._model.visible) return;
      const now = Date.now();
      if (now - this._lastClickAt < CLICK_THROTTLE_MS) return; // 防连击（350ms，原 800ms 偏保守）
      this._lastClickAt = now;
      this.notifyUserInteract(); // 点击数字人即视为用户互动，刷新空闲分级

      // 点击即尝试角色原声（pet-voice 内部 25s 冷却自动去重、失败静默）。
      // 必须在这里发而依赖 live2d:interact：区域冷却（3~3.5s）期间 _playRegion
      // 会静默 return，把语音一起吞掉——实测 3 次点击只有 1 次出声。
      if (window.RoleplayPetCore) window.RoleplayPetCore.emitIntent("click", {});

      // ① 点击交换：坐标 → 模型归一化坐标 → 命中区域优先。
      // 归一化基准必须是【真实内容盒】（与 _fit 同源、与 interact_map 的矩形同义）。
      // 旧实现除以 _srcW/_srcH（布局框），而 interact_map 的矩形是按角色本体比例定的，
      // 两个基准不一致 -> 点身体会命中"空白"或错区的下摆（用户反馈的"定位有问题"）。
      const box = this._contentBox;
      if (this._regionMap && cx != null && cy != null && box && box.w > 0 && box.h > 0) {
        const s = this._model.scale.x || 1;
        const rx = (cx - this._model.x) / s / box.w - box.x / box.w;
        const ry = (cy - this._model.y) / s / box.h - box.y / box.h;
        // 仅在角色内容范围内（0~1）才做区域判定，角色外点击不触发区域互动
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
        // 动作（存在性检查：三套模型动作集不同，314704 无扇子/遮脸组）
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
      // 双语（P3-1）：stage 同时给出 zh（text/tts）与 en（text_en/tts_en）两套，
      // 由监听方按当前配音语言（RoleplayPetVoice.getLang()）择一，避免英配模式下
      // 弹出中文、或英文位为空导致副标题缺行。缺英文时回落到中文（宁可双语同文，
      // 也不要出现空行）。
      try {
        global.dispatchEvent(new CustomEvent("live2d:interact", {
          detail: {
            region: region.id,
            stage: idx,
            text: s.text || "",
            tts: s.tts || "",
            text_en: s.text_en || s.text || "",
            tts_en: s.tts_en || s.tts || "",
          }
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
      if (this._sleepLevel === 2) return; // 深睡：停待机动作池（配合 sleep() 降帧）
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
      // t_biyan（闭眼）最贴切，但只有 314704 有；其余模型回落到点头/遮面/摇头，
      // 由 _motionKeys 过滤（314704 无 b_zhelian 会自动剔除）。
      const sleepy = ["t_biyan", "b_diantou", "b_zhelian", "b_yaotou"]
        .filter((k) => this._motionKeys[k]);
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
      if (this._sleepLevel > 0) this.sleep(0); // 互动即唤醒：恢复帧率（sleep(0) 内部会再调本函数，注意重入）
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

    /** 设置拖拽偏移（由 chat.js 从持久化状态恢复）。
     *  实际生效值由 _fit 内的 _clampOffset 夹紧 —— 历史遗留的过大偏移
     *  （旧版本没有边界限制）不会再把角色顶出画布外。 */
    setOffset(x, y) {
      this._userOffsetX = Number(x) || 0;
      this._userOffsetY = Number(y) || 0;
      this._fit();
    },

    /** 实际生效的缩放倍率（被"不得超出画布"上限夹过之后的值）。 */
    getAppliedZoom() {
      return this._zoomApplied != null ? this._zoomApplied : this._zoomMult;
    },

    getModels() {
      return MODELS;
    },

    getCurrentModelId() {
      return this._currentModelId;
    },

    /**
     * 销毁渲染器（宠物页渲染器切换时调用）：
     * 停 ticker、解绑 resize/拖拽、销毁 PIXI App 并移除画布。
     * 此前切换渲染器不销毁会留下孤儿 WebGL 上下文 + 60fps ticker 空转（泄漏）。
     */
    destroy() {
      if (this._idleTimer) { clearTimeout(this._idleTimer); this._idleTimer = null; }
      if (this._emotionHoldTimer) { clearTimeout(this._emotionHoldTimer); this._emotionHoldTimer = null; }
      if (this._pixiApp) {
        try { this._pixiApp.ticker.stop(); } catch (_) {}
        try { this._pixiApp.ticker.remove(this._tickFn); } catch (_) {}
        try {
          // 第二个参数为移除监听选项；destroy(true) 同时移除画布 DOM
          this._pixiApp.destroy(true, { children: true, texture: true, baseTexture: true });
        } catch (_) {}
        this._pixiApp = null;
      }
      if (this._onResize) {
        try { global.removeEventListener("resize", this._onResize); } catch (_) {}
        this._onResize = null;
      }
      this._dragBound = false; // init 时重新绑定拖拽
      this._model = null;
      this._internalModel = null;
      this._tickFn = null;
      this._ready = false;
      this._sleepLevel = 0;
      this._lastSleepFps = 0;
    },

    /**
     * 模型内容包围盒（DOM 坐标，供宠物页点击穿透命中测试）。
     * 模型未就绪返回 null（调用方回落近似矩形）。
     */
    getBounds() {
      if (!this._model || !this._pixiApp || !this._container) return null;
      try {
        const b = this._model.getBounds();
        if (!b || !isFinite(b.width) || b.width <= 0 || !isFinite(b.height) || b.height <= 0) return null;
        const r = this._container.getBoundingClientRect();
        return { left: r.left + b.x, top: r.top + b.y, width: b.width, height: b.height };
      } catch (_) {
        return null;
      }
    },

    /**
     * 空闲分级（宠物页驱动）：0=唤醒 1=浅睡 2=深睡。
     * 降帧省电：浅睡 30fps / 深睡 12fps；深睡另停待机动作池，唤醒恢复 60fps。
     */
    sleep(level) {
      this._sleepLevel = level === 2 ? 2 : level === 1 ? 1 : 0;
      const t = this._pixiApp && this._pixiApp.ticker;
      if (t) {
        const fps = this._sleepLevel === 0 ? 0 : this._sleepLevel === 1 ? 30 : 12; // 0=不限制
        if (fps !== this._lastSleepFps) {
          this._lastSleepFps = fps;
          try { t.maxFPS = fps; } catch (_) {}
        }
      }
      if (this._sleepLevel === 2 && this._ready) this._playSleepGesture();
      if (this._sleepLevel === 0) this.notifyUserInteract(); // 唤醒：重置犯困标记并重排待机
    },

    get ready() {
      return this._ready;
    },
  };

  global.RoleplayLive2D = RoleplayLive2D;
})(window);
