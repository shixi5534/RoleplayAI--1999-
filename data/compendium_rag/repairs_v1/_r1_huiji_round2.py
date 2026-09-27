# -*- coding: utf-8 -*-
"""R1 P0 焊拆 · 灰机取证（第二轮）：卡卡尼亚页全文 + 关键名搜索。
落盘仅写本目录；每次 API 调用披露 -> _r1_huiji_fetches.json（追加）。
"""
import json, time, urllib.parse
from pathlib import Path
from urllib.parse import quote

HERE = Path(__file__).resolve().parent
WIKI = "https://res1999.huijiwiki.com"
API = WIKI + "/api.php"
fetch_log = []
out = {}

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
        return {"_http_error": res.get("status")}
    return json.loads(body)

def main():
    from playwright.sync_api import sync_playwright
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "huiji_fetch", HERE.parents[2] / "scripts" / "huiji_fetch.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    with sync_playwright() as pw:
        exe = next((p for p in mod.CHROME_CANDIDATES if p.is_file()), None)
        kwargs = {"headless": False, "args": ["--disable-blink-features=AutomationControlled"]}
        if exe is not None:
            kwargs["executable_path"] = str(exe)
        browser = pw.chromium.launch(**kwargs)
        ctx = browser.new_context(locale="zh-CN", viewport={"width": 1440, "height": 900})
        ctx.add_init_script(mod.STEALTH)
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

        # 1) 卡卡尼亚 页全文
        d = api(page, {"action": "parse", "page": "卡卡尼亚", "prop": "wikitext"})
        p = d.get("parse", {})
        wt = p.get("wikitext")
        if isinstance(wt, dict):
            wt = wt.get("*", "")
        out["kakania_page"] = {"title": p.get("title"), "wikitext": wt or ""}

        # 2) 搜索
        for term in ["兀尔德", "德洛丝 OR 德洛斯", "玛尔塔", "别斯米尔"]:
            d = api(page, {"action": "query", "list": "search", "srsearch": term, "srlimit": "10"})
            out.setdefault("search", {})[term] = [
                {"title": r.get("title"), "snippet": (r.get("snippet") or "").replace('<span class="searchmatch">', "[").replace("</span>", "]")}
                for r in (d.get("query", {}).get("search") or [])]
        browser.close()

    (HERE / "_r1_huiji_fetches.json").write_text(
        json.dumps(fetch_log, ensure_ascii=False, indent=1), encoding="utf-8")
    (HERE / "_r1_huiji_round2.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(fetch_log, ensure_ascii=False, indent=1))
    print("== kakania page wikitext ==")
    print(out["kakania_page"]["wikitext"])
    for term, res in out.get("search", {}).items():
        print("=" * 20, term)
        for r in res:
            print(" ", r["title"], "|", r["snippet"][:150])


if __name__ == "__main__":
    main()
