# -*- coding: utf-8 -*-
"""补齐 _gen_batch122.py 缺失端点。"""
from pathlib import Path

p = Path(__file__).resolve().parent / "_gen_batch122.py"
s = p.read_text(encoding="utf-8")

BLOCKS = {
    "830af26eda2198cb341f96e1": ('        E("狼", "概念", "屏幕中的野兽"),',
                                 '        E("狼", "概念", "屏幕中的野兽"),\n'
                                 '        E("维尔汀", "角色", "被循味者"),'),
    "bd1cb283ea62347070410012": ('        E("芭妮芭妮", "角色", "自责者"),',
                                 '        E("警察", "角色", "呈递文书者"),\n'
                                 '        E("芭妮芭妮", "角色", "自责者"),'),
}
for key, (old, new) in BLOCKS.items():
    i = s.index(f'BATCH["{key}"]')
    j = s.index("\n}\n", i)
    seg = s[i:j]
    if new.split("\n")[1].strip() not in seg:
        s = s[:i] + seg.replace(old, new, 1) + s[j:]

p.write_text(s, encoding="utf-8")
print("patched")
