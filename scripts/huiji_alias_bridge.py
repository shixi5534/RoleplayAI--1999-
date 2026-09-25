# -*- coding: utf-8 -*-
"""灰机正典 → 剧情图谱「别名桥」生成与核查。

问题
    300 题分诊：188 个缺失证据组里 **147 个是「别名桥缺失」**——
    答案实体就在图里（英文 ASR 正名，如 ``Charlotte`` / ``Tooth Fairy``），
    但用户提问用的中文称谓（薇洛 / 雾女士 / 牙仙）没有通向它的路。
    图谱 fingerprint 的 embedder 是 ``none``，没有向量兜底，桥断了就彻底取不回。

做法（灰机 wiki 是唯一标准）
    1. 用 ``huiji_canon.json``（章节/角色/NPC 的中英对照，来自灰机 wiki）建 en↔zh 索引；
    2. 对图谱实体逐个匹配，**只接受归一化后的精确匹配**（同名才算，绝不做模糊猜测）；
    3. 产出提案：``{正名(图中现有) : [要补的中文名...]}`` + 来源 URL + 依据；
    4. ``--apply`` 才写入 ``plot_aliases.json``（键沿用图中现有正名，避免重建时拆节点）。

用法：
    .venv/Scripts/python.exe -X utf8 scripts/huiji_alias_bridge.py --analyse
    .venv/Scripts/python.exe -X utf8 scripts/huiji_alias_bridge.py --analyse --limit 40
    .venv/Scripts/python.exe -X utf8 scripts/huiji_alias_bridge.py --apply     # 需 --yes

产出：``data/knowledge/_audit/huiji_alias_bridge.json``（提案 + 逐条依据）
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from roleplay.config import get_settings  # noqa: E402
from roleplay.core.knowledge.factory import build_plot_registry  # noqa: E402
from roleplay.core.knowledge.graph_store import norm_name  # noqa: E402
from roleplay.core.knowledge.plot_graph import is_noise_entity  # noqa: E402

CANON = ROOT / "data" / "lore" / "wu_ming_zhe" / "huiji_canon.json"
ALIASES = ROOT / "data" / "lore" / "wu_ming_zhe" / "plot_aliases.json"
TRIAGE = ROOT / "data" / "knowledge" / "_audit" / "plot_rag_triage.json"
OUT = ROOT / "data" / "knowledge" / "_audit" / "huiji_alias_bridge.json"

_CJK = re.compile(r"[\u4e00-\u9fff]")


def load_canon() -> dict:
    if not CANON.is_file():
        raise SystemExit(f"[FAIL] 正典库不存在，请先跑 scripts/huiji_canon.py --harvest：{CANON}")
    return json.loads(CANON.read_text(encoding="utf-8"))


def build_index(canon: dict) -> tuple[dict[str, list[dict]], dict[str, list[dict]]]:
    """en→[条目] 与 zh→[条目]（一个名字可对应多条目，保留全部供人工裁决）。"""
    en_idx: dict[str, list[dict]] = {}
    zh_idx: dict[str, list[dict]] = {}

    def add(zh: str, en: str, kind: str, src: str, extra: dict | None = None) -> None:
        zh = (zh or "").strip()
        en = (en or "").strip()
        rec = {"zh": zh, "en": en, "kind": kind, "source": src}
        if extra:
            rec.update(extra)
        if en:
            en_idx.setdefault(norm_name(en), []).append(rec)
            # 去掉 "Miss/Mr./Ms." 前缀再登记一遍（ASR 里常带称谓）
            stripped = re.sub(r"^(mr|mrs|ms|miss|madam|madame|dr|sir|lady)\.?\s+", "", en,
                              flags=re.I)
            if stripped != en:
                en_idx.setdefault(norm_name(stripped), []).append(rec)
        if zh:
            zh_idx.setdefault(norm_name(zh), []).append(rec)

    for c in canon.get("characters") or []:
        add(c.get("zh", ""), c.get("en", ""), "character", c.get("page", ""))
    for n in canon.get("npcs") or []:
        add(n.get("zh", ""), n.get("en", ""), "npc", n.get("page", ""),
            {"arc": n.get("arc", ""), "identity": n.get("identity", "")})
        # NPC 的 name 字段可能是「绒毛公爵、红色泰坦、杰克老弟」这种并列写法
        for part in re.split(r"[、,，/]", n.get("zh") or ""):
            part = part.strip()
            if part and part != (n.get("zh") or "").strip():
                add(part, n.get("en", ""), "npc", n.get("page", ""))
    for ch in canon.get("chapters") or []:
        add(ch.get("zh", ""), ch.get("en", ""), f"chapter:{ch.get('kind','')}",
            ch.get("page", ""), {"version": ch.get("version", "")})
    # 全站命名表（displaytitle 扫描）：覆盖角色/一览之外的地点、组织、物品、概念页。
    # 分诊实测别名桥缺口大量落在这些类别上，只吃角色表补不到。
    for nt in canon.get("name_table") or []:
        add(nt.get("zh", ""), nt.get("en", ""), "name_table", nt.get("page", ""))
    return en_idx, zh_idx


def analyse(args) -> int:
    canon = load_canon()
    en_idx, zh_idx = build_index(canon)

    settings = get_settings()
    registry = build_plot_registry(settings)
    retr = registry.get(args.character)
    if retr is None:
        print(f"[FAIL] 图谱未加载（character={args.character}）")
        return 2

    table = json.loads(ALIASES.read_text(encoding="utf-8")) if ALIASES.is_file() else {}
    covered: set[str] = set()
    for k, vs in table.items():
        covered.add(norm_name(k))
        for v in vs or []:
            covered.add(norm_name(str(v)))

    entities = retr.store.entities()
    print(f"[load] 图谱实体 {len(entities)}｜别名表条目 {len(table)}（覆盖 {len(covered)} 个归一名）")

    props: list[dict] = []
    stats = Counter()
    for ent in entities:
        name = str(ent.get("name") or "")
        if not name or is_noise_entity(name):
            stats["noise"] += 1
            continue
        aliases = [str(a) for a in (ent.get("aliases") or [])]
        own = {norm_name(name)} | {norm_name(a) for a in aliases}
        # 对实体的**每一个可信拉丁名**去灰机命名表里查中文名，缺哪个补哪个。
        # 注意：不能只处理「还没有中文名」的实体——分诊实测的缺口恰恰是
        # 「有中文名，但不是用户会打的那个」（如 Apple 有正名/别名却没有「摇滚苹果号」）。
        #
        # **可信名 = 正名 ∪ 人工别名表里的名字**，抽取来的别名一律不参与取证。
        # 依据（本轮实测踩到的真错）：抽取别名里混着别家的名字——
        # 实体「迈克尔」（NPC Michael）的抽取别名含 "The Fool"，于是灰机命名表把
        # 「弄臣」（The Fool，**另一个角色**）桥到了迈克尔头上；实体「戒指」的
        # 别名 "The Ring" 又把 NPC「圈环」桥了过来。用噪声别名取证＝把噪声洗成"正典"。
        trusted_src = [name] + [a for a in aliases if norm_name(a) in covered]
        adds: list[str] = []
        src: dict = {}
        ambiguous = False
        for n in trusted_src:
            if not n or _CJK.search(n):
                continue
            hits = en_idx.get(norm_name(n)) or []
            zh = sorted({str(h.get("zh") or "") for h in hits if h.get("zh")})
            if len(zh) > 1:
                ambiguous = True
                continue
            if len(zh) == 1 and norm_name(zh[0]) not in own and zh[0] not in adds:
                adds.append(zh[0])
                src = hits[0]
        if not adds:
            stats["no_new_name"] += 1
            if ambiguous:
                stats["ambiguous"] += 1
            continue
        conf = "high" if not ambiguous else "medium"
        if conf == "high":
            stats["proposed"] += 1
        else:
            stats["proposed_medium"] += 1
        props.append({
            "key": name,
            "add": adds[:4],
            "confidence": conf,
            "reason": f"灰机命名表（{src.get('kind')}）中英对照精确匹配",
            "kind": src.get("kind", ""),
            "source": src.get("page", ""),
            "alias_count": len(aliases),
        })

    # ── 顺带核查：分诊里「别名桥缺失」的答案实体，能不能被新别名救活 ──
    rescue = Counter()
    rescue_rows: list[dict] = []
    if TRIAGE.is_file():
        tri = json.loads(TRIAGE.read_text(encoding="utf-8"))
        for g in tri.get("action_alias_bridge_gap") or []:
            query = g.get("q") or ""
            ents = g.get("group_entities") or []
            rescued = []
            for kw in ents:
                # 证据关键词本身就是正典写法：直接把中文关键词当作候选桥
                if _CJK.search(str(kw)) and norm_name(str(kw)) not in covered:
                    rescued.append(str(kw))
            if rescued:
                rescue["rescuable_by_chinese_kw"] += 1
                rescue_rows.append({"id": g.get("id"), "q": query, "candidates": rescued})
            else:
                rescue["needs_content_retrieval"] += 1

    payload = {
        "meta": {
            "tool": "scripts/huiji_alias_bridge.py",
            "canon_source": canon.get("_source"),
            "canon_fetched_at": canon.get("fetched_at"),
            "entities": len(entities),
            "stats": dict(stats),
        },
        "proposals": props,
        "triage_rescue": {"summary": dict(rescue), "rows": rescue_rows[:200]},
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"[stat] {dict(stats)}")
    print(f"[triage] {dict(rescue)}")
    print(f"[save] {OUT}")
    print("\n=== high 置信提案（前 40）===")
    n = 0
    for p in props:
        if p["confidence"] != "high":
            continue
        print(f"  {p['key']:32s} += {p['add']}   ← {p['kind']} {p['source']}")
        n += 1
        if n >= 40:
            break
    return 0


def apply_proposals(args) -> int:
    data = json.loads(OUT.read_text(encoding="utf-8"))
    props = [p for p in data.get("proposals") or [] if p["confidence"] == "high"]
    if not args.yes:
        print(f"[dry-run] 将写入 {len(props)} 条提案；确认后加 --yes")
        return 0
    table = json.loads(ALIASES.read_text(encoding="utf-8"))
    added = 0
    for p in props:
        key = p["key"]
        cur = table.setdefault(key, [])
        for a in p["add"]:
            if a not in cur:
                cur.append(a)
                added += 1
    ALIASES.write_text(json.dumps(table, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[apply] 新增 {added} 条别名，写入 {ALIASES}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="灰机正典 → 别名桥")
    ap.add_argument("--character", default="wu_ming_zhe")
    ap.add_argument("--analyse", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--yes", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    if args.apply:
        return apply_proposals(args)
    return analyse(args)


if __name__ == "__main__":
    raise SystemExit(main())
