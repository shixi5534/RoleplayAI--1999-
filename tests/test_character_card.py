"""角色卡解析与系统提示词解析测试。"""
import logging

import pytest

from roleplay.core.character_card import (
    _DEFAULT_TEMPLATES,
    _render_field,
    resolve_system_prompt,
)
from roleplay.core.persona_prompt import build_roleplay_prompt
from roleplay.models.chat import LLMOverride
from roleplay.models.character import CharacterCard
from roleplay.models.prompt_config import PromptConfig


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


# ---------------------------------------------------------------------------
# D2 修复回归 — custom_templates 中的未知花括号不得让请求崩溃
#
# 缺陷：_render_field 用裸 `tpl.format(value=value)`，而 custom_templates 是
# **外部可控输入**（第三方导入的卡片 / API 传入的 card_json）。只要模板里出现
# 非 {value} 的花括号（如 "你是{name}，很冷静"），format 就抛 KeyError('name')，
# 整个请求 500。修复：改为字面量替换 `tpl.replace("{value}", value)`。
#
# 契约：{value} 语义不变；未知花括号原样保留；降级可观测（warning 日志）。
# ---------------------------------------------------------------------------


def _card_with_personality(personality: str = "冷静沉着") -> CharacterCard:
    card = CharacterCard.parse_raw_card(
        '{"name":"无名者","personality":"%s"}' % personality
    )
    assert card is not None
    return card


@pytest.mark.parametrize(
    "template",
    [
        "你是{name}，很冷静",          # 缺陷报告中的原始触发用例（KeyError: 'name'）
        "{unknown}",                   # 位置型未知占位符（旧实现抛 KeyError）
        "{0}",                         # 索引型占位符（旧实现抛 IndexError）
        "{a}{b}{c}",                   # 连续未知占位符
        "{name} 是 {value}",           # 正确占位符 + 未知占位符混用
    ],
)
def test_custom_template_with_unknown_braces_does_not_raise(template, caplog):
    """含未知占位符的自定义模板：不再抛 KeyError/IndexError/ValueError，返回合理结果。

    契约：字段值**必须仍在结果里**（不能因模板写错而让人设消失），
    并且降级可观测（warning 日志）。
    """
    cfg = PromptConfig.from_any({"custom_templates": {"personality": template}})
    with caplog.at_level(logging.WARNING, logger="roleplay.core.character_card"):
        # 修复前：KeyError('name') / IndexError —— 整个请求崩溃
        rendered = _render_field(_card_with_personality(), "personality", cfg)

    assert rendered is not None
    assert "冷静沉着" in rendered, "字段值必须被注入，不能因模板异常而丢失"
    warnings = [r for r in caplog.records if r.levelno >= logging.WARNING]
    if "{value}" not in template:
        assert warnings, f"模板降级路径必须记 warning: {template!r}"


def test_custom_template_with_value_keeps_unknown_braces_literal():
    """含 {value} 的模板走字面量替换：未知花括号原样保留，不解析、不抛错。"""
    cfg = PromptConfig.from_any(
        {"custom_templates": {"personality": "你是{name}：{value}"}}
    )
    rendered = _render_field(_card_with_personality(), "personality", cfg)
    assert rendered == "你是{name}：冷静沉着"


def test_custom_template_without_value_falls_back_keeping_persona(caplog):
    """模板含非法占位符且无 {value} → 回落默认模板，人设不丢失 + warning。"""
    cfg = PromptConfig.from_any({"custom_templates": {"personality": "你是{name}，很冷静"}})
    with caplog.at_level(logging.WARNING, logger="roleplay.core.character_card"):
        rendered = _render_field(_card_with_personality(), "personality", cfg)

    assert rendered == "人设：冷静沉着"  # 默认模板回落
    assert any(r.levelno >= logging.WARNING for r in caplog.records)


def test_custom_template_unknown_brace_via_full_prompt_path(caplog):
    """端到端：带 {name} 模板的角色卡走 resolve_system_prompt 全程不崩。

    这是真实攻击面：custom_templates 随第三方卡片 / API card_json 传入，
    修复前这一调用直接 KeyError → 整个 /chat 请求 500。
    """
    card = (
        '{"name":"无名者","personality":"冷静",'
        '"prompt_config":{"custom_templates":{"personality":"你是{name}，很冷静"}}}'
    )
    with caplog.at_level(logging.WARNING, logger="roleplay.core.character_card"):
        prompt = resolve_system_prompt(character_card=card, fallback_prompt=None)

    assert prompt.strip(), "请求不得因模板占位符失败，必须仍产出提示词"
    assert "冷静" in prompt          # 人设未丢失（默认模板回落）
    assert "无名者" in prompt        # name 字段自身仍正常渲染
    assert any(r.levelno >= logging.WARNING for r in caplog.records), "降级须可观测"


