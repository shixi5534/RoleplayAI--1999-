# 无名者桌面宠物 · 视觉资源实施清单 v0.3

> 编制：视觉实施工程师 · 林绘澄
> 依据：`C:\Users\Lenovo\WorkBuddy\2026-07-27-16-45-03\roleplay-ai\docs\design\pet-visual-styleboard-v0.3.md`（§11 token / §7 组件 / §8 Spine / §9 图标）
> 性质：**计划文档** —— 只给清单与方案，不改任何现有代码。
> 对照现状：`frontend\pet.html`（内联 `<style>`）、`frontend\index.html`（"暴雨之前"视觉语言 3.0）、`frontend\assets\lib\`（pixi/live2d，无 spine 运行时）、Spine 素材目录（简化版 512² + 完整版）。

---

## 0. 关键结论（先读）

1. **token 冲突的本质**：`pet.html` 与 `index.html` 是两个独立 HTML 文档，各自内联 `<style>`，**不存在级联覆盖冲突**；"同名冲突"是**语义漂移**（同名不同值），集中在 `--fg-dim / --line / --line-strong / --font-mono` 四处。合并方案见 §1.2。
2. **Spine 动画名重大偏差（必须传达给文策渊）**：风格板 §8.5 表情映射表用的是**完整版（初始皮肤）**命名 `bm_hy* / cm_hy* / zm*`；而宠物 v0.3 默认渲染的 **512² 简化版** 骨骼里**没有**这些名字，实际动画名是 `idle / st~st7 / j1~j4 / bian~bian4 / mao / hua / xc1~xc4 / cx2~cx6 / cs2 / djc1~djc2 / wei / target~target3 / born / jump / x_ls_*`。表情映射必须按简化版实况重建（§5.5 占位表）。
3. **图标"16"的拆解**：风格板 §9 表格 17 行，但「静音/取消静音」「上一句/下一句」各为**同一槽位双态**，去重后正好 **16 个图标槽位**（§3）。
4. **图标 token 染色**：外部 `<img src="icons/*.svg">` 会丢失 `currentColor` 继承（外部 SVG 是独立文档），**必须用 inline SVG 或 sprite `<use>`**；§9 的 `assets/icons/*.svg` 仅作源文件存档与审计。CSP 允许 inline SVG（§3.3 判断）。
5. **CSS 组织**：推荐拆出 `frontend\css\pet.css`（外链，CSP 的 `style-src 'self' 'unsafe-inline'` 同时放行外链与内联），token 抽到 `frontend\css\tokens.css` 与 index 共享语义层（§6）。

---

## 1. 完整 Design Token 清单

### 1.1 `:root` 变量块（风格板 §11 原样转录，可直接复制）

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

### 1.2 与 `index.html` 现有 `--bg-0/--bg-1/--fg/--accent` 体系的同名冲突与合并

`index.html :root`（暗色）关键值：

| index token | 值 |
|---|---|
| `--bg-0` | `#0c1014` |
| `--bg-1` | `#10161c` |
| `--bg-2` | `#161e26` |
| `--line` | `rgba(201,168,106,0.14)` |
| `--line-strong` | `rgba(201,168,106,0.32)` |
| `--fg` | `#e8e2d4` |
| `--fg-dim` | `#8d8a7e` |
| `--accent` | `#c9a86a` |
| `--accent-strong` | `#b08d4f` |
| `--accent-ink` | `#1a1408` |
| `--accent-tint` | `rgba(201,168,106,0.13)` |
| `--danger` | `#c96a6a` |
| `--radius-sm/md/pill` | `4px / 8px / 999px` |
| `--font-sans` | `"Georgia","Songti SC","SimSun","STSong",serif` |
| `--font-mono` | `"Courier New", ui-monospace, "Cascadia Mono", Menlo, monospace` |

逐 token 对照结论：

| 风格板 token | 风格板值 | index 同名 token | index 值 | 结论 | 处理 |
|---|---|---|---|---|---|
| `--fg` | `#e8e2d4` | `--fg` | `#e8e2d4` | ✅ 值一致 | 共享，无冲突 |
| `--fg-dim` | `#9a968a` | `--fg-dim` | `#8d8a7e` | ⚠️ **冲突（值不同）** | 宠物采用风格板值（更亮，宠物窗更小需更可读）；若共享文件，隔离为 `--pet-fg-dim` |
| `--fg-faint` | 新增 | — | — | ➕ 新增 | 宠物专属，无冲突 |
| `--accent` | `#c9a86a` | `--accent` | `#c9a86a` | ✅ 值一致 | 共享 |
| `--accent-dim` | 新增 | — | — | ➕ 新增 | 宠物专属 |
| `--accent-glow` | `0.14` | `--accent-tint` | `0.13` | ⚠️ **语义重叠、值差 0.01** | 二者是同一用途（hover 底）；建议统一为 `--accent-tint`，宠物侧别名 `--accent-glow: var(--accent-tint)` |
| `--accent-bright` | `#d4b57e` | — | — | ➕ 新增 | 宠物专属；对应 index `--accent-strong`(#b08d4f) 的"提亮"变体，非同名 |
| `--ok` | 新增 | — | — | ➕ 新增 | index 用 `--accent` 表成功，宠物用 `--ok`，无冲突 |
| `--danger` | `#c96a6a` | `--danger` | `#c96a6a` | ✅ 值一致 | 共享 |
| `--warn` | 新增 | — | — | ➕ 新增 | 宠物专属 |
| `--bg-panel` | `rgba(16,22,28,0.92)` | `--bg-1` | `#10161c` | ℹ️ **实色等价**（`16,22,28`=`#10161c`） | `--bg-panel` 的实色 = index `--bg-1`；建议改为 `--bg-panel: color-mix(...)` 或写 `rgba(16,22,28,0.92)` 并在注释标注"实色 = --bg-1" |
| `--bg-panel-hover/active` | 新增 | — | — | ➕ 新增 | 宠物专属 |
| `--line` | `0.28` | `--line` | `0.14` | ⚠️ **冲突（值不同，宠物更亮）** | 宠物采用 0.28；共享文件时隔离为 `--pet-line` |
| `--line-strong` | `0.50` | `--line-strong` | `0.32` | ⚠️ **冲突（值不同）** | 同上，隔离为 `--pet-line-strong` |
| `--line-faint` | `0.14` | `--line` | `0.14` | ⚠️ **值撞车**：宠物"最弱描边" = index"常规描边" | 命名不同、值相同；合并时注意 `--line-faint` 不可直接映射到 index `--line`，避免语义混淆 |
| `--font-serif` / `--font-sans` | 改名 + 别名 | `--font-sans` | 同值 | ✅ 值一致（宠物 v0.3 把 `--font-sans` 改名为 `--font-serif`，旧名留别名一版） | 共享；v0.4 移除旧名时同步删 index 的 `--font-sans` |
| `--font-mono` | `"Consolas","Courier New",monospace` | `--font-mono` | `"Courier New",ui-monospace,...` | ⚠️ 轻微差异 | 建议统一为 index 版（更完整 fallback），宠物追加 `Consolas` 即可 |
| `--space-1…6` | 新增 | — | — | ➕ 新增 | 宠物专属，index 无间距 token 体系 |
| `--radius-chip/card/bubble/drawer` | 新增 | `--radius-sm/md/pill` | `4/8/999` | ℹ️ 语义对应、命名不同 | `--radius-card`(8)=index `--radius-md`；`--radius-chip`(999)=index `--radius-pill`；宠物多出 `bubble`(10)/`drawer`(12) 两档 |
| `--shadow-s1…s4` | 新增 | — | — | ➕ 新增 | 宠物专属（index 未定义阴影 token，阴影硬编码在组件里） |
| `--dur-*` / `--ease-*` | 新增 | — | — | ➕ 新增 | 宠物专属（index 动效硬编码 0.18s/0.3s） |

**合并 / 命名空间隔离建议（二选一）：**

- **方案 A（推荐，两页真正统一）**：新建 `frontend\css\tokens.css` 作为唯一 token 源，只放**值一致**的共享 token（`--fg / --accent / --danger / --font-serif / --radius-card / --radius-chip` 等）。冲突项一律**命名空间隔离**：宠物侧用 `--pet-line / --pet-line-strong / --pet-fg-dim / --pet-line-faint` 等前缀，在 `pet.css` 顶部 `:root{ --line: var(--pet-line); … }` 做本地别名，index 侧继续用原 `--line` 值。这样两页可同时 `<link>` 同一 `tokens.css` 而互不污染。
- **方案 B（最小改动，接受差异）**：两页继续各自内联/各自外链，宠物 `:root` 整体替换为 §1.1 块；对 4 处冲突 token 在注释中写明 index 对应值（`/* index: --line=0.14 */`），防止未来误"统一"。工作量最小，但"延续但统一"目标只达成一半。

> 决策建议：**方案 A** 落地 `tokens.css`（共享 `--fg/--accent/--danger/--font-serif` 等无冲突项）+ 宠物专属前缀隔离冲突项。优先级 P1（非阻塞，P0 可先用方案 B 跑通，再迁移）。

---

## 2. 组件视觉规格表

> 结构/状态机以文策渊《交互呈现规格 v0.3》为准，本节只定**皮肤**。所有尺寸 4px 栅格对齐。

### 2.0 z-index 层级栈（全局约定）

| 层 | z-index | 元素 | 现 pet.html 值 |
|---|---|---|---|
| 底 | 0 | 模型画布 `#pet-canvas`、锁位虚线框 `#pet-lockframe` | 无（canvas 无 z-index） |
| 气泡 | 10 | `#pet-bubble` | 无（当前被 status 压住） |
| 常驻 | 15 | `#pet-brand` 品牌条、`#pet-status` chips | 5 / 5 |
| 输入 | 20 | `#pet-inputbar` | 15 |
| 提示 | 25 | `#browser-hint` | 无 |
| 菜单 | 40 | `#pet-menu` | 20 |
| 抽屉 | 60 | `#pet-settings` | 30 |
| 模态 | 80 | `#pet-onboarding` 引导滑层 | 无（新增） |
| 通知 | 90 | `.toast` | 50 |

