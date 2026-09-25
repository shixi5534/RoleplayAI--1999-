# -*- coding: utf-8 -*-
"""修正 _gen_batch128.py（第二轮）：
1) 所有 `E("阿历克塞", ...)` 声明改名为全名并挂 alias（与端点一致）；
2) 缩短超长 evidence。
"""
import re
from pathlib import Path

p = Path(__file__).resolve().parent / "_gen_batch128.py"
s = p.read_text(encoding="utf-8")

# 1) 实体声明改全名 + alias（保留原 desc）
def rep(m):
    desc = m.group(1)
    return (f'E("阿历克塞·费奥多罗维奇·雷列耶夫", "角色", {desc}, ["阿历克塞"])')

s, n = re.subn(r'E\("阿历克塞", "角色", ("[^"]*")\)', rep, s)

# 2) 超长 evidence 缩短
s = s.replace('"列兵阿历克塞·费奥多罗维奇·雷列耶夫，在乌哈拉郊外执行搜救任务时枪杀了一位协从军战友"',
              '"在乌哈拉郊外执行搜救任务时枪杀了一位协从军战友"')

p.write_text(s, encoding="utf-8")
print(f"renamed entity declarations: {n}")
