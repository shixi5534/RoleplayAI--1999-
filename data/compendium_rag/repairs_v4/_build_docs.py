# -*- coding: utf-8 -*-
"""R4 修复者：生成 3 个 sidecar（entity_annotations / chunk_version_map）+ 审计报告 + proposal_v4.md。
只读既有文件；只写本目录产物。
"""
import json, sys, io
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[3]
R4 = Path(__file__).resolve().parent
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)

res = json.loads((R4 / "_compute_results.json").read_text(encoding="utf-8"))
d4 = json.loads((R4 / "_d4_classes.json").read_text(encoding="utf-8"))
selfval = json.loads((R4 / "_selfval.json").read_text(encoding="utf-8"))
proposal = json.loads((R4 / "proposal.json").read_text(encoding="utf-8"))
g = json.loads((ROOT / "data/compendium_rag/graph.json").read_text(encoding="utf-8"))
ents = {e["eid"]: e for e in g["entities"]}
ch = json.loads((ROOT / "data/compendium_rag/chunks.json").read_text(encoding="utf-8"))
n_chunks = len(ch["chunks"])
p2 = json.loads((ROOT / "data/compendium_rag/repairs_v2/proposal.json").read_text(encoding="utf-8"))
r2flags = {e["target"]["eid"]: e for e in p2["entries"] if e.get("type") == "flag_grounding_r4"}

# ============ 1) entity_annotations.json ============
NOTE_NONE = ("规范名在全语料 3695 块中逐字 0 命中（QC 检2『nowhere』类，post-R3 重算）——"
             "模型的改写/描述性归一名；name-key/提及通道天然不命中，节点仅经边通道可达。"
             "处置=标注不改名不删节点（作战书 §1-R4；QC 修复建议10：检索侧可对本 eid 跳过 name-key 提及匹配以省时）。")
NOTE_MISMATCH = ("规范名在此节点任何声称块中逐字 0 命中，但在语料其他块出现（QC 检2『elsewhere』类）——"
                 "疑似跨块归属错位。处置=标注不改名不删节点；后续复核可按 df_corpus/elsewhere_docs 定位真正声称块。")

annotations = {}
for r in res["grounding_none"]:
    annotations[r["eid"]] = {
        "grounding": "none",
        "type": r["type"], "nchunks": r["nchunks"], "df_corpus": 0,
        "note": NOTE_NONE, "qc_ref": "图谱与原文质检报告_20260926.md 检2 nowhere（967→post-R3 965）",
        "retrieval_hint": "skip_name_key_mention_match",
    }
for r in res["grounding_mismatch"]:
    annotations[r["eid"]] = {
        "grounding": "claimed_mismatch",
        "type": r["type"], "nchunks": r["nchunks"], "df_corpus": r["df_total"],
        "elsewhere_docs": r["elsewhere_docs"],
        "note": NOTE_MISMATCH, "qc_ref": "图谱与原文质检报告_20260926.md 检2 elsewhere（122→post-R3 121）",
        "retrieval_hint": "skip_name_key_mention_match; review_chunk_attribution",
    }

