"""剧情图谱层（PlotGraph）：用 GraphRAG 存**实际剧情**（B站转写文案）。

与现有 RAG 的隔离边界（docs/GRAPHRAG加强计划书.md §16）：

| 维度 | 现有 RAG（lore 层） | 剧情图谱（plot 层） |
|---|---|---|
| 数据源 | 9 份手工资料（+已混入的转写块） | 仅 266 份机器转写 md |
| 命名空间 | ``lore_<cid>`` | ``plot_<cid>`` |
| 落盘 | ``data/knowledge/lore_<cid>.json``（含 768 维向量） | ``plot_corpus_<cid>.json``（纯文本）+ ``plot_graph_<cid>.json``（图） |
| 检索 | 向量 + BM25 混合 | 实体链接 + PPR + 词法兜底（**零嵌入依赖**） |
| 开关 | ``rag_enabled`` / ``graph_enabled`` | ``plot_graph_enabled``（默认关） |
| 依赖 | embedder / KnowledgeBase | 无（可离线独立构建与检索） |

两条链路的文件、索引、开关、预算、来源标签全部互不引用：
``plot_graph_enabled=False``（默认）时，lore 检索路径与现状逐字节一致。

语言处理（约束①）：英配视频正文为英文，逐块按语种选择抽取提示词；
实体名保留原文语种，关系谓语统一用中文；跨语言同指靠
``data/lore/<cid>/plot_aliases.json`` 双语别名表归并（bind_alias_table）。
"""
from __future__ import annotations

import asyncio
import json
import logging
import math
import re
from pathlib import Path

from ...core.rag.base import RetrievedChunk  # 复用检索块结构，便于统一渲染
from .graph_ppr import (
    WEAK_EVIDENCE_MIN,
    build_adjacency,
    filter_edges,
    hop_distance,
    personalized_pagerank,
)
from .graph_store import (
    GraphStore,
    build_local_endpoint_map,
    norm_name,
    resolve_endpoint,
)
from .plot_corpus import PlotCorpus, plot_namespace, tokenize
from .relation_vocab import (
    RELATION_RULES_PROMPT,
    canonicalize_relation,
    vocab_prompt_block,
)

logger = logging.getLogger(__name__)

# 剧情图谱 schema 版本（与 lore 图谱 v1 区分，互不兼容触发重建提示）
PLOT_GRAPH_SCHEMA = "plot-v1"

# 转写证据的 importance：低于 lore 手工资料（0.7），防 ASR 噪声长入主干
IMPORTANCE_TRANSCRIPT = 0.6
# 证据条数 < 2 的边视为「孤证」：ASR 误识别风险高，默认不注入上下文
# （WEAK_EVIDENCE_MIN 定义在 graph_ppr，与 PPR 传播口径共用同一常量）

# ── P2 融合分数带 ──
# 融合后把分数映射到 [0.6, 1.0]：下界必须高于 persona_prompt.MIN_CONTEXT_SCORE(0.05)，
# 否则剧情块会被绝对门整批滤掉；上界 1.0 表示"本通道融合最强"。
FUSE_MIN_SCORE = 0.6
FUSE_MAX_SCORE = 1.0
# 同一块被多路命中时的主 path 归属（数字大者优先）：结构化的边证据最有解释力
FUSE_PATH_PRIORITY = {"edge": 3, "mention": 2, "lexical": 1}


# ── 语言感知抽取提示词 ──
_JSON_SPEC = (
    '{"entities": [{"name": "<canonical 称呼>", '
    '"type": "角色|物品|地点|组织|概念|事件", "aliases": ["<同指的曾用名/代称/昵称>"]}], '
    '"relations": [{"src": "<实体名>", "dst": "<实体名>", "relation": "<简短中文谓语>", '
    '"confidence": 0.0-1.0}]}'
)

# 关系受控词表段（与 lore 层共用同一份 relation_vocab，两处提示词永不漂移）：
# 显式枚举允许的关系类型 + 禁止否定谓语 + 长度/标点/黑名单卫生规则。
_VOCAB_RULES = RELATION_RULES_PROMPT + "（受控词表：" + vocab_prompt_block() + "）"

EXTRACT_PROMPT_ZH = (
    "你是剧情知识图谱构建助手。下面是一段《重返未来：1999》剧情解说/实录的"
    "**机器转写**文本（可能含识别错误、缺标点、口语重复）。抽取实体与关系，只输出单行 JSON："
    + _JSON_SPEC
    + "规则："
    "- 实体名取文中最正式的称呼；代词不作实体，但其同指要收进 aliases；"
    + _VOCAB_RULES
    + "- confidence：文中明确陈述 ≥0.9；强推断 0.6-0.8；模糊 ≤0.5 或疑似转写错误则**不输出**；"
    "- 遇到明显是识别错误的词（同音错别字、无意义音节）直接忽略，不要造实体；"
    "- src/dst 必须出现在 entities 的 name 或 aliases 中；"
    '- 无可抽取内容输出 {"entities":[],"relations":[]}。'
)

EXTRACT_PROMPT_EN = (
    "你是剧情知识图谱构建助手。下面是一段《重返未来：1999》(Reverse: 1999) 剧情的"
    "**英文语音转写**文本（可能含识别错误）。抽取实体与关系，只输出单行 JSON：" + _JSON_SPEC + "规则："
    "- 实体名保留英文原文（用文中最正式的称呼，如 'Madam Lucy'），并把去掉称谓的"
    "  短形式（'Lucy'）与你有把握的**中文译名**一并放进 aliases；"
    "- **relation 必须写简短中文谓语**，不要英文长句——图谱检索与提示词渲染统一用中文谓语；"
    + _VOCAB_RULES
    + "- confidence：文中明确陈述 ≥0.9；强推断 0.6-0.8；模糊 ≤0.5 或疑似转写错误则**不输出**；"
    "- 忽略语气词、重复句与明显识别错误（同音词、无意义音节），不要为它们造实体；"
    "- src/dst 必须出现在 entities 的 name 或 aliases 中；"
    '- 无可抽取内容输出 {"entities":[],"relations":[]}。'
)


def prompt_for_lang(lang: str) -> str:
    """按 chunk 语种选抽取提示词（other → 中文提示词兜底）。"""
    return EXTRACT_PROMPT_EN if lang == "en" else EXTRACT_PROMPT_ZH


# ── 转写噪声实体过滤（建图时丢弃，防 ASR 残句长入图谱）──
# 实测噪声形态：称谓/语气词（ma'am、senora、Senorita）、冠词开头的句子片段
# （An exorcist、the eyes hiding in the shadows）、含句子标点的转写残句
# （It's alright, truly.）——它们会抢占正牌实体的别名索引。
_NOISE_CANONICAL = {
    "ma'am", "senora", "señora", "senorita", "señorita", "madam", "sir",
    "miss", "mister", "mr", "ms", "mrs", "dr", "okay", "alright", "truly",
    "sorry", "please", "thank you", "excuse me", "everyone", "somebody",
}

# ── 人称代词 / 泛指名词（约束①：代词不作实体）──
# 本地 7B 模型违反抽取提示词，把 you/she/he/her/we/they/girl/friend 等当成实体
# 正名抽取，实测污染 20 个实体 + 186 条边，且「she」这类词会抢占别名索引、
# 让 PPR 激活扩散到无关实体。此类正名一律在建图时丢弃（含其参与的边）。
# 注意：仅当**正名**命中才丢弃；作为关系端点时 link_exact 解析不到即自然丢弃。
_PRONOUN_CANONICAL = {
    # 人称代词（主格/宾格/所有格/反身）
    "i", "me", "my", "mine", "myself", "you", "your", "yours", "yourself",
    "he", "him", "his", "himself", "she", "her", "hers", "herself",
    "it", "its", "itself", "we", "us", "our", "ours", "ourselves",
    "they", "them", "their", "theirs", "themselves",
    # 指示/不定/疑问代词
    "this", "that", "these", "those", "who", "whom", "whose", "what",
    "which", "someone", "somebody", "something", "anyone", "anybody",
    "anything", "nobody", "nothing", "none", "one", "ones", "all", "both",
    "each", "either", "neither", "some", "any", "most", "others", "other",
    # 泛指名词（非任何角色的 canonical 称呼）
    "people", "person", "man", "woman", "child", "children", "boy", "girl",
    "friend", "friends", "enemy", "enemies", "stranger", "somebody else",
    # 中文代词 / 泛指：本地模型同样会把「她/他/你/我们」当实体正名抽出来，
    # 且与英文代词一样会造成无效边（实测 16 块缓存含 18 个）。
    "她", "他", "它", "你", "我", "您", "我们", "你们", "他们", "她们", "它们",
    "咱们", "咱", "大家", "某人", "有人", "众人", "对方", "彼此",
}
_RE_HONORIFIC_PREFIX = re.compile(
    r"^(?:mr|mrs|ms|dr|st|saint|madam|sir|lady|lord)\.?\s+", re.IGNORECASE
)
_RE_ARTICLE_PREFIX = re.compile(r"^(?:a|an|the)\s+", re.IGNORECASE)
_RE_SENTENCE_MARK = re.compile(r"[,.!?;:]")
# 版本号实体（1.4版本 / 3.7版本PV）：是元数据不是剧情实体，且「版本」词元
# 会污染链接种子
_RE_VERSION_ENTITY = re.compile(r"^\d+\.\d+\s*版本", re.IGNORECASE)

