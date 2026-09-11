# GraphRAG 收尾专项实施计划（G0 → R → P2 → A → P3 → P4 → O → M）

> 日期：2026-09-09（v2，已并入两份外部评审意见并逐条代码核验）
> 范围：仅 GraphRAG / 检索链路收尾与配套性能治理；
> 不含提示词 P1-1~P1-4、语音模块、前端重构等并行线。
> 前置状态：审计 P0/P1 修复已合入，全量测试 **562 passed / 1 skipped / 0 failed**。
> v2 变更：新增 **阶段 R（检索质量）**、**阶段 A（PPR 有向语义）**、**阶段 O（性能与资源）**；
> 驳回/降级 7 条评审建议（见 §1，含 4 条与代码事实不符者）。
> **v3 变更（第二轮全量复核）**：发现并修正 **2 个阻塞级方法缺陷**（B1 lore 孤证过滤可能让图谱检索形同虚设、
> B2 对话边被同一过滤全部丢弃）与 8 项实现层错误（B3–B10），详见 **§1.4**；
> 同步修订 §4（G0 增加证据分布门禁与检索烟雾测试）、§5（改写红线与去重取舍）、§6（P2 豁免/节流/悬空清理）、§12（新增 4 个配置）。
> **v4 变更（第三轮：业界先例调研）**：就 B1/B2「孤证边如何处理」检索了 HippoRAG 2 / Microsoft GraphRAG / LightRAG / BambooKG / G2ConS 等先例，**结论一致：主流框架都没有「证据条数 ≥ N 才保留」的硬阈值，一律是「保留 + 按计数加权衰减」**。据此 B1/B2 的解法从「开开关 + 打折」升级为 **「证据数驱动的连续衰减（权重化）」**，更彻底、且 `weak_edge_factor=0.0` 时严格等价于现状（零回归）。详见 **§1.5**。
> **v5 变更（第四轮：测试方法先例）**：新增 **§1.6 五层测试体系**（L0 等价性回归 / L1 参数消融 / L2 golden set / L3 reference-free + 人设一致性 / L4 门禁）。
> 关键先例：SubgraphRAG 的三档 **recall + ablation**、GTSQA 的 **ground-truth 子图标注**、Foundry 的 **Holes 指标**与「一次只改一个参数」、
> golden set 的 **git 版本化 + 0–3 分级 + shadow set**、以及「**探针集必须在调参前冻结**」这条防自欺红线。
> **v6 变更（第五轮：计划自身的结构性优化）**：v4/v5 连续增补后，计划出现了**方案与阶段表脱节**和**与自身旧版本矛盾**的问题。本轮修正：
> ① 新增 **阶段 W**（孤证边权重化 + L0/L1）——§1.5/§1.6 定义的一整套改动此前**没有任何阶段承接**；
> ② 修掉 §4.2 / §9.4 残留的 v3 旧结论（"置 `include_weak=True`"）与 v4 权重化方案的矛盾；
> ③ §12 补 `plot_weak_edge_factor`（此前遗漏，且默认值必须 0.5 才不改剧情层行为）+ 澄清"零回归到底靠什么保证"；
> ④ §3 补**工时口径**（L2/L3 的 1.5–2.5d 人工此前完全没排期）；
> ⑤ 新增 §1.6.4：把"人设一致性"、统计功效、绝对门槛这三处口号写成可执行条款。

---

## 0. 现状核对（实施前的事实基线）

| 事实 | 依据 | 影响 |
|---|---|---|
| lore 图谱**尚未构建**，无 `graph_wu_ming_zhe.json` | `ls data/knowledge/` | **G0 是 P2~P4 硬前置** |
| lore 语料 **2085 块**（另有 `lore_<cid>_spoken`） | 实测 | 评审一"927 块"为旧数据，本计划以 2085 为准 |
| 剧情图谱 **5026 实体 / 4261 边** | 实测 `plot_graph_wu_ming_zhe.json` | P3 社区检测规模合适；边结构含 `src/dst/relation/confidence/importance/evidence/ts/source` |
| 剧情图谱实体 `vec` 实为 `None`（未预计算） | 实测实体样本 | 评审二 D7"实体向量占内存"**不成立**，见 §1 |
| `graph_enabled=False`；`plot_graph_enabled=False` | `config.py:139/108` | 两套图谱均默认关闭，各阶段可零回归上线 |
| `top_k=2`，注释自认"检索无判别力" | `config.py:63` | 阶段 R 的核心动因 |
| 编排器**四路全用原始 `req.message`**，无查询改写 | `orchestrator.py` `_retrieve`（`grep rewrite` 零命中） | 口语/指代查询召回低 |
| 四路合并**无跨路去重**（`_filter_chunks` 只做低分过滤与相对门） | `persona_prompt.py:69`；`grep dedup` 零命中 | 同一 chunk 可能被向量路与图谱路重复注入 |
| `GraphStore._lock = threading.RLock()` | `graph_store.py:103` | 写路径必用 `asyncio.to_thread` |
| `_collect` 在 `self._lock` 内遍历全量块算余弦 | `vector_store.py:310-322` | 锁内 CPU，阻塞写入（评审二 D3 属实） |
| `_BM25.__init__` 保留 `self._docs`，建完索引后不再使用 | `vector_store.py:123-140` | 可直接释放（D2 属实，1 行改动） |
| `_run_async` 每次新建 `ThreadPoolExecutor(max_workers=1)` | `embedder.py:42` | 线程反复创建销毁（D6 属实） |
| 嵌入器**无结果缓存** | `embedder.py` `grep cache` 零命中 | 离线建库重复计算（D5 属实） |
| `GraphSearcher._evidence()` 按 `chunk_text_hash` 回查 KB，按 `kb.version` 失效 | `graph_search.py:152-183` | 对话事件天然可溯源；首次构建仍是全量扫描（A7 收益点） |
| `consolidate_entries` 返回 `int`，不返回 doc id | `memory_tier.py:91-127` | P2 需加 `return_ids` |
| `upsert_edge(source=...)` + `stats()["edges_conversation"]` 已就绪 | `graph_store.py:338/463` | P2 有现成埋点 |
| `session_memory` 已实现 `<sid>.summary.json` 增量历史摘要 | `session_memory.py:12/26/131` | 评审二 P5 建议**已实现**，无需再做 |
| PPR **强制无向化**（双向加边） | `graph_ppr.py:49-50`（§0 原记 47-48，行号已漂移） | 方向语义丢失（评审一 A6 属实） |
| ⚠️ 剧情图边数存在两个口径 | §0 实测 **4261**；`config.py:118-123` 注释写 **4302** | 注释为旧数据，**一律以实测为准**；注释里的"4289/4302 单证"仅作规律参考，比例（99.7%）仍有效 |

---

## 1. 外部评审裁定表（v2 新增，逐条代码核验）

### 1.1 评审一（架构与能力）

| 编号 | 建议 | 裁定 | 依据 |
|---|---|---|---|
| A1 | 补社区摘要 / global 查询 | ✅ **采纳** = 阶段 P3 | 与本计划原 P3 一致 |
| A2 | top_k 2→5 + cross-encoder 重排序 | ⚠️ **拆分**：top_k 提升 ✅ 采纳（阶段 R3，由 P4 裁决）；cross-encoder ⏸ **降级待评估** —— 需新增依赖且常驻 ~1GB 显存/内存，与"底显存"目标冲突，先做 R1/R2，若 P4 仍不达标再上 | `config.py:63`；无 reranker 依赖 |
| A3 | 查询改写 `_rewrite_query` | ✅ **采纳** = 阶段 R1（最高性价比） | 编排器确无改写 |
| A4 | 双图谱抽象统一，减 40% 重复代码 | ❌ **驳回（延后）** | 两层数据源（lore vs 转写）、语种、证据回查方式、默认参数差异大；且 **P4 尚未证明图谱有效**，此刻重构 ROI 为负、回归风险高。登记为遗留 |
| A5 | P2 对话增量写图 | ✅ **采纳** = 阶段 P2 | 原计划已含 |
| A6 | PPR 区分有向/无向关系 | ✅ **采纳** = 阶段 A（小项） | `graph_ppr.py:47` 确为无向；但无向化是"对称语义关联"的刻意设计，改为**按关系类型**保留方向，默认不变 |
| A7 | 证据倒排索引离线预建 | ✅ **采纳** = 阶段 O6 | 现有缓存按 `kb.version` 失效，首次与 KB 变更后仍全量扫 |

### 1.2 评审二（代码级与内存/显存）

