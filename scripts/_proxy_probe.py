# -*- coding: utf-8 -*-
"""验证「502 是代理劫持 localhost」：禁用代理直连 ollama 再试一次。"""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "knowledge" / "_audit" / "_proxy_probe.txt"
buf: list[str] = []

import os  # noqa: E402
buf.append("代理相关环境变量：")
for k in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy",
          "ALL_PROXY", "NO_PROXY", "no_proxy"):
    v = os.environ.get(k)
    if v:
        buf.append(f"  {k} = {v}")
buf.append("")

url = "http://localhost:11434/api/tags"
body = None
for label, opener in (("默认（走代理）", urllib.request.build_opener()),
                      ("禁用代理直连", urllib.request.build_opener(
                          urllib.request.ProxyHandler({})))):
    try:
        req = urllib.request.Request(url)
        with opener.open(req, timeout=8) as r:
            d = json.loads(r.read().decode("utf-8"))
            buf.append(f"{label} → 200，模型 {len(d.get('models') or [])} 个 "
                       f"{[m.get('name') for m in (d.get('models') or [])][:5]}")
    except Exception as e:  # noqa: BLE001
        buf.append(f"{label} → 失败 {type(e).__name__}: {str(e)[:70]}")

# 禁用代理后再测嵌入
try:
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    body = json.dumps({"model": "bge-m3", "input": "探测"}).encode("utf-8")
    req = urllib.request.Request("http://localhost:11434/api/embed", data=body,
                                 headers={"Content-Type": "application/json"})
    with opener.open(req, timeout=30) as r:
        d = json.loads(r.read().decode("utf-8"))
        v = (d.get("embeddings") or [[0.0]])[0]
        buf.append(f"嵌入（禁代理）→ 200，维度 {len(v)}，前4维 "
                   f"{[round(float(x), 6) for x in v[:4]]}")
except Exception as e:  # noqa: BLE001
    buf.append(f"嵌入（禁代理）→ 失败 {type(e).__name__}: {str(e)[:70]}")

OUT.write_text("\n".join(buf), encoding="utf-8")
