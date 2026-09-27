# -*- coding: utf-8 -*-
"""R3 evidence round 2: targeted greps + chunk dumps for items 1-7. READ-ONLY."""
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

def ent(name):
    return gents.get(name)

def dump(cid, width=1500):
    t = chunks.get(cid)
    if t is None:
        P(f"!! missing chunk {cid}")
        return
    P(f"--- {cid} ({len(t)} chars) ---")
    P(t[:width])
    if len(t) > width:
        P(f"...[truncated {len(t)-width}]")

# ===== A. R090: 自囚 / 塔 in 阿莱夫 stories =====
P("===== A. R090 =====")
for term in ["自囚", "囚于", "central tower", "中央塔"]:
    hits = df(term)
    P(f"DF[{term}] = {len(hits)}: {hits[:10]}")
al = ent("阿莱夫")
P("阿莱夫 chunk_ids:", json.dumps(al["chunk_ids"], ensure_ascii=False))
P("-- 阿莱夫 chunks containing 塔:")
for cid in al["chunk_ids"]:
    t = chunks[cid]
    if "塔" in t:
        i = t.find("塔")
        P(f"  {cid}: ...{t[max(0,i-80):i+80]}...".replace("\n", " / "))
P("-- 阿莱夫 chunks containing 囚:")
for cid in al["chunk_ids"]:
    t = chunks[cid]
    for kw in ("囚", "自困", "困于"):
        i = t.find(kw)
        if i >= 0:
            P(f"  {cid} [{kw}]: ...{t[max(0,i-70):i+70]}...".replace("\n", " / "))
            break
# R090 gold reachability: chunks with 阿莱夫 AND (囚 or 塔)
for cid in al["chunk_ids"]:
    t = chunks[cid]
    if "自囚" in t or ("囚" in t and "塔" in t):
        P(f"  CAND gold {cid}: 自囚={'自囚' in t}")
        dump(cid, 900)

# ===== B. R127: 净化机 / 雾霾 / 伦敦 =====
P("\n===== B. R127 =====")
for term in ["净化机", "雾霾", "伦敦", "发明", "福格尔女士"]:
    hits = df(term)
    P(f"DF[{term}] = {len(hits)}")
    if term == "发明":
        docs = Counter(h.split(":")[0] for h in hits)
        P("  docs:", dict(docs))

# ===== C. R170: 玩具盒 full chunk + 36101 device scan =====
P("\n===== C. R170 =====")
dump("activity__27101_1987宇宙组曲:17.1.0", 2200)
for term in ["平衡伞", "玩具盒", "盒子"]:
    hits = df(term, "activity__36101")
    P(f"DF[{term}] in 36101 = {len(hits)}: {hits[:6]}")
hits = df("平衡伞")
P(f"DF[平衡伞] corpus = {len(hits)}: {hits[:8]}")

# ===== D. Ship: 摇滚苹果 / Rockin / 巨轮 / 二世 =====
P("\n===== D. Ship =====")
for term in ["摇滚苹果", "Rockin", "摇滚巨轮", "巨轮", "二世", "APPLe号"]:
    hits = df(term)
    P(f"DF[{term}] = {len(hits)}")
    for h in hits[:12]:
        t = chunks[h]
        i = t.find(term)
        P(f"  {h}: ...{t[max(0,i-50):i+len(term)+50]}...".replace("\n", " / "))

P("-- APPLe号 node chunk_ids:", json.dumps(ent("APPLe号")["chunk_ids"], ensure_ascii=False))
P("-- APPLe号摇滚巨轮二世 chunk_ids:", json.dumps(ent("APPLe号摇滚巨轮二世")["chunk_ids"], ensure_ascii=False))
for cid in ent("APPLe号")["chunk_ids"] + ent("APPLe号摇滚巨轮二世")["chunk_ids"]:
    dump(cid, 800)

