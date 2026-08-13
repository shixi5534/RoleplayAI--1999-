# roleplay-ai 升级方案：从「写提示词」到「系统性工程」

> 版本：v1.1 ｜ 日期：2026-08-13 ｜ 状态：**P0/P1 已实施并验证（B/A/D/C），P2 未实施**
>
> 参考输入：GitHub 开源项目（Poppet / NemoEngine / RoleCard / Codified Profiles / Echo Protocol 等）
> 与 2025-2026 研究趋势（结构化规则、记忆驱动、人格一致性）。
>
> **实施记录（2026-08-13）**：
> - ✅ P0-B 会话摘要落盘复用（`<sid>.summary.json` + 增量压缩 + 长度稳定合并）
> - ✅ P0-A 结构化 if-then 行为规则（`core/behavior_rules.py` + `behavior_rules_structured` 字段）
> - ✅ P1-D 提示词模板可配置（`models/prompt_config.py` + 角色卡 `prompt_config` + 全局 `prompt_config_path`）
> - ✅ P1-C 长期记忆结构化（`core/knowledge/event_extractor.py` + `consolidate_entries` + `event_extract_enabled` 开关）
> - ⬜ P2-E Lorebook 双触发 / P2-F 人格档案：未实施
> - 验证：项目测试 344 passed、1 skipped；默认输出零回归（逐字节一致）；端到端结构化规则实测生效

---

## 0. 现状关键事实（已核实）

| 模块 | 文件 | 关键事实 |
|---|---|---|
| 角色卡 | `src/roleplay/models/character.py` | `CharacterCard`：V2 字段超集（name/personality/scenario/background/behavior_rules/tone/first_mes/mes_example/post_history_instructions/system_prompt/character_book/knowledge_scope/voice_id/tts_*）；JSON 存 `data/characters/<cid>.json` |
| 行为规则 | 同上 | `behavior_rules: str` **自由文本**，仅 normalize 做编号列表化，无结构化 if-then 数据 |
| Lorebook | `src/roleplay/core/character_card.py` `_build_lorebook` | `character_book.entries[].keys` 对 message 做 **substring 匹配**，无 LLM 触发/无相关性加权 |
| 提示词拼装 | `src/roleplay/core/character_card.py` `resolve_system_prompt` + `src/roleplay/core/persona_prompt.py` `build_roleplay_prompt` | 固定顺序：人设→语气→【用户资料】→【角色资料库】；**无字段开关/无模板配置** |
| 短期记忆 | `src/roleplay/core/session_memory.py` | `<sid>.json` 为 `[{role,content,ts}]` 数组（`_load_all` 直接解析，**格式不可破坏**）；40 轮上限 |
| 会话摘要 | `src/roleplay/core/orchestrator.py` L359-389 `_summarize_history` | 历史超 40 条时 LLM 压缩旧一半；**只存当次请求 messages，不落盘、每轮重复压缩** |
| 长期记忆 | `src/roleplay/core/knowledge/memory_tier.py` L58-80 `consolidate` | 每 6 轮把游标后新轮次**整段拼成一条**向量 → `events:<cid>`；衰减+重要性排序（设计合理） |
| 用户画像 | `src/roleplay/core/knowledge/extractors.py` | Rule 正则（confidence=0.3 兜底）+ LLM（超时+三级 JSON 解析+永不抛出）组合降级——**C/F 可复用的健壮范式** |
| 情绪 | `src/roleplay/core/emotion/detector.py` | 三层责任链 LLM→classifier→keyword，驱动 live2d |
| 配置 | `src/roleplay/config.py` | `Settings`（ROLEPLAY_ 前缀，.env 可覆盖，frozen 运行期不可变） |

**数据现状**：`data/knowledge/events.json` = `[]`（长期记忆为空）、`profile.json` 不存在 → 新增命名空间/条目安全，无迁移负担。

---

## 1. 差距分析（按影响面排序）

| 编号 | 差距 | 影响 | 对应方向 |
|---|---|---|---|
| **G1** | 行为规则是自由文本，无法程序化触发/排序/开关 | 规则仍是"提示"，小模型遵守不稳定；无法按条件动态注入 | 定规则 |
| **G2** | 会话摘要不落盘，超阈值后每轮重复 LLM 压缩同一批旧历史 | token 持续浪费；摘要每次生成不稳定，前后不一致 | 管记忆 |
| **G3** | 长期记忆整段文本合并成单条向量 | 单条信息密度低、噪音高；无法做"角色记住了某事实"细粒度查询 | 管记忆 |
| **G4** | 提示词拼装写死固定顺序 | 加字段/调顺序/自定义模板需改代码 | 系统工程 |
| **G5** | Lorebook 纯 substring 匹配 | 用户改写表达（同义转述）漏触发，设定补全不稳定 | 定规则 |
| **G6** | 无角色人格档案 | 极长对话行为漂移无矫正手段 | 管记忆 |

