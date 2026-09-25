# -*- coding: utf-8 -*-
"""清理 _gen_batch125.py：删自环、补端点。"""
import re
from pathlib import Path

p = Path(__file__).resolve().parent / "_gen_batch125.py"
s = p.read_text(encoding="utf-8")

pat = re.compile(r'^\s*R\("([^"]+)",\s*"[^"]+",\s*"\1",[^\n]*\n', re.M)
s, n = pat.subn("", s)

fixes = {
    "6f46842b6c2915c5b6cd3475": ('        E("红宝石", "物品", "鸽子血似的"),',
                                 '        E("红宝石", "物品", "鸽子血似的"),\n'
                                 '        E("老贵族", "角色", "未谋面的婚约者"),\n'
                                 '        E("掮客", "角色", "促成契约者"),'),
    "576b56eef0babbaa83d4ff0a": ('        E("书信", "物品", "留予父亲"),',
                                 '        E("书信", "物品", "留予父亲"),\n'
                                 '        E("父亲", "角色", "奥德之父"),'),
    "8f41a693ce40a9e6dbc1c679": ('        E("宝藏", "物品", "分予农民"),',
                                 '        E("宝藏", "物品", "分予农民"),\n'
                                 '        E("皇帝", "角色", "泥鯭的士所怨者"),'),
    "efead6c70646564324c31464": ('        E("笑话", "概念", "所蕴能量"),',
                                 '        E("笑话", "概念", "所蕴能量"),\n'
                                 '        E("战场", "概念", "奥利弗所惧"),'),
    "6893450b2ec96714d4883fc2": ('        E("箱中实验室", "地点", "实验之处"),',
                                 '        E("箱中实验室", "地点", "实验之处"),\n'
                                 '        E("实验室安全守则", "概念", "所违之规"),'),
    "981eec5af4e0588e7e5a0310": ('        E("汽车", "物品", "被拍打之车"),',
                                 '        E("汽车", "物品", "被拍打之车"),\n'
                                 '        E("十四行诗", "角色", "接传单者"),'),
    "f6d125baf3b3e9abd71688a9": ('        E("地下车库", "地点", "所设之处"),',
                                 '        E("地下车库", "地点", "所设之处"),\n'
                                 '        E("十四行诗", "角色", "寻人者"),\n'
                                 '        E("泼水机", "物品", "上一个机器"),'),
    "2839d77baa99dbd0c693526b": ('        E("弹珠飞行器", "物品", "所拆之器"),',
                                 '        E("弹珠飞行器", "物品", "所拆之器"),\n'
                                 '        E("母亲", "角色", "小女孩之母"),\n'
                                 '        E("苏菲", "角色", "患病的孩子"),'),
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
print(f"self-loops removed: {n}")