### 2.1 气泡 `#pet-bubble`

| 属性 | 值 |
|---|---|
| 尺寸 | `max-width: 88%`（320 窗 ≈ 280px）；`min-width: 120px`；最多 4 行，超出 `overflow-y: auto`（滚动条宽 4px，滑块 `--line`） |
| 间距 | `padding: 10px 14px`（纵 `--space-3` + 横 14px 微调）；与模型头顶净距 ≥ `--space-2`(8px)；锚定 `top: var(--space-2)` |
| 圆角 | `--radius-bubble`(10px) |
| 边框 | `1px solid var(--line)`；尾巴 `::after` 10×10 方块旋转 45°（下边框+右边框），朝下居中，翻转到上时改 `top:-6px` + `border-left`+`border-top` |
| 背景 | `--bg-panel` |
| 字号 | `--fs-bubble`(14px) / `--lh-normal`(1.55)，颜色 `--fg` |
| 阴影 | `--shadow-s2` |
| 光标 | 正文末尾 `│`（`--accent`），530ms `steps(1)` 闪烁，流式结束移除 |
| 辅助按钮 | 右下内嵌一行，12×12 SVG，间距 `--space-2`，默认 `opacity 0.5`，hover 单个 `opacity 1` + `--accent-glow` 圆角 4px 底 |
| 动效-入 | `opacity 0→1` + `translateY(4px→0)`，`var(--dur-mid) var(--ease-enter)` |
| 动效-出 | 反向，`var(--dur-mid) var(--ease-exit)` |
| 收窄兜底 | 窗口高 < 380px 时 `max-width: 76%` + 启用滚动，绝不下压至模型面部（包围盒上 40%） |
| z-index | 10 |

