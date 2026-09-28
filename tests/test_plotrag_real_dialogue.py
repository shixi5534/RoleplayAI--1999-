# -*- coding: utf-8 -*-
"""真实对话回归（2026-09-12 用户实测 7 句）。

背景：用户在实际对话里问下列 7 个名字，角色（无名者）的回答是「没接触过 / 记不清」。
逐句诊断（docs/plot-graph-rag/audit/plot-rag-dialogue-fix-20260912.md）确认不是模型问题：
  ① 剧情图谱层当时**没开**（plot_graph_enabled=False），检索到的东西一个字都没进提示词；
  ② 语料是英文 ASR，6/7 个中文名在手工 lore 资料里 0 命中，必须靠别名桥；
  ③ 开启后另有三个排序缺陷把答案块丢掉（脏别名劫持 / 边证据压过提及块 / 0.85 相对门）。

本文件把这 7 句固化为**可证伪**的验收：
**注入提示词的前 2 块里，至少 1 块含该实体的可信名**（可信名由检索器自己判定，
不是硬编码清单——旧实现下牙仙的 top 块是 Campbell/doll，会直接判失败）。

数据缺失时整体 skip。
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from roleplay.core.knowledge.factory import build_plot_registry

ROOT = Path(__file__).resolve().parent.parent
CORPUS_PATH = ROOT / "data" / "knowledge" / "plot_corpus_wu_ming_zhe.json"
GRAPH_PATH = ROOT / "data" / "knowledge" / "plot_graph_wu_ming_zhe.json"
ALIAS_PATH = ROOT / "data" / "lore" / "wu_ming_zhe" / "plot_aliases.json"

# 用户原话（含口语包裹，长度不一，用来验证"实体查询"判定不依赖精确措辞）
DIALOGUE = [
    "纸信圈儿",
    "牙仙",
    "你还记得诺谛卡吗？",
    "芭卡洛儿你还记的吗？",
    "维尔汀",
    "十四行诗",
    "阿尔卡纳",
]

# 跨语种桥接的硬期望：这些中文名的证据在英文 ASR 里，必须命中对应写法。
# （不是全部 7 句都写死——其余用检索器自判的可信名，避免把设计当成答案抄进来）
HARD_EXPECT = {
    "牙仙": ["tooth fairy"],          # 人工表 P0 新增条目
    "纸信圈儿": ["flutter page", "flutterpage"],
    "你还记得诺谛卡吗？": ["nautica"],
    "芭卡洛儿你还记的吗？": ["barcarola", "baccarola"],
    "阿尔卡纳": ["arcana"],
}


@pytest.fixture(scope="module")
def live():
    if not (CORPUS_PATH.is_file() and GRAPH_PATH.is_file() and ALIAS_PATH.is_file()):
        pytest.skip("缺少真实剧情语料/图谱/别名表")
    retr = build_plot_registry().get("wu_ming_zhe")
    if retr is None or not retr.corpus.chunks:
        pytest.skip("剧情图谱未能加载")
    return retr


def _trusted_names_of_seeds(retr, query: str) -> set[str]:
    """该查询命中实体的全部可信名（用检索器自己的判定，避免硬编码清单）。"""
    names: set[str] = set()
    for eid in retr.seed_gate(retr.link_detailed(query)):
        ent = retr.store.get_entity(eid) or {}
        pool = [str(ent.get("name") or "")] + [
            str(a) for a in (ent.get("aliases") or [])
        ]
        names |= retr._trusted_names(eid, pool)
    return names


@pytest.mark.parametrize("query", DIALOGUE)
def test_dialogue_turn_injects_entity_evidence(live, query):
    """A1：注入提示词的前 2 块中，至少 1 块含该实体的可信名。"""
    retr = live
    chunks = retr.retrieve(query, top_chunks=3, lexical_fallback=2)
    assert chunks, f"{query!r} 零注入——剧情层没能给出任何证据"

    trusted = _trusted_names_of_seeds(retr, query)
    assert trusted, f"{query!r} 没有解析出任何实体种子"
    hit = any(any(n in c.text.lower() for n in trusted) for c in chunks[:2])
    assert hit, (
        f"{query!r} 的前 2 块不含该实体的可信名（可信 {len(trusted)} 个："
        f"{sorted(trusted)[:6]}）\n实际前 2 块：{[c.text[:70] for c in chunks[:2]]}"
    )


@pytest.mark.parametrize("query,expect", list(HARD_EXPECT.items()))
def test_dialogue_turn_cross_language_bridge(live, query, expect):
    """跨语种桥接硬期望（2026-09-20 修订）。

    原文断言「前 3 块必须含**英文写法**」——那是**英文 ASR 单语料时代**的要求：
    中文问句在语料里没有中文正文可命中，只能靠别名桥落到英文证据块。

    compendium 中文正典入库后（+5 226 块中文正文），中文问句可直接命中
    **中文正典块**（`**牙仙**：…`，比英文 ASR 更贴题）。此时死写英文写法，
    等于要求中文正典给英文 ASR 让位，与本层「中文查询 ↔ 中文正文」的建层
    目的相悖（见 plot_corpus.CANON_DIRNAME 的设计说明）。

    判据改为：前 3 块必须含该实体的**中文正名或英文写法之一**。
    可信名由检索器自己判定（复用 _trusted_names_of_seeds），不硬编码清单。
    """
    retr = live
    chunks = retr.retrieve(query, top_chunks=3, lexical_fallback=2)
    joined = " ".join(c.text.lower() for c in chunks[:3])
    trusted = _trusted_names_of_seeds(retr, query)
    ok = any(k in joined for k in expect) or any(n in joined for n in trusted)
    assert ok, (
        f"{query!r} 前 3 块既不含英文写法 {expect}，也不含该实体的可信名之一"
        f"（{sorted(trusted)[:6]}）：{[c.text[:60] for c in chunks[:3]]}"
    )


def test_dialogue_context_survives_prompt_gate(live):
    """注入链路（相对门 → 提示词渲染）不得把证据块丢掉。"""
    from roleplay.core.persona_prompt import _filter_chunks, build_plot_context

    retr = live
    for query in DIALOGUE:
        chunks = retr.retrieve(query, top_chunks=3, lexical_fallback=2)
        kept = _filter_chunks(chunks)
        assert len(kept) == len(chunks), f"{query!r} 被相对门砍掉 {len(chunks) - len(kept)} 块"
        ctx = build_plot_context(chunks, max_chars=1000)
        assert ctx and "【剧情记忆" in ctx, f"{query!r} 未渲染出剧情记忆块"
