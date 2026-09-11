# 桌面宠物 v0.3 呈现层重设计 · 实施总计划

> 汇编：游承峰（Orchestrator）· 日期：2026-08-14
> 输入：`docs/design/pet-v0.3-INDEX.md`（索引）、`pet-presentation-spec-v0.3.md`（呈现规范，379 行全文通读）、
> `pet-visual-styleboard-v0.3.md`（视觉风格板，§11 token 全文核对）
> 子计划：`plan-spec-v0.3.md`（文策渊 · 工程实施方案）、`plan-visual-v0.3.md`（林绘澄 · 视觉资源清单）
> 状态：**计划定稿，待用户拍板 Q1–Q5 后进入实施**

---

## 0. 冲突定稿（实施前必须拍板；子计划发现 + 主理人二进制实测核验）

| # | 冲突 | 证据 | 裁定 |
|---|---|---|---|
| C1 | 勿扰透明度 0.45（规范 §6.2/§11）vs **0.55**（规范 §6.1/风格板 §7.7/INDEX Rev1） | 已核对原文 | **取 0.55**；实施时同步修正规范陈旧值 |
| C2 | **Spine 情绪动画命名错源**：风格板 §8.5 用 `bm_hy01/06、cm_hy03/09、zm_*` | 二进制实测：这些名字只存在于**完整版** fight/room/ui 骨骼；**简化版**（512²，宠物默认）不含 | 风格板 §8.5 表作废重填；以 s_room 实况为准（见下方动画清单） |
| C3 | ~~呈现规范 §2.1 动画名笔误~~ | **实测撤回**：`bian4、cx3/cx5/cx6、idle、st、j1~j4` 均真实存在于 s_room.skel（早期提取因过滤规则误删）；规范 §2.1 名字基本准确，仅补 `idle/st/j1~j4/cx2` 等 | 规范 §2.1 名字可采信；语义仍需巡检页实播定稿 |
| C4 | 默认窗口 320×420（规范）vs `config.js` 现状 420×560 | 已核对 config.js DEFAULTS | P0 改默认 **320×420**（M4/E5） |
| C5 | 气泡 max-width 92%（规范 §4.1）vs 88%（风格板 §7.1）；缩放范围 0.5~1.5 vs 0.7~1.4；引导遮罩 rgba(0,0,0,.55) vs rgba(8,10,14,0.72) | 已核对原文 | 取「呈现规范值为主、风格板为皮肤」；代码统一走 token |
| C6 | **断点表偏差**：规范 §3.3 = S 320×420 / M 420×560 / L 480×640，宽阈值 380/460；视觉子计划误写为 M 400×480 / L 480×560、阈值 400/480 | 已核对两份文档 | **以规范 §3.3 为准**（S 320×420 / M 420×560 / L 480×640，<380 / 380~460 / >460）；视觉子计划 §4 表作废重抄 |
| C7 | **z-index 数值偏差**：规范 §3.2（模型0/品牌5/状态5/气泡10/输入15/菜单20/抽屉30/引导40）vs 视觉子计划 §2.0（气泡10/常驻15/输入20/菜单40/抽屉60/引导80） | 顺序一致、数值不同 | **以规范 §3.2 数值为准**（与命中优先级表绑定，且现 pet.html 已按此落位）；视觉子计划仅作层级顺序参考 |

### 0.1 简化版骨骼动画实测清单（2026-08-14 二进制提取，供 P0 巡检页与映射表使用）

**`314701_wmz_s_room.skel`（默认人偶用）候选动画名**：
`idle、st、st2~st7、j1、j2、j23、j3、j4、bian、bian2、bian3、bian4、cs2、cx2、cx3、cx5、cx6、djc1、djc2、hua、mao、sc1、wei、target、target2、target3、xc1~xc4、xiangzishang、zm、x_ls_deng、x_ls_he_di、x_ls_he_gai1~4、x_ls_he_shang、x_ls_jinxian1~12(+90)`
（注：其中 `zm`、`j*`、`st*` 等也可能含骨骼/插槽名，**巡检页必须以 skeleton.data.animations 实际枚举为准**）

**`s_ui.skel` 独有**：`born`（出场）等；**`s_fight.skel` 独有**：`born`、`jump`（跳跃）等。

