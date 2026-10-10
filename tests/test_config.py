"""Settings 配置校验测试：关键数值字段越界应在启动前快速失败。"""
import pytest
from pydantic import ValidationError

from roleplay.config import Settings


@pytest.mark.parametrize(
    "field,value",
    [
        ("llm_temperature", 2.1),
        ("llm_temperature", -0.1),
        ("emotion_llm_timeout", 0.0),
        ("emotion_confidence_threshold", 1.1),
        ("chunk_size", 10),
        ("top_k", 0),
        ("rag_hybrid_alpha", 1.5),
        ("rag_hybrid_candidates", 0),
        ("embed_dim", 8),
        ("memory_retention_days", 0),
        ("longterm_consolidate_every", 0),
        ("profile_extract_every", 0),
        ("profile_top_k", 0),
        ("profile_max_items", 0),
        ("profile_llm_timeout", 0.0),
        ("profile_synonym_threshold", 2.0),
        ("profile_reminder_days", -1),
        ("web_max_results", 0),
        ("max_message_length", 0),
        ("max_tokens_per_reply", 0),
        ("history_summary_threshold", 1),
        ("session_memory_max_chars", -1),
        ("voice_request_timeout", 0.0),
    ],
)
def test_settings_reject_out_of_range(field, value):
    with pytest.raises(ValidationError):
        Settings(**{field: value})


def test_settings_defaults_still_valid():
    s = Settings()
    # 0.8 → 0.6：RAGAS 2.0 评估显示 7B 在 0.8 下倾向"表演"（纯修辞/编造场景），
    # Faithfulness 仅 0.75；0.6 保留角色灵动性同时显著抑制放飞。见 rag-knowledge-audit.md。
    assert s.llm_temperature == 0.6
    assert s.chunk_size == 600
    assert s.static_no_cache is True
    # P0-B：会话历史字符预算（默认 120_000）。依据见 session_memory._CHAR_BUDGET：
    # 40 轮 × 每轮 ~3000 字（云端档 max_tokens=2048）≈ 120k，不误伤正常会话。
    assert s.session_memory_max_chars == 120_000
