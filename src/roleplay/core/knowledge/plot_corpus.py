"""剧情语料层（PlotCorpus）：B站机器转写文案 → **独立于 lore 向量库**的切块语料。

定位（docs/GRAPHRAG加强计划书.md §16 剧情图谱层）：
- 只吃 ``data/lore/<cid>/视频文案/`` 下的机器转写产物，供剧情图谱（PlotGraph）
  做证据溯源与词法兜底检索；
- **不写入** ``lore_<cid>`` 命名空间、**不依赖** KnowledgeBase 与嵌入器，
  因此与现有 RAG 完全解耦（关掉剧情层，lore 检索行为逐字节不变）；
- 落盘 ``data/knowledge/plot_corpus_<cid>.json``：自带 chunk 文本（无向量），
  体积约为向量库的 1/10，且嵌入器换型不会让它失效。

语料隔离的三重白名单（任一不满足即拒绝，防手工整理 md 混入）：
1. 目录白名单：仅 ``<角色目录>/视频文案/`` 递归；
2. 文件名白名单：``^BV[0-9A-Za-z]+(?:_p\\d+)?_`` ；
3. 头部白名单：元数据头必须含 ``来源：B站`` 与 ``机器提取`` 标记。

语言处理（约束①）：英配视频正文为英文（whisper 自动检测偶有 es 误判），
逐块启发式判定 zh/en/other 并写入 meta，供抽取提示词分语种选择与检索降权。
"""
from __future__ import annotations

import hashlib
import json
import logging
import math
import re
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

# ① 文件名白名单：BV号 + 可选分P（机器转写产物命名规范，见 bilibili_lore_ingest）
TRANSCRIPT_FILE_RE = re.compile(r"^(BV[0-9A-Za-z]+?)(?:_p(\d+))?_", re.IGNORECASE)
# ② 头部白名单标记
HEADER_MARKERS = ("来源：B站", "机器提取")
# 转写目录名（手工整理 md 在角色目录根，天然被排除）
TRANSCRIPT_DIRNAME = "视频文案"

# 标题解析：# 【重返未来：1999】3.8版本「世纪末尺度」全剧情流程 - Reverse: 1999｜4K（01.世纪末的忧郁）
#
# 版本号在 726 份转写标题里有三种实测形态（M0/N0-1，见 docs 剧情语料审计）：
#   ① 《…》3.8版本「世纪末尺度」…                    592 份（旧正则已覆盖）
#   ② …公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜1~4）  76 份
#   ③ 《重返未来1999》中配1.6【朔日手记】全剧情【4K】（10【异乡人关怀】…）24 份
# 三条分支都要求「小数 + 强上下文」，绝不单独靠小数判版本号——否则
# 「1.5小时」「2024.10 更新」这类无关数字会被误判成版本（见单元测试边界用例）。
# 命名分组便于 parse_title_meta 取到实际命中的那一条（交替分支只可能命中一个）。
RE_VERSION = re.compile(
    r"(?P<v_tag>\d+\.\d+)\s*版本"  # ① 3.8版本
    r"|【\s*(?P<v_bracket>\d+\.\d+)\s*[-－]"  # ② 【1.1-活动】/【1.0-主线】/【1.1-角色】
    r"|(?<=[中英日韩]配)\s*(?P<v_dub>\d+\.\d+)"  # ③ 中配1.6 / 英配1.6
)
RE_ARC = re.compile(r"「([^」]{1,30})」")
RE_CHAPTER = re.compile(r"[（(](\d{1,2})[.、\s]*([^）)]{1,30})[）)]\s*$")
RE_META_UP = re.compile(r"UP主：([^｜|]+)")
RE_META_PUB = re.compile(r"发布：(\d{4}-\d{2}-\d{2})")
RE_META_DUR = re.compile(r"时长：(\d+:\d{2})")
RE_META_METHOD = re.compile(r"提取方式：([^（(]+)")

