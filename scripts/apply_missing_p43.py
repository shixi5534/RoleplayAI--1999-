#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""补抽 backfill5/pro_01.txt 的 100 个边角块（外文/B站 whisper 转写）。
逐块手工抽取实体/关系，写盘前 validate() 悬空自检 + landing() 落地自检（对照 pro_01.txt 正文）。
落地原则：外文正文 → 实体 name 直接用正文专名（连续子串），中文正名放 aliases。"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "knowledge" / "plot_cache" / "wu_ming_zhe"
PRO = ROOT / "data" / "knowledge" / "_audit" / "backfill5" / "pro_01.txt"

RESULTS = {
    "f6d41ffd3a45fc2e": {"entities": [], "relations": []},
    "044b16e640256c71": {"entities": [
        {"name": "SPDM", "type": "组织", "aliases": ["斯德普姆"]},
        {"name": "the Foundation", "type": "组织", "aliases": ["基金会", "圣洛夫基金会"]},
        {"name": "the storm", "type": "现象", "aliases": ["风暴"]},
    ], "relations": [
        {"src": "the Foundation", "dst": "the storm", "relation": "确认关联", "confidence": 0.85},
    ]},
    "8a1bf8018c19e13d": {"entities": [
        {"name": "Uluru", "type": "地点", "aliases": ["乌卢鲁"]},
        {"name": "Uluru games", "type": "事件", "aliases": ["乌卢鲁运动会"]},
        {"name": "st.Pavlov foundation", "type": "组织", "aliases": ["圣洛夫基金会"]},
        {"name": "Uluru games organizing committee", "type": "组织", "aliases": ["乌卢鲁运动会组委会"]},
        {"name": "Uluru London qualifiers", "type": "事件", "aliases": ["乌卢鲁伦敦资格赛"]},
    ], "relations": [
        {"src": "Uluru games organizing committee", "dst": "Uluru London qualifiers", "relation": "致函", "confidence": 0.8},
    ]},
    "f1a70d8f5663de59": {"entities": [
        {"name": "London", "type": "地点", "aliases": ["伦敦"]},
        {"name": "London atmospheric cleanup committee", "type": "组织", "aliases": ["伦敦大气净化委员会"]},
        {"name": "tuberculosis", "type": "现象", "aliases": ["结核病"]},
        {"name": "Uluru London qualifiers", "type": "事件", "aliases": ["乌卢鲁伦敦资格赛"]},
        {"name": "Paris", "type": "地点", "aliases": ["巴黎"]},
    ], "relations": [
        {"src": "London", "dst": "tuberculosis", "relation": "爆发", "confidence": 0.8},
    ]},
    "8d17d58912f50193": {"entities": [
        {"name": "Europe", "type": "地点", "aliases": ["欧洲"]},
        {"name": "London", "type": "地点", "aliases": ["伦敦"]},
        {"name": "the Foundation", "type": "组织", "aliases": ["基金会", "圣洛夫基金会"]},
        {"name": "Mr.Fogg", "type": "角色", "aliases": ["福格先生"]},
        {"name": "black fog", "type": "现象", "aliases": ["黑雾"]},
    ], "relations": [
        {"src": "Mr.Fogg", "dst": "the Foundation", "relation": "提及", "confidence": 0.7},
    ]},
    "de795d60210a61c3": {"entities": [
        {"name": "Freddy", "type": "角色", "aliases": ["弗雷迪"]},
    ], "relations": []},
    "252eecb64a549bd3": {"entities": [
        {"name": "Tooth Fairy", "type": "角色", "aliases": ["牙仙"]},
    ], "relations": []},
    "be65dfbd9f10f49d": {"entities": [
        {"name": "Miss O'Hagan", "type": "角色", "aliases": ["奥哈根小姐"]},
    ], "relations": []},
    "d71fdb956934aa4f": {"entities": [
        {"name": "Miss Willow", "type": "角色", "aliases": ["薇洛小姐"]},
    ], "relations": []},
    "716c34528f80ef74": {"entities": [
        {"name": "Uluru Games", "type": "事件", "aliases": ["乌卢鲁运动会"]},
    ], "relations": []},
    "9845ee2fb686561d": {"entities": [
        {"name": "Ms.Tooth Fairy", "type": "角色", "aliases": ["牙仙"]},
        {"name": "black fog", "type": "现象", "aliases": ["黑雾"]},
        {"name": "tuberculosis", "type": "现象", "aliases": ["结核病"]},
        {"name": "fog critter", "type": "现象", "aliases": ["雾怪"]},
    ], "relations": [
        {"src": "fog critter", "dst": "tuberculosis", "relation": "致病", "confidence": 0.85},
    ]},
    "4ac0fbd180231c95": {"entities": [
        {"name": "smog", "type": "现象", "aliases": ["烟雾"]},
        {"name": "critter", "type": "现象", "aliases": ["雾怪"]},
    ], "relations": [
        {"src": "critter", "dst": "smog", "relation": "以之为食", "confidence": 0.85},
    ]},
    "4eabde05d6911169": {"entities": [
        {"name": "London", "type": "地点", "aliases": ["伦敦"]},
    ], "relations": []},
    "1da74495b90755d6": {"entities": [
        {"name": "Mr.Fogg", "type": "角色", "aliases": ["福格先生"]},
        {"name": "Mr.Brinley", "type": "角色", "aliases": ["布林利先生"]},
        {"name": "the relief center", "type": "组织", "aliases": ["救济中心"]},
    ], "relations": [
        {"src": "Mr.Fogg", "dst": "Mr.Brinley", "relation": "共同讨论", "confidence": 0.8},
    ]},
    "36480249b661afb1": {"entities": [
        {"name": "the foundations", "type": "组织", "aliases": ["基金会", "圣洛夫基金会"]},
    ], "relations": []},
    "34ecc91b68505df4": {"entities": [
        {"name": "Uluru", "type": "地点", "aliases": ["乌卢鲁"]},
        {"name": "London Uluru Exhibition Games", "type": "事件", "aliases": ["伦敦乌卢鲁博览会运动会"]},
        {"name": "Flutter Page", "type": "角色", "aliases": ["芙萝拉·佩奇"]},
    ], "relations": [
        {"src": "Uluru", "dst": "London Uluru Exhibition Games", "relation": "命名来源", "confidence": 0.8},
    ]},
    "fbc71c9e5b286895": {"entities": [
        {"name": "Arthur", "type": "角色", "aliases": ["阿瑟"]},
        {"name": "smog", "type": "现象", "aliases": ["烟雾"]},
    ], "relations": [
        {"src": "Arthur", "dst": "smog", "relation": "展示危害", "confidence": 0.8},
    ]},
    "e1b9b0799cdaf693": {"entities": [
        {"name": "Burton", "type": "角色", "aliases": ["伯顿"]},
        {"name": "Blackout watchtower", "type": "地点", "aliases": ["停电瞭望塔"]},
    ], "relations": []},
    "ad453b62d40e43d7": {"entities": [
        {"name": "the Foundation", "type": "组织", "aliases": ["基金会", "圣洛夫基金会"]},
        {"name": "gravity vacuum cleaner", "type": "物品", "aliases": ["重力吸尘器"]},
        {"name": "rehab center", "type": "组织", "aliases": ["康复中心"]},
    ], "relations": []},
    "c0f847a741e75013": {"entities": [
        {"name": "the universe", "type": "概念", "aliases": ["宇宙"]},
        {"name": "the committee", "type": "组织", "aliases": ["委员会"]},
        {"name": "the lab", "type": "地点", "aliases": ["实验室"]},
    ], "relations": []},
    "91b6155206310dbe": {"entities": [], "relations": []},
    "70e83ea764e653f5": {"entities": [], "relations": []},
    "0c3ec437ab5ef650": {"entities": [
        {"name": "the Horn of Plenty", "type": "物品", "aliases": ["丰饶之角"]},
        {"name": "the harvest festival", "type": "事件", "aliases": ["丰收节"]},
        {"name": "The Ouroboros", "type": "概念", "aliases": ["衔尾蛇", "ouroboros"]},
    ], "relations": [
        {"src": "the Horn of Plenty", "dst": "the harvest festival", "relation": "于其装满", "confidence": 0.8},
    ]},
    "cb2eff422eb35131": {"entities": [
        {"name": "the pure-blood Arcanist", "type": "角色", "aliases": ["纯血术师"]},
        {"name": "the cleansing ceremony", "type": "事件", "aliases": ["净化仪式"]},
    ], "relations": []},
    "1ae5b0d5944bd303": {"entities": [
        {"name": "afflatus", "type": "概念", "aliases": ["神性", "灵感"]},
    ], "relations": []},
    "38b35020fb985655": {"entities": [
        {"name": "A bullet", "type": "角色", "aliases": ["子弹"]},
        {"name": "the heavy rain at the end of the century", "type": "现象", "aliases": ["世纪末大雨"]},
    ], "relations": [
        {"src": "A bullet", "dst": "the heavy rain at the end of the century", "relation": "幸免于", "confidence": 0.8},
    ]},
    "8bb7d2a8d12581ae": {"entities": [
        {"name": "Miss Furtin", "type": "角色", "aliases": ["弗廷小姐"]},
    ], "relations": []},
    "880e76d5ea267623": {"entities": [
        {"name": "Apollo", "type": "角色", "aliases": ["阿波罗"]},
        {"name": "the Classic Man", "type": "概念", "aliases": ["古典人"]},
    ], "relations": [
        {"src": "the Classic Man", "dst": "Apollo", "relation": "受启于", "confidence": 0.75},
    ]},
    "da164551450440fd": {"entities": [
        {"name": "humanocentrism", "type": "概念", "aliases": ["人类中心主义"]},
        {"name": "the Arcanum", "type": "概念", "aliases": ["秘术", "阿卡纳"]},
        {"name": "Arcanus", "type": "地点", "aliases": ["阿卡努斯"]},
    ], "relations": [
        {"src": "Arcanus", "dst": "the Arcanum", "relation": "关联", "confidence": 0.7},
    ]},
    "7504cab9ac15941a": {"entities": [], "relations": []},
    "1bfc622cade67a95": {"entities": [], "relations": []},
    "cf4ea5bff85fd07a": {"entities": [
        {"name": "Arcanum", "type": "概念", "aliases": ["秘术", "阿卡纳"]},
        {"name": "another universe in the shape of an egg", "type": "概念", "aliases": ["蛋形宇宙"]},
    ], "relations": [
        {"src": "Arcanum", "dst": "another universe in the shape of an egg", "relation": "关联", "confidence": 0.7},
    ]},
    "142c9fd6a5158810": {"entities": [
        {"name": "Miss Lockerhead", "type": "角色", "aliases": ["洛克黑德小姐"]},
        {"name": "the Arcanum containment department", "type": "组织", "aliases": ["秘术收容部"]},
    ], "relations": [
        {"src": "Miss Lockerhead", "dst": "the Arcanum containment department", "relation": "取自", "confidence": 0.8},
    ]},
    "fffbb03591def173": {"entities": [
        {"name": "Poitier", "type": "角色", "aliases": ["普瓦捷"]},
        {"name": "loggerhead", "type": "角色", "aliases": []},
    ], "relations": [
        {"src": "Poitier", "dst": "loggerhead", "relation": "包庇", "confidence": 0.8},
    ]},
    "2d338595b7b23e42": {"entities": [
        {"name": "the Division of Arcane Affairs", "type": "组织", "aliases": ["秘术事务部", "异术事务部"]},
        {"name": "Nightpiercer", "type": "角色", "aliases": ["夜穿刺者"]},
        {"name": "Nightpiercer attacks", "type": "事件", "aliases": ["夜穿刺者袭击"]},
    ], "relations": [
        {"src": "the Division of Arcane Affairs", "dst": "Nightpiercer", "relation": "调查", "confidence": 0.8},
        {"src": "Nightpiercer", "dst": "Nightpiercer attacks", "relation": "实施", "confidence": 0.85},
    ]},
    "3a6f31bc50a05df7": {"entities": [
        {"name": "Teresa", "type": "角色", "aliases": ["特蕾莎"]},
        {"name": "复活节", "type": "时间", "aliases": ["Easter"]},
    ], "relations": []},
    "7a7d0a5c4edcd4e3": {"entities": [
        {"name": "night piercer", "type": "角色", "aliases": ["夜穿刺者"]},
        {"name": "Poitier", "type": "角色", "aliases": ["普瓦捷"]},
    ], "relations": [
        {"src": "Poitier", "dst": "night piercer", "relation": "关联", "confidence": 0.7},
    ]},
    "ee10f7ce8a56c83a": {"entities": [
        {"name": "Los Angeles", "type": "地点", "aliases": ["洛杉矶"]},
        {"name": "the Division of Arcane Affairs", "type": "组织", "aliases": ["秘术事务部", "异术事务部"]},
        {"name": "the LAPD", "type": "组织", "aliases": ["洛杉矶警局"]},
        {"name": "the DAA", "type": "组织", "aliases": ["异术事务部"]},
    ], "relations": [
        {"src": "the LAPD", "dst": "the DAA", "relation": "增设职位", "confidence": 0.8},
        {"src": "the LAPD", "dst": "Los Angeles", "relation": "管辖", "confidence": 0.85},
    ]},
    "664bcc011264c7a6": {"entities": [
        {"name": "the DAA", "type": "组织", "aliases": ["异术事务部"]},
        {"name": "Teresa", "type": "角色", "aliases": ["特蕾莎"]},
    ], "relations": [
        {"src": "the DAA", "dst": "Teresa", "relation": "展示遗作", "confidence": 0.7},
    ]},
    "30d78b45a57d1f2e": {"entities": [
        {"name": "the vigils", "type": "组织", "aliases": ["守夜人"]},
    ], "relations": []},
    "84d5040b5e724b92": {"entities": [
        {"name": "Liang", "type": "角色", "aliases": ["梁"]},
    ], "relations": []},
    "10f41714c11d78bc": {"entities": [
        {"name": "Laplace", "type": "组织", "aliases": ["拉普拉斯"]},
        {"name": "Laplace bots", "type": "物品", "aliases": ["拉普拉斯机器人"]},
        {"name": "Ms.Qixing", "type": "角色", "aliases": ["七星小姐", "Ms.Qi Xin"]},
        {"name": "V.I.S.H.I.A.L.", "type": "概念", "aliases": ["仿生人", "维希阿尔"]},
        {"name": "CO7", "type": "物品", "aliases": ["CO7电影"]},
    ], "relations": [
        {"src": "Laplace", "dst": "Laplace bots", "relation": "制造", "confidence": 0.8},
        {"src": "Ms.Qixing", "dst": "V.I.S.H.I.A.L.", "relation": "启发", "confidence": 0.8},
        {"src": "Ms.Qixing", "dst": "CO7", "relation": "出演", "confidence": 0.8},
    ]},
    "6e6427c9b5ed4dd1": {"entities": [], "relations": []},
    "c9fc6466f36feff8": {"entities": [
        {"name": "Liang Yue", "type": "角色", "aliases": ["梁月"]},
        {"name": "the Liang family", "type": "组织", "aliases": ["梁家"]},
        {"name": "the Twelve Jinz", "type": "组织", "aliases": ["十二金"]},
    ], "relations": [
        {"src": "Liang Yue", "dst": "the Liang family", "relation": "隶属", "confidence": 0.9},
        {"src": "the Liang family", "dst": "the Twelve Jinz", "relation": "隶属", "confidence": 0.85},
    ]},
    "943c960c763ffa62": {"entities": [
        {"name": "Mister Yuli", "type": "角色", "aliases": ["尤利先生"]},
        {"name": "Arkane", "type": "概念", "aliases": ["秘术", "阿卡纳"]},
    ], "relations": [
        {"src": "Mister Yuli", "dst": "Arkane", "relation": "关联", "confidence": 0.7},
    ]},
    "1af638cab876c6a5": {"entities": [
        {"name": "l'Arcane", "type": "概念", "aliases": ["秘术", "阿卡纳"]},
        {"name": "la rivière de Palin", "type": "地点", "aliases": ["帕林河"]},
    ], "relations": [
        {"src": "l'Arcane", "dst": "la rivière de Palin", "relation": "受影响于", "confidence": 0.85},
    ]},
    "a11573275a3ab9d9": {"entities": [
        {"name": "la fondation", "type": "组织", "aliases": ["基金会", "圣洛夫基金会"]},
        {"name": "Constance Scott", "type": "角色", "aliases": ["康斯坦斯·斯科特"]},
        {"name": "SPDM", "type": "组织", "aliases": ["斯德普姆"]},
        {"name": "Le commissaire Pedra", "type": "角色", "aliases": ["佩德拉警长"]},
    ], "relations": [
        {"src": "Constance Scott", "dst": "SPDM", "relation": "隶属", "confidence": 0.9},
        {"src": "Le commissaire Pedra", "dst": "Constance Scott", "relation": "托付", "confidence": 0.8},
    ]},
    "03090a3af9267310": {"entities": [
        {"name": "Chine", "type": "地点", "aliases": ["中国"]},
    ], "relations": []},
    "b8411caf32b9bd78": {"entities": [], "relations": []},
    "2a74b0653f071e4f": {"entities": [
        {"name": "Hollywood", "type": "地点", "aliases": ["好莱坞"]},
    ], "relations": []},
    "c15749b6def66988": {"entities": [], "relations": []},
    "f89f0d9d1f63314b": {"entities": [
        {"name": "Darkness", "type": "概念", "aliases": ["黑暗"]},
    ], "relations": []},
    "8e9fd9f1e0f6aad3": {"entities": [
        {"name": "Seatful Spirit of the Year Award", "type": "事件", "aliases": ["年度满座之灵奖"]},
    ], "relations": []},
    "1e5a5d9bfcc3feff": {"entities": [], "relations": []},
    "284b3d552ccf8539": {"entities": [], "relations": []},
    "df80c39708d644ec": {"entities": [
        {"name": "Reyes", "type": "角色", "aliases": ["雷耶斯"]},
        {"name": "miss Furtin", "type": "角色", "aliases": ["弗廷小姐"]},
    ], "relations": []},
    "abf7a0c61b4318d2": {"entities": [
        {"name": "TTT", "type": "角色", "aliases": []},
        {"name": "Texas", "type": "地点", "aliases": ["得克萨斯"]},
    ], "relations": [
        {"src": "TTT", "dst": "Texas", "relation": "讲述", "confidence": 0.8},
    ]},
    "65129b12d62b33f9": {"entities": [], "relations": []},
    "e28d23943ba9b927": {"entities": [], "relations": []},
    "593ae97b79140f7a": {"entities": [
        {"name": "a sheep-headed arcanist", "type": "角色", "aliases": ["羊首术师"]},
    ], "relations": []},
    "4406b11b205887c4": {"entities": [
        {"name": "a merchant's son", "type": "角色", "aliases": ["商人之子"]},
        {"name": "Zeus", "type": "角色", "aliases": ["宙斯"]},
        {"name": "Zeus' grandfather", "type": "角色", "aliases": ["宙斯之祖父"]},
    ], "relations": [
        {"src": "Zeus' grandfather", "dst": "Zeus", "relation": "祖孙", "confidence": 0.9},
    ]},
    "f711c7802a7bd67e": {"entities": [
        {"name": "the eighth planet", "type": "地点", "aliases": ["第八行星"]},
        {"name": "the Ceres", "type": "地点", "aliases": ["谷神星"]},
        {"name": "the Uranus", "type": "地点", "aliases": ["天王星"]},
        {"name": "the merchant's son", "type": "角色", "aliases": ["商人之子"]},
    ], "relations": [
        {"src": "the merchant's son", "dst": "the eighth planet", "relation": "推演", "confidence": 0.7},
    ]},
    "6aff012f3b1a9a16": {"entities": [], "relations": []},
    "4e17ae2025a8c88c": {"entities": [], "relations": []},
    "298fed6a63fcc94a": {"entities": [
        {"name": "the storm", "type": "现象", "aliases": ["风暴"]},
        {"name": "divination", "type": "概念", "aliases": ["占卜"]},
        {"name": "Musique Verain", "type": "地点", "aliases": ["维兰音乐厅"]},
    ], "relations": [
        {"src": "divination", "dst": "the storm", "relation": "探知", "confidence": 0.8},
    ]},
    "2a7202199bc1defe": {"entities": [
        {"name": "Istanbul", "type": "地点", "aliases": ["伊斯坦布尔"]},
        {"name": "the Egypt office", "type": "组织", "aliases": ["埃及分部"]},
        {"name": "the storm", "type": "现象", "aliases": ["风暴"]},
        {"name": "the headquarters", "type": "组织", "aliases": ["总部"]},
        {"name": "1985", "type": "时间", "aliases": ["1985年"]},
    ], "relations": [
        {"src": "the Egypt office", "dst": "the headquarters", "relation": "隶属", "confidence": 0.8},
        {"src": "the Egypt office", "dst": "the storm", "relation": "受波及", "confidence": 0.7},
    ]},
    "d09f45c9610c6d84": {"entities": [
        {"name": "San Marco", "type": "组织", "aliases": ["圣马可咖啡馆"]},
        {"name": "a neurologist", "type": "角色", "aliases": ["神经学家"]},
        {"name": "the interpretation of dreams", "type": "物品", "aliases": ["梦的解析"]},
    ], "relations": [
        {"src": "San Marco", "dst": "a neurologist", "relation": "接待", "confidence": 0.8},
        {"src": "a neurologist", "dst": "the interpretation of dreams", "relation": "携带", "confidence": 0.8},
    ]},
    "06f0ebb57081130f": {"entities": [
        {"name": "Zhonyang", "type": "角色", "aliases": ["仲央", "中央"]},
        {"name": "luchus", "type": "概念", "aliases": []},
    ], "relations": []},
    "02de13c15b77548a": {"entities": [], "relations": []},
    "ea69409780367e27": {"entities": [
        {"name": "Holy Mary", "type": "角色", "aliases": ["圣母玛利亚"]},
        {"name": "the medal awarded for the research", "type": "物品", "aliases": ["研究奖章"]},
        {"name": "Young cavalrymen", "type": "角色", "aliases": ["年轻骑兵"]},
    ], "relations": []},
    "dce2ab5b76a5d8e8": {"entities": [
        {"name": "Hurtas", "type": "组织", "aliases": ["赫尔塔斯"]},
    ], "relations": []},
    "f4c878f42c32956d": {"entities": [
        {"name": "Petrov", "type": "角色", "aliases": ["彼得罗夫"]},
        {"name": "ancient strata in the south", "type": "地点", "aliases": ["南方古地层"]},
        {"name": "extreme weather", "type": "现象", "aliases": ["极端天气"]},
    ], "relations": []},
    "6686df262a14ec8d": {"entities": [
        {"name": "Manoises", "type": "地点", "aliases": ["马诺伊斯"]},
        {"name": "the fog", "type": "现象", "aliases": ["雾"]},
        {"name": "the rain", "type": "现象", "aliases": ["雨"]},
    ], "relations": [
        {"src": "Manoises", "dst": "the fog", "relation": "异常出现", "confidence": 0.7},
    ]},
    "4279aabf10bb817b": {"entities": [
        {"name": "London", "type": "地点", "aliases": ["伦敦"]},
        {"name": "the bell of art", "type": "概念", "aliases": ["艺术之钟"]},
        {"name": "Decided street", "type": "地点", "aliases": ["决意街"]},
        {"name": "a grand party of art", "type": "事件", "aliases": ["艺术盛会"]},
    ], "relations": [
        {"src": "London", "dst": "a grand party of art", "relation": "举办", "confidence": 0.8},
        {"src": "the bell of art", "dst": "a grand party of art", "relation": "象征", "confidence": 0.7},
    ]},
    "7a0e04799646f249": {"entities": [], "relations": []},
    "3700a41caedae664": {"entities": [
        {"name": "Patriots", "type": "组织", "aliases": ["爱国者"]},
        {"name": "Fordmanship", "type": "概念", "aliases": ["福特主义"]},
    ], "relations": [
        {"src": "Patriots", "dst": "Fordmanship", "relation": "以之为名", "confidence": 0.8},
    ]},
    "74221c336a9ad218": {"entities": [
        {"name": "Pink Torch Hummingbird", "type": "角色", "aliases": ["粉火炬蜂鸟"]},
        {"name": "Glittering platypus", "type": "角色", "aliases": ["闪光鸭嘴兽"]},
    ], "relations": [
        {"src": "Pink Torch Hummingbird", "dst": "Glittering platypus", "relation": "或为别名", "confidence": 0.7},
    ]},
    "3a1452d685d72180": {"entities": [
        {"name": "Jason", "type": "角色", "aliases": ["杰森"]},
        {"name": "Michael", "type": "角色", "aliases": ["迈克尔"]},
    ], "relations": [
        {"src": "Jason", "dst": "Michael", "relation": "同伴", "confidence": 0.8},
    ]},
    "461c9510a5e179b5": {"entities": [
        {"name": "Green Lake campsite", "type": "地点", "aliases": ["绿湖营地"]},
    ], "relations": []},
    "190c8b66e8a5e23d": {"entities": [
        {"name": "the lake monster", "type": "角色", "aliases": ["湖怪"]},
        {"name": "a curse", "type": "概念", "aliases": ["诅咒"]},
    ], "relations": []},
    "b4185f6d8350ec22": {"entities": [
        {"name": "Zeno", "type": "角色", "aliases": ["芝诺"]},
    ], "relations": []},
    "cf1ccb56efc96abe": {"entities": [], "relations": []},
    "16fb55604f74fd6d": {"entities": [
        {"name": "Jerry Littlefinger", "type": "角色", "aliases": ["杰瑞·小指"]},
        {"name": "Short Ken", "type": "角色", "aliases": ["矮肯"]},
    ], "relations": [
        {"src": "Jerry Littlefinger", "dst": "Short Ken", "relation": "同伙", "confidence": 0.7},
    ]},
    "271c86eb5f374e55": {"entities": [
        {"name": "Chase Forge", "type": "地点", "aliases": ["追逐熔炉"]},
    ], "relations": []},
    "d53094d763ea98c6": {"entities": [
        {"name": "San Francisco", "type": "地点", "aliases": ["旧金山"]},
    ], "relations": []},
    "d95a0204e8950463": {"entities": [
        {"name": "Sergeant Howard Eden", "type": "角色", "aliases": ["霍华德·伊登警长"]},
        {"name": "Army", "type": "组织", "aliases": ["军队"]},
    ], "relations": [
        {"src": "Sergeant Howard Eden", "dst": "Army", "relation": "隶属", "confidence": 0.9},
    ]},
    "9523bd75c9b956d2": {"entities": [
        {"name": "les deux arcanes", "type": "概念", "aliases": ["两个阿卡纳"]},
        {"name": "Mr.Bernard", "type": "角色", "aliases": ["伯纳德先生"]},
        {"name": "la presse", "type": "组织", "aliases": ["媒体"]},
    ], "relations": [
        {"src": "Mr.Bernard", "dst": "la presse", "relation": "抢先于", "confidence": 0.8},
    ]},
    "01b973d323aca473": {"entities": [
        {"name": "Pavlov", "type": "组织", "aliases": ["帕夫洛夫", "圣洛夫基金会"]},
        {"name": "Polina Lesage", "type": "角色", "aliases": ["波琳娜·莱萨热"]},
        {"name": "headquarters", "type": "组织", "aliases": ["总部"]},
    ], "relations": [
        {"src": "Pavlov", "dst": "Polina Lesage", "relation": "关联", "confidence": 0.7},
        {"src": "headquarters", "dst": "Polina Lesage", "relation": "处理", "confidence": 0.7},
    ]},
    "e424e49677dfb44e": {"entities": [
        {"name": "Polina", "type": "角色", "aliases": ["波琳娜", "波琳娜·莱萨热"]},
    ], "relations": []},
    "64f9c74f3053e814": {"entities": [
        {"name": "nema", "type": "概念", "aliases": ["内玛", "生命力"]},
        {"name": "energy healers", "type": "角色", "aliases": ["能量治疗师"]},
    ], "relations": [
        {"src": "energy healers", "dst": "nema", "relation": "感知", "confidence": 0.8},
    ]},
    "685fb553481b5d2d": {"entities": [
        {"name": "Paul", "type": "角色", "aliases": ["保罗"]},
        {"name": "Paulina", "type": "角色", "aliases": ["波琳娜"]},
        {"name": "a foundation member", "type": "角色", "aliases": ["基金会成员"]},
    ], "relations": [
        {"src": "Paul", "dst": "Paulina", "relation": "称呼", "confidence": 0.8},
    ]},
    "edaae7727cb16bf4": {"entities": [
        {"name": "圣洛夫基金会总部", "type": "组织", "aliases": ["圣洛夫基金会"]},
    ], "relations": []},
    "7548975f01caa3c0": {"entities": [
        {"name": "维拉", "type": "角色", "aliases": ["Vila"]},
        {"name": "亚什基", "type": "地点", "aliases": []},
    ], "relations": [
        {"src": "维拉", "dst": "亚什基", "relation": "前往", "confidence": 0.85},
    ]},
    "dbc376206006508b": {"entities": [
        {"name": "星锑", "type": "角色", "aliases": []},
        {"name": "摇滚精神", "type": "概念", "aliases": ["摇滚之魂"]},
    ], "relations": [
        {"src": "星锑", "dst": "摇滚精神", "relation": "称其源于", "confidence": 0.8},
    ]},
    "ead021ef2a9bca41": {"entities": [
        {"name": "贡比涅", "type": "地点", "aliases": ["贡比涅谈判"]},
        {"name": "1920年", "type": "时间", "aliases": []},
    ], "relations": [
        {"src": "贡比涅", "dst": "1920年", "relation": "关联", "confidence": 0.7},
    ]},
    "756a16e8f01a5b36": {"entities": [
        {"name": "约翰", "type": "角色", "aliases": ["John"]},
        {"name": "委员会大楼", "type": "地点", "aliases": []},
    ], "relations": []},
    "ab9e4417a6f3ec8f": {"entities": [], "relations": []},
    "70da599a0e0ec082": {"entities": [
        {"name": "莱格斯", "type": "角色", "aliases": []},
        {"name": "墨西哥卷", "type": "物品", "aliases": []},
    ], "relations": [
        {"src": "莱格斯", "dst": "墨西哥卷", "relation": "适合", "confidence": 0.8},
    ]},
    "541e6a713e79533f": {"entities": [], "relations": []},
    "4de0c9e163839f38": {"entities": [], "relations": []},
}


