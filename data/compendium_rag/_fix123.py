# -*- coding: utf-8 -*-
"""清理 _gen_batch123.py：删自环、修 artifact、补端点。"""
import re
from pathlib import Path

p = Path(__file__).resolve().parent / "_gen_batch123.py"
s = p.read_text(encoding="utf-8")

# 1) 自环
pat = re.compile(r'^\s*R\("([^"]+)",\s*"[^"]+",\s*"\1",[^\n]*\n', re.M)
s, n = pat.subn("", s)

# 2) artifact：if False else
s = s.replace('R("星之眼", "外访", "阿卡迪亚占位" if False else "单身公寓", "在那之后，星之眼也离开过几次行李箱", 0.9),',
              'R("星之眼", "外访", "单身公寓", "在那之后，星之眼也离开过几次行李箱", 0.9),')

# 3) 补端点
fixes = {
    "eb2941f803c4ea3e233bb8ee": ('        E("第九区特别调查组", "组织", "所派小队"),',
                                 '        E("第九区特别调查组", "组织", "所派小队"),\n'
                                 '        E("警察", "角色", "传令者"),'),
    "e4353c85346f0ea7d2b750de": ('        E("堪萨斯州", "地点", "威廉姆斯的家"),',
                                 '        E("堪萨斯州", "地点", "威廉姆斯的家"),\n'
                                 '        E("单身公寓", "地点", "旧居"),'),
    "1c2aea2faca3fd23ef4c900b": ('        E("孤岛", "地点", "人潮涌入"),',
                                 '        E("孤岛", "地点", "人潮涌入"),\n'
                                 '        E("记者", "角色", "索取者"),'),
}
for key, (old, new) in fixes.items():
    i = s.index(f'BATCH["{key}"]')
    j = s.index("\n}\n", i)
    seg = s[i:j]
    tail = new.split("\n")[1].strip()
    # 仅当该块 entities 段尚无此实体时插入
    ent_start = seg.index('"entities"')
    rel_start = seg.index('"relations"')
    if tail not in seg[ent_start:rel_start]:
        s = s[:i] + seg.replace(old, new, 1) + s[j:]

p.write_text(s, encoding="utf-8")
print(f"self-loops removed: {n}")
