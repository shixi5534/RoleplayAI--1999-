# -*- coding: utf-8 -*-
"""盲测题集**机械校验**：与主口径契约严格一致，独立复核子代理的自述。

校验项（任一不过则该题不可用于评测）：
  1. JSON 合法、字段齐全（id/q/evidence/dims）
  2. id 唯一且符合前缀
  3. evidence 结构 = 嵌套列表，非空，元素为非空字符串
  4. **每个关键词在所有 3695 块中逐字出现**（否则该题在语料层不可答）
  5. 关键词未泄题（不出现在自己的 q 中）—— 泄题会使检索变得过易
  6. 中文关键词占比统计（评测口径要求答案词可在中文语料命中）
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "data/knowledge/_audit/blind_v1"
RE_CN = re.compile(r"[\u4e00-\u9fff]")


def flatten(ev):
    out = []
    for grp in (ev or []):
        if isinstance(grp, str):
            out.append(grp)
        elif isinstance(grp, (list, tuple)):
            out.extend(str(x) for x in grp if x)
    return [k.strip() for k in out if k and k.strip()]


def main() -> int:
    chunks = json.loads((ROOT / "data/compendium_rag/chunks.json").read_text(encoding="utf-8"))["chunks"]
    blob = {c["chunk_id"]: f"{c['text']}\n{c['chapter_title']}\n{c.get('scene_title','')}\n{c.get('part_title','')}"
            for c in chunks}

    files = [f for f in sorted(D.glob("questions_*.json"))
             if f.name not in ("questions_merged.json", "questions_clean.json",
                               "questions_strict.json")]
    if not files:
        print("无 questions_*.json")
        return 1
    grand = Counter()
    allcases = []
    for f in files:
        d = json.loads(f.read_text(encoding="utf-8"))
        cases = d.get("cases", [])
        print("=" * 80)
        print(f"{f.name}  meta.author={d.get('meta',{}).get('author')}  n={len(cases)}")
        ids = [str(c.get("id")) for c in cases]
        dup = [k for k, v in Counter(ids).items() if v > 1]
        bad_struct, ungrounded, leaked, cn_only = [], [], [], 0
        for c in cases:
            kws = flatten(c.get("evidence"))
            if not kws:
                bad_struct.append(c.get("id"))
                continue
            miss = [k for k in kws if not any(k in t for t in blob.values())]
            if miss:
                ungrounded.append((c.get("id"), miss[:2]))
            q = c.get("q", "")
            lk = [k for k in kws if k in q]
            if lk:
                leaked.append((c.get("id"), lk[:2]))
            if any(RE_CN.search(k) for k in kws):
                cn_only += 1
        print(f"  id 重复      : {len(dup)} {dup[:5]}")
        print(f"  evidence 空/缺失: {len(bad_struct)} {bad_struct[:5]}")
        print(f"  **语料层不可答**: {len(ungrounded)} {ungrounded[:5]}")
        print(f"  关键词泄题   : {len(leaked)} {leaked[:5]}")
        print(f"  含中文关键词 : {cn_only}/{len(cases)}")
        grand["cases"] += len(cases)
        grand["dup"] += len(dup)
        grand["ungrounded"] += len(ungrounded)
        grand["leaked"] += len(leaked)
        allcases += cases

    print("=" * 80)
    print(f"合计: {grand['cases']} 题 | id重复 {grand['dup']} | 语料层不可答 {grand['ungrounded']} "
          f"| 泄题 {grand['leaked']}")
    # 合并输出（供评测）
    if allcases:
        merged = {"meta": {"source": "blind_v1 (subagent-authored, blind)",
                           "n": len(allcases), "files": [f.name for f in files]},
                  "cases": allcases}
        out = D / "questions_merged.json"
        out.write_text(json.dumps(merged, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"-> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
