# -*- coding: utf-8 -*-
"""未抽取剧情块补抽 · 第 20 批（backfill2 batch_10，20 块）。

用法：
  python scripts/apply_missing_p20.py            # 预演（悬空+落地自检）
  python scripts/apply_missing_p20.py --apply    # 写盘
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

# 本批 20 块均为带剧情正文，无纯数值/UI/无剧情页 → 无 NOOP。
NOOP_ADD: list[str] = []

RESULTS: dict[str, dict] = {
    # 1) 乌卢鲁运动会珍藏影集 · 萨曼莎·格林/苏菲·罗杰斯/本杰明·斯通与水怪赛事
    "8f44cd5e0756db67": {
        "entities": [
            {"name": "神秘学家", "type": "概念", "aliases": []},
            {"name": "乌卢鲁岩地", "type": "地点", "aliases": []},
            {"name": "乌卢鲁运动会珍藏影集", "type": "物品", "aliases": ["《乌卢鲁运动会珍藏影集》"]},
            {"name": "萨曼莎·格林", "type": "角色", "aliases": []},
            {"name": "500米水怪障碍赛", "type": "事件", "aliases": ["“500米水怪障碍赛”"]},
            {"name": "水怪", "type": "角色", "aliases": []},
            {"name": "苏菲·罗杰斯", "type": "角色", "aliases": []},
            {"name": "咒语对决", "type": "事件", "aliases": ["“咒语对决”"]},
            {"name": "浮空术", "type": "概念", "aliases": []},
            {"name": "隔空取物", "type": "概念", "aliases": []},
            {"name": "本杰明·斯通", "type": "角色", "aliases": []},
            {"name": "盛装骑术团体赛", "type": "事件", "aliases": []},
            {"name": "海洋马戏团", "type": "组织", "aliases": ["“海洋马戏团”"]},
            {"name": "袋鼠游骑兵", "type": "组织", "aliases": ["“袋鼠游骑兵”"]},
            {"name": "海马", "type": "角色", "aliases": []},
            {"name": "米娅", "type": "角色", "aliases": []},
            {"name": "轮回者", "type": "概念", "aliases": ["“轮回者”"]},
            {"name": "名人堂", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "萨曼莎·格林", "dst": "500米水怪障碍赛", "relation": "夺得", "confidence": 0.8},
            {"src": "萨曼莎·格林", "dst": "水怪", "relation": "驾驶", "confidence": 0.8},
            {"src": "苏菲·罗杰斯", "dst": "咒语对决", "relation": "参与", "confidence": 0.7},
            {"src": "苏菲·罗杰斯", "dst": "名人堂", "relation": "步入", "confidence": 0.7},
            {"src": "苏菲·罗杰斯", "dst": "浮空术", "relation": "施展", "confidence": 0.7},
            {"src": "苏菲·罗杰斯", "dst": "隔空取物", "relation": "施展", "confidence": 0.7},
            {"src": "本杰明·斯通", "dst": "海洋马戏团", "relation": "带队", "confidence": 0.8},
            {"src": "海洋马戏团", "dst": "盛装骑术团体赛", "relation": "参与", "confidence": 0.7},
            {"src": "海洋马戏团", "dst": "袋鼠游骑兵", "relation": "颠覆", "confidence": 0.7},
            {"src": "海洋马戏团", "dst": "海马", "relation": "配合", "confidence": 0.7},
            {"src": "乌卢鲁运动会珍藏影集", "dst": "萨曼莎·格林", "relation": "收录", "confidence": 0.8},
            {"src": "乌卢鲁运动会珍藏影集", "dst": "乌卢鲁岩地", "relation": "关于", "confidence": 0.7},
            {"src": "浮空术", "dst": "隔空取物", "relation": "配合", "confidence": 0.7},
        ],
    },
    # 2) 盗火者传说 · 康威V代自动机（生命游戏V）与拉普拉斯
    "83c8914ab4ee5802": {
        "entities": [
            {"name": "盗火者", "type": "组织", "aliases": []},
            {"name": "普罗米修斯", "type": "角色", "aliases": []},
            {"name": "腔棘鱼", "type": "角色", "aliases": []},
            {"name": "混沌", "type": "概念", "aliases": []},
            {"name": "神秘学", "type": "概念", "aliases": []},
            {"name": "康威V代自动机", "type": "物品", "aliases": ["生命游戏V"]},
            {"name": "拉普拉斯", "type": "组织", "aliases": []},
            {"name": "科学", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "盗火者", "dst": "神秘学", "relation": "回归", "confidence": 0.7},
            {"src": "盗火者", "dst": "混沌", "relation": "回归", "confidence": 0.7},
            {"src": "盗火者", "dst": "科学", "relation": "抛弃", "confidence": 0.7},
            {"src": "康威V代自动机", "dst": "拉普拉斯", "relation": "流行于", "confidence": 0.7},
            {"src": "康威V代自动机", "dst": "生命游戏V", "relation": "又名", "confidence": 0.9},
        ],
    },
    # 3) 绳结传统 · 格尔迪奥斯之结、奇普、印加人与基因排序
    "2089b22ed779ec9d": {
        "entities": [
            {"name": "绳结", "type": "物品", "aliases": []},
            {"name": "格尔迪奥斯之结", "type": "概念", "aliases": []},
            {"name": "奇普", "type": "概念", "aliases": ["“奇普”"]},
            {"name": "印加人", "type": "概念", "aliases": []},
            {"name": "莎士比亚", "type": "角色", "aliases": []},
            {"name": "基因排序", "type": "概念", "aliases": []},
            {"name": "相变", "type": "概念", "aliases": []},
            {"name": "荧光屏", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "印加人", "dst": "奇普", "relation": "称作", "confidence": 0.8},
            {"src": "奇普", "dst": "绳结", "relation": "指代", "confidence": 0.8},
            {"src": "格尔迪奥斯之结", "dst": "绳结", "relation": "是", "confidence": 0.8},
            {"src": "基因排序", "dst": "相变", "relation": "并列", "confidence": 0.6},
        ],
    },
    # 4) 苏芙比辞别信 · 埃尔多拉多/提神魔药与定期调令（伊戈尔调往芝诺巴西支部）
    "bcdc084f9e52bff1": {
        "entities": [
            {"name": "镇纸", "type": "物品", "aliases": []},
            {"name": "我出门一趟！", "type": "物品", "aliases": ["《我出门一趟！》"]},
            {"name": "苏芙比", "type": "角色", "aliases": []},
            {"name": "莫桑", "type": "角色", "aliases": ["莫桑老师"]},
            {"name": "维尔汀", "type": "角色", "aliases": []},
            {"name": "埃尔多拉多", "type": "地点", "aliases": ["黄金之国"]},
            {"name": "提神魔药", "type": "物品", "aliases": []},
            {"name": "咖啡", "type": "物品", "aliases": []},
            {"name": "黄金", "type": "物品", "aliases": []},
            {"name": "自动咖啡滴水兽", "type": "物品", "aliases": []},
            {"name": "提神药剂", "type": "物品", "aliases": []},
            {"name": "乌龟", "type": "角色", "aliases": []},
            {"name": "定期调令", "type": "物品", "aliases": []},
            {"name": "德克萨斯基地", "type": "地点", "aliases": []},
            {"name": "伊戈尔", "type": "角色", "aliases": ["伊戈尔同志"]},
            {"name": "芝诺巴西支部", "type": "组织", "aliases": []},
            {"name": "卡洛斯将军", "type": "角色", "aliases": []},
            {"name": "人类和平安全理事会", "type": "组织", "aliases": []},
            {"name": "淑女的原则", "type": "物品", "aliases": ["《淑女的原则》"]},
            {"name": "移动小岛", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "苏芙比", "dst": "莫桑", "relation": "提及", "confidence": 0.8},
            {"src": "苏芙比", "dst": "维尔汀", "relation": "同行", "confidence": 0.7},
            {"src": "苏芙比", "dst": "埃尔多拉多", "relation": "前往", "confidence": 0.8},
            {"src": "维尔汀", "dst": "埃尔多拉多", "relation": "前往", "confidence": 0.8},
            {"src": "提神魔药", "dst": "咖啡", "relation": "含", "confidence": 0.7},
            {"src": "提神魔药", "dst": "黄金", "relation": "含", "confidence": 0.7},
            {"src": "自动咖啡滴水兽", "dst": "咖啡", "relation": "制取", "confidence": 0.8},
            {"src": "苏芙比", "dst": "提神魔药", "relation": "调制", "confidence": 0.7},
            {"src": "乌龟", "dst": "苏芙比", "relation": "象征", "confidence": 0.6},
            {"src": "伊戈尔", "dst": "芝诺巴西支部", "relation": "调往", "confidence": 0.9},
            {"src": "伊戈尔", "dst": "卡洛斯将军", "relation": "接任", "confidence": 0.9},
            {"src": "定期调令", "dst": "人类和平安全理事会", "relation": "获批准", "confidence": 0.8},
            {"src": "定期调令", "dst": "德克萨斯基地", "relation": "放弃", "confidence": 0.8},
            {"src": "定期调令", "dst": "伊戈尔", "relation": "提及", "confidence": 0.8},
            {"src": "移动小岛", "dst": "苏芙比", "relation": "身处", "confidence": 0.7},
            {"src": "淑女的原则", "dst": "苏芙比", "relation": "约束", "confidence": 0.7},
        ],
    },
    # 5) 行动报告清单 · 阿派朗学派/芝诺/阿尔卡纳、APPLeⅢ、蓝手帕、箱中
    "b4a767a428c4a27e": {
        "entities": [
            {"name": "阿派朗学派", "type": "组织", "aliases": []},
            {"name": "芝诺", "type": "组织", "aliases": []},
            {"name": "阿尔卡纳", "type": "角色", "aliases": []},
            {"name": "APPLeⅢ", "type": "物品", "aliases": ["“APPLeⅢ”"]},
            {"name": "绿湖营地", "type": "地点", "aliases": []},
            {"name": "洁西卡", "type": "角色", "aliases": []},
            {"name": "77号公路", "type": "地点", "aliases": []},
            {"name": "蓝手帕旅馆", "type": "地点", "aliases": []},
            {"name": "蓝手帕", "type": "角色", "aliases": []},
            {"name": "箱中", "type": "组织", "aliases": []},
            {"name": "神秘学意识体", "type": "概念", "aliases": []},
            {"name": "红腹锯脂鲤", "type": "概念", "aliases": []},
            {"name": "金手指", "type": "角色", "aliases": ["“金手指”"]},
        ],
        "relations": [
            {"src": "阿派朗学派", "dst": "芝诺", "relation": "联合行动", "confidence": 0.8},
            {"src": "芝诺", "dst": "阿尔卡纳", "relation": "击毙", "confidence": 0.7},
            {"src": "洁西卡", "dst": "绿湖营地", "relation": "涉及", "confidence": 0.7},
            {"src": "蓝手帕", "dst": "蓝手帕旅馆", "relation": "涉及", "confidence": 0.7},
            {"src": "神秘学意识体", "dst": "箱中", "relation": "置入", "confidence": 0.8},
        ],
    },
    # 6) UTTU 访谈准则 · 加密记录#5225 与数羊羔小姐回避暴雨
    "6dd4d5e4a97c77e7": {
        "entities": [
            {"name": "宗教支派", "type": "组织", "aliases": []},
            {"name": "外来势力", "type": "组织", "aliases": []},
            {"name": "天使", "type": "角色", "aliases": []},
            {"name": "绿裙小姑娘", "type": "角色", "aliases": []},
            {"name": "老兵", "type": "角色", "aliases": []},
            {"name": "帮派安全屋", "type": "地点", "aliases": []},
            {"name": "蓄水缸", "type": "物品", "aliases": []},
            {"name": "访谈准则", "type": "概念", "aliases": []},
            {"name": "加密记录#5225", "type": "物品", "aliases": []},
            {"name": "数羊羔小姐", "type": "角色", "aliases": []},
            {"name": "基金会", "type": "组织", "aliases": []},
            {"name": "UTTU", "type": "组织", "aliases": []},
            {"name": "暴雨", "type": "现象", "aliases": ["“暴雨”"]},
        ],
        "relations": [
            {"src": "宗教支派", "dst": "外来势力", "relation": "沦为附庸", "confidence": 0.8},
            {"src": "数羊羔小姐", "dst": "基金会", "relation": "接受采访", "confidence": 0.7},
            {"src": "数羊羔小姐", "dst": "UTTU", "relation": "接待", "confidence": 0.7},
            {"src": "UTTU", "dst": "暴雨", "relation": "回避", "confidence": 0.7},
            {"src": "数羊羔小姐", "dst": "暴雨", "relation": "回避", "confidence": 0.7},
            {"src": "加密记录#5225", "dst": "数羊羔小姐", "relation": "记录", "confidence": 0.8},
            {"src": "蓄水缸", "dst": "帮派安全屋", "relation": "藏有钥匙", "confidence": 0.7},
        ],
    },
    # 7) 数羊羔小姐赴德克萨斯/77号公路 · 玛蒂尔达、司辰、兀尔德、天使娜娜与无形学院
    "20e0bdd80b20d79a": {
        "entities": [
            {"name": "UTTU", "type": "组织", "aliases": []},
            {"name": "数羊羔小姐", "type": "角色", "aliases": []},
            {"name": "德克萨斯", "type": "地点", "aliases": []},
            {"name": "77号公路", "type": "地点", "aliases": []},
            {"name": "玛蒂尔达", "type": "角色", "aliases": []},
            {"name": "司辰", "type": "角色", "aliases": []},
            {"name": "兀尔德", "type": "角色", "aliases": []},
            {"name": "巴西圣保罗荣军院", "type": "地点", "aliases": []},
            {"name": "天使娜娜", "type": "角色", "aliases": []},
            {"name": "塞壬之歌", "type": "概念", "aliases": []},
            {"name": "无形学院", "type": "组织", "aliases": []},
            {"name": "皇家学会", "type": "组织", "aliases": []},
            {"name": "波义耳", "type": "角色", "aliases": ["罗伯特·波义耳"]},
            {"name": "波义耳定律", "type": "概念", "aliases": []},
            {"name": "你所不知的无形学院逸闻——波义耳的不可能瓶", "type": "物品",
             "aliases": ["《你所不知的无形学院逸闻——波义耳的不可能瓶》"]},
            {"name": "止痛药", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "玛蒂尔达", "dst": "77号公路", "relation": "前往", "confidence": 0.8},
            {"src": "司辰", "dst": "77号公路", "relation": "接管", "confidence": 0.7},
            {"src": "司辰", "dst": "兀尔德", "relation": "获悉", "confidence": 0.7},
            {"src": "兀尔德", "dst": "巴西圣保罗荣军院", "relation": "身处", "confidence": 0.8},
            {"src": "数羊羔小姐", "dst": "德克萨斯", "relation": "前往", "confidence": 0.7},
            {"src": "数羊羔小姐", "dst": "77号公路", "relation": "前往", "confidence": 0.7},
            {"src": "天使娜娜", "dst": "塞壬之歌", "relation": "吟唱", "confidence": 0.8},
            {"src": "天使娜娜", "dst": "止痛药", "relation": "令人忘却", "confidence": 0.7},
            {"src": "皇家学会", "dst": "无形学院", "relation": "前身是", "confidence": 0.8},
            {"src": "波义耳", "dst": "无形学院", "relation": "属于", "confidence": 0.8},
            {"src": "波义耳", "dst": "波义耳定律", "relation": "提出", "confidence": 0.8},
            {"src": "你所不知的无形学院逸闻——波义耳的不可能瓶", "dst": "波义耳", "relation": "关于", "confidence": 0.8},
            {"src": "你所不知的无形学院逸闻——波义耳的不可能瓶", "dst": "无形学院", "relation": "关于", "confidence": 0.7},
        ],
    },
    # 8) 神秘学军事图鉴：单兵载具篇 · Su-01ве（女巫）、芝诺军备学院与基金会药事名册
    "3f039b439ffe85fb": {
        "entities": [
            {"name": "神秘学军事图鉴：单兵载具篇", "type": "物品", "aliases": ["《神秘学军事图鉴：单兵载具篇》"]},
            {"name": "Su-01ве（女巫）", "type": "物品", "aliases": []},
            {"name": "战斗飞行扫帚", "type": "物品", "aliases": []},
            {"name": "苏霍伊设计局", "type": "组织", "aliases": []},
            {"name": "芝诺军备学院", "type": "组织", "aliases": []},
            {"name": "芝诺", "type": "组织", "aliases": []},
            {"name": "基金会药事管理名册", "type": "物品", "aliases": ["《基金会药事管理名册》"]},
            {"name": "苦哑巴药剂", "type": "物品", "aliases": []},
            {"name": "圣洛夫基金会", "type": "组织", "aliases": []},
            {"name": "基金会神秘学制剂持有许可", "type": "物品", "aliases": ["《基金会神秘学制剂持有许可》"]},
            {"name": "神秘学探测器", "type": "物品", "aliases": []},
            {"name": "ST-30-1 30mm神秘术瞬发装置", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "神秘学军事图鉴：单兵载具篇", "dst": "Su-01ве（女巫）", "relation": "记载", "confidence": 0.8},
            {"src": "Su-01ве（女巫）", "dst": "战斗飞行扫帚", "relation": "是", "confidence": 0.8},
            {"src": "苏霍伊设计局", "dst": "Su-01ве（女巫）", "relation": "研制", "confidence": 0.8},
            {"src": "Su-01ве（女巫）", "dst": "芝诺军备学院", "relation": "隶属", "confidence": 0.9},
            {"src": "芝诺军备学院", "dst": "芝诺", "relation": "属于", "confidence": 0.8},
            {"src": "基金会药事管理名册", "dst": "苦哑巴药剂", "relation": "收录", "confidence": 0.8},
            {"src": "苦哑巴药剂", "dst": "圣洛夫基金会", "relation": "需批准", "confidence": 0.7},
            {"src": "基金会药事管理名册", "dst": "基金会神秘学制剂持有许可", "relation": "提及", "confidence": 0.7},
            {"src": "Su-01ве（女巫）", "dst": "神秘学探测器", "relation": "装配", "confidence": 0.7},
            {"src": "Su-01ве（女巫）", "dst": "ST-30-1 30mm神秘术瞬发装置", "relation": "装配", "confidence": 0.7},
        ],
    },
    # 9) 甲板装饰群与船员战力排名 · 莫桑女士的随身记录册、苏芙比、诺拉·沃德
    "81604fd950090dc2": {
        "entities": [
            {"name": "甲板装饰群", "type": "物品", "aliases": []},
            {"name": "船长", "type": "角色", "aliases": []},
            {"name": "暴风雨", "type": "现象", "aliases": []},
            {"name": "优雅的橡树女士", "type": "角色", "aliases": []},
            {"name": "巡航女巫", "type": "角色", "aliases": []},
            {"name": "领航者", "type": "角色", "aliases": []},
            {"name": "莫桑女士的随身记录册", "type": "物品", "aliases": []},
            {"name": "莫桑", "type": "角色", "aliases": []},
            {"name": "苏芙比", "type": "角色", "aliases": []},
            {"name": "基金会", "type": "组织", "aliases": []},
            {"name": "坚果干酪酥", "type": "物品", "aliases": []},
            {"name": "覆盆子蛋白酥布丁", "type": "物品", "aliases": []},
            {"name": "德国分部", "type": "组织", "aliases": []},
            {"name": "玛丽·史密斯", "type": "角色", "aliases": ["史密斯女士"]},
            {"name": "诺拉·沃德", "type": "角色", "aliases": []},
            {"name": "反抗军", "type": "组织", "aliases": []},
            {"name": "林地", "type": "地点", "aliases": []},
            {"name": "和平主义者", "type": "概念", "aliases": []},
            {"name": "Just One Song", "type": "物品", "aliases": []},
            {"name": "Rock Around the Ship", "type": "物品", "aliases": []},
            {"name": "Please Please Sotheby", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "优雅的橡树女士", "dst": "反抗军", "relation": "为领军", "confidence": 0.8},
            {"src": "优雅的橡树女士", "dst": "林地", "relation": "守护", "confidence": 0.8},
            {"src": "领航者", "dst": "和平主义者", "relation": "是", "confidence": 0.8},
            {"src": "莫桑女士的随身记录册", "dst": "莫桑", "relation": "属于", "confidence": 0.9},
            {"src": "莫桑女士的随身记录册", "dst": "苏芙比", "relation": "提及", "confidence": 0.7},
            {"src": "莫桑女士的随身记录册", "dst": "基金会", "relation": "提及", "confidence": 0.7},
            {"src": "莫桑女士的随身记录册", "dst": "德国分部", "relation": "提及", "confidence": 0.7},
            {"src": "莫桑女士的随身记录册", "dst": "玛丽·史密斯", "relation": "提及", "confidence": 0.8},
            {"src": "诺拉·沃德", "dst": "德国分部", "relation": "隶属", "confidence": 0.7},
            {"src": "莫桑", "dst": "诺拉·沃德", "relation": "化名", "confidence": 0.8},
            {"src": "玛丽·史密斯", "dst": "莫桑", "relation": "联络", "confidence": 0.7},
        ],
    },
    # 10) 介绍信与暴雨采集分析报告 · 莫桑、马丁·莫尔、维尔汀、非对称核素R
    "03b496b1c17c02a6": {
        "entities": [
            {"name": "介绍信", "type": "物品", "aliases": []},
            {"name": "莫桑", "type": "角色", "aliases": []},
            {"name": "基金会总部", "type": "组织", "aliases": []},
            {"name": "马丁·莫尔", "type": "角色", "aliases": []},
            {"name": "德国分部", "type": "组织", "aliases": []},
            {"name": "巴伐利亚地区", "type": "地点", "aliases": []},
            {"name": "陶瓷工坊", "type": "地点", "aliases": []},
            {"name": "云杉", "type": "物品", "aliases": []},
            {"name": "维尔汀", "type": "角色", "aliases": []},
            {"name": "暴雨", "type": "现象", "aliases": ["“暴雨”"]},
            {"name": "暴雨采集分析报告", "type": "物品", "aliases": ["暴雨”采集分析报告"]},
            {"name": "暴雨雨滴", "type": "物品", "aliases": ["暴雨”雨滴"]},
            {"name": "拉普拉斯科算中心", "type": "组织", "aliases": []},
            {"name": "非对称核素R", "type": "概念", "aliases": ["“非对称核素R”"]},
            {"name": "神秘术显影实验", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "介绍信", "dst": "莫桑", "relation": "致", "confidence": 0.7},
            {"src": "基金会总部", "dst": "莫桑", "relation": "联络", "confidence": 0.7},
            {"src": "马丁·莫尔", "dst": "德国分部", "relation": "隶属", "confidence": 0.8},
            {"src": "莫桑", "dst": "巴伐利亚地区", "relation": "前往", "confidence": 0.7},
            {"src": "莫桑", "dst": "德国分部", "relation": "调查", "confidence": 0.7},
            {"src": "陶瓷工坊", "dst": "云杉", "relation": "有", "confidence": 0.7},
            {"src": "暴雨采集分析报告", "dst": "拉普拉斯科算中心", "relation": "委托于", "confidence": 0.8},
            {"src": "暴雨采集分析报告", "dst": "暴雨雨滴", "relation": "采集", "confidence": 0.8},
            {"src": "暴雨雨滴", "dst": "非对称核素R", "relation": "含", "confidence": 0.8},
            {"src": "神秘术显影实验", "dst": "非对称核素R", "relation": "观测", "confidence": 0.8},
            {"src": "维尔汀", "dst": "暴雨", "relation": "行走于", "confidence": 0.8},
        ],
    },
    # 11) 灰白屋子与因数 · 37、质数、调侃诗/酒神之诗、赛事回顾/辩论赛
    "1fff927b0533cef0": {
        "entities": [
            {"name": "灰白屋子", "type": "地点", "aliases": []},
            {"name": "因数", "type": "概念", "aliases": []},
            {"name": "真理", "type": "概念", "aliases": []},
            {"name": "37", "type": "概念", "aliases": []},
            {"name": "质数", "type": "概念", "aliases": []},
            {"name": "天才", "type": "概念", "aliases": []},
            {"name": "调侃诗", "type": "物品", "aliases": []},
            {"name": "酒神之诗", "type": "物品", "aliases": []},
            {"name": "赛事回顾", "type": "概念", "aliases": []},
            {"name": "辩论赛", "type": "事件", "aliases": []},
        ],
        "relations": [
            {"src": "37", "dst": "质数", "relation": "是", "confidence": 0.9},
            {"src": "37", "dst": "天才", "relation": "象征", "confidence": 0.7},
            {"src": "调侃诗", "dst": "酒神之诗", "relation": "是", "confidence": 0.8},
            {"src": "赛事回顾", "dst": "辩论赛", "relation": "关于", "confidence": 0.7},
            {"src": "辩论赛", "dst": "真理", "relation": "驳倒", "confidence": 0.7},
        ],
    },
    # 12) 第三条岔路与白袍子老师 · 康庄大道、方砖、林间小路
    "1d6254a09b5bcf16": {
        "entities": [
            {"name": "第三条岔路", "type": "地点", "aliases": []},
            {"name": "洞穴", "type": "地点", "aliases": []},
            {"name": "考卷", "type": "物品", "aliases": []},
            {"name": "勋章", "type": "物品", "aliases": []},
            {"name": "树蛙", "type": "角色", "aliases": []},
            {"name": "石桌", "type": "物品", "aliases": []},
            {"name": "白袍子", "type": "物品", "aliases": []},
            {"name": "老师", "type": "角色", "aliases": ["教员", "导师", "教书匠"]},
            {"name": "旗帜", "type": "物品", "aliases": []},
            {"name": "康庄大道", "type": "概念", "aliases": []},
            {"name": "柏油马路", "type": "物品", "aliases": []},
            {"name": "燃油汽车", "type": "物品", "aliases": []},
            {"name": "方砖", "type": "物品", "aliases": []},
            {"name": "林间小路", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "白袍子", "dst": "老师", "relation": "被称作", "confidence": 0.7},
            {"src": "老师", "dst": "旗帜", "relation": "不署名于", "confidence": 0.7},
            {"src": "康庄大道", "dst": "柏油马路", "relation": "含", "confidence": 0.7},
            {"src": "康庄大道", "dst": "燃油汽车", "relation": "含", "confidence": 0.7},
            {"src": "老师", "dst": "树蛙", "relation": "教导", "confidence": 0.6},
        ],
    },
    # 13) 中立者与数字牢狱 · 37、艺术乌托邦、教典、沙滩/广场
    "64cc7e380374d5bb": {
        "entities": [
            {"name": "真理", "type": "概念", "aliases": []},
            {"name": "37", "type": "概念", "aliases": []},
            {"name": "颜色驳杂的废纸若干", "type": "物品", "aliases": []},
            {"name": "数字牢狱", "type": "概念", "aliases": []},
            {"name": "艺术乌托邦", "type": "概念", "aliases": []},
            {"name": "教典", "type": "物品", "aliases": []},
            {"name": "艺术沙龙", "type": "组织", "aliases": []},
            {"name": "沙滩", "type": "地点", "aliases": []},
            {"name": "广场", "type": "地点", "aliases": []},
            {"name": "乌托邦", "type": "概念", "aliases": []},
            {"name": "中立者", "type": "角色", "aliases": []},
            {"name": "数学", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "37", "dst": "数学", "relation": "关乎", "confidence": 0.7},
            {"src": "数字牢狱", "dst": "艺术乌托邦", "relation": "改造为", "confidence": 0.8},
            {"src": "教典", "dst": "艺术沙龙", "relation": "授课于", "confidence": 0.7},
            {"src": "沙滩", "dst": "广场", "relation": "连同", "confidence": 0.7},
            {"src": "乌托邦", "dst": "艺术乌托邦", "relation": "即", "confidence": 0.7},
        ],
    },
    # 14) 哨兵传说 · 受伤士兵、玛尔纱与乔尼、愤恨的主妇
    "98124eb7ebb5668d": {
        "entities": [
            {"name": "受伤士兵", "type": "角色", "aliases": []},
            {"name": "哨兵", "type": "角色", "aliases": ["‘哨兵’"]},
            {"name": "伤兵", "type": "角色", "aliases": []},
            {"name": "绷带", "type": "物品", "aliases": []},
            {"name": "投矛", "type": "物品", "aliases": []},
            {"name": "蝙蝠", "type": "角色", "aliases": []},
            {"name": "教堂钟楼", "type": "地点", "aliases": []},
            {"name": "石像鬼", "type": "角色", "aliases": []},
            {"name": "斗篷", "type": "物品", "aliases": []},
            {"name": "目击者", "type": "角色", "aliases": []},
            {"name": "乔尼", "type": "角色", "aliases": []},
            {"name": "玛尔纱", "type": "角色", "aliases": []},
            {"name": "愤恨的主妇", "type": "角色", "aliases": []},
            {"name": "国家英雄", "type": "角色", "aliases": []},
            {"name": "贵族", "type": "角色", "aliases": []},
            {"name": "家长", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "哨兵", "dst": "投矛", "relation": "持", "confidence": 0.7},
            {"src": "哨兵", "dst": "蝙蝠", "relation": "似", "confidence": 0.7},
            {"src": "哨兵", "dst": "石像鬼", "relation": "似", "confidence": 0.7},
            {"src": "哨兵", "dst": "教堂钟楼", "relation": "栖于", "confidence": 0.6},
            {"src": "玛尔纱", "dst": "乔尼", "relation": "哀悼", "confidence": 0.7},
            {"src": "目击者", "dst": "哨兵", "relation": "目击", "confidence": 0.7},
            {"src": "愤恨的主妇", "dst": "国家英雄", "relation": "评说", "confidence": 0.7},
            {"src": "受伤士兵", "dst": "绷带", "relation": "缠", "confidence": 0.7},
        ],
    },
    # 15) 艾格尼丝致信 · 拉蒂斯、玛丽安娜、教堂、机器与狗哨
    "e601a2f8952a74eb": {
        "entities": [
            {"name": "拉蒂斯", "type": "角色", "aliases": []},
            {"name": "玛丽安娜", "type": "角色", "aliases": []},
            {"name": "艾格尼丝", "type": "角色", "aliases": []},
            {"name": "教堂", "type": "地点", "aliases": []},
            {"name": "机器", "type": "概念", "aliases": []},
            {"name": "狗哨", "type": "物品", "aliases": []},
            {"name": "老兵", "type": "角色", "aliases": []},
            {"name": "魔鬼", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "艾格尼丝", "dst": "拉蒂斯", "relation": "提及", "confidence": 0.7},
            {"src": "艾格尼丝", "dst": "玛丽安娜", "relation": "交谈", "confidence": 0.7},
            {"src": "艾格尼丝", "dst": "教堂", "relation": "设想修建", "confidence": 0.7},
            {"src": "艾格尼丝", "dst": "机器", "relation": "欲盖过", "confidence": 0.6},
        ],
    },
    # 16) 巴黎神秘学企业家与神秘学家观察 · 灰调蓝、夜巡特遣管理局、预言家
    "3e3c090a48461d30": {
        "entities": [
            {"name": "人类", "type": "概念", "aliases": []},
            {"name": "神秘学家", "type": "概念", "aliases": []},
            {"name": "巴黎", "type": "地点", "aliases": []},
            {"name": "神秘学企业家", "type": "角色", "aliases": []},
            {"name": "神秘学家观察（半月刊）", "type": "物品", "aliases": ["《神秘学家观察（半月刊）》"]},
            {"name": "灰调蓝小姐", "type": "角色", "aliases": []},
            {"name": "占卜师", "type": "角色", "aliases": []},
            {"name": "夜巡特遣管理局", "type": "组织", "aliases": []},
            {"name": "预言", "type": "概念", "aliases": []},
            {"name": "神秘学藏品", "type": "物品", "aliases": []},
            {"name": "预言家", "type": "角色", "aliases": []},
            {"name": "命运", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "神秘学企业家", "dst": "巴黎", "relation": "开设分店", "confidence": 0.8},
            {"src": "巴黎", "dst": "神秘学家", "relation": "吸引", "confidence": 0.8},
            {"src": "神秘学家观察（半月刊）", "dst": "巴黎", "relation": "报道", "confidence": 0.7},
            {"src": "灰调蓝小姐", "dst": "预言", "relation": "回避", "confidence": 0.7},
            {"src": "灰调蓝小姐", "dst": "占卜师", "relation": "是", "confidence": 0.7},
            {"src": "夜巡特遣管理局", "dst": "神秘学藏品", "relation": "追究", "confidence": 0.7},
            {"src": "预言家", "dst": "神秘学藏品", "relation": "取走", "confidence": 0.7},
            {"src": "预言家", "dst": "夜巡特遣管理局", "relation": "被调查", "confidence": 0.7},
            {"src": "预言家", "dst": "预言", "relation": "从事", "confidence": 0.7},
            {"src": "预言家", "dst": "灰调蓝小姐", "relation": "对话", "confidence": 0.8},
        ],
    },
    # 17) 玛丽姨妈与费利西安 · 灰调蓝呼唤不存在的朋友、雷电神秘术与发电机
    "292d48e02e0e53de": {
        "entities": [
            {"name": "玛丽姨妈", "type": "角色", "aliases": []},
            {"name": "灰调蓝小姐", "type": "角色", "aliases": []},
            {"name": "弗里西亚", "type": "角色", "aliases": []},
            {"name": "费利西安", "type": "角色", "aliases": []},
            {"name": "贝丽尔", "type": "角色", "aliases": []},
            {"name": "阿黛拉", "type": "角色", "aliases": []},
            {"name": "贵族", "type": "角色", "aliases": []},
            {"name": "雷电神秘术", "type": "概念", "aliases": []},
            {"name": "发电机", "type": "物品", "aliases": []},
            {"name": "相册", "type": "物品", "aliases": []},
            {"name": "合照", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "灰调蓝小姐", "dst": "费利西安", "relation": "呼唤", "confidence": 0.7},
            {"src": "费利西安", "dst": "灰调蓝小姐", "relation": "关联", "confidence": 0.7},
            {"src": "费利西安", "dst": "贵族", "relation": "是", "confidence": 0.8},
            {"src": "费利西安", "dst": "雷电神秘术", "relation": "拥有", "confidence": 0.8},
            {"src": "费利西安", "dst": "发电机", "relation": "因之没落", "confidence": 0.7},
            {"src": "灰调蓝小姐", "dst": "弗里西亚", "relation": "误称", "confidence": 0.6},
            {"src": "费利西安", "dst": "贝丽尔", "relation": "并列提及", "confidence": 0.6},
            {"src": "费利西安", "dst": "阿黛拉", "relation": "并列提及", "confidence": 0.6},
            {"src": "玛丽姨妈", "dst": "合照", "relation": "不在", "confidence": 0.7},
            {"src": "玛丽姨妈", "dst": "相册", "relation": "不在", "confidence": 0.7},
        ],
    },
    # 18) 布列科夫少将处置令 · 芝诺最高指挥部、梅蕾尔、玛尔纱、托勒密、止血带
    "7c022711e639ef7a": {
        "entities": [
            {"name": "布列科夫少将", "type": "角色", "aliases": []},
            {"name": "芝诺最高指挥部", "type": "组织", "aliases": []},
            {"name": "军督队", "type": "组织", "aliases": []},
            {"name": "芝诺", "type": "组织", "aliases": []},
            {"name": "芝诺军备学院", "type": "组织", "aliases": []},
            {"name": "梅蕾尔", "type": "角色", "aliases": []},
            {"name": "玛尔纱", "type": "角色", "aliases": []},
            {"name": "托勒密", "type": "角色", "aliases": []},
            {"name": "止血带", "type": "物品", "aliases": []},
            {"name": "橡皮管", "type": "物品", "aliases": []},
            {"name": "医院", "type": "地点", "aliases": []},
            {"name": "狮鹫军", "type": "组织", "aliases": []},
            {"name": "创伤性脑损伤", "type": "概念", "aliases": []},
            {"name": "基本处置方案", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "芝诺最高指挥部", "dst": "布列科夫少将", "relation": "处罚", "confidence": 0.9},
            {"src": "布列科夫少将", "dst": "芝诺", "relation": "隶属", "confidence": 0.7},
            {"src": "芝诺最高指挥部", "dst": "军督队", "relation": "派遣", "confidence": 0.8},
            {"src": "芝诺军备学院", "dst": "芝诺", "relation": "属于", "confidence": 0.8},
            {"src": "芝诺军备学院", "dst": "布列科夫少将", "relation": "签署处置", "confidence": 0.7},
            {"src": "梅蕾尔", "dst": "玛尔纱", "relation": "提及", "confidence": 0.8},
            {"src": "梅蕾尔", "dst": "托勒密", "relation": "对话", "confidence": 0.7},
            {"src": "梅蕾尔", "dst": "止血带", "relation": "需要", "confidence": 0.7},
            {"src": "梅蕾尔", "dst": "医院", "relation": "身处", "confidence": 0.7},
            {"src": "止血带", "dst": "橡皮管", "relation": "用", "confidence": 0.7},
            {"src": "基本处置方案", "dst": "创伤性脑损伤", "relation": "未提及", "confidence": 0.7},
            {"src": "狮鹫军", "dst": "止血带", "relation": "拥有", "confidence": 0.7},
        ],
    },
    # 19) 顿河伊万与斯捷尔诺娃 · 梅蕾尔追问跟踪药剂、猎犬、刻雷乌斯
    "e732309d0892d47c": {
        "entities": [
            {"name": "斯捷尔诺娃", "type": "角色", "aliases": []},
            {"name": "伊万", "type": "角色", "aliases": ["军长伊万"]},
            {"name": "顿河", "type": "地点", "aliases": []},
            {"name": "埃梅利", "type": "角色", "aliases": []},
            {"name": "嫩芦苇", "type": "角色", "aliases": ["“嫩芦苇”"]},
            {"name": "老马", "type": "角色", "aliases": []},
            {"name": "小马驹儿", "type": "角色", "aliases": []},
            {"name": "行政申诉", "type": "物品", "aliases": []},
            {"name": "基金会", "type": "组织", "aliases": []},
            {"name": "梅蕾尔", "type": "角色", "aliases": []},
            {"name": "叶尔莫莱", "type": "角色", "aliases": []},
            {"name": "跟踪药剂", "type": "物品", "aliases": []},
            {"name": "猎犬", "type": "角色", "aliases": ["“猎犬”"]},
            {"name": "刻雷乌斯", "type": "角色", "aliases": []},
            {"name": "厨房", "type": "地点", "aliases": []},
            {"name": "检讨书", "type": "物品", "aliases": []},
            {"name": "战马", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "斯捷尔诺娃", "dst": "伊万", "relation": "汇报", "confidence": 0.8},
            {"src": "伊万", "dst": "顿河", "relation": "来自", "confidence": 0.7},
            {"src": "埃梅利", "dst": "嫩芦苇", "relation": "保下", "confidence": 0.8},
            {"src": "嫩芦苇", "dst": "战马", "relation": "养护", "confidence": 0.7},
            {"src": "老马", "dst": "小马驹儿", "relation": "保护", "confidence": 0.7},
            {"src": "梅蕾尔", "dst": "叶尔莫莱", "relation": "对话", "confidence": 0.8},
            {"src": "梅蕾尔", "dst": "跟踪药剂", "relation": "追问", "confidence": 0.7},
            {"src": "叶尔莫莱", "dst": "跟踪药剂", "relation": "施用", "confidence": 0.7},
            {"src": "梅蕾尔", "dst": "猎犬", "relation": "称呼", "confidence": 0.7},
            {"src": "猎犬", "dst": "叶尔莫莱", "relation": "即", "confidence": 0.8},
            {"src": "梅蕾尔", "dst": "刻雷乌斯", "relation": "汇报", "confidence": 0.7},
            {"src": "叶尔莫莱", "dst": "刻雷乌斯", "relation": "遇见", "confidence": 0.7},
            {"src": "梅蕾尔", "dst": "检讨书", "relation": "写", "confidence": 0.8},
            {"src": "基金会", "dst": "行政申诉", "relation": "提出", "confidence": 0.7},
        ],
    },
    # 20) 伦敦报纸与新闻速报 · 泰晤士河条例、长毛绒绒运动会、艺术与艺术家
    "2f059b5ee12542dd": {
        "entities": [
            {"name": "一叠报纸", "type": "物品", "aliases": []},
            {"name": "伦敦警方", "type": "组织", "aliases": []},
            {"name": "泰晤士河禁止通行条例（暂行）", "type": "物品", "aliases": ["《泰晤士河禁止通行条例（暂行）》"]},
            {"name": "长毛绒绒运动会", "type": "事件", "aliases": []},
            {"name": "海德公园", "type": "地点", "aliases": []},
            {"name": "伦敦第一家免费商店", "type": "组织", "aliases": []},
            {"name": "摄政街", "type": "地点", "aliases": []},
            {"name": "灵感泡泡水", "type": "物品", "aliases": []},
            {"name": "寂静的春天", "type": "物品", "aliases": ["《寂静的春天》"]},
            {"name": "波普艺术标牌", "type": "物品", "aliases": []},
            {"name": "市长", "type": "角色", "aliases": []},
            {"name": "主食", "type": "物品", "aliases": ["“主食”"]},
            {"name": "字母意面", "type": "物品", "aliases": []},
            {"name": "杜松子酒", "type": "物品", "aliases": []},
            {"name": "艺术与艺术家", "type": "概念", "aliases": []},
            {"name": "中等教育", "type": "概念", "aliases": []},
            {"name": "通俗艺术", "type": "概念", "aliases": []},
            {"name": "抽象主义", "type": "概念", "aliases": []},
            {"name": "街头文化", "type": "概念", "aliases": []},
            {"name": "新闻速报", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "伦敦警方", "dst": "泰晤士河禁止通行条例（暂行）", "relation": "颁布", "confidence": 0.9},
            {"src": "长毛绒绒运动会", "dst": "海德公园", "relation": "举办于", "confidence": 0.9},
            {"src": "伦敦第一家免费商店", "dst": "摄政街", "relation": "位于", "confidence": 0.8},
            {"src": "伦敦第一家免费商店", "dst": "灵感泡泡水", "relation": "出售", "confidence": 0.8},
            {"src": "伦敦第一家免费商店", "dst": "寂静的春天", "relation": "出售", "confidence": 0.8},
            {"src": "伦敦第一家免费商店", "dst": "波普艺术标牌", "relation": "出售", "confidence": 0.8},
            {"src": "一叠报纸", "dst": "新闻速报", "relation": "刊载", "confidence": 0.7},
            {"src": "一叠报纸", "dst": "市长", "relation": "记录", "confidence": 0.7},
            {"src": "主食", "dst": "字母意面", "relation": "含", "confidence": 0.7},
            {"src": "主食", "dst": "杜松子酒", "relation": "含", "confidence": 0.7},
            {"src": "艺术与艺术家", "dst": "通俗艺术", "relation": "提及", "confidence": 0.7},
            {"src": "艺术与艺术家", "dst": "抽象主义", "relation": "提及", "confidence": 0.7},
            {"src": "艺术与艺术家", "dst": "街头文化", "relation": "提及", "confidence": 0.7},
            {"src": "中等教育", "dst": "通俗艺术", "relation": "并行", "confidence": 0.6},
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
        noop = set(json.loads(NOOP_FILE.read_text(encoding="utf-8")))
        noop |= set(NOOP_ADD)
        NOOP_FILE.write_text(
            json.dumps(sorted(noop), ensure_ascii=False, indent=1), encoding="utf-8"
        )
    print(f"[apply-missing-p20] 写入 {len(RESULTS)} 条，NOOP +{len(NOOP_ADD)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
