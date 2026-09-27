# -*- coding: utf-8 -*-
"""R4 修复者：生成 proposal.json（remove_alias ×N + keep_with_note ×1）。
只读 graph/chunks/_compute_results；只写本目录 proposal.json。
"""
import json, sys, io
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
R4 = Path(__file__).resolve().parent
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)

res = json.loads((R4 / "_compute_results.json").read_text(encoding="utf-8"))
g = json.loads((ROOT / "data/compendium_rag/graph.json").read_text(encoding="utf-8"))
ch = json.loads((ROOT / "data/compendium_rag/chunks.json").read_text(encoding="utf-8"))
ctext = {c["chunk_id"]: c["text"] for c in ch["chunks"]}
ents = {e["eid"]: e for e in g["entities"]}
ent_order = {e["eid"]: i for i, e in enumerate(g["entities"])}

dead = res["dead"]
# 属主 blob 内 0 命中复断 + elsewhere 例块 + 摘录
entries = []
kept = []
i = 0
for d in sorted(dead, key=lambda x: (x["owner"], x["alias"])):
    owner, alias = d["owner"], d["alias"]
    assert alias not in "\n".join(ctext[c] for c in ents[owner]["chunk_ids"] if c in ctext)
    if d["query_hits"]:
        kept.append(d)
        continue
    i += 1
    ev_chunks = []
    if d["df_total"] > 0:
        for cid, t in ctext.items():
            if alias in t:
                p = t.find(alias)
                snip = t[max(0, p - 20):p + len(alias) + 20].replace("\n", "⏎")
                ev_chunks.append({"chunk_id": cid, "doc": cid.split(":")[0], "snippet": snip})
                if len(ev_chunks) >= 3:
                    break
    tags = []
    if d["df_total"] == 0:
        tags.append("nowhere")
    else:
        tags.append("elsewhere")
    if d["multi_owner"]:
        others = [o for o in d["multi_owners"] if o != owner]
        alive_others = [o for o in others if alias in "\n".join(ctext[c] for c in ents[o]["chunk_ids"] if c in ctext)]
        if alive_others:
            first = min(alive_others + others, key=lambda o: ent_order.get(o, 10 ** 9))
            tags.append(f"multi_owner→removal re-routes alias_index[{alias}] to {alive_others[0]}"
                        + (f"（首属主 {first}，其声称块逐字含该串）" if alive_others else "（其余属主同为死别名，alias 将消失）"))
        else:
            tags.append("multi_owner_all_dead→alias 消失")
    if all(ord(c) < 128 or c.isascii() for c in alias):
        tags.append("cross_language_alias（语料 DF=0；如需保留须走『词表 alias 豁免』机制，本版按红线3 摘除）")
    if alias == "原初的兀尔德":
        tags.append("R1 disclosure inherited（R1 合并 传记作家兀尔德→兀尔德 时继承；任务书语境『允尔德』系『兀尔德』笔误）")
    qc_cls = "nowhere（QC 检3：全语料 0 命中）" if d["df_total"] == 0 else f"elsewhere（QC 检3：语料他块出现、属主块 0 命中，DF={d['df_total']}/{d['elsewhere_docs_n']}docs）"
    entries.append({
        "id": f"R4-E{i:02d}",
        "type": "remove_alias",
        "target": {"owner_eid": owner, "alias": alias},
        "owner": owner,
        "alias": alias,
        "evidence": {
            "df_in_owner": 0,
            "owner_nchunks": d["owner_chunks"],
            "df_corpus": d["df_total"],
            "qc_class": qc_cls,
            "elsewhere_examples": ev_chunks,
            "qc_ref": "docs/图谱与原文质检报告_20260926.md 检3（死 alias 79/1023 → 本版在 R1-R3 后图重算 78/994，逐条对账见 meta.baseline_recount）",
            "tags": tags,
        },
        "before": f"alias {alias}@{owner} 在属主 {d['owner_chunks']} 个声称块中逐字 0 命中（死别名）——查询若含该串将以 0.9 分注入 {owner} 为错锚点（mention 通道召回的块内并无此词）",
        "after": f"摘除 alias {alias}@{owner}；{owner} 规范名/边通道不变",
    })
