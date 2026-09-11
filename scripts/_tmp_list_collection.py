# -*- coding: utf-8 -*-
"""临时脚本：从视频页 __INITIAL_STATE__.sectionsInfo 提取合集分节清单。只读。"""
import json
import re
import sys

sys.path.insert(0, "scripts")
from bilibili_lore_ingest import BiliHttp  # noqa: E402

SEED_BV = "BV1PrgE6WEre"
http = BiliHttp()
html = http.get(f"https://www.bilibili.com/video/{SEED_BV}/")
m = (re.search(r"window\.__INITIAL_STATE__=(\{.*?\});\(function", html, re.S)
     or re.search(r"window\.__INITIAL_STATE__=(\{.*?\});</script>", html, re.S))
if not m:
    print("[fatal] 页面未含 __INITIAL_STATE__，前200字符：", file=sys.stderr)
    print(repr(html[:200]) if html else "None", file=sys.stderr)
    sys.exit(1)
st = json.loads(m.group(1))
info = st["sectionsInfo"]
sections = info["sections"]

all_bv: list[str] = []
for sec in sections:
    eps = sec.get("episodes") or []
    print(f"\n== 栏目「{sec.get('title')}」 {len(eps)}个 ==")
    for i, ep in enumerate(eps, 1):
        bv = ep.get("bvid") or ""
        t = ep.get("title", "")
        print(f"{i:02d}. {bv}  {t[:60]}")
        if bv:
            all_bv.append(bv)

print(f"\n=== 全部 {len(all_bv)} 个BV（按栏目顺序） ===")
print(" ".join(all_bv))
