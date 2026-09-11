# -*- coding: utf-8 -*-
"""补抽 408 块空抽取中的第 2 批（67 块，云端人工抽取）。同 apply_empty_p1.py。"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from roleplay.config import get_settings  # noqa: E402

NOOP: list[str] = [
    "1547dd26fbd82116",  # 德语一战独白，无专名
    "9d4d34d787c2f8e5",  # 德语一战独白，无专名
    "56a9d8c526b54f38",  # 车厢闲聊（boss / big but slow），无专名
]

RESULTS: dict[str, dict] = {
    "4b7c71eda40fec96": {
        "entities": [
            {"name": "圣洛夫基金会", "type": "组织", "aliases": ["Foundation"]},
            {"name": "罗斯海", "type": "地点", "aliases": ["Ross Sea"]},
            {"name": "研究者", "type": "角色", "aliases": ["researcher"]},
        ],
        "relations": [
            {"src": "圣洛夫基金会", "dst": "罗斯海", "relation": "舰队驶来", "confidence": 0.9},
        ],
    },
    "25224a7dab749724": {
        "entities": [
            {"name": "拉普拉斯", "type": "组织", "aliases": ["Laplace"]},
            {"name": "奇美拉", "type": "概念", "aliases": ["chimera"]},
            {"name": "咒文", "type": "概念", "aliases": ["incantations"]},
        ],
        "relations": [
            {"src": "拉普拉斯", "dst": "奇美拉", "relation": "制造", "confidence": 0.7},
            {"src": "奇美拉", "dst": "咒文", "relation": "免疫", "confidence": 0.9},
        ],
    },
    "902a9a7b14a16c43": {
        "entities": [
            {"name": "不列颠", "type": "地点", "aliases": ["Britain"]},
            {"name": "重塑之手", "type": "组织", "aliases": ["menace", "Menace", "Manus"]},
            {"name": "圣洛夫基金会", "type": "组织", "aliases": ["foundation", "Foundation"]},
            {"name": "奥秘", "type": "概念", "aliases": ["Arkanum", "Arcanum"]},
            {"name": "秘术师", "type": "概念", "aliases": ["Arkanus"]},
            {"name": "人类士兵", "type": "组织", "aliases": ["Human soldiers"]},
        ],
        "relations": [
            {"src": "不列颠", "dst": "奥秘", "relation": "依赖", "confidence": 0.8},
            {"src": "人类士兵", "dst": "秘术师", "relation": "掩护撤退", "confidence": 0.9},
            {"src": "重塑之手", "dst": "圣洛夫基金会", "relation": "争夺忠诚", "confidence": 0.7},
        ],
    },
    "6be302389aab06e8": {
        "entities": [
            {"name": "米安尼", "type": "地点", "aliases": ["Mianni"]},
            {"name": "疏散", "type": "事件", "aliases": ["evacuation"]},
            {"name": "暴雨", "type": "事件", "aliases": ["Storm", "The Storm"]},
            {"name": "秘术能量", "type": "概念", "aliases": ["arcane energy levels"]},
        ],
        "relations": [
            {"src": "暴雨", "dst": "秘术能量", "relation": "预测依据", "confidence": 0.8},
            {"src": "疏散", "dst": "米安尼", "relation": "进行于", "confidence": 0.8},
        ],
    },
    "972fb3c2772fb777": {
        "entities": [
            {"name": "APPLe", "type": "角色", "aliases": ["Apple", "苹果"]},
            {"name": "希腊文化", "type": "概念", "aliases": ["Greek stuff"]},
        ],
        "relations": [
            {"src": "APPLe", "dst": "希腊文化", "relation": "热衷", "confidence": 0.9},
        ],
    },
    "835cc4a2a75b343b": {
        "entities": [
            {"name": "雅典人", "type": "概念", "aliases": ["Athelians"]},
            {"name": "狄俄尼索斯节", "type": "事件", "aliases": ["Dionysia"]},
            {"name": "悲剧", "type": "概念", "aliases": ["Tragedy"]},
            {"name": "文明", "type": "概念", "aliases": ["civilization"]},
        ],
        "relations": [
            {"src": "雅典人", "dst": "狄俄尼索斯节", "relation": "举办", "confidence": 0.9},
            {"src": "狄俄尼索斯节", "dst": "悲剧", "relation": "上演", "confidence": 0.8},
        ],
    },
    "1ce831904bf0e305": {
        "entities": [
            {"name": "荷马史诗", "type": "物品", "aliases": ["Homer's epic"]},
            {"name": "斯库拉", "type": "概念", "aliases": ["Scylla"]},
            {"name": "奥德修斯", "type": "角色", "aliases": ["Odysseus"]},
            {"name": "特洛伊战争", "type": "事件", "aliases": ["Trojan War"]},
            {"name": "波吕斐摩斯", "type": "角色",
             "aliases": ["Cyclops Polyphemus", "Cyclops"]},
            {"name": "埃俄罗斯", "type": "角色", "aliases": ["Aeolus", "Wind Ruler Aeolus"]},
            {"name": "喀耳刻", "type": "角色",
             "aliases": ["Circe", "Master Sorceress Circe"]},
            {"name": "塞壬", "type": "概念", "aliases": ["Siren"]},
        ],
        "relations": [
            {"src": "荷马史诗", "dst": "斯库拉", "relation": "记载", "confidence": 0.9},
            {"src": "斯库拉", "dst": "奥德修斯", "relation": "阻挡", "confidence": 0.9},
            {"src": "波吕斐摩斯", "dst": "奥德修斯", "relation": "磨难", "confidence": 0.8},
            {"src": "埃俄罗斯", "dst": "奥德修斯", "relation": "磨难", "confidence": 0.8},
            {"src": "喀耳刻", "dst": "奥德修斯", "relation": "磨难", "confidence": 0.8},
            {"src": "特洛伊战争", "dst": "奥德修斯", "relation": "归乡受阻", "confidence": 0.8},
        ],
    },
    "ba91c7ba34a0af96": {
        "entities": [
            {"name": "芝诺军备学院", "type": "组织", "aliases": ["Zeno", "Xeno"]},
            {"name": "骑兵队", "type": "组织", "aliases": ["cavalry", "Cavalry"]},
            {"name": "匪帮", "type": "组织", "aliases": ["bandits", "Brigands"]},
            {"name": "麦田", "type": "地点", "aliases": ["fields"]},
            {"name": "粮食", "type": "物品", "aliases": ["grain", "food"]},
        ],
        "relations": [
            {"src": "骑兵队", "dst": "芝诺军备学院", "relation": "隶属", "confidence": 0.9},
            {"src": "麦田", "dst": "粮食", "relation": "无收成", "confidence": 0.7},
            {"src": "匪帮", "dst": "麦田", "relation": "盘踞", "confidence": 0.7},
        ],
    },
    "85a76d4ad0de781d": {
        "entities": [
            {"name": "阿德勒", "type": "角色", "aliases": ["Adler", "Researcher Adler"]},
            {"name": "K2", "type": "地点", "aliases": ["Mount Godwin-Austin"]},
            {"name": "珠峰", "type": "地点", "aliases": ["Mount Everest", "Everest"]},
        ],
        "relations": [
            {"src": "K2", "dst": "珠峰", "relation": "仅次于", "confidence": 0.9},
            {"src": "阿德勒", "dst": "K2", "relation": "提及", "confidence": 0.7},
        ],
    },
    "c8d07eab8a8f3972": {
        "entities": [
            {"name": "圣洛夫基金会", "type": "组织", "aliases": ["Foundation"]},
            {"name": "圣洛夫基金会武装部队", "type": "组织",
             "aliases": ["Foundation Armed Forces"]},
            {"name": "乔治五世海岸", "type": "地点",
             "aliases": ["King George of the Fifth Coast"]},
            {"name": "维多利亚地", "type": "地点", "aliases": ["Victoria Land"]},
            {"name": "直升机", "type": "物品", "aliases": ["helicopter"]},
        ],
        "relations": [
            {"src": "圣洛夫基金会", "dst": "圣洛夫基金会武装部队", "relation": "统辖",
             "confidence": 0.9},
            {"src": "圣洛夫基金会武装部队", "dst": "乔治五世海岸", "relation": "登陆",
             "confidence": 0.7},
            {"src": "维多利亚地", "dst": "乔治五世海岸", "relation": "邻近",
             "confidence": 0.7},
        ],
    },
    "bf11cd77076bc6ca": {
        "entities": [
            {"name": "咖啡馆", "type": "地点", "aliases": ["cafe"]},
            {"name": "咖啡师", "type": "角色", "aliases": ["barista"]},
            {"name": "浓缩咖啡", "type": "物品", "aliases": ["espresso", "Java"]},
        ],
        "relations": [
            {"src": "咖啡师", "dst": "咖啡馆", "relation": "供职", "confidence": 0.8},
            {"src": "咖啡馆", "dst": "浓缩咖啡", "relation": "供应", "confidence": 0.8},
        ],
    },
    "95976f804f142273": {
        "entities": [
            {"name": "守夜团", "type": "组织", "aliases": ["Vigils", "vigils"]},
            {"name": "帮派", "type": "组织", "aliases": ["gangs"]},
            {"name": "亡灵节", "type": "事件", "aliases": ["Dia de los fieles difuntos"]},
            {"name": "谋杀案", "type": "事件", "aliases": ["murders"]},
            {"name": "城市", "type": "地点", "aliases": ["city"]},
        ],
        "relations": [
            {"src": "亡灵节", "dst": "城市", "relation": "举行于", "confidence": 0.8},
            {"src": "谋杀案", "dst": "城市", "relation": "发生于", "confidence": 0.8},
            {"src": "守夜团", "dst": "谋杀案", "relation": "调查", "confidence": 0.7},
        ],
    },
    "617b01c6c3c83e6c": {
        "entities": [
            {"name": "纳西索斯", "type": "角色", "aliases": ["Narcissus"]},
            {"name": "壁画", "type": "物品", "aliases": ["fresco"]},
            {"name": "水上竞技会", "type": "事件", "aliases": ["games"]},
            {"name": "享乐主义", "type": "概念", "aliases": ["hedonism"]},
            {"name": "评委", "type": "角色", "aliases": ["judges"]},
        ],
        "relations": [
            {"src": "纳西索斯", "dst": "水上竞技会", "relation": "预告", "confidence": 0.8},
            {"src": "壁画", "dst": "水上竞技会", "relation": "描绘", "confidence": 0.7},
            {"src": "水上竞技会", "dst": "享乐主义", "relation": "重构", "confidence": 0.7},
            {"src": "评委", "dst": "水上竞技会", "relation": "评判", "confidence": 0.8},
        ],
    },
    "dc129ab6f5adc9f5": {
        "entities": [
            {"name": "总部", "type": "地点", "aliases": ["headquarters", "Headquarters"]},
            {"name": "布宜诺斯艾利斯", "type": "地点", "aliases": ["Buenos Aires"]},
            {"name": "阿根廷政府", "type": "组织", "aliases": ["Argentine government"]},
            {"name": "监狱", "type": "地点", "aliases": ["prison"]},
            {"name": "许可证", "type": "物品", "aliases": ["permit"]},
        ],
        "relations": [
            {"src": "总部", "dst": "布宜诺斯艾利斯", "relation": "通知分部",
             "confidence": 0.9},
            {"src": "阿根廷政府", "dst": "许可证", "relation": "签发", "confidence": 0.9},
            {"src": "总部", "dst": "监狱", "relation": "申请进入", "confidence": 0.7},
        ],
    },
    "d51c6af815051c03": {
        "entities": [
            {"name": "守夜团", "type": "组织", "aliases": ["Vigils"]},
            {"name": "城市", "type": "地点", "aliases": ["city"]},
            {"name": "超自然", "type": "概念", "aliases": ["supernatural"]},
            {"name": "罪案", "type": "事件", "aliases": ["crime"]},
        ],
        "relations": [
            {"src": "守夜团", "dst": "罪案", "relation": "调查", "confidence": 0.8},
            {"src": "城市", "dst": "超自然", "relation": "常见", "confidence": 0.7},
        ],
    },
    "ca11a8c1137855ba": {
        "entities": [
            {"name": "德雷克海峡", "type": "地点", "aliases": ["Drake Passage"]},
            {"name": "泰坦尼克号", "type": "事件", "aliases": ["Titanic"]},
            {"name": "作家", "type": "角色", "aliases": ["writer"]},
            {"name": "老板", "type": "角色", "aliases": ["boss"]},
            {"name": "探险队", "type": "组织", "aliases": ["team"]},
        ],
        "relations": [
            {"src": "探险队", "dst": "德雷克海峡", "relation": "穿越", "confidence": 0.9},
            {"src": "探险队", "dst": "泰坦尼克号", "relation": "引以为戒", "confidence": 0.7},
            {"src": "老板", "dst": "作家", "relation": "追查", "confidence": 0.8},
        ],
    },
    "5b03cb39da7f41b8": {
        "entities": [
            {"name": "中尉", "type": "角色", "aliases": ["Lieutenant"]},
            {"name": "薄荷油", "type": "物品", "aliases": ["mint oil"]},
            {"name": "审讯", "type": "事件", "aliases": ["interrogation"]},
            {"name": "谈判", "type": "事件", "aliases": ["Negotiations"]},
        ],
        "relations": [
            {"src": "审讯", "dst": "中尉", "relation": "主导", "confidence": 0.8},
            {"src": "谈判", "dst": "中尉", "relation": "破裂", "confidence": 0.7},
        ],
    },
    "612279a4bfcba6dc": {
        "entities": [
            {"name": "怪物", "type": "概念", "aliases": ["monsters", "Monsters"]},
            {"name": "蛇", "type": "概念", "aliases": ["snakes"]},
        ],
        "relations": [
            {"src": "蛇", "dst": "怪物", "relation": "疑为", "confidence": 0.6},
        ],
    },
    "22eb9fce6ddeefbb": {
        "entities": [
            {"name": "玛尔纱", "type": "角色", "aliases": ["Marsha"]},
            {"name": "帕拉比安", "type": "角色", "aliases": ["Parabian", "Par-Parabian"]},
            {"name": "村庄", "type": "地点", "aliases": ["village"]},
            {"name": "化学武器", "type": "物品", "aliases": ["chemical weapons"]},
        ],
        "relations": [
            {"src": "村庄", "dst": "化学武器", "relation": "藏匿", "confidence": 0.7},
            {"src": "帕拉比安", "dst": "玛尔纱", "relation": "施救", "confidence": 0.8},
        ],
    },
    "9d6032a8cdeefcb3": {
        "entities": [
            {"name": "展览馆", "type": "地点", "aliases": ["exhibition hall"]},
            {"name": "巨型机器人", "type": "物品", "aliases": ["supersized robot", "robot"]},
        ],
        "relations": [
            {"src": "巨型机器人", "dst": "展览馆", "relation": "冲出", "confidence": 0.9},
        ],
    },
    "6de0459f638b0eef": {
        "entities": [
            {"name": "双胞胎", "type": "角色", "aliases": ["The Twins", "twins"]},
            {"name": "P3", "type": "角色", "aliases": ["P3 guy"]},
            {"name": "机器人", "type": "物品", "aliases": ["robot"]},
            {"name": "攻击模式", "type": "概念", "aliases": ["attack pattern"]},
        ],
        "relations": [
            {"src": "机器人", "dst": "攻击模式", "relation": "遵循", "confidence": 0.9},
            {"src": "P3", "dst": "机器人", "relation": "疑似操纵", "confidence": 0.6},
        ],
    },
    "59ce7ccf11393118": {
        "entities": [
            {"name": "圣洛夫基金会", "type": "组织", "aliases": ["Foundation"]},
            {"name": "拱形波动", "type": "概念", "aliases": ["Arching Fluctuations"]},
            {"name": "视象局", "type": "组织", "aliases": ["Visuals Bureau"]},
            {"name": "秘术", "type": "概念", "aliases": ["Arching skill", "arcane skill"]},
            {"name": "溺亡", "type": "事件", "aliases": ["drowning"]},
            {"name": "仪式", "type": "概念", "aliases": ["ritual"]},
        ],
        "relations": [
            {"src": "视象局", "dst": "拱形波动", "relation": "存档", "confidence": 0.8},
            {"src": "拱形波动", "dst": "秘术", "relation": "属于", "confidence": 0.7},
            {"src": "仪式", "dst": "溺亡", "relation": "关联", "confidence": 0.7},
        ],
    },
    "7f97227ff65dcc3a": {
        "entities": [
            {"name": "雪", "type": "概念", "aliases": ["snow", "Snow"]},
            {"name": "柴油发电机", "type": "物品", "aliases": ["diesel generators"]},
            {"name": "雪地摩托", "type": "物品", "aliases": ["snowmobiles"]},
            {"name": "无线电发射机", "type": "物品", "aliases": ["radio transmitters"]},
            {"name": "加热器", "type": "物品", "aliases": ["heater"]},
        ],
        "relations": [
            {"src": "雪", "dst": "雪地摩托", "relation": "需清除", "confidence": 0.7},
            {"src": "加热器", "dst": "柴油发电机", "relation": "依赖供电",
             "confidence": 0.6},
        ],
    },
    "19e27372cd8d0fd1": {
        "entities": [
            {"name": "鱼缸", "type": "物品", "aliases": ["fish tank"]},
            {"name": "办公室", "type": "地点", "aliases": ["office", "corner office"]},
            {"name": "报告", "type": "物品", "aliases": ["report"]},
        ],
        "relations": [
            {"src": "鱼缸", "dst": "办公室", "relation": "放置于", "confidence": 0.8},
        ],
    },
    "4bf8ec42001a95d6": {
        "entities": [
            {"name": "拉普拉斯", "type": "组织", "aliases": ["Laplace", "LSCC"]},
            {"name": "未来", "type": "时间", "aliases": ["future"]},
            {"name": "世界", "type": "概念", "aliases": ["world"]},
        ],
        "relations": [
            {"src": "未来", "dst": "世界", "relation": "剧变", "confidence": 0.8},
        ],
    },
    "9fb771d1bf7750f9": {
        "entities": [
            {"name": "布斯特", "type": "角色", "aliases": ["Booster"]},
            {"name": "父母", "type": "角色", "aliases": ["parents"]},
        ],
        "relations": [
            {"src": "布斯特", "dst": "父母", "relation": "走散", "confidence": 0.6},
        ],
    },
    "1fa25d67add725d7": {
        "entities": [
            {"name": "列车", "type": "物品", "aliases": ["train"]},
            {"name": "大雪", "type": "事件", "aliases": ["heavy snow"]},
            {"name": "餐车", "type": "地点", "aliases": ["dining carriage"]},
            {"name": "土耳其软糖", "type": "物品", "aliases": ["Turkish Delight"]},
        ],
        "relations": [
            {"src": "大雪", "dst": "列车", "relation": "阻断", "confidence": 0.9},
            {"src": "餐车", "dst": "土耳其软糖", "relation": "供应", "confidence": 0.8},
        ],
    },
    "e8b17c3538b3563a": {
        "entities": [
            {"name": "墨西哥城", "type": "地点", "aliases": ["Mexico City"]},
            {"name": "秘术师领地", "type": "概念", "aliases": ["Arcanus territory"]},
            {"name": "拍卖会", "type": "事件", "aliases": ["auction"]},
            {"name": "邀请函", "type": "物品", "aliases": ["invitation"]},
            {"name": "神圣历", "type": "概念", "aliases": ["sacred calendar"]},
            {"name": "太阳历", "type": "概念", "aliases": ["solar calendars"]},
        ],
        "relations": [
            {"src": "拍卖会", "dst": "秘术师领地", "relation": "举行于", "confidence": 0.8},
            {"src": "秘术师领地", "dst": "墨西哥城", "relation": "位于城外",
             "confidence": 0.7},
            {"src": "邀请函", "dst": "神圣历", "relation": "提及", "confidence": 0.8},
            {"src": "神圣历", "dst": "太阳历", "relation": "对齐", "confidence": 0.9},
        ],
    },
    "6f5e3625180b8ff4": {
        "entities": [
            {"name": "阿兹特克神话", "type": "概念", "aliases": ["Aztec myth"]},
            {"name": "新火仪式", "type": "事件", "aliases": ["new fire ceremony"]},
            {"name": "阿兹特克历", "type": "概念", "aliases": ["Aztec calendar"]},
            {"name": "星丘", "type": "地点", "aliases": ["hill of the star"]},
            {"name": "昴星团", "type": "概念", "aliases": ["Pleiades"]},
            {"name": "托纳尔波瓦利", "type": "概念", "aliases": ["tonal Puali"]},
        ],
        "relations": [
            {"src": "阿兹特克历", "dst": "新火仪式", "relation": "周期举行",
             "confidence": 0.9},
            {"src": "新火仪式", "dst": "星丘", "relation": "举行于", "confidence": 0.9},
            {"src": "昴星团", "dst": "星丘", "relation": "观测", "confidence": 0.8},
            {"src": "托纳尔波瓦利", "dst": "阿兹特克历", "relation": "组成",
             "confidence": 0.8},
        ],
    },
    "6c7540d04126cc38": {
        "entities": [
            {"name": "兔毛手袋", "type": "角色",
             "aliases": ["Medicine Pocket", "medicine pocket"]},
            {"name": "乌鸦", "type": "概念", "aliases": ["raven"]},
        ],
        "relations": [
            {"src": "兔毛手袋", "dst": "乌鸦", "relation": "警戒", "confidence": 0.7},
        ],
    },
    "954226afc6ab7fb1": {
        "entities": [
            {"name": "阿拉特", "type": "角色", "aliases": ["Allat"]},
            {"name": "引导者", "type": "角色", "aliases": ["guiding one", "Guiding One"]},
            {"name": "圣洛夫基金会", "type": "组织", "aliases": ["Foundation", "foundations"]},
            {"name": "伏击", "type": "事件", "aliases": ["ambush"]},
        ],
        "relations": [
            {"src": "伏击", "dst": "圣洛夫基金会", "relation": "针对", "confidence": 0.9},
            {"src": "引导者", "dst": "伏击", "relation": "指挥", "confidence": 0.8},
            {"src": "阿拉特", "dst": "引导者", "relation": "交谈", "confidence": 0.7},
        ],
    },
    "a19938eae1788910": {
        "entities": [
            {"name": "医院", "type": "地点", "aliases": ["hospital"]},
            {"name": "枪械", "type": "物品", "aliases": ["guns"]},
            {"name": "歌曲", "type": "物品", "aliases": ["song"]},
            {"name": "求婚", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "歌曲", "dst": "求婚", "relation": "用于", "confidence": 0.7},
        ],
    },
    "1d8060d37d0149d1": {
        "entities": [
            {"name": "病房", "type": "地点", "aliases": ["ward"]},
            {"name": "父亲", "type": "角色", "aliases": ["Papa"]},
            {"name": "松鼠", "type": "概念", "aliases": ["squirrel"]},
            {"name": "洋娃娃", "type": "物品", "aliases": ["doll"]},
            {"name": "公寓", "type": "地点", "aliases": ["apartment"]},
            {"name": "纪念地", "type": "概念", "aliases": ["memorial"]},
        ],
        "relations": [
            {"src": "洋娃娃", "dst": "松鼠", "relation": "形似", "confidence": 0.8},
            {"src": "公寓", "dst": "纪念地", "relation": "视为", "confidence": 0.7},
            {"src": "病房", "dst": "父亲", "relation": "思念", "confidence": 0.7},
        ],
    },
    "f56f4aeac5cfc968": {
        "entities": [
            {"name": "科兹洛夫", "type": "角色",
             "aliases": ["Kozlov", "Mr. and Mrs. Kozlov"]},
            {"name": "马戏团", "type": "组织", "aliases": ["circus"]},
            {"name": "群星", "type": "概念", "aliases": ["stars"]},
        ],
        "relations": [
            {"src": "科兹洛夫", "dst": "马戏团", "relation": "所属", "confidence": 0.8},
        ],
    },
    "2198852469c36714": {
        "entities": [
            {"name": "司辰", "type": "角色", "aliases": ["Timekeeper"]},
            {"name": "海兽", "type": "概念", "aliases": ["sea beast", "dorsal fin"]},
            {"name": "暗礁", "type": "地点", "aliases": ["reefs"]},
            {"name": "终点", "type": "概念", "aliases": ["finish line"]},
        ],
        "relations": [
            {"src": "司辰", "dst": "海兽", "relation": "触碰", "confidence": 0.9},
            {"src": "海兽", "dst": "暗礁", "relation": "游向", "confidence": 0.7},
        ],
    },
    "66e51afaaf6e5edd": {
        "entities": [
            {"name": "系统", "type": "概念", "aliases": ["system"]},
            {"name": "雨滴", "type": "概念", "aliases": ["raindrops"]},
            {"name": "观察者", "type": "概念", "aliases": ["spectator"]},
        ],
        "relations": [
            {"src": "观察者", "dst": "系统", "relation": "影响", "confidence": 0.9},
            {"src": "雨滴", "dst": "系统", "relation": "被触碰", "confidence": 0.7},
        ],
    },
    "9ce25332c0d9d29f": {
        "entities": [
            {"name": "Uccello", "type": "角色", "aliases": ["乌切洛"]},
            {"name": "壁画", "type": "物品", "aliases": ["fresco"]},
            {"name": "线性透视", "type": "概念", "aliases": ["linear perspective"]},
            {"name": "柏拉图理型论", "type": "概念",
             "aliases": ["Plato's Theory of Forms"]},
        ],
        "relations": [
            {"src": "Uccello", "dst": "壁画", "relation": "主持绘制", "confidence": 0.9},
            {"src": "壁画", "dst": "线性透视", "relation": "运用", "confidence": 0.9},
            {"src": "线性透视", "dst": "柏拉图理型论", "relation": "建议参考",
             "confidence": 0.7},
        ],
    },
    "fc0ac04b47d23dbd": {
        "entities": [
            {"name": "巴黎", "type": "地点", "aliases": ["Paris", "Parisian"]},
            {"name": "命运之流", "type": "概念", "aliases": ["Streams of fate"]},
            {"name": "卜杖探源", "type": "概念", "aliases": ["Dowsing"]},
        ],
        "relations": [
            {"src": "命运之流", "dst": "卜杖探源", "relation": "寻找", "confidence": 0.7},
        ],
    },
    "5894e470d390f860": {
        "entities": [
            {"name": "巴黎", "type": "地点", "aliases": ["Paris"]},
            {"name": "战时工厂", "type": "组织", "aliases": ["wartime factories"]},
        ],
        "relations": [
            {"src": "战时工厂", "dst": "巴黎", "relation": "关闭", "confidence": 0.8},
        ],
    },
    "a430623ba9ca7aaf": {
        "entities": [
            {"name": "阿马尔菲塔诺村", "type": "地点", "aliases": ["Amalfitano"]},
            {"name": "索诺拉沙漠", "type": "地点", "aliases": ["Sonora desert"]},
            {"name": "巴比伦塔多", "type": "概念", "aliases": ["Tado of Babylon"]},
            {"name": "研究者", "type": "角色", "aliases": ["researcher"]},
            {"name": "1975年", "type": "时间", "aliases": ["1975"]},
        ],
        "relations": [
            {"src": "阿马尔菲塔诺村", "dst": "索诺拉沙漠", "relation": "位于",
             "confidence": 0.9},
            {"src": "研究者", "dst": "阿马尔菲塔诺村", "relation": "到访",
             "confidence": 0.9},
            {"src": "阿马尔菲塔诺村", "dst": "巴比伦塔多", "relation": "信奉",
             "confidence": 0.7},
        ],
    },
    "d6475a48d10eef89": {
        "entities": [
            {"name": "谋杀案", "type": "事件", "aliases": ["murder", "sixth murder"]},
            {"name": "画作", "type": "物品", "aliases": ["paintings", "painting"]},
            {"name": "拍卖会", "type": "事件", "aliases": ["auction"]},
            {"name": "犯罪现场", "type": "地点", "aliases": ["crime scenes"]},
        ],
        "relations": [
            {"src": "画作", "dst": "谋杀案", "relation": "关联", "confidence": 0.9},
            {"src": "犯罪现场", "dst": "画作", "relation": "出现", "confidence": 0.9},
            {"src": "拍卖会", "dst": "画作", "relation": "拍出", "confidence": 0.8},
        ],
    },
    "51387d0b99f1483a": {
        "entities": [
            {"name": "外交官", "type": "角色", "aliases": ["diplomat", "Diplomat"]},
            {"name": "记者", "type": "角色", "aliases": ["journalist"]},
            {"name": "画作", "type": "物品", "aliases": ["painting", "paintings"]},
            {"name": "杀手", "type": "角色", "aliases": ["killer"]},
            {"name": "宅邸", "type": "地点", "aliases": ["mansions"]},
        ],
        "relations": [
            {"src": "记者", "dst": "外交官", "relation": "转交画作", "confidence": 0.8},
            {"src": "杀手", "dst": "外交官", "relation": "杀害", "confidence": 0.9},
            {"src": "画作", "dst": "杀手", "relation": "作案关键", "confidence": 0.8},
        ],
    },
    "f3780f98c9951bd8": {
        "entities": [
            {"name": "火箭", "type": "物品", "aliases": ["rockets", "Rockets"]},
            {"name": "坦克", "type": "物品", "aliases": ["tanks", "Tanks"]},
            {"name": "书籍", "type": "物品", "aliases": ["books", "Books"]},
            {"name": "废墟", "type": "概念", "aliases": ["ruins"]},
            {"name": "沉默", "type": "概念", "aliases": ["silence", "Silence"]},
        ],
        "relations": [
            {"src": "书籍", "dst": "废墟", "relation": "化为", "confidence": 0.7},
            {"src": "坦克", "dst": "废墟", "relation": "化为", "confidence": 0.6},
        ],
    },
    "aaa399f2f52a0117": {
        "entities": [
            {"name": "塞梅尔维斯", "type": "角色",
             "aliases": ["Semmelweis", "Semmovice", "Ms. Semmovice Hoffman"]},
            {"name": "圣洛夫基金会", "type": "组织", "aliases": ["Foundation", "foundation"]},
            {"name": "调查员", "type": "角色", "aliases": ["investigator"]},
        ],
        "relations": [
            {"src": "塞梅尔维斯", "dst": "圣洛夫基金会", "relation": "任职",
             "confidence": 0.9},
            {"src": "塞梅尔维斯", "dst": "调查员", "relation": "担任", "confidence": 0.9},
        ],
    },
    "99d2dfb99f034469": {
        "entities": [
            {"name": "马克西姆", "type": "角色", "aliases": ["Maxim"]},
            {"name": "父母", "type": "角色", "aliases": ["parents"]},
            {"name": "亡者", "type": "概念", "aliases": ["dead"]},
        ],
        "relations": [
            {"src": "马克西姆", "dst": "亡者", "relation": "哀悼", "confidence": 0.8},
            {"src": "父母", "dst": "马克西姆", "relation": "逝去", "confidence": 0.7},
        ],
    },
    "3800076e8b392c9a": {
        "entities": [
            {"name": "集体", "type": "概念", "aliases": ["collective superstructure"]},
            {"name": "农民", "type": "角色", "aliases": ["farmers"]},
            {"name": "机器人", "type": "物品", "aliases": ["robots"]},
            {"name": "苏联", "type": "地点", "aliases": ["Soviet"]},
            {"name": "农业机器人", "type": "物品", "aliases": ["agricultural robotics"]},
        ],
        "relations": [
            {"src": "农民", "dst": "机器人", "relation": "协同", "confidence": 0.8},
            {"src": "苏联", "dst": "农业机器人", "relation": "发明", "confidence": 0.8},
            {"src": "农业机器人", "dst": "集体", "relation": "构成", "confidence": 0.7},
        ],
    },
    "55dcd94e009bc6c3": {
        "entities": [
            {"name": "苏联社会", "type": "概念", "aliases": ["Soviet society"]},
            {"name": "机器人", "type": "物品", "aliases": ["robots"]},
            {"name": "瘟疫", "type": "事件", "aliases": ["plague"]},
            {"name": "乌托邦", "type": "概念", "aliases": ["utopia"]},
        ],
        "relations": [
            {"src": "机器人", "dst": "苏联社会", "relation": "奠基", "confidence": 0.9},
            {"src": "瘟疫", "dst": "苏联社会", "relation": "曾肆虐", "confidence": 0.8},
            {"src": "苏联社会", "dst": "乌托邦", "relation": "被视为", "confidence": 0.7},
        ],
    },
    "482e2218cfdb2844": {
        "entities": [
            {"name": "北方哨歌", "type": "角色",
             "aliases": ["Winsong", "Ms. Winsong", "Windsong"]},
            {"name": "八月的种子", "type": "物品", "aliases": ["August's seeds"]},
            {"name": "信件", "type": "物品", "aliases": ["letter"]},
            {"name": "外勤任务", "type": "事件", "aliases": ["field missions"]},
        ],
        "relations": [
            {"src": "北方哨歌", "dst": "八月的种子", "relation": "接收", "confidence": 0.9},
            {"src": "北方哨歌", "dst": "信件", "relation": "接收", "confidence": 0.9},
            {"src": "外勤任务", "dst": "北方哨歌", "relation": "指派", "confidence": 0.8},
        ],
    },
    "8379b5b119357675": {
        "entities": [
            {"name": "初雪", "type": "事件", "aliases": ["first snow"]},
            {"name": "钢铁巨兽", "type": "概念", "aliases": ["steel behemoths"]},
            {"name": "巫术", "type": "概念", "aliases": ["fell sorcery"]},
            {"name": "冬季", "type": "时间", "aliases": ["Winter"]},
        ],
        "relations": [
            {"src": "初雪", "dst": "冬季", "relation": "标志", "confidence": 0.8},
            {"src": "巫术", "dst": "钢铁巨兽", "relation": "抵御", "confidence": 0.7},
        ],
    },
    "f4ee61f6cde0beab": {
        "entities": [
            {"name": "伯顿", "type": "角色", "aliases": ["Burton"]},
            {"name": "火山", "type": "地点", "aliases": ["volcano"]},
            {"name": "伊利昂", "type": "地点", "aliases": ["Ilium"]},
            {"name": "引擎", "type": "物品", "aliases": ["Engines"]},
        ],
        "relations": [
            {"src": "伯顿", "dst": "火山", "relation": "遭遇险境", "confidence": 0.7},
            {"src": "伊利昂", "dst": "伯顿", "relation": "欲阻拦", "confidence": 0.6},
        ],
    },
    "5e53fbc12e4337d4": {
        "entities": [
            {"name": "达芬奇", "type": "角色", "aliases": ["Leonardo", "Mr. Leonardo"]},
            {"name": "卡森先生", "type": "角色", "aliases": ["Mr. Carson"]},
            {"name": "线性透视", "type": "概念", "aliases": ["linear perspective"]},
            {"name": "消失点", "type": "概念",
             "aliases": ["vanishing points", "Vanishing points"]},
            {"name": "蛋", "type": "物品", "aliases": ["eggs"]},
        ],
        "relations": [
            {"src": "达芬奇", "dst": "线性透视", "relation": "运用", "confidence": 0.9},
            {"src": "线性透视", "dst": "消失点", "relation": "包含", "confidence": 0.9},
            {"src": "卡森先生", "dst": "达芬奇", "relation": "提及训练法",
             "confidence": 0.7},
        ],
    },
    "e42222a8f7fca849": {
        "entities": [
            {"name": "法国", "type": "地点", "aliases": ["France"]},
            {"name": "战争", "type": "事件", "aliases": ["war"]},
            {"name": "和平", "type": "概念", "aliases": ["peace"]},
            {"name": "经济", "type": "概念", "aliases": ["economy"]},
        ],
        "relations": [
            {"src": "战争", "dst": "法国", "relation": "影响", "confidence": 0.9},
            {"src": "法国", "dst": "和平", "relation": "渴望", "confidence": 0.8},
            {"src": "经济", "dst": "法国", "relation": "一度繁荣", "confidence": 0.7},
        ],
    },
    "fe57651bed3e0c8c": {
        "entities": [
            {"name": "狱卒", "type": "角色", "aliases": ["jailer", "Jailer"]},
            {"name": "医师", "type": "角色", "aliases": ["physician"]},
            {"name": "艺术家", "type": "角色", "aliases": ["artists"]},
            {"name": "花园", "type": "地点", "aliases": ["garden"]},
        ],
        "relations": [
            {"src": "狱卒", "dst": "艺术家", "relation": "驱散", "confidence": 0.8},
            {"src": "医师", "dst": "花园", "relation": "审批集会", "confidence": 0.7},
            {"src": "艺术家", "dst": "花园", "relation": "聚集", "confidence": 0.8},
        ],
    },
    "3671b672e80dad52": {
        "entities": [
            {"name": "加西亚", "type": "角色", "aliases": ["Garcia"]},
            {"name": "幻想元素", "type": "概念",
             "aliases": ["elemento de la fantasía", "fantasy"]},
            {"name": "药物", "type": "物品", "aliases": ["medicina", "medicine"]},
        ],
        "relations": [
            {"src": "加西亚", "dst": "药物", "relation": "服用", "confidence": 0.8},
            {"src": "加西亚", "dst": "幻想元素", "relation": "追求", "confidence": 0.7},
        ],
    },
    "2cb2e7e44096aa61": {
        "entities": [
            {"name": "科马拉", "type": "地点", "aliases": ["Komala"]},
            {"name": "监狱", "type": "地点", "aliases": ["prison", "prisión"]},
            {"name": "杂志", "type": "物品", "aliases": ["magazine"]},
            {"name": "破坏", "type": "概念", "aliases": ["Destruction"]},
            {"name": "停滞", "type": "概念", "aliases": ["stagnant pond"]},
        ],
        "relations": [
            {"src": "科马拉", "dst": "监狱", "relation": "属于", "confidence": 0.9},
            {"src": "破坏", "dst": "停滞", "relation": "破除", "confidence": 0.7},
        ],
    },
    "e156c5de6148c04a": {
        "entities": [
            {"name": "拍卖会", "type": "事件", "aliases": ["auction"]},
            {"name": "竞拍牌", "type": "物品", "aliases": ["paddle"]},
            {"name": "1928年", "type": "时间", "aliases": ["1928"]},
        ],
        "relations": [
            {"src": "拍卖会", "dst": "竞拍牌", "relation": "使用", "confidence": 0.8},
        ],
    },
    "f18ba441d0fe87d4": {
        "entities": [
            {"name": "秘术", "type": "概念", "aliases": ["arcane skill"]},
            {"name": "子弹", "type": "物品", "aliases": ["bullets"]},
            {"name": "医药", "type": "物品", "aliases": ["medicine"]},
            {"name": "战场", "type": "地点", "aliases": ["battlefield"]},
        ],
        "relations": [
            {"src": "秘术", "dst": "战场", "relation": "救命", "confidence": 0.8},
            {"src": "子弹", "dst": "战场", "relation": "使用", "confidence": 0.7},
        ],
    },
    "d7fa356a5b4dd7d3": {
        "entities": [
            {"name": "拉普拉斯", "type": "组织", "aliases": ["LSCC", "Laplace"]},
            {"name": "收容部", "type": "组织", "aliases": ["Containment Department"]},
            {"name": "喋喋帽", "type": "物品", "aliases": ["chatter cap"]},
            {"name": "共生体", "type": "概念", "aliases": ["symbionts"]},
        ],
        "relations": [
            {"src": "喋喋帽", "dst": "共生体", "relation": "通信", "confidence": 0.9},
            {"src": "喋喋帽", "dst": "拉普拉斯", "relation": "联络", "confidence": 0.9},
            {"src": "收容部", "dst": "拉普拉斯", "relation": "隶属", "confidence": 0.8},
        ],
    },
    "e133eff6232016b2": {
        "entities": [
            {"name": "整合之家", "type": "组织", "aliases": ["House of Integritas"]},
            {"name": "主楼梯", "type": "地点",
             "aliases": ["mainstairwell", "main stairwell"]},
            {"name": "非战斗人员", "type": "概念", "aliases": ["noncombatant staff"]},
            {"name": "会议", "type": "事件", "aliases": ["meeting"]},
        ],
        "relations": [
            {"src": "整合之家", "dst": "会议", "relation": "请求", "confidence": 0.8},
            {"src": "非战斗人员", "dst": "主楼梯", "relation": "疏散", "confidence": 0.9},
        ],
    },
    "ed8405a36f3f6d0e": {
        "entities": [
            {"name": "医生", "type": "角色", "aliases": ["doctor", "Doctor"]},
            {"name": "疯女人", "type": "角色", "aliases": ["that woman", "lunatic"]},
        ],
        "relations": [
            {"src": "疯女人", "dst": "医生", "relation": "需就诊", "confidence": 0.7},
        ],
    },
    "43669ec99b0362a8": {
        "entities": [
            {"name": "战争", "type": "事件", "aliases": ["war", "this war"]},
            {"name": "战场", "type": "地点", "aliases": ["battlefield"]},
            {"name": "英雄", "type": "概念", "aliases": ["heroes"]},
        ],
        "relations": [
            {"src": "战场", "dst": "战争", "relation": "发生于", "confidence": 0.8},
            {"src": "战争", "dst": "英雄", "relation": "渴望成为", "confidence": 0.7},
        ],
    },
    "07c503926a9bd5e4": {
        "entities": [
            {"name": "黑暗时代", "type": "时间", "aliases": ["dark times"]},
            {"name": "科学家", "type": "角色", "aliases": ["scientists", "young scientists"]},
            {"name": "悲剧", "type": "概念", "aliases": ["tragedies"]},
        ],
        "relations": [
            {"src": "黑暗时代", "dst": "悲剧", "relation": "关联", "confidence": 0.7},
        ],
    },
    "335427c326ab3680": {
        "entities": [
            {"name": "聚合物同化适应", "type": "概念",
             "aliases": ["Polymer Assimilative Adaptation"]},
            {"name": "集体1.0", "type": "概念", "aliases": ["Collective 1.0"]},
            {"name": "接口装置", "type": "物品", "aliases": ["interface devices"]},
            {"name": "机器人", "type": "物品", "aliases": ["robots"]},
            {"name": "人脑", "type": "概念", "aliases": ["human brain"]},
        ],
        "relations": [
            {"src": "聚合物同化适应", "dst": "接口装置", "relation": "实现植入",
             "confidence": 0.9},
            {"src": "接口装置", "dst": "集体1.0", "relation": "连接", "confidence": 0.9},
            {"src": "集体1.0", "dst": "机器人", "relation": "控制", "confidence": 0.9},
            {"src": "聚合物同化适应", "dst": "人脑", "relation": "影响未知",
             "confidence": 0.7},
        ],
    },
    "2f2662933b4159fb": {
        "entities": [
            {"name": "指针", "type": "角色", "aliases": ["Pointer"]},
            {"name": "笔", "type": "物品", "aliases": ["pen", "Pen"]},
            {"name": "数字数据", "type": "概念", "aliases": ["digital data"]},
            {"name": "影像记录", "type": "物品", "aliases": ["video", "last record"]},
        ],
        "relations": [
            {"src": "影像记录", "dst": "数字数据", "relation": "保存为", "confidence": 0.9},
            {"src": "影像记录", "dst": "笔", "relation": "取代", "confidence": 0.8},
            {"src": "指针", "dst": "影像记录", "relation": "被询问", "confidence": 0.8},
        ],
    },
}


def main() -> int:
    ap = argparse.ArgumentParser(description="补抽空块 第 2 批")
    ap.add_argument("--character", default="wu_ming_zhe")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    settings = get_settings()
    cache_dir = Path(settings.plot_cache_dir) / args.character
    cache_dir.mkdir(parents=True, exist_ok=True)

    written = skipped = 0
    for h, data in RESULTS.items():
        p = cache_dir / f"{h}.json"
        if p.exists() and not args.force:
            skipped += 1
            continue
        p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        written += 1
    noop_path = ROOT / "data/knowledge/_audit/noop_confirmed.json"
    cur = set()
    if noop_path.exists():
        cur = set(json.loads(noop_path.read_text(encoding="utf-8")))
    cur |= set(NOOP)
    noop_path.write_text(json.dumps(sorted(cur), ensure_ascii=False, indent=1),
                         encoding="utf-8")
    print(f"[apply-p2] 写入 {written} 条，跳过 {skipped} 条")
    print(f"[apply-p2] NOOP 累计 {len(cur)} 条")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
