"""内存向量库测试。"""
from roleplay.core.rag.memory import InMemoryVectorStore


def test_search_ranks_relevant():
    vs = InMemoryVectorStore()
    vs.add(["猫喜欢睡觉", "狗喜欢跑步", "鱼生活在水里"])
    res = vs.search("猫", top_k=1)
    assert res and "猫" in res[0].text
    assert res[0].score > 0


def test_search_empty_when_no_match():
    vs = InMemoryVectorStore()
    assert vs.search("完全无关的词xyz") == []


def test_search_respects_top_k():
    vs = InMemoryVectorStore()
    vs.add(["苹果", "苹果派", "橙子", "香蕉"])
    res = vs.search("苹果", top_k=2)
    assert len(res) <= 2


def test_search_cjk_multi_char():
    # 中文需逐字切分；多字查询应命中含该短语的文档
    vs = InMemoryVectorStore()
    vs.add(["我喜欢在雨天散步，听雨声很放松", "工作压力大时可以深呼吸"])
    res = vs.search("雨天散步", top_k=1)
    assert res and "雨天散步" in res[0].text