# ── 来源分级（G4 数据层，N0-2）──────────────────────────────────────────────
# 只写数据字段，**不做检索层过滤**（检索过滤是后续 M5，本次不碰）。
# 取值：
#   canon    主线/官方剧情实录（可当剧情事实），老语料缺失该字段时的默认值
#   analysis 考据/解析/推测/科普向（UP 主二次解读，可信度低于实录）
#   official 官方号物料（PV/前瞻，权威但可能含未落地设定）
SOURCE_KIND_CANON = "canon"
SOURCE_KIND_ANALYSIS = "analysis"
SOURCE_KIND_OFFICIAL = "official"
SOURCE_KINDS = (SOURCE_KIND_CANON, SOURCE_KIND_ANALYSIS, SOURCE_KIND_OFFICIAL)

# 主线实录 UP 主白名单（缺德的德鲁伊：257/266 文档 = 98.8%）：命中即 canon，
# 优先级高于标题关键词——避免实录标题里出现「解析」二字被误降级。
CANON_UPLOADERS = frozenset({"缺德的德鲁伊"})
# 官方号（游戏官方账号发布的 PV / 前瞻）
OFFICIAL_UPLOADERS = frozenset({"重返未来1999", "重返未来：1999"})
# 考据/分析向 UP 主白名单（实测 7 个，共 63 chunk / 8 文档）
ANALYSIS_UPLOADERS = frozenset(
    {
        "薯条小叔叔",
        "荟小荟",
        "银发三千雪满头",
        "众口难调有口难开",
        "账号已注销",
        "介慈啊",
        "梦驿九际-凌痕",
    }
)
# 标题关键词兜底：不在白名单里的 UP 主，标题命中这些词也算考据/分析向
ANALYSIS_TITLE_KEYWORDS = (
    "解析", "考据", "推测", "猜想", "分析", "盘点", "科普", "梳理",
    "万字", "一分钟看懂", "带你看懂", "快速了解", "入坑", "重讲",
)

CJK_RE = re.compile(r"[\u4e00-\u9fff]")
LATIN_RE = re.compile(r"[A-Za-z]")

# 英文转写里高频的口语填充词（词法检索降噪用）
EN_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "if", "then", "than", "that", "this",
    "these", "those", "is", "are", "was", "were", "be", "been", "am", "do", "does",
    "did", "have", "has", "had", "i", "you", "he", "she", "it", "we", "they", "me",
    "him", "her", "them", "my", "your", "his", "its", "our", "their", "of", "in",
    "on", "at", "to", "for", "with", "from", "by", "as", "so", "not", "no", "yes",
    "there", "here", "what", "who", "how", "why", "when", "about", "just", "now",
    "up", "out", "into", "over", "again", "all", "one", "s", "t", "don", "re", "ve",
}


def plot_namespace(character_id: str) -> str:
    """剧情层命名空间：``plot_<character_id>``（与 lore_<cid> 严格分离）。"""
    safe = re.sub(r"[^A-Za-z0-9_\u4e00-\u9fff]+", "_", (character_id or "").strip())
    return f"plot_{safe or 'default'}"


def chunk_hash(text: str) -> str:
    """chunk 文本指纹（图谱证据溯源键，与 graph_store.chunk_text_hash 同口径）。"""
    return hashlib.sha1((text or "").encode("utf-8")).hexdigest()[:16]


def detect_lang(text: str) -> str:
    """启发式语种判定：zh / en / other（机器转写，宁可粗判也要稳定）。"""
    sample = (text or "")[:800]
    if not sample:
        return "other"
    cjk = len(CJK_RE.findall(sample))
    latin = len(LATIN_RE.findall(sample))
    if cjk >= 20 and cjk > latin * 0.3:
        return "zh"
    if latin >= 60 and cjk < latin * 0.1:
        return "en"
    return "other"


