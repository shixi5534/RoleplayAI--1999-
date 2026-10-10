# -*- coding: utf-8 -*-
"""v9-P2 归因二（**只读**）：孤点的关系在缓存里到底有没有？

诊断一（p2_landing_diag）推翻了 P2 的前提：1128 个孤点里 1086 个（96.3%）名字
**逐字在语料里**，名不落地的只有 42 个。所以「清理落地问题」最多治 3.7% 的孤点，
把 ≤0.10 的希望押在别名落地上是押错了地方。

剩下只有两种可能，治法完全相反，必须分开量：

A. **缓存里这个名从来没进过任何关系三元组** → 抽取阶段就只把它当「出场名单」列出来，
   图谱没有依据建边。Track 1 无解（要么补关系 = Track 2 重抽，要么按「一次性提及」
   显式披露），**绝不能为了让分母好看去造边或删节点**。
B. **缓存里有关系、图上却没有对应的边** → 这是构建期的数据丢失（端点解析、自环、
   skip 规则），是 P2 真正该修的 bug。

本脚本判 A/B：拿缓存全部关系端点（含别名解析后的 eid）与图上边集对账。
顺带量两个同源缺口：缓存端点**解析不到任何实体**的（丢边）、以及**非孤点**实体里
关系名不落地但通过别名落地的比例（说明别名通道确实在起作用）。

用法：PYTHONPATH=src .venv/Scripts/python.exe -X utf8 scripts/compendium_rag_p2_cache_rel_diag.py
"""
from __future__ import annotations

import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from compendium_rag import pipeline as P  # noqa: E402
from compendium_rag.config import get_settings  # noqa: E402
from compendium_rag.extract import _norm_name  # noqa: E402
from compendium_rag.graph_store import GraphStore  # noqa: E402

CACHE_DIR = ROOT / "data/compendium_rag/cache"
OUT = ROOT / "data/compendium_rag/reports/p2_cache_rel_diag.json"


