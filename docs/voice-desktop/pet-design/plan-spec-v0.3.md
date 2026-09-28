# 桌面宠物 v0.3 呈现层 · 工程实施方案（plan-spec-v0.3）

> 状态：**实施方案（待评审 / 可直接指导实施）** —— 只做计划，不改代码。
> 依据：`$ROOT\docs\design\pet-presentation-spec-v0.3.md`（呈现层规范 v0.3）、
> `$ROOT\docs\design\pet-visual-styleboard-v0.3.md`（视觉风格板 v0.3）。
> 对照基线：真实代码现状（`frontend/pet.html`、`frontend/js/pet.js`、`frontend/js/live2d.js`、`desktop/src/main/*`、`desktop/src/preload/pet.js`）。
> 仓库根（下文统一简写 `$ROOT`）：`C:\Users\Lenovo\WorkBuddy\2026-07-27-16-45-03\roleplay-ai`
> 素材库根（下文简写 `$SRC`）：`C:\Users\Lenovo\WorkBuddy\2026-07-26-22-28-10`

> ⚠️ 本文档使用 `$ROOT` / `$SRC` 简写仅出现在本导读与表头，正文所有「涉及文件」一律给绝对路径。

---

## 0. 关键结论速览（实施前必读）

1. **默认形态切换是"先建后切"**：当前 `pet.html` 只加载 Live2D 运行时、`pet.js` 默认走 `RoleplayLive2D`。P0 需先落位 Spine 素材 + 新增 `spine.js`（SpinePet 适配器），再在 `pet.js` 引入「渲染器路由」，把默认渲染器切到 Spine，Live2D 降级为设置里的"对话模式"。切换即销毁旧渲染器，避免双 WebGL 上下文并存。
2. **规范存在 3 处内部/跨文档冲突，实施前需定稿**（详见 §6.1 风险 R3/R4/R5）：勿扰透明度 0.45 vs 0.55；Spine 动画命名风格板 `bm_hy*/zm_*` vs 呈现规范 `x_ls_*/target/djc*`；默认窗口 320×420（规范）vs `config.js` 现状 420×560。
3. **P0 首日的动画巡检页是全局前置依赖**：所有动作映射（待机/行走/情绪/睡眠）都建立在"30+ 动画名 → 语义"回填表之上；语义表落盘为 `frontend/assets/spine/animation_map.json`。
4. **主进程改动最小化**：锁位/勿扰/多屏摆位/缩放 IPC 全部收敛在 `index.js`（注册）+ `windows.js`（moveBy 守卫 + setSize/moveToDisplay）+ `config.js`（新默认字段）+ `preload/pet.js`（白名单新方法）四处；`physics.js` 已天然多屏感知，`ocr.js` 已具备三档，无需大改。

---

## 1. 规范要点提取

### 1.1 组件清单（7 组件）

| # | 组件 | DOM 锚点 | 用途 | 关键视觉约束（引用风格板 token） |
|---|---|---|---|---|
| 1 | 气泡 | `#pet-bubble` | 对话/OCR/引导的唯一文字出口 | max-width 92%（风格板 §7.1 写 88%，见 R4）；字号 `--fs-bubble`；尾巴指向头顶；打字机光标 `│` 530ms steps(1) 闪烁；完成后操作行「上一句/下一句/复制/朗读/✕」 |
| 2 | 品牌条 | `#pet-brand` | 身份表达 | 左上角极细一行「**无名者** · 桌面宠物」，`pointer-events:none` 永远穿透，z-index 5 |
| 3 | 状态 chip | `#pet-status .chip` | 诊断条（替换 7×7 灰点） | 高 20px，6px 圆点 + 文字；S 档收起为圆点+计数，M/L 档显文字；四枚：后端 / Ollama / 录音 / 勿扰（勿扰仅开启时显示） |
| 4 | 右键菜单 | `#pet-menu` | 全部主动作入口 | min-width 172px；三组（互动/感知/系统）；16px SVG 描边图标；组间 1px 分隔线；贴边翻转 |
| 5 | 设置抽屉 | `#pet-settings` | 唯一配置入口 | 全窗覆盖层；顶部 tab 条 32px；五 tab 卡片化；控件 28px 高；range 右侧实时数值 |
| 6 | 输入条 | `#pet-inputbar` | 桌面端文字入口 | 高 36px；折叠态右下 32px 圆钮 ✎；展开态发送钮 32×32 方形 + 语音切换钮 |
| 7 | 引导滑层 | `#pet-onboarding`（新增） | 首次启动教会 5 操作 | 全窗 backdrop + 居中卡片 260px；步骤点 ●●○○○；「上一步/下一步/跳过」 |

### 1.2 九态状态机（含勿扰/锁位正交修饰态）

主状态 6 个：**闲置 / 漫步 / 拖拽 / 聆听 / 思考 / 说话**；修饰态 2 个：**勿扰 / 锁位**（与主状态正交叠加）；子状态 1 个：**睡眠**（闲置的子状态，90s/5min 分级）。共 9 态。

| 状态 | 动画 | 装饰 | chip | 透明度 | 声音 |
|---|---|---|---|---|---|
| 闲置 | `jinxian` 待机池 | 无 | 常态 | 1.0 | 无 |
| 漫步 | `target` 行走 + 窗口 lerp | 无 | 常态 | 1.0 | 无 |
| 拖拽 | 待机悬停帧 | 光标 grabbing | 常态 | 1.0 | 无 |
| 聆听 | 待机减速 50% | 录音 chip 呼吸 | 录音=accent | 1.0 | 无 |
| 思考 | 待机微动 | 气泡打字中 `▍` | 常态 | 1.0 | 无 |
| 说话 | 待机微动 | 气泡尾巴摆动 | 常态 | 1.0 | TTS |
| 勿扰 | 待机呼吸减半 | 勿扰 chip | accent 呼吸 | **0.55** | **禁** |
| 锁位 | 同闲置 | 小锁图标 / 虚线框 | 常态 | 1.0 | 同当前态 |
| 睡眠 | `he_shang→he_di` | 可选 "Zzz" | 常态 | 0.7 | 无 |

**勿扰（修饰态）确切行为参数**：
- 透明度降至 **0.55**（风格板 §7.7 / Rev1 修订值；规范 §6.2 与 §11 仍写 0.45，属陈旧，见 R3）。
- 待机呼吸动效幅度减半；禁 TTS 发声；漫步暂停（主进程 walker 停）。
- 勿扰中收到对话请求：只显气泡、不发声。
- 右上角浮现"勿扰" chip（accent 呼吸）；可选"30 分钟后自动解除"。
- 菜单顶部插入提示项「勿扰中 · 点击解除」（点击即解除，风格板 §7.7）。

