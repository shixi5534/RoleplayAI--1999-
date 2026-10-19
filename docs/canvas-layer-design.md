# 透明画布互动层 · 整合版技术计划 v1.0

> 项目：roleplay-ai（`C:/Users/Lenovo/WorkBuddy/2026-07-27-16-45-03/roleplay-ai`）
> 状态：调研 + PRD + 架构 + 对抗评审 + 两项 spike 全部完成。**未修改项目任何代码。**
> 日期：2026-10-17

---

## 0. 需求原文

> 这个项目的呈现页面有独立单独的一层透明画布，在回应用户时，可以通过代码或者其他方式，在画布上渲染画面，来增加互动感。这个能力的上限应该是和所用模型的能力强相关；为了后续弱模型（无记忆、每次调用不带上文）能快速上手，可以在后台写例子，类似于 skill 或者 mcp。先产出计划，不要修改代码。

## 1. 调研结论（摘要）

**方向判断：工具化是主干道。** 对「模型驱动画布渲染」，结构化指令/白名单机制在时延（百毫级 vs computer use 秒级循环）、可靠性（确定性管道 vs 视觉定位错误率）、成本（文本 token vs VLM 截图调用）四个维度全面占优；computer use 的定位是「无 API 环境的降级方案」，而浏览器 canvas 有完备 JS API。连 OpenAI 自家 Canvas 走的也是「结构化触发 + 沙箱预览」而非 computer use。

**强相关项目**：

| 项目 | 相关度 | 借鉴点 |
|---|---|---|
| A2UI（Google, Apache 2.0） | 架构同构 | 声明式 JSON + 客户端可信目录，「传消息不传可执行代码」 |
| Claude Artifacts | L3 标杆 | 沙箱三层隔离（sandbox 属性 + CSP + 禁同源） |
| OpenAI Canvas | 产品先例 | 模型驱动画布表面 + 触发时机被度量训练（83%） |
| Open-LLM-VTuber / ChatdollKit / VTube Studio API / Amica | 场景同构 | in-band 标签、能力清单注入 prompt、参数注入+缓动枚举、情绪权重两段式 |
| Neuro-sama | 形态最接近 | 闭源无公开资料 |
| MCP-UI / MCP Apps / RiveMCP / Text-to-Lottie skill | 机制参考 | ui:// 资源、工具目录两跳暴露、LLM 写动画 JSON 的 skill 禁令 |

**缺口**：「透明画布层 + 模型驱动装饰渲染 + 角色扮演」无完整开源先例；国内星野/猫箱止于预置模板。基础设施 2026 年齐备（MCP-UI ratified、A2UI 开源），时机合适。

## 2. 产品定义与能力叙事（对抗评审后修订）

**一句话**：在呈现页叠加独立透明画布，**后端策略保底、模型指令增强**，能力上限随模型强度分层，弱模型零配置上手。

**叙事修订**（原「能力上限随模型强度」名存实亡，改为）：**画布永远在线（后端保底下限）；模型强弱决定画面的机智程度（决策上限）。**

四档：

| 档 | 能力 | 决策者 | 默认 |
|---|---|---|---|
| L0 | 后端情绪驱动氛围（策展 preset） | 后端策略 | 开 |
| L1 | 白名单原语，即时微调（「在这放朵花」的细粒度） | 模型 | 开 |
| L2 | 策展 preset 整体氛围（一整套协调视觉） | 模型选 preset | 开 |
| L3 | 沙箱代码生成，完全自由（preset 库未覆盖场景的申诉通道） | 模型 | 关 |

档位判定：`model_id` glob 映射（`canvas_model_tiers`，如 `{"qwen*":"L1","*r1*":"L3","*":"L1"}`），来源 `req.llm.model` → `settings.llm_model`。

## 3. 核心架构（最终版）

```
装饰栈（既有四层 + 新第五层）：
  .kv-backdrop(z-2) .kv-veil/film-grain/rain(z-1)   [既有]
  #canvas-layer(--z-canvas:10, pointer-events:none)  [新增，inset 顶部避开 --topbar-h]
  .stage/Live2D  topbar  .modal  .toast

双通道（同源于一次文本生成，零额外 LLM 调用）：
  ① in-band [canvas:...] 指令：随 SSE chunk 流式到达，前端剥离渲染（先发优势：思考期即有画面）
  ② SSE canvas 事件：流末、done 之前下发，带钳制后参数与 seq，前端去重后仅应用增量
```

