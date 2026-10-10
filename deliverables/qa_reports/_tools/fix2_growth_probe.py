"""Growth probe: pre/post fix measurement of the mock x SessionMemory feedback loop.

Run:  .\\.venv\\Scripts\\python.exe deliverables\\qa_reports\\_tools\\fix2_growth_probe.py

Measured (2026-07-27, this repo):
  PRE-FIX (echo=True, no budget):           22 轮 74,287,556 字符
  mock fixed only (echo=False, no budget):  52 轮 1,880 字符
  POST-FIX (echo=False, budget=120k):       52 轮 1,880 字符
  POST-FIX (echo=True, budget=120k):        52 轮 120,965 字符（越界仅因单条超长）
"""
import asyncio
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))
from roleplay.core.llm.mock import MockLLMProvider  # noqa: E402
from roleplay.core.session_memory import SessionMemory  # noqa: E402


def run(n, echo, max_chars, label):
    d = Path(tempfile.mkdtemp(prefix="growth_"))
    sm = SessionMemory(persist_dir=d, max_total_chars=max_chars)
    llm = MockLLMProvider(echo_history=echo)
    out = []

    async def go():
        for i in range(n):
            h = sm.get_history("s")
            r = await llm.generate(system="sys", user=f"第{i}轮用户输入", history=h)
            sm.append_many("s", [("user", f"第{i}轮用户输入"), ("assistant", r)])
            out.append(sum(len(m["content"]) for m in sm.get_history("s")))

    asyncio.run(go())
    print(
        f"{label}: n={n} totals@1,6,10,22 = "
        + ", ".join(str(out[j - 1]) for j in (1, 6, 10, 22) if j <= n)
        + f" | final={out[-1]}"
    )


run(22, True, 0, "PRE-FIX (echo=True, no budget)")
run(52, False, 0, "mock fixed only (echo=False, no budget)")
run(52, False, 120_000, "POST-FIX (echo=False, budget=120k)")
run(52, True, 120_000, "POST-FIX full (echo=True, budget=120k)")
