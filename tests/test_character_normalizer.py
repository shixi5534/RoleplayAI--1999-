"""角色设定标准化模块测试。

覆盖三层：
1. 纯函数层：normalize_character_text 的空白/标点/列表/幂等契约；
2. 模型层：CharacterCard / CharacterUpsert 字段级 validator 兜底；
3. 仓库层：CharacterStore.create/update 自动标准化（API 链路入口）。
"""
import pytest

from roleplay.core.character_normalizer import (
    normalize_character_text,
    normalize_card_texts,
    normalize_single_line,
)
from roleplay.core.knowledge.character_store import CharacterStore, _slug
from roleplay.models.character import CharacterCard, CharacterUpsert


# ---------------------------------------------------------------------------
# 1) 纯函数层
# ---------------------------------------------------------------------------

class TestNormalizePure:
    def test_none_and_blank_are_empty(self):
        assert normalize_character_text(None, "personality") == ""
        assert normalize_character_text("", "personality") == ""
        assert normalize_character_text("  　  ", "personality") == ""

    def test_fullwidth_space_to_halfwidth(self):
        out = normalize_character_text("冷静　果断", "personality")
        assert out == "冷静 果断"

    def test_inline_whitespace_collapse(self):
        out = normalize_character_text("  冷静    果断  ", "personality")
        assert out == "冷静 果断"

    def test_newline_surrounding_whitespace(self):
        out = normalize_character_text("冷静  \n  果断", "personality")
        assert out == "冷静\n果断"

    def test_ascii_punct_to_cn(self):
        out = normalize_character_text("冷静,果断;话少", "personality")
        assert out == "冷静，果断；话少"

    def test_repeat_punct_collapse(self):
        out = normalize_character_text("真的吗？？！！", "personality")
        assert "？？" not in out and "！！" not in out

    def test_trailing_punct_cleaned(self):
        out = normalize_character_text("冷静、果断，", "personality")
        assert not out.endswith("，") and not out.endswith("、")

    def test_inline_list_expanded(self):
        out = normalize_character_text("1) 冷静  2) 果断  3) 话少", "behavior_rules")
        assert out == "1. 冷静\n2. 果断\n3. 话少"

    def test_cn_numeral_list_expanded(self):
        out = normalize_character_text("一、冷静 二、果断 三、话少", "behavior_rules")
        assert "1. 冷静" in out and "2. 果断" in out and "3. 话少" in out

    def test_single_item_list_not_touched(self):
        out = normalize_character_text("1) 冷静", "behavior_rules")
        # 单条目不强制展开，但条目格式统一
        assert "冷静" in out

    def test_light_field_does_not_expand_list(self):
        # first_mes 是对话文本，不得把数字当成列表展开
        out = normalize_character_text("1) 你来啦 2) 今晚去哪", "first_mes")
        assert "1) 你来啦" in out

    def test_idempotent(self):
        for src, f in [
            ("  冷静　,果断；　话少  ", "personality"),
            ("1) 冷静  2) 果断  3) 话少", "behavior_rules"),
            ("真实吗？？！！   ", "first_mes"),
        ]:
            once = normalize_character_text(src, f)
            twice = normalize_character_text(once, f)
            assert twice == once, f"幂等失败: {src!r} -> {once!r}"

    def test_normalize_single_line(self):
        assert normalize_single_line("多行\n文本") == "多行 文本"
        assert normalize_single_line("  a,b  ") == "a，b"

    def test_normalize_card_texts_preserves_non_text(self):
        data = {
            "name": "  测试  ",
            "behavior_rules": "1) a  2) b",
            "tts_speed": 1.2,
            "character_book": {"entries": []},
            "knowledge_scope": ["events"],
        }
        out = normalize_card_texts(data)
        assert out["name"] == "测试"
        assert out["behavior_rules"] == "1. a\n2. b"
        assert out["tts_speed"] == 1.2
        assert out["character_book"] == {"entries": []}
        assert out["knowledge_scope"] == ["events"]
        # 入参未被就地修改
        assert data["name"] == "  测试  "


# ---------------------------------------------------------------------------
# 2) 模型层 validator
# ---------------------------------------------------------------------------

class TestModelValidators:
    def test_character_card_auto_cleans(self):
        card = CharacterCard(
            name="  无名者  ",
            personality="  冷静　,果断  ",
            behavior_rules="1) 不泄露身份  2) 守口如瓶",
        )
        assert card.name == "无名者"
        assert card.personality == "冷静，果断"
        assert card.behavior_rules == "1. 不泄露身份\n2. 守口如瓶"

    def test_character_card_system_prompt_none_preserved(self):
        card = CharacterCard(name="A", system_prompt=None)
        assert card.system_prompt is None
        card2 = CharacterCard(name="A", system_prompt="   ")
        assert card2.system_prompt is None

    def test_upsert_blank_text_becomes_empty(self):
        up = CharacterUpsert(name="  ", personality="   ")
        # name 空白 → 空串（API 层校验 name 非空会拒绝）
        assert up.name == ""
        assert up.personality == ""

    def test_upsert_blank_system_prompt_becomes_none(self):
        up = CharacterUpsert(system_prompt="   ")
        assert up.system_prompt is None

    def test_upsert_cleans_text_fields(self):
        up = CharacterUpsert(
            behavior_rules="1) a  2) b",
            tone="  低沉、简短  ",
        )
        assert up.behavior_rules == "1. a\n2. b"
        # 顿号是中文标准列举标点，规范化后保留
        assert up.tone == "低沉、简短"


# ---------------------------------------------------------------------------
# 3) 仓库层自动标准化
# ---------------------------------------------------------------------------

@pytest.fixture
def store(tmp_path):
    return CharacterStore(
        persist_dir=tmp_path / "chars",
        seed_card_path=None,  # 不注入种子，测纯 CRUD
    )


class TestStoreAutoNormalize:
    def test_create_normalizes(self, store):
        cid = store.create(
            {
                "name": "  冷面  医生  ",
                "personality": "  冷静,果断　话少  ",
                "behavior_rules": "1) 不透露病人隐私  2) 每次问诊先听",
            }
        )
        card = store.get(cid)
        assert card is not None
        assert card.name == "冷面 医生"
        assert "冷静，果断" in card.personality
        assert card.behavior_rules == "1. 不透露病人隐私\n2. 每次问诊先听"

    def test_update_normalizes_partial(self, store):
        cid = store.create({"name": "A", "personality": "old"})
        store.update(cid, {"behavior_rules": "1) x  2) y"})
        card = store.get(cid)
        assert card is not None
        assert card.behavior_rules == "1. x\n2. y"
        # 未更新字段保留原值
        assert card.personality == "old"

    def test_create_blank_name_falls_back(self, store):
        cid = store.create({"name": "   ", "personality": "x"})
        card = store.get(cid)
        assert card is not None and card.name == "新角色"

    def test_slug_with_whitespace(self):
        assert _slug("  无名 者  ") == "无名_者"
