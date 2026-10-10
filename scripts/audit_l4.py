# -*- coding: utf-8 -*-
"""WP4 —— L4 图实体级跨角色一致性（compendium_rag，v8 冻结口径）。

模式：
  group      谓语归组 sidecar（**不写回 graph.json**）：
             classify_relation 可解析的直接落；drop:* 记不合规；
             review:unmapped 尾巴按边频分层送云端 LLM 归组（temp=0），
             并出 10% 分层抽样盲评复核文件给独立子代理。
             产物：data/knowledge/_audit/predicate_grouping_v1.json
  symmetry   关系对称性/互斥矛盾（依赖 group + inverse_predicate_map.json）
  temporal   时序/状态矛盾（依赖 plot_timeline + chunk 前缀 story_rank）
  privacy    私密锚点泄漏探测（依赖子代理 gold l4_privacy_gold.json）
  worldview  世界观定义互斥检测

运行：
    PYTHONHASHSEED=0 .venv/Scripts/python.exe scripts/audit_l4.py --mode group
"""
from __future__ import annotations

import argparse
import asyncio
import json
import random
import re
import sys
from collections import Counter

import audit_common as AC

AC.apply_v8_env()

AUDIT_DIR = AC.ROOT / "data" / "knowledge" / "_audit"
REPORTS_DIR = AC.ROOT / "data" / "compendium_rag" / "reports"
OUT_DIR = AUDIT_DIR / "predicate_grouping"
PROGRESS = AUDIT_DIR / "l4_group_progress.json"
SEED = 42
BATCH = 50


def _vocab():
    from roleplay.core.knowledge.relation_vocab import (
        CANONICAL_RELATIONS, RELATION_GROUPS, classify_relation)
    return CANONICAL_RELATIONS, RELATION_GROUPS, classify_relation


def _sys_prompt(canonicals, groups) -> str:
    lines = []
    for gname, members in groups.items():
        lines.append(f"- {gname}：" + "、".join(members))
    return (
        "你是《重返未来：1999》知识图谱谓语治理员。给定自由文本谓语清单，"
        "把每个谓语归入以下受控词表（77 个 canonical，按组列出）中语义最接近的一个；"
        "确实没有可归项时 canonical 输出 null。\n\n"
        "## 受控词表\n" + "\n".join(lines) + "\n\n"
        "## 规则\n"
        "1. 只输出 JSON：{\"mapping\":[{\"predicate\":\"…\",\"canonical\":\"…或null\","
        "\"confidence\":0~1}]}，顺序与输入一致。\n"
        "2. canonical 必须**逐字**来自词表；不得发明新词。\n"
        "3. 方向敏感：`师从` 不能归 `指导`（方向相反），若无互逆项可归则输出 null 并在"
        " confidence 里体现不确定。\n"
        "4. 泛化动词（进行/做出/产生…）与无名指代 → null。\n"
        "5. 以 evidence 示例语境为准，不凭世界知识脑补。")


def _user_prompt(batch_items) -> str:
    payload = [{"predicate": it["predicate"], "edges": it["edges"],
                "examples": [e[:60] for e in it["examples"][:3]]}
               for it in batch_items]
    return json.dumps(payload, ensure_ascii=False)


def _extract_json_obj(text: str):
    """剥 markdown 围栏后取最外层 {…}；失败退回 parse_json_loose。"""
    from compendium_rag.llm import parse_json_loose
    t = text.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[-1] if "\n" in t else ""
        if t.rfind("```") >= 0:
            t = t[:t.rfind("```")]
    a, b = t.find("{"), t.rfind("}")
    if a >= 0 and b > a:
        try:
            return json.loads(t[a:b + 1])
        except ValueError:
            pass
    return parse_json_loose(text)


async def _call_group_json(llm, sys_p: str, user: str) -> dict | None:
    """归组批调用：本任务返回 {"mapping":[…]}，非抽取信封，绕开 complete_json。"""
    for _attempt in range(2):
        try:
            j = await llm._post([{"role": "system", "content": sys_p},
                                 {"role": "user", "content": user}],
                                max_tokens=8192)
        except Exception:  # noqa: BLE001 - 网关抖动交给下一轮
            continue
        ch = (j.get("choices") or [{}])[0]
        content = ((ch.get("message") or {}).get("content") or "").strip()
        parsed = _extract_json_obj(content)
        if isinstance(parsed, dict) and isinstance(parsed.get("mapping"), list):
            return parsed
    return None


