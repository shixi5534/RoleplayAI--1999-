# 前端重构计划（v1）

> 状态：**待你拍板**（第 9 节有 7 个需要你定的点，其余按本文执行）
> 基线快照：commit `1c5966f` + tag `frontend-v3-baseline`（分支 `plotrag/M0`）
> 起草依据：2026-10-19 对 `frontend/` 全量实测（行数、标签数、变量表、全局清单均来自脚本统计，不是估算）

---

## 0. 一句话

当前前端是「**16 个 `<script>` 平铺 + 全局对象互相摸 + 两份互不认识的 CSS 变量表**」的结构，功能没问题，但每加一个特性都在给这三笔债付利息。这次重构只做三件事：**把模块边界长出来、把样式变量收敛成一份、把视觉验收变成可自动跑的**。视觉风格由你定，不动。

---

## 1. 现状体检（全部实测）

### 1.1 规模

| 类别 | 文件数 | 行数 | 体积 |
|---|---:|---:|---:|
| HTML（6 个页面） | 6 | 3,034 | 163.1 KB |
| JS（`js/` 15 + `shared/` 1） | 16 | 10,055 | 475.9 KB |
| CSS（4 个） | 4 | 2,525 | 96.1 KB |
| **源码合计** | **26** | **15,614** | **735.1 KB** |
| `frontend/assets/`（模型/纹理/音频/第三方库） | 284 | — | 44.2 MB |

### 1.2 加载方式（`frontend/index.html`，共 19 个标签）

```
icon ×1
css  ×2   index.css?v=7   pet-subtitle.css?v=5
lib  ×3   live2dcubismcore.min.js?v=7  pixi.min.js?v=7  pixi-live2d-display-cubism4.min.js?v=7
app ×13   rain / canvas-fx?v=6 / live2d?v=12 / voice?v=7 / llm-switch?v=3 /
          live2d-bootstrap?v=8 / pet-core?v=1 / pet-voice?v=6 / pet-subtitle?v=5 /
          chat?v=11 / knowledge?v=1 / desktop-pet?v=4 / layout?v=1
```

- **没有构建系统**：仓库根没有 `package.json`、没有 `node_modules`；`node v24.14.1` / `npm 11.11.0` 在本机可用但前端一次都没用过。
- **缓存靠手改版本号**：`?v=N` 是人工维护的。现已发现不一致：`chat.js?v=11`（index.html）vs `chat.js?v=9`（pet.html）；`pet.css?v=1`。
- **`pet.html` 另起一套 11 个标签**，共用 `chat.js` / `voice.js` / `pet-core.js` / `pet-subtitle.js`，靠 `PET_MODE` 常量在运行时分支（`chat.js:21`）。

### 1.3 模块化程度

| 指标 | 实测 |
|---|---|
| 有 `import` / `export` 的文件 | **0 / 16** |
| 全部是 IIFE + 全局变量 | 是（`live2d.js` 是 `(function(global){…})(window)`，其余 `(function(){…})()`） |
| 挂在 window 上的对外 API | 12 个：`RoleplayChat` `RoleplayLive2D` `RoleplayLLM` `RoleplayVoice` `RoleplayPetVoice` `RoleplayPet` `RoleplaySpine` `RoleplayPetCore` `RoleplayLayout` `KnowledgePanel` `__canvasFx` `__lastMouse` |
| 跨文件调用一律走 `window.X` | 是（无法静态分析、无类型、加载顺序即依赖顺序） |

**耦合最重的两个**：`pet.js` 摸 6 个全局，`chat.js` 摸 4 个。

### 1.4 重复

`chat.js`（1,282 行）与 `pet.js`（1,699 行）是**同一件事的两次实现**：

| 重复点 | 现状 |
|---|---|
| `detectGesture` | 两处同名不同实现（一处查对象、一处查 `Map`） |
| `loadState` / `saveState` | 两处同名不同键（`roleplay_ui_state` vs `roleplay_pet_state`），chat.js 版还有数值类型校正 |
| SSE 流解析 | 两套（chat.js 自己写 `TextDecoder` 逐块解析） |
| `/chat/stream` 调用 | 两处 |

### 1.5 样式系统

| 文件 | 行数 | 体积 | `:root` 块 | 自定义变量 |
|---|---:|---:|---:|---:|
| `css/index.css` | 1,443 | 55.6 KB | 4 | 37 |
| `css/pet.css` | 781 | 28.3 KB | 2 | 55 |
| `css/pet-subtitle.css` | 195 | 7.3 KB | 0 | 0 |
| `css/pet-inspect.css` | 106 | 4.9 KB | 1 | 9 |

**最要命的一条**：`index.css` 和 `pet.css` 有 **10 个同名变量、取值完全不同**——

