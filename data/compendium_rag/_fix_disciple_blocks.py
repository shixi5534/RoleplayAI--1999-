# -*- coding: utf-8 -*-
"""修复「组织名被挂在成员节点上」的块（§4.12 残留之一：重塑·门徒Ⅰ–Ⅳ）。

语料事实（mainline__105_洞穴的囚徒:19.0.1，已反查块原文）：
    **重塑·门徒Ⅰ**：ㄏㄡˇ——！   ← 四个**独立说话人**
    冰冷的岩洞深处，重塑之手的门徒正疯狂用头撞击着墙壁。
    **维尔汀**：……看来，刚刚的阿其翁，真身就是重塑之手。

原抽取却写成：`重塑·门徒1`(type=**组织**, aliases=**['重塑之手']`)，Ⅱ–Ⅳ 同为「组织」。
→ 别名方向倒置（把组织写成个人的别名）+ 类型错标，DSU 于是把
  `重塑之手` 与 `重塑·门徒Ⅰ` 焊成同一节点，组织与成员一起失真。

处置（§4.11 规避口径「需要可解析的写法优先建独立节点」）：
  ① Ⅰ–Ⅳ 改为独立 角色 节点，剥掉倒置 alias；
  ② 新建 `重塑之手`（组织）节点；
  ③ 补 `Ⅰ–Ⅳ 隶属于 重塑之手`，证据用旁白原句（关系不再凭空挂在组织名上）。

另一块 anecdote__1904_埃里克角色故事:4.2.0(`8c8c92…`) 实测**本就**把
`重塑·门徒Ⅰ/Ⅱ` 声明为独立 角色 节点，无倒置 alias，故不在本遍范围内。

定点替换：before-state 断言不成立即退出 1，绝不静默改别的块。
用法（本目录）：python _fix_disciple_blocks.py [--apply]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / "cache"

KEY = "be2f07852f65d59bd46103bd"
MEMBERS = ["重塑·门徒Ⅰ", "重塑·门徒Ⅱ", "重塑·门徒Ⅲ", "重塑·门徒Ⅳ"]
ORG = "重塑之手"
EV_MEMBERSHIP = "重塑之手的门徒正疯狂用头撞击着墙壁"


def patch(raw: dict) -> tuple[dict, list[str]]:
    ents = raw["entities"]
    rels = raw["relations"]
    by = {e["name"]: e for e in ents}
    assert set(MEMBERS) <= set(by), f"缺成员节点：{set(MEMBERS) - set(by)}"
    assert by[MEMBERS[0]].get("aliases") == [ORG], \
        f"Ⅰ 的 alias 非预期：{by[MEMBERS[0]].get('aliases')}"
    assert all(by[m]["type"] == "组织" for m in MEMBERS), "成员类型已非「组织」"
    assert ORG not in by, f"{ORG} 已是独立节点，无需再改"
    assert not any(r["src"] == ORG or r["dst"] == ORG for r in rels
                   if r["relation"] == "隶属于"), "隶属关系已存在"

    log = []
    for m in MEMBERS:
        by[m]["type"] = "角色"
        by[m]["aliases"] = []
    log.append(f"{MEMBERS[0]} 倒置 alias ['{ORG}'] → []；Ⅰ–Ⅳ 类型 组织→角色")
    ents.append({"name": ORG, "type": "组织", "aliases": [], "desc": "阿其翁的真身"})
    log.append(f"新建独立 组织 节点「{ORG}」")
    for m in MEMBERS:
        rels.append({"src": m, "relation": "隶属于", "dst": ORG,
                     "evidence": EV_MEMBERSHIP, "confidence": 0.95})
    log.append(f"补 {len(MEMBERS)} 条 成员-隶属于->{ORG}（证据=旁白原句）")
    return raw, log


def main() -> int:
    apply = "--apply" in sys.argv
    f = CACHE / KEY[:2] / f"{KEY}.json"
    if not f.exists():
        print(f"!! 缺文件 {f}")
        return 1
    doc = json.loads(f.read_text(encoding="utf-8"))
    if doc.get("__cache_format__") != "raw":
        print(f"!! 缓存格式异常：{doc.get('__cache_format__')}")
        return 1
    before = (len(doc["raw"]["entities"]), len(doc["raw"]["relations"]))
    try:
        raw, log = patch(doc["raw"])
    except AssertionError as e:
        print(f"!! {KEY} 断言失败：{e}（可能已修过）")
        return 1
    print(f"[{KEY}] 实体 {before[0]}→{len(raw['entities'])}"
          f"｜关系 {before[1]}→{len(raw['relations'])}")
    for line in log:
        print("     ·", line)

    if not apply:
        print("\n[DRY-RUN] 未写盘")
        return 0
    f.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    n_b = 0
    for p in sorted(ROOT.glob("_agent_batch*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            print(f"!! 无法解析 {p.name}，跳过")
            continue
        if KEY not in data or not isinstance(data[KEY], dict):
            continue
        data[KEY] = raw
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        n_b += 1
    print(f"\n[APPLY] 已写 cache 1 块｜batch 文件改动 {n_b} 个")
    return 0


if __name__ == "__main__":
    sys.exit(main())
