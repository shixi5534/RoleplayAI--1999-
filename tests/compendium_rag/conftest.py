"""``tests/compendium_rag`` 专用夹具。

**作用域**：只服务新增的独立库 ``src/compendium_rag``。
这里**不导入** ``roleplay.*``，不读取既有 ``data/knowledge``，也不受根
``tests/conftest.py`` 里那套 ``ROLEPLAY_*`` 环境变量影响——新库的测试
与既有系统的测试完全解耦（符合"与之前的独立"这一要求）。

所有测试默认**离线**：不调用云端 LLM、不依赖 Ollama。需要真实网络的用例
一律用 ``@pytest.mark.online`` 标记，并在默认运行中被排除。
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

VENDOR = ROOT / "vendor" / "Reverse1999-Story-Compendium"
READABLE = VENDOR / "readable" / "story_zh_CN_chapter_edition"


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "online: 需要真实云端 LLM / Ollama 的用例（默认跳过）")


def pytest_collection_modifyitems(config, items):
    if config.getoption("-m") and "online" in str(config.getoption("-m")):
        return
    skip = pytest.mark.skip(reason="默认离线运行；需要 -m online 才执行")
    for item in items:
        if "online" in item.keywords:
            item.add_marker(skip)


@pytest.fixture(scope="session")
def readable_dir() -> Path:
    if not READABLE.is_dir():
        pytest.skip(f"Compendium 数据源不存在：{READABLE}")
    return READABLE


@pytest.fixture()
def isolated_settings(tmp_path, readable_dir):
    """指向临时目录的设置，避免污染真实 data/compendium_rag。"""
    from compendium_rag.config import Settings

    return Settings(source_dir=readable_dir, data_dir=tmp_path / "kb",
                    llm_api_key="test-key", llm_model="test-model",
                    embed_base_url="http://127.0.0.1:1",
                    categories=("mainline", "activity", "character",
                                "anecdote", "appendix_unbound"))


@pytest.fixture(scope="session")
def _chapters_cache(readable_dir):
    """全量语料只解析一次（151 篇解析约 1.5s，逐个用例重解析会拖慢整套）。"""
    from compendium_rag.corpus import load_corpus

    return load_corpus(readable_dir, ("mainline", "activity", "character",
                                      "anecdote", "appendix_unbound"))


@pytest.fixture()
def all_chapters(_chapters_cache):
    """全量语料（共享只读缓存，调用方不得就地修改）。"""
    return _chapters_cache


@pytest.fixture(scope="session")
def _chunks_cache(_chapters_cache):
    from compendium_rag.chunker import chunk_corpus
    from compendium_rag.config import Settings

    s = Settings(source_dir=READABLE)
    return chunk_corpus(_chapters_cache, s)


@pytest.fixture()
def all_chunks(_chunks_cache):
    """全量分块（共享只读缓存）。"""
    return _chunks_cache


@pytest.fixture()
def mini_chapters():
    """3 篇代表性剧情（主线 / 活动 / 轶事），足够覆盖结构差异。"""
    from compendium_rag.corpus import load_corpus

    if not READABLE.is_dir():
        pytest.skip("Compendium 数据源不存在")
    return load_corpus(READABLE, ("mainline", "activity", "anecdote"))


@pytest.fixture()
def mini_chunks(mini_chapters, isolated_settings):
    from compendium_rag.chunker import chunk_corpus

    return chunk_corpus(mini_chapters, isolated_settings)
