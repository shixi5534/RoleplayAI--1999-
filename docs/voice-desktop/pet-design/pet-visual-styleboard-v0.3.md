# 桌面宠物 · 视觉风格板 v0.3

> 状态：**设计规范（供实施引用）** —— 纯视觉规范文档，不含代码改动。
> 配套文档：`pet-interaction-spec-v0.3.md`（文策渊：组件结构 / 状态机 / 交互流程）。
> 分工约定：组件的**结构、状态、行为**以文策渊文档为准；组件的**色彩、字体、间距、描边、阴影、动效、素材适配**以本文档为准。两份文档通过 §11 的 design token 对齐——文策渊文档中所有视觉值只允许写作 `var(--token)` 形式，禁止硬编码色值与像素。

---

## 1. 设计哲学

### 三个视觉支柱

1. **古典克制**：桌面宠物是"常驻桌面的一角"，不是应用主界面。所有 UI 元素默认退让，只在被召唤（悬停 / 右键 / 对话）时浮现。任何常驻元素的视觉重量都必须低到"余光可忽略"——细字、细线、低饱和、半透明。
2. **暗夜金铜**：延续主页"暴雨之前"的暗调底色与金铜强调色。金铜 `#c9a86a` 是全应用唯一的高饱和装饰色，只用于：强调文字、图标描边、焦点反馈、品牌字。不做大面积填充。
3. **人偶私语**：v0.3 起默认渲染形态从 Live2D 大模型切换为 **Spine 小模型（人偶形态）**。气质从"舞台上的角色"变为"桌上的小偶人"——更小、更近、更安静。文案与 UI 密度都随之收敛：气泡是"凑近耳边的一句话"，不是对话框。

### 与主页"暴雨之前"的关系：延续但不复制

主页是**剧场**（1280×800，完整 HUD、聊天面板、仪式感）；宠物是**剧场散场后留在桌上的那个人偶**。两者共享同一套色板、字体栈、金铜描边语言，但宠物侧做三处降格处理：

- 字号整体下调一档（主页正文 14px → 宠物正文 13px）；
- 面板透明度更高（`--bg-panel` 沿用 0.92 alpha，但 chip 等次级面板降到 0.66 alpha），让桌面壁纸透出来；
- 装饰元素只保留"描边 + 阴影"两种，不引入主页的标题栏纹理与 HUD 框架。

---

## 2. 色彩系统

### 2.1 主色板

沿用现有色板（`pet.html :root`），新增弱化/强化层级，构成完整梯度：

| Token | 值 | 用途 |
|---|---|---|
| `--fg` | `#e8e2d4` | 主文字（气泡正文、菜单项、输入框文字） |
| `--fg-dim` | `#9a968a` | 次级文字（label、placeholder、chip 中性态） |
| `--fg-faint` | `rgba(232, 226, 212, 0.25)` | **新增**。弱化层级：禁用文字、装饰性提示、引导滑层的插图占位描边 |
| `--accent` | `#c9a86a` | 强调：图标描边、标题字、焦点态、发送按钮底色 |
| `--accent-dim` | `rgba(201, 168, 106, 0.55)` | **新增**。次级强调：非激活 tab、次级描边文字 |
| `--accent-glow` | `rgba(201, 168, 106, 0.14)` | **新增**。金铜辉光：菜单项 hover 底色、chip hover 底色 |
| `--ok` | `#7fb069` | 成功态（后端在线、Ollama 就绪） |
| `--danger` | `#c96a6a` | 警示红（后端离线、录音中、退出菜单项） |
| `--warn` | `#d9a24a` | **新增**。非致命警告（Ollama 未启动但可重试、OCR 无结果、低电量式提示）。与 `--accent` 区分：warn 只出现在状态圆点和 chip 文字，不做装饰 |
| `--bg-panel` | `rgba(16, 22, 28, 0.92)` | 主面板底（气泡、菜单、抽屉） |
| `--bg-panel-hover` | `rgba(26, 34, 42, 0.94)` | **新增**。面板 hover 底（控件悬停） |
| `--bg-panel-active` | `rgba(34, 44, 54, 0.95)` | **新增**。面板按下 / 选中底（激活 tab、选中项） |
| `--line` | `rgba(201, 168, 106, 0.28)` | 常规描边 |
| `--line-strong` | `rgba(201, 168, 106, 0.50)` | **新增**。强反馈描边（输入框 focus、激活 tab 下划线、锁位虚线） |
| `--line-faint` | `rgba(201, 168, 106, 0.14)` | **新增**。最弱描边（菜单分隔线、chip 默认描边、卡片内分隔） |

