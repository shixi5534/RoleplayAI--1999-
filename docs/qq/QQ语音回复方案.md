# QQ 渠道语音回复方案（含中/英配音切换）

> 状态：**P0 已实施**（原声切片链路 + `!voice`/`!lang` 指令 + 失败降级，2026-09-05）。
> P1（TTS 兜底 / 文本净化 / 启动自检 / 随机概率）与 P2 未实施。
> 目标：QQ（NapCat / OneBot v11）场景下，命中特定条件时以语音回复，且可切换中配/英配。

---

## 一、联网调研结论

### 1.1 OneBot v11 发语音的可行链路（已确认）

| 事实 | 来源 | 对本项目的影响 |
|---|---|---|
| 消息段为 `{"type":"record","data":{"file":"file:///abs/path.mp3"}}`，也可 `base64://` 或 http URL | OneBot v11 官方消息段文档 | 发语音无需自研协议 |
| NapCat **内置 ffmpeg 自动转码**：外部 mp3/wav → `encodeSilk()` → silk/amr → NTQQ 上传 | NapCat `packages/napcat-core/helper/audio.ts` | **我们自己不用转 silk**，直接给 mp3 |
| NapCat 官方建议"通过通常的方法发送音频文件，无需特别注意" | NapCat 最佳实践 · 文件处理 | 链路成熟 |
| 接收方向：`get_record` 支持 `out_format=mp3/amr/wav/flac/...` | NapCat 最佳实践 | 后续若接"用户发语音→STT"可直接复用现有 faster-whisper |
| `record` 段支持 `magic=1`（变声） | OneBot v11 文档 | 可选彩蛋，不建议主线用 |

### 1.2 已知坑（必须在实现里防）

1. **NapCat 版本 bug**：4.9.17 / 4.9.20 存在 `convert silk failed Error: Failed to open input`，官方 4.9.21 修复（NapCatQQ issues #1336）。
   → 方案：发送失败必须**静默降级为文字**，并在日志里提示"检查 NapCat 版本/ffmpeg"。
2. **ffmpeg 缺失**：NapCat 转 silk 依赖 ffmpeg，未装则报「语音转换失败，请检查语音文件是否正常」（AstrBot issue #3265）。
   → 方案：首次发送前做一次**探测性自检**，失败则整个语音功能自动禁用，只留文字。
3. **路径语义**：`file://` 是**NapCat 进程所在机器**的路径。跨设备/Docker 部署时失效。
   → 方案：本项目与 NapCat 同机，但**优先用 `base64://`**（单条切片仅几十 KB），彻底规避路径问题；大文件才走 file://。
4. **时长/大小限制**：QQ 语音普通用户 ≤60s，会员 3min，超会 5min；开放平台口径 ≤5min / ≤28MB / silk。
   → 方案：切片与 TTS 都卡上限，超出则截断或改发文字。（实现：切片时长上限取 **65s** 以兜住切片库实测最长 62.6s 的官方切片；TTS 路径 P1 时仍按 60s 收紧）

### 1.3 同类产品做法（可抄的部分）

| 产品 | 做法 | 是否借鉴 |
|---|---|---|
| **AstrBot 原生 TTS** | 「TTS 回复概率」随机触发 | ✅ 借鉴为兜底概率触发 |
| **astrbot_plugin_actively_calls_tts** | 给 LLM 注册一个 TTS **工具（function calling）**，由 LLM 自主决定何时发语音 | ⭐ **最有价值**，列为 P2 高级触发 |
| **AstrBot PR #5512 `filter_regex`** | TTS 前用正则剔除角色扮演的**动作描写/内心独白**，如「(微笑着说)你好啊」 | ⭐ **必做**，本项目角色卡回复就带括号动作描写 |
| **astrbot_plugin_translate_tts** | LLM 回复 → 翻译成目标语言 → TTS | ⚠️ 不采纳（会改语义）；中英切换改走**音色对 + 原声切片双套** |
| 多引擎（Edge TTS / OpenAI TTS / GPT-SoVITS / FishAudio） | 可插拔 TTS Provider | ✅ 沿用现有 `tts.py` 抽象，暂只接 Edge TTS |

