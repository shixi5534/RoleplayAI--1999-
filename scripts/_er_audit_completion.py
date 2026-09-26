# -*- coding: utf-8 -*-
"""完成度审计（离线、只读、全量范围）：把计划书闸门逐条映射到落盘产物并现场复算。

不接受代理信号：每条判据都从磁盘文件重算，产物缺失/口径不符 ⇒ 该条 FAIL 而非跳过。
退出码：0=全部 PASS；1=有 FAIL；2=有 PENDING（尚未跑完的档位）。
"""
from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DR = ROOT / "data" / "compendium_rag"
REP = DR / "reports"
SETS = ("native", "300_cn", "i")
GRAPH = DR / "graph.json"
SPLIT = re.compile(r"[、,，]")

ROUTE_SCRIPTS = ("_gen_entity_candidates.py", "_er_merge_map.py", "_er_report_gates.py",
                 "_replay_entity_map.py", "_iset_merge_map.py", "_iset_eval5.py")
NET_PAT = re.compile(r"\b(requests|httpx|urllib|openai|anthropic|aiohttp|socket)\b|api[_-]?key",
                     re.I)

C: list[str] = []      # 结论行
BLIND: dict[str, list[str]] = {}   # 原始识别记录里自述「见过 gold」的行


def check(name: str, ok: str, detail: str) -> None:
    C.append((name, ok, detail))


def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def mcnemar_exact(b: int, c: int) -> float:
    n = b + c
    if n == 0:
        return 1.0
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(min(b, c) + 1)) / (2 ** n))


def raw_picks(st: str) -> dict[str, list[str]] | None:
    """脱离合并脚本重读识别原始产物；找不到返回 None。

    TSV 契约（与 `_er_merge_map.py` 一致）：col0=qid、col1=名字（「、，」分隔）、col2 起为批注；
    批注含 seen_gold 等 ⇒ 记为非盲行（BLIND 表里报告），但**不参与**名字解析。
    """
    if st == "i":
        d = ROOT / "data" / "eval_set_i" / "id_out"
        files = sorted(d.glob("batch_*.out.jsonl"))
        if not files:
            return None
        out: dict[str, list[str]] = {}
        for f in files:
            for ln in f.read_text(encoding="utf-8").splitlines():
                ln = ln.strip()
                if not ln:
                    continue
                try:
                    o = json.loads(ln)
                except json.JSONDecodeError:
                    continue
                qid = str(o.get("qid", ""))
                extra = [k for k in o if k not in ("qid", "picks")]
                if extra:
                    BLIND.setdefault(st, []).append(f"{qid}:字段{extra}")
                if qid and qid not in out:
                    out[qid] = [str(x).strip() for x in (o.get("picks") or []) if str(x).strip()]
        return out
    path = (DR / "er2" / "picks_raw.tsv") if st == "native" else (DR / "er2" / st / "picks_raw.tsv")
    if not path.exists():
        return None
    rows: dict[str, list[str]] = {}
    for ln in path.read_text(encoding="utf-8").splitlines():
        if not ln.strip():
            continue
        parts = ln.split("\t")
        qid = parts[0].strip()
        names = [t.strip() for t in SPLIT.split(parts[1]) if t.strip()] if len(parts) > 1 else []
        for note in parts[2:]:
            if note.strip():
                BLIND.setdefault(st, []).append(f"{qid}:{note.strip()[:40]}")
        if names and any("#" in n for n in names):
            BLIND.setdefault(st, []).append(f"{qid}:名字列含批注")
        rows[qid] = [n.split("#")[0].strip() for n in names if n.split("#")[0].strip()]
    return rows


