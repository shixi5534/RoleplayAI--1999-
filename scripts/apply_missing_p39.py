#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""补抽 2 个批次（backfill3/batch_mid_00,01）共 50 个漏网块。
手工抽取，写盘前 validate() 悬空自检 + landing() 落地自检。"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "knowledge" / "plot_cache" / "wu_ming_zhe"
CORPUS = ROOT / "data" / "knowledge" / "plot_corpus_wu_ming_zhe.json"

# 判无剧情信息的块 -> 空
NOOP = {
    "f4a7e94ebd5b2d88": {},   # 控诉演说，无专名
    "bc2475cd69394efd": {},   # 抽象叙事，无专名
    "4d69c8c237750cfe": {},   # 内心独白，无专名
    "42c70cdc60f18c27": {},   # 抽象叙事，无专名
    "5309d527b97e6a5c": {},   # 内心独白，无专名
}

RESULTS = {
    # ===== batch_mid_00 =====
    "2acab0ee277f0cba": {
        "entities": [
            {"name": "上帝", "type": "角色", "aliases": ["our God"]},
        ],
        "relations": [],
    },
    "ac73d176de6662ee": {
        "entities": [
            {"name": "Atootoo", "type": "角色", "aliases": []},
        ],
        "relations": [],
    },
    "3f570fd20f606384": {
        "entities": [
            {"name": "风暴研究组", "type": "组织", "aliases": ["Storm Research Group"]},
        ],
        "relations": [],
    },
    "1cb002bc5bf62135": {
        "entities": [
            {"name": "司辰", "type": "角色", "aliases": ["timekeeper", "Timekeeper"]},
            {"name": "十四行诗", "type": "角色", "aliases": ["sonnetto"]},
            {"name": "弹跳灯泡", "type": "物品", "aliases": ["the bouncing bulb", "bouncing bulb"]},
            {"name": "雷古卢斯", "type": "角色", "aliases": ["Regulus", "Researcher Regulus"]},
            {"name": "塞涅罗", "type": "角色", "aliases": ["Senero", "Miss Senero"]},
        ],
        "relations": [],
    },
    "f4a7e94ebd5b2d88": NOOP["f4a7e94ebd5b2d88"],
    "7108bd3b78e9f89c": {
        "entities": [
            {"name": "塔普萨尔虫", "type": "角色", "aliases": ["the Tapsal worm", "Tapsal worm"]},
            {"name": "橡树游行蛾", "type": "角色", "aliases": ["Oak processionary moths"]},
        ],
        "relations": [],
    },
    "0fc81ff7477915e3": {
        "entities": [
            {"name": "浓雾", "type": "现象", "aliases": ["Fog"]},
        ],
        "relations": [],
    },
    "bc2475cd69394efd": NOOP["bc2475cd69394efd"],
    "23717b6e45e2f40d": {
        "entities": [
            {"name": "乌托邦", "type": "概念", "aliases": ["Utopia"]},
            {"name": "智能洗涤枪", "type": "物品", "aliases": ["the smart detergent gun", "smart detergent gun"]},
        ],
        "relations": [],
    },
    "28e671673af55612": {
        "entities": [
            {"name": "安保公司", "type": "组织", "aliases": ["security company", "the new security company"]},
            {"name": "安保指南", "type": "概念", "aliases": ["guidance on security", "the guidance on security"]},
        ],
        "relations": [
            {"src": "安保公司", "dst": "安保指南", "relation": "遵循", "confidence": 0.85},
        ],
    },
    "9014f843babc5fd7": {
        "entities": [
            {"name": "鉴定机构", "type": "组织", "aliases": ["verification agency", "the verification agency"]},
            {"name": "带沿杯", "type": "物品", "aliases": ["the rimmed cup", "rimmed cup"]},
            {"name": "拉米雷斯", "type": "角色", "aliases": ["Ramirez"]},
            {"name": "希尔协会", "type": "组织", "aliases": ["Hill Society", "the Hill Society"]},
            {"name": "安保指南", "type": "概念", "aliases": ["guidance on security"]},
            {"name": "安保理论", "type": "概念", "aliases": ["security theory"]},
        ],
        "relations": [
            {"src": "拉米雷斯", "dst": "希尔协会", "relation": "危害", "confidence": 0.9},
            {"src": "拉米雷斯", "dst": "安保理论", "relation": "主张", "confidence": 0.85},
            {"src": "鉴定机构", "dst": "带沿杯", "relation": "鉴定为赝品", "confidence": 0.85},
            {"src": "希尔协会", "dst": "安保指南", "relation": "采用", "confidence": 0.8},
            {"src": "希尔协会", "dst": "安保理论", "relation": "摒弃", "confidence": 0.8},
        ],
    },
    "dc1fbc385c9254b7": {
        "entities": [
            {"name": "安保理论", "type": "概念", "aliases": ["security theories"]},
            {"name": "人类安保机器人", "type": "角色", "aliases": ["human security robots", "new human security robots"]},
            {"name": "里梅特杯", "type": "物品", "aliases": ["Rimmet Cup", "the Rimmet Cup"]},
        ],
        "relations": [],
    },
    "461f01e5de06eaaa": {
        "entities": [
            {"name": "乌托邦", "type": "概念", "aliases": ["utopia", "the never will happen utopia"]},
            {"name": "展览特别活动", "type": "事件", "aliases": ["special event of the exhibition", "the special event of the exhibition"]},
            {"name": "肥皂泡", "type": "现象", "aliases": ["soap bubbles", "these soap bubbles"]},
            {"name": "通风系统", "type": "物品", "aliases": ["ventilation system", "the ventilation system"]},
            {"name": "肥皂泡装置", "type": "物品", "aliases": ["soap bubble device", "the soap bubble device"]},
        ],
        "relations": [
            {"src": "肥皂泡装置", "dst": "通风系统", "relation": "启动", "confidence": 0.8},
        ],
    },
    "01d63f81c9cc6c96": {
        "entities": [
            {"name": "乌托邦", "type": "概念", "aliases": ["utopia", "Your utopia"]},
            {"name": "临时聚会", "type": "事件", "aliases": ["impromptu party"]},
            {"name": "演出", "type": "事件", "aliases": ["show", "the show"]},
            {"name": "收音机", "type": "物品", "aliases": ["radio"]},
        ],
        "relations": [],
    },
    "3023a942811bad63": {
        "entities": [
            {"name": "阿卡尼斯塔", "type": "角色", "aliases": ["Arcanista"]},
            {"name": "杰森", "type": "角色", "aliases": ["Jason"]},
            {"name": "迈克尔", "type": "角色", "aliases": ["Michael"]},
        ],
        "relations": [],
    },
    "7d3469fc94d0d5a7": {
        "entities": [
            {"name": "超大质量黑洞", "type": "现象", "aliases": ["supermassive black hole"]},
            {"name": "邻近星系", "type": "地点", "aliases": ["nearby galaxies", "the nearby galaxies"]},
            {"name": "引力", "type": "现象", "aliases": ["gravity"]},
            {"name": "类星体", "type": "现象", "aliases": ["quasars"]},
            {"name": "第三页", "type": "物品", "aliases": ["Page three"]},
        ],
        "relations": [
            {"src": "超大质量黑洞", "dst": "邻近星系", "relation": "吸引", "confidence": 0.85},
        ],
    },
    "2eb0dac447ea3d07": {
        "entities": [
            {"name": "奇迹珠宝与钱包", "type": "物品", "aliases": ["Miracle jewelry and wallet"]},
            {"name": "火车站免费地图", "type": "物品", "aliases": ["the map that they give at the railway station for free", "map of the treasure"]},
            {"name": "火车站", "type": "地点", "aliases": ["railway station", "the railway station"]},
            {"name": "卡片", "type": "物品", "aliases": ["the card", "card"]},
            {"name": "宝藏", "type": "物品", "aliases": ["treasure"]},
        ],
        "relations": [
            {"src": "火车站", "dst": "火车站免费地图", "relation": "发放", "confidence": 0.8},
            {"src": "火车站免费地图", "dst": "宝藏", "relation": "标示", "confidence": 0.7},
        ],
    },
    "7106d4ac52e1e268": {
        "entities": [
            {"name": "毛塔", "type": "角色", "aliases": ["Mauta"]},
            {"name": "芬特雷", "type": "组织", "aliases": ["Fintre"]},
            {"name": "宝藏", "type": "物品", "aliases": ["treasure"]},
            {"name": "芝麻开门", "type": "概念", "aliases": ["open sesame"]},
        ],
        "relations": [],
    },
    "295fcb238d4eb32f": {
        "entities": [
            {"name": "萨满", "type": "角色", "aliases": ["shaman", "a shaman"]},
            {"name": "白象", "type": "角色", "aliases": ["White elephant"]},
        ],
        "relations": [],
    },
    "6e7808e91bead09d": {
        "entities": [
            {"name": "修正者", "type": "角色", "aliases": ["corrector", "every corrector"]},
            {"name": "数字王国", "type": "地点", "aliases": ["simple kingdom featuring numbers only", "this simple kingdom"]},
            {"name": "几何", "type": "角色", "aliases": ["Geometry"]},
        ],
        "relations": [
            {"src": "几何", "dst": "数字王国", "relation": "位于", "confidence": 0.8},
        ],
    },
    "d4404f4f09e351d1": {
        "entities": [
            {"name": "钥匙", "type": "物品", "aliases": ["the key", "key"]},
            {"name": "坐垫", "type": "物品", "aliases": ["the cushion", "cushion"]},
            {"name": "文件", "type": "物品", "aliases": ["the files", "files"]},
            {"name": "石凳", "type": "物品", "aliases": ["the stone bench", "stone bench"]},
            {"name": "监视者", "type": "角色", "aliases": ["this monitor", "monitor"]},
        ],
        "relations": [
            {"src": "监视者", "dst": "文件", "relation": "考核", "confidence": 0.7},
        ],
    },
    "5cf7913267571f73": {
        "entities": [
            {"name": "纵队", "type": "组织", "aliases": ["the column", "column"]},
            {"name": "火袋鼠", "type": "角色", "aliases": ["fire kangaroos"]},
            {"name": "住房压力", "type": "概念", "aliases": ["housing stress"]},
            {"name": "金属UFO", "type": "物品", "aliases": ["metal UFO", "a metal UFO"]},
            {"name": "木马", "type": "物品", "aliases": ["wooden horse", "a wooden horse"]},
        ],
        "relations": [
            {"src": "火袋鼠", "dst": "纵队", "relation": "重创", "confidence": 0.7},
        ],
    },
    "4d69c8c237750cfe": NOOP["4d69c8c237750cfe"],
    "42c70cdc60f18c27": NOOP["42c70cdc60f18c27"],
    "6bf9ac507a9ed51b": {
        "entities": [
            {"name": "水火卦", "type": "概念", "aliases": ["hexagram of water and fire", "the hexagram of water and fire"]},
            {"name": "需卦", "type": "概念", "aliases": ["Xu", "hexagram of waiting", "Xu, the hexagram of waiting"]},
        ],
        "relations": [],
    },
    # ===== batch_mid_01 =====
    "5b91fad03f50fcc1": {
        "entities": [
            {"name": "医生", "type": "角色", "aliases": ["doctor", "the doctor"]},
        ],
        "relations": [],
    },
    "998a7cb17a678286": {
        "entities": [
            {"name": "戴帽的布谷鸟", "type": "角色", "aliases": ["the hatted cuckoo", "hatted cuckoo"]},
            {"name": "玛努斯", "type": "组织", "aliases": ["the Manus", "Manus"]},
            {"name": "拉普拉斯", "type": "地点", "aliases": ["Laplace"]},
            {"name": "总部", "type": "地点", "aliases": ["the headquarters", "headquarters"]},
        ],
        "relations": [
            {"src": "玛努斯", "dst": "总部", "relation": "攻击", "confidence": 0.8},
            {"src": "总部", "dst": "拉普拉斯", "relation": "位于", "confidence": 0.7},
        ],
    },
    "299ca04ffe9f0c56": {
        "entities": [
            {"name": "城镇", "type": "地点", "aliases": ["our town", "town"]},
            {"name": "小怪物", "type": "角色", "aliases": ["these little monsters", "little monsters"]},
        ],
        "relations": [],
    },
    "5309d527b97e6a5c": NOOP["5309d527b97e6a5c"],
    "30a793cb2cc5044b": {
        "entities": [
            {"name": "菲力牛排", "type": "物品", "aliases": ["Fillet steak"]},
            {"name": "腌牛肉", "type": "物品", "aliases": ["corned beef"]},
            {"name": "棒球手套", "type": "物品", "aliases": ["baseball gloves"]},
            {"name": "致幻剂", "type": "物品", "aliases": ["the hallucinogen", "hallucinogen"]},
            {"name": "风暴", "type": "现象", "aliases": ["the storm", "storm"]},
        ],
        "relations": [],
    },
    "d6035408355a6ac7": {
        "entities": [
            {"name": "糖精甜味剂", "type": "物品", "aliases": ["saccharine sweeteners", "these saccharine sweeteners"]},
            {"name": "数学", "type": "概念", "aliases": ["math"]},
        ],
        "relations": [],
    },
    "432a87f634611efe": {
        "entities": [
            {"name": "简", "type": "角色", "aliases": ["Jane"]},
            {"name": "商店", "type": "地点", "aliases": ["shop", "shops"]},
            {"name": "仇恨街", "type": "地点", "aliases": ["Hate Street"]},
        ],
        "relations": [
            {"src": "商店", "dst": "仇恨街", "relation": "迁离", "confidence": 0.8},
        ],
    },
    "e175ddcfb406294e": {
        "entities": [
            {"name": "街道", "type": "地点", "aliases": ["these streets", "streets"]},
            {"name": "艺术家拖车", "type": "物品", "aliases": ["artist trailers"]},
            {"name": "占卜师", "type": "角色", "aliases": ["the diviners", "diviners"]},
            {"name": "卡尼斯", "type": "角色", "aliases": ["canists"]},
        ],
        "relations": [],
    },
    "519cdb37c84f4291": {
        "entities": [
            {"name": "B级权限", "type": "概念", "aliases": ["Access level B"]},
            {"name": "紧急支援队", "type": "组织", "aliases": ["emergency support team", "the emergency support team", "Emergency support"]},
            {"name": "奥术波动", "type": "现象", "aliases": ["arcane fluctuations"]},
            {"name": "团队", "type": "组织", "aliases": ["team", "our team"]},
        ],
        "relations": [],
    },
    "6a69ef8b9c4b72fd": {
        "entities": [
            {"name": "大门", "type": "物品", "aliases": ["gate", "this gate"]},
            {"name": "毒蛇巢穴", "type": "地点", "aliases": ["nest of vipers", "their nest of vipers"]},
            {"name": "薯条", "type": "角色", "aliases": ["french fry"]},
            {"name": "仪式", "type": "事件", "aliases": ["ceremony", "that ceremony of theirs"]},
            {"name": "最终启示", "type": "事件", "aliases": ["last revelation", "the last revelation"]},
        ],
        "relations": [
            {"src": "毒蛇巢穴", "dst": "大门", "relation": "位于其后", "confidence": 0.7},
            {"src": "仪式", "dst": "最终启示", "relation": "关乎", "confidence": 0.7},
        ],
    },
    "592f99221799653a": {
        "entities": [
            {"name": "主人", "type": "角色", "aliases": ["host", "our host"]},
            {"name": "新客人", "type": "角色", "aliases": ["new guests"]},
        ],
        "relations": [
            {"src": "主人", "dst": "新客人", "relation": "酬谢", "confidence": 0.7},
        ],
    },
    "183b6db3fd022eda": {
        "entities": [
            {"name": "援军", "type": "组织", "aliases": ["reinforcements", "the reinforcements"]},
        ],
        "relations": [],
    },
    "cc42cc987b82e2b8": {
        "entities": [
            {"name": "枪", "type": "物品", "aliases": ["gun", "the gun"]},
            {"name": "汽车旅馆", "type": "地点", "aliases": ["motel", "this motel"]},
            {"name": "雇佣兵", "type": "角色", "aliases": ["mercenary", "a mercenary"]},
        ],
        "relations": [],
    },
    "b9240a0a4dc81f47": {
        "entities": [
            {"name": "蹄印", "type": "现象", "aliases": ["hoof prints", "the hoof prints"]},
        ],
        "relations": [],
    },
    "f66bb55f6966178d": {
        "entities": [
            {"name": "仪式", "type": "事件", "aliases": ["ritual", "the ritual"]},
            {"name": "一等航空兵", "type": "角色", "aliases": ["Airman First Class"]},
        ],
        "relations": [
            {"src": "一等航空兵", "dst": "仪式", "relation": "意欲废除", "confidence": 0.7},
        ],
    },
    "8f0d4f49e0093bd5": {
        "entities": [
            {"name": "狼", "type": "角色", "aliases": ["wolf", "a wolf"]},
        ],
        "relations": [],
    },
    "1b762c447776ebab": {
        "entities": [
            {"name": "唤醒程序", "type": "概念", "aliases": ["wake-up procedure", "free wake-up procedure"]},
            {"name": "卫生推车", "type": "物品", "aliases": ["sanitary trolley", "the sanitary trolley"]},
            {"name": "最大垃圾袋", "type": "物品", "aliases": ["garbage bag", "the biggest garbage bag"]},
        ],
        "relations": [
            {"src": "最大垃圾袋", "dst": "卫生推车", "relation": "存放于", "confidence": 0.8},
        ],
    },
    "01d02646bf0b97ed": {
        "entities": [
            {"name": "小蠕虫", "type": "角色", "aliases": ["tiny worms", "these tiny worms"]},
            {"name": "滴水", "type": "现象", "aliases": ["dripping water", "the dripping water"]},
            {"name": "咒语", "type": "概念", "aliases": ["incantations"]},
        ],
        "relations": [
            {"src": "咒语", "dst": "小蠕虫", "relation": "克制", "confidence": 0.7},
        ],
    },
    "4e4e3c6cf33fd064": {
        "entities": [
            {"name": "茶水", "type": "物品", "aliases": ["tea", "the tea"]},
        ],
        "relations": [],
    },
    "c3b308d3c11e102c": {
        "entities": [
            {"name": "那艘船", "type": "物品", "aliases": ["ship", "the ship"]},
        ],
        "relations": [],
    },
    "78b15cd5ea1eae47": {
        "entities": [
            {"name": "罢工", "type": "事件", "aliases": ["strike", "a strike"]},
            {"name": "伦敦", "type": "地点", "aliases": ["London"]},
            {"name": "烟草病", "type": "现象", "aliases": ["Tobacolosis"]},
            {"name": "空气污染", "type": "现象", "aliases": ["air pollution"]},
            {"name": "肺结核", "type": "现象", "aliases": ["TB"]},
            {"name": "风暴", "type": "现象", "aliases": ["storm", "the storm"]},
            {"name": "1952年大烟雾", "type": "事件", "aliases": ["Great Smog of 1952", "the Great Smog of 1952"]},
        ],
        "relations": [
            {"src": "罢工", "dst": "伦敦", "relation": "结束于", "confidence": 0.85},
            {"src": "肺结核", "dst": "1952年大烟雾", "relation": "严重度逼近", "confidence": 0.7},
            {"src": "空气污染", "dst": "肺结核", "relation": "关联", "confidence": 0.6},
        ],
    },
    "4894459024d17e35": {
        "entities": [
            {"name": "巴芬", "type": "角色", "aliases": ["Baffin"]},
            {"name": "袋鼠", "type": "角色", "aliases": ["kangaroo", "a kangaroo"]},
            {"name": "烟雾", "type": "现象", "aliases": ["smog", "this smog"]},
            {"name": "小巷", "type": "地点", "aliases": ["alley", "the end of the alley", "an alley"]},
        ],
        "relations": [
            {"src": "巴芬", "dst": "袋鼠", "relation": "大如", "confidence": 0.7},
            {"src": "巴芬", "dst": "小巷", "relation": "注视", "confidence": 0.6},
        ],
    },
    "a3fb4906532ad931": {
        "entities": [
            {"name": "传单", "type": "物品", "aliases": ["flyer", "the flyer"]},
            {"name": "医生", "type": "角色", "aliases": ["doctor", "a doctor"]},
            {"name": "肺结核爆发", "type": "事件", "aliases": ["tuberculosis outbreak", "a tuberculosis outbreak"]},
            {"name": "黑雾", "type": "现象", "aliases": ["black fog", "strange black fog", "Black fog"]},
            {"name": "医院", "type": "地点", "aliases": ["hospital", "the hospital"]},
            {"name": "烟雾", "type": "现象", "aliases": ["smog"]},
            {"name": "黑烟", "type": "现象", "aliases": ["black smoke"]},
            {"name": "工厂烟囱", "type": "地点", "aliases": ["factory chimneys", "the factory chimneys"]},
            {"name": "十字街", "type": "地点", "aliases": ["Cross Street"]},
            {"name": "卡尼斯", "type": "角色", "aliases": ["canists"]},
        ],
        "relations": [
            {"src": "黑雾", "dst": "医院", "relation": "破坏", "confidence": 0.85},
            {"src": "医生", "dst": "肺结核爆发", "relation": "调查", "confidence": 0.85},
            {"src": "黑雾", "dst": "烟雾", "relation": "区别于", "confidence": 0.6},
            {"src": "黑烟", "dst": "工厂烟囱", "relation": "来自", "confidence": 0.7},
        ],
    },
    "3f07f72fb5a8096b": {
        "entities": [
            {"name": "空气污染", "type": "现象", "aliases": ["air pollution", "the air pollution"]},
            {"name": "十字街", "type": "地点", "aliases": ["Cross Street"]},
            {"name": "浓雾", "type": "现象", "aliases": ["fog", "the fog"]},
        ],
        "relations": [
            {"src": "十字街", "dst": "浓雾", "relation": "不顾", "confidence": 0.6},
            {"src": "空气污染", "dst": "浓雾", "relation": "关联", "confidence": 0.6},
        ],
    },
    "eab8d53d34043a6b": {
        "entities": [
            {"name": "蒸汽涡轮", "type": "物品", "aliases": ["steam turbines", "the steam turbines"]},
            {"name": "螺丝", "type": "物品", "aliases": ["screws"]},
            {"name": "烟囱", "type": "物品", "aliases": ["chimneys"]},
            {"name": "黑雾", "type": "现象", "aliases": ["black fog", "this black fog"]},
        ],
        "relations": [
            {"src": "蒸汽涡轮", "dst": "烟囱", "relation": "含", "confidence": 0.6},
            {"src": "螺丝", "dst": "蒸汽涡轮", "relation": "固定", "confidence": 0.6},
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
    print(f"[apply-missing-p39] 写入 {len(RESULTS)} 条")
    return 0


if __name__ == "__main__":
    sys.exit(main())
