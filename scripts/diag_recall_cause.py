# -*- coding: utf-8 -*-
"""召回率（recall = 34.17%）归因 —— **只读诊断，不改任何数据**。

recall 在 eval_plot_rag.evaluate_case 里的定义：
    n_full = 返回块中「单块覆盖全部证据组」的块数
    denom  = min(top_chunks, len(full))          # full = 语料中所有可单块作答的块
    recall = min(n_full, denom) / denom          # 无 full 块时记 0

也就是说，recall 低有三种完全不同的原因，混在一起看是没意义的：
    A. 语料里**根本不存在**能单块作答的块（ceiling=False）→ recall 恒为 0，与检索无关
    B. 存在，且被召回到 top-5 → recall 正常
    C. 存在，但在 top-6~30 之间 → **融合/排序把它挤掉了**（可救）
    D. 存在，但连 top-30 都进不去 → **真召回失败**（首跳就没捞到）

本脚本把 300 题分进 A/B/C/D 四桶，并给出每桶对 recall 的损失贡献，
从而回答「34.17% 到底是谁造成的」。

用法：
    .venv/Scripts/python.exe -X utf8 scripts/diag_recall_cause.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import eval_plot_rag as E  # noqa: E402
from roleplay.config import get_settings  # noqa: E402
from roleplay.core.knowledge.factory import build_plot_registry  # noqa: E402

AUDIT = ROOT / "data" / "knowledge" / "_audit"
TESTSET = AUDIT / "rag_testset_300_clean.json"
TOP_DEEP = 30         # 深挖上限：用来判断证据块到底在不在候选池里
BUDGET = 2400
# ⚠️ 生产 top 不能硬编码：.env 里 ROLEPLAY_PLOT_MAX_CHUNKS=6，
#    再加 plot_lexical_fallback 默认 2 ⇒ 实际返回 8 块（实测平均 7.89 块与此吻合）。
#    早期注释写的「3+2=5」已过期，硬编码会低估生产召回能力。


def main() -> int:
    # PowerShell 重定向会把 stdout 写成 UTF-16（Read 读出来是二进制），
    # 所以这里把同样的内容再写一份 UTF-8 文件，保证结果可读。
    import builtins
    _buf: list[str] = []
    _real = builtins.print   # 不能写 `print`：下面 def print 会把它变成局部变量

    def print(*a, **k):  # noqa: A001
        _buf.append(" ".join(str(x) for x in a))
        _real(*a, **k)

    cases = json.loads(TESTSET.read_text(encoding="utf-8"))
    s = get_settings()
    retr = build_plot_registry(s).get("wu_ming_zhe")
    oracle = E.build_oracle(retr.corpus, cases)

    top_prod = int(getattr(s, "plot_max_chunks", 6))
    lf_prod = int(getattr(s, "plot_lexical_fallback", 2))
    n_prod = top_prod + lf_prod
    print(f"[cfg] 生产口径：plot_max_chunks={top_prod} + lexical_fallback={lf_prod}"
          f" = 返回上限 {n_prod} 块")

    rows = []
    for item in cases:
        qid = str(item["id"])
        full = oracle[qid]["full"]
        # denom 与 evaluate_case 对齐：只用 plot_max_chunks（不含词法兜底）
        denom = min(top_prod, len(full)) if full else 0

        # ⚠️ RetrievedChunk 没有 hash / id 字段（只有 text/score/metadata），
        #    必须用与 oracle 同一套文本指纹 chunk_hash(text) 才能比对。
        ch5 = retr.retrieve(item["q"], top_chunks=top_prod, lexical_fallback=lf_prod)
        h5 = [E.chunk_hash(c.text) for c in ch5]
        n_full_5 = sum(1 for h in h5 if h in full)
        recall_5 = (min(n_full_5, denom) / denom) if denom else 0.0

        ch30 = retr.retrieve(item["q"], top_chunks=TOP_DEEP, lexical_fallback=0)
        h30 = [E.chunk_hash(c.text) for c in ch30]
        rank30 = next((i + 1 for i, h in enumerate(h30) if h in full), 0)
        n_full_30 = sum(1 for h in h30 if h in full)
        denom30 = min(TOP_DEEP, len(full)) if full else 0
        recall_30 = (min(n_full_30, denom30) / denom30) if denom30 else 0.0

        if not full:
            bucket = "A_no_ceiling"
        elif n_full_5 >= 1:
            bucket = "B_top5"
        elif rank30:
            bucket = "C_squeezed"     # 在 top-6~30 ⇒ 被融合/排序挤掉
        else:
            bucket = "D_recall_fail"  # 连 top-30 都没有 ⇒ 真召回失败

        rows.append({
            "id": qid, "q": item.get("q"), "bucket": bucket,
            "n_full": len(full), "n_full_5": n_full_5, "n_full_30": n_full_30,
            "rank_in_30": rank30, "recall_5": recall_5, "recall_30": recall_30,
            "len_ch30": len(ch30),
        })

    n = len(rows)
    mean_r5 = sum(r["recall_5"] for r in rows) / n
    mean_r30 = sum(r["recall_30"] for r in rows) / n

    cnt = {b: sum(1 for r in rows if r["bucket"] == b)
           for b in ("A_no_ceiling", "B_top5", "C_squeezed", "D_recall_fail")}
    sumr = {b: sum(r["recall_5"] for r in rows if r["bucket"] == b) / n
            for b in cnt}

    print("=" * 78)
    print(f"题量 {n}｜生产 top={top_prod}+{lf_prod}｜深挖 top={TOP_DEEP}")
    print(f"recall（生产口径）  = {mean_r5:.4f}")
    print(f"recall（深挖 top-30）= {mean_r30:.4f}   ← 若显著更高，说明损失来自截断/排序")
    print("=" * 78)
    print(f"{'桶':<16}{'题数':>6}{'占比':>9}{'对recall的贡献':>16}{'桶内均值':>10}")
    label = {"A_no_ceiling": "A 无单块可答", "B_top5": "B 已进入top5",
             "C_squeezed": "C 被挤到6~30", "D_recall_fail": "D 真召回失败"}
    for b in ("A_no_ceiling", "B_top5", "C_squeezed", "D_recall_fail"):
        c = cnt[b]
        inner = (sumr[b] / (c / n)) if c else 0.0
        print(f"{label[b]:<16}{c:>6}{c / n:>8.1%}{sumr[b]:>16.4f}{inner:>10.4f}")
    print("-" * 78)
    print(f"{'合计':<16}{n:>6}{1.0:>8.1%}{mean_r5:>16.4f}")
    print("=" * 78)

    c_cnt = cnt["C_squeezed"]
    ranks = [r["rank_in_30"] for r in rows if r["bucket"] == "C_squeezed"]
    if ranks:
        ranks.sort()
        print(f"\nC 桶（被挤掉）{c_cnt} 题的证据块名次分布："
              f" 中位 {ranks[len(ranks)//2]}｜最小 {ranks[0]}｜最大 {ranks[-1]}")
        print(f"  其中名次 6~10 的：{sum(1 for x in ranks if x <= 10)} 题"
              f"（只需把 top 从 5 放宽到 10 就能救回）")

    print(f"\n结论口径：A 桶 {cnt['A_no_ceiling']} 题的 recall 是**指标定义**导致的 0，"
          f"不是检索失败；真正可救的是 C 桶 {c_cnt} 题。")
    print(f"若把 A 桶剔除，剩余 {n - cnt['A_no_ceiling']} 题的 recall 为 "
          f"{sum(r['recall_5'] for r in rows if r['bucket'] != 'A_no_ceiling') / max(n - cnt['A_no_ceiling'], 1):.4f}")

    out = AUDIT / "diag_recall_cause.json"
    out.write_text(json.dumps({
        "params": {"top_prod": top_prod, "lexical_fallback": lf_prod,
                   "top_deep": TOP_DEEP, "budget": BUDGET},
        "recall_prod": mean_r5, "recall_deep": mean_r30,
        "counts": cnt, "contrib": sumr, "rows": rows,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[save] {out.relative_to(ROOT)}")
    (AUDIT / "_recall_run.txt").write_text("\n".join(_buf), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
