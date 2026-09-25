#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""补抽 2 个漏网高价值块（d71d5583a8796e4b / 3a79f546855e938e）。
手工抽取，写盘前 validate() 悬空自检 + landing() 落地自检。"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "knowledge" / "plot_cache" / "wu_ming_zhe"
CORPUS = ROOT / "data" / "knowledge" / "plot_corpus_wu_ming_zhe.json"

RESULTS = {
    "d71d5583a8796e4b": {
        "entities": [
            {"name": "格鲁托夫", "type": "角色", "aliases": []},
            {"name": "风网", "type": "概念", "aliases": ["“风网”"]},
            {"name": "飞蛾", "type": "角色", "aliases": []},
            {"name": "普莱玛", "type": "角色", "aliases": []},
            {"name": "火渡船", "type": "角色", "aliases": []},
            {"name": "阿尔卡纳", "type": "组织", "aliases": []},
            {"name": "鸽子屋", "type": "组织", "aliases": ["“鸽子屋”"]},
            {"name": "内务部", "type": "组织", "aliases": ["“内务部”"]},
            {"name": "芝诺", "type": "组织", "aliases": []},
            {"name": "基金会", "type": "组织", "aliases": []},
            {"name": "阿尔卡纳入侵行动评估报告", "type": "物品", "aliases": []},
            {"name": "阿尔卡纳入侵事件", "type": "事件", "aliases": []},
        ],
        "relations": [
            {"src": "飞蛾", "dst": "普莱玛", "relation": "窃取情报", "confidence": 0.9},
            {"src": "阿尔卡纳", "dst": "阿尔卡纳入侵事件", "relation": "发起", "confidence": 0.9},
            {"src": "阿尔卡纳", "dst": "鸽子屋", "relation": "试探", "confidence": 0.9},
            {"src": "阿尔卡纳", "dst": "内务部", "relation": "测试", "confidence": 0.85},
            {"src": "阿尔卡纳入侵行动评估报告", "dst": "阿尔卡纳入侵事件", "relation": "评估", "confidence": 0.95},
            {"src": "阿尔卡纳入侵行动评估报告", "dst": "内务部", "relation": "建议伪装", "confidence": 0.8},
            {"src": "内务部", "dst": "基金会", "relation": "隶属", "confidence": 0.75},
            {"src": "格鲁托夫", "dst": "风网", "relation": "知晓", "confidence": 0.85},
        ],
    },
    "3a79f546855e938e": {
        "entities": [
            {"name": "每日鉴报", "type": "组织", "aliases": ["《每日鉴报》"]},
            {"name": "乌卢鲁运动会", "type": "事件", "aliases": ["乌卢鲁赛事"]},
            {"name": "笃笃骨", "type": "角色", "aliases": []},
            {"name": "鬼婆", "type": "角色", "aliases": []},
            {"name": "雾怪事件", "type": "事件", "aliases": ["“雾怪事件”"]},
            {"name": "帝国航空", "type": "组织", "aliases": []},
            {"name": "救济医院", "type": "地点", "aliases": ["市区救济医院"]},
            {"name": "伦敦", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "每日鉴报", "dst": "乌卢鲁运动会", "relation": "报道", "confidence": 0.9},
            {"src": "笃笃骨", "dst": "雾怪事件", "relation": "化解", "confidence": 0.85},
            {"src": "鬼婆", "dst": "雾怪事件", "relation": "制造", "confidence": 0.8},
            {"src": "笃笃骨", "dst": "鬼婆", "relation": "被质疑作秀", "confidence": 0.7},
            {"src": "乌卢鲁运动会", "dst": "伦敦", "relation": "改变环境", "confidence": 0.8},
            {"src": "帝国航空", "dst": "乌卢鲁运动会", "relation": "运送运动员", "confidence": 0.8},
        ],
    },
}


def _norm(s: str) -> str:
    return (s or "").strip().lower().replace(" ", "").replace("\n", "").replace("\r", "")


def validate() -> int:
    bad = 0
    for h, d in RESULTS.items():
        pool = set()
        for e in d.get("entities") or []:
            nm = e.get("name") or ""
            pool.add(nm)
            pool |= set(e.get("aliases") or [])
        for r in d.get("relations") or []:
            if r.get("src") not in pool or r.get("dst") not in pool:
                print(f"[dangling] {h} {r.get('src')} -> {r.get('dst')}")
                bad += 1
    return bad


def landing() -> int:
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    text_by_hash = {c["hash"]: c.get("text", "") for c in corpus["chunks"]}
    bad = 0
    for h, d in RESULTS.items():
        ntext = _norm(text_by_hash.get(h, ""))
        if not ntext:
            print(f"[landing-missing-corpus] {h}")
            bad += 1
            continue
        for e in d.get("entities") or []:
            cands = [e.get("name") or ""] + list(e.get("aliases") or [])
            if not any(_norm(c) in ntext for c in cands):
                print(f"[landing-fail] {h} entity={e.get('name')} aliases={e.get('aliases')}")
                bad += 1
    return bad


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    v, m = validate(), landing()
    total_e = sum(len(d.get("entities") or []) for d in RESULTS.values())
    total_r = sum(len(d.get("relations") or []) for d in RESULTS.values())
    print(f"[validate] 块 {len(RESULTS)}，悬空 {v}，未落地 {m}")
    print(f"[stats] 实体 {total_e}，关系 {total_r}")
    if v or m:
        print("[ABORT] 存在悬空或未落地，未写盘")
        return 1
    if not args.apply:
        print("[dry-run] 加 --apply 写盘")
        return 0
    CACHE.mkdir(parents=True, exist_ok=True)
    for h, d in RESULTS.items():
        (CACHE / f"{h}.json").write_text(
            json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    print(f"[apply-missing-p33] 写入 {len(RESULTS)} 条")
    return 0


if __name__ == "__main__":
    sys.exit(main())