# ── 泛词种子黑名单（P3 门控）──
# 实测（300 题 + 10 条离题负样本）：图里混着大量"世界常识泛词"实体——它们因为
# 转写里有人聊天气/经济/三餐而被抽出来，甚至带 1–11 条边。离题问句一旦精确命中
# 这些名字，就会拿到 5–7 块剧情上下文注入人设提示词（实测「今天天气怎么样」→ 5 块）。
# 这张表只收**与作品无关的世界常识泛词**，不收剧情专名（圣火/雅典/伦敦/灯塔/钥匙/
# 十字街/滚鳄书店 等实测是题集里的有效种子，一律保留）。
GENERIC_SEED_NAMES = frozenset(
    {
        # 中文：日常/世界常识
        "天气", "气候", "春天", "夏天", "秋天", "冬天", "季节",
        "经济", "股市", "房价", "新闻", "广告", "会议", "上班", "下班",
        "时间", "名字", "故事", "笑话", "诗歌", "机器", "软件", "电脑",
        "手机", "网络", "游戏", "电影", "音乐", "咖啡", "茶", "餐厅",
        "饭店", "食物", "早餐", "午餐", "晚餐", "城市", "国家", "世界",
        "朋友", "家人", "旅行", "假期", "考试", "学校", "医院", "银行",
        # 英文：日常/世界常识（转写里高频的口语名词）
        "weather", "time", "times", "day", "days", "week", "year", "years",
        "story", "stories", "name", "names", "thing", "things", "stuff",
        "place", "places", "world", "people", "person", "man", "woman",
        "girl", "boy", "young lady", "friend", "friends", "family",
        "restaurant", "food", "water", "coffee", "tea", "movie", "music",
        "game", "computer", "phone", "software", "machine", "city", "country",
        "money", "job", "work", "school", "hospital", "bank", "holiday",
        "joke", "poem", "news", "economy", "weather report",
    }
)


def is_generic_seed_name(name: str) -> bool:
    """种子名是否为「世界常识泛词」（P3 门控用；剧情专名一律返回 False）。"""
    return norm_name(name) in GENERIC_SEED_NAMES


def is_noise_entity(name: str) -> bool:
    """判定抽取正名是否为转写噪声（句子片段/称谓/语气词）。

    中文名不受影响；正常英文名（含 ``Madam Lucy``、``St. Pavlov Foundation``
    这类敬称/缩写开头）也不受影响。
    """
    n = (name or "").strip()
    if len(n) < 2:
        return True
    low = n.lower()
    # 代词判定必须**早于**中文提前返回：否则「我们/他们」这类中文代词会
    # 被下面的 CJK 分支判为合法正名（实测图内已混入「我们」实体）。
    if low in _NOISE_CANONICAL or low in _PRONOUN_CANONICAL:
        return True
    if _RE_VERSION_ENTITY.match(n):
        return True
    if re.search(r"[\u4e00-\u9fff]", n):
        return False
    core = _RE_HONORIFIC_PREFIX.sub("", n)
    if _RE_ARTICLE_PREFIX.match(core):
        return True
    if _RE_SENTENCE_MARK.search(core):
        return True
    return len(core.split()) >= 4  # ≥4 个拉丁词 → 句子片段


def rescue_noise_entity(entity: dict) -> dict | None:
    """name 命中噪声但存在干净别名时，把别名升为正名（name 与该别名互换）。

    ``is_noise_entity`` 5 类误杀（``T.Kettler`` / ``the Sixes`` / ``mine`` /
    单字母 ``Z`` / ≥4 词机构名）的打捞路径：过滤器保持严格（句子片段绝不进图），
    但 worker 把完整形式写进 ``aliases`` 时信息不再丢——取第一个干净别名当正名，
    原噪声 name 降级为别名（端点解析靠别名索引仍可命中）。
   无可打捞别名时返回 ``None``（调用方按噪声丢弃计数）。
    """
    name = str(entity.get("name") or "").strip()
    aliases = [
        str(a).strip()
        for a in (entity.get("aliases") or [])
        if str(a).strip()
    ]
    for i, alias in enumerate(aliases):
        if alias != name and not is_noise_entity(alias):
            rescued = dict(entity)
            rescued["name"] = alias
            rest = [a for j, a in enumerate(aliases) if j != i]
            rest.append(name)
            rescued["aliases"] = rest
            return rescued
    return None


def _substantial_tokens(text: str) -> set[str]:
    """有区分度的词元：拉丁词与 CJK 二元组（CJK 单字如「生」「了」太泛，弃用）。"""
    return {t for t in tokenize(text) if len(t) >= 2}


# 提及命中缓存的「未命中」哨兵：与「命中但零次」({} 空字典) 严格区分。
_MISS = object()


# ── 跨语言别名表 ──
def _coerce_aliases(value: object) -> tuple[list[str], bool]:
    """单个条目的 value → 别名列表；返回 ``(别名列表, 是否因类型非法被丢弃)``。

    防御点（实测踩过）：旧实现 ``[str(a).strip() for a in (v or [])]`` 在 value
    是**字符串**时会逐字符迭代，产出 ``["m","a","d","a","m"]`` 这种单字符"别名"，
    污染别名索引并抢占正牌实体的链接。这里按类型分派：

    - ``str``  → 当单个别名处理（``"Lucy"`` → ``["Lucy"]``）；
    - ``list``/``tuple`` → 逐项 ``str().strip()``，去空；
    - 其他（dict/int/None/bool…）→ 丢弃并计 ``dropped_bad_type``。
    """
    if isinstance(value, str):
        alias = value.strip()
        return ([alias] if alias else []), False
    if isinstance(value, (list, tuple)):
        out: list[str] = []
        for item in value:
            if item is None:
                continue
            s = str(item).strip()
            if s:
                out.append(s)
        return out, False
    return [], True


def load_alias_table(path: str | Path) -> dict[str, list[str]]:
    """加载 ``plot_aliases.json``：{canonical: [alias...]}（人工维护，权威）。

    签名与返回类型保持不变（老调用方零改动）；需要丢弃统计时用
    :func:`load_alias_table_with_stats`。
    """
    table, _stats = load_alias_table_with_stats(path)
    return table


def load_alias_table_with_stats(
    path: str | Path,
) -> tuple[dict[str, list[str]], dict]:
    """同 :func:`load_alias_table`，额外返回丢弃统计（M0-5 观测性）。

    统计键：
    - ``total``：读到的顶层条目数；
    - ``kept``：成功保留的条目数（含空别名表的正名锚定条目）；
    - ``aliases``：保留下来的别名总条数；
    - ``dropped_underscore``：``_`` 开头的元数据键（如 ``_meta``/``_note``）被跳过数；
    - ``dropped_bad_type``：value 既非 str 也非 list/tuple 被丢弃数；
    - ``dropped_empty``：正名为空被丢弃数。
    """
    p = Path(path)
    stats = {
        "total": 0,
        "kept": 0,
        "aliases": 0,
        "dropped_underscore": 0,
        "dropped_bad_type": 0,
        "dropped_empty": 0,
    }
    if not p.is_file():
        return {}, stats
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        logger.warning("剧情别名表解析失败 %s：%s", p, exc)
        return {}, stats
    if not isinstance(data, dict):
        logger.warning("剧情别名表顶层非 object，已忽略：%s", p)
        return {}, stats

    table: dict[str, list[str]] = {}
    for key, value in data.items():
        stats["total"] += 1
        raw_key = str(key).strip()
        # 元数据键（plot_glossary.json 的 _meta / 各段的 _note）：不是术语，跳过
        if raw_key.startswith("_"):
            stats["dropped_underscore"] += 1
            continue
        if not raw_key:
            stats["dropped_empty"] += 1
            continue
        aliases, bad_type = _coerce_aliases(value)
        if bad_type:
            stats["dropped_bad_type"] += 1
            logger.warning(
                "剧情别名表条目 %r 的 value 类型非法（%s），已丢弃：%s",
                raw_key,
                type(value).__name__,
                p,
            )
            continue
        table[raw_key] = aliases
        stats["aliases"] += len(aliases)
        stats["kept"] += 1
    return table, stats


