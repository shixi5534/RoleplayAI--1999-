# -*- coding: utf-8 -*-
"""R3 护栏加固的回归测试（负样本 10→57 扩充后暴露的两类真实缺陷）。

背景（本轮最重要的发现）
    把负样本从 10 条扩到 57 条后，原本"全绿"的护栏立刻失守 15 条——
    **10 条样本从未覆盖到这些问法**。这正是 Spec 反复强调的那句话：
    「阈值标定需要样本量，样本太少的阈值不是标定，是拍脑袋」。

本轮修掉的两类（各自零代价，见下）
    A. **问候/感叹 + 抽象泛化名词**被 ASR 抽成实体（``Buona sera`` / ``gracias`` /
       ``Haha`` / 事件 / 模型 / 意识 / 复仇），靠精确匹配点火。
    B. **代词/敬称/填充词作为别名**：``me``→Shamane、``I``→Calabona。
       ``is_noise_entity`` 只在**建图时对正名**生效，**别名完全绕过**——
       后果是「tell me a joke」这类任意英文句子都能点火。
       （这正是审计报告「建图只过滤正名、不过滤别名」那个洞的检索侧出口。）

尚未修复、且有明确路径的残余（**如实记录，不得假装通过**）
    ``苹果公司的 CEO 是谁`` / ``巴黎在哪个国家`` / ``who is the president...`` 等 5 条：
    种子 ``苹果``(度 2) / ``Paris``(度 31) / ``President``(度 6) 都是**作品内真实实体**，
    仅凭结构判据无法与"离题引用"区分——必须靠 B3（reranker 安全间隔）的语义相关度。
    两条被数据否决的粗暴修法已记录在案：
      ① 要求"至少一个锚定种子" → 会短路 **111/300** 正样本（正是别名桥缺失主战场）；
      ② 孤立实体（度 0）不做种子 → 会短路 **23/288**（滚鳄书店/菲林士多/Nuku Teow 等
         真实体只是零度节点）。
"""
from __future__ import annotations

import pytest

from roleplay.core.knowledge.graph_store import GraphStore
from roleplay.core.knowledge.plot_corpus import PlotCorpus
from roleplay.core.knowledge.plot_graph import (
    GENERIC_SEED_NAMES,
    PlotGraphRetriever,
    is_generic_seed_name,
    is_pronoun_or_filler,
)


class TestPronounOrFiller:
    @pytest.mark.parametrize("name", [
        "me", "I", "i", "you", "she", "he", "they", "it", "my", "your", "his",
        "this", "that", "who", "what",
    ])
    def test_pronouns_rejected(self, name):
        assert is_pronoun_or_filler(name) is True

    @pytest.mark.parametrize("name", [
        "ma'am", "sir", "madam", "miss", "okay", "alright", "sorry", "please",
        "thank you", "everyone", "somebody", "truly",
    ])
    def test_honorifics_and_fillers_rejected(self, name):
        assert is_pronoun_or_filler(name) is True

    @pytest.mark.parametrize("name", [
        "Shamane", "Calabona", "牙仙", "露西", "Nuku Teow", "菲林士多", "J",
    ])
    def test_real_names_pass(self, name):
        """真实体名与**单字母别名 J** 必须放行——后者是人工表刻意允许的。

        这条是本函数不能直接复用 is_noise_entity 的原因：后者含「长度<2 即噪声」，
        套到别名上会误杀 ``Jay: ["J"]``。
        """
        assert is_pronoun_or_filler(name) is False

    def test_single_letter_not_rejected_here(self):
        assert is_pronoun_or_filler("J") is False
        assert is_pronoun_or_filler("Z") is False