### 2.2 状态色映射（chip 专用）

| 状态源 | 正常 | 异常 / 特殊 |
|---|---|---|
| 后端 | 圆点 `--ok`，文字 `--fg` | 圆点 `--danger`，文字 `--danger` |
| Ollama | 圆点 `--ok`，文字 `--fg` | 未启动：圆点 `--warn`，文字 `--warn`（非致命，可重试）；探测失败：圆点 `--danger` |
| 录音 | 待机：圆点 `--fg-dim`，文字 `--fg-dim` | 录音中：圆点 `--danger`（呼吸闪烁，见 §6），文字 `--fg` |
| 勿扰 | — | 圆点 `--fg-dim`，文字 `--fg-dim`，chip 描边降为 `--line-faint` |
| 睡眠 | — | 圆点 `--fg-dim`，文字 `--fg-dim`，文字内容"睡眠中" |

规则：**圆点永远承担色彩信号，文字永远承担语义信号**——色盲用户不靠圆点颜色也能读懂状态（见 §10）。

### 2.3 对比度自查（WCAG AA）

以最深背景（面板底等效 `#10161c` 实色）为基准计算：

| 组合 | 对比度 | 要求 | 结论 |
|---|---|---|---|
| `--fg` on `--bg-panel` | ≈ 13.2:1 | ≥ 4.5:1 | ✅ |
| `--fg-dim` on `--bg-panel` | ≈ 6.1:1 | ≥ 3:1（次级） | ✅ |
| `--accent` on `--bg-panel` | ≈ 7.4:1 | ≥ 4.5:1（图标/强调文） | ✅ |
| `--warn` on `--bg-panel` | ≈ 6.8:1 | ≥ 4.5:1 | ✅ |
| `--danger` on `--bg-panel` | ≈ 4.9:1 | ≥ 4.5:1 | ✅ |
| `--ok` on `--bg-panel` | ≈ 6.3:1 | ≥ 4.5:1 | ✅ |

注意：`--fg-faint`（0.25 alpha）对比度不足 3:1，**只允许用于装饰与禁用态，禁止承载信息**。

---

## 3. 字体规范

### 3.1 字体栈

| Token | 值 | 用途 |
|---|---|---|
| `--font-serif` | `"Georgia", "Songti SC", "SimSun", "STSong", serif` | 全部 UI 文字（沿用现有 `--font-sans`，v0.3 改名 `--font-serif`，旧名保留别名一版） |
| `--font-mono` | `"Consolas", "Courier New", monospace` | OCR 摘要、错误码、快捷键键名（如 `Alt+Space`） |

### 3.2 字号阶梯

| Token | 值 | 用途 |
|---|---|---|
| `--fs-chip` | 10px | chip 文字、品牌条、气泡辅助按钮标注 |
| `--fs-caption` | 11px | 次级说明、tooltip、浏览器提示条 |
| `--fs-small` | 12px | 菜单项、设置 label、toast |
| `--fs-body` | 13px | 正文基准：设置正文、输入框、错误提示 |
| `--fs-bubble` | 14px | 气泡正文（强调正文，宠物"说话"要比 UI 文字大半档） |
| `--fs-title` | 16px | 抽屉标题、引导滑层步骤标题（备用档） |
| `--fs-heading` | 18px | 引导滑层主标题（宠物侧最大字号，到此为止） |

### 3.3 字重 / 行高 / 字距

- **字重**：400 为默认；500 仅用于强调词与激活 tab；700 仅允许用于纯数字（如设置中的温度值、计时）。古风衬线体在 700 下笔画粘连，**禁止用于中文标题**。
- **行高**：`--lh-tight: 1.4`（chip / 菜单 / 单行控件）；`--lh-normal: 1.55`（气泡正文，沿用现有）；`--lh-loose: 1.7`（设置正文、引导描述）。
- **字距**：常规 `0`；强调文字 `0.05em`；标题与品牌条 `0.2em`（沿用现有品牌条的 0.22em 微调为统一 token）；chip 文字 `0.08em`。