> **结论**：C2 是唯一实质性的动画命名冲突（风格板误用完整版名）；语义映射（哪个动画=开心/难过/行走）仍全部以 P0 巡检页实播为准——「P0-T1 巡检 + P0-T2 语义表」是不可跳过的全局前置依赖。

---

## 1. 目标与范围

- 把桌面宠物从"半截 Live2D 大模型 + 3 个灰点"重设计为
  **"小尺寸 Spine 人偶 + 品牌条 + 状态 chip + 打字输入条 + 5 步新手引导"**；
- 默认窗口 **320×420**（三档 S/M/L：<380 / 380~460 / >460），延续"暴雨之前"古风暗黑视觉语言；
- 覆盖审查报告 P0（#1–4）、P1（#5–10）、P2（#11–20）；P3 结构性项不在本版；
- **改动边界**（规范 §1.2）：`frontend/pet.html`、`frontend/js/pet.js`、新增 `frontend/assets/spine/`、
  主进程仅做必要 IPC 扩展（锁位/勿扰/多屏摆位/窗口档位）；**不动** `/chat/stream`、`/api/voice/*`、`/api/llm/*`。

## 2. 关键决策（已定，来自 INDEX §3）

1. 渲染选型：首选 `pixi-spine`（@esotericsoftware/spine-pixi 4.2，与现有 PIXI 栈共享 GL 上下文，可编程控制 animationState）；
   `spine-player.js` 为降级 fallback（整段切换、允许 1 帧硬切）。两条路径统一收敛在 pet.js 的 `SpinePet` 适配器后，
   行为接口（walk/idle/emotion/click/sleep/entry）与 Live2D 模式一致。
2. 默认窗口 320×420；Live2D 对话模式强制 ≥420×560。
3. 人偶定位：水平居中、垂直居中偏下；头顶留白 = 窗口高 8%（硬约束，气泡占位）；脚底落地线 = 下沿 −16px；
   缩放 = min(舞台可用高 / 骨骼自然高) × 0.92。
4. 状态机九态（闲置/漫步/拖拽/聆听/思考/说话/睡眠 + 勿扰/锁位正交修饰态）；睡眠沿用 90s/5min 分级。
5. 勿扰：透明度 0.55（INDEX §5 裁定值）、禁声、漫步暂停、chip 呼吸；锁位：拖拽失效、长按 1.5s 解锁。
6. emoji 图标全退役 → SVG 描边 1.5px 金铜（16 个，Lucide 同语义）。
7. 输入条展开抢焦点 + 8s 自动收起（已接受的取舍，Q1 建议维持）。

## 3. 素材准备（一次性）

| # | 动作 | 落点 |
|---|---|---|
| M1 | 从素材包复制 `314701_wmz_s_room.skel` + `314701_wmz_s.atlas` + `314701_wmz_s.png` + `314701_wmz_s_bloom.png` | `frontend/assets/spine/`（不改名） |
| M2 | 获取 pixi-spine 运行时（@esotericsoftware/spine-pixi 4.2 + spine-core 4.2；评估用 npmmirror 拉 npm 包或从素材库 viewer/lib 方案对齐） | `frontend/assets/lib/` |
| M3 | 兜底运行时 `spine-player.js` 原样复制自素材库 `viewer/lib/` | `frontend/assets/lib/` |
| M4 | 桌面端默认窗口配置 420×560 → **320×420** | `desktop/src/main/config.js` DEFAULTS.pet |

## 4. 实施分期（P0 → P1 → P2，每期验收见 §7）

### P0（必做）——"半截模型"变"完整人偶"

