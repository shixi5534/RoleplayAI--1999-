# -*- coding: utf-8 -*-
"""按灰机 wiki 权威设定修正剧情图谱抽取缺陷。

事实基准（2026-09-08 抓取，https://res1999.huijiwiki.com/wiki/）：
- 无名者 = Ms. Stranger = 淑女格蕾丝（Ms. Grace），2.0 登场、3.7 加入征集，
  司辰小队成员，原展出于冰岛 → 转至圣洛夫基金会 → 曾短暂展出于重塑之手。
  ⇒ 与「露西 Lucy」（拉普拉斯科算中心负责人）是**两个不同角色**。
- 伊戈尔：原属芝诺 → 「忧郁的热带」叛变加入重塑之手 → 「远征记」脱离重塑之手。
- 重塑之手领袖为阿尔卡纳。

修正内容（全部改抽取缓存，改完重建图谱）：
1. 删与灰机冲突的关系：
   - `Miss Stranger —持有→ Foundation`：原文是 "I'm not in a position to speak
     **on behalf of** the Foundation, Miss Stranger"（我不能代表基金会发言），
     被误抽成「持有」，方向+谓语双错。
   - `Igor —是→ my father / my parents`：原文 "I didn't want anyone to
     **take my father's place**"（我不想任何人取代我父亲的位置），语义被**反转**。
   - `Arcana —不是→ Verta`：否定关系无信息量，且 Verta 是 Vertin 的 ASR 误读。
2. 删污染别名（本地 7B 抽取产物，人工别名表是干净的）：
   - 乱码：`斯特्र昂德`（天城文）
   - 角色混淆：`Lucy (Miss Stranger)`（把无名者错指为露西）
   - 提示词模板泄漏：`伊万 (Madam Lucy的曾用名/代称/昵称)`
   - 中文整句：如「阿尔卡纳第一次见到维尔廷时说…这句」
   - 英文代词短语：my father / my parents / their letters（连带删实体与关系）

用法（项目根目录）：
  .venv/Scripts/python.exe -X utf8 scripts/fix_huiji_conflicts.py --apply
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "knowledge" / "plot_cache" / "wu_ming_zhe"

CN = re.compile(r"[一-鿿]")
SENT_HINT = re.compile(r"(说|的|了|这句|当时|曾|因为|所以|就是|时候|喜欢)")
PRON_PHRASE = re.compile(r"^(my|his|her|their|its|your)\s+[a-z][a-z ]*$", re.I)
CN_PRON_PHRASE = re.compile(r"^(我们|他们|她们|他|她|它|你|我|大家|某人|咱们)(的)?[一-鿿]{1,6}$")
TEMPLATE_LEAK = re.compile(r"曾用名|代称|昵称")

# 中文译名缺英文表层形式 → 补别名，使其可在正文落地
ADD_ALIAS: dict[str, list[tuple[str, str]]] = {
    # 原文：residual energy at **its eye**, the point identified by Admiral Igor
    "60f70945e7278eee": [("风暴眼", "its eye")],
}

# 与灰机冲突、必须删除的关系（hash -> [(src, relation, dst), ...]）
DROP_RELATIONS: dict[str, list[tuple[str, str, str]]] = {
    "fdab0f84630e55f8": [("Miss Stranger", "持有", "Foundation")],
    "d8bfa3f3e78c661f": [("Igor", "是", "my father"), ("Igor", "是", "my parents")],
    "e72ea83a9fca6598": [("Arcana", "不是", "Verta")],
}

# 谓语/方向改写（hash, (src, rel, dst) -> (new_src, new_rel, new_dst)）：
# 1) 原文 "Here we **serve** Arcana"（重塑之手效忠阿尔卡纳）+ 灰机「领袖阿尔卡纳」
#    → 谓语「持有」改为「效忠」（组织→领袖，方向不变）。
# 2) 原文「无名者是因为**基金会**需要他成为间谍才**被施加了剥离记忆的神秘术**」——
#    施加者是基金会、承受者是无名者，原抽取把终点写成了「基金会」，方向/终点双错；
#    且这恰好印证灰机「淑女格蕾丝是圣洛夫基金会安插的卧底」。
REWRITE_RELATIONS: dict[str, dict[tuple[str, str, str], tuple[str, str, str]]] = {
    "a1512c58d1d57ec1": {("Manus Vindicti", "持有", "Arcana"): ("Manus Vindicti", "效忠", "Arcana")},
    "e1f12151dc6aba12": {("Manus Vindictae", "持有", "Arcana"): ("Manus Vindictae", "效忠", "Arcana")},
    "daffd2d8b08b783f": {
        ("无名者", "被施加", "基金会"): ("基金会", "剥离记忆", "无名者"),
    },
}


def _alias_bad(a: str) -> str | None:
    s = str(a or "").strip()
    if not s:
        return "空"
    for ch_ in s:
        if ord(ch_) > 0x0900 and not ("一" <= ch_ <= "鿿") and not ch_.isalnum():
            nm = unicodedata.name(ch_, "")
            if nm.startswith(("DEVANAGARI", "ARABIC", "THAI")):
                return f"乱码({nm})"
    if TEMPLATE_LEAK.search(s):
        return "提示词模板泄漏"
    if re.search(r"\bLucy\b", s, re.I) and "Miss Stranger" in s:
        return "角色混淆：把无名者指向露西"
    if CN.search(s) and len(s) >= 12 and SENT_HINT.search(s):
        return "中文整句"
    if PRON_PHRASE.match(s):
        return "英文代词短语"
    return None


def _name_bad(name: str) -> bool:
    """实体名本身是代词短语（my father / their letters / 他们的信 …）。"""
    n = str(name or "").strip()
    return bool(PRON_PHRASE.match(n) or CN_PRON_PHRASE.match(n))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="写盘（默认只预演）")
    args = ap.parse_args()

    n_alias = n_rel = n_ent = n_rel_pron = n_add_alias = n_rw = 0
    report: list[str] = []

    for h, mapping in REWRITE_RELATIONS.items():
        p = CACHE / f"{h}.json"
        if not p.exists():
            report.append(f"[缺失] {h}")
            continue
        data = json.loads(p.read_text(encoding="utf-8"))
        for r in data.get("relations") or []:
            key = (str(r.get("src") or ""), str(r.get("relation") or ""), str(r.get("dst") or ""))
            if key in mapping:
                ns, nr, nd = mapping[key]
                report.append(f"[改关系] {h} :: {key[0]} —{key[1]}→ {key[2]}"
                              f"  ⇒  {ns} —{nr}→ {nd}")
                r["src"], r["relation"], r["dst"] = ns, nr, nd
                n_rw += 1
        if args.apply:
            p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    for h, drops in DROP_RELATIONS.items():
        p = CACHE / f"{h}.json"
        if not p.exists():
            report.append(f"[缺失] {h}")
            continue
        data = json.loads(p.read_text(encoding="utf-8"))
        before = len(data.get("relations") or [])
        kept = []
        for r in data.get("relations") or []:
            key = (str(r.get("src") or ""), str(r.get("relation") or ""), str(r.get("dst") or ""))
            if key in drops:
                n_rel += 1
                report.append(f"[删关系] {h} :: {key[0]} —{key[1]}→ {key[2]}")
                continue
            kept.append(r)
        data["relations"] = kept
        if args.apply and len(kept) != before:
            p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    for p in sorted(CACHE.glob("*.json")):
        data = json.loads(p.read_text(encoding="utf-8"))
        changed = False
        drop_names: set[str] = set()

        for e in data.get("entities") or []:
            nm = str(e.get("name") or "")
            aliases = [str(a) for a in (e.get("aliases") or [])]
            kept_a, dropped = [], []
            for a in aliases:
                why = _alias_bad(a)
                if why:
                    dropped.append((a, why))
                else:
                    kept_a.append(a)
            if dropped:
                e["aliases"] = kept_a
                changed = True
                n_alias += len(dropped)
                for a, why in dropped:
                    report.append(f"[删别名] {p.stem} :: {nm} -{a!r} （{why}）")
            if _name_bad(nm):
                drop_names.add(nm)
                n_ent += 1
                report.append(f"[删实体] {p.stem} :: {nm}（英文代词短语）")

        if drop_names:
            before = len(data.get("entities") or [])
            data["entities"] = [
                e for e in (data.get("entities") or [])
                if str(e.get("name") or "") not in drop_names
            ]
            rels = data.get("relations") or []
            kept = [
                r for r in rels
                if str(r.get("src") or "") not in drop_names
                and str(r.get("dst") or "") not in drop_names
            ]
            n_rel_pron += len(rels) - len(kept)
            data["relations"] = kept
            changed = changed or before != len(data["entities"])

        if changed and args.apply:
            p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    # 补别名必须放在删除之后：像 "its eye" 这类表层形式会被上面的代词短语规则命中
    for h, pairs in ADD_ALIAS.items():
        p = CACHE / f"{h}.json"
        if not p.exists():
            continue
        data = json.loads(p.read_text(encoding="utf-8"))
        for e in data.get("entities") or []:
            for name, alias in pairs:
                if str(e.get("name") or "") != name:
                    continue
                aliases = [str(a) for a in (e.get("aliases") or [])]
                if alias not in aliases:
                    aliases.append(alias)
                    e["aliases"] = aliases
                    n_add_alias += 1
                    report.append(f"[补别名] {h} :: {name} +{alias!r}")
        if args.apply:
            p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n".join(report))
    print(
        f"\n[huiji-fix] {'已写盘' if args.apply else '预演'}："
        f"改关系 {n_rw}，删关系 {n_rel}（冲突）+ {n_rel_pron}（代词端点），删别名 {n_alias}，删实体 {n_ent}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
