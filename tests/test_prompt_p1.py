"""P1 提示词优化项测试（消息结构 / 输出格式 / 情感节奏 / 生成后自检）。

覆盖：
- P1-1 消息结构重构：分层 system_blocks + user_prefix，默认单 system（零回归）；
- P1-2 输出格式升级：动态长度提示（分档 + 情绪上调）；
- P1-3 情感节奏：emotional_layers 的 surface / trigger / trust 三层选择与优先级；
- P1-4 生成后质量自检：身份出戏 / 客服腔 / 格式违规三类规则 + 重试接线。

共同约束：所有新字段与开关缺省时，输出必须与改造前逐字节一致（零回归）。
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from roleplay.core import orchestrator as orchestrator_module
from roleplay.core.llm.openai_like import _build_messages
from roleplay.core.orchestrator import ChatOrchestrator
from roleplay.core.persona_prompt import (
    build_length_hint,
    build_pacing_block,
    build_roleplay_messages,
    build_roleplay_prompt,
    resolve_pacing_strategy,
)
from roleplay.core.quality_guard import (
    find_quality_violations,
    quality_retry_hint,
)
from roleplay.core.rag.base import RetrievedChunk
from roleplay.core.emotion.detector import KeywordEmotionDetector
from roleplay.core.rag.memory import InMemoryVectorStore
from roleplay.models.character import CharacterCard
from roleplay.models.chat import ChatRequest
from roleplay.models.prompt_config import PromptConfig

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


# ===========================================================================
# P1-1 消息结构重构
# ===========================================================================

def test_message_layering_off_by_default():
    """默认配置不分層（零回归，且兼容不支持多 system 的端点）。"""
    assert PromptConfig().message_layering is False
    assert PromptConfig().dynamic_length is False


def test_layers_roundtrip_equals_single_system():
    """分层结构的块拼回去，必须与单 system 输出逐字节一致。"""
    card = (
        '{"name":"无名者","personality":"冷静","tone":"低沉",'
        '"post_history_instructions":"风格指令","core_anchors":["锚一"],'
        '"emotion_strategies":{"sad":"陪伴"},'
        '"prompt_config":{"footer_fields":["post_history_instructions"]}}'
    )
    kwargs = dict(
        card_json=card,
        fallback_prompt=None,
        default_card=None,
        message="我很难过",
        chunks=[_chunk("她害怕打雷。")],
        profile_chunks=[_chunk("用户在重庆念书。", ns="profile")],
        emotion="sad",
        repetition_block="【复读抑制】",
    )
    prompt = build_roleplay_prompt(**kwargs)
    layers = build_roleplay_messages(**kwargs)
    joined = "\n\n".join([b for b in [*layers.system_blocks, layers.user_prefix] if b])
    assert prompt == joined, "分层与单串两条路径必须产出相同内容"


def test_layers_split_persona_context_and_tail():
    """核心人设 / 资料画像在 system_blocks；动态指令进 user_prefix。"""
    card = (
        '{"name":"无名者","personality":"冷静","tone":"低沉",'
        '"post_history_instructions":"风格指令","core_anchors":["锚一"],'
        '"prompt_config":{"footer_fields":["post_history_instructions"]}}'
    )
    layers = build_roleplay_messages(
        card_json=card,
        fallback_prompt=None,
        default_card=None,
        message="你好",
        chunks=[_chunk("她害怕打雷。")],
        profile_chunks=[_chunk("用户在重庆念书。", ns="profile")],
        repetition_block="【复读抑制】",
    )
    # 4 条：核心人设 / 语气 / 用户画像 / RAG 资料
    assert len(layers.system_blocks) == 4, "人设 / 语气 / 画像 / RAG 各成一条 system"
    assert "你是无名者" in layers.system_blocks[0]
    assert "【语气要求】" in layers.system_blocks[1]
    assert "【用户资料】" in layers.system_blocks[2]
    assert "她害怕打雷" in layers.system_blocks[3]
    # 动态指令不留在 system 侧
    assert "【复读抑制】" not in "".join(layers.system_blocks)
    assert "别忘了你是谁" not in "".join(layers.system_blocks)
    # 且出现在 user_prefix
    assert "【复读抑制】" in layers.user_prefix
    assert "别忘了你是谁" in layers.user_prefix
    assert "风格指令" in layers.user_prefix


def test_layers_user_prefix_order():
    """user_prefix 内部顺序：情绪策略 → 情感节奏 → footer → 长度 → 锚点 → 复读抑制。"""
    card = (
        '{"name":"A","post_history_instructions":"风格","core_anchors":["锚"],'
        '"emotion_strategies":{"sad":"陪伴策略"},'
        '"emotional_layers":{"surface":"日常疏离"},'
        '"prompt_config":{"footer_fields":["post_history_instructions"],'
        '"dynamic_length":true}}'
    )
    layers = build_roleplay_messages(
        card_json=card,
        fallback_prompt=None,
        default_card=None,
        message="我很难过",
        emotion="sad",
        repetition_block="【复读】",
    )
    up = layers.user_prefix
    order = [
        up.index("此刻对方的状态"),   # 情绪策略
        up.index("此刻你的姿态"),     # 情感节奏
        up.index("风格"),             # footer
        up.index("本轮长度"),         # 动态长度
        up.index("别忘了你是谁"),     # 核心锚点
        up.index("【复读】"),         # 复读抑制
    ]
    assert order == sorted(order), f"置底块顺序错误：{order}"


def test_openai_build_messages_single_system_unchanged():
    """不传分层参数 → messages 与改造前逐条一致。"""
    msgs = _build_messages(system="人设", user="你好", history=[{"role": "user", "content": "上一句"}])
    assert msgs == [
        {"role": "system", "content": "人设"},
        {"role": "user", "content": "上一句"},
        {"role": "user", "content": "你好"},
    ]


def test_openai_build_messages_layered():
    """system_blocks → 多条 system；user_prefix 拼在 user 之前。"""
    msgs = _build_messages(
        system="兜底人设",
        user="你好",
        history=[{"role": "user", "content": "上一句"}],
        system_blocks=["人设", "资料"],
        user_prefix="【风格】简短",
    )
    assert [m["role"] for m in msgs] == ["system", "system", "user", "user"]
    assert msgs[0] == {"role": "system", "content": "人设"}
    assert msgs[1] == {"role": "system", "content": "资料"}
    assert msgs[-1]["content"] == "【风格】简短\n\n你好"
    assert "兜底人设" not in json.dumps(msgs, ensure_ascii=False)


def test_openai_build_messages_skips_blank_blocks():
    """空白块被跳过；system_blocks 全空时回退单 system。"""
    msgs = _build_messages(
        system="人设", user="你好", history=None,
        system_blocks=["人设", "   ", ""], user_prefix="  ",
    )
    assert [m["role"] for m in msgs] == ["system", "user"]
    assert msgs[0]["content"] == "人设"
    assert msgs[-1]["content"] == "你好"  # 空白 prefix 不产生多余空行

    fallback = _build_messages(system="人设", user="你好", history=None, system_blocks=[])
    assert fallback[0] == {"role": "system", "content": "人设"}


# ===========================================================================
# P1-2 输出格式与动态长度
# ===========================================================================

def test_length_bands_by_message_length():
    """<10 字 → 1-2 句；10–30 字 → 2-4 句；>30 字 → 3-6 句。"""
    assert "1-2 句" in build_length_hint("你好")
    assert "1-2 句" in build_length_hint("一二三四五六七八九")      # 9 字
    assert "2-4 句" in build_length_hint("一二三四五六七八九十")    # 10 字
    assert "2-4 句" in build_length_hint("一" * 30)
    assert "3-6 句" in build_length_hint("一" * 31)


def test_length_upgrades_on_intense_emotion():
    """高唤醒情绪上调一档，封顶 3-6 句。"""
    assert "2-4 句" in build_length_hint("你好", "sad")        # 0 → 1
    assert "3-6 句" in build_length_hint("一" * 20, "angry")   # 1 → 2
    assert "3-6 句" in build_length_hint("一" * 50, "fear")    # 2 → 2（封顶）
    # 非激烈情绪不上调
    assert "1-2 句" in build_length_hint("你好", "neutral")
    assert "1-2 句" in build_length_hint("你好", "happy")


def test_dynamic_length_off_zero_regression():
    """未开 dynamic_length → 提示词里没有长度块（零回归）。"""
    base = (
        '{"name":"A","post_history_instructions":"风格",'
        '"prompt_config":{"footer_fields":["post_history_instructions"]}}'
    )
    # 在 prompt_config 的闭合花括号前插入开关（base 结尾是 "]}}"）
    on = base[:-2] + ',"dynamic_length":true}}'
    off = build_roleplay_prompt(card_json=base, fallback_prompt=None, default_card=None, message="你好", chunks=[])
    enabled = build_roleplay_prompt(card_json=on, fallback_prompt=None, default_card=None, message="你好", chunks=[])
    assert "本轮长度" not in off
    assert "本轮长度" in enabled


def test_length_hint_overrides_footer():
    """动态长度必须排在 footer 之后，才能覆盖卡内静态的句数要求。"""
    card = (
        '{"name":"A","post_history_instructions":"每条 2-4 句",'
        '"prompt_config":{"footer_fields":["post_history_instructions"],"dynamic_length":true}}'
    )
    prompt = build_roleplay_prompt(
        card_json=card, fallback_prompt=None, default_card=None,
        message="一" * 40, chunks=[],
    )
    assert prompt.index("每条 2-4 句") < prompt.index("本轮长度")


# ===========================================================================
# P1-3 情感节奏（防备层）
# ===========================================================================

LAYERS = {
    "surface": "日常疏离",
    "trigger_topics": ["过去", "身份"],
    "trigger_reaction": "先回避",
    "trust_signals": ["示弱"],
    "trust_reaction": "放下讽刺",
}


def test_pacing_trigger_topic():
    """命中敏感话题 → 叠加 trigger_reaction。"""
    out = resolve_pacing_strategy(LAYERS, "聊聊你的过去", turn_count=0)
    assert out is not None and "日常疏离" in out and "先回避" in out
    assert "放下讽刺" not in out


def test_pacing_trust_after_threshold():
    """未触发且轮次达标 → 叠加 trust_reaction。"""
    out = resolve_pacing_strategy(LAYERS, "今天天气不错", turn_count=6)
    assert out is not None and "日常疏离" in out and "放下讽刺" in out
    assert "先回避" not in out


def test_pacing_trigger_beats_trust():
    """被踩到敏感话题时不会同时敞开心扉——防备优先。"""
    out = resolve_pacing_strategy(LAYERS, "你的身份是什么", turn_count=20)
    assert out is not None and "先回避" in out and "放下讽刺" not in out


def test_pacing_surface_only_early_on():
    """既未触发也未积累信任 → 只有基线姿态。"""
    out = resolve_pacing_strategy(LAYERS, "今天天气不错", turn_count=3)
    assert out == "日常疏离"


def test_pacing_absent_when_unset_zero_regression():
    """未配置 emotional_layers → 零注入。"""
    assert resolve_pacing_strategy(None, "聊聊过去") is None
    assert resolve_pacing_strategy({}, "聊聊过去") is None
    assert build_pacing_block(None) == ""
    card = '{"name":"A","personality":"冷静"}'
    assert "此刻你的姿态" not in build_roleplay_prompt(
        card_json=card, fallback_prompt=None, default_card=None, message="你好", chunks=[]
    )


def test_pacing_injected_into_prompt():
    """配置后本轮注入【此刻你的姿态】块。"""
    card = (
        '{"name":"A","personality":"冷静",'
        '"emotional_layers":{"surface":"日常疏离","trigger_topics":["过去"],'
        '"trigger_reaction":"先回避"}}'
    )
    prompt = build_roleplay_prompt(
        card_json=card, fallback_prompt=None, default_card=None, message="聊聊过去", chunks=[]
    )
    assert "【此刻你的姿态】" in prompt
    assert "先回避" in prompt


def test_emotional_layers_normalization():
    """模型层清洗：未知键丢弃、列表去空白去重、空 dict 保留（区分 None）。"""
    card = CharacterCard.model_validate(
        {
            "name": "A",
            "emotional_layers": {
                "surface": "  日常疏离  ",
                "trigger_topics": ["过去", "过去", "  ", "身份"],
                "unknown_key": "丢弃",
                "trust_signals": "不是列表",
            },
        }
    )
    layers = card.emotional_layers
    assert layers["surface"] == "日常疏离"
    assert layers["trigger_topics"] == ["过去", "身份"]
    assert "unknown_key" not in layers
    assert "trust_signals" not in layers
    # None / 非法 → None（不阻断卡片加载）
    assert CharacterCard.model_validate({"name": "A", "emotional_layers": None}).emotional_layers is None
    assert CharacterCard.model_validate({"name": "A", "emotional_layers": "x"}).emotional_layers is None
    # 空 dict 保留，与 None 区分（供「清空该字段」语义）
    assert CharacterCard.model_validate({"name": "A", "emotional_layers": {}}).emotional_layers == {}


# ===========================================================================
# P1-4 生成后质量自检
# ===========================================================================

def test_quality_identity_violation():
    hits = find_quality_violations("作为AI，我无法回答这个问题。")
    assert [h.kind for h in hits] == ["identity"]


def test_quality_service_tone_tail():
    hits = find_quality_violations("嗯，就这样吧。希望这对你有帮助。")
    assert [h.kind for h in hits] == ["service"]


def test_quality_user_action_format():
    hits = find_quality_violations("*你愣了一下*，没说话。")
    assert [h.kind for h in hits] == ["format"]


def test_quality_clean_reply_no_violations():
    """正常角色口吻不误伤。"""
    for reply in [
        "嗯……这个我说不清。",
        "*她抬了抬眼* 别急着给自己下结论。",
        "难过是很贵的情绪，我把它留给了更值得的事。",
        "",
        None,
    ]:
        assert find_quality_violations(reply) == [], f"不应误伤：{reply!r}"


def test_quality_multiple_kinds_reported_once_each():
    """同类只报一条，不同类可叠加。"""
    hits = find_quality_violations("作为AI，我可以帮你。*你点了点头*。希望这对你有帮助。")
    kinds = [h.kind for h in hits]
    assert kinds == ["identity", "service", "format"]
    assert len(kinds) == len(set(kinds))


def test_quality_retry_hint_empty_when_clean():
    assert quality_retry_hint([]) == ""
    hint = quality_retry_hint(find_quality_violations("作为AI，我不能回答。"))
    assert "出戏了，重写" in hint and "身份出戏" in hint


# ===========================================================================
# 编排层接线：自检重试 + 分层传参
# ===========================================================================

class ScriptedLLM:
    """按脚本顺序返回回复，并记录每次调用的 kwargs。"""

    def __init__(self, replies: list[str]) -> None:
        self._replies = list(replies)
        self.calls: list[dict] = []

    @property
    def model_name(self) -> str:
        return "scripted"

    async def generate(
        self,
        *,
        system: str,
        user: str,
        history=None,
        temperature=None,
        system_blocks=None,
        user_prefix=None,
    ) -> str:
        self.calls.append(
            {
                "system": system,
                "user": user,
                "system_blocks": system_blocks,
                "user_prefix": user_prefix,
            }
        )
        return self._replies.pop(0) if self._replies else "兜底回复。"


def _orch(llm, monkeypatch, **kw) -> ChatOrchestrator:
    """构造编排器，并把请求级 LLM 覆盖固定为注入的桩。

    run()/stream() 内部会调 build_llm_from_config(settings, req.llm) 现取客户端，
    不走构造函数注入的 self._llm，所以必须替换该函数才能用脚本化 LLM 断言调用次数
    与收到的分层参数。
    """
    monkeypatch.setattr(
        orchestrator_module, "build_llm_from_config", lambda settings, override: (llm, False)
    )
    return ChatOrchestrator(
        llm=llm,
        emotion=KeywordEmotionDetector(),
        rag=InMemoryVectorStore(),
        enable_emotion=False,
        **kw,
    )


@pytest.mark.asyncio
async def test_orchestrator_quality_guard_retries(monkeypatch):
    """出戏回复 → 追加重写指令重试，最终采用改写后的回复。"""
    llm = ScriptedLLM(["作为AI，我无法回答这个问题。", "嗯……这个我说不清，别问了。"])
    orch = _orch(llm, monkeypatch, quality_guard_enabled=True, quality_guard_max_retries=2)
    res = await orch.run(ChatRequest(session_id="s", message="你好"))
    assert res.response.reply == "嗯……这个我说不清，别问了。"
    assert len(llm.calls) == 2, "命中出戏应重试一次"
    assert "出戏了，重写" in llm.calls[1]["system"]


@pytest.mark.asyncio
async def test_orchestrator_quality_guard_disabled_no_retry(monkeypatch):
    """关闭自检 → 不产生额外调用（零回归）。"""
    llm = ScriptedLLM(["作为AI，我无法回答这个问题。"])
    orch = _orch(llm, monkeypatch, quality_guard_enabled=False)
    res = await orch.run(ChatRequest(session_id="s", message="你好"))
    assert len(llm.calls) == 1
    assert res.response.reply.startswith("作为AI")


@pytest.mark.asyncio
async def test_orchestrator_quality_guard_capped(monkeypatch):
    """一直出戏也不会无限重试（上限 2 次重写）。"""
    llm = ScriptedLLM(["作为AI-1", "作为AI-2", "作为AI-3", "作为AI-4"])
    orch = _orch(llm, monkeypatch, quality_guard_enabled=True, quality_guard_max_retries=2)
    await orch.run(ChatRequest(session_id="s", message="你好"))
    assert len(llm.calls) == 3, "1 次首生成 + 2 次重写上限"


@pytest.mark.asyncio
async def test_orchestrator_layering_passes_system_blocks(monkeypatch):
    """卡片开启 message_layering → LLM 收到 system_blocks / user_prefix。"""
    card = json.dumps(
        {
            "name": "无名者",
            "personality": "冷静",
            "post_history_instructions": "风格：简短",
            "core_anchors": ["锚一"],
            "prompt_config": {
                "footer_fields": ["post_history_instructions"],
                "message_layering": True,
            },
        },
        ensure_ascii=False,
    )
    llm = ScriptedLLM(["嗯，我在。"])
    orch = _orch(llm, monkeypatch)
    await orch.run(ChatRequest(session_id="s", message="你好", character_card=card))
    call = llm.calls[0]
    assert isinstance(call["system_blocks"], list) and len(call["system_blocks"]) >= 1
    assert "你是无名者" in call["system_blocks"][0]
    assert call["user_prefix"] and "别忘了你是谁" in call["user_prefix"]


@pytest.mark.asyncio
async def test_orchestrator_no_layering_by_default(monkeypatch):
    """默认不分層 → 不传 system_blocks / user_prefix（兼容第三方 LLMPort）。"""
    card = json.dumps({"name": "无名者", "personality": "冷静"}, ensure_ascii=False)
    llm = ScriptedLLM(["嗯，我在。"])
    orch = _orch(llm, monkeypatch)
    await orch.run(ChatRequest(session_id="s", message="你好", character_card=card))
    call = llm.calls[0]
    assert call["system_blocks"] is None and call["user_prefix"] is None
    assert "你是无名者" in call["system"]


# ===========================================================================
# 角色卡数据层：两张卡都带 P1 字段且合法
# ===========================================================================

@pytest.mark.parametrize("path", [CARD_PATH, ASSET_CARD_PATH], ids=["data", "assets"])
def test_character_card_p1_fields(path):
    """P1-2 输出格式写入规则；P1-3 emotional_layers 齐备；P1-1/P1-2 开关已启用。"""
    raw = json.loads(path.read_text(encoding="utf-8"))
    card = CharacterCard.model_validate(raw)

    # P1-2：行为规则与风格指令都定义了 *动作* /（内心独白）格式
    assert "*…*" in card.behavior_rules or "*..." in card.behavior_rules
    assert "（…）" in card.behavior_rules or "(...)" in card.behavior_rules
    assert "（…）" in card.post_history_instructions or "(...)" in card.post_history_instructions
    assert "不写对方的动作" in card.post_history_instructions

    # P1-3：情感层次五要素齐全
    layers = card.emotional_layers
    assert layers, "emotional_layers 应已配置"
    for key in ("surface", "trigger_topics", "trigger_reaction", "trust_signals", "trust_reaction"):
        assert layers.get(key), f"缺少 emotional_layers.{key}"

    # P1-1 / P1-2：开关已在该卡启用
    cfg = PromptConfig.from_any(card.prompt_config)
    assert cfg.message_layering is True
    assert cfg.dynamic_length is True