---

## 4. 间距与栅格

基础栅格 **4px**，所有尺寸必须是 4 的倍数。

| Token | 值 | 典型用途 |
|---|---|---|
| `--space-1` | 4px | chip 内 dot 与文字间距、图标与文字最小间距 |
| `--space-2` | 8px | chip 之间间距、菜单项纵向 padding、气泡按钮间距 |
| `--space-3` | 12px | 设置行间距、气泡内边距（纵向）、小窗口内边距 |
| `--space-4` | 16px | 标准窗口内边距、抽屉内边距、卡片 padding |
| `--space-5` | 24px | 分组之间的垂直间距、引导滑层区块间距 |
| `--space-6` | 32px | 抽屉大分组间距、引导滑层上下留白 |

固定规则：
- 窗口内边距：默认窗口（320×420）用 `--space-3`（12px）；放大窗口（≥480 宽）用 `--space-4`（16px）。
- 组件间距：chip 与 chip `--space-2`；菜单项上下 padding `--space-2`；设置行纵向间距 `--space-3`；设置分组间距 `--space-5`。
- 气泡与模型的最小净距：**8px**（气泡尾巴尖到模型头顶包围盒，见 §7.1）。

---

## 5. 描边与阴影

### 5.1 描边

- 常规：`1px solid var(--line)`——气泡、菜单、抽屉、输入框默认态。
- 强反馈：`1px solid var(--line-strong)`——输入框 focus、锁位模式虚线（`dashed`）、激活 tab。
- 禁用 / 弱化：`1px solid var(--line-faint)`——菜单分隔线（1px 高实色填充）、chip 默认描边、禁用控件。

### 5.2 圆角

| Token | 值 | 用于 |
|---|---|---|
| `--radius-chip` | 999px | chip、toast、胶囊按钮 |
| `--radius-card` | 8px | 菜单、设置卡片、输入框、控件 |
| `--radius-bubble` | 10px | 气泡（比卡片多半档，呼应"说话"的柔软感） |
| `--radius-drawer` | 12px | 设置抽屉、引导滑层 |

### 5.3 阴影阶梯

| Token | 值 | 层级语义 |
|---|---|---|
| `--shadow-s1` | `0 4px 12px rgba(0,0,0,0.35)` | 浮起：chip、按钮 hover、输入条 |
| `--shadow-s2` | `0 6px 24px rgba(0,0,0,0.45)` | 卡片：气泡（沿用现有值） |
| `--shadow-s3` | `0 10px 32px rgba(0,0,0,0.55)` | 弹层：右键菜单（沿用现有值）、设置抽屉 |
| `--shadow-s4` | `0 20px 60px rgba(0,0,0,0.65)` | 模态：新手引导滑层 |

阴影只做"抬升"，不做彩色辉光；金铜氛围靠 `--accent-glow` 底色与描边表达，不靠 shadow。

---

## 6. 动效规范

### 6.1 时长阶梯

| Token | 值 | 用于 |
|---|---|---|
| `--dur-fast` | 120ms | hover 变色、按钮反馈 |
| `--dur-mid` | 200ms | 菜单开合、气泡进出、chip 显隐 |
| `--dur-slow` | 350ms | 抽屉滑入、设置卡片展开 |
| `--dur-xslow` | 600ms | 引导滑层翻页、欢迎入场 |

### 6.2 缓动

| Token | 值 | 用于 |
|---|---|---|
| `--ease-standard` | `cubic-bezier(0.4, 0, 0.2, 1)` | 状态切换默认 |
| `--ease-enter` | `cubic-bezier(0, 0, 0.2, 1)` | 元素入场（先快后稳） |
| `--ease-exit` | `cubic-bezier(0.4, 0, 1, 1)` | 元素退场（加速离开） |

### 6.3 具体动效约定

