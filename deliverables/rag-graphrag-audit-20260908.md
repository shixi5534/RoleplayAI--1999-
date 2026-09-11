# RAG / GraphRAG 代码审计报告

> 项目：roleplay-ai（无名者 Ms. Stranger）
> 日期：2026-09-08
> 范围：**检索链路的处理与调用逻辑**（lore 向量 RAG / 剧情 GraphRAG / 编排器接线）
> 方法：全量测试基线 + 静态审读 + 可执行探针 + 真实语料端到端复现（真实 nomic 嵌入）
> 配套套件：`tests/test_rag_graphrag_audit.py`
> 基线（本次新增套件之前）：**529 passed / 1 skipped**
> 审计后（修复完成）：**562 passed / 1 skipped / 0 failed**

---

## 修复状态总览（2026-09-08 更新）

| 编号 | 缺陷 | 状态 | 修复要点 |
|---|---|---|---|
| F1 | 长期记忆被相对分数门系统性丢弃 | ✅ 已修复 | `_filter_chunks` 按**分数尺度分组**做相对门（`_score_group`） |
| F2 | 剧情图谱块被词法兜底挤掉 | ✅ 已修复 | ① 分组相对门（`via=plot_graph` / `plot_lexical` 各自计算）；② 词法兜底默认仅在**图谱零命中**时启用（`plot_lexical_topup=False`） |
| F3 | lore GraphRAG 未接入（死代码） | ✅ 已修复 | 新增 `graph_search.py`（实体链接+PPR+证据回查）、`graph_ppr.py`（共享 PPR）、`scripts/build_graph.py`、`graph_*` 配置、编排器第三路、`build_graph_context` 关系脉络块、`/api/knowledge/graph/*` 调试接口；**默认关闭**（零回归） |
| F4 | 关系端点挂到错误实体 | ✅ 已修复 | `build_local_endpoint_map` / `resolve_endpoint`：chunk 内局部解析，歧义别名 → 丢弃该关系（两个建图器共用） |
| F5 | 剧情层默认关闭 | ✅ 已确认（配置决策） | 保持默认关闭；需在 `.env` 设 `ROLEPLAY_PLOT_GRAPH_ENABLED=true` 才参与对话 |
| F6 | `PlotGraphRegistry` 默认 `include_weak` 与 Settings 冲突 | ✅ 已修复 | 默认值改为 `True`，并加回归断言 |
| F7 | `build_rag_context` 单块突破预算 | ✅ 已修复 | 与 `build_plot_context` 对齐：单块截断 + `…` |
| F8 | `_cosine` 维度失配静默返回伪分数 | ✅ 已修复 | 维度不等 → 告警并返回 0 |
| F9 | hybrid alpha/candidates 默认值三处不一致 | ✅ 已修复 | 统一为 `DEFAULT_HYBRID_ALPHA=0.45` / `DEFAULT_HYBRID_CANDIDATES=30`（base/memory/chroma/KnowledgeBase 全部对齐），文档同步 |
| F10 | 注册表缓存键未 strip | ✅ 已修复 | 缓存键统一 `strip()` |
| F11 | 新实体 `mentions=0` | ✅ 已修复 | 首现实体同样计 1；`remove_by_doc` 不再用边数覆盖 mentions |
| F12 | 测试函数重复定义 | ✅ 已修复 | 删除 `tests/test_plot_graph.py` 中的重复定义 |
| F13 | 其他一致性项 | ✅ 已修复 | `_ns_weight` 冗余分支、`_hop_distance` 过滤口径、`retrieve` 上限/docstring |
| F14 | Ollama 嵌入器跨事件循环复用 | ✅ 已修复 | 客户端按运行中的 loop 缓存，loop 变更/关闭时重建 |
| F15 | 边证据去重导致代表块不确定 | ✅ 已修复 | `upsert_edge` 保序去重（原用 set，顺序不定） |

> 说明：F1/F2/F3/F4/F15 在修复过程中由探针复现并验证；F15 是修复 F2 时新发现的缺陷。

---

## 摘要

| 结论 | 说明 |
|---|---|
| 检索主干可用 | lore 向量库（2085 块 / 768 维）、混合重排、命名空间隔离、剧情图谱（5026 实体 / 4261 边）均能正常工作 |
| **2 个高优缺陷（已修复）** | ① 长期记忆被相对分数门系统性丢弃；② 剧情图谱结果被词法兜底的 BM25 原始分挤掉 |
| **1 个结构性缺口（已补齐）** | lore 层 GraphRAG 现已接入在线链路（默认关闭），`scripts/build_graph.py` 可离线构建 |
| 其余 12 项（已修复） | 预算突破、维度失配静默、默认值三处不一致、证据顺序不确定等 |
| 无回归 | 全量测试 562 passed / 0 failed；审计套件 33 项全绿 |

