# GraphRAG 收尾计划（v6）可行性审计

> 审计日期：2026-09-09
> 被审计对象：`deliverables/graphrag-phase2-plan-20260909.md`（v6，897 行）
> 审计方式：① 逐条核验计划对代码/数据的事实断言；② **在真实剧情图谱（4261 边）与原 lore 知识库（2085 块）上跑验证实验**；③ 联网检索 2026 年 GraphRAG / 检索评测 / LLM-as-judge 最新实践做横向校准
> 审计结论：**有条件通过（Conditional Go）— 但必须先做结构减除，v6 现状不可直接执行**

---

## 0. 一句话结论

计划的**工程严谨度很高**（尤其 B1/B2 的发现与 D7/D11/D12 的驳回都经得起验证），但它犯了一个典型的"过度设计"错误：**把一个二元开关包装成连续旋钮，然后围绕这个旋钮新增了一整个阶段（W）、四个配置项、一套五层测试体系和一批人工标注工时**。

我在真实图谱上做了实证：**这个旋钮在本项目数据上数学近似无效**（§2.1）。同时计划遗漏了三件业界公认最高杠杆的事：**约束 relation 词表、锁定知识库嵌入状态、解耦 judge 模型**（§2.2–§2.4）。此外 Git 仓库当前**零提交**，计划中所有依赖 git tag / 版本化 / 回滚的机制**一条都跑不了**（§4.1）。

---

## 1. 核验通过的部分（应予肯定）

计划中绝大多数代码断言我都逐行验证了，**准确度显著高于一般的技术计划**。以下为实测确认成立：

| 计划断言 | 验证方式 | 结果 |
|---|---|---|
| 全量测试基线 **562 passed / 1 skipped / 0 failed** | 实跑 `pytest tests/ -q` | ✅ 实测 563 项（562 passed + 1 skipped），29s |
| lore 语料 **2085 块** | 解析 `lore_wu_ming_zhe.json` | ✅ 精确命中（+ spoken 54 块 = 2139） |
| 剧情图谱 **5026 实体 / 4261 边** | 解析图谱 JSON | ✅ 精确命中 |
| 单证边 **99.7%** | 证据条数分布统计 | ✅ 实测 4248/4261 = **99.69%**（≥2 证据仅 13 条） |
| 实体 `vec` 全为 `None`，**D7 驳回正确** | 遍历 entities | ✅ 5026/5026 全部 `vec=null`，`ensure_entity_vectors` 已是懒加载 |
| `graph_ppr.py:40-41` 硬阈值丢边 | 读源码 | ✅ 证实（且 `graph_search.py:217` 同逻辑但硬编码 `2` 而非引用常量） |
| 合并键 `(src,dst,relation)` 方向+谓语双敏感 | `graph_store.py:375` | ✅ 证实 |
| `GraphSearchRegistry.get()` 按 **mtime** 缓存 | `graph_search.py:307-337` | ✅ 证实，B5 判断正确 |
| `_collect` 锁内算余弦（D3） | `vector_store.py:310-329` | ✅ 证实 |
| `_BM25.__init__` 保留 `_docs`（D2） | `vector_store.py:123-140` | ✅ 证实（`_doc_len` 需保留，只能释放 `_docs`） |
| `_run_async` 每次新建线程池（D6） | `embedder.py:42-43` | ✅ 证实 |
| `consolidate_entries` 返回 `int` | `memory_tier.py:129` | ✅ 证实 |
| **D11 驳回正确**（consolidate 无双写） | `orchestrator.py:793-801` | ✅ 确为 if/else，不是双写 |
| **D12 驳回正确**（prune 已被调用） | `orchestrator.py:807` | ✅ 确已调用 |
| `_gather_context` 拿不到 history（B3） | `orchestrator.py:335,374,405,409` | ✅ 四路确全用 `req.message`，无改写 |
| 长期记忆走独立分支（B10） | `orchestrator.py:638` | ✅ 证实 |
| 剧情层 `score *= 0.5` 硬编码 | `plot_graph.py:400-401` | ✅ 证实 |
| **角色卡 `entity_aliases` 未填** | 读 `data/characters/wu_ming_zhe.json` | ✅ 确为 `null`，G0 步骤 2 是真痛点 |
| **lore 图谱尚未构建** | `ls data/knowledge/` | ✅ 无 `graph_wu_ming_zhe.json` |
| 向量改 `array('f')` 省 **~50MB**（D1/O1） | 按 2085×768 float 实测推算 | ✅ **49MB → 6MB**，估算准确 |
| `factor=0.0 ≡ include_weak=False` 零回归 | 40 个高热度种子逐位比对 | ✅ **最大差 0.000e+00**，严格等价成立 |
| Ollama 资源可用 | `curl :11434/api/tags` | ✅ `qwen2.5:7b`(Q4_K_M) + `nomic-embed-text` 在线，CPU 20 线程 |

> 值得肯定：`factor=0.0` 的严格等价性这条核心承诺是**站得住的**，计划在这件事上的推理正确。

---

## 2. 🔴 阻塞级问题（必须先解决）

