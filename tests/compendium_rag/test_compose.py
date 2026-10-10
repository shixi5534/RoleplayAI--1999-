# -*- coding: utf-8 -*-
"""P4 作答通路的**离线**测试：装配契约 + 文本模式传输。

全部不需要网络：``CloudLLM`` 的 httpx 客户端在进入上下文后被换成
``httpx.MockTransport``（同 ``test_llm_parse.py`` 的假 HTTP 思路）。
"""
from __future__ import annotations

import asyncio
import json

import httpx
import pytest

from compendium_rag.compose import (ANSWER_SYSTEM_PROMPT, CONTEXT_EMPTY_NOTICE,
                                    answer, compose, render_prompt,
                                    render_role_card)
from compendium_rag.graph_store import Entity
from compendium_rag.llm import CloudLLM, LLMError, LLMResult

CTX = ("【原文证据】\n"
       "[S1 chunk=c1 doc=d cat=mainline] [第一章] 维尔汀持有一枚怀表。\n\n"
       "[S2 chunk=c2 doc=d cat=character] [第二章] 怀表的来历未在片段中说明。")


def _content(messages: list[dict]) -> str:
    return "\n".join(str(m.get("content") or "") for m in messages)


async def _with_mock(handler, coro_factory):
    """把 CloudLLM 的 httpx 客户端换成 MockTransport 后执行用例（零网络）。"""
    client = CloudLLM(base_url="http://mock.local/v1", api_key="k", model="m",
                      concurrency=1, max_retries=2, temperature=0.0)
    async with client:
        await client._client.aclose()
        client._client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        try:
            return await coro_factory(client)
        finally:
            await client._client.aclose()
            client._client = None


def _ok_response(content: str, finish: str = "stop", *, usage=None):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={
            "model": "mock-model",
            "choices": [{"message": {"role": "assistant", "content": content},
                         "finish_reason": finish}],
            "usage": usage or {"prompt_tokens": 11, "completion_tokens": 7},
        })
    return handler


# ── 系统提示：三条硬规则 ──

def test_system_prompt_states_three_hard_rules():
    """三条硬规则必须在提示词里逐条可检：编号引用 / 未记载 / 禁外部知识。

    这不是文风要求，而是评测前提：规则缺失时 L3.4（幻觉）与 L3.3（faithfulness）
    测的就不再是同一个东西了。
    """
    p = ANSWER_SYSTEM_PROMPT
    assert "只准引用带编号片段" in p
    assert "[S1]" in p and "[S2]" in p          # 编号引用形态要给出例子
    assert "未记载" in p
    assert "不得引入外部游戏知识" in p
    # 先验知识必须被显式点名，否则「我知道所以我答」没有可判定的边界
    assert "先验知识" in p


def test_system_prompt_forbids_uncited_statement():
    """规则 1 必须同时禁掉「没有编号的陈述」，而不只是禁造编号。"""
    assert "不得把多个片段的内容混成一条没有编号的陈述" in ANSWER_SYSTEM_PROMPT


# ── compose 装配 ──

def test_compose_message_shape_and_order():
    msgs = compose("维尔汀持有什么？", CTX)
    assert [m["role"] for m in msgs] == ["system", "user"]
    assert msgs[0]["content"].startswith(ANSWER_SYSTEM_PROMPT)
    user = msgs[-1]["content"]
    assert "【检索片段】" in user and "【问题】" in user
    assert user.index("【检索片段】") < user.index("【问题】")
    assert "维尔汀持有什么？" in user


def test_compose_context_passed_through_verbatim():
    """片段**逐字**透传：编号与顺序是本模块不能碰的部分。

    编号一旦在这里被重排/重编号，「引用 S2」就回查不到窗口第 2 块，
    审查端无法逐条对账（契约见 tests/compendium_rag/test_retriever.py::
    test_context_tags_evidence_with_citable_provenance）。
    """
    user = compose("q", CTX)[-1]["content"]
    assert CTX in user
    assert user.index("[S1 ") < user.index("[S2 ")


