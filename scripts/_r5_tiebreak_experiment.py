# -*- coding: utf-8 -*-
"""Phase 2 决定性实验：alias_index 插入序是否真的改变检索结果？

背景（#39 核验）：
  retriever.py:300 `sorted(alias_index.keys(), key=len, reverse=True)`
  Python 稳定排序 -> 同长键的先后完全由**字典插入序**决定。
  R4 时代的评测跑在 Applier 落盘后的暖进程里（内存插入序），
  冷启动则自 graph.json 重建（文件序），两者插入序不同 -> 边界题翻转。

本脚本只做只读验证，不写任何图/索引：
  1. 用两种「合法但顺序不同」的方式构造 GraphStore（同内容、不同插入序）；
  2. 对同一批查询跑 link()，比较 seeds 与最终 top-k chunks；
  3. 定位究竟是哪些查询受影响，并给出「加显式次级键后是否收敛」的判据。

用法:
  ./.venv/Scripts/python.exe scripts/_r5_tiebreak_experiment.py
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from compendium_rag.config import get_settings          # noqa: E402
from compendium_rag.graph_store import GraphStore       # noqa: E402
from compendium_rag.retriever import GraphRetriever     # noqa: E402


def build_alias_index_in_order(g: GraphStore, entity_order: list[str]) -> dict[str, str]:
    """复刻 graph_store.py:263-266 的构造，但按指定实体顺序插入。"""
    ai: dict[str, str] = {}
    for eid in entity_order:
        e = g.entities[eid]
        # 263-264: 成员名直接赋值
        ai[e.name] = eid
        # 265-266: 别名 setdefault
        for a in (e.aliases or []):
            ai.setdefault(a, eid)
    return ai


def link_with_index(g: GraphStore, alias_index: dict[str, str], query: str,
                    top_k: int = 6):
    """用给定的 alias_index 复现 GraphRetriever.link()（retriever.py:288-312）。"""
    from compendium_rag.retriever import _name_matches, Seed
    ql = (query or "").strip().lower()
    seeds: dict[str, Seed] = {}
    # 关键行：与 retriever.py:300 完全一致（无次级键）
    cands = sorted(alias_index.keys(), key=len, reverse=True)
    for name in cands:
        if not _name_matches(name, ql):
            continue
        eid = alias_index[name]
        ent = g.entities[eid]
        how = "exact" if name == ent.name else "alias"
        sc = 1.0 if how == "exact" else 0.9
        cur = seeds.get(eid)
        if cur is None or sc > cur.score:
            seeds[eid] = Seed(eid, ent.name, sc, how)
    return sorted(seeds.values(), key=lambda s: -s.score)[:top_k]


def link_with_tiebreak(alias_index: dict[str, str], g: GraphStore, query: str,
                       top_k: int = 6):
    """加显式次级键后（提案修复）的结果：键按 (-len, 键本身) 排序。"""
    from compendium_rag.retriever import _name_matches, Seed
    ql = (query or "").strip().lower()
    seeds: dict[str, Seed] = {}
    cands = sorted(alias_index.keys(), key=lambda k: (-len(k), k))
    for name in cands:
        if not _name_matches(name, ql):
            continue
        eid = alias_index[name]
        ent = g.entities[eid]
        how = "exact" if name == ent.name else "alias"
        sc = 1.0 if how == "exact" else 0.9
        cur = seeds.get(eid)
        if cur is None or sc > cur.score:
            seeds[eid] = Seed(eid, ent.name, sc, how)
    return sorted(seeds.values(), key=lambda s: -s.score)[:top_k]


def main() -> int:
    s = get_settings()
    graph_path = s.data_dir / "graph.json"
    print(f"[load] {graph_path}")
    g = GraphStore.load(graph_path)
    print(f"[load] entities={len(g.entities)} edges={len(g.edges)} "
          f"on-disk alias_index={len(g.alias_index)}")

    eids_cold = [e.eid for e in g.entities.values()]

    # 暖序模拟：Applier 逐条 apply 时，被触碰的实体会被「重新赋值」到 dict 尾部。
    # CPython 的 dict 保持插入序；对已存在键赋值不改变位置，但新键追加到末尾。
    # R1-R4 反复 remove_alias/add_alias 会改变实体别名集合 -> 重建时集合序不同。
    # 这里用固定种子洗牌来采样「另一种合法插入序」。
    eids_warm = eids_cold[:]
    random.Random(20260927).shuffle(eids_warm)

    ai_cold = build_alias_index_in_order(g, eids_cold)
    ai_warm = build_alias_index_in_order(g, eids_warm)

    print(f"[alias] cold keys={len(ai_cold)} warm keys={len(ai_warm)}")
    same_map = ai_cold == ai_warm
    print(f"[alias] 两种插入序得到的 **键->实体映射完全相同**: {same_map}")
    if not same_map:
        diff = {k for k in set(ai_cold) | set(ai_warm)
                if ai_cold.get(k) != ai_warm.get(k)}
        print(f"[alias] 映射不同的键: {len(diff)} 例 -> {sorted(diff)[:10]}")

    # 键集合相同，但排序后顺序不同 -> 这才是 tie-break 的着力点
    order_cold = sorted(ai_cold.keys(), key=len, reverse=True)
    order_warm = sorted(ai_warm.keys(), key=len, reverse=True)
    print(f"[order] 无次级键排序结果相同: {order_cold == order_warm}")

    # 测试集：只取有 gold 的题
    ts_path = ROOT / "data/knowledge/_audit/rag_testset_300_cn.json"
    ts = json.loads(ts_path.read_text(encoding="utf-8"))
    items = ts["cases"] if isinstance(ts, dict) else ts
    print(f"[tset] {ts_path.name} items={len(items)}")

    flip = []
    n_seed_diff = 0
    for it in items:
        q = it.get("q") or it.get("question") or it.get("query") or ""
        qid = it.get("id") or it.get("qid")
        a = link_with_index(g, ai_cold, q)
        b = link_with_index(g, ai_warm, q)
        c = link_with_tiebreak(ai_cold, g, q)
        d = link_with_tiebreak(ai_warm, g, q)
        sa = [x.eid for x in a]
        sb = [x.eid for x in b]
        if sa != sb:
            n_seed_diff += 1
            flip.append((qid, sa, sb, [x.eid for x in c]))
        # 次级键修复后，两种插入序必须给出相同结果
        assert [x.eid for x in c] == [x.eid for x in d], f"tie-break 未收敛: {qid}"

    print()
    print("=" * 72)
    print(f"[RESULT] seeds 随插入序改变的题数: {n_seed_diff} / {len(items)}")
    for qid, sa, sb, sc in flip[:15]:
        print(f"  {qid}: cold={sa}")
        print(f"       warm={sb}")
        print(f"       tie-broken={sc}")
    print("=" * 72)
    print(f"[RESULT] 加显式次级键后，全部 {len(items)} 题的 seeds 在两种插入序下一致: True")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
