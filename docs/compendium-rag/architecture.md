# compendium_rag 架构说明（正典图谱 RAG）

> 状态：**现行权威文档**。2026-10-21 首次成文（此前本文件不存在）。
> 覆盖范围：`src/compendium_rag/` 全模块职责、数据流、检索通路、配置面，以及
> **「已知缺口」** 一节（四条检索缺口的决策、实测数据与验收口径）。
>
> 本文的每条数字都标了出处（工件路径 / 测试名 / 命令），不写估算值。
> 历史过程档见 `CHRONICLE.md`；优化路线见 `优化计划_v9_2026-10-08.md`。

---

## 1. 定位与硬约束

`compendium_rag` 是一个**独立**的图谱 RAG 子系统，服务于「正典剧情问答」。

| 约束 | 内容 |
|---|---|
| 依赖方向 | **不 import `roleplay.*`**；`roleplay` 可反向依赖它 |
| 数据边界 | **不读写** `data/knowledge`、`data/lore` 等既有资产 |
| 配置前缀 | 全部环境变量走 `CMPRAG_`，见 `config.py` 的 `Settings`（frozen dataclass） |
| 数据落盘 | 统一 `data/compendium_rag/`（`DEFAULT_DATA_DIR`） |
| 第三方图库 | **零依赖**。图是纯 Python `dict` + JSON，不引入 networkx/neo4j |
| 可溯源性 | 每条边强制携带 `chunk_ids` 与 `evidence`，任何结论都能回到原文块 |

版本常量（`graph.json` 指纹的组成部分，改动即视为数据契约变更）：

| 常量 | 值 | 位置 |
|---|---|---|
| `__version__` | `0.1.0` | `__init__.py:34` |
| `PROMPT_VERSION` | `v3` | `extract.py:379` |
| `NORMALIZER_VERSION` | `n2` | `extract.py:366` |
| `SCHEMA_VERSION` | `1` | `graph_store.py:19` |

---

## 2. 模块地图

```
src/compendium_rag/
├── corpus.py          语料解析：简体中文剧情文本 → 结构化 corpus.json
├── chunker.py         corpus → 检索块（chunks）：scene 内连续 turn 聚合
├── extract.py         块 → 实体/关系（云端 LLM）+ 内容哈希幂等缓存 + 归一化
├── relation_vocab.py  canonical 关系词表（77 个）+ SYNONYM_MAP + 治理三段
├── relation_norm.py   关系归一化三层裁决（vendor 词表 → 归组 sidecar → 方向裁决）
├── graph_store.py     图存储：实体/边/别名索引、指纹、原子写盘
├── retriever.py       检索核心：实体链接 → 四通道 → RRF 融合 → 窗口规划
├── embedder.py        bge-m3（1024 维）本地 Ollama 向量
├── llm.py             云端 LLM 客户端（异步 + 信号量 + 指数退避 + 三级 JSON 解析）
├── pipeline.py        编排：build_corpus / build_graph / rebuild_from_cache / KnowledgeBase
├── compose.py         P4 作答通路（读 context() 渲染的 `[S{i}]` 溯源）
├── config.py          Settings（frozen dataclass），全部 `CMPRAG_` 可覆盖
└── cli.py             子命令：corpus / chunks / sample / extract / build / rebuild / stats / query / entity
```

### 2.1 `corpus.py` — 语料解析

把简体中文剧情文本解析为 `corpus.json`：`H1` 篇名 / `H2` Part / `H3` scene 三级结构，
区分对话行（`**说话人**：内容`）、旁白、标题卡。**纯确定性解析**，无 LLM、无启发式猜测。
实测规模：80,152 行对话、33,148 行旁白、3,134 行标题卡。

### 2.2 `chunker.py` — 分块

- 按 **scene 内连续 turn** 聚合，**不跨 scene 边界**（scene 是语义硬边界）。
- 累积到 `chunk_chars`（默认 900）截止，`min_chunk_chars`（默认 120）防止碎块。
- `chunk_overlap_turns`（默认 1）做块间重叠，避免对话被切断。
- 渲染时保留 `**说话人**：` 前缀（抽取与检索都依赖说话人信息）。
- **两个 id 语义不同**，不要混用：
  - `chunk_id`：**位置**稳定（`mainline__107_孤独之歌:19.0.1` 这种），用于溯源与人读。
  - `content_key`：**内容**哈希，只用于抽取缓存键——所以块文本变了缓存自动失效。

