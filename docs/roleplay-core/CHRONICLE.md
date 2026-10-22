# 核心系统（角色扮演 / lore 向量层 / 架构 / 提示词） · 历史编年史

> 本文件由 **79 份历史过程档**合并而来（2026-09-29 首轮整理），2026-10-21 再并入 3 份「已落地的一次性报告」。
> 收录原则：已完成的一次性报告（审计 / 实验 / 验收 / 阶段总结 / 已实现的设计稿）。
> **当前权威文档仍以独立文件形式保留**，见 `docs/README.md` 索引。
>
> 原文未丢失：首轮删除前快照在 git 标签 `backup-pre-testdocs-cleanup`，2026-10-21 批次在 `backup-pre-docsclean-20261021`，
> 且每条下方记录了来源路径与 SHA-16，可用 `git show <tag>:<path>` 找回。

---

## 2026-08-13 · roleplay-ai 升级方案：从「写提示词」到「系统性工程」

- 来源：`docs/roleplay-core/architecture/UPGRADE_PLAN.md`
- SHA-16：`ee128bb2640d869d`

**要点**

- **目标**：让角色行为规则可程序化判定与注入，小模型也能稳定遵守。
- `match_condition(cond, context) -> bool`：子串/正则/情绪标签代码判定，**零 LLM 开销**
- **复杂度**：中 ｜ **风险**：低（可选字段 + 纯代码判定，无幻觉）
- **目标**：摘要持久化，跨请求复用，停止每轮重复烧 token。


## 2026-09-09 · roleplay-ai 版本库事故记录与首次提交报告

- 来源：`docs/roleplay-core/audit/git-repo-recovery-20260909.md`
- SHA-16：`3a24a2b7fb8c256c`

**要点**

- 结论：**与仓库、配置、git 版本无关**，是当前执行环境（沙箱）对


## — · 代码优化修复方案（审计确认 · 已应用）

- 来源：`docs/roleplay-core/audit/optimization-fix-plan.md`
- SHA-16：`9d7668af582ad9de`

**要点**

- 问题：结构化条目（`consolidate_entries`）的 importance 标度为 [0,1]（规则提取器 0.4/0.55、LLM 缺省 0.5、纠错下限 0.3），而整段合并（`consolidate`）标度为 [1,3]。阈值 0.6 会立即清掉全部结构化条目。
- 修复：`await fetch` 之后、改写 `modelSel` 之前复查 `providerSel.value === "ollama"`，不符则丢弃结果。
- 修复：`Promise.any` 并发探测（各自 800ms AbortController，`clearTimeout` 放 `finally`）；结果 TTL 缓存（如 5s），悬停读缓存、点击强制重探；复查定时器去重（记录 id，已存在不重复注册）。


## 2026-09-08 · RAG / GraphRAG 代码审计报告

- 来源：`docs/roleplay-core/audit/rag-graphrag-audit-20260908.md`
- SHA-16：`edae793fd65afb6c`

**要点**

- 而 `LongTermMemory.retrieve` 返回的是**原始余弦**（nomic 实测 0.5–0.75）。
- **同一个相对门** `0.85 × top1` → 只要 lore 命中够强，长期记忆必然落在门外。
- score=    49.383 via=plot_lexical      ← BM25 原始分（无上界）
- score=    46.100 via=plot_lexical


## 2026-09-01 · 角色提示词注入系统优化 · P0 阶段交付报告

- 来源：`docs/roleplay-core/prompt/roleplay-prompt-optimization-p0.md`
- SHA-16：`e414dfb54988bb1d`


## 2026-09-02 · 角色提示词注入系统优化 —— P1 阶段交付报告

- 来源：`docs/roleplay-core/prompt/roleplay-prompt-optimization-p1.md`
- SHA-16：`e609e6dfffcb8401`

**要点**

- 客服腔判定时先剥掉尾部标点/引号再 `endswith`，避免句号导致漏判。


## 2026-08-29 · roleplay-ai 角色扮演提示词优化报告（v2 · 基于实测）

- 来源：`docs/roleplay-core/prompt/roleplay-prompt-optimization.md`
- SHA-16：`42f71dfae30141ed`

**要点**

- **结论**：只在提示词里写「想说的多就分几条发」是空头支票，必须同步修渲染。
- 不要复述：开头不要重复对方刚说的话，结尾不要总结，不要写「总的来说」「希望这对你有帮助」这类收尾。
- ⚠️ **「分多条」与「主动提问」未达标**：3 次采样中「分多条」0/3、带问句 0–2/3。
- **覆盖范围 41/44**：覆盖了原库全部角色事实；丢弃 3 块纯元信息——第 0 块（整理说明）、第 35 块（来源 URL）、第 36 块（剧本转载头）。这三块不含任何角色事实，其中「使用说明：本资料按角色扮演还原需求进行结构化分类」这类文字会**提醒模型它正在读参考文档**，正是要消除的东西。

