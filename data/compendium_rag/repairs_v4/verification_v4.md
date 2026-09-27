# R4 独立复核报告（verification_v4）— 2026-09-26

- **复核人**：R4-verifier（独立代理；未参与提案撰写，不给看 Repairer 推理，仅凭 proposal + 同标准源独立重推——作战书 §2.2）
- **对象**：`repairs_v4/proposal.json`（77 remove_alias + 1 keep_with_note）+ 三份 sidecar + `time_consistency_audit.md` + `_selfval.json`
- **图状态**：7033 实体 / 29957 边，fingerprint `7dc29bf90681a3f7`（读图确认）；全程零网络、全程只读（graph.json md5 干跑前后一致 `2b66313aa31ddb817ed41de45a61471b`）
- **方法**：全部结论出自自写脚本独立重推（graph.json/chunks.json/双测试集/三份标准源），仅与 proposal 做集合级 diff；中间产物与脚本在复核侧临时目录，不落仓库

## 0. 总裁决

| 项 | 结论 |
|---|---|
| 逐条复核（78 条） | **agree 78 / disagree 0 / insufficient 0** |
| R4-K01 仲裁（被提案搁置的决策） | **remove**（非阻塞；keep-with-waiver 亦安全；qualify 不可行） |
| 死别名清单（D1） | **agree** — 独立重算集合与提案 78/78 完全一致 |
| 标注 sidecar（D2） | **agree** — 三类集合双向 0 差，抽检全过 |
| 版本映射（D3） | **agree** — 3695 全覆盖、156 null 逐块对账、规则 0 diff |
| 时间审计（D4） | **agree** — 201/A117/B81/C3 复现，0 删边成立 |
| 自验证复现 | **reproduced** — 0/420 种子 diff；Applier 干跑全绿 |
| **must-fix-before-apply** | **无** |

## 1. D1 死别名清理（77 remove + K01）— agree

**清单对账**：按 作战书/QC 检3 同口径（alias 不逐字出现在属主任一声称 chunk；DF=3695 块子串计数）对全图 994 条 alias 声明独立重算 → **死别名 78 条（nowhere 58 / elsewhere 20）**，与提案 77 条 remove + K01 的集合**完全一致（0 漏 0 多）**。 nowhere/elsewhere 构成 58/19(remove)+1(K01 elsewhere) 与提案 §1 一致。

**基线对账复现**：对 `backups/graph.json.prev.r1r2` 同口径重算 = **79 死 / 1023 声明**，与 QC（79/1023）一致。79→78 漂移三笔逐条复现：`+（兀尔德, 原初的兀尔德）`（R1 合并传记作家兀尔德时继承，仍死，df_corpus=0）、`−（传记作家兀尔德, 原初的兀尔德）`（属主被合并）、`−（逃兵, 两人）`（R2 泛称摘除连带）。

**逐条检查（78/78 通过，0 错误）**：属主存在 ✓、alias 现存 ✓、df_in_owner=0 ✓、evidence.df_corpus 与复算一致 ✓、elsewhere 例块摘录经归一化（⏎ 换行/`**` 加粗剥离）后**全部逐字命中**所指 chunk ✓、类标（nowhere/elsewhere）与实测一致 ✓。样例数字复现：`外国@爱琴海` DF=21/10docs、`至高的秩序@真理` DF=1、K01 `诊疗` DF=41/12docs。

**例外扫描复现**：420 查询（300_cn 300 + gen_r1r2 120）对 78 条死别名的包含扫描 → **唯一命中 `诊疗@诊所`（gen_r1r2 GA-25）** ✓；`alias==他实体规范名` = **0 例** ✓。

**3 条多主摘除复核**：
- `特里格拉夫战列舰`：两名属主（特里格拉夫/特里格拉夫号）均死、全语料 DF=0 → 摘除后 alias 键整体消失，无任何规范名碰撞；
- `高地据点`：299高地 死 / 地下堡垒 **活**（`mainline__111_行于漫漫长路上:20.1.0` 玛丽安娜台词逐字含"高地据点"）。模拟证实 `alias_index[高地据点]` **当前指向死属主 299高地**，摘除后按 setdefault 语义重路由→活的 地下堡垒——**属改善而非风险**，提案判断正确。

