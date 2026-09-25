# -*- coding: utf-8 -*-
"""未抽取剧情块补抽 · 第 23 批（backfill2 batch_13，20 块）。

用法：
  python scripts/apply_missing_p23.py            # 预演（悬空+落地自检）
  python scripts/apply_missing_p23.py --apply    # 写盘
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

# 本批 20 块均含剧情/对白，无纯数值/UI 页 → 无 NOOP。
NOOP_ADD: list[str] = []

RESULTS: dict[str, dict] = {
    # 1) 收监记录对话 · 感染种转化实验记录与歌声刺激
    "8cad150b34dbdc7f": {
        "entities": [
            {"name": "感染种转化实验记录", "type": "物品", "aliases": []},
            {"name": "感染种", "type": "概念", "aliases": []},
            {"name": "歌声", "type": "概念", "aliases": ['"歌声"']},
            {"name": "神秘学家", "type": "概念", "aliases": []},
            {"name": "人类", "type": "概念", "aliases": []},
            {"name": "血食怪", "type": "概念", "aliases": []},
            {"name": "临时变异融合能力", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "感染种转化实验记录", "dst": "感染种", "relation": "研究", "confidence": 0.8},
            {"src": "感染种转化实验记录", "dst": "歌声", "relation": "以之为刺激源", "confidence": 0.8},
            {"src": "感染种转化实验记录", "dst": "神秘学家", "relation": "采集样本", "confidence": 0.7},
            {"src": "感染种转化实验记录", "dst": "人类", "relation": "采集样本", "confidence": 0.7},
            {"src": "感染种转化实验记录", "dst": "血食怪", "relation": "采集样本", "confidence": 0.7},
            {"src": "临时变异融合能力", "dst": "感染种", "relation": "确认为", "confidence": 0.8},
        ],
    },
    # 2) 长毛绒绒运动会 · 餐后甜点故事与机会主义怪盗
    "7d288174542fc536": {
        "entities": [
            {"name": "长毛绒绒运动会", "type": "事件", "aliases": []},
            {"name": "大伦敦", "type": "地点", "aliases": ["大伦敦全区"]},
            {"name": "宠物文化", "type": "概念", "aliases": []},
            {"name": "餐后甜点", "type": "概念", "aliases": ['"餐后甜点"']},
            {"name": "拉米雷斯", "type": "角色", "aliases": ['"拉米雷斯"']},
            {"name": "伦敦评论", "type": "物品", "aliases": ["《伦敦评论》"]},
            {"name": "立场", "type": "物品", "aliases": ["《立场》"]},
            {"name": "黏黏球", "type": "物品", "aliases": []},
            {"name": "烟囱管道", "type": "物品", "aliases": []},
            {"name": "折光毛毯", "type": "物品", "aliases": []},
            {"name": "恶作剧", "type": "概念", "aliases": []},
            {"name": "机会主义怪盗", "type": "角色", "aliases": []},
            {"name": "泡沫", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "长毛绒绒运动会", "dst": "大伦敦", "relation": "覆盖于", "confidence": 0.7},
            {"src": "长毛绒绒运动会", "dst": "宠物文化", "relation": "推广", "confidence": 0.7},
            {"src": "机会主义怪盗", "dst": "黏黏球", "relation": "使用", "confidence": 0.7},
            {"src": "机会主义怪盗", "dst": "烟囱管道", "relation": "使用", "confidence": 0.7},
            {"src": "机会主义怪盗", "dst": "折光毛毯", "relation": "使用", "confidence": 0.7},
            {"src": "机会主义怪盗", "dst": "恶作剧", "relation": "制造", "confidence": 0.8},
            {"src": "伦敦评论", "dst": "立场", "relation": "刊登", "confidence": 0.8},
            {"src": "泡沫", "dst": "机会主义怪盗", "relation": "比喻", "confidence": 0.7},
        ],
    },
    # 3) 乔的私人眼睛信件 · L.A.中国城艺术物与《Virgil's Archive》
    "99cdc049abc44770": {
        "entities": [
            {"name": "Jo", "type": "角色", "aliases": []},
            {"name": "私人眼睛", "type": "角色", "aliases": []},
            {"name": "DAA", "type": "组织", "aliases": []},
            {"name": "L.A.", "type": "地点", "aliases": []},
            {"name": "中国城", "type": "地点", "aliases": []},
            {"name": "Mr.Wong", "type": "角色", "aliases": []},
            {"name": "医生", "type": "角色", "aliases": []},
            {"name": "患者", "type": "角色", "aliases": []},
            {"name": "Virgil's Archive", "type": "物品", "aliases": ["《Virgil's Archive》"]},
            {"name": "艺术物", "type": "概念", "aliases": []},
            {"name": "艺术部分", "type": "组织", "aliases": []},
            {"name": "基础部分", "type": "概念", "aliases": []},
            {"name": "精神力量", "type": "概念", "aliases": []},
            {"name": "灵魂和空间", "type": "概念", "aliases": []},
            {"name": "尺子", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "Jo", "dst": "私人眼睛", "relation": "是", "confidence": 0.9},
            {"src": "Jo", "dst": "DAA", "relation": "对抗", "confidence": 0.8},
            {"src": "私人眼睛", "dst": "尺子", "relation": "持有", "confidence": 0.7},
            {"src": "L.A.", "dst": "中国城", "relation": "包含", "confidence": 0.8},
            {"src": "中国城", "dst": "患者", "relation": "出现", "confidence": 0.7},
            {"src": "Mr.Wong", "dst": "患者", "relation": "类似", "confidence": 0.7},
            {"src": "Virgil's Archive", "dst": "艺术物", "relation": "记载案例", "confidence": 0.7},
            {"src": "艺术部分", "dst": "基础部分", "relation": "属于", "confidence": 0.8},
            {"src": "艺术物", "dst": "基础部分", "relation": "保存于", "confidence": 0.7},
        ],
    },
    # 4) 科兹洛夫团长与基金会员工闲谈 · 命名日与哑谜化现象
    "d9cd451ba9708fa3": {
        "entities": [
            {"name": "科兹洛夫团长", "type": "角色", "aliases": ["科兹洛夫"]},
            {"name": "新世界", "type": "概念", "aliases": []},
            {"name": "基金会", "type": "组织", "aliases": []},
            {"name": "命名日", "type": "概念", "aliases": []},
            {"name": "罗马传说", "type": "概念", "aliases": []},
            {"name": "日耳曼民俗", "type": "概念", "aliases": []},
            {"name": "日耳曼人", "type": "概念", "aliases": []},
            {"name": "民俗传说", "type": "概念", "aliases": []},
            {"name": "哥特人", "type": "概念", "aliases": []},
            {"name": "哑谜化现象", "type": "现象", "aliases": []},
            {"name": "食堂", "type": "地点", "aliases": []},
            {"name": "字符", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "命名日", "dst": "罗马传说", "relation": "关联", "confidence": 0.7},
            {"src": "命名日", "dst": "日耳曼民俗", "relation": "关联", "confidence": 0.7},
            {"src": "基金会", "dst": "食堂", "relation": "设有", "confidence": 0.7},
            {"src": "哑谜化现象", "dst": "字符", "relation": "呈现于", "confidence": 0.7},
            {"src": "科兹洛夫团长", "dst": "基金会", "relation": "隶属", "confidence": 0.7},
        ],
    },
    # 5) 数值/技能页尾部拼接对白 · 保镖与J
    "0d2219155ab71dcd": {
        "entities": [
            {"name": "报社", "type": "组织", "aliases": []},
            {"name": "前线记者", "type": "角色", "aliases": []},
            {"name": "保镖", "type": "角色", "aliases": []},
            {"name": "记者", "type": "角色", "aliases": []},
            {"name": "座驾", "type": "物品", "aliases": []},
            {"name": "J", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "报社", "dst": "保镖", "relation": "雇佣", "confidence": 0.8},
            {"src": "保镖", "dst": "前线记者", "relation": "保护", "confidence": 0.7},
            {"src": "保镖", "dst": "座驾", "relation": "拥有", "confidence": 0.7},
            {"src": "保镖", "dst": "记者", "relation": "见识", "confidence": 0.7},
            {"src": "保镖", "dst": "J", "relation": "对立", "confidence": 0.7},
        ],
    },
    # 6) 祝县论坛帖 · 松鼠、松子与万物有灵
    "cad64dbd964613b7": {
        "entities": [
            {"name": "太爷爷", "type": "角色", "aliases": ["爷爷"]},
            {"name": "松鼠", "type": "角色", "aliases": []},
            {"name": "松子", "type": "物品", "aliases": []},
            {"name": "花生", "type": "物品", "aliases": []},
            {"name": "树根", "type": "地点", "aliases": []},
            {"name": "老乡", "type": "角色", "aliases": []},
            {"name": "腰果", "type": "物品", "aliases": []},
            {"name": "杏仁", "type": "物品", "aliases": []},
            {"name": "树林", "type": "地点", "aliases": []},
            {"name": "祝县", "type": "地点", "aliases": []},
            {"name": "小树林", "type": "地点", "aliases": []},
            {"name": "田地", "type": "地点", "aliases": []},
            {"name": "刺猬", "type": "角色", "aliases": []},
            {"name": "小鸟", "type": "角色", "aliases": []},
            {"name": "阳台", "type": "地点", "aliases": []},
            {"name": "小米", "type": "物品", "aliases": []},
            {"name": "鸟窝", "type": "物品", "aliases": []},
            {"name": "神秘学松鼠", "type": "角色", "aliases": []},
            {"name": "万物有灵", "type": "概念", "aliases": []},
            {"name": "气蕴万物", "type": "概念", "aliases": []},
            {"name": "体育养生", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "太爷爷", "dst": "松鼠", "relation": "跟随", "confidence": 0.7},
            {"src": "太爷爷", "dst": "松子", "relation": "发现", "confidence": 0.7},
            {"src": "松鼠", "dst": "松子", "relation": "藏匿", "confidence": 0.7},
            {"src": "太爷爷", "dst": "老乡", "relation": "随行", "confidence": 0.7},
            {"src": "祝县", "dst": "小树林", "relation": "包含", "confidence": 0.7},
            {"src": "祝县", "dst": "田地", "relation": "包含", "confidence": 0.7},
            {"src": "神秘学松鼠", "dst": "松鼠", "relation": "属于", "confidence": 0.7},
            {"src": "万物有灵", "dst": "神秘学松鼠", "relation": "体现于", "confidence": 0.7},
        ],
    },
    # 7) 柏林以东述职 · 鬼魂、水母拍拍与时空灾害
    "31acee1d075b4d7f": {
        "entities": [
            {"name": "基金会官员", "type": "角色", "aliases": []},
            {"name": "基金会", "type": "组织", "aliases": []},
            {"name": "柏林以东", "type": "角色", "aliases": []},
            {"name": "老上司", "type": "角色", "aliases": []},
            {"name": "历史", "type": "概念", "aliases": []},
            {"name": "忠诚者", "type": "概念", "aliases": []},
            {"name": "胜利者", "type": "概念", "aliases": []},
            {"name": "鹰派", "type": "概念", "aliases": []},
            {"name": "鸽派", "type": "概念", "aliases": []},
            {"name": "鬼魂", "type": "概念", "aliases": ['"鬼魂"']},
            {"name": "水母拍拍", "type": "物品", "aliases": []},
            {"name": "建筑", "type": "地点", "aliases": []},
            {"name": "时空灾害", "type": "现象", "aliases": ['"时空灾害"']},
            {"name": "石头", "type": "物品", "aliases": []},
            {"name": "童谣", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "基金会官员", "dst": "基金会", "relation": "隶属", "confidence": 0.8},
            {"src": "柏林以东", "dst": "基金会", "relation": "隶属", "confidence": 0.8},
            {"src": "老上司", "dst": "柏林以东", "relation": "送入", "confidence": 0.7},
            {"src": "鹰派", "dst": "鸽派", "relation": "对立", "confidence": 0.7},
            {"src": "鬼魂", "dst": "建筑", "relation": "存在于", "confidence": 0.7},
            {"src": "鬼魂", "dst": "水母拍拍", "relation": "被记录于", "confidence": 0.7},
            {"src": "鬼魂", "dst": "石头", "relation": "一体同源", "confidence": 0.8},
            {"src": "石头", "dst": "时空灾害", "relation": "免疫", "confidence": 0.7},
            {"src": "鬼魂", "dst": "童谣", "relation": "相关", "confidence": 0.7},
        ],
    },
    # 8) 论坛讨论重塑之手 · 一本未完的书与暴雨至90年代
    "2d9e071dfdf1a892": {
        "entities": [
            {"name": "露西女士", "type": "角色", "aliases": ["露西"]},
            {"name": "重塑之手", "type": "组织", "aliases": []},
            {"name": "拉普拉斯", "type": "角色", "aliases": []},
            {"name": "一本未完的书", "type": "物品", "aliases": []},
            {"name": "暴雨", "type": "现象", "aliases": ['"暴雨"']},
            {"name": "伊索尔德小姐", "type": "角色", "aliases": ["伊索尔德"]},
            {"name": "卡卡尼亚小姐", "type": "角色", "aliases": ["卡卡尼亚"]},
            {"name": "塞梅尔维斯女士", "type": "角色", "aliases": ["塞梅尔维斯"]},
            {"name": "血食怪", "type": "概念", "aliases": []},
            {"name": "维也纳事件", "type": "事件", "aliases": []},
            {"name": "霍夫曼女士", "type": "角色", "aliases": ["霍夫曼"]},
            {"name": "委外合约人才管理组织", "type": "组织", "aliases": []},
            {"name": "新时代", "type": "概念", "aliases": []},
            {"name": "90年代", "type": "时间", "aliases": []},
            {"name": "1920年", "type": "时间", "aliases": []},
        ],
        "relations": [
            {"src": "重塑之手", "dst": "拉普拉斯", "relation": "关联", "confidence": 0.7},
            {"src": "一本未完的书", "dst": "暴雨", "relation": "提及", "confidence": 0.7},
            {"src": "一本未完的书", "dst": "伊索尔德小姐", "relation": "提及", "confidence": 0.8},
            {"src": "卡卡尼亚小姐", "dst": "伊索尔德小姐", "relation": "同伴", "confidence": 0.7},
            {"src": "塞梅尔维斯女士", "dst": "血食怪", "relation": "成为", "confidence": 0.8},
            {"src": "塞梅尔维斯女士", "dst": "维也纳事件", "relation": "经历", "confidence": 0.8},
            {"src": "卡卡尼亚小姐", "dst": "委外合约人才管理组织", "relation": "隶属", "confidence": 0.7},
            {"src": "卡卡尼亚小姐", "dst": "新时代", "relation": "融入", "confidence": 0.7},
            {"src": "一本未完的书", "dst": "霍夫曼女士", "relation": "致谢", "confidence": 0.7},
        ],
    },
    # 9) 咖啡馆闲谈 · 好医生、尼采与病情报告
    "03d7768e1d0a9bad": {
        "entities": [
            {"name": "尼采", "type": "角色", "aliases": ['"尼采"']},
            {"name": "幽默剧", "type": "概念", "aliases": []},
            {"name": "病情报告", "type": "物品", "aliases": []},
            {"name": "医生", "type": "角色", "aliases": []},
            {"name": "病人", "type": "角色", "aliases": []},
            {"name": "书籍", "type": "物品", "aliases": []},
            {"name": "杂志", "type": "物品", "aliases": []},
            {"name": "医学院学生", "type": "角色", "aliases": []},
            {"name": "咖啡馆老主顾", "type": "角色", "aliases": []},
            {"name": "吃药", "type": "概念", "aliases": ['"吃药"']},
            {"name": "大脑囚笼", "type": "概念", "aliases": []},
            {"name": "欲望", "type": "概念", "aliases": []},
            {"name": "妄想", "type": "概念", "aliases": []},
            {"name": "灵魂", "type": "概念", "aliases": []},
            {"name": "剧场印象", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "尼采", "dst": "幽默剧", "relation": "创作", "confidence": 0.7},
            {"src": "医生", "dst": "病情报告", "relation": "出具", "confidence": 0.7},
            {"src": "病人", "dst": "吃药", "relation": "服用", "confidence": 0.7},
            {"src": "医生", "dst": "病人", "relation": "诊治", "confidence": 0.7},
            {"src": "病情报告", "dst": "书籍", "relation": "出现于", "confidence": 0.7},
            {"src": "病情报告", "dst": "杂志", "relation": "出现于", "confidence": 0.7},
            {"src": "病情报告", "dst": "医学院学生", "relation": "出现于", "confidence": 0.7},
            {"src": "大脑囚笼", "dst": "欲望", "relation": "包含", "confidence": 0.7},
            {"src": "大脑囚笼", "dst": "妄想", "relation": "包含", "confidence": 0.7},
        ],
    },
    # 10) 维也纳看戏 · 各幕与第六幕人物
    "00d44e74d3c2c2da": {
        "entities": [
            {"name": "维也纳", "type": "地点", "aliases": []},
            {"name": "戏剧", "type": "概念", "aliases": []},
            {"name": "故事", "type": "概念", "aliases": []},
            {"name": "第一幕", "type": "概念", "aliases": []},
            {"name": "第三幕", "type": "概念", "aliases": []},
            {"name": "第五幕", "type": "概念", "aliases": []},
            {"name": "第六幕", "type": "概念", "aliases": []},
            {"name": "国王", "type": "角色", "aliases": []},
            {"name": "骑士", "type": "角色", "aliases": []},
            {"name": "反叛者", "type": "角色", "aliases": []},
            {"name": "暴君", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "维也纳", "dst": "戏剧", "relation": "以之闻名", "confidence": 0.7},
            {"src": "戏剧", "dst": "第一幕", "relation": "包含", "confidence": 0.7},
            {"src": "戏剧", "dst": "第三幕", "relation": "包含", "confidence": 0.7},
            {"src": "戏剧", "dst": "第五幕", "relation": "包含", "confidence": 0.7},
            {"src": "戏剧", "dst": "第六幕", "relation": "包含", "confidence": 0.8},
            {"src": "第六幕", "dst": "国王", "relation": "描绘", "confidence": 0.7},
            {"src": "第六幕", "dst": "骑士", "relation": "描绘", "confidence": 0.7},
            {"src": "第六幕", "dst": "反叛者", "relation": "描绘", "confidence": 0.7},
            {"src": "第六幕", "dst": "暴君", "relation": "描绘", "confidence": 0.7},
        ],
    },
    # 11) 枪响前夜 · 好医生振翅与战争如火车
    "1733306c8835c5d1": {
        "entities": [
            {"name": "好医生", "type": "角色", "aliases": []},
            {"name": "小姐", "type": "角色", "aliases": []},
            {"name": "下层人", "type": "角色", "aliases": []},
            {"name": "咖啡馆", "type": "地点", "aliases": []},
            {"name": "环城大道", "type": "地点", "aliases": []},
            {"name": "镜子", "type": "物品", "aliases": []},
            {"name": "枪响前夜", "type": "事件", "aliases": []},
            {"name": "红磷", "type": "物品", "aliases": []},
            {"name": "战争", "type": "事件", "aliases": []},
            {"name": "火车", "type": "物品", "aliases": []},
            {"name": "老人", "type": "角色", "aliases": []},
            {"name": "婴儿", "type": "角色", "aliases": []},
            {"name": "年轻人", "type": "角色", "aliases": []},
            {"name": "煤炭", "type": "物品", "aliases": []},
            {"name": "旗帜", "type": "物品", "aliases": []},
            {"name": "翅膀", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "好医生", "dst": "翅膀", "relation": "拥有", "confidence": 0.7},
            {"src": "好医生", "dst": "小姐", "relation": "安抚", "confidence": 0.7},
            {"src": "好医生", "dst": "咖啡馆", "relation": "飞向", "confidence": 0.7},
            {"src": "好医生", "dst": "下层人", "relation": "鼓励", "confidence": 0.7},
            {"src": "枪响前夜", "dst": "红磷", "relation": "涉及", "confidence": 0.7},
            {"src": "枪响前夜", "dst": "战争", "relation": "预示", "confidence": 0.8},
            {"src": "战争", "dst": "火车", "relation": "犹如", "confidence": 0.7},
            {"src": "战争", "dst": "旗帜", "relation": "关联", "confidence": 0.7},
            {"src": "火车", "dst": "老人", "relation": "载着", "confidence": 0.7},
            {"src": "火车", "dst": "婴儿", "relation": "载着", "confidence": 0.7},
            {"src": "年轻人", "dst": "煤炭", "relation": "添入", "confidence": 0.7},
            {"src": "好医生", "dst": "环城大道", "relation": "比作", "confidence": 0.7},
            {"src": "好医生", "dst": "镜子", "relation": "比作", "confidence": 0.7},
        ],
    },
    # 12) 美泉宫前夜 · 奥匈帝国与战争发起者
    "e2895db966f292ab": {
        "entities": [
            {"name": "美泉宫", "type": "地点", "aliases": []},
            {"name": "奥匈帝国", "type": "组织", "aliases": []},
            {"name": "侵略者", "type": "角色", "aliases": []},
            {"name": "爱国者", "type": "角色", "aliases": []},
            {"name": "奥匈帝国的夫妇", "type": "角色", "aliases": []},
            {"name": "敞篷汽车", "type": "物品", "aliases": []},
            {"name": "子弹", "type": "物品", "aliases": []},
            {"name": "火车", "type": "物品", "aliases": []},
            {"name": "诗人", "type": "角色", "aliases": []},
            {"name": "音乐家", "type": "角色", "aliases": []},
            {"name": "壕沟", "type": "地点", "aliases": []},
            {"name": "战争发起者", "type": "角色", "aliases": []},
            {"name": "谈判桌", "type": "地点", "aliases": []},
            {"name": "天鹅绒", "type": "物品", "aliases": []},
            {"name": "甜品", "type": "物品", "aliases": []},
            {"name": "泉水", "type": "物品", "aliases": []},
            {"name": "枪膛", "type": "物品", "aliases": []},
            {"name": "炮火", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "奥匈帝国", "dst": "美泉宫", "relation": "拥有", "confidence": 0.7},
            {"src": "奥匈帝国", "dst": "侵略者", "relation": "派遣", "confidence": 0.7},
            {"src": "爱国者", "dst": "子弹", "relation": "赠送", "confidence": 0.7},
            {"src": "敞篷汽车", "dst": "奥匈帝国的夫妇", "relation": "载着", "confidence": 0.7},
            {"src": "子弹", "dst": "枪膛", "relation": "出自", "confidence": 0.7},
            {"src": "诗人", "dst": "壕沟", "relation": "埋于", "confidence": 0.7},
            {"src": "音乐家", "dst": "炮火", "relation": "聆听", "confidence": 0.7},
            {"src": "战争发起者", "dst": "谈判桌", "relation": "位于", "confidence": 0.7},
            {"src": "战争发起者", "dst": "天鹅绒", "relation": "享用", "confidence": 0.7},
            {"src": "美泉宫", "dst": "泉水", "relation": "拥有", "confidence": 0.7},
            {"src": "奥匈帝国的夫妇", "dst": "敞篷汽车", "relation": "乘坐", "confidence": 0.7},
        ],
    },
    # 13) 毕业告别与完美置换 · 改良版隐形墨水配方
    "88e546108bc1c39f": {
        "entities": [
            {"name": "学校", "type": "地点", "aliases": []},
            {"name": "战争", "type": "事件", "aliases": []},
            {"name": "树", "type": "物品", "aliases": []},
            {"name": "法国同窗", "type": "角色", "aliases": []},
            {"name": "胆小鬼", "type": "角色", "aliases": []},
            {"name": "完美置换", "type": "概念", "aliases": []},
            {"name": "改良版隐形墨水配方", "type": "物品", "aliases": []},
            {"name": "仪式祭礼", "type": "概念", "aliases": []},
            {"name": "面粉", "type": "物品", "aliases": []},
            {"name": "干意大利面", "type": "物品", "aliases": []},
            {"name": "咆哮根", "type": "物品", "aliases": []},
            {"name": "盐封咒", "type": "概念", "aliases": []},
            {"name": "苦盐", "type": "物品", "aliases": []},
            {"name": "食盐", "type": "物品", "aliases": []},
            {"name": "湖边", "type": "地点", "aliases": []},
            {"name": "树根", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "学校", "dst": "树", "relation": "拥有", "confidence": 0.7},
            {"src": "战争", "dst": "学校", "relation": "对比", "confidence": 0.7},
            {"src": "完美置换", "dst": "改良版隐形墨水配方", "relation": "涉及", "confidence": 0.7},
            {"src": "改良版隐形墨水配方", "dst": "仪式祭礼", "relation": "用于", "confidence": 0.7},
            {"src": "仪式祭礼", "dst": "面粉", "relation": "使用", "confidence": 0.7},
            {"src": "仪式祭礼", "dst": "干意大利面", "relation": "替代", "confidence": 0.7},
            {"src": "咆哮根", "dst": "盐封咒", "relation": "用于", "confidence": 0.7},
            {"src": "盐封咒", "dst": "苦盐", "relation": "需要", "confidence": 0.7},
            {"src": "盐封咒", "dst": "食盐", "relation": "替代", "confidence": 0.7},
            {"src": "咆哮根", "dst": "湖边", "relation": "发现于", "confidence": 0.7},
            {"src": "法国同窗", "dst": "树", "relation": "类比", "confidence": 0.7},
            {"src": "树", "dst": "树根", "relation": "位于", "confidence": 0.7},
        ],
    },
    # 14) 装卸区域劳作 · 镇民、维拉同志与芝诺谈判
    "fb25b310021a282a": {
        "entities": [
            {"name": "劳动食堂", "type": "地点", "aliases": []},
            {"name": "捡树枝行动", "type": "事件", "aliases": []},
            {"name": "废弃矿区", "type": "地点", "aliases": []},
            {"name": "居民区", "type": "地点", "aliases": []},
            {"name": "装卸区域", "type": "地点", "aliases": []},
            {"name": "劳作区域", "type": "地点", "aliases": []},
            {"name": "镇民", "type": "角色", "aliases": []},
            {"name": "零件", "type": "物品", "aliases": []},
            {"name": "卢恩矿石", "type": "物品", "aliases": []},
            {"name": "钢材", "type": "物品", "aliases": []},
            {"name": "维拉同志", "type": "角色", "aliases": ["维拉"]},
            {"name": "叶甫根尼同志", "type": "角色", "aliases": ["叶甫根尼"]},
            {"name": "芝诺", "type": "组织", "aliases": []},
            {"name": "旅馆", "type": "地点", "aliases": []},
            {"name": "孩子们", "type": "角色", "aliases": []},
            {"name": "矿工", "type": "角色", "aliases": []},
            {"name": "课程", "type": "概念", "aliases": []},
            {"name": "派遣队伍", "type": "组织", "aliases": []},
        ],
        "relations": [
            {"src": "镇民", "dst": "零件", "relation": "发现", "confidence": 0.7},
            {"src": "零件", "dst": "卢恩矿石", "relation": "含有", "confidence": 0.7},
            {"src": "镇民", "dst": "维拉同志", "relation": "提及", "confidence": 0.7},
            {"src": "维拉同志", "dst": "孩子们", "relation": "照看", "confidence": 0.7},
            {"src": "叶甫根尼同志", "dst": "芝诺", "relation": "谈判", "confidence": 0.8},
            {"src": "镇民", "dst": "芝诺", "relation": "议论", "confidence": 0.7},
            {"src": "废弃矿区", "dst": "矿工", "relation": "关联", "confidence": 0.7},
            {"src": "装卸区域", "dst": "劳作区域", "relation": "位于", "confidence": 0.7},
            {"src": "维拉同志", "dst": "课程", "relation": "教授", "confidence": 0.7},
        ],
    },
    # 15) 矿井安全规章与工厂生产 · 伊利亚、基里尔、波金娜、克努特
    "e3e6d946c61b71f9": {
        "entities": [
            {"name": "矿井", "type": "地点", "aliases": []},
            {"name": "生产工厂", "type": "地点", "aliases": []},
            {"name": "矿工", "type": "角色", "aliases": []},
            {"name": "叶甫根尼同志", "type": "角色", "aliases": ["叶甫根尼"]},
            {"name": "伊·伊·诺维科夫", "type": "角色", "aliases": []},
            {"name": "波·弗·布拉金斯卡娅", "type": "角色", "aliases": []},
            {"name": "伊利亚", "type": "角色", "aliases": []},
            {"name": "基里尔", "type": "角色", "aliases": []},
            {"name": "波金娜", "type": "角色", "aliases": []},
            {"name": "克努特", "type": "角色", "aliases": []},
            {"name": "铲车", "type": "物品", "aliases": []},
            {"name": "数独", "type": "概念", "aliases": []},
            {"name": "木材", "type": "物品", "aliases": []},
            {"name": "围场", "type": "地点", "aliases": []},
            {"name": "十字滑轨", "type": "物品", "aliases": []},
            {"name": "支架", "type": "物品", "aliases": []},
            {"name": "零件", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "叶甫根尼同志", "dst": "生产工厂", "relation": "批准生产", "confidence": 0.8},
            {"src": "伊·伊·诺维科夫", "dst": "生产工厂", "relation": "批准", "confidence": 0.7},
            {"src": "波·弗·布拉金斯卡娅", "dst": "生产工厂", "relation": "尝试", "confidence": 0.7},
            {"src": "伊利亚", "dst": "基里尔", "relation": "呼唤", "confidence": 0.7},
            {"src": "伊利亚", "dst": "波金娜", "relation": "提醒", "confidence": 0.7},
            {"src": "波金娜", "dst": "铲车", "relation": "坐在", "confidence": 0.7},
            {"src": "波金娜", "dst": "数独", "relation": "玩", "confidence": 0.7},
            {"src": "基里尔", "dst": "木材", "relation": "运送", "confidence": 0.7},
            {"src": "矿井", "dst": "木材", "relation": "需要", "confidence": 0.7},
            {"src": "生产工厂", "dst": "支架", "relation": "生产", "confidence": 0.7},
            {"src": "生产工厂", "dst": "零件", "relation": "生产", "confidence": 0.7},
            {"src": "伊利亚", "dst": "克努特", "relation": "招呼", "confidence": 0.7},
        ],
    },
    # 16) 书籍之间 · 女巫的花园与小雀儿、魔精顶芽
    "e01722fc8b42f944": {
        "entities": [
            {"name": "书籍", "type": "物品", "aliases": []},
            {"name": "姐姐", "type": "角色", "aliases": []},
            {"name": "妈妈", "type": "角色", "aliases": []},
            {"name": "隔壁太太", "type": "角色", "aliases": []},
            {"name": "宝宝", "type": "角色", "aliases": []},
            {"name": "虫子", "type": "角色", "aliases": []},
            {"name": "紫色花", "type": "物品", "aliases": []},
            {"name": "叶子", "type": "物品", "aliases": []},
            {"name": "应急指南", "type": "物品", "aliases": []},
            {"name": "女巫", "type": "角色", "aliases": []},
            {"name": "花园", "type": "地点", "aliases": []},
            {"name": "小雀儿", "type": "角色", "aliases": []},
            {"name": "倒刺", "type": "概念", "aliases": []},
            {"name": "植物", "type": "物品", "aliases": []},
            {"name": "魔精", "type": "概念", "aliases": []},
            {"name": "顶芽", "type": "物品", "aliases": []},
            {"name": "笔", "type": "物品", "aliases": []},
            {"name": "小腿", "type": "物品", "aliases": []},
            {"name": "伤口", "type": "物品", "aliases": []},
            {"name": "包裹", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "姐姐", "dst": "包裹", "relation": "接收", "confidence": 0.7},
            {"src": "妈妈", "dst": "宝宝", "relation": "嘱托照顾", "confidence": 0.7},
            {"src": "隔壁太太", "dst": "宝宝", "relation": "被照顾", "confidence": 0.7},
            {"src": "虫子", "dst": "紫色花", "relation": "关联", "confidence": 0.7},
            {"src": "虫子", "dst": "叶子", "relation": "关联", "confidence": 0.7},
            {"src": "女巫", "dst": "花园", "relation": "拥有", "confidence": 0.8},
            {"src": "小雀儿", "dst": "花园", "relation": "进入", "confidence": 0.7},
            {"src": "女巫", "dst": "小雀儿", "relation": "跟随", "confidence": 0.7},
            {"src": "植物", "dst": "倒刺", "relation": "带有", "confidence": 0.7},
            {"src": "魔精", "dst": "顶芽", "relation": "垂下", "confidence": 0.7},
            {"src": "应急指南", "dst": "植物", "relation": "警示", "confidence": 0.7},
            {"src": "应急指南", "dst": "魔精", "relation": "警示", "confidence": 0.7},
            {"src": "笔", "dst": "虫子", "relation": "绘制", "confidence": 0.7},
        ],
    },
    # 17) 冒险者独白 · 灵感克制与新闻一则
    "95e1739fbf52bcab": {
        "entities": [
            {"name": "冒险者", "type": "角色", "aliases": []},
            {"name": "神秘学家", "type": "概念", "aliases": []},
            {"name": "基因报告", "type": "物品", "aliases": []},
            {"name": "理智", "type": "概念", "aliases": []},
            {"name": "清洁工", "type": "角色", "aliases": []},
            {"name": "基金经理", "type": "角色", "aliases": []},
            {"name": "水晶骷髅头", "type": "物品", "aliases": []},
            {"name": "太平洋", "type": "地点", "aliases": []},
            {"name": "水草", "type": "物品", "aliases": []},
            {"name": "灵感克制", "type": "概念", "aliases": []},
            {"name": "新闻一则", "type": "物品", "aliases": []},
            {"name": "公告传单", "type": "物品", "aliases": []},
            {"name": "新闻", "type": "概念", "aliases": ['"新闻"']},
        ],
        "relations": [
            {"src": "神秘学家", "dst": "理智", "relation": "缺乏", "confidence": 0.7},
            {"src": "基因报告", "dst": "理智", "relation": "探究", "confidence": 0.7},
            {"src": "水晶骷髅头", "dst": "太平洋", "relation": "无关", "confidence": 0.7},
            {"src": "水草", "dst": "太平洋", "relation": "生长于", "confidence": 0.7},
            {"src": "新闻一则", "dst": "公告传单", "relation": "是", "confidence": 0.9},
            {"src": "新闻一则", "dst": "新闻", "relation": "标示", "confidence": 0.7},
        ],
    },
    # 18) 南太平洋征程 · 找作家命令与幽灵电台
    "4ef1b6ca195e6c3b": {
        "entities": [
            {"name": "美利坚", "type": "地点", "aliases": []},
            {"name": "巴西", "type": "地点", "aliases": []},
            {"name": "澳大利亚", "type": "地点", "aliases": []},
            {"name": "南太平洋", "type": "地点", "aliases": []},
            {"name": "阿根廷", "type": "地点", "aliases": []},
            {"name": "南极", "type": "地点", "aliases": []},
            {"name": "作家", "type": "角色", "aliases": []},
            {"name": "军人", "type": "角色", "aliases": []},
            {"name": "童子军", "type": "角色", "aliases": []},
            {"name": "神秘术", "type": "概念", "aliases": []},
            {"name": "行动纲领", "type": "概念", "aliases": []},
            {"name": "大本营", "type": "地点", "aliases": []},
            {"name": "炮灰", "type": "概念", "aliases": []},
            {"name": "鬼故事", "type": "概念", "aliases": []},
            {"name": "幽灵电台", "type": "物品", "aliases": []},
            {"name": "无线电爱好者", "type": "角色", "aliases": []},
            {"name": "短波台", "type": "物品", "aliases": []},
            {"name": "蜂鸣器", "type": "物品", "aliases": []},
            {"name": "女声", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "美利坚", "dst": "巴西", "relation": "行程经", "confidence": 0.7},
            {"src": "巴西", "dst": "澳大利亚", "relation": "行程经", "confidence": 0.7},
            {"src": "澳大利亚", "dst": "南太平洋", "relation": "畅游", "confidence": 0.7},
            {"src": "南太平洋", "dst": "阿根廷", "relation": "途径", "confidence": 0.7},
            {"src": "阿根廷", "dst": "南极", "relation": "退守", "confidence": 0.7},
            {"src": "作家", "dst": "大本营", "relation": "位于", "confidence": 0.7},
            {"src": "神秘术", "dst": "行动纲领", "relation": "体现", "confidence": 0.7},
            {"src": "童子军", "dst": "军人", "relation": "不及", "confidence": 0.7},
            {"src": "幽灵电台", "dst": "短波台", "relation": "是", "confidence": 0.8},
            {"src": "无线电爱好者", "dst": "幽灵电台", "relation": "收听", "confidence": 0.7},
            {"src": "幽灵电台", "dst": "女声", "relation": "含有", "confidence": 0.7},
            {"src": "鬼故事", "dst": "幽灵电台", "relation": "涉及", "confidence": 0.7},
        ],
    },
    # 19) 登山遇企鹅 · 乌尔里希、莫莉德尔中尉与重塑之手
    "ac4f52667ecfb397": {
        "entities": [
            {"name": "国家公园", "type": "地点", "aliases": []},
            {"name": "登山步道", "type": "地点", "aliases": []},
            {"name": "护卫兵", "type": "角色", "aliases": []},
            {"name": "巨石", "type": "物品", "aliases": []},
            {"name": "老板", "type": "角色", "aliases": []},
            {"name": "乌尔里希", "type": "角色", "aliases": []},
            {"name": "莫莉德尔中尉", "type": "角色", "aliases": ["莫莉德尔"]},
            {"name": "重塑之手", "type": "组织", "aliases": []},
            {"name": "类魔精生物", "type": "概念", "aliases": ['"类魔精生物"']},
            {"name": "企鹅", "type": "角色", "aliases": []},
            {"name": "极地恶兽", "type": "角色", "aliases": []},
            {"name": "登山者", "type": "角色", "aliases": []},
            {"name": "手榴弹", "type": "物品", "aliases": []},
            {"name": "近卫团南极特勤先遣分队", "type": "组织", "aliases": []},
            {"name": "鱼缸头意识唤醒者", "type": "角色", "aliases": []},
            {"name": "嚼嚼松果", "type": "角色", "aliases": []},
            {"name": "佛罗里达", "type": "地点", "aliases": []},
            {"name": "企鹅族群", "type": "角色", "aliases": []},
            {"name": "地图", "type": "物品", "aliases": []},
            {"name": "雪地", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "护卫兵", "dst": "巨石", "relation": "推开", "confidence": 0.7},
            {"src": "乌尔里希", "dst": "地图", "relation": "研究", "confidence": 0.7},
            {"src": "莫莉德尔中尉", "dst": "地图", "relation": "拥有", "confidence": 0.7},
            {"src": "护卫兵", "dst": "重塑之手", "relation": "险为阶下囚", "confidence": 0.7},
            {"src": "类魔精生物", "dst": "雪地", "relation": "出现于", "confidence": 0.7},
            {"src": "企鹅", "dst": "类魔精生物", "relation": "属于", "confidence": 0.7},
            {"src": "极地恶兽", "dst": "登山者", "relation": "攻击", "confidence": 0.7},
            {"src": "护卫兵", "dst": "手榴弹", "relation": "携带", "confidence": 0.7},
            {"src": "近卫团南极特勤先遣分队", "dst": "企鹅", "relation": "统领", "confidence": 0.7},
            {"src": "鱼缸头意识唤醒者", "dst": "近卫团南极特勤先遣分队", "relation": "属于", "confidence": 0.7},
            {"src": "嚼嚼松果", "dst": "乌尔里希", "relation": "道歉", "confidence": 0.7},
            {"src": "嚼嚼松果", "dst": "企鹅族群", "relation": "率领", "confidence": 0.7},
            {"src": "企鹅族群", "dst": "佛罗里达", "relation": "归乡自", "confidence": 0.7},
            {"src": "莫莉德尔中尉", "dst": "护卫兵", "relation": "相救", "confidence": 0.7},
        ],
    },
    # 20) 《叮咚快报》与本耶普实验 · 澳大利亚生物行为学报
    "c6bf8a99b9f10172": {
        "entities": [
            {"name": "入场券", "type": "物品", "aliases": []},
            {"name": "马科尔", "type": "角色", "aliases": []},
            {"name": "叮咚快报", "type": "物品", "aliases": ["《叮咚快报》"]},
            {"name": "私家侦探", "type": "概念", "aliases": ['"私家侦探"']},
            {"name": "澳大利亚生物行为学报", "type": "物品", "aliases": ["《澳大利亚生物行为学报》"]},
            {"name": "本耶普", "type": "角色", "aliases": []},
            {"name": "复兴小队", "type": "组织", "aliases": []},
            {"name": "水族箱", "type": "物品", "aliases": []},
            {"name": "暗箱", "type": "物品", "aliases": []},
            {"name": "卡片", "type": "物品", "aliases": []},
            {"name": "苹果", "type": "物品", "aliases": []},
            {"name": "香蕉", "type": "物品", "aliases": []},
            {"name": "梨", "type": "物品", "aliases": []},
            {"name": "人类志愿者", "type": "角色", "aliases": []},
            {"name": "背鳍", "type": "物品", "aliases": []},
            {"name": "摄像头", "type": "物品", "aliases": []},
            {"name": "谎言反射机制", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "马科尔", "dst": "叮咚快报", "relation": "撰稿", "confidence": 0.8},
            {"src": "叮咚快报", "dst": "私家侦探", "relation": "自称", "confidence": 0.7},
            {"src": "澳大利亚生物行为学报", "dst": "本耶普", "relation": "研究", "confidence": 0.8},
            {"src": "澳大利亚生物行为学报", "dst": "复兴小队", "relation": "协助", "confidence": 0.7},
            {"src": "本耶普", "dst": "水族箱", "relation": "饲养于", "confidence": 0.7},
            {"src": "卡片", "dst": "暗箱", "relation": "放置于", "confidence": 0.7},
            {"src": "卡片", "dst": "苹果", "relation": "描绘", "confidence": 0.7},
            {"src": "卡片", "dst": "香蕉", "relation": "描绘", "confidence": 0.7},
            {"src": "卡片", "dst": "梨", "relation": "描绘", "confidence": 0.7},
            {"src": "人类志愿者", "dst": "本耶普", "relation": "描述", "confidence": 0.7},
            {"src": "摄像头", "dst": "本耶普", "relation": "记录", "confidence": 0.7},
            {"src": "本耶普", "dst": "谎言反射机制", "relation": "具有", "confidence": 0.7},
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
    print(f"[apply-missing-p23] 写入 {len(RESULTS)} 条，NOOP +{len(NOOP_ADD)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
