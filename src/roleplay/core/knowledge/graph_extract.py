"""实体/关系抽取器（GraphRAG 离线索引层）。

设计（docs/GRAPHRAG加强计划书.md §4）：
- GraphExtractor：LLM 按 chunk 抽取实体与关系，三级 JSON 解析兜底、永不抛出
  （复用 event_extractor 的健壮范式）；抽取/对话分模型配置（D5，
  照搬 LightRAG「抽取用非思考快速模型」建议）。
- GraphCache：chunk 内容 sha1 → 抽取结果的幂等缓存，重跑只处理新增/变更块
  （照搬 bilibili_lore_ingest 的重跑幂等模式）。
- build_graph_from_chunks：批量（Semaphore 限流）+ 失败收集 + 实体归并落库。
"""
from __future__ import annotations

import asyncio
import json
import logging
import re
from pathlib import Path

from ..llm.base import LLMPort
from .graph_store import (
    GraphStore,
    build_local_endpoint_map,
    chunk_text_hash,
    resolve_endpoint,
)
from .relation_vocab import (
    RELATION_RULES_PROMPT,
    canonicalize_relation,
    vocab_prompt_block,
)

logger = logging.getLogger(__name__)

# 抽取提示词（计划书附录 A）：canonical 名 + 别名收编 + 置信度纪律 + 严格 JSON。
# 关系谓语受控词表（relation_vocab）直接枚举在提示词里——源头约束，见
# docs/GRAPHRAG加强计划书.md 关系命名治理章节：模型只能从词表里选谓语，
# 选不出就丢弃；归一化层（canonicalize_relation）再兜一道底。
EXTRACT_SYSTEM_PROMPT = (
    "你是知识图谱构建助手。从下面的角色设定/剧情文本中抽取实体与关系，只输出单行 JSON："
    '{"entities": [{"name": "<canonical 称呼>", '
    '"type": "角色|物品|地点|组织|概念|事件", "aliases": ["<同指的曾用名/代称/昵称>"]}], '
    '"relations": [{"src": "<实体名>", "dst": "<实体名>", "relation": "<简短中文谓语>", '
    '"confidence": 0.0-1.0}]}'
    "规则："
    "- 实体名取文中最正式的称呼；代词不作为实体，但它的同指别名要收进 aliases；"
    + RELATION_RULES_PROMPT
    + "（受控词表：" + vocab_prompt_block() + "）"
    "- confidence：文中明确陈述 ≥0.9；强推断 0.6-0.8；模糊 ≤0.5 直接不输出；"
    "- src/dst 必须出现在 entities 的 name 或 aliases 中；"
    '- 没有可抽取内容时输出 {"entities":[],"relations":[]}。'
)


def _clamp_confidence(v) -> float:
    try:
        return max(0.0, min(1.0, float(v)))
    except (TypeError, ValueError):
        return 0.5


def normalize_extraction(raw) -> tuple[list[dict], list[dict]]:
    """清洗 LLM 抽取输出 → (entities, relations)。

    实体：name 必填；别名/类型清洗。关系：src/dst/relation 必填、confidence 钳制。
    关系的 src/dst 允许出现在实体 name 或 aliases 中（不满足则丢弃，防悬空引用）。
    """
    if not isinstance(raw, dict):
        return [], []
    entities: list[dict] = []
    known: set[str] = set()
    for item in raw.get("entities") or []:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or "").strip()
        if not name:
            continue
        aliases = [
            str(a).strip()
            for a in (item.get("aliases") or [])
            if isinstance(a, str) and str(a).strip()
        ]
        entities.append(
            {
                "name": name,
                "type": str(item.get("type") or "").strip(),
                "aliases": aliases,
            }
        )
        known.add(name)
        known.update(aliases)

    relations: list[dict] = []
    for item in raw.get("relations") or []:
        if not isinstance(item, dict):
            continue
        src = str(item.get("src") or item.get("head") or "").strip()
        dst = str(item.get("dst") or item.get("tail") or "").strip()
        relation = str(item.get("relation") or "").strip()
        if not src or not dst or not relation:
            continue
        if src not in known or dst not in known:
            continue
        # 谓语卫生过滤（关系命名治理第二段）：映射不到 canonical 的一律丢弃——
        # 覆盖否定短语（「不隶属于」）、超长谓语（>8 字）、含标点/拉丁字符、
        # 垃圾黑名单。同义词在此归一（「属于」→「隶属」），入库即受控。
        canon = canonicalize_relation(relation)
        if canon is None:
            continue
        relations.append(
            {
                "src": src,
                "dst": dst,
                "relation": canon,
                "confidence": _clamp_confidence(item.get("confidence", 0.7)),
            }
        )
    return entities, relations