| 变量 | index.css（金铜/复古） | pet.css（紫/现代） |
|---|---|---|
| `--accent` | `#c9a86a` | `#7F77DD` |
| `--fg` | `#e8e2d4` | `#EDEDED` |
| `--fg-dim` | `#8d8a7e` | `#A7A5B8` |
| `--line` | `rgba(201,168,106,.14)` | `rgba(127,119,221,.28)` |
| `--line-strong` | `rgba(201,168,106,.32)` | `rgba(127,119,221,.52)` |
| `--danger` | `#c96a6a` | `#D4537E` |
| `--font-sans` | Georgia / Songti | Varela Round / 微软雅黑 |
| `--font-mono` | Courier New | Cascadia Mono |
| `--fs-body` | `15px` | `13px` |
| `--fs-title` | `17px` | `16px` |

即：**同一个变量名在两个页面上是两个意思**，任何跨页复用组件都会静默走形。另有 `index.css` 里 4 个 `:root` 块（含浅色主题覆盖）+ 分散在文件后半段的 6 组 `@media` 覆盖同一批变量。

### 1.6 DOM 契约（隐形但很紧）

- `index.html` 里 **89 个 `id`**，其中 **88 个**被 JS 按字面量引用（唯一未引用的是 `stage-tag`）。
- 意味着：任何 HTML 结构调整都可能静默打断某个模块，而 `pytest` 完全看不见（见 1.8）。

### 1.7 持久化契约

6 个 localStorage 键，直接 `JSON.parse`，无版本字段：

```
roleplay_session_id   roleplay_ui_state    roleplay_live2d_poslock
roleplay_llm_state    roleplay_pet_state   roleplay_voice_state
```

### 1.8 质量网现状

| 方面 | 现状 |
|---|---|
| pytest | 1,465 个用例，**强制离线**可跑（`tests/conftest.py`） |
| 其中碰前端的 | **1 个**（`tests/e2e_pet_voice.py`，还需另起静态服务器） |
| JS/CSS 单测 | **0** |
| Lint / 格式化 | **无配置** |
| CI | **无**（没有 `.github/`） |
| 视觉验收 | 有，但全在 `.agent_tmp/canvas_v1/`（`audit2.py` / `region.py` / `ascii.py` / `shot_real.py`），属于**临时目录，未入库** |

即：**前端 1.2 万行代码目前没有任何自动化保护**。这是本次重构最大的风险源，必须第一批解决。

### 1.9 后端与运行面约束（重构不能碰坏）

| 约束 | 位置 | 影响 |
|---|---|---|
| `StaticFiles` 挂在 `/`，`html=True` | `src/roleplay/main.py:189` | 产物必须仍在 `frontend/` 下；`pet.html`、`index.html` 的 URL 不能变 |
| `NoCacheMiddleware` 对 `.html/.js/.css/.json/.map` 与 `/assets/` `/js/` 发 `no-store` | `main.py:49-73` | 已有 no-store，`?v=` 其实是冗余的（P7 再收） |
| CSP `script-src 'self' 'unsafe-eval'`，`style-src 'self' 'unsafe-inline'` | `middleware.py:15-30` | **禁止内联 `<script>`**；ESM 模块化天然合规；`unsafe-eval` 是 PIXI v6 的既有让步，别动 |
| `X-Frame-Options: DENY` | `middleware.py:15` | 第三方 iframe 嵌入不可用（画布层设计里已有路径级覆盖方案） |
| Electron 加载 `http://127.0.0.1:8000/pet.html` | `desktop/src/main/config.js:17` | `pet.html` 路径与文件名**冻结** |
| Electron `sandbox:true` / `contextIsolation:true` / `nodeIntegration:false` | `desktop/src/main/windows.js:199-203` | 前端不能用 Node API，纯浏览器环境 |
| 桌宠探针脚本按选择器抓 DOM | `desktop/scripts/` 11 个脚本（`smoke_render.js` 11 处、`verify_subtitle.js` 9 处、`measure_subtitle_baseline.js` 8 处、`iv_probe_*` 6-7 处） | 选择器改名会打断这些验收脚本，需同步维护 |

### 1.10 死代码

| 文件 | 行/体积 | 引用情况 |
|---|---|---|
| `frontend/redesign.html` | 2,311 行 / 113.9 KB（内联 style 45.5 KB + 内联 script 26.4 KB） | **全仓库零引用**的静态设计稿 |
| `frontend/_l2d_poc.html` | 103 行 | 零引用 |
| `frontend/_verify_blink.html` | 92 行 | 仅 `desktop/scripts/verify_l2d_blink.js` 引用 |
| `frontend/pet-inspect.html` + `pet-inspect.js` + `pet-inspect.css` | 63+172+106 行 | 调试面板 |

`redesign.html` 一个文件就占前端源码体积的 **15%**，且内联 71 KB 样式与脚本（违反 CSP 的 script 约束，只能作为静态稿存在）。

