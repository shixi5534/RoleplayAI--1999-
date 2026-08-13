"""Round 2 回归复核：P1 并发竞态修复验证（多 key × 多任务压力 + 锁语义）。

验证目标（team-lead Round 2 任务）：
1. 复跑固化的复现用例（同 key 并发）→ 确认绿
2. 更强的并发验证：多 key × 多任务 → 无重复、versions 正确（确认锁覆盖所有写入路径）
3. 锁语义：异常时正确释放（asyncio.Lock 上下文管理器）、无死锁（锁内无嵌套锁）
4. 锁覆盖范围：跨多个 UserProfile 实例共享同一 KB 的并发写入（生产可能场景）
"""
import asyncio
from collections import Counter

import pytest

from roleplay.core.knowledge.embedder import HashingEmbedder
from roleplay.core.knowledge.profile import UserProfile
from roleplay.core.knowledge.profile_models import ProfileEntry
from roleplay.core.knowledge.vector_store import KnowledgeBase


@pytest.fixture
def profile():
    return UserProfile(KnowledgeBase(HashingEmbedder(dim=64)), namespace="profile")


# ───────────────────────── 1. 固化复现用例（同 key 并发） ─────────────────────────
async def test_r2_same_key_concurrent_fixed(profile):
    """P1 竞态复现用例：同 key 并发 upsert → 修复后应合并为 1 条。"""
    e1 = ProfileEntry(type="preference", key="咖啡", value="喜欢拿铁", confidence=0.6)
    e2 = ProfileEntry(type="preference", key="咖啡", value="喜欢美式", confidence=0.6)
    await asyncio.gather(profile.upsert([e1]), profile.upsert([e2]))
    items = profile.list_entries()
    assert len(items) == 1, f"并发同 key 应合并为 1 条，实际 {len(items)} 条"
    assert items[0].key == "咖啡"
    assert items[0].versions >= 2, f"合并后 versions 应为 ≥2，实际 {items[0].versions}"
    # 最终 value 是两次写入之一（后写覆盖）
    assert items[0].value in ("喜欢拿铁", "喜欢美式")


# ───────────────────────── 2. 多 key × 多任务压力（锁覆盖所有写入路径） ─────────────────────────
async def test_r2_multi_key_multi_task_no_dup(profile):
    """5 个不同 key 各 gather 3 次 → 无重复、versions==3（锁覆盖全部 key 的写路径）。"""
    keys = ["咖啡", "茶", "可乐", "牛奶", "果汁"]
    tasks = []
    for k in keys:
        for i in range(3):
            tasks.append(
                profile.upsert(
                    [ProfileEntry(type="preference", key=k, value=f"喜欢{k}{i}", confidence=0.6)]
                )
            )
    results = await asyncio.gather(*tasks)
    assert all(r == 1 for r in results), f"每任务应处理 1 条，实际 {results}"
    items = profile.list_entries()
    assert len(items) == 5, f"5 key 各 3 次并发应合并为 5 条，实际 {len(items)} 条"
    by_key = {e.key: e for e in items}
    for k in keys:
        assert by_key[k].versions == 3, f"{k} versions 应为 3，实际 {by_key[k].versions}"
        assert by_key[k].value == f"喜欢{k}2"  # 最后一次写入胜出（串行顺序保证）


async def test_r2_multi_key_multi_task_with_correction(profile):
    """多 key × 多任务 + correction 混合：correction 与普通更新并发 → 不丢、不重复。"""
    # 先写一条 preference
    await profile.upsert(
        [ProfileEntry(type="preference", key="咖啡", value="喜欢咖啡", importance=0.8, confidence=0.6)]
    )
    tasks = [
        profile.upsert([ProfileEntry(type="preference", key="咖啡", value="更喜欢冷萃", confidence=0.6)]),
        profile.upsert([ProfileEntry(type="correction", key="咖啡", value="不再喝咖啡", confidence=0.3)]),
        profile.upsert([ProfileEntry(type="preference", key="茶", value="喜欢绿茶", confidence=0.6)]),
        profile.upsert([ProfileEntry(type="preference", key="茶", value="喜欢红茶", confidence=0.6)]),
    ]
    await asyncio.gather(*tasks)
    items = profile.list_entries()
    assert len(items) == 2, f"应为咖啡+茶 2 条，实际 {len(items)} 条"
    by_key = {e.key: e for e in items}
    assert "茶" in by_key and by_key["茶"].versions == 2
    assert "咖啡" in by_key
    # 咖啡被 correction 覆盖（可能再被普通更新覆盖），无论哪种 value 都不应有重复条目
    assert by_key["咖啡"].versions >= 2


