#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
灰机 wiki 事实问答评测：用项目真实检索器跑正典问题集。

与 verify_wiki_canonical.py 的区别：
  - verify_* 是**静态比对**：图谱里有没有这条边
  - 本脚本是**检索评测**：用户真的这么问，检索链路能不能把它激活出来

评测链路（复刻 GraphSearcher.retrieve 前半段，不依赖 kb/向量库）：
    实体链接 link(query) → PPR 激活 → 按 score 取 top 边

事实来源：deliverables/wiki-r1999-relation-reference-20260909.md

用法：
  .venv/Scripts/python.exe -X utf8 scripts/eval_wiki_retrieval.py [--json] [--top-k 12]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.roleplay.core.knowledge.graph_ppr import hop_distance, personalized_pagerank
from src.roleplay.core.knowledge.graph_search import GraphSearcher
from src.roleplay.core.knowledge.graph_store import GraphStore
from src.roleplay.core.knowledge.plot_corpus import PlotCorpus
from src.roleplay.core.knowledge.plot_graph import PlotGraphRetriever

LORE_GRAPH = ROOT / "data" / "knowledge" / "graph_wu_ming_zhe.json"
PLOT_GRAPH = ROOT / "data" / "knowledge" / "plot_graph_wu_ming_zhe.json"
PLOT_CORPUS = ROOT / "data" / "knowledge" / "plot_corpus_wu_ming_zhe.json"


class _StubKB:
    """仅满足 GraphSearcher 接口；本评测不回查证据块文本。"""

    version = "eval-stub"

    def list_items(self, ns: str):  # noqa: D102
        return []


# ------------------------------------------------------------------ 评测集
# (问题, 主语实体, 期望边(A,B), 答案实体, 备注)
# 期望边只校验两端实体，不校验谓语（谓语归一化仍在治理中）
QA = [
    ("无名者属于哪个组织？", "无名者", ("无名者", "圣洛夫基金会"), "圣洛夫基金会", ""),
    ("重塑之手的首领是谁？", "重塑之手", ("阿尔卡纳", "重塑之手"), "阿尔卡纳", ""),
    ("无名者曾经隶属哪个组织？", "无名者", ("无名者", "重塑之手"), "重塑之手", "曾隶属"),
    ("康斯坦丁在基金会担任什么职务？", "康斯坦丁", ("康斯坦丁", "圣洛夫基金会"), "康斯坦丁", ""),
    ("维尔汀隶属于哪里？", "维尔汀", ("维尔汀", "圣洛夫基金会"), "圣洛夫基金会", ""),
    ("无名者和康斯坦丁是什么关系？", "无名者", ("无名者", "康斯坦丁"), "康斯坦丁", "养母"),
    ("拉普拉斯科算中心归谁管？", "拉普拉斯科算中心", ("圣洛夫基金会", "拉普拉斯科算中心"),
     "圣洛夫基金会", ""),
    ("洛伦兹研究所属于哪个机构？", "洛伦兹研究所", ("拉普拉斯科算中心", "洛伦兹研究所"),
     "拉普拉斯科算中心", ""),
    ("谁给无名者做治疗？", "无名者", ("无名者", "小梅斯梅尔"), "小梅斯梅尔", ""),
    ("无名者对抗的人是谁？", "无名者", ("无名者", "阿尔卡纳"), "阿尔卡纳", ""),
    ("圣洛夫基金会的敌人是谁？", "圣洛夫基金会", ("圣洛夫基金会", "重塑之手"), "重塑之手", ""),
    ("无名者和维尔汀是什么关系？", "无名者", ("无名者", "维尔汀"), "维尔汀", "同伴"),
    ("勿忘我属于哪个组织？", "勿忘我", ("勿忘我", "重塑之手"), "重塑之手", "corpus_pending"),
    ("拉普拉斯科算中心的负责人是谁？", "拉普拉斯科算中心", ("露西", "拉普拉斯科算中心"),
     "露西", ""),
]


def build_lore(include_weak: bool = False):
    store = GraphStore(LORE_GRAPH, min_confidence=0.55)
    searcher = GraphSearcher(store, _StubKB(), namespace="graph_wu_ming_zhe",
                             min_confidence=0.55, include_weak=include_weak,
                             link_threshold=0.82, damping=0.85, max_iter=50,
                             max_hops=2, max_edges=12, top_chunks=0)
    return "lore", store, searcher, dict(min_confidence=0.55,
                                         include_weak=include_weak,
                                         damping=0.85, max_iter=50, max_hops=2)


def build_plot(include_weak: bool = False):
    corpus = PlotCorpus(PLOT_CORPUS, character_id="wu_ming_zhe")
    store = GraphStore(PLOT_GRAPH, min_confidence=0.6)
    retr = PlotGraphRetriever(corpus, store, namespace="plot_wu_ming_zhe",
                              min_confidence=0.6, include_weak=include_weak,
                              max_hops=2, damping=0.85, max_iter=40,
                              link_threshold=0.5, max_edges=10)
    return "plot", store, retr, dict(min_confidence=0.6,
                                     include_weak=include_weak,
                                     damping=0.85, max_iter=40, max_hops=2)


