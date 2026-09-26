# -*- coding: utf-8 -*-
"""灰机 wiki 预取工具（修复战役 R1/R2 的离线资料准备）。
只访问 https://res1999.huijiwiki.com/api.php（MediaWiki API），带 UA，禁浏览器页。
两步：search 找真实页名 → parse 拉wikitext。全部落盘 data/compendium_rag/huiji_pages/，
每次拉取披露 {url, fetched_at, bytes, status}。"""
import json, time, sys, io, urllib.request, urllib.parse
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "data" / "compendium_rag" / "huiji_pages"
OUT.mkdir(parents=True, exist_ok=True)
API = "https://res1999.huijiwiki.com/api.php"
UA = {"User-Agent": "roleplay-ai/repair-prefetch (offline-first research; api.php only)"}
LOG = []

def api_get(params, tries=4):
    url = API + "?" + urllib.parse.urlencode(params)
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                raw = r.read()
            obj = json.loads(raw.decode("utf-8"))
            LOG.append({"url": url, "fetched_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "bytes": len(raw), "status": 200})
            return obj
        except Exception as e:
            LOG.append({"url": url, "fetched_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "error": str(e)[:120], "attempt": i + 1})
            time.sleep(2 * (i + 1))
    return None

def prefetch(name):
    out = {"name": name, "search": None, "pages": {}}
    s = api_get({"action": "query", "list": "search", "srsearch": name,
                 "srlimit": 8, "format": "json", "formatversion": 2})
    if not s:
        out["search"] = "FETCH_FAILED"
    else:
        hits = [(h["title"], h.get("snippet", "")) for h in s.get("query", {}).get("search", [])]
        out["search"] = hits
        for title, _snip in hits[:2]:
            p = api_get({"action": "parse", "page": title, "prop": "wikitext",
                         "format": "json", "formatversion": 2})
            if p and "parse" in p:
                out["pages"][title] = p["parse"].get("wikitext", "")
            else:
                out["pages"][title] = f"PARSE_FAILED_OR_MISSING: {p}"
    fp = OUT / f"r1_{name}.json"
    fp.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{name}: search={'OK' if out['search'] not in (None,'FETCH_FAILED') else 'FAIL'} "
          f"pages={list(out['pages'])}")

if __name__ == "__main__":
    names = sys.argv[1:] or ["卡卡尼亚", "德洛丝", "玛尔塔", "别斯米尔", "兀尔德", "克拉拉"]
    for nm in names:
        prefetch(nm)
        time.sleep(1)
    (OUT / "_prefetch_log.json").write_text(
        json.dumps(LOG, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"共 {len(LOG)} 次请求，日志 -> huiji_pages/_prefetch_log.json")