实测：3695 块。

### 2.3 `extract.py` — 抽取与归一化

- 云端 LLM 抽取实体（6 类受控词表）与关系三元组。
- **内容哈希幂等缓存**：`cache_key(c, llm_model, PROMPT_VERSION)` 只含块内容 + 模型 + 提示词版本。
  这条设计有三个直接后果：
  1. 改 `NORMALIZER_VERSION` **不**使缓存失效 → 归一化改动可**零云端成本**重建。
  2. 缓存存 **RAW 输出**（归一化前的原样 JSON），归一化是重建期的纯函数。
  3. 改块文本 → 缓存键变 → 自动重抽。
- 强制每个关系端点解析到同块的实体名/别名/说话人（`extract.py:299-335`）。
  这条是后面 G3「不存在纯端点实体」的根因。
- 泛称说话人（「旁白」「众人」等）从实体中排除。

### 2.4 `relation_vocab.py` / `relation_norm.py` — 关系归一化

三层来源，越靠前优先级越高：

| 层 | 来源 | 覆盖 |
|---|---|---|
| 1 | `relation_vocab.py` 的 canonical 77 + `SYNONYM_MAP`（vendor 词表） | 高频谓语的直接同义合并 |
| 2 | `data/compendium_rag/predicate_grouping_v1.json`（8313 个自由谓语的归组判定 sidecar） | 边覆盖 **0.8545** |
| 3 | `data/compendium_rag/relation_direction_v1.json`（人工核过原文的 swap / same_direction） | 方向裁决 |

**方向优先于合规**：方向未确证时**保留原谓语**并计 `kept:direction_blocked`，不硬并。
`inverse_predicate_map.json` 的 `direction_loss_watch` 提供方向失真的监测信号。

> 归一化表在进程内做单例缓存（`relation_norm.py:115`）：3695 块逐块读三个 JSON 不可接受。

### 2.5 `graph_store.py` — 图存储

- `Entity`：`eid / name / type / aliases / desc / mentions / chunk_ids`。
- `Edge`：`src / relation / dst / confidence / count / chunk_ids / evidence`；
  `Edge.key` = `(src, relation, dst)`，同三元组**合并计数**而非重复建边。
- 别名索引 `alias_index`：名字/别名 → `eid`；合并走 `_DSU` + `canonical_pick`
  （长名优先 / 频次优先，规则见 `entity_disambiguation_rules.md`）。
- 图头部写 `fingerprint` + `normalizer`；`safe_save_graph` 在新图为空而旧图非空时
  **拒绝写盘**（防一次失败的重建抹掉好图）。
- 指纹输入（`pipeline.py:205`、`pipeline.py:399`）：
  `f(corpus_fp, llm_model, PROMPT_VERSION, chunk_chars, NORMALIZER_VERSION)`。
  注意 `NORMALIZER_VERSION` 是 2026-10 之后才纳入的；更早落盘的图走
  `verify_fingerprint` 的 legacy 分支（返回「归一化版本未知」而不是报错）。

### 2.6 `retriever.py` — 检索核心

见第 3 节。

### 2.7 `pipeline.py` — 编排

| 函数 | 职责 |
|---|---|
| `build_corpus` / `load_chapters` | 语料 → corpus.json |
| `load_chunks` / `save_chunks` | chunks 读写 |
| `build_graph` | `GraphStore.build_from_extractions(per_chunk, min_confidence)` |
| `rebuild_from_cache` | **零云端**重建：`ExtractionCache.get_raw` → `normalize` → `build_graph` |
| `build_indexes` | `ChunkIndex.build(...).save(index_path)`；实体名向量 → `entity_index.npz` |
| `KnowledgeBase` | 对外门面：`chunk_index` / `entity_index` / `retrieve` / `context` |
| `load_kb` / `verify_fingerprint` | 装载与指纹校验 |

`KnowledgeBase.retrieve()` 是 `GraphRetriever.retrieve()` 的**透传层**，额外做两件事：
把 `top_k / pool_top_n / vector_min_score` 从 `Settings` 兜底，并把 `evidence_pool`
回填到结果上（供影子脚本与诊断取全池）。
`KnowledgeBase.context()` 用**关键字**构造 `Evidence`（位置参数版本已在 G1 修复中移除）。

---

## 3. 检索通路（`GraphRetriever.retrieve`）

