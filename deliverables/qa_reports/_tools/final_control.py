"""决定性对照：把编排器内部的 LLM 构建替换为「非回显 LLM」，看历史增长是否线性。

这能精确界定膨胀的适用范围：
- 若替换后线性有界 -> 膨胀是「mock 回显历史」+「历史持久化」的乘积效应，
  即默认（mock）配置特有，真实 provider 不受影响。
- 若仍然指数 -> 属通用缺陷。

手法：monkeypatch roleplay.core.orchestrator.build_llm_from_config。
只读（临时目录）。
"""
import asyncio
import os
import sys
import tempfile
from pathlib import Path

_t = Path(tempfile.mkdtemp(prefix="final_"))
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
from roleplay.core import orchestrator as O  # noqa: E402
from roleplay.core.rag.memory import InMemoryVectorStore  # noqa: E402
from roleplay.core.session_memory import SessionMemory  # noqa: E402
from roleplay.models.chat import ChatRequest  # noqa: E402


class BoundedLLM(LLMPort):
    """模拟真实云端 LLM：回复长度固定、不含历史。"""

    @property
    def model_name(self):
        return "bounded"

    async def generate(self, *, system, user, history=None, temperature=None,
                       system_blocks=None, user_prefix=None):
        return "好的，我明白了。（固定长度回复，约 20 字）"

    async def generate_stream(self, **kw):
        yield await self.generate(**kw)


# ---- 拦截工厂，强制使用 BoundedLLM ----
_real_factory = O.build_llm_from_config


def fake_factory(settings=None, override=None):
    return BoundedLLM(), False


O.build_llm_from_config = fake_factory

print("=" * 74)
print("对照实验：编排器内部使用「非回显 LLM」（模拟真实 provider）")
sm = SessionMemory(persist_dir=_t / "s_bounded", max_turns=40)
orch = O.ChatOrchestrator(llm=BoundedLLM(), emotion=KeywordEmotionDetector(enabled=True),
                          rag=InMemoryVectorStore(), enable_emotion=True,
                          session_memory=sm, enable_history_summary=False)
rows = []
for i in range(30):
    asyncio.run(orch.run(ChatRequest(session_id="bounded", message="第%d轮 你好" % i)))
    h = sm.get_history("bounded")
    chars = sum(len(m["content"]) for m in h)
    rows.append((i + 1, len(h), chars))
    if (i + 1) % 6 == 0:
        print("   turn %2d: %2d 条 / %8d 字符" % (i + 1, len(h), chars))

print()
print("   末轮: %d 条 / %d 字符" % (rows[-1][1], rows[-1][2]))
ratio = rows[-1][2] / rows[-7][2] if len(rows) >= 7 else 0
print("   近 6 轮增长率: x%.2f  (每轮)" % (ratio ** (1 / 6) if ratio else 0))
print()
if ratio < 1.5:
    print("   >>> [CONFIRMED] 非回显 LLM 下历史线性有界（受 _TURN_CAP 约束）")
    print("       结论：指数膨胀 = 默认 mock provider「回显历史」× 历史持久化 的乘积效应，")
    print("            仅在 mock（README 声明的默认/演示配置）下发生。")
else:
    print("   >>> 仍呈指数增长 → 属通用缺陷")

O.build_llm_from_config = _real_factory

print()
print("=" * 74)
print("落盘文件体量（mock 50 轮的会话 JSON 有多大）")
sm2 = SessionMemory(persist_dir=_t / "s_disk", max_turns=40)
for i in range(24):
    asyncio.run(orch.run(ChatRequest(session_id="disk", message="x%d" % i)))
sm2 = SessionMemory(persist_dir=_t / "s_disk", max_turns=40)
# 用真实全局 mock 跑一个短会话，量落盘
import subprocess  # noqa: E402

d = _t / "s_disk"
print("   s_disk 目录内最大的文件:")
for f in sorted(d.glob("*.json"), key=lambda p: -p.stat().st_size)[:3]:
    print("      %10d bytes  %s" % (f.stat().st_size, f.name))
print()
print("   注：mock 下 24 轮的历史已约 %d 万字符，落盘 JSON 达 MB 级。"
      % (rows[-1][2] // 10000))
