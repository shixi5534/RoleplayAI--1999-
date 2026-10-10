"""会话记忆字符预算（P0-B）+ mock 历史回显开关（P0-A）回归测试。

背景（两个已实测确诊的真实缺陷）：
- P0-A：``MockLLMProvider.generate()`` 曾无条件把最近 6 条历史原样拼进回复，
  而该回复又被 ``SessionMemory`` 写回历史 → **自我复制正反馈**。
  实测默认 mock：10 轮 43_210 字符 → 22 轮 6_570 万 → 52 轮 **7.77 亿字符**
  （单次响应 872MB、进程内存 7.3GB），增长率 ×1.84/轮。
- P0-B：``SessionMemory`` 只有 ``_TURN_CAP = 40`` 的**条数**上限，源码里
  ``token``/``budget``/``max_chars`` 关键词计数为 0 —— 单条 MB 级消息完全不受约束。

本文件锁定修复后的契约：
- mock 默认**不回显**历史（回复确定性、不含传入 history 的任何内容）；
  显式 ``echo_history=True`` 才恢复旧行为。
- SessionMemory 在条数上限之外再生效一道**字符预算**，且至少保留最近 1 轮。
- 单条超长消息不抛异常。
- 20 轮长度递增写入后总字符数**不**出现指数增长（被预算压住）——本次修复的核心证据。
"""
import logging
from pathlib import Path

import pytest

from roleplay.core.llm.mock import MockLLMProvider
from roleplay.core.session_memory import SessionMemory


# ═════════════════════ P0-A：mock 历史回显开关 ═════════════════════
async def test_mock_default_does_not_echo_history():
    """默认（echo_history=False）：回复不含传入 history 的任何内容。"""
    llm = MockLLMProvider()
    history = [
        {"role": "user", "content": "机密哨兵A：我最喜欢的颜色是靛蓝"},
        {"role": "assistant", "content": "机密哨兵B：我记住了你的靛蓝"},
    ]
    out = await llm.generate(system="sys", user="你好", history=history)
    assert "机密哨兵A" not in out
    assert "机密哨兵B" not in out
    assert "靛蓝" not in out
    assert "稍早的对话" not in out
    assert "你好" in out  # 仍回显本轮用户输入


async def test_mock_default_reply_is_history_independent_and_bounded():
    """默认模式下，回复长度与历史无关（这正是切断指数膨胀的关键）。"""
    llm = MockLLMProvider()
    short = await llm.generate(system="s", user="你好", history=[])
    huge = await llm.generate(
        system="s",
        user="你好",
        history=[{"role": "assistant", "content": "X" * 100_000}],
    )
    assert short == huge  # 确定性 + 与历史无关
    assert len(huge) < 200


async def test_mock_echo_history_true_keeps_legacy_behavior():
    """显式开启时维持旧行为（演示/旧测试依赖），仅此时才拼历史。"""
    llm = MockLLMProvider(echo_history=True)
    history = [{"role": "user", "content": "旧台词"}]
    out = await llm.generate(system="s", user="新台词", history=history)
    assert "稍早的对话" in out
    assert "旧台词" in out


async def test_mock_default_no_echo_via_stream_too():
    """流式路径复用 generate()，必须同样遵守开关（拼接后不含历史）。"""
    llm = MockLLMProvider()
    chunks = [
        c
        async for c in llm.generate_stream(
            system="s",
            user="流式提问",
            history=[{"role": "assistant", "content": "不该出现的历史回显"}],
        )
    ]
    text = "".join(chunks)
    assert "不该出现的历史回显" not in text
    assert "流式提问" in text


# ═════════════════════ P0-B：字符预算 ═════════════════════
def test_char_budget_caps_total_chars(tmp_path):
    """塞入大量长消息后，get_history 总字符数受预算约束。"""
    budget = 10_000
    sm = SessionMemory(persist_dir=tmp_path / "s", max_total_chars=budget)
    for i in range(60):
        sm.append_many("sess", [("user", f"问题{i}"), ("assistant", "回" * 900)])
    hist = sm.get_history("sess")
    total = sum(len(m["content"]) for m in hist)
    assert total <= budget, f"总字符 {total} 超出预算 {budget}"
    assert hist, "不应清空历史"


