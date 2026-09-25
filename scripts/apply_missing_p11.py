# -*- coding: utf-8 -*-
"""未抽取剧情块补抽 · 第 11 批（backfill2 batch_01，20 块）。

用法：python scripts/apply_missing_p11.py --apply
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "knowledge" / "plot_cache" / "wu_ming_zhe"

RESULTS: dict[str, dict] = {
    # v2.4 乌尔里希与哑谜：洛伦兹研究所、人工暴雨、灵知
    "ce8b42e50f5134cb": {
        "entities": [
            {"name": "乌尔里希", "type": "角色", "aliases": []},
            {"name": "哑谜", "type": "角色", "aliases": []},
            {"name": "洛伦兹研究所", "type": "组织", "aliases": []},
            {"name": "洛伦兹蝴蝶", "type": "角色", "aliases": []},
            {"name": "委外合约人才管理组织", "type": "组织", "aliases": []},
            {"name": "暴雨", "type": "事件", "aliases": ["“暴雨”"]},
            {"name": "人工暴雨", "type": "概念", "aliases": ["“人工暴雨”"]},
            {"name": "灵知", "type": "概念", "aliases": ["“灵知”"]},
            {"name": "灵性", "type": "概念", "aliases": ["“灵性”"]},
            {"name": "黑箱", "type": "概念", "aliases": ["“黑箱”"]},
            {"name": "超自然现象", "type": "现象", "aliases": []},
        ],
        "relations": [
            {"src": "乌尔里希", "dst": "洛伦兹研究所", "relation": "提及", "confidence": 0.8},
            {"src": "洛伦兹蝴蝶", "dst": "暴雨", "relation": "预言", "confidence": 0.85},
            {"src": "委外合约人才管理组织", "dst": "乌尔里希", "relation": "协助", "confidence": 0.8},
            {"src": "洛伦兹研究所", "dst": "人工暴雨", "relation": "助力研究", "confidence": 0.8},
            {"src": "乌尔里希", "dst": "黑箱", "relation": "引用", "confidence": 0.7},
            {"src": "哑谜", "dst": "乌尔里希", "relation": "对话", "confidence": 0.8},
        ],
    },
    # v1.5 教授与爱兹拉：克劳福德、《轮回者实录》、喷雾清单
    "bd7b063fbc8d2ada": {
        "entities": [
            {"name": "教授", "type": "角色", "aliases": []},
            {"name": "爱兹拉", "type": "角色", "aliases": ["小爱兹拉"]},
            {"name": "克劳福德", "type": "角色", "aliases": ["克劳福德博士"]},
            {"name": "索菲婶婶", "type": "角色", "aliases": ["管理员索菲婶婶"]},
            {"name": "伦琴", "type": "角色", "aliases": ["伦琴先生"]},
            {"name": "轮回者实录", "type": "物品", "aliases": ["《轮回者实录》"]},
            {"name": "轮回者", "type": "概念", "aliases": ["“轮回者”"]},
            {"name": "喷雾类用品清单", "type": "物品", "aliases": ["随带喷雾类用品清单"]},
        ],
        "relations": [
            {"src": "爱兹拉", "dst": "教授", "relation": "对话", "confidence": 0.85},
            {"src": "教授", "dst": "克劳福德", "relation": "共事", "confidence": 0.85},
            {"src": "克劳福德", "dst": "轮回者实录", "relation": "著", "confidence": 0.85},
            {"src": "索菲婶婶", "dst": "轮回者实录", "relation": "管理借阅", "confidence": 0.7},
            {"src": "爱兹拉", "dst": "轮回者", "relation": "视作研究方向", "confidence": 0.75},
        ],
    },
    # v1.5 谣言的源头 + 白乳菇研究笔记
    "0e61b1432d685ede": {
        "entities": [
            {"name": "白乳菇", "type": "物品", "aliases": ["辣乳菇"]},
            {"name": "丹德农山脉", "type": "地点", "aliases": []},
            {"name": "研究笔记", "type": "物品", "aliases": ["研究笔记"]},
            {"name": "谣言的源头", "type": "概念", "aliases": ["谣言的源头"]},
        ],
        "relations": [
            {"src": "白乳菇", "dst": "丹德农山脉", "relation": "发现于", "confidence": 0.85},
            {"src": "研究笔记", "dst": "白乳菇", "relation": "记录", "confidence": 0.8},
        ],
    },
    # v? 神秘学家黑暗年代 + 不入流的儿歌 + 防身情报（魔精）
    "c6e68da25f219b39": {
        "entities": [
            {"name": "神秘学家", "type": "概念", "aliases": []},
            {"name": "黄蛉", "type": "角色", "aliases": []},
            {"name": "箱主", "type": "角色", "aliases": []},
            {"name": "纯白鸽", "type": "角色", "aliases": []},
            {"name": "魔精", "type": "角色", "aliases": ["魔精"]},
            {"name": "不入流的儿歌", "type": "物品", "aliases": ["不入流的儿歌"]},
            {"name": "油漆未干的门", "type": "物品", "aliases": ["油漆未干的门"]},
            {"name": "防身情报", "type": "物品", "aliases": ["防身情报", "防身芹报"]},
            {"name": "传单", "type": "物品", "aliases": ["传单"]},
        ],
        "relations": [
            {"src": "黄蛉", "dst": "纯白鸽", "relation": "杀害", "confidence": 0.7},
            {"src": "箱主", "dst": "纯白鸽", "relation": "见证死亡", "confidence": 0.7},
            {"src": "魔精", "dst": "传单", "relation": "传播", "confidence": 0.8},
        ],
    },
    # v? 勿忘我（大嘴巴布告栏）+ 纽约新闻报：橡木树林火灾、韦耶豪瑟破产
    "4c595eb32fc317d9": {
        "entities": [
            {"name": "勿忘我", "type": "角色", "aliases": []},
            {"name": "大嘴巴布告栏", "type": "物品", "aliases": ["《大嘴巴布告栏：读者投稿专栏》", "大嘴巴布告栏"]},
            {"name": "反酒馆联盟", "type": "组织", "aliases": []},
            {"name": "犹太教会", "type": "组织", "aliases": ["犹太教会"]},
            {"name": "国会", "type": "组织", "aliases": ["国会"]},
            {"name": "重塑人员", "type": "角色", "aliases": ["重塑人员"]},
            {"name": "纽约新闻报", "type": "物品", "aliases": ["《纽约新闻报》"]},
            {"name": "橡木树林", "type": "地点", "aliases": ["橡木树林"]},
            {"name": "韦耶豪瑟", "type": "角色", "aliases": ["韦耶豪瑟夫妇"]},
            {"name": "汤姆森·乔伊斯", "type": "角色", "aliases": []},
            {"name": "雪莱·杰拉德", "type": "角色", "aliases": []},
            {"name": "凯利·基思", "type": "角色", "aliases": []},
            {"name": "罗素·詹姆斯", "type": "角色", "aliases": ["施工负责人罗素·詹姆斯"]},
            {"name": "木材供应风波", "type": "事件", "aliases": ["木材供应风波"]},
        ],
        "relations": [
            {"src": "大嘴巴布告栏", "dst": "勿忘我", "relation": "报道", "confidence": 0.8},
            {"src": "纽约新闻报", "dst": "橡木树林", "relation": "报道", "confidence": 0.85},
            {"src": "韦耶豪瑟", "dst": "橡木树林", "relation": "遇难", "confidence": 0.8},
            {"src": "木材供应风波", "dst": "韦耶豪瑟", "relation": "致破产", "confidence": 0.85},
            {"src": "勿忘我", "dst": "反酒馆联盟", "relation": "知悉秘密", "confidence": 0.7},
            {"src": "勿忘我", "dst": "犹太教会", "relation": "知悉计划", "confidence": 0.7},
            {"src": "勿忘我", "dst": "国会", "relation": "知悉秘闻", "confidence": 0.7},
        ],
    },
    # v1.9 子弹 + 克拉尼图形的声音传播课题
    "9a24e54a6807de85": {
        "entities": [
            {"name": "子弹", "type": "角色", "aliases": ["这枚子弹"]},
            {"name": "克拉尼图形", "type": "概念", "aliases": ["克拉尼图形"]},
            {"name": "科算中心", "type": "组织", "aliases": ["科算中心"]},
            {"name": "乌尔里希", "type": "角色", "aliases": ["乌尔里希先生"]},
            {"name": "声音传播课题", "type": "物品", "aliases": ["运用克拉尼图形的声音传播课题"]},
        ],
        "relations": [
            {"src": "科算中心", "dst": "克拉尼图形", "relation": "统计波段", "confidence": 0.8},
            {"src": "乌尔里希", "dst": "克拉尼图形", "relation": "提供资料", "confidence": 0.8},
            {"src": "声音传播课题", "dst": "克拉尼图形", "relation": "运用", "confidence": 0.8},
        ],
    },
    # v1.9 大战前夕的来信 + 绳结的艺术
    "dfbfa7b1c5bf998b": {
        "entities": [
            {"name": "书箱", "type": "物品", "aliases": ["书箱"]},
            {"name": "绳结的艺术", "type": "物品", "aliases": ["绳结的艺术"]},
            {"name": "结", "type": "概念", "aliases": ["“结”"]},
            {"name": "匈牙利", "type": "地点", "aliases": []},
            {"name": "奥地利", "type": "地点", "aliases": []},
            {"name": "马扎尔", "type": "地点", "aliases": []},
            {"name": "日耳曼", "type": "地点", "aliases": []},
            {"name": "内莱塔尼亚", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "绳结的艺术", "dst": "结", "relation": "关于", "confidence": 0.85},
        ],
    },
    # v2.6 世界尽头的乌斯怀亚：十四行诗、虚构集、死刑犯
    "66da7f8dd90613fa": {
        "entities": [
            {"name": "乌斯怀亚", "type": "地点", "aliases": ["乌斯怀亚"]},
            {"name": "十四行诗", "type": "角色", "aliases": []},
            {"name": "虚构集", "type": "角色", "aliases": []},
            {"name": "死刑犯", "type": "角色", "aliases": ["死刑犯"]},
            {"name": "企鹅", "type": "角色", "aliases": ["企鹅"]},
            {"name": "监狱", "type": "地点", "aliases": ["监狱"]},
            {"name": "流放", "type": "概念", "aliases": ["流放"]},
        ],
        "relations": [
            {"src": "乌斯怀亚", "dst": "死刑犯", "relation": "流放至", "confidence": 0.85},
            {"src": "乌斯怀亚", "dst": "监狱", "relation": "关联", "confidence": 0.8},
            {"src": "乌斯怀亚", "dst": "流放", "relation": "关联", "confidence": 0.8},
            {"src": "十四行诗", "dst": "乌斯怀亚", "relation": "讨论", "confidence": 0.7},
            {"src": "虚构集", "dst": "乌斯怀亚", "relation": "讨论", "confidence": 0.7},
        ],
    },
    # v2.6 十四行诗与维尔汀论惩罚 + 破碎的邀请函（国家福柯学会）+ 奇怪术式
    "f424594d40ceb5ec": {
        "entities": [
            {"name": "十四行诗", "type": "角色", "aliases": []},
            {"name": "维尔汀", "type": "角色", "aliases": []},
            {"name": "司辰", "type": "角色", "aliases": []},
            {"name": "狱医先生", "type": "角色", "aliases": ["狱医先生"]},
            {"name": "德勒兹", "type": "角色", "aliases": []},
            {"name": "第一防线学校", "type": "组织", "aliases": ["第一防线学校"]},
            {"name": "国家福柯学会", "type": "组织", "aliases": ["国家福柯学会"]},
            {"name": "阿莱夫", "type": "角色", "aliases": ["阿莱夫先生"]},
            {"name": "何塞·达尔杜夫", "type": "角色", "aliases": []},
            {"name": "乌斯怀亚", "type": "地点", "aliases": []},
            {"name": "科马拉监狱", "type": "地点", "aliases": ["科马拉监狱"]},
            {"name": "重塑之手", "type": "组织", "aliases": ["重塑之手"]},
            {"name": "规训与惩罚", "type": "物品", "aliases": ["规训与惩罚"]},
            {"name": "管理型权力", "type": "概念", "aliases": ["管理型权力"]},
            {"name": "神秘学家", "type": "概念", "aliases": ["神秘学家"]},
        ],
        "relations": [
            {"src": "十四行诗", "dst": "维尔汀", "relation": "对话", "confidence": 0.8},
            {"src": "维尔汀", "dst": "第一防线学校", "relation": "提及", "confidence": 0.7},
            {"src": "第一防线学校", "dst": "规训与惩罚", "relation": "符合", "confidence": 0.8},
            {"src": "德勒兹", "dst": "管理型权力", "relation": "提出", "confidence": 0.8},
            {"src": "国家福柯学会", "dst": "阿莱夫", "relation": "邀请", "confidence": 0.85},
            {"src": "何塞·达尔杜夫", "dst": "国家福柯学会", "relation": "代表", "confidence": 0.8},
            {"src": "何塞·达尔杜夫", "dst": "科马拉监狱", "relation": "署名于", "confidence": 0.8},
            {"src": "重塑之手", "dst": "神秘学家", "relation": "需要", "confidence": 0.7},
            {"src": "十四行诗", "dst": "司辰", "relation": "对话", "confidence": 0.8},
            {"src": "维尔汀", "dst": "狱医先生", "relation": "讨论", "confidence": 0.8},
        ],
    },
    # v2.6 亦去亦返 + 密谈：桑托斯、芝诺士兵、基金会布宜诺斯艾利斯分部舰队
    "9c6e7060cadaa36f": {
        "entities": [
            {"name": "科马拉监狱", "type": "地点", "aliases": ["科马拉监狱"]},
            {"name": "重塑之手", "type": "组织", "aliases": ["重塑之手"]},
            {"name": "乌斯怀亚", "type": "地点", "aliases": []},
            {"name": "桑托斯", "type": "角色", "aliases": []},
            {"name": "芝诺士兵", "type": "角色", "aliases": ["芝诺士兵"]},
            {"name": "伊戈尔", "type": "角色", "aliases": []},
            {"name": "天使兄弟会", "type": "组织", "aliases": ["天使兄弟会"]},
            {"name": "芝诺", "type": "组织", "aliases": ["芝诺"]},
            {"name": "传道者", "type": "角色", "aliases": ["传道者"]},
            {"name": "基金会布宜诺斯艾利斯分部", "type": "组织", "aliases": ["基金会布宜诺斯艾利斯分部"]},
            {"name": "战列巡洋舰", "type": "物品", "aliases": ["战列巡洋舰"]},
            {"name": "驱逐舰", "type": "物品", "aliases": ["驱逐舰"]},
            {"name": "阿莱夫", "type": "角色", "aliases": ["阿莱夫先生", "“阿莱夫”"]},
        ],
        "relations": [
            {"src": "伊戈尔", "dst": "芝诺士兵", "relation": "派遣", "confidence": 0.8},
            {"src": "芝诺士兵", "dst": "桑托斯", "relation": "传达", "confidence": 0.8},
            {"src": "桑托斯", "dst": "天使兄弟会", "relation": "代表", "confidence": 0.8},
            {"src": "芝诺", "dst": "基金会布宜诺斯艾利斯分部", "relation": "拦截消息", "confidence": 0.8},
            {"src": "基金会布宜诺斯艾利斯分部", "dst": "战列巡洋舰", "relation": "派遣", "confidence": 0.8},
            {"src": "基金会布宜诺斯艾利斯分部", "dst": "驱逐舰", "relation": "派遣", "confidence": 0.8},
            {"src": "重塑之手", "dst": "科马拉监狱", "relation": "成员驻留", "confidence": 0.7},
        ],
    },
    # v3.5 洛伦兹蝴蝶与阿莱夫：语言学家、超忆症 + 除灵指南（龙舌兰等）
    "c7c3126a58125426": {
        "entities": [
            {"name": "洛伦兹蝴蝶", "type": "角色", "aliases": []},
            {"name": "阿莱夫", "type": "角色", "aliases": []},
            {"name": "语言学家", "type": "角色", "aliases": ["“语言学家”"]},
            {"name": "拉普拉斯", "type": "组织", "aliases": ["拉普拉斯"]},
            {"name": "超忆症", "type": "概念", "aliases": ["超忆症"]},
            {"name": "阿玛尔菲塔诺", "type": "概念", "aliases": ["阿玛尔菲塔诺"]},
            {"name": "龙舌兰", "type": "物品", "aliases": ["龙舌兰"]},
            {"name": "墨西哥香菜", "type": "物品", "aliases": ["Epazote"]},
            {"name": "芸香", "type": "物品", "aliases": ["芸香"]},
            {"name": "除灵指南", "type": "物品", "aliases": ["“必要”的除灵指南", "除灵指南"]},
            {"name": "一成不变房间", "type": "概念", "aliases": ["“一成不变房间”"]},
            {"name": "永恒的大火", "type": "事件", "aliases": ["永恒的大火"]},
        ],
        "relations": [
            {"src": "洛伦兹蝴蝶", "dst": "阿莱夫", "relation": "对话", "confidence": 0.8},
            {"src": "洛伦兹蝴蝶", "dst": "语言学家", "relation": "提及", "confidence": 0.7},
            {"src": "拉普拉斯", "dst": "阿莱夫", "relation": "提供居所", "confidence": 0.8},
            {"src": "阿莱夫", "dst": "超忆症", "relation": "患", "confidence": 0.8},
            {"src": "阿莱夫", "dst": "永恒的大火", "relation": "经历", "confidence": 0.8},
            {"src": "除灵指南", "dst": "龙舌兰", "relation": "记载", "confidence": 0.85},
            {"src": "除灵指南", "dst": "墨西哥香菜", "relation": "记载", "confidence": 0.85},
            {"src": "除灵指南", "dst": "芸香", "relation": "记载", "confidence": 0.85},
        ],
    },
    # v3.5 除灵指南续：科巴脂、迷迭香、阿兹特克太阳石
    "fcfb4c1e24ad9e1b": {
        "entities": [
            {"name": "科巴脂", "type": "物品", "aliases": ["科巴脂"]},
            {"name": "迷迭香", "type": "物品", "aliases": ["迷迭香"]},
            {"name": "阿兹特克太阳石", "type": "物品", "aliases": ["阿兹特克日历"]},
            {"name": "托纳蒂乌", "type": "角色", "aliases": ["太阳神托纳蒂乌"]},
            {"name": "美洲虎", "type": "角色", "aliases": ["美洲虎"]},
            {"name": "太阳", "type": "概念", "aliases": ["“太阳”"]},
            {"name": "诸灵节", "type": "事件", "aliases": ["诸灵节"]},
            {"name": "阿兹特克", "type": "概念", "aliases": ["阿兹特克"]},
            {"name": "玛雅", "type": "概念", "aliases": ["玛雅"]},
            {"name": "太阳石的故事", "type": "物品", "aliases": ["太阳石的故事"]},
            {"name": "古老日历", "type": "物品", "aliases": ["古老日历"]},
        ],
        "relations": [
            {"src": "科巴脂", "dst": "阿兹特克", "relation": "祭祀使用", "confidence": 0.8},
            {"src": "科巴脂", "dst": "诸灵节", "relation": "用于", "confidence": 0.85},
            {"src": "阿兹特克太阳石", "dst": "托纳蒂乌", "relation": "刻画", "confidence": 0.85},
            {"src": "阿兹特克太阳石", "dst": "太阳", "relation": "记录", "confidence": 0.8},
            {"src": "美洲虎", "dst": "太阳", "relation": "吞噬", "confidence": 0.8},
            {"src": "阿兹特克太阳石", "dst": "阿兹特克", "relation": "属于", "confidence": 0.8},
            {"src": "太阳石的故事", "dst": "阿兹特克太阳石", "relation": "讲述", "confidence": 0.8},
        ],
    },
    # v? 壁画密室：比安卡致乌切洛的信 + 观测实验记录（苏芙比、APPLe）
    "37f28a9cf5f0d807": {
        "entities": [
            {"name": "乌切洛", "type": "角色", "aliases": ["乌切洛"]},
            {"name": "比安卡", "type": "角色", "aliases": []},
            {"name": "普拉托韦基奥", "type": "地点", "aliases": ["普拉托韦基奥"]},
            {"name": "里皮", "type": "角色", "aliases": ["里皮"]},
            {"name": "乔万尼", "type": "角色", "aliases": ["乔万尼"]},
            {"name": "壁画之谜", "type": "物品", "aliases": ["壁画之谜"]},
            {"name": "佛罗伦萨奇观", "type": "地点", "aliases": ["佛罗伦萨奇观"]},
            {"name": "脚手架", "type": "物品", "aliases": ["脚手架"]},
            {"name": "密室", "type": "地点", "aliases": ["密室"]},
            {"name": "苏芙比", "type": "角色", "aliases": ["苏芙比小姐"]},
            {"name": "苹果先生", "type": "角色", "aliases": ["APPLe先生"]},
            {"name": "观测指南", "type": "物品", "aliases": ["《观测指南》"]},
            {"name": "橄榄树", "type": "物品", "aliases": ["橄榄树"]},
            {"name": "无花果", "type": "物品", "aliases": ["无花果"]},
            {"name": "野餐布", "type": "物品", "aliases": ["野餐布"]},
        ],
        "relations": [
            {"src": "比安卡", "dst": "乌切洛", "relation": "致信", "confidence": 0.85},
            {"src": "乌切洛", "dst": "普拉托韦基奥", "relation": "返回", "confidence": 0.8},
            {"src": "里皮", "dst": "密室", "relation": "返回", "confidence": 0.7},
            {"src": "乔万尼", "dst": "密室", "relation": "返回", "confidence": 0.7},
            {"src": "苏芙比", "dst": "苹果先生", "relation": "同伴", "confidence": 0.7},
            {"src": "苏芙比", "dst": "观测指南", "relation": "引用", "confidence": 0.8},
            {"src": "壁画之谜", "dst": "佛罗伦萨奇观", "relation": "记述", "confidence": 0.7},
        ],
    },
    # v? X的实验记录（时空泡泡球雨幕舞台）+ 今日要闻（瓦维洛夫综合体、熊蜂）
    "ba413e87e5fca87f": {
        "entities": [
            {"name": "X", "type": "角色", "aliases": ["X"]},
            {"name": "惠更斯-菲涅尔干涉仪", "type": "物品", "aliases": ["惠更斯-菲涅尔干涉仪"]},
            {"name": "时空泡泡球雨幕舞台", "type": "概念", "aliases": ["时空泡泡球雨幕舞台"]},
            {"name": "黑箱", "type": "概念", "aliases": ["黑箱"]},
            {"name": "瓦维洛夫综合体", "type": "组织", "aliases": ["瓦维洛夫综合体"]},
            {"name": "熊蜂", "type": "物品", "aliases": ["“熊蜂”"]},
            {"name": "有机聚合物", "type": "物品", "aliases": ["有机聚合物"]},
            {"name": "火星", "type": "地点", "aliases": ["火星"]},
            {"name": "聚合物国际峰会", "type": "事件", "aliases": ["聚合物国际峰会"]},
            {"name": "小麦", "type": "物品", "aliases": ["小麦种子"]},
        ],
        "relations": [
            {"src": "X", "dst": "时空泡泡球雨幕舞台", "relation": "实验", "confidence": 0.8},
            {"src": "惠更斯-菲涅尔干涉仪", "dst": "时空泡泡球雨幕舞台", "relation": "建构", "confidence": 0.85},
            {"src": "X", "dst": "黑箱", "relation": "提及", "confidence": 0.7},
            {"src": "瓦维洛夫综合体", "dst": "小麦", "relation": "研发", "confidence": 0.85},
            {"src": "熊蜂", "dst": "有机聚合物", "relation": "搬运", "confidence": 0.8},
            {"src": "瓦维洛夫综合体", "dst": "火星", "relation": "计划栽培", "confidence": 0.7},
            {"src": "聚合物国际峰会", "dst": "有机聚合物", "relation": "推广", "confidence": 0.8},
        ],
    },
    # v3.0 “Ⅻ”小队成员档案：叶尔莫莱、梅蕾尔、刻雷乌斯 + 芝诺叛变审查
    "1b40bb6c3e91feb7": {
        "entities": [
            {"name": "刻雷乌斯", "type": "角色", "aliases": []},
            {"name": "叶尔莫莱", "type": "角色", "aliases": ["猎犬"]},
            {"name": "梅蕾尔", "type": "角色", "aliases": ["乌鸫"]},
            {"name": "Ⅻ小队", "type": "组织", "aliases": ["“Ⅻ”小队"]},
            {"name": "夜巡特遣管理局", "type": "组织", "aliases": ["夜巡特遣管理局"]},
            {"name": "第一防线学校", "type": "组织", "aliases": ["第一防线学校"]},
            {"name": "红弩箭中尉", "type": "角色", "aliases": ["红弩箭中尉"]},
            {"name": "莫莉德尔", "type": "角色", "aliases": ["莫莉德尔"]},
            {"name": "芝诺军备学院", "type": "组织", "aliases": ["芝诺军备学院"]},
            {"name": "圣保罗事件", "type": "事件", "aliases": ["圣保罗事件"]},
            {"name": "基金会", "type": "组织", "aliases": ["基金会"]},
            {"name": "澳大利亚", "type": "地点", "aliases": ["澳大利亚"]},
            {"name": "芝诺叛变", "type": "事件", "aliases": ["芝诺叛变"]},
        ],
        "relations": [
            {"src": "刻雷乌斯", "dst": "叶尔莫莱", "relation": "推荐", "confidence": 0.8},
            {"src": "叶尔莫莱", "dst": "夜巡特遣管理局", "relation": "任职", "confidence": 0.8},
            {"src": "叶尔莫莱", "dst": "Ⅻ小队", "relation": "加入", "confidence": 0.8},
            {"src": "梅蕾尔", "dst": "第一防线学校", "relation": "毕业", "confidence": 0.8},
            {"src": "梅蕾尔", "dst": "Ⅻ小队", "relation": "加入", "confidence": 0.8},
            {"src": "红弩箭中尉", "dst": "圣保罗事件", "relation": "逃离", "confidence": 0.8},
            {"src": "莫莉德尔", "dst": "红弩箭中尉", "relation": "协助", "confidence": 0.8},
            {"src": "红弩箭中尉", "dst": "基金会", "relation": "留驻", "confidence": 0.8},
            {"src": "芝诺军备学院", "dst": "芝诺叛变", "relation": "涉及", "confidence": 0.8},
        ],
    },
    # v3.0 近期有关重塑之手的报告：刻雷乌斯应急预案
    "9e158a3bee0effaf": {
        "entities": [
            {"name": "重塑之手", "type": "组织", "aliases": ["重塑之手"]},
            {"name": "刻雷乌斯", "type": "角色", "aliases": []},
            {"name": "委员会", "type": "组织", "aliases": ["委员会"]},
            {"name": "基金会", "type": "组织", "aliases": ["基金会"]},
            {"name": "芝诺", "type": "组织", "aliases": ["芝诺"]},
            {"name": "暴雨", "type": "事件", "aliases": ["“暴雨”"]},
            {"name": "应急预案", "type": "物品", "aliases": ["应急预案"]},
            {"name": "军队", "type": "组织", "aliases": ["直属军队"]},
        ],
        "relations": [
            {"src": "刻雷乌斯", "dst": "应急预案", "relation": "起草", "confidence": 0.85},
            {"src": "应急预案", "dst": "委员会", "relation": "提交", "confidence": 0.8},
            {"src": "应急预案", "dst": "重塑之手", "relation": "针对", "confidence": 0.85},
            {"src": "基金会", "dst": "军队", "relation": "拟建", "confidence": 0.8},
        ],
    },
    # v3.3 被遗落的俘虏日记：墨袍女巫、重塑之手走狗、秘之教诲者
    "a571233bedd5af75": {
        "entities": [
            {"name": "盲眼女人", "type": "角色", "aliases": ["盲眼女人"]},
            {"name": "墨袍女巫", "type": "角色", "aliases": ["墨袍女巫"]},
            {"name": "包亚雷什金", "type": "角色", "aliases": []},
            {"name": "阿尔乔姆", "type": "角色", "aliases": []},
            {"name": "麦列霍夫", "type": "角色", "aliases": []},
            {"name": "重塑之手", "type": "组织", "aliases": ["重塑之手的走狗"]},
            {"name": "秘之教诲者", "type": "概念", "aliases": ["秘之教诲者"]},
            {"name": "手术刀", "type": "物品", "aliases": ["手术刀"]},
            {"name": "俘虏日记", "type": "物品", "aliases": ["被遗落的俘虏日记", "俘虏日记"]},
        ],
        "relations": [
            {"src": "重塑之手", "dst": "包亚雷什金", "relation": "杀害", "confidence": 0.8},
            {"src": "重塑之手", "dst": "阿尔乔姆", "relation": "杀害", "confidence": 0.8},
            {"src": "重塑之手", "dst": "麦列霍夫", "relation": "杀害", "confidence": 0.8},
            {"src": "墨袍女巫", "dst": "秘之教诲者", "relation": "吟唱", "confidence": 0.8},
            {"src": "墨袍女巫", "dst": "手术刀", "relation": "递还", "confidence": 0.8},
            {"src": "俘虏日记", "dst": "重塑之手", "relation": "记录", "confidence": 0.7},
        ],
    },
    # v3.3 军报（伊戈尔部狮鹫军）+ 苦目树提取物
    "313d43ce53b447ca": {
        "entities": [
            {"name": "伊戈尔", "type": "角色", "aliases": ["伊戈尔"]},
            {"name": "狮鹫军", "type": "组织", "aliases": ["狮鹫军"]},
            {"name": "民兵团", "type": "组织", "aliases": ["民兵团"]},
            {"name": "神圣第七疗养院", "type": "组织", "aliases": ["神圣第七疗养院"]},
            {"name": "骑兵军", "type": "组织", "aliases": ["骑兵军"]},
            {"name": "苦目树", "type": "物品", "aliases": ["苦目树"]},
            {"name": "苦目素", "type": "物品", "aliases": ["苦目素"]},
            {"name": "拉普拉斯科算中心医疗技术组", "type": "组织", "aliases": ["拉普拉斯科算中心医疗技术组"]},
            {"name": "神秘学家", "type": "概念", "aliases": ["神秘学家"]},
            {"name": "学术无界", "type": "概念", "aliases": ["学术无界"]},
        ],
        "relations": [
            {"src": "伊戈尔", "dst": "狮鹫军", "relation": "统领", "confidence": 0.85},
            {"src": "狮鹫军", "dst": "民兵团", "relation": "协同", "confidence": 0.8},
            {"src": "民兵团", "dst": "神圣第七疗养院", "relation": "保全", "confidence": 0.8},
            {"src": "民兵团", "dst": "骑兵军", "relation": "请求协助", "confidence": 0.8},
            {"src": "苦目树", "dst": "苦目素", "relation": "提取", "confidence": 0.85},
            {"src": "拉普拉斯科算中心医疗技术组", "dst": "苦目素", "relation": "收入药典", "confidence": 0.8},
            {"src": "苦目素", "dst": "神秘学家", "relation": "作用", "confidence": 0.8},
        ],
    },
    # v3.9 和平乌鲁 + 某人的独身生活挑战记录
    "ec8e4dfe37543f25": {
        "entities": [
            {"name": "和平乌鲁", "type": "角色", "aliases": ["和平乌鲁"]},
            {"name": "伊萨卡国王", "type": "角色", "aliases": ["伊萨卡国王"]},
            {"name": "半神英雄", "type": "角色", "aliases": ["半神英雄"]},
            {"name": "独身生活挑战记录", "type": "物品", "aliases": ["独身生活挑战记录"]},
            {"name": "十二挑战", "type": "事件", "aliases": ["十二挑战"]},
        ],
        "relations": [
            {"src": "独身生活挑战记录", "dst": "伊萨卡国王", "relation": "援引", "confidence": 0.7},
            {"src": "独身生活挑战记录", "dst": "半神英雄", "relation": "援引", "confidence": 0.7},
            {"src": "半神英雄", "dst": "十二挑战", "relation": "完成", "confidence": 0.8},
        ],
    },
    # v3.1 血食怪声明 + 安娜贝尔的日记
    "ab38721a4f1d5ac7": {
        "entities": [
            {"name": "血食怪", "type": "角色", "aliases": ["血食怪"]},
            {"name": "感染种", "type": "角色", "aliases": ["感染种"]},
            {"name": "超自然者", "type": "概念", "aliases": ["超自然者"]},
            {"name": "基金会", "type": "组织", "aliases": ["基金会"]},
            {"name": "安娜贝尔", "type": "角色", "aliases": ["安娜贝尔"]},
            {"name": "小威廉", "type": "角色", "aliases": ["小威廉"]},
            {"name": "多萝西女士", "type": "角色", "aliases": ["多萝西女士"]},
            {"name": "伊斯坦布尔", "type": "地点", "aliases": ["伊斯坦布尔"]},
            {"name": "布达佩斯", "type": "地点", "aliases": ["布达佩斯"]},
            {"name": "安娜贝尔的日记", "type": "物品", "aliases": ["安娜贝尔的日记"]},
            {"name": "小熊", "type": "物品", "aliases": ["小熊"]},
            {"name": "多巴什蛋糕", "type": "物品", "aliases": ["多巴什蛋糕"]},
        ],
        "relations": [
            {"src": "基金会", "dst": "血食怪", "relation": "归类", "confidence": 0.85},
            {"src": "基金会", "dst": "超自然者", "relation": "归类", "confidence": 0.85},
            {"src": "血食怪", "dst": "感染种", "relation": "转化", "confidence": 0.85},
            {"src": "安娜贝尔", "dst": "安娜贝尔的日记", "relation": "撰写", "confidence": 0.85},
            {"src": "安娜贝尔", "dst": "小威廉", "relation": "同伴", "confidence": 0.8},
            {"src": "安娜贝尔", "dst": "多萝西女士", "relation": "随行", "confidence": 0.8},
            {"src": "安娜贝尔", "dst": "伊斯坦布尔", "relation": "离开", "confidence": 0.8},
            {"src": "安娜贝尔", "dst": "布达佩斯", "relation": "前往", "confidence": 0.8},
            {"src": "安娜贝尔", "dst": "血食怪", "relation": "向往", "confidence": 0.7},
            {"src": "安娜贝尔", "dst": "小熊", "relation": "持有", "confidence": 0.7},
            {"src": "安娜贝尔", "dst": "多巴什蛋糕", "relation": "期待", "confidence": 0.7},
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
    print(f"[apply-missing-p11] 写入 {len(RESULTS)} 条")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
