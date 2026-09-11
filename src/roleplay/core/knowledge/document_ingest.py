"""多格式资料导入管线（文档 / 网页 / 数据库 → 预处理 → 分块 → 向量化入库）。

管线四阶段：
  1. 加载（Loader）   ：按来源类型提取纯文本 + 来源元数据
     - 本地文件：.md / .markdown / .txt / .html / .htm / .json / .csv / .pdf / .docx
     - 网页 URL：http(s) 抓取正文（复用 ingest._fetch_text）
     - 数据库  ：SQLite（表名或自定义 SQL，行 → 文本记录）
  2. 预处理（Preprocess）：统一换行、去控制字符、压缩空白、去 HTML 残留
  3. 分块（Chunk）    ：Markdown 标题感知切块（章节路径入元数据），
                        其余格式回退到 chunk_text 滑窗重叠切块
  4. 入库（Store）    ：KnowledgeBase.add()，向量化由注入的 EmbedderPort 完成

命名空间约定：
  - 角色专属资料 → lore_<character_id>（如 lore_wu_ming_zhe），
    与角色卡 knowledge_scope 字段联动，实现"知识范围"约束检索。
  - 通用资料     → 调用方自定义（默认 "docs"）。

纯标准库实现，无第三方依赖，可离线运行。
"""
from __future__ import annotations

import csv
import io
import json
import logging
import re
import sqlite3
import unicodedata
from pathlib import Path
from typing import Callable, List

from .ingest import chunk_text, _fetch_text
from .security_utils import safe_local_path, safe_url
from .vector_store import KnowledgeBase

logger = logging.getLogger(__name__)

SUPPORTED_SUFFIXES = {
    ".md", ".markdown", ".txt", ".html", ".htm", ".json", ".csv",
    ".pdf", ".docx",  # 需 pypdf / python-docx（缺失时给出清晰报错）
}

_heading_re = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
_html_tag_re = re.compile(r"<[^>]+>")
_html_block_re = re.compile(r"<(script|style)[\s\S]*?</\1>", re.I)


# ────────────────────────── 2) 预处理 ──────────────────────────
def preprocess_text(text: str) -> str:
    """统一换行 / NFC 归一 / 去控制字符 / 压缩多余空白（保留换行结构）。"""
    if not text:
        return ""
    text = unicodedata.normalize("NFC", text.replace("\r\n", "\n").replace("\r", "\n"))
    # 去除除 \n\t 外的控制字符
    text = "".join(c for c in text if c == "\n" or c == "\t" or not unicodedata.category(c).startswith("C"))
    # 行内空白压缩；连续空行压为一个
    lines = [re.sub(r"[ \t\u3000]+", " ", ln).strip() for ln in text.split("\n")]
    out: list[str] = []
    for ln in lines:
        if ln or (out and out[-1]):
            out.append(ln)
    return "\n".join(out).strip()


def _strip_html(raw: str) -> str:
    raw = _html_block_re.sub(" ", raw)
    raw = _html_tag_re.sub(" ", raw)
    raw = re.sub(r"&[a-zA-Z#0-9]+;", " ", raw)
    return raw


# ────────────────────────── 3) 分块 ──────────────────────────
def chunk_markdown(
    text: str, size: int = 600, overlap: int = 80
) -> List[tuple[str, dict]]:
    """Markdown 标题感知切块：先按标题分节，节内超长再滑窗切分。

    返回 [(chunk_text, {"section": "一级 > 二级"}), ...]，
    章节路径写入元数据，检索命中后可溯源到原文位置。
    """
    text = (text or "").strip()
    if not text:
        return []
    # 按标题切节
    sections: list[tuple[list[str], list[str]]] = []  # (heading_path, lines)
    path: dict[int, str] = {}
    cur_lines: list[str] = []
    cur_path: list[str] = []

    def flush() -> None:
        body = "\n".join(cur_lines).strip()
        if body:
            sections.append((list(cur_path), [body]))

    for line in text.split("\n"):
        m = _heading_re.match(line)
        if m:
            flush()
            cur_lines = []
            level = len(m.group(1))
            path[level] = m.group(2).strip()
            for deeper in [k for k in path if k > level]:
                path.pop(deeper, None)
            cur_path = [path[k] for k in sorted(path)]
        else:
            cur_lines.append(line)
    flush()

    out: List[tuple[str, dict]] = []
    for heading_path, bodies in sections:
        section = " > ".join(heading_path) if heading_path else ""
        for body in bodies:
            # 节标题拼进块首，增强向量召回（查询常含章节主题词）
            prefix = f"【{section}】\n" if section else ""
            for piece in chunk_text(body, size=size, overlap=overlap):
                out.append((prefix + piece, {"section": section}))
    return out


