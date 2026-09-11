"""复读抑制（repetition guard）测试：单元 + 编排集成。"""
import tempfile
from pathlib import Path

from roleplay.core.emotion.detector import KeywordEmotionDetector
from roleplay.core.llm.mock import MockLLMProvider
from roleplay.core.orchestrator import ChatOrchestrator
from roleplay.core.persona_prompt import build_roleplay_prompt
from roleplay.core.rag.memory import InMemoryVectorStore
from roleplay.core.repetition_guard import (
    build_repetition_block,
    extract_recent_phrases,
    find_violations,
    retry_hint,
    split_sentences,
)
from roleplay.core.session_memory import SessionMemory
from roleplay.models.chat import ChatRequest


# ─────────────────────────── 单元：短语提取 ───────────────────────────

def test_split_sentences_basic():
    text = "窗外的蛾子又往亮处扑了，很蠢，也很像人。嗯……被骂的那几句，还在你脑子里转吧？"
    parts = split_sentences(text)
    assert parts == ["窗外的蛾子又往亮处扑了，很蠢，也很像人", "嗯……被骂的那几句，还在你脑子里转吧"]


def test_split_sentences_strips_quotes_and_empty():
    assert split_sentences("「只有这一句。」") == ["只有这一句"]
    assert split_sentences("") == []
    assert split_sentences("。。。") == []


def test_extract_recent_phrases_only_assistant():
    history = [
        {"role": "user", "content": "窗外的蛾子又往亮处扑了，很蠢，也很像人。"},
        {"role": "assistant", "content": "我今天不想聊蛾子。"},
    ]
    phrases = extract_recent_phrases(history)
    assert "我今天不想聊蛾子" in phrases
    assert "窗外的蛾子又往亮处扑了，很蠢，也很像人" not in phrases  # 用户原话不算


def test_extract_recent_phrases_window_dedupe_minlen_cap():
    history = [{"role": "assistant", "content": f"第 {i} 句完全不同的台词用于测试窗口。"} for i in range(12)]
    phrases = extract_recent_phrases(history, window=3, max_phrases=2)
    assert len(phrases) == 2
    assert "第 11 句完全不同的台词用于测试窗口" in phrases  # 最近的在列
    assert "第 0 句完全不同的台词用于测试窗口" not in phrases  # 超出窗口
    # 去重 + 最小长度
    dup = [{"role": "assistant", "content": "同一句话重复两次。"}] * 3
    assert len(extract_recent_phrases(dup)) == 1
    assert extract_recent_phrases([{"role": "assistant", "content": "短"}]) == []


def test_extract_recent_phrases_extra_first():
    history = [{"role": "assistant", "content": "历史上的台词。"}]
    phrases = extract_recent_phrases(
        history, extra_phrases=["口吻示范（只学语气，禁止照抄）\n「窗外的蛾子又往亮处扑了。」"]
    )
    # 示例句在列（防止首轮照抄）；头行「口吻示范…」也会被列入（无害）
    assert "窗外的蛾子又往亮处扑了" in phrases
    assert "历史上的台词" in phrases


# ─────────────────────────── 单元：提示块 / 校验 / 重试指令 ───────────────────────────

def test_build_repetition_block_none_on_empty():
    assert build_repetition_block([]) is None
    assert build_repetition_block(None) is None


def test_build_repetition_block_renders():
    block = build_repetition_block(["窗外的蛾子又往亮处扑了"])
    assert block is not None
    assert "【别说重复的话" in block
    assert "「窗外的蛾子又往亮处扑了」" in block
    assert "用过一次就换新的" in block


def test_find_violations():
    phrases = ["窗外的蛾子又往亮处扑了，很蠢，也很像人"]
    assert find_violations("窗外的蛾子又往亮处扑了，很蠢，也很像人。", phrases) == phrases
    assert find_violations("今天说点别的吧。", phrases) == []
    assert find_violations("", phrases) == []
    assert find_violations("窗外的蛾子", []) == []


def test_find_violations_exclude_in_skips_user_quotes():
    phrases = ["窗外的蛾子又往亮处扑了，很蠢，也很像人"]
    reply = "你指的是我说的「窗外的蛾子又往亮处扑了，很蠢，也很像人」那句吧。"
    # 用户本轮引用了角色原话 → 解释性复述不算违规
    assert find_violations(reply, phrases, exclude_in=reply) == []
    # 用户没引用 → 依然判违规
    assert find_violations(reply, phrases) == phrases
    # 用户消息不含该短语但回复含 → 判违规
    assert find_violations(reply, phrases, exclude_in="别的提问") == phrases