| 编号 | 建议 | 裁定 | 依据 |
|---|---|---|---|
| D1 | 向量改 `array('f')` / `.npy` 分离 | ⚠️ **降级** = 阶段 O1，需带迁移方案 | 收益真实（~50MB），但改持久化格式 → 旧库兼容 + `fingerprint` 联动，风险高于收益排序，放在 R/P2 之后 |
| D2 | `_BM25` 建完索引释放 `_docs` | ✅ **采纳** = 阶段 O2（1 行） | `scores()` 只用 `_postings/_idf/_doc_len/_avgdl/_n` |
| D3 | `_collect` 移出锁 | ✅ **采纳** = 阶段 O3 | `vector_store.py:310` 锁内全量余弦 |
| D4 | BM25 缓存按命名空间清 | ✅ **采纳**（并入 O3，低优先） | 全清策略在增量写入后重建代价高 |
| D5 | 嵌入结果磁盘缓存 | ✅ **采纳** = 阶段 O5 | 离线建库重复文本多，收益最大 |
| D6 | 共享线程池替代每次新建 | ✅ **采纳** = 阶段 O4 | `embedder.py:42` |
| D7 | 实体向量不预存以省内存 | ❌ **驳回** | 实测剧情图谱实体 `vec=None`，**本就未预计算**；`ensure_entity_vectors` 已是按需懒算。改为实时算反而更慢 |
| D8 | `remove_by_doc` 倒排索引 | ✅ **采纳**（并入 M 漂移巡检） | O(E) 遍历，4261 边可接受但应留索引位 |
| D9 | 四路应用改写后查询 | ✅ **采纳** = R1 | 同 A3 |
| D10 | 跨路结果去重 | ✅ **采纳** = R2（保留来源标签、高分优先） | 合并处无去重 |
| D11 | `consolidate` 与 `consolidate_entries` 重复执行 | ❌ **驳回（评审错误）** | `orchestrator.py:792-802` 是 **if/else**：entries 非空走结构化写入，为空才回退整段合并，不存在双写 |
| D12 | `prune` 从未被编排器调用 | ❌ **驳回（评审错误）** | `orchestrator.py:807` 每轮 consolidate 后已调用 `self._memory_tier.prune(...)` |
| D13 | `PlotCorpus` 改懒加载 | ⚠️ **降级为不做** | `PlotCorpus` 只在 `plot_graph.py:524` 的 registry 内构造，**剧情层默认关闭时根本不加载**；收益 ≤10MB，复杂度不划算 |
| D14 | `top_k` 默认值偏小 | ✅ **采纳**（与 R1 绑定） | 同 A2 |
| P0 | 嵌入换 `bge-small-**en**` + Q4 量化 | ❌ **驳回（有害建议）** | ① **en 模型用于中文剧情语料会显著降召回**；② 换嵌入 = `fingerprint` 失效 + 2085 块 KB 全量重建 + 既有评测基线全部作废。若将来换，只能是 `bge-m3` / `gte-Qwen2-7B-instruct` 等中文多语言模型，且**必须走 P4 A/B**。其中 `keep_alive` 缩短与在线/离线批量分级 ✅ 采纳（O7/O8，零风险） |
| P1 | 内存组合优化 | ⚠️ **部分采纳** | D2/D3 真实可用；D7 已证伪，实际节省远小于宣称的 ~110MB |
| P3 | LLM 共享实例 + 抽取用小模型 + max_tokens 800→256 | ⚠️ **部分采纳** | 共享实例 ✅（O9，需确认线程安全）；max_tokens 改 512 更稳妥（先测）；抽取小模型 ⏸ 待评估（质量风险） |
| P4 | 冷热分层存储 | ⏸ **延后** | 2085 块规模下无收益，>1 万块再议 |
| P5 | 会话历史压缩 | ❌ **驳回（已实现）** | `session_memory.py` 已有 `<sid>.summary.json` 增量摘要 |

### 1.3 裁定统计
- 采纳 15 条 · 降级 5 条 · 驳回 8 条（含 4 条事实错误/有害建议）
- 评审一数据口径更正：lore 语料 **2085 块**（非 927 块）

---

## 1.4 第二轮全量复核：方法缺陷清单（v3 修正，阻塞项优先）

> 全量通读 `orchestrator / persona_prompt / graph_search / graph_store / build_graph /
> vector_store / memory_tier / config / factory` 后复核，发现**原计划有 2 个会让后续阶段
> 直接失效的阻塞级问题**，以及 6 个实现层面的方法错误。以下修正已并入 §4–§6 与 §12。

### 🔴 B1（阻塞）`graph_include_weak=False` 很可能让 lore 图谱检索形同虚设

**证据链**
- `GraphSearcher.retrieve`（`graph_search.py:217`）：`if not self.include_weak and len(evidence) < 2: continue` —— 孤证边**直接丢弃**；
- 剧情层的实测结论（`config.py:118-123` 注释）：4302 条边里 **4289 条只有 1 条证据（99.7%）**，因为"每块独立抽取、同一关系在不同块里谓语措辞略有差异，几乎无法自然累积到 2 条"；
- 剧情层因此把 `plot_include_weak` 默认改为 **True**，并给孤证边 `score *= 0.5` 降权（`plot_graph.py:389-401`）；
- 而 `config.py:146` 给 lore 层写的是 `graph_include_weak: bool = False  # lore 层证据较密` —— **这是未经验证的假设，与剧情层实测规律相反**；且 lore 检索器**没有** 0.5 折降权这条退路。

**后果**：若不改，G0 的 stats 会很漂亮（实体/边达标），但 P4 测的是一个几乎不返回结果的死特性，整套 A/B 结论作废。

**根因补充（v4）**：除"措辞差异"外还有**结构性原因**——`graph_store.py:375` 的合并键是
`(src, dst, relation)` 三元组，**方向与谓语都敏感**；而 PPR 传播本身却是无向化的
（`graph_ppr.py:49-50`）。即"甲→乙 认识"与"乙→甲 同伴"在传播时是同一条边，计数时却是两条，永远攒不到 2。
（对标：LightRAG 的合并键是 `tuple(sorted([src, dst]))`，方向无关。）

**修正（已并入 §4；v4 升级为权重化方案，见 §1.5 修正 1/2）**
1. G0 增加**证据分布门禁**：构建后统计 `≥2 条证据的边 / 总边数`；
2. **主改动**：把 `graph_ppr.py:40-41` 的「`n < 2` 直接 `continue`」改为
   **「`w = confidence × importance × (weak_edge_factor if n < 2 else 1.0)`」**——单证边**保留但传不远**，
   而不是删除。`graph_weak_edge_factor` 默认 0.35（剧情层沿用 0.5 折语义）；
   `include_weak=False` 退化为 `weak_edge_factor=0.0` 的兼容别名，**行为与现状逐位相同**；
3. 可选补丁 §1.5 修正 2：查询时按**无序实体对**聚合证据数（默认关闭，G0 实测后再定）；
4. G0 增加**检索烟雾测试**：≥10 条代表性查询经 `GraphSearcher.retrieve`，非空率 ≥60%；不达标不得进 P4；
5. 空结果**计数器**（不回退、不改其它路）→ P4 判断图谱路是否活着（MS GraphRAG 排障先例）。

### 🔴 B2（阻塞）P2 的对话边会被同一道孤证过滤全部丢弃

- 对话三元组天然只有 1 条证据 → 在 `include_weak=False` 下**永远不会被检索到**，P2 做完等于没做。
- **修正（v4）**：§1.5 修正 1 的权重化方案**自动解决** B2——对话边不再被删，只是按 `weak_edge_factor` 衰减。
  对话边时效性强、噪声低于抽取噪声，因此给独立档 `graph_conversation_weak_edge_factor=0.6`（高于 lore 的 0.35）。
  原 `graph_conversation_include_weak` **降级为可选兼容开关**（仍可强制全丢弃），不再是 P2 的必要前提。

### 🟠 B3 查询改写：拿不到历史 + 有污染生成输入的风险

- `_gather_context`（`orchestrator.py:335`）在会话锁**之外**执行，历史是 `run()/stream()` 加锁后才用 `get_history` 取的 —— `_gather_context` **手上没有 history**。
- **修正**：在 `_gather_context` 内 `await asyncio.to_thread(self._session_memory.get_history, sid)` 取最近 3 轮（避免锁内/事件循环内同步 IO）。
- **红线**：改写结果**只喂检索**，绝不能替换 `req.message` —— 生成（`_gen`）与情感检测仍需用户原句，否则把用户的"那后来呢？"换成别的句子，回复会文不对题。
- mock provider 下改写返回固定串 → 测试必须注入 stub LLM，并断言"改写关闭时不发生额外 LLM 调用"。

### 🟠 B4 跨路去重不能"保留分数更高者"

- 两路量纲不可比：向量路经混合重排后 top1≈1.0；图谱路 = PPR×confidence，实测量级 0.01~0.2。
- **修正**：同文本时**保留图谱块（带「关系」行、信息更全），从 lore 向量列表移除**；且**仅在 `graph_enabled` 为真时执行**（默认关闭 → 零回归）。

### 🟠 B5 P2 写盘会让在线检索器反复重建

- `GraphSearchRegistry.get()`（`:307-337`）按 **mtime** 缓存；每次 `save()` 都改 mtime → 下一个请求重建 `GraphSearcher`，重新解析图谱 JSON 并用 `list_items` 重建证据索引。
- **修正**：写盘节流 `graph_conversation_flush_min_interval=60`（或会话结束才 flush）；flush 时顺带 `ensure_entity_vectors`——**新实体无 vec 时只能靠精确匹配链接**（`_link_vector` 过滤 `if e.get("vec")`）。

### 🟠 B6 KB prune 会让对话边证据悬空

- `LongTermMemory.prune`（`memory_tier.py:155`）删除 events 条目 → 图谱 evidence 的 hash 回查不到 → 该边静默不产出块（`retrieve` 已 skip）。
- **修正**：接受悬空（不报错），但 flush 时清理"证据全部失效"的边，避免边数虚高；写入时给对话边足够的 `importance`，降低被 prune 概率。

### 🟡 B7 `--rebuild` 会删文件，`--build` 不会

- `build_graph.py:145-148`：`--rebuild` 先 `cache.clear()` 再 `gpath.unlink()`；`--build` 是增量、保留已有边。
- **修正**：`--preserve-conversation` 只需覆盖 `--rebuild` 分支（原计划结论正确，此处补全实现位置）。

### 🟡 B8 G0 抽取并发与超时

- `graph_extract_batch=8` + `graph_extract_timeout=60s`；而剧情层实测本地 7B 在 8 并发下会把单块推过 60s（`config.py:131-133`）。
- **修正**：先 `--limit 50` 实测单块耗时与失败率再定 batch（建议 4）；新增验收"抽取失败率 <10%"。

### 🟡 B9 / B10
- `build_graph.py:187` 已在构建末尾调用 `ensure_entity_vectors` → G0 后实体向量可用；P2 新增实体需自行补算（见 B5）。
- 长期记忆走 `memory_tier.retrieve`（`orchestrator.py:638`），是**独立于 lore 的分支** → 改写后的 query 必须同时透传给这一路，否则记忆侧仍被指代问题困扰。

---

## 1.5 第三轮：业界先例调研（v4，专攻 B1/B2「孤证边怎么处理」）