---

## 2. 九条病灶（按代价排序）

| # | 病灶 | 代价 | 证据 |
|---|---|---|---|
| 1 | **前端零自动化保护** | 改任何东西都是盲改 | 1.8：JS 单测 0、lint 无、CI 无、1,465 个 pytest 里只有 1 个碰前端 |
| 2 | **无模块边界，全局即接口** | 加载顺序即依赖；无法静态分析、无法 tree-shake、改名靠全文搜索 | 1.3：0 个 `import/export`，12 个 window API |
| 3 | **两套 CSS 变量表同名不同值** | 跨页组件永远无法复用，且错误是静默的（不报错，只是难看） | 1.5：10 个同名变量取值冲突 |
| 4 | **`chat.js` / `pet.js` 双实现** | 修一个 bug 要改两处，且已经分叉（`loadState` 实现不同） | 1.4 |
| 5 | **手改 `?v=` 缓存号** | 已经出现版本不一致（chat.js v11 vs v9）；漏改 = 用户看到旧代码 | 1.2 |
| 6 | **88 个 id 的隐形契约** | HTML 一动就可能静默失效，且没有测试会发现 | 1.6 |
| 7 | **单文件过大**：`chat.js` 1,282 / `pet.js` 1,699 / `live2d.js` 1,286 / `index.css` 1,443 行 | 定位成本高、review 不可行、多人并行必冲突 | 1.1 |
| 8 | **`redesign.html` 等死代码** | 占 15% 体积，误导新人，`grep` 噪音 | 1.10 |
| 9 | **`?v=` 与 no-store 策略冲突的认知负担** | 每次改前端都要判断「该不该提版本号」 | 1.9 |

---

## 3. 目标架构

### 3.1 目录

```
frontend/
├── index.html              # 薄壳：只剩 DOM + 一个 <script type="module">
├── pet.html                # 同上（路径冻结，Electron 依赖）
├── pet-inspect.html        # 调试页，同样薄壳化
├── assets/                 # 不动（44.2 MB 模型/音频/第三方库）
├── src/
│   ├── core/               # 零业务：被所有 feature 依赖，自己不依赖任何人
│   │   ├── bus.js          #   事件总线（替代跨文件 window 调用）
│   │   ├── store.js        #   极简订阅式状态（set/get/subscribe，可选持久化）
│   │   ├── storage.js      #   localStorage 封装 + 版本字段 + 迁移
│   │   ├── http.js         #   fetch 封装（超时 / 错误归一 / 中止）
│   │   ├── sse.js          #   SSE 流解析（从 chat.js 抽出，纯函数，可单测）
│   │   ├── dom.js          #   $ / $$ / on / el 等
│   │   └── log.js          #   分级日志（替代散落的 console.*）
│   ├── data/               # 只懂协议，不懂 DOM
│   │   ├── chat-api.js     #   /chat/stream  /chat/clear  /api/sessions/*
│   │   ├── characters-api.js
│   │   ├── knowledge-api.js
│   │   ├── llm-api.js
│   │   └── voice-api.js    #   /voice/stt  /voice/tts
│   ├── features/           # 一个目录 = 一个可见功能
│   │   ├── chat/           #   消息流、气泡、打字机、滚动跟随、追问
│   │   ├── hud/            #   温度/灵敏度/速度/缩放/位置 读数与快捷键
│   │   ├── live2d/         #   PIXI + Live2D 渲染层（现 live2d.js 拆开）
│   │   ├── spine/          #   桌宠 Spine 渲染
│   │   ├── voice/          #   STT/TTS/预录语音
│   │   ├── subtitle/       #   桌宠字幕
│   │   ├── knowledge/      #   知识库面板
│   │   ├── llm-switch/     #   模型切换
│   │   ├── layout/         #   分栏拖拽、响应式
│   │   └── decor/          #   画布装饰层 canvas-fx（白炽灯+飞蛾）
│   ├── ui/                 # 无业务的可复用件：toast / modal / splitter / chip
│   ├── pages/
│   │   ├── chat-page.js    # index.html 的入口
│   │   ├── pet-page.js     # pet.html 的入口
│   │   └── inspect-page.js
│   └── styles/
│       ├── tokens.css      # ★ 唯一变量来源（design tokens）
│       ├── reset.css
│       ├── base.css        # 字体、滚动条、选区
│       ├── themes/
│       │   ├── theme-archive.css   #   现 index.css 的金铜/复古主题
│       │   └── theme-pet.css       #   现 pet.css 的紫主题
│       └── components/     # 按组件拆：topbar / stage / chat / hud / toast …
└── tools/                  # 从 .agent_tmp 提升入库的视觉与契约验收
    ├── visual-audit.py     #   亮度/死黑/空格率/色相/分区（现 audit2 + region）
    ├── ascii-preview.py    #   无图像输入时的文本看图（现 ascii.py）
    ├── shot.py             #   Playwright 截图（现 shot_real.py）
    ├── dom-contract.mjs    #   校验 JS 引用的 id/class 在 HTML 里都存在
    └── baselines/          #   基线截图（判定回归用）
```