**锁位（修饰态）确切行为参数**：
- 拖拽手势失效（光标不变 grab）；拖拽尝试 → 光标 `not-allowed` + 虚线框闪烁一次。
- 状态区追加锁位 chip：12×12 锁形 SVG（`--accent`）+ 文字"已锁位"。
- 锁定中拖拽尝试 → 人偶播 `djc1` 摇头 + toast「已锁定，长按 1.5s 解锁」。
- 长按人偶 1.5s 直接解锁（防"锁死找不到开关"）。
- 视觉：窗口内边距 `--space-2` 处绘制 1px `dashed var(--line-strong)` 矩形框，8s 周期缓慢流动（`prefers-reduced-motion` 静止，风格板 §7.8）。

**互斥规则**（沿用 v0.2）：拖拽/漫步互斥；对话与录音期间暂停漫步调度。

### 1.3 新手引导 5 步内容

容器（§4.6）：全窗 backdrop `rgba(0,0,0,.55)`（风格板 §7.6 写 `rgba(8,10,14,0.72)`，见 R4）+ 居中卡片 260px + 顶部步骤点 + 底部「上一步/下一步/跳过」。每步 = 标题 + 描述 + 左侧 200×140 配图占位槽（虚线框）。

| 步 | 标题 | 文案 | 配图 |
|---|---|---|---|
| 1 | 拖我移动 | 按住我，拖到桌面任何角落。 | 拖拽手势示意 |
| 2 | 右键看菜单 | 右键点我，说话、动作、识别屏幕都在这里。 | 右键菜单示意 |
| 3 | 按住 Alt+Space 说话 | 按住快捷键，直接对我讲话。 | 快捷键示意（浏览器降级模式替换为「点底部 ✎ 打字」） |
| 4 | 识别屏幕 | 我可以看一眼你的屏幕，聊聊你在做什么。全程本地，不落盘。 | 屏幕识别示意 |
| 5 | 设置抽屉 | 模型、声音、漫步频率，都在设置里。祝你与无名者相处愉快。 | 设置抽屉示意 |

触发：`localStorage roleplay_pet_state.onboarded === false` 时入场动画结束后自动弹出；完成/跳过写 `onboarded=true`；设置「桌面端」tab 提供"重看引导"。

### 1.4 Spine 人偶定位规则（§2.3 + 风格板 §8.2）

- **水平居中**；**垂直居中偏下**。
- **头顶留白 = 窗口高 × 8%**（420 高下 ≈ 33px），是硬约束，不允许模型顶到窗口上沿（气泡悬浮区）。
- **脚底落地线 = 窗口下沿 − 16px**（给输入条折叠态留悬浮空间）。
- 行走时 `flipX`（`scaleX` 镜像）控制方向，水平位置不位移；翻转过渡 ≤ 100ms。
- **缩放公式**：`scale = min(舞台可用高 / 骨骼自然高) × 0.92`，初始化与 resize 时各算一次；用户缩放叠加其上（滚轮 0.5×~1.5× 步进 0.05；风格板 §8.3 写可调范围 0.7~1.4，见 R4）。
- 模型包围盒与窗口左右边距各 ≥ 12px，超出时自动缩放回最大适配值。

### 1.5 窗口三档断点 S/M/L（§2.3 / §3.3）

| 档位 | 窗口尺寸 | 顶栏 chip | 气泡最大行数 | 输入条 | 适用 |
|---|---|---|---|---|---|
| **S（默认）** | **320×420** | 收起为圆点+计数 | 3 行 | 折叠圆钮 | 日常陪伴 |
| M | 420×560 | 横排展开文字 | 4 行 | 折叠可展开 | 均衡 |
| L | 480×640（上限） | 竖排全文字 | 4 行 + 翻页 | 常驻展开可选 | 对话模式/Live2D |

- 断点按**窗口宽**取档：`<380=S`，`380~460=M`，`>460=L`。
- Live2D 对话模式强制 `≥420×560`（即 M/L）。
- 拖拽缩放经主进程 resize IPC，渲染层 `ResizeObserver` 触发 §1.4 重算。
- ⚠️ 现状 `config.js` 默认 `pet.width=420 / height=560`（M 档），与规范"默认 320×420"不符，见 R5。

---

## 2. 分期实施方案 P0 / P1 / P2

分期以规范 §10 为准（对应审查项：P0 = P0-1~4 + P1-1；P1 = P1-2~6 + P2-13；P2 = P2-1/2/5/9/10 + P2-14/15/16/20）。

### 2.1 P0 · 必做（Spine 接通 + 基础组件）

