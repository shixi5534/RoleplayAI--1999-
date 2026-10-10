"""P10·R2 前置影子（**只读**）：角色可见性过滤在三套 MRR 上到底误伤多少。

为什么必须先跑它：唯一能让 `N_retrieval` 有访问控制语义的动作是写图（owner/visibility 边），
而批准写图的依据不该是"分数会降"（那一格在本量具上不可证伪，见 owner_shadow），
只能是**代价**。P3 的角色域过滤器已经判负一次：owners 尺子把 17–30% 的转述 gold 也算成跨域
（project-p3-rolefilter-shadow-verdict）。本脚本把"可见性"这件事在三套主题集上量成
**同一次运行内的 before/after Δ**，Δ 才可比，绝对值不与别轮混表。

两种过滤形态（都只作用在 top-10，主体 = seeds 里第一个 `type=="角色"` 的实体）：
  strict：主体名形式（name + aliases）不在块正文/说话人里 ⇒ 挡。最紧，等价于"只谈自己的块可见"。
  scene ：主体在该章（同 doc_id）里出现过 anywhere ⇒ 放行。松，等价于"场景在场即可见"。

检索调用与 CBI 通道同参数（`kb.retrieve(query, top_k=...)`，默认口径），
并先做 **前缀一致性检查**：top-30 的前 10 必须等于 top-10 的结果，
不等就说明"取深候选再回填"这套读数会污染基线，直接 [FATAL] 退出。

只读图与主题集，只写 `reports/cbi/visibility_shadow_rows.jsonl`（增量、可按 qid 续跑）
与 `visibility_shadow.{json,md}`；不改图、不改缓存、不删任何文件。
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import statistics as st
import sys
import time
from pathlib import Path

import audit_common as AC

AC.apply_v8_env()

ROOT = AC.ROOT
AUDIT_DIR = ROOT / "data" / "knowledge" / "_audit"
CBI = ROOT / "data" / "compendium_rag" / "reports" / "cbi"
ROWS = CBI / "visibility_shadow_rows.jsonl"
HB = CBI / "visibility_shadow.heartbeat.txt"
OUT_JSON = CBI / "visibility_shadow.json"
OUT_MD = CBI / "visibility_shadow.md"

TOP_K = 10
DEEP = 30                      # 过滤后回填用的候选池深度
CHECK_N = 20                   # 前缀一致性抽查题数
EXPECTED_SHA = "911bb538160db80e"
FLOOR_TARGET = 0.39            # 用户给的 MRR 闸门
DELTABUDGET = 0.02             # 预注册的"回退线"：Δ MRR 超过它就判定该形态不落地
SETS_CFG = [
    ("300cn", AUDIT_DIR / "rag_testset_300_cn.json", "300cn_answerable"),
    ("blind", AUDIT_DIR / "blind_v1" / "questions_strict.json", "blind_all"),
    ("gen", AUDIT_DIR / "rag_testset_gen_r1r2.json", "gen_all"),
]


def sha16(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()[:16]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def mrr(rel: list[bool]) -> float:
    return AC.mrr_at_k(rel)


def hit(rel: list[bool]) -> int:
    return int(any(rel))


def keep_flags(cids, rel, visible):
    """过滤 + 回填：按原序保留可见的，最多 TOP_K 个（rel 跟着走）。"""
    out = []
    for cid, r in zip(cids, rel):
        if visible(cid):
            out.append(r)
            if len(out) == TOP_K:
                break
    while len(out) < TOP_K:
        out.append(False)
    return out


def main_loop(limit: int) -> int:
    from compendium_rag import pipeline as P
    from compendium_rag.config import get_settings

    if sha16(ROOT / "data" / "compendium_rag" / "graph.json") != EXPECTED_SHA:
        raise SystemExit(f"[FATAL] 图指纹漂移，不等于冻结 r11 {EXPECTED_SHA}，不写任何文件")

    E300 = AC.eval300_module()
    sets_cfg = SETS_CFG
    wl = load_json(AUDIT_DIR / "audit_qid_whitelist.json")["lists"]
    done = set()
    if ROWS.exists():
        for line in ROWS.read_text(encoding="utf-8").splitlines():
            try:
                done.add(json.loads(line)["qid"])
            except (json.JSONDecodeError, KeyError):
                continue

    async def run() -> int:
        s = get_settings()
        kb = P.load_kb(s)
        graph = kb.graph
        cmeta = {c.chunk_id: c for c in kb.chunks}
        blob = {c.chunk_id: AC.blob_of(c) for c in kb.chunks}
        doc_blob: dict[str, str] = {}
        for c in kb.chunks:
            doc_blob[c.doc_id] = doc_blob.get(c.doc_id, "") + "\n" + (c.text or "")

        CBI.mkdir(parents=True, exist_ok=True)
        HB.write_text(f"start {time.strftime('%H:%M:%S')} done={len(done)}", encoding="utf-8")

        # ── 前缀一致性：top-30 的前 10 必须等于 top-10 ──
        probe = []
        for name, path, key in sets_cfg:
            for c in [x for x in E300.load_cases(path) if x.qid in set(wl[key])][:3]:
                probe.append((name, c))
        for _, c in probe:
            a = [ev["chunk_id"] for ev in
                 (await kb.retrieve(c.query, top_k=TOP_K)).get("evidence", [])[:TOP_K]]
            b = [ev["chunk_id"] for ev in
                 (await kb.retrieve(c.query, top_k=DEEP)).get("evidence", [])[:TOP_K]]
            if a != b:
                raise SystemExit(f"[FATAL] 前缀不一致（{c.qid}）：top_k 改变前 10 ⇒ "
                                 f"回填读数会换口径，本影子不成立")
        print(f"[OK] 前缀一致性通过（{len(probe)} 题抽查）")

        n = 0
        with ROWS.open("a", encoding="utf-8") as fh:
            for name, path, key in sets_cfg:
                cases = [c for c in E300.load_cases(path) if c.qid in set(wl[key])]
                if limit:
                    cases = cases[:limit]
                for c in cases:
                    if c.qid in done:
                        continue
                    keys = [k for k in c.keywords if k]
                    r_q = {cid for cid, b in blob.items() if any(k in b for k in keys)}
                    res = await kb.retrieve(c.query, top_k=DEEP)
                    ev = res.get("evidence", [])
                    deep_ids = [e["chunk_id"] for e in ev[:DEEP]]
                    rel = [cid in r_q for cid in deep_ids]
                    base = rel[:TOP_K]

                    seeds = res.get("seeds", [])
                    subj = None
                    for sd in seeds:
                        ent = graph.entities.get(sd["eid"])
                        if ent and ent.type == "角色":
                            subj = ent
                            break
                    if subj is None:
                        row = {"set": name, "qid": c.qid, "role_domain": False,
                               "n_rel": len(r_q),
                               "base_mrr": mrr(base), "base_hit": hit(base),
                               "base_recall": AC.recall_at_k(base, len(r_q))}
                        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
                        fh.flush()
                        n += 1
                        continue

                    names = {nm for nm in (subj.name, *subj.aliases) if nm}

                    def vis_strict(cid):
                        ch = cmeta.get(cid)
                        if ch is None:
                            return True
                        hay = (ch.text or "") + "\n" + "\n".join(ch.speakers or [])
                        return any(nm in hay for nm in names)

                    def vis_scene(cid, _names=names, _docs=doc_blob):
                        ch = cmeta.get(cid)
                        if ch is None or vis_strict(cid):
                            return True
                        b = _docs.get(ch.doc_id, "")
                        return any(nm in b for nm in _names)

                    s_rel = keep_flags(deep_ids, rel, vis_strict)
                    c_rel = keep_flags(deep_ids, rel, vis_scene)
                    killed = [i for i in range(min(len(base), TOP_K))
                              if base[i] and not vis_strict(deep_ids[i])]
                    row = {
                        "set": name, "qid": c.qid, "role_domain": True,
                        "subject": subj.name, "n_names": len(names), "n_rel": len(r_q),
                        "base_mrr": mrr(base), "base_hit": hit(base),
                        "base_recall": AC.recall_at_k(base, len(r_q)),
                        "strict_mrr": mrr(s_rel), "strict_hit": hit(s_rel),
                        "strict_recall": AC.recall_at_k(s_rel, len(r_q)),
                        "scene_mrr": mrr(c_rel), "scene_hit": hit(c_rel),
                        "scene_recall": AC.recall_at_k(c_rel, len(r_q)),
                        "slots_dropped_strict": sum(1 for cid in deep_ids[:TOP_K]
                                                   if not vis_strict(cid)),
                        "relevant_killed_strict": len(killed),
                        # 转述型：top-10 里有相关块，但主体名字不在该块字面里 ⇒ 名字型闸门挡它
                        "narration_gold": bool(killed),
                    }
                    fh.write(json.dumps(row, ensure_ascii=False) + "\n")
                    fh.flush()
                    n += 1
                    if n % 25 == 0:
                        HB.write_text(f"{time.strftime('%H:%M:%S')} wrote={n} "
                                      f"total={len(done) + n}", encoding="utf-8")
        print(f"[OK] 本轮新增 {n} 行 → {ROWS.name}")
        return 0

    return asyncio.run(run())


def aggregate() -> int:
    rows = [json.loads(l) for l in ROWS.read_text(encoding="utf-8").splitlines()] if ROWS.exists() else []
    if not rows:
        raise SystemExit("[FATAL] 没有行，先跑采集阶段")
    # 覆盖率门：每集的期望题数从主题集与白名单现算，不齐就**不给判**
    # （部分输入上发"可落地"是本项目吃过教训的那类假通过）
    E300 = AC.eval300_module()
    wl = load_json(AUDIT_DIR / "audit_qid_whitelist.json")["lists"]
    want = {}
    for name, path, key in SETS_CFG:
        want[name] = len([c for c in E300.load_cases(path) if c.qid in set(wl[key])])
    got = {r["set"] for r in rows}
    dedup = {r["qid"]: r for r in rows}          # 续跑安全：同 qid 取最后一次
    rows = list(dedup.values())
    cover = {k: (len([r for r in rows if r["set"] == k]), want[k])
             for k in want if k in got}
    complete = bool(cover) and set(cover) == set(want) and \
        all(g == w for g, w in cover.values())
    rd = [r for r in rows if r.get("role_domain")]
    per = {}
    for name in sorted({r["set"] for r in rows}):
        g = [r for r in rows if r["set"] == name]
        d = [r for r in g if r.get("role_domain")]
        nd = [r for r in g if not r.get("role_domain")]
        per[name] = {
            "n": len(g), "n_role_domain": len(d), "n_non_role": len(nd),
            "base_mrr": round(st.mean(r["base_mrr"] for r in g), 5),
            "strict_mrr": round(st.mean(r.get("strict_mrr", r["base_mrr"]) for r in g), 5),
            "scene_mrr": round(st.mean(r.get("scene_mrr", r["base_mrr"]) for r in g), 5),
            "d_mrr_role": round(st.mean(r["strict_mrr"] - r["base_mrr"] for r in d), 5) if d else 0.0,
            "d_mrr_role_scene": round(st.mean(r["scene_mrr"] - r["base_mrr"] for r in d), 5) if d else 0.0,
            "hit_base_role": round(st.mean(r["base_hit"] for r in d), 4) if d else None,
            "hit_strict_role": round(st.mean(r["strict_hit"] for r in d), 4) if d else None,
            "hit_scene_role": round(st.mean(r["scene_hit"] for r in d), 4) if d else None,
            "narration_gold_rows": sum(1 for r in d if r.get("narration_gold")),
            "starved_strict": sum(1 for r in d if r["strict_hit"] == 0 and r["base_hit"]),
        }
    d_role = [r["strict_mrr"] - r["base_mrr"] for r in rd]
    d_role_scene = [r["scene_mrr"] - r["base_mrr"] for r in rd]
    worst = min([v["d_mrr_role"] for v in per.values()] or [0])
    out = {
        "schema": "compendium_rag.p10_visibility_shadow/v1",
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "graph_sha": sha16(ROOT / "data" / "compendium_rag" / "graph.json"),
        "top_k": TOP_K, "deep": DEEP,
        "n_rows": len(rows), "n_role_domain": len(rd),
        "per_set": per,
        "mean_delta_strict_role": round(st.mean(d_role), 5) if d_role else None,
        "mean_delta_scene_role": round(st.mean(d_role_scene), 5) if d_role_scene else None,
        "worst_set_delta_strict": worst,
        "coverage": cover, "coverage_complete": complete,
        "verdict": ("不给判：覆盖不全，先跑完采集" if not complete else
                    ("不落地（Δ 越过 0.02 回退线）" if worst < -DELTABUDGET
                     else "可落地（Δ 在预注册的 0.02 回退线内）")),
        "budget": DELTABUDGET,
        "caveat": ("主体由 seeds 的第一个「角色」实体推断，与 L2.3 的口径一致；"
                   f"过滤作用在 top-{DEEP} 候选上并回填到 {TOP_K}，所以这不是「删了就少几条」，"
                   "而是重排后的真实读数。名形式判据与图上的 owner 边不等价 —— "
                   "真边标注能标注「别人转述 A 的事也归 A」，名字代理不能。"),
    }
    OUT_JSON.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    L = ["# P10·R2 前置影子：角色可见性过滤在三套 MRR 上的误伤（只读）",
         "",
         f"- 行数：{len(rows)}（角色域 {len(rd)}），冻结图 `{out['graph_sha']}`",
         f"- 判据：主体 = seeds 里第一个 `type==\"角色\"` 实体（与 L2.3 同口径）；"
         f"过滤在 top-{DEEP} 上做并**回填**到 top-{TOP_K}，所以报的是重排后的真实读数",
         "",
         "| 集 | n | 角色域 | base MRR | strict MRR | Δstrict(角色域) | scene MRR | Δscene(角色域) | 转述型金标行 |",
         "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for k, v in per.items():
        L.append(f"| {k} | {v['n']} | {v['n_role_domain']} | {v['base_mrr']:.5f} | "
                 f"{v['strict_mrr']:.5f} | **{v['d_mrr_role']:+.5f}** | {v['scene_mrr']:.5f} | "
                 f"{v['d_mrr_role_scene']:+.5f} | {v['narration_gold_rows']} |")
    L += ["",
          f"- 全库角色域平均 Δ：strict **{out['mean_delta_strict_role']:+.5f}** ／ "
          f"scene **{out['mean_delta_scene_role']:+.5f}**",
          f"- 最差集 Δ（strict）：{worst:+.5f}；预注册回退线 {DELTABUDGET} ⇒ **{out['verdict']}**",
          "",
          "读法：strict 是「只谈自己的块才可见」的最紧形态，scene 是「该章出现过即可见」的松形态。"
          "若 strict 判负而 scene 判可落地，R2 的实现就该取松的那一档 —— "
          "但这仍是名字代理的结论，真边标注的语义比它宽（可以标「别人转述 A 的事也归 A」），"
          "所以这里的 Δ 是**误伤上界**，不是终值。",
          "",
          "两条读数纪律：",
          "1. **recall@10 的 Δ 只列不判** —— 本主题的 R_q 是关键词子串在全语料扩出来的，"
          "单题可达几十上百块（实测有 365 块的），Recall@10 早被 10/R_q 数学封顶，"
          "这是项目里已登记过的死闸门，别拿它的变化当证据。判据用 MRR@10 与 hit@10。",
          "2. **Δ 为正不构成收益主张** —— 过滤顺带当了重排器，可能把更相关的可见块推前；"
          "本表只回答「有没有把本来可达的金标挡掉」，不回答「值不值得为它上线」。"]
    OUT_MD.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"[OK] 汇总 → {OUT_JSON.name} / {OUT_MD.name}")
    for k, v in per.items():
        print(f"     {k:8s} n={v['n']:4d} base={v['base_mrr']:.5f} "
              f"strict={v['strict_mrr']:.5f} ({v['d_mrr_role']:+.5f}) "
              f"scene={v['scene_mrr']:.5f} ({v['d_mrr_role_scene']:+.5f})")
    print(f"     最差 Δ {worst:+.5f} vs 回退线 {DELTABUDGET} ⇒ {out['verdict']}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["collect", "aggregate"], default="collect")
    ap.add_argument("--limit", type=int, default=0, help="调试：每集只取前 N 题")
    a = ap.parse_args()
    sys.exit(aggregate() if a.stage == "aggregate" else main_loop(a.limit))
