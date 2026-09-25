# -*- coding: utf-8 -*-
"""`never_candidate` 正解块「到底在哪」探测（只读诊断，不改检索行为）。

背景
----
``diag_block_provenance.py`` 实测：105 道失败题里 **60 题的正解块从未进入任何通道
候选池**。这是当前最大的失分组，但在动手修之前必须先回答三个问题——它们的答案
对应**三种完全不同的修法**，选错就是白投：

  Q1. 正解块在**语义全库**里排第几？（不是候选池里排第几，是 9021 块里排第几）
      - 若集中在 top-50~200 ⇒ 「候选池太浅」，扩池 + RRF 即可，成本最低；
      - 若排在几千名开外 ⇒ 语义表示对这类 query 失效，扩池无用，只能改查询表示或索引。
  Q2. 正解块在**BM25 词法**全库里排第几？词法路当前候选命中率是 0%，需要确认
      是「排在后面」还是「一个 query 词都没命中」（后者意味着词法路结构性不可达）。
  Q3. 正解块文本里**有没有种子实体的名字**？
      - mention 通道靠「块文本含种子名」取块；若 gold 块不含任何种子名，
        那这条通道对这 60 题是结构性不可达的，修融合/预算/重排都救不了。

产出即决策依据：
  - ``semantic_top_k_hit``：语义全库 top-K 命中率（K=20/50/100/200/500/1000/全库）
  - ``lexical_top_k_hit``：BM25 全库 top-K 命中率
  - ``gold_has_seed_name_rate``：gold 块含种子实体名的题数比例（mention 通道可达性）

用法（项目根目录）
------------------
    .venv/Scripts/python.exe -X utf8 scripts/diag_gold_rank.py
    .venv/Scripts/python.exe -X utf8 scripts/diag_gold_rank.py --limit 10   # 冒烟

输入：``data/knowledge/_audit/diag_block_provenance_20260917.json``（never_candidate 清单）
产物：``data/knowledge/_audit/diag_gold_rank.json`` + 同名 ``.log``
退出码：0 正常｜1 环境/数据缺失｜2 语义降级｜3 输入清单缺失
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

import diag_seedless_ceiling as D  # noqa: E402
import eval_plot_rag as E  # noqa: E402

DEFAULT_OUT = ROOT / "data" / "knowledge" / "_audit" / "diag_gold_rank.json"
DEFAULT_FROM = ROOT / "data" / "knowledge" / "_audit" / "diag_block_provenance_20260917.json"
KS = (20, 50, 100, 200, 500, 1000, 9021)

_LOG: list[str] = []


def log(msg: str) -> None:
    print(msg, flush=True)
    _LOG.append(str(msg))


def main() -> int:
    ap = argparse.ArgumentParser(description="正解块全库排名探测（只读诊断）")
    ap.add_argument("--character", default="wu_ming_zhe")
    ap.add_argument("--from", dest="from_path", default=str(DEFAULT_FROM))
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--allow-degraded", action="store_true")
    args = ap.parse_args()

    out_path = Path(args.out)
    log_path = out_path.with_suffix(out_path.suffix + ".log")
    src = Path(args.from_path)
    if not src.is_file():
        log(f"[FAIL] 缺少输入清单 {src}；请先跑 diag_block_provenance.py")
        return 3
    prev = json.loads(src.read_text(encoding="utf-8"))
    cases = [c for c in (prev.get("per_case") or []) if c.get("kind") == "never_candidate"]
    if args.limit:
        cases = cases[: args.limit]
    if not cases:
        log("[FAIL] 清单里没有 never_candidate 题")
        return 3
    log(f"[from] never_candidate 题 {len(cases)}")

    settings = get_settings()
    registry = build_plot_registry(settings)
    retr = registry.get(args.character)
    if retr is None:
        log("[FAIL] 剧情图谱未加载")
        return 1
    if getattr(retr, "semantic", None) is None and not args.allow_degraded:
        log("[FAIL] 语义通道已降级（--allow-degraded 可强行继续）")
        return 2

    items = E.load_testset(None)
    by_id = {str(it.get("id")): it for it in items}
    todo = [by_id[str(c["id"])] for c in cases if str(c["id"]) in by_id]
    oracle = E.build_oracle(retr.corpus, todo)
    name_map = D.build_entity_name_map(retr)

    sem = retr.semantic
    # 注意：``sem.hashes`` 是 numpy 数组，不能用 ``or`` 判空（会触发
    # "truth value of an array ... is ambiguous"），必须显式判 None。
    _hashes = sem.hashes
    hashes = [str(h) for h in (_hashes if _hashes is not None else [])]
    vecs = sem.vectors
    mask = getattr(sem, "_mask", None)
    rows = np.flatnonzero(mask) if mask is not None else np.arange(len(hashes))
    log(f"[idx] 语义索引行数 {len(rows)} / 语料 {len(retr.corpus.chunks)} 块"
        f"（mask={'有' if mask is not None else '无'}）")
    n_chunks = len(retr.corpus.chunks)

    sem_hit = {k: 0 for k in KS}
    lex_hit = {k: 0 for k in KS}
    sem_best: list[int] = []
    lex_best: list[int] = []
    gold_has_seed = 0
    gold_has_truth = 0
    per_case: list[dict] = []

    t0 = time.time()
    for i, item in enumerate(todo, start=1):
        qid = str(item.get("id"))
        q = str(item.get("q") or "")
        ent = oracle.get(qid) or {}
        full = set(ent.get("full") or set())
        gold = full if full else set(ent.get("any") or set())
        if not gold:
            continue
        seeds = retr.seed_gate(retr.link_detailed(q))
        truth, _ = D.truth_entities_for_item(item, ent, retr.corpus, name_map)
        seed_names = {n for eid in seeds for n in name_map.get(str(eid), []) if len(n) >= 2}
        truth_names = {n for eid in truth for n in name_map.get(str(eid), []) if len(n) >= 2}

        # Q1 语义全库排名：直接对索引全量打分（不经过候选池截断）
        qvec = D.embed_with_retry(retr, q)
        sem_rank = None
        if qvec is not None and vecs is not None and len(rows):
            qn = np.asarray(qvec, dtype=np.float32)
            qn = qn / (np.linalg.norm(qn) or 1.0)
            sims = vecs[rows] @ qn
            order = np.argsort(-sims)
            ranked = [hashes[rows[j]] for j in order]
            pos = {h: r for r, h in enumerate(ranked, start=1)}
            cand = [pos[h] for h in gold if h in pos]
            sem_rank = min(cand) if cand else None

        # Q2 BM25 全库排名：一次取满，看 gold 落在第几位（不在列表 = 零命中）
        lex_rank = None
        try:
            hits = retr.corpus.search(q, len(retr.corpus.chunks))
            for r, (c, _s) in enumerate(hits, start=1):
                if str(getattr(c, "hash", "")) in gold:
                    lex_rank = r
                    break
        except Exception as exc:  # noqa: BLE001
            log(f"  [warn] {qid} 词法检索异常：{exc!r}")

        if sem_rank:
            sem_best.append(sem_rank)
            for k in KS:
                if sem_rank <= min(k, len(rows)):
                    sem_hit[k] += 1
        if lex_rank:
            lex_best.append(lex_rank)
            for k in KS:
                if lex_rank <= min(k, n_chunks):
                    lex_hit[k] += 1

        # Q3 mention 通道可达性：gold 块文本里有没有种子 / 真阳实体的名字
        has_seed = False
        has_truth_name = False
        for h in list(gold)[:20]:
            chunk = retr.corpus.by_hash(str(h))
            if chunk is None:
                continue
            text = chunk.text or ""
            if any(nm in text for nm in seed_names):
                has_seed = True
            if any(nm in text for nm in truth_names):
                has_truth_name = True
            if has_seed and has_truth_name:
                break
        gold_has_seed += int(has_seed)
        gold_has_truth += int(has_truth_name)

        per_case.append({
            "id": qid, "q": q, "n_gold": len(gold), "n_seeds": len(seeds),
            "semantic_best_rank": sem_rank, "lexical_best_rank": lex_rank,
            "gold_has_seed_name": has_seed, "gold_has_truth_name": has_truth_name,
        })
        if i % 15 == 0:
            log(f"  [progress] {i}/{len(todo)}｜已用 {time.time() - t0:.0f}s")

    n = max(1, len(per_case))
    report: dict[str, Any] = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "source": str(args.from_path),
        "counts": {"never_candidate": len(per_case),
                   "indexed_chunks": int(len(rows)), "corpus_chunks": n_chunks},
        "semantic_top_k_hit": {str(k): {"n": sem_hit[k], "rate": D.rate(sem_hit[k], n)}
                               for k in KS},
        "semantic_best_rank_quantiles": D.quantiles([float(x) for x in sem_best]),
        "lexical_top_k_hit": {str(k): {"n": lex_hit[k], "rate": D.rate(lex_hit[k], n)}
                              for k in KS},
        "lexical_best_rank_quantiles": D.quantiles([float(x) for x in lex_best]),
        "mention_reachability": {
            "gold_has_seed_name": gold_has_seed,
            "gold_has_seed_name_rate": D.rate(gold_has_seed, n),
            "gold_has_truth_name": gold_has_truth,
            "gold_has_truth_name_rate": D.rate(gold_has_truth, n),
        },
        "per_case": per_case,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    log("\n==== 摘要 ====")
    log(f"never_candidate 题 {len(per_case)}｜语义索引 {len(rows)} 块｜语料 {n_chunks} 块")
    log("Q1 语义全库 best_rank 命中率：")
    for k in KS:
        log(f"  top-{k:<5} {sem_hit[k]:3d}  ({D.rate(sem_hit[k], n)})")
    log(f"  分位：{json.dumps(report['semantic_best_rank_quantiles'], ensure_ascii=False)}")
    log("Q2 BM25 全库 best_rank 命中率：")
    for k in KS:
        log(f"  top-{k:<5} {lex_hit[k]:3d}  ({D.rate(lex_hit[k], n)})")
    log(f"  分位：{json.dumps(report['lexical_best_rank_quantiles'], ensure_ascii=False)}")
    log(f"Q3 mention 可达性：gold 块含种子名 {gold_has_seed}/{n}"
        f"｜含真阳名 {gold_has_truth}/{n}")
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