| # | 任务 | 涉及文件 | 依赖 | 验收 |
|---|---|---|---|---|
| P0-T1 | **动画巡检页**：临时页加载 s_room.skel，下拉逐个实播 30+ 动画（zm*/bm_hy/cm_hy/target/posture/skill/bian/djc/hua/xc/x_ls/xiangzishang/mao/cs2…），确认语义 | 新增 `frontend/pet-anim-inspector.html`（临时，验收后可保留为调试页） | M1/M2 | §2.1 ⚠️ 表全部去 ⚠️ |
| P0-T2 | **动画语义表定稿**：回填 `animation_map.json`（行为槽位 → 动画名），作为 SpinePet 与 Live2D 对照的唯一来源 | 新增 `frontend/assets/spine/animation_map.json`；更新规范 §2.1/§2.4 | P0-T1 | 表与实播一致 |
| P0-T3 | **SpinePet 适配器**：加载 skel+atlas、居中偏下定位（§2.3/风格板 §8.2）、walk/idle/emotion/click/sleep/entry 接口、flipX 行走方向、zoom | 新增 `frontend/js/pet-spine.js`；`pet.js` 引入双渲染器选择（默认 Spine） | P0-T2 | 320×420 下头/肩/手完整可见、落地线 −16px |
| P0-T4 | **三档布局 + 窗口档位**：S/M/L 断点样式；主进程 resize IPC + 设置切档 | `pet.html`（+CSS）、`desktop/src/main/windows.js`/`index.js`、preload `resizeWindow` | P0-T3 | 三档切换后定位重算正确 |
| P0-T5 | **品牌条 + 状态 chip 四枚**：chip 高 20px、圆点+文字（S 档收起为圆点+计数）、悬停诊断 tooltip、异常可点击重试、勿扰 chip 动态 | `pet.html`/`pet.js`（现有 chip 升级） | — | 四枚 chip 状态机正确 |
| P0-T6 | **输入条升级**：折叠态 = 右下 32px 圆钮 ✎；展开 36px 条；8s 自动收起；Ctrl+Enter 展开；Enter 走 SSE | `pet.html`/`pet.js`（现有输入栏升级） | — | 三种展开方式 + 自动收起 |
| P0-T7 | **气泡基础**：打字机（逐字+光标 ▍）、完成 4~9s 淡出、悬停暂停、位置翻转（头顶不足翻到下方、尾巴指头）、多行滚动 | `pet.html`/`pet.js` | — | 与 §4.1 一致 |
| P0-T8 | **5 步新手引导滑层**（替换现有气泡式 onboarding）：260px 卡片、步骤点、上一步/下一步/跳过、配图槽位 200×140、`role=dialog` | `pet.html`/`pet.js`（重写 startOnboarding） | — | 完成/跳过写标记、设置可重看 |
| P0-T9 | **CSS token 落地**：风格板 §11 `:root` 全量 token 进入宠物页；样式组织方案按视觉子计划定（独立 pet.css vs 内联） | `pet.html`/新增 `frontend/css/pet.css` | — | token 与风格板一致、无硬编码色值 |

### P1（强化）

| # | 任务 | 涉及文件 | 验收 |
|---|---|---|---|
| P1-T1 | 右键菜单三组（互动/感知/系统）+ 16 个 SVG 图标替换 emoji + 快捷键 hint | `pet.html`/`pet.js` | 无 emoji、分组正确 |
| P1-T2 | 设置抽屉五 tab（模型/对话/语音/屏幕识别/桌面端）卡片化 + range 实时数值 + "已生效✓" | `pet.html`/`pet.js` | 五 tab 全量可改可存 |
| P1-T3 | 勿扰模式：透明度 0.55、禁声、漫步暂停、chip 呼吸、30 分钟自动解除选项 | `pet.js` + 主进程 walker 联动 | §11 对应项 |
| P1-T4 | 锁位模式：拖拽失效、锁位 chip、长按 1.5s 解锁、拖拽尝试播 djc1 摇头 + toast | `pet.js` + preload | §11 对应项 |
| P1-T5 | 状态机九态完整实现（含睡眠序列 he_shang→he_di→deng、聆听减速 50%、说话气泡尾巴摆动） | `pet.js`（state-machine 独立模块化） | §6.1 逐态对照 |
| P1-T6 | OCR 气泡首句摘要 +「详细」折叠；三档节流已有，补提示 | `pet.js` | P1-9 |
| P1-T7 | 多屏摆位：设置选主屏/副屏/指定坐标；副屏断开回主屏 | 主进程 `windows.js`/`config.js` | Q3 默认策略 |
| P1-T8 | `?` 帮助气泡（快捷键一览）、Alt+Space 常驻提示 | `pet.html`/`pet.js` | P1-4 |

### P2（打磨）

