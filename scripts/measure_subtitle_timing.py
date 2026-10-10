# -*- coding: utf-8 -*-
"""量测字幕的「可读时间」是否足够（用户反馈：英语读不完）。

除了"文字太长"，还有一个独立成因：字幕停留时长由【音频时长】决定
（见 frontend/js/pet-subtitle.js）：

    const ms = Math.max(o.replay ? 700 : 2200, (durSec || 4) * 1000 + HIDE_EXTRA_MS);

即 dur=0.72s 的片段，字幕最多留 2.2s（被 2200 下限兜住）。若此时屏上是 145 个英文
字符，必然读不完。

本脚本对清单里每条音频计算：
    需要阅读速度 = 显示文本长度 / 实际停留秒数
并与保守的舒适阅读速度比较：
    中文 ≈ 6 字/秒，英文 ≈ 14 字符/秒
超出即判"读不完"。

用法：
  .venv\\Scripts\\python.exe scripts\\measure_subtitle_timing.py
  .venv\\Scripts\\python.exe scripts\\measure_subtitle_timing.py --lang en
"""
from __future__ import annotations

import argparse
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "frontend", "assets", "voice", "wu_ming_zhe", "manifest.json")

HIDE_EXTRA_MS = 1600          # 与 pet-subtitle.js 的常量保持一致
MIN_DWELL_MS = 2200           # 与 pet-subtitle.js 的 MIN_DWELL_MS 一致
READ_CPS_ZH = 6               # 与 pet-subtitle.js 的 READ_CPS_ZH 一致
READ_CPS_EN = 14              # 与 pet-subtitle.js 的 READ_CPS_EN 一致
READ_SLACK = 1.15             # 与 pet-subtitle.js 的 READ_SLACK 一致
MAX_DWELL_MS = 20000          # 与 pet-subtitle.js 的 MAX_DWELL_MS 一致

READ_ZH_PER_SEC = READ_CPS_ZH
READ_EN_PER_SEC = READ_CPS_EN


def dwell_seconds(dur: float, zh: str = "", en: str = "") -> float:
    """复刻 pet-subtitle.js 现在的停留时长计算（秒）。

    新逻辑同时满足三件事：音频播完、够读完、且不低于下限，最后加总上限。
    """
    read = max(len(zh or "") / READ_CPS_ZH, len(en or "") / READ_CPS_EN) * READ_SLACK
    ms = max(MIN_DWELL_MS, (dur or 4) * 1000 + HIDE_EXTRA_MS, read * 1000)
    ms = min(ms, MAX_DWELL_MS)
    return ms / 1000.0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", default="all", choices=["all", "zh", "en"])
    ap.add_argument("--top", type=int, default=12)
    a = ap.parse_args()

    man = json.load(io.open(MANIFEST, encoding="utf-8"))
    clips = man["clips"]

    rows = []
    for c in clips:
        if a.lang != "all" and c["lang"] != a.lang:
            continue
        sub = c.get("subtitle") or {}
        # 字幕条同时显示中英两行，两行都要读 -> 取更吃力的那一行来评估
        need_zh = len((sub.get("zh") or "")) / READ_ZH_PER_SEC
        need_en = len((sub.get("en") or "")) / READ_EN_PER_SEC
        need = max(need_zh, need_en)
        dwell = dwell_seconds(c.get("dur"), sub.get("zh") or "", sub.get("en") or "")
        rows.append({
            "id": c["id"], "lang": c["lang"], "dur": c.get("dur", 0),
            "dwell": dwell, "need": need,
            "rate": need / dwell if dwell else 0,
            "zh_len": len(sub.get("zh") or ""), "en_len": len(sub.get("en") or ""),
            "audio": (c.get("text") or "")[:40],
        })

    bad = [r for r in rows if r["rate"] > 1.0]
    rows.sort(key=lambda r: -r["rate"])

    print("字幕可读性（停留时长 vs 阅读所需时长）")
    print("  判定阈值：需要时长 / 停留时长 > 1.0 即「读不完」")
    print("  样本 %d 条，其中读不完 %d 条 (%.0f%%)"
          % (len(rows), len(bad), 100.0 * len(bad) / max(1, len(rows))))
    print()
    print("  %-8s %-3s %6s %6s %7s %6s %6s  %s" %
          ("id", "lg", "dur", "停留", "需要", "倍率", "en字数", "音频"))
    for r in rows[: a.top]:
        flag = "!!" if r["rate"] > 1.0 else "  "
        print("  %s%-8s %-3s %6.2f %6.2f %7.2f %6.2f %6d  %s" %
              (flag, r["id"], r["lang"], r["dur"], r["dwell"], r["need"],
               r["rate"], r["en_len"], r["audio"]))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
