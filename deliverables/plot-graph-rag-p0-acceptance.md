# 剧情图谱 RAG —— P0 验收报告（M-12 数据源自动生成）

> 生成器：`scripts/report_p0_acceptance.py`（所有数字取自 `data/knowledge/_audit/` 下的 JSON 物证，**无手抄**）｜主轮报告：`data/knowledge/_audit/plot_rag_eval_report_r0.json`｜开始时间 2026-09-13 23:18:49

## 0. 结论速览

| 门禁 | 判据 | 实测 | 结论 |
|---|---|---|---|
| 300 题严格通过率 | 目标 ≥75%（基线 63.7%） | 191/300 = 63.7% | **未达标（差 11.3pt）** |
| 注入口径通过率 | 产品真实口径 | 175/300 = 58.3% | 记录 |
| A5 负样本零注入 | 逐条 0 块 | 注入 37 块 / 53 条 | **有界未达标**（已知残余 5 条，新增泄漏 0 条） |
| 灰机 14 题标准 | 14/14（口径 `--top 10`） | 14/14 | 达标 |
| pytest 全绿 | 0 失败 | 959 passed, 1 skipped | 达标 |
| A1 延迟增量 | p95 增量 ≤100ms（同条件基线） | 本轮 p95 724.5ms（见 §2） | 见 §2 |
| 报告 schema | 四键齐备 + 11 字段 + 9 值枚举 + 成对产出 | 14/14 条通过 | 达标 |

## 1. 主轮指标

- 题量 **300**｜严格通过 **191**（63.7%）｜天花板内 66.7%（天花板内题 279）
- 块精度 0.3283｜答案块率 0.221｜MRR 0.3864｜oracle recall 0.2999｜平均返回 7.74 块｜空结果 1.0%
- 注入口径（预算 2400 字符，实际均装入 2469.6 字符）：175（58.3%）
- 延迟 p50 618.2ms｜p90 685.9ms｜p95 724.5ms｜max 3664.3ms
- 路径归因 {'mention': 731, 'edge': 857, 'semantic': 636, 'chapter': 97}

### 1b. 灰机 14 题闸门：**按返回预算分口径**（预算不同，读数不同）

| 报告 | 口径 `--top` | 通过 | 缺口题 |
|---|---|---|---|
| `rag_huiji_eval_report.json` | 10 | 14/14 | — |
| `ablation/huiji_top10.json` | 10 | 14/14 | — |
| `ablation/huiji_top6.json` | 6 | 13/14 | 维也纳篇与卡卡尼亚对峙决斗的医生是谁？ |
| `ablation/huiji_top5.json` | 5 | 13/14 | 维也纳篇与卡卡尼亚对峙决斗的医生是谁？ |

> 闸门口径是 **`--top 10`（14/14）**；脚本默认 `--top 5` 更严，在「维也纳篇与卡卡尼亚对峙决斗的医生是谁？」上少一块证据（13/14）。**同一份代码在不同返回预算下读数不同**，故口径必须随读数一起写出——只写「14/14」而不写预算是不可比的读数。


| 口径 | 值 | 用途 |
|---|---|---|
| ① 基线事实（现状 p95 实测） | 691.2ms（`plot_rag_eval_report_p0_2_baseline.json`） | 事实记录，不是允许上限 |
| ② **合入判据**：新增在线组件 p95 增量 | 33.3ms（阈值 ≤100ms） | **唯一判据** |
| ③ 历史 300ms 绝对线 | 本轮 724.5ms | **不作判据**（消歧遗留） |

> 埋点轮的耗时**不计入** p95：延迟一律取无埋点首轮，否则评测自身开销会污染判据。首轮与埋点轮逐题判定一致性 = True（差异 0/300）——这一条同时是「埋点不改变检索结果」的不变量检验。

### 2b. 同条件重复运行的 p95 抖动（这就是判据必须用增量、不能用绝对线的原因）