### 2.2 品牌条 `#pet-brand`

| 属性 | 值 |
|---|---|
| 尺寸/间距 | 极细一行；`top: --space-1`、`left: --space-2` |
| 背景/边框 | 无底无框 |
| 字号 | `--fs-chip`(10px)，字距 `0.2em`（统一 token，替代现 0.22em），颜色 `rgba(232,226,212,0.55)`（`--fg` 的 0.55 透明度） |
| 强调 | `<b>` 金铜 `--accent`，`font-weight: normal` |
| 阴影 | `text-shadow: 0 1px 3px rgba(0,0,0,0.6)` |
| 动效 | 无（常驻，`pointer-events:none`） |
| z-index | 15 |

### 2.3 状态 chip `#pet-status .chip`

| 属性 | 值 |
|---|---|
| 尺寸 | 高 20px；圆点 6×6px；`padding: 4px 8px`；dot↔文字 5px |
| 间距 | 右上角纵向堆叠，chip 间 `--space-2`，右对齐；容器 `top/right: --space-2` |
| 圆角 | `--radius-chip`(999px) |
| 边框 | `1px solid var(--line-faint)` |
| 背景 | `rgba(12,16,20,0.66)`（≈ `--bg-0` 实色 66%） |
| 字号 | `--fs-chip`(10px)，字距 `0.08em`；颜色 `--fg-dim` |
| 状态映射 | ok：dot `--ok` + 字 `--fg`；bad：dot `--danger` + 字 `--danger`；warn：dot `--warn` + 字 `--warn`；dim（勿扰/睡眠）：dot+字 `--fg-dim` + 描边 `--line-faint` |
| hover | 底升 `--bg-panel-hover` + `--shadow-s1` + 显示 tooltip（`--fs-caption`，底 `--bg-panel`） |
| 动效 | 显隐 `--dur-mid`；录音 dot 呼吸 1200ms（见 §2.9） |
| 废弃 | `.dot` 独立用法（7×7 裸圆点）删除，圆点只作 `.chip` 子元素 |
| z-index | 15 |

### 2.4 右键菜单 `#pet-menu`

| 属性 | 值 |
|---|---|
| 尺寸 | `min-width: 172px`；菜单项高 36px（`padding: 0 14px`）；整体 `padding: 5px 0` |
| 间距 | 图标↔文字 9px；分隔线上下 `--space-1`、左右内缩 `--space-2` |
| 圆角 | `--radius-card`(8px) |
| 边框 | `1px solid var(--line)`；分隔线 1px 高 `--line-faint` |
| 背景 | `--bg-panel` |
| 字号 | `--fs-small`(12px) / `--lh-tight`(1.4)，颜色 `--fg` |
| 图标 | 16×16 SVG 描边，`--accent`；危险项 `--danger` |
| hover | 底 `--accent-glow`；危险项 hover 底 `rgba(201,106,106,0.12)` |
| 快捷键 | 项右 `--font-mono` 10px `--fg-dim`（如 `Alt+Space`） |
| 禁用项 | `opacity 0.4` + 图标描边降 `--fg-faint` |
| 阴影 | `--shadow-s3` |
| 动效 | 开合 `--dur-mid`（`--ease-enter` 入 / `--ease-exit` 出） |
| z-index | 40 |

### 2.5 设置抽屉 `#pet-settings`（五 tab）

| 属性 | 值 |
|---|---|
| 布局 | 全窗覆盖，`--radius-drawer`(12px) 四角露透明边；`padding: --space-4`；`overflow-y: auto` |
| 背景 | `rgba(12,16,20,0.94)`（≈ `--bg-0` 实色 94%，略深于 `--bg-panel` 压住后方模型） |
| 边框 | `1px solid var(--line)` |
| 阴影 | `--shadow-s3` |
| tab bar | 高 32px，底 1px `--line` 分隔；tab 字 `--fs-small`，未激活 `--fg-dim`，激活 `--accent` + 底 2px `--line-strong` 指示条；tab 间距 `--space-4` |
| 分组卡片 | 底 `rgba(22,30,38,0.6)`，描边 `--line-faint`，圆角 `--radius-card`，`padding: --space-3 --space-4`，纵向间距 `--space-3`；卡片标题 `--fs-caption` `--fg-dim` 字距 0.2em |
| 控件 | select/number/range/开关 高 28px，底 `rgba(22,30,38,0.9)`，描边 `--line`，focus `--line-strong`；range 滑块圆 12px 底 `--accent`；开关 32×18 胶囊，on 底 `--accent-dim` + 圆点 `--accent` |
| 行密度 | 行高 28px + 上下 `--space-1`；label 左 `--fg-dim`，控件右；行间 `--space-2` |
| 关闭按钮 | 右上 18×18 "×" SVG（`--fg-dim`，hover `--fg`） |
| 字号 | 正文 `--fs-body`(13px) / `--lh-loose`(1.7)；label `--fs-small`(12px) |
| 动效 | 滑入 `--dur-slow`（350ms）`--ease-enter`；卡片展开 `--dur-slow` |
| z-index | 60 |

