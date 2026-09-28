# compendium 强模型实体识别（补名）执行报告

对应计划书：`docs/compendium-rag/extraction/compendium强模型实体识别_计划书.md`
执行分支：`plotrag/M0`　日期：2026-09-26

## 0. 裁决记录（阶段 0）

计划书将"强模型识别由谁执行"列为治理阻塞点。用户 2026-09-25 裁决：**强模型直接由主 agent 处理**——识别过程 = agent 亲自读题+候选名表、手写 JSON，与 #36 抽取同形，符合铁律 #1（禁网关、禁云端抽取调用；例外仅限本地 Ollama bge-m3 向量嵌入）。全程零网关触达。

**三题集终判（阶段 1→3 全部跑完，2026-09-26）**：

| 题集 | 主口径（full，强模型补名 − 空映射） | 结论 |
|---|---|---|
| native 250 | **−4.40pt**（去盲敏感性 −5.24pt，§3.5） | 负向 |
| 300_cn answerable 196 | **−0.51pt**（0.801→0.7959）；graph_only +1.02pt | 主口径负向；unanswerable 安全底线 **0.0096→0.0096 成立**；该集可达上限仅 +2.55pt（5 题可救） |
| 题集 i（T1，hit@10） | **+2.16pt，p=0.344**；graph_only +9.73pt；strong−random +5.41pt（p=0.021） | **主闸未过 ⇒ 路线不验收** |

安全底线与逐位复现三集全绿（grounded=1.000、空映射逐位差异 0），机理证据（纯符号通道 +9.73pt）证真"补名有信息、但合入 query 重嵌入会把它冲掉"⇒ 后续方向为**只走 symbol 通道、保留原始 query 嵌入**，而非扩大补名规模。

## 1. 阶段 1：零网关候选生成器

脚本：`scripts/_gen_entity_candidates.py`（图 1-hop 邻域，无任何模型调用）

- 每题 `link()` 取种子（≤6），候选 = 种子邻居名字并集（剔除种子本身），超过 CAP 时按 PPR 排序截断。
- **CAP 敏感性**：CAP=200 时 T1/T1r 覆盖 98.81%/98.8%（维尔汀 364 邻居被截断，gold「斑纹马」被挤出）→ 未过闸；**CAP=400 时零截断**，闸门全绿。
- 产物：`data/compendium_rag/entity_candidates_{native,300_cn}.json` + `entity_candidates_stats_*.json`

闸门结果（native，CAP=400）：

| 池 | n | seeded | cov_seeded（金标在候选表中） | truncated |
|---|---|---|---|---|
| T1 | 84 | 84 | **1.000** | 0 |
| T1r | 83 | 83 | **1.000** | 0 |
| T2 | 83 | 48 | 0.4375（不在补名射程） | 0 |

候选规模：中位 39 / p90 196 / max 364。300_cn 整体 cov 21.3%（seed 命中低，属预期）。

**阶段 1 闸门：native T1/T1r 覆盖 = 100% ✅**

## 2. 阶段 2：主 agent 逐题识别（离线映射）

冻结协议：识别时每题只见 `qid + query + 扁平候选名表`（无图边、无度数、无 gold、无检索结果——计划书 §8 反循环性红线 R2）。

- 题料：`data/compendium_rag/er2/batch01..09.txt`，215 道 seeded native 题（含已命中题，防"miss 子集投射"，§6）。
- 作答：`data/compendium_rag/er2/picks_raw.tsv`（215 行；N009/N138/N234 无候选，空答）。
- 白名单 resolve：`graph_store.resolve(name)`，失败即丢弃该 pick（不自由发挥实体名）。解析率 **250/255 = 98.04% ≥ 90% ✅**（5 个失败均为凭记忆写出、不在该题候选表中的名字：N027 萨赫蛋糕、N030 完全数、N115 维也纳事件、N131 会长、N134 圣洛夫基金会——护栏按设计正确拒绝）。
- 产物：`data/compendium_rag/entity_map_native.json`——215 qid，207 题非空，共 250 个 eid。

