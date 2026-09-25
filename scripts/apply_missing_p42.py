#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""补抽 backfill5/pro_00.txt 的 100 个边角块（外文 whisper 转写）。
逐块手工抽取实体/关系，写盘前 validate() 悬空自检 + landing() 落地自检（对照 pro_00.txt 正文）。
落地原则：外文正文 → 实体 name 直接用正文专名（连续子串），中文正名放 aliases。"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "knowledge" / "plot_cache" / "wu_ming_zhe"
PRO = ROOT / "data" / "knowledge" / "_audit" / "backfill5" / "pro_00.txt"

RESULTS = {
    "a18aeb0c60aefb2b": {"entities": [], "relations": []},
    "2980a6344f0d2c67": {"entities": [], "relations": []},
    "53212886ec8dce07": {"entities": [
        {"name": "Arthur", "type": "角色", "aliases": ["阿瑟"]},
    ], "relations": []},
    "a4eab9aca4d16b72": {"entities": [
        {"name": "South America", "type": "地点", "aliases": ["南美洲"]},
        {"name": "Ocean Conservation Association", "type": "组织", "aliases": ["海洋保护协会"]},
    ], "relations": []},
    "195b0d424e8eca06": {"entities": [
        {"name": "Regulus", "type": "角色", "aliases": ["雷古勒斯"]},
    ], "relations": []},
    "6e15ac8a262465a1": {"entities": [
        {"name": "Essam", "type": "角色", "aliases": ["埃萨姆"]},
        {"name": "Nova Scotia", "type": "地点", "aliases": ["新斯科舍"]},
    ], "relations": [
        {"src": "Essam", "dst": "Nova Scotia", "relation": "告别", "confidence": 0.8},
    ]},
    "b25196f5f6f428fe": {"entities": [
        {"name": "Ulrich", "type": "角色", "aliases": ["乌尔里希"]},
        {"name": "Jonathan", "type": "角色", "aliases": ["乔纳森"]},
        {"name": "artificial storm", "type": "现象", "aliases": ["人工风暴"]},
    ], "relations": [
        {"src": "Ulrich", "dst": "artificial storm", "relation": "策划", "confidence": 0.85},
    ]},
    "a65c8b5030bac28b": {"entities": [
        {"name": "Laplace", "type": "组织", "aliases": ["拉普拉斯"]},
        {"name": "Penelope", "type": "角色", "aliases": ["佩内洛普"]},
    ], "relations": []},
    "8a281d42a8151138": {"entities": [
        {"name": "Medicine Pocket", "type": "角色", "aliases": []},
        {"name": "1995", "type": "时间", "aliases": []},
        {"name": "artificial storm project", "type": "概念", "aliases": ["人工风暴项目"]},
    ], "relations": [
        {"src": "Medicine Pocket", "dst": "artificial storm project", "relation": "参与", "confidence": 0.85},
    ]},
    "99f2bc0158c3f98c": {"entities": [
        {"name": "Regulus", "type": "角色", "aliases": ["雷古勒斯"]},
        {"name": "Ulrich", "type": "角色", "aliases": ["乌尔里希"]},
        {"name": "Regulus satellite", "type": "物品", "aliases": ["雷古勒斯卫星"]},
        {"name": "Plesetsk", "type": "地点", "aliases": ["普列谢茨克"]},
        {"name": "asymmetrical nuclide r", "type": "物品", "aliases": []},
    ], "relations": [
        {"src": "Regulus", "dst": "Regulus satellite", "relation": "拥有", "confidence": 0.85},
        {"src": "Plesetsk", "dst": "Regulus satellite", "relation": "提供", "confidence": 0.8},
    ]},
    "9a3454a2560b06d2": {"entities": [
        {"name": "Lucas", "type": "角色", "aliases": ["卢卡斯"]},
        {"name": "storm", "type": "现象", "aliases": ["人工风暴", "the storm"]},
        {"name": "Lycopis lucidus", "type": "物品", "aliases": ["琉璃草"]},
    ], "relations": [
        {"src": "Lucas", "dst": "storm", "relation": "关注", "confidence": 0.8},
    ]},
    "512ca969b2565da5": {"entities": [], "relations": []},
    "b285e0293b011c75": {"entities": [], "relations": []},
    "809a77bc6162f22b": {"entities": [
        {"name": "Agnestins", "type": "组织", "aliases": []},
    ], "relations": []},
    "54632490e2dfcbcd": {"entities": [], "relations": []},
    "55228d40dcf881a2": {"entities": [], "relations": []},
    "1b93f2cfe7e2ab4d": {"entities": [
        {"name": "Schönbrunn Palace", "type": "地点", "aliases": ["美泉宫", "Schonbrunn Palace"]},
        {"name": "Austria-Hungary", "type": "地点", "aliases": ["奥匈帝国"]},
    ], "relations": [
        {"src": "Austria-Hungary", "dst": "Schönbrunn Palace", "relation": "拥有", "confidence": 0.8},
    ]},
    "f4a7e94ebd5b2d88": {"entities": [], "relations": []},
    "113f0d6214c6ef0a": {"entities": [
        {"name": "the Foundation", "type": "组织", "aliases": ["基金会"]},
    ], "relations": []},
    "18b799b934d04064": {"entities": [
        {"name": "North America", "type": "地点", "aliases": ["北美"]},
        {"name": "storm", "type": "现象", "aliases": ["人工风暴", "the storm"]},
    ], "relations": [
        {"src": "North America", "dst": "storm", "relation": "免受影响", "confidence": 0.8},
    ]},
    "7b0d805874f385f7": {"entities": [
        {"name": "Vienna", "type": "地点", "aliases": ["维也纳"]},
        {"name": "the Enlightenment", "type": "概念", "aliases": ["启蒙运动"]},
    ], "relations": []},
    "dce2ab5b76a5d8e8": {"entities": [
        {"name": "Hurtas", "type": "组织", "aliases": []},
    ], "relations": []},
    "0e669bab34d56724": {"entities": [], "relations": []},
    "9006f5f4c3eef34b": {"entities": [], "relations": []},
    "60133143327dc970": {"entities": [], "relations": []},
    "f0edb5d49139ecc0": {"entities": [
        {"name": "Project Assessment of Human Science and Technology", "type": "组织", "aliases": ["人类科技项目评估"]},
    ], "relations": []},
    "5b67138bde294630": {"entities": [
        {"name": "The Windy City", "type": "地点", "aliases": ["风城"]},
    ], "relations": []},
    "f49457fc6eb88dbb": {"entities": [], "relations": []},
    "bec383f66691e43d": {"entities": [
        {"name": "the Messiah", "type": "角色", "aliases": ["弥赛亚"]},
    ], "relations": []},
    "dc6ecb2dda50e34c": {"entities": [], "relations": []},
    "dc2932d4a64376ed": {"entities": [], "relations": []},
    "16e36bc0a7dd89e3": {"entities": [
        {"name": "Mr.Robot", "type": "角色", "aliases": ["机器人先生"]},
        {"name": "London", "type": "地点", "aliases": ["伦敦"]},
    ], "relations": [
        {"src": "Mr.Robot", "dst": "London", "relation": "活跃于", "confidence": 0.8},
    ]},
    "0f68bba7890dece6": {"entities": [
        {"name": "Rest In", "type": "地点", "aliases": ["安息旅馆"]},
        {"name": "Insomnia Nighty Hotel", "type": "地点", "aliases": ["失眠夜酒店"]},
    ], "relations": []},
    "8eb1310001e5d715": {"entities": [
        {"name": "Regulus", "type": "角色", "aliases": ["雷古勒斯"]},
    ], "relations": []},
    "3c6342dd4ffef6c1": {"entities": [
        {"name": "Miss Acie", "type": "角色", "aliases": ["Acie", "阿西小姐"]},
        {"name": "Father", "type": "角色", "aliases": ["父亲"]},
    ], "relations": [
        {"src": "Father", "dst": "Miss Acie", "relation": "遗留", "confidence": 0.85},
    ]},
    "ec0133ef6ed5cac1": {"entities": [
        {"name": "Rimmick Cup", "type": "物品", "aliases": ["里米克杯"]},
        {"name": "Ramirez", "type": "组织", "aliases": ["拉米雷斯"]},
    ], "relations": [
        {"src": "Ramirez", "dst": "Rimmick Cup", "relation": "保护", "confidence": 0.9},
    ]},
    "7b72fc931efe253b": {"entities": [
        {"name": "Rimmet Cup", "type": "物品", "aliases": ["里米特杯"]},
        {"name": "Mr.Iverson", "type": "角色", "aliases": ["艾弗森先生"]},
        {"name": "father", "type": "角色", "aliases": ["父亲"]},
    ], "relations": [
        {"src": "Mr.Iverson", "dst": "Rimmet Cup", "relation": "负责", "confidence": 0.75},
    ]},
    "a9ee2aa80a993c6e": {"entities": [
        {"name": "London", "type": "地点", "aliases": ["伦敦"]},
        {"name": "security robots", "type": "概念", "aliases": ["安保机器人", "Urban tin monsters"]},
    ], "relations": [
        {"src": "London", "dst": "security robots", "relation": "部署", "confidence": 0.85},
    ]},
    "324b124529a80133": {"entities": [
        {"name": "London", "type": "地点", "aliases": ["伦敦"]},
    ], "relations": []},
    "9ce7d17df70f9b08": {"entities": [
        {"name": "London", "type": "地点", "aliases": ["伦敦"]},
    ], "relations": []},
    "52345d6741de0f2d": {"entities": [], "relations": []},
    "038204011a58a4e6": {"entities": [
        {"name": "Miss Acie", "type": "角色", "aliases": ["Acie", "阿西小姐"]},
        {"name": "robots", "type": "概念", "aliases": ["安保机器人", "those robots"]},
    ], "relations": [
        {"src": "Miss Acie", "dst": "robots", "relation": "反对", "confidence": 0.8},
    ]},
    "efff3dc35a917dce": {"entities": [
        {"name": "apple", "type": "角色", "aliases": ["这个苹果", "the apple"]},
        {"name": "puppy", "type": "角色", "aliases": ["小狗", "the puppy"]},
        {"name": "security robots", "type": "概念", "aliases": ["安保机器人"]},
    ], "relations": [
        {"src": "apple", "dst": "puppy", "relation": "协助", "confidence": 0.8},
    ]},
    "e04225a1911b3570": {"entities": [
        {"name": "the London authorities", "type": "组织", "aliases": ["伦敦当局", "London authorities"]},
        {"name": "security robots", "type": "概念", "aliases": ["安保机器人"]},
        {"name": "London", "type": "地点", "aliases": ["伦敦"]},
    ], "relations": [
        {"src": "the London authorities", "dst": "security robots", "relation": "部署", "confidence": 0.85},
    ]},
    "b56f68f81221e9ad": {"entities": [
        {"name": "Ramirez", "type": "组织", "aliases": ["拉米雷斯"]},
        {"name": "Remit Cup", "type": "物品", "aliases": ["雷米特杯"]},
    ], "relations": [
        {"src": "Ramirez", "dst": "Remit Cup", "relation": "涉及", "confidence": 0.7},
    ]},
    "10d1f0323d5ef9b1": {"entities": [], "relations": []},
    "8cd3361387957b29": {"entities": [], "relations": []},
    "1ca1cdae2913c82d": {"entities": [], "relations": []},
    "b1951c11ab7441c5": {"entities": [
        {"name": "Nina", "type": "角色", "aliases": []},
    ], "relations": []},
    "bbfd5c68f3978fd0": {"entities": [
        {"name": "Mother Nature", "type": "概念", "aliases": ["自然之母"]},
        {"name": "father", "type": "角色", "aliases": ["父亲"]},
    ], "relations": []},
    "cf5758ec0a1f1be7": {"entities": [
        {"name": "Kaiserschmarrn", "type": "物品", "aliases": ["皇帝松饼"]},
        {"name": "Zeus", "type": "角色", "aliases": ["宙斯"]},
    ], "relations": []},
    "d924e070bc3b65a8": {"entities": [
        {"name": "Ceres", "type": "地点", "aliases": ["谷神星", "the Ceres"]},
        {"name": "Uranus", "type": "地点", "aliases": ["天王星", "the Uranus"]},
    ], "relations": []},
    "87c8f93721b525c1": {"entities": [
        {"name": "the Sultan's palace", "type": "地点", "aliases": ["苏丹宫殿"]},
    ], "relations": []},
    "d2004df746f19d76": {"entities": [], "relations": []},
    "cf4a1d0a0d4be0c1": {"entities": [
        {"name": "xenopilot", "type": "角色", "aliases": ["异星飞行员"]},
        {"name": "serpent eating its own tail", "type": "概念", "aliases": ["衔尾蛇", "ouroboros"]},
    ], "relations": []},
    "a4d06a7bf13e3939": {"entities": [
        {"name": "Betty", "type": "角色", "aliases": ["贝蒂"]},
        {"name": "Hamptons Villa", "type": "地点", "aliases": ["汉普顿别墅", "a Hamptons Villa"]},
    ], "relations": []},
    "314f57877e7c9bcf": {"entities": [
        {"name": "London", "type": "地点", "aliases": ["伦敦"]},
    ], "relations": []},
    "ddc8e7fbd7b54d7a": {"entities": [
        {"name": "concentration potion", "type": "物品", "aliases": ["浓缩药剂"]},
        {"name": "type 2 PMMA safety boxes", "type": "物品", "aliases": ["PMMA安全箱"]},
    ], "relations": []},
    "954fa14dd00259e2": {"entities": [], "relations": []},
    "4d69c8c237750cfe": {"entities": [], "relations": []},
    "0e3869f6d740a20f": {"entities": [
        {"name": "Shangrei", "type": "地点", "aliases": ["香格里"]},
    ], "relations": []},
    "3d5e99a49e8671e5": {"entities": [], "relations": []},
    "9d8a9e1c7a188996": {"entities": [
        {"name": "the gods of Shoti", "type": "角色", "aliases": ["肖提神"]},
    ], "relations": []},
    "3b10731fea1e1fbc": {"entities": [
        {"name": "Lushus", "type": "角色", "aliases": ["路舒斯"]},
        {"name": "the Jitsi", "type": "地点", "aliases": ["吉茨"]},
    ], "relations": [
        {"src": "the Jitsi", "dst": "Lushus", "relation": "栖息", "confidence": 0.8},
    ]},
    "3739af19bf4f57dd": {"entities": [
        {"name": "The New Young Mountain", "type": "地点", "aliases": ["新青年山"]},
        {"name": "half-divine beasts", "type": "角色", "aliases": ["半神兽", "halfdivinebeasts"]},
    ], "relations": [
        {"src": "The New Young Mountain", "dst": "half-divine beasts", "relation": "庇护", "confidence": 0.85},
    ]},
    "2470d4266836a30a": {"entities": [], "relations": []},
    "1c4f086b22ce2b3d": {"entities": [
        {"name": "Ball pens", "type": "角色", "aliases": ["圆珠笔"]},
    ], "relations": []},
    "e8f8c77fef72aae9": {"entities": [
        {"name": "Bohemia", "type": "地点", "aliases": ["波西米亚"]},
        {"name": "the Antarctic Sea", "type": "地点", "aliases": ["南极海"]},
    ], "relations": []},
    "fceb9e3255432508": {"entities": [
        {"name": "Talefield", "type": "角色", "aliases": []},
    ], "relations": []},
    "97e58c7cc8c39d54": {"entities": [
        {"name": "Golden Age", "type": "概念", "aliases": ["黄金时代"]},
    ], "relations": []},
    "7f7849c351cfaa19": {"entities": [], "relations": []},
    "8ccf422f117aada3": {"entities": [
        {"name": "Ms.Wensong", "type": "角色", "aliases": ["文松女士", "Wensong"]},
        {"name": "ley lines", "type": "概念", "aliases": ["地脉"]},
    ], "relations": [
        {"src": "Ms.Wensong", "dst": "ley lines", "relation": "研究", "confidence": 0.85},
    ]},
    "e0f957ff9d2bd8d7": {"entities": [
        {"name": "Ryashki", "type": "地点", "aliases": ["里亚什基"]},
        {"name": "ley lines", "type": "概念", "aliases": ["地脉"]},
    ], "relations": [
        {"src": "Ryashki", "dst": "ley lines", "relation": "接受", "confidence": 0.8},
    ]},
    "1b8c125e3c272ddf": {"entities": [
        {"name": "Rajaski", "type": "地点", "aliases": ["拉亚斯基"]},
    ], "relations": []},
    "cac23b5b25871207": {"entities": [
        {"name": "Whiskers", "type": "角色", "aliases": ["胡须"]},
    ], "relations": []},
    "f411dec4311017f0": {"entities": [
        {"name": "self-purification system", "type": "概念", "aliases": ["自净系统"]},
    ], "relations": []},
    "a5ccb81c2259b794": {"entities": [
        {"name": "friendship cheese", "type": "物品", "aliases": ["友谊奶酪"]},
    ], "relations": []},
    "70e83ea764e653f5": {"entities": [], "relations": []},
    "4ead90ffa0bdabaa": {"entities": [
        {"name": "Miss Virgin", "type": "角色", "aliases": ["处女小姐"]},
    ], "relations": []},
    "70e374beac4fb5e5": {"entities": [
        {"name": "Apollo", "type": "角色", "aliases": ["阿波罗"]},
    ], "relations": []},
    "b8901facceff6903": {"entities": [], "relations": []},
    "16f36997526892f5": {"entities": [
        {"name": "1920s", "type": "时间", "aliases": ["二十世纪二十年代", "the 1920s"]},
    ], "relations": []},
    "a655475e2378934c": {"entities": [
        {"name": "Neolithic era", "type": "时间", "aliases": ["新石器时代", "the Neolithic era"]},
    ], "relations": []},
    "287433e071891ca4": {"entities": [
        {"name": "Arcanum", "type": "概念", "aliases": ["秘术"]},
    ], "relations": []},
    "4bfafe87c8afb2a1": {"entities": [], "relations": []},
    "534cfc653d814f7b": {"entities": [], "relations": []},
    "4df9eb468f5f0473": {"entities": [
        {"name": "Hollywood", "type": "地点", "aliases": ["好莱坞"]},
        {"name": "Sergeant Howard Eden", "type": "角色", "aliases": ["霍华德·伊登", "Howard Eden"]},
    ], "relations": []},
    "d4ae31c3fe18b332": {"entities": [], "relations": []},
    "0343fd56a636462b": {"entities": [
        {"name": "Texas", "type": "地点", "aliases": ["得克萨斯"]},
    ], "relations": []},
    "6f13c1d3519d2fdd": {"entities": [], "relations": []},
    "932644c1c95dcce3": {"entities": [
        {"name": "Captain", "type": "角色", "aliases": ["船长"]},
    ], "relations": []},
    "9bbfe73b8bc3e8d4": {"entities": [], "relations": []},
    "9e00b29cc55f0983": {"entities": [
        {"name": "room 210", "type": "地点", "aliases": ["210号房"]},
    ], "relations": []},
    "59be1c54299217be": {"entities": [
        {"name": "room 218", "type": "地点", "aliases": ["218号房"]},
        {"name": "Texas", "type": "地点", "aliases": ["得克萨斯"]},
    ], "relations": []},
    "24d814af7958841f": {"entities": [
        {"name": "Ms.Furtin", "type": "角色", "aliases": ["弗廷女士", "Furtin"]},
    ], "relations": []},
    "7c55794998b8818b": {"entities": [], "relations": []},
    "07d67ffde2acb395": {"entities": [
        {"name": "griffology", "type": "概念", "aliases": ["狮鹫学"]},
    ], "relations": []},
    "d89c497a67972086": {"entities": [], "relations": []},
    "f3ef3150dd98ec25": {"entities": [
        {"name": "devil", "type": "角色", "aliases": ["恶魔", "a devil"]},
    ], "relations": []},
    "7ff329b253aa5613": {"entities": [
        {"name": "S-1", "type": "事件", "aliases": ["the S-1"]},
    ], "relations": []},
}


