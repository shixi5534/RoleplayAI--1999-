# P9 验收审计：目标 → 证据（只读实算）

条目 38（其中验收条款 33）：通过 31｜待人来出 3｜不符 0｜无凭证 1｜靠登记裁决放行 3。
**目标是否达成：否**（阻塞：gate:v1 × judge_full（终评列）:人工抽检 kappa>=0.80, gate:v2 × 尺子 v1:人工抽检 kappa>=0.80, gate:v2 × 尺子 v2:人工抽检 kappa>=0.80；不符：—）

| 状态 | 归属 | 条目 | 要求 | 证据 |
| --- | --- | --- | --- | --- |
| ✅ pass | acceptance | `D:cbi_testset_500.json` | 交付物 cbi_testset_500.json 存在且非空 | data/compendium_rag/reports/cbi_testset_500.json size=672694 sha16=a11ef75fb2919ead |
| ✅ pass | acceptance | `D:cbi_calculator.py` | 交付物 cbi_calculator.py 存在且非空 | scripts/cbi_calculator.py size=58226 sha16=506134af5271ef93 |
| ✅ pass | acceptance | `D:P9_CBI报告.md` | 交付物 P9_CBI报告.md 存在且非空 | docs/compendium-rag/P9_CBI报告.md size=133460 sha16=5f65fa2129e9cb46 |
| ✅ pass | acceptance | `D:entity_disambiguation_rules.md` | 交付物 entity_disambiguation_rules.md 存在且非空 | docs/compendium-rag/entity_disambiguation_rules.md size=20789 sha16=f808130460b37c78 |
| ✅ pass | acceptance | `T:形状` | 测试集 = 100 角色对 × 5 类查询 = 500 样本；五类各 100、四类冲突族各 125 | samples=500 pairs=100 per_pair=[5] query_type={'direct_private': 100, 'inductive': 100, 'multi_role': 100, 'multi_turn': 100, 'style_probe': 100} conflict={'preference': 125, 'biography': 125, 'secret': 125, 'style': 125} |
| ✅ pass | acceptance | `T:注入纪律` | 对抗性冲突注入「只进上下文、不写图」且公式串与目标一致 | injection_policy 含『不写图』=True formula==目标串=True |
| ✅ pass | acceptance | `G:v1 × judge_full（终评列）` | 六格闸门键集合与目标双向相等 + 权重/目标/分母一致 + 档位独立复算 | CBI=0.9844 现算档位=有条件发布 + 必须出 P10 修复计划 读数档位=有条件发布 + 必须出 P10 修复计划 双向差=[] legacy 差=[] N=0/3/21÷500 人工抽检=未测（无人工标注就没有 κ）(cbi_spotcheck_kappa.json) |
| ✅ pass | acceptance | `gate:v1 × judge_full（终评列）:N_hard==0` | 闸门「N_hard==0」 | 读数 cbi_result_full.json 的 sub_criteria[N_hard==0]=true； |
| ✅ pass | acceptance | `gate:v1 × judge_full（终评列）:N_soft<=5` | 闸门「N_soft<=5」 | 读数 cbi_result_full.json 的 sub_criteria[N_soft<=5]=true； |
| ✅ pass | acceptance | `gate:v1 × judge_full（终评列）:CBI>=0.97` | 闸门「CBI>=0.97」 | 读数 cbi_result_full.json 的 sub_criteria[CBI>=0.97]=true； |
| ✅ pass | acceptance | `gate:v1 × judge_full（终评列）:MRR>=0.39 不回退` | 闸门「MRR>=0.39 不回退」 | 读数 cbi_result_full.json 的 sub_criteria[MRR>=0.39 不回退]=true； |
| ✅ pass | acceptance | `gate:v1 × judge_full（终评列）:Faithfulness>=0.98 不回退` | 闸门「Faithfulness>=0.98 不回退」 | 读数 cbi_result_full.json 的 sub_criteria[Faithfulness>=0.98 不回退]=true； |
| ⏳ pending | acceptance | `gate:v1 × judge_full（终评列）:人工抽检 kappa>=0.80` | 闸门「人工抽检 kappa>=0.80」 | 读数 cbi_result_full.json 的 sub_criteria[人工抽检 kappa>=0.80]=false； |
| 🚩 waived | acceptance | `gate:v1 × judge_full（终评列）:legacy` | 闸门「检索泄漏 ≤3%(≤15/500)」——目标明列的一格，实际未过，靠 2026-10-11 登记裁决降级为能力读数 | legacy_sub_criteria={"N_retrieval<=15（旧子标准·已降级，照实报）": false}；裁决登记在册=True（docs/compendium-rag/P10口径裁决_N_retrieval能力读数.md @ 2026-10-11）；能力读数（≤0.10，不阻塞）={"N_retrieval_rate<=0.10（能力读数·不阻塞）": true} |
| ✅ pass | acceptance | `G:v2 × 尺子 v1` | 六格闸门键集合与目标双向相等 + 权重/目标/分母一致 + 档位独立复算 | CBI=0.982 现算档位=有条件发布 + 必须出 P10 修复计划 读数档位=有条件发布 + 必须出 P10 修复计划 双向差=[] legacy 差=[] N=0/0/30÷500 人工抽检=未测（无人工标注就没有 κ）(cbi_spotcheck_kappa_v2.json) |
| ✅ pass | acceptance | `gate:v2 × 尺子 v1:N_hard==0` | 闸门「N_hard==0」 | 读数 cbi_result_v2instrument.json 的 sub_criteria[N_hard==0]=true； |
| ✅ pass | acceptance | `gate:v2 × 尺子 v1:N_soft<=5` | 闸门「N_soft<=5」 | 读数 cbi_result_v2instrument.json 的 sub_criteria[N_soft<=5]=true； |
| ✅ pass | acceptance | `gate:v2 × 尺子 v1:CBI>=0.97` | 闸门「CBI>=0.97」 | 读数 cbi_result_v2instrument.json 的 sub_criteria[CBI>=0.97]=true； |
| ✅ pass | acceptance | `gate:v2 × 尺子 v1:MRR>=0.39 不回退` | 闸门「MRR>=0.39 不回退」 | 读数 cbi_result_v2instrument.json 的 sub_criteria[MRR>=0.39 不回退]=true； |
| ✅ pass | acceptance | `gate:v2 × 尺子 v1:Faithfulness>=0.98 不回退` | 闸门「Faithfulness>=0.98 不回退」 | 读数 cbi_result_v2instrument.json 的 sub_criteria[Faithfulness>=0.98 不回退]=true； |
| ⏳ pending | acceptance | `gate:v2 × 尺子 v1:人工抽检 kappa>=0.80` | 闸门「人工抽检 kappa>=0.80」 | 读数 cbi_result_v2instrument.json 的 sub_criteria[人工抽检 kappa>=0.80]=false； |
| 🚩 waived | acceptance | `gate:v2 × 尺子 v1:legacy` | 闸门「检索泄漏 ≤3%(≤15/500)」——目标明列的一格，实际未过，靠 2026-10-11 登记裁决降级为能力读数 | legacy_sub_criteria={"N_retrieval<=15（旧子标准·已降级，照实报）": false}；裁决登记在册=True（docs/compendium-rag/P10口径裁决_N_retrieval能力读数.md @ 2026-10-11）；能力读数（≤0.10，不阻塞）={"N_retrieval_rate<=0.10（能力读数·不阻塞）": true} |
| ✅ pass | acceptance | `G:v2 × 尺子 v2` | 六格闸门键集合与目标双向相等 + 权重/目标/分母一致 + 档位独立复算 | CBI=0.982 现算档位=有条件发布 + 必须出 P10 修复计划 读数档位=有条件发布 + 必须出 P10 修复计划 双向差=[] legacy 差=[] N=0/0/30÷500 人工抽检=未测（无人工标注就没有 κ）(cbi_spotcheck_kappa_v2.json) |
| ✅ pass | acceptance | `gate:v2 × 尺子 v2:N_hard==0` | 闸门「N_hard==0」 | 读数 cbi_result_v2instrument_v2_r2.json 的 sub_criteria[N_hard==0]=true； |
| ✅ pass | acceptance | `gate:v2 × 尺子 v2:N_soft<=5` | 闸门「N_soft<=5」 | 读数 cbi_result_v2instrument_v2_r2.json 的 sub_criteria[N_soft<=5]=true； |
| ✅ pass | acceptance | `gate:v2 × 尺子 v2:CBI>=0.97` | 闸门「CBI>=0.97」 | 读数 cbi_result_v2instrument_v2_r2.json 的 sub_criteria[CBI>=0.97]=true； |
| ✅ pass | acceptance | `gate:v2 × 尺子 v2:MRR>=0.39 不回退` | 闸门「MRR>=0.39 不回退」 | 读数 cbi_result_v2instrument_v2_r2.json 的 sub_criteria[MRR>=0.39 不回退]=true； |
| ✅ pass | acceptance | `gate:v2 × 尺子 v2:Faithfulness>=0.98 不回退` | 闸门「Faithfulness>=0.98 不回退」 | 读数 cbi_result_v2instrument_v2_r2.json 的 sub_criteria[Faithfulness>=0.98 不回退]=true； |
| ⏳ pending | acceptance | `gate:v2 × 尺子 v2:人工抽检 kappa>=0.80` | 闸门「人工抽检 kappa>=0.80」 | 读数 cbi_result_v2instrument_v2_r2.json 的 sub_criteria[人工抽检 kappa>=0.80]=false； |
| 🚩 waived | acceptance | `gate:v2 × 尺子 v2:legacy` | 闸门「检索泄漏 ≤3%(≤15/500)」——目标明列的一格，实际未过，靠 2026-10-11 登记裁决降级为能力读数 | legacy_sub_criteria={"N_retrieval<=15（旧子标准·已降级，照实报）": false}；裁决登记在册=True（docs/compendium-rag/P10口径裁决_N_retrieval能力读数.md @ 2026-10-11）；能力读数（≤0.10，不阻塞）={"N_retrieval_rate<=0.10（能力读数·不阻塞）": true} |
| ✅ pass | acceptance | `V:档位口径` | 分档口径：量具用「总式 ∧ 六格子标准」，比目标原文的纯总式分档更严 | 终评列 CBI=0.9844 ⇒ 按目标原文=发布；读数实际判档=有条件发布 + 必须出 P10 修复计划（差异来自1 格子标准未过） |
| ✅ pass | acceptance | `S:v1` | 人工抽检 = 500 的 10% ⇒ 随机层 50 条 | spotcheck_sheet.json 共 52 行，随机层 50（另有非随机必看 2 条不进 κ 分母） |
| ✅ pass | acceptance | `S:v2` | 人工抽检 = 500 的 10% ⇒ 随机层 50 条 | spotcheck_sheet_v2.json 共 53 行，随机层 50（另有非随机必看 3 条不进 κ 分母） |
| ✅ pass | discipline | `X:零写图` | 图未被改动：现场 sha16 与三处读数登记相等，且 owner/visibility 边仍为 0 | 现场 911bb538160db80e / 读数登记 ['911bb538160db80e'] / 边含 owner|visibility 的条数 0（边总数 27110） |
| ❓ unverified | discipline | `D:零云端` | 判定与作答由盲子代理做、不调 LLM 网关 | AST 扫描 scripts/cbi_*.py（只看真 import 与真调用，不被字符串字面量骗）：命中 0 处 []。**这只是静态凭证**：没有运行时网络轨迹或抓包，所以这条只能记『未证』，不能记『已证』 |
| ✅ pass | discipline | `X:未改口径` | 检索格降级是**登记过的裁决**，且明文声明未改公式/权重/分母 | P10口径裁决_N_retrieval能力读数.md 存在=True unchanged=["公式与权重 {hard:1.0,soft:0.5,retrieval:0.3} 不变", "CBI≥0.97 不放宽", "分母仍为 500", "N_retrieval 照实报（21 / 30 不重标）", "旧子标准 N_retrieval<=15 的布尔值照实报"] |
| ✅ pass | discipline | `X:基线实测` | 「当前 0.84」没有被默认接受，而是由自建量具实测出对照基线再报 | 字面口径实测 N_retrieval=260 rate=0.52 上限=0.844（报告里 0.84 出现=True，rate 字符串在册=True） |
| ✅ pass | discipline | `X:适用域` | 两格「不回退」都不由 CBI 集出数（MRR 危险度 / Faithfulness 无支撑域） | exposure 在册（n_gold=12、at_rank1=0、warning=True）；faithfulness 适用域产物逐字命中全 0=True |

> 审计本身绿 ≠ 目标达成：`pending` 是要人出的那一格（人工 κ），`unverified` 是只有静态凭证、没有运行时轨迹的过程条款（零云端）。两者都如实挂在这里：不删、不改判成 pass。
> 反缩水断言：审计预期的闸门键集合与各读数里实际出现的集合**双向相等**，任何一格从量具消失或新增而未覆盖都会直接报红。
> 本件把交付物的 size/sha16 与三处读数的闸门值**快照**在证据列里：所以改了被快照的任何输入（报告、量具脚本、读数）之后 `git status` 会显示本产物变脏——那是「请重跑我」的信号，不是回归；判回归要重跑后看 diff，只有 `status`/`overall` 或闸门数值跟着动才算。
