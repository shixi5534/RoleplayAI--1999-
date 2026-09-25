# -*- coding: utf-8 -*-
"""按 scene 内连续 turn 聚合分块。

分块策略（确定性，无模型参与）：
- 以 H3 剧情单元（scene）为**不跨越**的边界——一个块内的对话有共同的场景前提；
- scene 内按累计字符数聚合到 ``chunk_chars``，相邻块保留 ``chunk_overlap_turns`` 行重叠，
  避免跨块的问答被硬切断；
- 渲染文本保留 ``**说话人**：`` 前缀（抽取与检索都依赖说话人归属）；
- ``chunk_id`` 位置稳定（重跑不变），``content_key`` 内容哈希（抽取缓存用）。
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

from .config import Settings
from .corpus import Chapter, Turn


@dataclass
class Chunk:
    chunk_id: str
    content_key: str
    doc_id: str
    chapter_title: str
    category: str
    part_title: str
    scene_title: str
    script_id: str
    chapter_id: str
    turns: list[Turn] = field(default_factory=list)
    speakers: list[str] = field(default_factory=list)
    text: str = ""

    @property
    def n_turns(self) -> int:
        return len(self.turns)

    def to_dict(self) -> dict:
        return {
            "chunk_id": self.chunk_id,
            "content_key": self.content_key,
            "doc_id": self.doc_id,
            "chapter_title": self.chapter_title,
            "category": self.category,
            "part_title": self.part_title,
            "scene_title": self.scene_title,
            "script_id": self.script_id,
            "chapter_id": self.chapter_id,
            "speakers": self.speakers,
            "speakers_text": "、".join(self.speakers),
            "text": self.text,
        }

    @staticmethod
    def from_dict(d: dict) -> "Chunk":
        return Chunk(
            chunk_id=d["chunk_id"], content_key=d.get("content_key", ""),
            doc_id=d.get("doc_id", ""), chapter_title=d.get("chapter_title", ""),
            category=d.get("category", ""), part_title=d.get("part_title", ""),
            scene_title=d.get("scene_title", ""), script_id=d.get("script_id", ""),
            chapter_id=d.get("chapter_id", ""), speakers=d.get("speakers", []) or [],
            text=d.get("text", ""),
        )


def render_turns(turns: list[Turn]) -> str:
    """turn 列表 → 文本。对话带说话人前缀，旁白/引用原样。"""
    out: list[str] = []
    for t in turns:
        if t.kind == "dialogue" and t.speaker:
            out.append(f"**{t.speaker}**：{t.text}")
        elif t.kind == "title_card":
            out.append(f"【标题卡】{t.text}")
        elif t.kind == "quote":
            out.append(f"「{t.text}」")
        else:
            out.append(t.text)
    return "\n".join(out)


def _content_key(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _speakers_of(turns: list[Turn]) -> list[str]:
    seen: dict[str, None] = {}
    for t in turns:
        if t.is_dialogue and t.speaker:
            seen.setdefault(t.speaker, None)
    return list(seen)


def _merge_small(chunks: list[Chunk], minimum: int) -> list[Chunk]:
    """把过小的碎块并入相邻块。

    实测 corpus 里 428 个 <120 字的块，绝大多数是 `「副标题：她义无反顾。」`
    这类章节副标题行——单开一块既浪费一次云端抽取调用，又因信息量太低
    必然抽出 0 实体。这里做**确定性合并**（不丢弃任何内容）：
    - 优先并入前一块；
    - 若它是本篇第一块（前面无处可并），则并入后一块。

    合并后 ``chunk_id`` 与 ``text`` 需重算，但整个过程只依赖输入顺序，
    因此重跑结果完全一致（幂等）。
    """
    if len(chunks) <= 1:
        return chunks

    def absorb(dst: Chunk, src: Chunk) -> None:
        dst.turns = dst.turns + src.turns
        dst.text = render_turns(dst.turns)
        dst.content_key = _content_key(dst.text)
        seen = list(dst.speakers)
        for s in src.speakers:
            if s not in seen:
                seen.append(s)
        dst.speakers = seen

    out: list[Chunk] = []
    for c in chunks:
        if out and len(c.text) < minimum:
            absorb(out[-1], c)
        else:
            out.append(c)

    # 首块仍可能过小（前面无处可并）→ 并入其后的块
    if len(out) >= 2 and len(out[0].text) < minimum:
        head, nxt = out[0], out[1]
        merged_turns = head.turns + nxt.turns
        nxt.turns = merged_turns
        nxt.text = render_turns(merged_turns)
        nxt.content_key = _content_key(nxt.text)
        seen = list(head.speakers) + [s for s in nxt.speakers if s not in head.speakers]
        nxt.speakers = seen
        # 场景上下文取更靠前的一个，避免归属丢失
        if not nxt.scene_title:
            nxt.scene_title = head.scene_title
        if not nxt.part_title:
            nxt.part_title = head.part_title
        out = out[1:]
    return out


def chunk_chapter(ch: Chapter, settings: Settings) -> list[Chunk]:
    """把一篇剧情切成若干块。"""
    chunks: list[Chunk] = []
    target = max(200, settings.chunk_chars)
    overlap = max(0, settings.chunk_overlap_turns)
    minimum = max(1, settings.min_chunk_chars)

    for pi, part in enumerate(ch.parts):
        for si, scene in enumerate(part.scenes):
            turns = scene.turns
            if not turns:
                continue
            # 贪心聚合
            groups: list[list[Turn]] = []
            cur: list[Turn] = []
            size = 0
            for t in turns:
                cur.append(t)
                size += len(t.text) + 1
                if size >= target:
                    groups.append(cur)
                    cur = cur[-overlap:] if overlap else []
                    size = sum(len(x.text) + 1 for x in cur)
            if cur:
                # 尾块过小则并入上一块（避免碎块）
                if groups and sum(len(x.text) + 1 for x in cur) < minimum:
                    groups[-1].extend(cur)
                else:
                    groups.append(cur)

            for ci, g in enumerate(groups):
                text = render_turns(g)
                if not text.strip():
                    continue
                cid = f"{ch.doc_id}:{pi}.{si}.{ci}"
                chunks.append(Chunk(
                    chunk_id=cid,
                    content_key=_content_key(text),
                    doc_id=ch.doc_id,
                    chapter_title=ch.title,
                    category=ch.category,
                    part_title=part.title,
                    scene_title=scene.title,
                    script_id=scene.script_id,
                    chapter_id=ch.chapter_id,
                    turns=list(g),
                    speakers=_speakers_of(g),
                    text=text,
                ))
    return _merge_small(chunks, minimum)


def chunk_corpus(chapters: list[Chapter], settings: Settings) -> list[Chunk]:
    out: list[Chunk] = []
    for ch in chapters:
        out.extend(chunk_chapter(ch, settings))
    return out


def chunks_stats(chunks: list[Chunk]) -> dict:
    if not chunks:
        return {"chunks": 0}
    sizes = sorted(len(c.text) for c in chunks)
    n = len(sizes)
    return {
        "chunks": n,
        "chars": sum(sizes),
        "mean_chars": round(sum(sizes) / n, 1),
        "p50_chars": sizes[n // 2],
        "p90_chars": sizes[int(n * 0.9)],
        "max_chars": sizes[-1],
        "min_chars": sizes[0],
        "by_category": _by_cat(chunks),
    }


def _by_cat(chunks: list[Chunk]) -> dict:
    out: dict[str, dict] = {}
    for c in chunks:
        d = out.setdefault(c.category, {"chunks": 0, "chars": 0})
        d["chunks"] += 1
        d["chars"] += len(c.text)
    return out