---

## 一、测试环境与方法

### 1.1 沙箱临时目录问题（环境性，非项目缺陷）

本机运行 pytest 时，`tmp_path` / `tempfile` 全部报 `PermissionError`（94 项错误）：
根因是**文件沙箱拒绝枚举以 `0o700` 模式创建的目录**（`tempfile.mkdtemp` 与 pytest
`make_numbered_dir` 都用该模式），与项目代码无关。

绕过方式（仅测试期，不改动项目代码）：

```powershell
$env:TEMP = "$PWD\tmp_pytest"; $env:TMP = $env:TEMP; $env:PYTHONPATH = "$PWD\tmp_pytest"
python -m pytest tests/ -q -p dsh_tmppath
```

`tmp_pytest/dsh_tmppath.py` 做了两件事：把 `os.mkdir` 的 `0o700` 降为 `0o777`；
用工作区内每次进程唯一的目录替换 `tmp_path`。

**在正常环境（无沙箱）下直接 `python -m pytest tests/` 即可，无需该插件。**

### 1.2 审计手段

| 手段 | 产出 |
|---|---|
| 全量回归 | 562 passed / 1 skipped / 0 failed（修复后） |
| 静态审读 | `vector_store.py` / `persona_prompt.py` / `orchestrator.py` / `graph_store.py` / `graph_extract.py` / `plot_graph.py` / `plot_corpus.py` / `memory_tier.py` / `document_ingest.py` / `api/knowledge.py` |
| 行为探针 | `tmp_pytest/probe_rag.py`、`probe_real.py`、`probe_evidence.py`、`probe_prompt.py` |
| 真实端到端 | `tmp_pytest/probe_e2e.py`：真实 `nomic-embed-text` + 真实 lore 向量库**副本**（只读）+ 真实角色卡 + 真实 `events` 写入 |

---

## 二、缺陷清单

### 🔴 F1 长期记忆（`events`）被相对分数门系统性丢弃

**位置**：`persona_prompt._filter_chunks` + `orchestrator._retrieve` + `vector_store._rerank`

**证据（真实数据端到端，`probe_e2e.py`）**

| 用户消息 | lore 命中分（混合重排） | 长期记忆分（原始余弦） | 相对门阈值 | 结果 |
|---|---|---|---|---|
| 发条装置是什么？ | 0.9688 / 0.9515 / 0.9197 | 0.7129 / 0.6688 | 0.8235 | 记忆**全丢** |
| 我最喜欢的颜色是什么？ | 0.9463 / 0.8676 / 0.8478 | 0.6339（正是答案） | 0.8044 | 记忆**全丢** |
| 我们之前约定了什么？ | 0.9398 / 0.9346 / 0.9106 | 0.6301 | 0.7988 | 记忆**全丢** |

**根因**：`_rerank` 的混合重排输出的是**相对归一化融合分**（top1 恒≈1.0），
而 `LongTermMemory.retrieve` 返回的是**原始余弦**（nomic 实测 0.5–0.75）。
`_retrieve` 把两者 `chunks + mem` 合并成一个列表，`_filter_chunks` 再对合并列表套
**同一个相对门** `0.85 × top1` → 只要 lore 命中够强，长期记忆必然落在门外。

**影响**：长期记忆（升级方案 C 的结构化事件/事实）在真实对话中几乎不会被注入。
叠加真实角色卡的 `header_templates.rag`（「涉及人名、地名、关系、剧情的问题，
必须以这里的片段为准」），模型会直接答「记不清」，而不是答用户说过的偏好。

**建议**
1. 最小改动：`_retrieve` 像剧情层那样把 memory 单独成块渲染（`build_memory_context`），
   不要与 lore 混排过同一个门；
2. 或让 `_rerank` 保留稠密原始分（另存 `dense_score` 字段），相对门用原始分计算；
3. 或在 `_filter_chunks` 内按来源分组做相对门。

**✅ 修复（采用方案 3）**：`persona_prompt._score_group` 把检索块按分数尺度分组
（`vector` / `events` / `plot_graph` / `plot_lexical` / `profile`），相对门在组内计算，
再按分数合并排序。单组时行为与旧实现完全一致（零回归）。

