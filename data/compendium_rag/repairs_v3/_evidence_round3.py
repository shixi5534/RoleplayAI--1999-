# -*- coding: utf-8 -*-
"""R3 evidence round 3: generic-node chunks, claimants, huiji lookups. READ-ONLY."""
import io, sys, json, os, glob
from collections import Counter

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
out = io.StringIO()
def P(*a): print(*a, file=out)

G = json.load(open(os.path.join(ROOT, "data", "compendium_rag", "graph.json"), encoding="utf-8"))
CHL = json.load(open(os.path.join(ROOT, "data", "compendium_rag", "chunks.json"), encoding="utf-8"))["chunks"]
chunks = {c["chunk_id"]: c["text"] for c in CHL}
gents = G["entities"] if isinstance(G.get("entities"), dict) else {e["eid"]: e for e in G["entities"]}

# reverse index chunk -> claiming entities
claim = {}
for eid, e in gents.items():
    for cid in (e.get("chunk_ids") or []):
        claim.setdefault(cid, []).append(eid)

def df(term, restrict=None):
    return [cid for cid, t in chunks.items()
            if (not restrict or cid.startswith(restrict)) and term in t]

def dump_short(cid, width=700):
    t = chunks.get(cid)
    if t is None:
        P(f"!! missing {cid}"); return
    P(f"--- {cid} ---")
    P(t[:width].replace("\n", " / "))
    if len(t) > width: P(f"...[+{len(t)-width} chars]")

# ===== Item 7: 警卫 / 店主 / 水手 chunk dumps =====
P("===== Item 7 generic nodes =====")
for name in ["警卫", "店主", "水手"]:
    e = gents[name]
    P(f"\n## {name}: chunks={len(e['chunk_ids'])} aliases={e.get('aliases')} desc={e.get('desc')}")
    for cid in e["chunk_ids"]:
        P(f"  claimants of {cid}: {claim.get(cid, [])[:12]}")
        dump_short(cid, 900)

# ===== claimants for key chunks =====
P("\n===== claimants =====")
for cid in ["activity__27101_1987宇宙组曲:17.1.0", "mainline__105_洞穴的囚徒:0.0.1",
            "mainline__113_他者的悲哀:5.1.1", "mainline__113_他者的悲哀:19.1.1",
            "mainline__109_疯癫与文明:11.0.1", "mainline__111_行于漫漫长路上:14.0.2",
            "mainline__113_他者的悲哀:1.2.2"]:
    P(f"  {cid}: {claim.get(cid, [])[:20]}")

# ===== remaining DF checks =====
P("\n===== DF checks =====")
for term in ["暴雨小组组长", "暴雨小组", "别斯米尔女士", "旅行队的别斯米尔", "探险家别斯米尔",
             "玩具盒子", "瞭望塔", "无武装水手", "远行队", "店主", "水手", "警卫"]:
    hits = df(term)
    docs = Counter(h.split(":")[0] for h in hits)
    P(f"DF[{term}] = {len(hits)} docs={dict(docs)}")

# containment checks
def contain(term, owner):
    oc = set(gents[owner].get("chunk_ids") or [])
    hits = [h for h in df(term) if h in oc]
    P(f"containment[{term} @ {owner}] = {len(hits)}: {hits[:6]}")
    for h in hits[:3]:
        t = chunks[h]; i = t.find(term)
        P(f"   {h}: ...{t[max(0,i-50):i+len(term)+50]}...".replace("\n", " / "))

P("\n===== containment =====")
contain("别斯米尔女士", "探险家别斯米尔")
contain("瞭望塔", "阿莱夫")
contain("自囚", "阿莱夫")
contain("暴雨小组", "暴雨小组组长乌尔里希")
contain("乌尔里希先生", "乌尔里希")
# who else claims 乌尔里希-bare chunks
ulc = set(gents["乌尔里希"]["chunk_ids"])
ul2c = set(gents["暴雨小组组长乌尔里希"]["chunk_ids"])
P("乌尔里希∩暴雨乌尔里希 chunk overlap:", len(ulc & ul2c))
P("圣保罗 chunks also claimed by 卡戎:", [h for h in df("圣保罗") if h in ulc][:5])

# ===== huiji_alias_bridge_v2 lookups =====
P("\n===== huiji_alias_bridge_v2 =====")
bp = os.path.join(ROOT, "data", "knowledge", "_audit", "huiji_alias_bridge_v2.json")
if os.path.exists(bp):
    B = json.load(open(bp, encoding="utf-8"))
    P("bridge type:", type(B), "keys:", list(B.keys())[:8] if isinstance(B, dict) else len(B))
    def bsearch(term):
        found = []
        def walk(o, path=""):
            if isinstance(o, dict):
                for k, v in o.items():
                    if term in str(k):
                        found.append((path + "/" + str(k), str(v)[:220]))
                    walk(v, path + "/" + str(k)[:40])
            elif isinstance(o, list):
                for i, v in enumerate(o[:400]):
                    walk(v, path + f"[{i}]")
        walk(B)
        return found
    for term in ["乌尔里希", "别斯米尔", "菲林士多", "Noire", "福格尔", "卡戎", "金伯利", "玩具盒", "中央塔", "阿莱夫"]:
        r = bsearch(term)
        P(f"  [{term}] hits: {len(r)}")
        for p, v in r[:6]:
            P(f"    {p}: {v}")
else:
    P("bridge file missing")

with open(os.path.join(ROOT, "data", "compendium_rag", "repairs_v3", "_evidence_round3.txt"), "w", encoding="utf-8") as f:
    f.write(out.getvalue())
print("written", len(out.getvalue()))
