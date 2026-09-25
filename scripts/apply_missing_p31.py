# -*- coding: utf-8 -*-
"""未抽取剧情块补抽 · 第 31 批（backfill2 batch_21，20 块）。

用法：
  python scripts/apply_missing_p31.py            # 预演（悬空+落地自检）
  python scripts/apply_missing_p31.py --apply    # 写盘
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

# 本批 5 块为角色技能/数值页（无剧情）：
#   1c41a8fbdac296c3（共荣秩序技能页）
#   6035f79b219deb9c（燥热鼓点技能页）
#   c7e579e4c14f1a64（怨念技能页）
#   5453d8a4b55b12a9（高频麻醉电流器技能页）
#   f8161649eab753c9（叮刺/荼毒技能页）
NOOP_ADD: list[str] = [
    "1c41a8fbdac296c3",
    "6035f79b219deb9c",
    "c7e579e4c14f1a64",
    "5453d8a4b55b12a9",
    "f8161649eab753c9",
]

RESULTS: dict[str, dict] = {
    # 1) 流浪汉与消防斧 · 角色卡叙事+技能页（抽叙事部分）
    "8d2e1ec79ac4c97f": {
        "entities": [
            {"name": "流浪汉", "type": "角色", "aliases": ["不修边幅的流浪汉"]},
            {"name": "消防斧", "type": "物品", "aliases": ["褪色的消防斧"]},
            {"name": "护工", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "流浪汉", "dst": "消防斧", "relation": "持有", "confidence": 0.8},
        ],
    },
    # 2) 马克西姆死亡秘密文件 · 聚合物展览馆能源室
    "94f1d3c1a43c417c": {
        "entities": [
            {"name": "秘密文件", "type": "物品", "aliases": []},
            {"name": "马克西姆", "type": "角色", "aliases": []},
            {"name": "聚合物展览馆", "type": "地点", "aliases": []},
            {"name": "能源室", "type": "地点", "aliases": []},
            {"name": "金属手表", "type": "物品", "aliases": []},
            {"name": "啁啾表链", "type": "物品", "aliases": []},
            {"name": "制式手枪", "type": "物品", "aliases": []},
            {"name": "国家政治局", "type": "组织", "aliases": []},
        ],
        "relations": [
            {"src": "秘密文件", "dst": "聚合物展览馆", "relation": "位于", "confidence": 0.8},
            {"src": "秘密文件", "dst": "能源室", "relation": "位于", "confidence": 0.8},
            {"src": "金属手表", "dst": "马克西姆", "relation": "属于", "confidence": 0.8},
            {"src": "啁啾表链", "dst": "马克西姆", "relation": "属于", "confidence": 0.8},
            {"src": "制式手枪", "dst": "马克西姆", "relation": "属于", "confidence": 0.8},
            {"src": "国家政治局", "dst": "秘密文件", "relation": "签署", "confidence": 0.8},
        ],
    },
    # 3) 圣帕勒基地对话 · 中国女孩/艇群/飞行艇/Vigil/代理长Alton/公主
    "bb300f37288a09b0": {
        "entities": [
            {"name": "中国女孩", "type": "角色", "aliases": []},
            {"name": "艇群", "type": "组织", "aliases": ["有名的艇群"]},
            {"name": "飞行艇", "type": "物品", "aliases": []},
            {"name": "圣帕勒基地", "type": "地点", "aliases": []},
            {"name": "Vigil", "type": "角色", "aliases": []},
            {"name": "Alton", "type": "角色", "aliases": ["代理长Alton"]},
            {"name": "公主", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "中国女孩", "dst": "艇群", "relation": "出身于", "confidence": 0.7},
            {"src": "飞行艇", "dst": "中国女孩", "relation": "聚集", "confidence": 0.7},
            {"src": "Vigil", "dst": "圣帕勒基地", "relation": "任职于", "confidence": 0.8},
            {"src": "Vigil", "dst": "Alton", "relation": "引荐", "confidence": 0.7},
            {"src": "公主", "dst": "中国女孩", "relation": "是", "confidence": 0.7},
        ],
    },
    # 4) 求祝县论坛目录 · 板块与发帖人
    "0481c266899ea289": {
        "entities": [
            {"name": "求祝县", "type": "地点", "aliases": []},
            {"name": "论坛", "type": "概念", "aliases": []},
            {"name": "高跷马", "type": "组织", "aliases": []},
            {"name": "神秘术", "type": "概念", "aliases": []},
            {"name": "白马道", "type": "地点", "aliases": []},
            {"name": "求祝县县志", "type": "物品", "aliases": []},
            {"name": "城中公园", "type": "地点", "aliases": []},
            {"name": "梅花树", "type": "物品", "aliases": []},
            {"name": "小小草", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "小小草", "dst": "论坛", "relation": "发帖于", "confidence": 0.7},
            {"src": "梅花树", "dst": "城中公园", "relation": "位于", "confidence": 0.8},
            {"src": "求祝县县志", "dst": "求祝县", "relation": "关于", "confidence": 0.7},
        ],
    },
    # 5) 韦耶豪瑟夫妇纵火案报道 · 起死回生剂捐赠三方
    "1c44573074c4ec31": {
        "entities": [
            {"name": "韦耶豪瑟夫妇", "type": "角色", "aliases": []},
            {"name": "起死回生剂", "type": "物品", "aliases": ["基础版起死回生剂"]},
            {"name": "纽约玛利亚疗养院", "type": "组织", "aliases": []},
            {"name": "俄亥俄州圣心疗养所", "type": "组织", "aliases": []},
            {"name": "长老会医疗中心", "type": "组织", "aliases": []},
            {"name": "林业用地", "type": "地点", "aliases": []},
            {"name": "市警署", "type": "组织", "aliases": []},
            {"name": "神秘学家", "type": "概念", "aliases": []},
            {"name": "詹姆斯·威尔斯", "type": "角色", "aliases": []},
            {"name": "多丽·约翰逊", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "韦耶豪瑟夫妇", "dst": "起死回生剂", "relation": "捐赠", "confidence": 0.8},
            {"src": "纽约玛利亚疗养院", "dst": "起死回生剂", "relation": "获赠", "confidence": 0.7},
            {"src": "俄亥俄州圣心疗养所", "dst": "起死回生剂", "relation": "获赠", "confidence": 0.7},
            {"src": "长老会医疗中心", "dst": "起死回生剂", "relation": "获赠", "confidence": 0.7},
            {"src": "韦耶豪瑟夫妇", "dst": "林业用地", "relation": "抛售", "confidence": 0.8},
            {"src": "市警署", "dst": "韦耶豪瑟夫妇", "relation": "调查", "confidence": 0.7},
            {"src": "詹姆斯·威尔斯", "dst": "韦耶豪瑟夫妇", "relation": "报道", "confidence": 0.8},
            {"src": "多丽·约翰逊", "dst": "韦耶豪瑟夫妇", "relation": "报道", "confidence": 0.8},
        ],
    },
    # 6) 重塑之手的造物 · 技能页叙事（明确出现"重塑之手"）
    "a2234bcfa0e836c4": {
        "entities": [
            {"name": "重塑之手", "type": "组织", "aliases": []},
            {"name": "造物", "type": "物品", "aliases": ["模仿的空壳"]},
            {"name": "灵魂", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "重塑之手", "dst": "造物", "relation": "创造", "confidence": 0.85},
            {"src": "造物", "dst": "灵魂", "relation": "缺乏", "confidence": 0.7},
        ],
    },
    # 7) 研究员藏宝图谜题 · 约翰·提托/乌尔里希/洛佩拉
    "a9162a2f8ad5a9e0": {
        "entities": [
            {"name": "研究员", "type": "角色", "aliases": []},
            {"name": "约翰·提托", "type": "角色", "aliases": []},
            {"name": "乌尔里希", "type": "角色", "aliases": []},
            {"name": "藏宝图", "type": "物品", "aliases": []},
            {"name": "计算机室", "type": "地点", "aliases": []},
            {"name": "澳大利亚", "type": "地点", "aliases": []},
            {"name": "打点卡", "type": "物品", "aliases": []},
            {"name": "解读器", "type": "物品", "aliases": []},
            {"name": "草稿纸", "type": "物品", "aliases": []},
            {"name": "洛佩拉", "type": "角色", "aliases": []},
            {"name": "往日的分径", "type": "概念", "aliases": ["往日的分径-洛佩拉"]},
        ],
        "relations": [
            {"src": "研究员", "dst": "藏宝图", "relation": "发现", "confidence": 0.7},
            {"src": "乌尔里希", "dst": "草稿纸", "relation": "丢弃", "confidence": 0.7},
            {"src": "打点卡", "dst": "计算机室", "relation": "来自", "confidence": 0.7},
            {"src": "打点卡", "dst": "解读器", "relation": "投入", "confidence": 0.7},
            {"src": "洛佩拉", "dst": "往日的分径", "relation": "拥有", "confidence": 0.8},
        ],
    },
    # 8) "免费"情报与"暴雨"研究 · 芝诺/基金会/科算中心
    "4f40d69a35da6547": {
        "entities": [
            {"name": "暴雨", "type": "现象", "aliases": ["“暴雨”"]},
            {"name": "暴雨研究", "type": "概念", "aliases": ["“暴雨”研究"]},
            {"name": "芝诺", "type": "组织", "aliases": []},
            {"name": "基金会", "type": "组织", "aliases": []},
            {"name": "科算中心", "type": "组织", "aliases": []},
            {"name": "东线", "type": "地点", "aliases": []},
            {"name": "免费情报", "type": "物品", "aliases": ["“免费”情报"]},
            {"name": "残缺的报告", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "芝诺", "dst": "暴雨研究", "relation": "进行", "confidence": 0.8},
            {"src": "基金会", "dst": "暴雨研究", "relation": "进行", "confidence": 0.8},
            {"src": "暴雨研究", "dst": "暴雨", "relation": "关于", "confidence": 0.8},
            {"src": "科算中心", "dst": "暴雨研究", "relation": "不知情", "confidence": 0.7},
            {"src": "残缺的报告", "dst": "暴雨研究", "relation": "提及", "confidence": 0.7},
        ],
    },
    # 9) 展览报道（英文）· Egon Ervin Kish / The Pan / Steinerhaus
    "2cd447d185b0622c": {
        "entities": [
            {"name": "Egon Ervin Kish", "type": "角色", "aliases": []},
            {"name": "New Free Press", "type": "组织", "aliases": []},
            {"name": "The Pan", "type": "组织", "aliases": []},
            {"name": "Die Fakl", "type": "组织", "aliases": []},
            {"name": "Alfred Rädl", "type": "角色", "aliases": ["ColonelAlfred Rädl"]},
            {"name": "Adolf Loos", "type": "角色", "aliases": []},
            {"name": "Steinerhaus", "type": "地点", "aliases": ["theSteinerhaus"]},
            {"name": "Maximilian Hohne", "type": "角色", "aliases": ["Major Maximilian Hohne"]},
            {"name": "exhibition", "type": "事件", "aliases": []},
        ],
        "relations": [
            {"src": "Egon Ervin Kish", "dst": "New Free Press", "relation": "任职于", "confidence": 0.8},
            {"src": "Egon Ervin Kish", "dst": "The Pan", "relation": "任职于", "confidence": 0.8},
            {"src": "Egon Ervin Kish", "dst": "Die Fakl", "relation": "创立", "confidence": 0.8},
            {"src": "Egon Ervin Kish", "dst": "Alfred Rädl", "relation": "揭露", "confidence": 0.8},
            {"src": "Adolf Loos", "dst": "Steinerhaus", "relation": "设计", "confidence": 0.8},
            {"src": "Maximilian Hohne", "dst": "exhibition", "relation": "参观", "confidence": 0.7},
        ],
    },
    # 10) 展览报道（英文变体）· Aegon Erwin Kish / the PAN / Steiner House
    "9939acaec1637505": {
        "entities": [
            {"name": "Aegon Erwin Kish", "type": "角色", "aliases": []},
            {"name": "New Free Press", "type": "组织", "aliases": []},
            {"name": "the PAN", "type": "组织", "aliases": []},
            {"name": "Die Fakl", "type": "组织", "aliases": []},
            {"name": "Alfred Riedel", "type": "角色", "aliases": ["ColonelAlfred Riedel"]},
            {"name": "Adolf Loos", "type": "角色", "aliases": []},
            {"name": "Steiner House", "type": "地点", "aliases": ["theSteiner House"]},
            {"name": "Maximilian Hohne", "type": "角色", "aliases": ["Major Maximilian Hohne"]},
            {"name": "exhibition", "type": "事件", "aliases": []},
        ],
        "relations": [
            {"src": "Aegon Erwin Kish", "dst": "New Free Press", "relation": "任职于", "confidence": 0.8},
            {"src": "Aegon Erwin Kish", "dst": "the PAN", "relation": "任职于", "confidence": 0.8},
            {"src": "Aegon Erwin Kish", "dst": "Die Fakl", "relation": "创立", "confidence": 0.8},
            {"src": "Aegon Erwin Kish", "dst": "Alfred Riedel", "relation": "揭露", "confidence": 0.8},
            {"src": "Adolf Loos", "dst": "Steiner House", "relation": "设计", "confidence": 0.8},
            {"src": "Maximilian Hohne", "dst": "exhibition", "relation": "参观", "confidence": 0.7},
        ],
    },
    # 11) 波斯尼亚军事演习笔记（英文）· Tanya / circle / Arcanum
    "0a5ea2774580006e": {
        "entities": [
            {"name": "The Sorrows of Young Weather", "type": "物品", "aliases": []},
            {"name": "Tanya", "type": "角色", "aliases": []},
            {"name": "circle", "type": "组织", "aliases": []},
            {"name": "magic", "type": "概念", "aliases": []},
            {"name": "Bosnia and Herzegovina", "type": "地点", "aliases": []},
            {"name": "military exercise", "type": "事件", "aliases": []},
            {"name": "Conrad Toulouse Power", "type": "角色", "aliases": ["General Conrad Toulouse Power"]},
            {"name": "Atlantic Ocean", "type": "地点", "aliases": []},
            {"name": "Arcanum", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "Tanya", "dst": "circle", "relation": "描述", "confidence": 0.7},
            {"src": "circle", "dst": "magic", "relation": "属于", "confidence": 0.7},
            {"src": "military exercise", "dst": "Bosnia and Herzegovina", "relation": "位于", "confidence": 0.8},
        ],
    },
    # 12) 北领地活动安全法问答（英文）· Uluru / City Government Service Center
    "02c3cb07cd356372": {
        "entities": [
            {"name": "Northern Territory Event Security Law", "type": "概念", "aliases": []},
            {"name": "type 3 field safety certification", "type": "概念", "aliases": []},
            {"name": "Uluru", "type": "地点", "aliases": []},
            {"name": "City Government Service Center", "type": "地点", "aliases": []},
            {"name": "District B", "type": "地点", "aliases": []},
            {"name": "Window 13", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "City Government Service Center", "dst": "District B", "relation": "包含", "confidence": 0.7},
            {"src": "City Government Service Center", "dst": "Window 13", "relation": "设", "confidence": 0.7},
        ],
    },
    # 13) 牙仙与伦敦救助中心（英文）· little tacker / Tooth Fairy / Arthur
    "9d46ccc984e573a3": {
        "entities": [
            {"name": "little tacker", "type": "角色", "aliases": []},
            {"name": "Tooth Fairy", "type": "角色", "aliases": ["Ms.Tooth Fairy"]},
            {"name": "Arthur", "type": "角色", "aliases": []},
            {"name": "London Emergency Relief Center for Special Tuberculosis Patients", "type": "组织", "aliases": []},
            {"name": "hospital", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "little tacker", "dst": "hospital", "relation": "被护送", "confidence": 0.7},
            {"src": "Tooth Fairy", "dst": "little tacker", "relation": "求助", "confidence": 0.6},
            {"src": "Arthur", "dst": "London Emergency Relief Center for Special Tuberculosis Patients", "relation": "命名", "confidence": 0.7},
            {"src": "London Emergency Relief Center for Special Tuberculosis Patients", "dst": "hospital", "relation": "是", "confidence": 0.8},
        ],
    },
    # 14) 旅程与壁画（英文）· Mom / Melbourne / Uluru / murals
    "a4c4bf8942fe3c7f": {
        "entities": [
            {"name": "Mom", "type": "角色", "aliases": []},
            {"name": "mankind", "type": "概念", "aliases": []},
            {"name": "mission", "type": "概念", "aliases": []},
            {"name": "Annual Jump of Frog Mushroom", "type": "物品", "aliases": []},
            {"name": "Fairy Ring Powders", "type": "物品", "aliases": []},
            {"name": "Butterfly Shaped PortobelloMushroom", "type": "物品", "aliases": []},
            {"name": "Melbourne", "type": "地点", "aliases": []},
            {"name": "Uluru", "type": "地点", "aliases": []},
            {"name": "murals", "type": "物品", "aliases": []},
            {"name": "journey", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "Mom", "dst": "mission", "relation": "传达", "confidence": 0.7},
            {"src": "mission", "dst": "mankind", "relation": "关乎", "confidence": 0.7},
            {"src": "journey", "dst": "Melbourne", "relation": "始于", "confidence": 0.7},
            {"src": "journey", "dst": "Uluru", "relation": "接近", "confidence": 0.7},
            {"src": "murals", "dst": "Uluru", "relation": "位于", "confidence": 0.7},
        ],
    },
    # 15) 德文诗歌片段 · Tosca / Schauspielerin / Silenz / Redetorske
    "dc12a9fd63d4026c": {
        "entities": [
            {"name": "Tosca", "type": "角色", "aliases": []},
            {"name": "Schauspielerin", "type": "角色", "aliases": []},
            {"name": "Silenz", "type": "概念", "aliases": ["Die Zeit der Silenz"]},
            {"name": "Redetorske", "type": "角色", "aliases": []},
            {"name": "Traum", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "Redetorske", "dst": "Traum", "relation": "表现", "confidence": 0.7},
        ],
    },
    # 16/17/18/19/20) 数值/技能页 → NOOP（见 NOOP_ADD）
    "1c41a8fbdac296c3": {"entities": [], "relations": []},
    "6035f79b219deb9c": {"entities": [], "relations": []},
    "c7e579e4c14f1a64": {"entities": [], "relations": []},
    "5453d8a4b55b12a9": {"entities": [], "relations": []},
    "f8161649eab753c9": {"entities": [], "relations": []},
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
    print(f"[apply-missing-p31] 写入 {len(RESULTS)} 条，NOOP +{len(NOOP_ADD)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