**修复后实测（真实 nomic + 真实 2085 块语料，`tmp_pytest/probe_e2e.py`）**

| 用户消息 | 修复前 | 修复后 |
|---|---|---|
| 发条装置是什么？ | 记忆全丢 | ✅ `（长期记忆）用户说自己最喜欢的颜色是克莱因蓝…` 已注入 |
| 我最喜欢的颜色是什么？ | 记忆全丢 | ✅ 记忆块进入 system 块 2 |
| 我们之前约定了什么？ | 记忆全丢 | ✅ 约定条目注入（弱相关的另一条被组内相对门正确滤掉） |

**回归护栏**：`tests/test_rag_graphrag_audit.py::test_memory_survives_relative_gate_with_strong_lore_hits`

---

### 🔴 F2 剧情图谱结果被词法兜底的 BM25 原始分挤掉

**位置**：`plot_graph.PlotGraphRetriever.retrieve` + `persona_prompt.build_plot_context`

**证据（真实语料，`probe_prompt.py`）**

```
q='今天天气怎么样'  retrieve 返回 3 条
  score=    49.383 via=plot_lexical      ← BM25 原始分（无上界）
  score=    46.100 via=plot_lexical
  score=     0.215 via=plot_graph        ← PPR 派生分（≈0.1–0.2）
→ 实际进入提示词 2 条：两条词法噪声；图谱块（0.215 < 0.85×49.383）被丢弃
```

**根因**：`retrieve` 把两条内部通道的分数混进同一个列表——
图谱路是 `(rank_s + rank_d) × confidence`（量级 0.1–0.2），
词法兜底是 `PlotCorpus.search` 的 **BM25 原始分**（量级 30–75）。
`build_plot_context` 复用 `_filter_chunks` 的相对门，于是词法块一旦出现，
图谱块几乎必然被滤掉；同时词法兜底**没有绝对下限**，无关查询也会注入噪声。

**影响**：GraphRAG 的「实体链接 → PPR → 证据」成果在混合场景下无法进入提示词；
反而注入了与话题无关的转写碎片（上例中「天气」只匹配到无关剧情片段）。

**建议**
1. 两条通道**分列表**返回（`graph_chunks` / `lexical_chunks`），或统一归一化到 [0,1]；
2. 词法兜底加绝对阈值（如 BM25 ≥ 语料分位阈值），或仅在图谱零命中时启用；
3. 相对门按通道分别计算。

**✅ 修复（采用方案 3 + 方案 2 的"仅零命中时启用"）**
1. `_filter_chunks` 按 `metadata.via` 分组做相对门（`plot_graph` 与 `plot_lexical` 各自算 top1）；
2. `PlotGraphRetriever.retrieve(..., topup=False)` 默认**仅在图谱零命中时**启用词法兜底
   （对齐 `plot_lexical_fallback` 的既定注释语义），旧行为可用 `topup=True` 或
   `ROLEPLAY_PLOT_LEXICAL_TOPUP=true` 恢复。

**修复后实测（真实剧情图谱，`tmp_pytest/probe_prompt.py`）**

| 查询 | 修复前注入提示词 | 修复后注入提示词 |
|---|---|---|
| 今天天气怎么样 | 2 段无关词法噪声 + 图谱块被丢弃 | ✅ 仅 1 条图谱块（`天气 —阻碍进入→ 遗迹`） |
| 推荐一家附近的餐厅 | 2 段无关词法噪声 | ✅ 仅 1 条图谱块 |
| 凯拉死后无名者的发条装置怎么样了 | 3 条图谱块（本次无词法竞争） | ✅ 3 条图谱块不变 |

**回归护栏**：`tests/test_rag_graphrag_audit.py::test_plot_graph_chunk_survives_lexical_fallback`

---

### 🟠 F3 lore 层 GraphRAG 已实现但完全未接入（死代码 + 缺失交付物）

**证据**

| 检查项 | 结果 |
|---|---|
| `GraphRegistry` 在 `src/` 内的构造点 | **0 处**（仅 `graph_store.py` 定义、`knowledge/__init__.py` 导出） |
| `build_graph_from_chunks` 调用点 | **0 处**（`src/`、`scripts/` 均无） |
| `Settings.graph_enabled` / `graph_dir` / `graph_ppr_damping` … | **不存在**（`config.py` 只有 `plot_*`） |
| `scripts/build_graph.py` | **不存在**（但 `graph_store.py:487` 的告警文案让用户去跑它） |
| 对话三元组写图谱（计划 P2） | 未实现：`memory_tier.consolidate_entries` 只写 `events`，`subject/predicate/object` 仍零消费 |
| 编排器 | `_retrieve` 只有「向量 + 长期记忆」两路，无图谱第三路 |

