# -*- coding: utf-8 -*-
"""清理抽取缓存里的代词/泛指名词实体（约束①：代词不作实体）。

背景：本地 7B 模型违反抽取提示词，把 ``you / she / he / her / we / they /
girl / friend`` 等代词与泛指名词当成实体正名写入缓存，导致图谱出现 20 个
“代词实体”和 186 条无意义边，并抢占别名索引、污染 PPR 激活扩散。

本脚本回溯清理**缓存**（图谱的单一事实来源）：
  1. 丢弃正名命中 ``_PRONOUN_CANONICAL`` 的实体；
  2. 丢弃 src/dst 命中该集合的关系（否则会留下悬空边）；
  3. 被修改的缓存原文备份到 ``plot_cache_pronoun_bak/``，可回滚。

改完缓存后按常规流程回放重建即可（零 LLM 调用）：
  .venv/Scripts/python.exe scripts/fix_pronoun_entities.py
  .venv/Scripts/python.exe -c "import os;os.remove('data/knowledge/plot_graph_wu_ming_zhe.json')"
  .venv/Scripts/python.exe scripts/build_plot_graph.py --character wu_ming_zhe --build-graph
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from roleplay.config import get_settings  # noqa: E402
from roleplay.core.knowledge.plot_graph import _PRONOUN_CANONICAL  # noqa: E402


def _is_pronoun(name: str) -> bool:
    return (name or "").strip().lower() in _PRONOUN_CANONICAL


def main() -> int:
    ap = argparse.ArgumentParser(description="清理抽取缓存中的代词实体")
    ap.add_argument("--character", default="wu_ming_zhe")
    ap.add_argument("--dry-run", action="store_true", help="只统计不写盘")
    args = ap.parse_args()

    settings = get_settings()
    cache_dir = Path(settings.plot_cache_dir) / args.character
    bak_dir = Path(settings.plot_cache_dir).parent / "plot_cache_pronoun_bak" / args.character
    if not cache_dir.is_dir():
        print(f"[error] 缓存目录不存在：{cache_dir}")
        return 1

    files = sorted(cache_dir.glob("*.json"))
    n_file = n_ent = n_rel = 0
    touched: list[str] = []
    for p in files:
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(data, dict):
            continue
        ents = data.get("entities") or []
        rels = data.get("relations") or []
        kept_e = [e for e in ents if isinstance(e, dict) and not _is_pronoun(str(e.get("name") or ""))]
        kept_r = [
            r for r in rels
            if isinstance(r, dict)
            and not _is_pronoun(str(r.get("src") or ""))
            and not _is_pronoun(str(r.get("dst") or ""))
        ]
        de, dr = len(ents) - len(kept_e), len(rels) - len(kept_r)
        if not de and not dr:
            continue
        n_file += 1
        n_ent += de
        n_rel += dr
        touched.append(p.stem)
        if args.dry_run:
            continue
        bak_dir.mkdir(parents=True, exist_ok=True)
        (bak_dir / p.name).write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
        p.write_text(
            json.dumps({"entities": kept_e, "relations": kept_r}, ensure_ascii=False),
            encoding="utf-8",
        )

    print(f"[pronoun] 扫描缓存 {len(files)} 条")
    print(f"[pronoun] 命中 {n_file} 条 → 删除实体 {n_ent} 个、关系 {n_rel} 条")
    if not args.dry_run:
        print(f"[pronoun] 原文备份 → {bak_dir}")
        (bak_dir / "_touched.json").write_text(
            json.dumps(touched, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    else:
        print("[pronoun] dry-run：未写盘")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
