# 05 · 3D / Blender 路线（**只记不做**）

> **用户原话**（`m00001`）：「我认为后面会用到3d建模如bulander（我还没装）。反正先分析」
> **用户原话**（`m00001` RAG 日志自定义答案）：「先不跑，你记下，后面还有，3d'建模测试，你记下后面不要动了」
>
> ⇒ **本文档的定位是路标：把可行路径、代价、决策门槛钉死，让将来真要做时不用重新调研。**
> ⇒ **本轮及后续所有阶段 P0~P7 都不包含任何 3D 工作**。不要因为它存在就提前动手。

---

## 1. 现状：零 3D 依赖（实测）

| 事实 | 证据 |
|---|---|
| `frontend/assets/lib/` 只有 **4 个 UMD** | `live2dcubismcore.min.js` 207,163 / `pixi.min.js` 460,342 / `pixi-live2d-display-cubism4.min.js` 119,923 / `spine-player.js` 612,944 |
| 全仓 grep `three\|babylon\|gltf\|glb\|model-viewer` | **零命中** |
| `assets/` 下无 3D 目录 | `lib` / `live2d` / `r1999` / `spine` / `voice` 五个 |
| `spine-player.js` 在主站**不加载** | 只在 `frontend/pet.html:172` 与 `frontend/pet-inspect.html:62` |
| 主站渲染栈 | **Canvas 2D**（`canvas-fx.js`）+ **PIXI/WebGL**（`live2d.js:213`）+ Spine（桌宠页） |

---

## 2. 四条路径（按推荐度排）

### (b) ⭐ **Blender 渲序列帧 / 视频，当装饰层** —— 推荐

| 项 | 值 |
|---|---|
| 新增依赖 | **0** |
| CSP 改动 | **0**（`media-src 'self' blob:` 已允许，`src/roleplay/middleware.py:27`） |
| 首屏代价 | 6s / 512×512 webm ≈ **200~500 KB**，且可 `preload="none"` 延迟到首屏后 |
| 插槽 | `frontend/index.html:12-16` 已有 4 个 `aria-hidden="true"` 全屏 div（`.kv-backdrop`/`.kv-veil`/`.film-grain`/`.rain`，z `-2/-1`）⇒ **加第 5 个 `.fx-cinema` 即可，零 JS 改动** |
| 适合做什么 | 开屏的"角色剪影/光斑"背景、装饰层的"金线流动"、转场 |
| 不适合做什么 | 角色本体（角色是 Live2D 实时口型/表情驱动，视频做不到） |

### (c) ⭐ **Blender 只出设计稿，实现仍 Canvas 2D** —— 推荐

| 项 | 值 |
|---|---|
| 新增依赖 | **0**，首屏代价 **0** |
| 现成先例 | **现有白炽灯 + 飞蛾就是这么来的**（`canvas-fx.js:1847` 行纯手写 2D） |
| 适合做什么 | 定光位/构图/配色，然后手写成 2D 绘制代码 |
| 优点 | 不增加任何运行时负担；与"帧预算 11.6ms"的约束天然兼容 |

### (a) glTF/GLB + three.js —— 暂不推荐

| 项 | 值 |
|---|---|
| 体积 | three core ≈ **600 KB** min + loader **200~400 KB** |
| 首屏 | DCL **+600 KB ≈ +120ms**（`_research` 实测口径） |
| **CSP** | **唯一要动 CSP 的路径**：wasm 解码需 `wasm-unsafe-eval`（当前 `script-src 'self' 'unsafe-eval'`） |
| **架构冲突** | **与 PIXI 抢同一个 WebGL 上下文**。`docs/canvas-layer-design.md:235` 明确记着「画布复用同一 PIXI Application 的 container，**不新建 canvas**（同页双 WebGL 上下文风险）」 |
| **视觉冲突** | `frontend/css/index.css:394-396` 的 `#live2d-canvas canvas { filter: drop-shadow(...) }` 是**整站受光唯一来源**，经 4 轮 A/B 定档；换渲染器必破 |

### (d) Cubism 3D —— **死路**

Cubism 的 `ParamAngleX` **只是网格形变参数**，不是真的 3D 骨骼/相机。它在 3D 意义上没有任何东西可复用。

---

## 3. 为什么现在不该引入 3D（三条硬理由）

1. **首屏已经压到极限**：JS + CSS 合计 **1,206,097 B ≈ 1,177.8 KB**（LIB 769.0 / APP 346.0 / CSS 62.9 KB）+ **7.5 MB 模型**。
2. **swiftshader 下 WebGL 冷启已到 8.6s**（`live2d:init-done` 实测 8629ms @1080p）。再塞一个 WebGL 上下文只会更差。
3. **角色是 Live2D，不是 3D**。3D 只能做**环境**，而环境用 (b)/(c) 零依赖就能做到。

---

## 4. 决策门槛（什么时候可以谈 3D）

> **门槛：Live2D 冷启从 ~7s 降到 2s 以内。**

在此之前做 3D，等于在已经超载的首屏上再压一层。降冷启的可行方向（都不在本文档范围内）：
- `.moc3` 体积（314704 的 `314704.moc3` = **7,550,080 B**）
- 贴图体积（`314704_wmz_00.webp` 2,137,422 + `_01.webp` 2,085,872）
- 是否要先加载完整模型再显示（而不是渐进/占位）

---

## 5. 明确不该做的三件事

| ❌ 不要 | 为什么 |
|---|---|
| 为"可能用 3D"建空目录 `frontend/features/3d/` | 会被后人误认为**已实现**，比没有更糟 |
| 提前改 CSP 加 `wasm-unsafe-eval` | 削弱安全边界去换一个还没决定要不要做的能力 |
| 把 `#live2d-canvas` 改通用名（如 `#stage-canvas`） | 全仓 **9 处**引用（`chat.js:520`、`index.css:309,332`、`index.html:71` 等），改名零收益 |

---

## 6. 唯一该留的两个口子（都已存在，不用新建）

| 口子 | 位置 | 说明 |
|---|---|---|
| **装饰层插槽** | `frontend/index.html:13-16` | 4 个 `aria-hidden` 全屏 div，未来加第 5 个 `.fx-cinema` 即可，**零 JS 改动** |
| **`_contentBox` 契约** | `frontend/js/live2d.js:443-518 _measureContent()`，返回 `{x, y, w, h, measured}` | **角色真实占位的唯一权威**。换任何渲染器，只要能给出这个盒子，`_fit` / 拖拽 / 吸附 / 动作包络全可复用 |

---

## 7. 如果将来真要做 3D 角色

顺序建议：**先 (c) 出设计稿 → 再 (b) 渲视频验证构图 → 最后才评估 (a) 实时 3D**。

前置条件：
1. Live2D 冷启 ≤ 2s
2. 首屏 JS+CSS 总量 ≤ 800 KB
3. 想清楚**为什么 Live2D 不够**（表情/口型/物理 Live2D 都有，3D 的真实增量是什么）

---

## 8. 验收（本文档的验收就是"没有动作"）

| # | 判据 |
|---|---|
| 1 | P0~P7 任何阶段都**没有**新增 `three`/`babylon`/`gltf` 依赖 |
| 2 | `frontend/assets/lib/` 仍只有那 4 个 UMD |
| 3 | `src/roleplay/middleware.py:23-31` 的 CSP **没有** `wasm-unsafe-eval` |
| 4 | `#live2d-canvas` 这个 id 仍在 |
| 5 | 若做了什么 3D 相关的事，**必须先回来改本文档**，不能偷偷加 |
