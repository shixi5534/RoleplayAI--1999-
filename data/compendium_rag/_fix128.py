# -*- coding: utf-8 -*-
"""修正 _gen_batch128.py：
1) 端点 `阿历克塞` → 本名 `阿历克塞·费奥多罗维奇·雷列耶夫`（端点须用实体本名）；
2) 补齐缺失端点实体：学员／加油站／同志／敌人／士兵。
"""
from pathlib import Path

p = Path(__file__).resolve().parent / "_gen_batch128.py"
s = p.read_text(encoding="utf-8")

# 1) 端点改名：把 R(...) 中作为 src/dst 的 `阿历克塞` 换成全名
s = s.replace('R("阿历克塞",', 'R("阿历克塞·费奥多罗维奇·雷列耶夫",')
s = s.replace(', "阿历克塞",', ', "阿历克塞·费奥多罗维奇·雷列耶夫",')

fixes = {
    "15f9975965dd5038b6971891": ('        E("第七百五十六小队", "组织", "所指挥之队"),',
                                 '        E("第七百五十六小队", "组织", "所指挥之队"),\n'
                                 '        E("阿历克塞·费奥多罗维奇·雷列耶夫", "角色", "被控的列兵", ["阿历克塞"]),'),
    "3b62e6710063aa5163b34371": ('        E("黑色棺材", "物品", "卸下之物"),',
                                 '        E("黑色棺材", "物品", "卸下之物"),\n'
                                 '        E("学员", "角色", "赴战区的见习者"),'),
    "56cd417d5c739ff1241dadb9": ('        E("山谷", "地点", "如飞行跑道"),',
                                 '        E("山谷", "地点", "如飞行跑道"),\n'
                                 '        E("加油站", "地点", "被炸之处"),'),
    "b7a163974aa2631edf13fa0d": ('        E("雷达", "物品", "ПВ-1182 导航雷达"),',
                                 '        E("雷达", "物品", "ПВ-1182 导航雷达"),\n'
                                 '        E("同志", "角色", "同队战友"),\n'
                                 '        E("敌人", "角色", "山上的伏击者"),'),
    "2b5f5d4f4e11253eda9b94c5": ('        E("红色-38", "物品", "飞行载具"),',
                                 '        E("红色-38", "物品", "飞行载具"),\n'
                                 '        E("士兵", "角色", "受命者"),'),
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
