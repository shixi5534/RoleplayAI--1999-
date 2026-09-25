# -*- coding: utf-8 -*-
"""定稿 _gen_batch137.py 的男孩命名（第三次修正）。

两次失败尝试记录（供后续同类问题参考）：
  ① `杰克·斯塔尔` 作节点名 → 被 graph_store 规则②（保守全名归并）与
     他章实体 `杰克` 合并（long.startswith(short) 且 rest[0]=='·'）。
  ② `斯塔尔家的男孩` 作节点名 → 被 extract.is_noise_name 判为噪声
     （GENERIC_PERSON_NOUNS 含「男孩」，name.endswith('男孩')）。
最终采用语料自带称谓 `小杰克`（朱迪原话「我们下次再找小杰克玩」）：
  既不被噪声规则拦，也不与 `杰克` 前缀合并；真名 `杰克·斯塔尔` 放 aliases。
"""
from pathlib import Path

p = Path(__file__).resolve().parent / "_gen_batch137.py"
s = p.read_text(encoding="utf-8")

s = s.replace(
    'JACK = "斯塔尔家的男孩"   # 真名 杰克·斯塔尔 放 aliases，避免与他章的「杰克」被规则②误并',
    'JACK = "小杰克"   # 语料自带称谓（朱迪原话）。真名 杰克·斯塔尔 放 aliases：\n'
    '                  #   用全名作节点名会被 graph_store 规则②误并进他章的「杰克」；\n'
    '                  #   用「……男孩」会被 is_noise_name 当噪声剔除。')

p.write_text(s, encoding="utf-8")
print("patched")
