"""角色扮演提示词系统（人设 / 语气 / 知识范围 / 行为约束 + RAG 动态注入）。

职责（纯函数，无副作用）：
1. resolve_knowledge_namespaces：由角色卡 knowledge_scope 决定检索命名空间
   —— "知识范围"约束落到检索层，而非仅提示词层。
2. build_rag_context：把检索结果格式化为「角色记忆/资料」提示词块，
   附带来源与使用守则（保持角色口吻、不暴露检索机制、资料缺失不编造）。
3. build_roleplay_prompt：人设提示词（复用 resolve_system_prompt）
   + 语气段 + RAG 上下文块 → 最终 system prompt。

与导入管线的无缝集成：
  document_ingest 按 lore_<character_id> 命名空间入库
  → 角色卡 knowledge_scope 引用同名命名空间
  → 对话时 Orchestrator 按该范围检索并经本模块注入提示词。
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ..models.character import CharacterCard
from ..models.chat import EMOTION_PARENT
from ..models.prompt_config import PromptConfig
from .character_card import render_footer_sections, resolve_system_prompt
from .rag.base import RetrievedChunk

# 未指定知识范围时的公共检索范围（不含 persona：人设已在 system prompt 中）
DEFAULT_RETRIEVAL_NAMESPACES = ["events", "web", "episodic"]

# 绝对分数下限：仅作"垃圾兜底"，用于拦掉退化/异常的低分（如未归一化的 0.01）。
# ⚠️ 不要指望它做相关性判定：_rerank 输出的是**相对归一化**融合分（top1 恒≈1.0），
# 而实测本项目嵌入器（nomic-embed-text + 41 条语料）的原始余弦在相关/无关两组上
# 完全重叠（0.702 vs 0.695），任何绝对阈值都没有判别力。相关性过滤靠下面的相对门。
MIN_CONTEXT_SCORE = 0.05

# 相对门：同一批命中里，分数低于 top1 的该比例的条目视为噪声丢弃。
# 实测（2026-09-01，RAGAS 2.0 评估）：
#   相关条目 ratio 0.89~1.00，噪声条目 ratio ≤0.84（"神秘术"查询的"神秘学家/基金会派系"误匹配）。
#   原 0.6 拦不住噪声（0.84 > 0.6），收紧到 0.85 可完美切分且不误伤相关条目。
RELATIVE_SCORE_GATE = 0.85


def _score_group(meta: dict) -> str:
    """把检索块按「分数尺度」分组——相对门必须在**同尺度内**计算。

    不同通道的分数量纲互不可比，混在一起做相对门会让整条通道被误杀：

    | 通道 | 分数来源 | 量纲 |
    |---|---|---|
    | ``vector`` | 向量库（混合重排后按最大值相对归一化） | top1 恒≈1.0 |
    | ``events`` | 长期记忆（原始余弦，未经混合重排） | 0.5–0.75 |
    | ``plot_graph`` | 剧情图谱（PPR 派生 × confidence） | 0.1–0.2 |
    | ``plot_lexical`` | 剧情词法兜底（BM25 原始分，无上界） | 30–75 |
    | ``profile`` | 用户画像（余弦 × 重要性） | 0–1 |

    历史缺陷：合并列表后套同一个 ``0.85 × top1``，导致 lore 命中强时长期记忆
    被整段丢弃、剧情图谱块被词法块挤掉（见 deliverables/rag-graphrag-audit）。
    """
    via = str(meta.get("via") or "")
    if via in ("plot_graph", "plot_lexical"):
        return via
    ns = str(meta.get("namespace") or "")
    if ns.startswith("events"):
        return "events"
    if ns.startswith("profile"):
        return "profile"
    return "vector"


def _filter_chunks(chunks: list) -> list:
    """低分垃圾过滤 + **按分数尺度分组**的相对门（各上下文块共用）。

    - 绝对下限 ``MIN_CONTEXT_SCORE`` 对所有块生效（拦退化/异常低分）；
    - 相对门 ``0.85 × 同组 top1`` 只在同一分数尺度内计算，避免跨通道误杀；
    - 单条时只走绝对下限（相对门对单条恒成立，无意义且会破坏既有测试语义）；
    - 极端情况下某组全被过滤时，至少保留该组 top1。
    """
    usable = [c for c in chunks if c.score >= MIN_CONTEXT_SCORE and c.text.strip()]
    if len(usable) <= 1:
        return usable
    groups: dict[str, list] = {}
    for c in usable:
        groups.setdefault(_score_group(c.metadata or {}), []).append(c)
    if len(groups) == 1:
        top = max(c.score for c in usable)
        kept = [c for c in usable if c.score >= top * RELATIVE_SCORE_GATE]
        return kept or usable[:1]
    kept_all: list = []
    for group in groups.values():
        top = max(c.score for c in group)
        kept = [c for c in group if c.score >= top * RELATIVE_SCORE_GATE]
        kept_all.extend(kept or group[:1])
    kept_all.sort(key=lambda c: c.score, reverse=True)
    return kept_all

_CONTEXT_HEADER = (
    "【角色资料库（你脑子里浮出来的片段）】\n"
    "以下资料是「你」的记忆、经历与设定依据。使用守则：\n"
    # P0-4：明确资料是「记忆碎片」而非「参考资料」，削弱引用感与拼接感
    "- 这些片段是你脑子里自己冒出来的，不是你在读一份文件；"
    "你可以只取其中一个细节，用自己的话说出来，甚至记错（当资料本身就含糊时）；\n"
    "- 用你自己的口吻把事实揉进对话，像你真的记得这些事；不要念稿、不要逐条罗列、"
    "不要说「根据资料」「检索到」等暴露系统机制的话；\n"
    "- 例：✗「根据资料，重庆工程学院位于巴南区。」"
    "  ✓「巴南区啊……你就在那儿的工程学院念书，对吧？」\n"
    # 忠实性约束（按 RAGAS Faithfulness 标准收紧）：
    # 允许演绎"怎么说"（语气/情绪/修辞），禁止编造"说什么"（具体事实）。
    # 旧措辞"资料未覆盖的细节可以合理演绎"经实测会诱发幻觉
    # （模型补全心理活动与关系细节，Faithfulness 曾掉到 0.50），故改为显式边界。
    "- 回答须与资料一致。可以演绎的只有口吻、情绪和修辞——把事实用「我」的说法讲出来；\n"
    "- 不得添加资料里没有的具体事实：不要编造经历经过、人物关系细节、他人的台词，"
    "也不要断言角色的心理动机；\n"
    "- 资料没提到的事，宁可留白、含糊带过，或直接说不确定，也不要自行补全；\n"
    "- 可以用比喻或修辞，但修辞之后必须带出至少一个资料里的具体事实，"
    "避免只剩意象而没有信息量；\n"
    "- 问「是什么」「谁」这类事实问题时，先直接给出资料里的事实，"
    "修辞和情绪只能做点缀，不能替代事实；\n"
    "- 资料与对话无关时忽略即可，不要生硬引用。"
)

# 剧情记忆块默认字符预算（独立于 rag 块的 3200）
_PLOT_MAX_CHARS = 1000

# 剧情记忆块头（PlotGraph：独立于【角色资料库】，实际剧情的回忆）
_PLOT_HEADER = (
    "【剧情记忆（你亲身经历过的事）】\n"
    "下面是你亲身经历过的剧情片段。使用守则：\n"
    "- 这是你的**经历**而不是档案：用「我」的口吻讲，像在回忆当时在场的事；\n"
    "- 只讲片段里真正发生过的事，不要补全动机、他人台词或没写出来的细节；\n"
    "- 片段来自语音转写，可能有听错的词——拿不准就说记不清，别硬说；\n"
    "- 与当前话题无关时忽略即可，不要主动报流水账。"
)

# 用户画像块头（ADR-5：人设 → 语气 → 【用户资料】→ 【角色资料库】）
_PROFILE_HEADER = (
    "【用户资料】\n"
    "以下是你对这位用户的了解（来自历史对话的沉淀），自然运用，不要提及系统机制；"
    "与当前话题无关时忽略即可。"
)


def _events_ns(character_id: str | None) -> str:
    """长期记忆命名空间：按角色隔离（namespace-per-tenant）。

    无角色（单角色/默认模式）时回退公共 events，避免隔离落空。
    """
    return f"events:{character_id}" if character_id else "events"


def resolve_knowledge_namespaces(
    card: CharacterCard | None, character_id: str | None = None
) -> list[str]:
    """知识范围 → 检索命名空间列表。空/未设置回退公共范围。

    character_id 非空时，把占位 "events" 映射到该角色的隔离命名空间
    events:<character_id>，实现跨角色长期记忆严格隔离（同角色跨会话仍共享）。
    """
    events = _events_ns(character_id)
    if card is not None and card.knowledge_scope:
        scoped = [ns.strip() for ns in card.knowledge_scope if ns and ns.strip()]
        if scoped:
            return [events if ns == "events" else ns for ns in scoped]
    return [events if ns == "events" else ns for ns in DEFAULT_RETRIEVAL_NAMESPACES]


def _source_label(meta: dict) -> str:
    """检索块 → 简短来源标签（供模型分辨资料出处层级）。"""
    ns = meta.get("namespace", "")
    if ns.startswith("plot_"):
        base = "剧情记忆"
    elif ns.startswith("graph_"):
        base = "关系脉络"
    elif ns.startswith("lore_"):
        base = "角色设定资料"
    elif ns == "events" or ns.startswith("events:"):
        base = "长期记忆"
    elif ns == "episodic":
        base = "对话情节"
    elif ns == "web":
        base = "联网资料"
    elif ns == "profile" or ns.startswith("profile:"):
        base = "用户资料"
    else:
        base = "资料"
    section = meta.get("section") or meta.get("title") or ""
    return f"{base}·{section}" if section else base


def build_rag_context(
    chunks: list[RetrievedChunk], max_chars: int = 3200, header: str | None = None
) -> str:
    """检索结果 → 提示词上下文块。空结果返回空串（调用方直接跳过）。

    条目格式（P0-4）：``（来源标签）正文`` —— 去掉改造前的 ``[1] (来源) 正文``
    编号与半角括号，弱化「引用/清单」感，让模型把资料当成记忆碎片而非参考资料。
    """
    usable = _filter_chunks(chunks)
    if not usable:
        return ""
    lines: list[str] = [header or _CONTEXT_HEADER, ""]
    used = 0
    for c in usable:
        text = c.text.strip()
        if used + len(text) > max_chars and used > 0:
            break
        # 单块就超预算时截断（与 build_plot_context 对齐），保证整块不突破预算
        if len(text) > max_chars:
            text = text[:max_chars].rstrip() + "…"
        used += len(text)
        lines.append(f"（{_source_label(c.metadata)}）{text}")
    return "\n".join(lines)


def build_plot_context(
    chunks: list[RetrievedChunk], max_chars: int = 1000, header: str | None = None
) -> str:
    """剧情图谱检索结果 → 「【剧情记忆】」提示词块。

    与 build_rag_context 同构（复用 _filter_chunks 与 _source_label），但：
    - 独立块头与独立预算（默认 1000 字符），不挤占 lore 资料块；
    - 每条前置 ``（剧情记忆·3.8版本·世纪末的忧郁）`` 来源标签，
      并在末尾附一句关系线索（图谱边），帮助模型把片段接成叙事；
    - 空结果返回空串（调用方跳过，不产生空块）。
    """
    usable = _filter_chunks(chunks)
    if not usable:
        return ""
    lines: list[str] = [header or _PLOT_HEADER, ""]
    used = 0
    for c in usable:
        text = c.text.strip()
        if used + len(text) > max_chars and used > 0:
            break
        # 单块就超预算时截断（语料块偶有超长段落），保证整块不突破预算
        if len(text) > max_chars:
            text = text[:max_chars].rstrip() + "…"
        used += len(text)
        lines.append(f"（{_source_label(c.metadata)}）{text}")
        edge = (c.metadata or {}).get("edge")
        if edge:
            lines.append(f"（关系）{edge}")
    return "\n".join(lines)


# 关系脉络块默认字符预算（lore 知识图谱层，独立于 rag 的 3200）
_GRAPH_MAX_CHARS = 1200

# 关系脉络块头（lore 层 GraphRAG：实体关系子图 + 溯源证据）
_GRAPH_HEADER = (
    "【关系脉络（你记得的人与事之间的联系）】\n"
    "下面是从你的记忆里理出来的关系线索。使用守则：\n"
    "- 这些联系是你本来就知道的，用「我」的口吻自然带出，不要念成清单；\n"
    "- 关系来自转述，可能有误差——拿不准就含糊带过，不要断言具体经过；\n"
    "- 与当前话题无关时忽略即可，不要主动报关系表。"
)


def build_graph_context(
    chunks: list[RetrievedChunk], max_chars: int = 1200, header: str | None = None
) -> str:
    """lore 图谱检索结果 → 「【关系脉络】」提示词块。

    与 build_plot_context 同构（复用 _filter_chunks 与 _source_label）：
    每条含溯源证据正文 + 一行「A —关系→ B」，独立预算，空结果返回空串。
    """
    usable = _filter_chunks(chunks)
    if not usable:
        return ""
    lines: list[str] = [header or _GRAPH_HEADER, ""]
    used = 0
    for c in usable:
        block = f"（{_source_label(c.metadata)}）{c.text.strip()}"
        edge = (c.metadata or {}).get("edge")
        if edge:
            block = f"{block}\n（关系）{edge}"
        if used + len(block) > max_chars and used > 0:
            break
        if len(block) > max_chars:
            block = block[:max_chars].rstrip() + "…"
        used += len(block)
        lines.append(block)
    return "\n".join(lines)


def build_profile_context(
    chunks: list[RetrievedChunk], max_chars: int = 1200, header: str | None = None
) -> str:
    """画像检索结果 → 「【用户资料】」提示词块。

    - 复用 _filter_chunks（低分垃圾过滤 + 相对门）；
    - 每行 ``- (来源) 画像句``（提醒行/检索行统一）；
    - 无条目返回空串（调用方直接跳过，不产生空块）。
    """
    usable = _filter_chunks(chunks)
    if not usable:
        return ""
    lines: list[str] = [header or _PROFILE_HEADER, ""]
    used = 0
    for i, c in enumerate(usable, 1):
        text = c.text.strip()
        if used + len(text) > max_chars and used > 0:
            break
        used += len(text)
        lines.append(f"- ({_source_label(c.metadata)}) {text}")
    return "\n".join(lines)


# P0-2：核心锚点块头（置底最末位，利用近因效应重复强化，对抗角色漂移）
_CORE_ANCHORS_TEMPLATE = "【别忘了你是谁】\n{value}"

# P0-3：情绪策略块头（置底、紧贴风格指令）
_EMOTION_STRATEGY_TEMPLATE = "【此刻对方的状态】\n{value}"


def resolve_emotion_strategy(
    strategies: dict | None, emotion: str | None
) -> str | None:
    """按当前情绪查回应策略：精确键 → EMOTION_PARENT 父类键 → None。

    父类兜底（如 love/grateful/excited → happy）让 15 类标签都能落到策略，
    不必为 8 个新增标签各写一份重复文案。

    未配置策略表 / 情绪为空 / 表里没有对应键（含父类）→ None（零注入）。
    """
    if not strategies or not emotion:
        return None
    key = str(emotion).strip().lower()
    hit = strategies.get(key)
    if hit is None:
        parent = EMOTION_PARENT.get(key)
        if parent:
            hit = strategies.get(parent)
    if not isinstance(hit, str) or not hit.strip():
        return None
    return hit.strip()


def build_core_anchors_block(
    anchors: list[str] | None, template: str | None = None
) -> str:
    """核心锚点列表 → 置底提示词块。空/未配置 → 空串（零回归）。"""
    if not anchors:
        return ""
    items = [a.strip() for a in anchors if isinstance(a, str) and a.strip()]
    if not items:
        return ""
    value = "\n".join(f"- {a}" for a in items)
    return (template or _CORE_ANCHORS_TEMPLATE).format(value=value)


def build_emotion_strategy_block(
    strategy: str | None, template: str | None = None
) -> str:
    """情绪策略文本 → 置底提示词块。None/空 → 空串（零回归）。"""
    if not strategy or not strategy.strip():
        return ""
    return (template or _EMOTION_STRATEGY_TEMPLATE).format(value=strategy.strip())


# ───────────────────────── P1-2：动态长度提示 ─────────────────────────
# 长度分档（按当前用户消息字数）。固定长度会让情绪激烈的场景展不开、
# 轻松闲聊又嫌啰嗦，故按输入规模给出本轮目标句数。
_LENGTH_BANDS = ("1-2 句", "2-4 句", "3-6 句")

# 需要"展开一档"的高唤醒情绪（其余按字数分档即可）。
# love/grateful/excited 归 happy 系，轻盈短句反而更自然，故不入列。
_INTENSE_EMOTIONS = frozenset(
    {
        "angry", "sad", "anxious", "fear", "surprise",
        "disappointed", "lonely", "embarrassed", "confused",
    }
)

# 块头模板（custom_templates.length 可覆盖）
_LENGTH_TEMPLATE = "【本轮长度】这一轮回复控制在 {value}。"


def _length_band(message: str | None) -> int:
    """用户消息字数 → 长度档位索引（0/1/2）。"""
    n = len((message or "").strip())
    if n < 10:
        return 0
    if n <= 30:
        return 1
    return 2


def build_length_hint(
    message: str | None, emotion: str | None = None, template: str | None = None
) -> str:
    """按用户消息长度（+情绪强度）生成本轮目标句数提示。

    - <10 字 → 1-2 句；10–30 字 → 2-4 句；>30 字 → 3-6 句；
    - 命中高唤醒情绪时整体上调一档（情绪激烈时允许展开），封顶 3-6 句。

    由 cfg.dynamic_length 控制是否注入；默认关闭 → 零回归。
    """
    idx = _length_band(message)
    key = str(emotion or "").strip().lower()
    if key in _INTENSE_EMOTIONS:
        idx = min(idx + 1, len(_LENGTH_BANDS) - 1)
    return (template or _LENGTH_TEMPLATE).format(value=_LENGTH_BANDS[idx])


# ───────────────────────── P1-3：情感节奏（防备层） ─────────────────────────
# 块头模板（custom_templates.pacing 可覆盖）
_PACING_TEMPLATE = "【此刻你的姿态】\n{value}"

# 信任层触发所需的累计轮次（默认 6 轮）。
# 说明：真实"信任"应来自用户主动示弱/不追问过去等语义信号，规则层难以可靠判定，
# 故此处用「累计对话轮次」作为可预测、可单测的代理指标；阈值可按角色卡调。
TRUST_TURN_THRESHOLD = 6


def _layer_text(layers: dict, key: str) -> str:
    """取情感层次表中的文本值（非字符串/空白 → 空串）。"""
    raw = layers.get(key)
    return raw.strip() if isinstance(raw, str) else ""


def resolve_pacing_strategy(
    layers: dict | None,
    message: str | None = None,
    *,
    turn_count: int = 0,
    trust_turn_threshold: int = TRUST_TURN_THRESHOLD,
) -> str | None:
    """按「本轮是否踩到敏感话题 / 是否已积累信任」解析本轮情感姿态。

    组合方式（surface 为基线，条件层叠加）：
    - surface：日常基线姿态，恒作底；
    - 命中 trigger_topics（当前用户消息含敏感词）→ 叠加 trigger_reaction（回避/轻描淡写）；
    - 未触发且累计轮次 ≥ trust_turn_threshold → 叠加 trust_reaction（罕见地放下防备）。

    用 elif：被踩到敏感话题时不会同时"敞开心扉"——防备优先，符合角色逻辑。
    未配置 emotional_layers / 各层均无有效文本 → None（零注入，零回归）。
    """
    if not isinstance(layers, dict) or not layers:
        return None
    parts: list[str] = []
    surface = _layer_text(layers, "surface")
    if surface:
        parts.append(surface)

    msg = (message or "").strip()
    topics = [
        t.strip()
        for t in (layers.get("trigger_topics") or [])
        if isinstance(t, str) and t.strip()
    ]
    triggered = bool(msg and topics and any(t in msg for t in topics))
    if triggered:
        reaction = _layer_text(layers, "trigger_reaction")
        if reaction:
            parts.append(reaction)
    elif turn_count >= max(1, int(trust_turn_threshold)):
        reaction = _layer_text(layers, "trust_reaction")
        if reaction:
            parts.append(reaction)

    return "\n".join(parts) or None


def build_pacing_block(
    strategy: str | None, template: str | None = None
) -> str:
    """情感姿态文本 → 提示词块。None/空 → 空串（零回归）。"""
    if not strategy or not strategy.strip():
        return ""
    return (template or _PACING_TEMPLATE).format(value=strategy.strip())


@dataclass
class PromptLayers:
    """P1-1 分层消息结构：system 侧分块 + 紧贴生成点的 user 前缀。

    - system_blocks：核心人设 / 用户画像 / RAG 资料 —— 各自成为**独立** system 消息。
      消息边界比混在一段长文本里更容易被注意力定位，且核心人设居首（首因效应）。
    - user_prefix：情绪策略 / 情感节奏 / 长度 / 风格指令 / 核心锚点 / 复读抑制
      —— 拼在当前 user 消息**之前**，占据近因效应最强的位置（对抗 lost-in-the-middle）。

    未启用分层（默认）时不会构造本对象，仍走单 system 字符串路径。
    """

    system_blocks: list[str] = field(default_factory=list)
    user_prefix: str = ""


def resolve_source_card(
    *,
    card_json: str | None = None,
    default_card: str | None = None,
    card: CharacterCard | None = None,
) -> CharacterCard | None:
    """确定「外层块」应依据哪张卡：请求 card_json > default_card > 传入的 card 对象。

    与 resolve_system_prompt 的采用顺序保持一致——否则请求卡非法时会走到
    fallback_prompt，外层却注入另一张卡的 tone/锚点，产生串味。
    """
    if card_json:
        parsed = CharacterCard.parse_raw_card(card_json)
        if parsed is not None:
            return parsed
        return None
    if default_card:
        parsed_default = CharacterCard.parse_raw_card(default_card)
        if parsed_default is not None:
            return parsed_default
    return card


def resolve_prompt_config(
    *,
    card_json: str | None = None,
    default_card: str | None = None,
    card: CharacterCard | None = None,
    prompt_config: PromptConfig | None = None,
) -> PromptConfig:
    """解析本轮生效的 PromptConfig：实际采用卡片内嵌 > 显式传入（全局）> 默认。

    供 Orchestrator 在**拼装之前**判断开关（如 P1-1 message_layering），
    避免与 _compose_prompt_parts 内部的解析逻辑漂移。
    """
    source_card = resolve_source_card(
        card_json=card_json, default_card=default_card, card=card
    )
    if source_card is not None and source_card.prompt_config is not None:
        return PromptConfig.from_any(source_card.prompt_config)
    return prompt_config or PromptConfig()


def _compose_prompt_parts(
    *,
    card_json: str | None,
    fallback_prompt: str | None,
    default_card: str | None,
    message: str,
    chunks: list[RetrievedChunk] | None = None,
    card: CharacterCard | None = None,
    profile_chunks: list[RetrievedChunk] | None = None,
    plot_chunks: list[RetrievedChunk] | None = None,
    plot_max_chars: int | None = None,
    graph_chunks: list[RetrievedChunk] | None = None,
    graph_max_chars: int | None = None,
    emotion: str | None = None,
    prompt_config: PromptConfig | None = None,
    repetition_block: str | None = None,
    turn_count: int = 0,
) -> tuple[str, list[str], list[str]]:
    """计算提示词的三段：**核心人设 / 上下文块 / 置底块**。

    返回 ``(persona, context_blocks, tail_blocks)``——所有块均已过滤空值，
    调用方决定「拼成一个 system 字符串」还是「拆成多条消息」。

    三段划分（P1-1）：
    - persona        ：resolve_system_prompt 产出的核心人设（首因效应，恒在第一条 system）
    - context_blocks ：tone / profile / rag（动态知识，按 cfg.ordered_fields 排序）
    - tail_blocks    ：情绪策略 → 情感节奏 → footer → 长度 → 核心锚点 → 复读抑制
                       （"怎么说"的动态指令，紧贴生成点）
    """
    cfg = resolve_prompt_config(
        card_json=card_json,
        default_card=default_card,
        card=card,
        prompt_config=prompt_config,
    )
    # 用于外层块（tone / 锚点 / 策略）的卡片必须与 system prompt 实际采用的卡片一致：
    # 请求 card_json 优先；未携带 card_json 时 default_card / CharacterStore card 才生效。
    # 若 card_json 非法，resolve_system_prompt 会走 fallback_prompt，外层也不应注入另一张卡的 tone。
    source_card = resolve_source_card(
        card_json=card_json, default_card=default_card, card=card
    )
    persona = resolve_system_prompt(
        character_card=card_json,
        fallback_prompt=fallback_prompt,
        default_card=default_card,
        message=message,
        emotion=emotion,
        prompt_config=cfg,
        turn_count=turn_count,
    )
    # ── 上下文块：tone / profile / rag（按配置顺序，默认与改造前一致） ──
    blocks: dict[str, str] = {}
    if source_card is not None and source_card.tone and source_card.tone.strip():
        blocks["tone"] = (
            cfg.custom_templates.get("tone") or "【语气要求】{value}"
        ).format(value=source_card.tone.strip())
    profile_ctx = build_profile_context(
        profile_chunks or [],
        header=cfg.header_templates.get("profile"),
    )
    if profile_ctx:
        blocks["profile"] = profile_ctx
    context = build_rag_context(
        chunks or [],
        header=cfg.header_templates.get("rag"),
    )
    if context:
        blocks["rag"] = context
    context_blocks: list[str] = []
    for name in cfg.ordered_fields():
        if name not in ("tone", "profile", "rag"):
            continue
        if not cfg.is_enabled(name):
            continue
        text = blocks.get(name)
        if text:
            context_blocks.append(text)
    # 剧情记忆块：独立于 lore 资料块渲染（独立预算、来源标签），
    # 放在资料块之后、置底指令之前；未启用剧情层时 plot_chunks 为空 → 零注入。
    plot_ctx = build_plot_context(
        plot_chunks or [],
        max_chars=plot_max_chars or _PLOT_MAX_CHARS,
        header=cfg.header_templates.get("plot"),
    )
    if plot_ctx:
        context_blocks.append(plot_ctx)
    # 关系脉络块：lore 层 GraphRAG（实体关系子图 + 溯源证据），独立预算；
    # 图谱层关闭 / 无命中时 graph_chunks 为空 → 零注入（零回归）。
    graph_ctx = build_graph_context(
        graph_chunks or [],
        max_chars=graph_max_chars or _GRAPH_MAX_CHARS,
        header=cfg.header_templates.get("graph"),
    )
    if graph_ctx:
        context_blocks.append(graph_ctx)

    # ── 置底块：动态指令，越靠后越靠近生成点 ──
    tail_blocks: list[str] = []
    if source_card is not None:
        # 1) 情绪策略（P0-3）：按本轮用户情绪动态注入回应策略
        strategy = resolve_emotion_strategy(source_card.emotion_strategies, emotion)
        block = build_emotion_strategy_block(
            strategy, cfg.custom_templates.get("emotion_strategy")
        )
        if block:
            tail_blocks.append(block)
        # 2) 情感节奏（P1-3）：敏感话题 → 回避；信任积累 → 罕见敞开心扉
        pacing = resolve_pacing_strategy(
            source_card.emotional_layers,
            message,
            turn_count=turn_count,
        )
        pacing_block = build_pacing_block(
            pacing, cfg.custom_templates.get("pacing")
        )
        if pacing_block:
            tail_blocks.append(pacing_block)
        # 3) 置底字段 footer_fields：风格/格式指令（比资料块更靠近生成点，
        #    否则模型会模仿紧邻其前的百科/剧本文体）
        if cfg.footer_fields:
            tail_blocks.extend(
                render_footer_sections(
                    source_card, message=message, emotion=emotion, cfg=cfg
                )
            )
        # 4) 动态长度（P1-2）：放在 footer 之后，才能覆盖卡内静态的"每条 2-4 句"
        if cfg.dynamic_length:
            tail_blocks.append(
                build_length_hint(
                    message, emotion, cfg.custom_templates.get("length")
                )
            )
        # 5) 核心锚点（P0-2）：倒数第二段，反复锚定角色核心特质
        anchors_block = build_core_anchors_block(
            source_card.core_anchors, cfg.custom_templates.get("core_anchors")
        )
        if anchors_block:
            tail_blocks.append(anchors_block)
    # 6) 复读抑制块：最末位（紧贴生成点）
    if repetition_block:
        tail_blocks.append(repetition_block)
    return persona, context_blocks, tail_blocks


def build_roleplay_messages(
    *,
    card_json: str | None,
    fallback_prompt: str | None,
    default_card: str | None,
    message: str,
    chunks: list[RetrievedChunk] | None = None,
    card: CharacterCard | None = None,
    profile_chunks: list[RetrievedChunk] | None = None,
    plot_chunks: list[RetrievedChunk] | None = None,
    plot_max_chars: int | None = None,
    graph_chunks: list[RetrievedChunk] | None = None,
    graph_max_chars: int | None = None,
    emotion: str | None = None,
    prompt_config: PromptConfig | None = None,
    repetition_block: str | None = None,
    turn_count: int = 0,
) -> PromptLayers:
    """拼装 P1-1 **分层消息**：核心人设/画像/RAG 各自成 system 消息，动态指令进 user 前缀。

    与 build_roleplay_prompt 共用 _compose_prompt_parts，故两段路径的块内容
    与顺序完全一致，差别只在「拼成一个字符串」还是「拆成多条消息」。

    返回 PromptLayers(system_blocks=[...], user_prefix="...")。
    system_blocks 至少含核心人设（不会为空）；user_prefix 在无置底块时为空串。
    """
    persona, context_blocks, tail_blocks = _compose_prompt_parts(
        card_json=card_json,
        fallback_prompt=fallback_prompt,
        default_card=default_card,
        message=message,
        chunks=chunks,
        card=card,
        profile_chunks=profile_chunks,
        plot_chunks=plot_chunks,
        plot_max_chars=plot_max_chars,
        graph_chunks=graph_chunks,
        graph_max_chars=graph_max_chars,
        emotion=emotion,
        prompt_config=prompt_config,
        repetition_block=repetition_block,
        turn_count=turn_count,
    )
    return PromptLayers(
        system_blocks=[persona, *context_blocks],
        user_prefix="\n\n".join(tail_blocks),
    )


def build_roleplay_prompt(
    *,
    card_json: str | None,
    fallback_prompt: str | None,
    default_card: str | None,
    message: str,
    chunks: list[RetrievedChunk] | None = None,
    card: CharacterCard | None = None,
    profile_chunks: list[RetrievedChunk] | None = None,
    plot_chunks: list[RetrievedChunk] | None = None,
    plot_max_chars: int | None = None,
    graph_chunks: list[RetrievedChunk] | None = None,
    graph_max_chars: int | None = None,
    emotion: str | None = None,
    prompt_config: PromptConfig | None = None,
    repetition_block: str | None = None,
    turn_count: int = 0,
) -> str:
    """拼装最终 system prompt：人设 → 语气 → 【用户资料】→ 【角色资料库】。

    - card_json/default_card/fallback_prompt：与 resolve_system_prompt 语义一致；
    - card：已解析的角色卡对象（仅当请求未携带 card_json/default_card 时，
      用于 tone 追加与 prompt_config，可为 None）；
    - chunks：本轮 RAG 检索结果，格式化后追加在末尾；
    - profile_chunks：本轮用户画像检索结果 + 提醒行，插在语气之后、RAG 之前；
    - emotion：当前轮情绪标签（结构化行为规则 emotion_is 条件用）；
    - prompt_config：显式配置（全局层传入）；角色卡内嵌 prompt_config 优先于它。
    - repetition_block：复读抑制负向提示块（repetition_guard 渲染），
      追加在最末尾（比 footer 更靠近生成点）；None 时输出与改造前一致。
    - turn_count：本会话累计轮次（P1-3 情感节奏的信任层判据）。

    置底块顺序（自前向后，越靠后越靠近生成点）：
      资料块 → 情绪策略（P0-3）→ 情感节奏（P1-3）→ footer_fields
      → 动态长度（P1-2）→ 核心锚点（P0-2）→ 复读抑制

    动态长度放在 footer 之后：footer 里通常写着卡内静态的「每条 2-4 句」，
    后出的指令才能覆盖它。

    字段开关（升级方案 D）：enabled_fields/field_order/custom_templates 控制
    tone / profile / rag 块；默认配置输出与改造前逐字节一致。
    custom_templates 另支持的置底块模板键：
      emotion_strategy / pacing（P1-3）/ length（P1-2）/ core_anchors。
    """
    # 与 build_roleplay_messages 共用同一套分块逻辑（P1-1），
    # 差别仅在「拼成一个 system 字符串」还是「拆成多条消息」。
    persona, context_blocks, tail_blocks = _compose_prompt_parts(
        card_json=card_json,
        fallback_prompt=fallback_prompt,
        default_card=default_card,
        message=message,
        chunks=chunks,
        card=card,
        profile_chunks=profile_chunks,
        plot_chunks=plot_chunks,
        plot_max_chars=plot_max_chars,
        graph_chunks=graph_chunks,
        graph_max_chars=graph_max_chars,
        emotion=emotion,
        prompt_config=prompt_config,
        repetition_block=repetition_block,
        turn_count=turn_count,
    )
    return "\n\n".join([persona, *context_blocks, *tail_blocks])
