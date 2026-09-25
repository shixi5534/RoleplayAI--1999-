import json, sys
from pathlib import Path
sys.path.insert(0,"src")
from compendium_rag.graph_store import _merge_candidates, canonical_pick, GraphStore
ROOT=Path("data/compendium_rag"); g=GraphStore.load(ROOT/"graph.json")
for n in ["卢卡斯","哑谜","兔毛手袋","露西","X","助理希曼","洛伦兹研究所","罗盘灼灼","非对称核素R","唱片机"]:
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
CAND=["舵手伊萨姆","舵手老查理","舵手乔瓦尼","通讯员","船员Ⅰ","船员Ⅱ",
      "乔纳森","佩内洛普","与会人员Ⅰ","与会人员Ⅱ","与会人员Ⅲ","与会人员Ⅳ",
      "与会人员Ⅴ","伊丽莎白女士","佩纽奶奶","塔雷克叔叔","纳塔诺爷爷",
      "游轮大厅","科算中心议事厅","电力供应室","拉普拉斯病房","新斯科舍",
      "莫阿纳","巨齿飞鳐聚集区","普列谢茨克航天基地","生物技术组",
      "巨齿飞鳐","口琴","扩音喇叭","蹦蹦跳弹力灯泡","太空种子","天体摄谱仪",
      "高速光度计","黑曜石晶体","泽兰护符","声波发生器","解压弹力球",
      "蝴蝶纹样信封","挑衅信","工牌","助理希曼","基金会客房"]
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
