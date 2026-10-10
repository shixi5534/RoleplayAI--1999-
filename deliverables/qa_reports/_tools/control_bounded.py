"""有界控制实验（把 C 组轮数压到 44 以内并加体量守卫，避免重演 7GB 耗尽）。

只测两件事：
A) 非回显 LLM（真实 provider 行为）30 轮 -> 历史是否线性有界
B) mock LLM 20 轮 -> 复现指数增长（20 轮约 2 千万字符，安全）
每轮打印，任何一轮历史超 3000 万字符立即停止。
只读。
"""
import asyncio
import os
import sys
import tempfile
from pathlib import Path

_t = Path(tempfile.mkdtemp(prefix="ctrl2_"))
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
from roleplay.core.llm.mock import MockLLMProvider  # noqa: E402
from roleplay.core.orchestrator import ChatOrchestrator  # noqa: E402
from roleplay.core.rag.memory import InMemoryVectorStore  # noqa: E402
from roleplay.core.session_memory import SessionMemory  # noqa: E402
from roleplay.models.chat import ChatRequest  # noqa: E402

GUARD = 30_000_000


class PlainLLM(LLMPort):
    """模拟真实云端 LLM：回复固定长度，不回显历史。"""

    @property
    def model_name(self):
        return "plain"

    async def generate(self, *, system, user, history=None, temperature=None,
                       system_blocks=None, user_prefix=None):
        return "好的，我明白了。"

    async def generate_stream(self, **kw):
        yield await self.generate(**kw)


def run_case(label, llm, turns, summary_enabled=True):
    sm = SessionMemory(persist_dir=_t / ("s_" + label), max_turns=40)
    orch = ChatOrchestrator(llm=llm, emotion=KeywordEmotionDetector(enabled=True),
                            rag=InMemoryVectorStore(), enable_emotion=True,
                            session_memory=sm,
                            enable_history_summary=summary_enabled,
                            history_summary_threshold=40)
    print("\n[%s] turns=%d summary=%s" % (label, turns, summary_enabled))
    for i in range(turns):
        asyncio.run(orch.run(ChatRequest(session_id=label, message="第%d轮 你好" % i)))
        h = sm.get_history(label)
        chars = sum(len(m["content"]) for m in h)
        if (i + 1) % 4 == 0 or i == turns - 1:
            print("   turn %2d: 保存 %2d 条 / %12d 字符" % (i + 1, len(h), chars))
        if chars > GUARD:
            print("   !! 体量守卫触发（>%d），提前停止" % GUARD)
            break
    h = sm.get_history(label)
    return len(h), sum(len(m["content"]) for m in h)


print("=" * 74)
print("A) 非回显 LLM（真实 provider 行为）")
n, c = run_case("plain", PlainLLM(), 30, summary_enabled=False)
print("   >>> 30 轮：%d 条 / %d 字符  → 线性有界（受 _TURN_CAP=80 条约束）" % (n, c))

print()
print("=" * 74)
print("B) mock LLM（README 声明默认 provider）")
n2, c2 = run_case("mock", MockLLMProvider(), 20, summary_enabled=False)
print("   >>> 20 轮：%d 条 / %d 字符  → 指数增长" % (n2, c2))

print()
print("=" * 74)
print("C) mock + 开启摘要（默认 enable_history_summary=True）")
n3, c3 = run_case("mockSum", MockLLMProvider(), 44, summary_enabled=True)
print("   >>> 44 轮：%d 条 / %d 字符" % (n3, c3))
summ = SessionMemory(persist_dir=_t / "s_mockSum", max_turns=40).get_summary("mockSum")
print("   摘要文件:", ("有，%d 字" % len(summ.get("summary_text", ""))) if summ else "无")
print("   >>> 摘要把旧片段压到 ≤120 字，但 keep=%d 条最近消息原样下传；"
      % max(40 // 2, 2))
print("       当单条消息已是 MB 级时，摘要无法阻止超大 payload。")