### 3.2 依赖方向（单向，无环）

```
pages → features → data → core
                ↘ ui ↗
所有层 → styles/tokens.css（通过 CSS 变量，不通过选择器）
```

**硬规则**（用 lint 守住，不靠自觉）：

1. `core/` 不得 import 任何其它层。
2. `data/` 不得出现 `document.`。
3. `features/x/` 不得 import `features/y/`（跨功能一律走 `core/bus.js`）。
4. 任何模块不得写 `window.X = …`（`window.__debug*` 诊断钩子除外，且必须带注释）。
5. 任何 `.js` 不得出现内联 `<script>`（CSP 已禁）。

### 3.3 构建方式：**不引入打包器**（Plan A）

| 方案 | 做法 | 优点 | 代价 |
|---|---|---|---|
| **A 无构建 ESM**（推荐） | 原生 `type="module"` + `importmap` 映射三个 UMD 库；`tsc --noEmit` 只做类型检查（JSDoc 标注），不产出 | 运行方式完全不变（仍是 `uvicorn` 起后端 → 浏览器打开）；无产物目录、无 sourcemap 债；Electron 无需重新打包 | 无压缩/无 tree-shaking；单文件多时首次加载请求数略多（本机场景可忽略） |
| B Vite 打包 | 新增 `web/` 源 + 产物落 `frontend/dist/` | 可压缩、HMR、生态完整 | 改运行流程（要先 `npm run build`）；后端挂载路径要改；Electron 要重新打包；等于新增一条构建链要养 |

**选 A**。理由：这是**本地跑的单机应用**（后端在 127.0.0.1、Electron 壳），1.2 万行源码的传输成本不是问题，而「多一条构建链」是永久成本。等真需要 HMR 或真的开始用 React 时再上 B，那时 A 的模块边界可以直接搬过去。

> ⚠️ 这条是**需要你确认的决策之一**（第 9 节 Q1）。

---

## 4. 六项技术决策

| # | 决策 | 选择 | 备选与不选的原因 |
|---|---|---|---|
| D1 | 模块系统 | **原生 ESM + importmap** | 不选打包器（见 3.3） |
| D2 | 语言 | **JS + JSDoc 类型注解**，`tsc --noEmit --checkJs` 做闸门 | 不选全量 TS 迁移：现网 1.2 万行、无类型基础，一次性改语言会把「重构」变成「重写」，风险不可控。JSDoc 拿到 90% 的类型收益（跳转、改名、找错），改动量却小一个量级 |
| D3 | UI 框架 | **不上框架**（手写 + 小 store + 事件总线） | 现有 DOM 已写死 88 个 id，上 React/Vue 等于重写全部 HTML + 全部交互；而需求并未要求虚拟 DOM（消息量小、无高频重渲染） |
| D4 | 状态管理 | **自写 `core/store.js`（约 60 行：get/set/subscribe/persist）** | 不引 Redux/Zustand：依赖为 0 是当前项目的隐形资产（离线可跑、无供应链风险） |
| D5 | 样式组织 | **单一 tokens.css + 每页一个 theme + 按组件拆文件**；`@layer` 声明优先级 | 不保留「两套变量同名不同值」，改为 `--color-accent`（语义层）与 `--theme-*`（主题层）分离；`@layer` 免掉现在靠选择器特异性互相压的写法 |
| D6 | 命名与出口 | 每个 feature 导出**一个 `mount()`**，内部状态私有；页面只负责按需 `mount` | 替代现在的「IIFE 自执行 + 挂 window」，让加载顺序不再等于依赖顺序 |

---

## 5. 文件处置表（26 个文件逐个安排）