def main() -> int:
    s = get_settings()
    g = GraphStore.load(s.graph_path)
    deg: Counter = Counter()
    edge_pairs: set[tuple[str, str]] = set()
    for e in g.edges:
        deg[e.src] += 1
        deg[e.dst] += 1
        edge_pairs.add((e.src, e.dst))
        edge_pairs.add((e.dst, e.src))
    iso = {eid for eid in g.entities if deg[eid] == 0}

    files = sorted(CACHE_DIR.rglob("*.json"))
    n_chunks = 0
    endpoint_mentions: Counter = Counter()      # 归一化端点名 -> 出现次数（按块去重后）
    rel_count = 0
    unresolvable: Counter = Counter()            # 解析不到实体的端点名 -> 次数
    iso_with_rel: dict[str, list[dict]] = defaultdict(list)
    name_by_eid = {eid: ent.name for eid, ent in g.entities.items()}
    # ── 全局丢边量（B 类的真实规模，不只孤点那 65 个）──
    # 边唯一键用 (src, dst, relation)；relation 走 n2 归一化后再比，
    # 才能分清「会新增边」与「只会并进已有边」。
    from compendium_rag.extract import NORMALIZER_VERSION  # noqa: E402
    assert NORMALIZER_VERSION == "n2", NORMALIZER_VERSION
    from compendium_rag.relation_norm import map_relation  # noqa: E402
    edge_triples: set[tuple[str, str, str]] = {
        (e.src, e.relation, e.dst) for e in g.edges}
    global_rows_both = 0
    global_new_triples: set[tuple[str, str, str]] = set()
    global_merge_triples: set[tuple[str, str, str]] = set()
    # 提案脚本要把这些边接上证据，证据得回到缓存块：这里顺手记下 cache key
    new_edge_detail: dict[tuple[str, str, str], dict] = {}
    global_merge_triples: set[tuple[str, str, str]] = set()
    rows_self_loop = 0
    rows_dropped_pred = 0
    new_triples_touch_iso: set[tuple[str, str, str]] = set()

    t0 = time.time()
    for i, p in enumerate(files, 1):
        try:
            o = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        raw = o.get("raw") or {}
        rels = raw.get("relations") or []
        n_chunks += 1
        seen: set[tuple[str, str]] = set()
        for r in rels:
            s_raw, d_raw = r.get("src"), r.get("dst")
            if not s_raw or not d_raw:
                continue
            rel_count += 1
            s_eid = g.resolve(_norm_name(str(s_raw)))
            d_eid = g.resolve(_norm_name(str(d_raw)))
            hit = False
            for nm, eid in ((s_raw, s_eid), (d_raw, d_eid)):
                key = _norm_name(str(nm))
                if eid is None:
                    unresolvable[key] += 1
                    continue
                endpoint_mentions[eid] += 1
                if eid in iso and not hit:
                    iso_with_rel[eid].append({
                        "src": str(s_raw), "dst": str(d_raw),
                        "rel": str(r.get("relation") or ""),
                        "resolved": "→".join(x or "∅" for x in (s_eid, d_eid)),
                        "edge_exists": (s_eid is not None and d_eid is not None
                                        and (s_eid, d_eid) in edge_pairs),
                        "self_loop": s_eid == d_eid,
                    })
                    hit = True
            if s_eid and d_eid:
                global_rows_both += 1
                if s_eid == d_eid:
                    rows_self_loop += 1
                    continue
                m = map_relation(s_eid, _norm_name(str(r.get("relation") or ""))[:12],
                                 d_eid)
                if not m.relation:
                    rows_dropped_pred += 1
                    continue
                tri = (m.src, m.relation, m.dst)
                if tri in edge_triples:
                    global_merge_triples.add(tri)
                else:
                    global_new_triples.add(tri)
                    det = new_edge_detail.setdefault(
                        tri, {"rows": 0, "cache_keys": [], "raw": []})
                    det["rows"] += 1
                    if len(det["cache_keys"]) < 3:
                        det["cache_keys"].append(p.stem)
                    if len(det["raw"]) < 3:
                        det["raw"].append([str(s_raw), str(r.get("relation") or ""),
                                          str(d_raw)])
                    if m.src in iso or m.dst in iso:
                        new_triples_touch_iso.add(tri)
        if i % 800 == 0:
            print(f"[{time.strftime('%H:%M:%S')}] cache {i}/{len(files)}"
                  f"（{time.time() - t0:.1f}s）")

    # 孤点里有多少在缓存中被当过关系端点（B 类候选）
    iso_ids = sorted(iso)
    b_ids = [e for e in iso_ids if endpoint_mentions[e] > 0]
    a_ids = [e for e in iso_ids if endpoint_mentions[e] == 0]

    # B 类进一步分型：同名端点在缓存里出现过，但图上没有任何边——
    # 到底是「端点解析对了、边被 skip 掉了」还是「关系里的写法指向别的 eid」。
    b_detail = []
    for eid in b_ids[:60]:
        rows = iso_with_rel[eid]
        b_detail.append({
            "eid": eid,
            "name": name_by_eid[eid],
            "cache_endpoint_hits": endpoint_mentions[eid],
            "any_edge_exists": any(r["edge_exists"] for r in rows),
            "all_self_loop": all(r["self_loop"] for r in rows),
            "sample": rows[:4],
        })

    stats = {
        "graph_sha256_16": __import__("hashlib").sha256(
            s.graph_path.read_bytes()).hexdigest()[:16],
        "entities": len(g.entities),
        "edges": len(g.edges),
        "isolated": len(iso),
        "isolated_ratio": round(len(iso) / len(g.entities), 6),
        "cache_files": len(files),
        "cache_chunks_with_raw": n_chunks,
        "cache_relation_rows": rel_count,
        "iso_with_cache_relation_endpoint_B": len(b_ids),
        "iso_without_any_relation_A": len(a_ids),
        "B_share_of_isolated": round(len(b_ids) / len(iso), 6) if iso else None,
        "unresolvable_endpoint_names": len(unresolvable),
        "unresolvable_endpoint_rows": sum(unresolvable.values()),
        "unresolvable_top": [
            {"name": n, "rows": k} for n, k in unresolvable.most_common(30)],
        # ── 全局丢边（构建期 chunk-local 端点作用域造成的证据丢失）──
        "global_rows_both_endpoints_resolvable": global_rows_both,
        "global_rows_self_loop": rows_self_loop,
        "global_rows_predicate_dropped": rows_dropped_pred,
        "would_be_new_edges": len(global_new_triples),
        "would_merge_into_existing_edges": len(global_merge_triples),
        "new_edges_touching_isolated": len(new_triples_touch_iso),
        "isolated_recoverable_by_new_edges": len({
            eid for tri in new_triples_touch_iso for eid in tri[:1] + tri[2:]
            if eid in iso}),
    }
    LOST = ROOT / "data/compendium_rag/reports/p2_lost_edges.json"
    if len(global_merge_triples) == 0:
        # 26908 条「新边」的教训：三元组键序写反过一次，全部边都对不上却看不出错。
        print("[warn] 没有任何缓存关系命中图上已有边 —— 三元组键序或归一化口径有问题，"
              "别信这份丢边清单")
    LOST.write_text(json.dumps({
        "schema": "compendium_rag.p2_lost_edges/v1",
        "note": "构建期 chunk-local 端点作用域丢掉的、缓存里确实存在且双端可解析的关系；"
                "cache_keys 是证据回查入口（需再映射到 chunk_id）。只读产物，未落图。",
        "count": len(new_edge_detail),
        "edges": [
            {"src": t[0], "relation": t[1], "dst": t[2],
             "rows": d["rows"], "cache_keys": d["cache_keys"], "raw": d["raw"]}
            for t, d in sorted(new_edge_detail.items(),
                               key=lambda kv: -kv[1]["rows"])
        ],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    rep = {
        "schema": "compendium_rag.p2_cache_rel_diag/v1",
        "mode": "read-only",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "question": "孤点是「抽取就没给关系」还是「构建期丢了边」",
        "stats": stats,
        "b_samples": b_detail,
        "a_samples": [name_by_eid[e] for e in a_ids[:60]],
        "lost_edges_sidecar": str(LOST),
    }
    OUT.write_text(json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    print(f"报告 → {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
