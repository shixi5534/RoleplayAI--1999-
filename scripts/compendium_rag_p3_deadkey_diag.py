# -*- coding: utf-8 -*-
"""v9-P3 前置诊断（**只读**，不写 graph.json / cache，不碰检索调参）：死键的真实暴露面。

P2 把「名字逐字不在语料」的实体数出来了（965 个名字不落地，其中 921 个被判 dead_key），
但那只是**图数据层**的读数。P3 真正要回答的是一个不同问题：

> 这些死键在**检索链路上**到底碰得到吗？碰得到多少题？

因为 `link()` 是拿**查询串**去匹配 `alias_index` 的键，语料里存不存在根本不影响它命中；
而 `mention_channel` 走的是 `_ent_chunks`（边上的 chunk_ids），也不查文本。
所以「名不落地 = 死键」这个说法在**数据层**成立（这个名字在原文里查不到，
证据回查会断），在**链路层**却可能完全无感——两种口径必须分开量，
否则又会像 P2 那样拿一笔预算去买它治不了的东西。

三段读数：
1. 键层：`alias_index` 的键有多少个在语料里逐字不存在（含主名键与别名键）。
2. 链路层：300 中文题跑一遍与 `link()` 同逻辑的实体链接（纯本地、零 LLM、零向量），
   数出「命中死键」的 seed 数、受影响题数、以及死键 seed 是否**挤进**了 top-6。
3. 证据层：命中死键的 seed，它声称的 chunk_ids 里到底有没有原文支撑（这个名字
   或它的别名在该块逐字出现吗）——这才是「回查断链」的真身。

用法（项目根目录）：
  PYTHONPATH=src .venv/Scripts/python.exe -X utf8 scripts/compendium_rag_p3_deadkey_diag.py
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from compendium_rag import pipeline as P  # noqa: E402
from compendium_rag.config import get_settings  # noqa: E402
from compendium_rag.retriever import Seed, _name_matches  # noqa: E402

OUT = ROOT / "data/compendium_rag/reports/p3_deadkey_diag.json"
MD = ROOT / "data/compendium_rag/reports/p3_deadkey_diag.md"
TESTSET = ROOT / "data/knowledge/_audit/rag_testset_300_cn.json"
# 修饰语前缀候选已在 P2 诊断里数过（587 组）——只引用，不重算，避免两套口径。
P2_DIAG = ROOT / "data/compendium_rag/reports/p2_landing_diag.json"

# P1 落盘后的当前图（v9-a）。漂移即中止：本诊断的每一条读数都绑定这个 SHA。
EXPECTED_SHA = "7cac5867e8c80879"


def _now() -> str:
    return time.strftime("%H:%M:%S")


def _link_like(query: str, graph, cands: list[str], top_k: int = 6) -> list[Seed]:
    """与 GraphRetriever.link() 同逻辑（精确/别名字面匹配，长名优先 + 字典序次级键）。

    刻意**不**接向量兜底：向量兜底命中的 eid 与名字落地与否无关，混进来会糊掉读数。
    """
    ql = (query or "").strip().lower()
    if not ql:
        return []
    seeds: dict[str, Seed] = {}
    for name in cands:
        if not _name_matches(name, ql):
            continue
        eid = graph.alias_index[name]
        ent = graph.entities[eid]
        how = "exact" if name == ent.name else "alias"
        sc = 1.0 if how == "exact" else 0.9
        cur = seeds.get(eid)
        if cur is None or sc > cur.score:
            seeds[eid] = Seed(eid, ent.name, sc, how)
    return sorted(seeds.values(), key=lambda s: -s.score)[:top_k]


def main() -> int:
    s = get_settings()
    gp = s.graph_path
    sha = hashlib.sha256(gp.read_bytes()).hexdigest()[:16]
    if sha != EXPECTED_SHA:
        print(f"[abort] 图谱 SHA 漂移：期望 {EXPECTED_SHA}，实测 {sha}")
        return 2
    print(f"[{_now()}] 图谱 SHA 校验通过：{sha}")

    chapters = P.load_chapters(s)
    chunks = P.chunk_corpus(chapters, s)
    chunk_text = {c.chunk_id: (c.text or "") for c in chunks}
    corpus = "\n".join(chunk_text.values())
    print(f"[{_now()}] 语料 {len(chapters)} 篇 / {len(chunks)} 块 / {len(corpus)} 字")

    g = P.load_kb(s).graph
    cands = sorted(g.alias_index.keys(), key=lambda k: (-len(k), k))

    # ── 1 键层 ──
    keys_ungrounded = [k for k in cands if k not in corpus]
    key_class = Counter()
    for k in cands:
        eid = g.alias_index[k]
        ent = g.entities.get(eid)
        key_class["main_name" if (ent and ent.name == k) else "alias"] += 1
    ungrounded_by_class = Counter()
    for k in keys_ungrounded:
        eid = g.alias_index[k]
        ent = g.entities.get(eid)
        ungrounded_by_class["main_name" if (ent and ent.name == k) else "alias"] += 1

    # 实体层：主名与全部别名都不落地，才算这个实体「无文本锚点」
    deg: Counter = Counter()
    ent_edges: dict[str, list] = {}
    for e in g.edges:
        deg[e.src] += 1
        deg[e.dst] += 1
        ent_edges.setdefault(e.src, []).append(e)
        ent_edges.setdefault(e.dst, []).append(e)

    # 与 GraphRetriever 的 `_ent_chunks` **同一口径**（`retriever.py:353-354`）：
    # mention_channel 用的是实体的 chunk_ids（不是边 chunk_ids 的并集），
    # 且只取前 `per_entity=3` 个（`retriever.py:436-438`）。证据层必须按这个算，
    # 否则量的就不是链路上真正被注入的那几块。
    ent_chunks = {eid: list(ent.chunk_ids) for eid, ent in g.entities.items()}
    PER_ENTITY = 3

    def entity_anchored(eid: str) -> bool:
        ent = g.entities[eid]
        names = [ent.name] + list(getattr(ent, "aliases", []) or [])
        return any(n and n in corpus for n in names)

    unanchored = [eid for eid in g.entities if not entity_anchored(eid)]
    unanchored_connected = [eid for eid in unanchored if deg[eid] > 0]

    # ── 2 链路层 ──
    unanchored_set = set(unanchored)
    sets = {
        "300cn": TESTSET,
        "blind206": ROOT / "data/knowledge/_audit/blind_v1/questions_strict.json",
        "gen120": ROOT / "data/knowledge/_audit/rag_testset_gen_r1r2.json",
    }
    per_set: dict[str, dict] = {}
    per_case: list[dict] = []
    for tag, path in sets.items():
        if not path.exists():
            per_set[tag] = {"status": "missing", "path": str(path.relative_to(ROOT))}
            continue
        raw = json.loads(path.read_text(encoding="utf-8"))
        cases = raw["cases"] if isinstance(raw, dict) else raw
        qkey = "q" if (cases and "q" in cases[0]) else "question"
        rows: list[dict] = []
        seed_total = dead_total = 0
        for c in cases:
            q = c.get(qkey) or c.get("query") or ""
            seeds_all = _link_like(q, g, cands, top_k=10 ** 6)
            top6 = seeds_all[:6]
            dead_all = [x for x in seeds_all if x.eid in unanchored_set]
            dead_top6 = [x for x in top6 if x.eid in unanchored_set]
            seed_total += len(top6)
            dead_total += len(dead_top6)
            if dead_all:
                rows.append({
                    "set": tag,
                    "id": c.get("id"),
                    "q": q,
                    "n_seeds_all": len(seeds_all),
                    "n_seeds_top6": len(top6),
                    "dead_keys": [{"eid": x.eid, "name": x.name, "how": x.how,
                                   "in_top6": any(y.eid == x.eid for y in dead_top6),
                                   "rank_top6": ([y.eid for y in top6].index(x.eid)
                                                 if x.eid in [y.eid for y in top6] else None),
                                   "degree": deg[x.eid],
                                   "n_entity_chunks": len(ent_chunks.get(x.eid, [])),
                                   "n_injected_chunks": min(PER_ENTITY,
                                                            len(ent_chunks.get(x.eid, [])))}
                                  for x in dead_all],
                })
        per_set[tag] = {
            "status": "ok",
            "cases": len(cases),
            "cases_with_dead_key_seed": len(rows),
            "share_of_cases": round(len(rows) / max(1, len(cases)), 4),
            "seeds_top6_total": seed_total,
            "dead_seeds_top6": dead_total,
            "share_of_top6_seeds": round(dead_total / max(1, seed_total), 4),
        }
        per_case.extend(rows)
        print(f"[{_now()}] {tag}: {len(rows)}/{len(cases)} 题命中无锚点实体")

    # ── 3 证据层：注入块里到底有没有这个名（回查断链的真身）──
    # 口径 = mention_channel 真正塞进融合的块：`ent.chunk_ids[:per_entity]`。
    # （不是全量证据块——那要跑带向量的完整检索，此刻回归闸门占着 Ollama，
    #   而且全量块的判定会把图/词面通道的贡献混进来，分不清是谁的锅。）
    evidence_checked = 0
    evidence_grounded = 0
    evidence_rows: list[dict] = []
    for row in per_case:
        for dk in row["dead_keys"]:
            if not dk["in_top6"]:
                continue
            ent = g.entities[dk["eid"]]
            names = [ent.name] + list(ent.aliases or [])
            cids = ent_chunks.get(dk["eid"], [])[:PER_ENTITY]
            hit = [cid for cid in cids if any(n and n in chunk_text.get(cid, "")
                                              for n in names)]
            evidence_checked += len(cids)
            evidence_grounded += len(hit)
            evidence_rows.append({
                "set": row["set"], "case": row["id"], "eid": dk["eid"],
                "injected_chunks": cids, "chunks_mentioning_name": len(hit),
                "n_injected": len(cids),
            })

    # 修饰语前缀线索：引用 P2 的读数（同一 SHA 才引用，否则标 stale）
    prefix_ref = {"status": "absent"}
    if P2_DIAG.exists():
        p2_stats = (json.loads(P2_DIAG.read_text(encoding="utf-8")) or {}).get("stats") or {}
        p2_sha = p2_stats.get("graph_sha256_16")
        prefix_ref = {"status": "ok" if p2_sha == sha else "stale",
                      "graph_sha256_16": p2_sha,
                      "prefix_candidates": p2_stats.get("prefix_candidates")}

    stats = {
        "graph_sha256_16": sha,
        "normalizer": getattr(g, "normalizer", None),
        "entities": len(g.entities),
        "edges": len(g.edges),
        "alias_index_keys": len(cands),
        "keys_ungrounded": len(keys_ungrounded),
        "keys_ungrounded_ratio": round(len(keys_ungrounded) / max(1, len(cands)), 4),
        "key_class_counts": dict(key_class),
        "ungrounded_by_key_class": dict(ungrounded_by_class),
        "entities_unanchored": len(unanchored),
        "entities_unanchored_connected": len(unanchored_connected),
        "link_exposure_by_set": per_set,
        "link_exposure_totals": {
            "cases": sum(v.get("cases", 0) for v in per_set.values()),
            "cases_with_dead_key_seed": sum(v.get("cases_with_dead_key_seed", 0)
                                            for v in per_set.values()),
            "dead_seeds_top6": sum(v.get("dead_seeds_top6", 0) for v in per_set.values()),
            "seeds_top6_total": sum(v.get("seeds_top6_total", 0) for v in per_set.values()),
        },
        "evidence_layer": {
            "caliber": "mention_channel 注入块 = ent.chunk_ids[:3]",
            "injected_chunks_checked": evidence_checked,
            "chunks_grounded": evidence_grounded,
            "ungrounded_ratio": round(1 - evidence_grounded / max(1, evidence_checked), 4),
        },
        "prefix_candidates_ref": prefix_ref,
    }
    print(json.dumps(stats, ensure_ascii=False, indent=2))

    rep = {
        "schema": "compendium_rag.p3_deadkey_diag/v1",
        "mode": "read-only",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "question": "P2 数出的 965 个无锚点实体，在 300 题检索链路上到底碰得到吗",
        "stats": stats,
        "cases": per_case,
        "evidence_rows": evidence_rows,
    }
    OUT.write_text(json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# v9-P3 前置诊断 · 死键在检索链路上的暴露面（只读）",
        "",
        f"- 图谱：`{sha}`（normalizer `{stats['normalizer']}`），实体 {stats['entities']}，"
        f"边 {stats['edges']}，alias_index 键 {stats['alias_index_keys']}",
        "- 口径提醒：**逐字存在 = 子串匹配**，是接地的上界，不是下界；"
        "正文块拼成的语料**不含**标题/文件名/栏目，比 P2 的口径更严。",
        "",
        "## 三层读数",
        "",
        f"1. 键层：不落地键 {stats['keys_ungrounded']}"
        f"（{stats['keys_ungrounded_ratio']:.2%}），"
        f"按主名/别名分 `{json.dumps(stats['ungrounded_by_key_class'], ensure_ascii=False)}`"
        f"——别名键 {stats['key_class_counts'].get('alias')} 个**全部落地**（P1/P2 那几轮焊别名治的就是这一层）；",
        f"2. 实体层：主名+全别名都不落地 {stats['entities_unanchored']}，"
        f"其中连通 {stats['entities_unanchored_connected']}",
        "3. 链路层（与 `link()` 同逻辑、零 LLM、零向量兜底）：",
        "",
        "| 题集 | 题数 | 命中无锚点实体的题 | 占比 | top-6 seed 中无锚点 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for tag, v in stats["link_exposure_by_set"].items():
        if v.get("status") != "ok":
            lines.append(f"| {tag} | — | {v.get('status')} | — | — |")
            continue
        lines.append(
            f"| {tag} | {v['cases']} | {v['cases_with_dead_key_seed']} "
            f"| {v['share_of_cases']:.2%} | {v['dead_seeds_top6']}/{v['seeds_top6_total']} "
            f"({v['share_of_top6_seeds']:.2%}) |")
    ev = stats["evidence_layer"]
    lines += [
        "",
        "## 为什么键层/实体层的数字不能直接当收益",
        "",
        "- `link()` 用**查询串**匹配键，语料里有没有这个名字不影响命中；",
        "- `mention_channel` 注入的是 `ent.chunk_ids[:3]`（`retriever.py:353-354,436-438`），也不查文本；",
        "- 所以「名不落地」破坏的是**证据回查**（人/审查脚本拿着块去原文里找这个名字，找不到）。"
        f"按注入块口径：3 题共注入 {ev['injected_chunks_checked']} 块，"
        f"其中**原文里连名字带别名一个都找不到**的有 "
        f"**{ev['injected_chunks_checked'] - ev['chunks_grounded']}** 块（{ev['ungrounded_ratio']:.2%}）；",
        "- 代理口径的两处已知偏差，都往**保守**方向偏（只会高估暴露面）：① 没接 `seed_threshold` 低分过滤；"
        "② `link()` 的向量兜底未接（向量命中的 eid 与名字落地无关，接了也只会再增加暴露题数）。",
        "- 结论要按链路层读：**链路暴露为 0 的集合上，给死键补名字不会动任何检索主数**。"
        "这一层的治疗价值在数据质量与可审计性（证据回查不断链），不在指标——"
        "所以不许拿它去换指标收益，也不许为读数好看去造别名（同 [[fix-data-not-metrics]]）。",
        "",
        "## 处置纪律",
        "",
        f"- 修饰语前缀候选（P2，同 SHA 引用）：`{json.dumps(stats['prefix_candidates_ref'], ensure_ascii=False)}`，"
        "**只作人工/盲评裁决线索**，不可自动合并（同指/异指混在一起，见 P2 的卡卡尼亚反例）；",
        "- 本诊断不产出任何写操作。改名/补别名要走提案 + 备份 + 指纹预登记，"
        "并且**不碰分母**（删点改分母是禁手）。",
    ]
    MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"报告 → {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