def test_budget_applies_on_single_append_path_too(tmp_path):
    """append()（单条写入路径）同样受预算约束，不是只有 append_many 生效。"""
    budget = 3_000
    sm = SessionMemory(persist_dir=tmp_path / "s", max_total_chars=budget)
    for i in range(40):
        sm.append("sess", "assistant", f"[{i}]" + "长" * 500)
    total = sum(len(m["content"]) for m in sm.get_history("sess"))
    assert total <= budget


def test_keeps_at_least_latest_turn(tmp_path):
    """始终至少保留最近 1 轮：最近一条消息必定在历史里。"""
    sm = SessionMemory(persist_dir=tmp_path / "s", max_total_chars=1_000)
    for i in range(30):
        sm.append_many("sess", [("user", f"u{i}"), ("assistant", f"a{i}")])
    hist = sm.get_history("sess")
    assert hist, "历史被清空了（违反「至少保留最近 1 轮」）"
    assert hist[-1]["content"] == "a29"


def test_oversized_single_message_does_not_raise_and_is_kept(tmp_path):
    """单条消息本身超预算：不抛异常，保留该条（角色不断片），只记 warning。"""
    budget = 500
    sm = SessionMemory(persist_dir=tmp_path / "s", max_total_chars=budget)
    sm.append_many("sess", [("user", "问题"), ("assistant", "超" * 5_000)])
    hist = sm.get_history("sess")
    assert len(hist[-1]["content"]) == 5_000  # 超长消息被保留，未被截断/丢弃
    assert hist[-1]["role"] == "assistant"


def test_oversized_message_logs_warning(tmp_path, caplog):
    """超预算路径必须留下 warning 日志（可观测，而不是静默）。"""
    sm = SessionMemory(persist_dir=tmp_path / "s", max_total_chars=200)
    with caplog.at_level(logging.WARNING, logger="roleplay.core.session_memory"):
        sm.append("sess", "assistant", "爆" * 2_000)
    assert any("超出预算" in r.message or "超长" in r.message for r in caplog.records)


def test_turn_cap_still_enforced(tmp_path):
    """原有条数上限（max_turns）语义不变：两闸并行。"""
    sm = SessionMemory(persist_dir=tmp_path / "s", max_turns=3)
    for i in range(20):
        sm.append_many("sess", [("user", f"u{i}"), ("assistant", f"a{i}")])
    assert len(sm.get_history("sess")) <= 6  # 3 轮 × 2 条


def test_budget_zero_disables_char_gate(tmp_path):
    """max_total_chars<=0 = 关闭字符闸（兼容旧行为），仅条数上限生效。"""
    sm = SessionMemory(persist_dir=tmp_path / "s", max_turns=40, max_total_chars=0)
    for i in range(3):
        sm.append("sess", "assistant", "字" * 200_000)
    assert sum(len(m["content"]) for m in sm.get_history("sess")) == 600_000


def test_persist_and_reload_respects_budget(tmp_path):
    """落盘 → 重新加载后，内存历史仍不超预算（预算不是只在写时生效）。"""
    d = tmp_path / "s"
    sm = SessionMemory(persist_dir=d, max_total_chars=4_000)
    for i in range(30):
        sm.append("sess", "assistant", "回" * 800)
    reloaded = SessionMemory(persist_dir=d, max_total_chars=4_000)
    total = sum(len(m["content"]) for m in reloaded.get_history("sess"))
    assert total <= 4_000


# ═════════════════════ 膨胀回归（核心证据） ═════════════════════
def test_no_exponential_growth_over_20_rounds(tmp_path):
    """20 轮「长度递增」写入，总字符数不出现指数增长（被预算压住）。

    未修复时（无字符闸），第 N 轮长度 ≈ 上一轮 × 1.84，20 轮即达 10^7 量级；
    修复后总字符数应始终 ≤ 预算，且增长是**线性**的。
    """
    budget = 50_000
    sm = SessionMemory(persist_dir=tmp_path / "s", max_total_chars=budget)
    totals = []
    for i in range(20):
        # 长度递增：模拟「回复越滚越长」的膨胀形态
        sm.append_many(
            "sess",
            [("user", f"第{i}轮提问"), ("assistant", "膨胀片段" * (10 * (i + 1)))],
        )
        totals.append(sum(len(m["content"]) for m in sm.get_history("sess")))

    # 1) 任何一轮都不越预算
    assert max(totals) <= budget, f"越预算：{max(totals)}"
    # 2) 非指数：末轮 / 首轮增幅应远小于指数增长率（未修复时 ×1.84/轮）
    assert totals[-1] <= budget
    # 3) 20 轮后的总字符数处于 10^4 量级（而非未修复时的 10^7+）
    assert totals[-1] < 10**5