诚实性备注：N038/N055 在 CAP=200 截断诊断阶段见过 gold 名单，**非严格盲测**，已在映射文件 `note` 字段标记。

**阶段 2 闸门：解析率 98.04% ≥ 90% ✅**

## 3. 阶段 3：离线回放评测

脚本：`scripts/_replay_entity_map.py`（复用 eval300 的 Case/score_case/summarize，检索代码零改动；q' = q + 补名，两模式 full/graph_only）。

### 3.1 零档自检（L4 安全线）✅

`--set native --map none` → **差异行数 0**（逐位复现 `eval_native_after_welds.json`），full 250/250、graph_only 250/250，全 all hit@6=0.632 / MRR=0.4264 / grounded=1.0。回放 harness 与基线同口径成立，映射档测量有效。

### 3.2 映射档（native 强模型补名）——**负向**

对照基线（after_welds，full）hit@6=0.632 / MRR=0.4264：

| 模式 | hit@6 | MRR | grounded | up | down | 净 |
|---|---|---|---|---|---|---|
| **full** | **0.588**（−4.4pt） | 0.4230 | 1.000 | 14 | 25 | **−11** |
| graph_only | 0.496 | 0.3725 | 1.000 | 20 | 18 | +2 |

- unanswerable 分层：native 250 题**全部 answerable**（unanswerable=0），"不升"约束本集 N/A。
- 逐题（full）：up=N005,N011,N016,N038,N040,N055,N061,N074,N109,N136,N148,N160,N212,N213；down=N014,N019,N021,N025,N059,N063,N107,N113,N118,N129,N141,N143,N152,N173,N191,N200,N203,N204,N210,N211,N222,N229,N232,N237,N241。
- 逐题（graph_only 对照）：up=N001,N010,N038,N041,N055,N064,N071,N097,N102,N109,N148,N150,N152,N175,N194,N206,N213,N215,N240,N246；down=N005,N017,N025,N036,N057,N063,N091,N092,N101,N107,N112,N173,N181,N195,N204,N205,N211,N238。

**结论（诚实）：native 线上「强模型补名」在真实工作模式 full 下净 −11 题命中、hit@6 −4.4pt，未过"answerable hit@6 提升"闸——与计划书 §6 灰机盲猜 −8.80pt 同向。** 机理：native T1/T1r 题面**本就点名锚点实体**，追加识别到的名字对嵌入 q' 是冗余+扰动，改变向量通道与 RRF 融合排名，把 gold 块挤出 top-6（graph_only 因不吃嵌入扰动，仅 +2 近持平，佐证扰动主要来自 full 的向量融合）。**修正见 §3.5：剔除 2 道非盲题（N038/N055，均在 up 里）后 graph_only 净效应为 0、full 恶化至 −5.24pt。**

**这恰恰是题集 i 的立项动机**：题集 i 题面为盲写自然语言、**不点名实体**，补名应提供**新增可达信号**而非冗余扰动。native 判负不构成对补名路线的终审，其角色降为 L4 逐位复现安全线（已过）。最终验收以 **题集 i 五臂对照**（`_iset_eval5.py`，见 `docs/compendium-rag/extraction/题集i_预注册与冻结记录.md` §7）为准：L1 全量 hit@10≥0.7 且 strong 同时优于 empty 与 random、McNemar p<0.05。

（300_cn `--map none` 零映射安全回归：已实际跑完并复算，见 §3.3——600 行逐位差异 0，PASS。）

### 3.3 300_cn 双题集回归（计划书 §6「两套都要报」+ unanswerable 安全线唯一可测集）

native 250 题全部 answerable，**「unanswerable 不升」这条最重要的安全底线在 native 上是空真**；只有 300_cn（unanswerable hit@6=0.0096）能非平凡地测它，故本轮补齐 300_cn 的识别与回放。

