# -*- coding: utf-8 -*-
"""补抽 408 块空抽取中的第 5 批（71 块：未命中已知实体但有内容）。同 p1。"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from roleplay.config import get_settings  # noqa: E402

NOOP: list[str] = [
    "c49b17d67830eb68",  # 敲门找人场景，无专名
]

RESULTS: dict[str, dict] = {
    "06a5d2ee3c7f3805": {
        "entities": [
            {"name": "祖国", "type": "概念", "aliases": ["Vaterland"]},
            {"name": "战争", "type": "事件", "aliases": ["Krieg"]},
            {"name": "士兵", "type": "角色", "aliases": ["Soldat", "soldiers"]},
            {"name": "武器", "type": "物品", "aliases": ["Waffe"]},
            {"name": "死亡", "type": "概念", "aliases": ["Tod"]},
        ],
        "relations": [
            {"src": "士兵", "dst": "祖国", "relation": "为之战死", "confidence": 0.9},
            {"src": "战争", "dst": "死亡", "relation": "习以为常", "confidence": 0.8},
        ],
    },
    "6f7ccc09a82a8f56": {
        "entities": [
            {"name": "拉菲亚", "type": "角色", "aliases": ["Raffia"]},
            {"name": "鲍勃", "type": "角色", "aliases": ["Bob"]},
            {"name": "埃克尔斯顿队", "type": "组织", "aliases": ["Ecclestone team"]},
            {"name": "墙壁", "type": "地点", "aliases": ["walls"]},
            {"name": "砖块", "type": "物品", "aliases": ["bricks"]},
        ],
        "relations": [
            {"src": "鲍勃", "dst": "墙壁", "relation": "拆除", "confidence": 0.9},
            {"src": "拉菲亚", "dst": "埃克尔斯顿队", "relation": "协助", "confidence": 0.8},
            {"src": "鲍勃", "dst": "砖块", "relation": "搬运", "confidence": 0.8},
        ],
    },
    "464f04b163c94dce": {
        "entities": [
            {"name": "聚合物展览馆", "type": "地点",
             "aliases": ["Polymer Exhibition Hall"]},
            {"name": "米斯玛", "type": "角色", "aliases": ["Misma"]},
            {"name": "语音导览", "type": "物品", "aliases": ["Audio Guide"]},
        ],
        "relations": [
            {"src": "聚合物展览馆", "dst": "语音导览", "relation": "提供", "confidence": 0.9},
            {"src": "米斯玛", "dst": "聚合物展览馆", "relation": "到访", "confidence": 0.8},
        ],
    },
    "2e0fa658121caa36": {
        "entities": [
            {"name": "回响石", "type": "物品", "aliases": ["echo stones"]},
            {"name": "建筑", "type": "地点", "aliases": ["building"]},
            {"name": "图纸", "type": "物品", "aliases": ["drawings"]},
            {"name": "倒塌", "type": "事件", "aliases": ["collapse"]},
        ],
        "relations": [
            {"src": "回响石", "dst": "建筑", "relation": "共鸣", "confidence": 0.9},
            {"src": "建筑", "dst": "倒塌", "relation": "有风险", "confidence": 0.8},
        ],
    },
    "4e0bc7b18664b699": {
        "entities": [
            {"name": "公共之声", "type": "组织", "aliases": ["Public Voices"]},
            {"name": "电视采访", "type": "事件", "aliases": ["on-camera interview"]},
            {"name": "旧铁路", "type": "地点", "aliases": ["old railway"]},
            {"name": "工地", "type": "地点", "aliases": ["construction sites"]},
            {"name": "灯光", "type": "概念", "aliases": ["lights"]},
        ],
        "relations": [
            {"src": "公共之声", "dst": "电视采访", "relation": "请求", "confidence": 0.9},
            {"src": "工地", "dst": "灯光", "relation": "闪烁", "confidence": 0.8},
            {"src": "旧铁路", "dst": "工地", "relation": "相邻", "confidence": 0.6},
        ],
    },
    "6a1d1d66bd4f4700": {
        "entities": [
            {"name": "建筑", "type": "概念", "aliases": ["Buildings", "building"]},
            {"name": "汉佐", "type": "角色", "aliases": ["Hanzo"]},
            {"name": "以太里科", "type": "角色", "aliases": ["Etherico"]},
            {"name": "几何形状", "type": "概念",
             "aliases": ["Triangles, rectangles, circles"]},
        ],
        "relations": [
            {"src": "汉佐", "dst": "以太里科", "relation": "呼唤", "confidence": 0.8},
            {"src": "几何形状", "dst": "建筑", "relation": "遍布", "confidence": 0.8},
        ],
    },
    "d06cff2b8f64a47d": {
        "entities": [
            {"name": "咒文", "type": "概念", "aliases": ["incantation"]},
            {"name": "冰", "type": "概念", "aliases": ["ice"]},
            {"name": "寒冷", "type": "概念", "aliases": ["cold"]},
            {"name": "真知", "type": "概念", "aliases": ["true knowledge"]},
        ],
        "relations": [
            {"src": "咒文", "dst": "寒冷", "relation": "抵御", "confidence": 0.8},
            {"src": "真知", "dst": "冰", "relation": "清除", "confidence": 0.7},
        ],
    },
    "ea025365bf1a6857": {
        "entities": [
            {"name": "军队", "type": "组织", "aliases": ["armies"]},
            {"name": "战壕", "type": "地点", "aliases": ["trenches"]},
            {"name": "士兵", "type": "角色", "aliases": ["Soldiers", "soldiers"]},
            {"name": "虚构与现实的界限", "type": "概念",
             "aliases": ["lines between fiction and reality"]},
        ],
        "relations": [
            {"src": "士兵", "dst": "战壕", "relation": "爬行", "confidence": 0.9},
            {"src": "军队", "dst": "虚构与现实的界限", "relation": "使之模糊",
             "confidence": 0.7},
        ],
    },
    "5ab73f72e3237203": {
        "entities": [
            {"name": "回响石", "type": "物品", "aliases": ["Echo Stone", "echo stones"]},
            {"name": "建筑", "type": "地点", "aliases": ["building"]},
            {"name": "穹顶", "type": "地点", "aliases": ["dome"]},
            {"name": "落成仪式", "type": "事件", "aliases": ["ceremony"]},
            {"name": "灵魂", "type": "概念", "aliases": ["soul"]},
        ],
        "relations": [
            {"src": "回响石", "dst": "穹顶", "relation": "用于封顶", "confidence": 0.9},
            {"src": "建筑", "dst": "灵魂", "relation": "铭记", "confidence": 0.8},
            {"src": "落成仪式", "dst": "穹顶", "relation": "庆祝", "confidence": 0.8},
        ],
    },
    "6570452f67787405": {
        "entities": [
            {"name": "启蒙", "type": "概念", "aliases": ["enlightenment"]},
            {"name": "真知", "type": "概念", "aliases": ["true knowledge"]},
            {"name": "造物", "type": "概念", "aliases": ["creation"]},
        ],
        "relations": [
            {"src": "造物", "dst": "真知", "relation": "无法掌握", "confidence": 0.7},
            {"src": "启蒙", "dst": "真知", "relation": "通向", "confidence": 0.7},
        ],
    },
    "14d49161773e0634": {
        "entities": [
            {"name": "战壕", "type": "地点", "aliases": ["Schutzingraben"]},
            {"name": "士兵", "type": "角色", "aliases": ["Soldat", "soldiers"]},
            {"name": "死亡", "type": "概念", "aliases": ["Tod", "der Tod"]},
            {"name": "幽灵", "type": "概念", "aliases": ["Geister", "ghosts"]},
            {"name": "兄弟", "type": "概念", "aliases": ["Brüder"]},
        ],
        "relations": [
            {"src": "士兵", "dst": "战壕", "relation": "阵亡于", "confidence": 0.8},
            {"src": "死亡", "dst": "士兵", "relation": "嘲弄", "confidence": 0.7},
            {"src": "幽灵", "dst": "战壕", "relation": "徘徊", "confidence": 0.8},
        ],
    },
    "bebac9fd10cf6257": {
        "entities": [
            {"name": "横幅", "type": "物品", "aliases": ["banner"]},
            {"name": "逝者史", "type": "概念", "aliases": ["The history of the deceased"]},
            {"name": "牺牲", "type": "概念", "aliases": ["sacrifices"]},
            {"name": "成就", "type": "概念", "aliases": ["achievements"]},
            {"name": "音乐", "type": "概念", "aliases": ["music"]},
        ],
        "relations": [
            {"src": "逝者史", "dst": "横幅", "relation": "书写于", "confidence": 0.9},
            {"src": "牺牲", "dst": "成就", "relation": "推动", "confidence": 0.8},
            {"src": "音乐", "dst": "逝者史", "relation": "纪念", "confidence": 0.7},
        ],
    },
    "db68d019577f423a": {
        "entities": [
            {"name": "变异", "type": "概念", "aliases": ["mutation"]},
            {"name": "感染", "type": "事件", "aliases": ["Infected", "infected"]},
            {"name": "登记", "type": "事件", "aliases": ["registration"]},
            {"name": "症状", "type": "概念", "aliases": ["symptoms"]},
        ],
        "relations": [
            {"src": "感染", "dst": "变异", "relation": "导致", "confidence": 0.8},
            {"src": "症状", "dst": "登记", "relation": "记录于", "confidence": 0.7},
        ],
    },
    "b1eaa2599a76edf3": {
        "entities": [
            {"name": "皮罗斯", "type": "角色", "aliases": ["Piros"]},
            {"name": "民兵营地", "type": "地点", "aliases": ["militia camp"]},
            {"name": "炸药", "type": "物品", "aliases": ["Explosives", "explosives"]},
        ],
        "relations": [
            {"src": "皮罗斯", "dst": "炸药", "relation": "缴获", "confidence": 0.9},
            {"src": "民兵营地", "dst": "炸药", "relation": "来源", "confidence": 0.9},
        ],
    },
    "f8664f2ea0832b8f": {
        "entities": [
            {"name": "车厢", "type": "物品", "aliases": ["carriages"]},
            {"name": "机车", "type": "物品", "aliases": ["locomotive"]},
            {"name": "理想主义", "type": "概念", "aliases": ["idealism"]},
            {"name": "乘客", "type": "概念", "aliases": ["passengers"]},
        ],
        "relations": [
            {"src": "机车", "dst": "车厢", "relation": "牵引", "confidence": 0.9},
            {"src": "车厢", "dst": "乘客", "relation": "运送", "confidence": 0.9},
        ],
    },
    "e8a71931ce9692ce": {
        "entities": [
            {"name": "壁画", "type": "物品", "aliases": ["murals", "paintings"]},
            {"name": "圣经场景", "type": "概念", "aliases": ["biblical scene"]},
            {"name": "希腊罗马神话", "type": "概念", "aliases": ["Greco-Roman mythology"]},
            {"name": "密室", "type": "地点", "aliases": ["secret chamber"]},
        ],
        "relations": [
            {"src": "壁画", "dst": "圣经场景", "relation": "排除", "confidence": 0.9},
            {"src": "壁画", "dst": "希腊罗马神话", "relation": "无关联", "confidence": 0.9},
            {"src": "壁画", "dst": "密室", "relation": "指向", "confidence": 0.8},
        ],
    },
    "6314b539edb88aea": {
        "entities": [
            {"name": "黑暗", "type": "概念", "aliases": ["darkness"]},
            {"name": "光", "type": "概念", "aliases": ["light"]},
            {"name": "呼吸", "type": "概念", "aliases": ["breath"]},
        ],
        "relations": [
            {"src": "黑暗", "dst": "光", "relation": "寻找", "confidence": 0.8},
        ],
    },
    "df5a4061886c6164": {
        "entities": [
            {"name": "巴比伦骰子", "type": "物品",
             "aliases": ["die of Babylon", "dado de Babilonia"]},
            {"name": "阿兹特克祭司", "type": "角色", "aliases": ["Aztec priest"]},
            {"name": "征服者", "type": "组织", "aliases": ["Conquistadores"]},
            {"name": "玛丽亚", "type": "角色", "aliases": ["María"]},
            {"name": "布宜诺斯艾利斯", "type": "地点", "aliases": ["Buenos Aires"]},
            {"name": "小说", "type": "物品", "aliases": ["novel"]},
        ],
        "relations": [
            {"src": "阿兹特克祭司", "dst": "巴比伦骰子", "relation": "创造",
             "confidence": 0.9},
            {"src": "征服者", "dst": "巴比伦骰子", "relation": "封印", "confidence": 0.8},
            {"src": "玛丽亚", "dst": "小说", "relation": "创作", "confidence": 0.8},
            {"src": "玛丽亚", "dst": "布宜诺斯艾利斯", "relation": "返回",
             "confidence": 0.8},
        ],
    },
    "35bc0bdab916d8f0": {
        "entities": [
            {"name": "穹顶", "type": "地点", "aliases": ["dome"]},
            {"name": "回响石", "type": "物品", "aliases": ["echo stones"]},
            {"name": "混凝土", "type": "物品", "aliases": ["concrete"]},
            {"name": "工地", "type": "地点", "aliases": ["site"]},
        ],
        "relations": [
            {"src": "混凝土", "dst": "回响石", "relation": "灌注", "confidence": 0.9},
            {"src": "回响石", "dst": "穹顶", "relation": "构成", "confidence": 0.9},
        ],
    },
    "30ddd20f44c94ff0": {
        "entities": [
            {"name": "玩具盒", "type": "物品", "aliases": ["toy box"]},
            {"name": "观测", "type": "概念", "aliases": ["observation"]},
            {"name": "门", "type": "地点", "aliases": ["door"]},
        ],
        "relations": [
            {"src": "玩具盒", "dst": "观测", "relation": "随…变化", "confidence": 0.9},
        ],
    },
    "4cda9436c4e46cf9": {
        "entities": [
            {"name": "神圣职责", "type": "概念", "aliases": ["sacred charge"]},
            {"name": "克制", "type": "概念", "aliases": ["restraint"]},
            {"name": "痛苦", "type": "概念", "aliases": ["pain"]},
        ],
        "relations": [
            {"src": "克制", "dst": "痛苦", "relation": "承受", "confidence": 0.9},
        ],
    },
    "90a8a3c51d48a17e": {
        "entities": [
            {"name": "荆棘长袍", "type": "物品", "aliases": ["gown with thorns"]},
            {"name": "牺牲", "type": "概念", "aliases": ["sacrifice"]},
            {"name": "建筑师", "type": "角色", "aliases": ["architect"]},
            {"name": "树枝", "type": "物品", "aliases": ["branches"]},
        ],
        "relations": [
            {"src": "荆棘长袍", "dst": "牺牲", "relation": "需以…偿还", "confidence": 0.8},
            {"src": "建筑师", "dst": "树枝", "relation": "引导众人登上", "confidence": 0.8},
        ],
    },
    "422ecf6ab5a660f9": {
        "entities": [
            {"name": "曼佩", "type": "地点", "aliases": ["Manpei"]},
            {"name": "刺杀", "type": "事件", "aliases": ["assassination"]},
            {"name": "和谈", "type": "事件", "aliases": ["peace talks"]},
            {"name": "调查员", "type": "角色", "aliases": ["investigators"]},
            {"name": "枪手", "type": "角色", "aliases": ["shooter"]},
        ],
        "relations": [
            {"src": "刺杀", "dst": "曼佩", "relation": "发生于", "confidence": 0.9},
            {"src": "刺杀", "dst": "和谈", "relation": "导致多国退出", "confidence": 0.9},
            {"src": "调查员", "dst": "枪手", "relation": "目击", "confidence": 0.9},
        ],
    },
    "6f8014ebac7df768": {
        "entities": [
            {"name": "潘家园", "type": "地点",
             "aliases": ["Panjayuan antique market", "Panjia Yuan"]},
            {"name": "古董", "type": "物品", "aliases": ["antique", "antiques"]},
            {"name": "微波炉", "type": "物品", "aliases": ["microwave ovens"]},
        ],
        "relations": [
            {"src": "潘家园", "dst": "古董", "relation": "出售", "confidence": 0.9},
            {"src": "古董", "dst": "微波炉", "relation": "可微波标识", "confidence": 0.8},
        ],
    },
    "1526d2f63b7a222b": {
        "entities": [
            {"name": "奇奇", "type": "角色", "aliases": ["Cici"]},
            {"name": "寻宝", "type": "概念", "aliases": ["searching for treasure"]},
            {"name": "焗土豆", "type": "物品", "aliases": ["gratin"]},
        ],
        "relations": [
            {"src": "奇奇", "dst": "寻宝", "relation": "同行", "confidence": 0.7},
        ],
    },
    "795f3c48fb1ce364": {
        "entities": [
            {"name": "聚会", "type": "事件", "aliases": ["party"]},
            {"name": "名单", "type": "物品", "aliases": ["list"]},
            {"name": "逝者", "type": "概念", "aliases": ["departed loved ones"]},
        ],
        "relations": [
            {"src": "聚会", "dst": "逝者", "relation": "纪念", "confidence": 0.9},
            {"src": "名单", "dst": "聚会", "relation": "关联", "confidence": 0.7},
        ],
    },
    "b5781cc1a3fe9a5d": {
        "entities": [
            {"name": "灰狗", "type": "角色", "aliases": ["Greyhound"]},
            {"name": "帽子", "type": "物品", "aliases": ["hat"]},
            {"name": "纺车", "type": "物品", "aliases": ["spinning wheels"]},
        ],
        "relations": [
            {"src": "灰狗", "dst": "帽子", "relation": "带回", "confidence": 0.9},
        ],
    },
    "77ed3446da1e65a6": {
        "entities": [
            {"name": "爱知群岛", "type": "地点", "aliases": ["Aicho Islands"]},
            {"name": "地衣", "type": "概念", "aliases": ["lichen"]},
            {"name": "岩石", "type": "概念", "aliases": ["rocks"]},
        ],
        "relations": [
            {"src": "地衣", "dst": "爱知群岛", "relation": "遍布", "confidence": 0.9},
            {"src": "岩石", "dst": "爱知群岛", "relation": "会移动", "confidence": 0.8},
        ],
    },
    "79e65b7b0e2edc79": {
        "entities": [
            {"name": "马图", "type": "角色", "aliases": ["Ma Tu"]},
            {"name": "遗迹", "type": "地点", "aliases": ["ruins"]},
            {"name": "天气", "type": "概念", "aliases": ["weather"]},
        ],
        "relations": [
            {"src": "马图", "dst": "遗迹", "relation": "判断可进入", "confidence": 0.8},
            {"src": "天气", "dst": "遗迹", "relation": "阻碍进入", "confidence": 0.8},
        ],
    },
    "1c75a311606c5c5e": {
        "entities": [
            {"name": "火山", "type": "地点", "aliases": ["volcano"]},
            {"name": "二氧化硫", "type": "概念", "aliases": ["sulfur dioxide"]},
            {"name": "熔岩", "type": "概念", "aliases": ["lava"]},
            {"name": "石塔", "type": "地点", "aliases": ["towers"]},
            {"name": "蜂巢", "type": "概念", "aliases": ["beehive"]},
        ],
        "relations": [
            {"src": "熔岩", "dst": "二氧化硫", "relation": "散发", "confidence": 0.9},
            {"src": "石塔", "dst": "蜂巢", "relation": "形似", "confidence": 0.9},
            {"src": "石塔", "dst": "火山", "relation": "出现于", "confidence": 0.8},
        ],
    },
    "900ca30bd4cf1d91": {
        "entities": [
            {"name": "火山", "type": "地点", "aliases": ["volcano"]},
            {"name": "地图", "type": "物品", "aliases": ["map"]},
            {"name": "危险区域", "type": "地点", "aliases": ["dangerous areas"]},
            {"name": "海拔", "type": "概念", "aliases": ["elevation"]},
        ],
        "relations": [
            {"src": "地图", "dst": "危险区域", "relation": "标注", "confidence": 0.9},
            {"src": "火山", "dst": "海拔", "relation": "为11616英尺", "confidence": 0.9},
        ],
    },
    "87e01522725a4448": {
        "entities": [
            {"name": "学校", "type": "地点", "aliases": ["school"]},
            {"name": "战争", "type": "事件", "aliases": ["war"]},
            {"name": "教官", "type": "角色", "aliases": ["instructor"]},
            {"name": "召唤阵", "type": "概念", "aliases": ["summoning"]},
        ],
        "relations": [
            {"src": "召唤阵", "dst": "学校", "relation": "用于脱离", "confidence": 0.8},
            {"src": "教官", "dst": "战争", "relation": "提及", "confidence": 0.8},
        ],
    },
    "e13cfaed1f5effab": {
        "entities": [
            {"name": "萨切尔博士", "type": "角色", "aliases": ["Dr. Satchel", "Satchel"]},
            {"name": "苏联科学家", "type": "组织", "aliases": ["Soviet scientist"]},
            {"name": "完美社会", "type": "概念", "aliases": ["perfect society"]},
            {"name": "2.0大事件", "type": "事件", "aliases": ["2.0 big event"]},
        ],
        "relations": [
            {"src": "萨切尔博士", "dst": "2.0大事件", "relation": "致辞", "confidence": 0.9},
            {"src": "苏联科学家", "dst": "完美社会", "relation": "追求", "confidence": 0.8},
        ],
    },
    "8b7973eae207e425": {
        "entities": [
            {"name": "双双五零", "type": "组织", "aliases": ["双双五零"]},
            {"name": "锁", "type": "物品", "aliases": ["lock"]},
            {"name": "门", "type": "地点", "aliases": ["door"]},
        ],
        "relations": [
            {"src": "双双五零", "dst": "门", "relation": "开启", "confidence": 0.8},
            {"src": "锁", "dst": "门", "relation": "已开启", "confidence": 0.8},
        ],
    },
    "b67f631d8c3985a0": {
        "entities": [
            {"name": "宇航员", "type": "角色", "aliases": ["astronaut"]},
            {"name": "太空", "type": "地点", "aliases": ["space"]},
            {"name": "邀约", "type": "概念", "aliases": ["offer"]},
        ],
        "relations": [
            {"src": "邀约", "dst": "宇航员", "relation": "邀请成为", "confidence": 0.9},
            {"src": "宇航员", "dst": "太空", "relation": "漂浮于", "confidence": 0.8},
        ],
    },
    "97197fd8966722f1": {
        "entities": [
            {"name": "走钢丝", "type": "概念", "aliases": ["tightrope"]},
            {"name": "杂技演员", "type": "角色", "aliases": ["acrobat"]},
            {"name": "观众", "type": "概念", "aliases": ["audience"]},
        ],
        "relations": [
            {"src": "杂技演员", "dst": "走钢丝", "relation": "表演", "confidence": 0.9},
            {"src": "观众", "dst": "走钢丝", "relation": "观看", "confidence": 0.8},
        ],
    },
    "7b03116fb175380b": {
        "entities": [
            {"name": "列车", "type": "物品", "aliases": ["train"]},
            {"name": "拘留室", "type": "地点", "aliases": ["detention room"]},
            {"name": "士兵", "type": "组织", "aliases": ["soldiers"]},
            {"name": "乘客", "type": "概念", "aliases": ["passengers"]},
        ],
        "relations": [
            {"src": "士兵", "dst": "拘留室", "relation": "看守", "confidence": 0.9},
            {"src": "士兵", "dst": "列车", "relation": "驻守", "confidence": 0.9},
            {"src": "列车", "dst": "乘客", "relation": "载有", "confidence": 0.8},
        ],
    },
    "b9d8f4151e299fca": {
        "entities": [
            {"name": "血迹", "type": "概念", "aliases": ["blood stain", "blood"]},
            {"name": "高层", "type": "组织", "aliases": ["big shots"]},
            {"name": "恢复计划", "type": "概念", "aliases": ["plan to restore"]},
        ],
        "relations": [
            {"src": "高层", "dst": "血迹", "relation": "迫使沾染", "confidence": 0.8},
            {"src": "恢复计划", "dst": "血迹", "relation": "旨在抹除", "confidence": 0.7},
        ],
    },
    "60d468998b461a3a": {
        "entities": [
            {"name": "Uccello", "type": "角色", "aliases": ["乌切洛"]},
            {"name": "彩色玻璃", "type": "物品", "aliases": ["stained glass"]},
            {"name": "线性透视", "type": "概念", "aliases": ["linear perspective"]},
            {"name": "自然", "type": "概念", "aliases": ["nature", "natural world"]},
        ],
        "relations": [
            {"src": "Uccello", "dst": "彩色玻璃", "relation": "举起", "confidence": 0.9},
            {"src": "线性透视", "dst": "自然", "relation": "超越临摹", "confidence": 0.8},
        ],
    },
    "23c49ac71d50d1f6": {
        "entities": [
            {"name": "理想主义者", "type": "角色",
             "aliases": ["Mr. Idealist", "Idealist"]},
            {"name": "短篇小说", "type": "物品",
             "aliases": ["short story", "Waitlessness", "historia corta"]},
            {"name": "鱼", "type": "概念", "aliases": ["pez", "fish"]},
            {"name": "太空", "type": "地点", "aliases": ["space"]},
        ],
        "relations": [
            {"src": "理想主义者", "dst": "短篇小说", "relation": "收到", "confidence": 0.8},
            {"src": "短篇小说", "dst": "鱼", "relation": "以…为题", "confidence": 0.8},
            {"src": "鱼", "dst": "太空", "relation": "漂浮于", "confidence": 0.7},
        ],
    },
    "451cc2160b026f09": {
        "entities": [
            {"name": "新成员", "type": "概念",
             "aliases": ["nuevos miembros", "new members"]},
            {"name": "小说", "type": "物品", "aliases": ["novel"]},
            {"name": "结构", "type": "概念", "aliases": ["estructura"]},
        ],
        "relations": [
            {"src": "新成员", "dst": "结构", "relation": "打乱", "confidence": 0.7},
        ],
    },
    "250b9fd470af84d0": {
        "entities": [
            {"name": "奥秘", "type": "概念", "aliases": ["Arkanum", "Arkane", "Arcanum"]},
            {"name": "秘术犯罪", "type": "事件", "aliases": ["Arkane crime"]},
            {"name": "波动", "type": "概念", "aliases": ["Fluctuations"]},
            {"name": "现场", "type": "地点", "aliases": ["scene"]},
            {"name": "仪式", "type": "概念", "aliases": ["ritual"]},
        ],
        "relations": [
            {"src": "奥秘", "dst": "现场", "relation": "遍布痕迹", "confidence": 0.9},
            {"src": "现场", "dst": "仪式", "relation": "曾举行", "confidence": 0.8},
            {"src": "波动", "dst": "现场", "relation": "追踪中断", "confidence": 0.9},
            {"src": "现场", "dst": "秘术犯罪", "relation": "判定为", "confidence": 0.8},
        ],
    },
    "57919b2bb85f93bb": {
        "entities": [
            {"name": "项目", "type": "概念", "aliases": ["project"]},
            {"name": "回响石", "type": "物品", "aliases": ["echo stones"]},
            {"name": "穹顶", "type": "地点", "aliases": ["dome"]},
            {"name": "三棱柱", "type": "物品", "aliases": ["triangular prism"]},
            {"name": "模型", "type": "物品", "aliases": ["model"]},
        ],
        "relations": [
            {"src": "回响石", "dst": "穹顶", "relation": "用于建造", "confidence": 0.9},
            {"src": "三棱柱", "dst": "模型", "relation": "最后放置", "confidence": 0.9},
            {"src": "模型", "dst": "项目", "relation": "阶段产物", "confidence": 0.8},
        ],
    },
    "054e0b2e795c22a3": {
        "entities": [
            {"name": "金字塔", "type": "地点", "aliases": ["pyramid"]},
            {"name": "墓地", "type": "地点", "aliases": ["cemetery"]},
            {"name": "明日", "type": "时间", "aliases": ["tomorrow"]},
        ],
        "relations": [
            {"src": "金字塔", "dst": "明日", "relation": "为…而升起", "confidence": 0.8},
            {"src": "墓地", "dst": "金字塔", "relation": "同被提及", "confidence": 0.6},
        ],
    },
    "3397c84c6a064257": {
        "entities": [
            {"name": "阿罗奈先生", "type": "角色", "aliases": ["Mr. Aronai", "Aronai"]},
            {"name": "投资", "type": "概念", "aliases": ["investment"]},
            {"name": "项目", "type": "概念", "aliases": ["project"]},
            {"name": "安全规程", "type": "概念", "aliases": ["safety protocols"]},
        ],
        "relations": [
            {"src": "阿罗奈先生", "dst": "安全规程", "relation": "关注", "confidence": 0.9},
            {"src": "投资", "dst": "项目", "relation": "有限", "confidence": 0.9},
        ],
    },
    "f13641657f8472a8": {
        "entities": [
            {"name": "艾瑞娜", "type": "角色", "aliases": ["Irenae"]},
            {"name": "办公室", "type": "地点", "aliases": ["office"]},
            {"name": "柏拉图三角", "type": "概念", "aliases": ["Plato's triangles"]},
            {"name": "矢车菊", "type": "物品", "aliases": ["corn flower"]},
            {"name": "工程师", "type": "角色", "aliases": ["engineer"]},
            {"name": "设计图", "type": "物品", "aliases": ["draft"]},
            {"name": "结构", "type": "概念", "aliases": ["structure"]},
        ],
        "relations": [
            {"src": "柏拉图三角", "dst": "结构", "relation": "支撑", "confidence": 0.9},
            {"src": "工程师", "dst": "设计图", "relation": "需审核", "confidence": 0.8},
            {"src": "艾瑞娜", "dst": "办公室", "relation": "拥有", "confidence": 0.9},
        ],
    },
    "debb865684d77bc7": {
        "entities": [
            {"name": "波兰饺子", "type": "物品", "aliases": ["pierogi"]},
            {"name": "摊位", "type": "地点", "aliases": ["stalls"]},
            {"name": "报告", "type": "物品", "aliases": ["report"]},
            {"name": "项目", "type": "概念", "aliases": ["project"]},
        ],
        "relations": [
            {"src": "报告", "dst": "项目", "relation": "调整", "confidence": 0.8},
            {"src": "摊位", "dst": "波兰饺子", "relation": "分发", "confidence": 0.7},
        ],
    },
    "d2c743dce6f8e832": {
        "entities": [
            {"name": "核心", "type": "物品", "aliases": ["core"]},
            {"name": "斯巴达", "type": "概念", "aliases": ["Sparta"]},
            {"name": "熵", "type": "概念", "aliases": ["entropy"]},
            {"name": "语言", "type": "概念", "aliases": ["language"]},
            {"name": "争夺", "type": "事件", "aliases": []},
        ],
        "relations": [
            {"src": "核心", "dst": "争夺", "relation": "目标", "confidence": 0.9},
            {"src": "熵", "dst": "语言", "relation": "达最小时精准", "confidence": 0.8},
        ],
    },
    "e99e955ef098cbbf": {
        "entities": [
            {"name": "维修站", "type": "地点", "aliases": ["repair station"]},
            {"name": "多功能维修装置", "type": "物品",
             "aliases": ["multifunctional repair device", "repair vendor"]},
            {"name": "原料", "type": "物品", "aliases": ["raw materials"]},
            {"name": "工具", "type": "物品", "aliases": ["tools"]},
        ],
        "relations": [
            {"src": "多功能维修装置", "dst": "维修站", "relation": "位于", "confidence": 0.9},
            {"src": "多功能维修装置", "dst": "原料", "relation": "改造为工具",
             "confidence": 0.9},
        ],
    },
    "276fa366aed9668f": {
        "entities": [
            {"name": "杂技演员", "type": "角色", "aliases": ["acrobat"]},
            {"name": "钢丝", "type": "物品", "aliases": ["wire"]},
            {"name": "观众", "type": "概念", "aliases": ["audience"]},
        ],
        "relations": [
            {"src": "杂技演员", "dst": "钢丝", "relation": "行走", "confidence": 0.9},
            {"src": "观众", "dst": "杂技演员", "relation": "观看", "confidence": 0.8},
        ],
    },
    "cd0d1ea8d33c1fdd": {
        "entities": [
            {"name": "疏散", "type": "事件", "aliases": ["evacuation"]},
            {"name": "新兵", "type": "组织", "aliases": ["new recruits"]},
            {"name": "露天矿坑", "type": "地点", "aliases": ["open mining pit"]},
            {"name": "士兵", "type": "组织", "aliases": ["soldiers"]},
            {"name": "命令", "type": "概念", "aliases": ["orders"]},
        ],
        "relations": [
            {"src": "疏散", "dst": "新兵", "relation": "不宜承担", "confidence": 0.8},
            {"src": "士兵", "dst": "命令", "relation": "遵从", "confidence": 0.8},
            {"src": "露天矿坑", "dst": "疏散", "relation": "目的地", "confidence": 0.7},
        ],
    },
    "c5558af855d0dd89": {
        "entities": [
            {"name": "人道主义支援人员", "type": "角色",
             "aliases": ["humanitarian support staff"]},
            {"name": "发射舱门", "type": "地点", "aliases": ["launch bay doors"]},
            {"name": "通讯器", "type": "物品", "aliases": ["communicators"]},
            {"name": "集合", "type": "事件", "aliases": []},
        ],
        "relations": [
            {"src": "发射舱门", "dst": "集合", "relation": "地点", "confidence": 0.9},
            {"src": "通讯器", "dst": "人道主义支援人员", "relation": "联络",
             "confidence": 0.8},
        ],
    },
    "75468567a66663c4": {
        "entities": [
            {"name": "宇宙", "type": "概念", "aliases": ["universe"]},
            {"name": "答案", "type": "概念", "aliases": ["answers"]},
            {"name": "过去", "type": "时间", "aliases": ["past"]},
            {"name": "未来", "type": "时间", "aliases": ["future"]},
        ],
        "relations": [
            {"src": "宇宙", "dst": "答案", "relation": "无从寻获", "confidence": 0.8},
            {"src": "过去", "dst": "未来", "relation": "不悔", "confidence": 0.7},
        ],
    },
    "4ebc542cd55fc88d": {
        "entities": [
            {"name": "画家", "type": "角色", "aliases": ["painter"]},
            {"name": "透明玻璃", "type": "概念", "aliases": ["sheet of transparent glass"]},
            {"name": "自然", "type": "概念", "aliases": ["natural world"]},
            {"name": "心如明镜", "type": "概念", "aliases": ["Minds as a mirror"]},
        ],
        "relations": [
            {"src": "画家", "dst": "透明玻璃", "relation": "心应如", "confidence": 0.9},
            {"src": "透明玻璃", "dst": "自然", "relation": "折射重构", "confidence": 0.8},
            {"src": "心如明镜", "dst": "画家", "relation": "被否定", "confidence": 0.8},
        ],
    },
    "cd43c5afa4288715": {
        "entities": [
            {"name": "警察", "type": "角色", "aliases": ["police"]},
            {"name": "宝石", "type": "物品", "aliases": ["shiny stones"]},
            {"name": "父母", "type": "角色", "aliases": ["parents"]},
        ],
        "relations": [
            {"src": "父母", "dst": "宝石", "relation": "痴迷", "confidence": 0.8},
        ],
    },
    "ecdba2c3b244abe2": {
        "entities": [
            {"name": "玻利瓦尔街", "type": "地点", "aliases": ["Calle Bolívar"]},
            {"name": "瞎眼女人", "type": "角色", "aliases": ["blind woman"]},
            {"name": "邮局", "type": "地点", "aliases": ["post office"]},
        ],
        "relations": [
            {"src": "瞎眼女人", "dst": "玻利瓦尔街", "relation": "呼唤于", "confidence": 0.9},
            {"src": "邮局", "dst": "玻利瓦尔街", "relation": "位于", "confidence": 0.7},
        ],
    },
    "ec491301a7df232b": {
        "entities": [
            {"name": "文学", "type": "概念", "aliases": ["literature"]},
            {"name": "万花筒", "type": "物品", "aliases": ["kaleidoscope"]},
            {"name": "视角", "type": "概念", "aliases": ["perspective"]},
        ],
        "relations": [
            {"src": "文学", "dst": "万花筒", "relation": "令人如", "confidence": 0.8},
            {"src": "文学", "dst": "视角", "relation": "表达", "confidence": 0.7},
        ],
    },
    "bfbc462c0afca939": {
        "entities": [
            {"name": "内脏现实主义", "type": "概念", "aliases": ["visceral realist"]},
            {"name": "诗歌", "type": "概念", "aliases": ["poetry"]},
            {"name": "监狱", "type": "地点", "aliases": ["prison"]},
            {"name": "诗人", "type": "角色", "aliases": ["poets"]},
            {"name": "生死边界", "type": "概念",
             "aliases": ["boundaries of life and death"]},
        ],
        "relations": [
            {"src": "诗歌", "dst": "生死边界", "relation": "架桥", "confidence": 0.8},
            {"src": "监狱", "dst": "诗人", "relation": "庇护", "confidence": 0.8},
        ],
    },
    "fad253ca4735805f": {
        "entities": [
            {"name": "流亡者", "type": "概念", "aliases": ["exiliados", "exiled"]},
            {"name": "文学之路", "type": "概念",
             "aliases": ["camino de la literatura"]},
            {"name": "古老传说", "type": "概念", "aliases": ["antigua leyenda"]},
            {"name": "通用语言", "type": "概念", "aliases": ["idioma genérico"]},
        ],
        "relations": [
            {"src": "流亡者", "dst": "文学之路", "relation": "坚守", "confidence": 0.8},
            {"src": "古老传说", "dst": "通用语言", "relation": "欲创造", "confidence": 0.7},
        ],
    },
    "24fb4fb7317bbf8b": {
        "entities": [
            {"name": "项目", "type": "概念", "aliases": ["project"]},
            {"name": "当地工人", "type": "组织", "aliases": ["locals", "new workers"]},
            {"name": "保密协议", "type": "概念", "aliases": ["confidentiality protocols"]},
            {"name": "能源使用", "type": "概念", "aliases": ["energy usage"]},
        ],
        "relations": [
            {"src": "项目", "dst": "能源使用", "relation": "改变", "confidence": 0.8},
            {"src": "当地工人", "dst": "保密协议", "relation": "不合规", "confidence": 0.8},
        ],
    },
    "97585ab7575d15fa": {
        "entities": [
            {"name": "维耶哈", "type": "物品", "aliases": ["vieja"]},
            {"name": "松枝", "type": "物品", "aliases": ["pine branches"]},
            {"name": "缎带", "type": "物品", "aliases": ["ribbons"]},
            {"name": "新建筑", "type": "地点", "aliases": ["new building"]},
        ],
        "relations": [
            {"src": "维耶哈", "dst": "新建筑", "relation": "悬挂于顶", "confidence": 0.9},
            {"src": "松枝", "dst": "维耶哈", "relation": "制成", "confidence": 0.9},
            {"src": "缎带", "dst": "维耶哈", "relation": "制成", "confidence": 0.9},
        ],
    },
    "de22d3f55094c453": {
        "entities": [
            {"name": "舞厅", "type": "地点", "aliases": ["ballroom"]},
            {"name": "世界末日", "type": "概念", "aliases": ["world going to end"]},
            {"name": "雨", "type": "事件", "aliases": ["Drizzling", "rain"]},
        ],
        "relations": [
            {"src": "世界末日", "dst": "雨", "relation": "联想", "confidence": 0.7},
        ],
    },
    "9f1654dbcefad457": {
        "entities": [
            {"name": "时间异常", "type": "事件", "aliases": ["temporal anomaly"]},
            {"name": "幸存者", "type": "概念", "aliases": ["survivors"]},
            {"name": "建筑免疫", "type": "概念", "aliases": ["immune"]},
            {"name": "怪雨", "type": "事件", "aliases": ["strange rain", "rain"]},
        ],
        "relations": [
            {"src": "时间异常", "dst": "幸存者", "relation": "产生", "confidence": 0.9},
            {"src": "幸存者", "dst": "建筑免疫", "relation": "见证", "confidence": 0.8},
            {"src": "怪雨", "dst": "幸存者", "relation": "被经历", "confidence": 0.8},
        ],
    },
    "1b188c7ea1ee4fcb": {
        "entities": [
            {"name": "布里莱", "type": "角色", "aliases": ["Brilay"]},
            {"name": "迷宫", "type": "地点", "aliases": ["labyrinth"]},
            {"name": "神庙遗迹", "type": "地点", "aliases": ["ruins of a temple"]},
            {"name": "异常白雾", "type": "事件", "aliases": ["abnormal whiteout"]},
            {"name": "石墙", "type": "物品", "aliases": ["stone wall"]},
            {"name": "挖掘痕迹", "type": "概念", "aliases": ["excavation marks"]},
        ],
        "relations": [
            {"src": "布里莱", "dst": "迷宫", "relation": "判断位置", "confidence": 0.8},
            {"src": "神庙遗迹", "dst": "迷宫", "relation": "位于其后", "confidence": 0.8},
            {"src": "石墙", "dst": "挖掘痕迹", "relation": "有", "confidence": 0.8},
            {"src": "异常白雾", "dst": "神庙遗迹", "relation": "阻碍勘察",
             "confidence": 0.8},
        ],
    },
    "35270387eb611923": {
        "entities": [
            {"name": "巴别塔", "type": "地点", "aliases": ["Tower of Babel"]},
            {"name": "物质状态", "type": "概念", "aliases": ["solid or a liquid"]},
        ],
        "relations": [
            {"src": "巴别塔", "dst": "物质状态", "relation": "质疑", "confidence": 0.6},
        ],
    },
    "024c568a67a6e244": {
        "entities": [
            {"name": "学校", "type": "地点", "aliases": ["school"]},
            {"name": "逃亡计划", "type": "概念", "aliases": ["escape plans"]},
            {"name": "学生", "type": "角色", "aliases": ["students"]},
            {"name": "秘密基地", "type": "概念", "aliases": ["secret hideout"]},
        ],
        "relations": [
            {"src": "学生", "dst": "学校", "relation": "逃离", "confidence": 0.9},
            {"src": "逃亡计划", "dst": "秘密基地", "relation": "滋养", "confidence": 0.7},
        ],
    },
    "d93ad7a749ebf251": {
        "entities": [
            {"name": "聚合物", "type": "物品", "aliases": ["Polymer"]},
            {"name": "先辈", "type": "概念", "aliases": ["forefathers"]},
            {"name": "科学", "type": "概念", "aliases": ["science"]},
            {"name": "研究团队", "type": "组织", "aliases": ["team"]},
        ],
        "relations": [
            {"src": "研究团队", "dst": "聚合物", "relation": "发明", "confidence": 0.9},
            {"src": "聚合物", "dst": "科学", "relation": "推动", "confidence": 0.8},
            {"src": "先辈", "dst": "科学", "relation": "奠基", "confidence": 0.8},
        ],
    },
    "728dcc21a2499800": {
        "entities": [
            {"name": "研究", "type": "概念", "aliases": ["research"]},
            {"name": "记录", "type": "物品", "aliases": ["records"]},
            {"name": "请愿书", "type": "物品", "aliases": ["petition"]},
            {"name": "团队", "type": "组织", "aliases": ["team"]},
        ],
        "relations": [
            {"src": "记录", "dst": "研究", "relation": "保存", "confidence": 0.9},
            {"src": "请愿书", "dst": "团队", "relation": "为…提交", "confidence": 0.8},
        ],
    },
    "b29f923e458bdcd9": {
        "entities": [
            {"name": "杂技演员", "type": "角色", "aliases": ["acrobat"]},
            {"name": "观众", "type": "概念", "aliases": ["audience"]},
            {"name": "大熊", "type": "角色", "aliases": ["big bear"]},
        ],
        "relations": [
            {"src": "观众", "dst": "杂技演员", "relation": "观看飞行与坠落",
             "confidence": 0.8},
        ],
    },
    "2af53230908548d2": {
        "entities": [
            {"name": "粒子", "type": "概念", "aliases": ["particles"]},
            {"name": "大脑", "type": "概念", "aliases": ["brains"]},
            {"name": "决定论", "type": "概念", "aliases": ["destined"]},
            {"name": "宇宙", "type": "概念", "aliases": ["universe"]},
            {"name": "时间", "type": "概念", "aliases": ["Past, present, future"]},
        ],
        "relations": [
            {"src": "粒子", "dst": "大脑", "relation": "构成", "confidence": 0.9},
            {"src": "宇宙", "dst": "决定论", "relation": "自起始注定", "confidence": 0.9},
            {"src": "时间", "dst": "决定论", "relation": "皆已注定", "confidence": 0.8},
        ],
    },
}


def main() -> int:
    ap = argparse.ArgumentParser(description="补抽空块 第 5 批")
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
    print(f"[apply-p5] 写入 {written} 条，跳过 {skipped} 条")
    print(f"[apply-p5] NOOP 累计 {len(cur)} 条")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