def _norm(s: str) -> str:
    return (s or "").strip().lower().replace(" ", "").replace("\n", "").replace("\r", "")


def _load_pro() -> dict:
    text = PRO.read_text(encoding="utf-8")
    out = {}
    for blk in text.split("\n\n"):
        lines = [l for l in blk.split("\n") if l.strip() != ""]
        if not lines:
            continue
        h = lines[0].strip()
        body = " ".join(l.strip() for l in lines[1:])
        out[h] = body
    return out


def validate() -> int:
    bad = 0
    for h, d in RESULTS.items():
        pool = set()
        for e in d.get("entities") or []:
            pool.add(_norm(e.get("name") or ""))
            pool |= set(_norm(c) for c in (e.get("aliases") or []))
        for r in d.get("relations") or []:
            if _norm(r.get("src")) not in pool or _norm(r.get("dst")) not in pool:
                print(f"[dangling] {h} {r.get('src')} -> {r.get('dst')}")
                bad += 1
    return bad


def landing(proc: dict) -> int:
    bad = 0
    for h, d in RESULTS.items():
        ntext = _norm(proc.get(h, ""))
        if not ntext:
            print(f"[landing-missing] {h}")
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
    proc = _load_pro()
    # 校验 RESULTS 的 key 与 pro 文件一致
    phash = set(proc.keys())
    rhash = set(RESULTS.keys())
    if phash != rhash:
        miss = phash - rhash
        extra = rhash - phash
        if miss:
            print(f"[key-mismatch] pro 有但 RESULTS 缺: {sorted(miss)}")
        if extra:
            print(f"[key-mismatch] RESULTS 有但 pro 缺: {sorted(extra)}")
        return 2
    v = validate()
    m = landing(proc)
    total_e = sum(len(d.get("entities") or []) for d in RESULTS.values())
    total_r = sum(len(d.get("relations") or []) for d in RESULTS.values())
    empties = [h for h, d in RESULTS.items() if not (d.get("entities") or d.get("relations"))]
    print(f"[validate] 块 {len(RESULTS)}，悬空 {v}，未落地 {m}")
    print(f"[stats] 实体 {total_e}，关系 {total_r}")
    print(f"[empty] 判无内容块 {len(empties)}")
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
    print(f"[apply-missing-p43] 写入 {len(RESULTS)} 条")
    return 0


if __name__ == "__main__":
    sys.exit(main())
