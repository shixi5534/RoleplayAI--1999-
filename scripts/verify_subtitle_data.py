# -*- coding: utf-8 -*-
"""Independent verifier: manifest subtitle data check (Agent 1's work).

Reads frontend/assets/voice/wu_ming_zhe/manifest.json directly.
Reports: empty subtitles, subtitle-vs-text match, chars/dur ratio, length extremes,
specific clips, and content-loss vs official lines.
"""
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "frontend" / "assets" / "voice" / "wu_ming_zhe" / "manifest.json"
OFFICIAL = Path(os.environ.get("TEMP", "/tmp")) / "wmz_official_lines.json"

man = json.loads(MANIFEST.read_text(encoding="utf-8"))
clips = man["clips"] if isinstance(man, dict) else man
print("== manifest ==")
print("version:", man.get("version"), "langs:", man.get("langs"), "n_clips:", len(clips))


def norm(s):
    """Normalise for comparison: drop whitespace/newlines, unify quotes."""
    if not s:
        return ""
    s = s.replace("\n", "").replace("\r", "")
    s = re.sub(r"\s+", "", s)
    for a, b in [("\u201c", '"'), ("\u201d", '"'), ("\u2018", "'"), ("\u2019", "'"),
                 ("\u2014", "-"), ("\uff0c", ","), ("\u3002", "."), ("\u2026", "."),
                 ("\uff1a", ":"), ("\uff1f", "?"), ("\uff01", "!")]:
        s = s.replace(a, b)
    return s


# ---------- 1. empty / missing ----------
print("\n== 1. empty or missing subtitle fields ==")
bad = []
for c in clips:
    sub = c.get("subtitle") or {}
    for lang in ("zh", "en"):
        v = sub.get(lang)
        if v is None or not str(v).strip():
            bad.append((c.get("id"), lang, repr(v)))
if bad:
    for b in bad:
        print("  EMPTY:", b)
else:
    print("  none (all 133 clips have non-empty subtitle.zh and subtitle.en)")

# ---------- 2. subtitle[lang] vs clip.text ----------
print("\n== 2. does subtitle[lang] match the clip's own spoken text? ==")
# zh side is the spoken side for zh clips; en side for en clips. Check both.
exact_zh = exact_en = 0
sub_super_zh = sub_super_en = 0   # subtitle longer than text (contains extra)
sub_sub_zh = sub_sub_en = 0       # subtitle shorter (truncated)
mismatch_examples = []
for c in clips:
    sub = c.get("subtitle") or {}
    t = norm(c.get("text") or "")
    z = norm(sub.get("zh") or "")
    e = norm(sub.get("en") or "")
    if z == t:
        exact_zh += 1
    elif t and t in z:
        sub_super_zh += 1
    elif z and z in t:
        sub_sub_zh += 1
    else:
        mismatch_examples.append((c.get("id"), "zh", (c.get("text") or "")[:50], (sub.get("zh") or "")[:50]))
    # en: no spoken 'en text' field separate; compare against text only if lang en
    if c.get("lang") == "en":
        if e == t:
            exact_en += 1
        elif t and t in e:
            sub_super_en += 1
        elif e and e in t:
            sub_sub_en += 1
print(f"  zh: exact={exact_zh}  subtitle-contains-text={sub_super_zh}  "
      f"text-contains-subtitle(TRUNCATED)={sub_sub_zh}  disjoint={len(mismatch_examples)}")
print(f"  en: exact={exact_en}  subtitle-contains-text={sub_super_en}  "
      f"text-contains-subtitle(TRUNCATED)={sub_sub_en}")
print("  first 12 disjoint (id, lang, text, subtitle):")
for m in mismatch_examples[:12]:
    print("   ", m)

# ---------- 3. chars/dur ratio on the SPOKEN side ----------
print("\n== 3. displayed-text-length / dur  (chars per second) ==")
rows = []
for c in clips:
    d = float(c.get("dur") or 0)
    sub = c.get("subtitle") or {}
    # spoken side = the language the audio is in
    lang = c.get("lang") or "zh"
    shown = sub.get(lang) or ""
    n = len(norm(shown))
    rows.append((n / d if d else float("inf"), c.get("id"), lang, d, n,
                 len(norm(sub.get("zh") or "")), len(norm(sub.get("en") or ""))))
rows.sort(reverse=True)
print("  worst 15 by chars/sec on the spoken side:")
print("   ratio  id            lang  dur     spokenN  zhN   enN")
for r in rows[:15]:
    print(f"   {r[0]:6.2f} {str(r[1]):13s} {r[2]:5s} {r[3]:6.2f}  {r[4]:6d}  {r[5]:5d} {r[6]:5d}")
