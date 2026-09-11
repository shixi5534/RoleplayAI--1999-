# GraphRAG 加强计划书（详细实施版）

> 项目：roleplay-ai（无名者 Ms. Stranger）
> 版本：v1.2 ｜ 日期：2026-09-07（v1.0 2026-09-06，v1.1 2026-09-07）
> 摘要版：[GRAPHRAG_ENHANCEMENT_PLAN.md](../GRAPHRAG_ENHANCEMENT_PLAN.md)（本文是其逐模块展开，冲突时以本文为准）
> 代码基线：分支 `refactor/frontend-layout`，全量测试 527 passed / 1 skipped
> 调研基线：2026-09-06 GitHub 实测（微软 GraphRAG 维护模式 / LightRAG 30.6k / HippoRAG 2 4.0k）
> **v1.1 新增**：§16 剧情图谱层（PlotGraph）——用 GraphRAG 存**实际剧情**（266 份 B站
> 转写文案），与 §1-§15 的 lore 向量 RAG 及 lore 图谱**完全独立**（文件/索引/开关/
> 预算/来源标签五重隔离，默认关闭，零回归）。
> **v1.2 新增**：§16.11 质量修复记录——首轮建图冒烟暴露的别名抢占 bug、ASR 噪声
> 实体过滤、实体链接收紧（含修复前后量化对比与重建注意事项）。

---

## 1. 背景与问题定义

### 1.1 现状量化（已逐行验证）

| 维度 | 现状 | 代码位置 |
|---|---|---|
| 检索 | 纯向量 + BM25 混合，**单跳** | `core/knowledge/vector_store.py:339-369` |
| 查询 | 用户原话直查，无改写、无实体识别 | `orchestrator.py:506`（`req.message` 原样传入） |
| 注入 | `top_k=2` + 相对分数门 0.85 | `config.py:61-63`、`persona_prompt.py:39-53` |
| 三元组 | LLM 已产出 subject/predicate/object，**零消费** | `event_extractor.py:95-107` → `memory_tier.py:112-123` |
| 语料 | `lore_wu_ming_zhe` 927 块 / 57 万字 | `data/knowledge/lore_wu_ming_zhe.json` |
| events | **空**（长期记忆未沉淀） | `data/knowledge/events*.json` ≈ 2B |
| 图能力 | 无任何实现，无图依赖 | 全仓库 grep 零命中 |

### 1.2 典型失败案例（驱动需求）

| 用户问法 | 现状表现 | 图谱期望 |
|---|---|---|
| 「凯拉死后，无名者的发条装置怎么样了？」 | 向量检索只能命中"凯拉之死"或"发条装置"其中一个 chunk，两个实体的关联散落在 927 块中，top_k=2 必漏 | PPR 从 {凯拉, 发条装置} 两个种子出发，两跳内把「凯拉 —死亡→ 触发 —象征→ 发条装置」的边链浮到前排，证据块成对召回 |
| 「格蕾丝和莉莉是同一个人吗？」 | 两个名字各自命中不同 chunk，无归一 | 别名表把四个曾用名归一到「无名者」单一实体 |
| 「上次我们约定了什么？」 | events 空 + 无时间线查询 | 对话边带 ts/occurred_round，按时间排序返回 |
| 「你们组织是怎么运作的？」 | 无语料级摘要，top_k=2 拼不出全局图景 | （P3）社区摘要注入 |

### 1.3 目标与非目标

**目标**：
1. 多跳事实类问题可答：多跳指标（`eval_rag_standard.py`）相对基线提升 ≥10%。
2. 单跳/闲聊零劣化：Faithfulness 不降、注入字符预算不超、延迟 p95 增幅 <50ms。
3. 零回归：`graph_enabled=False` 时行为与现状一致；SSE 契约、`/chat` 接口不动。
4. 按角色隔离：图谱数据、检索、增量写图全部 per-character，跨角色不串台。

**非目标**（本期不做）：
- 分布式/大规模图谱（927 块规模，JSON 邻接表足够）；
- 实时流式图谱更新（对话写图走每 N 轮沉淀节奏，与 `consolidate_every` 同步）；
- 多角色联合图谱（跨角色关系图留待真实需求出现）。

---

## 2. 总体设计

### 2.1 架构与数据流