def classify_source_kind(*, uploader: str = "", title: str = "") -> str:
    """来源分级（G4 数据层）：按 UP 主白名单 + 标题关键词判定 ``source_kind``。

    优先级：官方号 > 主线实录白名单 > 考据向白名单 > 标题关键词 > canon（兜底）。
    规则全部集中在上面的常量里，后续人工调整只改常量、不动调用点。
    """
    up = (uploader or "").strip()
    if up in OFFICIAL_UPLOADERS:
        return SOURCE_KIND_OFFICIAL
    if up in CANON_UPLOADERS:
        return SOURCE_KIND_CANON
    if up in ANALYSIS_UPLOADERS:
        return SOURCE_KIND_ANALYSIS
    text = title or ""
    if any(kw in text for kw in ANALYSIS_TITLE_KEYWORDS):
        return SOURCE_KIND_ANALYSIS
    return SOURCE_KIND_CANON


def parse_title_meta(title: str) -> dict:
    """从 md 一级标题解析 版本 / 篇章 / 章节序号与章节名。"""
    out: dict = {"version": "", "arc": "", "chapter_no": 0, "chapter": ""}
    if not title:
        return out
    m = RE_VERSION.search(title)
    if m:
        # 交替分支只会命中一个分组，其余为 None
        out["version"] = next((g for g in m.groups() if g), "")
    m = RE_ARC.search(title)
    if m:
        out["arc"] = m.group(1)
    tail = title.split("｜")[-1] if "｜" in title else title
    m = RE_CHAPTER.search(tail.strip())
    if m:
        out["chapter_no"] = int(m.group(1))
        out["chapter"] = m.group(2).strip()
        return out
    m = RE_CHAPTER.search(title.strip())
    if m:
        out["chapter_no"] = int(m.group(1))
        out["chapter"] = m.group(2).strip()
    return out


def split_body(body: str, chunk_size: int = 600) -> list[str]:
    """正文 → chunk：按空行分段，贪心合并到 chunk_size（不跨段硬切）。"""
    paras = [p.strip() for p in re.split(r"\n\s*\n", body or "") if p.strip()]
    chunks: list[str] = []
    buf: list[str] = []
    size = 0
    for p in paras:
        if size and size + len(p) > chunk_size:
            chunks.append("\n\n".join(buf))
            buf, size = [], 0
        if len(p) > chunk_size * 2:  # 极长段（无空行的转写）：按句再切
            for piece in _split_long(p, chunk_size):
                buf.append(piece)
                size += len(piece)
                if size >= chunk_size:
                    chunks.append("\n\n".join(buf))
                    buf, size = [], 0
            continue
        buf.append(p)
        size += len(p)
    if buf:
        chunks.append("\n\n".join(buf))
    return [c for c in chunks if c.strip()]


def _split_long(text: str, size: int) -> list[str]:
    """超长段按句末标点切分（英文句号同样适用）。"""
    pieces, buf = [], ""
    for ch in text:
        buf += ch
        if len(buf) >= size and ch in "。！？.!?；;\n":
            pieces.append(buf.strip())
            buf = ""
    if buf.strip():
        pieces.append(buf.strip())
    return pieces or [text]


