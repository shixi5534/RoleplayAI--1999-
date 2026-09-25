# -*- coding: utf-8 -*-
"""未抽取剧情块补抽 · 第 12 批（batch_02，20 块）。

来源：data/knowledge/_audit/backfill2/batches/batch_02.txt
规范：只抽正文明确出现的词；实体名用中文正名，原文/带引号写法进 aliases；
      type ∈ 角色/组织/地点/物品/概念/事件/时间/现象；谓语纯中文；
      src/dst 须落在本块 entities 的 name 或 aliases 内。
用法：python scripts/apply_missing_p12.py --apply
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "knowledge" / "plot_cache" / "wu_ming_zhe"

# 本批 20 块均有剧情信息，无 NOOP。

RESULTS: dict[str, dict] = {
    # ---- a5ec858c7f2c92bc v3.1 多瑙黎明号/血食怪眷属传闻 ----
    "a5ec858c7f2c92bc": {
        "entities": [
            {"name": "血食怪", "type": "角色", "aliases": ["伟大的血食怪"]},
            {"name": "维也纳-潘诺尼亚运输公司", "type": "组织", "aliases": []},
            {"name": "多瑙黎明号", "type": "物品", "aliases": ["多瑙黎明号"]},
            {"name": "猩红梦魇", "type": "角色", "aliases": []},
            {"name": "伊斯坦布尔", "type": "地点", "aliases": []},
            {"name": "维也纳", "type": "地点", "aliases": []},
            {"name": "多瑙河", "type": "地点", "aliases": ["多瑙河流域"]},
        ],
        "relations": [
            {"src": "维也纳-潘诺尼亚运输公司", "dst": "多瑙黎明号", "relation": "运营", "confidence": 0.9},
            {"src": "猩红梦魇", "dst": "血食怪", "relation": "隶属", "confidence": 0.8},
            {"src": "猩红梦魇", "dst": "多瑙黎明号", "relation": "出没于", "confidence": 0.8},
            {"src": "多瑙黎明号", "dst": "伊斯坦布尔", "relation": "连接", "confidence": 0.85},
            {"src": "多瑙黎明号", "dst": "维也纳", "relation": "连接", "confidence": 0.85},
        ],
    },
    # ---- 0e6e1b578ecb49dd v2.7 乌特恩亚亚马戏团演出 ----
    "0e6e1b578ecb49dd": {
        "entities": [
            {"name": "科兹洛夫", "type": "角色", "aliases": []},
            {"name": "娜塔莉亚", "type": "角色", "aliases": []},
            {"name": "以利亚", "type": "角色", "aliases": []},
            {"name": "弗拉西奥斯", "type": "角色", "aliases": []},
            {"name": "理线学", "type": "概念", "aliases": []},
            {"name": "乌特恩亚亚马戏团", "type": "组织", "aliases": ["伟大的乌特恩亚亚马戏团"]},
            {"name": "库珀花环", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "以利亚", "dst": "乌特恩亚亚马戏团", "relation": "隶属", "confidence": 0.8},
            {"src": "弗拉西奥斯", "dst": "乌特恩亚亚马戏团", "relation": "隶属", "confidence": 0.8},
            {"src": "库珀花环", "dst": "乌特恩亚亚马戏团", "relation": "隶属", "confidence": 0.8},
        ],
    },
    # ---- 537a6c2c6e9e9b69 v2.1 搭车客专栏/下水道怪谈 ----
    "537a6c2c6e9e9b69": {
        "entities": [
            {"name": "77号公路", "type": "地点", "aliases": []},
            {"name": "搭车客专栏", "type": "物品", "aliases": ["《搭车客专栏》"]},
            {"name": "下水道的食人鱼", "type": "事件", "aliases": ["下水道的食人鱼"]},
            {"name": "变成野兔的乡野女巫", "type": "事件", "aliases": ["变成野兔的乡野女巫"]},
            {"name": "纽约市", "type": "地点", "aliases": []},
            {"name": "K先生", "type": "角色", "aliases": []},
            {"name": "政府", "type": "组织", "aliases": []},
            {"name": "神秘组织", "type": "组织", "aliases": []},
            {"name": "变形类神秘术", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "神秘组织", "dst": "下水道的食人鱼", "relation": "培养", "confidence": 0.7},
            {"src": "K先生", "dst": "纽约市", "relation": "居住于", "confidence": 0.85},
            {"src": "搭车客专栏", "dst": "下水道的食人鱼", "relation": "提及", "confidence": 0.8},
        ],
    },
    # ---- 72471a2d9d598890 v2.1 克隆实验体观察记录 ----
    "72471a2d9d598890": {
        "entities": [
            {"name": "实验体", "type": "角色", "aliases": []},
            {"name": "JSRV逆转录病毒", "type": "物品", "aliases": []},
            {"name": "芬兰多塞特白面母绵羊", "type": "物品", "aliases": []},
            {"name": "美式乡村音乐", "type": "概念", "aliases": []},
            {"name": "无菌室", "type": "地点", "aliases": []},
            {"name": "动物医学团队", "type": "组织", "aliases": []},
        ],
        "relations": [
            {"src": "实验体", "dst": "JSRV逆转录病毒", "relation": "感染", "confidence": 0.85},
            {"src": "实验体", "dst": "芬兰多塞特白面母绵羊", "relation": "头部相似", "confidence": 0.8},
            {"src": "美式乡村音乐", "dst": "实验体", "relation": "缓解过敏", "confidence": 0.8},
            {"src": "动物医学团队", "dst": "实验体", "relation": "诊治", "confidence": 0.7},
        ],
    },
    # ---- a91a1fd6fbdd2712 v2.1 蓝手帕与监管对象“旅馆” ----
    "a91a1fd6fbdd2712": {
        "entities": [
            {"name": "蓝手帕", "type": "角色", "aliases": []},
            {"name": "旅馆", "type": "角色", "aliases": []},
            {"name": "德克萨斯州", "type": "地点", "aliases": []},
            {"name": "77号公路", "type": "地点", "aliases": []},
            {"name": "北美地区", "type": "地点", "aliases": []},
            {"name": "血腥玛丽", "type": "角色", "aliases": []},
            {"name": "天蛾人", "type": "角色", "aliases": []},
            {"name": "骚灵传说", "type": "事件", "aliases": ["骚灵传说"]},
            {"name": "司辰小队", "type": "组织", "aliases": []},
            {"name": "卡车司机", "type": "角色", "aliases": []},
            {"name": "南部平原之声", "type": "物品", "aliases": ["《南部平原之声》"]},
            {"name": "老镇子", "type": "地点", "aliases": []},
            {"name": "神秘学集合体", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "蓝手帕", "dst": "旅馆", "relation": "监管", "confidence": 0.85},
            {"src": "蓝手帕", "dst": "旅馆", "relation": "搭档", "confidence": 0.8},
            {"src": "旅馆", "dst": "德克萨斯州", "relation": "存在于", "confidence": 0.85},
            {"src": "旅馆", "dst": "77号公路", "relation": "模仿", "confidence": 0.7},
            {"src": "神秘学集合体", "dst": "血腥玛丽", "relation": "呈现", "confidence": 0.8},
            {"src": "神秘学集合体", "dst": "天蛾人", "relation": "呈现", "confidence": 0.8},
            {"src": "神秘学集合体", "dst": "骚灵传说", "relation": "呈现", "confidence": 0.8},
            {"src": "卡车司机", "dst": "旅馆", "relation": "经历", "confidence": 0.8},
            {"src": "蓝手帕", "dst": "司辰小队", "relation": "拟调入", "confidence": 0.7},
        ],
    },
    # ---- e5124202c2df30eb v3.8 肯纳/奠基石勘测与鬼魂酒友 ----
    "e5124202c2df30eb": {
        "entities": [
            {"name": "肯纳", "type": "角色", "aliases": []},
            {"name": "奠基石", "type": "角色", "aliases": []},
            {"name": "时空灾害", "type": "事件", "aliases": ["时空灾害"]},
            {"name": "委员会", "type": "组织", "aliases": []},
            {"name": "UTTU", "type": "组织", "aliases": []},
            {"name": "小酒馆", "type": "地点", "aliases": []},
            {"name": "鬼魂", "type": "角色", "aliases": ["邻居"]},
            {"name": "老米哈乌", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "肯纳", "dst": "奠基石", "relation": "支持", "confidence": 0.8},
            {"src": "老米哈乌", "dst": "鬼魂", "relation": "即是", "confidence": 0.75},
            {"src": "小酒馆", "dst": "鬼魂", "relation": "存在", "confidence": 0.8},
        ],
    },
    # ---- 0eb6c955b3e660a5 v3.8 诺瓦米奇工厂/砖与拱 ----
    "0eb6c955b3e660a5": {
        "entities": [
            {"name": "罗莎", "type": "角色", "aliases": []},
            {"name": "诺瓦米奇", "type": "地点", "aliases": []},
            {"name": "安德烈", "type": "角色", "aliases": []},
            {"name": "运河", "type": "地点", "aliases": []},
            {"name": "河流", "type": "地点", "aliases": []},
            {"name": "罗马", "type": "地点", "aliases": []},
            {"name": "布鲁内莱斯基", "type": "角色", "aliases": []},
            {"name": "多纳泰罗", "type": "角色", "aliases": []},
            {"name": "印度", "type": "地点", "aliases": []},
            {"name": "印度管理学院", "type": "组织", "aliases": []},
            {"name": "砖", "type": "物品", "aliases": []},
            {"name": "拱", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "罗莎", "dst": "诺瓦米奇", "relation": "提及", "confidence": 0.8},
            {"src": "运河", "dst": "诺瓦米奇", "relation": "位于", "confidence": 0.8},
            {"src": "布鲁内莱斯基", "dst": "多纳泰罗", "relation": "同时代", "confidence": 0.8},
            {"src": "印度管理学院", "dst": "印度", "relation": "位于", "confidence": 0.85},
            {"src": "砖", "dst": "拱", "relation": "向往", "confidence": 0.85},
        ],
    },
    # ---- 49b64cd14c817f0a v3.8 迟来的葬礼/守灵夜 ----
    "49b64cd14c817f0a": {
        "entities": [
            {"name": "卡塔日娜", "type": "角色", "aliases": []},
            {"name": "马雷克", "type": "角色", "aliases": []},
            {"name": "守灵夜", "type": "事件", "aliases": []},
            {"name": "迟来的葬礼", "type": "事件", "aliases": []},
            {"name": "亚肖", "type": "角色", "aliases": []},
            {"name": "斯塔夏", "type": "角色", "aliases": []},
            {"name": "卢齐安", "type": "角色", "aliases": []},
            {"name": "穹顶", "type": "地点", "aliases": []},
            {"name": "小酒吧", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "斯塔夏", "dst": "卢齐安", "relation": "致辞于", "confidence": 0.85},
            {"src": "亚肖", "dst": "迟来的葬礼", "relation": "参加", "confidence": 0.8},
            {"src": "守灵夜", "dst": "小酒吧", "relation": "发生于", "confidence": 0.8},
            {"src": "迟来的葬礼", "dst": "卢齐安", "relation": "祭奠", "confidence": 0.85},
            {"src": "卢齐安", "dst": "穹顶", "relation": "愿修复", "confidence": 0.8},
        ],
    },
    # ---- 86a7fee125924ae2 v3.8 群众智慧/水母拍拍 ----
    "86a7fee125924ae2": {
        "entities": [
            {"name": "奠基石", "type": "角色", "aliases": []},
            {"name": "蓝图", "type": "角色", "aliases": []},
            {"name": "柏林以东", "type": "角色", "aliases": []},
            {"name": "居民Ⅰ", "type": "角色", "aliases": []},
            {"name": "居民Ⅱ", "type": "角色", "aliases": []},
            {"name": "马顿", "type": "角色", "aliases": []},
            {"name": "回声谣", "type": "角色", "aliases": []},
            {"name": "奥尔加", "type": "角色", "aliases": []},
            {"name": "水母拍拍", "type": "物品", "aliases": []},
            {"name": "录像带", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "奠基石", "dst": "蓝图", "relation": "协作", "confidence": 0.8},
            {"src": "奠基石", "dst": "柏林以东", "relation": "委托", "confidence": 0.85},
            {"src": "柏林以东", "dst": "录像带", "relation": "携带", "confidence": 0.8},
            {"src": "奥尔加", "dst": "奠基石", "relation": "称赞", "confidence": 0.8},
        ],
    },
    # ---- 95e9e4d51a796c51 v3.6 弦理论讲座/玩具箱说明 ----
    "95e9e4d51a796c51": {
        "entities": [
            {"name": "弦理论", "type": "概念", "aliases": []},
            {"name": "弦", "type": "概念", "aliases": []},
            {"name": "高维空间", "type": "概念", "aliases": []},
            {"name": "张同学", "type": "角色", "aliases": []},
            {"name": "玩具箱", "type": "物品", "aliases": []},
            {"name": "缪斯三世", "type": "角色", "aliases": []},
            {"name": "缪斯博物馆", "type": "组织", "aliases": []},
        ],
        "relations": [
            {"src": "弦理论", "dst": "弦", "relation": "基于", "confidence": 0.85},
            {"src": "张同学", "dst": "弦理论", "relation": "听讲", "confidence": 0.8},
            {"src": "玩具箱", "dst": "缪斯三世", "relation": "归属", "confidence": 0.85},
            {"src": "缪斯三世", "dst": "缪斯博物馆", "relation": "拥有", "confidence": 0.8},
            {"src": "高维空间", "dst": "弦", "relation": "容纳", "confidence": 0.8},
        ],
    },
    # ---- 10da4166a5067162 v3.6 密码入门指南/嫌疑人名单 ----
    "10da4166a5067162": {
        "entities": [
            {"name": "拉普拉斯", "type": "组织", "aliases": []},
            {"name": "维吉尼亚密码", "type": "概念", "aliases": []},
            {"name": "凯撒密码", "type": "概念", "aliases": []},
            {"name": "阿德勒", "type": "角色", "aliases": []},
            {"name": "乌尔里希", "type": "角色", "aliases": []},
            {"name": "X", "type": "角色", "aliases": []},
            {"name": "理查德", "type": "角色", "aliases": []},
            {"name": "道金斯", "type": "角色", "aliases": []},
            {"name": "维克托", "type": "角色", "aliases": []},
            {"name": "玩具箱", "type": "物品", "aliases": []},
            {"name": "密码入门指南·维吉尼亚篇", "type": "物品", "aliases": ["《密码入门指南·维吉尼亚篇》"]},
            {"name": "密码恶作剧", "type": "事件", "aliases": []},
        ],
        "relations": [
            {"src": "拉普拉斯", "dst": "密码入门指南·维吉尼亚篇", "relation": "发布", "confidence": 0.85},
            {"src": "维吉尼亚密码", "dst": "凯撒密码", "relation": "升级自", "confidence": 0.85},
            {"src": "阿德勒", "dst": "密码恶作剧", "relation": "涉嫌", "confidence": 0.7},
            {"src": "乌尔里希", "dst": "密码恶作剧", "relation": "涉嫌", "confidence": 0.7},
            {"src": "X", "dst": "密码恶作剧", "relation": "涉嫌", "confidence": 0.7},
            {"src": "理查德", "dst": "密码恶作剧", "relation": "涉嫌", "confidence": 0.7},
            {"src": "道金斯", "dst": "密码恶作剧", "relation": "涉嫌", "confidence": 0.7},
            {"src": "维克托", "dst": "密码恶作剧", "relation": "涉嫌", "confidence": 0.7},
        ],
    },
    # ---- 843c6f03ea31a87e v3.7 基金会诊疗记录/飞蛾 ----
    "843c6f03ea31a87e": {
        "entities": [
            {"name": "颤颤之齿", "type": "物品", "aliases": []},
            {"name": "牙仙小姐", "type": "角色", "aliases": []},
            {"name": "医务室", "type": "地点", "aliases": []},
            {"name": "神秘学家乳牙", "type": "物品", "aliases": []},
            {"name": "飞蛾", "type": "角色", "aliases": []},
            {"name": "基金会", "type": "组织", "aliases": []},
            {"name": "南极", "type": "地点", "aliases": []},
            {"name": "重塑之手", "type": "组织", "aliases": []},
            {"name": "趋光性定律", "type": "概念", "aliases": []},
            {"name": "人格覆写", "type": "概念", "aliases": []},
            {"name": "神经修复肽", "type": "物品", "aliases": []},
            {"name": "基金会诊疗记录档案", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "牙仙小姐", "dst": "神秘学家乳牙", "relation": "收藏", "confidence": 0.8},
            {"src": "飞蛾", "dst": "基金会", "relation": "隶属", "confidence": 0.8},
            {"src": "飞蛾", "dst": "南极", "relation": "行动于", "confidence": 0.8},
            {"src": "飞蛾", "dst": "重塑之手", "relation": "潜入", "confidence": 0.8},
            {"src": "飞蛾", "dst": "人格覆写", "relation": "承受", "confidence": 0.8},
            {"src": "基金会", "dst": "飞蛾", "relation": "治疗", "confidence": 0.85},
            {"src": "神经修复肽", "dst": "飞蛾", "relation": "用于", "confidence": 0.8},
        ],
    },
    # ---- 0e95aa3975ffaa88 v3.7 敌干部档案/普莱玛 ----
    "0e95aa3975ffaa88": {
        "entities": [
            {"name": "平", "type": "角色", "aliases": []},
            {"name": "歌唱家", "type": "角色", "aliases": []},
            {"name": "火渡船", "type": "角色", "aliases": []},
            {"name": "假想敌", "type": "角色", "aliases": []},
            {"name": "绀紫腕", "type": "角色", "aliases": []},
            {"name": "普莱玛", "type": "角色", "aliases": []},
            {"name": "阿尼姆斯", "type": "角色", "aliases": []},
            {"name": "重塑之手", "type": "组织", "aliases": []},
            {"name": "伊戈尔", "type": "角色", "aliases": []},
            {"name": "狮鹫军", "type": "组织", "aliases": []},
            {"name": "基金会", "type": "组织", "aliases": []},
            {"name": "南极事件", "type": "事件", "aliases": []},
            {"name": "学校", "type": "组织", "aliases": []},
            {"name": "风", "type": "角色", "aliases": ["风"]},
        ],
        "relations": [
            {"src": "普莱玛", "dst": "阿尼姆斯", "relation": "母亲", "confidence": 0.85},
            {"src": "阿尼姆斯", "dst": "重塑之手", "relation": "隶属", "confidence": 0.85},
            {"src": "阿尼姆斯", "dst": "南极事件", "relation": "死于", "confidence": 0.85},
            {"src": "普莱玛", "dst": "伊戈尔", "relation": "协作", "confidence": 0.8},
            {"src": "伊戈尔", "dst": "狮鹫军", "relation": "统领", "confidence": 0.8},
            {"src": "伊戈尔", "dst": "基金会", "relation": "救援", "confidence": 0.8},
            {"src": "普莱玛", "dst": "学校", "relation": "反对袭击", "confidence": 0.8},
            {"src": "普莱玛", "dst": "重塑之手", "relation": "隶属", "confidence": 0.75},
        ],
    },
    # ---- 1dbf75f165e38beb v3.7 刻雷乌斯与特别检察官问询 ----
    "1dbf75f165e38beb": {
        "entities": [
            {"name": "刻雷乌斯", "type": "角色", "aliases": []},
            {"name": "特别检察官", "type": "角色", "aliases": []},
            {"name": "最高裁判所", "type": "组织", "aliases": []},
            {"name": "总部", "type": "组织", "aliases": []},
            {"name": "委员会", "type": "组织", "aliases": []},
            {"name": "跟踪药剂", "type": "物品", "aliases": []},
            {"name": "示踪剂", "type": "物品", "aliases": ["示踪剂"]},
            {"name": "定位试验样本", "type": "物品", "aliases": ["定位试验样本"]},
            {"name": "医疗组", "type": "组织", "aliases": []},
            {"name": "基金会", "type": "组织", "aliases": []},
            {"name": "叶尔莫莱", "type": "角色", "aliases": []},
            {"name": "顿河", "type": "地点", "aliases": []},
            {"name": "暴雨", "type": "事件", "aliases": ["暴雨"]},
            {"name": "审判", "type": "事件", "aliases": ["审判"]},
            {"name": "陪审团", "type": "组织", "aliases": []},
            {"name": "机密研究项目", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "刻雷乌斯", "dst": "特别检察官", "relation": "遇见", "confidence": 0.8},
            {"src": "特别检察官", "dst": "刻雷乌斯", "relation": "问询", "confidence": 0.8},
            {"src": "刻雷乌斯", "dst": "跟踪药剂", "relation": "使用", "confidence": 0.85},
            {"src": "跟踪药剂", "dst": "示踪剂", "relation": "亦即", "confidence": 0.85},
            {"src": "刻雷乌斯", "dst": "定位试验样本", "relation": "指认", "confidence": 0.8},
            {"src": "医疗组", "dst": "定位试验样本", "relation": "存放", "confidence": 0.8},
            {"src": "刻雷乌斯", "dst": "叶尔莫莱", "relation": "派遣", "confidence": 0.85},
            {"src": "叶尔莫莱", "dst": "顿河", "relation": "前往", "confidence": 0.85},
            {"src": "叶尔莫莱", "dst": "机密研究项目", "relation": "调查", "confidence": 0.8},
            {"src": "特别检察官", "dst": "最高裁判所", "relation": "隶属", "confidence": 0.75},
        ],
    },
    # ---- f4df23174b0caca2 v1.8 来亚什基/被留下的 ----
    "f4df23174b0caca2": {
        "entities": [
            {"name": "帕特里基", "type": "角色", "aliases": []},
            {"name": "来亚什基", "type": "地点", "aliases": []},
            {"name": "克努特", "type": "角色", "aliases": []},
            {"name": "维拉", "type": "角色", "aliases": []},
            {"name": "北方哨歌", "type": "角色", "aliases": []},
            {"name": "拉伊莎", "type": "角色", "aliases": []},
            {"name": "叶甫根尼", "type": "角色", "aliases": []},
            {"name": "综合课堂", "type": "地点", "aliases": []},
            {"name": "针脚与面包", "type": "地点", "aliases": []},
            {"name": "巴努哇", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "维拉", "dst": "北方哨歌", "relation": "同伴", "confidence": 0.8},
            {"src": "维拉", "dst": "拉伊莎", "relation": "同伴", "confidence": 0.8},
            {"src": "拉伊莎", "dst": "维拉", "relation": "教授", "confidence": 0.8},
            {"src": "拉伊莎", "dst": "针脚与面包", "relation": "工作于", "confidence": 0.8},
            {"src": "维拉", "dst": "巴努哇", "relation": "穿着", "confidence": 0.7},
            {"src": "帕特里基", "dst": "来亚什基", "relation": "生活于", "confidence": 0.8},
            {"src": "综合课堂", "dst": "来亚什基", "relation": "位于", "confidence": 0.8},
            {"src": "针脚与面包", "dst": "来亚什基", "relation": "位于", "confidence": 0.8},
        ],
    },
    # ---- 7eb821fb19382bb5 v1.8 拉伊莎独白/广场聚会 ----
    "7eb821fb19382bb5": {
        "entities": [
            {"name": "拉伊莎", "type": "角色", "aliases": []},
            {"name": "维拉", "type": "角色", "aliases": []},
            {"name": "叶甫根尼", "type": "角色", "aliases": []},
            {"name": "来亚什基", "type": "地点", "aliases": []},
            {"name": "广场聚会", "type": "事件", "aliases": []},
            {"name": "广场", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "拉伊莎", "dst": "维拉", "relation": "感激", "confidence": 0.8},
            {"src": "拉伊莎", "dst": "叶甫根尼", "relation": "相信", "confidence": 0.8},
            {"src": "拉伊莎", "dst": "来亚什基", "relation": "生活于", "confidence": 0.8},
            {"src": "广场聚会", "dst": "广场", "relation": "发生于", "confidence": 0.85},
            {"src": "广场聚会", "dst": "来亚什基", "relation": "位于", "confidence": 0.8},
        ],
    },
    # ---- 659185b3ecdb8e54 v1.8 乌里扬娜归来 ----
    "659185b3ecdb8e54": {
        "entities": [
            {"name": "来亚什基", "type": "地点", "aliases": []},
            {"name": "莫斯科", "type": "地点", "aliases": []},
            {"name": "学校", "type": "组织", "aliases": []},
            {"name": "广场", "type": "地点", "aliases": []},
            {"name": "维拉", "type": "角色", "aliases": []},
            {"name": "乌里扬娜", "type": "角色", "aliases": []},
            {"name": "雪", "type": "现象", "aliases": []},
        ],
        "relations": [
            {"src": "乌里扬娜", "dst": "来亚什基", "relation": "返回", "confidence": 0.85},
            {"src": "维拉", "dst": "乌里扬娜", "relation": "迎接", "confidence": 0.8},
            {"src": "维拉", "dst": "乌里扬娜", "relation": "同志", "confidence": 0.8},
            {"src": "莫斯科", "dst": "来亚什基", "relation": "令想起", "confidence": 0.7},
            {"src": "学校", "dst": "来亚什基", "relation": "位于", "confidence": 0.8},
            {"src": "广场", "dst": "来亚什基", "relation": "位于", "confidence": 0.8},
            {"src": "乌里扬娜", "dst": "学校", "relation": "任教于", "confidence": 0.75},
        ],
    },
    # ---- c4c2a9f7e93bfde2 v? 命名日/阿夫西维告别 ----
    "c4c2a9f7e93bfde2": {
        "entities": [
            {"name": "阿夫西维", "type": "角色", "aliases": []},
            {"name": "彼得森", "type": "角色", "aliases": []},
            {"name": "维拉", "type": "角色", "aliases": []},
            {"name": "浣熊先生", "type": "角色", "aliases": []},
            {"name": "命名日", "type": "角色", "aliases": []},
            {"name": "基金会", "type": "组织", "aliases": []},
            {"name": "来亚什基", "type": "地点", "aliases": []},
            {"name": "列宁格勒", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "阿夫西维", "dst": "维拉", "relation": "告别", "confidence": 0.8},
            {"src": "阿夫西维", "dst": "彼得森", "relation": "去找", "confidence": 0.8},
            {"src": "阿夫西维", "dst": "浣熊先生", "relation": "告别", "confidence": 0.8},
            {"src": "命名日", "dst": "列宁格勒", "relation": "路过", "confidence": 0.8},
            {"src": "维拉", "dst": "来亚什基", "relation": "命名", "confidence": 0.85},
        ],
    },
    # ---- 27e6dd3ddbffb820 v2.5 夜巡特遣管理局/密友广告 ----
    "27e6dd3ddbffb820": {
        "entities": [
            {"name": "夜巡特遣管理局", "type": "组织", "aliases": []},
            {"name": "夜巡调解条例", "type": "概念", "aliases": []},
            {"name": "圣洛夫基金会", "type": "组织", "aliases": ["基金会", "基金会宣传部"]},
            {"name": "密友", "type": "概念", "aliases": ["密友"]},
            {"name": "侲子", "type": "角色", "aliases": ["侲子"]},
            {"name": "险道兽", "type": "角色", "aliases": ["险道兽"]},
            {"name": "梁", "type": "组织", "aliases": ["梁家族"]},
            {"name": "险道兽强梁", "type": "角色", "aliases": ["险道兽强梁"]},
            {"name": "新巴别塔魔精公司", "type": "组织", "aliases": []},
        ],
        "relations": [
            {"src": "夜巡特遣管理局", "dst": "夜巡调解条例", "relation": "遵守", "confidence": 0.8},
            {"src": "侲子", "dst": "险道兽", "relation": "作伴", "confidence": 0.85},
            {"src": "梁", "dst": "险道兽强梁", "relation": "结为密友", "confidence": 0.85},
            {"src": "险道兽强梁", "dst": "险道兽", "relation": "属于", "confidence": 0.8},
            {"src": "新巴别塔魔精公司", "dst": "密友", "relation": "提供", "confidence": 0.8},
            {"src": "圣洛夫基金会", "dst": "密友", "relation": "提供", "confidence": 0.8},
        ],
    },
    # ---- 6a3c0395617c8331 v2.5 菲林士多访谈梁月/险道兽强梁 ----
    "6a3c0395617c8331": {
        "entities": [
            {"name": "黄先生", "type": "角色", "aliases": []},
            {"name": "社火游行", "type": "事件", "aliases": []},
            {"name": "菲林士多", "type": "角色", "aliases": []},
            {"name": "梁月", "type": "角色", "aliases": []},
            {"name": "险道兽强梁", "type": "角色", "aliases": ["强梁"]},
            {"name": "梁家", "type": "组织", "aliases": []},
            {"name": "何日君", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "菲林士多", "dst": "梁月", "relation": "访谈", "confidence": 0.8},
            {"src": "黄先生", "dst": "社火游行", "relation": "介绍", "confidence": 0.8},
            {"src": "梁月", "dst": "险道兽强梁", "relation": "召唤", "confidence": 0.85},
            {"src": "险道兽强梁", "dst": "梁家", "relation": "回应祭祀", "confidence": 0.8},
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
    print(f"[apply-missing-p12] 写入 {len(RESULTS)} 条")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
