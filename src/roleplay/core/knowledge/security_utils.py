"""输入收敛与 SSRF 防护（纯标准库，零依赖）。

依据 OWASP A10 / SSRF Prevention Cheat Sheet：
- 本地路径：realpath 收敛后必须仍位于 allowlist 根目录内（防 ../ 穿越、绝对路径越界）。
- URL：正向 allowlist（scheme=https + host 白名单）；解析后 IP 落在私有/保留段即拒绝
  （环回、RFC1918、链路本地/云元数据 169.254.169.254、IPv6 唯一本地、共享地址等）；
  并禁用重定向（由调用方在 httpx 中设置 allow_redirects=False）。
- Web 抓取深度防御：解析失败放行（离线场景交由 HTTP 层处理），解析成功且为私有地址则拒绝。

本模块不依赖任何项目内其它模块，避免与 document_ingest / ingest 形成循环导入。
"""
from __future__ import annotations

import ipaddress
import socket
import urllib.parse
from pathlib import Path

# 私有 / 保留地址段（OWASP 推荐的最小拒绝集 + IPv6 唯一本地 + 共享地址空间）
BLOCKED_IP_NETS = [
    ipaddress.ip_network("127.0.0.0/8"),       # 环回
    ipaddress.ip_network("0.0.0.0/8"),         # 当前网络
    ipaddress.ip_network("10.0.0.0/8"),         # RFC1918 私有
    ipaddress.ip_network("172.16.0.0/12"),      # RFC1918 私有
    ipaddress.ip_network("192.168.0.0/16"),     # RFC1918 私有
    ipaddress.ip_network("169.254.0.0/16"),     # 链路本地（含云元数据 169.254.169.254）
    ipaddress.ip_network("100.64.0.0/10"),      # 运营商共享地址空间（RFC 6598）
    ipaddress.ip_network("::1/128"),            # IPv6 环回
    ipaddress.ip_network("fc00::/7"),           # IPv6 唯一本地
]


def is_blocked_ip(ip_str: str) -> bool:
    """IP 是否落在私有/保留段内。非法字符串当作非阻塞。"""
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return False
    return any(ip in net for net in BLOCKED_IP_NETS)


def safe_local_path(path: str | Path, allowed_roots: list[str]) -> Path:
    """把路径收敛到 allowlist 根目录内，防路径穿越；返回已校验的绝对 Path。

    允许 roots 为空（调用方选择不约束），此时原样返回 realpath。
    """
    p = Path(path).resolve()
    if not allowed_roots:
        return p
    for root in allowed_roots:
        r = Path(root).resolve()
        # p 等于根，或位于根之下（r 是 p 的某个祖先目录）
        if p == r or r in p.parents:
            return p
    raise ValueError(f"路径超出允许范围（路径穿越防护）：{path}")


def safe_url(url: str, allowed_hosts: list[str]) -> str:
    """正向 allowlist 校验 + 私有 IP 拦截。空 allowlist 即拒绝一切。

    - scheme 仅允许 https；
    - host 必须显式在允许列表内（绝不用 denylist/正则，易绕过）；
    - 解析后每个 IP 不得落在私有/保留段（防 DNS rebinding：解析在请求同一次调用内完成）。
    """
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https":
        raise ValueError("仅允许 https 方案的 URL")
    host = (parsed.hostname or "").lower()
    if not host:
        raise ValueError("URL 缺少主机名")
    allow = {h.strip().lower() for h in allowed_hosts}
    if host not in allow:
        raise ValueError(f"主机不在允许列表：{host}")
    try:
        infos = socket.getaddrinfo(host, parsed.port or 443)
    except socket.gaierror as exc:
        raise ValueError(f"无法解析主机：{host}") from exc
    for info in infos:
        ip = info[4][0]
        if is_blocked_ip(ip):
            raise ValueError(f"目标为私有/保留地址，禁止访问：{ip}")
    return url


def assert_public_url(url: str) -> None:
    """Web 抓取深度防御：解析后若为私有/保留地址则拒绝。

    解析失败（离线/无法解析）放行 —— 交由 HTTP 层处理，避免离线环境误杀。
    """
    parsed = urllib.parse.urlparse(url)
    host = (parsed.hostname or "").lower()
    if not host:
        raise ValueError("URL 缺少主机名")
    try:
        infos = socket.getaddrinfo(host, parsed.port or 80)
    except (socket.gaierror, UnicodeError, ValueError):
        return
    for info in infos:
        if is_blocked_ip(info[4][0]):
            raise ValueError(f"目标为私有/保留地址，禁止抓取：{info[4][0]}")
