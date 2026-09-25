# -*- coding: utf-8 -*-
"""batch205 归并/别名落点实测（红线 3，rebuild 前的权威预演）。

**严格复刻** `GraphStore.build_from_extractions` 的 ② 归一 + alias_index 构造，
在「全量 cache ∪ 本批」的观测集合上跑，逐条报告：

  * 每个 name 最终是否为自己的 canonical（没被吸入他组）
  * 每个 alias 在 **alias_index** 里是否指向它的本体（这才是 `resolve()` 的依据）

关键点（第一版脚本踩到）：alias 若**从未作为 name 出现**，它不进 DSU 的 names，
`_merge_candidates` 会因 `b in dsu.p` 失败而**丢弃这条 alias 边**；
但最终 `aliases.update(...)` + `alias_index.setdefault(a, eid)` 仍会让它可解析。
所以必须照抄整个算法，而不是只看 DSU 分组。
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent / "src"))

from compendium_rag.graph_store import _merge_candidates, canonical_pick  # noqa: E402

BATCH = json.loads((ROOT / "_agent_batch205.json").read_text(encoding="utf-8"))


def load_obs():
    """复刻 obs_entities：name -> {types, aliases, descs}。"""
    obs: dict[str, dict] = {}
    for p in sorted((ROOT / "cache").rglob("*.json")):
        try:
            obj = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        raw = obj.get("raw") or {}
        for e in raw.get("entities") or []:
            if not e.get("name"):
                continue
            o = obs.setdefault(e["name"],
                               {"types": {}, "aliases": set(), "descs": {}})
            o["types"][e["type"]] = o["types"].get(e["type"], 0) + 1
            o["aliases"].update(a for a in (e.get("aliases") or []) if a)
            if e.get("desc"):
                o["descs"][e["desc"]] = o["descs"].get(e["desc"], 0) + 1
        for r in raw.get("relations") or []:
            for side in ("src", "dst"):
                if r.get(side):
                    obs.setdefault(r[side], {"types": {}, "aliases": set(),
                                             "descs": {}})
    return obs


obs = load_obs()
for blk in BATCH.values():
    for e in blk.get("entities", []):
        o = obs.setdefault(e["name"], {"types": {}, "aliases": set(), "descs": {}})
        o["types"][e["type"]] = o["types"].get(e["type"], 0) + 1
        o["aliases"].update(a for a in (e.get("aliases") or []) if a)
        if e.get("desc"):
            o["descs"][e["desc"]] = o["descs"].get(e["desc"], 0) + 1


def normalize(obs):
    """照抄 build_from_extractions 的 ②，返回 name -> canonical 的 alias_index。"""
    names = sorted(obs.keys())
    alias_edges = []
    for n, o in obs.items():
        for a in o["aliases"]:
            if a != n:
                alias_edges.append((n, a))
    dsu = _merge_candidates(names, alias_edges)

    groups: dict[str, list[str]] = {}
    for n in names:
        groups.setdefault(dsu.find(n), []).append(n)

    alias_index: dict[str, str] = {}
    canon_of: dict[str, str] = {}
    for root, members in groups.items():
        obs_count = {m: sum(obs[m]["types"].values())
                     + sum(obs[m]["descs"].values()) for m in members}
        canon = canonical_pick(members, obs_count)
        for m in members:
            alias_index[m] = canon          # ← 先按成员写
            canon_of[m] = canon
        aliases: set[str] = set()
        for m in members:
            aliases.update(obs[m]["aliases"])
        aliases.discard(canon)
        aliases -= set(members)
        for a in aliases:
            alias_index.setdefault(a, canon)  # ← 再兜底写未成名的别名
    return alias_index, canon_of, groups, names


alias_index, canon_of, groups, names = normalize(obs)
print(f"观测名 {len(obs)}｜alias_index {len(alias_index)}")

declared_names: dict[str, set] = {}
for blk in BATCH.values():
    for e in blk["entities"]:
        declared_names.setdefault(e["name"], set()).update(e["aliases"])

bad: list[str] = []
print("\n=== 本批 name 落点 ===")
for n in sorted(declared_names):
    got = alias_index.get(n)
    grp = groups.get(n, [n])
    if got != n:
        bad.append(f"name {n!r} → {got!r}（被吸入他组）")
        print(f"  ❌ {n:18s} → {got!r}")
    else:
        extra = [m for m in grp if m != n]
        tail = f"，同组 {extra}" if extra else ""
        print(f"  ✅ {n:18s} → 自己{tail}")

print("\n=== 本批 alias 落点（resolve() 依据）===")
for n in sorted(declared_names):
    for a in sorted(declared_names[n]):
        got = alias_index.get(a)
        if got != n:
            bad.append(f"alias {a!r}（声明给 {n!r}）→ {got!r}")
            print(f"  ❌ {a!r} @ {n!r} → {got!r}")
        else:
            print(f"  ✅ {a!r} @ {n!r} → {got!r}")

print()
if bad:
    print(f"✗ {len(bad)} 处问题：")
    for b in bad:
        print("   -", b)
    raise SystemExit(1)
print("✓ 全部 name/alias 的 resolve() 落点符合声明")
