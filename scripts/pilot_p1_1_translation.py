# -*- coding: utf-8 -*-
"""P1-1 前提小试：**翻译到底能不能救「中文查 → 英文块」**。

为什么不直接上全量：
    P1-1 全量方案要把 ~8000 个英文块翻译成中文再建独立索引，成本以小时计。
    在投入之前，先用**最小的代价验证前提**——如果翻译根本提升不了匹配度，
    全量方案就是纯浪费。（前车之鉴：别名桥 v2 做完才发现方向原理上无效。）

做法（只针对 en_only 失分题，共 60 道）：
    1. 取该题的 oracle 证据块（语料里确实能作答的块）
    2. 用 qwen2.5:7b 把它翻译成中文
    3. 用 bge-m3 算三组相似度：
         t  = sim(中文提问, 原英文块)     ← 现状
         t' = sim(中文提问, 译后中文块)   ← P1-1 生效后
         c  = sim(中文提问, 实际检索到的第 1 块)  ← 现状的胜者
    4. 判据：P1-1 要有效，必须 t' > c（译后才排得进前 2）

⚠️ 局限说明（避免过读）：
    这里用的是 **oracle 块**（已知正确），是刻意的——本脚本只验证
    「翻译能否提升跨语言匹配度」这一**前提**，不声称能提升多少检索指标。
    前提若不成立，后面一步都不必做。

用法：
    .venv/Scripts/python.exe -X utf8 scripts/pilot_p1_1_translation.py
    .venv/Scripts/python.exe -X utf8 scripts/pilot_p1_1_translation.py --n 20
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import eval_plot_rag as E  # noqa: E402
from roleplay.config import get_settings  # noqa: E402
from roleplay.core.knowledge.factory import build_plot_registry  # noqa: E402

AUDIT = ROOT / "data" / "knowledge" / "_audit"
OLLAMA = "http://localhost:11434"
TRANS_MODEL = "qwen2.5:7b"
EMBED_MODEL = "bge-m3"
MAX_CHARS = 700


def _post(path: str, payload: dict, timeout: float = 180.0) -> dict:
    req = urllib.request.Request(
        f"{OLLAMA}{path}", data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def embed(text: str) -> list[float]:
    d = _post("/api/embed", {"model": EMBED_MODEL, "input": text}, timeout=60.0)
    return d["embeddings"][0]


def translate(text: str) -> str:
    prompt = ("把下面的英文游戏剧情文本翻译成简体中文。只输出译文，不要任何解释：\n\n"
              + text)
    d = _post("/api/generate", {"model": TRANS_MODEL, "prompt": prompt,
                                "stream": False,
                                "options": {"temperature": 0.0, "num_predict": 900}},
              timeout=300.0)
    return str(d.get("response") or "").strip()


def cos(a: list[float], b: list[float]) -> float:
    import math
    s = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(x * x for x in b)) or 1.0
    return s / (na * nb)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=60)
    args = ap.parse_args()

    outs: list[str] = []

    def p(*a):
        line = " ".join(str(x) for x in a)
        outs.append(line)
        print(line, flush=True)

    lang = json.loads((AUDIT / "diag_lang_headroom.json").read_text(encoding="utf-8"))
    fails = [r for r in (lang.get("rows") or [])
             if r.get("bucket") == "en_only" and not r.get("inject")][: args.n]
    cases = {str(c.get("id")): c for c in
             json.loads((AUDIT / "rag_testset_300_clean.json").read_text(encoding="utf-8"))}

    s = get_settings()
    retr = build_plot_registry(s).get("wu_ming_zhe")
    oracle = E.build_oracle(retr.corpus, list(cases.values()))
    by_hash = {E.chunk_hash(c.text): c.text for c in retr.corpus.chunks}
    top_prod = int(getattr(s, "plot_max_chunks", 6))
    lf_prod = int(getattr(s, "plot_lexical_fallback", 2))

    p("=" * 80)
    p(f"P1-1 前提小试｜en_only 失分题 {len(fails)} 道｜翻译 {TRANS_MODEL}｜向量 {EMBED_MODEL}")
    p("=" * 80)

    d_sim: list[float] = []      # t' - t
    wins = 0
    tried = 0
    rows: list[dict] = []
    t_all = time.time()
    for r in fails:
        qid = str(r.get("id"))
        item = cases.get(qid)
        if not item:
            continue
        full = oracle[qid]["full"] or oracle[qid]["any"]
        if not full:
            continue
        h = next(iter(sorted(full)))
        orig = (by_hash.get(h) or "")[:MAX_CHARS]
        if not orig.strip():
            continue
        got = retr.retrieve(item["q"], top_chunks=top_prod, lexical_fallback=lf_prod)
        if not got:
            continue
        try:
            qv = embed(item["q"])
            tv = embed(orig)
            cv = embed(got[0].text[:MAX_CHARS])
            zh = translate(orig)
            if not zh.strip():
                continue
            zhv = embed(zh[:MAX_CHARS])
        except Exception as exc:  # noqa: BLE001
            p(f"  [skip] {qid} {type(exc).__name__}: {str(exc)[:50]}")
            continue
        t0, t1, c0 = cos(qv, tv), cos(qv, zhv), cos(qv, cv)
        d_sim.append(t1 - t0)
        tried += 1
        win = t1 > c0
        wins += int(win)
        rows.append({"id": qid, "sim_orig": t0, "sim_zh": t1, "sim_top1": c0,
                     "delta": t1 - t0, "would_win": win})

    p()
    if not tried:
        p("[FATAL] 没有可评估的样本")
        (AUDIT / "_p1_1_pilot.txt").write_text("\n".join(outs), encoding="utf-8")
        return 1

    p("-" * 80)
    p(f"有效样本 {tried} 题｜耗时 {(time.time() - t_all) / 60:.1f} min")
    p(f"  sim(问, 原英文块) 均值 {statistics.mean([r['sim_orig'] for r in rows]):.4f}")
    p(f"  sim(问, 译后中文) 均值 {statistics.mean([r['sim_zh'] for r in rows]):.4f}")
    p(f"  译后 − 译前       均值 {statistics.mean(d_sim):+.4f}｜中位 {statistics.median(d_sim):+.4f}")
    p(f"  sim(问, 实际第1块) 均值 {statistics.mean([r['sim_top1'] for r in rows]):.4f}")
    p()
    p(f"★ 译后能反超实际第 1 块的：{wins}/{tried} = {wins / tried:.1%}")
    p()
    p("=" * 80)
    p("判定")
    p("=" * 80)
    if wins / tried >= 0.5:
        p("✅ 前提成立：翻译能显著提升跨语言匹配，且多数能反超现有第 1 块")
        p("   ⇒ P1-1 全量方案值得投入（需翻译 ~8000 块并建独立索引）")
    else:
        p("❌ 前提不成立：翻译提升有限，多数仍排不进第 1")
        p("   ⇒ P1-1 全量方案不应投入——成本以小时计，收益看不到")
    p()
    p("⚠️ 本脚本用的是 oracle 块（已知正确），只验证**前提**，不代表最终检索指标。")

    (AUDIT / "_p1_1_pilot.txt").write_text("\n".join(outs), encoding="utf-8")
    (AUDIT / "p1_1_pilot.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1),
                                           encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
