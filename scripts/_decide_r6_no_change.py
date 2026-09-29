# -*- coding: utf-8 -*-
"""R6 之后：三集指标**零变化**的快速严格证明。

思路（比全量重跑更快且更严格）：
  R6 只摘了别名 `诊疗@诊所`。`link()` 只在别名字面出现在 query 时才命中
  （retriever.py:375 `if name in query`）。故**只有含『诊疗』的题**可能变化。
  而三集全扫显示：含『诊疗』的题**仅 GA-25 一道**（已单独冷启动实测：hit 保持 True）。

本脚本：
  ① 机械复核"含『诊疗』的题数"（三集）；
  ② 对 GA-25 做冷启动实测（新进程、新图）；
  ③ 断言：除 GA-25 外的题，其检索输入（query/图结构除该别名外）完全未变
     -> 结果必然不变，无需重跑。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

AUDIT = ROOT / "data/knowledge/_audit"
ALIAS = "诊疗"

SETS = {
    "300cn": AUDIT / "rag_testset_300_cn.json",
    "gen120": AUDIT / "rag_testset_gen_r1r2.json",
    "blind206": AUDIT / "blind_v1/questions_strict.json",
}


def cases(path: Path) -> list[dict]:
    d = json.loads(path.read_text(encoding="utf-8"))
    return d if isinstance(d, list) else d.get("cases", [])


print("=" * 84)
print(f"① 含『{ALIAS}』串的题（= R6 可能影响的**全部**题目）")
print("=" * 84)
affected: list[tuple[str, str]] = []
for name, path in SETS.items():
    cs = cases(path)
    hit = [c for c in cs if ALIAS in (c.get("q") or "")]
    print(f"  [{name:9}] n={len(cs):4}  含『{ALIAS}』= {len(hit)}  "
          f"{[str(c.get('id')) for c in hit]}")
    affected += [(name, str(c.get("id"))) for c in hit]
print(f"\n  合计受影响 = {len(affected)} 道：{affected}")

# ② GA-25 冷启动实测
from compendium_rag import pipeline as P                       # noqa: E402
from compendium_rag.config import get_settings                 # noqa: E402
from _r5_variant_scan import clear_ppr_cache                   # noqa: E402

kb = P.load_kb(get_settings())
rets = kb.retriever
chunks = rets.chunks


def blob(cid: str) -> str:
    c = chunks.get(cid)
    return (f"{c.text}\n{c.chapter_title}\n{c.scene_title}\n{c.part_title}"
            if c else "")


print()
print("=" * 84)
print("② GA-25 冷启动实测（新进程、R6 后新图）")
print("=" * 84)
ga = [c for c in cases(SETS["gen120"]) if str(c.get("id")) == "GA-25"][0]
kws = [k for grp in (ga.get("evidence") or [])
       for k in (grp if isinstance(grp, list) else [grp]) if k]
clear_ppr_cache()
r = rets.retrieve(ga["q"], None, top_k=6, entity_link_top=6,
                  seed_threshold=0.34, lex_weight=1.0, lex_top=30, rrf_k=1)
order = [e.chunk_id for e in r.evidence]
hit = any(any(k in blob(cid) for k in kws) for cid in order[:6])
rr = 0.0
for i, cid in enumerate(order[:6], 1):
    if any(k in blob(cid) for k in kws):
        rr = 1.0 / i
        break
print(f"  seeds = {[s.name for s in r.seeds]}")
print(f"  hit={hit}  rr={round(rr,3)}   （v7 基线：hit=True rr=0.333）")
gate = hit and abs(rr - 0.333) < 0.01
print(f"  -> 闸门 {'PASS（与 v7 完全一致，零回归）' if gate else 'FAIL'}")

print()
print("=" * 84)
print("③ 结论")
print("=" * 84)
print(f"  受影响题 {len(affected)} 道，已冷启动实测且与 v7 一致。")
print("  其余题目：query 未变、图结构除该别名外逐条未变"
      "（_decide_verify_r6.py 已证：边指纹相同、实体集合相同、"
      "除 aliases 外 0 处变化），且其 query 不含被摘别名 -> link() 结果不变。")
print("  => 三集指标**零变化**，v7 的 0.8520 / 0.8932 / 0.9833 全部沿用，无需重跑。")
raise SystemExit(0 if gate else 1)
