# -*- coding: utf-8 -*-
"""从灰机离线资源提取「中英对照词典」（别名桥的数据底座）。

数据来源（全部离线，不联网）：
  1. ``data/lore/wu_ming_zhe/huiji_canon.json``   —— 已结构化的 926 条中英对照
  2. ``data/lore/_huiji_cache/*.json`` 的 parse 页 —— 页面正文（HTML text / wikitext）

提取规则（只收高可信模式，不做模糊猜测）：
  R1 ``{{DisplayTitle|English}}``                    页面中文标题 ↔ 英文标题（最强）
  R2 ``'''中文{{cb|English}}'''`` / ``{{cb|English}}`` 正文内嵌中英并列
  R3 parse.displaytitle 里的 ``中文 <small>English</small>``
  R4 纯文本里的 ``中文 English`` 紧邻并列（敌人/地点名，需通过形态过滤）
  R5 canon 的 terms.displaytitle（"暴雨 The Storm"）

产出：``data/lore/wu_ming_zhe/huiji_lexicon.json``
  {"meta": {...}, "zh2en": {...}, "en2zh": {...}, "sources": {...}}
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANON = ROOT / "data" / "lore" / "wu_ming_zhe" / "huiji_canon.json"
CACHE = ROOT / "data" / "lore" / "_huiji_cache"
OUT = ROOT / "data" / "lore" / "wu_ming_zhe" / "huiji_lexicon.json"

CJK = re.compile(r"[\u4e00-\u9fff]")
# 中文名：2~20 个汉字，可含 · 间隔号与 - 连字符
RE_ZH = r"[\u4e00-\u9fff][\u4e00-\u9fff·\-]{1,19}"
# 英文名：首字母大写起，允许空格、点、撇号、连字符、&
RE_EN = r"[A-Z][A-Za-z0-9'’\-\.]*(?:\s+(?:of|the|and|in|at|de|la|le|von|van)?\s*[A-Z][A-Za-z0-9'’\-\.]*){0,6}"
# 停用词：这些"英文"不是专名
EN_STOP = {
    "the", "a", "an", "and", "or", "of", "in", "on", "at", "to", "for", "with",
    "level", "goal", "reward", "enemy", "battle", "information", "id", "hp", "atk",
    "out", "use", "all", "no", "ltd", "co", "inc", "vs", "new", "old", "top",
    "no.", "sd", "bgm", "cv", "sp", "lv", "exp", "buff", "debuff", "stage",
    "round", "turn", "damage", "skill", "target", "cost", "type", "name", "ip",
    "hp", "mp", "def", "res", "crit", "max", "min", "s", "a", "b", "c", "d",
}
# 形态过滤：英文串不能全是常见词
CJK_STOP_ZH = {"等级", "回合", "上限", "战斗", "消耗", "人数", "目标", "奖励", "敌方",
               "基本信息", "目录", "活动", "内容", "详情", "参与", "条件", "附加条件",
               "试用角色", "环境", "我方", "关卡", "名称", "推荐", "信息", "资源",
               "阵容", "提示", "说明", "备注", "简介", "数据", "效果", "技能", "状态"}


def add(zh2en: dict, en2zh: dict, srcs: dict, zh: str, en: str, rule: str) -> bool:
    zh = (zh or "").strip().strip("：:·-— ")
    en = (en or "").strip().strip("：:.,;·-— ")
    if not zh or not en:
        return False
    if not CJK.search(zh) or not re.match(r"^[A-Za-z]", en):
        return False
    if len(zh) < 2 or len(zh) > 20 or len(en) < 2 or len(en) > 60:
        return False
    if zh in CJK_STOP_ZH:
        return False
    words = [w.lower() for w in re.split(r"\s+", en)]
    if all(w in EN_STOP for w in words):
        return False
    if len(words) == 1 and words[0] in EN_STOP:
        return False
    # 纯 ASCII 的"英文"必须至少有一个词首字母大写（专名特征）
    if not re.match(r"^[A-Z]", en):
        return False
    zh2en.setdefault(zh, [])
    if en not in zh2en[zh]:
        zh2en[zh].append(en)
    en2zh.setdefault(en, [])
    if zh not in en2zh[en]:
        en2zh[en].append(zh)
    # 记录该配对的来源规则（可多条），供下游分级
    srcs.setdefault(f"{zh}\u0000{en}", [])
    if rule not in srcs[f"{zh}\u0000{en}"]:
        srcs[f"{zh}\u0000{en}"].append(rule)
    return True


def main() -> int:
    canon = json.loads(CANON.read_text(encoding="utf-8"))
    zh2en: dict[str, list[str]] = {}
    en2zh: dict[str, list[str]] = {}
    srcs: dict[str, list[str]] = {}
    cnt: Counter[str] = Counter()

    # ---- R5 / canon 结构表 ----
    for arr, rule in (("characters", "canon.character"), ("npcs", "canon.npc"),
                      ("chapters", "canon.chapter"), ("name_table", "canon.name_table")):
        for rec in canon.get(arr) or []:
            zh = str(rec.get("zh") or "")
            en = str(rec.get("en") or "")
            if add(zh2en, en2zh, srcs, zh, en, rule):
                cnt[rule] += 1
            # NPC 并列写法「甲、乙、丙」拆开
            for part in re.split(r"[、,，/]", zh):
                part = part.strip()
                if part and part != zh and add(zh2en, en2zh, srcs, part, en, rule + ".split"):
                    cnt[rule + ".split"] += 1
    for zh, v in (canon.get("terms") or {}).items():
        dt = str(v.get("displaytitle") or "")
        m = re.match(rf"^\s*({RE_ZH})\s+(.+?)\s*$", dt)
        if m and add(zh2en, en2zh, srcs, m.group(1), m.group(2), "canon.term"):
            cnt["canon.term"] += 1

    # ---- 缓存页 ----
    parsed = []
    if CACHE.is_dir():
        for f in sorted(CACHE.glob("*.json")):
            try:
                d = json.loads(f.read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001
                continue
            if isinstance(d, dict) and isinstance(d.get("parse"), dict):
                parsed.append(d["parse"])

    for pr in parsed:
        title = str(pr.get("title") or "")
        title_zh = title.split("/")[-1].strip()

        # R1 DisplayTitle（wikitext）
        wt = pr.get("wikitext") or ""
        if wt:
            for m in re.finditer(r"\{\{\s*DisplayTitle\s*\|\s*([^}|]+?)\s*\}\}", wt, re.I):
                if add(zh2en, en2zh, srcs, title_zh, m.group(1), "wiki.DisplayTitle"):
                    cnt["wiki.DisplayTitle"] += 1
            # R2 内嵌并列：'''中文{{cb|English}}'''
            for m in re.finditer(rf"({RE_ZH})\s*\{{\{{\s*(?:cb|color|ruby)\s*\|\s*([^}}|]+?)\s*\}}\}}", wt):
                if add(zh2en, en2zh, srcs, m.group(1), m.group(2), "wiki.cb"):
                    cnt["wiki.cb"] += 1

        # R3 displaytitle 里的 <small>English</small>
        dt = str(pr.get("displaytitle") or "")
        if dt:
            m = re.search(rf"({RE_ZH})\s*<small>.*?>([^<]+)</span></small>", dt, re.S)
            if m:
                if add(zh2en, en2zh, srcs, m.group(1), m.group(2), "wiki.displaytitle_small"):
                    cnt["wiki.displaytitle_small"] += 1

        # R4 纯文本并列（敌人名 / 地名）
        html = pr.get("text")
        if isinstance(html, str) and html:
            plain = re.sub(r"<[^>]+>", " ", html)
            plain = plain.replace("&nbsp;", " ").replace("&#160;", " ")
            plain = re.sub(r"\s+", " ", plain)
            for m in re.finditer(rf"({RE_ZH})\s+({RE_EN})", plain):
                if add(zh2en, en2zh, srcs, m.group(1), m.group(2), "wiki.plain"):
                    cnt["wiki.plain"] += 1

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "meta": {
            "source": "灰机 wiki《重返未来：1999》中文维基（离线缓存 + 结构化 canon）",
            "canon_file": str(CANON.relative_to(ROOT)),
            "cache_dir": str(CACHE.relative_to(ROOT)),
            "parsed_pages": len(parsed),
            "zh_entries": len(zh2en),
            "en_entries": len(en2zh),
            "by_rule": dict(cnt),
        },
        "zh2en": zh2en, "en2zh": en2zh, "rules": srcs,
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"[lexicon] 解析页 {len(parsed)} ｜ 中文条目 {len(zh2en)} ｜ 英文条目 {len(en2zh)}")
    print(f"[lexicon] 提取规则命中 {dict(cnt)}")
    print(f"[lexicon] → {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
