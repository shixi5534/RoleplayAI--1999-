# -*- coding: utf-8 -*-
"""删除 _gen_batch122.py 中的自环关系行（name -rel-> 同名）。"""
import re
from pathlib import Path

p = Path(__file__).resolve().parent / "_gen_batch122.py"
s = p.read_text(encoding="utf-8")
pat = re.compile(r'^\s*R\("([^"]+)",\s*"[^"]+",\s*"\1",[^\n]*\n', re.M)
s, n = pat.subn("", s)
p.write_text(s, encoding="utf-8")
print(f"removed self-loops: {n}")
