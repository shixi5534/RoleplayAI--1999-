# -*- coding: utf-8 -*-
"""图谱关系名离线归一化（一次性治理脚本，**不改变抽取逻辑、不重建图谱结构**）。

做什么：遍历 ``<graph>.json`` 的 ``edges``，只改写 ``relation`` 字段——
按 ``relation_vocab`` 的受控词表映射到 canonical 谓语；否定短语 / 超长谓语 /
含标点或拉丁字符 / 黑名单词的边直接丢弃；映射不到的边保留原名并打上
``needs_review=true`` 标记，同时导出人工审核清单。

不做什么：不动 ``entities`` / ``alias_index`` / ``anchored`` / ``fingerprint``，
不重新抽取、不重新嵌入、不改 evidence。

一个必须处理的副作用：GraphStore 的边唯一键是 ``(src, dst, relation)``，
归一化后不同谓语会撞成同一键（如「持有」「拥有」「携带」都→「持有」）。
默认 ``--merge-dupes`` 会按 GraphStore.upsert_edge 的语义合并：evidence 取并集、
confidence/importance 取 max。关掉它会留下违反唯一键约束的重复边。

用法（项目根目录执行）：
  python scripts/normalize_graph_relations.py --graph data/knowledge/plot_graph_wu_ming_zhe.json --dry-run
  python scripts/normalize_graph_relations.py --graph data/knowledge/plot_graph_wu_ming_zhe.json --apply
  python scripts/normalize_graph_relations.py --graph ... --apply --drop-unmapped
"""
from __future__ import annotations

import argparse
import collections
import json
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from roleplay.core.knowledge.relation_vocab import (  # noqa: E402
    CANONICAL_RELATIONS,
    REVIEW_SENTINEL,
    classify_relation,
    is_dropped,
)


def _dist(counter: collections.Counter) -> dict:
    """关系词频分布指标（唯一名数 / 单例数 / 单例占唯一名比 / 头部集中度）。"""
    uniq = len(counter)
    total = sum(counter.values())
    singles = sum(1 for v in counter.values() if v == 1)
    top10 = sum(v for _, v in counter.most_common(10))
    return {
        "edges": total,
        "unique_relations": uniq,
        "singletons": singles,
        "singleton_ratio_of_unique": round(singles / uniq, 4) if uniq else 0.0,
        "singleton_ratio_of_edges": round(singles / total, 4) if total else 0.0,
        "top10_share_of_edges": round(top10 / total, 4) if total else 0.0,
    }


def _edge_key(e: dict) -> tuple[str, str, str]:
    return (str(e.get("src")), str(e.get("dst")), str(e.get("relation") or "").strip())


def _merge_into(dst: dict, src: dict) -> None:
    """按 GraphStore.upsert_edge 语义合并同键边：evidence 并集 + 置信度取高。"""
    seen = {
        (str(x.get("ns")), str(x.get("doc_id")), str(x.get("hash")))
        for x in (dst.get("evidence") or [])
    }
    for ev in src.get("evidence") or []:
        k = (str(ev.get("ns")), str(ev.get("doc_id")), str(ev.get("hash")))
        if k not in seen:
            seen.add(k)
            dst.setdefault("evidence", []).append(ev)
    for field in ("confidence", "importance"):
        if field in src or field in dst:
            dst[field] = max(
                float(dst.get(field) or 0.0), float(src.get(field) or 0.0)
            )
    dst["ts"] = max(float(dst.get("ts") or 0.0), float(src.get("ts") or 0.0))