| 报告 | 配置差异 | p95 (ms) |
|---|---|---|
| `plot_rag_eval_report_p0_2_baseline.json` | M8 基线（同配置） | 691.2 |
| `ablation/d1_on.json` | D1 全开（排序路径与 R0 相同） | 693.1 |
| `ablation/d1_off.json` | D1 关（= R0 配置） | 691.8 |
| `ablation/c4_off.json` | C4 关 | 689.6 |
| `plot_rag_eval_report_r0.json` | R0 全开 | 724.5 |

> 同一份代码、同一题集、同一配置的多次运行，p95 相差可达数十毫秒（OS 文件缓存、嵌入服务排队、CPU 频率）。因此 Spec §1.4.1 的三口径里，历史 300ms **绝对线**不作判据；判据是**同条件增量 ≤100ms**。

## 3. 六通道瀑布（`trace_agg.channels[]`，跨题聚合）

| 通道 | 量纲 | 执行题数/总题数 | 命中率 | hit_avg | hit_blk_avg | kept_avg | kept_rate | 被挤出 | skip_reason 分布 |
|---|---|---|---|---|---|---|---|---|---|
| 别名精确 | seed | 300/300 | 96% | 1.32 | 9.1233 | 3.0767 | 34% | 6.0467 | {'gate_rejected': 12} |
| BM25 兜底 | block | 288/300 | 0% | 0.0 | 0.0 | 0.0 | — | 0.0 | {'no_candidate': 288, 'no_seed': 12} |
| 语义向量 | block | 300/300 | 96% | 4.8 | 4.8 | 2.78 | 58% | 2.02 | {'no_seed': 12} |
| 图传播 | block | 288/300 | 100% | 17.3924 | 7.8889 | 2.9757 | 38% | 4.9132 | {'no_seed': 12, 'no_candidate': 1} |
| 篇章路由 | block | 288/300 | 38% | 1.0694 | 1.0694 | 0.4549 | 43% | 0.6146 | {'no_candidate': 178, 'no_seed': 3} |
| 扩展查询 | block | 0/300 | — | — | — | — | — | — | {'not_enabled': 300} |

- **桶 4 融合层稀释**：`squeezed_total` = 2198（Σ over 块通道（6 通道去「别名精确」）× max(0, hit_blocks − kept_in_final)；「别名精确」是种子来源维度，量纲不同不参与求和）
  - 适用性前提 `graph_hit_total` = **2580**（图传播 + 篇章路由（display 通道口径，含 mention 块））；图通道子集 `squeezed_total_graph_only` = 1592
  - 规格原文公式逐字复算值 `squeezed_total_literal_spec_formula` = 4012（与主口径的差额 = 「别名精确」种子量纲混入块量纲的部分，落盘以便审计）
- **AC-3 标定证据（margin 直方图）**：桶边界显式落盘 `[0.0, 0.02, 0.05, 0.1, 0.2, 0.35, 0.5]`；触发 12 题、有 margin 12、单候选（margin 无定义）0
  - 分布：{'[0.00,0.02)': 7, '[0.02,0.05)': 2, '[0.05,0.10)': 3, '[0.10,0.20)': 0, '[0.20,0.35)': 0, '[0.35,0.50)': 0, '>=0.50': 0}
  - 阈值取值：{'0.0': 12}
- **降级**：`fallback_counts` = {}（适用性前提：`cases` = 300、`total_ms` = {'p50': 627.1, 'p95': 689.6}）
- **负样本通道执行计数**（R3 的成因侧证据）
  - 负样本 53 条：seeds 合计 59、图传播 hit 18、语义向量 hit 25
  - skip_reason：{'gate_rejected': 34, 'no_seed': 192, 'not_enabled': 53, 'no_candidate': 24} —— 「零注入」到底是护栏拦下的还是通道压根没跑，由这两行区分

## 4. 消融矩阵（AC-1：判据本体 = McNemar 配对检验）

