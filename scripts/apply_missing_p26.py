# -*- coding: utf-8 -*-
"""未抽取剧情块补抽 · 第 26 批（backfill2 batch_16，19 块）。

用法：
  python scripts/apply_missing_p26.py            # 预演（悬空+落地自检）
  python scripts/apply_missing_p26.py --apply    # 写盘
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "knowledge" / "plot_cache" / "wu_ming_zhe"
NOOP_FILE = ROOT / "data" / "knowledge" / "_audit" / "noop_confirmed.json"
CORPUS = ROOT / "data" / "knowledge" / "plot_corpus_wu_ming_zhe.json"

# 本批 19 块均含剧情内容（含数值页尾部拼接对白），无纯数值/UI 空块。
NOOP_ADD: list[str] = []

RESULTS: dict[str, dict] = {
    # 1) 多瑙黎明号调查 · 鲍里斯先生与尼卡检查站
    "6e48046318c97714": {
        "entities": [
            {"name": "多瑙黎明号", "type": "物品", "aliases": ["“多瑙黎明号”"]},
            {"name": "鲍里斯先生", "type": "角色", "aliases": ["鲍里斯", "鲍里斯军官"]},
            {"name": "尼卡检查站", "type": "地点", "aliases": []},
            {"name": "塞梅尔维斯", "type": "角色", "aliases": []},
            {"name": "七十七分队", "type": "组织", "aliases": []},
            {"name": "三流小说", "type": "概念", "aliases": []},
            {"name": "普通而不普通的故事", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "鲍里斯先生", "dst": "尼卡检查站", "relation": "任职于", "confidence": 0.8},
        ],
    },
    # 2) 报纸拼贴 · 基金会伦敦会议与长毛绒绒运动会
    "c8c13c710990d6a1": {
        "entities": [
            {"name": "伦敦评论", "type": "物品", "aliases": ["《伦敦评论》"]},
            {"name": "立场", "type": "物品", "aliases": ["《立场》"]},
            {"name": "基金会", "type": "组织", "aliases": []},
            {"name": "基金会伦敦会议", "type": "事件", "aliases": []},
            {"name": "拼贴艺术", "type": "概念", "aliases": []},
            {"name": "拼贴画", "type": "物品", "aliases": []},
            {"name": "长毛绒绒运动会", "type": "事件", "aliases": ["“长毛绒绒运动会”"]},
            {"name": "达达主义", "type": "概念", "aliases": ["《无人问津的达达主义》"]},
            {"name": "大本钟", "type": "地点", "aliases": []},
            {"name": "海盗电台", "type": "组织", "aliases": ["《海盗电台被列入非法名单》"]},
            {"name": "拉米雷斯", "type": "角色", "aliases": ["《拉米雷斯宣告破产》"]},
        ],
        "relations": [
            {"src": "基金会伦敦会议", "dst": "基金会", "relation": "隶属", "confidence": 0.8},
            {"src": "立场", "dst": "伦敦评论", "relation": "刊登于", "confidence": 0.7},
            {"src": "拼贴艺术", "dst": "拼贴画", "relation": "包含", "confidence": 0.7},
            {"src": "拼贴艺术", "dst": "达达主义", "relation": "包含", "confidence": 0.7},
        ],
    },
    # 3) 被退回的信件 · 玛蒂尔达与环状水星对话
    "015724d5a6615ee0": {
        "entities": [
            {"name": "被退回的信件", "type": "物品", "aliases": []},
            {"name": "圣洛夫基金会", "type": "组织", "aliases": []},
            {"name": "霍利克", "type": "角色", "aliases": []},
            {"name": "保利娜", "type": "角色", "aliases": []},
            {"name": "修理铺", "type": "地点", "aliases": []},
            {"name": "餐馆", "type": "地点", "aliases": []},
            {"name": "宇宙禅", "type": "概念", "aliases": []},
            {"name": "玛蒂尔达", "type": "角色", "aliases": []},
            {"name": "环状水星", "type": "角色", "aliases": []},
            {"name": "疗愈师", "type": "概念", "aliases": []},
            {"name": "新纪元集市事件", "type": "事件", "aliases": ["“新纪元集市事件”"]},
        ],
        "relations": [
            {"src": "玛蒂尔达", "dst": "环状水星", "relation": "对话", "confidence": 0.7},
            {"src": "玛蒂尔达", "dst": "疗愈师", "relation": "是", "confidence": 0.8},
            {"src": "霍利克", "dst": "修理铺", "relation": "筹备", "confidence": 0.7},
            {"src": "被退回的信件", "dst": "保利娜", "relation": "寄给", "confidence": 0.7},
            {"src": "保利娜", "dst": "圣洛夫基金会", "relation": "到达", "confidence": 0.7},
        ],
    },
    # 4) 有场大赛要开始了 · J的地下拳击赛与《周六夜狂热》
    "5442629a21ad0f00": {
        "entities": [
            {"name": "有场大赛要开始了", "type": "事件", "aliases": ["“有场大赛要开始了”"]},
            {"name": "J", "type": "角色", "aliases": []},
            {"name": "地下拳击赛", "type": "事件", "aliases": []},
            {"name": "擂台", "type": "地点", "aliases": []},
            {"name": "贝克特", "type": "角色", "aliases": []},
            {"name": "墨西哥卷", "type": "物品", "aliases": []},
            {"name": "霍利克", "type": "角色", "aliases": []},
            {"name": "周六夜狂热", "type": "物品", "aliases": ["《周六夜狂热》"]},
            {"name": "S女士", "type": "角色", "aliases": []},
            {"name": "餐馆", "type": "地点", "aliases": []},
            {"name": "杂碎黑帮", "type": "组织", "aliases": []},
        ],
        "relations": [
            {"src": "J", "dst": "地下拳击赛", "relation": "参加", "confidence": 0.8},
            {"src": "地下拳击赛", "dst": "擂台", "relation": "使用", "confidence": 0.7},
            {"src": "贝克特", "dst": "J", "relation": "付给", "confidence": 0.7},
            {"src": "贝克特", "dst": "墨西哥卷", "relation": "购买", "confidence": 0.8},
            {"src": "J", "dst": "霍利克", "relation": "对话", "confidence": 0.7},
            {"src": "霍利克", "dst": "周六夜狂热", "relation": "观看", "confidence": 0.7},
        ],
    },
    # 5) 论坛：揽诸传说与最长寿的鲤鱼
    "aa5890d8171693c3": {
        "entities": [
            {"name": "揽诸", "type": "角色", "aliases": []},
            {"name": "强梁", "type": "角色", "aliases": []},
            {"name": "方相氏", "type": "角色", "aliases": []},
            {"name": "摄提神敦牂", "type": "角色", "aliases": []},
            {"name": "险道兽", "type": "概念", "aliases": []},
            {"name": "齐云居士", "type": "角色", "aliases": []},
            {"name": "灵物", "type": "概念", "aliases": []},
            {"name": "天道", "type": "概念", "aliases": []},
            {"name": "华南鲤", "type": "角色", "aliases": []},
            {"name": "太湖", "type": "地点", "aliases": []},
            {"name": "吴中在线", "type": "组织", "aliases": []},
            {"name": "水利环境研究所", "type": "组织", "aliases": []},
            {"name": "龙", "type": "概念", "aliases": []},
            {"name": "雷电", "type": "现象", "aliases": []},
        ],
        "relations": [
            {"src": "方相氏", "dst": "揽诸", "relation": "收服", "confidence": 0.8},
            {"src": "摄提神敦牂", "dst": "方相氏", "relation": "协助", "confidence": 0.7},
            {"src": "揽诸", "dst": "险道兽", "relation": "属于", "confidence": 0.8},
            {"src": "强梁", "dst": "雷电", "relation": "具", "confidence": 0.7},
            {"src": "华南鲤", "dst": "太湖", "relation": "捕获于", "confidence": 0.7},
            {"src": "水利环境研究所", "dst": "华南鲤", "relation": "购得", "confidence": 0.7},
            {"src": "吴中在线", "dst": "华南鲤", "relation": "报道", "confidence": 0.7},
            {"src": "华南鲤", "dst": "灵物", "relation": "是", "confidence": 0.7},
        ],
    },
    # 6) 研究日程与谜语之争 · 老妇人与老头
    "d54db23cc557d749": {
        "entities": [
            {"name": "阶梯会议室", "type": "地点", "aliases": []},
            {"name": "演说厅", "type": "地点", "aliases": []},
            {"name": "乌卢鲁运动场", "type": "地点", "aliases": []},
            {"name": "神话考古学", "type": "概念", "aliases": []},
            {"name": "仿神体", "type": "概念", "aliases": ["“仿神体”"]},
            {"name": "光子动态全息礼服", "type": "物品", "aliases": []},
            {"name": "酒馆", "type": "地点", "aliases": []},
            {"name": "老妇人", "type": "角色", "aliases": []},
            {"name": "老头", "type": "角色", "aliases": []},
            {"name": "谜语", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "老头", "dst": "酒馆", "relation": "逗留", "confidence": 0.7},
            {"src": "老妇人", "dst": "谜语", "relation": "提及", "confidence": 0.7},
            {"src": "光子动态全息礼服", "dst": "仿神体", "relation": "研究", "confidence": 0.7},
        ],
    },
    # 7) 破产公告与新公司注册 · 无名来客实战测验
    "e9066170f77a227c": {
        "entities": [
            {"name": "罗斯福路", "type": "地点", "aliases": []},
            {"name": "神秘学界月亮报", "type": "物品", "aliases": ["《神秘学界月亮报》"]},
            {"name": "五大湖传媒公司", "type": "组织", "aliases": []},
            {"name": "西奥多·杰克逊", "type": "角色", "aliases": []},
            {"name": "埃米利奥·罗伯特·亨格尔", "type": "角色", "aliases": []},
            {"name": "斯蒂芬·谢丽丹", "type": "角色", "aliases": []},
            {"name": "广播电台", "type": "组织", "aliases": []},
            {"name": "纳尔逊法", "type": "概念", "aliases": ["《纳尔逊法》"]},
            {"name": "菲尔德伍德通讯公司", "type": "组织", "aliases": []},
            {"name": "大卫·克劳伯格", "type": "角色", "aliases": []},
            {"name": "世界神秘学周报", "type": "物品", "aliases": ["《世界神秘学周报》"]},
            {"name": "卡尔娱乐出版公司", "type": "组织", "aliases": []},
            {"name": "文斯·邓恩", "type": "角色", "aliases": []},
            {"name": "美国巫师娱乐刊", "type": "物品", "aliases": ["《美国巫师娱乐刊》"]},
            {"name": "海岸联合出版公司", "type": "组织", "aliases": []},
            {"name": "休·迈达克斯", "type": "角色", "aliases": []},
            {"name": "夜间新闻", "type": "物品", "aliases": ["《夜间新闻》"]},
            {"name": "无名来客", "type": "角色", "aliases": ["无名来客Ⅰ"]},
            {"name": "实战测验", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "神秘学界月亮报", "dst": "五大湖传媒公司", "relation": "隶属", "confidence": 0.8},
            {"src": "神秘学界月亮报", "dst": "罗斯福路", "relation": "位于", "confidence": 0.8},
            {"src": "广播电台", "dst": "神秘学界月亮报", "relation": "冲击", "confidence": 0.7},
            {"src": "西奥多·杰克逊", "dst": "五大湖传媒公司", "relation": "涉及", "confidence": 0.7},
            {"src": "埃米利奥·罗伯特·亨格尔", "dst": "五大湖传媒公司", "relation": "涉及", "confidence": 0.7},
            {"src": "斯蒂芬·谢丽丹", "dst": "五大湖传媒公司", "relation": "涉及", "confidence": 0.7},
            {"src": "菲尔德伍德通讯公司", "dst": "世界神秘学周报", "relation": "经营", "confidence": 0.8},
            {"src": "卡尔娱乐出版公司", "dst": "美国巫师娱乐刊", "relation": "经营", "confidence": 0.8},
            {"src": "海岸联合出版公司", "dst": "夜间新闻", "relation": "经营", "confidence": 0.8},
            {"src": "大卫·克劳伯格", "dst": "菲尔德伍德通讯公司", "relation": "任职于", "confidence": 0.8},
            {"src": "文斯·邓恩", "dst": "卡尔娱乐出版公司", "relation": "任职于", "confidence": 0.8},
            {"src": "休·迈达克斯", "dst": "海岸联合出版公司", "relation": "任职于", "confidence": 0.8},
            {"src": "无名来客", "dst": "实战测验", "relation": "搞砸", "confidence": 0.8},
        ],
    },
    # 8) 暴雨与聚光灯之外 · 圣洛夫基金会各分部
    "d4d82a5358e2685d": {
        "entities": [
            {"name": "暴雨", "type": "现象", "aliases": ["“暴雨”"]},
            {"name": "聚光灯之外", "type": "概念", "aliases": []},
            {"name": "演职员名单", "type": "物品", "aliases": []},
            {"name": "圣洛夫基金会小队长A", "type": "角色", "aliases": ["“圣洛夫基金会小队长A”"]},
            {"name": "圣洛夫基金会", "type": "组织", "aliases": []},
            {"name": "伊娃", "type": "角色", "aliases": ["法兰西分部的伊娃"]},
            {"name": "拉", "type": "角色", "aliases": ["埃及分部的拉"]},
            {"name": "套娃", "type": "角色", "aliases": ["俄罗斯分部的套娃"]},
            {"name": "肯", "type": "角色", "aliases": ["苏格兰分部的肯"]},
            {"name": "苏格兰分部", "type": "组织", "aliases": []},
            {"name": "法兰西分部", "type": "组织", "aliases": []},
            {"name": "埃及分部", "type": "组织", "aliases": []},
            {"name": "俄罗斯分部", "type": "组织", "aliases": []},
            {"name": "舞台灯", "type": "物品", "aliases": []},
            {"name": "白色的伞", "type": "物品", "aliases": []},
            {"name": "绿色光斑", "type": "现象", "aliases": []},
        ],
        "relations": [
            {"src": "伊娃", "dst": "法兰西分部", "relation": "隶属", "confidence": 0.8},
            {"src": "拉", "dst": "埃及分部", "relation": "隶属", "confidence": 0.8},
            {"src": "套娃", "dst": "俄罗斯分部", "relation": "隶属", "confidence": 0.8},
            {"src": "肯", "dst": "苏格兰分部", "relation": "隶属", "confidence": 0.8},
            {"src": "伊娃", "dst": "圣洛夫基金会", "relation": "隶属", "confidence": 0.8},
            {"src": "拉", "dst": "圣洛夫基金会", "relation": "隶属", "confidence": 0.8},
            {"src": "套娃", "dst": "圣洛夫基金会", "relation": "隶属", "confidence": 0.8},
            {"src": "肯", "dst": "圣洛夫基金会", "relation": "隶属", "confidence": 0.8},
            {"src": "圣洛夫基金会小队长A", "dst": "圣洛夫基金会", "relation": "隶属", "confidence": 0.7},
            {"src": "白色的伞", "dst": "绿色光斑", "relation": "致", "confidence": 0.7},
        ],
    },
    # 9) 白伞与白鸽 · 方舟抉择
    "9f341a6e4fdd668c": {
        "entities": [
            {"name": "暴雨", "type": "现象", "aliases": ["“暴雨”"]},
            {"name": "白色的伞", "type": "物品", "aliases": []},
            {"name": "橘红头发白衣裳的小姑娘", "type": "角色", "aliases": []},
            {"name": "肯", "type": "角色", "aliases": ["苏格兰分部的肯"]},
            {"name": "苏格兰分部", "type": "组织", "aliases": []},
            {"name": "白鸽", "type": "组织", "aliases": ["“白鸽”"]},
            {"name": "方舟", "type": "概念", "aliases": []},
            {"name": "伊娃", "type": "角色", "aliases": ["法兰西分部的伊娃"]},
            {"name": "拉", "type": "角色", "aliases": ["埃及分部的拉"]},
            {"name": "套娃", "type": "角色", "aliases": ["俄罗斯分部的套娃"]},
            {"name": "舞台下阴暗的角落", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "白色的伞", "dst": "暴雨", "relation": "遮挡", "confidence": 0.8},
            {"src": "白色的伞", "dst": "橘红头发白衣裳的小姑娘", "relation": "留下", "confidence": 0.7},
            {"src": "肯", "dst": "苏格兰分部", "relation": "隶属", "confidence": 0.8},
            {"src": "白鸽", "dst": "方舟", "relation": "关联", "confidence": 0.7},
        ],
    },
    # 10) 战场与厨刀 · 告别芜菁
    "fb982436b0f51dcc": {
        "entities": [
            {"name": "死亡", "type": "概念", "aliases": []},
            {"name": "战场", "type": "地点", "aliases": []},
            {"name": "军官", "type": "角色", "aliases": []},
            {"name": "母亲", "type": "角色", "aliases": []},
            {"name": "厨刀", "type": "物品", "aliases": []},
            {"name": "芜菁", "type": "物品", "aliases": []},
            {"name": "碎香肠", "type": "物品", "aliases": []},
            {"name": "椅子", "type": "物品", "aliases": []},
            {"name": "客人", "type": "角色", "aliases": []},
            {"name": "和平", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "死亡", "dst": "战场", "relation": "发生于", "confidence": 0.7},
            {"src": "芜菁", "dst": "客人", "relation": "招待", "confidence": 0.7},
            {"src": "碎香肠", "dst": "芜菁", "relation": "佐", "confidence": 0.7},
        ],
    },
    # 11) 77号公路 · 魔精读书会与启明会信徒
    "ba15cee099261cf6": {
        "entities": [
            {"name": "77号公路", "type": "地点", "aliases": ["77公路"]},
            {"name": "神秘汽车旅馆", "type": "地点", "aliases": []},
            {"name": "镇公所", "type": "地点", "aliases": []},
            {"name": "魔精", "type": "概念", "aliases": []},
            {"name": "神秘学家", "type": "概念", "aliases": []},
            {"name": "魔精读书会", "type": "组织", "aliases": []},
            {"name": "民俗学读本", "type": "物品", "aliases": []},
            {"name": "搭车客们", "type": "角色", "aliases": []},
            {"name": "公路双雄", "type": "角色", "aliases": []},
            {"name": "创业者", "type": "角色", "aliases": ["“创业者”"]},
            {"name": "启明会", "type": "组织", "aliases": ["“启明会”"]},
            {"name": "信徒", "type": "角色", "aliases": []},
            {"name": "通俗小册子", "type": "物品", "aliases": []},
            {"name": "司机", "type": "角色", "aliases": []},
            {"name": "被劫持者", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "魔精读书会", "dst": "民俗学读本", "relation": "阅读", "confidence": 0.7},
            {"src": "77号公路", "dst": "神秘汽车旅馆", "relation": "关联", "confidence": 0.7},
            {"src": "启明会", "dst": "信徒", "relation": "有", "confidence": 0.8},
            {"src": "公路双雄", "dst": "创业者", "relation": "由构成", "confidence": 0.7},
            {"src": "信徒", "dst": "通俗小册子", "relation": "携带", "confidence": 0.7},
            {"src": "被劫持者", "dst": "公路双雄", "relation": "获助", "confidence": 0.7},
            {"src": "魔精", "dst": "77号公路", "relation": "出没于", "confidence": 0.7},
        ],
    },
    # 12) 论坛：祝县县志与城中公园闹鬼
    "61b47fb5c1386b35": {
        "entities": [
            {"name": "祝县县志", "type": "物品", "aliases": ["《祝县县志》"]},
            {"name": "祝县图书馆", "type": "地点", "aliases": []},
            {"name": "网速太慢了", "type": "角色", "aliases": []},
            {"name": "甜蜜蜜", "type": "角色", "aliases": []},
            {"name": "明代", "type": "时间", "aliases": []},
            {"name": "城中公园", "type": "地点", "aliases": []},
            {"name": "梅花树", "type": "物品", "aliases": []},
            {"name": "神仙府楼盘", "type": "地点", "aliases": []},
            {"name": "中心公园", "type": "地点", "aliases": []},
            {"name": "保安室", "type": "地点", "aliases": []},
            {"name": "骡子", "type": "角色", "aliases": []},
            {"name": "铜钱", "type": "物品", "aliases": []},
            {"name": "红纸", "type": "物品", "aliases": []},
            {"name": "红衣女鬼", "type": "角色", "aliases": []},
            {"name": "勤劳致富", "type": "角色", "aliases": []},
            {"name": "领导", "type": "角色", "aliases": []},
            {"name": "游客", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "梅花树", "dst": "城中公园", "relation": "位于", "confidence": 0.8},
            {"src": "梅花树", "dst": "中心公园", "relation": "位于", "confidence": 0.8},
            {"src": "神仙府楼盘", "dst": "中心公园", "relation": "邻近", "confidence": 0.7},
            {"src": "骡子", "dst": "保安室", "relation": "出现于", "confidence": 0.7},
            {"src": "红衣女鬼", "dst": "梅花树", "relation": "出现于", "confidence": 0.7},
            {"src": "祝县县志", "dst": "祝县图书馆", "relation": "藏于", "confidence": 0.8},
            {"src": "网速太慢了", "dst": "祝县县志", "relation": "提及", "confidence": 0.7},
            {"src": "甜蜜蜜", "dst": "网速太慢了", "relation": "回应", "confidence": 0.7},
            {"src": "游客", "dst": "中心公园", "relation": "到访", "confidence": 0.7},
        ],
    },
    # 13) 叩门飞匙赛报名名单 · 乌卢鲁运动会
    "b0a6050014b9b983": {
        "entities": [
            {"name": "叩门飞匙赛", "type": "事件", "aliases": []},
            {"name": "飞匙", "type": "物品", "aliases": ["“飞匙”"]},
            {"name": "彼得·托马斯", "type": "角色", "aliases": []},
            {"name": "肯特郡", "type": "地点", "aliases": []},
            {"name": "维多利亚·怀特", "type": "角色", "aliases": []},
            {"name": "约克郡", "type": "地点", "aliases": []},
            {"name": "斯坦利·史密斯", "type": "角色", "aliases": []},
            {"name": "伦敦郡", "type": "地点", "aliases": []},
            {"name": "巴黎", "type": "地点", "aliases": []},
            {"name": "1500米负重竞速", "type": "事件", "aliases": []},
            {"name": "蓝鸽铃", "type": "角色", "aliases": []},
            {"name": "查尔斯·斯科特", "type": "角色", "aliases": []},
            {"name": "圭内斯郡", "type": "地点", "aliases": []},
            {"name": "莉莉·莫里斯", "type": "角色", "aliases": []},
            {"name": "格拉斯哥郡", "type": "地点", "aliases": []},
            {"name": "苏格兰小矮马俱乐部", "type": "组织", "aliases": []},
            {"name": "小矮马", "type": "角色", "aliases": []},
            {"name": "自由祭祀", "type": "事件", "aliases": []},
            {"name": "卡洛琳·巴特利", "type": "角色", "aliases": []},
            {"name": "南约克郡", "type": "地点", "aliases": []},
            {"name": "乌卢鲁运动会", "type": "事件", "aliases": []},
            {"name": "安娜·鲍德温", "type": "角色", "aliases": []},
            {"name": "埃塞克斯郡", "type": "地点", "aliases": []},
            {"name": "笃笃骨", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "彼得·托马斯", "dst": "叩门飞匙赛", "relation": "参赛于", "confidence": 0.8},
            {"src": "维多利亚·怀特", "dst": "叩门飞匙赛", "relation": "退赛于", "confidence": 0.7},
            {"src": "斯坦利·史密斯", "dst": "叩门飞匙赛", "relation": "参赛于", "confidence": 0.7},
            {"src": "叩门飞匙赛", "dst": "巴黎", "relation": "预选于", "confidence": 0.7},
            {"src": "乌卢鲁运动会", "dst": "卡洛琳·巴特利", "relation": "含", "confidence": 0.8},
            {"src": "卡洛琳·巴特利", "dst": "安娜·鲍德温", "relation": "影响", "confidence": 0.7},
            {"src": "莉莉·莫里斯", "dst": "苏格兰小矮马俱乐部", "relation": "隶属", "confidence": 0.8},
            {"src": "蓝鸽铃", "dst": "1500米负重竞速", "relation": "退赛于", "confidence": 0.7},
            {"src": "查尔斯·斯科特", "dst": "1500米负重竞速", "relation": "改报", "confidence": 0.7},
            {"src": "笃笃骨", "dst": "自由祭祀", "relation": "参赛于", "confidence": 0.7},
            {"src": "彼得·托马斯", "dst": "肯特郡", "relation": "来自", "confidence": 0.7},
            {"src": "维多利亚·怀特", "dst": "约克郡", "relation": "来自", "confidence": 0.7},
            {"src": "斯坦利·史密斯", "dst": "伦敦郡", "relation": "来自", "confidence": 0.7},
            {"src": "莉莉·莫里斯", "dst": "格拉斯哥郡", "relation": "来自", "confidence": 0.7},
            {"src": "卡洛琳·巴特利", "dst": "南约克郡", "relation": "来自", "confidence": 0.7},
            {"src": "安娜·鲍德温", "dst": "埃塞克斯郡", "relation": "来自", "confidence": 0.7},
            {"src": "蓝鸽铃", "dst": "肯特郡", "relation": "来自", "confidence": 0.7},
            {"src": "查尔斯·斯科特", "dst": "圭内斯郡", "relation": "来自", "confidence": 0.7},
            {"src": "笃笃骨", "dst": "伦敦郡", "relation": "来自", "confidence": 0.7},
        ],
    },
    # 14) 象征动物 · 学派戒律与象征
    "903c39c313c1a9de": {
        "entities": [
            {"name": "学派", "type": "概念", "aliases": []},
            {"name": "戒律", "type": "概念", "aliases": []},
            {"name": "白色的公鸡", "type": "角色", "aliases": []},
            {"name": "象征", "type": "概念", "aliases": ["“象征”"]},
            {"name": "号角", "type": "物品", "aliases": []},
            {"name": "圆圈", "type": "概念", "aliases": []},
            {"name": "三角", "type": "概念", "aliases": []},
            {"name": "三重螺旋", "type": "概念", "aliases": []},
            {"name": "蛇", "type": "角色", "aliases": []},
            {"name": "鹰", "type": "角色", "aliases": []},
            {"name": "泥土", "type": "物品", "aliases": []},
            {"name": "花朵", "type": "物品", "aliases": []},
            {"name": "月亮", "type": "概念", "aliases": []},
            {"name": "蜡烛", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "学派", "dst": "戒律", "relation": "制定", "confidence": 0.7},
            {"src": "白色的公鸡", "dst": "戒律", "relation": "触犯", "confidence": 0.7},
            {"src": "蛇", "dst": "象征", "relation": "体现", "confidence": 0.7},
            {"src": "鹰", "dst": "象征", "relation": "体现", "confidence": 0.7},
            {"src": "圆圈", "dst": "象征", "relation": "体现", "confidence": 0.7},
            {"src": "三角", "dst": "象征", "relation": "体现", "confidence": 0.7},
            {"src": "三重螺旋", "dst": "象征", "relation": "体现", "confidence": 0.7},
            {"src": "花朵", "dst": "象征", "relation": "体现", "confidence": 0.7},
            {"src": "泥土", "dst": "象征", "relation": "体现", "confidence": 0.7},
        ],
    },
    # 15) 金伯利女郎契约物日志 · 宗教改革与天使娜娜
    "4861e76ee4b5715a": {
        "entities": [
            {"name": "金伯利女郎", "type": "角色", "aliases": []},
            {"name": "契约物", "type": "物品", "aliases": []},
            {"name": "总部", "type": "组织", "aliases": []},
            {"name": "暴雨", "type": "现象", "aliases": ["“暴雨”"]},
            {"name": "芝诺", "type": "组织", "aliases": []},
            {"name": "伊戈尔将军", "type": "角色", "aliases": ["伊戈尔"]},
            {"name": "旧金山", "type": "地点", "aliases": []},
            {"name": "当地政府机构", "type": "组织", "aliases": []},
            {"name": "特派专员", "type": "角色", "aliases": []},
            {"name": "往日的分径-天使娜娜", "type": "概念", "aliases": []},
            {"name": "天使娜娜", "type": "角色", "aliases": []},
            {"name": "发条小人", "type": "物品", "aliases": []},
            {"name": "宗教改革", "type": "物品", "aliases": []},
            {"name": "遗失的教典", "type": "物品", "aliases": []},
            {"name": "君王", "type": "角色", "aliases": []},
            {"name": "教皇", "type": "角色", "aliases": []},
            {"name": "圆桌", "type": "物品", "aliases": []},
            {"name": "天使", "type": "角色", "aliases": []},
            {"name": "天堂", "type": "概念", "aliases": []},
            {"name": "石墙", "type": "物品", "aliases": []},
            {"name": "人类", "type": "概念", "aliases": []},
            {"name": "电报", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "金伯利女郎", "dst": "契约物", "relation": "拥有", "confidence": 0.8},
            {"src": "契约物", "dst": "总部", "relation": "封存于", "confidence": 0.8},
            {"src": "暴雨", "dst": "契约物", "relation": "致遗失", "confidence": 0.8},
            {"src": "芝诺", "dst": "金伯利女郎", "relation": "搜索", "confidence": 0.8},
            {"src": "伊戈尔将军", "dst": "契约物", "relation": "寻回", "confidence": 0.8},
            {"src": "金伯利女郎", "dst": "旧金山", "relation": "出现于", "confidence": 0.8},
            {"src": "当地政府机构", "dst": "契约物", "relation": "接收", "confidence": 0.7},
            {"src": "特派专员", "dst": "金伯利女郎", "relation": "封印", "confidence": 0.7},
            {"src": "宗教改革", "dst": "君王", "relation": "提及", "confidence": 0.7},
            {"src": "宗教改革", "dst": "教皇", "relation": "提及", "confidence": 0.7},
            {"src": "宗教改革", "dst": "人类", "relation": "提及", "confidence": 0.7},
            {"src": "往日的分径-天使娜娜", "dst": "电报", "relation": "关于", "confidence": 0.7},
            {"src": "天使娜娜", "dst": "往日的分径-天使娜娜", "relation": "属于", "confidence": 0.7},
            {"src": "天使", "dst": "天堂", "relation": "引向", "confidence": 0.7},
        ],
    },
    # 16) 吼叫匣升级 · 一日女巫巡演
    "671f85730833b932": {
        "entities": [
            {"name": "匣子", "type": "物品", "aliases": []},
            {"name": "X", "type": "角色", "aliases": []},
            {"name": "吼叫匣", "type": "物品", "aliases": []},
            {"name": "蝴蝶女士", "type": "角色", "aliases": []},
            {"name": "小春雀儿", "type": "角色", "aliases": []},
            {"name": "老师", "type": "角色", "aliases": []},
            {"name": "科算中心", "type": "组织", "aliases": []},
            {"name": "乌尔里希组长", "type": "角色", "aliases": ["乌尔里希"]},
            {"name": "司辰", "type": "角色", "aliases": []},
            {"name": "自由海风号", "type": "物品", "aliases": ["“自由海风号”"]},
            {"name": "开发者", "type": "角色", "aliases": []},
            {"name": "绝对好运", "type": "概念", "aliases": []},
            {"name": "一日女巫", "type": "物品", "aliases": ["《一日女巫》"]},
            {"name": "墨西哥", "type": "地点", "aliases": []},
            {"name": "百夫长女士", "type": "角色", "aliases": ["百夫长"]},
            {"name": "好运金币", "type": "物品", "aliases": []},
            {"name": "墨西哥城", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "X", "dst": "吼叫匣", "relation": "升级", "confidence": 0.8},
            {"src": "小春雀儿", "dst": "X", "relation": "询问", "confidence": 0.7},
            {"src": "老师", "dst": "吼叫匣", "relation": "发明", "confidence": 0.8},
            {"src": "老师", "dst": "小春雀儿", "relation": "委托", "confidence": 0.7},
            {"src": "小春雀儿", "dst": "乌尔里希组长", "relation": "寄给", "confidence": 0.7},
            {"src": "小春雀儿", "dst": "科算中心", "relation": "寄给", "confidence": 0.7},
            {"src": "司辰", "dst": "自由海风号", "relation": "调查", "confidence": 0.8},
            {"src": "蝴蝶女士", "dst": "吼叫匣", "relation": "使用", "confidence": 0.7},
            {"src": "一日女巫", "dst": "墨西哥", "relation": "巡演于", "confidence": 0.8},
            {"src": "百夫长女士", "dst": "一日女巫", "relation": "关联", "confidence": 0.8},
            {"src": "绝对好运", "dst": "好运金币", "relation": "关联", "confidence": 0.7},
            {"src": "百夫长女士", "dst": "墨西哥城", "relation": "现身", "confidence": 0.7},
        ],
    },
    # 17) 球类游戏 · 模仿秀与球赛
    "1b15057d6726b9ec": {
        "entities": [
            {"name": "球类游戏", "type": "事件", "aliases": []},
            {"name": "小球儿", "type": "物品", "aliases": []},
            {"name": "球拍", "type": "物品", "aliases": []},
            {"name": "救世主", "type": "概念", "aliases": []},
            {"name": "球赛", "type": "事件", "aliases": []},
            {"name": "球队", "type": "组织", "aliases": []},
            {"name": "队服", "type": "物品", "aliases": []},
            {"name": "签名球", "type": "物品", "aliases": []},
            {"name": "椰子", "type": "物品", "aliases": []},
            {"name": "原始人", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "小球儿", "dst": "救世主", "relation": "类比", "confidence": 0.7},
            {"src": "球赛", "dst": "球队", "relation": "含", "confidence": 0.7},
            {"src": "球队", "dst": "队服", "relation": "拥有", "confidence": 0.7},
            {"src": "球队", "dst": "签名球", "relation": "拥有", "confidence": 0.7},
            {"src": "原始人", "dst": "椰子", "relation": "抛", "confidence": 0.7},
        ],
    },
    # 18) 技能数值页尾部对白 · 启明会与墨西哥卷
    "adccafd1a6ac21f8": {
        "entities": [
            {"name": "启明会", "type": "组织", "aliases": []},
            {"name": "蟑螂", "type": "角色", "aliases": []},
            {"name": "害虫", "type": "概念", "aliases": []},
            {"name": "墨西哥卷", "type": "物品", "aliases": []},
            {"name": "中餐", "type": "物品", "aliases": []},
            {"name": "面条", "type": "物品", "aliases": []},
            {"name": "街坊", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "启明会", "dst": "蟑螂", "relation": "类比", "confidence": 0.7},
            {"src": "启明会", "dst": "害虫", "relation": "类比", "confidence": 0.7},
            {"src": "中餐", "dst": "墨西哥卷", "relation": "替代", "confidence": 0.7},
            {"src": "面条", "dst": "中餐", "relation": "属于", "confidence": 0.7},
            {"src": "启明会", "dst": "街坊", "relation": "侵扰", "confidence": 0.7},
        ],
    },
    # 19) 芝诺军备学院录音复原报告 · 索姆将军与伊戈尔叛军
    "dcb65693dca83b14": {
        "entities": [
            {"name": "芝诺军备学院", "type": "组织", "aliases": []},
            {"name": "录音复原报告", "type": "物品", "aliases": []},
            {"name": "圣洛夫基金会", "type": "组织", "aliases": []},
            {"name": "司辰", "type": "角色", "aliases": []},
            {"name": "芝诺录音复原技术", "type": "概念", "aliases": ["“芝诺录音复原技术”"]},
            {"name": "神秘学共振粒子学说", "type": "概念", "aliases": []},
            {"name": "索姆将军", "type": "角色", "aliases": ["索姆"]},
            {"name": "东线", "type": "地点", "aliases": []},
            {"name": "芝诺", "type": "组织", "aliases": []},
            {"name": "伊戈尔", "type": "角色", "aliases": []},
            {"name": "叛军", "type": "组织", "aliases": []},
        ],
        "relations": [
            {"src": "录音复原报告", "dst": "圣洛夫基金会", "relation": "提交于", "confidence": 0.8},
            {"src": "司辰", "dst": "录音复原报告", "relation": "提交", "confidence": 0.8},
            {"src": "芝诺军备学院", "dst": "录音复原报告", "relation": "出具", "confidence": 0.8},
            {"src": "芝诺录音复原技术", "dst": "神秘学共振粒子学说", "relation": "基于", "confidence": 0.8},
            {"src": "索姆将军", "dst": "东线", "relation": "调遣至", "confidence": 0.7},
            {"src": "伊戈尔", "dst": "叛军", "relation": "拥有", "confidence": 0.8},
            {"src": "叛军", "dst": "芝诺", "relation": "不属于", "confidence": 0.7},
        ],
    },
}


def _norm(s: str) -> str:
    return re.sub(r"\s+", "", str(s).lower())


def validate() -> int:
    """悬空自检：关系 src/dst 必须落在块内实体 name/aliases 池。"""
    bad = 0
    for h, d in RESULTS.items():
        pool = set()
        for e in d.get("entities") or []:
            pool.add(_norm(e.get("name") or ""))
            pool |= {_norm(a) for a in (e.get("aliases") or [])}
        for r in d.get("relations") or []:
            for k in ("src", "dst"):
                if _norm(r.get(k) or "") not in pool:
                    print(f"[dangling] {h} {k}={r.get(k)}")
                    bad += 1
    return bad


def landing() -> int:
    """落地自检：实体 name/任一 alias 须是语料库正文的子串。"""
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    text_by_hash = {c["hash"]: c["text"] for c in corpus["chunks"]}
    bad = 0
    for h, d in RESULTS.items():
        text = text_by_hash.get(h, "")
        if not text:
            print(f"[landing-missing-corpus] {h}")
            bad += 1
            continue
        ntext = _norm(text)
        for e in d.get("entities") or []:
            name = e.get("name") or ""
            cands = [name] + list(e.get("aliases") or [])
            if not any(_norm(c) in ntext for c in cands):
                print(f"[landing-fail] {h} entity={name} aliases={e.get('aliases')}")
                bad += 1
    return bad


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    n = validate()
    m = landing()
    total_e = sum(len(d.get("entities") or []) for d in RESULTS.values())
    total_r = sum(len(d.get("relations") or []) for d in RESULTS.values())
    nonempty = sum(1 for d in RESULTS.values() if (d.get("entities") or d.get("relations")))
    print(f"[validate] 块 {len(RESULTS)}（含NOOP {sum(1 for d in RESULTS.values() if not (d.get('entities') or d.get('relations')))}），悬空 {n}，未落地 {m}")
    print(f"[stats] 非空块 {nonempty}，实体 {total_e}，关系 {total_r}，"
          f"空块 {sum(1 for d in RESULTS.values() if not (d.get('entities') or d.get('relations')))}")

    if n or m:
        print("[ABORT] 存在悬空或未落地，未写盘")
        return 1

    if not args.apply:
        print("[dry-run] 加 --apply 写盘")
        return 0

    for h, d in RESULTS.items():
        (CACHE / f"{h}.json").write_text(
            json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    if NOOP_ADD:
        existing = set()
        if NOOP_FILE.exists():
            existing = set(json.loads(NOOP_FILE.read_text(encoding="utf-8")))
        noop = existing | set(NOOP_ADD)
        NOOP_FILE.write_text(
            json.dumps(sorted(noop), ensure_ascii=False, indent=1), encoding="utf-8"
        )
    print(f"[apply-missing-p26] 写入 {len(RESULTS)} 条，NOOP +{len(NOOP_ADD)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
