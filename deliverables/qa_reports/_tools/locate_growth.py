"""定位真正的膨胀源。

关键疑点：传入的 llm 是否真的被使用？（PlainLLM 与 MockLLM 得到完全相同的曲线，
怀疑 llm 参数被忽略、全局 mock 生效。）

测试设计：
1) 传入一个「一旦被调用就抛异常」的 LLM。若历史仍然增长 -> 说明根本没用传入的 llm。
2) 直接 dump 各条消息的角色/长度/前 200 字符，看清到底是什么内容在膨胀。
3) 检查 orchestrator 如何选择 llm 实例。
只读。
"""
import asyncio
import os
import sys
import tempfile
from pathlib import Path

_t = Path(tempfile.mkdtemp(prefix="locate_"))
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

from roleplay.core.emotion.detector import KeywordEmotionDetector  # noqa: E402
from roleplay.core.llm.base import LLMPort  # noqa: E402
from roleplay.core.orchestrator import ChatOrchestrator  # noqa: E402
from roleplay.core.rag.memory import InMemoryVectorStore  # noqa: E402
from roleplay.core.session_memory import SessionMemory  # noqa: E402
from roleplay.models.chat import ChatRequest  # noqa: E402


class ExplodingLLM(LLMPort):
    """一旦被调用就抛异常，用来判断传入的 llm 是否真的被使用。"""

    @property
    def model_name(self):
        return "exploding"

    async def generate(self, **kw):
        raise RuntimeError("EXPLODING_LLM_WAS_CALLED")

    async def generate_stream(self, **kw):
        raise RuntimeError("EXPLODING_LLM_WAS_CALLED")
        yield  # pragma: no cover


print("=" * 74)
print("1) 传入 ExplodingLLM，看它是否被调用 / 历史是否仍增长")
sm = SessionMemory(persist_dir=_t / "s1", max_turns=40)
orch = ChatOrchestrator(llm=ExplodingLLM(), emotion=KeywordEmotionDetector(enabled=True),
                        rag=InMemoryVectorStore(), enable_emotion=True,
                        session_memory=sm, enable_history_summary=False)
for i in range(14):
    try:
        asyncio.run(orch.run(ChatRequest(session_id="exp", message="第%d轮" % i)))
    except Exception as e:  # noqa: BLE001
        print("   第 %d 轮抛出: %s: %s" % (i, type(e).__name__, str(e)[:120]))
        break
h = sm.get_history("exp")
print("   历史: %d 条 / %d 字符" % (len(h), sum(len(m['content']) for m in h)))
if h:
    print("   >>> [CONFIRMED] 传入的 llm 未被使用（历史仍在增长）")
else:
    print("   >>> 传入的 llm 被正常使用")

print()
print("=" * 74)
print("2) 消息构成明细（用模块全局 mock，14 轮）")
sm2 = SessionMemory(persist_dir=_t / "s2", max_turns=40)
orch2 = ChatOrchestrator(llm=None, emotion=KeywordEmotionDetector(enabled=True),
                         rag=InMemoryVectorStore(), enable_emotion=True,
                         session_memory=sm2, enable_history_summary=False)
for i in range(14):
    asyncio.run(orch2.run(ChatRequest(session_id="dump", message="第%d轮" % i)))
h2 = sm2.get_history("dump")
print("   共 %d 条 / %d 字符" % (len(h2), sum(len(m['content']) for m in h2)))
for i, m in enumerate(h2):
    c = m.get("content", "")
    print("   #%-2d %-9s %9d 字符 | %s" % (i, m.get("role"), len(c), c[:150].replace("\n", " ")))

print()
print("=" * 74)
print("3) orchestrator 如何选择 llm 实例")
import inspect  # noqa: E402

src = inspect.getsource(ChatOrchestrator)
for pat in ("self._llm", "llm or", "llm =", "_global", "build_llm"):
    cnt = src.count(pat)
    print("   %-14s 出现 %d 次" % (pat, cnt))
for i, ln in enumerate(src.splitlines(), 1):
    if "_llm" in ln and ("=" in ln) and ("self._llm =" in ln or "llm or" in ln):
        print("      L%d: %s" % (i, ln.strip()[:130]))
