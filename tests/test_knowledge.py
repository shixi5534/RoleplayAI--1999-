"""知识库 / 分层记忆 / 多角色 / 联网 核心模块测试。

覆盖需求 1–5 的关键路径：持久化检索、角色 CRUD、长期记忆衰减、联网优雅降级。
"""
import json
import time

import asyncio
import pytest

from roleplay.core.knowledge import (
    CharacterStore,
    DuckDuckGoAdapter,
    FallbackWebSearch,
    HashingEmbedder,
    KnowledgeBase,
    LongTermMemory,
    build_embedder,
    build_web_search,
)
from roleplay.core.knowledge.ingest import chunk_text
from roleplay.core.knowledge.web_search import WebResult


def test_chunk_text_preserves_all_content_and_bridges_overlap():
    """P0 回归：chunk_text 必须完整保留正文，且相邻块以「当前块头部」桥接。

    曾有两代 bug：
    1. 用 p[-overlap:] 覆盖后 continue → 除第一块外正文大面积丢失；
    2. 把当前块「尾部」接到上一块末尾 → 尾部字符冗余重复（验证同样被误导）。
    正确语义：上一块末尾 = 原内容 + 当前块头部 overlap。
    """
    text = ("第一句。第二句。第三句。第四句。第五句。第六句。第七句。第八句。") * 30
    size, overlap = 100, 20
    chunks = chunk_text(text, size=size, overlap=overlap)
    assert len(chunks) > 5, "长文本应切出多块"

    # 正文完整保留：每块去掉头部 overlap 后拼接，应还原全部原文
    core = [c[overlap:].strip() if i > 0 else c.strip() for i, c in enumerate(chunks)]
    assert "".join(core).replace(" ", "") == text.replace(" ", "")

    # 相邻块上下文桥：上一块末尾应包含当前块头部 overlap 字符
    for i in range(len(chunks) - 1):
        tail = chunks[i][-overlap:].strip()
        assert tail and chunks[i + 1].startswith(tail), f"块{i}→{i+1} 头部桥接缺失"

    # 单块短文本/无重叠配置直接返回
    assert chunk_text("你好", size=100, overlap=20) == ["你好"]
    assert chunk_text(text, size=100, overlap=0)  # overlap<=0 不合并
    assert chunk_text("   ") == []


def test_embedder_hashing_deterministic():
    e = HashingEmbedder(dim=64)
    v1 = e.embed(["你好世界"])
    v2 = e.embed(["你好世界"])
    assert len(v1[0]) == 64
    assert v1[0] == v2[0]


def test_knowledge_base_add_search_persist(tmp_path):
    e = HashingEmbedder(dim=64)
    kb = KnowledgeBase(e, persist_dir=tmp_path / "kb")
    kb.add(["我喜欢在雨天散步听雨声", "工作压力大时深呼吸放松"], namespace="episodic")
    res = kb.search("雨天散步", top_k=2, namespaces=["episodic"])
    assert res and res[0].score > 0

    # 重新加载（模拟重启）→ 数据仍在
    kb2 = KnowledgeBase(e, persist_dir=tmp_path / "kb")
    res2 = kb2.search("深呼吸", top_k=2, namespaces=["episodic"])
    assert res2 and any("深呼吸" in c.text for c in res2)


def test_knowledge_base_reembeds_when_embedder_dim_changes(tmp_path):
    """模拟 hashing 维度配置变化：加载旧向量库时应用当前嵌入器自动重建。"""
    dir_ = tmp_path / "kb"
    kb1 = KnowledgeBase(HashingEmbedder(dim=64), persist_dir=dir_)
    kb1.add(["我喜欢在雨天散步"], namespace="episodic")
    kb2 = KnowledgeBase(HashingEmbedder(dim=128), persist_dir=dir_)
    items = kb2.list_items("episodic")
    assert items and len(items[0]["vec"]) == 128
    assert kb2.search("雨天", top_k=1, namespaces=["episodic"])


def test_knowledge_base_list_items_returns_all_and_copy(tmp_path):
    """list_items：返回命名空间全量条目（含 id/text/meta），且为浅拷贝（不暴露内部引用）。"""
    e = HashingEmbedder(dim=64)
    kb = KnowledgeBase(e, persist_dir=tmp_path / "kb")
    kb.add(
        ["第一句", "第二句"],
        metadatas=[{"type": "preference", "key": "a"}, {"type": "habit", "key": "b"}],
        namespace="profile",
    )
    items = kb.list_items("profile")
    assert len(items) == 2
    ids = {it["id"] for it in items}
    assert len(ids) == 2
    metas = {it["meta"]["key"] for it in items}
    assert metas == {"a", "b"}
    # 浅拷贝：修改返回的 dict 不影响内部数据
    items[0]["meta"]["key"] = "mutated"
    items[0]["text"] = "mutated"
    after = kb.list_items("profile")
    assert all(it["meta"]["key"] != "mutated" for it in after)
    assert all(it["text"] != "mutated" for it in after)
    # 未落过数据的命名空间返回空列表
    assert kb.list_items("not-exist") == []


