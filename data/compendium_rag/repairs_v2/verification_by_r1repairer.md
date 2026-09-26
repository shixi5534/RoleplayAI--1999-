# R2 提案复核报告 — Verifier: R1-repairer（作战书 §2 轮换）

- **under review**: `data/compendium_rag/repairs_v2/proposal.json`（71 entries）+ `proposal_v2.md`
- **独立性**：复核者（R1 修复者）未参与 R2 撰写；全部数字由 `graph.json` / `chunks.json` / `data/knowledge/_audit/rag_testset_300_cn.json` **独立重算**，未采信提案数值。
- **约束遵守**：全程零网络（wiki 复验只用离线资产：`huiji_lexicon.json` / `huiji_canon.json` / 474 页缓存 / 前代 43 页 revcontent）；graph/corpus 只读；本次输出仅本 JSON+MD 两件；未用 Ollama。
- **机读件**：`verification_by_r1repairer.json`（含 71 条逐项 verdict）。

## 0. 结论

| 项 | 数 |
|---|---|
| **agree** | **71 / 71**（36 remove_alias ＋ 25 keep_with_note ＋ 9 flag_grounding_r4 ＋ 1 keep_node） |
| **disagree** | 0 |
| **insufficient-evidence** | 0 |
| **must-fix-before-apply** | **0**（4 条 note 级元数据/表述勘误，见 §5，均不改任何条目处置） |

## 1. DF / owner 复算（61/61 全量，超出 ≥20 抽样要求）

- 58 清单确认：声明 alias 去重 **1016** 条中 DF≥50 恰 **58** 条 ✅；提案 61 目标 = 58 ∪ {老伙计, 老朋友, 卡森} ✅。
- alias_index 重建（GraphStore.from_dict 语义）：pre **8049** 键 ✅；移除 36 键后 **8013** ✅；36 键无 canonical 名碰撞、无悬空引用 ✅。
- **DF total / owner 归属：61/61 全部一致，0 偏差**。
- 唯一簿记分歧：`玛丽` 的 `in_owner_claims=1` 只计主 owner（圣路连士兵），extra owner 玛丽安娜 声称的 29 块被计入 unrelated（union 口径应为 29/57）。不影响裁决（两主均摘），记 note。

## 2. 300 题 link() 种子 diff —— 精确复现

模拟口径：`retriever._name_matches` 逐字拷贝、长名优先、exact 1.0 / alias 0.9、top_k=6。pre/post 全量 diff：

- **种子集变化的查询 = 11 题（复现 11/11，逐题 lost 实体与分数与提案一致）**，0 gained、0 rescored。
- 逐题 lost seed 分类（用 testset ref/evidence 人工裁决）：

| qid | lost seed | 分类 | ref 依据 |
|---|---|---|---|
| R018 | 邓肯先生 0.9 | **wrong** | ref=Shamane（鬃毛沙砾） |
| R062/R069/R076 | 奇美拉 0.9 ×3 | **wrong** | ref=巨怪（troll），奇美拉≠巨怪 |
| R087 | 泰内布朗热家 0.9 | **wrong** | ref=阿马尔菲塔诺 |
| R259 | 泰内布朗热家 0.9 | **wrong** | ref=阿黛尔·塔维尼耶（塔维尼耶家族≠泰内布朗热家） |
| R127/R170/R180/R240 | 环境监测装置 0.9 ×4 | **wrong** | ref=净化机 / 玩具盒 / 发条装置 / 阿尔卡纳 |
| R228 | 勿忘我 0.9 | **wrong** | ref=Melania；正确种子 拉米雷斯 1.0 保留（亲验） |

→ **lost-correct = 0**，与提案断言完全一致；对 answerable hit@6 无回归路径。
- **R018**：pre `[伙计 1.0, 猎人 1.0, 邓肯先生 0.9]` → post `[伙计 1.0, 猎人 1.0]` ✅（独立模拟逐字复现）。
- pool-out 交集 4 题（R018/R127/R170/R297）复现；R297 全称直配零变化确认（不在 11 题内）。

## 3. 36 条 remove_alias 的 wiki/语料复验

- **wiki 离线裁决：36/36 支持摘除**。关键亲验：
  - `门`：huiji_canon characters 有独立角色页 **{zh:门, en:Door}** → 挂 神殿之门 属跨实体冲突（提案 md 断言核实）。
  - `别斯米尔`：lexicon 别斯米尔→Bessmert（独立 NPC）；卡卡尼亚 owner 页 wikitext 不含该串；与 R1 拆焊方向一致。
  - `老爷`：维尔汀 owner 页全篇**仅 1 次**命中，且是 `<ref>` 引文「老爷……您也不是纯血吧」（斯奈德 2ND-7）——非注册 alias；DF=77 跨篇他指 → 摘除正确，提案注记如实。
  - 其余 33 条 owner 页基本不存在（故事级实体）→ 灰机无从背书这些泛称 alias。
- **证据块 72/72 全部复验通过**：chunk 存在、snip 经 ⏎→换行归一后逐字、alias 串在场、块非 owner 声称。复核者另抽 5 条独立 unrelated 样本（街道/怪物/家族/组长/装置）均成立。
- 保留的限定形 alias 全部在册亲验：乌斯怀亚·街道、基金会联合委员会/基金委、重塑信徒/黑袍信徒、南极神秘学地图/诺谛卡的地图、贵学派、乌尔里希组长/破译组长、小龙/幼龙、亲爱的妹妹、玄武岩迷宫、便携式平衡伞 ✅。

## 4. 25 条 keep_with_note —— 全量反事实模拟（超出 ≥10 抽样）

对每条 keep 做「单别名摘除」模拟（precomputed matched-keys 重放，含 top-k 截断）：

