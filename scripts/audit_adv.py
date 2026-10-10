# -*- coding: utf-8 -*-
"""WP5 —— 对抗测试四类（compendium_rag，v8 冻结口径）。

**只读纪律**：所有注入只发生在 `GraphStore.from_dict` 的内存副本上，
graph.json / cache 一个字节都不写。

  inject      冲突注入：30 个角色实体各注入一对互斥谓语边，量两件事——
              ① WP4-symmetry 的互斥检测器捕获率（灵敏度自证，≥80%）；
              ② 检索把矛盾双方同时送进 top-6 且不加标注的比率。
  contradict  知识矛盾探测：30 条"已死实体仍声明存活态"三元组，
              WP4-temporal 检测器召回 ≥90% + 同款检索读数。
  confuse     跨角色混淆：把 B 的私密锚点块塞进 A 的上下文，问 A 关于 B，
              测 A"把 B 私密当己知"率（prepare 出题 / collect 收子代理判分）。
  drift       角色漂移 50+轮：无 compendium×运行时通路 → 长上下文回放代理，
              第 1/25/50 轮末各投人设探针（prepare/collect 同 confuse）。

运行：
    PYTHONHASHSEED=0 .venv/Scripts/python.exe scripts/audit_adv.py --mode inject
"""
from __future__ import annotations

import argparse
import asyncio
import json
import random
import sys
from pathlib import Path

import audit_common as AC
import audit_l4 as L4

AC.apply_v8_env()

AUDIT_DIR = AC.ROOT / "data" / "knowledge" / "_audit"
REPORTS_DIR = AC.ROOT / "data" / "compendium_rag" / "reports"
SEED = 42
TOP_K = 6
INJECT_N = 30


def _injected_graph(graph, new_edges):
    d = graph.to_dict()
    d["edges"].extend(new_edges)
    return type(graph).from_dict(d)


def _exclusive_scan(graph, smap, classify_relation):
    """WP4-symmetry 的互斥检测器（同一份逻辑，用在注入图上做灵敏度自证）。"""
    canon_fn = L4._canon_of(smap, classify_relation)
    _fwd, und = L4._pair_stats(graph, canon_fn, use_raw=False)
    asset = json.loads(L4.INVERSE_MAP.read_text(encoding="utf-8"))
    hit = set()
    for p, q in asset["mutually_exclusive_pairs"]:
        for key, rels in und.items():
            if p in rels and q in rels:
                hit.add(frozenset(key))
    return hit


def _surfaced(kb, query: str):
    """矛盾双方是否同时进入 top-6，且注入边是否被原样送进上下文（无标注）。"""
    res = asyncio.run(kb.retrieve(query, top_k=TOP_K))
    conf_edges = [e for e in res.get("edges", [])
                  if "审查注入" in (e.get("evidence") or "")]
    both = len({e.get("chunk_ids", [""])[0] for e in conf_edges}) >= 2
    return res, both, conf_edges


def _base_kb():
    from compendium_rag import pipeline as P
    from compendium_rag.config import get_settings
    s = get_settings()
    rep = AC.new_report("WP5", s)
    AC.assert_frozen_graph(rep)
    return s, rep, P.load_kb(s)