# 英文转写里常见的句首词/语气词，挖掘候选实体时剔除
_EN_NOISE_TOKENS = {
    # 句首高频词 / 语气词（转写里几乎每段开头都有，纯噪声）
    "I", "The", "A", "An", "And", "But", "So", "If", "Then", "What", "Who", "How",
    "Why", "When", "Where", "Yes", "No", "Okay", "Oh", "Ah", "Well", "Now", "This",
    "That", "These", "Those", "There", "Here", "You", "We", "They", "He", "She",
    "It", "My", "Your", "His", "Her", "Its", "Our", "Their", "Sorry", "Listen",
    "Pardon", "Right", "Sure", "Look", "Come", "Wait", "Please", "Thank", "Thanks",
    "Good", "Great", "Alright", "Hey", "Hmm", "Mr", "Ms", "Madam", "Sir", "Mrs",
    "Dr", "Just", "Let", "Don", "Not", "Are", "All", "Our", "For", "Maybe", "Even",
    "Perhaps", "Did", "Have", "Has", "Had", "Take", "Can", "Could", "Would", "Should",
    "One", "Everyone", "Everybody", "Everything", "Nothing", "Something", "Anything",
    "Though", "Although", "Still", "After", "Before", "Like", "Some", "Understood",
    "Because", "Since", "However", "Actually", "Really", "Very", "Much", "Many",
    "More", "Most", "Other", "Another", "Each", "Every", "Both", "Either", "Neither",
    "Which", "While", "Until", "Unless", "Whether", "Besides", "Also", "Too", "Again",
    "Once", "Soon", "Later", "Today", "Tomorrow", "Yesterday", "Always", "Never",
    "Often", "Sometimes", "Indeed", "Certainly", "Enough", "About", "Over", "Under",
    "Into", "Out", "Up", "Down", "Off", "On", "In", "At", "To", "Of", "With", "From",
    "By", "As", "Do", "Does", "Done", "Go", "Gone", "Get", "Got", "Make", "Made",
    "Know", "Knew", "Think", "Thought", "See", "Saw", "Say", "Said", "Tell", "Told",
    "Want", "Need", "Must", "Shall", "Will", "Won", "Isn", "Aren", "Wasn", "Weren",
    "Let's", "That's", "It's", "There's", "Here's", "What's", "Who's", "How's",
}

RE_CANDIDATE = re.compile(r"\b(?:[A-Z][a-z]{2,}|[A-Z]{2,})\b(?:\s+(?:of|the|von|de|van))?(?:\s+\b(?:[A-Z][a-z]{2,}|[A-Z]{2,})\b){0,2}")


def mine_entity_candidates(corpus: PlotCorpus, top_n: int = 300) -> list[tuple[str, int]]:
    """从英文转写块挖掘候选专名（纯规则，供人工/LLM 译名对照）。"""
    freq: dict[str, int] = {}
    for c in corpus.chunks:
        if c.lang != "en":
            continue
        for m in RE_CANDIDATE.finditer(c.text):
            name = m.group(0).strip()
            first = name.split()[0]
            if first in _EN_NOISE_TOKENS or name in _EN_NOISE_TOKENS:
                continue
            if len(name) < 3:
                continue
            freq[name] = freq.get(name, 0) + 1
    ranked = sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))
    return ranked[: max(1, top_n)]