```
┌─────────────────────── 离线索引层（幂等，可中断续跑） ───────────────────────┐
│ scripts/build_graph.py --character wu_ming_zhe                              │
│   ① 取 lore_<cid> 全部 chunk（KnowledgeBase.list_items）                    │
│   ② chunk sha1 → 缓存命中? 跳过 : LLM 抽取（附录A 提示词，batch=8 并发）      │
│   ③ 实体归一：canonical 名 + aliases 合并（角色卡 entity_aliases 优先）      │
│   ④ 边构建：confidence ≥ 阈值，evidence = (ns, doc_id, chunk_hash)          │
│   ⑤ GraphStore 落盘 graph_<cid>.json（原子写 + index_fingerprint）           │
│ 对话侧（每 consolidate_every 轮）：consolidate_entries 的 s/p/o → 增量写边   │
└─────────────────────────────────────────────────────────────────────────────┘
┌─────────────────────── 在线检索层（每轮，目标 <10ms + 1 次嵌入调用） ────────┐
│ Orchestrator._gather_context 第三路 gather：                                 │
│   ① 实体链接：BM25 词元匹配（零调用）→ 无命中再实体名向量余弦（1 次调用）     │
│   ② PPR 展开激活：种子=链接实体，转移权=confidence×importance，d=0.85         │
│   ③ 边选取：PPR 分 top graph_max_edges 且 BFS 跳距 ≤ graph_max_hops          │
│   ④ 证据解析：EvidenceResolver 按 chunk_hash 回查 KnowledgeBase 原文          │
│   ⑤ build_graph_context() 渲染 → 与向量块统一去重 → 注入 system prompt       │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 新增/改动模块一览

| 模块 | 类型 | 职责 |
|---|---|---|
| `core/knowledge/graph_store.py` | 新增 | GraphStore：实体/边存储、别名表、邻接查询、指纹、增量删除 |
| `core/knowledge/graph_extract.py` | 新增 | LLM 实体关系抽取（含幂等缓存）、抽取结果归一 |
| `core/knowledge/graph_search.py` | 新增 | 实体链接 + PPR + 证据解析（EvidenceResolver） |
| `scripts/build_graph.py` | 新增 | 离线构建 CLI（dry-run/重建/续跑） |
| `tests/test_graph.py` | 新增 | 图谱全模块单测 |
| `config.py` | 修改 | `graph_*` 配置段 |
| `core/knowledge/factory.py` | 修改 | `KnowledgeServices` 增 `graph_store`，`build_services` 装配 |
| `api/deps.py` | 修改 | `build_orchestrator` 注入图谱参数 |
| `core/orchestrator.py` | 修改 | `_gather_context`/`_retrieve` 第三路并行检索；`_persist` 挂钩增量写图 |
| `core/persona_prompt.py` | 修改 | `build_graph_context()`、`_source_label` 加 graph 标签 |
| `core/knowledge/memory_tier.py` | 修改（P2） | `consolidate_entries` 返回结构化条目供写图（或编排层直接取） |
| `api/knowledge.py` | 修改 | 图谱调试端点 2 个 |
| `models/character.py` | 修改（可选） | `entity_aliases` 字段 |
| `scripts/eval_rag_standard.py` | 修改（P4） | `--graph` A/B 开关 |
| `core/knowledge/plot_corpus.py` | 新增（§16） | 剧情语料层：转写 md 扫描/白名单/切块/落盘/BM25 |
| `core/knowledge/plot_graph.py` | 新增（§16） | 剧情图谱层：语言感知抽取 + PPR 检索 + 注册表 |
| `scripts/build_plot_graph.py` | 新增（§16） | 剧情层离线构建 CLI（建语料/建图/统计/别名挖掘） |
| `tests/test_plot_graph.py` | 新增（§16） | 剧情层单测（隔离/语言/PPR/零回归）13 项 |

### 2.3 关键设计决策（ADR）

| # | 决策 | 理由 |
|---|---|---|
| D1 | 存储用**纯 JSON 邻接表**，不用 networkx/neo4j | LightRAG 默认存储即 JsonKV+NetworkX 全内存+文件持久化，小规模已被验证；我们 927 块、数百实体，纯 dict 足够；Windows 环境（win32）零编译依赖 |
| D2 | 邻域排序用 **PPR** 而非 BFS k-hop | HippoRAG 2 论文核心：多跳关联自然浮到前排；约 30 行纯 Python；k-hop 仅保留为"跳距上限"约束 |
| D3 | 证据溯源存 **(ns, doc_id, chunk_hash)** 而非 KB chunk id | 已验证 `KnowledgeBase.add` 生成 `f"{ns}-{seq}"` 顺序 id（vector_store.py:201），KB 重建后 id 全变；chunk 文本 sha1 稳定 |
| D4 | 图谱上下文**独立预算、独立来源标签**，不挤占向量 top_k | top_k=2 是刻意降噪配置；图谱是增量信息源，挤占会劣化单跳 |
| D5 | 抽取/对话**分模型**配置 | 照搬 LightRAG 角色化 LLM 配置与"抽取用非思考快速模型"建议；本地场景抽取专职 qwen 小模型即可 |
| D6 | 指纹校验（embedder/llm/schema 版本） | 照搬 HippoRAG 2 index_manifest：模型切换后旧图谱向量/口径失配，宁可拒绝检索也不静默出错 |
| D7 | 实体链接两级：BM25 词元优先、向量兜底 | 实体名多为专名，BM25 命中零嵌入调用（复用 `_BM25`）；纯语义问法（"那个钟表机器"）才花 1 次嵌入调用 |

---

## 3. GraphStore 详细设计（`graph_store.py`）

### 3.1 落盘格式（`data/knowledge/graph_<cid>.json`）

```json
{
  "fingerprint": {
    "schema": "v1",
    "embedder": "nomic-embed-text",
    "embed_dim": 768,
    "extract_llm": "qwen3:8b",
    "built_at": 1780000000.0
  },
  "entities": {
    "e_wu_ming_zhe": {
      "name": "无名者", "type": "角色",
      "aliases": ["格蕾丝", "莉莉", "凯拉", "塞西莉", "Ms. Stranger"],
      "mentions": 47,
      "summary": "", "vec": null
    }
  },
  "edges": [
    {
      "src": "e_wu_ming_zhe", "dst": "e_clockwork_device",
      "relation": "持有",
      "confidence": 0.92, "importance": 0.8,
      "evidence": [{"ns": "lore_wu_ming_zhe", "doc_id": "lore_md", "hash": "a1b2c3…"}],
      "ts": 1780000000.0, "source": "lore"
    }
  ],
  "alias_index": {"无名者": "e_wu_ming_zhe", "格蕾丝": "e_wu_ming_zhe"}
}
```

要点：
- `alias_index` 落盘冗余（运行时 dict 直查，O(1) 精确命中）；
- `vec` 默认 `null`——实体名向量**启动时懒加载**（首次检索按需批量嵌入并回写），避免构建期对嵌入器的硬依赖；
- 边的 `importance` 取证据块的 meta `importance`（lore 块默认 0.7）或对话边的提取值。

### 3.2 类接口

```python
class GraphStore:
    def __init__(self, path: Path, character_id: str | None = None,
                 min_confidence: float = 0.55) -> None: ...
    # —— 查询 ——
    def link_exact(self, mention: str) -> str | None            # alias_index 精确命中
    def entities(self) -> list[dict]                            # 全量实体（含 name/aliases，供 BM25/向量链接）
    def neighbors(self, eid: str) -> list[tuple[dict, dict]]    # (edge, 对端实体) 正反向合并
    def edges_of(self, eid: str) -> list[dict]                  # 实体的全部边（时间线用）
    def stats(self) -> dict                                     # 端点统计
    # —— 写入 ——
    def upsert_entities(self, items: list[dict]) -> list[str]   # 归一去重（名/别名冲突→mentions 累加）
    def upsert_edge(self, edge: dict) -> bool                   # (src,dst,relation) 相同边合并：evidence 并集、confidence 取 max
    def remove_by_doc(self, ns: str, doc_id: str) -> int        # 见 3.3
    def set_entity_vec(self, eid: str, vec: list[float]) -> None
    # —— 持久化 ——
    def save(self) -> None          # tempfile + os.replace 原子写（对齐 KnowledgeBase._save_ns）
    def check_fingerprint(self, embedder_name: str, dim: int) -> bool
