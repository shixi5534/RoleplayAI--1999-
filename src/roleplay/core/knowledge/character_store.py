"""多角色人设仓库：CRUD + 激活 + 人设同步到知识库。

- 每个角色一个 JSON 文件，存于 characters_dir；另用 _active.json 记录当前激活角色。
- 启动时若目录为空，则把内置默认角色卡（无名者）作为首个种子角色写入。
- 任意增删改/切换后，自动把所有人设重新嵌入知识库 persona 命名空间，
  使检索能「按当前上下文召回相关人设」，维持角色一致性（需求 1 + 5）。

设计要点：纯文件持久化、线程安全、对非法 JSON 容错。
"""
from __future__ import annotations

import json
import logging
import re
import threading
from pathlib import Path
from typing import Any, List

from ...config import Settings, get_settings
from ..character_repo import DEFAULT_CARD_PATH
from ..character_normalizer import normalize_card_texts
from ..rag.base import VectorStore
from ...models.character import CharacterCard

logger = logging.getLogger(__name__)

_PERSONA_NS = "persona"


def _slug(name: str) -> str:
    s = re.sub(r"[^A-Za-z0-9_\u4e00-\u9fff]+", "_", (name or "char").strip().lower())
    s = s.strip("_") or "char"
    return s[:48]