| 运行 | 关闭的功能 | m | b | c | delta_pt | method | mcnemar_p | cases_executed | cases_total | 判读 |
|---|---|---|---|---|---|---|---|---|---|---|
| R0 全开（参照轮） | — | — | — | — | — | — | — | — | — | 非消融：严格通过 191/300（63.7%） |
| 关 C4 手工边豁免弱证过滤 | `plot_weak_exempt_sources`='' | 0 | 0 | 0 | 0.0 | `exact` | None | 36 | 300 | 无翻转：Δ 严格为 0，**无检验意义**（mcnemar_p 必须为 null，不得给 1.0 假值）。先看 cases_executed=36 —— 为 0 |
| 关 D1 node specificity | `plot_ppr_node_specificity`='false' | 10 | 4 | 6 | 0.67 | `exact` | 0.753906 | 255 | 300 | 不显著：正式结论不得写「无效」——不显著只表示本轮证据不足；须同时给出 cases_executed 与 m 才能判读 |
| D1 全开（D1 消融的参照轮） | — | — | — | — | — | — | — | — | — | 非消融：严格通过 189/300（63.0%） |

**关 C4 手工边豁免弱证过滤**（作用面：R8 红线：人工事实边是否参与传播）

- 全开 'manual'（参照 `data/knowledge/_audit/plot_rag_eval_report_r0.json`） → 关闭 ''；配对题数 300
- `cases_executed` = **36** —— 该题图路存在「被豁免保留且落在跳距内」的弱证边（可能作用面）；c4_used 为其中真正产出证据块的题数
- 原始执行计数：{'c4_candidates': 36, 'c4_used': 1, 'd1_seeds_total': 0, 'd1_seeds_downweighted': 0, 'semantic_items_in': 1440, 'seeds_total': 396}
- 快速判读档（**不作判据**）：≤1pt（≤3 题）：贡献不显著
- 结论：无翻转：Δ 严格为 0，**无检验意义**（mcnemar_p 必须为 null，不得给 1.0 假值）。先看 cases_executed=36 —— 为 0 只说明「功能本次未触发」，不构成「功能无效」的证据（§7.6.6）
- 关闭轮：严格通过 191（63.7%）；负样本注入 37 块，新增泄漏 0 条
- 参照轮 `data/knowledge/_audit/plot_rag_eval_report_r0.json`：**只差被消融开关的那一轮**（其余配置相同）——配对前提由 `--ablate-on` 的配置一致性硬校验保证（不一致时脚本直接拒绝出结论），不靠人记得。

**关 D1 node specificity**（作用面：泛种子抑制 / 多跳质量）

- 全开 'true'（参照 `data/knowledge/_audit/ablation/d1_on.json`） → 关闭 'false'；配对题数 300
- `cases_executed` = **255** —— 该题至少有 1 个种子被降权（specificity<1）；孤立种子按 1.0 不计
- 原始执行计数：{'c4_candidates': 36, 'c4_used': 1, 'd1_seeds_total': 409, 'd1_seeds_downweighted': 333, 'semantic_items_in': 1440, 'seeds_total': 396}
- 快速判读档（**不作判据**）：≤1pt（≤3 题）：贡献不显著
- 结论：不显著：正式结论不得写「无效」——不显著只表示本轮证据不足；须同时给出 cases_executed 与 m 才能判读
- 关闭轮：严格通过 191（63.7%）；负样本注入 37 块，新增泄漏 0 条
- 参照轮 `data/knowledge/_audit/ablation/d1_on.json`：**只差被消融开关的那一轮**（其余配置相同）——配对前提由 `--ablate-on` 的配置一致性硬校验保证（不一致时脚本直接拒绝出结论），不靠人记得。

## 5. 逐题 diff（数据源统一取 `ablation.case_ids_flipped`）

- 配对题数 300｜来源 `compute_flipped(baseline.items, items)（与 ablation 同一实现）`
- 新增通过（fail→pass）0 题：—
- 新增失败（pass→fail）0 题：—

## 6. 失分桶归因（架构 §4e 五桶）

失分 **109/300**（通过 191；有 trace 的失分题 300）

