# -*- coding: utf-8 -*-
"""未抽取剧情块补抽 · 第 13 批（backfill2 batch_03，20 块）。

块 12 (e313f5aebbab8403) 为技能/数值 UI 页（毒性病理、空气净化行动…），
非剧情文本 → 空结果，登记 NOOP。

用法：
  python scripts/apply_missing_p13.py            # 预演（悬空+落地自检）
  python scripts/apply_missing_p13.py --apply    # 写盘
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

# 数值/UI/无剧情页 → 空
NOOP_ADD = ["e313f5aebbab8403"]

RESULTS: dict[str, dict] = {
    # 1) 伦敦煤烟污染勘察与清除大使 研发记录
    "8728232b4917c973": {
        "entities": [
            {"name": "雾行者家族", "type": "组织", "aliases": []},
            {"name": "圣洛夫基金会", "type": "组织", "aliases": ["基金会"]},
            {"name": "术式刻录方法", "type": "概念", "aliases": []},
            {"name": "附魔神秘术", "type": "概念", "aliases": []},
            {"name": "伦敦煤烟污染勘察与清除大使", "type": "物品",
             "aliases": ["伦敦煤烟污染勘察与清除大使MK."]},
            {"name": "改良吸尘装置", "type": "物品", "aliases": []},
            {"name": "神秘术辅助装置", "type": "物品", "aliases": []},
            {"name": "煤烟污染清除装置", "type": "物品", "aliases": []},
            {"name": "改良版煤烟污染清除装置", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "圣洛夫基金会", "dst": "术式刻录方法", "relation": "分享", "confidence": 0.9},
            {"src": "伦敦煤烟污染勘察与清除大使", "dst": "术式刻录方法", "relation": "应用", "confidence": 0.85},
            {"src": "伦敦煤烟污染勘察与清除大使", "dst": "附魔神秘术", "relation": "使用", "confidence": 0.85},
        ],
    },
    # 2) 善后事宜：伦敦清洁空气委员会 致 基金会驻伦敦分部
    "430bd0a977db6f03": {
        "entities": [
            {"name": "伦敦清洁空气委员会", "type": "组织", "aliases": []},
            {"name": "亚瑟·福葛", "type": "角色", "aliases": []},
            {"name": "基金会驻伦敦分部", "type": "组织", "aliases": ["基金会"]},
            {"name": "伦敦煤烟污染勘察与清除大使", "type": "物品", "aliases": []},
            {"name": "乌卢鲁预选赛", "type": "事件", "aliases": ["乌卢鲁伦敦预选赛"]},
        ],
        "relations": [
            {"src": "亚瑟·福葛", "dst": "伦敦清洁空气委员会", "relation": "隶属", "confidence": 0.9},
            {"src": "伦敦清洁空气委员会", "dst": "基金会驻伦敦分部", "relation": "致信", "confidence": 0.9},
            {"src": "伦敦清洁空气委员会", "dst": "伦敦煤烟污染勘察与清除大使", "relation": "研发", "confidence": 0.85},
            {"src": "伦敦煤烟污染勘察与清除大使", "dst": "乌卢鲁预选赛", "relation": "未能解决危机", "confidence": 0.8},
        ],
    },
    # 3) 星锑项目 采买清单 / 卫星假说
    "fc8c22ca86b79bb5": {
        "entities": [
            {"name": "暴雨", "type": "事件", "aliases": []},
            {"name": "外星人", "type": "角色", "aliases": []},
            {"name": "剃刀小队", "type": "组织", "aliases": []},
            {"name": "人造卫星", "type": "物品", "aliases": []},
            {"name": "科算中心", "type": "组织", "aliases": []},
            {"name": "龙血树脂罗盘", "type": "物品", "aliases": []},
            {"name": "龙血树脂", "type": "物品", "aliases": []},
            {"name": "黑曜石晶体", "type": "物品", "aliases": []},
            {"name": "太阳能板", "type": "物品", "aliases": []},
            {"name": "阿兹特克神秘术", "type": "概念", "aliases": []},
            {"name": "波波卡特佩特火山", "type": "地点", "aliases": []},
            {"name": "星锑项目", "type": "概念", "aliases": []},
            {"name": "星锑", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "外星人", "dst": "暴雨", "relation": "跨越并输送信号", "confidence": 0.6},
            {"src": "科算中心", "dst": "人造卫星", "relation": "负责升空", "confidence": 0.85},
            {"src": "星锑项目", "dst": "龙血树脂罗盘", "relation": "采购", "confidence": 0.8},
            {"src": "龙血树脂罗盘", "dst": "龙血树脂", "relation": "由之雕刻", "confidence": 0.9},
            {"src": "黑曜石晶体", "dst": "太阳能板", "relation": "制作素材", "confidence": 0.85},
            {"src": "阿兹特克神秘术", "dst": "太阳能板", "relation": "提升效能", "confidence": 0.8},
            {"src": "波波卡特佩特火山", "dst": "黑曜石晶体", "relation": "采集", "confidence": 0.85},
        ],
    },
    # 4) 芭卡洛儿 审查 星锑 / 航海大百科
    "ed15af4e8871f358": {
        "entities": [
            {"name": "芭卡洛儿", "type": "角色", "aliases": []},
            {"name": "星锑", "type": "角色", "aliases": []},
            {"name": "船长", "type": "角色", "aliases": []},
            {"name": "摇滚海盗", "type": "组织", "aliases": []},
            {"name": "自由海风号", "type": "物品", "aliases": []},
            {"name": "啪唧匣子", "type": "物品", "aliases": []},
            {"name": "广播室", "type": "地点", "aliases": []},
            {"name": "巨齿飞鳐", "type": "角色", "aliases": ["Serres"]},
            {"name": "海蝙蝠", "type": "物品", "aliases": []},
            {"name": "航海大百科-海怪篇", "type": "物品", "aliases": ["《航海大百科-海怪篇》"]},
            {"name": "象牙", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "芭卡洛儿", "dst": "星锑", "relation": "信任", "confidence": 0.9},
            {"src": "芭卡洛儿", "dst": "船长", "relation": "接受审查", "confidence": 0.85},
            {"src": "芭卡洛儿", "dst": "自由海风号", "relation": "维护名誉", "confidence": 0.8},
            {"src": "芭卡洛儿", "dst": "啪唧匣子", "relation": "同被扔下船", "confidence": 0.7},
            {"src": "航海大百科-海怪篇", "dst": "巨齿飞鳐", "relation": "记载", "confidence": 0.9},
            {"src": "巨齿飞鳐", "dst": "象牙", "relation": "冒充", "confidence": 0.5},
        ],
    },
    # 5) 自由海风号事件报告 / 人工暴雨实验
    "f13713312f056077": {
        "entities": [
            {"name": "星锑", "type": "角色", "aliases": ["星锑研究员"]},
            {"name": "龙血树脂罗盘", "type": "物品", "aliases": []},
            {"name": "铂金通灵板", "type": "物品", "aliases": []},
            {"name": "暴雨", "type": "事件", "aliases": []},
            {"name": "自由海风号", "type": "物品", "aliases": []},
            {"name": "自由海风号事件", "type": "事件", "aliases": ["自由海风号劫持事件"]},
            {"name": "淑女格蕾丝", "type": "角色", "aliases": []},
            {"name": "重塑之手", "type": "组织", "aliases": []},
            {"name": "努库泰澳人", "type": "角色", "aliases": []},
            {"name": "司辰", "type": "角色", "aliases": []},
            {"name": "拉普拉斯", "type": "组织", "aliases": ["拉普拉斯研究员"]},
            {"name": "乌尔里希", "type": "角色", "aliases": []},
            {"name": "人工暴雨", "type": "概念", "aliases": []},
            {"name": "星锑唱片", "type": "物品", "aliases": ["星锑（代号）唱片"]},
            {"name": "时代病", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "淑女格蕾丝", "dst": "重塑之手", "relation": "隶属", "confidence": 0.9},
            {"src": "淑女格蕾丝", "dst": "自由海风号事件", "relation": "主导", "confidence": 0.9},
            {"src": "淑女格蕾丝", "dst": "努库泰澳人", "relation": "诱拐", "confidence": 0.85},
            {"src": "乌尔里希", "dst": "人工暴雨", "relation": "完成实验", "confidence": 0.85},
            {"src": "乌尔里希", "dst": "自由海风号", "relation": "于其完成", "confidence": 0.8},
            {"src": "星锑", "dst": "人工暴雨", "relation": "协助", "confidence": 0.85},
            {"src": "星锑唱片", "dst": "人工暴雨", "relation": "提供免疫", "confidence": 0.8},
            {"src": "星锑唱片", "dst": "时代病", "relation": "延缓发作", "confidence": 0.8},
            {"src": "暴雨", "dst": "星锑", "relation": "引发症候", "confidence": 0.85},
            {"src": "铂金通灵板", "dst": "暴雨", "relation": "改善无效", "confidence": 0.7},
        ],
    },
    # 6) 黑色星期四 / 送奶工与约翰 / 重塑之手公开信息
    "5dc8facd79b65b83": {
        "entities": [
            {"name": "送奶工", "type": "角色", "aliases": []},
            {"name": "黑色星期四", "type": "事件", "aliases": []},
            {"name": "约翰", "type": "角色", "aliases": []},
            {"name": "华尔街", "type": "地点", "aliases": []},
            {"name": "重塑之手", "type": "组织", "aliases": []},
            {"name": "神秘学家混血种", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "送奶工", "dst": "黑色星期四", "relation": "见证", "confidence": 0.7},
            {"src": "送奶工", "dst": "约翰", "relation": "提醒", "confidence": 0.8},
            {"src": "约翰", "dst": "华尔街", "relation": "提及", "confidence": 0.6},
            {"src": "重塑之手", "dst": "神秘学家混血种", "relation": "仇恨", "confidence": 0.85},
        ],
    },
    # 7) 暴雨症候调查记录 / 破译小组名单
    "d0bba06996a73cd2": {
        "entities": [
            {"name": "暴雨症候调查记录", "type": "物品", "aliases": []},
            {"name": "暴雨", "type": "事件", "aliases": []},
            {"name": "维也纳", "type": "地点", "aliases": []},
            {"name": "雅典", "type": "地点", "aliases": []},
            {"name": "开罗", "type": "地点", "aliases": []},
            {"name": "橄榄树", "type": "物品", "aliases": []},
            {"name": "金字塔", "type": "物品", "aliases": []},
            {"name": "战争油画", "type": "物品", "aliases": []},
            {"name": "破译小组", "type": "组织", "aliases": []},
            {"name": "乌尔里希", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "暴雨", "dst": "维也纳", "relation": "临界点为", "confidence": 0.9},
            {"src": "暴雨症候调查记录", "dst": "暴雨", "relation": "记录", "confidence": 0.9},
            {"src": "雅典", "dst": "橄榄树", "relation": "产生破坏冲动", "confidence": 0.8},
            {"src": "开罗", "dst": "金字塔", "relation": "改造工事", "confidence": 0.8},
            {"src": "破译小组", "dst": "乌尔里希", "relation": "包含", "confidence": 0.9},
        ],
    },
    # 8) 破译小组选拔名单
    "c40e8ced0eba4b40": {
        "entities": [
            {"name": "拉普拉斯", "type": "组织", "aliases": []},
            {"name": "破译小组", "type": "组织", "aliases": []},
            {"name": "道金斯", "type": "角色", "aliases": []},
            {"name": "理查德", "type": "角色", "aliases": []},
            {"name": "马修", "type": "角色", "aliases": []},
            {"name": "威廉姆斯", "type": "角色", "aliases": []},
            {"name": "维克托", "type": "角色", "aliases": []},
            {"name": "防止冷笑话发生器", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "破译小组", "dst": "拉普拉斯", "relation": "隶属", "confidence": 0.85},
            {"src": "破译小组", "dst": "道金斯", "relation": "通过", "confidence": 0.9},
            {"src": "破译小组", "dst": "理查德", "relation": "通过", "confidence": 0.9},
            {"src": "破译小组", "dst": "马修", "relation": "通过", "confidence": 0.9},
            {"src": "破译小组", "dst": "威廉姆斯", "relation": "通过", "confidence": 0.9},
            {"src": "破译小组", "dst": "维克托", "relation": "通过", "confidence": 0.9},
            {"src": "威廉姆斯", "dst": "马修", "relation": "辅佐", "confidence": 0.8},
            {"src": "防止冷笑话发生器", "dst": "道金斯", "relation": "监管", "confidence": 0.7},
        ],
    },
    # 9) 破译小组补录 / 用火安全（盗火者隐喻）
    # 注意：本块正文仅有"这次破译"，无"破译小组"字面词，故不抽该组织，
    # 关系落在明确出现的 维克托/道金斯 与 盗火者/赫利俄斯 上。
    "e1442fc8d8ebcb1f": {
        "entities": [
            {"name": "维克托", "type": "角色", "aliases": []},
            {"name": "道金斯", "type": "角色", "aliases": []},
            {"name": "阿德勒", "type": "角色", "aliases": []},
            {"name": "赫利俄斯", "type": "角色", "aliases": []},
            {"name": "盗火者", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "维克托", "dst": "道金斯", "relation": "同组禁忌", "confidence": 0.7},
            {"src": "盗火者", "dst": "赫利俄斯", "relation": "盗火", "confidence": 0.5},
        ],
    },
    # 10) 康威自动机维修 / 葬礼延期 / 斯芬克斯谜题
    "3818beff8a5d5a35": {
        "entities": [
            {"name": "康威自动机", "type": "物品", "aliases": []},
            {"name": "康威V代自动机", "type": "物品", "aliases": []},
            {"name": "暴雨", "type": "事件", "aliases": []},
            {"name": "科算中心", "type": "组织", "aliases": []},
            {"name": "游戏小子色彩版", "type": "物品", "aliases": []},
            {"name": "破译小组", "type": "组织", "aliases": []},
            {"name": "葬礼延期通告", "type": "物品", "aliases": []},
            {"name": "朵拉", "type": "角色", "aliases": []},
            {"name": "埃文斯", "type": "角色", "aliases": []},
            {"name": "盖瑞", "type": "角色", "aliases": []},
            {"name": "理查德", "type": "角色", "aliases": []},
            {"name": "文森特", "type": "角色", "aliases": []},
            {"name": "道金斯", "type": "角色", "aliases": []},
            {"name": "维克托", "type": "角色", "aliases": []},
            {"name": "玛格丽特", "type": "角色", "aliases": []},
            {"name": "路易", "type": "角色", "aliases": []},
            {"name": "斯芬克斯", "type": "角色", "aliases": []},
            {"name": "俄狄浦斯", "type": "角色", "aliases": []},
            {"name": "埃及", "type": "地点", "aliases": []},
            {"name": "希腊", "type": "地点", "aliases": []},
            {"name": "人", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "康威V代自动机", "dst": "科算中心", "relation": "隶属", "confidence": 0.9},
            {"src": "暴雨", "dst": "康威自动机", "relation": "遗失于", "confidence": 0.85},
            {"src": "科算中心", "dst": "破译小组", "relation": "支持", "confidence": 0.8},
            {"src": "葬礼延期通告", "dst": "暴雨", "relation": "源于", "confidence": 0.8},
            {"src": "葬礼延期通告", "dst": "理查德", "relation": "记载伤亡", "confidence": 0.8},
            {"src": "葬礼延期通告", "dst": "道金斯", "relation": "记载伤亡", "confidence": 0.8},
            {"src": "葬礼延期通告", "dst": "维克托", "relation": "记载伤亡", "confidence": 0.8},
            {"src": "俄狄浦斯", "dst": "斯芬克斯", "relation": "击败", "confidence": 0.85},
            {"src": "斯芬克斯", "dst": "埃及", "relation": "象征于", "confidence": 0.8},
            {"src": "斯芬克斯", "dst": "希腊", "relation": "归入隐秘", "confidence": 0.8},
        ],
    },
    # 11) 意识唤醒者临床 / 加密记录#832（芝诺-司辰-重塑之手）
    "e258b888c8d9a75a": {
        "entities": [
            {"name": "意识唤醒者", "type": "角色", "aliases": []},
            {"name": "外装躯壳", "type": "物品", "aliases": []},
            {"name": "加密记录#832", "type": "物品", "aliases": []},
            {"name": "芝诺", "type": "角色", "aliases": []},
            {"name": "司辰", "type": "角色", "aliases": []},
            {"name": "科算中心", "type": "组织", "aliases": []},
            {"name": "重塑之手", "type": "组织", "aliases": []},
            {"name": "通讯专线", "type": "物品", "aliases": []},
            {"name": "诅咒", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "意识唤醒者", "dst": "外装躯壳", "relation": "拥有", "confidence": 0.9},
            {"src": "意识唤醒者", "dst": "诅咒", "relation": "克服", "confidence": 0.8},
            {"src": "芝诺", "dst": "司辰", "relation": "希望建立通讯", "confidence": 0.85},
            {"src": "芝诺", "dst": "重塑之手", "relation": "拟军事行动", "confidence": 0.6},
            {"src": "科算中心", "dst": "芝诺", "relation": "调查目的", "confidence": 0.8},
            {"src": "加密记录#832", "dst": "芝诺", "relation": "涉及", "confidence": 0.8},
            {"src": "通讯专线", "dst": "司辰", "relation": "连接", "confidence": 0.8},
        ],
    },
    # 12) e313f5aebbab8403 —— 技能/数值 UI 页，无剧情 → 空
    "e313f5aebbab8403": {
        "entities": [],
        "relations": [],
    },
    # 13) 自救与拯救 / 上帝之手
    "7245fb5ac42b3d0f": {
        "entities": [
            {"name": "自救与拯救", "type": "概念", "aliases": []},
            {"name": "拯救", "type": "概念", "aliases": []},
            {"name": "布宜诺斯艾利斯", "type": "地点", "aliases": []},
            {"name": "上帝之手", "type": "概念", "aliases": []},
            {"name": "迷茫与躁动的瘟疫", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "自救与拯救", "dst": "拯救", "relation": "包含", "confidence": 0.8},
            {"src": "布宜诺斯艾利斯", "dst": "上帝之手", "relation": "提及", "confidence": 0.7},
        ],
    },
    # 14) 波义耳 不可能瓶 / 往日的分径 / 感谢墙
    "4141e49d6dd546f1": {
        "entities": [
            {"name": "波义耳", "type": "角色", "aliases": []},
            {"name": "神秘术", "type": "概念", "aliases": []},
            {"name": "烧瓶", "type": "物品", "aliases": []},
            {"name": "不可能瓶", "type": "物品", "aliases": []},
            {"name": "皇家学会", "type": "组织", "aliases": []},
            {"name": "德洛斯医生", "type": "角色", "aliases": ["往日的分径-德洛斯医生"]},
            {"name": "邓肯先生", "type": "角色", "aliases": ["往日的分径-邓肯先生"]},
            {"name": "扳手", "type": "物品", "aliases": []},
            {"name": "感谢墙", "type": "物品", "aliases": []},
            {"name": "大理石先生", "type": "角色", "aliases": []},
            {"name": "荣军院", "type": "组织", "aliases": []},
            {"name": "大理石椅子", "type": "物品", "aliases": []},
            {"name": "天使娜娜", "type": "角色", "aliases": ["往日的分径-天使娜娜"]},
            {"name": "隐秘组织", "type": "组织", "aliases": []},
            {"name": "绷带", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "波义耳", "dst": "神秘术", "relation": "使用", "confidence": 0.9},
            {"src": "波义耳", "dst": "烧瓶", "relation": "制作", "confidence": 0.85},
            {"src": "波义耳", "dst": "不可能瓶", "relation": "创造", "confidence": 0.7},
            {"src": "波义耳", "dst": "皇家学会", "relation": "捐赠", "confidence": 0.85},
            {"src": "德洛斯医生", "dst": "绷带", "relation": "关联", "confidence": 0.7},
            {"src": "邓肯先生", "dst": "扳手", "relation": "关联", "confidence": 0.7},
            {"src": "大理石先生", "dst": "荣军院", "relation": "捐款", "confidence": 0.9},
            {"src": "大理石先生", "dst": "大理石椅子", "relation": "捐赠", "confidence": 0.8},
            {"src": "感谢墙", "dst": "隐秘组织", "relation": "罗列成员", "confidence": 0.8},
        ],
    },
    # 15) 启明会问话记录 / 牌桌礼仪
    "f1a1bcd05eb42ac0": {
        "entities": [
            {"name": "天使娜娜", "type": "角色", "aliases": []},
            {"name": "旧金山", "type": "地点", "aliases": []},
            {"name": "启明会", "type": "组织", "aliases": []},
            {"name": "重塑之手", "type": "组织", "aliases": []},
            {"name": "阿尔卡纳", "type": "角色", "aliases": []},
            {"name": "基金会", "type": "组织", "aliases": []},
            {"name": "勿忘我", "type": "角色", "aliases": []},
            {"name": "阿派朗学派", "type": "组织", "aliases": []},
            {"name": "苏菲亚", "type": "角色", "aliases": []},
            {"name": "传道者", "type": "角色", "aliases": []},
            {"name": "牌桌礼仪", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "启明会", "dst": "重塑之手", "relation": "等同", "confidence": 0.85},
            {"src": "基金会", "dst": "启明会", "relation": "收容成员", "confidence": 0.8},
            {"src": "阿尔卡纳", "dst": "启明会", "relation": "被信奉", "confidence": 0.7},
            {"src": "苏菲亚", "dst": "阿派朗学派", "relation": "隶属", "confidence": 0.7},
            {"src": "勿忘我", "dst": "启明会", "relation": "可能为领导人", "confidence": 0.5},
        ],
    },
    # 16) 十四行诗的笔记本 / 皮拉苏皮
    "472bf9f62d05f382": {
        "entities": [
            {"name": "十四行诗的笔记本", "type": "物品", "aliases": []},
            {"name": "皮拉苏皮", "type": "物品", "aliases": []},
            {"name": "独角皮拉苏皮", "type": "物品", "aliases": []},
            {"name": "菲奥娜", "type": "角色", "aliases": []},
            {"name": "角质层", "type": "物品", "aliases": []},
            {"name": "棱柱层", "type": "物品", "aliases": []},
            {"name": "珍珠层", "type": "物品", "aliases": []},
            {"name": "二号食堂", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "十四行诗的笔记本", "dst": "皮拉苏皮", "relation": "记载", "confidence": 0.9},
            {"src": "独角皮拉苏皮", "dst": "皮拉苏皮", "relation": "即", "confidence": 0.9},
            {"src": "菲奥娜", "dst": "皮拉苏皮", "relation": "提及", "confidence": 0.6},
            {"src": "独角皮拉苏皮", "dst": "角质层", "relation": "具有", "confidence": 0.85},
            {"src": "独角皮拉苏皮", "dst": "棱柱层", "relation": "具有", "confidence": 0.85},
            {"src": "独角皮拉苏皮", "dst": "珍珠层", "relation": "具有", "confidence": 0.85},
        ],
    },
    # 17) 维廉W5战略剃刀 使用须知 / 对峙的第三方
    "e869c95200ef0a26": {
        "entities": [
            {"name": "维廉W5战略剃刀（增强型）", "type": "物品", "aliases": []},
            {"name": "基金会特别行动队", "type": "组织", "aliases": []},
            {"name": "拉普拉斯科算中心", "type": "组织", "aliases": ["拉普拉斯"]},
            {"name": "对峙的第三方", "type": "事件", "aliases": []},
            {"name": "海豚", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "维廉W5战略剃刀（增强型）", "dst": "基金会特别行动队", "relation": "配装", "confidence": 0.9},
            {"src": "维廉W5战略剃刀（增强型）", "dst": "拉普拉斯科算中心", "relation": "研发", "confidence": 0.9},
            {"src": "对峙的第三方", "dst": "海豚", "relation": "加入", "confidence": 0.7},
        ],
    },
    # 18) 脑叶白质切除术史 / 福柯讨论
    "d036f7fff4d2972f": {
        "entities": [
            {"name": "安东尼奥", "type": "角色", "aliases": ["安东尼奥教授"]},
            {"name": "脑叶白质切除术", "type": "概念", "aliases": []},
            {"name": "脑白质切除器", "type": "物品", "aliases": []},
            {"name": "弗里曼", "type": "角色", "aliases": []},
            {"name": "冰锥疗法", "type": "概念", "aliases": []},
            {"name": "瓦西里·加雅诺夫斯基", "type": "角色", "aliases": []},
            {"name": "苏联政府", "type": "组织", "aliases": []},
            {"name": "美国", "type": "地点", "aliases": []},
            {"name": "维尔汀", "type": "角色", "aliases": []},
            {"name": "福柯", "type": "角色", "aliases": []},
            {"name": "十四行诗", "type": "角色", "aliases": []},
            {"name": "第一防线学校", "type": "组织", "aliases": []},
            {"name": "司辰", "type": "角色", "aliases": []},
            {"name": "葡萄牙", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "安东尼奥", "dst": "脑叶白质切除术", "relation": "实施首例", "confidence": 0.9},
            {"src": "弗里曼", "dst": "冰锥疗法", "relation": "改进发明", "confidence": 0.9},
            {"src": "冰锥疗法", "dst": "脑叶白质切除术", "relation": "即", "confidence": 0.9},
            {"src": "瓦西里·加雅诺夫斯基", "dst": "苏联政府", "relation": "建议", "confidence": 0.85},
            {"src": "苏联政府", "dst": "脑叶白质切除术", "relation": "禁止", "confidence": 0.9},
            {"src": "维尔汀", "dst": "十四行诗", "relation": "询问", "confidence": 0.85},
            {"src": "维尔汀", "dst": "司辰", "relation": "被称作", "confidence": 0.9},
            {"src": "十四行诗", "dst": "福柯", "relation": "讨论", "confidence": 0.8},
            {"src": "十四行诗", "dst": "第一防线学校", "relation": "就读", "confidence": 0.7},
        ],
    },
    # 19) 硬币女孩儿传说 / 墨西哥城先驱周报 外交官
    "7798911715570dbf": {
        "entities": [
            {"name": "加里波第广场", "type": "地点", "aliases": []},
            {"name": "索卡洛广场", "type": "地点", "aliases": []},
            {"name": "索奇米尔科", "type": "地点", "aliases": []},
            {"name": "硬币女孩儿", "type": "角色", "aliases": []},
            {"name": "墨西哥城", "type": "地点", "aliases": []},
            {"name": "布卡雷利街", "type": "地点", "aliases": []},
            {"name": "诸灵节", "type": "事件", "aliases": []},
            {"name": "阿兹特克神话", "type": "概念", "aliases": []},
            {"name": "太阳石", "type": "物品", "aliases": []},
            {"name": "圣卡洛斯学院", "type": "组织", "aliases": []},
            {"name": "公共壁画", "type": "物品", "aliases": []},
            {"name": "拉梅塞德市场", "type": "地点", "aliases": []},
            {"name": "墨西哥城先驱周报", "type": "物品", "aliases": ["《墨西哥城先驱周报》"]},
            {"name": "万寿菊", "type": "物品", "aliases": []},
            {"name": "糖果头骨", "type": "物品", "aliases": []},
            {"name": "版画", "type": "物品", "aliases": []},
            {"name": "外交官", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "硬币女孩儿", "dst": "索卡洛广场", "relation": "出现", "confidence": 0.7},
            {"src": "硬币女孩儿", "dst": "索奇米尔科", "relation": "停留", "confidence": 0.7},
            {"src": "外交官", "dst": "墨西哥城", "relation": "抵达", "confidence": 0.9},
            {"src": "外交官", "dst": "索卡洛广场", "relation": "停留", "confidence": 0.8},
            {"src": "外交官", "dst": "布卡雷利街", "relation": "途经", "confidence": 0.8},
            {"src": "外交官", "dst": "阿兹特克神话", "relation": "了解", "confidence": 0.8},
            {"src": "外交官", "dst": "太阳石", "relation": "了解", "confidence": 0.8},
            {"src": "外交官", "dst": "圣卡洛斯学院", "relation": "造访", "confidence": 0.85},
            {"src": "外交官", "dst": "拉梅塞德市场", "relation": "驻足", "confidence": 0.8},
            {"src": "万寿菊", "dst": "诸灵节", "relation": "为节陈列", "confidence": 0.8},
            {"src": "墨西哥城先驱周报", "dst": "外交官", "relation": "报道", "confidence": 0.8},
        ],
    },
    # 20) 骷髅偶人 / 空脑袋与虚构集 / 神秘学藏品管理部
    "a80e6471b3bd94cc": {
        "entities": [
            {"name": "骷髅偶人", "type": "物品", "aliases": []},
            {"name": "外交官", "type": "角色", "aliases": []},
            {"name": "菲茨威廉", "type": "角色", "aliases": ["记者菲茨威廉"]},
            {"name": "墨西哥城", "type": "地点", "aliases": []},
            {"name": "空脑袋", "type": "角色", "aliases": []},
            {"name": "虚构集", "type": "角色", "aliases": []},
            {"name": "莱瑟姆", "type": "角色", "aliases": ["莱瑟姆小姐"]},
            {"name": "神秘学藏品管理部", "type": "组织", "aliases": []},
            {"name": "清洁卷轴", "type": "物品", "aliases": []},
            {"name": "第三版清理咒语", "type": "物品", "aliases": []},
            {"name": "暴雨", "type": "事件", "aliases": []},
            {"name": "司辰", "type": "角色", "aliases": []},
            {"name": "基金会", "type": "组织", "aliases": []},
        ],
        "relations": [
            {"src": "菲茨威廉", "dst": "外交官", "relation": "报道", "confidence": 0.85},
            {"src": "空脑袋", "dst": "神秘学藏品管理部", "relation": "隶属", "confidence": 0.85},
            {"src": "空脑袋", "dst": "虚构集", "relation": "指导", "confidence": 0.8},
            {"src": "虚构集", "dst": "莱瑟姆", "relation": "对话", "confidence": 0.8},
            {"src": "虚构集", "dst": "司辰", "relation": "被推荐", "confidence": 0.85},
            {"src": "虚构集", "dst": "墨西哥城", "relation": "想去采风", "confidence": 0.8},
            {"src": "神秘学藏品管理部", "dst": "清洁卷轴", "relation": "曾使用", "confidence": 0.8},
            {"src": "神秘学藏品管理部", "dst": "第三版清理咒语", "relation": "使用", "confidence": 0.85},
            {"src": "暴雨", "dst": "神秘学藏品管理部", "relation": "影响", "confidence": 0.8},
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
    print(f"[validate] 块 {len(RESULTS)}，悬空 {n}，未落地 {m}")
    print(f"[stats] 实体 {total_e}，关系 {total_r}，"
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
        noop = set(json.loads(NOOP_FILE.read_text(encoding="utf-8")))
        noop |= set(NOOP_ADD)
        NOOP_FILE.write_text(
            json.dumps(sorted(noop), ensure_ascii=False, indent=1), encoding="utf-8"
        )
    print(f"[apply-missing-p13] 写入 {len(RESULTS)} 条，NOOP +{len(NOOP_ADD)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
