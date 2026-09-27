# -*- coding: utf-8 -*-
"""R2-repairer step 2: decision-support tables.

A) testset queries triggering each item (for false-positive eyeballing)
B) owner alias retention check (post-removal verbatim alias count)
C) qualify-form verification (longer forms verbatim in owner claims)
D) wiki lexicon lookups incl. special cases (门/信/线 etc.)
Outputs _r2_step2.json + prints readable summary.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
OUT_DIR = REPO / "data/compendium_rag/repairs_v2"

def main() -> None:
    full = json.loads((OUT_DIR / "_r2_items_full.json").read_text(encoding="utf-8"))
    items = full["items"]
    graph = json.loads((REPO / "data/compendium_rag/graph.json").read_text(encoding="utf-8"))
    chunks = json.loads((REPO / "data/compendium_rag/chunks.json").read_text(encoding="utf-8"))["chunks"]
    cid = [c["chunk_id"] for c in chunks]
    texts = [c["text"] for c in chunks]
    ents = {e["name"]: e for e in graph["entities"]}

    # ── B) owner alias retention + canonical grounding ──
    removal_candidates = [a for a, v in items.items() if v["owners"]]
    retention = {}
    for alias in removal_candidates:
        owner = items[alias]["owners"][0]
        e = ents[owner]
        claimed = set(e["chunk_ids"])
        blob = "\n".join(t for c, t in zip(cid, texts) if c in claimed)
        al_info = []
        for al in e["aliases"]:
            al_info.append({"alias": al, "verbatim_in_owner": al in blob})
        retention[alias] = {
            "owner": owner,
            "canonical_grounded": e["name"] in blob,
            "owner_aliases_verbatim": al_info,
            "verbatim_alias_count_excl_self": sum(1 for x in al_info
                                                  if x["verbatim_in_owner"] and x["alias"] != alias),
        }

    # ── C) qualify-form verification ──
    qualify_forms = {
        "保罗": "保罗·霍伊默尔",
        "拉普拉斯": "拉普拉斯科算中心",
    }
    qualify_check = {}
    for short, longf in qualify_forms.items():
        owner = items[short]["owners"][0]
        e = ents[owner]
        claimed = set(e["chunk_ids"])
        blob = "\n".join(t for c, t in zip(cid, texts) if c in claimed)
        df_long = sum(1 for t in texts if longf in t)
        qualify_check[longf] = {
            "candidate_for": short, "owner": owner, "df": df_long,
            "verbatim_in_owner": longf in blob,
            "is_alias_or_canonical": longf in e["aliases"] or longf == e["name"],
        }

    # ── D) wiki lexicon special lookups ──
    lex = json.loads((REPO / "data/lore/wu_ming_zhe/huiji_lexicon.json").read_text(encoding="utf-8"))
    zh2en = lex["zh2en"]
    canon = json.loads((REPO / "data/lore/wu_ming_zhe/huiji_canon.json").read_text(encoding="utf-8"))
    wiki_rows = {}
    for grp in ("characters", "npcs"):
        for row in canon[grp]:
            if isinstance(row, dict) and row.get("zh"):
                wiki_rows[row["zh"]] = {"en": row.get("en"), "grp": grp}
    specials = ["信", "门", "线", "基金会", "重塑", "司辰", "拉普拉斯", "伙计", "猎人", "小孩",
                "教师", "管理员", "水手", "警卫", "店主", "卫兵", "信众", "卡森", "老伙计",
                "怪物", "幽灵", "格蕾丝", "阿德勒", "伊万", "莫莉", "保罗", "玛丽", "德洛丝",
                "别斯米尔", "纸信圈儿", "Z", "哑谜"]
    wiki_lookup = {s: {"zh2en": zh2en.get(s), "canon_row": wiki_rows.get(s)} for s in specials}

    res = {"retention": retention, "qualify_check": qualify_check, "wiki_lookup": wiki_lookup}
    (OUT_DIR / "_r2_step2.json").write_text(json.dumps(res, ensure_ascii=False, indent=1),
                                            encoding="utf-8")

    # ── A) print testset queries per item ──
    print("=== testset queries per item (ts>0) ===")
    for a, v in sorted(items.items(), key=lambda kv: -len(kv[1]["testset_hits"])):
        hits = v["testset_hits"]
        if not hits:
            continue
        print(f"\n[{a}] df={v['df']} owner={v['owners']} n_ts={len(hits)}")
        for qid, q in hits:
            print(f"   {qid}: {q}")

    print("\n\n=== retention check (removal candidates) ===")
    for a, r in retention.items():
        keep_n = r["verbatim_alias_count_excl_self"]
        cg = r["canonical_grounded"]
        print(f"{a:<10} owner={r['owner']:<10} canon_grounded={cg} "
              f"verbatim_aliases_excl_self={keep_n} "
              f"aliases={[x['alias'] for x in r['owner_aliases_verbatim'] if x['verbatim_in_owner']][:6]}")

    print("\n=== qualify checks ===")
    for lf, c in qualify_check.items():
        print(lf, c)

    print("\n=== wiki lookups ===")
    for s, w in wiki_lookup.items():
        print(f"{s:<8} zh2en={w['zh2en']} canon={w['canon_row']}")


if __name__ == "__main__":
    main()
