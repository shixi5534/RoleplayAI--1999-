"""复读抑制（repetition guard）：动态负向提示 + 生成后校验。

问题（线上实测）：角色会把 mes_example 示范句逐字复现
（「窗外的蛾子又往亮处扑了，很蠢，也很像人。」连续两轮原文照搬），
并在后续轮次反复使用同一意象（蛾子连用三轮），用户反馈「复读机/成天念叨」。
采样层 repetition_penalty（1.10）无法根治：它只按 token 局部惩罚，
整句照抄 few-shot 示例依然会发生。

方案（对齐社区成熟做法，如 echoproof：把最近对话历史注入 negative prompt）：
1. 预防：提取「本会话最近几轮角色已说过的话」为禁用短语，渲染成提示词块
   注入 system prompt 末尾（靠近生成点），明令禁止再次出现；
2. 校验：非流式路径生成后逐字比对，命中禁用短语则追加「重写指令」重试；
3. 源头：角色卡同时收紧意象使用规则（见 data/characters/wu_ming_zhe.json）。

设计约束：
- 只统计 assistant 消息，不把用户原话当禁用短语；
- 短语长度下限（默认 6 字）防碎片化误伤；数量上限（默认 8 条）控 prompt 膨胀；
- 空历史 → 返回 None / 空列表，提示词输出与改造前逐字节一致（零回归）；
- 纯字符串处理，无 IO、无外部依赖，可离线单测。
"""
from __future__ import annotations

import re

# 句切分：中文句号/问号/叹号/分号/换行视为句子边界。
# 注意：省略号「……」是句中停顿（如「嗯……被骂的那几句」），不算边界。
_SENT_SPLIT = re.compile(r"[。！？!?\n；;]+")
# 每条短语最长保留（防超长句撑爆 prompt）
_MAX_PHRASE_CHARS = 60
# 最小短语长度：低于此长度没有禁用价值，反而易误伤正常表达
_MIN_PHRASE_LEN = 6


def split_sentences(text: str) -> list[str]:
    """按句读切分文本，返回去空白与首尾标点后的句子列表。"""
    parts = _SENT_SPLIT.split(text or "")
    out: list[str] = []
    for p in parts:
        p = p.strip().strip("「」『』“”\"'（）()，,。.：: ")
        if p:
            out.append(p)
    return out


def extract_recent_phrases(
    history: list[dict] | None,
    *,
    window: int = 8,
    min_len: int = _MIN_PHRASE_LEN,
    max_phrases: int = 8,
    extra_phrases: list[str] | None = None,
) -> list[str]:
    """从最近 window 条 assistant 消息提取「禁用短语」。

    - 只统计 assistant 消息（用户原话不算）；
    - 句子去重（保持首次出现顺序）；
    - 超长句截断到 _MAX_PHRASE_CHARS；
    - extra_phrases（如角色卡 mes_example / first_mes 的句子）始终在列，
      防止首轮就照抄示例原句。
    """
    phrases: list[str] = []
    seen: set[str] = set()

    def _add(p: str) -> None:
        p = p.strip()
        if len(p) < min_len or p in seen:
            return
        seen.add(p)
        phrases.append(p[:_MAX_PHRASE_CHARS])

    for ex in extra_phrases or []:
        for s in split_sentences(ex):
            _add(s)
    if history:
        tail = 0
        for msg in reversed(history):
            if (msg or {}).get("role") != "assistant":
                continue
            if tail >= window:
                break
            tail += 1
            for s in split_sentences((msg or {}).get("content") or ""):
                _add(s)
    return phrases[:max_phrases]


_BLOCK_HEADER = (
    "【别说重复的话（最高优先级，压过上面所有内容）】\n"
    "下面这些话你已经在这个对话里说过，这一轮绝对禁止再出现"
    "（原句、只改几个字、或换个比喻表达同样的意思都不行）："
)

_BLOCK_FOOTER = (
    "宁可换一种说法，或者干脆不提，也不要复读。"
    "同一个比喻、同一句口头禅，用过一次就换新的。"
)


def build_repetition_block(phrases: list[str]) -> str | None:
    """渲染负向提示块。空列表返回 None（调用方不追加，保持零回归）。"""
    if not phrases:
        return None
    items = "\n".join(f"- 「{p}」" for p in phrases)
    return f"{_BLOCK_HEADER}\n{items}\n{_BLOCK_FOOTER}"


def find_violations(
    reply: str,
    phrases: list[str],
    *,
    exclude_in: str | None = None,
    min_len: int = _MIN_PHRASE_LEN,
) -> list[str]:
    """生成后校验：回复中逐字包含的禁用短语（子串匹配）。

    exclude_in：若短语同时出现在该文本中（如**当前用户消息**里引用了角色
    上一轮的原话），则不判违规——用户引用场景下模型需要复述原句来解释，
    强禁会导致绕圈子甚至答非所问（引用回环误伤，审查发现）。
    """
    if not reply or not phrases:
        return []
    hits: list[str] = []
    for p in phrases:
        if len(p) < min_len:
            continue
        if exclude_in and p in exclude_in:
            continue
        if p in reply:
            hits.append(p)
    return hits


def retry_hint(violations: list[str]) -> str:
    """重试指令：追加在提示词末尾，要求重写一条完全不同的回复。"""
    if not violations:
        return ""
    items = "、".join(f"「{v}」" for v in violations[:3])
    return (
        "【立即重写】你刚才的回复里出现了已经说过的话（" + items + "）。\n"
        "请重新写一条完全不同的回复：换一种说法，不要出现上述任何句子，"
        "也不要重复刚才用过的意象。"
    )
