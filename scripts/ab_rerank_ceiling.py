# -*- coding: utf-8 -*-
"""重排上界验证（只改运行期实例属性 + 重排钩子，不改配置、不改检索代码）。

为什么做这个实验
-----------------
``ab_mention_depth.py`` 实测：把 mention 通道截断从 (per_entity=5, cap=10) 放大到
(20, 50) 后，60 道 never_candidate 题里 **gold 块进入候选池的从 0 题涨到 19 题**，
但最终 strict 只救回 **1 题**。

这说明瓶颈已经从「召回面（gold 进不了池）」转移到「排序（进了池挤不进 top-8）」：
候选池扩到 42 块后，RRF 按名次给分，排在 20 名开外的 gold 块拿到的融合分太低，
被 edge / mention 前排块挤出预算。**继续扩池是无效的**——扩得越大，gold 的名次
反而越靠后。

那就必须先回答：重排能不能把 gold 块捞上来？本脚本用**离线余弦重排**模拟 rerank 的
理论上限（不是某个具体 reranker 的成绩，是"这块料值不值得做 rerank"）：

  档 A 基线：生产截断 (5, 10)，不重排
  档 B 扩池：(20, 50)，不重排
  档 C 扩池 + 余弦重排：候选池全量按 query 余弦重排后取 top-(top+lexical_fallback)

判定**完全复用主评测口径**：把重排函数作为 ``evaluate_case`` 的 ``chunks_transform``
钩子传入，避免在实验脚本里自建 strict/inject 口径（自建口径已踩过坑：72.67% vs 67.67%
不可比）。候选池通过 spy 住 ``_fuse_channels`` 取得（融合前全通道候选，含块对象）。

用法（项目根目录）
------------------
    .venv/Scripts/python.exe -X utf8 scripts/ab_rerank_ceiling.py
    .venv/Scripts/python.exe -X utf8 scripts/ab_rerank_ceiling.py --limit 10   # 冒烟

输入：``data/knowledge/_audit/diag_block_provenance_20260917.json``
产物：``data/knowledge/_audit/ab_rerank_ceiling.json`` + 同名 ``.log``
退出码：0 正常｜1 环境缺失｜2 语义降级｜3 输入清单缺失
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from roleplay.config import get_settings  # noqa: E402
from roleplay.core.knowledge.factory import build_plot_registry  # noqa: E402
from roleplay.core.knowledge.plot_graph import (  # noqa: E402
    FUSE_MIN_SCORE,
    RetrievedChunk,
)

import diag_seedless_ceiling as D  # noqa: E402
import eval_plot_rag as E  # noqa: E402

DEFAULT_OUT = ROOT / "data" / "knowledge" / "_audit" / "ab_rerank_ceiling.json"
DEFAULT_FROM = ROOT / "data" / "knowledge" / "_audit" / "diag_block_provenance_20260917.json"

_LOG: list[str] = []


def log(msg: str) -> None:
    print(msg, flush=True)
    _LOG.append(str(msg))


def main() -> int:
    ap = argparse.ArgumentParser(description="重排上界验证（只读模拟，不改检索代码）")
    ap.add_argument("--character", default="wu_ming_zhe")
    ap.add_argument("--from", dest="from_path", default=str(DEFAULT_FROM))
    ap.add_argument("--expand-per", type=int, default=20)
    ap.add_argument("--expand-cap", type=int, default=50)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--scope", choices=("never", "all"), default="never",
                    help="never=只跑 never_candidate 子集；all=全量 300 题（**净收益必须用 all**）")
    ap.add_argument("--keep-top", type=int, default=0,
                    help="重排时保留 RRF 前 N 名不动，其余名额用余弦补位（0=全量重排）")
    ap.add_argument("--skip-b", action="store_true",
                    help="跳过 B 档（扩池不重排），只跑 A 与 C")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--allow-degraded", action="store_true")
    args = ap.parse_args()

    out_path = Path(args.out)
    log_path = out_path.with_suffix(out_path.suffix + ".log")
    src = Path(args.from_path)
    if args.scope == "all":
        # 重排是**全局**的：它同样会重排那 195 道已通过的题。只看 60 题子集会把
        # "新救回 9 题"当成净收益，而真实净收益必须扣掉被重排砸下去的题。
        # 故收益判定一律以全量口径为准，子集口径只用于解释"收益从哪来"。
        cases = []
        log("[scope] all：全量题集（净收益口径）")
    elif not src.is_file():
        log(f"[FAIL] 缺少输入清单 {src}")
        return 3
    else:
        prev = json.loads(src.read_text(encoding="utf-8"))
        cases = [c for c in (prev.get("per_case") or []) if c.get("kind") == "never_candidate"]
        log(f"[from] never_candidate 题 {len(cases)}")
    if args.limit:
        cases = cases[: args.limit]
    log(f"[from] never_candidate 题 {len(cases)}")

    settings = get_settings()
    registry = build_plot_registry(settings)
    retr = registry.get(args.character)
    if retr is None:
        log("[FAIL] 剧情图谱未加载")
        return 1
    sem = getattr(retr, "semantic", None)
    if sem is None and not args.allow_degraded:
        log("[FAIL] 语义通道已降级（--allow-degraded 可强行继续）")
        return 2

    top = int(getattr(settings, "plot_max_chunks", 3) or 3)
    lex_fb = int(getattr(settings, "plot_lexical_fallback", 2) or 0)
    inject_chars = int(getattr(settings, "plot_context_max_chars", 1000) or 0)
    budget = top + max(0, lex_fb)

    items = E.load_testset(None)
    by_id = {str(it.get("id")): it for it in items}
    todo = items if args.scope == "all" else [by_id[str(c["id"])] for c in cases
                                             if str(c["id"]) in by_id]
    if args.limit:
        todo = todo[: args.limit]
    oracle = E.build_oracle(retr.corpus, todo)
    log(f"[load] 待救题 {len(todo)}｜top={top}｜lexical_fallback={lex_fb}｜预算 {budget} 块")

    # 语义索引：hash → 行号，供余弦重排取块向量
    _hashes = getattr(sem, "hashes", None)
    vecs = getattr(sem, "vectors", None)
    hash2row: dict[str, int] = {}
    if _hashes is not None:
        hash2row = {str(h): i for i, h in enumerate(_hashes)}
    log(f"[idx] 语义索引 {len(hash2row)} 块")

    # spy：捕获融合前全通道候选（保留**块对象**，重排要用）
    cap: dict[str, Any] = {"pool": []}
    orig_fuse = retr._fuse_channels

    def spy(channels, *, limit):
        # 注意：候选池里是**裸 PlotChunk**（无 metadata），而 retrieve 返回的是
        # RetrievedChunk。重排后必须自己包一层，否则 evaluate_case 读 c.metadata 会炸。
        seen: list[tuple[str, float, Any, dict]] = []
        seen_h: set[str] = set()
        for path, _w, ch_items in channels:
            for score, c, extra in ch_items:
                h = str(getattr(c, "hash", "") or "")
                if h and h not in seen_h:
                    seen_h.add(h)
                    seen.append((str(path), float(score), c, dict(extra or {})))
        cap["pool"] = seen
        return orig_fuse(channels, limit=limit)

    retr._fuse_channels = spy
    prod_per = int(getattr(retr, "mention_per_entity", 5))
    prod_cap = int(getattr(retr, "mention_total_cap", 10))

    def make_rerank(enable: bool, keep_top: int = 0):
        """返回 chunks_transform 钩子：按 query 余弦重排候选池后截断到预算。

        ``keep_top > 0`` 时保留 RRF 前 N 名不动，只用余弦给**剩余名额**补位。
        为什么需要这个模式（实测驱动）：全量重排把 inject 从 177 打到 151（-26 题）。
        原因是余弦偏袒「与 query 整体最像」的块，选出的 8 块容易高度同质，
        丢掉 RRF 多路命中带来的**互补证据**；而 inject 口径（2400 字符装配）
        恰恰需要多块互补才能覆盖全部证据组。保留头部 = 保住互补性，
        只让尾部名额去捞深层候选。
        """
        def fn(query: str, chunks: list[Any]) -> list[Any]:
            if not enable:
                return chunks
            pool = cap.get("pool") or []
            if not pool or sem is None or vecs is None:
                return chunks
            qvec = D.embed_with_retry(retr, query)
            if qvec is None:
                return chunks
            qn = np.asarray(qvec, dtype=np.float32)
            qn = qn / (np.linalg.norm(qn) or 1.0)
            scored: list[tuple[float, int, Any, dict]] = []
            for i, (_path, _sc, c, extra) in enumerate(pool):
                row = hash2row.get(str(getattr(c, "hash", "") or ""))
                if row is None:
                    continue
                v = vecs[row]
                nv = np.linalg.norm(v)
                if not nv:
                    continue
                scored.append((float(np.dot(v, qn) / nv), i, c, extra))
            if not scored:
                return chunks
            scored.sort(key=lambda t: (-t[0], t[1]))
            keep: list[Any] = []
            if keep_top:
                keep = list(chunks[:keep_top])
                # RetrievedChunk 没有 hash 属性，用文本前缀做身份键足够（块文本唯一）
                keep_keys = {(getattr(c, "text", "") or "")[:120] for c in keep}
                scored = [t for t in scored
                          if (getattr(t[2], "text", "") or "")[:120] not in keep_keys]
            picked = scored[: max(0, budget - len(keep))]
            # 分数带对齐（第一版实测翻车点，显式处理）：
            # RRF 归一到 [FUSE_MIN_SCORE, 1.0]；补位块的分数必须**低于**被保留的
            # 头部块，否则名次会被打乱，keep_top 就失去意义。
            keep_min = min((float(getattr(c, "score", 0.0) or 0.0) for c in keep),
                           default=1.0)
            raw = [s for s, _i, _c, _e in picked]
            lo, hi = (min(raw), max(raw)) if raw else (0.0, 1.0)
            span = (hi - lo) or 1.0
            ceil_score = max(FUSE_MIN_SCORE, keep_min - 1e-3) if keep else 1.0
            out: list[Any] = list(keep)
            for s, _i, c, extra in picked:
                frac = (s - lo) / span
                norm = FUSE_MIN_SCORE + (ceil_score - FUSE_MIN_SCORE) * frac
                meta = c.meta(retr.namespace)
                meta.update(extra or {})
                meta["reranked"] = True
                out.append(RetrievedChunk(text=c.text, score=float(norm), metadata=meta))
            return out
        return fn

    def run_negatives(rerank: bool, keep_top: int = 0) -> dict[str, Any]:
        """负样本判定（与 E.evaluate_negatives 同口径：注入 = 返回块数）。

        之所以不直接调 ``E.evaluate_negatives``：它内部直接 ``retr.retrieve``，
        拿不到 chunks_transform，重排档的负样本读数会失真。口径不变，只是把
        transform 自己套上。
        """
        total = 0
        cases_with = 0
        dirty: list[str] = []
        transform = make_rerank(rerank, keep_top)
        for _cat, q in E.NEGATIVE_CASES:
            cap["pool"] = []
            chunks = retr.retrieve(q, top_chunks=top, lexical_fallback=lex_fb)
            chunks = transform(q, chunks)
            n = len(chunks)
            total += n
            if n:
                cases_with += 1
                dirty.append(q)
        known = set(getattr(E, "KNOWN_RESIDUAL_NEGATIVES", ()) or ())
        # 对偶校验：同一实例、同一时刻再跑一次主评测的负样本函数。
        # 两个口径必须给出相同的「失守条数 / 注入块数」；不一致说明本函数的
        # transform 包装改变了行为（或主评测口径已变），此时读数不可信，必须暴露。
        ref = E.evaluate_negatives(retr, top, lex_fb)
        ref_cases = len(ref.get("violations") or [])
        ref_blocks = ref.get("negative_injection_total")
        consistent = (ref_cases == cases_with and ref_blocks == total)
        if not consistent:
            log(f"  [warn] 负样本口径不一致：本函数 {cases_with} 条/{total} 块 "
                f"vs 主评测 {ref_cases} 条/{ref_blocks} 块")
        return {
            "cases": len(E.NEGATIVE_CASES),
            "cases_with_injection": cases_with,
            "injection_total": total,
            "new_leaks": [q for q in dirty if q not in known],
            "crosscheck_main_eval": {
                "cases_with_injection": ref_cases,
                "injection_total": ref_blocks,
                "consistent": consistent,
            },
        }

    def run(label: str, per: int, capv: int, rerank: bool, keep_top: int = 0) -> dict[str, Any]:
        retr.mention_per_entity, retr.mention_total_cap = per, capv
        t0 = time.time()
        n_pass = 0
        n_inj = 0
        pool_sizes: list[int] = []
        for item in todo:
            cap["pool"] = []
            row = E.evaluate_case(retr, item, oracle[str(item.get("id"))], top, lex_fb,
                                  inject_chars,
                                  chunks_transform=make_rerank(rerank, keep_top))
            n_pass += int(bool(row.get("strict_pass")))
            n_inj += int(bool(row.get("inject_pass")))
            pool_sizes.append(len(cap["pool"]))
        neg = run_negatives(rerank)
        r = {
            "label": label, "per_entity": per, "total_cap": capv, "rerank": rerank,
            "strict_pass_n": n_pass, "strict_pass": D.rate(n_pass, len(todo)),
            "inject_pass_n": n_inj, "inject_pass": D.rate(n_inj, len(todo)),
            "pool_avg": round(sum(pool_sizes) / max(1, len(pool_sizes)), 1),
            # 键名必须与 run_negatives 的返回**逐字对齐**：这里曾误用主评测的
            # ``violations`` / ``negative_injection_total``，结果失守条数被吞成 0、
            # 块数变成 null，护栏读数完全失真（口径纪律：0 与"没测到"必须可区分）。
            "negatives": {
                "cases": neg.get("cases"),
                "cases_with_injection": neg.get("cases_with_injection"),
                "injection_total": neg.get("injection_total"),
                "new_leaks": neg.get("new_leaks"),
                "crosscheck_main_eval": neg.get("crosscheck_main_eval"),
            },
            "elapsed_s": round(time.time() - t0, 1),
        }
        xc = r["negatives"].get("crosscheck_main_eval") or {}
        log(f"  [{label}] strict {n_pass}/{len(todo)}｜inject {n_inj}"
            f"｜候选池均 {r['pool_avg']} 块"
            f"｜负样本失守 {r['negatives']['cases_with_injection']}/{r['negatives']['cases']} 条"
            f"（注入 {r['negatives']['injection_total']} 块，"
            f"新增泄漏 {len(r['negatives']['new_leaks'] or [])}，"
            f"对偶校验 {'一致' if xc.get('consistent') else '不一致'}）｜{r['elapsed_s']}s")
        return r

    results = [run("A 基线(5,10)", prod_per, prod_cap, False)]
    if not args.skip_b:
        results.append(run(f"B 扩池({args.expand_per},{args.expand_cap})",
                           args.expand_per, args.expand_cap, False))
    results.append(run(f"C 扩池+余弦重排(keep_top={args.keep_top})",
                       args.expand_per, args.expand_cap, True, args.keep_top))

    retr._fuse_channels = orig_fuse
    retr.mention_per_entity, retr.mention_total_cap = prod_per, prod_cap

    base = results[0]
    report = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "config": {"top": top, "lexical_fallback": lex_fb, "inject_chars": inject_chars,
                   "budget": budget, "cases": len(todo)},
        "results": results,
        "delta_vs_baseline": [
            {"label": r["label"],
             "d_strict": (r["strict_pass_n"] or 0) - (base["strict_pass_n"] or 0),
             "d_inject": (r["inject_pass_n"] or 0) - (base["inject_pass_n"] or 0),
             "d_neg_cases": (r["negatives"]["cases_with_injection"] or 0)
                            - (base["negatives"]["cases_with_injection"] or 0)}
            for r in results
        ],
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    log("\n==== 摘要 ====")
    for d in report["delta_vs_baseline"]:
        log(f"{d['label']:<28} Δstrict={d['d_strict']:+d} 题｜Δinject={d['d_inject']:+d} 题"
            f"｜Δ负样本失守={d['d_neg_cases']:+d} 条")
    log(f"[out] {out_path}")
    log_path.write_text("\n".join(_LOG), encoding="utf-8")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except BaseException as exc:  # noqa: BLE001
        import traceback
        try:
            Path(str(DEFAULT_OUT) + ".crash").write_text(
                f"{time.strftime('%Y-%m-%d %H:%M:%S')}\n{traceback.format_exc()}",
                encoding="utf-8")
        except Exception:
            pass
        print(f"[CRASH] {exc!r}", flush=True)
        raise
