import json, sys
from pathlib import Path
sys.path.insert(0,"src")
from compendium_rag.graph_store import _merge_candidates, canonical_pick
ROOT=Path("data/compendium_rag")
obs={}
for p in sorted((ROOT/"cache").rglob("*.json")):
    try: o=json.loads(p.read_text(encoding="utf-8"))
    except Exception: continue
    raw=o.get("raw") or {}
    for e in raw.get("entities") or []:
        n=e.get("name")
        if not n: continue
        d=obs.setdefault(n,{"types":{},"aliases":set(),"descs":{}})
        d["types"][e.get("type")]=d["types"].get(e.get("type"),0)+1
        if e.get("desc"): d["descs"][e["desc"]]=d["descs"].get(e["desc"],0)+1
        for a in e.get("aliases") or []:
            if a: d["aliases"].add(a)
    for r in raw.get("relations") or []:
        for s in ("src","dst"):
            if r.get(s): obs.setdefault(r[s],{"types":{},"aliases":set(),"descs":{}})
CAND=["梁月","梁父","强梁","险道兽","方相氏","侲子","梁家","波蒂埃",
      "艾丽娅·波蒂埃","神秘学警察Ⅰ","神秘学警察Ⅱ","埃尔登警长","埃尔登",
      "针人","棍骗约翰","C07","菲林士多","乔什","调度中心","市民Ⅰ","市民Ⅱ",
      "老警察","男子","夜巡特遣管理局","见习执夜人","市政大厅","警长办公室",
      "餐馆","洛杉矶·神秘学犯罪科","洛杉矶·街道","神秘学犯罪科",
      "东亚分部","圣洛夫基金会东亚分部","慢慢吞","提线魔咒","拟影魔咒",
      "飞针神秘术","基础神秘学警情","神秘学警探C07","梁家的强梁"]
for n in CAND:
    d=obs.setdefault(n,{"types":{},"aliases":set(),"descs":{}})
    d["types"]["角色"]=d["types"].get("角色",0)+1
names=sorted(obs); ae=[]
for n,o in obs.items():
    for a in o["aliases"]:
        if a!=n: ae.append((n,a))
dsu=_merge_candidates(names,ae); groups={}
for n in names: groups.setdefault(dsu.find(n),[]).append(n)
cnt={n:sum(obs[n]["types"].values())+sum(obs[n]["descs"].values()) for n in names}
print("=== 注入后落点 ===")
for t in CAND:
    root=dsu.find(t); mem=sorted(groups[root]); canon=canonical_pick(mem,cnt)
    mark="✅" if canon==t else "❌"
    line=f"  {mark} {t:24s} canon={canon!r}"
    if t!=canon: line+=f"  组{len(mem)}: {[(m,cnt[m]) for m in sorted(mem,key=lambda x:-cnt[x])[:5]]}"
    print(line)
