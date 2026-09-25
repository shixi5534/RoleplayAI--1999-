# -*- coding: utf-8 -*-
"""未抽取剧情块补抽 · 第 30 批（backfill2 batch_20，20 块，含 2 个重复 hash，18 唯一）。

用法：
  python scripts/apply_missing_p30.py            # 预演（悬空+落地自检）
  python scripts/apply_missing_p30.py --apply    # 写盘
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

# 本批纯数值/技能/UI 页（无剧情）：643283c38c4fdab4（技能页）、759d30c5ea40eecf（技能页）、
# d4f3a44ed5e1a6d9（传递火炬任务 UI 页）。
NOOP_ADD: list[str] = [
    "643283c38c4fdab4",
    "759d30c5ea40eecf",
    "d4f3a44ed5e1a6d9",
]

RESULTS: dict[str, dict] = {
    # 1) 基金会普通职员数值页 · 尾部角色描述（碎纸机/儿童锁）
    "c695cc648c8ded67": {
        "entities": [
            {"name": "基金会", "type": "组织", "aliases": []},
            {"name": "碎纸机", "type": "物品", "aliases": []},
            {"name": "儿童锁", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "碎纸机", "dst": "儿童锁", "relation": "需配", "confidence": 0.7},
        ],
    },
    # 4) 旧友来信 · 阿派朗学派与火山岛人、维尔汀、37、流溢
    "ff46c24d3c487dd6": {
        "entities": [
            {"name": "维尔汀", "type": "角色", "aliases": ["维尔汀小姐"]},
            {"name": "阿派朗学派", "type": "组织", "aliases": []},
            {"name": "火山岛人", "type": "概念", "aliases": []},
            {"name": "火山岛", "type": "地点", "aliases": []},
            {"name": "流溢", "type": "概念", "aliases": ['“流溢”']},
            {"name": "37", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "阿派朗学派", "dst": "维尔汀", "relation": "致信", "confidence": 0.8},
            {"src": "阿派朗学派", "dst": "火山岛人", "relation": "信仰分歧", "confidence": 0.8},
            {"src": "阿派朗学派", "dst": "流溢", "relation": "受波及", "confidence": 0.7},
            {"src": "火山岛人", "dst": "火山岛", "relation": "居于", "confidence": 0.8},
            {"src": "37", "dst": "阿派朗学派", "relation": "隶属", "confidence": 0.7},
        ],
    },
    # 5) 重启机器论坛 · 语言异化症、重塑之手、暴雨、科算中心、安保部门
    "c43ad217d08c3f24": {
        "entities": [
            {"name": "语言异化症", "type": "概念", "aliases": ['“语言异化症”']},
            {"name": "重塑之手", "type": "组织", "aliases": []},
            {"name": "暴雨", "type": "现象", "aliases": ['“暴雨”']},
            {"name": "科算中心", "type": "组织", "aliases": []},
            {"name": "安保部门", "type": "组织", "aliases": []},
            {"name": "兔毛手袋", "type": "物品", "aliases": []},
            {"name": "服务器", "type": "物品", "aliases": []},
            {"name": "约翰", "type": "角色", "aliases": ["十六进制约翰"]},
        ],
        "relations": [
            {"src": "暴雨", "dst": "语言异化症", "relation": "引发", "confidence": 0.8},
            {"src": "科算中心", "dst": "暴雨", "relation": "被波及", "confidence": 0.7},
            {"src": "安保部门", "dst": "语言异化症", "relation": "处置", "confidence": 0.7},
            {"src": "语言异化症", "dst": "服务器", "relation": "损毁", "confidence": 0.8},
            {"src": "约翰", "dst": "兔毛手袋", "relation": "超越", "confidence": 0.7},
        ],
    },
    # 6) ？？？对话 · 十字架、战争、火灾（内容抽象，仅抽明确名词）
    "936f2c7f8e4382f5": {
        "entities": [
            {"name": "十字架", "type": "物品", "aliases": []},
            {"name": "战争", "type": "事件", "aliases": []},
            {"name": "火灾", "type": "事件", "aliases": []},
        ],
        "relations": [],
    },
    # 8) 基金会大楼会客层守卫数值页 · 基金会大楼
    "48088bb3cf872f45": {
        "entities": [
            {"name": "基金会大楼", "type": "地点", "aliases": []},
            {"name": "基金会", "type": "组织", "aliases": []},
        ],
        "relations": [
            {"src": "基金会大楼", "dst": "基金会", "relation": "属于", "confidence": 0.8},
        ],
    },
    # 9) 澳洲魔鬼蜥蜴 · 神秘学鞍具、古代运动员
    "5a55f68073d358fe": {
        "entities": [
            {"name": "魔鬼蜥蜴", "type": "角色", "aliases": []},
            {"name": "澳洲", "type": "地点", "aliases": []},
            {"name": "神秘学鞍具", "type": "物品", "aliases": []},
            {"name": "古代运动员", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "魔鬼蜥蜴", "dst": "澳洲", "relation": "化生自", "confidence": 0.7},
            {"src": "古代运动员", "dst": "神秘学鞍具", "relation": "定制", "confidence": 0.8},
            {"src": "神秘学鞍具", "dst": "魔鬼蜥蜴", "relation": "用于", "confidence": 0.8},
        ],
    },
    # 11) 人工梦游引导 · 战斗中对话拼接剧情
    "ff0023c72edd8600": {
        "entities": [
            {"name": "人工梦游引导", "type": "概念", "aliases": []},
        ],
        "relations": [],
    },
    # 12) 拉普拉斯康复中心时间表 · 珊迪、阿曼达、《诡丽幻谭》
    "ff5f1108c3f233d8": {
        "entities": [
            {"name": "拉普拉斯康复中心", "type": "地点", "aliases": []},
            {"name": "珊迪", "type": "角色", "aliases": []},
            {"name": "阿曼达", "type": "角色", "aliases": []},
            {"name": "诡丽幻谭", "type": "物品", "aliases": ["《诡丽幻谭》"]},
        ],
        "relations": [
            {"src": "珊迪", "dst": "拉普拉斯康复中心", "relation": "任职于", "confidence": 0.8},
            {"src": "阿曼达", "dst": "拉普拉斯康复中心", "relation": "任职于", "confidence": 0.8},
            {"src": "诡丽幻谭", "dst": "拉普拉斯康复中心", "relation": "存于", "confidence": 0.7},
        ],
    },
    # 13) 梅克卢战斗对话 · 新纪元集市、魔精、疗愈药草茶、鼠尾草、薰衣草
    "bb6be2fcf5f3c1d6": {
        "entities": [
            {"name": "梅克卢", "type": "角色", "aliases": []},
            {"name": "墨西哥卷", "type": "物品", "aliases": []},
            {"name": "新纪元集市", "type": "地点", "aliases": []},
            {"name": "鼠尾草", "type": "物品", "aliases": []},
            {"name": "薰衣草", "type": "物品", "aliases": []},
            {"name": "魔精", "type": "概念", "aliases": []},
            {"name": "灯球", "type": "物品", "aliases": []},
            {"name": "疗愈药草茶", "type": "物品", "aliases": ["疗——愈——药——草——茶"]},
        ],
        "relations": [
            {"src": "梅克卢", "dst": "魔精", "relation": "提及", "confidence": 0.7},
            {"src": "新纪元集市", "dst": "疗愈药草茶", "relation": "提供", "confidence": 0.7},
            {"src": "疗愈药草茶", "dst": "鼠尾草", "relation": "含", "confidence": 0.7},
            {"src": "疗愈药草茶", "dst": "薰衣草", "relation": "含", "confidence": 0.7},
        ],
    },
    # 14) 魔鬼蜥蜴愤懑 · 片段（正文仅见“魔鬼”引号写法）
    "e3c7bf0ba93e3cab": {
        "entities": [
            {"name": "魔鬼蜥蜴", "type": "角色", "aliases": ["魔鬼"]},
        ],
        "relations": [],
    },
    # 15) 阿兹特克人密码纸 · 佩雷斯、走私名单、卡尔维尔、勒德-罗朗
    "53965159906579ca": {
        "entities": [
            {"name": "阿兹特克人", "type": "概念", "aliases": []},
            {"name": "佩雷斯", "type": "角色", "aliases": ['佩雷斯“先生”']},
            {"name": "密码纸", "type": "物品", "aliases": ['佩雷斯“先生”的密码纸']},
            {"name": "傲慢与偏见", "type": "物品", "aliases": ['“傲慢与偏见”']},
            {"name": "走私名单", "type": "物品", "aliases": ["一份走私名单"]},
            {"name": "卡尔维尔", "type": "角色", "aliases": []},
            {"name": "勒德-罗朗", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "佩雷斯", "dst": "密码纸", "relation": "持有", "confidence": 0.7},
            {"src": "卡尔维尔", "dst": "走私名单", "relation": "列入", "confidence": 0.8},
            {"src": "勒德-罗朗", "dst": "走私名单", "relation": "列入", "confidence": 0.8},
        ],
    },
    # 16) 弃票箱与小狗儿之歌 · 约翰·灰镜·布朗、《纽约每日报》
    "0ebab92b0f0bef8f": {
        "entities": [
            {"name": "弃票箱", "type": "概念", "aliases": ['“弃票箱”']},
            {"name": "约翰·灰镜·布朗", "type": "角色", "aliases": []},
            {"name": "纽约每日报", "type": "物品", "aliases": ["《纽约每日报》"]},
            {"name": "小狗儿之歌", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "约翰·灰镜·布朗", "dst": "纽约每日报", "relation": "撰稿", "confidence": 0.8},
        ],
    },
    # 17) 英文对话 · Mr.Crolic 与 vultures（正文为英文，名即原文）
    "0e9c550cbf9a6580": {
        "entities": [
            {"name": "Mr.Crolic", "type": "角色", "aliases": []},
            {"name": "vultures", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "Mr.Crolic", "dst": "vultures", "relation": "论及", "confidence": 0.7},
        ],
    },
    # 18) 雨伞之前 · 桥毁山上的寺庙、元天堂
    "1a989685b6ffd959": {
        "entities": [
            {"name": "雨伞", "type": "概念", "aliases": []},
            {"name": "桥", "type": "地点", "aliases": ["桥头"]},
            {"name": "山上的寺庙", "type": "地点", "aliases": []},
            {"name": "元天堂", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "桥", "dst": "山上的寺庙", "relation": "毁灭", "confidence": 0.7},
        ],
    },
    # 19/20) 佩城眼疾对话 · 北人、胡人、官府、过所
    "8799d461cb9bae5b": {
        "entities": [
            {"name": "佩城", "type": "地点", "aliases": []},
            {"name": "北人", "type": "概念", "aliases": []},
            {"name": "胡人", "type": "概念", "aliases": []},
            {"name": "官府", "type": "组织", "aliases": []},
            {"name": "过所", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "胡人", "dst": "佩城", "relation": "抵达", "confidence": 0.7},
        ],
    },
    # 2/3) 技能页（无剧情） → NOOP
    "643283c38c4fdab4": {
        "entities": [],
        "relations": [],
    },
    # 10) 技能页（无剧情） → NOOP
    "759d30c5ea40eecf": {
        "entities": [],
        "relations": [],
    },
    # 7) 传递火炬任务 UI 页（无剧情） → NOOP
    "d4f3a44ed5e1a6d9": {
        "entities": [],
        "relations": [],
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
    print(f"[apply-missing-p30] 写入 {len(RESULTS)} 条，NOOP +{len(NOOP_ADD)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
