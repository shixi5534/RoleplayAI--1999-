# -*- coding: utf-8 -*-
"""R3 evidence round 5: huiji canon entries + final verbatim checks. READ-ONLY."""
import io, sys, json, os
from collections import Counter

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
out = io.StringIO()
def P(*a): print(*a, file=out)

G = json.load(open(os.path.join(ROOT, "data", "compendium_rag", "graph.json"), encoding="utf-8"))
CHL = json.load(open(os.path.join(ROOT, "data", "compendium_rag", "chunks.json"), encoding="utf-8"))["chunks"]
chunks = {c["chunk_id"]: c["text"] for c in CHL}
gents = G["entities"] if isinstance(G.get("entities"), dict) else {e["eid"]: e for e in G["entities"]}

def df(term, restrict=None):
    return [cid for cid, t in chunks.items()
            if (not restrict or cid.startswith(restrict)) and term in t]

# ===== huiji canon / lexicon / wiki_zh_en / plot_aliases =====
P("===== wu_ming_zhe lexicons =====")
for fn in ["huiji_canon.json", "huiji_lexicon.json", "wiki_zh_en.json", "plot_aliases.json", "plot_glossary.json"]:
    fp = os.path.join(ROOT, "data", "lore", "wu_ming_zhe", fn)
    d = json.load(open(fp, encoding="utf-8"))
    P(f"\n## {fn}: type={type(d).__name__}, keys={list(d.keys())[:6] if isinstance(d, dict) else len(d)}")
    items = d if isinstance(d, list) else (d.get("entries") or d.get("canon") or d.get("terms") or d.get("aliases") or d)
    if isinstance(items, dict):
        for key in ["乌尔里希", "别斯米尔", "菲林士多", "Noire", "福葛", "金伯利", "金伯利女郎", "卡戎", "保罗", "玩具盒", "中央塔", "中央瞭望塔", "Anjo Nala", "天使娜娜"]:
            if key in items:
                P(f"  [{key}]:", json.dumps(items[key], ensure_ascii=False)[:400])
    elif isinstance(items, list):
        for it in items:
            s = json.dumps(it, ensure_ascii=False)
            if any(k in s for k in ["乌尔里希", "别斯米尔", "菲林士多", "Noire", "福葛", "金伯利", "卡戎", "玩具盒", "Anjo"]):
                P("  ", s[:400])

# ===== 23101 device scan (R127) =====
P("\n===== 23101 净化/大型 contexts =====")
for term in ["净化", "大型"]:
    for h in df(term, "activity__23101"):
        t = chunks[h]; i = t.find(term)
        P(f"  [{term}] {h}: ...{t[max(0,i-90):i+90]}...".replace("\n", " / "))

# ===== verbatim checks for 米拉 naming =====
P("\n===== 米拉 node naming candidates =====")
own = [c for c in df("米拉") if c.startswith("anecdote__1917")]
P("乘法轴 chunks with 米拉:", own)
for s in ["冰淇淋店店主", "店主米拉", "米拉小姐", "冰淇淋店主", "老板"]:
    hits = [c for c in own if s in chunks[c]]
    P(f"  DF[{s}] in 乘法轴/米拉-chunks = {len(hits)}")
    for h in hits[:3]:
        t = chunks[h]; i = t.find(s)
        P(f"    {h}: ...{t[max(0,i-40):i+len(s)+40]}...".replace("\n", " / "))

# ===== 饭店店主罗莎 precedent =====
e = gents.get("饭店店主罗莎")
P("\n饭店店主罗莎 node:", json.dumps({k: e.get(k) for k in ('eid','name','type','aliases','desc')}, ensure_ascii=False) if e else None)

# ===== 旅行队的别斯米尔 chunk claimants + merge overlap =====
P("\n===== 旅行队的别斯米尔 =====")
tvid = "appendix_unbound__006_1_6_赛季剧情:4.1.0"
claim = {}
for eid, ee in gents.items():
    for cid in (ee.get("chunk_ids") or []):
        claim.setdefault(cid, []).append(eid)
P("claimants:", claim.get(tvid))
e2 = gents["探险家别斯米尔"]
P("探险家别斯米尔 desc:", e2.get("desc"), "type:", e2.get("type"))
P("appendix chunk has 别斯米尔女士:", "别斯米尔女士" in chunks[tvid])
P("探险家别斯米尔 chunk_ids contains appendix__006:", [c for c in e2["chunk_ids"] if "appendix" in c])

# ===== 暴雨乌尔里希: the 1 chunk without bare 乌尔里希 =====
ul2 = gents["暴雨小组组长乌尔里希"]
nohit = [c for c in ul2["chunk_ids"] if "乌尔里希" not in chunks[c]]
P("\n暴雨乌尔里希 chunks WITHOUT bare 乌尔里希:", nohit)
for c in nohit:
    P("  text head:", chunks[c][:200].replace("\n", " / "))

# ===== 水手 23101 chunk: name of that sailor =====
t = chunks["activity__23101_圣火纪行_东区黎明:7.1.0"]
i = t.find("水手")
P("\n23101 水手 ctx:", t[max(0,i-120):i+120].replace("\n", " / "))

# ===== 卡戎 19 保罗-chunks: any that mention 圣保罗 (verified 0) + 拉普拉斯 alias check =====
P("\n金伯利女郎 edges to 77号往事 story?")
kb = gents["金伯利女郎"]
P("金伯利女郎 chunk count in 21101:", len([c for c in kb["chunk_ids"] if "21101" in c]))
st = gents.get("77号往事")
P("77号往事 node:", json.dumps({k: (st or {}).get(k) for k in ('eid','name','type','aliases','desc')}, ensure_ascii=False)[:200] if st else None)
s77 = [n for n in gents if "77" in n]
P("names containing 77:", s77[:10])

# ===== 保罗 removal: check who else could own 保罗 alias =====
paul_owners = [n for n, ee in gents.items() if "保罗" in (ee.get("aliases") or [])]
P("\nnodes with 保罗 alias:", paul_owners)
paul_nodes = [n for n in gents if n == "保罗" or "保罗" in n]
P("nodes named *保罗*:", [(n, len(gents[n].get('chunk_ids') or [])) for n in paul_nodes])

with open(os.path.join(ROOT, "data", "compendium_rag", "repairs_v3", "_evidence_round5.txt"), "w", encoding="utf-8") as f:
    f.write(out.getvalue())
print("written", len(out.getvalue()))