GEN_NOTE = {
    "伙计": "R2 flag_grounding_r4 继承：df=161 vs 5 块（打虎记 1 篇）；R018 以 1.0 分抢种子案例节点之一。",
    "猎人": "R2 flag_grounding_r4 继承：概念节点（anecdote__1906 诗中贪婪者，1 块）；灰机 zh2en『猎人』↔UFO 疑另一所指；R018 抢种子案例节点之一。",
    "小孩": "R2 flag_grounding_r4 继承：df=104 vs 6 块（塞梅尔维斯 1 篇）。",
    "教师": "R2 flag_grounding_r4 继承：df=21 vs 2 块（在路上 1 篇）；R273『少女教师』被其抢种子（QC 检6）。",
    "卫兵": "R2 flag_grounding_r4 继承：df=43 vs 6 块（飞渡往日 1 篇）；篇内身份一致但词面泛称。",
    "信众": "R2 flag_grounding_r4 继承：df=24 vs 1 块（帕米埃 1 篇）；宗教泛称。",
    "店主": "R2 flag_grounding_r4 继承 + post-R3 更新：R3-E15/E16 拆出 店主米拉（乘法轴上的一天，10 块）后，本节点仅剩 第一千夜 3 块——跨篇焊合已被 R3 消解，现按单篇泛称标注。",
    "警卫": "R2 flag_grounding_r4 继承 + R4 跨篇审计判定（见 cross_story_audit）：df=40 vs 4 块 4 篇。",
    "水手": "R2 flag_grounding_r4 继承 + R4 跨篇审计判定（见 cross_story_audit）：df=26 vs 3 块 2 篇。",
}
GUARD_AUDIT = {
    "verdict": "keep_no_split",
    "scope": "跨篇同泛称焊合复核（R3-E17 记录在案、R4 本条裁决）",
    "instances": [
        {"doc": "mainline__103_故事一无所有", "nchunks": 1, "who": "按倒伊莎贝拉的警卫（校长出场段）", "named_anchor": False},
        {"doc": "character__20601_旧金山小子", "nchunks": 1, "who": "旧金山场景警卫", "named_anchor": False},
        {"doc": "anecdote__1908_齿轮的意志", "nchunks": 1, "who": "齿轮的意志场景警卫", "named_anchor": False},
        {"doc": "anecdote__1910_风吹乌哈拉", "nchunks": 1, "who": "押人受审的警卫", "named_anchor": False},
    ],
    "reasoning": "4 块横跨 4 篇、4 个不同故事的匿名个体；语料零具名（R3-E17 引 mainline__103:10.1.1、anecdote__1910:0.0.2 原文），"
                 "拆分缺乏 R1 卡卡尼亚式具名锚点，且泛称别名『警卫』只能经 setdefault 落到其中之一反而制造错配；"
                 "4 块规模 PPR 污染半径有限。R4 裁定：不拆分、不删节点，按 per_story_generic 标注（与 R3-E17 保守保留一致）。",
    "evidence": [
        {"src": "corpus mainline__103_故事一无所有:10.1.1", "quote": "白。他转向旁边站着的警卫。/**校长**：去把第一排最右边的那个女孩给我拉下去！！"},
        {"src": "corpus anecdote__1910_风吹乌哈拉:0.0.2", "quote": "脚戴镣铐的先生被警卫押入房间，迟疑地坐上身后的木凳。/审讯官抬手示意，警卫随即解下他的眼罩"},
    ],
    "r3_ref": "repairs_v3/proposal.json R3-E17 (keep_with_note)",
}
SAILOR_AUDIT = {
    "verdict": "keep_no_split",
    "scope": "跨篇同泛称焊合复核（R3-E18 记录在案、R4 本条裁决）",
    "instances": [
        {"doc": "mainline__110_复乐园", "nchunks": 2, "who": "乌尔里希纵帆船上的水手（含 alias 无武装水手，逐字于 110:7.0.2）", "named_anchor": False},
        {"doc": "activity__23101_圣火纪行_东区黎明", "nchunks": 1, "who": "『刚从蒂尔伯里码头回来的水手』（福葛先生转述）", "named_anchor": False},
    ],
    "reasoning": "第二实例语料无名且仅 1 块，拆分收益不足（R3-E18 同判）；mainline__110 实例已持有逐字 alias 无武装水手。"
                 "R4 裁定：不拆分、不删节点，按 per_story_generic 标注；圣火纪行实例记录为潜在 1 块分裂候选（无锚点，不动）。",
    "evidence": [
        {"src": "corpus mainline__110_复乐园:7.0.2", "quote": "**对讲机**：报告中尉，除一名无武装水手外，纵帆船已确认清空。经前哨确认，暂无任何其余船只侵入近海。"},
        {"src": "corpus activity__23101_圣火纪行_东区黎明:7.1.0", "quote": "**福葛先生**：看看他，本家的大儿子，刚从蒂尔伯里码头回来的水手，看到他手上的麻绳了吗，那可是世界上最稳固的一种。"},
    ],
    "r3_ref": "repairs_v3/proposal.json R3-E18 (keep_with_note)",
}
for eid, info in GEN_NOTE.items():
    e = ents[eid]
    docs = sorted({c.split(":")[0] for c in e["chunk_ids"]})
    a = {
        "grounding_scope": "per_story_generic",
        "per_story_generic": docs,
        "story_scope_docs": docs,
        "type": e["type"], "nchunks": len(e["chunk_ids"]),
        "note": info,
        "source": "repairs_v2/proposal.json flag_grounding_r4（R2 移交）+ post-R3 篇目重算",
        "wiki_verdict": r2flags.get(eid, {}).get("wiki_verdict", ""),
    }
    if eid == "警卫":
        a["cross_story_audit"] = GUARD_AUDIT
    if eid == "水手":
        a["cross_story_audit"] = SAILOR_AUDIT
    annotations[eid] = a

annotations["玩具盒"] = {
    "metaphor_note": "1987宇宙组曲中宇航员库珀花环出舱观测「暴雨」影响时的比喻意象：「宇宙在她眼前展开，如同……玩具盒子」。"
                     "本中文语料唯一提及（DF=1，activity__27101_1987宇宙组曲:17.1.0）。评测集 R170 将『玩具盒（toy box）』列为"
                     "「人们向何处去篇拉普拉斯的重要装置」——该装置读法来自官方英文配音语料（plot_glossary: toy box 39 次），"
                     "本中文语料无该装置明文；本节点按语料实际语义落档（R3-E08 零网关抽取）。R170 的机械改善取决于重排窗口，"
                     "非本节点单独可保证。语义上本节点≠拉普拉斯装置，检索侧不得将两者混同。",
    "source": "repairs_v3/proposal.json R3-E08 (add_entity) 的 metaphor 限定说明，R4 转入标注 sidecar",
    "type": ents["玩具盒"]["type"], "nchunks": 1, "grounding": "ok",
}

