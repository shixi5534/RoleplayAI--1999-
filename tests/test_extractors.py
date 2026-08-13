"""画像提取器测试：规则类型映射 / 否定→correction / LLM 三级解析 / 组合降级。"""
import asyncio

import pytest

from roleplay.core.knowledge.extractors import (
    LLMProfileExtractor,
    RuleProfileExtractor,
    build_profile_extractors,
    extract_profile_entries,
)
from roleplay.core.knowledge.profile_models import ProfileEntry
from roleplay.core.llm.mock import MockLLMProvider


# ───────────────────────── 规则提取：类型映射 ─────────────────────────
def test_rule_preference():
    r = RuleProfileExtractor()
    entries = r.extract([{"role": "user", "content": "我喜欢咖啡"}])
    assert len(entries) == 1
    e = entries[0]
    assert e.type == "preference"
    assert e.key == "咖啡"
    assert e.value == "喜欢咖啡"
    assert e.confidence == 0.3


def test_rule_preference_negative():
    r = RuleProfileExtractor()
    entries = r.extract([{"role": "user", "content": "我讨厌香菜"}])
    assert len(entries) == 1
    e = entries[0]
    assert e.type == "preference"
    assert "不喜欢" in e.value or "讨厌" in e.value


def test_rule_habit():
    r = RuleProfileExtractor()
    entries = r.extract([{"role": "user", "content": "我习惯早起"}])
    assert len(entries) == 1
    assert entries[0].type == "habit"
    assert entries[0].key == "早起"


def test_rule_important_date():
    r = RuleProfileExtractor()
    entries = r.extract([{"role": "user", "content": "我生日是5月20日"}])
    assert len(entries) == 1
    assert entries[0].type == "important_date"
    assert entries[0].value == "5月20日"


def test_rule_fact():
    r = RuleProfileExtractor()
    entries = r.extract([{"role": "user", "content": "我养了猫"}])
    assert len(entries) == 1
    assert entries[0].type == "fact"


def test_rule_only_user_turns():
    r = RuleProfileExtractor()
    entries = r.extract(
        [
            {"role": "assistant", "content": "我喜欢咖啡"},  # 角色说的话不提取
            {"role": "user", "content": "我喜欢茶"},
        ]
    )
    assert len(entries) == 1
    assert entries[0].key == "茶"


def test_rule_never_fails_on_garbage():
    r = RuleProfileExtractor()
    entries = r.extract([{"role": "user", "content": None}, {"role": "user", "content": 123}])
    assert entries == []


# ───────────────────────── 否定 → correction ─────────────────────────
def test_rule_correction():
    r = RuleProfileExtractor()
    entries = r.extract([{"role": "user", "content": "其实我不喜欢咖啡"}])
    assert len(entries) == 1
    e = entries[0]
    assert e.type == "correction"
    assert "咖啡" in e.key or "咖啡" in e.value


def test_rule_correction_no_longer():
    r = RuleProfileExtractor()
    entries = r.extract([{"role": "user", "content": "我现在不再喜欢咖啡了"}])
    assert entries and entries[0].type == "correction"


# ───────────────────────── LLM 提取：三级解析 ─────────────────────────
class _JsonLLM(MockLLMProvider):
    """可控 Mock：按 user 文本返回预置 JSON 字符串。"""

    def __init__(self, reply: str) -> None:
        super().__init__()
        self._reply = reply
        self.calls = 0

    async def generate(self, *, system, user, history=None, temperature=None) -> str:
        self.calls += 1
        return self._reply


async def test_llm_valid_json_array():
    llm = _JsonLLM(
        '[{"type": "preference", "key": "咖啡", "value": "喜欢拿铁", "importance": 0.8}]'
    )
    ext = LLMProfileExtractor(llm=llm, timeout=8.0)
    entries = await ext.extract([{"role": "user", "content": "我喜欢咖啡"}])
    assert len(entries) == 1
    e = entries[0]
    assert e.type == "preference"
    assert e.key == "咖啡"
    assert e.importance == 0.8
    assert llm.calls == 1


async def test_llm_json_block_wrapped():
    llm = _JsonLLM("```json\n[{\"type\": \"habit\", \"key\": \"早起\", \"value\": \"每天6点\", \"importance\": 0.6}]\n```")
    ext = LLMProfileExtractor(llm=llm)
    entries = await ext.extract([{"role": "user", "content": "我习惯早起"}])
    assert len(entries) == 1
    assert entries[0].type == "habit"


async def test_llm_regex_fallback():
    llm = _JsonLLM('garbage [{"type": "fact", "key": "猫", "value": "养了一只", "importance": 0.4}] trailing')
    ext = LLMProfileExtractor(llm=llm)
    entries = await ext.extract([{"role": "user", "content": "我养了猫"}])
    assert len(entries) == 1
    assert entries[0].type == "fact"