class TestLinkGating:
    def _retr(self, tmp_path, aliases):
        store = GraphStore(tmp_path / "g.json", min_confidence=0.5)
        store.upsert_entities([{"name": "Shamane", "aliases": aliases}])
        eid = store.link_exact("Shamane")
        store.upsert_entities([{"name": "另一个人"}])
        other = store.link_exact("另一个人")
        store.upsert_edge(src=eid, dst=other, relation="关联", confidence=0.9)
        corpus = PlotCorpus(tmp_path / "c.json", character_id="x")
        corpus.chunks = []
        return PlotGraphRetriever(corpus, store, min_confidence=0.5, include_weak=True)

    def test_pronoun_alias_does_not_link(self, tmp_path):
        """``me`` 作为别名不得把实体链接出来——旧实现会让任意英文句子点火。"""
        r = self._retr(tmp_path, ["me", "鬃毛沙砾"])
        assert r.link_detailed("tell me a joke") == {}, \
            "代词别名仍然能链接（任意英文句子都会命中）"
        # 真实别名仍须可用（info["name"] 是**命中的那个别名**，不是正名）
        hit = r.link_detailed("鬃毛沙砾是谁")
        assert "鬃毛沙砾" in [v["name"] for v in hit.values()], "真实别名被误杀"

    def test_single_letter_alias_still_links(self, tmp_path):
        """人工表刻意允许的单字母别名不能被这道门误杀。"""
        store = GraphStore(tmp_path / "g.json", min_confidence=0.5)
        store.upsert_entities([{"name": "Jay", "aliases": ["J", "Joe Brown"]}])
        corpus = PlotCorpus(tmp_path / "c.json", character_id="x")
        corpus.chunks = []
        r = PlotGraphRetriever(corpus, store, min_confidence=0.5, include_weak=True)
        # info["name"] 存的是**归一化**后命中名（小写），比较时统一 lower
        assert "j" in [v["name"].lower() for v in r.link_detailed("J 的义妹是谁").values()]

    def test_entity_fully_pruned_still_linkable_by_canonical(self, tmp_path):
        """别名全被拒时兜底保留正名，实体不会彻底失联。"""
        r = self._retr(tmp_path, ["me", "you"])
        assert "shamane" in [v["name"].lower() for v in r.link_detailed("Shamane").values()]


class TestGenericLexiconExpansion:
    @pytest.mark.parametrize("name", [
        # ② 问候/感叹（命中别名形态）
        "谢谢", "晚安", "哈哈", "thanks", "sorry", "please",
        # ③ 抽象泛化名词（中文命中别名形态 + 英文命中正名形态都要覆盖）
        "事件", "模型", "意识", "复仇", "公司", "国家",
        "incident", "consciousness", "president", "model", "event",
    ])
    def test_new_categories_present(self, name):
        assert is_generic_seed_name(name) is True, f"{name} 未被泛词表覆盖"

    @pytest.mark.parametrize("name", ["牙仙", "星锑", "洞穴", "十字街", "灯塔", "钥匙"])
    def test_plot_words_still_pass(self, name):
        """作品内词不得被误收——扩充后 300 题严格通过率必须零变化（已实测）。"""
        assert is_generic_seed_name(name) is False

    def test_lexicon_is_category_organised(self):
        """词表必须成规模且有分类注释（防止后人零散打补丁）。"""
        assert len(GENERIC_SEED_NAMES) > 150
        src = __import__("inspect").getsource(
            __import__("roleplay.core.knowledge.plot_graph", fromlist=["x"])
        )
        for marker in ("问候", "抽象泛化名词"):
            assert marker in src, f"泛词表缺少分类注释：{marker}"


class TestNegativeCaseSetShape:
    def test_negative_set_has_57_cases_in_8_categories(self):
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
        from eval_plot_rag import NEGATIVE_CASES, NEGATIVE_QUERIES
        assert len(NEGATIVE_CASES) >= 50, "Spec 要求负样本扩到 50+（AC-3 阈值标定前提）"
        assert len(NEGATIVE_QUERIES) == len(NEGATIVE_CASES)
        cats = {c for c, _q in NEGATIVE_CASES}
        assert len(cats) >= 6, f"分类过少，失守后无法定位成因：{cats}"
        assert len(set(NEGATIVE_QUERIES)) == len(NEGATIVE_QUERIES), "负样本不得重复"