def normalize(
    graph_path: Path,
    *,
    apply: bool,
    merge_dupes: bool,
    keep_unmapped: bool,
    report_path: Path | None,
) -> dict:
    data = json.loads(graph_path.read_text(encoding="utf-8"))
    edges = data.get("edges") or []
    before = collections.Counter(str(e.get("relation") or "") for e in edges)

    reason_uniq: collections.Counter = collections.Counter()
    reason_edges: collections.Counter = collections.Counter()
    rewrites: collections.Counter = collections.Counter()  # (原名→新名) 计数
    review: collections.Counter = collections.Counter()
    dropped_samples: dict[str, list[str]] = collections.defaultdict(list)

    kept: list[dict] = []
    seen_reasons: dict[str, str] = {}
    n_dropped = 0
    for e in edges:
        raw = str(e.get("relation") or "")
        canon, reason = classify_relation(raw)
        if raw not in seen_reasons:
            seen_reasons[raw] = reason
            reason_uniq[reason] += 1
        reason_edges[reason] += 1
        if canon is None:
            if is_dropped(reason):
                n_dropped += 1
                if len(dropped_samples[reason]) < 12:
                    dropped_samples[reason].append(raw)
                continue
            # review:unmapped —— 归入「待审核」哨兵桶，原名另存，交人工审核
            review[raw] += 1
            if keep_unmapped:
                e["relation"] = REVIEW_SENTINEL
                e["relation_raw"] = raw
                e["needs_review"] = True
                kept.append(e)
            else:
                n_dropped += 1
            continue
        if canon != raw:
            rewrites[f"{raw}→{canon}"] += 1
        e["relation"] = canon
        e.pop("needs_review", None)
        e.pop("relation_raw", None)
        kept.append(e)

    # 同键合并（保持 GraphStore (src,dst,relation) 唯一键约束）
    n_merged = 0
    if merge_dupes:
        merged: dict[tuple[str, str, str], dict] = {}
        for e in kept:
            k = _edge_key(e)
            if k in merged:
                _merge_into(merged[k], e)
                n_merged += 1
            else:
                merged[k] = e
        kept = list(merged.values())

    after = collections.Counter(str(e.get("relation") or "") for e in kept)
    after_canon = collections.Counter(
        {k: v for k, v in after.items() if k != REVIEW_SENTINEL}
    )
    result = {
        "graph": str(graph_path),
        "canonical_vocab_size": len(CANONICAL_RELATIONS),
        "before": _dist(before),
        "after": _dist(after),
        "after_excluding_review_bucket": _dist(after_canon),
        "edges_dropped": n_dropped,
        "edges_merged": n_merged,
        "reason_by_unique_relation": dict(reason_uniq.most_common()),
        "reason_by_edge": dict(reason_edges.most_common()),
        "needs_review_unique": len(review),
        "needs_review_edges": sum(review.values()),
        "top_rewrites": dict(rewrites.most_common(30)),
        "dropped_samples": {k: v for k, v in dropped_samples.items()},
        "applied": bool(apply),
    }

    if apply:
        bak = graph_path.with_suffix(
            graph_path.suffix + f".bak_relnorm_{time.strftime('%Y%m%d_%H%M%S')}"
        )
        shutil.copy2(graph_path, bak)
        data["edges"] = kept
        graph_path.write_text(
            json.dumps(data, ensure_ascii=False), encoding="utf-8"
        )
        result["backup"] = str(bak)

    if report_path is not None:
        lines = [
            "# 关系名归一化报告",
            "",
            f"- 图谱：`{graph_path}`",
            f"- 受控词表：{len(CANONICAL_RELATIONS)} 个 canonical 谓语",
            f"- 生成时间：{time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"- 落盘：{'是' if apply else '否（dry-run）'}",
            "",
            "## 词频分布对比",
            "",
            "| 指标 | 归一化前 | 归一化后（含待审核桶） | 归一化后（仅 canonical） |",
            "| --- | --- | --- | --- |",
        ]
        b, a, ac = (
            result["before"],
            result["after"],
            result["after_excluding_review_bucket"],
        )
        for key, label in (
            ("edges", "边数"),
            ("unique_relations", "唯一关系名"),
            ("singletons", "单例谓语数"),
            ("singleton_ratio_of_unique", "单例占唯一名比"),
            ("singleton_ratio_of_edges", "单例占边比"),
            ("top10_share_of_edges", "Top10 谓语覆盖边比"),
        ):
            lines.append(f"| {label} | {b[key]} | {a[key]} | {ac[key]} |")
        lines += [
            "",
            f"- 卫生过滤丢弃边：{n_dropped}",
            f"- 同键合并边：{n_merged}",
            f"- 待人工审核唯一名：{len(review)}（{sum(review.values())} 条边）",
            "",
            "## 判定原因分布（按边）",
            "",
            "| 原因 | 边数 |",
            "| --- | --- |",
        ]
        for r, n in reason_edges.most_common():
            lines.append(f"| {r} | {n} |")
        lines += ["", "## 丢弃样例", ""]
        for r, samples in dropped_samples.items():
            lines.append(f"- **{r}**：{'、'.join(samples)}")
        lines += ["", "## 待人工审核清单（原名 / 边数）", ""]
        for name, n in review.most_common():
            lines.append(f"- `{name}`  ×{n}")
        lines += ["", "## 归一化后词频（全表）", "", "| 关系 | 边数 |", "| --- | --- |"]
        for name, n in after.most_common():
            lines.append(f"| {name} | {n} |")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        result["report"] = str(report_path)
    return result


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="图谱关系名离线归一化（只改 relation 字段）")
    p.add_argument("--graph", required=True, help="图谱 JSON 路径")
    p.add_argument("--apply", action="store_true", help="落盘（默认 dry-run，先备份）")
    p.add_argument("--dry-run", action="store_true", help="只统计不落盘（默认行为）")
    p.add_argument(
        "--no-merge-dupes",
        action="store_true",
        help="不合并归一化后撞键的重复边（会破坏 (src,dst,relation) 唯一键）",
    )
    p.add_argument(
        "--drop-unmapped",
        action="store_true",
        help="映射不到的边直接丢弃（默认归入「待审核」哨兵桶：relation=待审核、原名存 relation_raw、打 needs_review 标记）",
    )
    p.add_argument("--report", default="", help="归一化报告落盘路径（.md）")
    args = p.parse_args(argv)

    gpath = Path(args.graph)
    if not gpath.is_file():
        print(f"[error] 图谱不存在：{gpath}")
        return 1
    report = Path(args.report) if args.report else None
    res = normalize(
        gpath,
        apply=bool(args.apply and not args.dry_run),
        merge_dupes=not args.no_merge_dupes,
        keep_unmapped=not args.drop_unmapped,
        report_path=report,
    )
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