> 问题表述：本项目用 `len(evidence) >= 2` 的**硬阈值**在建图/检索时丢边（`graph_ppr.py:40-41`、
> `graph_search.py:217`），实测剧情层 99.7% 的边只有 1 条证据。这种"单证据边"业界怎么处理？

### 1.5.1 先例汇总

| 来源 | 边权重怎么定 | 是否过滤单证边 | 对本项目的直接启示 |
|---|---|---|---|
| **HippoRAG 2**（OSU，arXiv 2502.14802，PPR 系直接对标） | 关系边 `w = 1`（每三元组一条边，**不做计数**）；同义边 `w = cos_sim`（τ=0.8）；上下文边 `w = 1` | **不过滤**。噪声交给**在线 LLM「识别记忆」过滤器**在检索时处理 | ① 单证边本来就合法；② 去噪应在**查询时**做（我们的 `confidence` 即等价物），不是建图时 |
| **Microsoft GraphRAG** | `weight = 共现计数`，跨 chunk **求和**，初值 1/次。早期版本让 LLM 直接打关系强度分，因主观性太强**被废弃**，改用客观计数 | **无最小证据阈值**；权重喂给 Leiden 社区检测 + Local/DRIFT 检索 | ① 计数应**喂给算法当权重**，而不是当开关；② P3 社区检测天然消费 `len(evidence)` |
| **LightRAG**（HKU） | 合并键 `tuple(sorted([src, dst]))` —— **方向无关**；`weight` 累加、`source_id` 取并集；重排 = 语义分 + 度中心性 + 关系置信度 + chunk 命中密度 | 不过滤 | 我们的键是 `(src, dst, relation)`（方向+谓语双敏感），这是证据攒不到 2 的**结构性原因** |
| **BambooKG**（Hebbian 频率加权） | 同块标签两两连无向边，`w += 1`，无三元组约束 | 不过滤 | 纯频率即可，无需强三元组结构 |
| **G2ConS**（arXiv 2510.24120） | 建边需同时满足 `cos ≥ θ_sem` **且** `Co ≥ θ_co`，权重用 **Dice 系数** `2·Co / (|T_i| + |T_j|)`；明确指出"纯共现 + BFS 会引入虚假相关" | 阈值是**语义+共现联合**的，不是共现单条件 | 我们的 `confidence` 就是语义项；**按证据数加权必须做 hub 归一化**，否则高频实体靠一堆单证边刷分 |
| 工程实现（NestJS + Neo4j GraphRAG） | `ON CREATE SET weight=1` / `ON MATCH SET weight += 1`；删除 chunk 时 `weight -= 1`，**归零则 `DETACH DELETE`** | — | 正是 B6 需要的；`graph_store.drop_source()`（`:427-446`）**已具备该能力**，只差接到 `memory_tier.prune()` |
| MS GraphRAG 排障笔记 | 已知症状「Graph has far fewer edges than expected / queries return sparse results」；建议「图遍历结果 < K 时**回退到纯向量检索**」 | — | G0 检索烟雾测试 + 空结果观测，是标准动作，不是我们臆造 |
| ml-digest KG-RAG 实践指南 | 「低置信关系应在**查询时**过滤，而不是建图时」；「始终保留一个纯 RAG 基线，才能证明图真的有用」；「图展开要有界、可观测」 | — | 与本计划 `graph_enabled=False` 默认关闭的零回归策略一致 |

**一句话结论**：**没有任何一个主流框架用「证据条数 ≥ N」的硬阈值丢边**；统一做法是
**全部保留 + 计数即权重 + 查询时衰减**。本项目的 `WEAK_EVIDENCE_MIN=2` 硬阈值属于自创且无先例，
而剧情层已经用实测数据（99.7%）打过它的脸。

### 1.5.2 由先例反推出的三项修正

#### ✅ 修正 1【B1/B2 的根本解法】把「硬阈值丢边」改成「证据数驱动的连续衰减」

`graph_ppr.py` 现在：

```python
# 现状（:40-44）
if not include_weak and len(e.get("evidence") or []) < WEAK_EVIDENCE_MIN:
    continue
w = float(e.get("confidence", 0.0)) * float(e.get("importance", 0.7))
```

PPR **本来就有转移权重**，只是没把证据条数放进去。改为：

```python
n = len(e.get("evidence") or [])
if n <= 0:
    continue                                   # 零证据边无来源，仍丢弃（唯一保留的硬过滤）
w = float(e.get("confidence", 0.0)) * float(e.get("importance", 0.7))
if n < WEAK_EVIDENCE_MIN:
    w *= weak_edge_factor                      # 连续衰减，不再删除
if w <= 0:
    continue
```

- 新增参数 `weak_edge_factor`（`personalized_pagerank` / `hop_distance` 都要加，
  **两者口径必须一致**，否则又会出现"有跳距但零 PPR 分"的节点）；
- `graph_weak_edge_factor = 0.35`（lore 默认）、`graph_conversation_weak_edge_factor = 0.6`（对话边，时效性高、噪声低）；
- **零回归保证**：`include_weak=False` ≡ `weak_edge_factor=0.0`，行为逐位等价；`include_weak=True` ≡ `1.0`。
  旧字段保留为兼容别名，内部先归一成 factor 再计算；
- 效果：图不再被削掉 99.7% 的边，单证边**参与传播但传不远** —— 同时满足
  HippoRAG 2「保留 + 查询时过滤」与 MS GraphRAG「计数即权重」两条先例。

#### ✅ 修正 2【B1 的结构性补丁，可选、无数据迁移】查询时按「无序实体对」聚合证据数

LightRAG 用 `tuple(sorted([src, dst]))` 说明业界认为 A→B 与 B→A 是同一条关系的两个视角。
本项目 PPR **传播是无向的**（`:49-50`），**计数却是有向的** —— 这是内部不一致。

不改存储，只在 PPR 入口做一次 `frozenset((src, dst))` 分组，
取组内 `len(evidence)` 的**最大值**作为衰减依据（取最大值而非求和，避免把同一关系重复计数放大权重）：

```python
pair_ev = {}
for e in edges:
    k = frozenset((str(e.get("src")), str(e.get("dst"))))
    pair_ev[k] = max(pair_ev.get(k, 0), len(e.get("evidence") or []))
```

- 新配置 `graph_undirected_evidence: bool = False`（默认关，零回归）；
- G0 实测：开启前后对比「≥2 证据边占比」与检索非空率，再决定是否默认打开；
- 只影响**衰减档位的选择**，不改变边的存在性，因此风险可控。

#### ✅ 修正 3【空结果可观测，MS GraphRAG 排障先例】

`GraphSearcher.retrieve` 返回空时 `_gather_context` 记一次 `graph_empty_total += 1`（不改其它路行为，
**不做自动回退** —— 自动回退会让 P4 的 A/B 失去判别力）。P4 报告中该指标与查询总数并列输出；
10 条查询非空率 <60% → G0 判不通过。

#### 修正 1/2/3 的落地文件清单

| 文件 | 改动 |
|---|---|
| `core/knowledge/graph_ppr.py` | `personalized_pagerank` / `hop_distance` 同步新增 `weak_edge_factor: float = 1.0`；删掉 `include_weak` 的 `continue`，改为权重衰减；可选 `undirected_evidence: bool = False`；`WEAK_EVIDENCE_MIN` 语义不变，仅作**档位分界** |
| `core/knowledge/graph_search.py` | `:217` 的硬过滤同样改为衰减；新增 `graph_weak_edge_factor` / `graph_conversation_weak_edge_factor` 读取；空结果时置 `self._stats["empty"] += 1` |
| `core/knowledge/plot_graph.py` | 复用同一衰减参数替换 `plot_graph.py:389-401` 的硬编码 `0.5`，**保证剧情层行为不变**（`plot_weak_edge_factor=0.5`，与现值一致） |
| `core/orchestrator.py` | `_gather_context` 读取图谱路空结果计数，累加到 P4 指标 |
| `config.py` | 新增 3 个配置项（见 §12），`include_weak` 系列字段保留为兼容别名 |

**回归要求**：`weak_edge_factor=0.0` 时必须与改动前**逐位相同**，这是新增测试的硬性断言
（用同一份图谱 JSON + 同一组 seeds，对比改动前后 `pagerank` 输出字典完全相等）。

### 1.5.3 先例**不支持**、因此明确不做的两件事

1. **不做 LLM 关系强度打分**：MS GraphRAG 早期试过，因"评估标准主观"已废弃，改回计数。我们的 `confidence`
   是抽取时的一次性判断，不是独立的强度打分调用，保留即可。
2. **不加 HippoRAG 2 式的在线 LLM 三元组过滤器**（recognition memory）：它要求**每次查询多一次 LLM 调用**，
   本地 7B 下延迟不可接受；且我们的 `confidence` + `weak_edge_factor` 已承担"查询时去噪"这一角色，
   属于同一职责的廉价实现。

### 1.5.4 存量代码里"意外对齐先例"的地方（无需改动，登记备查）

- `graph_store.drop_source(ns, doc_id)`（`:427-446`）：证据全失效则删边 —— 与 NestJS 实现的 `weight -= 1 / 归零删除` 同构。B6 只需**接线**，不需新写。
- P3 社区检测：消费 `len(evidence)` 作为边权 —— 与 MS GraphRAG 的用法一致。
  ⚠️ **v6 措辞修正**：P3 用的是**无向化连通分量 + 标签传播**（零依赖，见 §8.1），**不是 Leiden**。
  而**连通分量本身不消费边权**（无权算法）——因此 `len(evidence)` 实际只在**标签传播细分**阶段生效。
  这条若不加说明，容易让人以为已实现 Leiden 级别的加权社区发现。
- `graph_enabled=False` / `plot_graph_enabled=False` 默认关闭 —— 与 ml-digest「保留纯 RAG 基线」一致。

---

## 1.6 第四轮：测试方法先例（v5，怎么证明改动有效且不退化）

