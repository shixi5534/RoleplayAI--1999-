"""P2 批次测试：动态压缩（P2-1）/ 两阶段生成（P2-3）/ 评估纯函数（P2-2）。

共同约束：dynamic_compression / refine_enabled 缺省（False）时，
输出与行为与改造前逐字节一致（零回归）。
"""
import importlib.util
import json
import sys
from pathlib import Path

import pytest

from roleplay.core.character_card import (
    _compression_band,
    _one_line_summary,
    resolve_system_prompt,
)
from roleplay.core.emotion.detector import KeywordEmotionDetector
from roleplay.core.llm.base import LLMPort
from roleplay.core.orchestrator import ChatOrchestrator
from roleplay.core.persona_prompt import build_roleplay_messages
from roleplay.core.rag.memory import InMemoryVectorStore
from roleplay.models.chat import ChatRequest

# ───────────────────────── 夹具：合成角色卡（结构对齐 wu_ming_zhe） ─────────────────────────
CARD_DICT = {
    "name": "测试角色",
    "personality": "平静、自控，带观察者的疏离。黑色幽默，能冷静复盘悲剧。",
    "background": "幼年被绑架接受训练，后成为特工。",
    "scenario": "第十三章之后刚加入小队。",
    "behavior_rules": "1. 始终第一人称\n2. 不承认是AI",
    "first_mes": "初次见面，请多关照。",
    "mes_example": "用户：A问题\n角色：第一组回答。\n\n用户：B问题\n角色：第二组回答。",
}
CARD_PLAIN = json.dumps(CARD_DICT, ensure_ascii=False)
# 开启动态压缩的同一张卡
CARD_COMPRESS = json.dumps(
    {**CARD_DICT, "prompt_config": {"dynamic_compression": True}},
    ensure_ascii=False,
)


# ───────────────────────── P2-1：压缩档位 ─────────────────────────
def test_band_boundaries():
    assert _compression_band(0) == 0
    assert _compression_band(5) == 0
    assert _compression_band(6) == 1
    assert _compression_band(19) == 1
    assert _compression_band(20) == 2
    assert _compression_band(-3) == 0  # 负数防御


def test_one_line_summary():
    assert _one_line_summary("平静、自控。黑色幽默，能复盘。") == "平静、自控。"
    assert _one_line_summary("没有句读的一长串" * 20) != ""


def test_compression_off_is_zero_regression():
    """开关关闭：任何轮次输出与 turn_count=0 逐字节一致。"""
    base = resolve_system_prompt(
        character_card=CARD_PLAIN, fallback_prompt=None, turn_count=0
    )
    for t in (5, 10, 25, 100):
        assert resolve_system_prompt(
            character_card=CARD_PLAIN, fallback_prompt=None, turn_count=t
        ) == base


def test_band0_compression_on_is_full():
    """开关开启但 <6 轮：与关闭时逐字节一致（零回归）。"""
    assert resolve_system_prompt(
        character_card=CARD_COMPRESS, fallback_prompt=None, turn_count=0
    ) == resolve_system_prompt(
        character_card=CARD_PLAIN, fallback_prompt=None, turn_count=0
    )


def test_band1_keeps_first_example_pair():
    """6–20 轮：mes_example 只留第一组对话对，其余字段完整。"""
    p = resolve_system_prompt(
        character_card=CARD_COMPRESS, fallback_prompt=None, turn_count=10
    )
    assert "第一组回答" in p
    assert "第二组回答" not in p
    assert "幼年被绑架" in p  # background 仍完整
    assert "初次见面" in p


def test_band2_drops_detail_keeps_core():
    """≥20 轮：撤下 background/scenario/first_mes/mes_example，人设一句话概括，
    保留 name 与核心规则（刻意偏离计划的 安全取舍，见 character_card 注释）。"""
    p = resolve_system_prompt(
        character_card=CARD_COMPRESS, fallback_prompt=None, turn_count=25
    )
    assert "你是测试角色。" in p
    assert "平静、自控，带观察者的疏离。" in p  # 一句话概括
    assert "黑色幽默" not in p  # 概括之外的细节被压缩
    assert "幼年被绑架" not in p
    assert "第十三章" not in p
    assert "初次见面" not in p
    assert "第一组回答" not in p
    assert "不承认是AI" in p  # 核心规则常驻


