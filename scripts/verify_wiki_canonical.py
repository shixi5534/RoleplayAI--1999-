#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
正典覆盖率审计：用灰机 wiki 查证得到的权威设定，反向检验知识图谱。

数据来源：deliverables/wiki-r1999-relation-reference-20260909.md
  - 第 2.1 节 阵营敌对/合作关系（置信度 高）
  - 第 3 节   核心人物关系表（以无名者为中心）

判定口径：
  HIT      — 两实体均存在且其间存在边（报告实际谓语）
  NO_EDGE  — 两实体均存在，但无直接边（图谱缺口）
  MISSING  — 至少一側实体在图谱中不存在（抽取未覆盖）
  N/A      — 低置信度事实，仅记录不参与统计

用法：
  .venv/Scripts/python.exe -X utf8 scripts/verify_wiki_canonical.py [--json]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

PLOT_PATH = os.path.join(ROOT, "data", "knowledge", "plot_graph_wu_ming_zhe.json")
LORE_PATH = os.path.join(ROOT, "data", "knowledge", "graph_wu_ming_zhe.json")

# ---------------------------------------------------------------- 正典事实表
# (A, 关系, B, 置信度, 备注)
# 置信度取自 wiki 报告；低置信度（低）不参与断言统计
CANON_RELATIONS = [
    # —— 第 2.1 节 阵营关系（官方名词诠释，置信度 高）——
    ("圣洛夫基金会", "对抗", "重塑之手", "高", "基金会头号敌人"),
    ("圣洛夫基金会", "隶属", "鸽子屋", "高", "人类和平安全理事会"),
    ("圣洛夫基金会", "包含", "拉普拉斯科算中心", "高", "基金会研究部门"),
    ("拉普拉斯科算中心", "包含", "洛伦兹研究所", "高", "隐藏于科算中心内部"),
    ("芝诺军备学院", "隶属", "鸽子屋", "高", "鸽子屋常备军队"),
    # —— 第 3 节 人物关系（置信度 高）——
    ("维尔汀", "隶属", "圣洛夫基金会", "高", "司辰，司辰小队领导人"),
    ("康斯坦丁", "任职", "圣洛夫基金会", "高", "副会长，实际掌权者"),
    ("阿尔卡纳", "指挥", "重塑之手", "高", "重塑之手首领"),
    # 注：勿忘我个体剧情属尚未导入的早期剧情，plot 语料缺该实体属预期行为
    ("勿忘我", "隶属", "重塑之手", "高", "重塑之手骨干（个体剧情未导入 plot 语料）"),
    ("露西", "任职", "拉普拉斯科算中心", "高", "总负责人，已革职"),
    ("哑谜", "任职", "拉普拉斯科算中心", "高", "负责人/洛伦兹成员"),
    ("无名者", "隶属", "圣洛夫基金会", "高", "第十三章末加入司辰小队"),
    # —— 第 3 节 人物关系（置信度 中）——
    ("无名者", "曾隶属", "重塑之手", "中", "展品卡：曾短暂展出于重塑之手"),
    ("无名者", "亲属", "康斯坦丁", "中", "养母，称「普帕」→「母亲」"),
    ("无名者", "同伴", "维尔汀", "中", "这本书能继续写下去的理由"),
    ("无名者", "隶属", "勿忘我", "中", "直属上级（个体剧情未导入 plot 语料）"),
    ("无名者", "对抗", "阿尔卡纳", "中", "破坏发条装置"),
    ("无名者", "治疗", "小梅斯梅尔", "中", "人工梦游治疗师"),
    ("无名者", "身份替代", "凯拉", "中", "外貌相似的农场女孩"),
    # —— 第 3 节（置信度 低，仅记录）——
    ("无名者", "被改造", "琥珀屋", "低", "真实身份官方从未明确交代"),
]

# 别名兜底：wiki 用名 → 图谱可能用的名字
NAME_FALLBACK = {
    "鸽子屋": ["鸽子屋", "人类和平安全理事会", "The Pax House", "理事会"],
    "哑谜": ["哑谜", "阿德勒·霍夫曼", "阿德勒", "霍夫曼"],
    "小梅斯梅尔": ["小梅斯梅尔", "梅斯梅尔", "Mesmer Jr."],
    "康斯坦丁": ["康斯坦丁", "康散丁"],
    "维尔汀": ["维尔汀", "Vertin", "维尔特", "维特"],
    "圣洛夫基金会": ["圣洛夫基金会", "基金会", "St. Pavlov Foundation"],
    "重塑之手": ["重塑之手", "Manus Vindictae"],
    "拉普拉斯科算中心": ["拉普拉斯科算中心", "拉普拉斯", "科算中心"],
    "洛伦兹研究所": ["洛伦兹研究所", "洛伦兹"],
    "芝诺军备学院": ["芝诺军备学院", "芝诺"],
    "无名者": ["无名者", "Ms. Stranger", "Ms. Grace", "淑女格蕾丝", "陌生人小姐",
               "无名之人", "格蕾丝", "莉莉", "凯拉", "塞西莉", "飞蛾", "普帕"],
    "琥珀屋": ["琥珀屋"],
}

# 纠错断言：无名者为「岩」灵感，图谱中不应出现「智」属性边
WRONG_ATTR_PATTERNS = ["智属性", "智系", "属性为智", "灵感为智"]


