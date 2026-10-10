# -*- coding: utf-8 -*-
"""v9-P3 · 角色域过滤的**影子评测**（只读：不改 `retriever.py`、不改图、零 LLM/零嵌入）。

为什么先做影子：`docs/compendium-rag/优化计划_v9_2026-10-08.md` §P3 登记的顺序是
「曲线定档 → 影子评测 → 才允许落成参数化实现」。直接改排序会把过滤器的效果和
`max_edges` 曲线读数混进同一份产物，事后分不清是哪一项带来的变化。

判据与 L2.3 **不同构**（这是它不被判「同义反复刷数」的理由）：
- L2.3 问「块 `text/speakers` 里有没有被问角色的名字」；
- 本脚本问「**这块是谁的场景**」：`owners(chunk) = chunk.speakers ∩ 具名角色表`，
  具名角色表 = `type=='角色'` 且非 `is_generic_speaker` 的实体（name+alias）。
  块为跨域的条件：`owners` 非空 **且** 与**本次全部种子**的 eid 无交。
  用全部种子而非首种子：泛称题常同时锚到 伙计 和某个具名角色，只看首 seed 会把
  「问题里点名的人自己的场景」误判成跨域。

动作**只降权不剔除**：前置诊断实测 `300cn/R200` 的两块 gold 完全由别人说出
（卡戎/威利/士兵Ⅰ/士兵Ⅱ/沃尔克中校/帕蒂塔），剔除 = 把答案滤掉。打分是
`graph_channel 块分 *= (1 - w·[跨域块])`，`w` 只在本脚本里当扫描档，**不写回默认值**。

主判据（先于跑数登记，见计划文档同节）：
1. **金块不掉出**是硬检查——任何档的 hit@k 低于 w=0 基线即判负；
2. 跨域块里 gold 的占比说明「剔除式」为什么不可用；
3. 本脚本**产不出** confuse 认领率与 WP3 双盲正确性，所以它只回答
   「值不值得落成参数」，不构成验收（[[fix-data-not-metrics]]）。

只作用在图通道：`mention_channel`（种子自身出现块）不加罚——那是「这个角色自己说过
什么」的正路，加罚会把角色域题的召回一起打掉。

用法（务必脱离会话生命周期）：
    PYTHONPATH=src .venv/Scripts/python.exe -X utf8 \\
        scripts/compendium_rag_p3_rolefilter_shadow.py
产物：``data/compendium_rag/reports/p3_rolefilter_shadow{,_smoke}.{json,md}``
      逐题中间产物 ``reports/p3_rf_shadow{,_smoke}/{tag}_w{档}.jsonl``（按 qid 续跑）
"""
from __future__ import annotations

import asyncio
import hashlib
import importlib.util
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

for _k, _v in {"CMPRAG_LEX_WEIGHT": "1.0", "CMPRAG_RRF_K": "1",
               "CMPRAG_LEX_FIRST": "0", "PYTHONHASHSEED": "0"}.items():
    os.environ.setdefault(_k, _v)      # 必须在 import config 之前

from compendium_rag import pipeline as P  # noqa: E402
from compendium_rag.config import get_settings  # noqa: E402
from compendium_rag.corpus import is_generic_speaker  # noqa: E402

EXPECTED_SHA = "7cac5867e8c80879"      # v9-a（P1 产物）
R = ROOT / "data" / "compendium_rag" / "reports"
# 冒烟档与全量档**分目录分文件名**：按 qid 续跑时 3 题会冒充全量读数。
LIMIT = int(os.environ.get("P3_RF_SHADOW_LIMIT", "0"))
JSONL = R / ("p3_rf_shadow_smoke" if LIMIT else "p3_rf_shadow")
SUFFIX = "_smoke" if LIMIT else ""
SETS = {
    "300cn": ROOT / "data" / "knowledge" / "_audit" / "rag_testset_300_cn.json",
    "blind206": ROOT / "data" / "knowledge" / "_audit" / "blind_v1" / "questions_strict.json",
    "gen120": ROOT / "data" / "knowledge" / "_audit" / "rag_testset_gen_r1r2.json",
}
W_ARMS = [0.0, 0.25, 0.5, 0.75, 1.0]
W_BASE = 0.0
TOP_K = 6


