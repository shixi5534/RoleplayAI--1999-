# -*- coding: utf-8 -*-
"""云端 LLM 客户端的**离线**测试：JSON 容错解析与畸形输出收敛。

这里锁定的都是真实踩过的坑（见各用例 docstring），全部不需要网络。
"""
from __future__ import annotations

import json

import pytest

from compendium_rag.llm import (_coerce_envelope, _looks_like_entity,
                                _looks_like_relation, _repair, _scan_json_values,
                                parse_json_loose)


# ── 信封收敛（核心正确性）──

def test_bare_array_not_collapsed_to_first_element():
    """回归：裸数组曾被"第一个配平块"陷阱塌缩成单个实体。

    实测 `activity__20101_飞驰_明日之城:14.0.1` 因此从 12 实体变成 0 实体，
    且静默消耗 900 token。这条测试是该 bug 的守卫。
    """
    raw = json.dumps([
        {"name": "J", "type": "角色", "aliases": ["维恩"]},
        {"name": "玛蒂尔达", "type": "角色"},
        {"name": "使徒米修斯", "type": "角色"},
    ], ensure_ascii=False)
    got = parse_json_loose(raw)
    assert got is not None
    assert len(got["entities"]) == 3, "裸数组必须整体解析，不能只取第一个元素"
    assert {e["name"] for e in got["entities"]} == {"J", "玛蒂尔达", "使徒米修斯"}


def test_bare_array_with_relations_split():
    raw = json.dumps([
        {"name": "J", "type": "角色"},
        {"src": "J", "relation": "怀念", "dst": "保利娜", "confidence": 0.9},
    ], ensure_ascii=False)
    got = parse_json_loose(raw)
    assert len(got["entities"]) == 1
    assert len(got["relations"]) == 1
    assert got["relations"][0]["relation"] == "怀念"


def test_bare_single_entity_wrapped():
    got = parse_json_loose('{"name":"J","type":"角色","aliases":["维恩"]}')
    assert got is not None
    assert len(got["entities"]) == 1
    assert got["entities"][0]["name"] == "J"


def test_standard_envelope_passthrough():
    raw = ('{"entities":[{"name":"A","type":"角色"}],'
           '"relations":[{"src":"A","relation":"认识","dst":"B"}]}')
    got = parse_json_loose(raw)
    assert len(got["entities"]) == 1 and len(got["relations"]) == 1


def test_fenced_json():
    raw = '```json\n{"entities":[{"name":"A","type":"角色"}],"relations":[]}\n```'
    got = parse_json_loose(raw)
    assert got and len(got["entities"]) == 1


def test_prose_wrapped_json():
    raw = ('好的，抽取结果如下：'
           '{"entities":[{"name":"A","type":"角色"}],"relations":[]} 以上。')
    got = parse_json_loose(raw)
    assert got and len(got["entities"]) == 1


def test_picks_richest_candidate():
    """多个候选块时取信息量最大者，而不是第一个。"""
    raw = ('先给个例子 {"entities":[{"name":"X","type":"角色"}],"relations":[]} '
           '真正的结果：{"entities":[{"name":"A","type":"角色"},'
           '{"name":"B","type":"角色"}],"relations":[{"src":"A","relation":"r","dst":"B"}]}')
    got = parse_json_loose(raw)
    assert len(got["entities"]) == 2
    assert len(got["relations"]) == 1


def test_subject_object_aliases():
    """兼容 subject/predicate/object 写法。"""
    raw = '[{"subject":"A","predicate":"认识","object":"B"}]'
    got = parse_json_loose(raw)
    assert len(got["relations"]) == 1


def test_nested_wrapper_keys():
    raw = '{"result":{"entities":[{"name":"A","type":"角色"}],"relations":[]}}'
    got = parse_json_loose(raw)
    assert got and len(got["entities"]) == 1


# ── 畸形修复 ──

def test_repair_trailing_comma():
    got = _repair('{"entities":[{"name":"A","type":"角色"},],"relations":[]}')
    assert isinstance(got, dict)


def test_repair_unclosed_brackets():
    got = parse_json_loose('{"entities":[{"name":"A","type":"角色"}')
    assert got is not None


@pytest.mark.parametrize("bad", ["", "   ", "no json here", None])
def test_garbage_returns_none(bad):
    assert parse_json_loose(bad) is None


