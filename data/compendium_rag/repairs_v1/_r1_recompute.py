# -*- coding: utf-8 -*-
"""R1 P0 焊拆 · 修复代理（离线）· 第三步：独立重算 + 修复模拟 + 自校验。
只读 graph.json / chunks.json；不写 graph.json。输出 _r1_recompute.json。
运行：PYTHONPATH=src PYTHONIOENCODING=utf-8 ./.venv/Scripts/python.exe data/compendium_rag/repairs_v1/_r1_recompute.py
"""
import json, time
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GRAPH = ROOT / "data/compendium_rag/graph.json"
CHUNKS = ROOT / "data/compendium_rag/chunks.json"
PREV = HERE / "_r1_weld_extract.json"
OUT = HERE / "_r1_recompute.json"

# ── 名字组（canonical + 别名，全部要求语料逐字）──
KAKANIA_NAMES = ["卡卡尼亚", "卡卡尼亚医生", "卡卡尼亚小姐",
                 "克拉拉", "克拉拉·温格勒", "克拉拉女士", "克拉拉小姐"]
URD_NAMES = ["兀尔德", "兀尔德女士", "传记作家兀尔德",
             "德洛丝", "德洛丝医生", "德洛丝女士", "无国界医生德洛丝"]
MARTA_NAMES = ["玛尔塔", "玛尔塔女士"]
BESSMERT_NAMES = ["别斯米尔", "探险家别斯米尔", "旅行队的别斯米尔"]

t0 = time.time()
g = json.loads(GRAPH.read_text(encoding="utf-8"))
ents = g["entities"] if isinstance(g.get("entities"), list) else list(g["entities"].values())
edges = g["edges"]
by_eid = {e.get("eid") or e.get("name"): e for e in ents}
cj = json.loads(CHUNKS.read_text(encoding="utf-8"))
chunk_by_id = {c["chunk_id"]: c for c in cj["chunks"]}
all_cids = [c["chunk_id"] for c in cj["chunks"]]

def ctext(cid, with_titles=True):
    c = chunk_by_id[cid]
    t = c.get("text") or ""
    if with_titles:
        t += "\n" + " ".join(x for x in [c.get("chapter_title"), c.get("part_title"),
                                         c.get("scene_title")] if x)
    return t

def hits(text, names):
    return [n for n in names if n in text]

# ── 1) 独立重算焊组 204 块归因（验证 predecessor extract）──
weld = by_eid["卡卡尼亚"]
weld_chunks = list(weld["chunk_ids"])
prev = json.loads(PREV.read_text(encoding="utf-8"))
prev_by_cid = {p["chunk_id"]: p for p in prev["per_chunk"]}

MEMBERS = ["卡卡尼亚", "德洛丝", "玛尔塔", "别斯米尔", "兀尔德", "克拉拉"]
mismatch = 0
combo = Counter()
per_chunk_recompute = {}
for cid in weld_chunks:
    t = ctext(cid)
    got = tuple(hits(t, MEMBERS))
    combo[" + ".join(got) if got else "(none)"] += 1
    per_chunk_recompute[cid] = list(got)
    p = prev_by_cid.get(cid)
    if p is None or sorted(p["members_text_titles"]) != sorted(got):
        mismatch += 1

# ── 2) 全语料逐字 DF（成员名 + 关键别名）──
ALL_NAMES = sorted(set(KAKANIA_NAMES + URD_NAMES + MARTA_NAMES +
                       ["别斯米尔", "德洛斯", "原初的兀尔德"]))
df = {n: 0 for n in ALL_NAMES}
chunks_with = defaultdict(list)
for c in cj["chunks"]:
    t = c.get("text") or ""
    for n in ALL_NAMES:
        if n in t:
            df[n] += 1
            chunks_with[n].append(c["chunk_id"])

# ── 3) 相关节点现状claims ──
cur_claims = {}
for eid in ["卡卡尼亚", "传记作家兀尔德", "探险家别斯米尔", "旅行队的别斯米尔"]:
    cur_claims[eid] = list(by_eid[eid]["chunk_ids"])

# 名字逐字块 vs 现状 claim 的差集（漏 grounding / 多 grounding）
claim_cross = {}
name_all = {"卡卡尼亚": "卡卡尼亚", "克拉拉": "克拉拉", "德洛丝": "德洛丝",
            "兀尔德": "兀尔德", "玛尔塔": "玛尔塔", "别斯米尔": "别斯米尔"}
for n, lst in chunks_with.items():
    in_weld = sum(1 for c in lst if c in set(weld_chunks))
    claim_cross[n] = {"df": len(lst), "in_weld204": in_weld,
                      "outside_weld204": len(lst) - in_weld}

# ── 4) 边重归属 ──
# 规则：对每条 incident 边，依次在 evidence 文本与边 chunk 文本中找成员名；
#   命中 唯一归属者 → move；命中多个 → multi（按证据里"主名"优先级裁决：
#   卡卡尼亚组 > 德洛丝/兀尔德组 > 玛尔塔 > 别斯米尔；若同块双名并列则 split 记录）；
#   全不命中 → 按 edge chunk 的归属投票；仍平 → keep（标记 review）。
ROUTE_KAKANIA = "卡卡尼亚"; ROUTE_URD = "兀尔德"
ROUTE_MARTA = "玛尔塔"; ROUTE_BESS = "探险家别斯米尔"

