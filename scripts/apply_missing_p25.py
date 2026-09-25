# -*- coding: utf-8 -*-
"""未抽取剧情块补抽 · 第 25 批（backfill2 batch_15，20 块，无纯数值/UI 页）。

用法：
  python scripts/apply_missing_p25.py            # 预演（悬空+落地自检）
  python scripts/apply_missing_p25.py --apply    # 写盘
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

# 本批 20 块均含剧情内容（含 UI 拼接块 00921610d57f3f1e，已抽地点/任务名与传说），
# 无纯数值页/UI 页，故无 NOOP。
NOOP_ADD: list[str] = []

RESULTS: dict[str, dict] = {
    # 1) 宁芙传说 · 乌卢鲁运动会赛事日程
    "9cf6fd834b2b29c9": {
        "entities": [
            {"name": "宁芙", "type": "角色", "aliases": []},
            {"name": "海宁芙", "type": "角色", "aliases": []},
            {"name": "泉水宁芙", "type": "角色", "aliases": []},
            {"name": "海豚", "type": "角色", "aliases": []},
            {"name": "海马", "type": "角色", "aliases": []},
            {"name": "海龙", "type": "角色", "aliases": []},
            {"name": "神秘学家家族", "type": "组织", "aliases": []},
            {"name": "乌卢鲁运动场", "type": "地点", "aliases": []},
            {"name": "火山岛海滩", "type": "地点", "aliases": []},
            {"name": "圣火", "type": "角色", "aliases": []},
            {"name": "乌卢鲁运动会", "type": "事件", "aliases": []},
            {"name": "基金会", "type": "组织", "aliases": []},
        ],
        "relations": [
            {"src": "海宁芙", "dst": "宁芙", "relation": "属于", "confidence": 0.8},
            {"src": "泉水宁芙", "dst": "宁芙", "relation": "属于", "confidence": 0.8},
            {"src": "泉水宁芙", "dst": "神秘学家家族", "relation": "合作", "confidence": 0.7},
            {"src": "乌卢鲁运动会", "dst": "乌卢鲁运动场", "relation": "举办于", "confidence": 0.8},
            {"src": "乌卢鲁运动会", "dst": "火山岛海滩", "relation": "举办于", "confidence": 0.7},
            {"src": "圣火", "dst": "乌卢鲁运动会", "relation": "建议", "confidence": 0.7},
        ],
    },
    # 2) 多瑙黎明号绝密外勤任务 · 血食怪与感染种
    "82da2626c7e92749": {
        "entities": [
            {"name": "圣洛夫基金会", "type": "组织", "aliases": []},
            {"name": "多瑙黎明号", "type": "物品", "aliases": []},
            {"name": "超自然者血食怪", "type": "角色", "aliases": []},
            {"name": "感染种", "type": "概念", "aliases": []},
            {"name": "塞梅尔维斯", "type": "角色", "aliases": []},
            {"name": "伊斯坦布尔", "type": "地点", "aliases": []},
            {"name": "维也纳", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "多瑙黎明号", "dst": "伊斯坦布尔", "relation": "往返于", "confidence": 0.7},
            {"src": "多瑙黎明号", "dst": "维也纳", "relation": "往返于", "confidence": 0.7},
            {"src": "多瑙黎明号", "dst": "超自然者血食怪", "relation": "检测到", "confidence": 0.8},
            {"src": "感染种", "dst": "超自然者血食怪", "relation": "属于", "confidence": 0.8},
            {"src": "塞梅尔维斯", "dst": "多瑙黎明号", "relation": "登乘", "confidence": 0.8},
            {"src": "圣洛夫基金会", "dst": "塞梅尔维斯", "relation": "任命", "confidence": 0.8},
        ],
    },
    # 3) 月亮日报读者来信 · 海洋之心专栏与寻人启事
    "ab728046680de96e": {
        "entities": [
            {"name": "海洋之心", "type": "概念", "aliases": []},
            {"name": "寻人启事", "type": "概念", "aliases": []},
            {"name": "月亮日报", "type": "组织", "aliases": []},
            {"name": "安保机器人", "type": "物品", "aliases": []},
            {"name": "蹩脚侦探", "type": "角色", "aliases": []},
            {"name": "游客朋友", "type": "角色", "aliases": []},
            {"name": "飞龙", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "海洋之心", "dst": "月亮日报", "relation": "隶属于", "confidence": 0.7},
            {"src": "寻人启事", "dst": "月亮日报", "relation": "出现于", "confidence": 0.7},
            {"src": "游客朋友", "dst": "海洋之心", "relation": "投稿", "confidence": 0.7},
            {"src": "蹩脚侦探", "dst": "安保机器人", "relation": "质疑", "confidence": 0.7},
        ],
    },
    # 4) 傩戏面具论坛 · 险道兽与侲童
    "16f25a9455e0def8": {
        "entities": [
            {"name": "天雷滚滚", "type": "角色", "aliases": []},
            {"name": "游客_9031", "type": "角色", "aliases": []},
            {"name": "和平鸽", "type": "角色", "aliases": []},
            {"name": "傩戏面具", "type": "物品", "aliases": []},
            {"name": "险道兽", "type": "角色", "aliases": []},
            {"name": "侲童", "type": "角色", "aliases": []},
            {"name": "甲作面具", "type": "物品", "aliases": []},
            {"name": "穷奇面具", "type": "物品", "aliases": []},
            {"name": "巯胃面具", "type": "物品", "aliases": []},
            {"name": "腾简面具", "type": "物品", "aliases": []},
            {"name": "揽诸面具", "type": "物品", "aliases": []},
            {"name": "强梁面具", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "甲作面具", "dst": "险道兽", "relation": "属于", "confidence": 0.8},
            {"src": "穷奇面具", "dst": "险道兽", "relation": "属于", "confidence": 0.8},
            {"src": "巯胃面具", "dst": "险道兽", "relation": "属于", "confidence": 0.8},
            {"src": "腾简面具", "dst": "险道兽", "relation": "属于", "confidence": 0.8},
            {"src": "揽诸面具", "dst": "险道兽", "relation": "属于", "confidence": 0.8},
            {"src": "强梁面具", "dst": "险道兽", "relation": "属于", "confidence": 0.8},
            {"src": "侲童", "dst": "险道兽", "relation": "被托付于", "confidence": 0.7},
            {"src": "天雷滚滚", "dst": "傩戏面具", "relation": "发现", "confidence": 0.7},
            {"src": "游客_9031", "dst": "险道兽", "relation": "解读", "confidence": 0.7},
            {"src": "和平鸽", "dst": "侲童", "relation": "提及", "confidence": 0.7},
        ],
    },
    # 5) 论坛帖 · 天道、精怪大乱斗与老鼠精
    "68d242cdc3676975": {
        "entities": [
            {"name": "斑竹的爹", "type": "角色", "aliases": []},
            {"name": "天道", "type": "概念", "aliases": []},
            {"name": "老鼠精", "type": "角色", "aliases": []},
            {"name": "黑狗精", "type": "角色", "aliases": []},
            {"name": "乌龟精", "type": "角色", "aliases": []},
            {"name": "热血精怪大乱斗", "type": "概念", "aliases": []},
            {"name": "zzrrrr", "type": "角色", "aliases": []},
            {"name": "游客_4517", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "斑竹的爹", "dst": "天道", "relation": "论述", "confidence": 0.7},
            {"src": "老鼠精", "dst": "热血精怪大乱斗", "relation": "出现于", "confidence": 0.8},
            {"src": "乌龟精", "dst": "热血精怪大乱斗", "relation": "出现于", "confidence": 0.8},
            {"src": "黑狗精", "dst": "热血精怪大乱斗", "relation": "出现于", "confidence": 0.8},
            {"src": "zzrrrr", "dst": "热血精怪大乱斗", "relation": "游玩", "confidence": 0.7},
        ],
    },
    # 6) 拉普拉斯科算中心通知 · 路德维希、诺谛卡与命名日
    "1953dda00703dcb5": {
        "entities": [
            {"name": "路德维希", "type": "角色", "aliases": []},
            {"name": "渡鸦", "type": "角色", "aliases": []},
            {"name": "诺谛卡小姐", "type": "角色", "aliases": []},
            {"name": "拉普拉斯科算中心", "type": "组织", "aliases": []},
            {"name": "阿德勒", "type": "角色", "aliases": []},
            {"name": "库珀花环", "type": "角色", "aliases": []},
            {"name": "爱兹拉", "type": "角色", "aliases": []},
            {"name": "西尔维", "type": "角色", "aliases": []},
            {"name": "兔毛手袋", "type": "角色", "aliases": []},
            {"name": "命名日", "type": "事件", "aliases": []},
            {"name": "苦目糖甜点", "type": "物品", "aliases": []},
            {"name": "航天小组", "type": "组织", "aliases": []},
        ],
        "relations": [
            {"src": "渡鸦", "dst": "路德维希", "relation": "疑似关联", "confidence": 0.7},
            {"src": "阿德勒", "dst": "拉普拉斯科算中心", "relation": "担任负责人", "confidence": 0.8},
            {"src": "库珀花环", "dst": "命名日", "relation": "回应", "confidence": 0.7},
            {"src": "兔毛手袋", "dst": "苦目糖甜点", "relation": "发明", "confidence": 0.8},
            {"src": "航天小组", "dst": "命名日", "relation": "举办", "confidence": 0.7},
            {"src": "西尔维", "dst": "命名日", "relation": "要求", "confidence": 0.7},
        ],
    },
    # 7) 迪塔斯多夫贵族独白 · 降灵、骑士精神与决斗
    "c848d8745a6901e3": {
        "entities": [
            {"name": "迪塔斯多夫", "type": "组织", "aliases": []},
            {"name": "降灵", "type": "概念", "aliases": []},
            {"name": "对抗疯狂", "type": "概念", "aliases": []},
            {"name": "骑士精神", "type": "概念", "aliases": []},
            {"name": "无主的笔记本", "type": "物品", "aliases": []},
            {"name": "决斗", "type": "事件", "aliases": []},
        ],
        "relations": [
            {"src": "迪塔斯多夫", "dst": "降灵", "relation": "能够", "confidence": 0.8},
            {"src": "对抗疯狂", "dst": "迪塔斯多夫", "relation": "体现于", "confidence": 0.7},
            {"src": "决斗", "dst": "骑士精神", "relation": "体现", "confidence": 0.8},
            {"src": "无主的笔记本", "dst": "决斗", "relation": "记载", "confidence": 0.7},
        ],
    },
    # 8) 平衡伞说明 · 重塑之手干部名单与新朋旧友
    "fd0cb4b5bf22bbb0": {
        "entities": [
            {"name": "平衡伞", "type": "物品", "aliases": []},
            {"name": "重塑之手", "type": "组织", "aliases": []},
            {"name": "重塑之手干部名单", "type": "物品", "aliases": []},
            {"name": "新朋旧友", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "重塑之手干部名单", "dst": "重塑之手", "relation": "属于", "confidence": 0.9},
            {"src": "新朋旧友", "dst": "重塑之手", "relation": "关联", "confidence": 0.7},
            {"src": "平衡伞", "dst": "重塑之手", "relation": "配备于", "confidence": 0.7},
        ],
    },
    # 9) 神秘酒客独白 · 十四行诗与飘逸的苹果
    "1ab6172e61458778": {
        "entities": [
            {"name": "十四行诗", "type": "角色", "aliases": []},
            {"name": "飘逸的苹果", "type": "角色", "aliases": []},
            {"name": "基金会", "type": "组织", "aliases": []},
            {"name": "水晶骷髅头", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "十四行诗", "dst": "飘逸的苹果", "relation": "提及", "confidence": 0.7},
            {"src": "基金会", "dst": "十四行诗", "relation": "训导", "confidence": 0.7},
        ],
    },
    # 10) 创世纪隐喻关卡 · 中尉、指挥官与忠诚
    "8a1b8ff6cbdc654e": {
        "entities": [
            {"name": "创世纪隐喻", "type": "概念", "aliases": ["《创世纪》隐喻"]},
            {"name": "中尉", "type": "角色", "aliases": []},
            {"name": "指挥官", "type": "角色", "aliases": []},
            {"name": "忠诚", "type": "概念", "aliases": []},
            {"name": "眼球侦察兵", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "中尉", "dst": "忠诚", "relation": "缺乏", "confidence": 0.7},
            {"src": "指挥官", "dst": "忠诚", "relation": "要求", "confidence": 0.7},
            {"src": "眼球侦察兵", "dst": "中尉", "relation": "误导", "confidence": 0.7},
        ],
    },
    # 11) 南极向导对话 · 嚼嚼松果、乌尔里希、司辰与企鹅
    "1f8d76691acbf0cd": {
        "entities": [
            {"name": "嚼嚼松果", "type": "角色", "aliases": []},
            {"name": "乌尔里希", "type": "角色", "aliases": []},
            {"name": "司辰", "type": "角色", "aliases": []},
            {"name": "特里波德罗", "type": "角色", "aliases": []},
            {"name": "企鹅", "type": "角色", "aliases": []},
            {"name": "重塑", "type": "组织", "aliases": []},
            {"name": "松鼠", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "企鹅", "dst": "特里波德罗", "relation": "学自", "confidence": 0.8},
            {"src": "乌尔里希", "dst": "重塑", "relation": "对比", "confidence": 0.7},
            {"src": "嚼嚼松果", "dst": "乌尔里希", "relation": "引导", "confidence": 0.8},
            {"src": "乌尔里希", "dst": "司辰", "relation": "呼叫", "confidence": 0.7},
            {"src": "松鼠", "dst": "乌尔里希", "relation": "陪同", "confidence": 0.7},
        ],
    },
    # 12) 火炬传递地图（UI 拼接块）· 报刊亭、乌卢鲁沙漠、壁画与泉眼
    "00921610d57f3f1e": {
        "entities": [
            {"name": "报刊亭", "type": "地点", "aliases": []},
            {"name": "乌卢鲁沙漠", "type": "地点", "aliases": []},
            {"name": "壁画", "type": "物品", "aliases": []},
            {"name": "通向泉眼的道路", "type": "地点", "aliases": []},
            {"name": "乌卢鲁泉眼", "type": "地点", "aliases": []},
            {"name": "火炬护卫队Ⅲ", "type": "事件", "aliases": []},
            {"name": "火炬护卫队Ⅳ", "type": "事件", "aliases": []},
        ],
        "relations": [
            {"src": "壁画", "dst": "乌卢鲁泉眼", "relation": "指引", "confidence": 0.8},
            {"src": "通向泉眼的道路", "dst": "乌卢鲁泉眼", "relation": "通往", "confidence": 0.8},
            {"src": "火炬护卫队Ⅲ", "dst": "报刊亭", "relation": "涉及", "confidence": 0.7},
            {"src": "火炬护卫队Ⅳ", "dst": "乌卢鲁沙漠", "relation": "涉及", "confidence": 0.7},
        ],
    },
    # 13) 孤岛对话 · 2007年与小岛
    "0ad723492e14f612": {
        "entities": [
            {"name": "2007年", "type": "时间", "aliases": []},
            {"name": "小岛", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "2007年", "dst": "小岛", "relation": "标记于", "confidence": 0.7},
        ],
    },
    # 14) 天文论坛 · 宙斯、谷神星、数学王子与预言
    "71499a15afaa3ec1": {
        "entities": [
            {"name": "宙斯", "type": "角色", "aliases": []},
            {"name": "谷神星", "type": "概念", "aliases": []},
            {"name": "乌拉诺斯", "type": "概念", "aliases": []},
            {"name": "刻瑞斯", "type": "概念", "aliases": []},
            {"name": "反射望远镜", "type": "物品", "aliases": []},
            {"name": "数学王子", "type": "角色", "aliases": []},
            {"name": "预言", "type": "概念", "aliases": []},
            {"name": "第八行星", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "数学王子", "dst": "谷神星", "relation": "计算轨道", "confidence": 0.8},
            {"src": "宙斯", "dst": "预言", "relation": "印证", "confidence": 0.7},
            {"src": "第八行星", "dst": "乌拉诺斯", "relation": "并列于", "confidence": 0.7},
        ],
    },
    # 15) 数字隐喻独白 · 37、质数、无限与游荡者
    "e84829ea9dc7a3ab": {
        "entities": [
            {"name": "37", "type": "角色", "aliases": []},
            {"name": "质数", "type": "概念", "aliases": []},
            {"name": "无限", "type": "概念", "aliases": []},
            {"name": "游荡者", "type": "角色", "aliases": []},
            {"name": "命运", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "37", "dst": "质数", "relation": "属于", "confidence": 0.7},
            {"src": "37", "dst": "命运", "relation": "象征", "confidence": 0.7},
        ],
    },
    # 16) 与火共舞关卡 · 保利娜、圣洛夫基金会与历史情报柜
    "cf068202b77ade06": {
        "entities": [
            {"name": "保利娜", "type": "角色", "aliases": []},
            {"name": "圣洛夫基金会", "type": "组织", "aliases": []},
            {"name": "历史情报柜", "type": "地点", "aliases": []},
            {"name": "公平竞赛", "type": "事件", "aliases": []},
            {"name": "与火共舞", "type": "事件", "aliases": []},
        ],
        "relations": [
            {"src": "保利娜", "dst": "圣洛夫基金会", "relation": "隶属", "confidence": 0.8},
            {"src": "保利娜", "dst": "历史情报柜", "relation": "打开", "confidence": 0.8},
        ],
    },
    # 17) 巴西黄金檀笔记 · 巴克蒂、墨西哥愚人节与神秘学家袭击
    "a60f15c6bdcdcd94": {
        "entities": [
            {"name": "巴西黄金檀", "type": "物品", "aliases": []},
            {"name": "巴克蒂", "type": "物品", "aliases": ["Bocote"]},
            {"name": "墨西哥愚人节", "type": "事件", "aliases": []},
            {"name": "保利娜", "type": "角色", "aliases": []},
            {"name": "阿兹蒂克文化", "type": "概念", "aliases": []},
            {"name": "园艺剪", "type": "物品", "aliases": []},
            {"name": "术杖", "type": "物品", "aliases": []},
            {"name": "尖刀", "type": "物品", "aliases": []},
            {"name": "苦味酸", "type": "物品", "aliases": []},
            {"name": "火棉", "type": "物品", "aliases": []},
            {"name": "调和魔药", "type": "物品", "aliases": []},
            {"name": "神谕", "type": "概念", "aliases": []},
            {"name": "癔症", "type": "概念", "aliases": []},
            {"name": "神秘学家", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "巴克蒂", "dst": "巴西黄金檀", "relation": "别称", "confidence": 0.9},
            {"src": "墨西哥愚人节", "dst": "神秘学家", "relation": "由…发动袭击", "confidence": 0.8},
            {"src": "神谕", "dst": "巴西黄金檀", "relation": "来自", "confidence": 0.7},
            {"src": "癔症", "dst": "神秘学家", "relation": "源于", "confidence": 0.7},
        ],
    },
    # 18) 红弩箭中尉审查报告 · 哨兵、诺阿与麦蒂斯将军
    "71b396c84e8f9d75": {
        "entities": [
            {"name": "红弩箭中尉", "type": "角色", "aliases": ["红弩箭"]},
            {"name": "芝诺", "type": "组织", "aliases": []},
            {"name": "诺阿", "type": "角色", "aliases": []},
            {"name": "麦蒂斯将军", "type": "角色", "aliases": []},
            {"name": "勒贝尔步枪", "type": "物品", "aliases": []},
            {"name": "玛尔纱", "type": "角色", "aliases": []},
            {"name": "哨兵", "type": "角色", "aliases": []},
            {"name": "战争狂人", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "红弩箭中尉", "dst": "芝诺", "relation": "接受审查", "confidence": 0.8},
            {"src": "哨兵", "dst": "诺阿", "relation": "击倒", "confidence": 0.8},
            {"src": "哨兵", "dst": "麦蒂斯将军", "relation": "击倒", "confidence": 0.8},
            {"src": "哨兵", "dst": "战争狂人", "relation": "击倒", "confidence": 0.7},
        ],
    },
    # 19) 十三年级三班学生名单与家乡来信
    "dba6705af2bf98fd": {
        "entities": [
            {"name": "十三年级三班", "type": "组织", "aliases": []},
            {"name": "迪特里希·贝克尔", "type": "角色", "aliases": []},
            {"name": "贝特克·齐默尔曼", "type": "角色", "aliases": []},
            {"name": "西蒙·米勒", "type": "角色", "aliases": []},
            {"name": "弗里德里希·鲍尔", "type": "角色", "aliases": []},
            {"name": "芬恩·瓦格纳", "type": "角色", "aliases": []},
            {"name": "埃尔文·诺伊曼", "type": "角色", "aliases": []},
            {"name": "费利克斯·齐默尔曼", "type": "角色", "aliases": []},
            {"name": "朱利安·克吕格", "type": "角色", "aliases": []},
            {"name": "本·贝克尔", "type": "角色", "aliases": []},
            {"name": "瓦尔特·施密特", "type": "角色", "aliases": []},
            {"name": "保罗·霍伊默尔", "type": "角色", "aliases": []},
            {"name": "艾伯哈特·布劳恩", "type": "角色", "aliases": []},
            {"name": "拉蒂斯", "type": "角色", "aliases": []},
            {"name": "玛丽安娜", "type": "角色", "aliases": []},
            {"name": "奥地利", "type": "地点", "aliases": []},
            {"name": "新艺术", "type": "概念", "aliases": []},
            {"name": "分离派展览馆", "type": "地点", "aliases": []},
            {"name": "维也纳工坊", "type": "组织", "aliases": []},
            {"name": "菲舍尔·冯·埃尔拉赫", "type": "角色", "aliases": []},
            {"name": "圣查尔斯教堂", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "迪特里希·贝克尔", "dst": "十三年级三班", "relation": "属于", "confidence": 0.8},
            {"src": "贝特克·齐默尔曼", "dst": "十三年级三班", "relation": "属于", "confidence": 0.8},
            {"src": "西蒙·米勒", "dst": "十三年级三班", "relation": "属于", "confidence": 0.8},
            {"src": "弗里德里希·鲍尔", "dst": "十三年级三班", "relation": "属于", "confidence": 0.8},
            {"src": "芬恩·瓦格纳", "dst": "十三年级三班", "relation": "属于", "confidence": 0.8},
            {"src": "埃尔文·诺伊曼", "dst": "十三年级三班", "relation": "属于", "confidence": 0.8},
            {"src": "费利克斯·齐默尔曼", "dst": "十三年级三班", "relation": "属于", "confidence": 0.8},
            {"src": "朱利安·克吕格", "dst": "十三年级三班", "relation": "属于", "confidence": 0.8},
            {"src": "本·贝克尔", "dst": "十三年级三班", "relation": "属于", "confidence": 0.8},
            {"src": "瓦尔特·施密特", "dst": "十三年级三班", "relation": "属于", "confidence": 0.8},
            {"src": "保罗·霍伊默尔", "dst": "十三年级三班", "relation": "属于", "confidence": 0.8},
            {"src": "艾伯哈特·布劳恩", "dst": "十三年级三班", "relation": "属于", "confidence": 0.8},
            {"src": "玛丽安娜", "dst": "拉蒂斯", "relation": "致信", "confidence": 0.9},
            {"src": "玛丽安娜", "dst": "维也纳工坊", "relation": "向往", "confidence": 0.7},
            {"src": "分离派展览馆", "dst": "奥地利", "relation": "位于", "confidence": 0.8},
            {"src": "圣查尔斯教堂", "dst": "菲舍尔·冯·埃尔拉赫", "relation": "由…建造", "confidence": 0.8},
            {"src": "新艺术", "dst": "奥地利", "relation": "关联于", "confidence": 0.7},
        ],
    },
    # 20) 暴雨狂热分子独白 · 夜巡特遣管理局、灰调蓝与陆上鲸歌
    "50ba300373410617": {
        "entities": [
            {"name": "暴雨", "type": "现象", "aliases": []},
            {"name": "夜巡特遣管理局", "type": "组织", "aliases": []},
            {"name": "基金会", "type": "组织", "aliases": []},
            {"name": "灰调蓝", "type": "角色", "aliases": []},
            {"name": "陆上鲸歌", "type": "事件", "aliases": []},
            {"name": "战神广场", "type": "地点", "aliases": []},
            {"name": "占卜师", "type": "角色", "aliases": []},
            {"name": "巴黎", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "占卜师", "dst": "灰调蓝", "relation": "帮助", "confidence": 0.8},
            {"src": "战神广场", "dst": "陆上鲸歌", "relation": "关联于", "confidence": 0.8},
            {"src": "陆上鲸歌", "dst": "巴黎", "relation": "发生于", "confidence": 0.7},
            {"src": "占卜师", "dst": "暴雨", "relation": "被疑渴望", "confidence": 0.7},
            {"src": "基金会", "dst": "占卜师", "relation": "警惕", "confidence": 0.7},
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
    print(f"[apply-missing-p25] 写入 {len(RESULTS)} 条，NOOP +{len(NOOP_ADD)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
