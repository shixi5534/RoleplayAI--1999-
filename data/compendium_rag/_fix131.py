# -*- coding: utf-8 -*-
"""修正 _gen_batch131.py：补 6 块缺失端点。"""
from pathlib import Path

p = Path(__file__).resolve().parent / "_gen_batch131.py"
s = p.read_text(encoding="utf-8")

FIXES = {
    "af6838e48e59a92109d7d31a": ('        E("墨镜", "物品", "遮光之器"),',
                                 '        E("墨镜", "物品", "遮光之器"),\n'
                                 '        E("维也纳", "地点", "返归之城"),\n'
                                 '        E("阳光", "概念", "所畏之光"),'),
    "995c92bdffd0a7ab4487d85d": ('        E("肯恩顿街", "地点", "所偏好之路"),',
                                 '        E("肯恩顿街", "地点", "所偏好之路"),\n'
                                 '        E("致幻粉尘", "概念", "燃烧所生"),'),
    "babc61f74c5ed3a52d9e0913": ('        E("露天餐厅", "地点", "遮阳棚下"),',
                                 '        E("露天餐厅", "地点", "遮阳棚下"),\n'
                                 '        E("人行道", "地点", "摔倒之处"),\n'
                                 '        E("靶子", "物品", "所击之标"),'),
    "812b81bcb5efa0d0af5b0b6c": ('        E("珍宝彩蛋", "物品", "所寻目标"),',
                                 '        E("珍宝彩蛋", "物品", "所寻目标"),\n'
                                 '        E("诺娜·伊斯特", "角色", "所查之人"),'),
    "f540fd0d8c47117509f62d06": ('        E("诺娜·伊斯特的工作室", "地点", "案发之处"),',
                                 '        E("诺娜·伊斯特的工作室", "地点", "案发之处"),\n'
                                 '        E("抽屉", "物品", "被撬之屉"),'),
    "fbe7714a07d73da63c9d38f4": ('        E("警笛", "概念", "随风起伏"),',
                                 '        E("警笛", "概念", "随风起伏"),\n'
                                 '        E("神秘术", "概念", "气味重现之术"),\n'
                                 '        E("诺娜·伊斯特", "角色", "被推断者"),'),
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