# ── 检索 ──
class PlotGraphRetriever:
    """剧情图谱检索：实体链接 → PPR 激活 → 证据回查语料（+ 词法兜底）。"""

    def __init__(
        self,
        corpus: PlotCorpus,
        store: GraphStore,
        *,
        namespace: str = "",
        min_confidence: float = 0.6,
        include_weak: bool = False,
        max_edges: int = 10,
        max_hops: int = 2,
        damping: float = 0.85,
        max_iter: int = 40,
        link_threshold: float = 0.5,
        mention_cache_size: int = 512,
        fuse_k: int = 3,
        weight_edge: float = 1.0,
        weight_mention: float = 1.0,
        weight_lexical: float = 0.6,
        diversity_per_doc: int = 1,
        require_anchored_token_seeds: bool = True,
        filter_generic_seeds: bool = True,
        mention_scoring: str = "count",
        cooccurrence_bonus: bool = True,
        mention_group_by_entity: bool = True,
    ) -> None:
        self.corpus = corpus
        self.store = store
        self.namespace = namespace or "plot"
        self.min_confidence = min_confidence
        self.include_weak = include_weak
        self.max_edges = max_edges
        self.max_hops = max_hops
        self.damping = damping
        self.max_iter = max_iter
        self.link_threshold = link_threshold
        # P2 融合参数（RRF：见 _fuse_channels）
        self.fuse_k = max(1, int(fuse_k))
        self.weight_edge = float(weight_edge)
        self.weight_mention = float(weight_mention)
        self.weight_lexical = float(weight_lexical)
        # 同一 doc（同一支视频/同一分P）在最终结果里的软上限：先按此去冗余，
        # 名额没填满时再放宽（避免"多样性"把返回条数压到 1 条，反而丢掉证据覆盖）
        self.diversity_per_doc = max(1, int(diversity_per_doc))
        # P3 种子门控（见 seed_gate / GENERIC_SEED_NAMES）
        self.require_anchored_token_seeds = bool(require_anchored_token_seeds)
        self.filter_generic_seeds = bool(filter_generic_seeds)
        # P2 提及打分模式（"count" = 旧口径；"idf" = 稀有名字加权，实测更差，见消融）
        self.mention_scoring = str(mention_scoring)
        self.cooccurrence_bonus = bool(cooccurrence_bonus)
        self.mention_group_by_entity = bool(mention_group_by_entity)
        self._entities_cache: list[dict] | None = None
        # 种子实体提及块挖掘（P0 融合策略）的惰性缓存：
        # 小写文本副本（CJK/拉丁名一次归一，多次查询复用）+ 拉丁词边界正则缓存
        self._low_texts_cache: list[str] | None = None
        self._name_pat_cache: dict[str, re.Pattern[str] | None] = {}
        # ── P1 性能缓存（全部随 store.revision / 重建而失效）──
        # 名字 → {块下标: 精确命中次数}：旧实现对每个名字全扫 8358 块，是检索热路径
        # 上唯一的秒级开销；这里按归一名字缓存（FIFO 上限 mention_cache_size）。
        self._mention_hits_cache: dict[str, dict[int, int] | None] = {}
        self._mention_cache_size = max(1, int(mention_cache_size))
        # hash → 块下标（候选 hash 集 → 下标集合，用于提及计数）
        self._hash_idx_cache: dict[str, int] | None = None
        # 实体 (eid, 正名归一名, [名字归一名...])：避免每查询对 14938 个别名重跑 norm_name
        self._named_cache: list[tuple[str, str, list[str]]] | None = None
        self._canon_map_cache: dict[str, str] = {}
        # 名字 → 有区分度词元（词法兜底打分复用，避免每查询重算 14k 次 tokenize）
        self._name_tokens_cache: dict[str, frozenset[str]] = {}
        # 过滤后的边表 + PPR 邻接 + hop 邻接，键为 (revision, min_confidence, include_weak)
        self._graph_view_cache: tuple[tuple, list[dict], tuple, dict[str, list[str]]] | None = None

    # —— 实体链接 ——
    def _entities(self) -> list[dict]:
        if self._entities_cache is None:
            self._entities_cache = self.store.entities()
        return self._entities_cache

    def _named_entities(self) -> list[tuple[str, str, list[str]]]:
        """``(eid, 正名归一名, [名字归一名...])`` 预计算表（P1）。

        旧实现每次 ``link()`` 都对 6814 实体 × 14938 别名重跑 ``norm_name``（unicode
        归一化不便宜），单查询实测 10–17ms 全花在这上面。名字只随图内容变化，
        故与 ``_entities_cache`` 同生命周期缓存一次。
        """
        if self._named_cache is None:
            named: list[tuple[str, str, list[str]]] = []
            canon: dict[str, str] = {}
            for ent in self._entities():
                eid = str(ent.get("id"))
                raw = [str(ent.get("name") or "")] + [
                    str(a) for a in (ent.get("aliases") or [])
                ]
                cnorm = norm_name(raw[0])
                canon[eid] = cnorm
                named.append((eid, cnorm, [norm_name(n) for n in raw]))
            self._named_cache = named
            self._canon_map_cache = canon
        return self._named_cache

    def _tokens_of(self, name: str) -> frozenset[str]:
        """名字的有区分度词元（缓存）：词法兜底打分旧实现每次查询重算 14k 次 tokenize。"""
        cached = self._name_tokens_cache.get(name)
        if cached is None:
            cached = frozenset(_substantial_tokens(name))
            self._name_tokens_cache[name] = cached
        return cached

    def link(self, query: str) -> dict[str, float]:
        """查询 → {eid: weight}：精确别名最长匹配 → 词元 BM25 兜底。

        精确匹配同长并列时按「正名命中 > mentions 高」排序且至多取 3 个
        种子——防止同一别名被多个（噪声）实体共享时种子爆炸
        （实测「露西女士是谁」曾带出 11 个种子）。
        """
        return {eid: info["weight"] for eid, info in self.link_detailed(query).items()}

    def link_detailed(self, query: str) -> dict[str, dict]:
        """同 :meth:`link`，但附带命中来源，供 P3 种子门控使用。

        返回 ``{eid: {"weight", "path": "exact"|"token", "name": 命中的归一名}}``。
        路径信息是门控的关键：实测 300 题里 293 题走精确匹配，只有 7 题落到词元兜底
        （且这 7 题的兜底种子全是「找到他发生了什么」这类碎片）——而离题问句
        （「推荐几家附近的餐厅」「用 Python 写一个快速排序」）几乎全靠词元兜底
        蹭上「restaurant」「this place」这类实体。因此词元兜底种子必须另有锚定才可用。
        """
        q = query or ""
        if not q:
            return {}
        qn = norm_name(q)
        named = self._named_entities()
        canon_map = self._canon_map_cache
        # ① 精确匹配：实体正名与别名的**最长**命中优先（避免「露西」命中「露西娅」短名）
        best_len = 0
        matches: dict[str, str] = {}  # eid -> 命中的归一名
        for eid, _canon, names in named:
            for nn in names:
                if not nn or nn not in qn:
                    continue
                if len(nn) < 2:
                    # 单字默认跳过（ASR 噪声别名多），但**单字母拉丁别名**例外：
                    # 如 Jay 的别名 "J"——只有它在查询里独立成词（严格词边界）
                    # 时才命中，避免 "j" 命中 "joy" 这类子串误伤。
                    if not (
                        len(nn) == 1
                        and re.fullmatch(r"[a-z0-9]", nn)
                        and re.search(
                            r"(?<![a-z0-9])" + re.escape(nn) + r"(?![a-z0-9])", qn
                        )
                    ):
                        continue
                # 拉丁名按词边界匹配，避免 "ania" 命中 "mania"
                if re.fullmatch(r"[a-z0-9 ]+", nn) and not re.search(
                    r"(?<![a-z0-9])" + re.escape(nn) + r"(?![a-z0-9])", qn
                ):
                    continue
                if len(nn) > best_len:
                    best_len = len(nn)
                    matches = {eid: nn}
                elif len(nn) == best_len:
                    matches.setdefault(eid, nn)
        if matches:
            # ① 并列 cap：同长并列时按「正名命中 > mentions 高」取至多 3 个
            def _rank(eid: str) -> tuple[int, int]:
                ent = self.store.get_entity(eid) or {}
                is_canon = canon_map.get(eid, "") == matches.get(eid)
                return (0 if is_canon else 1, -int(ent.get("mentions") or 0))

            primary = sorted(matches, key=_rank)[:3]
            # ② 跨片段补充：查询里**不同提及片段**命中的较短名也参与链接
            # （如「自由海风号邮轮的音乐总监」——自由海风号 与 音乐总监 指向
            # 两个实体，都该做种子）。两条压制线防种子爆炸/误带：
            #   a. 同一提及跨度的子串短名不得带出（「露西娅在哪」⊂匹配的「露西」）；
            #   b. 仅收**人工别名表锚定**的实体——图内抽取的泛词实体
            #      （小说/故事/维也纳…）mentions 高但语义杂，禁止走此通道。
            winners = list(matches.values())
            anchored = self.store.anchored_ids
            extras: dict[str, str] = {}
            for eid, _canon, names in named:
                if eid in matches or eid not in anchored:
                    continue
                for nn in names:
                    if (
                        not nn
                        or len(nn) < 2
                        or len(nn) >= best_len
                        or nn not in qn
                        or any(nn in w for w in winners)
                    ):
                        continue
                    if re.fullmatch(r"[a-z0-9 ]+", nn) and not re.search(
                        r"(?<![a-z0-9])" + re.escape(nn) + r"(?![a-z0-9])", qn
                    ):
                        continue
                    extras.setdefault(eid, nn)
                    break
            seeds_out = primary + sorted(extras, key=_rank)[
                : max(0, 4 - len(primary))
            ]
            return {
                eid: {"weight": 1.0, "path": "exact", "name": matches.get(eid, "")}
                for eid in seeds_out
            }
        # ② 词元兜底：实体名/别名的 token 与查询 token 交集打分
        q_tokens = _substantial_tokens(q)
        if not q_tokens:
            return {}
        scored: list[tuple[str, float, str]] = []
        for eid, _canon, names in named:
            hit = 0
            total = 0
            hit_name = ""
            for nn in names:
                toks = self._tokens_of(nn)
                if not toks:
                    continue
                total += 1
                if toks & q_tokens:
                    hit += 1
                    if not hit_name:
                        hit_name = nn
            if hit and total:
                scored.append((eid, hit / total, hit_name))
        scored.sort(key=lambda kv: kv[1], reverse=True)
        out: dict[str, dict] = {}
        for eid, s, hit_name in scored[:3]:
            if s >= self.link_threshold:
                prev = out.get(eid)
                if prev is None or s > prev["weight"]:
                    out[eid] = {"weight": float(s), "path": "token", "name": hit_name}
        return out

    # —— P3 种子门控 ——
    def seed_gate(self, seeds: dict[str, dict]) -> dict[str, float]:
        """过滤链接结果，只留「值得信」的种子（P3 精度门控）。

        三条规则（全部实测驱动，见 deliverables/plot-rag-audit-20260912.md §P3）：
        1. **人工别名表锚定**的实体一律保留（人写的名字最可信）；
        2. **词元兜底**（path=token）种子必须被锚定——实测 300 题里只有 7 题落到这条
           路径且种子全是碎片，而离题问句几乎全靠它蹭上 restaurant / this place；
        3. 非锚定种子命中**世界常识泛词**（``GENERIC_SEED_NAMES``）时丢弃——
           「今天天气怎么样」正是命中泛词实体「天气」才注入 5 块剧情上下文。

        返回 ``{eid: weight}``；调用方在结果为空时**整体短路**（词法兜底也不启用），
        即"剧情层只回答图能认得的问题"。
        """
        if not seeds:
            return {}
        anchored = self.store.anchored_ids
        out: dict[str, float] = {}
        for eid, info in seeds.items():
            if eid in anchored:
                out[eid] = float(info.get("weight", 1.0))
                continue
            if info.get("path") == "token" and self.require_anchored_token_seeds:
                continue
            if self.filter_generic_seeds and is_generic_seed_name(str(info.get("name") or "")):
                continue
            out[eid] = float(info.get("weight", 1.0))
        return out

    # —— 图谱视图缓存（P1）——
    def _graph_view(self) -> tuple[list[dict], tuple, dict[str, list[str]]]:
        """按 ``(store.revision, min_confidence, include_weak)`` 缓存的图视图。

        返回 ``(过滤后的边表, PPR 邻接(adj, deg), hop 邻接)``。
        旧实现每次 ``retrieve()`` 都要 3 次 ``all_edges()`` 浅拷贝 + 3 次过滤 +
        2 次邻接重建（5719 边量级），实测 PPR 一次 88ms。
        """
        key = (self.store.revision, float(self.min_confidence), bool(self.include_weak))
        cached = self._graph_view_cache
        if cached is not None and cached[0] == key:
            return cached[1], cached[2], cached[3]
        # 边表与邻接必须用**同一份**过滤口径（graph_ppr.filter_edges 是唯一来源），
        # 否则会出现「邻接里没有、边循环里却有」的弱证据边漏网。
        edges = filter_edges(
            _edges_of_store(self.store),
            min_confidence=self.min_confidence,
            include_weak=self.include_weak,
        )
        ppr_adj = build_adjacency(edges, min_confidence=0.0, include_weak=True)
        hop_adj: dict[str, list[str]] = {}
        for src, nbrs in ppr_adj[0].items():
            hop_adj.setdefault(src, [])
            for dst, _w in nbrs:
                hop_adj[src].append(dst)
        self._graph_view_cache = (key, edges, ppr_adj, hop_adj)
        return edges, ppr_adj, hop_adj

    # —— 种子实体提及块（P0 融合策略）——
    def _low_texts(self) -> list[str]:
        """全部 chunk 正文的小写副本（惰性构建一次，供提及计数复用）。"""
        if self._low_texts_cache is None:
            self._low_texts_cache = [c.text.lower() for c in self.corpus.chunks]
        return self._low_texts_cache

    def _hash_to_idx(self) -> dict[str, int]:
        """hash → 块下标（候选 hash 集反查下标）。重复 hash 保留首个，与 by_hash 同口径。"""
        if self._hash_idx_cache is None:
            idx: dict[str, int] = {}
            for i, c in enumerate(self.corpus.chunks):
                if c.hash and c.hash not in idx:
                    idx[c.hash] = i
            self._hash_idx_cache = idx
        return self._hash_idx_cache

    def _name_hits(self, name: str) -> tuple[dict[int, int] | None, float]:
        """实体名 → ``({块下标: 精确命中次数}, 权重)``；名字不可用返回 ``(None, 0.0)``。

        P1 性能修复（本层最大的单点开销）：旧实现给每个名字造一个闭包，再对**全部
        8358 块**跑一次 ``re.findall``/``str.count``——实测单查询 128 个名字 ⇒
        1,069,824 次 ``findall``、16.9s，占 ``retrieve()`` 总耗时 97.6%。
        现在先取 ``corpus.candidate_hashes(name)`` 候选集（含该名字词元的块，实测均值
        63 块），只在候选上跑**语义完全相同**的计数器；名字无可用词元时回落全扫。

        命中次数与权重口径与旧 ``_name_counter`` 逐条一致：
        拉丁名按词边界正则计数、单字母权重 0.3、其余 1.0；CJK/混合名子串计数、权重 0.6。
        结果按归一名字缓存（FIFO 上限 ``mention_cache_size``），跨查询复用。
        """
        low = norm_name(name)
        if not low or "?" in low:
            return None, 0.0  # ASR 疑似误识别别名（如 "Henpal?"）不参与
        if is_noise_entity(name):
            return None, 0.0  # 代词/称谓/句子片段别名会扫出海量噪声块
        is_latin = re.fullmatch(r"[a-z0-9 ]+", low) is not None
        weight = (0.3 if len(low) == 1 else 1.0) if is_latin else 0.6

        cached = self._mention_hits_cache.get(low, _MISS)
        if cached is not _MISS:
            return cached, weight  # type: ignore[return-value]

        low_texts = self._low_texts()
        if is_latin:
            pat = self._name_pat_cache.get(low)
            if pat is None:
                pat = re.compile(r"(?<![a-z0-9])" + re.escape(low) + r"(?![a-z0-9])")
                self._name_pat_cache[low] = pat

            def _count_at(i: int, p=pat, texts=low_texts) -> int:
                return len(p.findall(texts[i]))

        else:

            def _count_at(i: int, n=low, texts=low_texts) -> int:
                return texts[i].count(n)

        cand = self.corpus.candidate_hashes(name)
        if cand is None:
            idxs: range | list[int] = range(len(self.corpus.chunks))
        else:
            h2i = self._hash_to_idx()
            idxs = [h2i[h] for h in cand if h in h2i]
        hits: dict[int, int] = {}
        for i in idxs:
            n = _count_at(i)
            if n:
                hits[i] = n
        # FIFO 淘汰：字典保持插入序，超限时丢最早的一条
        if len(self._mention_hits_cache) >= self._mention_cache_size:
            self._mention_hits_cache.pop(next(iter(self._mention_hits_cache)), None)
        self._mention_hits_cache[low] = hits
        return hits, weight

    def _mention_channel(
        self,
        targets: dict[str, float],
        *,
        per_entity: int = 3,
        total_cap: int = 6,
    ) -> list[tuple[float, object, dict]]:
        """提及通道：**idf 加权**的实体名命中块（属性题主战场）。

        背景：PPR 证据回查只从**边**取块，属性题（X 的 Y 是谁）的答案块往往只含种子
        实体自身的提及而不在任何入选边里，故需要单开一路"含实体名自身的块"。

        打分（P2，模式由 ``mention_scoring`` 决定；消融结果见审计报告 §P2）：
        - ``"count"``（默认）：``score = Σ_名字 w(名)·出现次数``，即旧口径；
        - ``"idf"``：``score = Σ_名字 w(名)·idf(名)·(1+0.3·ln 次数)``，稀有名字加权。
          实测在本语料上 **idf 反而更差**（严格通过率 −4pt：ASR 转写里"反复提到某角色"
          的块通常正是该角色的主场戏，也就是答案块；稀有别名命中多为顺带一提）。
          故默认回到旧口径，idf 作为可选模式保留，供换语料时重新评估。
        - ``cooccurrence_bonus``：块命中 k≥2 个目标实体时 ``×(1+0.5·(k−1))``——
          多实体共现是关系题/多跳题答案块的特征；
        - ``seed_factor``：种子 1.0 / PPR 邻居 0.5（保持"种子优先"的既有语义）；
        - 每实体先取前 ``per_entity`` 块再汇总，与旧实现的候选收敛口径一致。

        返回 ``[(score, PlotChunk, meta_extra)]``，按分数降序（并列按下标升序，确保可复现）。
        """
        if not targets or per_entity <= 0:
            return []
        chunks = self.corpus.chunks
        total_docs = max(1, len(chunks))
        use_idf = self.mention_scoring == "idf"
        # 每个目标实体 → [(命中表, 原始权重, idf 权重)]
        per_entity_data: list[tuple[str, float, list[tuple[dict[int, int], float, float]]]] = []
        for eid, base in targets.items():
            ent = self.store.get_entity(eid)
            if not ent:
                continue
            ent_name = str(ent.get("name") or eid)
            names: list[tuple[dict[int, int], float, float]] = []
            for n in [ent_name] + [str(a) for a in (ent.get("aliases") or [])]:
                hits, weight = self._name_hits(n)
                if not hits:
                    continue
                idf = math.log(1.0 + total_docs / max(1, len(hits)))
                names.append((hits, weight, weight * idf))
            if names:
                per_entity_data.append((ent_name, 1.0 if base >= 1.0 else 0.5, names))
        if not per_entity_data:
            return []

        # 块 → {实体序号: 该实体给出的分数}
        picks: dict[int, dict[int, float]] = {}
        ranked_by_entity: dict[int, list[tuple[float, int]]] = {}
        for ei, (_name, seed_factor, names) in enumerate(per_entity_data):
            per_chunk: dict[int, float] = {}
            for hits, w_raw, w_idf in names:
                if use_idf:
                    # idf 加权 + 次线性词频：稀有名字命中更有区分度
                    for i, n in hits.items():
                        per_chunk[i] = per_chunk.get(i, 0.0) + w_idf * (1.0 + 0.3 * math.log(n))
                else:
                    # 原始加权词频（旧口径，实测在本语料上更优，见审计报告 §P2 消融）
                    for i, n in hits.items():
                        per_chunk[i] = per_chunk.get(i, 0.0) + w_raw * n
            ranked = sorted(per_chunk.items(), key=lambda kv: (-kv[1], kv[0]))[:per_entity]
            ranked_by_entity[ei] = [(s * seed_factor, i) for i, s in ranked]
            for i, s in ranked:
                picks.setdefault(i, {})[ei] = s * seed_factor

        if self.mention_group_by_entity:
            # **实体分组序**（默认）：种子按 base(=1+PPR) 降序、邻居按 PPR 降序，
            # 每个实体的代表块连续排列。旧实现所有提及块共用同一分数、靠稳定排序
            # 自然形成这个顺序；显式实现它才能既保住该顺序、又让每个块有可比的分数。
            # 实测（300 题）：全局按分数交错会让严格通过率掉 ~6pt。
            groups = sorted(
                range(len(per_entity_data)),
                key=lambda ei: (-per_entity_data[ei][1], ei),
            )
            ordered: list[tuple[float, int, str]] = []
            for ei in groups:
                name = per_entity_data[ei][0]
                for s, i in ranked_by_entity.get(ei, []):
                    ordered.append((s, i, name))
            return [
                (float(s), chunks[i], {"path": "mention", "seed_mention": name})
                for s, i, name in ordered[:total_cap]
            ]

        scored: list[tuple[float, int, str]] = []
        for i, by_entity in picks.items():
            k = len(by_entity)
            total = sum(by_entity.values())
            if self.cooccurrence_bonus:
                total *= 1.0 + 0.5 * (k - 1)
            best_ei = max(by_entity, key=lambda e: (by_entity[e], -e))
            scored.append((total, i, per_entity_data[best_ei][0]))
        scored.sort(key=lambda kv: (-kv[0], kv[1]))
        return [
            (float(s), chunks[i], {"path": "mention", "seed_mention": name})
            for s, i, name in scored[:total_cap]
        ]

    # —— P2 通道融合 ——
    def _fuse_channels(
        self,
        channels: list[tuple[str, float, list[tuple[float, object, dict]]]],
        *,
        limit: int,
    ) -> list[tuple[float, object, dict]]:
        """RRF 融合多路候选，返回 ``[(归一化分数, chunk, meta_extra)]``（分数降序）。

        为什么必须融合：三条通道的分数量纲**互不可比**——边证据 ≈0.2（PPR×confidence）、
        提及块 ≈1.2（旧实现给常数 1.0 + 种子 PPR）、词法兜底是 BM25 原始分（30–75）。
        旧实现把它们直接塞进一个列表排序，实际效果是"提及路稳压边证据、词法路稳压两者"，
        图结构（PPR/多跳）这条最有价值的能力**从未真正进入过提示词**
        （``persona_prompt`` 的 0.85 组内相对门会把 0.2 的边证据整批丢掉）。

        RRF（reciprocal rank fusion）只用**名次**不用原始分，天然免疫量纲问题：
        ``fused(h) = Σ_c w_c / (k + rank_c(h))``，k=``fuse_k``。
        融合后线性映射到 ``[0.6, 1.0]``：既保证高于 ``persona_prompt.MIN_CONTEXT_SCORE``
        （0.05），又让分数保持可比的排序含义（首位 1.0，其余按融合强度递减）。
        """
        fused: dict[str, float] = {}
        order: list[str] = []
        chunk_by_hash: dict[str, object] = {}
        meta_by_hash: dict[str, dict] = {}
        paths_by_hash: dict[str, list[str]] = {}
        for path, weight, items in channels:
            if weight <= 0:
                continue
            for rank, (_s, chunk, extra) in enumerate(items):
                h = str(getattr(chunk, "hash", "") or "")
                if not h:
                    continue
                if h not in fused:
                    order.append(h)
                    chunk_by_hash[h] = chunk
                    meta_by_hash[h] = dict(extra or {})
                    paths_by_hash[h] = []
                fused[h] = fused.get(h, 0.0) + weight / (self.fuse_k + rank)
                if path not in paths_by_hash[h]:
                    paths_by_hash[h].append(path)
        if not order:
            return []
        top = max(fused.values()) or 1.0
        out: list[tuple[float, object, dict]] = []
        for h in order:
            meta = meta_by_hash[h]
            best = max(paths_by_hash[h], key=lambda p: (FUSE_PATH_PRIORITY.get(p, 0), p))
            meta["path"] = best
            meta["paths"] = sorted(paths_by_hash[h])
            out.append((FUSE_MIN_SCORE + (FUSE_MAX_SCORE - FUSE_MIN_SCORE) * (fused[h] / top),
                        chunk_by_hash[h], meta))
        # 稳定排序：同分保持通道内名次（order 的插入顺序即"边证据优先、再提及"）
        out.sort(key=lambda item: -item[0])
        # 同一 doc 软去冗余：先按上限取，名额没填满再放宽（避免返回条数被压到 1 条）
        if self.diversity_per_doc > 0:
            kept: list[tuple[float, object, dict]] = []
            per_doc: dict[str, int] = {}
            for item in out:
                doc = str(getattr(item[1], "doc_id", "") or "")
                if per_doc.get(doc, 0) >= self.diversity_per_doc:
                    continue
                per_doc[doc] = per_doc.get(doc, 0) + 1
                kept.append(item)
                if len(kept) >= limit:
                    break
            if len(kept) < limit:
                for item in out:
                    if item in kept:
                        continue
                    kept.append(item)
                    if len(kept) >= limit:
                        break
            out = kept
        return out[:limit]

    # —— PPR ——
    def _ppr(self, seeds: dict[str, float]) -> dict[str, float]:
        """个性化 PageRank（无向化传播，多跳关联自然浮到前排）。

        邻接表由 :meth:`_graph_view` 按 store 版本缓存：旧实现每次检索都重扫
        5719 边重建邻接（PPR 实测 88ms/次，其中约三成花在重建上）。
        这里传 ``edges`` 仅为「无可用边时原样返回种子」的短路判断，过滤口径
        已由 ``build_adjacency`` 在缓存构建时施加（故传中性过滤参数）。
        """
        edges, ppr_adj, _hop = self._graph_view()
        return personalized_pagerank(
            edges,
            seeds,
            min_confidence=0.0,
            include_weak=True,
            damping=self.damping,
            max_iter=self.max_iter,
            adjacency=ppr_adj,
        )

    def _hop_distance(self, seeds: set[str], max_hops: int) -> dict[str, int]:
        """从种子做 BFS，得到节点跳距（约束证据边不超过 max_hops）。

        过滤口径与 ``_ppr`` / ``retrieve`` 保持一致（min_confidence + 弱证据门），
        否则会出现「有跳距但零 PPR 分」的节点，令筛选逻辑难以解释。
        """
        edges, _ppr_adj, hop_adj = self._graph_view()
        return hop_distance(
            edges,
            seeds,
            max_hops,
            min_confidence=0.0,
            include_weak=True,
            adjacency=hop_adj,
        )

    # —— 检索入口 ——
    def retrieve(
        self,
        query: str,
        *,
        top_chunks: int = 3,
        lexical_fallback: int = 2,
        topup: bool = False,
    ) -> list[RetrievedChunk]:
        """返回剧情证据块（三通道 RRF 融合：边证据 / 提及块 / 词法兜底）。

        - ``topup=False``（默认）：**仅当图谱路零命中**才走词法兜底。
          这是 Settings.plot_lexical_fallback 的既定语义（"图零命中时的词法兜底"），
          也避免无关查询被 BM25 噪声占满上下文。
        - ``topup=True``：图谱命中不足 top_chunks 时也补齐（旧行为，可显式开启）。

        P2 排序契约（``metadata``）：
        - ``via``：``plot_graph``（图路两通道）/ ``plot_lexical``（词法兜底）——**不变**；
        - ``path``：``edge`` / ``mention`` / ``lexical``，用于区分"图结构到底有没有起作用"
          （旧实现下 ``via`` 恒为 plot_graph，图谱路径占比是个恒 1.0 的无效指标）；
        - ``paths``：该块被哪些通道命中（多路命中排名更高）；
        - ``edge`` / ``edge_score`` / ``seed_mention`` 保留原字段，API 与前端零改动。

        分数为 RRF 融合后归一到 ``[0.6, 1.0]`` 的可比分数（见 :meth:`_fuse_channels`）；
        返回条数上限为 ``top_chunks + max(0, lexical_fallback)``。
        """
        seeds = self.seed_gate(self.link_detailed(query))
        edge_items: list[tuple[float, object, dict]] = []
        mention_items: list[tuple[float, object, dict]] = []
        if seeds:
            ranks = self._ppr(seeds)
            dist = self._hop_distance(set(seeds), self.max_hops)
            edges_view = self._graph_view()[0]  # 已按 min_confidence + 弱证据门过滤（缓存）
            scored: list[tuple[float, dict]] = []
            for e in edges_view:
                weak = len(e.get("evidence") or []) < WEAK_EVIDENCE_MIN
                s, dd = str(e.get("src")), str(e.get("dst"))
                if s not in dist or dd not in dist:
                    continue
                if max(dist[s], dist[dd]) > self.max_hops:
                    continue
                score = (ranks.get(s, 0.0) + ranks.get(dd, 0.0)) * float(
                    e.get("confidence", 0.0)
                )
                if weak:
                    score *= 0.5  # 孤证降权（仍可入选，但排在后面）
                if score > 0:
                    scored.append((score, e))
            scored.sort(key=lambda kv: kv[0], reverse=True)
            # 通道①：边证据（结构化关系路径）。每条边只取一条代表证据，避免同边刷屏。
            seen_edge_ev: set[str] = set()
            for score, e in scored[: self.max_edges]:
                for ev in e.get("evidence") or []:
                    h = ev.get("hash")
                    if not h or h in seen_edge_ev:
                        continue
                    chunk = self.corpus.by_hash(str(h), doc_id=ev.get("doc_id"))
                    if chunk is None:
                        continue
                    seen_edge_ev.add(str(h))
                    edge_items.append(
                        (
                            float(score),
                            chunk,
                            {
                                "via": "plot_graph",
                                "path": "edge",
                                "edge": f"{_name_of(self.store, e.get('src'))}"
                                f" —{e.get('relation')}→ "
                                f"{_name_of(self.store, e.get('dst'))}",
                                "edge_score": round(float(score), 4),
                            },
                        )
                    )
                    break
            # 通道②：种子/高 PPR 实体自身的提及块（属性题主战场）。
            # targets: 种子给 1.0+（seed_factor=1.0），PPR top 邻居按 rank 竞争（0.5）。
            if top_chunks > 0:
                targets = {eid: 1.0 + float(ranks.get(eid, 0.0)) for eid in seeds}
                for eid, rank in sorted(
                    ranks.items(), key=lambda kv: kv[1], reverse=True
                ):
                    if len(targets) >= 4:
                        break
                    if eid not in targets and rank > 0:
                        targets[eid] = float(rank)
                mention_items = self._mention_channel(targets)

        # 通道③：词法兜底（BM25）。口径不变：**仅在图谱零命中**时启用（plot_lexical_topup
        # 语义），或显式 topup=True 时补齐；否则无关查询会被 BM25 噪声占满上下文。
        lexical_items: list[tuple[float, object, dict]] = []
        # 图路"命中数"必须按**去重后的块**计：同一块常同时出现在边证据与提及两路，
        # 按通道条目数相加会把 1 块当成 2 块，导致 topup 判定失效（该补词法却不补）。
        graph_hashes = {
            str(getattr(c, "hash", "") or "")
            for _s, c, _m in list(edge_items) + list(mention_items)
        }
        graph_count = len(graph_hashes - {""})
        # 词法兜底只服务于「图能认得」的查询（**通过门控的种子非空**）：
        # 没有任何可信种子时整体短路——否则任何含常见词的问句都会被 BM25 灌进
        # 5–7 块无关转写（实测「1+1 等于几」「给我讲个笑话」各注入 5 块）。
        need_fallback = bool(seeds) and (
            graph_count == 0 if not topup else graph_count < max(0, top_chunks)
        )
        if need_fallback and lexical_fallback > 0:
            need = max(0, top_chunks) + max(0, lexical_fallback)
            for chunk, s in self.corpus.search(query, top_k=need):
                lexical_items.append(
                    (float(s), chunk, {"via": "plot_lexical", "path": "lexical"})
                )

        # RRF 融合 + 归一化分数带 + 同一 doc 软去冗余（见 _fuse_channels）
        # 预算语义（与旧实现一致）：**图路可用满整个返回预算**
        # （top_chunks + lexical_fallback）；词法兜底只在图路不足时占用剩余名额。
        # 实测教训：把图路硬压到 top_chunks(=3) 会让返回块数从 4.83 掉到 2.86，
        # 严格通过率直降 9pt——证据块并集口径下，"少给块"就是"少覆盖"。
        graph_limit = max(0, top_chunks)
        if lexical_items and graph_count:
            # 两路共存（topup）：图路占 top_chunks 名额，词法只补 lexical_fallback 个
            fused = self._fuse_channels(
                [
                    ("edge", self.weight_edge, edge_items),
                    ("mention", self.weight_mention, mention_items),
                    ("lexical", self.weight_lexical, lexical_items),
                ],
                limit=graph_limit + max(0, lexical_fallback),
            )
            graph_kept = [it for it in fused if it[2].get("path") != "lexical"][:graph_limit]
            lex_kept = [it for it in fused if it[2].get("path") == "lexical"][
                : max(0, lexical_fallback)
            ]
            fused = graph_kept + lex_kept
            fused.sort(key=lambda item: -item[0])
        elif lexical_items:
            # 只有词法路（图谱零命中）：同样归一到分数带，保持跨通道可比
            fused = self._fuse_channels(
                [("lexical", self.weight_lexical, lexical_items)],
                limit=max(0, lexical_fallback) or len(lexical_items),
            )
        else:
            fused = self._fuse_channels(
                [
                    ("edge", self.weight_edge, edge_items),
                    ("mention", self.weight_mention, mention_items),
                ],
                limit=graph_limit + max(0, lexical_fallback),
            )

        out: list[RetrievedChunk] = []
        for score, chunk, extra in fused:
            meta = chunk.meta(self.namespace)
            meta.update(extra or {})
            out.append(RetrievedChunk(text=chunk.text, score=float(score), metadata=meta))
        return out[: max(0, top_chunks + max(0, lexical_fallback))]


