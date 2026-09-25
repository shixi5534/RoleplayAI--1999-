# -*- coding: utf-8 -*-
"""未抽取剧情块补抽 · 第 32 批（backfill2 batch_22，16 块，含 3 个数值页 NOOP）。

用法：
  python scripts/apply_missing_p32.py            # 预演（悬空+落地自检）
  python scripts/apply_missing_p32.py --apply    # 写盘
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

# 本批 3 块为角色技能/数值页（无剧情）：67cfe67357ebedfd、91bcbdcfb271e568、041aa7c214eb1e39
NOOP_ADD: list[str] = [
    "67cfe67357ebedfd",
    "91bcbdcfb271e568",
    "041aa7c214eb1e39",
]

RESULTS: dict[str, dict] = {
    # 1) 人质对峙 · DAA 现身
    "ac2416380925a408": {
        "entities": [
            {"name": "DAA", "type": "角色", "aliases": []},
            {"name": "hostage", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "DAA", "dst": "hostage", "relation": "介入", "confidence": 0.6},
        ],
    },
    # 2) 传送技术论证 · 波形/神秘术/经验论
    "da0d3c1bada2018b": {
        "entities": [
            {"name": "波形", "type": "概念", "aliases": []},
            {"name": "神秘术", "type": "概念", "aliases": []},
            {"name": "传送技术", "type": "概念", "aliases": []},
            {"name": "航天技术", "type": "概念", "aliases": []},
            {"name": "外卖技术", "type": "概念", "aliases": []},
            {"name": "经验论", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "神秘术", "dst": "传送技术", "relation": "提供能量", "confidence": 0.8},
            {"src": "传送技术", "dst": "航天技术", "relation": "凌驾于", "confidence": 0.8},
            {"src": "传送技术", "dst": "经验论", "relation": "基于", "confidence": 0.7},
        ],
    },
    # 3) 技能/数值页（无剧情） → NOOP
    "67cfe67357ebedfd": {
        "entities": [],
        "relations": [],
    },
    # 4) 卡纳比街追捕 · Ragged Lad / 警长威廉 / Diggers
    "c778d9a86a7ba360": {
        "entities": [
            {"name": "Ragged Lad", "type": "角色", "aliases": []},
            {"name": "Carnaby Street", "type": "地点", "aliases": []},
            {"name": "Sergeant William", "type": "角色", "aliases": []},
            {"name": "Diggers", "type": "角色", "aliases": []},
            {"name": "seal", "type": "物品", "aliases": []},
            {"name": "police", "type": "组织", "aliases": []},
            {"name": "trap", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "Ragged Lad", "dst": "trap", "relation": "闯入", "confidence": 0.8},
            {"src": "Sergeant William", "dst": "seal", "relation": "遗失", "confidence": 0.8},
            {"src": "Diggers", "dst": "police", "relation": "伪造证件", "confidence": 0.7},
            {"src": "Diggers", "dst": "police", "relation": "攻击", "confidence": 0.7},
        ],
    },
    # 5) 贝壳与婴孩 · Savina / Pops / 火
    "cc0276546b812c4d": {
        "entities": [
            {"name": "shell", "type": "物品", "aliases": []},
            {"name": "door", "type": "物品", "aliases": []},
            {"name": "Savina", "type": "角色", "aliases": []},
            {"name": "baby", "type": "角色", "aliases": []},
            {"name": "Pops", "type": "角色", "aliases": []},
            {"name": "torches", "type": "物品", "aliases": []},
            {"name": "chains", "type": "物品", "aliases": []},
            {"name": "fire", "type": "现象", "aliases": []},
        ],
        "relations": [
            {"src": "Savina", "dst": "baby", "relation": "呼喊", "confidence": 0.8},
            {"src": "Pops", "dst": "torches", "relation": "持", "confidence": 0.7},
            {"src": "Pops", "dst": "chains", "relation": "持", "confidence": 0.7},
            {"src": "door", "dst": "fire", "relation": "起火", "confidence": 0.8},
        ],
    },
    # 6) 汽车旅馆相遇 · Wind / 糖果 / 羊
    "9c5bbd6de804ba9d": {
        "entities": [
            {"name": "candy", "type": "物品", "aliases": []},
            {"name": "Halloween", "type": "概念", "aliases": []},
            {"name": "Wind", "type": "角色", "aliases": []},
            {"name": "aerial stunts", "type": "事件", "aliases": []},
            {"name": "motel", "type": "地点", "aliases": []},
            {"name": "sheep", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "Wind", "dst": "motel", "relation": "身处", "confidence": 0.8},
            {"src": "Wind", "dst": "aerial stunts", "relation": "观看", "confidence": 0.7},
            {"src": "Wind", "dst": "sheep", "relation": "听见", "confidence": 0.7},
        ],
    },
    # 7) 乌鲁预选赛 · 黑雾 / 火山 / 十字街
    "72fe5c7f15dc02fa": {
        "entities": [
            {"name": "Uluru Qualifiers", "type": "事件", "aliases": []},
            {"name": "Flutterpage", "type": "角色", "aliases": []},
            {"name": "Uluru Fair", "type": "事件", "aliases": []},
            {"name": "Black Fog", "type": "现象", "aliases": []},
            {"name": "volcanoes", "type": "地点", "aliases": []},
            {"name": "Cross Street", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "Flutterpage", "dst": "Uluru Qualifiers", "relation": "参与", "confidence": 0.8},
            {"src": "Black Fog", "dst": "volcanoes", "relation": "没入", "confidence": 0.7},
        ],
    },
    # 8) 薇洛的诅咒 · 血布 / 机油
    "0dad7cc27c8a3e55": {
        "entities": [
            {"name": "Willow", "type": "角色", "aliases": []},
            {"name": "curse", "type": "概念", "aliases": []},
            {"name": "Bloodstained rags", "type": "物品", "aliases": []},
            {"name": "arcane skills", "type": "概念", "aliases": []},
            {"name": "Machine lubricant", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "Willow", "dst": "curse", "relation": "降下", "confidence": 0.8},
        ],
    },
    # 9) 伦敦乌鲁展会 · 标记鸟夺冠 / 十字街重建体育场
    "2411c786bc3b422a": {
        "entities": [
            {"name": "London Uluru Exhibition Games", "type": "事件", "aliases": []},
            {"name": "Cross Street", "type": "地点", "aliases": []},
            {"name": "stadium", "type": "地点", "aliases": []},
            {"name": "painting", "type": "物品", "aliases": []},
            {"name": "marking bird", "type": "角色", "aliases": []},
            {"name": "gold medal", "type": "物品", "aliases": []},
            {"name": "singing competition", "type": "事件", "aliases": []},
        ],
        "relations": [
            {"src": "Cross Street", "dst": "stadium", "relation": "重建", "confidence": 0.8},
            {"src": "marking bird", "dst": "gold medal", "relation": "获得", "confidence": 0.8},
            {"src": "marking bird", "dst": "singing competition", "relation": "夺冠", "confidence": 0.8},
            {"src": "painting", "dst": "London Uluru Exhibition Games", "relation": "不符主题", "confidence": 0.7},
        ],
    },
    # 10) 德语镜中独白 · 医生 / 灵魂 / 布
    "500eda98ce5b60d4": {
        "entities": [
            {"name": "Spiegel", "type": "物品", "aliases": []},
            {"name": "Seele", "type": "概念", "aliases": []},
            {"name": "Doktor", "type": "角色", "aliases": []},
            {"name": "Tuch", "type": "物品", "aliases": []},
            {"name": "Licht", "type": "现象", "aliases": []},
            {"name": "Vorhänge", "type": "物品", "aliases": []},
            {"name": "Ideale", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "Doktor", "dst": "Ideale", "relation": "怀抱", "confidence": 0.8},
            {"src": "Spiegel", "dst": "Seele", "relation": "映照", "confidence": 0.7},
        ],
    },
    # 11) 通风系统失控 · 机器人追狗 / Austin Vader 致歉 Iverson
    "5afb8eec0728d1ad": {
        "entities": [
            {"name": "ventilation system", "type": "物品", "aliases": []},
            {"name": "dog fur", "type": "物品", "aliases": []},
            {"name": "dog", "type": "角色", "aliases": []},
            {"name": "robots", "type": "角色", "aliases": []},
            {"name": "Austin Vader", "type": "角色", "aliases": []},
            {"name": "Mr. Iverson", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "robots", "dst": "dog", "relation": "追捕", "confidence": 0.8},
            {"src": "dog", "dst": "dog fur", "relation": "遗留", "confidence": 0.7},
            {"src": "Austin Vader", "dst": "Mr. Iverson", "relation": "致歉", "confidence": 0.8},
        ],
    },
    # 12) 藏身怯懦 · Mr. Jinn / Cheena / Mata / Raj
    "608428d8e0b96f41": {
        "entities": [
            {"name": "Mr. Jinn", "type": "角色", "aliases": []},
            {"name": "Cheena", "type": "角色", "aliases": []},
            {"name": "Pati", "type": "角色", "aliases": []},
            {"name": "Dada", "type": "角色", "aliases": []},
            {"name": "Mata", "type": "角色", "aliases": []},
            {"name": "monsters", "type": "角色", "aliases": []},
            {"name": "Raj", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "Cheena", "dst": "Mr. Jinn", "relation": "求助", "confidence": 0.7},
            {"src": "Mr. Jinn", "dst": "Cheena", "relation": "安抚", "confidence": 0.8},
            {"src": "Pati", "dst": "Cheena", "relation": "叮嘱", "confidence": 0.7},
            {"src": "Dada", "dst": "Cheena", "relation": "叮嘱", "confidence": 0.7},
            {"src": "Mata", "dst": "monsters", "relation": "畏惧", "confidence": 0.8},
            {"src": "Raj", "dst": "monsters", "relation": "畏惧", "confidence": 0.7},
        ],
    },
    # 13) 病床争执 · Ms P-Pudding / 医生 / Qiang Liao 拒召
    "f9b19920612e75bb": {
        "entities": [
            {"name": "Ms P-Pudding", "type": "角色", "aliases": []},
            {"name": "doctor", "type": "角色", "aliases": []},
            {"name": "Poitier", "type": "角色", "aliases": []},
            {"name": "Teng Leng", "type": "角色", "aliases": []},
            {"name": "Qiang Liao", "type": "角色", "aliases": []},
            {"name": "summon", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "doctor", "dst": "Ms P-Pudding", "relation": "嘱咐卧床", "confidence": 0.8},
            {"src": "Qiang Liao", "dst": "Poitier", "relation": "拒绝召唤", "confidence": 0.8},
            {"src": "Teng Leng", "dst": "Poitier", "relation": "为友", "confidence": 0.7},
        ],
    },
    # 14) 蒙特利尔异兽 · 咒语 / LSCC / Montullo
    "20a3d04411bbc6c0": {
        "entities": [
            {"name": "incantations", "type": "概念", "aliases": []},
            {"name": "manipulation incantation", "type": "概念", "aliases": []},
            {"name": "shadow incantation", "type": "概念", "aliases": []},
            {"name": "Montreal", "type": "角色", "aliases": []},
            {"name": "Miss New Bible Critter Rehabilitation Center", "type": "组织", "aliases": []},
            {"name": "LSCC", "type": "组织", "aliases": []},
            {"name": "Montullo", "type": "角色", "aliases": []},
            {"name": "Arkin materials", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "manipulation incantation", "dst": "incantations", "relation": "属于", "confidence": 0.8},
            {"src": "shadow incantation", "dst": "incantations", "relation": "属于", "confidence": 0.8},
            {"src": "Montreal", "dst": "Miss New Bible Critter Rehabilitation Center", "relation": "源自", "confidence": 0.8},
            {"src": "Montreal", "dst": "LSCC", "relation": "获认可", "confidence": 0.8},
            {"src": "Montullo", "dst": "Arkin materials", "relation": "消耗", "confidence": 0.8},
        ],
    },
    # 15) 技能/数值页（无剧情） → NOOP
    "91bcbdcfb271e568": {
        "entities": [],
        "relations": [],
    },
    # 16) 技能/数值页（无剧情） → NOOP
    "041aa7c214eb1e39": {
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
    print(f"[apply-missing-p32] 写入 {len(RESULTS)} 条，NOOP +{len(NOOP_ADD)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
