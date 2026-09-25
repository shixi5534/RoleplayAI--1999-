#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""补抽 2 个漏网高价值批次（batch_midhigh_04 / batch_midhigh_05，共 50 块）。
手工抽取，写盘前 validate() 悬空自检 + landing() 落地自检。"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "knowledge" / "plot_cache" / "wu_ming_zhe"
CORPUS = ROOT / "data" / "knowledge" / "plot_corpus_wu_ming_zhe.json"

RESULTS = {
    # ===== batch_midhigh_04 =====
    "7c31215e0b750f5f": {
        "entities": [
            {"name": "乌卢鲁资格赛", "type": "事件", "aliases": ["Uluru qualifiers"]},
        ],
        "relations": [],
    },
    "1e50d27a44307fd3": {
        "entities": [
            {"name": "牙仙小姐", "type": "角色", "aliases": ["Miss Tooth Fairy"]},
            {"name": "柳小姐", "type": "角色", "aliases": ["Miss Willow"]},
            {"name": "飞行药", "type": "物品", "aliases": ["flying medicine"]},
        ],
        "relations": [
            {"src": "牙仙小姐", "dst": "飞行药", "relation": "给予", "confidence": 0.85},
        ],
    },
    "00dd00358345b98f": {
        "entities": [
            {"name": "弗雷迪", "type": "角色", "aliases": ["Freddy"]},
            {"name": "flutterpeach", "type": "角色", "aliases": ["Flutterpeach"]},
        ],
        "relations": [],
    },
    "802cb62cf6f41f45": {
        "entities": [
            {"name": "斯克鲁奇", "type": "角色", "aliases": ["Scrooge"]},
            {"name": "牙仙女士", "type": "角色", "aliases": ["Ms.Tooth Fairy"]},
            {"name": "体育场", "type": "地点", "aliases": ["the stadium"]},
            {"name": "鱼缸", "type": "物品", "aliases": ["the fish tank"]},
            {"name": "资格赛", "type": "事件", "aliases": ["the qualifiers"]},
        ],
        "relations": [
            {"src": "牙仙女士", "dst": "鱼缸", "relation": "查看", "confidence": 0.8},
        ],
    },
    "994e347caee1df24": {
        "entities": [
            {"name": "韦尔豪泽小姐", "type": "角色", "aliases": ["Miss Weyerhaeuser"]},
            {"name": "协议", "type": "物品", "aliases": ["the agreement"]},
            {"name": "银酒", "type": "物品", "aliases": ["silver wine"]},
            {"name": "蟾蜍油", "type": "物品", "aliases": ["toad oil"]},
        ],
        "relations": [],
    },
    "99b0acd3b5822e06": {
        "entities": [
            {"name": "罗塞塔石碑假说", "type": "概念", "aliases": ["Rosetta's Stone Hypothesis"]},
            {"name": "咒语", "type": "概念", "aliases": ["the Incantation", "Incantation"]},
            {"name": "数字密码", "type": "概念", "aliases": ["Numerical Code", "the numerical code"]},
            {"name": "觉醒者", "type": "角色", "aliases": ["the Awakened", "the awakened"]},
            {"name": "散发", "type": "现象", "aliases": ["the emanation"]},
        ],
        "relations": [
            {"src": "咒语", "dst": "数字密码", "relation": "共享本质", "confidence": 0.85},
            {"src": "咒语", "dst": "散发", "relation": "拯救", "confidence": 0.85},
            {"src": "觉醒者", "dst": "咒语", "relation": "证明有效", "confidence": 0.85},
            {"src": "觉醒者", "dst": "数字密码", "relation": "实验", "confidence": 0.8},
        ],
    },
    "5b19e9a9fc03338a": {
        "entities": [
            {"name": "坎贾拉", "type": "地点", "aliases": ["Kanjara"]},
            {"name": "老板", "type": "角色", "aliases": ["Boss"]},
        ],
        "relations": [],
    },
    "ce838526702249d8": {
        "entities": [
            {"name": "守夜人", "type": "组织", "aliases": ["the Vigil"]},
            {"name": "守夜人学员", "type": "角色", "aliases": ["the Vigil's cadet"]},
        ],
        "relations": [
            {"src": "守夜人学员", "dst": "守夜人", "relation": "隶属", "confidence": 0.85},
        ],
    },
    "6e3615f50e764080": {
        "entities": [
            {"name": "三碗不出门", "type": "概念", "aliases": ["Sam Wan Chut Pak"]},
            {"name": "灵能", "type": "概念", "aliases": ["spiritual energy"]},
            {"name": "奇盛", "type": "角色", "aliases": ["Kee Sing"]},
            {"name": "奚行", "type": "角色", "aliases": ["Xi Xing"]},
        ],
        "relations": [
            {"src": "三碗不出门", "dst": "灵能", "relation": "等同", "confidence": 0.9},
        ],
    },
    "84b5e72dc758c545": {
        "entities": [
            {"name": "钱粮", "type": "角色", "aliases": ["Qianliang", "Qiang Liao"]},
            {"name": "恶灵", "type": "现象", "aliases": ["the evil spirits"]},
            {"name": "阵子", "type": "概念", "aliases": ["Zhenzi"]},
        ],
        "relations": [
            {"src": "钱粮", "dst": "恶灵", "relation": "收纳", "confidence": 0.85},
            {"src": "钱粮", "dst": "阵子", "relation": "缔结契约", "confidence": 0.85},
        ],
    },
    "8c71cb0850c99057": {
        "entities": [
            {"name": "玛蒂尔达", "type": "角色", "aliases": ["Matilda"]},
            {"name": "两名警官", "type": "角色", "aliases": ["the two officers"]},
        ],
        "relations": [],
    },
    "0fcac85868be2b42": {
        "entities": [
            {"name": "公主", "type": "角色", "aliases": ["princess"]},
        ],
        "relations": [],
    },
    "69c1d2f5453a7931": {
        "entities": [
            {"name": "疯子", "type": "角色", "aliases": ["that lunatic"]},
            {"name": "神秘学事务官", "type": "角色", "aliases": ["arcane affairs officer"]},
            {"name": "守夜人", "type": "组织", "aliases": ["a vigil"]},
            {"name": "三回约翰尼", "type": "角色", "aliases": ["Johnny Three Times"]},
        ],
        "relations": [
            {"src": "神秘学事务官", "dst": "守夜人", "relation": "隶属", "confidence": 0.8},
        ],
    },
    "59a52f96fc96f535": {
        "entities": [
            {"name": "普瓦捷", "type": "角色", "aliases": ["Poitier"]},
            {"name": "DAA", "type": "组织", "aliases": ["the DAA"]},
            {"name": "菜鸟", "type": "角色", "aliases": ["rookie"]},
        ],
        "relations": [
            {"src": "普瓦捷", "dst": "菜鸟", "relation": "训斥", "confidence": 0.75},
        ],
    },
    "e8baf0340318cd58": {
        "entities": [
            {"name": "穿刺骑士", "type": "角色", "aliases": ["Knight Piercer"]},
            {"name": "七星女士", "type": "角色", "aliases": ["Ms.Qi Xin"]},
            {"name": "银针", "type": "概念", "aliases": ["Silver Needle"]},
            {"name": "洛杉矶", "type": "地点", "aliases": ["L.A."]},
        ],
        "relations": [
            {"src": "七星女士", "dst": "穿刺骑士", "relation": "术法相似", "confidence": 0.8},
            {"src": "七星女士", "dst": "银针", "relation": "掌握", "confidence": 0.85},
        ],
    },
    "4c87d25a88d6dd5e": {
        "entities": [
            {"name": "210号房", "type": "地点", "aliases": ["room 210"]},
            {"name": "二楼", "type": "地点", "aliases": ["the second floor"]},
        ],
        "relations": [],
    },
    "e45e6b23a7a2bbad": {
        "entities": [
            {"name": "太阳", "type": "概念", "aliases": ["the Sun", "Sun"]},
            {"name": "水星", "type": "概念", "aliases": ["Mercury"]},
            {"name": "金星", "type": "概念", "aliases": ["Venus"]},
            {"name": "火星", "type": "概念", "aliases": ["Mars"]},
            {"name": "木星", "type": "概念", "aliases": ["Jupiter"]},
            {"name": "土星", "type": "概念", "aliases": ["Saturn"]},
            {"name": "天王星", "type": "概念", "aliases": ["Uranus"]},
            {"name": "地球", "type": "概念", "aliases": ["Earth"]},
        ],
        "relations": [],
    },
    "22448ba4f42cd9bb": {
        "entities": [
            {"name": "太阳", "type": "概念", "aliases": ["the sun", "sun"]},
            {"name": "火星", "type": "概念", "aliases": ["Mars"]},
            {"name": "木星", "type": "概念", "aliases": ["Jupiter"]},
            {"name": "土星", "type": "概念", "aliases": ["Saturn"]},
            {"name": "天王星", "type": "概念", "aliases": ["Uranus"]},
        ],
        "relations": [],
    },
    "845819044d0298fa": {
        "entities": [],
        "relations": [],
    },
    "13aed9fb0912f43b": {
        "entities": [
            {"name": "有条件术法", "type": "概念", "aliases": ["The arcane skill with conditions"]},
            {"name": "西伯利亚萨满教", "type": "概念", "aliases": ["Siberian shamanism"]},
            {"name": "不可挽回的诅咒与誓言", "type": "概念", "aliases": ["the irretrievable curses and vows"]},
        ],
        "relations": [
            {"src": "有条件术法", "dst": "不可挽回的诅咒与誓言", "relation": "类似", "confidence": 0.85},
            {"src": "不可挽回的诅咒与誓言", "dst": "西伯利亚萨满教", "relation": "属于", "confidence": 0.85},
        ],
    },
    "786296845ae7a158": {
        "entities": [
            {"name": "传教士", "type": "角色", "aliases": ["the preacher"]},
            {"name": "新神谕", "type": "事件", "aliases": ["a new oracle"]},
            {"name": "安全屋", "type": "地点", "aliases": ["the safety house"]},
        ],
        "relations": [],
    },
    "b3fbb0e9359d0d61": {
        "entities": [
            {"name": "博尼什小姐", "type": "角色", "aliases": ["Mlle Boniche"]},
            {"name": "基金会", "type": "组织", "aliases": ["la fondation"]},
            {"name": "手形面具", "type": "物品", "aliases": ["masques en forme de mains"]},
        ],
        "relations": [
            {"src": "博尼什小姐", "dst": "基金会", "relation": "出身", "confidence": 0.85},
        ],
    },
    "413b453463147488": {
        "entities": [
            {"name": "库里亚", "type": "组织", "aliases": ["Curia"]},
            {"name": "美国", "type": "地点", "aliases": ["America"]},
            {"name": "水晶耳环", "type": "物品", "aliases": ["crystal earring"]},
            {"name": "时尚魔杖", "type": "物品", "aliases": ["a stylish wand"]},
            {"name": "库珀", "type": "角色", "aliases": ["Miss Cooper", "Cooper"]},
        ],
        "relations": [],
    },
    "dc505d76b6b9a5f3": {
        "entities": [
            {"name": "重塑之手", "type": "组织", "aliases": []},
            {"name": "迷雾", "type": "现象", "aliases": []},
            {"name": "罕见术法", "type": "概念", "aliases": []},
            {"name": "追踪神秘术", "type": "概念", "aliases": []},
            {"name": "“剃刀”小队", "type": "组织", "aliases": []},
            {"name": "陶德·史密斯", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "追踪神秘术", "dst": "迷雾", "relation": "受扰于", "confidence": 0.8},
            {"src": "追踪神秘术", "dst": "罕见术法", "relation": "受扰于", "confidence": 0.8},
            {"src": "陶德·史密斯", "dst": "“剃刀”小队", "relation": "隶属", "confidence": 0.85},
        ],
    },
    "a2286637c42ede55": {
        "entities": [
            {"name": "受压迫工人", "type": "角色", "aliases": ["the oppressed workers"]},
            {"name": "一封信", "type": "物品", "aliases": ["a letter"]},
            {"name": "笔者", "type": "角色", "aliases": ["writer"]},
        ],
        "relations": [
            {"src": "笔者", "dst": "一封信", "relation": "撰写", "confidence": 0.8},
        ],
    },
    # ===== batch_midhigh_05 =====
    "596e17d02dc22c62": {
        "entities": [
            {"name": "船员队", "type": "组织", "aliases": ["the crew"]},
            {"name": "船长", "type": "角色", "aliases": ["the captain", "captain"]},
            {"name": "新成员", "type": "角色", "aliases": ["the new recruits"]},
        ],
        "relations": [
            {"src": "船长", "dst": "新成员", "relation": "挑剔", "confidence": 0.8},
        ],
    },
    "0bfc1f6426f3e42b": {
        "entities": [
            {"name": "护符", "type": "物品", "aliases": ["talisman"]},
            {"name": "试炼", "type": "事件", "aliases": ["the trials"]},
            {"name": "不对称核素-R", "type": "物品", "aliases": ["asymmetrical nuclide-R"]},
            {"name": "仓库", "type": "地点", "aliases": ["the warehouse"]},
            {"name": "药袋", "type": "角色", "aliases": ["medicine pocket"]},
            {"name": "乔纳森", "type": "角色", "aliases": ["Jonathan"]},
            {"name": "减压球", "type": "物品", "aliases": ["stress ball"]},
            {"name": "代理主任", "type": "角色", "aliases": ["substitute director"]},
        ],
        "relations": [
            {"src": "不对称核素-R", "dst": "仓库", "relation": "存放于", "confidence": 0.85},
            {"src": "乔纳森", "dst": "减压球", "relation": "取用", "confidence": 0.8},
        ],
    },
    "c8a7402e8e16d14d": {
        "entities": [
            {"name": "印象派", "type": "概念", "aliases": ["Impressionism"]},
            {"name": "新自由报", "type": "组织", "aliases": ["the New Free Press"]},
            {"name": "维也纳", "type": "地点", "aliases": ["Vienna"]},
            {"name": "少校", "type": "角色", "aliases": ["that major"]},
            {"name": "记者", "type": "角色", "aliases": ["The reporter"]},
            {"name": "频繁自杀", "type": "事件", "aliases": ["the frequent suicide"]},
        ],
        "relations": [
            {"src": "记者", "dst": "新自由报", "relation": "任职于", "confidence": 0.85},
            {"src": "记者", "dst": "频繁自杀", "relation": "讨论", "confidence": 0.8},
            {"src": "少校", "dst": "频繁自杀", "relation": "讨论", "confidence": 0.8},
            {"src": "频繁自杀", "dst": "维也纳", "relation": "发生于", "confidence": 0.8},
        ],
    },
    "fa80203afd266300": {
        "entities": [
            {"name": "未来历史的幽灵", "type": "现象", "aliases": ["The ghosts of future history"]},
            {"name": "孩童幽灵", "type": "现象", "aliases": ["the ghosts of little children"]},
            {"name": "被夷平的城市", "type": "事件", "aliases": ["Cities bombed to the ground"]},
            {"name": "满载人的列车", "type": "物品", "aliases": ["trains full of people"]},
        ],
        "relations": [],
    },
    "fc8cae35fd958c92": {
        "entities": [
            {"name": "国际程序法第78条", "type": "概念", "aliases": ["Article 78 of the International Law of Procedure"]},
            {"name": "国际程序法", "type": "概念", "aliases": ["the International Law of Procedure"]},
            {"name": "证词", "type": "概念", "aliases": ["testimony"]},
            {"name": "证人", "type": "角色", "aliases": ["witness"]},
        ],
        "relations": [
            {"src": "国际程序法第78条", "dst": "国际程序法", "relation": "出自", "confidence": 0.9},
        ],
    },
    "c8f65766f659b22b": {
        "entities": [
            {"name": "警员", "type": "角色", "aliases": ["police officer", "officer"]},
            {"name": "警长", "type": "角色", "aliases": ["the sergeant", "sergeant"]},
            {"name": "消防车", "type": "物品", "aliases": ["fire engine"]},
            {"name": "激光泡泡", "type": "物品", "aliases": ["The laser bubble"]},
            {"name": "人们的梦", "type": "概念", "aliases": ["people's dreams"]},
            {"name": "广场", "type": "地点", "aliases": ["the square"]},
            {"name": "泡泡", "type": "物品", "aliases": ["bubbles"]},
        ],
        "relations": [
            {"src": "警长", "dst": "消防车", "relation": "批准使用", "confidence": 0.85},
            {"src": "激光泡泡", "dst": "人们的梦", "relation": "反射", "confidence": 0.85},
            {"src": "激光泡泡", "dst": "广场", "relation": "致眠于", "confidence": 0.8},
        ],
    },
    "844c2021a7c5d7dc": {
        "entities": [
            {"name": "小家伙们", "type": "角色", "aliases": ["Critters"]},
            {"name": "闪亮破金库", "type": "地点", "aliases": ["the shiny crappy vault"]},
            {"name": "Ziz爆裂果", "type": "物品", "aliases": ["Ziz popping nuts"]},
            {"name": "父亲", "type": "角色", "aliases": ["Father"]},
            {"name": "伦敦之心", "type": "物品", "aliases": ["the Heart of London"]},
            {"name": "笨贼", "type": "角色", "aliases": ["that dim thief"]},
            {"name": "惊人蜗牛喷雾", "type": "物品", "aliases": ["the surprising slug spray"]},
            {"name": "安保室", "type": "地点", "aliases": ["the security room"]},
        ],
        "relations": [
            {"src": "父亲", "dst": "伦敦之心", "relation": "带来", "confidence": 0.85},
            {"src": "笨贼", "dst": "安保室", "relation": "闯入", "confidence": 0.85},
            {"src": "笨贼", "dst": "惊人蜗牛喷雾", "relation": "使用", "confidence": 0.8},
        ],
    },
    "1ff02f25636e5812": {
        "entities": [
            {"name": "蛙杯展", "type": "事件", "aliases": ["The Ribbit Cup exhibition", "Ribbit Cup exhibition"]},
            {"name": "新人类", "type": "组织", "aliases": ["New humans"]},
            {"name": "安保机器人", "type": "物品", "aliases": ["security robots"]},
            {"name": "警察", "type": "组织", "aliases": ["the police"]},
            {"name": "伦敦", "type": "地点", "aliases": ["London"]},
            {"name": "安保系统", "type": "概念", "aliases": ["the security systems"]},
        ],
        "relations": [
            {"src": "新人类", "dst": "蛙杯展", "relation": "承办", "confidence": 0.85},
            {"src": "安保系统", "dst": "警察", "relation": "部署于", "confidence": 0.8},
            {"src": "蛙杯展", "dst": "伦敦", "relation": "举办于", "confidence": 0.8},
        ],
    },
    "43c236f283f7bcd0": {
        "entities": [
            {"name": "喵喵喵管药剂", "type": "物品", "aliases": ["Mew Mew Mewtube potion"]},
            {"name": "喵喵喵", "type": "角色", "aliases": ["Mew Mew Mew"]},
            {"name": "喷洒系统", "type": "物品", "aliases": ["the spraying system"]},
            {"name": "泡泡", "type": "物品", "aliases": ["bubbles"]},
            {"name": "安全承诺书", "type": "物品", "aliases": ["the safety commitment statement"]},
            {"name": "展览", "type": "事件", "aliases": ["the exhibition"]},
        ],
        "relations": [
            {"src": "喵喵喵", "dst": "喷洒系统", "relation": "激活", "confidence": 0.85},
            {"src": "喷洒系统", "dst": "泡泡", "relation": "清除", "confidence": 0.85},
        ],
    },
    "9bd466e6184a0de9": {
        "entities": [
            {"name": "戴帽女孩", "type": "角色", "aliases": ["the girl with the hat"]},
            {"name": "白衣女孩", "type": "角色", "aliases": ["the girl in the white"]},
            {"name": "你的电影", "type": "物品", "aliases": ["your movie"]},
        ],
        "relations": [],
    },
    "2c10e689ff154770": {
        "entities": [
            {"name": "芝诺", "type": "角色", "aliases": ["Zeno"]},
            {"name": "城镇", "type": "地点", "aliases": ["the town"]},
            {"name": "小屋", "type": "地点", "aliases": ["This cabin"]},
            {"name": "营地", "type": "地点", "aliases": ["campsite"]},
        ],
        "relations": [
            {"src": "芝诺", "dst": "城镇", "relation": "关联", "confidence": 0.7},
        ],
    },
    "0d67d13992753164": {
        "entities": [
            {"name": "药膏", "type": "物品", "aliases": ["ointment"]},
        ],
        "relations": [],
    },
    "dd7bb54412efcb7a": {
        "entities": [
            {"name": "塔卡尔叔叔", "type": "角色", "aliases": ["Uncle Takal", "uncle", "Uncle"]},
            {"name": "地震", "type": "现象", "aliases": ["an earthquake", "the earthquake"]},
            {"name": "基金会", "type": "组织", "aliases": ["the foundation"]},
        ],
        "relations": [
            {"src": "地震", "dst": "基金会", "relation": "先于", "confidence": 0.7},
        ],
    },
    "deeddf653c2490c2": {
        "entities": [
            {"name": "爱琴海地区", "type": "地点", "aliases": ["the Aegean Sea region"]},
            {"name": "千年之声", "type": "组织", "aliases": ["The Voice of the Millennium"]},
            {"name": "主编", "type": "角色", "aliases": ["the chief editor"]},
            {"name": "这本书", "type": "物品", "aliases": ["this book"]},
            {"name": "巴比伦评论", "type": "组织", "aliases": ["The Babylonian review"]},
            {"name": "阿波罗星", "type": "概念", "aliases": ["the Apollo Star", "Apollo Star"]},
            {"name": "作者", "type": "角色", "aliases": ["the author"]},
            {"name": "黄金时代", "type": "概念", "aliases": ["the golden era"]},
        ],
        "relations": [
            {"src": "主编", "dst": "千年之声", "relation": "任职于", "confidence": 0.9},
            {"src": "主编", "dst": "这本书", "relation": "推荐", "confidence": 0.85},
            {"src": "巴比伦评论", "dst": "阿波罗星", "relation": "警示", "confidence": 0.8},
            {"src": "作者", "dst": "阿波罗星", "relation": "观测", "confidence": 0.85},
            {"src": "这本书", "dst": "黄金时代", "relation": "再现", "confidence": 0.8},
        ],
    },
    "9b938c75ca2d1a4a": {
        "entities": [
            {"name": "熟练消防队", "type": "组织", "aliases": ["a skilled fire brigade"]},
        ],
        "relations": [],
    },
    "9b89bfc3b35ad5d6": {
        "entities": [
            {"name": "俱乐部", "type": "组织", "aliases": ["the clubs"]},
            {"name": "赛事主办方", "type": "组织", "aliases": ["the hosts of the games"]},
            {"name": "赛事", "type": "事件", "aliases": ["the games"]},
            {"name": "药物滥用", "type": "概念", "aliases": ["Drug abuse"]},
            {"name": "人类体育产业", "type": "组织", "aliases": ["The sport industry of humans"]},
            {"name": "运动员", "type": "角色", "aliases": ["athletes"]},
            {"name": "灰姑娘的故事", "type": "概念", "aliases": ["Cinderella's story"]},
        ],
        "relations": [
            {"src": "人类体育产业", "dst": "运动员", "relation": "提供机会", "confidence": 0.85},
            {"src": "赛事主办方", "dst": "赛事", "relation": "主办", "confidence": 0.85},
            {"src": "运动员", "dst": "灰姑娘的故事", "relation": "喻指", "confidence": 0.7},
        ],
    },
    "b503beb67e18c147": {
        "entities": [
            {"name": "福行", "type": "事件", "aliases": ["the Fortune Walk"]},
            {"name": "桥跃", "type": "事件", "aliases": ["the Bridge Leap"]},
            {"name": "节庆动物", "type": "角色", "aliases": ["festive animals"]},
            {"name": "知希", "type": "角色", "aliases": ["Zhixi"]},
            {"name": "山羊", "type": "角色", "aliases": ["A goat"]},
            {"name": "驴子", "type": "角色", "aliases": ["donkeys"]},
            {"name": "马匹", "type": "角色", "aliases": ["horses"]},
        ],
        "relations": [
            {"src": "节庆动物", "dst": "福行", "relation": "用于", "confidence": 0.85},
            {"src": "节庆动物", "dst": "桥跃", "relation": "用于", "confidence": 0.85},
            {"src": "节庆动物", "dst": "知希", "relation": "庆贺", "confidence": 0.7},
            {"src": "马匹", "dst": "驴子", "relation": "替代", "confidence": 0.7},
        ],
    },
    "b5e600fde990d1f1": {
        "entities": [
            {"name": "罗曼司", "type": "角色", "aliases": ["Romance"]},
            {"name": "红新娘", "type": "角色", "aliases": ["the Red Bride"]},
            {"name": "主持人", "type": "角色", "aliases": ["the host"]},
            {"name": "摇篮曲", "type": "物品", "aliases": ["a lullaby"]},
            {"name": "那杯酒", "type": "物品", "aliases": ["the wine"]},
            {"name": "紫银发", "type": "概念", "aliases": ["purple and silver hair"]},
        ],
        "relations": [
            {"src": "主持人", "dst": "摇篮曲", "relation": "演唱", "confidence": 0.85},
        ],
    },
    "48226fc760044ebc": {
        "entities": [
            {"name": "分裂团体", "type": "组织", "aliases": ["secession groups"]},
            {"name": "分裂", "type": "概念", "aliases": ["the secession"]},
            {"name": "费解画作", "type": "物品", "aliases": ["inexplicable paintings"]},
            {"name": "神经质疯子", "type": "角色", "aliases": ["neurostenic lunatics"]},
            {"name": "尊贵支部", "type": "组织", "aliases": ["our venerable branch"]},
            {"name": "维也纳骑士", "type": "角色", "aliases": ["the knight of Vienna", "knight of Vienna", "the guard", "guard"]},
            {"name": "维也纳", "type": "地点", "aliases": ["Vienna"]},
            {"name": "神秘仪式", "type": "概念", "aliases": ["arcane ritual"]},
        ],
        "relations": [
            {"src": "分裂团体", "dst": "分裂", "relation": "主张", "confidence": 0.8},
            {"src": "维也纳骑士", "dst": "神秘仪式", "relation": "由...驱动", "confidence": 0.85},
            {"src": "维也纳骑士", "dst": "维也纳", "relation": "位于", "confidence": 0.85},
        ],
    },
    "d5dbedc2a543c4f4": {
        "entities": [
            {"name": "那片雾", "type": "现象", "aliases": ["the fog"]},
            {"name": "病人", "type": "角色", "aliases": ["Patients"]},
            {"name": "构造区", "type": "地点", "aliases": ["the structure zone"]},
            {"name": "药剂", "type": "物品", "aliases": ["the potion", "potion"]},
            {"name": "媒体", "type": "组织", "aliases": ["The press", "the press"]},
            {"name": "新闻发布会", "type": "事件", "aliases": ["a press conference"]},
            {"name": "救济", "type": "概念", "aliases": ["relief"]},
        ],
        "relations": [
            {"src": "病人", "dst": "药剂", "relation": "服用", "confidence": 0.85},
            {"src": "媒体", "dst": "新闻发布会", "relation": "要求", "confidence": 0.85},
        ],
    },
    "41db64ed8d56e602": {
        "entities": [
            {"name": "医院", "type": "地点", "aliases": ["hospitals"]},
            {"name": "生者与死者", "type": "概念", "aliases": ["the living and the dead ones"]},
            {"name": "瘾君子", "type": "角色", "aliases": ["addicts"]},
            {"name": "病狗", "type": "角色", "aliases": ["sick dogs"]},
            {"name": "香料", "type": "物品", "aliases": ["spices"]},
            {"name": "蜡烛", "type": "物品", "aliases": ["candles"]},
            {"name": "那场火", "type": "事件", "aliases": ["the fire"]},
            {"name": "通灵者", "type": "角色", "aliases": ["psychic"]},
            {"name": "先知", "type": "角色", "aliases": ["a prophet"]},
        ],
        "relations": [],
    },
    "23696480b37a0287": {
        "entities": [
            {"name": "司机", "type": "角色", "aliases": ["drivers"]},
            {"name": "飞行员", "type": "角色", "aliases": ["pilots"]},
            {"name": "引擎", "type": "物品", "aliases": ["engines"]},
            {"name": "转速表", "type": "物品", "aliases": ["the tachometer"]},
            {"name": "前轮转向", "type": "物品", "aliases": ["the nose wheel steering"]},
            {"name": "操纵杆", "type": "物品", "aliases": ["the joystick"]},
            {"name": "节流杆", "type": "物品", "aliases": ["the throttlelever", "throttlelever"]},
            {"name": "襟翼", "type": "物品", "aliases": ["the flaps"]},
            {"name": "卡皮坦", "type": "角色", "aliases": ["Capitan"]},
            {"name": "汽车", "type": "物品", "aliases": ["a car", "car"]},
            {"name": "飞行器", "type": "物品", "aliases": ["a flying machine", "flying machine"]},
            {"name": "这堆金属", "type": "物品", "aliases": ["this hunk of metal"]},
        ],
        "relations": [
            {"src": "汽车", "dst": "飞行器", "relation": "不同于", "confidence": 0.75},
        ],
    },
    "bb3ec3eb2f038406": {
        "entities": [
            {"name": "大自流盆地", "type": "地点", "aliases": ["the Great Artesian Basin"]},
            {"name": "迷雾森林", "type": "地点", "aliases": ["misty woods"]},
            {"name": "神秘学技能", "type": "概念", "aliases": ["the arcane skill"]},
            {"name": "柳小姐", "type": "角色", "aliases": ["miss Willow"]},
            {"name": "远古", "type": "时间", "aliases": ["ancient days"]},
            {"name": "薄雾", "type": "现象", "aliases": ["haze"]},
        ],
        "relations": [
            {"src": "柳小姐", "dst": "神秘学技能", "relation": "传授", "confidence": 0.8},
        ],
    },
    "91af9ad66172d0c4": {
        "entities": [
            {"name": "死老鼠", "type": "物品", "aliases": ["a dead mouse"]},
            {"name": "苹果", "type": "物品", "aliases": ["apples"]},
            {"name": "那些蛋", "type": "物品", "aliases": ["eggs"]},
            {"name": "老顽固", "type": "角色", "aliases": ["that boring old codger"]},
            {"name": "那碗粥", "type": "物品", "aliases": ["porridge"]},
            {"name": "蒸汽", "type": "现象", "aliases": ["steam"]},
            {"name": "幽灵", "type": "现象", "aliases": ["ghosts"]},
            {"name": "萨温节", "type": "事件", "aliases": ["the Samhain", "Samhain"]},
            {"name": "小马", "type": "角色", "aliases": ["the ponies"]},
            {"name": "诅咒", "type": "概念", "aliases": ["Curse"]},
        ],
        "relations": [
            {"src": "老顽固", "dst": "苹果", "relation": "给予", "confidence": 0.8},
            {"src": "老顽固", "dst": "那些蛋", "relation": "给予", "confidence": 0.8},
            {"src": "老顽固", "dst": "小马", "relation": "赌于", "confidence": 0.75},
            {"src": "幽灵", "dst": "萨温节", "relation": "出现于", "confidence": 0.7},
        ],
    },
    "46e9c82317cb20ca": {
        "entities": [
            {"name": "2401号选手", "type": "角色", "aliases": ["Competitor number 2401"]},
            {"name": "2402与2403号选手", "type": "角色", "aliases": ["Competitors 2402 and 2403"]},
            {"name": "更衣室", "type": "地点", "aliases": ["the locker room"]},
            {"name": "夏洛特", "type": "角色", "aliases": ["Charlotte"]},
            {"name": "挑战", "type": "事件", "aliases": ["the challenge"]},
            {"name": "场地", "type": "地点", "aliases": ["the floor"]},
        ],
        "relations": [
            {"src": "2401号选手", "dst": "场地", "relation": "进入", "confidence": 0.85},
            {"src": "2402与2403号选手", "dst": "更衣室", "relation": "等候于", "confidence": 0.85},
            {"src": "夏洛特", "dst": "挑战", "relation": "关联", "confidence": 0.7},
        ],
    },
}