### 1.4 Edge TTS 音色选型

无名者 = 冷静、克制、带距离感的成熟女声（Ms. Stranger）。

| 语言 | 推荐 | 备选 | 理由 |
|---|---|---|---|
| 中文 | `zh-CN-XiaoxiaoNeural`（Warm） | `zh-CN-XiaomoNeural`（成熟）、`zh-CN-XiaoxuanNeural`（温暖） | 现有默认已是 Xiaoxiao，先沿用 |
| 英文 | `en-US-AriaNeural`（News/Novel, Positive+Confident） | `en-US-JennyNeural`（Friendly/Considerate）、`en-US-MichelleNeural`（News/Novel） | Aria 是"小说朗读"定位，最接近无名者的叙事感；Jenny 偏亲切，与角色疏离感不符 |

---

## 二、现状盘点（本项目独有的优势）

| 资产 | 位置 | 说明 |
|---|---|---|
| **角色原声切片库** | `frontend/assets/voice/wu_ming_zhe/manifest.json` + `zh/`(48) `en/`(85) | **133 条官方中/英双配音切片**，每条带 `subtitle:{zh,en}` 双语字幕。manifest 顶层已有 `slots` 映射（槽位 → clip id 列表），选片无需给切片打标 |
| 切片槽位 | `slots: enter/click/happy/sad/surprise/sleep/idle/intel/battle` | 与后端 15 类情绪天然可映射 |
| 前端槽位映射 | `frontend/js/pet-voice.js` 的 `POSE_TO_SLOT` | 后端可直接照搬，保证 Web / 宠物 / QQ 三端行为一致 |
| 后端情绪输出 | `OrchestratorResult.response.emotion`（emotion + score） | **现成的触发信号源**，无需二次 LLM 调用。⚠️ 检测对象是**用户消息**（`orchestrator._detect_emotion(req.message)`），不是回复——语义是"用户难过 → 角色发 sad 槽位原声"，与前端 emotion 事件驱动宠物姿态的行为一致 |
| TTS 后端 | `src/roleplay/core/voice/tts.py::synthesize_speech_to_bytes`（edge-tts，含缓存/重试/切分） | 已有，直接复用。⚠️ 受 `tts_backend_enabled` 门控（tts.py 内 `synthesize_speech` 入口），该开关本意只管 `/voice/*` API，P1 接 TTS 兜底时需处理 |
| STT 后端 | `src/roleplay/core/voice/stt.py`（faster-whisper） | 后续接"听语音"时用，本期不动 |
| QQ 渠道 | `src/roleplay/channels/qq_onebot.py` | `_send_msg` 已扩展 `segments`/`wait_response` 可选参数，纯文本调用方式不变 |

**槽位 ↔ 情绪映射表**（照搬前端 `POSE_TO_SLOT`，保证三端一致。confused→surprise 为有意保留前端口径；后端 `EMOTION_PARENT` 的 confused→anxious 仅用于 Live2D 表情回退，用途不同，勿互相"对齐"）：

| 情绪（后端枚举） | 槽位 |
|---|---|
| happy / love / grateful / excited | `happy` |
| sad / angry / disappointed / lonely | `sad` |
| surprise / confused / fear | `surprise` |
| sleepy | `sleep` |
| anxious / embarrassed / neutral | `idle` |

---

## 三、方案设计

### 3.1 分层（严格不破坏现有边界）

```
src/roleplay/channels/qq_onebot.py   ← 只负责：拼 record 段、发、失败降级
        │
        ▼
src/roleplay/core/voice/voice_reply.py   ← 【新增】语音回复决策器（纯业务，渠道无关）
   ├─ 触发判定（指令/关键词/情绪/概率）
   ├─ 文本净化（剥离动作描写，P1）
   └─ 决定用「原声切片」还是「TTS」
        │
        ├──► src/roleplay/core/voice/clip_store.py   【新增】manifest 加载 + 按 lang/slot 选片
        └──► src/roleplay/core/voice/tts.py          【复用，P1】synthesize_speech_to_bytes
```

`voice_reply.py` 对渠道零耦合 → 以后接微信/Telegram 直接复用。

