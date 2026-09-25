# -*- coding: utf-8 -*-
"""在多个候选仓库里找「可直接用 onnxruntime 加载」的中文 cross-encoder。"""
from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data" / "knowledge" / "_audit"
OUT = AUDIT / "_ce_candidates.txt"
buf: list[str] = []


def p(*a):
    buf.append(" ".join(str(x) for x in a))


from huggingface_hub import HfApi  # noqa: E402

api = HfApi()
CANDS = [
    "Xenova/bge-reranker-v2-m3",
    "Xenova/bge-reranker-base",
    "Xenova/bge-reranker-large",
    "onnx-community/bge-reranker-v2-m3",
    "onnx-community/bge-reranker-base",
    "maidalun1020/bce-reranker-base_v1",
    "Xenova/bce-reranker-base_v1",
]

p("寻找可直接 onnxruntime 加载的中文 cross-encoder")
p("=" * 84)
best: list[tuple[str, str, float]] = []
for repo in CANDS:
    try:
        info = api.repo_info(repo, files_metadata=True)
        files = [(f.rfilename, (f.size or 0) / 1024 / 1024) for f in (info.siblings or [])]
    except Exception as e:  # noqa: BLE001
        p(f"  {repo:<40} 不可达（{type(e).__name__}）")
        continue
    onnx = [(n, s) for n, s in files if n.lower().endswith((".onnx", ".onnx_data"))]
    tk = any(n == "tokenizer.json" for n, _ in files)
    if onnx:
        for n, s in sorted(onnx, key=lambda x: -x[1]):
            p(f"  {repo:<40} {s:>8.1f}MB  {n}")
        p(f"  {'':<40} tokenizer.json={'有' if tk else '**缺**'}")
        best.append((repo, onnx[0][0], max(s for _, s in onnx)))
    else:
        st = [s for n, s in files if n.endswith(".safetensors")]
        p(f"  {repo:<40} 无 onnx（safetensors {sum(st):.0f}MB）")

p()
p("=" * 84)
if best:
    p("候选（按体积升序）：")
    for repo, f, mb in sorted(best, key=lambda x: x[2]):
        p(f"  {mb:>8.1f}MB  {repo} / {f}")
else:
    p("**没有任何候选提供 ONNX** ⇒ 只能走「装 torch CPU + transformers」路线")

OUT.write_text("\n".join(buf), encoding="utf-8")
