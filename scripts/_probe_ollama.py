# -*- coding: utf-8 -*-
"""探测 ollama 可用性与嵌入器实际身份。"""
from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
OUT = ROOT / "data" / "knowledge" / "_audit" / "_ollama_probe.txt"
buf: list[str] = []

for url in ("http://localhost:11434/api/tags",
            "http://localhost:11434/api/embed"):
    try:
        if url.endswith("tags"):
            with urllib.request.urlopen(url, timeout=8) as r:
                d = json.loads(r.read().decode("utf-8"))
                buf.append(f"{url} → 200，模型 {len(d.get('models') or [])} 个："
                           f"{[m.get('name') for m in (d.get('models') or [])][:6]}")
        else:
            body = json.dumps({"model": "bge-m3", "input": "探测"}).encode("utf-8")
            req = urllib.request.Request(url, data=body,
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=20) as r:
                d = json.loads(r.read().decode("utf-8"))
                v = (d.get("embeddings") or [[0.0]])[0]
                buf.append(f"{url} → 200，向量维度 {len(v)}，前4维 "
                           f"{[round(float(x), 6) for x in v[:4]]}")
    except Exception as e:  # noqa: BLE001
        buf.append(f"{url} → **失败** {type(e).__name__}: {str(e)[:80]}")

from roleplay.config import get_settings  # noqa: E402
from roleplay.core.knowledge.factory import build_plot_registry  # noqa: E402

s = get_settings()
reg = build_plot_registry(s)
retr = reg.get("wu_ming_zhe")
sem = getattr(retr, "semantic", None)
buf.append(f"\nregistry.semantic_status = {dict(getattr(reg, 'semantic_status', {}) or {})}")
buf.append(f"retr.semantic = {type(sem).__name__}")
emb = getattr(sem, "embedder", None) if sem is not None else None
if emb is not None and hasattr(emb, "name"):
    buf.append(f"语义索引内部嵌入器 name = {emb.name()}")
# 直接问嵌入器工厂会造出什么
from roleplay.core.knowledge.embedder import build_embedder  # noqa: E402
e2 = build_embedder(s)
n2 = e2.name() if callable(getattr(e2, "name", None)) else getattr(e2, "name", "?")
buf.append(f"build_embedder() 现在会返回：{type(e2).__name__}｜name={n2}")

OUT.write_text("\n".join(buf), encoding="utf-8")