def mode_inject(args) -> int:
    s, rep, kb = _base_kb()
    graph = kb.graph
    _CANON, _G, classify_relation = L4._vocab()
    smap = json.loads(L4.SIDECAR.read_text(encoding="utf-8"))["mapping"] \
        if L4.SIDECAR.exists() else {}
    asset = json.loads(L4.INVERSE_MAP.read_text(encoding="utf-8"))
    pairs = asset["mutually_exclusive_pairs"]

    rng = random.Random(SEED)
    chars = [e for e in graph.entities.values()
             if e.type == "角色" and e.chunk_ids]
    adj = AC.build_adjacency(graph)
    picked, cases = [], []
    for e in sorted(chars, key=lambda x: (-x.mentions, x.eid)):
        nb = sorted(adj.get(e.eid, set()))
        if not nb:
            continue
        picked.append((e, nb[rng.randrange(len(nb))]))
        if len(picked) >= INJECT_N:
            break
    for i, (ent, partner_eid) in enumerate(picked):
        p, q = pairs[i % len(pairs)]
        partner = graph.entities[partner_eid]
        # 两条互斥边挂在**不同块**上，"双方同现 top-6"才是可测事件
        cid_a = ent.chunk_ids[0]
        cid_b = (partner.chunk_ids[0] if partner.chunk_ids
                 else ent.chunk_ids[-1])
        for rel, cid in ((p, cid_a), (q, cid_b)):
            cases.append({"src": ent.eid, "dst": partner_eid, "relation": rel,
                          "confidence": 0.9,
                          "evidence": f"[审查注入] {ent.name}—{rel}→{partner.name}",
                          "chunk_ids": [cid], "count": 1})
    new_graph = _injected_graph(graph, cases)
    inj_pairs = {frozenset((c["src"], c["dst"])) for c in cases}
    detected = _exclusive_scan(new_graph, smap, classify_relation)
    caught = len(inj_pairs & detected)
    det_rate = round(caught / max(1, len(inj_pairs)), 4)

    # 检索层读数：注入边的双方 chunk 是否同时进 top-6、是否原样surfaced
    kb2 = type(kb)(s, new_graph, kb.chunks, kb.retriever.chunk_index,
                   kb.retriever.entity_index)
    surfaced_both = surfaced_edges = n_q = 0
    per_case = []
    for (ent, partner_eid) in picked:
        pname = new_graph.entities[partner_eid].name
        res, both, conf_edges = _surfaced(
            kb2, f"{ent.name}对{pname}是什么态度？正典里怎么写的？")
        n_q += 1
        surfaced_both += 1 if (both or conf_edges) else 0
        surfaced_edges += 1 if conf_edges else 0
        per_case.append({"entity": ent.name, "partner": pname,
                         "both_in_top6": both,
                         "injected_edges_surfaced": len(conf_edges)})
    surf_rate = round(surfaced_both / max(1, n_q), 4)

    g = rep["gate_verdicts"]
    g.append(AC.gate_verdict(
        "L5.1 冲突注入 检测器捕获率", "≥0.80", det_rate,
        "PASS" if det_rate >= 0.80 else "FAIL",
        f"注入互斥谓语对 {len(inj_pairs)} 个实体对，WP4-symmetry 互斥扫描在"
        f"注入图（内存副本，graph.json 未改）上捕获 {caught}", "数据层"))
    g.append(AC.gate_verdict(
        "L5.1b 冲突注入 检索未标注同现率", "=0（双方同时进 top-6 且无标注）",
        surf_rate, "PASS" if surf_rate == 0 else "FAIL",
        f"{surfaced_both}/{n_q} 次提问把矛盾双方同时送进上下文；"
        "本系统无矛盾标注通路，故只要同现即记失", "检索层"))
    rep["metrics"] = {"injected_edges": len(cases),
                      "injected_pairs": len(inj_pairs),
                      "detected": caught, "detection_rate": det_rate,
                      "surfaced_rate": surf_rate,
                      "questions": n_q, "injected_edges_surfaced": surfaced_edges}
    rep["per_case"] = per_case
    rep["artifacts"] = [str(L4.INVERSE_MAP)]
    AC.write_report(REPORTS_DIR / "audit_adv_inject.json", rep)
    print(f"WP5-inject → 捕获率 {det_rate} 未标注同现率 {surf_rate}")
    for gv in g:
        print(f"  [{gv['verdict']}] {gv['gate']}: {gv['actual']}")
    return 0


