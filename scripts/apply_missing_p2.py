# -*- coding: utf-8 -*-
"""无缓存块补抽 · 第 2 批（6 块剧情块）。

同批读到的另外 12 块是游戏战斗数值页/UI 页，已由
`mark_noop_nonstory.py` 标记为确认 NOOP，不在这里抽。

用法：python scripts/apply_missing_p2.py --apply
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "knowledge" / "plot_cache" / "wu_ming_zhe"

RESULTS: dict[str, dict] = {
    # v1.8 来亚什基：维拉打开叶甫根尼留下的铁盒与遗信
    "c05aa473f0ccc67a": {
        "entities": [
            {"name": "维拉", "type": "角色", "aliases": ["维拉老师", "教师"]},
            {"name": "叶甫根尼", "type": "角色", "aliases": ["叶甫根尼同志"]},
            {"name": "小铁盒", "type": "物品", "aliases": ["盒子"]},
            {"name": "信纸", "type": "物品", "aliases": ["信"]},
            {"name": "来亚什基", "type": "地点", "aliases": ["镇上"]},
            {"name": "卢恩矿石", "type": "物品", "aliases": ["矿石"]},
        ],
        "relations": [
            {"src": "叶甫根尼", "dst": "小铁盒", "relation": "留下", "confidence": 0.9},
            {"src": "维拉", "dst": "信纸", "relation": "阅读", "confidence": 0.9},
            {"src": "叶甫根尼", "dst": "来亚什基", "relation": "规划", "confidence": 0.85},
            {"src": "来亚什基", "dst": "卢恩矿石", "relation": "开采", "confidence": 0.8},
        ],
    },
    # v2.0 新纪元集市：摊贩与占卜师议论「他们」寻找医生
    "1b8fe57edea2512d": {
        "entities": [
            {"name": "先驱者", "type": "角色", "aliases": ["假人伙计"]},
            {"name": "集市摊贩", "type": "角色", "aliases": ["摊贩"]},
            {"name": "集市占卜师", "type": "角色", "aliases": ["占卜师"]},
            {"name": "莱格斯", "type": "组织", "aliases": ["莱格斯那帮人"]},
            {"name": "新纪元集市", "type": "地点", "aliases": ["集市"]},
            {"name": "神秘病人", "type": "角色", "aliases": ["一位神秘的病人"]},
            {"name": "药草", "type": "物品", "aliases": ["稀罕的药草"]},
        ],
        "relations": [
            {"src": "集市摊贩", "dst": "神秘病人", "relation": "议论", "confidence": 0.85},
            {"src": "莱格斯", "dst": "药草", "relation": "搜集", "confidence": 0.8},
            {"src": "集市占卜师", "dst": "莱格斯", "relation": "评价", "confidence": 0.75},
            {"src": "先驱者", "dst": "新纪元集市", "relation": "现身", "confidence": 0.7},
        ],
    },
    # v3.5 墨西哥壁画运动：壁画三杰与午夜厨房
    "2f783009a631ceae": {
        "entities": [
            {"name": "墨西哥壁画运动", "type": "事件", "aliases": ["壁画运动"]},
            {"name": "里维拉", "type": "角色", "aliases": []},
            {"name": "奥罗斯科", "type": "角色", "aliases": []},
            {"name": "西凯罗斯", "type": "角色", "aliases": []},
            {"name": "午夜厨房", "type": "地点", "aliases": []},
            {"name": "1920年代", "type": "时间", "aliases": ["二十世纪第三个十年"]},
        ],
        "relations": [
            {"src": "墨西哥壁画运动", "dst": "1920年代", "relation": "兴起于", "confidence": 0.9},
            {"src": "里维拉", "dst": "墨西哥壁画运动", "relation": "参与", "confidence": 0.85},
            {"src": "奥罗斯科", "dst": "墨西哥壁画运动", "relation": "参与", "confidence": 0.85},
            {"src": "西凯罗斯", "dst": "墨西哥壁画运动", "relation": "参与", "confidence": 0.85},
            {"src": "午夜厨房", "dst": "墨西哥壁画运动", "relation": "见证", "confidence": 0.7},
        ],
    },
    # v2.6 打字机记录：重塑之手名义下的实验
    "8457983596a11c97": {
        "entities": [
            {"name": "重塑之手", "type": "组织", "aliases": []},
            {"name": "打字机记录", "type": "物品", "aliases": ["打字机记录#P12"]},
            {"name": "暗色带编织", "type": "物品", "aliases": ["暗色带编织·卷四"]},
            {"name": "福柯", "type": "角色", "aliases": []},
            {"name": "精神分析", "type": "概念", "aliases": []},
            {"name": "实验", "type": "事件", "aliases": []},
        ],
        "relations": [
            {"src": "重塑之手", "dst": "实验", "relation": "进行", "confidence": 0.8},
            {"src": "实验", "dst": "精神分析", "relation": "以…为名", "confidence": 0.75},
            {"src": "打字机记录", "dst": "重塑之手", "relation": "记载", "confidence": 0.8},
        ],
    },
    # v3.3 军事指令：布列科夫少将与各部队
    "e6067e2176343f97": {
        "entities": [
            {"name": "伊万·伊万诺维奇·布列科夫", "type": "角色", "aliases": ["布列科夫少将", "布列科夫"]},
            {"name": "芝诺军备学院", "type": "组织", "aliases": ["芝诺"]},
            {"name": "狩马部队", "type": "组织", "aliases": ["狩马"]},
            {"name": "老市民单位", "type": "组织", "aliases": ["老市民"]},
            {"name": "长尾巴部队", "type": "组织", "aliases": ["长尾巴"]},
            {"name": "坎查短剑营地", "type": "地点", "aliases": ["坎查短剑"]},
            {"name": "南方小城", "type": "地点", "aliases": []},
            # 正文写作「"暴雨"战争」，中间夹了引号，故别名用「暴雨」才能落地
            {"name": "暴雨战争", "type": "事件", "aliases": ["暴雨"]},
            {"name": "辎重", "type": "物品", "aliases": ["马匹、辎重"]},
        ],
        "relations": [
            {"src": "伊万·伊万诺维奇·布列科夫", "dst": "芝诺军备学院", "relation": "隶属", "confidence": 0.9},
            {"src": "伊万·伊万诺维奇·布列科夫", "dst": "暴雨战争", "relation": "参加", "confidence": 0.85},
            {"src": "狩马部队", "dst": "南方小城", "relation": "协防", "confidence": 0.8},
            {"src": "长尾巴部队", "dst": "狩马部队", "relation": "支援", "confidence": 0.8},
            {"src": "坎查短剑营地", "dst": "辎重", "relation": "保管", "confidence": 0.75},
        ],
    },
    # v3.0 炼金术滥用与配方残页
    "d4c9911d43b49669": {
        "entities": [
            {"name": "炼金术", "type": "概念", "aliases": []},
            {"name": "秘银", "type": "物品", "aliases": []},
            {"name": "负子蟾", "type": "物品", "aliases": []},
            {"name": "血根草", "type": "物品", "aliases": []},
            {"name": "松节油", "type": "物品", "aliases": []},
            {"name": "战场", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "炼金术", "dst": "战场", "relation": "滥用", "confidence": 0.85},
            {"src": "秘银", "dst": "炼金术", "relation": "催化", "confidence": 0.75},
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
    print(f"[apply-missing-p2] 写入 {len(RESULTS)} 条")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
