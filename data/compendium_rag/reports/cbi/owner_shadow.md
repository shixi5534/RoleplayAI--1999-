# P10·R2 影子：owner/visibility 过滤的可挡性与误伤（只读，名形式代理）

> **先读这条**：金标块按构造就是「含 B 名、不含 A 名」的双向独占块（`compendium_rag_p9_cbi_testset.py:165`），所以下面「可零代价挡」与「过滤后 N_retrieval=0」**都是同义反复，不能当 R2 的收益证据**。有经验含量的只有下面两个丢槽率。

- 泄漏复现：影子 **21** 条 = 计算器 21 条 ✅（同集合，未换判据）
- 按题型：{'multi_role': 16, 'inductive': 2, 'multi_turn': 2, 'style_probe': 1}
- 金标锚点块在 top-6：12/21（其余 9 条是**别的**归 B 块命中 ⇒ 泄漏判据比单锚点宽，与计算器里 gold_anchor_in_top6=12 一致）
- 可零代价挡掉（定义性，见上）：**21/21**

| 过滤变体 | 丢掉的槽位 | 丢槽率 | 其中非金标（=误伤） | 误伤率 |
| --- | --- | --- | --- | --- |
| v1 黑名单（挡归 B 且 A 不在场） | 107/3000 | 3.6% | **95** | 3.2% |
| v2 白名单（A 不在场就挡，最激进） | 479/3000 | 16.0% | — | — |

v1 之后剩 ≤2 块（上下文饥饿）的泄漏行数：2/21；索引里找不到的块 0 个。

**v2 的丢槽率才是该拿去比的一条**：它与 P3 角色域过滤器实测的 17–30% 误伤同量级，说明「A 不在场就挡」这种白名单式可见性，代价会直接压在 MRR 上；而 v1 的小误伤率只在本量具的选块约束下成立，换到 eval300/blind206 那种以转述块为 gold 的题集上必然更大。

## 逐条

| sample_id | 题型 | 冲突 | 泄漏块 | A 在场 | B 在场 | 零代价可挡 |
| --- | --- | --- | --- | --- | --- | --- |
| `CC-002-multi_role` | multi_role | biography | `anecdote__1901_雾行者角色故事:0.0.0` | False | True | ✅ |
| `CC-003-inductive` | inductive | secret | `character__19101_漫漫之夜行迹:0.0.0` | False | True | ✅ |
| `CC-003-multi_turn` | multi_turn | secret | `character__19101_漫漫之夜行迹:0.0.0` | False | True | ✅ |
| `CC-003-style_probe` | style_probe | secret | `character__19101_漫漫之夜行迹:0.0.0` | False | True | ✅ |
| `CC-004-multi_role` | multi_role | style | `character__30601_三重赋格:0.0.0` | False | True | ✅ |
| `CC-005-multi_role` | multi_role | preference | `character__22911_洛佩拉玩法剧情:0.0.0` | False | True | ✅ |
| `CC-007-multi_role` | multi_role | secret | `character__17701_小房间:3.0.1` | False | True | ✅ |
| `CC-009-inductive` | inductive | preference | `character__17701_小房间:0.0.0` | False | True | ✅ |
| `CC-009-multi_role` | multi_role | preference | `character__17701_小房间:0.0.0` | False | True | ✅ |
| `CC-009-multi_turn` | multi_turn | preference | `character__17701_小房间:0.0.0` | False | True | ✅ |
| `CC-027-multi_role` | multi_role | secret | `anecdote__1904_埃里克角色故事:1.1.0` | False | True | ✅ |
| `CC-033-multi_role` | multi_role | preference | `character__17701_小房间:0.0.0` | False | True | ✅ |
| `CC-050-multi_role` | multi_role | biography | `character__20603_第一千夜:1.0.0` | False | True | ✅ |
| `CC-061-multi_role` | multi_role | preference | `anecdote__1901_雾行者角色故事:0.0.0` | False | True | ✅ |
| `CC-072-multi_role` | multi_role | style | `character__16601_曲香蒙求:0.0.0` | False | True | ✅ |
| `CC-074-multi_role` | multi_role | biography | `character__22911_洛佩拉玩法剧情:1.0.0` | False | True | ✅ |
| `CC-076-multi_role` | multi_role | style | `character__23601_夜游十字街:0.0.0` | False | True | ✅ |
| `CC-077-multi_role` | multi_role | preference | `character__34701_打虎记:0.0.1` | False | True | ✅ |
| `CC-092-multi_role` | multi_role | style | `anecdote__1901_雾行者角色故事:0.0.0` | False | True | ✅ |
| `CC-095-multi_role` | multi_role | secret | `character__20601_旧金山小子:1.0.1` | False | True | ✅ |
| `CC-097-multi_role` | multi_role | preference | `anecdote__1901_雾行者角色故事:0.0.0` | False | True | ✅ |

## 这条影子能支撑什么决策、不能支撑什么

能：给出两种可见性规则的**上下文代价量级**（丢槽率、饥饿行数），以及名形式代理与真 owner 边的分叉方向。
不能：给出「R2 能把 N_retrieval 降到多少」。金标块的定义就包含「A 不在场」，任何挡住它的过滤器都能把这个通道的读数做到 0 —— **这一格在本量具上不可证伪**，所以批准写图不能凭这条影子。
该凭的是：在 eval300 / blind206 / gen120 三套**以转述块为 gold** 的题集上量 MRR 误伤（P3 实测这类过滤器误伤 17–30%），误伤压过收益就不落地。
另外：图上的边可以按「这段私密是 B 的」来标，而名字代理只能看谁的称呼出现在字面里；转述与代称场景两者必然分叉。