```

### 3.3 `remove_by_doc` 增量清理（照搬 LightRAG 删除重建）

触发时机：`ingest_file` 带 `doc_id` 重复导入（幂等替换）或删除文档后，编排层调用。
算法：遍历边，若 `evidence` 全部属于 `(ns, doc_id)` → 删边；否则过滤掉该 doc 的证据条目。删边后 `mentions` 递减，为 0 的实体删除（除非被 `entity_aliases` 显式锚定）。返回清理边数。**这是防图谱与 KB 漂移的唯一机制，P0 必做。**

### 3.4 并发模型

在线检索只读、增量写图发生在 `_persist` 的会话锁内（与长期记忆写入同锁），无跨协程竞争；构建脚本与服务器互斥（脚本启动时若检测到 `.lock` 文件报警告）。不需要进程级锁。

---

## 4. 离线抽取管线（`graph_extract.py` + `scripts/build_graph.py`）

### 4.1 抽取流程

```
for batch in chunked(pending_chunks, size=8):        # asyncio.Semaphore(8)
    results = await asyncio.gather(*[extract_one(c) for c in batch])
    for chunk, res in zip(batch, results):
        if res is None: failed.append(chunk); continue
        cache.write(chunk_hash, res)                  # 幂等缓存
        store.upsert_entities(...); store.upsert_edge(...)
store.save()
```

- `chunk_hash = sha1(text).hexdigest()[:16]`，缓存文件 `data/knowledge/graph_cache/<cid>/<hash>.json`；
- **续跑**：启动时先扫缓存，命中即跳过 LLM；中断重跑零重复成本；
- **失败兜底**：单块 LLM 失败/超时（12s）记入 `failed`，不影响整体；结尾打印失败清单与重试命令；
- JSON 解析复用 `LLMEventExtractor._parse_json` 的三级兜底模式（json.loads → 正则抽对象 → 跳过）。

### 4.2 成本估算（927 块）

| 抽取模型 | 单块耗时 | batch=8 总耗时 | 说明 |
|---|---|---|---|
| 本地 qwen3:8b（ollama） | ~2-4s | **5-10 分钟** | 推荐默认，`ROLEPLAY_GRAPH_EXTRACT_PROVIDER=ollama` |
| 本地 30B 级 | ~8-15s | 20-40 分钟 | 质量更高，可选 |
| 对话主模型 | — | 不建议 | 避免与在线服务抢吞吐 |

内存：全量 chunk 文本 + 图谱常驻 <50MB，无压力。

### 4.3 实体归一与别名草稿

合并顺序（优先级降序）：
1. 角色卡 `entity_aliases` 显式表（人工权威）；
2. 抽取结果 `aliases` 声明（LLM 判断的同指）；
3. 运行时向量合并：实体名嵌入余弦 ≥ `graph_entity_link_threshold`(0.82) 的候选对**只生成报告不自动合并**（`--review` 输出 `graph_review_<cid>.md`，人工确认后回填角色卡别名表）。

### 4.4 CLI 规格

```bash
python scripts/build_graph.py --character wu_ming_zhe          # 全量增量构建
python scripts/build_graph.py --character wu_ming_zhe --dry-run  # 抽 10 块预览 JSON，不落盘
python scripts/build_graph.py --character wu_ming_zhe --rebuild  # 清缓存+图谱重建
python scripts/build_graph.py --character wu_ming_zhe --review   # 生成别名归并人工复核报告
```

构建顺序按 chunk meta：核心资料（doc_id=档案/汇编）→ 剧情摘录 → 视频文案转写；`--limit N` 支持分批。

---

## 5. 在线检索设计（`graph_search.py`）

### 5.1 实体链接（`link_entities(query) -> dict[eid, weight]`）

```
第一级（零网络调用）：query 分词（复用 _BM25 中文单字+英文词切分）→ 对 (name+aliases)
    全量做最长匹配 + BM25 词元命中 → weight=1.0（别名命中与正名同权）
第二级（1 次嵌入调用，仅当第一级零命中）：aembed_query(query) 与实体名向量
    （启动懒加载并缓存）余弦 ≥ 0.82 的 top-3 → weight=相似度
```

### 5.2 PPR 算法规格

```
输入：种子 S（|S|≤5，weight 归一），邻接表 G，d=graph_ppr_damping(0.85)
r₀(v) = 1[v∈S]/|S|
r_{t+1}(v) = (1-d)·1[v∈S]/|S| + d·Σ_{u→v} r_t(u)·w(u,v)/outdeg(u)   （w=confidence×importance）
收敛：L1‖r_{t+1}-r_t‖ < 1e-6 或 t=graph_ppr_max_iter(50)
```

- 边得分 = `r(src) + r(dst)`，过滤 BFS 跳距 > `graph_max_hops`(2) 的边，取 top `graph_max_edges`(12)；
- 复杂度 O(iter × E) ≈ 50 × 数百 = 毫秒级；实现约 30 行纯 Python；
- 单测锚点：三角关系（A→B→C 无 A→C 直达边）查询 C 时 B 的证据必须入选（多跳可达性）。

### 5.3 证据解析（`EvidenceResolver`）

- 构建：首次使用时从 `KnowledgeBase.list_items(ns)` 建 `{chunk_hash: (text, meta)}` 映射，监听 KB `_version` 失效重建；
- 返回 `RetrievedChunk(text, score=edge_score, metadata={...原meta, "namespace": ns, "via": "graph", "edges": [边描述]})`，从而**直接复用** `build_rag_context` 的渲染与去重通道。

### 5.4 延迟预算

| 步骤 | 耗时 |
|---|---|
| BM25 实体链接 | <1ms |
| PPR 迭代 | <5ms（数百实体） |
| 证据查表 | <1ms |
| （兜底）向量链接 | +1 次嵌入调用（~20-50ms，仅 BM25 零命中时） |

---

## 6. 编排与提示词集成

### 6.1 `_retrieve` 修改草案（`orchestrator.py`）

```python
# _gather_context 中与向量检索 asyncio.gather 并行（新增第三路）：
graph_ctx = await self._graph_retrieve(req.message, card_obj, character_id)

