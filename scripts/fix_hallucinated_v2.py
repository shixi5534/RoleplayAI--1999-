# -*- coding: utf-8 -*-
"""按「全局别名池跨块传播」修复 hallucinated_entity。

背景：语料扩充到 9021 块后，新增的 1.x/2.x 块由本地 7B 抽取，审计报出
2770 块 hallucinated_entity（3914 个实例，去重 425 个名字）。抽查发现分两类：

A 类 **真幻觉**：正文段落里根本没提这个角色，纯靠模型对高频角色的先验硬塞。
   例：v1.1 正文 "Finally, I'm back... Miss A.C." 里抽出实体 Spathodea。
   → 删除实体及其关系。

B 类 **跨语种/译名不匹配**：角色确实在场，但正文用的是另一种语言的称谓。
   例：v2.6 西语正文 "el Tempo Keeper"/"el investigador de paracausalidad"
   指的就是司辰（维尔汀），而实体写的是中文「维尔汀」+ 别名 Vertín。
   → 补上正文里的表层形式作为别名即可保留。

判别方法：把**同一角色在所有块里出现过的别名**聚合成全局池，再用这个池去
当前块正文里匹配。命中即 B 类（补别名），未命中即 A 类（删实体+关系）。

用法（项目根目录）：
  python scripts/fix_hallucinated_v2.py            # 预演
  python scripts/fix_hallucinated_v2.py --apply    # 写盘
  python scripts/fix_hallucinated_v2.py --apply --min-pool 2   # 只用出现≥2次的别名
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "knowledge" / "plot_cache" / "wu_ming_zhe"
CORPUS = ROOT / "data" / "knowledge" / "plot_corpus_wu_ming_zhe.json"
ALIAS_TABLE = ROOT / "data" / "lore" / "wu_ming_zhe" / "plot_aliases.json"


def norm(s: str) -> str:
    return (s or "").strip().lower().replace(" ", "")


def in_text(name: str, text_norm: str) -> bool:
    n = norm(name)
    return bool(n) and len(n) >= 2 and n in text_norm


def build_pool(min_pool: int) -> dict[str, set[str]]:
    """角色名 -> 该角色在全部缓存中出现过的所有表层形式（含别名表）。"""
    pool: dict[str, set[str]] = defaultdict(set)
    freq: Counter = Counter()

    for p in CACHE.glob("*.json"):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        for e in d.get("entities") or []:
            nm = str(e.get("name") or "").strip()
            if not nm:
                continue
            for a in (e.get("aliases") or []):
                a = str(a or "").strip()
                if a and len(a) >= 2:
                    freq[(nm, a)] += 1

    for (nm, a), n in freq.items():
        if n >= min_pool:
            pool[nm].add(a)

    # 人工别名表（权威，直接并入）
    if ALIAS_TABLE.exists():
        table = json.loads(ALIAS_TABLE.read_text(encoding="utf-8"))
        for canon, aliases in table.items():
            for a in aliases if isinstance(aliases, list) else [aliases]:
                a = str(a or "").strip()
                if a and len(a) >= 2:
                    pool[str(canon)].add(a)
    return pool


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="写盘（默认预演）")
    ap.add_argument("--min-pool", type=int, default=1, help="别名至少在 N 个块出现过才采信")
    args = ap.parse_args()

    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    chunks = corpus["chunks"] if isinstance(corpus, dict) else corpus
    txt = {c["hash"]: c.get("text", "") for c in chunks}

    pool = build_pool(args.min_pool)
    print(f"[pool] 采信别名 {sum(len(v) for v in pool.values())} 条，覆盖 {len(pool)} 个角色名")

    issues = [
        json.loads(l)
        for l in (ROOT / "data" / "knowledge" / "_audit" / "full_issues.jsonl")
        .read_text(encoding="utf-8").splitlines()
        if l.strip()
    ]
    targets = [r["hash"] for r in issues if "hallucinated_entity" in r.get("flags", [])]

    n_rescue = n_drop_e = n_drop_r = n_still = 0
    rescued_names: Counter = Counter()
    dropped_names: Counter = Counter()

    for h in targets:
        p = CACHE / f"{h}.json"
        if not p.exists():
            continue
        text_norm = norm(txt.get(h, ""))
        data = json.loads(p.read_text(encoding="utf-8"))
        ents = data.get("entities") or []

        keep, drop = [], set()
        changed = False
        for e in ents:
            nm = str(e.get("name") or "").strip()
            aliases = [str(a) for a in (e.get("aliases") or []) if str(a or "").strip()]
            if in_text(nm, text_norm) or any(in_text(a, text_norm) for a in aliases):
                keep.append(e)
                continue
            # 用全局别名池再试一次
            hit = [a for a in pool.get(nm, ()) if in_text(a, text_norm)]
            if hit:
                merged = list(dict.fromkeys(aliases + hit[:3]))
                e["aliases"] = merged
                keep.append(e)
                changed = True
                n_rescue += 1
                rescued_names[nm] += 1
            else:
                drop.add(nm)
                n_drop_e += 1
                dropped_names[nm] += 1

        if drop:
            data["entities"] = keep
            rels = data.get("relations") or []
            kept = [
                r for r in rels
                if str(r.get("src") or "") not in drop and str(r.get("dst") or "") not in drop
            ]
            n_drop_r += len(rels) - len(kept)
            data["relations"] = kept
            changed = True
            if not data["entities"] and not data["relations"]:
                n_still += 1

        # 写盘条件必须是 changed 而非 drop：只补别名（没删任何实体）的块也要落盘，
        # 否则补的别名全部丢失（曾导致「救回 738 个但审计毫无变化」）。
        if args.apply and changed:
            p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n[rescue] 补别名救回 {n_rescue} 个实体（top15）")
    for n, c in rescued_names.most_common(15):
        print(f"   {c:5d}  {n}")
    print(f"\n[drop] 删除 {n_drop_e} 个实体 + {n_drop_r} 条关系（top15）")
    for n, c in dropped_names.most_common(15):
        print(f"   {c:5d}  {n}")
    print(f"\n[h-v2] {'已写盘' if args.apply else '预演'}；转空块 {n_still}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
