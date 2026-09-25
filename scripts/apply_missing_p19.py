# -*- coding: utf-8 -*-
"""未抽取剧情块补抽 · 第 19 批（backfill2 batch_09，20 块，全部有剧情）。

用法：
  python scripts/apply_missing_p19.py            # 预演（悬空+落地自检）
  python scripts/apply_missing_p19.py --apply    # 写盘
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

# 本批 20 块均含剧情，无 NOOP。
NOOP_ADD: list[str] = []

RESULTS: dict[str, dict] = {
    # 1) 多瑙黎明号乘客登记笔记 · 索尼娅/阿不思诺
    "2464cf584cef7e97": {
        "entities": [
            {"name": "多瑙黎明号", "type": "物品", "aliases": []},
            {"name": "维也纳-潘诺尼亚运输公司", "type": "组织", "aliases": []},
            {"name": "索尼娅", "type": "角色", "aliases": []},
            {"name": "阿不思诺", "type": "角色", "aliases": []},
            {"name": "乘客信息登记笔记", "type": "物品", "aliases": []},
            {"name": "多瑙河", "type": "地点", "aliases": []},
            {"name": "铁路", "type": "物品", "aliases": []},
            {"name": "石油", "type": "物品", "aliases": []},
            {"name": "战争", "type": "概念", "aliases": []},
            {"name": "血食怪眷属说", "type": "概念", "aliases": []},
            {"name": "无主之“歌”", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "索尼娅", "dst": "多瑙黎明号", "relation": "登乘", "confidence": 0.8},
            {"src": "阿不思诺", "dst": "铁路", "relation": "投资", "confidence": 0.8},
            {"src": "阿不思诺", "dst": "石油", "relation": "投资", "confidence": 0.8},
            {"src": "维也纳-潘诺尼亚运输公司", "dst": "多瑙黎明号", "relation": "翻修", "confidence": 0.8},
            {"src": "多瑙黎明号", "dst": "多瑙河", "relation": "沿行", "confidence": 0.7},
            {"src": "战争", "dst": "索尼娅", "relation": "影响", "confidence": 0.7},
            {"src": "战争", "dst": "阿不思诺", "relation": "影响", "confidence": 0.7},
            {"src": "血食怪眷属说", "dst": "多瑙黎明号", "relation": "涉及", "confidence": 0.7},
            {"src": "乘客信息登记笔记", "dst": "索尼娅", "relation": "记录", "confidence": 0.7},
            {"src": "乘客信息登记笔记", "dst": "阿不思诺", "relation": "记录", "confidence": 0.7},
        ],
    },
    # 2) 无名童谣 + 游击队对话（伊格丽卡/鲍里斯）
    "8824bde7f8f15c5f": {
        "entities": [
            {"name": "无名童谣", "type": "概念", "aliases": []},
            {"name": "伊格丽卡", "type": "角色", "aliases": []},
            {"name": "鲍里斯", "type": "角色", "aliases": []},
            {"name": "游击队", "type": "组织", "aliases": ["家"]},
            {"name": "联合与希望", "type": "概念", "aliases": []},
            {"name": "解放阵线", "type": "组织", "aliases": []},
            {"name": "血的使者", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "鲍里斯", "dst": "游击队", "relation": "加入", "confidence": 0.9},
            {"src": "伊格丽卡", "dst": "游击队", "relation": "属于", "confidence": 0.8},
            {"src": "游击队", "dst": "联合与希望", "relation": "秉持", "confidence": 0.8},
            {"src": "联合与希望", "dst": "解放阵线", "relation": "属于", "confidence": 0.8},
            {"src": "伊格丽卡", "dst": "鲍里斯", "relation": "接纳", "confidence": 0.8},
            {"src": "鲍里斯", "dst": "伊格丽卡", "relation": "对话", "confidence": 0.7},
            {"src": "血的使者", "dst": "无名童谣", "relation": "出现于", "confidence": 0.7},
        ],
    },
    # 3) “歌声”效应研究 + 染血0073-MV任务笔记（塞梅尔维斯/七十七分队）
    "6bb30eb56055d4bf": {
        "entities": [
            {"name": "歌声", "type": "概念", "aliases": []},
            {"name": "感染种", "type": "概念", "aliases": []},
            {"name": "染血0073-MV", "type": "物品", "aliases": []},
            {"name": "塞梅尔维斯", "type": "角色", "aliases": []},
            {"name": "七十七分队", "type": "组织", "aliases": []},
            {"name": "神秘列车", "type": "物品", "aliases": []},
            {"name": "血食怪", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "歌声", "dst": "感染种", "relation": "增加转化概率", "confidence": 0.8},
            {"src": "塞梅尔维斯", "dst": "七十七分队", "relation": "加入", "confidence": 0.8},
            {"src": "七十七分队", "dst": "神秘列车", "relation": "调查", "confidence": 0.7},
            {"src": "神秘列车", "dst": "血食怪", "relation": "关联", "confidence": 0.7},
            {"src": "塞梅尔维斯", "dst": "染血0073-MV", "relation": "涉及", "confidence": 0.7},
        ],
    },
    # 4) 替海关做事（圆环/脉轮） + 玛蒂尔达/J幕后花絮（情景喜剧）
    "ed25edd1db83db9f": {
        "entities": [
            {"name": "铁圆环", "type": "物品", "aliases": []},
            {"name": "脉轮", "type": "概念", "aliases": []},
            {"name": "老大", "type": "角色", "aliases": []},
            {"name": "环刃", "type": "物品", "aliases": []},
            {"name": "汽油", "type": "物品", "aliases": []},
            {"name": "新纪元集市", "type": "地点", "aliases": []},
            {"name": "玛蒂尔达", "type": "角色", "aliases": []},
            {"name": "保利娜", "type": "角色", "aliases": ["保利娜小姐"]},
            {"name": "情景喜剧", "type": "概念", "aliases": []},
            {"name": "法国", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "老大", "dst": "脉轮", "relation": "沉迷", "confidence": 0.8},
            {"src": "老大", "dst": "环刃", "relation": "索要", "confidence": 0.8},
            {"src": "老大", "dst": "汽油", "relation": "索要", "confidence": 0.8},
            {"src": "玛蒂尔达", "dst": "法国", "relation": "交换留学", "confidence": 0.7},
            {"src": "玛蒂尔达", "dst": "保利娜", "relation": "提及", "confidence": 0.7},
            {"src": "保利娜", "dst": "法国", "relation": "来自", "confidence": 0.7},
            {"src": "玛蒂尔达", "dst": "情景喜剧", "relation": "提及", "confidence": 0.7},
        ],
    },
    # 5) 圣诞礼物回忆 + 环状水星/J疗愈对话
    "38818d86979041bd": {
        "entities": [
            {"name": "妈妈", "type": "角色", "aliases": []},
            {"name": "大个子", "type": "角色", "aliases": []},
            {"name": "蓝丝巾", "type": "物品", "aliases": []},
            {"name": "海特街", "type": "地点", "aliases": []},
            {"name": "小熊", "type": "物品", "aliases": []},
            {"name": "蛋糕", "type": "物品", "aliases": []},
            {"name": "环状水星", "type": "角色", "aliases": []},
            {"name": "圣诞礼物", "type": "物品", "aliases": []},
            {"name": "冥想会", "type": "事件", "aliases": []},
            {"name": "能量", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "大个子", "dst": "蓝丝巾", "relation": "赠送", "confidence": 0.8},
            {"src": "圣诞礼物", "dst": "蓝丝巾", "relation": "包含", "confidence": 0.7},
            {"src": "环状水星", "dst": "冥想会", "relation": "主持", "confidence": 0.8},
            {"src": "环状水星", "dst": "能量", "relation": "感知", "confidence": 0.7},
            {"src": "环状水星", "dst": "海特街", "relation": "关切", "confidence": 0.7},
        ],
    },
    # 6) 玛蒂尔达/斯普特尼克灯球 + 玛蒂尔达/环状水星宇宙能量对话
    "f1fe20b1456fef0f": {
        "entities": [
            {"name": "玛蒂尔达", "type": "角色", "aliases": []},
            {"name": "斯普特尼克", "type": "角色", "aliases": []},
            {"name": "灯球", "type": "物品", "aliases": []},
            {"name": "环状水星", "type": "角色", "aliases": []},
            {"name": "宇宙能量", "type": "概念", "aliases": []},
            {"name": "涟漪", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "玛蒂尔达", "dst": "斯普特尼克", "relation": "探查", "confidence": 0.7},
            {"src": "玛蒂尔达", "dst": "灯球", "relation": "误认", "confidence": 0.7},
            {"src": "斯普特尼克", "dst": "灯球", "relation": "是", "confidence": 0.8},
            {"src": "玛蒂尔达", "dst": "环状水星", "relation": "询问", "confidence": 0.8},
            {"src": "环状水星", "dst": "宇宙能量", "relation": "展示", "confidence": 0.8},
            {"src": "环状水星", "dst": "涟漪", "relation": "感知", "confidence": 0.7},
        ],
    },
    # 7) 问责记录（莫莉德尔/伊戈尔将军） + 小镇故事日记（皮尔斯/玛丽塔）
    "7fc8a434417bcefe": {
        "entities": [
            {"name": "莫莉德尔", "type": "角色", "aliases": []},
            {"name": "伊戈尔将军", "type": "角色", "aliases": ["伊戈尔"]},
            {"name": "副官", "type": "角色", "aliases": []},
            {"name": "上尉L.哈里斯", "type": "角色", "aliases": []},
            {"name": "中士K.罗德里格斯", "type": "角色", "aliases": []},
            {"name": "中尉J.戴维斯", "type": "角色", "aliases": []},
            {"name": "史蒂文·加西亚", "type": "角色", "aliases": []},
            {"name": "真空弹", "type": "物品", "aliases": []},
            {"name": "皮尔斯", "type": "角色", "aliases": []},
            {"name": "玛丽塔", "type": "角色", "aliases": []},
            {"name": "皮面日记本", "type": "物品", "aliases": []},
            {"name": "斗牛犬", "type": "角色", "aliases": []},
            {"name": "问责记录", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "莫莉德尔", "dst": "副官", "relation": "是", "confidence": 0.9},
            {"src": "莫莉德尔", "dst": "问责记录", "relation": "撰写", "confidence": 0.9},
            {"src": "问责记录", "dst": "伊戈尔将军", "relation": "记录", "confidence": 0.8},
            {"src": "伊戈尔将军", "dst": "上尉L.哈里斯", "relation": "问责", "confidence": 0.8},
            {"src": "伊戈尔将军", "dst": "中士K.罗德里格斯", "relation": "问责", "confidence": 0.8},
            {"src": "伊戈尔将军", "dst": "中尉J.戴维斯", "relation": "问责", "confidence": 0.8},
            {"src": "史蒂文·加西亚", "dst": "真空弹", "relation": "泄露", "confidence": 0.7},
            {"src": "皮面日记本", "dst": "皮尔斯", "relation": "记录", "confidence": 0.7},
            {"src": "皮面日记本", "dst": "玛丽塔", "relation": "记录", "confidence": 0.7},
            {"src": "玛丽塔", "dst": "斗牛犬", "relation": "拥有", "confidence": 0.7},
        ],
    },
    # 8) UTTU访谈（蓝手帕/数羊羔） + 蓝手帕旅馆清扫记录
    "82c84003fdf120e9": {
        "entities": [
            {"name": "蓝手帕", "type": "角色", "aliases": []},
            {"name": "数羊羔", "type": "角色", "aliases": []},
            {"name": "UTTU", "type": "组织", "aliases": []},
            {"name": "恐惧", "type": "概念", "aliases": []},
            {"name": "蓝手帕旅馆", "type": "地点", "aliases": []},
            {"name": "蓝手帕旅馆清扫记录", "type": "物品", "aliases": []},
            {"name": "105房间", "type": "地点", "aliases": []},
            {"name": "108房间", "type": "地点", "aliases": []},
            {"name": "205房间", "type": "地点", "aliases": []},
            {"name": "211房间", "type": "地点", "aliases": []},
            {"name": "前台", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "数羊羔", "dst": "蓝手帕", "relation": "采访", "confidence": 0.9},
            {"src": "数羊羔", "dst": "恐惧", "relation": "记录", "confidence": 0.8},
            {"src": "蓝手帕", "dst": "恐惧", "relation": "品鉴", "confidence": 0.7},
            {"src": "蓝手帕", "dst": "UTTU", "relation": "接受访谈", "confidence": 0.7},
            {"src": "蓝手帕旅馆清扫记录", "dst": "蓝手帕旅馆", "relation": "关于", "confidence": 0.8},
            {"src": "蓝手帕旅馆清扫记录", "dst": "105房间", "relation": "记录", "confidence": 0.7},
            {"src": "蓝手帕旅馆清扫记录", "dst": "108房间", "relation": "记录", "confidence": 0.7},
            {"src": "蓝手帕旅馆清扫记录", "dst": "205房间", "relation": "记录", "confidence": 0.7},
            {"src": "蓝手帕旅馆清扫记录", "dst": "211房间", "relation": "记录", "confidence": 0.7},
            {"src": "蓝手帕旅馆清扫记录", "dst": "前台", "relation": "记录", "confidence": 0.7},
        ],
    },
    # 9) 论坛帖子（小小草/齐云居士/雪落无声）· 风水/祝县/流水无涯
    "4702b62781c1c3fc": {
        "entities": [
            {"name": "小小草", "type": "角色", "aliases": []},
            {"name": "齐云居士", "type": "角色", "aliases": []},
            {"name": "雪落无声", "type": "角色", "aliases": []},
            {"name": "祝县", "type": "地点", "aliases": []},
            {"name": "风水", "type": "概念", "aliases": []},
            {"name": "流水无涯", "type": "组织", "aliases": []},
            {"name": "人民西路", "type": "地点", "aliases": []},
            {"name": "L神", "type": "角色", "aliases": []},
            {"name": "行者", "type": "角色", "aliases": []},
            {"name": "浮云", "type": "角色", "aliases": []},
            {"name": "斑竹", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "齐云居士", "dst": "祝县", "relation": "评价", "confidence": 0.7},
            {"src": "齐云居士", "dst": "风水", "relation": "擅长", "confidence": 0.7},
            {"src": "小小草", "dst": "风水", "relation": "咨询", "confidence": 0.7},
            {"src": "雪落无声", "dst": "流水无涯", "relation": "活跃于", "confidence": 0.7},
            {"src": "L神", "dst": "流水无涯", "relation": "升级", "confidence": 0.8},
            {"src": "雪落无声", "dst": "斑竹", "relation": "曾任", "confidence": 0.8},
            {"src": "雪落无声", "dst": "行者", "relation": "交流", "confidence": 0.7},
            {"src": "雪落无声", "dst": "浮云", "relation": "交流", "confidence": 0.7},
            {"src": "小小草", "dst": "人民西路", "relation": "拟购", "confidence": 0.7},
        ],
    },
    # 10) 齐云居士风水帖 · 气/七十二变/孙悟空
    "9f09201adf42f9f1": {
        "entities": [
            {"name": "气蕴万物", "type": "概念", "aliases": []},
            {"name": "齐云居士", "type": "角色", "aliases": []},
            {"name": "七十二变", "type": "概念", "aliases": []},
            {"name": "二十四节气", "type": "概念", "aliases": []},
            {"name": "孙悟空", "type": "角色", "aliases": []},
            {"name": "菩提祖师", "type": "角色", "aliases": []},
            {"name": "大鲲化鹏", "type": "概念", "aliases": []},
            {"name": "腐草为萤", "type": "概念", "aliases": []},
            {"name": "大椿", "type": "概念", "aliases": []},
            {"name": "彭祖", "type": "角色", "aliases": []},
            {"name": "长生", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "齐云居士", "dst": "气蕴万物", "relation": "撰写", "confidence": 0.9},
            {"src": "气蕴万物", "dst": "七十二变", "relation": "论及", "confidence": 0.7},
            {"src": "气蕴万物", "dst": "二十四节气", "relation": "论及", "confidence": 0.7},
            {"src": "气蕴万物", "dst": "大鲲化鹏", "relation": "举例", "confidence": 0.7},
            {"src": "气蕴万物", "dst": "腐草为萤", "relation": "举例", "confidence": 0.7},
            {"src": "气蕴万物", "dst": "大椿", "relation": "提及", "confidence": 0.7},
            {"src": "气蕴万物", "dst": "彭祖", "relation": "提及", "confidence": 0.7},
            {"src": "孙悟空", "dst": "七十二变", "relation": "掌握", "confidence": 0.8},
            {"src": "孙悟空", "dst": "菩提祖师", "relation": "师从", "confidence": 0.8},
            {"src": "菩提祖师", "dst": "七十二变", "relation": "传授", "confidence": 0.8},
            {"src": "孙悟空", "dst": "长生", "relation": "求取", "confidence": 0.8},
        ],
    },
    # 11) 圣洛夫基金会东欧分部备案 + “暴雨”法案节选
    "02006c326c0b1901": {
        "entities": [
            {"name": "圣洛夫基金会东欧分部", "type": "组织", "aliases": []},
            {"name": "诺瓦米奇办事处", "type": "组织", "aliases": []},
            {"name": "圣洛夫基金会", "type": "组织", "aliases": []},
            {"name": "圣洛夫基金会中央理事会", "type": "组织", "aliases": []},
            {"name": "诺瓦米奇项目", "type": "概念", "aliases": []},
            {"name": "暴雨", "type": "现象", "aliases": []},
            {"name": "“暴雨”法案（暂行）", "type": "物品", "aliases": []},
            {"name": "时空灾害", "type": "概念", "aliases": []},
            {"name": "基金会职责补充法案", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "圣洛夫基金会东欧分部", "dst": "诺瓦米奇办事处", "relation": "取代", "confidence": 0.9},
            {"src": "圣洛夫基金会", "dst": "圣洛夫基金会东欧分部", "relation": "设立", "confidence": 0.9},
            {"src": "圣洛夫基金会中央理事会", "dst": "圣洛夫基金会东欧分部", "relation": "备案", "confidence": 0.8},
            {"src": "诺瓦米奇项目", "dst": "暴雨", "relation": "确认本质", "confidence": 0.8},
            {"src": "暴雨", "dst": "时空灾害", "relation": "旧称", "confidence": 0.7},
            {"src": "“暴雨”法案（暂行）", "dst": "暴雨", "relation": "定义", "confidence": 0.9},
            {"src": "基金会职责补充法案", "dst": "暴雨", "relation": "明确职责", "confidence": 0.8},
            {"src": "圣洛夫基金会", "dst": "暴雨", "relation": "研究预警", "confidence": 0.8},
        ],
    },
    # 12) 擦鞋童们 + 维也纳咖啡（费舍尔/萨赫蛋糕）
    "4ce44958414d7c75": {
        "entities": [
            {"name": "擦鞋童们", "type": "角色", "aliases": []},
            {"name": "歌剧", "type": "概念", "aliases": []},
            {"name": "萨赫蛋糕", "type": "物品", "aliases": []},
            {"name": "维也纳", "type": "地点", "aliases": []},
            {"name": "法语", "type": "概念", "aliases": []},
            {"name": "费舍尔", "type": "角色", "aliases": []},
            {"name": "牛皮笔记本", "type": "物品", "aliases": []},
            {"name": "镀金笔", "type": "物品", "aliases": []},
            {"name": "绒盒", "type": "物品", "aliases": []},
            {"name": "维也纳咖啡", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "擦鞋童们", "dst": "歌剧", "relation": "谈论", "confidence": 0.7},
            {"src": "擦鞋童们", "dst": "萨赫蛋糕", "relation": "推荐", "confidence": 0.7},
            {"src": "擦鞋童们", "dst": "维也纳", "relation": "位于", "confidence": 0.7},
            {"src": "擦鞋童们", "dst": "法语", "relation": "学习", "confidence": 0.7},
            {"src": "绒盒", "dst": "费舍尔", "relation": "拓印", "confidence": 0.8},
            {"src": "绒盒", "dst": "牛皮笔记本", "relation": "装着", "confidence": 0.8},
            {"src": "绒盒", "dst": "镀金笔", "relation": "装着", "confidence": 0.8},
            {"src": "维也纳咖啡", "dst": "维也纳", "relation": "位于", "confidence": 0.7},
        ],
    },
    # 13) 重塑之手活动报告 + 雨前外勤观测总结（马库斯/塞梅尔维斯）
    "ddd455e535ef2ec7": {
        "entities": [
            {"name": "马库斯", "type": "角色", "aliases": []},
            {"name": "塞梅尔维斯", "type": "角色", "aliases": []},
            {"name": "重塑之手", "type": "组织", "aliases": []},
            {"name": "时代临界点", "type": "概念", "aliases": []},
            {"name": "暴雨", "type": "现象", "aliases": []},
            {"name": "总部检查站", "type": "地点", "aliases": []},
            {"name": "欧洲各分部", "type": "组织", "aliases": []},
            {"name": "撤离预案", "type": "事件", "aliases": []},
            {"name": "避难点", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "马库斯", "dst": "时代临界点", "relation": "观测", "confidence": 0.8},
            {"src": "塞梅尔维斯", "dst": "时代临界点", "relation": "观测", "confidence": 0.8},
            {"src": "重塑之手", "dst": "时代临界点", "relation": "活动于", "confidence": 0.7},
            {"src": "暴雨", "dst": "时代临界点", "relation": "伴随", "confidence": 0.7},
            {"src": "暴雨", "dst": "撤离预案", "relation": "触发", "confidence": 0.8},
            {"src": "总部检查站", "dst": "撤离预案", "relation": "执行", "confidence": 0.8},
            {"src": "暴雨", "dst": "避难点", "relation": "避难", "confidence": 0.8},
        ],
    },
    # 14) 镇民对话（叶甫根尼/维拉/贝托尔特/芝诺）
    "ecfb1510d064e380": {
        "entities": [
            {"name": "镇民Ⅰ", "type": "角色", "aliases": []},
            {"name": "镇民Ⅱ", "type": "角色", "aliases": []},
            {"name": "叶甫根尼", "type": "角色", "aliases": ["叶甫根尼同志"]},
            {"name": "维拉", "type": "角色", "aliases": ["维拉同志"]},
            {"name": "贝托尔特", "type": "角色", "aliases": []},
            {"name": "芝诺", "type": "组织", "aliases": []},
            {"name": "北方哨歌", "type": "角色", "aliases": ["北方哨歌女士"]},
            {"name": "拓荒", "type": "事件", "aliases": []},
            {"name": "镇子", "type": "地点", "aliases": ["小镇"]},
        ],
        "relations": [
            {"src": "镇民Ⅱ", "dst": "叶甫根尼", "relation": "信任", "confidence": 0.7},
            {"src": "镇民Ⅰ", "dst": "维拉", "relation": "认同", "confidence": 0.7},
            {"src": "贝托尔特", "dst": "芝诺", "relation": "隶属", "confidence": 0.9},
            {"src": "贝托尔特", "dst": "叶甫根尼", "relation": "提及", "confidence": 0.7},
            {"src": "贝托尔特", "dst": "北方哨歌", "relation": "提及", "confidence": 0.7},
            {"src": "芝诺", "dst": "镇子", "relation": "援助", "confidence": 0.7},
            {"src": "镇民Ⅰ", "dst": "镇子", "relation": "居住", "confidence": 0.7},
            {"src": "维拉", "dst": "拓荒", "relation": "提及", "confidence": 0.7},
            {"src": "叶甫根尼", "dst": "拓荒", "relation": "关联", "confidence": 0.7},
        ],
    },
    # 15) 克努特/基里尔/伊利亚/波金娜 遗书对话（叶甫根尼同志）
    "6ec5889cec363dd7": {
        "entities": [
            {"name": "克努特", "type": "角色", "aliases": []},
            {"name": "基里尔", "type": "角色", "aliases": ["基里尔同志"]},
            {"name": "伊利亚", "type": "角色", "aliases": []},
            {"name": "波金娜", "type": "角色", "aliases": []},
            {"name": "叶甫根尼", "type": "角色", "aliases": ["叶甫根尼同志"]},
            {"name": "遗书", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "克努特", "dst": "遗书", "relation": "发现", "confidence": 0.9},
            {"src": "叶甫根尼", "dst": "遗书", "relation": "留下", "confidence": 0.9},
            {"src": "基里尔", "dst": "叶甫根尼", "relation": "缅怀", "confidence": 0.7},
            {"src": "波金娜", "dst": "叶甫根尼", "relation": "评价", "confidence": 0.7},
            {"src": "波金娜", "dst": "基里尔", "relation": "劝慰", "confidence": 0.7},
            {"src": "伊利亚", "dst": "基里尔", "relation": "对话", "confidence": 0.7},
            {"src": "克努特", "dst": "基里尔", "relation": "赞同", "confidence": 0.7},
            {"src": "波金娜", "dst": "遗书", "relation": "提及", "confidence": 0.7},
        ],
    },
    # 16) 维拉/乌里扬娜 来亚什基回忆（瓦夏/莫斯科/哮喘）
    "3ab7c5a56c86a0cc": {
        "entities": [
            {"name": "维拉", "type": "角色", "aliases": ["维拉同志"]},
            {"name": "乌里扬娜", "type": "角色", "aliases": []},
            {"name": "来亚什基", "type": "地点", "aliases": []},
            {"name": "莫斯科", "type": "地点", "aliases": []},
            {"name": "瓦夏", "type": "角色", "aliases": []},
            {"name": "哮喘", "type": "现象", "aliases": []},
            {"name": "杨絮", "type": "物品", "aliases": []},
            {"name": "画笔", "type": "物品", "aliases": []},
            {"name": "广场", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "乌里扬娜", "dst": "来亚什基", "relation": "来自", "confidence": 0.8},
            {"src": "乌里扬娜", "dst": "莫斯科", "relation": "迁居", "confidence": 0.8},
            {"src": "乌里扬娜", "dst": "瓦夏", "relation": "母子", "confidence": 0.9},
            {"src": "瓦夏", "dst": "哮喘", "relation": "患有", "confidence": 0.8},
            {"src": "维拉", "dst": "来亚什基", "relation": "建设", "confidence": 0.7},
            {"src": "维拉", "dst": "乌里扬娜", "relation": "安慰", "confidence": 0.7},
            {"src": "画笔", "dst": "广场", "relation": "用于", "confidence": 0.7},
            {"src": "瓦夏", "dst": "画笔", "relation": "想要", "confidence": 0.7},
        ],
    },
    # 17) 维拉/拉普拉斯研究员/北方哨歌 讲座（理线学/阿夫西维）
    "f962554a3527eb93": {
        "entities": [
            {"name": "维拉", "type": "角色", "aliases": []},
            {"name": "拉普拉斯研究员", "type": "角色", "aliases": ["拉普拉斯"]},
            {"name": "北方哨歌", "type": "角色", "aliases": ["北方哨歌同志"]},
            {"name": "讲座", "type": "事件", "aliases": []},
            {"name": "理线学", "type": "概念", "aliases": []},
            {"name": "阿夫西维", "type": "角色", "aliases": []},
            {"name": "翻花绳", "type": "事件", "aliases": []},
            {"name": "答疑环节", "type": "事件", "aliases": []},
        ],
        "relations": [
            {"src": "北方哨歌", "dst": "讲座", "relation": "主讲", "confidence": 0.9},
            {"src": "维拉", "dst": "北方哨歌", "relation": "协助", "confidence": 0.7},
            {"src": "拉普拉斯研究员", "dst": "北方哨歌", "relation": "请教", "confidence": 0.8},
            {"src": "北方哨歌", "dst": "理线学", "relation": "擅长", "confidence": 0.8},
            {"src": "北方哨歌", "dst": "阿夫西维", "relation": "约定", "confidence": 0.7},
            {"src": "北方哨歌", "dst": "翻花绳", "relation": "表演", "confidence": 0.7},
            {"src": "讲座", "dst": "答疑环节", "relation": "包含", "confidence": 0.7},
            {"src": "维拉", "dst": "讲座", "relation": "参加", "confidence": 0.7},
        ],
    },
    # 18) ？？？独白（基金会临时代表/胶囊） + 华尔街新闻日报魔精广告
    "7335e5de9983645d": {
        "entities": [
            {"name": "基金会临时代表", "type": "角色", "aliases": []},
            {"name": "胶囊", "type": "物品", "aliases": []},
            {"name": "西装女孩", "type": "角色", "aliases": []},
            {"name": "特拉帕尼", "type": "地点", "aliases": []},
            {"name": "西西里岛", "type": "地点", "aliases": []},
            {"name": "非洲大陆", "type": "地点", "aliases": []},
            {"name": "华尔街新闻日报", "type": "组织", "aliases": []},
            {"name": "魔精", "type": "概念", "aliases": []},
            {"name": "C.C魔精典卖行", "type": "组织", "aliases": []},
        ],
        "relations": [
            {"src": "基金会临时代表", "dst": "胶囊", "relation": "持有", "confidence": 0.9},
            {"src": "胶囊", "dst": "西装女孩", "relation": "影响", "confidence": 0.7},
            {"src": "非洲大陆", "dst": "特拉帕尼", "relation": "吹向", "confidence": 0.8},
            {"src": "特拉帕尼", "dst": "西西里岛", "relation": "位于", "confidence": 0.7},
            {"src": "华尔街新闻日报", "dst": "魔精", "relation": "报道", "confidence": 0.7},
            {"src": "华尔街新闻日报", "dst": "C.C魔精典卖行", "relation": "刊登", "confidence": 0.7},
            {"src": "C.C魔精典卖行", "dst": "魔精", "relation": "收购", "confidence": 0.8},
        ],
    },
    # 19) 中场休息（卡邦克鲁/拉伯雷多） + ？？？酒瓶独白（瓦尔登湖魔药酒吧）
    "003fbe0e83c7d639": {
        "entities": [
            {"name": "卡邦克鲁", "type": "概念", "aliases": []},
            {"name": "拉伯雷多", "type": "概念", "aliases": []},
            {"name": "C.C行长", "type": "角色", "aliases": []},
            {"name": "乳浊玻璃酒瓶", "type": "物品", "aliases": []},
            {"name": "魔精的鼻涕", "type": "物品", "aliases": []},
            {"name": "瓦尔登湖魔药酒吧", "type": "地点", "aliases": []},
            {"name": "魔精", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "卡邦克鲁", "dst": "魔精", "relation": "属于", "confidence": 0.8},
            {"src": "拉伯雷多", "dst": "魔精", "relation": "属于", "confidence": 0.8},
            {"src": "C.C行长", "dst": "魔精", "relation": "担保", "confidence": 0.7},
            {"src": "乳浊玻璃酒瓶", "dst": "魔精的鼻涕", "relation": "实为", "confidence": 0.7},
            {"src": "乳浊玻璃酒瓶", "dst": "瓦尔登湖魔药酒吧", "relation": "来自", "confidence": 0.8},
            {"src": "魔精的鼻涕", "dst": "魔精", "relation": "属于", "confidence": 0.7},
        ],
    },
    # 20) 南极探险（乌尔里希/护卫兵/嚼嚼松果中士/莫莉德尔中尉/企鹅）
    "d4e33ded23e2e43e": {
        "entities": [
            {"name": "乌尔里希", "type": "角色", "aliases": []},
            {"name": "护卫兵", "type": "角色", "aliases": []},
            {"name": "嚼嚼松果中士", "type": "角色", "aliases": ["嚼嚼松果", "松鼠中士", "松鼠"]},
            {"name": "莫莉德尔中尉", "type": "角色", "aliases": ["莫莉德尔"]},
            {"name": "企鹅", "type": "角色", "aliases": []},
            {"name": "芝诺", "type": "组织", "aliases": []},
            {"name": "南极", "type": "地点", "aliases": []},
            {"name": "火山", "type": "地点", "aliases": []},
            {"name": "唱片", "type": "物品", "aliases": []},
            {"name": "仪式", "type": "事件", "aliases": []},
            {"name": "磁流体", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "嚼嚼松果中士", "dst": "莫莉德尔中尉", "relation": "受遣", "confidence": 0.9},
            {"src": "莫莉德尔中尉", "dst": "嚼嚼松果中士", "relation": "派遣", "confidence": 0.9},
            {"src": "乌尔里希", "dst": "嚼嚼松果中士", "relation": "遇见", "confidence": 0.7},
            {"src": "护卫兵", "dst": "嚼嚼松果中士", "relation": "遇见", "confidence": 0.7},
            {"src": "企鹅", "dst": "芝诺", "relation": "致礼", "confidence": 0.8},
            {"src": "嚼嚼松果中士", "dst": "南极", "relation": "向导", "confidence": 0.8},
            {"src": "嚼嚼松果中士", "dst": "火山", "relation": "引导攀登", "confidence": 0.8},
            {"src": "嚼嚼松果中士", "dst": "仪式", "relation": "赶赴", "confidence": 0.7},
            {"src": "唱片", "dst": "仪式", "relation": "关乎", "confidence": 0.7},
            {"src": "磁流体", "dst": "嚼嚼松果中士", "relation": "对话", "confidence": 0.7},
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
    print(f"[apply-missing-p19] 写入 {len(RESULTS)} 条，NOOP +{len(NOOP_ADD)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