> 承接 §1.5：方案改对了，还得**证明**它对。尤其 `weak_edge_factor` 是个连续参数，
> 调大召回高、噪声也大，"跑一下感觉还行"必然自我欺骗。以下先例全部来自检索/GraphRAG 的评测实践。

### 1.6.1 先例汇总

| 来源 | 测试方法 | 可直接抄的部分 |
|---|---|---|
| **SubgraphRAG**（arXiv 2410.20724） | 三档 **recall** 指标：① 最短路径三元组召回 ② **LLM 标注的相关三元组召回** ③ **答案实体召回**；外加 wall-clock；最后做 **ablation study** 拆各组件贡献 | 我们的 L2 指标骨架：**实体召回 + 三元组召回 + 耗时 + 消融** |
| **GTSQA**（arXiv 2511.04473） | 专门构造 **ground-truth 子图（Ground-Truth Subgraphs）** 作为评测基准，指出 path-based 检索器召回的子图偏小 | 标注对象应是**实体/三元组集合**，不是 chunk 文本（chunk 会重写，实体名稳定） |
| **RAGAS**（通用标准） | Faithfulness / Answer Relevancy / Context Precision / Context Recall（LLM-as-judge） | §9 已在用；但**后两者需要 ground truth**，我们没有 |
| **Microsoft Foundry 检索评测** | 有标注用 nDCG / Fidelity / **Holes**；无标注用 LLM-judge 1–5。**Holes = 检索到但没被标注的 ID 占比**，高则 nDCG 不可信 | 把 **Holes** 引进来当"标注覆盖度自检"——这正是我们最容易忽略的 |
| **A/B 方法论**（AI-300 检索调优） | **一次只改一个检索参数**，冻结 generator / prompt / temperature；在**冻结的**标注集上打分；**保留对照臂与回滚 tag**；不要 100% 生产切流、留 holdout | 写进 §9.2 的硬约束 |
| **Golden query set 实践**（qaskills） | golden 文件 **git 版本化 + 打 baseline tag**；分级标注 0–3（3=必排顶部，0=无关）；双标注算 Cohen's kappa；**标注分歧大的查询隔离进 shadow set，不参与 CI 门禁**；查询来源要含"历史上零命中"的用例 | 探针集的文件格式、分级口径、shadow set 机制 |
| **生产 RAG 评测**（Gems of Coding） | golden set 是**回归套件**——任何 chunker / embedding / 阈值改动不跑它不许上线；**合成查询要人工抽检**（合成问题比真实输入"过于规范"）；**reference-free 指标**（nugget 分解、幻觉打分、重复运行一致性）绕开 ground truth 瓶颈 | 我们角色扮演**没有标准答案**，必须走 reference-free 路线 |
| **Braintrust / Open RAG Eval** | 起步 golden set **30–50 条**即可；必须含 4 类：事实型 / 多文档综合 / 歧义 / **"信息不存在"** | 探针集的最小构成 |
| **Briefcase 自动标注流水线** | 用标注 agent 给 query–doc 对打相关性分 → 算 NDCG / recall@k / MRR；**label 缓存复用**（同一对只标一次） | 低成本扩标注的办法 |

### 1.6.2 本项目落地：**五层测试体系**

> 关键约束：**lore 图谱还没建**（`graph_wu_ming_zhe.json` 不存在），所以 L2/L3 现在做不了。
> L0/L1 不依赖图谱内容，**G0 前就能写**；L2/L3 必须等图谱建完，且**探针集要在调参之前冻结**。

#### L0 — 单元与等价性回归（不需要 ground truth，现在就能写）

| 用例 | 断言 |
|---|---|
| **等价性（最重要）** | 同一份图谱 + 同一组 seeds，`weak_edge_factor=0.0` 的输出字典与改动前 `include_weak=False` 的输出**逐位相等** —— 这是零回归的硬保证 |
| **确定性** | 同一输入连续跑 2 次，PPR 输出完全一致（项目已有先例：`graph_store.py:361-362` 为可复现性特意把 set 换成有序 list） |
| **口径一致** | `personalized_pagerank` 与 `hop_distance` 在相同 factor 下**过滤出的边集相同**（否则出现"有跳距但零 PPR 分"） |
| **边界** | 0 证据边必丢弃；全单证图；空 seeds；孤立节点；`confidence=0`；`factor=0` 且全单证 → 返回 seeds 原样 |
| **单调性** | factor 递增时，单证边端点的 PPR 分**单调不减**（防止符号写反） |

#### L1 — 参数扫描 / 消融（SubgraphRAG + Foundry 的 parameter sweep 范式）

- 网格：`weak_edge_factor ∈ {0.0, 0.2, 0.35, 0.6, 1.0}` × `undirected_evidence ∈ {False, True}`，**其余全部冻结**
  （generator、prompt、temperature、top_k、图谱文件、种子查询集）。
- 每条记录：非空率 / 平均命中边数 / 平均证据块数 / 单证边贡献占比 / P95 延迟 / PPR 迭代次数。
- **一次只动一个变量**；结果写成 JSON 进 `deliverables/`，不允许"看着差不多就定"。
- 判据：**无关查询误召率不得随 factor 单调爆炸**——G2ConS 已证明纯共现会引入虚假相关，factor=1.0 大概率是噪声上限。

#### L2 — 检索质量 golden set（图谱建完后）

`tests/fixtures/graph_probe_set.json`，**git 版本化，打 `probe@YYYY-MM-DD` tag**：

```json
{ "version": "2026-09-09", "k": 10, "queries": [
  { "id": "q-001", "text": "无名者和维尔汀是什么关系",
    "type": "multi-hop",
    "expected_entities": ["无名者", "维尔汀"],
    "expected_relations": [["无名者","维尔汀"]],
    "grades": { "ent:无名者": 3, "ent:维尔汀": 3 } } ] }
```

- **规模**：先 30–50 条（Braintrust 起步建议），够用再扩到 200。
- **四类必含**：单跳事实 / 多跳关联 / **无关干扰**（测误召，最容易暴露 factor 过大）/ **指代省略**（"那后来呢？"，测 R1 改写）。
  另加 qaskills 建议的**"历史零命中"**用例。
- **标注粒度**：标**实体/关系**，不标 chunk 文本（GTSQA 教训 + chunk 会重写）。
- **指标**：实体召回（对标 SubgraphRAG 的 answer entity recall）、关系召回、**NDCG@k**、MRR、Precision@k、
  以及 **Holes**（检索到但未标注的实体占比 → 标注没覆盖就别信 NDCG）。
- **一致性**：双标注算 Cohen's kappa；分歧大的进 **shadow set**，只观测、**不进 CI 门禁**。
- **防作弊红线**：探针集**必须在调参前冻结并 commit**。先例明确警告小规模 golden set
  "Easy to cherry-pick queries that favor one method" —— 边调参边加查询 = 自我欺骗。

#### L3 — 端到端（reference-free，因为角色扮演没有标准答案）

- 用得上：Faithfulness（是否编造）、Answer Relevancy（是否答非所问）—— **这两个不需要 ground truth**。
- 用不上：Context Recall / Context Precision 需要 ground truth → 降级为 **L2 的实体召回** 替代。
- **领域专属指标（先例没有，我们必须自建）**：**人设一致性** —— LLM judge 判"回复是否符合角色卡设定"。
  这是角色扮演场景的核心风险：图谱注入更多上下文后，角色可能**变得更啰嗦或泄露世界观外的信息**。
- **人工盲评**：A/B 两版回复**随机打乱顺序**成对给评，避免位置偏差；评"是否符合人设 / 是否更贴合提问"。
- **稳定性**：同一查询 `--repeat 3`，统计输出方差（reference-free 的 consistency 指标）。

#### L4 — 护栏与门禁

| 门禁 | 内容 |
|---|---|
| 全量 pytest | 维持 **562 passed / 1 skipped / 0 failed**，新增用例只能加不能减 |
| 性能 | P95 延迟、PPR 迭代次数、峰值内存（图谱路开启前后对比） |
| 观测 | `GraphSearcher` 计数器：实体链接命中/未命中、参与 PPR 的边数、**被衰减的边数**、空结果次数（§1.5 修正 3） |
| 上线 | 保留对照臂与回滚 tag；**留 holdout，不 100% 切流**（AI-300 明确要求） |

### 1.6.3 对 §9（P4）的补充约束

1. A/B **一次只改一个变量**，generator / prompt / temperature 冻结；
2. 探针集与 `weak_edge_factor` 的最优值**在不同阶段确定**：先冻结探针集 → 再跑 L1 扫描 → 定 factor → 最后才跑 L3 A/B；
3. 报告中必须同时给出 **Holes** 与**无关查询误召率**，否则 nDCG 与"非空率提升"都可能是假象；
4. 新增判据：**人设一致性不降**（Δ ≥ -0.03）——这是角色扮演区别于通用 RAG 的独有红线。

### 1.6.4 三处最容易"写成口号、执行时架空"的地方（v6 补全）

#### ① L3「人设一致性」必须可执行化，否则等于没写

§1.6 L3 说"LLM judge 判是否符合角色卡设定"，但没给 judge 是谁、怎么打分。**必须补齐**：

| 项 | 规定 |
|---|---|
| judge 模型 | **不得用生成回复的同一个本地 7B**。LLM-as-judge 有公认的 **self-enhancement bias**（偏好自己/同源模型的输出）。<br>可选方案：① 用云端大模型（GPT-4o-mini 级别）做 judge，只评不改；② 用**另一个不同家族**的本地模型；③ **以人工盲评为主、LLM 打分为辅**（推荐，成本可控） |
| 评分维度（每项 1–5） | ① 称谓与自称是否符合角色卡 ② 是否泄露角色不应知道的信息 ③ 口吻/用词是否符合设定 ④ **是否因图谱注入而变得啰嗦或百科全书化** |
| 抽样量 | 每条探针 `--repeat 3` 取均值；人工盲评至少 **30 对**（A/B 随机打乱顺序，双评，算一致率） |
| 阈值 | 四项均值 Δ ≥ -0.03；**单项不得出现 ≥0.1 的下降**（尤其"泄露不应知道的信息"这一项，出现即判不通过） |