class CharacterStore:
    def __init__(
        self,
        persist_dir: str | Path | None = None,
        seed_card_path: str | Path | None = DEFAULT_CARD_PATH,
        settings: Settings | None = None,
    ) -> None:
        s = settings or get_settings()
        self._dir = Path(persist_dir or s.characters_dir)
        self._seed = Path(seed_card_path) if seed_card_path else None
        self._lock = threading.RLock()
        self._chars: dict[str, CharacterCard] = {}
        self._active: str | None = None
        self._load()

    # ── 加载 / 持久化 ──
    def _load(self) -> None:
        try:
            self._dir.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass
        try:
            for f in self._dir.glob("*.json"):
                if f.name == "_active.json":
                    continue
                try:
                    card = CharacterCard.parse_raw_card(f.read_text(encoding="utf-8"))
                    if card:
                        self._chars[f.stem] = card
                except Exception:  # noqa: BLE001
                    continue
        except OSError:
            pass
        if not self._chars and self._seed and self._seed.is_file():
            raw = self._seed.read_text(encoding="utf-8")
            card = CharacterCard.parse_raw_card(raw)
            if card:
                self._chars["wu_ming_zhe"] = card
                self._save_char("wu_ming_zhe", card)
                logger.info("角色仓库：已用内置默认角色卡作为种子")
        self._active = self._read_active() or (
            next(iter(self._chars)) if self._chars else None
        )

    def _save_char(self, cid: str, card: CharacterCard) -> None:
        try:
            self._dir.joinpath(f"{cid}.json").write_text(
                card.model_dump_json(indent=2), encoding="utf-8"
            )
        except OSError as exc:
            logger.warning("保存角色 %s 失败：%s", cid, exc)

    def _read_active(self) -> str | None:
        try:
            p = self._dir / "_active.json"
            if p.is_file():
                return json.loads(p.read_text(encoding="utf-8")).get("active")
        except (OSError, ValueError, TypeError):
            pass
        return None

    def _write_active(self) -> None:
        try:
            self._dir.joinpath("_active.json").write_text(
                json.dumps({"active": self._active}, ensure_ascii=False),
                encoding="utf-8",
            )
        except OSError:
            pass

    # ── 查询 ──
    def list(self) -> List[dict]:
        out: List[dict] = []
        for cid, c in self._chars.items():
            out.append(
                {
                    "id": cid,
                    "name": c.name,
                    "description": c.description,
                    "active": cid == self._active,
                }
            )
        return out

    def get(self, cid: str) -> CharacterCard | None:
        return self._chars.get(cid)

    def get_active(self) -> CharacterCard | None:
        return self._chars.get(self._active) if self._active else None

    def get_active_id(self) -> str | None:
        return self._active

    def to_json(self, cid: str) -> str | None:
        c = self._chars.get(cid)
        return c.model_dump_json(indent=2) if c else None

    # ── 写操作 ──
    def create(self, payload: dict) -> str:
        name = (payload.get("name") or "新角色").strip() or "新角色"
        cid = _slug(name)
        with self._lock:
            base, i = cid, 1
            while cid in self._chars:
                cid = f"{base}_{i}"
                i += 1
            card = self._build_card(payload)
            self._chars[cid] = card
            self._save_char(cid, card)
            if self._active is None:
                self._active = cid
                self._write_active()
        return cid

    def update(self, cid: str, payload: dict) -> bool:
        with self._lock:
            if cid not in self._chars:
                return False
            card = self._build_card(payload, base=self._chars[cid])
            self._chars[cid] = card
            self._save_char(cid, card)
        return True

    def delete(self, cid: str) -> bool:
        with self._lock:
            if cid not in self._chars:
                return False
            if len(self._chars) <= 1:
                raise ValueError("至少保留一个角色，无法删除最后一个")
            self._chars.pop(cid, None)
            try:
                self._dir.joinpath(f"{cid}.json").unlink(missing_ok=True)
            except OSError:
                pass
            if self._active == cid:
                self._active = next(iter(self._chars))
                self._write_active()
        return True

    def set_active(self, cid: str) -> bool:
        with self._lock:
            if cid not in self._chars:
                return False
            self._active = cid
            self._write_active()
        return True

    @staticmethod
    def _build_card(payload: dict, base: CharacterCard | None = None) -> CharacterCard:
        # 自动标准处理：所有文本字段统一清洗（空白/标点/列表结构化），
        # 覆盖 create/update 全部入口（API、脚本、种子加载）。
        payload = normalize_card_texts(payload)
        fields = {
            "name": payload.get("name") or (base.name if base else "新角色"),
            "description": payload.get("description", base.description if base else ""),
            "personality": payload.get("personality", base.personality if base else ""),
            "scenario": payload.get("scenario", base.scenario if base else ""),
            "background": payload.get("background", base.background if base else ""),
            "behavior_rules": payload.get(
                "behavior_rules", base.behavior_rules if base else ""
            ),
            "behavior_rules_structured": payload.get(
                "behavior_rules_structured",
                base.behavior_rules_structured if base else None,
            ),
            "prompt_config": payload.get(
                "prompt_config", base.prompt_config if base else None
            ),
            "tone": payload.get("tone", base.tone if base else ""),
            "knowledge_scope": payload.get(
                "knowledge_scope", base.knowledge_scope if base else None
            ),
            "first_mes": payload.get("first_mes", base.first_mes if base else ""),
            "mes_example": payload.get("mes_example", base.mes_example if base else ""),
            "post_history_instructions": payload.get(
                "post_history_instructions",
                base.post_history_instructions if base else "",
            ),
            "system_prompt": payload.get("system_prompt", base.system_prompt if base else None),
            "character_book": payload.get(
                "character_book", base.character_book if base else None
            ),
            # 四期扩展：语音人设字段映射
            "voice_id": payload.get("voice_id", base.voice_id if base else ""),
            "tts_speed": payload.get("tts_speed", base.tts_speed if base else 1.0),
            "tts_pitch": payload.get("tts_pitch", base.tts_pitch if base else 1.0),
            "tts_volume": payload.get("tts_volume", base.tts_volume if base else 1.0),
        }
        return CharacterCard(**fields)

    # ── 人设同步到知识库（检索用） ──
    def sync_persona_to_kb(self, kb: VectorStore) -> int:
        """把所有人设重建嵌入到知识库 persona 命名空间。返回写入条数。

        Chroma / 落盘 KnowledgeBase 的 add/clear 均为同步阻塞调用：
        - API 层（characters.py）已用 asyncio.to_thread 卸载到线程池；
        - 应用启动期（factory.py）在事件循环之外直接调用本方法，无阻塞问题。
        因此本方法保持同步实现，由调用方决定执行上下文。
        """
        if not isinstance(kb, object):
            return 0
        # 清空旧人设
        try:
            kb.clear_namespace(_PERSONA_NS)  # type: ignore[attr-defined]
        except Exception:  # noqa: BLE001
            pass
        texts: List[str] = []
        metas: List[dict] = []
        for cid, c in self._chars.items():
            sections = [
                f"角色名：{c.name}",
                f"性格：{c.personality}" if c.personality else "",
                f"背景：{c.background}" if c.background else "",
                f"行为准则：{c.behavior_rules}" if c.behavior_rules else "",
                f"场景：{c.scenario}" if c.scenario else "",
                f"开场白：{c.first_mes}" if c.first_mes else "",
            ]
            persona_text = "\n".join(x for x in sections if x).strip()
            if not persona_text:
                continue
            texts.append(persona_text)
            metas.append(
                {
                    "character_id": cid,
                    "name": c.name,
                    "source": "persona",
                }
            )
        if not texts:
            return 0
        try:
            kb.add(texts, metadatas=metas, namespace=_PERSONA_NS)  # type: ignore[attr-defined]
            return len(texts)
        except Exception as exc:  # noqa: BLE001
            logger.warning("人设同步到知识库失败：%s", exc)
            return 0