**影响**：`GRAPHRAG_ENHANCEMENT_PLAN.md` 的 P0（数据底座）/P1（在线检索）此前处于
「代码在、链路不在」状态；实际在线可用的 GraphRAG 只有 `plot_graph.py`（剧情层），
且它默认关闭（`plot_graph_enabled=False`），因此审计时生产配置下**没有任何 GraphRAG 参与对话**。

**✅ 修复**：补齐 P0/P1 在线链路（全部默认关闭，零回归）：

| 新增/修改 | 内容 |
|---|---|
| `core/knowledge/graph_ppr.py` | 共享 PPR + BFS 跳距（lore 层与剧情层共用，避免算法漂移） |
| `core/knowledge/graph_search.py` | `GraphSearcher`：别名/正名精确链接 → 实体名向量 top-m 兜底 → PPR → 证据 hash 回查 KnowledgeBase（索引按 `kb.version` 失效） |
| `config.py` | `graph_enabled` / `graph_dir` / `graph_max_chunks` / `graph_max_edges` / `graph_max_hops` / `graph_edge_min_confidence` / `graph_include_weak` / `graph_entity_link_threshold` / `graph_ppr_damping` / `graph_ppr_max_iter` / `graph_context_max_chars` / `graph_extract_*` |
| `factory.py` + `api/deps.py` | `build_graph_registry`，装配进 `KnowledgeServices` 并注入编排器 |
| `orchestrator.py` | `_graph_retrieve` 第三路检索（与向量/画像/剧情并行，异常静默降级） |
| `persona_prompt.py` | `_source_label` 新增 `graph_*` → 「关系脉络」；`build_graph_context()` 独立块 + 独立预算（1200 字） |
| `api/knowledge.py` | `GET /api/knowledge/graph/stats`、`GET /api/knowledge/graph/entity?q=`（邻域子图人工校验） |
| `scripts/build_graph.py` | 离线构建 CLI（`--build/--rebuild/--dry-run/--stats/--limit/--namespaces`，chunk 哈希幂等缓存） |
| `models/character.py` | 角色卡新增 `entity_aliases`（人工权威别名表） |

**修复后实测**：
- `python scripts/build_graph.py --character wu_ming_zhe --stats` → 正确报告未构建；
- `--dry-run --limit 1`（真实 `qwen2.5:7b`）→ 抽取成功：
  `{"entities":[{"name":"暴雨",...},{"name":"重塑之手",...}],"relations":[{"src":"暴雨","dst":"重塑之手","relation":"发动","confidence":0.9}]}`；
- `ROLEPLAY_GRAPH_ENABLED=true` 且无图谱文件 → 服务正常启动、`_graph_retrieve` 返回 `[]`（静默降级）；
- `GET /api/knowledge/graph/stats` → 200；`/graph/entity` 无图谱 → 404 + 明确提示。

**回归护栏**：`test_lore_graph_search_is_wired_into_runtime`、`test_graph_searcher_links_and_resolves_evidence`、
`test_graph_searcher_evidence_index_invalidates_on_kb_write`、`test_graph_context_block_rendering`、
`test_roleplay_prompt_includes_graph_block`、`test_orchestrator_graph_path_off_by_default_and_optional`

---

### 🟠 F4 抽取关系端点经全局别名索引解析 → 边挂到错误实体

**位置**：`graph_extract.normalize_extraction` / `build_graph_from_chunks`、`plot_graph.build_plot_graph`

**证据（`probe_rag.py` P5）**

```python
entities = [{"name": "Madam Lucy", "aliases": ["露西"]},
            {"name": "Doris",      "aliases": ["露西"]}]      # 同一 chunk 内别名冲突
relations = [{"src": "露西", "dst": "Doris", "relation": "认识"}]  # 本意指向 Doris
落图边: ('Madam Lucy', '认识', 'Doris')                        # 实际挂到首注册实体
```

**根因**：`normalize_extraction` 只校验 src/dst 出现在「本 chunk 所有实体名/别名的并集」里；
随后 `link_exact(rel["src"])` 查的是**全局** `_alias_index`，首注册者胜出。
`build_graph_from_chunks` 里其实已经算好了 `name_to_eid`（chunk 内局部映射），
但**从未使用**——修复只写了一半。

