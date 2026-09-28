# -*- coding: utf-8 -*-
"""用 100 道评测题测试剧情图谱检索层。

指标：
  hit@1 / hit@3 / hit@5   —— 返回块里是否包含该题的 ground-truth 块
  via_graph 占比          —— 是否走图谱路径返回
  entity_hit 占比         —— 返回边中是否出现题面主体/客体实体
  latencies               —— 平均 / P95 / 最大延迟

用法（项目根目录）：
  .venv/Scripts/python.exe -X utf8 scripts/run_eval_questions.py
产物：docs/plot-graph-rag/acceptance/剧情图谱100题评测报告.md + data/knowledge/_audit/eval_result.json
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
from roleplay.core.knowledge.plot_graph import PlotGraphRegistry  # noqa: E402

CHARACTER = "wu_ming_zhe"
AUDIT = ROOT / "data" / "knowledge" / "_audit"
QFILE = AUDIT / "eval_questions.json"
OUT_MD = ROOT / "docs" / "剧情图谱100题评测报告.md"
OUT_JSON = AUDIT / "eval_result.json"

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--ks", type=str, default="", help="多档对比，如 5,10,20")
    args = ap.parse_args()
    ks = [int(x) for x in args.ks.split(",") if x.strip()] or [args.top]
    out_json = AUDIT / (f"eval_result_top{ks[0]}.json" if len(ks) == 1 else "eval_result_multi.json")

    payload = json.loads(QFILE.read_text(encoding="utf-8"))
    items = payload["items"]

    settings = get_settings()
    registry = PlotGraphRegistry(
        corpus_dir=settings.plot_corpus_dir,
        graph_dir=settings.plot_graph_dir,
        alias_dir=settings.plot_lore_dir,
        include_weak=bool(settings.plot_include_weak),
    )
    retr = registry.get(CHARACTER)
    if retr is None:
        print("[FATAL] 检索器加载失败")
        return 1

    text2hash: dict[str, str] = {}
    for ch in retr.corpus.chunks:
        text2hash.setdefault(ch.text, ch.hash)

    # 图谱实体 id → 该实体全部名称（正名 + 别名），用于别名感知的关系判定
    graph = json.loads(
        (ROOT / "data" / "knowledge" / f"plot_graph_{CHARACTER}.json").read_text(encoding="utf-8")
    )
    id_names: dict[str, list[str]] = {}
    for eid, v in graph["entities"].items():
        ns = [str(v.get("name") or "")] + [str(a) for a in (v.get("aliases") or [])]
        id_names[eid] = [n.strip() for n in ns if len(n.strip()) >= 2]

    rows: list[dict] = []
    lat: list[float] = []
    for it in items:
        t0 = time.perf_counter()
        out = retr.retrieve(it["question"], top_chunks=args.top)
        ms = (time.perf_counter() - t0) * 1000
        lat.append(ms)

        got = [text2hash.get(c.text, "") for c in out]
        gt = set(it["gt_hashes"])
        r1 = bool(gt & set(got[:1]))
        r3 = bool(gt & set(got[:3]))
        r5 = bool(gt & set(got))

        # 语义命中：返回块的正文里同时出现题面主体与客体（关系题）/ 出现主体（实体题）。
        # 同一段剧情在语料中有多块提及，严格按 evidence hash 判定会低估召回。
        subj = (it.get("subject") or "").strip().lower()
        obj = (it.get("object") or "").strip().lower()
        # 只有关系题要求返回正文同时含主体与客体；实体题/别名题只需含主体。
        need_obj = (it.get("kind") == "relation") and bool(obj)

        def _txt(c) -> str:
            return (c.text or "").lower()
        sem1 = sem5 = False
        for i, c in enumerate(out):
            t = _txt(c)
            ok_c = bool(subj) and subj in t and (not need_obj or obj in t)
            if ok_c:
                sem5 = True
                if i == 0:
                    sem1 = True
        via = any(c.metadata.get("via") == "plot_graph" for c in out)
        names = {str(it.get("subject") or ""), str(it.get("object") or "")}
        names.discard("")
        ent_hit = False
        pair_hit = False  # 返回的某条图谱边同时覆盖题面主体与客体
        for c in out:
            edge = str(c.metadata.get("edge") or "")
            if not edge:
                continue
            if any(n and n in edge for n in names):
                ent_hit = True
            if it.get("object") and it.get("subject") \
                    and it["subject"] in edge and it["object"] in edge:
                pair_hit = True
        if it.get("kind") != "relation":
            pair_hit = ent_hit

        # 别名感知关系命中：返回边同时覆盖 src 侧任一名称与 dst 侧任一名称
        alias_pair = False
        if it.get("kind") == "relation" and it.get("src_id") and it.get("dst_id"):
            src_names = [n.lower() for n in id_names.get(it["src_id"], [])]
            dst_names = [n.lower() for n in id_names.get(it["dst_id"], [])]
            for c in out:
                edge = str(c.metadata.get("edge") or "").lower()
                if edge and any(n in edge for n in src_names) \
                        and any(n in edge for n in dst_names):
                    alias_pair = True
                    break
        else:
            alias_pair = pair_hit
        rows.append({
            "id": it["id"], "kind": it["kind"], "q": it["question"],
            "hit1": r1, "hit3": r3, "hit5": r5,
            "sem1": sem1, "sem5": sem5,
            "via_graph": via, "entity_hit": ent_hit, "pair_hit": pair_hit,
            "alias_pair": alias_pair,
            "ms": round(ms, 1), "n_gt": len(gt),
        })

    def rate(key: str, sub: list[dict] | None = None) -> float:
        s = sub if sub is not None else rows
        return (sum(1 for r in s if r[key]) / len(s)) if s else 0.0

    kinds = sorted({r["kind"] for r in rows})
    lat_sorted = sorted(lat)
    summary = {
        "n": len(rows),
        "hit@1": round(rate("hit1"), 4),
        "hit@3": round(rate("hit3"), 4),
        "hit@5": round(rate("hit5"), 4),
        "sem@1": round(rate("sem1"), 4),
        "sem@5": round(rate("sem5"), 4),
        "via_graph": round(rate("via_graph"), 4),
        "entity_hit": round(rate("entity_hit"), 4),
        "pair_hit": round(rate("pair_hit"), 4),
        "alias_pair": round(rate("alias_pair"), 4),
        "lat_avg": round(statistics.mean(lat), 1),
        "lat_p95": round(lat_sorted[max(0, int(len(lat_sorted) * 0.95) - 1)], 1),
        "lat_max": round(max(lat), 1),
        "by_kind": {
            k: {
                "n": sum(1 for r in rows if r["kind"] == k),
                "hit@5": round(rate("hit5", [r for r in rows if r["kind"] == k]), 4),
                "sem@5": round(rate("sem5", [r for r in rows if r["kind"] == k]), 4),
                "pair": round(rate("pair_hit", [r for r in rows if r["kind"] == k]), 4),
                "alias_pair": round(rate("alias_pair", [r for r in rows if r["kind"] == k]), 4),
            }
            for k in kinds
        },
    }

    out_json.write_text(
        json.dumps({"summary": summary, "rows": rows}, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )

    lines = [
        "# 剧情图谱 100 题评测报告",
        "",
        f"- 执行时间：{time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"- 题量：{summary['n']}（关系 {summary['by_kind'].get('relation', {}).get('n', 0)}"
        f" / 实体 {summary['by_kind'].get('entity', {}).get('n', 0)}"
        f" / 别名 {summary['by_kind'].get('alias', {}).get('n', 0)}）",
        f"- top-k：{args.top}",
        "",
        "## 总体指标",
        "",
        "| 指标 | 结果 |",
        "|---|---|",
        f"| hit@1（严格：命中 evidence 块） | {summary['hit@1']:.1%} |",
        f"| hit@3（严格） | {summary['hit@3']:.1%} |",
        f"| hit@5（严格） | {summary['hit@5']:.1%} |",
        f"| **sem@1（语义：正文含主体/客体）** | **{summary['sem@1']:.1%}** |",
        f"| **sem@5（语义）** | **{summary['sem@5']:.1%}** |",
        f"| **pair_hit（返回边覆盖主客体）** | **{summary['pair_hit']:.1%}** |",
        f"| **alias_pair（别名感知，关系题）** | **{summary['alias_pair']:.1%}** |",
        f"| 走图谱路径占比 | {summary['via_graph']:.1%} |",
        f"| 返回边含目标实体 | {summary['entity_hit']:.1%} |",
        f"| 平均延迟 | {summary['lat_avg']} ms |",
        f"| P95 延迟 | {summary['lat_p95']} ms |",
        f"| 最大延迟 | {summary['lat_max']} ms |",
        "",
        "> 严格判定要求返回块恰好是该题的 evidence 块；语义判定只要返回块正文同时含"
        "题面主体与客体即可。同一段剧情在 9021 块语料中有多块提及，严格判定会低估召回。",
        "",
        "## 分题型",
        "",
        "| 题型 | 题数 | hit@5（严格） | sem@5（语义） | pair_hit | alias_pair |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for k in kinds:
        v = summary["by_kind"][k]
        lines.append(f"| {k} | {v['n']} | {v['hit@5']:.1%} | {v['sem@5']:.1%} "
                     f"| {v['pair']:.1%} | {v['alias_pair']:.1%} |")

    misses = [r for r in rows if not (r["alias_pair"] or r["hit5"])]
    lines += ["", f"## 未命中样例（{len(misses)} 题）", ""]
    for r in misses[:20]:
        lines.append(f"- `{r['id']}` {r['q']}（gt {r['n_gt']} 块）")
    if len(misses) > 20:
        lines.append(f"- …其余 {len(misses) - 20} 题见 eval_result.json")

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"[eval] {summary['n']} 题 | 严格 hit@1 {summary['hit@1']:.1%} "
          f"hit@3 {summary['hit@3']:.1%} hit@5 {summary['hit@5']:.1%} | "
          f"语义 sem@1 {summary['sem@1']:.1%} sem@5 {summary['sem@5']:.1%} | "
          f"via_graph {summary['via_graph']:.1%} | 平均 {summary['lat_avg']}ms")
    print(f"[eval] 报告 → {OUT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