#### ② 30–50 条探针**做不了多变量析因**，别把 top_k 塞进同一套 A/B

§9.1 第 3 条写"R3 裁决：同一套 A/B 增加 `top_k=2 vs 4`（叠加 R1/R2）对照"——
这与 §1.6.3 的"一次只改一个变量"**直接冲突**。析因设计需要 2×2×2=8 个组合，
30–50 条查询摊到每组只剩个位数，**统计功效严重不足**，结论基本是噪声。

**修正**：`top_k` 作为**独立的第三臂**单独跑（基线 / +图谱 / +top_k4），
不做交叉；若一定要析因，先把探针集扩到 **200 条以上**并说明功效计算。

#### ③ P4 判据只有相对提升，会被低基线放大

"multi-hop 相对基线提升 ≥15%" —— 若基线 multi-hop 得分只有 0.20，提升 15% 是 0.23，
**绝对意义上仍然很差**。必须补**绝对门槛**：

| 指标 | 相对判据 | **绝对门槛（必须同时满足）** |
|---|---|---|
| multi-hop 忠实度 | ≥ +15% | **≥ 0.70** |
| Faithfulness（整体） | Δ ≥ -0.03 | **≥ 0.80** |
| 人设一致性 | Δ ≥ -0.03 | **≥ 4.0 / 5** |
| 无关查询误召率 | 不升 | **≤ 10%** |

---

## 2. 目标与非目标

**目标**
1. lore 图谱真正构建并通过抽检（G0）。
2. 修复"口语/指代查询召回低"这一**最廉价的质量缺口**（R）。
3. 让长期记忆升级为可多跳、可回溯的关系记忆（P2 + A）。
4. 让宏观/总结型问题有解（P3）。
5. 用 A/B 数据决定图谱与检索参数是否启用，而不是拍脑袋（P4）。
6. 在不改变行为的前提下回收内存/显存（O）。

**非目标（明确不做）**
- ❌ 不换嵌入模型（`bge-small-en` 尤禁）；换模型必须走 P4 A/B。
- ❌ 不做双图谱抽象统一重构（A4）。
- ❌ 不引入 LightRAG sidecar / Leiden / faiss 等新依赖（P3、P4 结论后再评估）。
- ❌ 不做图谱可视化 UI、不改分块策略与语料内容。

---

## 3. 阶段总览与依赖

| 阶段 | 名称 | 依赖 | 耗时 | 独立上线 |
|---|---|---|---|---|
| **W** | **孤证边权重化 + L0/L1 测试**（v6 新增，见 §3.1） | **无** | 0.5d + L1 扫描 0.5d | ✅ |
| **G0** | lore 图谱全量构建 + 抽检 | 无 | 机器 1~2.5h / 人工 0.5d | ✅ |
| **R** | 检索质量：查询改写 + 跨路去重 + top_k 实验 | 无 | 1d | ✅（新开关默认 False） |
| **P2** | 对话三元组增量写图 + 时间线 | G0（建议） | 1.5d | ✅ |
| **A** | PPR 有向语义（关系类型分级） | G0 | 0.5d | ✅ |
| **P3** | 社区摘要 + 全局路由 | G0 | 2d | ✅ |
| **P4** | A/B 评估 + 观测指标（裁决 R/P2/A/P3） | G0 | 1.5d | ✅ |
| **O** | 性能与资源治理 | 无 | 1d | ✅ |
| **M** | 工程卫生 + 漂移巡检 + 文档同步 | 无 | 0.5d | ✅ |

**推荐顺序（v6 修订）**：
```
W1（L0 测试先行，纯合成小图）
  → 并行：G0 后台构建 ‖ R（检索质量，与图谱无关）
  → W2~W4（权重化改造 + 计数器）
  → P4 采基线（此时冻结探针集 v1）
  → W5（L1 参数扫描，定 weak_edge_factor）
  → P2 → A → P3
  → P4 A/B 复跑（L3）→ O → M
```

理由：
- **W1 必须最先**：`graph_ppr.py` 一改就无法再采集"改动前"的行为基线，L0 等价性用例是唯一能锁住零回归的东西。
- W 与 R 都**不依赖真实图谱**，可以和 G0 的机器时间完全并行，是等待期最该做的事。
- P4 基线要在 W5 之前采，否则基线里已经混入了权重化的影响。
- L1 扫描（W5）需要真实图谱，所以排在 G0 之后。

**⚠️ 工时口径说明（v6 补）：上表的"耗时"是纯工程工时，不含标注与评测的人工成本。**
v5 引入 L2/L3 后新增了三块**显著且容易被漏算**的开销，应单独排期：

| 新增工作 | 估算 | 说明 |
|---|---|---|
| L2 探针集构建与标注 | **0.5–1d** | 30–50 条查询 × 双标注 + Cohen's kappa 计算 + shadow set 隔离；**不可压缩**，压缩就等于放弃判别力 |
| L1 扫描执行与选档 | 0.5d | 10 组配置，跑批时间取决于图谱规模 |
| L3 人工盲评 | **0.5–1d** | ≥30 对 × 双评；这是唯一能兜住"人设一致性"的手段，不能用 LLM judge 完全替代 |

合计约 **1.5–2.5d 额外人工**，需在项目排期中显式体现，否则会出现"代码做完了但结论出不来"。

---

## 3.1 阶段 W：孤证边权重化 + L0/L1 测试（v6 新增）

> **为什么单列**：v4/v5 在 §1.5/§1.6 定义了一整套改动（改 `graph_ppr.py` / `graph_search.py` /
> `plot_graph.py` / `orchestrator.py` / `config.py`），但 §3 的八个阶段**没有任何一个承接它们**。
> 这是纯文档遗漏，不改会导致"方案定了但没人知道什么时候做"。补此阶段。

### W1 — L0 等价性测试先行（不改任何产品代码）

用**合成小图**（10 来条边、手工指定 evidence 条数），落在 `tests/test_graph_ppr_weighting.py`。
**必须包含**：等价性（`factor=0.0` ≡ 旧 `include_weak=False`，逐位相等）、确定性、口径一致
（`pagerank` 与 `hop_distance` 过滤出的边集相同）、边界、单调性。详见 §1.6 L0。

**验收**：全红或全绿无意义——要求在不改动 `graph_ppr.py` 的前提下，用旧的 `include_weak` 参数跑出**全绿**，
证明这套断言确实锁住了现状；然后再动产品代码。

### W2 — PPR 权重化

`graph_ppr.py`：`personalized_pagerank` / `hop_distance` 同步加 `weak_edge_factor`、`undirected_evidence`。
`include_weak` 保留为兼容别名（内部归一成 factor）。

### W3 — 检索器与剧情层对齐

- `graph_search.py:217` 硬过滤改衰减；新增空结果计数器。
- `plot_graph.py:389-401` 硬编码 `0.5` 换成 `plot_weak_edge_factor`（**默认必须是 0.5**，见 §12 澄清块）。

### W4 — 观测计数器

`orchestrator._gather_context` 读取图谱路空结果次数，累加进 P4 指标（§1.5 修正 3）。

### W5 — L1 参数扫描（依赖 G0）

`weak_edge_factor ∈ {0.0, 0.2, 0.35, 0.6, 1.0}` × `undirected_evidence ∈ {F, T}`，其余全冻结，
每条记「非空率 / 平均命中边数 / 平均证据块数 / 无关查询误召率 / P95 延迟 / PPR 迭代次数」，
结果落 `deliverables/graph-factor-sweep-<date>.json`。详见 §1.6 L1。

### W 涉及文件与测试

| 文件 | 变更 |
|---|---|
| `core/knowledge/graph_ppr.py` | `weak_edge_factor` / `undirected_evidence` 参数 |
| `core/knowledge/graph_search.py` | 硬过滤改衰减 + 空结果计数器 |
| `core/knowledge/plot_graph.py` | 0.5 硬编码 → `plot_weak_edge_factor` |
| `core/orchestrator.py` | 空结果计数上报 |
| `config.py` | 3+1 个配置项（§12） |
| `tests/test_graph_ppr_weighting.py` | **新增**（≥10 项，L0 全套） |

### W 的退出条件

L0 全绿 **且** 全量 pytest 维持 562 passed / 1 skipped / 0 failed **且**
`plot_graph_enabled=true` 下剧情层输出与改动前一致（人工比对 5 条查询）。

---

## 4. 阶段 G0：lore 图谱全量构建与质量验收（硬前置）

### 4.1 实施步骤
1. **抽样预览**：`python scripts/build_graph.py --character wu_ming_zhe --dry-run --limit 8`
   检查点：实体类型稳定、`relation` 短语化（非整句）、`confidence` 分布合理。质量不达标**不要**进全量。
2. **补全角色卡 `entity_aliases`**（人工 10 分钟，收益最高）：
   ```json
   {"entity_aliases": {"无名者": ["格蕾丝", "莉莉", "凯拉", "塞西莉"], "重塑之手": ["重塑"]}}
   ```
   依据：`GraphStore.bind_alias_table()`（`graph_store.py:265`）别名精确匹配优先于向量链接。
   ⚠️ **校验（v6 补）**：`entity_aliases` 的值必须是**同一实体的不同称谓**（本名/化名/称号/别称）。
   **绝不能把其他角色的名字列进来** —— 别名是精确匹配且优先于向量链接，写错会造成**跨实体错误合并**，
   且这种错误在建图后极难发现（图谱 stats 看起来完全正常）。
   建议：先跑 `GET /api/knowledge/graph/entity?q=<别名>` 逐个确认再落盘；完成后**重跑一次构建**（哈希缓存下成本可控）。
