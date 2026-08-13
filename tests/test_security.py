"""SSRF / 路径穿越 防护单测（security_utils）。

覆盖 OWASP A10 关键控制：路径收敛到 allowlist 根、URL 正向 allowlist、
私有/保留地址拦截、禁用凭据通配。
"""
import socket

import pytest

from roleplay.core.knowledge.security_utils import (
    assert_public_url,
    is_blocked_ip,
    safe_local_path,
    safe_url,
)


def test_is_blocked_ip_ranges():
    assert is_blocked_ip("127.0.0.1")
    assert is_blocked_ip("10.0.0.5")
    assert is_blocked_ip("192.168.1.1")
    assert is_blocked_ip("172.16.0.1")
    assert is_blocked_ip("169.254.169.254")  # 云元数据
    assert is_blocked_ip("::1")
    assert not is_blocked_ip("93.184.216.34")  # 公网


def test_safe_local_path_blocks_traversal(tmp_path):
    root = tmp_path / "data"
    root.mkdir()
    secret = tmp_path / "secret" / "pass.txt"
    secret.parent.mkdir()
    # 越过 root 的相对越界
    with pytest.raises(ValueError):
        safe_local_path(root / ".." / "secret" / "pass.txt", [str(root)])
    # 绝对路径越界
    with pytest.raises(ValueError):
        safe_local_path("/etc/passwd", [str(root)])
    # 跨盘符/根外
    with pytest.raises(ValueError):
        safe_local_path(tmp_path.parent / "outside.txt", [str(root)])
    # 根内路径放行
    ok = root / "ok.txt"
    assert safe_local_path(ok, [str(root)]) == ok.resolve()


def test_safe_url_rejects_non_https():
    with pytest.raises(ValueError):
        safe_url("http://allowed.example.com/x", ["allowed.example.com"])


def test_safe_url_rejects_unlisted_host():
    with pytest.raises(ValueError):
        safe_url("https://evil.com/x", ["allowed.com"])


def test_safe_url_empty_allowlist_blocks_all():
    with pytest.raises(ValueError):
        safe_url("https://anything.example.com/x", [])


def test_safe_url_rejects_private_ip():
    # host 在白名单但解析到云元数据地址 → 拒绝
    with pytest.raises(ValueError):
        safe_url("https://169.254.169.254/latest/meta-data/", ["169.254.169.254"])


def test_safe_url_allows_listed_public_host(monkeypatch):
    def fake_getaddrinfo(host, port, *a, **k):
        return [(socket.AF_INET, None, None, None, ("93.184.216.34", 0))]

    monkeypatch.setattr(
        "roleplay.core.knowledge.security_utils.socket.getaddrinfo", fake_getaddrinfo
    )
    assert (
        safe_url("https://allowed.example.com/x", ["allowed.example.com"])
        == "https://allowed.example.com/x"
    )


def test_assert_public_url_blocks_metadata():
    with pytest.raises(ValueError):
        assert_public_url("http://169.254.169.254/")
