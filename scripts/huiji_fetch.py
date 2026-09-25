# -*- coding: utf-8 -*-
"""灰机 wiki（res1999.huijiwiki.com）抓取器 —— 过 Cloudflare + 页面内 fetch MediaWiki API。

为什么需要它
    灰机 wiki 是本项目剧情数据的**正典标准**，但站点在 Cloudflare 后面：
    直连（requests / web_fetch / playwright headless）一律 403「请稍候…」。
    实测：真实 Chrome（``channel="chrome"``、非 headless、去自动化特征）打开页面后
    约 25–35 秒，Cloudflare 的 JS 挑战自行放行。

怎么做得快
    挑战只在**首次导航**时出现。一旦放行，就在**页面上下文里**用同源 ``fetch``
    直接打 MediaWiki API（Cookie 自动带上），拿到的是结构化 JSON 而不是 HTML——
    而且一次会话可以连续抓几百页。

用法（项目根目录）：
    .venv/Scripts/python.exe -X utf8 scripts/huiji_fetch.py --probe          # 连通性自检
    .venv/Scripts/python.exe -X utf8 scripts/huiji_fetch.py --search 绿湖噩梦
    .venv/Scripts/python.exe -X utf8 scripts/huiji_fetch.py --page 无名者
    .venv/Scripts/python.exe -X utf8 scripts/huiji_fetch.py --category 角色 --limit 50
    .venv/Scripts/python.exe -X utf8 scripts/huiji_fetch.py --batch pages.txt

缓存：``data/lore/_huiji_cache/<sha1>.json``（幂等：命中即不联网）
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "data" / "lore" / "_huiji_cache"
WIKI = "https://res1999.huijiwiki.com"
API = WIKI + "/api.php"
CHROME_CANDIDATES = [
    Path.home() / "AppData/Local/Google/Chrome/Application/chrome.exe",
    Path("C:/Program Files/Google/Chrome/Application/chrome.exe"),
    Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"),
]

STEALTH = """
Object.defineProperty(navigator,'webdriver',{get:()=>undefined});
window.chrome = window.chrome || { runtime: {} };
Object.defineProperty(navigator,'languages',{get:()=>['zh-CN','zh','en']});
Object.defineProperty(navigator,'plugins',{get:()=>[1,2,3,4,5]});
"""


def cache_key(kind: str, payload: dict) -> Path:
    raw = kind + "|" + json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return CACHE_DIR / (hashlib.sha1(raw.encode("utf-8")).hexdigest()[:20] + ".json")


def cache_get(kind: str, payload: dict):
    p = cache_key(kind, payload)
    if p.is_file():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def cache_put(kind: str, payload: dict, value) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_key(kind, payload).write_text(
        json.dumps(value, ensure_ascii=False), encoding="utf-8"
    )


class HuijiSession:
    """一次浏览器会话，多次 API 调用。"""

    def __init__(self, *, headless: bool = False, timeout_ms: int = 60000,
                 challenge_wait_s: int = 60, verbose: bool = False) -> None:
        self.headless = headless
        self.timeout_ms = timeout_ms
        self.challenge_wait_s = challenge_wait_s
        self.verbose = verbose
        self._pw = None
        self._browser = None
        self._page = None
        self.calls = 0

    # —— 生命周期 ——
    def __enter__(self) -> "HuijiSession":
        from playwright.sync_api import sync_playwright

        exe = next((p for p in CHROME_CANDIDATES if p.is_file()), None)
        self._pw = sync_playwright().start()
        kwargs: dict = {"headless": self.headless,
                        "args": ["--disable-blink-features=AutomationControlled"]}
        if exe is not None:
            kwargs["executable_path"] = str(exe)
        else:
            kwargs["channel"] = "chrome"
        self._browser = self._pw.chromium.launch(**kwargs)
        ctx = self._browser.new_context(locale="zh-CN",
                                        viewport={"width": 1440, "height": 900})
        ctx.add_init_script(STEALTH)
        self._page = ctx.new_page()
        self._page.set_default_timeout(self.timeout_ms)
        self._page.goto(WIKI + "/wiki/" + "%E9%A6%96%E9%A1%B5",
                        wait_until="domcontentloaded")
        self._wait_challenge()
        return self

    def __exit__(self, *exc) -> None:
        try:
            if self._browser:
                self._browser.close()
        finally:
            if self._pw:
                self._pw.stop()

    def _wait_challenge(self) -> None:
        """Cloudflare 挑战放行（实测 25–35s）。"""
        deadline = time.time() + self.challenge_wait_s
        while time.time() < deadline:
            try:
                title = self._page.title()
            except Exception:
                title = ""
            if "请稍候" not in title and "Just a moment" not in title:
                if self.verbose:
                    print(f"[cf] 放行：{title}")
                return
            self._page.wait_for_timeout(3000)
        raise SystemExit("[FAIL] Cloudflare 挑战未在时限内放行（换 --headful 或稍后重试）")

    # —— API ——
    def api(self, params: dict) -> dict:
        """在页面上下文里打同源 API（Cookie 自动带上）。"""
        payload = dict(params)
        payload.setdefault("format", "json")
        payload.setdefault("formatversion", "2")
        qs = "&".join(f"{k}={_urlquote(str(v))}" for k, v in payload.items())
        js = """
        async (url) => {
          const r = await fetch(url, {credentials: 'include'});
          const t = await r.text();
          return {status: r.status, body: t};
        }
        """
        res = self._page.evaluate(js, f"{API}?{qs}")
        self.calls += 1
        if res.get("status") != 200:
            raise SystemExit(f"[FAIL] API {res.get('status')}：{res.get('body','')[:200]}")
        try:
            return json.loads(res["body"])
        except json.JSONDecodeError:
            raise SystemExit(f"[FAIL] 非 JSON 响应：{res.get('body','')[:200]}")

    def cached_api(self, kind: str, params: dict) -> dict:
        hit = cache_get(kind, params)
        if hit is not None:
            return hit
        out = self.api(params)
        cache_put(kind, params, out)
        return out

    # —— 高层 ——
    def page_wikitext(self, title: str) -> dict:
        data = self.cached_api("wikitext", {"action": "parse", "page": title,
                                            "prop": "wikitext|displaytitle|categories"})
        return data

    def page_plain(self, title: str) -> dict:
        return self.cached_api("extract", {"action": "query", "prop": "extracts",
                                           "explaintext": "1", "titles": title,
                                           "redirects": "1"})

    def search(self, q: str, limit: int = 20) -> dict:
        return self.cached_api("search", {"action": "query", "list": "search",
                                          "srsearch": q, "srlimit": limit})

    def category(self, name: str, limit: int = 500) -> dict:
        return self.cached_api("category", {"action": "query", "list": "categorymembers",
                                            "cmtitle": f"Category:{name}", "cmlimit": limit})

    def allpages(self, prefix: str = "", limit: int = 500) -> dict:
        return self.cached_api("allpages", {"action": "query", "list": "allpages",
                                            "apprefix": prefix, "aplimit": limit})

    def links(self, title: str, limit: int = 500) -> dict:
        return self.cached_api("links", {"action": "query", "prop": "links",
                                         "titles": title, "pllimit": limit})

    def wikitext_of(self, title: str) -> str:
        d = self.page_wikitext(title)
        return ((d.get("parse") or {}).get("wikitext") or "")

    def displaytitle_of(self, title: str) -> str:
        d = self.page_wikitext(title)
        return ((d.get("parse") or {}).get("displaytitle") or "")


def _urlquote(s: str) -> str:
    from urllib.parse import quote
    return quote(s, safe="")


# ── 标题清洗：灰机 displaytitle 常带 <span> 包裹 ─────────────────────────
_TAG = re.compile(r"<[^>]+>")


def clean_title(s: str) -> str:
    return _TAG.sub("", s or "").strip()


def main() -> int:
    ap = argparse.ArgumentParser(description="灰机 wiki 抓取器")
    ap.add_argument("--probe", action="store_true", help="连通性自检")
    ap.add_argument("--page")
    ap.add_argument("--plain", action="store_true", help="取纯文本而非 wikitext")
    ap.add_argument("--search")
    ap.add_argument("--category")
    ap.add_argument("--allpages", metavar="PREFIX")
    ap.add_argument("--links")
    ap.add_argument("--limit", type=int, default=50)
    ap.add_argument("--headful", action="store_true", help="强制非 headless（默认已是非 headless）")
    ap.add_argument("--out")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with HuijiSession(headless=False, verbose=args.verbose) as s:
        if args.probe:
            d = s.page_wikitext("无名者")
            wt = (d.get("parse") or {}).get("wikitext") or ""
            print(f"[probe] 无名者 wikitext {len(wt)} 字符")
            print(wt[:300].replace("\n", " "))
            return 0

        out = None
        if args.page:
            out = (s.page_plain(args.page) if args.plain else s.page_wikitext(args.page))
        elif args.search:
            out = s.search(args.search, args.limit)
        elif args.category:
            out = s.category(args.category, args.limit)
        elif args.allpages is not None:
            out = s.allpages(args.allpages, args.limit)
        elif args.links:
            out = s.links(args.links, args.limit)
        else:
            ap.print_help()
            return 2

        text = json.dumps(out, ensure_ascii=False, indent=1)
        if args.out:
            Path(args.out).write_text(text, encoding="utf-8")
            print(f"[save] {args.out}（{len(text)} 字符，API 调用 {s.calls} 次）")
        else:
            print(text[:4000])
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