**触发时机后置（第一优先级设计）**：
- 「何时渲」= 后端策略：情绪高分 / 关键词 / 剧情状态触发 + 预算冷却。注入点现成——`orchestrator.py:1053-1063` emotion 事件先于一切 chunk，其后立即 yield canvas 事件；**不等 ctx_task**（`orchestrator.py:1065`，检索可达数十秒，「先发」是后端驱动的核心体验优势）；
- 「渲什么」= 模型决策（L1/L2/L3）。模型指令与后端注入共用一条渲染队列，FIFO + 预算共享；
- 语义定调：情绪检测作用于 user 消息（`orchestrator.py:283`），「sad→雨」是**用户情绪共情镜像**，不是演出氛围；回复级情绪信号是架构缺口，P1+。

**分层与生命周期**：

| 层 | 用途 | 约束 |
|---|---|---|
| behind | 氛围默认层（角色后、既有装饰层之下） | 新 ambient 带过渡替换旧的（单槽） |
| front | 角色前少量标记 | safe-area 顶 15%/底 20% 避让人物 bbox；桌宠默认禁 |
| ui | 仅预设符号粒子（❀⚑✦） | **不做自由飘字**（聊天气泡+桌宠字幕+飘字三套文本通道重叠）；文本一律归既有气泡 |

生命周期：`ambient`（持续，behind 单槽，可被覆盖或 clear）/ `burst`（瞬时，TTL 自灭，允许多个）。语法 layer 默认 behind、kind 由 op 推断（scene→ambient），弱模型永远只写 `[canvas:scene|rain]`。

**预算与冷却**：
- ambient 不计主动画预算（防叠加靠单槽）；
- front/burst 计预算：普通轮 1 条；高分情绪轮（score≥0.7，emotion 事件现成）或剧情关键词命中轮 3 条；
- 同类 preset 60s 去重（防审美疲劳，非防数量）；
- 元素预算按视口面积 **sqrt 缩放**（视觉密度与边长成正比）；桌宠窗（320×420）在缩放基础上再减半（always-on-top 常驻桌面）；
- 预算账本记在**前端画布控制器**（后端流结束后才见完整 reply，`orchestrator.py:1106`）；下一轮 prompt 回一句「上条回复画布已用 N/2」（挂点 `orchestrator.py:437-479`）；
- 拦截必须留痕：done 事件或 console 带统计（parsed/applied/dropped/clamped），否则线上无法归因。

**策展边界**：策展制只管 L1/L2 的默认审美（preset 定义调色板/轨迹/节奏，模型只写名字得全套；未定义维度才回落 L1 参数）；**L3 保留完全自由**，是策展失效时的申诉通道。撑住卖点的三根支柱：preset 库可扩展（JSON 文件化）+ L1 组合空间 + L3 逃生舱。首批 preset ≤6 个，对齐情绪七父类（`mapping.py:20-31`：happy/sad/angry/anxious/surprise/fear/neutral）；preset 种子与示例库种子是同一笔投入。

## 4. 协议规格（spike 裁决后最终版）

### 4.1 语法

```text
[canvas:<op>|<主参数>|<k>=<v> <k>=<v> ...]

op ∈ {text, sprite, particle, shape, scene, clear}    # clear 无参数
主参数: text=文案(≤40字, 禁 |][) | sprite=贴图名 | particle=粒子预设 | shape=图形名 | scene=模板名
k ∈ {x, y, color, size, dur, count, delay, easing, intensity, layer, kind}
```

### 4.2 默认值表（spike 裁决补全，前后端唯一事实源）

| 键 | 默认 | 值域 |
|---|---|---|
| x, y | 0.5 | 0..1（3 位小数，y 向下） |
| color | #FFFFFF | #RRGGBB 或 16 命名色板（不分组） |
| size | 24 | text 字号 12..96px / shape 半径 0.01..0.5 |
| dur | 2.0 | 0.3..8.0 秒 |
| count | 12 | 1..64 |
| delay | 0 | 0..3.0 秒 |
| easing | linear | linear/easeIn/easeOut/easeBoth/overshoot/zip（VTube Studio 命名） |
| intensity | 0.5 | 0.2..1.0（仅 scene；默认可由 emotion score 承接） |
| layer | behind | behind/front/ui |
| kind | 由 op 推断（scene→ambient，其余→burst） | ambient/burst |