#### P0-1 素材落位 + 运行时引入
- 【涉及文件】新增 `$ROOT\frontend\assets\spine\314701_wmz_s_room.skel`、`...\314701_wmz_s.atlas`、`...\314701_wmz_s.png`、`...\314701_wmz_s_bloom.png`（自 `$SRC\viewer-data\03_动态资源\Spine战斗\Spine战斗_314701_简化版\` 复制，不改名）；新增 `$ROOT\frontend\assets\lib\spine-core.js`、`...\spine-pixi.js`（主方案运行时）、`...\spine-player.js`（自 `$SRC\viewer\lib\spine-player.js` 复制的降级运行时）；修改 `$ROOT\frontend\pet.html`（script 引入）。
- 【改动内容】复制 4 个素材文件到 `frontend/assets/spine/`；引入 spine 运行时并排在 `pixi.min.js` 之后（加载顺序见 §4.2）。
- 【依赖前置】无。
- 【验收标准】`pet.html` 加载后 `window.PIXI.spine`（主方案）或 `window.spine`/`SpinePlayer`（降级）可用；`frontend/assets/spine/` 四文件存在且 atlas 内引用名与 png 文件名一致。

#### P0-2 Spine 渲染器（SpinePet 适配器）
- 【涉及文件】新增 `$ROOT\frontend\js\spine.js`；修改 `$ROOT\frontend\js\pet.js`（渲染器路由，见 §4.3）。
- 【改动内容】实现 `window.RoleplaySpine`：加载 skel → `SpinePet` 实例；提供 `walk / idle / emotion / click / sleep / setZoom / setVisible / setFlip` 统一行为接口；实现 §1.4 定位（头顶 8% / 落地线 −16px / `min(可用高/骨骼自然高)×0.92`）；`ResizeObserver` 重算。
- 【依赖前置】P0-1。
- 【验收标准】320×420 下人偶头/肩/手完整可见，头顶留白 ≈8%，脚底贴落地线（下沿 −16px）；resize 到 420×560 / 480×640 后重算正确。

#### P0-3 动画巡检页 + 语义表回填
- 【涉及文件】新增 `$ROOT\frontend\pet-inspect.html`、`$ROOT\frontend\js\pet-inspect.js`（临时页）；新增 `$ROOT\frontend\assets\spine\animation_map.json`（回填产物）。
- 【改动内容】临时页下拉选动画名 + 播放 + flipX + 循环 + 0.5×/2× 速度；枚举 skel 全部动画名；半小时内实播 30+ 动画，确认语义后回填 `animation_map.json`（含 `target/djc/hua/bian/cs2/cx*/x_ls_*` 与风格板 `bm_hy*/cm_hy*/zm_*` 的对照，消解命名冲突 R4）。
- 【依赖前置】P0-1。
- 【验收标准】`animation_map.json` 覆盖全部动画名，含 `{name, slot, semantics, confidence}`；文档 §2.1 语义表回填完成。

#### P0-4 三档布局 + 居中偏下定位
- 【涉及文件】修改 `$ROOT\frontend\pet.html`（布局 CSS）、`$ROOT\frontend\js\spine.js`（定位）、`$ROOT\frontend\js\pet.js`（断点判定）。
- 【改动内容】实现 S/M/L 三档：`<380=S / 380~460=M / >460=L`；chip 收起/展开/竖排三态；气泡 3/4/4+翻页 行数；输入条折叠/常驻展开；`ResizeObserver` 驱动重算。
- 【依赖前置】P0-2。
- 【验收标准】三档切换后组件状态正确；宽度断点边界 380/460 处无闪烁。

#### P0-5 品牌条 + 四枚状态 chip 升级
- 【涉及文件】修改 `$ROOT\frontend\pet.html`（chip DOM）、`$ROOT\frontend\js\pet.js`（`setDot` 逻辑、新增勿扰 chip、tooltip）。
- 【改动内容】品牌条沿用现有 `#pet-brand`；把现有 3 枚 chip（后端/Ollama/录音）升级为 20px 胶囊 + 6px 圆点 + 文字，新增"勿扰" chip（仅开启时显示）；S 档收起为圆点+异常计数；悬停 tooltip 完整诊断，异常 chip 可点击重试。
- 【依赖前置】无（可并行）。
- 【验收标准】chip 高度 20px、文字 `--fs-chip`；悬停有 tooltip；异常 chip 点击触发重试（Ollama 走 `/api/llm/ollama/models`）。

#### P0-6 输入条（折叠圆钮 + 展开 + Ctrl+Enter）
- 【涉及文件】修改 `$ROOT\frontend\pet.html`（输入条 DOM + 折叠圆钮）、`$ROOT\frontend\js\pet.js`（`openInputBar/closeInputBar/submitInput` 扩展、快捷键）。
- 【改动内容】折叠态右下 32px 圆钮 ✎；展开态 36px 输入框 + 32×32 发送钮 + 语音切换钮；`Ctrl+Enter` 展开并聚焦；`Esc` 收起；发送后 8s 无操作自动收起；流式期间发送钮转 loading。
- 【依赖前置】无（可并行）。
- 【验收标准】菜单/圆钮/Ctrl+Enter 三入口展开；Enter 发送走 `RoleplayChat.send` 完整 SSE 管线；Esc 收起。

#### P0-7 新手引导滑层（五步）
- 【涉及文件】修改 `$ROOT\frontend\pet.html`（新增 `#pet-onboarding` 容器 + CSS）、`$ROOT\frontend\js\pet.js`（替换现有气泡式 `startOnboarding`，五步状态机 + 跳过/重看）。
- 【改动内容】五步卡片（标题/描述/200×140 配图占位槽/步骤点/上一步/下一步/跳过）；`onboarded=false` 入场动画后弹出；完成/跳过写 `onboarded=true`；设置「桌面端」tab 加"重看引导"。
- 【依赖前置】无（可并行，但需 P0-6 的输入条锚点供步骤 3 降级文案）。
- 【验收标准】五步可逐步/跳过；关闭后 localStorage 标记生效；设置中可重看。

#### P0-8 气泡基础（打字机/超时/关闭）
- 【涉及文件】修改 `$ROOT\frontend\pet.html`（气泡 CSS + `aria-live`）、`$ROOT\frontend\js\pet.js`（`showBubble/appendBubbleText/hideBubble` 增强）。
- 【改动内容】流式打字机逐字追加 + 光标 `│` 闪烁；完成 4~9s（2200+90ms/字，上限 9000）淡出；`Esc`/点击空白/✕ 关闭；`role="status" aria-live="polite"`；位置翻转（头顶空间不足时翻到下方，尾巴始终指向头顶）。
- 【依赖前置】无（可并行）。
- 【验收标准】流式打字机正确；超时/关闭正确；翻转时尾巴方向正确。

#### P0-9 默认渲染器切换 Spine（路由收口）
- 【涉及文件】修改 `$ROOT\frontend\js\pet.js`（`initLive2D` → `initRenderer` 路由）、`$ROOT\frontend\pet.html`（加载顺序）。
- 【改动内容】默认走 `RoleplaySpine`；`renderer: "spine"` 默认值；设置切换模型时销毁旧渲染器再建新渲染器（避免双 WebGL 上下文）；Live2D 成为设置"对话模式"选项。
- 【依赖前置】P0-1~P0-8。
- 【验收标准】默认启动即 Spine 人偶；设置切 Live2D 后 ≥420×560 大模型完整可见；来回切换无上下文泄漏。

### 2.2 P1 · 强化

#### P1-1 右键菜单分组 + SVG 图标
- 【涉及文件】修改 `$ROOT\frontend\pet.html`（菜单三组 DOM + SVG 图标）、新增 `$ROOT\frontend\assets\icons\*.svg`（风格板 §9 清单）、修改 `$ROOT\frontend\js\pet.js`（`handleMenuAction` 扩展、键盘 ↑↓+Enter、贴边翻转沿用）。
- 【改动内容】三组：互动（说话/打字聊天/随机动作/语音对话）· 感知（识别屏幕/切换模型）· 系统（勿扰/锁位/静音/设置/退出 danger）；emoji 全换 16px SVG 描边图标；min-width 168px→172px；快捷键 hint 灰小字；`role="menu"/menuitem`。
- 【依赖前置】P0 收口。
- 【验收标准】三组分组、无 emoji、图标描边 `--accent`；贴边翻转正确；↑↓+Enter 可达。

