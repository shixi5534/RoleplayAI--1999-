"""控制实验：区分「mock 自放大」与「通用缺 token 预算」。

A) 非回显 LLM（真实 provider 行为）-> 历史增长是否线性有界
B) mock LLM（回显历史）-> 指数增长（复现）
C) 摘要阈值启用后，摘要能否挡住膨胀（keep=20 条中的巨块是否仍全量下传）
只读。
"""
import asyncio
import os
import sys
import tempfile
from pathlib import Path

_t = Path(tempfile.mkdtemp(prefix="ctrl_"))
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


class PlainLLM(LLMPort):
    """模拟真实云端 LLM：不把历史回显进回复。"""

    @property
    def model_name(self):
        return "plain"

    async def generate(self, *, system, user, history=None, temperature=None,
                       system_blocks=None, user_prefix=None):
        return "好的，我明白了。"  # 固定长度，不含历史

    async def generate_stream(self, **kw):
        yield await self.generate(**kw)


class Spy(LLMPort):
    """记录每次实际下传给 LLM 的 history 体量。"""

    def __init__(self, inner):
        self.inner = inner
        self.calls = []

    @property
    def model_name(self):
        return self.inner.model_name

    async def generate(self, *, system, user, history=None, temperature=None,
                       system_blocks=None, user_prefix=None):
        self.calls.append((len(history or []), sum(len(h.get("content", "")) for h in (history or [])),
                           len(user or "")))
        return await self.inner.generate(system=system, user=user, history=history,
                                         temperature=temperature, system_blocks=system_blocks,
                                         user_prefix=user_prefix)

    async def generate_stream(self, **kw):
        yield await self.generate(**kw)


def run_case(label, llm, turns, summary_enabled=True):
    sm = SessionMemory(persist_dir=_t / ("s_" + label), max_turns=40)
    spy = Spy(llm)
    orch = ChatOrchestrator(llm=spy, emotion=KeywordEmotionDetector(enabled=True),
                            rag=InMemoryVectorStore(), enable_emotion=True,
                            session_memory=sm,
                            enable_history_summary=summary_enabled,
                            history_summary_threshold=40)
    from roleplay.models.chat import ChatRequest

    print("\n[%s] turns=%d summary=%s" % (label, turns, summary_enabled))
    for i in range(turns):
        asyncio.run(orch.run(ChatRequest(session_id=label, message="第%d轮 你好" % i)))
        if (i + 1) % 5 == 0 or i == turns - 1:
            h = sm.get_history(label)
            chars = sum(len(m["content"]) for m in h)
            dl, dc, du = spy.calls[-1] if spy.calls else (-1, -1, -1)
            print("   turn %2d: 保存 %2d条/%9d字符 | 本次下传LLM %2d条/%9d字符"
                  % (i + 1, len(h), chars, dl, dc))
    return sm, spy


print("=" * 74)
print("A) 非回显 LLM（真实 provider 行为）：历史增长是否有界")
sm, spy = run_case("plain", PlainLLM(), 30, summary_enabled=False)
h = sm.get_history("plain")
print("   >>> 30 轮后 %d 条 / %d 字符（线性，受 _TURN_CAP=80 条约束）"
      % (len(h), sum(len(m["content"]) for m in h)))

print()
print("=" * 74)
print("B) mock LLM（README 声明的默认 provider）：是否指数增长")
sm2, spy2 = run_case("mock", MockLLMProvider(), 22, summary_enabled=False)
h2 = sm2.get_history("mock")
print("   >>> 22 轮后 %d 条 / %d 字符" % (len(h2), sum(len(m["content"]) for m in h2)))

print()
print("=" * 74)
print("C) 开启摘要（默认 enable_history_summary=True）能否挡住 mock 膨胀")
sm3, spy3 = run_case("mockSum", MockLLMProvider(), 46, summary_enabled=True)
h3 = sm3.get_history("mockSum")
tot = sum(len(m["content"]) for m in h3)
print("   >>> 46 轮后 保存 %d 条 / %d 字符" % (len(h3), tot))
print("   末次下传 LLM: %d 条 / %d 字符" % (spy3.calls[-1][0], spy3.calls[-1][1]))
sizes = sorted((len(m["content"]) for m in h3), reverse=True)[:3]
print("   最大三条消息字符数:", sizes)
summ = sm3.get_summary("mockSum")
print("   摘要文件: %s" % (("有，%d 字" % len(summ.get("summary_text", ""))) if summ else "无"))
print()
print("   >>> 结论: 摘要把『旧片段』压成 ≤120 字，但 keep=20 条『最近消息』原样下传；")
print("       当单条消息本身已达 MB 级时，摘要无法阻止超大 payload 进入 LLM 与响应。")