### 2.1 `weak_edge_factor` 在本项目数据上数学近似无效（阶段 W 需整体重评）

**这是本次审计最重要的发现。** 计划用整整一个阶段 W + 4 个配置项 + L0/L1 五层测试来落地"证据数驱动的连续衰减"。我在真实剧情图谱上直接跑了对照实验：

实验设计：取度最高的 40 个实体逐个做单种子 PPR，`weak_edge_factor ∈ {0.0, 0.2, 0.35, 0.6, 1.0}`，比较相对 `factor=1.0` 的 top-10 结果。

```
=== factor 扫描（40 个高热度种子，参照 factor=1.0）===
  factor=0.0   使用边数=13      top10 集合重合度=0.215  序一致率=0.600
  factor=0.2   使用边数=4261    top10 集合重合度=0.972  序一致率=0.979
  factor=0.35  使用边数=4261    top10 集合重合度=0.982  序一致率=0.988
  factor=0.6   使用边数=4261    top10 集合重合度=0.993  序一致率=0.993
  factor=1.0   使用边数=4261    top10 集合重合度=1.000  序一致率=1.000
```

**结论：**

1. **中间档位之间没有有意义的区别。** `factor ∈ {0.2, 0.35, 0.6, 1.0}` 两两之间的 top-10 重合度高达 **97.2%–99.3%**，序一致率 97.9%–99.3%。按计划的 L1 扫描网格跑完，会得到一条**几乎平坦的曲线**，无法支撑"基于数据选参数"的决策。
2. **数学原因**：PPR 的转移概率是 `w / deg(u)`，即**按节点度归一化**。既然 99.69% 的边都是单证边，给它们统一乘同一个常数，每个节点内部的**相对份额完全不变**，传播结果自然不变。计划里"单证边传不远"的直觉描述在 PPR 里不成立。
3. **真正起作用的只有一个二元开关**：`factor=0.0`（用 13 条边） vs `factor>0`（用 4261 条边）——这两者之间 top-10 重合度只有 **0.215**，差异巨大。**而这恰恰就是 `include_weak` 这个布尔值本身。**
4. **`undirected_evidence`（修正 2）完全无效**：
   ```
   无序聚合后从「单证」晋升为「多证」的边 = 23 / 4261 (0.54%)
   undirected=True vs False 的 top10 重合度 = 1.000（完全相同）
   ```
   为了它新增 1 个配置项 + 占掉 L1 扫描一半的维度（10 组配置里有 5 组），产出为零。
5. **等价性仍成立**：`factor=0.0` 与旧 `include_weak=False` 的输出最大差 `0.000e+00`。计划这一条承诺没有被推翻——但它是"1 vs 0"的等价，不是"0.35 有意义"的证明。

**处置建议（结构性减除）**：
- **删除** `weak_edge_factor` / `graph_conversation_weak_edge_factor` / `plot_weak_edge_factor` / `undirected_evidence` 共 4 个配置项；
- **删除**阶段 W（W2/W3/W5）与 L1 参数扫描；保留 W1（L0 等价性测试）与 W4（空结果计数器），但这二者各自 < 0.5d；
- B1 的解法回归为一句话：**`graph_include_weak = True`（lore 对齐剧情层现状）+ 展示层 `0.5` 折扣 + 空结果计数器**。这正是剧情层已经验证过、且 `plot_graph.py:389-401` 已在跑的方案。
- 净效果：**省约 1.0–1.5 人日 + 3 个配置项 + 10 组无意义的扫描，同时修复效果不变。**

### 2.2 P4 的核心判据存在"数学死锁"：Faithfulness 绝对门槛当前不可达

计划 §1.6.4 ③ 规定绝对门槛：**Faithfulness ≥ 0.80**。而现有基线（`deliverables/rag-eval-standard.json`，60 条用例）实测：

```
faithfulness   n=53  mean=0.712  min=0.19  max=1.00
relevance      n=48  mean=0.748
precision      n=48  mean=0.984
recall         n=39  mean=0.884
multihop       n= 9  mean=0.796
refusal        n= 7  mean=1.000
```

**对照臂（基线）自己就是 0.712 < 0.80。** 按 §9.4 决策门"相对达标但绝对门槛未过 → **判未通过**"，那么无论图谱多有效，P4 都将永远输出"不通过"。而把 faithfulness 从 0.712 拉到 0.80，**不在计划任何阶段的范围内**。

同时，multi-hop 判据存在**天花板效应**：

```
multi-hop 明细: [0.67, 1.0, 1.0, 1.0, 1.0, 0.5, 0.5, 1.0, 0.5]   均值 0.796
→ 理论上限 1.000，相对提升上限仅 (1.0-0.796)/0.796 = 25.6%
→ 计划要求 ≥ +15%，需达 0.916
→ 4 个不全对的用例必须几乎全部修到满分；只要有一个 0.5 没修好：
   最高 = (1+5+1+0.5)/9 = 0.833 → 仅 +4.7% → 判不通过
```

9 条用例的样本量也远低于统计显著性要求，且其中有 5 条已经满分（无法再提升）。

