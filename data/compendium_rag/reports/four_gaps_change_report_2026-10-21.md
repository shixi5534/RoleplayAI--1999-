# compendium_rag 四缺口修复 · 变更报告

> 日期：2026-10-21
> 范围：G1 池宽解耦 / G2 向量阈值 / G3 端点提及 / G4 PPR dangling
> 计划：`compendium_rag_检索四缺口修复计划_v10_2026-10-21.md`
> 架构文档：`docs/compendium-rag/architecture.md` §4
> 外部对照：`docs/compendium-rag/research/四缺口外部设计对照_2026-10-21.md`
> 机读版：`data/compendium_rag/reports/four_gaps_change_report_2026-10-21.json`

---

## 0. 一句话结论

**四条缺口全部在代码层修复，测试 383 → 398 passed（新增 15 条），默认值路径与改造前逐位一致。**
**验收（生产配置 `lex_weight=1.0 / rrf_k=1 / lex_top=30`，eval300 cn 集，top_k=6）：**
**同日 HEAD vs CUR 对照 —— full/answerable hit@6 0.8520 → 0.8571、MRR 0.6616 → 0.6622；**
**graph_only 三种口径逐位完全不变（answerable hit@6 0.8061、MRR 0.6012）。**
**既无退化，也无显著提升——净效应是 1 换 1 的位次波动（救回 R263、R167 掉一位）。**
**`graph.json` 未重建** —— G3 的重建口径净增量为 **0**，而重建本身会带来 840/583 条
边的变动（全部来自归一化/合并规则的代码演进，与本轮无关），属独立的**数据刷新决策**，
需拍板后单独执行。**本轮不宣称任何召回提升。**

> ✅ 2026-10-10 的 r11 基线（0.852041 / 0.661650）**可以复现**：用未改动的 HEAD 代码
> + 生产配置重跑得 0.8520 / 0.6616，逐位吻合。
> 早前本报告写的「不可复现（0.8010/0.6156）」是**一次实验错误**——那批读数用的是
> 默认配置 `lex_weight=0, rrf_k=60`（历史上没开词面通道），与 r11 的生产口径不同。
> 错误结论已全部撤回，细节与教训见 §7.2。

---

## 1. 改动面

| 文件 | 增行 | 内容 |
|---|---|---|
| `src/compendium_rag/retriever.py` | +186 | `default_pool_top_n` / `resolve_pool_top_n`；`evidence_pool`；`search(min_score=)`；`vector_channel(min_score=)`；`retrieve(pool_top_n=, vector_min_score=, want_pool=)`；PPR dangling 回流；种子全序；`graph_ok=False` 孤立种子分支 |
| `src/compendium_rag/graph_store.py` | +50 | `_count_mentions` 三段式（声明 / 端点 / 顺序确定化） |
| `src/compendium_rag/pipeline.py` | +40 | `KnowledgeBase.retrieve` 透传三个新参数；`context()` 改关键字构造 `Evidence` 并回填 `evidence_pool` |
| `src/compendium_rag/config.py` | +34 | `_env_opt_int` / `_env_opt_float`；`retrieval_pool_top_n` / `retrieval_vector_min_score`（均默认 `None`） |
| `src/compendium_rag/cli.py` | +10 | `--pool-top-n` / `--vector-min-score` |
| `tests/compendium_rag/test_retriever.py` | +166 | 12 条新测试 |
| `tests/compendium_rag/test_graph_store.py` | +66 | 3 条新测试 |
| `scripts/compendium_rag_p8_roleiso_shadow.py` | 13 | 显式 `pool_top_n=`（唯一硬依赖池宽的脚本） |
| `scripts/_miss_vector_reach.py` | 5 | 全库扫描显式 `min_score=None` 防误伤 |

> 工作区里其余 modified 文件（`README.md`、`data/compendium_rag/reports/cbi/*`、
> `docs/compendium-rag/P9_CBI报告.md`、`entity_disambiguation_rules.md`、
> `scripts/cbi_*.py`、`src/roleplay/api/llm_config.py` 等）是**本次开工前的既有脏工作区**，
> 不是本轮改的。