# ────────────────────────── 1) 加载器 ──────────────────────────
def _load_pdf(path: Path) -> str:
    """PDF → 按页提取正文（pypdf）。缺失依赖时报清晰错误。"""
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # noqa: BLE001
        raise RuntimeError(
            "需要 pypdf 才能导入 PDF，请执行：pip install pypdf"
        ) from exc
    reader = PdfReader(str(path))
    pages: list[str] = []
    for i, page in enumerate(reader.pages):
        try:
            text = page.extract_text() or ""
        except Exception as exc:  # noqa: BLE001
            logger.warning("PDF 第 %d 页提取失败：%s", i + 1, exc)
            text = ""
        if text.strip():
            pages.append(f"【第 {i + 1} 页】\n{text}")
    return "\n\n".join(pages)


def _load_docx(path: Path) -> str:
    """DOCX → 段落 + 表格文本（python-docx）。缺失依赖时报清晰错误。"""
    try:
        from docx import Document
    except ImportError as exc:  # noqa: BLE001
        raise RuntimeError(
            "需要 python-docx 才能导入 DOCX，请执行：pip install python-docx"
        ) from exc
    doc = Document(str(path))
    parts: list[str] = []
    for para in doc.paragraphs:
        if para.text.strip():
            style = para.style.name if para.style else ""
            prefix = f"【{style}】" if style and style != "Normal" else ""
            parts.append(f"{prefix}{para.text}")
    for ti, table in enumerate(doc.tables):
        rows: list[str] = []
        for row in table.rows:
            cells = [c.text.strip() for c in row.cells if c.text.strip()]
            if cells:
                rows.append(" | ".join(cells))
        if rows:
            parts.append(f"【表格 {ti + 1}】\n" + "\n".join(rows))
    return "\n\n".join(parts)


