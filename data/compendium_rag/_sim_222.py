import json, sys
from pathlib import Path
sys.path.insert(0,"src")
from compendium_rag.graph_store import _merge_candidates, canonical_pick, GraphStore
ROOT=Path("data/compendium_rag"); g=GraphStore.load(ROOT/"graph.json")
for n in ["琼斯","通灵板","前行者","信徒","监控室","海岸","卫星定位系统","冠军琼斯"]:
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
CAND=["舵手众","琼斯先生","基蒂欧纳","小皮塔","努库泰澳信徒Ⅰ","努库泰澳信徒Ⅱ",
      "27岁俱乐部","广播室","舷窗","海岸基站","国际海事组织",
      "科算中心澳大利亚分部","毛毛虫溶剂","玻璃缸","前行者Ⅰ号卫星定位系统",
      "昏睡幻剂","思维电流","声波催化频率","超自然现象发生地","铂金通灵板",
      "幼龙舌管","火蛾脂粉","复制唱片","棕色噪音","试炼","古铜面具",
      "救生艇","备用锚","那不勒斯","二氧化硅","碳酸钙镁","氧化铝",
      "海上","游轮大厅","船长室","监控室"]
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
