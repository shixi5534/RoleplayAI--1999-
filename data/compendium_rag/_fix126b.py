# -*- coding: utf-8 -*-
"""修正 _gen_batch126.py：
1) 关系端点 `布莱恩` → `布莱恩·芬努`（端点须用实体本名，别名不能当端点）；
2) 补齐缺失实体：X／道路／道德／施术波动／吸血鬼。
"""
import re
from pathlib import Path

p = Path(__file__).resolve().parent / "_gen_batch126.py"
s = p.read_text(encoding="utf-8")

# 1) 端点改名（仅出现在 R(...) 的参数里；实体声明行的 name 不动）
s = s.replace('R("布莱恩",', 'R("布莱恩·芬努",')
s = s.replace(', "布莱恩",', ', "布莱恩·芬努",')

# 2) 补实体
fixes = {
    "07a343a60f6639217897c45d": ('        E("蝴蝶", "概念", "已扇动的翅膀"),',
                                 '        E("蝴蝶", "概念", "已扇动的翅膀"),\n'
                                 '        E("X", "角色", "诵文者"),'),
    "61d259498cdd0e4683e8e30a": ('        E("废弃高楼", "地点", "波动所出"),',
                                 '        E("废弃高楼", "地点", "波动所出"),\n'
                                 '        E("道路", "概念", "所祝福者"),\n'
                                 '        E("道德", "概念", "被质问者"),\n'
                                 '        E("施术波动", "概念", "高楼传出之物"),'),
    "b30cb987c176d4d5d7a00fa3": ('        E("手摇发电机", "概念", "戏谑之喻"),',
                                 '        E("手摇发电机", "概念", "戏谑之喻"),\n'
                                 '        E("吸血鬼", "概念", "传说之物"),'),
    "49db1c29d49b31a977e6d6d3": ('        E("军火供应商", "组织", "邀其来者"),',
                                 '        E("军火供应商", "组织", "邀其来者"),\n'
                                 '        E("吸血鬼", "概念", "所论之族"),'),
    "35548adb0a443b4f3dd6b3cb": ('        E("上帝", "概念", "所归因者"),',
                                 '        E("上帝", "概念", "所归因者"),'),
    "c4524f7e372e1fe3c38861b7": ('        E("宅邸", "地点", "拍摄之地"),',
                                 '        E("宅邸", "地点", "拍摄之地"),\n'
                                 '        E("吸血鬼", "概念", "所欲拍摄者"),'),
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
print("patched")