- 透明度过渡统一 `opacity var(--dur-mid) ease`（沿用现有 0.18s，v0.3 归一为 token 引用）。
- 气泡进场：`opacity 0→1` + `translateY(4px→0)`，`var(--dur-mid) var(--ease-enter)`；退场反向用 `--ease-exit`。
- 录音 chip 圆点呼吸：`opacity 1→0.35→1`，1200ms 循环，`--ease-standard`；**进入勿扰/睡眠或 prefers-reduced-motion 时停闪**，改常亮。
- 打字机光标：竖线 `│` 字符，`opacity` 步进闪烁 530ms（`steps(1)`，模拟终端光标，不做平滑渐变）。
- 模型淡入（欢迎动画 P2-2）：`opacity 0→1` + `scale 0.96→1.0`，`var(--dur-xslow) var(--ease-enter)`。
- **减少动效模式**：`@media (prefers-reduced-motion: reduce)` 下所有过渡/动画时长强制为 `0.01ms`，即瞬时切换；呼吸闪烁与打字机光标改为常亮显示。

---

## 7. 组件视觉规格

> 组件的结构与状态机以文策渊《交互呈现规格 v0.3》为准；本节只定**皮肤**。

### 7.1 气泡 `#pet-bubble`

- **尺寸**：`max-width: 88%`（相对窗口，320 宽窗口下 ≈ 280px）；`min-width: 120px`；`padding: 10px 14px`（即 `--space-3` 纵向 + 14px 横向，横向不破栅格属排版微调，允许）；最多 4 行，超出 `overflow-y: auto`（自定义滚动条宽 4px，滑块 `--line`）。
- **配色**：底 `--bg-panel`，描边 `1px --line`，文字 `--fg`，正文 `--fs-bubble` / `--lh-normal`。
- **阴影**：`--shadow-s2`。
- **尾巴**：`::after` 10×10px 方块旋转 45°，沿用现有实现；默认朝下居中（气泡在模型上方时）；当窗口贴近屏幕顶部、气泡改为显示在模型**下方**时，尾巴翻转到上方（`top: -6px`，边框改 `border-left` + `border-top`），旋转角度不变——**尾巴永远指向模型头顶**。
- **打字机光标**：正文末尾追加 `│`（`--accent` 色），530ms `steps(1)` 闪烁，流式结束后移除。
- **辅助按钮区**（关闭 / 复制 / 朗读，见交互规格）：气泡右下内嵌一行，图标 12×12 SVG（§9），图标间距 `--space-2`，默认 `opacity 0.5`，hover 单个按钮 `opacity 1` + `--accent-glow` 圆角 4px 底。
- **定位规则（解决"气泡与模型重叠"）**：气泡锚定窗口顶部 `top: var(--space-2)`；气泡底沿到模型头顶包围盒顶沿的净距 ≥ `--space-2`（8px）。若窗口高度 < 380px 导致净距不足，气泡自动收窄到 `max-width: 76%` 并启用滚动，**绝不允许下压到模型面部区域**（面部区域 = 模型包围盒上 40%）。

### 7.2 右键菜单 `#pet-menu`

- **尺寸**：`min-width: 172px`；菜单项高 **36px**（padding `0 14px`）；菜单整体 padding `5px 0`（沿用）。
- **配色**：底 `--bg-panel`，描边 `--line`，文字 `--fg` / `--fs-small` / `--lh-tight`；hover 底 `--accent-glow`（沿用现有 0.14 值，归入 token）；危险项（退出）文字 `--danger`，hover 底 `rgba(201,106,106,0.12)`。
- **图标**：16×16 SVG 描边图标（§9），与文字间距 9px（沿用现有 gap），描边色 `--accent`；危险项图标描边 `--danger`。
- **分组分隔线**：1px 高 `--line-faint`，上下 margin `--space-1`，左右内缩 `--space-2`。
- **阴影**：`--shadow-s3`。圆角：`--radius-card`。
- **状态**：禁用项 `opacity 0.4` + 图标描边降为 `--fg-faint`；带快捷键的项右侧显示键名（`--font-mono` 10px `--fg-dim`，如 `Alt+Space`）。

### 7.3 设置抽屉 `#pet-settings`