### 4.3 spike 裁决（parser-spike 87/87 通过后定）

| # | 分歧 | 裁决 |
|---|---|---|
| S1 | 流末未闭合标签：后端保留文本 vs 前端「丢弃残余」删可见文本 | **统一 release**：前端显示口径 = 后端权威口径；prompt 声明单行闭合仅作缓解 |
| S2 | >400 字符指令 vs 400 安全阀阈值冲突，前端行为随 chunk 边界抖动 | **双修**：采纳 S3 补丁（出现 `]`/`[`/`\n` 而 exec 未匹配即立即释放）；安全阀阈值提至 600 兜底 |
| S3 | 语法死前缀（`[canvas:]` 等永不合法前缀）前端流末误丢 | **纳入 spec**（补丁已实测与后端一致） |
| — | kv 分隔符歧义（`|x=0.5|y=0.4` 致整条静默跳过，真实必踩） | **宽容**：解析器将 kv 段竖线等价空格（合法语法无竖线，宽容零误判）+ prompt 反例明示 |
| — | clear 带参 / intensity 非 scene 现整条作废 | **宽松**：忽略非法键，不作废整条 |
| — | 大小写/全角 | 零容忍维持；prompt 明示 ASCII 小写 |

其余纪律：剥离只合并 `[ \t]{2,}`、**禁 trim 换行**（chat.js:104-108 血的纪律）；原文 ≤400 字符；单回复 ≤8 条（含后端注入）；已知限制：markdown 代码块内 `[canvas:` 误剥率 100%（prompt 反例缓解，不期根治）。

### 4.4 后端解析

正则 `re.compile(r"\[canvas:([a-z]+)(?:\|([^\[\]\n]*))?\]")`，随后白名单校验 + 钳制。性能实测：Python 整段 10k 字符 0.079ms；JS 流式最坏逐字符 4.19ms——远低于 SSE 预算。

## 5. 安全设计

### 5.1 L1/L2（零注入面）

白名单枚举校验（op/键/色板/模板名）；未知指令静默忽略 + 日志；参数钳制（坐标/颜色/时长/数量/速率/同屏元素）。**主页面严禁 eval/new Function 模型内容**（CSP 的 unsafe-eval 是 PIXI v6 filter 的既有让步，middleware.py:19-20，不得扩大解释）。画布资源 URL 同源（CSP `connect-src 'self'`）。

### 5.2 L3 沙箱（sandbox-spike 13/13 PASS，GO）

架构：专用路由 `/canvas-sandbox.html` + iframe `sandbox="allow-scripts"`（不给 allow-same-origin → opaque origin）+ 路径级响应头覆盖 + postMessage + TTL 15s。

**实测结论**（Chromium 145 headless）：
- 基线 XFO DENY 确实挡同源 iframe → middleware.py:38 setdefault 必须先改；
- 路径覆盖表成立：沙箱页同源可嵌入，外站仍被挡（沙箱页自身也不被外站嵌套）；
- 沙箱隔离完整：子页访问 parent.document/localStorage/cookie 全部 SecurityError（cookie 是抛异常，比预期更严）；
- srcdoc 继承父页 CSP（无 nonce 时内联脚本被拦）→ 专用路由判断成立；
- postMessage：子→父通（origin="null"）；父→子必须 `targetOrigin='*'`（`'null'` 抛 SyntaxError，真实 origin 静默丢弃）；
- `connect-src 'none'` 不影响 postMessage；harness 所需 JS/CSS 必须加载时引入，不能运行时 fetch；
- new Function 可执行可 catch；TTL teardown 干净（移除 iframe 后心跳停止）。

