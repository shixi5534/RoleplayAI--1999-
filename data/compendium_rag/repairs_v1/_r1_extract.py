# -*- coding: utf-8 -*-
"""R1 P0 焊拆 · 修复代理 · 第一步：焊组提取 + 语料足迹（只读，不改 graph.json/corpus.json）。
单遍加载 graph.json / chunks.json，全部在内存内完成；输出中间证据到本目录。
运行：PYTHONPATH=src PYTHONIOENCODING=utf-8 ./.venv/Scripts/python.exe data/compendium_rag/repairs_v1/_r1_extract.py
"""
import json, time, sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
GRAPH = ROOT / "data/compendium_rag/graph.json"
CHUNKS = ROOT / "data/compendium_rag/chunks.json"
OUT = Path(__file__).resolve().parent / "_r1_weld_extract.json"

WELD = "卡卡尼亚"
MEMBERS = ["卡卡尼亚", "德洛丝", "玛尔塔", "别斯米尔", "兀尔德", "克拉拉"]
EN_NAMES = ["Kakania", "Dolores", "Dores", "Marta", "Bessmert", "Bessmer",
            "Urd", "Urdr", "Clara", "Klara"]
# 15 条在册 alias + 候选新 alias（用于逐字 DF 验证）
ALIAS_CANDIDATES = [
    "兀尔德", "兀尔德女士", "克拉拉", "克拉拉·温格勒", "克拉拉女士", "克拉拉小姐",
    "别斯米尔", "卡卡尼亚医生", "卡卡尼亚小姐", "德洛丝", "德洛丝医生",
    "德洛丝女士", "无国界医生德洛丝", "玛尔塔", "玛尔塔女士",
    "传记作家兀尔德", "原初的兀尔德", "德洛斯", "德洛斯医生",
]

t0 = time.time()
g = json.loads(GRAPH.read_text(encoding="utf-8"))
ents = g["entities"] if isinstance(g.get("entities"), list) else list(g["entities"].values())
edges = g["edges"]
by_eid = {}
for e in ents:
    by_eid[e.get("eid") or e.get("name")] = e
n_eid_name_mismatch = sum(1 for e in ents if e.get("eid") != e.get("name"))

node = by_eid.get(WELD)
assert node is not None, "weld node missing"
weld_aliases = list(node.get("aliases") or [])
weld_chunks = list(node.get("chunk_ids") or [])

# ── 成员名节点是否存在（含包含式，如 传记作家兀尔德）──
member_nodes = []
for eid, e in by_eid.items():
    nm = e.get("name", "")
    for m in MEMBERS:
        if m in nm and nm != WELD:
            member_nodes.append({"eid": eid, "type": e.get("type"),
                                 "mentions": e.get("mentions"),
                                 "n_chunks": len(e.get("chunk_ids") or []),
                                 "aliases": e.get("aliases"),
                                 "desc": (e.get("desc") or "")[:120],
                                 "chunk_ids": list(e.get("chunk_ids") or [])})
            break

# ── 15 alias 的当前全图属主（多主检查）──
alias_owners = defaultdict(list)
for e in ents:
    eid = e.get("eid") or e.get("name")
    if eid == WELD:
        continue
    for a in (e.get("aliases") or []):
        if a in set(weld_aliases) | {"传记作家兀尔德", "原初的兀尔德"}:
            alias_owners[a].append(eid)
    nm = e.get("name", "")
    if nm in set(weld_aliases):
        alias_owners[nm].append("<canonical-name:" + eid + ">")

# ── 焊组全部边 ──
incident = [ed for ed in edges if ed.get("src") == WELD or ed.get("dst") == WELD]
deg_edges = len(incident)
deg_chunksum = sum(len(ed.get("chunk_ids") or []) for ed in incident)
edges_out = [{"src": ed["src"], "dst": ed["dst"], "relation": ed.get("relation", ""),
              "confidence": ed.get("confidence"), "evidence": (ed.get("evidence") or "")[:160],
              "chunk_ids": list(ed.get("chunk_ids") or []), "count": ed.get("count")} for ed in incident]

# ── chunks.json 单遍加载 + 归因 ──
cj = json.loads(CHUNKS.read_text(encoding="utf-8"))
all_chunks = cj["chunks"]
chunk_by_id = {c["chunk_id"]: c for c in all_chunks}
missing = [cid for cid in weld_chunks if cid not in chunk_by_id]
assert not missing, f"dangling weld chunks: {missing}"

def scan_names(text):
    zh = {m: (m in text) for m in MEMBERS}
    en = {n: (n in text) for n in EN_NAMES if n in text}
    return zh, en