print("  best 5 by chars/sec:")
for r in rows[-5:]:
    print(f"   {r[0]:6.2f} {str(r[1]):13s} {r[2]:5s} {r[3]:6.2f}  {r[4]:6d}  {r[5]:5d} {r[6]:5d}")

# explicit overflow check: is displayed speech longer than audio can carry?
# 20 ch/s zh and 18 ch/s en are already very fast reading; use as sanity thresholds
THRESH = {"zh": 14.0, "en": 16.0}
over = [r for r in rows if r[0] > THRESH.get(r[2], 16.0)]
print(f"\n  clips exceeding reading threshold ({THRESH}): {len(over)}")
for r in over[:25]:
    print(f"   {r[0]:6.2f} ch/s  {r[1]}  lang={r[2]} dur={r[3]} spokenN={r[4]}")

# ---------- 4. length extremes ----------
print("\n== 4. English / Chinese text length extremes ==")
lens_en = sorted(((len(norm((c.get('subtitle') or {}).get('en') or '')), c.get('id')) for c in clips),
                 reverse=True)
lens_zh = sorted(((len(norm((c.get('subtitle') or {}).get('zh') or '')), c.get('id')) for c in clips),
                 reverse=True)
print("  EN max 5:", lens_en[:5])
print("  EN min 5:", lens_en[-5:])
print("  ZH max 5:", lens_zh[:5])
print("  ZH min 5:", lens_zh[-5:])

# ---------- 5. named clips ----------
print("\n== 5. named clips ==")
byid = {c.get("id"): c for c in clips}
for cid in ("en_16", "en_17", "en_18", "en_34", "zh_24"):
    c = byid.get(cid)
    if not c:
        print(f"  {cid}: NOT FOUND")
        continue
    sub = c.get("subtitle") or {}
    z = sub.get("zh") or ""
    e = sub.get("en") or ""
    print(f"  {cid}: lang={c.get('lang')} dur={c.get('dur')} text={ (c.get('text') or '')[:60]!r}")
    print(f"      zh len={len(z)} ratio={len(z)/float(c.get('dur') or 1):.2f} ch/s  zh={z[:160]!r}")
    print(f"      en len={len(e)} ratio={len(e)/float(c.get('dur') or 1):.2f} ch/s  en={e[:200]!r}")

# ---------- 6. duplicate subtitle blocks (fragment fan-out) ----------
print("\n== 6. how many clips share an identical subtitle block? ==")
from collections import Counter
blocks = Counter()
for c in clips:
    sub = c.get("subtitle") or {}
    blocks[(sub.get("zh") or "", sub.get("en") or "")] += 1
dups = [(n, k) for k, n in blocks.items() if n > 1]
dups.sort(reverse=True)
print(f"  distinct subtitle blocks: {len(blocks)} for {len(clips)} clips; "
      f"{len(dups)} blocks used more than once")
for n, k in dups[:12]:
    print(f"   x{n}  zh[:50]={k[0][:50]!r} en[:50]={k[1][:50]!r}")

# ---------- 7. content loss vs official lines ----------
print("\n== 7. content loss vs official lines ==")
if not OFFICIAL.exists():
    print("  official lines file missing:", OFFICIAL)
else:
    off = json.loads(OFFICIAL.read_text(encoding="utf-8"))
    print(f"  official lines: {len(off)}")
    # build the union of all manifest subtitle text per lang
    alzh = "\n".join(norm((c.get("subtitle") or {}).get("zh") or "") for c in clips)
    alen = "\n".join(norm((c.get("subtitle") or {}).get("en") or "") for c in clips)
    missing_zh, missing_en = [], []
    for ol in off:
        for lang, pool, sink in (("zh", alzh, missing_zh), ("en", alen, missing_en)):
            seg = norm(ol.get(lang) or "")
            if not seg:
                continue
            # official line split on / and ... into chunks; each chunk must appear
            chunks = [norm(x) for x in re.split(r"\s*/\s*", ol.get(lang) or "") if norm(x)]
            miss = [ch for ch in chunks if ch not in pool]
            if miss:
                sink.append((ol.get("index"), ol.get("label"), miss))
    print(f"  official ZH chunks NOT found in manifest: {len(missing_zh)}")
    for m in missing_zh[:15]:
        print(f"    [{m[0]}] {m[1]}: MISSING {len(m[2])} chunk(s)")
        for ch in m[2][:2]:
            print(f"        {ch[:110]!r}")
    print(f"  official EN chunks NOT found in manifest: {len(missing_en)}")
    for m in missing_en[:15]:
        print(f"    [{m[0]}] {m[1]}: MISSING {len(m[2])} chunk(s)")
        for ch in m[2][:2]:
            print(f"        {ch[:110]!r}")
