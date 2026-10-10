# -*- coding: utf-8 -*-
"""Extract official Ms. Stranger voice lines (zh/en) from UTTU into a JSON corpus.

IMPORTANT: parse the RAW html (before entity-unescaping) — the attribute values
themselves contain straight quotes once unescaped, which would truncate a naive
`data-en="([^"]*)"` match. Unescape each captured value only afterwards.
"""
from __future__ import annotations

import html as htmlmod
import io
import json
import os
import re
import sys
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
OUT = os.path.join(os.environ.get("TEMP", "."), "wmz_official_lines.json")
PROFILE = "https://uttu.merui.net/profiles/ms._stranger"

# data-en="..."  |  data-en='...'  |  data-en=bare-token
ATTR_RE = re.compile(r"data-(en|zh|tw|jp|kr)=(?:\"([^\"]*)\"|'([^']*)'|([^\s>]+))", re.S)
TAG_START_RE = re.compile(r'class="[^"]*voice-line-text[^"]*"')


def tag_bounds(html: str, pos: int) -> tuple[int, int]:
    """Return (start, end) of the element tag containing position `pos`.

    A naive `<div[^>]*>` scan breaks because attribute VALUES here contain raw
    '>' characters (from nested <mark ...> markup), so walk the tag
    quote-aware: inside "..." or '...' a '>' does not terminate the tag.
    """
    start = html.rfind("<", 0, pos)
    i = start
    quote = None
    while i < len(html):
        ch = html[i]
        if quote:
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
        elif ch == ">":
            return start, i + 1
        i += 1
    return start, len(html)


def get(u: str) -> str:
    req = urllib.request.Request(u, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", "replace")


def clean(s: str) -> str:
    if not s:
        return ""
    s = htmlmod.unescape(s)
    s = re.sub(r"<br\s*/?>", "\n", s)
    s = re.sub(r"</?mark[^>]*>", "", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = htmlmod.unescape(s)
    s = re.sub(r"[ \t\u00a0]+", " ", s)
    s = "\n".join(ln.strip() for ln in s.split("\n") if ln.strip())
    return s.strip()


def main() -> int:
    raw = get(PROFILE)  # NOTE: raw, not unescaped
    blocks = list(TAG_START_RE.finditer(raw))
    rows = []
    for i, m in enumerate(blocks):
        tstart, tend = tag_bounds(raw, m.start())
        attrs = raw[tstart:tend]
        vals = {}
        for am in ATTR_RE.finditer(attrs):
            key = am.group(1)
            val = am.group(2) if am.group(2) is not None else (
                am.group(3) if am.group(3) is not None else am.group(4))
            vals.setdefault(key, val)
        # section label sits just before the block
        pre = raw[max(0, tstart - 900):tstart]
        labs = re.findall(r">([^<>]{2,60})<br>", pre)
        rec = {
            "index": i,
            "label": clean(labs[-1]) if labs else "",
            "en": clean(vals.get("en", "")),
            "zh": clean(vals.get("zh", "")),
            "tw": clean(vals.get("tw", "")),
            "jp": clean(vals.get("jp", "")),
            "kr": clean(vals.get("kr", "")),
        }
        rows.append(rec)

    with io.open(OUT, "w", encoding="utf-8") as fh:
        json.dump({"source": PROFILE, "count": len(rows), "lines": rows}, fh,
                  ensure_ascii=False, indent=1)

    miss_zh = [r["index"] for r in rows if not r["zh"]]
    miss_en = [r["index"] for r in rows if not r["en"]]
    print("extracted %d lines -> %s" % (len(rows), OUT))
    print("missing zh: %s" % miss_zh)
    print("missing en: %s" % miss_en)
    for r in rows:
        print("[%02d] %-22s | ZH %s" % (r["index"], r["label"][:22],
                                        r["zh"][:46].replace("\n", " / ")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