**第一层口径（根因）**：`triage_plot_rag.py（逐题根因；与审计 §1 同口径）`｜来源 `data/knowledge/_audit/plot_rag_triage_r0.json`（该轮通过 191/300，与本轮同源核对）

| 桶 | 题数 | 占失分 | §4e 期望规模（偏离即需重校归因） | trace 症状题数 | 判定规则 |
|---|---|---|---|---|---|
| 别名桥缺失 | 88 | 80.7% | 111/300 题（审计 §1 基线，126 个缺失证据组） | 0 | alias_bridge_gap：实体在图里，但**查询里根本没出现该证据组实体的任何名字/别名** |
| 语义兜底无安全间隔 | 0 | 0.0% | 分诊实测：负样本实体 0.60–0.82 > 失败题正解 0.48 | 0 | 实体链接兜底触发但 linked=False：候选中分数重叠，过不了阈值（正解可能就在候选里） |
| 抽取召回不均 | 2 | 1.8% | 边数极不平衡（高塔 5 边 vs 阿莱夫 32 边） | 0 | graph_gap（语料有块但没被图谱引用为证据）+ unreachable_gap（有证据但本次激活不到） |
| 跨语言底座 | 0 | 0.0% | 9021 块中 88% 为英文 ASR | 28 | 查询为中文且返回块 CJK 占比 < 0.5：中文查询 vs 英文 ASR 正文，词法不可比 |
| 融合层稀释 | 0 | 0.0% | 附加桶（PM F5 假设；扩大候选已被证伪） | 99 | 图通道有命中但 kept_in_final == 0：通道有货，被 RRF 融合层挤出最终结果 |
| retrieval_gap | 12 | 11.0% | —（§4e 未列此桶） | 0 | 图谱记了证据也够得着，但没取回（修排序，算法面） |
| no_entity_gap | 3 | 2.8% | —（§4e 未列此桶） | 0 | 证据组关键词在图谱里找不到实体（补实体，数据面） |
| link_bug | 4 | 3.7% | —（§4e 未列此桶） | 0 | 名字就在查询里却没链上（修链接，算法面） |

triage 全部根因：{'alias_bridge_gap': 88, 'retrieval_gap': 12, 'no_entity_gap': 3, 'link_bug': 4, 'unreachable_gap': 1, 'graph_gap': 1}

§4e 未列的原因（数据/算法缺口，**单列**不并入未归因）：{'retrieval_gap': 12, 'no_entity_gap': 3, 'link_bug': 4}

**第二层口径（症状，可重叠）**：{'graph_squeezed': 99, 'zh_query_en_chunks': 28, 'margin_triggered': 10, 'margin_rejected': 10, 'graph_no_hit': 10}——桶 4/桶 5 由 trace 补（triage 看不见「取回后」现象），其 `trace_overlay_cases` 与桶计数可重叠

> 第一层 section4e = 根因归因（一题一桶，按 triage 逐题最严重根因）；第二层 trace_signals = 症状计数（可重叠）。两者读数不可互相校验。

**偏离核对（架构 §5 第 9 条：无某桶题量占比严重偏离预期，否则归因需重校）**

- 桶 1（别名桥缺失）：本轮 88 题 / 300，审计 §1 基线为 111 题 / 300（M8 语义层上线后已下降；差额即语义层直接命中答案块的那部分）
- 桶 3/桶 5 的期望规模是**结构性事实**（边密度不平衡、88% 英文 ASR），不是阈值；本轮读数见上表

## 7. 阴性证据通则核对表（§7.6.6）

| 阴性读数 | 值 | 必须并列的适用性前提 |
|---|---|---|
| `trace_agg.squeezed_total` | 2198 | `graph_hit_total` = 2580（图传播 2272 + 篇章路由 308）；图通道子集 squeezed = 1592 |
| `trace_agg.fallback_counts` | {} | `cases` = 300；`total_ms` = {'p50': 627.1, 'p95': 689.6} |
| `trace_agg.margin_histogram`（触发数） | triggered = 12 | `n_with_margin` = 12；`n_single_candidate` = 0；阈值 {'0.0': 12} |
| `negatives.negative_injection_total`（R3 零注入） | 37 块 / 53 条 | 负样本通道执行计数：图传播 hit 18、语义向量 hit 25、seeds 合计 59、skip {'gate_rejected': 34, 'no_seed': 192, 'not_enabled': 53, 'no_candidate': 24} |

