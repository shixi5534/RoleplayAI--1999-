# -*- coding: utf-8 -*-
"""剧情 RAG（PlotGraph）离线检索评测台（非 pytest，直接跑真实图谱 + 300 题集）。

与 ``scripts/eval_rag_huiji.py``（14 题灰机标准）的分工：
  - 灰机 14 题：人工核对的标准答案，用于**正确性**回归（并集子串命中，宽松）；
  - 本脚本 300 题：``data/knowledge/_audit/rag_testset_300.json``，用于**可复现的检索指标**
    （严格通过率 / 块精度 / 答案块率 / oracle recall / MRR / 延迟 / 路径归因 / 负样本）。

关键设计（为什么指标要这么定）：
  1. **oracle 天花板**：题集的 evidence 组并不保证"存在单块覆盖全部组"的语料块
     （实测 27/300 题不存在）。这类题只能靠多块并集命中，因此除 ``strict_pass`` 外
     单独报 ``ceiling_pass``（只在天花板内的题上算），避免把"语料缺口"记到检索头上。
  2. **严格口径与灰机评测一致**：证据组内任一关键词出现在**返回块并集**里即算覆盖，
     全部组覆盖才算 PASS。口径一致才能与 13/14 的历史结论横向比较。
  3. **路径归因**：``via`` 只有 plot_graph / plot_lexical 两个值，无法区分"边证据路"
     与"种子提及路"。本脚本按 ``meta["path"]`` 归因，缺失时回落到结构推断，
     让"图谱结构到底有没有起作用"第一次可测。
  4. **负样本**：通用问句（天气/写诗/算术）必须**零注入**。这是"图内泛词实体当种子"
     这类精度缺陷唯一稳定的护栏。
  5. **可复现**：报告记录 argv、配置快照、数据文件 SHA256、抽样参数；
     同参数复跑逐位可比。

用法（项目根目录）：
  .venv/Scripts/python.exe -X utf8 scripts/eval_plot_rag.py                    # 全量 300 题
  .venv/Scripts/python.exe -X utf8 scripts/eval_plot_rag.py --sample 60 --seed 7 # 分层抽样快跑
  .venv/Scripts/python.exe -X utf8 scripts/eval_plot_rag.py --baseline data/knowledge/_audit/plot_rag_eval_report.json
  .venv/Scripts/python.exe -X utf8 scripts/eval_plot_rag.py --check-targets     # 验收线自检

退出码：0 正常（或与基线相比未回退）｜1 环境/数据缺失｜2 缺少必要的基线｜3 相对基线回退｜4 验收线未达标
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import statistics
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from roleplay.config import get_settings  # noqa: E402
from roleplay.core.knowledge.factory import build_plot_registry  # noqa: E402
from roleplay.core.knowledge.plot_corpus import chunk_hash  # noqa: E402

DEFAULT_CHARACTER = "wu_ming_zhe"
TESTSET_PATH = ROOT / "data" / "knowledge" / "_audit" / "rag_testset_300.json"
DEFAULT_OUT = ROOT / "data" / "knowledge" / "_audit" / "plot_rag_eval_report.json"

# ── 验收线（A1/A5 来自审计报告 §2；A2–A4 是相对基线的增量，见 --baseline）────────
TARGET_LATENCY_P95_MS = 300.0
TARGET_NEGATIVE_INJECTION = 0

# ── 负样本：通用问句 / 元问题 / 与剧情无关的请求，必须零注入 ────────────────────
# 覆盖三类失效模式：① 图内泛词实体（天气/故事）；② 纯闲聊；③ 系统元问题。
NEGATIVE_QUERIES = [
    "今天天气怎么样",
    "帮我写一首关于春天的诗",
    "1+1 等于几",
    "推荐几家附近的餐厅",
    "你怎么看最近的经济形势",
    "给我讲个笑话",
    "明天几点开会",
    "这个软件怎么安装",
    "你好呀，在吗",
    "用 Python 写一个快速排序",
]

# 与基线对比时的回退判定：这些指标「越大越好」
HIGHER_IS_BETTER = ("strict_pass", "chunk_precision", "answer_chunk_rate", "mrr")
# 这些指标「越小越好」
LOWER_IS_BETTER = ("latency_p95_ms", "negative_injection_total")
# 回退容忍（比率类指标允许 0.005 的浮点/抽样抖动）
TOLERANCE = 0.005


def sha256_head(path: Path, n: int = 16) -> str:
    """文件指纹前 n 位（数据资产可复现标识；缺失返回空串）。"""
    try:
        h = hashlib.sha256()
        with path.open("rb") as fh:
            for block in iter(lambda: fh.read(1 << 20), b""):
                h.update(block)
        return h.hexdigest()[:n]
    except OSError:
        return ""


def percentile(values: list[float], q: float) -> float:
    """线性插值分位数（不引第三方依赖；values 需非空）。"""
    if not values:
        return 0.0
    xs = sorted(values)
    if len(xs) == 1:
        return float(xs[0])
    pos = (len(xs) - 1) * q
    lo, hi = int(pos), min(int(pos) + 1, len(xs) - 1)
    frac = pos - lo
    return float(xs[lo] * (1 - frac) + xs[hi] * frac)


def stratified_sample(items: list[dict], n: int, seed: int) -> list[dict]:
    """按 ``dims.type`` 比例分层抽样（确定性：同 n/seed 必得同一子集）。"""
    if n <= 0 or n >= len(items):
        return list(items)
    pools: dict[str, list[dict]] = defaultdict(list)
    for it in items:
        pools[str(it.get("dims", {}).get("type") or "unknown")].append(it)
    rng = random.Random(seed)
    picked: list[dict] = []
    for key in sorted(pools):
        pool = sorted(pools[key], key=lambda x: x.get("id", ""))
        want = max(1, round(n * len(pool) / len(items)))
        picked.extend(rng.sample(pool, min(want, len(pool))))
    picked = picked[:n] if len(picked) > n else picked
    picked.sort(key=lambda x: x.get("id", ""))
    return picked


def load_testset() -> list[dict]:
    data = json.loads(TESTSET_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, list) or not data:
        raise SystemExit(f"[FAIL] 题集为空或结构非法：{TESTSET_PATH}")
    return [it for it in data if isinstance(it, dict) and it.get("q") and it.get("evidence")]


def build_oracle(corpus, items: list[dict]) -> dict[str, dict]:
    """每题预计算 oracle 命中块（单块覆盖全部证据组 = full，覆盖任一 = any）。

    返回 ``{item_id: {"full": set[hash], "any": set[hash], "ceiling": bool}}``。
    语料 8358 块 × 300 题实测约 2s，一次性成本。
    """
    out: dict[str, dict] = {}
    for it in items:
        groups = it["evidence"]
        full: set[str] = set()
        anyhit: set[str] = set()
        for chunk in corpus.chunks:
            text = chunk.text
            hits = [any(kw in text for kw in g) for g in groups]
            if all(hits):
                full.add(chunk.hash)
            if any(hits):
                anyhit.add(chunk.hash)
        out[str(it.get("id"))] = {
            "full": full,
            "any": anyhit,
            "ceiling": bool(full),  # 天花板：存在可单块作答的语料块
        }
    return out


def infer_path(meta: dict) -> str:
    """区块路径归因：优先新字段 ``path``，缺失时按旧字段结构推断（兼容优化前代码）。"""
    path = str(meta.get("path") or "")
    if path:
        return path
    if str(meta.get("via") or "") == "plot_lexical":
        return "lexical"
    if meta.get("seed_mention"):
        return "mention"
    if meta.get("edge"):
        return "edge"
    return "unknown"


def evaluate_case(retr, item: dict, oracle: dict, top: int, lexical_fallback: int) -> dict:
    """单题检索 + 打分（严格口径与灰机评测一致：并集子串命中）。"""
    t0 = time.perf_counter()
    chunks = retr.retrieve(item["q"], top_chunks=top, lexical_fallback=lexical_fallback)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    groups = item["evidence"]
    union = "\n".join(c.text for c in chunks)
    covered = [any(kw in union for kw in g) for g in groups]
    missing = [i for i, ok in enumerate(covered) if not ok]

    # RetrievedChunk 不带 hash 字段（只有 text/score/metadata）：用语料同一套文本指纹
    # 还原，保证与 oracle 命中集、图谱 evidence.hash 三处同口径。
    hashes = [chunk_hash(c.text) for c in chunks]
    full = oracle["full"]
    anyhit = oracle["any"]
    n_full = sum(1 for h in hashes if h in full)
    n_rel = sum(1 for h in hashes if h in anyhit)
    total = len(hashes)

    # MRR：第一个「全证据组覆盖块」的名次（1 基）；无则 0
    mrr = 0.0
    for rank, h in enumerate(hashes, start=1):
        if h in full:
            mrr = 1.0 / rank
            break
    # oracle recall@k：返回里命中的 full 块占「可命中上限」的比例
    denom = min(top, len(full)) if full else 0
    recall = (min(n_full, denom) / denom) if denom else 0.0

    paths = Counter(infer_path(c.metadata or {}) for c in chunks)
    return {
        "id": item.get("id"),
        "q": item["q"],
        "dims": item.get("dims") or {},
        "strict_pass": not missing,
        "covered": f"{len(groups) - len(missing)}/{len(groups)}",
        "missing_groups": missing,
        "ceiling": oracle["ceiling"],
        "n_chunks": total,
        "n_relevant": n_rel,
        "n_full_match": n_full,
        "recall": round(recall, 4),
        "mrr": round(mrr, 4),
        "paths": dict(paths),
        "latency_ms": round(elapsed_ms, 2),
    }


def aggregate(rows: list[dict]) -> dict:
    """总体指标（strict_pass 等为比率，latency 为毫秒分位）。"""
    n = max(1, len(rows))
    ceiling_rows = [r for r in rows if r["ceiling"]]
    lat = [r["latency_ms"] for r in rows]
    n_chunks = sum(r["n_chunks"] for r in rows)
    paths: Counter = Counter()
    for r in rows:
        paths.update(r["paths"])
    return {
        "cases": len(rows),
        "ceiling_cases": len(ceiling_rows),
        "strict_pass": round(sum(1 for r in rows if r["strict_pass"]) / n, 4),
        "strict_pass_n": sum(1 for r in rows if r["strict_pass"]),
        "ceiling_pass": round(
            sum(1 for r in ceiling_rows if r["strict_pass"]) / max(1, len(ceiling_rows)), 4
        ),
        "chunk_precision": round(sum(r["n_relevant"] for r in rows) / max(1, n_chunks), 4),
        "answer_chunk_rate": round(sum(r["n_full_match"] for r in rows) / max(1, n_chunks), 4),
        "mrr": round(sum(r["mrr"] for r in rows) / n, 4),
        "recall": round(statistics.mean([r["recall"] for r in rows]) if rows else 0.0, 4),
        "avg_returned_chunks": round(n_chunks / n, 2),
        "latency_p50_ms": round(percentile(lat, 0.50), 1),
        "latency_p90_ms": round(percentile(lat, 0.90), 1),
        "latency_p95_ms": round(percentile(lat, 0.95), 1),
        "latency_max_ms": round(max(lat) if lat else 0.0, 1),
        "path_counts": dict(paths),
        "empty_rate": round(sum(1 for r in rows if r["n_chunks"] == 0) / n, 4),
    }


def by_dimension(rows: list[dict], dim: str) -> dict:
    """按 ``dims`` 某一维度分层聚合（定位"哪类题在拖后腿"）。"""
    buckets: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        buckets[str((r.get("dims") or {}).get(dim) or "unknown")].append(r)
    out: dict[str, dict] = {}
    for key in sorted(buckets):
        sub = buckets[key]
        out[key] = {
            "cases": len(sub),
            "strict_pass": round(sum(1 for r in sub if r["strict_pass"]) / len(sub), 4),
            "chunk_precision": round(
                sum(r["n_relevant"] for r in sub) / max(1, sum(r["n_chunks"] for r in sub)), 4
            ),
            "latency_p50_ms": round(percentile([r["latency_ms"] for r in sub], 0.5), 1),
        }
    return out


def evaluate_negatives(retr, top: int, lexical_fallback: int) -> dict:
    """负样本：通用问句必须零注入。注入即列出块首句，便于定位是哪类泛词种子。"""
    rows = []
    for q in NEGATIVE_QUERIES:
        t0 = time.perf_counter()
        chunks = retr.retrieve(q, top_chunks=top, lexical_fallback=lexical_fallback)
        ms = (time.perf_counter() - t0) * 1000.0
        rows.append(
            {
                "q": q,
                "injected": len(chunks),
                "paths": dict(Counter(infer_path(c.metadata or {}) for c in chunks)),
                "samples": [c.text[:60] for c in chunks[:2]],
                "latency_ms": round(ms, 2),
            }
        )
    return {
        "cases": len(rows),
        "negative_injection_total": sum(r["injected"] for r in rows),
        "negative_clean": all(r["injected"] == 0 for r in rows),
        "rows": rows,
    }


def compare_with_baseline(base: dict, cur: dict) -> tuple[list[dict], bool]:
    """与基线报告对比，返回 (对比行, 是否回退)。"""
    b, c = base.get("summary", {}), cur.get("summary", {})
    b_neg = base.get("negatives", {}).get("negative_injection_total")
    c_neg = cur.get("negatives", {}).get("negative_injection_total")
    rows: list[dict] = []
    regressed = False

    def _add(name: str, before, after, higher_better: bool) -> None:
        nonlocal regressed
        if before is None or after is None:
            rows.append({"metric": name, "baseline": before, "current": after, "delta": None})
            return
        delta = round(float(after) - float(before), 4)
        bad = delta < -TOLERANCE if higher_better else delta > TOLERANCE
        regressed = regressed or bad
        rows.append(
            {
                "metric": name,
                "baseline": before,
                "current": after,
                "delta": delta,
                "verdict": "回退" if bad else ("提升" if delta else "持平"),
            }
        )

    for key in HIGHER_IS_BETTER:
        _add(key, b.get(key), c.get(key), True)
    for key in LOWER_IS_BETTER:
        if key == "negative_injection_total":
            _add(key, b_neg, c_neg, False)
        else:
            _add(key, b.get(key), c.get(key), False)
    return rows, regressed


def check_targets(summary: dict, negatives: dict) -> tuple[bool, list[str]]:
    """验收线自检（A1 / A5；A2–A4 属相对基线增量，由 --baseline 判定）。"""
    notes: list[str] = []
    ok = True
    if summary["latency_p95_ms"] > TARGET_LATENCY_P95_MS:
        ok = False
        notes.append(
            f"A1 未达标：p95 {summary['latency_p95_ms']}ms > {TARGET_LATENCY_P95_MS}ms"
        )
    if negatives["negative_injection_total"] > TARGET_NEGATIVE_INJECTION:
        ok = False
        notes.append(
            f"A5 未达标：负样本注入 {negatives['negative_injection_total']} 块 > "
            f"{TARGET_NEGATIVE_INJECTION}"
        )
    return ok, notes


def main() -> int:
    ap = argparse.ArgumentParser(description="剧情 RAG 离线检索评测台（300 题集）")
    ap.add_argument("--character", default=DEFAULT_CHARACTER, help="角色 id（默认 wu_ming_zhe）")
    # 默认与生产严格对齐：plot_max_chunks=3 + plot_lexical_fallback=2（返回上限 5 块）。
    # 想复现灰机报告的宽松口径可显式 --top 10。
    ap.add_argument("--top", type=int, default=3, help="图路返回块上限（生产 plot_max_chunks=3）")
    ap.add_argument("--lexical-fallback", type=int, default=2, help="词法兜底条数（生产默认 2）")
    ap.add_argument("--sample", type=int, default=0, help="分层抽样题量（0=全量；同 seed 确定性）")
    ap.add_argument("--seed", type=int, default=7, help="抽样随机种子")
    ap.add_argument("--limit", type=int, default=0, help="只跑前 N 题（冒烟用，不用于对比）")
    ap.add_argument("--out", default=str(DEFAULT_OUT), help="报告落盘路径")
    ap.add_argument("--baseline", default="", help="基线报告路径：与本次结果对比并判定回退")
    ap.add_argument("--check-targets", action="store_true", help="按审计验收线 A1/A5 自检")
    ap.add_argument("--quiet", action="store_true", help="不逐题打印")
    args = ap.parse_args()

    settings = get_settings()
    # 走**生产同一条装配路径**（build_plot_registry 从 Settings 读全部检索参数）。
    # 反例教训：脚本一度自行 new PlotGraphRegistry(...) 只传了 4 个参数，新增的融合权重
    # 与门控参数全被默认值覆盖——评测量到的根本不是生产配置（消融实验 7 组结果一模一样
    # 才发现）。凡"调试入口"都必须与生产共用装配函数。
    registry = build_plot_registry(settings)
    t0 = time.time()
    retr = registry.get(args.character)
    if retr is None:
        print(f"[FAIL] 剧情图谱未能加载（角色 {args.character}）；请先运行 "
              f"scripts/build_plot_graph.py --character {args.character}")
        return 1
    load_s = time.time() - t0

    items = load_testset()
    if args.sample:
        items = stratified_sample(items, args.sample, args.seed)
    if args.limit:
        items = items[: args.limit]

    print(
        f"[load] 角色 {args.character}｜实体 {len(retr.store.entities())}｜"
        f"边 {len(retr.store.all_edges())}｜语料 {len(retr.corpus.chunks)} 块｜"
        f"加载 {load_s:.2f}s"
    )
    print(f"[eval] 题量 {len(items)}｜top={args.top}｜lexical_fallback={args.lexical_fallback}"
          f"｜sample={args.sample or '全量'}｜seed={args.seed}")

    t0 = time.time()
    oracle = build_oracle(retr.corpus, items)
    ceiling_n = sum(1 for v in oracle.values() if v["ceiling"])
    print(f"[oracle] 天花板内题 {ceiling_n}/{len(items)}（其余题不存在单块覆盖全部证据组的语料块）"
          f"｜耗时 {time.time() - t0:.1f}s")

    rows: list[dict] = []
    t0 = time.time()
    for i, item in enumerate(items, start=1):
        row = evaluate_case(retr, item, oracle[str(item.get("id"))], args.top, args.lexical_fallback)
        rows.append(row)
        if not args.quiet:
            tag = "PASS" if row["strict_pass"] else "FAIL"
            print(
                f"[{i:3d}/{len(items)}] {tag} {row['id']} {str(row['dims'].get('type'))[:9]:9s} "
                f"覆盖 {row['covered']}｜相关 {row['n_relevant']}/{row['n_chunks']}｜"
                f"满匹配 {row['n_full_match']}｜{row['latency_ms']:8.1f}ms  {row['q'][:30]}",
                flush=True,
            )
    eval_s = time.time() - t0

    summary = aggregate(rows)
    negatives = evaluate_negatives(retr, args.top, args.lexical_fallback)
    dims_report = {
        dim: by_dimension(rows, dim)
        for dim in ("type", "difficulty", "depth", "hop", "chapter", "text_len")
        if any((r.get("dims") or {}).get(dim) for r in rows)
    }

    print("\n==== 汇总（严格口径：并集子串覆盖全部证据组） ====")
    print(
        f"题量 {summary['cases']}｜严格通过 {summary['strict_pass_n']} "
        f"({summary['strict_pass']:.1%})｜天花板内 {summary['ceiling_pass']:.1%}"
    )
    print(
        f"块精度 {summary['chunk_precision']:.3f}｜答案块率 {summary['answer_chunk_rate']:.3f}"
        f"｜MRR {summary['mrr']:.3f}｜oracle recall {summary['recall']:.3f}"
        f"｜平均返回 {summary['avg_returned_chunks']} 块｜空结果 {summary['empty_rate']:.1%}"
    )
    print(
        f"延迟 p50 {summary['latency_p50_ms']}ms｜p90 {summary['latency_p90_ms']}ms"
        f"｜p95 {summary['latency_p95_ms']}ms｜max {summary['latency_max_ms']}ms"
        f"｜检索总耗时 {eval_s:.1f}s"
    )
    print(f"路径归因 {summary['path_counts']}")
    print(
        f"负样本 {negatives['cases']} 条｜注入块合计 {negatives['negative_injection_total']}"
        f"｜零注入 {negatives['negative_clean']}"
    )
    for dim, buckets in dims_report.items():
        worst = sorted(buckets.items(), key=lambda kv: kv[1]["strict_pass"])[:3]
        print(f"  [{dim}] 最弱三档：" + "｜".join(
            f"{k} {v['strict_pass']:.0%}(n={v['cases']})" for k, v in worst
        ))
    for r in negatives["rows"]:
        if r["injected"]:
            print(f"  [负样本注入] {r['q']} → {r['injected']} 块 {r['paths']} "
                  f"样例：{r['samples'][:1]}")

    report = {
        "meta": {
            "tool": "scripts/eval_plot_rag.py",
            "standard": "rag_testset_300.json（证据组并集子串覆盖）+ 负样本零注入",
            "character": args.character,
            "argv": sys.argv,
            "top": args.top,
            "lexical_fallback": args.lexical_fallback,
            "sample": args.sample,
            "seed": args.seed,
            "limit": args.limit,
            "config": {
                k: getattr(settings, k)
                for k in dir(settings)
                if k.startswith("plot_") and not k.startswith("__")
            },
            "assets_sha256_head16": {
                "plot_graph": sha256_head(Path(settings.plot_graph_dir) / f"plot_graph_{args.character}.json"),
                "plot_corpus": sha256_head(Path(settings.plot_corpus_dir) / f"plot_corpus_{args.character}.json"),
                "testset": sha256_head(TESTSET_PATH),
            },
            "started_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "elapsed_s": round(load_s + eval_s, 1),
        },
        "summary": summary,
        "by_dims": dims_report,
        "negatives": negatives,
        "items": rows,
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[save] {out}")

    rc = 0
    if args.baseline:
        bp = Path(args.baseline)
        if not bp.is_file():
            print(f"[FAIL] 基线报告不存在：{bp}")
            return 2
        base = json.loads(bp.read_text(encoding="utf-8"))
        b_meta = base.get("meta", {})
        if (b_meta.get("sample"), b_meta.get("seed"), b_meta.get("top")) != (
            args.sample, args.seed, args.top
        ) and not args.limit:
            print(
                f"[warn] 基线抽样参数不一致（基线 sample={b_meta.get('sample')} "
                f"seed={b_meta.get('seed')} top={b_meta.get('top')}）——对比仅供参考"
            )
        rows_cmp, regressed = compare_with_baseline(base, report)
        print("\n==== 基线对比（+ 提升 / - 回退） ====")
        for r in rows_cmp:
            d = "—" if r["delta"] is None else f"{r['delta']:+.4f}"
            print(f"  {r['metric']:24s} {str(r['baseline']):>10} → {str(r['current']):>10}  {d}"
                  f"  {r.get('verdict', '')}")
        if regressed:
            print("[FAIL] 存在指标回退（阈值 0.005）")
            rc = 3

    if args.check_targets:
        ok, notes = check_targets(summary, negatives)
        print("\n==== 验收线自检 ====")
        print(f"  A1 延迟 p95 ≤ {TARGET_LATENCY_P95_MS}ms：{summary['latency_p95_ms']}ms")
        print(f"  A5 负样本零注入：{negatives['negative_injection_total']} 块")
        for note in notes:
            print(f"  [未达标] {note}")
        if not ok and rc == 0:
            rc = 4
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
