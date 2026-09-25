# -*- coding: utf-8 -*-
"""未抽取剧情块补抽 · 第 18 批（backfill2 batch_08，20 块，含 1 个重复 hash）。

用法：
  python scripts/apply_missing_p18.py            # 预演（悬空+落地自检）
  python scripts/apply_missing_p18.py --apply    # 写盘
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "knowledge" / "plot_cache" / "wu_ming_zhe"
NOOP_FILE = ROOT / "data" / "knowledge" / "_audit" / "noop_confirmed.json"
CORPUS = ROOT / "data" / "knowledge" / "plot_corpus_wu_ming_zhe.json"

# 本批 1 块为角色技能/数值页（无剧情）：7060aea3621d9d0f（正文重复出现 2 次）。
NOOP_ADD: list[str] = [
    "7060aea3621d9d0f",
]

RESULTS: dict[str, dict] = {
    # 1) 收监记录对话 · 阴谋与重塑之手随行人员
    "f8354660deb90aa7": {
        "entities": [
            {"name": "重塑之手", "type": "组织", "aliases": []},
            {"name": "天使兄弟会", "type": "组织", "aliases": []},
            {"name": "金伯利女郎", "type": "角色", "aliases": []},
            {"name": "洛佩拉少尉", "type": "角色", "aliases": ["洛佩拉"]},
            {"name": "卡洛斯将军", "type": "角色", "aliases": ["卡洛斯"]},
            {"name": "伊戈尔将军", "type": "角色", "aliases": ["伊戈尔"]},
            {"name": "红腹锯脂鲤", "type": "概念", "aliases": ["食人鱼"]},
        ],
        "relations": [
            {"src": "金伯利女郎", "dst": "重塑之手", "relation": "跟随", "confidence": 0.8},
            {"src": "洛佩拉少尉", "dst": "金伯利女郎", "relation": "抓捕", "confidence": 0.8},
            {"src": "金伯利女郎", "dst": "天使兄弟会", "relation": "出现于", "confidence": 0.7},
            {"src": "金伯利女郎", "dst": "卡洛斯将军", "relation": "无关", "confidence": 0.7},
            {"src": "伊戈尔将军", "dst": "金伯利女郎", "relation": "发落", "confidence": 0.7},
        ],
    },
    # 2) 乔治橡树童谣 · 禁闭室设计与教员食堂
    "4602fb68bb3260a0": {
        "entities": [
            {"name": "乔治橡树", "type": "概念", "aliases": []},
            {"name": "禁闭室", "type": "地点", "aliases": []},
            {"name": "魔精", "type": "概念", "aliases": []},
            {"name": "教员食堂", "type": "地点", "aliases": []},
            {"name": "炸鱼薯条", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "禁闭室", "dst": "魔精", "relation": "布置", "confidence": 0.7},
            {"src": "教员食堂", "dst": "炸鱼薯条", "relation": "提供", "confidence": 0.7},
        ],
    },
    # 3) 极简主义独白 · 绿意守卫与被遗落的赠礼
    "3bd33c0c6d4786ba": {
        "entities": [
            {"name": "极简主义", "type": "概念", "aliases": []},
            {"name": "巨人观", "type": "概念", "aliases": []},
            {"name": "绿意守卫", "type": "角色", "aliases": []},
            {"name": "被遗落的赠礼", "type": "物品", "aliases": []},
            {"name": "灵缇幼犬", "type": "角色", "aliases": []},
            {"name": "青蛙玩偶", "type": "物品", "aliases": []},
            {"name": "水晶", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "被遗落的赠礼", "dst": "水晶", "relation": "包含", "confidence": 0.7},
        ],
    },
    # 4) 巷尾传言 · 杰瑞·威尔逊被关与破壳之卵
    "ab472dba2e44a8fb": {
        "entities": [
            {"name": "杰瑞·威尔逊", "type": "角色", "aliases": ["杰瑞"]},
            {"name": "哈利", "type": "角色", "aliases": []},
            {"name": "破壳之卵", "type": "概念", "aliases": []},
            {"name": "泽西恶魔", "type": "角色", "aliases": []},
            {"name": "基金会", "type": "组织", "aliases": []},
            {"name": "大野狼", "type": "概念", "aliases": []},
            {"name": "逃跑路线规划", "type": "物品", "aliases": []},
            {"name": "一张合影", "type": "物品", "aliases": []},
            {"name": "怪建筑", "type": "地点", "aliases": []},
            {"name": "恐惧", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "杰瑞·威尔逊", "dst": "怪建筑", "relation": "被关押于", "confidence": 0.8},
            {"src": "哈利", "dst": "杰瑞·威尔逊", "relation": "目击", "confidence": 0.7},
            {"src": "破壳之卵", "dst": "泽西恶魔", "relation": "诞生于", "confidence": 0.8},
            {"src": "破壳之卵", "dst": "恐惧", "relation": "伴随", "confidence": 0.7},
            {"src": "基金会", "dst": "破壳之卵", "relation": "借喻警示", "confidence": 0.7},
            {"src": "破壳之卵", "dst": "大野狼", "relation": "类似", "confidence": 0.7},
        ],
    },
    # 5) 非对称核素R对照实验 · 暴雨性状与海水对话
    "4c9f122ebcfacdf4": {
        "entities": [
            {"name": "非对称核素R", "type": "概念", "aliases": []},
            {"name": "暴雨", "type": "现象", "aliases": ['"暴雨"']},
            {"name": "实验小鼠", "type": "角色", "aliases": []},
            {"name": "雨滴", "type": "物品", "aliases": []},
            {"name": "海水", "type": "物品", "aliases": []},
            {"name": "浮夸的表", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "非对称核素R", "dst": "暴雨", "relation": "决定性状", "confidence": 0.9},
            {"src": "非对称核素R", "dst": "雨滴", "relation": "存在于", "confidence": 0.7},
            {"src": "雨滴", "dst": "实验小鼠", "relation": "接触", "confidence": 0.8},
            {"src": "非对称核素R", "dst": "实验小鼠", "relation": "造成损伤", "confidence": 0.8},
        ],
    },
    # 6/13) 水怪技能/数值页（无剧情） → NOOP
    "7060aea3621d9d0f": {
        "entities": [],
        "relations": [],
    },
    # 7) 重塑之手意图摧毁人类 · 监狱改造笔记与科马拉议会
    "4bc392ecd2d568ce": {
        "entities": [
            {"name": "重塑之手", "type": "组织", "aliases": []},
            {"name": "瞭望塔", "type": "地点", "aliases": []},
            {"name": "监狱改造笔记", "type": "物品", "aliases": []},
            {"name": "科马拉议会", "type": "组织", "aliases": []},
            {"name": "A1675诗集", "type": "物品", "aliases": []},
            {"name": "L6759文选", "type": "物品", "aliases": []},
            {"name": "绷带", "type": "物品", "aliases": []},
            {"name": "镜子碎片", "type": "物品", "aliases": []},
            {"name": "囚室", "type": "地点", "aliases": []},
            {"name": "人类", "type": "概念", "aliases": []},
            {"name": "地西泮", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "重塑之手", "dst": "人类", "relation": "意图摧毁", "confidence": 0.9},
            {"src": "监狱改造笔记", "dst": "科马拉议会", "relation": "提及", "confidence": 0.7},
            {"src": "科马拉议会", "dst": "地西泮", "relation": "取消", "confidence": 0.7},
            {"src": "监狱改造笔记", "dst": "绷带", "relation": "记录", "confidence": 0.7},
        ],
    },
    # 8) 伊甸苹果与莱昂纳多 · 舞台之外实验与斑驳的故事
    "6aee1f8a75cea8be": {
        "entities": [
            {"name": "伊甸苹果", "type": "物品", "aliases": []},
            {"name": "莱昂纳多", "type": "角色", "aliases": []},
            {"name": "米兰", "type": "地点", "aliases": []},
            {"name": "尼可罗·马基亚维利", "type": "角色", "aliases": []},
            {"name": "小春雀儿", "type": "角色", "aliases": []},
            {"name": "X", "type": "角色", "aliases": []},
            {"name": "APPLe先生", "type": "角色", "aliases": ["4号观测者"]},
            {"name": "观测者", "type": "角色", "aliases": []},
            {"name": "乌切洛", "type": "角色", "aliases": []},
            {"name": "父亲", "type": "角色", "aliases": []},
            {"name": "壁画", "type": "物品", "aliases": []},
            {"name": "舞台之外", "type": "概念", "aliases": []},
            {"name": "斑驳的故事", "type": "概念", "aliases": []},
            {"name": "名画", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "莱昂纳多", "dst": "米兰", "relation": "居住于", "confidence": 0.7},
            {"src": "尼可罗·马基亚维利", "dst": "莱昂纳多", "relation": "提及", "confidence": 0.7},
            {"src": "X", "dst": "小春雀儿", "relation": "对话", "confidence": 0.7},
            {"src": "X", "dst": "观测者", "relation": "提及", "confidence": 0.7},
            {"src": "APPLe先生", "dst": "观测者", "relation": "是", "confidence": 0.8},
            {"src": "乌切洛", "dst": "壁画", "relation": "创作", "confidence": 0.8},
            {"src": "斑驳的故事", "dst": "名画", "relation": "记录", "confidence": 0.7},
        ],
    },
    # 9) 神秘学家隐喻独白 · 红鼻子坏蛋与电视机
    "c5fc0c7844df77c8": {
        "entities": [
            {"name": "神秘学家", "type": "概念", "aliases": []},
            {"name": "神秘学物种", "type": "概念", "aliases": []},
            {"name": "神秘学", "type": "概念", "aliases": []},
            {"name": "红鼻子的坏蛋", "type": "角色", "aliases": []},
            {"name": "电视机", "type": "物品", "aliases": []},
            {"name": "麦克风", "type": "物品", "aliases": []},
            {"name": "王座", "type": "物品", "aliases": []},
            {"name": "白袍子", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "神秘学家", "dst": "神秘学物种", "relation": "属于", "confidence": 0.8},
            {"src": "神秘学物种", "dst": "神秘学", "relation": "归于", "confidence": 0.8},
            {"src": "红鼻子的坏蛋", "dst": "电视机", "relation": "出现于", "confidence": 0.7},
        ],
    },
    # 10) 基金会立法辩论 · 聚光灯之外提及暴雨与神秘学家
    "8bb0b237d9e7884d": {
        "entities": [
            {"name": "基金会联合委员会", "type": "组织", "aliases": []},
            {"name": "最高裁判所", "type": "组织", "aliases": []},
            {"name": "会议主席", "type": "角色", "aliases": []},
            {"name": "议案", "type": "物品", "aliases": []},
            {"name": "法案", "type": "物品", "aliases": []},
            {"name": "聚光灯之外", "type": "概念", "aliases": []},
            {"name": "暴雨", "type": "现象", "aliases": ['"暴雨"']},
            {"name": "神秘学家", "type": "概念", "aliases": []},
            {"name": "舞台灯", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "会议主席", "dst": "基金会联合委员会", "relation": "受理请求", "confidence": 0.7},
            {"src": "最高裁判所", "dst": "法案", "relation": "裁定", "confidence": 0.8},
            {"src": "聚光灯之外", "dst": "暴雨", "relation": "提及", "confidence": 0.7},
            {"src": "聚光灯之外", "dst": "神秘学家", "relation": "提及", "confidence": 0.7},
        ],
    },
    # 11) 列别杰夫手记 · 诺拉与双生舞伶、门捷列夫综合体
    "71a15a492c118955": {
        "entities": [
            {"name": "列别杰夫", "type": "角色", "aliases": []},
            {"name": "自动化武器制造厂", "type": "地点", "aliases": []},
            {"name": "门捷列夫综合体", "type": "组织", "aliases": []},
            {"name": "维修小站", "type": "地点", "aliases": []},
            {"name": "诺拉", "type": "角色", "aliases": []},
            {"name": "科学家", "type": "角色", "aliases": []},
            {"name": "双生舞伶", "type": "角色", "aliases": []},
            {"name": "D·谢切诺夫", "type": "角色", "aliases": []},
            {"name": "春天", "type": "概念", "aliases": []},
            {"name": "至上主义", "type": "概念", "aliases": []},
            {"name": "胡桃夹子", "type": "物品", "aliases": ["《胡桃夹子》"]},
            {"name": "有始无终的信", "type": "物品", "aliases": []},
            {"name": "人工智能", "type": "概念", "aliases": []},
            {"name": "岛", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "列别杰夫", "dst": "自动化武器制造厂", "relation": "建造", "confidence": 0.7},
            {"src": "自动化武器制造厂", "dst": "门捷列夫综合体", "relation": "属于", "confidence": 0.8},
            {"src": "列别杰夫", "dst": "维修小站", "relation": "维护", "confidence": 0.7},
            {"src": "诺拉", "dst": "人工智能", "relation": "是", "confidence": 0.9},
            {"src": "诺拉", "dst": "科学家", "relation": "令兴奋", "confidence": 0.7},
            {"src": "双生舞伶", "dst": "人工智能", "relation": "是", "confidence": 0.9},
            {"src": "双生舞伶", "dst": "春天", "relation": "识别为", "confidence": 0.7},
            {"src": "双生舞伶", "dst": "至上主义", "relation": "识别为", "confidence": 0.7},
            {"src": "双生舞伶", "dst": "胡桃夹子", "relation": "播放", "confidence": 0.7},
            {"src": "D·谢切诺夫", "dst": "有始无终的信", "relation": "撰写", "confidence": 0.8},
        ],
    },
    # 12) 玛尔纱致玛丽安娜 · Ⅻ小队与骑士团
    "77189ba12f7032af": {
        "entities": [
            {"name": "玛尔纱", "type": "角色", "aliases": []},
            {"name": "玛丽安娜", "type": "角色", "aliases": ["玛丽"]},
            {"name": "Ⅻ小队", "type": "组织", "aliases": ['“Ⅻ”小队']},
            {"name": "刻雷乌斯", "type": "角色", "aliases": ["刻雷乌斯先生"]},
            {"name": "骑士团", "type": "组织", "aliases": []},
            {"name": "基金会", "type": "组织", "aliases": []},
            {"name": "东线", "type": "地点", "aliases": []},
            {"name": "医生", "type": "角色", "aliases": []},
            {"name": "毒气", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "玛尔纱", "dst": "玛丽安娜", "relation": "致信", "confidence": 0.9},
            {"src": "玛尔纱", "dst": "Ⅻ小队", "relation": "加入", "confidence": 0.8},
            {"src": "刻雷乌斯", "dst": "玛尔纱", "relation": "邀请", "confidence": 0.8},
            {"src": "玛尔纱", "dst": "骑士团", "relation": "寻找", "confidence": 0.7},
            {"src": "骑士团", "dst": "基金会", "relation": "意向加入", "confidence": 0.7},
            {"src": "玛尔纱", "dst": "东线", "relation": "前往", "confidence": 0.7},
            {"src": "玛丽安娜", "dst": "毒气", "relation": "作战于", "confidence": 0.7},
            {"src": "医生", "dst": "玛丽安娜", "relation": "检查", "confidence": 0.7},
        ],
    },
    # 14) 巴黎水晶生意与《神秘学家观察》评选
    "da997c4291df1972": {
        "entities": [
            {"name": "巴黎", "type": "地点", "aliases": []},
            {"name": "水晶", "type": "物品", "aliases": []},
            {"name": "预言", "type": "概念", "aliases": []},
            {"name": "神秘学家观察", "type": "物品", "aliases": ["《神秘学家观察》"]},
            {"name": "神秘术", "type": "概念", "aliases": []},
            {"name": "神秘学家", "type": "概念", "aliases": []},
            {"name": "沙龙", "type": "组织", "aliases": []},
            {"name": "人类", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "巴黎", "dst": "神秘学家", "relation": "吸引定居", "confidence": 0.8},
            {"src": "神秘学家观察", "dst": "巴黎", "relation": "评选", "confidence": 0.7},
            {"src": "神秘学家", "dst": "神秘术", "relation": "施展", "confidence": 0.8},
            {"src": "沙龙", "dst": "神秘学家", "relation": "接待", "confidence": 0.7},
            {"src": "预言", "dst": "水晶", "relation": "更受欢迎", "confidence": 0.7},
        ],
    },
    # 15) 利益前线 · 索姆与伊万、骑兵军、重塑之手疑云
    "9b002548f06b639e": {
        "entities": [
            {"name": "红弩箭中尉", "type": "角色", "aliases": ["红弩箭"]},
            {"name": "芝诺", "type": "组织", "aliases": []},
            {"name": "伊戈尔", "type": "角色", "aliases": []},
            {"name": "利益前线", "type": "概念", "aliases": []},
            {"name": "基金会", "type": "组织", "aliases": []},
            {"name": "伊里内伊", "type": "角色", "aliases": []},
            {"name": "索姆", "type": "角色", "aliases": []},
            {"name": "伊万", "type": "角色", "aliases": ["伊万军长"]},
            {"name": "骑兵军", "type": "组织", "aliases": []},
            {"name": "匪军", "type": "组织", "aliases": []},
            {"name": "重塑之手", "type": "组织", "aliases": []},
            {"name": "顿河地区", "type": "地点", "aliases": []},
            {"name": "前将军", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "红弩箭中尉", "dst": "芝诺", "relation": "隶属", "confidence": 0.8},
            {"src": "伊里内伊", "dst": "基金会", "relation": "任职于", "confidence": 0.8},
            {"src": "索姆", "dst": "伊万", "relation": "联络", "confidence": 0.7},
            {"src": "索姆", "dst": "伊万", "relation": "调查", "confidence": 0.7},
            {"src": "骑兵军", "dst": "匪军", "relation": "遭袭扰", "confidence": 0.8},
            {"src": "匪军", "dst": "重塑之手", "relation": "疑似关联", "confidence": 0.7},
            {"src": "索姆", "dst": "骑兵军", "relation": "援助", "confidence": 0.7},
            {"src": "伊万", "dst": "前将军", "relation": "受信赖于", "confidence": 0.7},
            {"src": "顿河地区", "dst": "基金会", "relation": "战略关联", "confidence": 0.7},
        ],
    },
    # 16) 张之之来信 · 第一防线学校借阅卡与招潮蟹变形术
    "d0a5e8f21bc1ffa8": {
        "entities": [
            {"name": "芝诺", "type": "组织", "aliases": []},
            {"name": "伊万", "type": "角色", "aliases": ["伊万军长"]},
            {"name": "索姆", "type": "角色", "aliases": ["索姆将军"]},
            {"name": "伊戈尔", "type": "角色", "aliases": []},
            {"name": "张之之", "type": "角色", "aliases": []},
            {"name": "姜茶", "type": "物品", "aliases": []},
            {"name": "顿河", "type": "地点", "aliases": []},
            {"name": "第一防线学校", "type": "组织", "aliases": []},
            {"name": "笨蛋也能学会的招潮蟹变形术", "type": "物品", "aliases": ["《笨蛋也能学会的招潮蟹变形术》"]},
            {"name": "十四行诗", "type": "角色", "aliases": []},
            {"name": "汉斯·李维斯", "type": "角色", "aliases": []},
            {"name": "西里尔·阿曼", "type": "角色", "aliases": []},
            {"name": "拉克·冯·斯图尔", "type": "角色", "aliases": []},
            {"name": "梅蕾尔", "type": "角色", "aliases": []},
            {"name": "图书管理员", "type": "角色", "aliases": []},
            {"name": "佳琳娜夫人", "type": "角色", "aliases": []},
            {"name": "战时菜谱", "type": "物品", "aliases": []},
            {"name": "海洋魔精", "type": "概念", "aliases": []},
            {"name": "招潮蟹", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "索姆", "dst": "伊万", "relation": "评价", "confidence": 0.8},
            {"src": "伊万", "dst": "伊戈尔", "relation": "有情谊", "confidence": 0.7},
            {"src": "张之之", "dst": "索姆", "relation": "提及", "confidence": 0.7},
            {"src": "张之之", "dst": "姜茶", "relation": "附带", "confidence": 0.7},
            {"src": "第一防线学校", "dst": "笨蛋也能学会的招潮蟹变形术", "relation": "馆藏", "confidence": 0.9},
            {"src": "十四行诗", "dst": "笨蛋也能学会的招潮蟹变形术", "relation": "借阅", "confidence": 0.8},
            {"src": "汉斯·李维斯", "dst": "笨蛋也能学会的招潮蟹变形术", "relation": "借阅", "confidence": 0.8},
            {"src": "西里尔·阿曼", "dst": "笨蛋也能学会的招潮蟹变形术", "relation": "借阅", "confidence": 0.8},
            {"src": "拉克·冯·斯图尔", "dst": "笨蛋也能学会的招潮蟹变形术", "relation": "借阅", "confidence": 0.8},
            {"src": "梅蕾尔", "dst": "笨蛋也能学会的招潮蟹变形术", "relation": "借阅", "confidence": 0.8},
            {"src": "图书管理员", "dst": "笨蛋也能学会的招潮蟹变形术", "relation": "批注", "confidence": 0.7},
            {"src": "佳琳娜夫人", "dst": "战时菜谱", "relation": "拥有", "confidence": 0.8},
            {"src": "笨蛋也能学会的招潮蟹变形术", "dst": "招潮蟹", "relation": "涉及", "confidence": 0.8},
            {"src": "笨蛋也能学会的招潮蟹变形术", "dst": "海洋魔精", "relation": "属类", "confidence": 0.7},
        ],
    },
    # 17) 女巫与卡戎 · 斯捷尔诺娃上校冰蹄铁行动作战指令
    "275f1326d6da5344": {
        "entities": [
            {"name": "卡戎", "type": "角色", "aliases": []},
            {"name": "女巫", "type": "角色", "aliases": []},
            {"name": "包亚雷什金", "type": "角色", "aliases": []},
            {"name": "阿尔乔姆", "type": "角色", "aliases": []},
            {"name": "麦列霍夫", "type": "角色", "aliases": []},
            {"name": "芝诺", "type": "组织", "aliases": []},
            {"name": "斯捷尔诺娃上校", "type": "角色", "aliases": ["斯捷尔诺娃"]},
            {"name": "冰蹄铁行动", "type": "事件", "aliases": ["冰蹄铁行动-Ω"]},
            {"name": "长矛轻骑兵师", "type": "组织", "aliases": ["“长矛”轻骑兵师"]},
            {"name": "马刀", "type": "组织", "aliases": []},
            {"name": "盾牌", "type": "组织", "aliases": []},
            {"name": "狩马部队", "type": "组织", "aliases": ["“狩马”部队"]},
            {"name": "老市民", "type": "组织", "aliases": []},
            {"name": "暗流", "type": "地点", "aliases": []},
            {"name": "南方小城", "type": "地点", "aliases": []},
            {"name": "黑色蝗虫部队", "type": "组织", "aliases": ["“黑色蝗虫”部队"]},
            {"name": "作战指令简报", "type": "物品", "aliases": []},
            {"name": "死亡", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "女巫", "dst": "卡戎", "relation": "称谢", "confidence": 0.8},
            {"src": "女巫", "dst": "死亡", "relation": "驭使", "confidence": 0.8},
            {"src": "卡戎", "dst": "女巫", "relation": "助益", "confidence": 0.8},
            {"src": "包亚雷什金", "dst": "阿尔乔姆", "relation": "同行", "confidence": 0.7},
            {"src": "包亚雷什金", "dst": "麦列霍夫", "relation": "同行", "confidence": 0.7},
            {"src": "斯捷尔诺娃上校", "dst": "作战指令简报", "relation": "签发", "confidence": 0.8},
            {"src": "作战指令简报", "dst": "冰蹄铁行动", "relation": "关于", "confidence": 0.8},
            {"src": "冰蹄铁行动", "dst": "长矛轻骑兵师", "relation": "命令", "confidence": 0.8},
            {"src": "长矛轻骑兵师", "dst": "马刀", "relation": "协同", "confidence": 0.7},
            {"src": "长矛轻骑兵师", "dst": "盾牌", "relation": "协同", "confidence": 0.7},
            {"src": "长矛轻骑兵师", "dst": "狩马部队", "relation": "配合", "confidence": 0.7},
            {"src": "长矛轻骑兵师", "dst": "老市民", "relation": "配合", "confidence": 0.7},
            {"src": "长矛轻骑兵师", "dst": "暗流", "relation": "沿袭", "confidence": 0.7},
            {"src": "黑色蝗虫部队", "dst": "南方小城", "relation": "进攻", "confidence": 0.8},
            {"src": "黑色蝗虫部队", "dst": "暗流", "relation": "集结于", "confidence": 0.7},
        ],
    },
    # 18) 贝壳切割匠游戏 · 火山岛神庙预言仪式
    "43c9defaffd47a08": {
        "entities": [
            {"name": "贝壳切割匠", "type": "角色", "aliases": []},
            {"name": "贝壳", "type": "物品", "aliases": []},
            {"name": "螺壳", "type": "物品", "aliases": []},
            {"name": "贝壳项链", "type": "物品", "aliases": []},
            {"name": "赫利孔酒吧", "type": "地点", "aliases": []},
            {"name": "火山岛神庙", "type": "地点", "aliases": []},
            {"name": "殿下", "type": "角色", "aliases": []},
            {"name": "预言仪式", "type": "事件", "aliases": []},
            {"name": "神谕", "type": "概念", "aliases": []},
            {"name": "预言者", "type": "角色", "aliases": []},
            {"name": "海鸥", "type": "角色", "aliases": []},
            {"name": "鹰", "type": "角色", "aliases": []},
            {"name": "蛇", "type": "角色", "aliases": []},
            {"name": "鸟", "type": "角色", "aliases": []},
            {"name": "火山岛", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "贝壳切割匠", "dst": "贝壳", "relation": "加工", "confidence": 0.8},
            {"src": "贝壳", "dst": "贝壳项链", "relation": "制成", "confidence": 0.8},
            {"src": "赫利孔酒吧", "dst": "贝壳切割匠", "relation": "举办", "confidence": 0.7},
            {"src": "火山岛神庙", "dst": "预言仪式", "relation": "筹备", "confidence": 0.8},
            {"src": "殿下", "dst": "预言仪式", "relation": "拥有", "confidence": 0.7},
            {"src": "预言者", "dst": "神谕", "relation": "解读", "confidence": 0.8},
            {"src": "火山岛", "dst": "预言仪式", "relation": "关乎", "confidence": 0.8},
            {"src": "海鸥", "dst": "鸟", "relation": "属于", "confidence": 0.7},
        ],
    },
    # 19) 预言者与德利诺 · 洋葱头、司辰、赫多涅殿下与水上运动会
    "cffe0cadbdbcf621": {
        "entities": [
            {"name": "预言者", "type": "角色", "aliases": []},
            {"name": "德利诺", "type": "角色", "aliases": []},
            {"name": "皮诺克", "type": "概念", "aliases": []},
            {"name": "洋葱头", "type": "角色", "aliases": []},
            {"name": "和平乌鲁", "type": "角色", "aliases": ["和平乌鲁女士"]},
            {"name": "司辰", "type": "角色", "aliases": []},
            {"name": "火山岛", "type": "地点", "aliases": []},
            {"name": "水上运动会", "type": "事件", "aliases": []},
            {"name": "箱中", "type": "组织", "aliases": []},
            {"name": "赫多涅殿下", "type": "角色", "aliases": ["赫多涅"]},
            {"name": "领袖", "type": "角色", "aliases": []},
            {"name": "运动精神", "type": "概念", "aliases": []},
            {"name": "公平竞争", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "预言者", "dst": "德利诺", "relation": "较镇定", "confidence": 0.7},
            {"src": "洋葱头", "dst": "和平乌鲁", "relation": "拜访", "confidence": 0.8},
            {"src": "司辰", "dst": "火山岛", "relation": "传回消息", "confidence": 0.8},
            {"src": "火山岛", "dst": "水上运动会", "relation": "举办", "confidence": 0.9},
            {"src": "司辰", "dst": "箱中", "relation": "转播", "confidence": 0.7},
            {"src": "司辰", "dst": "洋葱头", "relation": "牵线搭桥", "confidence": 0.7},
            {"src": "赫多涅殿下", "dst": "火山岛", "relation": "统治", "confidence": 0.9},
            {"src": "赫多涅殿下", "dst": "水上运动会", "relation": "引领", "confidence": 0.8},
            {"src": "赫多涅殿下", "dst": "运动精神", "relation": "喜好", "confidence": 0.7},
            {"src": "洋葱头", "dst": "赫多涅殿下", "relation": "采访", "confidence": 0.7},
            {"src": "洋葱头", "dst": "领袖", "relation": "询问", "confidence": 0.7},
        ],
    },
    # 20) 多瑙黎明号行动 · 血食怪、感染种与圣洛夫基金会
    "942e16d0f1870371": {
        "entities": [
            {"name": "多瑙黎明号", "type": "物品", "aliases": []},
            {"name": "超自然者血食怪", "type": "角色", "aliases": []},
            {"name": "感染种", "type": "概念", "aliases": ["感染种"]},
            {"name": "重塑之手", "type": "组织", "aliases": []},
            {"name": "塞梅尔维斯调查员", "type": "角色", "aliases": ["塞梅尔维斯"]},
            {"name": "下多瑙河七十七小队", "type": "组织", "aliases": []},
            {"name": "圣洛夫基金会", "type": "组织", "aliases": []},
            {"name": "G站", "type": "地点", "aliases": []},
            {"name": "维也纳-潘诺尼亚运输公司", "type": "组织", "aliases": []},
            {"name": "多瑙河", "type": "地点", "aliases": []},
            {"name": "伊斯坦布尔", "type": "地点", "aliases": []},
            {"name": "维也纳", "type": "地点", "aliases": []},
            {"name": "哈布斯堡", "type": "组织", "aliases": []},
            {"name": "凡尔赛宫", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "感染种", "dst": "超自然者血食怪", "relation": "属于", "confidence": 0.8},
            {"src": "重塑之手", "dst": "超自然者血食怪", "relation": "合作", "confidence": 0.7},
            {"src": "塞梅尔维斯调查员", "dst": "多瑙黎明号", "relation": "登乘", "confidence": 0.8},
            {"src": "塞梅尔维斯调查员", "dst": "下多瑙河七十七小队", "relation": "会合", "confidence": 0.8},
            {"src": "圣洛夫基金会", "dst": "塞梅尔维斯调查员", "relation": "派遣", "confidence": 0.8},
            {"src": "维也纳-潘诺尼亚运输公司", "dst": "多瑙黎明号", "relation": "翻修", "confidence": 0.8},
            {"src": "多瑙黎明号", "dst": "多瑙河", "relation": "沿行", "confidence": 0.7},
            {"src": "多瑙黎明号", "dst": "伊斯坦布尔", "relation": "始发", "confidence": 0.7},
            {"src": "多瑙黎明号", "dst": "维也纳", "relation": "终到", "confidence": 0.7},
            {"src": "多瑙黎明号", "dst": "凡尔赛宫", "relation": "比作", "confidence": 0.7},
            {"src": "多瑙黎明号", "dst": "哈布斯堡", "relation": "具派头", "confidence": 0.7},
        ],
    },
}


def _norm(s: str) -> str:
    return re.sub(r"\s+", "", str(s).lower())


def validate() -> int:
    """悬空自检：关系 src/dst 必须落在块内实体 name/aliases 池。"""
    bad = 0
    for h, d in RESULTS.items():
        pool = set()
        for e in d.get("entities") or []:
            pool.add(_norm(e.get("name") or ""))
            pool |= {_norm(a) for a in (e.get("aliases") or [])}
        for r in d.get("relations") or []:
            for k in ("src", "dst"):
                if _norm(r.get(k) or "") not in pool:
                    print(f"[dangling] {h} {k}={r.get(k)}")
                    bad += 1
    return bad


def landing() -> int:
    """落地自检：实体 name/任一 alias 须是语料库正文的子串。"""
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    text_by_hash = {c["hash"]: c["text"] for c in corpus["chunks"]}
    bad = 0
    for h, d in RESULTS.items():
        text = text_by_hash.get(h, "")
        if not text:
            print(f"[landing-missing-corpus] {h}")
            bad += 1
            continue
        ntext = _norm(text)
        for e in d.get("entities") or []:
            name = e.get("name") or ""
            cands = [name] + list(e.get("aliases") or [])
            if not any(_norm(c) in ntext for c in cands):
                print(f"[landing-fail] {h} entity={name} aliases={e.get('aliases')}")
                bad += 1
    return bad


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    n = validate()
    m = landing()
    total_e = sum(len(d.get("entities") or []) for d in RESULTS.values())
    total_r = sum(len(d.get("relations") or []) for d in RESULTS.values())
    nonempty = sum(1 for d in RESULTS.values() if (d.get("entities") or d.get("relations")))
    print(f"[validate] 块 {len(RESULTS)}（含NOOP {sum(1 for d in RESULTS.values() if not (d.get('entities') or d.get('relations')))}），悬空 {n}，未落地 {m}")
    print(f"[stats] 非空块 {nonempty}，实体 {total_e}，关系 {total_r}，"
          f"空块 {sum(1 for d in RESULTS.values() if not (d.get('entities') or d.get('relations')))}")

    if n or m:
        print("[ABORT] 存在悬空或未落地，未写盘")
        return 1

    if not args.apply:
        print("[dry-run] 加 --apply 写盘")
        return 0

    for h, d in RESULTS.items():
        (CACHE / f"{h}.json").write_text(
            json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    if NOOP_ADD:
        noop = set(json.loads(NOOP_FILE.read_text(encoding="utf-8")))
        noop |= set(NOOP_ADD)
        NOOP_FILE.write_text(
            json.dumps(sorted(noop), ensure_ascii=False, indent=1), encoding="utf-8"
        )
    print(f"[apply-missing-p18] 写入 {len(RESULTS)} 条，NOOP +{len(NOOP_ADD)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