**阶段 1（300_cn 候选表，零网关）**：`entity_candidates_stats_300_cn.json` — cap=400，n=300，seeded=272（有 seed 的题），cov_seeded=**0.2353**（seeded 题中「gold 实体/关键词落在候选表内」的比例），cands_median=31，p90=202，truncated=5，**31 题候选表为空**。
覆盖率远低于 native（**闸门口径 T1/T1r 均 =1.000**；native 三池合算 overall=0.8744）是**构造性差异**，不是识别失误：300_cn 题面多为不点名实体的自然问法，`link()` 要么取不到 seed（31 题名字表为空），要么把 seed 落在错误实体上（⇒ 有 seed 的 272 题里只有 23.53% 的 gold 进入名字表）。因此 300_cn 上「能识别的题」天然受限。
独立回算（直接从 `entity_candidates_300_cn.json` 逐题重数）：n=300、`n_seeds>0` 的题 **272**、空表 **31**、长度达 cap=400 的题恰 **5** 个（R176、R236、R281、R289、R292 = truncated 计数）；272 与「非空表 269」差的 3 题（R029、R104、R108）是 seed eid 不在 `g.entities` 中、被 `names` 推导式过滤所致，与脚本逻辑一致。

**阶段 2（主 agent 盲识别，`er2/300_cn/`）**：15 个批次文件（300 行、317,850 字符）逐题识别，规则与前两轮一致且更保守——**只选逐字出现在该题候选表内、且与答案有明确别名/指向关系的名字；题面已点名该实体（如「『露西』的英文写法是什么」）视为冗余不选；无把握即弃答**。
合并与双校验：`scripts/_er_merge_map.py --set 300_cn` → `entity_map_300_cn.json`。
- 提议 **75** 个名字 → 白名单/resolve 保留 **73** = token 合法率 **0.9733**；
- 被护栏丢弃 2 个：R047「时空灾害研究负责人露西」（该名字是图谱实体，但不在 R047 自己的候选表里——从相邻批次误带，护栏按设计拒绝）、R255「暴雨」（R255 候选表只有「第十次暴雨」，无裸「暴雨」）；
- **全合法题占比 = 0.9933 ≥ 0.90 闸门 ✅**；非空映射题 **72/300 = 0.24**（其余 228 题弃答）。
- 安全底线暴露面（离线按 eval300 同口径 `_answerable = 任一 evidence 关键词出现在语料` 复算，300_cn：answerable **196** / unanswerable **104**，与基线分层一致）：72 道被补名题中 **60 道 answerable、12 道 unanswerable**（R002、R062、R063、R076、R091、R098、R128、R143、R145、R160、R165、R230）。⇒ 「unanswerable 不升」在此集只有这 12 题能触发；主口径覆盖 60 题只是**份额上限**（60/196=30.61pt），真实可达上限受基线限制：**full 仅 5 题可救 ⇒ +2.55pt，graph_only 12 题 ⇒ +6.12pt**（见 §3.3 阶段 3）。实测幅度须按此归一化解读，**不可与 native/题集 i 的全覆盖口径直接比大小**。

