# -*- coding: utf-8 -*-
"""R3 evidence round 6: final DF + exact chunk lists + huiji quotes. READ-ONLY."""
import io, sys, json, os, re
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

P("== final DF checks ==")
for term in ["神秘警探C07", "神秘警探", "Noir", "雾气净化器", "净化器", "伦敦煤烟污染勘察与清除大使",
             "魅魔", "驱雾", "清洁大气"]:
    hits = df(term)
    docs = Counter(h.split(":")[0] for h in hits)
    P(f"DF[{term}] = {len(hits)} docs={dict(docs)}")

P("\n== 魅魔 node? ==")
for n in ["魅魔", "小魅魔"]:
    e = gents.get(n)
    if e:
        P(f"  node {n}: chunks={len(e.get('chunk_ids') or [])} aliases={e.get('aliases')} desc={e.get('desc')}")
        P("   its chunk docs:", dict(Counter(c.split(':')[0] for c in (e.get('chunk_ids') or []))))
# who owns bare alias 魅魔 via canonical-priority
P("  金伯利女郎 chunks containing bare 魅魔:",
  len([c for c in gents["金伯利女郎"]["chunk_ids"] if "魅魔" in chunks[c]]))

P("\n== 福葛先生 exact chunk list ==")
fug = df("福葛")
P(json.dumps(fug, ensure_ascii=False))
P("n =", len(fug))
P("福葛先生 node exists:", "福葛先生" in gents)
P("-- 福葛先生 verbatim in all 福葛 chunks?", all("福葛先生" in chunks[c] for c in fug))
only_fu = [c for c in fug if "福葛先生" not in chunks[c]]
P("chunks with 福葛 but not 福葛先生:", only_fu)

P("\n== 雾气净化器 chunks ==")
wq = df("雾气净化器")
P(json.dumps(wq, ensure_ascii=False))
for c in wq[:8]:
    t = chunks[c]; i = t.find("雾气净化器")
    P(f"  {c}: ...{t[max(0,i-50):i+60]}...".replace("\n", " / "))

P("\n== 伦敦煤烟污染勘察与清除大使 chunks ==")
ldn = df("伦敦煤烟污染勘察与清除大使")
P(json.dumps(ldn, ensure_ascii=False))

P("\n== 店主 exact chunk_ids ==")
dz = gents["店主"]["chunk_ids"]
P(json.dumps(dz, ensure_ascii=False))
P("乘法轴 subset:", [c for c in dz if "1917" in c])
P("第一千夜 subset:", [c for c in dz if "20603" in c])

P("\n== 中央瞭望塔 exact chunk_ids ==")
z = gents["中央瞭望塔"]["chunk_ids"]
P(json.dumps(z, ensure_ascii=False))
P("中央塔 verbatim subset:", [c for c in z if "中央塔" in chunks[c]])
P("desc/aliases:", gents["中央瞭望塔"].get("desc"), gents["中央瞭望塔"].get("aliases"))

P("\n== APPLe号摇滚巨轮二世 / APPLe号 / 菲林士多 node descs ==")
for n in ["APPLe号摇滚巨轮二世", "APPLe号", "菲林士多", "乌尔里希", "探险家别斯米尔", "旅行队的别斯米尔", "福格尔"]:
    e = gents[n]
    P(f"  {n}: type={e.get('type')} desc={e.get('desc')} aliases={e.get('aliases')}")

P("\n== huiji canon entries: 福葛 ==")
canon = json.load(open(os.path.join(ROOT, "data", "lore", "wu_ming_zhe", "huiji_canon.json"), encoding="utf-8"))
def find_key(obj, needle, path="", depth=0):
    if depth > 6:
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            if needle in str(k):
                P(f"  {path}/{k}:", json.dumps(v, ensure_ascii=False)[:500])
            find_key(v, needle, path + "/" + str(k)[:30], depth + 1)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            if isinstance(v, (dict, list)):
                find_key(v, needle, path + f"[{i}]", depth + 1)
            elif needle in str(v):
                P(f"  {path}[{i}]:", str(v)[:300])
for needle in ["福葛", "菲林士多", "Noire", "乌尔里希", "别斯米尔", "玩具盒"]:
    P(f" [{needle}]")
    find_key(canon, needle)
    lex = json.load(open(os.path.join(ROOT, "data", "lore", "wu_ming_zhe", "huiji_lexicon.json"), encoding="utf-8"))
    z2e = lex.get("zh2en", {})
    for k in z2e:
        if needle in k:
            P("  zh2en:", k, "->", json.dumps(z2e[k], ensure_ascii=False)[:200])

P("\n== huiji cache quote: 菲林士多/Noire (莫桑女士 page) ==")
raw = open(os.path.join(ROOT, "data", "lore", "_huiji_cache", "f8ae467bdc5b463db196.json"), encoding="utf-8").read()
for m in re.finditer(r"[^\"<>]{0,80}(Noire|菲林士多)[^\"<>]{0,80}", raw):
    P("   ...", m.group(0).replace("\n", " / ")[:160])

P("\n== huiji cache quote: 别斯米尔 (其他角色一览/1.x) ==")
raw = open(os.path.join(ROOT, "data", "lore", "_huiji_cache", "49910dc30331af4cb845.json"), encoding="utf-8").read()
for m in re.finditer(r"[^\"<>]{0,60}别斯米尔[^\"<>]{0,90}", raw):
    P("   ...", m.group(0).replace("\n", " / ")[:170])

P("\n== huiji cache quote: 乌尔里希 (圣洛夫基金会 page) ==")
raw = open(os.path.join(ROOT, "data", "lore", "_huiji_cache", "150c2161ffb8e33df537.json"), encoding="utf-8").read()
for m in list(re.finditer(r"[^\"<>]{0,60}乌尔里希[^\"<>]{0,90}", raw))[:8]:
    P("   ...", m.group(0).replace("\n", " / ")[:170])

P("\n== huiji cache quote: 福葛 (其他角色一览/2.x) ==")
raw = open(os.path.join(ROOT, "data", "lore", "_huiji_cache", "dd48cf716bfebe7c792b.json"), encoding="utf-8").read()
for m in list(re.finditer(r"[^\"<>]{0,60}福葛[^\"<>]{0,90}", raw))[:8]:
    P("   ...", m.group(0).replace("\n", " / ")[:170])

P("\n== huiji cache quote: 金伯利 (小径/唐人街影话) ==")
raw = open(os.path.join(ROOT, "data", "lore", "_huiji_cache", "6a693bbbbaeca0040b5b.json"), encoding="utf-8").read()
for m in list(re.finditer(r"[^\"<>]{0,50}(金伯利|Anjo|Nala)[^\"<>]{0,80}", raw))[:6]:
    P("   ...", m.group(0).replace("\n", " / ")[:150])

with open(os.path.join(ROOT, "data", "compendium_rag", "repairs_v3", "_evidence_round6.txt"), "w", encoding="utf-8") as f:
    f.write(out.getvalue())
print("written", len(out.getvalue()))
