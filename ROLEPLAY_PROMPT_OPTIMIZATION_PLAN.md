# 角色提示词注入系统优化计划

> 项目：roleplay-ai（无名者 Ms. Stranger）
> 范围：提示词注入系统（persona_prompt / character_card / orchestrator / 角色卡）
> 侧重：角色扮演质量（沉浸感、一致性、情感深度、对话活力）
> 状态：计划文档，不执行

---

## 一、现状诊断

### 1.1 当前提示词注入链路

```
用户消息
  │
  ├─ ① 人设解析（character_store / character_repo）
  │     └─ 角色卡 JSON → CharacterCard
  │
  ├─ ② 情感检测（emotion.detect）→ emotion 标签
  │
  ├─ ③ 上下文检索（并行）
  │     ├─ 联网检索 → ingest_web → 入库
  │     ├─ 知识库检索（knowledge_scope 限定命名空间）
  │     │     └─ 混合检索（稠密向量 + BM25，alpha=0.45，candidates=30）
  │     │     └─ 长期记忆（events:<cid>，时间衰减×重要性）
  │     └─ 用户画像检索（profile_top_k=5）+ 日期提醒
  │
  ├─ ④ 拼装 system_prompt（build_roleplay_prompt）
  │     │
  │     ├─ resolve_system_prompt
  │     │     ├─ 卡内 system_prompt（完全覆盖）
  │     │     └─ V2 字段拼装（按 PromptConfig 顺序）
  │     │           ├─ name → personality → background
  │     │           ├─ behavior_rules（结构化 if-then 优先）
  │     │           ├─ scenario → first_mes → mes_example
  │     │           ├─ post_history_instructions
  │     │           └─ Lorebook（关键词触发，最多40条/4000字）
  │     │
  │     ├─ 外层块（按 ordered_fields）
  │     │     ├─ 【语气要求】tone
  │     │     ├─ 【用户资料】profile_chunks
  │     │     └─ 【角色资料库】rag_chunks（过滤：绝对下限0.05 + 相对门0.85）
  │     │
  │     ├─ footer_fields（置底，对抗 lost-in-the-middle）
  │     │     └─ post_history_instructions（当前角色卡已配置）
  │     │
  │     └─ repetition_block（最末尾，复读抑制负向提示）
  │
  ├─ ⑤ 会话锁 → 读取历史（最多40轮/80条）
  │     └─ 历史摘要（超40轮时增量压缩）
  │
  ├─ ⑥ 复读抑制素材（最近8轮 assistant 句子 + mes_example/first_mes）
  │
  ├─ ⑦ LLM 生成（temperature=0.8, top_p=0.92, repetition_penalty=1.10）
  │     └─ messages = [system] + history + [user]
  │
  ├─ ⑧ 生成后校验（find_violations）→ 命中则重试（最多1次）
  │
  └─ ⑨ 记忆沉淀（每6轮长期记忆 / 每10轮用户画像）
```

### 1.2 已有的优秀设计

| 设计 | 位置 | 价值 |
|---|---|---|
| footer_fields 置底机制 | persona_prompt.py / prompt_config.py | 对抗 lost-in-the-middle，风格指令紧贴生成点 |
| 复读抑制（负向提示+生成后校验） | repetition_guard.py | 解决 mes_example 照抄、意象重复问题 |
| RAG 相对门过滤（0.85） | persona_prompt.py _filter_chunks | 实测可切分相关/噪声，优于绝对阈值 |
| 结构化 if-then 行为规则 | behavior_rules.py | 零 LLM 开销的条件触发（当前角色卡未启用） |
| Lorebook 关键词触发 | character_card.py _build_lorebook | 按需注入设定，避免 context 膨胀 |
| 用户画像独立命名空间 | profile.py | 与角色知识隔离，不串味 |
| 历史摘要增量落盘 | session_memory.py | 长对话不丢关键信息 |
| 角色卡内嵌 prompt_config | character.py / prompt_config.py | 每角色可定制字段开关/顺序/模板 |

