# -*- coding: utf-8 -*-
"""只读探针：核对 batch139 计划用名是否已在 graph.json 中，避免重复建节点。

用法：& $py data/compendium_rag/_probe_names139.py
零网络、零写入（只读 graph.json）。
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
g = json.loads((ROOT / "graph.json").read_text(encoding="utf-8"))
ents = {e["name"]: e for e in g["entities"]}

# 计划沿用的既有名（同一对象 → 必须复用原值）
REUSE = [
    "37", "6", "X", "小梅斯梅尔", "兔毛手袋", "爱兹拉", "维尔汀", "苏菲亚",
    "挖掘艺术", "教众Ⅱ", "科算中心", "霍夫曼", "格拉瓦库斯", "纸杯蛋糕",
    "暴雨", "店主", "数学", "真理", "小岛", "伦敦", "卡纳比街", "重塑之手",
    "镜面肥皂泡", "海报", "整数", "无理数", "几何体", "沙滩",
]

# 计划新建的名（应与现有图无同名冲突）
NEW = [
    "拉普拉斯博物馆", "拉普拉斯科算中心", "拉普拉斯研究员Ⅰ", "拉普拉斯研究员Ⅱ",
    "参观者Ⅰ", "参观者Ⅱ", "参观者Ⅲ", "缺席", "误差", "柏拉图立体",
    "乘法轴上的一天", "海岬尽头", "数轴", "冰淇淋", "奇迹之星", "奇迹之石",
    "巨岩魔", "砂金石榴子石", "鳞翼石", "湛极矿", "象鼻虫", "黄金比例",
    "正十二面体", "气动管道", "引火线虫草", "火山地带", "莎草纸信件",
    "跳房子", "格线", "海鸥", "冰淇淋店", "圆桌", "活力", "秩序",
    "伊索尔德", "藏品", "稿纸", "几何模型", "引火线虫草子座",
    "气动送餐罐", "冰淇淋海报", "数学女神", "相扑比赛",
]


def main() -> None:
    print("── 既有名核对（应为 YES）──")
    bad = []
    for n in REUSE:
        e = ents.get(n)
        print(f"{'YES' if e else ' no'}  {n}"
              + (f"  [{e['type']}] {e.get('desc','')[:40]}" if e else ""))
        if not e:
            bad.append(n)
    print()
    print("── 新名冲突核对（应全为 no）──")
    clash = []
    for n in NEW:
        if n in ents:
            clash.append(n)
            print(f"YES {n}  ← 已存在，需复用！  [{ents[n]['type']}]")
        else:
            print(f" no {n}")
    print()
    # 子串提示：新名若是某个既有名的子串（或反之）会引发检索串扰，仅提示不拦
    print("── 子串提示 ──")
    for n in NEW:
        for m in ents:
            if n != m and (n in m or m in n) and len(m) >= 2:
                print(f"  提示：{n}  <->  {m}")
    print()
    print(f"REUSE 缺失 {len(bad)} 个：{bad}")
    print(f"NEW 冲突 {len(clash)} 个：{clash}")
    print(f"graph 实体总数 {len(ents)}")


if __name__ == "__main__":
    main()