> 五 tab 名与内容由文策渊交互规格定义；皮肤规格（上表）对五 tab 一致。

### 2.6 输入条 `#pet-inputbar`

| 属性 | 值 |
|---|---|
| 折叠态 | 高 36px，底部居中宽 160px 胶囊；底 `--bg-panel`，描边 `--line`，圆角 `--radius-chip`；左 18×18 键盘 icon（`--accent`），右 placeholder"说点什么…"（`--fs-small` `--fg-dim`）；hover 描边升 `--line-strong` + `--shadow-s1` |
| 展开态 | 占满窗宽（左右 `--space-2`，`bottom: --space-2`），高 36px；输入底 `rgba(16,22,28,0.94)`，描边 `--line`，focus 描边 `--accent` |
| 发送按钮 | 32×32 方形，圆角 `--radius-card`，底 `--accent`，图标 16×16 描边 `#1a1408`（深底反色）；hover 底 `--accent-bright`(`#d4b57e`) |
| 字号 | 输入 `--fs-body`(13px)；placeholder `--fs-small` |
| 动效 | 折叠↔展开：宽度 + 透明度，`var(--dur-mid) var(--ease-enter)` |
| z-index | 20 |

### 2.7 新手引导滑层 `#pet-onboarding`

| 属性 | 值 |
|---|---|
| 遮罩 | 全窗 `rgba(8,10,14,0.72)` backdrop |
| 卡片 | 宽 260px；底 `--bg-panel`，描边 `--line`，圆角 `--radius-drawer`，阴影 `--shadow-s4`，`padding: --space-5 --space-4` |
| 标题 | `--fs-heading`(18px) `--accent` 字距 0.2em |
| 描述 | `--fs-body`(13px) `--fg` `--lh-loose` |
| 配图区 | 200×140px 占位框，1px 虚线 `--fg-faint`，圆角 `--radius-card`；留空时中央 12px `--fg-faint` 文字"示意图" |
| 进度点 | 5 个 6×6px，当前 `--accent` 实色，其余 `--fg-faint`，间距 `--space-2` |
| 按钮 | 「下一步」胶囊（底 `--accent`，字 `#1a1408`，`--fs-small`，`padding 6px 14px`）；「跳过」文字按钮（`--fg-dim`，hover `--fg`） |
| 动效 | 步骤切换 `translateX(12px→0)` + 淡入，`var(--dur-xslow) var(--ease-enter)`；欢迎入场 `--dur-xslow` |
| z-index | 80 |

### 2.8 勿扰模式视觉

| 属性 | 值 |
|---|---|
| 模型 | 整体 `opacity 0.55`，过渡 `var(--dur-slow) ease` |
| chips | 全降 dim 态；勿扰 chip 显示"勿扰"并常显（不随其余 chip 自动隐藏） |
| 气泡 | 禁弹新气泡；正在显示者以 `--ease-exit` 收起 |
| 菜单 | 保留，顶部插一行"勿扰中 · 点击解除"（`--fg-dim`，可点击），下加分隔线 |
| 输入条 | 折叠态保留可用 |
| z-index | 不变 |

### 2.9 锁位模式视觉

| 属性 | 值 |
|---|---|
| 虚线框 | 窗口内边距 `--space-2` 处 `1px dashed var(--line-strong)` 矩形，圆角 4px；8s 周期 `stroke-dashoffset` 顺时针流动（reduced-motion 静止） |
| 锁位 chip | 12×12 锁形 SVG（`--accent`）+ 文字"已锁位"，追加进状态区 |
| 拖拽反馈 | 光标 `not-allowed`；虚线框描边闪烁一次（`--line-strong → --accent → --line-strong`，`--dur-mid`） |
| z-index | 虚线框 0（衬底）；锁位 chip 随状态区 15 |

### 2.10 录音圆点呼吸（跨组件动效）

| 属性 | 值 |
|---|---|
| 动画 | `opacity 1→0.35→1`，1200ms 循环，`--ease-standard` |
| 停止条件 | 勿扰/睡眠、`prefers-reduced-motion` 时停闪改常亮 |

---

## 3. 16 个 SVG 图标清单

> 风格板 §9 表格 17 行；「静音/取消静音」「上一句/下一句」各为同一槽位双态，去重后 **16 个独立槽位**。

### 3.1 图标清单

