"""剧情时间线排序模块测试。

覆盖：
1. data/lore/wu_ming_zhe/plot_timeline.json 可加载且 schema 正确；
2. story_rank 非空项严格递增且无重复；
3. entries 覆盖语料全部 distinct version；
4. 年代锚点断言（v1.2=1971 / v2.2=1990 / v2.6=1991 / 7th=1914）；
5. scripts/plot_timeline.py --check 以子进程方式 exit 0。
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

from plot_timeline import (  # noqa: E402
    SCHEMA,
    check_timeline,
    corpus_stats,
    load_corpus,
    load_timeline,
    sort_story,
    sort_version,
)

TIMELINE_PATH = ROOT / "data" / "lore" / "wu_ming_zhe" / "plot_timeline.json"


@pytest.fixture(scope="module")
def timeline() -> dict:
    """加载时间线元数据（整份 json）。"""
    return json.loads(TIMELINE_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def stats() -> dict:
    """语料按 version 的统计（chunk/doc/arc）。"""
    corpus = load_corpus("wu_ming_zhe")
    return corpus_stats(list(corpus.chunks))


# ── ① 可加载且 schema 正确 ──────────────────────────────────

def test_timeline_loadable_and_schema_correct(timeline: dict) -> None:
    assert TIMELINE_PATH.exists(), "时间线文件必须存在"
    assert timeline["schema"] == SCHEMA
    assert timeline["character_id"] == "wu_ming_zhe"
    assert isinstance(timeline["entries"], list) and timeline["entries"]
    # 每个 entry 十个字段齐全
    required = {
        "key", "version", "chapter", "name", "story_time",
        "year", "year_end", "story_rank", "source", "confidence",
    }
    keys = set()
    for entry in timeline["entries"]:
        assert required <= set(entry), f"entry 缺字段: {entry.get('key')}"
        assert entry["key"] and entry["name"]
        assert entry["version"] is not None  # 空串=语料中无版本标签的 chunk，合法
        keys.add(entry["key"])
    assert len(keys) == len(timeline["entries"]), "key 必须唯一"


# ── ② story_rank 严格递增无重复 ─────────────────────────────

def test_story_rank_strictly_increasing_and_unique(timeline: dict) -> None:
    ranks = [e["story_rank"] for e in timeline["entries"] if e["story_rank"] is not None]
    assert ranks, "至少要有非空 story_rank"
    assert len(set(ranks)) == len(ranks), f"story_rank 有重复: {ranks}"
    for prev, cur in zip(ranks, ranks[1:]):
        assert cur > prev, f"story_rank 非严格递增: {prev} -> {cur}"
    assert ranks == list(range(1, len(ranks) + 1)), "story_rank 应为 1..N 连续"


# ── ③ 覆盖语料全部 distinct version ─────────────────────────

def test_entries_cover_all_corpus_versions(timeline: dict, stats: dict) -> None:
    covered = {e["version"] for e in timeline["entries"]}
    missing = sorted(v for v in stats if v not in covered)
    assert not missing, f"语料 version 未被 entries 覆盖: {missing}"


# ── ④ 年代锚点断言 ─────────────────────────────────────────

def test_year_anchors(timeline: dict) -> None:
    by_key = {e["key"]: e for e in timeline["entries"]}
    assert by_key["v1.2"]["year"] == 1971
    assert by_key["v2.2"]["year"] == 1990
    assert by_key["v2.6"]["year"] == 1991
    assert by_key["7th"]["year"] == 1914


# ── ⑤ --check 子进程 exit 0 ─────────────────────────────────

def test_check_subprocess_exit_zero() -> None:
    result = subprocess.run(
        [sys.executable, "-X", "utf8", str(ROOT / "scripts" / "plot_timeline.py"),
         "--check"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=str(ROOT),
        timeout=300,
    )
    assert result.returncode == 0, f"--check 失败:\n{result.stdout}\n{result.stderr}"
    assert "通过" in result.stdout


# ── 排序函数补充断言 ────────────────────────────────────────

def test_sort_story_nulls_last(timeline: dict) -> None:
    ordered = sort_story(timeline["entries"])
    ranks = [e["story_rank"] for e in ordered]
    non_null = [r for r in ranks if r is not None]
    assert non_null == sorted(non_null)
    assert all(r is None for r in ranks[len(non_null):]), "未考项必须排在最后"


def test_sort_version_numeric_then_chapter(timeline: dict) -> None:
    ordered = sort_version(timeline["entries"])
    versions = [e["version"] for e in ordered]
    numeric = [v for v in versions if v]
    assert numeric == sorted(numeric, key=float), "数值 version 必须按数值序"
    # 同版本（1.0）内按章节叙事序：序幕在 1ST 之前、1ST 在 2ND 之前
    v10 = [e["chapter"] for e in ordered if e["version"] == "1.0"]
    assert v10.index("序幕") < v10.index("1ST") < v10.index("2ND")