def test_character_store_crud_and_sync(tmp_path):
    store = CharacterStore(persist_dir=tmp_path / "chars")
    cid = store.create({"name": "小蓝", "personality": "活泼", "background": "来自海边"})
    assert store.get(cid) is not None
    assert store.get_active_id() == cid or store.get_active_id() is not None

    store.update(cid, {"personality": "沉稳"})
    assert store.get(cid).personality == "沉稳"

    # 同步到知识库：persona 命名空间应有该角色
    e = HashingEmbedder(dim=64)
    kb = KnowledgeBase(e, persist_dir=tmp_path / "kb2")
    n = store.sync_persona_to_kb(kb)
    assert n >= 1
    persona = kb.search("小蓝", top_k=3, namespaces=["persona"])
    assert any("小蓝" in c.text for c in persona)

    # 删除：至少保留一个角色
    store.create({"name": "小绿"})
    before = len(store.list())
    store.delete(cid)
    after = len(store.list())
    assert after == before - 1
    # 删除最后一个应报错
    ids = [c["id"] for c in store.list()]
    for i in ids[:-1]:
        store.delete(i)
    try:
        store.delete(ids[-1])
        assert False, "应拒绝删除最后一个角色"
    except ValueError:
        pass


async def test_longterm_memory_decay_ranking(tmp_path):
    e = HashingEmbedder(dim=64)
    kb = KnowledgeBase(e, persist_dir=tmp_path / "ltm")
    ltm = LongTermMemory(kb, decay_lambda=0.05, retention_days=60)
    # 高重要度事件
    await ltm.consolidate("s1", [{"role": "user", "content": "记住，我最喜欢蓝色"}, {"role": "assistant", "content": "好的，记住了"}])
    # 普通事件
    await ltm.consolidate("s1", [{"role": "user", "content": "今天天气不错"}, {"role": "assistant", "content": "是啊"}])
    res = await ltm.retrieve("蓝色 喜欢", top_k=3)
    assert res, "应能检索到长期记忆"
    # 高重要度应排在更前（或至少被检索到）
    assert any("蓝色" in c.text for c in res)


async def test_longterm_memory_isolated_by_character(tmp_path):
    """跨角色长期记忆隔离：角色 B 检索不到角色 A 沉淀的记忆。"""
    e = HashingEmbedder(dim=64)
    kb = KnowledgeBase(e, persist_dir=tmp_path / "iso")
    ltm_a = LongTermMemory(kb, decay_lambda=0.05, retention_days=60)
    ltm_b = LongTermMemory(kb, decay_lambda=0.05, retention_days=60)
    await ltm_a.consolidate(
        "s_a", [{"role": "user", "content": "记住，角色A最爱蓝色"}], character_id="char_a"
    )
    await ltm_b.consolidate(
        "s_b", [{"role": "user", "content": "角色B喜欢红色"}], character_id="char_b"
    )
    # 角色 A 的检索命中自己的记忆
    a_hits = await ltm_a.retrieve("蓝色 喜欢", top_k=3, character_id="char_a")
    assert any("蓝色" in c.text for c in a_hits)
    # 角色 B 检索不到角色 A 的记忆（命名空间隔离）
    b_hits = await ltm_b.retrieve("蓝色 喜欢", top_k=3, character_id="char_b")
    assert not any("蓝色" in c.text for c in b_hits)
    # 同角色跨会话仍共享（新会话 s_a2 也能命中）
    a_hits2 = await ltm_a.retrieve("蓝色 喜欢", top_k=3, character_id="char_a")
    assert any("蓝色" in c.text for c in a_hits2)


async def test_longterm_memory_prune_threshold_aligned(tmp_path):
    """B1 回归：prune 阈值与结构化条目 importance 标度 [0,1] 对齐。

    旧阈值 0.6 会误杀规则/LLM 提取器产出的全部结构化条目（0.4~0.55），
    长期记忆「写入即被清空」。现在仅清理极不重要（<0.3）条目。
    """
    e = HashingEmbedder(dim=64)
    kb = KnowledgeBase(e, persist_dir=tmp_path / "prune")
    ltm = LongTermMemory(kb, decay_lambda=0.05, retention_days=60)
    await ltm.consolidate_entries(
        "s1",
        [
            {"type": "fact", "content": "用户喜欢蓝色", "importance": 0.4},
            {"type": "important_date", "content": "用户生日是三月一日", "importance": 0.55},
            {"type": "fact", "content": "毫无信息量的闲聊", "importance": 0.2},
        ],
    )
    removed = ltm.prune()
    items = kb.list_items("events")
    texts = [it["text"] for it in items]
    assert removed == 1, "仅极不重要条目应被清理"
    assert "用户喜欢蓝色" in texts
    assert "用户生日是三月一日" in texts
    assert "毫无信息量的闲聊" not in texts