**阶段 3 回放（两份，均已实际跑 Ollama 端 full+graph_only 各 300 题）**：
- 零档自检 `--map none` → `reports/replay_300cn_zero.json`：`scripts/_er_report_gates.py --set 300_cn` 现场复算 → **600 行 / 基线 600 / 对齐 600，逐位差异 0 行 = PASS**（native、300_cn 双题集 L4 安全线均成立；回放 harness 与基线同口径，映射档测量有效）。
- 映射档 `--map entity_map_300_cn.json` → `reports/replay_300cn_map.json`（2026-09-26 落盘并现场复算，`scripts/_er_report_gates.py --set 300_cn`）：
  - **full（主口径）**：answerable hit@6 **0.801 → 0.7959（−0.51pt，未提升 ⇒ FAIL）**，MRR 0.6147→0.6401；all 0.5267→0.5233（−0.34pt）；unanswerable hit@6 **0.0096 → 0.0096（+0.00pt ⇒ 安全底线 PASS）**；grounded **1.0**（全分层）。逐题翻转 up=1（R142）/ down=2（R022、R199），三题**全部落在映射覆盖的 72 题内**（未覆盖题 0 翻转 ⇒ 无随机性混杂）；McNemar b=1 c=2 **p=1.00000**。
  - **graph_only**：answerable hit@6 0.6684→0.6786（**+1.02pt**）、all 0.44→0.4467、MRR 全线上升；unanswerable 0.0096→0.0096（PASS）；up=6（R057、R088、R142、R177、R262、R280）/ down=4（R021、R022、R246、R289）。
  - **归一化解读（重要）**：主口径可动上限不是「60/196 = 30.61pt」这个覆盖份额，而是**覆盖且基线未命中的题数** —— full 只有 **5 题可救**（上限 0.8265，+2.55pt），实测 −0.51pt ⇒ 5 题中救回 1、反损 2；graph_only 有 **12 题可救**（上限 0.7296，+6.12pt），实测 +1.02pt。即 300_cn 上强模型补名的**可证收益空间本身极小**，不能与全覆盖题集直接比大小。
- 闸门报告落盘：`reports/er_300cn_gates.md`。

### 3.4 证据复核（2026-09-26 独立回算）

本节数字全部从落盘产物重新推导核对，非记忆复用：
- 阶段1 `entity_candidates_stats_native.json`：CAP=400，T1 84/84、T1r 83/83，cov_seeded 均 =1.000，truncated=0。
- 阶段2 `entity_map_native.json`：215 qid / 207 非空 / 250 eid（白名单 resolve 后）。
  - **解析率独立回算**（`er2/picks_raw.tsv` ↔ 映射文件逐题比对，「、」分词）：提议 255 个名字 → 保留 250 = **0.9804**，被丢弃的 5 个恰为 §2 记录的 N027 萨赫蛋糕 / N030 完全数 / N115 维也纳事件 / N131 会长 / N134 圣洛夫基金会（均不在该题候选表中，护栏按设计拒绝）；空答 3 题 N009/N138/N234 与"无候选"一致。数字可从落盘产物复现，非记忆复用。
- §3.1 L4：`replay_native_zero.json` vs `eval_native_after_welds.json`，500/500 行按 (qid,mode) 对齐，度量列（hit/rr/grounded/seed_hit/n_evidence/n_edges）**逐位差异 = 0**。
- §3.2：`replay_native_map.json` 逐模式回算 hit 翻转——full up14/down25 净 **−11**（hit@6 158→147）、graph_only up20/down18 净 **+2**。文件顶层 `up`(29)/`down`(37) 是**跨两模式按 qid 去重**的集合（同一 qid 可 full 降、graph_only 升，如 N005），故不与逐模式净值相加。
- §3.3 300_cn 阶段 2 **脱离合并脚本的第三次独立回算**（直接读 `er2/300_cn/picks_raw.tsv` + 该题候选表，「、，,」分词逐 token 判白名单）：行数 300 / 重复 0、提议 **75** → 保留 **73**（token 合法率 **0.9733**）、全合法题 **298/300 = 0.9933**、被弃 2 名逐字复现为 R047 时空灾害研究负责人露西 / R255 暴雨，`unresolved` 空；把回算的合法子集与 `entity_map_300_cn.json` 的 `map` 逐题排序比对 → **不匹配题数 0**。非空题 **72/300 = 0.24** 亦复现。
- §3.3 300_cn 安全线暴露面回算（读 `replay_300cn_zero.json` 的 `answerable` 标记，full 模式）：分层 **answerable 196 / unanswerable 104**，与基线一致；72 道被补名题中 **60 answerable + 12 unanswerable**，12 题号复现为 R002、R062、R063、R076、R091、R098、R128、R143、R145、R160、R165、R230；基线 full answerable hit@6=**0.801**、unanswerable hit@6=**0.0096**。**可动上限修正（2026-09-26，逐题回算覆盖题的基线命中状态）**：30.61pt 是 60/196 的**份额**而非可达上限 —— 覆盖的 60 道 answerable 题中基线**未命中仅 5 道** ⇒ full 真实可达上限 **0.8265（+2.55pt）**，graph_only 未命中 12 道 ⇒ 上限 **0.7296（+6.12pt）**；unanswerable 侧 12 道全覆盖题基线全未命中 ⇒ 安全线最大可恶化 **11.54pt**（0.0096→0.1250），实测 0.00pt。
- §3.3 300_cn L4 零档：`scripts/_er_report_gates.py --set 300_cn --zero reports/replay_300cn_zero.json` → 行数 600 / 基线 600 / 对齐 600、度量列逐位差异 **0**，落盘 `reports/er_300cn_gates.md`。