# keep-with-waiver
wa = kept[0]
q = wa["query_hits"][0]
entries.append({
    "id": "R4-K01",
    "type": "keep_with_note",
    "target": "诊所",
    "note": f"死别名 {wa['alias']}@诊所 保留（测试集豁免）：gen_r1r2 [{q['qid']}] 查询「{q['q']}」含该串（『{wa['alias']}室』），"
            f"当前 link() 经 alias 0.9 种子 诊所（跨篇：犹在镜中/今夜星光灿烂/孤独之歌；GA-25 gold=卡卡尼亚@小房间）。"
            f"作战书规则：已知查询路由路径上的死别名 → keep-with-waiver 而非删除；摘除会改变该题种子集（可能消除跨篇错种子，但也属路由变更），"
            f"留给 Verifier/重校准闸门裁决后再动。DF={wa['df_total']}（{wa['elsewhere_docs_n']} docs）。",
    "evidence": [{"src": f"testset {q['testset']} {q['qid']}", "quote": q["q"]},
                 {"src": "graph 诊所", "quote": f"aliases={ents['诊所']['aliases']}; chunks={len(ents['诊所']['chunk_ids'])} 跨 3 篇"}],
    "before": "alias 诊疗@诊所 保留（waiver）",
    "after": "不变；建议 Verifier 裁决是否降级/摘除并重跑 GA-25",
})

other_canon = [d for d in dead if d["other_canonical"]]
proposal = {
    "meta": {
        "author": "R4-repairer-offline",
        "timestamp": "2026-09-26",
        "batch": "R4 死别名清理 + 实体标注 sidecar + 版本映射 sidecar + 时间一致性审计（作战书 §1-R4、§2 协议）",
        "network": "none（零网络；huiji WAF 403 已知，仅用本地缓存/词表，不涉身份裁决）",
        "graph_state": {
            "entities": res["n_entities"], "edges": res["n_edges"], "chunks": res["n_chunks"],
            "fingerprint": "7dc29bf90681a3f7",
            "state": "post-R1/R2/R3（R3 于 2026-09-27 应用于同指纹图）",
        },
        "dead_alias_rule": "dead = alias 不逐字出现在属主任一声称 chunk 文本（QC 检3 同口径保守红线3）；DF 口径 = 3695 块原文子串计数",
        "baseline_recount": {
            "pre_R1_graph": "backups/graph.json.prev.r1r2（7033 实体/29967 边）：dead 79 / grounding-none 967 —— 与 QC 检3 检2 完全一致（79/1023、967）",
            "current_post_R3": "dead 78 / grounding-none 965 / claimed-mismatch 121",
            "delta_dead": "+原初的兀尔德 由 传记作家兀尔德 继承至 兀尔德（R1 合并，仍死）；-（逃兵,两人）（R2 泛称摘除连带）→ 净 -1",
            "delta_none": "-旅行队的别斯米尔、-暴雨小组组长乌尔里希（R3 合并入落地名节点）；R3 新增 店主米拉/玩具盒 均落地（无新增死名）",
        },
        "exceptions_rule": "keep-with-waiver = 已知测试集（300_cn 420 题并集）查询串包含该死别名；alias==他实体规范名 = 现图 0 例（QC 检3 已清零，本版复算确认）",
        "applier_compat": "仅 remove_alias + keep_with_note（Applier NOOP）；无 desc 编辑——实体标注走 sidecar data/compendium_rag/repairs_v4/entity_annotations.json，不改 graph.json",
        "task_context_note": "任务书语境中的『允尔德』为『兀尔德』笔误：原初的兀尔德 死别名实际属主=兀尔德；R1/R2/R3 应用状态经读图核实一致",
        "sidecars": [
            "entity_annotations.json — 965 grounding:none + 121 claimed_mismatch + 9 per_story_generic + 玩具盒 metaphor + 警卫/水手 跨篇审计判定",
            "chunk_version_map.json — 3695 chunk→version（3539 有版本 / 156 null；1243 条无版本化 chunk 的边全部被 null 文档覆盖）",
            "time_consistency_audit.md — 201 条跨版本边分类（对账 meetability 199）：117 章节重复伪跨版本 + 81 长线关系 + 3 R3 合并伴生；0 删边提案",
        ],
    },
    "entries": entries,
}
(R4 / "proposal.json").write_text(json.dumps(proposal, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"proposal.json: {len(entries)} entries = {len(entries)-1} remove_alias + 1 keep_with_note; other_canonical cases: {len(other_canon)}")
