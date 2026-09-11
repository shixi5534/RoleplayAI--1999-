# 桌面宠物（Desktop Pet）设计方案 v0.2

> 状态：**设计稿（未实施）** —— 本文档只做设计，不修改任何代码。
> **v0.2 定位修正**：桌面宠物是**网页版（roleplay-ai）的附属功能**，不是独立重写的新应用。
> Electron 只做「浏览器做不到的事」（悬浮窗/穿透/全局快捷键/截图），
> Live2D、对话、情感、语音、模型切换**全部直接复用网页版现有代码**。

---

## 0. 设计原则（v0.2 核心）

1. **页面即功能**：宠物窗口加载的就是网页版自己的页面 `http://127.0.0.1:8000/pet.html`，
   与 `index.html` 同源、同后端、同资产，**零复制**（Live2D 模型、JS 模块、后端接口全部共享）。
2. **Electron 只做壳**：透明无边框置顶窗、点击穿透、窗口拖拽/漫步（物理）、全局快捷键（按住说话）、
   屏幕截图+OCR、托盘、协议唤起、回环控制服务、后端拉起。
3. **复用 > 新增**：能调网页现有模块就绝不重写；新增代码仅三处——①网页版加一个 `pet.html` 宠物页
   （新页面，但内部全是既有模块）；②`chat.js` 做**一次小重构**暴露编程接口（index.html 行为不变）；
   ③`desktop/` Electron 壳（不含任何业务逻辑）。
4. **后端零改动（v1）**：宠物走网页版全部现有接口（`/chat/stream`、`/api/voice/*`、`/api/llm/*`）。
5. **Ollama 强制本地**：复用 `llm-switch.js` 的请求级覆盖机制，宠物页强制 `provider=ollama`，
   从机制上杜绝调用远程 API（后端 `build_llm_from_config` 已支持，零改动）。

---