### 3.5 盲性瑕疵披露与去盲敏感性分析（审计脚本 `scripts/_er_audit_completion.py` 扫出）

全量扫描三题集的**原始识别记录**（不是合并后的 map）时，发现 native 的 `er2/picks_raw.tsv` 有 **2 行带自述批注**：

```
N038  斑纹马  # seen_gold(截断诊断时见过)
N055  斑纹马  # seen_gold(截断诊断时见过)
```

即这两题在做识别判断前，我在**候选生成器的截断诊断**输出里已经见过 gold 名字 ⇒ 这两行的「盲」不成立。批注当时就写进了原始记录（未删），合并脚本按 TSV 契约只读第 2 列，故批注未进入 map；但 map 里 N038/N055 的「斑纹马」确实是**非盲条件下产出**的。300_cn 与题集 i 的原始记录经同一扫描器检查：**0 行批注、0 个额外字段**，盲性完整。

**去盲敏感性（把这两题整题剔除后重算 §3.2）：**

| 模式 | 全样本（发布口径） | 剔除 N038/N055 |
|---|---|---|
| full | hit@6 0.632→0.588（−4.40pt）up14/down25 净 **−11** | 0.637→0.585（**−5.24pt**）up12/down25 净 **−13** |
| graph_only | 0.488→0.496（+0.80pt）up20/down18 净 **+2** | 0.492→0.492（**+0.00pt**）up18/down18 净 **0** |

⇒ 结论方向不变且**更不利**：native full 的负向不依赖这两题（剔除后从 −4.40pt 变为 −5.24pt）；但 §3.2 里「graph_only +2 近持平」这句需修正为——**去掉非盲两题后 graph_only 净效应恰为 0**，native 线上补名对纯符号通道也没有可测量的增益。此前"+2 近持平"的表述偏乐观，此处以去盲数字为准。

**对终审的影响：无。** native 本就是判负档（只充当 L4 安全线与机理证据）；决定路线成败的**题集 i 完全盲**（五臂 strong−empty +2.16pt / strong−random +5.40pt、up/down 题号均未涉及任何非盲行），其数字不受此瑕疵污染。审计脚本把该行扫出并单列为 `E 盲性披露 = DISCLOSED`，属流程自净成功而非隐藏。

## 4. 终审：题集 i 五臂对照（`_iset_eval5.py`，2026-09-26 完成）

反循环盲测集（题面不点名实体、287 题，主口径 L1=全量 T1 n=185）五臂同跑，full + graph_only 双模式。产物 `data/compendium_rag/reports/eval5_set_i.json`，闸门表 `set_i_gates.md`。

**L1（full 模式，hit@6 / hit@10 / MRR）：**

| 臂 | hit@6 | hit@10 | MRR | grounded |
|---|---|---|---|---|
| empty | 0.8919 | 0.9243 | 0.661 | 1.000 |
| random | 0.7946 | 0.8919 | 0.5534 | 1.000 |
| alias | 0.8703 | 0.9135 | 0.6278 | 1.000 |
| vector | 0.8432 | 0.8973 | 0.6078 | 1.000 |
| **strong** | **0.9027** | **0.9459** | **0.7099** | 1.000 |

