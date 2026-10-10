"""第四轮：SSRF 正确签名复现 + 历史全量喂给 LLM 的确认。只读。"""
import inspect
import os
import sys
import tempfile
from pathlib import Path

_t = Path(tempfile.mkdtemp(prefix="verify4_"))
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

print("=" * 72)
print("1) SSRF：LLMOverride 从哪来 + build_llm_from_config 是否放行内网")
try:
    from roleplay.core.llm import factory as F

    print("   factory 可用名:", [n for n in vars(F) if "Override" in n or n.startswith("build")])
    LLMOverride = getattr(F, "LLMOverride", None)
    print("   LLMOverride:", LLMOverride)
    if LLMOverride is not None:
        print("   fields:", list(getattr(LLMOverride, "model_fields", {}) or
                                getattr(LLMOverride, "__dataclass_fields__", {})))
    targets = [
        "http://169.254.169.254/latest/meta-data",
        "http://127.0.0.1:11434",
        "http://192.168.1.1",
        "http://10.0.0.1:8080",
        "https://evil.example.com/v1",
    ]
    accepted, rejected = [], []
    for t in targets:
        try:
            ov = LLMOverride(provider="openai", model="gpt-x", base_url=t, api_key="k")
            port, used_global = F.build_llm_from_config(None, ov)
            accepted.append((t, type(port).__name__, used_global))
        except Exception as e:  # noqa: BLE001
            rejected.append((t, "%s: %s" % (type(e).__name__, str(e)[:80])))
    print("   ACCEPTED:")
    for t, cls, g in accepted:
        print("      %-46s -> %-20s used_global=%s" % (t, cls, g))
    print("   REJECTED:")
    for t, w in rejected:
        print("      %-46s -> %s" % (t, w))
    internal = [t for t, _, _ in accepted if any(x in t for x in ("169.254", "127.0.0.1", "192.168", "10.0."))]
    print("   >>> %s：%d 个内网地址被接受" %
          ("[CONFIRMED] SSRF 校验缺失" if internal else "[REFUTED]", len(internal)))
except Exception as e:  # noqa: BLE001
    print("   失败:", repr(e))

print()
print("=" * 72)
print("2) 是否有 token/字符预算截断（历史全量喂 LLM？）")
try:
    from roleplay.core import orchestrator as O

    src = inspect.getsource(O)
    print("   orchestrator 中出现的关键词计数:")
    for kw in ("token_budget", "max_chars", "truncate", "max_history", "budget",
               "history[:", "history[-", "summar"):
        print("      %-16s %d" % (kw, src.count(kw)))

    from roleplay.core.session_memory import SessionMemory

    print("   SessionMemory 签名:", inspect.signature(SessionMemory.__init__))
    sm_src = inspect.getsource(SessionMemory)
    print("   session_memory 中 token/字符预算关键词:")
    for kw in ("token", "budget", "max_chars", "len(content)"):
        print("      %-16s %d" % (kw, sm_src.count(kw)))
except Exception as e:  # noqa: BLE001
    print("   失败:", repr(e))

print()
print("=" * 72)
print("3) 历史是否原样传给 LLM（拦截 generate 参数实测）")
try:
    import asyncio

    from roleplay.core.emotion.detector import KeywordEmotionDetector
    from roleplay.core.llm.base import LLMPort
    from roleplay.core.orchestrator import ChatOrchestrator
    from roleplay.core.rag.memory import InMemoryVectorStore
    from roleplay.core.session_memory import SessionMemory

    seen = {}

    class Spy(LLMPort):
        @property
        def model_name(self):
            return "spy"

        async def generate(self, *, system, user, history=None, temperature=None,
                           system_blocks=None, user_prefix=None):
            seen["history_len"] = len(history or [])
            seen["history_chars"] = sum(len(h.get("content", "")) for h in (history or []))
            seen["user"] = user
            return "好的。" + ("啊" * 400)

        async def generate_stream(self, **kw):
            yield await self.generate(**kw)

    sm = SessionMemory(persist_dir=_t / "s2", max_turns=40)
    orch = ChatOrchestrator(llm=Spy(), emotion=KeywordEmotionDetector(enabled=True),
                            rag=InMemoryVectorStore(), enable_emotion=True,
                            session_memory=sm)
    for i in range(6):
        asyncio.run(orch.chat(session_id="spy", message="第%d轮" % i))
    print("   末轮送给 LLM 的 history: %d 条 / %d 字符"
          % (seen.get("history_len", -1), seen.get("history_chars", -1)))
    h = sm.get_history("spy")
    print("   会话内实际保存: %d 条 / %d 字符"
          % (len(h), sum(len(m["content"]) for m in h)))
    full = seen.get("history_chars", 0) >= sum(len(m["content"]) for m in h) * 0.9
    print("   >>> %s：历史几乎全量喂给 LLM（无字符/token 预算裁剪）"
          % ("[CONFIRMED]" if full else "[PARTIAL]"))
except Exception as e:  # noqa: BLE001
    import traceback
    print("   失败:", repr(e))
    traceback.print_exc()
