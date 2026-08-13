"""用户画像（UserProfile）核心测试：去重/同义/correction/检索/提醒/上限/持久化。"""
from datetime import date, timedelta

import pytest

from roleplay.core.knowledge.embedder import HashingEmbedder
from roleplay.core.knowledge.profile import UserProfile
from roleplay.core.knowledge.profile_models import ProfileEntry
from roleplay.core.knowledge.vector_store import KnowledgeBase


@pytest.fixture
def kb(tmp_path):
    return KnowledgeBase(HashingEmbedder(dim=64), persist_dir=tmp_path / "kb")


@pytest.fixture
def profile(kb):
    return UserProfile(
        kb,
        namespace="profile",
        decay_lambda=0.05,
        synonym_threshold=0.85,
        reminder_days=3,
        max_items=200,
        top_k=5,
    )


# ───────────────────────── 精确键去重 / 更新 ─────────────────────────
async def test_same_key_increments_versions(profile):
    n = await profile.upsert(
        [ProfileEntry(type="preference", key="咖啡", value="喜欢喝拿铁", confidence=0.3)],
        source_round=5,
    )
    assert n == 1
    assert profile.count() == 1
    # 同 key 再 upsert → versions==2，value 更新，不新增
    n2 = await profile.upsert(
        [ProfileEntry(type="preference", key="咖啡", value="喜欢喝美式", confidence=0.6)],
        source_round=6,
    )
    assert n2 == 1
    assert profile.count() == 1
    items = profile.list_entries()
    assert items[0].versions == 2
    assert items[0].value == "喜欢喝美式"
    assert items[0].confidence == 0.6  # max(old, new)
    assert items[0].history == ["喜欢喝拿铁"]  # 旧 value 进 history


async def test_same_key_normalized(profile):
    """去重键归一化：key 大小写/空白不同视为同一。"""
    await profile.upsert([ProfileEntry(type="fact", key="  CoFFee ", value="产地云南")])
    await profile.upsert([ProfileEntry(type="fact", key="coffee", value="产地云南保山")])
    assert profile.count() == 1
    assert profile.list_entries()[0].versions == 2


# ───────────────────────── 同义检查（向量相似度） ─────────────────────────
async def test_synonym_updates_without_new(profile):
    """相似文本（同类型）判同义 → 更新原条目，不新增。"""
    await profile.upsert(
        [ProfileEntry(type="preference", key="咖啡", value="喜欢喝拿铁", confidence=0.6)]
    )
    # 高度重叠的同义 key + 相同 value（向量相似度 > 0.85）→ 判同义更新，不新增
    n = await profile.upsert(
        [ProfileEntry(type="preference", key="咖啡豆", value="喜欢喝拿铁", confidence=0.6)]
    )
    assert n == 1
    items = profile.list_entries()
    assert len(items) == 1  # 同义 → 不新增
    assert items[0].versions == 2


async def test_low_confidence_skips_synonym_check(profile):
    """规则条目 confidence=0.3 < 0.4 → 跳过同义检查，直接新增。"""
    await profile.upsert(
        [ProfileEntry(type="preference", key="咖啡", value="喜欢喝拿铁", confidence=0.3)]
    )
    await profile.upsert(
        [ProfileEntry(type="preference", key="拿铁咖啡", value="喜欢喝热拿铁", confidence=0.3)]
    )
    assert profile.count() == 2  # 低置信不判同义 → 新增


# ───────────────────────── correction 覆盖 ─────────────────────────
async def test_correction_overrides_and_halves_importance(profile):
    await profile.upsert(
        [ProfileEntry(type="preference", key="咖啡", value="喜欢喝拿铁", importance=0.8, confidence=0.6)]
    )
    await profile.upsert(
        [ProfileEntry(type="correction", key="咖啡", value="不再喜欢咖啡", importance=0.5, confidence=0.3)]
    )
    items = profile.list_entries()
    assert len(items) == 1
    e = items[0]
    # importance 降半（0.8*0.5=0.4 ≥ 0.3）
    assert e.importance == pytest.approx(0.4)
    assert e.value == "不再喜欢咖啡"
    assert e.versions == 2
    # corrected 标记写入 metadata
    raw = profile._kb.list_items("profile")[0]["meta"]
    assert raw.get("corrected") is True


async def test_correction_floor_importance(profile):
    """correction 降半但下限 0.3。"""
    await profile.upsert(
        [ProfileEntry(type="preference", key="咖啡", value="喜欢喝拿铁", importance=0.4, confidence=0.6)]
    )
    await profile.upsert(
        [ProfileEntry(type="correction", key="咖啡", value="不再喜欢咖啡", importance=0.5, confidence=0.3)]
    )
    e = profile.list_entries()[0]
    assert e.importance == pytest.approx(0.3)  # 0.4*0.5=0.2 → floor 0.3


async def test_correction_no_target_becomes_fact(profile):
    """correction 找不到原条目 → 转存 fact 条目 importance=0.3。"""
    n = await profile.upsert(
        [ProfileEntry(type="correction", key="不存在的爱好", value="不再喜欢X", importance=0.5, confidence=0.3)]
    )
    assert n == 1
    items = profile.list_entries()
    assert len(items) == 1
    assert items[0].type == "fact"
    assert items[0].importance == pytest.approx(0.3)