3. **后台全量构建**（长任务，务必后台 + 落日志）：
   ```powershell
   python scripts/build_graph.py --character wu_ming_zhe --build 2>&1 | Tee-Object -FilePath logs/build_graph_$(Get-Date -f yyyyMMdd_HHmm).log
   ```
   可先 `--limit 300` 跑核心资料再放开（哈希缓存保证重跑零成本）。
4. **统计与抽检**：`--stats`、`GET /api/knowledge/graph/stats`、`GET /api/knowledge/graph/entity?q=发条装置`

### 4.2 验收标准（未达标不得进 P4）
| 项 | 门槛 |
|---|---|
| 实体 / 边 | ≥150 / ≥400 |
| 孤岛实体占比 | ≤35% |
| **证据分布记录**（B1，v4 已改口径） | 统计 `≥2 条证据的边 / 总边数`。**这是记录项，不再是"触发某开关"的门禁**——剧情层实测 99.7% 单证，lore 大概率同量级，`<50%` 必然成立，判别力为零。真正的决策交给 **阶段 W 的 L1 参数扫描**（§3.1） |
| **检索烟雾测试**（B1） | ≥10 条代表性查询走 `GraphSearcher.retrieve`，**非空率 ≥60%**；否则先修检索链路（查 `link()` 是否零命中、指纹是否漂移），不得进 P4 |
| 抽取失败率（B8） | <10%（先 `--limit 50` 定 batch，再全量） |
| 人工抽检 | 随机 20 条边，错误端点或错误关系 ≤3 条 |
| 幂等 | 重跑输出"新处理 0 块" |
| 服务可用 | `ROLEPLAY_GRAPH_ENABLED=true` 启动无异常，`/graph/stats` 200 |

### 4.3 风险与对策
| 风险 | 对策 |
|---|---|
| 全量耗时长（~2300 块 × 本地 7B） | 后台 + 分批 `--limit`；哈希缓存可续跑 |
| 抽取幻觉 | 边必带 `evidence_chunk_ids`；`graph_edge_min_confidence=0.55`；抽检不合格提至 0.65 重建 |
| 指纹漂移 | 换 embedder/LLM 后需 `--rebuild` |

### 4.4 G0 附加动作：证据分布与检索烟雾测试（B1 强制）

构建完成后**必须**执行（否则 P4 可能在测一个死特性）：

```powershell
# 1) 证据分布：≥2 证据的边占比
python -c "import json;d=json.load(open('data/knowledge/graph_wu_ming_zhe.json',encoding='utf-8'));e=d['edges'];n=sum(1 for x in e if len(x.get('evidence') or [])>=2);print(f'{n}/{len(e)} = {n/max(1,len(e)):.1%}')"

# 2) 检索烟雾测试：10+ 条代表性查询（含单跳 / 多跳 / 无关），统计非空率
python scripts/build_graph.py --character wu_ming_zhe --stats
python tmp_pytest/probe_graph_smoke.py   # 新增只读探针：打印每条查询的命中边数与证据块
```

判定与动作（v4，改为**权重化**而非开关）：
- 占比 <50% → 不再"删边"，而是把 `graph_weak_edge_factor` 设为 **0.35**（默认即此值，等于默认就走衰减路径）。
  **不要**再退回 `include_weak=False`（那会把 99.7% 的边删掉，重复 B1）。
- 非空率 <60% → 先查实体链接（`link()` 是否零命中）与指纹，修好再进 P4。
- 对比实测：`factor ∈ {0.0, 0.35, 0.6, 1.0}` 各跑一遍烟雾测试，记录「非空率 / 平均命中边数 / 平均证据块数」，
  挑非空率达标且**无关查询误召最低**的档位（先例提示：`factor` 越大召回越高但噪声越大，G2ConS 已证明纯共现会引入虚假相关）。
- **补展示层 0.5 折降权**：`GraphSearcher.retrieve` 目前无此折扣（剧情层有，`plot_graph.py:400`），需对齐，
  避免单证块在上下文里喧宾夺主（注意：这是**排序展示层**的折扣，与 PPR 传播层的 `weak_edge_factor` 是两件事，两者都要）。
- 同时试 `graph_undirected_evidence=True`（§1.5 修正 2），记录同一组指标，决定是否默认打开。
- **测试配套（§1.6）**：改 `graph_ppr.py` **之前**先写 L0 等价性用例（用合成小图即可，不依赖真实图谱），
  断言 `weak_edge_factor=0.0` 与旧逻辑输出逐位相等；L1 扫描脚本与 L2 探针集**骨架**也在 G0 阶段建好，
  探针条目等图谱建完再填。**探针集填完即 commit 冻结，之后不许为迎合结果而增删。**

---

## 5. 阶段 R：检索质量（v2 新增，最高性价比）

### 5.1 R1 查询改写
- **新增** `orchestrator._rewrite_query(history, current)`：
  - 触发条件：会话历史 ≥2 轮 **且** 命中指代/省略特征（含"那/他/她/它/后来/怎么样/呢"且长度 <12 字）；否则直接用原句（省调用）。
  - 输入最近 3 轮 + 当前句，LLM 输出独立完整查询；`asyncio.wait_for(..., timeout=3)`，失败/超时**静默回退原句**。
  - 改写结果同时供**四路**使用（向量 RAG / 长期记忆 / 剧情图谱 / lore 图谱）。
- 开关：`query_rewrite_enabled=False`；配置 `query_rewrite_timeout=3.0`、`query_rewrite_max_tokens=64`。

**实现红线（B3，务必照做）**
1. `_gather_context`（`orchestrator.py:335`）**拿不到 history**：历史是在 `run()/stream()` 加锁后取的。改写需在此处
   `history = await asyncio.to_thread(self._session_memory.get_history, req.session_id)` 取最近 3 轮（禁止在事件循环内做同步文件 IO）。
2. **改写结果只喂检索，绝不替换 `req.message`**：`_gen()` 的 `user=` 与情感检测必须用用户原句，
   否则把"那后来呢？"换成改写句后，角色会对着一个自己没听过的问句作答。
3. 长期记忆走的是**独立分支** `memory_tier.retrieve`（`orchestrator.py:638`）——改写后的 query 必须同时透传到这里（B10），不能只改 `_retrieve`。
4. mock provider 下改写会返回固定串：测试须注入 stub LLM，并断言"开关关闭时零额外 LLM 调用"。

### 5.2 R2 跨路去重
- 在 `_gather_context` 合并处按 `chunk_text_hash(text)` 去重。
- **取舍规则（B4 修正）**：两路分数量纲不可比（向量路 top1≈1.0，图谱路 = PPR×confidence ≈0.01~0.2），
  **禁止按分数取舍**。同文本时**保留图谱块**（带「（关系）A —r→ B」行，信息更全），**从 lore 向量列表移除**。
- 范围：**只在 lore 向量路与 lore 图谱路之间做**；剧情块独立预算、独立渲染不动（保住 F2 修复的护栏）。
- 生效条件：**仅当 `graph_enabled` 为真时执行**（默认关闭 → 零回归）。

### 5.3 R3 top_k 实验
- `top_k` 2 → 4，**仅在 R1/R2 生效后**由 P4 A/B 裁决；未达标则回退 2。
- 判据写进 P4：Context Recall 提升且 Faithfulness 不降。

### 5.4 涉及文件与测试
| 文件 | 变更 |
|---|---|
| `src/roleplay/core/orchestrator.py` | `_rewrite_query` + `_gather_context` 内跨路去重 |
| `src/roleplay/config.py` | `query_rewrite_*` |
| `tests/test_query_rewrite.py` | **新增**（≥6 项：触发条件、超时回退、LLM 异常回退、关闭时零调用、四路同用改写结果、去重保留高分与来源标签） |

---

## 6. 阶段 P2：对话三元组增量写图 + 时间线

### 6.1 关键实现决策（逐条已对代码验证）

| 决策点 | 方案 | 依据 |
|---|---|---|
| 落点 | 新建 `core/knowledge/graph_writer.py`：`ConversationGraphWriter` | 保持 `memory_tier` 职责单一 |
| 触发 | `orchestrator.py:794` `consolidate_entries` 之后追加，受 `graph_conversation_write` 控制，异常只告警 | 与长期记忆同批写入 |
| 拿 doc id | `consolidate_entries(..., return_ids: bool = False) -> int \| list[str]`，默认行为不变 | 现有返回 `int`；`tests/test_knowledge.py:190` 未接收返回值，零回归 |
| 端点归一 | `norm_name()` + 角色卡 `entity_aliases` + 代词映射（"我"→用户实体，"你"→角色名），**代词不建实体** | `graph_store.py:32` |
| 与 lore 合并 | 向量相似 ≥ `graph_conversation_link_threshold`（默认 **0.86**，严于 lore 的 0.82）才合并；否则建 pending 实体，`mentions ≥ 3` 转正 | 误合并代价高于漏合并 |
| 边过滤 | `predicate` 空 / >8 字 / 停用谓词 → 丢弃；`confidence` 过低由 `upsert_edge` 自拒 | `graph_store.py:352` |
| evidence | `{ns: "events:<cid>", doc_id: <kb id>, hash: chunk_text_hash(content)}` | `_evidence()` 按文本 hash 回查，events 已在索引范围 |
| **孤证处理**（B2，阻塞；v4 改为权重化） | 对话边**不再豁免过滤开关**，而是走 `graph_conversation_weak_edge_factor=0.6` 的连续衰减（lore 单证边是 0.35）。`PPR` 侧统一按 `n < 2 → w *= factor` 处理 | 先例一致（HippoRAG 2 保留、MS GraphRAG 计数即权重，均**无硬阈值**）；`factor=0.0` 时与旧 `include_weak=False` 逐位等价，`graph_conversation_include_weak` 保留为兼容开关 |
| 异步与落盘 | 整体 `await asyncio.to_thread(...)`；缓冲 `graph_conversation_flush_every=5` 条后 `save()` | `_lock` 是 RLock，禁止锁内 await；图谱 JSON 全量重写 |
| **写盘节流**（B5） | 两次 `save()` 最小间隔 `graph_conversation_flush_min_interval=60s`（或会话结束才 flush） | `GraphSearchRegistry` 按 **mtime** 缓存（`:307-337`）；每次写盘都会让在线检索器重建并重新扫描 KB 建证据索引 |
| **新实体补向量**（B5） | flush 时在线程内 `ensure_entity_vectors` | 新实体无 `vec` 时只能精确匹配链接（`_link_vector` 过滤 `if e.get("vec")`，`graph_search.py:128-132`） |
| **证据悬空清理**（B6） | 优先**复用** `GraphStore.drop_source(ns, doc_id)`（`graph_store.py:427-446`，证据清空则删边）；flush 时用它清理对话边 | 与 NestJS+Neo4j 先例同构（`weight -= 1`，归零 `DETACH DELETE`）——**能力已存在，只需把 `memory_tier.prune()` 的删除 doc id 接进来**，不要新写一套 |
| 淘汰 | `graph_conversation_max_edges=500`，超出按 `ts` + `importance` 淘汰 | 防 PPR 变慢 |
| **rebuild 保护**（B7） | `build_graph.py --preserve-conversation`（默认 True）：`--rebuild` 必须保留 `source == "conversation"` 的边与仅被对话边引用的实体 | `build_graph.py:145-148` 的 `--rebuild` 会 `gpath.unlink()` 直接删文件；`--build` 是增量、天然保留 |

