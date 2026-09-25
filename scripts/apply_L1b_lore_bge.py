# -*- coding: utf-8 -*-
"""L1-b 执行脚本：lore 层瘦身 + 全命名空间换 bge-m3(1024)。

决策依据（2026-09-16）：
  1. 实测 lore 库 92.1% 是英文 ASR（非"全中文"），且与剧情语料**同源**
     （Top 来源均为 BV1eo4y1u7aW 系列，抽样 40 条中 80% 内容片段能在剧情语料找到）；
  2. 角色卡 knowledge_scope 把 lore 定位为「角色设定资料」（_source_label），
     但库里 92% 是剧情转写 → **定位错配**；
  3. A/B 实测（ab_lore_embed.py，同池 10 题）：nomic hit@5 70% vs bge-m3 **90%**，
     且 nomic 的失败模式是"匹配标题汉字而非语义"（把"暴雨是什么"匹配到 1.6 版本全剧情）；
  4. KnowledgeBase 用**单一 embedder**，同实例内不能混维度 → 必须整库统一模型。

做法：
  - lore：只保留 CJK≥0.3 的**中文设定条目**（461 条），换 bge-m3 重建；英文条目归档
  - events / web：条数极少（2 / 42），一并换 bge-m3 重建
  - 原子写盘 + 备份；英文条目落 _archive 可回退

用法：
    .venv/Scripts/python.exe -X utf8 scripts/apply_L1b_lore_bge.py --dry-run
    .venv/Scripts/python.exe -X utf8 scripts/apply_L1b_lore_bge.py --apply
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from roleplay.core.knowledge.embedder import OllamaEmbedder  # noqa: E402

KDIR = ROOT / "data" / "knowledge"
ARCHIVE = KDIR / "_archive"
LORE = KDIR / "lore_wu_ming_zhe.json"
CJK_MIN = 0.3
MODEL = "bge-m3"
TARGETS = ["lore_wu_ming_zhe.json", "events%3Awu_ming_zhe.json", "web.json"]


def cjk_ratio(t: str) -> float:
    if not t:
        return 0.0
    return len(re.findall(r"[\u4e00-\u9fff]", t)) / len(t)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    stamp = time.strftime("%Y%m%d_%H%M")
    emb = OllamaEmbedder(model=MODEL, base_url="http://localhost:11434", timeout=180.0)
    print(f"[model] {MODEL} dim={emb.dim}")

    plan: dict[str, dict] = {}
    for fn in TARGETS:
        p = KDIR / fn
        if not p.is_file():
            print(f"[skip] {fn} 不存在")
            continue
        data = json.loads(p.read_text(encoding="utf-8"))
        if fn == LORE.name:  # 注意：LORE 是 Path，fn 是字符串，必须比 name
            keep = [e for e in data if cjk_ratio(str(e.get("text") or "")) >= CJK_MIN]
            drop = [e for e in data if cjk_ratio(str(e.get("text") or "")) < CJK_MIN]
            plan[fn] = {"path": p, "keep": keep, "drop": drop, "total": len(data)}
            print(f"[plan] {fn}: {len(data)} → 保留 {len(keep)}（中文设定）｜归档 {len(drop)}（英文 ASR）")
        else:
            plan[fn] = {"path": p, "keep": data, "drop": [], "total": len(data)}
            print(f"[plan] {fn}: {len(data)} 条（全保留）")

    if not args.apply:
        print("\n[dry-run] 加 --apply 执行")
        return 0

    ARCHIVE.mkdir(parents=True, exist_ok=True)
    for fn, info in plan.items():
        info["path"].parent.mkdir(parents=True, exist_ok=True)
        # 备份
        shutil.copy2(info["path"], ARCHIVE / f"{fn.replace('%3A', '_')}.pre_L1b_{stamp}.bak")
        # 归档被移除的条目
        if info["drop"]:
            (ARCHIVE / f"lore_en_asr_retired_{stamp}.json").write_text(
                json.dumps(info["drop"], ensure_ascii=False), encoding="utf-8")
            print(f"[archive] {fn} 归档 {len(info['drop'])} 条 → "
                  f"lore_en_asr_retired_{stamp}.json")

    total = 0
    for fn, info in plan.items():
        items = info["keep"]
        if not items:
            continue
        texts = [str(e.get("text") or "") for e in items]
        vecs = emb.embed(texts)
        for e, v in zip(items, vecs):
            e["vec"] = v
        info["path"].write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")
        total += len(items)
        print(f"[apply] {fn}: 重嵌入 {len(items)} 条（dim={len(vecs[0])}）")

    print(f"\n[done] 共重嵌入 {total} 条；模型 {MODEL}")
    print("[next] 需同步设置 ROLEPLAY_EMBED_MODEL=bge-m3，否则查询侧仍是 768 维")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
