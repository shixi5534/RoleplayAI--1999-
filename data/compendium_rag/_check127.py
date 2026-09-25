# -*- coding: utf-8 -*-
"""报告 _gen_batch127.py 生成的 batch 中所有缺失端点（便于一次性补齐）。"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
p = ROOT / "_agent_batch127.json"
if not p.exists():
    print("batch json 不存在，先生成"); sys.exit(1)
d = json.loads(p.read_text(encoding="utf-8"))
for k, v in d.items():
    names = {e["name"] for e in v["entities"]}
    miss = []
    for r in v["relations"]:
        for side in ("src", "dst"):
            if r[side] not in names:
                miss.append(f'{side}={r[side]} (rel={r["relation"]})')
    if miss:
        print(f"{k}:")
        for m in sorted(set(miss)):
            print("   ", m)