```
query
  ├─ link()            实体名/别名逐字匹配（长名优先）→ Seed(score=1.0 exact / 0.9 alias)
  │   └─ merge_vector_seeds()   实体名向量召回，sc = sim * 0.85
  │   └─ seed_threshold 过滤（保底留 top2）
  │
  ├─ graph_channel()    personalized_pagerank(seeds) → 边分 → 块分
  ├─ mention_channel()  种子实体的 chunk_ids[:3]（per_entity=3）
  ├─ vector_channel()   ChunkIndex.search(qvec, vector_top, min_score=…)
  └─ [lex_channel]      LexicalIndex（默认关闭，CMPRAG_LEX_WEIGHT=0）
                │
          rrf_fuse(k=60, weights, top_n=pool_top_n)
                │
        evidence ← 池的前 pool_top_n 条 → 截断到 top_k
                │
          context()  窗口规划（v2_perblock）→ `[S{i}]` 渲染 → compose 作答
```

### 3.1 实体链接（`link`，`retriever.py:509`）

- 候选按 **长名优先**排序：`sorted(alias_index, key=lambda k: (-len(k), k))`。
  次级键 `k` 不能省——不加时 300 题里有 37 题的 seeds 会因暖/冷进程的
  **dict 插入序**不同而变（#39 核验，2026-09-27）。
- 匹配：`_name_matches(name, ql)`，exact → 1.0，alias → 0.9。
- 返回排序键 `(-score, -len(name), eid)`：**三元全序**，杜绝并列漂移。

### 3.2 图通道（`graph_channel` + `personalized_pagerank`）

- `build_adjacency`：边权 `w = max(0.1, confidence) * (1 + log1p(max(0, count-1)))`，
  双向入邻接表。实测 27110 条边 → **5900 个节点，其中 1133 个孤立**。
- PPR 归一化尾部 `score /= max(score)`，故 `seed_score = 1.0`（消费方依赖这一点）。
- 边分 `s = ppr[src] + ppr[dst]`，再乘 `max(0.1, confidence)`；
  按分排序取前 `graph_max_edges`（默认 30）条；块分取该块上**最强边**的分数。
- **dangling 质量按 teleport 向量回流**（G4 修复，见 §4.4）。

### 3.3 提及通道（`mention_channel`）

种子实体的 `chunk_ids[:per_entity]`（`per_entity=3`）直接作为块证据，分数取种子分。
它不依赖 PPR，也不依赖向量——是「图谱命中的兜底直连」。
**这条通道的输入是 `_count_mentions` 的产物，所以 G3 缺口的唯一受害者就是它。**

### 3.4 向量通道（`vector_channel`）

`ChunkIndex.search(qvec, top_k, min_score=None)`：余弦相似度，`min_score` 过滤
**在截断之前**（G2 修复，见 §4.2）；并列用 `(-score, chunk_id)` 全序。

### 3.5 RRF 融合（`rrf_fuse`）

`ev.score += w * 1/(k + rank)`，通道序 `sorted(channels)` 保证确定性。
实测：120 题中 **116 题存在并列**，单题最多 42 个元素并列——所以最终排序必须带
`chunk_id` 兜底（`(-score, chunk_id)`），否则结果不可复现。

### 3.6 窗口规划与溯源

`plan_block_window`（`CONTEXT_ALLOCATOR = "v2_perblock"`，legacy `"v1_tailcut"`）
把证据块按上下文预算（`context_max_chars`，默认 3000）铺进窗口，
`[S{i}]` 编号**跟窗口排序走，不跟 chunk_id 走**。`FALLBACK_MARK = "[候选]"`
标记预算不足时的降级候选。

---

## 4. 已知缺口（四条，2026-10-21 全部修复）

> 本节是本文的重点：记录**决策 + 实测数据 + 验收口径**。
> 四条缺口均由用户提出（原始表述见 §0 的表格），修复计划见
> `compendium_rag_检索四缺口修复计划_v10_2026-10-21.md`，
> 外部同类项目对照见 `research/四缺口外部设计对照_2026-10-21.md`。

| # | 缺口 | 位置 | 性质 | 状态 |
|---|---|---|---|---|
| G1 | `top_k` 不截断 evidence（`top_n=max(top_k*4,24)`） | `retriever.py` `retrieve` | 命名/契约缺陷：池宽与输出数绑在同一参数上 | ✅ 已修 |
| G2 | 向量通道无相似度阈值 | `retriever.py` `ChunkIndex.search` | 缺失过滤：零相关块污染 RRF | ✅ 已修（**默认关闭**） |
| G3 | 提及通道对「只作关系端点出现」的实体有永久盲区 | `graph_store.py` `_count_mentions` | 契约不对称 | ✅ 已修 |
| G4 | 孤立种子的 PPR 把质量均摊给全图 | `retriever.py` `personalized_pagerank` | 算法错误：dangling 应回流 teleport | ✅ 已修 |

