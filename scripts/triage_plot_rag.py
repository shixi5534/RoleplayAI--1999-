# -*- coding: utf-8 -*-
"""剧情 RAG 失败分诊台：把「答不对」拆成「数据问题」与「检索问题」。

背景（为什么需要这个脚本）
    300 题评测台只回答「过不过」，不回答「为什么不过」。上一轮审计的结论是
    「严格通过率 45.7%、天花板内 49.5%」——但同一句话背后的修复动作完全不同：
      - 语料里根本没有这个事实        → 要联网补资料（灰机 wiki 为准）
      - 语料有、图谱没记这条证据      → 抽取/建图缺口（数据问题）
      - 图谱记了、检索没取回来        → 排序/预算问题（算法问题）
      - 查询里的名字不在图里          → 别名表缺口（数据问题）
    不分类就动手，等于把钱花在错的地方。

四级根因（对每个「缺失证据组」判定，取最严重的一级作为整题根因）
    1. ``corpus_gap``    ：8358 块语料里没有任何块含该组任一关键词 → 剧情资料缺失
    2. ``graph_gap``     ：语料有块，但这些块**一条都没被图谱引用为证据** → 建图/抽取缺口
    3. ``retrieval_gap`` ：图谱引用了这些块，但本次检索没返回 → 排序/预算/门控问题
    4. ``covered``       ：该组已被返回块覆盖（未缺失）

附带产出（都是后续行动的输入清单）
    - ``corpus_gap_groups``：需要按灰机 wiki 补的剧情事实（题号 + 关键词 + 章节）
    - ``unaligned_query_entities``：查询里出现的、图谱中并不存在的词（别名/实体缺口线索）
    - ``zero_hit_entities``：中文正名在语料中零命中、且度数 ≥3 的实体（别名表待补清单）

用法（项目根目录）：
    .venv/Scripts/python.exe -X utf8 scripts/triage_plot_rag.py
    .venv/Scripts/python.exe -X utf8 scripts/triage_plot_rag.py --limit 50
    .venv/Scripts/python.exe -X utf8 scripts/triage_plot_rag.py --no-retrieve   # 只做语料/图谱分诊

退出码：0 正常｜2 环境/数据缺失
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from roleplay.config import get_settings  # noqa: E402
from roleplay.core.knowledge.factory import build_plot_registry  # noqa: E402
from roleplay.core.knowledge.plot_corpus import chunk_hash  # noqa: E402
from roleplay.core.knowledge.plot_graph import is_noise_entity, norm_name  # noqa: E402

CHARACTER = "wu_ming_zhe"
TESTSET_PATH = ROOT / "data" / "knowledge" / "_audit" / "rag_testset_300.json"
DEFAULT_OUT = ROOT / "data" / "knowledge" / "_audit" / "plot_rag_triage.json"

# 单组最多留存的语料命中块数（只用于「有没有被图谱引用」的判定与抽样展示）
HIT_CAP = 800

# 查询里出现但不算「实体名」的常见疑问/停用片段（避免把「什么」「关系」当缺口）
_CJK_STOP = {
    "什么", "怎么", "为什么", "如何", "哪里", "哪个", "哪些", "是谁", "多少",
    "关系", "时候", "结局", "最后", "后来", "结果", "原因", "目的", "身份",
    "真名", "名字", "故事", "剧情", "经过", "后来", "之后", "之前", "在哪",
    "是谁", "是谁?", "结局如何", "有什么", "有没有", "是不是", "能不能",
}


def sha16(text: str) -> str:
    """与 PlotChunk.hash / graph evidence.hash 同口径的块指纹。"""
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:16]


def load_testset() -> list[dict]:
    data = json.loads(TESTSET_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, list) or not data:
        raise SystemExit(f"[FAIL] 题集为空或结构非法：{TESTSET_PATH}")
    return [it for it in data if isinstance(it, dict) and it.get("q") and it.get("evidence")]


def graph_evidence_hashes(store) -> set[str]:
    """图谱中所有边上引用过的语料块 hash（'图谱记过这条证据'的判据）。"""
    out: set[str] = set()
    for edge in store.all_edges():
        for ev in edge.get("evidence") or []:
            h = str((ev or {}).get("hash") or "")
            if h:
                out.add(h)
    return out


def degree_map(store) -> Counter:
    deg: Counter = Counter()
    for edge in store.all_edges():
        deg[str(edge.get("src"))] += 1
        deg[str(edge.get("dst"))] += 1
    return deg


def hash_to_entities(store) -> dict[str, set[str]]:
    """证据块 hash → 引用它的边的端点实体集合（判断「这块证据够得着吗」）。"""
    idx: dict[str, set[str]] = defaultdict(set)
    for edge in store.all_edges():
        src, dst = str(edge.get("src")), str(edge.get("dst"))
        for ev in edge.get("evidence") or []:
            h = str((ev or {}).get("hash") or "")
            if h:
                idx[h].add(src)
                idx[h].add(dst)
    return idx


def analyse_corpus(corpus, groups: list[list[str]]) -> list[dict]:
    """一次全语料扫描，给出每个证据组的命中块 hash（截断到 HIT_CAP）。"""
    hits: list[list[str]] = [[] for _ in groups]
    for chunk in corpus.chunks:
        text = chunk.text
        for gi, g in enumerate(groups):
            if len(hits[gi]) >= HIT_CAP:
                continue
            if any(kw in text for kw in g):
                hits[gi].append(chunk.hash or sha16(text))
    return [
        {"group": gi, "keywords": groups[gi], "n_hits": len(h), "hashes": h}
        for gi, h in enumerate(hits)
    ]


def extract_cjk_terms(query: str) -> list[str]:
    """从查询里粗提 2–8 字的中文候选实体词（含停用词过滤）。"""
    terms = []
    for run in re.findall(r"[\u4e00-\u9fff]{2,8}", query or ""):
        if run in _CJK_STOP or len(run) < 2:
            continue
        terms.append(run)
    return terms


def query_entity_mentions(retr, query: str) -> list[dict]:
    """查询里出现、且能对上图谱实体名/别名的实体（用于判断链接是否成功）。"""
    qn = norm_name(query)
    out = []
    for eid, canon, names in retr._named_entities():  # noqa: SLF001（诊断脚本，复用预计算表）
        for nn in names:
            if nn and len(nn) >= 2 and nn in qn:
                out.append({"eid": eid, "name": canon, "matched": nn})
                break
    return out


def name_index(retr) -> dict[str, str]:
    """归一名 → eid（图谱里所有正名与别名）。"""
    idx: dict[str, str] = {}
    for eid, _canon, names in retr._named_entities():  # noqa: SLF001
        for nn in names:
            if nn:
                idx.setdefault(nn, eid)
    return idx


def entity_names_index(retr) -> dict[str, list[str]]:
    """eid → 该实体的全部归一名（正名 + 别名）。"""
    out: dict[str, list[str]] = {}
    for eid, _canon, names in retr._named_entities():  # noqa: SLF001
        out[eid] = [n for n in names if n]
    return out


def query_names_entity(query: str, eid: str, eid_names: dict[str, list[str]]) -> list[str]:
    """查询里是否出现了该实体的任一名字（长度 ≥2 的归一名子串）。

    这是「查询→实体」这座桥是否存在的最硬判据：
      - 出现了却没链上  → 链接缺陷（算法）
      - 压根没出现      → 缺的是「描述性称谓 → 实体」的别名（数据，须按灰机核）
    """
    qn = norm_name(query)
    hits = []
    for nn in eid_names.get(eid, []):
        if len(nn) >= 2 and nn in qn:
            hits.append(nn)
    return hits


def group_entities(keywords: list[str], nidx: dict[str, str]) -> list[tuple[str, str]]:
    """证据组关键词能对上哪些图谱实体：``[(keyword, eid), ...]``。

    这是「这条证据的主体在图里存不存在」的判据——一个都对不上，说明该实体/别名
    根本没进图谱，再好的排序也取不回来（数据缺口，不是排序问题）。
    """
    out: list[tuple[str, str]] = []
    for kw in keywords:
        nk = norm_name(str(kw))
        if not nk:
            continue
        eid = nidx.get(nk)
        if eid is None:
            # 关键词是短语时允许子串命中（如证据词 "Rockin" 对应实体 "Rockin' Apple"）
            for name, cand in nidx.items():
                if len(nk) >= 4 and nk in name:
                    eid = cand
                    break
        if eid:
            out.append((str(kw), eid))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="剧情 RAG 失败分诊")
    ap.add_argument("--character", default=CHARACTER)
    ap.add_argument("--limit", type=int, default=0, help="只跑前 N 题（0=全量）")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--no-retrieve", action="store_true", help="跳过真实检索（只做语料/图谱分诊）")
    ap.add_argument("--top", type=int, default=0, help="覆盖 plot_max_chunks（默认取配置）")
    args = ap.parse_args()

    settings = get_settings()
    registry = build_plot_registry(settings)
    retr = registry.get(args.character)
    if retr is None:
        print(f"[FAIL] 图谱未加载（character={args.character}）")
        return 2

    corpus = retr.corpus
    store = retr.store
    top = args.top or int(getattr(settings, "plot_max_chunks", 3) or 3)
    lex = int(getattr(settings, "plot_lexical_fallback", 2) or 0)

    items = load_testset()
    if args.limit:
        items = items[: args.limit]

    ev_hashes = graph_evidence_hashes(store)
    h2e = hash_to_entities(store)
    deg = degree_map(store)
    nidx = name_index(retr)
    eid_names = entity_names_index(retr)
    print(f"[load] 语料 {len(corpus.chunks)} 块｜图 {len(store.entities())} 实体 / "
          f"{len(store.all_edges())} 边｜图上被引用过的证据块 {len(ev_hashes)}")

    t0 = time.perf_counter()
    rows: list[dict] = []
    for n, item in enumerate(items, start=1):
        groups = item["evidence"]
        cov = analyse_corpus(corpus, groups)

        if args.no_retrieve:
            covered = [False] * len(groups)
            paths: dict[str, int] = {}
            seeds: dict[str, dict] = {}
            active: set[str] = set()
        else:
            chunks = retr.retrieve(item["q"], top_chunks=top, lexical_fallback=lex)
            union = "\n".join(c.text for c in chunks)
            covered = [any(kw in union for kw in g) for g in groups]
            paths = dict(Counter(str((c.metadata or {}).get("path") or "?") for c in chunks))
            seeds = retr.link_detailed(item["q"])
            # 「够得着吗」：种子 + PPR 激活前 20 的实体，视为本次检索真正能触达的实体集。
            # 一条边两端都不在该集合里，说明这条证据即使被图谱记过，也不会被这次查询激活。
            ppr = retr._ppr({eid: float(info["weight"]) for eid, info in seeds.items()})  # noqa: SLF001
            active = set(seeds) | {
                eid for eid, _s in sorted(ppr.items(), key=lambda kv: -kv[1])[:20]
            }

        reasons: list[dict] = []
        for gi, g in enumerate(groups):
            if covered[gi]:
                continue
            info = cov[gi]
            referenced = [h for h in info["hashes"] if h in ev_hashes]
            reachable = [h for h in referenced if h2e.get(h, set()) & active]
            gents = group_entities(g, nidx)
            linked = sorted({eid for _kw, eid in gents if eid in seeds})
            in_query = sorted({
                nn for _kw, eid in gents for nn in query_names_entity(item["q"], eid, eid_names)
            })
            if info["n_hits"] == 0:
                reason = "corpus_gap"
            elif not gents:
                # 证据组的关键词（正典答案的写法）在图谱里找不到任何对应实体：
                # 实体/别名根本没进图 —— 纯数据缺口，与排序无关
                reason = "no_entity_gap"
            elif not in_query:
                # 查询里没有任何该实体的名字：缺的是「描述性称谓 → 实体」的别名桥（数据）
                reason = "alias_bridge_gap"
            elif not linked:
                # 名字就在查询里却没链上 → 链接缺陷（算法）
                reason = "link_bug"
            elif not referenced:
                reason = "graph_gap"
            elif not reachable:
                reason = "unreachable_gap"
            else:
                reason = "retrieval_gap"
            reasons.append({
                "group": gi,
                "keywords": g,
                "reason": reason,
                "corpus_hits": info["n_hits"],
                "graph_referenced": len(referenced),
                "reachable": len(reachable),
                "group_entities": [n for n, _e in gents][:6],
                "names_in_query": in_query[:4],
                "linked_entities": [str(seeds[e].get("name")) for e in linked][:4],
            })

        # 整题根因 = 最严重的一级（数据面 > 算法面）
        order = {"corpus_gap": 7, "no_entity_gap": 6, "alias_bridge_gap": 5,
                 "graph_gap": 4, "link_bug": 3, "unreachable_gap": 2, "retrieval_gap": 1}
        case_reason = "covered"
        if reasons:
            case_reason = max(reasons, key=lambda r: order[r["reason"]])["reason"]

        mentions = query_entity_mentions(retr, item["q"])
        rows.append({
            "id": item.get("id"),
            "q": item["q"],
            "ref": item.get("ref", ""),
            "dims": item.get("dims") or {},
            "covered": f"{len(groups) - len(reasons)}/{len(groups)}",
            "strict_pass": not reasons,
            "reason": case_reason,
            "details": reasons,
            "paths": paths,
            "n_seeds": len(seeds),
            "seed_names": sorted({str(v.get("name")) for v in seeds.values()})[:6],
            "query_mentions": [m["name"] for m in mentions][:6],
            "unlinked_mentions": [m["name"] for m in mentions if m["eid"] not in seeds][:6],
            "cjk_terms": extract_cjk_terms(item["q"])[:6],
        })
        if n % 50 == 0:
            print(f"  … {n}/{len(items)}")

    elapsed = time.perf_counter() - t0

    fails = [r for r in rows if not r["strict_pass"]]
    by_reason = Counter(r["reason"] for r in fails)
    by_reason_dim: dict[str, Counter] = defaultdict(Counter)
    for r in fails:
        by_reason_dim[r["reason"]][str((r["dims"] or {}).get("hop"))] += 1

    # ── 行动清单 1：需要按灰机 wiki 补的剧情资料（corpus_gap 组）──
    corpus_gaps = [
        {
            "id": r["id"], "q": r["q"], "ref": r["ref"],
            "chapter": (r["dims"] or {}).get("chapter"),
            "group": d["group"], "keywords": d["keywords"],
        }
        for r in fails for d in r["details"] if d["reason"] == "corpus_gap"
    ]

    # ── 行动清单 2：图谱没记证据的组（建图/抽取缺口）──
    graph_gaps = [
        {
            "id": r["id"], "q": r["q"], "ref": r["ref"], "group": d["group"],
            "keywords": d["keywords"], "corpus_hits": d["corpus_hits"],
        }
        for r in fails for d in r["details"] if d["reason"] == "graph_gap"
    ]

    # ── 行动清单 2b：证据在图上、但接不到本次能触达的实体（结构/链接缺口）──
    unreachable_gaps = [
        {
            "id": r["id"], "q": r["q"], "ref": r["ref"], "group": d["group"],
            "keywords": d["keywords"], "corpus_hits": d["corpus_hits"],
            "graph_referenced": d["graph_referenced"], "seeds": r["seed_names"],
        }
        for r in fails for d in r["details"] if d["reason"] == "unreachable_gap"
    ]

    # ── 行动清单 2c：证据组主体在图中无对应实体（实体/别名缺失 = 数据缺口）──
    no_entity_gaps = [
        {
            "id": r["id"], "q": r["q"], "ref": r["ref"], "group": d["group"],
            "keywords": d["keywords"], "corpus_hits": d["corpus_hits"],
            "chapter": (r["dims"] or {}).get("chapter"),
        }
        for r in fails for d in r["details"] if d["reason"] == "no_entity_gap"
    ]

    # ── 行动清单 2d：实体在图上、查询没链上（查询→实体的桥缺失）──
    not_linked_gaps = [
        {
            "id": r["id"], "q": r["q"], "ref": r["ref"], "group": d["group"],
            "keywords": d["keywords"], "group_entities": d["group_entities"],
            "seeds": r["seed_names"], "corpus_hits": d["corpus_hits"],
        }
        for r in fails for d in r["details"] if d["reason"] == "not_linked_gap"
    ]

    # ── 行动清单 2e：查询里根本没出现该实体的任何名字（描述性称谓别名缺失 = 数据）──
    alias_bridge_gaps = [
        {
            "id": r["id"], "q": r["q"], "ref": r["ref"], "group": d["group"],
            "keywords": d["keywords"], "group_entities": d["group_entities"],
            "seeds": r["seed_names"], "chapter": (r["dims"] or {}).get("chapter"),
            "corpus_hits": d["corpus_hits"],
        }
        for r in fails for d in r["details"] if d["reason"] == "alias_bridge_gap"
    ]

    # ── 行动清单 2f：名字就在查询里却没链上（链接缺陷 = 算法）──
    link_bugs = [
        {
            "id": r["id"], "q": r["q"], "ref": r["ref"], "group": d["group"],
            "names_in_query": d["names_in_query"], "seeds": r["seed_names"],
            "corpus_hits": d["corpus_hits"],
        }
        for r in fails for d in r["details"] if d["reason"] == "link_bug"
    ]

    # ── 行动清单 3：图谱记了证据却取不回（算法缺口）──
    retrieval_gaps = [
        {
            "id": r["id"], "q": r["q"], "group": d["group"], "keywords": d["keywords"],
            "graph_referenced": d["graph_referenced"], "paths": r["paths"],
            "seeds": r["seed_names"],
        }
        for r in fails for d in r["details"] if d["reason"] == "retrieval_gap"
    ]

    # ── 行动清单 4：别名表待补（中文正名零命中 + 度数 ≥3，未锚定）──
    anchored = {str(x) for x in (getattr(store, "anchored_ids", set()) or set())}
    zero_hit = []
    for ent in store.entities():
        eid = str(ent.get("id"))
        name = str(ent.get("name") or "")
        if not re.search(r"[\u4e00-\u9fff]", name):
            continue
        if deg.get(eid, 0) < 3 or eid in anchored or is_noise_entity(name):
            continue
        hits, _w = retr._name_hits(name)  # noqa: SLF001
        if hits:
            continue
        zero_hit.append({"eid": eid, "name": name, "degree": deg.get(eid, 0),
                         "type": ent.get("type"), "mentions": ent.get("mentions")})
    zero_hit.sort(key=lambda r: -r["degree"])

    # ── 行动清单 5：查询里提到、图上却没有对应实体的中文词（实体缺口线索）──
    term_missing: Counter = Counter()
    for r in fails:
        known = {norm_name(m) for m in r["query_mentions"]}
        for t in r["cjk_terms"]:
            if norm_name(t) in known:
                continue
            term_missing[t] += 1

    report = {
        "meta": {
            "tool": "scripts/triage_plot_rag.py",
            "character": args.character,
            "top": top, "lexical_fallback": lex,
            "cases": len(items), "elapsed_s": round(elapsed, 1),
            "corpus_chunks": len(corpus.chunks),
            "graph_entities": len(store.entities()),
            "graph_edges": len(store.all_edges()),
            "graph_evidence_blocks": len(ev_hashes),
        },
        "summary": {
            "pass": len(rows) - len(fails),
            "fail": len(fails),
            "strict_pass": round((len(rows) - len(fails)) / max(1, len(rows)), 4),
            "fail_by_reason": dict(by_reason),
            "fail_by_reason_hop": {k: dict(v) for k, v in by_reason_dim.items()},
            "corpus_gap_groups": len(corpus_gaps),
            "graph_gap_groups": len(graph_gaps),
            "unreachable_gap_groups": len(unreachable_gaps),
            "no_entity_gap_groups": len(no_entity_gaps),
            "not_linked_gap_groups": len(not_linked_gaps),
            "alias_bridge_gap_groups": len(alias_bridge_gaps),
            "link_bug_groups": len(link_bugs),
            "retrieval_gap_groups": len(retrieval_gaps),
            "zero_hit_entities": len(zero_hit),
        },
        "action_corpus_gap": corpus_gaps,
        "action_graph_gap": graph_gaps,
        "action_unreachable_gap": unreachable_gaps,
        "action_no_entity_gap": no_entity_gaps,
        "action_not_linked_gap": not_linked_gaps,
        "action_alias_bridge_gap": alias_bridge_gaps,
        "action_link_bug": link_bugs,
        "action_retrieval_gap": retrieval_gaps,
        "action_zero_hit_entities": zero_hit,
        "action_missing_query_terms": term_missing.most_common(80),
        "items": rows,
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")

    s = report["summary"]
    print("\n==== 分诊结果 ====")
    print(f"  通过 {s['pass']}/{len(rows)}（{s['strict_pass']:.1%}）｜失败 {s['fail']}")
    print(f"  失败根因：{s['fail_by_reason']}")
    print(f"  缺失证据组：语料缺口 {s['corpus_gap_groups']}｜实体缺失 {s['no_entity_gap_groups']}｜"
          f"别名桥缺失 {s['alias_bridge_gap_groups']}｜建图缺口 {s['graph_gap_groups']}｜"
          f"链接缺陷 {s['link_bug_groups']}｜接不上 {s['unreachable_gap_groups']}｜"
          f"够得着没取回 {s['retrieval_gap_groups']}")
    data_side = (s["corpus_gap_groups"] + s["no_entity_gap_groups"]
                 + s["alias_bridge_gap_groups"] + s["graph_gap_groups"])
    algo_side = s["link_bug_groups"] + s["unreachable_gap_groups"] + s["retrieval_gap_groups"]
    total_groups = data_side + algo_side
    print(f"  → 数据面 {data_side}/{total_groups} 组（{data_side / max(1, total_groups):.1%}）"
          f"｜算法面 {algo_side}/{total_groups} 组")
    print(f"  别名表待补（中文正名零命中·度≥3）：{s['zero_hit_entities']}")
    print(f"  用时 {elapsed:.1f}s")
    print(f"[save] {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
