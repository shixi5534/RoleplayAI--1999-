# -*- coding: utf-8 -*-
"""续修 _gen_batch123.py：补齐剩余缺失端点。"""
from pathlib import Path

p = Path(__file__).resolve().parent / "_gen_batch123.py"
s = p.read_text(encoding="utf-8")

fixes = {
    "59539fae529848983d1d730b": ('        E("莫桑小姐", "角色", "读爱情小说者"),',
                                 '        E("莫桑小姐", "角色", "读爱情小说者"),\n'
                                 '        E("警察", "角色", "威廉姆斯旧属"),'),
    "55192762362ebdc7f3e3193e": ('        E("针叶林", "地点", "躲避之处"),',
                                 '        E("孤岛", "地点", "流放之地"),\n'
                                 '        E("针叶林", "地点", "躲避之处"),'),
    "b58c2ba1660dda15e20c8ccf": ('        E("绿街", "概念", "政治犯所受之刑"),',
                                 '        E("绿街", "概念", "政治犯所受之刑"),\n'
                                 '        E("孤岛", "地点", "流放之地"),'),
    "e6cd3caa0c815d202fb40dd1": ('        E("孤岛", "地点", "刻字之地"),',
                                 '        E("孤岛", "地点", "刻字之地"),\n'
                                 '        E("冬", "角色", "被议论的本尊"),\n'
                                 '        E("梅德维奇", "角色", "冬的棕熊朋友"),'),
}
for key, (old, new) in fixes.items():
    i = s.index(f'BATCH["{key}"]')
    j = s.index("\n}\n", i)
    seg = s[i:j]
    ent_start = seg.index('"entities"')
    rel_start = seg.index('"relations"')
    add = new.split("\n")[1:]
    missing = [ln for ln in add if ln.strip() and ln.strip() not in seg[ent_start:rel_start]]
    if missing:
        s = s[:i] + seg.replace(old, old + "\n" + "\n".join(missing), 1) + s[j:]

p.write_text(s, encoding="utf-8")
print("patched")