## 2. R4-K01 仲裁 — verdict: **remove**（非阻塞）

事实底座全部复核无误：诊疗@诊所 死别名（属主 6 块 0 命中）；GA-25『在诊疗室门前等待时…』是 420 题唯一命中。但 **keep 的保护前提经量化不成立**：

1. **GA-25 当前战绩**（eval_gen_r1r2.json）：`hit=true, rr=1.0, seed_hit=false` —— 该题的命中**不来自种子通道**，0.9 的 诊所 种子不是命中来源；
2. **摘除后的种子集**（真 link() 模拟）：`伊索尔德@1.0 + 索尔@1.0 + 诊疗室@1.0` 保留，仅失去 `诊所@0.9`。关键：**诊疗室 是图中独立规范实体**，其声称块 = `character__17701_小房间:7.0.4/7.0.5`，**恰是 GA-25 的 gold 文档** —— gold 锚点不受影响，且被移除的 诊所 种子携带 3 个跨篇噪声文档（犹在镜中/今夜星光灿烂/孤独之歌）；
3. **420 题种子集恰变化 1 条**（仅 GA-25）；
4. **qualify 不可行**：诊疗室 不在 诊所 6 个声称块逐字（红线3 违例），且已是独立实体（改挂即撞名）。

**执行建议（二选一，均安全）**：(a) 本版把 K01 改为 remove_alias（78/78 全清）；此时落盘后复验**必须包含 gen_r1r2 检索指标**——预注册闸门 §3 只列 300_cn+native，GA-25 不在清单内，这是唯一需要补的监督点；(b) 按 proposal 原样 keep-with-waiver 落盘（apply 后检索行为零变化），remove 移交 R5。K01 条目本身是"留 Verifier 裁决"的 deferral 载体，事实无误，故条目级 verdict=agree。

## 3. D2 实体标注 sidecar — agree

- 全量重算三分类：**ok 5947 / claimed_mismatch 121 / none 965**，与 sidecar 集合**双向 0 差**（none: 0/0，mismatch: 0/0）。
- 账目自洽：唯一 eid **1096** = 965 none + 121 mismatch + 9 per_story_generic + 1 metaphor；警卫/水手 的 cross_story_audit 并入 9 泛称之内 ✓。
- 抽检：**20/20** none（含指定的 探险家别斯米尔——规范名全语料 0 命中，确认 R1 命名形态非本版引入）、**10/10** claimed_mismatch（名不在己块、df>0、elsewhere_docs 吻合）、**9/9** per_story_generic 的 story_scope_docs 与 post-R3 实际篇目一致——`店主` 经 R3 拆出 店主米拉 后确已收敛为 第一千夜×3 单篇 ✓。
- 跨篇审计：警卫（4 块 4 篇）/水手（2+1 块 2 篇）实例数逐块核实，keep_no_split 判定的规模前提成立；玩具盒 metaphor 的 `玩具盒子` 在其唯一声称块逐字在场 ✓。
- pre-R1 基线复算：**967 none / 122 mismatch**，与 QC 完全一致。

## 4. D3 版本映射 sidecar — agree

- 覆盖 **3695/3695**（无缺无多）；**156 null 恰 = 3 联动 doc（翡冷翠之春 40 + 入雅典记 30 + 聚合浪潮 55 = 125）+ 4 附录 doc（2+3+14+12 = 31）** ✓。
- 151 doc 规则**独立重推 0 diff**（mainline 查表 × clean_report rows 交叉、activity XY101 × huiji_canon 版本弧交叉、character/anecdote/appendix 同构验证）；置信分布 high 119 / low 25（anecdote→1.9 推定，如实标 low）/ none 7。
- 30 块跨 5 类抽检（mainline 6 / activity 7 / character 5 / anecdote 6 / appendix 6）**全过**；三个 null 联动 doc 均在 clean_report `missing_version` 清单中得到印证。
- meetability 口径复核：无任何版本化 chunk 的边 **1243** / 触及 null 块的边 **1245**，与提案 meta 一致。

