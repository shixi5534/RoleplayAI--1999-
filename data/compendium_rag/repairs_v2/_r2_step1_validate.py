# -*- coding: utf-8 -*-
"""R2-repairer step 1: recompute DF, validate predecessor scratch, fill gaps.

Read-only on graph.json/chunks.json/testset/triage/lexicons.
Outputs to repairs_v2/_r2_items_full.json (working data, NOT the proposal).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]  # .../roleplay-ai
OUT_DIR = REPO / "data/compendium_rag/repairs_v2"

# ── faithful copy of retriever._name_matches (audit precedent; avoids heavy imports) ──
def _name_matches(name: str, ql: str) -> bool:
    if not name or not ql:
        return False
    is_ascii = all(ord(c) < 128 for c in name)
    if is_ascii:
        pat = re.compile(r"(?<![A-Za-z0-9_])" + re.escape(name.lower()) +
                         r"(?![A-Za-z0-9_])")
        return bool(pat.search(ql))
    if len(name) >= 2:
        return name in ql
    return bool(re.search(r"(?<![\u4e00-\u9fff])" + re.escape(name) +
                          r"(?![\u4e00-\u9fff])", ql))


def main() -> None:
    # ── load corpus blobs ──
    chunks = json.loads((REPO / "data/compendium_rag/chunks.json").read_text(encoding="utf-8"))["chunks"]
    n_chunks = len(chunks)
    texts = [c["text"] for c in chunks]
    cid = [c["chunk_id"] for c in chunks]
    print(f"chunks: {n_chunks}", file=sys.stderr)

    # ── load graph, rebuild alias_index exactly like GraphStore._rebuild ──
    graph = json.loads((REPO / "data/compendium_rag/graph.json").read_text(encoding="utf-8"))
    ents = graph["entities"]
    alias_index: dict[str, str] = {}
    for e in ents:
        alias_index[e["name"]] = e["eid"]          # canonical: direct set
    for e in ents:
        for a in e["aliases"]:
            alias_index.setdefault(a, e["eid"])    # alias: first owner wins
    print(f"entities: {len(ents)}  alias_index keys: {len(alias_index)}", file=sys.stderr)

    ent_by_name = {e["name"]: e for e in ents}
    # owner chunk sets (for overlap analysis)
    owner_chunks: dict[str, set[str]] = {e["name"]: set(e["chunk_ids"]) for e in ents}

    # ── DF over chunk blobs ──
    # blob rule: DF(alias) = #{chunks : alias is a raw substring of chunk['text']}, all 3695 blobs
    all_keys = sorted(set(alias_index.keys()) | set(e["name"] for e in ents))
    df: dict[str, int] = {}
    for k in all_keys:
        df[k] = sum(1 for t in texts if k in t)
    print(f"DF computed for {len(df)} strings", file=sys.stderr)

    # ── declared aliases (deduped) ──
    declared: dict[str, list[str]] = {}   # alias -> owners in entity order
    for e in ents:
        for a in e["aliases"]:
            declared.setdefault(a, []).append(e["name"])
    hi = sorted([(a, df[a]) for a in declared if df[a] >= 50], key=lambda x: -x[1])
    print(f"declared aliases: {len(declared)}  distinct; DF>=50: {len(hi)}", file=sys.stderr)

    # ── load predecessor scratch ──
    prev = json.loads((OUT_DIR / "_scratch_items.json").read_text(encoding="utf-8"))
    prev_items = prev["items"]
    prev_df = prev["df_map"]
    prev_canon = prev["canon"]

    # validate predecessor DF
    diffs = [(k, prev_df[k], df.get(k)) for k in prev_df if prev_df.get(k) != df.get(k)]
    print(f"predecessor df_map entries: {len(prev_df)}  DF mismatches vs recompute: {len(diffs)}",
          file=sys.stderr)
    if diffs:
        for k, a, b in diffs[:20]:
            print(f"  MISMATCH {k}: prev={a} mine={b}", file=sys.stderr)

    # predecessor item coverage vs the 58-list
    prev_alias_set = set(prev_items.keys())
    hi_set = {a for a, _ in hi}
    print(f"58-list covered by predecessor items: {len(hi_set & prev_alias_set)}/{len(hi_set)}",
          file=sys.stderr)
    print(f"predecessor extras (not in 58-list): {sorted(prev_alias_set - hi_set)}", file=sys.stderr)
    print(f"58-list missing from predecessor: {sorted(hi_set - prev_alias_set)}", file=sys.stderr)

    # ── testset ──
    ts = json.loads((REPO / "data/knowledge/_audit/rag_testset_300_cn.json").read_text(encoding="utf-8"))["cases"]
    queries = [(t["id"], t["q"], t["q"].lower()) for t in ts]

    # ── lexicons (offline wiki standard) ──
    lex = json.loads((REPO / "data/lore/wu_ming_zhe/huiji_lexicon.json").read_text(encoding="utf-8"))
    zh2en: dict[str, list[str]] = lex["zh2en"]
    canon = json.loads((REPO / "data/lore/wu_ming_zhe/huiji_canon.json").read_text(encoding="utf-8"))
    wiki_zh_names: set[str] = set(zh2en.keys())
    for grp in ("characters", "npcs"):
        for row in canon[grp]:
            if isinstance(row, dict) and row.get("zh"):
                wiki_zh_names.add(row["zh"])

    # ── per-item build for 58-list + predecessor extras ──
    pool = sorted(hi_set | prev_alias_set)
    out: dict[str, dict] = {}
    for alias in pool:
        e: dict = {}
        e["df"] = df[alias]
        owners = declared.get(alias, [])
        e["owners"] = owners
        # owner info (prefer recomputed; fall back to predecessor extras for canonical names)
        if owners:
            o = ent_by_name[owners[0]]
            e["owner_type"] = o["type"]
            e["owner_desc"] = o["desc"]
            e["owner_nchunks"] = len(o["chunk_ids"])
            e["owner_degree"] = None  # filled later if needed
            e["owner_aliases"] = o["aliases"]
            claimed = owner_chunks[owners[0]]
        else:
            e["owner_type"] = e["owner_desc"] = None
            e["owner_nchunks"] = e["owner_degree"] = None
            e["owner_aliases"] = []
            claimed = set()
        # DF∩owner-claimed + unrelated samples
        hits = [(cid[i], t) for i, t in enumerate(texts) if alias in t]
        df_cids = [h[0] for h in hits]
        e["df_chunks_in_owner_claims"] = sum(1 for c in df_cids if c in claimed) if owners else None
        e["grounded_in_owner"] = (any(alias in t for i, t in
                                      [(i, texts[i]) for i in range(n_chunks)]
                                      ) and
                                  any(alias in t for c, t in
                                      zip(cid, texts) if c in claimed)) if owners else None
        unrelated = [(c, t) for c, t in hits if c not in claimed]
        e["df_unrelated"] = len(unrelated)
        samples = []
        for c, t in unrelated[:3]:
            p = t.find(alias)
            s = t[max(0, p - 60):p + len(alias) + 60].replace("\n", "⏎")
            samples.append({"chunk_id": c, "snip": s})
        e["unrelated_samples"] = samples
        # testset link check
        e["testset_hits"] = [[qid, q] for qid, q, ql in queries if _name_matches(alias, ql)]
        # wiki offline lexicon
        e["wiki_zh2en"] = zh2en.get(alias)
        e["wiki_zh_name"] = alias in wiki_zh_names
        out[alias] = e

    # ── canonical bare-generic nodes (10) ──
    canon_nodes = ["伙计", "猎人", "小孩", "教师", "管理员", "水手", "警卫", "店主", "卫兵", "信众"]
    canon_out = {}
    for nm in canon_nodes:
        e = ent_by_name.get(nm)
        c = {"df": df[nm], "exists_in_graph": e is not None}
        if e:
            claimed = set(e["chunk_ids"])
            docs = sorted({c0.split(":")[0] for c0 in e["chunk_ids"]})
            c.update({"type": e["type"], "desc": e["desc"], "nchunks": len(e["chunk_ids"]),
                      "aliases": e["aliases"], "docs": docs,
                      "name_ground": any(nm in texts[i] for i in range(n_chunks)
                                         if cid[i] in claimed)})
            # name-contains candidates: other entities whose name contains this generic word
            subs = [(x["name"], len(x["chunk_ids"])) for x in ents
                    if nm in x["name"] and x["name"] != nm]
            c["name_contains_entities"] = sorted(subs, key=lambda x: -x[1])[:12]
            c["wiki_zh_name"] = nm in wiki_zh_names
            c["wiki_zh2en"] = zh2en.get(nm)
            # sample snips (3)
            hits = [(cid[i], texts[i]) for i in range(n_chunks) if nm in texts[i]]
            c["df_sample_snips"] = [t[max(0, t.find(nm) - 60):t.find(nm) + len(nm) + 60]
                                    .replace("\n", "⏎") for _, t in hits[:3]]
        canon_out[nm] = c

    res = {
        "blob_rule": "DF(s) = #{chunk of 3695 in chunks.json : s is raw substring of chunk['text']}",
        "alias_index_rule": "canonical name -> direct set; aliases -> setdefault in entity list order",
        "n_chunks": n_chunks,
        "declared_aliases_distinct": len(declared),
        "df_ge50_declared": [[a, d] for a, d in hi],
        "df_map_mismatch_count": len(diffs),
        "prev_extras": sorted(prev_alias_set - hi_set),
        "prev_missing": sorted(hi_set - prev_alias_set),
        "items": out,
        "canon_nodes": canon_out,
        "testset_n": len(queries),
        "wiki_zh_names_count": len(wiki_zh_names),
    }
    (OUT_DIR / "_r2_items_full.json").write_text(json.dumps(res, ensure_ascii=False, indent=1),
                                                 encoding="utf-8")
    print("wrote _r2_items_full.json", file=sys.stderr)


if __name__ == "__main__":
    main()