#### P1-2 设置抽屉五 tab 全量
- 【涉及文件】修改 `$ROOT\frontend\pet.html`（tab bar + 卡片化 CSS）、`$ROOT\frontend\js\pet.js`（`renderSettings` 重写为五 tab + 持久化分流）、修改 `$ROOT\desktop\src\preload\pet.js`（如需写 config 走 `setConfig`）。
- 【改动内容】五 tab：模型（渲染器/缩放/入场动画开关）· 对话（Ollama 模型/地址/温度/自动朗读/闲话来言）· 语音（音色/语速/音量，读写 `roleplay_voice_state` 与主页共享/按住说话键）· 屏幕识别（触发档位/关键词 chip 编辑器/OCR 语言/节流）· 桌面端（窗口档位 S/M/L/置顶层级/漫步频率/锁位/多显示器摆位/重置位置/恢复默认）；控件 28px 高、range 右侧数值；「已生效 ✓」1.5s 微提示。
- 【依赖前置】P0、P1-1（菜单设置入口）。
- 【验收标准】五 tab 全部可改可存；LLM/语音进 localStorage，桌面端项经 `petApi.setConfig` 写 `config.json` 重启生效。

#### P1-3 勿扰模式
- 【涉及文件】修改 `$ROOT\frontend\js\pet.js`（DND 状态 + 渲染表现）、`$ROOT\desktop\src\main\config.js`（`pet.dnd` 默认字段）、`$ROOT\desktop\src\main\index.js`（IPC + walker 联动）、`$ROOT\desktop\src\preload\pet.js`（`setDnd`）、`$ROOT\frontend\pet.html`（勿扰 chip + 菜单提示项）。
- 【改动内容】透明度 0.55、呼吸减半、禁 TTS、漫步暂停（主进程 walker.pause）、勿扰 chip 浮现、菜单顶部「勿扰中 · 点击解除」、可选 30min 自动解除。
- 【依赖前置】P0、P1-2。
- 【验收标准】透明度 0.55、禁声、漫步暂停、chip 浮现；菜单一键解除；可选自动解除计时生效。

#### P1-4 锁位模式
- 【涉及文件】修改 `$ROOT\desktop\src\main\config.js`（`pet.locked`）、`$ROOT\desktop\src\main\windows.js`（`moveBy` 守卫）、`$ROOT\desktop\src\main\index.js`（IPC `pet:locked`）、`$ROOT\desktop\src\preload\pet.js`（`setLocked`）、`$ROOT\frontend\js\pet.js`（长按 1.5s 解锁 + 拖拽尝试反馈 + 锁位 chip）、`$ROOT\frontend\pet.html`（虚线框 + 锁位 chip）。
- 【改动内容】锁定时 `moveBy` no-op；拖拽尝试播 `djc1` 摇头 + toast「已锁定，长按 1.5s 解锁」；长按人偶 1.5s 解锁；锁位 chip（12×12 锁形 + "已锁位"）；窗口内边距虚线框 8s 流动。
- 【依赖前置】P0、P1-3。
- 【验收标准】锁定时拖拽窗口不移动；长按 1.5s 解锁；虚线框 + chip 显示正确。

#### P1-5 状态机完整实现（含睡眠序列）
- 【涉及文件】修改 `$ROOT\frontend\js\pet.js`（集中状态机替换零散状态）、`$ROOT\frontend\js\spine.js`（睡眠三段 `he_shang→he_di→deng` 与待机池）。
- 【改动内容】按 §1.2 九态实现：漫步调度（`target` 行走 + 窗口 lerp）、聆听（待机减速 50% + 麦克风 chip）、思考/说话（打字机/尾巴摆动）、睡眠（90s/5min 分级 + 透明度 0.7 + 唤醒 `deng`）；修饰态正交叠加；互斥规则（拖拽/漫步互斥，对话/录音暂停漫步）。
- 【依赖前置】P0、P1-3/P1-4。
- 【验收标准】九态视觉与 §1.2 一致；修饰态可正交叠加（如"勿扰+漫步"仍 0.55 + 禁声 + 漫步动画）。

#### P1-6 OCR 摘要气泡 + 三档节流
- 【涉及文件】修改 `$ROOT\frontend\js\pet.js`（`onScreenText` 处理）、`$ROOT\desktop\src\main\ocr.js`（关键词/定时节流微调，已有）、`$ROOT\desktop\src\main\config.js`（`ocr` 默认已齐）。
- 【改动内容】OCR 结果 → 气泡首句摘要 + 「详细」折叠；三档触发（手动 ≥2s / 关键词 ≥30s / 定时 ≥60s）沿用现有 `ocr.js` 结构，补关键词编辑器回写 config。
- 【依赖前置】P0、P1-2（屏幕识别 tab）。
- 【验收标准】气泡显首句摘要 + 「详细」折叠；三档节流生效；零落盘。

#### P1-7 多屏摆位
- 【涉及文件】修改 `$ROOT\desktop\src\main\windows.js`（`moveToDisplay` / `defaultPosition` 按显示器）、`$ROOT\desktop\src\main\index.js`（IPC）、`$ROOT\desktop\src\preload\pet.js`（`getDisplays/moveToDisplay`）。
- 【改动内容】用 Electron `screen` API 枚举显示器；设置「桌面端」tab 选主屏/副屏/指定坐标；副屏断开自动回主屏原位（Q3 取前者）。
- 【依赖前置】P0、P1-2。
- 【验收标准】三档摆位可用；副屏断开回主屏；坐标不外传。

#### P1-8 快捷键提示
- 【涉及文件】修改 `$ROOT\frontend\js\pet.js`（`?` 帮助气泡 + `Alt+Space` 提示）、`$ROOT\desktop\src\main\index.js`（`globalShortcut` 已注册）。
- 【改动内容】`?` 弹快捷键一览气泡；菜单项快捷键 hint；按住说话键可改（写 config）。
- 【依赖前置】P1-1。
- 【验收标准】`?` 弹帮助气泡；菜单 hint 正确；改键后 `registerPtt` 生效。

### 2.3 P2 · 打磨

