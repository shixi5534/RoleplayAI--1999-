"""联网检索端口（可插拔）。

- DuckDuckGoAdapter：免 key，抓 html.duckduckgo.com 结果页并尽力解析（无需 API key）。
- BingAdapter：免 key，抓 www.bing.com/search 结果页并尽力解析（DDG 在某些网络
  （如部分国内网络）不可达时的免 key 备选；实测 Bing 可达且结果块完整）。
- TavilyAdapter：配置 ROLEPLAY_TAVILY_KEY 后使用，结果更稳更全。
- build_web_search：按配置选择实现；未配 key 时默认 DDG，DDG 失败自动回退 Bing。

所有实现均做异常兜底，单条失败不影响整体，返回已成功解析的结果。

并发模型：search 为异步方法，内部用 httpx.AsyncClient 发起请求，避免在异步事件循环
中执行阻塞式同步网络 IO。
"""
from __future__ import annotations

import asyncio
import html as html_mod
import json
import logging
import re
import urllib.parse
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List

import httpx

from ...config import Settings, get_settings

logger = logging.getLogger(__name__)

_UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )
}


@dataclass
class WebResult:
    url: str
    title: str
    snippet: str
    content: str = ""


class WebSearchPort(ABC):
    @abstractmethod
    async def search(self, query: str, max_results: int = 5) -> List[WebResult]:
        """返回与 query 相关的网页结果（无需保证数量）。异步。"""


class DuckDuckGoAdapter(WebSearchPort):
    """免 key 的 DuckDuckGo HTML 结果页抓取（尽力解析）。"""

    async def search(self, query: str, max_results: int = 5) -> List[WebResult]:
        results: List[WebResult] = []
        try:
            url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query)
            async with httpx.AsyncClient(
                headers=_UA, timeout=httpx.Timeout(3.0)  # 短超时：DDG 常不可达，快速回退
            ) as client:
                resp = await client.get(url)
                body = resp.text
            # 每个结果块形如：<a class="result__a" href="<redirect>" ...>标题</a>
            # 以及 <a class="result__snippet" ...>摘要</a>
            links = re.findall(
                r'<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
                body,
                re.S,
            )
            snippets = re.findall(
                r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>', body, re.S
            )
            for i, (href, title_html) in enumerate(links[:max_results]):
                real = self._decode_ddg_url(href)
                if not real:
                    continue
                title = re.sub(r"<.*?>", "", title_html).strip()
                snippet = ""
                if i < len(snippets):
                    snippet = re.sub(r"<.*?>", "", snippets[i]).strip()
                results.append(WebResult(url=real, title=title, snippet=snippet))
        except Exception as exc:  # noqa: BLE001
            logger.warning("DuckDuckGo 搜索失败：%s", exc)
        return results

    @staticmethod
    def _decode_ddg_url(href: str) -> str:
        # DDG 把真实地址放在 uddg 参数里（如 //duckduckgo.com/l/?uddg=<encoded>）
        m = re.search(r"uddg=([^&]+)", href)
        if m:
            try:
                return urllib.parse.unquote(m.group(1))
            except Exception:  # noqa: BLE001
                pass
        if href.startswith("//"):
            return "https:" + href
        if href.startswith("http"):
            return href
        return ""