def test_compose_is_deterministic():
    a = compose("q", CTX, role_card="名字：维尔汀", history=[("user", "hi")])
    b = compose("q", CTX, role_card="名字：维尔汀", history=[("user", "hi")])
    assert a == b


def test_compose_empty_context_does_not_crash():
    """空 context 必须能装配，且**显式**告诉模型这次是空的（不静默省略整段）。"""
    msgs = compose("q", "")
    assert [m["role"] for m in msgs] == ["system", "user"]
    assert CONTEXT_EMPTY_NOTICE in msgs[-1]["content"]


def test_compose_none_context_does_not_crash():
    msgs = compose("q", None)  # type: ignore[arg-type]
    assert CONTEXT_EMPTY_NOTICE in msgs[-1]["content"]


def test_compose_empty_query_does_not_crash():
    msgs = compose("", CTX)
    assert "【问题】" in msgs[-1]["content"]


def test_compose_without_role_card_omits_section():
    sys_msg = compose("q", CTX)[0]["content"]
    assert "【角色卡】" not in sys_msg


def test_compose_with_role_card_appends_section():
    sys_msg = compose("q", CTX, role_card="名字：维尔汀\n类型：角色")[0]["content"]
    assert "【角色卡】" in sys_msg
    assert sys_msg.index(ANSWER_SYSTEM_PROMPT) < sys_msg.index("【角色卡】")
    assert "名字：维尔汀" in sys_msg


def test_compose_history_preserved_and_ordered():
    hist = [{"role": "user", "content": "第一问"},
            {"role": "assistant", "content": "第一答"}]
    msgs = compose("第二问", CTX, history=hist)
    assert [m["role"] for m in msgs] == ["system", "user", "assistant", "user"]
    assert msgs[1]["content"] == "第一问"
    assert msgs[2]["content"] == "第一答"
    # 证据+问题固定在**末条 user**，历史之后
    assert CTX in msgs[-1]["content"]


def test_compose_empty_history_behaves_like_no_history():
    assert compose("q", CTX, history=[]) == compose("q", CTX, history=None)


def test_compose_history_skips_unusable_items():
    """取不到 role/content 的项直接跳过，不许把 None 塞进 messages。"""
    msgs = compose("q", CTX, history=[{"content": "无角色"}, ("user", "有效"), None])
    assert [m["role"] for m in msgs] == ["system", "user", "user"]
    assert msgs[1]["content"] == "有效"


def test_compose_history_accepts_object_items():
    class _Turn:
        def __init__(self, role, content):
            self.role, self.content = role, content

    msgs = compose("q", CTX, history=[_Turn("user", "对象轮次")])
    assert msgs[1] == {"role": "user", "content": "对象轮次"}


# ── 角色卡渲染 ──

def test_render_role_card_with_full_entity():
    ent = Entity(eid="e1", name="维尔汀", type="角色",
                 aliases=["Vertin", "司辰"], desc="圣洛夫基金会的司辰。")
    card = render_role_card(ent)
    assert "名字：维尔汀" in card
    assert "类型：角色" in card
    assert "别名：Vertin、司辰" in card
    assert "简介：圣洛夫基金会的司辰。" in card


def test_render_role_card_without_desc_or_aliases_omits_labels():
    card = render_role_card(Entity(eid="e1", name="柏林以东", type="角色"))
    assert card == "名字：柏林以东\n类型：角色"
    assert "别名" not in card and "简介" not in card


def test_render_role_card_without_name_returns_empty():
    """没有资料就返回空串——**绝不编造**人设（宁可没有角色卡）。"""
    assert render_role_card(None) == ""
    assert render_role_card({}) == ""
    assert render_role_card({"desc": "只有简介没有名字"}) == ""
    assert render_role_card(Entity(eid="e1", name="   ")) == ""


def test_render_role_card_accepts_mapping():
    card = render_role_card({"name": "十四行诗", "type": "物品",
                             "aliases": ["Sonetto"], "desc": "诗册。"})
    assert "名字：十四行诗" in card and "别名：Sonetto" in card


