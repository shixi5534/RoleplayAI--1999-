# -*- coding: utf-8 -*-
"""修正 _gen_batch132.py：补 5 块缺失端点。"""
from pathlib import Path

p = Path(__file__).resolve().parent / "_gen_batch132.py"
s = p.read_text(encoding="utf-8")

FIXES = {
    "c7634b738ae1220d86d01cc5": ('        E("小径", "地点", "月光所落"),',
                                 '        E("小径", "地点", "月光所落"),\n'
                                 '        E("血迹", "物品", "刀上所留"),'),
    "061c3b31468919a46a825f36": ('        E("秘密地点", "地点", "囚禁之所"),',
                                 '        E("秘密地点", "地点", "囚禁之所"),\n'
                                 '        E("人质", "概念", "待救者"),\n'
                                 '        E("彩蛋", "物品", "所制之物"),\n'
                                 '        E("赎金", "概念", "未索之财"),'),
    "4c7745f2a2c411cadae76e9a": ('        E("诗", "物品", "流浪女人所作"),',
                                 '        E("诗", "物品", "流浪女人所作"),\n'
                                 '        E("线索", "概念", "彩蛋所载"),\n'
                                 '        E("诺娜·伊斯特", "角色", "远程引爆者"),'),
    "74d55e5700c1d02a5f3b0d91": ('        E("圣斯蒂芬大教堂", "地点", "满溢阳光"),',
                                 '        E("圣斯蒂芬大教堂", "地点", "满溢阳光"),\n'
                                 '        E("诺娜·伊斯特", "角色", "所锁定者"),'),
    "304318d7d2cdd5ec00201e6a": ('        E("多瑙河", "地点", "诅咒横渡之河"),',
                                 '        E("多瑙河", "地点", "诅咒横渡之河"),\n'
                                 '        E("软弹枪", "物品", "教堂所射"),'),
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
