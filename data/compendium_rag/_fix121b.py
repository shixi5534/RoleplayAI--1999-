# -*- coding: utf-8 -*-
"""精修 _gen_batch121.py（第二轮）：按块精确定位补齐/去重/改名。"""
from pathlib import Path

p = Path(__file__).resolve().parent / "_gen_batch121.py"
s = p.read_text(encoding="utf-8")

BLOCKS = {
    "4754414c37035e5b7efb1472": ('        E("作业本", "物品", "所欠之物"),',
                                 '        E("作业本", "物品", "所欠之物"),\n'
                                 '        E("一群小船员", "角色", "聚拢的孩子们"),'),
    "cc39fea28a68e8dee6712ab0": ('        E("教管学校", "地点", "转学之处"),',
                                 '        E("教管学校", "地点", "转学之处"),\n'
                                 '        E("哈拉尔", "角色", "信中所念的外祖父"),'),
}
for key, (old, new) in BLOCKS.items():
    i = s.index(f'BATCH["{key}"]')
    j = s.index("\n}\n", i)
    seg = s[i:j]
    if new.split("\n")[1].strip() not in seg:
        seg = seg.replace(old, new, 1)
        s = s[:i] + seg + s[j:]

# 7.0.0：删掉重复的第二个 哈拉尔
i = s.index('BATCH["13b5ffd08945ce1403c66aa6"]')
j = s.index("\n}\n", i)
seg = s[i:j]
seg = seg.replace('        E("信纸", "物品", "最后之信"),\n        E("哈拉尔", "角色", "收信的外祖父"),',
                  '        E("信纸", "物品", "最后之信"),', 1)
s = s[:i] + seg + s[j:]

# 0.0.0：关系端点改名，与实体名一致（去掉「蜂」）
s = s.replace('R("苏芙比", "筹备", "独角兽肚脐酿蜂蜜黄油特饮"',
              'R("苏芙比", "筹备", "独角兽肚脐酿蜜黄油特饮"')

p.write_text(s, encoding="utf-8")
print("patched")