| # | 任务 | 涉及文件 | 验收 |
|---|---|---|---|
| P2-T1 | 入场动画 cs2 + 窗口淡入（~2s） | `pet-spine.js`/`pet.js` | 启动即入场 |
| P2-T2 | 气泡操作行：上一句/下一句/复制/朗读/✕；历史 20 条 + ↑↓ 翻页 | `pet.html`/`pet.js` | P2-9/14/19 |
| P2-T3 | 底栏控制条（输入条外露时让位） | `pet.html` | P2-1 |
| P2-T4 | 跟随光标 / 跟随活动窗口（两种陪伴模式开关） | 主进程 + `pet.js` | P2-15/16 |
| P2-T5 | 主聊天页宠物预览卡（顶栏状态点悬停弹出状态小卡） | `frontend/index.html`/`js/desktop-pet.js` | P2-16 |
| P2-T6 | 截图分享（人偶+气泡合成 PNG，导出走系统保存对话框） | `pet.js` + 主进程 dialog | 零自动落盘 |
| P2-T7 | `prefers-reduced-motion` 全量降级（入场改淡入、打字机关、漫步瞬移、呼吸静止） | `pet.html` CSS/`pet.js` | §8 对应项 |

## 5. 主进程扩展点（最小改动面）

| # | 扩展 | 落点 |
|---|---|---|
| E1 | 窗口档位 S/M/L + resize IPC（含 min 320×420 / max 480×640 约束；Live2D 模式强制 ≥420×560） | `windows.js`、`config.js`、preload `petApi.resizeWindow(size)` |
| E2 | 勿扰状态持久化 + 漫步暂停联动（`pet:busy` 已有，扩展语义为 `pet:mode {dnd}`） | `index.js`、`behavior.js`、`config.js` |
| E3 | 锁位：`pet:locked` → 主进程忽略 move-by（或渲染层不发） | `index.js`（渲染层主导，主进程仅存状态） |
| E4 | 多屏摆位：设置写入 `pet.screen = primary|secondary|{x,y}`，启动/切换时应用；副屏断开回主屏 | `windows.js`、`config.js` |
| E5 | 默认窗口 320×420（M4） | `config.js` |

## 6. 风险与缓解

| 风险 | 缓解 |
|---|---|
| pixi-spine 与 .skel 4.2 二进制不兼容 | fallback spine-player.js（SpinePet 内双实现，统一接口） |
| bloom 贴图在透明窗的混合表现异常 | 设置「模型辉光」开关（风格板 §8.1） |
| 动画语义推测偏差（Q5） | P0-T1 巡检页首日实播回填，允许文档小修订 |
| 输入条抢焦点影响穿透体验 | 8s 自动收起 + Esc（Q1 维持） |
| 素材复制引入体积 | s_room 全套 <1MB，可忽略 |
| token 与 index.html 现有变量同名冲突 | 视觉子计划给出命名空间/合并方案（宠物页独立作用域，不污染主页） |

## 7. 验收清单（QA 可勾选，转自规范 §11）

- [ ] 320×420 默认档下 Spine 人偶头/肩/手/表情完整可见，头顶留白 ≈8%，脚底落地线 −16px
- [ ] 漫步时 target 动画与窗口位移同步、flipX 方向正确
- [ ] 品牌条常显；chip 带文字（M/L）、悬停诊断、异常可点击重试
- [ ] 输入条三入口展开（菜单/圆钮/Ctrl+Enter）、Enter 走 SSE、Esc 收起、8s 自动收起
- [ ] 引导滑层 5 步逐步/跳过、标记持久化、设置可重看
- [ ] 菜单三组 + SVG 图标、无 emoji、贴边翻转
- [ ] 设置五 tab 全量可改可存，桌面端项写 config.json 重启生效
- [ ] 勿扰 0.55 透明/禁声/漫步暂停/chip；锁位拖拽失效 + 长按 1.5s 解锁
- [ ] 九态视觉与 §6.1 一致；修饰态正交叠加
- [ ] OCR 摘要气泡 +「详细」折叠；三档节流生效
- [ ] 键盘全路径可达；reduced-motion 降级
- [ ] 仅回环网络；截图零落盘（导出除外）
- [ ] 切 Live2D 对话模式后 420×560 大模型完整可见、情感联动正常

## 8. 开放问题（Q1–Q5，待用户拍板）

