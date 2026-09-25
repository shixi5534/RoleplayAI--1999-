# -*- coding: utf-8 -*-
"""无缓存/空块补抽 · 第 3 批（9 块，按信息量降序的高价值剧情块）。

同批 35ee79e160d7e1bb（v3.4）是论坛灌水页（贴主/IP/“此回复已被管理员删除”），
虽然词频高但无剧情信息，单独登记为 NOOP，不在这里抽。

用法：python scripts/apply_missing_p3.py --apply
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "knowledge" / "plot_cache" / "wu_ming_zhe"
NOOP_FILE = ROOT / "data" / "knowledge" / "_audit" / "noop_confirmed.json"

# 论坛灌水页：只有贴主/IP/回复，无剧情实体
NOOP_ADD = ["35ee79e160d7e1bb"]

RESULTS: dict[str, dict] = {
    # v2.2 巴西支部哗变、总部通告、邓肯与洛佩拉的旧物
    "bc652c1cd2374881": {
        "entities": [
            {"name": "邓肯先生", "type": "角色", "aliases": ["邓肯"]},
            {"name": "洛佩拉", "type": "角色", "aliases": []},
            {"name": "长管左轮枪", "type": "物品", "aliases": ["一对长管左轮枪"]},
            {"name": "巴西支部", "type": "组织", "aliases": ["巴西当地"]},
            {"name": "总部", "type": "组织", "aliases": []},
            {"name": "1961年", "type": "时间", "aliases": []},
            {"name": "刚果维和行动", "type": "事件", "aliases": []},
            {"name": "哗变", "type": "事件", "aliases": ["叛变"]},
            # 正文只有「以重塑**秩序**为你的终身事业」，并未出现「重塑之手」组织名，
            # 不能靠背景知识外推，故不建该组织实体与关系。
            {"name": "秩序", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "巴西支部", "dst": "哗变", "relation": "发生", "confidence": 0.9},
            {"src": "总部", "dst": "巴西支部", "relation": "审查", "confidence": 0.85},
            {"src": "洛佩拉", "dst": "长管左轮枪", "relation": "使用", "confidence": 0.8},
            {"src": "邓肯先生", "dst": "刚果维和行动", "relation": "参加", "confidence": 0.7},
        ],
    },
    # v2.8 对话：指挥官与牺牲、忠诚
    "c73a4610c81d30f7": {
        "entities": [
            {"name": "指挥官", "type": "角色", "aliases": ["多愁善感的指挥官"]},
            {"name": "老兵", "type": "角色", "aliases": []},
            {"name": "信念", "type": "概念", "aliases": ["忠于信念"]},
            {"name": "盲信者", "type": "角色", "aliases": ["割掉舌头的盲信者"]},
        ],
        "relations": [
            {"src": "指挥官", "dst": "老兵", "relation": "统率", "confidence": 0.75},
            {"src": "盲信者", "dst": "信念", "relation": "追随", "confidence": 0.7},
        ],
    },
    # 人工梦游使用规范 / 调查员考核
    "4be51f48ef572431": {
        "entities": [
            {"name": "人工梦游", "type": "概念", "aliases": ["人工梦游使用规范"]},
            {"name": "调查员", "type": "角色", "aliases": []},
            {"name": "神秘学家", "type": "角色", "aliases": []},
            {"name": "考核梦境", "type": "概念", "aliases": ["梦境"]},
            {"name": "咒语", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "调查员", "dst": "考核梦境", "relation": "参加", "confidence": 0.85},
            {"src": "调查员", "dst": "咒语", "relation": "运用", "confidence": 0.75},
            {"src": "人工梦游", "dst": "考核梦境", "relation": "生成", "confidence": 0.8},
        ],
    },
    # v2.8 苏菲亚与十四行诗的争论、大洪水
    "e164508361d835bb": {
        "entities": [
            {"name": "苏菲亚", "type": "角色", "aliases": ["苏菲亚小姐"]},
            {"name": "十四行诗", "type": "角色", "aliases": []},
            {"name": "重塑之手", "type": "组织", "aliases": []},
            {"name": "大洪水", "type": "事件", "aliases": []},
            {"name": "鱼的时代", "type": "概念", "aliases": []},
            {"name": "大雨", "type": "事件", "aliases": ["永不间断的大雨"]},
        ],
        "relations": [
            {"src": "十四行诗", "dst": "重塑之手", "relation": "指责", "confidence": 0.9},
            {"src": "大雨", "dst": "大洪水", "relation": "导致", "confidence": 0.8},
            {"src": "苏菲亚", "dst": "十四行诗", "relation": "质问", "confidence": 0.8},
        ],
    },
    # 来亚什基生产工厂：克努特取零件
    "6a525cc433a62856": {
        "entities": [
            {"name": "克努特", "type": "角色", "aliases": ["克努特同志"]},
            {"name": "埃琳娜", "type": "角色", "aliases": []},
            {"name": "阿德里安", "type": "角色", "aliases": []},
            {"name": "阿图尔", "type": "角色", "aliases": []},
            {"name": "矿场", "type": "地点", "aliases": ["矿上"]},
            {"name": "零件", "type": "物品", "aliases": []},
            {"name": "旧工具", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "埃琳娜", "dst": "零件", "relation": "制作", "confidence": 0.9},
            {"src": "克努特", "dst": "零件", "relation": "搬运", "confidence": 0.9},
            {"src": "阿德里安", "dst": "旧工具", "relation": "保养", "confidence": 0.85},
            {"src": "矿场", "dst": "零件", "relation": "需要", "confidence": 0.8},
        ],
    },
    # 蜗牛与痕迹：罐头房子里的研究者
    "51f85a24aba56117": {
        "entities": [
            {"name": "蜗牛", "type": "物品", "aliases": ["缓慢爬行的蜗牛"]},
            {"name": "研究者", "type": "角色", "aliases": ["研究者们"]},
            {"name": "罐头房子", "type": "地点", "aliases": []},
            {"name": "第一滴雨", "type": "事件", "aliases": []},
        ],
        "relations": [
            {"src": "研究者", "dst": "罐头房子", "relation": "工作于", "confidence": 0.85},
        ],
    },
    # v2.8 电台残讯：刻雷乌斯、地母
    "d89d7716eeb86bdf": {
        "entities": [
            {"name": "电台", "type": "物品", "aliases": ["无线电台"]},
            {"name": "刻雷乌斯", "type": "角色", "aliases": []},
            {"name": "地母", "type": "概念", "aliases": []},
            {"name": "冰尸", "type": "物品", "aliases": ["一具冰尸"]},
        ],
        "relations": [
            {"src": "电台", "dst": "地母", "relation": "呼叫", "confidence": 0.7},
        ],
    },
    # v3.0 基金会鸽派/鹰派、芝诺叛逃、刻雷乌斯应急预案
    "ab052d626e488cfd": {
        "entities": [
            {"name": "圣洛夫基金会", "type": "组织", "aliases": ["基金会"]},
            {"name": "芝诺", "type": "组织", "aliases": ["芝诺军备学院"]},
            {"name": "鸽派", "type": "组织", "aliases": ["所谓“鸽派”"]},
            {"name": "鹰派", "type": "组织", "aliases": []},
            {"name": "刻雷乌斯", "type": "角色", "aliases": []},
            {"name": "暴雨", "type": "事件", "aliases": ["这场“暴雨”"]},
            {"name": "重塑之手", "type": "组织", "aliases": []},
            {"name": "神秘学家", "type": "角色", "aliases": []},
            {"name": "应急预案", "type": "概念", "aliases": []},
            {"name": "和平与秩序", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "芝诺", "dst": "圣洛夫基金会", "relation": "叛逃", "confidence": 0.9},
            {"src": "刻雷乌斯", "dst": "应急预案", "relation": "提出", "confidence": 0.9},
            {"src": "圣洛夫基金会", "dst": "神秘学家", "relation": "斡旋", "confidence": 0.85},
            {"src": "鹰派", "dst": "圣洛夫基金会", "relation": "形成于", "confidence": 0.8},
            {"src": "鸽派", "dst": "和平与秩序", "relation": "主张", "confidence": 0.8},
        ],
    },
    # v2.7 康斯坦丁的问候：北方哨歌、库珀花环、指针、兔毛手袋
    "8c119864829f8415": {
        "entities": [
            {"name": "康斯坦丁", "type": "角色", "aliases": ["康斯坦丁女士"]},
            {"name": "北方哨歌", "type": "角色", "aliases": ["北方哨歌女士"]},
            {"name": "库珀花环", "type": "角色", "aliases": ["库珀花环小姐"]},
            {"name": "指针", "type": "角色", "aliases": ["指针女士"]},
            {"name": "兔毛手袋", "type": "角色", "aliases": ["兔毛手袋研究员"]},
            {"name": "理线学", "type": "概念", "aliases": []},
            {"name": "拉普拉斯科算中心", "type": "组织", "aliases": ["拉普拉斯"]},
            {"name": "传送软盘", "type": "物品", "aliases": []},
            {"name": "航天实验", "type": "事件", "aliases": []},
        ],
        "relations": [
            {"src": "康斯坦丁", "dst": "北方哨歌", "relation": "问候", "confidence": 0.9},
            {"src": "康斯坦丁", "dst": "库珀花环", "relation": "问候", "confidence": 0.9},
            {"src": "库珀花环", "dst": "拉普拉斯科算中心", "relation": "就职", "confidence": 0.8},
            {"src": "理线学", "dst": "航天实验", "relation": "应用于", "confidence": 0.85},
            {"src": "指针", "dst": "传送软盘", "relation": "发明", "confidence": 0.85},
            {"src": "兔毛手袋", "dst": "理线学", "relation": "研究", "confidence": 0.7},
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
    for h in NOOP_ADD:
        (CACHE / f"{h}.json").write_text(
            json.dumps({"entities": [], "relations": []}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        noop = set(json.loads(NOOP_FILE.read_text(encoding="utf-8")))
        noop.add(h)
        NOOP_FILE.write_text(
            json.dumps(sorted(noop), ensure_ascii=False, indent=1), encoding="utf-8"
        )
    print(f"[apply-missing-p3] 写入 {len(RESULTS)} 条，NOOP +{len(NOOP_ADD)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