| 现文件 | 行数 | 处置 | 去向 / 说明 |
|---|---:|---|---|
| `index.html` | 294 | **改薄** | 保留全部 88 个被引用的 id 与结构；`<script>` 从 16 个降为 1 个 `src/pages/chat-page.js` |
| `pet.html` | 171 | **改薄** | 路径冻结（Electron），同上 |
| `pet-inspect.html` | 63 | 改薄 | 或移入 `tools/`（见 Q5） |
| `redesign.html` | 2,311 | **移出** | 零引用的设计稿 → `docs/design/redesign-static.html`（不入前端构建，也不占 15% 源码体积）；若你还想留作参考 |
| `_l2d_poc.html` | 103 | **删 / 归档** | 零引用；建议删（git 里有） |
| `_verify_blink.html` | 92 | 移入 `tools/` | `desktop/scripts/verify_l2d_blink.js` 依赖它，路径要同步改 |
| `js/canvas-fx.js` | 1,756 | **拆** | → `src/features/decor/`：`lamp.js`（灯硬件+辉光）/ `cone.js`（光锥+尘）/ `moth.js`（蛾精灵+行为）/ `backdrop.js` / `index.js`（编排 + mount）。参数全部外置到 `decor/config.js` |
| `js/chat.js` | 1,282 | **拆 4 份** | SSE 解析 → `core/sse.js`；协议调用 → `data/chat-api.js`；消息流/气泡/打字机 → `features/chat/`；HUD 与快捷键 → `features/hud/`。`PET_MODE` 分支随双实现一起消失 |
| `js/pet.js` | 1,699 | **拆 3 份** | 与 chat 共用的部分并入 `features/chat/` + `data/`；Spine 相关 → `features/spine/`；气泡/字幕/引导 → `features/subtitle/` + `features/onboarding/` |
| `js/live2d.js` | 1,286 | **拆 3 份** | PIXI 应用与渲染循环 → `features/live2d/renderer.js`；`_fit` 取景数学 → `features/live2d/fit.js`（**纯函数，可单测**）；交互（拖拽/缩放/点击/眨眼）→ `features/live2d/interaction.js` |
| `js/spine.js` | 980 | 就地模块化 | → `features/spine/` |
| `js/voice.js` | 472 | 就地模块化 | → `features/voice/recorder.js` + `data/voice-api.js` |
| `js/pet-voice.js` | 438 | 就地模块化 | → `features/voice/manifest.js` |
| `js/llm-switch.js` | 670 | 就地模块化 | → `features/llm-switch/` + `data/llm-api.js` |
| `js/knowledge.js` | 538 | 就地模块化 | → `features/knowledge/` + `data/knowledge-api.js` |
| `js/pet-subtitle.js` | 263 | 就地模块化 | → `features/subtitle/` |
| `js/desktop-pet.js` | 181 | 就地模块化 | → `features/desktop-launch/`（只有 1 个端点，也可并入 `ui/`） |
| `js/layout.js` | 144 | 就地模块化 | → `features/layout/` |
| `js/live2d-bootstrap.js` | 51 | **合并** | 只有 51 行且 `"use strict"` 都没有 → 并入 `pages/chat-page.js` |
| `js/rain.js` | 26 | 并入 | 与 canvas-fx 同属装饰层 → `features/decor/rain.js` |
| `shared/pet-core.js` | 97 | 并入 | → `core/`（它本来就是公共件） |
| `css/index.css` | 1,443 | **拆 + 变量重写** | tokens 抽到 `styles/tokens.css`；金铜主题 → `styles/themes/theme-archive.css`；其余按组件拆到 `styles/components/` |
| `css/pet.css` | 781 | **拆 + 变量重写** | 紫主题 → `styles/themes/theme-pet.css`；组件规则与 archive 合并（同名变量冲突按 D5 消除） |
| `css/pet-subtitle.css` | 195 | 并入 | → `styles/components/subtitle.css` |
| `css/pet-inspect.css` | 106 | 并入 | → `styles/components/inspect.css`（或随调试页移入 tools） |

---

## 6. 阶段计划

> 原则：**每一阶段结束时站点都是可用的、可回滚的**（strangler pattern：新结构在旁边长出来，最后一次性拔管）。任何阶段都不许出现「重构到一半不能跑」的状态。
> 工作量是「一个熟练开发 + 有自动化闸门」的净编码时间，不含等待评审。

### P0 · 保底快照 ✅ 已完成

| 项 | 内容 |
|---|---|
| 产物 | commit `1c5966f` + tag `frontend-v3-baseline` |
| 范围 | 只提交前端 4 文件 + `docs/canvas-layer-design.md`；`data/` `scripts/` `src/` 下其它工作流的 39 个未提交改动**一律未动** |
| 回滚 | `git reset --hard frontend-v3-baseline` |

### P1 · 长出自动的质量网（**先做这个，否则后面全是盲改**）

| 项 | 内容 |
|---|---|
| 范围 | 新增根 `package.json`（devDeps 全部本地）；`.gitignore` 加 `node_modules/`；`tools/` 目录把 `.agent_tmp/canvas_v1/` 里已验证的脚本提升入库 |
| 产物 | ① `npm run lint`（ESLint，规则含 3.2 的四条硬规则）② `npm run typecheck`（`tsc --noEmit --checkJs`，先只覆盖 `tools/` 与新代码，旧代码用 `// @ts-nocheck` 暂时豁免并登记）③ `npm run test`（Vitest + jsdom，先只测纯函数）④ `tools/dom-contract.mjs`（**校验 88 个 id 契约**）⑤ `tools/shot.py` + `tools/visual-audit.py` + 基线截图 ⑥ `npm run check` 串起 ①~④ |
| 验收 | `npm run check` 全绿；故意改坏一个 id 能被 `dom-contract` 抓到；故意在 `features/x` 里 import `features/y` 能被 lint 抓到；视觉基线图与当前截图 diff < 阈值 |
| 回滚 | 纯新增文件，删掉即可 |
| 工作量 | **1.5 人日** |