**graph_only（纯符号通道，L1 hit@10）：** empty 0.773 → **strong 0.8703（+9.73pt）**；random 0.6703、alias 0.7622、vector 0.7135。

**预注册闸门（L1/T1，hit@10）：** ① ≥0.70 ✅（0.9459）；② strong−empty ≥+5pt & McNemar p<0.05 → **+2.16pt、b=7 c=3 p=0.344 ✗**（up7: i053,i076,i087,i157,i168,i227,i334；down3: i141,i228,i285）；③ strong 优于 random → **+5.40pt、b=13 c=3 p=0.021 ✅**；④ grounded=1.000 全臂 ✅。

**终审结论（诚实）：** 补名路线**方向被证真、用法被证伪**。识别信号真实且强可达——纯符号通道 +9.73pt，strong 在两模式全指标（hit@6/hit@10/MRR）居五臂之首、显著优于随机。但预注册主闸口径是 full 模式，full 下仅 +2.16pt（p=0.344，未过）：**根因是把补名并入整条 query 再嵌入，扰动了向量通道**（与 native §3.2「full −11 / graph_only +2」同源）。⇒ **native 判负、题集 i full 未过主闸、但 graph_only 与优于 random 证明路线内核成立**。后续修复任务（非本轮闸内项）：补名只入符号通道（PPR 种子/graph 权重），嵌入仍用原 query，预期把 +9.73pt 的大部分带回 full，再重跑复核主闸。阶段 4 线上接线（StaticMapIdentifier）因主闸未过**不触发**。

## 5. 完成度审计（2026-09-26 独立复算，逐条对齐计划书闸门）

所有数字从落盘产物重新推导，非记忆复用；判据为「产物存在 + 数字可复算」，不接受代理信号。

