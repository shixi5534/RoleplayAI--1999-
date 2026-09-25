# -*- coding: utf-8 -*-
"""补 _gen_batch136.py 缺失端点 + 修一处 self-loop。"""
from pathlib import Path

p = Path(__file__).resolve().parent / "_gen_batch136.py"
s = p.read_text(encoding="utf-8")

# 删 拉拉泉 -练习-> 拉拉泉 自环（改为「练习」自介，指向 气球派对 更合原文）
s = s.replace('        R("拉拉泉", "练习", "拉拉泉", "我、我是泉水精灵……拉拉泉！", 0.7),\n', "")
s = s.replace('        R("拉拉泉", "请求", "气球派对",',
              '        R("拉拉泉", "练习", "气球派对", "我、我是泉水精灵……拉拉泉！", 0.95),\n'
              '        R("拉拉泉", "请求", "气球派对",')

FIXES = {
    "b6f2857e4ef669c6a623989b": ('        E("洪水", "概念", "未退之水"),',
                                 '        E("洪水", "概念", "未退之水"),\n'
                                 '        E("众人", "角色", "旁听者"),\n'
                                 '        E("泉水精灵特辑", "事件", "所播栏目"),'),
    "d64b9df5d96cf771aa531f82": ('        E("X-301号海绵型清理船", "物品", "吸水之船", ["X-301号"]),',
                                 '        E("X-301号海绵型清理船", "物品", "吸水之船", ["X-301号"]),\n'
                                 '        E("真实世界", "概念", "难以接受之全貌"),'),
    "8cfa53304305634e2224a966": ('        E("洪水", "概念", "已退之水"),',
                                 '        E("洪水", "概念", "已退之水"),\n'
                                 '        E("朋友", "概念", "所倚之人"),\n'
                                 '        E("泉水精灵特辑", "事件", "所播栏目"),\n'
                                 '        E("箱庭", "地点", "洪水所淹"),'),
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
