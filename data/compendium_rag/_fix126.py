# -*- coding: utf-8 -*-
"""清理 _gen_batch126.py：删自环、补端点。"""
import re
from pathlib import Path

p = Path(__file__).resolve().parent / "_gen_batch126.py"
s = p.read_text(encoding="utf-8")

pat = re.compile(r'^\s*R\("([^"]+)",\s*"[^"]+",\s*"\1",[^\n]*\n', re.M)
s, n = pat.subn("", s)

fixes = {
    "07a343a60f6639217897c45d": ('        E("威尔森医药公司", "地点", "被围之处"),',
                                 '        E("威尔森医药公司", "地点", "被围之处"),\n'
                                 '        E("道路", "概念", "所祝福者"),\n'
                                 '        E("拉普拉斯科算中心", "组织", "被诘问者"),'),
    "649bf09d6e6f7cd18d2a711a": ('        E("军官俱乐部", "地点", "40年代相聚处"),',
                                 '        E("军官俱乐部", "地点", "40年代相聚处"),\n'
                                 '        E("军队", "组织", "所应征者"),'),
    "496d59e4cc6ee8b21e5c79e5": ('        E("神秘生物学", "概念", "所引之学"),',
                                 '        E("神秘生物学", "概念", "所引之学"),\n'
                                 '        E("布莱恩", "角色", "受片者"),'),
}
for key, (old, new) in fixes.items():
    i = s.index(f'BATCH["{key}"]')
    j = s.index("\n}\n", i)
    seg = s[i:j]
    ent_start = seg.index('"entities"')
    rel_start = seg.index('"relations"')
    ent_seg = seg[ent_start:rel_start]
    add = [ln for ln in new.split("\n")[1:] if ln.strip() and ln.strip() not in ent_seg]
    if add:
        s = s[:i] + seg.replace(old, old + "\n" + "\n".join(add), 1) + s[j:]

p.write_text(s, encoding="utf-8")
print(f"self-loops removed: {n}")