| 闸门 | 判据来源 | 复算结果 | 结论 |
|---|---|---|---|
| 阶段1 native T1/T1r 覆盖=100% | `entity_candidates_stats_native.json` | T1 84/84、T1r 83/83，cov_seeded=1.000，truncated=0，CAP=400（overall cov_seeded=0.8744，T2 池拉低，非闸门项） | ✅ |
| 阶段1 均值邻域 ≤ CAP | 同上 `cands_max` + 生成器截断逻辑 | native max=364、300_cn max=400 均 ≤ CAP=400；**该条由构造成立**（超 CAP 必先按 PPR 截断），非独立信息量 | ✅（构造性） |
| 阶段0 治理裁决（阻塞项：触网关） | 用户注册目标指令 | 识别改由**主 agent 亲自盲判**完成，全程零网关、零云端调用（仅本地 Ollama 嵌入）⇒ 铁律 #1 冲突消解，阶段 1 起可动工 | ✅ |
| 阶段2 解析率 ≥90%（**三题集**，token 口径独立回算） | 各集**原始识别记录** ↔ 该集候选表 ↔ `graph.json` 实体名（`scripts/_er_audit_completion.py`，脱离合并脚本） | native 255→250=**0.9804**；300_cn 75→73=**0.9733**；题集 i 713→711=**0.9972**，三集均 ≥0.90；map 全量违例（白名单/resolve）**均为 0** | ✅ |
| 阶段3 全量口径 hit@6/MRR/grounded | `replay_native_map.json`、`replay_300cn_map.json` | native full 0.632→0.588 / 0.4264→0.4230 / 1.000；graph_only 0.488→0.496。300_cn full answerable **0.801→0.7959（−0.51pt）**、MRR 0.6147→0.6401、grounded **1.0**；graph_only answerable **+1.02pt** | ✅ 已测（native 负向 §3.2；300_cn 主口径负向、可达上限仅 +2.55pt §3.3） |
| unanswerable 不升 | `replay_300cn_map.json` 非平凡实测 | native 250 题 answerable=250、unanswerable=0（约束空真）；**300_cn：0.0096→0.0096（+0.00pt，被补名的 12 道 unanswerable 题无一转命中）⇒ 安全底线 PASS**（该组可恶化上限 11.54pt） | ✅ 非平凡成立 |
| 空映射逐位复现 `eval_*_after_welds.json` | `replay_native_zero.json` vs 基线；`replay_300cn_zero.json` vs 基线 | native：500/500 行对齐、6 度量列差异 **0**；300_cn：600/600 行对齐、差异 **0** | ✅ 双题集 |
| 逐题 up/down 题号 | §3.2、§3.3 | native full up14/down25、graph_only up20/down18 题号全列已落文档；**去盲敏感性（剔 N038/N055）：full −5.24pt/净 −13、graph_only +0.00pt/净 0**（§3.5）。300_cn full up1（R142）/down2（R022、R199）、graph_only up6（R057、R088、R142、R177、R262、R280）/down4（R021、R022、R246、R289），**全部落在 72 道被补名题内**，未覆盖题 0 翻转 ⇒ 翻转可完全归因于补名 | ✅ 含敏感性 |
| 识别过程盲性（原始记录扫描） | `scripts/_er_audit_completion.py` 判据 E | native `er2/picks_raw.tsv` 有 **2 行自述 `# seen_gold(截断诊断时见过)`**（N038/N055）⇒ 已披露并做去盲敏感性（§3.5），结论方向不变且更不利；300_cn、题集 i 原始记录 **0 批注 / 0 额外字段**，盲性完整 | ⚠️ 已披露（native 2 行非盲）；i/300_cn ✅ |
| 审计可重放（不留一次性人工核对） | `scripts/_er_audit_completion.py`（离线只读、全量范围、PENDING≠PASS 的退出码：0/1/2） | 300_cn 映射档落盘后复跑：**18 条判据 0 FAIL / 0 PENDING，退出码 0**（落盘 `reports/er_completion_audit.md`）；题集 i 主闸数字由 rows 现场重算并与 `gates` 打印值一致（Δempty +2.16 / Δrandom +5.41、up/down 题号逐项相等）；判据 E 为**已披露**（native 2 行非盲），非 PASS 非 FAIL | ✅ |
| 题集 i 冻结完整性 | `rag_testset_i.json` | 全文件 SHA256 `035bf4e17acae5c2…` 逐字匹配；L1 指纹 `6a020d07ba27ff8d` 复现（算法：`sha256("\n".join(sorted(id)))[:16]`，字段为 `id`/`_pool`）；pool `{T1:185,T2i:58,MULTI:44}` | ✅ |
| 题集 i 反循环机检 | 同上 | `evidence` 答案词出现在题面 = **0**；题面含 `relation::`/`::`/`degree` = **0**。（以 `_gold_name` 判会误报 i163：其 gold 实体「无名者」是题面锚点，答题词为「格蕾丝」不在题面） | ✅ |
| 题集 i 五臂数字非陈旧打印 | `eval5_set_i.json` rows 重算 | 五臂 hit@6/hit@10/MRR/grounded、strong−empty full **+2.16** / graph_only **+9.73**、L2 MULTI/T2i 全部与 `set_i_gates.md`、§4 一致 | ✅ |
| 零网关（铁律 #1） | `grep` 本路线 6 个新脚本 | 无 `requests/httpx/urllib/openai/anthropic/api_key` 等任何网络端点；嵌入仅经 `src/compendium_rag/config.py:OLLAMA_BASE_URL` → `embedder.py` 的 `127.0.0.1` 本地 Ollama | ✅ |

**主闸结论：题集 i full 模式 strong−empty = +2.16pt、p=0.344，未过「≥+5pt 且 p<0.05」⇒ 路线未达验收，阶段 4 不触发。** 此为本轮诚实终判，未以任何口径调整来换取通过。

### 5.1 证据链持久性（已按用户决策入库，2026-09-26）

