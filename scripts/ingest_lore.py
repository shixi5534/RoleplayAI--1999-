# -*- coding: utf-8 -*-
"""角色资料导入 CLI：目录/文件/URL/SQLite → 角色专属知识库命名空间。

用法（在项目根目录执行）：
  python scripts/ingest_lore.py --character wu_ming_zhe --dir data/lore/wu_ming_zhe
  python scripts/ingest_lore.py --character wu_ming_zhe --url https://example.com/page
  python scripts/ingest_lore.py --character wu_ming_zhe --db data/x.db --table events

导入后自动把角色卡的 knowledge_scope 绑定到 lore_<character> 命名空间
（保留 events/episodic 公共记忆），实现「导入即生效」。
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from roleplay.config import get_settings  # noqa: E402
from roleplay.core.knowledge import (  # noqa: E402
    CharacterStore,
    build_knowledge_base,
    ingest_directory,
    ingest_file,
    ingest_sqlite,
    ingest_url,
    lore_namespace,
)


def main() -> int:
    ap = argparse.ArgumentParser(description="角色资料导入 RAG 知识库")
    ap.add_argument("--character", required=True, help="角色 id（characters 目录中的文件名）")
    ap.add_argument("--dir", help="导入目录（批量，支持 md/txt/html/json/csv）")
    ap.add_argument("--file", help="导入单个文件")
    ap.add_argument("--url", help="导入网页 URL")
    ap.add_argument("--db", help="SQLite 数据库路径")
    ap.add_argument("--table", help="SQLite 表名")
    ap.add_argument("--query", help="SQLite 自定义 SELECT")
    ap.add_argument("--fresh", action="store_true", help="导入前清空该角色命名空间")
    ap.add_argument("--tone", help="顺带更新角色卡语气字段")
    args = ap.parse_args()

    settings = get_settings()
    kb = build_knowledge_base(settings)
    ns = lore_namespace(args.character)

    if args.fresh:
        kb.clear_namespace(ns)
        print(f"[fresh] 已清空命名空间 {ns}")

    total = 0
    if args.dir:
        r = ingest_directory(kb, args.dir, namespace=ns, character_id=args.character,
                             chunk_size=settings.chunk_size)
        print(f"[dir] {args.dir} → {r['stored']} 块（{len(r['files'])} 个文件：{r['files']}）")
        total += r["stored"]
    if args.file:
        r = ingest_file(kb, args.file, namespace=ns, character_id=args.character,
                        chunk_size=settings.chunk_size)
        print(f"[file] {args.file} → {r['stored']} 块")
        total += r["stored"]
    if args.url:
        r = ingest_url(kb, args.url, namespace=ns, character_id=args.character,
                       chunk_size=settings.chunk_size)
        print(f"[url] {args.url} → {r['stored']} 块")
        total += r["stored"]
    if args.db:
        r = ingest_sqlite(kb, args.db, table=args.table, query=args.query,
                          namespace=ns, character_id=args.character)
        print(f"[db] {args.db} → {r['stored']} 块")
        total += r["stored"]
    if total == 0 and not args.fresh:
        print("未指定任何来源（--dir/--file/--url/--db）", file=sys.stderr)
        return 2

    # 绑定角色卡知识范围（导入即生效）
    store = CharacterStore(settings=settings)
    card = store.get(args.character)
    if card is None:
        print(f"[warn] 角色 {args.character} 不存在，跳过 knowledge_scope 绑定")
    else:
        scope = list(dict.fromkeys([ns, "events", "episodic"]))
        payload: dict = {"knowledge_scope": scope}
        if args.tone:
            payload["tone"] = args.tone
        store.update(args.character, payload)
        print(f"[card] {args.character}.knowledge_scope = {scope}"
              + (f"，tone 已更新" if args.tone else ""))

    print(f"[done] 共入库 {total} 块 → 命名空间 {ns}；当前统计：{kb.count()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
