# -*- coding: utf-8 -*-
"""构造**无泄题**盲测子集（strict），作为 85% 目标的诚实判据。

为什么必须剔除泄题题：
  evidence 关键词若**逐字出现在问题串里**，则该题在现有 RRF 口径下几乎必中
  （向量通道 + 词面都直接命中），会系统性**高估**系统能力。
  保留它们等于用"题目自带答案"自证。

剔除规则（保守，宁少勿滥）：
  对每题，若某**证据组**中的关键词出现在 q 中，则从该题的 evidence 中
  **移除该组**；若移除后无剩余证据组，则整题剔除。

同时输出统计，便于报告如实披露剔除了多少。
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "data/knowledge/_audit/blind_v1"


def main() -> int:
    files = [f for f in sorted(D.glob("questions_*.json"))
             if f.name not in ("questions_merged.json", "questions_clean.json",
                               "questions_strict.json")]
    strict, dropped_total, groups_dropped = [], 0, 0
    per_file = {}
    for f in files:
        d = json.loads(f.read_text(encoding="utf-8"))
        kept = 0
        for c in d.get("cases", []):
            q = c.get("q", "")
            groups = c.get("evidence") or []
            keep_groups = []
            for grp in groups:
                items = grp if isinstance(grp, (list, tuple)) else [grp]
                clean = [str(x) for x in items if x and str(x).strip() not in q]
                if clean:
                    keep_groups.append(clean)
                else:
                    groups_dropped += 1
            if keep_groups:
                cc = dict(c)
                cc["evidence"] = keep_groups
                strict.append(cc)
                kept += 1
            else:
                dropped_total += 1
        per_file[f.name] = {"total": len(d.get("cases", [])), "kept": kept}
        print(f"{f.name}: {len(d.get('cases', []))} -> 保留 {kept}")

    out = D / "questions_strict.json"
    out.write_text(json.dumps({
        "meta": {"source": "blind_v1 strict（剔除泄题组后）",
                 "n": len(strict), "per_file": per_file,
                 "groups_dropped": groups_dropped,
                 "note": "关键词出现在问题串中的证据组被移除；无剩余组则整题剔除"},
        "cases": strict}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n严格子集: {len(strict)} 题（剔除整题 {dropped_total}；移除证据组 {groups_dropped}）")
    print(f"dims: {Counter(c['dims']['type'] for c in strict)}")
    print(f"diff: {Counter(c['dims']['difficulty'] for c in strict)}")
    print(f"-> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
