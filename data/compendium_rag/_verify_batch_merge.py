# -*- coding: utf-8 -*-
"""通用归并/别名落点实测（红线 3，rebuild 前的权威预演）。

用法：`python _verify_batch_merge.py _agent_batch205.json [更多批次...]`

严格复刻 `GraphStore.build_from_extractions` 的 ② 归一 + alias_index 构造，
在「全量 cache ∪ 指定批次」的观测集合上跑，逐条报告：
  * 每个 name 是否为自己的 canonical（没被吸入他组）
  * 每个 alias 在 alias_index 里是否指向它的本体（`resolve()` 的依据）

踩坑记录：alias 若从未作为 name 出现，不会进 DSU 的 names，
`_merge_candidates` 会因 `b in dsu.p` 失败而丢弃该边；但最终
`aliases.update(...)` + `alias_index.setdefault(a, eid)` 仍让它可解析。
所以必须照抄整个算法，而不是只看 DSU 分组。
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent / "src"))

from compendium_rag.graph_store import _merge_candidates, canonical_pick  # noqa: E402


def load_obs():
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


def inject(obs, batch):
    for blk in batch.values():
        for e in blk.get("entities", []):
            o = obs.setdefault(e["name"], {"types": {}, "aliases": set(),
                                           "descs": {}})
            o["types"][e["type"]] = o["types"].get(e["type"], 0) + 1
            o["aliases"].update(a for a in (e.get("aliases") or []) if a)
            if e.get("desc"):
                o["descs"][e["desc"]] = o["descs"].get(e["desc"], 0) + 1


def normalize(obs):
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
    for root, members in groups.items():
        obs_count = {m: sum(obs[m]["types"].values())
                     + sum(obs[m]["descs"].values()) for m in members}
        canon = canonical_pick(members, obs_count)
        for m in members:
            alias_index[m] = canon
        aliases: set[str] = set()
        for m in members:
            aliases.update(obs[m]["aliases"])
        aliases.discard(canon)
        aliases -= set(members)
        for a in aliases:
            alias_index.setdefault(a, canon)
    return alias_index, groups


# 有意为之的归并：声明的 name 并非 canonical，但它**确实**是同一个对象，
# 收敛到既有 canonical 才是正解（§4.1：关系端点逐字用原文写法，规范名另算）。
# 白名单外的任何"被吸入他组"都视为缺陷。
EXPECTED_MERGE = {
    "Z女士": "Z",      # Z女士 = 既有 Z（张之之），模拟实测 count Z=142 占优
}


def main(paths: list[str]) -> int:
    obs = load_obs()
    labels = []
    for p in paths:
        f = ROOT / p
        labels.append(f.name)
        inject(obs, json.loads(f.read_text(encoding="utf-8")))
    alias_index, groups = normalize(obs)
    print(f"批次 {'+'.join(labels)}｜观测名 {len(obs)}｜alias_index {len(alias_index)}")

    declared: dict[str, set] = {}
    for p in paths:
        for blk in json.loads((ROOT / p).read_text(encoding="utf-8")).values():
            for e in blk["entities"]:
                declared.setdefault(e["name"], set()).update(e["aliases"])

    bad: list[str] = []
    print("\n=== name 落点 ===")
    for n in sorted(declared):
        got = alias_index.get(n)
        grp = groups.get(n, [n])
        if got != n:
            if EXPECTED_MERGE.get(n) == got:
                print(f"  ➖ {n:18s} → {got!r}（有意归并，已白名单）")
                continue
            bad.append(f"name {n!r} → {got!r}")
            print(f"  ❌ {n:18s} → {got!r}")
        else:
            extra = [m for m in grp if m != n]
            print(f"  ✅ {n:18s} → 自己" + (f"，同组 {extra}" if extra else ""))

    print("\n=== alias 落点（resolve() 依据）===")
    for n in sorted(declared):
        for a in sorted(declared[n]):
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
        return 1
    print("✓ 全部 name/alias 的 resolve() 落点符合声明")
    return 0


if __name__ == "__main__":
    args = sys.argv[1:] or ["_agent_batch205.json"]
    raise SystemExit(main(args))