| # | 文件名（Lucide 名） | 语义 | 出现位置 | 尺寸 | 描边色 |
|---|---|---|---|---|---|
| 1 | `message-circle` | 说话/对话气泡 | 右键菜单「说话」项 | 16×16 | `--accent` |
| 2 | `keyboard` | 打字聊天 | 右键菜单「打字聊天」项 + 输入条折叠态左 icon | 16 / 18 | `--accent` |
| 3 | `dices`（备 `clapperboard`） | 随机动作 | 右键菜单「随机动作」项 | 16×16 | `--accent` |
| 4 | `scan-line` | 识别屏幕 | 右键菜单「识别屏幕」项 | 16×16 | `--accent` |
| 5 | `mic` | 语音对话/麦克风 | 右键菜单「语音对话」项 | 16×16 | `--accent` |
| 6 | `volume-x` ↔ `volume-2` | 静音/取消静音（双态） | 右键菜单「静音」项动态切换 | 16×16 | `--accent` |
| 7 | `settings` | 设置 | 右键菜单「设置」项 | 16×16 | `--accent` |
| 8 | `log-out` | 退出 | 右键菜单「退出」项（危险） | 16×16 | `--danger` |
| 9 | `moon` | 勿扰 | 右键菜单「勿扰」项 | 16×16 | `--accent` |
| 10 | `lock` | 锁位 | 右键菜单「锁位」项 + 锁位 chip | 16 / 12 | `--accent` |
| 11 | `copy` | 复制 | 气泡辅助按钮 | 12×12 | `--accent` |
| 12 | `audio-lines` | 朗读 | 气泡辅助按钮 | 12×12 | `--accent` |
| 13 | `chevron-up` / `chevron-down` | 上一句/下一句（双态） | 气泡辅助按钮 / 历史切换 | 12×12 | `--accent` |
| 14 | `send` | 发送 | 输入条发送按钮 | 16×16 | `#1a1408`（深底反色） |
| 15 | `x` | 关闭 | 抽屉右上角 / 气泡关闭 | 18 / 12 | `--fg-dim`→hover `--fg` |
| 16 | `circle-help` | 帮助 | 引导滑层 / 菜单帮助项 | 16×16 | `--accent` |

### 3.2 统一 SVG 模板

```html
<svg viewBox="0 0 24 24" width="16" height="16" fill="none"
     stroke="currentColor" stroke-width="1.5"
     stroke-linecap="round" stroke-linejoin="round"
     aria-hidden="true" focusable="false">
  <!-- 引用 Lucide / Feather / Heroicons 同语义 path 体 -->
</svg>
```

规则：
- `viewBox` 统一 `0 0 24 24`，用 `width/height` 缩放，`stroke-width` 恒 1.5。
- 描边色一律 `currentColor` + CSS `color: var(--accent)` 控制；危险项 `color: var(--danger)`；禁用项 `color: var(--fg-faint)`。金铜色**通过 CSS 变量流进 `currentColor`**，path 上不写任何色值。
- 禁止保留库默认黑（stroke/fill 硬编码）。

### 3.3 组织方式（inline vs sprite，CSP 判断）

- **CSP 判定**：现 CSP（`C:\Users\Lenovo\WorkBuddy\2026-07-27-16-45-03\roleplay-ai\src\roleplay\middleware.py`）= `style-src 'self' 'unsafe-inline'` + `script-src 'self' 'unsafe-eval'`（**无 `unsafe-inline` 脚本**）。**inline `<svg>` 在 HTML 内是标记而非脚本，不触发 `script-src` 限制；其 `stroke`/`fill` 是 SVG 展示属性而非样式，也不受 `style-src` 拦截**。结论：**inline SVG 可行**，与 `index.html` 现有内联线性 SVG 用法一致，沿用即可。
- **推荐方案**：SVG sprite —— 页头放一个 `<svg style="display:none"><symbol id="i-mic" viewBox="0 0 24 24">…</symbol>…</svg>`，组件用 `<svg class="ico"><use href="#i-mic"/></svg>` + `.ico{color:var(--accent)}`。`currentColor` 会穿透 `<use>` 进入 symbol，兼顾去重与 token 染色。
- **不推荐**：外部 `<img src="assets/icons/mic.svg">` —— 外部 SVG 经 `<img>` 渲染为独立文档，**无法继承父级 CSS `color`**，`currentColor` 回退默认黑，破坏 token 控制。故 §9 的"收进 `frontend\assets\icons\*.svg`"只作为**源文件存档与审计**（文件名 = Lucide 名），运行时用 sprite/inline 注入，不进 `<img>`。

---

## 4. 三档断点 S / M / L 样式策略

> 断点按窗口宽度预设划分。标「出处=风格板」的是 §4/§7 明文；标「建议」的是本清单推导、需 P0 微调确认。

| 断点 | 窗口预设（宽×高） | 触发 |
|---|---|---|
| **S** | 320×420（默认） | 宽 < 400px |
| **M** | 400×480（可选预设） | 400 ≤ 宽 < 480 |
| **L** | 480×560（放大预设） | 宽 ≥ 480px |

| 组件属性 | S (320×420) | M (400×480) | L (480×560) | 出处 |
|---|---|---|---|---|
| 窗口内边距（抽屉/定位基准） | 12px `--space-3` | 12px `--space-3` | 16px `--space-4` | 风格板 §4 |
| 气泡 `max-width` | 88%（≈280px） | 84%（≈336px） | 80%（≈384px） | §7.1 + 建议 |
| 气泡正文字号 | 14px `--fs-bubble` | 14px | 15px（建议，M 保持 14） | §7.1 + 建议 |
| 气泡 padding | 10px 14px | 10px 14px | 12px 16px（建议） | §7.1 + 建议 |
| chip 高/圆点/字号 | 20px / 6px / 10px | 不变 | 不变 | §7.4 固定 |
| 菜单 `min-width` | 172px | 180px（建议） | 188px（建议） | §7.2 + 建议 |
| 菜单项高 | 36px | 36px | 36px | §7.2 固定 |
| 输入条高 | 36px | 36px | 36px | §7.5 固定 |
| 输入条左右留白 | 8px `--space-2` | 8px | 12px（建议） | §7.5 + 建议 |
| 抽屉内边距 | 12px | 12px | 16px `--space-4` | §4 |
| 引导卡片宽 | 260px | 260px | 260px（居中） | §7.6 固定 |
| 模型缩放基准 | zoom 1.0 → 280×360 | 按窗口高等比 | 按窗口高等比 | §8.3 |

