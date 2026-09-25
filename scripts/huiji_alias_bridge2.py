# -*- coding: utf-8 -*-
"""别名桥 v2：以灰机中英对照词典为标准，为图谱实体补桥。

相比 v1（huiji_alias_bridge.py）增强三点：
  ① 数据源从「canon 926 条」扩到「huiji_lexicon.json 913 条中文 / 855 条英文」
     （含 202 个灰机正文页里提取的敌人 / 地点 / 活动名）；
  ② 支持**双向**：英文正名 → 补中文（v1 只有这个方向），中文正名 → 补英文；
  ③ 支持**异译**：图中译名与灰机译名不同（如图中「塞内塔」、灰机「扎内塔」），
     把灰机译名作为额外别名补上。

质量红线（与 v1 一致，不放松）：
  - 只接受归一化后的**精确匹配**，绝不做模糊 / 相似度猜测；
  - 一个英文名在灰机里对应多个中文名（歧义）→ 跳过并记录待裁决；
  - 候选名必须已存在于灰机词典，来源可复核；
  - 别名不得与正名相同、不得与图谱中**其它实体**的正名相撞。

用法：
  .venv/Scripts/python.exe -X utf8 scripts/huiji_alias_bridge2.py --analyse
  .venv/Scripts/python.exe -X utf8 scripts/huiji_alias_bridge2.py --apply --yes
产出：data/knowledge/_audit/huiji_alias_bridge_v2.json
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

LEXICON = ROOT / "data" / "lore" / "wu_ming_zhe" / "huiji_lexicon.json"
CANON_JSON = ROOT / "data" / "lore" / "wu_ming_zhe" / "huiji_canon.json"
ALIASES = ROOT / "data" / "lore" / "wu_ming_zhe" / "plot_aliases.json"
TRIAGE = ROOT / "data" / "knowledge" / "_audit" / "plot_rag_triage_r0.json"
OUT = ROOT / "data" / "knowledge" / "_audit" / "huiji_alias_bridge_v2.json"

CJK_RUN = None

# 明显不是专名的英文词（别名通道的过滤）
EN_STOP_WORDS = {
    "the", "and", "you", "that", "this", "with", "have", "what", "your", "they",
    "from", "will", "would", "there", "their", "about", "which", "when", "them",
    "these", "than", "then", "some", "such", "only", "other", "into", "more",
    "very", "just", "also", "been", "were", "said", "each", "much", "many",
    "miss", "mister", "sir", "madam", "lady", "captain", "doctor", "professor",
    "yes", "no", "not", "but", "for", "are", "was", "has", "had", "his", "her",
    "him", "she", "one", "two", "all", "any", "can", "our", "out", "who", "why",
    "how", "now", "new", "old", "day", "night", "time", "people", "thing",
}


def has_cjk(s: str) -> bool:
    return any("\u4e00" <= ch <= "\u9fff" for ch in s)


def analyse(args) -> int:
    lex = json.loads(LEXICON.read_text(encoding="utf-8"))
    zh2en: dict[str, list[str]] = lex["zh2en"]
    en2zh: dict[str, list[str]] = lex["en2zh"]
    rules: dict[str, list[str]] = lex.get("rules") or {}

    HIGH_RULES = ("canon.", "wiki.DisplayTitle", "wiki.cb", "wiki.displaytitle")
    # 冲突检测：某个名字若出现在高可信来源里，就不要再被 wiki.plain 的配对覆盖/竞争。
    # 注意：canon 里存在中英同名的条目（如 APPLe ↔ APPLe），这类在 lexicon 里
    # 因「中文名必须含汉字」被丢弃，所以这里直接回读 canon 原始表补全。
    high_zh: set[str] = set()
    high_en: set[str] = set()
    canon = json.loads(CANON_JSON.read_text(encoding="utf-8"))
    for arr in ("characters", "npcs", "chapters", "name_table"):
        for rec in canon.get(arr) or []:
            zh = str(rec.get("zh") or "").strip()
            en = str(rec.get("en") or "").strip()
            if zh:
                high_zh.add(norm_name(zh))
                for part in zh.replace("、", ",").replace("，", ",").replace("/", ",").split(","):
                    if part.strip():
                        high_zh.add(norm_name(part.strip()))
            if en:
                high_en.add(norm_name(en))
    for k, rs in rules.items():
        if any(r.startswith(HIGH_RULES) for r in rs):
            zh, _, en = k.partition("\u0000")
            high_zh.add(norm_name(zh))
            high_en.add(norm_name(en))

    def pair_ok(zh: str, en: str) -> bool:
        """只有高可信规则产出的配对可用。

        ``wiki.plain``（页面纯文本里「中文 English」紧邻并列）实测混入大量错配
        （``UTTU ↔ 阅读访谈``、``UFO ↔ 猎人``、``狼群 ↔ Pavia``）——它抓到的多是
        关卡表头与敌人名，穷举过滤不现实，且这些名字对剧情问答无用。
        质量优先：直接弃用该规则，只保留 canon 表 / DisplayTitle / cb / displaytitle。
        """
        key = f"{zh}\u0000{en}"
        rs = rules.get(key) or []
        return any(r.startswith(HIGH_RULES) for r in rs)

    # 归一化索引（只保留通过判定且 1:1 的配对）
    zh_idx: dict[str, set[str]] = {}
    en_idx: dict[str, set[str]] = {}
    for zh, ens in zh2en.items():
        for en in ens:
            if not pair_ok(zh, en):
                continue
            zh_idx.setdefault(norm_name(zh), set()).add(en)
            en_idx.setdefault(norm_name(en), set()).add(zh)

    settings = get_settings()
    registry = build_plot_registry(settings)
    retr = registry.get(args.character)
    if retr is None:
        print(f"[FAIL] 图谱未加载（character={args.character}）")
        return 2

    table = json.loads(ALIASES.read_text(encoding="utf-8")) if ALIASES.is_file() else {}
    aliased: set[str] = set()
    for k, vs in table.items():
        aliased.add(norm_name(k))
        for v in vs or []:
            aliased.add(norm_name(str(v)))

    entities = retr.store.entities()
    # 图谱里所有实体正名（用于"别名不得撞别家正名"的检查）
    all_names = {norm_name(str(e.get("name") or "")) for e in entities}
    # triage 缺口组的实体名（用于评估桥的命中率）
    targets: set[str] = set()
    if TRIAGE.is_file():
        tri = json.loads(TRIAGE.read_text(encoding="utf-8"))
        for g in tri.get("action_alias_bridge_gap") or []:
            for k in (g.get("group_entities") or []) + (g.get("keywords") or []):
                k = str(k or "").strip()
                if k:
                    targets.add(norm_name(k))

    print(f"[load] 图谱实体 {len(entities)}｜灰机词典 中 {len(zh_idx)} / 英 {len(en_idx)}"
          f"｜人工别名表 {len(table)}｜缺口靶子 {len(targets)}")

    props: list[dict] = []
    stats: Counter[str] = Counter()
    hit_targets: set[str] = set()

    for ent in entities:
        name = str(ent.get("name") or "")
        if not name or is_noise_entity(name):
            stats["noise"] += 1
            continue
        raw_aliases = [str(a) for a in (ent.get("aliases") or [])]
        own = {norm_name(name)} | {norm_name(a) for a in raw_aliases}
        # 取证名：正名 + 人工别名表里的名字（防噪声洗白）。
        trusted = [name] + [a for a in raw_aliases if norm_name(a) in aliased]
        # 补充通路：**正名是中文**的实体，其拉丁别名可参与取证。
        # 依据：正名已是中文时，别名里的拉丁串就是它的外文名（如「塞内塔」别名含
        # Zanetta），这是捕捉「异译」的唯一通路——图中译名与灰机译名不同
        # （图中「塞内塔」vs 灰机「扎内塔」）时，靠这条把灰机译名补进来。
        # 噪声风险由 en_idx 的 1:1 约束 + 与其它实体正名的撞名检查兜住。
        if has_cjk(name):
            for a in raw_aliases:
                a = a.strip()
                if (len(a) >= 4 and a[:1].isupper() and not has_cjk(a)
                        and re.fullmatch(r"[A-Za-z0-9'’\-\. ]+", a)
                        and a.lower() not in EN_STOP_WORDS):
                    trusted.append(a)

        adds: list[dict] = []
        for n in trusted:
            if not n:
                continue
            nn = norm_name(n)
            if has_cjk(n):
                # 中文名 → 查英文（反向桥）
                ens = sorted(zh_idx.get(nn) or [])
                if len(ens) == 1:
                    cand = ens[0]
                    cn = norm_name(cand)
                    if cn not in own and cand not in [a["name"] for a in adds]:
                        if cn in all_names:
                            stats["skip_name_clash"] += 1
                            continue
                        adds.append({"name": cand, "dir": "zh→en",
                                     "reason": f"灰机中英对照：{n} ↔ {cand}"})
            else:
                # 英文名 → 查中文（正向桥）
                zhs = sorted(en_idx.get(nn) or [])
                if len(zhs) > 1:
                    stats["ambiguous"] += 1
                    continue
                if len(zhs) == 1:
                    cand = zhs[0]
                    cn = norm_name(cand)
                    if cn not in own and cand not in [a["name"] for a in adds]:
                        if cn in all_names:
                            stats["skip_name_clash"] += 1
                            continue
                        adds.append({"name": cand, "dir": "en→zh",
                                     "reason": f"灰机中英对照：{n} ↔ {cand}"})
        if not adds:
            stats["no_new_name"] += 1
            continue

        stats["proposed"] += 1
        key = norm_name(name)
        if key in targets:
            hit_targets.add(key)
        props.append({
            "key": name,
            "type": ent.get("type") or "",
            "mentions": ent.get("mentions") or 0,
            "add": [a["name"] for a in adds],
            "detail": adds,
            "confidence": "high",
            "source": "灰机 wiki 中文维基（huiji_lexicon.json）",
        })

    # 缺口靶子里能直接补上名字的
    for k in targets:
        if len(en_idx.get(k) or []) == 1:
            hit_targets.add(k)

    payload = {
        "meta": {
            "tool": "scripts/huiji_alias_bridge2.py",
            "canon_source": "灰机 wiki《重返未来：1999》中文维基（离线 lexicon）",
            "entities": len(entities),
            "lexicon": {"zh": len(zh_idx), "en": len(en_idx)},
            "targets": len(targets),
            "targets_covered": len(hit_targets),
            "stats": dict(stats),
        },
        "proposals": props,
        "targets": sorted(targets),
        "targets_covered": sorted(hit_targets),
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"[stat] {dict(stats)}")
    print(f"[targets] 缺口靶子 {len(targets)}｜桥可覆盖 {len(hit_targets)}")
    print(f"[save] {OUT.relative_to(ROOT)}")
    print()
    print("=== 提案样例（前 30） ===")
    for p in props[:30]:
        print(f"  {p['key'][:34]:<34} += {p['add'][:3]}  ({p['detail'][0]['dir']})")

    if args.apply:
        if not args.yes:
            print("[ABORT] --apply 需要同时给 --yes")
            return 1
        merged = 0
        for p in props:
            cur = table.setdefault(p["key"], [])
            for a in p["add"]:
                if a not in cur:
                    cur.append(a)
                    merged += 1
        ALIASES.write_text(json.dumps(table, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"[apply] 写入 plot_aliases.json：新增 {merged} 条别名，涉及 {len(props)} 个实体")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--character", default="wu_ming_zhe")
    ap.add_argument("--analyse", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--yes", action="store_true")
    args = ap.parse_args()
    return analyse(args)


if __name__ == "__main__":
    raise SystemExit(main())