**处置建议**：
- 把绝对门槛改成"**不低于复测后的基线**"，或先单列一个前置任务（建议称 P3.5）把 faithfulness 拉过 0.80 再开 P4；**二者必须选一，否则 P4 是空转**。
- 补一节"判据可达性验算"：给出当前值、理论上限、所需绝对提升，再决定相对百分比。
- multi-hop 探针数先从 9 扩到 ≥30 且**重新分布难度**（当前 5/9 已满分的分布毫无判别空间）。
- **注意**：§1.6.4③ 的 Faithfulness ≥0.80 比脚本现存门槛 **0.90** 更低，属于"以引入绝对门槛之名降低既有门禁"，需明确说明这是有意的还是笔误。

### 2.3 Judge 与被测模型同源 — 计划自设红线被自己的落地方案违反

计划 §1.6.4 ① 明确写道：*"judge 模型**不得用生成回复的同一个本地 7B**。LLM-as-judge 有公认的 self-enhancement bias"*。

但 §9.1 的落地方式是"扩展 `scripts/eval_rag_standard.py`"，而该脚本：

```python
# scripts/eval_rag_standard.py:39
JUDGE_MODEL = None  # 运行时从 settings 读（与被评估模型一致）
# scripts/eval_rag_standard.py:708
JUDGE_MODEL = s.llm_model          # ← .env: ROLEPLAY_LLM_MODEL=qwen2.5:7b
```

**judge 就是生成器本身。** 计划里所有LLM-judge 指标（faithfulness、multihop、 relevance、以及拟建的人设一致性 LLM 打分）都会自带自增强偏差。

外部校准确认了这条红线的严重性：self-preference / self-enhancement bias 在同源模型上有 **10–25 个百分点的 inflated winrate**（Zheng et al. 2024，via FutureAGI 2026 综述）；行业公认的可靠改法是"**judge 必须来自不同模型家族**"，其次才"多 judge 投票 / 提高人工占比"。

同时计划的 Cohen's kappa 只用于**双标注人间一致性**，完全缺少外部推荐的**judge-to-human kappa**（≥0.6 才算可接受门校准）。

**处置建议**：
- P4 前置项：给 eval 脚本加 `JUDGE_MODEL` **独立配置**（默认仍兼容，但必须允许指向不同模型/云端模型），并在报告里输出所用 judge 身份；
- 建 50–100 条人工校准集，跑**judge-to-human kappa**，<0.6 不得用该 judge 下上线结论；
- 人设一致性**以人工盲评为主**（计划已倾向此方向，应写成硬要求而非"推荐"）。

### 2.4 计划自承认的时序前提被打破：仓库零提交

```
$ git rev-list --all --count
0
$ cat .git/HEAD
ref: refs/heads/refactor/frontend-layout      # 无任何提交
```

仓库**没有任何一次提交**。这直接使得以下计划条款**全部无法执行**：

- §1.6.2 L2："探针集 **git 版本化，打 `probe@YYYY-MM-DD` tag**"
- §9.2："**保留对照臂与回滚 tag**"
- §14：11 条"提交粒度建议"（`test(graph): …` / `feat(rag): …` 等）
- §1.6.3 的"探针集必须在调参前**冻结并 commit**"

**处置建议**：在任何阶段开始前先做首次提交（建议卡片成为 `#0`），否则整套"可复现 / 可回滚 / 防自欺"机制是空话。

---

## 3. 🟠 高优先级问题

### 3.1 【最高杠杆遗漏】抽取器未约束 relation 词表，垃圾谓语会污染提示词

2026 年业界面向 GraphRAG 的一致最高杠杆建议是"**抽取前先限定 relation 词表**"：

> *"The single highest-leverage decision is restricting which node and relationship types the extractor may produce. An unconstrained LLM extractor invents HELPED_WITH, ASSISTED_ON, and SUPPORTED for the same idea, **fragmenting the graph so traversals miss connections**."* — GraphRAG Best Practices, kindatechnical
>
> *"**Define your relation types before extraction.** Do not run a generic entity and relation extraction pipeline and hope the graph is useful. If you cannot articulate what your edges mean, the graph will not help with reasoning."* — When to Use KG-RAG, ML Digest

本项目的抽取提示词（`graph_extract.py:30-42`）只要求"*relation 用简短谓语（隶属/持有/摧毁/杀死/象征/发动/约定…）*"，**是开放词表**；`normalize_extraction`（:90-96）对 relation 也**只做 strip，不做归一化/近义词折叠**。在已构建的剧情图谱上后果已经爆表：

```
=== relation 词表治理状况（4261 条边）===
不同 relation 词        = 1564   （词表/边数 = 36.7%）
仅出现 1 次的 relation  = 1128   （占词表 72.1%）

Top 谓语：前往346 / 持有176 / 象征111 / 隶属于68 / 背叛65 / 拥有53 / 隶属52 …
单例谓语抽样：不 / 不与 / 不会 / 一度繁荣 / 一手推动 / 下达 / 下达命令 /
             不同于 / 不属于 / 不隶属于 / 不如其专业 / 不宜承担 / 不过是 /
             不符合描述 / 行心力 / 用 RFID？ …

近义谓语自动聚类 = 101 簇，涉及 1294 条边（30.4%）
  {不…, 存在, 存在于, 是, 生存于, 生活于, 所在, 所在地 …}     141 条边
  {不同于, 不属于, 不隶属于, 属于, 隶属于}                     123 条边
  {不象征, 象征}                                              112 条边
```

