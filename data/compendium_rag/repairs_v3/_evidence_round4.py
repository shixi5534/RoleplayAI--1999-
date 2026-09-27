# -*- coding: utf-8 -*-
"""R3 evidence round 4: 中央瞭望塔 node, 福葛/米拉, huiji cache greps. READ-ONLY."""
import io, sys, json, os, glob, re
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

# ===== nodes named *瞭望塔* / 米拉 / 福葛 / 蒂尔伯里 =====
P("===== node name checks =====")
for pat in ["瞭望塔", "米拉", "福葛", "福格", "蒂尔伯里", "冰淇淋", "路边小店", "蜡烛", "监测器"]:
    rx = re.compile(pat)
    hits = [n for n in gents if rx.search(n)]
    P(f"names~{pat}: {[(n, len(gents[n].get('chunk_ids') or [])) for n in sorted(hits)][:12]}")

P("\n===== 中央瞭望塔 node =====")
e = gents.get("中央瞭望塔")
if e:
    oc = e.get("chunk_ids") or []
    docs = Counter(cid.split(":")[0] for cid in oc)
    P("type:", e.get("type"), "desc:", e.get("desc"), "aliases:", e.get("aliases"))
    P("chunks:", len(oc), "docs:", dict(docs))
    P("edges n:", len(e.get("edges") or []))
    eg = e.get("edges") or []
    for ed in eg[:10]:
        P("  edge:", json.dumps(ed, ensure_ascii=False)[:150])
else:
    P("NOT FOUND")

# gold chunk 109:11.0.1 in its claims?
P("109:11.0.1 claimed by 中央瞭望塔:", "mainline__109_疯癫与文明:11.0.1" in (e.get("chunk_ids") if e else []))

# ===== 福葛 =====
P("\n===== 福葛 (R127 candidate) =====")
for term in ["福葛", "福葛先生"]:
    hits = df(term)
    P(f"DF[{term}] = {len(hits)}: {hits[:12]}")
P("-- 23101 装置/发明/净化 scan:")
for term in ["装置", "发明", "净化", "麻绳", "大型"]:
    hits = df(term, "activity__23101")
    P(f"DF[{term}] in 23101 = {len(hits)}")
hits = df("福葛")
for h in hits[:14]:
    t = chunks[h]; i = t.find("福葛")
    P(f"  {h}: ...{t[max(0,i-60):i+80]}...".replace("\n", " / "))

# ===== 米拉 =====
P("\n===== 米拉 =====")
hits = df("米拉")
P(f"DF[米拉] = {len(hits)}: {hits}")
for h in hits[:12]:
    t = chunks[h]; i = t.find("米拉")
    P(f"  {h}: ...{t[max(0,i-50):i+50]}...".replace("\n", " / "))
hits2 = df("冰淇淋店")
P(f"DF[冰淇淋店] = {len(hits2)}: {hits2[:6]}")
hits3 = df("路边小店")
P(f"DF[路边小店] = {len(hits3)}: {hits3[:6]}")
# first-thousand-night shopkeeper chunks contain 米拉?
for cid in ["character__20603_第一千夜:5.0.0", "character__20603_第一千夜:5.0.1", "character__20603_第一千夜:5.0.2"]:
    P(f"米拉 in {cid}:", "米拉" in chunks[cid])

# ===== 110:24.0.0 (卡戎 x 圣保罗) =====
P("\n===== 110:24.0.0 =====")
t = chunks["mainline__110_复乐园:24.0.0"]
i = t.find("圣保罗")
P(t[:600].replace("\n", " / "))
P(f"圣保罗 ctx: ...{t[max(0,i-60):i+80]}...")

# ===== huiji cache greps =====
P("\n===== huiji cache greps =====")
cache_dirs = [os.path.join(ROOT, "data", "lore", "_huiji_cache"),
              os.path.join(ROOT, "data", "lore", "wu_ming_zhe"),
              os.path.join(ROOT, "data", "compendium_rag", "huiji_pages")]
files = []
for d in cache_dirs:
    if os.path.isdir(d):
        files += glob.glob(os.path.join(d, "*.json"))
P("cache files:", len(files))
TERMS = ["乌尔里希", "别斯米尔", "菲林士多", "Noire", "福格尔", "福葛", "金伯利", "玩具盒", "中央瞭望塔", "卡戎", "Anjo", "契约魅魔"]
for fp in files:
    try:
        raw = open(fp, encoding="utf-8").read()
    except Exception as ex:
        P(f"!! read fail {fp}: {ex}")
        continue
    found = [t for t in TERMS if t in raw]
    if found:
        # find page title
        m = re.search(r'"title"\s*:\s*"([^"]+)"', raw)
        title = m.group(1) if m else os.path.basename(fp)
        P(f"  {os.path.relpath(fp, ROOT)} [{title}]: {found}")

with open(os.path.join(ROOT, "data", "compendium_rag", "repairs_v3", "_evidence_round4.txt"), "w", encoding="utf-8") as f:
    f.write(out.getvalue())
print("written", len(out.getvalue()))