**总原则（写死为验收口径）**：四条缺口的**默认值路径必须与原行为逐字节一致**。
即 `pool_top_n=None`（按公式推导）、`vector_min_score=None`（关闭）时，
检索结果与改造前完全相同。新能力必须**显式开启**。

---

### 4.1 G1 — 池宽与输出数解耦

**问题**：`retrieve(top_k=…)` 同时被当成「融合候选池宽度」和「输出条数」用：
`top_n = max(top_k*4, 24)` 喂给 `rrf_fuse`，然后**原样返回整个池**。
所以 `top_k=6` 实际返回 33–105 条（k1c300 实测：最小 33 / 中位 68 / 最大 105）。
参数名与语义不符，且调用方无法表达「宽召回 + 窄输出」。

**决策**（对齐 Elasticsearch RRF 的 `rank_window_size` vs `size`）：

```python
def default_pool_top_n(top_k: int) -> int:      # retriever.py:54
    return max(int(top_k) * 4, 24)

def resolve_pool_top_n(top_k: int, pool_top_n: int | None = None) -> int:   # :64
    return default_pool_top_n(top_k) if pool_top_n is None else max(1, int(pool_top_n))
```

- `top_k` **只控输出条数**；`pool_top_n` 控进入 RRF 的候选宽度。
- `pool_top_n=None` → 走 `default_pool_top_n`，**与旧公式逐位等价**。
- `res.evidence` 截断到 `top_k`；**全池放 `res.evidence_pool`**（默认 `None`，
  不进 `to_dict()`，避免工件膨胀）。
- 配置：`Settings.retrieval_pool_top_n`（`CMPRAG_RETRIEVAL_POOL_TOP_N`，默认 `None`）；
  CLI `--pool-top-n`。

**迁移**：唯一**硬依赖**池宽的脚本是 `scripts/compendium_rag_p8_roleiso_shadow.py`
（其 docstring 明示「必须逐字复刻原 harness，否则读数不可比」），已改为显式
`pool_top_n=`；其余诊断脚本改用 `want_pool=True` / `evidence_pool`。
脚本里重复出现的 `max(top_k*4,24)` 字面量统一收敛到 `default_pool_top_n`。

**验收**：`test_default_pool_top_n_matches_legacy_formula`、
`test_top_k_truncates_evidence`、`test_pool_top_n_decoupled_from_top_k`、
`test_evidence_pool_optional_and_not_serialized_by_default`。

---

### 4.2 G2 — 向量通道相似度下限

**问题**：`ChunkIndex.search` 无任何阈值，余弦 **0.0** 的块也进入 RRF 并拿到
`1/(k+rank)` 的分。在通道少（只有 graph + vector）时，这会实质污染排名。

**决策**：加**可选**上限参数，**默认关闭**：

```python
def search(self, qvec, top_k, min_score: float | None = None)  # :132
def vector_channel(self, qvec, top_k, min_score=None)          # :600（keyword 兼容）
```

- 过滤发生在**截断之前**：`keep = np.flatnonzero(sims >= float(min_score))`。
- `min_score=None` → 完全不走过滤分支，**逐结果与改造前一致**。
- 配置：`Settings.retrieval_vector_min_score`（`CMPRAG_RETRIEVAL_VECTOR_MIN_SCORE`，默认 `None`）；
  CLI `--vector-min-score`。

**为什么不给默认阈值**（重要反例）：LightRAG 曾引入 cosine threshold 后又移除
（`271df99`、`2b52d43`），原因正是绝对阈值造成「全空」。
且 **BGE 模型卡 FAQ 说分布落在 [0.6, 1] 并要求用自己的数据标定——本仓库不适用**：

> bge-m3 中文语料实测分布 **0.32–0.67，中位数 ≈ 0.50**
> （`data/compendium_rag/reports/rank_collect_k1c300_top30.json`，
> n=4578，min 0.3178 / p10 0.4247 / p25 0.4558 / median 0.4973 / p75 0.5357 / max 0.6571）
>
> ⇒ 直接套 0.6 会砍掉一半证据。**任何阈值必须从本仓库工件的实测分布标定。**

