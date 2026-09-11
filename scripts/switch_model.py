# -*- coding: utf-8 -*-
"""切换 roleplay-ai 的 LLM 模型（Ollama 本地）。

用法：
  python scripts/switch_model.py qwen2.5:7b     # 切到 7B
  python scripts/switch_model.py qwen2.5:1.5b   # 回滚到 1.5B
  python scripts/switch_model.py                # 查看当前模型

- 只改 .env 的 ROLEPLAY_LLM_MODEL 一行，不动其他配置
- 备份 .env 到 .env.bak.<时间戳>（首次切换时）
- 切换后自动做一次连通性冒烟测试（可选 --no-test 跳过）
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV = ROOT / ".env"


def get_current_model() -> str:
    for line in ENV.read_text(encoding="utf-8").splitlines():
        if line.startswith("ROLEPLAY_LLM_MODEL="):
            return line.split("=", 1)[1].strip()
    return "?"


def set_model(model: str) -> None:
    lines = ENV.read_text(encoding="utf-8").splitlines()
    out = []
    replaced = False
    for line in lines:
        if line.startswith("ROLEPLAY_LLM_MODEL="):
            out.append(f"ROLEPLAY_LLM_MODEL={model}")
            replaced = True
        else:
            out.append(line)
    if not replaced:
        out.append(f"ROLEPLAY_LLM_MODEL={model}")
    ENV.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"[ok] ROLEPLAY_LLM_MODEL -> {model}")


def smoke_test(model: str) -> bool:
    """调 Ollama OpenAI 兼容接口做一次最小生成，确认模型可用。"""
    import json
    import urllib.request

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "说一句话证明你在。"}],
        "max_tokens": 20,
        "stream": False,
    }
    req = urllib.request.Request(
        "http://localhost:11434/v1/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
        reply = data["choices"][0]["message"]["content"].strip()
        print(f"[smoke] 模型响应: {reply[:40]}")
        return True
    except Exception as e:  # noqa: BLE001
        print(f"[fail] 冒烟测试失败: {e}")
        return False


def main() -> int:
    ap = argparse.ArgumentParser(description="切换 roleplay-ai LLM 模型")
    ap.add_argument("model", nargs="?", help="目标模型名，如 qwen2.5:7b")
    ap.add_argument("--no-test", action="store_true", help="跳过冒烟测试")
    args = ap.parse_args()

    cur = get_current_model()
    if not args.model:
        print(f"当前模型: {cur}")
        return 0

    if args.model == cur:
        print(f"已经是 {cur}，无需切换")
        return 0

    # 首次切换前备份
    bak = ENV.with_suffix(f".env.bak.{time.strftime('%Y%m%d_%H%M%S')}")
    if not list(ENV.parent.glob(".env.bak.*")):
        shutil.copy2(ENV, bak)
        print(f"[backup] 已备份到 {bak.name}")

    set_model(args.model)
    if not args.no_test:
        print("[test] 冒烟测试中…")
        ok = smoke_test(args.model)
        if not ok:
            print("[rollback] 冒烟失败，自动回滚")
            set_model(cur)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
