"""端到端复验 P0-2 修复：默认配置下跑真实 /chat/stream，确认历史不再指数膨胀。

通过 HTTP 打真实 uvicorn（若有）或直接用 TestClient —— 这里用 TestClient 保证可复现。
同时验证 P0-1：注入 LLM 的独有标记确实出现在回复里。
只读（临时数据目录）。
"""
import os
import sys
import tempfile
from pathlib import Path

_t = Path(tempfile.mkdtemp(prefix="verify_fix_"))
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

from roleplay.core.llm.mock import MockLLMProvider  # noqa: E402
from roleplay.main import app  # noqa: E402

print("=" * 70)
print("A) 默认 mock 下 30 轮对话的历史体量（修复前 22 轮已达 6570 万字符）")
with TestClient(app) as c:
    prev = 0
    ratios = []
    for i in range(30):
        r = c.post("/chat/stream", json={"session_id": "grow", "message": "第%d轮" % i})
        h = c.get("/api/sessions/grow/history").json().get("history", [])
        chars = sum(len(m.get("content", "")) for m in h)
        if prev:
            ratios.append(chars / prev if prev else 0)
        prev = chars
        if (i + 1) % 10 == 0:
            print("   turn %2d: resp=%7d bytes, history=%8d chars, msgs=%d"
                  % (i + 1, len(r.content), chars, len(h)))
    final = prev

print()
print("   末轮历史 = %d 字符" % final)
print("   相邻轮增长率（后几轮）: %s" % ["%.2f" % x for x in ratios[-5:]])
if final < 2_000_000:
    print("   >>> [PASS] 历史体量受控（修复前同轮数量级为千万~亿）")
else:
    print("   >>> [FAIL] 仍在膨胀")

print()
print("B) P0-1 复验：注入标记 LLM 是否真的被使用")
import asyncio  # noqa: E402

from roleplay.core.emotion.detector import KeywordEmotionDetector  # noqa: E402
from roleplay.core.orchestrator import ChatOrchestrator  # noqa: E402
from roleplay.core.rag.memory import InMemoryVectorStore  # noqa: E402
from roleplay.core.session_memory import SessionMemory  # noqa: E402
from roleplay.models.chat import ChatRequest  # noqa: E402

MARK = "【INJECTED-LLM-MARKER】"


class Marked(MockLLMProvider):
    def __init__(self):
        super().__init__()
        self.calls = 0

    async def generate(self, **kw):
        self.calls += 1
        return MARK


llm = Marked()
orch = ChatOrchestrator(llm=llm, emotion=KeywordEmotionDetector(enabled=True),
                        rag=InMemoryVectorStore(), enable_emotion=True,
                        session_memory=SessionMemory(persist_dir=_t / "s2"))
res = asyncio.run(orch.run(ChatRequest(session_id="di", message="你好")))
print("   注入 LLM 调用次数 = %d" % llm.calls)
print("   reply 含标记      = %s" % (MARK in res.response.reply))
print("   >>> %s" % ("[PASS] 依赖注入生效" if (llm.calls > 0 and MARK in res.response.reply)
                     else "[FAIL] 注入仍被忽略"))

print()
print("C) mock 默认不再回显历史（P0-A 根因）")
m = MockLLMProvider()
huge = [{"role": "assistant", "content": "X" * 100_000}]
import inspect  # noqa: E402

out = asyncio.run(m.generate(system="s", user="你好", history=huge))
print("   传入 10 万字符历史，回复长度 = %d" % len(out))
print("   回复是否含历史内容 = %s" % ("X" in out))
print("   >>> %s" % ("[PASS] 默认不回显" if "X" not in out else "[FAIL] 仍在回显"))
print("   构造签名 =", inspect.signature(MockLLMProvider.__init__))