**六条落地条件**：
1. middleware 路径感知覆盖表（见 5.3）；
2. harness **外置**（沙箱 CSP 无 unsafe-inline，内联脚本会被拦——与项目外置脚本惯例一致）；模型代码经 postMessage 下发 + new Function 执行；
3. iframe URL 带一次性 token；父侧 **source 身份 + token + schema 三重校验**（origin 白名单不可行，子页 origin 恒为 null）；
4. 就绪判断用 postMessage 信号，**不用 load 事件**（被拦 iframe 也触发 load，Chrome 内部提交错误页）；
5. **ready 信号必须等画布有真实尺寸**（视觉验证实测教训，2026-10-17）：iframe 刚加载时 `innerWidth` 可能为 0，若此刻发 ready，模型代码会捕获 `W=H=0` → 所有粒子挤在左上角（实测 bbox 从 [0,0,33,35] 到修复后 [0,2,622,359]）；harness 需轮询 `innerWidth>0` 布局确定后才发 `harness-hello`；
6. **不得依赖 `new Function` 的返回值**：无 `return` 即返回 undefined（JS 函数语义，实测证实），执行结果以「无异常」为准。

**视觉验证已通过**（2026-10-17，headless Chromium 145 实测 + 截图）：沙箱 iframe 透明叠加在 mock 舞台上，模型代码（postMessage → new Function）在沙箱内 canvas 渲染粒子动画，A2/A3 截图粒子位置不同证明动画运行；HUD 实时显示三项隔离 BLOCKED；基线 XFO DENY 对照舞台空白。证据在 `canvas-spike/visual/`（run_visual.py 可复现，含像素级诊断：非透明像素数 + bbox + emoji 字形探针）。

**视觉迭代教训**（同一机制、四版模型代码的对比，正是「策展制」的实证）：v2 = 随机 emoji + 彩色圆点（无艺术指导，像特效乱炖）→ v4 = 暗色舞台 + 四色封顶色板 + 三层景深 + 心/瓣/星 canvas 绘制形 + 尺寸下限纪律 + 开场冲击环 + 边缘淡入淡出 + 近景微光 → v5 = 8×6 分层抖动网格（48 颗，覆盖率均匀）+ 景深排序绘制（画家算法）→ **v6 = 最终视觉语言（用户定向「抖音特效风」，否决了 v2-v5 的氛围型慢飘）**：事件型 punch——① 弹幕滑行（白字 + 墨色粗描边，右入左出，边缘淡入淡出）② 大字 slam（抖音红 `#FE2C55` + 13px 墨色描边 + 金色下划条，easeOutBack 缩放砸入带回弹，微旋转，定格后放大淡出）③ 爱心 pop（右下「点赞键位」每 0.35s 一颗，pop 缩放 + 上浮 + 正弦 wobble + 淡出 + 微光）④ 字符爆点（💥✨⭐😱 随机位置 pop）。**渲染机制始终相同，审美走向完全由「策展」层决定**。落地时 L2 preset 目录按抖音特效风人工策展（事件型为主、氛围型降级为可选 preset），reference 实现见 `canvas-spike/visual/parent.js` 的 MODEL_CODE（v6）。

### 5.3 middleware.py 最小改动（只描述，未实施）

```python
SANDBOX_PATHS = ('/canvas-sandbox.html',)
SANDBOX_CSP = ("default-src 'self'; script-src 'self' 'unsafe-eval'; "
               "style-src 'self' 'unsafe-inline'; connect-src 'none'; img-src 'self' data:")
# 头部设置处（约 38 行）改路径感知：
#   path in SANDBOX_PATHS → XFO: SAMEORIGIN + CSP: SANDBOX_CSP（覆盖，非 setdefault）
#   else → setdefault('X-Frame-Options', 'DENY')（现状不动）
# 沙箱路由需透传 query token（?t=...）；保留 XFO 不引入 frame-ancestors
```

局限性：单浏览器版本（Chromium 145 headless）；p5.js 真实加载与重绘负载未测（外置脚本机制已验）；data: 顶层页未测；top-navigation 未实测（沙箱无 allow-top-navigation，理论被挡）。

## 6. 弱模型上手机制

