# -*- coding: utf-8 -*-
"""全库 alias 污染体检（只读）：泛称 alias、跨宿主共享 alias、被撑爆的枢纽节点。

为什么要跑全量而不是只看一个节点
--------------------------------
`女士`/`医生` 这类**裸泛称**挂在某个角色节点上时，实体链指会把任何含「女士」的查询
链到该节点，于是它的**整条邻边**都进了种子扩展 —— 卡卡尼亚实测 deg=439。
第 19~20 会话的 `_fix_alias_welds.py` 只处理了**当时发现的那批**（WELD_DROPS 逐条裁定），
本脚本负责把**整个图谱**扫一遍，给出还剩下的污染面，避免「只查最新一批」的老毛病。

输出三类，均打印**被扫群体的规模**（防「0 违规」实为「0 输入」）：
  A 裸泛称 alias：alias 命中泛称表，或 alias 在全语料的块频次 ≥ 阈值且不含宿主名
  B 跨宿主共享 alias：同一写法被 ≥2 个不同宿主声明（DSU 焊接的直接来源）
  C 枢纽节点：deg 排名前列 + 其中有多少来自 A 类
"""
from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from compendium_rag import pipeline as P  # noqa: E402
from compendium_rag.config import get_settings  # noqa: E402
from compendium_rag.graph_store import GraphStore  # noqa: E402

# 裸泛称：称谓/军衔/职务/群体名词，本身不指向任何唯一人物
GENERIC = set("""女士 先生 小姐 医生 老师 队长 士兵 队员 成员 观众 游客 记者 工作人员
同伴 朋友 敌人 少年 女孩 女人 男人 孩子 老人 乘客 职员 干部 同志 代表 司机 船长
牧师 护士 警察 士兵们 人们 某人 那个人 这个人 神秘学家 学生 教师 商人 农民 工人
矿工 渔民 水手 犯人 难民 贵族 仆人 丫鬟 学徒 导师 领袖 首领 头目 指挥官 将军
上校 中尉 少校 上尉 准将 元帅 警官 探长 侦探 作家 诗人 画家 演员 歌手 舞者
歌手们 组织者 参与者 旁观者 讲述者 记录者 发明者 建造者 守护者 守卫 哨兵 祭司""".split())


def main() -> int:
    s = get_settings()
    texts = [f"{c.text}\n{c.chapter_title}\n{c.scene_title}\n{c.part_title}"
             for c in P.load_chunks(s)]
    g = GraphStore.load(ROOT / "data/compendium_rag/graph.json")
    print(f"体检群体：实体 {len(g.entities)} 个 / 边 {len(g.edges)} 条 / 语料块 {len(texts)}")

    # 每个 alias 写法被哪些宿主声明（含以 name 形式出现的）
    declared: dict[str, set[str]] = defaultdict(set)
    for e in g.entities.values():
        declared[e.name].add(e.name)
        for a in (e.aliases or []):
            declared[a].add(e.name)

    df_cache: dict[str, int] = {}

    def df(w: str) -> int:
        if w not in df_cache:
            df_cache[w] = sum(1 for t in texts if w in t)
        return df_cache[w]

    a_rows, b_rows = [], []
    for e in g.entities.values():
        for a in (e.aliases or []):
            if a in GENERIC or (df(a) >= 150 and len(a) <= 5 and a not in e.name):
                a_rows.append((e.name, a, df(a), len(g.neighbors(e.eid)),
                               "泛称表" if a in GENERIC else "高频且不含宿主名"))
    for w, hosts in declared.items():
        if len(hosts) >= 2:
            b_rows.append((w, len(hosts), df(w), sorted(hosts)[:4]))

    a_rows.sort(key=lambda r: -r[3])
    b_rows.sort(key=lambda r: (-r[1], -r[2]))
    print(f"\nA 裸泛称/高频泛化 alias：{len(a_rows)} 条（涉及宿主 "
          f"{len(set(r[0] for r in a_rows))} 个）")
    for host, a, d, deg, why in a_rows[:25]:
        print(f"   {host} ← `{a}` 语料DF={d} 宿主deg={deg}  [{why}]")
    print(f"\nB 跨宿主共享写法：{len(b_rows)} 个（≥2 宿主，DSU 焊接来源）")
    for w, n, d, hosts in b_rows[:25]:
        print(f"   `{w}` 宿主数={n} 语料DF={d} → {hosts}")

    deg_top = sorted(g.entities.values(), key=lambda e: -len(g.neighbors(e.eid)))[:12]
    print("\nC deg 前 12 枢纽：")
    for e in deg_top:
        bad = [a for a in (e.aliases or []) if a in GENERIC]
        print(f"   {e.name} deg={len(g.neighbors(e.eid))} aliases={len(e.aliases or [])} "
              f"裸泛称={bad}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
