# -*- coding: utf-8 -*-
"""补 _gen_batch134.py 缺失端点（4.2.1 需 火光灼灼／瞬时石化咒）。"""
from pathlib import Path

p = Path(__file__).resolve().parent / "_gen_batch134.py"
s = p.read_text(encoding="utf-8")

key = "7cea05dc99c34efef92803e3"
old = '        E("生日", "事件", "所忆之期"),'
new = (old + "\n"
       '        E("火光灼灼", "概念", "所施之术"),\n'
       '        E("瞬时石化咒", "概念", "所施之术"),')

i = s.index(f'BATCH["{key}"]')
j = s.index("\n}\n", i)
seg = s[i:j]
ent_start = seg.index('"entities"')
rel_start = seg.index('"relations"')
ent_seg = seg[ent_start:rel_start]
add = [ln for ln in new.split("\n")[1:] if ln.strip() not in ent_seg]
if add:
    s = s[:i] + seg.replace(old, old + "\n" + "\n".join(add), 1) + s[j:]

p.write_text(s, encoding="utf-8")
print("patched")
