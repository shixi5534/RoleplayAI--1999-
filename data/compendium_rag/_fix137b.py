# -*- coding: utf-8 -*-
"""修正 _gen_batch137.py：把幽灵男孩的**节点名**改为不与他章「杰克」前缀冲突的形式。

根因：graph_store._merge_candidates 规则②（保守全名归并）会把
`杰克` 并入 `杰克·斯塔尔`（long.startswith(short) 且 rest[0] == '·'），
因为两个名字在整个语料命名空间里共存 → 报社记者「杰克」(飞渡往日)
被错并进本作的幽灵男孩。

修法：男孩节点名用描述性称谓 `斯塔尔家的男孩`，把真名 `杰克·斯塔尔` 放进 aliases。
注意：**别名不参与规则②**，且只有当某写法本身是「实体名或关系端点」时才进 dsu.p，
故把 `杰克·斯塔尔` 限制在 aliases 内即可彻底避免误并，同时不丢失真名。
"""
from pathlib import Path

p = Path(__file__).resolve().parent / "_gen_batch137.py"
s = p.read_text(encoding="utf-8")

s = s.replace(
    'JACK = "杰克·斯塔尔"',
    'JACK = "斯塔尔家的男孩"   # 真名 杰克·斯塔尔 放 aliases，避免与他章的「杰克」被规则②误并')

# 男孩实体声明：挂上真名别名
s = s.replace(
    'E(JACK, "角色", "衣柜里的男孩"),',
    'E(JACK, "角色", "衣柜里的男孩", ["杰克·斯塔尔"]),')
s = s.replace(
    'E(JACK, "角色", "寻找父亲的孩子"),',
    'E(JACK, "角色", "寻找父亲的孩子", ["杰克·斯塔尔"]),')

p.write_text(s, encoding="utf-8")
print("patched")
