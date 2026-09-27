# R4 修复提案（死别名清理 + 标注 sidecar + 版本映射 + 时间一致性审计）— 2026-09-26

- 作者：R4-repairer-offline（作战书 §2.1；修复者不复核自己，待独立 Verifier）
- 图状态：post-R1/R2/R3，7033 实体 / 29957 边，fingerprint `7dc29bf90681a3f7`（别名/实体/边层修复不改指纹，作战书 §0.4）
- 网络：零（huiji WAF 403 已知；本版无身份裁决需求，未用灰机缓存）
- 本版**不直接写 graph.json**；提案仅含 Applier 支持的 `remove_alias`（×77）与 no-op `keep_with_note`（×1）。实体标注走 sidecar（Applier 无 desc 编辑能力）。

## 0. 交付物清单（全部在本目录）

| 文件 | 内容 |
|---|---|
| `proposal.json` | meta + 78 条（remove_alias ×77 + keep_with_note ×1 豁免） |
| `entity_annotations.json` | 实体标注 sidecar：grounding:none ×965 + claimed_mismatch ×121 + per_story_generic ×9 + 玩具盒 metaphor_note + 警卫/水手 跨篇审计判定 ×2 |
| `chunk_version_map.json` | 3695 chunk→version 全量映射（3539 有版本 / 156 null；151 doc 规则表） |
| `time_consistency_audit.md` | 201 条跨版本边分类审计：A 117 / B 81 / C 3 / 删边 0 |
| `_compute.py` / `_compute_results.json` / `_d4_classes.json` / `_build_entries.py` / `_selfval.py` / `_selfval.json` | 可复现脚本与中间产物（审计可重放） |

## 1. 交付一：死别名清理（remove_alias ×77 + 豁免 ×1）

**口径（QC 检3 同款）**：dead = alias 不逐字出现在属主任一声称 chunk 文本；DF = 3695 块原文子串计数。

**基线对账**（对 `backups/graph.json.prev.r1r2` 用同口径重算，验证脚本可信）：

| 指标 | QC（pre-R1） | pre-R1 复算 | post-R3 复算 | 差因 |
|---|---|---|---|---|
| 死 alias | 79/1023 | **79**（一致） | **78**/994 | +(兀尔德,原初的兀尔德)（R1 合并 传记作家兀尔德 时继承，仍死）；−(逃兵,两人)（R2 泛称摘除连带） |
| grounding-none 名 | 967 | **967**（一致） | **965** | −旅行队的别斯米尔、−暴雨小组组长乌尔里希（R3 合并入落地节点）；R3 新增 店主米拉/玩具盒 均落地 |
| claimed-mismatch 名 | 122 | **122**（一致） | **121** | −传记作家兀尔德（R1 合并） |

**例外扫描**：

- 查询路由豁免：420 条测试集查询（300_cn 300 + gen_r1r2 120）逐一与 78 条死别名做包含检查 → **仅 1 条命中**：`诊疗@诊所`（gen_r1r2 GA-25『在诊疗室门前等待时…』含『诊疗』）→ 按作战书规则 flag **keep-with-waiver**（R4-K01，keep_with_note），摘除与否留 Verifier+重校准裁决。
- alias==他实体规范名：现图 **0 例**（QC 检3 已清零，本版复算确认）——无 cosmetic-only 条目。
- 多主死别名 3 条：`特里格拉夫战列舰`（两名属主均死，摘除后 alias 消失）、`高地据点`（299高地 死/地下堡垒 活——摘除后 setdefault 语义自动重路由到活的属主，属改善）。

**条目构成**：77 条 remove_alias = nowhere 类 58（全语料 0 命中，含继承的 `原初的兀尔德`@兀尔德、跨语名 CactusCat/ParadiseRegained/TierradelFuego/déjàvu/Launuacirklo/TheCongress）+ elsewhere 类 19（他块出现、属主块 0 命中，如 `外国`@爱琴海 DF=21/10docs、`至高的秩序`@真理）。每条 evidence 含 df_in_owner=0 / df_corpus / elsewhere 例块与摘录（≤3）。

**检索影响预判**：死别名是反向伤害——查询命中后 mention 通道锚到不含该词的块。摘除不影响任何测试集查询的种子集（§4 自验证 0/420 diff）。

## 2. 交付二：实体标注 sidecar（entity_annotations.json）

作战书 §1-R4 原文：『967 虚构接地规范名标注（grounding:none 元数据，不改名不删节点——删除影响面不可控）』。