new_claims = defaultdict(set)   # eid -> chunk_ids (post-repair)
for cid in weld_chunks:
    ms = set(per_chunk_recompute[cid])
    if "卡卡尼亚" in ms or "克拉拉" in ms:
        new_claims[ROUTE_KAKANIA].add(cid)
    if "德洛丝" in ms or "兀尔德" in ms:
        new_claims[ROUTE_URD].add(cid)
    if "玛尔塔" in ms:
        new_claims[ROUTE_MARTA].add(cid)
    if "别斯米尔" in ms:
        new_claims[ROUTE_BESS].add(cid)

edge_action = {"keep": [], "move": [], "multi": [], "review": []}
for ed in edges:
    if ed.get("src") != "卡卡尼亚" and ed.get("dst") != "卡卡尼亚":
        continue
    ev = ed.get("evidence") or ""
    h_ev = set()
    for n in KAKANIA_NAMES:
        if n in ev: h_ev.add(ROUTE_KAKANIA); break
    for n in URD_NAMES:
        if n in ev: h_ev.add(ROUTE_URD); break
    for n in MARTA_NAMES:
        if n in ev: h_ev.add(ROUTE_MARTA); break
    if "别斯米尔" in ev: h_ev.add(ROUTE_BESS)
    cids = ed.get("chunk_ids") or []
    h_chunk = defaultdict(int)
    for cid in cids:
        for tgt in new_claims:
            if cid in new_claims[tgt]:
                h_chunk[tgt] += 1
    if len(h_ev) == 1:
        tgt = next(iter(h_ev))
        edge_action["move" if tgt != ROUTE_KAKANIA else "keep"].append(
            {"edge": [ed["src"], ed.get("relation"), ed["dst"]], "to": tgt,
             "how": "evidence", "evidence": ev[:100]})
    elif len(h_ev) > 1:
        edge_action["multi"].append({"edge": [ed["src"], ed.get("relation"), ed["dst"]],
                                     "evidence_hits": sorted(h_ev), "evidence": ev[:100]})
    else:
        if len(h_chunk) == 1:
            tgt = next(iter(h_chunk))
            edge_action["move" if tgt != ROUTE_KAKANIA else "keep"].append(
                {"edge": [ed["src"], ed.get("relation"), ed["dst"]], "to": tgt,
                 "how": "chunk-vote", "evidence": ev[:100]})
        elif len(h_chunk) > 1:
            edge_action["multi"].append({"edge": [ed["src"], ed.get("relation"), ed["dst"]],
                                         "chunk_votes": dict(h_chunk), "evidence": ev[:100]})
        else:
            edge_action["review"].append({"edge": [ed["src"], ed.get("relation"), ed["dst"]],
                                          "evidence": ev[:100], "chunk_ids": cids})

# ── 5) 焊组外：新节点名字逐字块是否已被声称 ──
outside = {}
weld_set = set(weld_chunks)
claimed_any = {eid: set(v) for eid, v in cur_claims.items()}
for n in ["兀尔德", "德洛丝", "玛尔塔", "别斯米尔", "传记作家兀尔德"]:
    outs = [c for c in chunks_with.get(n, []) if c not in weld_set]
    detail = []
    for cid in outs:
        owners = [eid for eid, s in claimed_any.items() if cid in s]
        detail.append({"chunk_id": cid, "current_owners": owners})
    outside[n] = detail

# (none) 10 块内容速览
none_chunks = [cid for cid in weld_chunks if not per_chunk_recompute[cid]]
none_info = [{"chunk_id": cid, "doc": cid.rsplit(":",1)[0],
              "speakers": chunk_by_id[cid].get("speakers"),
              "text_head": (chunk_by_id[cid].get("text") or "")[:120]} for cid in none_chunks]

out = {
    "meta": {"script": "_r1_recompute.py", "ran_at": time.strftime("%Y-%m-%d %H:%M:%S"),
             "elapsed_sec": round(time.time() - t0, 1)},
    "validation_vs_predecessor": {"per_chunk_mismatches": mismatch, "weld_chunks": len(weld_chunks)},
    "combo_recompute": dict(combo),
    "df_verbatim": df,
    "claim_cross": claim_cross,
    "cur_claims_size": {k: len(v) for k, v in cur_claims.items()},
    "new_claims_size_from_weld204": {k: len(v) for k, v in new_claims.items()},
    "edge_action_summary": {k: len(v) for k, v in edge_action.items()},
    "edge_action": edge_action,
    "outside_string_chunks": outside,
    "none_chunks": none_info,
}
OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print("== recompute done ==")
print("vs predecessor per_chunk mismatches:", mismatch)
print("combo:", dict(combo))
print("df:", df)
print("claim_cross:", json.dumps(claim_cross, ensure_ascii=False))
print("new_claims from weld204:", {k: len(v) for k, v in new_claims.items()})
print("edge_action:", {k: len(v) for k, v in edge_action.items()})
print("edge move targets:", Counter(m["to"] for m in edge_action["move"]))
print("multi detail:", json.dumps(edge_action["multi"], ensure_ascii=False, indent=1)[:1500])
print("review n:", len(edge_action["review"]))
print("outside:", json.dumps({k: len(v) for k, v in outside.items()}, ensure_ascii=False))
for n, lst in outside.items():
    own = Counter()
    for d in lst:
        own[tuple(d["current_owners"])] += 1
    print("  outside", n, dict(own))
print("none chunks:", json.dumps(none_info, ensure_ascii=False, indent=1))
