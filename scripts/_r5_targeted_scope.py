# -*- coding: utf-8 -*-
"""R5（丙）定向补缺：只对**孤立/极薄**角色补少量同场边，规避 PPR 稀释。

用户裁决（2026-09-27）：选 (丙) —— 仅定向补相遇测试暴露的具体缺口对。

相遇测试暴露的缺口（meetability_test_20260927.json）：
  - 8 个随机组里 5 组「不可达」；56 对中仅 12 对 ≤2 跳；同场可遇 = 0
  - **176 个零度角色**（完全无任何边）：万尼亚少校、伊佐、乌佐、伊冯娜…
  - 池内零边实体 6 个：学生Ⅲ、男孩Ⅲ、记者Ⅰ、门槛旁的乞丐、阿曼达、首相

设计原则（与全量方案的差别）：
  1. **只给零度/低度角色加边**（度数 ≤ threshold），不动高枢纽 -> 不摊薄现有邻域；
  2. 只连**同 chunk 共现**的对（有逐字证据）；
  3. 每个孤立实体最多连 K 条（避免单点爆度）；
  4. 优先连向**度数低**的伙伴（帮助建立可达性，而非把一切挂到维尔汀）。

本脚本先只做**范围与稀释测算**（只读），确认规模可控后再生成提案。
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from compendium_rag import pipeline as P                     # noqa: E402
from compendium_rag.config import get_settings               # noqa: E402


def main() -> int:
    s = get_settings()
    kb = P.load_kb(s)
    g = kb.graph

    deg = Counter()
    for e in g.edges:
        deg[e.src] += 1
        deg[e.dst] += 1
    chars = {eid: e for eid, e in g.entities.items() if e.type == "角色"}
    zero = [c for c in chars if deg.get(c, 0) == 0]
    print(f"[graph] 边={len(g.edges):,} 角色={len(chars)} 零度角色={len(zero)}")

    # 共现表
    chunk2chars: dict[str, set[str]] = defaultdict(set)
    for eid in chars:
        for cid in g.entities[eid].chunk_ids:
            chunk2chars[cid].add(eid)

    # 对每个零度角色，找其出现块里的其它角色
    partner_deg = Counter()
    zero_with_partner = 0
    zero_alone = []
    for z in zero:
        partners: set[str] = set()
        for cid in g.entities[z].chunk_ids:
            partners |= chunk2chars[cid] - {z}
        if partners:
            zero_with_partner += 1
            for p in partners:
                partner_deg[deg.get(p, 0)] += 1
        else:
            zero_alone.append(z)

    print(f"[scope] 零度角色中：有共现伙伴 {zero_with_partner}；完全孤立（无可连） {len(zero_alone)}")
    if zero_alone:
        print(f"        完全孤立样例: {zero_alone[:8]}")

    # 候选边：零度角色 x 其共现伙伴，每伙伴最多 K 条
    K = 3
    cand = []
    for z in zero:
        partners = set()
        for cid in g.entities[z].chunk_ids:
            partners |= chunk2chars[cid] - {z}
        # 优先低度伙伴
        partners = sorted(partners, key=lambda p: (deg.get(p, 0), p))[:K]
        for p in partners:
            cand.append((z, p))
    print(f"\n[candidate] 每孤立实体最多连 K={K} 条 -> 候选边 {len(cand)}")

    # 稀释影响：只看**伙伴侧**度数增量（伙伴多为低度，才不摊薄）
    add = Counter()
    for z, p in cand:
        add[p] += 1
        add[z] += 1
    hub_touch = [(e, add[e], deg.get(e, 0)) for e in add if deg.get(e, 0) > 100]
    print(f"[dilution] 被触及的高度伙伴（度>100）: {len(hub_touch)} 个 -> {hub_touch[:10]}")
    worst = sorted(add.items(), key=lambda kv: -(kv[1] / max(deg.get(kv[0], 0), 1)))[:10]
    print("[dilution] 相对度数增幅最大 Top10（原度 -> +add, 倍数）:")
    for e, a in worst:
        o = deg.get(e, 0)
        print(f"   {e:22} {o:5} -> {o + a:5}  (×{(o + a) / max(o, 1):.2f})")

    # 对照：全量方案给维尔汀的增幅
    print(f"\n[对照] 全量星型方案曾使 维尔汀 度 1524 -> 5103 (×3.3)、既有邻居摊薄 ×0.548")
    print(f"[对照] 本定向方案给 维尔汀 的增量: +{add.get('维尔汀', 0)} 条")

    out = {
        "total_edges": len(g.edges),
        "zero_degree_chars": len(zero),
        "zero_with_partner": zero_with_partner,
        "zero_isolated": len(zero_alone),
        "candidate_edges": len(cand),
        "cand_pct": round(len(cand) / len(g.edges) * 100, 2),
        "hub_touched": len(hub_touch),
        "top_relative_growth": [{"eid": e, "deg": deg.get(e, 0), "add": a} for e, a in worst],
        "vilting_add": add.get("维尔汀", 0),
    }
    (ROOT / "data/compendium_rag/reports/_r5_targeted_scope.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n-> reports/_r5_targeted_scope.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