- **布局**：全窗口覆盖，圆角 `--radius-drawer`（四角露出窗口透明边），底 `rgba(12,16,20,0.94)`（沿用现有，略深于 `--bg-panel` 以压住后方模型），阴影 `--shadow-s3`，内边距 `--space-4`。
- **顶部 tab bar**：高 **32px**，底部 1px `--line` 分隔；tab 文字 `--fs-small`，未激活 `--fg-dim`，激活 `--accent` + 底部 2px `--line-strong` 指示条；tab 间距 `--space-4`。
- **分组卡片化（解决"60% 留白"）**：每组设置项放进卡片——底 `rgba(22,30,38,0.6)`，描边 `--line-faint`，圆角 `--radius-card`，padding `--space-3` `--space-4`，卡片纵向间距 `--space-3`。卡片标题 `--fs-caption` `--fg-dim` 字距 0.2em。
- **控件**：所有控件（select / number / range / 开关）高 **28px**，底 `rgba(22,30,38,0.9)`，描边 `--line`，focus 时描边 `--line-strong`；range 滑块圆形 12px，底 `--accent`；开关 32×18px 胶囊，on 态底 `--accent-dim`、圆点 `--accent`。
- **行密度**：行高 28px + 上下 `--space-1`，label 左 `--fg-dim`，控件右；行与行 `--space-2`。
- 右上角关闭按钮：18×18 "×" 图标（SVG 描边，`--fg-dim`，hover 变 `--fg`）。

### 7.4 状态 chip `#pet-status .chip`

- **尺寸**：高 **20px**；圆点 **6×6px**；文字 `--fs-chip`（10px）；padding `4px 8px`；dot 与文字间距 5px（沿用）。
- **配色**：底 `rgba(12,16,20,0.66)`（沿用），描边 `1px --line-faint`；圆角 `--radius-chip`。
- **颜色语义**：见 §2.2 映射表（ok / bad / warn / dim 四态）。
- **布局**：右上角纵向堆叠，chip 间距 `--space-2`，右对齐；整体容器 top `--space-2`、right `--space-2`。
- **交互**：hover 时 chip 底升为 `--bg-panel-hover` + 阴影 `--shadow-s1`，并显示 tooltip（诊断文案，`--fs-caption`，底 `--bg-panel`，由交互规格定义内容）。
- 替换掉旧的 7×7px 裸圆点（`.dot` 独立用法废弃，圆点只作为 chip 的子元素存在）。

### 7.5 输入条 `#pet-inputbar`

- **折叠态**（默认）：高 **36px**，位于窗口底部居中、宽 160px 的胶囊——底 `--bg-panel`，描边 `--line`，圆角 `--radius-chip`；左侧 18×18 键盘图标（`--accent`），右侧 placeholder 文字"说点什么…"（`--fs-small` `--fg-dim`）。hover：描边升 `--line-strong`，阴影 `--shadow-s1`。
- **展开态**：占满窗口宽度（左右 `--space-2`，bottom `--space-2`），高 36px；输入框底 `rgba(16,22,28,0.94)`，描边 `--line`，focus 描边 `--accent`（沿用现有）；发送按钮 **32×32px 方形**（圆角 `--radius-card`），底 `--accent`，图标 16×16 描边 `#1a1408`（深底反色，与现有按钮文字色一致）；发送按钮 hover 底 `--accent-dim` 反转为 `--accent` 提亮 10%（实色 `#d4b57e`，仅此处允许，记为 `--accent-bright`）。
- 折叠↔展开过渡：宽度 + 透明度，`var(--dur-mid) var(--ease-enter)`。

### 7.6 新手引导滑层 `#pet-onboarding`

- **结构**：全窗口覆盖，遮罩 `rgba(8,10,14,0.72)` backdrop；中央卡片宽 260px，底 `--bg-panel`，描边 `--line`，圆角 `--radius-drawer`，阴影 `--shadow-s4`，padding `--space-5` `--space-4`。
- **每步内容**：标题 `--fs-heading`（18px）`--accent` 字距 0.2em；描述 `--fs-body`（13px）`--fg` `--lh-loose`；配图区 **200×140px** 占位框——1px 虚线 `--fg-faint` 描边，圆角 `--radius-card`，内部可放示意图或留空（留空时中央放 12px `--fg-faint` 文字"示意图"）。
- **底部导航**：进度点 5 个，6×6px 圆点，当前步 `--accent` 实色，其余 `--fg-faint`，间距 `--space-2`；右侧「下一步」胶囊按钮（底 `--accent`，文字 `#1a1408`，`--fs-small`，padding `6px 14px`），左侧「跳过」文字按钮（`--fg-dim`，hover `--fg`）。
- **动效**：步骤切换 `translateX(12px→0)` + 淡入，`var(--dur-xslow) var(--ease-enter)`。