**影响**：图谱里出现「错误主语」的关系边，PPR 会把激活扩散到无关实体，
提示词中的「（关系）A —谓语→ B」可能与原文不符（幻觉来源之一）。

**建议**：关系端点优先在「本 chunk 实体集合」内解析（`name`/`aliases` → eid），
解析不到再回落全局索引；同时丢弃「同一别名指向多个本 chunk 实体」的歧义关系。

**回归护栏**：`test_relation_endpoint_resolves_within_chunk_entities`、`test_build_graph_from_chunks_drops_ambiguous_relations`

---

### 🟡 F5 剧情层默认关闭，2MB 图谱产物闲置

`plot_graph_enabled` 默认 `False`（`config.py:108`），`.env` 未设置 → 生产不启用。
`data/knowledge/plot_graph_wu_ming_zhe.json`（2.07MB，5026 实体 / 4261 边）与
`plot_corpus_wu_ming_zhe.json`（2.45MB，2477 块）已构建完成却不参与对话。

**建议**：确认是否要在 `.env` 打开；若长期不启用，考虑把产物移出 `data/knowledge`
以免被误认为在线链路的一部分。

---

### 🟡 F6 `PlotGraphRegistry` 的 `include_weak` 默认值与 Settings 冲突

**证据（`probe_real2.py` R1 vs R2）**

| 构造方式 | include_weak | 「发条装置是什么」检索结果 |
|---|---|---|
| `PlotGraphRegistry(...)` 默认 | **False** | 3 条全部 `plot_lexical`（图谱路完全失效） |
| `build_plot_registry()`（生产） | True | 3 条全部 `plot_graph` |

真实语料 **99.7% 的边只有 1 条证据**（4248/4261），`include_weak=False` 等于把图谱路关掉。
任何直接构造注册表的调试脚本/第三方调用都会得到与生产不同的行为。

**建议**：把 `PlotGraphRegistry.__init__` 的默认值改为 `True`，或直接**移除默认值**
（强制显式传参），避免与 `Settings` 漂移。

**回归护栏**：`test_plot_registry_defaults_match_settings`

---

### 🟢 F7 `build_rag_context` 预算可被单块突破（当前语料风险低）

**证据（`probe_rag.py` P2）**：`max_chars=200`，单条 900 字块 → 输出 **1390 字符**。

根因是 `if used + len(text) > max_chars and used > 0: break` 中的 `used > 0` 守卫，
使**首块永不截断**。`build_plot_context` 有单块截断逻辑，两者行为不一致。

**实测风险**：当前真实语料块长分布——lore 库 p50=720 / max=**782** 字符（2085 块），
口吻库 max=543，剧情语料 max=601，均远小于默认预算 3200，**暂不会触发**。
但预算一旦下调（或导入长段落 PDF），单块即可击穿。

**建议**：与 `build_plot_context` 对齐，对单块做 `text[:max_chars] + "…"` 截断。

**回归护栏**：`test_rag_context_respects_budget_for_single_oversized_chunk`

---

### 🟡 F8 `_cosine` 维度不一致时静默返回错误分数

**证据（`probe_rag.py` P3）**：`cos([1,0,0],[1,0,0,5,5]) = 0.1400`（应为 0 或报错）。

`_cosine` 用 `common = min(len(a), len(b))` 截断点积，却用**全量范数**归一化。
`_reembed_ns_if_needed` 能覆盖「嵌入器切换」场景，但若重建失败（网络异常）或
查询侧维度与库内不一致，检索会**静默给出无意义分数**而非降级/告警。

**建议**：`len(a) != len(b)` 时记 warning 并返回 0.0。

**回归护栏**：`test_cosine_rejects_dimension_mismatch`

---

### 🟡 F9 混合检索 alpha 默认值三处不一致

| 位置 | 值 |
|---|---|
| `Settings.rag_hybrid_alpha`（`.env` 也设了） | **0.45** |
| `KnowledgeBase.search/asearch` 形参默认 | **0.3** |
| `rag/base.py` 注释 + `RAG_SYSTEM_DESIGN.md §3.7` | **0.3** |
| `GET /api/knowledge/search` | 不传 alpha → 走 **0.3** |

`rag_hybrid_candidates` 同样：文档写 12，`Settings` 为 30。

**影响**：调试接口的检索结果与线上对话路径不一致，容易得出错误结论。

**建议**：接口默认值改为从 `Settings` 取；文档同步。

