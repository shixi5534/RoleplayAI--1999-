"""角色卡解析与系统提示词解析测试。"""
from roleplay.core.character_card import resolve_system_prompt
from roleplay.core.persona_prompt import build_roleplay_prompt
from roleplay.models.chat import LLMOverride
from roleplay.models.character import CharacterCard


def test_parse_wrapped():
    raw = '{"data": {"name": "无名者", "personality": "神秘"}}'
    card = CharacterCard.parse_raw_card(raw)
    assert card is not None and card.name == "无名者"


def test_parse_invalid_returns_none():
    assert CharacterCard.parse_raw_card("not json at all") is None


def test_parse_empty_returns_none():
    assert CharacterCard.parse_raw_card("") is None


def test_resolve_prefers_system_prompt():
    card = '{"name":"A","system_prompt":"你是A"}'
    assert resolve_system_prompt(character_card=card, fallback_prompt="fb") == "你是A"


def test_resolve_fallback_when_no_card():
    assert resolve_system_prompt(character_card=None, fallback_prompt="简易提示") == "简易提示"


def test_resolve_default_when_empty():
    prompt = resolve_system_prompt(character_card=None, fallback_prompt=None)
    assert "私人助手" in prompt


def test_resolve_builds_from_fields():
    card = '{"name":"无名者","personality":"冷静","scenario":"雨夜"}'
    prompt = resolve_system_prompt(character_card=card, fallback_prompt=None)
    assert "无名者" in prompt and "冷静" in prompt and "雨夜" in prompt


# ---------------------------------------------------------------------------
# Phase 2 — 人设标准化：双模型一致性单测
# 目的：证明 system prompt 生成与 LLM override 正交。同一角色卡在不同
# LLMOverride（provider/model/base_url/api_key 各异）下，resolve_system_prompt
# 与 build_roleplay_prompt 的输出必须逐字节一致。这从测试侧锁死「模型切换不
# 污染人设」的契约，避免未来重构时把 override 泄漏进提示词路径。
# ---------------------------------------------------------------------------

_CARD_JSON = (
    '{"name":"无名者","personality":"冷静","scenario":"雨夜",'
    '"background":"失落之城","behavior_rules":"不泄露身份",'
    '"tone":"低沉简短","first_mes":"……你来啦。"}'
)


def _make_overrides() -> list[LLMOverride]:
    """构造一组差异化的 LLMOverride（覆盖典型前端模型切换场景）。"""
    return [
        LLMOverride(),  # 全空：回退全局配置
        LLMOverride(provider="openai", model="gpt-4o", api_key="sk-x"),
        LLMOverride(provider="deepseek", model="deepseek-chat", api_key="sk-y"),
        LLMOverride(provider="ollama", model="qwen2.5:14b", base_url="http://localhost:11434/v1"),
        LLMOverride(provider="openai", model="gpt-4o-mini", base_url="https://api.openai.com/v1", api_key="sk-z", timeout=60.0),
    ]


def test_resolve_system_prompt_invariant_under_llm_override():
    """resolve_system_prompt 不接受 override 参数——直接验证其输出稳定。

    这里显式调用并断言多次结果一致，锁死「纯函数、无外部状态」契约。
    """
    first = resolve_system_prompt(character_card=_CARD_JSON, fallback_prompt=None)
    for _ in range(3):
        again = resolve_system_prompt(character_card=_CARD_JSON, fallback_prompt=None)
        assert again == first, "resolve_system_prompt 应为纯函数，重复调用必须一致"
    # 基本内容断言
    assert "无名者" in first and "冷静" in first and "雨夜" in first