def test_compose_accepts_rendered_role_card_in_system_only():
    """角色卡只进 system，绝不混进证据段（否则会与 [S{i}] 抢引用权）。"""
    card = render_role_card(Entity(eid="e1", name="维尔汀", type="角色"))
    msgs = compose("q", CTX, role_card=card)
    assert "名字：维尔汀" in msgs[0]["content"]
    assert "名字：维尔汀" not in msgs[-1]["content"]


# ── complete_text：文本模式传输 ──

def test_complete_text_returns_text_without_json_parse():
    """文本模式不得解析 JSON：答案原样返回，即使它**恰好**是 JSON。"""
    raw = '{"这不是信封": "而是答案文本"}'

    async def run(client):
        return await client.complete_text([{"role": "user", "content": "q"}])

    text, meta = asyncio.run(_with_mock(_ok_response(raw), run))
    assert text == raw                      # 逐字返回，没有被 parse_json_loose 改写
    assert isinstance(meta, LLMResult)
    assert isinstance(meta.text, str)       # 不是 dict
    assert meta.model == "mock-model"
    assert meta.prompt_tokens == 11 and meta.completion_tokens == 7


def test_complete_text_sends_no_response_format():
    """文本模式不能带 response_format（带了等于要求网关返回 JSON 对象）。"""
    seen: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen.update(json.loads(request.content.decode("utf-8")))
        return httpx.Response(200, json={
            "model": "mock-model",
            "choices": [{"message": {"content": "答案"}, "finish_reason": "stop"}],
        })

    async def run(client):
        return await client.complete_text([{"role": "user", "content": "q"}])

    asyncio.run(_with_mock(handler, run))
    assert "response_format" not in seen
    assert seen["messages"] == [{"role": "user", "content": "q"}]


def test_complete_text_legacy_two_arg_form():
    """``complete_text(system, user)`` 旧式两参写法照样可用。"""
    seen: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen.update(json.loads(request.content.decode("utf-8")))
        return httpx.Response(200, json={
            "model": "mock-model",
            "choices": [{"message": {"content": "答案"}, "finish_reason": "stop"}],
        })

    async def run(client):
        return await client.complete_text("系统", "用户")

    text, _ = asyncio.run(_with_mock(handler, run))
    assert text == "答案"
    assert seen["messages"] == [{"role": "system", "content": "系统"},
                                {"role": "user", "content": "用户"}]


def test_complete_text_accepts_truncated_answer():
    """``finish=length`` 的截断答案照常返回（由调用方看 meta 处置），不许静默丢弃。"""
    async def run(client):
        return await client.complete_text([{"role": "user", "content": "q"}])

    text, meta = asyncio.run(_with_mock(_ok_response("半句答案", "length"), run))
    assert text == "半句答案"
    assert meta.finish_reason == "length"


def test_complete_text_retries_empty_content():
    """空 content 是实测过的推理模型故障，必须重试而不是返回空串。"""
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        content = "" if calls["n"] == 1 else "第二次有内容"
        return httpx.Response(200, json={
            "model": "mock-model",
            "choices": [{"message": {"content": content}, "finish_reason": "stop"}],
        })

    async def run(client):
        client._backoff = _no_sleep
        return await client.complete_text([{"role": "user", "content": "q"}])

    text, meta = asyncio.run(_with_mock(handler, run))
    assert text == "第二次有内容"
    assert calls["n"] == 2
    assert meta.attempts == 2


def test_complete_text_raises_on_persistent_empty():
    """重试耗尽后必须抛错，不许返回空串（与 complete_json 同口径）。"""
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={
            "model": "mock-model",
            "choices": [{"message": {"content": "", "finish_reason": "stop"}}],
        })

    async def run(client):
        client._backoff = _no_sleep
        with pytest.raises(LLMError) as ei:
            await client.complete_text([{"role": "user", "content": "q"}])
        assert "content 为空" in str(ei.value)

    asyncio.run(_with_mock(handler, run))


