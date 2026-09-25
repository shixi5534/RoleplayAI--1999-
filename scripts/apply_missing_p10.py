# -*- coding: utf-8 -*-
"""未抽取剧情块补抽 · 第 10 批（backfill2/batch_00，20 块）。

仿 apply_missing_p4.py：顶部 RESULTS 常量 + validate() 悬空自检 + main() 写盘 + --apply。
规则：仅抽正文明确出现的词；实体名/别名需为块正文子串；关系谓语纯中文且 src/dst 落在本块实体中。

用法：python scripts/apply_missing_p10.py            # 预演
      python scripts/apply_missing_p10.py --apply    # 写盘
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "knowledge" / "plot_cache" / "wu_ming_zhe"

NOOP_ADD: list[str] = []  # 本批无纯数值/UI 页

RESULTS: dict[str, dict] = {
    # v2.3 第七次测试 / 基金会小纸条儿 / 雾行者
    "159c21c70e8064d8": {
        "entities": [
            {"name": "基金会", "type": "组织", "aliases": []},
            {"name": "小纸条儿", "type": "物品", "aliases": ['"小纸条儿"']},
            {"name": "雾行者", "type": "角色", "aliases": []},
            {"name": "豌豆浓汁布丁", "type": "物品", "aliases": ['"豌豆浓汁布丁"']},
            {"name": "清除装置", "type": "物品", "aliases": []},
            {"name": "乌卢鲁传单", "type": "物品", "aliases": []},
            {"name": "伦敦预选赛", "type": "事件", "aliases": ["取消伦敦预选赛"]},
        ],
        "relations": [
            {"src": "雾行者", "dst": "清除装置", "relation": "拼凑", "confidence": 0.85},
            {"src": "基金会", "dst": "小纸条儿", "relation": "持有", "confidence": 0.8},
            {"src": "基金会", "dst": "伦敦预选赛", "relation": "取消", "confidence": 0.8},
        ],
    },
    # v2.4 星锑望远镜物料清单 / 告别
    "f5a14d271619d455": {
        "entities": [
            {"name": "广域照相机", "type": "物品", "aliases": ["广域行星照相机"]},
            {"name": "加州理工", "type": "组织", "aliases": []},
            {"name": "天体摄谱仪", "type": "物品", "aliases": []},
            {"name": "星锑望远镜", "type": "物品", "aliases": []},
            {"name": "科算中心", "type": "组织", "aliases": []},
            {"name": "高速光度计", "type": "物品", "aliases": []},
            {"name": "暴雨", "type": "事件", "aliases": ['"暴雨"']},
            {"name": "太空种子", "type": "物品", "aliases": []},
            {"name": "普列谢茨克", "type": "地点", "aliases": []},
            {"name": "星锑唱片", "type": "物品", "aliases": ["“星锑”唱片", "唱片"]},
            {"name": "闭幕式", "type": "事件", "aliases": []},
            {"name": "星锑", "type": "角色", "aliases": []},
            {"name": "可燃点", "type": "角色", "aliases": []},
            {"name": "爱兹拉", "type": "角色", "aliases": []},
            {"name": "沙丝绒", "type": "角色", "aliases": ["沙丝绒小姐"]},
            {"name": "乌卢鲁往事大揭秘", "type": "物品", "aliases": ["《乌卢鲁往事大揭秘》"]},
            {"name": "如何抢到最前排门票", "type": "物品", "aliases": ["《如何抢到最前排门票》"]},
            {"name": "APPLe", "type": "角色", "aliases": ["APPLe某"]},
            {"name": "光学实验室", "type": "组织", "aliases": []},
        ],
        "relations": [
            {"src": "加州理工", "dst": "广域照相机", "relation": "提供", "confidence": 0.9},
            {"src": "科算中心", "dst": "天体摄谱仪", "relation": "拥有", "confidence": 0.8},
            {"src": "星锑望远镜", "dst": "天体摄谱仪", "relation": "搭载", "confidence": 0.9},
            {"src": "高速光度计", "dst": "暴雨", "relation": "早于除役", "confidence": 0.8},
            {"src": "普列谢茨克", "dst": "太空种子", "relation": "存有", "confidence": 0.75},
            {"src": "星锑唱片", "dst": "星锑望远镜", "relation": "驱动", "confidence": 0.9},
            {"src": "星锑", "dst": "可燃点", "relation": "道别", "confidence": 0.8},
            {"src": "星锑", "dst": "爱兹拉", "relation": "道别", "confidence": 0.8},
            {"src": "星锑", "dst": "沙丝绒", "relation": "道别", "confidence": 0.8},
            {"src": "APPLe", "dst": "星锑", "relation": "嘱托", "confidence": 0.8},
            {"src": "沙丝绒", "dst": "乌卢鲁往事大揭秘", "relation": "售卖", "confidence": 0.8},
        ],
    },
    # v2.4 巨齿飞鳐 / 混沌吼叫匣
    "2f25ef330975c4d8": {
        "entities": [
            {"name": "巨齿飞鳐", "type": "角色", "aliases": []},
            {"name": "奥利图欧", "type": "角色", "aliases": []},
            {"name": "哑谜", "type": "角色", "aliases": []},
            {"name": "乌尔里希", "type": "角色", "aliases": []},
            {"name": "混沌吼叫匣", "type": "物品", "aliases": ["吼叫仪", '"混沌吼叫匣"']},
            {"name": "洛伦兹蝴蝶", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "乌尔里希", "dst": "混沌吼叫匣", "relation": "指出", "confidence": 0.85},
            {"src": "洛伦兹蝴蝶", "dst": "混沌吼叫匣", "relation": "附送", "confidence": 0.9},
            {"src": "巨齿飞鳐", "dst": "奥利图欧", "relation": "区别于", "confidence": 0.85},
            {"src": "哑谜", "dst": "混沌吼叫匣", "relation": "质疑", "confidence": 0.6},
        ],
    },
    # v1.5 乌卢鲁运动会复兴 / 复兴小队
    "b95a187aa62a00b5": {
        "entities": [
            {"name": "乌卢鲁运动会", "type": "事件", "aliases": ['"乌卢鲁运动会"']},
            {"name": "复兴小队", "type": "组织", "aliases": ['"复兴小队"']},
            {"name": "女学生", "type": "角色", "aliases": []},
            {"name": "人类菌菇学家", "type": "角色", "aliases": []},
            {"name": "圣洛夫基金会", "type": "组织", "aliases": []},
            {"name": "本耶普", "type": "角色", "aliases": []},
            {"name": "兔女郎", "type": "角色", "aliases": []},
            {"name": "疯狂科学家", "type": "角色", "aliases": []},
            {"name": "巨型大啡菇", "type": "角色", "aliases": []},
            {"name": "像素鸸鹋", "type": "角色", "aliases": []},
            {"name": "爱丽丝泉市政厅", "type": "地点", "aliases": []},
            {"name": "凯特女士", "type": "角色", "aliases": ["凯特"]},
        ],
        "relations": [
            {"src": "女学生", "dst": "复兴小队", "relation": "带领", "confidence": 0.9},
            {"src": "人类菌菇学家", "dst": "复兴小队", "relation": "隶属", "confidence": 0.8},
            {"src": "圣洛夫基金会", "dst": "复兴小队", "relation": "背书", "confidence": 0.9},
            {"src": "复兴小队", "dst": "乌卢鲁运动会", "relation": "复兴", "confidence": 0.85},
            {"src": "复兴小队", "dst": "爱丽丝泉市政厅", "relation": "出现于", "confidence": 0.85},
            {"src": "复兴小队", "dst": "凯特女士", "relation": "扰乱", "confidence": 0.85},
            {"src": "兔女郎", "dst": "复兴小队", "relation": "隶属", "confidence": 0.7},
            {"src": "疯狂科学家", "dst": "复兴小队", "relation": "隶属", "confidence": 0.7},
            {"src": "巨型大啡菇", "dst": "复兴小队", "relation": "隶属", "confidence": 0.7},
            {"src": "像素鸸鹋", "dst": "复兴小队", "relation": "隶属", "confidence": 0.7},
        ],
    },
    # v2.6 布宜诺斯艾利斯分部收容报告 / 乌斯怀亚港口爆炸
    "66a9fa4c6eb555e0": {
        "entities": [
            {"name": "布宜诺斯艾利斯分部", "type": "组织", "aliases": []},
            {"name": "暴雨专项小组", "type": "组织", "aliases": ['"暴雨专项小组"']},
            {"name": "乌尔里希", "type": "角色", "aliases": []},
            {"name": "星锑", "type": "角色", "aliases": []},
            {"name": "司辰", "type": "角色", "aliases": []},
            {"name": "火地岛", "type": "地点", "aliases": []},
            {"name": "十四行诗", "type": "角色", "aliases": []},
            {"name": "芭卡洛儿", "type": "角色", "aliases": []},
            {"name": "自由海风号", "type": "物品", "aliases": ['"自由海风号"']},
            {"name": "图图石子", "type": "角色", "aliases": []},
            {"name": "努库泰奥族", "type": "组织", "aliases": ["努库泰奥族人"]},
            {"name": "乌斯怀亚港口爆炸", "type": "事件", "aliases": []},
            {"name": "乌斯怀亚港口", "type": "地点", "aliases": ["乌斯怀亚"]},
            {"name": "芝诺", "type": "角色", "aliases": []},
            {"name": "海军", "type": "组织", "aliases": []},
            {"name": "消防部门", "type": "组织", "aliases": []},
            {"name": "第三码头", "type": "地点", "aliases": []},
            {"name": "储油罐", "type": "物品", "aliases": []},
            {"name": "货运仓库", "type": "物品", "aliases": []},
            {"name": "监狱", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "布宜诺斯艾利斯分部", "dst": "乌尔里希", "relation": "收容", "confidence": 0.9},
            {"src": "布宜诺斯艾利斯分部", "dst": "星锑", "relation": "收容", "confidence": 0.9},
            {"src": "暴雨专项小组", "dst": "乌尔里希", "relation": "隶属", "confidence": 0.9},
            {"src": "暴雨专项小组", "dst": "星锑", "relation": "隶属", "confidence": 0.9},
            {"src": "司辰", "dst": "火地岛", "relation": "登陆", "confidence": 0.85},
            {"src": "十四行诗", "dst": "司辰", "relation": "呈交报告", "confidence": 0.8},
            {"src": "芭卡洛儿", "dst": "自由海风号", "relation": "任职", "confidence": 0.9},
            {"src": "图图石子", "dst": "努库泰奥族", "relation": "隶属", "confidence": 0.9},
            {"src": "乌斯怀亚港口爆炸", "dst": "储油罐", "relation": "源于", "confidence": 0.85},
            {"src": "乌斯怀亚港口爆炸", "dst": "货运仓库", "relation": "源于", "confidence": 0.85},
            {"src": "乌斯怀亚港口爆炸", "dst": "第三码头", "relation": "涉及", "confidence": 0.8},
            {"src": "乌斯怀亚港口爆炸", "dst": "乌斯怀亚港口", "relation": "发生于", "confidence": 0.9},
            {"src": "海军", "dst": "乌斯怀亚港口爆炸", "relation": "扑救", "confidence": 0.8},
            {"src": "消防部门", "dst": "乌斯怀亚港口爆炸", "relation": "扑救", "confidence": 0.8},
        ],
    },
    # v2.6 致未曾谋面的笔友 / 阿莱夫与虚构集
    "c7a321a3afaee372": {
        "entities": [
            {"name": "阿莱夫", "type": "角色", "aliases": []},
            {"name": "银行职员", "type": "角色", "aliases": []},
            {"name": "阿马尔菲塔诺", "type": "角色", "aliases": []},
            {"name": "亡灵", "type": "概念", "aliases": []},
            {"name": "沙漠", "type": "概念", "aliases": []},
            {"name": "命运", "type": "概念", "aliases": []},
            {"name": "虚构集", "type": "角色", "aliases": ["虚构集小姐"]},
            {"name": "哥伦比亚", "type": "地点", "aliases": []},
            {"name": "圣菲波哥大", "type": "地点", "aliases": []},
            {"name": "露天剧场", "type": "地点", "aliases": []},
            {"name": "诗会", "type": "事件", "aliases": []},
            {"name": "乌斯怀亚", "type": "地点", "aliases": []},
            {"name": "科马拉监狱", "type": "地点", "aliases": []},
            {"name": "布宜诺斯艾利斯", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "阿莱夫", "dst": "虚构集", "relation": "通信", "confidence": 0.9},
            {"src": "阿莱夫", "dst": "科马拉监狱", "relation": "关押于", "confidence": 0.9},
            {"src": "阿莱夫", "dst": "乌斯怀亚", "relation": "身处", "confidence": 0.85},
            {"src": "阿莱夫", "dst": "阿马尔菲塔诺", "relation": "创作", "confidence": 0.85},
            {"src": "阿马尔菲塔诺", "dst": "银行职员", "relation": "担任", "confidence": 0.8},
            {"src": "阿莱夫", "dst": "亡灵", "relation": "探讨", "confidence": 0.7},
            {"src": "阿莱夫", "dst": "沙漠", "relation": "探讨", "confidence": 0.7},
            {"src": "阿莱夫", "dst": "命运", "relation": "探讨", "confidence": 0.7},
            {"src": "虚构集", "dst": "诗会", "relation": "出席", "confidence": 0.8},
            {"src": "诗会", "dst": "露天剧场", "relation": "举办于", "confidence": 0.8},
            {"src": "诗会", "dst": "圣菲波哥大", "relation": "位于", "confidence": 0.8},
            {"src": "诗会", "dst": "哥伦比亚", "relation": "位于", "confidence": 0.8},
        ],
    },
    # v3.5 百夫长与洛伦兹蝴蝶 / 灰车党 / 夜巡特遣管理局
    "b37fc0256bddc637": {
        "entities": [
            {"name": "百夫长", "type": "角色", "aliases": []},
            {"name": "洛伦兹蝴蝶", "type": "角色", "aliases": []},
            {"name": "铁箱子", "type": "物品", "aliases": []},
            {"name": "这座城市是我们的", "type": "概念", "aliases": ['"这座城市是我们的"']},
            {"name": "暴雨", "type": "事件", "aliases": ['"暴雨"']},
            {"name": "夜巡特遣管理局", "type": "组织", "aliases": ["夜巡特遣"]},
            {"name": "执夜人", "type": "角色", "aliases": []},
            {"name": "政府机构", "type": "组织", "aliases": []},
            {"name": "灰车党", "type": "组织", "aliases": ['"灰车党"']},
            {"name": "现代化犯罪", "type": "概念", "aliases": ['"现代化犯罪"']},
            {"name": "本地警察", "type": "组织", "aliases": []},
            {"name": "地下帮派", "type": "组织", "aliases": []},
            {"name": "地下势力", "type": "组织", "aliases": []},
        ],
        "relations": [
            {"src": "百夫长", "dst": "洛伦兹蝴蝶", "relation": "约定重逢", "confidence": 0.8},
            {"src": "洛伦兹蝴蝶", "dst": "铁箱子", "relation": "隐现于", "confidence": 0.7},
            {"src": "暴雨", "dst": "夜巡特遣管理局", "relation": "促使出现", "confidence": 0.8},
            {"src": "夜巡特遣管理局", "dst": "执夜人", "relation": "下设", "confidence": 0.85},
            {"src": "夜巡特遣管理局", "dst": "政府机构", "relation": "协作", "confidence": 0.85},
            {"src": "灰车党", "dst": "现代化犯罪", "relation": "被称为", "confidence": 0.85},
            {"src": "灰车党", "dst": "地下帮派", "relation": "属于", "confidence": 0.8},
            {"src": "本地警察", "dst": "夜巡特遣管理局", "relation": "分工", "confidence": 0.75},
            {"src": "地下势力", "dst": "地下帮派", "relation": "同指", "confidence": 0.7},
        ],
    },
    # v3.5 壁画复兴运动 / 墨西哥
    "5695450270129a21": {
        "entities": [
            {"name": "警察", "type": "组织", "aliases": []},
            {"name": "执夜人", "type": "角色", "aliases": []},
            {"name": "灰色车辆", "type": "物品", "aliases": []},
            {"name": "壁画复兴运动", "type": "事件", "aliases": ["壁画运动"]},
            {"name": "墨西哥", "type": "地点", "aliases": []},
            {"name": "政府", "type": "组织", "aliases": []},
            {"name": "旧秩序", "type": "概念", "aliases": []},
            {"name": "传统文化", "type": "概念", "aliases": []},
            {"name": "公共建筑", "type": "地点", "aliases": []},
            {"name": "湿壁画", "type": "物品", "aliases": []},
            {"name": "墨西哥人", "type": "角色", "aliases": []},
            {"name": "画家", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "壁画复兴运动", "dst": "墨西哥", "relation": "发生于", "confidence": 0.9},
            {"src": "政府", "dst": "旧秩序", "relation": "维持", "confidence": 0.8},
            {"src": "旧秩序", "dst": "传统文化", "relation": "禁锢", "confidence": 0.85},
            {"src": "壁画复兴运动", "dst": "传统文化", "relation": "复兴", "confidence": 0.85},
            {"src": "壁画复兴运动", "dst": "墨西哥人", "relation": "塑造认同", "confidence": 0.8},
            {"src": "公共建筑", "dst": "壁画复兴运动", "relation": "承载", "confidence": 0.8},
            {"src": "画家", "dst": "湿壁画", "relation": "创作", "confidence": 0.85},
            {"src": "警察", "dst": "执夜人", "relation": "并存", "confidence": 0.75},
            {"src": "灰色车辆", "dst": "警察", "relation": "同行", "confidence": 0.7},
        ],
    },
    # v? 湿漉漉的信 / 卡兹与来信者Z / 法兰西分部
    "6cffcf3232e7ea3b": {
        "entities": [
            {"name": "湿漉漉的信", "type": "物品", "aliases": []},
            {"name": "来信者Z", "type": "角色", "aliases": ["Z"]},
            {"name": "法兰西分部", "type": "组织", "aliases": []},
            {"name": "暴雨", "type": "事件", "aliases": ['"暴雨"']},
            {"name": "基金会", "type": "组织", "aliases": []},
            {"name": "司辰", "type": "角色", "aliases": ['"司辰"']},
            {"name": "大人物", "type": "角色", "aliases": []},
            {"name": "基金会总部", "type": "组织", "aliases": ["总部"]},
            {"name": "黑伞", "type": "物品", "aliases": []},
            {"name": "卡兹", "type": "角色", "aliases": []},
            {"name": "科学家", "type": "角色", "aliases": ['"科学家"']},
            {"name": "乒乓赛", "type": "事件", "aliases": []},
        ],
        "relations": [
            {"src": "卡兹", "dst": "法兰西分部", "relation": "隶属", "confidence": 0.9},
            {"src": "卡兹", "dst": "来信者Z", "relation": "致信", "confidence": 0.9},
            {"src": "来信者Z", "dst": "湿漉漉的信", "relation": "收到", "confidence": 0.8},
            {"src": "法兰西分部", "dst": "暴雨", "relation": "不知情", "confidence": 0.85},
            {"src": "基金会", "dst": "司辰", "relation": "需要", "confidence": 0.9},
            {"src": "大人物", "dst": "暴雨", "relation": "渴求", "confidence": 0.7},
            {"src": "卡兹", "dst": "基金会总部", "relation": "返回", "confidence": 0.85},
            {"src": "卡兹", "dst": "黑伞", "relation": "提及", "confidence": 0.8},
            {"src": "卡兹", "dst": "科学家", "relation": "评价", "confidence": 0.8},
            {"src": "卡兹", "dst": "乒乓赛", "relation": "约定", "confidence": 0.8},
        ],
    },
    # v3.3 黑面包食谱 / 金色饥荒 / 近卫团通告
    "f60a2c033fada9b8": {
        "entities": [
            {"name": "黑面包", "type": "物品", "aliases": []},
            {"name": "金色饥荒", "type": "事件", "aliases": ['"金色饥荒"']},
            {"name": "伊万", "type": "角色", "aliases": []},
            {"name": "辣椒糊", "type": "物品", "aliases": []},
            {"name": "熏鱼", "type": "物品", "aliases": []},
            {"name": "草根汤", "type": "物品", "aliases": []},
            {"name": "流浪诗人", "type": "角色", "aliases": ["无名的流浪诗人"]},
            {"name": "红菜汤", "type": "物品", "aliases": []},
            {"name": "瓦莉娅夫人", "type": "角色", "aliases": ["瓦莉娅"]},
            {"name": "果酱", "type": "物品", "aliases": []},
            {"name": "苹果酱", "type": "物品", "aliases": []},
            {"name": "大地之母", "type": "概念", "aliases": []},
            {"name": "前线", "type": "地点", "aliases": []},
            {"name": "近卫团", "type": "组织", "aliases": []},
            {"name": "格鲁托夫上尉", "type": "角色", "aliases": ["格鲁托夫"]},
            {"name": "南极", "type": "地点", "aliases": []},
            {"name": "机密文件", "type": "物品", "aliases": []},
            {"name": "通讯设备", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "金色饥荒", "dst": "黑面包", "relation": "催生", "confidence": 0.85},
            {"src": "伊万", "dst": "黑面包", "relation": "喜爱", "confidence": 0.85},
            {"src": "伊万", "dst": "辣椒糊", "relation": "涂抹", "confidence": 0.8},
            {"src": "流浪诗人", "dst": "草根汤", "relation": "提供配方", "confidence": 0.85},
            {"src": "瓦莉娅夫人", "dst": "果酱", "relation": "赠送", "confidence": 0.9},
            {"src": "瓦莉娅夫人", "dst": "苹果酱", "relation": "赠送", "confidence": 0.9},
            {"src": "瓦莉娅夫人", "dst": "大地之母", "relation": "祈愿", "confidence": 0.8},
            {"src": "格鲁托夫上尉", "dst": "近卫团", "relation": "隶属", "confidence": 0.9},
            {"src": "格鲁托夫上尉", "dst": "南极", "relation": "行动于", "confidence": 0.85},
            {"src": "格鲁托夫上尉", "dst": "机密文件", "relation": "带走", "confidence": 0.9},
            {"src": "格鲁托夫上尉", "dst": "通讯设备", "relation": "带走", "confidence": 0.9},
        ],
    },
    # v1.6 混种血食怪的来历 / UTTU编辑部与告死鸟
    "07bf6c9f11f62c0c": {
        "entities": [
            {"name": "小女孩", "type": "角色", "aliases": []},
            {"name": "血食怪", "type": "角色", "aliases": []},
            {"name": "混种血食怪", "type": "角色", "aliases": []},
            {"name": "叔叔", "type": "角色", "aliases": []},
            {"name": "战争", "type": "事件", "aliases": []},
            {"name": "古堡", "type": "地点", "aliases": []},
            {"name": "古堡的女主人", "type": "角色", "aliases": []},
            {"name": "绷带", "type": "物品", "aliases": []},
            {"name": "风", "type": "概念", "aliases": ['"风"']},
            {"name": "网", "type": "概念", "aliases": ['"网"']},
            {"name": "UTTU编辑部", "type": "组织", "aliases": ["《UTTU》编辑部", "UTTU"]},
            {"name": "多瑙黎明号", "type": "物品", "aliases": ['"多瑙黎明号"']},
            {"name": "告死鸟", "type": "角色", "aliases": []},
            {"name": "恶魔", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "小女孩", "dst": "血食怪", "relation": "父为", "confidence": 0.9},
            {"src": "小女孩", "dst": "混种血食怪", "relation": "属于", "confidence": 0.85},
            {"src": "叔叔", "dst": "小女孩", "relation": "救助", "confidence": 0.9},
            {"src": "叔叔", "dst": "古堡", "relation": "前往", "confidence": 0.85},
            {"src": "古堡的女主人", "dst": "小女孩", "relation": "治愈", "confidence": 0.9},
            {"src": "战争", "dst": "小女孩", "relation": "波及", "confidence": 0.8},
            {"src": "小女孩", "dst": "绷带", "relation": "缠绕", "confidence": 0.8},
            {"src": "叔叔", "dst": "恶魔", "relation": "交易", "confidence": 0.7},
            {"src": "风", "dst": "网", "relation": "交织", "confidence": 0.7},
            {"src": "告死鸟", "dst": "多瑙黎明号", "relation": "任职", "confidence": 0.9},
            {"src": "告死鸟", "dst": "UTTU编辑部", "relation": "隶属", "confidence": 0.85},
        ],
    },
    # v1.7 维纳斯诗篇 / 药物样品实验记录
    "9fd954a7b027959a": {
        "entities": [
            {"name": "维纳斯", "type": "角色", "aliases": []},
            {"name": "实验记录", "type": "物品", "aliases": []},
            {"name": "001号药物样品", "type": "物品", "aliases": []},
            {"name": "008号药物样品", "type": "物品", "aliases": []},
            {"name": "研究员", "type": "角色", "aliases": []},
            {"name": "提纯液", "type": "物品", "aliases": []},
            {"name": "试剂", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "001号药物样品", "dst": "提纯液", "relation": "提炼出", "confidence": 0.85},
            {"src": "008号药物样品", "dst": "试剂", "relation": "影响", "confidence": 0.8},
            {"src": "实验记录", "dst": "001号药物样品", "relation": "记载", "confidence": 0.9},
            {"src": "实验记录", "dst": "008号药物样品", "relation": "记载", "confidence": 0.9},
            {"src": "研究员", "dst": "实验记录", "relation": "参与", "confidence": 0.8},
        ],
    },
    # v1.7 苦目树药物实验 / 罗马尼亚护身符
    "fa101bbd675c6691": {
        "entities": [
            {"name": "019号药物样品", "type": "物品", "aliases": []},
            {"name": "苦目树", "type": "物品", "aliases": []},
            {"name": "苦目树叶", "type": "物品", "aliases": []},
            {"name": "023号药物样品", "type": "物品", "aliases": []},
            {"name": "试剂", "type": "物品", "aliases": []},
            {"name": "025号药物样品", "type": "物品", "aliases": []},
            {"name": "蔗糖", "type": "物品", "aliases": []},
            {"name": "酒精", "type": "物品", "aliases": []},
            {"name": "053号药物样品", "type": "物品", "aliases": []},
            {"name": "苦目糖", "type": "物品", "aliases": []},
            {"name": "098-A号药物样品", "type": "物品", "aliases": []},
            {"name": "志愿者", "type": "角色", "aliases": []},
            {"name": "159-C号药物样品", "type": "物品", "aliases": []},
            {"name": "实验笔记", "type": "物品", "aliases": []},
            {"name": "沉重的门", "type": "物品", "aliases": []},
            {"name": "罗马尼亚", "type": "地点", "aliases": []},
            {"name": "三月节", "type": "事件", "aliases": []},
            {"name": "吉娜奶奶", "type": "角色", "aliases": ["吉娜"]},
            {"name": "护身符", "type": "物品", "aliases": []},
            {"name": "埃列娜", "type": "角色", "aliases": []},
            {"name": "水仙花粉", "type": "物品", "aliases": []},
            {"name": "墓地", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "019号药物样品", "dst": "苦目树", "relation": "取自", "confidence": 0.85},
            {"src": "019号药物样品", "dst": "苦目树叶", "relation": "取自", "confidence": 0.8},
            {"src": "023号药物样品", "dst": "试剂", "relation": "涉及", "confidence": 0.8},
            {"src": "025号药物样品", "dst": "蔗糖", "relation": "含", "confidence": 0.85},
            {"src": "025号药物样品", "dst": "苦目树叶", "relation": "含", "confidence": 0.85},
            {"src": "025号药物样品", "dst": "酒精", "relation": "含", "confidence": 0.8},
            {"src": "053号药物样品", "dst": "苦目糖", "relation": "研究", "confidence": 0.85},
            {"src": "098-A号药物样品", "dst": "志愿者", "relation": "试验于", "confidence": 0.9},
            {"src": "159-C号药物样品", "dst": "志愿者", "relation": "验证", "confidence": 0.7},
            {"src": "实验笔记", "dst": "019号药物样品", "relation": "记载", "confidence": 0.8},
            {"src": "吉娜奶奶", "dst": "护身符", "relation": "分发", "confidence": 0.9},
            {"src": "吉娜奶奶", "dst": "埃列娜", "relation": "赠予", "confidence": 0.85},
            {"src": "罗马尼亚", "dst": "三月节", "relation": "庆祝", "confidence": 0.85},
            {"src": "埃列娜", "dst": "墓地", "relation": "否认关联", "confidence": 0.7},
            {"src": "埃列娜", "dst": "水仙花粉", "relation": "否认", "confidence": 0.7},
        ],
    },
    # v1.7 孤儿院 / 霍夫曼调查资料
    "da81e45c60aebeec": {
        "entities": [
            {"name": "埃列娜", "type": "角色", "aliases": []},
            {"name": "护身符", "type": "物品", "aliases": []},
            {"name": "吉娜奶奶", "type": "角色", "aliases": ["吉娜"]},
            {"name": "孤儿院", "type": "地点", "aliases": []},
            {"name": "安德烈", "type": "角色", "aliases": []},
            {"name": "霍夫曼调查的资料", "type": "物品", "aliases": []},
            {"name": "西奥菲尔·冯·迪塔斯多夫", "type": "角色", "aliases": ["迪塔斯多夫"]},
            {"name": "魔圈", "type": "组织", "aliases": ['"魔圈"']},
            {"name": "重塑之手", "type": "组织", "aliases": []},
            {"name": "暴雨", "type": "事件", "aliases": ['"暴雨"']},
            {"name": "拯救", "type": "物品", "aliases": ["《拯救》"]},
            {"name": "萨赫酒店", "type": "地点", "aliases": []},
            {"name": "德梅尔", "type": "角色", "aliases": []},
            {"name": "萨赫蛋糕", "type": "物品", "aliases": []},
            {"name": "古斯·克林特", "type": "角色", "aliases": ["克林特"]},
            {"name": "伊根·希尔德", "type": "角色", "aliases": ["希尔德"]},
        ],
        "relations": [
            {"src": "埃列娜", "dst": "护身符", "relation": "系结", "confidence": 0.85},
            {"src": "埃列娜", "dst": "吉娜奶奶", "relation": "期待认可", "confidence": 0.7},
            {"src": "孤儿院", "dst": "安德烈", "relation": "收留", "confidence": 0.8},
            {"src": "霍夫曼调查的资料", "dst": "西奥菲尔·冯·迪塔斯多夫", "relation": "记载", "confidence": 0.9},
            {"src": "西奥菲尔·冯·迪塔斯多夫", "dst": "魔圈", "relation": "隶属", "confidence": 0.9},
            {"src": "西奥菲尔·冯·迪塔斯多夫", "dst": "重塑之手", "relation": "疑似接触", "confidence": 0.8},
            {"src": "西奥菲尔·冯·迪塔斯多夫", "dst": "暴雨", "relation": "透露", "confidence": 0.85},
            {"src": "西奥菲尔·冯·迪塔斯多夫", "dst": "拯救", "relation": "著", "confidence": 0.9},
            {"src": "萨赫酒店", "dst": "萨赫蛋糕", "relation": "供应", "confidence": 0.8},
            {"src": "德梅尔", "dst": "萨赫蛋糕", "relation": "制作", "confidence": 0.85},
            {"src": "伊根·希尔德", "dst": "重塑之手", "relation": "关系不明", "confidence": 0.7},
        ],
    },
    # v3.7 临时门卫牢骚 / 刻雷乌斯 / 瞭望塔传说
    "4c5b5186641c3fad": {
        "entities": [
            {"name": "基金会", "type": "组织", "aliases": []},
            {"name": "刻雷乌斯", "type": "角色", "aliases": []},
            {"name": "夜巡特遣", "type": "组织", "aliases": ["夜巡特遣管理局"]},
            {"name": "鹰派", "type": "组织", "aliases": ['"鹰派"', "'鹰派'"]},
            {"name": "扩大收容法案", "type": "概念", "aliases": []},
            {"name": "司辰", "type": "角色", "aliases": []},
            {"name": "暴雨倒计时", "type": "事件", "aliases": ["暴雨’倒计时", "倒计时"]},
            {"name": "难民", "type": "角色", "aliases": []},
            {"name": "总部", "type": "组织", "aliases": ["基金会总部"]},
            {"name": "乌鸫", "type": "角色", "aliases": ['"乌鸫"']},
            {"name": "老兵", "type": "角色", "aliases": []},
            {"name": "间谍", "type": "角色", "aliases": []},
            {"name": "瞭望塔", "type": "地点", "aliases": []},
            {"name": "学校", "type": "组织", "aliases": []},
            {"name": "教员", "type": "角色", "aliases": []},
            {"name": "显形药剂", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "基金会", "dst": "刻雷乌斯", "relation": "雇佣", "confidence": 0.8},
            {"src": "刻雷乌斯", "dst": "夜巡特遣", "relation": "原属", "confidence": 0.85},
            {"src": "刻雷乌斯", "dst": "鹰派", "relation": "隶属", "confidence": 0.8},
            {"src": "鹰派", "dst": "扩大收容法案", "relation": "推行", "confidence": 0.85},
            {"src": "司辰", "dst": "暴雨倒计时", "relation": "发布", "confidence": 0.9},
            {"src": "暴雨倒计时", "dst": "难民", "relation": "引发", "confidence": 0.8},
            {"src": "难民", "dst": "总部", "relation": "围堵", "confidence": 0.85},
            {"src": "基金会", "dst": "老兵", "relation": "筛选", "confidence": 0.7},
            {"src": "刻雷乌斯", "dst": "乌鸫", "relation": "对付", "confidence": 0.8},
            {"src": "学校", "dst": "瞭望塔", "relation": "不曾有", "confidence": 0.7},
            {"src": "教员", "dst": "瞭望塔", "relation": "提及", "confidence": 0.7},
            {"src": "显形药剂", "dst": "瞭望塔", "relation": "显影", "confidence": 0.7},
        ],
    },
    # v1.8 来亚什基镇民 / 帕特里基 / 芝诺提议
    "4b448b5f7c47615f": {
        "entities": [
            {"name": "镇民Ⅱ", "type": "角色", "aliases": []},
            {"name": "贝托尔特", "type": "角色", "aliases": []},
            {"name": "叶甫根尼", "type": "角色", "aliases": ["叶甫根尼同志"]},
            {"name": "矿石", "type": "物品", "aliases": []},
            {"name": "阿廖卡", "type": "物品", "aliases": []},
            {"name": "帕特里基", "type": "角色", "aliases": []},
            {"name": "铁皮罐头", "type": "物品", "aliases": []},
            {"name": "果酱", "type": "物品", "aliases": []},
            {"name": "面粉", "type": "物品", "aliases": []},
            {"name": "土豆", "type": "物品", "aliases": []},
            {"name": "魔精", "type": "角色", "aliases": []},
            {"name": "来亚什基", "type": "地点", "aliases": []},
            {"name": "芝诺", "type": "角色", "aliases": []},
            {"name": "工厂", "type": "地点", "aliases": []},
            {"name": "机器", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "镇民Ⅱ", "dst": "矿石", "relation": "提及", "confidence": 0.7},
            {"src": "贝托尔特", "dst": "叶甫根尼", "relation": "等候", "confidence": 0.85},
            {"src": "帕特里基", "dst": "阿廖卡", "relation": "分发", "confidence": 0.85},
            {"src": "帕特里基", "dst": "来亚什基", "relation": "居住", "confidence": 0.85},
            {"src": "帕特里基", "dst": "铁皮罐头", "relation": "分食", "confidence": 0.8},
            {"src": "帕特里基", "dst": "果酱", "relation": "储存", "confidence": 0.8},
            {"src": "帕特里基", "dst": "面粉", "relation": "储存", "confidence": 0.8},
            {"src": "帕特里基", "dst": "土豆", "relation": "提及", "confidence": 0.8},
            {"src": "帕特里基", "dst": "魔精", "relation": "提及", "confidence": 0.7},
            {"src": "叶甫根尼", "dst": "芝诺", "relation": "回应提议", "confidence": 0.8},
            {"src": "芝诺", "dst": "来亚什基", "relation": "威胁", "confidence": 0.8},
            {"src": "芝诺", "dst": "工厂", "relation": "威胁", "confidence": 0.8},
            {"src": "芝诺", "dst": "机器", "relation": "威胁", "confidence": 0.8},
        ],
    },
    # v2.5 洛杉矶神秘学警察教官考核
    "0cbe77810f04094d": {
        "entities": [
            {"name": "波蒂埃", "type": "角色", "aliases": ["波蒂埃教官"]},
            {"name": "梁月", "type": "角色", "aliases": []},
            {"name": "洛杉矶神秘学警察", "type": "组织", "aliases": []},
            {"name": "洛杉矶", "type": "地点", "aliases": []},
            {"name": "神秘学犯罪", "type": "概念", "aliases": []},
            {"name": "市民", "type": "角色", "aliases": []},
            {"name": "督察组", "type": "组织", "aliases": []},
            {"name": "神秘学条子", "type": "角色", "aliases": ['"神秘学条子"']},
            {"name": "嘉宾夜现场", "type": "事件", "aliases": []},
            {"name": "青年演员", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "波蒂埃", "dst": "梁月", "relation": "任教官", "confidence": 0.9},
            {"src": "波蒂埃", "dst": "洛杉矶神秘学警察", "relation": "隶属", "confidence": 0.9},
            {"src": "梁月", "dst": "洛杉矶神秘学警察", "relation": "隶属", "confidence": 0.9},
            {"src": "洛杉矶神秘学警察", "dst": "洛杉矶", "relation": "辖区", "confidence": 0.9},
            {"src": "洛杉矶神秘学警察", "dst": "神秘学犯罪", "relation": "打击", "confidence": 0.85},
            {"src": "洛杉矶神秘学警察", "dst": "市民", "relation": "服务", "confidence": 0.8},
            {"src": "神秘学条子", "dst": "洛杉矶神秘学警察", "relation": "别称", "confidence": 0.9},
            {"src": "波蒂埃", "dst": "督察组", "relation": "提及", "confidence": 0.7},
            {"src": "嘉宾夜现场", "dst": "青年演员", "relation": "邀请", "confidence": 0.8},
        ],
    },
    # v2.4 神秘学族群史 / 努库泰澳 / 星锑试用期
    "fc25dba5b07238cb": {
        "entities": [
            {"name": "羊皮纸", "type": "物品", "aliases": []},
            {"name": "神秘学族群史", "type": "物品", "aliases": ["《神秘学族群史》"]},
            {"name": "努库泰澳", "type": "地点", "aliases": ["努库泰澳人"]},
            {"name": "贝壳人", "type": "角色", "aliases": []},
            {"name": "寄居蟹人", "type": "角色", "aliases": []},
            {"name": "南太平洋", "type": "地点", "aliases": []},
            {"name": "大航海时代", "type": "时间", "aliases": []},
            {"name": "星锑", "type": "角色", "aliases": []},
            {"name": "暴雨专项研究小组", "type": "组织", "aliases": ["专项研究小组"]},
            {"name": "圣洛夫基金会", "type": "组织", "aliases": []},
            {"name": "通讯设备", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "羊皮纸", "dst": "神秘学族群史", "relation": "注释", "confidence": 0.8},
            {"src": "努库泰澳", "dst": "神秘学族群史", "relation": "记载于", "confidence": 0.85},
            {"src": "努库泰澳", "dst": "大航海时代", "relation": "现世于", "confidence": 0.8},
            {"src": "南太平洋", "dst": "贝壳人", "relation": "传说记载", "confidence": 0.8},
            {"src": "南太平洋", "dst": "寄居蟹人", "relation": "传说记载", "confidence": 0.8},
            {"src": "星锑", "dst": "暴雨专项研究小组", "relation": "隶属", "confidence": 0.9},
            {"src": "暴雨专项研究小组", "dst": "圣洛夫基金会", "relation": "隶属", "confidence": 0.85},
            {"src": "暴雨专项研究小组", "dst": "通讯设备", "relation": "验证", "confidence": 0.8},
        ],
    },
    # v2.4 星锑告别爱兹拉 / 自由海风号登船风波
    "3cf210c4f6b785f6": {
        "entities": [
            {"name": "星锑", "type": "角色", "aliases": ["星锑女士"]},
            {"name": "爱兹拉", "type": "角色", "aliases": []},
            {"name": "大副", "type": "角色", "aliases": []},
            {"name": "科算中心", "type": "组织", "aliases": []},
            {"name": "部门之声", "type": "概念", "aliases": []},
            {"name": "人事部门", "type": "组织", "aliases": []},
            {"name": "芭卡洛儿", "type": "角色", "aliases": ["芭卡洛儿小姐"]},
            {"name": "船长", "type": "角色", "aliases": []},
            {"name": "自由海风号", "type": "物品", "aliases": ['"自由海风号"']},
            {"name": "拉普拉斯", "type": "组织", "aliases": []},
            {"name": "泰晤士河", "type": "地点", "aliases": []},
            {"name": "伦敦", "type": "地点", "aliases": []},
            {"name": "英国广播台", "type": "组织", "aliases": []},
            {"name": "唱片公司", "type": "组织", "aliases": []},
            {"name": "英国政府", "type": "组织", "aliases": []},
            {"name": "摇滚海盗", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "星锑", "dst": "爱兹拉", "relation": "道别", "confidence": 0.85},
            {"src": "星锑", "dst": "大副", "relation": "道别", "confidence": 0.8},
            {"src": "爱兹拉", "dst": "科算中心", "relation": "隶属", "confidence": 0.85},
            {"src": "爱兹拉", "dst": "人事部门", "relation": "提及", "confidence": 0.7},
            {"src": "部门之声", "dst": "科算中心", "relation": "隶属", "confidence": 0.8},
            {"src": "星锑", "dst": "拉普拉斯", "relation": "隶属", "confidence": 0.85},
            {"src": "星锑", "dst": "自由海风号", "relation": "登船被拒", "confidence": 0.85},
            {"src": "芭卡洛儿", "dst": "自由海风号", "relation": "试图登船", "confidence": 0.8},
            {"src": "芭卡洛儿", "dst": "船长", "relation": "交涉", "confidence": 0.8},
            {"src": "摇滚海盗", "dst": "泰晤士河", "relation": "广播于", "confidence": 0.8},
            {"src": "摇滚海盗", "dst": "伦敦", "relation": "占领", "confidence": 0.8},
            {"src": "摇滚海盗", "dst": "英国广播台", "relation": "为敌", "confidence": 0.85},
            {"src": "摇滚海盗", "dst": "唱片公司", "relation": "为敌", "confidence": 0.85},
            {"src": "英国政府", "dst": "摇滚海盗", "relation": "取缔", "confidence": 0.85},
            {"src": "摇滚海盗", "dst": "星锑", "relation": "同名", "confidence": 0.7},
        ],
    },
    # v1.6 神秘学探索场景（机翻碎块，仅抽明确出现的具体词）
    "0c3246bbd43c0d11": {
        "entities": [
            {"name": "鸳鸯", "type": "角色", "aliases": ["巨大的鸳鸯"]},
            {"name": "警察", "type": "组织", "aliases": []},
            {"name": "翻译者", "type": "角色", "aliases": []},
            {"name": "城市", "type": "地点", "aliases": ["你面前的城市"]},
        ],
        "relations": [
            {"src": "警察", "dst": "城市", "relation": "巡逻", "confidence": 0.7},
            {"src": "鸳鸯", "dst": "城市", "relation": "现身于", "confidence": 0.6},
        ],
    },
}


def validate() -> int:
    bad = 0
    for h, d in RESULTS.items():
        pool = set()
        for e in d.get("entities") or []:
            pool.add(str(e.get("name") or "").strip())
            pool |= {str(a).strip() for a in (e.get("aliases") or [])}
        for r in d.get("relations") or []:
            for k in ("src", "dst"):
                if str(r.get(k) or "").strip() not in pool:
                    print(f"[dangling] {h} {k}={r.get(k)}")
                    bad += 1
    return bad


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    n = validate()
    print(f"[validate] 块 {len(RESULTS)}，悬空 {n}")
    if n:
        return 1
    if not args.apply:
        print("[dry-run] 加 --apply 写盘")
        return 0
    for h, d in RESULTS.items():
        (CACHE / f"{h}.json").write_text(
            json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    print(f"[apply-missing-p10] 写入 {len(RESULTS)} 条，NOOP +{len(NOOP_ADD)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
