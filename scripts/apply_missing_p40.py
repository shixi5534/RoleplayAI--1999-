#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""补抽 backfill3 中 batch_mid_02 / batch_mid_03 共 50 个剧情块。
手工抽取，写盘前 validate() 悬空自检 + landing() 落地自检。"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "knowledge" / "plot_cache" / "wu_ming_zhe"
CORPUS = ROOT / "data" / "knowledge" / "plot_corpus_wu_ming_zhe.json"

RESULTS = {
    # ===== batch_mid_02 =====
    "7dcd9f9890522410": {"entities": [], "relations": []},

    "3e868d5d8d2be62c": {
        "entities": [
            {"name": "乌卢鲁委员会", "type": "组织", "aliases": ["Uluru Committee", "the Uluru Committee"]},
            {"name": "福格先生", "type": "角色", "aliases": ["Mr Fogg"]},
        ],
        "relations": [
            {"src": "乌卢鲁委员会", "dst": "福格先生", "relation": "补偿", "confidence": 0.8},
        ],
    },

    "7532c50e122f0c4d": {
        "entities": [
            {"name": "牙仙小姐", "type": "角色", "aliases": ["Ms.Tooth Fairy"]},
        ],
        "relations": [],
    },

    "7eb2307a9b68cad8": {
        "entities": [
            {"name": "乌卢鲁运动会", "type": "事件", "aliases": ["Uluru Games", "the Uluru Games"]},
            {"name": "基金会", "type": "组织", "aliases": ["the Foundation"]},
        ],
        "relations": [
            {"src": "基金会", "dst": "乌卢鲁运动会", "relation": "未干涉", "confidence": 0.8},
        ],
    },

    "2f8b90549ca9de7d": {
        "entities": [
            {"name": "福格先生", "type": "角色", "aliases": ["Mr.Fogg"]},
            {"name": "Fludder Page", "type": "组织", "aliases": []},
            {"name": "亚瑟", "type": "角色", "aliases": ["Arthur"]},
            {"name": "烟雾", "type": "现象", "aliases": ["the smog", "smog"]},
        ],
        "relations": [
            {"src": "福格先生", "dst": "Fludder Page", "relation": "拒绝取用", "confidence": 0.75},
        ],
    },

    "57d3c17ca1962e69": {
        "entities": [
            {"name": "基金会", "type": "组织", "aliases": ["foundation"]},
            {"name": "基金会掩盖事件", "type": "事件", "aliases": ["foundation cover-ups"]},
        ],
        "relations": [
            {"src": "基金会", "dst": "基金会掩盖事件", "relation": "掩盖", "confidence": 0.8},
        ],
    },

    "66bc76f2f4f31bb5": {
        "entities": [
            {"name": "政治游戏", "type": "概念", "aliases": ["the game of politics"]},
            {"name": "那次逃脱", "type": "事件", "aliases": ["that escape"]},
        ],
        "relations": [],
    },

    "fd2b1be79c5cbe63": {
        "entities": [
            {"name": "主管办公室", "type": "地点", "aliases": ["the supervisor's office", "supervisor's office"]},
            {"name": "图书馆", "type": "地点", "aliases": ["the library", "library"]},
            {"name": "812号窗", "type": "地点", "aliases": ["window 812"]},
        ],
        "relations": [
            {"src": "812号窗", "dst": "图书馆", "relation": "位于", "confidence": 0.7},
        ],
    },

    "e27acd4b68ebab1b": {
        "entities": [
            {"name": "法克顿", "type": "角色", "aliases": ["Farkton"]},
            {"name": "二楼", "type": "地点", "aliases": ["the second floor", "second floor"]},
        ],
        "relations": [],
    },

    "17516b6f6c0d964d": {
        "entities": [
            {"name": "第一圆环", "type": "概念", "aliases": ["the First Circle", "First Circle"]},
            {"name": "初民", "type": "概念", "aliases": ["The First of Man"]},
        ],
        "relations": [],
    },

    "7504cab9ac15941a": {"entities": [], "relations": []},

    "df4c38437f230b77": {
        "entities": [
            {"name": "神祇", "type": "角色", "aliases": ["The gods", "gods"]},
            {"name": "灵感", "type": "概念", "aliases": ["inspiration"]},
        ],
        "relations": [
            {"src": "神祇", "dst": "灵感", "relation": "思索", "confidence": 0.7},
        ],
    },

    "876d26f6fdd5b365": {
        "entities": [
            {"name": "几何形体", "type": "概念", "aliases": ["the geometric bodies", "geometric bodies"]},
            {"name": "超越界", "type": "概念", "aliases": ["the Transcendental World", "Transcendental World"]},
            {"name": "妈妈", "type": "角色", "aliases": ["Mama"]},
            {"name": "黑暗", "type": "现象", "aliases": ["The darkness", "darkness"]},
        ],
        "relations": [
            {"src": "几何形体", "dst": "超越界", "relation": "显现", "confidence": 0.8},
        ],
    },

    "b492d9be3d511cc2": {
        "entities": [
            {"name": "天文台", "type": "地点", "aliases": ["the observatory", "observatory"]},
            {"name": "施密特博士", "type": "角色", "aliases": ["Dr.Schmidt"]},
            {"name": "恒星级黑洞", "type": "概念", "aliases": ["a stellar black hole", "stellar black hole"]},
        ],
        "relations": [
            {"src": "施密特博士", "dst": "恒星级黑洞", "relation": "推断退行", "confidence": 0.7},
        ],
    },

    "e87645b8e1f7bc66": {
        "entities": [
            {"name": "超大质量黑洞", "type": "概念", "aliases": ["a supermassive black hole", "supermassive black hole"]},
            {"name": "空间之境", "type": "概念", "aliases": ["the realm of space"]},
            {"name": "类星体", "type": "概念", "aliases": ["the Quasars", "Quasars"]},
            {"name": "超新星", "type": "现象", "aliases": ["a supernova", "supernova"]},
        ],
        "relations": [
            {"src": "类星体", "dst": "超新星", "relation": "近似", "confidence": 0.7},
        ],
    },

    "736ef5a590ef7988": {
        "entities": [
            {"name": "父亲", "type": "角色", "aliases": ["Mon père"]},
            {"name": "雕像", "type": "物品", "aliases": ["ces statues", "statues"]},
            {"name": "入口", "type": "地点", "aliases": ["l'entrée", "entrée"]},
        ],
        "relations": [
            {"src": "父亲", "dst": "雕像", "relation": "提及", "confidence": 0.8},
        ],
    },

    "b67f476479c83f2a": {
        "entities": [
            {"name": "警察局长", "type": "角色", "aliases": ["the police chief", "police chief"]},
            {"name": "主管", "type": "角色", "aliases": ["the director"]},
            {"name": "枪击", "type": "事件", "aliases": ["the shooting"]},
            {"name": "搜查令", "type": "物品", "aliases": ["a search warrant", "search warrant"]},
            {"name": "李英", "type": "角色", "aliases": ["Li Ying"]},
            {"name": "女警官", "type": "角色", "aliases": ["Miss Officer"]},
        ],
        "relations": [],
    },

    "812656b31bd88310": {
        "entities": [
            {"name": "桑河游行", "type": "事件", "aliases": ["the Sun Ho Parade", "Sun Ho Parade"]},
            {"name": "庆典", "type": "事件", "aliases": ["the celebration"]},
        ],
        "relations": [
            {"src": "桑河游行", "dst": "庆典", "relation": "即是", "confidence": 0.85},
        ],
    },

    "b15607310b340eeb": {
        "entities": [
            {"name": "拉瑟姆小姐", "type": "角色", "aliases": ["Miss Latham"]},
            {"name": "Using", "type": "角色", "aliases": []},
            {"name": "阿森", "type": "角色", "aliases": ["Ah Sen"]},
            {"name": "那根针", "type": "物品", "aliases": ["that needle", "needle"]},
        ],
        "relations": [],
    },

    "892520b1044c5bf4": {
        "entities": [
            {"name": "那部影片", "type": "物品", "aliases": ["the film", "film"]},
            {"name": "特蕾莎", "type": "角色", "aliases": ["Teresa"]},
        ],
        "relations": [],
    },

    "2111f8ec21c99eb5": {
        "entities": [
            {"name": "阿星", "type": "角色", "aliases": ["Ah Sing"]},
            {"name": "最佳影片", "type": "概念", "aliases": ["the best film", "best film"]},
            {"name": "更好的影片", "type": "概念", "aliases": ["a better film", "better film"]},
        ],
        "relations": [],
    },

    "324f416a3921cda7": {
        "entities": [
            {"name": "阿尔金制作产业", "type": "组织", "aliases": ["the Arkin production industry", "Arkin production industry"]},
        ],
        "relations": [],
    },

    "882a0b56b1cbfb52": {
        "entities": [
            {"name": "我的零食", "type": "物品", "aliases": ["my precious munchies", "munchies"]},
            {"name": "隔壁邻居", "type": "角色", "aliases": ["my next-door neighbor", "next-door neighbor"]},
            {"name": "监狱", "type": "地点", "aliases": ["jail"]},
            {"name": "蒙查洛", "type": "角色", "aliases": ["monchalos"]},
            {"name": "副本", "type": "角色", "aliases": ["The copy", "the copy"]},
        ],
        "relations": [
            {"src": "隔壁邻居", "dst": "监狱", "relation": "被关押", "confidence": 0.8},
        ],
    },

    "bb0066183faf1103": {
        "entities": [
            {"name": "强良", "type": "角色", "aliases": ["the Qiang Liang", "Qiang Liang"]},
            {"name": "家族编年史", "type": "物品", "aliases": ["our family chronicles", "family chronicles"]},
        ],
        "relations": [
            {"src": "家族编年史", "dst": "强良", "relation": "记载", "confidence": 0.7},
        ],
    },

    "63f7dbc41650d44a": {
        "entities": [
            {"name": "我们部门", "type": "组织", "aliases": ["our department"]},
            {"name": "侦探C.O.7电影", "type": "物品", "aliases": ["detective C.O.7 films", "C.O.7 films"]},
            {"name": "奥术", "type": "概念", "aliases": ["Arcanum"]},
            {"name": "奥术师", "type": "角色", "aliases": ["Arcanists"]},
            {"name": "夜刃", "type": "概念", "aliases": ["Nightpiercer"]},
        ],
        "relations": [
            {"src": "侦探C.O.7电影", "dst": "奥术", "relation": "聚焦", "confidence": 0.8},
            {"src": "侦探C.O.7电影", "dst": "奥术师", "relation": "聚焦", "confidence": 0.8},
            {"src": "夜刃", "dst": "侦探C.O.7电影", "relation": "招式近似", "confidence": 0.7},
        ],
    },

    # ===== batch_mid_03 =====
    "1226d4456e697082": {
        "entities": [
            {"name": "新闻", "type": "角色", "aliases": ["News"]},
            {"name": "奥术支援", "type": "概念", "aliases": ["immediate arcana support", "arcana support"]},
            {"name": "市政厅", "type": "地点", "aliases": ["City hall"]},
        ],
        "relations": [],
    },

    "1491aab1a20a77f6": {
        "entities": [
            {"name": "强良", "type": "角色", "aliases": ["Qiang Liang"]},
        ],
        "relations": [],
    },

    "232f4b818ce3f1bf": {
        "entities": [
            {"name": "年末", "type": "时间", "aliases": ["the end of the year"]},
            {"name": "肖霍尔游行", "type": "事件", "aliases": ["the Shohour Parade", "Shohour Parade"]},
            {"name": "结局", "type": "概念", "aliases": ["the ending"]},
            {"name": "最后一部CO7影片", "type": "物品", "aliases": ["the last film in the CO7 series"]},
        ],
        "relations": [
            {"src": "最后一部CO7影片", "dst": "结局", "relation": "有结局", "confidence": 0.85},
            {"src": "肖霍尔游行", "dst": "结局", "relation": "令人想起", "confidence": 0.8},
        ],
    },

    "17c425efa619bf34": {
        "entities": [
            {"name": "风暴", "type": "现象", "aliases": ["La tempête", "tempête"]},
            {"name": "各部门", "type": "组织", "aliases": ["chaque département", "département"]},
            {"name": "妈妈", "type": "角色", "aliases": ["maman"]},
            {"name": "齐亚夫人", "type": "角色", "aliases": ["Madame Zia"]},
            {"name": "玛蒂尔德·阿布阿尼什", "type": "角色", "aliases": ["Mathilde Abouaniche"]},
        ],
        "relations": [
            {"src": "齐亚夫人", "dst": "妈妈", "relation": "监视", "confidence": 0.8},
            {"src": "各部门", "dst": "风暴", "relation": "研究", "confidence": 0.8},
        ],
    },

    "7dcca37d5c6d4c01": {
        "entities": [
            {"name": "那口板条箱", "type": "物品", "aliases": ["the crate", "crate"]},
            {"name": "咒语", "type": "物品", "aliases": ["this incantation", "incantation"]},
            {"name": "一等航空兵", "type": "角色", "aliases": ["Airman First Class"]},
            {"name": "总部", "type": "地点", "aliases": ["headquarters"]},
        ],
        "relations": [],
    },

    "6bfcfc4f79b5b1af": {
        "entities": [
            {"name": "我的汽车旅馆", "type": "地点", "aliases": ["my motel", "motel"]},
            {"name": "那间舒适小屋", "type": "地点", "aliases": ["this cozy little room"]},
        ],
        "relations": [],
    },

    "9c9ecdbc0abb6a37": {
        "entities": [
            {"name": "裹布母猴", "type": "角色", "aliases": ["the mother covered in cloth"]},
        ],
        "relations": [],
    },

    "e28d23943ba9b927": {"entities": [], "relations": []},

    "471fce84d114619d": {
        "entities": [
            {"name": "一份报纸", "type": "物品", "aliases": ["A newspaper", "newspaper"]},
            {"name": "他们的板车", "type": "物品", "aliases": ["Their cart", "cart"]},
        ],
        "relations": [],
    },

    "c3e01c03710e819b": {"entities": [], "relations": []},

    "166f9f5a8f26665a": {
        "entities": [
            {"name": "占卜", "type": "概念", "aliases": ["divination"]},
            {"name": "昨日", "type": "时间", "aliases": ["yesterday"]},
        ],
        "relations": [],
    },

    "ae0a8d4a171b9b0d": {
        "entities": [
            {"name": "警方通告", "type": "物品", "aliases": ["Police notice"]},
            {"name": "洒水车", "type": "物品", "aliases": ["a watering car", "watering car"]},
            {"name": "公共交通", "type": "概念", "aliases": ["public transit"]},
            {"name": "三天", "type": "时间", "aliases": ["three days"]},
            {"name": "崭新世界", "type": "概念", "aliases": ["A brand new world", "brand new world"]},
            {"name": "昨日", "type": "时间", "aliases": ["yesterday"]},
            {"name": "我的乌托邦", "type": "概念", "aliases": ["my utopia"]},
            {"name": "伦敦", "type": "地点", "aliases": ["London"]},
        ],
        "relations": [],
    },

    "509c9913c150f447": {
        "entities": [
            {"name": "毒瘾", "type": "概念", "aliases": ["Drug addiction"]},
            {"name": "早衰", "type": "概念", "aliases": ["premature senility"]},
            {"name": "不可逆身体损伤", "type": "概念", "aliases": ["irreversible physical damage"]},
            {"name": "奥术运动员", "type": "角色", "aliases": ["Arcanist athlete", "Arcanist athletes"]},
            {"name": "俱乐部", "type": "组织", "aliases": ["the clubs", "clubs"]},
            {"name": "赛事主办方", "type": "组织", "aliases": ["the hosts of the games"]},
            {"name": "药物滥用", "type": "概念", "aliases": ["Drug abuse"]},
        ],
        "relations": [
            {"src": "奥术运动员", "dst": "毒瘾", "relation": "遭受", "confidence": 0.8},
            {"src": "俱乐部", "dst": "毒瘾", "relation": "未担责", "confidence": 0.7},
            {"src": "赛事主办方", "dst": "毒瘾", "relation": "未担责", "confidence": 0.7},
        ],
    },

    "8961a3b8dbb68462": {
        "entities": [
            {"name": "谣言", "type": "概念", "aliases": ["rumours"]},
            {"name": "巨怪", "type": "角色", "aliases": ["a three-floor-high and multi-legged, gigantic monster"]},
            {"name": "售票亭", "type": "物品", "aliases": ["the ticket box", "ticket box"]},
            {"name": "哈皮", "type": "角色", "aliases": ["Happy"]},
        ],
        "relations": [
            {"src": "哈皮", "dst": "售票亭", "relation": "协助", "confidence": 0.7},
        ],
    },

    "4665acef5e81fbc8": {
        "entities": [
            {"name": "椅子上的红按钮", "type": "物品", "aliases": ["This red button on the chair", "red button"]},
            {"name": "这台打字机", "type": "物品", "aliases": ["This typewriter", "typewriter"]},
            {"name": "多丽丝", "type": "角色", "aliases": ["Doris"]},
        ],
        "relations": [],
    },

    "6f219cc566241d05": {
        "entities": [
            {"name": "入场费", "type": "物品", "aliases": ["your entry fee", "entry fee"]},
            {"name": "最高赌注赌徒", "type": "角色", "aliases": ["the highest stakes gambler"]},
            {"name": "赌桌", "type": "物品", "aliases": ["the table", "table"]},
            {"name": "黑袍者", "type": "角色", "aliases": ["the black robes", "black robes"]},
            {"name": "混乱", "type": "概念", "aliases": ["chaos"]},
        ],
        "relations": [
            {"src": "黑袍者", "dst": "赌桌", "relation": "图谋掀翻", "confidence": 0.85},
            {"src": "赌桌", "dst": "混乱", "relation": "引发", "confidence": 0.7},
        ],
    },

    "ad937888ce53f09d": {"entities": [], "relations": []},

    "1190da5b07e7db95": {
        "entities": [
            {"name": "新命令", "type": "概念", "aliases": ["Les nouvelles ordres", "nouvelles ordres"]},
            {"name": "O2的编辑", "type": "组织", "aliases": ["les éditeurs de O2", "éditeurs de O2"]},
            {"name": "奥术师", "type": "角色", "aliases": ["ces deux Arcanistes", "Arcanistes"]},
            {"name": "谐和转换", "type": "事件", "aliases": ["la conversion harmonique", "conversion harmonique"]},
            {"name": "预言", "type": "概念", "aliases": ["la prophétie", "prophétie"]},
            {"name": "末世论", "type": "概念", "aliases": ["l'eschatologie", "eschatologie"]},
        ],
        "relations": [
            {"src": "谐和转换", "dst": "预言", "relation": "揭示失效", "confidence": 0.8},
            {"src": "谐和转换", "dst": "末世论", "relation": "揭示失效", "confidence": 0.8},
            {"src": "新命令", "dst": "O2的编辑", "relation": "涉及", "confidence": 0.7},
        ],
    },

    "37c32f975ce75ce7": {
        "entities": [
            {"name": "那场火", "type": "现象", "aliases": ["le feu", "feu"]},
            {"name": "灵能者", "type": "角色", "aliases": ["psychique"]},
        ],
        "relations": [],
    },

    "b383a85506eb7999": {
        "entities": [
            {"name": "常态者", "type": "角色", "aliases": ["a normalist", "normalist"]},
            {"name": "布朗先生", "type": "角色", "aliases": ["Mr.Brown"]},
            {"name": "奥术师", "type": "角色", "aliases": ["an arcanist", "arcanist"]},
            {"name": "黏腻魅力", "type": "概念", "aliases": ["That long-sticky charisma"]},
            {"name": "粗俗近身喜剧", "type": "概念", "aliases": ["this vulgar hand-to-hand comedy"]},
        ],
        "relations": [
            {"src": "布朗先生", "dst": "粗俗近身喜剧", "relation": "施展", "confidence": 0.7},
        ],
    },

    "33376271e4210f82": {
        "entities": [
            {"name": "诺塞勒曼", "type": "角色", "aliases": ["NoSeleman"]},
            {"name": "特别调查员", "type": "角色", "aliases": ["the special investigator"]},
            {"name": "玛蒂尔达·博阿尼什", "type": "角色", "aliases": ["Matilda Boanich"]},
            {"name": "索内托小姐", "type": "角色", "aliases": ["Mademoiselle Sonnetto"]},
            {"name": "启蒙", "type": "概念", "aliases": ["The Enlightenment", "Enlightenment"]},
        ],
        "relations": [
            {"src": "玛蒂尔达·博阿尼什", "dst": "特别调查员", "relation": "是身份", "confidence": 0.85},
        ],
    },

    "ee85d156ff9f3612": {"entities": [], "relations": []},

    "5bccd90cd228db10": {
        "entities": [
            {"name": "那艘船", "type": "物品", "aliases": ["ship"]},
            {"name": "璀璨文明世界", "type": "概念", "aliases": ["the resplendent civilized world", "civilized world"]},
            {"name": "疯狂", "type": "概念", "aliases": ["Madness"]},
            {"name": "知识", "type": "概念", "aliases": ["the sedative that is knowledge"]},
            {"name": "疯狂与文明之战", "type": "事件", "aliases": ["a war between madness and civilization"]},
            {"name": "文明", "type": "概念", "aliases": ["civilization"]},
            {"name": "他的基地", "type": "地点", "aliases": ["his home base"]},
        ],
        "relations": [
            {"src": "疯狂", "dst": "文明", "relation": "交战", "confidence": 0.85},
            {"src": "疯狂", "dst": "知识", "relation": "源自", "confidence": 0.75},
        ],
    },

    "1406c3cc0b837842": {
        "entities": [
            {"name": "隐喻大师", "type": "角色", "aliases": ["a master of metaphor", "master of metaphor"]},
            {"name": "是非", "type": "概念", "aliases": ["right from wrong"]},
            {"name": "幻想与现实", "type": "概念", "aliases": ["fantasy from reality"]},
        ],
        "relations": [],
    },

    "a1e44db6bcd1cf45": {
        "entities": [
            {"name": "努卡泰人", "type": "角色", "aliases": ["the Nukatai", "Nukatai"]},
            {"name": "克雷莫纳人", "type": "角色", "aliases": ["Cremonese"]},
            {"name": "小提琴", "type": "物品", "aliases": ["its violins", "violins", "the violin"]},
            {"name": "中提琴", "type": "物品", "aliases": ["the viola", "viola"]},
            {"name": "大提琴", "type": "物品", "aliases": ["the violoncello", "violoncello"]},
        ],
        "relations": [
            {"src": "克雷莫纳人", "dst": "小提琴", "relation": "以之为荣", "confidence": 0.85},
            {"src": "克雷莫纳人", "dst": "中提琴", "relation": "热爱", "confidence": 0.8},
            {"src": "克雷莫纳人", "dst": "大提琴", "relation": "热爱", "confidence": 0.8},
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
    noop = [h for h, d in RESULTS.items() if not (d.get("entities") or []) and not (d.get("relations") or [])]
    print(f"[validate] 块 {len(RESULTS)}，悬空 {v}，未落地 {m}")
    print(f"[stats] 实体 {total_e}，关系 {total_r}")
    print(f"[noop] 判无内容 {len(noop)}: {noop}")
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
    print(f"[apply-missing-p40] 写入 {len(RESULTS)} 条")
    return 0


if __name__ == "__main__":
    sys.exit(main())
