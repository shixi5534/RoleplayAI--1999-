# 角色提示词注入系统优化 —— P1 阶段交付报告

> 项目：roleplay-ai（无名者 Ms. Stranger）
> 范围：P1-1 消息结构重构 / P1-2 输出格式升级 / P1-3 情感节奏 / P1-4 生成后质量自检
> 日期：2026-09-02
> 基线：P0 五项已完成（18/18 通过）

---

## 一、总览

| 项 | 问题 | 方案 | 状态 |
|---|---|---|---|
| P1-1 | 所有内容塞进单一 system，注意力分配不均 | 分层：人设/语气/画像/资料各成 system 消息，动态指令进 user 前缀 | ✅ |
| P1-2 | 输出格式过于保守，限制沉浸感 | 动作 `*…*` + 内心独白 `（…）` 结构化格式 + 动态长度分档 | ✅ |
| P1-3 | 缺少情感节奏，角色过于"配合" | `emotional_layers` 防备层：基线 / 敏感话题 / 信任积累三层 | ✅ |
| P1-4 | 生成后只查复读，不查角色一致性 | `quality_guard` 纯规则自检：身份出戏 / 客服腔 / 格式违规 | ✅ |

**测试**：新增 `tests/test_prompt_p1.py`（31 用例，全通过）；全量 **462 passed / 2 skipped**，零回归。

---

## 二、P1-1 消息结构重构

### 改动

- `persona_prompt.py`
  - 抽出 `_compose_prompt_parts()`，把提示词算成三段：
    `persona`（核心人设）/ `context_blocks`（语气·画像·RAG）/ `tail_blocks`（置底动态指令）。
  - 新增 `build_roleplay_messages()` → 返回 `PromptLayers(system_blocks, user_prefix)`。
  - `build_roleplay_prompt()` 改为复用同一函数后按 `"\n\n"` 拼接——**两条路径块内容与顺序完全一致**，
    有测试断言 `prompt == "\n\n".join([*system_blocks, user_prefix])`。
  - 新增 `resolve_source_card()` / `resolve_prompt_config()`，供编排层在拼装前判断开关，
    避免与内部解析逻辑漂移。
- `llm/base.py` / `openai_like.py` / `mock.py`
  - `generate()` / `generate_stream()` 新增**可选**参数 `system_blocks` / `user_prefix`。
  - `_build_messages()`：`system_blocks` 非空时每个块各成一条 system 消息（跳过空白块）；
    `user_prefix` 非空时拼在当前 user 消息之前。
- `orchestrator.py`
  - `_build_prompt()` 返回 `(system_prompt, layers)`；新增 `_llm_extra()` 只在分层模式下
    返回那两个参数——**未启用时返回空 dict，用 `**extra` 展开即完全不传**，
    因此不兼容的第三方 `LLMPort` 与测试替身不会收到未知参数。
  - 新增 `_prepare_full()`（4 元组）；保留 `_prepare()` 3 元组作为兼容入口（6 处测试调用未受影响）。
- `prompt_config.py`：新增 `message_layering: bool = False`（默认关闭＝零回归）。

### 消息形态

```
system[0]  核心人设（name+personality+behavior_rules+lorebook）   ← 首因效应
system[1]  【语气要求】
system[2]  【用户资料】
system[3]  【你记得的事】RAG 记忆碎片
...history...
user       【此刻对方的状态】→【此刻你的姿态】→【说话方式】→【本轮长度】
           →【别忘了你是谁】→【别说重复的话】
           （空行）
           用户原话                                              ← 近因效应最强
```

动态长度刻意排在 footer 之后，才能覆盖卡内静态的「每条 2–4 句」。

---

## 三、P1-2 输出格式升级与动态长度

### 角色卡（`data` 与 `assets` 两张卡同步）

- `behavior_rules` 第 6 条：从「只写自己说的话和极少的动作」改为结构化格式——
  主体是说话，动作写 `*…*`、想说没说出口的念头写 `（…）`，合计不超过三成；
  禁止写对方的动作/反应/心理。
- `post_history_instructions`：新增【格式】两条，并让静态句数要求让位于【本轮长度】。

### 动态长度

新增 `build_length_hint(message, emotion)`：

| 用户消息字数 | 目标句数 |
|---|---|
| < 10 | 1-2 句 |
| 10–30 | 2-4 句 |
| > 30 | 3-6 句 |

命中高唤醒情绪（`angry/sad/anxious/fear/surprise/disappointed/lonely/embarrassed/confused`）
时整体上调一档，封顶 3-6 句。由 `prompt_config.dynamic_length` 控制，默认关闭。

---

## 四、P1-3 情感节奏（防备层）

### 数据模型

`CharacterCard` / `CharacterUpsert` 新增 `emotional_layers`：

```json
{
  "surface":          "日常基线姿态（疏离/礼貌/轻讽）",
  "trigger_topics":   ["发条装置", "康斯坦丁", "凯拉", "过去", "身份", ...],
  "trigger_reaction": "被触发时先回避，追问才透露一点",
  "trust_signals":    ["对方主动示弱", "不追问你的过去", "说话算话"],
  "trust_reaction":   "罕见地放下讽刺说句真心话，再用玩笑拉回"
}
```

- 清洗：未知键丢弃、列表去空白去重、非 dict → `None`。
- 用 `mode="before"` 校验器：坏值收敛为 `None` 而不是抛异常把整张卡打回默认提示词
  （比 `core_anchors`/`emotion_strategies` 更宽松是刻意的——这是可选增强字段）。