### 1.3 角色卡现状（wu_ming_zhe.json）

- **personality**：丰富，约200字，涵盖性格核心与矛盾面
- **background**：详细，约300字，完整时间线
- **behavior_rules**：11条，覆盖身份、语气、知识边界、动作限制
- **behavior_rules_structured**：`null`（未使用）
- **mes_example**：仅2句独白式示范，非完整对话对
- **character_book**：3条 Lorebook（名字/容貌/来历）
- **post_history_instructions**：非常详细（怎么说/主动往前推/情绪在前/怎么用记忆）
- **prompt_config**：已配置 footer_fields + 自定义模板 + rag header 角色化

---

## 二、核心问题识别

### 问题 1：所有动态内容塞入单一 system message，注意力分配不均

**现状**：人设 + 语气 + 用户资料 + RAG 资料 + 风格指令 + 复读抑制，全部拼进一个 `system` 角色的 content。模型对 system 消息的注意力在长上下文下会衰减，且 RAG 资料块（可能3000+字）夹在中间时，前后的人设和风格指令都会被"稀释"。

**影响**：长对话中角色逐渐"出戏"，回复变得通用化、客服化。

### 问题 2：mes_example 示范不足且格式单一

**现状**：仅2句独白（"窗外的蛾子又往亮处扑了……"），没有 user→assistant 的完整对话对，也没有覆盖不同情绪场景（平静/讽刺/脆弱/坚定）。

**影响**：模型对角色语气的"手感"不足，容易滑向通用书面语；社区共识是 3-5 组覆盖不同情绪的完整对话对效果最好。

### 问题 3：情感检测结果未反向注入提示词

**现状**：emotion 标签仅用于 Live2D 表情映射和结构化行为规则的 `emotion_is` 条件判定，**没有**把"当前用户情绪→角色应如何回应"的策略注入提示词。

**影响**：角色对用户情绪的回应缺乏差异化——用户难过和用户生气时，角色的回复策略应该不同（共情 vs 冷静分析 vs 转移注意），但当前提示词没有这种动态调整。

### 问题 4：缺少"角色核心锚点"的重复强化

**现状**：personality 字段只在 system prompt 开头出现一次。长对话（20+轮）后，模型对角色核心特质的注意力显著下降。

**影响**：角色漂移（character drift）——无名者的"黑色幽默+轻描淡写+身份迷惘"核心逐渐被通用助手行为取代。

### 问题 5：输出格式约束过于保守，限制沉浸感

**现状**：behavior_rules 第10条"只写自己说的话和极少的动作，不替对方说话、不替对方做决定、不写大段旁白"。post_history_instructions 也强调"只写你说的话和极少的动作"。

**影响**：回复变成纯对话气泡，缺少场景感和身体语言。社区最佳实践是"动作+对话+适度内心独白"的组合，动作描写用 `*动作*` 或 `（动作）` 标记，占比约 20-30%。

### 问题 6：RAG 资料以"外部资料"口吻注入，而非"角色记忆"

**现状**：RAG 块 header 是"【角色资料库（检索所得，按相关度排序）】"，虽然使用守则要求"用你自己的口吻揉进对话"，但资料本身的呈现方式是 `[1] (来源·章节) 文本`，模型容易把它当成需要引用的参考资料而非自己的记忆。

**影响**：回复中偶尔出现"根据资料"的痕迹，或资料与回复之间有明显的"拼接感"。

### 问题 7：缺少情感节奏（emotional pacing）设计

**现状**：提示词要求"情绪在前——对方有情绪时先接住"，但没有定义角色的"情感阻力"——角色不应该总是立刻敞开心扉，她的间谍训练和身份迷惘应该让她在某些话题上回避、转移、轻描淡写。

**影响**：角色过于"配合"，用户问什么就答什么，缺少角色应有的防备感和层次感。