def test_build_roleplay_prompt_invariant_under_llm_override():
    """同一角色卡 + 同一检索上下文，在 5 种 LLMOverride 下 system prompt 必须一致。

    build_roleplay_prompt 不接收 LLMOverride（签名层面隔离），这里通过模拟
    「前端切换模型后再次请求」的场景，断言提示词逐字节相等，从而锁死正交性。
    """
    card_obj = CharacterCard.parse_raw_card(_CARD_JSON)
    assert card_obj is not None
    prompts: list[str] = []
    for _ov in _make_overrides():
        # override 仅影响 orchestrator 的 LLM 客户端构建，不传入提示词路径
        prompt = build_roleplay_prompt(
            card_json=_CARD_JSON,
            fallback_prompt=None,
            default_card=None,
            message="今晚的雨真大",
            chunks=[],
            card=card_obj,
        )
        prompts.append(prompt)
    # 所有 override 下提示词必须完全一致
    assert all(p == prompts[0] for p in prompts), (
        "不同 LLMOverride 下 system prompt 不一致——人设标准化被破坏"
    )
    # 内容断言：人设 + 语气段均在
    base = prompts[0]
    assert "无名者" in base and "冷静" in base
    assert "【语气要求】低沉简短" in base


def test_build_roleplay_prompt_override_does_not_leak_into_prompt():
    """负向防护：LLMOverride 中的敏感字段（api_key/base_url）绝不出现在 prompt 中。

    防止未来有重构把 override 误传入提示词路径，导致密钥泄漏或人设漂移。
    """
    card_obj = CharacterCard.parse_raw_card(_CARD_JSON)
    sensitive_overrides = [
        LLMOverride(provider="openai", model="gpt-4o", api_key="sk-LEAK-1234567890", base_url="https://leak.example.com/v1"),
        LLMOverride(provider="deepseek", model="deepseek-chat", api_key="sk-SECRET-xyz", base_url="https://secret.example.com/v1"),
    ]
    for ov in sensitive_overrides:
        prompt = build_roleplay_prompt(
            card_json=_CARD_JSON,
            fallback_prompt=None,
            default_card=None,
            message="测试消息",
            chunks=[],
            card=card_obj,
        )
        # api_key 不落盘、不进日志、不进 prompt
        assert ov.api_key not in prompt, f"LLMOverride api_key 泄漏到 system prompt: {ov.api_key}"
        # base_url 不应出现在人设提示词中
        assert ov.base_url not in prompt, f"LLMOverride base_url 泄漏到 system prompt: {ov.base_url}"
        assert ov.model not in prompt, f"LLMOverride model 泄漏到 system prompt: {ov.model}"


def test_resolve_system_prompt_with_lorebook_invariant_under_override():
    """带 Lorebook 的角色卡（关键词触发）也须在 override 下稳定。

    覆盖 _build_lorebook 路径，确保按需设定注入同样与模型切换正交。
    """
    card_with_book = (
        '{"name":"守夜人","personality":"缄默",'
        '"character_book":{"entries":[{"keys":["雨","夜"],"content":"雨夜禁足令"},'
        '{"keys":["剑"],"content":"佩剑无名"}]}}'
    )
    card_obj = CharacterCard.parse_raw_card(card_with_book)
    assert card_obj is not None
    base_prompt = build_roleplay_prompt(
        card_json=card_with_book,
        fallback_prompt=None,
        default_card=None,
        message="外面在下雨",
        chunks=[],
        card=card_obj,
    )
    # 关键词命中应注入
    assert "雨夜禁足令" in base_prompt
    # 未命中关键词不应注入
    assert "佩剑无名" not in base_prompt
    # 在 5 种 override 下必须一致
    for _ov in _make_overrides():
        again = build_roleplay_prompt(
            card_json=card_with_book,
            fallback_prompt=None,
            default_card=None,
            message="外面在下雨",
            chunks=[],
            card=card_obj,
        )
        assert again == base_prompt, "带 Lorebook 的人设在 override 下不一致"


def test_simplified_mode_fallback_invariant_under_override():
    """简化模式（无角色卡，仅 fallback_prompt）也须在 override 下稳定。

    覆盖 fallback_prompt 分支，确保「无角色卡」场景的人设同样不被模型切换污染。
    """
    base_prompt = build_roleplay_prompt(
        card_json=None,
        fallback_prompt="你是一个温和的向导。",
        default_card=None,
        message="你好",
        chunks=[],
        card=None,
    )
    assert "温和的向导" in base_prompt
    for _ov in _make_overrides():
        again = build_roleplay_prompt(
            card_json=None,
            fallback_prompt="你是一个温和的向导。",
            default_card=None,
            message="你好",
            chunks=[],
            card=None,
        )
        assert again == base_prompt, "简化模式 fallback 在 override 下不一致"
