# -*- coding: utf-8 -*-
"""识别批次生成器（零网关/零模型/只读产物）。

输入 `entity_candidates_<set>.json`，输出 `er2/batchNN.txt`：每行
    QID<TAB>query<TAB>候选名1、候选名2、...
即「只见 q + 扁平候选名表」（计划书 §8 反循环红线 R2）——不含 seeds、边、
度数、gold、检索结果。供主 agent 逐题识别（铁律 #1 裁决形态）使用。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PER_BATCH = 30


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", required=True, help="native | 300_cn | i")
    ap.add_argument("--outdir", default="data/compendium_rag/er2")
    ap.add_argument("--per", type=int, default=PER_BATCH)
    ap.add_argument("--max-names", type=int, default=0, help="0=不截断（保覆盖）")
    args = ap.parse_args()

    src = ROOT / "data/compendium_rag" / f"entity_candidates_{args.set}.json"
    data = json.loads(src.read_text(encoding="utf-8"))
    entries = sorted(data.items(), key=lambda kv: kv[0])
    lines = []
    for qid, v in entries:
        names = v.get("candidates") or []
        if args.max_names:
            names = names[: args.max_names]
        lines.append(f"{qid}\t{v.get('query','')}\t" + "、".join(names))

    outdir = ROOT / args.outdir / args.set
    outdir.mkdir(parents=True, exist_ok=True)
    for old in outdir.glob("batch*.txt"):
        old.unlink()
    n = 0
    for i in range(0, len(lines), args.per):
        n += 1
        (outdir / f"batch{n:02d}.txt").write_text(
            "\n".join(lines[i:i + args.per]) + "\n", encoding="utf-8")
    print(f"set={args.set} lines={len(lines)} batches={n} per={args.per} -> {outdir}")
    print(f"total_chars={sum(len(l) for l in lines)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