@dataclass
class PlotChunk:
    """剧情语料块：自带文本与剧情元数据（无向量依赖）。"""

    hash: str
    text: str
    doc_id: str
    bv: str
    page: int
    part: str = ""
    title: str = ""
    uploader: str = ""
    pubdate: str = ""
    duration: str = ""
    version: str = ""
    arc: str = ""
    chapter_no: int = 0
    chapter: str = ""
    lang: str = "other"
    method: str = ""
    seq: int = 0
    # 来源分级（G4 数据层，N0-2）：canon / analysis / official。
    # 可选字段：老语料 JSON 没有该键时 from_dict 会用默认值 canon，不报错。
    source_kind: str = SOURCE_KIND_CANON
    extra: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "hash": self.hash,
            "text": self.text,
            "doc_id": self.doc_id,
            "bv": self.bv,
            "page": self.page,
            "part": self.part,
            "title": self.title,
            "uploader": self.uploader,
            "pubdate": self.pubdate,
            "duration": self.duration,
            "version": self.version,
            "arc": self.arc,
            "chapter_no": self.chapter_no,
            "chapter": self.chapter,
            "lang": self.lang,
            "method": self.method,
            "seq": self.seq,
            "source_kind": self.source_kind,
            "extra": self.extra,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PlotChunk":
        known = {f for f in cls.__dataclass_fields__}  # type: ignore[attr-defined]
        obj = cls(**{k: v for k, v in (data or {}).items() if k in known})
        # 老语料/异常值兜底：source_kind 缺失或不在受控取值内 → canon
        if obj.source_kind not in SOURCE_KINDS:
            obj.source_kind = SOURCE_KIND_CANON
        return obj

    def meta(self, namespace: str) -> dict:
        """检索块 metadata（供 persona_prompt._source_label 与前端展示）。"""
        label = self.chapter or self.part or f"P{self.page}"
        meta = {
            "namespace": namespace,
            "doc_id": self.doc_id,
            "source_type": "plot_transcript",
            "bv": self.bv,
            "page": self.page,
            "part": self.part,
            "title": self.title,
            "section": f"{self.version}版本·{label}" if self.version else label,
            "version": self.version,
            "arc": self.arc,
            "chapter": self.chapter,
            "lang": self.lang,
            "seq": self.seq,
            "url": f"https://www.bilibili.com/video/{self.bv}"
            + (f"?p={self.page}" if self.page else ""),
            "via": "plot_graph",
        }
        meta.update(self.extra or {})
        return meta


