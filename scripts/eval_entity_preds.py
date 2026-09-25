# -*- coding: utf-8 -*-
"""评估 agent 的实体识别：准确率 + 接入检索后的实际收益。

两件事
    ① 识别准确率：预测的实体是否命中该题 evidence（含中英别名归一）
    ② 接入收益：把预测实体追加到 query 后，A 类 67 题的 inject/strict/top2 变化
       —— 这才是「实体识别有没有用」的最终判据

匹配规则（中英归一）
    把 evidence 关键词与预测名都归一到「名称组」：canon 的 zh↔en + lexicon 的 zh↔en。
    例如 evidence ['Apeiron','阿派朗'] 与预测 'Apeiron' 视为命中。

用法：.venv/Scripts/python.exe -X utf8 scripts/eval_entity_preds.py
"""
from __future__ import annotations

import json
import sys
import time
import traceback
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import eval_plot_rag as E  # noqa: E402
from roleplay.config import get_settings  # noqa: E402
from roleplay.core.knowledge.factory import build_plot_registry  # noqa: E402

AUDIT = ROOT / "data" / "knowledge" / "_audit"
LOG = AUDIT / "_entity_eval.txt"
HB = AUDIT / "_entity_eval_heartbeat.txt"
BUDGET = 2400


def beat(m: str) -> None:
    with HB.open("a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%H:%M:%S')} {m}\n")


def norm_key(s: str) -> str:
    return " ".join(str(s).strip().lower().split())


def build_groups() -> dict[str, set[str]]:
    """名字 -> 该实体的全部等价名（中英互译 + 大小写归一）。"""
    g: dict[str, set[str]] = {}

    def add(a: str, b: str) -> None:
        a, b = norm_key(a), norm_key(b)
        if not a or not b:
            return
        s = g.setdefault(a, set())
        s.add(a)
        s.add(b)
        g.setdefault(b, set()).update(s)

    canon_p = ROOT / "data" / "lore" / "wu_ming_zhe" / "huiji_canon.json"
    if canon_p.is_file():
        c = json.loads(canon_p.read_text(encoding="utf-8"))
        for key in ("characters", "npcs"):
            for it in c.get(key) or []:
                zh, en = str(it.get("zh") or ""), str(it.get("en") or "")
                if zh and en:
                    add(zh, en)
    lex_p = ROOT / "data" / "lore" / "wu_ming_zhe" / "huiji_lexicon.json"
    if lex_p.is_file():
        lx = json.loads(lex_p.read_text(encoding="utf-8"))
        for key in ("zh2en", "en2zh"):
            for a, b in (lx.get(key) or {}).items():
                for x in (b if isinstance(b, (list, tuple)) else [b]):
                    add(a, str(x))
    return g


