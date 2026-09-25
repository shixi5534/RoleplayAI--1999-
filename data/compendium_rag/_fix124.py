# -*- coding: utf-8 -*-
"""清理 _gen_batch124.py：删自环、修 artifact、补端点。"""
import re
from pathlib import Path

p = Path(__file__).resolve().parent / "_gen_batch124.py"
s = p.read_text(encoding="utf-8")

# 1) 自环
pat = re.compile(r'^\s*R\("([^"]+)",\s*"[^"]+",\s*"\1",[^\n]*\n', re.M)
s, n = pat.subn("", s)

# 2) artifact
s = s.replace('E("恒常之剑", "角色", "罗兰之剑", 0.0) if False else E("恒常之剑", "物品", "罗兰所用"),',
              'E("恒常之剑", "物品", "罗兰所用"),')

# 3) 补端点：按块，仅插入 entities 段
fixes = {
    "6b119dbf24ad3dcba13659ee": ('        E("箱中走廊", "地点", "通往图书室"),',
                                 '        E("箱中走廊", "地点", "通往图书室"),\n'
                                 '        E("圣洛夫基金会", "组织", "收诗稿方"),\n'
                                 '        E("孤岛", "地点", "留驻之地"),'),
    "07740006cb0c43ad4f8f5289": ('        E("年代", "概念", "所问之题"),',
                                 '        E("年代", "概念", "所问之题"),\n'
                                 '        E("箱内一隅", "地点", "辉光管所在"),'),
    "fb3970feaca1db8db11915bb": ('        E("潘蓬特森林", "地点", "伏击之地"),',
                                 '        E("潘蓬特森林", "地点", "伏击之地"),\n'
                                 '        E("笑话节", "事件", "加尼隆所提议"),'),
    "32d27ebfa51d483d3ce20434": ('        E("未锈铠房间", "地点", "故事会之处"),',
                                 '        E("未锈铠房间", "地点", "故事会之处"),\n'
                                 '        E("奥德", "角色", "出谜的女骑士"),'),
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
