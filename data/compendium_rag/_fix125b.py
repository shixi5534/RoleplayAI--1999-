# -*- coding: utf-8 -*-
"""续修 _gen_batch125.py：补齐剩余端点 + 去掉无实体的「四方」。"""
from pathlib import Path

p = Path(__file__).resolve().parent / "_gen_batch125.py"
s = p.read_text(encoding="utf-8")

# 「四方」非实体，改关系为「奥德 游历 城堡」→ 直接删该行
s = s.replace('        R("奥德", "游历", "四方", "她在战胜了巨人之后，在四方游历", 0.9),\n', "")

fixes = {
    "2cd2d5299f039cea2d3e4ed3": ('        E("里拉琴", "物品", "吟游诗人所拨"),',
                                 '        E("里拉琴", "物品", "吟游诗人所拨"),\n'
                                 '        E("吟游诗人", "角色", "巧舌如簧者"),'),
    "981eec5af4e0588e7e5a0310": ('        E("汽车", "物品", "被拍打之车"),',
                                 '        E("汽车", "物品", "被拍打之车"),\n'
                                 '        E("威尔森医药公司", "组织", "所涉之企"),'),
    "875593444315caa6b3b81c03": ('        E("暴雨", "事件", "将临之灾"),',
                                 '        E("暴雨", "事件", "将临之灾"),\n'
                                 '        E("威尔森医药公司", "组织", "所涉之企"),'),
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
