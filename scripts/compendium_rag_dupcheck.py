# -*- coding: utf-8 -*-
"""抽取缓存查重 + 按版本剧情分组的进度统计。

三件事：
  1. 批次文件（_agent_batchNN.json）之间的重复 key——同 key 重复提交=浪费的重复抽取
  2. 孤儿缓存——缓存里有、但当前分块口径下没有任何块对应的 key
     （旧 prompt 版本 / 旧 chunk 参数的产物，构图永远不会用到）
  3. 待抽块按「版本剧情」前缀（chunk_id 冒号前的部分）分组计数，
     供按版本逐个抽取排程。

零网络，纯本地。用法：& $py scripts/compendium_rag_dupcheck.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from compendium_rag import pipeline as P  # noqa: E402
from compendium_rag.config import get_settings  # noqa: E402
from compendium_rag.extract import PROMPT_VERSION, ExtractionCache, cache_key  # noqa: E402


def main() -> int:
    s = get_settings()
    chunks = P.load_chunks(s)
    key_of = {c.chunk_id: cache_key(c, s.llm_model, PROMPT_VERSION)
              for c in chunks}
    cache = ExtractionCache(s.cache_dir)
    cached = {cid for cid, k in key_of.items()
              if cache.get_raw(k) is not None}

    # ── 1. 批次文件之间的重复 key ──
    batch_keys: dict[str, list[str]] = defaultdict(list)   # key -> [batch file]
    batch_key_chunk: dict[str, str] = {}
    id_by_key = {k: cid for cid, k in key_of.items()}
    for f in sorted(s.data_dir.glob("_agent_batch*.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            print(f"⚠ 无法解析 {f.name}: {e}")
            continue
        for k in d:
            batch_keys[k].append(f.name)
            batch_key_chunk.setdefault(k, id_by_key.get(k, f"<未知块 key={k}>"))
    dup_in_batches = {k: v for k, v in batch_keys.items() if len(v) > 1}
    print(f"== 批次文件重复 key ==")
    if dup_in_batches:
        for k, files in sorted(dup_in_batches.items()):
            print(f"  {k} ({batch_key_chunk.get(k, '?')}) ← {', '.join(files)}")
        print(f"  共 {len(dup_in_batches)} 个 key 被重复提交（缓存按内容哈希，后写覆盖先写，无脏数据）")
    else:
        print("  无")

    # ── 2. 孤儿缓存 ──
    live_keys = set(key_of.values())
    disk_keys = set()
    for sub in s.cache_dir.iterdir():
        if sub.is_dir():
            disk_keys.update(p.stem for p in sub.glob("*.json"))
    orphans = sorted(disk_keys - live_keys)
    print(f"\n== 孤儿缓存（磁盘有、当前口径不认） ==")
    if orphans:
        for k in orphans[:20]:
            print(f"  {k}")
        if len(orphans) > 20:
            print(f"  … 共 {len(orphans)} 个")
        print(f"  共 {len(orphans)} 个（多为旧 prompt 版本产物，不参与构图；可留可清）")
    else:
        print("  无")

    # ── 3. 按版本剧情分组 ──
    print(f"\n== 抽取进度：{len(cached)}/{len(chunks)} "
          f"({len(cached)/len(chunks)*100:.1f}%) ==")
    groups: dict[str, dict[str, int]] = defaultdict(lambda: {"done": 0, "todo": 0})
    for c in chunks:
        story = c.chunk_id.split(":", 1)[0]
        groups[story]["done" if c.chunk_id in cached else "todo"] += 1
    rows = sorted(groups.items(),
                  key=lambda kv: (-kv[1]["todo"], kv[0]))
    print(f"{'版本剧情':<44}{'待抽':>6}{'已完成':>6}")
    for story, g in rows:
        if g["todo"] or g["done"]:
            print(f"{story:<44}{g['todo']:>6}{g['done']:>6}")
    todo_total = sum(g["todo"] for g in groups.values())
    print(f"{'合计':<44}{todo_total:>6}{len(chunks)-todo_total:>6}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
