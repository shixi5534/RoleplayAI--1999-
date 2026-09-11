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
    return UserProfile(kb, namespace="profile", decay_lambda=0.05, synonym_threshold=0.85,
                       reminder_days=3, max_items=200, top_k=5)


async def test_scratch_max(profile):
    profile._max_items = 0
    n = await profile.upsert([ProfileEntry(type="fact", key="f", value="F", importance=0.5, confidence=0.5)])
    print("handled=", n, "count=", profile.count())
    print("items=", profile._kb.list_items("profile"))
    assert profile.count() == 0
