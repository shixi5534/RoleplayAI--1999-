"""语音回复决策器与切片库单元测试（QQ 语音 P0）。

覆盖：
- ClipStore：manifest 加载、按 槽位×语言 选片、最近一条去重与单条池回退、字节读取
- default_manifest_path：配置覆盖优先、路径无效返回 None
- VoiceReplyService 触发矩阵：开关（全局/会话）、情绪阈值、keyword 来源豁免、
  neutral 拦截、群聊约束、冷却、配音语言切换、超长切片降级、!clear 语义
"""
import json
import types

from roleplay.core.voice.clip_store import ClipStore, default_manifest_path
from roleplay.core.voice.voice_reply import EMOTION_TO_SLOT, VoiceReplyService
from roleplay.models.chat import EmotionInfo

ALL_EMOTIONS = [
    "happy", "sad", "angry", "anxious", "surprise", "fear", "neutral",
    "love", "grateful", "excited", "disappointed", "lonely", "embarrassed",
    "confused", "sleepy",
]


# ── 测试数据 ──
def _write_manifest(root, clips, slots):
    """在 root 下写 manifest 与占位 mp3，返回 manifest 路径。"""
    root.mkdir(parents=True, exist_ok=True)
    manifest = {
        "character": "tester",
        "version": 1,
        "langs": ["zh", "en"],
        "clips": clips,
        "slots": slots,
    }
    for c in clips:
        p = root / c["file"]
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(f"audio:{c['id']}".encode())
    path = root / "manifest.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    return path


def _make_store(tmp_path, *, with_long=False):
    clips = [
        {"id": "zh_h1", "lang": "zh", "file": "zh/h1.mp3", "dur": 5.0,
         "subtitle": {"zh": "中一", "en": "en one"}},
        {"id": "zh_h2", "lang": "zh", "file": "zh/h2.mp3", "dur": 6.0,
         "subtitle": {"zh": "中二", "en": "en two"}},
        {"id": "en_h1", "lang": "en", "file": "en/h1.mp3", "dur": 4.0,
         "subtitle": {"zh": "英配中字", "en": "en one"}},
        {"id": "zh_s1", "lang": "zh", "file": "zh/s1.mp3", "dur": 3.0,
         "subtitle": {"zh": "惊一", "en": "sur one"}},
    ]
    slots = {"happy": ["zh_h1", "zh_h2", "en_h1"], "surprise": ["zh_s1"]}
    if with_long:
        clips.append({"id": "zh_long", "lang": "zh", "file": "zh/long.mp3",
                      "dur": 70.0, "subtitle": {"zh": "超长", "en": "long"}})
        slots["sad"] = ["zh_long"]
    return ClipStore(_write_manifest(tmp_path / "voice", clips, slots))


def _settings(**kw):
    defaults = dict(
        qq_voice_enabled=False,
        qq_voice_lang="zh",
        qq_voice_clip_manifest="",
        qq_voice_emotion_threshold=0.6,
        qq_voice_cooldown_sec=60.0,
        qq_voice_max_sec=65.0,
        qq_voice_group_enabled=False,
    )
    defaults.update(kw)
    return types.SimpleNamespace(**defaults)


def _svc(store, **kw):
    return VoiceReplyService(_settings(**kw), store=store)


def _emo(emotion, score, source="llm"):
    return EmotionInfo(emotion=emotion, score=score, source=source)


HAPPY = _emo("happy", 0.9)


# ── ClipStore ──
def test_clip_store_loads_and_picks_by_lang(tmp_path):
    store = _make_store(tmp_path)
    for _ in range(20):  # 随机选片，多次采样只应命中 zh
        c = store.pick("happy", "zh")
        assert c is not None and c.lang == "zh"
    c = store.pick("happy", "en")
    assert c is not None and c.id == "en_h1"


def test_clip_store_exclude_and_single_pool_fallback(tmp_path):
    store = _make_store(tmp_path)
    # 双条池：排除后绝不返回被排除那条
    for _ in range(20):
        assert store.pick("happy", "zh", exclude="zh_h1").id == "zh_h2"
    # 单条池：排除后允许重复（对齐前端，避免槽位被去重卡死）
    c = store.pick("surprise", "zh", exclude="zh_s1")
    assert c is not None and c.id == "zh_s1"


def test_clip_store_unknown_slot_or_lang_returns_none(tmp_path):
    store = _make_store(tmp_path)
    assert store.pick("battle", "zh") is None  # 无此槽位
    assert store.pick("surprise", "en") is None  # 槽位无该语言


def test_clip_store_read_bytes(tmp_path):
    store = _make_store(tmp_path)
    entry = store.pick("happy", "en")
    assert store.read_bytes(entry) == b"audio:en_h1"


def test_default_manifest_path_override(tmp_path):
    path = _write_manifest(tmp_path / "v", [], {})
    assert default_manifest_path(_settings(qq_voice_clip_manifest=str(path))) == path
    assert default_manifest_path(_settings(qq_voice_clip_manifest=str(tmp_path / "nope.json"))) is None