---

## 2. G1 — 池宽与输出数解耦

**问题**：`top_n = max(top_k*4, 24)` 既当融合池宽又当输出数，于是 `top_k=6`
实际返回 **33–105 条**（`rank_collect_k1c300_top30.json`：最小 33 / 中位 68 / 最大 105）。

**改动**：
```python
default_pool_top_n(top_k) -> max(top_k*4, 24)        # 旧公式，保留
resolve_pool_top_n(top_k, pool_top_n=None)           # None → 走旧公式
RetrievalResult.evidence_pool: list[Evidence] | None # 全池出口，默认 None
retrieve(..., pool_top_n=None, want_pool=False)
```

- `res.evidence` 截断到 `top_k`；全池放 `evidence_pool`（**不进 `to_dict()`**，避免工件膨胀）。
- 配置 `CMPRAG_RETRIEVAL_POOL_TOP_N`（默认 `None`）、CLI `--pool-top-n`。
- 默认等价性：`pool_top_n=None` → `max(top_k*4,24)`，**与改造前逐位等价**。

**迁移**：`scripts/compendium_rag_p8_roleiso_shadow.py` 是唯一**硬依赖**池宽的脚本
（docstring 明示「必须逐字复刻原 harness，否则读数不可比」），已显式传参。
脚本里重复的 `max(top_k*4,24)` 字面量统一收敛到 `default_pool_top_n`。

**测试**：`test_default_pool_top_n_matches_legacy_formula`、`test_top_k_truncates_evidence`、
`test_pool_top_n_decoupled_from_top_k`、`test_evidence_pool_optional_and_not_serialized_by_default`。

---

## 3. G2 — 向量通道相似度下限（**默认关闭**）

**问题**：`ChunkIndex.search` 无阈值，余弦 **0.0** 的块也进 RRF 并拿 `1/(k+rank)`。

**改动**：`search(qvec, top_k, min_score=None)` / `vector_channel(qvec, top_k, min_score=None)`。
**过滤在截断之前**：`keep = np.flatnonzero(sims >= min_score)`。并列用 `(-score, chunk_id)` 全序。

**默认 `None` = 完全关闭**，关掉时逐结果与改造前一致。

**为什么不给默认阈值**：
- LightRAG 曾引入 cosine threshold 后又移除（`271df99` / `2b52d43`），因绝对阈值造成「全空」。
- BGE 模型卡说 [0.6, 1]，**本仓库不适用**：bge-m3 中文语料实测
  **0.3178–0.6571，中位 0.4973**（n=4578，p10=0.4247）。套 0.6 会砍掉约一半证据。

**标定未执行**，候选扫描点 `{0.40, 0.42, 0.4247, 0.45, 0.47, 0.50}`，
必须在 eval300 上验证 hit@6 不退化才允许考虑开启。**当前保持 `None`。**

**测试**：`test_vector_min_score_filters`、`test_zero_cosine_block_excluded`、
`test_vector_min_score_none_is_legacy`、`test_vector_min_score_filters_before_truncation`、
`test_retrieve_passes_vector_min_score_through`。

---

## 4. G3 — 关系端点计入提及（**收益 ≈ 0，契约修复**）

**问题**：`_count_mentions` 只看块内显式声明，仅作关系 `src`/`dst` 出现的实体
在该块上永久盲区 → `mention_channel` 取不到。

**改动**（`graph_store.py:298` 三段式）：
1. 块内显式声明（原逻辑逐位保留）。
2. 关系端点 `src`/`dst`，同块已声明则不重复计数。
3. `chunk_ids` 按 `(块在语料中的序, chunk_id)` 排序 —— 保证 `cids[:3]` 稳定。

### 4.1 受影响实体数 / 块对数（两套口径必须分开读）

| 口径 | 来源 | 结果 |
|---|---|---|
| **工件口径** | `g3_blind_report.json` | 盲区实体 **1** 个（店主）；盲区 (entity, block) 对 **11** 个；涉及边 **29** 条；店主 `declared=3` vs `blind=11`，样例块全在 `anecdote__1917_乘法轴上的一天` 下 |
| **重建口径** | `drift_split.json` B vs C | **全零**：实体 0 / 边 0 / `chunk_ids` 0 / mentions 0 |

