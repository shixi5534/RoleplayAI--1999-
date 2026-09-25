#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""补抽 2 个批次（batch_midhigh_08 / batch_midhigh_09）的未抽取剧情块。
手工抽取，写盘前 validate() 悬空自检 + landing() 落地自检。"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "knowledge" / "plot_cache" / "wu_ming_zhe"
CORPUS = ROOT / "data" / "knowledge" / "plot_corpus_wu_ming_zhe.json"

RESULTS = {
    # ===== batch_midhigh_08 =====
    "cea4bc8fc0b0f3ab": {
        "entities": [
            {"name": "酒店", "type": "地点", "aliases": ["a hotel"]},
            {"name": "旅行者", "type": "角色", "aliases": ["A traveler"]},
            {"name": "哭泣的孩子", "type": "角色", "aliases": ["A crying child"]},
            {"name": "母亲", "type": "角色", "aliases": ["their mother"]},
        ],
        "relations": [
            {"src": "母亲", "dst": "哭泣的孩子", "relation": "安抚", "confidence": 0.7},
        ],
    },
    "0f2d83b2afcd5451": {
        "entities": [
            {"name": "高级小怪", "type": "角色", "aliases": ["advanced critter"]},
            {"name": "神秘学技能", "type": "概念", "aliases": ["arcane skills"]},
            {"name": "神秘学家", "type": "角色", "aliases": ["arcaneist"]},
        ],
        "relations": [
            {"src": "神秘学技能", "dst": "高级小怪", "relation": "对其无效", "confidence": 0.8},
        ],
    },
    "4aaffbed8caf7130": {
        "entities": [
            {"name": "鬼婆", "type": "角色", "aliases": ["the Hag", "Hag"]},
            {"name": "小怪", "type": "角色", "aliases": ["critters"]},
            {"name": "花园", "type": "地点", "aliases": ["her garden"]},
            {"name": "蜗牛", "type": "物品", "aliases": ["snails"]},
            {"name": "神秘学技能", "type": "概念", "aliases": ["arcane skills"]},
        ],
        "relations": [
            {"src": "鬼婆", "dst": "花园", "relation": "拥有", "confidence": 0.8},
            {"src": "鬼婆", "dst": "神秘学技能", "relation": "传授", "confidence": 0.8},
            {"src": "小怪", "dst": "花园", "relation": "出自", "confidence": 0.8},
        ],
    },
    "cda961aced914eb9": {
        "entities": [
            {"name": "雾婆", "type": "角色", "aliases": ["fog hag"]},
            {"name": "蟾蜍怪", "type": "角色", "aliases": ["toad monster"]},
            {"name": "古代炼金术师", "type": "角色", "aliases": ["ancient alchemist"]},
            {"name": "夏洛特·奥哈根", "type": "角色", "aliases": ["Charlotte O'Hagan"]},
            {"name": "鬼屋", "type": "地点", "aliases": ["haunted house"]},
            {"name": "蜗牛", "type": "物品", "aliases": ["Snails"]},
        ],
        "relations": [
            {"src": "夏洛特·奥哈根", "dst": "雾婆", "relation": "是", "confidence": 0.85},
            {"src": "夏洛特·奥哈根", "dst": "蟾蜍怪", "relation": "是", "confidence": 0.7},
            {"src": "古代炼金术师", "dst": "夏洛特·奥哈根", "relation": "造出", "confidence": 0.7},
            {"src": "夏洛特·奥哈根", "dst": "鬼屋", "relation": "居住", "confidence": 0.8},
        ],
    },
    "7c0a6e66a742bd43": {
        "entities": [
            {"name": "格雷戈里", "type": "角色", "aliases": ["Gregory"]},
            {"name": "福格先生", "type": "角色", "aliases": ["Mr.Fogg"]},
            {"name": "麦克风", "type": "物品", "aliases": ["the microphone"]},
            {"name": "典礼", "type": "事件", "aliases": ["the ceremony"]},
        ],
        "relations": [
            {"src": "福格先生", "dst": "典礼", "relation": "出席", "confidence": 0.7},
            {"src": "麦克风", "dst": "典礼", "relation": "用于", "confidence": 0.7},
        ],
    },
    "c81707c48a7f92f7": {
        "entities": [
            {"name": "乌卢鲁运动会", "type": "事件", "aliases": ["Uluru Games"]},
            {"name": "伦敦预选赛", "type": "事件", "aliases": ["The London qualifiers"]},
            {"name": "布里姆利先生", "type": "角色", "aliases": ["Mr.Brimley"]},
            {"name": "体育场", "type": "地点", "aliases": ["the stadium"]},
            {"name": "福格先生", "type": "角色", "aliases": ["Mr.Fogg"]},
            {"name": "黑雾团", "type": "现象", "aliases": ["A ball of black fog", "black fog"]},
            {"name": "小巷", "type": "地点", "aliases": ["the alley"]},
            {"name": "小怪", "type": "角色", "aliases": ["critter"]},
        ],
        "relations": [
            {"src": "乌卢鲁运动会", "dst": "伦敦预选赛", "relation": "取消", "confidence": 0.85},
            {"src": "布里姆利先生", "dst": "体育场", "relation": "讲述", "confidence": 0.8},
            {"src": "黑雾团", "dst": "小巷", "relation": "出现于", "confidence": 0.8},
            {"src": "黑雾团", "dst": "小怪", "relation": "弱于", "confidence": 0.7},
        ],
    },
    "874b6715136a7de2": {
        "entities": [
            {"name": "十字街", "type": "地点", "aliases": ["Cross Street"]},
            {"name": "预选赛", "type": "事件", "aliases": ["the qualifiers"]},
            {"name": "铁", "type": "物品", "aliases": ["this iron", "iron"]},
            {"name": "传家宝", "type": "物品", "aliases": ["family heirloom"]},
            {"name": "漂浮射击弹弓", "type": "物品", "aliases": ["floating shot sling"]},
            {"name": "秒表", "type": "物品", "aliases": ["the stopwatch"]},
            {"name": "调解人", "type": "角色", "aliases": ["mediator"]},
        ],
        "relations": [
            {"src": "十字街", "dst": "预选赛", "relation": "请愿", "confidence": 0.8},
            {"src": "铁", "dst": "传家宝", "relation": "是", "confidence": 0.8},
            {"src": "铁", "dst": "漂浮射击弹弓", "relation": "改装为", "confidence": 0.8},
            {"src": "调解人", "dst": "秒表", "relation": "使用", "confidence": 0.7},
        ],
    },
    "86af8a0d9d4c3a13": {
        "entities": [
            {"name": "请愿书", "type": "物品", "aliases": ["petitions"]},
            {"name": "烟雾", "type": "现象", "aliases": ["the smog", "smog"]},
            {"name": "救济中心", "type": "组织", "aliases": ["the relief center"]},
            {"name": "活动", "type": "事件", "aliases": ["the event"]},
            {"name": "应急指南", "type": "物品", "aliases": ["the emergency guidebook", "emergency guidebook"]},
        ],
        "relations": [
            {"src": "救济中心", "dst": "活动", "relation": "处理文书", "confidence": 0.8},
            {"src": "应急指南", "dst": "烟雾", "relation": "应对", "confidence": 0.7},
        ],
    },
    "7f85cfaa29e58f8f": {
        "entities": [
            {"name": "伦敦乌卢鲁展览运动会", "type": "事件", "aliases": ["London Uluru Exhibition Games", "the London Uluru Exhibition Games"]},
            {"name": "烟", "type": "现象", "aliases": ["The smoke", "smoke"]},
            {"name": "体育场", "type": "地点", "aliases": ["the stadium"]},
            {"name": "运动员", "type": "角色", "aliases": ["athletes"]},
            {"name": "基金会", "type": "组织", "aliases": ["the foundation"]},
        ],
        "relations": [
            {"src": "伦敦乌卢鲁展览运动会", "dst": "体育场", "relation": "举办于", "confidence": 0.8},
            {"src": "基金会", "dst": "伦敦乌卢鲁展览运动会", "relation": "未支持", "confidence": 0.7},
        ],
    },
    "f7022bab9d82dd33": {
        "entities": [
            {"name": "雷文小姐", "type": "角色", "aliases": ["Miss Raven"]},
            {"name": "同学", "type": "角色", "aliases": ["My classmates"]},
            {"name": "小丑", "type": "角色", "aliases": ["clown"]},
            {"name": "夏日郊游", "type": "事件", "aliases": ["the summer outing"]},
            {"name": "运动日", "type": "事件", "aliases": ["sports days"]},
            {"name": "训练", "type": "概念", "aliases": ["the training"]},
        ],
        "relations": [],
    },
    "5132643690f7497a": {
        "entities": [
            {"name": "阿尔卡纳术师", "type": "角色", "aliases": ["Arkanists"]},
            {"name": "大屠杀", "type": "事件", "aliases": ["Massacres"]},
            {"name": "暴政", "type": "概念", "aliases": ["tyranny"]},
            {"name": "复仇", "type": "概念", "aliases": ["revenge"]},
            {"name": "基金会", "type": "组织", "aliases": ["the Foundation"]},
            {"name": "改革", "type": "概念", "aliases": ["reform"]},
            {"name": "风暴", "type": "现象", "aliases": ["the unexpected storm", "storm"]},
        ],
        "relations": [
            {"src": "阿尔卡纳术师", "dst": "大屠杀", "relation": "引发", "confidence": 0.85},
            {"src": "阿尔卡纳术师", "dst": "暴政", "relation": "造成", "confidence": 0.8},
            {"src": "阿尔卡纳术师", "dst": "复仇", "relation": "引发", "confidence": 0.8},
            {"src": "基金会", "dst": "改革", "relation": "缺乏", "confidence": 0.8},
            {"src": "风暴", "dst": "改革", "relation": "阻碍", "confidence": 0.7},
        ],
    },
    "85ce15f3568b1a27": {
        "entities": [
            {"name": "预言", "type": "概念", "aliases": ["the prophecy"]},
            {"name": "幻象", "type": "概念", "aliases": ["the vision", "vision"]},
            {"name": "断裂甲板", "type": "物品", "aliases": ["two broken decks", "broken decks"]},
            {"name": "深水", "type": "现象", "aliases": ["the deep water"]},
        ],
        "relations": [
            {"src": "预言", "dst": "幻象", "relation": "显现", "confidence": 0.7},
            {"src": "断裂甲板", "dst": "深水", "relation": "沉入", "confidence": 0.8},
        ],
    },
    "16b2cbb9eb07dd35": {
        "entities": [
            {"name": "阿尔卡努斯", "type": "角色", "aliases": ["Arcanus"]},
            {"name": "阿尔卡努斯罪犯", "type": "角色", "aliases": ["Arcanus' criminals"]},
            {"name": "商莲", "type": "角色", "aliases": ["Shang Lian"]},
            {"name": "幽影怪", "type": "角色", "aliases": ["spookter", "spooky spookter"]},
            {"name": "疯狂", "type": "概念", "aliases": ["madness"]},
        ],
        "relations": [
            {"src": "阿尔卡努斯", "dst": "疯狂", "relation": "血脉含", "confidence": 0.8},
            {"src": "阿尔卡努斯罪犯", "dst": "阿尔卡努斯", "relation": "源自", "confidence": 0.8},
        ],
    },
    "7b53a13d1826d97b": {
        "entities": [
            {"name": "强良", "type": "角色", "aliases": ["Qiang Liang"]},
            {"name": "双刃剑", "type": "概念", "aliases": ["a double-edged sword"]},
            {"name": "驱鬼服务", "type": "概念", "aliases": ["ghost busting service"]},
            {"name": "传奇神兽", "type": "角色", "aliases": ["legendary beast"]},
        ],
        "relations": [
            {"src": "传奇神兽", "dst": "双刃剑", "relation": "如同", "confidence": 0.7},
        ],
    },
    "d53b0a91dfcfc8a9": {
        "entities": [
            {"name": "补贴", "type": "概念", "aliases": ["My subsidy"]},
            {"name": "鸡肉三明治", "type": "物品", "aliases": ["chicken sandwich"]},
            {"name": "新手", "type": "角色", "aliases": ["rookie"]},
            {"name": "富家子弟", "type": "角色", "aliases": ["rich kid"]},
            {"name": "梁家", "type": "组织", "aliases": ["The Liang family", "Liang family"]},
            {"name": "传奇祖先", "type": "角色", "aliases": ["legendary ancestors"]},
        ],
        "relations": [
            {"src": "梁家", "dst": "传奇祖先", "relation": "拥有", "confidence": 0.85},
            {"src": "富家子弟", "dst": "梁家", "relation": "出身于", "confidence": 0.8},
        ],
    },
    "ed1b31da9fcb4929": {
        "entities": [
            {"name": "工作", "type": "概念", "aliases": ["the job"]},
            {"name": "家规", "type": "概念", "aliases": ["family rules"]},
            {"name": "搭档", "type": "角色", "aliases": ["partners"]},
            {"name": "LAPD神秘学事务部", "type": "组织", "aliases": ["LAPD Division of Arcane Affairs"]},
        ],
        "relations": [
            {"src": "搭档", "dst": "LAPD神秘学事务部", "relation": "任职于", "confidence": 0.8},
        ],
    },
    "f225b973c8da8596": {
        "entities": [
            {"name": "神秘学歪道", "type": "概念", "aliases": ["arcane skew"]},
            {"name": "不祥躬身", "type": "概念", "aliases": ["ominous obeisance"]},
            {"name": "受害者", "type": "角色", "aliases": ["victims"]},
            {"name": "骗子", "type": "角色", "aliases": ["scammer"]},
            {"name": "三回约翰尼", "type": "角色", "aliases": ["Johnny Three Times"]},
            {"name": "疯子", "type": "角色", "aliases": ["loony"]},
            {"name": "警方护送队", "type": "组织", "aliases": ["the police escort"]},
            {"name": "警官", "type": "角色", "aliases": ["officer"]},
            {"name": "手铐", "type": "物品", "aliases": ["the cuffs", "cuffs"]},
        ],
        "relations": [
            {"src": "三回约翰尼", "dst": "骗子", "relation": "是", "confidence": 0.85},
            {"src": "三回约翰尼", "dst": "受害者", "relation": "操控", "confidence": 0.85},
            {"src": "三回约翰尼", "dst": "神秘学歪道", "relation": "使用", "confidence": 0.8},
            {"src": "三回约翰尼", "dst": "不祥躬身", "relation": "使用", "confidence": 0.8},
            {"src": "疯子", "dst": "警方护送队", "relation": "袭击", "confidence": 0.8},
            {"src": "疯子", "dst": "三回约翰尼", "relation": "劫持", "confidence": 0.8},
            {"src": "警官", "dst": "三回约翰尼", "relation": "铐住", "confidence": 0.8},
        ],
    },
    "ff60e57a9f115771": {
        "entities": [
            {"name": "义务警员", "type": "角色", "aliases": ["young vigil"]},
            {"name": "搭档", "type": "角色", "aliases": ["partner"]},
            {"name": "老电影", "type": "物品", "aliases": ["old flicks"]},
            {"name": "电影", "type": "概念", "aliases": ["the movies", "movies"]},
            {"name": "侦探", "type": "角色", "aliases": ["detective"]},
        ],
        "relations": [
            {"src": "义务警员", "dst": "搭档", "relation": "合作", "confidence": 0.8},
            {"src": "侦探", "dst": "电影", "relation": "出演", "confidence": 0.75},
        ],
    },
    "88b345735d0115db": {
        "entities": [
            {"name": "结局", "type": "概念", "aliases": ["ending"]},
            {"name": "悲剧", "type": "概念", "aliases": ["Tragedy"]},
            {"name": "喜剧", "type": "概念", "aliases": ["comedy"]},
            {"name": "好人", "type": "角色", "aliases": ["the good guys"]},
            {"name": "坏人", "type": "角色", "aliases": ["the bad guys"]},
            {"name": "现实", "type": "概念", "aliases": ["Reality", "reality"]},
            {"name": "故事", "type": "概念", "aliases": ["stories"]},
            {"name": "电影", "type": "概念", "aliases": ["a movie"]},
        ],
        "relations": [
            {"src": "悲剧", "dst": "喜剧", "relation": "印象更深", "confidence": 0.8},
            {"src": "好人", "dst": "坏人", "relation": "败于", "confidence": 0.8},
            {"src": "现实", "dst": "悲剧", "relation": "如同", "confidence": 0.7},
            {"src": "电影", "dst": "现实", "relation": "折射", "confidence": 0.7},
        ],
    },
    "e2e651829b826227": {
        "entities": [
            {"name": "一等航空兵", "type": "角色", "aliases": ["Airman First Class"]},
            {"name": "飞行员", "type": "角色", "aliases": ["pilot"]},
            {"name": "剪贴簿", "type": "物品", "aliases": ["scrapbook"]},
            {"name": "飞行报告", "type": "物品", "aliases": ["the reports", "reports"]},
            {"name": "飞行", "type": "事件", "aliases": ["your flights", "flights"]},
            {"name": "士兵", "type": "角色", "aliases": ["soldier"]},
            {"name": "仪式", "type": "概念", "aliases": ["the ritual", "ritual"]},
        ],
        "relations": [
            {"src": "一等航空兵", "dst": "士兵", "relation": "是", "confidence": 0.8},
            {"src": "剪贴簿", "dst": "飞行报告", "relation": "收录", "confidence": 0.8},
            {"src": "飞行员", "dst": "飞行", "relation": "执行", "confidence": 0.8},
        ],
    },
    "ee81ff297718bc7e": {
        "entities": [
            {"name": "服务", "type": "概念", "aliases": ["my services"]},
            {"name": "电话", "type": "物品", "aliases": ["the phone", "phone"]},
            {"name": "外界", "type": "概念", "aliases": ["the outside world"]},
            {"name": "孩子", "type": "角色", "aliases": ["a poor, helpless child", "child"]},
            {"name": "母亲", "type": "角色", "aliases": ["your mother", "mother"]},
            {"name": "路边", "type": "地点", "aliases": ["the roadside"]},
        ],
        "relations": [
            {"src": "孩子", "dst": "路边", "relation": "流落于", "confidence": 0.8},
            {"src": "母亲", "dst": "孩子", "relation": "叮嘱", "confidence": 0.7},
        ],
    },
    "ddc037afe54980d5": {
        "entities": [
            {"name": "狼", "type": "角色", "aliases": ["a wolf"]},
            {"name": "目标", "type": "角色", "aliases": ["the targets"]},
            {"name": "任务", "type": "概念", "aliases": ["your missions", "missions"]},
        ],
        "relations": [
            {"src": "目标", "dst": "任务", "relation": "隶属", "confidence": 0.8},
        ],
    },
    "62baf9ed5517e83f": {
        "entities": [
            {"name": "司机", "type": "角色", "aliases": ["My driver"]},
            {"name": "车顶", "type": "物品", "aliases": ["the car roof"]},
            {"name": "刮擦声", "type": "现象", "aliases": ["scraping sound"]},
            {"name": "命运", "type": "概念", "aliases": ["Destiny's", "Destiny"]},
            {"name": "出差", "type": "事件", "aliases": ["a business trip"]},
            {"name": "眼睛", "type": "物品", "aliases": ["your eyes", "eyes"]},
        ],
        "relations": [
            {"src": "司机", "dst": "刮擦声", "relation": "受惊于", "confidence": 0.8},
        ],
    },
    "b3200b9ce4beceb2": {
        "entities": [
            {"name": "羊头阿尔卡纳术师", "type": "角色", "aliases": ["a sheep-headed Arcanist", "sheep-headed Arcanist", "an Arcanist with the head of a Sheep"]},
            {"name": "阿尔卡纳术师", "type": "角色", "aliases": ["Arcanist", "this Arcanist"]},
            {"name": "羊", "type": "角色", "aliases": ["a Sheep", "Sheep"]},
        ],
        "relations": [
            {"src": "羊头阿尔卡纳术师", "dst": "阿尔卡纳术师", "relation": "是", "confidence": 0.9},
            {"src": "羊头阿尔卡纳术师", "dst": "羊", "relation": "头部为", "confidence": 0.85},
        ],
    },
    "6c98660a04e13176": {
        "entities": [
            {"name": "蹄印", "type": "物品", "aliases": ["the hoof prints", "hoof prints"]},
            {"name": "瘦高孩子", "type": "角色", "aliases": ["a slenderkid", "a slender kid"]},
            {"name": "维登小姐", "type": "角色", "aliases": ["Miss Verden"]},
            {"name": "小东西", "type": "物品", "aliases": ["this little thing"]},
        ],
        "relations": [
            {"src": "蹄印", "dst": "瘦高孩子", "relation": "属于", "confidence": 0.8},
        ],
    },
    # ===== batch_midhigh_09 =====
    "a6e0052e9872f0c0": {
        "entities": [
            {"name": "火腿三明治", "type": "物品", "aliases": ["ham sandwiches"]},
            {"name": "枪声", "type": "事件", "aliases": ["the shot"]},
            {"name": "门铃", "type": "物品", "aliases": ["my doorbell", "doorbell"]},
            {"name": "朋友", "type": "角色", "aliases": ["my friend"]},
            {"name": "镇上", "type": "地点", "aliases": ["town"]},
            {"name": "赏金", "type": "概念", "aliases": ["a bounty", "bounty"]},
        ],
        "relations": [
            {"src": "朋友", "dst": "镇上", "relation": "来自", "confidence": 0.8},
        ],
    },
    "48cc98d0a734548b": {
        "entities": [
            {"name": "野外任务撤离指示", "type": "物品", "aliases": ["Field Mission Evacuation Instructions"]},
            {"name": "第21条", "type": "概念", "aliases": ["Article 21"]},
            {"name": "紧急情况", "type": "事件", "aliases": ["an emergency", "emergency"]},
            {"name": "野外军官", "type": "角色", "aliases": ["the fieldofficer", "field officer"]},
            {"name": "SOS密码", "type": "概念", "aliases": ["SOS code"]},
            {"name": "魔杖", "type": "物品", "aliases": ["their wands", "wands"]},
            {"name": "传输装置", "type": "物品", "aliases": ["transmission device"]},
            {"name": "圆形按钮", "type": "物品", "aliases": ["round buttons"]},
            {"name": "基金会", "type": "组织", "aliases": ["Foundation"]},
            {"name": "旋钮", "type": "物品", "aliases": ["the knob", "knob"]},
        ],
        "relations": [
            {"src": "野外任务撤离指示", "dst": "第21条", "relation": "包含", "confidence": 0.9},
            {"src": "野外军官", "dst": "SOS密码", "relation": "发送", "confidence": 0.85},
            {"src": "野外军官", "dst": "魔杖", "relation": "使用", "confidence": 0.8},
            {"src": "野外任务撤离指示", "dst": "基金会", "relation": "指示", "confidence": 0.8},
            {"src": "传输装置", "dst": "圆形按钮", "relation": "配备", "confidence": 0.8},
        ],
    },
    "00779e6b356e13ea": {
        "entities": [
            {"name": "地质学家", "type": "角色", "aliases": ["geologist"]},
            {"name": "土壤", "type": "概念", "aliases": ["soils"]},
            {"name": "泛滥平原", "type": "地点", "aliases": ["flood plains"]},
            {"name": "山脉", "type": "地点", "aliases": ["mountains"]},
            {"name": "沉积岩", "type": "物品", "aliases": ["sedimentary rock"]},
            {"name": "雨", "type": "现象", "aliases": ["The rain", "rain"]},
        ],
        "relations": [
            {"src": "地质学家", "dst": "土壤", "relation": "辨析", "confidence": 0.8},
            {"src": "土壤", "dst": "泛滥平原", "relation": "存于", "confidence": 0.8},
            {"src": "土壤", "dst": "山脉", "relation": "存于", "confidence": 0.8},
        ],
    },
    "97e541ba8dfb145a": {
        "entities": [
            {"name": "凳子", "type": "物品", "aliases": ["a stool"]},
            {"name": "表格", "type": "物品", "aliases": ["the form", "form"]},
            {"name": "阿尔卡努斯集会登记表", "type": "物品", "aliases": ["Arcanus Gathering Registration Form"]},
            {"name": "大型活动申请表", "type": "物品", "aliases": ["Mass Events Application Form"]},
            {"name": "沙漠地区集会申请表", "type": "物品", "aliases": ["Desert AreasGathering Application Form"]},
            {"name": "申请", "type": "概念", "aliases": ["Your application"]},
            {"name": "审批流程", "type": "概念", "aliases": ["approval process"]},
        ],
        "relations": [
            {"src": "阿尔卡努斯集会登记表", "dst": "表格", "relation": "属于", "confidence": 0.9},
            {"src": "大型活动申请表", "dst": "表格", "relation": "属于", "confidence": 0.9},
            {"src": "沙漠地区集会申请表", "dst": "表格", "relation": "属于", "confidence": 0.9},
            {"src": "申请", "dst": "审批流程", "relation": "进入", "confidence": 0.8},
        ],
    },
    "0fb5d3cd3146badb": {
        "entities": [
            {"name": "阿尔卡纳术师", "type": "角色", "aliases": ["Arcanist"]},
            {"name": "骑墙者", "type": "角色", "aliases": ["fence-sitter"]},
        ],
        "relations": [
            {"src": "骑墙者", "dst": "阿尔卡纳术师", "relation": "投靠", "confidence": 0.85},
        ],
    },
    "60701ebe11b4382a": {
        "entities": [
            {"name": "顾客", "type": "角色", "aliases": ["our customers", "customers"]},
            {"name": "硬币", "type": "物品", "aliases": ["coin"]},
            {"name": "主人", "type": "角色", "aliases": ["our host", "host"]},
            {"name": "新客人", "type": "角色", "aliases": ["new guests"]},
            {"name": "报酬", "type": "概念", "aliases": ["reward"]},
            {"name": "钱", "type": "概念", "aliases": ["your money", "money"]},
            {"name": "预算", "type": "概念", "aliases": ["my budget", "budget"]},
            {"name": "生意", "type": "概念", "aliases": ["business"]},
        ],
        "relations": [
            {"src": "顾客", "dst": "生意", "relation": "带来", "confidence": 0.8},
            {"src": "主人", "dst": "新客人", "relation": "接待", "confidence": 0.8},
            {"src": "主人", "dst": "报酬", "relation": "提供", "confidence": 0.8},
        ],
    },
    "46d63d0f9d25c6bf": {
        "entities": [
            {"name": "表演", "type": "事件", "aliases": ["the show"]},
            {"name": "戈耳工洋流", "type": "地点", "aliases": ["the Gorgon Current", "Gorgon Current"]},
            {"name": "地中海血统", "type": "概念", "aliases": ["Mediterranean roots"]},
            {"name": "头骨", "type": "物品", "aliases": ["your skull", "skull"]},
        ],
        "relations": [],
    },
    "2362b02f18448fb4": {
        "entities": [
            {"name": "老头", "type": "角色", "aliases": ["The old man"]},
            {"name": "吉奥", "type": "角色", "aliases": ["Gio"]},
            {"name": "老板", "type": "角色", "aliases": ["your boss", "boss"]},
            {"name": "刀", "type": "物品", "aliases": ["my own knife", "knife"]},
            {"name": "女人", "type": "角色", "aliases": ["a woman"]},
        ],
        "relations": [
            {"src": "吉奥", "dst": "刀", "relation": "归还", "confidence": 0.85},
        ],
    },
    "ee4e73af8f8eb6bc": {
        "entities": [
            {"name": "基金会", "type": "组织", "aliases": ["the Foundation"]},
            {"name": "波琳娜", "type": "角色", "aliases": ["Polina"]},
            {"name": "文书", "type": "物品", "aliases": ["the proper paperwork", "paperwork"]},
            {"name": "特别调查员", "type": "角色", "aliases": ["special investigator"]},
            {"name": "假人", "type": "角色", "aliases": ["mannequin"]},
        ],
        "relations": [
            {"src": "文书", "dst": "波琳娜", "relation": "证明", "confidence": 0.8},
        ],
    },
    "27d07d03d1841bd3": {
        "entities": [
            {"name": "墨丘莉小姐", "type": "角色", "aliases": ["Miss Mercuria"]},
            {"name": "吉奥", "type": "角色", "aliases": ["Gio", "Geo"]},
            {"name": "访客", "type": "角色", "aliases": ["a visitor", "visitor"]},
            {"name": "杰伊", "type": "角色", "aliases": ["Jay"]},
            {"name": "怪人调查员", "type": "角色", "aliases": ["weirdo investigator"]},
            {"name": "帐篷", "type": "地点", "aliases": ["this tent"]},
        ],
        "relations": [
            {"src": "墨丘莉小姐", "dst": "吉奥", "relation": "认识", "confidence": 0.8},
            {"src": "吉奥", "dst": "访客", "relation": "是", "confidence": 0.8},
            {"src": "怪人调查员", "dst": "帐篷", "relation": "探头进入", "confidence": 0.8},
            {"src": "杰伊", "dst": "访客", "relation": "目击", "confidence": 0.7},
        ],
    },
    "c25981809cbb4d55": {
        "entities": [
            {"name": "奇星", "type": "角色", "aliases": ["奇星"]},
            {"name": "斯考特", "type": "角色", "aliases": ["“斯考特”"]},
            {"name": "职员", "type": "角色", "aliases": ["职员"]},
            {"name": "梁月", "type": "角色", "aliases": ["梁月"]},
            {"name": "执棋人", "type": "角色", "aliases": ["执棋人"]},
        ],
        "relations": [
            {"src": "奇星", "dst": "斯考特", "relation": "意图杀害", "confidence": 0.85},
            {"src": "斯考特", "dst": "职员", "relation": "是", "confidence": 0.9},
            {"src": "梁月", "dst": "执棋人", "relation": "是", "confidence": 0.9},
        ],
    },
    "0678eb71edadd4a7": {
        "entities": [],
        "relations": [],
    },
    "8a0f82ece84b25d2": {
        "entities": [],
        "relations": [],
    },
    "1f6c6b1e6aa16b66": {
        "entities": [
            {"name": "桑托斯", "type": "角色", "aliases": ["桑托斯"]},
            {"name": "芝诺士兵", "type": "角色", "aliases": ["芝诺士兵"]},
            {"name": "传道者", "type": "角色", "aliases": ["传道者"]},
            {"name": "将军", "type": "角色", "aliases": ["将军"]},
            {"name": "基金会", "type": "组织", "aliases": ["基金会"]},
            {"name": "老弱舰队", "type": "组织", "aliases": ["老弱舰队"]},
            {"name": "使命", "type": "概念", "aliases": ["使命"]},
        ],
        "relations": [
            {"src": "桑托斯", "dst": "传道者", "relation": "效忠", "confidence": 0.85},
            {"src": "桑托斯", "dst": "使命", "relation": "完成", "confidence": 0.8},
            {"src": "桑托斯", "dst": "将军", "relation": "传话于", "confidence": 0.8},
            {"src": "老弱舰队", "dst": "基金会", "relation": "隶属", "confidence": 0.9},
            {"src": "芝诺士兵", "dst": "桑托斯", "relation": "遵从", "confidence": 0.7},
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
    print(f"[apply-missing-p38] 写入 {len(RESULTS)} 条")
    return 0


if __name__ == "__main__":
    sys.exit(main())
