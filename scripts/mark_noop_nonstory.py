# -*- coding: utf-8 -*-
"""把「非剧情块」标记为确认 NOOP。

语料里混入了大量**游戏战斗数值页**（生命/攻击/暴击率/技能倍率表）和
**UI 模板页**（点击查看详情 / 目标GOAL / 奖励REWARD）。这些不是剧情文本，
本地 7B 会从里面硬抽出「生命」「攻击」之类的伪实体，或干脆抽不出内容。

对补抽而言它们应当按「确实无可抽」处理：写入空抽取结果并登记到
`noop_confirmed.json`，这样审计的 `empty` 指标才有意义（empty 应只反映
「剧情块没抽出来」，而不是「本来就没剧情」）。

用法（项目根目录）：
  python scripts/mark_noop_nonstory.py            # 预演
  python scripts/mark_noop_nonstory.py --apply    # 写盘
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "knowledge" / "plot_cache" / "wu_ming_zhe"
CORPUS = ROOT / "data" / "knowledge" / "plot_corpus_wu_ming_zhe.json"
NOOP = ROOT / "data" / "knowledge" / "_audit" / "noop_confirmed.json"


def is_battle(text: str) -> bool:
    """战斗数值页：生命/攻击/暴击率/防御 等属性表 + 技能倍率。"""
    return (
        ("生命：" in text or "生命:" in text)
        and "攻击" in text
        and ("暴击" in text or "现实防御" in text)
    )


def is_ui(text: str) -> bool:
    """UI 模板页：大量重复的界面固定文案，几乎无剧情信息。"""
    return len(
        re.findall(r"(点击查看详情|目标GOAL|奖励REWARD|敌方ENEMY|装配|塑造)", text)
    ) >= 3


# ── 非剧情内容块：题记 / 诗引 / 纯标题卡 / 极短收束句 ──────────────────────
# 背景（2026-09-20 compendium 正典入库后复核）：补齐 5 226 块抽取后，验收 R10 仍有
# 差集 6 块。逐块人工复核确认它们**抽取为空且确实无剧情实体可抽**——不是「漏抽」，
# 而是题记/诗引/标题卡这类非剧情内容。审计的 empty 指标只应反映「剧情块没抽出来」，
# 故按本文件的既定语义登记为 NOOP。复核明细见 docs/compendium正典入库报告.md。
EPIGRAPH_REVIEWED = {
    "41a87d00beb17c2d": "洞穴的囚徒·题记（「三种人/奥林匹克」引文，非本作事件）",
    "a4cbbd7c68cf9530": "在我们的时代里·里尔克诗引（德语原文＋中译）",
    "56d926db186c20d0": "第一千夜·收束句（「祝愿…都如此夜一般」）",
    "6001106d4f92dd64": "重返人间·纯标题卡（【标题卡】THE END）",
    "70ab73dac0ff7ebc": "黄金与悲喜剧·广告台词（无剧情实体）",
    "bed30cc4d626ae22": "小春雀儿·收束句＋标题卡（复抽仅得「小狗/蝴蝶」通用名词）",
}


def is_card_only(text: str) -> bool:
    """整块只有标题卡（如「【标题卡】THE END」）。"""
    body = re.sub(r"【[^】]{0,24}】", "", text or "")
    return bool(re.search(r"【[^】]{0,24}】", text or "")) and not body.strip(" \t\r\n。，、—…")


def is_tiny(text: str) -> bool:
    """极短块（去空白后 < 50 字）：收束句/单句广告之类，无实体可抽。"""
    return len(re.sub(r"\s+", "", text or "")) < 50


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    chunks = corpus["chunks"] if isinstance(corpus, dict) else corpus

    noop = set(json.loads(NOOP.read_text(encoding="utf-8"))) if NOOP.exists() else set()
    n_battle = n_ui = n_epi = n_card = n_tiny = 0
    by_hash = {c["hash"]: c for c in chunks}

    def _write_empty(h: str) -> None:
        if args.apply:
            (CACHE / f"{h}.json").write_text(
                json.dumps({"entities": [], "relations": []}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

    for c in chunks:
        h = c["hash"]
        text = c.get("text", "") or ""
        kind = "battle" if is_battle(text) else ("ui" if is_ui(text) else "")
        if not kind:
            continue
        p = CACHE / f"{h}.json"
        if p.exists() and (json.loads(p.read_text(encoding="utf-8")).get("entities") or []):
            continue  # 已有实质抽取结果，不动
        if kind == "battle":
            n_battle += 1
        else:
            n_ui += 1
        noop.add(h)
        _write_empty(h)

    # ② 逐块复核过的非剧情块（题记/诗引/纯标题卡/极短收束句）
    for h in EPIGRAPH_REVIEWED:
        if h not in by_hash:
            continue
        p = CACHE / f"{h}.json"
        if p.exists() and (json.loads(p.read_text(encoding="utf-8")).get("entities") or []):
            continue
        noop.add(h)
        n_epi += 1
        _write_empty(h)

    # ③ 纯标题卡 / 极短块：仅在**抽取为空**时登记（防误伤有内容的短块）
    for c in chunks:
        h = c["hash"]
        text = c.get("text", "") or ""
        if h in noop:
            continue
        p = CACHE / f"{h}.json"
        if not p.exists():
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except ValueError:
            continue
        if data.get("entities") or data.get("relations"):
            continue  # 有实质抽取，不是空块
        if is_card_only(text):
            noop.add(h)
            n_card += 1
        elif is_tiny(text):
            noop.add(h)
            n_tiny += 1

    print(
        f"[noop-nonstory] {'已写盘' if args.apply else '预演'}："
        f"战斗数值页 {n_battle}｜UI 页 {n_ui}｜复核非剧情 {n_epi}｜"
        f"纯标题卡 {n_card}｜极短块 {n_tiny}｜NOOP 合计 {len(noop)}"
    )
    if args.apply:
        NOOP.write_text(
            json.dumps(sorted(noop), ensure_ascii=False, indent=1), encoding="utf-8"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