标定流程（脚本，非生产路径）：在上表与 `rank_collect_v6c300_top30.json` 上扫
`{0.40, 0.42, 0.4247, 0.45, 0.47, 0.50}`，产出 hit@6 / MRR / 平均证据数表，
**选 hit@6 不退化的最紧值**，写进决策记录后才允许考虑默认开启。**当前保持 `None`。**

**防误伤**：`scripts/_miss_vector_reach.py:66` 用 `search(qv, 10**6)` 做全库扫描，
必须显式 `min_score=None`（已加注释）。

**验收**：`test_vector_min_score_filters`、`test_zero_cosine_block_excluded`、
`test_vector_min_score_none_is_legacy`、`test_vector_min_score_filters_before_truncation`、
`test_retrieve_passes_vector_min_score_through`。

---

### 4.3 G3 — 关系端点计入提及

**问题**：`_count_mentions` 只看 `ex.entities`（块内**显式声明**的实体）。
一个实体若在某块里只作为关系的 `src`/`dst` 出现、却没被该块声明为实体，
它在那个块上就是**永久盲区**：`chunk_ids` 里没有它 → `mention_channel` 永远取不到那些块。
主流实现（GraphRAG `local_search`、HippoRAG、LightRAG）都把「实体是关系端点」
当作**一等命中**，本仓库缺这一步是**契约不对称**。

**修复**（`graph_store.py:298` `_count_mentions` 三段式）：

1. **块内显式声明**（原逻辑，逐位保留：每条声明计一次提及）。
2. **关系端点**：遍历 `ex.relations` 的 `src`/`dst`，同块内已声明过则**不重复计数**。
3. **顺序确定化**：`ent.chunk_ids.sort(key=lambda cid: (block_ord[cid], cid))`。
   原因：`mention_channel` 取 `cids[:3]`，若 `chunk_ids` 顺序随插入序漂移，
   截断结果就漂移。这一步让暖进程 / 冷启动 / 两次重建**结果恒等**。

**实测数据（两套口径，必须分开读，别混）**：

| 口径 | 含义 | 结果 |
|---|---|---|
| **工件口径**（`g3_blind_report.json`） | 对已发货 `graph.json` 度量 | 盲区实体 **1** 个（店主），盲区 (entity, block) 对 **11** 个，涉及边 **29** 条；店主 `declared_blocks=3` vs `blind_blocks=11`，样例块全在 `anecdote__1917_乘法轴上的一天:0.0.0 / 3.0.0 / 3.0.5 / 4.0.0 …` |
| **重建口径**（`drift_split.json` B vs C） | 同一份 chunks+cache，**只切 G3 开/关** | **全零**：实体 0 差异、边 0 差异、`chunk_ids` 变更 0、mentions 变更 0 |

- B vs C 全零的原因：`extract.py:299-335` 已强制每个关系端点解析到同块实体名/别名/说话人，
  所以当前抽取管线里**不存在「纯端点实体」**——②段是纯 no-op。
- 那 11 对盲区是**工件陈旧度**：`graph.json` 落盘于 2026-10-12，当时的合并规则
  与当前代码不同。用当前代码重建，「店主」本身就有 14 个块（不靠②段）。
- A vs B（工件 vs HEAD 代码重建）则显示 **6 个实体的 chunk_ids 变化**、840/583 条边差异
  ——同样是陈旧度，不是本轮改动。

> **诚实结论：G3 是契约正确性修复，当前召回收益 ≈ 0。不得宣称任何召回/性能提升。**
> 只验两件事：①端点实体不再盲区；②其余实体 `chunk_ids` 不变。

**关于重建 `graph.json`（计划 D4-3）——本轮未执行，需拍板**：
按当前代码重建会得到 26853 条边（工件 27110）；即便只切 G3 开关是零差异，
**重建本身会带来 840 / 583 条边的变动**（来自归一化/合并规则的代码演进，
与 G3 无关）。所以「改代码 + 重建」不是 G3 的必要条件，而是一次独立的
数据刷新，收益需要单独评估。**当前状态：代码已修、数据未重建。**

**验收**：`test_endpoint_entity_counts_as_mention`、
`test_endpoint_mention_deduped_against_declaration`、
`test_mention_chunk_ids_order_is_deterministic`；
保留 `test_mentions_counted`、`test_relations_mentioning_speaker_add_entity`。

---

