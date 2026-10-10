# -*- coding: utf-8 -*-
"""Fragments vs official corpus: proper alignment-based content-loss check.

The manifest's 133 clips are fragments of the 51 official lines. Concatenating
all clips in order should approximately reproduce the official corpus in order.
Use difflib on the two streams and report what official material is absent.
"""
import difflib
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "frontend" / "assets" / "voice" / "wu_ming_zhe" / "manifest.json"
OFFICIAL = Path(os.environ.get("TEMP", "/tmp")) / "wmz_official_lines.json"

clips = json.loads(MANIFEST.read_text(encoding="utf-8"))["clips"]
off = json.loads(OFFICIAL.read_text(encoding="utf-8"))["lines"]


def norm(s):
    if not s:
        return ""
    s = s.replace("\r", "")
    s = re.sub(r"[ \t\u00a0]+", " ", s)
    s = re.sub(r"\s*\n\s*", "\n", s)
    for a, b in [("\u201c", '"'), ("\u201d", '"'), ("\u2018", "'"), ("\u2019", "'"),
                 ("\uff0c", ","), ("\u3002", "."), ("\u2026", "..."),
                 ("\uff1a", ":"), ("\uff1f", "?"), ("\uff01", "!")]:
        s = s.replace(a, b)
    return s.strip()


def sq(s):
    return re.sub(r"\s+", "", norm(s))


# join official lines per language into one stream, recording boundaries
for lang, key in (("zh", "zh"), ("en", "en")):
    offmap = [(i, sq(l[key])) for i, l in enumerate(off) if sq(l.get(key))]
    offstream = "".join(t for _, t in offmap)
    bounds, pos = [], 0
    for i, t in offmap:
        bounds.append((pos, pos + len(t), i, off[i]["label"]))
        pos += len(t)
    # manifest stream for clips of that language, in clip order
    mclips = [(c["id"], sq((c.get("subtitle") or {}).get(key) or ""))
              for c in clips if (c.get("lang") == lang) and sq((c.get("subtitle") or {}).get(key) or "")]
    mstream = "".join(t for _, t in mclips)

    print("=" * 80)
    print("%s: official stream %d chars (%d lines) | manifest stream %d chars (%d clips)"
          % (lang.upper(), len(offstream), len(offmap), len(mstream), len(mclips)))
    sm = difflib.SequenceMatcher(None, offstream, mstream, autojunk=False)
    cov = sum(b.size for b in sm.get_matching_blocks()) / max(1, len(offstream))
    print("  official-stream coverage by manifest stream: %.1f%%" % (cov * 100))

    # attribute each unmatched official run to its official line
    lost = {}
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag in ("delete", "replace") and (i2 - i1) > 0:
            # find which official line(s) this run belongs to
            for s, e, idx, lab in bounds:
                a, b = max(i1, s), min(i2, e)
                if b > a:
                    lost.setdefault((idx, lab), []).append(offstream[a:b])
    tot = sum(sum(len(x) for x in v) for v in lost.values())
    print("  unmatched official material: %d chars across %d official lines" % (tot, len(lost)))
    print("  --- lines with the most lost material ---")
    rank = sorted(((sum(len(x) for x in v), k, v) for k, v in lost.items()), reverse=True)
    for n, (idx, lab), chunks in rank[:18]:
        print("   [%02d] %-22s lost %4d chars" % (idx, (lab or "")[:22], n))
        for ch in chunks[:2]:
            if len(ch.strip()) > 1:
                print("        %r" % ch[:150])
    if lang == "zh":
        print("  --- lines fully represented (0 lost) ---")
        ok = [k for k in [(i, off[i]["label"]) for i, _ in offmap] if k not in lost
              and any(b[2] == k[0] for b in bounds)]
        for idx, lab in ok:
            print("   [%02d] %s" % (idx, lab))
