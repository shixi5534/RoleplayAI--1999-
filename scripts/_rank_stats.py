# -*- coding: utf-8 -*-
"""排序实验 · 配对显著性检验（rank_stats）。

对两份报告做逐题配对检验，纯离线、零网关（只读 json，不跑检索）。

输入两种口径，自动识别并归一化为每 (qid, mode) 的
``{hit6, hit10, rr6, rr10}``：
  1) rank_collect 产物（``_rank_collect.py``，行里有 ``rank`` 字段）：
     hit6 = rank<=6，hit10 = rank<=10，rr@k = 1/rank（rank 超窗则 0）。
  2) eval300 式报告（``compendium_rag_eval300.py``，行里只有 hit/rr，
     top_k 取报告级字段）：hit6 = rr>=1/6（即名次<=6）；top_k=10 时
     hit10 = hit；top_k>10 时 hit10 = rr>=1/10；top_k<10 时 hit10 只能取
     hit（**下界**，输出会注明）。rr6/rr10 同理由 rr 阈值截断。

检验：
  - 按共同 qid 配对（同 mode、同 stratum 过滤后）。
  - McNemar 精确双侧：b=base 未中而 cand 命中、c=base 命中而 cand 未中
    （与 _er_report_gates 的 up/down 同序），p = 2·Σ_{i<=min(b,c)} C(n,i)/2^n。
    优先探测 scipy（本 venv 未装则退回 math.comb 手工实现，两者等价）。
  - hit 类指标直接做 McNemar；mrr6 是连续值，McNemar 按 rr6>0 二值化
    （输出注明），主报告为配对 Bootstrap Δ（均值差）百分位 CI。
  - Bootstrap：10k 次有放回重采样（默认，--boot 可调），固定种子可复现。

用法（项目根目录）：
  ./.venv/Scripts/python.exe scripts/_rank_stats.py \
      --base data/compendium_rag/reports/eval_300_cn_after_welds.json \
      --cand  data/compendium_rag/reports/eval_300_cn_after_welds.json
  ./.venv/Scripts/python.exe scripts/_rank_stats.py \
      --base data/compendium_rag/reports/rank_collect_300_cn_top20.json \
      --cand  data/compendium_rag/reports/rank_collect_300_cn_top20.json \
      --metric hit10 --stratum answerable --mode full

退出码：0=完成（含自比 b=c=0 的平凡情形）；输入不合法/配对为空 → 1。
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
EPS = 1e-9
RNG_SEED = 20260926      # 固定种子：Bootstrap 可复现
METRICS = ("hit6", "hit10", "mrr6")
STRATA = ("answerable", "unanswerable", "all")


def load_normalized(path: Path) -> tuple[dict, dict]:
    """读报告 → ({(qid,mode): 归一行}, 元信息)。"""
    d = json.loads(path.read_text(encoding="utf-8"))
    rows = d.get("rows") or []
    if not rows:
        raise SystemExit(f"[FAIL] {path} 没有 rows")
    is_collect = "rank" in rows[0]
    top_k = int(d.get("top_k", 6) or 6)
    out: dict[tuple[str, str], dict] = {}
    for r in rows:
        qid = str(r.get("qid", ""))
        mode = r.get("mode", "")
        if is_collect:
            rank = r.get("rank")
            hit6 = rank is not None and rank <= 6
            hit10 = rank is not None and rank <= 10
            rr6 = 1.0 / rank if (rank is not None and rank <= 6) else 0.0
            rr10 = 1.0 / rank if (rank is not None and rank <= 10) else 0.0
        else:
            rr = float(r.get("rr") or 0.0)
            hit = bool(r.get("hit"))
            hit6 = rr >= 1.0 / 6 - EPS
            if top_k == 10:
                hit10 = hit
            elif top_k > 10:
                hit10 = rr >= 1.0 / 10 - EPS
            else:
                hit10 = hit          # top_k<10：只能给下界
            rr6 = rr if rr >= 1.0 / 6 - EPS else 0.0
            rr10 = rr if rr >= 1.0 / 10 - EPS else 0.0
        out[(qid, mode)] = {"hit6": hit6, "hit10": hit10, "rr6": rr6,
                            "rr10": rr10, "answerable": r.get("answerable")}
    return out, {"kind": "rank_collect" if is_collect else f"eval300式(top_k={top_k})",
                 "top_k": top_k, "rows": len(rows)}


def mcnemar_exact(b: int, c: int) -> float:
    """McNemar 精确双侧 p。优先 scipy（若装了），否则 math.comb 手工实现。"""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    try:
        from scipy.stats import binomtest  # noqa: PLC0415  运行时探测
        return float(binomtest(k, n, 0.5, alternative="two-sided").pvalue)
    except ImportError:
        tail = sum(math.comb(n, i) for i in range(k + 1)) / (2 ** n)
        return min(1.0, 2 * tail)


def bootstrap_ci(va: np.ndarray, vb: np.ndarray, boot: int) -> tuple[float, float]:
    """配对 Bootstrap：Δ = mean(cand) - mean(base) 的百分位 95% CI。"""
    rng = np.random.RandomState(RNG_SEED)
    n = len(va)
    idx = rng.randint(0, n, size=(boot, n))
    d = va[idx].mean(axis=1) - vb[idx].mean(axis=1)
    lo, hi = np.percentile(d, [2.5, 97.5])
    return float(lo), float(hi)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--cand", required=True)
    ap.add_argument("--metric", default="hit6", choices=METRICS)
    ap.add_argument("--stratum", default="answerable", choices=STRATA)
    ap.add_argument("--mode", default="full", choices=["full", "graph_only"])
    ap.add_argument("--boot", type=int, default=10000)
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    def rp(p: str) -> Path:
        x = Path(p)
        return x if x.is_absolute() else ROOT / p

    bp, cp = rp(args.base), rp(args.cand)
    nb, meta_b = load_normalized(bp)
    nc, meta_c = load_normalized(cp)

    def pick(norm: dict) -> tuple[list, list, int]:
        keys, vals = [], []
        skipped = 0
        for (qid, mode), v in norm.items():
            if mode != args.mode:
                continue
            if args.stratum != "all":
                if v["answerable"] is None:
                    skipped += 1
                    continue
                if v["answerable"] != (args.stratum == "answerable"):
                    continue
            keys.append(qid)
            vals.append(v)
        return keys, vals, skipped

    kb_keys, kb_vals, skip_b = pick(nb)
    kc_keys, kc_vals, skip_c = pick(nc)
    common = sorted(set(kb_keys) & set(kc_keys))
    if not common:
        print(f"[FAIL] 无共同 qid：base 有 {len(kb_keys)} 题，cand 有 {len(kc_keys)} 题"
              f"（mode={args.mode} stratum={args.stratum}）")
        return 1
    bmap = dict(zip(kb_keys, kb_vals))
    cmap = dict(zip(kc_keys, kc_vals))

    if args.metric == "mrr6":
        va = np.array([cmap[q]["rr6"] for q in common], dtype=float)
        vb = np.array([bmap[q]["rr6"] for q in common], dtype=float)
        mcn_note = "McNemar 按 rr6>0 二值化（mrr6 为连续值）"
        bin_c = [cmap[q]["rr6"] > 0 for q in common]
        bin_b = [bmap[q]["rr6"] > 0 for q in common]
    else:
        va = np.array([1.0 if cmap[q][args.metric] else 0.0 for q in common])
        vb = np.array([1.0 if bmap[q][args.metric] else 0.0 for q in common])
        mcn_note = ""
        bin_c = [bool(cmap[q][args.metric]) for q in common]
        bin_b = [bool(bmap[q][args.metric]) for q in common]

    # b = base 未中而 cand 命中（cand 净胜）；c = base 命中而 cand 未中
    b = sum(1 for x, y in zip(bin_b, bin_c) if y and not x)
    c = sum(1 for x, y in zip(bin_b, bin_c) if x and not y)
    p = mcnemar_exact(b, c)
    lo, hi = bootstrap_ci(va, vb, max(1, args.boot))
    delta = float(va.mean() - vb.mean())

    unit = args.metric
    lines = [
        f"# 排序配对显著性 · base={bp.name} cand={cp.name}", "",
        f"- 口径：metric={unit}  stratum={args.stratum}  mode={args.mode}  "
        f"boot={args.boot}",
        f"- 归一化：base={meta_b['kind']} cand={meta_c['kind']}"
        + ("  ⚠ base/cand 的 top_k<10，hit10 为下界"
           if args.metric == "hit10" and (meta_b["top_k"] < 10 or meta_c["top_k"] < 10)
           else ""),
        f"- 配对 n={len(common)}（按 qid；base 弃 {skip_b} 行无 answerable 标记，"
        f"cand 弃 {skip_c} 行）",
        f"- base={vb.mean():.4f}  cand={va.mean():.4f}  Δ={delta:+.4f}",
        f"- McNemar exact（双侧）b={b} c={c} n={b + c} p={p:.5f}"
        + (f"  ← {mcn_note}" if mcn_note else ""),
        f"- Bootstrap 95% CI（Δ，{args.boot} 次重采样，seed={RNG_SEED}）："
        f"[{lo:+.4f}, {hi:+.4f}]", "",
        "| 指标 | base | cand | Δ | b | c | p | CI95 |",
        "|---|---|---|---|---|---|---|---|",
        f"| {unit} | {vb.mean():.4f} | {va.mean():.4f} | {delta:+.4f} "
        f"| {b} | {c} | {p:.5f} | [{lo:+.4f}, {hi:+.4f}] |", "",
        "b/c 约定：b=base 未中而 cand 命中（cand 净胜），c=base 命中而 cand 未中",
    ]
    text = "\n".join(lines) + "\n"
    print(text)
    if args.out:
        op = Path(args.out) if Path(args.out).is_absolute() else ROOT / args.out
        op.parent.mkdir(parents=True, exist_ok=True)
        op.write_text(text, encoding="utf-8")
        print(f"[written] {op}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