class GraphExtractor:
    """LLM 实体关系抽取器：单块输入 → {"entities": [...], "relations": [...]}。"""

    def __init__(self, *, llm: LLMPort | None = None, timeout: float = 12.0) -> None:
        self._llm = llm
        self._timeout = timeout

    @property
    def available(self) -> bool:
        return self._llm is not None

    async def extract(self, text: str, system: str | None = None) -> dict | None:
        """抽取单块文本。失败/超时/解析不出 → None（调用方记入 failed 清单）。

        system：覆盖默认抽取提示词（剧情层按语种传中文/英文提示词，见
        plot_graph.prompt_for_lang）；None 时用默认（lore 层）提示词。
        """
        if self._llm is None or not (text or "").strip():
            return None
        try:
            raw = await asyncio.wait_for(
                self._llm.generate(
                    system=system or EXTRACT_SYSTEM_PROMPT, user=text, temperature=0.0
                ),
                timeout=self._timeout,
            )
        except asyncio.TimeoutError:
            logger.warning("图谱抽取超时（%.1fs）", self._timeout)
            return None
        except Exception as exc:  # noqa: BLE001
            logger.warning("图谱抽取失败：%s", exc)
            return None
        parsed = self._parse_json(raw or "")
        if parsed is None:
            return None
        entities, relations = normalize_extraction(parsed)
        return {"entities": entities, "relations": relations}

    def _parse_json(self, raw: str) -> dict | None:
        """三级解析：json.loads → 剥围栏 → 正则抽首个 JSON 对象。"""
        text = (raw or "").strip()
        if not text:
            return None
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text).strip()
            text = re.sub(r"\s*```$", "", text).strip()
        try:
            obj = json.loads(text)
            if isinstance(obj, dict):
                return obj
        except (json.JSONDecodeError, TypeError, ValueError):
            pass
        for m in re.finditer(r"\{.*\}", text, re.DOTALL):
            try:
                obj = json.loads(m.group(0))
                if isinstance(obj, dict):
                    return obj
            except (json.JSONDecodeError, TypeError, ValueError):
                continue
        logger.warning("图谱抽取输出解析失败：%r", raw[:160])
        return None


class GraphCache:
    """chunk 哈希 → 抽取结果的幂等缓存（<cache_dir>/<hash>.json，单文件单块）。"""

    def __init__(self, directory: str | Path) -> None:
        self._dir = Path(directory)

    def get(self, chunk_hash: str) -> dict | None:
        path = self._dir / f"{chunk_hash}.json"
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else None
        except (OSError, ValueError):
            return None

    def put(self, chunk_hash: str, data: dict) -> None:
        try:
            if not self._dir.exists():
                self._dir.mkdir(parents=True, exist_ok=True)
            (self._dir / f"{chunk_hash}.json").write_text(
                json.dumps(data, ensure_ascii=False), encoding="utf-8"
            )
        except OSError as exc:  # noqa: BLE001
            logger.warning("抽取缓存写入失败 %s：%s", chunk_hash, exc)

    def clear(self) -> int:
        """清空缓存目录，返回删除文件数（--rebuild 用）。"""
        removed = 0
        if not self._dir.exists():
            return 0
        for p in self._dir.glob("*.json"):
            try:
                p.unlink()
                removed += 1
            except OSError:  # noqa: BLE001
                pass
        return removed


async def build_graph_from_chunks(
    chunks: list[tuple[str, dict]],
    store: GraphStore,
    extractor: GraphExtractor,
    cache: GraphCache,
    *,
    batch: int = 8,
    limit: int | None = None,
) -> dict:
    """把 KB chunk 列表构建进图谱（幂等：缓存命中不调 LLM）。

    chunks: [(text, meta)]，meta 至少含 doc_id（证据溯源）。
    返回统计 {chunks, extracted, cached, failed, skipped}。
    """
    if limit is not None:
        chunks = chunks[: max(0, limit)]
    sem = asyncio.Semaphore(max(1, batch))
    stats = {"chunks": len(chunks), "extracted": 0, "cached": 0, "failed": 0, "skipped": 0}
    failed: list[str] = []

    async def _one(text: str, meta: dict) -> None:
        chash = chunk_text_hash(text)
        doc_id = str(meta.get("doc_id") or "legacy")
        ns = str(meta.get("namespace") or "lore")
        data = cache.get(chash)
        if data is None:
            async with sem:
                data = await extractor.extract(text)
            if data is None:
                stats["failed"] += 1
                failed.append(chash)
                return
            cache.put(chash, data)
            stats["extracted"] += 1
        else:
            stats["cached"] += 1
        entities, relations = normalize_extraction(data)
        if not entities and not relations:
            stats["skipped"] += 1
            return
        store.upsert_entities(entities)
        # 关系端点先按本 chunk 的实体/别名局部解析（歧义别名 → 丢弃该关系），
        # 解析不到再回落全局别名索引。旧实现直接用全局索引，同一 chunk 内两个
        # 实体共享别名时会把关系挂到首注册实体上（错误主语）。
        local = build_local_endpoint_map(store, entities)
        for rel in relations:
            src_eid = resolve_endpoint(store, local, rel["src"])
            dst_eid = resolve_endpoint(store, local, rel["dst"])
            if not src_eid or not dst_eid or src_eid == dst_eid:
                continue
            store.upsert_edge(
                src=src_eid,
                dst=dst_eid,
                relation=rel["relation"],
                confidence=rel["confidence"],
                evidence=[{"ns": ns, "doc_id": doc_id, "hash": chash}],
                source="lore",
            )

    await asyncio.gather(*[_one(t, m) for t, m in chunks])
    if failed:
        logger.warning("图谱抽取失败 %d 块（可重跑续做）：%s", len(failed), failed[:5])
    return stats