### 3.2 三条语音来源（优先级从高到低）

1. **角色原声切片**（首选）
   情感命中槽位时，从 manifest 里按 `lang` 随机取一条。**发的是游戏官方配音**，沉浸感远强于 TTS。
2. **Edge TTS**（兜底读正文）
   无命中切片 / 用户明确要"念这段"时，把净化后的回复正文合成语音。
3. **纯文字**（最终兜底）
   以上任一环节抛错 → 发文字，日志记 warning。**绝不因为语音失败而丢回复**。

### 3.3 触发条件（"特定条件"，四级可组合）

| 级别 | 条件 | 默认 | 说明 |
|---|---|---|---|
| **L1 显式指令** | `!voice on` / `!voice off` / `!lang zh` / `!lang en` | off | 会话级开关，写内存 dict（与现有 `_session_chars` 同款） |
| **L2 关键词** | 消息含「说句话」「念给我听」「用英语说」「voice」「speak」 | — | 命中即强制本次语音，并可按关键词临时切语言 |
| **L3 情感阈值** | `emotion.score ≥ 阈值` 且情绪能映射到槽位 | 阈值 0.6 | 只在"情绪够强"时才出声，避免每条都发语音扰群 |
| **L4 概率 + 冷却** | 兜底随机概率 + 会话冷却 | 概率 0（关）/ 冷却 60s | 冷却防刷屏；默认关，避免群聊噪音 |

**判定顺序**：L1 开关 → L2 关键词（强制）→ L3 情感 → L4 概率 → 不发。
**群聊额外约束**：`qq_group_at_only=True` 场景下语音频率再降一档（建议群默认只认 L1/L2，L3/L4 仅私聊生效）。

**score 口径注意（P0 实现约定）**：LLM/分类器来源的 score 是 [0,1] 置信分；关键词层是权重累加（单命中仅 0.3~0.5，多命中封顶 1.0），且只在正则真实命中时才产出非 neutral 标签。因此实现约定：**keyword 来源的非 neutral 命中视为已达标**（不做阈值比较）——否则纯关键词部署（无 LLM）下任何情绪都过不了 0.6 阈值，功能形同虚设。neutral 恒不出声（责任链对 neutral 恒下沉，最终 score 恒为 0，`decide` 再显式挡一道）。

### 3.4 中 / 英切换

| 维度 | 原声切片 | Edge TTS |
|---|---|---|
| 切换方式 | manifest 每个 slot 都有 `zh_*` / `en_*` 两套，切 lang = 切整套配音 | 音色对 `zh-CN-XiaoxiaoNeural` ↔ `en-US-AriaNeural` |
| 字幕 | 切片自带 `subtitle.zh/en`，可随语音附带台词文本 | 无（可选：发 `subtitle.zh` 作文字补充） |

**切换粒度（三档，后者覆盖前者）**：
1. 全局默认：`ROLEPLAY_QQ_VOICE_LANG=zh`
2. 会话级：`!lang en`（存 session dict，重启丢失）
3. 单次：`用英语说这句话`（仅本条生效）

**关键设计**：语言切换**只影响语音音色，不影响 LLM 回复语种**（LLM 该怎么答还怎么答）。
中配模式下若回复是英文、或英配模式下回复是中文，由 `detect_lang()` 自动挑选匹配音色，避免中文用英音念。

### 3.5 发送链路

```
决策产出 (audio_bytes, kind, lang)
   │
   ├─ 大小/时长校验：≤60s（用 clip.dur 或 mp3 估算）；超限 → 降级文字
   │
   ├─ 编码：base64://<b64>   （首选，规避跨机路径问题）
   │         file:///abs/path.mp3 （base64 过大时备选）
   │
   ├─ 组装： [{"type":"reply","data":{"id":msg_id}},       ← 引用原消息（可选）
   │          {"type":"record","data":{"file":"base64://..."}}]
   │
   └─ send_msg → 失败 → 捕获 → 改发纯文字 + 记日志
```

`_send_msg` 扩展为 **可选 `segments` / `wait_response` 参数**，纯文本调用方式**完全不变**（零回归）。

