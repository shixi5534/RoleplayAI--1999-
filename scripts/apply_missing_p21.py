# -*- coding: utf-8 -*-
"""未抽取剧情块补抽 · 第 21 批（backfill2 batch_11，20 块，无纯数值/UI 空块）。

用法：
  python scripts/apply_missing_p21.py            # 预演（悬空+落地自检）
  python scripts/apply_missing_p21.py --apply    # 写盘
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

# 本批 20 块均含剧情片段（块 9ad5baa8599d37ce 为技能页但尾部含乌尔里希对白，已抽取），
# 故无 NOOP 空块。
NOOP_ADD: list[str] = []

RESULTS: dict[str, dict] = {
    # 1) J/玛蒂尔达 情景喜剧 · 不和谐音 · “剃刀”小队
    "076eb3b49ae310ab": {
        "entities": [
            {"name": "玛蒂尔达", "type": "角色", "aliases": []},
            {"name": "情景喜剧", "type": "物品", "aliases": []},
            {"name": "小熊", "type": "物品", "aliases": []},
            {"name": "不和谐音", "type": "概念", "aliases": []},
            {"name": "吉他", "type": "物品", "aliases": []},
            {"name": "黑胶唱片", "type": "物品", "aliases": []},
            {"name": "“剃刀”", "type": "角色", "aliases": []},
            {"name": "“剃刀”小队", "type": "组织", "aliases": []},
            {"name": "“剃刀”小队队员", "type": "角色", "aliases": []},
            {"name": "喷漆罐", "type": "物品", "aliases": []},
            {"name": "乐队", "type": "概念", "aliases": []},
            {"name": "制服", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "玛蒂尔达", "dst": "情景喜剧", "relation": "观看", "confidence": 0.7},
            {"src": "玛蒂尔达", "dst": "小熊", "relation": "怀抱", "confidence": 0.7},
            {"src": "黑胶唱片", "dst": "不和谐音", "relation": "奏出", "confidence": 0.7},
            {"src": "吉他", "dst": "不和谐音", "relation": "奏出", "confidence": 0.7},
            {"src": "“剃刀”小队队员", "dst": "“剃刀”小队", "relation": "隶属", "confidence": 0.8},
            {"src": "“剃刀”", "dst": "“剃刀”小队", "relation": "率领", "confidence": 0.8},
            {"src": "“剃刀”小队队员", "dst": "乐队", "relation": "想绘制", "confidence": 0.7},
            {"src": "“剃刀”小队队员", "dst": "喷漆罐", "relation": "使用", "confidence": 0.7},
            {"src": "“剃刀”小队队员", "dst": "制服", "relation": "顾惜", "confidence": 0.7},
        ],
    },
    # 2) 斯普特尼克/杰洛/贝克特 攒钱飞天 · 乔(=J)与假人
    "6835d83af5759f69": {
        "entities": [
            {"name": "斯普特尼克", "type": "角色", "aliases": []},
            {"name": "杰洛", "type": "角色", "aliases": []},
            {"name": "贝克特", "type": "角色", "aliases": []},
            {"name": "乔", "type": "角色", "aliases": ["J"]},
            {"name": "假人", "type": "角色", "aliases": ["假人模特"]},
            {"name": "最初的伙伴", "type": "概念", "aliases": []},
            {"name": "迪斯科球", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "杰洛", "dst": "斯普特尼克", "relation": "对话", "confidence": 0.7},
            {"src": "贝克特", "dst": "杰洛", "relation": "对话", "confidence": 0.7},
            {"src": "乔", "dst": "假人", "relation": "遇见", "confidence": 0.8},
            {"src": "乔", "dst": "假人", "relation": "帮助", "confidence": 0.7},
            {"src": "假人", "dst": "乔", "relation": "讲述往事", "confidence": 0.7},
            {"src": "最初的伙伴", "dst": "乔", "relation": "关乎", "confidence": 0.7},
        ],
    },
    # 3) 房间监控日志 · 摇篮曲 · “蓝手帕旅馆”事件调查报告
    "216cbed393174a86": {
        "entities": [
            {"name": "102房间", "type": "地点", "aliases": []},
            {"name": "105房间", "type": "地点", "aliases": []},
            {"name": "202房间", "type": "地点", "aliases": []},
            {"name": "摇篮曲", "type": "物品", "aliases": []},
            {"name": "猫头鹰", "type": "角色", "aliases": []},
            {"name": "鼯鼠", "type": "角色", "aliases": []},
            {"name": "黑马儿", "type": "角色", "aliases": []},
            {"name": "谷仓", "type": "地点", "aliases": []},
            {"name": "“蓝手帕旅馆”", "type": "概念", "aliases": ["“旅馆”"]},
            {"name": "蓝手帕", "type": "角色", "aliases": []},
            {"name": "基金会", "type": "组织", "aliases": []},
        ],
        "relations": [
            {"src": "摇篮曲", "dst": "猫头鹰", "relation": "提及", "confidence": 0.7},
            {"src": "摇篮曲", "dst": "鼯鼠", "relation": "提及", "confidence": 0.7},
            {"src": "摇篮曲", "dst": "黑马儿", "relation": "提及", "confidence": 0.7},
            {"src": "摇篮曲", "dst": "谷仓", "relation": "提及", "confidence": 0.7},
            {"src": "基金会", "dst": "“蓝手帕旅馆”", "relation": "接手", "confidence": 0.8},
            {"src": "“蓝手帕旅馆”", "dst": "蓝手帕", "relation": "回应", "confidence": 0.8},
        ],
    },
    # 4) 流水无涯论坛帖 · 奇闻天下松鼠帖
    "6bc623ee1b6d6c7f": {
        "entities": [
            {"name": "流水无涯", "type": "组织", "aliases": []},
            {"name": "一头小毛骡", "type": "角色", "aliases": []},
            {"name": "雪落无声", "type": "角色", "aliases": []},
            {"name": "wa666666", "type": "角色", "aliases": []},
            {"name": "清风徐来", "type": "角色", "aliases": []},
            {"name": "奇闻天下", "type": "概念", "aliases": []},
            {"name": "体育场", "type": "地点", "aliases": []},
            {"name": "松鼠", "type": "角色", "aliases": []},
            {"name": "太爷爷", "type": "角色", "aliases": []},
            {"name": "松果", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "一头小毛骡", "dst": "流水无涯", "relation": "发帖于", "confidence": 0.8},
            {"src": "雪落无声", "dst": "一头小毛骡", "relation": "回复", "confidence": 0.7},
            {"src": "wa666666", "dst": "一头小毛骡", "relation": "支持", "confidence": 0.7},
            {"src": "清风徐来", "dst": "奇闻天下", "relation": "发帖于", "confidence": 0.7},
            {"src": "太爷爷", "dst": "松鼠", "relation": "偶遇", "confidence": 0.7},
            {"src": "太爷爷", "dst": "松果", "relation": "采摘", "confidence": 0.7},
        ],
    },
    # 5) 收藏条目清单 · 听梦话的医生=西格蒙德·弗洛伊德
    "c495e74d12f464ab": {
        "entities": [
            {"name": "小径①", "type": "地点", "aliases": []},
            {"name": "擦鞋童们", "type": "角色", "aliases": []},
            {"name": "维也纳咖啡", "type": "物品", "aliases": []},
            {"name": "枪响前夜", "type": "事件", "aliases": []},
            {"name": "游离在外的小坏蛋", "type": "角色", "aliases": []},
            {"name": "雨天的老朋友", "type": "角色", "aliases": []},
            {"name": "实验记录", "type": "物品", "aliases": []},
            {"name": "沉重的门", "type": "物品", "aliases": []},
            {"name": "资料册", "type": "物品", "aliases": []},
            {"name": "勇士之歌", "type": "物品", "aliases": []},
            {"name": "白信封", "type": "物品", "aliases": []},
            {"name": "听梦话的医生", "type": "角色", "aliases": []},
            {"name": "西格蒙德·弗洛伊德", "type": "角色", "aliases": ["弗洛伊德"]},
            {"name": "“自由联想”", "type": "概念", "aliases": []},
            {"name": "波斯地毯", "type": "物品", "aliases": []},
            {"name": "莎士比亚", "type": "角色", "aliases": []},
            {"name": "雪茄", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "小径①", "dst": "擦鞋童们", "relation": "收录", "confidence": 0.7},
            {"src": "小径①", "dst": "枪响前夜", "relation": "收录", "confidence": 0.7},
            {"src": "听梦话的医生", "dst": "西格蒙德·弗洛伊德", "relation": "是", "confidence": 0.9},
            {"src": "西格蒙德·弗洛伊德", "dst": "“自由联想”", "relation": "使用", "confidence": 0.8},
            {"src": "西格蒙德·弗洛伊德", "dst": "莎士比亚", "relation": "热衷", "confidence": 0.7},
            {"src": "西格蒙德·弗洛伊德", "dst": "雪茄", "relation": "喜爱", "confidence": 0.7},
            {"src": "西格蒙德·弗洛伊德", "dst": "波斯地毯", "relation": "诊室铺设", "confidence": 0.7},
        ],
    },
    # 6) 帝国寓言独白：维也纳/匈牙利/奥地利/波希米亚/摩拉维亚
    "5d1d0e0ebe34de58": {
        "entities": [
            {"name": "维也纳", "type": "地点", "aliases": []},
            {"name": "匈牙利", "type": "地点", "aliases": []},
            {"name": "奥地利", "type": "地点", "aliases": []},
            {"name": "波希米亚", "type": "地点", "aliases": []},
            {"name": "摩拉维亚", "type": "地点", "aliases": []},
            {"name": "神秘学家", "type": "概念", "aliases": []},
            {"name": "中央政府", "type": "组织", "aliases": []},
            {"name": "帝国", "type": "组织", "aliases": []},
            {"name": "慈善舞会", "type": "事件", "aliases": []},
        ],
        "relations": [
            {"src": "匈牙利", "dst": "奥地利", "relation": "共筑", "confidence": 0.8},
            {"src": "匈牙利", "dst": "中央政府", "relation": "共筑", "confidence": 0.8},
            {"src": "帝国", "dst": "匈牙利", "relation": "包含", "confidence": 0.7},
            {"src": "帝国", "dst": "奥地利", "relation": "包含", "confidence": 0.7},
            {"src": "帝国", "dst": "波希米亚", "relation": "包含", "confidence": 0.7},
            {"src": "帝国", "dst": "摩拉维亚", "relation": "包含", "confidence": 0.7},
            {"src": "慈善舞会", "dst": "维也纳", "relation": "举办于", "confidence": 0.7},
            {"src": "神秘学家", "dst": "帝国", "relation": "同处边缘", "confidence": 0.7},
        ],
    },
    # 7) 勋章/金色大厅/十一位孩子 · 友好交流字条(绿鹦鹉/亚诺什) · 破镜中的残影 ·《维也纳日报》
    "3552cfa6f87cd5c1": {
        "entities": [
            {"name": "勋章", "type": "物品", "aliases": []},
            {"name": "金色大厅", "type": "地点", "aliases": []},
            {"name": "十一位孩子", "type": "角色", "aliases": []},
            {"name": "友好交流", "type": "物品", "aliases": []},
            {"name": "绿鸟儿", "type": "角色", "aliases": ["绿鹦鹉"]},
            {"name": "镜子", "type": "物品", "aliases": []},
            {"name": "“术杖”", "type": "物品", "aliases": []},
            {"name": "亚诺什", "type": "角色", "aliases": []},
            {"name": "蓝色条纹裤", "type": "物品", "aliases": []},
            {"name": "暴发户", "type": "概念", "aliases": []},
            {"name": "破镜中的残影", "type": "概念", "aliases": []},
            {"name": "《维也纳日报》", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "金色大厅", "dst": "十一位孩子", "relation": "欢歌压过啼哭", "confidence": 0.7},
            {"src": "友好交流", "dst": "绿鹦鹉", "relation": "斥责", "confidence": 0.8},
            {"src": "绿鹦鹉", "dst": "镜子", "relation": "摆弄", "confidence": 0.8},
            {"src": "镜子", "dst": "“术杖”", "relation": "被称", "confidence": 0.7},
            {"src": "亚诺什", "dst": "蓝色条纹裤", "relation": "穿着", "confidence": 0.7},
            {"src": "破镜中的残影", "dst": "镜子", "relation": "源自", "confidence": 0.7},
        ],
    },
    # 8) 伙伴集结反攻 · 诺谛卡/“剃刀”/重塑之手清理
    "c40c6d92d2dc9ec9": {
        "entities": [
            {"name": "格鲁托夫", "type": "角色", "aliases": []},
            {"name": "诺谛卡", "type": "角色", "aliases": []},
            {"name": '"剃刀"', "type": "角色", "aliases": []},
            {"name": "阿尔卡纳", "type": "角色", "aliases": []},
            {"name": "小春雀儿", "type": "角色", "aliases": []},
            {"name": "星锑", "type": "角色", "aliases": []},
            {"name": "APPLe", "type": "角色", "aliases": []},
            {"name": "槲寄生", "type": "角色", "aliases": []},
            {"name": "虚构集", "type": "角色", "aliases": []},
            {"name": "重塑之手", "type": "组织", "aliases": []},
            {"name": "收藏品", "type": "物品", "aliases": []},
            {"name": "空运来的软盘", "type": "物品", "aliases": []},
            {"name": "歌唱家", "type": "角色", "aliases": []},
            {"name": "绀紫腕", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "格鲁托夫", "dst": "阿尔卡纳", "relation": "提及", "confidence": 0.7},
            {"src": "诺谛卡", "dst": "阿尔卡纳", "relation": "询问", "confidence": 0.7},
            {"src": "诺谛卡", "dst": "小春雀儿", "relation": "搭载", "confidence": 0.7},
            {"src": "槲寄生", "dst": "重塑之手", "relation": "提及", "confidence": 0.8},
            {"src": '"剃刀"', "dst": "重塑之手", "relation": "清剿", "confidence": 0.8},
            {"src": "小春雀儿", "dst": "虚构集", "relation": "提醒", "confidence": 0.7},
            {"src": "虚构集", "dst": "收藏品", "relation": "保护", "confidence": 0.8},
            {"src": "空运来的软盘", "dst": "歌唱家", "relation": "来自", "confidence": 0.7},
            {"src": "绀紫腕", "dst": "歌唱家", "relation": "接应", "confidence": 0.7},
        ],
    },
    # 9) 追悼会 · 来自“无名者”的案件调查报告(雨前调度中心/暴雨/重塑之手)
    "a86ee3de7eb4eeb2": {
        "entities": [
            {"name": "追悼会", "type": "事件", "aliases": []},
            {"name": "临时校长", "type": "角色", "aliases": []},
            {"name": "金线", "type": "概念", "aliases": []},
            {"name": "健忘症", "type": "概念", "aliases": []},
            {"name": "宝贝箱子", "type": "物品", "aliases": []},
            {"name": "救世主", "type": "概念", "aliases": []},
            {"name": "袭击策略", "type": "概念", "aliases": []},
            {"name": "“无名者”", "type": "角色", "aliases": []},
            {"name": "雨前调度中心", "type": "组织", "aliases": []},
            {"name": "临时调查委员会", "type": "组织", "aliases": []},
            {"name": "“暴雨”", "type": "现象", "aliases": []},
            {"name": "重塑之手", "type": "组织", "aliases": []},
            {"name": "袭击者", "type": "组织", "aliases": []},
            {"name": "基金会总部", "type": "组织", "aliases": []},
            {"name": "第一防线学校", "type": "组织", "aliases": []},
        ],
        "relations": [
            {"src": "追悼会", "dst": "临时校长", "relation": "关联", "confidence": 0.7},
            {"src": "追悼会", "dst": "金线", "relation": "累积", "confidence": 0.7},
            {"src": "雨前调度中心", "dst": "临时调查委员会", "relation": "联合授权", "confidence": 0.8},
            {"src": "重塑之手", "dst": "袭击者", "relation": "是", "confidence": 0.9},
            {"src": "重塑之手", "dst": "第一防线学校", "relation": "袭击", "confidence": 0.9},
            {"src": "重塑之手", "dst": "“暴雨”", "relation": "于前夕袭击", "confidence": 0.8},
            {"src": "“无名者”", "dst": "袭击者", "relation": "案件指向", "confidence": 0.7},
            {"src": "基金会总部", "dst": "第一防线学校", "relation": "辖属", "confidence": 0.8},
        ],
    },
    # 10) 责任制对话(小格蕾丝/蛇影/魅魔) · “人工暴雨”实验录像
    "72cb152f5739cee4": {
        "entities": [
            {"name": "责任制", "type": "概念", "aliases": []},
            {"name": "小格蕾丝", "type": "角色", "aliases": []},
            {"name": "蛇影", "type": "角色", "aliases": []},
            {"name": "米修斯", "type": "角色", "aliases": []},
            {"name": "魅魔", "type": "角色", "aliases": []},
            {"name": "契约物", "type": "物品", "aliases": []},
            {"name": "金伯利", "type": "角色", "aliases": []},
            {"name": "德克萨斯", "type": "地点", "aliases": []},
            {"name": "伊戈尔", "type": "角色", "aliases": []},
            {"name": "努库泰澳人", "type": "组织", "aliases": []},
            {"name": "‘象形贝壳’", "type": "物品", "aliases": []},
            {"name": "维尔汀", "type": "角色", "aliases": []},
            {"name": "“人工暴雨”", "type": "现象", "aliases": []},
            {"name": "录像带", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "小格蕾丝", "dst": "蛇影", "relation": "受教", "confidence": 0.8},
            {"src": "契约物", "dst": "魅魔", "relation": "控制", "confidence": 0.8},
            {"src": "小格蕾丝", "dst": "米修斯", "relation": "不同", "confidence": 0.7},
            {"src": "金伯利", "dst": "契约物", "relation": "致失", "confidence": 0.7},
            {"src": "伊戈尔", "dst": "契约物", "relation": "弄丢", "confidence": 0.7},
            {"src": "努库泰澳人", "dst": "‘象形贝壳’", "relation": "献上", "confidence": 0.8},
            {"src": "蛇影", "dst": "维尔汀", "relation": "关注", "confidence": 0.8},
            {"src": "“人工暴雨”", "dst": "录像带", "relation": "录于", "confidence": 0.8},
        ],
    },
    # 11) 身体指挥部寓言 · 地母故事集
    "214c93b7bdbb7960": {
        "entities": [
            {"name": "大脑指挥部", "type": "概念", "aliases": []},
            {"name": "副指挥部", "type": "概念", "aliases": []},
            {"name": "心脏", "type": "概念", "aliases": []},
            {"name": "关隘道口", "type": "概念", "aliases": []},
            {"name": "文艺复兴", "type": "概念", "aliases": []},
            {"name": "米开朗基罗", "type": "角色", "aliases": []},
            {"name": "户外实验", "type": "事件", "aliases": []},
            {"name": "外骨骼", "type": "物品", "aliases": []},
            {"name": "童话的背面", "type": "概念", "aliases": []},
            {"name": "地母故事集", "type": "物品", "aliases": []},
            {"name": "地母", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "大脑指挥部", "dst": "副指挥部", "relation": "设置", "confidence": 0.7},
            {"src": "米开朗基罗", "dst": "文艺复兴", "relation": "属于", "confidence": 0.7},
            {"src": "户外实验", "dst": "外骨骼", "relation": "建议配备", "confidence": 0.7},
            {"src": "地母故事集", "dst": "地母", "relation": "记载", "confidence": 0.8},
        ],
    },
    # 12) 失真/救世主 · 电台旁讨论(‘差分机’小队/‘钨丝’小队/奥匈帝国)
    "1276be547d25fb9f": {
        "entities": [
            {"name": "救世主", "type": "概念", "aliases": []},
            {"name": "橙色小狗", "type": "角色", "aliases": []},
            {"name": "帽子", "type": "物品", "aliases": []},
            {"name": "失真", "type": "概念", "aliases": []},
            {"name": "‘差分机’小队", "type": "组织", "aliases": []},
            {"name": "总部", "type": "组织", "aliases": []},
            {"name": "阿尔卡纳", "type": "角色", "aliases": []},
            {"name": "‘钨丝’小队", "type": "组织", "aliases": []},
            {"name": "委外合约小队", "type": "组织", "aliases": []},
            {"name": "皇家邮轮", "type": "物品", "aliases": []},
            {"name": "潜艇", "type": "物品", "aliases": []},
            {"name": "协约国", "type": "组织", "aliases": []},
            {"name": "霍尔韦格", "type": "角色", "aliases": []},
            {"name": "凡尔登战役", "type": "事件", "aliases": []},
            {"name": "奥匈帝国", "type": "组织", "aliases": []},
            {"name": "奥斯曼", "type": "组织", "aliases": []},
            {"name": "重塑之手", "type": "组织", "aliases": []},
            {"name": "神秘学家", "type": "概念", "aliases": []},
            {"name": "基金会通讯员", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "橙色小狗", "dst": "帽子", "relation": "捡回", "confidence": 0.8},
            {"src": "‘差分机’小队", "dst": "总部", "relation": "隶属", "confidence": 0.8},
            {"src": "‘差分机’小队", "dst": "‘钨丝’小队", "relation": "会合", "confidence": 0.8},
            {"src": "阿尔卡纳", "dst": "‘差分机’小队", "relation": "不在辖区", "confidence": 0.7},
            {"src": "委外合约小队", "dst": "总部", "relation": "失联", "confidence": 0.7},
            {"src": "皇家邮轮", "dst": "潜艇", "relation": "遭袭", "confidence": 0.8},
            {"src": "协约国", "dst": "皇家邮轮", "relation": "救援", "confidence": 0.7},
            {"src": "奥匈帝国", "dst": "凡尔登战役", "relation": "经历", "confidence": 0.7},
            {"src": "重塑之手", "dst": "奥匈帝国", "relation": "介入战事", "confidence": 0.7},
            {"src": "基金会通讯员", "dst": "神秘学家", "relation": "记录讨论", "confidence": 0.7},
        ],
    },
    # 13) 技能页尾部含乌尔里希对白（电台）——抽剧情片段
    "9ad5baa8599d37ce": {
        "entities": [
            {"name": "乌尔里希", "type": "角色", "aliases": []},
            {"name": "电台", "type": "物品", "aliases": ["宝贝电台"]},
        ],
        "relations": [
            {"src": "乌尔里希", "dst": "电台", "relation": "持有备用", "confidence": 0.7},
        ],
    },
    # 14) 白乳菇研究 · 沾满灰尘的门票(澳式橄榄球) · 像素鸸鹋日记
    "9ce3c5c644deb008": {
        "entities": [
            {"name": "白乳菇", "type": "物品", "aliases": []},
            {"name": "神秘学家", "type": "概念", "aliases": []},
            {"name": "沾满灰尘的门票", "type": "物品", "aliases": []},
            {"name": "澳式橄榄球", "type": "概念", "aliases": []},
            {"name": "霍巴特蓝湖队", "type": "组织", "aliases": []},
            {"name": "像素鸸鹋", "type": "角色", "aliases": []},
            {"name": "鸸鹋", "type": "角色", "aliases": []},
            {"name": "市政员工", "type": "角色", "aliases": []},
            {"name": "日记", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "白乳菇", "dst": "神秘学家", "relation": "可作补给", "confidence": 0.7},
            {"src": "沾满灰尘的门票", "dst": "澳式橄榄球", "relation": "属于", "confidence": 0.8},
            {"src": "霍巴特蓝湖队", "dst": "澳式橄榄球", "relation": "参赛", "confidence": 0.7},
            {"src": "市政员工", "dst": "像素鸸鹋", "relation": "表扬", "confidence": 0.8},
            {"src": "市政员工", "dst": "鸸鹋", "relation": "共事", "confidence": 0.7},
            {"src": "日记", "dst": "市政员工", "relation": "属于", "confidence": 0.8},
        ],
    },
    # 15) 肉瘤/风城寓言 · 漫漫长夜旅行(天主教的葬礼)
    "a8ff04e9b9f3f748": {
        "entities": [
            {"name": "勿忘我", "type": "角色", "aliases": []},
            {"name": "风城", "type": "地点", "aliases": []},
            {"name": "肉瘤", "type": "概念", "aliases": []},
            {"name": "舞台", "type": "概念", "aliases": []},
            {"name": "小径①", "type": "地点", "aliases": []},
            {"name": "漫漫长夜旅行", "type": "事件", "aliases": []},
            {"name": "天主教的葬礼", "type": "事件", "aliases": []},
        ],
        "relations": [
            {"src": "勿忘我", "dst": "风城", "relation": "被嘱托", "confidence": 0.7},
            {"src": "肉瘤", "dst": "风城", "relation": "喻指", "confidence": 0.8},
            {"src": "小径①", "dst": "漫漫长夜旅行", "relation": "收录", "confidence": 0.8},
            {"src": "漫漫长夜旅行", "dst": "天主教的葬礼", "relation": "包含", "confidence": 0.8},
            {"src": "舞台", "dst": "肉瘤", "relation": "搭建于", "confidence": 0.7},
        ],
    },
    # 16) 弥撒/斯奈德 · 苏芙比的药剂 · 森林中的魔精 · 堵截车队(圣洛夫基金会/重塑之手)
    "60dabd753e6b876b": {
        "entities": [
            {"name": "弥撒", "type": "事件", "aliases": []},
            {"name": "主祭者", "type": "角色", "aliases": []},
            {"name": "斯奈德", "type": "角色", "aliases": []},
            {"name": "苏芙比的药剂", "type": "物品", "aliases": []},
            {"name": "苏芙比", "type": "角色", "aliases": []},
            {"name": "美味嚼嚼幻剂Ⅱ", "type": "物品", "aliases": []},
            {"name": "森林中的魔精", "type": "角色", "aliases": []},
            {"name": "焦木林", "type": "地点", "aliases": []},
            {"name": "小径①", "type": "地点", "aliases": []},
            {"name": "堵截车队·一", "type": "事件", "aliases": []},
            {"name": "堵截车队·二", "type": "事件", "aliases": []},
            {"name": "堵截车队·三", "type": "事件", "aliases": []},
            {"name": "圣洛夫基金会", "type": "组织", "aliases": []},
            {"name": "重塑之手", "type": "组织", "aliases": []},
            {"name": "物资车队", "type": "物品", "aliases": []},
            {"name": "清理小队", "type": "组织", "aliases": []},
            {"name": "《基金会作战规范手册》", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "斯奈德", "dst": "弥撒", "relation": "回应", "confidence": 0.8},
            {"src": "主祭者", "dst": "弥撒", "relation": "主持", "confidence": 0.8},
            {"src": "苏芙比", "dst": "苏芙比的药剂", "relation": "提供", "confidence": 0.9},
            {"src": "苏芙比的药剂", "dst": "美味嚼嚼幻剂Ⅱ", "relation": "含有", "confidence": 0.8},
            {"src": "森林中的魔精", "dst": "焦木林", "relation": "出没于", "confidence": 0.8},
            {"src": "小径①", "dst": "苏芙比的药剂", "relation": "收录", "confidence": 0.7},
            {"src": "圣洛夫基金会", "dst": "清理小队", "relation": "派遣", "confidence": 0.8},
            {"src": "圣洛夫基金会", "dst": "重塑之手", "relation": "拦截", "confidence": 0.9},
            {"src": "清理小队", "dst": "物资车队", "relation": "截获", "confidence": 0.8},
            {"src": "堵截车队·一", "dst": "圣洛夫基金会", "relation": "出自", "confidence": 0.8},
        ],
    },
    # 17) 清剿收尾 · 斗犬之隔(雾气/红羽毛/斯奈德/德鲁伊/芝加哥物资)
    "b37c222b9f5d9f40": {
        "entities": [
            {"name": "清理小队", "type": "组织", "aliases": []},
            {"name": "重塑之手", "type": "组织", "aliases": []},
            {"name": "物资车队", "type": "物品", "aliases": []},
            {"name": "《基金会作战规范手册》", "type": "物品", "aliases": []},
            {"name": "小径④", "type": "地点", "aliases": []},
            {"name": "斗犬之隔", "type": "概念", "aliases": []},
            {"name": "雾气", "type": "现象", "aliases": []},
            {"name": "斗犬", "type": "概念", "aliases": []},
            {"name": "红羽毛", "type": "物品", "aliases": []},
            {"name": "斯奈德", "type": "角色", "aliases": []},
            {"name": "德鲁伊", "type": "角色", "aliases": []},
            {"name": "木箱子", "type": "物品", "aliases": []},
            {"name": "棉花", "type": "物品", "aliases": []},
            {"name": "黄油", "type": "物品", "aliases": []},
            {"name": "面粉", "type": "物品", "aliases": []},
            {"name": "蔗糖", "type": "物品", "aliases": []},
            {"name": "黑狗", "type": "角色", "aliases": []},
            {"name": "芝加哥", "type": "地点", "aliases": []},
            {"name": "绸缎", "type": "物品", "aliases": []},
            {"name": "宝石", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "清理小队", "dst": "物资车队", "relation": "截获", "confidence": 0.8},
            {"src": "清理小队", "dst": "《基金会作战规范手册》", "relation": "依此核验", "confidence": 0.8},
            {"src": "雾气", "dst": "斗犬", "relation": "隔开", "confidence": 0.7},
            {"src": "斯奈德", "dst": "红羽毛", "relation": "伴随之物", "confidence": 0.7},
            {"src": "德鲁伊", "dst": "斯奈德", "relation": "被窃语", "confidence": 0.7},
            {"src": "黑狗", "dst": "黄油", "relation": "转运", "confidence": 0.7},
            {"src": "黑狗", "dst": "面粉", "relation": "转运", "confidence": 0.7},
            {"src": "黑狗", "dst": "蔗糖", "relation": "转运", "confidence": 0.7},
            {"src": "黑狗", "dst": "芝加哥", "relation": "运往", "confidence": 0.7},
            {"src": "木箱子", "dst": "棉花", "relation": "仅装", "confidence": 0.7},
        ],
    },
    # 18) 圣洛夫基金会/迷雾 · 酒馆老板制雾 · 摇滚女孩儿/红果子
    "66a2b4108489470f": {
        "entities": [
            {"name": "圣洛夫基金会", "type": "组织", "aliases": []},
            {"name": "重塑之手", "type": "组织", "aliases": []},
            {"name": "迷雾", "type": "现象", "aliases": ["雾气"]},
            {"name": "致幻", "type": "概念", "aliases": []},
            {"name": "摇滚女孩儿", "type": "角色", "aliases": []},
            {"name": "红果子", "type": "物品", "aliases": []},
            {"name": "沉睡之城", "type": "地点", "aliases": []},
            {"name": "奇迹的小狗", "type": "角色", "aliases": []},
            {"name": "酒馆老板", "type": "角色", "aliases": []},
            {"name": "大坩埚", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "圣洛夫基金会", "dst": "重塑之手", "relation": "察觉行动", "confidence": 0.8},
            {"src": "圣洛夫基金会", "dst": "迷雾", "relation": "逼近", "confidence": 0.7},
            {"src": "酒馆老板", "dst": "迷雾", "relation": "制作", "confidence": 0.9},
            {"src": "迷雾", "dst": "致幻", "relation": "具有效用", "confidence": 0.7},
            {"src": "摇滚女孩儿", "dst": "红果子", "relation": "同行携带", "confidence": 0.7},
            {"src": "奇迹的小狗", "dst": "沉睡之城", "relation": "比喻", "confidence": 0.7},
        ],
    },
    # 19) 仪式/波吕斐摩斯与奥德修斯 · 协理者的记录(玛尔塔/210/苏菲亚)
    "aa36d5d8e06c9869": {
        "entities": [
            {"name": "仪式", "type": "事件", "aliases": []},
            {"name": "试炼", "type": "事件", "aliases": []},
            {"name": "牛犊", "type": "物品", "aliases": []},
            {"name": "火堆", "type": "物品", "aliases": []},
            {"name": "波吕斐摩斯", "type": "角色", "aliases": []},
            {"name": "奥德修斯", "type": "角色", "aliases": []},
            {"name": "巨人", "type": "角色", "aliases": []},
            {"name": "协理者的记录", "type": "物品", "aliases": []},
            {"name": "玛尔塔", "type": "角色", "aliases": []},
            {"name": "沙滩", "type": "地点", "aliases": []},
            {"name": "游记", "type": "物品", "aliases": []},
            {"name": "210", "type": "角色", "aliases": []},
            {"name": "苏菲亚", "type": "角色", "aliases": []},
            {"name": "牺牲", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "波吕斐摩斯", "dst": "奥德修斯", "relation": "询问", "confidence": 0.8},
            {"src": "奥德修斯", "dst": "巨人", "relation": "逃离", "confidence": 0.8},
            {"src": "仪式", "dst": "试炼", "relation": "包含", "confidence": 0.7},
            {"src": "仪式", "dst": "牛犊", "relation": "献祭", "confidence": 0.7},
            {"src": "仪式", "dst": "火堆", "relation": "围绕", "confidence": 0.7},
            {"src": "协理者的记录", "dst": "玛尔塔", "relation": "记录", "confidence": 0.8},
            {"src": "玛尔塔", "dst": "游记", "relation": "撰写", "confidence": 0.7},
            {"src": "协理者的记录", "dst": "210", "relation": "提及", "confidence": 0.7},
            {"src": "协理者的记录", "dst": "苏菲亚", "relation": "提及", "confidence": 0.7},
            {"src": "仪式", "dst": "牺牲", "relation": "需要", "confidence": 0.7},
        ],
    },
    # 20) 镜子两面/兄妹 · 诊断记录——意识唤醒者(露西)
    "687402392003b023": {
        "entities": [
            {"name": "镜子", "type": "物品", "aliases": []},
            {"name": "污点", "type": "概念", "aliases": []},
            {"name": "污渍", "type": "概念", "aliases": []},
            {"name": "裂痕", "type": "概念", "aliases": []},
            {"name": "大手术", "type": "概念", "aliases": []},
            {"name": "术后创伤", "type": "概念", "aliases": []},
            {"name": "诊断记录——意识唤醒者", "type": "物品", "aliases": []},
            {"name": "露西", "type": "角色", "aliases": []},
            {"name": "X光扫描", "type": "物品", "aliases": []},
            {"name": "显影术", "type": "概念", "aliases": []},
            {"name": "透视术", "type": "概念", "aliases": []},
            {"name": "磁力感应检查", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "镜子", "dst": "污渍", "relation": "映现", "confidence": 0.7},
            {"src": "污点", "dst": "污渍", "relation": "转为", "confidence": 0.7},
            {"src": "大手术", "dst": "术后创伤", "relation": "引发", "confidence": 0.7},
            {"src": "诊断记录——意识唤醒者", "dst": "露西", "relation": "对象", "confidence": 0.9},
            {"src": "诊断记录——意识唤醒者", "dst": "X光扫描", "relation": "含项目", "confidence": 0.8},
            {"src": "诊断记录——意识唤醒者", "dst": "显影术", "relation": "含项目", "confidence": 0.8},
            {"src": "诊断记录——意识唤醒者", "dst": "透视术", "relation": "含项目", "confidence": 0.8},
            {"src": "诊断记录——意识唤醒者", "dst": "磁力感应检查", "relation": "含项目", "confidence": 0.8},
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
        # 别名不可与正名相同
        for e in d.get("entities") or []:
            if e.get("name") in (e.get("aliases") or []):
                print(f"[alias_self_ref] {h} entity={e.get('name')}")
                bad += 1
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
    empty = sum(1 for d in RESULTS.values() if not (d.get("entities") or d.get("relations")))
    print(f"[validate] 块 {len(RESULTS)}（NOOP {empty}），悬空 {n}，未落地 {m}")
    print(f"[stats] 非空块 {nonempty}，实体 {total_e}，关系 {total_r}")

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
    print(f"[apply-missing-p21] 写入 {len(RESULTS)} 条，NOOP +{len(NOOP_ADD)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
