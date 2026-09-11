# -*- coding: utf-8 -*-
"""补抽 408 块空抽取中的第 6 批（71 块，最后一批）。至此 408 块全覆盖。"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from roleplay.config import get_settings  # noqa: E402

NOOP: list[str] = []

RESULTS: dict[str, dict] = {
    "1f984b507d4d9b6a": {
        "entities": [
            {"name": "世界", "type": "概念", "aliases": ["world"]},
            {"name": "梦", "type": "概念", "aliases": ["dream", "Dream"]},
        ],
        "relations": [
            {"src": "梦", "dst": "世界", "relation": "融为一体", "confidence": 0.6},
        ],
    },
    "2bcb2a6e2cef2294": {
        "entities": [
            {"name": "吸血鬼", "type": "概念", "aliases": ["vampire", "vampires"]},
            {"name": "纯血种", "type": "概念", "aliases": ["pure-blood vampire"]},
            {"name": "吸血鬼列车", "type": "物品", "aliases": ["vampire train"]},
            {"name": "同志", "type": "概念", "aliases": ["comrades"]},
        ],
        "relations": [
            {"src": "吸血鬼列车", "dst": "吸血鬼", "relation": "载有", "confidence": 0.9},
            {"src": "纯血种", "dst": "吸血鬼", "relation": "属于", "confidence": 0.9},
        ],
    },
    "88a6060110130ad6": {
        "entities": [
            {"name": "吸血鬼", "type": "概念", "aliases": ["vampires"]},
            {"name": "故事", "type": "概念", "aliases": ["story", "tall tales"]},
            {"name": "死亡", "type": "概念", "aliases": ["death"]},
            {"name": "说书人", "type": "角色", "aliases": ["Storytellers"]},
        ],
        "relations": [
            {"src": "说书人", "dst": "故事", "relation": "讲述", "confidence": 0.9},
            {"src": "吸血鬼", "dst": "死亡", "relation": "超越", "confidence": 0.8},
        ],
    },
    "285a78bfd5ea46ce": {
        "entities": [
            {"name": "列车", "type": "物品", "aliases": ["train"]},
            {"name": "车票", "type": "物品", "aliases": ["tickets"]},
            {"name": "可预测的结局", "type": "概念", "aliases": ["predictable endings"]},
            {"name": "悲剧", "type": "概念", "aliases": ["tragic"]},
        ],
        "relations": [
            {"src": "可预测的结局", "dst": "悲剧", "relation": "通常", "confidence": 0.8},
            {"src": "列车", "dst": "车票", "relation": "需检票", "confidence": 0.9},
        ],
    },
    "12180d9db7ef5e20": {
        "entities": [
            {"name": "家庭", "type": "概念", "aliases": ["Family"]},
            {"name": "半岛", "type": "地点", "aliases": ["peninsula"]},
            {"name": "列车", "type": "物品", "aliases": ["train"]},
            {"name": "乘客", "type": "概念", "aliases": ["passengers"]},
            {"name": "新衣", "type": "物品", "aliases": ["new clothes"]},
        ],
        "relations": [
            {"src": "新衣", "dst": "家庭", "relation": "维系", "confidence": 0.8},
            {"src": "列车", "dst": "乘客", "relation": "迎来", "confidence": 0.8},
        ],
    },
    "9e0fdf3d9ffa326d": {
        "entities": [
            {"name": "岛屿", "type": "地点", "aliases": ["island"]},
            {"name": "秘术幻象", "type": "概念", "aliases": ["arcane illusion"]},
            {"name": "强力仪式", "type": "概念", "aliases": ["powerful ritual"]},
            {"name": "自然现象", "type": "概念",
             "aliases": ["naturally occurring phenomenon"]},
        ],
        "relations": [
            {"src": "秘术幻象", "dst": "岛屿", "relation": "遮蔽", "confidence": 0.8},
            {"src": "强力仪式", "dst": "岛屿", "relation": "可能遮蔽", "confidence": 0.7},
            {"src": "自然现象", "dst": "岛屿", "relation": "可能成因", "confidence": 0.7},
        ],
    },
    "99a52835fb1b8685": {
        "entities": [
            {"name": "飞行器", "type": "物品", "aliases": ["this beauty", "craft"]},
            {"name": "发射台", "type": "地点", "aliases": ["platform"]},
            {"name": "海盗", "type": "角色", "aliases": ["pirate"]},
            {"name": "摇滚明星", "type": "角色", "aliases": ["rock star"]},
        ],
        "relations": [
            {"src": "飞行器", "dst": "发射台", "relation": "起飞", "confidence": 0.9},
            {"src": "海盗", "dst": "摇滚明星", "relation": "无法匹敌", "confidence": 0.7},
        ],
    },
    "4c23f7d1c5ce1310": {
        "entities": [
            {"name": "家庭肖像", "type": "物品", "aliases": ["family portrait"]},
            {"name": "画家", "type": "角色", "aliases": ["painter"]},
            {"name": "兄弟", "type": "角色", "aliases": ["brother"]},
        ],
        "relations": [
            {"src": "画家", "dst": "家庭肖像", "relation": "绘制", "confidence": 0.9},
        ],
    },
    "bfc6cba28b925839": {
        "entities": [
            {"name": "咪咪", "type": "角色", "aliases": []},
            {"name": "无感缺失", "type": "概念", "aliases": []},
            {"name": "树", "type": "物品", "aliases": []},
            {"name": "论坛", "type": "组织", "aliases": []},
            {"name": "鱼池", "type": "地点", "aliases": []},
            {"name": "末日", "type": "概念", "aliases": []},
            {"name": "联络", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "树", "dst": "咪咪", "relation": "封入", "confidence": 0.9},
            {"src": "咪咪", "dst": "无感缺失", "relation": "患有", "confidence": 0.8},
            {"src": "论坛", "dst": "联络", "relation": "用于", "confidence": 0.9},
            {"src": "末日", "dst": "鱼池", "relation": "未发生", "confidence": 0.7},
        ],
    },
    "a0fa95e7f4af61dd": {
        "entities": [
            {"name": "家族诅咒", "type": "概念", "aliases": ["familial curse"]},
            {"name": "河流", "type": "概念", "aliases": ["stream"]},
            {"name": "行踪", "type": "概念", "aliases": ["where she has been"]},
        ],
        "relations": [
            {"src": "家族诅咒", "dst": "行踪", "relation": "可追踪", "confidence": 0.8},
            {"src": "河流", "dst": "行踪", "relation": "观察", "confidence": 0.8},
        ],
    },
    "30522800e3b0ae5e": {
        "entities": [
            {"name": "苏努纳", "type": "角色", "aliases": ["Sununa"]},
            {"name": "生意", "type": "概念", "aliases": ["business"]},
            {"name": "投资", "type": "概念", "aliases": ["investment"]},
        ],
        "relations": [
            {"src": "生意", "dst": "投资", "relation": "收回", "confidence": 0.8},
            {"src": "苏努纳", "dst": "生意", "relation": "经营", "confidence": 0.8},
        ],
    },
    "f68bcc05fe99ae14": {
        "entities": [
            {"name": "诗歌", "type": "概念", "aliases": ["poetry"]},
            {"name": "金预言", "type": "概念", "aliases": ["Golden Prophecy"]},
            {"name": "诗人", "type": "角色", "aliases": ["poets"]},
        ],
        "relations": [
            {"src": "诗人", "dst": "诗歌", "relation": "创作", "confidence": 0.9},
            {"src": "诗歌", "dst": "金预言", "relation": "受制", "confidence": 0.8},
        ],
    },
    "24a9c6b54ca347c9": {
        "entities": [
            {"name": "回响石", "type": "物品", "aliases": ["echo stones"]},
            {"name": "能量分布", "type": "概念", "aliases": ["energy distribution"]},
            {"name": "感知机制", "type": "概念", "aliases": ["sense mechanisms"]},
            {"name": "扰动", "type": "概念", "aliases": ["disturbance"]},
            {"name": "实验", "type": "事件", "aliases": ["experimentation"]},
            {"name": "风险", "type": "概念", "aliases": ["risk"]},
        ],
        "relations": [
            {"src": "能量分布", "dst": "回响石", "relation": "维持平衡", "confidence": 0.9},
            {"src": "感知机制", "dst": "扰动", "relation": "反应", "confidence": 0.9},
            {"src": "实验", "dst": "风险", "relation": "伴随", "confidence": 0.9},
        ],
    },
    "258de1001e5d6593": {
        "entities": [
            {"name": "道路", "type": "概念", "aliases": ["Roads"]},
            {"name": "工程核心", "type": "组织", "aliases": ["engineering core"]},
            {"name": "城市重建", "type": "事件",
             "aliases": ["reconstruction of a city"]},
            {"name": "城市", "type": "地点", "aliases": ["city"]},
        ],
        "relations": [
            {"src": "道路", "dst": "城市", "relation": "构成骨架", "confidence": 0.9},
            {"src": "城市重建", "dst": "城市", "relation": "分阶段", "confidence": 0.9},
            {"src": "工程核心", "dst": "城市", "relation": "依序震动", "confidence": 0.8},
        ],
    },
    "0cbd6d84aa8acacf": {
        "entities": [
            {"name": "时间异常", "type": "事件", "aliases": ["temporal anomaly"]},
            {"name": "1999年12月31日", "type": "时间",
             "aliases": ["the 31st of December, 1999"]},
            {"name": "大规模幻觉", "type": "事件", "aliases": ["mass illusions"]},
            {"name": "逆降雨", "type": "事件", "aliases": ["inverted rainfall"]},
            {"name": "时空倒转", "type": "概念", "aliases": ["spatial and temporal reversion"]},
            {"name": "时空连续性", "type": "概念", "aliases": ["time-space continuity"]},
        ],
        "relations": [
            {"src": "时间异常", "dst": "1999年12月31日", "relation": "起始于",
             "confidence": 0.9},
            {"src": "大规模幻觉", "dst": "时间异常", "relation": "属于", "confidence": 0.9},
            {"src": "逆降雨", "dst": "时空倒转", "relation": "导致", "confidence": 0.9},
            {"src": "时间异常", "dst": "时空连续性", "relation": "不可逆破坏",
             "confidence": 0.9},
        ],
    },
    "636aa309609d89ac": {
        "entities": [
            {"name": "建筑", "type": "地点", "aliases": ["building"]},
            {"name": "主厅", "type": "地点", "aliases": ["main hall"]},
            {"name": "基本形状", "type": "概念",
             "aliases": ["basic shapes", "Circles, rectangles, triangles"]},
            {"name": "等边三角形", "type": "概念", "aliases": ["equilateral triangles"]},
            {"name": "筒形拱顶", "type": "概念", "aliases": ["Straight line vaults"]},
        ],
        "relations": [
            {"src": "基本形状", "dst": "建筑", "relation": "被强调", "confidence": 0.9},
            {"src": "主厅", "dst": "基本形状", "relation": "凸显", "confidence": 0.9},
            {"src": "基本形状", "dst": "等边三角形", "relation": "包含", "confidence": 0.9},
            {"src": "筒形拱顶", "dst": "建筑", "relation": "采用", "confidence": 0.8},
        ],
    },
    "fe2f53f96b5a212e": {
        "entities": [
            {"name": "冰塔", "type": "地点", "aliases": ["ice towers", "towers"]},
            {"name": "岩浆", "type": "概念", "aliases": ["magma"]},
            {"name": "地壳裂缝", "type": "概念",
             "aliases": ["narrow cracks in the crust"]},
            {"name": "火山", "type": "地点", "aliases": ["volcanoes", "volcano"]},
            {"name": "微生物", "type": "概念", "aliases": ["microbes"]},
        ],
        "relations": [
            {"src": "岩浆", "dst": "地壳裂缝", "relation": "逸出热气", "confidence": 0.9},
            {"src": "冰塔", "dst": "火山", "relation": "常见于", "confidence": 0.9},
            {"src": "微生物", "dst": "冰塔", "relation": "气味来源", "confidence": 0.8},
        ],
    },
    "1067bd6c4a6d7252": {
        "entities": [
            {"name": "模型", "type": "概念", "aliases": ["models"]},
            {"name": "玩具盒", "type": "物品", "aliases": ["toy box"]},
            {"name": "秘术波动", "type": "概念", "aliases": ["arcane fluctuations"]},
            {"name": "验证", "type": "事件", "aliases": ["verification"]},
        ],
        "relations": [
            {"src": "模型", "dst": "验证", "relation": "需多轮", "confidence": 0.9},
            {"src": "玩具盒", "dst": "秘术波动", "relation": "散发", "confidence": 0.9},
        ],
    },
    "0a1d08da33af38c0": {
        "entities": [
            {"name": "密码", "type": "概念", "aliases": ["Codes"]},
            {"name": "符号", "type": "概念", "aliases": ["symbols"]},
            {"name": "手稿", "type": "物品", "aliases": ["manuscripts"]},
            {"name": "白日梦邮报", "type": "组织", "aliases": ["Daydream post"]},
        ],
        "relations": [
            {"src": "密码", "dst": "符号", "relation": "重排", "confidence": 0.9},
            {"src": "手稿", "dst": "白日梦邮报", "relation": "投稿", "confidence": 0.9},
        ],
    },
    "d1f57f787f37b505": {
        "entities": [
            {"name": "学生", "type": "角色", "aliases": ["students", "children"]},
            {"name": "图书馆", "type": "地点", "aliases": ["library"]},
            {"name": "教官", "type": "角色", "aliases": ["instructors"]},
            {"name": "学校安保", "type": "组织", "aliases": ["school security"]},
            {"name": "中央瞭望塔", "type": "地点", "aliases": ["central watchtower"]},
        ],
        "relations": [
            {"src": "学生", "dst": "图书馆", "relation": "集结", "confidence": 0.9},
            {"src": "教官", "dst": "中央瞭望塔", "relation": "可能撤退", "confidence": 0.8},
            {"src": "学校安保", "dst": "中央瞭望塔", "relation": "可能撤退",
             "confidence": 0.8},
        ],
    },
    "3c6c3059a4aa6975": {
        "entities": [
            {"name": "创新", "type": "概念", "aliases": ["Innovation"]},
            {"name": "自然选择", "type": "概念", "aliases": ["natural selection"]},
            {"name": "基因突变", "type": "概念", "aliases": ["genetic mutation"]},
            {"name": "人类", "type": "概念", "aliases": ["humanity"]},
        ],
        "relations": [
            {"src": "创新", "dst": "自然选择", "relation": "类比", "confidence": 0.8},
            {"src": "基因突变", "dst": "自然选择", "relation": "慢于", "confidence": 0.8},
        ],
    },
    "2fca9be0346c9bf4": {
        "entities": [
            {"name": "访谈记录", "type": "物品", "aliases": ["interview record"]},
            {"name": "法国记录", "type": "物品", "aliases": ["French record"]},
            {"name": "模块", "type": "概念", "aliases": ["module"]},
        ],
        "relations": [
            {"src": "法国记录", "dst": "访谈记录", "relation": "关联", "confidence": 0.7},
        ],
    },
    "54301fbc2230f2fb": {
        "entities": [
            {"name": "特殊病患", "type": "概念", "aliases": ["special patients"]},
            {"name": "剂量", "type": "概念", "aliases": ["dosage"]},
            {"name": "耐药性", "type": "概念", "aliases": ["drug resistance"]},
            {"name": "兽医", "type": "角色", "aliases": ["vet"]},
        ],
        "relations": [
            {"src": "剂量", "dst": "特殊病患", "relation": "需关注", "confidence": 0.9},
            {"src": "耐药性", "dst": "特殊病患", "relation": "需关注", "confidence": 0.9},
        ],
    },
    "539c42a8a870188d": {
        "entities": [
            {"name": "项目", "type": "概念", "aliases": ["project"]},
            {"name": "盆栽中的精灵", "type": "角色", "aliases": ["sleepyhead in that pot"]},
            {"name": "月球", "type": "概念", "aliases": ["moon"]},
            {"name": "交易", "type": "概念", "aliases": ["deal"]},
        ],
        "relations": [
            {"src": "盆栽中的精灵", "dst": "项目", "relation": "提供所需",
             "confidence": 0.8},
            {"src": "交易", "dst": "盆栽中的精灵", "relation": "达成", "confidence": 0.8},
        ],
    },
    "149e20402b34afc3": {
        "entities": [
            {"name": "申请表", "type": "物品", "aliases": ["application form"]},
            {"name": "传送", "type": "概念", "aliases": ["teleport"]},
            {"name": "防护垫", "type": "物品", "aliases": ["protective sheet"]},
            {"name": "纸制品", "type": "物品", "aliases": ["paper products"]},
        ],
        "relations": [
            {"src": "传送", "dst": "纸制品", "relation": "需防护垫", "confidence": 0.9},
            {"src": "申请表", "dst": "传送", "relation": "曾被撕碎", "confidence": 0.8},
        ],
    },
    "c4c8139b984e0e1f": {
        "entities": [
            {"name": "走钢丝", "type": "概念", "aliases": ["tightrope"]},
            {"name": "当下", "type": "时间", "aliases": ["present"]},
            {"name": "幻觉说", "type": "概念", "aliases": ["all perception is illusion"]},
        ],
        "relations": [
            {"src": "走钢丝", "dst": "当下", "relation": "只感受", "confidence": 0.8},
            {"src": "幻觉说", "dst": "当下", "relation": "主张", "confidence": 0.7},
        ],
    },
    "d06872b2b88ef019": {
        "entities": [
            {"name": "武器", "type": "物品", "aliases": ["weapons"]},
            {"name": "外部来源", "type": "概念", "aliases": ["outer source"]},
            {"name": "监视", "type": "概念", "aliases": ["surveillance"]},
            {"name": "当地人", "type": "角色", "aliases": ["locals"]},
        ],
        "relations": [
            {"src": "武器", "dst": "外部来源", "relation": "来自", "confidence": 0.9},
            {"src": "监视", "dst": "当地人", "relation": "覆盖", "confidence": 0.8},
        ],
    },
    "1cf2b82d62872e89": {
        "entities": [
            {"name": "最终比赛", "type": "事件", "aliases": ["final competition"]},
            {"name": "火山口", "type": "地点", "aliases": ["mouth of the volcano"]},
            {"name": "障碍", "type": "概念", "aliases": ["obstacles"]},
            {"name": "参赛者", "type": "角色", "aliases": ["contestants"]},
            {"name": "冠军", "type": "概念", "aliases": ["champion"]},
        ],
        "relations": [
            {"src": "最终比赛", "dst": "火山口", "relation": "通往", "confidence": 0.9},
            {"src": "参赛者", "dst": "最终比赛", "relation": "参加", "confidence": 0.9},
            {"src": "障碍", "dst": "最终比赛", "relation": "天然形成", "confidence": 0.9},
        ],
    },
    "5ce9df67690863ad": {
        "entities": [
            {"name": "心智", "type": "概念", "aliases": ["mind"]},
            {"name": "古老剧本", "type": "物品", "aliases": ["ancient scripts"]},
            {"name": "物质世界", "type": "概念", "aliases": ["material world"]},
            {"name": "洞穴之影", "type": "概念", "aliases": ["flicker on a cave wall"]},
            {"name": "终极真理", "type": "概念", "aliases": ["ultimate truth"]},
        ],
        "relations": [
            {"src": "物质世界", "dst": "洞穴之影", "relation": "不过是", "confidence": 0.9},
            {"src": "终极真理", "dst": "物质世界", "relation": "被隐藏", "confidence": 0.8},
            {"src": "心智", "dst": "古老剧本", "relation": "借用台词", "confidence": 0.8},
        ],
    },
    "491ff825c6aca3ae": {
        "entities": [
            {"name": "水晶", "type": "物品", "aliases": ["crystal"]},
            {"name": "光之路", "type": "概念", "aliases": ["path of light"]},
            {"name": "命运", "type": "概念", "aliases": ["fate"]},
            {"name": "预言", "type": "概念", "aliases": ["reading", "divination"]},
        ],
        "relations": [
            {"src": "水晶", "dst": "光之路", "relation": "折射可预测", "confidence": 0.9},
            {"src": "预言", "dst": "命运", "relation": "预示", "confidence": 0.8},
        ],
    },
    "41c563c8fdf1bc82": {
        "entities": [
            {"name": "内脏现实主义", "type": "概念", "aliases": ["visceral realism"]},
            {"name": "诗歌", "type": "概念", "aliases": ["poems", "poetry"]},
            {"name": "资产阶级", "type": "概念", "aliases": ["bourgeoisie"]},
            {"name": "逻辑", "type": "概念", "aliases": ["logic"]},
        ],
        "relations": [
            {"src": "内脏现实主义", "dst": "诗歌", "relation": "关联", "confidence": 0.8},
            {"src": "逻辑", "dst": "诗歌", "relation": "扼杀新芽", "confidence": 0.8},
        ],
    },
    "55eb42837adc00b3": {
        "entities": [
            {"name": "建筑", "type": "地点", "aliases": ["buildings"]},
            {"name": "学校", "type": "地点", "aliases": ["schools"]},
            {"name": "公交车", "type": "物品", "aliases": ["buses"]},
            {"name": "诊所", "type": "地点", "aliases": ["polyclinic"]},
            {"name": "城市脉络", "type": "概念", "aliases": ["veins of the city"]},
            {"name": "城市", "type": "地点", "aliases": ["city"]},
        ],
        "relations": [
            {"src": "城市脉络", "dst": "建筑", "relation": "构成", "confidence": 0.8},
            {"src": "诊所", "dst": "城市", "relation": "遍布", "confidence": 0.8},
            {"src": "学校", "dst": "城市", "relation": "出现", "confidence": 0.8},
        ],
    },
    "abfeffcf2b642e83": {
        "entities": [
            {"name": "1999年", "type": "时间", "aliases": ["1999"]},
            {"name": "雨前的世界", "type": "概念", "aliases": ["world before the rain"]},
            {"name": "现代主义", "type": "概念", "aliases": ["Modernism"]},
            {"name": "玻璃铝合金建筑", "type": "概念",
             "aliases": ["boxes of glass and aluminum alloys"]},
            {"name": "互联网", "type": "概念", "aliases": ["internet"]},
            {"name": "加里", "type": "角色", "aliases": ["Gary"]},
        ],
        "relations": [
            {"src": "现代主义", "dst": "1999年", "relation": "建筑界主导",
             "confidence": 0.9},
            {"src": "互联网", "dst": "1999年", "relation": "已存在", "confidence": 0.8},
            {"src": "玻璃铝合金建筑", "dst": "1999年", "relation": "普遍",
             "confidence": 0.8},
        ],
    },
    "81a09a46b873beb3": {
        "entities": [
            {"name": "马丘比丘", "type": "地点", "aliases": ["Machu Picchu"]},
            {"name": "石墙", "type": "物品", "aliases": ["stones"]},
            {"name": "项目", "type": "概念", "aliases": ["project"]},
            {"name": "组织", "type": "概念", "aliases": ["organization"]},
        ],
        "relations": [
            {"src": "石墙", "dst": "马丘比丘", "relation": "属于", "confidence": 0.9},
            {"src": "项目", "dst": "组织", "relation": "关乎未来", "confidence": 0.8},
        ],
    },
    "3b9dce0ac9e64988": {
        "entities": [
            {"name": "建筑", "type": "地点", "aliases": ["building"]},
            {"name": "安全区", "type": "概念", "aliases": ["safe zone"]},
            {"name": "时间异常", "type": "事件", "aliases": ["anomaly", "temporal anomaly"]},
            {"name": "敌人", "type": "组织", "aliases": ["enemy"]},
        ],
        "relations": [
            {"src": "建筑", "dst": "安全区", "relation": "可成为", "confidence": 0.9},
            {"src": "安全区", "dst": "时间异常", "relation": "抵御", "confidence": 0.9},
            {"src": "建筑", "dst": "敌人", "relation": "形成优势", "confidence": 0.8},
        ],
    },
    "b0fc092fcb8d0479": {
        "entities": [
            {"name": "梦", "type": "概念", "aliases": ["dream"]},
            {"name": "歌声", "type": "概念", "aliases": ["song"]},
            {"name": "教官", "type": "角色", "aliases": ["instructors"]},
        ],
        "relations": [
            {"src": "歌声", "dst": "梦", "relation": "出现于", "confidence": 0.8},
        ],
    },
    "6ba3bee202e4769a": {
        "entities": [
            {"name": "手电筒", "type": "物品", "aliases": ["flashlights"]},
            {"name": "光束", "type": "概念", "aliases": ["beams of light"]},
            {"name": "玩具盒", "type": "物品", "aliases": ["toy box"]},
            {"name": "外部观察者", "type": "概念", "aliases": ["people outside the room"]},
        ],
        "relations": [
            {"src": "光束", "dst": "手电筒", "relation": "互相干扰", "confidence": 0.9},
            {"src": "外部观察者", "dst": "玩具盒", "relation": "增加干扰",
             "confidence": 0.9},
        ],
    },
    "36224f682ae74e99": {
        "entities": [
            {"name": "破译工作", "type": "事件", "aliases": ["decoding work"]},
            {"name": "实验室", "type": "地点", "aliases": ["laboratory"]},
            {"name": "宿舍", "type": "地点", "aliases": ["dorm"]},
            {"name": "应急避难所", "type": "地点", "aliases": ["emergency shelter"]},
            {"name": "房屋", "type": "地点", "aliases": ["house"]},
        ],
        "relations": [
            {"src": "房屋", "dst": "实验室", "relation": "非", "confidence": 0.9},
            {"src": "房屋", "dst": "应急避难所", "relation": "非", "confidence": 0.9},
            {"src": "破译工作", "dst": "房屋", "relation": "进行于", "confidence": 0.8},
        ],
    },
    "1f6ad655c25f0617": {
        "entities": [
            {"name": "瘟疫", "type": "事件", "aliases": ["plague"]},
            {"name": "人类", "type": "概念", "aliases": ["humanity"]},
            {"name": "严冬", "type": "时间", "aliases": ["harsh winter"]},
            {"name": "太阳", "type": "概念", "aliases": ["sun"]},
        ],
        "relations": [
            {"src": "瘟疫", "dst": "人类", "relation": "威胁存续", "confidence": 0.9},
            {"src": "人类", "dst": "严冬", "relation": "抵御", "confidence": 0.8},
        ],
    },
    "2bcf3f3a7feba2a8": {
        "entities": [
            {"name": "宇航员", "type": "角色", "aliases": ["astronaut"]},
            {"name": "零重力环境", "type": "概念",
             "aliases": ["zero-gravity environment"]},
            {"name": "训练课程", "type": "事件", "aliases": ["training course"]},
            {"name": "高压", "type": "概念", "aliases": ["high pressure"]},
        ],
        "relations": [
            {"src": "训练课程", "dst": "宇航员", "relation": "需完成", "confidence": 0.9},
            {"src": "零重力环境", "dst": "宇航员", "relation": "需适应", "confidence": 0.9},
            {"src": "高压", "dst": "宇航员", "relation": "需承受", "confidence": 0.8},
        ],
    },
    "c15f68e41ae70ce6": {
        "entities": [
            {"name": "蛆虫", "type": "概念", "aliases": ["Maggots"]},
            {"name": "尸体", "type": "概念", "aliases": ["bodies"]},
            {"name": "泥土", "type": "概念", "aliases": ["mud"]},
            {"name": "雨水", "type": "概念", "aliases": ["rainwater"]},
        ],
        "relations": [
            {"src": "蛆虫", "dst": "尸体", "relation": "啃食", "confidence": 0.9},
            {"src": "尸体", "dst": "泥土", "relation": "融入", "confidence": 0.9},
        ],
    },
    "ced12ebcf0d55b20": {
        "entities": [
            {"name": "言语", "type": "概念", "aliases": ["Words"]},
            {"name": "影子", "type": "概念", "aliases": ["second shadow"]},
            {"name": "枪声", "type": "概念", "aliases": ["gunshots"]},
            {"name": "记忆", "type": "概念", "aliases": ["memory"]},
        ],
        "relations": [
            {"src": "影子", "dst": "言语", "relation": "如影随形", "confidence": 0.8},
            {"src": "枪声", "dst": "记忆", "relation": "被埋葬", "confidence": 0.8},
        ],
    },
    "45d47fc65cd65aea": {
        "entities": [
            {"name": "杂志编辑", "type": "角色", "aliases": ["Magazine editor"]},
            {"name": "战地记者", "type": "角色", "aliases": ["combat correspondent"]},
            {"name": "感染者", "type": "概念", "aliases": ["infected"]},
            {"name": "车站仓库", "type": "地点", "aliases": ["station warehouse"]},
            {"name": "隔离", "type": "事件", "aliases": ["quarantine"]},
        ],
        "relations": [
            {"src": "杂志编辑", "dst": "战地记者", "relation": "转行", "confidence": 0.9},
            {"src": "感染者", "dst": "车站仓库", "relation": "来自", "confidence": 0.9},
            {"src": "隔离", "dst": "感染者", "relation": "针对", "confidence": 0.9},
        ],
    },
    "b3e5a77dd474f693": {
        "entities": [
            {"name": "奥斯曼人", "type": "角色", "aliases": ["Ottoman"]},
            {"name": "叔叔", "type": "角色", "aliases": ["uncle"]},
            {"name": "汽车", "type": "物品", "aliases": ["car"]},
            {"name": "收成", "type": "概念", "aliases": ["harvest"]},
            {"name": "土地", "type": "地点", "aliases": ["the land"]},
        ],
        "relations": [
            {"src": "叔叔", "dst": "汽车", "relation": "需修理", "confidence": 0.8},
            {"src": "收成", "dst": "土地", "relation": "关乎", "confidence": 0.7},
        ],
    },
    "b943d2bfd4229051": {
        "entities": [
            {"name": "赛船", "type": "物品", "aliases": ["ship"]},
            {"name": "倾斜边缘", "type": "地点", "aliases": ["inclined rim"]},
            {"name": "滑翔", "type": "概念", "aliases": ["glide"]},
            {"name": "竞技会", "type": "事件", "aliases": ["competitions"]},
            {"name": "岛屿", "type": "地点", "aliases": ["island"]},
        ],
        "relations": [
            {"src": "赛船", "dst": "倾斜边缘", "relation": "起滑", "confidence": 0.9},
            {"src": "滑翔", "dst": "赛船", "relation": "决定距离", "confidence": 0.9},
            {"src": "竞技会", "dst": "岛屿", "relation": "举办于", "confidence": 0.8},
        ],
    },
    "65c3db710bcbe59f": {
        "entities": [
            {"name": "充气结构", "type": "概念", "aliases": ["inflatable"]},
            {"name": "轮子", "type": "物品", "aliases": ["wheels"]},
            {"name": "硬质机翼", "type": "物品", "aliases": ["rigid wings"]},
            {"name": "滑翔", "type": "概念", "aliases": ["glide"]},
            {"name": "起飞", "type": "事件", "aliases": ["launch"]},
            {"name": "空中稳定", "type": "概念", "aliases": ["stability in the air"]},
        ],
        "relations": [
            {"src": "充气结构", "dst": "滑翔", "relation": "延长", "confidence": 0.9},
            {"src": "轮子", "dst": "起飞", "relation": "使平稳", "confidence": 0.9},
            {"src": "硬质机翼", "dst": "空中稳定", "relation": "确保", "confidence": 0.9},
        ],
    },
    "0d0b5770e20918e1": {
        "entities": [
            {"name": "诅咒", "type": "概念", "aliases": ["curse"]},
            {"name": "恶魔附身", "type": "概念", "aliases": ["demonic possession"]},
            {"name": "暗影之兽", "type": "概念",
             "aliases": ["beast born of no mortal womb", "monstrosity"]},
            {"name": "城市", "type": "地点", "aliases": ["city"]},
            {"name": "旧秩序", "type": "概念", "aliases": ["old order"]},
            {"name": "崩塌", "type": "事件", "aliases": []},
        ],
        "relations": [
            {"src": "暗影之兽", "dst": "城市", "relation": "潜伏", "confidence": 0.8},
            {"src": "恶魔附身", "dst": "诅咒", "relation": "被解释为", "confidence": 0.8},
            {"src": "旧秩序", "dst": "崩塌", "relation": "已", "confidence": 0.8},
        ],
    },
    "361dedc8c6157a66": {
        "entities": [
            {"name": "占卜", "type": "概念", "aliases": ["divinations"]},
            {"name": "自我实现的预言", "type": "概念",
             "aliases": ["self-fulfilling prophecies"]},
            {"name": "水晶球", "type": "物品", "aliases": ["crystal ball"]},
            {"name": "命运", "type": "概念", "aliases": ["fate"]},
            {"name": "因果律", "type": "概念", "aliases": ["cause and effect"]},
        ],
        "relations": [
            {"src": "占卜", "dst": "自我实现的预言", "relation": "可能是",
             "confidence": 0.8},
            {"src": "命运", "dst": "因果律", "relation": "是", "confidence": 0.9},
        ],
    },
    "3494fe1df6dd3ab9": {
        "entities": [
            {"name": "故事", "type": "概念", "aliases": ["historia", "story"]},
            {"name": "根", "type": "概念", "aliases": ["raíces"]},
            {"name": "力量", "type": "概念", "aliases": ["fuerza"]},
        ],
        "relations": [
            {"src": "故事", "dst": "根", "relation": "失去力量", "confidence": 0.7},
        ],
    },
    "c69f0a4c30725352": {
        "entities": [
            {"name": "建筑几何", "type": "概念", "aliases": ["building's geometry"]},
            {"name": "金色能量", "type": "概念",
             "aliases": ["energy like a river of gold"]},
        ],
        "relations": [
            {"src": "建筑几何", "dst": "金色能量", "relation": "关联", "confidence": 0.6},
        ],
    },
    "40d6be0d9f957778": {
        "entities": [
            {"name": "时间异常", "type": "事件",
             "aliases": ["temporal anomaly", "anomaly"]},
            {"name": "时间倒转", "type": "概念", "aliases": ["time reversal"]},
            {"name": "不可逆点", "type": "概念", "aliases": ["points irreversible"]},
            {"name": "合作", "type": "概念", "aliases": ["collaboration"]},
        ],
        "relations": [
            {"src": "时间异常", "dst": "时间倒转", "relation": "是否必然",
             "confidence": 0.8},
            {"src": "不可逆点", "dst": "时间异常", "relation": "相关地点",
             "confidence": 0.9},
            {"src": "合作", "dst": "不可逆点", "relation": "需建立", "confidence": 0.7},
        ],
    },
    "b2443e590bd76dce": {
        "entities": [
            {"name": "研究站", "type": "地点", "aliases": ["research station"]},
            {"name": "摩尔斯电码", "type": "概念", "aliases": ["Morse code"]},
            {"name": "警告信息", "type": "物品", "aliases": ["warning message"]},
            {"name": "团队", "type": "组织", "aliases": ["team"]},
        ],
        "relations": [
            {"src": "团队", "dst": "研究站", "relation": "建造", "confidence": 0.9},
            {"src": "摩尔斯电码", "dst": "警告信息", "relation": "用于拼写",
             "confidence": 0.9},
        ],
    },
    "872490bd08ceda49": {
        "entities": [
            {"name": "玩具盒", "type": "物品", "aliases": ["toy box"]},
            {"name": "数据集", "type": "概念", "aliases": ["dataset"]},
            {"name": "自动售货机", "type": "物品", "aliases": ["vending machine"]},
            {"name": "数据滞后", "type": "概念", "aliases": ["lag in data"]},
        ],
        "relations": [
            {"src": "玩具盒", "dst": "数据集", "relation": "存于", "confidence": 0.9},
            {"src": "数据滞后", "dst": "自动售货机", "relation": "使其稳定",
             "confidence": 0.9},
        ],
    },
    "1bb6d567a60ac340": {
        "entities": [
            {"name": "树", "type": "物品", "aliases": ["tree"]},
            {"name": "火", "type": "概念", "aliases": ["fire"]},
            {"name": "鸡", "type": "物品", "aliases": ["chicken"]},
            {"name": "果实", "type": "概念", "aliases": ["fruit"]},
            {"name": "浆果", "type": "物品", "aliases": ["berries"]},
        ],
        "relations": [
            {"src": "火", "dst": "鸡", "relation": "烤", "confidence": 0.9},
            {"src": "树", "dst": "果实", "relation": "未结", "confidence": 0.8},
            {"src": "浆果", "dst": "果实", "relation": "替代", "confidence": 0.7},
        ],
    },
    "52ff2f1fa83d3843": {
        "entities": [
            {"name": "出院", "type": "事件", "aliases": ["discharged"]},
            {"name": "医疗手册", "type": "物品", "aliases": ["medical manual"]},
            {"name": "疗程", "type": "概念", "aliases": ["course of treatment"]},
            {"name": "南极洲", "type": "地点", "aliases": ["Antarctic"]},
            {"name": "未知之物", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "医疗手册", "dst": "疗程", "relation": "规定", "confidence": 0.9},
            {"src": "南极洲", "dst": "未知之物", "relation": "藏于", "confidence": 0.7},
        ],
    },
    "3272b540c5ccce5a": {
        "entities": [
            {"name": "人类", "type": "概念", "aliases": ["humans"]},
            {"name": "生存", "type": "概念", "aliases": ["survival"]},
            {"name": "科学", "type": "概念", "aliases": ["science"]},
            {"name": "科技", "type": "概念", "aliases": ["human technology"]},
        ],
        "relations": [
            {"src": "生存", "dst": "人类", "relation": "最大动机", "confidence": 0.9},
            {"src": "科学", "dst": "生存", "relation": "被导向", "confidence": 0.8},
        ],
    },
    "72afa70c6e7b91fe": {
        "entities": [
            {"name": "花", "type": "物品", "aliases": ["flowers"]},
            {"name": "种子", "type": "物品", "aliases": ["seeds"]},
            {"name": "疏散", "type": "事件", "aliases": ["evacuation", "evacuate"]},
            {"name": "邻居", "type": "角色", "aliases": ["neighbors"]},
            {"name": "严寒", "type": "概念", "aliases": ["cold"]},
        ],
        "relations": [
            {"src": "种子", "dst": "花", "relation": "长成", "confidence": 0.9},
            {"src": "邻居", "dst": "花", "relation": "获赠", "confidence": 0.8},
            {"src": "疏散", "dst": "花", "relation": "迫使舍弃", "confidence": 0.8},
        ],
    },
    "bd848747fd05001c": {
        "entities": [
            {"name": "内脏现实主义", "type": "概念", "aliases": ["visceral realism"]},
            {"name": "玛丽亚", "type": "角色", "aliases": ["Maria"]},
            {"name": "虚构小镇", "type": "地点", "aliases": ["fictitious town"]},
            {"name": "小说", "type": "物品", "aliases": ["novel"]},
            {"name": "严冬", "type": "时间", "aliases": ["winter"]},
        ],
        "relations": [
            {"src": "内脏现实主义", "dst": "小说", "relation": "主题", "confidence": 0.8},
            {"src": "虚构小镇", "dst": "小说", "relation": "重要", "confidence": 0.8},
            {"src": "玛丽亚", "dst": "内脏现实主义", "relation": "倡导",
             "confidence": 0.8},
        ],
    },
    "48addd9fe8baf8d7": {
        "entities": [
            {"name": "1999年后的世界", "type": "概念", "aliases": ["A world after 1999"]},
            {"name": "阅读写作", "type": "概念",
             "aliases": ["keep reading, keep writing"]},
        ],
        "relations": [
            {"src": "阅读写作", "dst": "1999年后的世界", "relation": "追寻",
             "confidence": 0.8},
        ],
    },
    "23c5449a2321c590": {
        "entities": [
            {"name": "死亡", "type": "概念", "aliases": ["death"]},
            {"name": "雨", "type": "事件", "aliases": ["rain"]},
            {"name": "抹除", "type": "概念", "aliases": ["washes something away"]},
        ],
        "relations": [
            {"src": "雨", "dst": "死亡", "relation": "必然相随", "confidence": 0.9},
            {"src": "雨", "dst": "抹除", "relation": "每次", "confidence": 0.9},
        ],
    },
    "771f0beb4f494429": {
        "entities": [
            {"name": "重塑之手", "type": "组织",
             "aliases": ["mannus", "Manus", "Manus Vindictae"]},
            {"name": "神秘学家", "type": "概念",
             "aliases": ["arcaneists", "arcanists", "Arcanists"]},
            {"name": "军队", "type": "组织", "aliases": ["army"]},
            {"name": "和平政策", "type": "概念", "aliases": ["peace policy"]},
            {"name": "委员会", "type": "组织", "aliases": ["committee"]},
        ],
        "relations": [
            {"src": "重塑之手", "dst": "军队", "relation": "组建", "confidence": 0.9},
            {"src": "和平政策", "dst": "神秘学家", "relation": "无法保护",
             "confidence": 0.8},
            {"src": "委员会", "dst": "军队", "relation": "审议", "confidence": 0.7},
        ],
    },
    "51612156545e3a81": {
        "entities": [
            {"name": "抉择", "type": "概念", "aliases": ["decision"]},
            {"name": "改变", "type": "概念", "aliases": ["change things"]},
            {"name": "保护", "type": "概念", "aliases": ["protect"]},
        ],
        "relations": [
            {"src": "抉择", "dst": "改变", "relation": "可能带来", "confidence": 0.8},
        ],
    },
    "70480fec23258c30": {
        "entities": [
            {"name": "疏散", "type": "事件", "aliases": ["evacuation"]},
            {"name": "花", "type": "物品", "aliases": ["flowers"]},
            {"name": "种子", "type": "物品", "aliases": ["seeds"]},
            {"name": "冻土", "type": "概念", "aliases": ["soil frozen over"]},
            {"name": "女儿", "type": "角色", "aliases": ["daughter"]},
            {"name": "奇迹", "type": "概念", "aliases": ["miracle"]},
        ],
        "relations": [
            {"src": "种子", "dst": "花", "relation": "长成", "confidence": 0.9},
            {"src": "女儿", "dst": "种子", "relation": "播种", "confidence": 0.9},
            {"src": "冻土", "dst": "花", "relation": "阻碍种植", "confidence": 0.9},
            {"src": "疏散", "dst": "花", "relation": "迫使舍弃", "confidence": 0.8},
        ],
    },
    "a3afd6861f65b501": {
        "entities": [
            {"name": "命运之路", "type": "概念", "aliases": ["fate's path"]},
            {"name": "世界", "type": "概念", "aliases": ["world"]},
            {"name": "发现", "type": "概念", "aliases": ["discover"]},
        ],
        "relations": [
            {"src": "命运之路", "dst": "发现", "relation": "带来裨益", "confidence": 0.7},
        ],
    },
    "be06b354010df748": {
        "entities": [
            {"name": "好运项链", "type": "物品", "aliases": ["good luck necklaces"]},
            {"name": "论文", "type": "物品", "aliases": ["paper"]},
            {"name": "冒险家", "type": "角色", "aliases": ["adventurer"]},
        ],
        "relations": [
            {"src": "论文", "dst": "好运项链", "relation": "发表后购买",
             "confidence": 0.8},
        ],
    },
    "55c25533aaa0eb52": {
        "entities": [
            {"name": "家乡", "type": "地点", "aliases": ["hometown"]},
            {"name": "灵感", "type": "概念", "aliases": ["inspiration"]},
            {"name": "自由", "type": "概念", "aliases": ["free to go"]},
        ],
        "relations": [
            {"src": "灵感", "dst": "家乡", "relation": "来自", "confidence": 0.8},
            {"src": "家乡", "dst": "自由", "relation": "重获", "confidence": 0.7},
        ],
    },
    "7d6c4c5a14be15c2": {
        "entities": [
            {"name": "木偶", "type": "概念", "aliases": ["puppets"]},
            {"name": "感冒", "type": "概念", "aliases": ["cold"]},
            {"name": "感染", "type": "概念", "aliases": ["infection"]},
            {"name": "招募", "type": "事件", "aliases": ["recruiting"]},
        ],
        "relations": [
            {"src": "感冒", "dst": "感染", "relation": "是", "confidence": 0.9},
            {"src": "木偶", "dst": "感冒", "relation": "会患", "confidence": 0.8},
        ],
    },
    "7cfbfd0094f67b5e": {
        "entities": [
            {"name": "拘留室", "type": "地点", "aliases": ["detention room"]},
            {"name": "驱魔师", "type": "角色", "aliases": ["exorcist"]},
            {"name": "学校", "type": "组织", "aliases": ["school"]},
            {"name": "幽灵", "type": "概念", "aliases": ["ghosts"]},
            {"name": "二分点", "type": "时间", "aliases": ["equinox"]},
        ],
        "relations": [
            {"src": "学校", "dst": "驱魔师", "relation": "雇请", "confidence": 0.9},
            {"src": "驱魔师", "dst": "二分点", "relation": "每届检查", "confidence": 0.9},
            {"src": "幽灵", "dst": "拘留室", "relation": "盘踞", "confidence": 0.7},
        ],
    },
    "925dc8a5aec1de7c": {
        "entities": [
            {"name": "3826设施", "type": "地点", "aliases": ["facility 3826"]},
            {"name": "拉菲克", "type": "角色", "aliases": ["rafik", "Rafik"]},
            {"name": "激活码", "type": "物品", "aliases": ["activation codes"]},
            {"name": "浮动岛", "type": "地点", "aliases": ["floating island"]},
            {"name": "会议场地", "type": "地点", "aliases": ["conference venue"]},
            {"name": "展览馆", "type": "地点", "aliases": ["exhibition hall"]},
        ],
        "relations": [
            {"src": "拉菲克", "dst": "激活码", "relation": "负责", "confidence": 0.9},
            {"src": "会议场地", "dst": "浮动岛", "relation": "位于", "confidence": 0.9},
            {"src": "3826设施", "dst": "展览馆", "relation": "含", "confidence": 0.8},
        ],
    },
    "9a0158e254a06508": {
        "entities": [
            {"name": "诱饵", "type": "角色", "aliases": ["decoy"]},
            {"name": "办公室", "type": "地点", "aliases": ["office"]},
            {"name": "供暖", "type": "概念", "aliases": ["heat"]},
            {"name": "同事", "type": "概念", "aliases": ["colleagues"]},
        ],
        "relations": [
            {"src": "诱饵", "dst": "办公室", "relation": "被带往", "confidence": 0.8},
            {"src": "办公室", "dst": "供暖", "relation": "需保持", "confidence": 0.8},
        ],
    },
    "23d22d6ef61e9252": {
        "entities": [
            {"name": "乡亲", "type": "组织", "aliases": ["townsfolk"]},
            {"name": "前线", "type": "地点", "aliases": ["front"]},
            {"name": "农时", "type": "时间", "aliases": ["farming season"]},
            {"name": "庄稼", "type": "物品", "aliases": ["crops"]},
            {"name": "种子", "type": "物品", "aliases": ["seed"]},
        ],
        "relations": [
            {"src": "乡亲", "dst": "前线", "relation": "归来", "confidence": 0.9},
            {"src": "农时", "dst": "庄稼", "relation": "无收", "confidence": 0.9},
            {"src": "庄稼", "dst": "种子", "relation": "不结", "confidence": 0.9},
        ],
    },
}


def main() -> int:
    ap = argparse.ArgumentParser(description="补抽空块 第 6 批")
    ap.add_argument("--character", default="wu_ming_zhe")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    settings = get_settings()
    cache_dir = Path(settings.plot_cache_dir) / args.character
    cache_dir.mkdir(parents=True, exist_ok=True)

    written = skipped = 0
    for h, data in RESULTS.items():
        p = cache_dir / f"{h}.json"
        if p.exists() and not args.force:
            skipped += 1
            continue
        p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        written += 1
    print(f"[apply-p6] 写入 {written} 条，跳过 {skipped} 条")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
