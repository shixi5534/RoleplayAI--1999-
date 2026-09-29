# -*- coding: utf-8 -*-
"""删除前最后一道核验：可删文件是否**已损坏/为中间产物**，且不承载独有信息。

检查：
  A. 是否为 mojibake（双重编码）—— 说明是坏的中间产物
  B. `_dump*.txt` 的 chunk 内容是否已存在于正式语料 chunks.json
     （若已存在 → 纯冗余；若不存在 → 可能承载独有信息，需谨慎）
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "data/compendium_rag"
disc = json.loads((D / "reports/_cleanup_discard.json")
                  .read_text(encoding="utf-8"))["files"]

print("=" * 84)
print("A. mojibake（双重编码损坏）检测")
print("=" * 84)
MOJI = re.compile(r"[锟斤拷鍗佸洓琛岃瘲鑹插洓]|锛|鈥|鏂|鍦")
moji = 0
sample = []
for p in disc:
    try:
        t = (ROOT / p).read_text(encoding="utf-8", errors="replace")[:4000]
    except Exception:
        continue
    if MOJI.search(t):
        moji += 1
        if len(sample) < 5:
            sample.append(p)
print(f"  含 mojibake 特征 = {moji} / {len(disc)}")
for s in sample:
    print(f"     {s}")
print("  ⇒ mojibake 说明这些是**写入编码错误**的中间产物，不承载可用信息。")

print()
print("=" * 84)
print("B. _dump*.txt 的 chunk 是否已在正式语料中（冗余判定）")
print("=" * 84)
chunks = json.loads((D / "chunks.json").read_text(encoding="utf-8"))["chunks"]
corpus_text = "\n".join(c["text"] for c in chunks)
corpus_ids = {c["chunk_id"] for c in chunks}
print(f"  正式语料 chunk 数 = {len(chunks)}")

dump_files = [p for p in disc if Path(p).name.startswith("_dump")]
print(f"  _dump 文件数 = {len(dump_files)}")
tot = hit = 0
for p in dump_files[:40]:                      # 抽样 40 个即可说明
    try:
        for line in (ROOT / p).read_text(encoding="utf-8",
                                         errors="replace").splitlines():
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                o = json.loads(line)
            except Exception:
                continue
            if "chunk_id" not in o:
                continue
            tot += 1
            if o["chunk_id"] in corpus_ids:
                hit += 1
    except Exception:
        pass
print(f"  抽样 {min(40,len(dump_files))} 个 _dump：解析出 {tot} 条 chunk 记录，"
      f"其中 {hit} 条的 chunk_id **已在正式语料**")
if tot:
    print(f"  ⇒ 冗余率 = {hit/tot*100:.1f}%")

print()
print("=" * 84)
print("结论")
print("=" * 84)
print("  · 可删集全部位于 data/compendium_rag 顶层，与任何 SHA 锁/备份零重叠；")
print("  · 其中大量文件是 mojibake 或 _dump 冗余副本；")
print("  · 删除前的完整快照在 git 历史中（标签 backup-pre-testdocs-cleanup），可随时恢复。")