## 8. 报告 schema 门禁（机器判据）

| # | 判据 | 结论 | 证据 |
|---|---|---|---|
| 1 | eval_run_complete 顶层键齐备 | ✅ 通过 | event、summary、trace_agg、ablation、diff_vs_baseline、bucket_attribution、assets_sha256_head16、items |
| 2 | event 取值 | ✅ 通过 | eval_run_complete |
| 3 | trace_agg 字段齐备（表 7.6.4-a） | ✅ 通过 | 8 字段齐备 |
| 4 | 六通道固定顺序（§7.6.1） | ✅ 通过 | ['别名精确', 'BM25 兜底', '语义向量', '图传播', '篇章路由', '扩展查询'] |
| 5 | channels[] 子结构字段齐备 | ✅ 通过 | 10 字段齐备（含设计侧双列 kept_in_final_avg/kept_rate） |
| 6 | skip_reason 只用 9 值枚举 | ✅ 通过 | 9 值内（9 值枚举） |
| 7 | trace_agg.cases == summary.cases | ✅ 通过 | 300 vs 300 |
| 8 | 通则成对产出：squeezed_total ↔ graph_hit_total | ✅ 通过 | 2198 ↔ 2580 |
| 9 | 通则成对产出：fallback_counts ↔ cases + total_ms | ✅ 通过 | {} ↔ cases=300 total_ms={'p50': 627.1, 'p95': 689.6} |
| 10 | 通则成对产出：kept_rate 分母 0 → null | ✅ 通过 | 仅当块级候选为 0 时出现 null |
| 11 | ablation 11 字段 + m=0→null（c4_off.json） | ✅ 通过 | m=0 p=None method=exact |
| 12 | ablation.trace_schema（c4_off.json） | ✅ 通过 | ablation-v1 |
| 13 | ablation 11 字段 + m=0→null（d1_off.json） | ✅ 通过 | m=10 p=0.753906 method=exact |
| 14 | ablation.trace_schema（d1_off.json） | ✅ 通过 | ablation-v1 |

## 8b. 「默认关 / 开关关掉时与现状逐位一致」的证据

| 开关 | 默认值 | 关掉后的行为 | 证据 |
|---|---|---|---|
| `plot_weak_exempt_sources`（C4） | `"manual"`（**Spec §4 锁定值**，非 False） | 空串 = 无豁免 = P0-1 改造前的过滤口径 | C4 消融轮与 R0 **逐题判定完全一致**（m=0，mcnemar_p=null） |
| `plot_ppr_node_specificity`（D1） | `False` | 默认即现状：`seed_weights=None`，PPR 输入逐键逐值不变 | `tests/test_plotrag_p0.py::TestBitIdenticalRegression::test_none_params_bit_identical`（以**改造前算法的参考实现**在真实规模随机图上差分，逐位相等） |
| `plot_semantic_rerank_enabled`（B3） | `False` | 未实现（P0-2） | 未启用即不存在该路径 |
| `plot_semantic_zh_enabled`（A1） | `False` | 未实现（P1-1） | 同上 |
| `plot_trace_enabled`（F8a） | `False` | 关时不构造 trace、不计时、不写盘 | 埋点轮与主轮逐题判定一致（True，差异 0/300） |

**R0 与 M8 基线逐位一致（检索结果未被本次改动触碰）**

| 指标 | 基线（M8 口径） | R0 全开 | Δ |
|---|---|---|---|
| strict_pass | 0.6367 | 0.6367 | 0.0 |
| chunk_precision | 0.3283 | 0.3283 | 0.0 |
| answer_chunk_rate | 0.221 | 0.221 | 0.0 |
| mrr | 0.3864 | 0.3864 | 0.0 |