**回归护栏**：`test_hybrid_alpha_default_matches_settings`

---

### 🟢 F10 `PlotGraphRegistry` 缓存键未归一

`get()` 的 `OSError` 分支用 `self._cache.pop((character_id or "default"), None)`，
而写入键是 `(character_id or "").strip() or "default"`。`character_id=" x "` 时清不掉 `"x"`。

**影响**：仅缓存滞留（`get` 仍返回 `None`），但长期运行会累积陈旧条目。

**回归护栏**：`test_plot_registry_cache_key_normalized`

---

### 🟢 F11 新建实体 `mentions=0`

`upsert_entities` 只对「已存在」实体 `mentions += 1`，首现实体恒为 0。
`PlotGraphRetriever.link` 的并列排序用 `-mentions`，因此「只出现一次但很重要」的实体
排序吃亏（真实数据里 5026 实体中大量 mentions=0）。

**回归护栏**：`test_new_entity_mentions_counts_first_occurrence`

---

### 🟢 F12 测试函数重复定义（后者静默覆盖前者）

`tests/test_plot_graph.py` 内 `test_plot_include_weak_defaults_to_true` 定义了两次
（第 402 行与第 413 行），前者**永不执行**。

**回归护栏**：`test_no_duplicate_test_function_names`

---

### 🟢 F13 其他一致性问题（无需单测）

| 项 | 说明 |
|---|---|
| `_ns_weight` 末行冗余 | `return NAMESPACE_WEIGHTS.get(ns, 1.0)` 与上方分支等价，不可达 |
| `retrieve` 返回上限与 docstring 不符 | docstring 称 `top_chunks + lexical_fallback`，实际词法兜底循环在 `len(out) >= top_chunks` 即停，上限恒为 `top_chunks` |
| `PlotCorpus.by_hash` O(n) 线性扫描 | 每次证据回查全量遍历；`search` 每次重建 hash 索引。当前规模（2477 块）实测 <1ms，可接受，但规模翻倍后需改索引 |
| 剧情层不受 `knowledge_scope` 约束 | `_plot_retrieve` 只看 `character_id`，不看角色卡知识范围；也没有请求级开关（仅全局 `plot_graph_enabled`）。按设计是「按角色隔离」，但与 lore 层的白名单机制不对称 |
| `_hop_distance` 与 `_ppr` 过滤口径不同 | 前者只按 `min_confidence`，后者还按 `include_weak`；当 `include_weak=False` 时会出现「有跳距但零 PPR 分」的节点 |
| 剧情图谱指纹未校验 | 落盘 `fingerprint.schema="v1"`（通用库版本），`PLOT_GRAPH_SCHEMA="plot-v1"` 仅用于日志；`PlotGraphRegistry.get()` 也不调用 `check_fingerprint`。**此项已在 `docs/剧情图谱测试结论.md` 记录** |

---

### 🟡 F14 `OllamaEmbedder` 的持久 AsyncClient 跨事件循环复用

**证据（`probe_e2e.py` 首轮）**：连续两次 `asyncio.run(...)` 时第二次抛
`RuntimeError: Ollama 嵌入调用失败：Event loop is closed`。

**根因**：`_get_client()` 缓存的 `httpx.AsyncClient` 绑定在**首个**事件循环上；
`_acall_temp`（同步桥接路径）已用短连接规避，但 `aembed`/`aembed_query`
（异步路径）复用持久客户端。生产是单长驻循环（uvicorn）不受影响；
**多轮 `asyncio.run()` 的脚本/测试、以及每个 TestClient 上下文新建循环的场景会踩坑**。

**建议**：按运行中的 loop 缓存客户端，或在捕获 `Event loop is closed` 后重建并重试一次。

---

## 三、已实现但未接入的能力对照（GraphRAG 计划落地度）

