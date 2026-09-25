# -*- coding: utf-8 -*-
"""lore 层嵌入器 A/B 对比：nomic-embed-text(768) vs bge-m3(1024)。

为什么做这个实验（2026-09-16）：
    L1（lore 换 bge-m3）要重建 6641 条向量，成本不低。而外部审查报告给出的理由
    （"lore 库全是中文，nomic 单语不适配"）**经复核不成立**——实测 92.1% 是英文。
    真正成立的理由是"**查询是中文、库是英文，需要跨语言对齐**"。
    所以在动手重建前，先用同一批查询做同池 A/B，确认 bge-m3 确实更优。

实验设计（同池、同题、只换模型）：
    池   = lore 库中"中文为主"的条目（384 条，即角色设定类）
    题   = N 个中文问句（覆盖世界观/组织/角色设定）
    对比 = top-k 命中率（命中的是"人工标注的期望条目"或其同主题条目）
    两模型各自 embed query；doc 侧 nomic 用存量向量、bge-m3 现算

用法：
    .venv/Scripts/python.exe -X utf8 scripts/ab_lore_embed.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np  # noqa: E402

from roleplay.core.knowledge.embedder import OllamaEmbedder  # noqa: E402

LORE = ROOT / "data" / "knowledge" / "lore_wu_ming_zhe.json"

# 中文问句 → 期望命中的**主题关键词**（用于判定 top-k 里是否出现相关内容）
CASES: list[tuple[str, list[str]]] = [
    ("暴雨是什么？", ["暴雨", "Storm"]),
    ("暴雨症候是什么？", ["症候"]),
    ("圣洛夫基金会是做什么的？", ["圣洛夫基金会", "基金会"]),
    ("重塑之手是什么组织？", ["重塑之手"]),
    ("司辰是什么职位？", ["司辰"]),
    ("神秘学家是什么？", ["神秘学"]),
    ("阿派朗岛在哪里？", ["阿派朗"]),
    ("维尔汀是谁？", ["维尔汀", "Vertin"]),
    ("十四行诗是谁？", ["十四行诗", "Sonetto"]),
    ("芝诺军备学院是什么？", ["芝诺"]),
]


def cjk_ratio(t: str) -> float:
    if not t:
        return 0.0
    return len(re.findall(r"[\u4e00-\u9fff]", t)) / len(t)


def main() -> int:
    lore = json.loads(LORE.read_text(encoding="utf-8"))
    pool = [e for e in lore if cjk_ratio(e.get("text") or "") >= 0.2]
    print(f"[pool] lore 总数 {len(lore)}｜中文为主（CJK≥20%）{len(pool)} 条")

    texts = [str(e.get("text") or "") for e in pool]
    nomic_vecs = np.asarray([e["vec"] for e in pool], dtype=np.float32)
    nomic_vecs /= (np.linalg.norm(nomic_vecs, axis=1, keepdims=True) + 1e-9)
    print(f"[nomic] 存量向量 {nomic_vecs.shape}")

    bge = OllamaEmbedder(model="bge-m3", base_url="http://localhost:11434", timeout=120.0)
    print(f"[bge-m3] 维度 {bge.dim}｜正在嵌入 {len(texts)} 条文档 …")
    bge_docs = np.asarray(bge.embed(texts), dtype=np.float32)
    bge_docs /= (np.linalg.norm(bge_docs, axis=1, keepdims=True) + 1e-9)

    rows = []
    for q, keys in CASES:
        rec: dict = {"q": q, "keys": keys}
        for tag, emb, docs in (("nomic", None, nomic_vecs), ("bge", bge, bge_docs)):
            mod = emb or OllamaEmbedder(model="nomic-embed-text",
                                        base_url="http://localhost:11434", timeout=120.0)
            qv = np.asarray(mod.embed_query(q), dtype=np.float32)
            qv /= (np.linalg.norm(qv) + 1e-9)
            sims = docs @ qv
            order = np.argsort(-sims)[:5]
            tops = [texts[i][:40].replace("\n", " ") for i in order]
            hit = any(any(k in tops[j] for k in keys) for j in range(5))
            rec[tag] = {"top1": tops[0], "hit@5": hit}
        rows.append(rec)

    print()
    print("=" * 78)
    print(f"{'查询':<22}{'nomic hit@5':<14}{'bge-m3 hit@5':<14}")
    print("-" * 78)
    n_hit = b_hit = 0
    for r in rows:
        n, b = r["nomic"]["hit@5"], r["bge"]["hit@5"]
        n_hit += n
        b_hit += b
        print(f"{r['q'][:20]:<22}{('✅' if n else '❌'):<14}{('✅' if b else '❌'):<14}")
    print("-" * 78)
    print(f"命中率: nomic {n_hit}/{len(rows)} ({n_hit/len(rows):.0%})"
          f"｜bge-m3 {b_hit}/{len(rows)} ({b_hit/len(rows):.0%})")
    print()
    print("各题 top1 对照：")
    for r in rows:
        print(f"  {r['q']}")
        print(f"     nomic : {r['nomic']['top1'][:56]}")
        print(f"     bge-m3: {r['bge']['top1'][:56]}")

    out = ROOT / "data" / "knowledge" / "_audit" / "ab_lore_embed.json"
    out.write_text(json.dumps({"pool": len(pool), "cases": rows,
                               "nomic_hit": n_hit, "bge_hit": b_hit},
                              ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n[save] {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
