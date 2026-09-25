# -*- coding: utf-8 -*-
"""未抽取剧情块补抽 · 第 29 批（backfill2 batch_19，19 块，含 1 个重复 hash）。

用法：
  python scripts/apply_missing_p29.py            # 预演（悬空+落地自检）
  python scripts/apply_missing_p29.py --apply    # 写盘
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

# 本批数值/技能页（无剧情正文）：a6e5f901(阿派朗学派)、51fabd49(句尾的暗喻，重复2次)、
# d70d1713(魔精之主)、e25accd5(剧院观众)。
NOOP_ADD: list[str] = [
    "a6e5f9010cae9c0b",
    "51fabd4906bef4b8",
    "d70d17135777949f",
    "e25accd5c9e21b5d",
]

RESULTS: dict[str, dict] = {
    # 0) 数值/技能页（无剧情）→ NOOP
    "a6e5f9010cae9c0b": {"entities": [], "relations": []},
    # 1) 阿其翁与船长 · 沙滩淘金者（拼接两段：织毯独白 + 小径探索）
    "6f0f83203abe169c": {
        "entities": [
            {"name": "阿其翁", "type": "概念", "aliases": []},
            {"name": "船长", "type": "角色", "aliases": []},
            {"name": "淘金者", "type": "概念", "aliases": []},
            {"name": "沙滩", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "阿其翁", "dst": "船长", "relation": "阻挡", "confidence": 0.7},
            {"src": "淘金者", "dst": "沙滩", "relation": "聚集于", "confidence": 0.7},
        ],
    },
    # 2) 伪证的反义词 · 执夜人问话（重塑之手/贝丽尔/迷思海）
    "15d8ace03bb8808a": {
        "entities": [
            {"name": "执夜人", "type": "角色", "aliases": []},
            {"name": "灰调蓝", "type": "角色", "aliases": []},
            {"name": "重塑之手", "type": "组织", "aliases": []},
            {"name": "罗西", "type": "角色", "aliases": []},
            {"name": "西莉亚", "type": "角色", "aliases": []},
            {"name": "贝丽尔·布翁尼", "type": "角色", "aliases": ["贝丽尔"]},
            {"name": "迷思海", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "罗西", "dst": "重塑之手", "relation": "隶属", "confidence": 0.8},
            {"src": "罗西", "dst": "西莉亚", "relation": "诱骗", "confidence": 0.8},
            {"src": "灰调蓝", "dst": "重塑之手", "relation": "被迫参与", "confidence": 0.8},
            {"src": "贝丽尔·布翁尼", "dst": "灰调蓝", "relation": "帮助", "confidence": 0.8},
            {"src": "贝丽尔·布翁尼", "dst": "迷思海", "relation": "逃离", "confidence": 0.7},
            {"src": "贝丽尔·布翁尼", "dst": "重塑之手", "relation": "无同谋", "confidence": 0.7},
        ],
    },
    # 3) 混语对话 · 王先生就医与DAA工作（中国城场景）
    "3138a80e4132fdf9": {
        "entities": [
            {"name": "王先生", "type": "角色", "aliases": ["Mr.Wong"]},
            {"name": "医生", "type": "角色", "aliases": []},
            {"name": "DAA", "type": "组织", "aliases": []},
            {"name": "中国小孩", "type": "角色", "aliases": []},
            {"name": "Liang老师", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "王先生", "dst": "医生", "relation": "求诊", "confidence": 0.7},
        ],
    },
    # 4) 沛城胡商对话 · 过所与商队
    "11694696e9a7befa": {
        "entities": [
            {"name": "沛城", "type": "地点", "aliases": []},
            {"name": "胡商", "type": "角色", "aliases": []},
            {"name": "中原", "type": "地点", "aliases": []},
            {"name": "过所", "type": "物品", "aliases": []},
            {"name": "商队", "type": "组织", "aliases": []},
            {"name": "旅店", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "胡商", "dst": "沛城", "relation": "贸易于", "confidence": 0.8},
            {"src": "胡商", "dst": "中原", "relation": "出入", "confidence": 0.7},
            {"src": "商队", "dst": "过所", "relation": "需携带", "confidence": 0.7},
            {"src": "胡商", "dst": "旅店", "relation": "投宿", "confidence": 0.7},
        ],
    },
    # 5/6) 句尾的暗喻（技能/数值页，重复2次）→ NOOP
    "51fabd4906bef4b8": {"entities": [], "relations": []},
    # 7) 阿星离职与阿升饰演C-07 · Teresa赠笔记
    "52da2b14043504d8": {
        "entities": [
            {"name": "阿星", "type": "角色", "aliases": []},
            {"name": "老板", "type": "角色", "aliases": []},
            {"name": "阿声", "type": "角色", "aliases": []},
            {"name": "Teresa", "type": "角色", "aliases": []},
            {"name": "阿升", "type": "角色", "aliases": []},
            {"name": "C-07", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "Teresa", "dst": "阿升", "relation": "赠笔记", "confidence": 0.7},
            {"src": "阿升", "dst": "C-07", "relation": "饰演", "confidence": 0.8},
            {"src": "阿星", "dst": "老板", "relation": "辞别", "confidence": 0.7},
        ],
    },
    # 8) 中国城寻狗事件 · 财政官与狗狗警察（Vigilante/Nightpiercer）
    "8439d3076cbbb0e8": {
        "entities": [
            {"name": "财政官", "type": "角色", "aliases": []},
            {"name": "中国城", "type": "地点", "aliases": []},
            {"name": "狗狗警察", "type": "组织", "aliases": []},
            {"name": "Vigilante", "type": "角色", "aliases": []},
            {"name": "Nightpiercer", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "Vigilante", "dst": "Nightpiercer", "relation": "遭遇", "confidence": 0.7},
            {"src": "财政官", "dst": "中国城", "relation": "搜寻于", "confidence": 0.7},
        ],
    },
    # 9) 涣州官僚体系论坛 · 守备/巡检司/兵备道
    "d3c530dd4d69048c": {
        "entities": [
            {"name": "涣州", "type": "地点", "aliases": []},
            {"name": "守备", "type": "角色", "aliases": []},
            {"name": "巡检司", "type": "组织", "aliases": []},
            {"name": "巡检", "type": "角色", "aliases": []},
            {"name": "兵备道", "type": "组织", "aliases": []},
            {"name": "总兵", "type": "角色", "aliases": []},
            {"name": "巡抚", "type": "角色", "aliases": []},
            {"name": "弓兵", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "守备", "dst": "巡检司", "relation": "节制", "confidence": 0.8},
            {"src": "守备", "dst": "总兵", "relation": "受辖于", "confidence": 0.7},
            {"src": "守备", "dst": "巡抚", "relation": "受辖于", "confidence": 0.7},
            {"src": "巡检司", "dst": "守备", "relation": "受辖于", "confidence": 0.7},
            {"src": "巡检", "dst": "巡检司", "relation": "隶属", "confidence": 0.8},
            {"src": "弓兵", "dst": "巡检", "relation": "受统于", "confidence": 0.7},
            {"src": "守备", "dst": "涣州", "relation": "防妖于", "confidence": 0.8},
        ],
    },
    # 10) 杀伐棋盘 · 格鲁托夫战报（基金会/乐团/格蕾丝/风网）
    "480eb532f58b5570": {
        "entities": [
            {"name": "格鲁托夫", "type": "角色", "aliases": []},
            {"name": "基金会", "type": "组织", "aliases": []},
            {"name": "乐团", "type": "组织", "aliases": []},
            {"name": "格蕾丝", "type": "角色", "aliases": []},
            {"name": "风网", "type": "组织", "aliases": []},
            {"name": "歌唱家", "type": "角色", "aliases": []},
            {"name": "杀伐棋盘", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "格鲁托夫", "dst": "基金会", "relation": "蔑称", "confidence": 0.7},
            {"src": "格鲁托夫", "dst": "乐团", "relation": "质问", "confidence": 0.7},
            {"src": "格鲁托夫", "dst": "格蕾丝", "relation": "指责", "confidence": 0.7},
            {"src": "格蕾丝", "dst": "风网", "relation": "摧毁", "confidence": 0.7},
        ],
    },
    # 11) 乌卢鲁开业日传单 · 维克多电影院/普克占卜店/花园卡邦克鲁
    "73c904e783d0e84f": {
        "entities": [
            {"name": "乌卢鲁", "type": "事件", "aliases": []},
            {"name": "开业日", "type": "事件", "aliases": []},
            {"name": "维克多电影院", "type": "地点", "aliases": []},
            {"name": "乌卢鲁传奇运动员", "type": "物品", "aliases": ["《乌卢鲁传奇运动员》"]},
            {"name": "普克占卜店", "type": "地点", "aliases": []},
            {"name": "欢庆集市", "type": "地点", "aliases": []},
            {"name": "花园卡邦克鲁", "type": "角色", "aliases": []},
            {"name": "人类的……晴报", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "乌卢鲁", "dst": "欢庆集市", "relation": "举办于", "confidence": 0.8},
            {"src": "维克多电影院", "dst": "乌卢鲁传奇运动员", "relation": "上映", "confidence": 0.8},
            {"src": "普克占卜店", "dst": "乌卢鲁", "relation": "预测", "confidence": 0.7},
            {"src": "花园卡邦克鲁", "dst": "人类的……晴报", "relation": "听闻", "confidence": 0.7},
        ],
    },
    # 12) 数值/技能页（无剧情）→ NOOP
    "d70d17135777949f": {"entities": [], "relations": []},
    # 13) 拉普拉斯论坛 · 暴雨重建/露西女士/哑谜增殖
    "c687ea9952b6324a": {
        "entities": [
            {"name": "暴雨", "type": "现象", "aliases": ["“暴雨”"]},
            {"name": "拉普拉斯", "type": "组织", "aliases": []},
            {"name": "露西女士", "type": "角色", "aliases": []},
            {"name": "约翰", "type": "角色", "aliases": []},
            {"name": "哑谜", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "拉普拉斯", "dst": "暴雨", "relation": "重建于", "confidence": 0.7},
            {"src": "露西女士", "dst": "约翰", "relation": "询问", "confidence": 0.7},
            {"src": "哑谜", "dst": "拉普拉斯", "relation": "增殖于", "confidence": 0.7},
            {"src": "约翰", "dst": "拉普拉斯", "relation": "隶属", "confidence": 0.8},
        ],
    },
    # 14) 混语对话 · L.A.S.T.R.E.A.S.T.I.E.S./Vigils/Nightpiercer/圣帕维罗的基金
    "7d7980dc85fa18b3": {
        "entities": [
            {"name": "L.A.S.T.R.E.A.S.T.I.E.S.", "type": "组织", "aliases": []},
            {"name": "Vigils", "type": "组织", "aliases": []},
            {"name": "Nightpiercer", "type": "角色", "aliases": []},
            {"name": "圣帕维罗的基金", "type": "组织", "aliases": []},
            {"name": "Alden", "type": "角色", "aliases": []},
            {"name": "飞行艇", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "Nightpiercer", "dst": "Vigils", "relation": "困扰", "confidence": 0.7},
        ],
    },
    # 15) 混语对话 · Lathem/Latham/奥奇利人/Loggerhead
    "ed4e1e73a265c575": {
        "entities": [
            {"name": "Lathem", "type": "角色", "aliases": []},
            {"name": "Latham", "type": "角色", "aliases": []},
            {"name": "奥奇利人", "type": "概念", "aliases": []},
            {"name": "Loggerhead", "type": "角色", "aliases": []},
            {"name": "警察", "type": "角色", "aliases": []},
            {"name": "蓝色物体", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "Lathem", "dst": "蓝色物体", "relation": "抢夺", "confidence": 0.8},
            {"src": "Latham", "dst": "奥奇利人", "relation": "是", "confidence": 0.9},
            {"src": "Loggerhead", "dst": "Latham", "relation": "指称", "confidence": 0.8},
            {"src": "警察", "dst": "Lathem", "relation": "查明", "confidence": 0.7},
        ],
    },
    # 16) 核心图对话 · 策论/水火/河
    "ecda07e2a9828e5e": {
        "entities": [
            {"name": "策论", "type": "概念", "aliases": []},
            {"name": "核心图", "type": "物品", "aliases": []},
            {"name": "水", "type": "概念", "aliases": []},
            {"name": "火", "type": "概念", "aliases": []},
            {"name": "河", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "核心图", "dst": "水", "relation": "描绘", "confidence": 0.7},
            {"src": "核心图", "dst": "火", "relation": "描绘", "confidence": 0.7},
        ],
    },
    # 17) 科算中心论坛 · 露西离职/乌尔里希绝食/约翰被推举
    "e3b08ad121c76764": {
        "entities": [
            {"name": "露西", "type": "角色", "aliases": []},
            {"name": "乌尔里希", "type": "角色", "aliases": []},
            {"name": "科算中心", "type": "组织", "aliases": []},
            {"name": "约翰", "type": "角色", "aliases": []},
            {"name": "委员会大楼", "type": "地点", "aliases": []},
            {"name": "充电椅", "type": "物品", "aliases": []},
            {"name": "机械工程组", "type": "组织", "aliases": []},
        ],
        "relations": [
            {"src": "露西", "dst": "科算中心", "relation": "离职", "confidence": 0.8},
            {"src": "乌尔里希", "dst": "科算中心", "relation": "隶属", "confidence": 0.8},
            {"src": "乌尔里希", "dst": "委员会大楼", "relation": "绝食抗议于", "confidence": 0.7},
            {"src": "乌尔里希", "dst": "充电椅", "relation": "拒绝就坐", "confidence": 0.7},
            {"src": "约翰", "dst": "机械工程组", "relation": "隶属", "confidence": 0.8},
            {"src": "约翰", "dst": "科算中心", "relation": "被推举", "confidence": 0.7},
        ],
    },
    # 18) 数值/技能页（无剧情）→ NOOP
    "e25accd5c9e21b5d": {"entities": [], "relations": []},
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
    print(f"[apply-missing-p29] 写入 {len(RESULTS)} 条，NOOP +{len(NOOP_ADD)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
