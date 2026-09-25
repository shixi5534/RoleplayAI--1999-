# -*- coding: utf-8 -*-
"""P1-1（块级中文翻译索引）收益上限测算 —— **只读诊断，不改任何数据**。

为什么必须先测这个：
    语料主体是英文 ASR，提问是中文。P1-1 的前提假设是「中文查 → 证据在英文块」
    造成失分，所以需要给英文块建中文翻译索引。
    但如果失分题的证据块**本来就是中文**，那跨语言根本不是瓶颈，
    P1-1 就是无的放矢 —— 与其花几小时建索引，不如先花两分钟证伪。

    （前车之鉴：别名桥 v2 做完 39 条才发现 96 个缺口组里 95 个题面不含实体名，
      方向在原理上就无效。本脚本就是为了不再重演一次。）

做法：
    1. 对每题算出 oracle 命中块（单块覆盖全部证据组 = full），标语言 zh/en
    2. 跑一次检索，得到 strict_pass / inject_pass
    3. 交叉统计：失分题的证据块语言分布 ⇒ P1-1 可覆盖的失分题上限

用法：
    .venv/Scripts/python.exe -X utf8 scripts/diag_lang_headroom.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import eval_plot_rag as E  # noqa: E402
from roleplay.config import get_settings  # noqa: E402
from roleplay.core.knowledge.factory import build_plot_registry  # noqa: E402

AUDIT = ROOT / "data" / "knowledge" / "_audit"
TESTSET = AUDIT / "rag_testset_300_clean.json"
BUDGET = 2400


def lang_of(text: str) -> str:
    try:
        return E.detect_lang(text)
    except Exception:  # pragma: no cover
        n = sum(1 for ch in text[:2000] if "\u4e00" <= ch <= "\u9fff")
        return "zh" if n / max(len(text[:2000]), 1) > 0.1 else "en"


def main() -> int:
    import builtins
    _buf: list[str] = []
    _real = builtins.print  # 不能写 `print`：下面 def print 会把它变成局部变量

    def print(*a, **k):  # noqa: A001
        _buf.append(" ".join(str(x) for x in a))
        _real(*a, **k)

    cases = json.loads(TESTSET.read_text(encoding="utf-8"))
    s = get_settings()
    retr = build_plot_registry(s).get("wu_ming_zhe")

    # 语料语言分布（一次性）
    corpus_lang = Counter(lang_of(c.text) for c in retr.corpus.chunks)
    hash_lang = {c.hash: lang_of(c.text) for c in retr.corpus.chunks}

    print(f"语料块数 {len(retr.corpus.chunks)}｜语言分布 "
          f"zh={corpus_lang.get('zh', 0)} en={corpus_lang.get('en', 0)}")

    oracle = E.build_oracle(retr.corpus, cases)
    top = int(getattr(s, "plot_max_chunks", 3))
    lf = int(getattr(s, "plot_lexical_fallback", 2))
    print(f"检索参数 top={top} lexical_fallback={lf} budget={BUDGET}")

    rows = []
    for item in cases:
        row = E.evaluate_case(retr, item, oracle[str(item["id"])], top, lf, BUDGET)
        full = oracle[str(item["id"])]["full"]
        langs = Counter(hash_lang.get(h, "en") for h in full)
        if not full:
            bucket = "no_oracle"
        elif langs.get("en", 0) and not langs.get("zh", 0):
            bucket = "en_only"      # 证据只在英文块 ⇒ P1-1 理论上能救
        elif langs.get("zh", 0) and not langs.get("en", 0):
            bucket = "zh_only"      # 证据已在中文块 ⇒ P1-1 对此题无用
        else:
            bucket = "mixed"        # 两种都有 ⇒ 存在中文可答块，非纯跨语言问题
        rows.append({
            "id": item.get("id"),
            "q": item.get("q"),
            "bucket": bucket,
            "n_full": len(full),
            "strict": bool(row.get("strict_pass")),
            "inject": bool(row.get("inject_pass")),
        })

    # 交叉统计
    print()
    print("=" * 74)
    print(f"{'证据块语言':<12}{'题数':>6}{'strict失败':>12}{'inject失败':>12}")
    tot_strict_fail = sum(1 for r in rows if not r["strict"])
    tot_inject_fail = sum(1 for r in rows if not r["inject"])
    for b in ("zh_only", "mixed", "en_only", "no_oracle"):
        sub = [r for r in rows if r["bucket"] == b]
        if not sub:
            continue
        sf = sum(1 for r in sub if not r["strict"])
        inf = sum(1 for r in sub if not r["inject"])
        print(f"{b:<12}{len(sub):>6}{sf:>12}{inf:>12}")
    print("-" * 74)
    print(f"{'合计':<12}{len(rows):>6}{tot_strict_fail:>12}{tot_inject_fail:>12}")
    print("=" * 74)

    en_fail = [r for r in rows if r["bucket"] == "en_only" and not r["inject"]]
    print(f"\nP1-1 收益上限：inject 失分 {tot_inject_fail} 题中，"
          f"证据只在英文块的 = {len(en_fail)} 题 "
          f"（即使 P1-1 完美生效，inject_pass 上限 +{len(en_fail) / len(rows) * 100:.2f} pt）")
    mixed_fail = [r for r in rows if r["bucket"] == "mixed" and not r["inject"]]
    print(f"  其中 mixed（已有中文可答块却仍失分）= {len(mixed_fail)} 题 "
          f"⇒ 说明失分主因不是跨语言")

    out = AUDIT / "diag_lang_headroom.json"
    out.write_text(json.dumps({
        "corpus_lang": dict(corpus_lang),
        "params": {"top": top, "lexical_fallback": lf, "budget": BUDGET},
        "tot_inject_fail": tot_inject_fail,
        "en_only_fail": len(en_fail),
        "mixed_fail": len(mixed_fail),
        "rows": rows,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[save] {out.relative_to(ROOT)}")
    (AUDIT / "_lang_summary.txt").write_text("\n".join(_buf), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
