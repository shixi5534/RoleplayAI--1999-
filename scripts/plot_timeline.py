# -*- coding: utf-8 -*-
"""剧情时间线排序 CLI：为角色剧情语料构建 版本排序 / 故事时间序 两套索引。

功能
----
- ``--check``   校验时间线元数据：schema/必填字段、story_rank 严格递增无重复、
                语料中出现的每个 version 都被 entries 覆盖。失败打印明确错误并 exit 1。
- ``--print``   打印时间线。``story``（默认）按故事时间序（story_rank 升序，未考排最后）；
                ``version`` 按版本数值序、同版本内按章节叙事序。每行附带语料统计。
- ``--build``   把时间线 + 语料统计落盘到 ``data/knowledge/plot_timeline_<cid>.json``。

用法（项目根目录执行）
----------------------
    python -X utf8 scripts/plot_timeline.py --check
    python -X utf8 scripts/plot_timeline.py --print story
    python -X utf8 scripts/plot_timeline.py --print version
    python -X utf8 scripts/plot_timeline.py --build

本脚本**只读语料**；时间线 json 仅在 ``--build`` 时写入 knowledge 目录，不碰其它文件。
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
# ROOT 使 `scripts.cloud_extract` 可导入（无论从哪个 cwd 执行）；
# src 使 roleplay 包可导入（项目未安装为 wheel）。
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

from scripts.cloud_extract import _paths  # noqa: E402
from roleplay.config import get_settings  # noqa: E402
from roleplay.core.knowledge.plot_corpus import PlotCorpus  # noqa: E402

SCHEMA = "plot-timeline-v1"
DEFAULT_CHARACTER = "wu_ming_zhe"
# 时间线元数据（人工考据的单一事实源）
TIMELINE_JSON = ROOT / "data" / "lore" / "{cid}" / "plot_timeline.json"
# --build 产物落盘目录
BUILD_DIR = ROOT / "data" / "knowledge"
BUILD_NAME = "plot_timeline_{cid}.json"

# entry 必填字段（chapter 及四个时间/置信字段允许 null，但字段本身必须存在）
REQUIRED_FIELDS: tuple[str, ...] = (
    "key", "version", "chapter", "name", "story_time",
    "year", "year_end", "story_rank", "source", "confidence",
)
# 这些字段语义上必须非空。version 允许空串（语料中确实存在无版本标签的 chunk），
# 但不得为 None/缺失。
NON_NULL_FIELDS: tuple[str, ...] = ("key", "name", "source")

# 章节叙事序（同版本内排序用；未登记章节排最后）
_CHAPTER_ORDER: dict[str, int] = {
    "序幕": 0, "1ST": 1, "2ND": 2, "3RD": 3, "4TH": 4,
    "5TH": 5, "6TH": 6, "7TH": 7, "8TH": 8, "9TH": 9,
}
_CHAPTER_DEFAULT = 90


# ──────────────────────────── 数据加载 ────────────────────────────

def load_timeline(character_id: str = DEFAULT_CHARACTER) -> dict[str, Any]:
    """加载时间线元数据 json；文件缺失或非法 json 抛出带说明的 ValueError。"""
    path = Path(str(TIMELINE_JSON).format(cid=character_id))
    if not path.exists():
        raise ValueError(f"时间线文件不存在: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise ValueError(f"时间线文件不是合法 JSON: {path} ({exc})") from exc
    if not isinstance(data, dict):
        raise ValueError(f"时间线文件顶层必须是对象: {path}")
    return data


def load_corpus(character_id: str = DEFAULT_CHARACTER) -> PlotCorpus:
    """按项目惯例（cloud_extract._paths）定位并加载剧情语料。"""
    cpath, _cloud, _cache = _paths(get_settings(), character_id)
    return PlotCorpus(cpath, character_id=character_id)


def corpus_stats(chunks: Iterable[Any]) -> dict[str, dict[str, Any]]:
    """按 version 聚合语料统计：chunk 数、doc 集合、arc 集合。"""
    stats: dict[str, dict[str, Any]] = {}
    for ch in chunks:
        entry = stats.setdefault(ch.version, {"chunks": 0, "docs": set(), "arcs": set()})
        entry["chunks"] += 1
        entry["docs"].add(ch.doc_id)
        if ch.arc:
            entry["arcs"].add(ch.arc)
    return stats


# ──────────────────────────── 校验 ────────────────────────────

def check_timeline(timeline: dict[str, Any], stats: dict[str, dict[str, Any]]) -> list[str]:
    """返回全部错误（空列表 = 通过）。"""
    errors: list[str] = []

    # ① schema 与必填字段
    if timeline.get("schema") != SCHEMA:
        errors.append(f"schema 不符: 期望 {SCHEMA!r}，实际 {timeline.get('schema')!r}")
    if timeline.get("character_id") != DEFAULT_CHARACTER:
        errors.append(
            f"character_id 不符: 期望 {DEFAULT_CHARACTER!r}，"
            f"实际 {timeline.get('character_id')!r}"
        )
    entries = timeline.get("entries")
    if not isinstance(entries, list) or not entries:
        errors.append("entries 缺失或为空")
        return errors

    keys: set[str] = set()
    for i, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"entries[{i}] 不是对象")
            continue
        for field in REQUIRED_FIELDS:
            if field not in entry:
                errors.append(f"entries[{i}] (key={entry.get('key')!r}) 缺少必填字段 {field!r}")
        for field in NON_NULL_FIELDS:
            if entry.get(field) in (None, ""):
                errors.append(f"entries[{i}] 字段 {field!r} 不得为空/None")
        if "version" in entry and entry["version"] is None:
            errors.append(f"entries[{i}] 字段 'version' 不得为 None（空串=无版本标签）")

    # key 唯一
    dup_keys = [k for k in {e.get("key") for e in entries if isinstance(e, dict)}
                if k is not None and [x.get("key") for x in entries if isinstance(x, dict)].count(k) > 1]
    if dup_keys:
        errors.append(f"key 重复: {sorted(set(dup_keys))}")

    # ② story_rank 非空项严格递增且无重复
    ranks = [e["story_rank"] for e in entries
             if isinstance(e, dict) and e.get("story_rank") is not None]
    for i in range(1, len(ranks)):
        if ranks[i] <= ranks[i - 1]:
            errors.append(f"story_rank 非严格递增: 第{i}处 {ranks[i - 1]} -> {ranks[i]}")
            break
    if len(set(ranks)) != len(ranks):
        errors.append(f"story_rank 存在重复: {sorted(r for r in ranks if ranks.count(r) > 1)}")

    # ③ 语料中每个 version 都被 entries 覆盖
    covered = {e.get("version") for e in entries if isinstance(e, dict)}
    missing = sorted((v for v in stats if v not in covered),
                     key=_version_sort_key)
    if missing:
        errors.append(f"语料 version 未被 entries 覆盖: {missing!r}")

    return errors


# ──────────────────────────── 排序 ────────────────────────────

def _version_sort_key(version: str) -> tuple[int, float, str]:
    """版本数值序；非数值标签（含空串）排在所有数值版本之后。"""
    try:
        return (0, float(version), "")
    except (TypeError, ValueError):
        return (1, 0.0, str(version))


def _chapter_sort_key(chapter: str | None) -> int:
    """章节叙事序；未登记章节排最后。"""
    if chapter is None:
        return _CHAPTER_DEFAULT + 1
    return _CHAPTER_ORDER.get(chapter, _CHAPTER_DEFAULT)


def sort_story(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """故事时间序：story_rank 升序，未考（null）排最后并保持原相对顺序。"""
    ranked = sorted(
        (e for e in entries if e.get("story_rank") is not None),
        key=lambda e: e["story_rank"],
    )
    unranked = [e for e in entries if e.get("story_rank") is None]
    return ranked + unranked


def sort_version(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """版本序：version 数值序，同版本内按章节叙事序，同章节按 story_rank。"""
    return sorted(
        entries,
        key=lambda e: (
            _version_sort_key(e.get("version", "")),
            _chapter_sort_key(e.get("chapter")),
            e.get("story_rank") if e.get("story_rank") is not None else 9999,
        ),
    )


# ──────────────────────────── 输出 ────────────────────────────

def _fmt(value: Any) -> str:
    if value is None:
        return "-"
    return str(value)


def print_entries(
    entries: list[dict[str, Any]],
    stats: dict[str, dict[str, Any]],
    mode: str,
) -> None:
    """统一行格式: rank | version | chapter | name | story_time | chunks,docs"""
    print(f"{'rank':>4} | {'ver':<5} | {'chapter':<6} | name | story_time | chunks,docs")
    for entry in entries:
        rank = entry.get("story_rank")
        rank_str = str(rank) if rank is not None else "[未考]"
        version = entry.get("version") or "(无版本)"
        st = stats.get(entry.get("version", ""), {"chunks": 0, "docs": set()})
        print(
            f"{rank_str:>4} | {version:<5} | {_fmt(entry.get('chapter')):<6} | "
            f"{entry.get('name')} | {_fmt(entry.get('story_time'))} | "
            f"{st['chunks']},{len(st['docs'])}"
        )
    total_vers = len(stats)
    print(f"-- 共 {len(entries)} 条 entries，覆盖语料 version {total_vers} 个（mode={mode}）")


# ──────────────────────────── build ────────────────────────────

def build(timeline: dict[str, Any], stats: dict[str, dict[str, Any]],
          character_id: str) -> Path:
    """把 entries + 语料统计写进 data/knowledge/plot_timeline_<cid>.json。"""
    enriched: list[dict[str, Any]] = []
    for entry in timeline["entries"]:
        st = stats.get(entry.get("version", ""))
        row = dict(entry)
        row["chunk_count"] = st["chunks"] if st else 0
        row["doc_count"] = len(st["docs"]) if st else 0
        row["arc_list"] = sorted(st["arcs"]) if st else []
        enriched.append(row)

    out = {
        "schema": SCHEMA,
        "character_id": character_id,
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "sources": timeline.get("sources", {}),
        "entries": enriched,
    }
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    path = BUILD_DIR / BUILD_NAME.format(cid=character_id)
    path.write_text(
        json.dumps(out, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    return path


# ──────────────────────────── CLI ────────────────────────────

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="剧情时间线排序 CLI")
    parser.add_argument("--character", default=DEFAULT_CHARACTER,
                        help=f"角色 id（默认 {DEFAULT_CHARACTER}）")
    parser.add_argument("--check", action="store_true",
                        help="校验时间线元数据与语料覆盖，失败 exit 1")
    parser.add_argument("--print", dest="print_mode", nargs="?", const="story",
                        choices=["story", "version"], default=None,
                        help="打印时间线（story=故事时间序，version=版本序；默认 story）")
    parser.add_argument("--build", action="store_true",
                        help="写 data/knowledge/plot_timeline_<cid>.json")
    args = parser.parse_args(argv)

    if not (args.check or args.print_mode or args.build):
        parser.print_help()
        return 2

    timeline = load_timeline(args.character)
    corpus = load_corpus(args.character)
    chunks = list(corpus.chunks)
    stats = corpus_stats(chunks)

    if args.check:
        errors = check_timeline(timeline, stats)
        if errors:
            print("[plot_timeline] --check 失败：")
            for err in errors:
                print(f"  - {err}")
            return 1
        covered = len({e.get("version") for e in timeline["entries"]} & set(stats))
        print(
            f"[plot_timeline] --check 通过：{len(timeline['entries'])} 条 entries，"
            f"覆盖语料 version {covered}/{len(stats)} 个，"
            f"语料共 {len(chunks)} chunks / {len({c.doc_id for c in chunks})} docs"
        )

    if args.print_mode:
        entries = timeline["entries"]
        ordered = sort_story(entries) if args.print_mode == "story" else sort_version(entries)
        print_entries(ordered, stats, args.print_mode)

    if args.build:
        path = build(timeline, stats, args.character)
        print(f"[plot_timeline] --build 已落盘: {path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
