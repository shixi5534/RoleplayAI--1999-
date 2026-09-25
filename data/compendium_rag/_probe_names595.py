# -*- coding: utf-8 -*-
"""号位 595 自用:列出 35101 前序批次(266-269)已建的实体名/类型/desc/alias。"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
want = sys.argv[1] if len(sys.argv) > 1 else ""
for n in (266, 267, 268, 269):
    b = json.load(open(ROOT / f"_agent_batch{n}.json", encoding="utf-8"))
    for key, blk in b.items():
        for e in blk.get("entities", []):
            nm = e["name"]
            if want and not re.search(want, nm):
                continue
            print(f"{n} | {nm} | {e.get('type')} | {e.get('desc')} | {e.get('aliases')}")