规则：
- 字号阶梯三档**基本不动**（`--fs-*` 固定），断点只调**比例尺寸与留白**——保持"人偶私语"的克制，不随窗口放大而放大字号。
- 窗口尺寸变化时，模型按高度等比缩放，头顶 8% / 脚下 16px 两规则优先于 zoom 绝对值（§8.3）。

---

## 5. Spine 适配视觉要求

> 素材源：`C:\Users\Lenovo\WorkBuddy\2026-07-26-22-28-10\viewer-data\03_动态资源\Spine战斗\Spine战斗_314701_简化版\`
> 完整版：`…\Spine战斗_314701_初始皮肤\`（仅表情名参考，宠物 P0 用简化版）

### 5.1 素材文件清单（简化版 512²）

| 文件 | 用途 |
|---|---|
| `314701_wmz_s.png` | 512×512 主贴图（atlas 声明 `scale:0.7`，为打包缩放，运行时自动处理，**不重打包不缩放**） |
| `314701_wmz_s.atlas` | atlas 描述 |
| `314701_wmz_s_bloom.png` | bloom 叠加发光层（烛火/金饰自发光） |
| `314701_wmz_s_room.skel` | 桌面待机/表情/行走（**P0 主用**） |
| `314701_wmz_s_ui.skel` | UI 交互（含 `born` 出场） |
| `314701_wmz_s_fight.skel` | 战斗（含 `born`/`jump`） |

### 5.2 窗口内定位（默认 320×420，与 §8.2 一致）

| 参数 | 值 |
|---|---|
| 水平 | 居中 |
| 垂直 | 居中偏下 |
| 头顶留白 | 窗口高 **8%**（420 高 ≈ 33px） |
| 脚下对齐 | 窗口下沿 **-16px**（脚底线距窗口底 16px，给输入条折叠态留悬浮空间） |
| 左右边距 | 各 ≥ 12px；超界自动缩回最大适配值 |
| 气泡净距 | 气泡底沿到模型头顶包围盒 ≥ 8px（§7.1） |

### 5.3 缩放

| 参数 | 值 |
|---|---|
| 默认 zoom | `1.0` → 320×420 窗下渲染 ≈ **280×360px** |
| 用户范围 | 0.7–1.4，步进 0.05，实时预览，松手按 §5.2 重新吸附 |
| 窗口变化 | 按高度等比，头顶 8% / 脚下 16px 优先于 zoom 绝对值 |

### 5.4 bloom 辉光与透明窗混合

| 项 | 要求 |
|---|---|
| bloom 层 | `314701_wmz_s_bloom.png` 叠加在模型之上，混合 `screen`（CSS `mix-blend-mode: screen` 或 pixi/spine ADD/SCREEN blend），**不透明度 0.6** |
| 开关 | 设置项"模型辉光"默认开；运行时性能不足允许整层关闭 |
| 显存 | 常驻 < 32MB；512² RGBA ≈ 1MB × 2 层，远低于预算，不压缩 |
| 透明窗注意 | ① `body{background:transparent}` 前提下，`screen` 混合在**透明像素区域无效果**（不会出现整块白/黑底），但需保证 bloom 纹理 **premultiplied alpha 一致**，否则半透明金饰边缘出现黑边/白边；② bloom 只表达自发光、不承担形体，关闭后形体仍完整；③ 拖拽/移动时 bloom 层随模型同 transform，避免辉光漂移 |

### 5.5 表情映射占位表（骨骼内动画名 → 待回填语义）

> ⚠️ **核对结论（重要）**：风格板 §8.5 用的 `bm_hy* / cm_hy* / zm* / posture_* / skill* / birthday*` 命名**只存在于完整版（初始皮肤）骨骼**（`314701_wmz_room.skel` 295KB / `_ui.skel` 213KB）。宠物 v0.3 使用的 **512² 简化版**（`314701_wmz_s_*.skel`，room 仅 32KB）**不含这些名字**。实施 P0 必须按简化版实况重建映射，并回填到 `frontend\assets\spine\expression_map.json`（与 Live2D `interact_map.json` 平级）。

**简化版实际动画名（从 skel 二进制字符串提取，非臆测）**：

| 类别 | 骨骼内动画名 | 待回填语义 |
|---|---|---|
| 待机/站立 | `idle` | 默认待机（确认） |
| 站立姿势 | `st`, `st2`, `st3`, `st4`, `st5`, `st6`, `st7` | 待核对各姿势差异，选作姿势池 |
| 手部/小动作 | `j1`, `j2`, `j23`, `j3`, `j4` | 待核对动作语义 |
| 表情/情绪候选 | `bian`, `bian2`, `bian3`, `bian4` | 待核对（风格板提示 `bian1` 蹲坐可作睡眠替代） |
| 表情/情绪候选 | `mao`, `hua`, `wei` | 待核对（发饰/花/尾动作） |
| 表情/情绪候选 | `xc1`, `xc2`, `xc3`, `xc4` | 待核对 |
| 表情/情绪候选 | `cx2`, `cx3`, `cx5`, `cx6`, `cs2` | 待核对（`cx` 疑为"笑"系） |
| 表情/情绪候选 | `djc1`, `djc2` | 待核对（疑偏头/疑惑） |
| 移动 | `target`, `target2`, `target3` | 行走/漫步（确认，对应交互规格移动池） |
| 特殊 | `born` | 出场/召唤（在 `_ui.skel` 与 `_fight.skel`，供欢迎动画 P2-2） |
| 特殊 | `jump` | 跳跃（在 `_fight.skel`） |
| 道具 | `x_ls_deng`, `x_ls_he_di`, `x_ls_he_gai1~gai4`, `x_ls_he_shang`, `x_ls_jinxian1~12` | 小笼子道具动画（灯/盒子/金线），P0 可不用 |

**情感事件 → 简化版候选映射（两列占位，语义待查看器回填）**：

| 情感事件 | Live2D 表情 | 简化版候选动画名（待回填定稿） | 备注 |
|---|---|---|---|
| 微笑/开心 | `e_weixiao` | `cx2` / `xc1`（疑"笑"系，待核对） | TTS 收尾手势 |
| 难过/委屈 | `e_nanguo` | `bian2`（疑垂头，待核对） | 持续 4s 回待机 |
| 疑惑/聆听 | `e_yihuo` | `djc1` / `cs2`（疑偏头，待核对） | 录音中常驻 |
| 严肃/认真 | `e_yansu` | 待核对（`st*` 站姿变体候选） | 提醒类文案 |
| 面具/营业态 | `e_mianju` | `xc1` / `hua`（标准微笑候选） | 勿扰解除首句 |
| 待机 | `e_idle` | `idle`（确认）+ `st`~`st7` 池轮播 8~18s | — |
| 睡眠 | 闭眼低头 | `bian` 蹲坐替代（风格板已提示，待核对） | 90s/5min 分级 |

> 完整版（初始皮肤）动画名存档供参考：`zm1~zm85`、`zm_bz/qz/yj/ys/zj/zs` 系列、`bm_hy1~33`、`cm_hy1~39`、`posture_ys/ys1~5`、`posture_zs/zs1~4`、`target1~8/targetx/targetz`、`skill1/skill2/skill22`、`birthday/birthday1/3`、`idle_room/idle_birthday_loop/idle_birthday_up`、`born`。

### 5.6 运行时缺口

| 项 | 现状 | 实施动作 |
|---|---|---|
| Spine 运行时 | `assets\lib\` 仅 pixi/live2d，**无 spine 运行时** | P0 引入 spine-webgl/spine-ts 运行时到 `frontend\assets\lib\`（CSP `script-src 'self' 'unsafe-eval'` 已兼容） |
| 素材落位 | 素材在 `2026-07-26-22-28-10\viewer-data\…` 外部目录 | 拷贝简化版 4 文件到 `frontend\assets\spine\` |
| 表达式映射 | 无 `expression_map.json` | P0 用查看器回填后落盘 |

---

## 6. CSS 文件组织方案

### 6.1 是否拆分 `frontend\css\pet.css`

- **CSP 兼容性**：现 CSP `style-src 'self' 'unsafe-inline'` **同时放行**外链同源 CSS（`'self'`）与内联 `<style>`（`'unsafe-inline'`）。二者皆合法，无 CSP 障碍。
- **推荐**：拆出 `frontend\css\pet.css`（外链），理由：① 与 pet.html 解耦、可缓存、便于 token 迁移；② 组件规格表（§2）体量大，内联会显著拉长 pet.html。**不引入 FOUC 风险**：宠物窗常驻、首屏非关键路径，且可保留一个最小内联 `:root` token 块做首屏兜底。
- **token 层**：新建 `frontend\css\tokens.css` 放共享 token（§1.2 方案 A），pet.css 顶部 `:root` 只写宠物专属/隔离 token + 别名。
- **与 index.html 内联 `<style>` 的取舍**：index.html 页面复杂、单页、已内联 1400 行，**本次不动**（重构成本高、无收益）；仅当未来做主题系统时再迁 index 到外链。pet 侧先行外链，两页通过 `tokens.css` 共享语义层即可。

### 6.2 旧样式迁移清单

**保留（类名不变，仅替换值为 token）**：

| 类名/ID | 处理 |
|---|---|
| `#pet-bubble` | 保留，规格按 §2.1 |
| `#pet-menu` | 保留，规格按 §2.4 |
| `#pet-settings` | 保留，规格按 §2.5 |
| `#pet-inputbar` | 保留，规格按 §2.6 |
| `#pet-status` | 保留，规格按 §2.3 |
| `#pet-brand` | 保留，规格按 §2.2 |
| `#browser-hint` | 保留 |
| `.toast` | 保留（voice.js 动态创建） |