## 2026-08-31 · RAG 知识库审查与补充报告（lore_wu_ming_zhe）

- 来源：`docs/roleplay-core/audit/rag-knowledge-audit.md`
- SHA-16：`2b8ae8f28782744d`

**要点**

- **底数**：主知识库 44 块 / 15,834 字 → **99 块**；口吻库 41 块未动（后于本轮扩到 54 条）；`docs.json` 由 1 条无关内容 → 0 条；角色卡 `character_book.entries` 3 条中 2 条有错，全部重写。
- **P0/P1/P2 问题**：跨实体对比句（"她不是司辰/维尔汀"）反而引入无关实体名、制造误匹配 → 已全部删除，改纯正面描述。600 字符硬切会把「无名者：」切成「名者：」→ 新文档改短段落（**结构性限制，记入遗留**）。
- **候选池泄漏（已修）**：混合检索候选数 `top_k × candidate_mult = 2×12 = 24`，长条目"吸引子"占满池子导致「暴雨」在 top_k=2 时漏召；实测 `candidate_mult ≥ 30` 才稳定 → `config.py` 默认 12 → **30**，`.env` 显式 `ROLEPLAY_RAG_HYBRID_CANDIDATES=30`。修复后 L1/L2 全量 **42/42**。
- **`RELATIVE_SCORE_GATE` 0.6 → 0.85**（`persona_prompt.py:39`）：实测相关条目 ratio 0.89–1.00、噪声 ≤0.84，0.85 可完美切分；修「神秘术」被"神秘学家/基金会派系"污染（precision 0.80→1.00）。
- **忠实性约束收紧**：旧措辞"资料未覆盖的细节可以合理演绎"实测诱发幻觉（Faithfulness 掉到 0.50）→ 改为「只许演绎口吻/修辞，禁止添加具体事实，资料没提到的宁可留白」。
- **采样温度 0.8 → 0.6**：7B 在 0.8 下倾向放飞（纯修辞、编造对话场景）。
- **口吻库 41 → 54 条**：新增 13 条世界观第一人称条目（暴雨/暴雨症候/圣洛夫基金会/内部派系/重塑之手/司辰/神秘学家/鸽子屋/时代背景/多跳锚点×2/槲寄生/平衡伞），以「你问X？」句式开头提升问句匹配；`vector_store.py` 新增 `_ns_weight()`，`*_spoken` 命名空间加权 **1.15**（口吻优先）。
- **RAGAS 2.0 最终读数**（60 用例 / repeat=3 / 本地 7B judge）：Context Precision **0.98** ✅、Context Recall **0.88** ✅、Multi-hop **0.80** ✅、Refusal **1.00** ✅；Faithfulness **0.71** ❌、Answer Relevance **0.75** ❌ —— 两项均属**7B 生成层容量上限**（角色扮演模式下倾向"表演"而非陈述），非知识库缺陷，换 14B+ 可改善。
- **样本量教训**：21 用例时 Faithfulness 看似 0.86，扩到 60 用例后降到 0.71 —— **0.71 更接近真实**。21→60 阶段不降反升（0.66→0.71）是因为同时补了槲寄生/平衡伞锚点，**扩样本 + 修缺口必须一起做，单独扩样本只会看到"变差"**。
- **测量纪律**：7B 生成噪声约 ±0.07，单次采样不可信，须 `--repeat ≥3`；judge 会把修辞当事实声明判罚（0.66 里估 0.05–0.10 是误伤）；口吻场景题用事实型期望词会得假性 0.00，须标 `scene=True` 跳过。
- **反直觉实测**：对「发条装置」这类专有名词精确查询，BM25（alpha→1）反而比向量更准。"角色扮演就偏向量"不是普适结论 —— 当前 0.45（55% 向量）对 5/6 关键查询已最优，未全局乱调。
- **遗留**：7 个拒答里唯一失败是「你今天吃了什么早餐？」（单次采样编造"面包配茶"），属 0.6 温度下偶发表演性回答，6/7 全对说明约束整体生效 —— **不为单次噪声改 prompt**（会牺牲角色感）。


## 2026-09-01 · 角色提示词注入系统优化计划（P0–P2 全量已落地）

- 来源：`docs/roleplay-core/prompt/ROLEPLAY_PROMPT_OPTIMIZATION_PLAN.md`
- SHA-16：`cabcda94b5f53d5c`