### P2 · 抽出 `core/` 与 `data/`（不改行为）

| 项 | 内容 |
|---|---|
| 范围 | 只建新文件，**不改任何现有调用**：`core/{bus,store,storage,http,sse,dom,log}.js`、`data/*-api.js`。把 `chat.js` 里的 SSE 解析与 `prompt/clear` 调用**复制**过来（不是移走），加单测 |
| 产物 | 新模块 + 单测；旧 `chat.js` 仍走自己那套 |
| 验收 | 单测覆盖 `sse.js`（分块边界、`event:`/`data:` 多行、`[DONE]`、中文跨块切分）与 `storage.js`（坏 JSON、类型漂移、缺键）；pytest 1,465 全绿（前端未动，应零影响） |
| 回滚 | 新文件不被引用，无风险 |
| 工作量 | **2 人日** |

### P3 · `chat` 页切到新结构

| 项 | 内容 |
|---|---|
| 范围 | `index.html` 改薄壳；`js/chat.js` 拆成 `features/chat/` + `features/hud/`，改用 `core/sse.js` + `data/chat-api.js`；删除旧 `chat.js` 的页面入口（保留 `RoleplayChat` 对外面作为过渡 shim，供 `pet.js` 继续用） |
| 产物 | index.html 只剩 1 个 module script；`RoleplayChat` 由 `features/chat/index.js` 导出并临时挂 window（标 `// TODO(P4)`） |
| 验收 | ① 聊天全链路人工过一遍：发消息 / 流式逐字 / 情绪标签 / 追问 / 清空 / 刷新后会话恢复 ② HUD 全部快捷键（温度 ± / 灵敏度 / 速度 / 缩放 / 位置 / LLM / 主题）逐个验证 ③ 视觉截图与 P1 基线 diff < 阈值 ④ `npm run check` 全绿 |
| 回滚 | `git revert` 单次提交即回到旧 `chat.js`（旧文件此时仍在） |
| 工作量 | **3 人日**（这是最大的一块，1,282 行） |

### P4 · `pet` 页切到新结构（顺带消灭双实现）

| 项 | 内容 |
|---|---|
| 范围 | `pet.html` 改薄壳；`js/pet.js` 拆到 `features/{spine,subtitle,onboarding,voice}`；`chat.js` 的重复件（`detectGesture`/`loadState`/SSE）从 `features/chat` 与 `core` 复用，**删掉 pet.js 里那套副本**；`PET_MODE` 常量删除 |
| 产物 | `js/chat.js`、`js/pet.js` 彻底消失；两页共享同一套 `core/data` |
| 验收 | ① 桌宠页人工过：气泡打字机 / 上翻历史 / 语音 / 字幕 / 引导 / 渲染器迁移逻辑 ② **Electron 壳实跑**：`desktop` 用 `npm start` 起，确认 `http://127.0.0.1:8000/pet.html` 正常、透明/置顶/穿透/拖拽/快捷键不回归 ③ `desktop/scripts` 里 11 个探针脚本跑通（选择器如改名需同步）④ localStorage 旧键值能读出来（`roleplay_pet_state` 保留，不迁移） |
| 回滚 | 同 P3 |
| 工作量 | **3.5 人日** |

### P5 · 样式系统统一

| 项 | 内容 |
|---|---|
| 范围 | 写 `styles/tokens.css`：把两份变量表的并集按「**语义层 / 主题层**」重排——语义层（`--color-fg`、`--color-accent`、`--space-*`、`--radius-*`、`--z-*`、`--dur-*`、`--ease-*`）只声明一次，主题层（`theme-archive` 金铜 / `theme-pet` 紫）只赋不同的值；`index.css`/`pet.css` 按组件拆文件；用 `@layer reset, tokens, base, components, utilities` 替代现在的特异性互压 |
| 产物 | 4 个 CSS 文件 → `tokens.css` + 2 个 theme + 约 12 个 component 文件；`?v=` 全部删除（后端已 no-store） |
| 验收 | ① **主题切换（含浅色主题）逐屏比对截图**：index 页 8 个区域 × 2 主题、pet 页 5 个区域 ② 所有 `--var` 引用在 CSS 里都能解析（加一个 lint 脚本）③ 无 `!important` 新增，原有的登记清单 ④ 移动端 3 个断点（860 / 480 / 560 高）截图 |
| 回滚 | 保留旧 4 个 CSS 文件直到验收通过，通过后一次删除 |
| 工作量 | **2.5 人日** |