**P0 实测行为**：命中语音时本轮**以语音为回复**（不再发送 LLM 文字），发送 record 段后附带所选语言的 `subtitle` 台词文本，让用户看到"她说了什么"；语音发送失败（连接异常 / 应答超时 / status=failed）→ 照常发送 LLM 文字回复。语音发送使用 `wait_response=True` 等 OneBot 应答判定成败（普通文本仍是发后即忘，延迟不变）。

### 3.6 文本净化（必做，来自 AstrBot filter_regex 经验）

角色卡回复形如：`（面具微微偏了偏）……来了啊。坐吧，想说什么都行。`
直接喂 TTS 会念出「括号面具微微偏了偏括号」，非常出戏。

净化规则（可配置正则，默认）：
- 剥离 `（）【】《》()[]` 包裹的内容 → 动作描写 / 内心独白
- 剥离 `*斜体*` 包裹的内容
- 剥离 Markdown 符号 `#*->`
- 连续空白压缩
- **净化后为空 → 不打语音**（改发原文）

---

## 四、配置项清单（全部默认关闭 / 零破坏）

```ini
# ---- QQ 语音回复（默认全关，不影响现有功能；P0 已实施）----
ROLEPLAY_QQ_VOICE_ENABLED=false              # 总开关（!voice on/off 可按会话覆盖）
ROLEPLAY_QQ_VOICE_LANG=zh                    # zh | en（全局默认配音；!lang zh/en 可按会话覆盖）
ROLEPLAY_QQ_VOICE_CLIP_MANIFEST=             # 空=自动定位 frontend/assets/voice/wu_ming_zhe/manifest.json
ROLEPLAY_QQ_VOICE_EMOTION_THRESHOLD=0.6      # 情感触发阈值（keyword 来源命中豁免，见 §3.3）
ROLEPLAY_QQ_VOICE_COOLDOWN_SEC=60            # 同一会话冷却
ROLEPLAY_QQ_VOICE_MAX_SEC=65                 # 单条语音时长上限（QQ 上限 60s；切片库实测最长 62.6s，故 65）
ROLEPLAY_QQ_VOICE_GROUP_ENABLED=false        # 群聊是否允许语音（防扰群）
ROLEPLAY_QQ_VOICE_TTS_VOICE_EN=en-US-AriaNeural  # 英文 TTS 音色（P1 预留；中文复用现有 ROLEPLAY_EDGE_TTS_DEFAULT_VOICE）

# ---- P1 实施时随实现一并加入 ----
ROLEPLAY_QQ_VOICE_MODE=auto                  # auto（情感命中走原声，否则 TTS）| clip | tts
ROLEPLAY_QQ_VOICE_RANDOM_RATE=0.0            # 兜底随机概率（群聊建议 0）
ROLEPLAY_QQ_VOICE_FILTER_REGEX=              # 文本净化（TTS 前剥离动作描写），空=内置默认规则
ROLEPLAY_QQ_VOICE_SELFTEST=true              # 启动时探测一次 NapCat 转码能力，失败即自动禁用
```

> 原方案中的 `ROLEPLAY_QQ_VOICE_TTS_VOICE_ZH` 已移除：中文音色直接复用现有
> `ROLEPLAY_EDGE_TTS_DEFAULT_VOICE`（默认即 zh-CN-XiaoxiaoNeural），避免双份配置漂移。

角色卡侧新增（可选，覆盖全局，P1 一并实现）：
```json
"voice_clips_dir": "wu_ming_zhe",   // 该角色对应的原声切片目录名
"tts_voice_en": "en-US-AriaNeural"  // 英配音色（与现有 voice_id 并列）
```

---

## 五、实施步骤

