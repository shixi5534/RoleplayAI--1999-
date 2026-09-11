# -*- coding: utf-8 -*-
"""补抽 408 块空抽取中的第 4 批（65 块，云端人工抽取）。同 apply_empty_p1.py。

本批含 3 块中文：v3.4 城市探索实录、神秘学家血统科普、小镇精神崩溃事件。
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
    "4948c01aa3d06baa",  # 市井劝离对白（school books / playground），无专名
    "3e4aaeb7c94a07f9",  # 告别寒暄（drowning / reunion），无专名
]

RESULTS: dict[str, dict] = {
    "aedcfc10e9500026": {
        "entities": [
            {"name": "巴黎", "type": "地点", "aliases": ["Paris"]},
            {"name": "城市最高建筑", "type": "地点",
             "aliases": ["the city's tallest structure"]},
            {"name": "神话深处", "type": "概念", "aliases": ["depths of myth"]},
            {"name": "高度", "type": "概念", "aliases": ["Altitude"]},
        ],
        "relations": [
            {"src": "巴黎", "dst": "城市最高建筑", "relation": "需登顶", "confidence": 0.8},
            {"src": "神话深处", "dst": "高度", "relation": "象征", "confidence": 0.7},
        ],
    },
    "af0083eb39dcf3c5": {
        "entities": [
            {"name": "暴雨", "type": "事件", "aliases": ["Storm", "The Storm", "storm"]},
            {"name": "群体癔症", "type": "概念", "aliases": ["mass hysteria"]},
            {"name": "世界舞台", "type": "概念", "aliases": ["world is a stage"]},
        ],
        "relations": [
            {"src": "暴雨", "dst": "群体癔症", "relation": "引发", "confidence": 0.8},
            {"src": "世界舞台", "dst": "暴雨", "relation": "比喻", "confidence": 0.7},
        ],
    },
    "f0efc26755ea0fd9": {
        "entities": [
            {"name": "暴雨", "type": "事件", "aliases": ["Storm", "The Storm"]},
            {"name": "命运", "type": "概念", "aliases": ["fate"]},
            {"name": "珠宝", "type": "物品", "aliases": ["jewels"]},
            {"name": "答案", "type": "概念", "aliases": ["answers"]},
        ],
        "relations": [
            {"src": "珠宝", "dst": "答案", "relation": "换取", "confidence": 0.8},
            {"src": "命运", "dst": "暴雨", "relation": "类比", "confidence": 0.7},
        ],
    },
    "0d41eee42feb5d84": {
        "entities": [
            {"name": "研究者", "type": "角色", "aliases": ["investigadora"]},
            {"name": "光谱同步", "type": "概念",
             "aliases": ["sincronización de sus espectros"]},
            {"name": "渔夫", "type": "角色", "aliases": ["hombre"]},
        ],
        "relations": [
            {"src": "研究者", "dst": "光谱同步", "relation": "识人", "confidence": 0.8},
            {"src": "研究者", "dst": "渔夫", "relation": "追问", "confidence": 0.7},
        ],
    },
    "2ead024e664a8e19": {
        "entities": [
            {"name": "展览", "type": "事件", "aliases": ["exhibición", "exhibition"]},
            {"name": "变化", "type": "概念", "aliases": ["cambio", "change"]},
            {"name": "稳定", "type": "概念", "aliases": ["estabilidad", "stability"]},
            {"name": "阴影", "type": "概念", "aliases": ["sombras", "shadows"]},
        ],
        "relations": [
            {"src": "展览", "dst": "变化", "relation": "需节奏", "confidence": 0.7},
            {"src": "变化", "dst": "稳定", "relation": "对立", "confidence": 0.7},
        ],
    },
    "0598d1e8a717d2f2": {
        "entities": [
            {"name": "加西亚", "type": "角色", "aliases": ["García", "Garcia"]},
            {"name": "惊奇画廊", "type": "地点",
             "aliases": ["galería de sorprendimiento", "gallery of surprise"]},
        ],
        "relations": [
            {"src": "加西亚", "dst": "惊奇画廊", "relation": "接待", "confidence": 0.7},
        ],
    },
    "aef42d9a83ef01fa": {
        "entities": [
            {"name": "低语", "type": "概念", "aliases": ["whisper of silence"]},
            {"name": "雏菊", "type": "物品", "aliases": ["daisies"]},
            {"name": "太阳", "type": "概念", "aliases": ["sun"]},
        ],
        "relations": [
            {"src": "雏菊", "dst": "太阳", "relation": "同被忆及", "confidence": 0.6},
        ],
    },
    "de0b3d30dafbdc30": {
        "entities": [
            {"name": "洪扎", "type": "角色", "aliases": ["Honza"]},
            {"name": "城市", "type": "地点", "aliases": ["city"]},
            {"name": "穹顶", "type": "地点", "aliases": ["dome"]},
        ],
        "relations": [
            {"src": "洪扎", "dst": "城市", "relation": "同行", "confidence": 0.8},
            {"src": "城市", "dst": "穹顶", "relation": "即将建成", "confidence": 0.9},
        ],
    },
    "81da641e732b0370": {
        "entities": [
            {"name": "PLAS", "type": "组织", "aliases": []},
            {"name": "穹顶", "type": "地点", "aliases": ["dome"]},
            {"name": "石样", "type": "物品", "aliases": ["stone samples"]},
            {"name": "免疫性", "type": "概念", "aliases": ["immunity"]},
        ],
        "relations": [
            {"src": "PLAS", "dst": "石样", "relation": "检测", "confidence": 0.9},
            {"src": "穹顶", "dst": "石样", "relation": "重建用", "confidence": 0.8},
            {"src": "石样", "dst": "免疫性", "relation": "具有", "confidence": 0.8},
        ],
    },
    "0150b086028c41ee": {
        "entities": [
            {"name": "罗西娅", "type": "角色", "aliases": ["Rosia"]},
            {"name": "回响石", "type": "物品", "aliases": ["echo stone", "echo stones"]},
            {"name": "建筑", "type": "地点", "aliases": ["building"]},
            {"name": "雨", "type": "事件", "aliases": ["rain"]},
        ],
        "relations": [
            {"src": "罗西娅", "dst": "回响石", "relation": "声音留存", "confidence": 0.9},
            {"src": "回响石", "dst": "建筑", "relation": "承载记忆", "confidence": 0.9},
        ],
    },
    "067629045205f8b0": {
        "entities": [
            {"name": "圣洛夫基金会", "type": "组织", "aliases": ["foundation", "Foundation"]},
            {"name": "报告", "type": "物品", "aliases": ["report"]},
            {"name": "工程", "type": "概念", "aliases": ["work"]},
        ],
        "relations": [
            {"src": "报告", "dst": "圣洛夫基金会", "relation": "提交", "confidence": 0.9},
            {"src": "工程", "dst": "圣洛夫基金会", "relation": "承接", "confidence": 0.7},
        ],
    },
    "f0d50f7624b592c9": {
        "entities": [
            {"name": "西翼", "type": "地点", "aliases": ["West Wing"]},
            {"name": "回响石", "type": "物品", "aliases": ["echo stones"]},
            {"name": "穹顶", "type": "地点", "aliases": ["dome"]},
        ],
        "relations": [
            {"src": "西翼", "dst": "回响石", "relation": "取材", "confidence": 0.9},
            {"src": "回响石", "dst": "穹顶", "relation": "用于重建", "confidence": 0.9},
        ],
    },
    "8e8df0a2757e9256": {
        "entities": [
            {"name": "青柠汁", "type": "物品", "aliases": ["lime juice"]},
            {"name": "中空地球", "type": "概念", "aliases": ["hollow earth"]},
            {"name": "绿洲", "type": "概念", "aliases": ["oasis"]},
            {"name": "冻伤", "type": "概念", "aliases": ["frostbite"]},
        ],
        "relations": [
            {"src": "中空地球", "dst": "绿洲", "relation": "被否定", "confidence": 0.8},
            {"src": "冻伤", "dst": "青柠汁", "relation": "同处困境", "confidence": 0.6},
        ],
    },
    "adc63950cc655f16": {
        "entities": [
            {"name": "重塑之手", "type": "组织", "aliases": ["Manus", "Manus Vindictae"]},
            {"name": "阴谋", "type": "事件", "aliases": ["scheme"]},
            {"name": "荒野", "type": "地点", "aliases": ["wilderness"]},
            {"name": "山顶", "type": "地点", "aliases": ["the top"]},
        ],
        "relations": [
            {"src": "重塑之手", "dst": "阴谋", "relation": "策划", "confidence": 0.9},
            {"src": "荒野", "dst": "山顶", "relation": "穿越可达", "confidence": 0.7},
        ],
    },
    "d1d0e25ee1512b57": {
        "entities": [
            {"name": "万物理论", "type": "概念",
             "aliases": ["a theory that unifies everything"]},
            {"name": "字谜", "type": "概念", "aliases": ["crossword"]},
            {"name": "睡眠", "type": "概念", "aliases": ["sleep"]},
            {"name": "人类", "type": "概念", "aliases": ["humanity"]},
            {"name": "说明书", "type": "物品", "aliases": ["instruction manual"]},
        ],
        "relations": [
            {"src": "万物理论", "dst": "字谜", "relation": "类比", "confidence": 0.8},
            {"src": "人类", "dst": "睡眠", "relation": "欲超越", "confidence": 0.8},
        ],
    },
    "871794a6b87bde9d": {
        "entities": [
            {"name": "音素", "type": "概念", "aliases": ["phonemes"]},
            {"name": "语言使用模拟", "type": "概念",
             "aliases": ["simulation of language use"]},
            {"name": "玻璃缸", "type": "物品", "aliases": ["glass tank"]},
            {"name": "玩具盒", "type": "地点", "aliases": ["toy box"]},
            {"name": "高塔", "type": "地点", "aliases": ["tower"]},
        ],
        "relations": [
            {"src": "语言使用模拟", "dst": "音素", "relation": "基于", "confidence": 0.9},
            {"src": "高塔", "dst": "玩具盒", "relation": "目标", "confidence": 0.7},
            {"src": "玻璃缸", "dst": "玩具盒", "relation": "位于其中", "confidence": 0.8},
        ],
    },
    "50492d5172423071": {
        "entities": [
            {"name": "伯顿", "type": "角色", "aliases": ["Burton"]},
            {"name": "报告", "type": "物品", "aliases": ["report"]},
            {"name": "技术发展分歧", "type": "概念",
             "aliases": ["divergence", "technological progression"]},
            {"name": "科学发现", "type": "概念", "aliases": ["scientific discovery"]},
        ],
        "relations": [
            {"src": "伯顿", "dst": "报告", "relation": "撰写", "confidence": 0.9},
            {"src": "报告", "dst": "技术发展分歧", "relation": "探讨", "confidence": 0.8},
            {"src": "科学发现", "dst": "技术发展分歧", "relation": "受环境塑造",
             "confidence": 0.7},
        ],
    },
    "8dfdec0b059e1ec7": {
        "entities": [
            {"name": "普列谢茨克", "type": "地点", "aliases": ["Plesetsk"]},
            {"name": "净化咒文", "type": "概念", "aliases": ["cleaning incantations"]},
            {"name": "植物仪式", "type": "概念", "aliases": ["plant-related rituals"]},
            {"name": "材料科学", "type": "概念", "aliases": ["material science"]},
            {"name": "航天工业", "type": "概念", "aliases": ["aerospace industry"]},
        ],
        "relations": [
            {"src": "普列谢茨克", "dst": "航天工业", "relation": "相关", "confidence": 0.8},
            {"src": "净化咒文", "dst": "植物仪式", "relation": "研究内容", "confidence": 0.8},
            {"src": "材料科学", "dst": "普列谢茨克", "relation": "选择理由", "confidence": 0.7},
        ],
    },
    "2df6dceeae1a8e83": {
        "entities": [
            {"name": "玛莎", "type": "角色", "aliases": ["Masha"]},
            {"name": "小熊", "type": "概念", "aliases": ["bear cub"]},
            {"name": "乌特连尼亚", "type": "地点", "aliases": ["utrenaya"]},
            {"name": "群星", "type": "概念", "aliases": ["stars"]},
        ],
        "relations": [
            {"src": "玛莎", "dst": "小熊", "relation": "是", "confidence": 0.9},
            {"src": "玛莎", "dst": "乌特连尼亚", "relation": "曾同眠", "confidence": 0.8},
        ],
    },
    "d342a8ec62552891": {
        "entities": [
            {"name": "赖泽尔", "type": "角色", "aliases": ["Reiser"]},
            {"name": "姜饼", "type": "物品", "aliases": ["gingerbread"]},
            {"name": "矿工", "type": "角色", "aliases": ["miners"]},
            {"name": "冬季", "type": "时间", "aliases": ["winter"]},
        ],
        "relations": [
            {"src": "赖泽尔", "dst": "姜饼", "relation": "制作", "confidence": 0.9},
            {"src": "矿工", "dst": "姜饼", "relation": "食用", "confidence": 0.8},
        ],
    },
    "7911f597eda3b48d": {
        "entities": [
            {"name": "米尔内", "type": "地点", "aliases": ["Myrniget", "Mirny"]},
            {"name": "宇航员", "type": "角色", "aliases": ["cosmonauts"]},
            {"name": "新鲜蔬果", "type": "物品",
             "aliases": ["fresh fruit and vegetables"]},
            {"name": "小镇", "type": "地点", "aliases": ["small town"]},
        ],
        "relations": [
            {"src": "宇航员", "dst": "新鲜蔬果", "relation": "技术来源", "confidence": 0.8},
            {"src": "小镇", "dst": "米尔内", "relation": "位于", "confidence": 0.7},
        ],
    },
    "d9ddbb7c322dc1ae": {
        "entities": [
            {"name": "暴雨", "type": "事件", "aliases": ["Storm", "The Storm", "storm"]},
            {"name": "外勤任务申请", "type": "物品",
             "aliases": ["field mission applications"]},
            {"name": "项目", "type": "概念", "aliases": ["project"]},
        ],
        "relations": [
            {"src": "外勤任务申请", "dst": "暴雨", "relation": "用于应对", "confidence": 0.8},
            {"src": "项目", "dst": "暴雨", "relation": "待解决", "confidence": 0.8},
        ],
    },
    "03dfbb78d4f93a56": {
        "entities": [
            {"name": "车票", "type": "物品", "aliases": ["ticket"]},
            {"name": "生存", "type": "概念", "aliases": ["survive"]},
            {"name": "饥饿", "type": "概念", "aliases": ["hadn't eaten"]},
        ],
        "relations": [
            {"src": "车票", "dst": "生存", "relation": "为…而取", "confidence": 0.8},
        ],
    },
    "ef319044d72a637a": {
        "entities": [
            {"name": "钻石", "type": "物品", "aliases": ["diamond"]},
            {"name": "诅咒", "type": "概念", "aliases": ["curse"]},
            {"name": "冒险", "type": "概念", "aliases": ["adventure", "Adventure"]},
            {"name": "父母", "type": "角色", "aliases": ["parents"]},
        ],
        "relations": [
            {"src": "钻石", "dst": "诅咒", "relation": "触发", "confidence": 0.8},
            {"src": "冒险", "dst": "钻石", "relation": "渴望", "confidence": 0.8},
        ],
    },
    "9e8a9ad11c779e02": {
        "entities": [
            {"name": "巴黎", "type": "地点", "aliases": ["Paris"]},
            {"name": "暴雨", "type": "事件", "aliases": ["rain", "coming rain"]},
            {"name": "时代", "type": "时间", "aliases": ["era"]},
            {"name": "错误", "type": "概念", "aliases": ["errors"]},
        ],
        "relations": [
            {"src": "暴雨", "dst": "巴黎", "relation": "冲刷", "confidence": 0.9},
            {"src": "时代", "dst": "巴黎", "relation": "将被抹去", "confidence": 0.8},
        ],
    },
    "2ead918bd0fcf3fa": {
        "entities": [
            {"name": "刺客", "type": "组织", "aliases": ["assassins", "Assassins"]},
            {"name": "赏金", "type": "物品", "aliases": ["reward"]},
            {"name": "城墙", "type": "地点", "aliases": ["wall"]},
            {"name": "比雷亚斯", "type": "地点", "aliases": ["Bireas"]},
        ],
        "relations": [
            {"src": "赏金", "dst": "刺客", "relation": "招致", "confidence": 0.8},
            {"src": "城墙", "dst": "比雷亚斯", "relation": "延伸至", "confidence": 0.7},
        ],
    },
    "b4ff90052ba36549": {
        "entities": [
            {"name": "司辰", "type": "角色", "aliases": ["Timekeeper"]},
            {"name": "研究者", "type": "角色", "aliases": ["researcher"]},
            {"name": "任命", "type": "事件", "aliases": ["appointment"]},
        ],
        "relations": [
            {"src": "研究者", "dst": "司辰", "relation": "要求会面", "confidence": 0.9},
            {"src": "任命", "dst": "研究者", "relation": "即将宣布", "confidence": 0.8},
        ],
    },
    "270e65e9672b396c": {
        "entities": [
            {"name": "司辰", "type": "角色", "aliases": ["Timekeeper"]},
            {"name": "暴雨", "type": "事件", "aliases": ["Storm", "The Storm", "storm"]},
            {"name": "新成员", "type": "概念", "aliases": ["new members"]},
            {"name": "增援", "type": "事件", "aliases": ["reinforce"]},
        ],
        "relations": [
            {"src": "增援", "dst": "司辰", "relation": "目标", "confidence": 0.9},
            {"src": "新成员", "dst": "暴雨", "relation": "首次经历", "confidence": 0.9},
        ],
    },
    "31c88b992410acf9": {
        "entities": [
            {"name": "灵魂", "type": "概念", "aliases": ["soul"]},
            {"name": "恶魔", "type": "概念", "aliases": ["demon", "wicked demon"]},
            {"name": "万人", "type": "概念", "aliases": ["ten thousand"]},
        ],
        "relations": [
            {"src": "恶魔", "dst": "灵魂", "relation": "蛊惑", "confidence": 0.7},
        ],
    },
    "7ff4f7731cfa8404": {
        "entities": [
            {"name": "大草原", "type": "地点", "aliases": ["Steppe", "steppe"]},
            {"name": "士兵", "type": "组织", "aliases": ["soldiers"]},
            {"name": "战争", "type": "事件", "aliases": ["war"]},
            {"name": "贪婪", "type": "概念", "aliases": ["greed"]},
            {"name": "怯懦", "type": "概念", "aliases": ["cowardice"]},
        ],
        "relations": [
            {"src": "战争", "dst": "大草原", "relation": "转向有利", "confidence": 0.8},
            {"src": "贪婪", "dst": "士兵", "relation": "蔓延", "confidence": 0.9},
            {"src": "怯懦", "dst": "士兵", "relation": "蔓延", "confidence": 0.9},
        ],
    },
    "1dead9b5ba934f1c": {
        "entities": [
            {"name": "永生", "type": "概念", "aliases": ["everlasting"]},
            {"name": "礼物", "type": "物品", "aliases": ["gift"]},
            {"name": "风险", "type": "概念", "aliases": ["risk"]},
            {"name": "梦想", "type": "概念", "aliases": ["dreams"]},
        ],
        "relations": [
            {"src": "礼物", "dst": "永生", "relation": "伴随", "confidence": 0.6},
            {"src": "风险", "dst": "梦想", "relation": "为…承担", "confidence": 0.7},
        ],
    },
    "f3ee14c362b22995": {
        "entities": [
            {"name": "铁路", "type": "组织", "aliases": ["railway"]},
            {"name": "军队", "type": "组织", "aliases": ["army"]},
            {"name": "徽章", "type": "物品", "aliases": ["badge"]},
            {"name": "车站", "type": "地点", "aliases": ["station"]},
            {"name": "战争", "type": "事件", "aliases": ["times of war"]},
            {"name": "调查", "type": "事件", "aliases": ["investigation"]},
        ],
        "relations": [
            {"src": "铁路", "dst": "军队", "relation": "合作", "confidence": 0.8},
            {"src": "车站", "dst": "铁路", "relation": "发车", "confidence": 0.8},
            {"src": "徽章", "dst": "调查", "relation": "关联", "confidence": 0.7},
        ],
    },
    "32bf6d82db79fe74": {
        "entities": [
            {"name": "露比", "type": "角色", "aliases": ["Ruby"]},
            {"name": "团结", "type": "概念", "aliases": ["unite as one"]},
            {"name": "手指", "type": "概念", "aliases": ["fingers"]},
        ],
        "relations": [
            {"src": "露比", "dst": "团结", "relation": "被询问", "confidence": 0.8},
            {"src": "手指", "dst": "团结", "relation": "比喻", "confidence": 0.8},
        ],
    },
    "233a290412cea2df": {
        "entities": [
            {"name": "瞎眼女人", "type": "角色", "aliases": ["blind woman"]},
            {"name": "乱世", "type": "时间", "aliases": ["chaotic times"]},
            {"name": "小丑", "type": "概念", "aliases": ["clowns"]},
            {"name": "宇宙", "type": "概念", "aliases": ["universe"]},
        ],
        "relations": [
            {"src": "瞎眼女人", "dst": "乱世", "relation": "被视为成因", "confidence": 0.7},
            {"src": "宇宙", "dst": "小丑", "relation": "沦为马戏团", "confidence": 0.7},
        ],
    },
    "b8c4275b6da197ad": {
        "entities": [
            {"name": "多伊卡", "type": "角色", "aliases": ["Dojka"]},
            {"name": "尘埃", "type": "概念", "aliases": ["dust", "Dust"]},
            {"name": "记忆", "type": "概念", "aliases": []},
            {"name": "火箭", "type": "物品", "aliases": ["rockets"]},
            {"name": "小号", "type": "物品", "aliases": ["trumpet"]},
        ],
        "relations": [
            {"src": "尘埃", "dst": "记忆", "relation": "拂去", "confidence": 0.8},
            {"src": "火箭", "dst": "记忆", "relation": "属于", "confidence": 0.7},
        ],
    },
    "61dc6e340a72dcc6": {
        "entities": [
            {"name": "狂风", "type": "事件", "aliases": ["gale"]},
            {"name": "众神", "type": "概念", "aliases": ["gods"]},
            {"name": "祭酒", "type": "物品", "aliases": ["wine"]},
            {"name": "仪式", "type": "概念", "aliases": ["rituals"]},
            {"name": "竞技会", "type": "事件", "aliases": ["games"]},
        ],
        "relations": [
            {"src": "仪式", "dst": "众神", "relation": "祭献", "confidence": 0.9},
            {"src": "竞技会", "dst": "仪式", "relation": "并列", "confidence": 0.8},
            {"src": "狂风", "dst": "仪式", "relation": "中举行", "confidence": 0.8},
        ],
    },
    "cd94643385df15c7": {
        "entities": [
            {"name": "提丰", "type": "角色", "aliases": ["Typhon"]},
            {"name": "火山碎屑闪电", "type": "事件", "aliases": ["pyroclastic lightning"]},
            {"name": "野兽", "type": "概念", "aliases": ["beast"]},
            {"name": "岛屿", "type": "地点", "aliases": ["island"]},
            {"name": "众神", "type": "概念", "aliases": ["godlets", "gods"]},
        ],
        "relations": [
            {"src": "野兽", "dst": "岛屿", "relation": "咆哮于", "confidence": 0.8},
            {"src": "野兽", "dst": "火山碎屑闪电", "relation": "发动", "confidence": 0.8},
            {"src": "提丰", "dst": "众神", "relation": "使人背弃", "confidence": 0.6},
        ],
    },
    "c64728c8c3f47dd2": {
        "entities": [
            {"name": "阳光", "type": "概念", "aliases": ["sunlight"]},
            {"name": "电磁波", "type": "概念", "aliases": ["electromagnetic radiation"]},
            {"name": "颜料", "type": "物品", "aliases": ["pigment"]},
            {"name": "红光", "type": "概念", "aliases": ["red light"]},
            {"name": "橙光", "type": "概念", "aliases": ["orange light"]},
        ],
        "relations": [
            {"src": "阳光", "dst": "电磁波", "relation": "由…组成", "confidence": 0.9},
            {"src": "颜料", "dst": "红光", "relation": "仅在其下可见", "confidence": 0.9},
            {"src": "颜料", "dst": "橙光", "relation": "仅在其下可见", "confidence": 0.8},
        ],
    },
    "be70314acbd7b492": {
        "entities": [
            {"name": "地下墓穴", "type": "地点", "aliases": ["catacombs", "Catacombs"]},
            {"name": "警察", "type": "组织", "aliases": ["police"]},
            {"name": "骷髅", "type": "概念", "aliases": ["skeletons"]},
            {"name": "迷宫", "type": "概念", "aliases": ["labyrinth"]},
            {"name": "禁区", "type": "地点", "aliases": ["restricted area"]},
        ],
        "relations": [
            {"src": "地下墓穴", "dst": "禁区", "relation": "起始", "confidence": 0.9},
            {"src": "地下墓穴", "dst": "骷髅", "relation": "陈放", "confidence": 0.9},
            {"src": "地下墓穴", "dst": "迷宫", "relation": "如", "confidence": 0.8},
        ],
    },
    "d74bc6ec47dcf26a": {
        "entities": [
            {"name": "巴黎", "type": "地点", "aliases": ["Paris", "La ville lumière"]},
            {"name": "时代", "type": "时间", "aliases": ["era"]},
            {"name": "小雨", "type": "事件", "aliases": ["rain"]},
            {"name": "意识形态", "type": "概念", "aliases": ["ideologies"]},
        ],
        "relations": [
            {"src": "小雨", "dst": "时代", "relation": "抹去", "confidence": 0.8},
            {"src": "巴黎", "dst": "意识形态", "relation": "包容", "confidence": 0.8},
        ],
    },
    "7db14d0c9c41cc1f": {
        "entities": [
            {"name": "芭芭拉", "type": "角色", "aliases": ["Barbara"]},
            {"name": "金家水井头", "type": "地点", "aliases": []},
            {"name": "咖啡店", "type": "地点", "aliases": []},
            {"name": "大槐树", "type": "地点", "aliases": ["大怀树", "怀树"]},
            {"name": "城中公园", "type": "地点", "aliases": []},
            {"name": "梅树", "type": "物品", "aliases": []},
            {"name": "郊区", "type": "地点", "aliases": []},
            {"name": "老房子", "type": "地点", "aliases": []},
            {"name": "木雕", "type": "物品", "aliases": []},
            {"name": "石雕", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "金家水井头", "dst": "大槐树", "relation": "位于其下", "confidence": 0.8},
            {"src": "城中公园", "dst": "梅树", "relation": "可观", "confidence": 0.8},
            {"src": "郊区", "dst": "老房子", "relation": "多有", "confidence": 0.7},
            {"src": "郊区", "dst": "木雕", "relation": "可看", "confidence": 0.7},
            {"src": "郊区", "dst": "石雕", "relation": "可看", "confidence": 0.7},
        ],
    },
    "28038a9fccc9cd04": {
        "entities": [
            {"name": "达西先生", "type": "角色", "aliases": ["Mr. Darcy", "Darcy"]},
            {"name": "外交官", "type": "角色", "aliases": ["diplomat", "Diplomat"]},
            {"name": "佩雷斯先生", "type": "角色", "aliases": ["Senor Perez", "Perez"]},
            {"name": "颜料", "type": "物品", "aliases": ["pigment"]},
            {"name": "俱乐部", "type": "地点", "aliases": ["club"]},
        ],
        "relations": [
            {"src": "俱乐部", "dst": "达西先生", "relation": "赠礼", "confidence": 0.8},
            {"src": "外交官", "dst": "颜料", "relation": "图谋", "confidence": 0.8},
            {"src": "佩雷斯先生", "dst": "颜料", "relation": "被牵涉", "confidence": 0.8},
        ],
    },
    "9d915f928d63c032": {
        "entities": [
            {"name": "神秘学家", "type": "概念", "aliases": ["Arcanist", "arcanist"]},
            {"name": "纯血种", "type": "概念", "aliases": []},
            {"name": "混血种", "type": "概念", "aliases": []},
            {"name": "感染种", "type": "概念", "aliases": []},
            {"name": "神秘术", "type": "概念", "aliases": []},
            {"name": "神秘血血统", "type": "概念", "aliases": ["神秘血统"]},
            {"name": "人类血统", "type": "概念", "aliases": []},
            {"name": "动物", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "神秘学家", "dst": "纯血种", "relation": "包含", "confidence": 0.9},
            {"src": "神秘学家", "dst": "混血种", "relation": "包含", "confidence": 0.9},
            {"src": "神秘血血统", "dst": "人类血统", "relation": "共存但不融洽",
             "confidence": 0.9},
            {"src": "纯血种", "dst": "神秘术", "relation": "能力最强", "confidence": 0.9},
            {"src": "混血种", "dst": "动物", "relation": "关系密切", "confidence": 0.7},
            {"src": "神秘学家", "dst": "感染种", "relation": "相关", "confidence": 0.7},
        ],
    },
    "f0e441cc76349144": {
        "entities": [
            {"name": "暴雨症候群", "type": "概念",
             "aliases": ["storm syndrome", "Storm Syndrome"]},
            {"name": "暴雨", "type": "事件", "aliases": ["Storm", "The Storm"]},
            {"name": "幻觉", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "暴雨症候群", "dst": "幻觉", "relation": "导致", "confidence": 0.8},
            {"src": "暴雨", "dst": "暴雨症候群", "relation": "引发", "confidence": 0.7},
        ],
    },
    "e32814318123093a": {
        "entities": [
            {"name": "帕拉维安", "type": "角色", "aliases": ["Paravian"]},
            {"name": "规程", "type": "概念", "aliases": ["protocol"]},
            {"name": "人力", "type": "概念", "aliases": ["manpower", "Manpower"]},
            {"name": "收容", "type": "事件", "aliases": []},
        ],
        "relations": [
            {"src": "帕拉维安", "dst": "规程", "relation": "遵从", "confidence": 0.9},
            {"src": "人力", "dst": "收容", "relation": "不足", "confidence": 0.8},
        ],
    },
    "013c91c3e0ab3a83": {
        "entities": [
            {"name": "伊戈尔", "type": "角色", "aliases": ["Igor"]},
            {"name": "克鲁托夫", "type": "角色", "aliases": ["Krutov"]},
            {"name": "骑兵", "type": "组织", "aliases": ["cavalry"]},
            {"name": "城市", "type": "地点", "aliases": ["city"]},
            {"name": "草原", "type": "地点", "aliases": ["step", "steppe"]},
        ],
        "relations": [
            {"src": "克鲁托夫", "dst": "伊戈尔", "relation": "有私怨", "confidence": 0.9},
            {"src": "骑兵", "dst": "城市", "relation": "保护", "confidence": 0.9},
            {"src": "草原", "dst": "伊戈尔", "relation": "交涉地", "confidence": 0.7},
        ],
    },
    "a1b6b205600929d4": {
        "entities": [
            {"name": "暴雨", "type": "事件", "aliases": ["Storm", "The Storm"]},
            {"name": "圣洛夫基金会", "type": "组织", "aliases": ["foundation", "Foundation"]},
            {"name": "身份置换", "type": "事件", "aliases": ["identities displaced"]},
            {"name": "43个灵魂", "type": "概念", "aliases": ["43 souls"]},
        ],
        "relations": [
            {"src": "暴雨", "dst": "身份置换", "relation": "导致", "confidence": 0.9},
            {"src": "43个灵魂", "dst": "身份置换", "relation": "关联", "confidence": 0.8},
        ],
    },
    "7496711494296a4f": {
        "entities": [
            {"name": "将军", "type": "角色", "aliases": ["general", "General"]},
            {"name": "神秘学家", "type": "概念", "aliases": ["arcanists", "Arcanists"]},
            {"name": "村庄", "type": "地点", "aliases": ["village"]},
            {"name": "淤泥", "type": "概念", "aliases": ["sludge"]},
            {"name": "冬青叶", "type": "物品", "aliases": ["holly leaves"]},
            {"name": "恶魔指菇", "type": "物品", "aliases": ["devil's finger mushrooms"]},
            {"name": "城市", "type": "地点", "aliases": ["city"]},
        ],
        "relations": [
            {"src": "将军", "dst": "神秘学家", "relation": "下令", "confidence": 0.9},
            {"src": "神秘学家", "dst": "淤泥", "relation": "被驱使清理", "confidence": 0.9},
            {"src": "村庄", "dst": "城市", "relation": "逃往", "confidence": 0.8},
        ],
    },
    "72ca01371429a9ea": {
        "entities": [
            {"name": "安德烈", "type": "角色", "aliases": ["Andre"]},
            {"name": "城市", "type": "地点", "aliases": ["city"]},
            {"name": "屋顶", "type": "地点", "aliases": ["rooftops"]},
        ],
        "relations": [
            {"src": "安德烈", "dst": "城市", "relation": "探索", "confidence": 0.8},
            {"src": "屋顶", "dst": "城市", "relation": "写生对象", "confidence": 0.8},
        ],
    },
    "b3f64833ba6012ab": {
        "entities": [
            {"name": "母神", "type": "角色", "aliases": ["Mother Spirit"]},
            {"name": "母神之光", "type": "概念", "aliases": ["mother spirit's light"]},
            {"name": "南极洲", "type": "地点", "aliases": ["Antarctica", "antarctica"]},
            {"name": "极地探险家", "type": "组织", "aliases": ["polar explorers"]},
            {"name": "丰收", "type": "概念", "aliases": ["harvest"]},
        ],
        "relations": [
            {"src": "母神之光", "dst": "极地探险家", "relation": "指引", "confidence": 0.8},
            {"src": "极地探险家", "dst": "南极洲", "relation": "深入", "confidence": 0.9},
            {"src": "母神", "dst": "丰收", "relation": "被歌颂", "confidence": 0.7},
        ],
    },
    "c4509455504a8c6b": {
        "entities": [
            {"name": "维尔汀", "type": "角色", "aliases": ["Vertin", "Verton"]},
            {"name": "索特里奥斯", "type": "角色", "aliases": ["Soterios"]},
            {"name": "节日油灯", "type": "物品", "aliases": ["festive oil lamp"]},
            {"name": "德拉克马", "type": "物品", "aliases": ["dracmi"]},
            {"name": "邪教徒", "type": "角色", "aliases": ["cultist"]},
        ],
        "relations": [
            {"src": "索特里奥斯", "dst": "节日油灯", "relation": "加价出售",
             "confidence": 0.9},
            {"src": "维尔汀", "dst": "索特里奥斯", "relation": "放行", "confidence": 0.8},
            {"src": "邪教徒", "dst": "索特里奥斯", "relation": "身份被否认",
             "confidence": 0.8},
        ],
    },
    "0444b2579cb0c781": {
        "entities": [
            {"name": "哑谜", "type": "角色", "aliases": ["Enigma", "enigma"]},
            {"name": "兔毛手袋", "type": "角色",
             "aliases": ["Medicine Pocket", "medicine pocket",
                         "researcher medicine pocket"]},
            {"name": "玩具盒", "type": "物品", "aliases": ["toy box"]},
            {"name": "审批制度", "type": "概念", "aliases": ["approval system"]},
            {"name": "报告", "type": "物品", "aliases": ["reports"]},
            {"name": "通信故障", "type": "事件", "aliases": ["communication problems"]},
        ],
        "relations": [
            {"src": "玩具盒", "dst": "通信故障", "relation": "导致", "confidence": 0.9},
            {"src": "哑谜", "dst": "报告", "relation": "审批", "confidence": 0.8},
            {"src": "兔毛手袋", "dst": "审批制度", "relation": "反对", "confidence": 0.9},
        ],
    },
    "8e95c8ef628de4c6": {
        "entities": [
            {"name": "沉默", "type": "概念", "aliases": ["silence", "Silence"]},
            {"name": "新大猩猩", "type": "概念", "aliases": ["new gorillas"]},
            {"name": "愤怒", "type": "概念", "aliases": ["anger"]},
            {"name": "失望", "type": "概念", "aliases": ["disappointment"]},
        ],
        "relations": [
            {"src": "沉默", "dst": "新大猩猩", "relation": "催生", "confidence": 0.8},
            {"src": "愤怒", "dst": "新大猩猩", "relation": "表达", "confidence": 0.7},
        ],
    },
    "40997fe98f4f3cc6": {
        "entities": [
            {"name": "冒险", "type": "概念", "aliases": ["adventure", "Adventure"]},
            {"name": "新时代", "type": "时间", "aliases": ["new era"]},
            {"name": "勇气", "type": "概念", "aliases": ["courage"]},
            {"name": "忠诚", "type": "概念", "aliases": ["loyalty"]},
            {"name": "传奇", "type": "概念", "aliases": ["legend"]},
        ],
        "relations": [
            {"src": "新时代", "dst": "冒险", "relation": "号召", "confidence": 0.8},
            {"src": "冒险", "dst": "勇气", "relation": "以…为纽带", "confidence": 0.8},
            {"src": "冒险", "dst": "传奇", "relation": "成就", "confidence": 0.7},
        ],
    },
    "9d4d309a26fa7fc0": {
        "entities": [
            {"name": "思维装置", "type": "物品", "aliases": ["thought device"]},
            {"name": "脑机接口", "type": "概念", "aliases": ["mind-machine interface"]},
            {"name": "展厅", "type": "地点", "aliases": ["gallery"]},
        ],
        "relations": [
            {"src": "思维装置", "dst": "脑机接口", "relation": "实现", "confidence": 0.9},
            {"src": "展厅", "dst": "脑机接口", "relation": "演示", "confidence": 0.9},
        ],
    },
    "21233d1132b7aa42": {
        "entities": [
            {"name": "滑翔机", "type": "物品",
             "aliases": ["fixed-wing unpowered sailplane", "sailplane"]},
            {"name": "咖啡", "type": "物品", "aliases": ["coffee"]},
            {"name": "酒", "type": "物品", "aliases": ["alcohol"]},
        ],
        "relations": [
            {"src": "咖啡", "dst": "酒", "relation": "同机酿制", "confidence": 0.7},
        ],
    },
    "04c9782cebd0ffd5": {
        "entities": [
            {"name": "神秘学家", "type": "概念",
             "aliases": ["canists", "arcanists", "Arcanists"]},
            {"name": "高塔", "type": "地点", "aliases": ["tower"]},
            {"name": "直觉", "type": "概念", "aliases": ["instincts"]},
            {"name": "观测", "type": "概念", "aliases": ["observation"]},
            {"name": "不可预测性", "type": "概念", "aliases": ["unpredictability"]},
        ],
        "relations": [
            {"src": "神秘学家", "dst": "不可预测性", "relation": "生活于",
             "confidence": 0.8},
            {"src": "直觉", "dst": "观测", "relation": "干扰", "confidence": 0.9},
            {"src": "观测", "dst": "高塔", "relation": "定位", "confidence": 0.8},
        ],
    },
    "59a17c6407d2c87b": {
        "entities": [
            {"name": "行李限额", "type": "概念", "aliases": ["20 kilograms"]},
            {"name": "军事装备", "type": "物品", "aliases": ["military equipment"]},
            {"name": "兵役合同", "type": "物品",
             "aliases": ["military service contracts"]},
            {"name": "文书", "type": "物品", "aliases": ["paperwork"]},
        ],
        "relations": [
            {"src": "行李限额", "dst": "军事装备", "relation": "例外", "confidence": 0.9},
            {"src": "兵役合同", "dst": "文书", "relation": "需签署", "confidence": 0.9},
        ],
    },
    "5f53c2931f757506": {
        "entities": [
            {"name": "恶魔", "type": "概念", "aliases": ["demons"]},
            {"name": "坦克", "type": "物品", "aliases": ["tank", "Tank"]},
            {"name": "火炮", "type": "物品", "aliases": ["cannon"]},
            {"name": "炸弹", "type": "物品", "aliases": ["bomb"]},
            {"name": "战争", "type": "事件", "aliases": ["war"]},
            {"name": "罪恶", "type": "概念", "aliases": ["sin"]},
        ],
        "relations": [
            {"src": "战争", "dst": "坦克", "relation": "使用", "confidence": 0.8},
            {"src": "战争", "dst": "火炮", "relation": "使用", "confidence": 0.8},
            {"src": "罪恶", "dst": "战争", "relation": "可终结", "confidence": 0.7},
        ],
    },
    "7f265d3ce2c1ec2a": {
        "entities": [
            {"name": "科学家", "type": "角色", "aliases": []},
            {"name": "队长", "type": "角色", "aliases": []},
            {"name": "医生", "type": "角色", "aliases": []},
            {"name": "维修小镇", "type": "地点", "aliases": []},
            {"name": "精神崩溃", "type": "事件", "aliases": ["疯掉", "情绪失败"]},
            {"name": "震惊剂", "type": "物品", "aliases": []},
            {"name": "炸肉包", "type": "物品", "aliases": []},
            {"name": "小朋友", "type": "概念", "aliases": []},
            {"name": "记者", "type": "角色", "aliases": ["journalist"]},
            {"name": "邀请名单", "type": "物品", "aliases": ["invitee list"]},
            {"name": "访问日志", "type": "物品", "aliases": ["visitor logs"]},
        ],
        "relations": [
            {"src": "科学家", "dst": "精神崩溃", "relation": "频发", "confidence": 0.9},
            {"src": "队长", "dst": "医生", "relation": "下令", "confidence": 0.8},
            {"src": "访问日志", "dst": "邀请名单", "relation": "比对", "confidence": 0.9},
            {"src": "记者", "dst": "邀请名单", "relation": "记录不符", "confidence": 0.9},
            {"src": "维修小镇", "dst": "震惊剂", "relation": "能否制造", "confidence": 0.7},
        ],
    },
    "b4da0defeebc64cb": {
        "entities": [
            {"name": "隔离检疫", "type": "事件", "aliases": ["quarantine"]},
            {"name": "车厢", "type": "地点", "aliases": ["carriage"]},
            {"name": "乘客", "type": "概念", "aliases": ["passengers"]},
            {"name": "囚犯", "type": "概念", "aliases": ["prisoners"]},
        ],
        "relations": [
            {"src": "隔离检疫", "dst": "车厢", "relation": "封锁", "confidence": 0.9},
            {"src": "乘客", "dst": "囚犯", "relation": "自比", "confidence": 0.8},
        ],
    },
    "0f9b0a2d115992a4": {
        "entities": [
            {"name": "圣洛夫基金会", "type": "组织", "aliases": ["foundation", "Foundation"]},
            {"name": "盖恩特利斯", "type": "角色", "aliases": ["gauntless", "Gauntless"]},
            {"name": "工地", "type": "地点", "aliases": ["site"]},
            {"name": "工人", "type": "组织", "aliases": ["workers"]},
        ],
        "relations": [
            {"src": "盖恩特利斯", "dst": "工地", "relation": "负责", "confidence": 0.8},
            {"src": "工人", "dst": "圣洛夫基金会", "relation": "不如其专业",
             "confidence": 0.8},
        ],
    },
    "a51fbe249323e574": {
        "entities": [
            {"name": "报春花", "type": "物品", "aliases": ["primroses"]},
            {"name": "斯特龙蒂亚", "type": "地点", "aliases": ["strontia"]},
            {"name": "雨", "type": "事件", "aliases": ["rain"]},
            {"name": "烟雾", "type": "概念", "aliases": ["smoke"]},
            {"name": "森林", "type": "地点", "aliases": ["forests"]},
        ],
        "relations": [
            {"src": "雨", "dst": "烟雾", "relation": "熄灭", "confidence": 0.8},
            {"src": "报春花", "dst": "森林", "relation": "盛开", "confidence": 0.9},
            {"src": "森林", "dst": "斯特龙蒂亚", "relation": "位于", "confidence": 0.8},
        ],
    },
}


def main() -> int:
    ap = argparse.ArgumentParser(description="补抽空块 第 4 批")
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
    print(f"[apply-p4] 写入 {written} 条，跳过 {skipped} 条")
    print(f"[apply-p4] NOOP 累计 {len(cur)} 条")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