### 6.2 涉及文件
| 文件 | 变更 |
|---|---|
| `core/knowledge/graph_writer.py` | **新增** |
| `core/knowledge/memory_tier.py` | `consolidate_entries` 增 `return_ids` |
| `core/orchestrator.py` | 挂钩写入（try/except 告警） |
| `core/knowledge/graph_search.py` | 新增 `timeline(eid, limit)`：按 `ts` 排序该实体全部边并返回证据块 |
| `api/knowledge.py` | `GET /api/knowledge/graph/timeline?entity=&limit=` |
| `scripts/build_graph.py` | `--preserve-conversation` |
| `tests/test_graph_conversation.py` | **新增** |

### 6.3 测试用例清单（≥13 项）
1. 三元组全字段 → 写入 `source="conversation"` 边，stats 计数 +1
2. 缺 `predicate` / 超长 → 丢弃
3. "我/你" → 归一为用户实体/角色名，不产生代词实体
4. 相似 0.9 → 合并已有 eid
5. 相似 0.7 → pending 实体，不参与检索
6. pending 命中 3 次 → 转正
7. `return_ids` 默认关闭时仍返回 int（零回归）
8. evidence 可被 `_evidence()` 回查到原文（真实 KB 往返）
9. 关闭 `graph_conversation_write` → 图谱文件不变（零回归）
10. 写入异常 → 主链路不受影响
11. 超过 `max_edges` → 最旧最低边被淘汰
12. `timeline()` 按 ts 倒序、跨会话正确
13. `--rebuild` 后对话边仍存在

### 6.4 验收
```powershell
python -m pytest tests/test_graph_conversation.py -q
python -m pytest tests/ -q          # 0 failed，基线 562 + 新增用例
python scripts/build_graph.py --character wu_ming_zhe --stats   # edges_conversation > 0
```

---

## 7. 阶段 A：PPR 有向语义（v2 新增，小项）

**问题**：`graph_ppr.py:47-48` 对所有边双向加边，"A 杀死 B" 与 "B 杀死 A" 传播等价。

**方案**（保持零回归）
1. 边结构增 `directed: bool`（缺省 `False` = 现状无向）。
2. **离线分类，不在线判断**：建图时用规则 + 可选 LLM 标注关系类型：
   - 有向类：`杀死/背叛/持有/发动/给予/导致/隶属/前往` → `directed=True`
   - 对称类：`朋友/同盟/同属/相识/恋人/对手/伙伴` → 无向
3. `personalized_pagerank` 增 `respect_direction: bool = False`；为 `True` 时 `directed=True` 的边只加 `src→dst`。
4. 默认关闭（`graph_ppr_respect_direction=False`）；开启后由 P4 判定是否有增益。

**测试**：有向边不再反向传播（A→B 的种子不激活 B 的上游）、对称边仍双向、默认参数行为与现状逐字节一致。

---

## 8. 阶段 P3：社区摘要与全局问答

### 8.1 实施
1. **新增 `core/knowledge/graph_community.py`**
   - `detect_communities(store)`：无向化连通分量（零依赖）；分量过大时标签传播细分。
     **权重只在标签传播阶段生效**（连通分量是无权算法）——`len(evidence)` 作为标签传播的边权输入，
     与 MS GraphRAG 一致；若未来要换 Leiden 再说（当前属非目标，见 §2）。
   - `summarize(...)`：每社区取 top 度实体 + 高频 relation，LLM 生成 2~3 句摘要。
   - **幂等缓存**：key = `sha1(sorted(成员 eid) + sorted(relation))`，落 `data/knowledge/graph_cache/<cid>/community_<hash>.json`。
2. **路由** `is_global_query(q)`：规则词表（整体/总体/你们/组织/世界/风格/总的来说/怎么看待）+ 问句不含具体专名。**规则优先，不上 LLM 分类器**（省调用、可解释）。
3. **注入**：`persona_prompt.build_community_context()` 渲染【背景总览】块，独立预算 `graph_community_max_chars=800`，排在【关系脉络】之后。
4. **编排**：`_gather_context` 增第六路 `_community_retrieve`（默认关闭、异常静默降级）。

### 8.2 涉及文件与测试
| 文件 | 变更 |
|---|---|
| `core/knowledge/graph_community.py` | **新增** |
| `core/persona_prompt.py` | `build_community_context()` + 【背景总览】 |
| `core/orchestrator.py` | 第六路并行 + 透传 |
| `scripts/build_graph.py` | `--communities` 离线预生成摘要 |
| `tests/test_graph_community.py` | **新增**（≥8 项） |

### 8.3 风险
| 风险 | 对策 |
|---|---|
| 摘要幻觉 | 摘要只基于实体名 + relation 统计生成，禁止自由发挥；记录来源社区成员可核对 |
| 喧宾夺主 | global 路由失败仍走 local；摘要块排最后、预算最小 |
| 首次提问卡顿 | 摘要离线预生成，在线只读缓存 |

---

## 9. 阶段 P4：A/B 评估与观测指标（决策依据）

### 9.1 实施
1. `scripts/eval_rag_standard.py` 增 `--graph`、`--ab`、`--out`：
   - 图谱臂：构造 `GraphSearchRegistry` → `searcher.retrieve(q)`；
   - 与生产对齐：`build_roleplay_prompt(..., chunks=chunks, graph_chunks=gchunks, graph_max_chars=s.graph_context_max_chars)`；
   - **口径修正**：把 `build_graph_context(gchunks)` 输出并入 `contexts`，否则低估 Context Recall/Precision；
   - 输出 JSON + Markdown 到 `deliverables/rag-eval-graph-ab-<date>.{json,md}`。
2. 观测：`GraphSearcher` 加计数器（实体链接命中/未命中、PPR 使用边数、证据解析成功/尝试），经 `stats()` 的 `retrieval` 段暴露。
3. **R3 裁决**：同一套 A/B 增加 `top_k=2 vs 4`（叠加 R1/R2）对照。

### 9.2 判据（写死在报告里）
- multi-hop 相对基线 **提升 ≥15%**；
- Faithfulness **不降**（Δ ≥ -0.03，`--repeat 2` 取均值）；
- 单跳用例 **不劣化**（Δ ≥ -0.03）；
- Context Recall 提升才接受 `top_k=4`。

**v5 补充（见 §1.6，均为硬约束）**
- **一次只改一个变量**：generator / prompt / temperature / 图谱文件 / 探针集全部冻结；只允许动被评估的那个检索参数。
- **顺序不可颠倒**：先冻结 probe set 并 commit → 跑 L1 参数扫描定 `weak_edge_factor` → 定完才跑 L3 A/B。
  （先例警告：小规模 golden set 极易被"挑查询"操纵，边调参边加查询等于自欺。）
- 报告**必须**同时给出：**Holes**（检索到但未标注的实体占比，高则 nDCG 不可信）、**无关查询误召率**、
  **被衰减边数 / 参与边数**。只有"非空率提升"而缺少后两项，结论不成立。
- **人设一致性不降**（Δ ≥ -0.03，LLM judge + 人工盲评抽样）——角色扮演区别于通用 RAG 的独有红线：
  图谱注入更多上下文后，角色可能变啰嗦或泄露世界观外的信息。
- 保留对照臂与回滚 tag；上线留 holdout，**不 100% 切流**。
- **绝对门槛（v6 补）**：相对提升之外必须同时满足 §1.6.4 ③ 的绝对线
  （multi-hop 忠实度 ≥0.70、整体 Faithfulness ≥0.80、人设一致性 ≥4.0/5、无关查询误召率 ≤10%）。
  只有"相对 +15%"而绝对值不达标 → 判**未通过**，不算"达标但幅度小"。

### 9.3 命令
```powershell
python scripts/eval_rag_standard.py --repeat 2 --out deliverables/rag-eval-base-20260909.json
python scripts/eval_rag_standard.py --ab --repeat 2 --out deliverables/rag-eval-graph-ab-20260909.json
```

### 9.4 决策门
| 结论 | 动作 |
|---|---|
| **全达标**（相对判据 + §1.6.4 ③ **绝对门槛**同时满足） | `graph_enabled` / `query_rewrite_enabled` 默认置 True，同步两份设计文档 |
| 相对达标但**绝对门槛未过** | **判未通过**（不是"小幅达标"）。低基线下的 +15% 没有意义，保持关闭，把绝对值写进报告作为后续目标 |
| multi-hop 达标但 Faithfulness 降 | 依次收紧 `graph_edge_min_confidence`（0.55→0.65）、下调 `graph_weak_edge_factor`（0.35→0.2）后复测；**不要再动 `include_weak`**（v4 起已降级为兼容开关） |
| 人设一致性下降 | **一票否决**，优先于 multi-hop 收益。角色扮演里"答得更全但人设崩了"是净损失 |
| `top_k` | **独立裁决**（§1.6.4 ②）：在图谱决策**之后**单独跑第三臂，不与图谱开关捆绑上线 |
| 未达标 | 保持默认关闭，A/B 数据与结论写进审计报告续章，图谱作为实验能力保留 |