class PlotCorpus:
    """单角色剧情语料：扫描 → 切块 → 落盘 → 词法检索。"""

    SCHEMA = "plot-corpus-v1"

    def __init__(self, path: str | Path, character_id: str = "") -> None:
        self._path = Path(path)
        self.character_id = character_id
        self.chunks: list[PlotChunk] = []
        self._bm25: dict[str, list[tuple[str, float]]] | None = None
        self._docs: dict[str, dict] = {}
        # hash → chunk 的 O(1) 索引（N0-3）：剧情图谱回查证据时逐块 by_hash，
        # 旧实现线性扫描 2477 块 × 每次检索，是检索热路径上的 O(n²)。
        self._by_hash: dict[str, PlotChunk] = {}
        self.load()

    # ── 构建 ──
    def build(self, source_dir: str | Path, *, chunk_size: int = 600) -> dict:
        """扫描转写目录重建语料。返回统计 {files, kept, rejected, chunks, by_lang}。"""
        src = Path(source_dir)
        files: list[Path] = []
        if src.is_dir():
            for p in sorted(src.rglob("*.md")):
                # 白名单①：路径中必须含 视频文案 目录段
                if TRANSCRIPT_DIRNAME not in p.parts:
                    continue
                files.append(p)
        chunks: list[PlotChunk] = []
        rejected: list[str] = []
        for p in files:
            parsed = _parse_transcript_file(p, chunk_size=chunk_size)
            if parsed is None:
                rejected.append(p.name)
                continue
            chunks.extend(parsed)
        self.chunks = chunks
        self._bm25 = None
        self._reindex_docs()
        langs: dict[str, int] = {}
        for c in chunks:
            langs[c.lang] = langs.get(c.lang, 0) + 1
        return {
            "files": len(files),
            "kept": len(files) - len(rejected),
            "rejected": len(rejected),
            "rejected_samples": rejected[:5],
            "chunks": len(chunks),
            "by_lang": langs,
            "by_source_kind": self.source_kind_counts(),
        }

    # ── 持久化 ──
    def load(self) -> bool:
        try:
            raw = json.loads(self._path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return False
        data = raw.get("chunks") if isinstance(raw, dict) else raw
        if not isinstance(data, list):
            return False
        self.chunks = [PlotChunk.from_dict(c) for c in data if isinstance(c, dict)]
        self._reindex_docs()
        return True

    def save(self) -> None:
        if self._path.parent and not self._path.parent.exists():
            self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema": self.SCHEMA,
            "character_id": self.character_id,
            "count": len(self.chunks),
            "docs": self._docs,
            "chunks": [c.to_dict() for c in self.chunks],
        }
        tmp = self._path.with_suffix(".tmp")
        tmp.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        tmp.replace(self._path)

    def _reindex_docs(self) -> None:
        docs: dict[str, dict] = {}
        for c in self.chunks:
            d = docs.setdefault(
                c.doc_id,
                {
                    "doc_id": c.doc_id,
                    "bv": c.bv,
                    "page": c.page,
                    "title": c.title,
                    "uploader": c.uploader,
                    "pubdate": c.pubdate,
                    "version": c.version,
                    "arc": c.arc,
                    "lang": c.lang,
                    "chunks": 0,
                },
            )
            d["chunks"] += 1
        self._docs = docs
        self._rebuild_hash_index()

    def _rebuild_hash_index(self) -> None:
        """重建 hash → chunk 索引（重复 hash 保留首个，与旧线性扫描语义一致）。"""
        index: dict[str, PlotChunk] = {}
        for c in self.chunks:
            if c.hash and c.hash not in index:
                index[c.hash] = c
        self._by_hash = index

    def _ensure_hash_index(self) -> None:
        """惰性兜底：直接改过 ``corpus.chunks`` 而没走 build/load 时也能命中索引。"""
        if len(self._by_hash) != len({c.hash for c in self.chunks}):
            self._rebuild_hash_index()

    # ── 查询 ──
    def by_hash(self, h: str) -> PlotChunk | None:
        """O(1) 按文本指纹取块（旧实现为 O(n) 线性扫描）。"""
        if not h:
            return None
        self._ensure_hash_index()
        return self._by_hash.get(h)

    def by_source_kind(self, kind: str) -> list[PlotChunk]:
        """按来源分级过滤（G4 数据层；检索层是否过滤属后续 M5，本次不动检索）。"""
        return [c for c in self.chunks if c.source_kind == kind]

    def source_kind_counts(self) -> dict[str, int]:
        """各来源分级的块数（打标结果观测用）。"""
        counts: dict[str, int] = {k: 0 for k in SOURCE_KINDS}
        for c in self.chunks:
            counts[c.source_kind] = counts.get(c.source_kind, 0) + 1
        return counts

    def docs(self) -> dict[str, dict]:
        return dict(self._docs)

    def _ensure_bm25(self) -> None:
        if self._bm25 is not None:
            return
        postings: dict[str, list[tuple[str, float]]] = {}
        for c in self.chunks:
            tf: dict[str, int] = {}
            for tok in tokenize(c.text):
                tf[tok] = tf.get(tok, 0) + 1
            for tok, n in tf.items():
                # BM25 词频饱和（k1=1.5, b=0.75 的子项；长度归一用固定 600 字近似）
                postings.setdefault(tok, []).append(
                    (c.hash, (n * 2.5) / (n + 1.5))
                )
        n_docs = max(1, len(self.chunks))
        scored: dict[str, list[tuple[str, float]]] = {}
        for tok, plist in postings.items():
            idf = math.log(1 + (n_docs - len(plist) + 0.5) / (len(plist) + 0.5))
            scored[tok] = [(h, w * idf) for h, w in plist]
        self._bm25 = scored

    def search(
        self,
        query: str,
        top_k: int = 5,
        *,
        lang: str | None = None,
        bv: str | None = None,
    ) -> list[tuple[PlotChunk, float]]:
        """BM25 词法检索（剧情层兜底通道，零嵌入依赖）。"""
        if not self.chunks:
            return []
        self._ensure_bm25()
        assert self._bm25 is not None
        scores: dict[str, float] = {}
        for tok in tokenize(query):
            for h, w in self._bm25.get(tok, ()):
                scores[h] = scores.get(h, 0.0) + w
        if not scores:
            return []
        top = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
        out: list[tuple[PlotChunk, float]] = []
        self._ensure_hash_index()
        for h, s in top:
            c = self._by_hash.get(h)
            if c is None:
                continue
            if lang and c.lang != lang:
                continue
            if bv and c.bv != bv:
                continue
            out.append((c, float(s)))
            if len(out) >= max(1, top_k):
                break
        return out

    def stats(self) -> dict:
        langs: dict[str, int] = {}
        versions: dict[str, int] = {}
        for c in self.chunks:
            langs[c.lang] = langs.get(c.lang, 0) + 1
            key = c.version or "未标注"
            versions[key] = versions.get(key, 0) + 1
        chars = sum(len(c.text) for c in self.chunks)
        return {
            "chunks": len(self.chunks),
            "docs": len(self._docs),
            "chars": chars,
            "by_lang": langs,
            "by_version": versions,
            "path": str(self._path),
        }


