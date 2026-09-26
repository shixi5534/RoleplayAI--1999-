# -*- coding: utf-8 -*-
"""题集 i · 阶段 3 收尾：读 eval5_set_i.json，产出预注册闸门表（Markdown 就绪）。

不重新检索（Ollama 零占用）——纯离线汇总 _iset_eval5.py 已落盘的 rows。
输出：L1(T1) 主口径五臂表 + McNemar + up/down + L2 报告 + grounded 安全线。
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "data/compendium_rag/reports/eval5_set_i.json"
ARMS = ("empty", "random", "alias", "vector", "strong")


def mcnemar(rows_a, rows_b, key):
    ba = {r["qid"]: r[key] for r in rows_a}
    bb = {r["qid"]: r[key] for r in rows_b}
    b = sum(1 for q in ba if ba[q] and not bb.get(q))
    c = sum(1 for q in ba if not ba[q] and bb.get(q))
    n = b + c
    if n == 0:
        return b, c, 1.0
    m = min(b, c)
    p = min(1.0, 2 * sum(math.comb(n, i) for i in range(m + 1)) * (0.5 ** n))
    return b, c, p


def flips(rows_a, rows_b, key):
    ba = {r["qid"]: r[key] for r in rows_a}
    bb = {r["qid"]: r[key] for r in rows_b}
    up = sorted(q for q in ba if ba[q] and not bb.get(q))
    down = sorted(q for q in ba if not ba[q] and bb.get(q))
    return up, down


def metric(rows):
    n = len(rows)
    if not n:
        return dict(n=0, hit6=None, hit10=None, mrr=None, gnd=None)
    return dict(n=n,
                hit6=round(sum(r["hit6"] for r in rows) / n, 4),
                hit10=round(sum(r["hit10"] for r in rows) / n, 4),
                mrr=round(sum(r["rr"] for r in rows) / n, 4),
                gnd=all(r["grounded"] for r in rows))


def _rows(rows, arm, mode):
    """容错取 rows：partial 报告里某臂某模式可能尚未落盘，返回 []。"""
    return (rows.get(arm) or {}).get(mode) or []


def main() -> int:
    r = json.loads(REPORT.read_text(encoding="utf-8"))
    rows = r["rows"]  # {arm: {mode: [row,...]}}
    arms = [a for a in ARMS if _rows(rows, a, "full")]

    print("# 题集 i 五臂闸门表（full 模式，L1=_pool T1 主口径）\n")
    print(f"partial={r.get('partial')}  n_cases={r.get('n_cases')}\n")
    print("| 臂 | n | hit@6 | hit@10 | MRR | grounded |")
    print("|---|---|---|---|---|---|")
    for a in arms:
        l1 = [x for x in _rows(rows, a, "full") if x["pool"] == "T1"]
        m = metric(l1)
        print(f"| {a} | {m['n']} | {m['hit6']} | **{m['hit10']}** | {m['mrr']} | {m['gnd']} |")

    if _rows(rows, "strong", "full"):
        s = [x for x in _rows(rows, "strong", "full") if x["pool"] == "T1"]
        sm = metric(s)
        print(f"\n## 闸门\n")
        print(f"- [ ] L1 全量 hit@10 ≥ 0.70：{sm['hit10']}")
        if _rows(rows, "empty", "full"):
            e = [x for x in _rows(rows, "empty", "full") if x["pool"] == "T1"]
            em = metric(e)
            gain = round((sm["hit10"] - em["hit10"]) * 100, 2)
            b, c, p = mcnemar(s, e, "hit10")
            up, down = flips(s, e, "hit10")
            print(f"- strong−empty = {gain:+.2f}pt（需 ≥ +5）；"
                  f"McNemar b={b} c={c} p={p:.4f}（需 <0.05）")
            print(f"  - up({len(up)}): {', '.join(up)}")
            print(f"  - down({len(down)}): {', '.join(down)}")
        if _rows(rows, "random", "full"):
            rj = [x for x in _rows(rows, "random", "full") if x["pool"] == "T1"]
            rm = metric(rj)
            b2, c2, p2 = mcnemar(s, rj, "hit10")
            print(f"- strong−random = {round((sm['hit10']-rm['hit10'])*100,2):+.2f}pt "
                  f"（需 >0，即强模型优于随机）；McNemar vs random p={p2:.4f}")
        print(f"- grounded=1.000 全臂：{all(metric([x for x in _rows(rows, a, 'full') if x['pool']=='T1'])['gnd'] for a in arms)}")

    # graph_only 对照 + L2 报告
    print("\n## graph_only 模式（对照，非主口径）\n")
    print("| 臂 | L1 hit@6 | L1 hit@10 |")
    print("|---|---|---|")
    for a in arms:
        go = _rows(rows, a, "graph_only")
        if not go:
            continue
        l1 = [x for x in go if x["pool"] == "T1"]
        m = metric(l1)
        print(f"| {a} | {m['hit6']} | {m['hit10']} |")

    print("\n## L2（MULTI 2-hop + T2i）仅报告\n")
    print("| 臂 | MULTI hit@10 | T2i hit@10 |")
    print("|---|---|---|")
    for a in arms:
        full = _rows(rows, a, "full")
        mu = metric([x for x in full if x["pool"] == "MULTI"])
        t2 = metric([x for x in full if x["pool"] == "T2i"])
        print(f"| {a} | {mu['hit10']} (n={mu['n']}) | {t2['hit10']} (n={t2['n']}) |")
    return 0


if __name__ == "__main__":
    sys.exit(main())