> 四项排序指标**逐位相等**说明：M-11 埋点（新增字段与计时）与 `hit_blocks` 归因（只影响报告聚合、不改排序）都没有触碰检索结果。延迟单独裁决（§2），不并入本表。

## 9. 逐项决策（结论形态：默认开关决策 / 待实现项）

- **P0-4 D1（node specificity）：保持默认关。** 依据：配对检验 m=10（b=4 通过→失败 / c=6 失败→通过），Δ=0.67pt，`mcnemar_p`=0.753906（exact）≥0.05 → 不显著；开启后净损 -2 题（b 比 c 多 -2）。`cases_executed`=255——**功能确实被测到了**，因此这不是「没测到」的阴性结论，而是「测到了、无正收益」。
- **P0-1 C4（手工边豁免）：保留 Spec 锁定默认值 `"manual"`。** 依据：配对检验 m=0（无翻转），`mcnemar_p`=null；`cases_executed`=36（图路确实存在被豁免保留的弱证边候选）。意义不在 300 题通过率，而在 R8 红线：人工事实边经过图谱重建后仍在场（`apply_manual_edges.py --check` 新增 0、在场率 100%）。
- **P0-2（B2+B3）：未实现**，开关默认关、无执行计数键 → `cases_executed` 显式报「未登记」而不是 0（避免把「未实现」读成「无效果」）。该项承担 AC-1 的 75% 目标缺口与 A5 的 5 条已知残余。
- **P0-3（A2 别名表扩充）：未实现**；triage 已给出待补清单（中文正名零命中·度≥3 的实体 40 个），是 P0-3 的输入。

## 10. 未达标项与遗留（逐条登记，不以「已知」代替「已修复」）

- A5 已知残余 5 条（待 B3 reranker 安全间隔）：
  - `哈利波特是谁`
  - `苹果公司的 CEO 是谁`
  - `巴黎在哪个国家`
  - `泰坦尼克号是哪一年沉没的`
  - `who is the president of the united states`
- 新增泄漏 0 条（无）
- 严格通过率 63.7% < 75%：剩余缺口由 P0-2（B2 实体摘要嵌入 + B3 reranker 安全间隔）与 P0-3（A2 别名表扩充）承担，本报告只登记现状。
- 未实现/未消融项：P0-2（B2/B3）、P0-3（A2）、P1-1（A1）——对应功能开关默认关（`plot_semantic_rerank_enabled` / `plot_semantic_zh_enabled`），未登记执行计数键的开关会由 `cases_executed` 显式报「未登记」而不是静默报 0。

## 11. 复现命令（本报告全部数字可由此重放）

```bash
# ① 全量主轮 + 埋点轮 + trace_agg/diff/bucket（含 A1/A5 自检）
.venv/Scripts/python.exe -X utf8 scripts/run_ablation_matrix.py --only R0

# ② 消融两行（C4 / D1；内部串行，含参照轮）
.venv/Scripts/python.exe -X utf8 scripts/run_ablation_matrix.py

# ③ §4e 归因的权威口径（逐题根因；供 bucket_attribution 第一层消费）
.venv/Scripts/python.exe -X utf8 scripts/triage_plot_rag.py \
    --out data/knowledge/_audit/plot_rag_triage_r0.json

# ④ 灰机 14 题正确性标准
.venv/Scripts/python.exe -X utf8 scripts/eval_rag_huiji.py

# ⑤ 单测全绿
.venv/Scripts/python.exe -X utf8 -m pytest tests/ -q

# ⑥ 生成本报告（不手抄任何数字；schema 门禁不过则退出码 4）
.venv/Scripts/python.exe -X utf8 scripts/report_p0_acceptance.py \
    --pytest "959 passed, 1 skipped" \
    --out deliverables/plot-graph-rag-p0-acceptance.md
```

> **串行**执行 ①②：本项目的延迟判据是 p95 增量 ≤100ms，并发两轮会互相抢 CPU 与本地嵌入服务，测到的是排队时间而不是组件开销（延迟三口径的第一条就是「同条件」）。

