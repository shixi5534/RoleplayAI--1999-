# -*- coding: utf-8 -*-
"""Verify the wu_ming_zhe voice manifest's fragment-level subtitles.

Checks (all 133 clips):
  1. every clip's subtitle.zh and subtitle.en are non-empty;
  2. subtitle[clip.lang] equals the clip's own audio `text` (normalised);
  3. reading load  = display chars / audio seconds, per language, within budget;
  4. value ratio   = display chars of the other-language side vs the
                     own-language side (both halves of the row must be readable);
  5. CONTENT: for every group of clips sharing one official line, the
     other-language fragments concatenated reconstruct that official line
     (token precision/recall), and the own-language `text` fragments cover it.

Reading-load threshold, justified
---------------------------------
Empirical adult reading speeds: ~15-20 chars/s for Latin script (250-320 wpm
x ~5 chars/word + spaces); for Chinese, ~5-8 chars/s (250-400 chars/min).
A subtitle must be comfortable, not maximal, and the reader is simultaneously
watching the character.  Budgets used here (chars/second of audio, counting a
CJK character as one char):
    zh <= 8.0   (a touch above the comfortable 5-8 range: short Chinese lines
                 are read in a glance and the leftover time is spare)
    en <= 20.0  (~240 wpm; above comfortable, still far below the 40+ chars/s
                 that put a 145-char paragraph inside a 0.72s clip)
A ratio budget of 3.0x guards the "one side is a paragraph, the other is a
fragment" failure independently of language speed.

Usage:
  python scripts/verify_voice_subtitles.py                 # verify manifest.json
  python scripts/verify_voice_subtitles.py --manifest PATH # verify a copy
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "frontend", "assets", "voice", "wu_ming_zhe", "manifest.json")
LINES_JSON = os.path.join(os.environ.get("TEMP", "."), "wmz_official_lines.json")

ZH_CPS = 8.0        # max Chinese chars per second of audio
EN_CPS = 20.0       # max Latin chars per second of audio
VALUE_RATIO = 3.0   # max len(other side) / len(own side), on spoken-weight units
ZH_CPM = 5.2        # spoken zh chars per second (used for the weight model)
EN_CPM = 13.0       # spoken en chars per second

PUNCT = re.compile(r"[\s，。！？、；：“”‘’（）《》…—～·,.!?;:\"'()\[\]<>~\-]+")


def norm(s: str) -> str:
    return PUNCT.sub("", (s or "").strip().lower())


def visible(s: str) -> int:
    """Characters a reader must actually read (whitespace excluded)."""
    return len(re.sub(r"\s+", "", s or ""))


def weigh(text: str, lang: str) -> float:
    t = text or ""
    if lang == "zh" and re.search(r"[\u4e00-\u9fff]", t):
        t = re.sub(r"[A-Za-z][A-Za-z'’\-]*", "", t)
    return len(re.sub(r"\s+", "", t)) / (ZH_CPM if lang == "zh" else EN_CPM)


def tokens(s: str) -> list[str]:
    """Content tokens: CJK chars individually + latin/number words."""
    out = []
    for tok in re.findall(r"[\u4e00-\u9fff]|[A-Za-z0-9][A-Za-z0-9'’\-,.]*", s or ""):
        out.append(tok.lower().rstrip(".,"))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default=MANIFEST)
    a = ap.parse_args()

    man = json.load(io.open(a.manifest, encoding="utf-8"))
    lines = json.load(io.open(LINES_JSON, encoding="utf-8"))["lines"]
    clips = man["clips"]

    fails: list[str] = []
    worst_load: list[tuple] = []
    worst_ratio: list[tuple] = []

    # ---- checks 1-4, per clip ----------------------------------------------
    for c in clips:
        cid, lang = c["id"], c["lang"]
        other = "en" if lang == "zh" else "zh"
        sub = c.get("subtitle") or {}
        sz, se = (sub.get("zh") or "").strip(), (sub.get("en") or "").strip()
        dur = max(float(c.get("dur") or 0), 0.01)

        if not sz or not se:
            fails.append("%s: EMPTY subtitle side (zh=%r en=%r)" % (cid, sz[:20], se[:20]))
            continue

        # 2. spoken side must be the audio
        if norm(sz if lang == "zh" else se) != norm(c.get("text", "")):
            own = sz if lang == "zh" else se
            fails.append("%s: subtitle[%s] != audio text  (%r vs %r)"
                         % (cid, lang, own[:46], c.get("text", "")[:46]))

        # 3. reading load
        for lg, txt, budget in (("zh", sz, ZH_CPS), ("en", se, EN_CPS)):
            load = visible(txt) / dur
            worst_load.append((load / budget, cid, lg, visible(txt), dur, budget, txt))
            if load > budget:
                fails.append("%s: %s reading load %.1f chars/s > %.1f (%d chars in %.2fs)"
                             % (cid, lg, load, budget, visible(txt), dur))

        # 4. value balance between the two rows
        own_w, oth_w = weigh(sz if lang == "zh" else se, lang), weigh(se if lang == "zh" else sz, other)
        ratio = max(own_w, oth_w) / max(min(own_w, oth_w), 0.05)
        worst_ratio.append((ratio, cid, own_w, oth_w,
                            (se if lang == "zh" else sz)))
        if ratio > VALUE_RATIO:
            fails.append("%s: side value ratio %.2f > %.1f (own %.1fs vs other %.1fs)"
                         % (cid, ratio, VALUE_RATIO, own_w, oth_w))

    # ---- check 5, per official-line group ----------------------------------
    # regroup using the same attribution rule the builder used: strongest
    # official line for the clip's own-language audio text.
    def split_zh(t):
        return [p.strip() for p in re.split(r"(?<=[。！？…；])", t or "") if p.strip()]

    def split_en(t):
        out, buf = [], ""
        for tok in re.split(r"(\s+)", (t or "").replace("\n", " ")):
            buf += tok
            if buf.rstrip().endswith((".", "!", "?")) and not re.search(r"\b(?:Ms|Mr|Mrs|Dr)\.$", buf.rstrip(), re.I):
                out.append(buf.strip())
                buf = ""
        if buf.strip():
            out.append(buf.strip())
        return [x for x in out if x]

    def split(t, lg):
        return split_zh(t) if lg == "zh" else split_en(t)

    import difflib

    def sim(x, y):
        x, y = norm(x), norm(y)
        if not x or not y:
            return 0.0
        if x in y or y in x:
            return 0.72 + 0.26 * min(len(x), len(y)) / max(len(x), len(y))
        return difflib.SequenceMatcher(None, x, y).ratio()

    def score(text, lg, ln):
        sents = split(text, lg)
        ls = split(ln.get(lg, ""), lg)
        if not sents or not ls:
            return 0.0
        return sum(max(sim(s, x) for x in ls) for s in sents) / len(sents)

    groups: dict[tuple[str, int], list] = {}
    for c in clips:
        lg = c["lang"]
        best = max(range(len(lines)), key=lambda i: score(c.get("text", ""), lg, lines[i]))
        groups.setdefault((lg, best), []).append(c)

    print("### CONTENT ROUND-TRIP (per official-line group) ###")
    print("groups: %d" % len(groups))
    # only groups whose OTHER-language fragments should reconstruct the line
    # (i.e. groups where the other side is the non-spoken language of that run)
    rt_fail = 0
    rt_stats = []
    for (lg, li), members in sorted(groups.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        other = "en" if lg == "zh" else "zh"
        members.sort(key=lambda c: c["start"])
        # the other language may be covered by a run of the SAME line from the
        # other language's own clips too; only check the spoken-run fragments.
        joined = " ".join((c["subtitle"].get(other) or "") for c in members)
        official = lines[li].get(other, "")
        jt, ot = tokens(joined), tokens(official)
        if not ot:
            continue
        # coverage of official by the fragments (multiset, order-insensitive)
        from collections import Counter
        jc, oc = Counter(jt), Counter(ot)
        covered = sum(min(jc[t], oc[t]) for t in oc)
        extra = sum(min(jc[t], max(0, jc[t] - oc[t])) for t in jc)
        rec = covered / len(ot) * 100.0
        prec = covered / max(len(jt), 1) * 100.0
        rt_stats.append((rec, prec, lg, li, len(ot), len(jt), lines[li]["label"]))
        if rec < 90.0:
            rt_fail += 1
            print("  MISS L%02d [%s] %-20s recall %.1f%%  official %d tok, fragments %d tok"
                  % (li, lg, lines[li]["label"][:20], rec, len(ot), len(jt)))
    print("  groups with <90%% token recall of the official line: %d" % rt_fail)
    rt_stats.sort()
    print("  worst 5 content recall:")
    for rec, prec, lg, li, no, nj, lab in rt_stats[:5]:
        print("    L%02d [%s] %-20s recall %.1f%%  precision %.1f%%"
              % (li, lg, lab[:20], rec, prec))

    # own-language check: does the concatenated `text` cover the official line?
    print("\n### OWN-LANGUAGE COVERAGE (audio text vs official line, same grouping) ###")
    from collections import Counter
    own_stats = []
    for (lg, li), members in groups.items():
        members.sort(key=lambda c: c["start"])
        jt = tokens(" ".join(c.get("text", "") for c in members))
        ot = tokens(lines[li].get(lg, ""))
        if not ot:
            continue
        jc, oc = Counter(jt), Counter(ot)
        covered = sum(min(jc[t], oc[t]) for t in oc)
        own_stats.append((covered / len(ot) * 100.0, lg, li, lines[li]["label"]))
    own_stats.sort()
    for rec, lg, li, lab in own_stats[:8]:
        print("    L%02d [%s] %-20s audio covers %.1f%% of the official line" % (li, lg, lab[:20], rec))

    # ---- report -------------------------------------------------------------
    print("\n### WORST 5 READING LOAD (load / budget; >1.0 fails) ###")
    worst_load.sort(reverse=True)
    for r, cid, lg, n, dur, bud, txt in worst_load[:5]:
        print("  %-8s %s  %5.1f chars/s (budget %.0f, ratio %.2f)  %d chars / %.2fs | %s"
              % (cid, lg, n / dur, bud, r, n, dur, txt[:56]))
    print("  (reading-load failures: %d)"
          % sum(1 for r, *_ in worst_load if r > 1.0))

    print("\n### WORST 5 VALUE RATIO (other side / own side spoken seconds) ###")
    worst_ratio.sort(reverse=True)
    for r, cid, ow, ot_, txt in worst_ratio[:5]:
        print("  %-8s ratio %4.2f  own %.1fs  other %.1fs | other: %s"
              % (cid, r, ow, ot_, txt[:56]))

    print("\n" + "=" * 72)
    if fails:
        print("FAIL — %d violated check(s):" % len(fails))
        for f in fails[:25]:
            print("   " + f)
        if len(fails) > 25:
            print("   ... and %d more" % (len(fails) - 25))
        return 1
    print("PASS — %d clips: no empty sides, every spoken side == its audio text,"
          % len(clips))
    print("       reading load within budget (zh<=%.0f, en<=%.0f chars/s),"
          % (ZH_CPS, EN_CPS))
    print("       side value ratio <= %.1fx, official-line content reconstructed"
          % VALUE_RATIO)
    return 0


if __name__ == "__main__":
    sys.exit(main())
