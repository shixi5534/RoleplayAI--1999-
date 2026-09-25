# -*- coding: utf-8 -*-
"""修正 _gen_batch135.py：补 4 块缺失端点（并把「伦敦的大雾」改为已有实体「雾」）。"""
from pathlib import Path

p = Path(__file__).resolve().parent / "_gen_batch135.py"
s = p.read_text(encoding="utf-8")

# 「伦敦的大雾」并非本块实体，改用通用概念「雾」
s = s.replace('R("雾行者", "比拟", "伦敦的大雾"', 'R("雾行者", "比拟", "雾"')

FIXES = {
    "3449fa8ff7f35cd232d8142f": ('        E("死亡", "概念", "所不免者"),',
                                 '        E("死亡", "概念", "所不免者"),\n'
                                 '        E("苏芙比", "角色", "所论之淑女"),'),
    "671385f1f23d397cd5731771": ('        E("愿望", "概念", "所索之由"),',
                                 '        E("愿望", "概念", "所索之由"),\n'
                                 '        E("派对", "事件", "所筹之会"),'),
    "0e46d41f706c521806871ddc": ('        E("许愿精灵", "概念", "所自称者"),',
                                 '        E("许愿精灵", "概念", "所自称者"),\n'
                                 '        E("浪潮", "概念", "所涌之水"),'),
    "2b220e724a227f3137c4695e": ('        E("箱中集会", "地点", "汇聚之处"),',
                                 '        E("箱中集会", "地点", "汇聚之处"),\n'
                                 '        E("雾", "概念", "伦敦之雾"),'),
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