async def _graph_retrieve(self, query, card_obj, character_id):
    if not self._graph_enabled or self._graph_store is None:
        return []                                   # 降级：返回空
    if card_obj and "graph" not in (card_obj.knowledge_scope or []) \
       and not self._graph_default_on:              # 知识范围未授权图谱时跳过（见 6.4）
        return []
    try:
        return await asyncio.to_thread(             # 纯 CPU，丢线程池不阻塞循环
            graph_search.retrieve, self._graph_store, self._knowledge_base,
            query, top_edges=self._graph_max_edges, ...)
    except Exception as exc:
        logger.warning("图谱检索失败，本轮跳过：%s", exc)
        return []
```

合并规则：图谱证据块与向量块按 `(namespace, 文本前 64 字符)` 去重，图谱块追加在向量块**之后**（向量块是主信息源）。

### 6.2 `build_graph_context()` 渲染格式（`persona_prompt.py`，对齐 `build_profile_context` 先例）

```
【关系脉络（你的记忆之间的关联）】
这些关联是你亲身经历的连接，可自然提起，不要像报数据库一样罗列。

（关系·持有）你 — 发条装置 ：它毁于凯拉之死那天
（关系·象征）发条装置 ：蛹与钟摆，你重启人生的执念
（记忆碎片）<证据 chunk 原文，最多 2 条，经 _source_label 标注>
```

- 独立预算 `graph_context_max_chars=1200`，超预算按边得分截断；
- `_source_label` 增加：`ns.startswith("graph")` → 「关系脉络」（实际图谱不进 KB，此分支用于证据块 meta 传递）；
- `build_roleplay_prompt` / `build_roleplay_messages`（分层模式 `PromptLayers.system_blocks`）各加一个 graph 块位，空串跳过（沿用 profile 块的既有惯例）。

### 6.3 知识范围约束

沿用 `resolve_knowledge_namespaces` 的映射惯例：角色卡 `knowledge_scope` 含占位符 `"graph"` 时映射为该角色图谱放行；**默认卡不含 `graph` → 图谱关闭**（显式 opt-in，与 lore 隔离哲学一致）。`ingest_lore.py` 导入后自动绑定改为 `["lore_<cid>", "graph", "events", "episodic"]`。

### 6.4 降级矩阵（零回归保证）

| 条件 | 行为 |
|---|---|
| `graph_enabled=False` | 不构建 GraphStore，检索路径与现状逐字节一致 |
| 图谱文件缺失 / 指纹不匹配 | warning 日志 + 跳过图谱路（不拦截对话） |
| 实体链接零命中 | 返回空，图谱块不注入 |
| `_graph_retrieve` 抛任何异常 | warning + 返回空（永不影响主链路） |

---

## 7. 对话增量写图（P2）

- 挂钩点：`_persist` 内 `extract_event_entries` 之后（每 `consolidate_every=6` 轮），把 s/p/o 非空的条目转边写入：`src=说话主体实体, dst=宾语实体, relation=predicate, source="conversation"`，`ts=now`、`occurred_round` 落边；
- 对话侧实体先与图谱做链接（复用 5.1，阈值放宽到 0.78）：命中→并入既有实体（mentions+1）；未命中→创建 `pending` 实体，mentions ≥3 自动转正（防一次性噪声污染图谱）；
- 对话边 `importance` 默认 ×0.8 权重（低于 lore 边），防单次对话长入主干；
- 时间线查询：`edges_of(eid)` 按 `ts` 排序 + 关联证据块 →「上次我们约定了什么」可回答（eval 增 2 个时间线用例）。

## 8. 全局问答（P3，可选）

- 社区划分：纯 Python 连通分量（`union-find`，~20 行）→ 每分量 ≥5 实体时 LLM 生成 2-3 句摘要（缓存进图谱文件 `community_summaries` 段，幂等）；
- 路由：规则命中宏观词（你们/组织/世界/整体/看法/风格）→ 注入 top-2 社区摘要（预算并入 graph 块）；
- 验收后若不足：LightRAG REST sidecar 只替换全局层（保留自研实体级检索）。

---

## 9. 配置项（`config.py`，`ROLEPLAY_` 前缀，全部带默认值）

```python
# ── GraphRAG（图谱增强检索） ──
graph_enabled: bool = True              # 总开关；False = 完全回退现状
graph_max_edges: int = 12               # 单次注入边上限
graph_max_hops: int = 2                 # 证据边距上限（跳距约束）
graph_edge_min_confidence: float = 0.55 # 边参与检索的置信度下限
graph_context_max_chars: int = 1200     # 图谱上下文独立预算
graph_entity_link_threshold: float = 0.82   # 实体名向量合并/链接阈值
graph_ppr_damping: float = 0.85         # PPR 阻尼
graph_ppr_max_iter: int = 50            # PPR 最大迭代
graph_extract_provider: str = ""        # 抽取专用 LLM（空=跟随 llm_provider）
graph_extract_batch: int = 8            # 离线抽取并发
graph_cache_dir: str = "./data/knowledge/graph_cache"
```

## 10. 调试 API（`api/knowledge.py`）

| 端点 | 响应示例 |
|---|---|
| `GET /api/knowledge/graph/stats?character_id=wu_ming_zhe` | `{"entities": 86, "edges": 214, "by_type": {"角色": 12, ...}, "top_degree": [{"name": "无名者", "degree": 38}], "fingerprint": {...}, "stale": false}` |
| `GET /api/knowledge/graph/entity?q=发条装置&character_id=...` | `{"seed": {"id": "...", "name": "发条装置", "aliases": []}, "linked_by": "bm25", "neighbors": [{"name": "无名者", "relation": "持有", "direction": "in", "confidence": 0.92}], "evidence": [{"hash": "...", "text": "...前 120 字"}]}` |

错误处理：图谱未构建 → 404 + 提示运行 build_graph；指纹失配 → 409 + `stale: true`。

## 11. 测试计划（`tests/test_graph.py` + 既有套件回归）

| 模块 | 用例（≈28 项） |
|---|---|
| graph_store | 落盘/加载往返；原子写中断不留半文件；alias_index 一致性；upsert_edge 同边合并（evidence 并集/confidence 取 max）；remove_by_doc 三分支（删边/过滤证据/实体 mentions 归零删除）；指纹失配拒绝 |
| graph_extract | 三级 JSON 解析（正常/围栏/噪声）；单块超时不拖垮批次；缓存幂等（同 hash 不二次调用——用 FakeLLM 计数断言）；实体归并优先级（角色卡 > LLM aliases） |
| graph_search | 别名精确链接；BM25 零命中走向量链接（FakeEmbedder）；**三角多跳可达**；跳距过滤；EvidenceResolver 按 hash 命中与 KB 重建失效重建；PPR 收敛与孤立实体不参与 |
| orchestrator 集成 | graph 块注入顺序（persona→tone→profile→rag→graph→tail）；`knowledge_scope` 无 graph 时零注入；异常降级不影响向量路径；FakeLLM 全链路冒烟 |
| persona_prompt | build_graph_context 预算截断；空图谱零块；分层模式 graph 块进 system_blocks |
| 回归 | 既有 462 项全绿；`graph_enabled=False` 时 `/chat/stream` SSE 契约 diff 为空 |

## 12. 评估方案（P4）

- 协议：`python scripts/eval_rag_standard.py --graph`（开关图谱路），同一 60 用例集跑两遍，输出对比表；
- 指标判定（基线 `deliverables/rag-eval-standard.json`）：

| 指标 | 通过标准 |
|---|---|
| Multi-hop | **≥ 基线 +10%**（预期主要增益来源） |
| Context Precision / Recall | 不降（±2% 容差） |
| Faithfulness | 不降（硬性） |
| 端到端延迟 p95 | 增幅 <50ms |

- 产出：`deliverables/graphrag-ab-report.md`（含失败用例逐条归因：链接失败/边缺失/证据噪声）。

## 13. WBS 与排期（单人，净估时；P3 可选）

| ID | 任务 | 依赖 | 估时 | DoD |
|---|---|---|---|---|
| T1 | config 字段 + GraphStore + 单测 | — | 1d | store 单测全绿 |
| T2 | graph_extract（提示词/缓存/归并）+ 单测 | T1 | 1d | FakeLLM 单测全绿 |
| T3 | build_graph CLI + 全量构建 + --review 报告 | T2 | 1d | 927 块建图完成，人工抽检 20 边全对 |
| T4 | graph_search（链接/PPR/证据）+ 单测 | T1 | 1d | 三角多跳单测过 |
| T5 | orchestrator/persona_prompt/deps 集成 + 降级 | T3,T4 | 1d | 端到端注入验证；零回归 |
| T6 | 调试 API + stats | T5 | 0.5d | 两个端点联调 |
| T7 | eval --graph A/B + 报告 | T5 | 1d | multi-hop 达标或归因清楚 |
| **M1-M2** | **P0+P1+P4 评估 = 可用里程碑** | | **≈6.5d** | |
| T8 (P2) | 对话增量写图 + 时间线 + pending 实体 | T5 | 1.5d | 多轮对话图谱增长；时间线用例过 |
| T9 (P3) | 社区摘要 + 全局路由（可选） | T7 | 2d | 宏观问题 A/B 改善 |

## 14. 风险登记册

| 风险 | 概率 | 对策 | 触发指标 |
|---|---|---|---|
| LLM 抽取幻觉污染图谱 | 中 | confidence 过滤 + evidence 溯源 + 抽检 20 边 + 对话边降权 | 抽检错误率 >10% → 降阈值换模型 |
| 实体歧义（四曾用名） | 高 | 角色卡别名表权威 + --review 人工复核流程 | 链接成功率 <70% |
| 证据 chunk_hash 与 KB 漂移 | 低 | remove_by_doc 同步清理 + resolver 版本监听 | 证据命中率 <90% |
| 上下文预算膨胀 | 低 | 独立预算 1200 字符 + 边数上限 + 得分截断 | system prompt 超 6K 字符 |
| 抽取成本超预期 | 低 | 缓存幂等 + batch 限流 + --limit 分批 + 专职小模型 | 单块 >15s |
| 指纹误拒（正常升级） | 低 | fingerprint 显式 schema 版本 + `--rebuild` 明确动作 | — |
| Windows 文件锁/编码 | 低 | 沿用 tempfile+os.replace 与 utf-8 既有惯例（KnowledgeBase 同款） | — |

## 15. 交付物清单

| 里程碑 | 交付物 |
|---|---|
| M1（T1-T3） | 可重建的 `graph_wu_ming_zhe.json` + 缓存 + review 报告 |
| M2（T4-T6） | 在线图谱检索上线（默认开启、可降级）+ 调试 API |
| M3（T7） | `deliverables/graphrag-ab-report.md`（A/B 数据） |
| M4（T8-T9） | 对话记忆图谱 + 时间线；（可选）全局摘要 |

---

---

## 16. 剧情图谱层（PlotGraph）：用 GraphRAG 存**实际剧情**

> 本章独立于 §1–§15。lore 层（角色设定资料）与 plot 层（实际剧情）是**两条互不引用**的链路；
> 本章所有开关默认关闭，关掉后系统行为与 v1.0 逐字节一致。

### 16.1 为什么需要单独一层

语料现状（2026-09-07 实测）：

| 指标 | 数值 | 说明 |
|---|---|---|
| 转写 md 文件 | **266** | `data/lore/wu_ming_zhe/视频文案/`，24 个 BV 号（259 个分P + 7 个单P） |
| 剧情语料切块 | **2477** | `chunk_size=600`，落盘 2.5 MB（纯文本，无向量） |
| 语种分布 | en **2329** / zh 146 / other 2 | 游戏为英配，转写正文 94% 为英文 |
| lore 知识库 | 2085 块 | 其中 **1961 块是已混入的转写**，手工资料仅 124 块 |
| 手工整理 md | 9 份 | 角色目录根，**严禁**进入剧情层 |

三个必须分层的理由：

1. **噪声等级不同**：转写是 ASR 产物（头部自述"机器提取，可能存在少量识别误差"），
   与人工整理的设定资料混在同一向量空间，会稀释 top_k=2 的珍贵配额；
2. **查询形态不同**：剧情问题是"叙事型"（谁对谁做了什么、第几章发生了什么、因果链），
   靠**实体关系与叙事顺序**组织，而非语义相似度；
3. **更新节奏不同**：转写随 B站更新随时增量，设定资料几乎不动。同一套索引会让
   每次增量都触发 lore 侧重建与指纹校验。

### 16.2 隔离边界（五重，逐条可验收）

| 维度 | lore 层（现有 RAG） | plot 层（剧情图谱） |
|---|---|---|
| 数据源 | 9 份手工 md（角色目录根） | 仅 `视频文案/`（三重白名单，见 16.3） |
| 命名空间 | `lore_<cid>` / `events:<cid>` / `profile` | `plot_<cid>`（只用于展示与来源标签） |
| 落盘文件 | `data/knowledge/lore_<cid>.json`（24 MB，含 768 维向量） | `plot_corpus_<cid>.json`（2.5 MB 文本）+ `plot_graph_<cid>.json`（图） |
| 检索实现 | `KnowledgeBase.asearch`（向量 + BM25 混合） | `PlotGraphRetriever`（实体链接 → PPR → 词法兜底） |
| 嵌入器依赖 | 强依赖（换嵌入器需重建） | **零依赖**（无向量，换模型/嵌入器不影响） |
| 开关 | `rag_enabled` / `graph_enabled` | `plot_graph_enabled`（**默认 False**） |
| 提示词块 | 【角色资料库】3200 字符 | 【剧情记忆】**独立** 1000 字符 |
| 来源标签 | `角色设定资料·章节` | `剧情记忆·3.8版本·世纪末的忧郁` |
| 写路径 | `ingest_file` / `_persist` 沉淀 | 仅 `scripts/build_plot_graph.py`（离线） |

验收口径：`plot_graph_enabled=False` 时 `_plot_retrieve` 直接返回 `[]`，
`build_plot_context([]) == ""`，提示词不出现【剧情记忆】块（§16.8 单测覆盖）。

### 16.3 语料隔离的三重白名单（防手工资料混入）

`plot_corpus._parse_transcript_file` 逐文件校验，任一不过即拒绝（返回 `None` 并计入 `rejected`）：

1. **目录白名单**：路径分段必须含 `视频文案`（9 份手工 md 在角色目录根，天然排除）；
2. **文件名白名单**：`^(BV[0-9A-Za-z]+?)(?:_p(\d+))?_` —— 不匹配即拒
   （如 `世界观_暴雨与阵营.md`）；
3. **头部白名单**：文件前 600 字符必须同时含 `来源：B站` 与 `机器提取`
   （伪造/串味的 md 即便改了名字也会被拦）。

实测：266 个文件全部通过，0 拒绝；单测另用「手工 md + 无头伪造 md」验证会被拒。

### 16.4 元数据与语言处理（约束①）

从 md 头部与标题正则解析，写入每个 chunk 的 meta：

```
doc_id  = BV12QEY6HEy7_p1        （多P带 _pN，与 ingest 脚本同口径）
version = 3.8                     ← 标题 `(\d+\.\d+)\s*版本`
arc     = 世纪末尺度               ← 标题 「…」
chapter = 世纪末的忧郁 / chapter_no = 1   ← 标题尾部 `（01.xxx）`
uploader / pubdate / duration / url
lang    = zh | en | other          ← 逐块启发式（CJK 占比 vs 拉丁占比）
method  = whisper语音转写 | B站CC/AI字幕
```

- **语种分流**（`prompt_for_lang`）：`en` 块走英文抽取提示词，要求
  **实体名保留英文原文**（如 `Madam Lucy`），并把去称谓短形式（`Lucy`）与
  **有把握的中文译名**一并写进 `aliases`；**关系谓语统一用中文**（隶属/持有/摧毁/杀死/
  象征/发动/约定…），保证图谱检索与提示词渲染语言一致。
- **跨语言归一**：`data/lore/<cid>/plot_aliases.json`（人工权威，最高优先级）
  → `bind_alias_table` 登记，使「露西女士 / Madam Lucy / Lucy」落到同一实体；
  构建脚本 `--mine-entities` 输出英文专名频次表
  （`data/knowledge/plot_entity_candidates_<cid>.md`，已剔除句首噪声词），
  人工填好译名后回填别名表即可。首版种子已含 圣洛夫基金会/重塑之手/拉普拉斯/
  芝诺军备学院/司辰/维尔汀 等对照。

### 16.5 图谱 schema（在 lore 图谱上做的剧情化扩展）

复用 `GraphStore`（纯 JSON 邻接表、别名索引、原子写），新增剧情语义字段：

| 字段 | 值 | 用途 |
|---|---|---|
| `evidence[]` | `{ns: plot_<cid>, doc_id: BV…_pN, hash}` | 证据溯源；`doc_id` 带分P，可定位到具体一集 |
| `source` | `"plot_transcript"` | 与 `lore`/`conversation` 边区分 |
| `importance` | **0.6**（lore 为 0.7） | ASR 证据整体降权，防噪声长入主干 |
| 孤证门控 | `len(evidence) < 2` 视为 weak | 只被一块（可能听错）支撑的边默认不注入，得分再 ×0.5；`plot_include_weak=True` 才放开 |
| 叙事顺序 | chunk meta `version/chapter_no/seq` | 「3.8 版本讲了什么」「第几章」可答（v1.1 先落 meta，P2 再建事件时序边） |

### 16.6 检索路径

```
query → ① 实体链接：别名/正名最长匹配（拉丁按词边界）→ 零命中则词元 BM25（阈值 0.35）
      → ② PPR 激活（无向化传播，w = confidence × importance，d=0.85，≤40 轮）
      → ③ 边选取：跳距 ≤ plot_max_hops(2) 且 confidence ≥ 0.6 且非孤证，取 top 10
      → ④ 证据回查 PlotCorpus.by_hash → 每条边取 1 条代表证据（去重）
      → ⑤ 不足时 BM25 词法兜底 ≤2 条（via=plot_lexical）