def test_find_violations_min_len_parameter():
    phrases = ["这是短句"]
    assert find_violations("这是短句", phrases, min_len=3) == ["这是短句"]
    assert find_violations("这是短句", phrases, min_len=5) == []  # 低于阈值不判


def test_retry_hint_contains_quoted_phrases():
    hint = retry_hint(["窗外的蛾子又往亮处扑了"])
    assert "「窗外的蛾子又往亮处扑了」" in hint
    assert "重新写一条完全不同的回复" in hint
    assert retry_hint([]) == ""


# ─────────────────────────── 单元：build_roleplay_prompt 追加 ───────────────────────────

def test_build_roleplay_prompt_repetition_block_appended_last():
    base = build_roleplay_prompt(
        card_json=None, fallback_prompt="你是测试角色。", default_card=None, message="hi"
    )
    with_block = build_roleplay_prompt(
        card_json=None,
        fallback_prompt="你是测试角色。",
        default_card=None,
        message="hi",
        repetition_block="【别说重复的话】\n- 「示例句」",
    )
    assert with_block == base + "\n\n【别说重复的话】\n- 「示例句」"
    assert "【别说重复的话】" not in base  # 默认路径零回归


# ─────────────────────────── 编排集成：可编排 LLM 替身 ───────────────────────────

class ScriptedLLM:
    """按序返回预设回复并记录调用（system 含 guard 断言用）。"""

    def __init__(self, *replies: str) -> None:
        self._replies = list(replies)
        self.calls: list[dict] = []

    @property
    def model_name(self) -> str:
        return "scripted"

    async def generate(self, *, system: str, user: str, history=None, temperature=None) -> str:
        self.calls.append({"system": system, "user": user, "history": history})
        return self._replies.pop(0) if self._replies else "（默认回复）"

    async def generate_stream(self, *, system: str, user: str, history=None, temperature=None):
        text = await self.generate(system=system, user=user, history=history, temperature=temperature)
        for i in range(0, len(text), 4):
            yield text[i : i + 4]


BANNED = "窗外的蛾子又往亮处扑了，很蠢，也很像人"


def _build_orch(llm, monkeypatch, *, guard_enabled=True, max_retries=1, memory=None):
    """构造编排器：monkeypatch 掉 run()/stream() 内部的 LLM 构建，强制使用替身。"""
    monkeypatch.setattr(
        "roleplay.core.orchestrator.build_llm_from_config",
        lambda s, override=None: (llm, False),
    )
    orch = ChatOrchestrator(
        llm=MockLLMProvider(),
        emotion=KeywordEmotionDetector(),
        rag=InMemoryVectorStore(),
        session_memory=memory or SessionMemory(Path(tempfile.mkdtemp(prefix="rg_"))),
        repetition_guard_enabled=guard_enabled,
        repetition_guard_max_retries=max_retries,
    )
    return orch


async def test_run_retries_when_reply_hits_banned_phrase(monkeypatch):
    memory = SessionMemory(Path(tempfile.mkdtemp(prefix="rg_")))
    memory.append_many("s", [("user", "你好"), ("assistant", BANNED)])
    llm = ScriptedLLM(BANNED, "今天聊聊别的吧。")
    orch = _build_orch(llm, monkeypatch, memory=memory)
    res = await orch.run(ChatRequest(session_id="s", message="继续"))
    assert res.response.reply == "今天聊聊别的吧。"
    assert len(llm.calls) == 2
    # 第一次调用已注入负向提示块
    assert "【别说重复的话" in llm.calls[0]["system"]
    assert BANNED in llm.calls[0]["system"]
    # 重试调用追加了重写指令
    assert "【立即重写】" in llm.calls[1]["system"]
    assert BANNED in llm.calls[1]["system"]


async def test_run_accepts_when_retries_exhausted(monkeypatch):
    memory = SessionMemory(Path(tempfile.mkdtemp(prefix="rg_")))
    memory.append_many("s", [("user", "你好"), ("assistant", BANNED)])
    llm = ScriptedLLM(BANNED, BANNED)
    orch = _build_orch(llm, monkeypatch, memory=memory, max_retries=1)
    res = await orch.run(ChatRequest(session_id="s", message="继续"))
    assert len(llm.calls) == 2  # 初始 + 1 次重试，不再无限循环
    assert res.response.reply == BANNED


