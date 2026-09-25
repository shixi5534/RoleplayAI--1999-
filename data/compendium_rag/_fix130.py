# -*- coding: utf-8 -*-
"""修正 _gen_batch130.py：删自环 + 补 6 块缺失端点。"""
import re
from pathlib import Path

p = Path(__file__).resolve().parent / "_gen_batch130.py"
s = p.read_text(encoding="utf-8")

pat = re.compile(r'^\s*R\("([^"]+)",\s*"[^"]+",\s*"\1",[^\n]*\n', re.M)
s, sl = pat.subn("", s)

FIXES = {
    "02cf929423dc73571bee1550": ('        E("乌哈拉", "地点", "不合时宜之地"),',
                                 '        E("乌哈拉", "地点", "不合时宜之地"),\n'
                                 '        E("战争", "概念", "所评议者"),'),
    "c8deffdc75dd5e4cad8db5f9": ('        E("黑色金属棺材", "物品", "郁金香所饰"),',
                                 '        E("黑色金属棺材", "物品", "郁金香所饰"),\n'
                                 '        E("芝诺", "组织", "哈桑所归"),'),
    "27d9b5fe46fbfa61ae196190": ('        E("童子军手册", "物品", "安全篇所出"),',
                                 '        E("童子军手册", "物品", "安全篇所出"),\n'
                                 '        E("泽维尔", "角色", "所寻的失踪者"),'),
    "447cb3e17e1e15a5525658f4": ('        E("环境异常", "概念", "所察觉者"),',
                                 '        E("环境异常", "概念", "所察觉者"),\n'
                                 '        E("童子军", "组织", "所欲加入者"),'),
    "0f8a001df2e4edc8b44fa8e6": ('        E("科尼岛", "地点", "旋转木马之喻"),',
                                 '        E("科尼岛", "地点", "旋转木马之喻"),\n'
                                 '        E("父母", "角色", "泽维尔之亲"),'),
    "fa40550584c4c7b0cc3c605d": ('        E("童子军", "组织", "所求不得入"),',
                                 '        E("童子军", "组织", "所求不得入"),\n'
                                 '        E("童子军手册", "物品", "素养所载"),'),
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