---

## 10. 阶段 O：性能与资源治理（v2 新增，行为零变更）

| 编号 | 项 | 位置 | 说明 |
|---|---|---|---|
| O2 | `_BM25` 建完索引 `del self._docs` | `vector_store.py:140` | 1 行，释放原始 token 列表 |
| O3 | `_collect` 锁内快照引用、锁外算余弦；BM25 缓存按 ns 失效 | `vector_store.py:304-322` | 减少写阻塞 |
| O4 | 共享线程池替换每次新建 | `embedder.py:42` | `max_workers=4` 模块级单例 |
| O5 | 嵌入结果磁盘缓存（LRU + JSON，key=文本 md5） | `embedder.py` | 离线建库收益最大；在线查询命中率 30~40% |
| O1 | 向量 `array('f')` 存储 | `vector_store.py` | ⚠️ 需**迁移方案**：读写兼容旧 `list[float]` 库文件，`fingerprint` 不变；放在最后做 |
| O6 | 证据倒排索引离线预建 | `build_graph.py` + `graph_search.py` | 输出 `hash → chunk` 索引，检索 O(1)；缺索引时回退现有扫描 |
| O7 | Ollama `keep_alive` 缩短（60s） | 配置/启动脚本 | 零风险省显存 |
| O8 | 在线/离线嵌入批量分级（4 / 32） | `embedder.py:aembed` | 低延迟 vs 高吞吐 |
| O9 | LLM 实例共享（单例） | `core/llm/factory.py` | 需确认线程/事件循环安全后再合 |

**验收**：每项改动后 `python -m pytest tests/ -q` 0 failed；O1 需额外验证旧库可读、新库可重载、`fingerprint` 不误报。

---

## 11. 阶段 M：工程卫生与文档同步

| 项 | 内容 | 验收 |
|---|---|---|
| 临时文件 | 清理根目录 `_shuzhi_extract.txt`、`_tmp_pron_edges.txt` → `tmp/` 并 `.gitignore` | 根目录无 `_` 开头临时文件 |
| 备份文件 | `data/knowledge/` 下 7 个 `.bak` + 3 个 `plot_cache_bak*`（约 15MB）→ **先出清单，确认后再归档**到 `data/knowledge/_backup/` | 清单经人工确认 |
| 依赖声明 | 统一以 `pyproject.toml` 为准，`requirements.txt` 由 `pip-compile` 生成锁定版 | 两处不冲突 |
| 漂移巡检 | 文档重导入/删除路径确认调用 `remove_by_doc`；缺失则补 `scripts/graph_gc.py` + `doc_hash → edge` 倒排 | 删文档后其证据边清理、无孤儿实体 |
| Python 版本 | 文档锁定 3.13（**不重建 .venv**，双 `.pyc` 属切换版本产物，无收益） | README 注明 |
| 文档同步 | `GRAPHRAG_ENHANCEMENT_PLAN.md`、`RAG_SYSTEM_DESIGN.md` 落地状态与新增阶段 | 与代码一致 |

---

## 12. 新增配置一览（均带默认值，缺省零回归）

| 字段 | 默认 | 阶段 |
|---|---|---|
| `query_rewrite_enabled` | `False` | R |
| `query_rewrite_timeout` | `3.0` | R |
| `query_rewrite_max_tokens` | `64` | R |
| `rag_cross_route_dedup` | `True` | R |
| `graph_conversation_write` | `False` | P2 |
| `graph_conversation_link_threshold` | `0.86` | P2 |
| `graph_entity_promote_mentions` | `3` | P2 |
| `graph_conversation_max_edges` | `500` | P2 |
| `graph_conversation_flush_every` | `5` | P2 |
| `graph_conversation_include_weak` | `True` | P2（**降级为兼容开关**，B2 已由权重化方案自动解决） |
| `graph_conversation_flush_min_interval` | `60` | P2（B5 写盘节流，秒） |
| `graph_weak_edge_factor` | `0.35` | G0（B1/v4：单证边权重系数；`0.0` ≡ 旧的 `include_weak=False`，零回归） |
| `graph_conversation_weak_edge_factor` | `0.6` | P2（B2/v4：对话单证边权重系数，高于 lore） |
| `graph_undirected_evidence` | `False` | G0（§1.5 修正 2：按无序实体对聚合证据数，实测后再定） |
| `graph_weak_edge_discount` | `0.5` | G0/P2（lore 检索器对单证边的**展示层**降权，对齐 `plot_graph.py:400`） |
| `plot_weak_edge_factor` | **`0.5`** | W（**不可改默认值**：替换 `plot_graph.py:389-401` 现存的硬编码 0.5 折；改成别的值会**静默改变已启用的剧情层行为**） |
| `graph_timeline_max_items` | `8` | P2 |
| `graph_ppr_respect_direction` | `False` | A |
| `graph_community_enabled` | `False` | P3 |
| `graph_community_min_size` | `5` | P3 |
| `graph_community_max_summaries` | `3` | P3 |
| `graph_community_max_chars` | `800` | P3 |
| `graph_global_keywords` | `["整体","总体","你们","组织","世界","风格","总的来说","怎么看待"]` | P3 |
| `embed_cache_enabled` | `True` | O |
| `embed_cache_dir` | `./data/knowledge/embed_cache` | O |
| `ollama_keep_alive` | `60s` | O |

> ⚠️ **零回归到底靠什么保证（v6 澄清，容易误解）**
> 新配置的默认值**本身并不保证零回归**——`graph_weak_edge_factor=0.35` 是一个**会改变行为**的值。
> 零回归实际由**两层**提供，缺一不可：
> 1. **整路开关**：`graph_enabled=False` / `plot_graph_enabled=False` —— 图谱路根本不执行，任何 factor 都无所谓；
> 2. **等价性开关**：`weak_edge_factor=0.0` ≡ 旧的 `include_weak=False` —— 用于**图谱路开启后**需要精确复现旧行为时。
>
> 因此：`plot_weak_edge_factor` **必须**默认 `0.5`（与现存硬编码一致），因为剧情层图谱**已经构建**，
> 一旦用户开启 `plot_graph_enabled` 就会生效，改默认值等于静默改动线上行为。
> `graph_weak_edge_factor=0.35` 可以默认，是因为 lore 图谱**尚未构建**、`graph_enabled` 默认关闭，不存在存量行为。

---

## 13. 全局验收矩阵

| 检查 | 命令 | 门槛 |
|---|---|---|
| 全量回归 | `python -m pytest tests/ -q` | 0 failed；基线 562 passed / 1 skipped，新增后递增 |
| 零回归（开关关闭） | 新开关置 False 跑对应套件 | 图谱文件不变、prompt 与现状一致 |
| 服务健康 | `ROLEPLAY_GRAPH_ENABLED=true` 启动 + `/graph/stats` | 200；无图谱文件时静默降级 `[]` |
| 图谱质量 | `scripts/build_graph.py --stats` | §4.2 |
| **L0 等价性**（v6） | `pytest tests/test_graph_ppr_weighting.py -q` | `factor=0.0` 与旧逻辑逐位相等；确定性；口径一致 |
| **L1 参数扫描**（v6） | `graph-factor-sweep-<date>.json` 存在且覆盖 10 组配置 | 非空率达标档位已选定，**无关查询误召率未随 factor 单调爆炸** |
| **L2 探针集**（v6） | `tests/fixtures/graph_probe_set.json` 已 commit 且打 tag | ≥30 条、四类齐全、含 Holes 指标；**调参后不得再增删条目** |
| **L3 人设一致性**（v6） | `--ab` 报告含 persona 分与人工盲评抽样 | 不降（Δ ≥ -0.03，判据定义见 §1.6 L3 补充） |
| 效果 | `scripts/eval_rag_standard.py --ab` | §9.2 判据（含**绝对门槛**，不只是相对提升） |

---

## 14. 提交粒度建议

0. `test(graph): PPR 权重化 L0 等价性用例（先于改动，锁住现状行为）`
1. `feat(graph): 孤证边权重化 weak_edge_factor + undirected_evidence（含剧情层 0.5→配置化，默认不变）`
2. `chore(graph): 全量构建 lore 图谱 + 质量抽检记录`（仅数据）
3. `feat(rag): 查询改写 + 跨路去重（默认关闭）`
4. `feat(graph): 对话三元组增量写图 + 时间线 API（默认关闭）`
5. `feat(graph): PPR 有向语义（默认关闭）`
6. `feat(graph): 社区摘要与全局路由（默认关闭）`
7. `test(eval): 冻结探针集 graph_probe_set.json（打 tag）`
8. `feat(eval): eval_rag_standard --ab A/B 评估 + 观测指标 + L1 扫描脚本`
9. `perf: BM25 释放 _docs / _collect 移出锁 / 嵌入缓存 / 共享线程池`
10. `chore: 清理临时与备份文件 + 依赖声明统一 + 文档同步`

每步提交前跑全量测试；不达标即停在原地，不带红灯进下一阶段。

---

## 15. 遗留（本计划之外，仅登记）

- 双图谱抽象统一（A4）：待 P4 证明图谱有效后再评估。
- 嵌入模型切换：只能是中文多语言（bge-m3 / gte-Qwen2-7B-instruct），必须走 P4 A/B；`bge-small-en` 已否决。
- cross-encoder 重排序：R 阶段后仍不达标再上，需评估显存代价。
- 抽取专用小模型 / max_tokens 下调：质量风险未评估。
- 冷热分层存储：>1 万块再议。
- LightRAG sidecar：P3 完成后按"只替换全局层"评估。
