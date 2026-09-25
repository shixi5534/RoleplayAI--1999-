# -*- coding: utf-8 -*-
"""下载 Xenova/bge-reranker-base 的 ONNX 权重与 tokenizer。

为什么选它：
    目标模型 bge-reranker-v2-m3 **没有 ONNX**（仓库只有 2.1GB torch safetensors），
    而本机没有 torch / transformers。Xenova 提供同一架构（XLM-RoBERTa）的 ONNX 导出，
    用现成的 onnxruntime 就能跑，无需改动 venv。

同时下 fp32 与 int8 两版：
    int8 推理快（CPU 上约快 2~4 倍），用于快速扫描；
    fp32 是精度参考，用于最终定论。
"""
from __future__ import annotations

import os
import time
from pathlib import Path

os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "models" / "bge-reranker-base-onnx"
REPO = "Xenova/bge-reranker-base"
FILES = [
    "tokenizer.json",
    "tokenizer_config.json",
    "special_tokens_map.json",
    "config.json",
    "onnx/model.onnx",          # fp32，精度参考
    "onnx/model_int8.onnx",     # 量化，快速扫描
]


def main() -> int:
    DEST.mkdir(parents=True, exist_ok=True)
    log: list[str] = []

    def p(*a):
        line = " ".join(str(x) for x in a)
        log.append(line)
        print(line, flush=True)

    from huggingface_hub import hf_hub_download
    p(f"目标 {REPO} → {DEST}")
    p("=" * 70)
    for f in FILES:
        t0 = time.time()
        try:
            path = hf_hub_download(REPO, f, local_dir=str(DEST))
            size = Path(path).stat().st_size / 1024 / 1024
            p(f"[ok] {f:<32}{size:>8.1f} MB  {time.time() - t0:>6.0f}s")
        except Exception as e:  # noqa: BLE001
            p(f"[ERR] {f:<32}{type(e).__name__}: {str(e)[:70]}")
    p("=" * 70)
    p("目录内容：")
    for pth in sorted(DEST.rglob("*")):
        if pth.is_file():
            p(f"  {pth.stat().st_size / 1024 / 1024:>8.1f} MB  {pth.relative_to(DEST)}")
    log_path = ROOT / "data" / "knowledge" / "_audit" / "_ce_download.txt"
    log_path.write_text("\n".join(log), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