- **skill 式（主力，P0）**：角色卡/全局配置挂载「指令规范 + few-shot 示例库」，prompt 组装时按档位注入，规范+示例 ≤800 token，超预算降级裁剪（反例→正例→仅目录）；
- **MCP 式（P1）**：对支持 function calling 的端点暴露 `canvas_primitive`/`canvas_scene` 工具（注意：OpenAI function name 不允许点号，`canvas.primitive` 会被拒收）；**前置条件：`openai_like.py` 当前无 tools 能力**（grep 零匹配），需先给 `base.py` 端口加 `tools` 可选参 + 流式 delta.tool_calls 聚合，工作量不小于 parser 本身——故 P0 双通道不依赖它；
- 示例库：`data/canvas/example_packs/{l1,l2}.jsonl`，`pack_version` 单调递增可回钉；`source` 字段（curated/derived/generated）预留半自动转换；
- 实证依据：7B 模型 few-shot +20% 成功率；分隔符简单格式优于完整 JSON；校验+重试+降级纯文本不崩溃。

### 6.1 品味规范来源：GitHub skill 调研（2026-10-17，v6 抖音风被用户否决「唐」后）

**v6 尸检（为什么唐）**：违反 frontend-design SKILL.md 的核心纪律——「A single orchestrated moment lands better than scattered effects」（一次编排时刻胜过满天特效）：v6 四条线齐发（弹幕+大字+爱心+爆点），boldness 花完，无记忆点；且「抖音红+金+粗描边」正是该 skill 点名的「默认网红味」——defaults rather than choices。

**调研收获（GitHub 实证）**：

| Skill | 来源 | 核心可借鉴 |
|---|---|---|
| frontend-design | anthropics/skills | 品味总则：先定 token 系统再写码；**单编排时刻原则**；boldness spent in one place；「出门前摘掉一件配饰」（Chanel）；AI 味默认陷阱清单（米白底+陶土 accent / 近黑底+酸绿 / SaaS 卡片kit / 全大写 eyebrow / 等）；动效必须回答用户动作 |
| canvas-design | anthropics/skills | **设计哲学先行**：先给运动命名 + 4-6 段宣言，再视觉表达；「像博物馆展品一样被精心制作」的工艺感叙事（meticulously crafted / master-level）；极简文字作视觉重音；「refine what exists, don't add more graphics」 |
| algorithmic-art | anthropics/skills | p5.js 生成艺术：种子随机+流场+粒子；「从创意哲学出发而非模仿现有风格」 |
| theme-factory | anthropics/skills | 10 套预设主题——「a page with colors vs a page with a palette」 |
| animate-text | pixel-point/animate-text（145★） | **24 个文字动效 JSON 契约**：portable spec（语义意图）+ exact effect recipe（渲染算法/时序/播放）两层结构——正是 L1/L2 preset 格式的蓝图；效果族：soft-blur-in / typewriter / shared-axis / kinetic-center-build / mask-reveal |
| text-to-lottie | diffusionstudio/lottie（5.5k★） | SKILL.md 教 Lottie JSON 方言 + **本地 player 热修 harness**（agent 自验证输出）——我们的 canvas-spike 已是同模式，固化为 preset 创作流程；「Prioritize clean, intentional, professional motion over merely satisfying the literal prompt」 |
| p5js skill | moltis-org/moltis | 创意标准原文：「First-render excellence is non-negotiable」「Cohesive aesthetic over feature count——ten unrelated effects is worse than three that belong together」 |
| ascii-shader-tsx | Codeptor | 有边界的风格系统（9 艺术风格 × 8 抖动算法 × FX 预设）——风格空间受限而非自由发挥的正面案例 |

**对我们方案的三处落地**：
1. **L3 代码生成规范（skill 注入内容改写）**：注入块从「语法说明」升级为「画布哲学卡」——先要求模型输出：运动名 + 4-6 句视觉宣言 + 色板（4-6 个命名 hex）+ 字体角色 + **本回复唯一的一个编排时刻**，再生成代码；把 frontend-design 的单编排时刻原则 / remove-one-accessor / AI 味陷阱清单写进反例；
2. **L1/L2 preset 格式升级**：模板 JSON 改为 animate-text 式两层——`spec`（语义意图：何时用/什么情绪）+ `recipe`（精确时序/缓动/渲染参数），preset 数量贵精不贵多；
3. **preset 创作流程**：每个 preset 必须过「生成→预览→自批判→refine 不加量」循环（text-to-lottie harness 模式），未过自验证的 preset 不进库。