| 标注 | 数量 | 说明 |
|---|---|---|
| grounding:none | 965 | 规范名全语料逐字 0 命中（QC 967 → post-R3 965，差因见上）；note 统一含 QC 修复建议10 的检索侧处置（跳过 name-key 提及匹配） |
| grounding:claimed_mismatch | 121 | 名在他块、不在声称块（QC elsewhere 122→121）；附 df_corpus + elsewhere_docs 供后续归属复核 |
| per_story_generic | 9 | R2 flag_grounding_r4 ×9 移交（伙计/猎人/小孩/教师/水手/警卫/店主/卫兵/信众），story_scope_docs 按 **post-R3** 篇目重算——`店主` 经 R3-E15/E16 拆出 店主米拉 后已收敛为单篇（第一千夜×3），标注如实更新 |
| cross_story_audit | 2 | 警卫（4 块 4 篇）、水手（3 块 2 篇）：R3-E17/E18 移交的跨篇焊复核，R4 裁决 **keep_no_split**（语料零具名、无 R1 式具名锚点、规模小），原句引文入档 |
| metaphor_note | 1 | 玩具盒：R3-E08 的比喻意象限定（≠拉普拉斯装置 toy box 的英文语料读法），转入 sidecar |

共标注 1096 个 eid。**不改 graph.json、不做 desc 编辑**。

## 3. 交付三：版本映射 sidecar（chunk_version_map.json）

- 规则 = meetability 报告 meta.time_mapping_rule 的逐 doc 展开（mainline 查表 / activity 5位 XY→X.Y / character XY→X.Y / anecdote 推定 1.9(low) / appendix 文件名内嵌 X_Y；7 个 doc 无本地版本证据 → null）。
- 覆盖：**3695/3695** chunk 全量入表；**3539 mapped / 156 null**（null=三联动文档 125 块 + 雷米特杯兑换/赛季·第十章·啁啾表 31 块）。
- meetability 口径复核：『全图无版本化 chunk 的边』= **1243**/29957（与其 1243/29959 一致，R3 合并不改此数）；另计触及 null 块的边 1245 条。
- 证据：compendium_clean_report × huiji_canon 版本弧 × plot_timeline 三源（全部本地）。版本分布 1.0×N…3.8 入 meta.version_distribution。

## 4. 交付四：时间一致性审计（time_consistency_audit.md）

- 重算跨版本边（chunk 覆盖 ≥2 版本）：**201** 条，对账 meetability 199（R3 乌尔里希合并去重 +3/−1，逐条列名）。
- 分类：**A 章节重复伪跨版本 117**（23501/24501 整章互拷的镜像，根因语料层）/ **B 长线关系 81**（含 5 条 evidence 漂移但共现扎实）/ **C R3 合并伴生 3**（逐条证据复核）。
- 删边裁决：预注册三判据（零共现 ∧ evidence 全部引用块不命中 ∧ 端点名全部引用块缺席）→ **0 条满足，0 delete_edge 提案**；201 条全部 documented keep。

## 5. 自验证（_selfval.json，verdict=PASS）

| 项 | 结果 |
|---|---|
| 逐条预检（Applier 同规则：属主存在、alias 在属主表） | 0 错误 / 0 警告 |
| 模拟应用后全图后检（悬空 eid/chunk、重名、eid!=name、mentions==chunk_ids） | 0 错误 |
| 变更面 | 仅 `aliases` 字段被改动（逐实体 diff 断言通过） |
| 测试集路由：420 查询 link() 种子前后 diff（GraphStore.from_dict 同序 alias_index + retriever._name_matches 忠实模拟） | **0 / 420** 变化 |
| 摘除串仍被查询命中 | 0（唯一命中的 诊疗 已豁免保留） |
| 失去全部别名的属主 | 46 个（canonical 名与边通道不变；与 QC 记录的 0-alias 实体常态一致，无新增结构风险） |

## 6. Verifier 交接要点

1. D1 独立重推：只需属主声称块逐字判定 + 420 查询包含检查（_compute.py 口径），重点复核 3 条多主摘除与 R4-K01 豁免。
2. D2 抽检建议：grounding:none 965 中抽 ≥30 个逐字复核；`探险家别斯米尔` 属 none（『探险家别斯米尔』非语料逐字串，语料作『别斯米尔（女士）』）——这是 R1 命名决策的已知形态，不是本版引入。
3. D3 复核：anecdote→1.9 置信 low、7 个 null doc 的理由是否接受。
4. D4 复核：三判据是否同意为『不可否认』标准；A 类 117 条是否同意根因归语料层。

## 7. Applier 调用（供执行者）

```bash
./.venv/Scripts/python.exe scripts/_graph_apply_repairs.py \
  --proposal data/compendium_rag/repairs_v4/proposal.json --version-tag r4   # 干跑
  # 确认全绿后加 --apply 落盘（将生成 backups/graph.json.prev.r4）
```