**这不是"计划已经解决的问题"，而是计划完全没有的事。** 更关键的是：`graph_search.retrieve` 会把边渲染成 `f"{src} —{relation}→ {dst}"` 送进提示词的【关系脉络】块。也就是说，**「xxx —行心力→ yyy」「xxx —用 RFID？→ yyy」这类字符串会被直接注入 system prompt**——这是 GraphRAG 特有的提示词污染路径，而 lore 层连 P2 那种"`predicate >8 字` 丢弃"的粗过滤都没有。

**处置建议（这是我认为性价比最高的新增项）**：
- 新建 **阶段 S-1（relation 词表治理，~0.5–1d）**，排在 G0 全量构建**之前**：
  1. 定义受控 relation 词表（建议 40–80 个，覆盖现有 top 谓语即可吃掉 ~60–70% 的边）；
  2. 在抽取提示词里显式枚举，并要求"不在表内的关系映射到最近的表内谓语，无法映射则不输出"；
  3. 对**已有 4261 条边**跑一次离线归一遍（小模型批处即可），成本远低于重建；
  4. 补 `predicate` 卫生过滤：长度 >8 字 / 含标点 / 命中垃圾黑名单 → 丢弃。
- G0 验收（§4.2）**增加 relation 卫生门槛**：唯一 relation 词 ≤ 目标值（建议 ≤300）、单例谓语占比 ≤40%、黑名单 0 命中。
- 预计副作用：这么做之后真正有意义的去重/ wiązanie 才可能发生。

### 3.2 计划对"99.7% 单证"的根因诊断解释力不足（实测证伪）

计划 §1.5 归因"。我们的实测可以证伪它的解释力：

```
把同一有向实体对 (src,dst) 上的所有不同 relation 全部合并后：
    证据条数分布 = {1: 3849, 2: 94, 3: 22, 4: 4, 5: 2, 8: 1}
    ≥2 证据的实体对 = 124 / 3973 = 3.12%   （未合并时 13/4261 = 0.31%）
```

也就是说：**即使把谓语碎片问题 100% 解决，`≥2 证据` 的比例也只能从 0.31% 抬到 3.12%，仍有约 97% 的边是单证。**

**真正的根因是抽取范式本身**：本 pipeline 是 **per-chunk 独立抽取**，一条语义关系在语料里通常只被陈述一次，`evidence` 计数**从设计上就攒不到 2**。`WEAK_EVIDENCE_MIN=2` 这个门槛在本范式下是一个**不可达目标**，而不是"需要调对的阈值"。

> **对照先例**：计划引用 MS GraphRAG"计数即权重"是对的，但 MS GraphRAG 的用法是 `weight = 共现次数`，**从 1 开始就是合法权重**，它没有"计数 <2 就算孤证"这道门。本项目的做法相当于把 MS GraphRAG 的连续权重**先离散成两档再加一个倍数**——在一个 99.7% 都落在同一档的分布上，这个离散化必然退化为常数，这就是 §2.1 实测结果的根因。

**结论**：一句话概括——**单证不是异常，是本项目抽取范式的常态。要做的不是给常态打折，是把门槛删掉。** 这进一步支持 §2.1 的"减除建议"。

### 3.3 PPR 延迟回归 122 倍，且计划无延迟数值门槛

```
=== PPR 延迟实测（lore 层默认 max_iter=50, max_hops=2, max_edges=12）===
include_weak=False（现状）      P50=0.7ms    P95=1.0ms    max=1.0ms
include_weak=True（B1 修完后）  P50=85.8ms   P95=87.9ms   max=89.1ms
```

且 factor>0 时 **PPR 全部跑满 50 次迭代仍未收敛**（`tol=1e-6` 未达成，对比 factor=0.0 时平均 11.6 次收敛）。

注意两点：
1. 剧情层**当前已经** `plot_include_weak=True`，即**线上已经在付这笔 ~86ms/查询**；
2. 计划 §13 性能门禁只写"P95 延迟"四个字，**没有数值**。而 §12 也没有 `max_iter` / `tol` 的调整项。

**处置建议（同时也是性能优化，建议归入新阶段 S）**：
- **硬延迟门禁**：`graph_enabled=true` 下 `_graph_retrieve` P95 ≤ 30ms（建议值，需按你们的用户体验预算定）；
- **结构性优化（推荐，顺带消灭另一个 hack）**：**先用 `hop_distance`（BFS，毫秒级）取 `max_hops` 内的子图，再把 PPR 限制在该子图上运行**。实测 `max_hops=2` 的子图规模远小于全图。这样做有三重收益：① PPR 快一个数量级；② 天然收敛；③ **`personalized_pagerank` 与 `hop_distance` 的"过滤口径必须一致"这条例行 risk 直接消失**（计划多次为它写补丁）。
- 若保留全图 PPR：把 `tol` 放宽到 `1e-4`、`max_iter` 降到 20，先把运营成本压住。