**改名**：

| 旧名 | 新名 | 原因 |
|---|---|---|
| `.dot` | （废弃，仅作 `.chip .dot` 子元素） | v0.2 7×7 裸圆点废除（§7.4） |
| `#live2d-canvas` | `#pet-canvas` | 渲染器从 Live2D 切 Spine，容器应渲染器无关 |
| `.live2d-loading` | `.model-loading` | 同上 |
| `.live2d-status` | `.model-status` | 同上 |
| `.live2d-loading .spinner` | `.model-loading .spinner` | 同上 |

**删除**：

| 项 | 原因 |
|---|---|
| `#pet-bubble.typing::after { content:"…" }` | 打字机光标改 `│` 字符闪烁（§6.3/§7.1） |
| 菜单 emoji 前缀 `💬 ⌨️ 🎬 🔍 🎙️ 🔇 ⚙️ ✕` | 全部替换为 16×16 SVG 图标（§3） |
| `#live2d-loading` / `#live2d-status` 的 Live2D 专用文案/结构 | Spine 化后由 `.model-*` 承接 |
| 输入条发送按钮文字"发送" | 改 16×16 `send` SVG 图标（§7.5） |

**新增**：

| 项 | 说明 |
|---|---|
| `#pet-onboarding` | 新手引导滑层（§2.7） |
| `#pet-lockframe` | 锁位虚线框（§2.9） |
| `.chip.warn` / `.chip.dim` | 状态修饰（§2.3） |
| `.chip-lock` | 锁位 chip（§2.9） |
| `.bubble-actions` | 气泡辅助按钮行（§2.1） |
| `.ico` | 通用图标类（`color` 控制 `currentColor`，§3.3） |
| 各组件 `:focus-visible` 焦点环 | `1px dashed var(--accent)` + `outline-offset:2px`（§10） |