### P6 · 装饰层（canvas-fx）模块化 + 参数外置

| 项 | 内容 |
|---|---|
| 范围 | 1,756 行拆成 `lamp / cone / moth / backdrop / index`；把散在函数里的魔法数收进 `decor/config.js`（灯位、锥角、蛾数、柔边档、尘密度指数、rim 参数…）；`prefers-reduced-motion` 与「异常全静默」两个约定写成模块级契约注释 |
| 产物 | 参数可调、可关（`?fx=off` 已有，补 `?fx=a|b` 等变体）；帧率与绘制调用计数进 `window.__fxStats`（现有 `__canvasFx` 保留兼容） |
| 验收 | ① 视觉截图与 P5 基线 diff < 阈值（本轮**只拆不改观感**）② `tools/visual-audit.py` 四项指标不回退：死黑 ≤0.06%、16×16 空格率 ≤0.0%@0.02、平均亮度 ≈24%±1、过曝(>0.85) ≤3% ③ 真机 fps（非 headless）记录一次基线 |
| 回滚 | 旧 `canvas-fx.js` 保留至验收通过 |
| 工作量 | **2 人日** |

### P7 · 清理与运维收尾

| 项 | 内容 |
|---|---|
| 范围 | 删 `redesign.html`（移 docs）、`_l2d_poc.html`；`_verify_blink.html` 移 `tools/` 并改 `desktop/scripts` 路径；`pet-inspect.html` 移 `tools/`（或保留但薄壳化）；`.gitattributes` 定 CRLF/LF（git 现在对每个前端文件都在警告）；写 `docs/frontend-architecture.md`（模块图 + 硬规则 + 新增功能的落位指引） |
| 产物 | 前端源码体积从 735 KB 降到 ~570 KB；`docs/frontend-architecture.md` |
| 验收 | `git grep redesign` 无命中；`npm run check` 全绿；pytest 全绿；Electron 探针全绿 |
| 工作量 | **1 人日** |

### P8 ·（可选）打包器

只有当真的需要压缩/HMR/引入 npm 依赖时才做。届时 `src/` 的模块边界可直接搬 Vite，估算 0.5 人日。

### 汇总

| 阶段 | 内容 | 人日 | 可回滚点 |
|---|---|---:|---|
| P0 | 基线快照 | ✅ | tag |
| P1 | 质量网（lint/typecheck/单测/DOM 契约/视觉基线） | 1.5 | 新增文件 |
| P2 | `core/` + `data/`（复制式，不改调用） | 2.0 | 无引用 |
| P3 | chat 页切换 | 3.0 | 单次 revert |
| P4 | pet 页切换 + 消灭双实现 | 3.5 | 单次 revert |
| P5 | 样式系统统一 | 2.5 | 旧 CSS 保留 |
| P6 | 装饰层模块化 + 参数外置 | 2.0 | 旧文件保留 |
| P7 | 清理与文档 | 1.0 | 单次 revert |
| **合计** | | **15.5 人日** | |

**建议节奏**：P1 单独一次上线（纯收益、零风险）；P2 跟上；P3/P4 之间隔一次完整回归（因为双实现要合流）；P5/P6 可并行（不同文件）。

---

## 7. 质量闸门（每阶段都必须过）

| 闸门 | 命令 | 判据 |
|---|---|---|
| 语法 | `node --check` each / `npm run lint` | 0 error；warning 数不得增加 |
| 类型 | `npm run typecheck` | 0 error |
| 单元 | `npm run test` | 全绿；新增模块必须有测试 |
| DOM 契约 | `node tools/dom-contract.mjs` | JS 引用的每个 id/class 都在对应 HTML 里存在 |
| 后端 | `pytest`（离线） | 1,465 全绿，**一个都不许跳过** |
| 视觉 | `python tools/shot.py <tag>` + `python tools/visual-audit.py` | 指标不回退（清单见 P6）+ 与基线图 diff 低于阈值 |
| 桌宠 | `cd desktop; npm run check; npm run smoke` | 全绿 |
| 人工 | 逐页清单（见各阶段「验收」） | 打勾 |

> 视觉闸门的判据不是「好看」，是**四项可量化的不回退指标**：死黑率、16×16 空格率、平均亮度、过曝率；「好看」永远由你定。

---

## 8. 风险登记

