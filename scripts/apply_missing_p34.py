#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""补抽 backfill3 批次 midhigh_00/01 共 50 块（未抽取剧情块）。
手工抽取，写盘前 validate() 悬空自检 + landing() 落地自检。"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "knowledge" / "plot_cache" / "wu_ming_zhe"
CORPUS = ROOT / "data" / "knowledge" / "plot_corpus_wu_ming_zhe.json"

RESULTS = {
    # ===================== batch_midhigh_00 =====================
    "b94b842ea5e91141": {
        "entities": [
            {"name": "阿卡纳斯集会", "type": "事件", "aliases": ["Arcanus Gathering"]},
            {"name": "阿卡纳斯集会登记表", "type": "物品", "aliases": ["Arcanus Gathering Registration Form"]},
            {"name": "大型活动申请表", "type": "物品", "aliases": ["mass events application form"]},
            {"name": "沙漠地区集会申请表", "type": "物品", "aliases": ["desert areas gathering application form"]},
        ],
        "relations": [],
    },
    "c1b4aad0f3a1b2b7": {
        "entities": [
            {"name": "柳小姐", "type": "角色", "aliases": ["Miss Willow", "Fog Lady"]},
            {"name": "布里姆利先生", "type": "角色", "aliases": ["Mr.Brimley"]},
        ],
        "relations": [
            {"src": "布里姆利先生", "dst": "柳小姐", "relation": "护送", "confidence": 0.8},
        ],
    },
    "eb106fc1718c241d": {
        "entities": [
            {"name": "天鹅女士", "type": "角色", "aliases": ["Swan Lady"]},
            {"name": "十字街", "type": "地点", "aliases": ["Cross Street"]},
            {"name": "雾女士", "type": "角色", "aliases": ["Fog Lady"]},
            {"name": "黑雾", "type": "现象", "aliases": ["Black Fog"]},
            {"name": "柳小姐", "type": "角色", "aliases": ["Miss Willow"]},
        ],
        "relations": [
            {"src": "天鹅女士", "dst": "十字街", "relation": "非来自", "confidence": 0.7},
            {"src": "黑雾", "dst": "雾女士", "relation": "关联", "confidence": 0.7},
        ],
    },
    "5d9b5c87bfeb8fd1": {
        "entities": [
            {"name": "巫医", "type": "角色", "aliases": ["witch doctor"]},
            {"name": "牙仙小姐", "type": "角色", "aliases": ["Miss Tooth Fairy"]},
            {"name": "柳小姐", "type": "角色", "aliases": ["Miss Willow"]},
            {"name": "金色精灵", "type": "角色", "aliases": ["golden fairies"]},
            {"name": "御风术", "type": "概念", "aliases": ["wind"]},
        ],
        "relations": [
            {"src": "柳小姐", "dst": "御风术", "relation": "传授", "confidence": 0.75},
        ],
    },
    "791146c98f868787": {
        "entities": [
            {"name": "斯科特病房", "type": "地点", "aliases": ["Scott's Ward"]},
            {"name": "康斯坦斯斯科特病房", "type": "地点", "aliases": ["Constance Scott's Ward"]},
            {"name": "医生", "type": "角色", "aliases": ["Doctor"]},
        ],
        "relations": [
            {"src": "医生", "dst": "康斯坦斯斯科特病房", "relation": "指引", "confidence": 0.8},
        ],
    },
    "5c2434c2b6cf8ef6": {
        "entities": [
            {"name": "羊小姐", "type": "角色", "aliases": ["Miss Sheep"]},
            {"name": "小羊羔", "type": "角色", "aliases": ["little lamb"]},
            {"name": "母羊", "type": "角色", "aliases": ["mama"]},
        ],
        "relations": [
            {"src": "羊小姐", "dst": "小羊羔", "relation": "救助", "confidence": 0.7},
            {"src": "小羊羔", "dst": "母羊", "relation": "母子", "confidence": 0.8},
        ],
    },
    "8a1ce924c9b0d77e": {
        "entities": [],
        "relations": [],
    },
    "34aafef5e83d56e9": {
        "entities": [],
        "relations": [],
    },
    "6ebea87ee6ca0286": {
        "entities": [
            {"name": "弗雷迪", "type": "角色", "aliases": ["Freddy"]},
            {"name": "福格先生", "type": "角色", "aliases": ["Mr.Fogg"]},
            {"name": "父亲", "type": "角色", "aliases": ["Dad"]},
            {"name": "望远镜", "type": "物品", "aliases": ["telescope"]},
            {"name": "机器", "type": "物品", "aliases": ["machine"]},
        ],
        "relations": [
            {"src": "父亲", "dst": "望远镜", "relation": "携带", "confidence": 0.8},
        ],
    },
    "0b3ad5a48367bfcb": {
        "entities": [
            {"name": "乌卢鲁伦敦资格赛", "type": "事件", "aliases": ["Uluru London Qualifiers"]},
            {"name": "巴特利", "type": "角色", "aliases": ["Bartley"]},
            {"name": "巡逻队", "type": "组织", "aliases": ["patrol"]},
        ],
        "relations": [
            {"src": "巴特利", "dst": "乌卢鲁伦敦资格赛", "relation": "参赛", "confidence": 0.8},
        ],
    },
    "4b72ff6a5ba79e86": {
        "entities": [
            {"name": "埃皮龙", "type": "角色", "aliases": ["Epirron"]},
            {"name": "外部世界", "type": "概念", "aliases": ["outside world"]},
        ],
        "relations": [],
    },
    "2bedd05d1ce740eb": {
        "entities": [
            {"name": "创伤", "type": "概念", "aliases": ["Traumata"]},
            {"name": "警卫室", "type": "地点", "aliases": ["guardhouse"]},
            {"name": "唐纳德贾德", "type": "角色", "aliases": ["Donald Judd"]},
        ],
        "relations": [],
    },
    "7dee35c3c93f1ffc": {
        "entities": [
            {"name": "水箱", "type": "物品", "aliases": ["water tank"]},
            {"name": "警官先生", "type": "角色", "aliases": ["Mr.Officer"]},
            {"name": "警察", "type": "角色", "aliases": ["cops"]},
            {"name": "自由法典", "type": "概念", "aliases": ["Code of Freedom"]},
        ],
        "relations": [],
    },
    "95236fed6424f369": {
        "entities": [
            {"name": "梅拉妮亚拉米雷斯", "type": "角色", "aliases": ["Melania Ramirez"]},
            {"name": "艾弗森先生", "type": "角色", "aliases": ["Mr.Iverson"]},
            {"name": "机器人", "type": "物品", "aliases": ["robots"]},
            {"name": "窃贼", "type": "角色", "aliases": ["thief"]},
            {"name": "指引条例", "type": "概念", "aliases": ["guidance"]},
        ],
        "relations": [
            {"src": "机器人", "dst": "指引条例", "relation": "违反", "confidence": 0.8},
        ],
    },
    "8872a1b5430acf56": {
        "entities": [
            {"name": "楚郎子", "type": "角色", "aliases": ["Chulangzi"]},
            {"name": "莫伊", "type": "角色", "aliases": ["Moe"]},
            {"name": "马", "type": "物品", "aliases": ["horses"]},
            {"name": "院子", "type": "地点", "aliases": ["yard"]},
            {"name": "正厅", "type": "地点", "aliases": ["main hall"]},
            {"name": "种子", "type": "物品", "aliases": ["seeds"]},
            {"name": "茶水", "type": "物品", "aliases": ["tea"]},
        ],
        "relations": [
            {"src": "楚郎子", "dst": "莫伊", "relation": "寻找", "confidence": 0.7},
        ],
    },
    "80a24618e2ea2c9d": {
        "entities": [
            {"name": "外国商人", "type": "角色", "aliases": ["foreign merchants"]},
            {"name": "积水", "type": "物品", "aliases": ["water"]},
            {"name": "茶水", "type": "物品", "aliases": ["tea"]},
        ],
        "relations": [],
    },
    "6d2635300387250f": {
        "entities": [
            {"name": "伏特加杯垫", "type": "物品", "aliases": ["Vodka coaster"]},
            {"name": "字条", "type": "物品", "aliases": ["note", "notes"]},
            {"name": "战利品", "type": "物品", "aliases": ["trophies"]},
        ],
        "relations": [],
    },
    "6096b3c92b3fc64d": {
        "entities": [
            {"name": "东区", "type": "地点", "aliases": ["East End"]},
            {"name": "开膛手杰克", "type": "角色", "aliases": ["Jack the Ripper"]},
            {"name": "埃文", "type": "角色", "aliases": ["Evan"]},
            {"name": "黑烟灰", "type": "物品", "aliases": ["dark soot"]},
        ],
        "relations": [
            {"src": "东区", "dst": "开膛手杰克", "relation": "滋生", "confidence": 0.7},
        ],
    },
    "8a91320dfba9b15a": {
        "entities": [
            {"name": "亚瑟", "type": "角色", "aliases": ["Arthur"]},
            {"name": "伦敦紧急救济中心", "type": "组织", "aliases": ["London Emergency Relief Centre"]},
            {"name": "小页小姐", "type": "角色", "aliases": ["Miss Flutterpage"]},
            {"name": "牙仙小姐", "type": "角色", "aliases": ["Miss Tooth Fairy"]},
            {"name": "肺结核病人", "type": "角色", "aliases": ["tuberculosis patients"]},
        ],
        "relations": [
            {"src": "小页小姐", "dst": "牙仙小姐", "relation": "寻找", "confidence": 0.85},
            {"src": "伦敦紧急救济中心", "dst": "肺结核病人", "relation": "救治", "confidence": 0.8},
        ],
    },
    "d9cb0c210fe4d331": {
        "entities": [
            {"name": "布朗太太", "type": "角色", "aliases": ["Mrs.Brown"]},
            {"name": "琼斯太太", "type": "角色", "aliases": ["Mrs.Jones"]},
            {"name": "本之子", "type": "角色", "aliases": ["Ben's son"]},
            {"name": "叫醒人", "type": "角色", "aliases": ["knocker upper"]},
            {"name": "魔法床单", "type": "物品", "aliases": ["enchanted sheet"]},
            {"name": "福格先生", "type": "角色", "aliases": ["Mr.Fogg"]},
            {"name": "展览会", "type": "事件", "aliases": ["exhibition"]},
        ],
        "relations": [
            {"src": "福格先生", "dst": "展览会", "relation": "举办", "confidence": 0.8},
            {"src": "叫醒人", "dst": "魔法床单", "relation": "给予", "confidence": 0.7},
        ],
    },
    "591be142e5acb66f": {
        "entities": [
            {"name": "国际天文学联合会", "type": "组织", "aliases": ["IAU", "International Astronomical Union"]},
            {"name": "泰晤士报", "type": "组织", "aliases": ["The Times"]},
            {"name": "地球", "type": "地点", "aliases": ["Earth"]},
            {"name": "太阳", "type": "概念", "aliases": ["Sun", "sun"]},
            {"name": "水星", "type": "概念", "aliases": ["Mercury"]},
            {"name": "金星", "type": "概念", "aliases": ["Venus"]},
            {"name": "天文单位", "type": "概念", "aliases": ["astronomical unit"]},
            {"name": "岛屿", "type": "地点", "aliases": ["island"]},
        ],
        "relations": [
            {"src": "国际天文学联合会", "dst": "泰晤士报", "relation": "报告刊于", "confidence": 0.7},
        ],
    },
    "c336363db6fecfb3": {
        "entities": [
            {"name": "紧急支援队", "type": "组织", "aliases": ["emergency support team"]},
            {"name": "玛蒂尔达鲍文尼奇", "type": "角色", "aliases": ["Matilda Bowenich"]},
            {"name": "海特街", "type": "地点", "aliases": ["Haight Street"]},
        ],
        "relations": [
            {"src": "玛蒂尔达鲍文尼奇", "dst": "紧急支援队", "relation": "隶属", "confidence": 0.7},
            {"src": "紧急支援队", "dst": "海特街", "relation": "未驻守", "confidence": 0.7},
        ],
    },
    "39bbf1ae9c66bd4a": {
        "entities": [
            {"name": "海特街", "type": "地点", "aliases": ["Haight Street"]},
            {"name": "杰伊", "type": "角色", "aliases": ["Jay"]},
            {"name": "新世纪市场", "type": "组织", "aliases": ["New Age market"]},
        ],
        "relations": [
            {"src": "杰伊", "dst": "海特街", "relation": "居于", "confidence": 0.7},
            {"src": "新世纪市场", "dst": "海特街", "relation": "位于", "confidence": 0.7},
        ],
    },
    "0bf83e6131c182bb": {
        "entities": [
            {"name": "绿湖", "type": "地点", "aliases": []},
            {"name": "交响乐团", "type": "组织", "aliases": []},
            {"name": "笔记本", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "笔记本", "dst": "绿湖", "relation": "记录", "confidence": 0.7},
        ],
    },
    "82daa66e7f89d75d": {
        "entities": [
            {"name": "雷古勒斯", "type": "角色", "aliases": ["Regulus"]},
            {"name": "格雷斯小姐", "type": "角色", "aliases": ["Miss Grace"]},
            {"name": "追乐人", "type": "角色", "aliases": ["music chaser"]},
            {"name": "外来者", "type": "角色", "aliases": ["outsiders"]},
        ],
        "relations": [
            {"src": "雷古勒斯", "dst": "追乐人", "relation": "自认", "confidence": 0.8},
            {"src": "格雷斯小姐", "dst": "外来者", "relation": "描述", "confidence": 0.7},
        ],
    },
    # ===================== batch_midhigh_01 =====================
    "02775a0412a3210d": {
        "entities": [
            {"name": "神秘术士", "type": "角色", "aliases": ["Arcanists"]},
            {"name": "源质", "type": "概念", "aliases": ["Arcanum"]},
            {"name": "源质生物", "type": "角色", "aliases": ["Arcanum creatures"]},
            {"name": "讲台", "type": "物品", "aliases": ["podium"]},
            {"name": "人类世界", "type": "概念", "aliases": ["human world"]},
        ],
        "relations": [
            {"src": "源质生物", "dst": "源质", "relation": "源自", "confidence": 0.7},
        ],
    },
    "5d38a1cf7e77e2c7": {
        "entities": [
            {"name": "温迪", "type": "角色", "aliases": ["Wendy"]},
            {"name": "里米克杯", "type": "事件", "aliases": ["Rimmick Cup"]},
            {"name": "妈妈", "type": "角色", "aliases": ["Mom"]},
            {"name": "足球", "type": "物品", "aliases": ["football"]},
            {"name": "球类游戏", "type": "事件", "aliases": ["ball game"]},
            {"name": "安全检查", "type": "事件", "aliases": ["security screening"]},
            {"name": "新时代战士", "type": "角色", "aliases": ["warrior of the new era"]},
        ],
        "relations": [
            {"src": "温迪", "dst": "里米克杯", "relation": "提议参观", "confidence": 0.7},
        ],
    },
    "4d8126d25ab40a8a": {
        "entities": [
            {"name": "幻梦", "type": "概念", "aliases": ["reverie"]},
            {"name": "恐怖袭击", "type": "事件", "aliases": ["terrorist attack"]},
            {"name": "艾弗森", "type": "角色", "aliases": ["Iverson"]},
            {"name": "恶魔", "type": "角色", "aliases": ["demon"]},
            {"name": "伏击", "type": "事件", "aliases": ["ambush"]},
        ],
        "relations": [
            {"src": "艾弗森", "dst": "恶魔", "relation": "召唤", "confidence": 0.8},
        ],
    },
    "98251ef847b7fb60": {
        "entities": [
            {"name": "传单", "type": "物品", "aliases": ["leaflet"]},
            {"name": "温迪", "type": "角色", "aliases": ["Wendy"]},
            {"name": "爱丽丝", "type": "角色", "aliases": ["Alice"]},
            {"name": "尼尔森", "type": "角色", "aliases": ["Nelson"]},
            {"name": "小泡菜", "type": "角色", "aliases": ["Little Pickles"]},
            {"name": "警犬", "type": "角色", "aliases": ["police dog"]},
            {"name": "幼犬乐园", "type": "地点", "aliases": ["puppy land"]},
        ],
        "relations": [
            {"src": "温迪", "dst": "爱丽丝", "relation": "同行", "confidence": 0.7},
            {"src": "警犬", "dst": "幼犬乐园", "relation": "守护", "confidence": 0.7},
        ],
    },
    "9d87951f63f3c022": {
        "entities": [
            {"name": "獾", "type": "角色", "aliases": ["badger"]},
            {"name": "警察局", "type": "组织", "aliases": ["police station"]},
            {"name": "老爹", "type": "角色", "aliases": ["daddy"]},
            {"name": "小偷", "type": "角色", "aliases": ["thief"]},
        ],
        "relations": [],
    },
    "efaf8cc47efc4b71": {
        "entities": [
            {"name": "神秘术怪物", "type": "角色", "aliases": ["arcane monsters"]},
            {"name": "汽车", "type": "物品", "aliases": ["car"]},
            {"name": "油门", "type": "物品", "aliases": ["gas pedal"]},
        ],
        "relations": [],
    },
    "f1cbb99b811a5c93": {
        "entities": [
            {"name": "老鸵鸟", "type": "角色", "aliases": ["old ostrich", "Pop ostrich"]},
            {"name": "黄金之城", "type": "物品", "aliases": ["The Golden City"]},
            {"name": "龙舌兰酒", "type": "物品", "aliases": ["Tequila"]},
            {"name": "女服务员", "type": "角色", "aliases": ["waitress"]},
            {"name": "地下拳赛", "type": "事件", "aliases": ["underground boxing match"]},
        ],
        "relations": [
            {"src": "老鸵鸟", "dst": "黄金之城", "relation": "播放", "confidence": 0.8},
        ],
    },
    "4df8e2bc119cad91": {
        "entities": [
            {"name": "罗斯", "type": "角色", "aliases": ["Roth"]},
            {"name": "库科", "type": "角色", "aliases": ["Kuko"]},
            {"name": "老奶奶", "type": "角色", "aliases": ["grandma"]},
            {"name": "长耳大野兔", "type": "角色", "aliases": ["jackrabbit"]},
        ],
        "relations": [
            {"src": "库科", "dst": "罗斯", "relation": "帮助", "confidence": 0.7},
        ],
    },
    "9740f730afc1d5d8": {
        "entities": [
            {"name": "母亲", "type": "角色", "aliases": ["mama"]},
            {"name": "子弹", "type": "物品", "aliases": ["bullets"]},
            {"name": "客人", "type": "角色", "aliases": ["guest"]},
            {"name": "房门", "type": "物品", "aliases": ["door"]},
        ],
        "relations": [],
    },
    "71f55f685747c6df": {
        "entities": [
            {"name": "诅咒", "type": "概念", "aliases": ["curse"]},
            {"name": "游侠", "type": "角色", "aliases": ["Ranger"]},
            {"name": "女巫", "type": "角色", "aliases": ["Hag"]},
            {"name": "黑雾", "type": "现象", "aliases": ["Black Fog"]},
            {"name": "巨鸸鹋战争", "type": "事件", "aliases": ["Great Emu War"]},
            {"name": "小生物", "type": "角色", "aliases": ["critters"]},
        ],
        "relations": [
            {"src": "黑雾", "dst": "小生物", "relation": "驱散", "confidence": 0.7},
            {"src": "游侠", "dst": "诅咒", "relation": "调查", "confidence": 0.7},
        ],
    },
    "aae82925aa7a8a88": {
        "entities": [
            {"name": "上帝", "type": "角色", "aliases": ["God"]},
            {"name": "小页", "type": "角色", "aliases": ["Flutter Page"]},
            {"name": "牙仙先生", "type": "角色", "aliases": ["Mr Tooth Fairy"]},
            {"name": "福格先生", "type": "角色", "aliases": ["Mr Fog"]},
            {"name": "布里姆利先生", "type": "角色", "aliases": ["Mr Brimley"]},
            {"name": "陷阱", "type": "物品", "aliases": ["trap"]},
        ],
        "relations": [
            {"src": "牙仙先生", "dst": "福格先生", "relation": "同行", "confidence": 0.7},
            {"src": "牙仙先生", "dst": "布里姆利先生", "relation": "同行", "confidence": 0.7},
        ],
    },
    "ebf69239509584ca": {
        "entities": [
            {"name": "展览会", "type": "事件", "aliases": ["exhibition"]},
            {"name": "救济中心", "type": "组织", "aliases": ["Relief Center"]},
            {"name": "伦敦空气污染自动净化器三号", "type": "物品", "aliases": ["London Air Pollution Autodetecting Purifier, Mark 3"]},
            {"name": "运动员", "type": "角色", "aliases": ["athletes"]},
            {"name": "应急计划", "type": "概念", "aliases": ["contingency plan"]},
        ],
        "relations": [
            {"src": "救济中心", "dst": "应急计划", "relation": "批准", "confidence": 0.85},
            {"src": "救济中心", "dst": "运动员", "relation": "保护", "confidence": 0.7},
        ],
    },
    "e4026a3cd8f4f685": {
        "entities": [
            {"name": "无知之网", "type": "概念", "aliases": ["web of ignorance"]},
            {"name": "邪恶", "type": "概念", "aliases": ["evil"]},
            {"name": "腐败之链", "type": "概念", "aliases": ["Corruption's chain"]},
            {"name": "黑暗甲壳", "type": "概念", "aliases": ["carapace of darkness"]},
            {"name": "墓冢", "type": "物品", "aliases": ["tomb"]},
            {"name": "真理", "type": "概念", "aliases": ["truth"]},
        ],
        "relations": [],
    },
    "e049bbfa893a162e": {
        "entities": [
            {"name": "骑士穿刺者案", "type": "事件", "aliases": ["Knight-Piercer case"]},
            {"name": "埃尔登", "type": "角色", "aliases": ["Eldon"]},
            {"name": "神秘术事务司", "type": "组织", "aliases": ["Division of Arcane Affairs"]},
            {"name": "池青", "type": "角色", "aliases": ["Chi-Shing"]},
            {"name": "记者会", "type": "事件", "aliases": ["press conference"]},
            {"name": "新兵", "type": "角色", "aliases": ["rookie"]},
            {"name": "城市", "type": "地点", "aliases": ["city"]},
        ],
        "relations": [
            {"src": "埃尔登", "dst": "神秘术事务司", "relation": "隶属", "confidence": 0.85},
            {"src": "埃尔登", "dst": "骑士穿刺者案", "relation": "回应", "confidence": 0.8},
            {"src": "池青", "dst": "城市", "relation": "占据", "confidence": 0.7},
        ],
    },
    "966f36f111ef90ce": {
        "entities": [
            {"name": "电话", "type": "物品", "aliases": ["phone call"]},
            {"name": "医院", "type": "组织", "aliases": ["hospital"]},
            {"name": "骗子", "type": "角色", "aliases": ["con man"]},
        ],
        "relations": [],
    },
    "4eb9268b9cb8d9ad": {
        "entities": [
            {"name": "燕子", "type": "角色", "aliases": ["Swallow"]},
            {"name": "马铁匠", "type": "角色", "aliases": ["Horsesmith"]},
            {"name": "流水", "type": "概念", "aliases": ["flowing water"]},
            {"name": "九子", "type": "组织", "aliases": ["Jiu-Zi"]},
        ],
        "relations": [
            {"src": "流水", "dst": "九子", "relation": "使其归属", "confidence": 0.7},
        ],
    },
    "aea6317dd4d8c1a3": {
        "entities": [
            {"name": "九子", "type": "组织", "aliases": ["Jiu-Zi"]},
            {"name": "流水", "type": "概念", "aliases": ["flowing water"]},
            {"name": "河流", "type": "地点", "aliases": ["river"]},
            {"name": "条纹马", "type": "角色", "aliases": ["striped horses"]},
            {"name": "祉锡", "type": "角色", "aliases": ["Zhixi"]},
            {"name": "四书五经", "type": "概念", "aliases": ["four books and five classics"]},
            {"name": "风水堪舆", "type": "概念", "aliases": ["Geomancy and Feng Shui"]},
        ],
        "relations": [
            {"src": "九子", "dst": "流水", "relation": "关切", "confidence": 0.7},
            {"src": "祉锡", "dst": "条纹马", "relation": "关注", "confidence": 0.7},
        ],
    },
    "4b0d8d3cdd3be96f": {
        "entities": [
            {"name": "布伦特", "type": "角色", "aliases": ["Brent"]},
            {"name": "布莱恩", "type": "角色", "aliases": ["Brian"]},
            {"name": "清洁剂", "type": "物品", "aliases": ["cleaner"]},
            {"name": "顾客", "type": "角色", "aliases": ["customer"]},
        ],
        "relations": [
            {"src": "布伦特", "dst": "布莱恩", "relation": "抛给", "confidence": 0.7},
        ],
    },
    "9615890f9c4b8bb7": {
        "entities": [
            {"name": "马蒂扎布瓦尼什", "type": "角色", "aliases": ["Matizah Bwanish"]},
            {"name": "圣帕夫洛夫基金会", "type": "组织", "aliases": ["Saint Pavlov Foundation"]},
            {"name": "保利娜", "type": "角色", "aliases": ["Paulina"]},
            {"name": "保密协议", "type": "物品", "aliases": ["confidentiality agreement"]},
            {"name": "基金会办公室", "type": "地点", "aliases": ["Foundation office"]},
        ],
        "relations": [
            {"src": "马蒂扎布瓦尼什", "dst": "圣帕夫洛夫基金会", "relation": "隶属", "confidence": 0.85},
            {"src": "保利娜", "dst": "基金会办公室", "relation": "藏身", "confidence": 0.7},
        ],
    },
    "76234ca7851019b5": {
        "entities": [
            {"name": "鲁萨尔卡", "type": "角色", "aliases": []},
            {"name": "维拉", "type": "角色", "aliases": []},
            {"name": "食堂", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "鲁萨尔卡", "dst": "食堂", "relation": "身处", "confidence": 0.7},
        ],
    },
    "19d0ac766b42d111": {
        "entities": [
            {"name": "乌卢鲁运动会", "type": "事件", "aliases": ["Uluru games"]},
            {"name": "妈咪", "type": "角色", "aliases": ["Mummy"]},
            {"name": "爷爷", "type": "角色", "aliases": ["grandpa"]},
            {"name": "玛莎阿姨", "type": "角色", "aliases": ["Auntie Martha"]},
            {"name": "雾净化机", "type": "物品", "aliases": ["fog purification machine"]},
            {"name": "蓝天", "type": "概念", "aliases": ["blue sky"]},
            {"name": "地球", "type": "地点", "aliases": ["Earth"]},
        ],
        "relations": [
            {"src": "玛莎阿姨", "dst": "雾净化机", "relation": "参与建造", "confidence": 0.7},
            {"src": "妈咪", "dst": "乌卢鲁运动会", "relation": "担忧", "confidence": 0.7},
        ],
    },
    "f0d5b8074b9dc999": {
        "entities": [
            {"name": "哈西小姐", "type": "角色", "aliases": ["Miss Hasee"]},
            {"name": "雷米克杯", "type": "事件", "aliases": ["Remick Cup"]},
            {"name": "父亲", "type": "角色", "aliases": ["Father"]},
            {"name": "公司", "type": "组织", "aliases": ["company"]},
            {"name": "墓地", "type": "地点", "aliases": ["cemetery"]},
        ],
        "relations": [
            {"src": "哈西小姐", "dst": "雷米克杯", "relation": "提及", "confidence": 0.7},
        ],
    },
    "f207dd97f2b6dcc4": {
        "entities": [
            {"name": "幻梦", "type": "概念", "aliases": ["reverie"]},
            {"name": "天堂", "type": "概念", "aliases": ["heaven"]},
            {"name": "缪斯", "type": "角色", "aliases": ["muse"]},
            {"name": "人类安保员", "type": "角色", "aliases": ["human security staff"]},
            {"name": "父亲", "type": "角色", "aliases": ["father"]},
            {"name": "地面格斗", "type": "概念", "aliases": ["ground-grappling"]},
            {"name": "污浊空气", "type": "概念", "aliases": ["dirty air"]},
        ],
        "relations": [
            {"src": "父亲", "dst": "地面格斗", "relation": "传授", "confidence": 0.8},
        ],
    },
    "2fa6dfd351ba7752": {
        "entities": [
            {"name": "肥皂泡", "type": "物品", "aliases": ["soap bubbles"]},
            {"name": "艾弗森先生", "type": "角色", "aliases": ["Mr.Iverson"]},
            {"name": "托尼", "type": "角色", "aliases": ["Tony"]},
            {"name": "易逝之美", "type": "概念", "aliases": ["transient beauties"]},
        ],
        "relations": [
            {"src": "艾弗森先生", "dst": "肥皂泡", "relation": "注视", "confidence": 0.7},
        ],
    },
    "de8d299eb3425426": {
        "entities": [
            {"name": "穿梭巴士", "type": "物品", "aliases": ["shuttle bus"]},
            {"name": "维斯帕", "type": "角色", "aliases": ["Vespa"]},
            {"name": "按钮", "type": "物品", "aliases": ["button"]},
            {"name": "人类之物", "type": "物品", "aliases": ["human thing"]},
        ],
        "relations": [
            {"src": "维斯帕", "dst": "按钮", "relation": "按住", "confidence": 0.7},
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
    print(f"[apply-missing-p34] 写入 {len(RESULTS)} 条")
    return 0


if __name__ == "__main__":
    sys.exit(main())