### P0 — 最小可用 ✅（2026-09-05 已实施）
1. ✅ `src/roleplay/config.py`：新增 `qq_voice_*` 配置项（全部默认关）
2. ✅ `src/roleplay/core/voice/clip_store.py`：加载 manifest（含顶层 `slots` 映射），`pick(slot, lang, exclude)` 对齐前端去重与单条池回退语义
3. ✅ `src/roleplay/core/voice/voice_reply.py`：`decide(session_id, emotion, is_group)`（L1 开关 + L3 情感阈值（keyword 豁免）+ 冷却 + 超长切片降级），会话态（开关/语言/冷却/去重）内聚在服务内
4. ✅ `src/roleplay/channels/qq_onebot.py`：
   - `_handle` 返回 `(reply, emotion)`；`_send_msg` 增加可选 `segments` / `wait_response`
   - 新增 `!voice on/off`、`!lang zh/en` 指令（`!clear` 一并清语音会话态，`!help` 更新）
   - 发 `base64://` record 段（引用原消息），`wait_response=True` 等应答判定成败，失败降级文字
5. ✅ **验收**：`tests/test_qq_voice.py`（决策矩阵 19 例）+ `tests/test_qq_onebot.py`（指令/record 段/降级/e2e 语音双发），全量 510 passed

### P1 — 完善
6. 文本净化 + `filter_regex` 可配置
7. TTS 兜底路径（无切片命中时念正文）
8. 启动自检（`ROLEPLAY_QQ_VOICE_SELFTEST`）：探测 NapCat 转码，失败自动关语音
9. 群聊频率控制（群内默认只认显式指令）
10. 单元测试：触发矩阵、语言切换、降级路径

### P2 — 进阶（可选）
11. **LLM 自主决定**（借鉴 AstrBot 插件）：注册 `send_voice` 工具，让 LLM 判断何时该出声
12. 接收方向：用户发语音 → `get_record(out_format=mp3)` → faster-whisper STT → 正常对话
13. 语音缓存：同一 (slot, lang) 或 (text, voice) 复用，减少 edge-tts 调用与 NapCat 转码

---

## 六、风险与验收

| 风险 | 影响 | 缓解 |
|---|---|---|
| NapCat silk 转码失败（版本 bug / 缺 ffmpeg） | 语音发不出去 | 发送失败（等应答判定）静默降级文字 + 日志明确提示版本；启动自检为 P1 |
| 群聊语音刷屏被踢 | 账号风险 | 群聊默认关（`QQ_VOICE_GROUP_ENABLED=false`，`!voice on` 在群内被拒）+ 冷却 + 情感阈值 |
| edge-tts 网络抖动 | 延迟/失败 | 现有 `tts.py` 已有 3 次重试 + 30s 超时 + 缓存，直接复用 |
| 动作描写被念出来 | 出戏 | 文本净化（P1-6）；P0 只发原声切片不念正文，暂不受影响 |
| 跨机部署 file:// 失效 | 语音发不出去 | 默认走 `base64://` |
| 原声切片与回复语义不搭 | 轻微出戏 | 触发情绪来自**用户消息**（切片是对用户情绪的回应，与 LLM 回复独立）；附带 subtitle 文本让用户看到"她说了什么" |

**验收清单**
- [x] `QQ_VOICE_ENABLED=false` 时，行为与改动前**完全一致**（零回归）——全量测试 510 passed，默认关状态下渠道行为不变
- [x] 开启后私聊强情绪 → 收到原声语音，且内容与情绪匹配（e2e：record 段引用原消息 + 台词文本）
- [x] `!lang en` / `!lang zh` → 配音语言实时切换，字幕同步（单测覆盖）
- [x] 断网 / 删 ffmpeg / 停 NapCat 任一场景下 → **仍能收到文字回复**（发送失败降级单测 + e2e）
- [x] 群聊默认不自动出声（`!voice on` 群内被拒；`decide` 按 `is_group` 拦截）
- [x] 单条语音 ≤65s（超长切片自动降级文字）
- [ ] **真机联调**：NapCat 实际收发语音（silk 转码、普通账号 60s 限制），需连真实 NapCat 验证一次

---

## 七、一句话总结

**复用已有的 133 条官方中/英双配音切片 + 后端现成的情绪输出，在 QQ 上做「情感命中 → 发角色原声 → 失败降级 TTS → 再失败降级文字」的四级链路，并用 `!lang zh/en` 会话级切换配音语言。**核心风险（NapCat silk 转码）用启动自检 + 全程降级兜住，默认全关保证零回归。