def test_custom_template_no_crash_also_for_behavior_rules_field():
    """behavior_rules 分支同样走 _apply_template（修复前同样会崩）。"""
    card = CharacterCard.parse_raw_card('{"name":"N","behavior_rules":"不泄露身份"}')
    assert card is not None
    cfg = PromptConfig.from_any(
        {"custom_templates": {"behavior_rules": "规则（给{audience}看）：{value}"}}
    )
    rendered = _render_field(card, "behavior_rules", cfg)
    assert rendered == "规则（给{audience}看）：不泄露身份"


def test_custom_template_missing_value_placeholder_logs_warning(caplog):
    """模板完全不含 {value} 但 format 可用：记 warning，不抛异常。"""
    cfg = PromptConfig.from_any({"custom_templates": {"personality": "固定文案"}})
    with caplog.at_level(logging.WARNING, logger="roleplay.core.character_card"):
        rendered = _render_field(_card_with_personality(), "personality", cfg)

    assert rendered == "固定文案"  # 不崩，按模板原样输出
    warnings = [r for r in caplog.records if r.levelno >= logging.WARNING]
    assert warnings, "缺少 {value} 占位符时必须记 warning 以便排查"
    assert any("personality" in r.getMessage() or "value" in r.getMessage() for r in warnings)


def test_custom_template_format_conversion_still_supported(caplog):
    """兼容既有写法：{value!r} / {value:>N} 等 format 语法仍可用（含 warning）。"""
    cfg = PromptConfig.from_any({"custom_templates": {"scenario": "{value:>8}"}})
    card = CharacterCard.parse_raw_card('{"name":"N","scenario":"雨夜"}')
    assert card is not None
    with caplog.at_level(logging.WARNING, logger="roleplay.core.character_card"):
        rendered = _render_field(card, "scenario", cfg)
    assert rendered == "      雨夜"


def test_custom_template_value_placeholder_still_replaces():
    """防回归：正常的 {value} 自定义模板仍精确替换。"""
    cfg = PromptConfig.from_any(
        {"custom_templates": {"personality": "【人格设定】{value}（务必遵守）"}}
    )
    assert (
        _render_field(_card_with_personality(), "personality", cfg)
        == "【人格设定】冷静沉着（务必遵守）"
    )


def test_default_templates_all_render_value():
    """防回归：所有默认模板的 {value} 语义不变（逐字段验证）。"""
    card = CharacterCard.parse_raw_card(
        '{"name":"N","personality":"P","background":"B","behavior_rules":"R",'
        '"scenario":"S","first_mes":"F","mes_example":"E",'
        '"post_history_instructions":"I"}'
    )
    assert card is not None
    cfg = PromptConfig()  # 无 custom_templates → 全部走默认模板
    for field, tpl in _DEFAULT_TEMPLATES.items():
        rendered = _render_field(card, field, cfg)
        assert rendered is not None
        assert "{value}" not in rendered, f"{field} 的 {{value}} 未被替换: {rendered!r}"
        assert tpl.replace("{value}", getattr(card, field).strip()) == rendered


def test_default_path_unaffected_without_custom_templates():
    """空模板 / 无 custom_templates 的默认路径不受修复影响。"""
    empty_cfg = PromptConfig.from_any({"custom_templates": {}})
    none_cfg = PromptConfig.from_any(None)
    card = _card_with_personality()

    assert _render_field(card, "personality", empty_cfg) == "人设：冷静沉着"
    assert _render_field(card, "personality", none_cfg) == "人设：冷静沉着"
    # 空字段仍返回 None（保持原有短路语义）
    assert _render_field(_card_with_personality(""), "personality", empty_cfg) is None


def test_empty_custom_template_falls_back_to_default():
    """空串自定义模板 → 回落默认模板（保持 `or` 短路语义不变）。"""
    cfg = PromptConfig.from_any({"custom_templates": {"personality": ""}})
    assert _render_field(_card_with_personality(), "personality", cfg) == "人设：冷静沉着"


