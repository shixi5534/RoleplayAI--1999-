# -*- coding: utf-8 -*-
"""未抽取剧情块补抽 · 第 15 批（backfill2 batch_05，20 块）。

用法：
  python scripts/apply_missing_p15.py            # 预演（悬空+落地自检）
  python scripts/apply_missing_p15.py --apply    # 写盘
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

# 本批 2 块为技能/战斗数值页（无剧情），加入 NOOP 确认集合。
NOOP_ADD: list[str] = [
    "ff3bd3b5c6618c5b",
    "00fc0b27403a25da",
]

RESULTS: dict[str, dict] = {
    # 1) 平/火渡船密谈 · 仿神体科研请愿表
    "06695eb735021afd": {
        "entities": [
            {"name": "平", "type": "角色", "aliases": []},
            {"name": "火渡船", "type": "角色", "aliases": []},
            {"name": "格鲁托夫", "type": "角色", "aliases": []},
            {"name": "引导之人", "type": "角色", "aliases": []},
            {"name": "基金会", "type": "组织", "aliases": []},
            {"name": "神秘学家", "type": "概念", "aliases": []},
            {"name": "理性的狂热", "type": "角色", "aliases": []},
            {"name": "诺谛卡", "type": "角色", "aliases": ["诺谛卡女士"]},
            {"name": "拉普拉斯科算中心", "type": "组织", "aliases": []},
            {"name": "仿神体", "type": "概念", "aliases": []},
            {"name": "苦目糖", "type": "物品", "aliases": []},
            {"name": "科研立项请愿表", "type": "物品", "aliases": ['"仿神体"科研立项请愿表']},
        ],
        "relations": [
            {"src": "平", "dst": "基金会", "relation": "意图摧毁", "confidence": 0.7},
            {"src": "火渡船", "dst": "基金会", "relation": "反对袭击", "confidence": 0.8},
            {"src": "平", "dst": "格鲁托夫", "relation": "提及", "confidence": 0.7},
            {"src": "平", "dst": "引导之人", "relation": "提及", "confidence": 0.7},
            {"src": "基金会", "dst": "神秘学家", "relation": "庇护", "confidence": 0.7},
            {"src": "拉普拉斯科算中心", "dst": "诺谛卡", "relation": "致函", "confidence": 0.8},
            {"src": "拉普拉斯科算中心", "dst": "仿神体", "relation": "研究", "confidence": 0.9},
            {"src": "仿神体", "dst": "苦目糖", "relation": "关联测试", "confidence": 0.7},
        ],
    },
    # 2) 出口规划 · 矿场能源与操作守则
    "59030625c2064ad8": {
        "entities": [
            {"name": "鲁萨尔卡", "type": "概念", "aliases": []},
            {"name": "出口规划", "type": "物品", "aliases": ["潮湿的纸张"]},
            {"name": "板条箱", "type": "物品", "aliases": []},
            {"name": "寒风", "type": "现象", "aliases": []},
            {"name": "原煤", "type": "物品", "aliases": []},
            {"name": "水煤气", "type": "物品", "aliases": []},
            {"name": "煤灰", "type": "物品", "aliases": []},
            {"name": "焦煤", "type": "物品", "aliases": []},
            {"name": "精煤", "type": "物品", "aliases": []},
            {"name": "叶甫根尼", "type": "角色", "aliases": ["叶甫根尼同志"]},
            {"name": "煤矿", "type": "地点", "aliases": []},
            {"name": "南方", "type": "地点", "aliases": []},
            {"name": "矿道", "type": "地点", "aliases": []},
            {"name": "矿场职工操作行为守则", "type": "物品", "aliases": ["《矿场职工操作行为守则》"]},
            {"name": "口岸", "type": "地点", "aliases": []},
            {"name": "工厂", "type": "地点", "aliases": []},
            {"name": "工人", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "出口规划", "dst": "口岸", "relation": "遗失于", "confidence": 0.8},
            {"src": "原煤", "dst": "水煤气", "relation": "可制成", "confidence": 0.85},
            {"src": "精煤", "dst": "南方", "relation": "需求于", "confidence": 0.8},
            {"src": "矿场职工操作行为守则", "dst": "工人", "relation": "规范", "confidence": 0.7},
        ],
    },
    # 3) 劳动食堂 · 维拉休息与阿夫西维来访
    "b6500b2035995998": {
        "entities": [
            {"name": "劳动食堂", "type": "地点", "aliases": []},
            {"name": "维拉", "type": "角色", "aliases": []},
            {"name": "厨师", "type": "角色", "aliases": []},
            {"name": "西蒙诺夫", "type": "角色", "aliases": ["西蒙诺夫同志"]},
            {"name": "手风琴", "type": "物品", "aliases": []},
            {"name": "绘画工具", "type": "物品", "aliases": []},
            {"name": "阿夫西维", "type": "角色", "aliases": []},
            {"name": "乌里扬娜", "type": "角色", "aliases": []},
            {"name": "向日葵", "type": "角色", "aliases": []},
            {"name": "命名日", "type": "角色", "aliases": []},
            {"name": "庆祝会", "type": "事件", "aliases": []},
            {"name": "演出彩排", "type": "事件", "aliases": []},
        ],
        "relations": [
            {"src": "维拉", "dst": "手风琴", "relation": "拥有", "confidence": 0.8},
            {"src": "维拉", "dst": "绘画工具", "relation": "携带", "confidence": 0.7},
            {"src": "西蒙诺夫", "dst": "手风琴", "relation": "评价", "confidence": 0.7},
            {"src": "阿夫西维", "dst": "维拉", "relation": "拜访", "confidence": 0.8},
            {"src": "阿夫西维", "dst": "乌里扬娜", "relation": "提及", "confidence": 0.7},
            {"src": "命名日", "dst": "维拉", "relation": "辞别", "confidence": 0.7},
            {"src": "维拉", "dst": "手风琴", "relation": "演奏", "confidence": 0.8},
        ],
    },
    # 4) 北方哨歌 · 命名日告别与来亚什基之行
    "eef4fb23f06a4175": {
        "entities": [
            {"name": "北方哨歌", "type": "角色", "aliases": ["北方哨歌同志"]},
            {"name": "理线学学者", "type": "概念", "aliases": []},
            {"name": "维拉", "type": "角色", "aliases": []},
            {"name": "阿夫西维", "type": "角色", "aliases": []},
            {"name": "乌里扬娜", "type": "角色", "aliases": []},
            {"name": "命名日", "type": "角色", "aliases": []},
            {"name": "基金会", "type": "组织", "aliases": []},
            {"name": "来亚什基", "type": "地点", "aliases": []},
            {"name": "向日葵", "type": "角色", "aliases": []},
            {"name": "雪人", "type": "物品", "aliases": []},
            {"name": "妈妈", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "北方哨歌", "dst": "理线学学者", "relation": "是", "confidence": 0.9},
            {"src": "维拉", "dst": "北方哨歌", "relation": "计划介绍", "confidence": 0.7},
            {"src": "命名日", "dst": "维拉", "relation": "承诺造访", "confidence": 0.7},
            {"src": "命名日", "dst": "基金会", "relation": "提供培训", "confidence": 0.7},
            {"src": "阿夫西维", "dst": "来亚什基", "relation": "前往", "confidence": 0.7},
            {"src": "阿夫西维", "dst": "基金会", "relation": "提及", "confidence": 0.7},
            {"src": "维拉", "dst": "基金会", "relation": "计划拜访", "confidence": 0.7},
            {"src": "阿夫西维", "dst": "妈妈", "relation": "学自", "confidence": 0.7},
            {"src": "向日葵", "dst": "阿夫西维", "relation": "伴随", "confidence": 0.7},
        ],
    },
    # 5) 奇星/菲林士多访谈 · 波蒂埃与梁月召唤强梁
    "a9506c1541dfe642": {
        "entities": [
            {"name": "奇星", "type": "角色", "aliases": ["奇星女士"]},
            {"name": "菲林士多", "type": "角色", "aliases": []},
            {"name": "波蒂埃", "type": "角色", "aliases": []},
            {"name": "梁月", "type": "角色", "aliases": []},
            {"name": "变色龙通信器", "type": "物品", "aliases": []},
            {"name": "强梁", "type": "角色", "aliases": []},
            {"name": "大哥大", "type": "物品", "aliases": []},
            {"name": "电话", "type": "物品", "aliases": []},
            {"name": "上一代传人", "type": "角色", "aliases": []},
            {"name": "皮影戏", "type": "概念", "aliases": []},
            {"name": "电视", "type": "物品", "aliases": []},
            {"name": "C07", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "奇星", "dst": "C07", "relation": "出演", "confidence": 0.8},
            {"src": "菲林士多", "dst": "C07", "relation": "参与", "confidence": 0.7},
            {"src": "波蒂埃", "dst": "梁月", "relation": "询问", "confidence": 0.7},
            {"src": "梁月", "dst": "变色龙通信器", "relation": "拥有", "confidence": 0.8},
            {"src": "梁月", "dst": "强梁", "relation": "召唤", "confidence": 0.9},
            {"src": "大哥大", "dst": "强梁", "relation": "用于召唤", "confidence": 0.8},
            {"src": "上一代传人", "dst": "强梁", "relation": "用皮影戏召唤", "confidence": 0.8},
            {"src": "波蒂埃", "dst": "电视", "relation": "观看", "confidence": 0.7},
        ],
    },
    # 6) 针人袭击棍骗约翰 · 拉普拉斯康复中心合作医院
    "001a53b2ff8bd387": {
        "entities": [
            {"name": "波蒂埃", "type": "角色", "aliases": []},
            {"name": "梁月", "type": "角色", "aliases": []},
            {"name": "强梁", "type": "角色", "aliases": []},
            {"name": "奇星", "type": "角色", "aliases": ["奇星女士"]},
            {"name": "针人", "type": "角色", "aliases": []},
            {"name": "棍骗约翰", "type": "角色", "aliases": []},
            {"name": "警员", "type": "角色", "aliases": []},
            {"name": "市民", "type": "角色", "aliases": ["普通市民"]},
            {"name": "知情人士", "type": "角色", "aliases": []},
            {"name": "群众", "type": "角色", "aliases": []},
            {"name": "C07", "type": "物品", "aliases": []},
            {"name": "拉普拉斯康复中心合作医院", "type": "组织", "aliases": []},
            {"name": "医生", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "波蒂埃", "dst": "强梁", "relation": "感谢", "confidence": 0.7},
            {"src": "梁月", "dst": "强梁", "relation": "召唤", "confidence": 0.9},
            {"src": "针人", "dst": "棍骗约翰", "relation": "袭击", "confidence": 0.85},
            {"src": "市民", "dst": "针人", "relation": "支持", "confidence": 0.8},
            {"src": "奇星", "dst": "市民", "relation": "接受采访", "confidence": 0.7},
            {"src": "医生", "dst": "拉普拉斯康复中心合作医院", "relation": "任职于", "confidence": 0.7},
        ],
    },
    # 7) 乌尔里希与嚼嚼松果通讯 · 拉普拉斯科算中心邀约
    "2207e6135baa73a9": {
        "entities": [
            {"name": "乌尔里希", "type": "角色", "aliases": []},
            {"name": "司辰", "type": "角色", "aliases": []},
            {"name": "嚼嚼松果", "type": "角色", "aliases": ["嚼嚼松果中士"]},
            {"name": "基金会", "type": "组织", "aliases": []},
            {"name": "莫莉德尔", "type": "角色", "aliases": ["莫莉德尔中尉"]},
            {"name": "短波电台", "type": "物品", "aliases": []},
            {"name": "遗址城", "type": "地点", "aliases": []},
            {"name": "雪坡", "type": "地点", "aliases": []},
            {"name": "拉普拉斯科算中心", "type": "组织", "aliases": []},
            {"name": "司辰小队", "type": "组织", "aliases": []},
        ],
        "relations": [
            {"src": "乌尔里希", "dst": "司辰", "relation": "呼叫", "confidence": 0.8},
            {"src": "乌尔里希", "dst": "司辰", "relation": "报告", "confidence": 0.8},
            {"src": "嚼嚼松果", "dst": "莫莉德尔", "relation": "效忠", "confidence": 0.85},
            {"src": "乌尔里希", "dst": "嚼嚼松果", "relation": "邀请加入", "confidence": 0.8},
            {"src": "乌尔里希", "dst": "基金会", "relation": "隶属", "confidence": 0.7},
            {"src": "司辰小队", "dst": "司辰", "relation": "包含", "confidence": 0.8},
        ],
    },
    # 8) 乌卢鲁运动会项目清单 · 叮咚快报抹黑复兴小队
    "dbdae99d76c1e1c9": {
        "entities": [
            {"name": "乌卢鲁运动会", "type": "事件", "aliases": []},
            {"name": "乌卢鲁运动会体育项目清单", "type": "物品", "aliases": []},
            {"name": "卡洛斯·卡斯蒂洛", "type": "角色", "aliases": ["古巴飞鼠"]},
            {"name": "狼群先生", "type": "角色", "aliases": []},
            {"name": "飞跃树梢", "type": "概念", "aliases": []},
            {"name": "飞碟", "type": "物品", "aliases": []},
            {"name": "木马", "type": "物品", "aliases": []},
            {"name": "人造卫星", "type": "物品", "aliases": []},
            {"name": "德鲁伊", "type": "角色", "aliases": []},
            {"name": "水怪", "type": "角色", "aliases": []},
            {"name": "500米水怪障碍赛", "type": "概念", "aliases": []},
            {"name": "水藻", "type": "物品", "aliases": []},
            {"name": "叮咚快报", "type": "物品", "aliases": ["《叮咚快报》"]},
            {"name": "复兴小队", "type": "组织", "aliases": []},
            {"name": "兔女郎", "type": "角色", "aliases": []},
            {"name": "市政厅", "type": "地点", "aliases": []},
            {"name": "公务员", "type": "角色", "aliases": []},
            {"name": "医疗站", "type": "地点", "aliases": []},
            {"name": "裁判", "type": "角色", "aliases": []},
            {"name": "观众", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "乌卢鲁运动会", "dst": "乌卢鲁运动会体育项目清单", "relation": "发布", "confidence": 0.8},
            {"src": "卡洛斯·卡斯蒂洛", "dst": "飞跃树梢", "relation": "缔造纪录", "confidence": 0.85},
            {"src": "狼群先生", "dst": "卡洛斯·卡斯蒂洛", "relation": "超越", "confidence": 0.7},
            {"src": "德鲁伊", "dst": "乌卢鲁运动会", "relation": "参赛", "confidence": 0.7},
            {"src": "水怪", "dst": "500米水怪障碍赛", "relation": "用于", "confidence": 0.8},
            {"src": "叮咚快报", "dst": "复兴小队", "relation": "造谣抹黑", "confidence": 0.8},
            {"src": "复兴小队", "dst": "市政厅", "relation": "大闹", "confidence": 0.8},
            {"src": "兔女郎", "dst": "复兴小队", "relation": "隶属", "confidence": 0.7},
        ],
    },
    # 9) 本耶普撒谎实验 · 热土运动编年史提及乌卢鲁运动会
    "a06fb46bbc2340dd": {
        "entities": [
            {"name": "本耶普", "type": "角色", "aliases": []},
            {"name": "志愿者", "type": "角色", "aliases": []},
            {"name": "水族箱", "type": "物品", "aliases": []},
            {"name": "YP-07", "type": "角色", "aliases": []},
            {"name": "香蕉", "type": "物品", "aliases": []},
            {"name": "图纸卡片", "type": "物品", "aliases": []},
            {"name": "热土运动编年史", "type": "物品", "aliases": ["《热土运动编年史》"]},
            {"name": "乌卢鲁运动会", "type": "事件", "aliases": []},
            {"name": "桉树", "type": "物品", "aliases": []},
            {"name": "石片", "type": "物品", "aliases": []},
            {"name": "红木枝", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "YP-07", "dst": "本耶普", "relation": "是", "confidence": 0.9},
            {"src": "YP-07", "dst": "香蕉", "relation": "偏好", "confidence": 0.7},
            {"src": "水族箱", "dst": "本耶普", "relation": "饲养", "confidence": 0.7},
            {"src": "热土运动编年史", "dst": "乌卢鲁运动会", "relation": "提及", "confidence": 0.8},
            {"src": "志愿者", "dst": "本耶普", "relation": "测试", "confidence": 0.7},
            {"src": "图纸卡片", "dst": "香蕉", "relation": "显示", "confidence": 0.7},
        ],
    },
    # 10) 波拉比与本耶普偶遇 · 凯特背包与复兴小队
    "ff1c3ba5d7541ff3": {
        "entities": [
            {"name": "水利工程申报文档", "type": "物品", "aliases": []},
            {"name": "鸸鹋", "type": "角色", "aliases": []},
            {"name": "波拉比", "type": "角色", "aliases": []},
            {"name": "单马尾女孩儿", "type": "角色", "aliases": []},
            {"name": "仙女苹果", "type": "物品", "aliases": []},
            {"name": "复兴小队", "type": "组织", "aliases": []},
            {"name": "凯特", "type": "角色", "aliases": []},
            {"name": "背包", "type": "物品", "aliases": []},
            {"name": "政府文员", "type": "角色", "aliases": []},
            {"name": "本耶普", "type": "角色", "aliases": []},
            {"name": "乔迁派对", "type": "事件", "aliases": []},
        ],
        "relations": [
            {"src": "波拉比", "dst": "鸸鹋", "relation": "是", "confidence": 0.8},
            {"src": "单马尾女孩儿", "dst": "波拉比", "relation": "命名", "confidence": 0.7},
            {"src": "波拉比", "dst": "政府文员", "relation": "帮助", "confidence": 0.7},
            {"src": "凯特", "dst": "背包", "relation": "遗忘", "confidence": 0.7},
            {"src": "凯特", "dst": "乔迁派对", "relation": "参加", "confidence": 0.7},
            {"src": "波拉比", "dst": "本耶普", "relation": "偶遇", "confidence": 0.8},
            {"src": "政府文员", "dst": "背包", "relation": "归还", "confidence": 0.7},
        ],
    },
    # 11) 星之眼/宽檐帽 · 祖母与小沙丝绒谈田径与盛装骑术赛
    "9b03b1293ff27f38": {
        "entities": [
            {"name": "星之眼", "type": "角色", "aliases": []},
            {"name": "宽檐帽", "type": "角色", "aliases": []},
            {"name": "飞碟", "type": "物品", "aliases": []},
            {"name": "细框眼镜", "type": "物品", "aliases": []},
            {"name": "马科尔", "type": "角色", "aliases": []},
            {"name": "道歉信", "type": "物品", "aliases": []},
            {"name": "祖母", "type": "角色", "aliases": []},
            {"name": "小沙丝绒", "type": "角色", "aliases": ["小丝绒"]},
            {"name": "体育老师", "type": "角色", "aliases": []},
            {"name": "田径", "type": "概念", "aliases": []},
            {"name": "波拉比", "type": "角色", "aliases": []},
            {"name": "盛装骑术赛", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "宽檐帽", "dst": "飞碟", "relation": "评论", "confidence": 0.7},
            {"src": "马科尔", "dst": "道歉信", "relation": "写", "confidence": 0.7},
            {"src": "祖母", "dst": "小沙丝绒", "relation": "称呼", "confidence": 0.8},
            {"src": "体育老师", "dst": "小沙丝绒", "relation": "评价", "confidence": 0.7},
            {"src": "小沙丝绒", "dst": "田径", "relation": "询问", "confidence": 0.7},
            {"src": "小沙丝绒", "dst": "波拉比", "relation": "提及", "confidence": 0.7},
            {"src": "小沙丝绒", "dst": "盛装骑术赛", "relation": "参加", "confidence": 0.7},
            {"src": "波拉比", "dst": "小沙丝绒", "relation": "是搭档", "confidence": 0.8},
        ],
    },
    # 12) 沙丝绒收缴假票 · 乌卢鲁运动会与波拉比
    "32dbc65c3e72a94a": {
        "entities": [
            {"name": "沙丝绒", "type": "角色", "aliases": ["小沙丝绒"]},
            {"name": "祖母", "type": "角色", "aliases": []},
            {"name": "乌卢鲁运动会", "type": "事件", "aliases": []},
            {"name": "波拉比", "type": "角色", "aliases": []},
            {"name": "报刊亭老板", "type": "角色", "aliases": []},
            {"name": "假票", "type": "物品", "aliases": []},
            {"name": "观众", "type": "角色", "aliases": []},
            {"name": "神秘学家", "type": "概念", "aliases": []},
            {"name": "帮派", "type": "组织", "aliases": []},
        ],
        "relations": [
            {"src": "沙丝绒", "dst": "祖母", "relation": "忆起", "confidence": 0.7},
            {"src": "沙丝绒", "dst": "波拉比", "relation": "拥有", "confidence": 0.8},
            {"src": "沙丝绒", "dst": "假票", "relation": "归还", "confidence": 0.7},
            {"src": "报刊亭老板", "dst": "假票", "relation": "售卖", "confidence": 0.8},
            {"src": "帮派", "dst": "报刊亭老板", "relation": "胁迫", "confidence": 0.7},
            {"src": "沙丝绒", "dst": "假票", "relation": "收缴", "confidence": 0.8},
            {"src": "沙丝绒", "dst": "乌卢鲁运动会", "relation": "提及", "confidence": 0.7},
            {"src": "乌卢鲁运动会", "dst": "神秘学家", "relation": "属于", "confidence": 0.7},
        ],
    },
    # 13) 岛上的独白 · 77/37/休与酿酒时节诗句
    "422a8696610e4875": {
        "entities": [
            {"name": "77", "type": "角色", "aliases": []},
            {"name": "37", "type": "角色", "aliases": []},
            {"name": "休", "type": "角色", "aliases": []},
            {"name": "苏菲亚", "type": "角色", "aliases": []},
            {"name": "协理人", "type": "概念", "aliases": []},
            {"name": "210", "type": "角色", "aliases": []},
            {"name": "伟大者", "type": "角色", "aliases": []},
            {"name": "酿酒时节", "type": "概念", "aliases": []},
            {"name": "卷轴", "type": "物品", "aliases": []},
            {"name": "镜子", "type": "物品", "aliases": []},
            {"name": "岛", "type": "地点", "aliases": []},
            {"name": "笔记本", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "休", "dst": "笔记本", "relation": "遗留", "confidence": 0.7},
            {"src": "苏菲亚", "dst": "笔记本", "relation": "持有", "confidence": 0.8},
            {"src": "210", "dst": "77", "relation": "认为得到答案", "confidence": 0.7},
            {"src": "酿酒时节", "dst": "卷轴", "relation": "记录于", "confidence": 0.8},
            {"src": "37", "dst": "岛", "relation": "位于", "confidence": 0.7},
        ],
    },
    # 16) 镇定药剂配方与禁闭室艺术独白（注意：原块号14/15为数值页已NOOP）
    "8e0b92e9ca6d3bc9": {
        "entities": [
            {"name": "圣洛夫基金会", "type": "组织", "aliases": []},
            {"name": "巡查人员", "type": "角色", "aliases": []},
            {"name": "基金会紧急防卫规范", "type": "物品", "aliases": ["《基金会紧急防卫规范》"]},
            {"name": "禁闭室", "type": "地点", "aliases": []},
            {"name": "方盒子", "type": "物品", "aliases": []},
            {"name": "唐纳德·贾德", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "圣洛夫基金会", "dst": "巡查人员", "relation": "配备", "confidence": 0.8},
            {"src": "巡查人员", "dst": "基金会紧急防卫规范", "relation": "依据", "confidence": 0.7},
            {"src": "唐纳德·贾德", "dst": "方盒子", "relation": "关联", "confidence": 0.7},
            {"src": "方盒子", "dst": "禁闭室", "relation": "位于", "confidence": 0.7},
        ],
    },
    # 17) 维廉W5战略剃刀维护 · 集会厅戒律与钟表匠隐喻
    "898d1c0d5f8ef059": {
        "entities": [
            {"name": "维廉W5战略剃刀", "type": "物品", "aliases": ["维廉W5战略剃刀（增强型）"]},
            {"name": "拉普拉斯科算中心", "type": "组织", "aliases": []},
            {"name": "集会厅", "type": "地点", "aliases": []},
            {"name": "岛", "type": "地点", "aliases": []},
            {"name": "甜甜圈", "type": "物品", "aliases": []},
            {"name": "商人的儿子", "type": "角色", "aliases": []},
            {"name": "钟表匠", "type": "角色", "aliases": []},
            {"name": "星星的谜底", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "维廉W5战略剃刀", "dst": "拉普拉斯科算中心", "relation": "维护联系", "confidence": 0.8},
            {"src": "集会厅", "dst": "岛", "relation": "位于", "confidence": 0.7},
            {"src": "商人的儿子", "dst": "星星的谜底", "relation": "发现", "confidence": 0.7},
            {"src": "钟表匠", "dst": "星星的谜底", "relation": "关联", "confidence": 0.7},
        ],
    },
    # 18) 十四行诗与虚构集谈国家福柯学会与科马拉全景监狱
    "f47451f4cc4850b0": {
        "entities": [
            {"name": "十四行诗", "type": "角色", "aliases": []},
            {"name": "国家福柯学会", "type": "组织", "aliases": []},
            {"name": "虚构集", "type": "角色", "aliases": []},
            {"name": "军政府", "type": "组织", "aliases": []},
            {"name": "福柯", "type": "角色", "aliases": []},
            {"name": "科马拉全景监狱", "type": "组织", "aliases": []},
            {"name": "笔友", "type": "角色", "aliases": []},
            {"name": "政府", "type": "组织", "aliases": []},
            {"name": "宪兵", "type": "角色", "aliases": []},
            {"name": "暗色带编织·卷一", "type": "物品", "aliases": []},
            {"name": "异端", "type": "概念", "aliases": []},
            {"name": "监视者", "type": "角色", "aliases": []},
            {"name": "囚犯", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "国家福柯学会", "dst": "军政府", "relation": "受支持于", "confidence": 0.8},
            {"src": "国家福柯学会", "dst": "福柯", "relation": "研究", "confidence": 0.8},
            {"src": "国家福柯学会", "dst": "科马拉全景监狱", "relation": "创立", "confidence": 0.85},
            {"src": "科马拉全景监狱", "dst": "囚犯", "relation": "监视", "confidence": 0.8},
            {"src": "虚构集", "dst": "笔友", "relation": "拥有", "confidence": 0.7},
            {"src": "宪兵", "dst": "虚构集", "relation": "威胁关押", "confidence": 0.7},
            {"src": "政府", "dst": "国家福柯学会", "relation": "实验对象", "confidence": 0.7},
            {"src": "十四行诗", "dst": "虚构集", "relation": "对话", "confidence": 0.7},
            {"src": "国家福柯学会", "dst": "异端", "relation": "迫害", "confidence": 0.7},
            {"src": "监视者", "dst": "囚犯", "relation": "监视", "confidence": 0.7},
        ],
    },
    # 19) 空脑袋受司辰鼓励 · 洛伦兹蝴蝶与百夫长墨西哥巡演
    "73b6bb8aff3d3797": {
        "entities": [
            {"name": "空脑袋", "type": "角色", "aliases": []},
            {"name": "司辰", "type": "角色", "aliases": []},
            {"name": "贝丽尔", "type": "角色", "aliases": ["贝丽尔女士"]},
            {"name": "莱瑟姆", "type": "角色", "aliases": ["莱瑟姆小姐"]},
            {"name": "虚构集", "type": "角色", "aliases": []},
            {"name": "洛杉矶", "type": "地点", "aliases": []},
            {"name": "墨西哥", "type": "地点", "aliases": []},
            {"name": "洛伦兹蝴蝶", "type": "角色", "aliases": []},
            {"name": "百夫长", "type": "角色", "aliases": []},
            {"name": "惊喜配方", "type": "物品", "aliases": []},
            {"name": "制作人", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "空脑袋", "dst": "司辰", "relation": "受鼓励于", "confidence": 0.8},
            {"src": "空脑袋", "dst": "莱瑟姆", "relation": "感谢提供线索", "confidence": 0.7},
            {"src": "莱瑟姆", "dst": "洛杉矶", "relation": "在经历", "confidence": 0.7},
            {"src": "空脑袋", "dst": "墨西哥", "relation": "前往", "confidence": 0.7},
            {"src": "洛伦兹蝴蝶", "dst": "惊喜配方", "relation": "品尝", "confidence": 0.8},
            {"src": "百夫长", "dst": "惊喜配方", "relation": "提供", "confidence": 0.7},
            {"src": "百夫长", "dst": "洛伦兹蝴蝶", "relation": "共饮", "confidence": 0.7},
            {"src": "百夫长", "dst": "墨西哥", "relation": "巡演于", "confidence": 0.7},
            {"src": "制作人", "dst": "百夫长", "relation": "筹备巡演", "confidence": 0.7},
        ],
    },
    # 20) 星锑追蝴蝶作业 · 莱瑟姆观影清单（地下世界/疤面人/马卡里奥）
    "e810c600975a20c1": {
        "entities": [
            {"name": "壁画", "type": "物品", "aliases": []},
            {"name": "星锑", "type": "角色", "aliases": []},
            {"name": "X", "type": "角色", "aliases": []},
            {"name": "自由海风号", "type": "物品", "aliases": []},
            {"name": "唱片", "type": "物品", "aliases": []},
            {"name": "莱瑟姆", "type": "角色", "aliases": []},
            {"name": "墨西哥", "type": "地点", "aliases": []},
            {"name": "地下世界", "type": "物品", "aliases": ["《地下世界》"]},
            {"name": "疤面人", "type": "物品", "aliases": ["《疤面人》"]},
            {"name": "马卡里奥", "type": "物品", "aliases": ["《马卡里奥》"]},
            {"name": "汤米枪", "type": "物品", "aliases": []},
            {"name": "诸灵节", "type": "概念", "aliases": []},
            {"name": "芝加哥", "type": "地点", "aliases": []},
            {"name": "混沌", "type": "概念", "aliases": []},
            {"name": "笔记", "type": "物品", "aliases": ["莱瑟姆的笔记"]},
        ],
        "relations": [
            {"src": "星锑", "dst": "混沌", "relation": "研究", "confidence": 0.7},
            {"src": "星锑", "dst": "自由海风号", "relation": "提及", "confidence": 0.7},
            {"src": "星锑", "dst": "唱片", "relation": "拥有", "confidence": 0.7},
            {"src": "X", "dst": "星锑", "relation": "讨论", "confidence": 0.7},
            {"src": "莱瑟姆", "dst": "笔记", "relation": "撰写", "confidence": 0.7},
            {"src": "莱瑟姆", "dst": "地下世界", "relation": "提及", "confidence": 0.7},
            {"src": "莱瑟姆", "dst": "疤面人", "relation": "提及", "confidence": 0.7},
            {"src": "莱瑟姆", "dst": "马卡里奥", "relation": "提及", "confidence": 0.7},
            {"src": "马卡里奥", "dst": "诸灵节", "relation": "关联", "confidence": 0.8},
            {"src": "疤面人", "dst": "芝加哥", "relation": "描述", "confidence": 0.7},
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
    print(f"[apply-missing-p15] 写入 {len(RESULTS)} 条，NOOP +{len(NOOP_ADD)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
