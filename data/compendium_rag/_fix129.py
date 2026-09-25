# -*- coding: utf-8 -*-
"""修正 _gen_batch129.py：补 4 块缺失端点，并修 1 字关系词。"""
import re
from pathlib import Path

p = Path(__file__).resolve().parent / "_gen_batch129.py"
s = p.read_text(encoding="utf-8")

# 1) 自环
pat = re.compile(r'^\s*R\("([^"]+)",\s*"[^"]+",\s*"\1",[^\n]*\n', re.M)
s, sl = pat.subn("", s)

# 2) 1 字关系「属」→「乃是」
s = s.replace('R("恩伊·哈努遗迹", "属", "希腊古城"', 'R("恩伊·哈努遗迹", "乃是", "希腊古城"')

FIXES = {
    "e14ff015e9b11f84b0755aab": ('        E("止血剂", "物品", "所乏之药"),',
                                 '        E("止血剂", "物品", "所乏之药"),\n'
                                 '        E("牧羊女", "角色", "先前的伤者"),'),
    "21466965143f7c4a9cda6684": ('        E("芝诺", "组织", "雇佣军"),',
                                 '        E("芝诺", "组织", "雇佣军"),\n'
                                 '        E("希腊古城", "地点", "恩伊·哈努之属"),\n'
                                 '        E("神秘学文献", "物品", "流入山间者"),\n'
                                 '        E("山间", "地点", "文献流入之处"),'),
    "8053963481b96f7fb51f536e": ('        E("郁金香", "物品", "棺上之花"),',
                                 '        E("郁金香", "物品", "棺上之花"),\n'
                                 '        E("士兵", "角色", "哈桑所带出者"),'),
    "de64a874d615a47ea7361bdf": ('        E("脓疮", "概念", "伤口之状"),',
                                 '        E("脓疮", "概念", "伤口之状"),\n'
                                 '        E("尸体", "概念", "所覆眼者"),'),
}
for key, (old, new) in FIXES.items():
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
print(f"self-loops removed: {sl}")