## 1. 总体架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       网页版 roleplay-ai（现有，几乎不动）                   │
│  FastAPI :8000 ── /chat/stream · /api/voice/* · /api/llm/* · 静态托管      │
│  frontend/ ── index.html（聊天页）  +【新增】pet.html（宠物页）             │
│       js/ ── live2d.js · chat.js · voice.js · llm-switch.js · knowledge.js │
│             ↑ 全部被宠物页直接复用                                        │
└──────────────────────────────▲───────────────────────────────────────────┘
                               │ http://127.0.0.1:8000/pet.html（同源加载）
┌──────────────────────────────┴───────────────────────────────────────────┐
│              Electron 壳（新增，desktop/，不含任何业务逻辑）                 │
│  主进程：悬浮窗管理 · 点击穿透 · 窗口拖拽/漫步物理 · 全局快捷键(按住说话)      │
│          桌面截图+OCR(tesseract.js) · 托盘 · roleplaypet:// 协议             │
│          Loopback 控制服务(127.0.0.1:39231) · 后端拉起(uvicorn) · 配置存储   │
│  preload：contextBridge 暴露 petApi（窗口移动/穿透状态/截图/按键事件/设置）   │
└─────────────────────────────────────────────────────────────────────────┘
```

- **宠物渲染进程 = 加载网页版 `pet.html`**。Live2D 渲染、SSE 对话、情感事件、语音全部走网页版
  既有的 `RoleplayLive2D` / `RoleplayChat` / `RoleplayVoice` / `RoleplayLLM` 模块。
- **网页按钮唤起**：`index.html` 顶栏加「🖥️ 桌面宠物」按钮（§6）。
- **Electron 与页面通信**：preload 注入 `window.petApi`（`contextIsolation: true` 的白名单桥）;
  页面在浏览器中打开时 `petApi` 不存在 → 宠物页自动降级为“网页内嵌模式”（功能子集，不报错）。

---

## 2. 复用清单（对现有代码的实际盘点结果）

| 现有模块 | 全局入口 | 宠物复用点（已验证存在） |
|---|---|---|
| `frontend/js/live2d.js` | `window.RoleplayLive2D` | `init({containerId,…})`、`getModels()`、`switchModel(id)`、`setZoom()`、`setVisible()`、`setOffset()`、`resetPosition()`、`playGesture(name, prio)`、`playExpression(name)`、`onEmotionEvent(d)`、`notifyUserInteract()`；**已内置**：鼠标拖拽模型（`live2d:offset` 事件）、双击复位、待机加权动作池（8~18s 随机）、点击区域互动（`interact_map.json`）、空闲分级睡眠（90s/5min）、情绪表情自动恢复、TTS 收尾手势、扇子变体池 |
| `frontend/js/chat.js` | （IIFE，页内私有 `sendMessage`） | **v0.2 唯一重构点**：把 SSE 核心抽取为 `window.RoleplayChat.send(text, opts)`（opts 提供气泡/情绪/完成的 DOM 钩子），`index.html` 现有行为完全不变，`pet.html` 传自己的气泡钩子 |
| `frontend/js/voice.js` | `window.RoleplayVoice` | `init()`、`startRecording()`、`stopRecording()`、`speak(text, opts)`、`stopSpeaking()`、`getSettings()`、`isRecording()`、`isSpeaking()`——MediaRecorder 录音 → `/api/voice/stt`（faster-whisper 本地识别，**whisper 多语言模型天然支持中英自动检测**）；`/api/voice/tts` 合成播放 |
| `frontend/js/llm-switch.js` | `window.RoleplayLLM` | `buildOverride()`（请求级 provider/model/base_url 覆盖，后端已有实现）——宠物页构造“永远 ollama”的 override；`onChanged(cb)`、HUD 显示 |
| `frontend/js/knowledge.js` | `window.KnowledgePanel` | （可选）宠物页不加载，不干扰 |
| `frontend/js/live2d-bootstrap.js` | — | 加载状态/错误提示，直接复用 |
| `frontend/assets/lib/*` | pixi / cubismcore / pixi-live2d-display | 同一套库文件，同源加载 |
| `frontend/assets/live2d/*` | 314701 / 314702 模型+动作+表情 | 同一目录，零复制 |
| 后端 `src/roleplay/**` | FastAPI | **完全不动**：`/chat/stream`（SSE chunk/emotion/done）、`/api/voice/stt`、`/api/voice/tts`、`/api/llm/*`、静态托管 `/pet.html`；Ollama provider、faster-whisper、edge-tts 均已实现 |

**结论**：原需求里“拖拽、待机动作、点击反馈、情感联动、语音输入输出、多轮对话、模型切换”
网页版**已经实现了 80%**，桌面端只需把它们装进一个会“穿透+置顶+能动窗口”的浏览器壳里。

### 2.1 素材库盘点（2026-07-26 素材包实际核查结果）

核查范围：`C:\Users\Lenovo\WorkBuddy\2026-07-26-22-28-10\`（viewer / viewer-data / 素材包三处）。

| 素材 | 数量 | 结论 |
|---|---|---|
| Live2D 模型 | 仅 2 套（314701 初始皮肤 / 314702 无尽且唯一的路） | 动作 24/25 个 + 表情 6 个，**与网页版 `frontend/assets` 已完全一致**；全库无其他 Live2D 小模型 |
| **Spine 4.2 骨骼（战斗版）** | 每角色 3 套骨骼：fight / room / ui（共享 2048×512 贴图） | **每套骨骼内含 100+ 动画**：`zm1~zm85` 站立姿势、`bm_hy×18`+`cm_hy×19` 表情动画、`posture_ys/zs×9`、`target1~8`（房间寻路/移动）、`skill1/2`、`birthday×4`、`hudie` |
| **Spine 简化版（小模型）** | 仅 314701 有：`314701_wmz_s_{fight,room,ui}.skel` + **512×512 小贴图**（原版 2048×512） | `s_room.skel` 含 **46 个房间互动动画**：`target/target2/3`（移动）、`x_ls_he_shang/…`（上下楼梯类）、`xc1-4`、`xiangzishang`（箱子上）、`mao`、`bian1-3`、`hua` 等 —— **这就是用户记忆中的“小模型 + 更多动作”** |
| Spine 剧情立绘 | 3 套（624901 / 533803 / 533903） | NPC 立绘，桌面宠物暂不用 |
| 运行时 | 素材库自带 `viewer/lib/spine-player.js`（Spine 4.2 官方 Web 播放器，597KB） | **可直接复用**，与现有 pixi/live2d lib 放一起，同源加载 |
| 音频资源 | `04_音频资源` 目录为空（本源缺失） | 语音不走素材库，沿用网页版 TTS/语音方案 |

**对设计的三个修正**：

1. **桌面宠物默认渲染形态改为 Spine 小模型**（简化版 room 骨骼）：贴图小（512²）、动画多（46 个房间动作，含 `target` 移动动画），
   天然适合悬浮窗性能与“行走/待机/互动”需求；Live2D 大厅模型作为**对话主视觉/大模型模式**（情感表情联动已在网页版打磨成熟）供用户切换。
2. **“行走动画”问题解决**：room 骨骼的 `target1~8`（原版）与 `target/target2/3`（简化版）就是房间寻路移动动画，
   漫步时播放 target 动画 + 窗口 lerp 移动，不再是“只能窗口滑动”。
3. 渲染层因此设计为**双渲染器**（见 §5.2）：`spine.js`（宠物小模型，动作丰富）与 `live2d.js`（对话大模型，情感联动），
   两者都复用素材包已验证的运行时（spine-player.js / pixi-live2d-display），宠物页按设置切换。

---

## 3. 新增/小改清单（v0.2 的全部代码改动）

| # | 位置 | 改动 | 量级 |
|---|---|---|---|
| 1 | `frontend/chat.js` | 抽取 `window.RoleplayChat.send(text, opts)` 公开 API（SSE 解析、手势触发、情绪事件、LLM 覆盖、错误处理逻辑原样保留；气泡/typing/追问渲染改为 opts 钩子，index.html 传原实现） | 小重构，行为零变化 |
| 2 | `frontend/pet.html` + `frontend/js/pet.js` + 样式 | 新宠物页：Live2D 舞台（复用 RoleplayLive2D）+ 气泡 + 右键菜单 + 窗口拖拽桥 + 按住说话桥 + 屏幕评论 + 漫步调度 + pet 设置抽屉 | 新页面（全复用模块拼装） |
| 3 | `frontend/index.html` + `frontend/js/desktop-pet.js` | 顶栏加「🖥️ 桌面宠物」按钮：先 ping 回环服务 → 已运行则唤出；否则 `roleplaypet://launch` 协议唤起；都失败则安装引导 | 一个按钮 + 一个桥接 js |
| 4 | `desktop/`（Electron 工程，同仓库子目录） | 主进程：窗口/穿透/拖拽动量/漫步/快捷键/截图OCR/托盘/协议/回环服务/后端拉起/配置；preload：`petApi` | 新，无业务逻辑 |
| 5 | `desktop/resources/ocr/` | tesseract.js 的 `chi_sim` + `eng` traineddata（随包分发，杜绝运行时联网下载） | 静态资源 |
| 6 | `frontend/assets/spine/` + `frontend/assets/lib/spine-player.js` | 从素材包复制 Spine 小模型（`314701_wmz_s_{fight,room,ui}.skel` + atlas/png，512² 贴图）与完整版 room 骨骼（可选大模型模式）+ 官方 spine-player 运行时 | 素材复制（**不含**渲染逻辑，渲染逻辑在 pet.js 双渲染器里） |
| 7 | 后端 | **v1 无改动**；v1.1 可选：加 `POST /api/pet/comment`（屏幕评论专用短提示词）让提示词更干净 | 可选 |

---

## 4. 需求逐条映射（复用 R / 新增 N）

| 需求 | 方案 | 归属 |
|---|---|---|
| 透明无边框置顶窗 | `BrowserWindow{transparent, frame:false, alwaysOnTop, skipTaskbar, hasShadow:false}`，置顶层级可配 | N(壳) |
| 点击穿透 | 常驻 `setIgnoreMouseEvents(true,{forward:true})`；渲染层用 `RoleplayLive2D` 模型包围盒 + 气泡/菜单 DOM 命中测试，命中时 IPC 切回可交互（50ms 去抖） | N(壳)+R |
| 左键拖拽移动 | `live2d.js` 已实现模型拖拽并广播 `live2d:offset` → `pet.js` 把位移转成 IPC → 主进程 `setPosition` 移动窗口（30Hz 节流） | R+N |
| 拖拽动量/回弹 | 释放速度采样（复用 offset 事件时间戳）→ 主进程 rAF 物理：摩擦 + 屏幕边缘阻尼反弹 + 底部“落地” | N(壳，纯函数可单测) |
| 单击反馈 | 复用 `RoleplayLive2D._handleClick` 区域互动/点击池（已实现）；宠物页额外叠加一条随机台词气泡 | R |
| 右键菜单 | 宠物页自绘 DOM 菜单（说话/随机动作/识别屏幕/语音对话/静音/设置/休息/退出） | N(页) |
| 待机动作/空闲分级 | 复用 live2d.js 待机调度 + 90s/5min 睡眠分级；**Spine 小模型另有 `zm1~85` 站立姿势池 + `bm_hy/cm_hy` 表情动画**，待机/睡眠池更丰富（pet.js 按渲染器取对应池） | R |
| 自主行走 | **Spine room 骨骼自带 `target1~8`（原版）/`target/2/3`（简化版）寻路移动动画**：漫步 = 播放 target 动画 + 窗口 lerp 移动（60fps），可配频率 5~120s；Live2D 模式退化为窗口滑动+轻动作 | R+N |
| 随机闲话 | 宠物页定时调 `RoleplayChat.send(闲话提示)` 或本地台词池（默认台词池，避免频繁打 Ollama） | N(页)+R |
| 屏幕截图 | 主进程 `desktopCapturer`（光标附近/全屏/活动窗口，内存流转零落盘） | N(壳) |
| OCR | 主进程 tesseract.js + 内置 `chi_sim`/`eng`（本地 traineddata）；关键词触发(可配列表)/手动触发；节流：手动≥2s、自动≥30s | N(壳) |
| 屏幕评论 | OCR 文本经 `petApi` 交给宠物页 → `RoleplayChat.send("（屏幕内容）…请点评")` → 气泡+TTS；v1.1 可选专有端点 | R+N |
| Ollama 唯一模型源 | 宠物页构造 `RoleplayLLM` 式 override：`provider=ollama`（本地地址/模型从宠物设置读取），后端 `build_llm_from_config` 已支持 | R |
| Ollama 探活/重试 | 宠物页顶部状态条：`/api/llm/ollama/models`（现成接口）探测，未运行给提示+重试按钮；Electron 侧另探 `127.0.0.1:11434` | R+N |
| 多轮上下文 | 复用网页版 session_id + 后端会话记忆（后端已实现），宠物与网页共享会话 | R |
| 语音输入 | 复用 `RoleplayVoice.startRecording/stopRecording`（MediaRecorder→`/api/voice/stt` faster-whisper，**本地**、多语言自动）；按住说话 = Electron `globalShortcut`（默认 `Alt+Space`，可配）→ IPC → 调 start/stop；聆听表情 = `playGesture` + `e_yihuo` | R+N |
| 持续语音对话 | `pet.js` 循环：识别→发送→播放完毕→再录（复用 voice.js 全链路）；唤醒词为可选后续项 | N(页)+R |
| 语音输出 | 复用 `RoleplayVoice.speak`（`/api/voice/tts`）；语速/音量/音色沿用网页语音面板（localStorage 共享同一配置）；嘴型 = TTS 播放中叠加“说话”动作/表情（复用 TTS 收尾手势机制） | R |
| 中英文切换 | 识别：whisper 多语言模型自动检测（已有）；合成：宠物页按回复文本 CJK 占比选中文/英文音色（`speak(text,{voice_id})` 现成参数） | R+N(页小函数) |
| 设置面板 | 网页侧已有：模型/人设/知识库/语音设置面板（继续用）；宠物专属设置（窗口大小/置顶层级/按键/OCR/漫步频率）放宠物页抽屉 + Electron 配置文件（`userData/config.json`） | R+N |
| 与网页版关系 | 同后端同会话：网页按钮唤起宠物；宠物里的对话在网页聊天页同样可见（同一 session） | R |

---

## 5. 关键模块设计（仅新增部分）

### 5.1 宠物窗口与穿透（desktop/main）

- 窗口尺寸默认 360×520（宠物默认 300×400 + 气泡空间），`focusable: true`、无阴影。
- 命中测试协议（preload `petApi.setInteractive(bool)`）：
  ```
  宠物页 rAF：命中 = 模型包围盒内（RoleplayLive2D 提供 getBounds）∪ 气泡DOM ∪ 菜单DOM ∪ 状态条
  → 状态变化(去抖50ms) → petApi.setInteractive(true/false)
  主进程：true → setIgnoreMouseEvents(false)；false → setIgnoreMouseEvents(true,{forward:true})
  ```
  无命中即全穿透，用户可正常操作桌面/其他应用。
- 多显示器：绝对坐标 + `screen` 模块监听显示器增删，跨屏钳制，显示器断开弹回主屏。

### 5.2 渲染层（双渲染器）与漫步物理（desktop/main/physics.ts）

- **双渲染器**（pet.js 内两个适配器，同一套“宠物行为接口”驱动）：
  - `SpinePet`（默认小模型）：`spine-player.js` 加载 `s_room.skel`（或完整版 room 骨骼）；
    动作池 = 待机 `zm_*`（85 个姿势）· 表情 `bm_hy/cm_hy`（37 个）· 行走 `target*` · 互动 `bian/mao/hua/xc/x_ls_*` 等；
    贴图 512²，悬浮窗长期运行开销最小。
  - `Live2DPet`（对话主视觉）：直接复用 `RoleplayLive2D`（情感表情、SSE emotion 联动、点击区域互动全保留）。
  - 设置里可切「小模型（Spine）/ 大模型（Live2D）」，行为接口（walk/idle/emotion/click/drag）两边实现一致。
- 拖拽：Spine 模式同样把拖拽位移转 `pet:moveBy` → `win.setPosition`（Live2D 模式沿用 live2d.js 现有拖拽事件桥接）。
- 释放：offset 时间序列估计速度 → 摩擦 `v*=0.92/frame` → 边缘 `v=-v*0.45` 反弹 → 底部任务栏上沿吸附（弹簧）。
- 漫步：调度器（频率可配）随机目标点 → 播放 `target*` 行走动画 + 60fps lerp 移动窗口 → 到达后恢复待机。
- 物理参数进宠物设置；拖拽/漫步互斥，对话/录音时暂停漫步。

### 5.3 屏幕识别（desktop/main/ocr.ts）

```
触发(手动/关键词/定时) → desktopCapturer 截图(光标附近1200×800,裁剪到屏内)
→ tesseract.js(chi_sim+eng, langPath=desktop/resources/ocr) → 文本
→ petApi.screenText(text) → pet.js 判定(手动/关键词命中) → RoleplayChat.send(评论提示)
```
全程内存流转；截图/文本零落盘、零上传；节流与互斥（手动 2s/自动 30s/定时 60s）。

### 5.4 按住说话（desktop/main/shortcuts.ts）

- `globalShortcut.register('Alt+Space')`（默认，可配，避免占用空格打字）按下/抬起 → IPC `pet:ptt-down/up`；
- 宠物页收事件 → `RoleplayVoice.startRecording()/stopRecording()`（复用现成录音+识别）；
- 录音中 `RoleplayLive2D.playGesture('聆听动作')` + `playExpression('e_yihuo')`，结束自动恢复。

### 5.5 后端拉起与探活（desktop/main/backend.ts）

- 启动时 `GET http://127.0.0.1:8000/health`（现成接口）：已运行 → 直接加载宠物页；
- 未运行 → 宠物窗显示内置引导页：「启动网页版后端」按钮（`desktop` 配置里的仓库路径：
  `…/roleplay-ai/.venv/Scripts/python.exe -m uvicorn roleplay.main:app --port 8000`，或执行现有
  `start_server.bat`；路径首次自动探测、可手改）+「重试」；Ollama 未运行同页提示（`127.0.0.1:11434` 探活）。

### 5.6 网页按钮唤起（§需求 G8）

- **回环控制服务**（Electron 主进程，`127.0.0.1:39231`，端口占用自动 +1 并落盘实际端口）：
  `GET /ping`、`POST /launch`（唤出/置顶宠物窗）、`POST /talk`（可选彩蛋）。
- **自定义协议**：`app.setAsDefaultProtocolClient('roleplaypet')`，网页 `window.open('roleplaypet://launch')`。
- 网页按钮逻辑：先 `fetch /ping`（800ms 超时）→ 已运行 → `POST /launch`；未运行 → 协议唤起；
  双失败 → 展示「请先启动/安装桌面宠物」引导弹层（含后端未启动的诊断提示）。

### 5.7 宠物页 UI（frontend/pet.html + js/pet.js）

- 结构：`#live2d-canvas`（RoleplayLive2D.init 原样调用）+ 气泡区 + 顶栏状态点（后端/Ollama/录音状态）
  + 右键菜单 + 设置抽屉 +（可选）`?mode=embed` 时在普通浏览器里以内嵌小窗形态运行。
- 宠物设置（存 localStorage `roleplay_pet_state` 或经 petApi 写 Electron 配置）：
  窗口大小、置顶层级、按住说话键、漫步频率、闲话开关/台词池、屏幕识别开关与关键词、OCR 语言、TTS 音色语言规则。
- 所有对话/情绪/语音链路与聊天页完全一致（同一 `session_id`），因此**宠物说话时网页聊天记录同步可见**。

---

## 6. 目录结构（改动后的目标形态）

```
roleplay-ai/
├── frontend/
│   ├── index.html              # 改：顶栏 + 1 个按钮
│   ├── pet.html                # 新增：宠物页（复用 lib/js/assets）
│   ├── js/
│   │   ├── chat.js             # 小重构：暴露 RoleplayChat.send（行为不变）
│   │   ├── pet.js              # 新增：宠物页逻辑（双渲染器 + 拼装既有模块）
│   │   └── desktop-pet.js      # 新增：网页按钮桥接（ping/协议唤起）
│   └── assets/
│       ├── live2d/…            # 零改动（现有大厅模型共享）
│       ├── spine/…             # 新增：从素材包复制 s_room 小模型（512²贴图）+ 完整版 room 骨骼
│       └── lib/spine-player.js # 新增：素材包自带 Spine 4.2 运行时（原样复制）
├── desktop/                    # 新增：Electron 壳工程（独立 package.json，electron-builder）
│   ├── src/main/{index,windows,physics,ocr,shortcuts,backend,control-server,protocol,config}.ts
│   ├── src/preload/pet.ts      # window.petApi
│   ├── resources/{icons,ocr/traineddata(chi_sim,eng)}
│   └── docs/PACKAGING.md
├── docs/DESKTOP_PET_DESIGN.md  # 本文档
└── src/roleplay/…              # 后端：v1 零改动
```

`desktop/` 与网页版同仓库（附属功能一体发布）；`.gitignore` 增加 `desktop/node_modules/`、`desktop/out/`、`desktop/dist/`。

---

## 7. 关键数据流（一句话版）

- **对话**：宠物页 `RoleplayChat.send` → `POST /chat/stream`（携带强制 ollama override）→ SSE `chunk/emotion/done` → 气泡 + `RoleplayLive2D.onEmotionEvent` + `RoleplayVoice.speak`（与聊天页同一套代码路径）。
- **语音输入**：`Alt+Space`（Electron 全局快捷键）→ IPC → `RoleplayVoice.startRecording` → MediaRecorder → `/api/voice/stt`（faster-whisper 本地）→ 文本回填 → 自动 `send`。
- **屏幕评论**：Electron 截图 → tesseract 本地 OCR → `petApi.screenText` → 宠物页判定触发 → `RoleplayChat.send(评论提示)`。
- **窗口移动**：`live2d:offset`（现有拖拽事件）→ IPC → 主进程 setPosition + 动量物理。

---

## 8. 设置归属（单一事实来源）

| 配置 | 存哪里 | 说明 |
|---|---|---|
| LLM 模型/地址（强制 Ollama） | 网页 localStorage（`roleplay_llm_state`）+ 宠物页固定 provider=ollama | 复用 llm-switch 的持久化，宠物页只注入 provider 与本地地址 |
| 语音设置（音色/语速/音量/开关） | 网页 localStorage（`roleplay_voice_state`） | 宠物与网页共用，改一处两边生效 |
| 会话/角色/知识库 | 后端（现有） | 共享会话 |
| 宠物窗口大小/置顶层级/按键/OCR/漫步 | Electron `userData/config.json`（经 petApi 读写） | 只有桌面端特有的才放这里 |

---

## 9. 安全与隐私（延续网页版约定）

- 网络：页面请求全部同源（127.0.0.1:8000）；Electron 主进程仅访问 127.0.0.1（Ollama/后端/回环服务），
  并加 webRequest 阻断兜底（非回环一律拒绝）。
- 渲染安全：`contextIsolation:true, sandbox:true, nodeIntegration:false`；preload 只暴露白名单 `petApi`；
  `will-navigate`/新窗口全拦截；CSP 沿用网页版。
- 隐私：截图/录音仅在内存流转（录音本来就走 MediaRecorder 上传到本地后端识别，与网页版一致），
  OCR 文本不进日志；本地 traineddata 随包分发，无运行时外部下载。

---

## 10. 实施阶段（确认后开工）

| 阶段 | 内容 | 验收 |
|---|---|---|
| P0 壳 | `desktop/` 工程、透明置顶穿透窗、加载 `http://127.0.0.1:8000/pet.html`、后端拉起/重试、pet.html 骨架（Live2D 复用跑通） | 悬浮窗显示模型，穿透正确，可拖拽移动窗口 |
| P1 对话 | `chat.js` 抽取 `RoleplayChat.send`（index.html 回归不变）→ pet.html 气泡/情绪/TTS 全链路；Ollama 强制 override + 探活提示 | 宠物能聊、会表情、会出声；网页与宠物共享会话 |
| P2 交互 | 窗口拖拽动量/回弹、右键菜单、漫步+闲话调度、单击反馈、宠物设置抽屉 | 拖动有惯性回弹；菜单全功能；宠物自己会动 |
| P3 屏幕识别 | desktopCapturer + tesseract（内置语言包）+ 关键词/手动触发 → 评论 | 手动/关键词两条路径出评论，零落盘 |
| P4 集成 | 按住说话全局快捷键（Alt+Space）、网页按钮（协议+ping）、打包 NSIS、README/模型说明 | 网页按钮可唤起/唤出；安装包可分发 |

## 11. 风险与待确认

1. **chat.js 抽取重构**是本设计唯一动到现有文件的地方：需保证 index.html 全功能回归（有 344 个后端测试 + 前端手工回归清单），抽取后加几条 pet 页冒烟脚本。
2. **Spine 集成**：spine-player.js 为官方 4.2 播放器（查看器已验证可播），但宠物需要编程控制（animationState 切换/循环/混排），实施 P0 先验证其 JS API（`new spine.SpinePlayer(container, {…})` 返回实例可控制 animationState；若不够用则换 `pixi-spine` 运行时，二选一，均在 P0 定案）。
3. **edge-tts 依赖网络**（网页版现状即如此，微软免费云）：完全离线的 TTS 兜底是浏览器 Web Speech（Windows 自带 Huihui 中文音色）；若坚持纯本地合成，后端加 piper/sherpa 适配器（可选 v1.1）。
4. **全局快捷键冲突**：默认 `Alt+Space`，提供录制改键；按住录音期间 pet 窗不抢焦点。
5. **pet.html 在普通浏览器直接打开**：`petApi` 缺失自动降级（窗口移动/穿透/截图/快捷键不可用，其余功能照常）。
6. 待确认：桌面壳是否**自动拉起后端**（推荐，默认开，可关）；是否打包进网页版仓库同一发布物；唤醒词是否纳入 v1.1；**默认形态用 Spine 小模型还是 Live2D 大模型**（建议默认 Spine 小模型，Live2D 作对话模式）。

## 12. 参考资料

- Electron 点击穿透 forward 模式：[PR #51144](https://github.com/electron/electron/pull/51144) · [自定义窗口交互](https://az.electronjs.org/zh/docs/latest/tutorial/custom-window-interactions)
- 协议唤起：[Electron 实现网页唤醒本地应用](https://juejin.cn/post/7371986999164633098)
- Live2D：[pixi-live2d-display](https://github.com/Hengle/pixi-live2d-display)（本项目网页版同款，已线上验证）
- OCR：[tesseract.js 中文识别实践](https://blog.csdn.net/weixin_29016315/article/details/159367884)
- 语音现状：网页版 `VOICE_ITERATION_REPORT.md`（faster-whisper 本地 STT 6 轮迭代结论，直接沿用）
- Ollama API：[REST 调用说明](https://eastondev.com/blog/zh/posts/ai/ollama-api-calls/)