2026-09-26 用 `git ls-files --error-unmatch` + `git check-ignore` 逐文件实测发现本路线三层产物**当时全部不在版本控制里**，且成因是两条不同规则：`data/*`（`.gitignore:13`）让证据层连 `git add` 都拒绝、必须 `-f`；而文档与代码层**根本没被忽略**，只是本轮从未提交。当时唯一可复算形态是"本机工作区"，一次 `git clean -fdx` 或换机即整体丢失（含审计脚本自身）。

经用户选择「文档+脚本先提交，证据 -f 随后」后，已落地两个提交并逐文件复核：

| 层 | 文件 | 归属提交 | 入库方式 |
|---|---|---|---|
| 文档 | 本执行报告、`计划书`、`题集i_预注册与冻结记录`、`补名路线_灰机实证`、`召回率_下一步路线评估`（后两篇被前两篇交叉引用，纳入以保持自洽） | `3759f61` docs(plotrag) | 普通 `git add` |
| 代码 | `_gen_entity_candidates.py`、`_gen_identify_batches.py`、`_er_merge_map.py`、`_er_report_gates.py`、`_er_audit_completion.py`、`_replay_entity_map.py`、`_iset_{annotate,eval5,freeze,make_id_view,merge_map,prepare_material,report_gates}.py`（共 13 个） | `3759f61` docs(plotrag) | 普通 `git add` |
| 证据 | `entity_candidates_{native,300_cn,i}.json`(+`_stats_*`)、`entity_map_{native,300_cn,i}.json`、`er2/`（批次文件 + 两份 `picks_raw.tsv` + 运行日志）、`reports/replay_{native,300cn}_{zero,map}.json`、`reports/eval5_set_i.json`、`reports/{er_native_gates,er_300cn_gates,er_completion_audit,set_i_gates}.md` | `0ce2b14` chore(evidence) | `git add -f` |
| 证据（最原始识别记录） | `data/eval_set_i/id_out/batch_{01..19}.out.jsonl` —— 判据 E 盲性扫描的输入，不可由任何已提交产物推导 | `0ce2b14` chore(evidence) | `git add -f` |
| 题集 | `data/knowledge/_audit/rag_testset_i.json`（287 题冻结集本体，未被忽略） | `0ce2b14` chore(evidence) | 普通 `git add` |

两提交合计 88 个新文件 / 194,536 行。基线 `reports/eval_{native,300_cn}_after_welds.json` 经实测**此前已在库中**，故逐位复现的参照物同样可取。**未入库**：`data/eval_set_i/{material,drafts,id_batches}`（≈3.6MB 写手材料与识别视图）—— 均可由已提交的脚本 + `graph.json` 快照确定性重建，属可推导产物，故按计划排除。当前 `git status` 仅剩 Live2D 工作流的 4 个未跟踪项，本路线工作区已干净。

**入库后实测的可复算边界（区分两件事，勿混称"可复现"）**：
- ✅ **判读可复算**：`_er_report_gates.py` 与 `_er_audit_completion.py` 全部 18 条判据只读 `graph.json`（已跟踪）+ 本次入库的 replay/eval5/原始识别记录，fresh clone 即可原样重跑并得到同一张表。**已实测**：`git worktree add ../_ercheck HEAD` 建出干净工作副本，在该副本里跑两脚本 → 审计 **18/18 非 FAIL 非 PENDING、退出码 0**，`--set 300_cn` 闸门同样退出 0 且首行仍为「600/600/对齐 600，差异 0 行」；随后 `git worktree remove` 清理。
- ⚠️ **回放需本机索引**：`_replay_entity_map.py` / `_iset_eval5.py` 依赖 `data/compendium_rag/{chunk_index,entity_index}.npz` 与 `chunks.json/corpus.json`（大二进制，经 `git ls-files` 实测**未跟踪**）+ 本地 Ollama。即换机可复算"结论"，但**重新产生** replay 需先按 #36 流程重建索引；因此本轮把四个 replay 与 eval5 产物一并入库，正是为了让结论不依赖该重建。