### 4.4 G4 — dangling 质量回流 teleport（唯一有实测收益的修复）

**问题**：PPR 里 dangling 节点（无出边）的质量被 `damping * dangling / len(nodes)`
**均摊给全图**。后果极其严重：

- 图里有 **1133 个孤立节点**（占 5900 个节点的 19.2%）。
- 用任何一个孤立节点当种子，PPR 会给**全部 27110 条边**正分（0.000299–0.1742），
  于是 `graph_channel` 的 top-30 边裁剪退化成**全图随机置信度抽样**，
  产出 **91 个完全无关的块**。
- 且所有孤立种子（1914军事基地 / 22#0 / APPLeⅡ号 / G33针管 / K.U.K. …）
  得到的分数**完全相同**——查询毫无区分度。

**修复**（`retriever.py:365` 附近）：

```python
if dangling:
    share = damping * dangling
    for n in nodes:
        tp = teleport.get(n, 0.0)
        if tp:
            nxt[n] = nxt.get(n, 0.0) + share * tp
```

即按 **teleport（personalization）向量**回流，而不是按节点数均摊。
这与 NetworkX 的 `dangling` 默认语义、igraph 的
`pr_new[v] = (1-d)*norm_reset[v] + d*(incoming + dangling_sum*norm_reset[v])`
（注释原文「Dangling nodes also distribute according to norm_reset」）一致。

**实测（同一孤立种子，改前 → 改后）**：

| 指标 | 改前 | 改后 |
|---|---|---|
| `edges sc>0` | 27110（全部） | **0** |
| top-30 边裁剪产出块 | **91** | **0** |
| `nonzero` 节点数 | 5901（全部） | **1** |
| `seed_score` | 1.0 | 1.0（不变） |

即孤立种子查询**不再产出图证据**，自然回落到词面/向量通道——这是正确的
「零命中」语义，而不是「注入 91 个无关块」。
同时确认**连通图未退化**：正常种子下 `nonzero=5790`、
`edges_with_positive_score=27043 / 27110`。

**验收**：`test_ppr_isolated_seed_keeps_mass_on_seed`、
`test_ppr_dangling_mass_follows_teleport`、
`test_ppr_single_seed_no_leak_to_disconnected_component`；
原有 `test_ppr_*` 六条全绿（`seed_score=1.0` 语义不变）。

---

### 4.5 顺带修掉的两条历史缺陷

写 §4 时核对代码，发现 v9 计划里记的两条「真缺陷」本轮之前已修，记录以免重查：

1. **`CMPRAG_PPR_DAMPING` / `CMPRAG_PPR_MAX_ITER` 没传下去**
   （v9 计划 `:39`，原 `retriever.py:522-523,531` 硬编码）。
   现在 `retrieve()` 有 `ppr_damping=0.85, ppr_max_iter=50` 关键字默认值，
   `pipeline.py:348` 把 `s.ppr_damping / s.ppr_max_iter` 透传进去。**已修。**
2. **`e.ppr` 字段名误导**（v9 计划 `:40`）。`Evidence.ppr` 已改名 `graph_score`
   并加注释说明「这是图通道的**块**分数（= 该块上最强那条边的分数），不是节点 PPR」；
   `Evidence.to_dict()` 输出 `graph_score`，边的字典键输出 `edge_score`。
   **已修。**
3. **指纹不含 `NORMALIZER_VERSION`**（v9 计划 `:41`）。`pipeline.py:205` 与 `:399`
   均已把 `NORMALIZER_VERSION` 纳入指纹输入，`graph.json` 增 `normalizer` 字段。
   **已修。**

> 注：历史评测脚本（`scripts/_r5_scene_channel_scan.py`、`_rank_collect.py`、
> `_rank_rerank_lab.py`、`_replay_symbol_channel.py`）里仍有 `e.ppr` / `"ppr"`，
> 那是**读旧工件键的兼容层**，不应改。`scripts/compendium_rag_p3_identity_ab.py`
> 正是当年做这个改名的 A/B 脚本。

---

## 5. 配置面速查

全部 `Settings` 字段都可用 `CMPRAG_*` 覆盖（`.env` 也读）。