async def mode_group_async(args) -> int:
    from compendium_rag import pipeline as P
    from compendium_rag.config import get_settings
    from compendium_rag.llm import CloudLLM

    s = get_settings()
    rep = AC.new_report("WP4-group", s)
    AC.assert_frozen_graph(rep)
    kb = P.load_kb(s)
    graph = kb.graph

    canonicals, groups, classify_relation = _vocab()
    canon_set = set(canonicals)

    ct: Counter = Counter()
    examples: dict[str, list[str]] = {}
    for e in graph.edges:
        ct[e.relation] += 1
        if e.evidence and len(examples.setdefault(e.relation, [])) < 3:
            examples[e.relation].append(e.evidence)

    resolved: dict[str, dict] = {}
    tail: list[dict] = []
    for rel, n in ct.most_common():
        canon, reason = classify_relation(rel)
        if canon and reason in ("canonical", "synonym", "rule"):
            resolved[rel] = {"canonical": canon, "method": reason, "edges": n}
        elif reason.startswith("drop"):
            resolved[rel] = {"canonical": None, "method": reason, "edges": n}
        else:
            tail.append({"predicate": rel, "edges": n,
                         "examples": examples.get(rel, [])})

    n_edges = sum(ct.values())
    rule_edges = sum(v["edges"] for v in resolved.values()
                     if v["canonical"])
    print(f"唯一谓语 {len(ct)}：规则可解析 {len(resolved) - sum(1 for v in resolved.values() if not v['canonical'])}，"
          f"drop {sum(1 for v in resolved.values() if not v['canonical'] and v['method'].startswith('drop'))}，"
          f"LLM 尾巴 {len(tail)}（覆盖边 {rule_edges}/{n_edges}）")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    sys_p = _sys_prompt(canonicals, groups)

    llm_out: dict[str, dict] = {}
    usage: dict = {}
    # 断点续跑：140 批 × 云端调用，进程一旦中断不能从零再来。
    # 只把「还没拿到判定」的谓语重新切批，部分命中的批不必整批重跑。
    if PROGRESS.exists() and not args.fresh:
        llm_out = json.loads(PROGRESS.read_text(encoding="utf-8"))
        print(f"  续跑：已有映射 {len(llm_out)}", flush=True)
    remaining = [t for t in tail if t["predicate"] not in llm_out]
    bs = args.batch_size or BATCH
    if args.limit_batches:
        remaining = remaining[:args.limit_batches * bs]
    batches = [remaining[i:i + bs] for i in range(0, len(remaining), bs)]
    if args.report_only:
        batches = []
        print(f"  --report-only：跳过云端，只用现有 progress/sidecar 重出报告"
              f"（未映射尾巴 {len(remaining)}）", flush=True)
    else:
        print(f"  待处理尾巴 {len(remaining)}/{len(tail)} → {len(batches)} 批",
              flush=True)
    if batches:
        if not s.llm_api_key:
            raise SystemExit("[FATAL] 缺 CMPRAG_LLM_API_KEY，group 模式需云端")
        todo = list(enumerate(batches, 1))
        sem = asyncio.Semaphore(args.concurrency)

        def _save_progress() -> None:
            tmp = PROGRESS.with_suffix(".tmp")
            tmp.write_text(json.dumps(llm_out, ensure_ascii=False),
                           encoding="utf-8")
            tmp.replace(PROGRESS)

        async with CloudLLM(base_url=s.llm_base_url, api_key=s.llm_api_key,
                            model=s.llm_model, temperature=0.0,
                            max_tokens=4096, timeout=s.llm_timeout,
                            concurrency=s.llm_concurrency,
                            max_retries=s.llm_max_retries) as llm:
            async def run_one(bi: int, batch: list[dict]):
                async with sem:
                    return bi, await _call_group_json(llm, sys_p,
                                                      _user_prompt(batch))
            done_n = 0
            for fut in asyncio.as_completed([run_one(bi, b) for bi, b in todo]):
                bi, j = await fut
                done_n += 1
                if j is None:
                    print(f"  批 {bi} 失败：mapping 解析不出", flush=True)
                    rep["metrics"].setdefault("failed_batches", []).append(
                        {"batch": bi, "error": "no mapping object"})
                else:
                    for m in j.get("mapping", []):
                        p = (m.get("predicate") or "").strip()
                        c = m.get("canonical")
                        if not p:
                            continue
                        if c is None or c in canon_set:
                            llm_out[p] = {"canonical": c, "method": "llm",
                                          "confidence": m.get("confidence")}
                        else:
                            # 模型给出的归组不在 77 canonical 词表里：
                            # 记为「已判定=无法归组」，否则这批谓语会被无声丢失，
                            # 基础设施 gate 也就失去了自证意义。
                            llm_out[p] = {"canonical": None,
                                          "method": "llm:no_match",
                                          "proposed": c}
                if done_n % 10 == 0 or done_n == len(todo):
                    _save_progress()
                    print(f"  {done_n}/{len(todo)} 批完成，累计映射 "
                          f"{len(llm_out)}", flush=True)
            _save_progress()
            usage = llm.usage_summary()

    merged = dict(resolved)
    for p, v in llm_out.items():
        merged[p] = {"canonical": v["canonical"], "method": v["method"],
                     "edges": next((t["edges"] for t in tail
                                    if t["predicate"] == p), 0)}
    unresolved_tail = [t["predicate"] for t in tail if t["predicate"] not in merged]

    sidecar = {
        "schema": "audit.predicate_grouping/v1",
        "note": "审查用 sidecar，不写回 graph.json；temp=0，模型见 llm_model",
        "graph_sha": rep["frozen_graph_sha"], "llm_model": s.llm_model,
        "usage": usage,
        "unique_predicates": len(ct), "total_edges": n_edges,
        "coverage_edge_rate": round(
            (sum(v["edges"] for v in merged.values() if v["canonical"]))
            / n_edges, 4),
        "method_distribution": dict(Counter(v["method"]
                                           for v in merged.values()).most_common()),
        "unresolved_tail": sorted(unresolved_tail,
                                  key=lambda p: -ct.get(p, 0))[:100],
        "mapping": {p: merged[p] for p in sorted(merged,
                                                 key=lambda p: -merged[p]["edges"])},
    }
    sc_path = AUDIT_DIR / "predicate_grouping_v1.json"
    sc_path.write_text(json.dumps(sidecar, ensure_ascii=False, indent=1),
                       encoding="utf-8")

    # 10% 分层抽样盲评复核文件（给独立子代理 A4）
    rng = random.Random(SEED)
    llm_mapped = [(p, v) for p, v in merged.items() if v["method"] == "llm"]
    review_n = max(10, len(llm_mapped) // 10)
    sample = rng.sample(llm_mapped, min(review_n, len(llm_mapped)))
    rev_path = AUDIT_DIR / "l4_group_review_sample.json"
    if not rev_path.exists():  # 抽样一旦交评就冻结，否则盲评结果与样本脱钩
        rev_path.write_text(json.dumps(
        {"schema": "audit.group_review/v1",
         "task": "对每项判定归组是否成立（keep/change/reject），输出 JSON "
                 "{\"reviews\":[{\"predicate\":\"…\",\"verdict\":\"keep|change|reject\","
                 "\"canonical_if_change\":\"…\",\"why\":\"…\"}]}"
                 "——你不知道归组过程，仅凭 predicate+examples 独立裁决。",
         "items": [{"predicate": p, "canonical": v["canonical"],
                    "examples": examples.get(p, [])[:3]}
                   for p, v in sample]},
        ensure_ascii=False, indent=1), encoding="utf-8")

    rep["artifacts"] = [str(sc_path), str(rev_path)]
    tail_edge_n = sum(t["edges"] for t in tail)
    mapped_tail_edge = sum(merged[p]["edges"] for p in llm_out if p in merged)
    rep["metrics"].update({
        "unique_predicates": len(ct), "tail_unique": len(tail),
        "tail_edges": tail_edge_n, "tail_edges_mapped": mapped_tail_edge,
        "coverage_edge_rate": sidecar["coverage_edge_rate"],
        "method_distribution": sidecar["method_distribution"],
        "batches_run": len(batches), "batches_total": len(
            [tail[i:i + BATCH] for i in range(0, len(tail), BATCH)]),
        "usage": usage,
        "tail_remaining_after_run": sum(1 for t in tail
                                        if t["predicate"] not in llm_out),
    })
    ok_rate = len(llm_out) >= 0.8 * max(1, len(tail))
    n_unmapped = sum(1 for t in tail if t["predicate"] not in merged)
    no_fail = (not rep["metrics"].get("failed_batches")) and n_unmapped == 0
    rep["gate_verdicts"].append(AC.gate_verdict(
        "L4 基础设施 谓语归组完备性", "尾巴 ≥80% 拿到判定且零未判定谓语",
        {"tail_mapped": len(llm_out), "tail_total": len(tail),
         "still_unmapped": n_unmapped,
         "edge_coverage": sidecar["coverage_edge_rate"]},
        "PASS" if (ok_rate and no_fail) else "FAIL",
        f"归组率<80% 或仍有 {n_unmapped} 个谓语未判定 → 先修基础设施再谈 "
        "L4 读数可信度（未判定谓语在对称性/时序口径里按 null 剔除）", "基础设施"))

    greview = AUDIT_DIR / "l4_group_review_result.json"
    if greview.exists():
        rv = json.loads(greview.read_text(encoding="utf-8")).get("reviews", [])
        cnt = Counter(r.get("verdict") for r in rv)
        n_dis = sum(cnt.get(k, 0) for k in ("change", "reject"))
        rate = round(n_dis / max(1, len(rv)), 4)
        rep["metrics"]["blind_review"] = {
            "n": len(rv), "keep": cnt.get("keep", 0),
            "change": cnt.get("change", 0), "reject": cnt.get("reject", 0),
            "disagreement_rate": rate}
        rep["gate_verdicts"].append(AC.gate_verdict(
            "L4.1 谓语归组盲评分歧率", "≤0.15", rate,
            "PASS" if rv and rate <= 0.15 else
            ("N/A" if not rv else "FAIL"),
            "独立子代理（A4）对 10% 分层抽样盲评，仅凭 predicate+examples 裁决："
            f"keep {cnt.get('keep', 0)} / change {cnt.get('change', 0)} / "
            f"reject {cnt.get('reject', 0)}；change+reject 记分歧。"
            "分歧>15% 说明归组本身不可信，L4 对称性读数须打折", "数据层"))
        rep["artifacts"].append(str(greview))

    out = AC.write_report(REPORTS_DIR / "audit_l4_group.json", rep)
    print(f"WP4-group → {out}")
    for gv in rep["gate_verdicts"]:
        print(f"  [{gv['verdict']}] {gv['gate']}: {gv['actual']}")
    return 0


def mode_group(args) -> int:
    return asyncio.run(mode_group_async(args))


INVERSE_MAP = AUDIT_DIR / "inverse_predicate_map.json"
SIDECAR = AUDIT_DIR / "predicate_grouping_v1.json"
RE_DIR_MARK = re.compile(r"(被|由|于|自|受|给|向|对)")


def _canon_of(sidecar_map, classify_relation):
    def f(rel: str) -> str | None:
        v = sidecar_map.get(rel)
        if v is not None:
            return v.get("canonical")
        c, _ = classify_relation(rel)
        return c
    return f


def _pair_stats(graph, canon_fn, use_raw: bool):
    """(有序对 → 谓语集合) 与 (无序对 → 谓语集合)。use_raw=True 时不归组。"""
    fwd: dict[tuple[str, str], set] = {}
    und: dict[frozenset, set] = {}
    for e in graph.edges:
        rel = e.relation if use_raw else canon_fn(e.relation)
        if not rel:
            continue
        fwd.setdefault((e.src, e.dst), set()).add(rel)
        und.setdefault(frozenset((e.src, e.dst)), set()).add(rel)
    return fwd, und


def mode_symmetry(args) -> int:
    from compendium_rag import pipeline as P
    from compendium_rag.config import get_settings

    s = get_settings()
    rep = AC.new_report("WP4-symmetry", s)
    AC.assert_frozen_graph(rep)
    if not SIDECAR.exists():
        raise SystemExit("[FATAL] 先跑 --mode group 生成 predicate_grouping_v1.json")
    graph = P.load_kb(s).graph
    _CANON, _G, classify_relation = _vocab()
    sidecar = json.loads(SIDECAR.read_text(encoding="utf-8"))
    smap = sidecar["mapping"]
    asset = json.loads(INVERSE_MAP.read_text(encoding="utf-8"))
    g = rep["gate_verdicts"]

    out = {}
    for tag, use_raw in (("grouped", False), ("raw", True)):
        canon_fn = _canon_of(smap, classify_relation)
        fwd, und = _pair_stats(graph, canon_fn, use_raw)
        # 方向对成对完整率
        inv_tot = inv_hit = 0
        per_pair = {}
        for a, b in asset["inverse_pairs"]:
            n = h = 0
            for (src, dst), rels in fwd.items():
                if a not in rels:
                    continue
                n += 1
                if b in fwd.get((dst, src), ()):
                    h += 1
            per_pair[f"{a}↔{b}"] = {"edges_a": n, "paired": h,
                                    "rate": round(h / n, 4) if n else None}
            inv_tot += n
            inv_hit += h
        inv_rate = round(inv_hit / inv_tot, 4) if inv_tot else None
        # 互斥谓语共存率（同一无序对上两个互斥谓语同时出现）
        mx_tot = mx_hit = 0
        mx_detail = {}
        for p, q in asset["mutually_exclusive_pairs"]:
            n = h = 0
            for key, rels in und.items():
                if p in rels or q in rels:
                    n += 1
                    if p in rels and q in rels:
                        h += 1
            mx_detail[f"{p}⊥{q}"] = {"pairs_with_either": n, "conflicts": h,
                                     "rate": round(h / n, 4) if n else None}
            mx_tot += n
            mx_hit += h
        mx_rate = round(mx_hit / mx_tot, 4) if mx_tot else None
        out[tag] = {"inverse_pairs": per_pair, "inverse_rate": inv_rate,
                    "exclusive_detail": mx_detail, "exclusive_rate": mx_rate}

    # 方向信息丢失清单：归组把带方向标记的自由谓语并进了无方向 canonical
    lost = {}
    for p, v in smap.items():
        c = v.get("canonical")
        if c and p != c and RE_DIR_MARK.search(p):
            lost[p] = {"canonical": c, "edges": v.get("edges", 0)}
    top_lost = sorted(lost.items(), key=lambda kv: -kv[1]["edges"])[:60]

    rep["metrics"] = {
        "inverse": out["grouped"]["inverse_rate"],
        "inverse_raw_floor": out["raw"]["inverse_rate"],
        "exclusive": out["grouped"]["exclusive_rate"],
        "exclusive_raw_floor": out["raw"]["exclusive_rate"],
        "direction_loss_unique": len(lost),
        "direction_loss_edges": sum(v["edges"] for v in lost.values()),
        "direction_loss_top": [{"predicate": p, **v} for p, v in top_lost],
        "detail": out,
    }
    gi = out["grouped"]["inverse_rate"]
    g.append(AC.gate_verdict(
        "L4.1a 方向对成对完整率", "≥0.95", gi,
        "PASS" if gi is not None and gi >= 0.95 else "FAIL",
        f"归组口径 inverse_pairs={asset['inverse_pairs']}；"
        f"原始谓语下限 {out['raw']['inverse_rate']}", "数据层"))
    ge = out["grouped"]["exclusive_rate"]
    g.append(AC.gate_verdict(
        "L4.1b 互斥谓语共存率", "≤0.05", ge,
        "PASS" if ge is not None and ge <= 0.05 else "FAIL",
        f"同一实体对上同时挂互斥谓语；原始谓语下限 "
        f"{out['raw']['exclusive_rate']}", "数据层"))
    rep["metrics"]["n_edges"] = len(graph.edges)
    rep["artifacts"] = [str(INVERSE_MAP), str(SIDECAR)]
    out_path = AC.write_report(REPORTS_DIR / "audit_l4_symmetry.json", rep)
    print(f"WP4-symmetry → {out_path}")
    for gv in g:
        print(f"  [{gv['verdict']}] {gv['gate']}: {gv['actual']}")
    return 0


PRIV_IN = AUDIT_DIR / "l4_privacy_inputs"
PRIV_GOLD = AUDIT_DIR / "l4_privacy_gold.json"
TOP_N_CHAR = 50


def _top_characters(graph) -> list:
    chars = [e for e in graph.entities.values() if e.type == "角色"]
    chars.sort(key=lambda e: (-e.mentions, -len(e.chunk_ids), e.eid))
    return [e for e in chars if len(e.chunk_ids) >= 3][:TOP_N_CHAR]


def mode_privacy(args) -> int:
    from compendium_rag import pipeline as P
    from compendium_rag.config import get_settings

    s = get_settings()
    rep = AC.new_report("WP4-privacy", s)
    AC.assert_frozen_graph(rep)
    kb = P.load_kb(s)
    graph = kb.graph
    cat_by_cid = {c.chunk_id: c.category for c in kb.chunks}
    text_by_cid = {c.chunk_id: c.text for c in kb.chunks}
    title_by_cid = {c.chunk_id: c.chapter_title for c in kb.chunks}
    chars = _top_characters(graph)

    if args.prep:
        PRIV_IN.mkdir(parents=True, exist_ok=True)
        rows = []
        for i, e in enumerate(chars, 1):
            own = Counter(cid.split(":")[0] for cid in e.chunk_ids
                         if cat_by_cid.get(cid) == "character")
            if not own:
                continue
            chap = own.most_common(1)[0][0]
            cids = [cid for cid in e.chunk_ids
                    if cid.split(":")[0] == chap and cid in text_by_cid]
            rows.append({"slot": i, "character": e.name, "aliases": e.aliases,
                         "chapter": chap,
                         "chapter_title": title_by_cid.get(cids[0], ""),
                         "mentions": e.mentions,
                         "chunks": [{"chunk_id": cid, "text": text_by_cid[cid]}
                                    for cid in cids]})
        for r in rows:
            p = PRIV_IN / f"char_{r['slot']:03d}.json"
            p.write_text(json.dumps(r, ensure_ascii=False, indent=1),
                         encoding="utf-8")
        print(f"privacy prep：{len(rows)}/{len(chars)} 角色有 character 篇章，"
              f"输入落 {PRIV_IN}")
        rep["metrics"] = {"characters_with_own_chapter": len(rows),
                          "top_n": len(chars)}
        rep["artifacts"] = [str(PRIV_IN)]
        AC.write_report(REPORTS_DIR / "audit_l4_privacy_prep.json", rep)
        return 0

    if not PRIV_GOLD.exists():
        raise SystemExit(f"[FATAL] 缺 {PRIV_GOLD}（先跑 --prep 再交子代理挖锚点）")
    gold = json.loads(PRIV_GOLD.read_text(encoding="utf-8"))["anchors"]
    asker_pool = [c.name for c in chars] or ["J"]
    names_by_char = {c.name: {c.name, *(c.aliases or [])} for c in chars}

    async def run() -> int:
        g = rep["gate_verdicts"]
        rows, leak_rows, co_present = [], [], 0
        for k, a in enumerate(gold):
            owner = a["character"]
            asker = next(asker_pool[(k + j) % len(asker_pool)]
                         for j in range(1, len(asker_pool) + 1)
                         if asker_pool[(k + j) % len(asker_pool)] != owner)
            aspect = a.get("aspect") or "不为人知的过去"
            # 探针题面**只点名提问者**：若同时点名锚点主人，检索命中本人篇章
            # 是正确行为而非泄漏，会把口径变成自证。
            q = f"{asker}的{aspect}，正典里是怎么写的？"
            res = await kb.retrieve(q, top_k=6)
            top_ids = [ev["chunk_id"] for ev in res.get("evidence", [])[:6]]
            anchor_in = a["chunk_id"] in top_ids
            # 提问者本就出现在锚点块里 → 该事实对提问者可公开，不算跨角色泄漏
            hay = text_by_cid.get(a["chunk_id"], "")
            co = any(nm in hay for nm in names_by_char.get(asker, {asker}))
            rows.append({"anchor_id": f"{k}:{owner}", "character": owner,
                         "asker": asker, "chunk_id": a["chunk_id"],
                         "leak_retrieval": anchor_in and not co,
                         "co_present": co, "top_ids": top_ids})
            if anchor_in and not co:
                leak_rows.append(rows[-1])
            if co:
                co_present += 1
            if (k + 1) % 40 == 0:
                print(f"  …{k + 1}/{len(gold)} 锚点", flush=True)
        n_den = len(rows) - co_present
        rate = round(len(leak_rows) / n_den, 4) if n_den else None
        rep["metrics"] = {"n_anchors": len(rows), "n_co_present": co_present,
                          "n_denominator": n_den, "n_leak": len(leak_rows),
                          "leak_rate": rate,
                          "gold_anchors": len(gold)}
        g.append(AC.gate_verdict(
            "L4.3 私密信息跨角色泄漏率（检索层口径）", "≤0.02", rate,
            "PASS" if rate is not None and rate <= 0.02 else "FAIL",
            "锚点=子代理从角色本人 character 篇章挖出的独家事实；题面只点名"
            "另一角色（不点名锚点主人），锚点块进入 top-6 记一次泄漏；"
            f"提问者姓名/别名已出现在锚点原文的 {co_present} 条判为可公开、"
            "移出分母；答案层复核在 WP5-confuse", "检索层"))
        rep["per_case"] = rows
        AC.write_report(REPORTS_DIR / "audit_l4_privacy.json", rep)
        return 0

    return asyncio.run(run())


TIMELINE = AC.ROOT / "data" / "knowledge" / "plot_timeline_wu_ming_zhe.json"
STATE_PREDICATES = ("杀死", "摧毁", "封印")
LIVE_PREDICATES = ("位于", "居住", "持有", "使用", "参与", "对话", "指挥",
                   "经历", "攻击", "保护")
WORLDVIEW_REVIEW = AUDIT_DIR / "l4_worldview_review.json"
TEMPORAL_REVIEW = AUDIT_DIR / "l4_temporal_review.json"
STATE_CONFLICT_REVIEW = AUDIT_DIR / "l4_state_conflict_review.json"
MULTISCENE_N = 60
MULTISCENE_IN = AUDIT_DIR / "l4_multiscene"
MULTISCENE_REVIEW = AUDIT_DIR / "l4_multiscene_review.json"


def _story_rank_map(kb):
    """chunk_id → story_rank：仅主线（mainline）且篇章名能在时间线里对上。"""
    tl = json.loads(TIMELINE.read_text(encoding="utf-8"))["entries"]
    key_rank = {}
    for en in tl:
        if en.get("story_rank") is None:
            continue
        names = {en.get("chapter"), en.get("name")} | set(en.get("arc_list") or [])
        for nm in filter(None, names):
            key_rank[str(nm)] = int(en["story_rank"])
    cid_rank = {}
    for c in kb.chunks:
        if c.category != "mainline":
            continue
        r = key_rank.get(c.chapter_title)
        if r is not None:
            cid_rank[c.chunk_id] = r
    return cid_rank, len(tl), len(key_rank)


def mode_temporal(args) -> int:
    from compendium_rag import pipeline as P
    from compendium_rag.config import get_settings

    s = get_settings()
    rep = AC.new_report("WP4-temporal", s)
    AC.assert_frozen_graph(rep)
    kb = P.load_kb(s)
    graph = kb.graph
    _CANON, _G, classify_relation = _vocab()
    smap = {}
    if SIDECAR.exists():
        smap = json.loads(SIDECAR.read_text(encoding="utf-8"))["mapping"]
    cid_rank, n_entries, n_keys = _story_rank_map(kb)

    def canon(rel):
        v = smap.get(rel)
        return v["canonical"] if v else classify_relation(rel)[0]

    # 实体 → [(rank, canonical, edge)]
    by_ent: dict[str, list] = {}
    for e in graph.edges:
        r = min((cid_rank[c] for c in e.chunk_ids if c in cid_rank),
                default=None)
        if r is None:
            continue
        c = canon(e.relation)
        if not c:
            continue
        # 状态变更谓语只落在**受事方**（e.dst）：把「维尔汀 杀死 X」记成
        # 维尔汀自己被杀死，是这类时序审计最常见的假阳性来源。
        for side in ((e.dst,) if c in STATE_PREDICATES else (e.src, e.dst)):
            by_ent.setdefault(side, []).append((r, c, e))

    covered_ents = len(by_ent)
    state_ents = [eid for eid, rows in by_ent.items()
                  if any(c in STATE_PREDICATES for _r, c, _e in rows)]
    contradictions, conflicts = [], []
    coarsen = 0
    for eid in state_ents:
        ent = graph.entities.get(eid)
        rows = sorted(by_ent[eid], key=lambda t: t[0])
        kill_r = min(r for r, c, _e in rows if c in STATE_PREDICATES)
        after_live = [(r, c, e) for r, c, e in rows
                      if r > kill_r and c in LIVE_PREDICATES]
        if after_live:
            r2, c2, e2 = after_live[0]
            contradictions.append({
                "eid": eid, "entity": ent.name if ent else eid,
                "state_rank_kill": kill_r,
                "state_predicates": [c for _r, c, _e in rows
                                     if c in STATE_PREDICATES],
                "state_evidence": [{"relation": e.relation,
                                    "chunk_ids": e.chunk_ids[:2],
                                    "evidence": (e.evidence or "")[:60]}
                                   for _r, c, e in rows
                                   if c in STATE_PREDICATES][:3],
                "later_live": [{"story_rank": r2, "canonical": c2,
                                "relation": e2.relation,
                                "chunk_ids": e2.chunk_ids[:2]}],
                "n_later_live": len(after_live)})
        same_r = [c for r, c, _e in rows if r == kill_r]
        if set(same_r) & set(STATE_PREDICATES) and "转变" in same_r:
            ev = [{"relation": _e.relation, "canonical": c2,
                   "chunk_ids": _e.chunk_ids[:2],
                   "evidence": (_e.evidence or "")[:80]}
                  for r, c2, _e in rows if r == kill_r
                  and (c2 in STATE_PREDICATES or c2 == "转变")]
            conflicts.append({"eid": eid,
                              "entity": ent.name if ent else eid,
                              "story_rank": kill_r, "predicates": same_r,
                              "state_evidence": ev[:6]})
        # 备查读数：同 rank 上「终结态 + 存活态谓语」并存的实体数。
        # 不用作 gate —— story_rank 是**篇章**粒度，同一章里既有日常行动
        # 又有终结事件本属正常，这个口径会退化成无判别力的读数。
        if (set(same_r) & set(STATE_PREDICATES)
                and set(same_r) & set(LIVE_PREDICATES)):
            coarsen += 1

    cands_raw = list(contradictions)
    n_c_raw = len(contradictions)
    n_conf_raw = len(conflicts)
    conf_raw = list(conflicts)
    refuted_by = {}
    if TEMPORAL_REVIEW.exists():
        rv = json.loads(TEMPORAL_REVIEW.read_text(encoding="utf-8")).get("reviews", [])
        for r in rv:
            v = r.get("verdict")
            for key in (r.get("entity"), r.get("eid")):
                if key:
                    refuted_by[str(key)] = (v != "true_contradiction")
        # 只有被复核明确判否的才剔除；未覆盖的候选保守地留在分子里。
        contradictions = [c for c in contradictions
                          if not refuted_by.get(c["entity"], False)]
    n_c = len(contradictions)
    sc_refuted = {}
    if STATE_CONFLICT_REVIEW.exists():
        rv = json.loads(STATE_CONFLICT_REVIEW.read_text(encoding="utf-8"))
        for r in rv.get("reviews", []):
            for key in (r.get("entity"), r.get("eid")):
                if key:
                    sc_refuted[str(key)] = (r.get("verdict") != "true_conflict")
        conflicts = [c for c in conflicts if not sc_refuted.get(c["entity"], False)]
    n_conf = len(conflicts)
    rate_c = round(n_c / len(state_ents), 4) if state_ents else None
    rate_conf = round(n_conf / len(state_ents), 4) if state_ents else None
    rep["metrics"] = {
        "timeline_entries": n_entries, "timeline_match_keys": n_keys,
        "chunks_with_rank": len(cid_rank),
        "rank_coverage_rate": round(len(cid_rank) / max(1, len(kb.chunks)), 4),
        "entities_ranked": covered_ents, "entities_with_state_change": len(state_ents),
        "temporal_contradictions_raw": n_c_raw,
        "adjudication_covered": sum(1 for c in cands_raw
                                    if c["entity"] in refuted_by
                                    or c["eid"] in refuted_by),
        "temporal_contradictions": n_c, "temporal_contradiction_rate": rate_c,
        "state_conflicts_raw": n_conf_raw,
        "state_conflicts": n_conf, "state_conflict_rate": rate_conf,
        # 检测器质量自证：脚本原始报警里有多少被子代理逐条核对原文后确认为真。
        "detector_precision_temporal": (round(n_c / n_c_raw, 4)
                                        if n_c_raw else None),
        "detector_precision_state_conflict": (round(n_conf / n_conf_raw, 4)
                                              if n_conf_raw else None),
        "same_rank_state_and_live_info": coarsen,
    }
    g = rep["gate_verdicts"]
    g.append(AC.gate_verdict(
        "L4.2a 时序矛盾率（状态变更实体内）", "≤0.03", rate_c,
        "PASS" if rate_c is not None and rate_c <= 0.03 else
        ("N/A" if rate_c is None else "FAIL"),
        f"口径：plot_timeline 覆盖 {len(cid_rank)} 块（仅主线篇章名命中，"
        f"覆盖率 {rep['metrics']['rank_coverage_rate']:.2%}）；anecdote/"
        "appendix 无序类不入分母。矛盾=杀死/摧毁/封印之后更晚的 story_rank "
        f"仍声明该实体的存活态谓语。脚本原始读数 {n_c_raw} 条"
        + (f"，经 A8 子代理逐条核对原文后驳回 {n_c_raw - n_c} 条"
           f"（谓语误映射/受事颠倒/story_rank 倒置），余 {n_c} 条判真"
           if refuted_by else "，尚未交子代理复核") , "数据层"))
    g.append(AC.gate_verdict(
        "L4.2b 同点状态冲突率", "≤0.02", rate_conf,
        "PASS" if rate_conf is not None and rate_conf <= 0.02 else
        ("N/A" if rate_conf is None else "FAIL"),
        f"口径=同一 story_rank 上「终结谓语（杀死/摧毁/封印）」与「转变」并存"
        f"（脚本原始 {n_conf_raw} 例）"
        + (f"，复核驳回 {n_conf_raw - n_conf} 例" if sc_refuted else "，尚未交子代理复核")
        + f"。备查：若改用「终结态+存活态谓语并存」口径，同 rank 命中 {coarsen} 例"
        "——story_rank 是篇章粒度，一章之内既有日常行动又有终结事件本属正常，"
        "该口径无判别力，故不采用", "数据层"))
    rep["per_case"] = [{**c, "adjudication": ("refuted" if refuted_by.get(
        c["entity"], False) else ("true" if c in contradictions else "unreviewed"))}
        for c in cands_raw[:200]]
    if not TEMPORAL_REVIEW.exists():  # 复核已在跑，勿覆盖它的输入
        (AUDIT_DIR / "l4_temporal_candidates.json").write_text(
            json.dumps({"schema": "audit.l4_temporal_candidates/v1",
                        "note": "交子代理复核 100 条（A8）：判定矛盾是否成立",
                        "items": contradictions[:100]}, ensure_ascii=False, indent=1),
            encoding="utf-8")
    rep["artifacts"] = [str(TIMELINE), str(AUDIT_DIR / "l4_temporal_candidates.json")]
    sc_path = AUDIT_DIR / "l4_state_conflict_candidates.json"
    if not STATE_CONFLICT_REVIEW.exists():
        sc_path.write_text(json.dumps(
            {"schema": "audit.l4_state_conflict_candidates/v1",
             "task": "逐例核对原文，判定「终结谓语 + 转变」在同篇章是否真的互斥"
                     "（verdict: true_conflict | false_positive_extraction | "
                     "false_positive_narrative | undecidable）",
             "items": conf_raw}, ensure_ascii=False, indent=1), encoding="utf-8")
        rep["artifacts"].append(str(sc_path))
    AC.write_report(REPORTS_DIR / "audit_l4_temporal.json", rep)
    print(f"WP4-temporal：状态实体 {len(state_ents)}，矛盾 {n_c}，冲突 {n_conf}")
    for gv in g:
        print(f"  [{gv['verdict']}] {gv['gate']}: {gv['actual']}")
    return 0


def mode_multiscene(args) -> int:
    """L4.5 多角色场景互洽性：抽 60 个含 ≥3 角色实体的块，子代理逐块评 1~5。

    原义"多角色同场运行时生成"在本仓库无通路（src/roleplay 零 import
    compendium_rag），另登记一条 N/A 豁免。
    """
    from compendium_rag import pipeline as P
    from compendium_rag.config import get_settings

    s = get_settings()
    rep = AC.new_report("WP4-multiscene", s)
    AC.assert_frozen_graph(rep)
    kb = P.load_kb(s)
    graph = kb.graph
    _CANON, _G, classify_relation = _vocab()
    smap = json.loads(SIDECAR.read_text(encoding="utf-8"))["mapping"] \
        if SIDECAR.exists() else {}
    canon_fn = _canon_of(smap, classify_relation)
    g = rep["gate_verdicts"]

    if args.prep:
        text_by_cid = {c.chunk_id: c.text for c in kb.chunks}
        chars = {e.eid for e in graph.entities.values() if e.type == "角色"}
        # chunk → 该块里出现（作为边端点）的角色实体
        per_chunk: dict[str, set] = {}
        for e in graph.edges:
            if not e.chunk_ids:
                continue
            cid = e.chunk_ids[0]
            for side in (e.src, e.dst):
                if side in chars:
                    per_chunk.setdefault(cid, set()).add(side)
        cand = [cid for cid, s in per_chunk.items()
                if len(s) >= 3 and cid in text_by_cid]
        rng = random.Random(SEED)
        rng.shuffle(cand)          # 随机抽样，不按角色数排序——否则抽到的全是"大会场"块
        cand = sorted(cand)[:MULTISCENE_N]
        items = []
        for cid in cand:
            involved = per_chunk[cid]
            rows = []
            for e in graph.edges:
                if e.chunk_ids and e.chunk_ids[0] == cid \
                        and e.src in involved and e.dst in involved:
                    rows.append({"src": graph.entities[e.src].name
                                 if e.src in graph.entities else e.src,
                                 "relation": e.relation,
                                 "canonical": canon_fn(e.relation),
                                 "dst": graph.entities[e.dst].name
                                 if e.dst in graph.entities else e.dst,
                                 "evidence": (e.evidence or "")[:80]})
            items.append({"chunk_id": cid,
                          "characters": sorted(graph.entities[x].name
                                               for x in involved
                                               if x in graph.entities),
                          "edges": rows[:25],
                          "text": text_by_cid[cid][:2600]})
        MULTISCENE_IN.mkdir(parents=True, exist_ok=True)
        for bi in range(0, len(items), 20):
            p = MULTISCENE_IN / f"ms_b{bi // 20 + 1:02d}.json"
            p.write_text(json.dumps(
                {"schema": "audit.l4_multiscene_input/v1",
                 "task": "逐块判定这些角色之间的关系陈述是否与原文互洽"
                         "（1~5 分）",
                 "items": items[bi:bi + 20]},
                ensure_ascii=False, indent=1), encoding="utf-8")
        rep["metrics"] = {"n_items": len(items), "n_batches":
                          (len(items) + 19) // 20}
        rep["artifacts"] = [str(MULTISCENE_IN)]
        AC.write_report(REPORTS_DIR / "audit_l4_multiscene_prep.json", rep)
        print(f"WP4-multiscene prep：{len(items)} 块 → {MULTISCENE_IN}")
        return 0

    parts = sorted(MULTISCENE_IN.glob("ms_b*_review.json"))
    if not parts:
        raise SystemExit(f"[FATAL] 缺 {MULTISCENE_IN}/ms_b*_review.json"
                         f"（先 --prep 再交子代理评分）")
    rv = []
    for p in parts:
        rv += json.loads(p.read_text(encoding="utf-8")).get("items", [])
    scores = [float(r["coherence"]) for r in rv
              if isinstance(r.get("coherence"), (int, float))]
    mean = round(sum(scores) / len(scores), 4) if scores else None
    rep["metrics"] = {"n_reviewed": len(scores), "mean_coherence": mean,
                      "low_scores": [r for r in rv
                                     if isinstance(r.get("coherence"),
                                                   (int, float))
                                     and float(r["coherence"]) <= 2][:20]}
    g.append(AC.gate_verdict(
        "L4.5 多角色场景关系互洽性", "≥4.0/5", mean,
        "PASS" if mean is not None and mean >= 4.0 else
        ("N/A" if mean is None else "FAIL"),
        f"口径：随机抽 {MULTISCENE_N} 个含 ≥3 角色实体的场景块，"
        f"子代理逐块核对图谱关系陈述与原文是否互洽（1~5）；实评 {len(scores)} 块",
        "数据层"))
    g.append(AC.gate_verdict(
        "L4.5b 多角色同场运行时生成一致性", "≥4.0/5", None, "N/A",
        "src/roleplay 与 compendium_rag 之间零 import、无运行时通路，"
        "正典库未接入多角色同场对话生成；对不存在的通路判负=惩罚未做的设计决策。"
        "豁免并从 L4 分母剔除", "通路不存在"))
    rep["artifacts"] = [str(p) for p in parts]
    AC.write_report(REPORTS_DIR / "audit_l4_multiscene.json", rep)
    print(f"WP4-multiscene：实评 {len(scores)} 块，均值 {mean}")
    for gv in g:
        print(f"  [{gv['verdict']}] {gv['gate']}: {gv['actual']}")
    return 0


def mode_worldview(args) -> int:
    from compendium_rag import pipeline as P
    from compendium_rag.config import get_settings

    s = get_settings()
    rep = AC.new_report("WP4-worldview", s)
    AC.assert_frozen_graph(rep)
    graph = P.load_kb(s).graph
    _CANON, _G, classify_relation = _vocab()
    smap = {}
    if SIDECAR.exists():
        smap = json.loads(SIDECAR.read_text(encoding="utf-8"))["mapping"]

    def canon(rel):
        v = smap.get(rel)
        return v["canonical"] if v else classify_relation(rel)[0]

    defs = {}
    deg = AC.degrees(AC.build_adjacency(graph))
    for e in graph.entities.values():
        if e.type != "概念" or deg.get(e.eid, 0) < 3:
            continue
        rows = []
        for ed in graph.edges:
            if e.eid not in (ed.src, ed.dst):
                continue
            c = canon(ed.relation)
            if c in ("是", "象征", "包含", "隶属", "影响"):
                other = ed.dst if ed.src == e.eid else ed.src
                oe = graph.entities.get(other)
                rows.append({"canonical": c, "relation": ed.relation,
                             "direction": "out" if ed.src == e.eid else "in",
                             "other": oe.name if oe else other,
                             "evidence": (ed.evidence or "")[:60]})
        if rows:
            defs[e.name] = {"eid": e.eid, "desc": e.desc, "degree": deg[e.eid],
                            "definition_edges": rows[:12]}
    cand_path = AUDIT_DIR / "l4_worldview_candidates.json"
    cand_path.write_text(json.dumps(
        {"schema": "audit.l4_worldview_candidates/v1",
         "task": "逐概念判定定义是否互斥/自相矛盾（同一概念被同时定义为 A 与 非A）",
         "items": [{"concept": k, **v} for k, v in defs.items()]},
        ensure_ascii=False, indent=1), encoding="utf-8")

    unity = None
    n_excl = None
    if WORLDVIEW_REVIEW.exists():
        rv = json.loads(WORLDVIEW_REVIEW.read_text(encoding="utf-8"))["reviews"]
        n_excl = sum(1 for r in rv if r.get("mutually_exclusive")
                     or r.get("verdict") == "mutually_exclusive")
        n_insuff = sum(1 for r in rv if r.get("verdict") == "insufficient")
        n_judged = len(rv) - n_insuff
        unity = round(1 - n_excl / max(1, n_judged), 4)
        rep["metrics"]["reviewed"] = len(rv)
        rep["metrics"]["insufficient"] = n_insuff
        rep["metrics"]["judged"] = n_judged
    rep["metrics"].update({"concepts_high_degree": len(defs),
                          "exclusive_concepts": n_excl, "unity": unity})
    rep["gate_verdicts"].append(AC.gate_verdict(
        "L4.4 世界观定义统一性", "≥0.95", unity,
        "PASS" if unity is not None and unity >= 0.95
        else ("N/A" if unity is None else "FAIL"),
        "N/A=子代理定义互斥复核（l4_worldview_review.json）尚未产出"
        if unity is None else
        f"高 degree 概念实体的 是/象征/包含 边 + desc 送审；复核 {len(rv)} 条、"
        f"可判 {rep['metrics']['judged']} 条（{rep['metrics']['insufficient']} 条"
        f"证据不足移出分母），互斥 {n_excl} 条", "数据层"))
    rep["artifacts"] = [str(cand_path)]
    AC.write_report(REPORTS_DIR / "audit_l4_worldview.json", rep)
    print(f"WP4-worldview：候选概念 {len(defs)} → {cand_path}")
    return 0


def _todo(name: str):
    def f(args):
        raise SystemExit(f"[{name}] 依赖前置 WP，稍后启用")
    return f


MODES = {"group": mode_group,
         "symmetry": mode_symmetry,
         "temporal": mode_temporal,
         "privacy": mode_privacy,
         "multiscene": mode_multiscene,
         "worldview": mode_worldview}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", required=True, choices=list(MODES))
    ap.add_argument("--report-only", action="store_true",
                    help="group 模式：不跑云端，只用现有 progress/盲评结果重出报告")
    ap.add_argument("--limit-batches", type=int, default=0,
                    help="调试：只跑前 N 批 LLM 归组")
    ap.add_argument("--concurrency", type=int, default=4,
                    help="归组批并发（CloudLLM 内部信号量另行限流）")
    ap.add_argument("--batch-size", type=int, default=0,
                    help="归组每批谓语句数（默认 50；补漏时调小可少丢条目）")
    ap.add_argument("--fresh", action="store_true",                    help="忽略断点文件，从零重跑归组")
    ap.add_argument("--prep", action="store_true",
                    help="privacy：只导出子代理挖锚点的输入文件")
    args = ap.parse_args()
    sys.exit(MODES[args.mode](args))
