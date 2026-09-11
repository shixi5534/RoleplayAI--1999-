# GraphRAG 加强计划 —— 知识图谱增强检索

> 项目：roleplay-ai（无名者 Ms. Stranger）
> 日期：2026-09-06
> **详细实施版：[docs/GRAPHRAG加强计划书.md](docs/GRAPHRAG加强计划书.md)**（模块设计/接口签名/算法规格/WBS/测试与评估协议，冲突时以详细版为准）
> 基线：现有 RAG 体系（`RAG_SYSTEM_DESIGN.md` + 9 月迭代：画像/事件提取方案 C、分层消息 P1-1、相对分数门）
> 全量测试基线：462 passed / 2 skipped
>
> **落地状态（2026-09-08 审计后补）**：P0/P1 已接入在线链路（`graph_enabled` 默认关闭；
> `graph_search.py` 实体链接+PPR+证据回查、`scripts/build_graph.py` 离线 CLI、
> `persona_prompt.build_graph_context` 关系脉络块、`/api/knowledge/graph/*` 调试接口）。
> P2（对话三元组增量写图）/P3（社区摘要）/P4（A/B 评估 `--graph`）仍未开始。
> 审计报告与修复清单：`deliverables/rag-graphrag-audit-20260908.md`

---

## 一、现状审计（全代码搜索结论）

### 1.1 搜索结果：**没有任何 GraphRAG 实现**

全仓库（`src/`、`scripts/`、`docs/`）grep `graphrag|graph_rag|knowledge_graph|三元组|实体` 后确认：
- 无图结构存储、无邻接遍历、无实体消歧逻辑；无 networkx / neo4j 等图依赖。
- `"Multi-hop"` 仅是 `scripts/eval_rag_standard.py` 的**评估指标**，检索本身不具备多跳能力。

### 1.2 现有检索能力边界（ production 真相）

| 能力 | 现状 | 位置 |
|---|---|---|
| 检索方式 | 纯向量（稠密余弦）+ BM25 混合重排，单跳 | `core/knowledge/vector_store.py:339-369` |
| 查询改写 | **无**，query = 用户原话直查 | `orchestrator.py:506`（`req.message` 原样传入） |
| 注入量 | `top_k=2`，注释自认"检索无判别力，以少注入降噪" | `config.py:61-63` |
| 相关性过滤 | 相对分数门（低于 top1 的 85% 视为噪声） | `persona_prompt.py:39-53` |
| 实体消歧/别名 | 无（曾用名格蕾丝/莉莉/凯拉/塞西莉无法归一） | — |
| 多跳/子图 | 无 | — |
| 时间维度 | 仅时间衰减重排 `exp(-λ·age)`，无时间线查询 | `memory_tier.py:131-153` |

### 1.3 关键发现：**三元组管线已存在但从未被消费**（最重要的现成扩展点）

```
LLMEventExtractor 提示词要求输出 {"subject","predicate","object",...}
  → event_extractor.py:95-107（提示词）、:207-216（_coerce 规范化）
  → consolidate_entries() 把三元组写入 events 条目 metadata
  → memory_tier.py:112-123
  → 检索侧只做 相似度×衰减×重要性，subject/predicate/object 三个字段【零消费】
```

### 1.4 数据规模与闲置资产

| 资产 | 规模 | 说明 |
|---|---|---|
| `lore_wu_ming_zhe` | **927 块 / 约 57 万字** | B 站剧情转写 + 档案，主体语料 |
| `lore_wu_ming_zhe_spoken` | 608KB | 第一人称口吻库 |
| `events:<cid>` | **空** | 长期记忆尚未沉淀真实数据 → 图谱必须先从 lore 离线构建 |
| 评估基线 | 60 用例 + `deliverables/rag-eval-standard.json` | 含 multi-hop 指标，可直接做 A/B |

### 1.5 明确的集成扩展点（已逐行验证）