| 任务 | 涉及文件 | 改动内容 | 依赖 | 验收标准 |
|---|---|---|---|---|
| P2-1 入场动画 | `spine.js` + `pet.js` + `pet.html` | `cs2`（⚠️待巡检确认）入场 + 窗口淡入 `opacity 0→1 scale 0.96→1.0` `--dur-xslow`；`prefers-reduced-motion` 改淡入 | P0 | 启动即播入场，降级模式改淡入 |
| P2-2 底栏控制条 | `pet.html` + `pet.js` | 底部常驻控制条（缩放/静音/勿扰/锁位快捷） | P0/P1 | 控制条可用，S 档隐藏 |
| P2-3 气泡操作行 | `pet.html` + `pet.js` | 复制/朗读/上一句/下一句/✕；历史翻页维护最近 20 条；`↑/↓` 翻页 | P0-8 | 操作行各按钮生效，历史翻页正确 |
| P2-4 跟随光标/活动窗口 | `desktop/src/main/*` + `pet.js` | 宠物可跟随光标或活动窗口 | P1 | 跟随模式可选、可关 |
| P2-5 主聊天页宠物预览卡 | 网页版 `index.html` 侧 | 主聊天页嵌入宠物预览卡 | P0 | 预览卡显示 Spine 缩略 |
| P2-6 截图分享 | `pet.js` + `desktop`（导出） | 合成"人偶+气泡"PNG，仅用户点导出后经系统保存对话框落盘 | P1 | 合成零落盘，导出需用户确认对话框 |

---

## 3. 代码差距分析

### 3.1 已具备（可直接沿用）

| 现状 | 位置 | 说明 |
|---|---|---|
| 品牌条 | `$ROOT\frontend\pet.html` `#pet-brand` | 已有一版，P0-5 沿用（微调 letter-spacing 0.22em→token） |
| 气泡基础 | `pet.js` `showBubble/appendBubbleText/hideBubble` + `pet.html` `#pet-bubble` | 已有 show/hide/超时(2200+90ms/字)，P0-8 在其上加打字机/操作行/aria |
| 状态 chip 骨架 | `pet.html` `#pet-status .chip`（后端/Ollama/录音）+ `pet.js` `setDot` + `checkBackend/checkOllama` | 已有三枚，但尺寸 10px/圆点 6px 需按 §7.4 升到 20px 高，加勿扰 chip |
| 右键菜单骨架 | `pet.html` `#pet-menu` + `pet.js` `openMenu/closeMenu/handleMenuAction` | 已有（贴边翻转），但 emoji 图标、min-width 168px、未分组、缺勿扰/锁位/切换模型项 |
| 设置抽屉骨架 | `pet.html` `#pet-settings` + `pet.js` `renderSettings`（7 行单页） | 已有单页 7 行，P1-2 需改五 tab 卡片化 |
| 输入条骨架 | `pet.html` `#pet-inputbar` + `pet.js` `openInputBar/closeInputBar/submitInput` | 已有展开/收起/Enter 发送，缺折叠圆钮/Ctrl+Enter/语音切换钮/8s 自动收起 |
| 对话链路 | `pet.js` `send()` → `RoleplayChat.send`（SSE，llmOverride 强制本地 Ollama） | 完整复用，无需改 |
| OCR 钩子 | `pet.js` `onScreenText` + `desktop/src/main/ocr.js`（三档） | 已具备手动/关键词/定时，P1-6 只需首句摘要+详细折叠 + 关键词编辑器 |
| 语音钩子 | `pet.js` `onPtt/onTalk` + `voice.js` | 已具备按住说话/网页让宠物说话 |
| 命中穿透 | `pet.js` `hitTest/computeInteractive/isOverInteractiveDom` + 50ms 去抖 | 已具备，需把 onboarding/settings 纳入 openEls，包围盒内缩 12%/6% 换精确 hitTest（P2 可选） |
| 拖拽桥 | `pet.js` `live2d:drag/dragend` → `api.moveBy/dragEnd` | 已具备，锁位时需守卫 |
| 漫步 | `desktop/src/main/behavior.js` `createWalker` + `pet.js` `onWalk` | 已具备，Spine 接入后替换 `WALK_MOTIONS` 为 `target*` |
| 物理 | `desktop/src/main/physics.js` | 已具备动量/回弹，`clampPosition` 用 `getDisplayNearestPoint` 已多屏感知 |
| 配置 | `desktop/src/main/config.js` `loadConfig/saveConfig`（原子写）+ `preload/pet.js` `getConfig/setConfig` | 已具备，P1 需加 `pet.locked/dnd/sizeTier/screenId` 默认字段 |
| Live2D 宠物分支 | `frontend/js/live2d.js` `fixedModel` + `_fitPet` | 已具备（对话模式沿用）；`_fitPet` 当前 topZone=min(110,h*0.2)/bottomMargin=12 与 §1.4（8%/16px）不一致，P0 需对齐或由 Spine 渲染器单独实现 |

### 3.2 需修改

| 文件（绝对路径） | 差距 | 规范要求 |
|---|---|---|
| `$ROOT\frontend\pet.html` | `:root` 只有 8 个 token（缺 `--fg-faint/--warn/--accent-glow/--line-strong/--font-mono/--fs-*` 等） | 全量引用风格板 §11 token 清单 |
| `$ROOT\frontend\pet.html` | `#pet-settings` 单页无 tab、无卡片化 | 五 tab + 卡片化 + 顶部 tab 条 32px |
| `$ROOT\frontend\pet.html` | `#pet-menu` emoji 图标、min-width 168px、未分三组 | SVG 图标、172px、三组 + 勿扰/锁位/切换模型 |
| `$ROOT\frontend\pet.html` | 无 `#pet-onboarding`（引导目前是 pet.js 里气泡式 4 行） | 五步滑层卡片 |
| `$ROOT\frontend\pet.html` | 无勿扰 chip / 锁位 chip / 虚线框 DOM | 新增三件 |
| `$ROOT\frontend\pet.html` | script 顺序无 spine 运行时 | 插入 spine-core/spine-pixi/spine-player（§4.2） |
| `$ROOT\frontend\js\pet.js` | `DEFAULT_STATE` 缺 `renderer/dnd/locked/sizeTier` 字段 | 补默认字段 |
| `$ROOT\frontend\js\pet.js` | `initLive2D()` 硬编码走 Live2D | 改 `initRenderer()` 路由（默认 Spine） |
| `$ROOT\frontend\js\pet.js` | `startOnboarding()` 气泡式 4 行 | 五步滑层 |
| `$ROOT\frontend\js\pet.js` | `renderSettings()` 单页 7 行 | 五 tab 渲染 + 存储分流 |
| `$ROOT\frontend\js\pet.js` | `handleMenuAction` 缺 勿扰/锁位/切换模型/语音对话分组 | 补全分组动作 |
| `$ROOT\frontend\js\pet.js` | `isOverInteractiveDom` 未含 onboarding/锁位虚线框 | 补层级 |
| `$ROOT\frontend\js\pet.js` | `WALK_MOTIONS` 为 Live2D 动作 | 切 Spine 后映射 `target/target2/target3` |
| `$ROOT\frontend\js\live2d.js` | `_fitPet` topZone=min(110,h*0.2)/bottomMargin=12 | 对齐 §1.4（8% / −16px），或对话模式保留现状仅 Spine 侧实现 |
| `$ROOT\desktop\src\main\config.js` | `DEFAULTS.pet` 默认 420×560、无 locked/dnd/sizeTier/screenId | 默认 320×420 + 新增字段 |
| `$ROOT\desktop\src\main\windows.js` | `resizable:false`、`moveBy` 无锁位守卫、无 `setSize/moveToDisplay` | 支持 resize IPC + 锁位守卫 + 多屏 |
| `$ROOT\desktop\src\main\index.js` | 无锁位/勿扰/resize/多屏 IPC | 注册新 IPC |
| `$ROOT\desktop\src\preload\pet.js` | 无 `setLocked/setDnd/setSize/resizeBy/getDisplays/moveToDisplay` | 白名单新增 |