def _norm(s: str) -> str:
    return (s or "").strip().lower().replace(" ", "").replace("\n", "").replace("\r", "")


def _load_pro() -> dict:
    text = PRO.read_text(encoding="utf-8")
    out = {}
    for blk in text.split("\n\n"):
        lines = [l for l in blk.split("\n") if l.strip() != ""]
        if not lines:
            continue
        h = lines[0].strip()
        body = " ".join(l.strip() for l in lines[1:])
        out[h] = body
    return out


def validate() -> int:
    bad = 0
    for h, d in RESULTS.items():
        pool = set()
        for e in d.get("entities") or []:
            pool.add(e.get("name") or "")
            pool |= set(e.get("aliases") or [])
        for r in d.get("relations") or []:
            if r.get("src") not in pool or r.get("dst") not in pool:
                print(f"[dangling] {h} {r.get('src')} -> {r.get('dst')}")
                bad += 1
    return bad


def landing(proc: dict) -> int:
    bad = 0
    for h, d in RESULTS.items():
        ntext = _norm(proc.get(h, ""))
        if not ntext:
            print(f"[landing-missing] {h}")
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
    proc = _load_pro()
    v = validate()
    m = landing(proc)
    total_e = sum(len(d.get("entities") or []) for d in RESULTS.values())
    total_r = sum(len(d.get("relations") or []) for d in RESULTS.values())
    empties = [h for h, d in RESULTS.items() if not (d.get("entities") or d.get("relations"))]
    print(f"[validate] 块 {len(RESULTS)}，悬空 {v}，未落地 {m}")
    print(f"[stats] 实体 {total_e}，关系 {total_r}")
    print(f"[empty] 判无内容块 {len(empties)}")
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
    print(f"[apply-missing-p42] 写入 {len(RESULTS)} 条")
    return 0


if __name__ == "__main__":
    sys.exit(main())