def _edges_of_store(store: GraphStore) -> list[dict]:
    """取图谱全部边（GraphStore 未暴露全量边接口时的兼容取法）。"""
    getter = getattr(store, "all_edges", None)
    if callable(getter):
        return list(getter())  # type: ignore[no-any-return]
    # 回退：统计式遍历（实体邻接去重）
    seen: set[int] = set()
    edges: list[dict] = []
    for ent in store.entities():
        for e, _dir in store.neighbors(str(ent.get("id"))):
            key = id(e)
            if key in seen:
                continue
            seen.add(key)
            edges.append(e)
    return edges


def _name_of(store: GraphStore, eid: str | None) -> str:
    if not eid:
        return "?"
    ent = store.get_entity(str(eid))
    return str((ent or {}).get("name") or eid)


# ── 注册表（在线检索入口，懒加载 + mtime 热重载）──
class PlotGraphRegistry:
    """按角色懒加载「剧情语料 + 剧情图谱」，缺失/过期一律静默降级。"""

    def __init__(
        self,
        *,
        corpus_dir: str | Path,
        graph_dir: str | Path,
        alias_dir: str | Path = "",
        min_confidence: float = 0.6,
        # 默认 True：真实语料 99.7% 的边只有 1 条证据，False 等于关掉图谱路
        # （与 Settings.plot_include_weak 保持一致，避免直接构造注册表时行为漂移）。
        include_weak: bool = True,
        max_edges: int = 10,
        max_hops: int = 2,
        damping: float = 0.85,
        link_threshold: float = 0.5,
        fuse_k: int = 3,
        weight_edge: float = 1.0,
        weight_mention: float = 1.0,
        weight_lexical: float = 0.6,
        diversity_per_doc: int = 1,
        mention_cache_size: int = 512,
        require_anchored_token_seeds: bool = True,
        filter_generic_seeds: bool = True,
        mention_scoring: str = "count",
        cooccurrence_bonus: bool = True,
        mention_group_by_entity: bool = True,
        alias_authoritative: bool = True,
    ) -> None:
        self._corpus_dir = Path(corpus_dir)
        self._graph_dir = Path(graph_dir)
        self._alias_dir = Path(alias_dir) if alias_dir else None
        self._cfg = dict(
            min_confidence=min_confidence,
            include_weak=include_weak,
            max_edges=max_edges,
            max_hops=max_hops,
            damping=damping,
            link_threshold=link_threshold,
            fuse_k=fuse_k,
            weight_edge=weight_edge,
            weight_mention=weight_mention,
            weight_lexical=weight_lexical,
            diversity_per_doc=diversity_per_doc,
            mention_cache_size=mention_cache_size,
            require_anchored_token_seeds=require_anchored_token_seeds,
            filter_generic_seeds=filter_generic_seeds,
            mention_scoring=mention_scoring,
            cooccurrence_bonus=cooccurrence_bonus,
            mention_group_by_entity=mention_group_by_entity,
            alias_authoritative=alias_authoritative,
        )
        self._cache: dict[str, tuple[float, float, PlotGraphRetriever]] = {}

    def paths_for(self, character_id: str | None) -> tuple[Path, Path]:
        cid = (character_id or "").strip() or "default"
        safe = cid.replace("/", "_").replace("\\", "_")
        return (
            self._corpus_dir / f"plot_corpus_{safe}.json",
            self._graph_dir / f"plot_graph_{safe}.json",
        )

    def get(self, character_id: str | None) -> PlotGraphRetriever | None:
        key = (character_id or "").strip() or "default"
        cpath, gpath = self.paths_for(character_id)
        try:
            cm, gm = cpath.stat().st_mtime, gpath.stat().st_mtime
        except OSError:
            # 缓存键必须与写入时一致（已 strip）：否则 character_id 含空白时清不掉旧条目
            self._cache.pop(key, None)
            return None
        cached = self._cache.get(key)
        if cached is not None and cached[0] == cm and cached[1] == gm:
            return cached[2]
        corpus = PlotCorpus(cpath, character_id=key)
        if not corpus.chunks:
            return None
        store = GraphStore(gpath, min_confidence=self._cfg["min_confidence"])
        if not store.entities():
            return None
        if self._alias_dir is not None:
            # 双语别名表按角色存放：<lore_dir>/<cid>/plot_aliases.json
            table = load_alias_table(self._alias_dir / key / "plot_aliases.json")
            if table:
                # P4：剧情层让人工别名表**真正**最高优先（冲突时改指人工规范实体）；
                # GraphStore 默认仍是 skip（lore 层与既有测试语义不变）。
                store.bind_alias_table(
                    table, on_conflict="merge" if self._cfg["alias_authoritative"] else "skip"
                )
        retr = PlotGraphRetriever(
            corpus,
            store,
            namespace=plot_namespace(key),
            min_confidence=self._cfg["min_confidence"],
            include_weak=self._cfg["include_weak"],
            max_edges=self._cfg["max_edges"],
            max_hops=self._cfg["max_hops"],
            damping=self._cfg["damping"],
            link_threshold=self._cfg["link_threshold"],
            fuse_k=self._cfg["fuse_k"],
            weight_edge=self._cfg["weight_edge"],
            weight_mention=self._cfg["weight_mention"],
            weight_lexical=self._cfg["weight_lexical"],
            diversity_per_doc=self._cfg["diversity_per_doc"],
            mention_cache_size=self._cfg["mention_cache_size"],
            require_anchored_token_seeds=self._cfg["require_anchored_token_seeds"],
            filter_generic_seeds=self._cfg["filter_generic_seeds"],
            mention_scoring=self._cfg["mention_scoring"],
            cooccurrence_bonus=self._cfg["cooccurrence_bonus"],
            mention_group_by_entity=self._cfg["mention_group_by_entity"],
        )
        self._cache[key] = (cm, gm, retr)
        return retr

    def peek(self, character_id: str | None) -> dict:
        cpath, gpath = self.paths_for(character_id)
        info: dict = {
            "corpus": str(cpath),
            "graph": str(gpath),
            "corpus_exists": cpath.exists(),
            "graph_exists": gpath.exists(),
        }
        if cpath.exists():
            info["corpus_stats"] = PlotCorpus(cpath).stats()
        if gpath.exists():
            info["graph_stats"] = GraphStore(gpath).stats()
        return info


