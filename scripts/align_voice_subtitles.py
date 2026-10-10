# -*- coding: utf-8 -*-
"""Reconcile the local voice manifest's bilingual subtitles with the official
UTTU Ms. Stranger line corpus.

THE DEFECT
----------
Each mp3 is a sentence-level fragment of an official voice line. The manifest's
contract is: the clip's own-language subtitle equals its audio text, and the
OTHER language's subtitle equals the full official line that fragment belongs to
(proved by the shipped data: en_16/en_17/en_18 all carry line 04's full Chinese
while their English is the individual fragment).

What was wrong is WHICH official line the other side was taken from: it had been
filled *positionally* rather than by content, so the pair drifted. On screen
(clicking the Live2D) that showed Chinese that did not correspond to the English
(or was empty):

  en_14  audio is the Idle line's 2nd sentence, but its zh was line 02's Chinese
         concatenated with line 03's Chinese;
  zh_21  its en was empty -> a blank second subtitle row;
  zh_02  its en was line 02's text although the audio is line 01's 4th sentence.

ALGORITHM
---------
1. Two independent witnesses per clip: its own-language audio text, and its
   existing cross-language subtitle text. Each is scored against every official
   line (mean of per-sentence best matches).
2. Clips whose OWN-language witness is strong (>= ANCHOR_SCORE) are pinned to that
   official line. These anchors cannot be moved, so a garbled whisper transcript
   elsewhere cannot drag a correct neighbour along with it.
3. Every run of clips between two anchors is resolved by a monotonic dynamic
   program (official-line index may only move forward, paying JUMP_PENALTY per
   step) over the boundary-constrained line range, using best-of-both-witness
   scores. Monotonicity mirrors the audio timeline: fragments of one line are
   contiguous.
4. The cross-language subtitle is set to the chosen line's official text; the
   clip's own-language subtitle stays audio-exact. Clips whose best evidence is
   below MIN_EVIDENCE keep their previous subtitle and are reported.

Usage:
  python scripts/align_voice_subtitles.py             # dry run + diff report
  python scripts/align_voice_subtitles.py --apply     # write manifest.json
"""
from __future__ import annotations

import argparse
import difflib
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "frontend", "assets", "voice", "wu_ming_zhe", "manifest.json")
LINES_JSON = os.path.join(os.environ.get("TEMP", "."), "wmz_official_lines.json")
SOURCE = "https://uttu.merui.net/profiles/ms._stranger"

ANCHOR_SCORE = 0.80    # own-language witness this strong pins the official line
MIN_EVIDENCE = 0.45    # below this nothing is trusted -> leave the clip alone
JUMP_PENALTY = 0.03    # cost per official-line index step inside a DP run

PUNCT = re.compile(r"[\s，。！？、；：“”‘’（）《》…—～·,.!?;:\"'()\[\]<>~\-]+")
ABBREV = re.compile(r"\b(?:Ms|Mr|Mrs|Dr|vs|etc|Jr|Sr)\.$", re.I)


def norm(s: str) -> str:
    return PUNCT.sub("", (s or "").strip().lower())


def sim(a: str, b: str) -> float:
    a, b = norm(a), norm(b)
    if not a or not b:
        return 0.0
    if a in b or b in a:
        return 0.72 + 0.26 * (min(len(a), len(b)) / max(len(a), len(b)))
    return difflib.SequenceMatcher(None, a, b).ratio()


def split_zh(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"(?<=[。！？…；])", text or "") if p.strip()]


def split_en(text: str) -> list[str]:
    out, buf = [], ""
    for tok in re.split(r"(\s+)", (text or "").replace("\n", " ")):
        buf += tok
        s = buf.rstrip()
        if s.endswith((".", "!", "?")):
            if s.endswith(".") and ABBREV.search(s):
                continue
            out.append(s)
            buf = ""
    if buf.strip():
        out.append(buf.strip())
    return [x for x in (t.strip() for t in out) if x]


def split(text: str, lang: str) -> list[str]:
    return split_zh(text) if lang == "zh" else split_en(text)


def build_pool(lines: list[dict]) -> dict[str, list[list[str]]]:
    return {lg: [split(ln.get(lg, ""), lg) for ln in lines] for lg in ("zh", "en")}


def score_all(text: str, lang: str, pool) -> list[float]:
    """score[line_index] for `text` against every official line."""
    sents = split(text, lang)
    if not sents:
        return [0.0] * len(pool[lang])
    out = []
    for line_sents in pool[lang]:
        if not line_sents:
            out.append(0.0)
            continue
        out.append(sum(max(sim(s, ls) for ls in line_sents) for s in sents) / len(sents))
    return out


def dp_range(scores: list[list[float]], lo: int, hi: int) -> list[int]:
    """Monotonic assignment over line indices [lo, hi] maximising total score."""
    n = len(scores)
    if not n:
        return []
    width = hi - lo + 1
    NEG = -1e9
    prev = [scores[0][lo + k] for k in range(width)]
    back = []
    for i in range(1, n):
        cur = [NEG] * width
        bk = [-1] * width
        best_val, best_idx = NEG, -1
        for k in range(width):
            if best_idx >= 0:
                best_val -= JUMP_PENALTY
            cand = prev[k]
            if cand >= best_val:
                best_val, best_idx = cand, k
            cur[k] = best_val + scores[i][lo + k]
            bk[k] = best_idx
        back.append(bk)
        prev = cur
    last = max(range(width), key=lambda k: prev[k])
    path = [0] * n
    path[n - 1] = lo + last
    for i in range(n - 1, 0, -1):
        last = back[i - 1][last]
        path[i - 1] = lo + last
    return path


