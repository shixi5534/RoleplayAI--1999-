# -*- coding: utf-8 -*-
"""未抽取剧情块补抽 · 第 24 批（backfill2 batch_14，20 块，全部含剧情）。

用法：
  python scripts/apply_missing_p24.py            # 预演（悬空+落地自检）
  python scripts/apply_missing_p24.py --apply    # 写盘
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

# 本批 20 块均含剧情内容，无纯数值/UI 空块。
NOOP_ADD: list[str] = []

RESULTS: dict[str, dict] = {
    # 1) 星之眼无罪辩护 · 波拉比与本耶普、叮当快报、航测局
    "def23487475db125": {
        "entities": [
            {"name": "波拉比", "type": "角色", "aliases": []},
            {"name": "本耶普", "type": "角色", "aliases": []},
            {"name": "星之眼", "type": "角色", "aliases": []},
            {"name": "沙丝绒", "type": "角色", "aliases": []},
            {"name": "宽檐帽", "type": "角色", "aliases": []},
            {"name": "叮当快报", "type": "物品", "aliases": ["《叮当快报》"]},
            {"name": "航测局", "type": "组织", "aliases": []},
        ],
        "relations": [
            {"src": "波拉比", "dst": "本耶普", "relation": "互动", "confidence": 0.8},
            {"src": "沙丝绒", "dst": "叮当快报", "relation": "阅读", "confidence": 0.8},
            {"src": "星之眼", "dst": "航测局", "relation": "归咎", "confidence": 0.7},
        ],
    },
    # 2) 追思弥撒 · 西杰克逊大道宗座圣殿与格雷克一家
    "915fa6f33865f9e1": {
        "entities": [
            {"name": "西杰克逊大道", "type": "地点", "aliases": []},
            {"name": "宗座圣殿", "type": "地点", "aliases": []},
            {"name": "黑袍妇女", "type": "角色", "aliases": []},
            {"name": "格雷克一家", "type": "角色", "aliases": ["格雷克先生"]},
            {"name": "斯奈德", "type": "角色", "aliases": []},
            {"name": "追思弥撒", "type": "事件", "aliases": []},
            {"name": "教堂", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "格雷克一家", "dst": "追思弥撒", "relation": "参加", "confidence": 0.8},
            {"src": "斯奈德", "dst": "格雷克一家", "relation": "缺席", "confidence": 0.7},
            {"src": "追思弥撒", "dst": "宗座圣殿", "relation": "举行于", "confidence": 0.7},
        ],
    },
    # 3) 梦境独白 · 潘朵拉、草履虫、驼背巨鱼与开放式三明治
    "b5b86d6fd0f46f6c": {
        "entities": [
            {"name": "潘朵拉", "type": "角色", "aliases": []},
            {"name": "草履虫", "type": "概念", "aliases": []},
            {"name": "驼背巨鱼", "type": "概念", "aliases": []},
            {"name": "开放式三明治", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "草履虫", "dst": "潘朵拉", "relation": "试图迫使屈服", "confidence": 0.7},
        ],
    },
    # 4) 白袍子与梅斯梅尔 · 拉普拉斯、学者、玻璃笔、苹果
    "eea4e68e86d883cc": {
        "entities": [
            {"name": "白袍子", "type": "角色", "aliases": []},
            {"name": "梅斯梅尔", "type": "角色", "aliases": []},
            {"name": "拉普拉斯", "type": "角色", "aliases": []},
            {"name": "学者", "type": "概念", "aliases": []},
            {"name": "神秘学家", "type": "概念", "aliases": []},
            {"name": "玻璃笔", "type": "物品", "aliases": []},
            {"name": "苹果", "type": "物品", "aliases": ["会跳舞的苹果"]},
        ],
        "relations": [
            {"src": "拉普拉斯", "dst": "学者", "relation": "合作", "confidence": 0.8},
            {"src": "梅斯梅尔", "dst": "白袍子", "relation": "属于", "confidence": 0.7},
            {"src": "梅斯梅尔", "dst": "神秘学家", "relation": "属于", "confidence": 0.7},
        ],
    },
    # 5) 梅斯梅尔们治疗癔症 · 儿童劳动保护法与聚酯纤维
    "37e600f3659385e9": {
        "entities": [
            {"name": "儿童劳动保护法", "type": "概念", "aliases": []},
            {"name": "梅斯梅尔们", "type": "角色", "aliases": []},
            {"name": "神秘学家", "type": "概念", "aliases": []},
            {"name": "人类", "type": "概念", "aliases": []},
            {"name": "癔症", "type": "概念", "aliases": []},
            {"name": "聚酯纤维", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "梅斯梅尔们", "dst": "癔症", "relation": "治疗", "confidence": 0.8},
            {"src": "神秘学家", "dst": "人类", "relation": "弱于", "confidence": 0.7},
        ],
    },
    # 6) 圣马可咖啡馆 · 萨赫蛋糕、20世纪、黄金时代、精神医师
    "dac7c2a4ecaf1ed8": {
        "entities": [
            {"name": "圣马可", "type": "地点", "aliases": []},
            {"name": "萨赫蛋糕", "type": "物品", "aliases": []},
            {"name": "20世纪", "type": "时间", "aliases": []},
            {"name": "黄金时代", "type": "概念", "aliases": []},
            {"name": "精神医师", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "精神医师", "dst": "圣马可", "relation": "现身于", "confidence": 0.7},
            {"src": "黄金时代", "dst": "20世纪", "relation": "处于", "confidence": 0.7},
        ],
    },
    # 7) 尺规与辩论赛 · 长棍面包、量器、神秘学、助手
    "f1bba46004143c63": {
        "entities": [
            {"name": "尺规", "type": "物品", "aliases": []},
            {"name": "长棍面包", "type": "物品", "aliases": []},
            {"name": "量器", "type": "物品", "aliases": []},
            {"name": "辩论赛", "type": "事件", "aliases": []},
            {"name": "神秘学", "type": "概念", "aliases": []},
            {"name": "助手", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "辩论赛", "dst": "助手", "relation": "使困扰", "confidence": 0.7},
        ],
    },
    # 8) 三条路寓言 · 冥府、女妖、幽微、林间小路、大道
    "356f1efa12c16d1d": {
        "entities": [
            {"name": "冥府", "type": "地点", "aliases": []},
            {"name": "女妖", "type": "角色", "aliases": []},
            {"name": "幽微", "type": "概念", "aliases": []},
            {"name": "林间小路", "type": "地点", "aliases": []},
            {"name": "大道", "type": "地点", "aliases": []},
            {"name": "童话故事", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "女妖", "dst": "冥府", "relation": "位于", "confidence": 0.7},
        ],
    },
    # 9) 数值/技能页尾部对白 · 死人莱格斯的复活
    "6506c7c7d168317a": {
        "entities": [
            {"name": "莱格斯", "type": "角色", "aliases": []},
        ],
        "relations": [],
    },
    # 10) 澳洲水怪风味 · 明星饲养下水道军队、水怪以谣言为食
    "bb07c14477e2869a": {
        "entities": [
            {"name": "水怪", "type": "角色", "aliases": []},
            {"name": "明星", "type": "角色", "aliases": []},
            {"name": "小巷", "type": "地点", "aliases": []},
            {"name": "下水道军队", "type": "组织", "aliases": []},
            {"name": "谣言", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "明星", "dst": "下水道军队", "relation": "饲养", "confidence": 0.8},
            {"src": "明星", "dst": "小巷", "relation": "躲藏于", "confidence": 0.7},
            {"src": "水怪", "dst": "谣言", "relation": "以之为食", "confidence": 0.8},
        ],
    },
    # 11) 文学战场 · 布宜诺斯艾利斯分部交接报告、军令、诗人、诗篇
    "4347a6a4e037ea00": {
        "entities": [
            {"name": "战争", "type": "事件", "aliases": []},
            {"name": "作家", "type": "角色", "aliases": []},
            {"name": "士兵", "type": "角色", "aliases": []},
            {"name": "军令", "type": "概念", "aliases": []},
            {"name": "诗人", "type": "角色", "aliases": []},
            {"name": "布宜诺斯艾利斯分部交接报告", "type": "物品", "aliases": ["《布宜诺斯艾利斯分部交接报告》"]},
            {"name": "士官长", "type": "角色", "aliases": []},
            {"name": "诗篇", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "士官长", "dst": "军令", "relation": "发出", "confidence": 0.8},
            {"src": "士兵", "dst": "军令", "relation": "遵从", "confidence": 0.7},
            {"src": "诗人", "dst": "诗篇", "relation": "创作", "confidence": 0.7},
        ],
    },
    # 12) 文学大爆炸 · 卡门卡洛斯、哥伦布、富恩特斯、科塔萨尔、马里奥加博
    "d56d06bf18c45454": {
        "entities": [
            {"name": "文学大爆炸", "type": "事件", "aliases": []},
            {"name": "西班牙", "type": "地点", "aliases": []},
            {"name": "加泰罗尼亚", "type": "地点", "aliases": []},
            {"name": "拉丁美洲", "type": "地点", "aliases": []},
            {"name": "卡门", "type": "角色", "aliases": []},
            {"name": "卡洛斯", "type": "角色", "aliases": []},
            {"name": "哥伦布", "type": "角色", "aliases": ["“哥伦布”"]},
            {"name": "猪尾巴男孩", "type": "角色", "aliases": []},
            {"name": "富恩特斯", "type": "角色", "aliases": []},
            {"name": "科塔萨尔", "type": "角色", "aliases": []},
            {"name": "马里奥", "type": "角色", "aliases": []},
            {"name": "加博", "type": "角色", "aliases": []},
            {"name": "出版社", "type": "组织", "aliases": []},
            {"name": "军事学院", "type": "组织", "aliases": []},
            {"name": "新美洲文学", "type": "概念", "aliases": []},
            {"name": "外交官", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "卡门", "dst": "卡洛斯", "relation": "共同策划", "confidence": 0.8},
            {"src": "哥伦布", "dst": "西班牙", "relation": "象征", "confidence": 0.7},
            {"src": "马里奥", "dst": "加博", "relation": "互通书信", "confidence": 0.8},
            {"src": "富恩特斯", "dst": "外交官", "relation": "是", "confidence": 0.8},
        ],
    },
    # 13) 芝诺叛逃部队动向 · 科马拉监狱、重塑之手、司辰小队、乌斯怀亚
    "af924ca5be5cdb20": {
        "entities": [
            {"name": "芝诺叛逃部队动向报告", "type": "物品", "aliases": ["《芝诺叛逃部队动向报告》"]},
            {"name": "芝诺叛逃部队", "type": "组织", "aliases": []},
            {"name": "塔", "type": "角色", "aliases": []},
            {"name": "司辰小队", "type": "组织", "aliases": []},
            {"name": "科马拉监狱", "type": "地点", "aliases": []},
            {"name": "神秘学家", "type": "概念", "aliases": []},
            {"name": "重塑之手", "type": "组织", "aliases": []},
            {"name": "乌斯怀亚", "type": "地点", "aliases": []},
            {"name": "骰子", "type": "物品", "aliases": []},
            {"name": "命运", "type": "概念", "aliases": []},
            {"name": "巴比伦人", "type": "角色", "aliases": []},
            {"name": "历史学家", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "芝诺叛逃部队", "dst": "科马拉监狱", "relation": "涉足", "confidence": 0.8},
            {"src": "芝诺叛逃部队", "dst": "重塑之手", "relation": "涉及", "confidence": 0.9},
            {"src": "芝诺叛逃部队", "dst": "乌斯怀亚", "relation": "撤离于", "confidence": 0.8},
            {"src": "科马拉监狱", "dst": "神秘学家", "relation": "关押", "confidence": 0.8},
            {"src": "司辰小队", "dst": "芝诺叛逃部队", "relation": "提供情报", "confidence": 0.7},
        ],
    },
    # 14) 文学兵役与会作家 · 塔德奥、埃玛·宗兹、阿莱夫、阿威罗伊、马克沁机枪
    "89d5963d7c192807": {
        "entities": [
            {"name": "塔德奥", "type": "角色", "aliases": []},
            {"name": "埃玛·宗兹", "type": "角色", "aliases": []},
            {"name": "阿莱夫", "type": "角色", "aliases": []},
            {"name": "阿威罗伊", "type": "角色", "aliases": []},
            {"name": "文学兵役", "type": "事件", "aliases": []},
            {"name": "作家", "type": "角色", "aliases": []},
            {"name": "马克沁机枪", "type": "物品", "aliases": []},
            {"name": "布宜诺斯艾利斯", "type": "地点", "aliases": []},
            {"name": "智利", "type": "地点", "aliases": []},
            {"name": "拉丁美洲", "type": "地点", "aliases": []},
            {"name": "意见领袖", "type": "角色", "aliases": []},
            {"name": "诗人", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "作家", "dst": "布宜诺斯艾利斯", "relation": "流浪至", "confidence": 0.7},
            {"src": "作家", "dst": "智利", "relation": "来自", "confidence": 0.7},
            {"src": "作家", "dst": "意见领袖", "relation": "是", "confidence": 0.7},
        ],
    },
    # 15) 疯子抢滩登陆 · 上将捧疯子为神、加西亚倚沉船、文明人交战疯子
    "78e91f89147d8ff4": {
        "entities": [
            {"name": "疯子", "type": "角色", "aliases": []},
            {"name": "上将", "type": "角色", "aliases": []},
            {"name": "知识", "type": "概念", "aliases": []},
            {"name": "加西亚", "type": "角色", "aliases": ["“加西亚”"]},
            {"name": "沉船", "type": "地点", "aliases": []},
            {"name": "指挥部", "type": "地点", "aliases": []},
            {"name": "文明人", "type": "角色", "aliases": []},
            {"name": "疫病", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "上将", "dst": "疯子", "relation": "捧为神", "confidence": 0.7},
            {"src": "加西亚", "dst": "沉船", "relation": "倚靠于", "confidence": 0.8},
            {"src": "加西亚", "dst": "指挥部", "relation": "身处", "confidence": 0.8},
            {"src": "文明人", "dst": "疯子", "relation": "交战", "confidence": 0.7},
            {"src": "知识", "dst": "疯子", "relation": "使人发疯", "confidence": 0.8},
        ],
    },
    # 16) 基金会立法辩论 · 白色石屋、第一防线学校、占卜初学者、水晶球
    "d0e448ed128125ca": {
        "entities": [
            {"name": "白色石屋", "type": "地点", "aliases": []},
            {"name": "基金会", "type": "组织", "aliases": []},
            {"name": "第一防线学校", "type": "组织", "aliases": []},
            {"name": "神秘学家", "type": "概念", "aliases": []},
            {"name": "人类", "type": "概念", "aliases": []},
            {"name": "无名垂钓者", "type": "角色", "aliases": ["“无名垂钓者”"]},
            {"name": "占卜初学者", "type": "角色", "aliases": []},
            {"name": "水晶球", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "基金会", "dst": "第一防线学校", "relation": "下属", "confidence": 0.7},
            {"src": "基金会", "dst": "白色石屋", "relation": "包含", "confidence": 0.7},
            {"src": "占卜初学者", "dst": "水晶球", "relation": "使用", "confidence": 0.7},
        ],
    },
    # 17) 灰调蓝的寓意 · 维尔汀、蓝礼帽、黑眼镜、水晶球、仿钻
    "b87765b146196a8b": {
        "entities": [
            {"name": "灰调蓝", "type": "角色", "aliases": []},
            {"name": "预言", "type": "概念", "aliases": []},
            {"name": "水晶球", "type": "物品", "aliases": []},
            {"name": "维尔汀", "type": "角色", "aliases": []},
            {"name": "蓝礼帽", "type": "角色", "aliases": []},
            {"name": "黑眼镜", "type": "角色", "aliases": []},
            {"name": "仿钻", "type": "物品", "aliases": []},
            {"name": "小鸭子", "type": "角色", "aliases": []},
            {"name": "基金会", "type": "组织", "aliases": []},
        ],
        "relations": [
            {"src": "蓝礼帽", "dst": "黑眼镜", "relation": "注视", "confidence": 0.8},
            {"src": "黑眼镜", "dst": "蓝礼帽", "relation": "应允", "confidence": 0.8},
            {"src": "水晶球", "dst": "预言", "relation": "显示", "confidence": 0.7},
        ],
    },
    # 18) 附件信件致维尔汀 · 伊万·伊万诺维奇·布列科夫、伊万伊戈尔、芝诺骑兵军
    "50c99d8fdfed7fa3": {
        "entities": [
            {"name": "维尔汀", "type": "角色", "aliases": []},
            {"name": "基金会", "type": "组织", "aliases": []},
            {"name": "伊万·伊万诺维奇·布列科夫", "type": "角色", "aliases": ["伊万·伊万诺维奇·布列科夫军长"]},
            {"name": "伊万", "type": "角色", "aliases": []},
            {"name": "伊戈尔", "type": "角色", "aliases": []},
            {"name": "芝诺骑兵军", "type": "组织", "aliases": []},
            {"name": "顿河", "type": "地点", "aliases": []},
            {"name": "东线", "type": "地点", "aliases": []},
            {"name": "信件", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "伊万", "dst": "伊戈尔", "relation": "有交情", "confidence": 0.8},
            {"src": "伊万", "dst": "顿河", "relation": "出身于", "confidence": 0.7},
            {"src": "伊戈尔", "dst": "顿河", "relation": "出身于", "confidence": 0.7},
            {"src": "维尔汀", "dst": "东线", "relation": "前往", "confidence": 0.7},
            {"src": "信件", "dst": "维尔汀", "relation": "致", "confidence": 0.8},
            {"src": "伊万·伊万诺维奇·布列科夫", "dst": "芝诺骑兵军", "relation": "关联", "confidence": 0.7},
        ],
    },
    # 19) 军长伊万与斯捷尔诺娃 · 黑袍子白袍子扭打、指挥部
    "4a829ce65a516095": {
        "entities": [
            {"name": "军长伊万", "type": "角色", "aliases": []},
            {"name": "斯捷尔诺娃", "type": "角色", "aliases": []},
            {"name": "黑袍子", "type": "角色", "aliases": []},
            {"name": "白袍子", "type": "角色", "aliases": []},
            {"name": "匪军", "type": "组织", "aliases": []},
            {"name": "指挥部", "type": "地点", "aliases": []},
            {"name": "安眠", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "军长伊万", "dst": "斯捷尔诺娃", "relation": "下令", "confidence": 0.8},
            {"src": "斯捷尔诺娃", "dst": "军长伊万", "relation": "服从", "confidence": 0.8},
            {"src": "白袍子", "dst": "黑袍子", "relation": "扭打", "confidence": 0.7},
            {"src": "军长伊万", "dst": "指挥部", "relation": "驻扎于", "confidence": 0.7},
        ],
    },
    # 20) 叶尔莫莱与梅蕾尔 · 刻雷乌斯、乌鸫、跟踪药剂、实验室、仓库
    "11c4871f9e2b6723": {
        "entities": [
            {"name": "叶尔莫莱", "type": "角色", "aliases": []},
            {"name": "梅蕾尔", "type": "角色", "aliases": []},
            {"name": "刻雷乌斯", "type": "角色", "aliases": []},
            {"name": "乌鸫", "type": "角色", "aliases": ["“乌鸫”"]},
            {"name": "跟踪药剂", "type": "物品", "aliases": []},
            {"name": "实验室", "type": "地点", "aliases": []},
            {"name": "仓库", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "叶尔莫莱", "dst": "梅蕾尔", "relation": "告知", "confidence": 0.8},
            {"src": "刻雷乌斯", "dst": "跟踪药剂", "relation": "获取", "confidence": 0.7},
            {"src": "梅蕾尔", "dst": "乌鸫", "relation": "代号为", "confidence": 0.7},
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
    empty = sum(1 for d in RESULTS.values() if not (d.get("entities") or d.get("relations")))
    print(f"[validate] 块 {len(RESULTS)}（NOOP {empty}），悬空 {n}，未落地 {m}")
    print(f"[stats] 非空块 {nonempty}，实体 {total_e}，关系 {total_r}，空块 {empty}")

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
    print(f"[apply-missing-p24] 写入 {len(RESULTS)} 条，NOOP +{len(NOOP_ADD)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