---

## 2. 升级项设计

### A. 结构化 if-then 行为规则（P0）

**目标**：让角色行为规则可程序化判定与注入，小模型也能稳定遵守。

**数据结构**（`models/character.py` 新增可选字段 `behavior_rules_structured`，原 `behavior_rules` 文本字段**保留不动**以兼容旧卡）：

```json
{
  "behavior_rules_structured": [
    {
      "id": "rule-001",
      "condition": {
        "type": "text_contains | text_regex | emotion_is",
        "field": "user_message | current_emotion",
        "pattern": "你是谁",
        "case_sensitive": false
      },
      "action": "列出几个名字后说「现在，这里只有无名者」",
      "priority": 10,
      "enabled": true,
      "category": "identity"
    }
  ]
}
```

**新引擎**：`src/roleplay/core/behavior_rules.py`（纯函数、无副作用）
- `match_condition(cond, context) -> bool`：子串/正则/情绪标签代码判定，**零 LLM 开销**
- `render_rules(rules, context) -> str`：按 priority 排序，仅注入命中的 enabled 规则
- 校验：pattern 非空、正则试编译、规则数上限 50、id 去重；**非法规则丢弃不阻断卡片加载**

**注入点**：`character_card.py` `resolve_system_prompt` —— 结构化规则非空走规则块（`【行为规则】`段落），否则走原文本 → **向后兼容**。

**复杂度**：中 ｜ **风险**：低（可选字段 + 纯代码判定，无幻觉）

---

### B. 会话摘要落盘复用（P0）

**目标**：摘要持久化，跨请求复用，停止每轮重复烧 token。

**存储**：独立文件 `<session_dir>/<sid>.summary.json`（**不改** session 数组结构，`_load_all` 不受影响）：

```json
{
  "summary_text": "用户与无名者聊了入学准备、对学校的期待……",
  "covered_turns": 30,
  "updated_at": 1723456789.123,
  "model": "qwen2.5:1.5b"
}
```

**改动**：
- `session_memory.py` 增 `get_summary(sid) / save_summary(sid, data)`（复用原子写 `_save` 模式）；`clear()` 同步删除 summary 文件
- `orchestrator._summarize_history` 改**增量**：仅对 `(covered_turns, len(history)-keep)` 区间新片段做 LLM 摘要，与旧摘要合并覆盖；LLM 失败回退旧摘要（不重新压缩）

**复杂度**：低 ｜ **风险**：低（独立文件，不碰 session 格式；增量逻辑清晰）

---

### C. 长期记忆结构化（P1）

**目标**：从"整段文本合并"升级为"事实/事件级提取"，支持细粒度查询与注入。

**新文件**：`src/roleplay/core/knowledge/event_extractor.py`（复刻 `LLMProfileExtractor` 范式）：
- LLM 输出 `[{type: "fact|event", content, subject, predicate, object, importance}]`，`asyncio.wait_for(timeout)` + 三级 JSON 解析 + 永不抛出
- Rule 兜底：按 `_IMPORTANCE_HINTS` 关键词切句，直接取句作为 fact

**存储**：**仍用 `events:<cid>` 命名空间**（兼容旧数据、检索公式不变）：
- text 改单句事实；meta 增 `{type, subject, predicate, object, confidence, occurred_round}`
- 旧整段条目照常可检索（无迁移成本）

**改动**：`memory_tier.consolidate` 由整段一条改为逐条写入（每次 LLM 一次调用，产出多条向量）。

**复杂度**：中 ｜ **风险**：中（每 6 轮额外一次 LLM 调用 → 需配开关 `event_extract_enabled`，参考 `profile_extract_every` 的成本控制）

---

### D. 提示词模板可配置（P1）

**目标**：加字段/调顺序/自定义模板不再改代码。

**新模型**：角色卡内嵌 `prompt_config`：

```json
{
  "prompt_config": {
    "enabled_fields": ["name", "personality", "background", "behavior_rules",
                       "scenario", "first_mes", "mes_example", "tone",
                       "profile", "rag"],
    "field_order": ["name", "personality", "background", "scenario",
                    "behavior_rules", "tone", "profile", "rag"],
    "custom_templates": { "personality": "性格：{value}" },
    "header_templates": { "profile": "【关于用户】" }
  }
}
```

**全局层**：`config.py` 增 `prompt_config_path`（留空=默认，输出与现状逐字节一致，**零回归**）；角色卡级覆盖全局。

**重构**：`persona_prompt.py` 改为「按字段渲染 → 按 order/enabled 组装」；A 的规则块作为 `behavior_rules` 字段接入该管线。

**复杂度**：中 ｜ **风险**：中（拼装核心重构，需回归测试确认默认输出不变）

---

### E. Lorebook 智能触发（P2 可选）

