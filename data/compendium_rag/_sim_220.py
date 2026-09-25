import json, sys
from pathlib import Path
sys.path.insert(0,"src")
from compendium_rag.graph_store import _merge_candidates, canonical_pick, GraphStore
ROOT=Path("data/compendium_rag"); g=GraphStore.load(ROOT/"graph.json")
for n in ["马修","重塑·门徒","克雷莫纳","怀表","面具","毒箭","甲板","扫帚","小东西"]:
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
CAND=["客人Ⅳ","客人众","马修先生","助手小姐","格拉茨","费拉拉","乌普萨拉",
      "机械室","舞台帘幕","下层甲板","游轮乐队","诺亚方舟","古铜色面具",
      "船员守则","叩门飞匙赛","面具试炼","乡愁","非对称核素R检测仪",
      "声波频率","竹制利箭","敲击锤","信号灯","抛绳","琴颈","船长室",
      "舵手伊萨姆","舵手老查理","舵手乔瓦尼","客人Ⅰ","客人Ⅱ","客人Ⅲ"]
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
