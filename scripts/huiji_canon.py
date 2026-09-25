# -*- coding: utf-8 -*-
"""灰机 wiki 正典库采集：把《重返未来:1999》的官方中文命名体系抓下来，供剧情图谱对齐。

为什么需要
    剧情图谱的实体正名来自 **B 站英文 ASR 转写**（Charlotte / Tooth Fairy / Rockin' Apple…），
    而用户提问用的是**中文正典名**（薇洛 / 牙仙 / 摇滚苹果号…）。
    300 题分诊结论：188 个缺失证据组里 **147 个是「别名桥缺失」**——
    实体在图里，但查询里的中文称谓找不到通向它的路。
    灰机 wiki 是这套中文命名体系的正典来源，本脚本负责把它结构化。

采集内容（全部带来源 URL，可复核）
    chapters   章节表：中文篇名 / 英文篇名 / 版本号 / 序号（来源：章节列表/主线故事）
    characters 可征集角色：中文名 / 英文名 / 页面（来源：Category:角色 + pageprops.displaytitle）
    npcs       其他角色一览：中文名 / 英文名 / 真实身份（来源：其他角色一览/*）
    pages      术语/组织/地点页的 wikitext 原文（按需）

用法（项目根目录，每次运行会复用缓存，重复跑不联网）：
    .venv/Scripts/python.exe -X utf8 scripts/huiji_canon.py --harvest
    .venv/Scripts/python.exe -X utf8 scripts/huiji_canon.py --status
    .venv/Scripts/python.exe -X utf8 scripts/huiji_canon.py --page 薇洛
    .venv/Scripts/python.exe -X utf8 scripts/huiji_canon.py --search 雾女士

产出：``data/lore/wu_ming_zhe/huiji_canon.json``
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from huiji_fetch import HuijiSession, clean_title  # noqa: E402

OUT = ROOT / "data" / "lore" / "wu_ming_zhe" / "huiji_canon.json"

# 章节表页（含主线全部章节的中英对照）
CHAPTER_PAGES = ["章节列表/主线故事", "章节列表", "主线故事"]
# NPC 一览（中文名 / 英文名 / 本名或身份）
NPC_PAGES = ["其他角色一览/1.x", "其他角色一览/2.x", "其他角色一览/3.x",
             "其他角色一览", "其他角色一览/联动"]
# 关键术语/组织/地点页（剧情图谱里高频出现、且容易与英文名脱节的）
TERM_PAGES = [
    "暴雨", "圣洛夫基金会", "重塑之手", "鸽子屋", "第一防线学校", "夜巡特遣管理局",
    "司辰小队", "共融院", "委外合约人才管理组织", "联合委员会",
    "洞穴的囚徒", "绿湖噩梦", "今夜星光灿烂", "孤独之歌", "再见，来亚什基",
    "老虎的金黄", "在我们的时代", "夜色温柔", "疯癫与文明", "绿松石蛇俱乐部",
    "圣火纪行：东区黎明", "飞驰！明日之城", "复乐园", "唐人街影话", "朔日手记",
    "聚合浪潮", "雷米特杯失窃案", "77号往事", "地球上最后的夜晚", "无路可返",
    "摇滚苹果号", "自由海风号", "发条装置", "趋光性定律", "神秘学家", "神秘学家艺术品",
    "雾中盛会", "血痛", "零号", "阿派朗", "乌卢斯", "努库泰澳",
]

# 章节表里的行：形如 `| 1.4 || 第五章 || [[洞穴的囚徒]] || ...`
_WIKILINK = re.compile(r"\[\[([^\]\|#]+)(?:\|([^\]]+))?\]\]")
_EN_IN_PAREN = re.compile(r"([A-Za-z][A-Za-z0-9''\.\-:! ]{2,60})")
_CJK = re.compile(r"[\u4e00-\u9fff]")


def strip_wiki(text: str) -> str:
    """wikitext → 纯文本（够用版：去模板、去链接语法、去 HTML）。"""
    text = re.sub(r"<ref[^>]*>.*?</ref>", "", text or "", flags=re.S)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\{\{[^{}]*\}\}", "", text)
    text = re.sub(r"\{\{[^{}]*\}\}", "", text)
    text = _WIKILINK.sub(lambda m: (m.group(2) or m.group(1)), text)
    text = text.replace("'''", "").replace("''", "")
    return text.strip()


def links_in(text: str) -> list[str]:
    return [clean_title(m.group(2) or m.group(1)) for m in _WIKILINK.finditer(text or "")]


def parse_templates(text: str, names: list[str]) -> list[dict]:
    """抽取 ``{{name|k=v|位置参数}}`` 形式的模板调用为 dict 列表。

    只处理**无嵌套花括号**的调用（灰机的数据模板都满足）；``[[链接]]`` 不受影响。
    位置参数收进 ``_pos``。
    """
    pat = re.compile(r"\{\{\s*(?:" + "|".join(re.escape(n) for n in names) +
                     r")\s*((?:\|[^{}]*)?)\}\}")
    out: list[dict] = []
    for m in pat.finditer(text or ""):
        params: dict = {}
        pos: list[str] = []
        for part in (m.group(1) or "").split("|")[1:]:
            part = part.strip()
            if not part:
                continue
            if "=" in part:
                k, v = part.split("=", 1)
                params[k.strip()] = v.strip()
            else:
                pos.append(part)
        params["_pos"] = pos
        out.append(params)
    return out


def harvest_name_table(s: HuijiSession, *, max_pages: int = 20000,
                       batch: int = 40) -> list[dict]:
    """全站命名表：枚举所有页面，取 ``pageprops.displaytitle`` 抽出「中文名 + 英文名」。

    为什么值得全站扫：灰机的页面命名约定就是「中文名 <small>English</small>」，
    所以一份 displaytitle 全表 = **该 wiki 知道的全部中英名对照**。
    角色/其他角色一览只覆盖 325 条，而分诊实测的别名桥缺口大量落在
    地点 / 组织 / 物品 / 概念上——不把全站捞一遍就补不到。
    """
    titles: list[str] = []
    cont: dict = {}
    while len(titles) < max_pages:
        params = {"action": "query", "list": "allpages", "aplimit": "500"}
        params.update(cont)
        d = s.cached_api("allpages:" + json.dumps(cont, sort_keys=True), params)
        q = d.get("query") or {}
        titles.extend(clean_title(p.get("title", "")) for p in (q.get("allpages") or []))
        # MediaWiki 的续传令牌在**响应根级**的 ``continue``，不在 ``query`` 里——
        # 取错位置会让枚举在第一页（500 条）就停住，而脚本仍报"采集完成"
        # （实测只拿到 616/数千页，差点把"漏采"当成"wiki 就这么多"）。
        cont = d.get("continue") or {}
        if not cont:
            break
    titles = [t for t in dict.fromkeys(titles) if t]
    out: list[dict] = []
    for i in range(0, len(titles), batch):
        chunk = titles[i:i + batch]
        q = s.cached_api("pageprops", {"action": "query", "prop": "pageprops",
                                       "titles": "|".join(chunk),
                                       "ppprop": "displaytitle"})
        for p in ((q.get("query") or {}).get("pages") or []):
            title = clean_title(p.get("title", ""))
            dt = clean_title((p.get("pageprops") or {}).get("displaytitle") or "")
            if not dt or dt == title:
                continue
            # displaytitle 形如「牙仙 Tooth Fairy」/「薇洛 Willow」/「6 Six」
            tail = dt[len(title):].strip() if dt.startswith(title) else ""
            if not tail or _CJK.search(tail):
                continue
            out.append({"zh": title, "en": tail.split("/")[0].strip(),
                        "kind": "page",
                        "page": f"https://res1999.huijiwiki.com/wiki/{title}"})
    return out


def harvest_chapters(s: HuijiSession) -> list[dict]:
    """章节表 → 章/篇（arc）与集（episode）两级中文名 ↔ 英文名。"""
    out: list[dict] = []
    for page in CHAPTER_PAGES:
        d = s.page_wikitext(page)
        wt = (d.get("parse") or {}).get("wikitext") or ""
        if not wt:
            continue
        # 篇（章）：{{title|序章 此即明日|This is Tomorrow|2}} 或 {{title|1ST 在我们的时代里|In Our Time|2}}
        for t in parse_templates(wt, ["title"]):
            pos = [p for p in t.get("_pos", []) if p]
            if len(pos) >= 2:
                zh, en = pos[0], pos[1]
                zh = re.sub(r"^\s*\d+\s*(?:ST|ND|RD|TH)?\s*", "", zh).strip()
                zh = re.sub(r"^第[一二三四五六七八九十百]+章\s*", "", zh).strip()
                if zh:
                    out.append({"kind": "arc", "zh": zh, "en": en,
                                "version": "", "page": page})
        # 集：{{章节列表|link=序章-01|index=01|name=摇滚电台|nameEn=Rock'in Radio|mode=single}}
        for t in parse_templates(wt, ["章节列表"]):
            name = t.get("name") or ""
            name_en = t.get("nameEn") or ""
            if name:
                out.append({"kind": "episode", "zh": name, "en": name_en,
                            "version": "", "index": t.get("index") or "",
                            "page": page})
    # 其他角色一览页的 `== {{stagv|2.4}} 地球上最后的夜晚 ==` 也是篇名（带版本号）
    for page in NPC_PAGES:
        d = s.page_wikitext(page)
        wt = (d.get("parse") or {}).get("wikitext") or ""
        for m in re.finditer(r"==\s*\{\{\s*stagv\s*\|\s*([\d.]+)\s*\}\}\s*([^=\n]+?)\s*==", wt):
            out.append({"kind": "arc", "zh": clean_title(m.group(2)), "en": "",
                        "version": m.group(1), "page": page})

    dedup: dict[tuple, dict] = {}
    for r in out:
        key = (r.get("kind"), r["zh"])
        cur = dedup.get(key)
        if cur is None:
            dedup[key] = r
        else:
            for f in ("en", "version", "index"):
                if not cur.get(f) and r.get(f):
                    cur[f] = r[f]
    return sorted(dedup.values(), key=lambda r: (r.get("kind"), r["zh"]))


def harvest_characters(s: HuijiSession, limit: int = 400) -> list[dict]:
    """Category:角色 → 中文名 / 英文名（displaytitle 里带 <small>English</small>）。"""
    d = s.cached_api("cat:角色", {"action": "query", "list": "categorymembers",
                                  "cmtitle": "Category:角色", "cmlimit": str(limit)})
    titles = [clean_title(m.get("title", ""))
              for m in ((d.get("query") or {}).get("categorymembers") or [])]
    titles = [t for t in titles if t]
    out: list[dict] = []
    for i in range(0, len(titles), 40):
        batch = titles[i:i + 40]
        q = s.cached_api("pageprops", {"action": "query", "prop": "pageprops",
                                       "titles": "|".join(batch),
                                       "ppprop": "displaytitle"})
        pages = ((q.get("query") or {}).get("pages") or [])
        for p in pages:
            title = clean_title(p.get("title", ""))
            dt = clean_title(((p.get("pageprops") or {}).get("displaytitle") or ""))
            en = ""
            if dt and dt != title:
                tail = dt[len(title):].strip() if dt.startswith(title) else dt
                if tail and not re.search(r"[\u4e00-\u9fff]", tail):
                    en = tail
            out.append({"zh": title, "en": en,
                        "page": f"https://res1999.huijiwiki.com/wiki/{title}"})
    return out


def harvest_npcs(s: HuijiSession) -> list[dict]:
    """其他角色一览/* → NPC 中文名 / 英文名 / 身份 / 所属篇。"""
    out: list[dict] = []
    for page in NPC_PAGES:
        d = s.page_wikitext(page)
        wt = (d.get("parse") or {}).get("wikitext") or ""
        if not wt:
            continue
        # 先按 `== {{stagv|2.4}} 地球上最后的夜晚 ==` 切块，块内 NPC 归属该篇
        blocks = re.split(r"==\s*\{\{\s*stagv\s*\|\s*([\d.]+)\s*\}\}\s*([^=\n]+?)\s*==", wt)
        chunks: list[tuple[str, str, str]] = []
        if len(blocks) > 1:
            for i in range(1, len(blocks), 3):
                chunks.append((blocks[i], clean_title(blocks[i + 1]),
                               blocks[i + 2] if i + 2 < len(blocks) else ""))
        else:
            chunks.append(("", "", wt))
        for ver, arc, body in chunks:
            for t in parse_templates(body, ["NPC信息/M", "NPC信息/L", "NPC信息"]):
                zh = t.get("name") or ""
                if not zh:
                    continue
                out.append({
                    "zh": clean_title(zh),
                    "en": t.get("nameEn") or "",
                    "identity": strip_wiki(t.get("desc") or ""),
                    "version": ver, "arc": arc, "page": page,
                })
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="灰机 wiki 正典库采集")
    ap.add_argument("--harvest", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--page")
    ap.add_argument("--search")
    ap.add_argument("--limit", type=int, default=20)
    args = ap.parse_args()

    if args.status:
        if not OUT.is_file():
            print("[--] 正典库尚未生成")
            return 2
        d = json.loads(OUT.read_text(encoding="utf-8"))
        print(f"章节 {len(d.get('chapters') or [])}｜角色 {len(d.get('characters') or [])}"
              f"｜NPC {len(d.get('npcs') or [])}｜术语页 {len(d.get('terms') or {})}")
        print("抓取时间：", d.get("fetched_at"))
        return 0

    with HuijiSession(headless=False) as s:
        if args.page:
            for prop in ({"action": "parse", "page": args.page,
                          "prop": "wikitext|displaytitle"},):
                d = s.cached_api("wikitext", prop)
                p = d.get("parse") or {}
                print("[displaytitle]", clean_title(p.get("displaytitle") or ""))
                print((p.get("wikitext") or "")[:6000])
            return 0
        if args.search:
            d = s.search(args.search, args.limit)
            for m in ((d.get("query") or {}).get("search") or []):
                print(f"  · {clean_title(m.get('title',''))}  | {re.sub('<[^>]+>','',m.get('snippet',''))[:80]}")
            return 0

        if not args.harvest:
            ap.print_help()
            return 2

        print("[1/4] 章节表 …")
        chapters = harvest_chapters(s)
        print(f"      {len(chapters)} 条")
        print("[2/4] 可征集角色 …")
        characters = harvest_characters(s)
        print(f"      {len(characters)} 条")
        print("[3/4] 其他角色一览 …")
        npcs = harvest_npcs(s)
        print(f"      {len(npcs)} 条")
        print("[4/4] 关键术语页 …")
        terms: dict[str, dict] = {}
        for t in TERM_PAGES:
            d = s.page_wikitext(t)
            wt = (d.get("parse") or {}).get("wikitext") or ""
            if not wt:
                continue
            terms[t] = {
                "displaytitle": clean_title((d.get("parse") or {}).get("displaytitle") or ""),
                "plain": strip_wiki(wt)[:4000],
                "links": links_in(wt)[:60],
                "url": f"https://res1999.huijiwiki.com/wiki/{t}",
            }
        print(f"      {len(terms)} 页")
        print("[5/5] 全站命名表（displaytitle 扫描）…")
        name_table = harvest_name_table(s)
        print(f"      {len(name_table)} 条中英对照")

        import datetime
        payload = {
            "_source": "https://res1999.huijiwiki.com/（灰机 wiki《重返未来：1999》中文维基）",
            "_note": "剧情图谱正典命名体系：中文名 ↔ 英文名 ↔ 章节。用于 plot_aliases.json 的别名桥对齐。",
            "fetched_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "chapters": chapters,
            "characters": characters,
            "npcs": npcs,
            "name_table": name_table,
            "terms": terms,
        }
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"[save] {OUT}")
        print(f"[api] 本次 API 调用 {s.calls} 次")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