def tokenize(text: str) -> list[str]:
    """中英混合分词：拉丁词 + CJK 单字与二元组（与 vector_store._BM25 同风格）。"""
    out: list[str] = []
    for m in re.finditer(r"[a-z0-9]+", (text or "").lower()):
        w = m.group(0)
        if len(w) > 1 and w not in EN_STOPWORDS:
            out.append(w)
    cjk = CJK_RE.findall(text or "")
    out.extend(cjk)
    out.extend(a + b for a, b in zip(cjk, cjk[1:]))
    return out


def _parse_transcript_file(path: Path, *, chunk_size: int = 600) -> list[PlotChunk] | None:
    """单个转写 md → chunk 列表；不满足白名单返回 None。"""
    m = TRANSCRIPT_FILE_RE.match(path.stem)
    if not m:
        return None  # 白名单②：非 BV 命名（手工整理 md / 杂项）
    try:
        raw = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    if not all(mark in raw[:600] for mark in HEADER_MARKERS):
        return None  # 白名单③：缺 B站来源或机器提取标记
    bv = m.group(1)
    page = int(m.group(2)) if m.group(2) else 1
    doc_id = f"{bv}_p{page}" if m.group(2) else bv

    head, sep, body = raw.partition("\n---\n")
    if not sep:
        return None
    title_line = ""
    for line in head.splitlines():
        if line.startswith("# "):
            title_line = line[2:].strip()
            break
    tmeta = parse_title_meta(title_line)
    up = RE_META_UP.search(head)
    pub = RE_META_PUB.search(head)
    dur = RE_META_DUR.search(head)
    meth = RE_META_METHOD.search(head)
    part = ""
    pm = re.search(r"[（(](\d{1,2})[.、\s]*([^）)]{1,30})[）)]", title_line)
    if pm:
        part = pm.group(2).strip()
    up_name = up.group(1).strip() if up else ""
    # 来源分级（N0-2 / G4 数据层）：只写字段，检索层暂不按它过滤（M5 再做）
    source_kind = classify_source_kind(uploader=up_name, title=title_line)

    chunks: list[PlotChunk] = []
    for i, text in enumerate(split_body(body, chunk_size=chunk_size)):
        chunks.append(
            PlotChunk(
                hash=chunk_hash(text),
                text=text,
                doc_id=doc_id,
                bv=bv,
                page=page,
                part=part,
                title=title_line,
                uploader=up_name,
                pubdate=(pub.group(1) if pub else ""),
                duration=(dur.group(1) if dur else ""),
                version=tmeta["version"],
                arc=tmeta["arc"],
                chapter_no=tmeta["chapter_no"],
                chapter=tmeta["chapter"],
                lang=detect_lang(text),
                method=(meth.group(1).strip() if meth else ""),
                seq=i,
                source_kind=source_kind,
            )
        )
    return chunks or None
