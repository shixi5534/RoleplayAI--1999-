# -*- coding: utf-8 -*-
"""失败题「正解块归属」诊断（只读诊断，不改检索行为）。

为什么需要这个脚本
-------------------
``diag_seed_quality.py`` 实测：失败 105 题里「种子含真阳仍失败」占 68 题，
远大于「无种子」的 5 题。也就是说主战场不是"没种子"，而是**种子对了也拿不回正解块**。

但要修它，必须先分清三种完全不同的失效模式（修法互不通用）：

  A. **never_candidate**：正解块**从未进入任何通道的候选池** → 召回面问题
     （通道根本没取到，改融合/预算/重排都没用）。
  B. **candidate_but_squeezed**：正解块进过候选池，但**没进最终 top-N** → 排序/预算问题
     （这是「救援兜底」想修的那一类；若实测占比很小，就解释了它为什么"无害但无效"）。
  C. **in_final_but_still_fail**：正解块**进了最终结果**仍判 FAIL → 判定口径问题
     （证据组含同场景共现冗余组 / 组装预算截断），修检索毫无意义。

方法：用实例级 spy 包住 ``PlotGraphRetriever._fuse_channels``，捕获**融合前**各通道
候选池（edge/mention/semantic/chapter/lexical，含名次）与**融合后**入选名单。
选融合层做观测点，是因为它是所有通道唯一的汇合处——在别处观测都要么拿不到全部通道，
要么读到的是被裁剪后的结果。

正解块定义（两口径并列，不允许混用）：
  - ``full``：单块覆盖**全部**证据组的块（最严格，主口径）；
  - ``any``：覆盖任一证据组的块（full 为空时的替代口径，报告中单独标注）。

用法（项目根目录）
------------------
    .venv/Scripts/python.exe -X utf8 scripts/diag_block_provenance.py
    .venv/Scripts/python.exe -X utf8 scripts/diag_block_provenance.py --limit 20   # 冒烟

输入：默认读 ``data/knowledge/_audit/diag_seed_quality_20260917.json`` 的逐题 pass 标记
      （避免重复跑一遍全量判定；缺失时本脚本自行判定全部题目）。
产物：``data/knowledge/_audit/diag_block_provenance.json`` + 同名 ``.log``
退出码：0 正常｜1 环境/数据缺失｜2 语义通道降级
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from roleplay.config import get_settings  # noqa: E402
from roleplay.core.knowledge.factory import build_plot_registry  # noqa: E402

import diag_seedless_ceiling as D  # noqa: E402
import eval_plot_rag as E  # noqa: E402

DEFAULT_OUT = ROOT / "data" / "knowledge" / "_audit" / "diag_block_provenance.json"
DEFAULT_FROM = ROOT / "data" / "knowledge" / "_audit" / "diag_seed_quality_20260917.json"
CHANNELS = ("edge", "mention", "semantic", "chapter", "lexical")

_LOG: list[str] = []


def log(msg: str) -> None:
    print(msg, flush=True)
    _LOG.append(str(msg))


def main() -> int:
    ap = argparse.ArgumentParser(description="失败题正解块归属诊断（只读）")
    ap.add_argument("--character", default="wu_ming_zhe")
    ap.add_argument("--from", dest="from_path", default=str(DEFAULT_FROM),
                    help="已有逐题 pass 标记的 JSON（缺则自行跑全量判定）")
    ap.add_argument("--limit", type=int, default=0, help="只处理前 N 个失败题（冒烟）")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--allow-degraded", action="store_true")
    args = ap.parse_args()

    out_path = Path(args.out)
    log_path = out_path.with_suffix(out_path.suffix + ".log")

    settings = get_settings()
    registry = build_plot_registry(settings)
    retr = registry.get(args.character)
    if retr is None:
        log(f"[FAIL] 剧情图谱未加载（{args.character}）")
        return 1
    degraded = getattr(retr, "semantic", None) is None
    if degraded and not args.allow_degraded:
        log("[FAIL] 语义通道已降级，拒绝出报告（--allow-degraded 可强行继续）")
        return 2

    top = int(getattr(settings, "plot_max_chunks", 3) or 3)
    lex_fb = int(getattr(settings, "plot_lexical_fallback", 2) or 0)
    items = E.load_testset(None)
    by_id = {str(it.get("id")): it for it in items}

    # ── 失败题清单：优先复用已有画像结果，避免重复跑一遍全量判定 ──────────────
    fail_ids: list[str] = []
    src = Path(args.from_path)
    if src.is_file():
        prev = json.loads(src.read_text(encoding="utf-8"))
        fail_ids = [str(c["id"]) for c in (prev.get("per_case") or []) if not c.get("pass")]
        log(f"[from] 复用 {src.name}：失败题 {len(fail_ids)}")
    if not fail_ids:
        log("[from] 无可用画像结果，改为自行判定全量（较慢）")
        oracle_all = E.build_oracle(retr.corpus, items)
        for it in items:
            row = E.evaluate_case(retr, it, oracle_all[str(it.get("id"))], top, lex_fb, 0)
            if not row.get("strict_pass"):
                fail_ids.append(str(it.get("id")))
        log(f"[scan] 失败题 {len(fail_ids)}/{len(items)}")
    if args.limit:
        fail_ids = fail_ids[: args.limit]
    fail_items = [by_id[i] for i in fail_ids if i in by_id]
    log(f"[todo] 待诊断失败题 {len(fail_items)}｜top={top}｜lexical_fallback={lex_fb}")

    oracle = E.build_oracle(retr.corpus, fail_items)

    # ── 观测点：融合层（所有通道唯一汇合处）─────────────────────────────────
    cap: dict[str, Any] = {"channels": [], "fused": []}
    orig_fuse = retr._fuse_channels

    def spy(channels, *, limit):
        cap["channels"] = [
            (str(path), [str(getattr(c, "hash", "") or "") for _s, c, _m in items])
            for path, _w, items in channels
        ]
        out = orig_fuse(channels, limit=limit)
        cap["fused"] = [str(getattr(c, "hash", "") or "") for _s, c, _m in out]
        return out

    retr._fuse_channels = spy  # 实例级遮蔽，不污染类与其他检索器

    buckets = {"never_candidate": 0, "candidate_but_squeezed": 0,
               "in_final_but_still_fail": 0, "no_full_ceiling": 0}
    chan_hit: dict[str, int] = {c: 0 for c in CHANNELS}
    chan_unique: dict[str, int] = {c: 0 for c in CHANNELS}
    per_case: list[dict] = []

    t0 = time.time()
    for i, item in enumerate(fail_items, start=1):
        qid = str(item.get("id"))
        ent = oracle.get(qid) or {}
        full = set(ent.get("full") or set())
        any_set = set(ent.get("any") or set())
        truth = full if full else any_set
        used_any_fallback = not full
        cap["channels"], cap["fused"] = [], []
        try:
            retr.retrieve(str(item.get("q") or ""), top_chunks=top, lexical_fallback=lex_fb)
        except Exception as exc:  # noqa: BLE001 - 单题异常不得中断整轮诊断
            log(f"  [warn] {qid} retrieve 异常：{exc!r}")
            continue

        chan_ranks: dict[str, int | None] = {}
        providers: list[str] = []
        for path, hashes in cap["channels"]:
            rank = next((r for r, h in enumerate(hashes, start=1) if h in truth), None)
            chan_ranks[path] = rank
            if rank is not None:
                providers.append(path)
                chan_hit[path] = chan_hit.get(path, 0) + 1
        if len(providers) == 1:
            chan_unique[providers[0]] = chan_unique.get(providers[0], 0) + 1
        in_final = any(h in truth for h in cap["fused"])
        # 口径纪律：**先分「有没有 full 正解块」，再谈归属**。
        # full 为空的题（语料里不存在单块覆盖全部证据组的块）用 any 兜底后，
        # "正解块进了 final 却仍 FAIL" 是**必然**的——那不是检索问题，是语料天花板。
        # 混进主口径会把结论带偏（冒烟 15 题里 5/15 属此类，占比 33%，足以颠倒主次）。
        if not full:
            kind = "no_full_ceiling"
            buckets["no_full_ceiling"] += 1
        elif in_final:
            kind = "in_final_but_still_fail"
            buckets["in_final_but_still_fail"] += 1
        elif providers:
            kind = "candidate_but_squeezed"
            buckets["candidate_but_squeezed"] += 1
        else:
            kind = "never_candidate"
            buckets["never_candidate"] += 1

        per_case.append({
            "id": qid, "q": str(item.get("q") or ""), "kind": kind,
            "gold_any_fallback": used_any_fallback, "n_gold": len(truth),
            "chan_rank": chan_ranks, "providers": providers,
            "in_final": in_final, "n_fused": len(cap["fused"]),
        })
        if i % 25 == 0:
            log(f"  [progress] {i}/{len(fail_items)}｜已用 {time.time() - t0:.0f}s")

    retr._fuse_channels = orig_fuse  # 无论成败都还原，避免污染后续调用

    n = max(1, len(per_case))
    report = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "character": args.character,
        "config": {"top": top, "lexical_fallback": lex_fb, "degraded": degraded,
                   "source": str(args.from_path)},
        "counts": {"fail_diagnosed": len(per_case), **buckets},
        "ratios": {k: D.rate(v, n) for k, v in buckets.items()},
        "channel_candidate_hit": {c: {"n": chan_hit.get(c, 0), "rate": D.rate(chan_hit.get(c, 0), n)}
                                  for c in CHANNELS},
        "channel_unique_provider": chan_unique,
        "per_case": per_case,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    log("\n==== 摘要 ====")
    log(f"诊断失败题 {len(per_case)}")
    for k, v in buckets.items():
        log(f"  {k:26s} {v:4d}  ({D.rate(v, n)})")
    log("各通道候选池含正解块的比例：")
    for c in CHANNELS:
        log(f"  {c:9s} {chan_hit.get(c, 0):4d}  ({D.rate(chan_hit.get(c, 0), n)})")
    log(f"唯一提供者（只有该通道取到正解块）：{chan_unique}")
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
