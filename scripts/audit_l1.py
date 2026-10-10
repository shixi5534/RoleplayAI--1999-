# -*- coding: utf-8 -*-
"""WP1 —— L1 图构建质量审查（compendium_rag 正典图谱）。

模式：
  structure  纯本地结构+词表合规（无 LLM）：孤立率 / 平均度数 / 连通分量替代
             读数 / 关系类型合规率（classify_relation 只读）/ 实体类型合规。
  sample     40 块分层抽样（固定 seed=42，含 8 个"缓存空结果"块专测漏抽），
             落 l1_sample_chunks.json + 标注提示词（extract.py 规则原文）。
  pr         读仲裁后的 gold（l1_gold_chunks40.json），对图算实体/关系 P/R：
             关系以**端点对**为主口径（谓语同义改写严重），三元组全等副口径。

运行：
    PYTHONHASHSEED=0 .venv/Scripts/python.exe scripts/audit_l1.py --mode structure
    ... --mode sample | --mode pr --gold data/knowledge/_audit/l1_gold_chunks40.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

import audit_common as AC

AC.apply_v8_env()

AUDIT_DIR = AC.ROOT / "data" / "knowledge" / "_audit"
REPORTS_DIR = AC.ROOT / "data" / "compendium_rag" / "reports"
ENTITY_TYPES_OK = {"角色", "组织", "地点", "物品", "概念", "事件"}


def _load_kb_graph():
    from compendium_rag import pipeline as P
    from compendium_rag.config import get_settings
    s = get_settings()
    return s, P.load_kb(s).graph


def _load_vocab():
    """只读加载受控谓语表（不写回任何产物）。"""
    from roleplay.core.knowledge.relation_vocab import (
        CANONICAL_SET, RELATION_GROUPS, classify_relation)
    return CANONICAL_SET, RELATION_GROUPS, classify_relation


def _load_isolation_attribution(sha: str | None) -> dict:
    """读 P2 前置诊断的孤点归因（只读，带 SHA 门）。

    诊断产物是另一批脚本跑出来的，图一变它们就过期；过期还拿来写根因，
    等于用旧图的结论判新图，所以 SHA 不符就降级成「未测」而不是照抄。
    """
    out: dict = {"status": "ok", "graph_sha256_16": sha}
    src = {
        "landing": REPORTS_DIR / "p2_landing_diag.json",
        "cache_rel": REPORTS_DIR / "p2_cache_rel_diag.json",
    }
    st: dict[str, dict] = {}
    for tag, path in src.items():
        if not path.is_file():
            out[tag] = "missing"
            continue
        try:
            d = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # 损坏当缺失，不当 0
            out[tag] = f"unreadable:{type(exc).__name__}"
            continue
        got = (d.get("stats") or {}).get("graph_sha256_16")
        if sha and got != sha:
            out[tag] = f"stale:{got}"
            continue
        st[tag] = d.get("stats") or {}
    land, cache = st.get("landing") or {}, st.get("cache_rel") or {}
    iso = land.get("isolated") or cache.get("isolated") or 0
    grounded = land.get("overlap_isolated_but_grounded")
    if grounded is not None and iso:
        out["iso_ungrounded"] = land.get("overlap_isolated_and_ungrounded")
        out["iso_grounded"] = grounded
        out["grounded_share_of_isolated"] = round(grounded / iso, 4)
    a_cnt = cache.get("iso_without_any_relation_A")
    if a_cnt is not None and iso:
        out["iso_no_relation_in_cache"] = a_cnt
        out["iso_no_relation_share"] = round(a_cnt / iso, 4)
    if out.get("status") == "ok" and not (st.get("landing") or st.get("cache_rel")):
        out["status"] = "unavailable"
    return out


# ── 模式 structure ──

def mode_structure(args) -> int:
    s, graph = _load_kb_graph()
    rep = AC.new_report("WP1-structure", s)
    AC.assert_frozen_graph(rep)

    st = graph.stats()
    adj = AC.build_adjacency(graph)
    degs = AC.degrees(adj)
    n_ent = len(graph.entities) or 1
    n_edge = len(graph.edges)
    avg_deg = 2 * n_edge / n_ent
    comps = AC.connected_components(adj)
    comps_sorted = sorted(comps, key=len, reverse=True)
    largest = len(comps_sorted[0])
    nontrivial = sum(1 for c in comps if len(c) > 1)
    n_roles = st["entity_types"].get("角色", 0)

    rep["metrics"]["graph"] = {
        "entities": n_ent, "edges": n_edge, "role_entities": n_roles,
        "isolated_entities": st["isolated_entities"],
        "isolated_ratio": st["isolated_ratio"],
        "avg_degree": round(avg_deg, 3),
        "components_total": len(comps),
        "components_nontrivial": nontrivial,
        "largest_cc_nodes": largest,
        "largest_cc_ratio": round(largest / n_ent, 4),
    }

    g = rep["gate_verdicts"]
    # 孤点归因来自 P2 前置诊断（两份只读产物）。**带 SHA 门**：诊断产物必须对应本次
    # 被审的图，否则宁可标注缺失，也不让上一版图的结论冒充这一版（陈旧输入不给过）。
    attribution = _load_isolation_attribution(rep.get("frozen_graph_sha"))
    rep["metrics"]["isolation_attribution"] = attribution
    iso_pass = st["isolated_ratio"] <= 0.10
    iso_reason = ""
    if not iso_pass:
        iso_reason = (
            "根因**不是**『名不落地』——v9-P2 前置诊断实测：孤立 "
            f"{st['isolated_entities']} 个里名字逐字在语料的占 "
            f"{attribution.get('grounded_share_of_isolated', '未测')}，"
            "名不落地的孤点只有 "
            f"{attribution.get('iso_ungrounded', '未测')} 个；"
            f"另有 {attribution.get('iso_no_relation_in_cache', '未测')} 个"
            "（占孤点 "
            f"{attribution.get('iso_no_relation_share', '未测')}）在抽取缓存里"
            "**从未进过任何关系三元组**——图上没有它们是无依据的，"
            "补边=造事实，删点=改分母，两条都是禁手。"
            "故 ≤0.10 在 Track 1（零云端、不造边）下结构性不可达，"
            "按 D3 先例维持原口径判 FAIL 并报结构上界；"
            "原表述『1089/7033 名不落地是孤立率主因』已被实测推翻，"
            "那条读数治的是 name-key 死键与实体精确率，不是连通性。")
    g.append(AC.gate_verdict(
        "L1.3 孤立节点占比", "≤0.10", st["isolated_ratio"],
        "PASS" if iso_pass else "FAIL", iso_reason, "数据层"))
    deg_pass = avg_deg >= 2.5
    g.append(AC.gate_verdict(
        "L1.3 平均度数", "≥2.5", round(avg_deg, 3),
        "PASS" if deg_pass else "FAIL", "", "数据层"))
    g.append(AC.gate_verdict(
        "L1.3 连通分量数≤1.5×角色数", "≤1.5×%d" % n_roles,
        {"components_total": len(comps), "nontrivial": nontrivial,
         "largest_cc_ratio": round(largest / n_ent, 4)}, "N/A",
        "原门槛为『每角色一子图』架构设计；本库是单张连通大图，"
        f"{len(comps)} 分量中 {st['isolated_entities']} 个是孤立点，该门槛无判别力。"
        "以最大分量覆盖率+非平凡分量数为替代读数（不设门槛），最终裁决留用户。",
        "口径替代"))

    # 实体类型合规（构造保证）+ 关系类型合规（classify_relation 只读）
    bad_types = [e.eid for e in graph.entities.values()
                 if e.type not in ENTITY_TYPES_OK]
    g.append(AC.gate_verdict(
        "L1.1 实体类型合规", "=1.00（6 类受控）",
        {"violation": len(bad_types), "types": st["entity_types"]},
        "PASS" if not bad_types else "FAIL",
        "extract._norm_type 构造保证收敛（非抽样结论）", ""))

    CANONICAL_SET, _GROUPS, classify_relation = _load_vocab()
    reason_ct: Counter = Counter()
    strict_canonical = 0
    review_examples: list[dict] = []
    for e in graph.edges:
        canon, reason = classify_relation(e.relation)
        reason_ct[reason] += 1
        if e.relation in CANONICAL_SET:
            strict_canonical += 1
        if reason.startswith("review") and len(review_examples) < 40:
            review_examples.append({"relation": e.relation,
                                    "chunk_id": (e.chunk_ids or [""])[0]})
    n_ed = n_edge or 1
    strict_rate = strict_canonical / n_ed
    mappable = sum(v for k, v in reason_ct.items()
                   if k in ("canonical", "synonym", "rule"))
    # 第二口径（D3：原口径照判，浓度并报）。合规率可以靠「把长尾谓语提拔进
    # canonical」刷上去，浓度刷不了——它量的是谓语有没有真的收敛成可复用关系。
    rel_ct = Counter(e.relation for e in graph.edges)
    common = rel_ct.most_common()
    singles = sum(1 for _, k in common if k == 1)
    unmapped = {rel for rel in rel_ct if classify_relation(rel)[0] is None}
    g.append(AC.gate_verdict(
        "L1.2 关系类型合规率（严格：原文谓语∈77 canonical）", "≥1.00",
        round(strict_rate, 4), "PASS" if strict_rate >= 1.0 else "FAIL",
        "" if strict_rate >= 1.0 else
        "根因=数据层：extract.py SYSTEM_PROMPT 允许 2~6 字自由谓语（规则 5）。"
        "v9-P1 已接入谓语受控化（relation_norm + p1_apply 就地落盘），"
        "0.0676→%.4f；剩余缺口是 %d 种未映射长尾（占边 %.4f），"
        "把长尾逐个提拔进 canonical 只会把自由文本换个形式重造，故不追此指标。"
        "不可刷的第二口径见 metrics.relation_vocab.concentration。"
        % (strict_rate, len(unmapped), sum(rel_ct[r] for r in unmapped) / n_ed),
        "数据层"))
    rep["metrics"]["relation_vocab"] = {
        "unique_predicates": st["relation_types"],
        "strict_canonical_rate": round(strict_rate, 4),
        "classifiable_rate": round(mappable / n_ed, 4),
        "reason_distribution": dict(reason_ct.most_common()),
        "top_relations": st["top_relations"][:20],
        "concentration": {
            "singleton_predicates": singles,
            "singleton_rate_of_predicates": (round(singles / len(rel_ct), 6)
                                             if rel_ct else None),
            "singleton_edges": singles,
            "top10_edge_coverage": round(sum(k for _, k in common[:10]) / n_ed, 6),
            "unmapped_edges": sum(rel_ct[r] for r in unmapped),
            "unmapped_distinct": len(unmapped),
        },
    }
    rep["per_case"] = [{"sample": "relation_review_examples",
                        "items": review_examples}]
    # 层级分配 1.4：单层平坦图，无 Context Tier → N/A 豁免
    g.append(AC.gate_verdict(
        "L1.4 层级分配准确率", "≥0.90", None, "N/A",
        "compendium 图为单层平坦结构，无 世界→全局角色→局部场景→个人记忆 "
        "tier；对不存在的结构判负=惩罚未做的设计决策，判正=伪造覆盖。"
        "豁免并从 L1 分母剔除；信息量由实体类型分类准确率（WP1-pr）替代。",
        "结构不存在"))

    out = AC.write_report(REPORTS_DIR / "audit_l1_structure.json", rep)
    print(f"WP1-structure → {out}")
    for gv in g:
        print(f"  [{gv['verdict']}] {gv['gate']}: {gv['actual']}")
    return 0


# ── 模式 sample ──

QUOTA = {"mainline": 10, "activity": 8, "character": 6,
         "anecdote": 4, "appendix_unbound": 4}   # 非空块共 32
N_EMPTY_SLOTS = 8
SEED = 42


def mode_sample(args) -> int:
    from compendium_rag import pipeline as P
    from compendium_rag.config import get_settings
    from compendium_rag.extract import PROMPT_VERSION, SYSTEM_PROMPT, normalize
    from compendium_rag.graph_store import GraphStore
    s = get_settings()
    chunks = P.load_chunks(s)
    cache = P.ExtractionCache(s.cache_dir)

    empty_ids: list[str] = []
    by_cat: dict[str, list] = defaultdict(list)
    for c in chunks:
        by_cat[c.category].append(c)
        raw = cache.get_raw(P.cache_key(c, s.llm_model, PROMPT_VERSION))
        if raw is not None:
            ex = normalize(c, raw)
            if ex.ok and not ex.entities and not ex.relations:
                empty_ids.append(c.chunk_id)

    rng = random.Random(SEED)
    empty_pick = rng.sample(sorted(empty_ids), min(N_EMPTY_SLOTS, len(empty_ids)))
    empty_set = set(empty_pick)
    chosen: list[str] = list(empty_pick)          # 8 个缓存空结果块（专测漏抽）
    for cat, q in QUOTA.items():                  # 32 个正常块，共 40
        pool = [c for c in by_cat.get(cat, []) if c.chunk_id not in empty_set]
        chosen += [c.chunk_id for c in rng.sample(pool, min(q, len(pool)))]
    assert len(chosen) == 40, f"抽样数 {len(chosen)} != 40（某类块不足配额）"
    cmap = {c.chunk_id: c for c in chunks}
    rows = []
    for cid in chosen:
        c = cmap[cid]
        rows.append({"chunk_id": cid, "category": c.category,
                     "chapter_title": c.chapter_title,
                     "scene_title": c.scene_title, "part_title": c.part_title,
                     "speakers": c.speakers[:20], "n_chars": len(c.text),
                     "text": c.text, "is_cache_empty": cid in empty_set})

    out = AUDIT_DIR / "l1_sample_chunks.json"
    out.write_text(json.dumps(
        {"schema": "audit.l1_sample/v1", "seed": SEED, "quota": QUOTA,
         "n_cache_empty_total": len(empty_ids),
         "n_cache_empty_sampled": len(empty_pick), "chunks": rows},
        ensure_ascii=False, indent=2), encoding="utf-8")
    # 标注规则原文（子代理口径 = extract.py 规则 1~12 逐字）
    rules = AUDIT_DIR / "l1_annotation_rules.md"
    rules.write_text(
        "# L1 gold 标注规则（= 被测系统抽取提示词逐字原文）\n\n"
        "标注员按下列规则从块文本中抽取实体与关系，输出 JSON：\n"
        "```\n" + SYSTEM_PROMPT + "\n```\n\n"
        "## 标注侧补充（与线上系统的差异声明）\n"
        "- 这是**人工口径 gold**：按规则字面执行，不沿用线上模型的偷懒惯例。\n"
        "- 泛称/无名指代（规则 6/9）一律跳过；事件实体只收有专名重大事件（规则 10）。\n"
        "- 每条关系必须给 evidence 原文短句（规则 7）。\n",
        encoding="utf-8")
    print(f"抽样 40 块 → {out}（缓存空结果块共 {len(empty_ids)}，抽 {len(empty_pick)}）")
    print(f"标注规则原文 → {rules}")
    return 0


# ── 模式 pr ──

def _norm(s: str) -> str:
    return (s or "").strip()


class ChunkGraph:
    """图产物的按块归因视图（只读）。"""

    def __init__(self, graph):
        self.graph = graph
        self.ent_by_chunk: dict[str, list] = defaultdict(list)
        for e in graph.entities.values():
            for cid in e.chunk_ids:
                self.ent_by_chunk[cid].append(e)
        self.edge_by_chunk: dict[str, list] = defaultdict(list)
        for e in graph.edges:
            for cid in e.chunk_ids:
                self.edge_by_chunk[cid].append(e)

    def resolve_name(self, name: str):
        """名/别名 -> eid（全局）。"""
        name = _norm(name)
        if not name:
            return None
        eid = self.graph.alias_index.get(name)
        return eid


def _ent_matches(ent, gname: str) -> bool:
    gname = _norm(gname)
    return gname == _norm(ent.name) or gname in (_norm(a) for a in ent.aliases)


def mode_pr(args) -> int:
    s, graph = _load_kb_graph()
    rep = AC.new_report("WP1-pr", s)
    AC.assert_frozen_graph(rep)

    gold_path = Path(args.gold)
    if not gold_path.exists():
        raise SystemExit(f"[FATAL] gold 不存在：{gold_path}（先完成子代理标注+仲裁）")
    gold = json.loads(gold_path.read_text(encoding="utf-8"))
    cg = ChunkGraph(graph)

    tot = Counter()
    per_case = []
    type_agree = type_total = 0
    strict_canonical = 0
    n_grel = 0
    _CANON, _GROUPS, classify_relation = _load_vocab()

    for chunk_gold in gold["chunks"]:
        cid = chunk_gold["chunk_id"]
        gents = chunk_gold.get("entities", [])
        grels = chunk_gold.get("relations", [])
        sys_ents = cg.ent_by_chunk.get(cid, [])
        sys_rels = cg.edge_by_chunk.get(cid, [])

        gnames = {_norm(e["name"]) for e in gents}
        galias = {a for e in gents for a in e.get("aliases", []) if _norm(a)}
        gnames_all = {g for g in (gnames | galias) if g}

        # 实体 P：本块归因的系统实体有多少被本块 gold 支持
        p_sup = sum(1 for e in sys_ents
                    if _norm(e.name) in gnames_all
                    or any(_norm(a) in gnames_all for a in e.aliases))
        # 实体 R：gold 实体是否被本块归因抽到（主口径）/ 全图存在（参考）
        r_hit_chunk = 0
        r_hit_graph = 0
        for ge in gents:
            nm = _norm(ge["name"])
            if any(_ent_matches(e, nm) for e in sys_ents):
                r_hit_chunk += 1
                r_hit_graph += 1
            elif cg.resolve_name(nm):
                r_hit_graph += 1
        tot["ent_sys"] += len(sys_ents)
        tot["ent_sys_supported"] += p_sup
        tot["ent_gold"] += len(gents)
        tot["ent_recall_chunk"] += r_hit_chunk
        tot["ent_recall_graph"] += r_hit_graph

        # 实体类型一致率（gold 类型 vs 系统类型，名字命中者才可比）
        for ge in gents:
            nm = _norm(ge["name"])
            for e in sys_ents:
                if _ent_matches(e, nm):
                    type_total += 1
                    type_agree += 1 if e.type == ge.get("type") else 0
                    break

        # 关系：端点对主口径（无序，经 eid 解析）+ 三元组全等副口径
        sys_pairs = Counter()          # (src_eid, dst_eid) 有序计数
        sys_triples = Counter()        # (src, canonical_or_raw, dst)
        for e in sys_rels:
            se, de = graph.entities.get(e.src), graph.entities.get(e.dst)
            if not se or not de:
                continue
            sys_pairs[(e.src, e.dst)] += 1
            canon, _ = classify_relation(e.relation)
            sys_triples[(e.src, canon or e.relation, e.dst)] += 1
            strict_canonical += 1 if e.relation in _CANON else 0
        # gold 名 -> eid（本块归因优先，再全局 alias）
        def g2e(nm):
            for e in sys_ents:
                if _ent_matches(e, nm):
                    return e.eid
            return cg.resolve_name(nm)
        n_grel += len(grels)
        rel_pair_hit_sys = 0
        rel_pair_hit_gold = 0
        rel_triple_hit = 0
        unresolvable = 0
        gold_pairs_un: set = set()
        for gr in grels:
            a, b = g2e(gr["src"]), g2e(gr["dst"])
            if not a or not b:
                unresolvable += 1
                continue
            gold_pairs_un.add(frozenset((a, b)))
            if (a, b) in sys_pairs or (b, a) in sys_pairs:
                rel_pair_hit_gold += 1
                canon, _ = classify_relation(gr["relation"])
                gr_raw = _norm(gr["relation"])
                if ((a, canon or gr_raw, b) in sys_triples
                        or (b, canon or gr_raw, a) in sys_triples):
                    rel_triple_hit += 1
        # 关系 P：本块系统边端点对（无序）落在 gold 边集
        rel_pair_hit_sys = sum(1 for (a, b) in sys_pairs
                               if frozenset((a, b)) in gold_pairs_un)
        n_sys_pairs_in_chunk = sum(sys_pairs.values())
        tot["rel_sys"] += n_sys_pairs_in_chunk
        tot["rel_sys_in_gold"] += rel_pair_hit_sys
        tot["rel_gold"] += len(grels)
        tot["rel_gold_found_chunk"] += rel_pair_hit_gold
        tot["rel_triple"] += rel_triple_hit
        tot["rel_gold_unresolvable"] += unresolvable

        per_case.append({
            "chunk_id": cid, "gold_entities": len(gents),
            "sys_entities": len(sys_ents), "ent_supported": p_sup,
            "ent_r_chunk": r_hit_chunk, "ent_r_graph": r_hit_graph,
            "gold_relations": len(grels), "sys_rel_pairs": n_sys_pairs_in_chunk,
            "rel_pair_in_gold": rel_pair_hit_sys,
            "rel_pair_gold_found": rel_pair_hit_gold,
            "rel_triple_hit": rel_triple_hit})

    def rate(a, b):
        return round(tot[a] / tot[b], 4) if tot[b] else None

    ent_p = rate("ent_sys_supported", "ent_sys")
    ent_r = rate("ent_recall_chunk", "ent_gold")
    ent_r_graph = rate("ent_recall_graph", "ent_gold")
    f1 = round(2 * ent_p * ent_r / (ent_p + ent_r), 4) if ent_p and ent_r else 0.0
    rel_p = rate("rel_sys_in_gold", "rel_sys")
    rel_r = rate("rel_gold_found_chunk", "rel_gold")
    rel_triple_rate = rate("rel_triple", "rel_gold")
    type_acc = round(type_agree / type_total, 4) if type_total else None

    rep["metrics"] = {
        "sampled_chunks": len(gold["chunks"]),
        "totals": dict(tot),
        "entity": {"P": ent_p, "R(chunk-attributed)": ent_r,
                   "R(graph-wide·参考)": ent_r_graph, "F1": f1},
        "relation": {"P(端点对)": rel_p, "R(端点对)": rel_r,
                     "R(三元组全等·副口径)": rel_triple_rate,
                     "strict_canonical_rate_sample": round(
                         strict_canonical / (tot["rel_sys"] or 1), 4)},
        "entity_type_accuracy": type_acc,
    }
    g = rep["gate_verdicts"]
    g.append(AC.gate_verdict("L1.1 实体精确率", "≥0.90", ent_p,
                             "PASS" if ent_p is not None and ent_p >= 0.90 else "FAIL",
                             "", "数据层"))
    g.append(AC.gate_verdict("L1.1 实体召回率", "≥0.85", ent_r,
                             "PASS" if ent_r is not None and ent_r >= 0.85 else "FAIL",
                             "主口径=本块归因；graph-wide 参考值见 metrics", "数据层"))
    g.append(AC.gate_verdict("L1.1 实体 F1", "≥0.87", f1,
                             "PASS" if f1 >= 0.87 else "FAIL", "", "数据层"))
    g.append(AC.gate_verdict("L1.2 关系精确率（端点对口径）", "≥0.85", rel_p,
                             "PASS" if rel_p is not None and rel_p >= 0.85 else "FAIL",
                             "谓语同义改写严重，端点对为主口径（score_audit 双口径设计）",
                             "数据层"))
    g.append(AC.gate_verdict("L1.4替代 实体类型分类准确率", "≥0.90", type_acc,
                             "PASS" if type_acc is not None and type_acc >= 0.90
                             else "FAIL", "层级分配 N/A 豁免后的信息量替代项",
                             "数据层"))
    rep["per_case"] = per_case
    out = AC.write_report(REPORTS_DIR / "audit_l1_pr.json", rep)
    print(f"WP1-pr → {out}")
    for gv in g:
        print(f"  [{gv['verdict']}] {gv['gate']}: {gv['actual']}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", required=True, choices=["structure", "sample", "pr"])
    ap.add_argument("--gold", default=str(AUDIT_DIR / "l1_gold_chunks40.json"))
    args = ap.parse_args()
    return {"structure": mode_structure, "sample": mode_sample,
            "pr": mode_pr}[args.mode](args)


if __name__ == "__main__":
    sys.exit(main())
