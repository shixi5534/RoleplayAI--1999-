# -*- coding: utf-8 -*-
"""Was the official-line coverage better at HEAD than in the working tree?

Runs the same alignment coverage on both revisions so a regression can be
told apart from a pre-existing gap.
"""
import difflib
import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OFFICIAL = Path(os.environ.get("TEMP", "/tmp")) / "wmz_official_lines.json"
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


def report(label, clips):
    out = {}
    for lang in ("zh", "en"):
        offmap = [(i, sq(l[lang])) for i, l in enumerate(off) if sq(l.get(lang))]
        offstream = "".join(t for _, t in offmap)
        bounds, pos = [], 0
        for i, t in offmap:
            bounds.append((pos, pos + len(t), i, off[i]["label"]))
            pos += len(t)
        ms = "".join(sq((c.get("subtitle") or {}).get(lang) or "")
                     for c in clips if c.get("lang") == lang)
        sm = difflib.SequenceMatcher(None, offstream, ms, autojunk=False)
        cov = sum(b.size for b in sm.get_matching_blocks()) / max(1, len(offstream))
        lost = set()
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag in ("delete", "replace") and (i2 - i1) > 0:
                for s, e, idx, lab in bounds:
                    if min(i2, e) > max(i1, s):
                        lost.add(idx)
        out[lang] = (cov, len(lost), len(offmap))
    print("%s" % label)
    for lang in ("zh", "en"):
        cov, nl, tot = out[lang]
        print("   %s coverage %.1f%%   official lines with ANY loss: %d/%d"
              % (lang.upper(), cov * 100, nl, tot))
    return out


head = json.loads(subprocess.run(
    ["git", "show", "HEAD:frontend/assets/voice/wu_ming_zhe/manifest.json"],
    cwd=ROOT, capture_output=True, check=True).stdout.decode("utf-8"))["clips"]
work = json.loads((ROOT / "frontend/assets/voice/wu_ming_zhe/manifest.json")
                  .read_text(encoding="utf-8"))["clips"]

a = report("== HEAD (before agents) ==", head)
b = report("\n== WORKING TREE (after agents) ==", work)
print("\n== DELTA ==")
for lang in ("zh", "en"):
    d = (b[lang][0] - a[lang][0]) * 100
    print("   %s coverage %+.1f pp ; lines-with-loss %d -> %d"
          % (lang.upper(), d, a[lang][1], b[lang][1]))
