"""默认角色卡仓库：加载内置角色，作为请求未携带角色卡时的兜底。

「深化单角色人设」的核心 —— 之前前端从不发送 character_card，
导致 LLM 一直用默认「乐于助人的私人助手」提示词，无名者的人设从未注入。
现在：请求无卡 → 使用此处加载的内置角色卡（位于 assets/characters/）。
"""
from functools import lru_cache
from pathlib import Path

from ..models.character import CharacterCard

DEFAULT_CARD_PATH = (
    Path(__file__).resolve().parent.parent
    / "assets"
    / "characters"
    / "wu_ming_zhe.json"
)


class CharacterRepo:
    def __init__(self, card_path: Path | None = DEFAULT_CARD_PATH) -> None:
        self._path = card_path

    @property
    def card_json(self) -> str | None:
        """角色卡原始 JSON（可能含完整 CharacterCard V2 结构）。"""
        if self._path and self._path.is_file():
            try:
                return self._path.read_text(encoding="utf-8")
            except OSError:
                return None
        return None

    def card(self) -> CharacterCard | None:
        raw = self.card_json
        return CharacterCard.parse_raw_card(raw) if raw else None


@lru_cache(maxsize=1)
def get_default_character_repo() -> CharacterRepo:
    return CharacterRepo()