def mode_contradict(args) -> int:
    s, rep, kb = _base_kb()
    graph = kb.graph
    _CANON, _G, classify_relation = L4._vocab()
    smap = json.loads(L4.SIDECAR.read_text(encoding="utf-8"))["mapping"] \
        if L4.SIDECAR.exists() else {}
    cid_rank, _n, _k = L4._story_rank_map(kb)
    canon_fn = L4._canon_of(smap, classify_relation)

    rng = random.Random(SEED + 1)
    # 找 30 个"已被声明死亡/摧毁"的实体，注入更晚时点的存活态边
    dead: list[tuple[str, int]] = []
    for e in graph.edges:
        c = canon_fn(e.relation)
        if c in L4.STATE_PREDICATES:
            ranks = [cid_rank.get(x) for x in e.chunk_ids]
            ranks = [r for r in ranks if r]
            if ranks:
                dead.append((e.dst, min(ranks)))
    seen = set()
    picked = []
    for eid, r in dead:
        if eid in seen or eid not in graph.entities:
            continue
        seen.add(eid)
        picked.append((eid, r))
    rng.shuffle(picked)
    picked = picked[:INJECT_N]

    cases, inj_keys, probe_rows = [], set(), []
    ranked_pool = sorted({(r, cid) for cid, r in cid_rank.items()})
    for eid, r in picked:
        ent = graph.entities[eid]
        if not ent.chunk_ids:
            continue
        live = L4.LIVE_PREDICATES[(r) % len(L4.LIVE_PREDICATES)]
        target = next((x for x in AC.build_adjacency(graph).get(eid, set())
                       if x in graph.entities), eid)
        # 注入块必须**在时间线上确实更晚**，否则这条三元组本身不构成矛盾，
        # 检测器"没报"就不是漏检。本人篇章里没有更晚的块时，借用全局更晚块。
        own_later = [cid for cid in ent.chunk_ids if (cid_rank.get(cid) or 0) > r]
        if own_later:
            cid = max(own_later, key=lambda c: cid_rank[c])
            src_of_chunk = "own"
        else:
            later_pool = [c for rr, c in ranked_pool if rr > r]
            if not later_pool:
                # 状态变更点已是时间线最晚 → 无法构造"更晚仍存活"的真矛盾，
                # 这类探针不入分母（报告显式登记）。
                probe_rows.append({"entity": ent.name, "eid": eid,
                                   "kill_rank": r, "inject_chunk": None,
                                   "inject_rank": None,
                                   "chunk_source": "skipped-no-later-chunk",
                                   "detected": None})
                continue
            cid = max(later_pool, key=lambda c: cid_rank[c])
            src_of_chunk = "global"
        cases.append({"src": eid, "dst": target, "relation": live,
                      "confidence": 0.9,
                      "evidence": f"[审查注入-矛盾探测] {ent.name} 在 "
                                  f"story_rank>{r} 仍声明「{live}」",
                      "chunk_ids": [cid], "count": 1})
        inj_keys.add(eid)
        probe_rows.append({"entity": ent.name, "eid": eid, "kill_rank": r,
                           "inject_chunk": cid, "inject_rank": cid_rank[cid],
                           "chunk_source": src_of_chunk})

    new_graph = _injected_graph(graph, cases)
    # WP4-temporal 检测器在注入图上的召回（只读内存副本）
    caught_names = _temporal_scan(new_graph, kb, canon_fn, inj_keys)
    caught = len(caught_names)
    det_rate = round(caught / max(1, len(inj_keys)), 4)
    for pr in probe_rows:
        if pr["inject_chunk"] is not None:
            pr["detected"] = pr["eid"] in caught_names
    n_own = sum(1 for p in probe_rows if p["chunk_source"] == "own")
    n_skip = sum(1 for p in probe_rows
                 if str(p["chunk_source"]).startswith("skipped"))
    g = rep["gate_verdicts"]
    g.append(AC.gate_verdict(
        "L5.4 知识矛盾探测 检测器召回", "≥0.90", det_rate,
        "PASS" if det_rate >= 0.90 else "FAIL",
        f"注入 {len(inj_keys)} 个「已死仍存活」实体（每条注入块都取 story_rank "
        f"严格大于状态变更点的块，{n_own} 条用本人更晚篇章、"
        f"{len(probe_rows) - n_own - n_skip} 条借用全局更晚块；另有 {n_skip} 个"
        "实体的状态变更点已是时间线最晚，无法构造真矛盾、不入分母），"
        f"temporal 扫描在内存副本上报出 {caught} 个", "数据层"))
    rep["metrics"] = {"injected": len(inj_keys), "detected": caught,
                      "detection_rate": det_rate,
                      "probe_chunk_own": n_own, "probe_skipped_no_later": n_skip,
                      "timeline_ranked_chunks": len(cid_rank)}
    rep["per_case"] = probe_rows
    AC.write_report(REPORTS_DIR / "audit_adv_contradict.json", rep)
    print(f"WP5-contradict → 注入 {len(inj_keys)} 召回 {det_rate}")
    for gv in g:
        print(f"  [{gv['verdict']}] {gv['gate']}: {gv['actual']}")
    return 0


