# v8 → v9 逐项 delta 表

- 口径：v8 归档 = data/compendium_rag/reports/v8_audit/；v9 = data/compendium_rag/reports/；两侧分别汇总，任一侧缺报告标 missing，不得互相补位。
- v8 图 SHA：`026b41699f021db2`；v9 图 SHA：`fb7322dd4f558e7c`
- 总分：v8 **43.39%（C）** → v9 **46.73%（C）**
- 可比 gate：47；单侧缺失：0；判定翻转：4；指标改善：9；**指标恶化：11**；方向不可判：10

> 纪律：本表逐行给出**数值方向**与**指标方向**（由 target 的 ≥/≤ 极性判定），恶化行以 ⚠ 标注——只报涨不报跌即为违规。
> 注意：幻觉率、泄漏率等「越小越好」的门槛，读数下降是改善而非恶化，故必须看指标方向列，不能只看数值方向。

## 1. 逐 gate delta

| 报告 | gate | 目标 | v8 | v9 | 数值方向 | 指标方向 | v8 判定 | v9 判定 |
|---|---|---|---|---|---|---|---|---|
| adv_confuse | L5.3 跨角色混淆「把他人私密当己知」率 | ≤0.10 | 0.0000 | 0.0000 | 平 | 持平 | PASS | PASS |
| adv_contradict | L5.4 知识矛盾探测 检测器召回 | ≥0.90 | 1.0000 | 1.0000 | 平 | 持平 | PASS | PASS |
| adv_drift | L5.2 角色漂移退化率（50 轮长上下文回放代理） | ≤0.10 | 0.8750 | 0.8750 | 平 | 持平 | FAIL | FAIL |
| adv_drift | L5.2b 真·运行时多轮漂移 | ≥50 轮在线会话 | 无通路 | 无通路 | n/a | 不可判 | N/A | N/A |
| adv_inject | L5.1 冲突注入 检测器捕获率 | ≥0.80 | 1.0000 | 1.0000 | 平 | 持平 | PASS | PASS |
| adv_inject | L5.1b 冲突注入 检索未标注同现率 | =0（双方同时进 top-6 且无标注） | 0.0000 | 0.0000 | 平 | 持平 | PASS | PASS |
| l1_pr | L1.1 实体精确率 | ≥0.90 | 0.5918 | 0.5918 | 平 | 持平 | FAIL | FAIL |
| l1_pr | L1.1 实体召回率 | ≥0.85 | 0.8135 | 0.8135 | 平 | 持平 | FAIL | FAIL |
| l1_pr | L1.1 实体 F1 | ≥0.87 | 0.6852 | 0.6852 | 平 | 持平 | FAIL | FAIL |
| l1_pr | L1.2 关系精确率（端点对口径） | ≥0.85 | 0.2718 | 0.2893 | 升 | 改善 | FAIL | FAIL |
| l1_pr | L1.4替代 实体类型分类准确率 | ≥0.90 | 0.9554 | 0.9554 | 平 | 持平 | PASS | PASS |
| l1_structure | L1.3 孤立节点占比 | ≤0.10 | 0.1594 | 0.1611 | 升 | 恶化 ⚠ | FAIL | FAIL |
| l1_structure | L1.3 平均度数 | ≥2.5 | 8.6080 | 7.7100 | 降 | 恶化 ⚠ | PASS | PASS |
| l1_structure | L1.3 连通分量数≤1.5×角色数 | ≤1.5×2023 | {"components_total": 1172, "nontrivial": 51, "largest_cc_rat | {"components_total": 1184, "nontrivial": 51, "largest_cc_rat | n/a | 不可判 | N/A | N/A |
| l1_structure | L1.1 实体类型合规 | =1.00（6 类受控） | {"violation": 0, "types": {"角色": 2023, "物品": 2004, "概念": 120 | {"violation": 0, "types": {"角色": 2023, "物品": 2004, "概念": 120 | n/a | 不可判 | PASS | PASS |
| l1_structure | L1.2 关系类型合规率（严格：原文谓语∈77 canonical） | ≥1.00 | 0.0676 | 0.8429 | 升 | 改善 | FAIL | FAIL |
| l1_structure | L1.4 层级分配准确率 | ≥0.90 | None | None | n/a | 不可判 | N/A | N/A |
| l2 | L2.1 Recall@10（集合级，主口径=三集合并） | ≥0.85 | 0.3869 | 0.3864 | 降 | 恶化 ⚠ | FAIL | FAIL |
| l2 | L2.1 MRR@10 | ≥0.70 | 0.7085 | 0.7074 | 降 | 恶化 ⚠ | PASS | PASS |
| l2 | L2.1 NDCG@10 | ≥0.65 | 0.5589 | 0.5581 | 降 | 恶化 ⚠ | FAIL | FAIL |
| l2 | L2.2 子图completeness | ≥0.8 | 0.2054 | 0.2270 | 升 | 改善 | FAIL | FAIL |
| l2 | L2.2 子图minimality | ≥0.75 | 0.5671 | 0.5317 | 降 | 恶化 ⚠ | FAIL | FAIL |
| l2 | L2.2 子图connectivity | ≥0.85 | 0.9561 | 0.9522 | 降 | 恶化 ⚠ | PASS | PASS |
| l2 | L2.3 跨角色知识泄漏率 | ≤0.03 | 0.1467 | 0.1556 | 升 | 恶化 ⚠ | FAIL | FAIL |
| l3 | L3.1 角色/正典忠实度（persona，1~5） | ≥4.0 | 4.6935 | 4.9138 | 升 | 改善 | PASS | PASS |
| l3 | L3.2 声音退化率（voice≤2 占比） | ≤0.10 | 0.0000 | 0.0000 | 平 | 持平 | PASS | PASS |
| l3 | L3.3 Faithfulness | ≥0.85 | 0.9486 | 0.9845 | 升 | 改善 | PASS | PASS |
| l3 | L3.4 幻觉率（域内题） | ≤0.08 | 0.1475 | 0.0345 | 降 | 改善 | FAIL | PASS |
| l3 | L3.5 越界拒答率（negative+unanswerable） | ≥0.80 | 0.9299 | 0.9618 | 升 | 改善 | PASS | PASS |
| l3 | L3.6 越界幻觉率 | ≤0.15 | 0.0510 | 0.0255 | 降 | 改善 | PASS | PASS |
| l3 | L3.7judge 复评一致性 Cohen κ（基础设施·可靠性自证） | ≥0.60 | 0.6737 | 0.7439 | 升 | 改善 | PASS | PASS |
| l4_group | L4 基础设施 谓语归组完备性 | 尾巴 ≥80% 拿到判定且零未判定谓语 | {"tail_mapped": 6916, "tail_total": 6956, "still_unmapped":  | {"tail_mapped": 6916, "tail_total": 1465, "still_unmapped":  | n/a | 不可判 | FAIL | PASS |
| l4_group | L4.1 谓语归组盲评分歧率 | ≤0.15 | 0.2000 | 0.2000 | 平 | 持平 | FAIL | FAIL |
| l4_multiscene | L4.5 多角色场景关系互洽性 | ≥4.0/5 | 3.9333 | 3.9333 | 平 | 持平 | FAIL | FAIL |
| l4_multiscene | L4.5b 多角色同场运行时生成一致性 | ≥4.0/5 | None | None | n/a | 不可判 | N/A | N/A |
| l4_privacy | L4.3 私密信息跨角色泄漏率（检索层口径） | ≤0.02 | 0.2152 | 0.2278 | 升 | 恶化 ⚠ | FAIL | FAIL |
| l4_symmetry | L4.1a 方向对成对完整率 | ≥0.95 | 0.0379 | 0.0376 | 降 | 恶化 ⚠ | FAIL | FAIL |
| l4_symmetry | L4.1b 互斥谓语共存率 | ≤0.05 | 0.0244 | 0.0247 | 升 | 恶化 ⚠ | PASS | PASS |
| l4_temporal | L4.2a 时序矛盾率（状态变更实体内） | ≤0.03 | 0.0000 | 0.0000 | 平 | 持平 | PASS | PASS |
| l4_temporal | L4.2b 同点状态冲突率 | ≤0.02 | 0.0000 | 0.0000 | 平 | 持平 | PASS | PASS |
| l4_worldview | L4.4 世界观定义统一性 | ≥0.95 | 0.9425 | 0.9425 | 平 | 持平 | FAIL | FAIL |
| wp0_env | graph_sha_vs_v8 | == 026b41699f021db2 | 026b41699f021db2 | fb7322dd4f558e7c | n/a | 不可判 | PASS | FAIL |
| wp0_env | graph_fingerprint | 语义指纹一致 | ok | ok | n/a | 不可判 | PASS | PASS |
| wp0_env | gateway_available | 可达（CloudLLM/兜底通道） | 200 | 200 | 平 | 持平 | PASS | PASS |
| wp0_env | ollama_available | bge-m3 嵌入可用 | 1024 | 1024 | 平 | 持平 | PASS | PASS |
| wp0_env | qid_whitelist_counts | 300/196/104/206/120 | {"300cn_all": 300, "300cn_answerable": 196, "300cn_unanswera | {"300cn_all": 300, "300cn_answerable": 196, "300cn_unanswera | n/a | 不可判 | PASS | PASS |
| wp0_env | v8_three_main_numbers | 167/196, 184/206, 118/120, safety 1/104（逐题差=0） | {"safety_unanswerable": {"hits": 1, "n": 104}, "300cn": {"hi | {"safety_unanswerable": {"hits": 1, "n": 104}, "300cn": {"hi | n/a | 不可判 | PASS | FAIL |

## 2. 判定翻转清单

- **L3.4 幻觉率（域内题）**：FAIL → PASS（0.1475 → 0.0345）
- **L4 基础设施 谓语归组完备性**：FAIL → PASS（{"tail_mapped": 6916, "tail_total": 6956, "still_unmapped":  → {"tail_mapped": 6916, "tail_total": 1465, "still_unmapped": ）
- **graph_sha_vs_v8**：PASS → FAIL（026b41699f021db2 → fb7322dd4f558e7c）（**口径性**，见下）
- **v8_three_main_numbers**：PASS → FAIL（{"safety_unanswerable": {"hits": 1, "n": 104}, "300cn": {"hi → {"safety_unanswerable": {"hits": 1, "n": 104}, "300cn": {"hi）（**口径性**，见下）

### 2b. 口径性翻转说明（不是质量回退）

- **graph_sha_vs_v8**：`scripts/audit_wp0_env.py` 硬编 `AC.V8_GRAPH_SHA16` 作为期望值，在任何 v9 图上必然 FAIL——口径性失败，不是图回退。
- **v8_three_main_numbers**：同一脚本把 v8 期的三主数当基线逐位比对；blind206 与 gen120 各高 1 题属真实读数变化（见第 6 节三主数专项），不是回退，但该 gate 的「逐位相等」口径本身已不适用于 v9。

## 3. 指标恶化清单（必须并列，不得被主口径盖过）

- ⚠ **L1.3 孤立节点占比**：0.1594 → 0.1611（升，目标 ≤0.10，v9 判定 FAIL）
- ⚠ **L1.3 平均度数**：8.6080 → 7.7100（降，目标 ≥2.5，v9 判定 PASS）
- ⚠ **L2.1 Recall@10（集合级，主口径=三集合并）**：0.3869 → 0.3864（降，目标 ≥0.85，v9 判定 FAIL）
- ⚠ **L2.1 MRR@10**：0.7085 → 0.7074（降，目标 ≥0.70，v9 判定 PASS）
- ⚠ **L2.1 NDCG@10**：0.5589 → 0.5581（降，目标 ≥0.65，v9 判定 FAIL）
- ⚠ **L2.2 子图minimality**：0.5671 → 0.5317（降，目标 ≥0.75，v9 判定 FAIL）
- ⚠ **L2.2 子图connectivity**：0.9561 → 0.9522（降，目标 ≥0.85，v9 判定 PASS）
- ⚠ **L2.3 跨角色知识泄漏率**：0.1467 → 0.1556（升，目标 ≤0.03，v9 判定 FAIL）
- ⚠ **L4.3 私密信息跨角色泄漏率（检索层口径）**：0.2152 → 0.2278（升，目标 ≤0.02，v9 判定 FAIL）
- ⚠ **L4.1a 方向对成对完整率**：0.0379 → 0.0376（降，目标 ≥0.95，v9 判定 FAIL）
- ⚠ **L4.1b 互斥谓语共存率**：0.0244 → 0.0247（升，目标 ≤0.05，v9 判定 PASS）

## 4. 指标改善清单（并列，便于对照）

- **L1.2 关系精确率（端点对口径）**：0.2718 → 0.2893（升，目标 ≥0.85，v9 判定 FAIL）
- **L1.2 关系类型合规率（严格：原文谓语∈77 canonical）**：0.0676 → 0.8429（升，目标 ≥1.00，v9 判定 FAIL）
- **L2.2 子图completeness**：0.2054 → 0.2270（升，目标 ≥0.8，v9 判定 FAIL）
- **L3.1 角色/正典忠实度（persona，1~5）**：4.6935 → 4.9138（升，目标 ≥4.0，v9 判定 PASS）
- **L3.3 Faithfulness**：0.9486 → 0.9845（升，目标 ≥0.85，v9 判定 PASS）
- **L3.4 幻觉率（域内题）**：0.1475 → 0.0345（降，目标 ≤0.08，v9 判定 PASS）
- **L3.5 越界拒答率（negative+unanswerable）**：0.9299 → 0.9618（升，目标 ≥0.80，v9 判定 PASS）
- **L3.6 越界幻觉率**：0.0510 → 0.0255（降，目标 ≤0.15，v9 判定 PASS）
- **L3.7judge 复评一致性 Cohen κ（基础设施·可靠性自证）**：0.6737 → 0.7439（升，目标 ≥0.60，v9 判定 PASS）

## 5. 两口径并列（诊断列，不改判）

- **L2.1**（目标 ≥0.85，计分口径判定 FAIL）
  - 原口径：**0.3864** — mean_q recall@10
  - 诊断口径：**0.6078** — mean_q recall@10 × |R_q| / min(10,|R_q|)
  - oracle 天花板：0.5884
  - 读法：两种口径均未达标：正确证据块基本都在前十，输在集合覆盖而非找不着（hit@10 见 gates 明细）。
- **L4.1a**（目标 ≥0.95，计分口径判定 FAIL）
  - 原口径：**0.0376** — grouped（归组后）方向对成对完整率
  - 诊断口径：**0.0376** — raw（原始谓语）方向对成对完整率
  - 读法：归组把成对率从 raw 抬到 grouped（约 6 倍），但两者都远低于 0.95：缺口主因是原文谓语本身不成对（抽取层），归并只能部分补偿。
  - 口径声明：诊断列仅并列呈现，不改判、不改门槛分母。

## 6. 三主数专项（full / graph_only 两口径）

| 集 | 模式 | 子集 | n | v8 hit@6 | v9 hit@6 | Δ | v8 MRR | v9 MRR | 配对 +/− | 方向 |
|---|---|---|---|---|---|---|---|---|---|---|
| 300cn | full | answerable | 196 | 0.8520 | 0.8520 | +0.0000 | 0.6645 | 0.6616 | +0/−0 | 平 |
| 300cn | full | all | 300 | 0.5600 | 0.5600 | +0.0000 | 0.4374 | 0.4356 | +0/−0 | 平 |
| 300cn | graph_only | answerable | 196 | 0.8010 | 0.8061 | +0.0051 | 0.6089 | 0.6012 | +1/−0 | 升 |
| 300cn | graph_only | all | 300 | 0.5267 | 0.5300 | +0.0033 | 0.4012 | 0.3961 | +1/−0 | 升 |
| blind206 | full | answerable | 206 | 0.8932 | 0.8981 | +0.0049 | 0.6762 | 0.6773 | +1/−0 | 升 |
| blind206 | full | all | 206 | 0.8932 | 0.8981 | +0.0049 | 0.6762 | 0.6773 | +1/−0 | 升 |
| blind206 | graph_only | answerable | 206 | 0.8447 | 0.8398 | -0.0049 | 0.5634 | 0.5549 | +0/−1 | 降 ⚠ |
| blind206 | graph_only | all | 206 | 0.8447 | 0.8398 | -0.0049 | 0.5634 | 0.5549 | +0/−1 | 降 ⚠ |
| gen120 | full | answerable | 120 | 0.9833 | 0.9917 | +0.0083 | 0.8253 | 0.8207 | +1/−0 | 升 |
| gen120 | full | all | 120 | 0.9833 | 0.9917 | +0.0083 | 0.8253 | 0.8207 | +1/−0 | 升 |
| gen120 | graph_only | answerable | 120 | 0.9667 | 0.9833 | +0.0167 | 0.7389 | 0.7593 | +2/−0 | 升 |
| gen120 | graph_only | all | 120 | 0.9667 | 0.9833 | +0.0167 | 0.7389 | 0.7593 | +2/−0 | 升 |

### 6b. 配对翻转题（逐题级，计划 :127 要求 blind206 graph_only 必须列出）

- **300cn / graph_only / answerable**：翻正 1 ['R083']；翻负 0 []
- **300cn / graph_only / all**：翻正 1 ['R083']；翻负 0 []
- **blind206 / full / answerable**：翻正 1 ['BB-006']；翻负 0 []
- **blind206 / full / all**：翻正 1 ['BB-006']；翻负 0 []
- **blind206 / graph_only / answerable**：翻正 0 []；翻负 1 ['BD-050']
- **blind206 / graph_only / all**：翻正 0 []；翻负 1 ['BD-050']
- **gen120 / full / answerable**：翻正 1 ['GA-11']；翻负 0 []
- **gen120 / full / all**：翻正 1 ['GA-11']；翻负 0 []
- **gen120 / graph_only / answerable**：翻正 2 ['GA-44', 'GA-50']；翻负 0 []
- **gen120 / graph_only / all**：翻正 2 ['GA-44', 'GA-50']；翻负 0 []

---

本表由 `scripts/compendium_rag_p7_delta.py` 现算生成，只读两侧报告；未改图、未改门槛分母、未调 LLM。