# ── VoiceReplyService：触发矩阵 ──
def test_disabled_by_default_no_voice(tmp_path):
    svc = _svc(_make_store(tmp_path))
    assert svc.decide("s1", HAPPY) is None


def test_session_enabled_triggers_clip(tmp_path):
    svc = _svc(_make_store(tmp_path))
    svc.set_enabled("s1", True)
    d = svc.decide("s1", HAPPY)
    assert d is not None
    assert d.kind == "clip" and d.slot == "happy" and d.lang == "zh"
    assert d.audio.startswith(b"audio:")
    assert d.subtitle["zh"] in ("中一", "中二")


def test_global_default_enabled(tmp_path):
    svc = _svc(_make_store(tmp_path), qq_voice_enabled=True)
    assert svc.is_enabled("s1") is True
    assert svc.decide("s1", HAPPY) is not None


def test_low_score_llm_not_triggered(tmp_path):
    svc = _svc(_make_store(tmp_path))
    svc.set_enabled("s1", True)
    assert svc.decide("s1", _emo("happy", 0.4, "llm")) is None


def test_keyword_source_low_score_qualifies(tmp_path):
    """关键词层单命中分值 0.3~0.5 天然低于阈值，真实命中应视为达标。"""
    svc = _svc(_make_store(tmp_path))
    svc.set_enabled("s1", True)
    assert svc.decide("s1", _emo("happy", 0.4, "keyword")) is not None


def test_neutral_never_triggers(tmp_path):
    svc = _svc(_make_store(tmp_path))
    svc.set_enabled("s1", True)
    assert svc.decide("s1", _emo("neutral", 0.9, "llm")) is None
    assert svc.decide("s1", None) is None


def test_cooldown_blocks_second_voice(tmp_path):
    svc = _svc(_make_store(tmp_path))
    svc.set_enabled("s1", True)
    assert svc.decide("s1", HAPPY) is not None
    assert svc.decide("s1", HAPPY) is None  # 冷却期内
    # 不同会话互不影响
    svc.set_enabled("s2", True)
    assert svc.decide("s2", HAPPY) is not None


def test_zero_cooldown_allows_repeat(tmp_path):
    svc = _svc(_make_store(tmp_path), qq_voice_cooldown_sec=0)
    svc.set_enabled("s1", True)
    assert svc.decide("s1", HAPPY) is not None
    assert svc.decide("s1", HAPPY) is not None


def test_lang_override_switches_voice(tmp_path):
    svc = _svc(_make_store(tmp_path))
    svc.set_enabled("s1", True)
    svc.set_lang("s1", "en")
    d = svc.decide("s1", HAPPY)
    assert d is not None and d.lang == "en" and d.clip_id == "en_h1"


def test_group_voice_gated_by_config(tmp_path):
    store = _make_store(tmp_path)
    svc = _svc(store, qq_voice_enabled=True, qq_voice_group_enabled=False)
    assert svc.decide("g1", HAPPY, is_group=True) is None
    svc2 = _svc(store, qq_voice_enabled=True, qq_voice_group_enabled=True)
    assert svc2.decide("g1", HAPPY, is_group=True) is not None


def test_overlong_clip_degrades_to_text(tmp_path):
    """切片超过 max_sec → 不出声（渠道侧降级发文字）。"""
    svc = _svc(_make_store(tmp_path, with_long=True))
    svc.set_enabled("s1", True)
    assert svc.decide("s1", _emo("sad", 0.9)) is None


def test_custom_max_sec_allows_long_clip(tmp_path):
    svc = _svc(_make_store(tmp_path, with_long=True), qq_voice_max_sec=80.0)
    svc.set_enabled("s1", True)
    d = svc.decide("s1", _emo("sad", 0.9))
    assert d is not None and d.duration == 70.0


def test_clear_session_resets_state(tmp_path):
    svc = _svc(_make_store(tmp_path))
    svc.set_enabled("s1", True)
    svc.set_lang("s1", "en")
    svc.clear_session("s1")
    assert svc.is_enabled("s1") is False  # 回到全局默认（关）
    assert svc.get_lang("s1") == "zh"
    # 冷却也一并重置：重新开启后立即可触发
    svc.set_enabled("s1", True)
    assert svc.decide("s1", HAPPY) is not None


def test_emotion_to_slot_covers_all_15():
    for e in ALL_EMOTIONS:
        assert e in EMOTION_TO_SLOT
    # 抽查关键映射（与方案 §二 / 前端 POSE_TO_SLOT 对齐）
    assert EMOTION_TO_SLOT["love"] == "happy"
    assert EMOTION_TO_SLOT["disappointed"] == "sad"
    assert EMOTION_TO_SLOT["confused"] == "surprise"  # 有意保留前端口径
    assert EMOTION_TO_SLOT["sleepy"] == "sleep"
    assert EMOTION_TO_SLOT["fear"] == "surprise"
