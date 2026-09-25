# -*- coding: utf-8 -*-
"""只读模拟（batch205 预检）：在全量 cache 观测上模拟 graph_store 的真实归并，
判定 21101 的候选名落点，避免"新建后被吸入他组"。

严格复刻 `GraphStore.build_from_extractions` 的 ② 归一：
  obs_entities[name] = {types, aliases, descs}
  alias_edges = (name, alias)
  dsu = _merge_candidates(names, alias_edges)
  obs_count[m] = sum(types) + sum(descs)
  canon = canonical_pick(members, obs_count)

零网络、只读；不落盘。
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent / "src"))

from compendium_rag.graph_store import _merge_candidates, canonical_pick  # noqa: E402

PROPOSED = json.loads((ROOT / "_agent_batch205.json").read_text(encoding="utf-8")) \
    if (ROOT / "_agent_batch205.json").exists() else {}

# 候选新名（若 _agent_batch205.json 尚未生成，用这里的手工清单）
EXTRA_NAMES = [
    "凯拉", "蓝手帕", "侍应生", "穆姆", "奇索斯镇",
    "“启明会”信众Ⅰ", "“启明会”信众Ⅱ",
]


def collect():
    obs = {}
    for p in sorted((ROOT / "cache").rglob("*.json")):
        try:
            obj = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        raw = obj.get("raw") or {}
        for e in raw.get("entities") or []:
            n = e.get("name")
            if not n:
                continue
            o = obs.setdefault(n, {"types": {}, "aliases": set(), "descs": {}})
            t = e.get("type") or "概念"
            o["types"][t] = o["types"].get(t, 0) + 1
            d = e.get("desc") or ""
            if d:
                o["descs"][d] = o["descs"].get(d, 0) + 1
            for a in e.get("aliases") or []:
                if a:
                    o["aliases"].add(a)
        for r in raw.get("relations") or []:
            for side in ("src", "dst"):
                if r.get(side):
                    obs.setdefault(r[side], {"types": {}, "aliases": set(),
                                             "descs": {}})
    return obs


# 注入拟声明的批次（含 name + aliases）
def inject(obs, batch):
    for key, blk in batch.items():
        for e in blk.get("entities", []):
            n = e.get("name")
            if not n:
                continue
            o = obs.setdefault(n, {"types": {}, "aliases": set(), "descs": {}})
            t = e.get("type") or "概念"
            o["types"][t] = o["types"].get(t, 0) + 1
            d = e.get("desc") or ""
            if d:
                o["descs"][d] = o["descs"].get(d, 0) + 1
            for a in e.get("aliases") or []:
                if a:
                    o["aliases"].add(a)


obs = collect()
print(f"cache 观测名 {len(obs)} 个")
if PROPOSED:
    print(f"注入 _agent_batch205.json：{len(PROPOSED)} 块")
    inject(obs, PROPOSED)
else:
    print("（未发现 _agent_batch205.json —— 用 EXTRA_NAMES 仅做 name 侧探针）")
    for n in EXTRA_NAMES:
        obs.setdefault(n, {"types": {"角色": 1}, "aliases": set(), "descs": {}})

names = sorted(obs.keys())
alias_edges = []
for n, o in obs.items():
    for a in o["aliases"]:
        if a != n:
            alias_edges.append((n, a))
dsu = _merge_candidates(names, alias_edges)
groups = {}
for n in names:
    groups.setdefault(dsu.find(n), []).append(n)

obs_count = {n: sum(obs[n]["types"].values()) + sum(obs[n]["descs"].values())
             for n in names}

print(f"并集实体 {len(names)}｜alias 边 {len(alias_edges)}")
print("\n=== 候选名落点（模拟 canonical_pick）===")
for cand in ["凯拉", "蓝手帕", "侍应生", "穆姆", "奇索斯镇",
             "“启明会”信众Ⅰ", "“启明会”信众Ⅱ", "阿尔古斯", "数羊羔",
             "蓝手帕旅馆", "77号公路", "德克萨斯", "启明会", "司机",
             "手帕", "奇索斯"]:
    if cand not in obs:
        print(f"  {cand:14s} [未观测]")
        continue
    root = dsu.find(cand)
    members = sorted(groups[root])
    canon = canonical_pick(members, obs_count)
    if len(members) == 1:
        print(f"  ✅ {cand:14s} 独立（canonical={canon!r}, count={obs_count[cand]}）")
    else:
        flag = "✅" if canon == cand else "❌"
        print(f"  {flag} {cand:14s} 组{len(members)}个 → canonical={canon!r}"
              f"  count({cand})={obs_count[cand]}")
        if canon != cand:
            top = sorted(members, key=lambda m: -obs_count[m])[:8]
            print(f"       组内: {[(m, obs_count[m]) for m in top]}")