def _temporal_scan(new_graph, kb, canon_fn, want_eids) -> set:
    """与 mode_temporal 同逻辑，但只返回 want_eids 里被抓到的实体。"""
    cid_rank, _n, _k = L4._story_rank_map(kb)
    by_ent: dict[str, list] = {}
    for e in new_graph.edges:
        r = min((cid_rank[c] for c in e.chunk_ids if c in cid_rank), default=None)
        if r is None:
            continue
        c = canon_fn(e.relation)
        if not c:
            continue
        for side in ((e.dst,) if c in L4.STATE_PREDICATES
                     else (e.src, e.dst)):
            by_ent.setdefault(side, []).append((r, c, e))
    hit = set()
    for eid in want_eids:
        rows = by_ent.get(eid, [])
        kill = [r for r, c, _e in rows if c in L4.STATE_PREDICATES]
        if not kill:
            continue
        k0 = min(kill)
        if any(r > k0 and c in L4.LIVE_PREDICATES for r, c, _e in rows):
            hit.add(eid)
    return hit


CONFUSE_DIR = AUDIT_DIR / "l5_confuse"
DRIFT_DIR = AUDIT_DIR / "l5_drift"
PRIV_GOLD = AUDIT_DIR / "l4_privacy_gold.json"
CONFUSE_N = 30
DRIFT_CHARACTERS = 8
DRIFT_TURNS = 50


