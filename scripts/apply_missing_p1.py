# -*- coding: utf-8 -*-
"""无缓存块补抽 · 第 1 批（14 块，中文高信息量块）。

原则（沿用 408 块回填的保守标准）：
- 只抽正文明确出现的实体，不靠背景知识外推；
- 实体名用中文正名，正文里的原词（英文/别称）放进 aliases 以便落地；
- 关系谓语必须中文；src/dst 必须落在本块 entities 的 name/aliases 内；
- 代词、泛指（「他们」「那个东西」）一律不抽。

用法（项目根目录）：
  python scripts/apply_missing_p1.py --apply
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "knowledge" / "plot_cache" / "wu_ming_zhe"

RESULTS: dict[str, dict] = {
    # v2.5 电玩餐馆：斯考特被操控、奇星夺走《三燕归巢》
    "4119deda9e96057d": {
        "entities": [
            {"name": "斯考特", "type": "角色", "aliases": ["斯考特小姐", "Scott"]},
            {"name": "佩德拉", "type": "角色", "aliases": ["佩德拉先生"]},
            {"name": "比利", "type": "角色", "aliases": []},
            {"name": "波蒂埃", "type": "角色", "aliases": ["波蒂埃长官"]},
            {"name": "梁月", "type": "角色", "aliases": []},
            {"name": "埃尔登警长", "type": "角色", "aliases": ["埃尔登"]},
            {"name": "菲林士多", "type": "角色", "aliases": ["菲林士多导演"]},
            {"name": "奇星", "type": "角色", "aliases": ["奇星小姐"]},
            {"name": "三燕归巢", "type": "物品", "aliases": ["《三燕归巢》"]},
            {"name": "针人", "type": "角色", "aliases": []},
            {"name": "人偶", "type": "物品", "aliases": []},
            {"name": "电玩餐馆", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "比利", "dst": "佩德拉", "relation": "通知", "confidence": 0.9},
            {"src": "菲林士多", "dst": "人偶", "relation": "操控", "confidence": 0.9},
            {"src": "奇星", "dst": "三燕归巢", "relation": "夺走", "confidence": 0.9},
            {"src": "梁月", "dst": "奇星", "relation": "未能阻止", "confidence": 0.8},
            {"src": "埃尔登警长", "dst": "波蒂埃", "relation": "增援", "confidence": 0.8},
        ],
    },
    # v2.5 电影散场：奇星与菲林士多复盘泰瑞莎
    "c391d660cf68a68a": {
        "entities": [
            {"name": "奇星", "type": "角色", "aliases": ["奇星小姐"]},
            {"name": "菲林士多", "type": "角色", "aliases": []},
            {"name": "泰瑞莎", "type": "角色", "aliases": []},
            {"name": "执夜人", "type": "角色", "aliases": ["执夜人小姐"]},
            {"name": "强梁", "type": "角色", "aliases": []},
            {"name": "电影", "type": "物品", "aliases": ["这部电影"]},
        ],
        "relations": [
            {"src": "奇星", "dst": "电影", "relation": "拍摄", "confidence": 0.9},
            {"src": "菲林士多", "dst": "泰瑞莎", "relation": "评价", "confidence": 0.85},
            {"src": "奇星", "dst": "强梁", "relation": "致歉", "confidence": 0.8},
            {"src": "奇星", "dst": "执夜人", "relation": "感谢", "confidence": 0.85},
        ],
    },
    # v1.8 来亚什基建镇：克努特、阿德里安筛矿石
    "1be8255f5cb6f54f": {
        "entities": [
            {"name": "来亚什基", "type": "地点", "aliases": ["这座镇子"]},
            {"name": "克努特", "type": "角色", "aliases": ["克努特同志"]},
            {"name": "叶甫根尼", "type": "角色", "aliases": ["叶甫根尼同志"]},
            {"name": "阿德里安", "type": "角色", "aliases": []},
            {"name": "卢恩矿石", "type": "物品", "aliases": ["矿石"]},
            {"name": "工厂精神", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "克努特", "dst": "叶甫根尼", "relation": "提及", "confidence": 0.8},
            {"src": "阿德里安", "dst": "卢恩矿石", "relation": "筛分", "confidence": 0.9},
            {"src": "来亚什基", "dst": "卢恩矿石", "relation": "蕴藏", "confidence": 0.85},
        ],
    },
    # v1.8 劳动食堂：孩子们放纸飞机、基金会来人
    "0696b915ba754751": {
        "entities": [
            {"name": "尼娜", "type": "角色", "aliases": []},
            {"name": "彼得森", "type": "角色", "aliases": ["彼得森同学"]},
            {"name": "阿夫西维", "type": "角色", "aliases": ["阿夫西维同学"]},
            {"name": "帕索诺", "type": "角色", "aliases": []},
            {"name": "维拉", "type": "角色", "aliases": ["维拉老师"]},
            {"name": "乌里扬娜", "type": "角色", "aliases": ["乌里扬娜老师"]},
            {"name": "海燕", "type": "角色", "aliases": []},
            {"name": "圣洛夫基金会", "type": "组织", "aliases": ["基金会"]},
            {"name": "纸飞机", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "尼娜", "dst": "纸飞机", "relation": "放飞", "confidence": 0.9},
            {"src": "彼得森", "dst": "尼娜", "relation": "比试", "confidence": 0.8},
            {"src": "维拉", "dst": "帕索诺", "relation": "照看", "confidence": 0.75},
            {"src": "圣洛夫基金会", "dst": "维拉", "relation": "接洽", "confidence": 0.7},
        ],
    },
    # v1.8 雪人与理线学：学者在来亚什基重拾理线学
    "c9d02d27d1fc53de": {
        "entities": [
            {"name": "来亚什基", "type": "地点", "aliases": ["小镇"]},
            {"name": "维拉", "type": "角色", "aliases": ["维拉老师"]},
            {"name": "理线学", "type": "概念", "aliases": []},
            {"name": "研究所", "type": "组织", "aliases": []},
            {"name": "工人们", "type": "组织", "aliases": ["工人"]},
            {"name": "雪人", "type": "物品", "aliases": ["雪人同志们"]},
            {"name": "矿石", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "理线学", "dst": "来亚什基", "relation": "应用于", "confidence": 0.85},
            {"src": "工人们", "dst": "来亚什基", "relation": "建造", "confidence": 0.85},
            {"src": "研究所", "dst": "理线学", "relation": "研究", "confidence": 0.8},
        ],
    },
    # v2.3 伦敦大雾：黑雾、肺结核、神秘学家
    "be41aa734cf7c837": {
        "entities": [
            {"name": "泰晤士河", "type": "地点", "aliases": ["泰晤士河畔"]},
            {"name": "黑雾", "type": "现象", "aliases": []},
            {"name": "肺结核", "type": "概念", "aliases": []},
            {"name": "神秘术", "type": "概念", "aliases": []},
            {"name": "神秘学家", "type": "角色", "aliases": []},
            {"name": "药剂", "type": "物品", "aliases": []},
        ],
        "relations": [
            # 「掀翻房子」里的房子是泛指，按保守原则不抽为实体，故不建该边
            {"src": "神秘学家", "dst": "黑雾", "relation": "研究", "confidence": 0.75},
            {"src": "肺结核", "dst": "泰晤士河", "relation": "蔓延于", "confidence": 0.7},
        ],
    },
    # v3.5 迷思海：劳伦·罗西、灰调蓝、贝丽尔
    "672a422d0a083307": {
        "entities": [
            {"name": "莱瑟姆", "type": "角色", "aliases": []},
            {"name": "迷思海", "type": "概念", "aliases": ["意象宝库", "集体潜意识的海洋"]},
            {"name": "劳伦·罗西", "type": "角色", "aliases": ["罗西教授"]},
            {"name": "重塑之手", "type": "组织", "aliases": []},
            {"name": "灰调蓝", "type": "角色", "aliases": ["阿黛拉·塔沃尼尔"]},
            {"name": "贝丽尔·布翁尼", "type": "角色", "aliases": ["贝丽尔"]},
            {"name": "法兰西之蓝", "type": "物品", "aliases": []},
            {"name": "1936年", "type": "时间", "aliases": []},
        ],
        "relations": [
            {"src": "劳伦·罗西", "dst": "重塑之手", "relation": "隶属", "confidence": 0.9},
            {"src": "劳伦·罗西", "dst": "迷思海", "relation": "研究", "confidence": 0.9},
            {"src": "贝丽尔·布翁尼", "dst": "灰调蓝", "relation": "带往", "confidence": 0.85},
            {"src": "1936年", "dst": "迷思海", "relation": "发生", "confidence": 0.75},
        ],
    },
    # v3.2 费利西安被回溯、地下墓穴
    "73903774306223de": {
        "entities": [
            {"name": "费利西安", "type": "角色", "aliases": []},
            {"name": "灰调蓝", "type": "角色", "aliases": []},
            {"name": "保罗", "type": "角色", "aliases": []},
            {"name": "地下墓穴", "type": "地点", "aliases": []},
            {"name": "巴黎", "type": "地点", "aliases": []},
            {"name": "暴雨", "type": "事件", "aliases": []},
        ],
        "relations": [
            {"src": "费利西安", "dst": "暴雨", "relation": "消失于", "confidence": 0.85},
            {"src": "保罗", "dst": "地下墓穴", "relation": "潜入", "confidence": 0.8},
            {"src": "费利西安", "dst": "灰调蓝", "relation": "相识", "confidence": 0.7},
        ],
    },
    # v1.5 乌卢鲁圣火与运动会
    "f7ca366835cec424": {
        "entities": [
            {"name": "沙丝绒", "type": "角色", "aliases": []},
            {"name": "报刊亭老板", "type": "角色", "aliases": []},
            {"name": "乌卢鲁圣火", "type": "概念", "aliases": ["圣火", "那团火"]},
            {"name": "乌卢鲁运动会", "type": "事件", "aliases": []},
            {"name": "乌卢鲁岩地", "type": "地点", "aliases": []},
            {"name": "假票", "type": "物品", "aliases": ["假票的走向"]},
        ],
        "relations": [
            {"src": "沙丝绒", "dst": "假票", "relation": "追查", "confidence": 0.9},
            {"src": "报刊亭老板", "dst": "沙丝绒", "relation": "提供情报", "confidence": 0.85},
            {"src": "乌卢鲁运动会", "dst": "乌卢鲁岩地", "relation": "举办于", "confidence": 0.9},
            {"src": "乌卢鲁圣火", "dst": "乌卢鲁运动会", "relation": "象征", "confidence": 0.9},
        ],
    },
    # 斯奈德身世：格雷克夫妇、地下市场
    "2c86feb7735a9811": {
        "entities": [
            {"name": "斯奈德", "type": "角色", "aliases": []},
            {"name": "格雷克夫妇", "type": "角色", "aliases": ["格雷克太太"]},
            {"name": "地下市场", "type": "地点", "aliases": []},
            {"name": "圣体礼", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "斯奈德", "dst": "地下市场", "relation": "进入", "confidence": 0.85},
            {"src": "格雷克夫妇", "dst": "斯奈德", "relation": "收养", "confidence": 0.7},
        ],
    },
    # v1.7 维也纳：有丝分裂派、镜子
    "a27a188d20155824": {
        "entities": [
            {"name": "维也纳", "type": "地点", "aliases": ["这座城市"]},
            {"name": "有丝分裂派", "type": "组织", "aliases": []},
            {"name": "镜子", "type": "物品", "aliases": ["小镜子"]},
            {"name": "华尔兹", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "有丝分裂派", "dst": "维也纳", "relation": "活跃于", "confidence": 0.8},
            {"src": "镜子", "dst": "维也纳", "relation": "映出", "confidence": 0.75},
        ],
    },
    # 拉普拉斯：小梅斯梅尔评分零食
    "91b83c929ac58365": {
        "entities": [
            {"name": "小梅斯梅尔", "type": "角色", "aliases": []},
            {"name": "拉普拉斯", "type": "组织", "aliases": ["拉普拉斯科算中心"]},
            {"name": "投影中转器", "type": "物品", "aliases": []},
            {"name": "利佳比特", "type": "组织", "aliases": []},
            {"name": "评分表", "type": "物品", "aliases": ["遗落的评分表"]},
        ],
        "relations": [
            {"src": "小梅斯梅尔", "dst": "拉普拉斯", "relation": "隶属", "confidence": 0.9},
            {"src": "小梅斯梅尔", "dst": "评分表", "relation": "填写", "confidence": 0.85},
            {"src": "小梅斯梅尔", "dst": "投影中转器", "relation": "调试", "confidence": 0.8},
        ],
    },
    # v2.1 小镇怪谈：露丝、摩根神父、约翰尼
    "fee4a962af91bdfc": {
        "entities": [
            {"name": "露丝", "type": "角色", "aliases": []},
            {"name": "摩根神父", "type": "角色", "aliases": ["神父"]},
            {"name": "皮尔斯", "type": "角色", "aliases": []},
            {"name": "玛丽塔", "type": "角色", "aliases": []},
            {"name": "约翰尼", "type": "角色", "aliases": []},
            {"name": "旅馆", "type": "地点", "aliases": []},
            {"name": "休斯顿", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "皮尔斯", "dst": "休斯顿", "relation": "前往", "confidence": 0.85},
            {"src": "约翰尼", "dst": "旅馆", "relation": "念叨", "confidence": 0.8},
            {"src": "摩根神父", "dst": "露丝", "relation": "安抚", "confidence": 0.7},
        ],
    },
    # v2.2 赌局与职业牌手
    "5b0cbfbf2b9262ff": {
        "entities": [
            {"name": "赌局", "type": "事件", "aliases": []},
            {"name": "职业牌手", "type": "角色", "aliases": ["身穿白色西装的职业牌手"]},
            {"name": "骰子", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "职业牌手", "dst": "赌局", "relation": "参与", "confidence": 0.85},
            {"src": "赌局", "dst": "骰子", "relation": "使用", "confidence": 0.8},
        ],
    },
}


def validate() -> int:
    """写盘前自检：关系端点必须能解析到本块实体的 name/aliases。"""
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
            if not str(r.get("relation") or "").strip():
                print(f"[no-pred] {h}")
                bad += 1
    return bad


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    n = validate()
    print(f"[validate] 块 {len(RESULTS)}，悬空/缺谓语 {n}")
    if n:
        return 1
    if not args.apply:
        print("[dry-run] 校验通过，加 --apply 写盘")
        return 0

    written = 0
    for h, d in RESULTS.items():
        p = CACHE / f"{h}.json"
        p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
        written += 1
    print(f"[apply-missing-p1] 写入 {written} 条")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
