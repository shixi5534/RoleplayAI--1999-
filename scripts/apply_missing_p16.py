# -*- coding: utf-8 -*-
"""未抽取剧情块补抽 · 第 16 批（backfill2 batch_06，20 块）。

用法：
  python scripts/apply_missing_p16.py            # 预演（悬空+落地自检）
  python scripts/apply_missing_p16.py --apply    # 写盘
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

# 本批 20 块均含剧情正文，无数值/UI/空块，NOOP 集合为空。
NOOP_ADD: list[str] = []

RESULTS: dict[str, dict] = {
    # 1) 乌切洛与众人作画 · 教堂地底梦魇兽与苏卡拉特 · 书商的笔记
    "a870f0506280a6fa": {
        "entities": [
            {"name": "乌切洛", "type": "角色", "aliases": []},
            {"name": "苏芙比", "type": "角色", "aliases": ["苏芙比小姐"]},
            {"name": "莱昂纳多", "type": "角色", "aliases": ["莱昂纳多先生"]},
            {"name": "拉·沃尔佩", "type": "角色", "aliases": ["狐狸先生"]},
            {"name": "梦魇兽", "type": "角色", "aliases": []},
            {"name": "苏卡拉特", "type": "角色", "aliases": []},
            {"name": "教堂地底", "type": "地点", "aliases": ["大教堂的地下室"]},
            {"name": "颜料", "type": "物品", "aliases": []},
            {"name": "熏香", "type": "物品", "aliases": []},
            {"name": "书商的笔记", "type": "物品", "aliases": []},
            {"name": "画稿", "type": "物品", "aliases": ["有孔洞的画稿"]},
        ],
        "relations": [
            {"src": "乌切洛", "dst": "颜料", "relation": "分发", "confidence": 0.8},
            {"src": "苏芙比", "dst": "梦魇兽", "relation": "发现", "confidence": 0.8},
            {"src": "苏芙比", "dst": "苏卡拉特", "relation": "描述", "confidence": 0.7},
            {"src": "拉·沃尔佩", "dst": "苏芙比", "relation": "称呼", "confidence": 0.8},
            {"src": "拉·沃尔佩", "dst": "莱昂纳多", "relation": "提醒", "confidence": 0.7},
            {"src": "教堂地底", "dst": "梦魇兽", "relation": "豢养", "confidence": 0.7},
        ],
    },
    # 2) 显微镜与科算中心内部报告会 · 长腿牧者人造下肢
    "dff7f01e9a1bebf3": {
        "entities": [
            {"name": "显微镜", "type": "物品", "aliases": []},
            {"name": "静置一旁的笔记本", "type": "物品", "aliases": []},
            {"name": "科算中心内部报告会笔记", "type": "物品", "aliases": ["第206期科算中心内部报告会-笔记"]},
            {"name": "卡拉汉", "type": "角色", "aliases": ["卡拉汉议员"]},
            {"name": "小卡拉汉", "type": "角色", "aliases": ["小卡拉汉博士"]},
            {"name": "拉普拉斯科算中心", "type": "组织", "aliases": []},
            {"name": "斑马线", "type": "概念", "aliases": []},
            {"name": "长腿牧者", "type": "物品", "aliases": ["长腿牧者[Tchangues]1-07完成版"]},
            {"name": "佩罗蒂", "type": "角色", "aliases": ["佩罗蒂女士"]},
            {"name": "人造下肢", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "卡拉汉", "dst": "科算中心内部报告会笔记", "relation": "提交", "confidence": 0.8},
            {"src": "小卡拉汉", "dst": "科算中心内部报告会笔记", "relation": "提交", "confidence": 0.8},
            {"src": "拉普拉斯科算中心", "dst": "科算中心内部报告会笔记", "relation": "举办", "confidence": 0.8},
            {"src": "小卡拉汉", "dst": "卡拉汉", "relation": "是曾孙", "confidence": 0.9},
            {"src": "长腿牧者", "dst": "拉普拉斯科算中心", "relation": "体现理念", "confidence": 0.8},
            {"src": "佩罗蒂", "dst": "长腿牧者", "relation": "发明", "confidence": 0.9},
            {"src": "长腿牧者", "dst": "人造下肢", "relation": "是", "confidence": 0.9},
            {"src": "科算中心内部报告会笔记", "dst": "斑马线", "relation": "研究", "confidence": 0.8},
        ],
    },
    # 3) 头顶空空之人与被裁剪旧报纸 · 弃票讨论
    "069a7299b5c10a5f": {
        "entities": [
            {"name": "头顶空空之人", "type": "概念", "aliases": []},
            {"name": "被裁剪过的旧报纸", "type": "物品", "aliases": []},
            {"name": "弃票", "type": "概念", "aliases": []},
            {"name": "弃票箱", "type": "物品", "aliases": []},
            {"name": "选择的自由", "type": "概念", "aliases": []},
            {"name": "差异者", "type": "概念", "aliases": []},
            {"name": "电梯间", "type": "地点", "aliases": []},
            {"name": "美洲大蠊", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "被裁剪过的旧报纸", "dst": "弃票", "relation": "讨论", "confidence": 0.8},
            {"src": "被裁剪过的旧报纸", "dst": "弃票箱", "relation": "提及", "confidence": 0.7},
            {"src": "弃票", "dst": "选择的自由", "relation": "象征", "confidence": 0.7},
            {"src": "弃票", "dst": "差异者", "relation": "促成", "confidence": 0.7},
        ],
    },
    # 4) 命运的奴隶独白 · 午夜哀声/异域面具目击记录 · 玛丽姨妈失踪报案
    "e4f4b4ab8fcf17b7": {
        "entities": [
            {"name": "命运", "type": "概念", "aliases": []},
            {"name": "目击记录", "type": "物品", "aliases": []},
            {"name": "午夜哀声", "type": "事件", "aliases": []},
            {"name": "酒店安保人员", "type": "角色", "aliases": []},
            {"name": "异域面具", "type": "物品", "aliases": []},
            {"name": "流浪汉", "type": "角色", "aliases": []},
            {"name": "螃蟹面具", "type": "物品", "aliases": []},
            {"name": "警铃大作", "type": "事件", "aliases": []},
            {"name": "接线员", "type": "角色", "aliases": []},
            {"name": "警察", "type": "角色", "aliases": []},
            {"name": "一通报案电话", "type": "物品", "aliases": []},
            {"name": "玛丽姨妈", "type": "角色", "aliases": []},
            {"name": "小巷", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "酒店安保人员", "dst": "午夜哀声", "relation": "陈述", "confidence": 0.8},
            {"src": "流浪汉", "dst": "异域面具", "relation": "目击", "confidence": 0.8},
            {"src": "流浪汉", "dst": "螃蟹面具", "relation": "目击", "confidence": 0.8},
            {"src": "螃蟹面具", "dst": "异域面具", "relation": "属于", "confidence": 0.8},
            {"src": "一通报案电话", "dst": "玛丽姨妈", "relation": "报告失踪", "confidence": 0.8},
            {"src": "警察", "dst": "警铃大作", "relation": "响应", "confidence": 0.7},
            {"src": "目击记录", "dst": "午夜哀声", "relation": "包含", "confidence": 0.7},
            {"src": "目击记录", "dst": "异域面具", "relation": "包含", "confidence": 0.7},
        ],
    },
    # 5) 落寞家族与神秘学家荣光 · 梦中小象 · 迷思海定名与弃票
    "ddd6bf7eace18734": {
        "entities": [
            {"name": "神秘学家", "type": "概念", "aliases": []},
            {"name": "目击记录", "type": "物品", "aliases": []},
            {"name": "梦中小象", "type": "事件", "aliases": []},
            {"name": "玩偶小象", "type": "物品", "aliases": []},
            {"name": "公园", "type": "地点", "aliases": []},
            {"name": "迷思之海", "type": "概念", "aliases": ["迷思海"]},
            {"name": "引导之人", "type": "角色", "aliases": []},
            {"name": "暴雨", "type": "现象", "aliases": []},
            {"name": "宝库", "type": "概念", "aliases": ["意象宝库"]},
            {"name": "费利西安", "type": "角色", "aliases": []},
            {"name": "灰调蓝", "type": "概念", "aliases": []},
            {"name": "劳伦·罗西", "type": "角色", "aliases": []},
            {"name": "阴谋", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "梦中小象", "dst": "玩偶小象", "relation": "关联", "confidence": 0.8},
            {"src": "引导之人", "dst": "暴雨", "relation": "关联", "confidence": 0.7},
            {"src": "暴雨", "dst": "迷思之海", "relation": "促成", "confidence": 0.8},
            {"src": "迷思之海", "dst": "宝库", "relation": "是", "confidence": 0.9},
            {"src": "费利西安", "dst": "灰调蓝", "relation": "关联", "confidence": 0.8},
            {"src": "劳伦·罗西", "dst": "阴谋", "relation": "策划", "confidence": 0.8},
            {"src": "目击记录", "dst": "梦中小象", "relation": "包含", "confidence": 0.7},
        ],
    },
    # 6) 托勒密为玛尔纱注射吗啡 · 电报汇报匪军渗透与基金会对抗
    "912b29c97b80a8b7": {
        "entities": [
            {"name": "托勒密", "type": "角色", "aliases": []},
            {"name": "医生", "type": "角色", "aliases": []},
            {"name": "吗啡", "type": "物品", "aliases": []},
            {"name": "玛尔纱", "type": "角色", "aliases": []},
            {"name": "梅蕾尔", "type": "角色", "aliases": []},
            {"name": "枪伤", "type": "概念", "aliases": []},
            {"name": "明码联系", "type": "事件", "aliases": []},
            {"name": "一封发给骑兵军指挥部的电报", "type": "物品", "aliases": ["电报"]},
            {"name": "骑兵军指挥部", "type": "组织", "aliases": []},
            {"name": "匪军", "type": "组织", "aliases": []},
            {"name": "狮鹫军", "type": "组织", "aliases": []},
            {"name": "骑兵军基金会", "type": "组织", "aliases": []},
            {"name": "波克罗夫儿童医院", "type": "组织", "aliases": []},
            {"name": "保温箱", "type": "物品", "aliases": []},
            {"name": "蒸气吸入器", "type": "物品", "aliases": []},
            {"name": "民兵第7街区自编连", "type": "组织", "aliases": []},
            {"name": "民兵第3街道自编连", "type": "组织", "aliases": []},
            {"name": "南城医疗物资仓库", "type": "地点", "aliases": []},
            {"name": "西城", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "托勒密", "dst": "吗啡", "relation": "注射", "confidence": 0.8},
            {"src": "托勒密", "dst": "玛尔纱", "relation": "关心", "confidence": 0.7},
            {"src": "梅蕾尔", "dst": "玛尔纱", "relation": "唤醒", "confidence": 0.8},
            {"src": "玛尔纱", "dst": "枪伤", "relation": "受", "confidence": 0.8},
            {"src": "玛尔纱", "dst": "医生", "relation": "请求", "confidence": 0.8},
            {"src": "一封发给骑兵军指挥部的电报", "dst": "骑兵军指挥部", "relation": "发给", "confidence": 0.9},
            {"src": "一封发给骑兵军指挥部的电报", "dst": "匪军", "relation": "报告", "confidence": 0.8},
            {"src": "狮鹫军", "dst": "匪军", "relation": "协同抵御", "confidence": 0.8},
            {"src": "骑兵军基金会", "dst": "波克罗夫儿童医院", "relation": "支援", "confidence": 0.8},
            {"src": "民兵第7街区自编连", "dst": "南城医疗物资仓库", "relation": "防卫", "confidence": 0.8},
            {"src": "民兵第3街道自编连", "dst": "西城", "relation": "守卫", "confidence": 0.8},
        ],
    },
    # 7) 工艺流程注意事项 · 鸣枪之后参谋长与军长伊万遣散娃娃兵
    "4e44e8f626f06db2": {
        "entities": [
            {"name": "人类和平安全理事会", "type": "组织", "aliases": []},
            {"name": "鸣枪之后", "type": "事件", "aliases": []},
            {"name": "参谋长", "type": "角色", "aliases": []},
            {"name": "马刺", "type": "物品", "aliases": []},
            {"name": "军长伊万", "type": "角色", "aliases": ["伊万"]},
            {"name": "斯捷尔诺娃", "type": "角色", "aliases": []},
            {"name": "嫩芦苇", "type": "角色", "aliases": ['"嫩芦苇"']},
            {"name": "娃娃兵", "type": "角色", "aliases": []},
            {"name": "埃梅利", "type": "角色", "aliases": []},
            {"name": "穆雷恒", "type": "角色", "aliases": ["穆雷恒大尉"]},
            {"name": "战功勋章", "type": "物品", "aliases": []},
            {"name": "金色饥荒", "type": "事件", "aliases": ['"金色饥荒"']},
            {"name": "草原", "type": "地点", "aliases": []},
            {"name": "老兵", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "军长伊万", "dst": "斯捷尔诺娃", "relation": "询问", "confidence": 0.7},
            {"src": "斯捷尔诺娃", "dst": "军长伊万", "relation": "请示", "confidence": 0.8},
            {"src": "军长伊万", "dst": "埃梅利", "relation": "授予", "confidence": 0.8},
            {"src": "埃梅利", "dst": "娃娃兵", "relation": "掩护", "confidence": 0.8},
            {"src": "埃梅利", "dst": "穆雷恒", "relation": "隶属", "confidence": 0.8},
            {"src": "斯捷尔诺娃", "dst": "娃娃兵", "relation": "发现", "confidence": 0.7},
            {"src": "军长伊万", "dst": "金色饥荒", "relation": "提及", "confidence": 0.8},
            {"src": "参谋长", "dst": "马刺", "relation": "佩戴", "confidence": 0.7},
            {"src": "军长伊万", "dst": "老兵", "relation": "提及", "confidence": 0.7},
            {"src": "嫩芦苇", "dst": "娃娃兵", "relation": "指代", "confidence": 0.7},
        ],
    },
    # 8) 海域神秘学生物报告与批复 · 百科全书介绍宁芙与人鱼
    "be9b16768b6221a3": {
        "entities": [
            {"name": "官僚机构", "type": "组织", "aliases": []},
            {"name": "海域神秘学生物异常表现报告", "type": "物品", "aliases": ["关于■■■海域神秘学生物异常表现的报告", "重复报告"]},
            {"name": "斯库拉", "type": "角色", "aliases": []},
            {"name": "船员", "type": "角色", "aliases": []},
            {"name": "牛头人身怪", "type": "角色", "aliases": []},
            {"name": "九头蛇", "type": "角色", "aliases": ["拥有巨大眼球的九头蛇"]},
            {"name": "基金会", "type": "组织", "aliases": []},
            {"name": "暴雨", "type": "现象", "aliases": []},
            {"name": "磁场紊乱", "type": "现象", "aliases": []},
            {"name": "神秘学能量", "type": "概念", "aliases": []},
            {"name": "百科全书", "type": "物品", "aliases": []},
            {"name": "九万个为什么——神秘学种族篇", "type": "物品", "aliases": []},
            {"name": "宁芙", "type": "角色", "aliases": []},
            {"name": "人鱼", "type": "角色", "aliases": []},
            {"name": "海洋的子民", "type": "概念", "aliases": ['"海洋的子民"']},
        ],
        "relations": [
            {"src": "斯库拉", "dst": "船员", "relation": "攻击", "confidence": 0.8},
            {"src": "基金会", "dst": "海域神秘学生物异常表现报告", "relation": "批复", "confidence": 0.8},
            {"src": "基金会", "dst": "暴雨", "relation": "提及", "confidence": 0.7},
            {"src": "九万个为什么——神秘学种族篇", "dst": "宁芙", "relation": "介绍", "confidence": 0.8},
            {"src": "宁芙", "dst": "人鱼", "relation": "是", "confidence": 0.9},
            {"src": "人鱼", "dst": "海洋的子民", "relation": "自称", "confidence": 0.8},
            {"src": "海域神秘学生物异常表现报告", "dst": "斯库拉", "relation": "提及", "confidence": 0.8},
            {"src": "牛头人身怪", "dst": "九头蛇", "relation": "同为怪物", "confidence": 0.7},
        ],
    },
    # 9) 前任列车长赫尔曼失踪 · 血食怪档案 · UTTU编辑空心木
    "4fa171c375a8f16e": {
        "entities": [
            {"name": "赫尔曼", "type": "角色", "aliases": ["赫尔曼先生"]},
            {"name": "政府", "type": "组织", "aliases": []},
            {"name": "勋章", "type": "物品", "aliases": ["银闪闪的勋章"]},
            {"name": "多瑙黎明号", "type": "物品", "aliases": ['"多瑙黎明号"']},
            {"name": "乘客", "type": "角色", "aliases": []},
            {"name": "布达佩斯", "type": "地点", "aliases": []},
            {"name": "血食怪", "type": "角色", "aliases": ["超自然者血食怪"]},
            {"name": "UTTU", "type": "物品", "aliases": ["《UTTU》"]},
            {"name": "空心木", "type": "角色", "aliases": []},
            {"name": "谁的梦魇", "type": "事件", "aliases": []},
            {"name": "超自然者血食怪档案", "type": "物品", "aliases": ["《超自然者血食怪档案》"]},
            {"name": "永恒", "type": "概念", "aliases": ['"永恒"']},
        ],
        "relations": [
            {"src": "政府", "dst": "赫尔曼", "relation": "授予", "confidence": 0.8},
            {"src": "赫尔曼", "dst": "勋章", "relation": "拥有", "confidence": 0.8},
            {"src": "赫尔曼", "dst": "多瑙黎明号", "relation": "隶属", "confidence": 0.8},
            {"src": "血食怪", "dst": "赫尔曼", "relation": "带走", "confidence": 0.8},
            {"src": "空心木", "dst": "UTTU", "relation": "编辑", "confidence": 0.9},
            {"src": "超自然者血食怪档案", "dst": "血食怪", "relation": "记录", "confidence": 0.9},
            {"src": "谁的梦魇", "dst": "超自然者血食怪档案", "relation": "翻看", "confidence": 0.8},
            {"src": "赫尔曼", "dst": "布达佩斯", "relation": "消失于", "confidence": 0.8},
        ],
    },
    # 10) 鲍里斯与告死鸟谈解放阵线 · 士兵守卫临时拘留室听到卢卡
    "102d6c9898e8216a": {
        "entities": [
            {"name": "鲍里斯", "type": "角色", "aliases": []},
            {"name": "告死鸟", "type": "角色", "aliases": []},
            {"name": "解放阵线", "type": "组织", "aliases": []},
            {"name": "伊斯坦布尔", "type": "地点", "aliases": []},
            {"name": "难民", "type": "角色", "aliases": []},
            {"name": "列车", "type": "物品", "aliases": []},
            {"name": "火车站", "type": "地点", "aliases": []},
            {"name": "游击队员", "type": "角色", "aliases": []},
            {"name": "士兵Ⅰ", "type": "角色", "aliases": []},
            {"name": "士兵Ⅱ", "type": "角色", "aliases": []},
            {"name": "临时拘留室", "type": "地点", "aliases": []},
            {"name": "卢卡", "type": "角色", "aliases": []},
            {"name": "无意义疑问", "type": "事件", "aliases": []},
        ],
        "relations": [
            {"src": "告死鸟", "dst": "解放阵线", "relation": "隶属", "confidence": 0.8},
            {"src": "鲍里斯", "dst": "告死鸟", "relation": "邀请", "confidence": 0.8},
            {"src": "难民", "dst": "列车", "relation": "试图搭乘", "confidence": 0.8},
            {"src": "告死鸟", "dst": "游击队员", "relation": "被称作", "confidence": 0.8},
            {"src": "士兵Ⅰ", "dst": "临时拘留室", "relation": "守卫", "confidence": 0.8},
            {"src": "士兵Ⅱ", "dst": "临时拘留室", "relation": "守卫", "confidence": 0.8},
            {"src": "士兵Ⅰ", "dst": "卢卡", "relation": "听到", "confidence": 0.8},
            {"src": "士兵Ⅰ", "dst": "士兵Ⅱ", "relation": "对话", "confidence": 0.7},
            {"src": "鲍里斯", "dst": "告死鸟", "relation": "对话", "confidence": 0.7},
        ],
    },
    # 11) 感谢声明寻犬 · 海盗电台与海盗船长 · 机会主义入门
    "f887683656ab1077": {
        "entities": [
            {"name": "感谢声明一则", "type": "物品", "aliases": []},
            {"name": "克劳斯", "type": "角色", "aliases": ["英国斗牛犬"]},
            {"name": "边境牧羊犬", "type": "角色", "aliases": ["边境牧羊犬先生"]},
            {"name": "肯辛顿高街", "type": "地点", "aliases": []},
            {"name": "啃啃乐", "type": "物品", "aliases": ['"啃啃乐"']},
            {"name": "开胃酒", "type": "概念", "aliases": ['"开胃酒"']},
            {"name": "海盗入侵电台", "type": "事件", "aliases": []},
            {"name": "海盗船长", "type": "角色", "aliases": []},
            {"name": "无线电清洁行动", "type": "事件", "aliases": ['"无线电清洁行动"']},
            {"name": "唱片", "type": "物品", "aliases": []},
            {"name": "磁带", "type": "物品", "aliases": []},
            {"name": "红色小船", "type": "物品", "aliases": []},
            {"name": "街道警探", "type": "角色", "aliases": []},
            {"name": "海盗电台", "type": "组织", "aliases": []},
            {"name": "伦敦评论", "type": "物品", "aliases": ["《伦敦评论》"]},
            {"name": "机会主义入门", "type": "物品", "aliases": []},
            {"name": "神偷", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "边境牧羊犬", "dst": "克劳斯", "relation": "领回", "confidence": 0.8},
            {"src": "感谢声明一则", "dst": "克劳斯", "relation": "提及", "confidence": 0.7},
            {"src": "海盗船长", "dst": "海盗电台", "relation": "拥有", "confidence": 0.8},
            {"src": "海盗船长", "dst": "唱片", "relation": "拥有", "confidence": 0.8},
            {"src": "海盗船长", "dst": "红色小船", "relation": "拥有", "confidence": 0.8},
            {"src": "海盗船长", "dst": "无线电清洁行动", "relation": "逃脱", "confidence": 0.8},
            {"src": "海盗入侵电台", "dst": "海盗电台", "relation": "关于", "confidence": 0.8},
            {"src": "海盗入侵电台", "dst": "伦敦评论", "relation": "刊登于", "confidence": 0.8},
            {"src": "机会主义入门", "dst": "神偷", "relation": "提及", "confidence": 0.7},
            {"src": "海盗船长", "dst": "街道警探", "relation": "躲避", "confidence": 0.7},
        ],
    },
    # 12) 玛蒂尔达与环状水星论灵性宇宙能量 · 歌曲我们会活下去
    "c76775d092791ab5": {
        "entities": [
            {"name": "玛蒂尔达", "type": "角色", "aliases": []},
            {"name": "环状水星", "type": "角色", "aliases": []},
            {"name": "灵性", "type": "概念", "aliases": ['"灵性"']},
            {"name": "宇宙能量", "type": "概念", "aliases": ['"宇宙能量"']},
            {"name": "泛神论派", "type": "概念", "aliases": []},
            {"name": "东方泛灵论", "type": "概念", "aliases": []},
            {"name": "我们会活下去", "type": "物品", "aliases": ['"我们会活下去"', "《我们会活下去》"]},
            {"name": "海特街", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "玛蒂尔达", "dst": "灵性", "relation": "探讨", "confidence": 0.8},
            {"src": "环状水星", "dst": "宇宙能量", "relation": "主张", "confidence": 0.8},
            {"src": "玛蒂尔达", "dst": "环状水星", "relation": "认为泛神论", "confidence": 0.7},
            {"src": "玛蒂尔达", "dst": "我们会活下去", "relation": "演唱", "confidence": 0.7},
            {"src": "我们会活下去", "dst": "海特街", "relation": "提及", "confidence": 0.8},
        ],
    },
    # 13) 剃刀小队涂名 · 启明会逼近海特街 · 唐吉老爹谈餐馆由来
    "bda6b39bfb738da4": {
        "entities": [
            {"name": "剃刀小队", "type": "组织", "aliases": ["“剃刀”小队"]},
            {"name": "启明会", "type": "组织", "aliases": []},
            {"name": "海特街", "type": "地点", "aliases": []},
            {"name": "胜利晚宴", "type": "事件", "aliases": []},
            {"name": "一切的原点", "type": "事件", "aliases": []},
            {"name": "唐吉老爹", "type": "角色", "aliases": []},
            {"name": "J", "type": "角色", "aliases": []},
            {"name": "霍利克", "type": "角色", "aliases": []},
            {"name": "贝克特", "type": "角色", "aliases": []},
            {"name": "唐人街", "type": "地点", "aliases": []},
            {"name": "黑帮", "type": "组织", "aliases": []},
            {"name": "卫生许可证", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "剃刀小队", "dst": "海特街", "relation": "控制", "confidence": 0.7},
            {"src": "启明会", "dst": "海特街", "relation": "活动于", "confidence": 0.7},
            {"src": "唐吉老爹", "dst": "J", "relation": "对话", "confidence": 0.8},
            {"src": "唐吉老爹", "dst": "霍利克", "relation": "提及", "confidence": 0.7},
            {"src": "唐吉老爹", "dst": "贝克特", "relation": "提及", "confidence": 0.7},
            {"src": "唐吉老爹", "dst": "唐人街", "relation": "来自", "confidence": 0.8},
            {"src": "黑帮", "dst": "唐吉老爹", "relation": "捣乱", "confidence": 0.7},
            {"src": "胜利晚宴", "dst": "启明会", "relation": "提及", "confidence": 0.7},
            {"src": "一切的原点", "dst": "唐吉老爹", "relation": "进入对话", "confidence": 0.7},
        ],
    },
    # 14) J与环状水星 · 鸵鸟电台宣扬宝瓶座时代放送歌曲
    "5fa049e801d916d7": {
        "entities": [
            {"name": "J", "type": "角色", "aliases": []},
            {"name": "环状水星", "type": "角色", "aliases": []},
            {"name": "不安", "type": "概念", "aliases": ['"不安"']},
            {"name": "宝瓶座时代", "type": "概念", "aliases": ['"宝瓶座时代"']},
            {"name": "双鱼座时代", "type": "概念", "aliases": ['"双鱼座时代"']},
            {"name": "鸵鸟电台", "type": "组织", "aliases": []},
            {"name": "The Golden City", "type": "物品", "aliases": ['"The Golden City"', "《The Golden City》"]},
            {"name": "另一个时代", "type": "物品", "aliases": ['"另一个时代"', "《另一个时代》"]},
            {"name": "黑帮", "type": "组织", "aliases": []},
            {"name": "迪斯科", "type": "概念", "aliases": []},
            {"name": "螺丝起子", "type": "物品", "aliases": []},
            {"name": "灯球", "type": "物品", "aliases": []},
            {"name": "魔精", "type": "角色", "aliases": []},
            {"name": "最初的伙伴", "type": "事件", "aliases": []},
        ],
        "relations": [
            {"src": "J", "dst": "环状水星", "relation": "对话", "confidence": 0.7},
            {"src": "环状水星", "dst": "J", "relation": "安抚", "confidence": 0.7},
            {"src": "鸵鸟电台", "dst": "宝瓶座时代", "relation": "宣扬", "confidence": 0.8},
            {"src": "鸵鸟电台", "dst": "双鱼座时代", "relation": "提及", "confidence": 0.8},
            {"src": "鸵鸟电台", "dst": "The Golden City", "relation": "放送", "confidence": 0.9},
            {"src": "鸵鸟电台", "dst": "另一个时代", "relation": "放送", "confidence": 0.9},
            {"src": "宝瓶座时代", "dst": "双鱼座时代", "relation": "接续", "confidence": 0.7},
            {"src": "鸵鸟电台", "dst": "黑帮", "relation": "提及", "confidence": 0.7},
            {"src": "最初的伙伴", "dst": "魔精", "relation": "提及", "confidence": 0.7},
        ],
    },
    # 15) 旧金山往事与昨日今日 · 玛蒂尔达进迪斯科舞厅遇宇宙灯球
    "22ef02b896403f22": {
        "entities": [
            {"name": "魔精", "type": "角色", "aliases": []},
            {"name": "旧金山往事", "type": "物品", "aliases": []},
            {"name": "旧金山", "type": "地点", "aliases": []},
            {"name": "昨日，今日", "type": "物品", "aliases": ['"昨日，今日"', "《昨日，今日》"]},
            {"name": "90年代", "type": "时间", "aliases": []},
            {"name": "海特街", "type": "地点", "aliases": []},
            {"name": "新纪元集市", "type": "地点", "aliases": []},
            {"name": "水晶疗愈", "type": "概念", "aliases": []},
            {"name": "黑袍子", "type": "角色", "aliases": []},
            {"name": "灯球", "type": "物品", "aliases": []},
            {"name": "迪斯科", "type": "概念", "aliases": []},
            {"name": "唐老爹餐馆", "type": "地点", "aliases": []},
            {"name": "新气象", "type": "事件", "aliases": []},
            {"name": "宇宙灯球", "type": "物品", "aliases": ['"酷到没朋友的宇宙灯球"']},
            {"name": "玛蒂尔达", "type": "角色", "aliases": []},
            {"name": "迪斯科舞厅", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "旧金山往事", "dst": "旧金山", "relation": "关于", "confidence": 0.8},
            {"src": "昨日，今日", "dst": "旧金山", "relation": "描述", "confidence": 0.8},
            {"src": "昨日，今日", "dst": "海特街", "relation": "提及", "confidence": 0.8},
            {"src": "昨日，今日", "dst": "新纪元集市", "relation": "提及", "confidence": 0.8},
            {"src": "昨日，今日", "dst": "迪斯科", "relation": "提及", "confidence": 0.8},
            {"src": "玛蒂尔达", "dst": "迪斯科舞厅", "relation": "进入", "confidence": 0.8},
            {"src": "宇宙灯球", "dst": "迪斯科舞厅", "relation": "位于", "confidence": 0.7},
            {"src": "新气象", "dst": "唐老爹餐馆", "relation": "提及", "confidence": 0.7},
        ],
    },
    # 16) 环状水星谈洋流 · 崭新的新纪元摒弃启明会 · 菲娜取消玛蒂尔达77号公路任务
    "ed5f4e193b3cd69f": {
        "entities": [
            {"name": "环状水星", "type": "角色", "aliases": []},
            {"name": "玛蒂尔达", "type": "角色", "aliases": ["玛蒂尔达小姐"]},
            {"name": "崭新的新纪元", "type": "事件", "aliases": []},
            {"name": "启明会", "type": "组织", "aliases": []},
            {"name": "海特街", "type": "地点", "aliases": []},
            {"name": "新纪元集市", "type": "地点", "aliases": []},
            {"name": "宇宙能量", "type": "概念", "aliases": []},
            {"name": "活死人的黎明", "type": "事件", "aliases": []},
            {"name": "追赶者，被追赶者", "type": "事件", "aliases": []},
            {"name": "职员菲娜", "type": "角色", "aliases": []},
            {"name": "77号公路", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "启明会", "dst": "海特街", "relation": "不适合", "confidence": 0.8},
            {"src": "崭新的新纪元", "dst": "启明会", "relation": "摒弃", "confidence": 0.8},
            {"src": "崭新的新纪元", "dst": "新纪元集市", "relation": "重开", "confidence": 0.8},
            {"src": "崭新的新纪元", "dst": "宇宙能量", "relation": "宣扬", "confidence": 0.8},
            {"src": "活死人的黎明", "dst": "宇宙能量", "relation": "指引", "confidence": 0.7},
            {"src": "职员菲娜", "dst": "玛蒂尔达", "relation": "道歉", "confidence": 0.8},
            {"src": "玛蒂尔达", "dst": "77号公路", "relation": "计划前往", "confidence": 0.8},
            {"src": "职员菲娜", "dst": "玛蒂尔达", "relation": "致使取消任务", "confidence": 0.7},
        ],
    },
    # 17) 菲娜委派司辰红弩箭77号公路 · 鸵鸟电台播报航天 · 斯普特尼克想当迪斯科球
    "834cd78f001ce0e0": {
        "entities": [
            {"name": "职员菲娜", "type": "角色", "aliases": []},
            {"name": "司辰", "type": "角色", "aliases": []},
            {"name": "玛蒂尔达", "type": "角色", "aliases": []},
            {"name": "红弩箭", "type": "角色", "aliases": ["红弩箭女士"]},
            {"name": "维尔汀", "type": "角色", "aliases": []},
            {"name": "小目标、大目标", "type": "事件", "aliases": []},
            {"name": "鸵鸟电台", "type": "组织", "aliases": []},
            {"name": "旧金山", "type": "地点", "aliases": []},
            {"name": "哈勃望远镜", "type": "物品", "aliases": []},
            {"name": "地球", "type": "地点", "aliases": []},
            {"name": "挑战者号", "type": "物品", "aliases": []},
            {"name": "迪斯科球", "type": "物品", "aliases": []},
            {"name": "水星", "type": "地点", "aliases": []},
            {"name": "金星", "type": "地点", "aliases": []},
            {"name": "太阳系", "type": "概念", "aliases": []},
            {"name": "77号公路", "type": "地点", "aliases": []},
            {"name": "斯普特尼克", "type": "角色", "aliases": ["斯普特尼克女士"]},
            {"name": "护士", "type": "角色", "aliases": []},
            {"name": "贝克特", "type": "角色", "aliases": []},
            {"name": "杰洛", "type": "角色", "aliases": []},
            {"name": "大气层", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "职员菲娜", "dst": "司辰", "relation": "委派", "confidence": 0.8},
            {"src": "职员菲娜", "dst": "红弩箭", "relation": "委派", "confidence": 0.8},
            {"src": "司辰", "dst": "77号公路", "relation": "受委派执行", "confidence": 0.8},
            {"src": "红弩箭", "dst": "77号公路", "relation": "受委派执行", "confidence": 0.8},
            {"src": "玛蒂尔达", "dst": "维尔汀", "relation": "评价", "confidence": 0.7},
            {"src": "鸵鸟电台", "dst": "哈勃望远镜", "relation": "播报", "confidence": 0.8},
            {"src": "鸵鸟电台", "dst": "挑战者号", "relation": "提及", "confidence": 0.8},
            {"src": "鸵鸟电台", "dst": "太阳系", "relation": "提及", "confidence": 0.7},
            {"src": "斯普特尼克", "dst": "大气层", "relation": "梦想飞出", "confidence": 0.8},
            {"src": "斯普特尼克", "dst": "迪斯科球", "relation": "想成为", "confidence": 0.8},
            {"src": "贝克特", "dst": "斯普特尼克", "relation": "称赞", "confidence": 0.8},
            {"src": "杰洛", "dst": "斯普特尼克", "relation": "劝阻", "confidence": 0.7},
            {"src": "护士", "dst": "斯普特尼克", "relation": "提醒", "confidence": 0.7},
            {"src": "小目标、大目标", "dst": "太阳系", "relation": "提及", "confidence": 0.7},
        ],
    },
    # 18) 艾斯黛乐愿望收藏柜 · 克浦斯故事与航天基地 · 派对花絮问冷周六
    "b2e8d25ba30d72e4": {
        "entities": [
            {"name": "艾斯黛乐", "type": "角色", "aliases": []},
            {"name": "愿望收藏柜", "type": "物品", "aliases": []},
            {"name": "克里姆林宫", "type": "地点", "aliases": []},
            {"name": "克浦斯", "type": "角色", "aliases": []},
            {"name": "金属外壳", "type": "物品", "aliases": []},
            {"name": "航天基地", "type": "地点", "aliases": []},
            {"name": "南半球", "type": "地点", "aliases": []},
            {"name": "派对花絮", "type": "事件", "aliases": []},
            {"name": "冷周六", "type": "角色", "aliases": ["冷周六小姐"]},
        ],
        "relations": [
            {"src": "艾斯黛乐", "dst": "愿望收藏柜", "relation": "拥有", "confidence": 0.8},
            {"src": "愿望收藏柜", "dst": "克里姆林宫", "relation": "关联", "confidence": 0.7},
            {"src": "克浦斯", "dst": "金属外壳", "relation": "拥有", "confidence": 0.8},
            {"src": "克浦斯", "dst": "航天基地", "relation": "回到", "confidence": 0.8},
            {"src": "克浦斯", "dst": "南半球", "relation": "提及", "confidence": 0.7},
            {"src": "派对花絮", "dst": "冷周六", "relation": "提及", "confidence": 0.8},
        ],
    },
    # 19) 魔精观赏会 · 如何猎捕UFO与巴克·斯塔尔顿 · 惊险旅程传单路线
    "77b3ed229a469c12": {
        "entities": [
            {"name": "魔精观赏会", "type": "事件", "aliases": []},
            {"name": "魔精", "type": "角色", "aliases": []},
            {"name": "德克萨斯", "type": "地点", "aliases": []},
            {"name": "农场", "type": "地点", "aliases": []},
            {"name": "嘉年华", "type": "事件", "aliases": []},
            {"name": "UFO猎人", "type": "角色", "aliases": []},
            {"name": "如何猎捕UFO", "type": "物品", "aliases": []},
            {"name": "巴克·斯塔尔顿", "type": "角色", "aliases": []},
            {"name": "牛仔", "type": "角色", "aliases": []},
            {"name": "外星人", "type": "角色", "aliases": []},
            {"name": "UFO", "type": "物品", "aliases": []},
            {"name": "雷达", "type": "物品", "aliases": []},
            {"name": "牛仔帽", "type": "物品", "aliases": []},
            {"name": "绳索", "type": "物品", "aliases": []},
            {"name": "德州口哨", "type": "物品", "aliases": []},
            {"name": "摩斯电码", "type": "概念", "aliases": []},
            {"name": "惊险旅程", "type": "事件", "aliases": []},
            {"name": "传单", "type": "物品", "aliases": []},
            {"name": "老河谷", "type": "地点", "aliases": []},
            {"name": "幽灵牛仔", "type": "角色", "aliases": []},
            {"name": "哈德利油田", "type": "地点", "aliases": []},
            {"name": "大个儿亨利", "type": "物品", "aliases": ['"大个儿亨利"']},
            {"name": "弯钩杀手", "type": "角色", "aliases": ['"弯钩杀手"']},
            {"name": "地球战士", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "魔精观赏会", "dst": "魔精", "relation": "展示", "confidence": 0.8},
            {"src": "魔精观赏会", "dst": "农场", "relation": "位于", "confidence": 0.8},
            {"src": "魔精观赏会", "dst": "嘉年华", "relation": "属于", "confidence": 0.7},
            {"src": "巴克·斯塔尔顿", "dst": "如何猎捕UFO", "relation": "著作", "confidence": 0.9},
            {"src": "巴克·斯塔尔顿", "dst": "UFO猎人", "relation": "是", "confidence": 0.9},
            {"src": "如何猎捕UFO", "dst": "UFO", "relation": "关于", "confidence": 0.9},
            {"src": "如何猎捕UFO", "dst": "外星人", "relation": "关于", "confidence": 0.8},
            {"src": "如何猎捕UFO", "dst": "德州口哨", "relation": "提及", "confidence": 0.7},
            {"src": "惊险旅程", "dst": "传单", "relation": "关于", "confidence": 0.8},
            {"src": "传单", "dst": "老河谷", "relation": "路线经", "confidence": 0.8},
            {"src": "传单", "dst": "哈德利油田", "relation": "路线经", "confidence": 0.8},
            {"src": "传单", "dst": "大个儿亨利", "relation": "路线经", "confidence": 0.8},
            {"src": "老河谷", "dst": "幽灵牛仔", "relation": "出没", "confidence": 0.8},
            {"src": "弯钩杀手", "dst": "大个儿亨利", "relation": "作案于", "confidence": 0.8},
            {"src": "牛仔", "dst": "地球战士", "relation": "成为", "confidence": 0.7},
            {"src": "UFO猎人", "dst": "UFO", "relation": "猎捕", "confidence": 0.8},
        ],
    },
    # 20) 老邮差与老妪翻照片 · 工装男人等蓝眼女人 · 挂坠盒物归奥尔加
    "9cb33ce843123972": {
        "entities": [
            {"name": "老邮差", "type": "角色", "aliases": []},
            {"name": "伏特加", "type": "物品", "aliases": []},
            {"name": "老妪", "type": "角色", "aliases": []},
            {"name": "照片", "type": "物品", "aliases": []},
            {"name": "居民楼", "type": "地点", "aliases": []},
            {"name": "工装男人", "type": "角色", "aliases": ["工装的男人"]},
            {"name": "小酒馆", "type": "地点", "aliases": []},
            {"name": "贝加尔湖", "type": "地点", "aliases": []},
            {"name": "神", "type": "概念", "aliases": []},
            {"name": "挂坠盒", "type": "物品", "aliases": []},
            {"name": "石头记住了新的声音", "type": "事件", "aliases": []},
            {"name": "奥尔加", "type": "角色", "aliases": ["奥尔加女士"]},
            {"name": "金属链", "type": "物品", "aliases": []},
            {"name": "居民区", "type": "地点", "aliases": []},
            {"name": "烧伤", "type": "概念", "aliases": []},
            {"name": "黄金", "type": "物品", "aliases": []},
            {"name": "原野", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "老妪", "dst": "照片", "relation": "翻看", "confidence": 0.8},
            {"src": "工装男人", "dst": "贝加尔湖", "relation": "提及", "confidence": 0.7},
            {"src": "工装男人", "dst": "神", "relation": "提及", "confidence": 0.7},
            {"src": "工装男人", "dst": "烧伤", "relation": "有", "confidence": 0.8},
            {"src": "工装男人", "dst": "原野", "relation": "前往", "confidence": 0.8},
            {"src": "工装男人", "dst": "黄金", "relation": "被许诺", "confidence": 0.7},
            {"src": "挂坠盒", "dst": "照片", "relation": "内含", "confidence": 0.8},
            {"src": "奥尔加", "dst": "挂坠盒", "relation": "收回", "confidence": 0.8},
            {"src": "石头记住了新的声音", "dst": "挂坠盒", "relation": "涉及", "confidence": 0.7},
            {"src": "工装男人", "dst": "小酒馆", "relation": "出现于", "confidence": 0.8},
            {"src": "老邮差", "dst": "小酒馆", "relation": "出现于", "confidence": 0.7},
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
    print(f"[apply-missing-p16] 写入 {len(RESULTS)} 条，NOOP +{len(NOOP_ADD)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
