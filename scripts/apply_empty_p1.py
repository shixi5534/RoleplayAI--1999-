# -*- coding: utf-8 -*-
"""补抽 408 块空抽取中的第 1 批（67 块，云端人工抽取）。

与 apply_failed_chunks_18.py 同一模式：直接写 plot_cache/<cid>/<hash>.json，
随后 --build-graph 从缓存回放（零 LLM 调用）。

判定原则（比本地 7B 更保守）：
- 只抽文中**明确出现**的实体，不靠背景知识补全；
- 通用词（foundation=地基、target=目标、mask=面具）不映射为专有实体；
- 战斗语音行 / 无专名的日常对白 → 判为「确认无内容」，进 NOOP 集合不写缓存。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from roleplay.config import get_settings  # noqa: E402

# 人工确认「无有效内容」：战斗语音行 / 纯日常对白 / 无专名
NOOP: list[str] = [
    "44ebd3bf57c3d315",  # 战斗语音行（Aim and shoot / Charging / Target confirmed）
    "bf0e9c29c20b66bb",  # 德语一战士兵对白，无专名
    "3771eb52cc1b8bde",  # 战斗语音行（Mirage / Charging / mint oil）
    "7bf977edf5ab3c84",  # 战场对白（masks / flank），无专名
    "bbe0a6ac9fa42b99",  # 战斗语音行（Target confirmed / data segment）
]

RESULTS: dict[str, dict] = {
    "909b7ee918682757": {
        "entities": [
            {"name": "APPLe", "type": "角色", "aliases": ["Apple", "苹果"]},
            {"name": "苏芙比", "type": "角色", "aliases": ["Sotheby", "Miss Sotheby"]},
            {"name": "达芬奇", "type": "角色",
             "aliases": ["Leonardo", "Mr. Leonardo", "Leonardo da Vinci"]},
            {"name": "Uccello", "type": "角色", "aliases": ["乌切洛"]},
            {"name": "睡眠气体", "type": "物品", "aliases": ["sleeping gas"]},
        ],
        "relations": [
            {"src": "APPLe", "dst": "睡眠气体", "relation": "识别", "confidence": 0.9},
            {"src": "APPLe", "dst": "苏芙比", "relation": "示警", "confidence": 0.9},
            {"src": "APPLe", "dst": "达芬奇", "relation": "呼唤", "confidence": 0.8},
            {"src": "达芬奇", "dst": "Uccello", "relation": "描述", "confidence": 0.6},
        ],
    },
    "401064e95a93aa9d": {
        "entities": [
            {"name": "北方哨歌", "type": "角色",
             "aliases": ["Windsong", "Winsong", "Miss Winsong", "Comrade Winsong"]},
            {"name": "远东分部", "type": "组织", "aliases": ["Far East branch"]},
            {"name": "向日葵卫兵", "type": "概念", "aliases": ["sunflower guards"]},
        ],
        "relations": [
            {"src": "北方哨歌", "dst": "远东分部", "relation": "出差前往", "confidence": 0.9},
            {"src": "向日葵卫兵", "dst": "北方哨歌", "relation": "转交", "confidence": 0.7},
        ],
    },
    "2ca462c45e22d01f": {
        "entities": [
            {"name": "帝国首相", "type": "角色", "aliases": ["Chancellor", "首相"]},
            {"name": "帝国议会", "type": "组织", "aliases": ["Reichstag"]},
            {"name": "欧洲", "type": "地点", "aliases": ["Europe"]},
            {"name": "蒙佩", "type": "地点", "aliases": ["Montpey"]},
            {"name": "停战协定", "type": "事件", "aliases": ["armistice"]},
            {"name": "和平主义政党", "type": "组织", "aliases": ["pacifist political parties"]},
        ],
        "relations": [
            {"src": "帝国首相", "dst": "帝国议会", "relation": "协同", "confidence": 0.8},
            {"src": "和平主义政党", "dst": "停战协定", "relation": "签署", "confidence": 0.8},
            {"src": "停战协定", "dst": "蒙佩", "relation": "签署于", "confidence": 0.9},
            {"src": "停战协定", "dst": "欧洲", "relation": "带来和平", "confidence": 0.7},
        ],
    },
    "52f3eebd9d5cf902": {
        "entities": [
            {"name": "阿尼尔", "type": "角色", "aliases": ["Anil"]},
            {"name": "胡亚雷斯先生", "type": "角色", "aliases": ["Mr. Juarez", "Juarez"]},
            {"name": "迪亚戈的店", "type": "地点", "aliases": ["Diago's"]},
            {"name": "罗马区", "type": "地点", "aliases": ["La Roma"]},
            {"name": "克里斯蒂娜", "type": "角色", "aliases": ["Christina"]},
            {"name": "万寿菊", "type": "物品", "aliases": ["marigolds"]},
            {"name": "家族墓穴", "type": "地点", "aliases": ["family tomb"]},
        ],
        "relations": [
            {"src": "胡亚雷斯先生", "dst": "阿尼尔", "relation": "委托", "confidence": 0.9},
            {"src": "胡亚雷斯先生", "dst": "家族墓穴", "relation": "委托重绘", "confidence": 0.9},
            {"src": "胡亚雷斯先生", "dst": "罗马区", "relation": "位于", "confidence": 0.7},
            {"src": "阿尼尔", "dst": "迪亚戈的店", "relation": "赶往", "confidence": 0.8},
            {"src": "阿尼尔", "dst": "克里斯蒂娜", "relation": "拜访", "confidence": 0.6},
        ],
    },
    "8267c113d7c75cb8": {
        "entities": [
            {"name": "飞行女巫", "type": "组织", "aliases": ["flying witch", "Flying Witches"]},
            {"name": "格鲁托夫匪帮", "type": "组织", "aliases": ["Grutov", "Grutov's bandits"]},
            {"name": "骑兵队", "type": "组织", "aliases": ["cavalry"]},
            {"name": "玛纳", "type": "概念", "aliases": ["manas"]},
            {"name": "传送仪式", "type": "事件", "aliases": ["teleport ritual"]},
            {"name": "阿尔法小队", "type": "组织", "aliases": ["The Alphas"]},
            {"name": "仪式现场", "type": "地点", "aliases": ["ritual site"]},
            {"name": "村庄", "type": "地点", "aliases": ["village"]},
        ],
        "relations": [
            {"src": "骑兵队", "dst": "格鲁托夫匪帮", "relation": "追击", "confidence": 0.9},
            {"src": "格鲁托夫匪帮", "dst": "传送仪式", "relation": "使用", "confidence": 0.7},
            {"src": "传送仪式", "dst": "玛纳", "relation": "消耗", "confidence": 0.7},
            {"src": "阿尔法小队", "dst": "仪式现场", "relation": "搜寻", "confidence": 0.8},
            {"src": "仪式现场", "dst": "村庄", "relation": "位于", "confidence": 0.8},
        ],
    },
    "3c35e8001ce1a8a0": {
        "entities": [
            {"name": "远旅", "type": "角色", "aliases": ["Voyager", "Miss Voyager"]},
            {"name": "芭卡洛儿", "type": "角色",
             "aliases": ["Barcarola", "Miss Barcarola"]},
            {"name": "水上竞技会", "type": "事件", "aliases": ["Aquatic Games"]},
            {"name": "海兽", "type": "概念", "aliases": ["sea beast", "wild sea beast"]},
        ],
        "relations": [
            {"src": "远旅", "dst": "芭卡洛儿", "relation": "合作演出", "confidence": 0.9},
            {"src": "远旅", "dst": "水上竞技会", "relation": "参加", "confidence": 0.8},
            {"src": "芭卡洛儿", "dst": "水上竞技会", "relation": "参加", "confidence": 0.8},
            {"src": "水上竞技会", "dst": "海兽", "relation": "倚仗", "confidence": 0.8},
        ],
    },
    "af9c781b9f214f03": {
        "entities": [
            {"name": "诺谛卡", "type": "角色", "aliases": ["Nautica", "Nautika"]},
            {"name": "船长", "type": "角色", "aliases": ["Captain"]},
            {"name": "圣所", "type": "地点", "aliases": ["sanctuary"]},
            {"name": "洪水", "type": "事件", "aliases": ["the flood"]},
            {"name": "世界终结", "type": "概念", "aliases": ["the end of this world"]},
            {"name": "M.R.E", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "船长", "dst": "诺谛卡", "relation": "呼叫", "confidence": 0.8},
            {"src": "圣所", "dst": "诺谛卡", "relation": "崩塌威胁", "confidence": 0.9},
            {"src": "船长", "dst": "M.R.E", "relation": "持有", "confidence": 0.7},
            {"src": "洪水", "dst": "世界终结", "relation": "象征", "confidence": 0.7},
        ],
    },
    "26f7e8e82f1a4f1e": {
        "entities": [
            {"name": "阿格尼丝", "type": "角色", "aliases": ["Agnes"]},
            {"name": "玛丽", "type": "角色", "aliases": ["Marie"]},
            {"name": "地狱之门", "type": "概念", "aliases": ["gates of hell"]},
        ],
        "relations": [
            {"src": "阿格尼丝", "dst": "玛丽", "relation": "呼唤", "confidence": 0.9},
            {"src": "玛丽", "dst": "地狱之门", "relation": "走向", "confidence": 0.8},
        ],
    },
    "093c0b406d16c27f": {
        "entities": [
            {"name": "暴雨", "type": "事件", "aliases": ["Storm", "The Storm"]},
            {"name": "拉普拉斯", "type": "组织", "aliases": ["Laplace", "LSCC"]},
            {"name": "皮亚塞克", "type": "地点", "aliases": ["Piaseck"]},
            {"name": "疗养中心", "type": "组织", "aliases": ["care center"]},
            {"name": "冷周六", "type": "角色", "aliases": ["Hissabeth", "Hissebeth"]},
        ],
        "relations": [
            {"src": "拉普拉斯", "dst": "皮亚塞克", "relation": "报到", "confidence": 0.8},
            {"src": "拉普拉斯", "dst": "疗养中心", "relation": "安排入驻", "confidence": 0.9},
            {"src": "暴雨", "dst": "拉普拉斯", "relation": "引发休假", "confidence": 0.7},
            {"src": "冷周六", "dst": "暴雨", "relation": "伺机而动", "confidence": 0.6},
        ],
    },
    "62a9ef41a53cf43f": {
        "entities": [
            {"name": "旅行者一号", "type": "物品", "aliases": ["Voyager 1", "Voyager"]},
            {"name": "金唱片", "type": "物品", "aliases": ["golden records", "Golden Records"]},
            {"name": "月球", "type": "概念", "aliases": ["moon"]},
            {"name": "落星", "type": "事件", "aliases": []},
        ],
        "relations": [
            {"src": "旅行者一号", "dst": "金唱片", "relation": "携带", "confidence": 0.9},
            {"src": "落星", "dst": "月球", "relation": "观测参照", "confidence": 0.6},
        ],
    },
    "0ac91f874f16ecdb": {
        "entities": [
            {"name": "暴雨", "type": "事件", "aliases": ["Storm", "The Storm"]},
            {"name": "零号仓库", "type": "地点", "aliases": ["warehouse zero"]},
            {"name": "总部", "type": "地点", "aliases": ["headquarters", "Headquarters"]},
            {"name": "芝诺军备学院", "type": "组织", "aliases": ["Xeno", "Zeno"]},
            {"name": "加密电报", "type": "物品", "aliases": ["encrypted telegrams"]},
        ],
        "relations": [
            {"src": "总部", "dst": "零号仓库", "relation": "封存机密", "confidence": 0.9},
            {"src": "芝诺军备学院", "dst": "加密电报", "relation": "使用", "confidence": 0.8},
            {"src": "零号仓库", "dst": "暴雨", "relation": "存放相关档案", "confidence": 0.6},
        ],
    },
    "6fc39b33578ac71a": {
        "entities": [
            {"name": "壁画运动", "type": "概念", "aliases": ["muralism movement"]},
            {"name": "迭戈", "type": "角色", "aliases": ["Diego"]},
            {"name": "火地岛", "type": "地点", "aliases": ["Tierra del Fuego"]},
            {"name": "墨西哥先驱报", "type": "组织",
             "aliases": ["El Seminario Heraldo de Mexico"]},
            {"name": "外交官", "type": "角色", "aliases": ["foreign diplomat", "Diplomat"]},
        ],
        "relations": [
            {"src": "迭戈", "dst": "火地岛", "relation": "前往", "confidence": 0.8},
            {"src": "墨西哥先驱报", "dst": "外交官", "relation": "专访", "confidence": 0.9},
            {"src": "迭戈", "dst": "壁画运动", "relation": "关注", "confidence": 0.7},
        ],
    },
    "ec7e73eeb4e5bc03": {
        "entities": [
            {"name": "血肉之子", "type": "概念", "aliases": ["children of flesh"]},
            {"name": "圣所大门", "type": "地点", "aliases": ["sanctuary gate"]},
            {"name": "母神", "type": "角色", "aliases": ["Mother Spirit", "Mother"]},
            {"name": "终末仪式", "type": "事件", "aliases": ["final ritual"]},
            {"name": "潮汐", "type": "概念", "aliases": ["tides"]},
        ],
        "relations": [
            {"src": "圣所大门", "dst": "终末仪式", "relation": "开启", "confidence": 0.9},
            {"src": "母神", "dst": "终末仪式", "relation": "主持", "confidence": 0.8},
            {"src": "母神", "dst": "潮汐", "relation": "化身", "confidence": 0.7},
            {"src": "血肉之子", "dst": "终末仪式", "relation": "见证", "confidence": 0.8},
        ],
    },
    "8f4ae08a7193f4bf": {
        "entities": [
            {"name": "飞行女巫", "type": "组织", "aliases": ["Flying Witches", "flying witch"]},
            {"name": "Xenu", "type": "角色", "aliases": []},
            {"name": "骑兵站", "type": "地点", "aliases": ["calvary station"]},
            {"name": "提琴蟹", "type": "概念", "aliases": ["Fiddler Crab"]},
        ],
        "relations": [
            {"src": "Xenu", "dst": "飞行女巫", "relation": "重组", "confidence": 0.7},
        ],
    },
    "68e891be3bc9056e": {
        "entities": [
            {"name": "鸽子雕塑", "type": "物品", "aliases": ["dove sculptures"]},
            {"name": "图书馆", "type": "地点", "aliases": ["library"]},
            {"name": "暴雨", "type": "事件", "aliases": ["Storm", "The Storm"]},
            {"name": "怪物", "type": "概念", "aliases": ["monsters", "Monsters"]},
        ],
        "relations": [
            {"src": "鸽子雕塑", "dst": "图书馆", "relation": "送往", "confidence": 0.9},
            {"src": "暴雨", "dst": "怪物", "relation": "伴随", "confidence": 0.6},
        ],
    },
    "161490bd162acd12": {
        "entities": [
            {"name": "苏芙比", "type": "角色", "aliases": ["Sotheby", "Miss Sotheby"]},
            {"name": "提丰", "type": "角色", "aliases": ["Typhon"]},
            {"name": "但丁诗集", "type": "物品", "aliases": ["Dante's poetry"]},
            {"name": "书商", "type": "角色", "aliases": ["book merchant"]},
            {"name": "拉丁语", "type": "概念", "aliases": ["Latin"]},
        ],
        "relations": [
            {"src": "苏芙比", "dst": "拉丁语", "relation": "练习", "confidence": 0.9},
            {"src": "书商", "dst": "但丁诗集", "relation": "出售", "confidence": 0.8},
        ],
    },
    "5ea14429c3ee3699": {
        "entities": [
            {"name": "主", "type": "角色", "aliases": ["Lord"]},
            {"name": "恶魔", "type": "概念", "aliases": ["devil"]},
            {"name": "硫磺与火", "type": "事件", "aliases": ["rimstone and fire", "brimstone"]},
            {"name": "Kier", "type": "角色", "aliases": ["基尔"]},
        ],
        "relations": [
            {"src": "主", "dst": "硫磺与火", "relation": "降下", "confidence": 0.9},
            {"src": "恶魔", "dst": "硫磺与火", "relation": "招致", "confidence": 0.7},
        ],
    },
    "bd29ef0e3b103ad8": {
        "entities": [
            {"name": "拉普拉斯", "type": "组织", "aliases": ["Laplace", "LSCC"]},
            {"name": "普莱西", "type": "地点", "aliases": ["Plessis"]},
            {"name": "北极圈", "type": "地点", "aliases": ["Arctic Circle"]},
            {"name": "普莱西航天中心", "type": "地点", "aliases": ["Plessis Cosmodrome"]},
            {"name": "小海蒂", "type": "角色", "aliases": ["Little Heathy"]},
        ],
        "relations": [
            {"src": "拉普拉斯", "dst": "普莱西", "relation": "设立分部", "confidence": 0.9},
            {"src": "拉普拉斯", "dst": "北极圈", "relation": "分部临近", "confidence": 0.8},
            {"src": "普莱西航天中心", "dst": "普莱西", "relation": "位于", "confidence": 0.9},
        ],
    },
    "8c870c518756d09a": {
        "entities": [
            {"name": "司辰", "type": "角色", "aliases": ["Timekeeper"]},
            {"name": "维尔汀", "type": "角色", "aliases": ["Vertin", "Virgin"]},
            {"name": "神秘学家", "type": "概念", "aliases": ["Arcanists", "Arcanist"]},
            {"name": "SPTM", "type": "组织", "aliases": []},
            {"name": "匪帮", "type": "组织", "aliases": ["bandits"]},
        ],
        "relations": [
            {"src": "维尔汀", "dst": "司辰", "relation": "担任", "confidence": 0.7},
            {"src": "维尔汀", "dst": "SPTM", "relation": "曾就读", "confidence": 0.6},
            {"src": "SPTM", "dst": "神秘学家", "relation": "培养", "confidence": 0.8},
            {"src": "神秘学家", "dst": "匪帮", "relation": "对抗", "confidence": 0.7},
        ],
    },
    "25fbb95cb19667fb": {
        "entities": [
            {"name": "肯纳", "type": "角色", "aliases": ["Kenna", "Miss Kenna"]},
            {"name": "诺沃米尔", "type": "地点", "aliases": ["Novomir", "Novomierz"]},
        ],
        "relations": [
            {"src": "肯纳", "dst": "诺沃米尔", "relation": "到访", "confidence": 0.8},
        ],
    },
    "8127a071adca5d61": {
        "entities": [
            {"name": "拉普拉斯", "type": "组织", "aliases": ["Laplace", "LSCC"]},
            {"name": "阿德勒", "type": "角色",
             "aliases": ["Adler", "Researcher Adler", "researcher Adler"]},
        ],
        "relations": [
            {"src": "拉普拉斯", "dst": "阿德勒", "relation": "任命", "confidence": 0.8},
            {"src": "阿德勒", "dst": "拉普拉斯", "relation": "隶属", "confidence": 0.9},
        ],
    },
    "85fed8043a3023a9": {
        "entities": [
            {"name": "达芬奇", "type": "角色",
             "aliases": ["Leonardo", "Mr. Leonardo", "Leonardo da Vinci"]},
            {"name": "艾吉奥", "type": "角色", "aliases": ["Ezio", "Ezio Auditore"]},
            {"name": "维尔汀", "type": "角色", "aliases": ["Vertin"]},
            {"name": "阿尔伯特神父", "type": "角色", "aliases": ["Father Albert"]},
            {"name": "壁画", "type": "物品", "aliases": ["fresco"]},
            {"name": "消失点", "type": "概念", "aliases": ["vanishing points"]},
            {"name": "谜题", "type": "概念", "aliases": ["riddle"]},
        ],
        "relations": [
            {"src": "达芬奇", "dst": "壁画", "relation": "探讨", "confidence": 0.8},
            {"src": "壁画", "dst": "消失点", "relation": "运用", "confidence": 0.8},
            {"src": "艾吉奥", "dst": "谜题", "relation": "被告知", "confidence": 0.8},
            {"src": "维尔汀", "dst": "艾吉奥", "relation": "同行", "confidence": 0.9},
            {"src": "达芬奇", "dst": "阿尔伯特神父", "relation": "拖延", "confidence": 0.8},
        ],
    },
    "af08b25cff1f9033": {
        "entities": [
            {"name": "理想主义者", "type": "角色", "aliases": ["the Idealist", "Idealist"]},
            {"name": "艺术展", "type": "事件", "aliases": ["exhibition", "exhibición"]},
        ],
        "relations": [
            {"src": "理想主义者", "dst": "艺术展", "relation": "委托", "confidence": 0.8},
        ],
    },
    "60f70945e7278eee": {
        "entities": [
            {"name": "伊戈尔", "type": "角色", "aliases": ["Igor", "Admiral Igor"]},
            {"name": "风暴眼", "type": "概念", "aliases": ["its eye"]},
            {"name": "柯林相机", "type": "物品", "aliases": ["Curlean cameras"]},
            {"name": "时间异常", "type": "事件", "aliases": ["temporal anomaly"]},
            {"name": "未明物质", "type": "概念", "aliases": ["unidentifiable substances"]},
        ],
        "relations": [
            {"src": "伊戈尔", "dst": "风暴眼", "relation": "定位", "confidence": 0.9},
            {"src": "柯林相机", "dst": "未明物质", "relation": "拍摄到", "confidence": 0.8},
            {"src": "未明物质", "dst": "时间异常", "relation": "相关", "confidence": 0.8},
        ],
    },
    "616b0b9ec870407e": {
        "entities": [
            {"name": "建筑师", "type": "角色", "aliases": ["architect"]},
            {"name": "设计阶段", "type": "概念", "aliases": ["design phase"]},
            {"name": "施工阶段", "type": "概念",
             "aliases": ["Pre-construction and construction"]},
            {"name": "地基工程", "type": "概念", "aliases": ["foundation construction"]},
        ],
        "relations": [
            {"src": "建筑师", "dst": "设计阶段", "relation": "负责", "confidence": 0.9},
            {"src": "施工阶段", "dst": "地基工程", "relation": "包含", "confidence": 0.9},
        ],
    },
    "85f191fc747400cb": {
        "entities": [
            {"name": "永恒", "type": "概念", "aliases": ["eternity", "Eternity"]},
            {"name": "宇宙", "type": "概念", "aliases": ["universe"]},
            {"name": "暴雨", "type": "事件", "aliases": ["Storm", "The Storm"]},
        ],
        "relations": [
            {"src": "永恒", "dst": "宇宙", "relation": "依存", "confidence": 0.7},
            {"src": "暴雨", "dst": "宇宙", "relation": "冲刷", "confidence": 0.7},
        ],
    },
    "e260dbe85c1df3ca": {
        "entities": [
            {"name": "忒弥斯", "type": "角色", "aliases": ["Themis"]},
            {"name": "水上竞技会", "type": "事件", "aliases": ["Aquatic Games"]},
            {"name": "滑海比赛", "type": "事件", "aliases": ["sea-gliding competition"]},
            {"name": "驯海兽表演", "type": "事件",
             "aliases": ["sea-beast-taming exhibition"]},
            {"name": "水下障碍赛", "type": "事件", "aliases": ["underwater obstacle race"]},
            {"name": "贸易港", "type": "地点", "aliases": ["trade port"]},
        ],
        "relations": [
            {"src": "水上竞技会", "dst": "滑海比赛", "relation": "包含", "confidence": 0.9},
            {"src": "水上竞技会", "dst": "驯海兽表演", "relation": "包含", "confidence": 0.9},
            {"src": "水上竞技会", "dst": "水下障碍赛", "relation": "包含", "confidence": 0.9},
            {"src": "忒弥斯", "dst": "水上竞技会", "relation": "解说", "confidence": 0.6},
            {"src": "水上竞技会", "dst": "贸易港", "relation": "举办于", "confidence": 0.6},
        ],
    },
    "f2c3c33da44c0bcd": {
        "entities": [
            {"name": "奥秘", "type": "概念", "aliases": ["Arcanum", "Arkanum"]},
            {"name": "普纽玛", "type": "概念", "aliases": ["Pneuma"]},
            {"name": "大规模秘仪", "type": "事件",
             "aliases": ["large scale arcane ritual", "Arcane ritual"]},
            {"name": "巡防队", "type": "组织", "aliases": ["patrol"]},
        ],
        "relations": [
            {"src": "普纽玛", "dst": "大规模秘仪", "relation": "供给", "confidence": 0.8},
            {"src": "大规模秘仪", "dst": "奥秘", "relation": "涉及", "confidence": 0.7},
            {"src": "巡防队", "dst": "奥秘", "relation": "防范事故", "confidence": 0.8},
        ],
    },
    "45fcc5bffb12110f": {
        "entities": [
            {"name": "时间异常", "type": "事件", "aliases": ["temporal anomaly"]},
            {"name": "拉普拉斯", "type": "组织", "aliases": ["LSCC", "Laplace"]},
            {"name": "重塑之手", "type": "组织",
             "aliases": ["Menace Vindicte", "Manus Vindictae", "Manus"]},
        ],
        "relations": [
            {"src": "拉普拉斯", "dst": "时间异常", "relation": "监测", "confidence": 0.9},
            {"src": "拉普拉斯", "dst": "重塑之手", "relation": "评估威胁", "confidence": 0.7},
        ],
    },
    "b02178c22ef2f7b5": {
        "entities": [
            {"name": "神秘学家", "type": "概念", "aliases": ["Arcanists", "Arcanist"]},
            {"name": "圣洛夫基金会", "type": "组织", "aliases": ["Foundation"]},
            {"name": "人类", "type": "概念", "aliases": ["Humans"]},
            {"name": "战争", "type": "事件", "aliases": ["war", "this war"]},
        ],
        "relations": [
            {"src": "人类", "dst": "神秘学家", "relation": "驱使", "confidence": 0.9},
            {"src": "神秘学家", "dst": "战争", "relation": "被推上前线", "confidence": 0.9},
            {"src": "神秘学家", "dst": "圣洛夫基金会", "relation": "敌视", "confidence": 0.7},
        ],
    },
    "332e9f57b9c7eae6": {
        "entities": [
            {"name": "永恒", "type": "概念", "aliases": ["eternity", "Eternity"]},
            {"name": "死亡", "type": "概念", "aliases": ["death"]},
            {"name": "无常", "type": "概念", "aliases": ["impermanence"]},
            {"name": "暴雨", "type": "事件", "aliases": ["Storm", "The Storm"]},
        ],
        "relations": [
            {"src": "永恒", "dst": "死亡", "relation": "需先理解", "confidence": 0.8},
            {"src": "永恒", "dst": "无常", "relation": "需先理解", "confidence": 0.8},
        ],
    },
    "aa40fcc4f55b51eb": {
        "entities": [
            {"name": "多瑙河黎明号", "type": "物品",
             "aliases": ["Danube Dawn", "The Danube Dawn", "the danube dawn"]},
            {"name": "多瑙河", "type": "地点", "aliases": ["Danube"]},
            {"name": "吸血鬼", "type": "概念", "aliases": ["vampires", "vampire"]},
            {"name": "狼人", "type": "概念", "aliases": ["werewolves"]},
        ],
        "relations": [
            {"src": "多瑙河黎明号", "dst": "多瑙河", "relation": "航行于", "confidence": 0.9},
            {"src": "吸血鬼", "dst": "狼人", "relation": "同属传说", "confidence": 0.6},
        ],
    },
    "0cd272360525d75f": {
        "entities": [
            {"name": "伊戈尔", "type": "角色", "aliases": ["Igor"]},
            {"name": "骑兵军团", "type": "组织", "aliases": ["Calvary Corps"]},
            {"name": "暴雨", "type": "事件", "aliases": ["Storm", "The Storm"]},
            {"name": "草原", "type": "地点", "aliases": ["steppe"]},
            {"name": "城市", "type": "地点", "aliases": ["city"]},
        ],
        "relations": [
            {"src": "伊戈尔", "dst": "城市", "relation": "围困", "confidence": 0.7},
            {"src": "骑兵军团", "dst": "暴雨", "relation": "无法庇护", "confidence": 0.7},
            {"src": "伊戈尔", "dst": "草原", "relation": "交战于", "confidence": 0.6},
        ],
    },
    "5c5517dc88f11ecc": {
        "entities": [
            {"name": "阿布拉", "type": "角色", "aliases": ["Abla"]},
            {"name": "玩具盒", "type": "物品", "aliases": ["toy box", "the box"]},
            {"name": "强制撤离", "type": "事件", "aliases": ["forced evacuation measures"]},
            {"name": "报销单", "type": "物品", "aliases": ["receipts"]},
        ],
        "relations": [
            {"src": "阿布拉", "dst": "强制撤离", "relation": "受制于", "confidence": 0.8},
            {"src": "玩具盒", "dst": "强制撤离", "relation": "触发", "confidence": 0.6},
        ],
    },
    "4f273942f999585c": {
        "entities": [
            {"name": "蝴蝶", "type": "角色", "aliases": ["the Butterfly", "Butterfly"]},
            {"name": "乐透牌戏", "type": "物品", "aliases": ["Lotería", "la lotería"]},
            {"name": "托洛乔帮", "type": "组织", "aliases": ["Tolocho's gang"]},
            {"name": "轮盘赌", "type": "物品", "aliases": ["Russian roulette"]},
        ],
        "relations": [
            {"src": "蝴蝶", "dst": "乐透牌戏", "relation": "常胜", "confidence": 0.9},
            {"src": "蝴蝶", "dst": "托洛乔帮", "relation": "挑战", "confidence": 0.8},
            {"src": "蝴蝶", "dst": "轮盘赌", "relation": "精通", "confidence": 0.7},
        ],
    },
    "bddbe7dcf15bb26c": {
        "entities": [
            {"name": "哑谜", "type": "角色", "aliases": ["Enigma"]},
            {"name": "阿德勒", "type": "角色", "aliases": ["Adler", "Researcher Adler"]},
            {"name": "密码学家", "type": "角色", "aliases": ["cryptographer"]},
            {"name": "试剂瓶", "type": "物品", "aliases": ["reagent bottles"]},
        ],
        "relations": [
            {"src": "哑谜", "dst": "密码学家", "relation": "自称", "confidence": 0.8},
            {"src": "哑谜", "dst": "阿德勒", "relation": "对话", "confidence": 0.7},
            {"src": "哑谜", "dst": "试剂瓶", "relation": "采样", "confidence": 0.7},
        ],
    },
    "344e596f1f1ab780": {
        "entities": [
            {"name": "巴里", "type": "角色", "aliases": ["Barry"]},
            {"name": "服装店", "type": "地点", "aliases": ["clothing store"]},
            {"name": "猎犬", "type": "概念", "aliases": ["hunting dogs"]},
        ],
        "relations": [
            {"src": "巴里", "dst": "服装店", "relation": "计划开设", "confidence": 0.9},
        ],
    },
    "a0494ef6c472f4fb": {
        "entities": [
            {"name": "玛尔纱", "type": "角色", "aliases": ["Marsha"]},
            {"name": "民兵", "type": "组织", "aliases": ["militia"]},
            {"name": "庄园卫兵", "type": "组织", "aliases": ["manor soldiers"]},
            {"name": "路障", "type": "物品", "aliases": ["barricades"]},
        ],
        "relations": [
            {"src": "庄园卫兵", "dst": "民兵", "relation": "潜过", "confidence": 0.7},
            {"src": "玛尔纱", "dst": "庄园卫兵", "relation": "遭遇", "confidence": 0.8},
            {"src": "玛尔纱", "dst": "路障", "relation": "巡查", "confidence": 0.8},
        ],
    },
    "ab2527f6049f966d": {
        "entities": [
            {"name": "圣洛夫基金会", "type": "组织", "aliases": ["Foundation"]},
            {"name": "南极洲", "type": "地点", "aliases": ["Antarctica", "antarctica"]},
            {"name": "凯特", "type": "角色", "aliases": ["Kate"]},
            {"name": "珠峰", "type": "地点", "aliases": ["Everest"]},
        ],
        "relations": [
            {"src": "圣洛夫基金会", "dst": "南极洲", "relation": "派遣间谍", "confidence": 0.9},
            {"src": "凯特", "dst": "珠峰", "relation": "未能攀登", "confidence": 0.7},
        ],
    },
    "c8617fb4b0cf3d4e": {
        "entities": [
            {"name": "普列谢茨克", "type": "地点", "aliases": ["Plesetsk"]},
            {"name": "军事基地", "type": "地点", "aliases": ["military base"]},
            {"name": "秘术物品", "type": "物品", "aliases": ["Arcane item"]},
        ],
        "relations": [
            {"src": "军事基地", "dst": "秘术物品", "relation": "藏有", "confidence": 0.8},
            {"src": "军事基地", "dst": "普列谢茨克", "relation": "护卫", "confidence": 0.7},
        ],
    },
    "77e941ee44b88749": {
        "entities": [
            {"name": "原子", "type": "概念", "aliases": ["atoms"]},
            {"name": "太行山", "type": "地点", "aliases": ["Mount Taihang"]},
            {"name": "黄河", "type": "地点", "aliases": ["Yellow River"]},
            {"name": "尘埃", "type": "概念", "aliases": ["dust", "Dust"]},
            {"name": "万物", "type": "概念", "aliases": ["everything"]},
        ],
        "relations": [
            {"src": "原子", "dst": "万物", "relation": "构成", "confidence": 0.9},
            {"src": "万物", "dst": "尘埃", "relation": "归于", "confidence": 0.7},
        ],
    },
    "ed93e11a38dd6319": {
        "entities": [
            {"name": "第77中队", "type": "组织", "aliases": ["Squad 77"]},
            {"name": "血亲同胞", "type": "概念",
             "aliases": ["brothers and sisters in blood"]},
            {"name": "胜利", "type": "概念", "aliases": ["victory"]},
        ],
        "relations": [
            {"src": "第77中队", "dst": "胜利", "relation": "带来", "confidence": 0.8},
        ],
    },
    "019333e9436d2e07": {
        "entities": [
            {"name": "S博士", "type": "角色", "aliases": ["Dr. S", "Dr.S"]},
            {"name": "多瑙河", "type": "地点", "aliases": ["Danube"]},
            {"name": "航行日志", "type": "物品", "aliases": ["logbooks", "Logbooks"]},
            {"name": "交接记录", "type": "物品", "aliases": ["shift handover logs"]},
            {"name": "调度指令", "type": "物品", "aliases": ["dispatch instructions"]},
        ],
        "relations": [
            {"src": "S博士", "dst": "航行日志", "relation": "交付", "confidence": 0.8},
            {"src": "航行日志", "dst": "交接记录", "relation": "同存", "confidence": 0.7},
        ],
    },
    "ed522a9ce2ab65f3": {
        "entities": [
            {"name": "拉普拉斯", "type": "组织", "aliases": ["Laplace", "LSCC"]},
            {"name": "万物理论", "type": "概念",
             "aliases": ["a theory that unifies everything"]},
            {"name": "字谜", "type": "概念", "aliases": ["crossword"]},
        ],
        "relations": [
            {"src": "万物理论", "dst": "拉普拉斯", "relation": "追求目标", "confidence": 0.7},
        ],
    },
    "294d764a768ef7db": {
        "entities": [
            {"name": "谢尔盖", "type": "角色", "aliases": ["Sergei", "Sergey"]},
            {"name": "中尉", "type": "角色", "aliases": ["Lieutenant"]},
            {"name": "渔网", "type": "物品", "aliases": ["fishnet"]},
        ],
        "relations": [
            {"src": "谢尔盖", "dst": "渔网", "relation": "偷窃", "confidence": 0.9},
            {"src": "中尉", "dst": "谢尔盖", "relation": "警告", "confidence": 0.8},
        ],
    },
    "c815a0422942cbe5": {
        "entities": [
            {"name": "刺客", "type": "组织", "aliases": ["assassins", "Assassins"]},
            {"name": "大教堂", "type": "地点", "aliases": ["Duomo"]},
            {"name": "罗德里戈先生", "type": "角色", "aliases": ["Signore Rodrigo"]},
            {"name": "复仇", "type": "概念", "aliases": ["revenge"]},
        ],
        "relations": [
            {"src": "刺客", "dst": "复仇", "relation": "以…为依据", "confidence": 0.8},
            {"src": "大教堂", "dst": "罗德里戈先生", "relation": "阻拦", "confidence": 0.8},
        ],
    },
    "f0cc034102eb2077": {
        "entities": [
            {"name": "雷蒙夫人", "type": "角色", "aliases": ["Madame Raymond"]},
            {"name": "占卜师", "type": "角色", "aliases": ["diviners"]},
            {"name": "诅咒", "type": "概念", "aliases": ["curse"]},
            {"name": "秘宝律法", "type": "概念", "aliases": ["obscure jewel law"]},
        ],
        "relations": [
            {"src": "雷蒙夫人", "dst": "诅咒", "relation": "触犯", "confidence": 0.8},
            {"src": "占卜师", "dst": "诅咒", "relation": "知晓", "confidence": 0.7},
        ],
    },
    "6ab7bfc51c232814": {
        "entities": [
            {"name": "捷径", "type": "概念", "aliases": ["shortcut", "Shortcut"]},
            {"name": "屋顶", "type": "地点", "aliases": ["roofs"]},
            {"name": "藤蔓", "type": "物品", "aliases": ["vine"]},
        ],
        "relations": [
            {"src": "藤蔓", "dst": "屋顶", "relation": "攀爬至", "confidence": 0.8},
        ],
    },
    "d23e52b1524787ee": {
        "entities": [
            {"name": "康定斯基", "type": "角色", "aliases": ["Kandinsky"]},
            {"name": "保罗·克利", "type": "角色", "aliases": ["Paul Klee"]},
            {"name": "时代", "type": "概念", "aliases": ["times", "Times"]},
        ],
        "relations": [
            {"src": "康定斯基", "dst": "时代", "relation": "引领", "confidence": 0.7},
            {"src": "保罗·克利", "dst": "时代", "relation": "引领", "confidence": 0.7},
        ],
    },
    "75ae08c241a6afa5": {
        "entities": [
            {"name": "暴雨", "type": "事件", "aliases": ["Storm"]},
            {"name": "1999年", "type": "时间", "aliases": ["1999"]},
            {"name": "突击队", "type": "组织", "aliases": ["commando"]},
            {"name": "炮灰", "type": "概念", "aliases": ["cannon fodder"]},
        ],
        "relations": [
            {"src": "暴雨", "dst": "1999年", "relation": "重现于", "confidence": 0.8},
            {"src": "突击队", "dst": "炮灰", "relation": "视士兵为", "confidence": 0.8},
        ],
    },
    "2b1d37058524a0e1": {
        "entities": [
            {"name": "圣洛夫基金会", "type": "组织", "aliases": ["Foundation"]},
            {"name": "暴雨前调度中心", "type": "组织",
             "aliases": ["Pre-Storm Dispatch Center"]},
            {"name": "暴雨", "type": "事件", "aliases": ["Storm", "The Storm"]},
        ],
        "relations": [
            {"src": "暴雨前调度中心", "dst": "圣洛夫基金会", "relation": "接管安保",
             "confidence": 0.9},
            {"src": "暴雨前调度中心", "dst": "暴雨", "relation": "暴雨前24小时接管",
             "confidence": 0.8},
        ],
    },
    "7392bc955842bb03": {
        "entities": [
            {"name": "天王星", "type": "概念", "aliases": ["Uranus"]},
            {"name": "罗杰一号", "type": "物品", "aliases": ["Roger 1"]},
            {"name": "太阳系", "type": "概念", "aliases": ["solar system"]},
            {"name": "北方哨歌", "type": "角色",
             "aliases": ["Ms. Vinsong", "Windsong", "Winsong"]},
            {"name": "科兹洛夫", "type": "角色", "aliases": ["Kozlov", "Mr. Kozlov"]},
        ],
        "relations": [
            {"src": "罗杰一号", "dst": "太阳系", "relation": "飞向边缘", "confidence": 0.9},
            {"src": "罗杰一号", "dst": "天王星", "relation": "探测", "confidence": 0.8},
            {"src": "北方哨歌", "dst": "科兹洛夫", "relation": "约定会面", "confidence": 0.9},
        ],
    },
    "92bdf40393d62e33": {
        "entities": [
            {"name": "吸血鬼", "type": "概念", "aliases": ["vampires"]},
            {"name": "血液", "type": "概念", "aliases": ["blood"]},
            {"name": "母亲", "type": "角色", "aliases": ["Mama"]},
            {"name": "怪物", "type": "概念", "aliases": ["monsters", "Monsters"]},
        ],
        "relations": [
            {"src": "吸血鬼", "dst": "血液", "relation": "饮用以复活", "confidence": 0.9},
            {"src": "母亲", "dst": "吸血鬼", "relation": "模仿", "confidence": 0.6},
        ],
    },
    "83881b08f4f5b91c": {
        "entities": [
            {"name": "巴黎", "type": "地点", "aliases": ["Paris"]},
            {"name": "时代", "type": "概念", "aliases": ["times", "eras"]},
        ],
        "relations": [
            {"src": "巴黎", "dst": "时代", "relation": "跨越", "confidence": 0.6},
        ],
    },
    "05a7c1f65b0a514c": {
        "entities": [
            {"name": "背叛", "type": "概念", "aliases": ["betrayal", "Betrayal"]},
            {"name": "信念", "type": "概念", "aliases": ["convictions"]},
            {"name": "母亲", "type": "角色", "aliases": ["mom", "Mom"]},
        ],
        "relations": [
            {"src": "背叛", "dst": "信念", "relation": "违背", "confidence": 0.7},
        ],
    },
    "90334021cc49aeff": {
        "entities": [
            {"name": "司辰", "type": "角色", "aliases": ["Timekeeper"]},
            {"name": "阿蒙小姐", "type": "角色", "aliases": ["Miss Amon"]},
            {"name": "毒怪", "type": "概念", "aliases": ["poisonous monsters"]},
            {"name": "蜜蜂", "type": "概念", "aliases": ["bees"]},
            {"name": "白巷", "type": "地点", "aliases": ["white alleys"]},
            {"name": "灵魂", "type": "概念", "aliases": ["souls"]},
        ],
        "relations": [
            {"src": "阿蒙小姐", "dst": "司辰", "relation": "提及", "confidence": 0.7},
            {"src": "毒怪", "dst": "白巷", "relation": "藏匿", "confidence": 0.8},
            {"src": "毒怪", "dst": "灵魂", "relation": "吞食", "confidence": 0.8},
            {"src": "毒怪", "dst": "蜜蜂", "relation": "形似", "confidence": 0.7},
        ],
    },
    "1b3c5738bf7574f2": {
        "entities": [
            {"name": "阿尔卡纳", "type": "角色", "aliases": ["Arcana"]},
            {"name": "重塑之手", "type": "组织",
             "aliases": ["Manus", "Manus Vindictae", "Manus Vindicte"]},
            {"name": "委员会大楼", "type": "地点", "aliases": ["committee building"]},
            {"name": "增援部队", "type": "组织", "aliases": ["reinforcements", "ground units"]},
            {"name": "袭击", "type": "事件", "aliases": ["another attack"]},
        ],
        "relations": [
            {"src": "重塑之手", "dst": "袭击", "relation": "发动", "confidence": 0.9},
            {"src": "阿尔卡纳", "dst": "委员会大楼", "relation": "位于", "confidence": 0.9},
            {"src": "增援部队", "dst": "委员会大楼", "relation": "驰援", "confidence": 0.8},
        ],
    },
    "dd35d5cad84094a3": {
        "entities": [
            {"name": "鸽派", "type": "组织", "aliases": ["Doves"]},
            {"name": "鹰派", "type": "组织", "aliases": ["Hawks"]},
            {"name": "草原", "type": "地点", "aliases": ["steppe"]},
        ],
        "relations": [
            {"src": "鸽派", "dst": "鹰派", "relation": "对立", "confidence": 0.7},
        ],
    },
    "a3a79d4bc55263cc": {
        "entities": [
            {"name": "拉普拉斯", "type": "组织", "aliases": ["Laplace"]},
            {"name": "桥梁", "type": "地点", "aliases": ["bridge"]},
            {"name": "掉队者", "type": "概念", "aliases": ["stragglers"]},
        ],
        "relations": [
            {"src": "拉普拉斯", "dst": "掉队者", "relation": "搜查", "confidence": 0.8},
        ],
    },
    "939dd843b8226741": {
        "entities": [
            {"name": "岛屿", "type": "地点", "aliases": ["island"]},
            {"name": "殖民者", "type": "概念", "aliases": ["colonists"]},
            {"name": "暴雨", "type": "事件", "aliases": ["Storm", "The Storm"]},
            {"name": "流溢", "type": "概念", "aliases": ["emanation"]},
        ],
        "relations": [
            {"src": "暴雨", "dst": "岛屿", "relation": "影响", "confidence": 0.8},
            {"src": "殖民者", "dst": "岛屿", "relation": "离开", "confidence": 0.7},
        ],
    },
    "3aeb820652a86a8b": {
        "entities": [
            {"name": "洋葱头", "type": "角色", "aliases": ["ONiON", "Head Onion"]},
            {"name": "水上竞技会", "type": "事件", "aliases": ["Aquatic Games"]},
            {"name": "神秘术", "type": "概念", "aliases": ["arcane skills", "arcane talent"]},
        ],
        "relations": [
            {"src": "洋葱头", "dst": "水上竞技会", "relation": "报道", "confidence": 0.9},
            {"src": "水上竞技会", "dst": "神秘术", "relation": "展示", "confidence": 0.8},
        ],
    },
    "8a327ce099c36d6b": {
        "entities": [
            {"name": "热沃当野兽", "type": "概念",
             "aliases": ["beast of Gévaudan", "beasts of Gévaudan", "Gévaudan"]},
            {"name": "幽灵", "type": "概念", "aliases": ["ghosts and spirits", "Spirits"]},
            {"name": "皇帝", "type": "角色", "aliases": ["emperor"]},
            {"name": "城市", "type": "地点", "aliases": ["city"]},
        ],
        "relations": [
            {"src": "热沃当野兽", "dst": "城市", "relation": "出没", "confidence": 0.9},
            {"src": "幽灵", "dst": "城市", "relation": "惊扰", "confidence": 0.7},
        ],
    },
}


def main() -> int:
    ap = argparse.ArgumentParser(description="补抽空块 第 1 批")
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
    # NOOP 集合落盘，供审计脚本排除
    noop_path = ROOT / "data/knowledge/_audit/noop_confirmed.json"
    cur = set()
    if noop_path.exists():
        cur = set(json.loads(noop_path.read_text(encoding="utf-8")))
    cur |= set(NOOP)
    noop_path.write_text(json.dumps(sorted(cur), ensure_ascii=False, indent=1),
                         encoding="utf-8")
    print(f"[apply-p1] 写入 {written} 条，跳过 {skipped} 条 → {cache_dir}")
    print(f"[apply-p1] NOOP 累计 {len(cur)} 条 → {noop_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
