# -*- coding: utf-8 -*-
"""未抽取剧情块补抽 · 第 28 批（backfill2 batch_18，20 块，含 2 个重复 hash）。

用法：
  python scripts/apply_missing_p28.py            # 预演（悬空+落地自检）
  python scripts/apply_missing_p28.py --apply    # 写盘
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

# 本批 20 块均为含剧情的论坛/对白/文献页，无纯数值/UI 页 → 无 NOOP。
# 370ac7dbfeab3499、b7de952c7bc9eded 各重复一次，按唯一 hash 写入即可。
NOOP_ADD: list[str] = []

RESULTS: dict[str, dict] = {
    # 1) 电影《略知一二》选角对白 · 夜巡特遣管理局与诸导演
    "8b306e1d493afe83": {
        "entities": [
            {"name": "警官小姐", "type": "角色", "aliases": []},
            {"name": "职业人小姐", "type": "角色", "aliases": []},
            {"name": "夜巡特遣管理局", "type": "组织", "aliases": []},
            {"name": "略知一二", "type": "物品", "aliases": ["《略知一二》"]},
            {"name": "雷森姆小姐", "type": "角色", "aliases": []},
            {"name": "捷人小姐", "type": "角色", "aliases": []},
            {"name": "芬琳士多导演", "type": "角色", "aliases": []},
            {"name": "菲林什多导演", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "夜巡特遣管理局", "dst": "略知一二", "relation": "参与拍摄", "confidence": 0.7},
            {"src": "雷森姆小姐", "dst": "职业人小姐", "relation": "提及", "confidence": 0.7},
            {"src": "捷人小姐", "dst": "菲林什多导演", "relation": "寻求认可", "confidence": 0.7},
        ],
    },
    # 2) 片场对话 · 李月、投资人与剧本
    "27196391132e736d": {
        "entities": [
            {"name": "李月", "type": "角色", "aliases": []},
            {"name": "投资人", "type": "角色", "aliases": []},
            {"name": "香港", "type": "地点", "aliases": []},
            {"name": "剧本", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "投资人", "dst": "剧本", "relation": "反对修改", "confidence": 0.7},
        ],
    },
    # 3) 唐人街拍戏闹剧 · 强梁神兽、夜群特遣晚礼局与结界
    "a93b1c52a8da4b9c": {
        "entities": [
            {"name": "强梁", "type": "角色", "aliases": ["强梁神兽", "显道兽强梁"]},
            {"name": "险道兽", "type": "概念", "aliases": []},
            {"name": "十二镇子", "type": "概念", "aliases": ["十二阵子"]},
            {"name": "老周", "type": "角色", "aliases": []},
            {"name": "唐人街", "type": "地点", "aliases": []},
            {"name": "社会游行", "type": "事件", "aliases": []},
            {"name": "夜群特遣晚礼局", "type": "组织", "aliases": []},
            {"name": "沈威", "type": "角色", "aliases": ["强梁大霸"]},
            {"name": "警长先生", "type": "角色", "aliases": []},
            {"name": "演员小姐", "type": "角色", "aliases": []},
            {"name": "胶片", "type": "物品", "aliases": ["被诅咒的胶片"]},
            {"name": "结界", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "警长先生", "dst": "演员小姐", "relation": "制服", "confidence": 0.8},
            {"src": "沈威", "dst": "强梁大霸", "relation": "被称为", "confidence": 0.8},
            {"src": "唐人街", "dst": "社会游行", "relation": "举办", "confidence": 0.8},
            {"src": "夜群特遣晚礼局", "dst": "十二镇子", "relation": "关联", "confidence": 0.7},
            {"src": "胶片", "dst": "结界", "relation": "关联", "confidence": 0.7},
        ],
    },
    # 4) 胶片结界崩溃 · 三眼归巢与邪朔
    "9a26af67485916e0": {
        "entities": [
            {"name": "胶片", "type": "物品", "aliases": ["被诅咒的胶片"]},
            {"name": "结界", "type": "概念", "aliases": []},
            {"name": "雷瑟姆小姐", "type": "角色", "aliases": []},
            {"name": "警长", "type": "角色", "aliases": []},
            {"name": "神秘学藏品管理部", "type": "组织", "aliases": []},
            {"name": "限制术士", "type": "角色", "aliases": []},
            {"name": "奇心小姐", "type": "角色", "aliases": []},
            {"name": "三眼归巢", "type": "概念", "aliases": []},
            {"name": "邪朔", "type": "概念", "aliases": []},
            {"name": "丽小姐", "type": "角色", "aliases": []},
            {"name": "洪先生", "type": "角色", "aliases": []},
            {"name": "行政大厅", "type": "地点", "aliases": []},
            {"name": "魂灵", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "警长", "dst": "雷瑟姆小姐", "relation": "调查", "confidence": 0.8},
            {"src": "神秘学藏品管理部", "dst": "限制术士", "relation": "交给", "confidence": 0.7},
            {"src": "三眼归巢", "dst": "洪先生", "relation": "影响", "confidence": 0.8},
            {"src": "魂灵", "dst": "洪先生", "relation": "侵入", "confidence": 0.7},
            {"src": "洪先生", "dst": "行政大厅", "relation": "发狂于", "confidence": 0.7},
            {"src": "邪朔", "dst": "三眼归巢", "relation": "关联", "confidence": 0.7},
        ],
    },
    # 5) 唐人街杂货店疑云 · 神婆与事物所
    "cd423431a4dfad0d": {
        "entities": [
            {"name": "同僚", "type": "角色", "aliases": []},
            {"name": "导演", "type": "角色", "aliases": []},
            {"name": "小说", "type": "物品", "aliases": []},
            {"name": "战争", "type": "概念", "aliases": []},
            {"name": "杂货店", "type": "地点", "aliases": []},
            {"name": "建峰", "type": "角色", "aliases": []},
            {"name": "姥姥", "type": "角色", "aliases": []},
            {"name": "中医", "type": "角色", "aliases": []},
            {"name": "马仔", "type": "角色", "aliases": []},
            {"name": "阿妈", "type": "角色", "aliases": []},
            {"name": "阿婆", "type": "角色", "aliases": []},
            {"name": "良媒", "type": "角色", "aliases": []},
            {"name": "神婆", "type": "角色", "aliases": []},
            {"name": "事物所", "type": "组织", "aliases": []},
            {"name": "唐人街", "type": "地点", "aliases": []},
            {"name": "卡片", "type": "物品", "aliases": []},
            {"name": "案件", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "姥姥", "dst": "中医", "relation": "就医", "confidence": 0.7},
            {"src": "良媒", "dst": "案件", "relation": "询问", "confidence": 0.7},
            {"src": "神婆", "dst": "事物所", "relation": "来自", "confidence": 0.7},
            {"src": "神婆", "dst": "唐人街", "relation": "抵达", "confidence": 0.7},
        ],
    },
    # 6) 无线电留言板 · 哑谜化现象、燕鸥迁徙与宇宙主义者（含叙事无线电记录）
    "ae2ceeb34f1e840d": {
        "entities": [
            {"name": "哑谜化现象", "type": "现象", "aliases": []},
            {"name": "西蒙娜", "type": "角色", "aliases": []},
            {"name": "愿望收藏柜", "type": "物品", "aliases": []},
            {"name": "克浦斯", "type": "角色", "aliases": []},
            {"name": "公共无线电使用记录", "type": "物品", "aliases": []},
            {"name": "天鹅湖", "type": "概念", "aliases": []},
            {"name": "异常极光", "type": "现象", "aliases": []},
            {"name": "燕鸥", "type": "角色", "aliases": []},
            {"name": "普列谢茨克", "type": "角色", "aliases": []},
            {"name": "米尔内", "type": "地点", "aliases": []},
            {"name": "宇宙主义者", "type": "角色", "aliases": []},
            {"name": "奇遇的预感", "type": "事件", "aliases": []},
        ],
        "relations": [
            {"src": "普列谢茨克", "dst": "公共无线电使用记录", "relation": "管理", "confidence": 0.7},
            {"src": "米尔内", "dst": "宇宙主义者", "relation": "关联", "confidence": 0.7},
        ],
    },
    # 7) 论文摘要 · 洛伦兹蝴蝶、重塑之手、暴雨环境
    "27a10ea6e3ad7f2a": {
        "entities": [
            {"name": "洛伦兹蝴蝶", "type": "角色", "aliases": []},
            {"name": "重塑之手", "type": "组织", "aliases": []},
            {"name": "司辰", "type": "角色", "aliases": []},
            {"name": "暴雨", "type": "现象", "aliases": ["“暴雨”"]},
            {"name": "混沌", "type": "概念", "aliases": ["“混沌”"]},
            {"name": "灵性", "type": "概念", "aliases": ["“灵性”"]},
            {"name": "非对称核素R", "type": "概念", "aliases": []},
            {"name": "免疫咒语", "type": "概念", "aliases": []},
            {"name": "空间望远镜", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "重塑之手", "dst": "司辰", "relation": "上报", "confidence": 0.7},
        ],
    },
    # 8) 论坛约翰之争 · 医疗组、理论物理组与科算中心
    "685abf6514d11d9f": {
        "entities": [
            {"name": "约翰", "type": "角色", "aliases": []},
            {"name": "医疗组", "type": "组织", "aliases": []},
            {"name": "理论物理组", "type": "组织", "aliases": []},
            {"name": "阿德勒", "type": "角色", "aliases": []},
            {"name": "拉普拉斯", "type": "地点", "aliases": []},
            {"name": "科算中心", "type": "组织", "aliases": []},
            {"name": "露西", "type": "角色", "aliases": []},
            {"name": "X", "type": "角色", "aliases": []},
            {"name": "理线学", "type": "概念", "aliases": []},
            {"name": "乌尔里希", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "约翰", "dst": "医疗组", "relation": "属于", "confidence": 0.7},
            {"src": "约翰", "dst": "理论物理组", "relation": "属于", "confidence": 0.7},
            {"src": "阿德勒", "dst": "理论物理组", "relation": "属于", "confidence": 0.7},
            {"src": "科算中心", "dst": "约翰", "relation": "拥有", "confidence": 0.7},
        ],
    },
    # 9) 赌徒独白与科马拉监狱治疗清单
    "2edd55de64618aa8": {
        "entities": [
            {"name": "骰子", "type": "物品", "aliases": []},
            {"name": "赌徒", "type": "角色", "aliases": []},
            {"name": "巫师", "type": "角色", "aliases": []},
            {"name": "数学家", "type": "角色", "aliases": []},
            {"name": "恶魔", "type": "角色", "aliases": []},
            {"name": "指挥官", "type": "角色", "aliases": []},
            {"name": "科马拉监狱治疗清单第303目", "type": "物品", "aliases": ["《科马拉监狱治疗清单第303目》"]},
            {"name": "氯丙嗪", "type": "物品", "aliases": []},
            {"name": "沙利度胺", "type": "物品", "aliases": []},
            {"name": "佛罗那", "type": "物品", "aliases": []},
            {"name": "暗色带编织·卷五", "type": "物品", "aliases": []},
            {"name": "占星者", "type": "角色", "aliases": []},
            {"name": "剪报", "type": "物品", "aliases": []},
            {"name": "冰锥", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "恶魔", "dst": "骰子", "relation": "关联", "confidence": 0.7},
            {"src": "科马拉监狱治疗清单第303目", "dst": "氯丙嗪", "relation": "配发", "confidence": 0.8},
            {"src": "科马拉监狱治疗清单第303目", "dst": "沙利度胺", "relation": "配发", "confidence": 0.8},
            {"src": "科马拉监狱治疗清单第303目", "dst": "佛罗那", "relation": "配发", "confidence": 0.8},
            {"src": "暗色带编织·卷五", "dst": "占星者", "relation": "记载", "confidence": 0.7},
            {"src": "剪报", "dst": "冰锥", "relation": "提及", "confidence": 0.7},
        ],
    },
    # 10) 河滩异变 · 酒水、猛琴与失踪胡商
    "370ac7dbfeab3499": {
        "entities": [
            {"name": "酒水", "type": "物品", "aliases": []},
            {"name": "露出", "type": "概念", "aliases": []},
            {"name": "浅滩", "type": "地点", "aliases": []},
            {"name": "河滩", "type": "地点", "aliases": []},
            {"name": "竹藤", "type": "物品", "aliases": []},
            {"name": "猛琴", "type": "角色", "aliases": []},
            {"name": "琴类", "type": "概念", "aliases": []},
            {"name": "年轻女子", "type": "角色", "aliases": []},
            {"name": "胡商", "type": "角色", "aliases": []},
            {"name": "娘子", "type": "角色", "aliases": []},
            {"name": "茶水", "type": "物品", "aliases": []},
            {"name": "官府", "type": "组织", "aliases": []},
            {"name": "知词", "type": "地点", "aliases": []},
            {"name": "马车", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "酒水", "dst": "露出", "relation": "致使变异", "confidence": 0.8},
            {"src": "年轻女子", "dst": "猛琴", "relation": "遭遇", "confidence": 0.8},
            {"src": "娘子", "dst": "茶水", "relation": "提供", "confidence": 0.7},
        ],
    },
    # 11) 乡邻宴客 · 竹叶花苗、纸马与法曹姬儿
    "b7de952c7bc9eded": {
        "entities": [
            {"name": "李正输国", "type": "角色", "aliases": []},
            {"name": "竹叶花苗", "type": "物品", "aliases": []},
            {"name": "酒", "type": "物品", "aliases": []},
            {"name": "结彩", "type": "物品", "aliases": []},
            {"name": "纸马", "type": "物品", "aliases": ["纸马刹"]},
            {"name": "法曹", "type": "角色", "aliases": []},
            {"name": "姬儿", "type": "角色", "aliases": []},
            {"name": "红人娘子", "type": "角色", "aliases": []},
            {"name": "主人家", "type": "角色", "aliases": []},
            {"name": "执词", "type": "物品", "aliases": []},
            {"name": "厨业", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "法曹", "dst": "姬儿", "relation": "拥有", "confidence": 0.7},
        ],
    },
    # 12) 奇星小姐执念 · 菲律师多、齐心小姐与 C07
    "bd26a4e4d68ff986": {
        "entities": [
            {"name": "奇星小姐", "type": "角色", "aliases": []},
            {"name": "神秘警探菲林七", "type": "角色", "aliases": []},
            {"name": "菲律师多女士", "type": "角色", "aliases": []},
            {"name": "菲律师多导演", "type": "角色", "aliases": []},
            {"name": "齐心小姐", "type": "角色", "aliases": []},
            {"name": "社会游行", "type": "事件", "aliases": []},
            {"name": "何日君小姐", "type": "角色", "aliases": []},
            {"name": "Kway", "type": "角色", "aliases": []},
            {"name": "C07", "type": "概念", "aliases": []},
            {"name": "摄像机", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "奇星小姐", "dst": "神秘警探菲林七", "relation": "耿耿于怀", "confidence": 0.8},
            {"src": "齐心小姐", "dst": "菲律师多女士", "relation": "认定", "confidence": 0.7},
            {"src": "菲律师多女士", "dst": "菲律师多导演", "relation": "不同于", "confidence": 0.8},
            {"src": "奇星小姐", "dst": "社会游行", "relation": "策划", "confidence": 0.8},
        ],
    },
    # 13) Teresa 与胶片 · 何日君小姐与职业人小姐
    "2431e9e1a289dd01": {
        "entities": [
            {"name": "何日君小姐", "type": "角色", "aliases": []},
            {"name": "拉桃花树", "type": "物品", "aliases": []},
            {"name": "职业人小姐", "type": "角色", "aliases": []},
            {"name": "胶片", "type": "物品", "aliases": []},
            {"name": "Teresa", "type": "角色", "aliases": []},
            {"name": "警长先生", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "职业人小姐", "dst": "Teresa", "relation": "轻视", "confidence": 0.7},
        ],
    },
    # 14) CO7 系列风波 · 其心先生、警察 C-07 与创作家
    "9fec8ed0f49c5631": {
        "entities": [
            {"name": "其心先生", "type": "角色", "aliases": []},
            {"name": "制作人", "type": "角色", "aliases": []},
            {"name": "CO7", "type": "概念", "aliases": []},
            {"name": "洛杉矶", "type": "地点", "aliases": []},
            {"name": "警察C-07", "type": "角色", "aliases": ["C-07"]},
            {"name": "创作家", "type": "角色", "aliases": []},
            {"name": "医生", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "其心先生", "dst": "制作人", "relation": "冲突", "confidence": 0.7},
            {"src": "其心先生", "dst": "CO7", "relation": "关联", "confidence": 0.7},
        ],
    },
    # 15) 王先生冤案 · Laplace 医疗中心与农场
    "c166dce37ed2e554": {
        "entities": [
            {"name": "医生", "type": "角色", "aliases": []},
            {"name": "农场", "type": "地点", "aliases": []},
            {"name": "Laplace医疗中心", "type": "组织", "aliases": []},
            {"name": "洛西拉斯", "type": "地点", "aliases": []},
            {"name": "警察", "type": "角色", "aliases": []},
            {"name": "王先生", "type": "角色", "aliases": []},
            {"name": "社群", "type": "概念", "aliases": []},
            {"name": "案件", "type": "概念", "aliases": []},
            {"name": "证据", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "Laplace医疗中心", "dst": "医生", "relation": "派遣", "confidence": 0.8},
            {"src": "王先生", "dst": "社群", "relation": "深爱", "confidence": 0.7},
            {"src": "案件", "dst": "证据", "relation": "需要", "confidence": 0.7},
        ],
    },
    # 16) 祝县游玩攻略论坛 · UTTU、古城墙与康乐步行街
    "f53c136550e5306a": {
        "entities": [
            {"name": "祝县", "type": "地点", "aliases": []},
            {"name": "稻花香", "type": "角色", "aliases": []},
            {"name": "甜点铺", "type": "地点", "aliases": []},
            {"name": "钞关", "type": "地点", "aliases": []},
            {"name": "蓝色忧郁", "type": "角色", "aliases": []},
            {"name": "UTTU", "type": "组织", "aliases": []},
            {"name": "古城墙", "type": "地点", "aliases": []},
            {"name": "shqj3744", "type": "角色", "aliases": []},
            {"name": "康乐步行街", "type": "地点", "aliases": []},
            {"name": "飞奔的猪猪", "type": "角色", "aliases": []},
            {"name": "小小草", "type": "角色", "aliases": []},
            {"name": "和风", "type": "概念", "aliases": []},
            {"name": "神秘术", "type": "概念", "aliases": []},
            {"name": "网速太慢了", "type": "角色", "aliases": []},
            {"name": "人民西路", "type": "地点", "aliases": []},
            {"name": "风水", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "稻花香", "dst": "甜点铺", "relation": "经营", "confidence": 0.7},
            {"src": "蓝色忧郁", "dst": "UTTU", "relation": "提及", "confidence": 0.7},
            {"src": "蓝色忧郁", "dst": "古城墙", "relation": "提及", "confidence": 0.7},
            {"src": "飞奔的猪猪", "dst": "康乐步行街", "relation": "提及", "confidence": 0.7},
            {"src": "小小草", "dst": "和风", "relation": "询问", "confidence": 0.7},
            {"src": "网速太慢了", "dst": "人民西路", "relation": "提及", "confidence": 0.7},
            {"src": "祝县", "dst": "古城墙", "relation": "拥有", "confidence": 0.7},
            {"src": "祝县", "dst": "康乐步行街", "relation": "拥有", "confidence": 0.7},
        ],
    },
    # 17) 高跷马招募论坛 · 气、踩马队与鲍三娘
    "90bd9ddd7d1114b2": {
        "entities": [
            {"name": "气", "type": "概念", "aliases": ["“气”"]},
            {"name": "驿路梅花", "type": "角色", "aliases": []},
            {"name": "叛逆的橘子", "type": "角色", "aliases": []},
            {"name": "阳光", "type": "概念", "aliases": []},
            {"name": "火焰", "type": "概念", "aliases": []},
            {"name": "电流", "type": "概念", "aliases": []},
            {"name": "高跷马", "type": "组织", "aliases": []},
            {"name": "望梅村", "type": "地点", "aliases": []},
            {"name": "望梅村龙哥", "type": "角色", "aliases": []},
            {"name": "踩马队", "type": "组织", "aliases": []},
            {"name": "白马战将", "type": "角色", "aliases": []},
            {"name": "锣鼓", "type": "物品", "aliases": []},
            {"name": "唢呐", "type": "物品", "aliases": []},
            {"name": "海阔天空", "type": "角色", "aliases": []},
            {"name": "红马", "type": "角色", "aliases": []},
            {"name": "盆景批发1847", "type": "角色", "aliases": []},
            {"name": "鲍三娘", "type": "角色", "aliases": []},
            {"name": "春暖花开", "type": "角色", "aliases": []},
            {"name": "春节", "type": "时间", "aliases": []},
        ],
        "relations": [
            {"src": "驿路梅花", "dst": "气", "relation": "撰写", "confidence": 0.7},
            {"src": "阳光", "dst": "气", "relation": "呈现为", "confidence": 0.7},
            {"src": "火焰", "dst": "气", "relation": "呈现为", "confidence": 0.7},
            {"src": "电流", "dst": "气", "relation": "呈现为", "confidence": 0.7},
            {"src": "望梅村龙哥", "dst": "高跷马", "relation": "招募", "confidence": 0.8},
            {"src": "踩马队", "dst": "望梅村", "relation": "位于", "confidence": 0.7},
            {"src": "踩马队", "dst": "白马战将", "relation": "招募", "confidence": 0.7},
            {"src": "海阔天空", "dst": "白马战将", "relation": "询问", "confidence": 0.7},
            {"src": "红马", "dst": "白马战将", "relation": "争吵", "confidence": 0.7},
            {"src": "盆景批发1847", "dst": "鲍三娘", "relation": "询问", "confidence": 0.7},
            {"src": "踩马队", "dst": "春节", "relation": "排练于", "confidence": 0.7},
        ],
    },
    # 18) 长生剑售卖论坛 · 李家园铸剑术与调气鼎（地震记录为数据页不抽）
    "8598c109c04eb421": {
        "entities": [
            {"name": "李家园", "type": "地点", "aliases": []},
            {"name": "铸剑术", "type": "概念", "aliases": []},
            {"name": "丹炉", "type": "物品", "aliases": []},
            {"name": "石胆精华", "type": "物品", "aliases": []},
            {"name": "长生剑", "type": "物品", "aliases": []},
            {"name": "气", "type": "概念", "aliases": ["“气”"]},
            {"name": "神秘学能量", "type": "概念", "aliases": []},
            {"name": "调气鼎", "type": "物品", "aliases": []},
            {"name": "上海", "type": "地点", "aliases": []},
            {"name": "雨滴", "type": "物品", "aliases": []},
            {"name": "一头小毛骡", "type": "角色", "aliases": []},
            {"name": "蓝色忧郁", "type": "角色", "aliases": []},
            {"name": "地震记录", "type": "物品", "aliases": []},
            {"name": "wa666666", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "李家园", "dst": "铸剑术", "relation": "擅长", "confidence": 0.7},
            {"src": "铸剑术", "dst": "丹炉", "relation": "使用", "confidence": 0.7},
            {"src": "铸剑术", "dst": "石胆精华", "relation": "施加", "confidence": 0.7},
            {"src": "长生剑", "dst": "气", "relation": "影响", "confidence": 0.8},
            {"src": "长生剑", "dst": "一头小毛骡", "relation": "拥有", "confidence": 0.7},
            {"src": "调气鼎", "dst": "上海", "relation": "拍卖于", "confidence": 0.7},
            {"src": "调气鼎", "dst": "雨滴", "relation": "价值", "confidence": 0.7},
            {"src": "wa666666", "dst": "地震记录", "relation": "发布", "confidence": 0.7},
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
    print(f"[apply-missing-p28] 写入 {len(RESULTS)} 条，NOOP +{len(NOOP_ADD)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