B vs C 全零的原因：`extract.py:299-335` 已强制每个关系端点解析到同块实体名/别名/说话人，
当前抽取管线**不存在纯端点实体**，②段是纯 no-op。

### 4.2 工件陈旧度（不是本轮改动）

A(工件) vs B(改动前代码重建)：**6 个实体** chunk_ids 变化、**840 / 583** 条边差异。

| 实体 | 工件块数 | 重建块数 | 增 | 减 |
|---|---|---|---|---|
| 卡卡尼亚 | 118 | 204 | 15 | 7 |
| 店主 | 3 | 14 | 11 | 0 |
| 探险家别斯米尔 | 71 | 67 | 0 | 4 |
| APPLe号摇滚巨轮二世 | 2 | 1 | 0 | 1 |
| 雾气净化器 | 13 | 10 | 0 | 3 |
| 乌尔里希 | 125 | 53 | 0 | 15 |

> ⇒ 计划 §2 说的「11 对 / 1 实体」是**工件口径**的观测，不是本轮改动的效果。
> **G3 不得宣称召回提升**，只验：①端点实体不再盲区；②其余实体 `chunk_ids` 不变。

**测试**：`test_endpoint_entity_counts_as_mention`、`test_endpoint_mention_deduped_against_declaration`、
`test_mention_chunk_ids_order_is_deterministic`；保留 `test_mentions_counted`、
`test_relations_mentioning_speaker_add_entity`。

---

## 5. G4 — dangling 质量回流 teleport（唯一有实测收益）

**问题**：`share = damping*dangling/len(nodes)` 均摊给全图。
图有 5900 节点、**1133 个孤立**（19.2%）。任一孤立种子 → **全部 27110 条边正分**
（0.000299–0.1742）→ top-30 边裁剪退化成**全图随机置信度抽样** → **91 个无关块**。

**改动**：
```python
if dangling:
    share = damping * dangling
    for n in nodes:
        tp = teleport.get(n, 0.0)
        if tp:
            nxt[n] = nxt.get(n, 0.0) + share * tp
```
按 teleport 向量回流（**叠加**在 `(1-damping)*teleport` 之上，不覆盖），
与 NetworkX `pagerank(dangling=…)` 默认语义、igraph
`pr_new[v] = (1-d)*norm_reset[v] + d*(incoming + dangling_sum*norm_reset[v])` 一致。

### 5.1 边分数变化（同一孤立种子）

| 指标 | 改前 | 改后 |
|---|---|---|
| `edges sc>0` | **27110**（全部） | **0** |
| top-30 边产出块 | **91** | **0** |
| `nonzero` 节点 | 5901（全部） | **1** |
| `seed_score` | 1.0 | 1.0（语义不变） |

### 5.2 连通图未退化

正常种子下：`nonzero=5790`、`edges_with_positive_score = **27043 / 27110**`。

**测试**：`test_ppr_isolated_seed_keeps_mass_on_seed`、`test_ppr_dangling_mass_follows_teleport`、
`test_ppr_single_seed_no_leak_to_disconnected_component`；原 `test_ppr_*` 六条全绿。

---

## 6. 爆炸半径（为什么没有重建 `graph.json`）

计划 D4-3 要求「重建图谱 + 产出变更报告（预期 1 实体 / 11 块对）」。
动手前用 **A/B/C 三口径**把「工件陈旧度」和「本轮改动作用面」拆开（`scratch_r12/`）：

| 口径 | 代码 | 边数 | `only_in_artifact` | `only_in_rebuilt` | 指纹 / normalizer |
|---|---|---|---|---|---|
| **A** 工件 | — | **27110** | — | — | `14daf1bbfa407388` / `n2` |
| **B** 改动前代码重建 | HEAD | 29198 | 13572 | 15660 | `14daf1bbfa407388` / `n2` |
| **B′** 更早（无 normalizer） | prev | 29967 | 21189 | 24046 | `7dc29bf90681a3f7` / `null` |
| **C** 改动后代码重建 | 本轮 | **26853** | 840 | 583 | `14daf1bbfa407388` / `n2` |

