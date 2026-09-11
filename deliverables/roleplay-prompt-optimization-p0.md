# 角色提示词注入系统优化 · P0 阶段交付报告

> 项目：roleplay-ai（无名者 Ms. Stranger）
> 阶段：P0（高价值/低成本，5 项）
> 时间：2026-09-01
> 基于计划：`ROLEPLAY_PROMPT_OPTIMIZATION_PLAN.md`

---

## 一、目标达成

按计划的优先级定义，**P0 阶段 5 项全部完成**：

| 计划项 | 内容 | 状态 |
|---|---|---|
| P0-1 | mes_example 扩写为 3 组情绪对话对 | ✅ |
| P0-2 | core_anchors 核心锚点每轮置底注入 | ✅ |
| P0-3 | emotion_strategies 情绪策略动态注入 | ✅ |
| P0-4 | RAG 块角色化（去编号、记忆碎片格式） | ✅ |
| P0-5 | 行为规则结构化迁移 + merge 开关 | ✅ |

> 说明：计划文档原计划把 P0-3 的查表逻辑放在 `orchestrator._prepare` 里注入新参数，
> 实际实现时改为在 `build_roleplay_prompt` 内部由 `source_card.emotion_strategies` +
> 已有的 `emotion` 参数直接查表（单一事实源，避免签名改动与重复解析），**功能等价且更内聚**。

---

## 二、改动清单（文件级）

### 后端（无回归核心约定）
- `src/roleplay/models/character.py`
  - `CharacterCard` / `CharacterUpsert` 新增可选字段 `core_anchors: list[str]`、
    `emotion_strategies: dict[str, str]`，均带标准化 validator（锚点逐条轻量清洗、
    策略表键小写归一；空 list/dict 保留以区分「清空」与「未提供」）。
  - 模块级 `_normalize_anchor_list` / `_normalize_strategy_map` 供两处模型共用。
- `src/roleplay/models/prompt_config.py`
  - 新增 `merge_structured_rules: bool = False`：结构化规则与文本规则的合并模式开关。
- `src/roleplay/core/persona_prompt.py`
  - 新增 `build_core_anchors_block` / `build_emotion_strategy_block` / `resolve_emotion_strategy`。
  - 置底块顺序：`资料块 → 情绪策略 → footer_fields → 核心锚点 → 复读抑制`。
  - `build_rag_context` 条目格式由 `[i] (来源) 正文` 改为 `（来源）正文`；`_CONTEXT_HEADER`
    新增「片段是你脑子里冒出来的」守则。
- `src/roleplay/core/character_card.py`
  - 抽出 `_render_behavior_rules`：按 `merge_structured_rules` 决定「命中即替换（默认，
    零回归）」或「文本常驻 + 命中规则叠加」。
- `src/roleplay/core/behavior_rules.py`
  - `match_condition` 的 `emotion_is` 支持 `|` 分隔多值（如 `sad|fear|anxious`），单值语义不变。
- `src/roleplay/core/knowledge/character_store.py`
  - `_build_card` 同步映射 `core_anchors` / `emotion_strategies`，避免 API 更新丢字段。

### 角色卡（两张卡同步）
- `data/characters/wu_ming_zhe.json`（运行时，被 `.gitignore` 忽略，已落盘）
- `src/roleplay/assets/characters/wu_ming_zhe.json`（内置种子/兜底，与数据卡同步 P0 字段，
  保留其自有 `knowledge_scope`）
- 改动：mes_example 三组对话对（≤600 字，去掉与自定义模板重复的标题行）；
  core_anchors（5 条 ≤20 字）；emotion_strategies（覆盖全部 15 类情绪标签）；
  behavior_rules 精简为 6 条核心 + 4 条结构化条件规则；`prompt_config` 开启
  `merge_structured_rules: true` 并改写 rag header 为记忆碎片口吻。

### 前端（满足「可配置一切」约定）
- `frontend/index.html`：角色编辑表单新增「核心锚点」「情绪回应策略」两个文本域。
- `frontend/js/chat.js`：`fillForm` / `readForm` 支持两字段的「数组↔每行一条」
  「对象↔每行 标签: 策略」双向转换。

### 脚本
- `scripts/eval_rag_standard.py`：`_split_context_blocks` 适配新条目格式（行首全角括号切分）。

### 测试
- 新增 `tests/test_prompt_p0.py`（18 用例，覆盖五项 + 零回归断言 + 字段落盘/清空）。

---

## 三、验证结果

- **单元测试全量**：`pytest -q` → **432 passed, 1 skipped**（原 414 + 新增 18）。
- **零回归断言全部通过**：
  - 未配置新字段（含 `null` / `[]` / `{}`）时，system prompt 与改造前逐字节一致；
  - 默认 `merge_structured_rules=False` 时行为规则「命中即替换」语义不变。
- **结构验证脚本（JSON 解析 + 字段约束）**：两张角色卡均能解析，
  core_anchors 3–5 条且每条 ≤20 字，emotion_strategies 覆盖 15 类标签，
  behavior_rules_structured 全部通过引擎校验（无非法规则被静默丢弃）。
- **端到端渲染抽查**：真实角色卡在「你到底是谁 / 难过 / 是否 AI」等输入下，
  条件规则按正则/情绪正确触发，核心文本规则常驻，核心锚点与情绪策略块位于置底，符合要求。
- **前端 JS 语法**：`node --check frontend/js/chat.js` 通过。
- **前端冒烟测试 `tests/test_pet_master_plan.js`**：4 个失败项**全部位于 `pet.html` 桌面宠物**
  （模型/气泡大小与锁位菜单、方向 C token、点击反馈层、错误层 display:none），
  与本次 P0 角色提示词改动无关——本次未触碰 `pet.html`/`pet.js`/`spine.js`，属既有问题，
  不在本计划范围内。

---

## 四、已知约束 / 后续

1. **Context 预算**：core_anchors（约 80 字）+ emotion_strategy（约 40 字）+ 4 条结构化规则
   （约 200 字）均控制在 200 字内，未挤占 RAG/历史空间。
2. **向后兼容**：所有新字段可选；默认配置输出逐字节一致。
3. **P1/P2 待办**（按计划路线图）：消息结构分层重构、动作/独白输出格式、情感节奏层次、
   生成后质量自检、动态压缩、评估集固化、两阶段生成。
4. **建议下一步**：跑 `P2-2 评估集`（脚本 `scripts/eval_rag_standard.py` 已适配新格式）
   建立 P0 基线，再推进 P1。