async def test_run_single_call_when_clean(monkeypatch):
    memory = SessionMemory(Path(tempfile.mkdtemp(prefix="rg_")))
    memory.append_many("s", [("user", "你好"), ("assistant", BANNED)])
    llm = ScriptedLLM("今天聊聊别的吧。")
    orch = _build_orch(llm, monkeypatch, memory=memory)
    res = await orch.run(ChatRequest(session_id="s", message="继续"))
    assert len(llm.calls) == 1
    assert res.response.reply == "今天聊聊别的吧。"


async def test_run_guard_disabled_no_block_no_retry(monkeypatch):
    memory = SessionMemory(Path(tempfile.mkdtemp(prefix="rg_")))
    memory.append_many("s", [("user", "你好"), ("assistant", BANNED)])
    llm = ScriptedLLM(BANNED)
    orch = _build_orch(llm, monkeypatch, memory=memory, guard_enabled=False)
    res = await orch.run(ChatRequest(session_id="s", message="继续"))
    assert len(llm.calls) == 1  # 关闭后不做校验重试
    assert "别说重复的话" not in llm.calls[0]["system"]


async def test_run_no_history_no_guard_zero_regression(monkeypatch):
    memory = SessionMemory(Path(tempfile.mkdtemp(prefix="rg_")))
    llm = ScriptedLLM("第一句话。")
    orch = _build_orch(llm, monkeypatch, memory=memory)
    await orch.run(ChatRequest(session_id="s", message="你好"))
    assert len(llm.calls) == 1
    # 空历史（无 assistant 消息）→ 不注入 guard 块
    assert "别说重复的话" not in llm.calls[0]["system"]


async def test_run_user_quote_not_retried(monkeypatch):
    """用户引用角色原话提问时，模型解释性复述不算违规（引用回环误伤修复）。"""
    memory = SessionMemory(Path(tempfile.mkdtemp(prefix="rg_")))
    memory.append_many("s", [("user", "你好"), ("assistant", BANNED)])
    llm = ScriptedLLM("你指的是我说的「窗外的蛾子又往亮处扑了，很蠢，也很像人」那句吧。")
    orch = _build_orch(llm, monkeypatch, memory=memory)
    user_quote = "你上次说的「窗外的蛾子又往亮处扑了，很蠢，也很像人」是什么意思？"
    res = await orch.run(ChatRequest(session_id="s", message=user_quote))
    assert len(llm.calls) == 1  # 不触发重写
    assert res.response.reply == "你指的是我说的「窗外的蛾子又往亮处扑了，很蠢，也很像人」那句吧。"


async def test_run_zero_retries_accepts_violation(monkeypatch):
    """max_retries=0：命中违规短语 → 单次调用、接受当前回复（for/else 走 else 告警）。"""
    memory = SessionMemory(Path(tempfile.mkdtemp(prefix="rg_")))
    memory.append_many("s", [("user", "你好"), ("assistant", BANNED)])
    llm = ScriptedLLM(BANNED)
    orch = _build_orch(llm, monkeypatch, memory=memory, max_retries=0)
    res = await orch.run(ChatRequest(session_id="s", message="继续"))
    assert len(llm.calls) == 1
    assert res.response.reply == BANNED


async def test_run_request_card_examples_banned_even_empty_history(monkeypatch):
    """请求携带自定义角色卡：无历史也注入 guard 块（防首轮照抄请求卡的示例句）。"""
    memory = SessionMemory(Path(tempfile.mkdtemp(prefix="rg_")))
    card_json = '{"name": "测试卡", "mes_example": "口吻示范：「自定义卡的独特例句。」"}'
    llm = ScriptedLLM("第一句话。")
    orch = _build_orch(llm, monkeypatch, memory=memory)
    await orch.run(
        ChatRequest(session_id="s", message="你好", character_card=card_json)
    )
    assert len(llm.calls) == 1
    assert "【别说重复的话" in llm.calls[0]["system"]
    assert "自定义卡的独特例句" in llm.calls[0]["system"]


async def test_stream_injects_guard_prevention_only(monkeypatch):
    memory = SessionMemory(Path(tempfile.mkdtemp(prefix="rg_")))
    memory.append_many("s", [("user", "你好"), ("assistant", BANNED)])
    llm = ScriptedLLM("今天聊聊别的吧。")
    orch = _build_orch(llm, monkeypatch, memory=memory)
    chunks = []
    async for ev in orch.stream(ChatRequest(session_id="s", message="继续")):
        if ev["type"] == "chunk":
            chunks.append(ev["text"])
    assert "".join(chunks) == "今天聊聊别的吧。"
    assert len(llm.calls) == 1  # 流式只预防、不重试
    assert "【别说重复的话" in llm.calls[0]["system"]