- 保留 substring 快速路；可选 LLM 路输出命中 entry id 并集，按 `insertion_order` + 相关性排序
- 配置 `lorebook_llm_trigger: bool = False`（默认关，失败回退 substring）

**复杂度**：低-中 ｜ **风险**：低（默认关 + 失败回退）

---

### F. 人格一致性守护（P2 可选）

**目标**：借鉴"持续更新人格档案"，防止长对话人格漂移。

- 新增 `core/knowledge/character_profile.py`（完全参照 UserProfile 架构），命名空间 `charprofile:<cid>`，条目类型 `trait/value/taboo/relationship`
- 复用 C 的提取器基础设施；检索时加入 `resolve_knowledge_namespaces`
- 默认关；需明确优先级：**静态人设卡为准、动态档案仅补充**

**复杂度**：高 ｜ **风险**：中（需人设优先级规则清晰，否则档案可能"教坏"角色）

---

## 3. 优先级与取舍

| 项 | 优先级 | 收益/成本 | 不做会怎样 |
|---|---|---|---|
| **B 摘要落盘** | **P0** | 高/低（最值得先做） | 长会话 token 浪费持续累积；摘要每轮不一致 |
| **A 结构化规则** | **P0** | 高/中 | 规则仍是"提示"，小模型遵守不稳定 |
| **D 模板可配置** | P1 | 中/中 | 加字段调顺序均需改代码 |
| **C 记忆结构化** | P1 | 中高/中 | 长期记忆维持整段噪音 |
| **E Lorebook 触发** | P2 | 中/低 | 关键词改写漏触发（可接受） |
| **F 一致性守护** | P2 | 中/高 | 极长对话轻微漂移（可接受） |

**明确取舍**：
- **走提示词工程路线（不微调）**：保留模型推理能力、无重训成本、无"泛化饱和"风险；结构化规则 + 白盒可解释是其核心支撑
- **跳过学术前沿**：SAE / 机制可解释性（RESGA/SAEGA）属研究方向，本项目不涉及
- **提示词工程受安全限制产生极端情绪**：与项目定位（克制型情感表达）一致，不构成问题

---

## 4. 实施顺序建议（每阶段可独立验证）

```
阶段 1 [P0] B 会话摘要落盘
        → 验证：.summary.json 出现；同一会话第二三轮 LLM 调用数下降；摘要稳定

阶段 2 [P0→P1] A 结构化规则 → D 提示词模板
        → A 独立落地先见收益（规则可程序化注入）；
          D 复用 A 的拼装改造（先 A 后 D，避免两处改拼装逻辑）
        → 验证：新规则卡命中触发；默认卡输出与改造前逐字节一致（回归）

阶段 3 [P1] C 长期记忆结构化
        → 复用 extractors.py 范式；配 event_extract_enabled 开关控成本
        → 验证：events 条目为单句事实 + 结构化 meta；旧条目仍可检索

阶段 4 [P2] E Lorebook 双触发、F 人格档案（按投入逐项做）
        → F 复用 C 提取器基础设施；E 独立、默认关
```

阶段依赖：`B → (A → D) → C → (E / F)`，每阶段完成可独立跑测试与人工验证。

---

## 5. 参考映射（开源项目 → 本项目落地）

| 开源项目/研究 | 核心思想 | 本项目落地点 |
|---|---|---|
| Codified Profiles / RRP | 角色逻辑写成 if-then 可执行函数 | **A 结构化行为规则** |
| RoleCard (RC) 语言 | 结构化提示词语言 + 状态机 | A 的 `condition` 可扩展状态字段 |
| Echo Protocol / Ai-Role-Play | 持久状态架构、记忆检索 | **B 摘要落盘 + C 记忆结构化** |
| AI YOU 框架 | 持续更新人格档案防漂移 | **F 人格一致性守护** |
| Memory-Driven Role-Playing (MRPrompt) | 角色知识当内在记忆检索 | C 的记忆检索注入（已具备基础） |
| NemoEngine / Poppet 预设 | 成熟叙事预设、反 melodrama | 可沉淀为 `behavior_rules_structured` 模板样例 |

---

## 6. 待确认问题（实施前）

1. **A 的结构化规则 schema** 是否需支持 `condition.type = state_machine`（状态机字段）？—— 建议 v1 只做 `text_contains/text_regex/emotion_is`，状态机 v2 再扩
2. **B 的摘要触发阈值**是否沿用现有 `history_summary_threshold = 40`？—— 建议沿用，落盘后阈值可下调（token 成本已降）
3. **C 的 LLM 成本**：每 6 轮一次提取调用，本地 Ollama 可接受；若接云端 API 需评估——建议默认开、可关
4. **D 的默认输出**必须与现状逐字节一致（零回归）——建议把「默认 prompt_config 渲染结果」纳入自动化测试
