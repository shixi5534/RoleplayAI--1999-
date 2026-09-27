# -*- coding: utf-8 -*-
"""R1 P0 焊拆 · 第三步补丁：经 Cloudflare 会话访问 res1999.huijiwiki.com/api.php。
复用 scripts/huiji_fetch.py 的过墙机制（真实 Chrome + 页内同源 fetch），
但所有落盘仅写入本目录（repairs_v1/），不新增缓存文件到 _huiji_cache。
每次 API 调用披露 {url, fetched_at, bytes} -> _r1_huiji_fetches.json。
"""
import json, time, urllib.parse
from pathlib import Path
from urllib.parse import quote

HERE = Path(__file__).resolve().parent
WIKI = "https://res1999.huijiwiki.com"
API = WIKI + "/api.php"
fetch_log = []
evidence = {"api": []}


def api(s, params):
    payload = dict(params)
    payload.setdefault("format", "json")
    payload.setdefault("formatversion", "2")
    qs = "&".join(f"{k}={quote(str(v), safe='')}" for k, v in payload.items())
    js = """
    async (url) => {
      const r = await fetch(url, {credentials: 'include'});
      const t = await r.text();
      return {status: r.status, body: t};
    }
    """
    res = s.evaluate(js, f"{API}?{qs}")
    body = res.get("body", "")
    fetch_log.append({"url": f"{API}?{qs}", "fetched_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                      "bytes": len(body), "status": res.get("status")})
    if res.get("status") != 200:
        return {"_http_error": res.get("status"), "body_head": body[:200]}
    return json.loads(body)


def wt_of(d):
    p = (d.get("parse") or {})
    wt = p.get("wikitext")
    if isinstance(wt, dict):
        wt = wt.get("*", "")
    return p.get("title"), (wt or "")


def main():
    import re
    from playwright.sync_api import sync_playwright
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "huiji_fetch", HERE.parents[2] / "scripts" / "huiji_fetch.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    CHROME_CANDIDATES, STEALTH = mod.CHROME_CANDIDATES, mod.STEALTH

    with sync_playwright() as pw:
        exe = next((p for p in CHROME_CANDIDATES if p.is_file()), None)
        kwargs = {"headless": False, "args": ["--disable-blink-features=AutomationControlled"]}
        if exe is not None:
            kwargs["executable_path"] = str(exe)
        browser = pw.chromium.launch(**kwargs)
        ctx = browser.new_context(locale="zh-CN", viewport={"width": 1440, "height": 900})
        ctx.add_init_script(STEALTH)
        page = ctx.new_page()
        page.set_default_timeout(60000)
        page.goto(WIKI + "/wiki/" + quote("首页", safe=""), wait_until="domcontentloaded")
        deadline = time.time() + 90
        while time.time() < deadline:
            title = page.title() if page else ""
            if "请稍候" not in title and "Just a moment" not in title:
                print(f"[cf] pass: {title}")
                break
            page.wait_for_timeout(3000)
        else:
            raise SystemExit("[FAIL] Cloudflare challenge not passed")

        # 1) 卡卡尼亚 角色页
        d = api(page, {"action": "parse", "page": "卡卡尼亚", "prop": "wikitext"})
        t, wt = wt_of(d)
        hits = []
        for kw in ["克拉拉", "温格勒", "真名", "本名", "笔名", "身份", "兀尔德", "Kakania"]:
            for m in list(re.finditer(re.escape(kw), wt))[:2]:
                hits.append({kw: wt[max(0, m.start() - 100): m.start() + 180]})
        evidence["api"].append({"page": t, "type": "parse/wikitext", "len": len(wt), "hits": hits[:14]})

        # 2) 批量存在性 + 重定向
        titles = "兀尔德|玛尔塔|别斯米尔|德洛斯|德洛丝|克拉拉|克拉拉·温格勒"
        d = api(page, {"action": "query", "titles": titles, "redirects": "1"})
        q = d.get("query", {})
        pages = [{"title": p.get("title"), "pageid": p.get("pageid"), "missing": "missing" in p}
                 for p in q.get("pages", [])]
        evidence["api"].append({"query_titles": titles, "pages": pages,
                                "redirects": q.get("redirects", [])})

        # 3) 对存在者拉 wikitext（最多 4 页）
        want = [p["title"] for p in pages if p.get("pageid") and not p.get("missing")]
        for tt in want[:4]:
            d = api(page, {"action": "parse", "page": tt, "prop": "wikitext"})
            t2, wt2 = wt_of(d)
            hits2 = []
            for kw in ["玛尔塔", "别斯米尔", "德洛斯", "德洛丝", "兀尔德", "卡卡尼亚",
                       "克拉拉", "笔名", "真名", "身份", "Urd", "Marta", "Bessmert", "Dores"]:
                for m in list(re.finditer(re.escape(kw), wt2))[:2]:
                    hits2.append({kw: wt2[max(0, m.start() - 100): m.start() + 180]})
            evidence["api"].append({"page": t2, "type": "parse/wikitext", "len": len(wt2),
                                    "hits": hits2[:16]})
        browser.close()

    (HERE / "_r1_huiji_fetches.json").write_text(
        json.dumps(fetch_log, ensure_ascii=False, indent=1), encoding="utf-8")
    (HERE / "_r1_huiji_evidence.json").write_text(
        json.dumps(evidence, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(fetch_log, ensure_ascii=False, indent=1))
    for a in evidence["api"]:
        print("-" * 70)
        print(json.dumps(a, ensure_ascii=False)[:1600])


if __name__ == "__main__":
    main()
