"""一次性迁移脚本：rag 项目 Chroma 知识库 → roleplay-ai 知识库（docs 命名空间）。

背景
----
- rag 项目（C:\\Users\\Lenovo\\Desktop\\rag）与 roleplay-ai 合并知识库，
  以 roleplay-ai 为主。两项目嵌入器不兼容（rag: all-MiniLM-L6-v2 384 维；
  roleplay-ai: Ollama nomic-embed-text / HashingEmbedder 768 维），
  因此本脚本只搬「文本 + 元数据」，在 roleplay-ai 侧重新向量化。
- 直读 Chroma 持久化文件（PersistentClient），无需启动 rag 后端。

用法
----
  python scripts/migrate_rag_kb.py --rag-dir <rag_chroma_dir> [--dry-run] [--reset] [--ns docs]
    --dry-run  只打印统计，不写入
    --reset    迁移前先按 origin=="rag" 清理 roleplay-ai docs 中已迁移的数据（幂等重跑）
    --ns       目标命名空间（默认 docs）

运行环境：rag 项目的 conda 环境（含 chromadb），通过 sys.path 注入 roleplay-ai 的 src。
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import uuid
from pathlib import Path

ROLEPLAY_SRC = Path(__file__).resolve().parents[1] / "src"
ROLEPLAY_DIR = Path(__file__).resolve().parents[1]

# 注入 roleplay-ai 源码路径
sys.path.insert(0, str(ROLEPLAY_SRC))

from roleplay.core.knowledge import KnowledgeBase  # noqa: E402
from roleplay.core.knowledge.embedder import build_embedder  # noqa: E402
from roleplay.config import get_settings  # noqa: E402

ORIGIN_TAG = "rag"


def load_rag_chunks(rag_dir: str | Path) -> list[dict]:
    """读取 rag Chroma 全部物理库的 documents + metadatas。

    返回 [{text, meta, rag_db}]；跳过空 collection。
    """
    import chromadb

    root = Path(rag_dir)
    if not root.is_dir():
        raise FileNotFoundError(f"rag Chroma 目录不存在：{root}")
    out: list[dict] = []
    for db_dir in sorted(root.iterdir()):
        if not db_dir.is_dir():
            continue
        db_name = db_dir.name
        try:
            client = chromadb.PersistentClient(path=str(db_dir))
            cols = client.list_collections()
        except Exception as exc:  # noqa: BLE001
            print(f"[skip] 无法打开物理库 {db_name}: {exc}")
            continue
        for col in cols:
            try:
                n = col.count()
                if n == 0:
                    continue
                data = col.get(include=["documents", "metadatas"])
            except Exception as exc:  # noqa: BLE001
                print(f"[skip] 读取 collection {col.name} 失败: {exc}")
                continue
            docs = data.get("documents") or []
            metas = data.get("metadatas") or []
            for i, text in enumerate(docs):
                if not text or not str(text).strip():
                    continue
                out.append(
                    {
                        "text": str(text),
                        "meta": dict(metas[i]) if i < len(metas) and metas[i] else {},
                        "rag_db": db_name,
                    }
                )
    return out


def migrate(
    rag_dir: str | Path,
    namespace: str = "docs",
    dry_run: bool = False,
    reset: bool = False,
    max_items: int = 5000,
) -> None:
    settings = get_settings()
    kb = KnowledgeBase(embedder=build_embedder(settings), persist_dir=settings.knowledge_dir)

    # 前置：统计 roleplay-ai 现有数据
    existing = len(kb.list_items(namespace))
    print(f"[roleplay-ai] {namespace} 现有条目：{existing}")

    if reset and not dry_run:
        removed = kb.filter_remove(
            namespace,
            lambda it: it.get("meta", {}).get("origin") == ORIGIN_TAG,
        )
        print(f"[reset] 已清理旧迁移数据：{removed} 条")

    chunks = load_rag_chunks(rag_dir)
    print(f"[rag] 读取到 {len(chunks)} 条文本（来自 Chroma documents）")
    if dry_run:
        # 统计各物理库分布
        by_db: dict[str, int] = {}
        for c in chunks:
            by_db[c["rag_db"]] = by_db.get(c["rag_db"], 0) + 1
        print("[dry-run] 各物理库条目数：")
        for db, n in sorted(by_db.items()):
            print(f"  {db}: {n}")
        print("[dry-run] 未写入任何数据。")
        return
    if not chunks:
        print("[rag] 无数据可迁移，跳过。")
        return
    if len(chunks) > max_items:
        print(f"[warn] 条目数 {len(chunks)} 超过上限 {max_items}，截断。")
        chunks = chunks[:max_items]

    # 分批嵌入入库（Ollama 批量接口，避免一次性大请求）
    BATCH = 64
    doc_groups: dict[str, dict] = {}
    total = 0
    for start in range(0, len(chunks), BATCH):
        batch = chunks[start : start + BATCH]
        texts = [c["text"] for c in batch]
        metas: list[dict] = []
        for c in batch:
            m = dict(c["meta"])
            m["origin"] = ORIGIN_TAG
            m["rag_db"] = c["rag_db"]
            m.setdefault("title", f"rag-{c['rag_db']}")
            # 每批内的文本生成一个共享 doc_id（同物理库同批视为一篇）：
            # 更精细的粒度按源 source 分组，见下方 dedup 逻辑
            m.setdefault("doc_id", str(uuid.uuid4()))
            metas.append(m)
        ids = kb.add(texts, metadatas=metas, namespace=namespace)
        total += len(ids)
        # 按 doc_id 统计
        for m in metas:
            did = m["doc_id"]
            d = doc_groups.setdefault(did, {"doc_id": did, "title": m.get("title", did), "chunk_count": 0, "rag_db": m["rag_db"]})
            d["chunk_count"] += 1
        print(f"[migrate] 批次 {start // BATCH + 1}: +{len(ids)} 条（累计 {total}）")

    # 落盘核对
    after = len(kb.list_items(namespace))
    print(f"[roleplay-ai] 迁移后 {namespace} 条目：{after}（增量 {after - existing}）")
    print(f"[doc-groups] 生成文档组 {len(doc_groups)} 篇：")
    for d in sorted(doc_groups.values(), key=lambda x: x["chunk_count"], reverse=True):
        print(f"  {d['title']} [{d['rag_db']}]  {d['chunk_count']} 块")

    # 校验：增量应等于迁移条目数
    if after - existing != total:
        print("[warn] 增量与迁移条数不一致，请检查！")
    else:
        print("[ok] 迁移完成，增量与迁移条数一致。")


def main() -> None:
    parser = argparse.ArgumentParser(description="迁移 rag Chroma 知识库到 roleplay-ai")
    parser.add_argument("--rag-dir", default=r"C:\Users\Lenovo\Desktop\rag\data\chroma",
                        help="rag Chroma 持久化目录")
    parser.add_argument("--ns", default="docs", help="目标命名空间（默认 docs）")
    parser.add_argument("--dry-run", action="store_true", help="只统计不写入")
    parser.add_argument("--reset", action="store_true", help="迁移前清理旧 rag 数据（幂等）")
    parser.add_argument("--max-items", type=int, default=5000, help="最大迁移条数")
    args = parser.parse_args()
    migrate(args.rag_dir, args.ns, args.dry_run, args.reset, args.max_items)


if __name__ == "__main__":
    main()
