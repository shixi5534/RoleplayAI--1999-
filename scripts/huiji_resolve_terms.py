# -*- coding: utf-8 -*-
"""灰机 wiki 中文术语 → 官方英文名 批量核查（别名桥的取证环节）。

用途
    分诊给出的「查询里出现、图谱不认」的中文正典词（伯里克利 / 卡穆塔 / 芝诺 /
    摇滚苹果号 …），需要一个**权威英文名**才能接进英文 ASR 语料。
    本脚本逐词做灰机检索 + 精确页核查，产出 ``{中文词: [英文名...]}`` 提案，
    每条带来源 URL 与命中页面，供人工/脚本审核后再写入 ``plot_aliases.json``。

**只认灰机，不认题集**：词表来自分诊（用户实际怎么说），英文名一律来自 wiki
（正典怎么写）——绝不用 300 题集的参考答案反查，避免评测泄漏。

用法：
    .venv/Scripts/python.exe -X utf8 scripts/huiji_resolve_terms.py --terms 伯里克利 卡穆塔 芝诺
    .venv/Scripts/python.exe -X utf8 scripts/huiji_resolve_terms.py --from-triage
    .venv/Scripts/python.exe -X utf8 scripts/huiji_resolve_terms.py --from-triage --apply
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from huiji_fetch import HuijiSession, clean_title  # noqa: E402
from roleplay.core.knowledge.graph_store import norm_name  # noqa: E402

TRIAGE = ROOT / "data" / "knowledge" / "_audit" / "plot_rag_triage_canon.json"
CANON = ROOT / "data" / "lore" / "wu_ming_zhe" / "huiji_canon.json"
ALIASES = ROOT / "data" / "lore" / "wu_ming_zhe" / "plot_aliases.json"
OUT = ROOT / "data" / "knowledge" / "_audit" / "huiji_term_proposals.json"

_CJK = re.compile(r"[\u4e00-\u9fff]")
# 拉丁专名：首字母大写、可含空格/撇号/点/连字符，长度 ≥3
_EN_NAME = re.compile(r"\b([A-Z][A-Za-z'’\.\-]{1,}(?:\s+[A-Z][A-Za-z'’\.\-]{1,}){0,3})\b")
# 灰机页面里的**结构词**（文件名、模板名、UI 词），不是人物/地名的专名。
# 实测不做这层过滤时，「翡冷翠」会被解析成 ['File','T-','Item']、「净化」成
# ['Skill','Color']——写进别名表就是纯噪声，故一律拒收。
_JUNK_EN = {
    "file", "item", "items", "skill", "skills", "color", "colour", "the", "a", "an",
    "and", "or", "of", "in", "on", "for", "with", "page", "pages", "image", "images",
    "template", "templates", "category", "categories", "class", "style", "span", "div",
    "width", "height", "size", "px", "png", "jpg", "webp", "gif", "svg", "right", "left",
    "center", "none", "hide", "show", "yes", "no", "true", "false", "nan", "info",
    "note", "notes", "data", "value", "name", "text", "type", "id", "url", "link",
    "hp", "atk", "def", "buff", "debuff", "lv", "exp", "star", "stars", "rarity",
    "rare", "bufftype", "special", "effect", "damage", "round", "turn", "target",
}


def _acceptable_en(value: str) -> bool:
    v = (value or "").strip().strip("《》").strip()
    if len(v) < 3 or _CJK.search(v):
        return False
    if v.lower() in _JUNK_EN:
        return False
    if len(v) <= 2 or v.endswith("-"):
        return False
    return True


def terms_from_triage(graph_names: set[str]) -> list[str]:
    """分诊：失败题里「证据关键词是中文、图谱却不认」的词（= 别名桥缺口）。"""
    if not TRIAGE.is_file():
        return []
    tri = json.loads(TRIAGE.read_text(encoding="utf-8"))
    out: list[str] = []
    seen: set[str] = set()
    for row in tri.get("items") or []:
        if row.get("strict_pass"):
            continue
        for dt in row.get("details") or []:
            for kw in dt.get("keywords") or []:
                kw = str(kw)
                if not _CJK.search(kw) or len(kw) < 2:
                    continue
                if norm_name(kw) in graph_names or norm_name(kw) in seen:
                    continue
                seen.add(norm_name(kw))
                out.append(kw)
    return out


def resolve(s: HuijiSession, term: str) -> dict:
    """灰机核查单个中文词：精确页 → （无则）检索首条 → 抽取英文名。"""
    rec: dict = {"term": term, "en": [], "evidence": [], "status": "unresolved"}
    # ① 精确页面 + displaytitle（角色页形如「牙仙 Tooth Fairy」）
    d = s.cached_api("wikitext", {"action": "parse", "page": term,
                                  "prop": "wikitext|displaytitle"})
    p = d.get("parse") or {}
    if p.get("wikitext"):
        dt = clean_title(p.get("displaytitle") or "")
        tail = dt[len(term):].strip() if dt.startswith(term) else dt
        if tail and not _CJK.search(tail):
            rec["en"].append(tail.strip("《》"))
            rec["evidence"].append({"via": "page.displaytitle", "title": term, "value": tail})
        # 模板参数 nameEn=
        for m in re.finditer(r"\|\s*(?:nameEn|name_en|英文名)\s*=\s*([^|\n}]+)", p["wikitext"]):
            v = clean_title(m.group(1)).strip()
            if v and not _CJK.search(v):
                rec["en"].append(v)
                rec["evidence"].append({"via": "page.nameEn", "title": term, "value": v})
        if rec["en"]:
            rec["status"] = "page"
            rec["url"] = f"https://res1999.huijiwiki.com/wiki/{term}"
            return _dedup(rec)
    # ② 检索：取首条页面，从**与中文词同一行/括号内**找英文专名（不看整段正文，
    #    那会把页脚模板、图集说明里的词也捞进来）。
    r = s.cached_api("search:" + term, {"action": "query", "list": "search",
                                        "srsearch": term, "srlimit": "5"})
    hits = [clean_title(h.get("title", ""))
            for h in ((r.get("query") or {}).get("search") or [])]
    rec["search_hits"] = hits[:5]
    for title in hits[:3]:
        dd = s.page_wikitext(title)
        wt = (dd.get("parse") or {}).get("wikitext") or ""
        if not wt:
            continue
        for m in re.finditer(re.escape(term) + r"[^\n]{0,40}", wt):
            frag = m.group(0)
            for mm in _EN_NAME.finditer(frag):
                cand = mm.group(1)
                if _acceptable_en(cand):
                    rec["en"].append(cand)
                    rec["evidence"].append({"via": "same-line", "title": title,
                                            "value": cand, "line": frag[:80]})
        # 首页模板的 nameEn= 最可信
        for m in re.finditer(r"\|\s*(?:nameEn|name_en)\s*=\s*([^|\n}]+)", wt):
            v = clean_title(m.group(1)).strip()
            if _acceptable_en(v):
                rec["en"].insert(0, v)
                rec["evidence"].insert(0, {"via": "page.nameEn", "title": title, "value": v})
    if rec["en"]:
        rec["status"] = "search"
        rec["url"] = f"https://res1999.huijiwiki.com/wiki/{hits[0]}" if hits else ""
    return _dedup(rec)


def _dedup(rec: dict) -> dict:
    seen: list[str] = []
    for e in rec["en"]:
        e = e.strip().strip("《》")
        if _acceptable_en(e) and e not in seen:
            seen.append(e)
    rec["en"] = seen[:6]
    if not seen and rec.get("status") not in ("error",):
        rec["status"] = "unresolved"
    return rec


def load_graph_names() -> set[str]:
    from roleplay.config import get_settings
    from roleplay.core.knowledge.factory import build_plot_registry

    r = build_plot_registry(get_settings()).get("wu_ming_zhe")
    names: set[str] = set()
    if r is None:
        return names
    for _eid, _c, ns in r._named_entities():  # noqa: SLF001
        names.update(n for n in ns if n)
    return names


def main() -> int:
    ap = argparse.ArgumentParser(description="灰机中文术语 → 英文名核查")
    ap.add_argument("--terms", nargs="*", default=[])
    ap.add_argument("--from-triage", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--yes", action="store_true")
    args = ap.parse_args()

    names = load_graph_names()
    terms = list(args.terms)
    if args.from_triage:
        for t in terms_from_triage(names):
            if t not in terms:
                terms.append(t)
    if not terms:
        ap.print_help()
        return 2
    print(f"[terms] 待核查 {len(terms)} 个：{terms}")

    rows: list[dict] = []
    with HuijiSession(headless=False) as s:
        for t in terms:
            try:
                rows.append(resolve(s, t))
            except SystemExit as e:
                rows.append({"term": t, "en": [], "status": "error", "error": str(e)})

    resolved = [r for r in rows if r["en"]]
    payload = {
        "meta": {"tool": "scripts/huiji_resolve_terms.py",
                 "source": "灰机 wiki（res1999.huijiwiki.com）",
                 "terms": len(terms), "resolved": len(resolved)},
        "proposals": rows,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n=== 核查结果（{len(resolved)}/{len(terms)} 有英文名）===")
    for r in rows:
        mark = "✓" if r["en"] else "✗"
        print(f"  {mark} {r['term']:10s} → {r['en']}   ({r['status']})")
    print(f"[save] {OUT}")

    if not args.apply:
        return 0
    if not args.yes:
        print("[dry-run] 加 --yes 才会写入 plot_aliases.json")
        return 0
    # 写入：以英文名为键（不重命名图中既有节点），中文词作为别名
    table = json.loads(ALIASES.read_text(encoding="utf-8")) if ALIASES.is_file() else {}
    existing = {norm_name(k) for k in table}
    for vs in table.values():
        existing.update(norm_name(str(v)) for v in (vs or []))
    added = 0
    for r in resolved:
        en = r["en"][0]
        if norm_name(en) in existing:
            # 英文名已在别名体系里：把中文词挂到它所属的正名条目下
            key = next((k for k, vs in table.items()
                        if any(norm_name(str(v)) == norm_name(en) for v in (vs or []))
                        or norm_name(k) == norm_name(en)), None)
            if key is None:
                continue
            if r["term"] not in table[key]:
                table[key].append(r["term"])
                added += 1
            continue
        table.setdefault(en, [])
        if r["term"] not in table[en]:
            table[en].append(r["term"])
            added += 1
    ALIASES.write_text(json.dumps(table, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[apply] 新增 {added} 条别名 → {ALIASES}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