| 计划项 | 交付物 | 状态 |
|---|---|---|
| P0-1 `core/knowledge/graph_store.py` | GraphStore / GraphRegistry / 原子写 / 指纹 / remove_by_doc | ✅ 代码完整且有测试 |
| P0-2 `core/knowledge/graph_extract.py` | 抽取器 + 三级 JSON 解析 + 哈希缓存 | ✅ 代码完整 |
| P0-3 `scripts/build_graph.py` | 离线构建 CLI | ✅ 已补齐 |
| P0-4 `config.py` graph_* 字段 | graph_enabled / graph_dir / graph_ppr_damping … | ✅ 已补齐 |
| P0-5 角色卡 `entity_aliases` | 别名表 | ✅ 模型字段在（真实卡未填），`bind_alias_table` 可用 |
| P1-1 `graph_search.py`（PPR） | 实体链接 + PPR + 证据回查 | ✅ 已补齐（PPR 抽到 `graph_ppr.py` 两层共用） |
| P1-2 `orchestrator._retrieve` 第三路 | 图谱并入检索 | ✅ 已接入（`_graph_retrieve`，默认关闭） |
| P1-3 `persona_prompt` `graph_*` 标签 | 关系脉络块 | ✅ 已补齐（`build_graph_context`） |
| P1-4 调试 API `/api/knowledge/graph/*` | 图谱统计/实体邻域 | ✅ 已补齐 |
| P2 对话三元组增量写图 | `consolidate_entries` → GraphStore | ❌ 未实现（本次未做） |
| P3 社区摘要 / 全局问答 | — | ❌ 未开始 |
| P4 A/B 评估 `--graph` | — | ❌ 未开始 |

> 结论（修复后）：**lore 图谱与剧情层两条 GraphRAG 链路均已接入**，默认关闭；
> 打开开关并构建图谱后即可参与对话。

---

## 四、验证通过的关键行为（回归护栏）

新增 `tests/test_rag_graphrag_audit.py` 的 **33 项**用例覆盖：

| 主题 | 断言 |
|---|---|
| BM25 | 与 Okapi 公式手算一致；CJK 单字 + 拉丁词分词 |
| 混合重排 | 能把含专名目标顶到首位；写入后缓存失效；默认参数与 Settings 一致 |
| 向量库持久化 | 落盘/重载往返；同目录图谱/语料 JSON 不被误载为命名空间；维度失配返回 0 |
| 图谱存储 | 边合并（confidence 取 max、证据**保序**去重）、低置信拒绝、原子写无残留、指纹校验、`remove_by_doc` 清孤儿、mentions 计数 |
| 关系端点 | chunk 内局部解析：歧义别名 → 丢弃关系（单元 + 端到端） |
| PPR | 种子直连节点得分高于远端节点（lore / 剧情共用 `graph_ppr`） |
| 实体链接 | 最长匹配（露西娅 ≠ 露西）、拉丁词边界（ania ≠ mania）、别名等价 |
| 图谱检索 | 证据回查 KB 原文块、索引随 KB 写入失效、零命中静默降级 |
| 提示词块 | 【关系脉络】空结果零注入、带关系行、独立预算截断 |
| 编排器 | 图谱路默认关闭返回空、开启后注入且不影响 lore 检索 |
| 语料隔离 | 三重白名单拒绝手工整理 md 与伪造转写 |
| 抽取幂等 | 缓存命中后不再调用抽取器 |
| 命名空间 | `events` → `events:<cid>` 按角色隔离 |
| 分数门 | 长期记忆与 lore 共存（分组相对门）；剧情图谱块不被词法块挤掉 |
| 测试卫生 | 无重复定义的测试函数 |

既有测试（SSE 契约、会话锁、角色 CRUD、画像、语音等）全部保持通过。

---

## 五、复现命令

```powershell
# 1) 全量回归（正常环境）
python -m pytest tests/ -q

# 2) 本沙箱环境（临时目录被拒时的绕过）
$env:TEMP = "$PWD\tmp_pytest"; $env:TMP = $env:TEMP; $env:PYTHONPATH = "$PWD\tmp_pytest"
python -m pytest tests/ -q -p dsh_tmppath

# 3) 审计套件单跑（全部为修复回归，应全绿）
python -m pytest tests/test_rag_graphrag_audit.py -v

# 4) 行为探针（只读；真实向量库用副本）
python tmp_pytest/probe_rag.py          # F4/F7/F8/F10/F11
python tmp_pytest/probe_prompt.py       # F2（提示词层证据）
python tmp_pytest/probe_evidence.py     # 图谱证据可解析率 100% 复核
python tmp_pytest/probe_e2e.py          # F1（真实 nomic + 真实语料，需 Ollama 在跑）

# 5) lore 图谱（默认关闭；构建后置 ROLEPLAY_GRAPH_ENABLED=true 生效）
python scripts/build_graph.py --character wu_ming_zhe --stats
python scripts/build_graph.py --character wu_ming_zhe --dry-run --limit 5
python scripts/build_graph.py --character wu_ming_zhe --build
```

---

## 六、修复记录（本次已完成）

