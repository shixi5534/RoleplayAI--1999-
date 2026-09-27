# -*- coding: utf-8 -*-
"""零网关重建向量索引（用户裁决 C：保留 bge-m3，仅限嵌入用途）。

铁律背景：抽取=agent 直读原文写 JSON；构图=rebuild（禁 build，因 build 会对
未缓存块 ping 网关）。向量索引此前被裁决冻结，2026-09-21 用户裁决 C 解除：
本地 Ollama bge-m3 **仅用于嵌入**，网关 127.0.0.1:7863 仍然禁触。

本脚本因此只做三件事：
  1. 校验 graph.json 指纹与当前语料一致（失配即拒绝，防索引与图谱脱节）
  2. 本地嵌入全部块 + 全部实体名 → 重建 chunk_index.npz / entity_index.npz
  3. 把 index 统计同步进 reports/build_report.json（只改 index 键，其余不动）

写前自动备份（2026-09-27 #39 核验追加）：
  此前本脚本直接覆盖 *.npz，无任何备份；2026-09-27 12:06 的 entity_index
  就被就地覆盖且无可回退副本（只能靠 .prev 的 Sep 25 版本 + 重嵌重建）。
  现改为：覆盖前把现有索引复制为 `<name>.prev`（保留上一版），
  并把当前图的 SHA-16 记入 `index_backup_manifest.json` 以便对账。

全程唯一网络访问目标是本地 Ollama（embed_base_url），无任何云端调用。
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from compendium_rag import pipeline as P  # noqa: E402
from compendium_rag.config import get_settings  # noqa: E402
from compendium_rag.corpus import corpus_fingerprint  # noqa: E402
from compendium_rag.embedder import OllamaEmbedder  # noqa: E402
from compendium_rag.extract import PROMPT_VERSION  # noqa: E402
from compendium_rag.graph_store import GraphStore, fingerprint_of  # noqa: E402
from compendium_rag.retriever import ChunkIndex, EntityVectorIndex  # noqa: E402

logger = logging.getLogger("rebuild_indexes")


def _sha16(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def _backup_existing(paths: list[Path], manifest_path: Path, note: str) -> dict:
    """覆盖前把现有索引另存为 <name>.prev（原子替换），并记录对账清单。

    只备份**已存在**的文件；不存在（首次构建）则跳过。
    """
    backed: dict[str, dict[str, str]] = {}
    for p in paths:
        prev = p.with_suffix(p.suffix + ".prev")
        if not p.exists():
            logger.info("备份跳过（不存在，视为首次构建）: %s", p.name)
            continue
        before = _sha16(p)
        shutil.copy2(p, prev)
        backed[p.name] = {"sha16_before_overwrite": before,
                          "prev_path": prev.name,
                          "prev_sha16": _sha16(prev)}
        logger.info("已备份 %s → %s（覆盖前 SHA16=%s）", p.name, prev.name, before)
    manifest = {"backed_up_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "note": note, "files": backed}
    if backed:
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2),
                                 encoding="utf-8")
        logger.info("备份清单 → %s", manifest_path)
    return manifest


async def run() -> int:
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)-7s %(message)s",
                        datefmt="%H:%M:%S")
    s = get_settings()
    s.ensure_dirs()

    # ── 1. 指纹守卫 ──
    graph = GraphStore.load(s.graph_path)
    chunks = P.load_chunks(s)
    fp = fingerprint_of(corpus_fingerprint(P.load_chapters(s)),
                        s.llm_model, PROMPT_VERSION, s.chunk_chars)
    ok, why = graph.check_fingerprint(fp)
    if not ok:
        logger.error("指纹失配，拒绝建索引：%s", why)
        logger.error("graph.json 不是当前语料/配置的产物；先跑 `rebuild` 重建图谱。")
        return 2
    logger.info("指纹校验通过；块=%d 实体=%d 边=%d",
                len(chunks), len(graph.entities), len(graph.edges))

    # ── 2. 本地嵌入 + 落盘 ──
    # 写前备份：先把现有索引存为 .prev（#39 核验追加，防无备份就地覆盖）
    ep = s.data_dir / "entity_index.npz"
    _backup_existing(
        [s.index_path, ep],
        s.reports_dir / "index_backup_manifest.json",
        note=f"rebuild_indexes 覆盖前备份；graph_sha16={_sha16(s.graph_path)}")

    t0 = time.time()
    async with OllamaEmbedder(s.embed_base_url, s.embed_model,
                              s.embed_timeout, concurrency=4) as emb:
        dim = await emb.probe()
        logger.info("嵌入模型=%s 维度=%d（Ollama=%s）",
                    s.embed_model, dim, s.embed_base_url)

        # 块向量：文本前缀章节语境，提升语义区分度（与 build 阶段口径一致）
        texts = [f"{c.chapter_title}｜{c.scene_title}\n{c.text}" if c.scene_title
                 else f"{c.chapter_title}\n{c.text}" for c in chunks]
        vecs = await emb.embed(texts)
        ChunkIndex.build([c.chunk_id for c in chunks], vecs).save(s.index_path)
        logger.info("块索引 %d 条 → %s（%.1fs）",
                    len(vecs), s.index_path, time.time() - t0)

        eids = list(graph.entities.keys())
        names = [graph.entities[e].name for e in eids]
        t1 = time.time()
        evecs = await emb.embed(names) if names else []
        if evecs:
            EntityVectorIndex.build(eids, names, evecs).save(ep)
        logger.info("实体索引 %d 条 → %s（%.1fs）", len(evecs), ep, time.time() - t1)

    # ── 3. 同步 build_report.json 的 index 字段 ──
    istats = {"embed_model": s.embed_model, "embed_dim": dim,
              "chunk_vectors": len(vecs), "entity_vectors": len(evecs),
              "seconds": round(time.time() - t0, 1),
              "note": "裁决 C：由 compendium_rag_rebuild_indexes.py 零网关重建"}
    rp = s.reports_dir / "build_report.json"
    if rp.exists():
        rep = json.loads(rp.read_text(encoding="utf-8"))
        rep["index"] = istats
        rp.write_text(json.dumps(rep, ensure_ascii=False, indent=2),
                      encoding="utf-8")
        logger.info("已同步 index 统计 → %s", rp)
    else:
        logger.warning("build_report.json 不存在，跳过同步（图谱统计仍需从 graph.json 实测）")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(run()))