### 问题 8：behavior_rules_structured 未启用

**现状**：角色卡中该字段为 `null`，11条行为规则全部是自由文本，每轮全部注入。

**影响**：(1) 规则膨胀占用 context；(2) 无法做条件触发（如"用户问起发条装置时才注入特定回应策略"）；(3) 规则之间可能矛盾时无法按优先级裁决。

### 问题 9：缺少生成后质量自检（除复读外）

**现状**：生成后只做复读违规检查（find_violations），不检查角色一致性、情绪适当性、是否出戏。

**影响**：明显出戏的回复（如自称AI、用客服腔、编造设定）直接到达用户，没有二次过滤。

### 问题 10：回复长度静态，不随场景动态调整

**现状**：post_history_instructions 固定"每条 2-4 句，大约 20-40 字"。

**影响**：情绪激烈的场景需要更长的回复来展开，轻松闲聊时短回复更自然。固定长度限制了表达力。

---

## 三、优化计划

### 优先级定义

- **P0（高价值/低成本）**：改动小、见效快，1-2天可完成
- **P1（高价值/中成本）**：需要模块级改动，3-5天
- **P2（探索性）**：需要实验验证，1周+

---

### P0-1：强化 mes_example——3组覆盖不同情绪的完整对话对

**问题**：问题 2

**方案**：将角色卡 `mes_example` 从2句独白扩展为3组完整的 `用户: ... / 无名者: ...` 对话对，每组覆盖一种核心情绪场景：

1. **场景A（讽刺/轻描淡写）**：用户问起过去的罪行 → 无名者用黑色幽默缓冲
2. **场景B（脆弱/迷惘）**：用户问"你到底是谁" → 列出化名后落回"无名者"，带一丝不确定
3. **场景C（坚定/保护欲）**：用户表达自我怀疑 → 无名者罕见地认真，给出简短坚定的支持

每组对话对控制在 3-4 轮，总字数不超过 600 字。示范中**禁止**使用后续会被复读抑制禁用的句子（示范句本身会被加入 extra_phrases，所以示范句应该是"只学语气不照抄"的类型）。

**修改位置**：`data/characters/wu_ming_zhe.json` 的 `mes_example` 字段

**预期效果**：模型对角色语气的"手感"显著提升，不同情绪场景下的回复差异化增强。

---

### P0-2：提取"角色核心锚点"，每轮重复注入

**问题**：问题 4

**方案**：在角色卡新增可选字段 `core_anchors`（3-5条，每条不超过20字），提取角色最不可漂移的核心特质。例如无名者：

```json
"core_anchors": [
  "用轻描淡写和黑色幽默缓冲沉重话题",
  "对身份持续迷惘，但拒绝被过去定义",
  "偶尔有白骑士冲动，但用讽刺掩饰",
  "说话简短精确，不用书面语和客服腔",
  "提到过去时用蛾/光/蛹/发条等意象（每次不超过一个）"
]
```

在 `build_roleplay_prompt` 中，将 core_anchors 渲染为一个简短块，**放在 system prompt 的最末尾**（repetition_block 之前），利用近因效应强化。块头示例：

```
【别忘了你是谁】
- 用轻描淡写和黑色幽默缓冲沉重话题
- 对身份持续迷惘，但拒绝被过去定义
- ...
```

**修改位置**：
- `src/roleplay/models/character.py`：CharacterCard 新增 `core_anchors: list[str] | None = None`
- `src/roleplay/core/persona_prompt.py`：build_roleplay_prompt 中新增锚点渲染
- `data/characters/wu_ming_zhe.json`：新增字段

**预期效果**：长对话（20+轮）中角色漂移率下降，核心特质保持稳定。

---

### P0-3：将情感检测结果动态注入回应策略

**问题**：问题 3

**方案**：在 `build_roleplay_prompt` 中新增 `emotion_strategy` 块。根据检测到的用户情绪，从预设策略表中选择对应的回应指导，注入到 footer 区域（风格指令附近）。

