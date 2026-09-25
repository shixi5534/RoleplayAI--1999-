# -*- coding: utf-8 -*-
"""灰机 wiki 官方中文剧情原文 → 正典语料层（``canon_zh``）。

为什么做这一层（分诊结论驱动）
    300 题分诊实测：188 个缺失证据组里 **147 个是「别名桥缺失」**——
    答案实体在图里（英文 ASR 正名），但用户提问是中文且不点名称呼它
    （「洞穴的囚徒篇里海盗船上的歌手是谁？」）。B 站语料是**英文 ASR**，
    图谱 fingerprint 的 embedder 是 ``none``，没有跨语料兜底 ⇒ 这类问题必错。
    灰机 wiki 的 ``小径/<篇名>`` 就是**官方中文剧情原文**（实测 116 页 / 约 30 万字），
    中文查询能直接与中文正文词法匹配，正文里也写明了实体名。

产出（每块都可溯源，头部带灰机 URL）
    ``data/lore/wu_ming_zhe/canon_zh/<篇名>.md``
    → 由 ``PlotCorpus.build()`` 以 ``source_kind="canon_zh"`` 收进剧情语料。

用法：
    .venv/Scripts/python.exe -X utf8 scripts/huiji_canon_corpus.py --fetch        # 抓取 + 落 md
    .venv/Scripts/python.exe -X utf8 scripts/huiji_canon_corpus.py --fetch --limit 5
    .venv/Scripts/python.exe -X utf8 scripts/huiji_canon_corpus.py --status
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from huiji_fetch import HuijiSession  # noqa: E402

CANON = ROOT / "data" / "lore" / "wu_ming_zhe" / "huiji_canon.json"
OUTDIR = ROOT / "data" / "lore" / "wu_ming_zhe" / "canon_zh"
PREFIX = "小径/"

_TAG = re.compile(r"<[^>]+>")
_SCRIPT = re.compile(r"<(script|style)\b.*?</\1>", re.S | re.I)
_BR = re.compile(r"<br\s*/?>|</p>|</div>|</li>|</h[1-6]>", re.I)
_MULTI_NL = re.compile(r"\n{3,}")


def html_to_text(html: str) -> str:
    """灰机渲染 HTML → 纯文本（保留换行结构；转义实体还原）。"""
    html = _SCRIPT.sub("", html or "")
    html = _BR.sub("\n", html)
    html = _TAG.sub("", html)
    for k, v in (("&nbsp;", " "), ("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"),
                 ("&quot;", '"'), ("&#39;", "'"), ("&ldquo;", "“"), ("&rdquo;", "”"),
                 ("&hellip;", "…"), ("&mdash;", "—")):
        html = html.replace(k, v)
    # 灰机正文里大量使用 &#160;（不换行空格）——不解码会变成噪声字符
    html = re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))), html)
    html = re.sub(r"&#[xX]([0-9a-fA-F]+);", lambda m: chr(int(m.group(1), 16)), html)
    html = html.replace("\u00a0", " ")
    lines = [ln.strip() for ln in html.splitlines()]
    return _MULTI_NL.sub("\n\n", "\n".join(ln for ln in lines if ln))


# 段末标点：有它的一行一定不是导航项
_SENT_END = ("。", "！", "？", "…", "；", "”", '"', "」", "』")


def _is_nav_line(line: str) -> bool:
    """导航/目录行判定：短、且不像一句剧情正文。

    注意**不能**用「含逗号就不算导航」这类规则——篇名本身带标点
    （「再见，来亚什基」「飞驰！明日之城」「重燃！流金之海」），
    实测那样判会在第 4 行就停下，导航只剥掉一半。
    可靠判据只有一个：**段末句读标点**。正文句子几乎总以 。！？…；” 收尾，
    导航项则停在名字上。
    """
    s = line.strip()
    if not s:
        return True
    if s in {"目录", "导航", "展开", "折叠", "上一篇", "下一篇"}:
        return True
    if len(s) > 20:
        return False
    return not s.endswith(_SENT_END)


def strip_nav(text: str, arc_names: list[str]) -> str:
    """剥掉灰机小径页顶部的「全部篇名导航 + 目录」块。

    为什么必须剥：每张页开头都把 40 多个篇名列一遍，会让**每个篇名在所有页面里
    都命中一次**，把词法检索彻底稀释掉。实测该块长度 25–45 行。
    判定用「短行且不像正文」的连续前导块；不足 8 行则不认为是导航（防误剥）。
    """
    lines = text.split("\n")
    i = 0
    while i < len(lines) and _is_nav_line(lines[i]):
        i += 1
    if i < 8:
        i = 0
    tail = lines[i:]
    j = len(tail)
    while j > 0 and _is_nav_line(tail[j - 1]):
        j -= 1
    if len(tail) - j < 8:
        j = len(tail)
    return "\n".join(tail[:j]).strip()


def main() -> int:
    ap = argparse.ArgumentParser(description="灰机正典中文剧情语料构建")
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--status", action="store_true")
    args = ap.parse_args()

    if args.status:
        files = sorted(OUTDIR.glob("*.md")) if OUTDIR.is_dir() else []
        total = 0
        for f in files:
            raw = f.read_text(encoding="utf-8")
            total += len(re.findall(r"[\u4e00-\u9fff]", raw))
        print(f"[canon_zh] {len(files)} 篇｜汉字合计 {total}｜目录 {OUTDIR}")
        return 0

    if not args.fetch:
        ap.print_help()
        return 2

    canon = json.loads(CANON.read_text(encoding="utf-8")) if CANON.is_file() else {}
    arc_names = [c["zh"] for c in (canon.get("chapters") or []) if c.get("zh")]
    versions = {}
    for c in canon.get("chapters") or []:
        if c.get("version") and c.get("zh"):
            versions.setdefault(c["zh"].strip("《》"), c["version"])

    OUTDIR.mkdir(parents=True, exist_ok=True)
    written = 0
    report = []
    with HuijiSession(headless=False) as s:
        d = s.cached_api("allpages:小径", {"action": "query", "list": "allpages",
                                           "apprefix": PREFIX, "aplimit": "500"})
        pages = [p.get("title") for p in ((d.get("query") or {}).get("allpages") or [])]
        pages = [p for p in pages if p and "/" in p]
        if args.limit:
            pages = pages[: args.limit]
        print(f"[fetch] 小径页 {len(pages)} 个")

        import datetime
        today = datetime.date.today().isoformat()
        for title in pages:
            arc = title.split("/", 1)[1]
            r = s.cached_api("render", {"action": "parse", "page": title, "prop": "text"})
            html = ((r.get("parse") or {}).get("text")) or ""
            text = strip_nav(html_to_text(html), arc_names + [arc])
            cjk = len(re.findall(r"[\u4e00-\u9fff]", text))
            if cjk < 120:
                report.append({"page": title, "cjk": cjk, "skipped": True})
                continue
            ver = versions.get(arc.strip("《》"), "")
            url = f"https://res1999.huijiwiki.com/wiki/{title}"
            head = [f"# {arc}"]
            if ver:
                head.append(f"版本：{ver}")
            head.append(f"来源：{url}")
            head.append(f"抓取：{today}")
            head.append("提取方式：灰机wiki 渲染文本（canon_zh）")
            body = "\n".join(head) + "\n\n---\n\n" + text + "\n"
            safe = re.sub(r"[^\w\u4e00-\u9fff]+", "_", arc).strip("_") or "page"
            (OUTDIR / f"{safe}.md").write_text(body, encoding="utf-8")
            written += 1
            report.append({"page": title, "arc": arc, "version": ver, "cjk": cjk,
                           "chars": len(text), "file": f"{safe}.md"})

    kept = [r for r in report if not r.get("skipped")]
    total_cjk = sum(r["cjk"] for r in kept)
    print(f"[done] 落盘 {written} 篇｜汉字合计 {total_cjk}")
    skipped = [r["page"] for r in report if r.get("skipped")]
    if skipped:
        print(f"[skip] {len(skipped)} 页正文过短：{skipped[:10]}")
    (ROOT / "data" / "knowledge" / "_audit" / "canon_zh_report.json").write_text(
        json.dumps({"pages": len(pages), "written": written, "cjk": total_cjk,
                    "rows": report}, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