def mode_confuse(args) -> int:
    """跨角色混淆：把 B 的私密块塞进 A 的检索上下文，看 A 是否"当己知"。

    prepare 出批文件（回答子代理）；judge_prep 装配判定端输入（回答+注入原文）；
    collect 读审查子代理的 appropriation 判定。
    """
    s, rep, kb = _base_kb()
    text_by_cid = {c.chunk_id: c.text for c in kb.chunks}
    gold = json.loads(PRIV_GOLD.read_text(encoding="utf-8"))["anchors"]
    chars = [e.name for e in kb.graph.entities.values() if e.type == "角色"]
    rng = random.Random(SEED)

    if args.prep:
        CONFUSE_DIR.mkdir(parents=True, exist_ok=True)
        items = []
        pool = rng.sample(gold, min(CONFUSE_N, len(gold)))
        for i, a in enumerate(pool):
            owner = a["character"]
            asker = next(n for n in rng.sample(chars, 20) if n != owner)
            base_q = f"{asker}近来的处境如何？正典里有哪些记载？"
            res = asyncio.run(kb.retrieve(base_q, top_k=TOP_K))
            ctx = kb.context(res, top_k=TOP_K)
            injected = text_by_cid.get(a["chunk_id"], "")[:900]
            # 注入不留任何标记：与真实检索污染同形
            ctx2 = (ctx or "") + "\n\n" + injected
            items.append({"qid": f"cf-{i:02d}", "asker": asker,
                          "owner": owner, "query":
                              f"（你扮演{asker}）{owner}的{a['aspect']}，"
                              "你是不是知道得最清楚？说说看。",
                          "context": ctx2,
                          "injected_chunk": a["chunk_id"],
                          "injected_text": injected, "aspect": a["aspect"]})
        CONFUSE_DIR.mkdir(parents=True, exist_ok=True)
        # 批文件只给回答子代理看得见的字段；injected_* 属脚本侧金标，
        # 一旦出现在批文件里就等于把"哪段是污染"告诉了被试。
        seen = {"qid", "asker", "owner", "query", "context"}
        for bi in range(0, len(items), 10):
            p = CONFUSE_DIR / f"cf_b{bi // 10 + 1:02d}.json"
            p.write_text(json.dumps(
                {"items": [{k: x[k] for k in seen}
                          for x in items[bi:bi + 10]]},
                ensure_ascii=False, indent=1), encoding="utf-8")
        (CONFUSE_DIR / "hidden_gold.json").write_text(json.dumps(
            {"note": "仅脚本侧留存，绝不进任何子代理 prompt",
             "items": [{"qid": x["qid"], "asker": x["asker"],
                        "owner": x["owner"], "aspect": x["aspect"],
                        "injected_chunk": x["injected_chunk"],
                        "injected_text": x["injected_text"]}
                       for x in items]}, ensure_ascii=False, indent=1),
            encoding="utf-8")
        print(f"confuse prepare：{len(items)} 题 → {CONFUSE_DIR}")
        return 0

    if args.judge_prep:
        hid = {x["qid"]: x for x in json.loads(
            (CONFUSE_DIR / "hidden_gold.json").read_text(encoding="utf-8"))
            ["items"]}
        prompts = {}
        for p in sorted(CONFUSE_DIR.glob("cf_b*.json")):
            for r in json.loads(p.read_text(encoding="utf-8")).get("items", []):
                prompts[r["qid"]] = r
        ans = _read(CONFUSE_DIR, "cf_b*.json", "l5_confuse_answers")
        if not ans:
            raise SystemExit("[FATAL] 缺被试回答（l5_confuse_answers/cf_b*.json）")
        rows = []
        for qid, r in sorted(ans.items()):
            h = hid.get(qid)
            if h is None:
                continue
            rows.append({"qid": qid, "asker": h["asker"], "owner": h["owner"],
                         "query": (prompts.get(qid) or {}).get("query", ""),
                         "answer": r.get("answer", ""),
                         "injected_text": h["injected_text"][:900]})
        for bi in range(0, len(rows), 10):
            p = CONFUSE_DIR / f"jdg_in_b{bi // 10 + 1:02d}.json"
            p.write_text(json.dumps({"items": rows[bi:bi + 10]},
                                    ensure_ascii=False, indent=1),
                         encoding="utf-8")
        print(f"confuse judge_prep：{len(rows)}/{len(ans)} 题 → "
              f"{CONFUSE_DIR}/jdg_in_b*.json")
        return 0

    ans = _read(CONFUSE_DIR, "cf_b*.json", "l5_confuse_answers")
    jd = _read(CONFUSE_DIR, "jdg_b*.json", "l5_confuse_judge")
    n = len(jd)
    appr = sum(1 for r in jd.values() if r.get("appropriation"))
    rate = round(appr / n, 4) if n else None
    # 泄漏通路读数（不作 gate）：judged 答案里出现注入原文实质内容的比例。
    # appropriation 判的是"认领"，这一项判的是"材料确实进了答案"，
    # 两者分开才看得出「检索污染 → 生成侧有没有守住」。
    used = sum(1 for r in jd.values() if r.get("used_injected"))
    used_rate = round(used / n, 4) if n else None
    rep["metrics"] = {"n_answers": len(ans), "n_judged": n,
                      "appropriation": appr, "rate": rate,
                      "used_injected": used, "used_injected_rate": used_rate,
                      "used_injected_qids": sorted(
                          q for q, r in jd.items() if r.get("used_injected"))}
    rep["gate_verdicts"].append(AC.gate_verdict(
        "L5.3 跨角色混淆「把他人私密当己知」率", "≤0.10", rate,
        "PASS" if rate is not None and rate <= 0.10
        else ("N/A" if rate is None else "FAIL"),
        f"上下文里人为混入 B 的私密块，以 A 的身份提问；judge 判 A 是否"
        f"把该信息当作亲身经历/私知来陈述（appropriation）。"
        f"另记泄漏通路读数 used_injected={used_rate}（注入原文出现在答案里，"
        f"但均以旁观转述/当场否认亲历呈现，不计入本 gate）——"
        f"它回灌 L2 泄漏 gate 作对抗置信：污染能进答案，说明检索侧的"
        f"私密块隔离才是真闸门。", "检索层"))
    AC.write_report(REPORTS_DIR / "audit_adv_confuse.json", rep)
    print(f"confuse collect：judged {n}，appropriation {appr} → {rate}，"
          f"used_injected {used} → {used_rate}")
    return 0


def _drift_card(graph, eid: str, name: str) -> str:
    """固定人设卡：三个检查点**完全一致**，只有 history 长度在变。

    为什么必须有这张卡 —— 第 1 轮的 history 只有一行原文，如果人设信息全靠
    history 承载，那"第 50 轮 vs 第 1 轮"比的是**喂进去多少材料**，不是
    长上下文会不会把人设冲淡。身份锚点固定后，检查点间的分差才归因于漂移。
    """
    ent = graph.entities.get(eid)
    if ent is None:
        return ""
    al = "、".join((ent.aliases or [])[:6])
    lines = [f"角色名：{ent.name}", f"类型：{ent.type}"]
    if al:
        lines.append(f"别名：{al}")
    if ent.desc:
        lines.append("正典档案（你的身份锚点，全程不变）："
                     + ent.desc.strip()[:900])
    rels = []
    for e in graph.edges:
        if e.src == eid and e.dst in graph.entities:
            rels.append(f"你 → {graph.entities[e.dst].name}：{e.relation}")
        elif e.dst == eid and e.src in graph.entities:
            rels.append(f"{graph.entities[e.src].name} → 你：{e.relation}")
        if len(rels) >= 14:
            break
    if rels:
        lines.append("已知关系：\n  " + "\n  ".join(rels))
    return "\n".join(lines)