def test_band2_no_empty_blocks():
    """压缩后渲染不含空块（字段清空 → 渲染层自然跳过）。"""
    p = resolve_system_prompt(
        character_card=CARD_COMPRESS, fallback_prompt=None, turn_count=25
    )
    for line in p.splitlines():
        if line.startswith(("背景：", "场景：", "对话示例")):
            pytest.fail(f"压缩后仍渲染已撤字段：{line}")


def test_layered_messages_also_compressed():
    """P1-1 分层路径同样吃到压缩（两者共用 resolve_system_prompt）。"""
    layers = build_roleplay_messages(
        card_json=CARD_COMPRESS, fallback_prompt=None, default_card=None,
        message="你好", turn_count=25,
    )
    assert layers.system_blocks
    assert "幼年被绑架" not in layers.system_blocks[0]


# ───────────────────────── P2-3：两阶段生成 ─────────────────────────
class ScriptedLLM(LLMPort):
    """按脚本依次返回回复并记录调用参数（验证精炼段触发/温度/采纳逻辑）。"""

    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []

    @property
    def model_name(self) -> str:
        return "scripted"

    async def generate(self, *, system, user, history=None,
                       temperature=None, system_blocks=None, user_prefix=None):
        self.calls.append({
            "system": system, "user": user, "temperature": temperature,
            "user_prefix": user_prefix,
        })
        return self.replies.pop(0) if self.replies else "好的。"

    async def generate_stream(self, **kw):
        text = await self.generate(**kw)
        for i in range(0, len(text), 3):
            yield text[i: i + 3]


BAD = "作为一个AI，希望这对你有帮助。"  # 身份出戏 + 客服腔（双违规）
GOOD = "嗯，我在。"


def _use_scripted_llm(monkeypatch, scripted):
    """run()/stream() 走「请求级 LLM 构建」（build_llm_from_config），
    不用构造器注入的 self._llm —— 测试里把该工厂指到脚本化桩上。"""
    import roleplay.core.orchestrator as orch_mod

    monkeypatch.setattr(
        orch_mod, "build_llm_from_config",
        lambda settings, override=None: (scripted, False),
    )


def _make_orch(scripted, **kw):
    return ChatOrchestrator(
        llm=scripted,
        emotion=KeywordEmotionDetector(),
        rag=InMemoryVectorStore(),
        **kw,
    )


async def test_refine_adopted_when_clean(monkeypatch):
    """精炼开启：违规稿 → SELF-CHECK 低温度重写 → 干净稿被采纳。"""
    scripted = ScriptedLLM([BAD, GOOD])
    _use_scripted_llm(monkeypatch, scripted)
    orch = _make_orch(
        scripted,
        quality_guard_max_retries=0,  # 跳过 P1-4 重试循环，直通精炼段
        refine_enabled=True,
    )
    res = await orch.run(ChatRequest(session_id="s", message="随便聊聊"))
    assert res.response.reply == GOOD
    assert len(scripted.calls) == 2
    first, second = scripted.calls
    # 兼容单 system 与分层两种模式：SELF-CHECK 指令必然出现在其中之一
    second_all = (second["system"] or "") + "\n" + (second["user_prefix"] or "")
    assert "SELF-CHECK" in second_all
    assert second["temperature"] == pytest.approx(0.3)  # 低温度
    assert first["temperature"] != second["temperature"]


async def test_refine_disabled_keeps_draft(monkeypatch):
    """精炼关闭（默认）：违规稿原样保留，只有一次生成（零回归）。"""
    scripted = ScriptedLLM([BAD])
    _use_scripted_llm(monkeypatch, scripted)
    orch = _make_orch(scripted, quality_guard_max_retries=0)
    res = await orch.run(ChatRequest(session_id="s", message="随便聊聊"))
    assert res.response.reply == BAD
    assert len(scripted.calls) == 1