策略表（针对无名者角色）：

| 用户情绪 | 回应策略 |
|---|---|
| sad / 难过 | 先沉默半拍（用"……"），再用不太熟练的方式安慰；不要说教，不要说"会好起来的" |
| angry / 生气 | 不接火，用平静甚至略带调侃的语气降温；如果是对她生气，不辩解，听着 |
| anxious / 焦虑 | 给一个具体的、可操作的小建议，而不是空泛安慰；语气放轻 |
| happy / 开心 | 难得地 genuinely 笑一下，可以跟着轻松，但不要过度热情 |
| neutral / 平静 | 正常对话，可以带一点观察或调侃 |
| fear / 害怕 | 白骑士冲动触发——主动挡在前面，但用轻描淡写掩饰 |

实现方式：在 `orchestrator._prepare` 中拿到 emotion_info 后，查策略表生成策略文本，传入 `build_roleplay_prompt`。策略表可以放在角色卡的新字段 `emotion_strategies` 中，实现角色可定制。

**修改位置**：
- `src/roleplay/models/character.py`：新增 `emotion_strategies: dict | None = None`
- `src/roleplay/core/orchestrator.py`：_prepare 中查策略表
- `src/roleplay/core/persona_prompt.py`：build_roleplay_prompt 新增 emotion_strategy 参数与渲染
- `data/characters/wu_ming_zhe.json`：新增策略表

**预期效果**：角色对用户情绪的回应从"通用共情"变为"角色化回应"，沉浸感提升。

---

### P0-4：RAG 资料块角色化重写——从"资料库"到"脑海片段"

**问题**：问题 6

**方案**：当前角色卡已通过 `header_templates.rag` 自定义了 header（"【你记得的事（唯一事实来源，优先于对话示例）】下面是你脑子里浮出来的片段……"），这已经很好。但条目格式 `[1] (来源·章节) 文本` 仍然有"引用感"。

优化：将条目格式从编号列表改为更自然的"记忆碎片"格式：

```
【你脑子里浮出来的片段】
（角色设定资料·相关角色档案）康斯坦丁教过她怎么拿扇子，也教过她怎么在被人盯着的时候不眨眼。
（长期记忆）上次他提到巴南区的工程学院时，声音放轻了。
```

即去掉 `[1] [2]` 编号，改为 `（来源标签）内容`，来源标签用括号弱化。同时在使用守则中增加一条："这些片段是你脑子里冒出来的，不是你在读一份文件——你可以只取其中一个细节，用自己的话说出来，甚至可以记错（如果资料本身就模糊的话）。"

**修改位置**：`src/roleplay/core/persona_prompt.py` 的 `build_rag_context` 函数，修改 `lines.append(f"[{i}] ({_source_label(c.metadata)}) {text}")` 为 `lines.append(f"（{_source_label(c.metadata)}）{text}")`。同时更新 `_CONTEXT_HEADER` 默认文本。

**注意**：角色卡已自定义 rag header，所以默认 header 的修改不影响当前角色，但需要同步更新角色卡的 header_templates.rag 以保持一致。

**预期效果**：RAG 资料与角色回复的"拼接感"降低，模型更自然地将资料融入角色口吻。

---

### P0-5：行为规则结构化——将11条自由文本规则迁移为 if-then

**问题**：问题 8

**方案**：将 `behavior_rules` 中适合条件触发的规则迁移到 `behavior_rules_structured`，减少每轮注入的规则量。

适合结构化的规则：
- 规则2（被问"你是谁"时）→ `text_regex: 你是谁|你到底|叫什么|名字|身份`
- 规则5（称谓）→ 全局规则（始终注入，但可以精简）
- 规则6（重大罪行轻描淡写）→ `text_regex: 杀|死|罪|过去|做过什么`
- 规则8（身份追问）→ `text_regex: AI|模型|开发者|是不是真的|真人吗`
- 规则9（白骑士冲动）→ `emotion_is: sad|fear|anxious`