### 7.7 勿扰模式视觉

- 模型整体 `opacity: 0.55`，过渡 `var(--dur-slow) ease`；
- 全部 chip 降为 dim 态（圆点 `--fg-dim`，文字 `--fg-dim`，描边 `--line-faint`），勿扰 chip 显示"勿扰"并常显（不随其余 chip 自动隐藏）；
- 气泡禁用：不弹新气泡；正在显示的气泡以 `--ease-exit` 收起；
- 右键菜单保留，但菜单顶部插入一行提示项"勿扰中 · 点击解除"（`--fg-dim`，不可选中式样但可点击，点击即解除），其下加分隔线；
- 输入条折叠态保留可用（用户主动打字视为解除勿扰的信号之一，具体行为见交互规格）。

### 7.8 锁位模式视觉

- 模型四周（窗口内边距 `--space-2` 处）绘制 `1px dashed var(--line-strong)` 矩形框，圆角 4px；虚线以 8s 周期缓慢顺时针流动（`stroke-dashoffset` 动画，`prefers-reduced-motion` 时静止）；
- 状态区追加一枚锁位 chip：12×12 锁形 SVG 图标（`--accent`）+ 文字"已锁位"；
- 拖拽手势在此模式下不改变窗口位置（行为见交互规格），视觉反馈：拖拽时光标 `not-allowed`，虚线框闪烁一次（描边 `--line-strong` → `--accent` → `--line-strong`，`--dur-mid`）。

---

## 8. Spine 小模型适配规范

### 8.1 贴图

- 主贴图 `314701_wmz_s.png`：**512×512 atlas**，直接作为 spine-player 的 atlas 纹理，不缩放、不重打包。
- bloom 通道 `314701_wmz_s_room.skel` 配套的 `314701_wmz_s_bloom.png`：作为**叠加发光层**渲染在模型之上——混合模式 `screen`（CSS `mix-blend-mode: screen` 或 pixi/spine 的 ADD/SCREEN blend），**不透明度 0.6**。该层只表达烛火/金饰的自发光，不承担形体；若运行时性能不足，允许整层关闭（设置项"模型辉光"默认开）。
- 贴图预算：宠物窗常驻显存目标 < 32MB；512² RGBA ≈ 1MB ×2 层，远低于预算，无需压缩。

### 8.2 窗口内定位（默认窗口 320×420）

- 模型**水平居中**，垂直方向**居中偏下**：
  - 头顶留白 = 窗口高的 **8%**（420 高下 ≈ 33px），为表情动画的头部摆动预留空间；
  - 脚下对齐窗口下沿 **-16px**（即模型脚底线距窗口底 16px，给输入条折叠态留出悬浮空间）。
- 模型包围盒与窗口左右边距各 ≥ 12px；若缩放导致超出，触发自动缩放回最大适配值。

### 8.3 缩放

- 默认 `zoom = 1.0`，对应 320×420 窗口下模型实际渲染 ≈ **280×360px**。
- 用户可调范围 **0.7 – 1.4**（设置抽屉滑杆，步进 0.05），调节实时预览，松手后按 §8.2 规则重新吸附定位。
- 窗口尺寸变化时（用户改窗口大小预设），模型按窗口高度等比缩放，保持头顶 8% / 脚下 16px 两条规则优先于 zoom 绝对值。

### 8.4 与窗口交互

- 鼠标跟随视线：`autoInteract: true`（spine 骨骼的头部/眼部 bone 朝向光标），默认开，可在设置关闭（省电/减少打扰）。
- 拖拽时模型保持原位（fixedModel）：窗口移动、模型在窗口内的相对位置不变；拖拽手势期间暂停待机动画池，松开后按动量物理（交互规格）滑停，滑停到位后恢复待机。
- 行走/漫步：播放 `target` / `target2` / `target3` 动画 + 窗口 lerp 移动；行走方向改变时模型 `scaleX` 翻转（水平镜像），翻转过渡 ≤ 100ms，避免"硬切头"感。

### 8.5 情感表情映射（Live2D ↔ Spine）

宠物页情感联动在两种渲染器下共用同一套情感事件；Spine 侧按下表映射到骨骼表情动画（命名沿用素材包 `bm_hy*` / `cm_hy*` / `e_*` 约定）：

