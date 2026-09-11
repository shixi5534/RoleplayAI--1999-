"""生成后角色一致性自检（P1-4）。

问题（问题 9）：生成后只做复读违规检查（repetition_guard.find_violations），
不检查角色一致性。明显出戏的回复（自称 AI、客服腔、替用户写动作）会直接
到达用户，没有任何二次过滤。

方案：**纯规则匹配**，不调用 LLM（零延迟、零成本、可离线单测）。
命中后把违规类型追加到重试指令里要求重写（由 Orchestrator 执行，重试上限 2 次）。

三类检测：
1. identity 身份出戏：回复里出现「作为AI」「我是语言模型」「开发者」等
   ——角色自我暴露为程序，是最严重的出戏。
2. service  客服腔：以「希望这对你有帮助」「有什么可以帮您」等收尾
   ——通用助手腔，与角色人设（疏离、带刺、话不多）正面冲突。
3. format   格式违规：出现 ``*你…*`` 这类描写**对方**动作/反应的片段
   ——违反「不替对方说话、不替对方做决定」的核心规则。

设计约束（与 repetition_guard 对齐）：
- 纯字符串处理，无 IO、无外部依赖；
- 空回复 / 无命中 → 空列表（调用方不重试，行为与改造前一致，零回归）；
- 词表与阈值集中在本模块，便于按角色扩展（如加第四类"编造设定"）。
"""
from __future__ import annotations

import re
from dataclasses import dataclass

# ── 1) 身份出戏 ──
# 英文/缩写片段统一小写比对（下方 lower() 后匹配），中文片段原样比对。
_IDENTITY_PATTERNS = (
    "作为ai",
    "作为 ai",
    "作为一个ai",
    "作为人工智能",
    "我是ai",
    "我是一个ai",
    "我是人工智能",
    "我是语言模型",
    "我是一个语言模型",
    "我是大语言模型",
    "我是虚拟角色",
    "我是虚拟人物",
    "我是助手",
    "我是一个助手",
    "我只是一个程序",
    "我没有真实情感",
    "我没有真实的情感",
    "openai",
    "chatgpt",
    "开发者设定",
)

_IDENTITY_ADVICE = (
    "你不是 AI，也不是任何程序或助手。抹掉这类自我暴露，"
    "直接以角色身份说话——被问到就否认、回避或轻描淡写地带过。"
)

# ── 2) 客服腔（收尾客套/总结） ──
# 判定：去掉尾部标点/引号后，回复**以**这些片段结尾。
_SERVICE_TAILS = (
    "希望这对你有帮助",
    "希望对你有帮助",
    "希望能帮到你",
    "希望可以帮到你",
    "有什么可以帮您",
    "有什么我可以帮您",
    "有什么我可以帮你",
    "随时为您服务",
    "随时为你服务",
    "如有其他问题",
    "如果还有其他问题",
    "祝您生活愉快",
    "祝你生活愉快",
    "欢迎继续提问",
    "欢迎随时提问",
    "总的来说",
    "总而言之",
)

_SERVICE_ADVICE = (
    "删掉收尾的客套与总结腔。她不会这样收尾——话说完就停，"
    "或用一句轻描淡写的话带过，不要替对方做总结。"
)

# 判尾时忽略的尾部标点/空白/引号
_TAIL_STRIP = " \t\r\n。！？!?~～.,，、;；:：'\"“”「」『』()（）"

# ── 3) 格式违规：描写「对方」的动作/反应 ──
# 只匹配被 *...* 包裹且含「你」的片段（动作用 *...* 标记，见 P1-2 输出格式）。
_USER_ACTION_RE = re.compile(r"\*[^*\n]*你[^*\n]*\*")

_FORMAT_ADVICE = (
    "不要写对方的动作、反应或心理。你只能写**自己**的动作与念头，"
    "对方发生了什么由对方自己说。"
)

# 违规类型 → 人类可读标签（写进日志与重试指令）
_KIND_LABELS = {
    "identity": "身份出戏（自称 AI/程序）",
    "service": "客服腔（客套/总结收尾）",
    "format": "格式违规（写了对方的动作）",
}


@dataclass
class QualityViolation:
    """一条角色一致性违规。"""

    kind: str  # identity / service / format
    detail: str  # 命中的原文片段（用于日志与提示词）
    advice: str  # 给模型的修改建议

    @property
    def label(self) -> str:
        return _KIND_LABELS.get(self.kind, self.kind)


def find_quality_violations(reply: str | None) -> list[QualityViolation]:
    """生成后自检：返回命中的角色一致性违规列表（无命中 → []）。

    三类检测独立运行，同类只报**第一条**（重试指令已经足够指明问题，
    重复罗列只会挤占提示词）。
    """
    text = (reply or "").strip()
    if not text:
        return []
    hits: list[QualityViolation] = []
    seen: set[str] = set()

    def _add(kind: str, detail: str, advice: str) -> None:
        if kind in seen:
            return
        seen.add(kind)
        hits.append(QualityViolation(kind=kind, detail=detail, advice=advice))

    lowered = text.lower()
    for pattern in _IDENTITY_PATTERNS:
        if pattern in lowered:
            _add("identity", pattern, _IDENTITY_ADVICE)
            break

    tail = text.rstrip(_TAIL_STRIP)
    for pattern in _SERVICE_TAILS:
        if tail.endswith(pattern):
            _add("service", pattern, _SERVICE_ADVICE)
            break

    match = _USER_ACTION_RE.search(text)
    if match:
        _add("format", match.group(0), _FORMAT_ADVICE)

    return hits


def quality_retry_hint(violations: list[QualityViolation]) -> str:
    """重试指令：把违规类型与修改建议追加到提示词末尾，要求重写。

    空列表 → 空串（调用方不追加，零回归）。
    """
    if not violations:
        return ""
    items = "\n".join(f"- {v.label}（命中：{v.detail}）：{v.advice}" for v in violations)
    return (
        "【出戏了，重写】你刚才的回复破坏了角色一致性：\n"
        f"{items}\n"
        "请保留原本想表达的意思，但换成这个角色**真的会**说的方式重写一遍。"
    )


def refine_instruction(violations: list[QualityViolation]) -> str:
    """P2-3 两阶段生成的 SELF-CHECK 精炼指令（低温度二次生成用）。

    与 quality_retry_hint 的分工：retry 是「规则已判违规 → 按条修正」的定向
    重写指令（P1-4 重试循环用）；refine 是「重试耗尽后的兜底自检」——四条
    自检覆盖语气/重复/越权等规则测不全的出戏维度，并附带已判明的违规建议。
    """
    base = (
        "【SELF-CHECK】先把刚才的回复对照四条自检，再输出修正后的终稿：\n"
        "1. 这句话像这个角色会说的吗？不像就重写。\n"
        "2. 有没有客服腔、书面语或总结式收尾？改成口语，话说完就停。\n"
        "3. 有没有重复此前用过的比喻、意象或句式？换新的说法。\n"
        "4. 有没有替用户说话、写用户的动作心理、替用户做决定？删掉，只写你自己。"
    )
    if violations:
        base += "\n\n" + quality_retry_hint(violations)
    return base
