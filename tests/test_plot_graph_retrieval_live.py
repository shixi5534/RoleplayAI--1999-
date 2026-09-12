# -*- coding: utf-8 -*-
"""剧情图谱**真实数据**端到端检索（pytest 可收集版）。

背景：``scripts/test_plot_graph_retrieval.py`` 是同一套检查的 CLI 版本，但它位于
``scripts/`` 而 ``pyproject.toml`` 的 ``testpaths = ["tests"]`` 只收集 ``tests/``——
也就是说**这套端到端检查从未进过 CI**。本文件把其中的断言部分抽成 pytest 用例
（查询清单与幻觉词清单仍从脚本导入，保持单一来源），脚本继续保留为可交互 CLI。

数据缺失（无真实语料/图谱）时整体 skip，离线环境照常通过。

运行：``.venv/Scripts/python.exe -m pytest tests/test_plot_graph_retrieval_live.py -q``
"""
from __future__ import annotations

import importlib.util
import json
import random
from pathlib import Path

import pytest

from roleplay.core.knowledge.plot_graph import PlotGraphRegistry

ROOT = Path(__file__).resolve().parent.parent
CORPUS_PATH = ROOT / "data" / "knowledge" / "plot_corpus_wu_ming_zhe.json"
GRAPH_PATH = ROOT / "data" / "knowledge" / "plot_graph_wu_ming_zhe.json"
ALIAS_PATH = ROOT / "data" / "lore" / "wu_ming_zhe" / "plot_aliases.json"
CHARACTER = "wu_ming_zhe"
# 反向验收（用块内实体名查回该块）实测召回 52.5%（21/40），门槛取 30% 留足抖动空间
BACKFILL_RECALL_FLOOR = 0.30


def _load_script(name: str):
    """按路径加载 scripts/ 下的脚本（保持查询清单单一来源）。"""
    spec = importlib.util.spec_from_file_location(f"_live_{name}", ROOT / "scripts" / name)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


@pytest.fixture(scope="module")
def live():
    """(retriever, 脚本模块, text→hash)。缺真实数据则跳过整组。"""
    if not (CORPUS_PATH.is_file() and GRAPH_PATH.is_file()):
        pytest.skip("缺少真实剧情语料/图谱")
    mod = _load_script("test_plot_graph_retrieval.py")
    registry = PlotGraphRegistry(
        corpus_dir=str(ROOT / "data" / "knowledge"),
        graph_dir=str(ROOT / "data" / "knowledge"),
        alias_dir=str(ROOT / "data" / "lore"),
    )
    retr = registry.get(CHARACTER)
    if retr is None or not retr.corpus.chunks:
        pytest.skip("剧情图谱未能加载")
    text2hash: dict[str, str] = {}
    for chunk in retr.corpus.chunks:
        text2hash.setdefault(chunk.text, chunk.hash)
    return retr, mod, text2hash


def test_fixed_queries_all_return_graph_evidence(live):
    """16 条固定查询：每条都要有结果，且至少一块来自图谱路（不许退化成纯词法）。"""
    retr, mod, _t2h = live
    empty: list[str] = []
    lexical_only: list[str] = []
    for q in mod.QUERIES:
        chunks = retr.retrieve(q, top_chunks=3)
        if not chunks:
            empty.append(q)
            continue
        if not any(c.metadata.get("via") == "plot_graph" for c in chunks):
            lexical_only.append(q)
    assert not empty, f"这些查询零结果：{empty}"
    assert not lexical_only, f"这些查询只剩词法兜底（图谱没接住）：{lexical_only}"


def test_hallucination_invariants_hold(live):
    """R13（噪声敏感性）不变式：历史幻觉「Madam Lucy 被系统性硬塞」不得复现。

    口径修订（2026-09-12，见审计报告）：旧口径是"结果文本里出现 Madam Lucy/露西/Lucy
    即算幻觉"，但露西是**人工别名表锚定、灰机核实的独立真实角色**——该口径会把正常
    提及误判（实测「Manus Vindictae」查到的正是真句 "…provided by Miss Lucy confirms
    that the Manus are moving…"）。改为两个可证伪的不变式：
      ① 图中不得有以噪声形态（称谓/句段/代词）为**正名**的实体；
      ② 因某实体名入选的提及块，正文必须真的出现该实体的干净名字。
    """
    retr, mod, _t2h = live
    assert not mod._noise_canonical_hits(retr), "图内出现噪声形态的正名实体"
    hits: list[str] = []
    for q in mod.QUERIES:
        hits += mod._ungrounded_mention_hits(retr, retr.retrieve(q, top_chunks=3))
    assert not hits, f"提及块缺乏正文自证：{hits[:5]}"


def test_backfill_blocks_are_retrievable(live):
    """补抽块反向验收：拿块内实体名去查，应能以 ≥30% 的比率召回该块本身。

    正向 16 条固定查询只覆盖极少数补抽块（6/395 属正常），因此用这个反向抽样测试
    衡量「补抽内容是否真的可检索」。
    """
    retr, mod, text2hash = live
    backfill = mod._backfill_hashes()
    if not backfill:
        pytest.skip("没有 apply_empty_p*.py 补抽记录，反向验收不适用")
    cache_dir = ROOT / "data" / "knowledge" / "plot_cache" / CHARACTER
    sample = random.Random(42).sample(sorted(backfill), min(40, len(backfill)))
    tried = hit = 0
    miss: list[str] = []
    for h in sample:
        cache = cache_dir / f"{h}.json"
        if not cache.exists():
            continue
        ents = json.loads(cache.read_text(encoding="utf-8")).get("entities") or []
        name = str((ents[0] if ents else {}).get("name") or "").strip()
        if not name:
            continue
        tried += 1
        got = {text2hash.get(c.text, "") for c in retr.retrieve(name, top_chunks=3)}
        if h in got:
            hit += 1
        else:
            miss.append(f"{h}({name})")
    if not tried:
        pytest.skip("抽样里没有可用的补抽块缓存")
    ratio = hit / tried
    assert ratio >= BACKFILL_RECALL_FLOOR, (
        f"补抽块反向召回率 {ratio:.1%}（{hit}/{tried}）低于门槛 "
        f"{BACKFILL_RECALL_FLOOR:.0%}；未命中样例 {miss[:5]}"
    )
