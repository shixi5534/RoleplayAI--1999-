# -*- coding: utf-8 -*-
"""关系命名治理验证脚本（治理三步后的量化验证）。

产出两组可验证指标：
A. 关系词频分布：唯一关系名数、单例谓语占比（治理目标：≤300 / ≤40%）。
B. 检索烟雾测试：≥10 条代表性查询，对比归一化前后图谱路的非空率与命中块数。
   - plot 图谱：归一化前（.bak_relnorm 备份）vs 归一化后（当前文件）。
   - lore 图谱：全新构建（无历史版本），只报告当前非空率，并与 plot 同口径对照。

用法（项目根目录执行）：
  python scripts/verify_relation_governance.py --plot
  python scripts/verify_relation_governance.py --lore
  python scripts/verify_relation_governance.py --plot --lore --json
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from roleplay.config import get_settings  # noqa: E402
from roleplay.core.knowledge.graph_store import GraphStore  # noqa: E402

KNOWLEDGE_DIR = ROOT / "data" / "knowledge"

# 代表性查询（覆盖角色 / 组织 / 物品 / 事件 / 地点 / 关系问句六类）
SMOKE_QUERIES = [
    "圣洛夫基金会是什么组织",
    "重塑之手的阴谋",
    "司辰是谁",
    "维尔汀与基金会的关系",
    "暴雨是什么事件",
    "阿黛尔的经历",
    "伊戈尔背叛",
    "露西女士是谁",
    "纳西索斯的传说",
    "玩具盒是什么物品",
    "无名者是谁",
    "玛蒂尔达和谁同行",
    "拉普拉斯计算中心",
    "神秘学家的隶属",
    "阿尔卡纳的目的",
    "1999年发生了什么",
]


def _dist(edges: list[dict]) -> dict:
    c = collections.Counter(str(e.get("relation") or "") for e in edges)
    uniq = len(c)
    total = sum(c.values())
    singles = sum(1 for v in c.values() if v == 1)
    return {
        "edges": total,
        "unique_relations": uniq,
        "singletons": singles,
        "singleton_ratio_of_unique": round(singles / uniq, 4) if uniq else 0.0,
        "singleton_ratio_of_edges": round(singles / total, 4) if total else 0.0,
        "top10_share": round(
            sum(v for _, v in c.most_common(10)) / total, 4
        )
        if total
        else 0.0,
        "top15_relations": dict(c.most_common(15)),
    }


def _smoke(retriever, queries: list[str]) -> dict:
    rows = []
    for q in queries:
        try:
            chunks = retriever.retrieve(q, top_chunks=3, lexical_fallback=0)
        except TypeError:
            # GraphSearcher（lore 层）的 retrieve 无 kwargs，top_chunks 走构造参数
            chunks = retriever.retrieve(q)
        via = [str(c.metadata.get("via")) for c in chunks]
        rows.append(
            {
                "query": q,
                "hits": len(chunks),
                "nonempty": bool(chunks),
                # plot 层 via="plot_graph"，lore 层 via="graph"
                "graph_path_hits": sum(1 for v in via if v in ("graph", "plot_graph")),
            }
        )
    n = len(rows)
    return {
        "queries": n,
        "nonempty": sum(1 for r in rows if r["nonempty"]),
        "nonempty_rate": round(sum(1 for r in rows if r["nonempty"]) / n, 4) if n else 0.0,
        "total_chunks": sum(r["hits"] for r in rows),
        "avg_chunks": round(sum(r["hits"] for r in rows) / n, 2) if n else 0.0,
        "graph_path_chunks": sum(r["graph_path_hits"] for r in rows),
        "rows": rows,
    }


def verify_plot(as_json: bool) -> dict:
    from roleplay.core.knowledge.plot_corpus import PlotCorpus, plot_namespace
    from roleplay.core.knowledge.plot_graph import PlotGraphRetriever

    cur = KNOWLEDGE_DIR / "plot_graph_wu_ming_zhe.json"
    baks = sorted(KNOWLEDGE_DIR.glob("plot_graph_wu_ming_zhe.json.bak_relnorm_*"))
    if not baks:
        raise SystemExit("[error] 找不到归一化前备份（.bak_relnorm_*）")
    bak = baks[-1]
    corpus_path = KNOWLEDGE_DIR / "plot_corpus_wu_ming_zhe.json"
    corpus = PlotCorpus(corpus_path, character_id="wu_ming_zhe")

    result: dict = {"backup": str(bak), "current": str(cur)}
    for tag, gpath in (("before", bak), ("after", cur)):
        store = GraphStore(gpath)
        retr = PlotGraphRetriever(
            corpus,
            store,
            namespace=plot_namespace("wu_ming_zhe"),
            include_weak=True,
        )
        result[tag] = {
            "relation_dist": _dist(store.all_edges()),
            "smoke": _smoke(retr, SMOKE_QUERIES),
        }
    result["smoke_detail"] = {
        "before": result["before"]["smoke"]["rows"],
        "after": [
            {
                "query": r["query"],
                "hits": r["hits"],
                "graph_path_hits": r["graph_path_hits"],
            }
            for r in result["after"]["smoke"]["rows"]
        ],
    }
    for tag in ("before", "after"):
        result[tag]["smoke"].pop("rows", None)
    return result


def verify_lore(as_json: bool) -> dict:
    from roleplay.core.knowledge.graph_search import GraphSearcher
    from roleplay.core.knowledge.vector_store import KnowledgeBase
    from roleplay.core.knowledge.embedder import build_embedder

    settings = get_settings()
    gpath = Path(settings.graph_dir) / "graph_wu_ming_zhe.json"
    if not gpath.exists():
        raise SystemExit(f"[error] lore 图谱未构建：{gpath}")
    kb = KnowledgeBase(
        embedder=build_embedder(settings), persist_dir=settings.knowledge_dir
    )
    store = GraphStore(gpath)
    searcher = GraphSearcher(
        store,
        kb,
        embedder=build_embedder(settings),
        namespace="graph_wu_ming_zhe",
        # 烟雾测试口径与 plot 层一致（include_weak=True）：
        # 新建 lore 图多数边仅 1 条证据，默认孤证门会全灭，测不出连接密度。
        include_weak=True,
    )
    smoke = _smoke(searcher, SMOKE_QUERIES)
    if not as_json:
        smoke["rows"] = [
            {k: v for k, v in r.items() if k != "query"} | {"query": r["query"]}
            for r in smoke["rows"]
        ]
    return {
        "graph": str(gpath),
        "relation_dist": _dist(store.all_edges()),
        "smoke": smoke,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="关系命名治理量化验证")
    p.add_argument("--plot", action="store_true", help="验证剧情图谱（前/后对比）")
    p.add_argument("--lore", action="store_true", help="验证 lore 图谱")
    p.add_argument("--json", action="store_true", help="精简 JSON 输出")
    args = p.parse_args(argv)
    if not (args.plot or args.lore):
        args.plot = args.lore = True

    out: dict = {}
    if args.plot:
        out["plot"] = verify_plot(args.json)
    if args.lore:
        out["lore"] = verify_lore(args.json)
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
