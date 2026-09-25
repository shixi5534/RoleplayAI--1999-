# -*- coding: utf-8 -*-
"""lore 层检索评测（长期跟踪用）。

指标体系：
    id_hit@k  ：检索 top-k 里出现**源条目本身**（id 精确匹配）——主判定，客观
    key_hit@k ：返回块正文含该题关键实体词——辅助判定，容忍同主题的其它条目
    MRR       ：源条目首次出现的排名倒数
    latency   ：查询延迟分位

为什么要有这个小评测集：lore 层原先没有标准题集，2026-09-16 换 bge-m3 时只能靠
A/B（10 题）+ 人工看检索结果验证。为长期跟踪（换模型 / 调 top_k / 改混合权重），
补建 136 题的评测集（题源＝条目自带的「常被问到」句式）。

用法：
    .venv/Scripts/python.exe -X utf8 scripts/eval_lore_retrieval.py
    .venv/Scripts/python.exe -X utf8 scripts/eval_lore_retrieval.py --top 5 --baseline <旧报告>
    .venv/Scripts/python.exe -X utf8 scripts/eval_lore_retrieval.py --no-hybrid   # 纯向量
产出：
    data/knowledge/_audit/lore_eval_report.json
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from roleplay.config import get_settings  # noqa: E402
from roleplay.core.knowledge.embedder import build_embedder  # noqa: E402
from roleplay.core.knowledge.vector_store import KnowledgeBase  # noqa: E402

TESTSET = ROOT / "data" / "knowledge" / "_audit" / "lore_testset.json"
OUT = ROOT / "data" / "knowledge" / "_audit" / "lore_eval_report.json"
NS = ["lore_wu_ming_zhe"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--baseline", default="", help="基线报告路径，做 diff")
    ap.add_argument("--no-hybrid", action="store_true", help="关闭混合检索（纯向量）")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    payload = json.loads(TESTSET.read_text(encoding="utf-8"))
    cases = payload["cases"]
    s = get_settings()
    emb = build_embedder(s)
    kb = KnowledgeBase(embedder=emb, persist_dir=s.knowledge_dir)
    hybrid = not args.no_hybrid
    print(f"[eval] 题量 {len(cases)}｜top={args.top}｜hybrid={hybrid}"
          f"｜模型 {emb.name}({emb.dim})")

    rows: list[dict] = []
    lat: list[float] = []
    for c in cases:
        t0 = time.perf_counter()
        out = kb.search(c["q"], top_k=args.top, namespaces=NS,
                        hybrid=hybrid, hybrid_alpha=0.45)
        ms = (time.perf_counter() - t0) * 1000
        lat.append(ms)
        texts = [" ".join(str(getattr(x, "text", "") or "").split()) for x in out]
        keys = c.get("src_keys") or []
        fp = str(c.get("src_fp") or "")

        def hit_id(k: int) -> bool:
            """是否召回**源条目本身**（内容指纹命中；RetrievedChunk 无 id 字段）。"""
            return bool(fp) and any(fp in t for t in texts[:k])

        def hit_key(k: int) -> bool:
            if not keys:
                return False
            joined = " ".join(texts[:k])
            return any(key in joined for key in keys[:1])  # 首关键词命中即算

        rr = 0.0
        for i, t in enumerate(texts, 1):
            if fp and fp in t:
                rr = 1.0 / i
                break
        rows.append({
            "q": c["q"], "src_id": c["src_id"], "src_keys": keys,
            "id_hit1": hit_id(1), "id_hit3": hit_id(3), "id_hit5": hit_id(5),
            "key_hit5": hit_key(5), "rr": round(rr, 4), "ms": round(ms, 1),
            "top1_text": texts[0][:60] if texts else "",
        })

    n = len(rows)

    def rate(k: str) -> float:
        return sum(1 for r in rows if r[k]) / n

    lat_sorted = sorted(lat)
    summary = {
        "cases": n, "top": args.top, "hybrid": hybrid, "model": emb.name,
        "id_hit@1": round(rate("id_hit1"), 4),
        "id_hit@3": round(rate("id_hit3"), 4),
        "id_hit@5": round(rate("id_hit5"), 4),
        "key_hit@5": round(rate("key_hit5"), 4),
        "mrr": round(statistics.mean([r["rr"] for r in rows]), 4),
        "latency_p50_ms": round(lat_sorted[len(lat_sorted) // 2], 1),
        "latency_p95_ms": round(lat_sorted[max(0, int(len(lat_sorted) * 0.95) - 1)], 1),
    }
    OUT.write_text(json.dumps({"summary": summary, "cases": rows},
                              ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"  id_hit@1 {summary['id_hit@1']:.1%}｜id_hit@3 {summary['id_hit@3']:.1%}"
          f"｜id_hit@5 {summary['id_hit@5']:.1%}")
    print(f"  key_hit@5 {summary['key_hit@5']:.1%}｜MRR {summary['mrr']:.3f}"
          f"｜延迟 p50 {summary['latency_p50_ms']}ms / p95 {summary['latency_p95_ms']}ms")
    print(f"[save] {OUT.relative_to(ROOT)}")

    if args.baseline and Path(args.baseline).is_file():
        b = json.loads(Path(args.baseline).read_text(encoding="utf-8"))["summary"]
        print("\n==== 基线对比 ====")
        for k in ("id_hit@1", "id_hit@3", "id_hit@5", "key_hit@5", "mrr"):
            if k in b:
                d = summary[k] - b[k]
                print(f"  {k:<12} {b[k]:.4f} → {summary[k]:.4f}  {d:+.4f}"
                      f"  {'提升' if d > 0.0005 else ('回退' if d < -0.0005 else '持平')}")

    if not args.quiet:
        misses = [r for r in rows if not r["id_hit5"]]
        print(f"\n=== 未命中源条目的题（{len(misses)}/{n}）===")
        for r in misses[:10]:
            print(f"  {r['q'][:30]:<32} keys={r['src_keys']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
