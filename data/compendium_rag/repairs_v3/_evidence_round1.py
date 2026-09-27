# -*- coding: utf-8 -*-
"""R3 evidence round 1: DF + owner containment for candidate aliases/bridges.
READ-ONLY on graph.json / chunks.json."""
import io, sys, json, os
from collections import Counter

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
out = io.StringIO()

def P(*a):
    print(*a, file=out)

G = json.load(open(os.path.join(ROOT, "data", "compendium_rag", "graph.json"), encoding="utf-8"))
CHL = json.load(open(os.path.join(ROOT, "data", "compendium_rag", "chunks.json"), encoding="utf-8"))["chunks"]
chunks = {c["chunk_id"]: c["text"] for c in CHL}

gents = G["entities"] if isinstance(G.get("entities"), dict) else {e["eid"]: e for e in G["entities"]}
P("graph entities:", len(gents), "top edges:", len(G.get("edges", [])))

def get_ent(name):
    return gents.get(name)

def ent_chunks(name):
    e = get_ent(name)
    return list(e.get("chunk_ids") or []) if e else None

def df(term, restrict=None):
    hits = []
    for cid, t in chunks.items():
        if restrict and not cid.startswith(restrict):
            continue
        if term in t:
            hits.append(cid)
    return hits

def show_hits(hits, term, n=6, width=60):
    for h in hits[:n]:
        t = chunks[h]
        i = t.find(term)
        P(f"    {h}: ...{t[max(0,i-50):i+len(term)+50].replace(chr(10), ' / ')}...")
    if len(hits) > n:
        P(f"    ... +{len(hits)-n} more")

# ---------- Item 1 greps ----------
TERMS = ["Noire", "中央塔", "福格", "福格尔", "福格先生", "净化", "契约魅魔", "格蕾丝", "玩具盒", "toy", "Toy"]
for term in TERMS:
    hits = df(term)
    P(f"\n== DF[{term}] = {len(hits)}")
    docs = Counter(h.split(":")[0] for h in hits)
    P("   docs:", dict(docs))
    if hits:
        show_hits(hits, term)

# owner containment
for term, owner in [("中央塔", "阿莱夫"), ("福格", "福格尔"), ("契约魅魔", "金伯利女郎"), ("玩具盒", "科算中心")]:
    oc = ent_chunks(owner)
    if oc is None:
        P(f"\n## owner {owner} MISSING")
        continue
    hits = df(term)
    inter = [h for h in hits if h in set(oc)]
    P(f"\n## containment[{term!r} @ {owner}]: owner_chunks={len(oc)}, term_hits={len(hits)}, in_owner={len(inter)}")
    for h in inter[:5]:
        t = chunks[h]
        i = t.find(term)
        P(f"    {h}: ...{t[max(0,i-60):i+len(term)+60].replace(chr(10), ' / ')}...")

# ---------- owner chunk doc distributions ----------
for name in ["菲林士多", "阿莱夫", "福格尔", "金伯利女郎", "乌尔里希", "暴雨小组组长乌尔里希",
             "探险家别斯米尔", "旅行队的别斯米尔", "APPLe号", "APPLe号摇滚巨轮二世", "APPLe",
             "警卫", "店主", "水手", "卡戎", "科算中心"]:
    e = get_ent(name)
    if e is None:
        P(f"\n## {name}: NOT IN GRAPH")
        continue
    oc = ent_chunks(name)
    docs = Counter(cid.split(":")[0] for cid in oc)
    P(f"\n## {name}: chunks={len(oc)} mentions={e.get('mentions')} type={e.get('type')} aliases={e.get('aliases')}")
    P("   doc dist:", dict(docs))

with open(os.path.join(ROOT, "data", "compendium_rag", "repairs_v3", "_evidence_round1.txt"), "w", encoding="utf-8") as f:
    f.write(out.getvalue())
print("written _evidence_round1.txt", len(out.getvalue()))
