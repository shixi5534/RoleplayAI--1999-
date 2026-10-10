# -*- coding: utf-8 -*-
"""v9-P3 前置诊断 · 角色域过滤动手前必须先量的两件事（只读）。

计划里那条「证据块不含被问角色名/别名就降权/剔除」不能直接写：
L2.3 的判据与过滤器的判据是**同一条**（同义反复陷阱，已在 §P3 登记）。定方案前有两个
没答的问题，答案决定过滤器该不该做、做成什么样：

**问题 1｜泛称锚点面**：v8 的 20 条泄漏样例里被问「角色」有 伙计/会长/上级/孩子们/
无名者/基金会调查员/黑鹮的副手 这类**泛称**。原计划用 `corpus.is_generic_speaker`
判它——**本脚本实测该口径在 2023 个「角色」实体上命中 0**（读数 1），那份正则只覆盖
旁白/众人/路人甲 这类说话人占位，治不了这些称谓。**读数 6 直接给了问题 1 的答案：
伙计/会长/上级/孩子们/无名者 都在 `alias_index` 里做键、各自指向一个同名「角色」
实体**，所以泛称题有锚点、图通道照跑、过滤器有靶子。**读数 7** 再量这个靶子有多大：
用不依赖人工名单的结构判据（词面嵌于 ≥2 个更长角色名）数出「类别词当专名」的规模。
另配**读数 2b** 的结构代理（角色实体跨章广度分位数）作旁证。

**问题 2｜假泄漏 vs 真越界**：泄漏块里有些本来就该出现（是该题的 gold 块，块里没写
被问角色的名字只是因为那句话由别人转述），有些才是真把别人的私密场景端上桌。分型：
- `is_gold`：该块属于该题的 relevant 集（与 `audit_l2.relevant_set` 同判据、同 `blob_of`）；
- `other_named_char`：块的 `speakers` 里出现**其他**具名「角色」实体 → 真越界候选；
- `unowned`：`speakers` 只有泛称/为空 → 无主段落，谈不上「跨角色」（假泄漏候选）。

数据出处纪律：泄漏行来自 **v8 审计产物** `reports/audit_l2.json`
（`frozen_graph_sha=026b41699f021db2`，225 角色域题 / 33 候选 / 0.1467），且审计只把
**20 条样例**落盘（完整 225 行未存），所以锚点读数是**样例内**计数。
P1 只改谓语与边、**实体逐字节全等**、语料未动 → 实体侧与块侧读数对 v8/v9-a 通用；
会随排序变的是**候选集合本身**，那归 P7 复审，不记在本脚本账上。

用法：
    PYTHONPATH=src .venv/Scripts/python.exe -X utf8 \\
        scripts/compendium_rag_p3_rolefilter_prereq_diag.py
产物：``data/compendium_rag/reports/p3_rolefilter_prereq.{json,md}``
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
for _k, _v in {"CMPRAG_LEX_WEIGHT": "1.0", "CMPRAG_RRF_K": "1",
               "CMPRAG_LEX_FIRST": "0", "PYTHONHASHSEED": "0"}.items():
    os.environ.setdefault(_k, _v)      # 必须在 import config 之前

import audit_common as AC              # noqa: E402  （blob_of 与 L2 同判据）
from compendium_rag import pipeline as P  # noqa: E402
from compendium_rag.config import get_settings  # noqa: E402
from compendium_rag.corpus import is_generic_speaker  # noqa: E402

EXPECTED_SHA = "7cac5867e8c80879"      # v9-a：实体/块读数用它
V8_SHA = "026b41699f021db2"            # 泄漏行出处
AUDIT_L2 = ROOT / "data" / "compendium_rag" / "reports" / "audit_l2.json"
AUDIT_DIR = ROOT / "data" / "knowledge" / "_audit"
SETS = {
    "300cn": AUDIT_DIR / "rag_testset_300_cn.json",
    "blind": AUDIT_DIR / "blind_v1" / "questions_strict.json",
    "gen": AUDIT_DIR / "rag_testset_gen_r1r2.json",
}
R = ROOT / "data" / "compendium_rag" / "reports"


def sha16(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def flatten_evidence(ev) -> list[str]:
    """与 `compendium_rag_eval300.flatten_evidence` 逐字同构（关键词集必须一致）。"""
    out: list[str] = []
    for grp in (ev or []):
        if isinstance(grp, str):
            out.append(grp)
        elif isinstance(grp, (list, tuple)):
            out.extend(str(x) for x in grp if x)
    seen, res = set(), []
    for k in out:
        k = k.strip()
        if k and k not in seen:
            seen.add(k)
            res.append(k)
    return res


def main() -> int:
    s = get_settings()
    sha = sha16(s.graph_path)
    if sha != EXPECTED_SHA:
        raise SystemExit(f"图指纹漂移：期望 {EXPECTED_SHA}，实际 {sha}，中止")
    audit = json.loads(AUDIT_L2.read_text(encoding="utf-8"))
    if audit.get("frozen_graph_sha") != V8_SHA:
        raise SystemExit(f"泄漏行出处不是 v8 冻结图"
                         f"（实际 {audit.get('frozen_graph_sha')}，期望 {V8_SHA}）")
    rl = audit["metrics"]["role_leak"]
    examples = rl["examples"]

    kb = P.load_kb(s)
    graph = kb.graph
    retr = kb.retriever
    chunk_by_cid = {c.chunk_id: c for c in kb.chunks}
    blob_by_cid = {cid: AC.blob_of(c) for cid, c in chunk_by_cid.items()}
    # 具名「角色」实体（排除泛称）——锚点面与「谁的场景」都以此为准
    named_roles = [e for e in graph.entities.values()
                   if e.type == "角色" and not is_generic_speaker(e.name)]
    role_names: dict[str, str] = {}
    for e in named_roles:
        for nm in (e.name, *e.aliases):
            if nm and nm not in role_names:
                role_names[nm] = e.name

    cases: dict[tuple[str, str], dict] = {}
    for tag, path in SETS.items():
        d = json.loads(path.read_text(encoding="utf-8"))
        rows = d if isinstance(d, list) else d.get("cases", [])
        for r in rows:
            cases[(tag, str(r.get("id", "")))] = r

    # ── 读数 1｜实体侧泛称规模 ──
    role_ents = [e for e in graph.entities.values() if e.type == "角色"]
    generic_ents = [e for e in role_ents if is_generic_speaker(e.name)]
    ent_read = {
        "role_entities": len(role_ents),
        "generic_role_entities": len(generic_ents),
        "generic_share": round(len(generic_ents) / max(1, len(role_ents)), 4),
        "sample_generic_names": sorted({e.name for e in generic_ents})[:30],
    }

    # ── 读数 2b｜结构代理：角色实体的「跨章广度」分布 ──
    # is_generic_speaker 对 伙计/会长/上级/孩子们/无名者 一个都没命中（实测），
    # 所以「是不是泛称」不能靠那份正则，改用可测的结构特征：泛称哪儿都在、
    # 跨章广度显著高于具名角色。
    def chapter_span(e) -> int:
        return len({chunk_by_cid[c].chapter_id for c in (e.chunk_ids or [])
                    if c in chunk_by_cid})

    spans_all = sorted(chapter_span(e) for e in role_ents)

    def pct(p: float) -> int:
        return spans_all[max(0, min(len(spans_all) - 1,
                                    int(len(spans_all) * p)))]

    def span_percentile(v: int) -> float:
        return round(sum(1 for x in spans_all if x <= v) / max(1, len(spans_all)), 4)

    # ── 读数 2/3｜逐条样例：锚点性质 + 泄漏块分型 ──
    rows_out = []
    for lk in examples:
        tag, qid = lk["set"], lk["qid"]
        c = cases.get((tag, qid))
        if c is None:
            rows_out.append({"set": tag, "qid": qid, "role": lk["role"],
                             "status": "qid_not_in_rebuilt_sets"})
            continue
        q = c.get("q", "")
        kws = flatten_evidence(c.get("evidence"))
        gold = {cid for cid, blob in blob_by_cid.items()
                if any(k in blob for k in kws)}
        seeds = [sd for sd in retr.link(q, top_k=s.entity_link_top)
                 if sd.score >= s.seed_score_threshold]
        first = graph.entities.get(seeds[0].eid) if seeds else None
        asked = first.name if first else lk["role"]
        in_q_named = sorted({role_names[nm] for nm, own in role_names.items()
                             if nm in q})
        generic_asked = is_generic_speaker(asked)
        # 结构代理（**不依赖 GENERIC_SPEAKER 正则**）：泛称的真实特征是「哪儿都在、
        # 谁都能指」——出现跨的章数多、单章密度低；具名角色通常集中在少数章。
        span = {}
        if first is not None:
            cids = list(first.chunk_ids)
            span = {"n_chunks": len(cids),
                    "n_chapters": len({chunk_by_cid[c].chapter_id
                                       for c in cids if c in chunk_by_cid}),
                    "n_scenes": len({chunk_by_cid[c].scene_title
                                     for c in cids if c in chunk_by_cid}),
                    "n_aliases": len(first.aliases or [])}
        # 靶子类：锚点是泛称，且题面除该泛称外**没有任何其他具名角色**
        only_generic_anchor = generic_asked and len(in_q_named) <= 1
        detail = []
        for cid in lk["leaked_chunks"]:
            ch = chunk_by_cid.get(cid)
            if ch is None:
                detail.append({"chunk_id": cid, "kind": "chunk_missing"})
                continue
            sp = [x for x in (ch.speakers or []) if x]
            owners = sorted({role_names[nm] for nm in sp if nm in role_names})
            kind = ("is_gold" if cid in gold else
                    "other_named_char" if owners else "unowned")
            detail.append({"chunk_id": cid, "kind": kind,
                           "speakers": sp[:8], "named_owners": owners[:8]})
        rows_out.append({
            "set": tag, "qid": qid, "query": q, "asked_role": asked,
            "generic_asked": generic_asked, "n_seeds": len(seeds),
            "seed_names": [sd.name for sd in seeds],
            "named_roles_in_query": in_q_named,
            "only_generic_anchor": only_generic_anchor,
            "span": span,
            "n_leaked": len(lk["leaked_chunks"]), "leaked_detail": detail})

    kinds = Counter(pc["kind"] for r in rows_out
                    for pc in r.get("leaked_detail", []))
    n_chunks = sum(kinds.values())
    anchor = {
        "examples": len(rows_out),
        "generic_asked": sum(1 for r in rows_out if r.get("generic_asked")),
        "only_generic_anchor": sum(1 for r in rows_out
                                   if r.get("only_generic_anchor")),
    }
    false_leak = kinds["is_gold"] + kinds["unowned"]
    # ── 读数 4｜说话人侧的泛称覆盖缺口（解释 read1 为什么是 0）──
    spk_count: Counter[str] = Counter()
    for c in kb.chunks:
        for nm in (c.speakers or []):
            if nm:
                spk_count[nm] += 1
    generic_spk = {n: v for n, v in spk_count.items() if is_generic_speaker(n)}
    # 看着像泛称但正则没盖住的：带罗马数字后缀（士兵Ⅰ/市民Ⅱ）或 甲乙丙丁 后缀。
    # 必须剔掉已注册为「角色」实体的名字：`[甲乙丙丁]$` 会把 康斯坦丁（×54）这类
    # 真名误当占位名，留下它就是把具名角色算进泛称缺口——同一种口径错误。
    role_name_set = {e.name for e in role_ents} | set(role_names)
    rom_num = re.compile(r"[ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ]$"
                         r"|(?:[甲乙丙丁]$)")
    num_hits = {n: v for n, v in spk_count.items()
                if not is_generic_speaker(n) and rom_num.search(n)}
    unmatched_generic = {n: v for n, v in num_hits.items()
                         if n not in role_name_set}
    registered_but_suffix = {n: v for n, v in num_hits.items()
                             if n in role_name_set}
    # 剔除后必须把「已注册为角色实体」这一桶拆开看：里面既有 康斯坦丁 这种真名
    # （正则误伤），也有 镇民Ⅰ/基金会职员Ⅱ 这种**被当成角色建了节点的泛称**——
    # 后者才是 read1「正则命中 0」背后的真实污染，且只能按后缀形态分离：
    # 罗马数字后缀一定是占位名，甲乙丙丁后缀要人工分辨。
    roman_only = {n: v for n, v in registered_but_suffix.items()
                  if n.endswith(tuple("ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ"))}
    abc_suffix = {n: v for n, v in registered_but_suffix.items()
                  if n[-1] in "甲乙丙丁"}
    speaker_read = {
        "distinct_speakers": len(spk_count),
        "generic_per_regex": len(generic_spk),
        "generic_per_regex_mentions": sum(generic_spk.values()),
        "unmatched_numeric_suffix": len(unmatched_generic),
        "unmatched_numeric_suffix_mentions": sum(unmatched_generic.values()),
        "top_unmatched_examples": [f"{n}×{v}" for n, v in
                                   sorted(unmatched_generic.items(),
                                          key=lambda kv: -kv[1])[:15]],
        "numeric_suffix_excluded_because_registered": len(registered_but_suffix),
        "numeric_suffix_excluded_examples": [
            f"{n}×{v}" for n, v in
            sorted(registered_but_suffix.items(), key=lambda kv: -kv[1])[:10]],
        "registered_role_entities_with_roman_suffix": len(roman_only),
        "registered_role_entities_with_roman_suffix_mentions":
            sum(roman_only.values()),
        "registered_role_entities_roman_suffix_examples": [
            f"{n}×{v}" for n, v in
            sorted(roman_only.items(), key=lambda kv: -kv[1])[:15]],
        "top_speakers_not_role_entities": [
            f"{n}×{v}" for n, v in sorted(spk_count.items(), key=lambda kv: -kv[1])
            if n not in role_name_set][:15],
    }
    rows_ranked = [{"qid": r["qid"], "asked_role": r.get("asked_role"),
                    "n_chapters": r.get("span", {}).get("n_chapters"),
                    "n_chunks": r.get("span", {}).get("n_chunks"),
                    "percentile_in_role_entities": span_percentile(
                        r.get("span", {}).get("n_chapters", 0) or 0)}
                   for r in rows_out if "span" in r]
    span_read = {
        "all_role_entities_chapter_span": {"p50": pct(0.5), "p90": pct(0.9),
                                           "p99": pct(0.99), "max": spans_all[-1]},
        "rows": sorted(rows_ranked, key=lambda x: -(x["n_chapters"] or 0)),
        "spread_ge_p90": sum(1 for x in rows_ranked
                             if (x["n_chapters"] or 0) >= pct(0.9)),
    }
    # ── 读数 6｜泛称词到底能不能当锚点：直接查 alias_index ──
    # 计划文档 §P3 问题① 的原话是「伙计/会长/上级/孩子们/无名者 是否被 alias_index
    # 当键命中」。这条不必推断，图里就有答案：link() 只做「查询串 vs alias_index 键」
    # 的包含匹配，键不存在 → 泛称题压根没有种子 → 角色域过滤器永远不会触发。
    probe = ["伙计", "会长", "上级", "孩子们", "无名者", "调查员", "职员", "学生",
             "镇民", "士兵", "记者", "医生", "议员", "队长", "军官", "主教", "特工",
             "幸存者", "平民", "商贩"]
    appellation_keys = []
    for w in probe:
        eid = graph.alias_index.get(w)
        e = graph.entities.get(eid) if eid else None
        appellation_keys.append({
            "word": w, "is_alias_key": eid is not None,
            "eid": eid, "entity": e.name if e else None,
            "entity_type": e.type if e else None,
            "n_chunks": len(e.chunk_ids or []) if e else 0})
    read6 = {
        "probed": len(probe),
        "hit_as_alias_key": sum(1 for r in appellation_keys if r["is_alias_key"]),
        "hit_words": [f"{r['word']}→{r['entity']}·{r['entity_type']}"
                      f"({r['n_chunks']}块)" for r in appellation_keys
                      if r["is_alias_key"]],
        "miss_words": [r["word"] for r in appellation_keys if not r["is_alias_key"]],
        "rows": appellation_keys,
    }
    # ── 读数 7｜实体侧「类别词被当专名建了节点」的规模 ──
    # read1 用 is_generic_speaker 数出 0，read6 却证明 伙计/会长/上级/无名者 就是
    # alias_index 的键且指向同名「角色」实体——两份读数不矛盾，是那份正则的口径
    # 只覆盖说话人占位名。这里换一个不依赖人工名单的结构判据：类别词一定还会作为
    # 真子串出现在别的角色名里（调查员 ⊂ 基金会调查员/调查员Ⅰ），专名不会。
    role_name_list = [e.name for e in role_ents]

    def broader_uses(name: str) -> int:
        return sum(1 for o in role_name_list
                   if o != name and len(o) > len(name) and name in o)

    by_eid_name = {e.name: e for e in role_ents}
    census = {n: broader_uses(n) for n in sorted(set(role_name_list))}
    cat_words = {n: v for n, v in census.items() if v >= 2}
    read7 = {
        "criterion": "词面作为真子串出现在 ≥2 个更长的「角色」实体名里",
        "role_entity_names": len(census),
        "category_word_like": len(cat_words),
        "category_word_like_share": round(len(cat_words) / max(1, len(census)), 4),
        "top_examples": [
            f"{n}(嵌于{v}个更长名/{len(by_eid_name[n].chunk_ids or [])}块)"
            for n, v in sorted(cat_words.items(), key=lambda kv: -kv[1])[:25]],
        "sample_anchor_status": [
            {"asked_role": nm,
             "is_alias_key": graph.alias_index.get(nm) is not None,
             "entity": (graph.entities.get(graph.alias_index[nm]).name
                        if graph.alias_index.get(nm) else None),
             "entity_type": (graph.entities.get(graph.alias_index[nm]).type
                             if graph.alias_index.get(nm) else None),
             "broader_uses": census.get(nm),
             "regex_generic": is_generic_speaker(nm)}
            for nm in sorted({r.get("asked_role") or "?" for r in rows_out})],
    }
    # ── 读数 8｜落地前提：归属表的覆盖率（owners 判据能不能算得出来）──
    # 过滤器按 `block.owners = speakers ∩ 具名角色表` 判定，未注册为实体的高频说话人
    # （？？？/医生/士兵/迪塔斯多夫）会让 owners 系统性偏空 → 真越界被误判成 unowned。
    # 所以落地前先把这个缺口数出来。
    absent = {n: v for n, v in spk_count.items() if n not in role_name_set}
    n_owned = sum(1 for c in kb.chunks if set(c.speakers or []) & role_name_set)
    char_chunks = [c for c in kb.chunks if c.category == "character"]
    n_char_owned = sum(1 for c in char_chunks
                       if set(c.speakers or []) & role_name_set)
    read8 = {
        "criterion": "owners = chunk.speakers ∩ 具名角色表（name+alias）",
        "speakers_absent_from_role_table": len(absent),
        "absent_mentions": sum(absent.values()),
        "absent_share_of_all_mentions": round(
            sum(absent.values()) / max(1, sum(spk_count.values())), 4),
        "top_absent_speakers": [f"{n}×{v}" for n, v in
                                sorted(absent.items(), key=lambda kv: -kv[1])[:20]],
        "chunks_total": len(kb.chunks),
        "chunks_with_owners": n_owned,
        "chunks_without_owners": len(kb.chunks) - n_owned,
        "character_chunks_total": len(char_chunks),
        "character_chunks_with_owners": n_char_owned,
        "character_ownership_coverage": round(
            n_char_owned / max(1, len(char_chunks)), 4),
    }
    rep = {
        "done_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "graph_sha256_16": sha,
        "leak_rows_source": {"file": str(AUDIT_L2.relative_to(ROOT)),
                             "frozen_graph_sha": audit["frozen_graph_sha"],
                             "role_domain_questions": rl["role_domain_questions"],
                             "leak_candidates": rl["leak_candidates"],
                             "rate": rl["rate"], "examples_stored": len(examples),
                             "note": "完整 225 行未落盘，只有 20 条 examples，"
                                     "故锚点读数是样例内计数而非 225 题计数"},
        "transfer_validity": "P1 只改谓语/边，实体逐字节全等、语料未动 → 实体侧与块侧"
                             "读数对 v8 与 v9-a 通用；随排序变的是候选集合本身，归 P7 复审",
        "caliber": {**{k: os.environ.get(k) for k in
                       ("CMPRAG_LEX_WEIGHT", "CMPRAG_RRF_K", "CMPRAG_LEX_FIRST",
                        "PYTHONHASHSEED")},
                    "entity_link_top": s.entity_link_top,
                    "seed_score_threshold": s.seed_score_threshold,
                    "generic_criterion": "corpus.is_generic_speaker（GENERIC_SPEAKER 正则）",
                    "gold_criterion": "audit_common.blob_of + 关键词子串，与 audit_l2.relevant_set 同判据",
                    "seed_rebuild": "retr.link(query) 后按 seed_score_threshold 过滤，"
                                    "不走向量兜底（与 graph_only 口径一致，保守）"},
        "read1_generic_entities": ent_read,
        "read2_anchor_exposure": anchor,
        "read2b_span_proxy": span_read,
        "read3_leaked_chunk_kinds": {**dict(kinds), "total_leaked_chunks": n_chunks,
                                     "false_leak_share": round(
                                         false_leak / max(1, n_chunks), 4),
                                     "true_cross_share": round(
                                         kinds["other_named_char"] / max(1, n_chunks), 4)},
        "read4_speaker_genericity": speaker_read,
        "read6_appellation_alias_keys": read6,
        "read7_category_word_census": read7,
        "read8_ownership_coverage": read8,
        "rows": rows_out,
    }
    (R / "p3_rolefilter_prereq.json").write_text(
        json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")

    md = [
        "# v9-P3 前置诊断 · 角色域过滤动手前必须先量的两件事",
        "",
        f"- 读数用的图 `{sha}`（实体/块侧）；泄漏行出处 `audit_l2.json`"
        f"（`{V8_SHA}`，{rl['role_domain_questions']} 角色域题 / "
        f"{rl['leak_candidates']} 候选 / {rl['rate']:.4f}，落盘样例 {len(examples)} 条）",
        f"- 可迁移性：{rep['transfer_validity']}",
        "",
        "## 读数 1｜实体侧的泛称规模",
        "",
        f"「角色」实体 {ent_read['role_entities']} 个，其中名字命中 `is_generic_speaker`"
        f" 的 **{ent_read['generic_role_entities']}** 个"
        f"（{ent_read['generic_share']:.2%}）。"
        f"样例：`{'、'.join(ent_read['sample_generic_names'][:15]) or '（空——一个都没有）'}`。"
        f"**但 0 不等于图里没有泛称**，见读数 4：那份正则只管说话人占位名，"
        f"实体侧的占位名是另一种形态。",
        "",
        "## 读数 2｜泄漏样例的锚点性质",
        "",
        f"{anchor['examples']} 条样例里，被问角色是泛称的 **{anchor['generic_asked']}** 条；"
        f"其中**题面除该泛称外再没有其他具名角色**（=过滤器真正的靶子）"
        f"**{anchor['only_generic_anchor']}** 条。",
        "",
        "## 读数 2b｜泛称不能靠那份正则（自我修正）",
        "",
        f"`is_generic_speaker` 在 2023 个「角色」实体上命中 **0** 个，样例里的 "
        f"伙计/会长/上级/孩子们/无名者/基金会调查员/黑鹮的副手 **一个都不在** "
        f"`GENERIC_SPEAKER` 正则里（该正则只覆盖 旁白/众人/路人甲/守卫乙/女仆 这类"
        f"说话人占位）。所以「被问的是不是泛称」不能用它判，本诊断改用结构代理："
        f"角色实体跨章广度全体 p50={span_read['all_role_entities_chapter_span']['p50']}、"
        f"p90={span_read['all_role_entities_chapter_span']['p90']}、"
        f"max={span_read['all_role_entities_chapter_span']['max']}；"
        f"20 条样例的锚点实体里**跨章广度 ≥p90** 的有 "
        f"**{span_read['spread_ge_p90']}** 条（逐条见 json）。",
        "",
        "## 读数 3｜泄漏块分型（假泄漏 vs 真越界）",
        "",
        f"{n_chunks} 个泄漏块中：`is_gold`（就是该题该找的块）**{kinds['is_gold']}**、"
        f"`unowned`（speakers 里没有具名角色）**{kinds['unowned']}**、"
        f"`other_named_char`（别人具名的场景）**{kinds['other_named_char']}**。",
        f"→ 假泄漏 {rep['read3_leaked_chunk_kinds']['false_leak_share']:.2%}、"
        f"真越界 {rep['read3_leaked_chunk_kinds']['true_cross_share']:.2%}。",
        "",
        "## 读数 4｜那份正则真正的战场在说话人侧，不在实体侧",
        "",
        f"全语料去重说话人 {speaker_read['distinct_speakers']} 个，其中命中 "
        f"`is_generic_speaker` 的 {speaker_read['generic_per_regex']} 个"
        f"（提及 {speaker_read['generic_per_regex_mentions']} 次）；另有 "
        f"{speaker_read['unmatched_numeric_suffix']} 个带罗马数字/甲乙丙丁后缀、"
        f"看着就是占位名却**没被正则盖住**（提及 "
        f"{speaker_read['unmatched_numeric_suffix_mentions']} 次），例如 "
        f"`{'、'.join(speaker_read['top_unmatched_examples'][:10])}`。"
        f"同类后缀里另有 "
        f"{speaker_read['numeric_suffix_excluded_because_registered']} 个名字"
        f"**已注册为「角色」实体**，已从缺口里剔除；这一桶必须拆开看："
        f"其中带罗马数字后缀的 "
        f"**{speaker_read['registered_role_entities_with_roman_suffix']} 个**"
        f"（提及 "
        f"{speaker_read['registered_role_entities_with_roman_suffix_mentions']} 次）"
        f"是**一定**的占位名，也就是 read1「正则命中 0」背后的真污染——"
        f"`{'、'.join(speaker_read['registered_role_entities_roman_suffix_examples'][:10])}`；"
        f"剩下的 甲乙丙丁/丁 后缀里则混着 康斯坦丁 这类真名，`[甲乙丙丁]$` 会把它们"
        f"误判成占位名，留着等于用同一个错口径去数泛称。",
        f"另有高频说话人未注册为「角色」实体："
        f"`{'、'.join(speaker_read['top_speakers_not_role_entities'][:10])}` —— "
        f"这类名字的块在「按具名角色归属」判定时会算进 `unowned`，read3 的假泄漏率"
        f"因此是**上界**。",
        "",
        "## 读数 6｜泛称词能不能当锚点（直接查 `alias_index`）",
        "",
        f"探 {read6['probed']} 个泛称/半泛称词，**{read6['hit_as_alias_key']} 个**"
        f"是 `alias_index` 的键：`{'、'.join(read6['hit_words']) or '（无）'}`；"
        f"没做键的：`{'、'.join(read6['miss_words'])}`。",
        "",
        "`link()` 只做「查询串 ⊇ 键」的包含匹配。**计划文档 §P3 问题① 的答案是"
        "『是』**：伙计/会长/上级/孩子们/无名者 都在 `alias_index` 里做键、且各自"
        "指向一个同名「角色」实体，所以泛称题**有锚点**，图通道会照常启动并把这个人"
        "不存在的『角色』的块铺进上下文——过滤器有靶子。",
        "",
        "## 读数 7｜实体侧『类别词当专名』的规模（不依赖人工名单的结构判据）",
        "",
        f"判据：{read7['criterion']}。2023 个「角色」实体名里符合的有 "
        f"**{read7['category_word_like']}** 个"
        f"（{read7['category_word_like_share']:.2%}）。"
        f"最典型：`{'、'.join(read7['top_examples'][:15])}`。",
        "",
        "样例 20 题的锚点逐个过三条口径（正则 / alias 键 / 结构嵌套）：",
        "",
        "| 题面角色 | `is_generic_speaker` | `alias_index` 键 | 指向实体 | 类型 | 嵌于更长名 |",
        "| --- | --- | --- | --- | --- | --- |",
    ] + [
        f"| {r['asked_role']} | {r['regex_generic']} | {r['is_alias_key']} "
        f"| {r['entity']} | {r['entity_type']} | {r['broader_uses']} |"
        for r in read7["sample_anchor_status"]
    ] + [
        "",
        "注意 read6 命中的 伙计/上级/孩子们 在这条结构判据下未必 ≥2（没有更长的同名"
        "角色名可嵌），所以**两条口径互补、都不能单独当泛称判据**：正则口径=0 是错的，"
        "结构口径会漏掉光杆类别词。而且这条结构口径自带假阳性——"
        "**安娜 / 威廉 / 丹** 这类真名也会嵌在更长的名字里（安娜贝尔、威廉姆斯），"
        "所以 119 是**上界**，不能直接当过滤名单用。",
        "",
        "## 读数 8｜落地前提：归属表覆盖率（owners 判据算不算得出来）",
        "",
        f"判据：{read8['criterion']}。说话人里**不在具名角色表**的有 "
        f"{read8['speakers_absent_from_role_table']} 个"
        f"（提及 {read8['absent_mentions']} 次，占全部提及 "
        f"{read8['absent_share_of_all_mentions']:.2%}），高频的如 "
        f"`{'、'.join(read8['top_absent_speakers'][:12])}`。",
        f"块级：全语料 {read8['chunks_total']} 块里 **owners 非空 "
        f"{read8['chunks_with_owners']} 块**、为空 "
        f"{read8['chunks_without_owners']} 块；"
        f"`category=='character'` 的 {read8['character_chunks_total']} 块里 "
        f"owners 非空 {read8['character_chunks_with_owners']} 块"
        f"（覆盖率 **{read8['character_ownership_coverage']:.2%}**）。",
        "",
        "这一列决定过滤器的形状：**owners 为空的块不能当「无主」直接放过，也不能当"
        "「别人的私知」滤掉**——L2.3 只统计 `character` 块，而这里 character 块的"
        "归属覆盖率就是过滤器的**可作用上限**。",
        "",
        "## 这两件事决定方案（不许跳过）",
        "",
        "1. **已量：28 个泄漏块里 89.29% 是 `other_named_char`（别人具名的场景），"
        "假泄漏只有 2+1 块 = 10.71%**——原计划担心的「判据把『块里没写这个名字』"
        "当成越界」**不是主要成分**，真越界是大头，过滤器原则上有的治。"
        "但 10.71% 里含 `is_gold` 2 块（`300cn/R200` 的两块 gold 由 卡戎/威利/士兵Ⅰ/"
        "士兵Ⅱ/沃尔克中校/帕蒂塔 说出），**按归属硬过滤会把答案块滤掉**，"
        "所以只能降权、不能剔除；且假泄漏率是上界（说话人未注册为实体的 "
        "`？？？/医生/士兵` 都算进了 `unowned`）。",
        "2. 靶子确实存在（泛称在做锚点，read6/read7），但**泛称判据必须重做**——"
        "现成的 `is_generic_speaker` 在实体侧命中 0，结构口径只覆盖 "
        f"{read7['category_word_like']} 个里的嵌套形态；靶子数量决定值不值得为此动排序；本诊断的结论是：改走 read3 的**块归属**"
        "（`speakers ∩ 具名角色表`），不以「题面词是不是泛称」为开关——归属可测、"
        "不需人工泛称名单，也不与 L2.3 同构（L2.3 问「块里有没有这个名字」，"
        "归属问「这块是谁的场景」），因此不构成同义反复刷数；",
        "3. 验收仍走两条腿：L2.3 照报 + confuse 认领率 / 双盲正确性不回退。",
        "",
        "> 只读脚本：不写图谱、不重建索引、不触 LLM/嵌入、不动检索参数。",
        "",
    ]
    # 逐锚点的实体侧泛称命中（read1 的样例侧补充，验「正则对 伙计/会长 一个都没命中」）
    per_anchor: dict[str, list[int]] = {}
    for r in rows_out:
        nm = r.get("asked_role") or "?"
        rec = per_anchor.setdefault(nm, [0, 0])
        rec[1] += 1
        if is_generic_speaker(nm):
            rec[0] += 1
    md.append("## 附｜样例锚点逐个过 `is_generic_speaker`")
    md.append("")
    for nm, (hits, seen) in sorted(per_anchor.items(), key=lambda kv: kv[1][0]):
        md.append(f"- `{nm}`：命中 {hits} / 出现 {seen} 次")
    md.append("")
    (R / "p3_rolefilter_prereq.md").write_text("\n".join(md), encoding="utf-8")
    rep["read5_anchor_regex"] = {nm: {"generic_hits": h, "appearances": s}
                                 for nm, (h, s) in per_anchor.items()}
    (R / "p3_rolefilter_prereq.json").write_text(
        json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[read1] 角色实体 {ent_read['role_entities']}，泛称 "
          f"{ent_read['generic_role_entities']}（{ent_read['generic_share']:.2%}）")
    print(f"[read2] 样例 {anchor['examples']}：泛称锚点 {anchor['generic_asked']}，"
          f"仅泛称锚点 {anchor['only_generic_anchor']}")
    print(f"[read3] 泄漏块 {dict(kinds)} 共 {n_chunks}；假泄漏 "
          f"{rep['read3_leaked_chunk_kinds']['false_leak_share']:.2%}、真越界 "
          f"{rep['read3_leaked_chunk_kinds']['true_cross_share']:.2%}")
    print(f"[read4] 说话人 {speaker_read['distinct_speakers']} 去重：正则泛称 "
          f"{speaker_read['generic_per_regex']}，漏网的数字后缀 "
          f"{speaker_read['unmatched_numeric_suffix']}"
          f"（提及 {speaker_read['unmatched_numeric_suffix_mentions']}）")
    print(f"[read5] 样例锚点正则命中 "
          f"{sum(v['generic_hits'] for v in rep['read5_anchor_regex'].values())}"
          f"/{len(rep['read5_anchor_regex'])} 个不同锚点名")
    print(f"[read6] 探 {read6['probed']} 个泛称词，作 `alias_index` 键的 "
          f"{read6['hit_as_alias_key']} 个：{'、'.join(read6['hit_words']) or '（无）'}")
    print(f"[read7] 结构口径「类别词当专名」 "
          f"{read7['category_word_like']}/{read7['role_entity_names']} "
          f"（{read7['category_word_like_share']:.2%}）："
          f"{'、'.join(read7['top_examples'][:8])}")
    print(f"[read8] character 块归属覆盖 "
          f"{read8['character_chunks_with_owners']}/"
          f"{read8['character_chunks_total']} = "
          f"{read8['character_ownership_coverage']:.2%}；"
          f"未注册的说话人 {read8['speakers_absent_from_role_table']} 个"
          f"（提及占 {read8['absent_share_of_all_mentions']:.2%}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
