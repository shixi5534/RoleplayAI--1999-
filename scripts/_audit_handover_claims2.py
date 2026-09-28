# -*- coding: utf-8 -*-
"""独立复核（第二轮）：锁定「分子/分母口径」错配与陈旧工件，产出订正值。"""
from __future__ import annotations

import json
from pathlib import Path

R = Path("data/compendium_rag/reports")


def rows_of(f: str) -> list[dict]:
    return json.loads((R / f).read_text(encoding="utf-8"))["rows"]


def table(f: str, label: str) -> None:
    p = R / f
    if not p.exists():
        print(f"  [缺] {label} ({f})")
        return
    rows = rows_of(f)
    full = [r for r in rows if r.get("mode") == "full"]
    ans = [r for r in full if r.get("answerable")]
    un = [r for r in full if not r.get("answerable")]
    h_all = sum(1 for r in full if r.get("hit"))
    h_ans = sum(1 for r in ans if r.get("hit"))
    h_un = sum(1 for r in un if r.get("hit"))
    na, nu = len(ans), len(un)
    print(f"  {label:26} {f}")
    print(f"      answerable {h_ans}/{na} = {h_ans/na:.4f}   |  raw full {h_all}/{len(full)}"
          f"   |  不可答命中 {h_un}/{nu}")
    if h_un:
        qs = [r["qid"] for r in un if r.get("hit")]
        print(f"      ⚠ 分子含不可答命中 -> 若用 {h_all}/{na} = {h_all/na:.4f} 则虚高 "
              f"{h_all-h_ans} 题 {qs}")


print("=" * 90)
print("① 逐文件「同一 run、两种口径」对照（这是 0.8418/0.8469 之争的根源）")
print("=" * 90)
for f, l in [("eval_300cn_v6_tb_lexoff.json", "300cn lex=0 (tiebreak后)"),
             ("eval_300cn_lex_on.json", "300cn lex=1 lex_on(旧)"),
             ("eval_300cn_lex_tiebreak.json", "300cn lex=1 tiebreak(新)"),
             ("eval_300cn_lexfirst.json", "300cn lex_first=3"),
             ("eval_blind_lex_on.json", "盲测 lex_on(旧)"),
             ("eval_blind_lex_tiebreak.json", "盲测 tiebreak(新)"),
             ("eval_blind_lexfirst.json", "盲测 lex_first=3"),
             ("eval_blind_lex_off.json", "盲测 lex=0")]:
    table(f, l)

print()
print("=" * 90)
print("② hit 字段语义：hit 是否 == rank<=6？（用 rr 反推）")
print("=" * 90)
for f in ["eval_300cn_lex_tiebreak.json", "eval_blind_lex_tiebreak.json"]:
    rows = rows_of(f)
    full = [r for r in rows if r.get("mode") == "full"]
    rrs = sorted({r.get("rr") for r in full if r.get("hit")})
    print(f"  {f}: 命中题的 rr 取值集合（前12）={rrs[:12]}")
    hit_gt6 = [r for r in full if r.get("hit") and r.get("rr") and 1.0 / r["rr"] > 6]
    print(f"      命中但 rank>6 的题数 = {len(hit_gt6)}  -> hit 字段口径 = "
          f"{'hit@6' if not hit_gt6 else 'hit@top_k(含>6)'}")

print()
print("=" * 90)
print("③ baseline_v6.json 锁定工件 vs 其声称数字（300cn 裸检索）")
print("=" * 90)
b = json.loads((R / "baseline_v6.json").read_text(encoding="utf-8"))
s = b["secondary_300cn"]
print(f"  声称 lex_on_bare_hit6 = {s['lex_on_bare_hit6']['rate']}"
      f" ({s['lex_on_bare_hit6']['hits']}/{s['lex_on_bare_hit6']['n']})")
print(f"  声称 graph_only      = {s['lex_on_graph_only']['rate']}"
      f" ({s['lex_on_graph_only']['hits']}/{s['lex_on_graph_only']['n']})")
print(f"  声称 生产口径(重排)   = {s['production_rerank_hit6']}")
print("  锁定键 -> 实际文件:")
for k in b["artifact_sha256_16"]:
    print(f"      {k}")
print("  ⚠ eval_300cn_lex_on.json（被锁定）answerable 命中 = 164/196 = 0.8367，"
      "不等于声称的 0.8418")
print("  ⚠ 支持 0.8418 的是 eval_300cn_lex_tiebreak.json，但它**不在锁内**")
print("  ⚠ 锁键 eval_300cn_lex_off 实际映射到 eval_blind_lex_off.json（盲测文件），"
      "真正的 eval_300cn_lex_off.json 不存在")

print()
print("=" * 90)
print("④ 盲测两笔 run 区分（0.8786 vs 0.8592）")
print("=" * 90)
acc = json.loads((R / "baseline_v6_acceptance.json").read_text(encoding="utf-8"))
a = acc["blind206 (留出集)"]
print(f"  [v6 现行] baseline_v6_acceptance.json  裸={a['bare_hit6']} 生产={a['rerank_hit6']} "
      f"up={a['up']} down={a['down']}  -> 172+{a['up']}-{a['down']}="
      f"{172+a['up']-a['down']} -> {(172+a['up']-a['down'])/206:.4f}")
d = json.loads((R / "frozen_prod_on_blindfinal.json").read_text(encoding="utf-8"))["blind_final(206)"]
print(f"  [R5 陈旧] frozen_prod_on_blindfinal.json 裸={d['baseline_hit6']} 生产={d['frozen_hit6']} "
      f"up={d['up']} down={d['down']}  -> 132+{d['up']}-{d['down']}="
      f"{132+d['up']-d['down']} -> {(132+d['up']-d['down'])/206:.4f}")
print("  → 交接文档 §3.1「盲测 0.8786（177→实际 up=46/down=1）」把两笔 run 拼接：")
print("     177 与 up=46/down=1 属于 0.8592（R5 期）；0.8786 的 up/down 是 10/1")