# ===== E. 乌尔里希 quotes in activity/appendix (暴雨小组 side) =====
P("\n===== E. 乌尔里希 =====")
ul = ent("乌尔里希"); ul2 = ent("暴雨小组组长乌尔里希")
P("-- 暴雨小组组长乌尔里希 chunks mentioning bare 乌尔里希 (sample):")
cnt = 0
for cid in ul2["chunk_ids"]:
    t = chunks[cid]
    if "乌尔里希" in t:
        cnt += 1
        if cnt <= 8:
            i = t.find("乌尔里希")
            P(f"  {cid}: ...{t[max(0,i-60):i+60]}...".replace("\n", " / "))
P(f"  total {cnt}/{len(ul2['chunk_ids'])} chunks contain bare 乌尔里希")
P("-- 乌尔里希 node: sample quotes from mainline107/110:")
for cid in ul["chunk_ids"][:6] + ul["chunk_ids"][24:27]:
    t = chunks[cid]
    i = t.find("乌尔里希")
    if i >= 0:
        P(f"  {cid}: ...{t[max(0,i-60):i+60]}...".replace("\n", " / "))
P("-- full-name form 暴雨小组组长乌尔里希 DF:")
hits = df("暴雨小组组长乌尔里希")
P(f"  = {len(hits)}: {hits[:12]}")
hits2 = df("组长乌尔里希")
P(f"DF[组长乌尔里希] = {len(hits2)}: {hits2[:12]}")

# ===== F. 保罗 / 保罗·霍伊默尔 =====
P("\n===== F. 保罗 =====")
kr = ent("卡戎")
krc = set(kr["chunk_ids"])
hits_p = df("保罗")
in_owner = [h for h in hits_p if h in krc]
non_sp = [h for h in in_owner if "圣保罗" not in chunks[h]]
P(f"DF[保罗]={len(hits_p)}; in 卡戎 chunks={len(in_owner)}; in-owner non-圣保罗={len(non_sp)}")
for h in non_sp[:8]:
    t = chunks[h]
    i = t.find("保罗")
    P(f"  {h}: ...{t[max(0,i-50):i+50]}...".replace("\n", " / "))
P("-- in-owner chunks that are 圣保罗 collisions:")
for h in in_owner:
    if h not in non_sp:
        t = chunks[h]
        i = t.find("圣保罗")
        P(f"  {h}: ...{t[max(0,i-40):i+40]}...".replace("\n", " / "))
hits_ph = df("保罗·霍伊默尔")
P(f"DF[保罗·霍伊默尔]={len(hits_ph)}; in 卡戎: {[h for h in hits_ph if h in krc]}")
hits_sp = df("圣保罗")
P(f"DF[圣保罗]={len(hits_sp)}")
docs = Counter(h.split(":")[0] for h in hits_sp)
P("  圣保罗 docs:", dict(docs))

# ===== G. 旅行队的别斯米尔 chunk =====
P("\n===== G. 旅行队的别斯米尔 =====")
for cid in ent("旅行队的别斯米尔")["chunk_ids"]:
    dump(cid, 2400)
P("-- that chunk contains 别斯米尔?", "别斯米尔" in chunks[ent("旅行队的别斯米尔")["chunk_ids"][0]])
i = chunks[ent("旅行队的别斯米尔")["chunk_ids"][0]].find("别斯米尔")
t = chunks[ent("旅行队的别斯米尔")["chunk_ids"][0]]
P(f"  ctx: ...{t[max(0,i-120):i+120]}...".replace("\n", " / "))
P("-- 探险家别斯米尔 sample quotes:")
for cid in ent("探险家别斯米尔")["chunk_ids"][:5]:
    t = chunks[cid]
    i = t.find("别斯米尔")
    P(f"  {cid}: ...{t[max(0,i-60):i+60]}...".replace("\n", " / "))

with open(os.path.join(ROOT, "data", "compendium_rag", "repairs_v3", "_evidence_round2.txt"), "w", encoding="utf-8") as f:
    f.write(out.getvalue())
print("written", len(out.getvalue()))
