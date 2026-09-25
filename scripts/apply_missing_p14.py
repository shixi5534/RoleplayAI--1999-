# -*- coding: utf-8 -*-
"""未抽取剧情块补抽 · 第 14 批（backfill2 batch_04，20 块）。

用法：
  python scripts/apply_missing_p14.py            # 预演（悬空+落地自检）
  python scripts/apply_missing_p14.py --apply    # 写盘
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

# 本批 20 块均含剧情文本，无数值/UI/无剧情页 → 空 NOOP 集合。
NOOP_ADD: list[str] = []

RESULTS: dict[str, dict] = {
    # 1) 灵魂出窍医学观察记录 / 壁画与转折
    "3c538d307bbe50c0": {
        "entities": [
            {"name": "使魔", "type": "角色", "aliases": []},
            {"name": "神秘学物质", "type": "物品", "aliases": ["蜂蜜"]},
            {"name": "苦目糖果", "type": "物品", "aliases": []},
            {"name": "康复中心", "type": "组织", "aliases": []},
            {"name": "咖啡机", "type": "物品", "aliases": []},
            {"name": "灵魂出窍", "type": "概念", "aliases": ["灵魂离体"]},
            {"name": "壁画", "type": "物品", "aliases": []},
            {"name": "墨西哥", "type": "地点", "aliases": []},
            {"name": "政府", "type": "组织", "aliases": []},
        ],
        "relations": [
            {"src": "康复中心", "dst": "咖啡机", "relation": "维修", "confidence": 0.8},
            {"src": "墨西哥", "dst": "壁画", "relation": "以之表达故事", "confidence": 0.7},
        ],
    },
    # 2) 好演员指南 / 壁画异变 / 金苹果与晚祷会
    "8a9a95216e3385f1": {
        "entities": [
            {"name": "好演员指南", "type": "物品", "aliases": []},
            {"name": "壁画", "type": "物品", "aliases": []},
            {"name": "佛罗伦萨", "type": "地点", "aliases": []},
            {"name": "圣殿暴徒", "type": "组织", "aliases": []},
            {"name": "密文", "type": "物品", "aliases": []},
            {"name": "金苹果", "type": "物品", "aliases": []},
            {"name": "伊甸苹果", "type": "物品", "aliases": []},
            {"name": "晚祷会", "type": "组织", "aliases": []},
            {"name": "艾吉奥", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "金苹果", "dst": "伊甸苹果", "relation": "关联不明", "confidence": 0.7},
            {"src": "金苹果", "dst": "晚祷会", "relation": "与密室相关", "confidence": 0.7},
            {"src": "佛罗伦萨", "dst": "金苹果", "relation": "盛产", "confidence": 0.7},
        ],
    },
    # 3) 共融院与委员会立法流程 / 康斯坦丁
    "9db36cf813031201": {
        "entities": [
            {"name": "共融院", "type": "组织", "aliases": []},
            {"name": "委员会", "type": "组织", "aliases": []},
            {"name": "基金会", "type": "组织", "aliases": []},
            {"name": "康斯坦丁", "type": "角色", "aliases": []},
            {"name": "代表人", "type": "角色", "aliases": []},
            {"name": "行政部门", "type": "组织", "aliases": []},
        ],
        "relations": [
            {"src": "代表人", "dst": "共融院", "relation": "隶属", "confidence": 0.8},
            {"src": "代表人", "dst": "委员会", "relation": "提交议案", "confidence": 0.85},
            {"src": "委员会", "dst": "代表人", "relation": "通过或拒绝议案", "confidence": 0.85},
            {"src": "康斯坦丁", "dst": "基金会", "relation": "引导方向", "confidence": 0.8},
        ],
    },
    # 4) 聚合物国际峰会 / 谢切诺夫与莫洛托夫反对声明
    "ae3614f3baa012de": {
        "entities": [
            {"name": "聚合物国际峰会", "type": "事件", "aliases": []},
            {"name": "苏联", "type": "地点", "aliases": []},
            {"name": "聚合物", "type": "物品", "aliases": []},
            {"name": "拉菲克", "type": "角色", "aliases": []},
            {"name": "涡轮车", "type": "物品", "aliases": []},
            {"name": "政治局", "type": "组织", "aliases": []},
            {"name": "谢切诺夫", "type": "角色", "aliases": []},
            {"name": "莫洛托夫", "type": "角色", "aliases": ["叶戈尔·齐莫菲叶维奇·莫洛托夫"]},
            {"name": "列别杰夫", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "聚合物国际峰会", "dst": "聚合物", "relation": "以之为主角", "confidence": 0.9},
            {"src": "苏联", "dst": "聚合物国际峰会", "relation": "举办", "confidence": 0.7},
            {"src": "谢切诺夫", "dst": "聚合物", "relation": "提出设想", "confidence": 0.8},
            {"src": "莫洛托夫", "dst": "政治局", "relation": "代表", "confidence": 0.9},
            {"src": "政治局", "dst": "谢切诺夫", "relation": "怀疑安全性", "confidence": 0.8},
        ],
    },
    # 5) 死而复生士兵 / Ⅻ小队花名册
    "8f3ba2a2a853e920": {
        "entities": [
            {"name": "死而复生士兵", "type": "角色", "aliases": ["死而复生"]},
            {"name": "布劳恩营长", "type": "角色", "aliases": []},
            {"name": "宣传部", "type": "组织", "aliases": []},
            {"name": "Ⅻ小队", "type": "组织", "aliases": ["Ⅻ"]},
            {"name": "帕拉维扬", "type": "角色", "aliases": []},
            {"name": "芝诺军备学院", "type": "组织", "aliases": []},
            {"name": "夜巡特遣管理局", "type": "组织", "aliases": []},
            {"name": "刻雷乌斯", "type": "角色", "aliases": []},
            {"name": "战争", "type": "事件", "aliases": []},
        ],
        "relations": [
            {"src": "死而复生士兵", "dst": "布劳恩营长", "relation": "担任士官", "confidence": 0.8},
            {"src": "死而复生士兵", "dst": "宣传部", "relation": "拒绝要求", "confidence": 0.85},
            {"src": "Ⅻ小队", "dst": "帕拉维扬", "relation": "包含", "confidence": 0.8},
            {"src": "帕拉维扬", "dst": "芝诺军备学院", "relation": "毕业", "confidence": 0.9},
            {"src": "帕拉维扬", "dst": "夜巡特遣管理局", "relation": "任职", "confidence": 0.9},
            {"src": "帕拉维扬", "dst": "刻雷乌斯", "relation": "协助", "confidence": 0.85},
        ],
    },
    # 6) 圣路连特别军规 / 石像鬼研究手札
    "d9753ceaa4a0da70": {
        "entities": [
            {"name": "圣路连特别军规", "type": "概念", "aliases": []},
            {"name": "意识唤醒者", "type": "角色", "aliases": []},
            {"name": "石像鬼研究手札", "type": "物品", "aliases": []},
            {"name": "石像鬼家族", "type": "组织", "aliases": []},
            {"name": "石像鬼", "type": "角色", "aliases": []},
            {"name": "墨洛温王朝", "type": "时间", "aliases": []},
            {"name": "鲁昂主教", "type": "角色", "aliases": []},
            {"name": "教堂", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "石像鬼家族", "dst": "石像鬼", "relation": "包含", "confidence": 0.9},
            {"src": "鲁昂主教", "dst": "石像鬼", "relation": "收服", "confidence": 0.9},
            {"src": "石像鬼", "dst": "教堂", "relation": "拱卫", "confidence": 0.85},
            {"src": "石像鬼研究手札", "dst": "石像鬼家族", "relation": "记载", "confidence": 0.8},
            {"src": "圣路连特别军规", "dst": "意识唤醒者", "relation": "约束", "confidence": 0.7},
        ],
    },
    # 7) 石像鬼家族神秘术 / 诅咒与出走
    "a6ce0d817c49d84f": {
        "entities": [
            {"name": "石像鬼家族", "type": "组织", "aliases": []},
            {"name": "石像鬼", "type": "角色", "aliases": []},
            {"name": "教会", "type": "组织", "aliases": []},
            {"name": "神秘术", "type": "概念", "aliases": []},
            {"name": "火炮", "type": "物品", "aliases": []},
            {"name": "诅咒", "type": "概念", "aliases": []},
            {"name": "生物学家", "type": "角色", "aliases": []},
            {"name": "宗教", "type": "概念", "aliases": []},
            {"name": "信仰", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "石像鬼家族", "dst": "神秘术", "relation": "拥有", "confidence": 0.9},
            {"src": "石像鬼", "dst": "神秘术", "relation": "具备", "confidence": 0.85},
            {"src": "石像鬼", "dst": "石像鬼家族", "relation": "出走", "confidence": 0.8},
            {"src": "石像鬼", "dst": "诅咒", "relation": "背负", "confidence": 0.9},
            {"src": "诅咒", "dst": "石像鬼", "relation": "导致堕落", "confidence": 0.8},
            {"src": "生物学家", "dst": "石像鬼家族", "relation": "研究", "confidence": 0.7},
            {"src": "石像鬼", "dst": "信仰", "relation": "抛弃", "confidence": 0.7},
        ],
    },
    # 8) 金色饥荒下的别列格勒 / 军长伊万与斯捷尔诺娃
    "506f1cb7f3a8778c": {
        "entities": [
            {"name": "金色饥荒", "type": "事件", "aliases": []},
            {"name": "军长伊万", "type": "角色", "aliases": []},
            {"name": "莎宾娜", "type": "角色", "aliases": []},
            {"name": "斯捷尔诺娃", "type": "角色", "aliases": []},
            {"name": "军需官", "type": "角色", "aliases": []},
            {"name": "黑市", "type": "组织", "aliases": []},
            {"name": "别列格勒", "type": "地点", "aliases": []},
            {"name": "费奥多尔·彼得罗维奇", "type": "角色", "aliases": []},
            {"name": "市民代表", "type": "角色", "aliases": []},
            {"name": "警卫连", "type": "组织", "aliases": []},
        ],
        "relations": [
            {"src": "斯捷尔诺娃", "dst": "军长伊万", "relation": "报告", "confidence": 0.8},
            {"src": "军长伊万", "dst": "费奥多尔·彼得罗维奇", "relation": "商谈", "confidence": 0.8},
            {"src": "金色饥荒", "dst": "别列格勒", "relation": "蔓延", "confidence": 0.8},
            {"src": "黑市", "dst": "别列格勒", "relation": "盘剥", "confidence": 0.7},
        ],
    },
    # 9) 职员休假闲谈 / 火山岛仪式游戏
    "5ccb2617d94f5f49": {
        "entities": [
            {"name": "黄石公园", "type": "地点", "aliases": []},
            {"name": "职员Ⅱ", "type": "角色", "aliases": []},
            {"name": "职员Ⅰ", "type": "角色", "aliases": []},
            {"name": "国立自然博物馆", "type": "地点", "aliases": []},
            {"name": "西班牙", "type": "地点", "aliases": []},
            {"name": "实验室", "type": "地点", "aliases": []},
            {"name": "菌群", "type": "物品", "aliases": []},
            {"name": "火山岛", "type": "地点", "aliases": []},
            {"name": "议会书记官", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "职员Ⅱ", "dst": "国立自然博物馆", "relation": "愿参观", "confidence": 0.7},
            {"src": "火山岛", "dst": "议会书记官", "relation": "设立游戏职位", "confidence": 0.7},
        ],
    },
    # 10) 超自然者血食怪特性与感染种
    "3e574c3d76cf93a4": {
        "entities": [
            {"name": "超自然者血食怪", "type": "角色", "aliases": []},
            {"name": "血液", "type": "物品", "aliases": []},
            {"name": "渴血症", "type": "概念", "aliases": []},
            {"name": "太阳光", "type": "现象", "aliases": []},
            {"name": "炼金术仪式", "type": "概念", "aliases": []},
            {"name": "纯银", "type": "物品", "aliases": []},
            {"name": "血食怪感染种", "type": "角色", "aliases": []},
            {"name": "神秘学家感染种", "type": "角色", "aliases": []},
            {"name": "重塑之手", "type": "组织", "aliases": []},
        ],
        "relations": [
            {"src": "超自然者血食怪", "dst": "血液", "relation": "摄入", "confidence": 0.9},
            {"src": "超自然者血食怪", "dst": "太阳光", "relation": "畏光", "confidence": 0.9},
            {"src": "纯银", "dst": "超自然者血食怪", "relation": "克制", "confidence": 0.9},
            {"src": "超自然者血食怪", "dst": "血食怪感染种", "relation": "感染", "confidence": 0.8},
            {"src": "血食怪感染种", "dst": "神秘学家感染种", "relation": "转变为", "confidence": 0.85},
            {"src": "重塑之手", "dst": "超自然者血食怪", "relation": "进行转化实验", "confidence": 0.85},
        ],
    },
    # 11) 多瑙黎明号传闻 / 灵性之歌 / UTTU编辑空心木
    "74601555f124aed7": {
        "entities": [
            {"name": "多瑙黎明号", "type": "物品", "aliases": []},
            {"name": "三号车厢", "type": "地点", "aliases": []},
            {"name": "哭声", "type": "现象", "aliases": []},
            {"name": "歌声", "type": "现象", "aliases": []},
            {"name": "灵性之歌", "type": "概念", "aliases": []},
            {"name": "多瑙河", "type": "地点", "aliases": []},
            {"name": "赫尔曼", "type": "角色", "aliases": []},
            {"name": "UTTU", "type": "物品", "aliases": ["《UTTU》"]},
            {"name": "空心木", "type": "角色", "aliases": []},
            {"name": "血月", "type": "现象", "aliases": []},
        ],
        "relations": [
            {"src": "多瑙黎明号", "dst": "三号车厢", "relation": "包含", "confidence": 0.9},
            {"src": "多瑙黎明号", "dst": "哭声", "relation": "传出", "confidence": 0.8},
            {"src": "歌声", "dst": "灵性之歌", "relation": "疑似为", "confidence": 0.7},
            {"src": "赫尔曼", "dst": "多瑙黎明号", "relation": "曾任车长", "confidence": 0.85},
            {"src": "赫尔曼", "dst": "歌声", "relation": "发出呼救", "confidence": 0.7},
            {"src": "空心木", "dst": "UTTU", "relation": "编辑", "confidence": 0.9},
            {"src": "多瑙河", "dst": "灵性之歌", "relation": "流传", "confidence": 0.8},
        ],
    },
    # 12) 匿名论坛 / 西蒙娜家书（迪布瓦家）
    "035f3497e6455bba": {
        "entities": [
            {"name": "暴雨", "type": "事件", "aliases": []},
            {"name": "实用技术约翰", "type": "角色", "aliases": []},
            {"name": "西蒙娜", "type": "角色", "aliases": []},
            {"name": "西尔维", "type": "角色", "aliases": []},
            {"name": "马克西姆", "type": "角色", "aliases": []},
            {"name": "亚历山德罗", "type": "角色", "aliases": []},
            {"name": "墨尼克", "type": "角色", "aliases": []},
            {"name": "塞普内特斯", "type": "角色", "aliases": []},
            {"name": "海伦娜", "type": "角色", "aliases": []},
            {"name": "尚塔尔", "type": "角色", "aliases": []},
            {"name": "皮埃罗", "type": "角色", "aliases": []},
            {"name": "梅露西娜", "type": "角色", "aliases": []},
            {"name": "帕斯捷尔纳克", "type": "角色", "aliases": []},
            {"name": "二月", "type": "物品", "aliases": ["《二月》"]},
            {"name": "迪布瓦家", "type": "组织", "aliases": []},
            {"name": "普列谢茨克", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "实用技术约翰", "dst": "暴雨", "relation": "设计", "confidence": 0.7},
            {"src": "西尔维", "dst": "二月", "relation": "印象最深", "confidence": 0.7},
            {"src": "迪布瓦家", "dst": "西尔维", "relation": "包含", "confidence": 0.8},
            {"src": "马克西姆", "dst": "西尔维", "relation": "帮助", "confidence": 0.8},
            {"src": "亚历山德罗", "dst": "西尔维", "relation": "帮助", "confidence": 0.8},
        ],
    },
    # 13) 圣洛夫基金会报告 / 德克萨斯重塑之手间谍
    "93aefe63bcc349f3": {
        "entities": [
            {"name": "德克萨斯", "type": "地点", "aliases": ["德州"]},
            {"name": "圣洛夫基金会", "type": "组织", "aliases": []},
            {"name": "外派调查小组", "type": "组织", "aliases": []},
            {"name": "安德烈·西尔韦斯特", "type": "角色", "aliases": []},
            {"name": "重塑之手", "type": "组织", "aliases": []},
            {"name": "达拉斯", "type": "地点", "aliases": []},
            {"name": "奥斯汀", "type": "地点", "aliases": []},
            {"name": "休斯顿", "type": "地点", "aliases": []},
            {"name": "启明会", "type": "组织", "aliases": []},
            {"name": "淑女格蕾丝", "type": "角色", "aliases": []},
            {"name": "康斯坦丁", "type": "角色", "aliases": []},
            {"name": "77号公路", "type": "地点", "aliases": []},
            {"name": "易容魔药", "type": "物品", "aliases": []},
            {"name": "美国", "type": "地点", "aliases": []},
            {"name": "神秘学事项", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "安德烈·西尔韦斯特", "dst": "外派调查小组", "relation": "担任组长", "confidence": 0.9},
            {"src": "外派调查小组", "dst": "圣洛夫基金会", "relation": "汇报", "confidence": 0.85},
            {"src": "外派调查小组", "dst": "重塑之手", "relation": "发现间谍", "confidence": 0.85},
            {"src": "重塑之手", "dst": "启明会", "relation": "建立渠道", "confidence": 0.8},
            {"src": "启明会", "dst": "神秘学事项", "relation": "筹备", "confidence": 0.7},
            {"src": "淑女格蕾丝", "dst": "德克萨斯", "relation": "活动", "confidence": 0.85},
            {"src": "淑女格蕾丝", "dst": "重塑之手", "relation": "隶属", "confidence": 0.85},
            {"src": "康斯坦丁", "dst": "圣洛夫基金会", "relation": "任职", "confidence": 0.9},
            {"src": "康斯坦丁", "dst": "淑女格蕾丝", "relation": "知悉", "confidence": 0.8},
        ],
    },
    # 14) 斯塔夏与托马什的酒吧对话 / 奥尔加特调
    "e0f2d89a11231a82": {
        "entities": [
            {"name": "斯塔夏", "type": "角色", "aliases": []},
            {"name": "贝加尔湖", "type": "地点", "aliases": []},
            {"name": "托马什", "type": "角色", "aliases": []},
            {"name": "吊坠", "type": "物品", "aliases": []},
            {"name": "采油厂", "type": "地点", "aliases": []},
            {"name": "时空灾害", "type": "事件", "aliases": []},
            {"name": "奥尔加", "type": "角色", "aliases": []},
            {"name": "亚肖", "type": "角色", "aliases": []},
            {"name": "蓝图", "type": "角色", "aliases": []},
            {"name": "奠基石", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "斯塔夏", "dst": "托马什", "relation": "找回吊坠", "confidence": 0.7},
            {"src": "托马什", "dst": "采油厂", "relation": "前往", "confidence": 0.8},
            {"src": "亚肖", "dst": "奥尔加", "relation": "祝酒", "confidence": 0.7},
            {"src": "蓝图", "dst": "奥尔加", "relation": "祝酒", "confidence": 0.7},
        ],
    },
    # 15) 亚肖的醉酒回忆 / 罗莎的童年日记
    "3c3a45e642f00830": {
        "entities": [
            {"name": "蓝图", "type": "角色", "aliases": []},
            {"name": "亚肖", "type": "角色", "aliases": []},
            {"name": "卡米拉", "type": "角色", "aliases": []},
            {"name": "莱娜", "type": "角色", "aliases": ["小莱娜"]},
            {"name": "西德", "type": "地点", "aliases": []},
            {"name": "罗莎", "type": "角色", "aliases": []},
            {"name": "埃米尔", "type": "角色", "aliases": []},
            {"name": "安德烈", "type": "角色", "aliases": []},
            {"name": "钢厂", "type": "地点", "aliases": []},
            {"name": "烟囱", "type": "物品", "aliases": []},
            {"name": "花坛", "type": "地点", "aliases": []},
            {"name": "日记本", "type": "物品", "aliases": []},
            {"name": "电车", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "亚肖", "dst": "卡米拉", "relation": "分离", "confidence": 0.8},
            {"src": "亚肖", "dst": "莱娜", "relation": "父女", "confidence": 0.9},
            {"src": "卡米拉", "dst": "莱娜", "relation": "带走", "confidence": 0.85},
            {"src": "莱娜", "dst": "西德", "relation": "前往", "confidence": 0.8},
            {"src": "罗莎", "dst": "花坛", "relation": "见面", "confidence": 0.7},
            {"src": "埃米尔", "dst": "钢厂", "relation": "前往", "confidence": 0.7},
            {"src": "安德烈", "dst": "钢厂", "relation": "前往", "confidence": 0.7},
        ],
    },
    # 16) 水母拍拍使用须知 / 活性电力系统异变
    "ff9082f0906ae54c": {
        "entities": [
            {"name": "水母拍拍", "type": "物品", "aliases": []},
            {"name": "洛伦兹研究所", "type": "组织", "aliases": []},
            {"name": "神秘术式", "type": "概念", "aliases": []},
            {"name": "雨前", "type": "现象", "aliases": []},
            {"name": "活性电力系统", "type": "概念", "aliases": []},
            {"name": "面包店员", "type": "角色", "aliases": []},
            {"name": "医院", "type": "组织", "aliases": []},
            {"name": "礼拜堂", "type": "地点", "aliases": []},
            {"name": "银饰", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "水母拍拍", "dst": "洛伦兹研究所", "relation": "生产", "confidence": 0.9},
            {"src": "活性电力系统", "dst": "面包店员", "relation": "致使变异", "confidence": 0.8},
            {"src": "活性电力系统", "dst": "医院", "relation": "导致涌入", "confidence": 0.7},
            {"src": "活性电力系统", "dst": "礼拜堂", "relation": "蔓延至", "confidence": 0.7},
        ],
    },
    # 17) 诺瓦米奇建筑征用备案 / 东欧分部设立
    "74684f43bd890464": {
        "entities": [
            {"name": "主持者", "type": "角色", "aliases": []},
            {"name": "露西", "type": "角色", "aliases": []},
            {"name": "伊里内伊", "type": "角色", "aliases": []},
            {"name": "肯纳", "type": "角色", "aliases": []},
            {"name": "艾达", "type": "角色", "aliases": []},
            {"name": "芬恩", "type": "角色", "aliases": []},
            {"name": "诺瓦米奇", "type": "地点", "aliases": []},
            {"name": "圣洛夫基金会", "type": "组织", "aliases": []},
            {"name": "诺瓦米奇办事处", "type": "组织", "aliases": []},
            {"name": "东欧分部", "type": "组织", "aliases": []},
            {"name": "时空灾害", "type": "事件", "aliases": []},
            {"name": "备案", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "圣洛夫基金会", "dst": "诺瓦米奇办事处", "relation": "设立", "confidence": 0.85},
            {"src": "诺瓦米奇办事处", "dst": "东欧分部", "relation": "升格", "confidence": 0.9},
            {"src": "圣洛夫基金会", "dst": "诺瓦米奇办事处", "relation": "征用", "confidence": 0.85},
            {"src": "诺瓦米奇办事处", "dst": "时空灾害", "relation": "抵御", "confidence": 0.85},
            {"src": "露西", "dst": "备案", "relation": "列席", "confidence": 0.8},
            {"src": "伊里内伊", "dst": "备案", "relation": "列席", "confidence": 0.8},
            {"src": "肯纳", "dst": "备案", "relation": "列席", "confidence": 0.8},
            {"src": "艾达", "dst": "备案", "relation": "列席", "confidence": 0.8},
            {"src": "芬恩", "dst": "备案", "relation": "列席", "confidence": 0.8},
        ],
    },
    # 18) 拉普拉斯科算中心意见箱节选
    "49f2fd3e3fe3cdfd": {
        "entities": [
            {"name": "意见箱", "type": "物品", "aliases": []},
            {"name": "吉森", "type": "角色", "aliases": []},
            {"name": "麦考尔", "type": "角色", "aliases": []},
            {"name": "托马斯", "type": "角色", "aliases": []},
            {"name": "面具", "type": "物品", "aliases": []},
            {"name": "拉普拉斯科算中心", "type": "组织", "aliases": []},
            {"name": "蜘蛛", "type": "角色", "aliases": []},
            {"name": "马达加斯加发声蟑螂", "type": "角色", "aliases": []},
            {"name": "蛛尾巴", "type": "物品", "aliases": []},
            {"name": "液压腿", "type": "物品", "aliases": []},
            {"name": "露西", "type": "角色", "aliases": []},
            {"name": "字母一号", "type": "角色", "aliases": []},
            {"name": "汤姆·埃文斯", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "吉森", "dst": "面具", "relation": "形象用于", "confidence": 0.7},
            {"src": "麦考尔", "dst": "面具", "relation": "形象用于", "confidence": 0.7},
            {"src": "托马斯", "dst": "面具", "relation": "形象用于", "confidence": 0.7},
            {"src": "拉普拉斯科算中心", "dst": "面具", "relation": "启动方案", "confidence": 0.7},
            {"src": "蜘蛛", "dst": "马达加斯加发声蟑螂", "relation": "食用", "confidence": 0.85},
            {"src": "汤姆·埃文斯", "dst": "蜘蛛", "relation": "抱怨", "confidence": 0.7},
            {"src": "拉普拉斯科算中心", "dst": "蛛尾巴", "relation": "研究", "confidence": 0.8},
            {"src": "拉普拉斯科算中心", "dst": "液压腿", "relation": "研究", "confidence": 0.7},
            {"src": "字母一号", "dst": "露西", "relation": "提建议", "confidence": 0.85},
            {"src": "露西", "dst": "拉普拉斯科算中心", "relation": "隶属", "confidence": 0.7},
        ],
    },
    # 19) 圣洛夫基金会维也纳分部卷舌咒解除流程
    "1c5b4ec46eb85120": {
        "entities": [
            {"name": "拉普拉斯科算中心", "type": "组织", "aliases": []},
            {"name": "圣洛夫基金会维也纳分部", "type": "组织", "aliases": []},
            {"name": "奥匈帝国治安内务部", "type": "组织", "aliases": []},
            {"name": "奥匈帝国治安公共事务局", "type": "组织", "aliases": []},
            {"name": "社会责任监察组", "type": "组织", "aliases": []},
            {"name": "公共事务局", "type": "组织", "aliases": []},
            {"name": "危害防范办公室", "type": "组织", "aliases": []},
            {"name": "卷舌咒", "type": "概念", "aliases": []},
            {"name": "联合处理申请表", "type": "物品", "aliases": []},
            {"name": "罚单", "type": "物品", "aliases": []},
            {"name": "卷舌咒解除术式", "type": "概念", "aliases": []},
            {"name": "行政窗口", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "圣洛夫基金会维也纳分部", "dst": "奥匈帝国治安内务部", "relation": "下设", "confidence": 0.85},
            {"src": "奥匈帝国治安内务部", "dst": "奥匈帝国治安公共事务局", "relation": "下设", "confidence": 0.85},
            {"src": "奥匈帝国治安公共事务局", "dst": "社会责任监察组", "relation": "下设", "confidence": 0.85},
            {"src": "公共事务局", "dst": "危害防范办公室", "relation": "发往", "confidence": 0.85},
            {"src": "危害防范办公室", "dst": "行政窗口", "relation": "发通知", "confidence": 0.85},
            {"src": "卷舌咒", "dst": "卷舌咒解除术式", "relation": "经由解除", "confidence": 0.8},
        ],
    },
    # 20) 秘密通讯 / 重塑之手袭击第一防线学校 / 火渡船与平
    "f64c3956007dc775": {
        "entities": [
            {"name": "羽笔", "type": "物品", "aliases": []},
            {"name": "第一防线学校", "type": "组织", "aliases": []},
            {"name": "重塑之手", "type": "组织", "aliases": []},
            {"name": "基金会", "type": "组织", "aliases": []},
            {"name": "暴雨", "type": "事件", "aliases": []},
            {"name": "重塑·信徒", "type": "角色", "aliases": []},
            {"name": "无名者", "type": "角色", "aliases": []},
            {"name": "火渡船", "type": "角色", "aliases": []},
            {"name": "平", "type": "角色", "aliases": []},
            {"name": "格鲁托夫", "type": "角色", "aliases": []},
            {"name": "引导之人", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "重塑之手", "dst": "第一防线学校", "relation": "袭击", "confidence": 0.9},
            {"src": "无名者", "dst": "重塑·信徒", "relation": "讯问", "confidence": 0.8},
            {"src": "重塑·信徒", "dst": "重塑之手", "relation": "隶属", "confidence": 0.85},
            {"src": "平", "dst": "格鲁托夫", "relation": "提及", "confidence": 0.7},
            {"src": "引导之人", "dst": "基金会", "relation": "欲接触", "confidence": 0.7},
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
    print(f"[validate] 块 {len(RESULTS)}，悬空 {n}，未落地 {m}")
    print(f"[stats] 实体 {total_e}，关系 {total_r}，"
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
    print(f"[apply-missing-p14] 写入 {len(RESULTS)} 条，NOOP +{len(NOOP_ADD)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
