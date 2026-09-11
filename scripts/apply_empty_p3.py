# -*- coding: utf-8 -*-
"""补抽 408 块空抽取中的第 3 批（67 块，云端人工抽取）。同 apply_empty_p1.py。

本批含 4 块中文（v3.4 巡神相关）。注意：
- ``typhon`` 在此处是「风暴」的比喻，不是角色提丰，未做别名映射；
- ``miss stranger`` 命中无名者（Ms. Stranger），是本批最有价值的补抽。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from roleplay.config import get_settings  # noqa: E402

NOOP: list[str] = [
    "1726821d6dab1ead",  # 市井对骂（brits / lady），无专名
    "ed8300d2c2c56f24",  # 日常斗嘴（razor sharp wit / flashbang），无专名
]

RESULTS: dict[str, dict] = {
    "226f849ec4ef15ac": {
        "entities": [
            {"name": "拉普拉斯", "type": "组织", "aliases": ["Laplace"]},
            {"name": "圣洛夫基金会", "type": "组织", "aliases": ["Foundation"]},
            {"name": "极光", "type": "概念", "aliases": ["Aurora"]},
            {"name": "传送圆盘", "type": "物品", "aliases": ["teleport disk"]},
        ],
        "relations": [
            {"src": "拉普拉斯", "dst": "圣洛夫基金会", "relation": "组队", "confidence": 0.9},
            {"src": "传送圆盘", "dst": "拉普拉斯", "relation": "研发", "confidence": 0.8},
            {"src": "传送圆盘", "dst": "极光", "relation": "观测目标", "confidence": 0.7},
        ],
    },
    "a8d9593cc4df55f0": {
        "entities": [
            {"name": "指针", "type": "角色", "aliases": ["Pointer"]},
            {"name": "流浪狗", "type": "概念", "aliases": ["stray dogs"]},
            {"name": "冬季", "type": "时间", "aliases": ["coldest winter nights"]},
            {"name": "工作", "type": "概念", "aliases": ["work"]},
        ],
        "relations": [
            {"src": "流浪狗", "dst": "冬季", "relation": "依偎取暖", "confidence": 0.8},
            {"src": "指针", "dst": "工作", "relation": "曾共事", "confidence": 0.7},
        ],
    },
    "ceab1ea5b17ae397": {
        "entities": [
            {"name": "琥珀室", "type": "地点", "aliases": ["Amber Room", "amber room"]},
            {"name": "教堂", "type": "地点", "aliases": ["church"]},
            {"name": "城市", "type": "地点", "aliases": ["city"]},
            {"name": "小规模冲突", "type": "事件", "aliases": ["skirmishes"]},
        ],
        "relations": [
            {"src": "小规模冲突", "dst": "城市", "relation": "持续", "confidence": 0.9},
            {"src": "琥珀室", "dst": "教堂", "relation": "安全性存疑", "confidence": 0.6},
        ],
    },
    "1d6541ffbfe3ffb2": {
        "entities": [
            {"name": "城邦", "type": "地点", "aliases": ["polis"]},
            {"name": "金杯", "type": "物品", "aliases": ["golden goblet"]},
            {"name": "无花果", "type": "物品", "aliases": ["figs"]},
            {"name": "橄榄枝", "type": "物品", "aliases": ["olive branches"]},
            {"name": "航行", "type": "事件", "aliases": ["voyage"]},
            {"name": "风暴", "type": "事件", "aliases": ["storms"]},
        ],
        "relations": [
            {"src": "城邦", "dst": "金杯", "relation": "携带自", "confidence": 0.9},
            {"src": "城邦", "dst": "橄榄枝", "relation": "携带自", "confidence": 0.9},
            {"src": "航行", "dst": "风暴", "relation": "遭遇", "confidence": 0.8},
        ],
    },
    "c70f0651029bb2d4": {
        "entities": [
            {"name": "伊萨卡", "type": "地点", "aliases": ["Ithaca"]},
            {"name": "港口", "type": "地点", "aliases": ["port"]},
        ],
        "relations": [
            {"src": "伊萨卡", "dst": "港口", "relation": "抵达", "confidence": 0.8},
        ],
    },
    "a2e90a056f2ff7e4": {
        "entities": [
            {"name": "APPLe", "type": "角色",
             "aliases": ["Apple", "苹果", "This Apple", "Signore Apple"]},
            {"name": "佛罗伦萨", "type": "地点", "aliases": ["Florence"]},
            {"name": "说明书", "type": "物品", "aliases": ["instruction book"]},
            {"name": "朝圣", "type": "概念", "aliases": ["pilgrimage"]},
            {"name": "绝对正义", "type": "概念", "aliases": ["absolute justice"]},
        ],
        "relations": [
            {"src": "APPLe", "dst": "佛罗伦萨", "relation": "抵达", "confidence": 0.9},
            {"src": "APPLe", "dst": "说明书", "relation": "查阅", "confidence": 0.8},
            {"src": "朝圣", "dst": "佛罗伦萨", "relation": "前往", "confidence": 0.7},
        ],
    },
    "4df22fcdb113ea08": {
        "entities": [
            {"name": "圣洛夫基金会", "type": "组织", "aliases": ["Foundation", "foundation"]},
            {"name": "拉普拉斯", "type": "组织", "aliases": ["Laplace"]},
            {"name": "暴雨", "type": "事件", "aliases": ["Storm", "The Storm"]},
            {"name": "研究者", "type": "角色", "aliases": ["researchers"]},
        ],
        "relations": [
            {"src": "研究者", "dst": "暴雨", "relation": "采集数据", "confidence": 0.9},
            {"src": "暴雨", "dst": "研究者", "relation": "致未能返回", "confidence": 0.8},
            {"src": "圣洛夫基金会", "dst": "暴雨", "relation": "处境艰难", "confidence": 0.7},
        ],
    },
    "f649694dec8eebe6": {
        "entities": [
            {"name": "欧洲", "type": "地点", "aliases": ["Europe"]},
            {"name": "重塑之手", "type": "组织",
             "aliases": ["Manus Vindicte", "Manus Vindicta", "Manus Vindictae", "Manus"]},
            {"name": "战争", "type": "事件", "aliases": ["war"]},
            {"name": "邪教", "type": "概念", "aliases": ["evil cult"]},
        ],
        "relations": [
            {"src": "欧洲", "dst": "重塑之手", "relation": "勾结", "confidence": 0.9},
            {"src": "重塑之手", "dst": "邪教", "relation": "被称为", "confidence": 0.9},
            {"src": "战争", "dst": "欧洲", "relation": "动摇", "confidence": 0.9},
            {"src": "重塑之手", "dst": "战争", "relation": "渴求屠杀", "confidence": 0.8},
        ],
    },
    "653ee9181a747158": {
        "entities": [
            {"name": "重塑之手", "type": "组织", "aliases": ["Manus", "Manus Vindictae"]},
            {"name": "总部", "type": "地点", "aliases": ["Headquarters", "headquarters"]},
            {"name": "暴雨", "type": "事件", "aliases": ["Storm", "The Storm"]},
            {"name": "委员会大楼", "type": "地点", "aliases": ["committee building"]},
        ],
        "relations": [
            {"src": "重塑之手", "dst": "总部", "relation": "袭击", "confidence": 0.9},
            {"src": "委员会大楼", "dst": "总部", "relation": "位于", "confidence": 0.7},
            {"src": "暴雨", "dst": "总部", "relation": "临近时遭袭", "confidence": 0.8},
        ],
    },
    "bb02dd4c818326cc": {
        "entities": [
            {"name": "无名者", "type": "角色",
             "aliases": ["Miss Stranger", "Ms. Stranger", "miss stranger", "陌生人小姐"]},
            {"name": "SPDM", "type": "组织", "aliases": []},
            {"name": "总部", "type": "地点", "aliases": ["headquarters"]},
            {"name": "奥斯本上尉", "type": "角色", "aliases": ["Captain Osborn", "Osborn"]},
            {"name": "第一小队", "type": "组织", "aliases": ["first squad"]},
        ],
        "relations": [
            {"src": "无名者", "dst": "SPDM", "relation": "负责准入", "confidence": 0.9},
            {"src": "第一小队", "dst": "SPDM", "relation": "前往", "confidence": 0.9},
            {"src": "奥斯本上尉", "dst": "第一小队", "relation": "指挥", "confidence": 0.9},
            {"src": "SPDM", "dst": "总部", "relation": "防止混乱扩散", "confidence": 0.8},
        ],
    },
    "1084bf6349eeb5f1": {
        "entities": [
            {"name": "仙人寿长生", "type": "概念", "aliases": ["寿长生"]},
            {"name": "程勋俭", "type": "角色", "aliases": ["小程勋俭", "小程训姐"]},
            {"name": "戏台", "type": "地点", "aliases": []},
            {"name": "盗人", "type": "角色", "aliases": ["嫌犯"]},
            {"name": "妖法", "type": "概念", "aliases": []},
            {"name": "打铁花", "type": "事件", "aliases": []},
            {"name": "城门", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "仙人寿长生", "dst": "戏台", "relation": "传言地点", "confidence": 0.9},
            {"src": "盗人", "dst": "城门", "relation": "施妖法", "confidence": 0.8},
            {"src": "盗人", "dst": "程勋俭", "relation": "自其手逃脱", "confidence": 0.8},
            {"src": "程勋俭", "dst": "戏台", "relation": "受命看守", "confidence": 0.7},
        ],
    },
    "27f5163744b3d194": {
        "entities": [
            {"name": "罗佐", "type": "角色", "aliases": ["Roseau"]},
            {"name": "引导者", "type": "角色", "aliases": ["guiding one", "Guiding One"]},
            {"name": "暴雨", "type": "事件", "aliases": ["Storm", "The Storm"]},
            {"name": "应许之地", "type": "概念", "aliases": ["promised land"]},
            {"name": "1999年", "type": "时间", "aliases": ["1999"]},
        ],
        "relations": [
            {"src": "引导者", "dst": "应许之地", "relation": "引领追寻", "confidence": 0.9},
            {"src": "罗佐", "dst": "引导者", "relation": "遵循意志", "confidence": 0.8},
            {"src": "暴雨", "dst": "引导者", "relation": "揭示奥秘", "confidence": 0.7},
            {"src": "1999年", "dst": "应许之地", "relation": "追寻起点", "confidence": 0.8},
        ],
    },
    "2d141879084450f4": {
        "entities": [
            {"name": "反抗军", "type": "组织", "aliases": ["Rebels"]},
            {"name": "拉普拉斯", "type": "组织", "aliases": ["Laplace"]},
            {"name": "研究者", "type": "角色", "aliases": ["researcher"]},
        ],
        "relations": [
            {"src": "研究者", "dst": "反抗军", "relation": "激怒", "confidence": 0.8},
            {"src": "研究者", "dst": "拉普拉斯", "relation": "隶属", "confidence": 0.8},
        ],
    },
    "eb16f780161d08a5": {
        "entities": [
            {"name": "APPLe", "type": "角色",
             "aliases": ["Apple", "苹果", "this apple", "This Apple"]},
            {"name": "铬化合物", "type": "物品", "aliases": ["chromium compounds"]},
            {"name": "氧化", "type": "概念", "aliases": ["oxidation"]},
            {"name": "颜料", "type": "物品", "aliases": ["pigments"]},
            {"name": "滤光片", "type": "物品", "aliases": ["optical filter"]},
        ],
        "relations": [
            {"src": "铬化合物", "dst": "氧化", "relation": "发生", "confidence": 0.9},
            {"src": "APPLe", "dst": "滤光片", "relation": "类比自身", "confidence": 0.8},
            {"src": "颜料", "dst": "氧化", "relation": "显现", "confidence": 0.7},
        ],
    },
    "1cf1b48e44ece771": {
        "entities": [
            {"name": "另一个自我", "type": "概念", "aliases": ["alter ego", "Alter Ego"]},
            {"name": "老妇人", "type": "角色", "aliases": ["anciana"]},
            {"name": "副因果研究者", "type": "角色",
             "aliases": ["investigadora de para-causalidad"]},
            {"name": "巴比伦骰子", "type": "物品", "aliases": ["dado de Babilonia"]},
            {"name": "孩童", "type": "概念", "aliases": ["niños", "children"]},
        ],
        "relations": [
            {"src": "副因果研究者", "dst": "另一个自我", "relation": "听闻", "confidence": 0.8},
            {"src": "巴比伦骰子", "dst": "老妇人", "relation": "遗留", "confidence": 0.7},
            {"src": "孩童", "dst": "老妇人", "relation": "被提及失踪", "confidence": 0.8},
        ],
    },
    "32520b27d995127b": {
        "entities": [
            {"name": "西蒙娜", "type": "角色", "aliases": ["Simone"]},
            {"name": "主任", "type": "角色", "aliases": ["director", "Director"]},
        ],
        "relations": [
            {"src": "西蒙娜", "dst": "主任", "relation": "质疑", "confidence": 0.8},
        ],
    },
    "d50e9d4c1a65dcd2": {
        "entities": [
            {"name": "拉普拉斯", "type": "组织", "aliases": ["Laplace"]},
            {"name": "拉普拉斯研究员", "type": "角色", "aliases": ["laplace researcher"]},
            {"name": "无线电", "type": "物品", "aliases": ["radio"]},
            {"name": "录像", "type": "物品", "aliases": ["video"]},
        ],
        "relations": [
            {"src": "拉普拉斯研究员", "dst": "拉普拉斯", "relation": "隶属", "confidence": 0.9},
            {"src": "录像", "dst": "无线电", "relation": "为避免干扰而关闭",
             "confidence": 0.8},
        ],
    },
    "4134d8bef97d19fd": {
        "entities": [
            {"name": "旅行者一号", "type": "物品", "aliases": ["Voyager 1", "Voyager"]},
            {"name": "陨石", "type": "事件", "aliases": ["meteor"]},
            {"name": "地球", "type": "地点", "aliases": ["Earth"]},
            {"name": "广播", "type": "概念", "aliases": ["broadcast"]},
        ],
        "relations": [
            {"src": "陨石", "dst": "地球", "relation": "坠落", "confidence": 0.9},
            {"src": "广播", "dst": "旅行者一号", "relation": "报道", "confidence": 0.9},
        ],
    },
    "ab4b3055fba99965": {
        "entities": [
            {"name": "程勋杰", "type": "角色", "aliases": []},
            {"name": "杨五", "type": "角色", "aliases": []},
            {"name": "神秘游行队伍", "type": "组织", "aliases": ["游行队伍"]},
            {"name": "长生之法", "type": "概念", "aliases": ["长生", "长生流言"]},
            {"name": "春花巷", "type": "地点", "aliases": []},
            {"name": "动物遗失案", "type": "事件", "aliases": ["动物遗失"]},
            {"name": "巡神", "type": "事件", "aliases": ["高校巡神"]},
            {"name": "大明律令", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "神秘游行队伍", "dst": "长生之法", "relation": "散布流言",
             "confidence": 0.9},
            {"src": "动物遗失案", "dst": "春花巷", "relation": "发生于", "confidence": 0.9},
            {"src": "巡神", "dst": "长生之法", "relation": "同期发生", "confidence": 0.8},
            {"src": "杨五", "dst": "程勋杰", "relation": "请示", "confidence": 0.8},
            {"src": "程勋杰", "dst": "动物遗失案", "relation": "督办", "confidence": 0.8},
        ],
    },
    "adc37fdb9a634543": {
        "entities": [
            {"name": "地下墓穴", "type": "地点", "aliases": ["catacombs", "Catacombs"]},
            {"name": "西莉亚", "type": "角色", "aliases": ["Celia"]},
            {"name": "命运之影", "type": "概念", "aliases": ["shadow of fate"]},
        ],
        "relations": [
            {"src": "西莉亚", "dst": "地下墓穴", "relation": "身处", "confidence": 0.8},
            {"src": "命运之影", "dst": "西莉亚", "relation": "追猎", "confidence": 0.8},
        ],
    },
    "7dd19791dfe8e1b3": {
        "entities": [
            {"name": "残影", "type": "概念", "aliases": ["shades", "Shades"]},
            {"name": "建筑免疫性", "type": "概念", "aliases": ["building's immunity"]},
            {"name": "走廊", "type": "地点", "aliases": ["corridor"]},
        ],
        "relations": [
            {"src": "残影", "dst": "建筑免疫性", "relation": "相关", "confidence": 0.7},
            {"src": "残影", "dst": "走廊", "relation": "出没", "confidence": 0.6},
        ],
    },
    "88df3001f23f52a4": {
        "entities": [
            {"name": "母神", "type": "角色", "aliases": ["Mother Spirit"]},
            {"name": "冰川瘟疫", "type": "事件", "aliases": ["plague in the glacier"]},
            {"name": "雪怪", "type": "概念", "aliases": ["snow monster"]},
            {"name": "驯鹿", "type": "概念", "aliases": ["reindeer"]},
        ],
        "relations": [
            {"src": "冰川瘟疫", "dst": "母神", "relation": "关联", "confidence": 0.7},
            {"src": "雪怪", "dst": "驯鹿", "relation": "力敌", "confidence": 0.7},
        ],
    },
    "70bb4dc171d6139f": {
        "entities": [
            {"name": "完美语言", "type": "概念", "aliases": ["perfect language"]},
            {"name": "暴雨症候群", "type": "概念",
             "aliases": ["storm syndrome", "Storm Syndrome"]},
            {"name": "语言紊乱", "type": "概念", "aliases": ["language disorder"]},
            {"name": "高塔", "type": "地点", "aliases": ["tower"]},
            {"name": "报告", "type": "物品", "aliases": ["reports"]},
        ],
        "relations": [
            {"src": "完美语言", "dst": "高塔", "relation": "以…为中心", "confidence": 0.9},
            {"src": "语言紊乱", "dst": "暴雨症候群", "relation": "属于", "confidence": 0.8},
            {"src": "报告", "dst": "完美语言", "relation": "记载", "confidence": 0.8},
        ],
    },
    "a2a6f5e1c792f990": {
        "entities": [
            {"name": "东线", "type": "地点", "aliases": ["eastern front", "Eastern Front"]},
            {"name": "战场", "type": "地点", "aliases": ["battlefield"]},
            {"name": "尘埃", "type": "概念", "aliases": ["dust", "Dust"]},
        ],
        "relations": [
            {"src": "战场", "dst": "东线", "relation": "赶赴", "confidence": 0.8},
        ],
    },
    "317ab05da436d59c": {
        "entities": [
            {"name": "谢切诺夫", "type": "角色", "aliases": ["Sechenov"]},
            {"name": "菲洛梅年科", "type": "角色", "aliases": ["Filomenenko"]},
            {"name": "聚合物氢电池", "type": "物品", "aliases": ["polymer hydrogen cell"]},
            {"name": "1939年", "type": "时间", "aliases": ["1939"]},
            {"name": "马克西姆", "type": "角色", "aliases": ["Maxim"]},
            {"name": "瘟疫", "type": "事件", "aliases": ["plague"]},
            {"name": "机器人学", "type": "概念", "aliases": ["robotics"]},
        ],
        "relations": [
            {"src": "谢切诺夫", "dst": "聚合物氢电池", "relation": "发明", "confidence": 0.9},
            {"src": "菲洛梅年科", "dst": "聚合物氢电池", "relation": "共同发明",
             "confidence": 0.9},
            {"src": "聚合物氢电池", "dst": "机器人学", "relation": "推动", "confidence": 0.9},
            {"src": "瘟疫", "dst": "马克西姆", "relation": "被提及", "confidence": 0.7},
        ],
    },
    "ca8ef9de1870635d": {
        "entities": [
            {"name": "暴雨", "type": "事件", "aliases": ["Storm", "The Storm"]},
            {"name": "太空", "type": "地点", "aliases": ["space"]},
            {"name": "地球", "type": "地点", "aliases": ["Earth"]},
            {"name": "同事", "type": "概念", "aliases": ["staff"]},
        ],
        "relations": [
            {"src": "暴雨", "dst": "太空", "relation": "需验证影响", "confidence": 0.8},
            {"src": "暴雨", "dst": "地球", "relation": "可能仅影响", "confidence": 0.7},
            {"src": "暴雨", "dst": "同事", "relation": "威胁", "confidence": 0.8},
        ],
    },
    "eda125453bb3ea54": {
        "entities": [
            {"name": "暴雨", "type": "事件", "aliases": ["Storm", "The Storm"]},
            {"name": "太阳", "type": "概念", "aliases": ["Sun"]},
            {"name": "地球", "type": "地点", "aliases": ["Earth"]},
            {"name": "宇宙", "type": "概念", "aliases": ["universe"]},
            {"name": "外星生命", "type": "概念", "aliases": ["alien life"]},
        ],
        "relations": [
            {"src": "太阳", "dst": "地球", "relation": "可能吞噬", "confidence": 0.7},
            {"src": "暴雨", "dst": "地球", "relation": "可能吞噬", "confidence": 0.7},
            {"src": "外星生命", "dst": "宇宙", "relation": "可能存在", "confidence": 0.6},
        ],
    },
    "6478ae68cff3faf7": {
        "entities": [
            {"name": "APPLe", "type": "角色",
             "aliases": ["Apple", "苹果", "Signore Apple"]},
            {"name": "滤光片", "type": "物品", "aliases": ["optical filter"]},
            {"name": "颜料", "type": "物品", "aliases": ["pigment"]},
            {"name": "日落", "type": "概念", "aliases": ["sunset"]},
        ],
        "relations": [
            {"src": "滤光片", "dst": "颜料", "relation": "使其显现", "confidence": 0.9},
            {"src": "日落", "dst": "滤光片", "relation": "原理相同", "confidence": 0.7},
        ],
    },
    "8c7de00250fdecd2": {
        "entities": [
            {"name": "圣洛夫基金会", "type": "组织", "aliases": ["Foundation"]},
            {"name": "暴雨", "type": "事件", "aliases": ["Storm", "The Storm"]},
            {"name": "肺鱼", "type": "概念", "aliases": ["lungfish"]},
        ],
        "relations": [
            {"src": "肺鱼", "dst": "暴雨", "relation": "创造", "confidence": 0.7},
            {"src": "圣洛夫基金会", "dst": "肺鱼", "relation": "不容身", "confidence": 0.8},
        ],
    },
    "e3d80068fdba0bae": {
        "entities": [
            {"name": "莎士比亚", "type": "角色", "aliases": ["Shakespeare"]},
            {"name": "音素", "type": "概念", "aliases": ["phonemes"]},
            {"name": "语言", "type": "概念", "aliases": ["language"]},
            {"name": "风", "type": "概念", "aliases": ["wind"]},
            {"name": "语言显微镜", "type": "概念", "aliases": ["language microscope"]},
        ],
        "relations": [
            {"src": "风", "dst": "语言", "relation": "拆解", "confidence": 0.9},
            {"src": "音素", "dst": "语言", "relation": "构成", "confidence": 0.9},
            {"src": "语言显微镜", "dst": "风", "relation": "类比", "confidence": 0.7},
        ],
    },
    "ee0168ea471df5cd": {
        "entities": [
            {"name": "暴雨", "type": "事件", "aliases": ["Storm", "The Storm"]},
            {"name": "重塑之手", "type": "组织",
             "aliases": ["Manus Vindictae", "Manus Vindictive", "Manus"]},
            {"name": "难民", "type": "概念", "aliases": ["refugees"]},
            {"name": "人类", "type": "概念", "aliases": []},
            {"name": "决议", "type": "事件", "aliases": ["resolution"]},
        ],
        "relations": [
            {"src": "暴雨", "dst": "人类", "relation": "吞噬亲友", "confidence": 0.9},
            {"src": "重塑之手", "dst": "暴雨", "relation": "揭露存在", "confidence": 0.9},
            {"src": "决议", "dst": "难民", "relation": "导致涌入", "confidence": 0.8},
        ],
    },
    "908f4648bc5ab6f5": {
        "entities": [
            {"name": "迪特里希", "type": "角色", "aliases": ["Dietrich"]},
            {"name": "穆尔贝格先生", "type": "角色",
             "aliases": ["Herr Müllberger", "Müllberger"]},
            {"name": "黑板", "type": "物品", "aliases": ["blackboard"]},
            {"name": "战场", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "穆尔贝格先生", "dst": "迪特里希", "relation": "授课", "confidence": 0.8},
            {"src": "迪特里希", "dst": "战场", "relation": "阵亡", "confidence": 0.9},
        ],
    },
    "dda0358e5ccb0b4f": {
        "entities": [
            {"name": "暴雨", "type": "事件", "aliases": ["Storm", "The Storm"]},
            {"name": "项目", "type": "概念", "aliases": ["project"]},
            {"name": "万物", "type": "概念", "aliases": ["things, places, people"]},
        ],
        "relations": [
            {"src": "暴雨", "dst": "万物", "relation": "抹除", "confidence": 0.9},
            {"src": "项目", "dst": "暴雨", "relation": "需停止", "confidence": 0.8},
        ],
    },
    "453a1524cc089f12": {
        "entities": [
            {"name": "暴雨", "type": "事件", "aliases": ["Storm", "The Storm"]},
            {"name": "秘术能量", "type": "概念", "aliases": ["arcane energy"]},
            {"name": "可观测宇宙", "type": "概念", "aliases": ["observable universe"]},
            {"name": "太阳", "type": "概念", "aliases": ["sun"]},
        ],
        "relations": [
            {"src": "暴雨", "dst": "秘术能量", "relation": "放大", "confidence": 0.9},
            {"src": "太阳", "dst": "可观测宇宙", "relation": "非最大", "confidence": 0.9},
        ],
    },
    "5b8dcc85e7ee6326": {
        "entities": [
            {"name": "医生", "type": "角色", "aliases": ["doctor", "Doctor", "miss doctor"]},
            {"name": "仪式师", "type": "角色", "aliases": ["ritualist"]},
            {"name": "骑士", "type": "组织", "aliases": ["knights", "Knights"]},
            {"name": "修道院", "type": "地点", "aliases": ["monastery"]},
            {"name": "雪山", "type": "地点", "aliases": ["snowy mountain"]},
        ],
        "relations": [
            {"src": "骑士", "dst": "修道院", "relation": "居住", "confidence": 0.9},
            {"src": "修道院", "dst": "雪山", "relation": "位于", "confidence": 0.9},
            {"src": "仪式师", "dst": "医生", "relation": "追捕孩童", "confidence": 0.7},
        ],
    },
    "07fd2ed827fa731e": {
        "entities": [
            {"name": "红38", "type": "物品", "aliases": ["Red 38"]},
            {"name": "飞天扫帚", "type": "物品", "aliases": ["broomstick", "Broomstick"]},
            {"name": "SU-01VE", "type": "物品", "aliases": []},
            {"name": "堡垒", "type": "地点", "aliases": ["fort"]},
        ],
        "relations": [
            {"src": "红38", "dst": "堡垒", "relation": "侦察", "confidence": 0.8},
            {"src": "飞天扫帚", "dst": "红38", "relation": "替代方案", "confidence": 0.6},
        ],
    },
    "cbbe0b9df6551fe9": {
        "entities": [
            {"name": "司辰", "type": "角色", "aliases": ["Timekeeper"]},
            {"name": "洋葱头", "type": "角色", "aliases": ["ONiON", "Onion", "Head Onion"]},
            {"name": "水上竞技会", "type": "事件",
             "aliases": ["aquatic game", "Aquatic Games"]},
        ],
        "relations": [
            {"src": "司辰", "dst": "水上竞技会", "relation": "招募队友", "confidence": 0.9},
            {"src": "洋葱头", "dst": "水上竞技会", "relation": "报道", "confidence": 0.9},
        ],
    },
    "467da57675f21332": {
        "entities": [
            {"name": "集体心智", "type": "概念", "aliases": ["collective mind"]},
            {"name": "时代", "type": "时间", "aliases": ["troubled times", "times"]},
            {"name": "冲突", "type": "概念", "aliases": ["conflicts"]},
            {"name": "海洋", "type": "概念", "aliases": ["ocean"]},
        ],
        "relations": [
            {"src": "集体心智", "dst": "冲突", "relation": "导致重复", "confidence": 0.9},
            {"src": "时代", "dst": "冲突", "relation": "频发", "confidence": 0.8},
        ],
    },
    "3ccb139370bf8abe": {
        "entities": [
            {"name": "科马拉", "type": "地点", "aliases": ["Kamala", "Komala"]},
            {"name": "流亡神秘学家", "type": "概念", "aliases": ["exiled arcanists"]},
            {"name": "作家", "type": "角色", "aliases": ["writer"]},
            {"name": "街道", "type": "地点", "aliases": ["streets"]},
        ],
        "relations": [
            {"src": "流亡神秘学家", "dst": "街道", "relation": "充斥", "confidence": 0.8},
            {"src": "作家", "dst": "科马拉", "relation": "前往", "confidence": 0.8},
        ],
    },
    "2d2fb32ba471b2b5": {
        "entities": [
            {"name": "圣洛夫基金会", "type": "组织", "aliases": ["Foundation", "foundation"]},
            {"name": "暴雨", "type": "事件", "aliases": ["Storm", "The Storm"]},
            {"name": "炼金术士", "type": "角色", "aliases": ["mad alchemist", "alchemist"]},
            {"name": "异常现象", "type": "概念", "aliases": ["anomalies"]},
            {"name": "员工委员会", "type": "组织", "aliases": ["staff committee"]},
        ],
        "relations": [
            {"src": "圣洛夫基金会", "dst": "异常现象", "relation": "报告", "confidence": 0.9},
            {"src": "员工委员会", "dst": "异常现象", "relation": "监测", "confidence": 0.9},
            {"src": "暴雨", "dst": "异常现象", "relation": "关联", "confidence": 0.8},
        ],
    },
    "28c7b73bc18ad722": {
        "entities": [
            {"name": "墨西哥城", "type": "地点", "aliases": ["Mexico City"]},
            {"name": "神秘学家", "type": "概念", "aliases": ["Arcanist", "arcanist"]},
            {"name": "暴雨", "type": "事件", "aliases": ["Storm", "The Storm"]},
            {"name": "壁画", "type": "物品", "aliases": ["mural"]},
            {"name": "分部", "type": "组织", "aliases": ["branch"]},
        ],
        "relations": [
            {"src": "暴雨", "dst": "墨西哥城", "relation": "引发移民潮", "confidence": 0.9},
            {"src": "神秘学家", "dst": "墨西哥城", "relation": "犯罪激增", "confidence": 0.9},
            {"src": "壁画", "dst": "分部", "relation": "位于", "confidence": 0.7},
        ],
    },
    "f3cbf1b46bba2bd0": {
        "entities": [
            {"name": "圣洛夫基金会", "type": "组织", "aliases": ["Foundation", "foundation"]},
            {"name": "总部", "type": "地点", "aliases": ["Headquarters", "headquarters"]},
            {"name": "不可逆点", "type": "概念", "aliases": ["points irreversible"]},
            {"name": "分部选址", "type": "地点", "aliases": ["branch site"]},
        ],
        "relations": [
            {"src": "不可逆点", "dst": "圣洛夫基金会", "relation": "提供安全区",
             "confidence": 0.8},
            {"src": "不可逆点", "dst": "分部选址", "relation": "可成为", "confidence": 0.8},
        ],
    },
    "a424a7c39d3829bb": {
        "entities": [
            {"name": "暴雨", "type": "事件", "aliases": ["Storm", "The Storm"]},
            {"name": "项目", "type": "概念", "aliases": ["project"]},
            {"name": "死亡", "type": "概念", "aliases": ["death"]},
        ],
        "relations": [
            {"src": "暴雨", "dst": "死亡", "relation": "后果未知", "confidence": 0.8},
            {"src": "项目", "dst": "暴雨", "relation": "冒险", "confidence": 0.8},
        ],
    },
    "2e8639b762f8318d": {
        "entities": [
            {"name": "克鲁托夫", "type": "角色", "aliases": ["Krutov"]},
            {"name": "士兵", "type": "组织", "aliases": ["soldiers"]},
            {"name": "战马", "type": "概念", "aliases": ["horses"]},
            {"name": "补给", "type": "物品", "aliases": ["supplies"]},
            {"name": "狮鹫", "type": "概念", "aliases": ["griffins", "Griffins"]},
        ],
        "relations": [
            {"src": "克鲁托夫", "dst": "补给", "relation": "获得", "confidence": 0.9},
            {"src": "士兵", "dst": "战马", "relation": "年少缺乏经验", "confidence": 0.8},
            {"src": "狮鹫", "dst": "克鲁托夫", "relation": "袭击其部", "confidence": 0.7},
        ],
    },
    "366b7e91ad177ca8": {
        "entities": [
            {"name": "火山", "type": "地点", "aliases": ["volcano"]},
            {"name": "悬崖", "type": "地点", "aliases": ["cliffs"]},
            {"name": "战船", "type": "物品", "aliases": ["ships"]},
            {"name": "熔岩之雨", "type": "事件", "aliases": ["shower of molten fire"]},
        ],
        "relations": [
            {"src": "熔岩之雨", "dst": "战船", "relation": "降临", "confidence": 0.9},
            {"src": "战船", "dst": "火山", "relation": "被焚", "confidence": 0.9},
            {"src": "悬崖", "dst": "火山", "relation": "攀爬", "confidence": 0.8},
        ],
    },
    "7a6fd981858afd1d": {
        "entities": [
            {"name": "火山", "type": "地点", "aliases": ["volcano"]},
            {"name": "野兽", "type": "概念", "aliases": ["savage beast"]},
            {"name": "暴风雨", "type": "事件", "aliases": ["ravaging tempest", "tempest"]},
            {"name": "沉默", "type": "概念", "aliases": ["silence", "Silence"]},
        ],
        "relations": [
            {"src": "暴风雨", "dst": "火山", "relation": "肆虐", "confidence": 0.8},
            {"src": "野兽", "dst": "火山", "relation": "盘踞", "confidence": 0.7},
        ],
    },
    "54d091b770cd2594": {
        "entities": [
            {"name": "纳西索斯", "type": "角色", "aliases": ["Narcissus"]},
            {"name": "岛屿", "type": "地点", "aliases": ["island"]},
            {"name": "预言", "type": "概念", "aliases": ["prophesying"]},
        ],
        "relations": [
            {"src": "纳西索斯", "dst": "岛屿", "relation": "常客", "confidence": 0.8},
            {"src": "预言", "dst": "岛屿", "relation": "涉及", "confidence": 0.6},
        ],
    },
    "05d73f8689594cdc": {
        "entities": [
            {"name": "程勋俭", "type": "角色", "aliases": ["小程勋俭"]},
            {"name": "县衙差役", "type": "组织", "aliases": ["弟兄们"]},
            {"name": "酒楼", "type": "地点", "aliases": []},
            {"name": "鲈鱼", "type": "物品", "aliases": []},
            {"name": "城防", "type": "事件", "aliases": []},
            {"name": "俸禄", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "程勋俭", "dst": "酒楼", "relation": "宴请", "confidence": 0.9},
            {"src": "程勋俭", "dst": "城防", "relation": "负责", "confidence": 0.8},
            {"src": "程勋俭", "dst": "县衙差役", "relation": "统辖", "confidence": 0.9},
        ],
    },
    "728810636e0f433e": {
        "entities": [
            {"name": "地下墓穴", "type": "地点", "aliases": ["catacombs", "Catacombs"]},
            {"name": "革命者", "type": "组织", "aliases": ["revolutionaries"]},
            {"name": "士兵", "type": "组织", "aliases": ["soldiers"]},
            {"name": "城市", "type": "地点", "aliases": ["city"]},
        ],
        "relations": [
            {"src": "地下墓穴", "dst": "革命者", "relation": "被使用", "confidence": 0.9},
            {"src": "地下墓穴", "dst": "城市", "relation": "位于", "confidence": 0.8},
            {"src": "地下墓穴", "dst": "士兵", "relation": "被使用", "confidence": 0.8},
        ],
    },
    "247b94aede0bed46": {
        "entities": [
            {"name": "圣洛夫基金会", "type": "组织", "aliases": ["Foundation"]},
            {"name": "建筑设计", "type": "概念", "aliases": ["architectural design"]},
            {"name": "工程学", "type": "概念", "aliases": ["engineering"]},
            {"name": "城市规划", "type": "概念", "aliases": ["urban planning"]},
            {"name": "系统", "type": "概念", "aliases": ["system"]},
        ],
        "relations": [
            {"src": "圣洛夫基金会", "dst": "建筑设计", "relation": "需要", "confidence": 0.8},
            {"src": "圣洛夫基金会", "dst": "城市规划", "relation": "需要", "confidence": 0.8},
            {"src": "建筑设计", "dst": "系统", "relation": "组成", "confidence": 0.7},
        ],
    },
    "644c4f6fda85f1f2": {
        "entities": [
            {"name": "石料", "type": "物品", "aliases": ["stones"]},
            {"name": "石磨", "type": "物品", "aliases": ["millstone"]},
            {"name": "穹顶", "type": "地点", "aliases": ["dome"]},
            {"name": "墙体", "type": "地点", "aliases": ["walls"]},
        ],
        "relations": [
            {"src": "穹顶", "dst": "石料", "relation": "需要", "confidence": 0.9},
            {"src": "石料", "dst": "墙体", "relation": "取自", "confidence": 0.9},
        ],
    },
    "ec6bd887ab422cb7": {
        "entities": [
            {"name": "脚手架", "type": "物品", "aliases": ["scaffolds"]},
            {"name": "安全规定", "type": "概念", "aliases": ["safety rules"]},
            {"name": "拆除", "type": "事件", "aliases": ["demolition"]},
            {"name": "工资", "type": "概念", "aliases": ["salary"]},
        ],
        "relations": [
            {"src": "安全规定", "dst": "工资", "relation": "违反扣", "confidence": 0.9},
            {"src": "拆除", "dst": "脚手架", "relation": "需先固定", "confidence": 0.9},
        ],
    },
    "2ae436c6a15c12fb": {
        "entities": [
            {"name": "船长", "type": "角色", "aliases": ["captain", "Captain"]},
            {"name": "下降风", "type": "概念", "aliases": ["catabatic winds"]},
            {"name": "南设得兰群岛", "type": "地点", "aliases": ["South Shetland Islands"]},
            {"name": "阿德利企鹅", "type": "概念", "aliases": ["Adélie penguins"]},
            {"name": "冰碛", "type": "地点", "aliases": ["moraine"]},
        ],
        "relations": [
            {"src": "船长", "dst": "下降风", "relation": "应对", "confidence": 0.9},
            {"src": "南设得兰群岛", "dst": "冰碛", "relation": "遍布", "confidence": 0.8},
            {"src": "阿德利企鹅", "dst": "南设得兰群岛", "relation": "栖息",
             "confidence": 0.8},
        ],
    },
    "e7b9cb272666ee81": {
        "entities": [
            {"name": "雪", "type": "概念", "aliases": ["snow", "Snow"]},
            {"name": "六分仪", "type": "物品", "aliases": ["sextant"]},
            {"name": "防风墙", "type": "物品", "aliases": ["windbreak"]},
            {"name": "通信设备", "type": "物品", "aliases": ["communication devices"]},
            {"name": "电磁干扰", "type": "概念", "aliases": ["EMI"]},
        ],
        "relations": [
            {"src": "六分仪", "dst": "雪", "relation": "导航", "confidence": 0.8},
            {"src": "防风墙", "dst": "通信设备", "relation": "优先于", "confidence": 0.8},
            {"src": "电磁干扰", "dst": "通信设备", "relation": "干扰", "confidence": 0.9},
        ],
    },
    "dd1b2912308f8a5e": {
        "entities": [
            {"name": "母神", "type": "角色", "aliases": ["Mother Spirit"]},
            {"name": "驯鹿", "type": "概念", "aliases": ["reindeer"]},
            {"name": "赛跑节", "type": "事件", "aliases": ["racing festival"]},
            {"name": "家乡", "type": "地点", "aliases": ["hometown"]},
        ],
        "relations": [
            {"src": "赛跑节", "dst": "驯鹿", "relation": "比赛", "confidence": 0.9},
            {"src": "赛跑节", "dst": "母神", "relation": "选出代言者", "confidence": 0.9},
            {"src": "家乡", "dst": "赛跑节", "relation": "每年举办", "confidence": 0.9},
        ],
    },
    "b1ef943dfadcdbcb": {
        "entities": [
            {"name": "仪式圣所", "type": "地点",
             "aliases": ["ritual sanctuary", "The sanctuary", "sanctuary"]},
            {"name": "火山", "type": "地点", "aliases": ["volcano"]},
            {"name": "藻类", "type": "概念", "aliases": ["algae"]},
            {"name": "城市", "type": "地点", "aliases": ["city"]},
            {"name": "纤维植物", "type": "物品", "aliases": ["fibrous plant"]},
            {"name": "食物", "type": "物品", "aliases": ["food"]},
        ],
        "relations": [
            {"src": "仪式圣所", "dst": "城市", "relation": "位于尽头", "confidence": 0.9},
            {"src": "藻类", "dst": "火山", "relation": "生长自山脚", "confidence": 0.9},
            {"src": "纤维植物", "dst": "食物", "relation": "作为", "confidence": 0.9},
        ],
    },
    "35e5b9c19b624ff1": {
        "entities": [
            {"name": "上帝", "type": "角色", "aliases": ["God"]},
            {"name": "巴别塔", "type": "概念", "aliases": ["Babel"]},
            {"name": "尼尼微", "type": "地点", "aliases": ["Nineveh"]},
            {"name": "现代化", "type": "概念", "aliases": ["artifices of modernity"]},
        ],
        "relations": [
            {"src": "尼尼微", "dst": "上帝", "relation": "听从", "confidence": 0.8},
            {"src": "巴别塔", "dst": "现代化", "relation": "类比", "confidence": 0.7},
        ],
    },
    "da926867c97b9375": {
        "entities": [
            {"name": "将军", "type": "角色", "aliases": ["general", "General"]},
            {"name": "军事法庭", "type": "组织", "aliases": ["court-martial"]},
            {"name": "祖国", "type": "地点", "aliases": ["fatherland"]},
            {"name": "1920年", "type": "时间", "aliases": ["1920"]},
            {"name": "战争", "type": "事件", "aliases": ["war"]},
        ],
        "relations": [
            {"src": "将军", "dst": "军事法庭", "relation": "受审", "confidence": 0.9},
            {"src": "战争", "dst": "1920年", "relation": "结束", "confidence": 0.9},
        ],
    },
    "d1589b94df854578": {
        "entities": [
            {"name": "人道主义口粮", "type": "物品", "aliases": ["humanitarian rations"]},
            {"name": "敌军", "type": "组织", "aliases": ["the other side"]},
            {"name": "死者", "type": "概念", "aliases": ["the dead"]},
        ],
        "relations": [
            {"src": "人道主义口粮", "dst": "敌军", "relation": "分发", "confidence": 0.9},
            {"src": "死者", "dst": "人道主义口粮", "relation": "不合时宜", "confidence": 0.6},
        ],
    },
    "aeb6ea076f3599ad": {
        "entities": [
            {"name": "灵薄狱", "type": "概念", "aliases": ["limbo", "Limbo"]},
            {"name": "塞西诺布博士", "type": "角色",
             "aliases": ["Dr. Sesshinobu", "Sesshinobu"]},
            {"name": "私人保镖", "type": "角色", "aliases": ["personal body guard"]},
            {"name": "梦", "type": "概念", "aliases": ["dream", "Dream"]},
        ],
        "relations": [
            {"src": "塞西诺布博士", "dst": "私人保镖", "relation": "拥有", "confidence": 0.9},
            {"src": "灵薄狱", "dst": "梦", "relation": "疑问", "confidence": 0.6},
        ],
    },
    "ee8e0adda834f59a": {
        "entities": [
            {"name": "苏联", "type": "地点", "aliases": ["Soviet Union"]},
            {"name": "舞台", "type": "概念", "aliases": ["stage"]},
            {"name": "时间线", "type": "概念", "aliases": ["timeline"]},
            {"name": "动描术", "type": "概念", "aliases": ["Kinography"]},
        ],
        "relations": [
            {"src": "动描术", "dst": "苏联", "relation": "推断", "confidence": 0.9},
            {"src": "舞台", "dst": "苏联", "relation": "位于", "confidence": 0.8},
            {"src": "时间线", "dst": "苏联", "relation": "技术加速", "confidence": 0.8},
        ],
    },
    "2483f0766407ab60": {
        "entities": [
            {"name": "普莱西", "type": "地点", "aliases": ["placids", "Plessis"]},
            {"name": "火箭", "type": "物品", "aliases": ["rocket"]},
            {"name": "补给", "type": "物品", "aliases": ["supplies"]},
            {"name": "人力", "type": "概念", "aliases": ["manpower", "Manpower"]},
            {"name": "卢恩", "type": "物品", "aliases": ["runeum"]},
        ],
        "relations": [
            {"src": "补给", "dst": "普莱西", "relation": "来源", "confidence": 0.8},
            {"src": "人力", "dst": "补给", "relation": "需补充", "confidence": 0.9},
            {"src": "火箭", "dst": "普莱西", "relation": "停放", "confidence": 0.7},
        ],
    },
    "42c2ea51a44bbe7c": {
        "entities": [
            {"name": "银剑", "type": "物品", "aliases": ["swords"]},
            {"name": "冬季", "type": "时间", "aliases": ["winter"]},
            {"name": "雪", "type": "概念", "aliases": ["snow", "Snow"]},
            {"name": "迷路女孩", "type": "角色", "aliases": ["little girl"]},
            {"name": "山谷", "type": "地点", "aliases": ["valley"]},
        ],
        "relations": [
            {"src": "雪", "dst": "山谷", "relation": "掩埋", "confidence": 0.9},
            {"src": "迷路女孩", "dst": "雪", "relation": "迷途", "confidence": 0.9},
        ],
    },
    "2063e425bae427c7": {
        "entities": [
            {"name": "塔马罗夫卡", "type": "地点", "aliases": ["Tamarovka"]},
            {"name": "草原", "type": "地点", "aliases": ["steppe"]},
            {"name": "夜行", "type": "事件", "aliases": ["Night marches", "night marches"]},
            {"name": "军队", "type": "组织", "aliases": ["army"]},
            {"name": "危险", "type": "概念", "aliases": ["dangers"]},
        ],
        "relations": [
            {"src": "军队", "dst": "塔马罗夫卡", "relation": "宿营", "confidence": 0.8},
            {"src": "夜行", "dst": "危险", "relation": "伴随", "confidence": 0.8},
            {"src": "草原", "dst": "军队", "relation": "为…而战", "confidence": 0.7},
        ],
    },
    "8a34c95c316e7d85": {
        "entities": [
            {"name": "路四姐", "type": "角色", "aliases": []},
            {"name": "黄狗", "type": "概念", "aliases": []},
            {"name": "城门", "type": "地点", "aliases": []},
            {"name": "玉吊雪莲", "type": "物品", "aliases": []},
            {"name": "西域", "type": "地点", "aliases": []},
            {"name": "行李盘查", "type": "事件", "aliases": []},
            {"name": "咒语", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "黄狗", "dst": "城门", "relation": "冲撞", "confidence": 0.9},
            {"src": "行李盘查", "dst": "城门", "relation": "进行", "confidence": 0.9},
            {"src": "路四姐", "dst": "咒语", "relation": "念诵", "confidence": 0.8},
            {"src": "玉吊雪莲", "dst": "西域", "relation": "购自", "confidence": 0.7},
        ],
    },
}


def main() -> int:
    ap = argparse.ArgumentParser(description="补抽空块 第 3 批")
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
    print(f"[apply-p3] 写入 {written} 条，跳过 {skipped} 条")
    print(f"[apply-p3] NOOP 累计 {len(cur)} 条")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