```

延迟：全内存数百边，PPR <5ms + 词法 <10ms，无网络调用；与向量检索并行（`asyncio.gather` 第四路），
端到端不额外增加串行耗时。

### 16.7 构建与运维（`scripts/build_plot_graph.py`）

```bash
python scripts/build_plot_graph.py --character wu_ming_zhe --build-corpus   # 扫目录→切块→落盘
python scripts/build_plot_graph.py --character wu_ming_zhe --stats          # 语料/图谱/缓存统计
python scripts/build_plot_graph.py --character wu_ming_zhe --mine-entities  # 英文专名候选（译名对照）
ROLEPLAY_LLM_PROVIDER=ollama ROLEPLAY_LLM_MODEL=qwen2.5:7b \
  python scripts/build_plot_graph.py --character wu_ming_zhe --build-graph --limit 300
python scripts/build_plot_graph.py --character wu_ming_zhe --build-graph --lang en  # 只抽英文块
```

- **幂等续跑**：`data/knowledge/plot_cache/<cid>/<hash>.json`，重跑只处理新增/失败块；
- **失败不拖垮**：单块超时（默认 60s）/解析失败记入 `failed` 清单，结尾打印可重跑哈希；
- **抽取专用模型**：`plot_extract_max_tokens=800`（对话默认 240 会把抽取 JSON 截断，
  实测输出被切成 `{"entities":[{"n`）、`plot_extract_concurrency=8`；
- **成本**：2477 块 × qwen2.5:7b(CPU) ≈ 3–6 小时全量，可分批 `--limit` 夜间跑；
  建议先跑英文块（`--lang en`，占 94%）。

### 16.8 调用逻辑改动清单（已落地）

| 文件 | 改动 | 回归风险 |
|---|---|---|
| `config.py` | 新增 `plot_*` 16 个配置项（默认关闭） | 无（新增字段，带默认值） |
| `core/knowledge/plot_corpus.py` | 新增 | 无（新模块） |
| `core/knowledge/plot_graph.py` | 新增 | 无（新模块） |
| `core/knowledge/graph_store.py` | 新增 `all_edges()` | 无（纯增方法） |
| `core/knowledge/graph_extract.py` | `extract(text, system=None)` 支持覆盖提示词 | 无（默认参数不变） |
| `core/knowledge/factory.py` | `KnowledgeServices.plot_graph` + `build_plot_registry()` | 无（仅在开关打开时装配） |
| `core/orchestrator.py` | `_gather_context` 返回三元组；新增第四路 `_plot_retrieve`；`_build_prompt` 透传 `plot_chunks` | 低（关闭时返回空列表） |
| `core/persona_prompt.py` | `build_plot_context()`、`_source_label` 支持 `plot_`、上下文块位 | 低（空 chunk 不产生块） |
| `api/deps.py` | 注入 `plot_*` 参数 | 无 |
| `api/knowledge.py` | `GET /api/knowledge/plot-graph/stats`、`/plot-graph/search` | 无（新端点） |
| `tests/test_plot_graph.py` | 新增 18 项（13 基础 + 5 质量修复） | — |

### 16.9 分阶段落地（在 §13 WBS 之后追加）

| ID | 任务 | 依赖 | 估时 | DoD |
|---|---|---|---|---|
| T10 | 剧情语料层 + 白名单 + 落盘 | — | 0.5d | 266 文件全部采纳、0 误纳；9 份手工 md 零混入 |
| T11 | 剧情图谱层（PPR + 别名 + 注册表） | T10 | 0.5d | 多跳/别名/孤证门控单测全绿 |
| T12 | 构建 CLI + 抽取提示词双语 + 缓存续跑 | T11 | 0.5d | `--build-graph --limit 50` 成功率 ≥90% |
| T13 | 编排器/提示词/API 接入（默认关闭） | T11 | 0.5d | 全量测试无回归；开启后【剧情记忆】块正确注入 |
| T14 | 全量建图 + 双语别名表人工复核 | T12 | 1d（机器时间）+ 0.5d 人工 | 图谱实体/边统计合理；抽检 20 边错误率 <10% |
| T15 | 剧情问答 A/B（剧情子集用例） | T13,T14 | 1d | 剧情类问题相对基线提升，单跳零劣化 |

### 16.10 新增风险

| 风险 | 概率 | 对策 | 触发指标 |
|---|---|---|---|
| ASR 误识别污染实体（如 `Manus Vindicte`） | 高 | 孤证门控 + importance 0.6 + 双语别名表统一正确形式 | 抽检错误率 >15% → 提高 `plot_edge_min_confidence` |
| 中英实体无法归一（露西 / Lucy） | 高 | 人工别名表 + `--mine-entities` 候选 + LLM 抽取自动带中文别名 | 链接成功率 <70% |
| 剧情剧透/人设冲突（角色"知道"未经历剧情） | 中 | 独立块 +「这是你的经历」措辞 + 默认关闭，按角色卡 opt-in | 一致性自检命中率上升 |
| 全量抽取成本（2477 块 × 本地 7B） | 中 | 缓存续跑 + `--limit` 分批 + 优先英文块 | 单块 >60s → 换更小模型 |
| 语料与 KB 长期双写不一致 | 低 | plot 层不写 KB；`bilibili_lore_ingest.py` 后续可切 `--namespace plot_<cid>` | — |

### 16.11 质量修复记录（T14 首轮 300 块冒烟后，v1.1）

首轮 300 块建图（693 实体 / 566 边）冒烟暴露三类问题，已全部修复并回归：

| # | 问题 | 根因 | 修复 | 效果（重建后实测） |
|---|---|---|---|---|
| Q1 | 别名冲突告警：`LSCC 已指向 e_bce91…，忽略对 拉普拉斯 的绑定` | 人工别名表与 LLM 抽取结果冲突 | `plot_aliases.json` 移除 LSCC（抽取已归它属）；补充 `Madam Lucy`/`维尔廷` 权威条目 | 17 条别名零冲突绑定 |
| Q2 | 「露西女士是谁」链接出 **11 个噪声种子**（ma'am、senora、An exorcist…） | ① ASR 噪声被抽成实体并**抢占**正牌别名；② `_ensure_entity` 合并路径覆盖 alias_index（后到者抢走 `露西`→Doris/Muriel）；③ 词法兜底 CJK 单字（生/了）匹配过松 | ① 新增 `is_noise_entity()` 建图过滤（称谓/冠词句段/含句读残句/≥4 词片段）；② 合并路径改为「首注册优先，不抢占」；③ 词法兜底弃用 CJK 单字 + 阈值 0.35→0.5 + 并列种子按「正名命中>mentions」排序截断 top-3 | 「露西女士是谁」11 种子 → **1 种子（Madam Lucy）**；「Madam Lucy」7→1；噪声查询（3.8版本…/暴雨是什么）3→0；图谱 693→560 实体、566→395 边 |
| Q3 | 部分查询退化为词法兜底（via=plot_lexical） | 300 块样本下多数边 evidence<2 被孤证门控，属预期 | 无需修复——全量建图后 evidence 随块数累积，图谱路自动激活 | 待 T14 全量完成后复测 |

新增测试 5 项：`test_ensure_entity_does_not_steal_alias`、`test_noise_entity_filter`、
`test_build_graph_filters_noise_entities`、`test_link_tie_break_caps_seeds`、
`test_link_lexical_ignores_single_cjk_overlap`。全量套件 527 passed（唯一失败
`test_llm_override_embedded_in_chat_request` 为 ollama 资源竞争导致的 502，与本次改动无关）。

> 重建注意事项：修复建图逻辑后**必须删除旧 `plot_graph_<cid>.json` 再重跑**
> （缓存命中不调 LLM，秒级回放 300 块）；`--rebuild` 会连缓存一起清，仅在
> 抽取提示词变更时使用。

**T14 全量建图完成（2026-09-07，ollama qwen2.5:7b，并发3，总耗时约 3h）**：
2477 块 → 成功 **2459 块（99.3%）**，18 块为 7B 模型对特定文本的确定性畸形
输出（重试无效，后续可换模型补齐）；噪声过滤 **1299 个实例**（含第二轮补充的
版本号实体模式 `^\d+\.\d+版本`）；图谱终态 **4396 实体 / 4102 边**
（角色1812/物品709/地点597/概念559/组织405/事件230/时间42）。冒烟验证：
「露西/露西女士/Madam Lucy」均 1 种子直达且 `via=plot_graph` 3/3（图谱路
已激活），「维尔汀和基金会」2 种子 `plot_graph` 3/3。全量套件 527 passed +
flaky 项复跑通过。

---

## 附录 A：抽取提示词草案（`graph_extract.py`）

```
你是知识图谱构建助手。从下面的角色设定/剧情文本中抽取实体与关系，只输出单行 JSON：
{"entities": [{"name": "<canonical 称呼>", "type": "角色|物品|地点|组织|概念|事件",
               "aliases": ["<同指的曾用名/代称/昵称>"]}],
 "relations": [{"src": "<实体名>", "dst": "<实体名>", "relation": "<简短中文谓语>",
                "confidence": 0.0-1.0}]}
规则：
- 实体名取文中最正式的称呼；代词不作为实体，但它的同指别名要收进 aliases；
- relation 用简短谓语（隶属/持有/摧毁/杀死/象征/发动/约定…），不要长句；
- confidence：文中明确陈述 ≥0.9；强推断 0.6-0.8；模糊 ≤0.5 直接不输出；
- src/dst 必须出现在 entities 的 name 或 aliases 中；
- 没有可抽取内容时输出 {"entities":[],"relations":[]}。
文本：
<<<
{chunk_text}
>>>
```

## 附录 B：参考资料

- [microsoft/graphrag](https://github.com/microsoft/graphrag)（维护模式声明）｜ [Local Search 文档](https://microsoft.github.io/graphrag/query/local_search/)
- [HKUDS/LightRAG](https://github.com/HKUDS/LightRAG)（EMNLP2025：默认存储/增量删除/角色化模型/mix 模式）
- [OSU-NLP-Group/HippoRAG](https://github.com/OSU-NLP-Group/HippoRAG)（ICML'25：KG+PPR，index_manifest，多跳 SOTA）
- 本仓库：[RAG_SYSTEM_DESIGN.md](../RAG_SYSTEM_DESIGN.md)、`scripts/eval_rag_standard.py`（多跳评估）、`scripts/bilibili_lore_ingest.py`（幂等管线先例）
