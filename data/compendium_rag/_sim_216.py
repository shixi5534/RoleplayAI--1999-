# -*- coding: utf-8 -*-
"""batch216 落点预演 + 安娜/观众Ⅲ 身份核查。"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent / "src"))
from compendium_rag.graph_store import _merge_candidates, canonical_pick, GraphStore  # noqa: E402

g = GraphStore.load(ROOT / "graph.json")
print("=== 既有实体 ===")
for n in ["安娜", "观众Ⅲ", "练习室", "邀请函", "行李箱", "黑雾", "魔精", "莱伊"]:
    e = g.entities.get(n)
    print(f"  {n:10s} resolve={g.resolve(n)!r:12s} "
          + (f"{e.type:4s} m={e.mentions} desc={e.desc!r}" if e else "[不在图]"))

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
    "瓦尔普吉斯", "西欧罗斯", "莱伊", "传声花", "丽娜婆婆", "威廉叔叔",
    "康蒂婶婶", "小玛丽", "老汉斯", "裁判组成员Ⅰ", "裁判组成员Ⅱ",
    "志愿者Ⅰ", "赛场观众Ⅰ", "赛场观众Ⅱ", "赛场观众Ⅳ", "赛场观众Ⅴ",
    "参赛选手Ⅰ", "参赛选手Ⅱ", "广播声", "第五准备区", "证件补办处",
    "伦敦分部", "应急管理局", "安保局", "应急指南", "奖牌", "门票",
    "太阳神", "雾中爵士", "冥府", "文件袋", "煤灰", "2401号选手",
    "2402号选手", "2406号选手", "练习室", "观众席", "运动会场",
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
for t in CAND:
    root = dsu.find(t)
    mem = sorted(groups[root])
    canon = canonical_pick(mem, cnt)
    mark = "✅" if canon == t else "❌"
    line = f"  {mark} {t:20s} canon={canon!r}"
    if t != canon:
        line += f"  组{len(mem)}: {[(m, cnt[m]) for m in sorted(mem, key=lambda x: -cnt[x])[:5]]}"
    print(line)