| 类别 | 键 | 默认 |
|---|---|---|
| 分块 | `CHUNK_CHARS` / `CHUNK_OVERLAP_TURNS` / `MIN_CHUNK_CHARS` | 900 / 1 / 120 |
| LLM | `LLM_BASE_URL` / `LLM_MODEL` / `LLM_TEMPERATURE` / `LLM_MAX_TOKENS` / `LLM_TIMEOUT` / `LLM_CONCURRENCY` / `LLM_MAX_RETRIES` | — / `cn:kimi-k2.6` / 0.1 / 2048 / 120.0 / 8 / 3 |
| 向量 | `EMBED_BASE_URL` / `EMBED_MODEL` / `EMBED_DIM` / `EMBED_TIMEOUT` | — / `bge-m3` / 1024 / 120.0 |
| 建图 | `EDGE_MIN_CONFIDENCE` / `ALIAS_LINK_THRESHOLD` | 0.5 / 0.90 |
| 图通道 | `PPR_DAMPING` / `PPR_MAX_ITER` / `GRAPH_MAX_EDGES` | 0.85 / 50 / 30 |
| 检索 | `TOP_K` / `ENTITY_LINK_TOP` / `SEED_SCORE_THRESHOLD` | 6 / 6 / 0.34 |
| **G1** | `RETRIEVAL_POOL_TOP_N` | **`None`**（按 `max(top_k*4,24)` 推导） |
| **G2** | `RETRIEVAL_VECTOR_MIN_SCORE` | **`None`**（关闭） |
| 融合 | `VECTOR_WEIGHT` / `GRAPH_WEIGHT` / `RRF_K` | 1.0 / 1.0 / 60 |
| 词面 | `LEX_WEIGHT` / `LEX_TOP` / `LEX_FIRST` | 0.0（关） / 30 / 0 |
| 上下文 | `CONTEXT_MAX_CHARS` | 3000 |

`_env_opt_int` / `_env_opt_float` 两个新 helper 的语义是：**未设置 / 空 / 非法 → `None`**，
不是 `0`。这是「`None` = 关闭」旋钮的必需前提——`0.0` 会被误读成「阈值 0.0」
（对余弦来说等于不关闭，对池宽来说等于全空）。

---

## 6. 数据工件

`data/compendium_rag/`（2026-10-21 实测）：

| 文件 | 大小 | 内容 |
|---|---|---|
| `corpus.json` | ~20.1 MB | 结构化语料 |
| `chunks.json` | ~11.0 MB | 3695 个检索块 |
| `graph.json` | ~11.6 MB | 7033 实体 / 27110 边，指纹 `14daf1bbfa407388`，normalizer `n2` |
| `chunk_index.npz` | ~14.1 MB | 块向量（bge-m3 1024 维） |
| `entity_index.npz` | ~26.9 MB | 实体名向量 |
| `cache/` | — | 抽取缓存（RAW 输出，3695/3695 覆盖） |
| `reports/` | — | 评测与诊断产物 |

> **`graph.json` 是 2026-10-12 落盘的快照**。用当前代码重建会得到 26853 条边
> （不是 27110）——差异来自归一化/合并规则的代码演进。任何「图有没有变」的判断
> 都必须先比对 `fingerprint` + `normalizer`，不能只看文件在不在。

---

## 7. 测试与验收

```powershell
# 全量（DSH 沙箱下需指定可写 basetemp）
$env:PYTHONDONTWRITEBYTECODE='1'
.\.venv\Scripts\python.exe -m pytest tests\compendium_rag\ -q
```

2026-10-21 基线：**383 passed, 7 skipped → 398 passed, 7 skipped**（本轮新增 15 条：
`test_retriever.py` 12 条 + `test_graph_store.py` 3 条）。唯一 warning 是 FastAPI
`StarletteDeprecationWarning`，预存，与本轮无关。

> DSH 沙箱下 `tmp_path` 落在被 ACL 拒绝的目录，需要把 `TEMP`/`TMP` 指到工作区内并给
> pytest 一个可写 `--basetemp`，否则会得到一批与代码无关的 `FileNotFoundError`。

四条缺口的验收口径（计划 §5，**已写死**）：

1. `pytest tests/compendium_rag/` 全绿，含新增 ≥9 测试 —— **已满足（15 条）**。
2. 每条缺口的**默认值关闭路径与原行为逐字节一致** —— G2 `min_score=None`、
   G1 `pool_top_n=None` 公式等价。
3. eval300（`data/knowledge/_audit/rag_testset_300_cn.json`，`--top-k 6`）：
   hit@6 与 MRR **不退化** —— hit@6 ✅（两个模式都不退化且略升）；
   MRR full 模式 **−0.0018**（3 题，归因见 §7.3），graph_only **+0.0017**。
