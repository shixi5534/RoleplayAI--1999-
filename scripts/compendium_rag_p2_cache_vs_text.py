# -*- coding: utf-8 -*-
"""v9-P2 归因三（**只读**）：抽取缓存的 raw 名字与它自己的块正文对不对得上。

触发点：诊断二 find 到 386 条「缓存里有、图上没有、双端可解析、置信度 0.85+」的关系。
逐条追到最原始记录（块正文）后发现，图是对的、缓存是错的：
``mainline__110_复乐园:19.0.1`` 正文里 兀尔德×2、德洛丝×9、卡卡尼亚×**0**，
而缓存 raw 把这段关系写成 ``维尔汀|寻访|卡卡尼亚``。

这件事的份量比 386 条边大得多：``rebuild_from_cache`` 的前提是
「缓存 = 模型对该块的原始输出」，而缓存里至少有一类条目被后续补名/焊接式改写污染过，
污染方向还与正文相反。所以**动任何「从缓存重建」的念头之前，必须先量清污染面**。

本脚本按块做最朴素的对照：raw 里的每个实体名 / 关系端点，在**它自己那块正文**里
逐字出现吗？分四类计数：
  own_chunk   —— 出现在自己块里（正常）
  elsewhere   —— 自己块里没有、但全语料有 → **错位归名**（把 A 块的人写进 B 块）
  nowhere     —— 全语料都没有 → 幻觉名
  alias_own   —— 本名不在、但它的某个别名在自己块里（可接受，写法差异）

用法：PYTHONPATH=src .venv/Scripts/python.exe -X utf8 scripts/compendium_rag_p2_cache_vs_text.py
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from compendium_rag import pipeline as P  # noqa: E402
from compendium_rag.config import get_settings  # noqa: E402
from compendium_rag.extract import cache_key  # noqa: E402

CACHE_DIR = ROOT / "data/compendium_rag/cache"
OUT = ROOT / "data/compendium_rag/reports/p2_cache_vs_text.json"
PROMPT_VERSION = "v3"


def _now() -> str:
    return time.strftime("%H:%M:%S")


def main() -> int:
    s = get_settings()
    chapters = P.load_chapters(s)
    chunks = P.chunk_corpus(chapters, s)
    by_key = {cache_key(c, s.llm_model, PROMPT_VERSION): c for c in chunks}
    corpus = "\n".join(c.text or "" for c in chunks)
    print(f"[{_now()}] 块={len(chunks)} 映射到缓存键={len(by_key)} 语料字数={len(corpus)}")

    files = sorted(CACHE_DIR.rglob("*.json"))
    ent_stat: Counter = Counter()
    rel_stat: Counter = Counter()
    bad_chunks = 0
    chunk_examples: list[dict] = []
    elsewhere_names: Counter = Counter()
    nowhere_names: Counter = Counter()
    n_no_chunk_match = 0
    rows_checked = 0

    for i, p in enumerate(files, 1):
        try:
            raw = json.loads(p.read_text(encoding="utf-8")).get("raw") or {}
        except Exception:
            continue
        ch = by_key.get(p.stem)
        if ch is None:
            n_no_chunk_match += 1
            continue
        text = ch.text or ""
        ents = raw.get("entities") or []
        local_alias: dict[str, list[str]] = {}
        for e in ents:
            nm = str(e.get("name") or "")
            local_alias.setdefault(nm, []).extend(
                str(a) for a in (e.get("aliases") or []) if a)
        violations = []
        for e in ents:
            nm = str(e.get("name") or "")
            if not nm:
                continue
            rows_checked += 1
            if nm in text:
                ent_stat["own_chunk"] += 1
                continue
            if any(a in text for a in local_alias.get(nm, ())):
                ent_stat["alias_own"] += 1
                continue
            if nm in corpus:
                ent_stat["elsewhere"] += 1
                elsewhere_names[nm] += 1
                violations.append(("entity_misplaced", nm))
            else:
                ent_stat["nowhere"] += 1
                nowhere_names[nm] += 1
                violations.append(("entity_hallucinated", nm))
        for r in raw.get("relations") or []:
            for side in ("src", "dst"):
                nm = str(r.get(side) or "")
                if not nm:
                    continue
                if nm in text:
                    rel_stat["own_chunk"] += 1
                elif nm in corpus:
                    rel_stat["elsewhere"] += 1
                    elsewhere_names[f"{nm}(rel)"] += 1
                    violations.append(("relation_misplaced", nm))
                else:
                    rel_stat["nowhere"] += 1
                    nowhere_names[f"{nm}(rel)"] += 1
                    violations.append(("relation_hallucinated", nm))
        if violations:
            bad_chunks += 1
            if len(chunk_examples) < 25:
                chunk_examples.append({
                    "chunk_id": ch.chunk_id,
                    "cache_key": p.stem,
                    "title": ch.chapter_title,
                    "violations": violations[:8],
                    "n_entities": len(ents),
                })
        if i % 600 == 0:
            print(f"[{_now()}] {i}/{len(files)} 违规块={bad_chunks}")

    n_ent_rows = sum(ent_stat.values())
    n_rel_rows = sum(rel_stat.values())
    stats = {
        "graph_sha256_16": hashlib.sha256(s.graph_path.read_bytes()).hexdigest()[:16],
        "cache_files": len(files),
        "chunks": len(chunks),
        "cache_keys_unmatched_to_chunk": n_no_chunk_match,
        "entity_rows_checked": n_ent_rows,
        "relation_endpoint_rows_checked": n_rel_rows,
        "entity_landing": dict(ent_stat.most_common()),
        "relation_endpoint_landing": dict(rel_stat.most_common()),
        "entity_bad_rate": round((ent_stat["elsewhere"] + ent_stat["nowhere"])
                                 / n_ent_rows, 6) if n_ent_rows else None,
        "relation_bad_rate": round((rel_stat["elsewhere"] + rel_stat["nowhere"])
                                   / n_rel_rows, 6) if n_rel_rows else None,
        "chunks_with_violations": bad_chunks,
        "chunks_with_violations_rate": round(bad_chunks / len(files), 6) if files else None,
        "elsewhere_top": elsewhere_names.most_common(30),
        "nowhere_top": nowhere_names.most_common(30),
    }
    rep = {
        "schema": "compendium_rag.p2_cache_vs_text/v1",
        "mode": "read-only",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "question": "缓存 raw 的名字与它自己的块正文对不对得上（决定 rebuild 是否可用）",
        "stats": stats,
        "chunk_examples": chunk_examples,
    }
    OUT.write_text(json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=False, indent=2)[:3000])
    print(f"报告 → {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