per_chunk = []
for cid in weld_chunks:
    c = chunk_by_id[cid]
    text = c.get("text") or ""
    titles = " ".join(x for x in [c.get("chapter_title"), c.get("part_title"),
                                  c.get("scene_title")] if x)
    speakers = c.get("speakers") or []
    zh_t, en_t = scan_names(text)
    zh_tt, en_tt = scan_names(text + "\n" + titles)
    present_t = [m for m in MEMBERS if zh_t[m]]
    present_tt = [m for m in MEMBERS if zh_tt[m]]
    # 命中的具体 alias 写法（evidence 引用用）
    alias_hits = [a for a in ALIAS_CANDIDATES if a in text]
    per_chunk.append({
        "chunk_id": cid, "doc_id": c.get("doc_id"),
        "chapter": c.get("chapter_title"), "part": c.get("part_title"),
        "scene": c.get("scene_title"), "speakers": speakers,
        "text_len": len(text),
        "members_text": present_t, "members_text_titles": present_tt,
        "en_hits_text": en_t, "alias_hits_text": alias_hits,
    })

combo_t = Counter(tuple(p["members_text"]) for p in per_chunk)
combo_tt = Counter(tuple(p["members_text_titles"]) for p in per_chunk)

# ── 全语料成员名 DF（新节点收编范围）──
df_all = {m: 0 for m in MEMBERS}
member_corpus_chunks = {m: [] for m in MEMBERS}
for c in all_chunks:
    text = c.get("text") or ""
    for m in MEMBERS:
        if m in text:
            df_all[m] += 1
            member_corpus_chunks[m].append(c["chunk_id"])

# alias 逐字 DF：全语料 / 焊组 204 块内
df_alias_all, df_alias_weld = {}, {}
for a in ALIAS_CANDIDATES:
    df_alias_all[a] = sum(1 for c in all_chunks if a in (c.get("text") or ""))
    df_alias_weld[a] = sum(1 for cid in weld_chunks if a in (chunk_by_id[cid].get("text") or ""))

# 每个成员名：语料哪些篇章
def doc_dist(cids):
    d = Counter(cid.rsplit(":", 1)[0] for cid in cids)
    return dict(d)

doc_dist_member = {m: doc_dist(member_corpus_chunks[m]) for m in MEMBERS}
doc_dist_weld = doc_dist(weld_chunks)

# 传记作家兀尔德 详情（连带分裂候选）
bio = next((mn for mn in member_nodes if mn["eid"] == "传记作家兀尔德"), None)
bio_edges = []
if bio:
    bio_edges = [{"src": ed["src"], "dst": ed["dst"], "relation": ed.get("relation", ""),
                  "confidence": ed.get("confidence"), "evidence": (ed.get("evidence") or "")[:160],
                  "chunk_ids": list(ed.get("chunk_ids") or [])}
                 for ed in edges if ed.get("src") == "传记作家兀尔德" or ed.get("dst") == "传记作家兀尔德"]

out = {
    "meta": {"script": "_r1_extract.py", "ran_at": time.strftime("%Y-%m-%d %H:%M:%S"),
             "graph_schema": g.get("schema"), "graph_fingerprint": g.get("fingerprint"),
             "n_entities": len(ents), "n_edges": len(edges),
             "eid_eq_name_mismatches": n_eid_name_mismatch,
             "elapsed_sec": round(time.time() - t0, 1)},
    "weld_node": {"eid": node.get("eid"), "name": node.get("name"), "type": node.get("type"),
                  "desc": node.get("desc"), "mentions": node.get("mentions"),
                  "n_chunk_ids": len(weld_chunks), "aliases": weld_aliases},
    "degree": {"incident_edges": deg_edges, "sum_edge_chunk_ids": deg_chunksum},
    "member_nodes": member_nodes,
    "alias_owners_other_than_weld": dict(alias_owners),
    "edges_incident": edges_out,
    "per_chunk": per_chunk,
    "combo_text": {" + ".join(k) if k else "(none)": v for k, v in combo_t.items()},
    "combo_text_titles": {" + ".join(k) if k else "(none)": v for k, v in combo_tt.items()},
    "corpus_df": {"members_all": df_all, "member_corpus_chunks": member_corpus_chunks,
                  "doc_dist_member": doc_dist_member, "doc_dist_weld": doc_dist_weld,
                  "alias_df_all": df_alias_all, "alias_df_in_weld204": df_alias_weld},
    "biographer_兀尔德": {"node": bio, "edges": bio_edges},
}
OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

print("== R1 extract done ==")
print("eid==name mismatches:", n_eid_name_mismatch)
print("weld aliases:", weld_aliases)
print("chunks:", len(weld_chunks), "deg_edges:", deg_edges, "deg_chunksum:", deg_chunksum)
print("combo(text):", dict(combo_t))
print("combo(text+titles):", dict(combo_tt))
print("member nodes found:", [mn["eid"] for mn in member_nodes])
print("corpus DF:", df_all)
print("doc_dist weld:", doc_dist_weld)
for m in MEMBERS:
    print(f"doc_dist[{m}]:", doc_dist_member[m])
print("alias DF all:", df_alias_all)
print("alias DF in weld204:", df_alias_weld)
print("alias owners (non-weld):", dict(alias_owners))