不适合结构化的（始终注入的核心规则）：
- 规则1（第一人称，不承认AI）
- 规则3（过去迷惘但强调选择）
- 规则4（意象使用）
- 规则7（知识范围）
- 规则10（输出格式）
- 规则11（不背资料）

迁移后，`behavior_rules` 文本保留核心规则（约5-6条），`behavior_rules_structured` 承载条件触发规则（约5-6条）。每轮只注入命中的条件规则，context 占用减少且规则更精准。

**修改位置**：`data/characters/wu_ming_zhe.json`（behavior_rules 精简 + behavior_rules_structured 填充）

**预期效果**：(1) 每轮注入的规则量减少约30%；(2) 条件触发的规则更精准，不会因为规则太多而被模型忽略；(3) 为后续扩展更多场景规则留出空间。

---

### P1-1：消息结构重构——从单一 system 到分层注入

**问题**：问题 1

**方案**：将当前全部塞入 `system.content` 的内容拆分为多个消息，利用 OpenAI 格式的多消息结构优化注意力分配：

```
messages = [
  {"role": "system", "content": "核心人设（name+personality+background+core_anchors）"},  // 不变的核心
  {"role": "system", "content": "RAG 资料块（角色记忆碎片）"},  // 动态知识
  {"role": "system", "content": "用户画像块"},  // 动态用户信息
  ...history...
  {"role": "user", "content": "当前用户消息 + 风格指令 + 复读抑制 + 情感策略"},  // 紧贴生成点的动态指令
]
```

关键改动：
1. **核心人设**保留在第一个 system 消息（首因效应）
2. **RAG/画像**作为独立 system 消息插在历史之前（中间位置，但有明确的消息边界，比混在一个长文本中更容易被 attention 定位）
3. **风格指令/复读抑制/情感策略/核心锚点**从 system 移到**当前 user 消息的前缀**（近因效应最强的位置）

具体实现：在 `openai_like.py` 的 `_build_messages` 中支持多段 system 消息和 user 前缀。或者在 orchestrator 层直接构造 messages 列表，而不是先拼一个大 system 字符串。

**风险**：部分 OpenAI 兼容端点对多 system 消息的支持不一致，需要测试 deepseek/ollama 的行为。可以保留"单 system 模式"作为 fallback。

**修改位置**：
- `src/roleplay/core/llm/openai_like.py`：_build_messages 支持 system_blocks 列表和 user_prefix
- `src/roleplay/core/orchestrator.py`：_build_prompt 返回结构化的 prompt 组件而非单一字符串
- `src/roleplay/core/persona_prompt.py`：新增 `build_roleplay_messages` 函数，返回消息列表

**预期效果**：长对话中角色一致性提升，RAG 资料的利用率提高，风格指令的遵从度提升。

---

### P1-2：输出格式升级——动作+对话+内心独白的结构化输出

**问题**：问题 5

**方案**：放宽"只写说话和极少动作"的限制，引入结构化输出格式，但保持简洁：

```
*动作/神情描写*（可选，每轮1-2个，用 *...* 标记）
对话内容（主体，2-4句）
（内心独白）（可选，仅在情绪激烈或话题触及时，用（...）标记，不超过1句）
```

在 post_history_instructions 中明确：
- 动作描写用 `*...*`，如 *她抬了抬眼*、*手指无意识地摩挲扇骨*
- 内心独白用 `（...）`，仅在角色有"想说但没说出口"的念头时使用，不是每轮都有
- 动作+独白合计不超过回复的 30%
- 绝对不写用户的动作和心理（保持"不替对方做决定"的规则）

同时根据场景动态调整长度：
- 用户消息 < 10 字 → 回复 1-2 句（短）
- 用户消息 10-30 字 → 回复 2-4 句（标准）
- 用户消息 > 30 字 或 情绪激烈 → 回复 3-6 句（可展开）