**待办→已出原型**：v7 三味型已按「单编排时刻」纪律出原型（2026-10-17，截图在 `canvas-spike/visual/V7*_closeup.png`，待用户选定）：
- **A 编辑感文字**：一句话的重量——细规展开 + 斜体衬线文字遮罩揭幕 + 哑金标点；暖白/灰紫/哑金三色；最贴合角色扮演产品（文字即媒介）；
- **B 生成艺术**：情绪流场——420 粒子沿双层正弦场漂移，靛蓝→玫紫，destination-out 拖尾；适合做 ambient 氛围档；
- **C 系统图表**：为情绪建档案——十字准线/圆/刻度/临床标签（EMO-07 / intensity 0.82 / decay t+1.4s）+ 单红点；canvas-design「虚构学科 diagram」路线，最独特但小众。
- **D 粒子语义场**（2026-10-17 晚用户定向：「用粒子拼接画面：字体、颜色、流动画面、块的流动，给人一种流动的感觉」）：**一种介质两种存在**——1500 粒子沿双层正弦流场游离（冷靛蓝低透明，destination-out 拖尾织出流动肌理）→ 被召唤时汇聚成形（暖玫金高亮）：拼字（离屏 canvas 采样「流动」字形取 850 目标点弹簧聚合）+ 块的流动（2 个矩形块，块内 7px 网格量化保轮廓，整体漂移）→ 解散回流场；色相随状态冷转暖渐变。四段时间线：0-2s 游离 / 2-3.9s 拼字 / 4.8-6.8s 块 / 之后回流。**四方向中唯一同时满足「字体+颜色+流动画面+块的流动」四要素**，且把讨论中 B「美但无语义」与 A「文字时刻」合成一个介质。截图 `canvas-spike/visual/V7D_*.png`，代码 VARIANT_D。工程注意：1500 粒子持续计费（需数量分档+查表色），拼字目标采样用离屏 getImageData。
- **E 数理曲线粒子**（2026-10-17 深夜用户定向，D 被批「太空了」后）：「粒子平常是正常的，通过具有美感的函数控制粒子的流动和颜色的变化，模拟海浪、花朵、玫瑰、爱心」+「正常的字体」。实现：**3240 粒子沿四族参数曲线同时流动，常态即完整画面**——海浪（6 条堆叠正弦线，粒子随波横流，青蓝色相沿 x 渐变）、爱心（心形线 x=16sin³t, y=13cos t−5cos2t−2cos3t−cos4t，三枚嵌套 + 呼吸缩放）、玫瑰（r=a·cos(kθ) 双环，k=3/5，慢旋 + 呼吸）、花朵（phyllotaxis 黄金角 137.5° 点阵，开合呼吸）；色相全部沿曲线参数/时间渐变；一句话用正常字体（15px 系统 sans）渲染于底部。参考：Bees & Bombs 距离延迟相位波、Math Curve Loaders（paidax01）18 曲线族。截图 `canvas-spike/visual/V7E_*.png`，代码 VARIANT_E。**这是目前唯一完全命中用户四要素（海浪/花朵/玫瑰/爱心 + 正常字体 + 常态完整）的方向**。v2 修缮（art-director 终审意见，已应用并重跑截图）：构图主次化（大爱心主角+双卫星、花朵上置、玫瑰右置，治四形缠结）、花朵呼吸改全局相位（治闪烁）、辉光 alpha 0.9→0.78 + 拖尾 0.13→0.16（治长时发雾）、字幕移出浪带。**艺术结论（art-director 终审，另两位终审待回）：E 主力（behind 层 ambient 常驻，情绪天气）+ A 特色档（front 层 burst，摘句编辑时刻，角色的话）——「天气不会失言，但产品不能只有天气」；E 的疲劳曲线是借来的（识别快感约 20 次耗尽），需形义映射（海浪=低落/爱心=心动/玫瑰=热烈/花朵=明快，对齐情绪七父类）+ 摘句寄生 + 形库轮换三机制才配常驻。**
五个原型的模型代码均在 `canvas-spike/visual/parent.js` 的 VARIANT_A/B/C/D/E（`?fx=a|b|c|d|e` 切换），可作为 L2 preset 首批候选。

## 7. 文件清单与任务分解

### 7.1 里程碑路线（对抗评审建议）