# ───────────────────────── 检索排序 ─────────────────────────
async def test_retrieve_ranks_by_importance(profile):
    await profile.upsert(
        [ProfileEntry(type="preference", key="咖啡", value="喜欢喝拿铁", importance=0.9, confidence=0.9)]
    )
    await profile.upsert(
        [ProfileEntry(type="preference", key="可乐", value="喜欢喝可乐", importance=0.1, confidence=0.1)]
    )
    hits = await profile.retrieve("咖啡 喜欢")
    assert hits, "应能检索到画像"
    # 高 importance 排在前面（或至少存在）
    texts = [h.text for h in hits]
    assert any("咖啡" in t for t in texts)
    assert any("可乐" in t for t in texts)


async def test_retrieve_respects_top_k(profile):
    for i in range(10):
        await profile.upsert(
            [ProfileEntry(type="fact", key=f"项{i}", value=f"事实{i}", importance=0.5, confidence=0.5)]
        )
    hits = await profile.retrieve("事实", top_k=3)
    assert len(hits) <= 3


# ───────────────────────── 提醒（important_date） ─────────────────────────
async def test_reminder_within_window(profile):
    today = date.today()
    d = today + timedelta(days=2)
    await profile.upsert(
        [ProfileEntry(type="important_date", key="生日", value=f"{d.month}月{d.day}日", importance=0.7)]
    )
    reminders = profile.check_reminders(today)
    assert reminders, "±3 天内应有提醒"
    assert any("生日" in r for r in reminders)


async def test_reminder_exact_today(profile):
    today = date.today()
    await profile.upsert(
        [ProfileEntry(type="important_date", key="纪念日", value=f"{today.month}月{today.day}日", importance=0.7)]
    )
    reminders = profile.check_reminders(today)
    assert any("今天" in r for r in reminders)


async def test_reminder_outside_window(profile):
    today = date.today()
    d = today + timedelta(days=10)
    await profile.upsert(
        [ProfileEntry(type="important_date", key="生日", value=f"{d.month}月{d.day}日", importance=0.7)]
    )
    assert profile.check_reminders(today) == []


async def test_reminder_iso_format(profile):
    today = date.today()
    d = today + timedelta(days=1)
    await profile.upsert(
        [ProfileEntry(type="important_date", key="生日", value=d.isoformat(), importance=0.7)]
    )
    reminders = profile.check_reminders(today)
    assert any("明天" in r for r in reminders)


async def test_reminder_unparseable_skipped(profile):
    await profile.upsert(
        [ProfileEntry(type="important_date", key="生日", value="不知道啥时候", importance=0.7)]
    )
    assert profile.check_reminders(date.today()) == []  # 解析失败跳过，不抛


# ───────────────────────── 上限淘汰 ─────────────────────────
async def test_prune_keeps_important_date(profile):
    profile._max_items = 3
    # 2 条 fact + 1 条 important_date 占满
    await profile.upsert(
        [ProfileEntry(type="fact", key="f1", value="事实1", importance=0.5, confidence=0.5)]
    )
    await profile.upsert(
        [ProfileEntry(type="fact", key="f2", value="事实2", importance=0.5, confidence=0.5)]
    )
    await profile.upsert(
        [ProfileEntry(type="important_date", key="生日", value="5月20日", importance=0.5, confidence=0.5)]
    )
    assert profile.count() == 3
    # 再新增一条 → 淘汰最低 importance 的 fact（保留 important_date）
    await profile.upsert(
        [ProfileEntry(type="fact", key="f3", value="事实3", importance=0.5, confidence=0.5)]
    )
    assert profile.count() == 3
    types = {e.type for e in profile.list_entries()}
    assert "important_date" in types  # important_date 不被淘汰


# ───────────────────────── 持久化（重启不丢） ─────────────────────────
async def test_persistence_across_reload(tmp_path):
    dirpath = tmp_path / "kb2"
    kb1 = KnowledgeBase(HashingEmbedder(dim=64), persist_dir=dirpath)
    up1 = UserProfile(kb1, namespace="profile")
    await up1.upsert(
        [ProfileEntry(type="preference", key="咖啡", value="喜欢喝拿铁", confidence=0.6)]
    )
    # 模拟重启
    kb2 = KnowledgeBase(HashingEmbedder(dim=64), persist_dir=dirpath)
    up2 = UserProfile(kb2, namespace="profile")
    assert up2.count() == 1
    items = up2.list_entries()
    assert items[0].type == "preference"
    assert items[0].key == "咖啡"
    hits = await up2.retrieve("咖啡")
    assert hits and any("咖啡" in h.text for h in hits)


# ───────────────────────── ProfileEntry 模型 ─────────────────────────
def test_profile_entry_validation():
    with pytest.raises(Exception):
        ProfileEntry(type="invalid_type", key="k", value="v")
    # importance/confidence 越界应报错（ge/le 校验）
    with pytest.raises(Exception):
        ProfileEntry(type="preference", key="k", value="v", importance=1.5)
    with pytest.raises(Exception):
        ProfileEntry(type="preference", key="k", value="v", confidence=-0.1)


def test_profile_entry_normalize_and_meta_roundtrip():
    e = ProfileEntry(type="habit", key="早起", value="每天6点起", importance=0.6, confidence=0.3)
    assert e.dedup_key == "habit:早起"
    meta = e.to_meta()
    e2 = ProfileEntry.from_meta(meta)
    assert e2.type == e.type
    assert e2.key == e.key
    assert e2.value == e.value