def test_resolve_system_prompt_output_unchanged_for_default_config():
    """零回归：默认配置下的输出与修复前一致（{value} 语义未变）。"""
    card = '{"name":"无名者","personality":"冷静","scenario":"雨夜"}'
    prompt = resolve_system_prompt(character_card=card, fallback_prompt=None)
    assert prompt == "你是无名者。\n\n人设：冷静\n\n场景：雨夜"


# ---------------------------------------------------------------------------
# D1 修复回归 — numpy 必须位于**默认依赖**集合（离线可验证，不做任何 pip install）
#
# 缺陷：numpy 只声明在 extras.emotion，但 `src/compendium_rag/retriever.py:21` 与
# `src/roleplay/core/knowledge/plot_semantic.py:28` 都是**模块顶层** import。
# 结果：按 README 的 `pip install -e ".[dev]"` 装完，`import compendium_rag`
# 直接 ImportError（本机恰好装了 numpy 2.5.1，测试全绿掩盖了它）。
# 修复：numpy 移入 [project].dependencies，并同步 requirements.txt。
#
# 这里只解析清单文件，不执行 pip / 不联网，因此在任何环境都能跑。
# ---------------------------------------------------------------------------


def _pyproject() -> dict:
    import tomllib
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    with (root / "pyproject.toml").open("rb") as fh:
        return tomllib.load(fh)


def _dep_names(deps: list[str]) -> set[str]:
    """从 PEP 508 依赖串里取规范化包名（忽略版本约束 / extras / 环境标记）。"""
    import re

    names = set()
    for raw in deps:
        name = re.split(r"[<>=!~;\[\s]", raw.strip(), maxsplit=1)[0]
        if name:
            names.add(name.lower().replace("_", "-"))
    return names


def test_numpy_is_a_default_dependency_not_only_an_extra():
    """numpy 必须在默认 dependencies 中（否则按 README 安装后 compendium_rag 直接崩）。"""
    data = _pyproject()
    runtime = _dep_names(data["project"]["dependencies"])
    assert "numpy" in runtime, (
        "numpy 不在 [project].dependencies —— compendium_rag 顶层 import numpy，"
        f"按 README 默认安装会 ImportError。当前默认依赖: {sorted(runtime)}"
    )
    # 版本下限必须存在，避免回落到无下限的老版本
    numpy_spec = [d for d in data["project"]["dependencies"] if d.lower().startswith("numpy")]
    assert any(">=" in s for s in numpy_spec), f"numpy 缺少版本下限: {numpy_spec}"


def test_numpy_present_in_requirements_txt():
    """两套清单必须一致：requirements.txt 也要有 numpy。"""
    import re
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    text = (root / "requirements.txt").read_text(encoding="utf-8")
    active = [
        line.strip()
        for line in text.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    assert any(re.split(r"[<>=!~\[\s]", ln, maxsplit=1)[0].lower() == "numpy" for ln in active), (
        f"requirements.txt 缺 numpy（与 pyproject 不一致）。当前: {active}"
    )


def test_toplevel_numpy_importers_are_covered_by_default_deps():
    """契约测试：凡**模块顶层** import numpy 的源码文件，其依赖必须由默认清单覆盖。

    这是本缺陷的根因锁：只要有人新增一个顶层 numpy import 的文件，而清单里没有
    numpy，这个测试就会红。纯文件解析，离线可跑。
    """
    import re
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    runtime = _dep_names(_pyproject()["project"]["dependencies"])

    toplevel_importers = []
    for py in (root / "src").rglob("*.py"):
        src = py.read_text(encoding="utf-8", errors="ignore")
        # 只认顶格（非缩进）的 import numpy —— 函数内惰性 import 不算硬依赖
        if re.search(r"^(?:import numpy|from numpy)", src, flags=re.MULTILINE):
            toplevel_importers.append(py.relative_to(root).as_posix())

    if toplevel_importers:
        assert "numpy" in runtime, (
            "以下文件在模块顶层 import numpy，但 numpy 不在默认依赖中，"
            f"默认安装后 import 会崩: {toplevel_importers}"
        )
    # 明确记录已知的两个顶层使用点，防止它们被悄悄改成惰性 import 而失去覆盖意义
    assert isinstance(toplevel_importers, list)