def main() -> int:
    out: list[str] = []
    HB.write_text(f"start {time.strftime('%H:%M:%S')}\n", encoding="utf-8")

    def p(*a):
        line = " ".join(str(x) for x in a)
        out.append(line)
        print(line, flush=True)

    preds = json.loads((AUDIT / "entity_preds_agent.json").read_text(encoding="utf-8"))
    P = preds["preds"]
    groups = build_groups()
    cases = {str(c["id"]): c for c in
             json.loads((AUDIT / "rag_testset_300_clean.json").read_text(encoding="utf-8"))}
    rank = json.loads((AUDIT / "positive_rank.json").read_text(encoding="utf-8"))
    a_ids = [str(r["id"]) for r in rank if r.get("verdict") == "A_不在候选池"]
    beat(f"目标 {len(a_ids)} 题")

    def expand(names) -> set[str]:
        s: set[str] = set()
        for n in names:
            k = norm_key(n)
            s.add(k)
            s.update(groups.get(k, set()))
        return s

    # —— ① 准确率 ——
    hit = miss = 0
    by_conf: dict[str, list[int]] = {}
    by_src: dict[str, list[int]] = {}
    rows: list[dict] = []
    for qid in a_ids:
        item = cases.get(qid)
        pr = P.get(qid)
        if not item or not pr:
            continue
        gold: set[str] = set()
        for g in (item.get("evidence") or []):
            gold.update(expand(g if isinstance(g, list) else [g]))
        picked = expand(pr.get("picks") or [])
        ok = bool(gold & picked)
        hit += int(ok)
        miss += int(not ok)
        by_conf.setdefault(pr.get("conf", "?"), []).append(int(ok))
        by_src.setdefault(pr.get("src", "?"), []).append(int(ok))
        rows.append({"id": qid, "picks": pr.get("picks"), "conf": pr.get("conf"),
                     "src": pr.get("src"), "hit": ok,
                     "gold": sorted(gold)[:4]})

    n = hit + miss
    p("=" * 86)
    p(f"① 实体识别准确率｜agent（强模型）vs 本地 qwen2.5:7b（此前 15.0%）")
    p("=" * 86)
    p(f"  命中 {hit}/{n} = **{hit / max(n, 1):.1%}**")
    p()
    p(f"  {'置信度':<10}{'题数':>6}{'命中率':>10}")
    for k in ("high", "mid", "low"):
        v = by_conf.get(k)
        if v:
            p(f"  {k:<10}{len(v):>6}{sum(v) / len(v):>10.1%}")
    p()
    p(f"  {'来源':<12}{'题数':>6}{'命中率':>10}")
    for k, v in sorted(by_src.items()):
        p(f"  {k:<12}{len(v):>6}{sum(v) / len(v):>10.1%}")

    # —— ② 接入收益 ——
    s = get_settings()
    retr = build_plot_registry(s).get("wu_ming_zhe")
    oracle = E.build_oracle(retr.corpus, list(cases.values()))
    top = int(getattr(s, "plot_max_chunks", 6))
    lf = int(getattr(s, "plot_lexical_fallback", 2))
    sub = [cases[q] for q in a_ids if q in cases]

    agg = {"b_inject": 0, "x_inject": 0, "b_strict": 0, "x_strict": 0,
           "b_top2": 0, "x_top2": 0}
    t0 = time.time()
    for i, item in enumerate(sub):
        if i % 15 == 0:
            beat(f"ab {i}/{len(sub)}")
        qid = str(item["id"])
        full = oracle[qid]["full"]
        picks = (P.get(qid) or {}).get("picks") or []
        item2 = dict(item)
        item2["q"] = f"{item['q']} {' '.join(picks)}".strip() if picks else item["q"]

        cap: dict[str, list] = {}

        def grab(tag):
            def f(q, chunks):
                cap[tag] = chunks
                return chunks
            return f

        rb = E.evaluate_case(retr, item, oracle[qid], top, lf, BUDGET,
                             chunks_transform=grab("b"))
        rx = E.evaluate_case(retr, item2, oracle[qid], top, lf, BUDGET,
                             chunks_transform=grab("x"))
        for k, r, c in (("b", rb, "b"), ("x", rx, "x")):
            agg[f"{k}_inject"] += bool(r.get("inject_pass"))
            agg[f"{k}_strict"] += bool(r.get("strict_pass"))
            agg[f"{k}_top2"] += any(E.chunk_hash(cc.text) in full
                                    for cc in (cap.get(c) or [])[:2])

    m = len(sub)
    p()
    p("=" * 86)
    p(f"② 接入收益（A 类 {m} 题）—— 把预测实体追加到 query")
    p("=" * 86)
    p(f"  {'指标':<14}{'不用预测':>12}{'用预测':>12}{'Δ':>12}")
    for k, label in (("inject", "inject_pass"), ("strict", "strict_pass"),
                     ("top2", "top2_hit")):
        b, x = agg[f"b_{k}"] / m, agg[f"x_{k}"] / m
        p(f"  {label:<14}{b:>12.4f}{x:>12.4f}{x - b:>+12.4f}")
    p("=" * 86)
    p(f"  耗时 {(time.time() - t0) / 60:.1f} min")

    p()
    p("逐题明细（前 25 条）：")
    for r in rows[:25]:
        mark = "✅" if r["hit"] else "❌"
        p(f"  {mark} {r['id']:<6}{r['conf']:<6}{r['src']:<10}"
          f"选中={r['picks']}  真值={r['gold']}")

    LOG.write_text("\n".join(out), encoding="utf-8")
    (AUDIT / "entity_eval.json").write_text(json.dumps({
        "n": n, "hit": hit, "acc": hit / max(n, 1), "rows": rows,
        "ab": {k: v / m for k, v in agg.items()},
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    beat("完成")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except BaseException:  # noqa: BLE001
        with LOG.open("a", encoding="utf-8") as f:
            f.write("\n[TRACEBACK]\n" + traceback.format_exc())
        raise