async def test_llm_invalid_json_returns_empty():
    llm = _JsonLLM("完全不是 JSON")
    ext = LLMProfileExtractor(llm=llm)
    entries = await ext.extract([{"role": "user", "content": "随便"}])
    assert entries == []
    assert ext._parse_fail >= 1


async def test_llm_exception_returns_empty():
    class _BoomLLM(MockLLMProvider):
        async def generate(self, *, system, user, history=None, temperature=None) -> str:
            raise RuntimeError("boom")

    ext = LLMProfileExtractor(llm=_BoomLLM())
    entries = await ext.extract([{"role": "user", "content": "我喜欢咖啡"}])
    assert entries == []


async def test_llm_timeout_returns_empty():
    class _SlowLLM(MockLLMProvider):
        async def generate(self, *, system, user, history=None, temperature=None) -> str:
            await asyncio.sleep(5)
            return "[]"

    ext = LLMProfileExtractor(llm=_SlowLLM(), timeout=0.05)
    entries = await ext.extract([{"role": "user", "content": "我喜欢咖啡"}])
    assert entries == []


async def test_llm_invalid_type_dropped():
    llm = _JsonLLM(
        '[{"type": "not_a_type", "key": "k", "value": "v"},'
        ' {"type": "fact", "key": "猫", "value": "养了一只", "importance": 0.4}]'
    )
    ext = LLMProfileExtractor(llm=llm)
    entries = await ext.extract([{"role": "user", "content": "我养了猫"}])
    assert len(entries) == 1
    assert entries[0].type == "fact"


# ───────────────────────── 组合提取（规则 + LLM 合并 / 降级） ─────────────────────────
async def test_combine_llm_priority_rule_fallback():
    """LLM 可用：LLM 条目优先，规则补漏。"""
    llm = _JsonLLM(
        '[{"type": "preference", "key": "咖啡", "value": "喜欢喝耶加雪菲", "importance": 0.9}]'
    )
    rule = RuleProfileExtractor()
    entries = await extract_profile_entries(
        [{"role": "user", "content": "我喜欢咖啡，我养了猫"}],
        rule=rule,
        llm=LLMProfileExtractor(llm=llm),
        llm_available=True,
    )
    keys = {e.key for e in entries}
    assert "咖啡" in keys  # LLM 优先（value 为 LLM 版本）
    assert "猫" in keys  # 规则补漏
    coffee = next(e for e in entries if e.key == "咖啡")
    assert coffee.value == "喜欢喝耶加雪菲"


async def test_combine_llm_unavailable_rule_only():
    """LLM 不可用（mock 零外发）→ 仅规则。"""
    llm = _JsonLLM('[]')
    rule = RuleProfileExtractor()
    entries = await extract_profile_entries(
        [{"role": "user", "content": "我喜欢咖啡"}],
        rule=rule,
        llm=LLMProfileExtractor(llm=llm),
        llm_available=False,
    )
    assert llm.calls == 0  # 零 LLM 调用
    assert len(entries) == 1
    assert entries[0].type == "preference"


async def test_combine_llm_failure_falls_back_to_rule():
    class _BoomLLM(MockLLMProvider):
        async def generate(self, *, system, user, history=None, temperature=None) -> str:
            raise RuntimeError("boom")

    rule = RuleProfileExtractor()
    entries = await extract_profile_entries(
        [{"role": "user", "content": "我喜欢咖啡"}],
        rule=rule,
        llm=LLMProfileExtractor(llm=_BoomLLM()),
        llm_available=True,
    )
    # LLM 异常 → 回退规则（仍有关键信息）
    assert len(entries) == 1
    assert entries[0].type == "preference"


# ───────────────────────── 构建辅助 ─────────────────────────
def test_build_profile_extractors_mock_no_llm():
    """mock 模式：LLM 提取器为 None（隐私：零外发）。"""
    from roleplay.config import Settings

    s = Settings(llm_provider="mock", llm_api_key="")
    rule, llm = build_profile_extractors(s)
    assert isinstance(rule, RuleProfileExtractor)
    assert llm is None


def test_build_profile_extractors_llm_with_key():
    """非 mock + 有 key：构建 LLM 提取器。"""
    from roleplay.config import Settings

    s = Settings(
        llm_provider="openai",
        llm_api_key="sk-test",
        llm_base_url="https://api.openai.com/v1",
    )
    rule, llm = build_profile_extractors(s)
    assert isinstance(rule, RuleProfileExtractor)
    assert isinstance(llm, LLMProfileExtractor)
