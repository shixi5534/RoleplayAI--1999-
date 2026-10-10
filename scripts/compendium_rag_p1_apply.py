# -*- coding: utf-8 -*-
"""P1 谓语受控化**就地落盘**（默认 dry-run，零云端）。

为什么不是 ``cli rebuild``
--------------------------
对照闸门 ``compendium_rag_p1_control_rebuild.py`` 实测：用「当前 cache + n1 归一化」
重建**复现不出**冻结的 v8 图谱（4 个实体名不同、690/388 条边不同）。原因是 v8
带有审查期的人工裁决，而这些裁决只落在 graph.json、没回到 cache：

* 规范名裁决：v8 = ``兀尔德``（``传记作家兀尔德`` 降为别名）、``玛尔塔``、
  ``店主米拉``、``玩具盒``；纯重建会挑回描述性伪实体名
  （``传记作家兀尔德`` / ``伦敦煤烟污染勘察与清除大使`` / ``旅行队的别斯米尔`` /
  ``暴雨小组组长乌尔里希``）；
* 实体 ``desc`` 里的人工考据（灰机wiki 出处、评测集读法说明）。

所以 graph.json 才是「最原始权威记录」，rebuild 会把上述修复整体回退。
本脚本因此只改 ``edges[*].relation``（及撞键合并），**entities 逐字节不动**。

安全闸
------
1. 输入图 SHA 必须等于 ``--expect-sha``（默认 v8 冻结锚点），漂移即中止；
2. ``--apply`` 前必须存在与输入同 SHA 的备份文件；
3. 落盘前断言 entities 序列化结果与输入完全一致；
4. 断言产出指纹等于预登记值（``baseline_v9_plan.json`` 的 n2 指纹）。

用法::

    PYTHONHASHSEED=0 .venv/Scripts/python.exe -X utf8 scripts/compendium_rag_p1_apply.py
    ... --apply
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from compendium_rag import pipeline as P                       # noqa: E402
from compendium_rag.config import get_settings                 # noqa: E402
from compendium_rag.extract import (NORMALIZER_VERSION,         # noqa: E402
                                    PROMPT_VERSION)
from compendium_rag.graph_store import Edge, GraphStore, fingerprint_of  # noqa: E402
from compendium_rag.corpus import corpus_fingerprint            # noqa: E402
from compendium_rag.relation_norm import default_tables, map_relation    # noqa: E402
from compendium_rag.relation_vocab import CANONICAL_SET         # noqa: E402

GRAPH = ROOT / "data" / "compendium_rag" / "graph.json"
BACKUP = ROOT / "data" / "compendium_rag" / "backups" / "graph.json.v8_frozen_026b41699f021db2"
REPORT = ROOT / "data" / "compendium_rag" / "reports" / "p1_apply.json"
BASELINE = ROOT / "data" / "compendium_rag" / "reports" / "baseline_v9_plan.json"
V8_SHA16 = "026b41699f021db2"


def _sha16(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def _isolated(entities: dict, edges: list[Edge]) -> dict:
    """孤立率。不用 ``GraphStore.stats()``：它的 multi_edge_entities 是
    O(实体×边) 全扫，7033×3 万 ≈ 2 亿次比较。"""
    touched = {e.src for e in edges} | {e.dst for e in edges}
    iso = sum(1 for eid in entities if eid not in touched)
    n = len(entities) or 1
    return {"entities": len(entities), "isolated": iso,
            "isolated_ratio": round(iso / n, 6)}


def _dist(edges: list[Edge]) -> dict:
    rel = Counter(e.relation for e in edges)
    n = len(edges) or 1
    canon = sum(v for k, v in rel.items() if k in CANONICAL_SET)
    common = rel.most_common()
    singles = sum(1 for _, k in common if k == 1)
    return {"edges": len(edges), "distinct_predicates": len(rel),
            "strict_canonical_rate": round(canon / n, 6),
            "singleton_predicates": singles,
            "singleton_rate": round(singles / len(rel), 6) if rel else None,
            "top10_edge_coverage": round(sum(k for _, k in common[:10]) / n, 6),
            "top10": [{"relation": r, "edges": k} for r, k in common[:10]]}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="P1 谓语受控化就地落盘（只改 edges.relation）")
    ap.add_argument("--graph", default=str(GRAPH))
    ap.add_argument("--expect-sha", default=V8_SHA16)
    ap.add_argument("--apply", action="store_true", help="落盘（默认 dry-run）")
    args = ap.parse_args(argv)

    gpath = Path(args.graph)
    sha = _sha16(gpath)
    if sha != args.expect_sha:
        print(f"[FATAL] 图谱 SHA 漂移：{sha} != {args.expect_sha}，中止。")
        return 2

    s = get_settings()
    tables = default_tables()
    g = GraphStore.load(gpath)
    fp_v8 = g.fingerprint
    norm_v8 = g.normalizer
    edges_v8 = list(g.edges)
    entities_before = json.dumps([e.to_dict() for e in g.entities.values()],
                                 ensure_ascii=False)

    fp_n2 = fingerprint_of(corpus_fingerprint(P.load_chapters(s)), s.llm_model,
                           PROMPT_VERSION, s.chunk_chars, NORMALIZER_VERSION)
    prereg = ""
    if BASELINE.exists():
        base = json.loads(BASELINE.read_text(encoding="utf-8"))
        txt = str(base.get("preregistered_gate_for_p1")
                  or (base.get("p0_changes_applied") or {})
                  .get("preregistered_gate_for_p1", ""))
        hit = re.search(r"\b[0-9a-f]{16}\b", txt)
        prereg = hit.group(0) if hit else ""

    merged: dict[tuple[str, str, str], Edge] = {}
    codes: Counter = Counter()
    dropped: Counter = Counter()
    blocked: Counter = Counter()
    rewritten: Counter = Counter()
    n_merged = 0
    for e in g.edges:
        m = map_relation(e.src, e.relation, e.dst, tables=tables)
        codes[m.code] += 1
        if not m.relation:
            dropped[m.code] += 1
            continue
        if m.src == m.dst:
            dropped["drop:self_loop"] += 1
            continue
        if m.code == "kept:direction_blocked":
            blocked[(e.relation, m.intended)] += 1
        elif m.relation != e.relation:
            rewritten[(e.relation, m.relation)] += 1
        key = (m.src, m.relation, m.dst)
        hit = merged.get(key)
        if hit is None:
            merged[key] = Edge(src=m.src, dst=m.dst, relation=m.relation,
                               confidence=e.confidence, evidence=e.evidence,
                               chunk_ids=list(e.chunk_ids), count=e.count)
            continue
        n_merged += 1
        hit.count += e.count
        hit.confidence = max(hit.confidence, e.confidence)
        if not hit.evidence and e.evidence:
            hit.evidence = e.evidence
        for cid in e.chunk_ids:
            if cid not in hit.chunk_ids:
                hit.chunk_ids.append(cid)

    new_edges = list(merged.values())
    g.edges = new_edges
    g._edge_index = merged
    g.fingerprint = fp_n2
    g.normalizer = NORMALIZER_VERSION

    entities_after = json.dumps([e.to_dict() for e in g.entities.values()],
                                ensure_ascii=False)
    entities_untouched = entities_before == entities_after

    rep = {
        "schema": "compendium_rag.p1_apply/v1",
        "mode": "apply" if args.apply else "dry-run",
        "input_graph": {"path": str(gpath), "sha256_16": sha,
                        "fingerprint": fp_v8, "normalizer": norm_v8},
        "normalizer_version": NORMALIZER_VERSION,
        "tables": {"overrides": len(tables.overrides), "watch": len(tables.watch),
                   "inverse_pairs": len(tables.inverse_pairs),
                   "swap": tables.policy.swap,
                   "same_direction": sorted(tables.policy.same_direction)},
        "before": _dist(edges_v8),
        "after": _dist(new_edges),
        "isolated_before": _isolated(g.entities, edges_v8),
        "codes": dict(codes.most_common()),
        "dropped": dict(dropped.most_common()),
        "edges_merged": n_merged,
        "direction_blocked": [{"raw": a, "canonical": b, "edges": n}
                              for (a, b), n in blocked.most_common()],
        "top_rewritten": [{"raw": a, "canonical": b, "edges": n}
                          for (a, b), n in rewritten.most_common(40)],
        "n_rewritten_predicates": len(rewritten),
        "gates": {
            "input_sha_matches_anchor": sha == args.expect_sha,
            "entities_untouched": entities_untouched,
            "fingerprint_n2": fp_n2,
            "fingerprint_preregistered": prereg,
            "fingerprint_matches_preregistration": bool(prereg) and fp_n2 == prereg,
            "backup_present_and_identical": BACKUP.exists() and _sha16(BACKUP) == sha,
        },
        "isolated_after": _isolated(g.entities, new_edges),
    }
    hard_ok = (rep["gates"]["entities_untouched"]
               and rep["gates"]["backup_present_and_identical"]
               and rep["gates"]["fingerprint_matches_preregistration"])
    rep["gates"]["all_ok"] = hard_ok

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: rep[k] for k in ("mode", "before", "after", "codes",
                                          "dropped", "edges_merged",
                                          "direction_blocked", "gates")},
                     ensure_ascii=False, indent=2))
    print(f"报告 → {REPORT}")

    if not args.apply:
        print("[DRY-RUN] 未写盘。")
        return 0 if hard_ok else 1
    if not hard_ok:
        print("[FATAL] 硬闸未过，拒绝落盘。")
        return 1
    g.save(gpath)
    print(f"[APPLY] 已写 {gpath} → sha256_16 {_sha16(gpath)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