class BingAdapter(WebSearchPort):
    """免 key 的 Bing 结果页抓取（尽力解析）。

    背景：DuckDuckGo 在部分网络（尤其国内直连）完全不可达，而 Bing
    （www.bing.com）实测可达且结果块完整。作为 DDG 的免 key 回退。

    解析策略（对应实测 Bing 结果页结构）：
    - 结果块：<li class="b_algo" ...>...</li>
    - 标题：块内第一个 <h2><a href="真实URL">标题</a></h2>
    - 摘要：块内 <p class="b_lineclamp...">...</p>
    链接为真实 URL（非重定向跳板），无需二次解码。
    """

    _SEARCH_URL = "https://www.bing.com/search"

    async def search(self, query: str, max_results: int = 5) -> List[WebResult]:
        results: List[WebResult] = []
        try:
            params = {
                "q": query,
                "setlang": "zh-hans",
                "cc": "cn",
                "count": str(max(10, max_results)),
            }
            async with httpx.AsyncClient(
                headers={**_UA, "Accept-Language": "zh-CN,zh;q=0.9"},
                timeout=httpx.Timeout(8.0),
                follow_redirects=True,
            ) as client:
                resp = await client.get(self._SEARCH_URL, params=params)
                body = resp.text
            blocks = re.findall(r'<li class="b_algo"[\s\S]*?</li>', body)
            for blk in blocks[:max_results]:
                m = re.search(
                    r'<h2[^>]*><a[^>]*href="([^"]+)"[^>]*>(.*?)</a></h2>',
                    blk,
                    re.S,
                )
                if not m:
                    continue
                url = html_mod.unescape(m.group(1)).strip()
                if not url.startswith(("http://", "https://")):
                    continue
                title = re.sub(r"<.*?>", "", m.group(2))
                title = html_mod.unescape(title).strip()
                p = re.search(r'<p[^>]*class="b_lineclamp[^"]*"[^>]*>(.*?)</p>', blk, re.S)
                snippet = ""
                if p:
                    snippet = re.sub(r"<.*?>", "", p.group(1))
                    snippet = html_mod.unescape(snippet).strip()
                results.append(WebResult(url=url, title=title, snippet=snippet))
        except Exception as exc:  # noqa: BLE001
            logger.warning("Bing 搜索失败：%s", exc)
        if not results:
            logger.warning("Bing 搜索未解析到结果（query=%r）", query)
        return results


class TavilyAdapter(WebSearchPort):
    """Tavily 搜索 API（需 ROLEPLAY_TAVILY_KEY）。"""

    def __init__(self, api_key: str) -> None:
        self._key = api_key

    async def search(self, query: str, max_results: int = 5) -> List[WebResult]:
        url = "https://api.tavily.com/search"
        payload = {
            "api_key": self._key,
            "query": query,
            "max_results": max_results,
            "search_depth": "basic",
        }
        try:
            async with httpx.AsyncClient(
                headers={"Content-Type": "application/json", **_UA},
                timeout=httpx.Timeout(12.0),
            ) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
        except Exception as exc:  # noqa: BLE001
            logger.warning("Tavily 搜索失败：%s", exc)
            return []
        out: List[WebResult] = []
        for r in data.get("results", []):
            out.append(
                WebResult(
                    url=r.get("url", ""),
                    title=r.get("title", ""),
                    snippet=r.get("content", ""),
                    content=r.get("content", ""),
                )
            )
        return out


class FallbackWebSearch(WebSearchPort):
    """多实现回退链：按顺序尝试，任一返回非空结果即停止。

    用于「DDG 在某些网络不可达」的容错：DDG 失败（超时/无结果）自动换 Bing，
    均失败再返回空（由上层降级处理）。
    """

    def __init__(self, *adapters: WebSearchPort) -> None:
        self._adapters = list(adapters)

    async def search(self, query: str, max_results: int = 5) -> List[WebResult]:
        for adapter in self._adapters:
            try:
                results = await adapter.search(query, max_results=max_results)
            except Exception as exc:  # noqa: BLE001
                logger.warning("联网检索 %s 异常，尝试下一个：%s", type(adapter).__name__, exc)
                continue
            if results:
                return results
            logger.info(
                "联网检索 %s 返回空结果，回退下一个", type(adapter).__name__
            )
        return []


def build_web_search(settings: Settings | None = None) -> WebSearchPort:
    s = settings or get_settings()
    if s.web_provider == "tavily" and s.tavily_api_key:
        logger.info("联网检索：使用 Tavily")
        return TavilyAdapter(s.tavily_api_key)
    if s.web_provider == "bing":
        logger.info("联网检索：使用 Bing（免 key）")
        return BingAdapter()
    # 默认免 key 链：DDG 优先（结果质量较好），失败自动回退 Bing（国内可达）
    logger.info("联网检索：使用 DuckDuckGo → Bing 回退链（免 key）")
    return FallbackWebSearch(DuckDuckGoAdapter(), BingAdapter())