def load_graph(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_name_index(graph: dict) -> dict:
    """名字/别名 -> [eid]，全部小写去空格做键"""
    idx = defaultdict(list)
    for eid, node in graph.get("entities", {}).items():
        names = [node.get("name", "")] + list(node.get("aliases") or [])
        for n in names:
            if n:
                idx[n.strip()].append(eid)
    return idx


def resolve(name: str, name_index: dict) -> list:
    """按名字解析 eid，先用别名兜底表，再精确匹配"""
    candidates = NAME_FALLBACK.get(name, [name])
    for cand in candidates:
        if cand in name_index:
            return name_index[cand]
    # 退化为子串包含匹配。
    # 注意：必须要求两侧长度都 >= 2，否则单字别名会造成严重误匹配
    # （例如节点 "deflected" 的 alias 是 "我"，会把 "勿忘我" 错误解析过去）
    hits = []
    for known, eids in name_index.items():
        if len(known) < 2:
            continue
        for c in candidates:
            if len(c) < 2:
                continue
            if c in known or known in c:
                hits.extend(eids)
                break
    return list(dict.fromkeys(hits))


def build_adjacency(graph: dict) -> dict:
    """(a,b) -> [relation]，无向"""
    adj = defaultdict(list)
    for e in graph.get("edges", []):
        adj[(e["src"], e["dst"])].append(e.get("relation", ""))
        adj[(e["dst"], e["src"])].append(e.get("relation", ""))
    return adj


def audit_one(graph_name: str, graph: dict) -> list:
    name_index = build_name_index(graph)
    adj = build_adjacency(graph)
    results = []
    for a, rel, b, conf, note in CANON_RELATIONS:
        ea, eb = resolve(a, name_index), resolve(b, name_index)
        if not ea or not eb:
            status, actual = "MISSING", []
        elif set(ea) & set(eb):
            # 两端解析到同一实体：图谱把 B 当成了 A 的别名，该关系无法在图中表达
            status, actual = "SAME_ENTITY", []
        else:
            actual = []
            for x in ea:
                for y in eb:
                    if x == y:
                        continue
                    actual.extend(adj.get((x, y), []))
            actual = sorted(set(actual))
            status = "HIT" if actual else "NO_EDGE"
        results.append({
            "graph": graph_name, "a": a, "relation": rel, "b": b,
            "confidence": conf, "note": note, "status": status,
            "actual_relations": actual,
        })
    return results


def check_attr_error(graph_name: str, graph: dict) -> list:
    """纠错验证：查找把无名者标成「智」属性的边"""
    name_index = build_name_index(graph)
    wm = set(resolve("无名者", name_index))
    bad = []
    for e in graph.get("edges", []):
        rel = e.get("relation", "")
        if e.get("src") in wm or e.get("dst") in wm:
            if any(p in rel for p in WRONG_ATTR_PATTERNS):
                bad.append(rel)
    return sorted(set(bad))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    graphs = {}
    for gname, path in (("plot", PLOT_PATH), ("lore", LORE_PATH)):
        graphs[gname] = load_graph(path) if os.path.exists(path) else None

    out = {"graphs": {}, "attr_error": {}}
    for gname, g in graphs.items():
        if g is None:
            out["graphs"][gname] = None
            continue
        res = audit_one(gname, g)
        out["graphs"][gname] = res
        out["attr_error"][gname] = check_attr_error(gname, g)

    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0

    for gname in ("plot", "lore"):
        res = out["graphs"].get(gname)
        print(f"\n{'='*72}\n{gname.upper()} 图谱 · 灰机正典覆盖率\n{'='*72}")
        if res is None:
            print("  [图谱文件不存在]")
            continue
        print(f"{'状态':<8}{'置信':<5}{'A':<16}{'关系':<10}{'B':<18}{'图谱实际谓语'}")
        print("-" * 72)
        for r in res:
            actual = "/".join(r["actual_relations"][:4]) if r["actual_relations"] else "—"
            print(f"{r['status']:<8}{r['confidence']:<6}{r['a']:<14}{r['relation']:<10}"
                  f"{r['b']:<16}{actual}")
        stat = defaultdict(int)
        for r in res:
            stat[r["status"]] += 1
        scored = [r for r in res if r["confidence"] in ("高", "中")]
        hit = sum(1 for r in scored if r["status"] == "HIT")
        print("-" * 72)
        print(f"HIT={stat['HIT']}  NO_EDGE={stat['NO_EDGE']}  MISSING={stat['MISSING']}")
        print(f"高+中置信度覆盖率：{hit}/{len(scored)} = {hit/len(scored)*100:.1f}%")
        bad = out["attr_error"].get(gname) or []
        print(f"属性纠错检查（不应出现「智」属性边）：{'未发现 ✅' if not bad else '发现 ' + str(bad) + ' ❌'}")

    # —— 并集覆盖率：混合检索时两图谱任一命中即算覆盖 ——
    plot_res = out["graphs"].get("plot") or []
    lore_res = out["graphs"].get("lore") or []
    if plot_res and lore_res:
        union_hit = 0
        scored_u = []
        print(f"\n{'='*72}\n并集覆盖率（plot ∪ lore，混合检索口径）\n{'='*72}")
        for p, l in zip(plot_res, lore_res):
            if p["confidence"] not in ("高", "中"):
                continue
            scored_u.append(p)
            if p["status"] == "HIT" or l["status"] == "HIT":
                union_hit += 1
            else:
                print(f"  未覆盖：{p['a']} —{p['relation']}— {p['b']}（{p['confidence']}）")
        print(f"\n并集覆盖：{union_hit}/{len(scored_u)} = {union_hit/len(scored_u)*100:.1f}%")
        out["union"] = {"hit": union_hit, "total": len(scored_u)}

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
