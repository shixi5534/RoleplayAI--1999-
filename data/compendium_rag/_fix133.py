# -*- coding: utf-8 -*-
"""修正 _gen_batch133.py：补 6 块缺失端点。"""
from pathlib import Path

p = Path(__file__).resolve().parent / "_gen_batch133.py"
s = p.read_text(encoding="utf-8")

FIXES = {
    "b1a0e14ecb66754340719a78": ('        E("鱼缸脸", "角色", "撰写愉悦研究者"),',
                                 '        E("鱼缸脸", "角色", "撰写愉悦研究者"),\n'
                                 '        E("司辰", "角色", "彩蛋订购者"),'),
    "3a3fafe2cf69164a7d0130c6": ('        E("箱内客厅", "地点", "整装之处"),',
                                 '        E("箱内客厅", "地点", "整装之处"),\n'
                                 '        E("父亲", "角色", "赠裙者"),'),
    "a823525f753fb676bc557f5c": ('        E("墙壁", "物品", "被炸出窟窿"),',
                                 '        E("墙壁", "物品", "被炸出窟窿"),\n'
                                 '        E("父亲", "角色", "赠糖者"),\n'
                                 '        E("苏芙比房间", "地点", "爆炸之处"),'),
    "f5d3ed20a867fcfe79fd6081": ('        E("苏芙比房间", "地点", "实验之处"),',
                                 '        E("苏芙比房间", "地点", "实验之处"),\n'
                                 '        E("玉米", "概念", "爆米花之源"),'),
    "7dcbb5f15fae661cc8b699fd": ('        E("天花板", "物品", "如夜空"),',
                                 '        E("天花板", "物品", "如夜空"),\n'
                                 '        E("护士小姐", "角色", "叮嘱者"),'),
    "81dc122f0f4058ad3265b9f8": ('        E("箱内客厅", "地点", "巡逻之处"),',
                                 '        E("箱内客厅", "地点", "巡逻之处"),\n'
                                 '        E("生日", "事件", "所睡过者"),'),
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
print("patched")
