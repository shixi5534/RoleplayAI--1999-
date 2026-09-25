# -*- coding: utf-8 -*-
"""剧情层「真缺口」题的通道归因诊断（B3 调优的前置）。

目的：区分两类失败——
    ① 召回失败：证据块**从未进入任何通道的候选**（种子/配额问题）
    ② 融合失败：证据块**进了候选池但没进 final**（排序/融合问题）
两者对策完全不同：前者要动种子/配额，后者要动融合权重。

用法：
    ROLEPLAY_PLOT_TRACE_ENABLED=true .venv/Scripts/python.exe -X utf8 \
        scripts/diag_plot_channels.py --testset clean --limit 0
产出：
    data/knowledge/_audit/diag_channels.json
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from roleplay.config import get_settings  # noqa: E402
from roleplay.core.knowledge.factory import build_plot_registry  # noqa: E402

AUDIT = ROOT / "data" / "knowledge" / "_audit"


def evidence_in(texts: list[str], group: list[str]) -> bool:
    joined = "\n".join(texts)
    return any(kw and kw in joined for kw in group)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--testset", default="clean", choices=["clean", "old"])
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--top", type=int, default=6)
    args = ap.parse_args()

    ts_file = AUDIT / ("rag_testset_300_clean.json" if args.testset == "clean"
                       else "rag_testset_300.json")
    ts = json.loads(ts_file.read_text(encoding="utf-8"))
    ov_file = AUDIT / ("evidence_overrides_clean.json" if args.testset == "clean"
                       else "evidence_overrides.json")
    ov = json.loads(ov_file.read_text(encoding="utf-8"))["overrides"] if ov_file.is_file() else {}

    s = get_settings()
    if not getattr(s, "plot_trace_enabled", False):
        print("[warn] trace 未开启——请用 ROLEPLAY_PLOT_TRACE_ENABLED=true 运行，"
              "否则 last_trace 为 None")
    retr = build_plot_registry(s).get("wu_ming_zhe")
    if retr is None:
        print("[FAIL] 检索器加载失败")
        return 2

    rows = []
    stat = collections.Counter()
    for it in ts:
        if args.limit and len(rows) >= args.limit:
            break
        q = it["q"]
        groups = it["evidence"]
        o = ov.get(it["id"])
        keeps = set(o["keep_groups"]) if o else set(range(len(groups)))
        t0 = time.perf_counter()
        out = retr.retrieve(q, top_chunks=args.top)
        ms = (time.perf_counter() - t0) * 1000
        texts = [str(getattr(c, "text", "") or "") for c in out]
        tr = retr.last_trace
        chans = {}
        cand_has_ev = False
        if tr is not None:
            for rec in getattr(tr, "channels", []):
                chans[rec.channel] = {
                    "executed": rec.executed,
                    "hit_count": int(getattr(rec, "hit_count", 0) or 0),
                    "kept_in_final": int(getattr(rec, "kept_in_final", 0) or 0),
                    "skip": str(getattr(rec, "skip_reason", "") or ""),
                }
        # 主组是否覆盖（final 文本层）
        main_covered = all(evidence_in(texts, groups[g]) for g in sorted(keeps))
        missing = [g for g in sorted(keeps) if not evidence_in(texts, groups[g])]
        if not missing:
            continue  # 只看缺口题
        # 有任何通道命中候选吗
        any_hit = any(v["hit_count"] > 0 for v in chans.values())
        seeds_total = int(getattr(tr, "seeds_total", 0) or 0) if tr else -1
        kind = "召回失败（无候选）" if not any_hit else "融合失败（有候选未进final）"
        stat[kind] += 1
        stat[f"seeds={seeds_total}"] += 1
        rows.append({
            "id": it["id"], "q": q, "keeps": sorted(keeps), "missing": missing,
            "kind": kind, "seeds_total": seeds_total,
            "channels": chans, "n_final": len(out), "ms": round(ms, 1),
            "final_head": texts[0][:60] if texts else "",
        })

    out_path = AUDIT / "diag_channels.json"
    out_path.write_text(json.dumps({"cases": rows, "stat": dict(stat)},
                                   ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[diag] 缺口题 {len(rows)} 道")
    print("[diag] 归类:", {k: v for k, v in stat.items() if not k.startswith("seeds=")})
    print("[diag] 种子数分布:", {k: v for k, v in stat.items() if k.startswith("seeds=")})
    print(f"[diag] → {out_path.relative_to(ROOT)}")
    print()
    for r in rows[:12]:
        hits = {k: v["hit_count"] for k, v in r["channels"].items() if v["hit_count"]}
        print(f"  {r['id']}｜缺{r['missing']}｜seeds={r['seeds_total']}｜{r['kind']}")
        print(f"      {r['q'][:44]}")
        print(f"      通道命中: {hits}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