| # | 问题 | 规范建议 | 我的倾向 |
|---|---|---|---|
| Q1 | 输入条展开抢焦点 vs 独立小窗 | 维持抢焦点+8s 收起 | ✅ 同意（实现简单、无额外窗口） |
| Q2 | 唤醒词是否纳入 v1.1 | 本版只做提示 | ✅ 同意（工作量 2~3d，后置） |
| Q3 | 副屏断开迁移 | 回主屏原位 | ✅ 同意（简单可预期） |
| Q4 | 截图分享范围 | 仅人偶+气泡 | ✅ 同意（隐私面最小） |
| Q5 | 动画语义表推测 | P0 巡检实播回填 | ✅ 同意，P0-T1 首日做 |

## 9. 实施顺序（推荐）

1. **P0-T1 动画巡检页**（全部映射的前置依赖）→ **P0-T2 语义表** → **P0-T3 SpinePet** → P0-T4~T9 并行铺开；
2. P0 验收 → P1（菜单/设置/勿扰/锁位/状态机）→ P2（打磨）;
3. 每期结束跑：前端语法检查 + 后端 pytest 回归 + Electron 实机冒烟（窗口/穿透/漫步/对话）。

## 10. 子计划索引

- 工程实施方案（文件级任务单）：`docs/design/plan-spec-v0.3.md`（文策渊）
- 视觉资源清单（token/图标/组件规格/CSS 组织）：`docs/design/plan-visual-v0.3.md`（林绘澄）

---

## 11. 实施状态（2026-08-14 更新）

### ✅ P0 完成
- T1 素材落位 + 巡检页（`pet-inspect.html`/`js/pet-inspect.js`）· T2 语义表种子（`animation_map.json`/`expression_map.json`，**待用户巡检实播定稿**）· T3 `js/spine.js` SpinePet 适配器（低层 SpineCanvas 全控制）· 默认切 Spine（Live2D 对话模式）· T4 三档布局 + resize IPC + 默认 320×420 · T5 品牌条 + chip 四枚 · T6 输入条（折叠圆钮/Ctrl+Enter/8s 自动收起）· T7 气泡打字机 + aria · T8 五步引导滑层 · T9 全量 token 落地。

### ✅ P1 完成
- 菜单三组 + 19 枚 SVG sprite 图标（emoji 全退役）· 设置五 tab 卡片化（模型/对话/语音/屏幕识别/桌面端，桌面端项写 config.json）· 勿扰（0.55/禁声/漫步暂停/30min 自动解除）· 锁位（moveBy 守卫/长按 1.5s 解锁/虚线框+chip/拖拽尝试反馈）· 睡眠分级（90s 浅睡/5min 深睡/交互唤醒）· OCR 摘要气泡 · 多屏摆位（getDisplays/moveToDisplay/重置位置）· `?` 帮助气泡 + 菜单快捷键 hint。

### ✅ P2 完成
- 入场淡入 + `enter()` 动作（cs2 暂定映射）· 气泡操作行（复制/朗读/上一句/下一句/✕ + 20 条历史 + ↑↓ 翻页）· 跟随光标模式（设置「桌面端」tab，200ms lerp，拖拽后 1.5s 内不跟随）· 主页顶栏悬停状态卡（/state 接口）· 截图分享（人偶+气泡合成 PNG → 系统保存对话框，零自动落盘）。

### ⏳ 遗留（不阻塞交付）
1. **动画语义表定稿**：需用户在 `pet-inspect.html` 实播标注后回填（C2 裁定）。
2. 底栏控制条（P2-2 简化：由折叠圆钮 + 菜单覆盖）。
3. 跟随活动窗口（P2 仅实现跟随光标）。
4. pixi-spine 主方案替换 spine-player 降级运行时（当前 SpineCanvas 已够用，可后置）。
5. 独立 `pet.css`/`tokens.css` 拆分（当前 token 已内联 pet.html，语义一致）。

### 验收证据
- 后端 pytest：344 passed（全程无回归）；全部 JS 语法检查通过；
- Electron 实机：320×420 透明置顶窗运行、Spine 人偶渲染、拖拽/漫步/对话/语音/OCR/勿扰/锁位链路接通、控制服务 /ping /state /launch /talk 正常、无崩溃日志。