def activate(store, retriever, query: str, cfg: dict, top_k: int):
    """复刻 retrieve 的实体链接 → PPR → 打分取边（不回查证据块）"""
    seeds = retriever.link(query)
    if not seeds:
        return [], {}, []
    edges = store.all_edges()
    ranks = personalized_pagerank(edges, seeds,
                                  min_confidence=cfg["min_confidence"],
                                  include_weak=cfg["include_weak"],
                                  damping=cfg["damping"], max_iter=cfg["max_iter"])
    dist = hop_distance(edges, set(seeds), cfg["max_hops"],
                        min_confidence=cfg["min_confidence"],
                        include_weak=cfg["include_weak"])
    scored = []
    for e in edges:
        if float(e.get("confidence", 0.0)) < cfg["min_confidence"]:
            continue
        if not cfg["include_weak"] and len(e.get("evidence") or []) < 2:
            continue
        s, d = str(e.get("src")), str(e.get("dst"))
        if s not in dist or d not in dist:
            continue
        if max(dist[s], dist[d]) > cfg["max_hops"]:
            continue
        score = (ranks.get(s, 0.0) + ranks.get(d, 0.0)) * float(e.get("confidence", 0.0))
        if score > 0:
            scored.append((score, e))
    scored.sort(key=lambda kv: kv[0], reverse=True)
    top = scored[:top_k]
    names = lambda eid: str((store.get_entity(eid) or {}).get("name") or eid)
    top_edges = [(names(str(e["src"])), str(e.get("relation")), names(str(e["dst"])),
                  round(sc, 4)) for sc, e in top]
    # 激活实体：按 PPR 排序取 top 20
    top_ents = [names(eid) for eid, _ in
                sorted(ranks.items(), key=lambda kv: kv[1], reverse=True)[:20]]
    return top_edges, top_ents, list(seeds)


def name_to_eids(store, name: str) -> set:
    """实体名（含别名）→ eid 集合"""
    out = set()
    for eid, ent in store.entities().items() if isinstance(store.entities(), dict) \
            else [(e["eid"], e) for e in store.entities()]:
        names = {str(ent.get("name") or "")} | set(ent.get("aliases") or [])
        if any(name == n or (len(n) >= 2 and (name in n or n in name)) for n in names):
            out.add(eid)
    return out


def run(top_k: int, include_weak: bool = False) -> dict:
    result = {}
    for builder in (build_lore, build_plot):
        gname, store, retr, cfg = builder(include_weak=include_weak)
        rows = []
        for q, subj, (ea, eb), ans, note in QA:
            top_edges, top_ents, seeds = activate(store, retr, q, cfg, top_k)
            # 边命中：top 边中任一条两端（无向）等于期望两端
            edge_hit = any(
                {a, b} == {ea, eb} for a, _r, b, _s in top_edges
            )
            # 答案实体召回：激活实体 top20 中含答案实体
            ent_hit = any(ans == n or (len(ans) >= 2 and ans in n) for n in top_ents)
            # 链接命中：种子实体里是否有问题主语
            seed_names = [str((store.get_entity(s) or {}).get("name") or s) for s in seeds]
            link_hit = any(subj == n or (len(subj) >= 2 and subj in n) for n in seed_names)
            rows.append({
                "q": q, "expect_edge": f"{ea}—{eb}", "answer": ans, "note": note,
                "link_hit": link_hit, "edge_hit": edge_hit, "ent_hit": ent_hit,
                "top_edges": top_edges[:5], "seeds": seed_names[:5],
            })
        result[gname] = rows
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--top-k", type=int, default=12)
    ap.add_argument("--include-weak", action="store_true",
                    help="纳入孤证边（P4-0 A/B 口径对比用）")
    args = ap.parse_args()

    res = run(args.top_k, include_weak=args.include_weak)

    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0

    for gname, rows in res.items():
        print(f"\n{'='*78}\n{gname.upper()} 检索评测（top_k={args.top_k}，共 {len(rows)} 题）\n{'='*78}")
        print(f"{'链接':<5}{'边':<5}{'实体':<5} 问题")
        print("-" * 78)
        for r in rows:
            m = lambda b: "✅" if b else "❌"
            print(f"{m(r['link_hit']):<5}{m(r['edge_hit']):<5}{m(r['ent_hit']):<5} {r['q']}")
            if not r["edge_hit"]:
                print(f"      期望边 {r['expect_edge']}；实得 "
                      f"{' | '.join(f'{a}-{x}→{b}' for a,x,b,_ in r['top_edges'][:3]) or '（无激活）'}")
        lk = sum(1 for r in rows if r["link_hit"])
        eg = sum(1 for r in rows if r["edge_hit"])
        en = sum(1 for r in rows if r["ent_hit"])
        n = len(rows)
        print("-" * 78)
        print(f"实体链接成功率 {lk}/{n} = {lk/n*100:.1f}%")
        print(f"正确边召回率   {eg}/{n} = {eg/n*100:.1f}%")
        print(f"答案实体召回率 {en}/{n} = {en/n*100:.1f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