| 里程碑 | 内容 | 验证目标 |
|---|---|---|
| **M1** | L0 后端驱动氛围：配置+种子数据+解析校验纯逻辑+后端注入+前端画布渲染 | 零模型依赖跑通整条 SSE 画布管线；桌宠主力路径（`pet.js:780-784` 强制 ollama）直接受益 |
| M2 | 模型指令（L1/L2 in-band）：注入块+流式剥离+档位判定 | 弱模型格式合规率 ≥90%；跨 chunk 一致性回归 |
| M3 | L3 沙箱代码：middleware 覆盖表+沙箱页+校验器+回退链 | 恶意指令（fetch 外联/读 cookie/跳转）成功率 0；TTL 正常 |
| M4 | P1 增强：MCP 工具化（先改 provider）、桌宠完整化、请求级档位、p5 vendor | function calling 端点工具调用闭环 |
| P2 | 画布交互、示例库半自动转换、管理 UI | — |

### 7.2 任务清单（P0）

| ID | 名称 | 依赖 | 关键文件 |
|---|---|---|---|
| T01 | 基建：canvas 配置组 + 示例库/模板种子 + 契约冻结 + conftest 钉 `ROLEPLAY_CANVAS_ENABLED=false` | — | `config.py`、`core/canvas/__init__.py`、`models/chat.py`、`data/canvas/**`、`tests/conftest.py` |
| T02 | 协议纯逻辑：解析+校验+钳制+模板展开 | T01 | `core/canvas/{models,parser,validator,templates}.py` + 测试 |
| T03 | 后端接线：CanvasService 门面 + prompt 注入 + SSE 事件 + /canvas 路由 | T02 | `core/canvas/{service,prompting,examples}.py`、`orchestrator.py`、`api/chat.py`、`api/canvas.py`、`api/deps.py` |
| T04 | 前端：画布层 + 流式剥离 + L1/L2 渲染 | T01 | `js/canvas.js`、`js/canvas-primitives.js`、`js/canvas-scenes.js`、`chat.js`、`index.html`、`css/index.css` |
| T05 | 联调 + L3 沙箱 + 桌宠预留 | T03+T04 | `canvas-sandbox.html`、`js/canvas-sandbox.js`、`middleware.py`、`pet.html`、`desktop/src/main/control-server.js`、`tests/test_canvas_e2e.py` |

### 7.3 实现注意事项（spike/评审产出）

- 画布复用同一 PIXI Application 的 container，**不新建 canvas**（同页双 WebGL 上下文风险）；桌宠页是另一套路径（Spine 挂 DOM 容器 `pet.js:332`），两条路径分别测；
- 新画布元素 id 避开 `#pet-canvas`（`pet.html:46` 已被占用）；
- 与既有常驻暴雨层（`index.html:16` + rain.js）定义 z 序表，L0 映射避开同型 preset 或支持「增强既有层」模式；
- 继承 rain.js:11 的 `prefers-reduced-motion` 纪律；
- 桌宠档复用 `config.js:25` 已有 S/M/L 尺寸档算预算，不建第二套配置体系；
- 前端新文件一律外置脚本（CSP 合规），与 rain.js/llm-switch.js 同风格。

## 8. 验收标准

1. 画布层 `pointer-events:none`，主体交互命中测试 100% 无遮挡回归；
2. M1：后端注入的画布事件先于首个 chunk 到达（P95）；未开启 canvas 时页面零变化、既有 1465 测试零回归；
3. M2：指令随 chunk 到达 → 画面 ≤100ms（P95）；弱模型格式合规率 ≥90%；非法指令 100% 拦截且文本流零影响；
4. M3：恶意指令成功率 0；沙箱启动到首帧 ≤1.5s；任意档位失败对话主链路可用性 100%；
5. 性能：burst 200 粒子下桌宠 ≥30fps、呈现页 ≥60fps；不达标自适应降元素；
6. 人工 UX 验收清单（含对抗用例）：畸形指令时文本不乱、弱模型连发时预算拦截无可见错误、冷却/去重期内连发排队行为、桌宠 front 不挡脸、刷新后状态重置、reduced-motion 降级、后端 L0 与模型 in-band 同氛围 5s 内不双闪现。

## 9. 决策记录（2026-10-17 主理人代决，用户授权「接手处理」）

原 9 项待确认问题**已按推荐默认值锁定**，均可低成本回滚（见表内备注）。如需变更，改配置或对应任务即可，不必推翻架构。