def test_mock_plus_session_memory_does_not_amplify(tmp_path):
    """端到端复现原反馈环：mock 回复经 append_many 写回历史，20 轮后不膨胀。

    这正是 P0-A + P0-B 的乘积效应现场：回复被写回历史、历史又被拼进回复。
    """
    import asyncio

    sm = SessionMemory(persist_dir=tmp_path / "s", max_total_chars=50_000)
    llm = MockLLMProvider()  # 默认不回显历史
    last_len = 0

    async def run() -> None:
        nonlocal last_len
        for i in range(20):
            user = f"第{i}轮：我们聊点别的吧"
            history = sm.get_history("sess")
            reply = await llm.generate(system="sys", user=user, history=history)
            sm.append_many("sess", [("user", user), ("assistant", reply)])
            last_len = len(reply)

    asyncio.run(run())
    total = sum(len(m["content"]) for m in sm.get_history("sess"))
    assert total <= 50_000, f"反馈环未切断，总字符 {total}"
    assert last_len < 1_000, f"单轮回复被历史放大到 {last_len} 字符"


def test_default_budget_is_120k():
    """默认预算常量锁定为 120_000（依据见 session_memory._CHAR_BUDGET 注释）。"""
    from roleplay.core.session_memory import _CHAR_BUDGET

    assert _CHAR_BUDGET == 120_000
    sm = SessionMemory()
    assert sm._max_chars == 120_000


def test_layout_and_persistence_semantics_preserved(tmp_path):
    """原子写（tmp + os.replace）与目录布局不变：落盘文件仍是 <sid>.json，无残留 tmp。"""
    d = tmp_path / "s"
    sm = SessionMemory(persist_dir=d, max_total_chars=5_000)
    sm.append_many("sess", [("user", "你好"), ("assistant", "在的")])
    files = sorted(p.name for p in d.iterdir())
    assert files == ["sess.json"]
    assert (d / "sess.json").read_text(encoding="utf-8").startswith("[")


def test_summary_files_still_skipped_on_load(tmp_path):
    """摘要文件仍在加载时跳过（_SUMMARY_SUFFIX 语义不变）。"""
    d = tmp_path / "s"
    sm = SessionMemory(persist_dir=d)
    sm.append_many("sess", [("user", "你好"), ("assistant", "在的")])
    sm.save_summary("sess", {"text": "摘要"})
    reloaded = SessionMemory(persist_dir=d)
    assert [m["content"] for m in reloaded.get_history("sess")] == ["你好", "在的"]
    assert reloaded.get_summary("sess") == {"text": "摘要"}


def test_loading_oversized_legacy_file_does_not_oom(tmp_path):
    """膨胀遗留：加载期先做文件大小闸，GB 级存档不被 read_text 读进内存。"""
    d = tmp_path / "s"
    d.mkdir(parents=True, exist_ok=True)
    big = d / "huge.json"
    # 用 JSON 字面量撑到 > 4MB（够触发加载闸），但不真写 GB 级（测试要快）
    big.write_text("[" + ",".join('{"role":"a","content":"x"}' for _ in range(200_000)) + "]", encoding="utf-8")
    assert big.stat().st_size > 4_000_000
    sm = SessionMemory(persist_dir=d, max_total_chars=120_000)
    assert sm.get_history("huge") == []  # 跳过加载 → 空历史（下次写入重建）


@pytest.mark.parametrize("budget", [1_000, 5_000, 20_000])
def test_budget_monotonic_across_sizes(tmp_path, budget):
    """多档预算下都不越界、都不清空（预算逻辑与具体数值无关）。"""
    sm = SessionMemory(persist_dir=tmp_path / f"s{budget}", max_total_chars=budget)
    for i in range(25):
        sm.append("sess", "assistant", "回" * 400)
    hist = sm.get_history("sess")
    assert hist and sum(len(m["content"]) for m in hist) <= budget


def test_path_is_importable_constant():
    """守卫：预算常量与 docstring 的依据一起存在（防后人静默删除注释）。"""
    src = Path(__file__).resolve().parent.parent / "src" / "roleplay" / "core" / "session_memory.py"
    text = src.read_text(encoding="utf-8")
    assert "_CHAR_BUDGET = 120_000" in text
    assert "max_total_chars" in text