**要点**

- **原文状态标注「计划文档，不执行」，但 15 个优化项已全部实现**（下述编号即代码里的注释记号，可直接 grep 定位）。
- **10 条现状诊断**：单一 system message 注意力分配不均 / mes_example 示范不足 / 情感检测未反向注入 / 缺核心锚点重复强化 / 输出格式过于保守 / RAG 以"外部资料"口吻注入而非"角色记忆" / 缺情感节奏 / `behavior_rules_structured` 未启用 / 缺生成后自检 / 回复长度静态。
- **P0（第 1 周）**：P0-1 mes_example 扩为 3 组完整对话对；P0-2 `core_anchors` 每轮**置底**重复注入（近因效应，`persona_prompt.py:336`）；P0-3 情绪策略表 `resolve_emotion_strategy` / `build_emotion_strategy_block`；P0-4 RAG 块角色化改写；P0-5 行为规则迁移进 `behavior_rules_structured`（`behavior_rules.py`，空/非法回落原文本，向后兼容）。
- **P1（第 2 周）**：P1-1 分层 `system_blocks` + `user_prefix`（默认仍单 system，**零回归**）；P1-2 动态长度档位（情绪激烈上调）；P1-3 情感节奏三层 `surface / trigger / trust`；P1-4 生成后质量自检（身份出戏 / 客服腔 / 格式违规三类规则 + 重试接线）。
- **P2（第 3 周+）**：P2-1 按会话轮次动态压缩人设（`character_card.py:261`）；P2-2 评估集固化（`scripts/eval_roleplay_quality.py`，20 例 10 类场景）；P2-3 两阶段生成 draft + refine。
- **达标线（`eval_roleplay_quality.py:62`）**：consistency / empathy / immersion 各 **4.0**、faithfulness **0.8**、recycle_rate **0.05**、回复字数带 **20–80**。
- **五条风险**：新字段必须可选（默认逐字节零回归）；注入块各控 **≤200 字**；deepseek/ollama/openai 对多 system 遵从度不同需实测；**不要过度约束**——无名者的魅力在不可预测性，规则越多越僵硬；渐进式上线，不要一次性全改否则无法定位。
- **测试锚点**：`tests/test_prompt_p1.py`（P1 全四项 + 零回归）、`tests/test_prompt_p2.py`（P2-1/P2-2/P2-3）。


## — · 用户画像（UserProfile）增量架构设计 —— 已实现

- 来源：`docs/roleplay-core/profile/user_profile_design.md`
- SHA-16：`db0f264f3b84f910`

**要点**

- **定位**：在「Clean Architecture + 多命名空间向量库 + LongTermMemory 分层记忆」之上加**独立 UserProfile 层**，不扩展 LongTermMemory —— 稳定属性（偏好/习惯/日期/事实）与事件叙事职责分离（ADR-1）。
- **9 条 ADR 的核心决定**：一条画像 = 一条 vector store 记录，`text` 为可读画像句、`metadata` 承载 `{type,key,value,importance,confidence,source}`（ADR-2）；提取 = 规则兜底（低置信 **0.3**、永不失败）+ LLM 优先合并（复用全局 LLMPort、JSON 数组、三级解析兜底）（ADR-3）；去重 = 精确键 + 相似度 **0.85** 同义 + correction 覆盖降权（ADR-4）；注入 = `persona_prompt` 纯函数扩展 `profile_chunks`，orchestrator 三路并行检索（ADR-5）；P1 提醒 = `check_reminders()` 扫描 `important_date`，**±3 天**内合成 chunk 注入（ADR-6）。
- **落地文件**：新增 `knowledge/profile_models.py` / `profile.py`（`class UserProfile`）/ `extractors.py`（`RuleProfileExtractor` + `LLMProfileExtractor` + `extract_profile_entries`）；改 `vector_store.py`（`list_items` 锁内浅拷贝）、`factory.py`、`orchestrator.py`（`_prepare` 第三路 + `_persist` 提取调度 + `_profile_cursor` 独立推进）、`persona_prompt.py`（`build_profile_context`）、`config.py`（8 个 `profile_*` 字段）；测试新增 `tests/test_profile.py` / `test_extractors.py`。
- **验收口径**：同 key 二次 upsert `versions==2`；相似文本同义更新不新增；correction 后 `importance` 降半且 `corrected=True`；reminder 命中 ±3 天；重启后条目仍在；SSE `emotion→chunk*→done` 契约不变。
- **零外发**：mock 模式下规则层保证离线可用，抓包零外发。

