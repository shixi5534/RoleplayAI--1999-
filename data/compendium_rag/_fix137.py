# -*- coding: utf-8 -*-
"""补 _gen_batch137.py 缺失端点 + 删自环 + 移除未使用的实体。"""
from pathlib import Path

p = Path(__file__).resolve().parent / "_gen_batch137.py"
s = p.read_text(encoding="utf-8")

# 1) 删自环（两具尸骸拥抱彼此，不是自环）
s = s.replace('        R("尸骸", "拥抱", "尸骸", "两具焦黑如炭的尸骸拥抱在一起", 0.7),\n', "")
# 2) 移除 4.0.1 中未使用的占位实体（「希望」在 2.0.1 另有专名条目）
s = s.replace('        E("希望", "概念", "所击碎者"),\n', "")

FIXES = {
    "af242b48de942c624c057822": ('        E("四柱床", "物品", "所置之床"),',
                                 '        E("四柱床", "物品", "所置之床"),\n'
                                 '        E("衣柜", "物品", "男孩藏身之处"),'),
    "32e432e0f2ccf8fb28d27167": ('        E("灵魂", "概念", "杰克所问"),',
                                 '        E("灵魂", "概念", "杰克所问"),\n'
                                 '        E("衣柜", "物品", "男孩钻出之处"),'),
    "21d6227efd28a095deec9d0d": ('        E("案发森林", "地点", "尸骸所在"),',
                                 '        E("案发森林", "地点", "尸骸所在"),\n'
                                 '        E("生活在希望中", "概念", "斯塔尔家纹章的题词"),'),
    "5fbd9562707e86f3ab775319": ('        E("求救的声音", "角色", "回荡之声"),',
                                 '        E("求救的声音", "角色", "回荡之声"),\n'
                                 '        E("重击", "事件", "来自背后的袭击"),'),
    "945bddbb63939574f7cdc5d9": ('        E("画纸", "物品", "所拍出者"),',
                                 '        E("画纸", "物品", "所拍出者"),\n'
                                 '        E("尼龙绳", "物品", "所缚之绳"),\n'
                                 '        E("漂白剂", "物品", "除痕之用"),'),
    "a299a5a68a55bcc1058f3eb4": ('        E("伊丽莎白·弗雷泽", "角色", "歌者"),',
                                 '        E("伊丽莎白·弗雷泽", "角色", "歌者"),\n'
                                 '        E("24号房", "地点", "朱迪所住"),'),
    "10c3e3c5a4ae3fadbd10584a": ('        E("地平线", "地点", "所望之处"),',
                                 '        E("地平线", "地点", "所望之处"),\n'
                                 '        E("州际公路", "地点", "行驶之路"),\n'
                                 '        E("火海", "概念", "梦中之焰"),'),
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