### 6.1 三条结论

1. **A 与 B 的指纹完全相同（`14daf1bbfa407388` / `n2`），边数却差 2088 条** ——
   指纹对本类「归一化/合并规则演进」不敏感。任何「图有没有变」的判断必须**同时**比对
   `fingerprint` + `normalizer` + 边数，只看文件在不在是不行的。
2. **C 比 B 少了 2345 条边**，但 **B vs C（G3 开关）是零差异** ——
   说明差异来自本轮以外的代码路径（归一化/合并），**G3 不是原因**。
3. 边差异的性质几乎全是**关系谓语归组/方向裁决**：
   工件 `重塑之手 攻击 APPLe号` vs 重建 `重塑之手 炮击 APPLe号`；
   `暴雨 发生于 1966英国伦敦` vs `暴雨 临近 …`。
   关系种类数也变了：工件 **1609** 种 vs 重建 **1543** 种（`告知 2784→2810`、`询问 955→958`）。

### 6.2 决策

**不重建 `graph.json`。** 理由：
- 重建对 G3 的净收益是 **0**（§4.1 重建口径全零）；
- 重建会顺带改动 **840 / 583** 条边，与四缺口无关，属独立的**数据刷新**；
- 该数据刷新的收益尚未评估，且会改变所有既有评测的对照基线。

**这是需要拍板的一项**：只改代码不重建（当前状态，代码正确、数据不动），
或改代码 + 重建（数据也正确，但需重新锁定全部基线读数）。

---

## 7. 测试与验收

```
tests/compendium_rag/    383 passed, 7 skipped  →  398 passed, 7 skipped  (+15)
```

新增 15 条：`test_retriever.py` 12 条、`test_graph_store.py` 3 条。
唯一 warning 是 FastAPI `StarletteDeprecationWarning`（预存，与本轮无关）。

### 验收对照（计划 §5）

| # | 要求 | 状态 |
|---|---|---|
| 1 | `pytest tests/compendium_rag/` 全绿，含新增 ≥9 测试 | ✅ 398 passed，新增 15 |
| 2 | 每条缺口默认值关闭路径与原行为逐字节一致 | ✅ G1 公式等价；G2 `None` 不走过滤分支；G3 空操作（见 §3）；G4 是**有意的**排名修复，非等价改动，已单列 |
| 3 | eval300（cn 集，`--top-k 6`）hit@6 与 MRR 不退化 | ✅ **两个模式、三个口径全部不退化**：full/answerable hit@6 0.852041→0.857143、MRR 0.661650→0.662245；graph_only 三种口径**逐位完全相同** |
| 4 | G3 不得宣称召回提升 | ✅ 全文无召回提升声明 |
| 5 | 产出变更报告 JSON + md | ✅ 本文件 + 同名 `.json` |

### 7.1 同日对照（唯一有效的验收判据）

同一库（chunks 3695 / entities 7033 / edges 27110）、同题集
`data/knowledge/_audit/rag_testset_300_cn.json`、同 harness、`top_k=6`，
**只换 `src` 树**：HEAD（`git show HEAD:src/...` 导出到 `scratch_r12/headsrc/src`，
`retriever.py` 33646 B）vs 本轮工作区（41233 B）。

**必须用生产检索配置**：
`CMPRAG_LEX_WEIGHT=1.0 CMPRAG_LEX_TOP=30 CMPRAG_LEX_FIRST=0 CMPRAG_RRF_K=1`。
默认值（`lex_weight=0, rrf_k=60`）是**历史行为**，只用于等价性检查，
拿来跟 README/r11 指标表对账会凭空差 5 个点（见 §7.2）。