def _load_eval():
    spec = importlib.util.spec_from_file_location(
        "ev300", ROOT / "scripts" / "compendium_rag_eval300.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    # 必须先注册再 exec：eval300 里有 @dataclass，dataclasses 会按
    # ``cls.__module__`` 回查 sys.modules，查不到就 AttributeError。
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def sha16(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def gold_blob(c) -> str:
    """与 `eval300.score_case` 判 hit 用的 blob 逐字一致，不另起一把尺子。"""
    return f"{c.text}\n{c.chapter_title}\n{c.scene_title}\n{c.part_title}"


class OwnerTable:
    """具名角色表 + 块归属。口径与 `p3_rolefilter_prereq_diag.py` 逐字一致。"""

    def __init__(self, graph, chunks):
        self.by_cid = {c.chunk_id: c for c in chunks}
        named = [e for e in graph.entities.values()
                 if e.type == "角色" and not is_generic_speaker(e.name)]
        self.name2eid: dict[str, str] = {}
        for e in named:
            for nm in (e.name, *e.aliases):
                if nm and nm not in self.name2eid:
                    self.name2eid[nm] = e.eid
        self._cache: dict[str, set[str]] = {}

    def owners(self, cid: str) -> set[str]:
        if cid not in self._cache:
            c = self.by_cid.get(cid)
            self._cache[cid] = {self.name2eid[s] for s in (c.speakers or [])
                                if s in self.name2eid} if c else set()
        return self._cache[cid]


def patch_graph_channel(kb, table: OwnerTable, w: float):
    """进程内替换 `graph_channel`：跨域块的分数乘 `(1-w)`。返回原函数以便还原。"""
    orig = kb.retriever.graph_channel

    def wrapper(seeds, **kw):
        chunk_scores, edges = orig(seeds, **kw)
        if not chunk_scores or not seeds:
            return chunk_scores, edges
        seed_eids = {s.eid for s in seeds}
        out = {}
        for cid, sc in chunk_scores.items():
            owners = table.owners(cid)
            cross = bool(owners) and not (owners & seed_eids)
            out[cid] = sc * (1.0 - w) if cross else sc
        return out, edges

    kb.retriever.graph_channel = wrapper
    return orig


def run_arm(kb, ev, table: OwnerTable, w: float, tag: str, cases) -> list[dict]:
    """一个档 × 一个集：逐题 append 到 jsonl；判分复用评测器；按 qid 续跑。"""
    out = JSONL / f"{tag}_w{w}.jsonl"
    done: dict[str, dict] = {}
    if out.exists():
        for line in out.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                done[r["qid"]] = r
    rows = [done[c.qid] for c in cases if c.qid in done]
    orig = patch_graph_channel(kb, table, w)
    try:
        with out.open("a", encoding="utf-8") as fh:
            for i, c in enumerate(cases, 1):
                if c.qid in done:
                    continue
                r = asyncio.run(ev.score_case(kb, c, TOP_K, False))
                r["w"] = w
                r["answerable"] = bool(c.dims.get("_answerable"))
                rows.append(r)
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
                fh.flush()
                if i % 50 == 0:
                    acc = sum(1 for x in rows if x["hit"]) / len(rows)
                    print(f"  [{tag} w={w}] {i}/{len(cases)} hit={acc:.4f}",
                          flush=True)
    finally:
        kb.retriever.graph_channel = orig       # 档间必须还原，否则罚分叠乘
    return rows


def cross_domain_census(kb, ev, table: OwnerTable, cases) -> dict:
    """w=0 基线下逐题统计：进窗块里多少跨域、其中多少是 gold。"""
    per_q = []
    for c in cases:
        res = asyncio.run(kb.retrieve(c.query, top_k=TOP_K, use_vector=False))
        seed_eids = {s["eid"] for s in res.get("seeds", [])}
        n_cross = n_cross_gold = 0
        for e in res.get("evidence", [])[:TOP_K]:
            cid = e["chunk_id"]
            owners = table.owners(cid)
            if owners and not (owners & seed_eids):
                n_cross += 1
                ch = kb.retriever.chunks.get(cid)
                if ch and any(k in gold_blob(ch) for k in c.keywords):
                    n_cross_gold += 1
        per_q.append({"qid": c.qid, "n_seeds": len(seed_eids),
                      "n_ev": len(res.get("evidence", [])[:TOP_K]),
                      "n_cross": n_cross, "n_cross_gold": n_cross_gold})
    tot_cross = sum(r["n_cross"] for r in per_q)
    tot_gold = sum(r["n_cross_gold"] for r in per_q)
    return {"questions": len(per_q),
            "questions_without_seeds": sum(1 for r in per_q if not r["n_seeds"]),
            "cross_domain_blocks_in_window": tot_cross,
            "blocks_in_window": sum(r["n_ev"] for r in per_q),
            "cross_domain_that_are_gold": tot_gold,
            "gold_share_of_cross": round(tot_gold / max(1, tot_cross), 4),
            "questions_with_any_cross": sum(1 for r in per_q if r["n_cross"]),
            "rows": per_q}


def main() -> int:
    s = get_settings()
    sha = sha16(s.graph_path)
    if sha != EXPECTED_SHA:
        raise SystemExit(f"图指纹漂移：期望 {EXPECTED_SHA}，实际 {sha}，中止")
    ev = _load_eval()
    kb = P.load_kb(s)
    table = OwnerTable(kb.graph, kb.chunks)
    JSONL.mkdir(parents=True, exist_ok=True)
    blob = "\n".join(c.text for c in kb.chunks)

    sets_read = {}
    for tag, path in SETS.items():
        cases = ev.load_cases(path)
        if LIMIT:
            cases = cases[:LIMIT]
        for c in cases:
            c.dims["_answerable"] = any(k in blob for k in c.keywords)
        arms = {}
        for w in W_ARMS:
            rows = run_arm(kb, ev, table, w, tag, cases)
            hit = sum(1 for r in rows if r["hit"]) / max(1, len(rows))
            mrr = sum(r["rr"] for r in rows) / max(1, len(rows))
            arms[str(w)] = {"n": len(rows),
                            "hit@6": round(hit, 4),
                            "MRR": round(mrr, 4),
                            "n_hit": sum(1 for r in rows if r["hit"])}
        census = cross_domain_census(kb, ev, table, cases)
        sets_read[tag] = {"n_cases": len(cases), "arms": arms,
                          "census": {k: v for k, v in census.items()
                                     if k != "rows"},
                          "census_rows": census["rows"]}
        print(f"[{tag}] " + " ".join(
            f"w={w}:{arms[str(w)]['hit@6']:.4f}" for w in W_ARMS), flush=True)

    regress = []
    for t, d in sets_read.items():
        base = d["arms"][str(W_BASE)]
        for w in W_ARMS[1:]:
            a = d["arms"][str(w)]
            if a["n_hit"] < base["n_hit"]:
                regress.append({"set": t, "w": w, "hit@6": a["hit@6"],
                                "base_hit@6": base["hit@6"],
                                "lost_questions": base["n_hit"] - a["n_hit"]})

    rep = {
        "done_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "graph_sha256_16": sha,
        "shadow_only": "只在进程内替换 graph_channel 打分；未改生产代码、未写图",
        "criterion": "owners = chunk.speakers ∩ 具名角色表(name+alias)；"
                     "owners 非空且与本次全部种子无交 → 跨域块，图通道块分 *= (1-w)",
        "why_no_drop": "R200 的两块 gold 全由别人说出；剔除式会直接滤掉答案",
        "mention_channel_untouched": True,
        "caliber": {k: os.environ.get(k) for k in
                    ("CMPRAG_LEX_WEIGHT", "CMPRAG_RRF_K", "CMPRAG_LEX_FIRST",
                     "PYTHONHASHSEED")},
        "top_k": TOP_K, "w_arms": W_ARMS, "smoke_limit": LIMIT,
        "sets": sets_read,
        "hit_regression": regress,
        "decision_rule": "硬检查=任何档 hit@6 不得低于 w=0；跨域块的 gold 占比越高说明"
                         "剔除式越不可用；泄漏降幅只报告，选档要另跑独立量（confuse/双盲）",
    }
    (R / f"p3_rolefilter_shadow{SUFFIX}.json").write_text(
        json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")

    md = ["# v9-P3 角色域过滤 · 影子评测", "",
          f"- 图 `{sha}`；**只读影子**（进程内替换图通道打分），`top_k={TOP_K}`，"
          f"档 `{W_ARMS}`（w=0 即基线）；`mention_channel` 不加罚"
          + (f"；**冒烟档 LIMIT={LIMIT}**" if LIMIT else ""),
          f"- 判据：{rep['criterion']}",
          f"- 不剔除的理由：{rep['why_no_drop']}", "",
          "| 集 | 题数 | " + " | ".join(f"w={w} hit@6" for w in W_ARMS)
          + " | 窗内块 | 跨域块 | 跨域且 gold | gold 占跨域 |"
          " 有跨域块的题 | 无种子题 |",
          "| --- | --- | " + " | ".join("---" for _ in W_ARMS)
          + " | --- | --- | --- | --- | --- | --- |"]
    for t, d in sets_read.items():
        c = d["census"]
        md.append(f"| {t} | {d['n_cases']} | "
                  + " | ".join(f"{d['arms'][str(w)]['hit@6']:.4f}" for w in W_ARMS)
                  + f" | {c['blocks_in_window']} | {c['cross_domain_blocks_in_window']}"
                  f" | {c['cross_domain_that_are_gold']}"
                  f" | {c['gold_share_of_cross']:.2%}"
                  f" | {c['questions_with_any_cross']}"
                  f" | {c['questions_without_seeds']} |")
    md += ["", "## MRR 同表（只报告，不用来选档）", "",
           "| 集 | " + " | ".join(f"w={w} MRR" for w in W_ARMS) + " |",
           "| --- | " + " | ".join("---" for _ in W_ARMS) + " |"]
    for t, d in sets_read.items():
        md.append(f"| {t} | " + " | ".join(
            f"{d['arms'][str(w)]['MRR']:.4f}" for w in W_ARMS) + " |")
    md += ["", "## 硬检查：金块不掉出（hit@6 回退）", ""]
    md += ([f"- **判负** `{r['set']}` w={r['w']}：{r['base_hit@6']:.4f} → "
            f"{r['hit@6']:.4f}（掉 {r['lost_questions']} 题）" for r in regress]
           or ["- 通过：任何档的 hit@6 都不低于 w=0 基线。"])
    md += ["", "> 影子脚本产不出 confuse 认领率 / WP3 双盲正确性，因此它只回答"
               "> 「值不值得落成参数」，**不构成验收**。", ""]
    (R / f"p3_rolefilter_shadow{SUFFIX}.md").write_text(
        "\n".join(md), encoding="utf-8")
    print(json.dumps({"hit_regression": regress,
                      "gold_share_of_cross": {
                          t: sets_read[t]["census"]["gold_share_of_cross"]
                          for t in sets_read}}, ensure_ascii=False))
    return 1 if regress else 0


if __name__ == "__main__":
    sys.exit(main())
