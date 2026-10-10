"""决定性验证：编排器是否忽略构造函数注入的 LLM（依赖注入失效）。

手法：注入一个输出「独有标记」的 LLM，调用 run()，看返回的 reply 里
是注入 LLM 的标记，还是全局 mock 的「（角色扮演中）」文案。
这同时解释了为什么整套测试都是绿的：测试注入的 mock 与全局 mock 恰好同类。

只读。
"""
import asyncio
import os
import sys
import tempfile
from pathlib import Path

_t = Path(tempfile.mkdtemp(prefix="di_"))
for k, v in dict(
    ROLEPLAY_LLM_PROVIDER="mock",          # 全局 = mock（同 conftest）
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

MARK = "【注入LLM的独有标记-ZQX】"


class MarkedLLM(LLMPort):
    def __init__(self):
        self.called = 0

    @property
    def model_name(self):
        return "marked"

    async def generate(self, *, system, user, history=None, temperature=None,
                       system_blocks=None, user_prefix=None):
        self.called += 1
        return MARK

    async def generate_stream(self, **kw):
        self.called += 1
        yield MARK


llm = MarkedLLM()
sm = SessionMemory(persist_dir=_t / "s", max_turns=40)
orch = ChatOrchestrator(llm=llm, emotion=KeywordEmotionDetector(enabled=True),
                        rag=InMemoryVectorStore(), enable_emotion=True,
                        session_memory=sm, enable_history_summary=False)

res = asyncio.run(orch.run(ChatRequest(session_id="di", message="你好")))
reply = res.response.reply

print("=" * 74)
print("注入 LLM 被调用次数 :", llm.called)
print("返回 reply 前 200 字 :", reply[:200].replace("\n", " "))
print("包含注入标记?       :", MARK in reply)
print("包含 mock 文案?     :", "（角色扮演中）" in reply)
print()
if MARK in reply and llm.called > 0:
    print(">>> [REFUTED] 注入的 LLM 生效，依赖注入正常")
else:
    print(">>> [CONFIRMED] 依赖注入失效：构造函数传入的 llm 被忽略，")
    print("     run() 走 build_llm_from_config(get_settings(), req.llm) → 全局 mock")
    print("     原因: orchestrator.py:852（stream 为 :1048）无条件重建 LLM，")
    print("     从不使用 self._llm（仅 :148 赋值，:669/:708 仅供摘要兜底）。")
    print()
    print("     影响: 测试里注入的 MockLLMProvider 与全局 mock 同类，")
    print("           因此整套测试无法发现该问题（断言实际打在全局 mock 上）。")

print()
print("=" * 74)
print("顺带确认: 全局 mock 的回复会把历史回显进去 → 与历史互相放大")
sm2 = SessionMemory(persist_dir=_t / "s2", max_turns=40)
orch2 = ChatOrchestrator(llm=MarkedLLM(), emotion=KeywordEmotionDetector(enabled=True),
                         rag=InMemoryVectorStore(), enable_emotion=True,
                         session_memory=sm2, enable_history_summary=False)
for i in range(8):
    r = asyncio.run(orch2.run(ChatRequest(session_id="di2", message="第%d轮" % i)))
h = sm2.get_history("di2")
sizes = [len(m["content"]) for m in h if m["role"] == "assistant"]
print("   注入 MarkedLLM 时，8 轮后 assistant 消息长度:", sizes)
print("   -> 若这些长度指数上升，说明回复根本不来自注入的 LLM（而是含历史回显的全局 mock）")
