# -*- coding: utf-8 -*-
"""为 46 组「alias 同时是另一个 name 且类型不同」的焊点收集裁决证据。

零网络、只读，扫描 **修复前备份 cache**（collapse 会改名，故必须在原始态上判断）。
每组打印：
  ① 声明侧块（宿主 entity 条目原文）
  ② A / H 各自「成名为 name」的块 + type 分布 + desc
  ③ A / H 各自参与的关系（含 evidence），用于按**文本关系**判定同指/异指
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path("src").resolve()))
from compendium_rag import pipeline as P                                   # noqa: E402
from compendium_rag.config import get_settings                             # noqa: E402
from compendium_rag.extract import (PROMPT_VERSION, ExtractionCache,       # noqa: E402
                                    cache_key, normalize)

BAK = Path("C:/Users/Lenovo/AppData/Local/Temp/cache_backup_pre_welds")


def main() -> int:
    pairs = [tuple(x.split(",")) for x in
             Path(sys.argv[1]).read_text(encoding="utf-8").splitlines() if x.strip()]
    s = get_settings()
    cache = ExtractionCache(BAK)
    blocks = {}                              # key -> (chunk, Extraction)
    for c in P.load_chunks(s):
        key = cache_key(c, s.llm_model, PROMPT_VERSION)
        raw = cache.get_raw(key)
        if raw is None:
            continue
        ex = normalize(c, raw)
        if ex is None or not getattr(ex, "ok", True):
            continue
        blocks[key] = (c, ex, raw)

    name_types = defaultdict(Counter)        # name -> Counter(type)
    name_desc = defaultdict(Counter)         # name -> Counter(desc)
    name_rel = defaultdict(list)             # name -> [(关系串, chunk尾)]
    decl = defaultdict(list)                 # alias -> [(holder, chunk尾, raw条目)]
    for key, (c, ex, raw) in blocks.items():
        tail = c.chunk_id[-30:]
        for e in ex.entities:
            if not e.name:
                continue
            name_types[e.name][e.type] += 1
            if e.desc:
                name_desc[e.name][e.desc] += 1
            for a in e.aliases:
                if a and a != e.name:
                    decl[a].append((e.name, tail,
                                    {"type": e.type, "desc": e.desc[:60]}))
        for r in ex.relations:
            for x in (r.src, r.dst):
                y = r.dst if x == r.src else r.src
                name_rel[x].append(
                    f"{r.src} -[{r.relation}]-> {r.dst}｜{r.evidence[:56]}｜{tail}")

    out = []
    for A, H in pairs:
        out.append(f"\n{'='*70}\n【{A}】({'/'.join(name_types[A])})  ⟵ alias 声明自  【{H}】({'/'.join(name_types[H])})")
        out.append(f"  A 成名 {sum(name_types[A].values())} 次｜H 成名 {sum(name_types[H].values())} 次")
        out.append(f"  A 作为 alias 被声明 {len(decl[A])} 次，宿主 {sorted({h for h, _, _ in decl[A]})}")
        for h, t, ent in decl[A][:4]:
            out.append(f"    声明块 …{t}: name={h} aliases=[…{A}…] {ent}")
        if name_desc[A]:
            out.append("  A desc: " + " ‖ ".join(d[:48] for d, _ in name_desc[A].most_common(3)))
        if name_desc[H]:
            out.append("  H desc: " + " ‖ ".join(d[:48] for d, _ in name_desc[H].most_common(3)))
        out.append("  A 关系:")
        for line in name_rel[A][:6]:
            out.append(f"    {line}")
        out.append("  H 关系:")
        for line in name_rel[H][:6]:
            out.append(f"    {line}")
    Path(sys.argv[2]).write_text("\n".join(out), encoding="utf-8")
    print(f"写入 {sys.argv[2]}（{len(pairs)} 组）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