## 5. D4 时间一致性审计 — agree

- 独立重算跨版本边 = **201**；分类 **A 117 / B 81 / C 3** 与审计一致。A 类 117 条版本跨度**全部** = 2.3∪2.4 且 chunk 引用**全部**落在 {character__23501, character__24501} 两 doc 内。
- **根因实证**：23501 与 24501 各 19 块，**19/19 互为逐字镜像**（difflib 全等/包含判定）——"整章互拷"成立，A 类是重复章节的镜像效应，删边错误。
- **0 删边裁决复现**：三判据逐一复核——零同块共现 18 条（与审计的 18 一致；含 利伯蒂×笃笃骨 等），但其证据在引用块逐字命中（判据2不满足）；端点缺席者 2 条；**三判据同时满足 = 0 条 → 0 delete_edge 成立**。未发现任何"应删未删"的边；最接近的 18 条候选全部有逐字证据在场。
- 20/20 抽检边（A/B/C 混合）的版本跨度、同块共现数（如 十四行诗-示警-维尔汀 311、哑谜-质问-乌尔里希 61、X-转述-乌尔里希 22）与附录表逐一吻合；5 条 evidence 漂移行中 4 条确非逐字、1 条（寻访 兀尔德）在"／分段"宽松口径下逐字——口径差异方向保守，不改分类与裁决。
- **199→201 对账精确**：对 `backups/graph.json.prev.r3` 重算 = 199；消失 1 条（X-转述-暴雨小组组长乌尔里希）、新增 3 条（R3-E09 合并改写端点后经 Applier 去重并集 chunk_ids），与审计 §1 逐条一致；C 类 3 条两端同块共现 22–61 块，keep 判定成立。

## 6. 自验证复现 + 落盘投影 — reproduced

| 项 | 复现结果 |
|---|---|
| link() 种子 diff（真 GraphStore.from_dict + GraphRetriever.link + _name_matches，420 查询） | **0/420**（K01 保留口径）✓ |
| Applier 干跑（`--proposal repairs_v4/proposal.json --version-tag r4`，无 --apply） | 78 条 / 预检 0 错 / 警告 0 / 后检 0 错；7033→7033 / 29957→29957；exit 0 ✓ |
| 变更面 | 仅 `aliases` 字段逐实体变动，边数组不变 ✓；graph.json md5 干跑前后一致（全程只读）✓ |
| 失去全部别名的属主 | 46（与 _selfval 一致）✓ |
| alias_index | 8021 → **7946**：77 次摘除涉 76 个键串（特里格拉夫战列舰 双属主同摘计 1 键），75 键消失 + `高地据点` 重路由 299高地→地下堡垒 ✓ |
| 规范名碰撞 | 0 ✓ |

## 7. 遗留小疵（均非阻塞，不构成 must-fix）

1. `chunk_version_map.json` 实际无 `meta.version_distribution` 键（proposal §3 表述与工件不符；分布可由 map 推出：3539 块 / 28 个版本值）。
2. `entity_annotations.json` 探险家别斯米尔 note 称语料作"别斯米尔（女士）"——逐字实为 `别斯米尔女士`（19 块）；不影响 none 判定。
3. 审计"判据2失败 188 条"为严格口径；宽松口径（／分段+标记剥离）下非逐字为 10 条——口径差异只会更少删边候选，方向保守。

## 8. 结论

R4 四项交付**全部通过独立复核**：78 条目 agree、死别名清单精确、sidecar 与审计数字可完整重放、自验证 0/420 与 Applier 干跑全绿复现。**可按预案进入 Applier 落盘**（建议落盘后复验含 gen_r1r2 检索指标，尤其若采纳 K01=remove 的仲裁）。
