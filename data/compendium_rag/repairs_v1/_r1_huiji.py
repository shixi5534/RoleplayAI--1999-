# -*- coding: utf-8 -*-
"""R1 P0 焊拆 · 修复代理 · 第二步：灰机身份裁决。
只访问 https://res1999.huijiwiki.com/api.php（MediaWiki API，禁浏览器页）。
每次拉取披露 {url, fetched_at, bytes}，落盘 _r1_huiji_fetches.json。
输出证据摘要 _r1_huiji_evidence.json。
"""
import json, time, urllib.request, urllib.parse, re
from pathlib import Path

HERE = Path(__file__).resolve().parent
API = "https://res1999.huijiwiki.com/api.php"
UA = {"User-Agent": "roleplay-ai/R1-repairer (offline-first research; api.php only)"}
fetch_log = []
evidence = {"offline_cache": [], "api": []}

def record(kind, url, raw):
    fetch_log.append({"kind": kind, "url": url, "fetched_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                      "bytes": len(raw)})

def api_get(params):
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read()
    record("api.php", url, raw)
    return json.loads(raw.decode("utf-8"))

# ── 0) 离线缓存（已在 _r1 提取中核对，这里登记为证据来源）──
evidence["offline_cache"] = [
    {"file": "data/lore/_huiji_cache/49910dc30331af4cb845.json", "page": "其他角色一览/1.x",
     "note": "玛尔塔(Marta) desc=兀尔德 @1.7今夜星光灿烂；别斯米尔(Bessmert) desc=兀尔德 @1.6朔日手记"},
    {"file": "data/lore/_huiji_cache/dd48cf716bfebe7c792b.json", "page": "其他角色一览/2.x",
     "note": "德洛斯医生(Doctor Dores) desc=兀尔德 @2.2忧郁的热带；兀尔德(Urd) 独立NPC @2.8复乐园"},
    {"file": "data/lore/_huiji_cache/ad593fdc51e3a5c218bf.json", "page": "疯癫与文明",
     "note": "小径故事《暗色带编织》= 兀尔德在主角团到达之前的故事"},
    {"file": "data/lore/wu_ming_zhe/huiji_canon.json", "page": "离线正典 (fetched 2026-09-13)",
     "note": "characters: 卡卡尼亚↔Kakania；npcs: 同上 NPC 表结论"},
]

# ── 1) 卡卡尼亚 角色页 wikitext ──
try:
    d = api_get({"action": "parse", "page": "卡卡尼亚", "prop": "wikitext", "format": "json"})
    wt = (d.get("parse", {}).get("wikitext") or {})
    wt = wt.get("*", "") if isinstance(wt, dict) else str(wt)
    evidence["api"].append({"page": "卡卡尼亚", "type": "parse/wikitext", "len": len(wt),
                            "excerpt_realname": [wt[max(0, m.start() - 120): m.start() + 200]
                                                 for m in re.finditer("克拉拉|温格勒|Kakania", wt)][:6]})
except Exception as ex:
    evidence["api"].append({"page": "卡卡尼亚", "error": repr(ex)})

# ── 2) 批量存在性 + 重定向检查 ──
titles = "兀尔德|玛尔塔|别斯米尔|德洛斯|德洛丝|克拉拉|克拉拉·温格勒|传记作家兀尔德"
try:
    d = api_get({"action": "query", "titles": titles, "redirects": 1, "format": "json"})
    q = d.get("query", {})
    pages = [{"title": p.get("title"), "pageid": p.get("pageid"), "missing": "missing" in p}
             for p in q.get("pages", [])]
    redirs = q.get("redirects", [])
    evidence["api"].append({"query_titles": titles, "pages": pages, "redirects": redirs})
except Exception as ex:
    evidence["api"].append({"query_titles": titles, "error": repr(ex)})

# ── 3) 对存在者拉 wikitext（逐页，限 4 页）──
want = []
for a in evidence["api"]:
    if "pages" in a:
        want = [p["title"] for p in a["pages"] if p.get("pageid") and not p.get("missing")]
for t in want[:4]:
    try:
        d = api_get({"action": "parse", "page": t, "prop": "wikitext", "format": "json"})
        wt = (d.get("parse", {}).get("wikitext") or {})
        wt = wt.get("*", "") if isinstance(wt, dict) else str(wt)
        keep = []
        for kw in ["玛尔塔", "别斯米尔", "德洛斯", "德洛丝", "兀尔德", "卡卡尼亚", "克拉拉", "笔名", "真名", "身份"]:
            for m in list(re.finditer(re.escape(kw), wt))[:2]:
                keep.append({kw: wt[max(0, m.start() - 100): m.start() + 160]})
        evidence["api"].append({"page": t, "type": "parse/wikitext", "len": len(wt), "hits": keep[:12]})
    except Exception as ex:
        evidence["api"].append({"page": t, "error": repr(ex)})

(HERE / "_r1_huiji_fetches.json").write_text(json.dumps(fetch_log, ensure_ascii=False, indent=1), encoding="utf-8")
(HERE / "_r1_huiji_evidence.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(fetch_log, ensure_ascii=False, indent=1))
for a in evidence["api"]:
    print("-" * 60)
    print(json.dumps(a, ensure_ascii=False)[:1200])
