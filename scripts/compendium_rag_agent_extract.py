# -*- coding: utf-8 -*-
"""由 agent 自己抽取：把结果写进 pipeline 能读的缓存格式。

背景：云端网关额度耗尽，不再依赖任何外部端点。本脚本只做两件事：
  1. `pending`  —— 列出还没抽的块（含提示词），供 agent 读取
  2. `submit`   —— 把 agent 产出的抽取结果按 ExtractionCache 格式落盘

缓存格式与 ``compendium_rag.extract.ExtractionCache.put_raw`` 完全一致，
因此 ``build`` / ``rebuild`` 能直接复用，无需改任何库代码。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from compendium_rag import pipeline as P  # noqa: E402
from compendium_rag.config import get_settings  # noqa: E402
from compendium_rag.extract import (NORMALIZER_VERSION, PROMPT_VERSION,  # noqa: E402
                                    ExtractionCache, SYSTEM_PROMPT,
                                    build_user_prompt, cache_key)


def cmd_pending(args) -> int:
    """输出待抽取块（JSON 行），供 agent 逐块读取。

    --story 按版本剧情前缀过滤（chunk_id 冒号前的部分），
    一轮只抽一个版本剧情，抽完再开下一个。
    """
    s = get_settings()
    chunks = P.load_chunks(s)
    cache = ExtractionCache(s.cache_dir)
    todo = []
    for c in chunks:
        if args.story and not c.chunk_id.split(":", 1)[0].startswith(args.story):
            continue
        key = cache_key(c, s.llm_model, PROMPT_VERSION)
        if cache.get_raw(key) is None:
            todo.append((c, key))
    todo = todo[args.start:args.start + args.limit]
    print(f"# 待抽取总数（本批 {len(todo)}）", file=sys.stderr)
    for c, key in todo:
        print(json.dumps({"key": key, "chunk_id": c.chunk_id,
                          "chars": len(c.text), "text": c.text},
                         ensure_ascii=False))
    return 0


def cmd_prompt(args) -> int:
    """打印系统提示词 + 指定块的 user prompt（供 agent 照此抽取）。"""
    s = get_settings()
    chunks = {c.chunk_id: c for c in P.load_chunks(s)}
    print("===== SYSTEM =====")
    print(SYSTEM_PROMPT)
    print("\n===== USER =====")
    print(build_user_prompt(chunks[args.chunk_id]))
    return 0


def cmd_submit(args) -> int:
    """把 agent 的抽取结果落盘。输入是 JSON 文件：{key: {entities,relations}, ...}"""
    s = get_settings()
    cache = ExtractionCache(s.cache_dir)
    payload = json.loads(Path(args.file).read_text(encoding="utf-8"))
    n = 0
    for key, raw in payload.items():
        cache.put_raw(key, raw)
        n += 1
    print(f"已写入缓存 {n} 条 → {cache.root}")
    return 0


def cmd_status(args) -> int:
    s = get_settings()
    chunks = P.load_chunks(s)
    cache = ExtractionCache(s.cache_dir)
    done = sum(1 for c in chunks
               if cache.get_raw(cache_key(c, s.llm_model, PROMPT_VERSION))
               is not None)
    pct = done / max(1, len(chunks)) * 100
    print(f"已抽取 {done}/{len(chunks)} ({pct:.1f}%)  "
          f"剩 {len(chunks) - done}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("pending")
    p.add_argument("--start", type=int, default=0)
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--story", type=str, default="",
                   help="按版本剧情前缀过滤（chunk_id 冒号前部分）")
    p.set_defaults(fn=cmd_pending)
    p = sub.add_parser("prompt"); p.add_argument("chunk_id"); p.set_defaults(fn=cmd_prompt)
    p = sub.add_parser("submit"); p.add_argument("file"); p.set_defaults(fn=cmd_submit)
    p = sub.add_parser("status"); p.set_defaults(fn=cmd_status)
    a = ap.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