def resolve(scores_list: list[list[float]], anchors: list[tuple[int, int]]) -> list[int]:
    """Assignment honouring `anchors` (clip_index -> line_index)."""
    n = len(scores_list)
    m = len(scores_list[0]) if n else 0
    out = [None] * n
    for ci, li in anchors:
        out[ci] = li
    apos = sorted(anchors)

    def solve(start: int, end: int, lo: int, hi: int):
        """Fill clips (start..end) exclusive-bounded by lines [lo, hi]."""
        if start > end:
            return
        lo = max(0, lo)
        hi = min(m - 1, hi)
        if lo > hi:
            lo = hi = max(0, min(m - 1, lo))
        seg = scores_list[start:end + 1]
        path = dp_range(seg, lo, hi)
        for k, li in enumerate(path):
            out[start + k] = li

    if not apos:
        solve(0, n - 1, 0, m - 1)
        return out

    # before the first anchor
    first_ci, first_li = apos[0]
    solve(0, first_ci - 1, 0, first_li)
    # between consecutive anchors
    for (c1, l1), (c2, l2) in zip(apos, apos[1:]):
        solve(c1 + 1, c2 - 1, l1, l2)
    # after the last anchor
    last_ci, last_li = apos[-1]
    solve(last_ci + 1, n - 1, last_li, m - 1)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--report", action="store_true", help="print the full assignment table")
    ap.add_argument("--out", default=MANIFEST, help="target manifest path")
    a = ap.parse_args()

    man = json.load(io.open(MANIFEST, encoding="utf-8"))
    lines = json.load(io.open(LINES_JSON, encoding="utf-8"))["lines"]
    pool = build_pool(lines)
    print("official corpus: %d lines" % len(lines))

    plans = []
    for lang in ("zh", "en"):
        run = [c for c in man["clips"] if c["lang"] == lang]
        other = "en" if lang == "zh" else "zh"
        own_scores, oth_scores = [], []
        for c in run:
            own_scores.append(score_all(c.get("text", ""), lang, pool))
            oth_scores.append(score_all((c.get("subtitle") or {}).get(other, ""), other, pool))
        combined = [[max(o, t) for o, t in zip(so, st)] for so, st in zip(own_scores, oth_scores)]
        anchors = []
        for i, sc in enumerate(own_scores):
            j = max(range(len(sc)), key=lambda k: sc[k])
            if sc[j] >= ANCHOR_SCORE:
                anchors.append((i, j))
        assign = resolve(combined, anchors)
        print("%s run: %d clips, %d anchors pinned" % (lang, len(run), len(anchors)))
        for i, c in enumerate(run):
            li = assign[i]
            best = combined[i][li]
            plans.append((c, li, best, own_scores[i][li], oth_scores[i][li], i in [x[0] for x in anchors]))

    if a.report:
        print("\n### assignment ###")
        for c, li, best, so, st, anch in plans:
            print("  %-8s %-3s L%02d %-22s %6.3f %s | %s"
                  % (c["id"], c["lang"], li, lines[li]["label"][:22], best,
                     "ANCHOR" if anch else "      ", lines[li]["zh"][:40].replace("\n", " / ")))

    changed = 0
    low = []
    for c, li, best, so, st, anch in plans:
        if li < 0 or best < MIN_EVIDENCE:
            low.append((c, best))
            continue
        other = "en" if c["lang"] == "zh" else "zh"
        new_sub = {"zh": "", "en": ""}
        new_sub[c["lang"]] = c.get("text", "")
        new_sub[other] = lines[li][other]
        c["_new"] = new_sub
        if (c.get("subtitle") or {}) != new_sub:
            changed += 1

    print("\n### %d clips to rewrite, %d untouched, %d low-confidence ###"
          % (changed, len(plans) - changed - len(low), len(low)))
    for c, best in low:
        print("   LOW %-8s %s %.3f  %s" % (c["id"], c["lang"], best, c.get("text", "")[:50]))

    print("\n### diff sample (first 25 changes) ###")
    shown = 0
    for c, li, best, so, st, anch in plans:
        new_sub = c.get("_new")
        if not new_sub:
            continue
        old = c.get("subtitle") or {}
        if old == new_sub or shown >= 25:
            continue
        shown += 1
        other = "en" if c["lang"] == "zh" else "zh"
        print("-" * 88)
        print("%s [%s] -> L%02d %s (%.3f, audio %.3f/prev %.3f)%s"
              % (c["id"], c["lang"], li, lines[li]["label"], best, so, st,
                 " [ANCHOR]" if anch else ""))
        print("   audio: %s" % c.get("text", "")[:95])
        print("   %s OLD: %s" % (other.upper(), (old.get(other) or "<empty>").replace("\n", " / ")[:95]))
        print("   %s NEW: %s" % (other.upper(), new_sub[other].replace("\n", " / ")[:95]))

    if not a.apply:
        for c in man["clips"]:
            c.pop("_new", None)
        print("\n(dry run - pass --apply to write)")
        return 0

    for c in man["clips"]:
        ns = c.pop("_new", None)
        if ns:
            c["subtitle"] = ns
    man["version"] = int(man.get("version", 0)) + 1
    man["align_source"] = SOURCE + " (official zh/en voice lines)"
    man["align_method"] = (
        "per-clip official line resolved from TWO witnesses (own-language audio text "
        "and the existing cross-language subtitle), pinned at strong matches and "
        "interpolated monotonically between them; own-language subtitle stays "
        "audio-exact, the other side takes the official full line"
    )
    with io.open(a.out, "w", encoding="utf-8") as fh:
        json.dump(man, fh, ensure_ascii=False, indent=1)
    print("\napplied: %d rewritten, version -> %s -> %s" % (changed, man["version"], a.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