### 3.3 需新增

| 新增文件（绝对路径） | 用途 |
|---|---|
| `$ROOT\frontend\assets\spine\314701_wmz_s_room.skel` / `.atlas` / `.png` / `_bloom.png` | Spine 小模型素材（自 `$SRC` 复制） |
| `$ROOT\frontend\assets\lib\spine-core.js` + `spine-pixi.js` | 主方案运行时（pixi-spine 4.2） |
| `$ROOT\frontend\assets\lib\spine-player.js` | 降级运行时（自 `$SRC\viewer\lib\spine-player.js` 复制） |
| `$ROOT\frontend\js\spine.js` | SpinePet 渲染器/适配器（`window.RoleplaySpine`） |
| `$ROOT\frontend\assets\spine\animation_map.json` | 动画名 → 语义表（P0-3 回填） |
| `$ROOT\frontend\assets\spine\expression_map.json` | 情绪映射表（与 `interact_map.json` 平级，风格板 §8.5） |
| `$ROOT\frontend\pet-inspect.html` + `$ROOT\frontend\js\pet-inspect.js` | 动画巡检页（P0 临时） |
| `$ROOT\frontend\assets\icons\*.svg` | SVG 描边图标集（风格板 §9 清单） |

### 3.4 逐项差距对照表（规范要求 vs 现状）

| 规范条目 | 现状 | 差距定性 |
|---|---|---|
| §2.1 Spine 素材落位 | 素材在 `$SRC\viewer-data\03_动态资源\Spine战斗\`，未复制进 `frontend/assets/spine/` | 需新增（复制） |
| §2.1 动画语义表（30+） | 无任何 Spine 动画映射 | 需新增（巡检回填） |
| §2.2 pixi-spine 4.2 运行时 | `assets/lib` 无 spine 运行时 | 需新增（运行时） |
| §2.3 三档窗口 320/420/480 | `config.js` 默认 420×560，`windows.js` `resizable:false` | 需修改（默认 + 缩放） |
| §2.3 居中偏下定位 | `live2d.js _fitPet` 近似实现但参数不一致 | 需修改/新增（Spine 侧重写） |
| §3.2 z-index 命中优先级 | `pet.js` 已有层级判定，但缺 onboarding/引导层 | 需修改 |
| §4.1 气泡打字机/操作行/aria | 只有 show/hide/超时，无打字机/操作行/aria | 需修改（P0 基础 / P2 操作行） |
| §4.2 右键菜单三组+SVG | emoji 图标、未分组、min-width 168 | 需修改 |
| §4.3 设置五 tab 卡片化 | 单页 7 行 | 需修改（P1） |
| §4.4 状态 chip 四枚 20px | 3 枚 10px chip + 6px 圆点 | 需修改 |
| §4.5 输入条折叠圆钮 | 无折叠圆钮、无 Ctrl+Enter、无语音切换 | 需修改 |
| §4.6 引导滑层五步 | 气泡式 4 行 | 需修改 |
| §4.7 勿扰 | 无（仅静音） | 需新增 |
| §4.8 锁位 | 无 | 需新增 |
| §6.1 九态状态机 | 状态零散（chatBusy/dragging/WALK_MOTIONS/录音轮询） | 需修改（集中重构） |
| §5.4 屏幕识别三档 | `ocr.js` 已有手动/关键词/定时 | 已具备（微调 + 编辑器） |
| §8 可访问性 | 无 aria/焦点可见/`prefers-reduced-motion` | 需新增 |

---

## 4. Spine 渲染器接入方案

### 4.1 技术选型与运行时获取

- **主方案**：pixi-spine（`@esotericsoftware/spine-pixi` 4.2）+ `@esotericsoftware/spine-core` 4.2，与已加载的 PIXI 同栈，共享 WebGL 上下文。
  - ⚠️ 工程注意：`spine-pixi` 以 ESM 分发，而 `pet.html` 是**无打包器的裸 `<script>` 环境**。落地方式二选一：
    1. （推荐）用 esbuild/rollup 一次性打包 `spine-core + spine-pixi` 为 IIFE 单文件 `frontend/assets/lib/spine-pixi.bundle.js`，`global.PIXI` 外部引用；或
    2. 直接引入第三方预构建的 UMD 版（如 jsdelivr 上的 spine-pixi 4.2 UMD bundle），同样要求 `PIXI` 全局先于其加载。
  - 需在 P0-1 用 `spine-core` 的 `SkeletonBinary.version` 校验 `.skel` 二进制版本（3.8 vs 4.x），版本不符即触发降级。
- **降级方案**：`spine-player.js`（素材包自带 `$SRC\viewer\lib\spine-player.js`，查看器取向，内置旧版 spine-webgl 运行时）。以其 `SpinePlayer` 实例的 `animationState` 做控制；混排能力降级为"整段切换"，行走-待机过渡允许 1 帧硬切。

### 4.2 文件级落点与加载顺序

**新文件**：
- `$ROOT\frontend\assets\lib\spine-core.js`（或 `spine-pixi.bundle.js`，二选一）
- `$ROOT\frontend\assets\lib\spine-pixi.js`（主方案运行时）
- `$ROOT\frontend\assets\lib\spine-player.js`（降级运行时，自 `$SRC\viewer\lib\spine-player.js` 复制）
- `$ROOT\frontend\js\spine.js`（SpinePet 适配器，`window.RoleplaySpine`）
- `$ROOT\frontend\assets\spine\` 四素材 + `animation_map.json` + `expression_map.json`

**加载顺序（`pet.html` `<body>` 末尾，插入 spine 相关脚本）**：
```
live2dcubismcore.min.js → pixi.min.js → pixi-live2d-display-cubism4.min.js
  → spine-core.js → spine-pixi.js → spine-player.js（降级，仅当 spine-pixi 加载失败时兜底）
  → live2d.js → voice.js → chat.js → spine.js（新增）→ live2d-bootstrap.js → pet.js
