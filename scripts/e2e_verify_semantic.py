"""端到端验证：用真实 nomic 语义嵌入器跑 /chat/stream，确认 RAG 上下文注入与角色回复质量。

绕过 tests/conftest.py 的 hashing 覆盖，强制使用 Ollama nomic-embed-text。
"""
import json
import os
import sys

# 关键：本脚本不加载 conftest，因此 ROLEPLAY_EMBEDDER 保持默认 ollama
os.environ.setdefault("ROLEPLAY_EMBEDDER", "ollama")

# 将项目根加入路径，保证 `import src.*` 可用
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from fastapi.testclient import TestClient

import src.roleplay.core.orchestrator as orch_mod
from src.roleplay.main import create_app

# 捕获真实注入的 RAG 上下文（monkeypatch 原函数，记录后透传）
captured = {}


def _patched_build_roleplay_prompt(*, card_json, fallback_prompt, default_card,
                                   message, chunks=None, card=None):
    captured["chunks"] = chunks or []
    captured["card_name"] = (card.name if card else None)
    # 调用原始实现
    return orch_mod.build_roleplay_prompt.__wrapped__(
        card_json=card_json, fallback_prompt=fallback_prompt,
        default_card=default_card, message=message, chunks=chunks, card=card,
    )


# 保存原函数并替换（build_roleplay_prompt 是普通函数，无 __wrapped__；改用闭包）
_orig_build = orch_mod.build_roleplay_prompt


def _wrapper(*, card_json, fallback_prompt, default_card, message, chunks=None, card=None):
    captured["chunks"] = chunks or []
    captured["card_name"] = (card.name if card else None)
    return _orig_build(
        card_json=card_json, fallback_prompt=fallback_prompt,
        default_card=default_card, message=message, chunks=chunks, card=card,
    )


orch_mod.build_roleplay_prompt = _wrapper

app = create_app()
client = TestClient(app)

QUERIES = [
    "凯拉是谁？你和她之间发生过什么？",
    "你胸口的发条装置究竟是什么？",
    "克莱因蓝对你来说有什么特别的含义？",
]

for q in QUERIES:
    captured.clear()
    print("\n" + "=" * 70)
    print(f"用户：{q}")
    print("-" * 70)
    payload = {
        "session_id": "e2e_verify_session",
        "message": q,
        "character_id": "wu_ming_zhe",
    }
    with client.stream("POST", "/chat/stream", json=payload) as resp:
        assert resp.status_code == 200, f"HTTP {resp.status_code}"
        reply = []
        emotions = []
        for line in resp.iter_lines():
            if not line:
                continue
            if line.startswith("event: "):
                event = line[len("event: "):].strip()
                continue
            if line.startswith("data: "):
                data = line[len("data: "):]
                if event == "chunk":
                    reply.append(json.loads(data))
                elif event == "emotion":
                    emotions.append(json.loads(data))
                elif event == "done":
                    pass
    # 展示注入的 RAG 上下文（取前 3 条，含来源 section）
    chunks = captured.get("chunks", [])
    print(f"[RAG 注入] 共 {len(chunks)} 块，角色={captured.get('card_name')}")
    for i, c in enumerate(chunks[:4]):
        meta = getattr(c, "metadata", {}) or {}
        sec = meta.get("section") or meta.get("source") or "?"
        score = getattr(c, "score", None)
        txt = (getattr(c, "text", "") or "")[:70].replace("\n", " ")
        score_s = f"{score:.3f}" if isinstance(score, (int, float)) else str(score)
        print(f"  #{i+1} score={score_s} section={sec[:40]}")
        print(f"       {txt}...")
    print(f"[情绪] {emotions}")
    print(f"[回复] {''.join(reply)}")
    print("=" * 70)
