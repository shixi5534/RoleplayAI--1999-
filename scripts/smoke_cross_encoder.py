# -*- coding: utf-8 -*-
"""Cross-Encoder 正确性冒烟 —— 必须排除「跑通了但没用」的伪通过。

检查四件事：
    1. 模型能加载，且**输入名**符合预期（不同 ONNX 导出变体可能不同）
    2. 打分**方向正确**：相关文档分数 > 无关文档分数
    3. 打分**不是常数**（伪通过最常见的形态：模型加载出错但被 fallback 成同一个值）
    4. 在**真实题集**上能否把 oracle 证据块往前挪 —— 这是唯一有意义的信号

用法：
    .venv/Scripts/python.exe -X utf8 scripts/smoke_cross_encoder.py
    .venv/Scripts/python.exe -X utf8 scripts/smoke_cross_encoder.py --file onnx/model.onnx
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
sys.path.insert(0, str(ROOT / "scripts"))

import eval_plot_rag as E  # noqa: E402
from roleplay.config import get_settings  # noqa: E402
from roleplay.core.knowledge.factory import build_plot_registry  # noqa: E402
from roleplay.core.knowledge.plot_rerank import CrossEncoderReranker  # noqa: E402

AUDIT = ROOT / "data" / "knowledge" / "_audit"
TESTSET = AUDIT / "rag_testset_300_clean.json"
MODEL_DIR = ROOT / "models" / "bge-reranker-base-onnx"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default="onnx/model_int8.onnx")
    ap.add_argument("--n", type=int, default=30, help="真实题集取样量")
    ap.add_argument("--pool", type=int, default=20)
    args = ap.parse_args()

    out_lines: list[str] = []

    def p(*a):
        line = " ".join(str(x) for x in a)
        out_lines.append(line)
        print(line, flush=True)

    t0 = time.time()
    rr = CrossEncoderReranker(model_dir=str(MODEL_DIR), onnx_file=args.file,
                              max_len=512, max_chars=1200)
    if not rr.available():
        p(f"[FATAL] 模型加载失败：{rr.last_error}")
        (AUDIT / "_ce_smoke.txt").write_text("\n".join(out_lines), encoding="utf-8")
        return 2
    p(f"[1] 加载成功 {args.file}｜输入 {getattr(rr, '_input_names', '?')}"
      f"｜耗时 {time.time() - t0:.1f}s")

    # —— 2/3：方向与常数检查 ——
    q = "暴雨是什么？"
    rel = ("暴雨是重塑世界的一种神秘现象，1999年最后一天开始出现，"
           "会让一切回到过去的某个时间点。")
    irr = ("他端起茶杯喝了一口，随后转身离开了房间，外面的雨下得很大但与他无关。")
    s_rel = rr.score_pair(q, rel)
    s_irr = rr.score_pair(q, irr)
    p(f"[2] 方向检查：相关 {s_rel:.4f} vs 无关 {s_irr:.4f} → "
      f"{'✅ 正确' if s_rel > s_irr else '❌ 反了'}（差 {s_rel - s_irr:.4f}）")

    many = [rr.score_pair(q, f"候选片段 {i}：天气、时间与记忆的变化。" if i % 3 else rel)
            for i in range(12)]
    spread = max(many) - min(many)
    p(f"[3] 非常数检查：12 次打分极差 {spread:.4f} → "
      f"{'✅ 有区分度' if spread > 1e-3 else '❌ 疑似常数/恒定输出'}")
    if s_rel <= s_irr or spread <= 1e-3:
        p("⇒ 冒烟未通过，停止后续实验")
        (AUDIT / "_ce_smoke.txt").write_text("\n".join(out_lines), encoding="utf-8")
        return 2

    # —— 4：真实题集上能否把证据块往前挪 ——
    cases = json.loads(TESTSET.read_text(encoding="utf-8"))[: args.n]
    s = get_settings()
    retr = build_plot_registry(s).get("wu_ming_zhe")
    oracle = E.build_oracle(retr.corpus, cases)
    top_prod = int(getattr(s, "plot_max_chunks", 6))
    lf_prod = int(getattr(s, "plot_lexical_fallback", 2))

    def rank_of(chunks, full):
        for i, c in enumerate(chunks, 1):
            if E.chunk_hash(c.text) in full:
                return i
        return 0

    moved = kept = lost = 0
    before_ranks: list[int] = []
    after_ranks: list[int] = []
    lat: list[float] = []
    for item in cases:
        full = oracle[str(item["id"])]["full"]
        if not full:
            continue
        base = retr.retrieve(item["q"], top_chunks=top_prod, lexical_fallback=lf_prod)
        rb = rank_of(base, full)

        pool = retr.retrieve(item["q"], top_chunks=args.pool, lexical_fallback=0)
        t1 = time.perf_counter()
        items = [(float(getattr(c, "score", 0.0) or 0.0), c, {}) for c in pool]
        out = rr.rerank(item["q"], items, top_k=top_prod + lf_prod)
        lat.append((time.perf_counter() - t1) * 1000)
        ra = rank_of([c for _s, c, _m in out], full)

        if rb:
            before_ranks.append(rb)
        if ra:
            after_ranks.append(ra)
        if rb and ra:
            if ra < rb:
                moved += 1
            elif ra == rb:
                kept += 1
            else:
                lost += 1
        elif ra and not rb:
            moved += 1

    p()
    p(f"[4] 真实题集（前 {len(cases)} 题，pool={args.pool} → keep={top_prod + lf_prod}）")
    p(f"    重排后名次  前进 {moved} 题｜不变 {kept} 题｜后退 {lost} 题")
    if before_ranks:
        p(f"    证据块名次中位：{statistics.median(before_ranks):.1f} → "
          f"{statistics.median(after_ranks) if after_ranks else 0:.1f}")
    p(f"    单题重排耗时：中位 {statistics.median(lat):.0f} ms｜均值 {statistics.mean(lat):.0f} ms")
    p()
    p("判据：若「前进」明显多于「后退」且名次中位下降 ⇒ 值得跑全量 A/B；")
    p("      否则说明该 Cross-Encoder 对本语料无效，止损。")

    (AUDIT / "_ce_smoke.txt").write_text("\n".join(out_lines), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
