# -*- coding: utf-8 -*-
"""Cross-Encoder 落地前环境勘查：依赖 / 网络 / 磁盘。决定走 ONNX 还是 torch 路线。"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data" / "knowledge" / "_audit"
OUT = AUDIT / "_ce_env.txt"
buf: list[str] = []


def p(*a):
    buf.append(" ".join(str(x) for x in a))


def ver(mod: str) -> str:
    try:
        m = __import__(mod)
        return getattr(m, "__version__", "?")
    except Exception as e:  # noqa: BLE001
        return f"MISSING ({type(e).__name__})"


p("=" * 66)
p("依赖")
p("=" * 66)
for m in ("onnxruntime", "torch", "transformers", "tokenizers",
          "FlagEmbedding", "huggingface_hub", "numpy"):
    p(f"  {m:<18}{ver(m)}")

# 磁盘剩余
try:
    total, used, free = shutil.disk_usage(str(ROOT))
    p()
    p(f"磁盘剩余 {free / 1024**3:.1f} GB / 总 {total / 1024**3:.1f} GB")
except Exception as e:  # noqa: BLE001
    p(f"磁盘查询失败：{e}")

# 网络：HF 镜像 / 官方
p()
p("=" * 66)
p("网络连通性")
p("=" * 66)
import urllib.request  # noqa: E402

targets = [
    ("hf-mirror 首页", "https://hf-mirror.com"),
    ("hf-mirror API", "https://hf-mirror.com/api/models/BAAI/bge-reranker-v2-m3"),
    ("HF 官方 API", "https://huggingface.co/api/models/BAAI/bge-reranker-v2-m3"),
]
for name, url in targets:
    for method in ("GET", "HEAD"):
        try:
            req = urllib.request.Request(url, method=method,
                                         headers={"User-Agent": "probe/1.0"})
            with urllib.request.urlopen(req, timeout=15) as r:
                body = r.read(2048)
                p(f"  {name:<16}{method:<5}{r.status}  {len(body)}B")
                if b"onnx" in body.lower():
                    p("      ↑ 响应里含 onnx 字样")
                break
        except Exception as e:  # noqa: BLE001
            p(f"  {name:<16}{method:<5}ERR  {type(e).__name__}: {str(e)[:60]}")

OUT.write_text("\n".join(buf), encoding="utf-8")