def main() -> int:
    # ---- A. 铁律 #1 零网关 ----
    hits = {}
    for s in ROUTE_SCRIPTS:
        p = ROOT / "scripts" / s
        if not p.exists():
            hits[s] = ["<脚本缺失>"]
            continue
        hits[s] = [f"L{i}: {ln.strip()[:70]}" for i, ln in
                   enumerate(p.read_text(encoding="utf-8").splitlines(), 1) if NET_PAT.search(ln)]
    bad = {k: v for k, v in hits.items() if v}
    check("A 铁律#1 零网关（6 个路线脚本无网络端点）", "PASS" if not bad else "FAIL",
          "全部无命中" if not bad else json.dumps(bad, ensure_ascii=False))

    ent = load(GRAPH)["entities"]
    names_all = {e["name"] for e in ent} | {e["eid"] for e in ent}
    check("A2 graph.json 可加载", "PASS", f"实体 {len(ent)} / 名字键 {len(names_all)}")

    for st in SETS:
        cand_p, map_p = DR / f"entity_candidates_{st}.json", DR / f"entity_map_{st}.json"
        stats_p = DR / f"entity_candidates_stats_{st}.json"
        if not (cand_p.exists() and map_p.exists() and stats_p.exists()):
            check(f"[{st}] 阶段1/2 产物存在", "FAIL",
                  f"cands={cand_p.exists()} map={map_p.exists()} stats={stats_p.exists()}")
            continue
        cands, mp, stats = load(cand_p), load(map_p), load(stats_p)
        wl = {q: set(v["candidates"]) for q, v in cands.items()}

        # 阶段1 闸门
        if st == "native":
            pools = stats["by_pool"]
            t1, t1r = pools.get("T1"), pools.get("T1r")
            ok = (t1 and t1["cov_seeded"] == 1.0 and t1r and t1r["cov_seeded"] == 1.0
                  and stats["overall"]["truncated"] == 0)
            check("B native 阶段1：T1/T1r 覆盖=100% 且 truncated=0", "PASS" if ok else "FAIL",
                  f"T1 {t1['seeded']}/{t1['n']} cov={t1['cov_seeded']}；"
                  f"T1r {t1r['seeded']}/{t1r['n']} cov={t1r['cov_seeded']}；"
                  f"truncated={stats['overall']['truncated']} cap={stats['cap']}")
        check(f"B [{st}] 候选名全部 ∈ graph（白名单源头合法）",
              "PASS" if all(n in names_all for v in cands.values() for n in v["candidates"]) else "FAIL",
              f"{sum(len(v['candidates']) for v in cands.values())} 个候选名逐 token 校验")

        # 阶段2 闸门：解析率 = 提议 token 中过白名单+resolve 的比例（计划书 §5 阶段2 原义），
        # 独立从原始识别产物回算；题级全合法率/非空率一并报，供口径核对但不作闸门。
        m = mp["map"]
        viol_wl = [(q, n) for q, v in m.items() for n in v if n not in wl.get(q, set())]
        viol_gr = [(q, n) for q, v in m.items() for n in v if n not in names_all]
        raw = raw_picks(st)
        if raw is None:
            tok_rate, src = None, "原始识别产物缺失"
            ok_rate = False
        else:
            prop = kept = q_ok = 0
            for q, pk in raw.items():
                bad = 0
                for n in pk:
                    prop += 1
                    if n in wl.get(q, set()) and n in names_all:
                        kept += 1
                    else:
                        bad += 1
                q_ok += 1 if bad == 0 else 0
            tok_rate = round(kept / prop, 4) if prop else None
            q_rate = round(q_ok / len(raw), 4) if raw else None
            ok_rate = tok_rate is not None and tok_rate >= 0.90
            src = (f"原始 {len(raw)} 行 → 提议 {prop} token、保留 {kept} ⇒ **token 解析率 {tok_rate}**；"
                   f"题级全合法率 {q_rate}")
        check(f"C [{st}] 阶段2：解析率≥90%（token 口径，独立回算）+ map 全量合法",
              "PASS" if ok_rate and not viol_wl and not viol_gr else "FAIL",
              f"{src}；map 题 {len(m)} / 非空 {sum(1 for v in m.values() if v)} / "
              f"名 {sum(len(v) for v in m.values())}；违例 白名单 {len(viol_wl)} resolve {len(viol_gr)}")
        if viol_wl or viol_gr:
            C.append((f"  └ {st} 违例样例", "FAIL",
                      json.dumps((viol_wl + viol_gr)[:5], ensure_ascii=False)))

        # 阶段3：零档逐位复现 + 映射档（题集 i 走五臂产物，形态不同）
        if st == "i":
            p5 = REP / "eval5_set_i.json"
            if not p5.exists():
                check("D [i] 阶段3 五臂对照产物", "FAIL", "eval5_set_i.json 未落盘")
                continue
            o5 = load(p5)
            need = {"empty", "random", "alias", "vector", "strong"}
            arms = set(o5["arms"]) | set(o5["rows"])
            gd = all(r["grounded"] for a in o5["rows"].values() for m in a.values() for r in m)
            check("D [i] 阶段3 五臂齐全 + grounded=1.000 + 非 partial",
                  "PASS" if need <= arms and gd and not o5.get("partial") else "FAIL",
                  f"臂={sorted(arms)} modes={o5['modes']} n_cases={o5['n_cases']} "
                  f"partial={o5.get('partial')} grounded全1.0={gd}")
            # 独立回算 L1(hit@10) 主闸三判：strong≥0.70、strong−empty、strong−random
            def l1(arm, mode="full"):
                return {r["qid"]: r["hit10"] for r in o5["rows"][arm][mode] if r["pool"] == "T1"}
            se, sr, sm = l1("empty"), l1("random"), l1("strong")
            ge, gs = l1("empty", "graph_only"), l1("strong", "graph_only")
            ge, gs = l1("empty", "graph_only"), l1("strong", "graph_only")
            def flip(a, b):
                ups = sorted(q for q in b if b[q] and not a.get(q))
                dns = sorted(q for q in a if a[q] and not b.get(q))
                return ups, dns
            up_e, dn_e = flip(se, sm)
            up_r, dn_r = flip(sr, sm)
            pt = lambda a, b: round(100 * (sum(b.values()) / len(b) - sum(a.values()) / len(a)), 2)
            check("D [i] L1 主闸独立回算（hit@10, full, n=T1）",
                  "PASS" if abs(pt(se, sm) - o5["gates"]["strong_minus_empty_pt"]) < 0.02
                  and abs(pt(sr, sm) - o5["gates"]["strong_minus_random_pt"]) < 0.02
                  and sorted(up_e) == sorted(o5["gates"]["up_qids"])
                  and sorted(dn_e) == sorted(o5["gates"]["down_qids"]) else "FAIL",
                  f"strong={sum(sm.values())/len(sm):.4f} Δempty={pt(se, sm):+}pt(b={len(up_e)},c={len(dn_e)},"
                  f"p={mcnemar_exact(len(up_e), len(dn_e)):.5f}) Δrandom={pt(sr, sm):+}pt"
                  f"(b={len(up_r)},c={len(dn_r)},p={mcnemar_exact(len(up_r), len(dn_r)):.5f})；"
                  f"打印值 Δempty={o5['gates']['strong_minus_empty_pt']} "
                  f"Δrandom={o5['gates']['strong_minus_random_pt']} "
                  f"up={o5['gates']['up_qids']} down={o5['gates']['down_qids']}")
            check("D [i] graph_only 机理证据独立回算（纯符号通道 strong−empty hit@10）",
                  "PASS" if abs(pt(ge, gs) - 9.73) < 0.05 else "FAIL",
                  f"empty={sum(ge.values())/len(ge):.4f} → strong={sum(gs.values())/len(gs):.4f} "
                  f"= {pt(ge, gs):+.2f}pt（发布值 +9.73pt）")

            # 五臂排序：strong 是否在两模式的 hit@6 / hit@10 / MRR 全部居首（§4 发布结论）
            def l1m(arm, mode, fld):
                return round(sum(r[fld] for r in o5["rows"][arm][mode] if r["pool"] == "T1")
                             / sum(1 for r in o5["rows"][arm][mode] if r["pool"] == "T1"), 4)
            best, tbl = True, []
            for mode in ("full", "graph_only"):
                for fld in ("hit6", "hit10", "rr"):
                    vals = {a: l1m(a, mode, fld) for a in sorted(need)}
                    top = max(vals, key=lambda a: vals[a])
                    best &= top == "strong"
                    tbl.append(f"{mode}/{fld}:{top}")
            check("D [i] §4「strong 两模式全指标居五臂之首」回算",
                  "PASS" if best else "FAIL", " ".join(tbl))
            continue
        for tier, want_map in (("zero", "none"), ("map", f"entity_map_{st}.json")):
            zp = REP / f"replay_{st.replace('_', '')}_{tier}.json"
            if not zp.exists():
                check(f"D [{st}] 阶段3 {tier} 档", "PENDING" if st == "300_cn" else "FAIL",
                      f"{zp.name} 未落盘")
                continue
            o = load(zp)
            used = str(o.get("map", ""))
            same = Path(used).name == want_map
            rows = o["rows"]
            g_all = all(r["grounded"] for r in rows)
            base_p = REP / {"native": "eval_native_after_welds.json",
                            "300_cn": "eval_300_cn_after_welds.json"}[st] if st != "i" else None
            line = f"map字段={Path(used).name} 行数={len(rows)} grounded全1.0={g_all}"
            verdict = "PASS" if same and g_all else "FAIL"
            if tier == "zero" and base_p and base_p.exists():
                bkey = {(r["qid"], r["mode"]): r for r in load(base_p)["rows"]}
                fld = ("hit", "rr", "seed_hit", "grounded", "n_evidence", "n_edges")
                diffs = sum(1 for r in rows if (r["qid"], r["mode"]) not in bkey
                            or any(r[f] != bkey[(r["qid"], r["mode"])][f] for f in fld))
                line += f" / 基线 {len(bkey)} 行，逐位差异={diffs}"
                verdict = "PASS" if same and g_all and diffs == 0 and len(rows) == len(bkey) else "FAIL"
            check(f"D [{st}] 阶段3 {tier} 档（口径身份+grounded+逐位）", verdict, line)

    blind_txt = "; ".join(f"{k}: {v}" for k, v in sorted(BLIND.items())) or "三题集原始识别记录均无 gold 泄漏批注"
    check("E 盲性披露（识别记录中自述见过 gold 的行）",
          "DISCLOSED" if BLIND else "PASS", blind_txt)

    print("| 判据 | 结论 | 复算依据 |")
    print("|---|---|---|")
    for n, ok, d in C:
        print(f"| {n} | {ok} | {d} |")
    codes = {ok for _, ok, _ in C}
    return 2 if "PENDING" in codes else (1 if "FAIL" in codes else 0)


if __name__ == "__main__":
    raise SystemExit(main())
