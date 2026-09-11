"""P0 提示词优化项测试（角色扮演质量专项）。

覆盖：
- P0-1 mes_example 三组情绪对话对（角色卡数据层校验）；
- P0-2 core_anchors 置底注入 + 零回归；
- P0-3 emotion_strategies 动态注入（精确/父类兜底/未命中）；
- P0-4 RAG 块去编号、改为「（来源）正文」记忆碎片格式；
- P0-5 behavior_rules 结构化迁移 + merge_structured_rules 两种语义。

共同约束：所有新字段缺省时，输出必须与改造前逐字节一致（零回归）。
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from roleplay.core.behavior_rules import match_condition
from roleplay.core.character_card import resolve_system_prompt
from roleplay.core.persona_prompt import (
    build_core_anchors_block,
    build_rag_context,
    build_roleplay_prompt,
    resolve_emotion_strategy,
)
from roleplay.core.rag.base import RetrievedChunk
from roleplay.models.character import CharacterCard

CARD_PATH = Path(__file__).resolve().parents[1] / "data" / "characters" / "wu_ming_zhe.json"
ASSET_CARD_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "roleplay"
    / "assets"
    / "characters"
    / "wu_ming_zhe.json"
)


def _chunk(text: str, score: float = 1.0, ns: str = "lore_x", section: str = "档案") -> RetrievedChunk:
    return RetrievedChunk(text=text, score=score, metadata={"namespace": ns, "section": section})


# ---------------------------------------------------------------------------
# P0-2 核心锚点
# ---------------------------------------------------------------------------

def test_core_anchors_injected_at_tail():
    """锚点块出现在提示词末尾，且早于复读抑制块、晚于 footer 风格指令。"""
    card = (
        '{"name":"无名者","personality":"冷静","post_history_instructions":"风格指令",'
        '"core_anchors":["用轻描淡写缓冲沉重话题","说话简短精确"],'
        '"prompt_config":{"footer_fields":["post_history_instructions"]}}'
    )
    prompt = build_roleplay_prompt(
        card_json=card, fallback_prompt=None, default_card=None,
        message="你到底是谁", chunks=[], repetition_block="【复读抑制】块",
    )
    assert "【别忘了你是谁】" in prompt
    assert "- 用轻描淡写缓冲沉重话题" in prompt
    assert "【复读抑制】块" in prompt
    # 顺序：footer 风格指令 → 锚点 → 复读抑制
    assert prompt.index("风格指令") < prompt.index("【别忘了你是谁】")
    assert prompt.index("【别忘了你是谁】") < prompt.rindex("【复读抑制】块")


def test_core_anchors_absent_when_unset_zero_regression():
    """未配置 core_anchors → 输出与同卡无该字段时逐字节一致（零回归）。"""
    base = '{"name":"无名者","personality":"冷静","tone":"低沉"}'
    with_null = base[:-1] + ',"core_anchors":null}'
    with_empty = base[:-1] + ',"core_anchors":[]}'
    p0 = build_roleplay_prompt(
        card_json=base, fallback_prompt=None, default_card=None, message="你好", chunks=[]
    )
    for variant in (with_null, with_empty):
        p = build_roleplay_prompt(
            card_json=variant, fallback_prompt=None, default_card=None, message="你好", chunks=[]
        )
        assert p == p0, "core_anchors 空值不得改变输出"
    assert "【别忘了你是谁】" not in p0


def test_core_anchors_template_override():
    """custom_templates.core_anchors 可覆盖默认块头。"""
    card = (
        '{"name":"A","core_anchors":["锚一"],'
        '"prompt_config":{"custom_templates":{"core_anchors":"【记住】\\n{value}"}}}'
    )
    prompt = build_roleplay_prompt(
        card_json=card, fallback_prompt=None, default_card=None, message="你好", chunks=[]
    )
    assert "【记住】" in prompt and "【别忘了你是谁】" not in prompt


def test_build_core_anchors_block_filters_blank():
    """空白/非字符串项被丢弃；全空 → 空串。"""
    assert build_core_anchors_block(None) == ""
    assert build_core_anchors_block([]) == ""
    assert build_core_anchors_block(["  ", "有效锚点"]) == "【别忘了你是谁】\n- 有效锚点"
    assert build_core_anchors_block(["  ", None, 123]) == ""  # type: ignore[list-item]


# ---------------------------------------------------------------------------
# P0-3 情绪策略
# ---------------------------------------------------------------------------

def test_resolve_emotion_strategy_exact_and_parent():
    strategies = {"sad": "陪伴策略", "happy": "轻松策略"}
    assert resolve_emotion_strategy(strategies, "sad") == "陪伴策略"
    # 父类兜底：love/grateful/excited → happy
    assert resolve_emotion_strategy(strategies, "love") == "轻松策略"
    assert resolve_emotion_strategy(strategies, "grateful") == "轻松策略"
    # 未命中（含父类也没有）→ None
    assert resolve_emotion_strategy(strategies, "angry") is None
    # 空输入 → None
    assert resolve_emotion_strategy(None, "sad") is None
    assert resolve_emotion_strategy(strategies, None) is None
    assert resolve_emotion_strategy({}, "sad") is None


def test_emotion_strategy_injected_before_footer():
    """策略块按情绪注入，且位于 footer 风格指令之前。"""
    card = (
        '{"name":"无名者","post_history_instructions":"风格指令",'
        '"emotion_strategies":{"sad":"先停半拍，再陪着"},'
        '"prompt_config":{"footer_fields":["post_history_instructions"]}}'
    )
    prompt = build_roleplay_prompt(
        card_json=card, fallback_prompt=None, default_card=None,
        message="我今天很难过", chunks=[], emotion="sad",
    )
    assert "【此刻对方的状态】" in prompt
    assert "先停半拍" in prompt
    assert prompt.index("【此刻对方的状态】") < prompt.index("风格指令")


def test_emotion_strategy_absent_when_no_match_zero_regression():
    """无策略表 / 情绪未命中 → 零注入，输出与不传 emotion 时一致。"""
    card = '{"name":"无名者","personality":"冷静"}'
    p_neutral = build_roleplay_prompt(
        card_json=card, fallback_prompt=None, default_card=None, message="你好", chunks=[]
    )
    p_unknown = build_roleplay_prompt(
        card_json=card, fallback_prompt=None, default_card=None,
        message="你好", chunks=[], emotion="sad",
    )
    assert p_neutral == p_unknown
    assert "【此刻对方的状态】" not in p_unknown


# ---------------------------------------------------------------------------
# P0-4 RAG 记忆碎片格式
# ---------------------------------------------------------------------------

def test_rag_context_uses_memory_fragment_format():
    """条目格式改为「（来源）正文」：无 [n] 编号、无半角括号包裹来源。"""
    ctx = build_rag_context(
        [_chunk("康斯坦丁教过她怎么拿扇子", 1.0, "lore_wu_ming_zhe", "养母"),
         _chunk("他提到巴南区的工程学院时声音放轻了", 0.9, "events", "")]
    )
    lines = ctx.splitlines()
    body = [ln for ln in lines if ln.startswith("（")]
    assert len(body) == 2, ctx
    assert "（角色设定资料·养母）康斯坦丁教过她怎么拿扇子" in ctx
    assert "（长期记忆）他提到巴南区的工程学院时声音放轻了" in ctx
    # 去编号：不得出现 "[1] （来源）" 形式的条目标记
    assert "[1]" not in ctx and "[2]" not in ctx
    assert re.search(r"^\s*\[\d+\]\s*[（(]", ctx, flags=re.M) is None


def test_rag_header_has_memory_fragment_rule():
    """默认 header 提示资料是「脑子里冒出来的片段」，且保留【角色资料库】前缀。"""
    ctx = build_rag_context([_chunk("某条资料")])
    assert ctx.startswith("【角色资料库")
    assert "脑子里自己冒出来的" in ctx


def test_rag_context_empty_returns_empty():
    assert build_rag_context([]) == ""


# ---------------------------------------------------------------------------
# P0-5 行为规则结构化
# ---------------------------------------------------------------------------

_TEXT_RULES = "1. 第一人称扮演\n2. 不写大段旁白"
_STRUCTURED = [
    {
        "id": "who",
        "condition": {"type": "text_regex", "field": "user_message", "pattern": "你是谁|身份"},
        "action": "列出化名后落回无名者",
        "priority": 10,
        "enabled": True,
    }
]


def _card_with_rules(merge: bool | None) -> str:
    cfg = {"footer_fields": []}
    if merge is not None:
        cfg["merge_structured_rules"] = merge
    return json.dumps(
        {
            "name": "无名者",
            "behavior_rules": _TEXT_RULES,
            "behavior_rules_structured": _STRUCTURED,
            "prompt_config": cfg,
        },
        ensure_ascii=False,
    )


def test_structured_rules_default_replace_semantics():
    """默认（未配置 merge）：命中即替换——保留改造前语义（零回归）。"""
    hit = resolve_system_prompt(character_card=_card_with_rules(None), fallback_prompt=None, message="你是谁")
    assert "列出化名后落回无名者" in hit
    assert "第一人称扮演" not in hit

    miss = resolve_system_prompt(character_card=_card_with_rules(None), fallback_prompt=None, message="今天天气")
    assert "列出化名后落回无名者" not in miss
    assert "第一人称扮演" in miss


def test_structured_rules_merge_mode_keeps_core_text():
    """merge_structured_rules=true：核心文本常驻 + 命中条件规则叠加。"""
    hit = resolve_system_prompt(character_card=_card_with_rules(True), fallback_prompt=None, message="你的身份是什么")
    assert "第一人称扮演" in hit
    assert "列出化名后落回无名者" in hit

    miss = resolve_system_prompt(character_card=_card_with_rules(True), fallback_prompt=None, message="今天天气")
    assert "第一人称扮演" in miss
    assert "列出化名后落回无名者" not in miss


def test_structured_rules_merge_mode_in_build_roleplay_prompt():
    """merge 模式在完整链路（build_roleplay_prompt）下同样生效。"""
    prompt = build_roleplay_prompt(
        card_json=_card_with_rules(True), fallback_prompt=None, default_card=None,
        message="你是谁", chunks=[], emotion=None,
    )
    assert "第一人称扮演" in prompt and "列出化名后落回无名者" in prompt


def test_emotion_is_supports_multi_value():
    """emotion_is 支持 | 分隔多值；单值语义不变。"""
    cond = {"type": "emotion_is", "field": "current_emotion", "pattern": "sad|fear|anxious"}
    assert match_condition(cond, {"current_emotion": "fear"})
    assert match_condition(cond, {"current_emotion": "sad"})
    assert not match_condition(cond, {"current_emotion": "happy"})
    single = {"type": "emotion_is", "field": "current_emotion", "pattern": "sad"}
    assert match_condition(single, {"current_emotion": "sad"})
    assert not match_condition(single, {"current_emotion": "sadness"})


# ---------------------------------------------------------------------------
# P0-1 + 角色卡数据层校验（data 与 assets 两张卡保持一致）
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("path", [CARD_PATH, ASSET_CARD_PATH])
def test_character_card_p0_fields(path: Path):
    """两张角色卡都完成 P0 改造，且能被模型层正确解析。"""
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    card = CharacterCard.parse_raw_card(raw)
    assert card is not None, f"{path.name} 解析失败"

    # P0-1：三组对话对，含 user/assistant 双方，总长 ≤600 字
    mes = card.mes_example
    groups = [g for g in mes.split("\n\n") if g.strip()]
    assert len(groups) == 3, f"期望 3 组对话对，实际 {len(groups)}"
    assert len(mes) <= 600, f"mes_example 过长：{len(mes)} 字"
    for g in groups:
        assert g.count("用户：") >= 1 and g.count("无名者：") >= 1
    # 自定义模板已带标题，值内不应重复
    assert "口吻示范" not in mes

    # P0-2：3-5 条锚点，每条 ≤20 字
    anchors = card.core_anchors
    assert anchors and 3 <= len(anchors) <= 5
    for a in anchors:
        assert len(a) <= 20, f"锚点过长：{a}"

    # P0-3：策略表覆盖 15 类情绪标签
    strategies = card.emotion_strategies
    assert strategies
    labels = {
        "happy", "sad", "angry", "anxious", "surprise", "fear", "neutral",
        "love", "grateful", "excited", "disappointed", "lonely",
        "embarrassed", "confused", "sleepy",
    }
    assert labels - set(strategies) == set(), f"缺少策略：{labels - set(strategies)}"

    # P0-5：核心文本规则精简 + 条件规则结构化
    assert data["behavior_rules_structured"], "结构化规则未启用"
    text_rules = [ln for ln in card.behavior_rules.split("\n") if ln.strip()]
    assert len(text_rules) <= 6, f"核心规则未精简：{len(text_rules)} 条"
    for rule in data["behavior_rules_structured"]:
        assert rule["condition"]["type"] in ("text_contains", "text_regex", "emotion_is")
        assert rule["action"].strip()

    # merge 开关必须开启，否则结构化规则命中时会顶掉核心文本规则
    assert data["prompt_config"].get("merge_structured_rules") is True


def test_store_roundtrip_keeps_p0_fields(tmp_path):
    """P0 字段走通 CharacterStore 落盘与局部更新（不被 update 清空）。"""
    from roleplay.core.knowledge.character_store import CharacterStore

    store = CharacterStore(persist_dir=tmp_path, seed_card_path=None)
    cid = store.create(
        {"name": "测试角色", "core_anchors": ["锚一", "   "],
         "emotion_strategies": {"Sad": "陪伴策略"}}
    )
    card = store.get(cid)
    assert card is not None
    assert card.core_anchors == ["锚一"]          # 空白项被收敛
    assert card.emotion_strategies == {"sad": "陪伴策略"}  # 键小写归一

    store.update(cid, {"tone": "低沉"})
    card = store.get(cid)
    assert card is not None
    assert card.core_anchors == ["锚一"], "局部更新不得清空 core_anchors"
    assert card.emotion_strategies == {"sad": "陪伴策略"}

    reloaded = CharacterStore(persist_dir=tmp_path, seed_card_path=None)
    assert reloaded.get(cid) is not None
    assert reloaded.get(cid).core_anchors == ["锚一"]

    # 显式清空：空列表/空字典必须能覆盖旧值（前端清空文本框后保存依赖此语义）
    store.update(cid, {"core_anchors": [], "emotion_strategies": {}})
    card = store.get(cid)
    assert card is not None
    assert card.core_anchors == [] and card.emotion_strategies == {}


def test_all_structured_rules_are_valid():
    """角色卡中的结构化规则全部通过引擎校验（无非法正则/缺字段被静默丢弃）。"""
    from roleplay.core.behavior_rules import _clean_rules

    data = json.loads(CARD_PATH.read_text(encoding="utf-8"))
    raw = data["behavior_rules_structured"]
    cleaned = _clean_rules(raw)
    assert len(cleaned) == len(raw), "存在被丢弃的非法规则"
    assert {r["id"] for r in cleaned} >= {"identity_who", "identity_deny_ai",
                                          "past_crimes_understatement", "white_knight"}