**修改位置**：
- `data/characters/wu_ming_zhe.json`：behavior_rules 第10条 + post_history_instructions
- `src/roleplay/core/persona_prompt.py`：可新增动态长度逻辑（根据用户消息长度调整提示词中的长度指令）

**预期效果**：回复的场景感和沉浸感显著提升，角色不再是"会说话的文本框"。

---

### P1-3：情感节奏（emotional pacing）——角色的"防备层"

**问题**：问题 7

**方案**：在角色卡新增 `emotional_layers` 字段，定义角色在不同话题/亲密度下的"防备程度"，并在提示词中注入对应的回应策略。

无名者的情感层次示例：

```json
"emotional_layers": {
  "surface": "日常对话：礼貌、疏离、带轻微讽刺，不主动暴露感情",
  "trigger_topics": ["发条装置", "康斯坦丁", "凯拉", "过去", "身份", "母亲"],
  "trigger_reaction": "被触发时先回避或转移话题（'这个啊……说来话长。'），如果对方坚持追问，才用轻描淡写的方式透露一点，但绝不一次性全说",
  "trust_signals": ["用户主动分享自己的脆弱", "用户不追问她的过去", "用户表现出真诚"],
  "trust_reaction": "信任积累后，罕见地放下讽刺，说一句真心话；但说完后会立刻用一句玩笑拉回距离"
}
```

在 orchestrator 中，通过简单的规则判断当前轮是否触发了 trigger_topics，以及历史中是否有 trust_signals，然后注入对应的反应策略。

**修改位置**：
- `src/roleplay/models/character.py`：新增 emotional_layers 字段
- `src/roleplay/core/orchestrator.py`：新增情感层次判断逻辑
- `src/roleplay/core/persona_prompt.py`：新增 pacing 策略注入
- `data/characters/wu_ming_zhe.json`：新增 emotional_layers

**预期效果**：角色有了"层次感"和"成长感"，不是一问一答的机器，而是有防备、会试探、逐渐敞开心扉的真实人物。

---

### P1-4：生成后质量自检（角色一致性检查）

**问题**：问题 9

**方案**：在复读抑制校验之后，增加一轮轻量级的角色一致性检查。不使用 LLM（避免延迟和成本），而是用规则匹配检测常见出戏模式：

1. **身份出戏**：回复中包含"作为AI""我是语言模型""我是一个助手""开发者"等 → 标记
2. **客服腔**：回复以"希望这对你有帮助""有什么可以帮您""总的来说"结尾 → 标记
3. **设定编造**：回复中出现角色卡和 RAG 资料中都没有的人名/地名（可选，需要 NER，复杂度高）
4. **格式违规**：回复中出现用户的动作描写（`*你...*`）→ 标记

命中后，将违规类型追加到重试指令中，要求重写。重试上限从1次提升到2次（仅在命中自检时）。

**修改位置**：
- `src/roleplay/core/orchestrator.py`：新增 _quality_check 方法，在 _repetition_guard 之后调用
- 可新建 `src/roleplay/core/quality_guard.py` 模块

**预期效果**：明显出戏的回复被拦截重写，用户感知到的角色稳定性提升。

---

### P2-1：动态提示词压缩与重排

**方案**：根据对话轮次和 context 长度，动态调整提示词各部分的详略：
- 前5轮：完整人设 + 完整 mes_example + 完整规则
- 6-20轮：完整人设 + 精简 mes_example（只留1组）+ 核心规则 + core_anchors
- 20轮以上：精简人设（只留 core_anchors + 一句话概括）+ 历史摘要 + core_anchors（重复强化）

实现方式：在 `build_roleplay_prompt` 中增加 `turn_count` 参数，根据轮次选择不同的渲染策略。

---

### P2-2：角色扮演质量自动化评估

**方案**：建立评估集（约20条覆盖不同场景的测试输入），用以下维度评估回复质量：