def _norm(s: str) -> str:
    return (s or "").strip().lower().replace(" ", "").replace("\n", "").replace("\r", "")


def validate() -> int:
    bad = 0
    for h, d in RESULTS.items():
        pool = set()
        for e in d.get("entities") or []:
            nm = e.get("name") or ""
            pool.add(nm)
            pool |= set(e.get("aliases") or [])
        for r in d.get("relations") or []:
            if r.get("src") not in pool or r.get("dst") not in pool:
                print(f"[dangling] {h} {r.get('src')} -> {r.get('dst')}")
                bad += 1
    return bad


def landing() -> int:
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    text_by_hash = {c["hash"]: c.get("text", "") for c in corpus["chunks"]}
    bad = 0
    for h, d in RESULTS.items():
        ntext = _norm(text_by_hash.get(h, ""))
        if not ntext:
            print(f"[landing-missing-corpus] {h}")
            bad += 1
            continue
        for e in d.get("entities") or []:
            cands = [e.get("name") or ""] + list(e.get("aliases") or [])
            if not any(_norm(c) in ntext for c in cands):
                print(f"[landing-fail] {h} entity={e.get('name')} aliases={e.get('aliases')}")
                bad += 1
    return bad


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    v, m = validate(), landing()
    total_e = sum(len(d.get("entities") or []) for d in RESULTS.values())
    total_r = sum(len(d.get("relations") or []) for d in RESULTS.values())
    print(f"[validate] 块 {len(RESULTS)}，悬空 {v}，未落地 {m}")
    print(f"[stats] 实体 {total_e}，关系 {total_r}")
    if v or m:
        print("[ABORT] 存在悬空或未落地，未写盘")
        return 1
    if not args.apply:
        print("[dry-run] 加 --apply 写盘")
        return 0
    CACHE.mkdir(parents=True, exist_ok=True)
    for h, d in RESULTS.items():
        (CACHE / f"{h}.json").write_text(
            json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    print(f"[apply-missing-p36] 写入 {len(RESULTS)} 条")
    return 0


if __name__ == "__main__":
    sys.exit(main())