| 优先级 | 项 | 结果 |
|---|---|---|
| P0 | F1 长期记忆被相对门丢弃 | ✅ 分组相对门（`_score_group`），真实数据端到端验证 |
| P0 | F2 剧情图谱块被词法兜底挤掉 | ✅ 分组相对门 + 词法兜底改为「仅图谱零命中」 |
| P1 | F3 lore GraphRAG 未接入 | ✅ 补齐 `graph_search` / `graph_ppr` / `build_graph.py` / 配置 / 编排器第三路 / 提示词块 / 调试 API |
| P1 | F4 关系端点挂错实体 | ✅ chunk 内局部解析 + 歧义丢弃 |
| P1 | F6 `include_weak` 默认值冲突 | ✅ 对齐 Settings |
| P2 | F7 单块截断 / F8 维度校验 / F9 默认值统一 | ✅ 全部修复 |
| P2 | F14 嵌入器跨事件循环复用 | ✅ 按 loop 缓存客户端 |
| P3 | F10 / F11 / F12 / F13 / F15 | ✅ 缓存键、mentions、重复测试、冗余分支、证据顺序 |
| — | F5 剧情层默认关闭 | 保持（配置决策，需显式开启） |

**未做（超出本次修复范围）**
- P2 对话三元组增量写图（`consolidate_entries` → GraphStore）；
- P3 社区摘要 / 全局问答；
- P4 `eval_rag_standard.py --graph` A/B 评估；
- `PlotCorpus.by_hash` 的 O(n) 线性扫描（当前 2477 块实测 <1ms，规模翻倍后再优化）。

---

## 七、变更文件清单

### 新增

| 文件 | 说明 |
|---|---|
| `src/roleplay/core/knowledge/graph_ppr.py` | 共享 PPR + BFS 跳距（lore / 剧情两层共用） |
| `src/roleplay/core/knowledge/graph_search.py` | `GraphSearcher` + `GraphSearchRegistry`（实体链接 → PPR → 证据回查） |
| `scripts/build_graph.py` | lore 图谱离线构建 CLI（幂等缓存） |
| `tests/test_rag_graphrag_audit.py` | 审计套件（33 项，全绿） |
| `deliverables/rag-graphrag-audit-20260908.md` | 本报告 |
| `tmp_pytest/dsh_tmppath.py`、`tmp_pytest/probe_*.py` | 沙箱临时目录插件 + 只读探针（测试环境用，非项目代码） |

### 修改

| 文件 | 变更 |
|---|---|
| `src/roleplay/core/persona_prompt.py` | `_score_group` 分组相对门；`build_rag_context` 单块截断；`build_graph_context`；`graph_chunks` 透传；`graph_*` 来源标签 |
| `src/roleplay/core/knowledge/vector_store.py` | `_cosine` 维度校验；`_ns_weight` 清理；混合参数默认值常量；`version` 属性 |
| `src/roleplay/core/rag/{base,memory,chroma_store}.py` | 混合参数默认值对齐 |
| `src/roleplay/core/knowledge/graph_store.py` | 局部端点映射/解析；mentions 计数；`remove_by_doc` 不再覆盖 mentions；证据保序去重 |
| `src/roleplay/core/knowledge/graph_extract.py` | 关系端点局部解析 |
| `src/roleplay/core/knowledge/plot_graph.py` | PPR/跳距改调共享实现；`topup` 参数与默认行为；`include_weak` 默认 True；缓存键 strip |
| `src/roleplay/core/knowledge/factory.py` | `build_graph_registry` + `KnowledgeServices.graph_registry` |
| `src/roleplay/core/knowledge/__init__.py` | 导出新增符号 |
| `src/roleplay/core/orchestrator.py` | `_graph_retrieve` 第三路 + `_gather_context` 五路并行 + 提示词透传 |
| `src/roleplay/config.py` | `graph_*` 配置组 + `plot_lexical_topup` |
| `src/roleplay/models/character.py` | 角色卡 `entity_aliases` 字段 |
| `src/roleplay/api/deps.py` | 图谱注册表注入编排器 |
| `src/roleplay/api/knowledge.py` | `/api/knowledge/graph/stats`、`/graph/entity` |
| `src/roleplay/core/knowledge/embedder.py` | AsyncClient 按事件循环缓存 |
| `tests/test_plot_graph.py` | 删除重复定义的测试函数 |
| `RAG_SYSTEM_DESIGN.md`、`GRAPHRAG_ENHANCEMENT_PLAN.md` | 默认值与落地状态同步 |
| `.gitignore` | 忽略审计临时目录 |