entity_annotations = {
    "_meta": {
        "author": "R4-repairer-offline", "timestamp": "2026-09-26",
        "purpose": "R4 实体标注 sidecar（作战书 §1-R4『967 虚构接地规范名标注（grounding:none 元数据，不改名不删节点）』+ R2 flag_grounding_r4 移交 + R3 转入说明）——不改 graph.json，不做 desc 编辑（Applier 不支持，规范名/别名层修复全走 R1-R3 既有机制）",
        "graph_state": "post-R1/R2/R3，7033 实体，fingerprint 7dc29bf90681a3f7",
        "rules": {
            "grounding:none": "canonical name 对 3695 块原文逐字 0 命中（QC 检2 nowhere 类）",
            "grounding:claimed_mismatch": "canonical name 不在自身任何声称块、但语料他块出现（QC 检2 elsewhere 类）",
            "per_story_generic": "R2 移交的裸泛称规范节点；story_scope_docs=post-R3 实际篇目重算",
            "cross_story_audit": "警卫/水手 跨篇焊合复核判定（R3-E17/E18 移交，R4 裁决）",
            "metaphor_note": "R3-E08 玩具盒 比喻意象限定",
        },
        "coverage": {
            "grounding_none": len(res["grounding_none"]),
            "claimed_mismatch": len(res["grounding_mismatch"]),
            "per_story_generic": 9,
            "metaphor_note": 1,
            "cross_story_audit": 2,
            "baseline_reconcile": "QC: none 967 + mismatch 122；pre-R1 复算一致；R3 合并消化 none×2（旅行队的别斯米尔/暴雨小组组长乌尔里希）+ mismatch×1（传记作家兀尔德）；R3 新增 店主米拉/玩具盒 均落地无新增",
        },
        "usage": "检索侧按 retrieval_hint 对 grounding!=ok 的 eid 跳过 name-key 提及匹配（省时且无精度损失）；重排/PPR 无需改动。",
    },
    "annotations": annotations,
}
(R4 / "entity_annotations.json").write_text(json.dumps(entity_annotations, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"entity_annotations.json: {len(annotations)} eids")

# ============ 2) chunk_version_map.json ============
cmap = res["version_map"]
doc_rules = res["doc_version_rules"]
null_docs = sorted({cid.split(":")[0] for cid in res["version_null_chunks"]})
n_mapped = sum(1 for v in cmap.values() if v)
conf_cnt = Counter(v[2] for d, v in doc_rules.items())
chunk_conf = Counter(doc_rules[c["doc_id"]][2] for c in ch["chunks"])
gj = g
n_edges = len(gj["edges"])
no_ver_edges = sum(1 for e in gj["edges"] if not any(cmap.get(c) for c in e.get("chunk_ids", [])))
touch_null_edges = sum(1 for e in gj["edges"] if any(cmap.get(c) is None for c in e.get("chunk_ids", [])))
ver_dist = Counter(v for v in cmap.values() if v)
vm = {
    "_meta": {
        "author": "R4-repairer-offline", "timestamp": "2026-09-26",
        "purpose": "R4 版本映射 sidecar：全部 3695 chunk → 游戏版本（null=本地无版本证据）。供时间一致性审计（time_consistency_audit.md）与后续带时间约束的检索/评测使用；不改 graph.json。",
        "mapping_rule": {
            "mainline__NNN_标题": "章节标题查表：000/101-104→1.0，105→1.4，106→1.7，107→1.9，108→2.2，109→2.6，110→2.8，111→3.0，112→3.3，113→3.7（meetability 三源核证：compendium_clean_report rows × huiji_canon 版本弧 × plot_timeline version↔name）",
            "activity__XY101(5位)": "XY→X.Y（18/18 与 huiji 版本弧相符，plot_timeline 逐条印证：朔日手记 1.6 … 世纪末尺度 3.8）",
            "activity__305101/305201/385101(6位)": "null——联动/特殊活动（翡冷翠之春/入雅典记=刺客信条联动；聚合浪潮=Polymerized Dreams），clean_report missing_version 同样未解析",
            "character__XYz01": "XY→X.Y（clean_report chapter_id_rule 全部一致）",
            "anecdote__19XX": "推定 1.9（clean_report 留空；低置信）",
            "appendix_unbound__NNN_X_Y_标题": "文件名内嵌 X_Y→X.Y；071(S02)/072/073/074 无内嵌版本→null",
        },
        "sources": [
            "data/lore/wu_ming_zhe/compendium_clean_report.json（version_by_source/missing_version）",
            "data/lore/wu_ming_zhe/huiji_canon.json（版本弧，离线缓存）",
            "data/lore/wu_ming_zhe/plot_timeline.json（version↔name↔故事年份）",
            "data/compendium_rag/reports/meetability_test_20260927.json meta.time_mapping_rule（相同规则，本文件按其逐 doc 展开）",
        ],
        "coverage": {
            "chunks_total": len(cmap),
            "chunks_mapped": n_mapped,
            "chunks_null": len(cmap) - n_mapped,
            "null_ratio": round((len(cmap) - n_mapped) / len(cmap), 4),
            "docs_total": len(doc_rules),
            "docs_null": len(null_docs),
            "null_docs": {d: doc_rules[d][0] for d in null_docs},
            "null_doc_reasons": {d: doc_rules[d][1] for d in null_docs},
            "edges_total": n_edges,
            "edges_without_any_versioned_chunk": no_ver_edges,
            "edges_touching_null_chunk": touch_null_edges,
            "note": "meetability 报告口径『全图无版本化 chunk 的边 1243/29959』在本图复核为 "
                    f"{no_ver_edges}/{n_edges}（R3 合并去重不改变该计数）；其 chunk 引用分布：聚合浪潮/翡冷翠之春/入雅典记 三联动文档 + 雷米特杯兑换/赛季·第十章·啁啾表 4 个无内嵌版本附录",
            "doc_confidence": dict(conf_cnt),
            "chunk_confidence": dict(chunk_conf),
            "version_distribution": dict(sorted(ver_dist.items(), key=lambda kv: [int(x) for x in kv[0].split(".")])),
        },
    },
    "doc_rules": {d: {"version": v[0], "rule": v[1], "confidence": v[2]} for d, v in sorted(doc_rules.items())},
    "map": cmap,
}
(R4 / "chunk_version_map.json").write_text(json.dumps(vm, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"chunk_version_map.json: {len(cmap)} chunks ({n_mapped} mapped / {len(cmap)-n_mapped} null)")

# ============ 3) time_consistency_audit.md ============
L = []
A = L.append
A("# 时间一致性审计（跨版本边 · 删边裁决）— R4 · 2026-09-26")
A("")
A("- 审计对象：`data/compendium_rag/graph.json` 全部边中 **chunk_ids 覆盖 ≥2 个游戏版本** 者（post-R1/R2/R3 图：7033 实体 / 29957 边，fingerprint `7dc29bf90681a3f7`）。")
A("- 版本口径：`chunk_version_map.json`（本目录 sidecar；规则 = `reports/meetability_test_20260927.json` meta.time_mapping_rule 的逐 doc 展开；null 版本块不参与版本集合）。")
A("- 只读审计 + 删边仅限『不可否认焊残留』（任务口径）；证据全部来自本地语料，零网络。")
A("")
A("## 1. 对账：199 → 201")
A("")
A("`reports/meetability_test_20260927.json` 报 `cross_version_edges.count_graphwide = 199`（post-R1/R2 图，7034 实体 / 29959 边）。")
A("本审计在 post-R3 图上重算得 **201**，差异逐条对账（对 `backups/graph.json.prev.r3` 用同一版本映射重算 = 恰好 199）：")
A("")
A("| 变化 | 边 | 原因 |")
A("|---|---|---|")
A("| R3 后消失 | (X, 转述, 暴雨小组组长乌尔里希) | R3-E09 合并 暴雨小组组长乌尔里希→乌尔里希 |")
A("| R3 后新增 | (X, 转述, 乌尔里希)；(哑谜, 质问, 乌尔里希)；(乌尔里希, 反驳, 哑谜) | 合并改写端点后，同名三元组边经 Applier 去重**合并双方 chunk_ids**，版本跨度并集成 1.9∪3.6 |")
A("")
A("净 +2。三条新增边单独复核见 §4.3（裁定 keep）。")
A("")
A("## 2. 分类总表（201 条，0 删边）")
A("")
A("| 类 | 计数 | 判定 |")
A("|---|---|---|")
A(f"| A. 章节重复伪跨版本 | {len(d4['dup23_24'])} | keep——版本跨度 {{2.3,2.4}} 全部源于 character__23501_太阳的背面 与 character__24501_河港与海之间 **整章逐字互拷**（QC 检5 P1：19 组/38 块，vendor 同一故事两个 doc_id）。关系本体真实（其中 111 条证据逐字命中），跨版本是重复章节的镜像效应。根因在语料层，按 QC 修复建议5 留给下次 rebuild 去重，**不是边的问题，删边错误**。 |")
A(f"| B. 长线关系时间聚合 | {len(d4['long_arc'])} | keep——合法跨版本关系（如 维尔汀—圣洛夫基金会『隶属于』1.0∪2.6、星锑—圣洛夫基金会『加入』1.0∪1.9）：关系在多个版本分别被语料陈述，边聚合各次观察。其中 76 条证据逐字命中；另 5 条属 QC 检5 P2『evidence 引文漂移』（4.2% 边的已知形态），但其 src/dst 名均逐字见引用块且 pair 全语料同块共现 ≥24 块，关系扎实，keep。 |")
A(f"| C. R3 合并伴生 | 3 | keep——R3-E09 合并（已由 R3 以语料+灰机双证裁定同一人）后，同一人在 1.9（孤独之歌）与 3.6（人们向何处去）的真实关系被合并去重拼出跨版本跨度。逐条证据复核见 §4.3。 |")
A("| D. 不可否认焊残留（删边） | **0** | 无一条满足删边判据（见 §3）。 |")
A("")
A("## 3. 删边判据与裁定")
A("")
A("预注册判据（全部满足才提 delete_edge）：")
A("")
A("1. pair（src,dst）在**全语料 3695 块中零同块共现**（无任何在场相遇）；且")
A("2. 边 evidence 在**全部**引用块中逐字（含标点/空白不敏感归一）不命中；且")
A("3. 至少一端实体名在**全部**引用块中逐字不出现（该边的全部 chunk 引用都对不上两端点）。")
A("")
A("201 条逐一过筛：同时满足三条者为 **0**。")
A("- 判据 1 的 18 条失败者（笃笃骨×利伯蒂 等，见 §4.1 深查）全部属 A 类章节重复，且证据逐字命中（判据 2 不满足）；")
A("- 判据 2 失败 188 条（evidence 或其『／』分段逐字命中引用块）；")
A("- 判据 3 失败 199 条（142 条两端名都在引用块，57 条至少一端在）。")
A("")
A("**结论：0 条 delete_edge 提案。** 201 条全部 documented keep（A 117 / B 81 / C 3）。")
A("")
A("## 4. 分类细节")
A("")
A("### 4.1 A 类：章节重复伪跨版本（117 条，版本跨度全部 = 2.3∪2.4）")
A("")
A("character__23501_太阳的背面（2.3）与 character__24501_河港与海之间（2.4）整章互拷（QC 检5 P1），")
A("凡声称块落在这两章的实体，其边同时引用两文档的同文块 → 版本跨度 2.3∪2.4。117 条的 chunk 引用**全部**落在 {23501,24501} 两文档内。")
A("")
A("深查其中 18 条零同块共现边（删边判据最接近者）：笃笃骨×利伯蒂×4、祖母/记者/小孩Ⅲ/小孩Ⅳ/土豆泥/小匣子/金牌/战争/炮弹 等与笃笃骨/魔精——")
A("证据均逐字命中引用块（如『这是这周的蜗牛』『奖牌安静地躺在绒布上』），但一端节点名是**跨章归一名**（利伯蒂 的逐字出现块在 圣火纪行/夜游十字街，"
  "不在 太阳的背面/河港与海之间 的信件章节；其余同属泛称/描述性归一名），属于 QC 检2『名不落地/跨块归属』家族的**节点层**现象，")
A("已在 `entity_annotations.json` 相应 eid 下标注；与边真伪无关，**不构成删边理由**。")
A("")
A("样例（前 12 条，完整 201 条清单见 §5 附录）：")
A("")
A("| src | 关系 | dst | 版本 | 证据（截断） |")
A("|---|---|---|---|---|")
for e in d4["dup23_24"][:12]:
    A(f"| {e['src']} | {e['rel']} | {e['dst']} | {'∪'.join(e['versions'])} | {e['ev'][:30]} |")
A("")
A("### 4.2 B 类：长线关系时间聚合（81 条）")
A("")
A("形态：同一关系在多个版本被分别陈述（对话/行为反复发生）。典型：")
A("")
A("| src | 关系 | dst | 版本 | 证据 |")
A("|---|---|---|---|---|")
A("| 维尔汀 | 隶属于 | 圣洛夫基金会 | 1.0∪2.6 | 我与你遇到的那群调查员来自同一个机构——圣洛夫基金会 |")
A("| 星锑 | 加入 | 圣洛夫基金会 | 1.0∪1.9 | 星锑将加入基金会成为我们的同僚 |")
A("| 维尔汀 | 宣告 | 暴雨 | 1.0∪1.9∪2.4 | “暴雨”来了…… |")
A("| APPLe | 提醒 | 星锑 | 1.0∪1.1∪1.9∪2.4 | 请小口小口喝，不要对食道造成太大的压力 |")
A("")
A("5 条 evidence 漂移仍 keep 者：")
A("")
A("| src | 关系 | dst | 版本 | 漂移证据 | 同块共现 |")
A("|---|---|---|---|---|---|")
for e in d4["long_arc"]:
    if not e["evv"]:
        A(f"| {e['src']} | {e['rel']} | {e['dst']} | {'∪'.join(e['versions'])} | {e['ev'][:30]} | {e['cooc']} 块 |")
A("")
A("（漂移形态与 QC 检5 P2 一致：模型引文近似而非逐字；两端名逐字在引用块、pair 高共现，关系扎实。）")
A("")
A("### 4.3 C 类：R3 合并伴生（3 条，逐条复核）")
A("")
A("| 边 | 版本 | 证据分段命中 | 裁定 |")
A("|---|---|---|---|")
A("| 哑谜 —质问→ 乌尔里希 | 1.9∪3.6 | 『你“忘掉”的这份报告，我帮你拿来了』→activity__36101:2.0.2（3.6）；『为什么——你们到底为什么还不停止实验？』→（1.9 段未见逐字，见下） | keep |")
A("| 乌尔里希 —反驳→ 哑谜 | 1.9∪3.6 | 『神秘学不是电学，你对它的原理一无所知』→mainline__107:16.0.1（1.9）；『他们和我们所熟悉的人，并没有什么客观意义上的区别』→activity__36101:3.2.0（3.6） | keep |")
A("| X —转述→ 乌尔里希 | 1.9∪3.6 | 『这是乌尔里希先生的描述，并非我亲眼所见』→activity__36101:2.0.2（3.6）；1.9 段引用 append__010（X 角色故事）块含『乌尔里希』 | keep |")
A("")
A("三条边的两端在语料同块共现 22–61 块；1.9 段引用块（mainline__107 孤独之歌）中 乌尔里希/哑谜 逐字在场。")
A("跨度是 R3-E09 正确合并（暴雨小组组长乌尔里希=乌尔里希，R3 已双证）后同一人跨版本关系的自然并集，属 B 类同型，非焊残留。")
A("")
A("## 5. 附录：201 条完整清单")
A("")
A("| # | 类 | src | 关系 | dst | 版本 | 证据逐字 | 同块共现 |")
A("|---|---|---|---|---|---|---|---|")
i = 0
for cls, label in [("dup23_24", "A"), ("long_arc", "B"), ("r3_sideeffect", "C")]:
    for e in d4[cls]:
        i += 1
        A(f"| {i} | {label} | {e['src']} | {e['rel']} | {e['dst']} | {'∪'.join(e['versions'])} | {'是' if e['evv'] else '否'} | {e['cooc']} |")
A("")
A("## 6. 遗留建议（非本版动作）")
A("")
A("1. 语料层：23501/24501 整章去重（QC 修复建议5）应在下次 rebuild 一并做——它一次性消解本审计 117 条伪跨版本与向量通道双份。")
A("2. 版本标注缺口：305101/305201/385101 三联动文档与 4 个无内嵌版本附录文档（156 块，1243 条边无任何版本化 chunk）建议向灰机 api.php 拉取版本证据后补映射（本版零网络不做）。")
A("3. anecdote 19XX 的 1.9 推定置信=low，如需硬锚点同样走灰机拉取。")
A("4. 相遇语义升级（meetability 建议2）：同 scene 共现补『同场』边并携带 chunk 版本，可把相遇点锚定到唯一叙事时间——属图谱增强，非修复。")
(R4 / "time_consistency_audit.md").write_text("\n".join(L), encoding="utf-8")
print(f"time_consistency_audit.md: {len(L)} lines")

# ============ 4) proposal_v4.md ============
n_remove = selfval["n_remove_alias"]
n_keep = selfval["n_keep_with_note"]
removed_dead = [e for e in proposal["entries"] if e["type"] == "remove_alias"]
n_nowhere = sum(1 for e in removed_dead if e["evidence"]["df_corpus"] == 0)
n_else = n_remove - n_nowhere
M = []
B = M.append
B("# R4 修复提案（死别名清理 + 标注 sidecar + 版本映射 + 时间一致性审计）— 2026-09-26")
B("")
B("- 作者：R4-repairer-offline（作战书 §2.1；修复者不复核自己，待独立 Verifier）")
B("- 图状态：post-R1/R2/R3，7033 实体 / 29957 边，fingerprint `7dc29bf90681a3f7`（别名/实体/边层修复不改指纹，作战书 §0.4）")
B("- 网络：零（huiji WAF 403 已知；本版无身份裁决需求，未用灰机缓存）")
B("- 本版**不直接写 graph.json**；提案仅含 Applier 支持的 `remove_alias`（×77）与 no-op `keep_with_note`（×1）。实体标注走 sidecar（Applier 无 desc 编辑能力）。")
B("")
B("## 0. 交付物清单（全部在本目录）")
B("")
B("| 文件 | 内容 |")
B("|---|---|")
B("| `proposal.json` | meta + 78 条（remove_alias ×77 + keep_with_note ×1 豁免） |")
B("| `entity_annotations.json` | 实体标注 sidecar：grounding:none ×965 + claimed_mismatch ×121 + per_story_generic ×9 + 玩具盒 metaphor_note + 警卫/水手 跨篇审计判定 ×2 |")
B("| `chunk_version_map.json` | 3695 chunk→version 全量映射（3539 有版本 / 156 null；151 doc 规则表） |")
B("| `time_consistency_audit.md` | 201 条跨版本边分类审计：A 117 / B 81 / C 3 / 删边 0 |")
B("| `_compute.py` / `_compute_results.json` / `_d4_classes.json` / `_build_entries.py` / `_selfval.py` / `_selfval.json` | 可复现脚本与中间产物（审计可重放） |")
B("")
B("## 1. 交付一：死别名清理（remove_alias ×77 + 豁免 ×1）")
B("")
B("**口径（QC 检3 同款）**：dead = alias 不逐字出现在属主任一声称 chunk 文本；DF = 3695 块原文子串计数。")
B("")
B("**基线对账**（对 `backups/graph.json.prev.r1r2` 用同口径重算，验证脚本可信）：")
B("")
B("| 指标 | QC（pre-R1） | pre-R1 复算 | post-R3 复算 | 差因 |")
B("|---|---|---|---|---|")
B("| 死 alias | 79/1023 | **79**（一致） | **78**/994 | +(兀尔德,原初的兀尔德)（R1 合并 传记作家兀尔德 时继承，仍死）；−(逃兵,两人)（R2 泛称摘除连带） |")
B("| grounding-none 名 | 967 | **967**（一致） | **965** | −旅行队的别斯米尔、−暴雨小组组长乌尔里希（R3 合并入落地节点）；R3 新增 店主米拉/玩具盒 均落地 |")
B("| claimed-mismatch 名 | 122 | **122**（一致） | **121** | −传记作家兀尔德（R1 合并） |")
B("")
B("**例外扫描**：")
B("")
B("- 查询路由豁免：420 条测试集查询（300_cn 300 + gen_r1r2 120）逐一与 78 条死别名做包含检查 → **仅 1 条命中**：`诊疗@诊所`（gen_r1r2 GA-25『在诊疗室门前等待时…』含『诊疗』）→ 按作战书规则 flag **keep-with-waiver**（R4-K01，keep_with_note），摘除与否留 Verifier+重校准裁决。")
B("- alias==他实体规范名：现图 **0 例**（QC 检3 已清零，本版复算确认）——无 cosmetic-only 条目。")
B("- 多主死别名 3 条：`特里格拉夫战列舰`（两名属主均死，摘除后 alias 消失）、`高地据点`（299高地 死/地下堡垒 活——摘除后 setdefault 语义自动重路由到活的属主，属改善）。")
B("")
B("**条目构成**：77 条 remove_alias = nowhere 类 " + str(n_nowhere) + "（全语料 0 命中，含继承的 `原初的兀尔德`@兀尔德、跨语名 CactusCat/ParadiseRegained/TierradelFuego/déjàvu/Launuacirklo/TheCongress）+ elsewhere 类 " + str(n_else) + "（他块出现、属主块 0 命中，如 `外国`@爱琴海 DF=21/10docs、`至高的秩序`@真理）。每条 evidence 含 df_in_owner=0 / df_corpus / elsewhere 例块与摘录（≤3）。")
B("")
B("**检索影响预判**：死别名是反向伤害——查询命中后 mention 通道锚到不含该词的块。摘除不影响任何测试集查询的种子集（§4 自验证 0/420 diff）。")
B("")
B("## 2. 交付二：实体标注 sidecar（entity_annotations.json）")
B("")
B("作战书 §1-R4 原文：『967 虚构接地规范名标注（grounding:none 元数据，不改名不删节点——删除影响面不可控）』。")
B("")
B("| 标注 | 数量 | 说明 |")
B("|---|---|---|")
B("| grounding:none | 965 | 规范名全语料逐字 0 命中（QC 967 → post-R3 965，差因见上）；note 统一含 QC 修复建议10 的检索侧处置（跳过 name-key 提及匹配） |")
B("| grounding:claimed_mismatch | 121 | 名在他块、不在声称块（QC elsewhere 122→121）；附 df_corpus + elsewhere_docs 供后续归属复核 |")
B("| per_story_generic | 9 | R2 flag_grounding_r4 ×9 移交（伙计/猎人/小孩/教师/水手/警卫/店主/卫兵/信众），story_scope_docs 按 **post-R3** 篇目重算——`店主` 经 R3-E15/E16 拆出 店主米拉 后已收敛为单篇（第一千夜×3），标注如实更新 |")
B("| cross_story_audit | 2 | 警卫（4 块 4 篇）、水手（3 块 2 篇）：R3-E17/E18 移交的跨篇焊复核，R4 裁决 **keep_no_split**（语料零具名、无 R1 式具名锚点、规模小），原句引文入档 |")
B("| metaphor_note | 1 | 玩具盒：R3-E08 的比喻意象限定（≠拉普拉斯装置 toy box 的英文语料读法），转入 sidecar |")
B("")
B("共标注 " + str(len(entity_annotations["annotations"])) + " 个 eid。**不改 graph.json、不做 desc 编辑**。")
B("")
B("## 3. 交付三：版本映射 sidecar（chunk_version_map.json）")
B("")
B("- 规则 = meetability 报告 meta.time_mapping_rule 的逐 doc 展开（mainline 查表 / activity 5位 XY→X.Y / character XY→X.Y / anecdote 推定 1.9(low) / appendix 文件名内嵌 X_Y；7 个 doc 无本地版本证据 → null）。")
B("- 覆盖：**3695/3695** chunk 全量入表；**3539 mapped / 156 null**（null=三联动文档 125 块 + 雷米特杯兑换/赛季·第十章·啁啾表 31 块）。")
B("- meetability 口径复核：『全图无版本化 chunk 的边』= **1243**/29957（与其 1243/29959 一致，R3 合并不改此数）；另计触及 null 块的边 1245 条。")
B("- 证据：compendium_clean_report × huiji_canon 版本弧 × plot_timeline 三源（全部本地）。版本分布 1.0×N…3.8 入 meta.version_distribution。")
B("")
B("## 4. 交付四：时间一致性审计（time_consistency_audit.md）")
B("")
B("- 重算跨版本边（chunk 覆盖 ≥2 版本）：**201** 条，对账 meetability 199（R3 乌尔里希合并去重 +3/−1，逐条列名）。")
B("- 分类：**A 章节重复伪跨版本 117**（23501/24501 整章互拷的镜像，根因语料层）/ **B 长线关系 81**（含 5 条 evidence 漂移但共现扎实）/ **C R3 合并伴生 3**（逐条证据复核）。")
B("- 删边裁决：预注册三判据（零共现 ∧ evidence 全部引用块不命中 ∧ 端点名全部引用块缺席）→ **0 条满足，0 delete_edge 提案**；201 条全部 documented keep。")
B("")
B("## 5. 自验证（_selfval.json，verdict=PASS）")
B("")
B("| 项 | 结果 |")
B("|---|---|")
B("| 逐条预检（Applier 同规则：属主存在、alias 在属主表） | 0 错误 / 0 警告 |")
B("| 模拟应用后全图后检（悬空 eid/chunk、重名、eid!=name、mentions==chunk_ids） | 0 错误 |")
B("| 变更面 | 仅 `aliases` 字段被改动（逐实体 diff 断言通过） |")
B("| 测试集路由：420 查询 link() 种子前后 diff（GraphStore.from_dict 同序 alias_index + retriever._name_matches 忠实模拟） | **0 / 420** 变化 |")
B("| 摘除串仍被查询命中 | 0（唯一命中的 诊疗 已豁免保留） |")
B("| 失去全部别名的属主 | 46 个（canonical 名与边通道不变；与 QC 记录的 0-alias 实体常态一致，无新增结构风险） |")
B("")
B("## 6. Verifier 交接要点")
B("")
B("1. D1 独立重推：只需属主声称块逐字判定 + 420 查询包含检查（_compute.py 口径），重点复核 3 条多主摘除与 R4-K01 豁免。")
B("2. D2 抽检建议：grounding:none 965 中抽 ≥30 个逐字复核；`探险家别斯米尔` 属 none（『探险家别斯米尔』非语料逐字串，语料作『别斯米尔（女士）』）——这是 R1 命名决策的已知形态，不是本版引入。")
B("3. D3 复核：anecdote→1.9 置信 low、7 个 null doc 的理由是否接受。")
B("4. D4 复核：三判据是否同意为『不可否认』标准；A 类 117 条是否同意根因归语料层。")
B("")
B("## 7. Applier 调用（供执行者）")
B("")
B("```bash")
B("./.venv/Scripts/python.exe scripts/_graph_apply_repairs.py \\")
B("  --proposal data/compendium_rag/repairs_v4/proposal.json --version-tag r4   # 干跑")
B("  # 确认全绿后加 --apply 落盘（将生成 backups/graph.json.prev.r4）")
B("```")
(R4 / "proposal_v4.md").write_text("\n".join(M), encoding="utf-8")
print(f"proposal_v4.md: {len(M)} lines")
print("ALL OUTPUTS WRITTEN")
