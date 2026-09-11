"""角色原声切片库：加载 manifest 并按 槽位×配音语言 选片。

数据来源：frontend/assets/voice/<char>/manifest.json（faster-whisper 听录官方
语音视频切分的中/英双配音切片，每条带 subtitle:{zh,en} 双语字幕）。manifest
顶层结构：clips（切片明细）+ slots（槽位 → clip id 列表）。

选片语义与前端 pet-voice.js 的 pickFromSlot 对齐：
- 按 lang 过滤（同一槽位中/英是两套独立配音）；
- 排除"最近一次播过的切片"，池因此为空时允许重复（否则单条槽位如 enter/zh
  会被去重逻辑永久卡死）。

本模块只管"数据 + 选片"，不涉及触发判定（见 voice_reply.py），对渠道零耦合。
"""
from __future__ import annotations

import json
import logging
import random
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ClipEntry:
    """一条可发送的原声切片（音频文件 + 元数据）。"""

    id: str
    lang: str  # zh / en
    file: str  # 相对 manifest 所在目录的路径，如 "zh/00.mp3"
    dur: float  # 秒
    subtitle: dict  # {"zh": ..., "en": ...}，缺失时为空 dict


class ClipStore:
    """一个角色的切片库。构造即加载 manifest（轻量 JSON，~200KB）。"""

    def __init__(self, manifest_path: str | Path) -> None:
        path = Path(manifest_path)
        raw = json.loads(path.read_text(encoding="utf-8"))
        self.root = path.parent  # 切片音频相对此目录
        self.character = str(raw.get("character", path.parent.name))
        self.clips: dict[str, ClipEntry] = {}
        for c in raw.get("clips", []):
            try:
                dur = float(c.get("dur") or 0.0) or float(
                    float(c.get("end", 0.0)) - float(c.get("start", 0.0))
                )
            except (TypeError, ValueError):
                dur = 0.0
            self.clips[str(c["id"])] = ClipEntry(
                id=str(c["id"]),
                lang=str(c.get("lang", "")),
                file=str(c.get("file", "")),
                dur=max(0.0, dur),
                subtitle=c.get("subtitle") or {},
            )
        # 槽位 → id 列表（过滤未知 id，保持 manifest 顺序）
        self.slots: dict[str, list[str]] = {
            str(slot): [cid for cid in ids if cid in self.clips]
            for slot, ids in (raw.get("slots") or {}).items()
        }
        logger.debug(
            "切片库加载：%s clips=%d slots=%d", path, len(self.clips), len(self.slots)
        )

    def pick(
        self, slot: str, lang: str, *, exclude: str | None = None
    ) -> ClipEntry | None:
        """按槽位与语言随机取一条；exclude 为最近播过的 clip id。

        无该槽位/该语言切片 → None（调用方降级）。
        """
        pool = [
            self.clips[cid]
            for cid in self.slots.get(slot, [])
            if self.clips[cid].lang == lang
        ]
        if not pool:
            return None
        fresh = [c for c in pool if c.id != exclude] if exclude else pool
        # 池只剩最近播过的一句（单条槽位）→ 允许重复，避免槽位被去重卡死
        return random.choice(fresh or pool)

    def read_bytes(self, entry: ClipEntry) -> bytes:
        """读取切片音频字节（mp3；NapCat 端负责转 silk，无需本地转码）。"""
        return (self.root / entry.file).read_bytes()


def default_manifest_path(settings) -> Path | None:
    """定位切片 manifest：配置项优先，否则按仓库布局自动定位。

    仓库布局锚点：本文件位于 <repo>/src/roleplay/core/voice/ 下，
    故 <repo> = parents[4]（与 main.py 的 parent.parent.parent 同一约定）。
    """
    override = (getattr(settings, "qq_voice_clip_manifest", "") or "").strip()
    if override:
        p = Path(override)
        if p.is_file():
            return p
        logger.warning("QQ 语音：ROLEPLAY_QQ_VOICE_CLIP_MANIFEST 指向的文件不存在：%s", override)
        return None
    base = (
        Path(__file__).resolve().parents[4]
        / "frontend"
        / "assets"
        / "voice"
        / "wu_ming_zhe"
        / "manifest.json"
    )
    return base if base.is_file() else None