async def _no_sleep(attempt, why):
    """替掉指数退避：用例不该真睡 1.5^n 秒。"""
    return None


# ── answer 端到端（假 HTTP）──

def test_answer_end_to_end_via_mock_transport():
    seen: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen.update(json.loads(request.content.decode("utf-8")))
        return httpx.Response(200, json={
            "model": "mock-model",
            "choices": [{"message": {"content": "维尔汀持有一枚怀表。[S1]"},
                         "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 100, "completion_tokens": 20},
        })

    async def run(client):
        return await answer(client, "维尔汀持有什么？", CTX,
                            role_card="名字：维尔汀", max_tokens=256)

    text, meta = asyncio.run(_with_mock(handler, run))
    assert text == "维尔汀持有一枚怀表。[S1]"
    assert meta.prompt_tokens == 100
    # 装配确实走到了线上：system 含硬规则，末条 user 含片段与问题
    sent = seen["messages"]
    assert sent[0]["role"] == "system"
    assert "未记载" in sent[0]["content"]
    assert CTX in sent[-1]["content"] and "维尔汀持有什么？" in sent[-1]["content"]
    assert seen["max_tokens"] == 256


def test_answer_with_fake_llm_client():
    """鸭子类型的假 LLM：answer 只依赖 ``complete_text(messages, max_tokens)``。"""
    class _Fake:
        def __init__(self):
            self.messages = None

        async def complete_text(self, messages, max_tokens=None):
            self.messages = messages
            return "未记载。[S1]", LLMResult(text="未记载。[S1]", model="fake")

    fake = _Fake()
    text, meta = asyncio.run(answer(fake, "q", CTX))
    assert text == "未记载。[S1]"
    assert meta.model == "fake"
    assert fake.messages[-1]["role"] == "user"


def test_answer_with_empty_context_still_calls_model():
    class _Fake:
        async def complete_text(self, messages, max_tokens=None):
            assert CONTEXT_EMPTY_NOTICE in messages[-1]["content"]
            return "未记载", LLMResult(text="未记载", model="fake")

    text, _ = asyncio.run(answer(_Fake(), "q", ""))
    assert text == "未记载"


# ── render_prompt：子代理批次用的单串投影（P4.2 双盲复测靠它同源）──

def test_render_prompt_is_compose_flattened():
    """投影必须与 ``compose`` 逐字同源：只是把 messages 摊平，不重写内容。"""
    msgs = compose("问题？", CTX, role_card="名字：维尔汀",
                   history=[{"role": "user", "content": "上一轮"}])
    flat = render_prompt("问题？", CTX, role_card="名字：维尔汀",
                         history=[{"role": "user", "content": "上一轮"}])
    expected = "\n\n".join(f"## {m['role']}\n{m['content']}" for m in msgs)
    assert flat == expected
    # 逐段可切回来，且片段与问题都在末段
    assert flat.count("## system") == 1
    assert flat.count("## user") == 2
    assert CTX in flat and "问题？" in flat
    assert flat.rstrip().endswith("问题？")


def test_render_prompt_without_history_is_blank_history():
    """双盲复测传 ``history=None``：不得凭空多出轮次。"""
    flat = render_prompt("q", CTX)
    assert flat == f"## system\n{ANSWER_SYSTEM_PROMPT}\n\n## user\n{compose('q', CTX)[-1]['content']}"
    assert flat.count("## ") == 2


def test_render_prompt_empty_context_keeps_notice():
    assert CONTEXT_EMPTY_NOTICE in render_prompt("q", "")


# ── 包级导出：调用方（脚本/子代理）从 compendium_rag 直接取 ──

def test_public_exports_are_reachable_from_package_root():
    import compendium_rag as pkg

    for name in ("ANSWER_SYSTEM_PROMPT", "compose", "answer", "render_role_card",
                 "render_prompt"):
        assert name in pkg.__all__, f"{name} 未导出"
        assert getattr(pkg, name) is not None
