# -*- coding: utf-8 -*-
"""P4 作答通路：把检索上下文装配成「只准引用带编号片段」的问答 messages。

**为什么必须写死「不得引入外部知识」**
    本库的证据面只有 ``data/compendium_rag`` 下的独立语料（3695 块）。
    审查期 L3.4 域内幻觉率 0.1475 的共性是「把同正典其他片段的原句当成本条依据引用」，
    而模型对《重返未来：1999》本身带有大量**先验知识**——一旦允许它自由陈述，
    「读到了」与「本来就知道」就再也分不开，faithfulness 与幻觉率同时失去意义。
    所以提示词把回答约束成**片段的函数**：片段里没有的，一律答「未记载」。

**编号口径（谁定、谁守）**
    ``[S{i}]`` 溯源头由 ``GraphRetriever.context()`` 渲染
    （``src/compendium_rag/retriever.py:593-610``，2026-10-09 P3 步骤3 落盘），
    ``i`` **跟窗口排序走、不跟 chunk_id 走**——契约测试
    ``tests/compendium_rag/test_retriever.py::test_context_tags_evidence_with_citable_provenance``
    已把它钉住（断言 ``[S1 …]`` 出现在 ``[S2 …]`` 之前）。
    本模块**只消费、不重排、不重新编号**：编号与片段的对应关系一旦在这里被改写，
    「引用 S2」就回查不到窗口第 2 块，审查端也就无法逐条对账。

分层：``compose`` 只负责装配（纯函数、零 IO），``answer`` 只负责调用，
``render_prompt`` 把同一份装配结果摊平成子代理批次可用的单串。
提示词的任何调整落在本模块，传输/重试落在 :mod:`compendium_rag.llm`，两边可各自单测。
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .llm import CloudLLM, LLMResult

#: 系统提示：三条硬规则。改动它等于改动 L3 的评测前提，须同步报告口径。
ANSWER_SYSTEM_PROMPT = """你是《重返未来：1999》官方剧情档案的检索问答助手。

你的回答**只能**来自下面给出的带编号片段。三条硬规则，任何情况下都不得违反：

1. **只准引用带编号片段**：每一条事实都必须用片段自己的编号标出来源，例如 `[S1]`、`[S2]`；
   编号必须与片段前缀 `[S1 chunk=… doc=… cat=…]` 里的编号逐字一致。
   不得引用不存在的编号，不得把多个片段的内容混成一条没有编号的陈述。
2. **片段里没有的，一律答「未记载」**：不得用先验知识、其他作品设定、网络资料或推测补全。
   如果片段不足以回答，就直接回答「未记载」，并说明还缺哪一类信息。
3. **不得引入外部游戏知识**：即使你确定某个设定、剧情或角色关系是正确的，只要片段里没有写，
   就不许出现在回答里；也不得引用其他作品或现实世界的资料。