async def test_refine_not_called_on_clean_draft(monkeypatch):
    """首轮即干净：不触发精炼（不为合格回复付延迟）。"""
    scripted = ScriptedLLM([GOOD])
    _use_scripted_llm(monkeypatch, scripted)
    orch = _make_orch(scripted, quality_guard_max_retries=0, refine_enabled=True)
    res = await orch.run(ChatRequest(session_id="s", message="随便聊聊"))
    assert res.response.reply == GOOD
    assert len(scripted.calls) == 1


async def test_refine_rejected_when_still_dirty(monkeypatch):
    """精炼稿仍违规：保留原稿（宁缺毋滥）。"""
    scripted = ScriptedLLM([BAD, "作为一个AI，我来帮你总结一下。"])
    _use_scripted_llm(monkeypatch, scripted)
    orch = _make_orch(
        scripted, quality_guard_max_retries=0, refine_enabled=True
    )
    res = await orch.run(ChatRequest(session_id="s", message="随便聊聊"))
    assert res.response.reply == BAD
    assert len(scripted.calls) == 2


async def test_refine_temperature_clamped(monkeypatch):
    """精炼温度钳制在 [0.05, 1]：非法配置不炸、不越界。"""
    scripted = ScriptedLLM([BAD, GOOD])
    _use_scripted_llm(monkeypatch, scripted)
    orch = _make_orch(
        scripted,
        quality_guard_max_retries=0,
        refine_enabled=True,
        refine_temperature=5.0,
    )
    await orch.run(ChatRequest(session_id="s", message="随便聊聊"))
    assert scripted.calls[1]["temperature"] == pytest.approx(1.0)


def test_refine_prompt_settings_defaults():
    """Settings 默认关闭（零回归）+ 字段可解析。"""
    from roleplay.config import Settings

    s = Settings()
    assert s.refine_enabled is False
    assert 0.0 < s.refine_temperature < 1.0


# ───────────────────────── P2-2：评估纯函数 ─────────────────────────
def _load_eval_module():
    path = Path(__file__).resolve().parents[1] / "scripts" / "eval_roleplay_quality.py"
    spec = importlib.util.spec_from_file_location("eval_rq", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["eval_rq"] = mod  # dataclass 反查 __module__ 需要注册进 sys.modules
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def ev():
    return _load_eval_module()


def test_recycle_rate_detects_copy(ev):
    refs = ["难过是很贵的情绪，我把它留给了更值得的事。"]
    copy = "难过是很贵的情绪，我把它留给了更值得的事。"
    fresh = "……贵不贵的，先吃饭吧。"
    assert ev.lexical_recycle_rate(copy, refs) > 0.5
    assert ev.lexical_recycle_rate(fresh, refs) < 0.3
    assert ev.lexical_recycle_rate("", refs) == 0.0


def test_net_reply_length_strips_actions(ev):
    text = "*她抬了抬眼*，嗯，我在。（很轻）"
    assert ev.net_reply_length(text) == len("，嗯，我在。")


def test_parse_judge_json_three_level(ev):
    assert ev.parse_judge_json('{"consistency": 5, "empathy": 4, "immersion": 5}') == {
        "consistency": 5, "empathy": 4, "immersion": 5,
    }
    got = ev.parse_judge_json('评语：不错 {"consistency": 4, "empathy": 4, "immersion": 4} 完')
    assert got and got["consistency"] == 4
    assert ev.parse_judge_json("完全不是JSON") is None
    assert ev.parse_judge_json("") is None


def test_eval_cases_inventory(ev):
    """评估集 ≥20 例，覆盖计划要求的全部场景类别。"""
    kinds = {c.kind for c in ev.EVAL_CASES}
    assert len(ev.EVAL_CASES) >= 20
    assert {"identity", "tone", "emotion", "boundary", "sensitive",
            "length", "recycle", "faithfulness", "profile", "meta"} <= kinds
    ids = [c.id for c in ev.EVAL_CASES]
    assert len(ids) == len(set(ids)), "用例 id 重复"
