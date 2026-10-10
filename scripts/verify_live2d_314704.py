# -*- coding: utf-8 -*-
"""Verify the staged 314704 asset set: JSON validity, moc3 magic, referenced files, params."""
from __future__ import annotations

import io
import json
import os
import re
import struct
import sys

STAGE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.environ.get("TEMP", "."), "l2d_314704")

print("staging:", STAGE)
model3_path = os.path.join(STAGE, "314704.model3.json")
raw = io.open(model3_path, "rb").read()
m3 = json.loads(raw.decode("utf-8"))
fr = m3["FileReferences"]
print("model3 OK  Name=%s" % m3.get("Name"))

# 1. every referenced file present + JSON files parse
missing, bad = [], []
refs = [fr["Moc"]] + list(fr.get("Textures") or [])
for v in (fr.get("Motions") or {}).values():
    for e in v:
        refs.append(e["File"])
for e in (fr.get("Expressions") or []):
    refs.append(e["File"])
for r in refs:
    p = os.path.join(STAGE, r.replace("/", os.sep))
    if not os.path.isfile(p):
        missing.append(r)
        continue
    if r.endswith(".json"):
        try:
            json.loads(io.open(p, encoding="utf-8").read())
        except Exception as e:  # noqa: BLE001
            bad.append((r, str(e)))
print("refs=%d missing=%d bad_json=%d" % (len(refs), len(missing), len(bad)))
for m in missing:
    print("   MISSING", m)
for b in bad:
    print("   BADJSON", b)

# 2. moc3 magic
moc = io.open(os.path.join(STAGE, fr["Moc"]), "rb").read()
print("moc3 magic=%r  bytes=%d" % (moc[:4], len(moc)))

# 3. parameter ids present in the moc3 (Cubism stores them as a name table)
text = moc.decode("latin-1")
ids = sorted(set(re.findall(r"Param[A-Za-z0-9_]{2,40}", text)))
print("param ids in moc3: %d" % len(ids))
interesting = [i for i in ids if re.search(r"Eye|Mouth|Brow|Angle|Body|Breath|Hair", i)]
for i in interesting:
    print("   ", i)

# 4. expression contents
print("\nexpressions:")
for e in (fr.get("Expressions") or []):
    js = json.loads(io.open(os.path.join(STAGE, e["File"].replace("/", os.sep)),
                            encoding="utf-8").read())
    ps = [p.get("Id") for p in (js.get("Parameters") or [])]
    print("   %-12s %s" % (e["Name"], ps[:6]))

print("\nGroups:", json.dumps(m3.get("Groups"), ensure_ascii=False))