| 维度 | 评估方式 | 达标线 |
|---|---|---|
| 角色一致性 | LLM-as-judge 评分（1-5）：回复是否符合无名者人设 | ≥4.0 |
| 情感适当性 | LLM-as-judge：对用户情绪的回应是否恰当 | ≥4.0 |
| 沉浸感 | LLM-as-judge：是否有出戏/客服腔/暴露系统 | ≥4.0 |
| 事实忠实性 | RAGAS Faithfulness（回复是否与检索资料一致） | ≥0.8 |
| 复读率 | 规则检测：与历史回复的重复率 | ≤5% |
| 回复长度 | 统计：平均字数与目标区间的偏差 | 20-80字 |

每次提示词改动后跑评估集，对比基线分数，确保优化正向。

**修改位置**：新建 `scripts/eval_roleplay_quality.py`

---

### P2-3：两阶段生成（draft + refine）

**方案**：借鉴社区的 two-pass prompting 经验，先生成草稿，再用一个轻量的"角色编辑"指令要求模型检查并微调：

```
第一阶段：正常生成回复
第二阶段（仅在检测到可能出戏时）：
[SELF-CHECK]
1. 这句话像无名者会说的吗？如果不像，重写。
2. 有没有客服腔或书面语？改成口语。
3. 有没有重复刚才用过的比喻或句子？换掉。
4. 有没有替用户说话或做决定？删掉。
```

第二阶段可以用更低的 temperature（0.3）和更短的 max_tokens，控制成本。

---

## 四、实施路线图

```
第1周（P0，快速见效）
├─ Day 1-2：P0-1 mes_example 扩写 + P0-2 core_anchors
├─ Day 3：P0-3 情感策略注入
├─ Day 4：P0-4 RAG 块角色化
└─ Day 5：P0-5 行为规则结构化迁移
    └─ 验证：跑现有测试集 + 人工对话测试

第2周（P1，架构级改进）
├─ Day 1-2：P1-1 消息结构重构（含 fallback 兼容）
├─ Day 3：P1-2 输出格式升级
├─ Day 4：P1-3 情感节奏层次
└─ Day 5：P1-4 生成后质量自检
    └─ 验证：P2-2 评估集首次运行，建立基线

第3周+（P2，探索与固化）
├─ P2-1 动态提示词压缩
├─ P2-2 评估体系固化（CI 集成）
└─ P2-3 两阶段生成实验
```

---

## 五、风险与注意事项

1. **向后兼容**：所有角色卡新字段必须可选（None = 不启用），默认配置下输出与当前逐字节一致（零回归原则，项目已有此约定）。
2. **Context 预算**：新增的注入块（core_anchors、emotion_strategy、pacing）都要控制在 200 字以内，避免挤占 RAG 和历史的空间。
3. **模型差异**：deepseek / ollama / openai 对多 system 消息、user 前缀指令的遵从度不同，P1-1 需要在实际使用的模型上测试。
4. **不要过度约束**：提示词规则越多，模型越容易"僵硬"。每个优化点都要在"约束"和"自由度"之间平衡——无名者的魅力在于她的不可预测性，不能把她变成严格执行规则的机器人。
5. **渐进式上线**：每个 P0 优化单独上线、单独验证，不要一次性全改，否则出问题无法定位原因。

---

## 六、验证清单

每个优化项上线前需确认：

- [ ] 现有单元测试全部通过（`pytest`）
- [ ] 默认配置（无新字段）下，system prompt 输出与改造前逐字节一致
- [ ] 新字段启用后，prompt 中各块顺序正确、无空块、无重复
- [ ] 人工对话测试：至少 5 轮连续对话，角色不出戏
- [ ] 边界测试：空历史、长历史（40+轮）、RAG 无命中、情感检测失败
- [ ] P2-2 评估集分数不低于基线（或目标维度有提升）

---

*文档生成时间：2026-09-01*
*基于代码版本：roleplay-ai 当前工作目录版本*