def test_scan_json_values_finds_all():
    s = '{"a":1} and {"b":2} and [1,2]'
    vals = _scan_json_values(s)
    assert len(vals) == 3


def test_scan_handles_braces_inside_strings():
    """字符串里的花括号不能干扰配平计数。"""
    s = '{"text":"a { b } c","n":1}'
    vals = _scan_json_values(s)
    assert len(vals) == 1
    assert vals[0]["n"] == 1


# ── 类型判定 ──

@pytest.mark.parametrize("d,exp", [
    ({"name": "A", "type": "角色"}, True),
    ({"name": "A", "aliases": []}, True),
    ({"name": "A", "desc": "x"}, True),
    ({"name": "A"}, False),
    ({"type": "角色"}, False),
])
def test_looks_like_entity(d, exp):
    assert _looks_like_entity(d) is exp


@pytest.mark.parametrize("d,exp", [
    ({"src": "A", "dst": "B"}, True),
    ({"subject": "A", "object": "B"}, True),
    ({"src": "A"}, False),
    ({"name": "A", "type": "角色"}, False),
])
def test_looks_like_relation(d, exp):
    assert _looks_like_relation(d) is exp


def test_coerce_empty_list_returns_none():
    assert _coerce_envelope([]) is None


def test_coerce_unknown_shape_returns_none():
    assert _coerce_envelope({"foo": "bar"}) is None


# ── 字符串内部未转义引号（实测高频故障）──

def test_unescaped_inner_quotes_in_desc():
    """回归：kimi 在 desc 里引用原文时用 ASCII 引号，导致整段 JSON 非法。

    实测该故障把 `飞驰！明日之城:14.0.1` 的 13 实体 10 关系静默降级成
    1 实体 0 关系（因为只解出了第一个配平片段）。
    """
    raw = ('{"entities":[{"name":"J","type":"角色","desc":"信奉"受苦者"的使徒"},'
           '{"name":"受苦者","type":"概念","desc":"被"皈依"的对象"}],'
           '"relations":[{"src":"J","relation":"信仰","dst":"受苦者",'
           '"evidence":"皈依"受苦者"的怀抱","confidence":1.0}]}')
    got = parse_json_loose(raw)
    assert got is not None, "含内部引号的 JSON 必须能被修复"
    assert len(got["entities"]) == 2, f"应为 2 实体，实际 {len(got['entities'])}"
    assert len(got["relations"]) == 1
    assert got["entities"][1]["name"] == "受苦者"


def test_unescaped_inner_quotes_preserve_text():
    raw = '{"entities":[{"name":"A","type":"角色","desc":"他说"你好"了"}]}'
    got = parse_json_loose(raw)
    assert got["entities"][0]["desc"] == '他说"你好"了'


def test_valid_escaped_quotes_still_work():
    """已正确转义的引号不能被破坏。"""
    raw = '{"entities":[{"name":"A","type":"角色","desc":"他说\\"你好\\"了"}]}'
    got = parse_json_loose(raw)
    assert got["entities"][0]["desc"] == '他说"你好"了'


def test_escaping_does_not_break_normal_json():
    from compendium_rag.llm import _escape_inner_quotes
    normal = '{"a":1,"b":"x","c":[1,2],"d":{"e":"y"}}'
    assert json.loads(_escape_inner_quotes(normal)) == json.loads(normal)


def test_chinese_quotes_untouched():
    raw = '{"entities":[{"name":"A","type":"角色","desc":"信奉“受苦者”的使徒"}]}'
    got = parse_json_loose(raw)
    assert got["entities"][0]["desc"] == "信奉“受苦者”的使徒"


def test_deep_nested_escaping():
    from compendium_rag.llm import _escape_inner_quotes
    s = '{"a":[{"b":"he said "hi" to me"}]}'
    got = json.loads(_escape_inner_quotes(s))
    assert got["a"][0]["b"] == 'he said "hi" to me'


# ── 额度耗尽：必须快速失败而非空转重试 ──

def test_quota_exhausted_detected():
    """网关 429 + error.code=14018「额度已用尽」应判为专用异常。

    回归：早期实现把它当普通限流，为 2997 个块各重试 3 次，
    实测浪费 6038 次重试且拖长构建时间。
    """
    from compendium_rag.llm import LLMQuotaExhausted, QUOTA_MARKERS
    assert "14018" in QUOTA_MARKERS
    assert "额度已用尽" in QUOTA_MARKERS
    assert issubclass(LLMQuotaExhausted, Exception)


