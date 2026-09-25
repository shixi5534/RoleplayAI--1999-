import json, sys
from pathlib import Path
sys.path.insert(0,"src")
from compendium_rag.graph_store import GraphStore, _merge_candidates, canonical_pick
ROOT=Path("data/compendium_rag"); g=GraphStore.load(ROOT/"graph.json")
for n in ["玛蒂尔达","病房","医生","医护人员","度朔节","神秘学藏品管理部","拉普拉斯康复中心"]:
    e=g.entities.get(n)
    print(f"  {n:12s} " + (f"{e.type:4s} m={e.mentions:3d} aliases={e.aliases[:4]} desc={e.desc!r}" if e else "[不在图]"))
print()
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
CAND=["奇星","艾瑞克·黄","丽莲·刘","民间侦探","女子","值班医生","青年警察",
      "蔬菜店","拉普拉斯康复中心合作医院","银针神秘术","社火游行",
      "金属变色龙通信器","自动贩卖机","橙汁","变身术","医院","艾瑞克",
      "橙子汁"," 变身神秘术"]
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
    line=f"  {mark} {t:26s} canon={canon!r}"
    if t!=canon: line+=f"  组{len(mem)}: {[(m,cnt[m]) for m in sorted(mem,key=lambda x:-cnt[x])[:5]]}"
    print(line)
