# -*- coding: utf-8 -*-
"""证据逐字核对(可复用):python _verify_evidence.py <batch.json> <dump.txt>

红线 3 第 2 类翻车(凭语义虚构写法)的机器化拦截:
每条 relation 的 evidence 去掉中文引号后,必须是该块原文的**连续子串**。
"""
import json
import sys
from pathlib import Path

QUOTES = str.maketrans("", "", "\u201c\u201d\u2018\u2019\"\u300c\u300d")


def main(batch: str, dumpf: str) -> int:
    base = Path(__file__).resolve().parent
    p = Path(batch)
    d = Path(dumpf)
    if not p.is_absolute():
        p = base / p
    if not d.is_absolute():
        d = base / d
    dump = {json.loads(l)["key"]: json.loads(l)["text"]
            for l in d.read_text(encoding="utf-8-sig").splitlines() if l.strip()}
    data = json.loads(p.read_text(encoding="utf-8"))
    miss = 0
    for k, blk in data.items():
        if k not in dump:
            print(f"✗ {k}: 不在 dump 中")
            miss += 1
            continue
        src = dump[k].translate(QUOTES)
        for r in blk["relations"]:
            ev = r["evidence"].translate(QUOTES)
            if ev not in src:
                miss += 1
                print(f"✗ {k} {r['src']}-{r['relation']}->{r['dst']}: {r['evidence']}")
    total = sum(len(b["relations"]) for b in data.values())
    print(f"\n核对 {total} 条证据，未命中 {miss} 条")
    return 1 if miss else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1], sys.argv[2]))
