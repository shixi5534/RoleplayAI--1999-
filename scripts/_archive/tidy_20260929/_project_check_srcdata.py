# -*- coding: utf-8 -*-
"""确认 src/data 是否只是「cwd 相对默认路径」造成的重复残留。"""
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAIRS = [
    ("src/data/characters/wu_ming_zhe.json", "data/characters/wu_ming_zhe.json"),
    ("src/data/knowledge/persona.json", "data/knowledge/persona.json"),
]


def sha(p: str) -> str:
    f = ROOT / p
    return hashlib.sha256(f.read_bytes()).hexdigest()[:12] if f.exists() else "MISSING"


print("=" * 76)
print("src/data 与 data/ 同名文件比对")
print("=" * 76)
same = True
for a, b in PAIRS:
    ha, hb = sha(a), sha(b)
    eq = ha == hb and ha != "MISSING"
    same &= eq
    print(f"  {a}")
    print(f"     src  = {ha}")
    print(f"     root = {hb}")
    print(f"     -> {'完全相同（重复残留）' if eq else '不同或缺失（需保留）'}")
print()
print("判定:", "src/data 是重复残留，可删" if same else "存在差异，需人工确认")