# ── 离线构建 ──
async def build_plot_graph(
    corpus: PlotCorpus,
    store: GraphStore,
    extractor,
    cache,
    *,
    namespace: str,
    batch: int = 8,
    limit: int | None = None,
    only_lang: str | None = None,
) -> dict:
    """把剧情语料构建进图谱（幂等：缓存命中不调 LLM）。

    extractor 需提供 ``extract(text, system=...)`` 或 GraphExtractor.extract(text)；
    为兼容两者，这里按有无 ``system`` 参数决定调用方式。
    """
    chunks = [c for c in corpus.chunks if not only_lang or c.lang == only_lang]
    if limit is not None:
        chunks = chunks[: max(0, limit)]
    sem = asyncio.Semaphore(max(1, batch))
    stats = {
        "chunks": len(chunks),
        "extracted": 0,
        "cached": 0,
        "failed": 0,
        "skipped": 0,
        "edges": 0,
        "noise_filtered": 0,
        "noise_rescued": 0,  # name 命中噪声但经别名打捞保住的实体数
        "rel_filtered": 0,  # 谓语卫生过滤丢弃的关系数（否定/超长/标点/黑名单/映射不到）
    }
    failed: list[str] = []

    async def _one(chunk) -> None:
        data = cache.get(chunk.hash)
        if data is None:
            async with sem:
                data = await _call_extract(extractor, chunk.text, chunk.lang)
            if data is None:
                stats["failed"] += 1
                failed.append(chunk.hash)
                return
            cache.put(chunk.hash, data)
            stats["extracted"] += 1
        else:
            stats["cached"] += 1
        entities = data.get("entities") or []
        relations = data.get("relations") or []
        # 转写噪声实体（称谓/句子片段）不进图谱：防抢占正牌实体的别名索引
        kept: list[dict] = []
        for e in entities:
            if not isinstance(e, dict):
                stats["noise_filtered"] += 1
                continue
            if not is_noise_entity(str(e.get("name") or "")):
                kept.append(e)
                continue
            rescued = rescue_noise_entity(e)
            if rescued is not None:
                stats["noise_rescued"] += 1
                kept.append(rescued)
            else:
                stats["noise_filtered"] += 1
        if not kept and not relations:
            stats["skipped"] += 1
            return
        store.upsert_entities(kept)
        # 关系端点局部解析（与 graph_extract 同一套逻辑）：同 chunk 内别名歧义 → 丢弃，
        # 避免关系被挂到首注册实体上；解析不到再回落全局别名索引。
        local = build_local_endpoint_map(store, kept)
        for rel in relations:
            src = resolve_endpoint(store, local, str(rel.get("src") or ""))
            dst = resolve_endpoint(store, local, str(rel.get("dst") or ""))
            if not src or not dst:
                continue
            if src == dst:  # 自环边（A→A）：小模型常见产物，无检索价值，丢弃
                continue
            # 谓语卫生过滤（与 graph_extract.normalize_extraction 同一规则源）：
            # 否定短语/超长/含标点或拉丁字符/黑名单/映射不到 canonical → 丢弃。
            # 缓存里的旧抽取结果（受控词表上线前生成）也在此被兜住。
            canon_rel = canonicalize_relation(str(rel.get("relation") or ""))
            if canon_rel is None:
                stats["rel_filtered"] += 1
                continue
            if store.upsert_edge(
                src=src,
                dst=dst,
                relation=canon_rel,
                confidence=float(rel.get("confidence", 0.7) or 0.7),
                importance=IMPORTANCE_TRANSCRIPT,
                evidence=[
                    {"ns": namespace, "doc_id": chunk.doc_id, "hash": chunk.hash}
                ],
                source="plot_transcript",
            ):
                stats["edges"] += 1

    await asyncio.gather(*[_one(c) for c in chunks])
    if failed:
        logger.warning("剧情图谱抽取失败 %d 块（可重跑续做）：%s", len(failed), failed[:5])
    store.save()
    # save() 在文件损坏/结构非法时会**静默拒绝落盘**（M0-2 安全网）。库函数不能
    # 直接 return 1，故把失败同时写到日志与 stats：调用方（CLI）据此退出码 1，
    # 否则运维会看到「落盘成功」而盘上一个字节都没变。
    if store.load_error:
        stats["save_error"] = store.load_error
        logger.error(
            "剧情图谱拒绝落盘（防空图覆盖）：%s｜本轮 %d 块抽取结果**未写入**",
            store.load_error,
            stats["chunks"],
        )
    return stats


async def _call_extract(extractor, text: str, lang: str):
    """按语种选提示词调用抽取器（兼容 extract(text, system=...) 与 extract(text)）。"""
    prompt = prompt_for_lang(lang)
    try:
        return await extractor.extract(text, system=prompt)
    except TypeError:
        return await extractor.extract(text)
