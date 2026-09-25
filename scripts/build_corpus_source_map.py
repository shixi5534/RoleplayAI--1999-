# -*- coding: utf-8 -*-
"""T15 修复件生成：语料来源映射 + 元数据/语言标注修正提案（**只读语料，产提案不落地**）。

依据（今日实测）：
  · 来源构成：英配视频 654doc/8069块（89.5%）、灰机正典 112doc/663块（7.3%）、
    中配视频 63doc/224块（2.5%）、UP 解说 5doc/58块、其他 4doc/7块；
  · lang 标注与实际不一致：标题写"中配"却标 en（BV1At4y1R7Mr_p24「英配」段合理，
    但同类"中英配"段落标注前后不一）；
  · version/arc 缺失：version 缺 120 doc（其中灰机 86、缺德的德鲁伊 25、解说 9）、
    arc 缺 109 doc。

产出（均为提案，不改动原语料）：
  · data/knowledge/_audit/corpus_source_map_20260917.json
      每 doc：source 类别 / 块数 / 标注 lang / 实际主导语言 / 建议 lang / 建议 arc / version
  · 控制台摘要：各类需修正的 doc 数
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(r"C:\Users\Lenovo\WorkBuddy\2026-07-27-16-45-03\roleplay-ai")
OUT = ROOT / "data" / "knowledge" / "_audit" / "corpus_source_map_20260917.json"
L: list[str] = []


def log(m: str = "") -> None:
    L.append(str(m))


CJK = re.compile(r"[\u4e00-\u9fff]")
ZH_DUB = re.compile(r"中配|国配|中文配音|普通话")
EN_DUB = re.compile(r"英配|英文配音|4K英配")
COMMENTARY = re.compile(r"解析|解说|串联|看懂|带我|带你|重讲|万字|保姆级")


def guess_lang(t: str) -> str:
    if not t:
        return "unknown"
    return "zh" if len(CJK.findall(t)) / len(t) > 0.2 else "en"


def arc_from_title(title: str) -> str:
    """从标题里抽取篇章名：《重返未来：1999》1.6版本「朔日手记」… → 朔日手记"""
    m = re.search(r"[「【]([^」】]{2,12})[」】]", title or "")
    return m.group(1) if m else ""


def version_from_title(title: str) -> str:
    m = re.search(r"(\d\.\d)\s*版本", title or "")
    return m.group(1) if m else ""


data = json.loads((ROOT / "data/knowledge/plot_corpus_wu_ming_zhe.json").read_text(encoding="utf-8"))
docs = data.get("docs") or {}
chunks = data.get("chunks") or []
blocks: Counter = Counter()
lang_of_blocks: dict[str, Counter] = defaultdict(Counter)
for c in chunks:
    d = str(c.get("doc_id") or "")
    blocks[d] += 1
    lang_of_blocks[d][guess_lang(str(c.get("text") or ""))] += 1

entries: list[dict] = []
need_lang = need_arc = need_ver = 0
for d, m in docs.items():
    up = str(m.get("uploader") or "")
    ti = str(m.get("title") or "")
    if "灰机" in up:
        src = "huiji_canon"
    elif ZH_DUB.search(ti):
        src = "video_zh_dub"
    elif "缺德的德鲁伊" in up or EN_DUB.search(ti):
        src = "video_en_dub"
    elif COMMENTARY.search(ti):
        src = "commentary_video"
    else:
        src = "other_video"
    dom = (lang_of_blocks[d].most_common(1) or [("unknown", 0)])[0][0]
    declared = str(m.get("lang") or "")
    sug_lang = dom if dom in ("zh", "en") else declared
    sug_arc = str(m.get("arc") or "") or arc_from_title(ti)
    sug_ver = str(m.get("version") or "") or version_from_title(ti)
    fix_lang = bool(declared and sug_lang and declared != sug_lang)
    fix_arc = not str(m.get("arc") or "") and bool(sug_arc)
    fix_ver = not str(m.get("version") or "") and bool(sug_ver)
    need_lang += int(fix_lang)
    need_arc += int(fix_arc)
    need_ver += int(fix_ver)
    entries.append({
        "doc_id": d, "source": src, "blocks": blocks[d],
        "uploader": up, "title": ti[:110],
        "lang_declared": declared, "lang_actual": dict(lang_of_blocks[d]),
        "lang_suggest": sug_lang, "needs_lang_fix": fix_lang,
        "arc": str(m.get("arc") or ""), "arc_suggest": sug_arc, "needs_arc_fix": fix_arc,
        "version": str(m.get("version") or ""), "version_suggest": sug_ver,
        "needs_version_fix": fix_ver,
    })

log(f"docs {len(entries)}")
log(f"需修正 lang：{need_lang}｜arc：{need_arc}｜version：{need_ver}")
log(f"其中 arc 可由标题自动补全的：{sum(1 for e in entries if e['needs_arc_fix'])}")
log(f"     version 可由标题自动补全的：{sum(1 for e in entries if e['needs_version_fix'])}")
log(f"\n按来源统计需修正：")
by_src: dict[str, Counter] = defaultdict(Counter)
for e in entries:
    by_src[e["source"]]["docs"] += 1
    by_src[e["source"]]["lang_fix"] += int(e["needs_lang_fix"])
    by_src[e["source"]]["arc_fix"] += int(e["needs_arc_fix"])
    by_src[e["source"]]["ver_fix"] += int(e["needs_version_fix"])
    by_src[e["source"]]["blocks"] += e["blocks"]
for s, c in sorted(by_src.items(), key=lambda kv: -kv[1]["blocks"]):
    log(f"  {s:<18} docs={c['docs']:>4}｜blocks={c['blocks']:>5}｜"
        f"lang_fix={c['lang_fix']:>3}｜arc_fix={c['arc_fix']:>3}｜ver_fix={c['ver_fix']:>3}")

log("\n【需要 lang 修正的 doc（前 15）】")
k = 0
for e in entries:
    if e["needs_lang_fix"]:
        log(f"  {e['doc_id']}｜标注 {e['lang_declared']} → 实际 {dict(e['lang_actual'])}｜"
            f"建议 {e['lang_suggest']}｜{e['title'][:70]}")
        k += 1
        if k >= 15:
            break

log("\n【arc 可由标题补全的 doc（前 10）】")
k = 0
for e in entries:
    if e["needs_arc_fix"]:
        log(f"  {e['doc_id']}｜建议 arc={e['arc_suggest']}｜v={e['version_suggest']}｜{e['title'][:70]}")
        k += 1
        if k >= 10:
            break

OUT.write_text(json.dumps({
    "generated_at": __import__("time").strftime("%Y-%m-%d %H:%M:%S"),
    "summary": {"docs": len(entries), "need_lang_fix": need_lang,
                "need_arc_fix": need_arc, "need_version_fix": need_ver,
                "by_source": {s: dict(c) for s, c in by_src.items()}},
    "entries": entries,
}, ensure_ascii=False, indent=1), encoding="utf-8")
log(f"\n[out] {OUT}")
Path(r"C:\Users\Lenovo\WorkBuddy\2026-09-17-13-00-26\_meta_fix.txt").write_text(
    "\n".join(L), encoding="utf-8")
print("ok")