def _load_file(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return _load_pdf(path)
    if suffix == ".docx":
        return _load_docx(path)
    raw = path.read_text(encoding="utf-8", errors="ignore")
    if suffix in {".html", ".htm"}:
        return _strip_html(raw)
    if suffix == ".json":
        try:
            data = json.loads(raw)
            return _json_to_text(data)
        except (ValueError, TypeError):
            return raw
    if suffix == ".csv":
        return _csv_to_text(raw)
    return raw  # md / txt


def _json_to_text(data, prefix: str = "") -> str:
    """JSON → 「键路径: 值」行式文本，保留结构信息便于检索。"""
    lines: list[str] = []
    if isinstance(data, dict):
        for k, v in data.items():
            p = f"{prefix}.{k}" if prefix else str(k)
            lines.append(_json_to_text(v, p))
    elif isinstance(data, list):
        for i, v in enumerate(data):
            lines.append(_json_to_text(v, f"{prefix}[{i}]"))
    else:
        return f"{prefix}: {data}"
    return "\n".join(x for x in lines if x)


def _csv_to_text(raw: str) -> str:
    """CSV → 每行「列名=值; ...」记录文本。"""
    try:
        reader = csv.DictReader(io.StringIO(raw))
        rows = [
            "; ".join(f"{k}={v}" for k, v in row.items() if v)
            for row in reader
        ]
        return "\n".join(rows)
    except csv.Error:
        return raw


# ────────────────────────── 4) 入库统一入口 ──────────────────────────
def _store_chunks(
    kb: KnowledgeBase,
    chunks: List[tuple[str, dict]],
    base_meta: dict,
    namespace: str,
) -> int:
    if not chunks:
        return 0
    texts = [c[0] for c in chunks]
    metas = [{**base_meta, **c[1]} for c in chunks]
    kb.add(texts, metadatas=metas, namespace=namespace)
    return len(texts)


def ingest_file(
    kb: KnowledgeBase,
    path: str | Path,
    namespace: str = "docs",
    character_id: str | None = None,
    chunk_size: int = 600,
    overlap: int = 80,
    extra_meta: dict | None = None,
    allowed_roots: list[str] | None = None,
    doc_id: str | None = None,
) -> dict:
    """导入本地文档（md/txt/html/json/csv/pdf/docx）。返回 {stored, source, format}。

    allowed_roots 非空时，path 须收敛在其内（防路径穿越）；API 层必传。

    doc_id 提供文档级唯一标识（如 uuid4），注入每个 chunk 的 meta，
    用于文档级管理（按 doc_id 聚合 / 删除整篇）。为 None 时行为与旧版一致。
    """
    p = safe_local_path(path, allowed_roots or [])
    if not p.is_file():
        raise FileNotFoundError(f"文件不存在：{p}")
    suffix = p.suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES:
        raise ValueError(f"不支持的格式 {suffix}，支持：{sorted(SUPPORTED_SUFFIXES)}")
    text = preprocess_text(_load_file(p))
    if suffix in {".md", ".markdown"}:
        chunks = chunk_markdown(text, size=chunk_size, overlap=overlap)
    else:
        chunks = [(c, {}) for c in chunk_text(text, size=chunk_size, overlap=overlap)]
    meta = {
        "source": "file",
        "path": str(p),
        "title": p.stem,
        "format": suffix.lstrip("."),
        **({"character_id": character_id} if character_id else {}),
        **({"doc_id": doc_id} if doc_id else {}),
        **(extra_meta or {}),
    }
    stored = _store_chunks(kb, chunks, meta, namespace)
    logger.info("文档入库：%s → ns=%s 切块=%d", p.name, namespace, stored)
    return {"stored": stored, "source": str(p), "format": suffix.lstrip(".")}


def ingest_url(
    kb: KnowledgeBase,
    url: str,
    namespace: str = "docs",
    character_id: str | None = None,
    chunk_size: int = 600,
    overlap: int = 80,
    timeout: float = 10.0,
    allowed_hosts: list[str] | None = None,
) -> dict:
    """导入网页正文（仅 https，且 host 须在 allowlist，并拦截私有地址 —— SSRF 防护）。

    allowed_hosts 为空即拒绝一切 URL 导入（生产默认关闭）。
    """
    safe_url(url, allowed_hosts or [])
    text = preprocess_text(_fetch_text(url, timeout=timeout))
    chunks = [(c, {}) for c in chunk_text(text, size=chunk_size, overlap=overlap)]
    meta = {
        "source": "url",
        "url": url,
        "format": "html",
        **({"character_id": character_id} if character_id else {}),
    }
    stored = _store_chunks(kb, chunks, meta, namespace)
    logger.info("网页入库：%s → ns=%s 切块=%d", url, namespace, stored)
    return {"stored": stored, "source": url, "format": "html"}


def ingest_sqlite(
    kb: KnowledgeBase,
    db_path: str | Path,
    table: str | None = None,
    query: str | None = None,
    namespace: str = "docs",
    character_id: str | None = None,
    max_rows: int = 2000,
    allowed_roots: list[str] | None = None,
) -> dict:
    """导入 SQLite 数据（表名或只读 SELECT 语句），每行转为一条记录文本。

    allowed_roots 非空时，db_path 须收敛在其内（防路径穿越）；API 层必传。
    """
    p = safe_local_path(db_path, allowed_roots or [])
    if not p.is_file():
        raise FileNotFoundError(f"数据库不存在：{p}")
    if not table and not query:
        raise ValueError("必须提供 table 或 query 之一")
    if query and not re.match(r"^\s*select\b", query, re.I):
        raise ValueError("query 仅允许 SELECT 语句")
    if table and not re.fullmatch(r"[A-Za-z0-9_]+", table):
        raise ValueError("非法表名")
    sql = query or f"SELECT * FROM {table}"
    conn = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
    try:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(sql).fetchmany(max_rows)
    finally:
        conn.close()
    chunks: List[tuple[str, dict]] = []
    for i, row in enumerate(rows):
        record = "; ".join(f"{k}={row[k]}" for k in row.keys() if row[k] is not None)
        if record.strip():
            chunks.append((preprocess_text(record), {"row": i}))
    meta = {
        "source": "sqlite",
        "path": str(p),
        "table": table or "query",
        "format": "db",
        **({"character_id": character_id} if character_id else {}),
    }
    stored = _store_chunks(kb, chunks, meta, namespace)
    logger.info("数据库入库：%s(%s) → ns=%s 行=%d", p.name, table or "query", namespace, stored)
    return {"stored": stored, "source": str(p), "format": "db"}


def ingest_directory(
    kb: KnowledgeBase,
    directory: str | Path,
    namespace: str = "docs",
    character_id: str | None = None,
    chunk_size: int = 600,
    recursive: bool = True,
    allowed_roots: list[str] | None = None,
) -> dict:
    """批量导入目录下所有受支持格式的文档。

    allowed_roots 非空时，directory 须收敛在其内（防路径穿越）；API 层必传。
    """
    d = safe_local_path(directory, allowed_roots or [])
    if not d.is_dir():
        raise FileNotFoundError(f"目录不存在：{d}")
    it = d.rglob("*") if recursive else d.glob("*")
    total, files = 0, []
    for f in sorted(it):
        if f.is_file() and f.suffix.lower() in SUPPORTED_SUFFIXES:
            try:
                r = ingest_file(
                    kb, f, namespace=namespace,
                    character_id=character_id, chunk_size=chunk_size,
                )
                total += r["stored"]
                files.append(f.name)
            except (OSError, ValueError) as exc:
                logger.warning("跳过 %s：%s", f.name, exc)
    return {"stored": total, "files": files}


def lore_namespace(character_id: str) -> str:
    """角色专属资料命名空间约定：lore_<character_id>。"""
    safe = re.sub(r"[^A-Za-z0-9_\u4e00-\u9fff]+", "_", character_id.strip())
    return f"lore_{safe or 'default'}"
