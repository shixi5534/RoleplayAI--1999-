# -*- coding: utf-8 -*-
"""无缓存/空块补抽 · 第 4 批（15 块高价值剧情块）。

同批 605e7def3e158736 是心相/技能数值页（所敬献者、减益集合、创伤倍率），
非剧情文本，登记为 NOOP。

用法：python scripts/apply_missing_p4.py --apply
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "knowledge" / "plot_cache" / "wu_ming_zhe"
NOOP_FILE = ROOT / "data" / "knowledge" / "_audit" / "noop_confirmed.json"

NOOP_ADD = ["605e7def3e158736"]

RESULTS: dict[str, dict] = {
    # v3.8 关于「不可回溯地」的第一次会议
    "4c39c478c6d69817": {
        "entities": [
            {"name": "肯纳", "type": "角色", "aliases": ["肯纳女士"]},
            {"name": "委员A", "type": "角色", "aliases": []},
            {"name": "委员B", "type": "角色", "aliases": []},
            {"name": "不可回溯地", "type": "地点", "aliases": []},
            {"name": "格拉斯哥", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "肯纳", "dst": "不可回溯地", "relation": "主张勘察", "confidence": 0.9},
            {"src": "委员A", "dst": "肯纳", "relation": "质疑", "confidence": 0.85},
            {"src": "肯纳", "dst": "格拉斯哥", "relation": "驻留", "confidence": 0.7},
        ],
    },
    # v3.8 藏起来的信：致奥尔加
    "66312acbb8345a53": {
        "entities": [
            {"name": "奥尔加", "type": "角色", "aliases": ["亲爱的奥尔加"]},
            {"name": "马雷克", "type": "角色", "aliases": []},
            {"name": "卢齐安", "type": "角色", "aliases": []},
            {"name": "格但斯克", "type": "地点", "aliases": []},
            {"name": "诺瓦米奇", "type": "地点", "aliases": []},
            {"name": "北港", "type": "地点", "aliases": []},
            {"name": "闷罐火车", "type": "物品", "aliases": ["运牲口的闷罐火车"]},
        ],
        "relations": [
            {"src": "马雷克", "dst": "奥尔加", "relation": "致信", "confidence": 0.85},
            {"src": "闷罐火车", "dst": "卢齐安", "relation": "吞噬", "confidence": 0.8},
            {"src": "奥尔加", "dst": "诺瓦米奇", "relation": "来自", "confidence": 0.8},
            {"src": "马雷克", "dst": "格但斯克", "relation": "居住", "confidence": 0.85},
        ],
    },
    # v3.7 袭击事件调查：风网、歌唱家
    "6b206e95ab9add21": {
        "entities": [
            {"name": "雨前调度中心", "type": "组织", "aliases": []},
            {"name": "临时调查委员会", "type": "组织", "aliases": []},
            {"name": "风网", "type": "概念", "aliases": ["神秘术阵"]},
            {"name": "歌唱家", "type": "角色", "aliases": []},
            {"name": "重塑之手", "type": "组织", "aliases": []},
            {"name": "暴雨", "type": "事件", "aliases": []},
        ],
        "relations": [
            {"src": "歌唱家", "dst": "重塑之手", "relation": "隶属", "confidence": 0.85},
            {"src": "重塑之手", "dst": "风网", "relation": "使用", "confidence": 0.85},
            {"src": "临时调查委员会", "dst": "风网", "relation": "调查", "confidence": 0.8},
        ],
    },
    # v2.5 通缉令：金伯利女郎、勿忘我
    "5decf843e212652a": {
        "entities": [
            {"name": "金伯利女郎", "type": "角色", "aliases": ["金伯利"]},
            {"name": "勿忘我", "type": "角色", "aliases": []},
            {"name": "重塑之手", "type": "组织", "aliases": []},
            {"name": "夜巡特遣", "type": "组织", "aliases": ["夜巡特遣管理局"]},
            {"name": "唐人街", "type": "地点", "aliases": []},
            {"name": "摄提神", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "勿忘我", "dst": "重塑之手", "relation": "隶属", "confidence": 0.9},
            {"src": "夜巡特遣", "dst": "金伯利女郎", "relation": "通缉", "confidence": 0.85},
            {"src": "唐人街", "dst": "摄提神", "relation": "供奉", "confidence": 0.8},
        ],
    },
    # v1.5 喷雾配方清单
    "d9300861bd82120f": {
        "entities": [
            {"name": "翠绿静息喷雾", "type": "物品", "aliases": ["<翠绿静息喷雾>"]},
            {"name": "丛伞胶孔菌诊断喷雾", "type": "物品", "aliases": []},
            {"name": "鸡油菌", "type": "物品", "aliases": []},
            {"name": "苍耳", "type": "物品", "aliases": ["菊科苍耳"]},
            {"name": "铁线蕨", "type": "物品", "aliases": []},
            {"name": "丛伞胶孔菌", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "翠绿静息喷雾", "dst": "鸡油菌", "relation": "含", "confidence": 0.9},
            {"src": "翠绿静息喷雾", "dst": "铁线蕨", "relation": "含", "confidence": 0.85},
            {"src": "丛伞胶孔菌诊断喷雾", "dst": "丛伞胶孔菌", "relation": "含", "confidence": 0.85},
        ],
    },
    # v1.9 暴雨避难通告
    "39bf9bffdc5e62cc": {
        "entities": [
            {"name": "司辰", "type": "角色", "aliases": []},
            {"name": "调查员", "type": "角色", "aliases": []},
            {"name": "总部", "type": "组织", "aliases": []},
            {"name": "暴雨", "type": "事件", "aliases": ["“暴雨”"]},
        ],
        "relations": [
            {"src": "司辰", "dst": "暴雨", "relation": "预警", "confidence": 0.9},
            {"src": "调查员", "dst": "总部", "relation": "返回", "confidence": 0.9},
        ],
    },
    # v1.9 韦耶豪瑟女士监察报告
    "e493310e1b4c3629": {
        "entities": [
            {"name": "韦耶豪瑟", "type": "角色", "aliases": ["韦耶豪瑟女士"]},
            {"name": "圣洛夫基金会", "type": "组织", "aliases": ["基金会"]},
            {"name": "树木处理班", "type": "组织", "aliases": ["临时树木处理班"]},
            {"name": "工程部", "type": "组织", "aliases": []},
            {"name": "森林事件", "type": "事件", "aliases": []},
        ],
        "relations": [
            {"src": "韦耶豪瑟", "dst": "森林事件", "relation": "涉及", "confidence": 0.9},
            {"src": "韦耶豪瑟", "dst": "树木处理班", "relation": "加入", "confidence": 0.9},
            {"src": "圣洛夫基金会", "dst": "韦耶豪瑟", "relation": "处罚", "confidence": 0.85},
            {"src": "树木处理班", "dst": "工程部", "relation": "供应", "confidence": 0.8},
        ],
    },
    # v2.0 唐吉老爹的餐馆由来
    "88ea463ea8372b6e": {
        "entities": [
            {"name": "J", "type": "角色", "aliases": []},
            {"name": "唐吉老爹", "type": "角色", "aliases": ["老爹"]},
            {"name": "餐馆", "type": "地点", "aliases": []},
            {"name": "维斯塔公园", "type": "地点", "aliases": []},
            {"name": "海特街", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "唐吉老爹", "dst": "餐馆", "relation": "开设", "confidence": 0.9},
            {"src": "唐吉老爹", "dst": "维斯塔公园", "relation": "途经", "confidence": 0.75},
            {"src": "J", "dst": "唐吉老爹", "relation": "相识", "confidence": 0.8},
        ],
    },
    # v2.1 德克萨斯派对：特里波德罗传闻
    "8af4747db4116328": {
        "entities": [
            {"name": "农场主", "type": "角色", "aliases": []},
            {"name": "马修", "type": "角色", "aliases": ["大个子马修"]},
            {"name": "哈罗德警督", "type": "角色", "aliases": []},
            {"name": "特里波德罗", "type": "角色", "aliases": ["Tripodero"]},
            {"name": "77号公路", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "农场主", "dst": "特里波德罗", "relation": "讲述", "confidence": 0.85},
            {"src": "哈罗德警督", "dst": "马修", "relation": "委托修车", "confidence": 0.8},
            {"src": "特里波德罗", "dst": "77号公路", "relation": "出没", "confidence": 0.75},
        ],
    },
    # v3.8 奠基石与蓝图论建筑几何
    "7d971acce9c272a9": {
        "entities": [
            {"name": "奠基石", "type": "角色", "aliases": []},
            {"name": "蓝图", "type": "角色", "aliases": []},
            {"name": "柏拉图", "type": "角色", "aliases": []},
            {"name": "蒂迈欧", "type": "物品", "aliases": ["《蒂迈欧》"]},
            {"name": "诺瓦米奇", "type": "地点", "aliases": []},
            {"name": "基本形", "type": "概念", "aliases": ["完美的圆"]},
        ],
        "relations": [
            {"src": "柏拉图", "dst": "蒂迈欧", "relation": "著", "confidence": 0.85},
            {"src": "奠基石", "dst": "柏拉图", "relation": "援引", "confidence": 0.85},
            {"src": "诺瓦米奇", "dst": "基本形", "relation": "采用", "confidence": 0.8},
        ],
    },
    # v3.6 玩具箱实验：乌尔里希与阿德勒
    "b40f1ed6f6baf575": {
        "entities": [
            {"name": "缪斯三世", "type": "角色", "aliases": []},
            {"name": "玩具箱", "type": "物品", "aliases": []},
            {"name": "拉普拉斯科算中心", "type": "组织", "aliases": ["科算中心", "拉普拉斯"]},
            {"name": "乌尔里希", "type": "角色", "aliases": ["乌尔里希研究员"]},
            {"name": "阿德勒", "type": "角色", "aliases": ["阿德勒研究员"]},
            {"name": "雨前紧急状况应对指南", "type": "物品", "aliases": []},
            {"name": "自由海风号", "type": "事件", "aliases": ["“自由海风号”事件"]},
            {"name": "人工暴雨", "type": "概念", "aliases": []},
            {"name": "暴雨", "type": "事件", "aliases": ["第九次“暴雨”"]},
        ],
        "relations": [
            {"src": "乌尔里希", "dst": "玩具箱", "relation": "主持", "confidence": 0.9},
            {"src": "阿德勒", "dst": "玩具箱", "relation": "监督", "confidence": 0.9},
            {"src": "缪斯三世", "dst": "玩具箱", "relation": "提供", "confidence": 0.85},
            {"src": "乌尔里希", "dst": "自由海风号", "relation": "参与", "confidence": 0.8},
        ],
    },
    # v3.7 关于五座高塔的传闻
    "801b95879c5a9fb5": {
        "entities": [
            {"name": "高塔", "type": "地点", "aliases": ["五座高塔", "那五座塔"]},
            {"name": "学校", "type": "组织", "aliases": []},
            {"name": "学生", "type": "角色", "aliases": []},
            {"name": "老师", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "学校", "dst": "高塔", "relation": "建造", "confidence": 0.85},
            {"src": "学生", "dst": "高塔", "relation": "禁止进入", "confidence": 0.85},
            {"src": "老师", "dst": "高塔", "relation": "值守", "confidence": 0.75},
        ],
    },
    # v3.7 传送软盘配给说明
    "3a9e18cab8e68106": {
        "entities": [
            {"name": "传送软盘", "type": "物品", "aliases": []},
            {"name": "总部", "type": "组织", "aliases": []},
            {"name": "战争核心冲突地区", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "总部", "dst": "传送软盘", "relation": "配发", "confidence": 0.9},
            {"src": "传送软盘", "dst": "战争核心冲突地区", "relation": "产自", "confidence": 0.85},
        ],
    },
    # v2.5 拉普拉斯康复中心广告
    "69f5c70f791fd579": {
        "entities": [
            {"name": "拉普拉斯康复中心", "type": "组织", "aliases": ["康复中心"]},
            {"name": "血食怪", "type": "角色", "aliases": []},
            {"name": "龙", "type": "角色", "aliases": []},
            {"name": "甲壳虫", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "拉普拉斯康复中心", "dst": "血食怪", "relation": "治疗咬伤", "confidence": 0.8},
        ],
    },
    # v2.5 波蒂埃与梁月搜查胶片
    "3602932bc64b84c4": {
        "entities": [
            {"name": "波蒂埃", "type": "角色", "aliases": ["波蒂埃长官"]},
            {"name": "梁月", "type": "角色", "aliases": []},
            {"name": "菲林士多", "type": "角色", "aliases": ["菲林士多女士"]},
            {"name": "僵尸女士", "type": "物品", "aliases": ["《僵尸女士》"]},
            {"name": "胶片", "type": "物品", "aliases": ["那盘胶片", "电影胶卷"]},
            {"name": "C07", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "波蒂埃", "dst": "胶片", "relation": "搜查", "confidence": 0.9},
            {"src": "梁月", "dst": "僵尸女士", "relation": "推荐", "confidence": 0.85},
            {"src": "菲林士多", "dst": "胶片", "relation": "收藏", "confidence": 0.8},
            {"src": "波蒂埃", "dst": "梁月", "relation": "搭档", "confidence": 0.85},
        ],
    },
}


def validate() -> int:
    bad = 0
    for h, d in RESULTS.items():
        pool = set()
        for e in d.get("entities") or []:
            pool.add(str(e.get("name") or "").strip())
            pool |= {str(a).strip() for a in (e.get("aliases") or [])}
        for r in d.get("relations") or []:
            for k in ("src", "dst"):
                if str(r.get(k) or "").strip() not in pool:
                    print(f"[dangling] {h} {k}={r.get(k)}")
                    bad += 1
    return bad


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    n = validate()
    print(f"[validate] 块 {len(RESULTS)}，悬空 {n}")
    if n:
        return 1
    if not args.apply:
        print("[dry-run] 加 --apply 写盘")
        return 0
    for h, d in RESULTS.items():
        (CACHE / f"{h}.json").write_text(
            json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    for h in NOOP_ADD:
        (CACHE / f"{h}.json").write_text(
            json.dumps({"entities": [], "relations": []}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        noop = set(json.loads(NOOP_FILE.read_text(encoding="utf-8")))
        noop.add(h)
        NOOP_FILE.write_text(
            json.dumps(sorted(noop), ensure_ascii=False, indent=1), encoding="utf-8"
        )
    print(f"[apply-missing-p4] 写入 {len(RESULTS)} 条，NOOP +{len(NOOP_ADD)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