| 情感事件 | Live2D 表情 | Spine 小模型动画 | 备注 |
|---|---|---|---|
| 微笑 / 开心 | `e_weixiao` | `bm_hy01`（微笑眉眼组） | TTS 收尾手势沿用 |
| 难过 / 委屈 | `e_nanguo` | `bm_hy06`（垂眉） | 持续 4s 后回 `e_idle` 等价态 |
| 疑惑 / 聆听 | `e_yihuo` | `cm_hy03`（偏头疑惑） | 录音中常驻此表情 |
| 严肃 / 认真 | `e_yansu` | `bm_hy11`（蹙眉正视） | 屏幕评论"提醒"类文案用 |
| 面具 / 营业态 | `e_mianju` | `cm_hy09`（标准微笑） | 勿扰解除后的第一句回复用 |
| 待机 | `e_idle` | `zm_*` 姿势池轮播 | 85 个站立姿势，8~18s 随机 |
| 睡眠 | （闭眼+低头动作） | `zm_sleep` 系（无则 `bian1` 蹲坐替代） | 90s/5min 分级沿用 |

> 上表 Spine 动画编号为**占位映射**，实施 P0 时用素材包查看器逐个核对 `bm_hy×18` / `cm_hy×19` 的实际表情语义后回填定稿；映射表落盘为 `frontend/assets/spine/expression_map.json`，与 Live2D 的 `interact_map.json` 平级。

---

## 9. 图标规范

- **风格**：SVG 纯描边，描边宽 **1.5px**，`stroke-linecap: round`，`stroke-linejoin: round`，无填充；描边色统一 `var(--accent)`（危险项用 `var(--danger)`，禁用项用 `var(--fg-faint)`）。
- **尺寸**：菜单 16×16；chip 12×12；输入条 18×18；气泡辅助按钮 12×12。`viewBox` 统一 `0 0 24 24`，用 `width/height` 缩放。
- **来源**：直接引用 Lucide / Feather / Heroicons 的同语义图标路径，**描边色必须覆盖为 token 色**（内联 `stroke="currentColor"` + CSS `color: var(--accent)`），禁止保留库默认黑色。
- **必备清单**（语义 → 推荐库图标名）：

| 用途 | 图标语义 | Lucide 参考 |
|---|---|---|
| 说话 | 对话气泡 | `message-circle` |
| 打字聊天 | 键盘 | `keyboard` |
| 随机动作 | 胶片 / 骰子 | `clapperboard` / `dices` |
| 识别屏幕 | 扫描框 | `scan-line` |
| 语音对话 | 麦克风 | `mic` |
| 静音 | 喇叭× | `volume-x` |
| 取消静音 | 喇叭 | `volume-2` |
| 设置 | 齿轮（细描边版） | `settings` |
| 退出 | 门 + 箭头 | `log-out` |
| 勿扰 | 月亮 | `moon` |
| 锁位 | 锁 | `lock` |
| 复制 | 双方块 | `copy` |
| 朗读 | 声波 | `audio-lines` |
| 上一句 / 下一句 | 上下尖括号 | `chevron-up` / `chevron-down` |
| 发送 | 纸飞机 | `send` |
| 关闭 | × | `x` |
| 帮助 | 问号圆 | `circle-help` |

全部图标收进 `frontend/assets/icons/*.svg`，文件名 = 上表 Lucide 名（如 `message-circle.svg`），便于审计与替换。

---

## 10. 可访问性视觉规范

- **焦点环**：所有可交互元素 `:focus-visible` 时绘制 `1px dashed var(--accent)`，向外偏移 2px（`outline-offset: 2px`），圆角随元素；禁止 `outline: none` 而无替代。
- **高对比模式**：`@media (prefers-contrast: more)` 下——`--fg` 提升为 `#ffffff`，`--fg-dim` 提升为 `#d4d0c4`，`--line` 提升为 `rgba(201,168,106,0.55)`，`--bg-panel` alpha 提到 0.97。通过 CSS 变量覆写实现，不改组件代码。
- **色彩不依赖**：所有状态同时提供**色 + 形 + 文**三通道——chip 永远是"圆点（色）+ 文字标签（文）+ 胶囊形（形）"；录音中额外有呼吸动画（形的变化）；危险项在菜单里同时有颜色与图标差异。不允许出现"只靠颜色区分"的纯圆点（v0.2 的 7×7px 圆点因此废弃）。
- **减少动效**：见 §6.3 末条，全局瞬时切换。
- **键盘可达**：菜单、抽屉、引导滑层全部 `Esc` 关闭 + Tab 顺序合理（DOM 顺序即 Tab 顺序，禁止 `tabindex > 0`）。

