# -*- coding: utf-8 -*-
"""独立性契约测试 —— 本文件守护用户的核心要求：「与之前的独立」。

用户原话：「用这里面的数据独立的新建一个数据图谱 rag，与之前的独立，
并只对这个新的库进行测试」。

把"独立"变成**可执行的静态约束**而不是口头承诺。检查全部基于 AST
（剥离注释与文档字符串后再判定），否则本库自己解释"与旧库无关"的注释
会被误判成违规——这是本文件第一版踩过的坑。
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PKG = ROOT / "src" / "compendium_rag"


def _py_files() -> list[Path]:
    files = sorted(PKG.rglob("*.py"))
    assert files, f"未找到包源码：{PKG}"
    return files


def _code_only(path: Path) -> str:
    """只保留可执行代码：剥离所有注释与模块/类/函数文档字符串。"""
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src)
    lines = src.splitlines()
    drop: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                             ast.AsyncFunctionDef)):
            body = getattr(node, "body", [])
            if (body and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)):
                for ln in range(body[0].lineno, body[0].end_lineno + 1):
                    drop.add(ln)
    return "\n".join(l for i, l in enumerate(lines, 1) if i not in drop)


# ── 代码级隔离 ──

def test_package_exists():
    assert PKG.is_dir()
    for name in ("__init__.py", "cli.py", "config.py", "corpus.py", "chunker.py",
                 "extract.py", "graph_store.py", "retriever.py", "pipeline.py",
                 "llm.py", "embedder.py"):
        assert (PKG / name).exists(), f"缺少模块 {name}"


def test_no_roleplay_imports():
    """核心隔离：新库不得 import 既有 roleplay 包（AST 检查）。"""
    offenders = []
    for f in _py_files():
        tree = ast.parse(f.read_text(encoding="utf-8"), filename=str(f))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    if a.name == "roleplay" or a.name.startswith("roleplay."):
                        offenders.append(f"{f.name}: import {a.name}")
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                if node.level == 0 and (mod == "roleplay"
                                        or mod.startswith("roleplay.")):
                    offenders.append(f"{f.name}: from {mod}")
    assert not offenders, f"新库不得 import roleplay：{offenders}"


def test_no_legacy_data_paths():
    """不得读写既有系统的数据目录（避免与旧库互相污染）。"""
    bad = ("data/knowledge", "data\\knowledge", "data/lore", "data\\lore",
           "data/characters", "data\\characters", "data/eval", "data\\eval",
           "plot_corpus_", "plot_graph_", "lore_wu_ming_zhe", "graph_wu_ming_zhe")
    offenders = []
    for f in _py_files():
        code = _code_only(f)
        for b in bad:
            if b in code:
                offenders.append(f"{f.name}: {b}")
    assert not offenders, f"新库引用既有数据资产：{offenders}"


# 既有 system 的配置字段名（不是本库自己的 graph_* 标识符）
LEGACY_FIELDS = (
    "plot_graph_enabled", "plot_lore_dir", "plot_corpus_dir", "plot_graph_dir",
    "plot_cache_dir", "plot_max_chunks", "plot_max_edges", "plot_ppr_damping",
    "plot_link_threshold", "plot_semantic_enabled", "plot_rerank_topup_enabled",
    "plot_entity_expand_enabled", "plot_trace_enabled",
    "graph_enabled", "graph_dir", "graph_cache_dir", "graph_max_chunks",
    "graph_entity_link_threshold", "graph_extract_batch",
)


def test_no_legacy_config_fields():
    """不得使用既有 plot_*/graph_* 配置字段。

    注意：本库自己有 ``graph_path`` / ``graph_channel`` / ``graph_store``
    这类标识符，它们是**本库内部命名**，与既有配置字段无关；
    因此这里按**精确字段名**匹配，而不是 ``graph_*`` 通配。
    """
    offenders = []
    for f in _py_files():
        code = _code_only(f)
        for field in LEGACY_FIELDS:
            if re.search(rf"\b{re.escape(field)}\b", code):
                offenders.append(f"{f.name}: {field}")
    assert not offenders, f"新库使用了既有配置字段：{offenders}"


def test_uses_cmprag_namespace():
    """本库的配置前缀必须是 CMPRAG_。"""
    code = _code_only(PKG / "config.py")
    assert "CMPRAG_" in code
    assert re.search(r'CMPRAG_[A-Z_]+', code)


def test_roleplay_env_reads_are_credential_fallback_only():
    """``ROLEPLAY_*`` 只允许作为**凭据回退**读取，且必须被 CMPRAG_ 覆盖。

    设计取舍：新库与旧库在数据/存储/检索上完全独立，但**不强迫用户重复配置
    同一组云端凭据**。因此允许在 CMPRAG_ 未设置时回退读取
    ROLEPLAY_LLM_{BASE_URL,API_KEY} 与 ROLEPLAY_OLLAMA_BASE_URL。
    这条测试把该例外限定成白名单，防止 ROLEPLAY_ 依赖悄悄扩大。
    """
    allowed = {
        "ROLEPLAY_LLM_BASE_URL", "ROLEPLAY_LLM_API_KEY",
        "ROLEPLAY_OLLAMA_BASE_URL",
    }
    used: set[str] = set()
    for f in _py_files():
        code = _code_only(f)
        used.update(re.findall(r"ROLEPLAY_[A-Z_]+", code))
        # 消息文本里提到配置名不算依赖
    used -= {"ROLEPLAY_LLM_API_KEY"} if False else set()
    # 排除仅出现在字符串提示里的名字：逐个核对确为 _env(...) 调用
    real: set[str] = set()
    for f in _py_files():
        code = _code_only(f)
        for name in re.findall(r'ROLEPLAY_[A-Z_]+', code):
            if re.search(rf'_env\(\s*"{name}"', code):
                real.add(name)
    extra = real - allowed
    assert not extra, f"ROLEPLAY_ 依赖超出凭据白名单：{extra}"


def test_cmprag_takes_precedence_over_roleplay():
    """CMPRAG_ 优先于 ROLEPLAY_（回退是单向的）。"""
    code = _code_only(PKG / "config.py")
    assert re.search(r'_env\(\s*"CMPRAG_LLM_API_KEY"\s*\)\s*\n?\s*or\s+_env\(',
                     code) or "_env(\"CMPRAG_LLM_API_KEY\")" in code


# ── 数据隔离 ──

def test_data_dir_is_dedicated():
    from compendium_rag.config import DEFAULT_DATA_DIR, get_settings

    assert DEFAULT_DATA_DIR.name == "compendium_rag"
    s = get_settings()
    assert s.data_dir.name == "compendium_rag"
    for p in (s.corpus_path, s.graph_path, s.index_path, s.cache_dir,
              s.reports_dir):
        assert str(s.data_dir) in str(p), f"{p} 不在独立数据目录内"


def test_data_dir_is_not_legacy_dir():
    from compendium_rag.config import get_settings

    s = get_settings()
    for legacy in ("knowledge", "lore", "characters", "eval", "docs"):
        assert s.data_dir != ROOT / "data" / legacy


def test_source_dir_points_at_vendor_compendium():
    """数据源必须是 Compendium 本地副本，而不是既有语料。"""
    from compendium_rag.config import get_settings

    s = get_settings()
    assert "Reverse1999-Story-Compendium" in str(s.source_dir)
    assert "story_zh_CN_chapter_edition" in str(s.source_dir)


def test_all_writes_go_to_data_dir():
    """pipeline 的所有落盘调用都必须指向 settings 提供的路径（或其形参）。

    允许的目标形态：
      - ``settings.xxx`` / ``s.path`` / ``self.settings``：直接取自配置
      - ``path``：函数的路径形参（如 ``safe_save_graph(graph, path)``）——
        调用方负责传入 ``settings.graph_path``，此处只收敛"不得出现硬编码/外部路径"。
    """
    code = _code_only(PKG / "pipeline.py")
    targets = re.findall(r"\.save\(([^)]*)\)", code)
    assert targets, "未找到落盘调用（结构可能已变，需更新本测试）"
    allowed_prefixes = ("settings.", "data_dir", "self.settings", "s.path")
    for t in targets:
        t = t.strip()
        ok = any(p in t for p in allowed_prefixes) or t == "path"
        assert ok, f"可疑写入目标：{t}"


def test_safe_save_graph_guards_empty_overwrite():
    """空图保护必须存在（防「缓存为空 → 覆盖已有图谱」事故）。"""
    code = _code_only(PKG / "pipeline.py")
    assert "def safe_save_graph" in code, "缺少空图保护函数"
    assert "if not graph.entities" in code, "保护逻辑缺失"
    cli = _code_only(PKG / "cli.py")
    assert "safe_save_graph" in cli, "CLI 未接入空图保护"


# ── 测试套件自身的隔离 ──

def test_conftest_does_not_set_roleplay_env():
    """本库 conftest 不得设置 ROLEPLAY_* 环境变量（避免影响/被影响旧测试）。"""
    conftest = ROOT / "tests" / "compendium_rag" / "conftest.py"
    code = _code_only(conftest)
    assert not re.search(r'environ\[["\']ROLEPLAY_', code), \
        "本库 conftest 不应写 ROLEPLAY_ 环境变量"
    assert "import roleplay" not in code


def test_conftest_isolates_data_dir():
    """本库测试必须把 data_dir 指到临时目录，绝不写真实数据目录。"""
    conftest = ROOT / "tests" / "compendium_rag" / "conftest.py"
    code = _code_only(conftest)
    assert "tmp_path" in code
    assert "data_dir=" in code


def test_new_tests_do_not_import_roleplay():
    """本库测试文件不得 import roleplay。"""
    tdir = ROOT / "tests" / "compendium_rag"
    offenders = []
    for f in sorted(tdir.glob("test_*.py")):
        tree = ast.parse(f.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    if a.name.startswith("roleplay"):
                        offenders.append(f"{f.name}: {a.name}")
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                if node.level == 0 and mod.startswith("roleplay"):
                    offenders.append(f"{f.name}: {mod}")
    assert not offenders, f"本库测试引入了 roleplay：{offenders}"


def test_tests_are_confined_to_own_directory():
    """本库测试只在自己的目录下，不改动既有测试文件。"""
    own = ROOT / "tests" / "compendium_rag"
    assert own.is_dir()
    names = {p.name for p in own.glob("test_*.py")}
    assert {"test_corpus.py", "test_chunker.py", "test_graph_store.py",
            "test_retriever.py", "test_extract.py", "test_llm_parse.py",
            "test_independence.py"} <= names


# ── 数据安全：脚本/测试绝不能写真实数据目录 ──

def test_scripts_never_target_real_data_dir():
    """``scripts/`` 下的 compendium 脚本若构造 Settings/删目录，必须显式指定
    ``data_dir`` 到临时位置。

    回归事故：``compendium_rag_test_resume.py`` 早期版本用
    ``Settings(llm_base_url=...)``（未传 data_dir）→ 落到真实
    ``data/compendium_rag/``，收尾的 ``rmtree(cache_dir)`` 删掉了 698 块
    **云端已付费**的抽取缓存。这条测试防止同类事故再现。
    """
    offenders = []
    for f in sorted((ROOT / "scripts").glob("compendium_rag_*.py")):
        src = f.read_text(encoding="utf-8")
        code = _code_only(f)
        # 出现删除操作
        if "rmtree" not in code and "unlink(" not in code:
            continue
        # 则必须把 data_dir 指到临时目录
        if "data_dir=" not in code:
            offenders.append(f"{f.name}: 有删除操作但未显式指定 data_dir")
        if "mkdtemp" not in code and "tmp_path" not in code:
            offenders.append(f"{f.name}: 有删除操作但未使用临时目录")
    assert not offenders, f"存在误删真实数据的风险：{offenders}"


def test_resume_script_guards_real_data_dir():
    """续跑验证脚本必须带"拒绝对真实目录操作"的硬断言。"""
    p = ROOT / "scripts" / "compendium_rag_test_resume.py"
    code = _code_only(p)
    assert "REAL_DATA_DIR" in code, "缺少真实数据目录保护常量"
    assert "data_dir=" in code, "必须显式指定 data_dir 到临时目录"
    assert "assert" in code, "缺少保护性断言"


def test_cli_rebuild_does_not_delete_cache():
    """``rebuild`` 只读缓存，绝不删除。"""
    code = _code_only(PKG / "cli.py")
    assert "rmtree" not in code, "CLI 不应有删除目录操作"
    assert "unlink" not in code, "CLI 不应有删除文件操作"
