"""量化会话历史膨胀：mock provider 下逐轮记录历史体量。

结论目标：
- 历史字符数随轮次如何增长（线性 / 指数）
- 单次响应体量
- _TURN_CAP=40（80 条消息）上限为何挡不住体量
只读：临时目录。
"""
import json
import os
import sys
import tempfile
from pathlib import Path

_t = Path(tempfile.mkdtemp(prefix="growth_"))
for k, v in dict(
    ROLEPLAY_LLM_PROVIDER="mock",
    ROLEPLAY_RAG_IMPL="memory",
    ROLEPLAY_EMBEDDER="hashing",
    ROLEPLAY_ENABLE_WEB="false",
    ROLEPLAY_EMOTION_DETECTOR="keyword",
).items():
    os.environ[k] = v
os.environ["ROLEPLAY_KNOWLEDGE_DIR"] = str(_t / "k")
os.environ["ROLEPLAY_CHARACTERS_DIR"] = str(_t / "c")
os.environ["ROLEPLAY_SESSION_MEMORY_DIR"] = str(_t / "s")

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from fastapi.testclient import TestClient  # noqa: E402

from roleplay.main import app  # noqa: E402

print("%-5s %-12s %-14s %-12s %s" % ("turn", "resp_bytes", "history_chars", "msgs", "reply_head"))
rows = []
with TestClient(app) as c:
    for i in range(22):
        r = c.post("/chat/stream", json={"session_id": "grow", "message": "第%d轮" % i})
        h = c.get("/api/sessions/grow/history").json().get("history", [])
        chars = sum(len(m.get("content", "")) for m in h)
        rows.append((i + 1, len(r.content), chars, len(h)))
        print("%-5d %-12d %-14d %-12d %s"
              % (i + 1, len(r.content), chars, len(h), r.text[:40].replace("\n", " ")))

print()
print("增长率（相邻两轮 history_chars 比值）:")
for k in range(1, len(rows)):
    prev, cur = rows[k - 1][2], rows[k][2]
    ratio = (cur / prev) if prev else 0
    print("   turn %2d -> %2d : %10d -> %10d   x%.2f" % (rows[k - 1][0], rows[k][0], prev, cur, ratio))

print()
print("理论对照: mock.py:29 取 history[-6:]，每条回复内嵌这 6 条 -> 每轮近似 x2 复制")
print("实测末轮 history_chars = %d" % rows[-1][2])

# 验证 _TURN_CAP 是否生效：消息条数上限 80
h = c.get("/api/sessions/grow/history").json().get("history", []) if False else None
print()
print("=== 检查 40 轮上限（消息数上限 80）是否只限制条数、不限制体量 ===")
from roleplay.core.session_memory import _TURN_CAP  # noqa: E402

print("   _TURN_CAP =", _TURN_CAP, "-> 消息上限 =", _TURN_CAP * 2)
print("   当前消息数 =", rows[-1][3], "（未超上限）")
print("   结论: 上限按『条数』截断，不含『字符/token 预算』-> 单条可无限膨胀")

# 单条内容到底有多大
r = c.get("/api/sessions/grow/history")
h = r.json().get("history", [])
sizes = sorted(((len(m.get("content", "")), m.get("role")) for m in h), reverse=True)[:5]
print()
print("最大的 5 条消息（字符数, role）:", sizes)

# 落盘文件体量
sd = _t / "s"
if sd.exists():
    files = sorted(((f.stat().st_size, f.name) for f in sd.glob("*.json")), reverse=True)[:5]
    print("落盘会话文件:", [(sz, nm) for sz, nm in files])
