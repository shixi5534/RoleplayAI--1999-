# -*- coding: utf-8 -*-
"""一次性修补 _gen_batch121.py：删除自环关系、补齐缺失实体。"""
import re
from pathlib import Path

p = Path(__file__).resolve().parent / "_gen_batch121.py"
s = p.read_text(encoding="utf-8")

# 1) 删除 name -rel-> 同一 name 的自环行
pat = re.compile(r'^\s*R\("([^"]+)",\s*"[^"]+",\s*"\1",[^\n]*\n', re.M)
s, n = pat.subn("", s)

# 2) 补齐缺失实体
fixes = [
    ('        E("鼻涕泡布克", "角色", "小船员", ["“鼻涕泡”布克"]),',
     '        E("鼻涕泡布克", "角色", "小船员", ["“鼻涕泡”布克"]),\n'
     '        E("一群小船员", "角色", "聚拢的孩子们"),'),
    ('        E("信纸", "物品", "最后之信"),',
     '        E("信纸", "物品", "最后之信"),\n'
     '        E("哈拉尔", "角色", "收信的外祖父"),'),
    ('        E("星之眼", "角色", "外驻蓝星的外星调查员"),',
     '        E("星之眼", "角色", "外驻蓝星的外星调查员"),\n'
     '        E("独角兽肚脐酿蜜黄油特饮", "物品", "苏芙比所欲制"),'),
    ('        E("披萨星球", "地点", "相似度 91% 的星球"),',
     '        E("披萨星球", "地点", "相似度 91% 的星球"),\n'
     '        E("人类", "概念", "被奉为神明者"),'),
]
added = 0
for old, new in fixes:
    if old in s and new.split("\n")[1] not in s:
        s = s.replace(old, new, 1)
        added += 1

p.write_text(s, encoding="utf-8")
print(f"removed self-loops: {n} | entities added: {added}")