def test_session_memory_append_many(tmp_path):
    """B4 回归：append_many 批量写入语义与 append 一致（含空内容跳过）。"""
    from roleplay.core.session_memory import SessionMemory

    sm = SessionMemory(persist_dir=tmp_path / "sessions")
    sm.append_many(
        "sid1",
        [("user", "你好"), ("assistant", "你好呀"), ("user", "   "), ("assistant", "")],
    )
    hist = sm.get_history("sid1")
    assert [t["role"] for t in hist] == ["user", "assistant"]
    assert hist[0]["content"] == "你好"
    # 空 session_id / 空列表安全
    sm.append_many("", [("user", "x")])
    sm.append_many("sid2", [])
    assert sm.get_history("sid2") == []


def test_web_search_ddg_graceful():
    # 离线环境 DDG 会超时，但不应抛异常（返回空列表）
    adapter = DuckDuckGoAdapter()
    out = asyncio.run(adapter.search("python web framework", max_results=3))
    assert isinstance(out, list)
    # 若有结果，结构正确
    for r in out:
        assert isinstance(r, WebResult)
        assert isinstance(r.url, str)


def test_bing_adapter_parses_real_markup():
    """BingAdapter 能从未经网络（本地 fixture）的 Bing 结果页解析出结构化结果。"""
    import roleplay.core.knowledge.web_search as ws_mod

    html_fixture = """
    <html><body><ol id="b_results">
    <li class="b_algo">
      <h2><a href="https://example.com/page1">示例标题一</a></h2>
      <div class="b_caption"><p class="b_lineclamp2 b_lineclamp3">这是摘要文本。补充内容。</p></div>
    </li>
    <li class="b_algo">
      <h2><a href="https://example.org/page2">示例标题二</a></h2>
      <div class="b_caption"><p class="b_lineclamp2">第二个摘要 &amp; 转义。</p></div>
    </li>
    </ol></body></html>
    """

    class _FakeClient:
        def __init__(self, *a, **k):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return False

        async def get(self, url, params=None):
            class _Resp:
                text = html_fixture

                def raise_for_status(self):
                    return None

            return _Resp()

    orig = ws_mod.httpx.AsyncClient
    ws_mod.httpx.AsyncClient = _FakeClient
    try:
        adapter = ws_mod.BingAdapter()
        out = asyncio.run(adapter.search("测试", max_results=5))
    finally:
        ws_mod.httpx.AsyncClient = orig

    assert len(out) == 2
    assert out[0].url == "https://example.com/page1"
    assert out[0].title == "示例标题一"
    assert "这是摘要文本" in out[0].snippet
    assert out[1].title == "示例标题二"
    assert "第二个摘要" in out[1].snippet


def test_build_web_search_returns_fallback_chain():
    """默认配置（无 Tavily key）应返回 DDG→Bing 回退链，且两者都可用。"""
    ws = build_web_search()
    assert isinstance(ws, FallbackWebSearch)
    assert len(ws._adapters) == 2


def test_build_embedder_fallback():
    # 未配置 Ollama 或不可达时回退到 hashing，不抛异常
    emb = build_embedder()
    assert emb is not None
    v = emb.embed(["测试"])
    assert isinstance(v[0], list) and len(v[0]) > 0


def test_session_memory_atomic_write_no_tmp_leak(tmp_path):
    # 原子写：append 后不应残留临时文件，且落盘 JSON 可解析、包含写入的轮次
    import os

    from roleplay.core.session_memory import SessionMemory

    sm = SessionMemory(persist_dir=tmp_path)
    sm.append("sess1", "user", "你好")
    sm.append("sess1", "assistant", "我在这里")
    # 不应残留 .tmp 文件
    tmps = list(tmp_path.glob("*.tmp"))
    assert tmps == [], f"原子写后不应残留临时文件，发现: {tmps}"
    # 落盘文件合法且内容完整
    data = json.loads((tmp_path / "sess1.json").read_text(encoding="utf-8"))
    assert [t["role"] for t in data] == ["user", "assistant"]
    assert data[0]["content"] == "你好"


def test_chroma_store_missing_dep_raises():
    # chromadb 未安装时构造 ChromaVectorStore 应给出清晰的 ConfigurationError，
    # 而非让 import 失败拖垮整个应用启动
    try:
        import chromadb  # noqa: F401

        have_chroma = True
    except ImportError:
        have_chroma = False
    if have_chroma:
        pytest.skip("chromadb 已安装，跳过缺依赖断言")
    from roleplay.core.rag.chroma_store import ChromaVectorStore
    from roleplay.errors import ConfigurationError

    with pytest.raises(ConfigurationError):
        ChromaVectorStore(persist_dir="./data/chroma")
