# -*- coding: utf-8 -*-
"""打印 _85_lexfirst_diag.json 的 LOST/GAINED 汇总表（供人读）。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
P = Path("data/compendium_rag/reports/_85_lexfirst_diag.json")
d = json.loads(P.read_text(encoding="utf-8"))


def show(tag: str) -> None:
    print("=" * 104)
    print(tag)
    print("=" * 104)
    for q, r in d[tag].items():
        print(f"=== {q}  {r['query']}")
        print(f"    v6rank={r['v6_rank']}  lfrank={r['lf_rank']}  "
              f"v6_gold={r['v6_gold_chunk']}  gold_own_lex_rank={r['v6_gold_chunk_lex_rank']}")
        print(f"    lex top3 scores={r['lex_top3_scores']}  gap(s1-s2)/s1={r['lex_gap_s1s2']}")
        for h in r["hoisted"]:
            print(f"      lex#{h['lex_rank']:<2} sc={h['lex_score']:<9} gold={str(h['is_gold']):<5} "
                  f"v6fused#{h['v6_fused_rank']}  {h['chunk_id']}")
        print(f"    v6_top6_gold={r['v6_top6_gold']}")
        print(f"    lf_top6_gold={r['lf_top6_gold']}")


show("lost")
show("gained")
print("\n=== mechanism ===")
for m in d["checks"]["mechanism"]:
    print(f"  {m['qid']}: v6rank={m['v6_rank']} gold_lex_rank={m['gold_lex_rank']} "
          f"hoisted_all_nongold={m['hoisted_all_nongold']} hoisted_gold={m['hoisted_gold_count']} "
          f"hoisted_in_v6={m['n_hoisted_present_in_v6']}")