**载荷组（摘除断种，keep 必要）**：基金会 **7** 题（R054/R236/R242/R279/R283/R286/R290）、司辰 4、拉普拉斯 3、康复中心 3、助手 1（R236）、保罗 1（R265）、伊万 1（R148）、格蕾丝 2、阿德勒 1（R050）、卡森 1（R105）。
**冗余组（摘除零影响，keep 无害）**：重塑、军长、纸信圈儿、德洛丝、维尔汀小姐、Z女士、苏芙比小姐、APPLe先生、露西女士、莫莉、第一助手、十四行诗小姐、拉普拉斯科算中心、基金会总部、APPLe某 —— **全部 0 变化** ✅。

ref 语义抽查（复跑 6 组）：R236 助手→十四行诗（ref=十四行诗，**审计「摘除助手」建议据此推翻，成立**）；R105 卡森→邓肯先生（ref=Carson；灰机 NPC 卡森/Mr. Karson id=5013 亲验，按篇豁免成立）；R279 基金会→圣洛夫基金会（seed=答案）；R148 伊万→军长伊万（seed=答案）；R191/R211 拉普拉斯→科算中心（seed=答案）；R176/R281 司辰→维尔汀（seed=答案）。

计数勘误（不改裁决）：基金会 bare 依赖为 **7** 题，提案列 6（R181 实为全称直配非依赖；R279/R283 漏列）。

## 5. Owner after-state / 规范节点 / 杂项

- **owner_after_state（34 owner）**：canonical_grounded 字段与复算一致；**「16/18」断言精确复现**——18 个 owner 别名清空，其中 16 个 canonical 名逐字落地，恰 信仰/卡卡尼亚之兄 2 例外（先在 grounding 缺陷，R4 职权）✅。
- **note**：3 处 `verbatim_aliases_left` 列表截断至 6 条，与自身 `n_verbatim_aliases_left`（卡卡尼亚 14、维尔汀 7/7）不符（漏 越狱头子 等）。n 计数正确，Applier 以实表重建不受影响。
- **10 个规范节点：10/10 数字与提案表一致**（管理员 6/2/2 keep；其余 9 flag）。`name_contains` 复算确认 flag-merge=0（命中皆为描述命名独立 NPC，如 维也纳警卫/城镇警卫Ⅰ/糖果店店主）；警卫(4 篇)/店主(2 篇)/水手(2 篇) 跨篇焊合嫌疑上报 R3 合理。管理员 keep（df=6、图书馆场景、ts=0）合理。
- **死 alias「78→77」**：为 itemscope 口径（自验件字段名可证）；本复核全 index nowhere 口径为 1167→1166，同为 −1（仅 两人 被移除且本为死键、0 新增）——两种口径结论一致，建议提案注明口径。

## 6. 三个 open questions —— 本复核裁决

**(a) 保罗 → QUALIFY（摘除裸 保罗，保留既有 alias 保罗·霍伊默尔）**
- DF(保罗)=92 中 **66 块是 圣保罗（城市）子串碰撞**，真指人名仅 26 块（卡戎 67 声称块中 19 块）。
- testset R265「…**圣保罗**贫民窟…女军官是谁？」pre seeds 含 **卡戎 0.9 = 城名碰撞假种子**（ref=洛佩拉）——本复核模拟实测 qualify 后该假种子消失。
- 保罗·霍伊默尔 DF=1 且所在块 mainline__111:14.0.2 为卡戎声称块（红线3 ✅）；卡戎另有 亡者/士官/收尸人/邮递员 + canonical 可达，无可达性损失。
- 提案「两案对 testset 种子均零影响」**表述不精确**：qualify 使 R265 种子集变化——失去的恰是错误种子（改善非回归）。testset 无任何查询含 保罗·霍伊默尔。

**(b) 重塑 → KEEP（同意 repairer）**
- 摘除模拟：testset **零变化**（12 个 owner-seeded 查询全经 重塑之手 全称直配）。
- 裸 重塑 非子串伪影：standalone 用法（重塑 后不接 之手/·）**155 块**、其中 70 块在 重塑之手 声称块外（如 mainline__101:2.0.0「重塑的势力正逐年剧增」）——语料真实短称。
- 提案的 327/506 in-claim 论证是循环的（重塑之手 ⊃ 重塑），结论恰被 standalone-155 独立支撑；建议提案补此论据。

**(c) 离线-only wiki 披露 → ACCEPT，协议合规**
- 本会话 2 次 api.php 直连均 Cloudflare 403，与 R1 期 `_prefetch_log.json` 38×403 WAF 阻断一致；禁用浏览器 bootstrap 正确（= 前代死因，作战书 §0 明令禁浏览器页）。
- 关键 wiki 事实全部离线可决且经本复核亲验（lexicon/canon/474 缓存/43 页 revcontent）；「无未决网关」断言与抽查一致；披露清单满足 §4。

## 7. Must-fix before apply

**无阻断项。** 4 条 note 级建议（不改变任何条目处置，Applier 以实表重建可自动绕开 2 条）：
1. `玛丽` df.in_owner_claims 口径注明 primary-only（或改并集 29）。
2. 卡卡尼亚/维尔汀 3 处 `verbatim_aliases_left` 列表与自身 n 计数不符（截断至 6）——重生成或删列表留计数。
3. 基金会 bare 依赖题号列表更正为 7 题（R181 非依赖；R279/R283 补入）。
4. 保罗 open-question 表述改为「对 hit@6 无回归；qualify 兼除 R265 假种子」。

复现口径：alias_index 按 GraphStore.from_dict（canonical 直配 + alias setdefault 首主抢注）；`_name_matches` 逐字拷贝；DF=3695 块 text 子串。
