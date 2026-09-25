# -*- coding: utf-8 -*-
"""未抽取剧情块补抽 · 第 22 批（backfill2 batch_12，20 块，含 1 重复 hash、2 空内容块）。

用法：
  python scripts/apply_missing_p22.py            # 预演（悬空+落地自检）
  python scripts/apply_missing_p22.py --apply    # 写盘
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

# 空内容块（数值/技能/UI 页，无剧情可抽）：
#   89ff5ea46c24eec6 = 启明会信徒技能数值页（batch 第3、15块重复同一 hash）
#   8136873543035790 = 创伤加成/谣言散布等技能数值页
NOOP_ADD: list[str] = [
    "89ff5ea46c24eec6",
    "8136873543035790",
]

RESULTS: dict[str, dict] = {
    # 1) 芝诺方通话 · 林中的行迹与子弹与微积分
    "9ab8b6a339c7fc2b": {
        "entities": [
            {"name": "芝诺", "type": "组织", "aliases": ["芝诺方"]},
            {"name": "人类和平安全理事会", "type": "组织", "aliases": []},
            {"name": "司辰", "type": "角色", "aliases": []},
            {"name": "林中的行迹", "type": "概念", "aliases": []},
            {"name": "子弹与微积分", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "人类和平安全理事会", "dst": "芝诺", "relation": "授权", "confidence": 0.7},
            {"src": "芝诺", "dst": "司辰", "relation": "保障安全", "confidence": 0.7},
        ],
    },
    # 2) 子弹与将军对话 · 莫辛与纳甘取代卡拉什尼科夫
    "6081d6d306f6df82": {
        "entities": [
            {"name": "数学家", "type": "角色", "aliases": []},
            {"name": "将军", "type": "角色", "aliases": []},
            {"name": "大块头", "type": "概念", "aliases": []},
            {"name": "莫辛与纳甘", "type": "物品", "aliases": []},
            {"name": "卡拉什尼科夫", "type": "物品", "aliases": []},
            {"name": "未来", "type": "概念", "aliases": []},
            {"name": "子弹", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "莫辛与纳甘", "dst": "卡拉什尼科夫", "relation": "取代", "confidence": 0.8},
            {"src": "子弹", "dst": "未来", "relation": "追赶", "confidence": 0.7},
            {"src": "将军", "dst": "子弹", "relation": "结交", "confidence": 0.7},
            {"src": "数学家", "dst": "子弹", "relation": "交流", "confidence": 0.7},
        ],
    },
    # 3/15) 启明会信徒技能数值页（无剧情） → NOOP
    "89ff5ea46c24eec6": {
        "entities": [],
        "relations": [],
    },
    # 4) 老旧合影 · 伦敦帝国理工学院留学生纪念与渡轮航线
    "a054812efb60bb85": {
        "entities": [
            {"name": "合影", "type": "物品", "aliases": ["一张合影"]},
            {"name": "伦敦帝国理工学院", "type": "组织", "aliases": []},
            {"name": "露珠", "type": "角色", "aliases": []},
            {"name": "百合花", "type": "物品", "aliases": []},
            {"name": "直布罗陀海峡", "type": "地点", "aliases": []},
            {"name": "苏伊士运河", "type": "地点", "aliases": []},
            {"name": "渡轮", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "合影", "dst": "伦敦帝国理工学院", "relation": "纪念", "confidence": 0.7},
            {"src": "渡轮", "dst": "直布罗陀海峡", "relation": "穿过", "confidence": 0.7},
            {"src": "渡轮", "dst": "苏伊士运河", "relation": "穿过", "confidence": 0.7},
            {"src": "露珠", "dst": "百合花", "relation": "附着于", "confidence": 0.7},
        ],
    },
    # 5) 百合花与露珠 · 弦论研究者与小径②绿植
    "c21f61ca3f79577c": {
        "entities": [
            {"name": "百合花", "type": "物品", "aliases": []},
            {"name": "露珠", "type": "角色", "aliases": []},
            {"name": "弦论", "type": "概念", "aliases": []},
            {"name": "理论物理学", "type": "概念", "aliases": []},
            {"name": "猫", "type": "概念", "aliases": []},
            {"name": "盒子", "type": "物品", "aliases": []},
            {"name": "绿植", "type": "物品", "aliases": []},
            {"name": "学生宿舍", "type": "地点", "aliases": []},
            {"name": "康复中心", "type": "地点", "aliases": []},
            {"name": "宿舍保洁员", "type": "角色", "aliases": []},
            {"name": "小径②", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "百合花", "dst": "露珠", "relation": "教导", "confidence": 0.8},
            {"src": "猫", "dst": "盒子", "relation": "关入", "confidence": 0.7},
            {"src": "理论物理学", "dst": "弦论", "relation": "研究", "confidence": 0.7},
            {"src": "绿植", "dst": "学生宿舍", "relation": "搬离", "confidence": 0.7},
            {"src": "绿植", "dst": "康复中心", "relation": "移入", "confidence": 0.7},
            {"src": "宿舍保洁员", "dst": "绿植", "relation": "照料", "confidence": 0.7},
        ],
    },
    # 6) 阴影中的兽群 · 古怪洞穴许诺寓言与调停者的命运
    "58e8278630da1902": {
        "entities": [
            {"name": "阴影中的兽群", "type": "概念", "aliases": []},
            {"name": "林中", "type": "地点", "aliases": []},
            {"name": "盐柱", "type": "物品", "aliases": []},
            {"name": "古怪洞穴", "type": "地点", "aliases": []},
            {"name": "寓言", "type": "概念", "aliases": []},
            {"name": "调停者的命运", "type": "概念", "aliases": []},
            {"name": "太阳", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "阴影中的兽群", "dst": "林中", "relation": "蛰伏于", "confidence": 0.7},
            {"src": "古怪洞穴", "dst": "寓言", "relation": "许诺", "confidence": 0.7},
            {"src": "调停者的命运", "dst": "太阳", "relation": "关乎", "confidence": 0.7},
        ],
    },
    # 7) 基里姆地毯与海泡石烟斗 · 除错工具与错误之河
    "cc5c271d99d875e8": {
        "entities": [
            {"name": "基里姆地毯", "type": "物品", "aliases": []},
            {"name": "海泡石烟斗", "type": "物品", "aliases": []},
            {"name": "玻璃罐", "type": "物品", "aliases": []},
            {"name": "方糖", "type": "物品", "aliases": []},
            {"name": "垂直织机", "type": "物品", "aliases": []},
            {"name": "毛线结", "type": "物品", "aliases": []},
            {"name": "千年帝国", "type": "概念", "aliases": []},
            {"name": "尺规", "type": "物品", "aliases": []},
            {"name": "扳手", "type": "物品", "aliases": []},
            {"name": "修理箱", "type": "物品", "aliases": []},
            {"name": "错误", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "基里姆地毯", "dst": "海泡石烟斗", "relation": "同至", "confidence": 0.7},
            {"src": "基里姆地毯", "dst": "玻璃罐", "relation": "同至", "confidence": 0.7},
            {"src": "基里姆地毯", "dst": "方糖", "relation": "同至", "confidence": 0.7},
            {"src": "毛线结", "dst": "垂直织机", "relation": "织于", "confidence": 0.7},
            {"src": "尺规", "dst": "错误", "relation": "补救", "confidence": 0.7},
        ],
    },
    # 8) 除错师与红头发小姑娘 · 几何织机与绸缎玩伴
    "618b63be7c714e9f": {
        "entities": [
            {"name": "除错师", "type": "角色", "aliases": []},
            {"name": "红头发小姑娘", "type": "角色", "aliases": []},
            {"name": "尺规", "type": "物品", "aliases": []},
            {"name": "猫", "type": "概念", "aliases": []},
            {"name": "织机", "type": "物品", "aliases": []},
            {"name": "几何织机", "type": "物品", "aliases": []},
            {"name": "绸缎", "type": "物品", "aliases": []},
            {"name": "岛", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "除错师", "dst": "猫", "relation": "寻找", "confidence": 0.7},
            {"src": "红头发小姑娘", "dst": "除错师", "relation": "是", "confidence": 0.8},
            {"src": "红头发小姑娘", "dst": "尺规", "relation": "持有", "confidence": 0.7},
            {"src": "红头发小姑娘", "dst": "织机", "relation": "离开", "confidence": 0.7},
            {"src": "红头发小姑娘", "dst": "几何织机", "relation": "研习", "confidence": 0.7},
            {"src": "绸缎", "dst": "红头发小姑娘", "relation": "为玩伴", "confidence": 0.7},
        ],
    },
    # 9) 友谊与爆炸 · 古巴诗人、暗色带编织与乌斯怀亚监狱
    "53b9e89aa5f61793": {
        "entities": [
            {"name": "友谊", "type": "概念", "aliases": []},
            {"name": "爆炸", "type": "概念", "aliases": ['“爆炸”']},
            {"name": "古巴诗人", "type": "角色", "aliases": []},
            {"name": "军政府", "type": "组织", "aliases": []},
            {"name": "哥伦布", "type": "角色", "aliases": ['“哥伦布”']},
            {"name": "暗色带编织·卷二", "type": "物品", "aliases": []},
            {"name": "暗色带编织·卷三", "type": "物品", "aliases": []},
            {"name": "打字机记录#P5", "type": "物品", "aliases": []},
            {"name": "乌斯怀亚", "type": "地点", "aliases": []},
            {"name": "南极", "type": "地点", "aliases": []},
            {"name": "监狱", "type": "地点", "aliases": []},
            {"name": "神秘学家", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "古巴诗人", "dst": "爆炸", "relation": "经历", "confidence": 0.7},
            {"src": "军政府", "dst": "古巴诗人", "relation": "压制", "confidence": 0.7},
            {"src": "暗色带编织·卷二", "dst": "暗色带编织·卷三", "relation": "续作", "confidence": 0.7},
            {"src": "乌斯怀亚", "dst": "监狱", "relation": "构建", "confidence": 0.7},
            {"src": "乌斯怀亚", "dst": "南极", "relation": "邻近", "confidence": 0.7},
            {"src": "监狱", "dst": "神秘学家", "relation": "关押", "confidence": 0.8},
        ],
    },
    # 10) 重塑之手仪式材料 · 未寄出的信与图书博览会导览
    "c9144db9b961eedd": {
        "entities": [
            {"name": "吼狮之尾", "type": "物品", "aliases": []},
            {"name": "圣甲虫双翼", "type": "物品", "aliases": []},
            {"name": "努库泰澳族人的贝壳", "type": "物品", "aliases": []},
            {"name": "永生之泉", "type": "物品", "aliases": []},
            {"name": "重塑之手", "type": "组织", "aliases": []},
            {"name": "未寄出的信", "type": "物品", "aliases": []},
            {"name": "虚构集", "type": "角色", "aliases": []},
            {"name": "理性家族的崛起与衰落", "type": "物品", "aliases": ["《理性家族的崛起与衰落》"]},
            {"name": "盲眼的织工", "type": "角色", "aliases": []},
            {"name": "…图书…博览会导览", "type": "物品", "aliases": ["《…图书…博览会导览》"]},
            {"name": "青鸟", "type": "物品", "aliases": ["《青鸟》"]},
            {"name": "沃森·克鲁斯", "type": "角色", "aliases": []},
            {"name": "天空下的福克斯", "type": "物品", "aliases": ["《天空下的福克斯》"]},
            {"name": "塔德奥", "type": "角色", "aliases": []},
            {"name": "血怪", "type": "物品", "aliases": ["《血怪》"]},
            {"name": "阿威罗伊", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "重塑之手", "dst": "永生之泉", "relation": "使用", "confidence": 0.8},
            {"src": "吼狮之尾", "dst": "永生之泉", "relation": "配合", "confidence": 0.7},
            {"src": "圣甲虫双翼", "dst": "永生之泉", "relation": "配合", "confidence": 0.7},
            {"src": "努库泰澳族人的贝壳", "dst": "永生之泉", "relation": "配合", "confidence": 0.7},
            {"src": "未寄出的信", "dst": "虚构集", "relation": "致", "confidence": 0.8},
            {"src": "未寄出的信", "dst": "理性家族的崛起与衰落", "relation": "附上", "confidence": 0.8},
            {"src": "未寄出的信", "dst": "盲眼的织工", "relation": "提及", "confidence": 0.7},
            {"src": "…图书…博览会导览", "dst": "青鸟", "relation": "收录", "confidence": 0.8},
            {"src": "…图书…博览会导览", "dst": "天空下的福克斯", "relation": "收录", "confidence": 0.8},
            {"src": "…图书…博览会导览", "dst": "血怪", "relation": "收录", "confidence": 0.8},
            {"src": "青鸟", "dst": "沃森·克鲁斯", "relation": "作者", "confidence": 0.8},
            {"src": "天空下的福克斯", "dst": "塔德奥", "relation": "作者", "confidence": 0.8},
            {"src": "血怪", "dst": "阿威罗伊", "relation": "作者", "confidence": 0.8},
        ],
    },
    # 11) 将军与士兵 · 闸刀火药与愚人船上的疯癫
    "f92e4b497d1c61bf": {
        "entities": [
            {"name": "将军", "type": "角色", "aliases": []},
            {"name": "士兵", "type": "角色", "aliases": []},
            {"name": "闸刀", "type": "物品", "aliases": []},
            {"name": "刽子手", "type": "角色", "aliases": []},
            {"name": "子弹", "type": "物品", "aliases": []},
            {"name": "火药", "type": "物品", "aliases": []},
            {"name": "战壕", "type": "地点", "aliases": []},
            {"name": "枪膛", "type": "物品", "aliases": []},
            {"name": "思想", "type": "概念", "aliases": []},
            {"name": "拉美的大爆炸", "type": "事件", "aliases": []},
            {"name": "愚人船", "type": "物品", "aliases": []},
            {"name": "文明世界", "type": "概念", "aliases": []},
            {"name": "监狱", "type": "地点", "aliases": []},
            {"name": "病院", "type": "地点", "aliases": []},
            {"name": "疯癫", "type": "概念", "aliases": ['“疯癫”']},
        ],
        "relations": [
            {"src": "将军", "dst": "士兵", "relation": "信任", "confidence": 0.8},
            {"src": "刽子手", "dst": "闸刀", "relation": "拉下", "confidence": 0.8},
            {"src": "火药", "dst": "子弹", "relation": "击发", "confidence": 0.8},
            {"src": "思想", "dst": "枪膛", "relation": "钻入", "confidence": 0.8},
            {"src": "思想", "dst": "子弹", "relation": "先于", "confidence": 0.7},
            {"src": "愚人船", "dst": "文明世界", "relation": "被驱逐于", "confidence": 0.8},
            {"src": "愚人船", "dst": "监狱", "relation": "充作", "confidence": 0.7},
            {"src": "愚人船", "dst": "病院", "relation": "充作", "confidence": 0.7},
        ],
    },
    # 12) 无名垂钓者传闻记录 · 安洁莉娜与玛丽的目击
    "c91b13bacaa1b5fa": {
        "entities": [
            {"name": "无名垂钓者", "type": "角色", "aliases": ['“无名垂钓者”']},
            {"name": "安洁莉娜", "type": "角色", "aliases": []},
            {"name": "外部行动小队", "type": "组织", "aliases": []},
            {"name": "基金会", "type": "组织", "aliases": []},
            {"name": "基金会广场", "type": "地点", "aliases": []},
            {"name": "景观泉水", "type": "地点", "aliases": []},
            {"name": "玛丽", "type": "角色", "aliases": []},
            {"name": "医疗组", "type": "组织", "aliases": []},
            {"name": "苦目提取液3号", "type": "物品", "aliases": []},
            {"name": "仓库", "type": "地点", "aliases": []},
            {"name": "橡胶制钓鱼桶", "type": "物品", "aliases": []},
            {"name": "豹纹脂身鲇", "type": "角色", "aliases": []},
            {"name": "巡逻小队", "type": "组织", "aliases": []},
            {"name": "13号会客房", "type": "地点", "aliases": []},
            {"name": "渔具", "type": "物品", "aliases": []},
            {"name": "碳纤维羊毛芯鱼竿", "type": "物品", "aliases": []},
            {"name": "失物招领点", "type": "地点", "aliases": []},
            {"name": "吸盘清道夫", "type": "概念", "aliases": []},
            {"name": "神秘术人偶", "type": "物品", "aliases": []},
            {"name": "小径①", "type": "概念", "aliases": []},
            {"name": "海水河", "type": "地点", "aliases": []},
            {"name": "溪流", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "安洁莉娜", "dst": "外部行动小队", "relation": "隶属", "confidence": 0.8},
            {"src": "玛丽", "dst": "医疗组", "relation": "隶属", "confidence": 0.8},
            {"src": "安洁莉娜", "dst": "基金会广场", "relation": "途经", "confidence": 0.7},
            {"src": "玛丽", "dst": "仓库", "relation": "前往", "confidence": 0.7},
            {"src": "玛丽", "dst": "苦目提取液3号", "relation": "核验", "confidence": 0.8},
            {"src": "橡胶制钓鱼桶", "dst": "豹纹脂身鲇", "relation": "盛有", "confidence": 0.8},
            {"src": "巡逻小队", "dst": "13号会客房", "relation": "巡查", "confidence": 0.7},
            {"src": "渔具", "dst": "碳纤维羊毛芯鱼竿", "relation": "包含", "confidence": 0.8},
            {"src": "渔具", "dst": "失物招领点", "relation": "储存于", "confidence": 0.8},
            {"src": "基金会", "dst": "无名垂钓者", "relation": "存在", "confidence": 0.8},
            {"src": "无名垂钓者", "dst": "神秘术人偶", "relation": "疑似为", "confidence": 0.7},
        ],
    },
    # 13) 保利娜控诉火 · 种族主义与幸存者疗养院
    "aaf95a85293715ff": {
        "entities": [
            {"name": "火", "type": "概念", "aliases": []},
            {"name": "保利娜", "type": "角色", "aliases": []},
            {"name": "种族主义", "type": "概念", "aliases": []},
            {"name": "千足虫", "type": "概念", "aliases": []},
            {"name": "金发", "type": "概念", "aliases": []},
            {"name": "白衣裳", "type": "物品", "aliases": []},
            {"name": "加长林肯", "type": "物品", "aliases": []},
            {"name": "粉色油漆", "type": "物品", "aliases": []},
            {"name": "古代欧洲硬汉", "type": "概念", "aliases": []},
            {"name": "沙发", "type": "物品", "aliases": []},
            {"name": "狗", "type": "角色", "aliases": []},
            {"name": "鼻屎", "type": "物品", "aliases": []},
            {"name": "基金会职员", "type": "角色", "aliases": []},
            {"name": "文件夹", "type": "物品", "aliases": []},
            {"name": "幸存者", "type": "角色", "aliases": []},
            {"name": "疗养院", "type": "地点", "aliases": []},
            {"name": "跟访记录", "type": "物品", "aliases": []},
            {"name": "感谢信", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "种族主义", "dst": "千足虫", "relation": "如同", "confidence": 0.7},
            {"src": "种族主义", "dst": "保利娜", "relation": "侵蚀", "confidence": 0.8},
            {"src": "保利娜", "dst": "火", "relation": "控诉", "confidence": 0.8},
            {"src": "基金会职员", "dst": "保利娜", "relation": "询问", "confidence": 0.7},
            {"src": "基金会职员", "dst": "文件夹", "relation": "翻动", "confidence": 0.7},
            {"src": "幸存者", "dst": "疗养院", "relation": "入住", "confidence": 0.8},
            {"src": "跟访记录", "dst": "幸存者", "relation": "记录", "confidence": 0.7},
            {"src": "千足虫", "dst": "金发", "relation": "钻入", "confidence": 0.7},
        ],
    },
    # 14) 火与燃烧共存 · 小保利娜转变与最高裁判所解释
    "7a92582d8c92785f": {
        "entities": [
            {"name": "火", "type": "概念", "aliases": []},
            {"name": "保利娜", "type": "角色", "aliases": []},
            {"name": "燃烧", "type": "概念", "aliases": ["‘燃烧’"]},
            {"name": "公职责任", "type": "概念", "aliases": []},
            {"name": "个人责任", "type": "概念", "aliases": []},
            {"name": "仇恨", "type": "概念", "aliases": []},
            {"name": "少数族群", "type": "概念", "aliases": []},
            {"name": "身体力行", "type": "概念", "aliases": []},
            {"name": "小保利娜", "type": "角色", "aliases": []},
            {"name": "绿眼珠子", "type": "概念", "aliases": []},
            {"name": "薯片调料粉", "type": "物品", "aliases": []},
            {"name": "既视感", "type": "概念", "aliases": []},
            {"name": "天秤", "type": "物品", "aliases": []},
            {"name": "雀鸟", "type": "角色", "aliases": []},
            {"name": "雪地", "type": "地点", "aliases": []},
            {"name": "最高裁判所", "type": "组织", "aliases": []},
            {"name": "冗长演讲", "type": "概念", "aliases": []},
            {"name": "解释", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "保利娜", "dst": "火", "relation": "共存", "confidence": 0.8},
            {"src": "燃烧", "dst": "火", "relation": "属于", "confidence": 0.7},
            {"src": "小保利娜", "dst": "保利娜", "relation": "是", "confidence": 0.9},
            {"src": "小保利娜", "dst": "绿眼珠子", "relation": "拥有", "confidence": 0.8},
            {"src": "最高裁判所", "dst": "冗长演讲", "relation": "解释", "confidence": 0.8},
            {"src": "最高裁判所", "dst": "解释", "relation": "发布", "confidence": 0.8},
        ],
    },
    # 16) 只有灰烬的破屋 · 破烂纺车与钟表匠
    "26bed9f2799e2b5d": {
        "entities": [
            {"name": "破屋", "type": "地点", "aliases": []},
            {"name": "纺车", "type": "物品", "aliases": []},
            {"name": "钟表匠", "type": "角色", "aliases": []},
            {"name": "战利品", "type": "物品", "aliases": []},
            {"name": "废墟", "type": "地点", "aliases": []},
            {"name": "铁锈", "type": "物品", "aliases": []},
            {"name": "焦臭", "type": "概念", "aliases": []},
            {"name": "战争", "type": "概念", "aliases": []},
            {"name": "茶", "type": "物品", "aliases": []},
            {"name": "点心", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "纺车", "dst": "战利品", "relation": "为", "confidence": 0.8},
            {"src": "破屋", "dst": "废墟", "relation": "位于", "confidence": 0.7},
            {"src": "战争", "dst": "纺车", "relation": "产出", "confidence": 0.7},
            {"src": "茶", "dst": "点心", "relation": "并列", "confidence": 0.7},
        ],
    },
    # 17) 创伤加成等技能数值页（无剧情） → NOOP
    "8136873543035790": {
        "entities": [],
        "relations": [],
    },
    # 18) 玛蒂尔达与暴雨 · 迷思海、劳伦·罗西、费利西安与神来之笔
    "323a27e2132e5bfa": {
        "entities": [
            {"name": "玛蒂尔达", "type": "角色", "aliases": []},
            {"name": "暴雨", "type": "现象", "aliases": ['“暴雨”']},
            {"name": "迷思海", "type": "地点", "aliases": []},
            {"name": "劳伦·罗西", "type": "角色", "aliases": []},
            {"name": "费利西安", "type": "角色", "aliases": []},
            {"name": "灰调蓝", "type": "角色", "aliases": []},
            {"name": "目击记录", "type": "物品", "aliases": []},
            {"name": "神来之笔", "type": "概念", "aliases": []},
            {"name": "画家", "type": "角色", "aliases": []},
            {"name": "立体主义构成", "type": "概念", "aliases": []},
            {"name": "新时代缪斯", "type": "概念", "aliases": []},
            {"name": "艺术之神", "type": "概念", "aliases": []},
            {"name": "广场", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "暴雨", "dst": "迷思海", "relation": "导致", "confidence": 0.8},
            {"src": "劳伦·罗西", "dst": "迷思海", "relation": "目睹", "confidence": 0.8},
            {"src": "费利西安", "dst": "迷思海", "relation": "被困于", "confidence": 0.8},
            {"src": "劳伦·罗西", "dst": "费利西安", "relation": "合作", "confidence": 0.7},
            {"src": "画家", "dst": "广场", "relation": "写生于", "confidence": 0.8},
            {"src": "画家", "dst": "神来之笔", "relation": "经历", "confidence": 0.7},
            {"src": "画家", "dst": "艺术之神", "relation": "视为", "confidence": 0.7},
            {"src": "神来之笔", "dst": "立体主义构成", "relation": "具有", "confidence": 0.7},
            {"src": "神来之笔", "dst": "新时代缪斯", "relation": "具有", "confidence": 0.7},
            {"src": "灰调蓝", "dst": "暴雨", "relation": "被毁于", "confidence": 0.7},
        ],
    },
    # 19) 鹰派领袖与伊里内伊 · 金色饥荒诗篇与顿河
    "c7295cc2fbedc1a1": {
        "entities": [
            {"name": "鹰派", "type": "概念", "aliases": ['“鹰派”']},
            {"name": "将军", "type": "角色", "aliases": []},
            {"name": "顿河", "type": "地点", "aliases": []},
            {"name": "黑海", "type": "地点", "aliases": []},
            {"name": "波罗的海", "type": "地点", "aliases": []},
            {"name": "水线", "type": "概念", "aliases": []},
            {"name": "伊里内伊", "type": "角色", "aliases": []},
            {"name": "金色饥荒", "type": "概念", "aliases": ['“金色饥荒”']},
            {"name": "诗篇", "type": "物品", "aliases": []},
            {"name": "悲伤的麦子们", "type": "概念", "aliases": []},
            {"name": "无名诗人", "type": "角色", "aliases": []},
            {"name": "铭印", "type": "概念", "aliases": []},
            {"name": "西线", "type": "地点", "aliases": []},
            {"name": "东线", "type": "地点", "aliases": []},
            {"name": "雏鸟", "type": "角色", "aliases": []},
            {"name": "成鸟", "type": "角色", "aliases": []},
            {"name": "大礼帽", "type": "物品", "aliases": []},
            {"name": "母亲", "type": "角色", "aliases": []},
            {"name": "裂缝", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "伊里内伊", "dst": "将军", "relation": "联络", "confidence": 0.8},
            {"src": "顿河", "dst": "裂缝", "relation": "如同", "confidence": 0.8},
            {"src": "黑海", "dst": "水线", "relation": "关乎", "confidence": 0.7},
            {"src": "波罗的海", "dst": "水线", "relation": "关乎", "confidence": 0.7},
            {"src": "伊里内伊", "dst": "顿河", "relation": "关注", "confidence": 0.7},
            {"src": "金色饥荒", "dst": "诗篇", "relation": "催生", "confidence": 0.7},
            {"src": "诗篇", "dst": "悲伤的麦子们", "relation": "收录", "confidence": 0.8},
            {"src": "诗篇", "dst": "无名诗人", "relation": "作者", "confidence": 0.8},
            {"src": "无名诗人", "dst": "顿河", "relation": "流浪于", "confidence": 0.8},
            {"src": "雏鸟", "dst": "成鸟", "relation": "追随", "confidence": 0.7},
        ],
    },
    # 20) 格鲁托夫与伊戈尔将军 · 庇护所、别列格勒与狮鹫军更名
    "863a67b007905a00": {
        "entities": [
            {"name": "格鲁托夫", "type": "角色", "aliases": []},
            {"name": "伊戈尔将军", "type": "角色", "aliases": ["伊戈尔"]},
            {"name": "重塑之手", "type": "组织", "aliases": []},
            {"name": "庇护所", "type": "地点", "aliases": ['“庇护所”']},
            {"name": "指挥部", "type": "组织", "aliases": []},
            {"name": "精锐部队", "type": "组织", "aliases": []},
            {"name": "顿河下游", "type": "地点", "aliases": []},
            {"name": "别列格勒", "type": "地点", "aliases": []},
            {"name": "前线", "type": "地点", "aliases": []},
            {"name": "情报部门", "type": "组织", "aliases": []},
            {"name": "近卫团", "type": "组织", "aliases": []},
            {"name": "狮鹫军", "type": "组织", "aliases": ['“狮鹫军”']},
            {"name": "莫莉德尔", "type": "角色", "aliases": ["莫莉德尔副官", "莫莉德尔中尉"]},
            {"name": "关键词", "type": "概念", "aliases": []},
            {"name": "十四行诗", "type": "角色", "aliases": []},
            {"name": "司辰", "type": "角色", "aliases": []},
            {"name": "刻雷乌斯", "type": "角色", "aliases": ["刻雷乌斯先生"]},
            {"name": "兀尔德", "type": "概念", "aliases": []},
            {"name": "琥珀屋", "type": "地点", "aliases": []},
            {"name": "基金会", "type": "组织", "aliases": []},
        ],
        "relations": [
            {"src": "格鲁托夫", "dst": "重塑之手", "relation": "合作", "confidence": 0.8},
            {"src": "伊戈尔将军", "dst": "格鲁托夫", "relation": "列为危险", "confidence": 0.8},
            {"src": "伊戈尔将军", "dst": "庇护所", "relation": "建设", "confidence": 0.7},
            {"src": "伊戈尔将军", "dst": "精锐部队", "relation": "率领", "confidence": 0.8},
            {"src": "精锐部队", "dst": "别列格勒", "relation": "前往", "confidence": 0.8},
            {"src": "别列格勒", "dst": "顿河下游", "relation": "位于", "confidence": 0.8},
            {"src": "精锐部队", "dst": "前线", "relation": "协作", "confidence": 0.7},
            {"src": "精锐部队", "dst": "情报部门", "relation": "协作", "confidence": 0.7},
            {"src": "指挥部", "dst": "伊戈尔将军", "relation": "通报", "confidence": 0.7},
            {"src": "近卫团", "dst": "狮鹫军", "relation": "更名", "confidence": 0.9},
            {"src": "莫莉德尔", "dst": "近卫团", "relation": "受理", "confidence": 0.7},
            {"src": "十四行诗", "dst": "司辰", "relation": "留言", "confidence": 0.8},
            {"src": "十四行诗", "dst": "刻雷乌斯", "relation": "提及", "confidence": 0.7},
            {"src": "基金会", "dst": "关键词", "relation": "出现于", "confidence": 0.7},
            {"src": "琥珀屋", "dst": "关键词", "relation": "出现于", "confidence": 0.7},
            {"src": "兀尔德", "dst": "关键词", "relation": "出现于", "confidence": 0.7},
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
    noop = sum(1 for d in RESULTS.values() if not (d.get("entities") or d.get("relations")))
    print(f"[validate] 块 {len(RESULTS)}（含NOOP {noop}），悬空 {n}，未落地 {m}")
    print(f"[stats] 非空块 {nonempty}，实体 {total_e}，关系 {total_r}，空块 {noop}")

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
    print(f"[apply-missing-p22] 写入 {len(RESULTS)} 条，NOOP +{len(NOOP_ADD)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