### 3.4 P3 社区检测会在本图上退化为一个巨型分量

```
=== 连通分量分析（P3 的 detect_communities 第一步）===
有边实体 = 3327，孤立实体 = 1699 / 5026 = 33.8%
连通分量数 = 336
最大分量 = 2441 实体           ← 占全部有边实体的 73.4%
其余 335 个分量的规模 = 11, 8, 8, 7, …
```

计划 §8.1 的方案是"无向化连通分量 + 过大时用标签传播细分"，`graph_community_min_size=5`。在这个图上**实际只会得到"1 个 2441 实体的巨型社区 + 极少数小社区"**：

- 把 2441 个实体压缩成"top 度实体 + 高频 relation"再让 LLM 生成 **2–3 句摘要**（§8.1 `summarize`），语义上无意义；
- 计划 §1.5.4 已坦承"连通分量本身不消费边权、`len(evidence)` 只在标签传播阶段生效"——但 **`len(evidence)` 在 99.7% 的边上都恒等于 1**，标签传播实际是**无权传播**，结果不稳定且不可复现；
- `graph_community_max_summaries=3` 意味着最多只出 3 条摘要，而它们大概率全部来自同一个巨型社区。

**处置建议**：
- P3 开工前先做一次"社区可行性预检"：报告最大分量占比、标签传播的模块度/稳定性（多随机种子跑 5 次算一致性）；
- 若稳定性不达标，**要么引入 Leiden/louvain（会打破"零新依赖"约束，需显式决策），要么把 P3 从"社区摘要"降级为"按 relation 类型/时间切片的话题索引"**——后者在剧情/角色扮演语料上更贴合用户真正会问的"这段剧情讲了什么"这类问题；
- 无论如何不要在没有预检的情况下先写代码。

### 3.5 计划中存在的事实性错误（不影响方向，但会造成实施返工）

| # | 计划原文 | 实际情况 |
|---|---|---|
| E1 | §1.5.1 / §1.5.4 / §6.1：复用 `GraphStore.drop_source(ns, doc_id)`（`:427-446`） | **该方法不存在**。真实方法名是 `remove_by_doc(ns, doc_id)`（`graph_store.py:424-460`）。能力描述基本吻合。 |
| E2 | §1.5.4 / §6.1："B6 只需**接线**，不需新写" | 不成立。`memory_tier.prune()` 返回 `int`（条数），**不返回被删 doc id**；`vector_store.filter_remove()` 同样只返回计数。要在 KB prune 时清理图边，**必须先改这两个方法的返回签名**。 |
| E3 | §10 / §1.2：O9 "LLM 实例共享（单例）"待实现 | **已实现**。`factory.py:26-57` 的 `_GLOBAL_LLM_CACHE` 就是 provider 级单例，docstring 明确写了"避免每请求新建 AsyncClient 导致连接池/FD 泄漏"。该 O 子项应从清单删除。 |
| E4 | §1.2 D4 "BM25 缓存按命名空间清"待办 | 缓存 key **已经是** `(ns_tuple, version)`（`vector_store.py:338`），本就按命名空间隔离。真正的问题是反过来的：**`_bump_version`（:195-197）会清空所有命名空间的缓存**，导致 events 写一条就让 lore（2085 块）的 BM25 索引被丢弃重建。这才是要修的东西，计划写反了。 |
| E5 | §11："7 个 `.bak` + 3 个 `plot_cache_bak*`（约 15MB）" | 实际 `data/knowledge/` 下 **5 个** .bak 文件 + 3 个 bak 目录；另有 `data/characters/wu_ming_zhe.json.bak`（计划漏记）。合计约 **18.5MB**。 §11 说"先出清单，确认后再归档"，方向正确，建议按此执行、勿批量删除。 |
| E6 | §4.2 门禁"孤岛实体占比 ≤35%" | 剧情图实测 **33.8%**。门槛贴着现状设，几乎没有判别余量，建议重设为独立质量标准（如 ≤25%）而非照抄现状。 |
| E7 | `graph_search.py:217` vs `graph_ppr.py:40` | 都做"证据 <2 丢弃"，但一处硬编码 `2`、一处引用 `WEAK_EVIDENCE_MIN` 常量。<｜hy_place▁holder▁no▁813｜>口径不同源，是回归隐患。 |

### 3.6 ⚠️ 环境副作用告知：知识库嵌入状态曾被降级，核验过程已触发自动重嵌

**这一点需要你知道。** 我在核验 G0 可行性时跑了 `scripts/build_graph.py --character wu_ming_zhe --dry-run --limit 2`，log 输出：

```
知识库命名空间 lore_wu_ming_zhe 的嵌入器已变化（保存=hashing/768，
  当前=ollama:nomic-embed-text/768，样本维度=768），正在用当前嵌入器自动重建向量
（同样的消息出现在 lore_wu_ming_zhe_spoken / persona / web 四个命名空间）
```

**说明在你本次会话之前，`lore` 主知识库的向量是「hashing 兜底向量」而非 Ollama 语义向量**（推测是某次 Ollama 不可用时静默回退后被写死）。`KnowledgeBase._reembed_ns_if_needed` 检测到后自动全量重建，现已恢复：