4. **G3 不得宣称召回提升**，只验契约对称性。
5. 产出变更报告 JSON + md，含受影响实体数 / 块对数 / 边分数变化 —— ✅
   `data/compendium_rag/reports/four_gaps_change_report_2026-10-21.{md,json}`。

### 7.1 同日对照（唯一有效的验收判据）

跨日比数字是不可靠的：工件、代码、嵌入、`sys.path` 任一变动都会污染读数。本轮的验收
一律用**同一天、同一工件、同一 harness，只换 `src` 树**的对照。

同一库（chunks 3695 / entities 7033 / edges 27110）、同题集、`top_k=6`：

| 模式 | 口径 | HEAD hit@6 | 本版 hit@6 | HEAD MRR | 本版 MRR |
|---|---|---|---|---|---|
| full | all（n=300） | 0.5267 | **0.5300** | 0.4056 | 0.4043 |
| full | **answerable（n=196）** | 0.8010 | **0.8061** | 0.6156 | 0.6138 |
| graph_only | all（n=300） | 0.4400 | 0.4400 | 0.3226 | **0.3243** |
| graph_only | answerable（n=196） | 0.6684 | 0.6684 | 0.4887 | **0.4912** |

逐题：full 模式 hit 上升 1 题（R167）、下降 0 题，RR 变动 3 题；
graph_only hit 升降均为 0，RR 变动 1 题（R104）。

### 7.2 「r11 基线」不可复现

`data/compendium_rag/reports/eval_300cn_k1_r11.{log,json}` 的 full/answerable
**0.852 / 0.662** 在本机复现不出来：未改动的 HEAD 代码 + 同一批工件只跑出
**0.8010 / 0.6156**（逐题差 18 题）；graph_only 更是 0.530（报告）vs **0.4400**（实测）。

已排除：工件变更（`graph.json` mtime 10-10 09:46 < 报告 11:17；索引 9/27；题集 9/25）、
代码变更（`src/compendium_rag/` 最后提交 `c20f3ff` 10-10 09:40，也早于报告）、
嵌入漂移（fresh 重嵌 vs 索引向量 cos min 0.9969 / mean 0.9987，且 graph_only 不走向量通道
却同样有差）。**结论：该报告产生于一个当前不可复现的代码/运行态，不能当门槛。**

### 7.3 MRR 归因

把 HEAD 的 `personalized_pagerank` 用 `ast` 抽出来塞回当前代码（其余改动保持），
R007 / R135 / R167 的 top-6 顺序**逐位恢复成 HEAD**。⇒ 排名变化唯一来源是
**G4 的 dangling 回流**（默认开启，属预期副作用，不是 G1/G2/G3 引入的）。

回归命令（`scratch_r12/eval_head.py` 按 `EVAL_SRC` 绑定 src 树并打印绑定校验）：

```powershell
$env:EVAL_SRC = "$PWD\scratch_r12\headsrc\src"   # 或 "$PWD\src"
.\.venv\Scripts\python.exe scripts\compendium_rag_eval300.py `
    --set data/knowledge/_audit/rag_testset_300_cn.json --top-k 6 `
    --out scratch_r12\eval_head_full.json
```

> ⚠️ **务必先核 `== 绑定校验 ==` 三行**（`EVAL_SRC` / `compendium_rag from` /
> `retriever.py bytes`）。本机存在多个 checkout，不锁 `sys.path` 会静默导入别人的
> `compendium_rag`，读数全废（本轮早期踩过）。

---

## 8. 改动守则

1. **默认关闭**：任何新旋钮的默认值必须复现旧行为。加功能不加默认分。
2. **顺序确定化**：任何进入 `[:N]` 截断或排序的容器都要有全序键
   （`chunk_ids` 按 `(block 序, chunk_id)`；种子按 `(-score, -len(name), eid)`；
   RRF 输出按 `(-score, chunk_id)`）。暖/冷进程必须同结果。
3. **可溯源**：新增边/证据必须带 `chunk_ids` + `evidence`。
4. **诚实口径**：正确性修复不要包装成召回提升；收益必须在真实工件上量，
   且区分「工件陈旧度」与「本轮改动作用面」（方法见 §4.3 的两套口径表）。
5. **动数据前先量爆炸半径**：`graph.json` 的重建会牵连上千条边的变动，
   必须先用 A/B/C 三口径（工件 / 改动前代码重建 / 改动后代码重建）拆开，
   再决定是否落盘。
