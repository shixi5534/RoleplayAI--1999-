# -*- coding: utf-8 -*-
"""batch217 落点预演 + 既有实体核查。"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent / "src"))
from compendium_rag.graph_store import _merge_candidates, canonical_pick, GraphStore  # noqa: E402

g = GraphStore.load(ROOT / "graph.json")
print("=== 既有实体 ===")
for n in ["图图石子", "卡穆塔", "托阿", "塞洛尼", "乌尔里希", "努库泰澳岛",
          "努库泰澳人Ⅰ", "努库泰澳人Ⅱ", "麦黎", "以提提", "米缇", "维布那",
          "拉普拉斯", "科算中心", "拉普拉斯科算中心", "磁流体", "船员",
          "自由海风号", "芭卡洛儿", "月相招潮蟹", "招潮蟹", "传单", "星锑"]:
    e = g.entities.get(n)
    if e:
        print(f"  {n:14s} resolve={g.resolve(n)!r:14s} {e.type:4s} m={e.mentions:3d} "
              f"aliases={e.aliases[:3]} desc={e.desc!r}")
    else:
        print(f"  {n:14s} resolve={g.resolve(n)!r:14s} [不在图]")

obs: dict[str, dict] = {}
for p in sorted((ROOT / "cache").rglob("*.json")):
    try:
        o = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        continue
    raw = o.get("raw") or {}
    for e in raw.get("entities") or []:
        n = e.get("name")
        if not n:
            continue
        d = obs.setdefault(n, {"types": {}, "aliases": set(), "descs": {}})
        d["types"][e.get("type")] = d["types"].get(e.get("type"), 0) + 1
        if e.get("desc"):
            d["descs"][e["desc"]] = d["descs"].get(e["desc"], 0) + 1
        for a in e.get("aliases") or []:
            if a:
                d["aliases"].add(a)
    for r in raw.get("relations") or []:
        for s in ("src", "dst"):
            if r.get(s):
                obs.setdefault(r[s], {"types": {}, "aliases": set(), "descs": {}})

CAND = [
    "汉米西", "宣传船员", "圆滑的船员", "忧心的船员", "街头商人",
    "街头艺术家", "努库泰澳", "努库泰澳岛", "马拉尼亚环礁", "雪梨港",
    "悉尼港", "丰收满满号", "军方", "暴雨专项研究小组",
    "独木舟环岛比赛", "象形贝壳", "啪唧匣子", "无影无踪雾",
    "鬼脸螃蟹", "风暴猫", "提克蜗", "鱼雷试验场", "白皮书", "船票",
    "人工泪滴", "计算机", "数独", "拉普拉斯命名法", "哈雷彗星",
    "柯伊伯带阋神星", "克赖斯特彻奇",
]
for n in CAND:
    d = obs.setdefault(n, {"types": {}, "aliases": set(), "descs": {}})
    d["types"]["角色"] = d["types"].get("角色", 0) + 1

names = sorted(obs)
ae = []
for n, o in obs.items():
    for a in o["aliases"]:
        if a != n:
            ae.append((n, a))
dsu = _merge_candidates(names, ae)
groups: dict[str, list[str]] = {}
for n in names:
    groups.setdefault(dsu.find(n), []).append(n)
cnt = {n: sum(obs[n]["types"].values()) + sum(obs[n]["descs"].values())
       for n in names}

print("\n=== 注入后落点 ===")
for t in CAND + ["乌尔里希", "拉普拉斯", "科算中心"]:
    root = dsu.find(t)
    mem = sorted(groups[root])
    canon = canonical_pick(mem, cnt)
    mark = "✅" if canon == t else "❌"
    line = f"  {mark} {t:22s} canon={canon!r}"
    if t != canon:
        line += f"  组{len(mem)}: {[(m, cnt[m]) for m in sorted(mem, key=lambda x: -cnt[x])[:5]]}"
    print(line)