def test_quota_exhausted_is_distinct_from_rate_limit():
    """额度耗尽 ≠ 普通限流：前者重试无意义，必须区分。"""
    from compendium_rag.llm import (LLMError, LLMQuotaExhausted, _repair)  # noqa: F401
    assert issubclass(LLMQuotaExhausted, LLMError)

    real_body = ('{"error":{"code":"rate_limit_exceeded","message":'
                 '"{\\"error\\":{\\"data\\":{\\"code\\":14018,\\"msg\\":'
                 '"额度已用尽，请访问以下链接"}}}"}}')
    from compendium_rag.llm import QUOTA_MARKERS
    assert any(m in real_body for m in QUOTA_MARKERS), \
        "实测网关响应体必须能被识别"


def test_quota_dead_flag_short_circuits():
    """一旦确认额度耗尽，同一进程内后续调用应立刻失败，不再打网关。"""
    import asyncio
    from compendium_rag.llm import CloudLLM, LLMQuotaExhausted

    async def run():
        client = CloudLLM(base_url="http://127.0.0.1:1", api_key="k",
                          model="m", concurrency=1, max_retries=3)
        async with client:
            client.quota_dead = True          # 模拟已确认耗尽
            try:
                await client.complete_json("s", "u")
            except LLMQuotaExhausted:
                return True
            return False

    assert asyncio.run(run()) is True


# ── 文本模式（P4 作答通路）：与 JSON 模式的边界必须钉死 ──

def _mock_client(handler):
    """把 CloudLLM 的 httpx 客户端换成 MockTransport（零网络）。

    不走 ``async with``，直接把 ``_sem`` / ``_client`` 装上——用例要测的是
    两条调用路径的**报文差异**，不需要真实客户端生命周期。
    """
    import asyncio

    import httpx

    from compendium_rag.llm import CloudLLM

    client = CloudLLM(base_url="http://mock.local/v1", api_key="k", model="m",
                      concurrency=1, max_retries=1, temperature=0.0)
    client._sem = asyncio.Semaphore(1)
    client._client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    return client


def test_complete_json_still_sends_json_mode_and_parses():
    """回归守卫：``complete_text`` 是**新增**路径，JSON 模式行为必须逐项不变。

    这是「只允许新增、不得改动 complete_json」这条写面约束的可执行版本——
    少了它，某次重构把两条路径合并就会静默改变抽取期行为。
    """
    import asyncio
    import json

    import httpx

    seen: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen.update(json.loads(request.content.decode("utf-8")))
        return httpx.Response(200, json={
            "model": "mock-model",
            "choices": [{"message": {"content": '{"entities":[{"name":"A","type":"角色"}],'
                                                '"relations":[]}'},
                         "finish_reason": "stop"}],
        })

    client = _mock_client(handler)

    async def run():
        try:
            return await client.complete_json("sys", "usr")
        finally:
            await client._client.aclose()

    parsed, meta = asyncio.run(run())
    assert seen["response_format"] == {"type": "json_object"}
    assert seen["messages"] == [{"role": "system", "content": "sys"},
                                {"role": "user", "content": "usr"}]
    assert isinstance(parsed, dict) and len(parsed["entities"]) == 1
    assert meta.finish_reason == "stop"


def test_complete_text_shares_transport_but_not_parser():
    """文本模式：同一份 messages 直接透传，且不要求网关返回 JSON。"""
    import asyncio
    import json

    import httpx

    seen: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen.update(json.loads(request.content.decode("utf-8")))
        return httpx.Response(200, json={
            "model": "mock-model",
            "choices": [{"message": {"content": "纯文本答案"}, "finish_reason": "stop"}],
        })

    client = _mock_client(handler)
    msgs = [{"role": "system", "content": "s"}, {"role": "user", "content": "u"}]

    async def run():
        try:
            return await client.complete_text(msgs)
        finally:
            await client._client.aclose()

    text, meta = asyncio.run(run())
    assert text == "纯文本答案"
    assert isinstance(text, str)
    assert "response_format" not in seen
    assert seen["messages"] == msgs
    assert meta.model == "mock-model"
