# -*- coding: utf-8 -*-
"""Analyse a rendered PNG: size, content bbox, and whether it looks like a full character.

Used to verify the 314704 framing without an image-capable model: reports the
aspect ratio and the vertical distribution of opaque pixels, so a "only the lower
body is visible" crop can be told apart from a full-body render.
"""
from __future__ import annotations

import io
import sys
from PIL import Image


def main() -> int:
    p = sys.argv[1]
    im = Image.open(p).convert("RGBA")
    w, h = im.size
    px = im.load()
    minx, miny, maxx, maxy = w, h, -1, -1
    n = 0
    rows = [0] * h
    for y in range(h):
        for x in range(w):
            if px[x, y][3] > 10:
                n += 1
                rows[y] += 1
                if x < minx: minx = x
                if x > maxx: maxx = x
                if y < miny: miny = y
                if y > maxy: maxy = y
    print("file:", p)
    print("canvas: %dx%d" % (w, h))
    print("opaque px: %d (%.1f%% of canvas)" % (n, 100.0 * n / (w * h)))
    if maxx < 0:
        print("EMPTY IMAGE")
        return 1
    print("content bbox: x %d..%d  y %d..%d  (w=%d h=%d)"
          % (minx, maxx, miny, maxy, maxx - minx + 1, maxy - miny + 1))
    print("content aspect (w/h): %.3f" % ((maxx - minx + 1) / (maxy - miny + 1)))

    # vertical profile in 10 bands
    print("\nvertical opaque-pixel profile (top -> bottom, 10 bands):")
    band = max(1, (maxy - miny + 1) // 10)
    for b in range(10):
        y0 = miny + b * band
        y1 = min(y0 + band, maxy + 1)
        cnt = sum(rows[y0:y1])
        bar = "#" * int(60 * cnt / max(1, max(rows)))
        print("  band %2d y%4d-%4d %8d %s" % (b, y0, y1 - 1, cnt, bar))

    # widest band = shoulders/body; face is near the top
    top_third = sum(rows[miny:miny + (maxy - miny + 1) // 3])
    mid_third = sum(rows[miny + (maxy - miny + 1) // 3:miny + 2 * (maxy - miny + 1) // 3])
    bot_third = sum(rows[miny + 2 * (maxy - miny + 1) // 3:maxy + 1])
    print("\nthirds (top/mid/bottom): %d / %d / %d" % (top_third, mid_third, bot_third))
    return 0


if __name__ == "__main__":
    sys.exit(main())
