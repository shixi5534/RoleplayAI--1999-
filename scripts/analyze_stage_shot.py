# -*- coding: utf-8 -*-
"""分析舞台截图：不透明内容占比、包围盒、以及各行/各列的覆盖分布。

用途：肉眼看不到图时，用数字判断"角色是否被切、是否偏"。
关键判据：
  - 包围盒是否贴到画布边缘（贴边=被裁切）；
  - 顶部若干行是否有内容（有内容且很宽 = 头被切平的痕迹）；
  - 左/右是否贴边。
"""
from __future__ import annotations

import os
import sys
from PIL import Image

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "desktop", "scripts", "out")


def main() -> int:
    files = sys.argv[1:] or ["stage_314701.png", "stage_314702.png", "stage_314704.png"]
    for name in files:
        p = name if os.path.isabs(name) else os.path.join(OUT, name)
        if not os.path.isfile(p):
            print("missing:", p)
            continue
        im = Image.open(p).convert("RGB")
        W, H = im.size
        px = im.load()

        # capturePage 给的是合成后的整页（深色底 + 角色），alpha 恒为 255，
        # 所以要靠【亮度】把角色从深色背景里分出来，不能用 alpha。
        # 先统计背景亮度，再以「明显亮于背景」为阈值。
        hist = [0] * 256
        for y in range(0, H, 2):
            for x in range(0, W, 2):
                r, g, b = px[x, y]
                hist[(r * 299 + g * 587 + b * 114) // 1000] += 1
        tot = sum(hist)
        acc = 0
        bg = 0
        for i in range(256):
            acc += hist[i]
            if acc >= tot * 0.5:
                bg = i
                break
        thr = max(28, bg + 22)   # 明显亮于背景才算角色

        rows = [0] * H
        cols = [0] * W
        n = 0
        minx, miny, maxx, maxy = W, H, -1, -1
        for y in range(H):
            for x in range(W):
                r, g, b = px[x, y]
                if (r * 299 + g * 587 + b * 114) // 1000 > thr:
                    n += 1
                    rows[y] += 1
                    cols[x] += 1
                    if x < minx: minx = x
                    if x > maxx: maxx = x
                    if y < miny: miny = y
                    if y > maxy: maxy = y

        print("=" * 74)
        print(name, f"{W}x{H}", f"背景亮度≈{bg} 阈值={thr}")
        if maxx < 0:
            print("  未检出角色像素")
            continue
        print(f"  角色像素 {n} ({100.0*n/(W*H):.1f}% 画布)")
        print(f"  包围盒 x {minx}..{maxx}  y {miny}..{maxy}"
              f"  (宽 {maxx-minx+1}, 高 {maxy-miny+1})")
        print("  贴边检查: " + ", ".join([
            f"左={'是' if minx <= 1 else '否'}",
            f"右={'是' if maxx >= W-2 else '否'}",
            f"上={'是' if miny <= 1 else '否'}",
            f"下={'是' if maxy >= H-2 else '否'}",
        ]))
        print(f"  上方留白 {miny}px ({100.0*miny/H:.1f}%)   下方留白 {H-1-maxy}px")
        print(f"  左方留白 {minx}px ({100.0*minx/W:.1f}%)   右方留白 {W-1-maxx}px")
        print("  顶部逐行覆盖宽度（前 10 行）: " +
              " ".join(str(rows[y]) for y in range(min(H, 10))))
        band = max(1, H // 8)
        prof = []
        for b in range(8):
            y0, y1 = b * band, min((b + 1) * band, H)
            prof.append(sum(rows[y0:y1]) // max(1, (y1 - y0)))
        print("  纵向每 1/8 的平均行宽: " + " ".join(str(v) for v in prof))
    return 0


if __name__ == "__main__":
    sys.exit(main())