1. **检索唯一入口**：`ChatOrchestrator._retrieve`（`orchestrator.py:506-564`）——events 已走独立 `LongTermMemory.retrieve` 分支，图谱检索可作为第三路并入。
2. **注入格式**：`build_rag_context` + `_source_label`（`persona_prompt.py:112-150`）——多来源标签机制现成，加一个 `graph_*` 标签即可。
3. **命名空间白名单**：`resolve_knowledge_namespaces`（`persona_prompt.py:96-109`）+ `lore_<cid>` 约定 → 天然延伸出 `graph_<cid>` 按角色隔离。
4. **基础设施复用**：`EmbedderPort`（实体名向量化）、`LLMPort`（关系抽取）、KnowledgeBase 原子写/元数据机制、`build_spoken_lore.py` 的幂等重建模式。

---

## 二、技术选型（2026-09-06 GitHub 实地调研）

### 2.1 主流开源项目现状

| 项目 | Stars | 活跃度（2026-09 实测） | 关键现状 |
|---|---|---|---|
| [microsoft/graphrag](https://github.com/microsoft/graphrag) | 31.8k | 最后 push 2026-03 | **官方 README 宣布进入维护模式**："won't be accepting new PRs or implementing new features"，仅修 CVE/依赖；自称 research project、非官方支持产品；README 明确警告"indexing can be an expensive operation" |
| [HKUDS/LightRAG](https://github.com/HKUDS/LightRAG) | 30.6k (EMNLP2025) | **活跃**：2026.07 仍在发新特性 | 5 种查询模式（naive/local/global/hybrid/**mix 默认**）；**默认存储就是 JsonKV + NanoVectorDB + NetworkX + JsonDocStatus 全内存+本地文件持久化**（自述仅适合小规模）；支持增量插入与删除（删文档自动重建受影响子图）；RAGAS 评估已内置；角色化 LLM 配置（EXTRACT/QUERY/KEYWORDS/VLM 分模型）；官方建议抽取用非思考快速模型、本地部署 Qwen3-30B-A3B 起步 |
| [OSU-NLP-Group/HippoRAG](https://github.com/OSU-NLP-Group/HippoRAG) | 4.0k (NeurIPS'24 + ICML'25) | **活跃**：最后 push 2026-09-03 | HippoRAG 2：KG + Personalized PageRank 展开激活；论文实测**多跳（MuSiQue/2Wiki/HotpotQA）与长文理解双提升**，且"offline indexing 资源消耗显著低于 GraphRAG/RAPTOR/LightRAG"；pip 可装，支持 OpenAI 兼容端点（可接 vLLM/本地模型）；索引带 manifest 身份校验（换嵌入模型强制重建，防状态错配） |

### 2.2 选型结论

| 方案 | 判定 | 理由 |
|---|---|---|
| 微软 GraphRAG | **排除** | 维护模式=无演进；依赖重（graspologic/parquet/lancedb）；索引成本高；社区层级面向语料级全局问答，与本项目**按角色隔离**（每角色独立图谱）冲突 |
| LightRAG 直接集成 | 缓选（保留为 P3 备选） | 亮点值得借鉴（见 2.3），但它自带整套存储/检索体系，与现有 KnowledgeBase 命名空间、来源标签、相对分数门**双账本**；embedding/LLM 抽象与 EmbedderPort/LLMPort 重复 |
| HippoRAG 直接集成 | 缓选 | 学术最强但默认绑定 NV-Embed/GritLM 等嵌入器，接 nomic 需自定义；整库替换侵入性大；其核心算法（PPR）可直接自研吸收 |
| **自研轻量图谱层（推荐 ✅）** | 采用 | ① LightRAG 默认存储 = JSON + NetworkX 内存图，**证明小规模（我们的 927 块）下该路线是被生产验证过的**；② 零新增第三方依赖（PPR 约 30 行纯 Python）；③ 复用全部现有抽象；④ `graph_<cid>` 天然按角色隔离；⑤ 边挂 chunk id 保证**证据可溯源**（防幻觉） |

### 2.3 从三个项目吸收的具体设计

1. **HippoRAG 2 → P1 检索算法升级**：邻域排序不用朴素 BFS k-hop，改用**个性化 PageRank（展开激活）**——以链接命中的实体为种子、边权（confidence×importance）为转移权重，迭代数十轮即收敛，多跳关联自然浮到前排（这正是 HippoRAG 论文多跳优势的来源，且纯 Python 可实现）。
2. **LightRAG → 抽取与更新的工程约定**：抽取模型与对话模型分角色配置（我们已有 `graph_extract_provider`，采纳其"抽取用非思考快速模型"建议）；**文档删除/重导入时按 doc_id 增量清理受影响的实体与边**（照搬其"删除自动重建子图"思路，防图谱与 KB 漂移）；评估阶段直接复用其 RAGAS 集成经验（我们已有 eval_rag_standard.py，同源）。
3. **HippoRAG 2 → 索引身份指纹**：图谱文件头记录 `{embedder 名, dim, llm 模型, 图 schema 版本}` 指纹（照搬其 index_manifest 思想），嵌入器/模型切换后拒绝混用旧图谱，提示重建——与 KnowledgeBase 的 `.kb_meta.json` 机制对齐。
4. **Microsoft GraphRAG → 只取方法论**：local（实体邻域）/global（社区报告）双模式界定保留为 P3 的设计蓝本（[官方 local search 文档](https://microsoft.github.io/graphrag/query/local_search/)、[Discussion #721](https://github.com/microsoft/graphrag/discussions/721)），不引入其代码。

---

## 三、总体架构

```
┌──────────────────── 离线索引层（幂等，可重跑） ────────────────────────┐
│  lore_<cid> chunks ──► 实体/关系 LLM 抽取（chunk 哈希缓存）            │
│      │                    │                                           │
│      │                    ▼                                           │
│      │              别名归一（entity_aliases + 实体名向量合并）         │
│      └──► 对话侧：consolidate_entries 的 subject/predicate/object ──┐  │
│                         ▼                                           ▼ │
│              GraphStore 落盘 data/knowledge/graph_<cid>.json ─────────┘
│              （entities + edges 邻接表，原子写，边挂 evidence_chunk_ids）│
└──────────────────────────────────────────────────────────────────────┘
┌──────────────────── 在线检索层（每轮，毫秒级） ────────────────────────┐
│  query ──► ① 实体链接：别名精确匹配 + 实体名向量 top-m（1 次嵌入调用）  │
│         ──► ② PPR 展开激活（HippoRAG 2 式）：链接实体为种子、           │
│              边权=confidence×importance 为转移权重，迭代收敛排序         │
│         ──► ③ 证据收集：边上的 evidence_chunk_ids → 回 KnowledgeBase   │
│         ──► ④ 图谱上下文渲染：实体卡 + 「实体—关系→实体」三元组行       │
│                与向量检索结果统一去重融合 → build_rag_context 注入      │
└──────────────────────────────────────────────────────────────────────┘
```

### 图数据结构（`graph_store.py`）

```python
Entity:  {id, name, aliases: [..], type: "角色|物品|地点|概念|事件", mentions: int,
          summary: str(可后补), vec: [float](实体名嵌入, 可选)}
Edge:    {src, dst, relation, confidence: float, importance: float,
          evidence_chunk_ids: [..],  # ← 溯源到 lore 原文块，防幻觉
          ts: float, source: "lore|conversation"}
# 落盘：data/knowledge/graph_<cid>.json（原子写，风格与 KnowledgeBase 一致）
# 文件头 index_fingerprint：{embedder 名, dim, llm 模型, schema 版本}
#   ← 照搬 HippoRAG 2 index_manifest 思想：模型/嵌入器变更后拒绝混用旧图谱，提示重建
```

---

## 四、分阶段实施计划

### P0 图谱数据底座（估 2-3 天）

**目标**：把 927 块 lore 变成一张可查询的实体关系图（离线完成，不碰在线链路）。

| 项 | 内容 |
|---|---|
| 新增 `core/knowledge/graph_store.py` | GraphStore：实体/边 CRUD、别名表、邻接查询、JSON 原子落盘、按 `graph_<cid>` 隔离；文件头 `index_fingerprint`（embedder/llm/schema 版本，对齐 `.kb_meta.json` 机制）；`remove_by_doc(doc_id)`：文档重导入/删除时增量清理受影响实体与边（照搬 LightRAG"删除自动重建子图"，防图谱与 KB 漂移） |
| 新增 `core/knowledge/graph_extract.py` | LLM 实体关系抽取器：按 chunk 抽取（实体+类型、关系三元组+confidence）；**chunk 内容哈希幂等缓存**（照搬 `bilibili_lore_ingest.py` 重跑幂等模式），重跑只处理新增/变更块 |
| 新增 `scripts/build_graph.py` | 离线构建 CLI：`python scripts/build_graph.py --character wu_ming_zhe`；顺序：核心资料汇编 → 剧情摘录 → 视频文案转写；`--dry-run` 抽样预览 |
| 新增 `config.py` 字段 | `graph_enabled=True`、`graph_dir=./data/knowledge`（复用）、`graph_extract_batch=8`、`graph_edge_min_confidence=0.55`、`graph_extract_provider`（默认跟随 llm_provider，可指定本地 ollama 专职抽取） |
| 角色卡可选字段 | `entity_aliases: dict[str, list[str]]`（如 `"无名者": ["格蕾丝","莉莉","凯拉","塞西莉"]`），缺失时从抽取结果自动生成草稿 |
| 测试 `tests/test_graph.py` | 抽取解析兜底（复用三级 JSON 解析）、别名归一、边权过滤、落盘/加载往返、幂等重跑 |

**验收**：全量构建完成并输出统计（实体数/边数/孤岛实体占比）；重跑只处理 0 个新块；测试全绿。

### P1 在线检索集成（估 2 天）

**目标**：图谱作为第三路检索并入 `_retrieve`，多跳问题能命中。

| 项 | 内容 |
|---|---|
| 新增 `core/knowledge/graph_search.py` | ① 实体链接（别名精确匹配优先，实体名向量 top-m 兜底，复用 EmbedderPort）；② **PPR 展开激活**（HippoRAG 2 核心算法：链接实体为种子集合，边权=confidence×importance 为转移权重，damping 迭代 ≤50 轮收敛，约 30 行纯 Python，多跳关联自然浮到前排）；③ 证据 chunk 收集（取 PPR 分最高的边，按 evidence_chunk_ids 回查 KnowledgeBase 原文） |
| 改 `orchestrator.py:_retrieve` | 图谱分支与向量分支并行 gather，结果按 chunk id 去重后合并；图谱上下文**不占向量 top_k 名额**（top_k=2 太小，图谱是增量信息不是挤占） |
| 改 `persona_prompt.py` | `_source_label` 加 `graph_*` → 「关系脉络」；新增 `build_graph_context()` 渲染：实体卡行（名字·类型·别名）+ 三元组行（`A —关系→ B`）+ 最多 2 条溯源证据块；独立预算 `graph_context_max_chars=1200` |
| 降级策略 | `graph_enabled=False` / 图谱文件缺失 / 实体链接零命中 → 静默回退纯向量路径（与 P0 前行为完全一致，零回归） |
| 调试 API | `GET /api/knowledge/graph/stats`、`GET /api/knowledge/graph/entity?q=发条装置`（返回邻域子图 JSON，供人工校验抽取质量） |

**验收**：端到端验证（沿用 `scripts/e2e_verify_semantic.py` 模式）——多跳问法（如「凯拉死后无名者的发条装置怎么样了」）能同时召回两条边的证据块；单跳问题图谱不喧宾夺主。

### P2 对话增量图谱与多跳记忆（估 2 天）

**目标**：激活已存在但从未消费的对话三元组，长期记忆升级为"可多跳的关系记忆"。

| 项 | 内容 |
|---|---|
| 改 `memory_tier.py`（或新增 graph writer 挂钩） | `consolidate_entries()` 写入 events 的同时，把 subject/predicate/object 非空的条目**增量写入 GraphStore**（`source="conversation"`，`occurred_round`/`ts` 一并落边） |
| 时间线查询 | `graph_search.py` 支持按实体收集其全部事件边并按 `ts/occurred_round` 排序 → 支持「上次我们约定了什么」「我和你之间发生过什么」类时间线问题 |
| 实体消歧（对话侧） | 对话实体与 lore 图谱实体做链接（向量相似 ≥ 阈值才合并），链接不上的新实体先挂起、积累 mentions 后转正 |

**验收**：多轮对话后 `graph_<cid>.json` 增长且 events 图与 lore 图连通；时间线检索单测通过。

### P3 全局问答与社区摘要（可选，估 2-3 天）

**目标**：支撑「你怎么看待你们组织」这类语料级主题问题（MS GraphRAG global search / LightRAG high-level 检索的定位）。

- 纯 Python 连通分量/标签传播（零依赖替代 Leiden）划社区 → 每社区 LLM 生成 2-3 句摘要并缓存（幂等）。
- 问题路由（对齐 LightRAG 五模式的 local/global 界定）：简单规则（含"整体/你们/组织/世界/风格"等宏观词）或轻量分类 → 命中 global 时注入相关社区摘要，否则走 P1 的实体级检索（对应 local/mix）。
- 此阶段结束再评估：若社区摘要质量不足，考虑以 REST API sidecar 方式接入 LightRAG（其自带 Server/WebUI），只替换全局层、保留自研实体级检索。

### P4 评估与度量（与 P1 同步启动）

| 项 | 内容 |
|---|---|
| A/B 评估 | `scripts/eval_rag_standard.py` 加 `--graph` 开关，60 用例跑「向量 vs 向量+图谱」，对比 multi-hop / Context Recall / Faithfulness |
| 目标 | multi-hop 指标相对基线提升（预期 ≥15%）；Faithfulness 不降；单跳用例不劣化 |
| 观测 | 图谱命中统计（实体链接成功率、PPR 证据利用率）进 `GET /api/knowledge/graph/stats` |

---

## 五、新增配置一览（`config.py`，均带默认值，缺省即关闭或零回归）

| 字段 | 默认 | 说明 |
|---|---|---|
| `graph_enabled` | `False` | 总开关（P1 起）；关闭 = 完全回退现状。实现取 False 以保零回归：图谱文件缺失时也不改变任何既有行为，构建完图谱后再置 true |
| `graph_dir` | `./data/knowledge` | 与 KnowledgeBase 同目录，`graph_<cid>.json` |
| `graph_max_hops` | `2` | （保留）证据收集时边距上限，防 PPR 高分边离种子过远 |
| `graph_ppr_damping` | `0.85` | PPR 阻尼系数（HippoRAG 同款语义） |
| `graph_ppr_max_iter` | `50` | PPR 最大迭代轮数 |
| `graph_max_edges` | `12` | 单次注入的边上限 |
| `graph_edge_min_confidence` | `0.55` | 低于此置信度的边不参与检索 |
| `graph_context_max_chars` | `1200` | 图谱上下文独立预算 |
| `graph_entity_link_threshold` | `0.82` | 实体名向量合并阈值 |
| `graph_extract_batch` | `8` | 离线抽取并发批量 |

## 六、风险与对策

| 风险 | 对策 |
|---|---|
| LLM 抽取幻觉（错误三元组污染图谱） | 边必须挂 `evidence_chunk_ids` 溯源原文；`confidence` 过滤；调试 API 人工抽检；对话侧来源边权重降权 |
| 实体歧义（一格蕾丝/莉莉/凯拉/塞西莉都是无名者） | 角色卡 `entity_aliases` 显式别名表优先；向量合并阈值 + mentions 计数人工复核 |
| 抽取成本（927 块 × LLM 调用） | chunk 哈希幂等缓存（重跑零成本）；本地 ollama 专职抽取（`graph_extract_provider`）；核心资料优先、视频转写分批 |
| 上下文预算冲突（现 top_k=2 + 相对门 0.85 很紧） | 图谱上下文**独立预算与独立来源标签**，不挤占向量 top_k；图谱段落自带守则文案 |
| 检索延迟 | 邻接表纯内存，PPR 迭代毫秒级（数百实体规模）；实体链接 1 次嵌入调用（实体名嵌入离线预计算，仅 query 侧在线） |
| 角色串台 | `graph_<cid>` 与 `lore_<cid>` 同约定按角色隔离，检索白名单复用 `resolve_knowledge_namespaces` |

## 七、总验收标准

1. `eval_rag_standard.py` 60 用例：multi-hop 提升、Faithfulness 不降（A/B 报告落 `deliverables/`）。
2. 全量测试零回归（基线 462 passed / 2 skipped）；SSE 事件契约与 `/chat` 接口不变。
3. `build_graph.py` 幂等：重跑只处理新增 chunk。
4. `graph_enabled=False` 时行为与现状逐字节一致。
