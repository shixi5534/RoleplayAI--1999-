import json, sys
from pathlib import Path
sys.path.insert(0,"src")
from compendium_rag.graph_store import _merge_candidates, canonical_pick, GraphStore
ROOT=Path("data/compendium_rag"); g=GraphStore.load(ROOT/"graph.json")
for n in ["星锑空间望远镜","天文望远镜","唱片","小东西","神秘学唱片机","面具",
          "人工暴雨","非对称核素R","鸽子屋","会长","奥尔德堡","基金会高层办公室"]:
    e=g.entities.get(n)
    print(f"  {n:18s} " + (f"{e.type:4s} m={e.mentions:3d} aliases={e.aliases[:4]} desc={e.desc!r}" if e else "[不在图]"))
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
CAND=["客人Ⅰ","客人Ⅱ","客人Ⅲ","弗兰克先生","亨利先生","特里波德罗",
      "克罗纳拉发射场旧址","克罗纳拉","圭亚那航天中心","普列谢茨克航天发射场",
      "悉尼港","船长室","南美分部","大洋洲","数字岛","人工暴雨项目",
      "美国航空航天局","基金会高层","天文望远镜卫星","迪吉里杜",
      "太空种子","龙血树脂罗盘","黑曜石晶体","广域照相机","天体摄谱仪",
      "免疫回溯","大筛选","陨石坑音乐节","星锑空间望远镜","唱片","神秘学唱片机"]
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
    line=f"  {mark} {t:22s} canon={canon!r}"
    if t!=canon: line+=f"  组{len(mem)}: {[(m,cnt[m]) for m in sorted(mem,key=lambda x:-cnt[x])[:5]]}"
    print(line)