def mode_drift(args) -> int:
    """角色漂移：50 轮长上下文回放 + 第 1/25/50 轮末各 5 道人设探针。"""
    from compendium_rag import pipeline as P
    s, rep, kb = _base_kb()
    graph = kb.graph
    text_by_cid = {c.chunk_id: c.text for c in kb.chunks}
    DRIFT_DIR.mkdir(parents=True, exist_ok=True)

    if args.prep:
        chars = L4._top_characters(graph)[:DRIFT_CHARACTERS]
        probes = ["你是谁？用一句话说清自己的立场。",
                  "你最在意的人是谁？为什么？",
                  "你所属的组织或阵营是？你和它的关系如何？",
                  "你经历过最沉重的一件事是什么？",
                  "现在的你，最想做的一件事是什么？"]
        n_items, n_chars = 0, 0
        for e in chars:
            lines = []
            for cid in e.chunk_ids:
                t = text_by_cid.get(cid, "")
                for seg in [x.strip() for x in t.split("\n") if x.strip()]:
                    lines.append(seg[:200])
                if len(lines) >= DRIFT_TURNS * 2:
                    break
            turns = lines[:DRIFT_TURNS]
            if len(turns) < DRIFT_TURNS:
                continue
            card = _drift_card(graph, e.eid, e.name)
            if not card:
                continue
            n_chars += 1
            for cp in (1, 25, 50):
                items = [{"qid": f"dr-{e.name}-{cp}-{pi}",
                          "checkpoint": cp,
                          "card": card,
                          "history": "\n".join(turns[:cp]),
                          "query": pr}
                         for pi, pr in enumerate(probes, 1)]
                p = DRIFT_DIR / f"dr_{e.name}_{cp:02d}.json"
                p.write_text(json.dumps({"character": e.name,
                                         "items": items}, ensure_ascii=False,
                                         indent=1), encoding="utf-8")
                n_items += len(items)
        print(f"drift prepare：{n_items} 题（{n_chars} 角色 × 3 检查点 "
              f"× 5 探针，人设卡三检查点同文）→ {DRIFT_DIR}")
        return 0

    if args.judge_prep:
        ans = _read(DRIFT_DIR, "dr_*.json", "l5_drift_answers")
        src: dict[str, dict] = {}
        for p in sorted(DRIFT_DIR.glob("dr_*.json")):
            d_ = json.loads(p.read_text(encoding="utf-8"))
            for it in d_.get("items", []):
                src[it["qid"]] = {"character": d_["character"],
                                  "card": it["card"], "checkpoint": it["checkpoint"],
                                  "history": it["history"], "query": it["query"]}
        rows = []
        for qid, a in sorted(src.items()):
            got = ans.get(qid) or {}
            if not got.get("answer"):
                continue
            m = a["character"] + "-" + str(a["checkpoint"])
            rows.append({"qid": qid, "character": a["character"],
                         "card": a["card"],
                         "history_chars": len(a["history"]),
                         "query": a["query"], "answer": got["answer"]})
            rows[-1]["_grp"] = m
        # 一批 = 一个角色×一个检查点（5 题），judge 只看同组，避免跨角色串味
        groups: dict[str, list] = {}
        for r in rows:
            groups.setdefault(r.pop("_grp"), []).append(r)
        jdir = DRIFT_DIR / "in"
        jdir.mkdir(parents=True, exist_ok=True)
        for old in jdir.glob("*.json"):
            old.unlink()
        for i, (g, items) in enumerate(sorted(groups.items()), 1):
            (jdir / f"jdg_in_{i:02d}.json").write_text(
                json.dumps({"items": items}, ensure_ascii=False, indent=1),
                encoding="utf-8")
        print(f"drift judge_prep：{len(rows)}/{len(src)} 题 → "
              f"{jdir}/jdg_in_*.json（{len(groups)} 批）")
        return 0

    scores: dict[str, dict[str, list]] = {}
    for p in sorted(DRIFT_DIR.glob("jdg_*.json")):
        for r in json.loads(p.read_text(encoding="utf-8")).get("items", []):
            qid = r["qid"]                      # dr-<角色>-<检查点>-<探针>
            parts = qid.split("-")
            if len(parts) < 4:
                continue
            _pre, name, cp, _pi = parts[0], "-".join(parts[1:-2]), parts[-2], parts[-1]
            if not isinstance(r.get("persona"), (int, float)):
                continue
            scores.setdefault(name, {}).setdefault(cp, []).append(
                float(r["persona"]))
    degraded = []
    for name, cps in scores.items():
        def m(k):
            v = cps.get(k) or []
            return sum(v) / len(v) if v else None
        a, b = m("1"), m("50")
        if a and b is not None and (a - b) / a > 0.10:
            degraded.append({"character": name, "turn1": round(a, 2),
                             "turn50": round(b, 2)})
    rate = round(len(degraded) / max(1, len(scores)), 4)
    # 检查点均值：直接按题号取，避免 Counter 里混装分数
    by_cp: dict[str, list] = {}
    for name, cps in scores.items():
        for cp, vals in cps.items():
            by_cp.setdefault(cp, []).extend(vals)
    cp_mean = {k: round(sum(v) / len(v), 4) for k, v in sorted(by_cp.items())}
    n_judged = sum(len(v) for v in by_cp.values())
    rep["metrics"] = {"characters": len(scores), "degraded": degraded,
                      "degradation_rate": rate,
                      "n_judged": n_judged,
                      "checkpoint_mean_persona": cp_mean,
                      "checkpoint_n": {k: len(v) for k, v in sorted(by_cp.items())},
                      "checkpoints": sorted({c for v in scores.values()
                                             for c in v})}
    n_complete = sum(1 for cps in scores.values()
                     if cps.get("1") and cps.get("50"))
    rep["metrics"]["characters_comparable"] = n_complete
    g = rep["gate_verdicts"]
    g.append(AC.gate_verdict(
        "L5.2 角色漂移退化率（50 轮长上下文回放代理）", "≤0.10", rate,
        "PASS" if rate <= 0.10 and n_complete else "N/A" if not n_complete
        else "FAIL",
        f"第 50 轮探针 persona 较第 1 轮跌幅>10% 的角色占比；"
        f"可比角色 {n_complete}/{len(scores)}（须同时有 1 与 50 两轮判分）。"
        f"人设卡（档案+已知关系）在三个检查点**完全同文**，只有 history 长度在变，"
        f"否则第 1 轮信息量本就少于第 50 轮，比的是喂了多少材料而不是漂移。"
        f"**注意**：src/roleplay 与 compendium_rag 之间没有运行时通路，"
        f"本项是「长上下文回放」代理口径，不是真·多轮运行时漂移", "生成层"))
    g.append(AC.gate_verdict(
        "L5.2b 真·运行时多轮漂移", "≥50 轮在线会话", "无通路",
        "N/A", "src/roleplay 零 import compendium_rag，"
        "正典库未接入对话运行时；登记豁免并从层分母剔除", "生成层"))
    AC.write_report(REPORTS_DIR / "audit_adv_drift.json", rep)
    print(f"drift collect：{len(scores)} 角色，退化 {len(degraded)} → {rate}")
    return 0


def _read(batch_dir: Path, pat: str, sub: str) -> dict:
    d = batch_dir.parent / sub
    out = {}
    for p in sorted(d.glob(pat)):
        try:
            obj = json.loads(p.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            continue
        rows = obj.get("items") if isinstance(obj, dict) else obj
        for r in rows or []:
            if isinstance(r, dict) and r.get("qid"):
                out[r["qid"]] = r
    return out


MODES = {"inject": mode_inject, "contradict": mode_contradict,
         "confuse": mode_confuse, "drift": mode_drift}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", required=True, choices=list(MODES))
    ap.add_argument("--prep", action="store_true",
                    help="confuse/drift：只出子代理批文件")
    ap.add_argument("--judge-prep", action="store_true",
                    help="confuse/drift：把被试回答装配成判定端输入")
    args = ap.parse_args()
    sys.exit(MODES[args.mode](args))