| # | 风险 | 概率 | 影响 | 应对 |
|---|---|---|---|---|
| R1 | 88 个 id 的隐形契约在拆分中被静默破坏 | 高 | 某功能静默失效 | P1 先建 `dom-contract` 闸门；P3/P4 每次提交都跑 |
| R2 | 前端零测试 → 行为回归无法自动发现 | 高 | 只有人眼能发现 | 人工验收清单（每阶段列死）+ 视觉基线 diff |
| R3 | Electron 壳（`sandbox:true`）里某些新写法不可用 | 中 | 桌宠起不来 | P4 必须实跑 `desktop npm start`；`desktop/scripts` 11 个探针全跑 |
| R4 | 样式变量重排导致某处颜色/间距走形 | 中 | 难看但不报错 | 逐屏截图比对（主题 × 区域矩阵）；旧 CSS 保留到验收通过 |
| R5 | `?v=` 删除后 Electron 缓存旧文件 | 低 | 桌宠看不到新代码 | 后端已 `no-store`；P5 先在 Electron 里验证一次 |
| R6 | 拆分过程中两套实现同时在跑（P3~P4 之间） | 中 | 修 bug 要改两处 | 该窗口期尽量短；`RoleplayChat` 过渡 shim 只许变薄不许变厚 |
| R7 | 一次性动 1.2 万行的诱惑 | 中 | 不可 review、不可回滚 | **硬规矩：每阶段独立可上线**；单次提交 > 400 行 diff 必须拆 |
| R8 | 视觉层被顺手「优化」 | 中 | 你又要否一轮 | P6 明确「只拆不改观感」，任何观感改动单独立项等你拍板 |

---

## 9. 需要你拍板的 7 个点

| # | 问题 | 我的建议 |
|---|---|---|
| **Q1** | 用**无构建 ESM**（Plan A，运行方式不变）还是**上 Vite 打包**（Plan B，要先 `npm run build`）？ | **A**。1.2 万行、单机、无压缩需求；B 会永久多养一条构建链 |
| **Q2** | 语言：**JS + JSDoc 类型**（`tsc --noEmit` 当闸门）还是**全量 TS 迁移**？ | **JS + JSDoc**。后者等于重写，风险翻倍而收益在本地应用里不成立 |
| **Q3** | `redesign.html`（113.9 KB、零引用的设计稿）**移到 `docs/design/`** 还是**直接删**（git 里有）？ | 移到 docs。它是有价值的设计资产，但不该占前端源码体积 |
| **Q4** | `pet-inspect.html` 调试面板：**保留**（薄壳化）还是**移入 `tools/`** 不入前端？ | 移入 `tools/`。它是开发工具不是产品页 |
| **Q5** | 两个主题（**金铜/复古 archive** vs **紫/现代 pet**）是**保持两套**，还是**统一成一套**（比如 pet 页也用金铜）？ | **保持两套**，但共享同一份语义变量（这就是 P5 干的事）。统一风格是审美决定，得你定 |
| **Q6** | 桌宠页现在用的是紫主题 + Varela Round，与主站金铜 + Georgia 完全不同世界 —— 这是有意的吗？ | 若是有意，P5 保留两套；若是历史遗留，可以合并。**需要你一句话** |
| **Q7** | 重构期间**要不要继续迭代视觉**（白炽灯/飞蛾那条线）？ | **暂停**。P1~P4 只做结构，视觉冻结在 `frontend-v3-baseline`；P6 之后再开视觉迭代，避免「边改结构边改观感」互相掩盖问题 |

---

## 10. 附录：命令与环境

```powershell
# 解释器（项目自带，禁用全局 python）
.\.venv\Scripts\python.exe -X utf8

# 后端（前端静态资源由它伺服）
.\.venv\Scripts\python.exe -m uvicorn roleplay.main:app --host 127.0.0.1 --port 8000

# 后端测试（离线，mock LLM；.env 指向本机计费网关，任何真实 LLM 调用都会扣费）
.\.venv\Scripts\python.exe -m pytest -q

# 前端（P1 之后）
npm run lint          # ESLint（含四条模块硬规则）
npm run typecheck     # tsc --noEmit --checkJs
npm run test          # Vitest + jsdom
npm run check         # 上面三者 + dom-contract

# 视觉验收（P1 之后入 tools/）
.\.venv\Scripts\python.exe tools\shot.py <tag> --t 3,7,12
.\.venv\Scripts\python.exe tools\visual-audit.py .agent_tmp\shots\<tag>_stage_3.png
.\.venv\Scripts\python.exe tools\ascii-preview.py <png> --w 72 --mode lum   # 无图像输入时看构图

# 桌宠
cd desktop; npm run check; npm start
```

**Chromium 在本机的唯一可用启动方式**（默认 `pw.chromium.launch()` 会找不存在的 headless shell）：

```python
pw.chromium.launch(
    executable_path=r"C:\Users\Lenovo\AppData\Local\ms-playwright\chromium-1208\chrome-win64\chrome.exe",
    headless=True,
    args=["--no-sandbox", "--disable-crash-reporter",
          "--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"],
)
```

---

*本文所有数字来自 2026-10-19 对 `frontend/` 的脚本实测；引用行号以 commit `1c5966f` 为准。*
