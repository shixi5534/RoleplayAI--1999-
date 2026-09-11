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
import re
from pathlib import Path

from ...core.rag.base import RetrievedChunk  # 复用检索块结构，便于统一渲染
from .graph_ppr import WEAK_EVIDENCE_MIN, hop_distance, personalized_pagerank
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


def _substantial_tokens(text: str) -> set[str]:
    """有区分度的词元：拉丁词与 CJK 二元组（CJK 单字如「生」「了」太泛，弃用）。"""
    return {t for t in tokenize(text) if len(t) >= 2}


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
        self._entities_cache: list[dict] | None = None

    # —— 实体链接 ——
    def _entities(self) -> list[dict]:
        if self._entities_cache is None:
            self._entities_cache = self.store.entities()
        return self._entities_cache

    def link(self, query: str) -> dict[str, float]:
        """查询 → {eid: weight}：精确别名最长匹配 → 词元 BM25 兜底。

        精确匹配同长并列时按「正名命中 > mentions 高」排序且至多取 3 个
        种子——防止同一别名被多个（噪声）实体共享时种子爆炸
        （实测「露西女士是谁」曾带出 11 个种子）。
        """
        q = query or ""
        if not q:
            return {}
        qn = norm_name(q)
        # ① 精确匹配：实体正名与别名的**最长**命中优先（避免「露西」命中「露西娅」短名）
        best_len = 0
        matches: dict[str, str] = {}  # eid -> 命中的归一名
        for ent in self._entities():
            names = [str(ent.get("name") or "")] + [
                str(a) for a in (ent.get("aliases") or [])
            ]
            eid = str(ent.get("id"))
            for n in names:
                nn = norm_name(n)
                if not nn or len(nn) < 2 or nn not in qn:
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
            def _rank(eid: str) -> tuple[int, int]:
                ent = self.store.get_entity(eid) or {}
                is_canon = norm_name(str(ent.get("name") or "")) == matches.get(eid)
                return (0 if is_canon else 1, -int(ent.get("mentions") or 0))

            return {eid: 1.0 for eid in sorted(matches, key=_rank)[:3]}
        # ② 词元兜底：实体名/别名的 token 与查询 token 交集打分
        q_tokens = _substantial_tokens(q)
        if not q_tokens:
            return {}
        seeds: dict[str, float] = {}
        scored: list[tuple[str, float]] = []
        for ent in self._entities():
            names = [str(ent.get("name") or "")] + [
                str(a) for a in (ent.get("aliases") or [])
            ]
            hit = 0
            total = 0
            for n in names:
                toks = _substantial_tokens(n)
                if not toks:
                    continue
                total += 1
                if toks & q_tokens:
                    hit += 1
            if hit and total:
                scored.append((str(ent.get("id")), hit / total))
        scored.sort(key=lambda kv: kv[1], reverse=True)
        for eid, s in scored[:3]:
            if s >= self.link_threshold:
                seeds[eid] = max(seeds.get(eid, 0.0), float(s))
        return seeds

    # —— PPR ——
    def _ppr(self, seeds: dict[str, float]) -> dict[str, float]:
        """个性化 PageRank（无向化传播，多跳关联自然浮到前排）。"""
        return personalized_pagerank(
            _edges_of_store(self.store),
            seeds,
            min_confidence=self.min_confidence,
            include_weak=self.include_weak,
            damping=self.damping,
            max_iter=self.max_iter,
        )

    def _hop_distance(self, seeds: set[str], max_hops: int) -> dict[str, int]:
        """从种子做 BFS，得到节点跳距（约束证据边不超过 max_hops）。

        过滤口径与 ``_ppr`` / ``retrieve`` 保持一致（min_confidence + 弱证据门），
        否则会出现「有跳距但零 PPR 分」的节点，令筛选逻辑难以解释。
        """
        return hop_distance(
            _edges_of_store(self.store),
            seeds,
            max_hops,
            min_confidence=self.min_confidence,
            include_weak=self.include_weak,
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
        """返回剧情证据块（图谱路优先，词法兜底按需补充）。

        - ``topup=False``（默认）：**仅当图谱路零命中**才走词法兜底。
          这是 Settings.plot_lexical_fallback 的既定语义（"图零命中时的词法兜底"），
          也避免无关查询被 BM25 噪声占满上下文（实测「今天天气怎么样」会注入
          两段与话题无关的转写碎片）。
        - ``topup=True``：图谱命中不足 top_chunks 时也补齐（旧行为，可显式开启）。

        返回条数上限为 ``top_chunks + max(0, lexical_fallback)``。
        """
        seeds = self.link(query)
        out: list[RetrievedChunk] = []
        seen: set[str] = set()
        if seeds:
            ranks = self._ppr(seeds)
            dist = self._hop_distance(set(seeds), self.max_hops)
            scored: list[tuple[float, dict]] = []
            for e in _edges_of_store(self.store):
                if e.get("confidence", 0.0) < self.min_confidence:
                    continue
                weak = len(e.get("evidence") or []) < WEAK_EVIDENCE_MIN
                if weak and not self.include_weak:
                    continue
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
            for score, e in scored[: self.max_edges]:
                for ev in e.get("evidence") or []:
                    h = ev.get("hash")
                    if not h or h in seen:
                        continue
                    chunk = self.corpus.by_hash(str(h))
                    if chunk is None:
                        continue
                    seen.add(h)
                    meta = chunk.meta(self.namespace)
                    meta.update(
                        {
                            "via": "plot_graph",
                            "edge": f"{_name_of(self.store, e.get('src'))}"
                            f" —{e.get('relation')}→ "
                            f"{_name_of(self.store, e.get('dst'))}",
                            "edge_score": round(float(score), 4),
                        }
                    )
                    out.append(
                        RetrievedChunk(text=chunk.text, score=float(score), metadata=meta)
                    )
                    break  # 每条边只取一条代表证据，避免同边刷屏
                if len(out) >= max(0, top_chunks):
                    break
        # 词法兜底：图谱零命中（或显式 topup 时不足）→ 用 BM25 直接翻语料
        need_fallback = not out if not topup else len(out) < max(0, top_chunks)
        if need_fallback and lexical_fallback > 0:
            need = max(0, top_chunks) - len(out)
            for chunk, s in self.corpus.search(query, top_k=need + len(seen)):
                if chunk.hash in seen:
                    continue
                seen.add(chunk.hash)
                meta = chunk.meta(self.namespace)
                meta["via"] = "plot_lexical"
                out.append(RetrievedChunk(text=chunk.text, score=float(s), metadata=meta))
                if len(out) >= max(0, top_chunks):
                    break
        out.sort(key=lambda c: c.score, reverse=True)
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
                store.bind_alias_table(table)
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
            if isinstance(e, dict) and not is_noise_entity(str(e.get("name") or "")):
                kept.append(e)
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
