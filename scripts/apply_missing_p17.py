# -*- coding: utf-8 -*-
"""未抽取剧情块补抽 · 第 17 批（backfill2 batch_07，20 块）。

用法：
  python scripts/apply_missing_p17.py            # 预演（悬空+落地自检）
  python scripts/apply_missing_p17.py --apply    # 写盘
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

# 本批 20 块均含剧情，无纯数值/UI/无剧情块，NOOP 集合为空。
NOOP_ADD: list[str] = []

RESULTS: dict[str, dict] = {
    # 1) 姓氏的分量 · 迪塔斯多夫与维也纳
    "a15f2fa6a7c08fe5": {
        "entities": [
            {"name": "迪塔斯多夫", "type": "组织", "aliases": ['"迪塔斯多夫"']},
            {"name": "维也纳", "type": "地点", "aliases": []},
            {"name": "灵性创作", "type": "概念", "aliases": ['"灵性创作"']},
        ],
        "relations": [
            {"src": "迪塔斯多夫", "dst": "维也纳", "relation": "关联", "confidence": 0.7},
            {"src": "迪塔斯多夫", "dst": "灵性创作", "relation": "具备", "confidence": 0.8},
        ],
    },
    # 2) 分离派之家与卡卡尼亚 · 战争阴云下的维也纳
    "ec76d8e5f952291f": {
        "entities": [
            {"name": "分离派之家", "type": "组织", "aliases": []},
            {"name": "卡卡尼亚", "type": "角色", "aliases": []},
            {"name": "垃圾", "type": "物品", "aliases": ['"垃圾"']},
            {"name": "绒盒", "type": "物品", "aliases": []},
            {"name": "牛皮封套", "type": "物品", "aliases": []},
            {"name": "1913年5月26日", "type": "时间", "aliases": []},
            {"name": "帝国", "type": "组织", "aliases": []},
            {"name": "俄国", "type": "地点", "aliases": []},
            {"name": "欧洲", "type": "地点", "aliases": []},
            {"name": "维也纳", "type": "地点", "aliases": []},
            {"name": "歌剧院", "type": "地点", "aliases": []},
            {"name": "萨克斯管", "type": "物品", "aliases": []},
            {"name": "金条", "type": "物品", "aliases": []},
            {"name": "宝石", "type": "物品", "aliases": []},
            {"name": "战争", "type": "事件", "aliases": ['"战争"']},
        ],
        "relations": [
            {"src": "卡卡尼亚", "dst": "分离派之家", "relation": "供职", "confidence": 0.8},
            {"src": "垃圾", "dst": "绒盒", "relation": "失去保护", "confidence": 0.7},
            {"src": "垃圾", "dst": "牛皮封套", "relation": "失去保护", "confidence": 0.7},
            {"src": "俄国", "dst": "帝国", "relation": "潜伏间谍", "confidence": 0.7},
            {"src": "战争", "dst": "维也纳", "relation": "波及", "confidence": 0.8},
            {"src": "战争", "dst": "欧洲", "relation": "笼罩", "confidence": 0.7},
        ],
    },
    # 3) 绿姑娘即小凤头鹦鹉 · 利奥波德区与分离派
    "2a8138ee5c10eed5": {
        "entities": [
            {"name": "绿姑娘", "type": "角色", "aliases": []},
            {"name": "小凤头鹦鹉", "type": "角色", "aliases": []},
            {"name": "心理医师", "type": "角色", "aliases": []},
            {"name": "利奥波德区", "type": "地点", "aliases": []},
            {"name": "欧洲", "type": "地点", "aliases": []},
            {"name": "分离派", "type": "组织", "aliases": []},
            {"name": "咖啡馆", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "绿姑娘", "dst": "小凤头鹦鹉", "relation": "是", "confidence": 0.9},
            {"src": "绿姑娘", "dst": "心理医师", "relation": "自称", "confidence": 0.8},
            {"src": "绿姑娘", "dst": "利奥波德区", "relation": "居住", "confidence": 0.7},
        ],
    },
    # 4) 海因里希与勇士之歌 · 圣洛夫基金会收容伊索尔德与克拉拉
    "f13e01fb488fec44": {
        "entities": [
            {"name": "海因里希", "type": "角色", "aliases": []},
            {"name": "勇士之歌", "type": "物品", "aliases": []},
            {"name": "白信封", "type": "物品", "aliases": []},
            {"name": "匕首", "type": "物品", "aliases": []},
            {"name": "手镜", "type": "物品", "aliases": []},
            {"name": "马库斯", "type": "角色", "aliases": ["马库斯小姐"]},
            {"name": "伊索尔德", "type": "角色", "aliases": ['"伊索尔德"', "伊索尔德·冯·迪塔斯多夫"]},
            {"name": "卡卡尼亚", "type": "角色", "aliases": ['"卡卡尼亚"']},
            {"name": "圣洛夫基金会", "type": "组织", "aliases": []},
            {"name": "暴雨", "type": "现象", "aliases": ['"暴雨"']},
            {"name": "迪塔斯多夫", "type": "组织", "aliases": []},
            {"name": "布拉格", "type": "地点", "aliases": []},
            {"name": "剃刀小队", "type": "组织", "aliases": []},
            {"name": "维也纳", "type": "地点", "aliases": []},
            {"name": "克拉拉·温格勒", "type": "角色", "aliases": []},
            {"name": "地下收容所", "type": "地点", "aliases": []},
            {"name": "收容管理条例（003号文件）", "type": "物品", "aliases": ["《收容管理条例（003号文件）》"]},
            {"name": "维也纳事件", "type": "事件", "aliases": []},
        ],
        "relations": [
            {"src": "马库斯", "dst": "圣洛夫基金会", "relation": "隶属", "confidence": 0.9},
            {"src": "圣洛夫基金会", "dst": "伊索尔德", "relation": "评估", "confidence": 0.8},
            {"src": "圣洛夫基金会", "dst": "卡卡尼亚", "relation": "知悉", "confidence": 0.7},
            {"src": "圣洛夫基金会", "dst": "克拉拉·温格勒", "relation": "评估", "confidence": 0.8},
            {"src": "圣洛夫基金会", "dst": "剃刀小队", "relation": "调动", "confidence": 0.8},
            {"src": "剃刀小队", "dst": "维也纳", "relation": "前往", "confidence": 0.8},
            {"src": "圣洛夫基金会", "dst": "暴雨", "relation": "预警", "confidence": 0.7},
            {"src": "克拉拉·温格勒", "dst": "维也纳事件", "relation": "作为证人", "confidence": 0.8},
            {"src": "白信封", "dst": "匕首", "relation": "涉及", "confidence": 0.7},
            {"src": "白信封", "dst": "手镜", "relation": "涉及", "confidence": 0.7},
            {"src": "伊索尔德", "dst": "迪塔斯多夫", "relation": "属于", "confidence": 0.85},
        ],
    },
    # 5) 刻雷乌斯与示踪剂 · 艺术陈列室藏品遗失
    "db3709ce3a61db58": {
        "entities": [
            {"name": "刻雷乌斯", "type": "角色", "aliases": []},
            {"name": "示踪剂", "type": "物品", "aliases": ['"示踪剂"']},
            {"name": "特别检察官", "type": "角色", "aliases": []},
            {"name": "叶尔莫莱", "type": "角色", "aliases": []},
            {"name": "别列格勒", "type": "地点", "aliases": []},
            {"name": "灌体实验", "type": "概念", "aliases": ['"灌体实验"']},
            {"name": "白色石屋", "type": "地点", "aliases": []},
            {"name": "琥珀屋", "type": "地点", "aliases": []},
            {"name": "暴雨", "type": "现象", "aliases": ['"暴雨"']},
            {"name": "艺术陈列室", "type": "地点", "aliases": []},
            {"name": "移动打字机", "type": "物品", "aliases": []},
            {"name": "迪斯科舞曲录音带", "type": "物品", "aliases": []},
            {"name": "雪墩山湖底剑柄", "type": "物品", "aliases": []},
            {"name": "时代藏品遗失清单", "type": "物品", "aliases": ['"时代藏品遗失清单"']},
            {"name": "艺术陈列室藏品遗失事故复盘纪要", "type": "物品", "aliases": []},
            {"name": "总部", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "特别检察官", "dst": "刻雷乌斯", "relation": "质询", "confidence": 0.8},
            {"src": "叶尔莫莱", "dst": "别列格勒", "relation": "调查", "confidence": 0.8},
            {"src": "叶尔莫莱", "dst": "灌体实验", "relation": "调查", "confidence": 0.8},
            {"src": "叶尔莫莱", "dst": "示踪剂", "relation": "获取", "confidence": 0.8},
            {"src": "刻雷乌斯", "dst": "叶尔莫莱", "relation": "命令", "confidence": 0.8},
            {"src": "刻雷乌斯", "dst": "琥珀屋", "relation": "寻找", "confidence": 0.7},
            {"src": "示踪剂", "dst": "灌体实验", "relation": "产物", "confidence": 0.9},
            {"src": "示踪剂", "dst": "暴雨", "relation": "追踪", "confidence": 0.8},
            {"src": "示踪剂", "dst": "别列格勒", "relation": "发现于", "confidence": 0.8},
            {"src": "刻雷乌斯", "dst": "示踪剂", "relation": "使用", "confidence": 0.8},
            {"src": "刻雷乌斯", "dst": "白色石屋", "relation": "提及", "confidence": 0.7},
            {"src": "艺术陈列室", "dst": "移动打字机", "relation": "遗失", "confidence": 0.8},
            {"src": "艺术陈列室", "dst": "迪斯科舞曲录音带", "relation": "遗失", "confidence": 0.8},
            {"src": "艺术陈列室", "dst": "雪墩山湖底剑柄", "relation": "遗失", "confidence": 0.8},
            {"src": "艺术陈列室藏品遗失事故复盘纪要", "dst": "艺术陈列室", "relation": "记录", "confidence": 0.8},
            {"src": "总部", "dst": "艺术陈列室", "relation": "包含", "confidence": 0.8},
            {"src": "总部", "dst": "时代藏品遗失清单", "relation": "提及", "confidence": 0.7},
        ],
    },
    # 6) 埃琳娜与亚什基 · 无管辖地带的零件
    "222a02a2a63d23ff": {
        "entities": [
            {"name": "埃琳娜", "type": "角色", "aliases": []},
            {"name": "镇子", "type": "地点", "aliases": []},
            {"name": "芝诺", "type": "组织", "aliases": []},
            {"name": "北风", "type": "现象", "aliases": []},
            {"name": "零件", "type": "物品", "aliases": []},
            {"name": "扳手", "type": "物品", "aliases": []},
            {"name": "钳子", "type": "物品", "aliases": []},
            {"name": "矿石", "type": "物品", "aliases": []},
            {"name": "亚什基", "type": "地点", "aliases": []},
            {"name": "无管辖地带", "type": "地点", "aliases": []},
            {"name": "克努特", "type": "角色", "aliases": []},
            {"name": "雕像", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "埃琳娜", "dst": "镇子", "relation": "居住", "confidence": 0.8},
            {"src": "埃琳娜", "dst": "芝诺", "relation": "不习惯", "confidence": 0.7},
            {"src": "埃琳娜", "dst": "亚什基", "relation": "到来", "confidence": 0.8},
            {"src": "埃琳娜", "dst": "零件", "relation": "提及", "confidence": 0.7},
            {"src": "埃琳娜", "dst": "扳手", "relation": "使用", "confidence": 0.7},
            {"src": "埃琳娜", "dst": "钳子", "relation": "使用", "confidence": 0.7},
            {"src": "埃琳娜", "dst": "矿石", "relation": "捡拾", "confidence": 0.7},
            {"src": "克努特", "dst": "零件", "relation": "找到", "confidence": 0.9},
            {"src": "克努特", "dst": "雕像", "relation": "提及", "confidence": 0.7},
        ],
    },
    # 7) 乌里扬娜归来 · 维拉与孩子们欢迎会
    "bda71a1453719eb2": {
        "entities": [
            {"name": "乌里扬娜", "type": "角色", "aliases": ["乌里扬娜老师", "乌里扬娜同志"]},
            {"name": "尼娜", "type": "角色", "aliases": []},
            {"name": "帕索诺", "type": "角色", "aliases": []},
            {"name": "彼得森", "type": "角色", "aliases": []},
            {"name": "矿场", "type": "地点", "aliases": []},
            {"name": "阿夫西维", "type": "角色", "aliases": []},
            {"name": "广场", "type": "地点", "aliases": []},
            {"name": "维拉", "type": "角色", "aliases": []},
            {"name": "向日葵", "type": "物品", "aliases": []},
            {"name": "亚什基", "type": "地点", "aliases": []},
            {"name": "基金会", "type": "组织", "aliases": []},
            {"name": "港口", "type": "地点", "aliases": []},
            {"name": "劳动食堂", "type": "地点", "aliases": []},
            {"name": "欢迎会", "type": "事件", "aliases": []},
            {"name": "庆祝会", "type": "事件", "aliases": []},
            {"name": "合作协议", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "尼娜", "dst": "乌里扬娜", "relation": "称呼老师", "confidence": 0.8},
            {"src": "帕索诺", "dst": "乌里扬娜", "relation": "称呼老师", "confidence": 0.8},
            {"src": "彼得森", "dst": "矿场", "relation": "知晓近路", "confidence": 0.7},
            {"src": "阿夫西维", "dst": "广场", "relation": "获赠", "confidence": 0.7},
            {"src": "阿夫西维", "dst": "维拉", "relation": "转述", "confidence": 0.7},
            {"src": "阿夫西维", "dst": "向日葵", "relation": "分享", "confidence": 0.8},
            {"src": "乌里扬娜", "dst": "向日葵", "relation": "称赞", "confidence": 0.7},
            {"src": "维拉", "dst": "乌里扬娜", "relation": "欢迎回家", "confidence": 0.9},
            {"src": "维拉", "dst": "基金会", "relation": "合作", "confidence": 0.8},
            {"src": "维拉", "dst": "亚什基", "relation": "在", "confidence": 0.7},
            {"src": "维拉", "dst": "港口", "relation": "前往", "confidence": 0.7},
            {"src": "欢迎会", "dst": "庆祝会", "relation": "同天", "confidence": 0.8},
            {"src": "维拉", "dst": "合作协议", "relation": "依据", "confidence": 0.7},
        ],
    },
    # 8) 玛蒂尔达之母贝丽尔 · 菲林士多履历与波蒂埃梁月查胶卷
    "52004dbecbc88eeb": {
        "entities": [
            {"name": "玛蒂尔达", "type": "角色", "aliases": ["玛蒂尔达小姐"]},
            {"name": "贝丽尔", "type": "角色", "aliases": ["贝丽尔女士"]},
            {"name": "莱瑟姆", "type": "角色", "aliases": []},
            {"name": "警局", "type": "地点", "aliases": []},
            {"name": "菲林士多", "type": "角色", "aliases": []},
            {"name": "神秘学家", "type": "概念", "aliases": []},
            {"name": "演员", "type": "概念", "aliases": ['"演员"']},
            {"name": "香港", "type": "地点", "aliases": []},
            {"name": "南加州电影艺术学院", "type": "组织", "aliases": []},
            {"name": "佳视电视台", "type": "组织", "aliases": []},
            {"name": "民间独立制片公司", "type": "组织", "aliases": []},
            {"name": "新艺术公司", "type": "组织", "aliases": []},
            {"name": "糊涂", "type": "物品", "aliases": ["《糊涂》"]},
            {"name": "神秘警探C07", "type": "物品", "aliases": ["《神秘警探C07》"]},
            {"name": "映像事件", "type": "事件", "aliases": ['"映像事件"']},
            {"name": "波蒂埃", "type": "角色", "aliases": []},
            {"name": "梁月", "type": "角色", "aliases": []},
            {"name": "空脑袋", "type": "角色", "aliases": []},
            {"name": "胶卷", "type": "物品", "aliases": []},
            {"name": "奇门遁甲", "type": "物品", "aliases": ["《奇门遁甲》"]},
            {"name": "僵尸女士", "type": "物品", "aliases": ["《僵尸女士》"]},
            {"name": "阿癫正传", "type": "物品", "aliases": ["《阿癫正传》"]},
        ],
        "relations": [
            {"src": "贝丽尔", "dst": "玛蒂尔达", "relation": "是母亲", "confidence": 0.9},
            {"src": "贝丽尔", "dst": "莱瑟姆", "relation": "理解", "confidence": 0.7},
            {"src": "菲林士多", "dst": "神秘学家", "relation": "是", "confidence": 0.9},
            {"src": "菲林士多", "dst": "演员", "relation": "操控", "confidence": 0.8},
            {"src": "菲林士多", "dst": "香港", "relation": "出生", "confidence": 0.8},
            {"src": "菲林士多", "dst": "南加州电影艺术学院", "relation": "毕业", "confidence": 0.8},
            {"src": "菲林士多", "dst": "佳视电视台", "relation": "供职", "confidence": 0.8},
            {"src": "菲林士多", "dst": "民间独立制片公司", "relation": "合作", "confidence": 0.7},
            {"src": "菲林士多", "dst": "新艺术公司", "relation": "成立", "confidence": 0.8},
            {"src": "菲林士多", "dst": "糊涂", "relation": "执导", "confidence": 0.8},
            {"src": "菲林士多", "dst": "神秘警探C07", "relation": "拍摄", "confidence": 0.8},
            {"src": "菲林士多", "dst": "映像事件", "relation": "关联", "confidence": 0.7},
            {"src": "波蒂埃", "dst": "梁月", "relation": "询问", "confidence": 0.8},
            {"src": "波蒂埃", "dst": "空脑袋", "relation": "提及", "confidence": 0.7},
            {"src": "梁月", "dst": "空脑袋", "relation": "复查", "confidence": 0.8},
            {"src": "空脑袋", "dst": "胶卷", "relation": "携带", "confidence": 0.8},
            {"src": "空脑袋", "dst": "奇门遁甲", "relation": "携带", "confidence": 0.8},
            {"src": "空脑袋", "dst": "僵尸女士", "relation": "携带", "confidence": 0.8},
            {"src": "空脑袋", "dst": "阿癫正传", "relation": "携带", "confidence": 0.8},
        ],
    },
    # 9) 口香糖与圣洛夫基金会南岸广场
    "b7c02e9a590c2512": {
        "entities": [
            {"name": "口香糖", "type": "物品", "aliases": []},
            {"name": "糖胶树胶", "type": "物品", "aliases": []},
            {"name": "薄荷", "type": "概念", "aliases": []},
            {"name": "瑞格利球场", "type": "地点", "aliases": []},
            {"name": "泡泡糖机", "type": "物品", "aliases": []},
            {"name": "胶基", "type": "物品", "aliases": []},
            {"name": "砂粒", "type": "物品", "aliases": []},
            {"name": "弹性纤维", "type": "物品", "aliases": []},
            {"name": "南岸", "type": "地点", "aliases": []},
            {"name": "圣洛夫基金会", "type": "组织", "aliases": []},
            {"name": "芝加哥", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "口香糖", "dst": "糖胶树胶", "relation": "由制成", "confidence": 0.8},
            {"src": "口香糖", "dst": "瑞格利球场", "relation": "来源于", "confidence": 0.8},
            {"src": "泡泡糖机", "dst": "口香糖", "relation": "销售", "confidence": 0.8},
            {"src": "口香糖", "dst": "胶基", "relation": "含有", "confidence": 0.8},
            {"src": "胶基", "dst": "砂粒", "relation": "混杂", "confidence": 0.8},
            {"src": "胶基", "dst": "弹性纤维", "relation": "混杂", "confidence": 0.8},
            {"src": "圣洛夫基金会", "dst": "南岸", "relation": "位于", "confidence": 0.9},
            {"src": "薄荷", "dst": "口香糖", "relation": "调味", "confidence": 0.8},
        ],
    },
    # 10) 南岸广场前的基金会小姑娘与黑西装小女孩
    "9b84cd2b464a5fef": {
        "entities": [
            {"name": "砂粒", "type": "物品", "aliases": []},
            {"name": "弹性纤维", "type": "物品", "aliases": []},
            {"name": "南岸", "type": "地点", "aliases": []},
            {"name": "圣洛夫基金会", "type": "组织", "aliases": ["基金会"]},
            {"name": "广场", "type": "地点", "aliases": []},
            {"name": "投机分子", "type": "角色", "aliases": []},
            {"name": "小姑娘", "type": "角色", "aliases": []},
            {"name": "政治家们", "type": "角色", "aliases": ['"政治家们"']},
            {"name": "任务胶囊", "type": "物品", "aliases": []},
            {"name": "黑西装小女孩", "type": "角色", "aliases": []},
            {"name": "加州", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "圣洛夫基金会", "dst": "南岸", "relation": "位于", "confidence": 0.9},
            {"src": "投机分子", "dst": "圣洛夫基金会", "relation": "引起注意", "confidence": 0.7},
            {"src": "圣洛夫基金会", "dst": "投机分子", "relation": "敷衍", "confidence": 0.7},
            {"src": "圣洛夫基金会", "dst": "小姑娘", "relation": "派出", "confidence": 0.8},
            {"src": "小姑娘", "dst": "任务胶囊", "relation": "持有", "confidence": 0.8},
            {"src": "小姑娘", "dst": "政治家们", "relation": "不擅长", "confidence": 0.7},
            {"src": "黑西装小女孩", "dst": "圣洛夫基金会", "relation": "关联", "confidence": 0.7},
            {"src": "黑西装小女孩", "dst": "广场", "relation": "位于", "confidence": 0.7},
            {"src": "圣洛夫基金会", "dst": "广场", "relation": "前临", "confidence": 0.8},
        ],
    },
    # 11) 苏芙比与十四行诗相逢 · 格雷克太太的城堡家族
    "853c51c0e6c1dd58": {
        "entities": [
            {"name": "咒语升阶", "type": "概念", "aliases": []},
            {"name": "苏芙比", "type": "角色", "aliases": []},
            {"name": "雷文哈特", "type": "角色", "aliases": []},
            {"name": "十四行诗", "type": "角色", "aliases": []},
            {"name": "魔精", "type": "角色", "aliases": []},
            {"name": "外头的朋友", "type": "概念", "aliases": ['"外头的朋友"']},
            {"name": "神秘术", "type": "概念", "aliases": []},
            {"name": "缴械技艺", "type": "概念", "aliases": []},
            {"name": "格雷克太太", "type": "角色", "aliases": []},
            {"name": "斯奈德", "type": "角色", "aliases": []},
            {"name": "黑衣人", "type": "角色", "aliases": []},
            {"name": "城堡", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "苏芙比", "dst": "十四行诗", "relation": "相逢", "confidence": 0.9},
            {"src": "十四行诗", "dst": "魔精", "relation": "击退", "confidence": 0.8},
            {"src": "十四行诗", "dst": "外头的朋友", "relation": "获得", "confidence": 0.8},
            {"src": "苏芙比", "dst": "雷文哈特", "relation": "宅邸陈列", "confidence": 0.7},
            {"src": "咒语升阶", "dst": "神秘术", "relation": "改变", "confidence": 0.8},
            {"src": "缴械技艺", "dst": "神秘术", "relation": "束缚", "confidence": 0.8},
            {"src": "格雷克太太", "dst": "斯奈德", "relation": "受关照", "confidence": 0.8},
            {"src": "格雷克太太", "dst": "黑衣人", "relation": "部署", "confidence": 0.8},
            {"src": "格雷克太太", "dst": "城堡", "relation": "关联", "confidence": 0.7},
        ],
    },
    # 12) 洛伦兹研究所与最初的蝴蝶 · 无名来客与魔精
    "c99b2961c9a6c1f1": {
        "entities": [
            {"name": "黑色粘液的信", "type": "物品", "aliases": []},
            {"name": "洛伦兹研究所", "type": "组织", "aliases": []},
            {"name": "暴雨", "type": "现象", "aliases": ['"暴雨"']},
            {"name": "拉普拉斯科算中心", "type": "组织", "aliases": []},
            {"name": "神秘术", "type": "概念", "aliases": []},
            {"name": "混沌能量", "type": "概念", "aliases": []},
            {"name": "最初的蝴蝶", "type": "概念", "aliases": ['"最初的蝴蝶"']},
            {"name": "洛伦兹调查员", "type": "角色", "aliases": []},
            {"name": "先锋小队", "type": "组织", "aliases": []},
            {"name": "仪式蕴蓄", "type": "概念", "aliases": []},
            {"name": "无名来客Ⅱ", "type": "角色", "aliases": []},
            {"name": "魔精", "type": "角色", "aliases": []},
            {"name": "吐真剂", "type": "物品", "aliases": []},
            {"name": "无名诗", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "洛伦兹研究所", "dst": "拉普拉斯科算中心", "relation": "独立于", "confidence": 0.9},
            {"src": "洛伦兹研究所", "dst": "暴雨", "relation": "诞生于", "confidence": 0.8},
            {"src": "洛伦兹研究所", "dst": "神秘术", "relation": "主张研究", "confidence": 0.8},
            {"src": "洛伦兹研究所", "dst": "混沌能量", "relation": "捕捉", "confidence": 0.8},
            {"src": "洛伦兹研究所", "dst": "最初的蝴蝶", "relation": "寻觅", "confidence": 0.8},
            {"src": "洛伦兹研究所", "dst": "洛伦兹调查员", "relation": "派出", "confidence": 0.8},
            {"src": "先锋小队", "dst": "洛伦兹调查员", "relation": "交锋", "confidence": 0.8},
            {"src": "无名来客Ⅱ", "dst": "暴雨", "relation": "受阻于", "confidence": 0.7},
            {"src": "魔精", "dst": "吐真剂", "relation": "接受", "confidence": 0.8},
        ],
    },
    # 13) 律动·其一与园丁剪刀 · 森林火灾与汽油
    "577748c3e2633354": {
        "entities": [
            {"name": "律动·其一", "type": "概念", "aliases": []},
            {"name": "旋律", "type": "概念", "aliases": []},
            {"name": "园丁剪刀", "type": "物品", "aliases": []},
            {"name": "荆棘", "type": "物品", "aliases": []},
            {"name": "藤蔓", "type": "物品", "aliases": []},
            {"name": "橡树", "type": "物品", "aliases": []},
            {"name": "烟尘", "type": "现象", "aliases": []},
            {"name": "火焰", "type": "现象", "aliases": []},
            {"name": "汽油", "type": "物品", "aliases": []},
            {"name": "草皮", "type": "物品", "aliases": []},
            {"name": "森林", "type": "地点", "aliases": []},
            {"name": "火灾", "type": "事件", "aliases": []},
            {"name": "铭牌", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "律动·其一", "dst": "旋律", "relation": "调整", "confidence": 0.8},
            {"src": "园丁剪刀", "dst": "荆棘", "relation": "剪去", "confidence": 0.8},
            {"src": "园丁剪刀", "dst": "藤蔓", "relation": "剪去", "confidence": 0.8},
            {"src": "森林", "dst": "橡树", "relation": "包含", "confidence": 0.8},
            {"src": "火灾", "dst": "汽油", "relation": "由引发", "confidence": 0.8},
            {"src": "火灾", "dst": "火焰", "relation": "包含", "confidence": 0.8},
            {"src": "汽油", "dst": "森林", "relation": "弥漫", "confidence": 0.7},
            {"src": "烟尘", "dst": "火灾", "relation": "源自", "confidence": 0.8},
        ],
    },
    # 14) 阿派朗学派交流 · 乌尔里希审核与先驱跨越暴雨
    "f9a0cf3534b039af": {
        "entities": [
            {"name": "阿派朗学派", "type": "组织", "aliases": []},
            {"name": "司辰", "type": "角色", "aliases": []},
            {"name": "暴雨", "type": "现象", "aliases": ['"暴雨"']},
            {"name": "科算中心", "type": "组织", "aliases": []},
            {"name": "圣洛夫基金会", "type": "组织", "aliases": []},
            {"name": "司辰小队", "type": "组织", "aliases": []},
            {"name": "乌尔里希", "type": "角色", "aliases": []},
            {"name": "思维交锋", "type": "概念", "aliases": []},
            {"name": "先驱", "type": "角色", "aliases": ['"先驱"']},
            {"name": "磁流体", "type": "物品", "aliases": []},
            {"name": "玻璃缸", "type": "物品", "aliases": []},
            {"name": "人造卫星", "type": "物品", "aliases": []},
            {"name": "数据", "type": "概念", "aliases": []},
            {"name": "照片", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "司辰", "dst": "暴雨", "relation": "调查", "confidence": 0.9},
            {"src": "科算中心", "dst": "暴雨", "relation": "研究", "confidence": 0.9},
            {"src": "司辰小队", "dst": "司辰", "relation": "由领导", "confidence": 0.8},
            {"src": "司辰小队", "dst": "圣洛夫基金会", "relation": "交流", "confidence": 0.7},
            {"src": "司辰小队", "dst": "阿派朗学派", "relation": "交流", "confidence": 0.7},
            {"src": "乌尔里希", "dst": "司辰小队", "relation": "评审", "confidence": 0.7},
            {"src": "思维交锋", "dst": "先驱", "relation": "讨论", "confidence": 0.8},
            {"src": "先驱", "dst": "暴雨", "relation": "跨越", "confidence": 0.8},
            {"src": "先驱", "dst": "人造卫星", "relation": "疑为", "confidence": 0.7},
            {"src": "人造卫星", "dst": "数据", "relation": "发送", "confidence": 0.8},
            {"src": "人造卫星", "dst": "暴雨", "relation": "被回溯", "confidence": 0.8},
            {"src": "磁流体", "dst": "玻璃缸", "relation": "位于", "confidence": 0.8},
        ],
    },
    # 15) 随船医护门诊日志 · 人工暴雨论文与努库泰澳
    "b628ff6a9f8e46a3": {
        "entities": [
            {"name": "病历单", "type": "物品", "aliases": []},
            {"name": "随船医护", "type": "角色", "aliases": []},
            {"name": "查理", "type": "角色", "aliases": []},
            {"name": "茶苯海明片", "type": "物品", "aliases": []},
            {"name": "珍妮丝", "type": "角色", "aliases": []},
            {"name": "卡莱阿", "type": "角色", "aliases": []},
            {"name": "阿莱西奥", "type": "角色", "aliases": []},
            {"name": "地芬诺酯", "type": "物品", "aliases": []},
            {"name": "电热水器", "type": "物品", "aliases": []},
            {"name": "水火箱", "type": "物品", "aliases": ['"水火箱"']},
            {"name": "热气壶", "type": "物品", "aliases": ['"热气壶"']},
            {"name": "船长", "type": "角色", "aliases": []},
            {"name": "挂贝壳的小伙子", "type": "角色", "aliases": []},
            {"name": "艾拉", "type": "角色", "aliases": []},
            {"name": "贝壳", "type": "物品", "aliases": []},
            {"name": "努库泰澳", "type": "地点", "aliases": []},
            {"name": "新时代", "type": "概念", "aliases": ['"新时代"']},
            {"name": "寻找稳定性材料", "type": "物品", "aliases": ["《寻找稳定性材料——来自\"人工暴雨\"实验的数据验证（一稿）》"]},
            {"name": "人工暴雨", "type": "概念", "aliases": ['"人工暴雨"']},
        ],
        "relations": [
            {"src": "随船医护", "dst": "查理", "relation": "诊治", "confidence": 0.8},
            {"src": "随船医护", "dst": "珍妮丝", "relation": "诊治", "confidence": 0.8},
            {"src": "随船医护", "dst": "卡莱阿", "relation": "诊治", "confidence": 0.8},
            {"src": "随船医护", "dst": "阿莱西奥", "relation": "诊治", "confidence": 0.8},
            {"src": "随船医护", "dst": "艾拉", "relation": "诊治", "confidence": 0.8},
            {"src": "查理", "dst": "茶苯海明片", "relation": "服用", "confidence": 0.8},
            {"src": "珍妮丝", "dst": "茶苯海明片", "relation": "服用", "confidence": 0.8},
            {"src": "卡莱阿", "dst": "茶苯海明片", "relation": "拒绝", "confidence": 0.7},
            {"src": "阿莱西奥", "dst": "地芬诺酯", "relation": "服用", "confidence": 0.8},
            {"src": "卡莱阿", "dst": "电热水器", "relation": "被烫伤", "confidence": 0.8},
            {"src": "船长", "dst": "挂贝壳的小伙子", "relation": "撇清", "confidence": 0.7},
            {"src": "艾拉", "dst": "新时代", "relation": "声称到达", "confidence": 0.8},
            {"src": "艾拉", "dst": "努库泰澳", "relation": "欲返回", "confidence": 0.8},
            {"src": "艾拉", "dst": "贝壳", "relation": "佩戴", "confidence": 0.8},
            {"src": "寻找稳定性材料", "dst": "人工暴雨", "relation": "关于", "confidence": 0.8},
            {"src": "挂贝壳的小伙子", "dst": "贝壳", "relation": "佩戴", "confidence": 0.7},
        ],
    },
    # 16) 康斯坦丁传话 · 阿尼姆斯与淑女格蕾丝筹备仪式
    "4a70d43b24c5b321": {
        "entities": [
            {"name": "康斯坦丁", "type": "角色", "aliases": []},
            {"name": "职场生存指南", "type": "物品", "aliases": []},
            {"name": "阿尼姆斯", "type": "角色", "aliases": ["阿尼姆斯女士"]},
            {"name": "淑女格蕾丝", "type": "角色", "aliases": []},
            {"name": "勿忘我先生", "type": "角色", "aliases": ['"勿忘我先生"', "勿忘我"]},
            {"name": "不老泉", "type": "物品", "aliases": []},
            {"name": "神殿", "type": "地点", "aliases": []},
            {"name": "圣地", "type": "地点", "aliases": []},
            {"name": "永生药", "type": "物品", "aliases": []},
            {"name": "圣所", "type": "地点", "aliases": []},
            {"name": "复苏之母", "type": "角色", "aliases": ["母"]},
            {"name": "面具", "type": "物品", "aliases": []},
            {"name": "秘之教诲者", "type": "角色", "aliases": []},
            {"name": "使徒", "type": "角色", "aliases": []},
            {"name": "红发的骗子", "type": "角色", "aliases": []},
            {"name": "追随者", "type": "角色", "aliases": []},
            {"name": "仪式", "type": "概念", "aliases": []},
            {"name": "忠诚的尺度", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "康斯坦丁", "dst": "淑女格蕾丝", "relation": "提及", "confidence": 0.7},
            {"src": "淑女格蕾丝", "dst": "勿忘我先生", "relation": "受委派", "confidence": 0.9},
            {"src": "淑女格蕾丝", "dst": "不老泉", "relation": "护送", "confidence": 0.9},
            {"src": "淑女格蕾丝", "dst": "神殿", "relation": "送往", "confidence": 0.9},
            {"src": "淑女格蕾丝", "dst": "阿尼姆斯", "relation": "协助", "confidence": 0.8},
            {"src": "淑女格蕾丝", "dst": "仪式", "relation": "筹备", "confidence": 0.8},
            {"src": "阿尼姆斯", "dst": "勿忘我先生", "relation": "质疑", "confidence": 0.7},
            {"src": "阿尼姆斯", "dst": "永生药", "relation": "评论", "confidence": 0.7},
            {"src": "勿忘我先生", "dst": "永生药", "relation": "炼制", "confidence": 0.8},
            {"src": "复苏之母", "dst": "勿忘我先生", "relation": "赋予使命", "confidence": 0.8},
            {"src": "勿忘我先生", "dst": "圣所", "relation": "应朝圣", "confidence": 0.7},
            {"src": "阿尼姆斯", "dst": "复苏之母", "relation": "信奉", "confidence": 0.8},
            {"src": "淑女格蕾丝", "dst": "秘之教诲者", "relation": "献信仰", "confidence": 0.8},
            {"src": "阿尼姆斯", "dst": "淑女格蕾丝", "relation": "指认为使徒", "confidence": 0.8},
            {"src": "淑女格蕾丝", "dst": "使徒", "relation": "被认作", "confidence": 0.8},
            {"src": "阿尼姆斯", "dst": "红发的骗子", "relation": "提及", "confidence": 0.7},
            {"src": "阿尼姆斯", "dst": "面具", "relation": "要求", "confidence": 0.7},
            {"src": "淑女格蕾丝", "dst": "面具", "relation": "未佩戴", "confidence": 0.7},
            {"src": "追随者", "dst": "仪式", "relation": "护送材料", "confidence": 0.7},
            {"src": "淑女格蕾丝", "dst": "追随者", "relation": "是", "confidence": 0.8},
        ],
    },
    # 17) 地母神话三则 · 孩子与宗教辩论
    "891ecc52e7541592": {
        "entities": [
            {"name": "孩子", "type": "角色", "aliases": []},
            {"name": "弓箭", "type": "物品", "aliases": []},
            {"name": "牝鹿", "type": "角色", "aliases": []},
            {"name": "地母", "type": "角色", "aliases": []},
            {"name": "春天", "type": "现象", "aliases": []},
            {"name": "太阳", "type": "现象", "aliases": []},
            {"name": "寒冰", "type": "现象", "aliases": []},
            {"name": "苔藓", "type": "物品", "aliases": []},
            {"name": "游鱼", "type": "角色", "aliases": []},
            {"name": "河床", "type": "地点", "aliases": []},
            {"name": "刀剑", "type": "物品", "aliases": []},
            {"name": "棺木", "type": "物品", "aliases": []},
            {"name": "锄头", "type": "物品", "aliases": []},
            {"name": "镐", "type": "物品", "aliases": []},
            {"name": "棉絮", "type": "物品", "aliases": []},
            {"name": "营火", "type": "物品", "aliases": []},
            {"name": "极南之地", "type": "地点", "aliases": []},
            {"name": "宗教辩论", "type": "事件", "aliases": []},
        ],
        "relations": [
            {"src": "孩子", "dst": "弓箭", "relation": "持有", "confidence": 0.9},
            {"src": "孩子", "dst": "牝鹿", "relation": "猎获", "confidence": 0.9},
            {"src": "地母", "dst": "孩子", "relation": "眷顾", "confidence": 0.9},
            {"src": "孩子", "dst": "地母", "relation": "祈祷", "confidence": 0.8},
            {"src": "孩子", "dst": "春天", "relation": "祈求", "confidence": 0.7},
            {"src": "太阳", "dst": "寒冰", "relation": "被封冻", "confidence": 0.8},
            {"src": "游鱼", "dst": "河床", "relation": "沉向", "confidence": 0.8},
            {"src": "游鱼", "dst": "刀剑", "relation": "熔为", "confidence": 0.8},
            {"src": "孩子", "dst": "极南之地", "relation": "前往", "confidence": 0.8},
            {"src": "孩子", "dst": "营火", "relation": "围坐", "confidence": 0.7},
            {"src": "宗教辩论", "dst": "地母", "relation": "涉及", "confidence": 0.7},
        ],
    },
    # 18) 反亢人类保护魔精 · 魔药书室灵译药方
    "f0c2c1db7359ac76": {
        "entities": [
            {"name": "布拉多克高地", "type": "地点", "aliases": []},
            {"name": "洞穴", "type": "地点", "aliases": []},
            {"name": "魔精", "type": "角色", "aliases": []},
            {"name": "人类", "type": "概念", "aliases": []},
            {"name": "魔药书室", "type": "组织", "aliases": ["Megrez δ魔药书室"]},
            {"name": "灵译药方", "type": "物品", "aliases": []},
            {"name": "金块", "type": "物品", "aliases": []},
            {"name": "残局", "type": "概念", "aliases": []},
            {"name": "晚餐宣传单", "type": "物品", "aliases": []},
            {"name": "传单", "type": "物品", "aliases": []},
            {"name": "金子", "type": "物品", "aliases": []},
            {"name": "绿纸", "type": "物品", "aliases": []},
            {"name": "钞票", "type": "物品", "aliases": []},
            {"name": "大报纸", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "魔精", "dst": "人类", "relation": "反抗", "confidence": 0.8},
            {"src": "魔精", "dst": "金块", "relation": "出现于", "confidence": 0.7},
            {"src": "魔精", "dst": "残局", "relation": "困于", "confidence": 0.8},
            {"src": "魔精", "dst": "传单", "relation": "阅读", "confidence": 0.8},
            {"src": "魔精", "dst": "晚餐宣传单", "relation": "提交", "confidence": 0.8},
            {"src": "人类", "dst": "金子", "relation": "食用", "confidence": 0.9},
            {"src": "金块", "dst": "金子", "relation": "即", "confidence": 0.9},
            {"src": "魔药书室", "dst": "灵译药方", "relation": "制作", "confidence": 0.8},
            {"src": "洞穴", "dst": "布拉多克高地", "relation": "位于", "confidence": 0.9},
        ],
    },
    # 19) 花园小径的门与卡文迪许 · 勿忘我少爷之死
    "1492c851ed2950f1": {
        "entities": [
            {"name": "人类", "type": "概念", "aliases": []},
            {"name": "魔药书室", "type": "组织", "aliases": ["Megrez δ魔药书室"]},
            {"name": "灵译药方", "type": "物品", "aliases": []},
            {"name": "花园小径的门", "type": "物品", "aliases": ["木门"]},
            {"name": "荆棘", "type": "物品", "aliases": []},
            {"name": "花园", "type": "地点", "aliases": []},
            {"name": "春日", "type": "现象", "aliases": []},
            {"name": "橡木林", "type": "地点", "aliases": []},
            {"name": "劳伦斯·卡文迪许", "type": "角色", "aliases": ["老卡文迪许", "小卡文迪许"]},
            {"name": "勿忘我", "type": "角色", "aliases": ['"勿忘我"', "少爷"]},
            {"name": "火", "type": "现象", "aliases": []},
            {"name": "刀", "type": "物品", "aliases": []},
            {"name": "魔药", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "人类", "dst": "火", "relation": "使用", "confidence": 0.8},
            {"src": "人类", "dst": "刀", "relation": "使用", "confidence": 0.8},
            {"src": "魔药书室", "dst": "灵译药方", "relation": "制作", "confidence": 0.8},
            {"src": "花园小径的门", "dst": "荆棘", "relation": "缠绕", "confidence": 0.8},
            {"src": "花园", "dst": "花园小径的门", "relation": "包含", "confidence": 0.8},
            {"src": "劳伦斯·卡文迪许", "dst": "勿忘我", "relation": "关联", "confidence": 0.7},
            {"src": "勿忘我", "dst": "魔药", "relation": "制作", "confidence": 0.7},
            {"src": "劳伦斯·卡文迪许", "dst": "魔药", "relation": "制作", "confidence": 0.7},
        ],
    },
    # 20) 八卦杂志与勿忘我先生 · 大嘴巴布告栏投稿
    "ab275044ab8e04e4": {
        "entities": [
            {"name": "漂亮箱子", "type": "物品", "aliases": []},
            {"name": "伞", "type": "物品", "aliases": []},
            {"name": "黑狗", "type": "角色", "aliases": []},
            {"name": "白狗", "type": "角色", "aliases": []},
            {"name": "爆米花", "type": "物品", "aliases": []},
            {"name": "八卦杂志", "type": "物品", "aliases": []},
            {"name": "瓦尔登湖酒吧", "type": "地点", "aliases": []},
            {"name": "勿忘我先生", "type": "角色", "aliases": []},
            {"name": "神秘学家", "type": "概念", "aliases": []},
            {"name": "派对", "type": "事件", "aliases": []},
            {"name": "大嘴巴布告栏", "type": "物品", "aliases": ["《大嘴巴布告栏：读者投稿专栏》"]},
            {"name": "1927年1224刊", "type": "物品", "aliases": []},
            {"name": "蛇", "type": "角色", "aliases": []},
            {"name": "漆黑女人", "type": "角色", "aliases": []},
            {"name": "畸形儿", "type": "角色", "aliases": []},
            {"name": "蛇鳞", "type": "物品", "aliases": []},
            {"name": "玻璃", "type": "物品", "aliases": []},
            {"name": "■■■的配方", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "八卦杂志", "dst": "瓦尔登湖酒吧", "relation": "记载", "confidence": 0.8},
            {"src": "八卦杂志", "dst": "勿忘我先生", "relation": "记载", "confidence": 0.8},
            {"src": "勿忘我先生", "dst": "神秘学家", "relation": "被称", "confidence": 0.8},
            {"src": "勿忘我先生", "dst": "派对", "relation": "参加", "confidence": 0.8},
            {"src": "勿忘我先生", "dst": "蛇鳞", "relation": "长有", "confidence": 0.8},
            {"src": "勿忘我先生", "dst": "畸形儿", "relation": "被称", "confidence": 0.7},
            {"src": "勿忘我先生", "dst": "漆黑女人", "relation": "派遣", "confidence": 0.8},
            {"src": "大嘴巴布告栏", "dst": "勿忘我先生", "relation": "报道", "confidence": 0.8},
            {"src": "大嘴巴布告栏", "dst": "神秘学家", "relation": "报道", "confidence": 0.7},
            {"src": "1927年1224刊", "dst": "大嘴巴布告栏", "relation": "是期号", "confidence": 0.9},
            {"src": "漆黑女人", "dst": "玻璃", "relation": "贴附", "confidence": 0.8},
            {"src": "黑狗", "dst": "白狗", "relation": "对立", "confidence": 0.8},
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
    empty = sum(1 for d in RESULTS.values() if not (d.get("entities") or d.get("relations")))
    print(f"[validate] 块 {len(RESULTS)}，悬空 {n}，未落地 {m}")
    print(f"[stats] 实体 {total_e}，关系 {total_r}，空块 {empty}")

    if n or m:
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
    if NOOP_ADD:
        noop = set(json.loads(NOOP_FILE.read_text(encoding="utf-8")))
        noop |= set(NOOP_ADD)
        NOOP_FILE.write_text(
            json.dumps(sorted(noop), ensure_ascii=False, indent=1), encoding="utf-8"
        )
    print(f"[apply-missing-p17] 写入 {len(RESULTS)} 条，NOOP +{len(NOOP_ADD)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