---

## 7. 验收清单

### 7.1 token 与一致性

- [ ] pet 侧 `:root` 完整包含 §1.1 全部 token，无遗漏（色彩 16 / 字体字号行高 13 / 间距 6 / 圆角 4 / 阴影 4 / 动效 8）
- [ ] 4 处冲突 token（`--fg-dim / --line / --line-strong / --font-mono`）按 §1.2 决策处理，注释标注 index 对应值
- [ ] `--font-sans` 别名存在，旧代码不改也能跑
- [ ] 组件样式**零硬编码色值/像素**，一律 `var(--token)`（文策渊文档同理）
- [ ] 所有尺寸为 4 的倍数（4px 栅格）

### 7.2 组件

- [ ] 气泡：`max-width 88%`、`min-width 120px`、padding 10px 14px、圆角 10px、阴影 s2、尾巴指向模型头顶、4 行滚动（滚动条 4px `--line`）
- [ ] 气泡打字机光标 `│` 530ms `steps(1)` 闪烁，流式结束移除
- [ ] 气泡辅助按钮（关闭/复制/朗读）12×12，默认 0.5，hover 1 + glow
- [ ] 菜单：min-width 172px、项高 36px、分隔线 `--line-faint`、危险项 hover 红底、快捷键 mono 10px
- [ ] 抽屉：全窗覆盖 0.94 深底、tab bar 32px + 2px 激活指示、分组卡片化、控件 28px、关闭 × 18px
- [ ] chip：高 20px、圆点 6px、padding 4px 8px、四态（ok/bad/warn/dim）色形文三通道
- [ ] 输入条：折叠胶囊 36px/160px、展开满宽、发送按钮 32×32 底 `--accent`、hover `--accent-bright`
- [ ] 引导滑层：遮罩 0.72、卡片 260px、配图 200×140 虚线框、进度点 5 个、翻页 `--dur-xslow`
- [ ] 勿扰：模型 0.55、chips 全 dim、气泡收起、菜单顶部解除行
- [ ] 锁位：虚线框 1px dashed `--line-strong` 8s 流动、锁位 chip、拖拽 not-allowed + 描边闪烁
- [ ] z-index 按 §2.0 层级栈落位（模型 0 / 气泡 10 / 常驻 15 / 输入 20 / 菜单 40 / 抽屉 60 / 引导 80 / toast 90）

### 7.3 图标

- [ ] 16 槽位齐全，viewBox `0 0 24 24`、stroke 1.5、`stroke-linecap/linejoin round`、`fill:none`
- [ ] 全部 `stroke="currentColor"`，无库默认黑；金铜经 `color: var(--accent)` 流入
- [ ] 危险项 `--danger`、禁用项 `--fg-faint`、发送 `#1a1408` 反色
- [ ] 采用 inline 或 sprite `<use>`（**不用** `<img src=…>`）
- [ ] `assets/icons/*.svg` 源文件归档，文件名 = Lucide 名

### 7.4 响应式断点

- [ ] S/M/L 三档按 §4 表生效；字号阶梯三档不动；≥480 宽内边距切 16px
- [ ] 窗口高 < 380px 气泡收窄 76% + 滚动，不下压模型面部

### 7.5 Spine

- [ ] 简化版 4 文件（png/atlas/room.skel/bloom.png）拷贝到 `frontend\assets\spine\`
- [ ] 头顶 8%（≈33px）、脚下 -16px、左右 ≥12px、zoom 1.0 → 280×360
- [ ] bloom `screen` 混合 + opacity 0.6，默认开、可关、无黑边/白边
- [ ] `expression_map.json` 用**简化版实况动画名**回填（§5.5），不用 bm_hy/cm_hy/zm 名
- [ ] spine 运行时引入 `assets\lib\`（CSP 兼容）
- [ ] 显存预算 < 32MB

### 7.6 可访问性

- [ ] `:focus-visible` 焦点环 `1px dashed var(--accent)` + `outline-offset:2px`，无 `outline:none` 无替代
- [ ] `prefers-contrast: more` 覆写（fg 白 / fg-dim 亮 / line 0.55 / bg-panel 0.97）
- [ ] `prefers-reduced-motion: reduce` 全局 0.01ms 瞬时；呼吸/打字光标改常亮；锁位虚线静止
- [ ] 状态三通道（色+形+文），无纯圆点
- [ ] 菜单/抽屉/引导 `Esc` 关闭；DOM 顺序 = Tab 顺序，无 `tabindex > 0`
- [ ] 对比度达标：`--fg` 13.2:1、`--accent` 7.4:1、`--danger` 4.9:1（≥4.5:1）；`--fg-faint` 只用于装饰/禁用，不承载信息

### 7.7 CSS 组织

- [ ] `frontend\css\pet.css` 外链引入（CSP `'self'` 放行）
- [ ] `frontend\css\tokens.css` 共享层建立（方案 A）
- [ ] 旧样式迁移清单（§6.2）执行：保留 8 项、改名 4 项、删除 4 项、新增 7 项
