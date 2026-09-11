# -*- coding: utf-8 -*-
"""补齐 18 个本地 7B 模型抽取失败的剧情块（云端模型人工校验结果）。

背景：本地 ``qwen2.5:7b`` 对这 18 块稳定产出畸形 JSON，重试无效；
本文件用云端模型（人工复核）的抽取结果直接写 ``plot_cache/<cid>/<hash>.json``，
随后 ``--build-graph`` 从缓存全量回放（零 LLM 调用）即可完成图谱补齐。

用法：
  python scripts/apply_failed_chunks_18.py            # 写缓存（已存在则跳过）
  python scripts/apply_failed_chunks_18.py --force    # 覆盖写
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from roleplay.config import get_settings  # noqa: E402

# hash → 抽取结果（格式与 GraphCache 一致）
RESULTS: dict[str, dict] = {
    # ── #1 zh 全主线解析（薯条小叔叔）：基金会派系斗争 / 冠体实验 ──
    "cd2a0d92e5ec8eb9": {
        "entities": [
            {"name": "维尔汀", "type": "角色", "aliases": ["Vertin", "维尔廷", "维尔丁"]},
            {"name": "拉普拉斯", "type": "组织", "aliases": ["Laplace"]},
            {"name": "圣洛夫基金会", "type": "组织", "aliases": ["基金会", "Foundation"]},
            {"name": "鸽子屋", "type": "组织", "aliases": ["Pigeon House"]},
            {"name": "重塑之手", "type": "组织", "aliases": ["Manus Vindictae", "重塑之首"]},
            {"name": "Pedra", "type": "角色", "aliases": ["佩德拉", "Pedra 保守派"]},
            {"name": "张芝芝", "type": "角色", "aliases": ["Zhang Zhizhi"]},
            {"name": "保守派", "type": "组织", "aliases": ["基金会保守派"]},
            {"name": "改革派", "type": "组织", "aliases": ["基金会改革派"]},
            {"name": "神秘学家", "type": "概念", "aliases": ["arcanist"]},
            {"name": "第一防线学校", "type": "组织", "aliases": ["第一防线"]},
            {"name": "冠体实验", "type": "事件", "aliases": []},
            {"name": "传送软盘", "type": "物品", "aliases": ["传送盘"]},
        ],
        "relations": [
            {"src": "鸽子屋", "dst": "圣洛夫基金会", "relation": "指示", "confidence": 0.9},
            {"src": "Pedra", "dst": "保守派", "relation": "代表", "confidence": 0.9},
            {"src": "张芝芝", "dst": "改革派", "relation": "代表", "confidence": 0.9},
            {"src": "张芝芝", "dst": "拉普拉斯", "relation": "来自", "confidence": 0.9},
            {"src": "Pedra", "dst": "圣洛夫基金会", "relation": "隶属", "confidence": 0.8},
            {"src": "保守派", "dst": "神秘学家", "relation": "主张管控", "confidence": 0.8},
            {"src": "改革派", "dst": "神秘学家", "relation": "主张合作", "confidence": 0.8},
            {"src": "保守派", "dst": "重塑之手", "relation": "视为威胁", "confidence": 0.7},
            {"src": "第一防线学校", "dst": "圣洛夫基金会", "relation": "隶属", "confidence": 0.6},
            {"src": "第一防线学校", "dst": "神秘学家", "relation": "消除记忆", "confidence": 0.7},
            {"src": "神秘学家", "dst": "拉普拉斯", "relation": "隶属", "confidence": 0.7},
            {"src": "传送软盘", "dst": "拉普拉斯", "relation": "来源", "confidence": 0.6},
            {"src": "维尔汀", "dst": "冠体实验", "relation": "涉及", "confidence": 0.6},
        ],
    },
    # ── #2 en 3.6《答案在盒底》：玩具盒模拟与应急预案 ──
    "4be44edf99ecf1ae": {
        "entities": [
            {"name": "拉普拉斯", "type": "组织", "aliases": ["Laplace"]},
            {"name": "toy box", "type": "物品", "aliases": ["玩具盒", "toy boxes"]},
            {"name": "emergency protocol", "type": "概念", "aliases": ["应急预案"]},
            {"name": "圣洛夫基金会", "type": "组织", "aliases": ["Foundation", "基金会"]},
        ],
        "relations": [
            {"src": "toy box", "dst": "emergency protocol", "relation": "用于制定", "confidence": 0.85},
            {"src": "圣洛夫基金会", "dst": "拉普拉斯", "relation": "施压", "confidence": 0.6},
            {"src": "拉普拉斯", "dst": "emergency protocol", "relation": "提交", "confidence": 0.7},
        ],
    },
    # ── #3 en 3.6《夜间攀登者》：拆解玩具盒的分歧 ──
    "9f1502e7a8b945b4": {
        "entities": [
            {"name": "toy box", "type": "物品", "aliases": ["玩具盒"]},
            {"name": "Ludwig", "type": "角色", "aliases": ["路德维希", "卢迪维克"]},
            {"name": "Medicine Pocket", "type": "角色", "aliases": ["researcher medicine pocket", "研究员药袋", "医药包"]},
            {"name": "core", "type": "物品", "aliases": ["核心"]},
            {"name": "cryptographer", "type": "角色", "aliases": ["密码学家"]},
            {"name": "key", "type": "物品", "aliases": ["密钥"]},
            {"name": "data loss", "type": "事件", "aliases": ["数据丢失"]},
        ],
        "relations": [
            {"src": "Ludwig", "dst": "toy box", "relation": "位于", "confidence": 0.85},
            {"src": "core", "dst": "toy box", "relation": "位于", "confidence": 0.85},
            {"src": "Medicine Pocket", "dst": "toy box", "relation": "主张拆解", "confidence": 0.9},
            {"src": "toy box", "dst": "data loss", "relation": "可能导致", "confidence": 0.8},
            {"src": "cryptographer", "dst": "key", "relation": "无法逆向", "confidence": 0.7},
        ],
    },
    # ── #4 en 3.7「他者的悲哀」TH.24【报偿】：离职申请与记录抹除 ──
    "ce4f4ec5c6f6fc43": {
        "entities": [
            {"name": "Madam Z", "type": "角色", "aliases": ["Z夫人", "Z女士"]},
            {"name": "Vice President", "type": "角色", "aliases": ["副会长", "副主席"]},
            {"name": "圣洛夫基金会", "type": "组织", "aliases": ["Foundation", "基金会"]},
            {"name": "one-way portal", "type": "地点", "aliases": ["单向门", "单向传送门"]},
            {"name": "无名者", "type": "角色", "aliases": ["Ms. Stranger", "Stranger"]},
        ],
        "relations": [
            {"src": "无名者", "dst": "圣洛夫基金会", "relation": "提交申请", "confidence": 0.7},
            {"src": "Madam Z", "dst": "Vice President", "relation": "商议", "confidence": 0.85},
            {"src": "Madam Z", "dst": "圣洛夫基金会", "relation": "隶属", "confidence": 0.8},
            {"src": "Vice President", "dst": "圣洛夫基金会", "relation": "隶属", "confidence": 0.8},
            {"src": "无名者", "dst": "one-way portal", "relation": "关闭", "confidence": 0.8},
            {"src": "圣洛夫基金会", "dst": "无名者", "relation": "抹除记录", "confidence": 0.85},
        ],
    },
    # ── #5 en 联动「聚合浪潮」：集体神经网络与机器人 ──
    "ae21a0e1cacae302": {
        "entities": [
            {"name": "collective", "type": "组织", "aliases": ["集合体", "集体"]},
            {"name": "collective neural network", "type": "概念", "aliases": ["集体神经网络"]},
            {"name": "robot", "type": "物品", "aliases": ["机器人", "robots"]},
            {"name": "farmer", "type": "角色", "aliases": ["农民", "farmers"]},
            {"name": "scientific advancement", "type": "概念", "aliases": ["科技进步"]},
        ],
        "relations": [
            {"src": "collective neural network", "dst": "robot", "relation": "控制", "confidence": 0.9},
            {"src": "collective", "dst": "collective neural network", "relation": "拥有", "confidence": 0.75},
            {"src": "robot", "dst": "farmer", "relation": "协助", "confidence": 0.7},
            {"src": "farmer", "dst": "scientific advancement", "relation": "研究", "confidence": 0.8},
        ],
    },
    # ── #6 en 3.1「长夜鸣笛」十三号车厢：吸血鬼与难民 ──
    "6761b931d082cc4e": {
        "entities": [
            {"name": "vampire", "type": "角色", "aliases": ["吸血鬼"]},
            {"name": "carriage", "type": "地点", "aliases": ["车厢", "十三号车厢", "13号车厢"]},
            {"name": "refugees", "type": "角色", "aliases": ["难民"]},
        ],
        "relations": [
            {"src": "vampire", "dst": "refugees", "relation": "追捕", "confidence": 0.7},
            {"src": "refugees", "dst": "carriage", "relation": "藏身", "confidence": 0.7},
            {"src": "vampire", "dst": "carriage", "relation": "搜寻", "confidence": 0.6},
        ],
    },
    # ── #7 zh 重讲未来#0：1913 年、重塑面具与阿派朗学派 ──
    "2f0402a9ed09feb7": {
        "entities": [
            {"name": "维尔汀", "type": "角色", "aliases": ["Vertin", "维尔廷", "维尔丁"]},
            {"name": "圣洛夫基金会", "type": "组织", "aliases": ["基金会", "Foundation"]},
            {"name": "鸽子屋", "type": "组织", "aliases": ["Pigeon House"]},
            {"name": "保守派", "type": "组织", "aliases": ["基金会保守派"]},
            {"name": "暴雨", "type": "事件", "aliases": ["the Storm", "风暴"]},
            {"name": "重塑面具", "type": "物品", "aliases": ["重塑的面具"]},
            {"name": "阿派朗学派", "type": "组织", "aliases": ["Apeiron", "阿派朗"]},
            {"name": "爱琴海", "type": "地点", "aliases": ["爱琴海小岛"]},
            {"name": "神秘学家", "type": "概念", "aliases": ["arcanist"]},
        ],
        "relations": [
            {"src": "鸽子屋", "dst": "圣洛夫基金会", "relation": "指示", "confidence": 0.9},
            {"src": "保守派", "dst": "圣洛夫基金会", "relation": "隶属", "confidence": 0.8},
            {"src": "维尔汀", "dst": "暴雨", "relation": "抵抗", "confidence": 0.9},
            {"src": "维尔汀", "dst": "重塑面具", "relation": "缴获", "confidence": 0.85},
            {"src": "重塑面具", "dst": "暴雨", "relation": "抵抗", "confidence": 0.8},
            {"src": "阿派朗学派", "dst": "爱琴海", "relation": "位于", "confidence": 0.8},
            {"src": "阿派朗学派", "dst": "暴雨", "relation": "观测", "confidence": 0.8},
            {"src": "阿派朗学派", "dst": "暴雨", "relation": "防护", "confidence": 0.7},
            {"src": "维尔汀", "dst": "阿派朗学派", "relation": "抵达", "confidence": 0.8},
            {"src": "阿派朗学派", "dst": "神秘学家", "relation": "由…组成", "confidence": 0.7},
        ],
    },
    # ── #8 en 3.3「远征记」时代遗物：骑兵撤离 ──
    "25ee52e8898f2ead": {
        "entities": [
            {"name": "cavalry", "type": "组织", "aliases": ["骑兵", "骑兵队", "Cavalry Corps", "The Cavalry"]},
            {"name": "Paragrad", "type": "地点", "aliases": ["帕拉格勒"]},
            {"name": "Tomarovka", "type": "地点", "aliases": ["托马罗夫卡"]},
            {"name": "Dawn", "type": "地点", "aliases": ["黎明", "曙光"]},
            {"name": "citizens", "type": "角色", "aliases": ["市民", "平民"]},
        ],
        "relations": [
            {"src": "cavalry", "dst": "citizens", "relation": "保护", "confidence": 0.85},
            {"src": "cavalry", "dst": "Dawn", "relation": "撤离", "confidence": 0.7},
            {"src": "citizens", "dst": "Tomarovka", "relation": "居住", "confidence": 0.6},
        ],
    },
    # ── #9 en 3.3「远征记」时代遗物：项目危害与军事区 ──
    "58e2b8696ba87295": {
        "entities": [
            {"name": "Green Lake campsite", "type": "地点", "aliases": ["绿湖营地", "Green Lake"]},
            {"name": "Ember Room", "type": "组织", "aliases": ["火光之室"]},
            {"name": "Berograd", "type": "地点", "aliases": ["贝罗格", "伯格拉德"]},
            {"name": "圣洛夫基金会", "type": "组织", "aliases": ["Foundation", "基金会"]},
            {"name": "project", "type": "事件", "aliases": ["该项目"]},
            {"name": "underground site", "type": "地点", "aliases": ["地下遗址"]},
            {"name": "military zone", "type": "地点", "aliases": ["军事区"]},
            {"name": "soldiers", "type": "角色", "aliases": ["士兵"]},
            {"name": "tourists", "type": "角色", "aliases": ["游客", "度假者"]},
        ],
        "relations": [
            {"src": "project", "dst": "tourists", "relation": "造成伤害", "confidence": 0.8},
            {"src": "tourists", "dst": "Green Lake campsite", "relation": "位于", "confidence": 0.7},
            {"src": "Ember Room", "dst": "Green Lake campsite", "relation": "破坏", "confidence": 0.6},
            {"src": "soldiers", "dst": "Berograd", "relation": "驻扎", "confidence": 0.75},
            {"src": "military zone", "dst": "Berograd", "relation": "位于", "confidence": 0.8},
            {"src": "military zone", "dst": "underground site", "relation": "保护", "confidence": 0.8},
            {"src": "圣洛夫基金会", "dst": "soldiers", "relation": "审查", "confidence": 0.8},
        ],
    },
    # ── #10 en 3.3「远征记」河岸静悄悄：谢尔盖与中尉 ──
    "d6cf5f40c8bee74e": {
        "entities": [
            {"name": "Sergei", "type": "角色", "aliases": ["谢尔盖", "塞吉"]},
            {"name": "Lieutenant", "type": "角色", "aliases": ["中尉"]},
            {"name": "telescope", "type": "物品", "aliases": ["望远镜"]},
            {"name": "watch point", "type": "地点", "aliases": ["哨点", "观察点"]},
        ],
        "relations": [
            {"src": "Sergei", "dst": "Lieutenant", "relation": "隶属", "confidence": 0.8},
            {"src": "Lieutenant", "dst": "Sergei", "relation": "命令", "confidence": 0.85},
            {"src": "Sergei", "dst": "telescope", "relation": "使用", "confidence": 0.8},
            {"src": "Lieutenant", "dst": "watch point", "relation": "巡查", "confidence": 0.6},
        ],
    },
    # ── #11 en 3.3「远征记」寂静所笼罩的：重塑之手的招募被拒 ──
    "839d82e10238842c": {
        "entities": [
            {"name": "重塑之手", "type": "组织", "aliases": ["Manus Vindictae", "Manus vindicti", "曼努斯·维尼克泰"]},
            {"name": "无名者", "type": "角色", "aliases": ["Ms. Stranger", "freak"]},
        ],
        "relations": [
            {"src": "重塑之手", "dst": "无名者", "relation": "招募", "confidence": 0.6},
            {"src": "无名者", "dst": "重塑之手", "relation": "拒绝", "confidence": 0.6},
        ],
    },
    # ── #12 zh 3.4「不老春」致此离离：陆思简被封梅花树 ──
    "a8c48a1bc81d3885": {
        "entities": [
            {"name": "小小草", "type": "角色", "aliases": ["小草"]},
            {"name": "陆思简", "type": "角色", "aliases": ["陆思姐", "鲁思姐"]},
            {"name": "长生", "type": "概念", "aliases": ["长生之法", "长生之术"]},
            {"name": "长生剑", "type": "物品", "aliases": []},
            {"name": "梅花树", "type": "地点", "aliases": ["梅树"]},
            {"name": "论坛", "type": "概念", "aliases": ["网络论坛"]},
            {"name": "光缆", "type": "物品", "aliases": ["黑色的线", "电缆"]},
            {"name": "神秘术", "type": "概念", "aliases": ["arcane skill"]},
            {"name": "互联网", "type": "概念", "aliases": ["网络"]},
        ],
        "relations": [
            {"src": "陆思简", "dst": "梅花树", "relation": "被封印", "confidence": 0.85},
            {"src": "陆思简", "dst": "小小草", "relation": "联系", "confidence": 0.85},
            {"src": "陆思简", "dst": "论坛", "relation": "借助", "confidence": 0.8},
            {"src": "陆思简", "dst": "光缆", "relation": "借助", "confidence": 0.75},
            {"src": "陆思简", "dst": "神秘术", "relation": "使用", "confidence": 0.8},
            {"src": "光缆", "dst": "互联网", "relation": "连接", "confidence": 0.8},
            {"src": "长生剑", "dst": "长生", "relation": "决定", "confidence": 0.7},
            {"src": "小小草", "dst": "长生", "relation": "追寻", "confidence": 0.8},
            {"src": "小小草", "dst": "陆思简", "relation": "采访", "confidence": 0.7},
        ],
    },
    # ── #13 zh 3.4「不老春」致此离离：小小草的长生答复 ──
    "ef77d6639051ad99": {
        "entities": [
            {"name": "小小草", "type": "角色", "aliases": ["小草"]},
            {"name": "长生", "type": "概念", "aliases": ["长生之法", "长生之术"]},
            {"name": "陆思简", "type": "角色", "aliases": ["陆思姐", "鲁思姐"]},
            {"name": "报道", "type": "概念", "aliases": ["新闻稿"]},
            {"name": "论坛", "type": "概念", "aliases": ["网络论坛"]},
        ],
        "relations": [
            {"src": "小小草", "dst": "长生", "relation": "追寻", "confidence": 0.9},
            {"src": "小小草", "dst": "报道", "relation": "撰写", "confidence": 0.7},
            {"src": "小小草", "dst": "陆思简", "relation": "对话", "confidence": 0.8},
            {"src": "陆思简", "dst": "小小草", "relation": "认可", "confidence": 0.7},
            {"src": "小小草", "dst": "论坛", "relation": "借助", "confidence": 0.6},
        ],
    },
    # ── #14 en 3.2「迁流的盛宴」城市的癔症：热沃当野兽 ──
    "28a719d8d9ef1687": {
        "entities": [
            {"name": "Beast of Gevaudan", "type": "角色", "aliases": ["热沃当野兽", "盖沃丹野兽"]},
            {"name": "monsters", "type": "角色", "aliases": ["怪物", "monster"]},
            {"name": "city", "type": "地点", "aliases": ["城市"]},
        ],
        "relations": [
            {"src": "monsters", "dst": "city", "relation": "出没", "confidence": 0.8},
            {"src": "Beast of Gevaudan", "dst": "monsters", "relation": "属于", "confidence": 0.6},
        ],
    },
    # ── #15 en 3.2「迁流的盛宴」应许的时刻：巴黎地标与集体想象 ──
    "e56cec89bfc0e8d2": {
        "entities": [
            {"name": "Paris", "type": "地点", "aliases": ["巴黎", "pari", "Paris 幻影"]},
            {"name": "Palace of Optics", "type": "地点", "aliases": ["光学宫"]},
            {"name": "Eiffel Tower", "type": "地点", "aliases": ["埃菲尔铁塔"]},
            {"name": "Arc de Triomphe", "type": "地点", "aliases": ["凯旋门"]},
            {"name": "Notre-Dame", "type": "地点", "aliases": ["巴黎圣母院"]},
            {"name": "Luxor Obelisk", "type": "地点", "aliases": ["卢克索方尖碑"]},
            {"name": "Lutetia Arena", "type": "地点", "aliases": ["卢泰西亚竞技场"]},
            {"name": "Medieval Quarters", "type": "地点", "aliases": ["中世纪城区"]},
            {"name": "Roseau", "type": "角色", "aliases": ["罗索", "Professor Roseau", "Laurent Roseau"]},
            {"name": "collective imagination", "type": "概念", "aliases": ["集体想象"]},
            {"name": "thought", "type": "概念", "aliases": ["思想"]},
            {"name": "reality", "type": "概念", "aliases": ["现实"]},
        ],
        "relations": [
            {"src": "Paris", "dst": "collective imagination", "relation": "诞生于", "confidence": 0.8},
            {"src": "Paris", "dst": "Palace of Optics", "relation": "包含", "confidence": 0.8},
            {"src": "Paris", "dst": "Eiffel Tower", "relation": "包含", "confidence": 0.85},
            {"src": "Paris", "dst": "Arc de Triomphe", "relation": "包含", "confidence": 0.85},
            {"src": "Paris", "dst": "Notre-Dame", "relation": "包含", "confidence": 0.85},
            {"src": "Paris", "dst": "Luxor Obelisk", "relation": "包含", "confidence": 0.8},
            {"src": "Paris", "dst": "Lutetia Arena", "relation": "包含", "confidence": 0.8},
            {"src": "Paris", "dst": "Medieval Quarters", "relation": "包含", "confidence": 0.8},
            {"src": "thought", "dst": "reality", "relation": "塑造", "confidence": 0.8},
        ],
    },
    # ── #16 en 3.2「迁流的盛宴」法兰西特快：阿黛尔·塔文尼埃 ──
    "3642207c78778d8b": {
        "entities": [
            {"name": "Adele", "type": "角色", "aliases": ["阿黛尔", "Adèle Tavernier", "阿黛尔·塔文尼埃"]},
            {"name": "Les Taverniers", "type": "组织", "aliases": ["塔文尼埃家族", "Tavernier family", "Tavernier"]},
            {"name": "French blue", "type": "物品", "aliases": ["法兰西之蓝", "法国蓝", "French Blue"]},
            {"name": "Bourbon", "type": "组织", "aliases": ["波旁家族"]},
            {"name": "arcane skill", "type": "概念", "aliases": ["神秘术", "秘技"]},
            {"name": "crystal", "type": "物品", "aliases": ["水晶"]},
            {"name": "fire", "type": "概念", "aliases": ["火焰"]},
        ],
        "relations": [
            {"src": "Adele", "dst": "Les Taverniers", "relation": "隶属", "confidence": 0.9},
            {"src": "Adele", "dst": "arcane skill", "relation": "使用", "confidence": 0.85},
            {"src": "Les Taverniers", "dst": "French blue", "relation": "寻回", "confidence": 0.85},
            {"src": "Bourbon", "dst": "French blue", "relation": "持有", "confidence": 0.85},
            {"src": "Adele", "dst": "crystal", "relation": "施术", "confidence": 0.7},
            {"src": "fire", "dst": "crystal", "relation": "揭示本质", "confidence": 0.7},
        ],
    },
    # ── #17 en 3.2「迁流的盛宴」法兰西特快：塔文尼埃少女的预言 ──
    "cbd85d3c306f0f3a": {
        "entities": [
            {"name": "Adele", "type": "角色", "aliases": ["阿黛尔", "tavernier girl", "塔文尼埃少女"]},
            {"name": "arcane skill", "type": "概念", "aliases": ["神秘术", "秘技"]},
            {"name": "destiny", "type": "概念", "aliases": ["命运", "宿命"]},
        ],
        "relations": [
            {"src": "Adele", "dst": "arcane skill", "relation": "使用", "confidence": 0.8},
            {"src": "Adele", "dst": "destiny", "relation": "遭遇", "confidence": 0.75},
            {"src": "arcane skill", "dst": "Adele", "relation": "预示", "confidence": 0.6},
        ],
    },
    # ── #18 en 3.2「迁流的盛宴」法兰西之蓝：灵界显化与努玛 ──
    "3ff8f4686693eda9": {
        "entities": [
            {"name": "spiritual world", "type": "地点", "aliases": ["灵界", "精神世界"]},
            {"name": "Numa", "type": "概念", "aliases": ["努玛", "Pnuma"]},
            {"name": "diamond", "type": "物品", "aliases": ["钻石"]},
            {"name": "world of matter", "type": "概念", "aliases": ["物质世界"]},
            {"name": "dream", "type": "概念", "aliases": ["梦", "梦境"]},
        ],
        "relations": [
            {"src": "diamond", "dst": "spiritual world", "relation": "存在于", "confidence": 0.7},
            {"src": "Numa", "dst": "world of matter", "relation": "显化", "confidence": 0.7},
            {"src": "diamond", "dst": "dream", "relation": "显现于", "confidence": 0.7},
            {"src": "diamond", "dst": "Numa", "relation": "借由重现", "confidence": 0.6},
        ],
    },
}


def main() -> int:
    ap = argparse.ArgumentParser(description="补齐 18 个失败剧情块的抽取缓存")
    ap.add_argument("--character", default="wu_ming_zhe")
    ap.add_argument("--force", action="store_true", help="已存在也覆盖写")
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
    print(f"[apply] 写入 {written} 条，跳过（已存在）{skipped} 条 → {cache_dir}")
    print(f"[apply] 缓存总数 {len(list(cache_dir.glob('*.json')))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