---

## 11. 设计 token 汇总（可直接复制）

```css
:root {
  /* ── 色彩 ── */
  --fg: #e8e2d4;
  --fg-dim: #9a968a;
  --fg-faint: rgba(232, 226, 212, 0.25);
  --accent: #c9a86a;
  --accent-dim: rgba(201, 168, 106, 0.55);
  --accent-glow: rgba(201, 168, 106, 0.14);
  --accent-bright: #d4b57e;              /* 仅发送按钮 hover */
  --ok: #7fb069;
  --danger: #c96a6a;
  --warn: #d9a24a;
  --bg-panel: rgba(16, 22, 28, 0.92);
  --bg-panel-hover: rgba(26, 34, 42, 0.94);
  --bg-panel-active: rgba(34, 44, 54, 0.95);
  --line: rgba(201, 168, 106, 0.28);
  --line-strong: rgba(201, 168, 106, 0.50);
  --line-faint: rgba(201, 168, 106, 0.14);

  /* ── 字体 ── */
  --font-serif: "Georgia", "Songti SC", "SimSun", "STSong", serif;
  --font-sans: var(--font-serif);        /* 旧名别名，v0.4 移除 */
  --font-mono: "Consolas", "Courier New", monospace;
  --fs-chip: 10px;
  --fs-caption: 11px;
  --fs-small: 12px;
  --fs-body: 13px;
  --fs-bubble: 14px;
  --fs-title: 16px;
  --fs-heading: 18px;
  --lh-tight: 1.4;
  --lh-normal: 1.55;
  --lh-loose: 1.7;

  /* ── 间距（4px 栅格）── */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 24px;
  --space-6: 32px;

  /* ── 圆角 ── */
  --radius-chip: 999px;
  --radius-card: 8px;
  --radius-bubble: 10px;
  --radius-drawer: 12px;

  /* ── 阴影 ── */
  --shadow-s1: 0 4px 12px rgba(0, 0, 0, 0.35);
  --shadow-s2: 0 6px 24px rgba(0, 0, 0, 0.45);
  --shadow-s3: 0 10px 32px rgba(0, 0, 0, 0.55);
  --shadow-s4: 0 20px 60px rgba(0, 0, 0, 0.65);

  /* ── 动效 ── */
  --dur-fast: 120ms;
  --dur-mid: 200ms;
  --dur-slow: 350ms;
  --dur-xslow: 600ms;
  --ease-standard: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-enter: cubic-bezier(0, 0, 0.2, 1);
  --ease-exit: cubic-bezier(0.4, 0, 1, 1);
}

/* 高对比模式覆写 */
@media (prefers-contrast: more) {
  :root {
    --fg: #ffffff;
    --fg-dim: #d4d0c4;
    --line: rgba(201, 168, 106, 0.55);
    --bg-panel: rgba(16, 22, 28, 0.97);
  }
}

/* 减少动效：全局瞬时切换 */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## 附：与交互规格的 token 对齐清单

供文策渊文档引用（禁止硬编码值）：

- 颜色：`--fg / --fg-dim / --fg-faint / --accent / --accent-dim / --accent-glow / --accent-bright / --ok / --danger / --warn / --bg-panel / --bg-panel-hover / --bg-panel-active / --line / --line-strong / --line-faint`
- 字体：`--font-serif / --font-mono`、`--fs-chip / --fs-caption / --fs-small / --fs-body / --fs-bubble / --fs-title / --fs-heading`、`--lh-tight / --lh-normal / --lh-loose`
- 间距：`--space-1 … --space-6`
- 圆角：`--radius-chip / --radius-card / --radius-bubble / --radius-drawer`
- 阴影：`--shadow-s1 … --shadow-s4`
- 动效：`--dur-fast / --dur-mid / --dur-slow / --dur-xslow`、`--ease-standard / --ease-enter / --ease-exit`