```
lore_wu_ming_zhe        n=2085  dim=768   非零 768/768，L2=1.0000  → 真实语义向量 ✅
lore_wu_ming_zhe_spoken n=54            web n=42    persona n=1
区块数量与原文均未变化，只是向量被替换
```

文件变动：`data/knowledge/lore_wu_ming_zhe.json` 15.3MB → 24.7MB（真实 float 精度），`.kb_meta.json` 更新为 `{"embedder_name":"ollama:nomic-embed-text","embedder_dim":768}`，四个命名空间文件 mtime 同步更新。**这是恢复而非损坏，文本与分块完全没丢。**

由此得出一条**对 P4 至关重要**的风险（计划完全没提，见下条）。

### 3.7 🔴 由此新增的关键风险：A/B 两侧可能落在不同嵌入空间

上面的事故说明：**本项目知识库的嵌入器身份会在无人察觉的情况下漂移**（Ollama 抖动 → hashing 兜底 → 自动重写 → 语义检索静默降级；恢复时再自动重建）。而计划 §9 P4 的全部判据建立在"基线 vs 图谱臂"的对比上。

这意味着一个真实且很可能发生的失败模式：**基线是在 hashing 退化态下测的、图谱臂是在 Ollama 恢复后测的，测出来的"图谱提升"其实是"嵌入器恢复"**。这正好命中 ML Digest 点名的行业通病：

> *"Start with a strong vanilla RAG baseline… A surprising number of 'GraphRAG wins' in practice turn out to be **wins over a weak baseline**, not over a well-engineered dense retrieval system."*

同时这也给现有基线数据打了个问号：`deliverables/rag-eval-standard.json`（Sep 1，faithfulness 0.712）是否也是在退化的检索器上测的——**很可能，但在拿到当时的 `.kb_meta.json` 之前无法证实。**

**处置建议（必须进 P4 前置检查表）**：
1. eval 脚本启动/结束时**断言并记录** KB 嵌入器身份与 `_kb_meta` 内容，写入报告头部；
2. A/B **双臂必须在同一次运行、同一个 KB 状态下采集**（不要分两次命令行跑）；
3. 增加"嵌入器一致性门禁"：`.kb_meta.json` 的 `embedder_name/dim` 与当前运行时不一致 → **直接报错退出**，不要静默自动重建（当前行为是静默救 + 静默改数据，风险大于收益）；
4. 采基线和采图谱臂之间插入一次 `kb.version` 与 fingerprint 校验。

---

## 4. 阶段划分与排期评估

### 4.1 计划从未给出总工时合计 — 补上后与"收尾专项"的定位有落差

按 §3 阶段表累加：

| 阶段 | 计划耗时 |
|---|---|
| W | 0.5d + L1 扫描 0.5d |
| G0 | 机器 1~2.5h + 人工 0.5d |
| R | 1d |
| P2 | 1.5d |
| A | 0.5d |
| P3 | 2d |
| P4 | 1.5d |
| O | 1d |
| M | 0.5d |
| **小计（工程）** | **9.5d** |
| 标注/盲评人工（§3 补） | 1.5–2.5d |
| **合计** | **11–12 人日（单人）** |

对一个已经标明"不含提示词 P1、语音模块、前端重构"的**收尾专项**来说，11–12 人日偏重。结合 §2.1 的减除建议（撤 W 的 ≥1d）和 §3.5 的错勤 deliveries（撤 O9，修正 D4），实际可压缩到 **9–10 人日**，但仍建议拆成两个 PR 批次而不是一口气做完。

### 4.2 G0「机器 1~2.5h」偏乐观，且当前存在未修复的抽取失败

实测 `--dry-run --limit 2`：**2 块里 1 块返回 `null`（50% 失败率）**，并复现了前序审计已记载、至今未修的 bug：

```
图谱抽取失败：Event loop is closed      # 与 deliverables/rag-graphrag-audit-20260908.md:369
                                        #   记载的 "RuntimeError: Ollama 嵌入调用失败：Event loop is closed" 同源
```

（样本极小，不能据此得出 50% 的结论，但足以证明该失败路径**当前是活的**。）

用计划自己的参数反推排期：`graph_extract_batch` 建议降到 4，单块 20–30s → `2139 / 4 × 25s ≈ 3.7h`；算上失败重试与 `--limit` 分批的人工巡检，**建议按 4–6h 排**，而不是 1–2.5h。

另外 §4.2 要求"抽取失败率 <10%"，但**修复上述 Event-loop 问题不在 G0 的步骤清单里**，按现状直接全量很可能过不了自己的门禁。**建议把"修复 Ollama 事件循环 / `_run_async` 复用"作为 G0 的前置 item #0。**

### 4.3 其余排期问题

