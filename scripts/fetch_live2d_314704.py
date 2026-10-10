# -*- coding: utf-8 -*-
"""Download the 314704 (Waltz of the Depths) Live2D asset set into a staging dir.

Writes to a staging directory (default: %TEMP%/l2d_314704) because subprocess
writes into the repo are sandboxed; the staged tree is then verified and placed.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import sys
import time
import urllib.error
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
BASE = "https://model.merui.net/l2d/314704/"
MODEL_ID = "314704"


def fetch(url: str, tries: int = 4) -> bytes:
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001 - report and retry
            last = e
            time.sleep(1.5 * (i + 1))
    raise RuntimeError("failed %s: %s" % (url, last))


def collect_paths(model3: dict) -> list[str]:
    fr = model3["FileReferences"]
    paths = [fr["Moc"]]
    paths += list(fr.get("Textures") or [])
    for entries in (fr.get("Motions") or {}).values():
        for e in entries:
            paths.append(e["File"])
    for e in (fr.get("Expressions") or []):
        paths.append(e["File"])
    if fr.get("Physics"):
        paths.append(fr["Physics"])
    if fr.get("Pose"):
        paths.append(fr["Pose"])
    if fr.get("DisplayInfo"):
        paths.append(fr["DisplayInfo"])
    # stable + de-duplicated
    seen, out = set(), []
    for p in paths:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def main() -> int:
    dest = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.environ.get("TEMP", "."), "l2d_314704")
    os.makedirs(dest, exist_ok=True)

    raw = fetch(BASE + "%s.model3.json" % MODEL_ID)
    model3 = json.loads(raw.decode("utf-8"))
    rel = collect_paths(model3)
    print("model3 ok; %d referenced files" % len(rel))

    manifest = []
    total = 0
    for i, r in enumerate(rel, 1):
        url = BASE + r
        data = fetch(url)
        target = os.path.join(dest, r.replace("/", os.sep))
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "wb") as fh:
            fh.write(data)
        total += len(data)
        print("  [%2d/%2d] %-44s %9d B" % (i, len(rel), r, len(data)))
        manifest.append({
            "path": r,
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        })

    # also stage the model3 itself
    with open(os.path.join(dest, "%s.model3.json" % MODEL_ID), "wb") as fh:
        fh.write(raw)
    manifest.append({
        "path": "%s.model3.json" % MODEL_ID,
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
    })

    with io.open(os.path.join(dest, "_download_manifest.json"), "w", encoding="utf-8") as fh:
        json.dump({
            "source": BASE,
            "model_id": MODEL_ID,
            "name": model3.get("Name"),
            "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "files": manifest,
            "total_bytes": total,
        }, fh, ensure_ascii=False, indent=1)

    print("\nstaged %d files, %.1f MB -> %s" % (len(manifest), total / 1048576.0, dest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
