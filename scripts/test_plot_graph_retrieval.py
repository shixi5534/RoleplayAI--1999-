# -*- coding: utf-8 -*-
"""剧情图谱重建后的端到端检索实测（非 pytest，直接跑真实数据）。

测什么：
1. 图谱能否加载、检索是否不抛异常；
2. 检索走的是「图谱路径（via=plot_graph）」还是「词法兜底（via=plot_lexical）」——
   前者说明种子链接 + PPR + 多跳都通了，后者说明图谱没接住；
3. **补抽的 395 块是否被真正召回**（这是本次 408 块回填的最终验收点）；
4. 召回的证据块里是否还混着上一轮清掉的幻觉实体（Madam Lucy 等）。

用法（项目根目录）：
  .venv/Scripts/python.exe -X utf8 scripts/test_plot_graph_retrieval.py
  .venv/Scripts/python.exe -X utf8 scripts/test_plot_graph_retrieval.py --top 5 --verbose
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from roleplay.config import get_settings  # noqa: E402
from roleplay.core.knowledge.factory import build_plot_registry  # noqa: E402

CHARACTER = "wu_ming_zhe"

# 覆盖：核心角色 / 组织 / 事件 / 补抽块里的冷门专名 / 英文原文查询
QUERIES = [
    "无名者是谁",
    "圣洛夫基金会是做什么的",
    "重塑之手的目的",
    "暴雨发生了什么",
    "维尔汀和司辰的关系",
    "伊戈尔",
    "乌尔德",
    "金预言",
    "潘家园",
    "巴比伦骰子",
    "皮罗斯",
    "曼佩刺杀",
    "Ms. Stranger",
    "Manus Vindictae",
    "the Storm",
    "SPDM",
]

# ── R13（噪声敏感性）监控口径（2026-09-12 修订）─────────────────────────────
# 历史缺陷：抽取模型把「Madam Lucy」当成**正名**写进 227 个正文根本没有 Lucy 的块。
# 旧监控口径是「检索结果文本里只要出现 Madam Lucy/露西/Lucy 就算幻觉」——但露西是
# 人工别名表锚定、灰机核实的**独立真实角色**（拉普拉斯科算中心负责人，与无名者是
# 两个人），正常提及会被这条口径误判。故改为两个**可证伪**的不变式：
#   ① 图中不得存在以称谓/句段形态为**正名**的实体（历史幻觉的落图形态）；
#   ② 因某实体名而入选的检索块，正文必须真的出现该实体的某个干净名字。
HALLUCINATION_WATCH = ["Madam Lucy", "露西", "Lucy"]  # 保留清单（报告字段兼容）


def _clean_names(store, ent_name: str) -> list[str]:
    """实体的「干净名字」集合（正名 + 非噪声别名，全部小写归一）。"""
    from roleplay.core.knowledge.graph_store import norm_name
    from roleplay.core.knowledge.plot_graph import is_noise_entity

    eid = store.link_exact(ent_name)
    ent = store.get_entity(eid) if eid else None
    if not ent:
        return []
    names = [str(ent.get("name") or "")] + [str(a) for a in (ent.get("aliases") or [])]
    return [norm_name(n) for n in names if n and not is_noise_entity(n)]


def _noise_canonical_hits(retr) -> list[str]:
    """不变式①：图中不得存在以**光杆称谓/语气词**为正名的实体。

    历史缺陷（docs/剧情图谱全量审查报告.md §三）：抽取模型把「Madam Lucy」写进
    227 个正文根本没有 Lucy 的块。落图后的可观测形态有两类：
      a. 光杆称谓被当成实体正名（``ma'am``/``señora``/``okay``…）——本不变式检查它；
      b. 带称谓的正常英文名（``Madam Lucy``/``St. Pavlov Foundation``）本身**合法**
         （``is_noise_entity`` 明确放行），其真伪只能靠"证据块正文是否出现该名字"
         判定，而共指（正文用 she/她 指代）会让该判定产生误报——故不在此断言，
         仅由不变式②兜住"检索层不得给出正文无该名的提及块"。
    """
    bare = {
        "ma'am", "senora", "señora", "senorita", "señorita", "madam", "madame",
        "sir", "miss", "mister", "mr", "ms", "mrs", "dr", "okay", "alright",
        "truly", "sorry", "please", "thank you", "excuse me", "everyone", "somebody",
    }
    hits: list[str] = []
    for ent in retr.store.entities():
        name = str(ent.get("name") or "").strip()
        if name and name.lower() in bare:
            hits.append(f"实体正名为光杆称谓：{name!r}")
    return hits


def _ungrounded_mention_hits(retr, chunks: list) -> list[str]:
    """不变式②：因某实体名而入选的提及块，正文必须真的出现该实体的干净名字。"""
    hits: list[str] = []
    clean = _clean_names(retr.store, "露西")
    if not clean:
        return hits
    for c in chunks:
        meta = c.metadata or {}
        if str(meta.get("seed_mention") or "") != "露西":
            continue
        low = c.text.lower()
        if not any(n in low for n in clean):
            hits.append(f"露西提及块正文无该名：{c.text[:40]!r}")
    return hits


def _backfill_hashes() -> set[str]:
    """6 个 apply_empty_p*.py 写入的块 hash（本次回填的全部成果）。"""
    hashes: set[str] = set()
    for p in (ROOT / "scripts").glob("apply_empty_p*.py"):
        hashes |= set(re.findall(r'"([0-9a-f]{16})":', p.read_text(encoding="utf-8")))
    return hashes


def _selftest_backfill(
    retr, backfill: set[str], text2hash: dict[str, str], n: int, top: int
) -> tuple[int, int, list[str]]:
    """反向验收：拿补抽块自己的实体名去查，看能否把该块召回。

    正向的 16 条固定查询只覆盖极少数补抽块（10/395 属正常），真正能说明
    「补抽内容是否可检索」的是这个反向测试。
    """
    import random

    cache_dir = ROOT / "data" / "knowledge" / "plot_cache" / CHARACTER
    sample = random.Random(42).sample(sorted(backfill), min(n, len(backfill)))
    hit = 0
    tried = 0
    miss: list[str] = []
    for h in sample:
        cache = cache_dir / f"{h}.json"
        if not cache.exists():
            continue
        ents = (json.loads(cache.read_text(encoding="utf-8")).get("entities") or [])
        if not ents:
            continue
        q = str(ents[0].get("name") or "").strip()
        if not q:
            continue
        tried += 1
        out = retr.retrieve(q, top_chunks=top)
        if h in {text2hash.get(c.text, "") for c in out}:
            hit += 1
        else:
            miss.append(f"{h}({q})")
    return hit, tried, miss


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=3, help="每问取几条证据")
    ap.add_argument("--verbose", action="store_true", help="打印证据正文")
    ap.add_argument(
        "--selftest-backfill",
        type=int,
        default=0,
        metavar="N",
        help="反向验收：抽样 N 个补抽块，用块内实体名查询，统计该块能否被召回",
    )
    ap.add_argument(
        "--include-weak",
        dest="include_weak",
        action="store_true",
        default=None,
        help="允许孤证边（evidence<2）参与检索，覆盖 settings.plot_include_weak",
    )
    args = ap.parse_args()

    settings = get_settings()
    # 与生产共用装配路径（build_plot_registry ← Settings），避免"调试脚本参数与生产漂移"
    # ——本脚本一度手工 new 注册表只传 include_weak，新增参数全被默认值覆盖。
    registry = build_plot_registry(settings)
    # Settings 是 frozen model，命令行覆盖只能改注册表内部配置并清缓存
    include_weak = (
        bool(args.include_weak)
        if args.include_weak is not None
        else bool(settings.plot_include_weak)
    )
    if include_weak != bool(settings.plot_include_weak):
        registry._cfg["include_weak"] = include_weak
        registry._cache.clear()
    print(f"[cfg ] plot_include_weak={include_weak}")
    retr = registry.get(CHARACTER)
    if retr is None:
        print("[FAIL] 图谱未能加载")
        return 1

    store = retr.store
    print(f"[load] 实体 {len(store.entities())}｜边 {len(store.all_edges())}")

    backfill = _backfill_hashes()
    # RetrievedChunk 只带 text/score/metadata，而 chunk.meta() 不含 hash，
    # 所以补抽块是否命中只能用「正文 → hash」反查。
    text2hash: dict[str, str] = {}
    for ch in retr.corpus.chunks:
        text2hash.setdefault(ch.text, ch.hash)
    hit_backfill: set[str] = set()
    via_graph = via_lexical = 0
    no_result: list[str] = []
    hallu_hits = len(_noise_canonical_hits(retr))

    for q in QUERIES:
        try:
            chunks = retr.retrieve(q, top_chunks=args.top)
        except Exception as exc:  # noqa: BLE001
            print(f"[ERROR] {q!r} → {type(exc).__name__}: {exc}")
            return 1
        if not chunks:
            no_result.append(q)
            print(f"  [空] {q}")
            continue
        # 排序后 BM25（词法）与 PPR（图谱）分数量纲不同，不能只看第一条：
        # 只要这批证据里存在 via=plot_graph，就说明图谱路径接通了。
        n_g = sum(1 for c in chunks if c.metadata.get("via") == "plot_graph")
        seeds = retr.link(q)
        seed_names = [
            (store.get_entity(eid) or {}).get("name", eid) for eid in list(seeds)[:4]
        ]
        if n_g:
            via_graph += 1
        else:
            via_lexical += 1
        tag = f"graph×{n_g}" if n_g else "lexical"
        print(f"  [{tag:<12}] {q}")
        print(f"      seeds: {seed_names or '（无）'}")
        first_graph = next(
            (c for c in chunks if c.metadata.get("via") == "plot_graph"), None
        )
        print(
            f"      edge: {first_graph.metadata.get('edge') if first_graph else '—'}"
        )
        for c in chunks:
            h = text2hash.get(c.text, "")
            if h in backfill:
                hit_backfill.add(h)
            if args.verbose:
                print(f"      - ({c.metadata.get('via')}/{c.metadata.get('path')}) {c.text[:110]}")
        hallu_hits += len(_ungrounded_mention_hits(retr, chunks))

    print("\n==== 汇总 ====")
    print(f"查询数 {len(QUERIES)}｜图谱路径命中 {via_graph}｜纯词法兜底 {via_lexical}｜无结果 {len(no_result)}")
    if no_result:
        print(f"  无结果查询：{no_result}")
    print(f"固定查询召回补抽块：{len(hit_backfill)} / {len(backfill)}")
    print(f"幻觉词重现计数：{hallu_hits}（期望 0）")

    if args.selftest_backfill:
        hit, tried, miss = _selftest_backfill(
            retr, backfill, text2hash, args.selftest_backfill, args.top
        )
        print(
            f"\n反向验收（抽样 {tried} 个补抽块，用块内实体名查询）："
            f"命中 {hit}（{hit/max(1,tried):.1%}）"
        )
        if miss:
            print(f"  未召回样例（{len(miss)}）：{miss[:10]}")

    ok = via_graph > 0 and hallu_hits == 0 and not no_result
    print("\n[RESULT]", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