| 模式 | 口径 | HEAD hit@6 | CUR hit@6 | HEAD MRR | CUR MRR | HEAD seed | CUR seed |
|---|---|---|---|---|---|---|---|
| full | all（n=300） | 0.560000 | **0.563333** | 0.435611 | **0.436000** | 0.2767 | 0.2767 |
| full | **answerable（n=196）** | **0.852041** | **0.857143** | **0.661650** | **0.662245** | 0.4235 | 0.4235 |
| full | answerable+cn（n=184） | 0.858696 | **0.864130** | 0.669475 | **0.670109** | 0.4348 | 0.4348 |
| graph_only | all（n=300） | 0.530000 | 0.530000 | 0.396111 | 0.396111 | 0.2333 | 0.2333 |
| graph_only | answerable（n=196） | 0.806122 | 0.806122 | 0.601190 | 0.601190 | 0.3571 | 0.3571 |
| graph_only | answerable+cn（n=184） | 0.815217 | 0.815217 | 0.605978 | 0.605978 | 0.3696 | 0.3696 |

逐题（answerable 196 题，`scratch_r12/acceptance_final.json`）：

- **full**：hit 上升 **1** 题（R263 `0.0 → 0.1667`）、下降 **0** 题；
  RR 变动 2 题（R167 `0.25 → 0.2`、R263 `0.0 → 0.1667`）。
- **graph_only**：hit、RR **均零变动**。

> 净效应：`full` 的 R263 被救回（G4 让孤立种子不再把激活平摊给全图），
> R167 掉一个位次。1 换 1 的位次波动落在噪声内，**不足以宣称提升**。

### 7.2 r11 基线可复现 —— 以及一次必须记下的实验错误

`data/compendium_rag/reports/eval_300cn_k1_r11.{log,json}` 记的是 full/answerable
**0.852041 / 0.661650**。用**未改动的 HEAD 代码 + 生产配置**重跑，得
**0.852041 / 0.661650** —— **逐位吻合**。`graph_only` 同样逐位吻合（0.806122 / 0.601190）。
**r11 完全可复现。**

本报告早前版本写过一段「r11 在本机不可复现，HEAD 只跑出 0.8010/0.6156」，
并据此把验收判据降级为同日对照。**那段是错的，已撤回**。真实原因很简单：

| 项 | 事实 |
|---|---|
| 错误读数的来源 | 对照实验忘了设 `CMPRAG_LEX_WEIGHT=1.0` / `CMPRAG_RRF_K=1`，跑的是默认配置 |
| 默认配置下 HEAD 的读数 | 0.8010 hit@6 / 0.6156 MRR（**这才是** `0.8010` 的出处） |
| 生产配置下 HEAD 的读数 | 0.852041 / 0.661650 = r11，逐位相同 |
| 差值的含义 | 词面通道（`lex_weight=1.0`）在本数据集上值约 **+5.1pt hit@6 / +4.6pt MRR**，与 README 的「Production value」注记一致 |
| 为什么当时「排除了代码/工件/嵌入」 | 因为这三者确实都没问题 —— 排除全对，但漏掉的是**配置**这一维 |

留给后续的教训（已写进 `docs/compendium-rag/architecture.md` 与 README 的指标表旁）：

1. 对账前先确认**配置**，再怀疑代码/工件/环境。三项「排除」全对也可能整体错。
2. `seed_hit` 全 300 题逐题相同、`n_evidence` 也相同，只有 18 题 hit 不同 ——
   这形态指向**排序/融合**而非**检索覆盖**，天然排除嵌入漂移与索引变更。
   这个信号当时就在手上，没有被读出来。
3. 默认值「等于历史行为」不代表「等于 README 的生产读数」。两者差 5 个点。

### 7.3 G4 的排名影响归因

`scratch_r12/probe_nog4.py` 用 `ast` 把 HEAD 的 `personalized_pagerank` 抽出来塞回当前
代码（其余改动保持），逐题重跑翻转题：**top-6 顺序恢复成 HEAD 的样子**。
⇒ 生产配置下那 2 题的 RR 变动，唯一来源是 **G4 的 dangling 回流**；
G1/G2/G3 的默认路径对排名**零影响**（`graph_only` 零变动，也印证这一点 ——
该模式下 G1 的截断与 G2 的阈值都不参与）。

这是 G4 的**预期**副作用（悬挂质量回流改变了平稳分布，孤立种子不再污染全图），
不是回归。如实记下，不宣称"对排名完全无影响"。