| # | 问题 | 锁定值 | 回滚成本 |
|---|---|---|---|
| 1 | 画布交互性 | 纯表现层，交互留 P2 | 一行 CSS + opts 开关 |
| 2 | 渲染实现 | 独立 2D canvas（复用 PIXI Application container 的技术点以 7.3 为准） | 低（渲染层独立） |
| 3 | L3 沙箱形态 | iframe 专用路由（spike 13/13 GO + 视觉验证通过） | 低（备选 Worker 方案已记录） |
| 4 | 档位判定 | model_id 静态映射（`canvas_model_tiers` glob） | 低（P1 留请求级覆盖字段） |
| 5 | 桌宠范围 | P0 仅 Web，接口预留复用 | 低（control-server 加路由即可） |
| 6 | 示例库种子 | 用户+强模型辅助+人工筛选；preset 种子同笔投入 | 低（JSONL 可迭代） |
| 7 | 指令位置 | in-band 为主 + SSE 事件为辅 | 中（双通道已设计，切换成本可控） |
| 8 | 第一里程碑 | **M1 = L0 后端驱动氛围**（已锁定） | 低（里程碑可并行调整） |
| 9 | L0+ 情绪氛围联动 | 并入 M1（sad→雨/excited→花瓣，后端触发不占模型预算） | 低（preset 开关） |
| 10 | 视觉语言定向（三人终审已收敛，2026-10-17） | **E 数理曲线粒子放行主力**。三票：art-director「E 主力（behind ambient 常驻=情绪天气）+ A 特色档（front burst 摘句=角色的话）+ C 退役（静态降级帧）+ B 砍」；product-judge 批准组合（「E 单飞=更漂亮的 B」），**M1 收缩为 E-lite（海浪+爱心两形+底部摘句+静态降级帧+fps governor）**；sys-judge 工程放行带两硬条件：**(a) 桌宠 fps 实测过 30fps 门（不过线走设计内降级链：优化→S 档密度→burst 化，不推翻方向）；(b) 三角函数/合批优化 + S 档密度进上线包，非后续项** | 低（preset 风格目录可扩展） |

**最终视觉定稿（v3 渲染 + 三票合一）**：E 数理曲线粒子——3210 颗粒子沿四族参数曲线（海浪/心形线/玫瑰线/黄金角）**弥散成独立辉光点云**（每粒子绕曲线高斯散开 ±8.5px + 预渲染径向辉光精灵 + 独立闪烁相位），常态即完整画面，底部正常字体摘句。**M1 = E-lite**（海浪+爱心两形 + 后端摘句 + 静态降级帧 + governor + ducking + reduced-motion + DPR 分档 + 桌宠 fps bench spike 放行门）；**M2 = 四形花园 + 形库轮换 + 强度耦合 + A 完整编辑 burst + persona 色调**。疲劳三机制（product-judge 优先级）：① 强度耦合（同形参数随 emotion score 连续变化）② 摘句寄生（唯一无限 novelty 通道，保守摘句：末句/≤40 字/摘不到静默）③ 形义映射（仅 valence 四情绪：海浪=低落/爱心=心动/玫瑰=热烈/花朵=明快，放弃 angry/anxious/fear/surprise 不硬凑）。工程红利（sys-judge）：E 无状态参数化 → 常驻无漂移、CI 黄金帧可测、resize 近零成本、burst 化包络近零成本。

**视觉定稿**：待 v7 重定（方向：单编排时刻 + 编辑感动效语法，见 §6.1）。用户明确的审美口径：要高饱和、有节拍、有「特效感」的事件型画面，不要氛围型慢飘，**更不要元素堆砌的土味**（v6 教训）。

## 10. Spike 证据索引

- 解析器口径：`canvas-spike/parser/`（87/87，REPORT.md + summary.json；复现 `python fixtures.py && node tests.js && python run_tests.py`）
- 沙箱实测：`canvas-spike/sandbox/evidence/`（13/13，report.md + results.json + console_log.txt + headers.txt；复现 `cd canvas-spike/sandbox && python run_tests.py`）
- 以上均在 `C:/Users/Lenovo/WorkBuddy/2026-10-15-08-37-59/canvas-spike/`，未碰项目文件。