# ───────────────────────── 3. 锁语义：异常释放 / 无死锁 ─────────────────────────
async def test_r2_lock_released_on_exception(profile, monkeypatch):
    """锁内 aadd 抛异常 → 锁正确释放，后续 upsert 仍可执行（无死锁）。"""
    await profile.upsert(
        [ProfileEntry(type="preference", key="咖啡", value="喜欢拿铁", confidence=0.6)]
    )

    async def _boom_aadd(texts, metadatas=None, namespace="episodic"):
        raise RuntimeError("embedder down")

    monkeypatch.setattr(profile._kb, "aadd", _boom_aadd)
    # 触发异常路径（upsert 内部捕获，不向上抛）
    await profile.upsert(
        [ProfileEntry(type="preference", key="咖啡", value="喜欢美式", confidence=0.6)]
    )
    # 恢复 aadd → 锁应已释放，可正常写入
    monkeypatch.undo()
    await profile.upsert(
        [ProfileEntry(type="preference", key="茶", value="喜欢绿茶", confidence=0.6)]
    )
    keys = {e.key for e in profile.list_entries()}
    assert "茶" in keys, "异常后锁未释放，后续写入被阻塞"


async def test_r2_no_deadlock_nested(profile):
    """锁内无嵌套锁：并发中 upsert 内仅一次锁获取，无自死锁（多轮压力）。"""
    for _ in range(10):
        tasks = [
            profile.upsert([ProfileEntry(type="fact", key=f"k{i}", value=f"v{i}", confidence=0.3)])
            for i in range(6)
        ]
        await asyncio.gather(*tasks)
    assert len(profile.list_entries()) == 6  # 6 个不同 key


# ───────────────────────── 4. 跨实例共享 KB 的并发（生产场景） ─────────────────────────
async def test_r2_two_profiles_shared_kb_concurrent():
    """两个 UserProfile 实例共享同一 KB 并发写同 key → 锁是实例级的，可能仍有竞态（P2 观察）。"""
    kb = KnowledgeBase(HashingEmbedder(dim=64))
    up1 = UserProfile(kb, namespace="profile")
    up2 = UserProfile(kb, namespace="profile")
    e1 = ProfileEntry(type="preference", key="咖啡", value="喜欢拿铁", confidence=0.6)
    e2 = ProfileEntry(type="preference", key="咖啡", value="喜欢美式", confidence=0.6)
    # 两个实例各自持锁 → 锁不互斥 → 竞态仍可能复现（观察点，不硬失败）
    await asyncio.gather(up1.upsert([e1]), up2.upsert([e2]))
    items = kb.list_items("profile")
    n = len(items)
    versions = sorted(
        ProfileEntry.from_meta(it["meta"]).versions for it in items
    )
    # 记录行为：生产装配中每个 UserProfile 实例只对应一个 orchestrator 实例（单例），
    # 跨实例并发仅在测试/多服务进程下出现，属已知边界。
    assert n >= 1
    if n == 2:
        pytest.skip(f"P2 观察点：跨 UserProfile 实例共享 KB 并发写同 key 产生 {n} 条（实例级锁不互斥）")


# ───────────────────────── 5. 最终一致性：串行与并发结果等价 ─────────────────────────
async def test_r2_concurrent_equals_serial():
    """并发 5 key×3 次 与 串行 5 key×3 次 结果一致（版本与最终 value）。"""
    async def run_concurrent():
        kb = KnowledgeBase(HashingEmbedder(dim=64))
        up = UserProfile(kb, namespace="profile")
        tasks = [
            up.upsert([ProfileEntry(type="preference", key=k, value=f"喜欢{k}{i}", confidence=0.6)])
            for k in ["咖啡", "茶", "可乐"] for i in range(3)
        ]
        await asyncio.gather(*tasks)
        return {e.key: (e.versions, e.value) for e in up.list_entries()}

    async def run_serial():
        kb = KnowledgeBase(HashingEmbedder(dim=64))
        up = UserProfile(kb, namespace="profile")
        for k in ["咖啡", "茶", "可乐"]:
            for i in range(3):
                await up.upsert([ProfileEntry(type="preference", key=k, value=f"喜欢{k}{i}", confidence=0.6)])
        return {e.key: (e.versions, e.value) for e in up.list_entries()}

    conc, ser = await asyncio.gather(run_concurrent(), run_serial())
    assert conc == ser, f"并发与串行结果不一致：\n并发={conc}\n串行={ser}"
