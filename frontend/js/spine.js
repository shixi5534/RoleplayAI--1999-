/*
 * spine.js —— Spine 小模型（人偶）渲染适配器（P0-T3）
 *
 * 基于素材包自带 spine-player.js 暴露的低层 API（spine.SpineCanvas），
 * 完全控制相机/骨架变换，实现 v0.3 呈现规范 §2.3 / 风格板 §8.2 的定位规则：
 *   - 水平居中；垂直居中偏下
 *   - 头顶留白 = 窗口高 8%（气泡区硬约束）
 *   - 脚底落地线 = 窗口下沿 −16px
 *   - 缩放 = min(可用宽/骨骼自然宽, 可用高/骨骼自然高) × 0.92 × 用户 zoom
 * 行为接口（walk/idle/emotion/click/sleep/enter/setZoom/setVisible/setFlip/destroy）
 * 收敛到 PetRenderer 约定，供 pet.js（Spine 唯一渲染器路由）调用。
 */
(function (global) {
  "use strict";

  const DEFAULTS = {
    containerId: "pet-canvas",
    skelUrl: "./assets/spine/314701_wmz_s_room.skel",
    atlasUrl: "./assets/spine/314701_wmz_s.atlas",
    animationMapUrl: "./assets/spine/animation_map.json",
    expressionMapUrl: "./assets/spine/expression_map.json",
  };

  const IDLE_MIN = 8000;   // 待机池轮换间隔
  const IDLE_MAX = 18000;
  const EMOTION_HOLD = 4000; // 情绪动画持续后回落待机
  const ENVELOPE_SAMPLES = 6; // 每个动画全周期采样点数（覆盖循环内的极端姿态）

  /**
   * P1.1：骨骼模型注册表。
   * - 314701_s：当前默认的简化版（轻量，窗口占用小）
   * - 314701：初始皮肤完整版 room
   * - 314702：无拘无束·唯一之路 room
   */
  const MODELS = Object.freeze([
    Object.freeze({
      id: "314701_s",
      name: "314701 · 简化版",
      skelUrl: "./assets/spine/314701_wmz_s_room.skel",
      atlasUrl: "./assets/spine/314701_wmz_s.atlas",
      animationMapUrl: "./assets/spine/animation_map.json",
      expressionMapUrl: "./assets/spine/expression_map.json",
    }),
    Object.freeze({
      id: "314701",
      name: "314701 · 初始皮肤",
      skelUrl: "./assets/spine/314701_wmz_room.skel",
      atlasUrl: "./assets/spine/314701_wmz.atlas",
      animationMapUrl: "./assets/spine/animation_map.json",
      expressionMapUrl: "./assets/spine/expression_map.json",
    }),
    Object.freeze({
      id: "314702",
      name: "314702 · 无拘无束·唯一之路",
      skelUrl: "./assets/spine/314702_wmz_room.skel",
      atlasUrl: "./assets/spine/314702_wmz.atlas",
      animationMapUrl: "./assets/spine/animation_map.json",
      expressionMapUrl: "./assets/spine/expression_map.json",
    }),
  ]);

  // 语义槽位兜底候选：animation_map.json 是暂定表，这里按完整版 .skel
  // 的真实动画名补齐。候选按顺序取第一个存在者，缺失继续回落 idle。
  const SLOT_ALIASES = {
    idle: ["idle_room", "idle"],
    idle_pool: ["idle_room", "idle", "idle_birthday_loop", "idle_birthday_up"],
    walk: ["walk"],
    enter: ["idle_birthday_up", "idle_room", "idle"],
    click: ["click", "interact"],
    happy: ["interact", "click"],
    sad: ["hit"],
    surprise: ["hit", "click"],
    listen: ["interact", "idle_room", "idle"],
    rest: ["idle_room", "idle"],
    sleep_in: ["sleep"],
    sleep_deep: ["sleep"],
    sleep_wake: ["idle_room", "idle"],
    egg: ["interact", "click"],
    unknown: ["idle_room", "idle"],
  };

  const EMOTION_ALIASES = {
    happy: ["interact", "click", "idle_room", "idle"],
    sad: ["hit"],
    angry: ["hit", "click"],
    anxious: ["interact", "click"],
    surprise: ["hit", "click"],
    fear: ["hit"],
    neutral: ["idle_room", "idle"],
    love: ["interact", "click"],
    grateful: ["interact", "click"],
    excited: ["click", "interact"],
    disappointed: ["hit"],
    lonely: ["idle_room", "idle"],
    embarrassed: ["hit", "click"],
    confused: ["interact", "click"],
    sleepy: ["sleep"],
  };

  // Live2D 时代手势名（chat.js GESTURES 关键词表 / LLM 输出 {动作：xxx} 指令）
  // → 语义槽位/情绪。这些名字在 Spine 模型里不存在，必须映射到槽位才能播出
  // 真实动画（playMotion 消费；未知名回落点击互动池，绝不让动作指令空转）。
  const GESTURE_SLOTS = {
    b_diantou: "click",        // 点头 → 点击互动池（完整版 click 即摇扇互动）
    b_shanzi: "click",         // 摇扇 → 同上
    b_liaofa: "click",         // 撩发 → 互动池
    b_taishou: "happy",        // 抬手招呼 → interact
    t_weixiao: "happy",        // 微笑 → interact
    t_nanguo: "sad",           // 难过 → hit
    b_yaotou: "angry",         // 摇头/不满 → hit
    b_zhelian: "embarrassed",  // 遮脸/害羞怕 → hit
    t_yihuo: "confused",       // 疑惑 → interact
  };

  const RoleplaySpine = {
    // ── 内部状态 ──
    _app: null,          // SpineCanvas 实例
    _canvas: null,
    _container: null,
    _modelId: null,      // 当前模型 id（对应 MODELS）
    _model: null,
    _skeleton: null,
    _state: null,        // AnimationState
    _animMap: { slots: {} },
    _exprMap: { emotions: {} },
    _ready: false,
    _disposed: false,
    _session: 0,        // 切换模型时递增，旧 SpineCanvas 回调凭此失效
    _zoomMult: 1,
    _visible: true,
    _flip: 1,            // 行走方向镜像：1 / -1
    _fitScale: 1,        // 由 _fit 计算
    _transformGuard: {   // 骨骼变换异常守卫：NaN/Infinity/缩放异常/位移突变 → 自动重置
      prev: new Map(),
      faultCount: 0,
      lastFaultAt: 0,
    },
    _alphaRects: null,    // 最近一次从渲染缓冲读出的非透明矩形区域（仅用于 hover 精确命中，不得用于 setShape 裁渲染）
    _alphaRectsAt: 0,
    _envReachX: 128,      // 全动画包络相对相机轴的最坏水平可达（unit 空间，含行走镜像）
    _envUp: 360,          // 落地线上方可达（unit 空间）
    _envDown: 0,          // 落地线下方可达（unit 空间）
    _setupW: 256,         // setup pose 可视宽（unit 空间；命中盒/气泡定位用）
    _setupH: 360,         // setup pose 可视高（unit 空间）
    _setupBottom: 0,      // setup pose 脚底 y（unit 空间；稳定相机锚点）
    _setupCenterX: 0,     // setup pose 水平中心（unit 空间；稳定相机锚点）
    _natW: 256,           // 兼容字段：= _setupW（getBounds/getShapeBounds 用）
    _natH: 360,
    _groundMargin: 16,   // 脚底落地线与窗口下沿的间距（CSS px）
    _slot: "idle",       // 当前行为槽位
    _busy: false,        // 情绪/点击等临时动作占用中
    _idleTimer: null,
    _emotionTimer: null,
    _resizeObserver: null,
    _w: 320,
    _h: 420,

    // ───────────────────────── 初始化 ─────────────────────────
    /** 切换模型前清空上一次运行时状态（同一单例可反复 init）。 */
    _resetRuntime() {
      if (this._idleTimer) clearTimeout(this._idleTimer);
      if (this._emotionTimer) clearTimeout(this._emotionTimer);
      this._idleTimer = null;
      this._emotionTimer = null;
      if (this._resizeObserver) { try { this._resizeObserver.disconnect(); } catch (_) {} this._resizeObserver = null; }
      if (this._app && typeof this._app.dispose === "function") { try { this._app.dispose(); } catch (_) {} }
      if (this._canvas && this._canvas.parentElement) this._canvas.parentElement.removeChild(this._canvas);
      this._app = null;
      this._canvas = null;
      this._skeleton = null;
      this._state = null;
      this._envReachX = 128;
      this._envUp = 360;
      this._envDown = 0;
      this._setupW = 256;
      this._setupH = 360;
      this._setupBottom = 0;
      this._setupCenterX = 0;
      this._ready = false;
      this._disposed = false;
      this._busy = false;
      this._slot = "idle";
      this._transformGuard.prev.clear();
      this._transformGuard.faultCount = 0;
      this._transformGuard.lastFaultAt = 0;
      this._alphaRects = null;
      this._alphaRectsAt = 0;
      this._session += 1; // 旧会话的异步回调全部失效
    },

    async init(opts) {
      opts = Object.assign({}, DEFAULTS, opts || {});
      this._resetRuntime();
      const model = this.getModelById(opts.modelId) || MODELS[0];
      this._model = model;
      this._modelId = model.id;
      opts.modelId = model.id;
      opts.skelUrl = opts.skelUrl || model.skelUrl;
      opts.atlasUrl = opts.atlasUrl || model.atlasUrl;
      opts.animationMapUrl = opts.animationMapUrl || model.animationMapUrl;
      opts.expressionMapUrl = opts.expressionMapUrl || model.expressionMapUrl;

      this._container = document.getElementById(opts.containerId || DEFAULTS.containerId);
      if (!this._container || !global.spine || !global.spine.SpineCanvas) {
        console.warn("[spine] 容器缺失或 spine 运行时未加载");
        return false;
      }
      const session = this._session; // 本次 init 的会话 id，旧会话回调一律丢弃

      // 动画/情绪映射表（缺失时用内置兜底）
      try {
        const r = await fetch(opts.animationMapUrl);
        const m = await r.json();
        this._animMap = m && m.slots ? m : { slots: {} };
      } catch (e) {
        console.warn("[spine] animation_map 加载失败，使用兜底", e);
        this._animMap = { slots: {} };
      }
      try {
        const r = await fetch(opts.expressionMapUrl);
        const m = await r.json();
        this._exprMap = m && m.emotions ? m : { emotions: {} };
      } catch (e) {
        console.warn("[spine] expression_map 加载失败，使用兜底", e);
        this._exprMap = { emotions: {} };
      }

      // 画布：铺满容器（透明），DPR 适配
      this._canvas = document.createElement("canvas");
      this._canvas.style.cssText = "position:absolute;inset:0;width:100%;height:100%;display:block;";
      this._container.appendChild(this._canvas);
      this._measure();
      this._resizeObserver = new ResizeObserver(() => this._measure());
      this._resizeObserver.observe(this._container);

      const self = this;
      try {
        this._app = new global.spine.SpineCanvas(this._canvas, {
          pathPrefix: "",
          app: {
            loadAssets: (app) => {
              // spine-player 4.2 的 loadAssets 回调参数是 SpineCanvas 实例；
              // 资源加载器位于 app.assetManager，而不是实例本身。
              app.assetManager.loadBinary(opts.skelUrl);
              app.assetManager.loadTextureAtlas(opts.atlasUrl);
            },
            initialize: (app) => {
              if (session !== self._session) return; // 已被更新的模型切换替换
              self._onInitialize(app, opts);
            },
            update: (app, delta) => {
              if (session !== self._session || app !== self._app) return;
              self._onUpdate(app, delta);
            },
            render: (app) => {
              if (session !== self._session || app !== self._app) return;
              self._onRender(app);
            },
            error: (_app, errs) => {
              if (session !== self._session) return;
              console.error("[spine] 加载失败:", errs);
              self._fail(errs, session);
            },
          },
        });
      } catch (e) {
        console.error("[spine] SpineCanvas 创建失败:", e);
        this._fail([e.message || String(e)], session);
        if (this._resizeObserver) { try { this._resizeObserver.disconnect(); } catch (_) {} this._resizeObserver = null; }
        if (this._canvas && this._canvas.parentElement) this._canvas.parentElement.removeChild(this._canvas);
        this._canvas = null;
        return false;
      }
      return true;
    },

    getModels() {
      return MODELS.map((m) => ({ id: m.id, name: m.name }));
    },
    getModelById(id) {
      return MODELS.find((m) => m.id === id) || MODELS[0];
    },
    getModel() {
      return this._model || this.getModelById(this._modelId);
    },

    /** 容器尺寸（CSS px）+ 画布缓冲尺寸（DPR）。 */
    _measure() {
      if (!this._canvas || !this._container) return;
      const w = this._container.clientWidth || 320;
      const h = this._container.clientHeight || 420;
      const dpr = Math.min(global.devicePixelRatio || 1, 2);
      this._w = w;
      this._h = h;
      if (this._canvas.width !== Math.round(w * dpr) || this._canvas.height !== Math.round(h * dpr)) {
        this._canvas.width = Math.round(w * dpr);
        this._canvas.height = Math.round(h * dpr);
      }
      if (this._ready) this._fit();
    },

    _fail(errs, session) {
      if (session !== undefined && session !== this._session) return; // 旧会话失败不广播
      try {
        global.dispatchEvent(new CustomEvent("spine:init-done", {
          detail: { ok: false, error: String(errs && errs.length ? errs[0] : "unknown") },
        }));
      } catch (_) {}
    },

    _onInitialize(app, opts) {
      const spine = global.spine;
      try {
        const atlas = app.assetManager.get(opts.atlasUrl);
        const data = app.assetManager.get(opts.skelUrl);
        const attachmentLoader = new spine.AtlasAttachmentLoader(atlas);
        const loader = new spine.SkeletonBinary(attachmentLoader);
        const skeletonData = loader.readSkeletonData(data);
        this._skeleton = new spine.Skeleton(skeletonData);
        if (skeletonData.skins && skeletonData.skins.length) {
          this._skeleton.setSkinByName(skeletonData.skins[0].name);
        }
        this._skeleton.setToSetupPose();
        this._resetConstraints(); // 初始化即重置头发等约束权重，避免物理/Transform 约束带脏状态
        const stateData = new spine.AnimationStateData(skeletonData);
        stateData.defaultMix = 0.15;
        this._state = new spine.AnimationState(stateData);
        this._measureEnvelope(); // 包络盒与相机锚点必须在 _fit 之前就绪
        this._ready = true;
        this._fit();
        // 入场动画在就绪此刻才播：init() 在 SpineCanvas 构造后即返回（此时
        // waitForAssets 还没跑、_ready 未置位），pet.js 紧随其后的 enter()
        // 必然空操作，入场动画因此从未播过。这里统一兜底，播完自动落待机。
        this.enter();
        try {
          global.dispatchEvent(new CustomEvent("spine:init-done", { detail: { ok: true } }));
        } catch (_) {}
      } catch (e) {
        console.error("[spine] 初始化异常:", e);
        this._fail([e.message]);
      }
    },

    /**
     * 重置头发/物理/Transform/IK/Path 约束到 setup pose。
     * 重点处理 Spine 4.x PhysicsConstraint：先 reset() 清物理累积，再 setToSetupPose() 恢复权重。
     */
    _resetConstraints() {
      const sk = this._skeleton;
      if (!sk) return;
      try {
        for (const c of sk.transformConstraints || []) {
          if (typeof c.setToSetupPose === "function") c.setToSetupPose();
        }
        for (const c of sk.ikConstraints || []) {
          if (typeof c.setToSetupPose === "function") c.setToSetupPose();
        }
        for (const c of sk.pathConstraints || []) {
          if (typeof c.setToSetupPose === "function") c.setToSetupPose();
        }
        for (const c of sk.physicsConstraints || []) {
          if (typeof c.reset === "function") c.reset(); // 清 xOffset/xVelocity 等物理累积
          if (typeof c.setToSetupPose === "function") c.setToSetupPose();
        }
      } catch (_) {}
    },

    _physicsReset() {
      const spine = global.spine;
      return spine && spine.Physics && spine.Physics.reset !== undefined ? spine.Physics.reset : 1;
    },

    /**
     * 测量「包络盒」与 setup pose 锚点（均在 unit 空间，与 fitScale/翻转解耦）：
     * - setup 锚点（脚底 y / 水平中心 x）：作为稳定相机常量，相机不再逐帧跟随
     *   当前动作 AABB（逐帧跟随会让模型随手摆/动作整体平移抖动，也让窗口
     *   坐标包络盒无法稳定映射，setShape 跟不上动画）；
     * - 包络盒 = 所有动画全周期采样 AABB 的并集（含 setup pose），水平对称化
     *   以覆盖行走镜像。主进程 setShape 只允许使用这个保守矩形——若使用逐帧
     *   姿态剪影（alpha 矩形），SetWindowRgn 裁剪必然滞后于动画，把动作/待机
     *   中超出旧形状的像素整块裁掉（表现为像素丢失）。
     */
    _measureEnvelope() {
      const spine = global.spine;
      const sk = this._skeleton;
      if (!spine || !sk) return;
      sk.x = 0;
      sk.y = 0;
      sk.scaleX = 1;
      sk.scaleY = 1;
      const off = new spine.Vector2();
      const size = new spine.Vector2();
      const temp = [new spine.Vector2(), new spine.Vector2()];
      try {
        sk.setToSetupPose();
        this._resetConstraints();
        sk.updateWorldTransform(this._physicsReset());
        sk.getBounds(off, size, temp);
        if (isFinite(off.x) && isFinite(size.x) && size.x > 0 && size.y > 0) {
          this._setupW = size.x;
          this._setupH = size.y;
          this._natW = size.x;
          this._natH = size.y;
          this._setupBottom = off.y;
          this._setupCenterX = off.x + size.x / 2;
        }
      } catch (_) {}
      let env = null;
      try {
        const anims = sk.data.animations || [];
        const events = [];
        const blend = spine.MixBlend ? spine.MixBlend.first : 1;
        const dir = spine.MixDirection ? spine.MixDirection.mixIn : 0;
        for (const a of anims) {
          const dur = a.duration || 0;
          for (let i = 0; i < ENVELOPE_SAMPLES; i++) {
            const t = dur * (i / Math.max(1, ENVELOPE_SAMPLES - 1));
            sk.setToSetupPose();
            this._resetConstraints();
            a.apply(sk, 0, t, events, 1, blend, dir);
            sk.updateWorldTransform(this._physicsReset());
            sk.getBounds(off, size, temp);
            if (!isFinite(off.x) || !isFinite(size.x) || size.x <= 0 || size.y <= 0) continue;
            if (!env) {
              env = { ox: off.x, oy: off.y, w: size.x, h: size.y };
            } else {
              const nx = Math.min(env.ox, off.x);
              const ny = Math.min(env.oy, off.y);
              env.w = Math.max(env.ox + env.w, off.x + size.x) - nx;
              env.h = Math.max(env.oy + env.h, off.y + size.y) - ny;
              env.ox = nx;
              env.oy = ny;
            }
          }
        }
      } catch (_) {}
      if (env) {
        // 记录 raw 包络盒与相对相机轴（setup 中心）的几何量；
        // 翻转围绕骨架原点 x=0 镜像，但相机恒以 ±setupCenterX 为轴心，
        // 因此窗口内最坏水平可达 = max(|ox−cx|, |right−cx|)，天然覆盖镜像。
        const cx = this._setupCenterX;
        this._envReachX = Math.max(Math.abs(env.ox - cx), Math.abs(env.ox + env.w - cx));
        this._envUp = Math.max(0, env.oy + env.h - this._setupBottom); // 落地线上方可达
        this._envDown = Math.max(0, this._setupBottom - env.oy);       // 落地线下方可达
      } else {
        // 采样失败：退回 setup pose 几何量（仍远优于逐帧姿态剪影）
        this._envReachX = this._setupW / 2;
        this._envUp = this._setupH;
        this._envDown = 0;
      }
      // 恢复 setup 姿态，交还后续动画状态机
      try {
        sk.setToSetupPose();
        this._resetConstraints();
      } catch (_) {}
      console.info("[spine] envelope ->", "setup", Math.round(this._setupW) + "x" + Math.round(this._setupH),
        "| reachX/up/down", Math.round(this._envReachX) + "/" + Math.round(this._envUp) + "/" + Math.round(this._envDown));
    },

    /**
     * 骨骼变换矩阵异常检测：
     * - NaN / Infinity
     * - 单轴缩放趋近 0 或 >20（飞散/塌缩）
     * - 单帧位移 >800px（明显跳变，常见于头发物理约束爆掉）
     * skipJump=true 时跳过位移检测：翻转/显隐那一帧骨骼世界坐标会合法瞬移
     * （整列骨骼对折，远离原点的骨骼位移可达数千 px），属正常变换而非异常。
     */
    _validateTransforms(skipJump) {
      const sk = this._skeleton;
      if (!sk || !sk.bones) return true;
      const MAX_SCALE = 20;
      const MIN_SCALE = 0.001;
      const MAX_JUMP = 800;
      for (const bone of sk.bones) {
        const a = bone.a, b = bone.b, c = bone.c, d = bone.d;
        const x = bone.worldX, y = bone.worldY;
        if (
          !isFinite(a) || !isFinite(b) || !isFinite(c) || !isFinite(d) ||
          !isFinite(x) || !isFinite(y)
        ) {
          return false;
        }
        const scaleX = Math.sqrt(a * a + c * c);
        const scaleY = Math.sqrt(b * b + d * d);
        // 双轴同时塌缩才判异常，避免某些骨骼单轴 0 缩放（合法隐藏/压扁）误触发
        if ((scaleX < MIN_SCALE && scaleY < MIN_SCALE) || scaleX > MAX_SCALE || scaleY > MAX_SCALE) {
          return false;
        }
        if (skipJump) continue;
        const prev = this._transformGuard.prev.get(bone);
        if (prev) {
          const dx = x - prev.x;
          const dy = y - prev.y;
          if (dx * dx + dy * dy > MAX_JUMP * MAX_JUMP) return false;
        }
      }
      this._transformGuard.prev.clear();
      for (const bone of sk.bones) {
        this._transformGuard.prev.set(bone, { x: bone.worldX, y: bone.worldY });
      }
      return true;
    },

    /** 变换异常自动恢复：重置骨骼/约束/动画，连续多次则自动重载当前模型（不依赖手动切换）。 */
    _recoverFromTransformFault() {
      if (!this._ready || !this._skeleton) return;
      const now = Date.now();
      const g = this._transformGuard;
      if (now - g.lastFaultAt > 60000) g.faultCount = 0;
      g.faultCount += 1;
      g.lastFaultAt = now;
      console.warn("[spine] 骨骼变换异常，自动恢复 #" + g.faultCount);

      try { this._state && this._state.clearTracks(); } catch (_) {}
      try { this._skeleton.setToSetupPose(); } catch (_) {}
      this._resetConstraints();
      try {
        const physics = (global.spine && global.spine.Physics && global.spine.Physics.update !== undefined)
          ? global.spine.Physics.update
          : 2;
        this._skeleton.updateWorldTransform(physics);
      } catch (_) {}
      this._transformGuard.prev.clear();

      if (g.faultCount >= 5) {
        g.faultCount = 0;
        this._reloadCurrentModel();
        return;
      }
      this.idle(); // 重置后回到待机池
    },

    /** 连续异常时自动销毁并重新初始化当前模型，避免用户手动切模型。 */
    _reloadCurrentModel() {
      const model = this._model || this.getModelById(this._modelId) || MODELS[0];
      console.warn("[spine] 连续异常，自动重新初始化当前模型:", model.id);
      const opts = {
        containerId: this._container ? this._container.id : "pet-canvas",
        modelId: model.id,
        skelUrl: model.skelUrl,
        atlasUrl: model.atlasUrl,
        animationMapUrl: model.animationMapUrl,
        expressionMapUrl: model.expressionMapUrl,
      };
      // 延迟到当前 update 回调栈外再重载，避免在 SpineCanvas 更新中销毁自身
      setTimeout(() => {
        this.init(opts).then((ok) => {
          if (ok) console.info("[spine] 自动重载完成:", model.id);
        });
      }, 0);
    },

    _onUpdate(app, delta) {
      if (!this._ready || this._disposed) return;
      const raw = Number(delta);
      if (!isFinite(raw) || raw <= 0) return;
      // P0 修复（完整版模型面部/头发「撕裂/冻结」）：spine 4.2 的物理约束
      // 步长取自 skeleton.time - lastTime（见运行时 PhysicsConstraint.update），
      // 而 skeleton.time 只由 skeleton.update(delta) 推进。此前从未调用它，
      // skeleton.time 恒为 0 → 物理步长恒 0 → 头发/面部物理骨骼全部冻结在
      // setup 姿态，而头部/帽子骨骼正常动画 → 两者错位叠加成「乱发糊脸」。
      // 简化版模型没有物理约束故幸免，完整版必现。补上骨架时钟推进后物理
      // 才真正开始模拟（与 Spine 官方 4.2 用法一致）。
      // delta 钳到 ≤50ms：窗口遮挡/休眠恢复时 SpineCanvas 会给数秒级 delta，
      // 钳制防止物理一步积分爆炸（数值源见运行时；对宠物无感知）。
      const dt = Math.min(raw, 1 / 20);
      this._skeleton.update(dt);
      this._state.update(dt);
      this._state.apply(this._skeleton);
      // 位置/镜像每帧重写（防动画内部改动 root 或外部逻辑覆盖）
      const scaleX = this._flip * this._fitScale * (this._visible ? 1 : 0.0001);
      const scaleY = this._fitScale * (this._visible ? 1 : 0.0001);
      this._skeleton.x = 0;
      this._skeleton.y = 0; // 世界原点放画布中心；脚底对齐由 _onRender 动态相机完成
      // 翻转/缩放/显隐会让物理骨骼的世界坐标瞬移（镜像 = 整列骨骼对折），
      // 物理惯性会把头发甩成一团—— scale 变化的那一帧改用 Physics.reset，
      // 让物理以新变换为基准重新起步（Spine 官方对「传送/翻转」的标准做法）。
      const scaleChanged =
        this._lastScaleX !== undefined &&
        (Math.abs(scaleX - this._lastScaleX) > 0.01 ||
          Math.abs(scaleY - this._lastScaleY) > 0.01);
      this._lastScaleX = scaleX;
      this._lastScaleY = scaleY;
      this._skeleton.scaleX = scaleX;
      this._skeleton.scaleY = scaleY;
      // spine-player 4.2 的 Skeleton.updateWorldTransform 必须传 Physics 枚举
      //（none=0/reset=1/update=2/pose=3）；不传会抛 "physics is undefined" 并中断渲染循环。
      const physics = (global.spine && global.spine.Physics && global.spine.Physics.update !== undefined)
        ? (scaleChanged ? global.spine.Physics.reset : global.spine.Physics.update)
        : (scaleChanged ? 1 : 2);
      this._skeleton.updateWorldTransform(physics);
      // 变换异常守卫：检测到 NaN/飞散/位移突变时自动重置/重载，不让坏帧继续
      // 渲染。翻转/显隐那一帧骨骼世界坐标合法对折瞬移，跳过位移检测。
      if (!this._validateTransforms(!!scaleChanged)) {
        this._recoverFromTransformFault();
        return;
      }
    },

    _onRender(app) {
      if (!this._ready || this._disposed) return;
      const gl = app.gl;
      gl.viewport(0, 0, app.htmlCanvas.width, app.htmlCanvas.height);
      gl.clearColor(0, 0, 0, 0);
      gl.clear(gl.COLOR_BUFFER_BIT);
      const cam = app.renderer.camera;
      cam.viewportWidth = this._w;
      cam.viewportHeight = this._h;
      cam.zoom = 1;

      // 稳定相机：锚定 setup pose（脚底 = 窗口下沿 groundMargin，水平中心 =
      // setup 中心），不逐帧跟随当前动作 AABB。旧实现每帧按 AABB 重新取景，
      // 待机物理/动作动画改变 AABB 时整个模型会在窗口里平移抖动，且模型
      // 任何超出当前取景的部位都被画布边缘裁掉；包络盒缩放（_fit）已保证
      // 所有姿态都在窗口内，固定相机即可完整呈现。
      const s = this._fitScale || 1;
      cam.position.x = this._flip * this._setupCenterX * s;
      cam.position.y = this._setupBottom * s + this._h / 2 - this._groundMargin;
      try { cam.clearColor = new global.spine.Color(0, 0, 0, 0); } catch (_) {}
      app.renderer.begin();
      app.renderer.drawSkeleton(this._skeleton, true);
      app.renderer.end();
    },

    // ───────────────────────── 定位（§2.3 / 风格板 §8.2） ─────────────────────────
    _fit() {
      if (!this._ready || !this._skeleton) return;
      // 缩放基准 = 全动画包络（unit 空间，init 时一次性实测），且按相机锚点
      // 折算窗口内最坏可达：水平 reachX 相对相机轴（含行走镜像），垂直拆成
      // 落地线上方 up / 下方 down。任何动作/待机姿态都不超出画布，配合稳定
      // 相机彻底消除边缘裁剪与逐帧抖动。不能用 live skeleton.getBoundsRect
      // 实测——它读的是上一帧 world 变换（含旧 fitScale），zoom/resize 时会
      // 造成双重缩放。
      const topZone = this._h * 0.08;          // 头顶留白 8%（气泡区硬约束）
      const ground = 16;                        // 落地线 −16px
      const sideMargin = 12;                    // 左右边距各 ≥12px
      const halfW = Math.max(1, this._w / 2 - sideMargin);
      const availH = Math.max(1, this._h - topZone - ground);
      const up = Math.max(1, this._envUp);
      let s = halfW / Math.max(1, this._envReachX);
      s = Math.min(s, availH / up);
      if (this._envDown > 0) s = Math.min(s, ground / this._envDown);
      s *= 0.92;
      if (!isFinite(s) || s <= 0) s = 0.5;
      // natW/natH 保持为 setup pose 可视尺寸（命中盒/气泡定位按站立姿态算），
      // 包络盒只决定缩放，不进命中盒。
      this._natW = this._setupW;
      this._natH = this._setupH;
      this._fitScale = s * this._zoomMult;
      console.info("[spine] fit ->", Math.round(this._w) + "x" + Math.round(this._h),
        "| setup", Math.round(this._setupW) + "x" + Math.round(this._setupH),
        "| reachX/up/down", Math.round(this._envReachX) + "/" + Math.round(this._envUp) + "/" + Math.round(this._envDown),
        "| scale", this._fitScale.toFixed(3));
    },

    // ───────────────────────── 行为接口 ─────────────────────────
    /** 播放某语义槽位（取该槽位动画列表第一个存在的）。 */
    _slotCandidates(slot) {
      const fromMap = (this._animMap.slots && this._animMap.slots[slot]) || [];
      const aliases = SLOT_ALIASES[slot] || [];
      return [...new Set([...fromMap, ...aliases])];
    },

    _playSlot(slot, opts) {
      opts = opts || {};
      if (!this._ready || !this._state) return null;
      const avail = this._validAnimations(slot);
      let name = opts.name || (avail.length ? avail[0] : null);
      if (!name) {
        if (slot === "idle_pool") {
          // animation_map 是暂定表，可能存在全部候选名都不在 .skel 里的情况。
          // 兜底顺序：idle 槽位 → .skel 内第一个动画。绝不让待机槽空转。
          const idleAvail = this._validAnimations("idle");
          const all = this._skeleton.data.animations || [];
          name = idleAvail[0] || (all.length ? all[0].name : null);
        } else {
          // 槽位无动画 → 回落待机池
          return this._playSlot("idle_pool", opts);
        }
      }
      if (!name) return null;
      this._slot = slot;
      const entry = this._state.setAnimation(0, name, opts.loop !== false);
      if (entry && opts.onComplete) entry.listener = { complete: () => opts.onComplete() };
      return entry;
    },

    _validAnimations(slot) {
      if (!this._skeleton) return [];
      return this._slotCandidates(slot).filter((n) => this._skeleton.data.findAnimation(n));
    },

    walk(direction) {
      // 行走：target* 循环 + 方向镜像；方向变化时立即翻转
      if (direction === "left") this._flip = -1;
      else if (direction === "right") this._flip = 1;
      return this._playSlot("walk", { loop: true });
    },
    stopWalk() {
      if (this._slot === "walk") this.idle();
    },
    idle() {
      this._busy = false;
      this._playSlot("idle_pool", { loop: true });
      this._scheduleIdle();
    },
    _currentAnimationName() {
      const track = this._state && this._state.tracks && this._state.tracks[0];
      return track && track.animation ? track.animation.name : null;
    },
    _scheduleIdle() {
      if (this._idleTimer) clearTimeout(this._idleTimer);
      const delay = IDLE_MIN + Math.random() * (IDLE_MAX - IDLE_MIN);
      this._idleTimer = setTimeout(() => {
        if (!this._ready || this._busy || this._slot === "walk") { this._scheduleIdle(); return; }
        const avail = this._validAnimations("idle_pool");
        if (avail.length <= 1) {
          // 只有一个有效待机动画：保持循环播放，不打断重播。
          this._scheduleIdle();
          return;
        }
        // 轮换待机池：随机挑一条与当前不同的，特殊待机（idle_birthday_*）
        // 才真正轮得到；旧实现恒播 avail[0]，池子其余条目永远不可达。
        const cur = this._currentAnimationName();
        const pool = cur ? avail.filter((n) => n !== cur) : avail;
        const pick = (pool.length ? pool : avail)[Math.floor(Math.random() * (pool.length || avail.length))];
        this._playSlot("idle_pool", { loop: false, name: pick, onComplete: () => this._scheduleIdle() });
      }, delay);
    },
    emotion(tag) {
      // 情绪：expression_map 候选 → 内置 EMOTION_ALIASES → idle 回落，播完回待机。
      const map = this._exprMap.emotions && this._exprMap.emotions[tag];
      const cands = [...((map && map.animations) || []), ...(EMOTION_ALIASES[tag] || [])];
      const fallback = (map && map.fallback) || "idle_pool";
      this._busy = true;
      if (this._idleTimer) clearTimeout(this._idleTimer);
      let played = null;
      for (const n of cands) {
        if (this._skeleton && this._skeleton.data.findAnimation(n)) {
          // 注意：_playSlot 内部已 setAnimation（返回 entry）。此前这里又
          // setAnimation 重启同一动画并覆盖 entry——白白发一次时间轴、
          // 还丢掉槽位记账。保留首个 entry 挂完成回调即可。
          played = this._playSlot(fallback === "idle_pool" ? "idle_pool" : fallback, { name: n, loop: false });
          if (played) {
            played.listener = { complete: () => { this._busy = false; this.idle(); } };
          }
          break;
        }
      }
      if (!played) {
        const entry = this._playSlot(fallback, { loop: false });
        if (entry) entry.listener = { complete: () => { this._busy = false; this.idle(); } };
        else { this._busy = false; this.idle(); }
      }
      if (this._emotionTimer) clearTimeout(this._emotionTimer);
      this._emotionTimer = setTimeout(() => {
        if (this._busy) { this._busy = false; this.idle(); }
      }, EMOTION_HOLD + 2000);
      return played;
    },
    click(name) {
      // P3：左键随机触发 click 槽位中的一个预设动作（map + 内置别名候选池）。
      const avail = this._validAnimations("click");
      const pick = name || (avail.length ? avail[Math.floor(Math.random() * avail.length)] : null);
      this._busy = true;
      const entry = this._playSlot("click", { loop: false, name: pick || undefined });
      if (entry) {
        entry.listener = { complete: () => { this._busy = false; this.idle(); } };
      } else {
        this._busy = false;
      }
    },
    /**
     * 播放一个语义动作名（pet.js 手势 / LLM {动作：xxx} / 外部调用统一入口），
     * 兼容四类输入，绝不空转：
     *   1) Live2D 手势名（b_diantou/t_weixiao…）→ GESTURE_SLOTS 映射到槽位/情绪；
     *   2) 语义槽位名（happy/listen/egg/…，animation_map.slots 或内置别名）
     *      → 直接播该槽位，播完回待机；
     *   3) 情绪名（expression_map / EMOTION_ALIASES 命中）→ 走 emotion 通道；
     *   4) 真实动画名 → 原样播放；未知名 → 回落点击互动池。
     */
    playMotion(name) {
      const key = String(name || "").trim();
      if (!key || key === "click") return this.click();
      const slot = GESTURE_SLOTS[key];
      if (slot === "click") return this.click();
      if (slot) return this.emotion(slot);
      if (key === "walk") return this.walk();
      if (this._validAnimations(key).length) {
        this._busy = true;
        const entry = this._playSlot(key, { loop: false });
        if (entry) entry.listener = { complete: () => { this._busy = false; this.idle(); } };
        else this._busy = false;
        return entry;
      }
      if ((this._exprMap.emotions && this._exprMap.emotions[key]) || EMOTION_ALIASES[key]) {
        return this.emotion(key);
      }
      if (this._skeleton && this._skeleton.data.findAnimation(key)) {
        this._busy = true;
        const entry = this._state.setAnimation(0, key, false);
        this._slot = key;
        if (entry) entry.listener = { complete: () => { this._busy = false; this.idle(); } };
        return entry;
      }
      return this.click();
    },
    sleep(level) {
      // level: 1=浅睡 2=深睡 0=唤醒
      this._busy = true;
      if (this._idleTimer) clearTimeout(this._idleTimer);
      if (level === 0) {
        const entry = this._playSlot("sleep_wake", { loop: false });
        if (entry) entry.listener = { complete: () => { this._busy = false; this.idle(); } };
        else { this._busy = false; this.idle(); }
      } else {
        this._playSlot(level === 2 ? "sleep_deep" : "sleep_in", { loop: true });
      }
    },
    enter() {
      const entry = this._playSlot("enter", { loop: false });
      if (entry) entry.listener = { complete: () => this.idle() };
      else this.idle();
    },

    // ───────────────────────── 状态控制 ─────────────────────────
    setZoom(mult) {
      this._zoomMult = Math.max(0.5, Math.min(2.0, Number(mult) || 1));
      this._fit();
    },
    setVisible(v) {
      this._visible = !!v;
    },
    setFlip(dir) {
      this._flip = dir === "left" ? -1 : 1;
    },
    /**
     * 人偶命中包围盒（DOM 坐标）。
     * P2：按 _fit 实测自然宽高 × fitScale（含用户 zoom）校正，并在身形四周加缓冲，
     * 避免 zoom≠1 时 getBounds 估算偏移导致点击热区跑偏。
     */
    getBounds() {
      if (!this._container) return null;
      const r = this._container.getBoundingClientRect();
      if (r.width <= 0 || r.height <= 0) return null;
      const bw = (this._natW || 256) * (this._fitScale || 1);
      const bh = (this._natH || 360) * (this._fitScale || 1);
      const padX = 14;
      const padY = 16;
      const cw = Math.min(r.width, Math.max(bw + padX * 2, r.width * 0.5));
      const ch = Math.min(r.height, Math.max(bh + padY * 2, r.height * 0.55));
      // 模型底部锚定在容器下沿 −16px 落地线，命中盒随 fitScale/zoom 同步伸缩。
      return {
        left: r.left + (r.width - cw) / 2,
        top: r.top + r.height - 16 - bh - padY,
        width: cw,
        height: ch,
      };
    },
    /**
     * 窗口裁剪/点击穿透用的“紧包围盒”：只含模型实际渲染尺寸（无点击缓冲），
     * 供主进程 setShape 使用，避免透明区域继续阻挡桌面。
     */
    getShapeBounds() {
      if (!this._container) return null;
      const r = this._container.getBoundingClientRect();
      if (r.width <= 0 || r.height <= 0) return null;
      const bw = (this._natW || 256) * (this._fitScale || 1);
      const bh = (this._natH || 360) * (this._fitScale || 1);
      if (bw <= 0 || bh <= 0) return null;
      const ground = 16;
      return {
        left: r.left + (r.width - bw) / 2,
        top: r.top + r.height - ground - bh,
        width: bw,
        height: bh,
      };
    },
    /**
     * 全动画包络盒（窗口 CSS 坐标）：以稳定相机的两条锚线（水平轴 = setup
     * 中心，垂直线 = setup 脚底）为基准，覆盖模型在所有动画/待机/行走镜像
     * 下可能到达的范围。主进程 setShape 只允许使用该矩形（+ 可见 UI 矩形）；
     * 逐帧姿态剪影（alpha 矩形）永远滞后于动画，用它裁窗口会把动作/待机中
     * 超出旧形状的像素整块裁掉（像素丢失），所以 alpha 矩形只允许用于
     * hover 精确命中判定。
     */
    getEnvelopeBounds() {
      if (!this._container) return null;
      const r = this._container.getBoundingClientRect();
      if (r.width <= 0 || r.height <= 0) return null;
      const s = this._fitScale || 1;
      const ground = 16;
      // 稳定相机下两条锚线是常量：setup 中心恒在窗口水平中心，setup 脚底
      // 恒在窗口下沿 −ground，与当前姿态/朝向无关。
      const axisX = r.left + r.width / 2;
      const groundY = r.top + r.height - ground;
      const reach = s * this._envReachX;
      return {
        left: axisX - reach,
        top: groundY - s * this._envUp,
        width: reach * 2,
        height: s * (this._envUp + this._envDown),
      };
    },
    /**
     * 读取 WebGL 渲染缓冲中的 alpha 通道，生成“非透明像素矩形列表”。
     * 主进程 setShape 使用这些矩形而不是整个 bbox，可以让 bbox 内的透明孔洞也穿透点击。
     * 使用 4px 块 + 横向合并，兼顾精度与矩形数量。
     */
    getAlphaRects() {
      const now = Date.now();
      if (this._alphaRects && now - this._alphaRectsAt < 500) return this._alphaRects;
      if (!this._app || !this._app.gl || !this._canvas || !this._container) return null;
      try {
        this._onRender(this._app); // 确保 backbuffer 有一帧最新渲染结果
        const gl = this._app.gl;
        const w = gl.drawingBufferWidth;
        const h = gl.drawingBufferHeight;
        if (!w || !h) return null;

        const pixels = new Uint8Array(w * h * 4);
        gl.readPixels(0, 0, w, h, gl.RGBA, gl.UNSIGNED_BYTE, pixels);

        const cssW = this._w || this._container.clientWidth || w;
        const cssH = this._h || this._container.clientHeight || h;
        const step = 4;
        const cols = Math.ceil(cssW / step);
        const rows = Math.ceil(cssH / step);
        const rects = [];

        for (let row = 0; row < rows; row++) {
          let runStart = -1;
          for (let col = 0; col < cols; col++) {
            const cx = Math.min(cssW - 1, col * step + step / 2);
            const cy = Math.min(cssH - 1, row * step + step / 2);
            const px = Math.min(w - 1, Math.max(0, Math.round(cx * w / cssW)));
            const py = Math.min(h - 1, Math.max(0, Math.round(cy * h / cssH)));
            const bufY = h - 1 - py; // WebGL readPixels 原点在左下，转成 DOM 左上坐标
            const idx = (bufY * w + px) * 4;
            const alpha = pixels[idx + 3];
            if (alpha > 10) {
              if (runStart < 0) runStart = col;
            } else if (runStart >= 0) {
              rects.push({
                left: runStart * step,
                top: row * step,
                width: (col - runStart) * step,
                height: step,
              });
              runStart = -1;
            }
          }
          if (runStart >= 0) {
            rects.push({
              left: runStart * step,
              top: row * step,
              width: (cols - runStart) * step,
              height: step,
            });
          }
        }

        this._alphaRects = rects;
        this._alphaRectsAt = now;
        return rects;
      } catch (_) {
        return null;
      }
    },
    destroy() {
      this._disposed = true;
      if (this._idleTimer) clearTimeout(this._idleTimer);
      if (this._emotionTimer) clearTimeout(this._emotionTimer);
      if (this._resizeObserver) { try { this._resizeObserver.disconnect(); } catch (_) {} }
      if (this._app && typeof this._app.dispose === "function") { try { this._app.dispose(); } catch (_) {} }
      if (this._canvas && this._canvas.parentElement) this._canvas.parentElement.removeChild(this._canvas);
      this._app = null;
      this._canvas = null;
      this._skeleton = null;
      this._state = null;
      this._transformGuard.prev.clear();
      this._transformGuard.faultCount = 0;
      this._transformGuard.lastFaultAt = 0;
      this._alphaRects = null;
      this._alphaRectsAt = 0;
      this._ready = false;
    },

    /** 立即重渲染一帧到 backbuffer。画布未开 preserveDrawingBuffer，合成后
     *  缓冲即被清空；截图/像素读取前必须先调用本方法（getAlphaRects 内部同）。 */
    renderNow() {
      if (this._app && this._ready) {
        try { this._onRender(this._app); } catch (_) {}
      }
    },

    get ready() { return this._ready; },

    /** 物理约束复位：清掉挂起的速度/偏移，头发/面部回到跟随姿态。
     *  页面从后台回到前台时由文件尾部的 visibilitychange 监听调用，
     *  与 _onUpdate 的 delta 钳制互为双保险，防止爆炸姿态驻留不自愈。 */
    resetPhysics() {
      if (!this._ready || !this._skeleton) return;
      this._resetConstraints();
      try {
        const physics = (global.spine && global.spine.Physics && global.spine.Physics.update !== undefined)
          ? global.spine.Physics.update
          : 2;
        this._skeleton.updateWorldTransform(physics);
      } catch (_) {}
    },
  };

  global.RoleplaySpine = RoleplaySpine;

  // 单例级一次性注册：页面重新可见时复位物理约束（handler 永远引用单例，
  // 模型切换/重载不需要重复注册）。
  if (global.document && typeof global.document.addEventListener === "function") {
    global.document.addEventListener("visibilitychange", () => {
      if (global.document.visibilityState === "visible") RoleplaySpine.resetPhysics();
    });
  }
})(window);
