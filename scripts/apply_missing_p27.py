# -*- coding: utf-8 -*-
"""未抽取剧情块补抽 · 第 27 批（backfill2 batch_17，20 块，含 1 个数值页 NOOP）。

用法：
  python scripts/apply_missing_p27.py            # 预演（悬空+落地自检）
  python scripts/apply_missing_p27.py --apply    # 写盘
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

# 本批 1 块为角色技能/数值页（无剧情）：2d1468aebea83023（与 p18 同款"启明会信徒"角色卡）。
NOOP_ADD: list[str] = [
    "2d1468aebea83023",
]

RESULTS: dict[str, dict] = {
    # 1) UTTU 编辑部代笔 · 多瑙黎明号与血食怪
    "ee0da778192cd5db": {
        "entities": [
            {"name": "白雪松", "type": "角色", "aliases": ["白雪松女士", "“白雪松”"]},
            {"name": "《UTTU》编辑部", "type": "组织", "aliases": ["《UTTU》"]},
            {"name": "空心木", "type": "角色", "aliases": []},
            {"name": "多瑙黎明号", "type": "物品", "aliases": ["“多瑙黎明号”"]},
            {"name": "血食怪", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "白雪松", "dst": "《UTTU》编辑部", "relation": "是精神核心", "confidence": 0.8},
            {"src": "空心木", "dst": "《UTTU》编辑部", "relation": "任职于", "confidence": 0.8},
            {"src": "空心木", "dst": "白雪松", "relation": "代笔", "confidence": 0.7},
            {"src": "多瑙黎明号", "dst": "血食怪", "relation": "涉及", "confidence": 0.7},
        ],
    },
    # 2) 论坛考据 · 祝县地灾与李家迁居
    "5d3cf0203896cb60": {
        "entities": [
            {"name": "祝县", "type": "地点", "aliases": []},
            {"name": "涣州", "type": "地点", "aliases": []},
            {"name": "淳镇", "type": "地点", "aliases": []},
            {"name": "李家", "type": "组织", "aliases": ["涣州李家"]},
            {"name": "陆家", "type": "组织", "aliases": []},
            {"name": "陈家", "type": "组织", "aliases": []},
            {"name": "厉家", "type": "组织", "aliases": []},
            {"name": "地灾", "type": "概念", "aliases": ["“地灾”"]},
            {"name": "《涣州府志》", "type": "物品", "aliases": []},
            {"name": "《涣州拾遗》", "type": "物品", "aliases": []},
            {"name": "《祝县县志》", "type": "物品", "aliases": []},
            {"name": "梅花教门", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "李家", "dst": "祝县", "relation": "原长居", "confidence": 0.8},
            {"src": "李家", "dst": "淳镇", "relation": "迁居", "confidence": 0.8},
            {"src": "李家", "dst": "地灾", "relation": "躲避", "confidence": 0.8},
            {"src": "陆家", "dst": "祝县", "relation": "迁出", "confidence": 0.7},
            {"src": "陈家", "dst": "祝县", "relation": "迁出", "confidence": 0.7},
            {"src": "厉家", "dst": "祝县", "relation": "迁出", "confidence": 0.7},
            {"src": "《涣州府志》", "dst": "地灾", "relation": "记录", "confidence": 0.7},
            {"src": "《涣州拾遗》", "dst": "地灾", "relation": "描述", "confidence": 0.8},
            {"src": "梅花教门", "dst": "地灾", "relation": "关联", "confidence": 0.7},
        ],
    },
    # 3) 戏中戏 · 公主与歌剧演员
    "510aa5218f5f4bc6": {
        "entities": [
            {"name": "公主", "type": "角色", "aliases": []},
            {"name": "国王", "type": "角色", "aliases": []},
            {"name": "小夜莺", "type": "角色", "aliases": []},
            {"name": "歌剧演员", "type": "角色", "aliases": []},
            {"name": "灰白色屋子", "type": "地点", "aliases": []},
            {"name": "灰白色衣服的先生", "type": "角色", "aliases": []},
            {"name": "冠冕", "type": "物品", "aliases": []},
            {"name": "舞台", "type": "概念", "aliases": []},
            {"name": "戏剧", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "公主", "dst": "国王", "relation": "是儿女", "confidence": 0.9},
            {"src": "歌剧演员", "dst": "公主", "relation": "是", "confidence": 0.8},
            {"src": "小夜莺", "dst": "歌剧演员", "relation": "比喻", "confidence": 0.7},
            {"src": "歌剧演员", "dst": "灰白色屋子", "relation": "进入", "confidence": 0.8},
            {"src": "歌剧演员", "dst": "灰白色衣服的先生", "relation": "颔首", "confidence": 0.7},
            {"src": "冠冕", "dst": "歌剧演员", "relation": "属于", "confidence": 0.7},
            {"src": "戏剧", "dst": "歌剧演员", "relation": "关于", "confidence": 0.7},
            {"src": "舞台", "dst": "歌剧演员", "relation": "关联", "confidence": 0.7},
        ],
    },
    # 4) 维也纳日报 · 迪塔斯多夫家族
    "4eb69765518b3046": {
        "entities": [
            {"name": "《维也纳日报》", "type": "物品", "aliases": []},
            {"name": "迪塔斯多夫家族", "type": "组织", "aliases": []},
            {"name": "维也纳", "type": "地点", "aliases": []},
            {"name": "伊文洁琳·迪塔斯多夫", "type": "角色", "aliases": []},
            {"name": "伊索尔德·迪塔斯多夫", "type": "角色", "aliases": []},
            {"name": "卡卡尼亚", "type": "角色", "aliases": []},
            {"name": "分离派之家", "type": "地点", "aliases": []},
            {"name": "施瓦茨医生", "type": "角色", "aliases": []},
            {"name": "《迪塔斯多夫：追忆那璀璨又易碎的维也纳天籁》", "type": "物品", "aliases": []},
            {"name": "《曾令人惊艳的七重纱》", "type": "物品", "aliases": []},
            {"name": "《伊索尔德：科学的支持者》", "type": "物品", "aliases": []},
            {"name": "神秘学家血脉", "type": "概念", "aliases": ["“诅咒”"]},
        ],
        "relations": [
            {"src": "伊文洁琳·迪塔斯多夫", "dst": "迪塔斯多夫家族", "relation": "属于", "confidence": 0.9},
            {"src": "伊索尔德·迪塔斯多夫", "dst": "迪塔斯多夫家族", "relation": "属于", "confidence": 0.9},
            {"src": "伊索尔德·迪塔斯多夫", "dst": "伊文洁琳·迪塔斯多夫", "relation": "是之女", "confidence": 0.9},
            {"src": "迪塔斯多夫家族", "dst": "维也纳", "relation": "名震于", "confidence": 0.8},
            {"src": "卡卡尼亚", "dst": "分离派之家", "relation": "主持", "confidence": 0.8},
            {"src": "伊索尔德·迪塔斯多夫", "dst": "施瓦茨医生", "relation": "就诊于", "confidence": 0.8},
            {"src": "伊索尔德·迪塔斯多夫", "dst": "神秘学家血脉", "relation": "受侵扰", "confidence": 0.8},
            {"src": "《迪塔斯多夫：追忆那璀璨又易碎的维也纳天籁》", "dst": "迪塔斯多夫家族", "relation": "记述", "confidence": 0.7},
            {"src": "《曾令人惊艳的七重纱》", "dst": "迪塔斯多夫家族", "relation": "记述", "confidence": 0.7},
            {"src": "《伊索尔德：科学的支持者》", "dst": "伊索尔德·迪塔斯多夫", "relation": "关于", "confidence": 0.8},
            {"src": "《维也纳日报》", "dst": "迪塔斯多夫家族", "relation": "报道", "confidence": 0.7},
        ],
    },
    # 5) 数值/技能页（无剧情）→ NOOP
    "2d1468aebea83023": {
        "entities": [],
        "relations": [],
    },
    # 6) IDM 维护记录 · 苏菲亚与接插线板
    "e1acb7cf000ac0f3": {
        "entities": [
            {"name": "IDM维护记录", "type": "物品", "aliases": []},
            {"name": "穿孔纸卡", "type": "物品", "aliases": []},
            {"name": "接插线板", "type": "物品", "aliases": ["新型接插线板"]},
            {"name": "示数表", "type": "物品", "aliases": []},
            {"name": "表a1G4", "type": "物品", "aliases": []},
            {"name": "苏菲亚", "type": "角色", "aliases": []},
            {"name": "离岛", "type": "地点", "aliases": []},
            {"name": "烤肉", "type": "物品", "aliases": []},
            {"name": "格格不入者", "type": "概念", "aliases": ["小径① 格格不入者"]},
        ],
        "relations": [
            {"src": "IDM维护记录", "dst": "穿孔纸卡", "relation": "记录更换", "confidence": 0.8},
            {"src": "IDM维护记录", "dst": "接插线板", "relation": "记录检查", "confidence": 0.8},
            {"src": "IDM维护记录", "dst": "示数表", "relation": "记录更换", "confidence": 0.8},
            {"src": "表a1G4", "dst": "示数表", "relation": "是", "confidence": 0.8},
            {"src": "苏菲亚", "dst": "接插线板", "relation": "获赠", "confidence": 0.8},
            {"src": "烤肉", "dst": "IDM维护记录", "relation": "现于涂鸦", "confidence": 0.7},
            {"src": "格格不入者", "dst": "离岛", "relation": "位于", "confidence": 0.7},
        ],
    },
    # 7) 芝诺密电 · 暴雨·兀尔德与回环实验室 + 拉普拉斯病历
    "e44c7dc58ebf6408": {
        "entities": [
            {"name": "芝诺", "type": "组织", "aliases": ["芝诺总部", "芝诺各分部"]},
            {"name": "暴雨", "type": "现象", "aliases": ["“暴雨”"]},
            {"name": "兀尔德", "type": "角色", "aliases": []},
            {"name": "最初的她", "type": "概念", "aliases": ["“最初的她”"]},
            {"name": "回环实验室", "type": "组织", "aliases": []},
            {"name": "琥珀屋", "type": "概念", "aliases": ["“琥珀屋”"]},
            {"name": "逃兵们", "type": "概念", "aliases": ["“逃兵们”"]},
            {"name": "顿河", "type": "地点", "aliases": []},
            {"name": "拉普拉斯康复研究中心", "type": "组织", "aliases": []},
            {"name": "路德维希", "type": "角色", "aliases": []},
            {"name": "拉普拉斯人事委员会", "type": "组织", "aliases": []},
            {"name": "蜂巢思维", "type": "概念", "aliases": []},
            {"name": "蜜蜂", "type": "角色", "aliases": []},
            {"name": "里沙尔·勒努阿尔", "type": "角色", "aliases": []},
            {"name": "菲茨威廉", "type": "角色", "aliases": []},
            {"name": "平", "type": "角色", "aliases": []},
            {"name": "拉丽莎", "type": "角色", "aliases": []},
            {"name": "挖掘艺术", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "芝诺", "dst": "暴雨", "relation": "研究", "confidence": 0.8},
            {"src": "芝诺", "dst": "兀尔德", "relation": "定位接触", "confidence": 0.8},
            {"src": "兀尔德", "dst": "最初的她", "relation": "是", "confidence": 0.9},
            {"src": "最初的她", "dst": "暴雨", "relation": "未受影响", "confidence": 0.7},
            {"src": "芝诺", "dst": "回环实验室", "relation": "建立", "confidence": 0.9},
            {"src": "回环实验室", "dst": "顿河", "relation": "位于", "confidence": 0.8},
            {"src": "回环实验室", "dst": "琥珀屋", "relation": "代号", "confidence": 0.8},
            {"src": "回环实验室", "dst": "暴雨", "relation": "免疫", "confidence": 0.8},
            {"src": "回环实验室", "dst": "逃兵们", "relation": "接收", "confidence": 0.8},
            {"src": "拉普拉斯康复研究中心", "dst": "路德维希", "relation": "收治", "confidence": 0.8},
            {"src": "拉普拉斯康复研究中心", "dst": "拉普拉斯人事委员会", "relation": "隶属", "confidence": 0.7},
            {"src": "蜂巢思维", "dst": "蜜蜂", "relation": "相关", "confidence": 0.7},
            {"src": "芝诺", "dst": "里沙尔·勒努阿尔", "relation": "提及", "confidence": 0.7},
            {"src": "芝诺", "dst": "菲茨威廉", "relation": "提及", "confidence": 0.7},
            {"src": "芝诺", "dst": "平", "relation": "提及", "confidence": 0.7},
            {"src": "芝诺", "dst": "拉丽莎", "relation": "提及", "confidence": 0.7},
            {"src": "芝诺", "dst": "挖掘艺术", "relation": "提及", "confidence": 0.7},
        ],
    },
    # 8) 巴黎传言 · 英雄之后与出租车司机
    "492228ef58f9e1bd": {
        "entities": [
            {"name": "法国", "type": "地点", "aliases": []},
            {"name": "巴黎", "type": "地点", "aliases": []},
            {"name": "大萧条", "type": "概念", "aliases": []},
            {"name": "出租车司机", "type": "角色", "aliases": []},
            {"name": "英雄之后", "type": "角色", "aliases": []},
            {"name": "宿命", "type": "概念", "aliases": []},
            {"name": "诅咒", "type": "概念", "aliases": []},
            {"name": "混沌", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "出租车司机", "dst": "法国", "relation": "居于", "confidence": 0.7},
            {"src": "出租车司机", "dst": "巴黎", "relation": "居于", "confidence": 0.7},
            {"src": "英雄之后", "dst": "宿命", "relation": "携带", "confidence": 0.8},
            {"src": "英雄之后", "dst": "诅咒", "relation": "携带", "confidence": 0.8},
            {"src": "英雄之后", "dst": "巴黎", "relation": "卷入", "confidence": 0.8},
            {"src": "大萧条", "dst": "法国", "relation": "影响", "confidence": 0.8},
            {"src": "巴黎", "dst": "混沌", "relation": "陷入", "confidence": 0.8},
        ],
    },
    # 9) 战斗对话 · S女士真名与乔·布朗、贝克特
    "2f3dd0bf13d57b79": {
        "entities": [
            {"name": "斯普特尼克女士", "type": "角色", "aliases": ["S女士", "斯普特尼克"]},
            {"name": "乔·布朗", "type": "角色", "aliases": ["J"]},
            {"name": "贝克特", "type": "角色", "aliases": ["贝克特先生"]},
        ],
        "relations": [
            {"src": "斯普特尼克女士", "dst": "乔·布朗", "relation": "是死党", "confidence": 0.8},
            {"src": "贝克特", "dst": "斯普特尼克女士", "relation": "猜名", "confidence": 0.7},
            {"src": "贝克特", "dst": "乔·布朗", "relation": "对话", "confidence": 0.7},
        ],
    },
    # 10) 决斗手册与帝国寓言 · 多瑙河
    "8a2832b5fe51d977": {
        "entities": [
            {"name": "多瑙河", "type": "地点", "aliases": []},
            {"name": "帝国", "type": "概念", "aliases": []},
            {"name": "帝国的孩子", "type": "概念", "aliases": []},
            {"name": "金色大厅", "type": "地点", "aliases": []},
            {"name": "法国1733龙骑兵燧发枪", "type": "物品", "aliases": []},
            {"name": "柯尔特M1873", "type": "物品", "aliases": []},
            {"name": "史密斯-韦森第一代转轮手枪", "type": "物品", "aliases": []},
            {"name": "副手", "type": "角色", "aliases": []},
            {"name": "医生", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "多瑙河", "dst": "帝国", "relation": "孕育", "confidence": 0.8},
            {"src": "帝国", "dst": "帝国的孩子", "relation": "由之构成", "confidence": 0.8},
            {"src": "金色大厅", "dst": "帝国", "relation": "位于", "confidence": 0.7},
        ],
    },
    # 11) 火炬接力地图 · 城市街角与乌卢鲁
    "2bb92e33f48dab3f": {
        "entities": [
            {"name": "城市街角", "type": "地点", "aliases": []},
            {"name": "火炬护卫队", "type": "组织", "aliases": ["火炬护卫队Ⅴ", "火炬护卫队Ⅵ"]},
            {"name": "火炬", "type": "概念", "aliases": []},
            {"name": "谣言的终结", "type": "事件", "aliases": []},
            {"name": "面对自己", "type": "事件", "aliases": []},
            {"name": "维尔汀的箱子", "type": "物品", "aliases": []},
            {"name": "乌卢鲁运动场", "type": "地点", "aliases": []},
            {"name": "乌卢鲁泉眼", "type": "地点", "aliases": []},
            {"name": "乌卢鲁沙漠", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "火炬护卫队", "dst": "火炬", "relation": "传递", "confidence": 0.8},
            {"src": "城市街角", "dst": "火炬", "relation": "关联", "confidence": 0.7},
            {"src": "面对自己", "dst": "火炬", "relation": "掌握", "confidence": 0.7},
        ],
    },
    # 12) 奇心小姐独白 · 贤道兽与十二摄提神
    "1fe2d4e039f8a613": {
        "entities": [
            {"name": "奇心小姐", "type": "角色", "aliases": []},
            {"name": "强良", "type": "角色", "aliases": []},
            {"name": "教官", "type": "角色", "aliases": []},
            {"name": "贤道兽", "type": "角色", "aliases": ["贤道手"]},
            {"name": "十二摄提神", "type": "角色", "aliases": []},
            {"name": "巫武之礼", "type": "概念", "aliases": []},
            {"name": "恶兽", "type": "角色", "aliases": []},
            {"name": "大贤方乡", "type": "概念", "aliases": []},
            {"name": "天子", "type": "角色", "aliases": []},
            {"name": "邪祟诡异", "type": "概念", "aliases": []},
            {"name": "不速之客", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "奇心小姐", "dst": "强良", "relation": "合作", "confidence": 0.8},
            {"src": "强良", "dst": "贤道兽", "relation": "召唤", "confidence": 0.8},
            {"src": "十二摄提神", "dst": "巫武之礼", "relation": "赐予", "confidence": 0.8},
            {"src": "巫武之礼", "dst": "恶兽", "relation": "降伏", "confidence": 0.8},
            {"src": "贤道兽", "dst": "邪祟诡异", "relation": "驱除", "confidence": 0.8},
            {"src": "大贤方乡", "dst": "天子", "relation": "受祸于", "confidence": 0.7},
            {"src": "天子", "dst": "十二摄提神", "relation": "被请愿", "confidence": 0.7},
            {"src": "奇心小姐", "dst": "不速之客", "relation": "同灭", "confidence": 0.7},
            {"src": "教官", "dst": "奇心小姐", "relation": "质疑", "confidence": 0.7},
        ],
    },
    # 13) 技能页 + 战斗对话 · 至终的仪式与钥匙
    "c6ceb9d509871a9d": {
        "entities": [
            {"name": "至终的仪式", "type": "事件", "aliases": []},
            {"name": "钥匙", "type": "物品", "aliases": []},
        ],
        "relations": [],
    },
    # 14) 珊迪值班表 · 乔治橡树童谣与欧洲树蛙
    "63075ec441139169": {
        "entities": [
            {"name": "珊迪", "type": "角色", "aliases": []},
            {"name": "假期申请", "type": "物品", "aliases": []},
            {"name": "又一个梦Ⅱ", "type": "概念", "aliases": ["小径② 又一个梦Ⅱ"]},
            {"name": "为沉眠者", "type": "概念", "aliases": ["小径① 为沉眠者"]},
            {"name": "欧洲树蛙", "type": "角色", "aliases": []},
            {"name": "拗口的童谣", "type": "概念", "aliases": []},
            {"name": "乔治橡树", "type": "概念", "aliases": []},
            {"name": "橡子", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "珊迪", "dst": "假期申请", "relation": "提交", "confidence": 0.8},
            {"src": "乔治橡树", "dst": "橡子", "relation": "结出", "confidence": 0.8},
            {"src": "拗口的童谣", "dst": "乔治橡树", "relation": "提及", "confidence": 0.8},
            {"src": "拗口的童谣", "dst": "橡子", "relation": "需要", "confidence": 0.8},
            {"src": "又一个梦Ⅱ", "dst": "欧洲树蛙", "relation": "关联", "confidence": 0.7},
        ],
    },
    # 15) 技能页 + 战斗对话 · 《回头是岸》与贝克特
    "f88aadb8a9e287a6": {
        "entities": [
            {"name": "《回头是岸》", "type": "物品", "aliases": []},
            {"name": "贝克特", "type": "角色", "aliases": []},
            {"name": "墨西哥卷", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "贝克特", "dst": "墨西哥卷", "relation": "提供赌注", "confidence": 0.8},
            {"src": "《回头是岸》", "dst": "贝克特", "relation": "主角相似", "confidence": 0.7},
        ],
    },
    # 16) 高原探查独白 · 活水与异常的花石
    "468223df278eda6d": {
        "entities": [
            {"name": "活水", "type": "概念", "aliases": []},
            {"name": "酒精", "type": "物品", "aliases": []},
            {"name": "高原", "type": "地点", "aliases": []},
            {"name": "占卜", "type": "概念", "aliases": []},
            {"name": "刺激", "type": "概念", "aliases": []},
            {"name": "花", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "活水", "dst": "高原", "relation": "发现于", "confidence": 0.7},
            {"src": "占卜", "dst": "高原", "relation": "指向", "confidence": 0.7},
            {"src": "刺激", "dst": "花", "relation": "伴随", "confidence": 0.7},
        ],
    },
    # 17) 异语探查独白 · 阿克林技术与河流
    "a4a1bbdad6331282": {
        "entities": [
            {"name": "阿克林技术", "type": "概念", "aliases": []},
            {"name": "河流", "type": "地点", "aliases": []},
            {"name": "南东", "type": "概念", "aliases": []},
            {"name": "花", "type": "概念", "aliases": []},
            {"name": "石头", "type": "物品", "aliases": []},
            {"name": "流水", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "阿克林技术", "dst": "河流", "relation": "指向", "confidence": 0.7},
            {"src": "河流", "dst": "流水", "relation": "是", "confidence": 0.9},
            {"src": "河流", "dst": "南东", "relation": "位于", "confidence": 0.7},
            {"src": "花", "dst": "石头", "relation": "伴随", "confidence": 0.7},
            {"src": "石头", "dst": "流水", "relation": "被淹没", "confidence": 0.7},
        ],
    },
    # 18) 胶片独白 · 唐人街事件与奇星小姐
    "a022e5f437de290c": {
        "entities": [
            {"name": "圣魂", "type": "概念", "aliases": []},
            {"name": "胶片", "type": "物品", "aliases": ["被诅咒的胶片"]},
            {"name": "奇奇小姐", "type": "角色", "aliases": []},
            {"name": "雷瑟姆小姐", "type": "角色", "aliases": []},
            {"name": "唐人街", "type": "地点", "aliases": []},
            {"name": "香港", "type": "地点", "aliases": []},
            {"name": "菲林士多女士", "type": "角色", "aliases": []},
            {"name": "射火游行", "type": "事件", "aliases": []},
            {"name": "职业人小姐", "type": "角色", "aliases": []},
            {"name": "奇星小姐", "type": "角色", "aliases": []},
            {"name": "孤蚊野鬼", "type": "概念", "aliases": []},
            {"name": "邪物", "type": "概念", "aliases": []},
            {"name": "遗物", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "胶片", "dst": "圣魂", "relation": "吸引", "confidence": 0.8},
            {"src": "雷瑟姆小姐", "dst": "胶片", "relation": "播放", "confidence": 0.8},
            {"src": "胶片", "dst": "唐人街", "relation": "制造受害者于", "confidence": 0.8},
            {"src": "奇星小姐", "dst": "胶片", "relation": "获得", "confidence": 0.8},
            {"src": "职业人小姐", "dst": "胶片", "relation": "控制", "confidence": 0.8},
            {"src": "射火游行", "dst": "胶片", "relation": "关联", "confidence": 0.7},
            {"src": "菲林士多女士", "dst": "胶片", "relation": "关联", "confidence": 0.7},
            {"src": "胶片", "dst": "邪物", "relation": "成为", "confidence": 0.8},
            {"src": "胶片", "dst": "遗物", "relation": "是", "confidence": 0.9},
            {"src": "圣魂", "dst": "孤蚊野鬼", "relation": "吸引", "confidence": 0.7},
            {"src": "香港", "dst": "唐人街", "relation": "关联", "confidence": 0.7},
        ],
    },
    # 19) 论坛灵异帖 · 梅花树阵眼与长生剑
    "fe5b3ab4104857fc": {
        "entities": [
            {"name": "梅花树", "type": "地点", "aliases": ["梅树", "老梅"]},
            {"name": "长发男", "type": "角色", "aliases": []},
            {"name": "阵眼", "type": "概念", "aliases": []},
            {"name": "厉鬼", "type": "角色", "aliases": []},
            {"name": "骡子", "type": "角色", "aliases": []},
            {"name": "公园", "type": "地点", "aliases": []},
            {"name": "祝县", "type": "地点", "aliases": []},
            {"name": "长生剑", "type": "物品", "aliases": []},
            {"name": "官方人员", "type": "角色", "aliases": []},
            {"name": "神秘学事件", "type": "概念", "aliases": []},
            {"name": "梅花", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "梅花树", "dst": "阵眼", "relation": "是", "confidence": 0.8},
            {"src": "梅花树", "dst": "厉鬼", "relation": "镇压", "confidence": 0.8},
            {"src": "长发男", "dst": "厉鬼", "relation": "是", "confidence": 0.8},
            {"src": "骡子", "dst": "公园", "relation": "位于", "confidence": 0.7},
            {"src": "公园", "dst": "官方人员", "relation": "被封锁", "confidence": 0.8},
            {"src": "官方人员", "dst": "神秘学事件", "relation": "调查", "confidence": 0.8},
            {"src": "公园", "dst": "祝县", "relation": "位于", "confidence": 0.7},
            {"src": "长生剑", "dst": "梅花树", "relation": "注入", "confidence": 0.8},
            {"src": "梅花", "dst": "梅花树", "relation": "生长于", "confidence": 0.8},
        ],
    },
    # 20) 陈列室失物报告 · 《"暴雨"清理协议》与重塑之手
    "8209d5b6623541c1": {
        "entities": [
            {"name": "《“暴雨”清理协议》", "type": "物品", "aliases": ["“暴雨”清理协议"]},
            {"name": "暴雨", "type": "现象", "aliases": ["“暴雨”"]},
            {"name": "后勤部门", "type": "组织", "aliases": []},
            {"name": "神秘学藏品管理部", "type": "组织", "aliases": []},
            {"name": "安保科", "type": "组织", "aliases": []},
            {"name": "重塑之手", "type": "组织", "aliases": []},
            {"name": "时代藏品", "type": "概念", "aliases": ["时代艺术藏品", "历史实物藏品"]},
            {"name": "历史生活废料", "type": "概念", "aliases": []},
            {"name": "72小时静置期", "type": "概念", "aliases": ["“72小时静置期”"]},
            {"name": "管理员", "type": "角色", "aliases": []},
            {"name": "监控术式", "type": "概念", "aliases": []},
            {"name": "调查人员", "type": "角色", "aliases": []},
            {"name": "失物", "type": "概念", "aliases": []},
            {"name": "1960-1970年代展区", "type": "地点", "aliases": ["“1960-1970年代”展区"]},
            {"name": "陈列室", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "后勤部门", "dst": "《“暴雨”清理协议》", "relation": "依据", "confidence": 0.8},
            {"src": "《“暴雨”清理协议》", "dst": "暴雨", "relation": "关于", "confidence": 0.9},
            {"src": "陈列室", "dst": "时代藏品", "relation": "遗失", "confidence": 0.8},
            {"src": "后勤部门", "dst": "时代藏品", "relation": "致丢失", "confidence": 0.7},
            {"src": "安保科", "dst": "重塑之手", "relation": "怀疑", "confidence": 0.8},
            {"src": "神秘学藏品管理部", "dst": "时代藏品", "relation": "管理", "confidence": 0.8},
            {"src": "后勤部门", "dst": "72小时静置期", "relation": "设置", "confidence": 0.8},
            {"src": "管理员", "dst": "监控术式", "relation": "调阅", "confidence": 0.8},
            {"src": "调查人员", "dst": "时代藏品", "relation": "评估", "confidence": 0.7},
            {"src": "失物", "dst": "时代藏品", "relation": "优先级低于", "confidence": 0.7},
            {"src": "1960-1970年代展区", "dst": "陈列室", "relation": "属于", "confidence": 0.8},
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
    print(f"[apply-missing-p27] 写入 {len(RESULTS)} 条，NOOP +{len(NOOP_ADD)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
