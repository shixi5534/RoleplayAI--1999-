# -*- coding: utf-8 -*-
"""列出 bge-reranker-v2-m3 仓库文件，挑体积合适的 ONNX 变体。"""
from __future__ import annotations

import os
from pathlib import Path

# HF 官方不可达（Tunnel 502），走镜像
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data" / "knowledge" / "_audit"
OUT = AUDIT / "_ce_files.txt"
buf: list[str] = []


def p(*a):
    buf.append(" ".join(str(x) for x in a))


try:
    from huggingface_hub import HfApi
except Exception as e:  # noqa: BLE001
    OUT.write_text(f"[FATAL] huggingface_hub 不可用：{e}", encoding="utf-8")
    raise SystemExit(1)

repo = "BAAI/bge-reranker-v2-m3"
p(f"仓库 {repo}｜镜像 {os.environ['HF_ENDPOINT']}")
p("=" * 78)
try:
    api = HfApi()
    info = api.repo_info(repo, files_metadata=True)
    files = [(f.rfilename, f.size or 0) for f in (info.siblings or [])]
except Exception as e:  # noqa: BLE001
    p(f"[ERR] 列文件失败：{type(e).__name__}: {e}")
    files = []

if files:
    for name, size in sorted(files, key=lambda x: -x[1]):
        mb = size / 1024 / 1024
        mark = ""
        low = name.lower()
        if low.startswith("onnx/") or low.endswith(".onnx") or low.endswith(".onnx_data"):
            mark = "  ★ONNX"
        elif name in ("config.json", "tokenizer.json", "tokenizer_config.json",
                      "special_tokens_map.json", "vocab.txt", "sentencepiece.bpe.model"):
            mark = "  ★必需"
        p(f"{mb:>9.1f} MB  {name}{mark}")

OUT.write_text("\n".join(buf), encoding="utf-8")