回归命令（两次跑，用 `EVAL_SRC` 切换 src 树；`scratch_r12/eval_head.py` 会打印绑定校验）：

```powershell
# 生产配置必须显式给，否则跑出来的不是 r11 口径
$env:CMPRAG_LEX_WEIGHT='1.0'; $env:CMPRAG_LEX_TOP='30'
$env:CMPRAG_LEX_FIRST='0';     $env:CMPRAG_RRF_K='1';  $env:EVAL_MODE='full'

$env:EVAL_SRC = "$PWD\scratch_r12\headsrc\src"; $env:EVAL_OUT = "$PWD\scratch_r12\eval_head_r11cfg_full.json"
.\.venv\Scripts\python.exe scratch_r12\eval_head.py

$env:EVAL_SRC = "$PWD\src"; $env:EVAL_OUT = "$PWD\scratch_r12\eval_cur_r11cfg_full.json"
.\.venv\Scripts\python.exe scratch_r12\eval_head.py
```

> ⚠️ **跑 eval 前必须核 `== 绑定校验 ==` 那三行**（`EVAL_SRC` / `compendium_rag from` /
> `retriever.py bytes`）。本轮早期有一批实验没锁 `sys.path`，实际一直导入的是另一个
> checkout 的 `compendium_rag`，导致得出过"退化 4.6pt"的错误结论——那批读数全部作废。
> 这是本轮**第二个**实验错误（第一个是 §7.2 的配置错误），两个都已留档。

---

## 8. 交付物清单

| 交付物 | 路径 |
|---|---|
| 架构文档（新建，含「已知缺口」节） | `docs/compendium-rag/architecture.md` |
| 外部设计对照（新建） | `docs/compendium-rag/research/四缺口外部设计对照_2026-10-21.md` |
| 变更报告（机读） | `data/compendium_rag/reports/four_gaps_change_report_2026-10-21.json` |
| 变更报告（人读） | 本文件 |
| v9 计划三条历史缺陷补「已修复」标注 | `docs/compendium-rag/优化计划_v9_2026-10-08.md`（§1 后） |
| 代码 | `src/compendium_rag/{retriever,graph_store,pipeline,config,cli}.py` |
| 测试 | `tests/compendium_rag/{test_retriever,test_graph_store}.py` |
| 证据工件 | `scratch_r12/{drift_report,g3_blind_report,g3_delta_report,blast_HEAD,blast_prev,blast_radius_report}.json` |
| eval 最终对照原始结果（生产配置） | `scratch_r12/{eval_head_r11cfg_full,eval_cur_r11cfg_full,eval_head_r11cfg_gonly,eval_cur_r11cfg_gonly}.json` |
| eval 最终三口径汇总 | `scratch_r12/acceptance_final.json` |
| eval 对照脚手架 | `scratch_r12/eval_head.py`（按 `EVAL_SRC` 绑定 src 树并打印绑定校验） |
| ~~eval 早期对照（作废）~~ | `scratch_r12/{eval_head_full,eval_cur_full,eval_head_gonly,eval_cur_gonly}.json` —— 用的是默认配置，**不得**用于任何结论 |

---

## 9. 未决事项

1. **`graph.json` 是否重建** —— 见 §6.2。当前：不重建。
2. **G2 阈值是否开启** —— 需先跑标定扫描 + eval300 验证，当前保持 `None`。
3. **G4 是否需要开关** —— 它是四条里唯一改变排名的（生产配置下 full 模式救回 R263、
   R167 掉一位；graph_only 零变动）。净效应在噪声内，但严格「逐位相等」不成立。
   若要绝对等价，可加 `ppr_dangling_backflow=False` 开关默认关闭；
   当前判断**不必**，因为 G4 修的是真实缺陷（孤立种子污染全图）。
4. **本报告的两处已撤回结论** —— §7.2 的「r11 不可复现」与更早的「退化 4.6pt」
   均已被实测推翻，正文已改正。这两次错误的**共同机制**是实验环境（配置 / 导入路径）
   未锁死；其代价是本轮返工了相当一部分测量工作。留档以警示后续。