| # | 问题 | 建议 |
|---|---|---|
| C1 | **P4 在推荐顺序里出现两次**（P4 采基线 / P4 A/B 复跑），预算只给 1.5d 一次 | 拆成 P4a（采基线+冻结探针，0.5d）与 P4b（A/B+报告，1d）分别列支 |
| C2 | **阶段 O 塞了 O1–O9 共 8+ 个子项，只给 1d**；其中 O1（向量 `array('f')` 迁移）自带"旧库兼容 + fingerprint 联动 + 迁移方案"，单项就不止 1d | O 拆为 O-core（O2/O3/O4/O7/O8，纯优化，~0.5d）与 O-migrate（O1/O5/O6，需迁移方案，~1.5d），后者可延后 |
| C3 | W 声称 0.5d+0.5d，但产物是平坦曲线（§2.1） | 撤 Wall；仅保留 L0 等价性测试 + 空结果计数器（≈0.5d） |
| C4 | `--preserve-conversation`（§6.1 B7）与 §4.1"改 `entity_aliases` 后重跑构建"的交互未定义 | 补一条：`entity_aliases` 变更 → 必须走 `--rebuild --preserve-conversation`，并给出验收 "conversation 边数不变" |
| C5 | 阶段 R 的 R3（top_k 2→4）由 P4 裁决，但 §1.6.4② 已正确要求它独立跑第三臂——两条没串起来 | §9.4 决策门的 `top_k` 行已写了"独立裁决"，但 §9.1 实施清单第 3 条仍写"同一套 A/B 增加 top_k=2 vs 4（叠加 R1/R2）"，**这条原文应删除**，否则实施时会照着冲突的写法做 |

---

## 5. 依赖与资源评估

| 资源/依赖 | 状态 | 是否满足 |
|---|---|---|
| Ollama 服务 | 在线，`qwen2.5:7b`(Q4_K_M, 4.7GB) + `nomic-embed-text`(274MB) | ✅ |
| CPU | 20 线程（i7-13650HX 档） | ✅ 可支撑 batch 4–8 离线抽取 |
| 抽取可用性 | **存在未修的 `Event loop is closed` 失败路径** | ❌ G0 前置阻塞 |
| 知识库嵌入状态 | **会静默漂移 hashing ↔ ollama**（已实际发生一次） | ❌ P4 前置阻塞 |
| lore 图谱文件 | **不存在**（`graph_wu_ming_zhe.json`） | ⚠️ G0 是硬前置，计划已正确识别 |
| 剧情图谱 | 5026 实体 / 4261 边 / 2.1MB，可用作 PPR 实验替身 | ✅ |
| 全量测试基线 | 562 passed / 1 skipped / 0 failed | ✅ |
| Git 仓库 | **零提交** | ❌ 阻塞所有 tag/版本化/回滚条款 |
| `tests/fixtures/` | **目录不存在** | ⚠️ L2 探针集路径需新建（小事） |
| `data/knowledge` 体积 | 46MB（含 ~18.5MB 备份）；lore 向量内存实测 49MB | ✅ 资源充裕，O1 收益真实（49MB→6MB） |
| cross-encoder 重排序（A2 降级项） | 未引入 | ✅ 降级理由显存/仄赖冲突、且要求"P4 不达标再评估"，裁定合理 |
| 517 Jupyter/Anthropic 云 judge | 未引入 | ⚠️ §2.3 建议补一个可配置的 judge 出口 |

---

## 6. 遗漏项清单（计划之外，但不可不做）

| 编号 | 遗漏项 | 优先级 | 建议归属 |
|---|---|---|---|
| M1 | **relation 词表治理**（§3.1）：限定词表 + 已建边离线归一 + 谓语卫生过滤 + G0 增加 relation 卫生门禁 | 🔴 最高 | 新阶段 S-1，**必须排在 G0 全量之前** |
| M2 | **KB 嵌入状态锁定 + A/B 同状态断言 + 自动重建改为显式报错**（§3.7） | 🔴 | P4 前置检查表 |
| M3 | **judge 模型解耦 + judge-to-human kappa 校准**（§2.3） | 🔴 | P4 前置检查表 |
| M4 | **faithfulness 基线修复路径**（0.712 → ≥0.80），否则 P4 死锁（§2.2） | 🔴 | 新阶段 P3.5，或重设为"不低于复测基线" |
| M5 | **PPR 性能优化：先 BFS 取 max_hops 子图再做 PPR + 硬延迟门禁**（§3.3） | 🟠 | 新阶段 S-2；顺带消灭 pagerank/hop_distance 口径一致性补丁 |
| M6 | **首次 git 提交**，否则所有 tag/回滚/冻结条款失效（§2.4） | 🔴 | 第 0 件事 |
| M7 | **修复 `Event loop is closed` 抽取失败**（§4.2） | 🔴 | G0 前置 item #0 |
| M8 | **lore 层 relation 长度/黑名单过滤**（P2 只对对话边做了 `predicate >8 字`，lore 层没有） | 🟠 | 并入 S-1 |
| M9 | **总 token 预算上限**：新增四路注入后总上下文无硬上限，角色扮演场景会因上下文膨胀导致人设崩（计划只设了各分块预算） | 🟠 | R 阶段增加总量闸 |
| M10 | **P3 社区可行性预检**（§3.4）：不做就写 P3 代码，大概率返工 | 🟠 | P3 门禁前置 |