- 空 dict 保留为 `{}`，与 `None` 区分，供「清空该字段」语义（同 P0-2/P0-3）。

### 解析逻辑 `resolve_pacing_strategy()`

`surface` 恒作底，条件层**互斥叠加**：

1. 当前用户消息命中 `trigger_topics` → 叠加 `trigger_reaction`
2. **elif** 累计轮次 ≥ `TRUST_TURN_THRESHOLD`（默认 6）→ 叠加 `trust_reaction`

用 `elif` 是刻意的：被踩到敏感话题时不会同时"敞开心扉"，防备优先。

> 已知取舍：真实"信任"应来自语义信号（主动示弱、不追问过去），规则层难以可靠判定，
> 故用**累计对话轮次**作为可预测、可单测的代理指标。阈值可按角色卡调整。

---

## 五、P1-4 生成后质量自检

新增 `src/roleplay/core/quality_guard.py`（纯规则、无 LLM、零延迟）：

| 类型 | 检测 | 例 |
|---|---|---|
| `identity` | 自称 AI/程序/助手 | 作为AI、我是语言模型、ChatGPT |
| `service` | 客套/总结收尾 | 希望这对你有帮助、有什么可以帮您、总的来说 |
| `format` | 写了对方的动作 | `*你愣了一下*` |

- 同类只报第一条（重试指令已足够指明问题，重复罗列只挤占提示词）。
- 客服腔判定时先剥掉尾部标点/引号再 `endswith`，避免句号导致漏判。
- 编排层接线：`run()` 在复读抑制校验之后调用，命中则追加 `quality_retry_hint()` 重写，
  与复读抑制**独立计次**，上限 `quality_guard_max_retries`（默认 2）；耗尽仍出戏则接受当前回复。
- 流式路径不重试（token 已发出不可撤回）。

---

## 六、验证

```
pytest tests/            → 462 passed, 2 skipped
pytest tests/test_prompt_p1.py -v → 31 passed
node tests/test_pet_master_plan.js → ALL TESTS PASSED
```

### 端到端冒烟（真实角色卡）

三system 块（人设 1348 字 / 语气 101 字 / 资料 379 字），user_prefix 按
情绪策略 → 情感节奏 → 说话方式 → 本轮长度 → 核心锚点 → 复读抑制 排列。

- 「今天天气不错」轮次 1 → 只有 `surface`
- 「聊聊你的过去吧」→ 叠加 `trigger_reaction`（且 Lorebook 被"过去"触发，人设块增到 1413 字）
- 「我今天有点撑不住了」轮次 8 → 叠加 `trust_reaction`

### 零回归清单

- 默认配置下 `build_roleplay_prompt` 输出与改造前逐字节一致（P0 的 18 个用例 + 新增断言覆盖）。
- 未开 `message_layering` 时，LLM **收不到** `system_blocks` / `user_prefix` 两个参数。
- 未开 `dynamic_length` 时提示词里不出现【本轮长度】。
- 未配置 `emotional_layers` 时不出现【此刻你的姿态】。
- 关闭 `quality_guard_enabled` 时不产生任何额外 LLM 调用。

---

## 七、改动文件

| 文件 | 说明 |
|---|---|
| `src/roleplay/core/persona_prompt.py` | 三段拆分、`build_roleplay_messages`、长度/节奏块、配置解析 |
| `src/roleplay/core/quality_guard.py` | **新增** P1-4 规则自检 |
| `src/roleplay/core/orchestrator.py` | 分层传参、自检重试、turn_count 透传 |
| `src/roleplay/core/llm/base.py` | 端口契约新增两个可选参数 |
| `src/roleplay/core/llm/openai_like.py` | `_build_messages` 支持分层 |
| `src/roleplay/core/llm/mock.py` | 契约对齐（忽略分层参数） |
| `src/roleplay/models/character.py` | `emotional_layers` + 清洗 |
| `src/roleplay/models/prompt_config.py` | `message_layering` / `dynamic_length` 开关 |
| `src/roleplay/core/knowledge/character_store.py` | `emotional_layers` 映射，防更新丢字段 |
| `data/characters/wu_ming_zhe.json` | P1-2/P1-3 内容 + 两个开关置 true |
| `src/roleplay/assets/characters/wu_ming_zhe.json` | 同上（与 data 卡保持一致） |
| `frontend/index.html`、`frontend/js/chat.js` | 情感节奏 JSON 编辑框 + 非法 JSON 保存拦截 |
| `tests/test_prompt_p1.py` | **新增** 31 用例 |

---

## 八、风险与回滚

1. **多 system 消息兼容性**：部分 OpenAI 兼容端点（尤其 Ollama 旧版本）对多条 system 的
   处理不一致。当前已在**无名者卡**上启用 `message_layering`。
   **一键回滚**：把该卡 `prompt_config.message_layering` 改为 `false`（或直接删除该键），
   立即回落到单 system 模式，其余 P1 能力不受影响。
   计划文档建议在实际使用的模型（deepseek / ollama）上各跑一轮对比再长期保留。
2. **`dynamic_length` 与卡内静态句数**冲突时以【本轮长度】为准（它排在 footer 之后）。
   若觉得分档不合适，改 `persona_prompt._LENGTH_BANDS` 或关掉该开关。
3. **信任层用轮次代理**：默认 6 轮，可能让角色"过早敞开心扉"。调
   `persona_prompt.TRUST_TURN_THRESHOLD` 或角色卡覆盖。
4. **质量自检误伤**：词表集中在 `quality_guard.py` 顶部，便于按角色增删；
   命中只会触发一次重写，误判代价可控。
