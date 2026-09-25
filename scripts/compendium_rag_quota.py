# -*- coding: utf-8 -*-
"""探测云端配额是否恢复，并给出可续跑的块数估算。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from compendium_rag.config import get_settings  # noqa: E402
from compendium_rag.extract import (PROMPT_VERSION, ExtractionCache, cache_key)  # noqa: E402
from compendium_rag import pipeline as P  # noqa: E402

MODELS = ["cn:kimi-k2.6", "cn:hunyuan-2.0-instruct", "cn:kimi-k2.5",
          "cn:glm-5.0-turbo", "cn:glm-5.3-flash", "cn:minimax-m2.7"]


def creds() -> tuple[str, str]:
    s = get_settings()
    return s.llm_base_url, s.llm_api_key


def probe(url: str, key: str, model: str) -> str:
    try:
        r = httpx.post(url.rstrip("/") + "/chat/completions",
                       json={"model": model,
                             "messages": [{"role": "user", "content": "hi"}],
                             "max_tokens": 5},
                       headers={"Authorization": f"Bearer {key}"}, timeout=45.0)
    except Exception as exc:  # noqa: BLE001
        return f"EXC {str(exc)[:60]}"
    if r.status_code == 200:
        return "OK"
    try:
        body = json.dumps(r.json(), ensure_ascii=False)
    except ValueError:
        body = r.text
    if "14018" in body or "额度已用尽" in body:
        return "QUOTA_EXHAUSTED"
    if "429" in str(r.status_code):
        return f"429 {body[:90]}"
    return f"HTTP {r.status_code} {body[:90]}"


def main() -> int:
    url, key = creds()
    print(f"endpoint = {url}")
    print(f"api_key  = {'set' if key else 'MISSING'}\n")

    alive = []
    for m in MODELS:
        st = probe(url, key, m)
        print(f"  {m:26} {st}")
        if st == "OK":
            alive.append(m)

    s = get_settings()
    chunks = P.load_chunks(s)
    cache = ExtractionCache(s.cache_dir)
    cached = sum(1 for c in chunks
                 if cache.get_raw(cache_key(c, s.llm_model, PROMPT_VERSION))
                 is not None)
    print(f"\n语料块总数        = {len(chunks)}")
    print(f"已缓存（模型={s.llm_model}） = {cached}")
    print(f"待抽取            = {len(chunks) - cached}")

    if alive:
        print(f"\n✅ 配额已恢复，可用模型：{alive}")
        if s.llm_model not in alive:
            print(f"   注意：默认模型 {s.llm_model} 不可用，"
                  f"可用 CMPRAG_LLM_MODEL 指定，例如：")
            print(f"   $env:CMPRAG_LLM_MODEL='{alive[0]}'")
    else:
        print("\n❌ 所有模型均不可用（配额未恢复或网关故障）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