```
约束：`spine-core` 必须先于 `spine-pixi`；`spine-pixi` 依赖全局 `PIXI`（在 `pixi.min.js` 之后）；`spine.js` 在 `pet.js` 之前，供 `pet.js` 引用 `window.RoleplaySpine`。

### 4.3 双渲染器接口（SpinePet 适配器 + 统一行为接口）

pet.js 引入渲染器路由，两渲染器收敛到同一 `PetRenderer` 接口：

```js
// pet.js 内部约定（不落地为独立文件，写在 spine.js / pet.js 注释）
interface PetRenderer {
  init(opts) -> Promise<boolean>            // 挂载容器、加载模型
  walk(direction)                            // 行走：Spine=target*+flipX；Live2D=窗口滑动+轻动作(退化)
  idle()                                     // 待机池
  emotion(tag)                               // 情绪：Spine=animation_map；Live2D=onEmotionEvent
  click()                                    // 单击反馈池：Spine=djc1/djc2；Live2D=CLICK_POOL
  sleep(level)                               // 睡眠序列：Spine=he_shang→he_di→deng
  setZoom(mult) / setVisible(v) / setFlip(dir)
  destroy()                                  // 切换渲染器前销毁（释放 WebGL 上下文）
}
```

- `window.RoleplaySpine`（`spine.js`）实现 `PetRenderer`，内部维护 `SpinePlayer`/pixi-spine 的 `animationState`、`TrackEntry` 回调、`flipX`。
- Live2D 侧用一个薄包装把现有 `RoleplayLive2D.playGesture/onEmotionEvent/...` 映射到同一 `PetRenderer`。
- pet.js 持有 `currentRenderer`，默认 `RoleplaySpine`；设置「模型」tab 切换时 `currentRenderer.destroy()` → `newRenderer.init()`。
- **行为映射表**（§2.4）作为单一数据源：`walk/idle/click/listen/speak/happy/sad/surprise/sleep/enter` 各列 Spine 动画名与 Live2D 动作名；未映射情绪回落待机池。

### 4.4 动画巡检页（P0 首日实播 30+ 动画回填语义表）

- 文件：`$ROOT\frontend\pet-inspect.html` + `$ROOT\frontend\js\pet-inspect.js`（**临时页，P0 完成后可保留为调试工具或删除**）。
- 实现要点：
  1. 仅加载 `pixi.min.js` + `spine-player.js`（降级运行时即可巡检，避免打包依赖）。
  2. 加载 `314701_wmz_s_room.skel` + `314701_wmz_s.atlas`，用 skeleton data 的 `animations` 数组枚举全部动画名（含 30+ 动画）。
  3. UI：下拉选动画名 + 播放/暂停 + flipX + loop + 0.5×/1×/2× 速度 + 记录按钮。
  4. 「记录」把 `{name, 观察到的语义槽位, 是否命名推测吻合, 备注}` 写进 localStorage，最终导出/复制为 `animation_map.json`。
- 产出：`$ROOT\frontend\assets\spine\animation_map.json`（覆盖全部动画名 → 语义槽位：行走/入场/点击/正向反馈/待机池/收纳/睡眠三段/情绪变体/彩蛋），并回填规范 §2.1 语义表（含 ⚠️ 项确认/修正）。
- 验收：半小时内完成；若发现语义不符（如 `bian` 实为换装），按 §12 Q5 允许文档内小修订。

### 4.5 降级路径判定

1. `spine-pixi` 未加载（`window.PIXI.spine` 不存在）→ 用 `spine-player.js`。
2. `spine-pixi` 加载 `.skel` 抛二进制版本不兼容 → 捕获后自动退回 `spine-player.js`。
3. 两条路径统一收敛在 `spine.js` 的 `SpinePet` 适配器后，`pet.js` 行为接口不变；降级时混排能力降级为整段切换。

---

## 5. 主进程扩展点（锁位 / 勿扰 / 多屏摆位 / resize IPC）

### 5.1 需求分解

| 需求 | 主进程职责 | 现有能力 |
|---|---|---|
| 锁位 | `moveBy` 锁定时 no-op；锁态持久化 | 无 |
| 勿扰 | 漫步暂停（walker.pause）+ 状态持久化 | `setBusy` 可临时暂停，但非持久态 |
| 多屏摆位 | `screen` 枚举 + 窗口定位到指定显示器/坐标 | `physics.clampPosition` 已多屏感知，但无主动摆位 |
| resize | 窗口三档/拖拽缩放 → `setSize` + 尺寸钳制 | `resizable:false`，无 setSize |

### 5.2 各文件最小改动清单

| 文件（绝对路径） | 改动内容 |
|---|---|
| `$ROOT\desktop\src\main\config.js` | `DEFAULTS.pet` 新增：`locked:false`、`dnd:false`、`sizeTier:"S"`（或 `width:320,height:420` 对齐默认档）、`screenId:null`、`alwaysOnTopLevel` 已有；新增 `pet.dndAutoReleaseMs:30*60*1000`（可选自动解除，渲染层计时，主进程只读） |
| `$ROOT\desktop\src\main\windows.js` | ① `moveBy(dx,dy)` 开头加 `if (loadConfig().pet.locked) return;`（或读入参）；② 新增 `setPetSize(w,h)`：`petWin.setSize(Math.round(w), Math.round(h))`，钳制到 320×420 ~ 480×640；③ 新增 `moveToDisplay(screenId)` / `moveToPosition(x,y)`（`screen.getAllDisplays()` 定位）；④ `defaultPosition(cfg)` 支持 `cfg.pet.screenId` 指定显示器；⑤ 保留 `resizable:false`，缩放走 resize IPC + 渲染层自绘 resize grip（透明无边框窗用 OS 边框缩放观感差） |
| `$ROOT\desktop\src\main\index.js` | 注册 IPC：`pet:locked`（`ipcMain.on`，写 config + 推送）、`pet:dnd`（写 config + `walker.pause()/resume()`）、`pet:resize`（`setPetSize`）、`pet:get-displays`（`ipcMain.handle` 返回 `screen.getAllDisplays()` 摘要）、`pet:move-to-display`（`moveToDisplay`）；`pet:move-by` 处理器内并入锁位守卫（或交 windows.moveBy 内部守卫） |
| `$ROOT\desktop\src\main\behavior.js` | 无结构改动；DND/锁位时由 index.js 调 `walker.pause()`（复用现有 API）。可选：`schedule()` 读 `cfg.pet.dnd/locked` 短路 |
| `$ROOT\desktop\src\main\physics.js` | 无改动（`clampPosition` 已用 `getDisplayNearestPoint`，天然多屏；锁位时无拖拽故无动量） |
| `$ROOT\desktop\src\main\ocr.js` | 无改动（三档已具备；关键词编辑器由渲染层写 config 后 `setConfig` 持久化） |
| `$ROOT\desktop\src\main\control-server.js` / `backend.js` / `raf.js` | 无改动 |
| `$ROOT\desktop\src\preload\pet.js` | `petApi` 新增：`setLocked(v)`、`setDnd(v)`、`setSize(w,h)`、`resizeBy(dx,dy)`、`getDisplays()`、`moveToDisplay(id)`、`onLockState(cb)`（主进程推送锁态给渲染层同步 chip） |

**IPC 契约（新增，供实施）**：
- `pet:locked` `(locked:boolean)` → 写 config + `webContents.send("pet:lock-state", {locked})`
- `pet:dnd` `(dnd:boolean)` → 写 config + `walker.pause()/resume()` + 推送
- `pet:resize` `({w,h})` → `setPetSize(w,h)`（钳制 320×420~480×640）
- `pet:get-displays` → `[{id, bounds, workArea, isPrimary}]`（`screen` API，不外传）
- `pet:move-to-display` `({id})` → `moveToDisplay(id)`

---

## 6. 风险清单与验收清单

### 6.1 风险清单

| # | 风险 | 影响 | 缓解 / 决策 |
|---|---|---|---|
| R1 | `.skel` 二进制版本与 spine-pixi 4.2 不兼容 | P0-2 阻塞 | P0-1 先校验版本；不兼容自动退 `spine-player.js`（§4.5） |
| R2 | 20+ 动画语义为命名推测（§2.1 ⚠️） | 后续所有映射错位 | P0-3 巡检页半小时实播回填，是全局前置依赖 |
| R3 | 勿扰透明度 0.45 vs 0.55 冲突 | 验收分歧 | 以 Rev1/风格板 §7.7 **0.55** 为准；同步修规范 §6.2 与 §11 陈旧值 |
| R4 | 跨文档命名冲突：Spine 动画名（风格板 §8.5 `bm_hy*/zm_*` vs 呈现规范 §2.1 `x_ls_*/target/djc*`）；气泡 max-width 88% vs 92%；缩放范围 0.7~1.4 vs 0.5~1.5；引导遮罩色值 | 实现选错源 | P0-3 巡检时以 `.skel` 真实动画名为准回填，映射表落盘统一；其余取"呈现规范为主、风格板为皮肤"并在代码注释标注 |
| R5 | 默认窗口 420×560（`config.js`）vs 规范默认 320×420 | 首屏不符 | P0 改 `DEFAULTS.pet.width/height` 为 320/420 |
| R6 | 输入条展开抢焦点 vs 穿透（§12 Q1） | 展开期间窗口不可穿透 | 接受取舍（8s 无操作自动收起），维持当前方案 |
| R7 | 双渲染器 WebGL 上下文并存 | 显存/性能 | 切换即 `destroy()` 旧渲染器，单上下文复用 PIXI App |
| R8 | 透明无边框窗的缩放（OS resize 边框观感差） | 视觉 | `resizable:false` + 自绘 resize grip + `pet:resize` IPC |
| R9 | 多屏副屏断开（§12 Q3） | 窗口迷失 | 取"副屏断开回主屏原位"（简单可预期） |
| R10 | 截图分享隐私（§12 Q4） | 隐私 | 仅合成"人偶+气泡"，导出需用户确认对话框 |
| R11 | 唤醒词（§12 Q2） | 范围蔓延 | 本版不做，列 v1.1 候选 |
| R12 | `prefers-reduced-motion` 覆盖全部动效 | a11y | 风格板 §6.3/§11 全局瞬时切换，实施时统一 token |

### 6.2 验收清单（QA 可勾选，对应规范 §11）

**P0**
- [ ] 320×420 默认档下 Spine 人偶头/肩/手/表情完整可见，头顶留白 ≈8%，脚底贴落地线（下沿−16px）
- [ ] 漫步时 `target` 行走动画与窗口位移同步，方向镜像（flipX）正确
- [ ] 顶栏品牌条常显；chip 带文字（M/L 档）且悬停有诊断 tooltip，异常可点击重试
- [ ] 输入条可从菜单/圆钮/Ctrl+Enter 展开，Enter 发送走完整 SSE 管线，Esc 收起
- [ ] 引导滑层 5 步可逐步/跳过，关闭后 localStorage 标记生效，设置中可重看
- [ ] 气泡打字机/超时（2200+90ms/字，上限 9000）/关闭正确；`role="status" aria-live="polite"`
- [ ] 默认启动即 Spine 人偶；设置切 Live2D 后 420×560 大模型完整可见、情感联动正常
- [ ] 动画巡检页完成，`animation_map.json` 覆盖 30+ 动画并回填 §2.1 语义表

**P1**
- [ ] 右键菜单三组分组、SVG 图标、无 emoji；贴边翻转正确；↑↓+Enter 可达
- [ ] 设置抽屉五个 tab 全部可改可存，桌面端项写入 `config.json` 重启生效
- [ ] 勿扰：透明度 0.55、禁声、漫步暂停、chip 浮现、菜单一键解除
- [ ] 锁位：拖拽失效、拖拽尝试播 `djc1` + toast、长按 1.5s 解锁、虚线框 + 锁位 chip
- [ ] 状态机九态视觉表现与 §1.2 一致；修饰态可正交叠加
- [ ] OCR 触发气泡显首句摘要 + 「详细」折叠；三档节流生效
- [ ] 多屏摆位：主屏/副屏/指定坐标可用，副屏断开回主屏
- [ ] 快捷键提示：`?` 帮助气泡、菜单 hint、改键生效

**P2**
- [ ] 入场动画（`cs2` ⚠️巡检确认）正确，`prefers-reduced-motion` 改淡入
- [ ] 气泡操作行（复制/朗读/上一句/下一句/✕）+ 历史翻页 20 条 + `↑/↓`
- [ ] 截图分享仅"人偶+气泡"、导出需用户确认对话框、零自动落盘

**全局**
- [ ] 键盘全路径可达；`prefers-reduced-motion` 下动效降级
- [ ] 全部网络请求仅回环；截图/录音内存流转零落盘
- [ ] 视觉值全部 `var(--token)` 引用，无硬编码色值（结构性尺寸如窗口档位除外）

---

*（正文完。本文档不修改任何现有代码，仅作为 `pet-presentation-spec-v0.3.md` 的可执行落地计划。）*