---

## 7. 审计结论与处置建议

### 结论：**有条件通过（Conditional Go）**

**计划的问题不在方向，在于它花了最多力气的地方产出为零，而真正决定成败的三件事它一件都没排。**

批准执行的前提是完成以下结构调整：

**A. 做减法（砍掉 ~1.5d 无效工作）**
1. 删除 `weak_edge_factor` / `graph_conversation_weak_edge_factor` / `plot_weak_edge_factor` / `undirected_evidence` 四个配置项；
2. 删除阶段 W 的 W2/W3/W5 与 L1 参数扫描（实测必然产出平坦曲线）；
3. B1/B2 改由 **`graph_include_weak=True` + 展示层 `0.5` 折扣 + 空结果计数器** 一条路径解决（剧情层已在跑，零新发明）；
4. 保留 W1（L0 等价性测试）与 W4（空结果计数器），这两个是真正有价值的。

**B. 做一个首次 Git 提交**（否则整份计划的版本化/回滚/tag 都是纸面条款）。

**C. 新增"阶段 S：检索前置治理"**，排在 G0 之前，包含：
- S-1 relation 词表治理（最高杠杆，见 M1/M8）
- S-2 PPR 子图化性能优化 + 硬延迟门禁（见 M5）
- S-3 抽取 Event-loop 修复（见 M7）

**D. 重设 P4 判据，并补"可达性验算"一节**：
- Faithfulness 绝对门槛要么改为"不低于复测基线"，要么单列 P3.5 先把 0.712 拉过 0.80；
- multi-hop 探针从 9 条扩到 ≥30 条并重新分布难度（当前 5/9 已满分的分布没有判别空间）；
- 明确说明 §1.6.4③ 的 0.80 是否降低了脚本原门槛 0.90。

**E. 给 P4 加三条前置检查（缺任一不许开跑）**：
1. judge 与生成器不同源 + judge-to-human kappa ≥ 0.6；
2. KB 嵌入器身份在双臂一致，且已关闭静默自动重建；
3. G0 的检索烟雾测试非空率达标，且空结果计数器已上线可观测。

**F. 事实纠错**：把 §1.5/§6.1 的 `drop_source` 改为 `remove_by_doc`，并明确 B6 需要改 `filter_remove`/`prune` 的返回签名；O9 从清单删除；D4 改为修正"`_bump_version` 全清缓存"的真实问题；§9.1 第 3 条与 §1.6.4② 的 `top_k` 冲突原文删除；.bak 数量按实测（5 文件 + 3 目录，另漏 characters 下 1 个，合计 ~18.5MB）订正。

**G. P3 先做可行性预检**（ §3.4），预检不通过就降级为"按 relation 类型/时间切片的话题索引"，不要硬上连通分量。

### 修订后的推荐顺序

```
#0  git 首次提交（建立 lineage）
S   S-1 relation 词表治理 ‖ S-2 PPR 子图化+延迟门禁 ‖ S-3 抽取 Event-loop 修复
       └→ 并行：R（查询改写 + 跨路去重，与图谱无关）
G0  lore 全量构建（4–6h）+ 增强验收（含 relation 卫生门禁 + 检索烟雾测试）
P3.5（可选分支）faithfulness 基线修复 → 若选此路则 P4 保留 0.80 绝对门槛
P4a 冻结探针集 v1 + 采基线（同状态断言）
P2 → A → P3（P3 前先过社区可行性预检）
P4b A/B 复跑 + O-core → O-migrate（可选）→ M
```

### 一句话禀报给你

这份计划的**代码核验准确度是我见过的高水平**（§1 核验表的 23 条断言逐一对得上，包括 D7/D11/D12 三处顶住外部评审的正确驳回），唯一的硬伤是掉进了一个**"一行配置被写成一整个阶段"的陷阱**：它本质是"`include_weak` 从 False 改成 True"，却被包装成了"权重化 + 参数扫描 + 五层测试 + 人工盲评"的完整阶段。我在真实图谱上证明了这个旋钮数学上近乎无效。真正该做的是三件脏活：**约束 relation 词表（1564 个谓语里有 72% 只出现一次，垃圾谓语已经进了提示词）、锁死知识库嵌入状态（已经静默漂移并被我触发了一次重建）、把 judge 从被测模型身上摘下来**。

---

## 附录：可复现的实验脚本

以上所有数字均可复现，脚本留在 `tmp_pytest/`：

| 脚本 | 产出 |
|---|---|
| `tmp_pytest/pprexp.py` | factor 扫描 / factor=0.0 严格等价性 / undirected_evidence 无效性（§2.1） |
| `tmp_pytest/pprexp2.py` | PPR 延迟实测 / 度分布 / 连通分量分析（§3.3、§3.4） |
| `tmp_pytest/relexp.py` | relation 词表碎片化分析 / 近义谓语聚类 / 合并后证据分布（§3.1、§3.2） |

验证命令（在项目根目录）：
```bash
python -X utf8 tmp_pytest/pprexp.py
python -X utf8 tmp_pytest/pprexp2.py
python -X utf8 tmp_pytest/relexp.py
```
