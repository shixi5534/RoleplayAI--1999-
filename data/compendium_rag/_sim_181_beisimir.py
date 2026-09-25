# -*- coding: utf-8 -*-
"""只读模拟（batch181 预检）：验证 16101 主角该用哪个名字才不会并入 卡卡尼亚 组。

背景：batch46/38/60/61 的 alias 链把 别斯米尔/玛尔塔/德洛丝/兀尔德 并入了
`卡卡尼亚`。若 16101 直接声明 name="别斯米尔"，会被同一链再次吸收。
本脚本用 graph_store 的真实归并逻辑（_merge_candidates + canonical_pick）
在**全量 cache 观测**上模拟，比较候选名。

零网络、只读；不落盘。
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent / "src"))

from compendium_rag.graph_store import _merge_candidates, canonical_pick  # noqa: E402


def collect_from_cache() -> tuple[dict, list]:
    """从 cache/ 还原 obs_entities 的 (names, alias_edges)。"""
    names: set[str] = set()
    alias_edges: list[tuple[str, str]] = []
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
            names.add(n)
            for a in e.get("aliases") or []:
                if a and a != n:
                    alias_edges.append((n, a))
        for r in raw.get("relations") or []:
            for side in ("src", "dst"):
                if r.get(side):
                    names.add(r[side])
    return names, alias_edges


def simulate(candidate: str, alias: str | None, names, alias_edges) -> str:
    n2 = set(names) | {candidate}
    ae = list(alias_edges)
    if alias:
        ae.append((candidate, alias))
    dsu = _merge_candidates(sorted(n2), ae)
    groups: dict[str, list[str]] = {}
    for n in sorted(n2):
        groups.setdefault(dsu.find(n), []).append(n)
    root = dsu.find(candidate)
    members = groups[root]
    counts = {m: 1 for m in members}
    counts["卡卡尼亚"] = 205
    canon = canonical_pick(members, counts)
    print(f"\n候选 name={candidate!r} alias={alias!r}")
    print(f"  所属组 {len(members)} 个写法 → canonical = {canon!r}")
    if canon == candidate or candidate in members and len(members) == 1:
        print("  ✅ 独立（未并入他组）")
    else:
        print(f"  ❌ 被并入组，canonical 为 {canon!r}")
        print(f"     组内: {sorted(members)[:20]}")
    return canon


names, alias_edges = collect_from_cache()
print(f"全量 cache 观测：名字 {len(names)} 个，alias 边 {len(alias_edges)} 条")

# 对照组：一个已知无关的名字，应与 卡卡尼亚 无关
simulate("小叶尼塞", None, names, alias_edges)
# 关键组：裸名 别斯米尔（预期被吸收）
simulate("别斯米尔", None, names, alias_edges)
# 候选限定名
simulate("探险家别斯米尔", None, names, alias_edges)
simulate("探险家别斯米尔", "别斯米尔女士", names, alias_edges)
simulate("朔日手记的别斯米尔", None, names, alias_edges)