补充要求：
- 用简体中文回答；先给结论，不要复述提示词，也不要大段抄录片段原文。
- 片段之间若互相矛盾，如实指出矛盾并分别给出编号，不要替它们调和。
- 「未记载」是合格回答，不是失败；编造才是。"""

#: 无片段时的占位（不静默省略：【检索片段】段永远存在，回答端看得见"这次是空的"）。
CONTEXT_EMPTY_NOTICE = "（本次检索没有返回任何片段）"


def _raw(obj: Any, key: str) -> Any:
    """鸭子类型取字段：既接受 ``graph_store.Entity`` 这类对象，也接受 dict。"""
    if obj is None:
        return None
    if isinstance(obj, Mapping):
        return obj.get(key)
    return getattr(obj, key, None)


def _text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def render_role_card(ent: Any) -> str:
    """把实体对象渲染成角色卡（鸭子类型：``name`` / ``type`` / ``aliases`` / ``desc``）。

    - **没有名字就返回空串**，不编造：宁可没有角色卡，也不许凭空生成一份人设；
    - 缺 ``desc`` / ``aliases`` 只渲染已有字段，不留空标签；
    - 不 import ``roleplay.*``、不在本包内硬编码任何角色数据（独立性契约，
      ``tests/compendium_rag/test_independence.py`` 是硬门）。
    """
    name = _text(_raw(ent, "name"))
    if not name:
        return ""
    lines = [f"名字：{name}"]
    etype = _text(_raw(ent, "type"))
    if etype:
        lines.append(f"类型：{etype}")
    aliases = _raw(ent, "aliases") or []
    if isinstance(aliases, str):
        aliases = [aliases]
    if isinstance(aliases, (list, tuple, set)):
        cleaned = [_text(a) for a in aliases]
        cleaned = [a for a in cleaned if a]
        if cleaned:
            lines.append("别名：" + "、".join(cleaned[:8]))
    desc = _text(_raw(ent, "desc"))
    if desc:
        lines.append(f"简介：{desc}")
    return "\n".join(lines)


def _normalize_history(history: list[Any] | None) -> list[dict]:
    """把历史收敛成 ``[{"role","content"}]``，保留顺序与角色；取不到角色的项直接跳过。"""
    out: list[dict] = []
    if not history:
        return out
    for item in history:
        role: Any = None
        content: Any = None
        if isinstance(item, Mapping):
            role, content = item.get("role"), item.get("content")
        elif isinstance(item, (tuple, list)) and len(item) == 2:
            role, content = item[0], item[1]
        else:
            role, content = getattr(item, "role", None), getattr(item, "content", None)
        role_s = _text(role)
        if not role_s or content is None:
            continue
        out.append({"role": role_s, "content": str(content)})
    return out


def compose(query: str, context: str, *, role_card: str = "",
            history: list[Any] | None = None) -> list[dict]:
    """装配 OpenAI 风格 messages（纯函数、确定性：同输入必得同输出）。

    固定顺序（本模块的口径，改动即口径变更）：

    1. ``system``     : :data:`ANSWER_SYSTEM_PROMPT`（有 ``role_card`` 时追加【角色卡】段）；
    2. ``history``    : 最近若干轮对话，原样保留角色与顺序（空/缺省则整段不出现）；
    3. 末条 ``user``  : 【检索片段】**逐字**来自 ``context``（不重排、不重新编号）+ 【问题】。

    为什么片段放在**最后一轮 user** 而不是单独一轮：
        证据离问题越近，模型越难「读着读着滑回先验知识」；同时保证
        「末条是 user」这一网关友好形态，多轮 history 不会被截断在证据与问题之间。
    """
    system_parts = [ANSWER_SYSTEM_PROMPT]
    card = _text(role_card)
    if card:
        system_parts.append("【角色卡】\n" + card)
    messages: list[dict] = [{"role": "system", "content": "\n\n".join(system_parts)}]

    messages.extend(_normalize_history(history))

    ctx = (context or "").strip()
    question = _text(query)
    messages.append({"role": "user", "content": "\n".join([
        "【检索片段】",
        ctx if ctx else CONTEXT_EMPTY_NOTICE,
        "【问题】",
        question,
    ])})
    return messages


async def answer(llm: CloudLLM, query: str, context: str, *,
                 role_card: str = "", history: list[Any] | None = None,
                 max_tokens: int | None = None) -> tuple[str, LLMResult]:
    """``compose`` 装配 → ``CloudLLM.complete_text`` 调用，返回（答案文本, 用量元信息）。

    文本模式：**不解析 JSON**，不向网关发 ``response_format``；
    ``meta.finish_reason == "length"`` 说明答案被截断，由调用方按需处置。
    """
    messages = compose(query, context, role_card=role_card, history=history)
    return await llm.complete_text(messages, max_tokens=max_tokens)


def render_prompt(query: str, context: str, *, role_card: str = "",
                  history: list[Any] | None = None) -> str:
    """把 :func:`compose` 的 messages 摊平成**单个字符串**（子代理批次用）。

    WP3/P4.2 的双盲架构里作答方是**子代理**，不是进程内的 ``CloudLLM``：
    ``scripts/audit_l3.py --mode prepare`` 落盘的批次项是
    ``{"qid", "query", "context"}``，子代理读纯文本而不是 messages 数组。
    这个函数就是那层投影——用**同一份** :func:`compose` 产物摊平，保证
    「进程内作答」与「子代理作答」逐字同源；否则两条路径的差异会混进
    L3.4 的 delta，读数无法归因。

    双盲复测请传 ``history=None``（回答端与审查端零共享历史是那套架构的前提）。
    """
    blocks = [f"## {m['role']}\n{m['content']}"
              for m in compose(query, context, role_card=role_card, history=history)]
    return "\n\n".join(blocks)
