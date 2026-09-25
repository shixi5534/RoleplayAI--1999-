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
from collections import Counter
from pathlib import Path

from ...core.rag.base import RetrievedChunk  # 复用检索块结构，便于统一渲染
from .retrieval_trace import (
    CHANNEL_ORDER,
    ChannelSkipReason,
    TraceCollector,
    channel_of_block,
    trace_path,
)
from .graph_ppr import (
    WEAK_EVIDENCE_MIN,
    _is_exempt as _edge_is_exempt,
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
from .plot_corpus import PlotCorpus, detect_lang, plot_namespace, tokenize
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
FUSE_PATH_PRIORITY = {"edge": 5, "mention": 4, "semantic": 3, "chapter": 2, "lexical": 1}


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
# 名字里是否含「真正的名字字符」（字母/数字/CJK）。纯标点（``？？？``/``……``）
# 是 VN 的未具名说话人占位符，不指向实体——见 is_pronoun_or_filler。
# 注意跑在 norm_name 之后，全角标点已折成半角。
_RE_HAS_NAME_CHAR = re.compile(r"[0-9a-z\u4e00-\u9fff]", re.IGNORECASE)
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
        # ── ② 问候 / 敬语 / 感叹 / 应答（负样本 10→57 扩充后暴露的一整类）──
        # 这些是**口语高频词**，ASR 抽取会把它们当成实体——实测图内真实存在
        # `Buona sera` / `gracias` / `Haha` 三个"实体"，且都能被精确匹配成种子。
        # 它们与作品无关，却足以点火整条检索链。
        "谢谢", "感谢", "多谢", "抱歉", "对不起", "不好意思", "你好", "您好",
        "再见", "拜拜", "晚安", "早安", "早上好", "下午好", "晚上好",
        "哈哈", "呵呵", "嘿嘿", "嘻嘻", "嗯", "哦", "啊", "呀", "喂", "嗨",
        "拜托", "劳驾", "打扰", "恭喜", "加油", "辛苦",
        "thanks", "thank you", "sorry", "hello", "hi", "hey", "goodbye", "bye",
        "good night", "good morning", "haha", "lol", "please", "excuse me",
        # ── ③ 抽象泛化名词（被抽成"概念/事件/组织"类型的那类）──
        # 判据：在通用汉语里是**抽象范畴词**，指代任何领域的抽象事物，不指向本作品
        # 的任何具体设定。实测被误当种子的：事件 / 模型 / 意识 / 复仇 / 公司 / 国家。
        # 注意「公司/国家/组织」已在旧表以「国家」形式部分覆盖，此处补齐同族词。
        "事件", "事情", "模型", "意识", "公司", "组织", "问题", "东西",
        "地方", "方法", "原因", "结果", "过程", "情况", "状态", "关系",
        "信息", "数据", "系统", "结构", "功能", "作用", "意义", "价值",
        "影响", "变化", "发展", "内容", "形式", "方式", "条件", "基础",
        "标准", "规则", "原则", "概念", "理论", "思想", "观点", "想法",
        "感觉", "情绪", "能力", "技术", "科学", "文化", "历史", "政治",
        "社会", "自然", "复仇", "总统", "国王", "女王", "公主", "王子",
        "event", "events", "incident", "model", "consciousness", "company", "organization",
        "problem", "method", "reason", "result", "process", "situation",
        "state", "relationship", "information", "data", "system", "structure",
        "function", "meaning", "value", "impact", "change", "development",
        "content", "form", "condition", "standard", "rule", "principle",
        "concept", "theory", "idea", "feeling", "emotion", "memory",
        "knowledge", "ability", "technology", "science", "culture", "history",
        "politics", "society", "nature", "president", "king", "queen",
        "princess", "prince",
        # ── ④ 动作/角色类泛词（中文正典层入库后暴露）──
        # 背景：canon_zh 中文正典入库后中文侧命中面扩大 6 倍，原本够不着的
        # **非锚定中文垃圾实体**开始点火。实测两条新泄漏的种子：
        #   「解释一下相对论」  ← 实体「解释」（动词被抽成实体）
        #   「红楼梦的作者是谁」 ← 实体「作者」（角色通名被抽成实体）
        # 判据与 ③ 同源：都是**指代任何领域**的抽象/通名，不指向本作品任何设定。
        "解释", "说明", "介绍", "作者", "读者", "观众", "听众", "记者",
        "编辑", "译者", "用户", "成员", "人员", "角色", "人物",
    }
)


def is_generic_seed_name(name: str) -> bool:
    """种子名是否为「世界常识泛词」（P3 门控用；剧情专名一律返回 False）。"""
    return norm_name(name) in GENERIC_SEED_NAMES


# ── 名字形态相近判定（P1 别名可信度分层用）──
# 用于识别「同一实体的 ASR 变体」：Baccarola↔Barcarola、Sonnetto⊃Sonnet、
# Ms.Tooth Fairy⊃Tooth Fairy。抽取别名里既有这类真变体，也有 doll/Campbell 这种
# 与实体无关的词，靠本判据把两者分开。
_NAME_TOKEN_RE = re.compile(r"[a-z0-9]{4,}|[\u4e00-\u9fff]{2,}")
# 称谓/功能词不参与「共享词元」判定：否则 Miss Campbell 会靠 "miss" 蹭上 Miss Tooth Fairy
_NAME_TOKEN_STOP = frozenset(
    {
        "miss", "mister", "madam", "madame", "lady", "lord", "sir", "mrs",
        "the", "this", "that", "these", "those", "our", "your", "their",
        "his", "her", "with", "from", "and", "mrss",
    }
)


def _levenshtein_le(a: str, b: str, limit: int) -> bool:
    """有界编辑距离：距离 ≤ limit 返回 True（早停，短名字专用，无第三方依赖）。"""
    if abs(len(a) - len(b)) > limit:
        return False
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        best = i
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
            if cur[j] < best:
                best = cur[j]
        if best > limit:
            return False
        prev = cur
    return prev[-1] <= limit


def _name_tokens(name: str) -> set[str]:
    """参与「共享词元」判定的词元（≥4 字符拉丁词 / ≥2 字 CJK 串，去称谓词）。"""
    return {
        t for t in _NAME_TOKEN_RE.findall(name or "") if t not in _NAME_TOKEN_STOP
    }


def _is_name_variant(name: str, anchors: set[str]) -> bool:
    """``name`` 是否与任一锚名**形态相近**（同一实体的书写变体）。

    三条判据任一命中即算相近：包含关系 / 受限编辑距离 / 共享一个实义词元。
    全部基于字面，不依赖语料统计——避免"抽取时因同块出现而被写成别名"的循环论证。

    两条防误判护栏（都是实测踩出来的）：
    - **必须含实义词元**：否则称谓片段 ``miss`` 会因"包含于 Miss Tooth Fairy"成为锚点，
      再把 ``Miss Campbell`` / ``Miss Switchdoctor`` 全部链式拖进可信集
      （实测这一条会让「牙仙」的可信名从 8 个膨胀到 19 个，且包含无关人名）；
    - **短名编辑距离收紧到 1**：两字中文名两两距离恒 ≤2（玩偶↔牙仙），
      放 2 会让任意两个两字名互相"相近"。
    """
    if not name:
        return False
    name_toks = _name_tokens(name)
    if not name_toks:
        return False
    for a in anchors:
        if not a or a == name:
            continue
        if name in a or a in name:
            return True
        limit = 2 if max(len(name), len(a)) >= 6 else 1
        if abs(len(name) - len(a)) <= limit and _levenshtein_le(name, a, limit):
            return True
        if name_toks & _name_tokens(a):
            return True
    return False


def is_noise_entity(name: str) -> bool:
    """判定抽取正名是否为转写噪声（句子片段/称谓/语气词）。

    中文名不受影响；正常英文名（含 ``Madam Lucy``、``St. Pavlov Foundation``
    这类敬称/缩写开头）也不受影响。
    """
    # 整个判定必须跑在**全库唯一归一化口径** ``norm_name``（NFKC 全角→半角 + 小写）上。
    # 旧实现只在比对噪声表时归一，**标点正则仍看原串**——于是全角形漏网：
    #   ``is_noise_entity("???")``  → True（_RE_SENTENCE_MARK 命中 ASCII 问号）
    #   ``is_noise_entity("？？？")`` → False（全角问号不在标点类里）
    # 后果：compendium 正典里作为**未具名说话人占位符**的「？？？」被抽成别名，
    # 任何「？？？」查询都会点火（负样本护栏实测新增 1 条离题注入）。
    n = norm_name(name or "")
    if len(n) < 2:
        return True
    low = n
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


def is_pronoun_or_filler(name: str) -> bool:
    """名字是否为**代词 / 敬称 / 口头填充词 / 纯标点占位符**（链接期门控用）。

    为什么不能直接复用 :func:`is_noise_entity`：
      后者含「长度 < 2 即噪声」这条，而单字母拉丁别名是**被刻意允许**的
      （人工别名表里 ``Jay: ["J"]``，且有严格词边界规则兜底）。把它套到别名上会误杀 ``J``。
    本函数只取「代词 / 敬称 / 填充词」这一类判据，长度规则另论。

    为什么必须在**链接期**加这道门（实测踩到的真缺陷）：
      ``is_noise_entity`` 只在**建图时对正名**生效，**别名完全绕过**——于是
      实体 ``Shamane`` 挂着别名 ``me``、实体 ``Calabona`` 挂着别名 ``I``。
      后果不是"多召回一点"，而是**任何英文句子都会命中**：
      「tell me a joke」→ 种子 Shamane（度数 3、mentions 44）→ 图传播 20 块 + 语义 5 块
      → 8 块无关剧情被注入。这正是审计报告里「建图只过滤正名、不过滤别名」那个洞的
      检索侧出口。
    """
    low = norm_name(name)
    if not low:
        return False
    if low in _PRONOUN_CANONICAL or low in _NOISE_CANONICAL:
        return True
    # 纯标点占位符（``？？？`` / ``……`` / ``——``）：VN 里表示「未具名说话人」，
    # 不指向任何实体。**必须在这里拦**（而不是靠 is_noise_entity）：本函数是
    # 唯一的别名门控点，而别名完全绕过建图期过滤。实测缺陷：compendium 正典
    # 把「？？？」抽成「无脸的女孩」的别名，任何「？？？」查询都会点火。
    # 用「无字母/数字」判定，单字母别名 ``J`` 不受影响（它有字母）。
    return not _RE_HAS_NAME_CHAR.search(low)


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
        alias_trust_ratio: float = 0.25,
        untrusted_extra_per_entity: int = 1,
        weight_mention_entity: float = 1.0,
        entity_query_max_len: int = 14,
        alias_trust_chained_min_df: int = 3,
        name_salience: bool = False,
        ppr_max_iter: int = 20,
        chapter_routing: bool = True,
        chapter_top: int = 3,
        chapter_max_names: int = 2,
        weight_chapter: float = 1.0,
        lexical_topup: bool = False,
        lexical_always: bool = False,
        mention_per_entity: int = 3,
        mention_total_cap: int = 6,
        semantic_index=None,
        semantic_enabled: bool = True,
        semantic_top: int = 5,
        weight_semantic: float = 1.0,
        semantic_link_min: float = 0.0,
        semantic_link_top: int = 3,
        semantic_min_score: float = 0.0,
        min_semantic_kept: int = 0,
        min_chapter_kept: int = 0,
        rerank_topup_enabled: bool = False,
        rerank_topup_keep: int = 3,
        exempt_sources: frozenset[str] | None = None,
        node_specificity: bool = False,
        trace_enabled: bool = False,
        character_id: str = "",
        trace_out_path=None,
        trace_config: dict | None = None,
        pipeline_version: str = "plot-v1.0",
        entity_expander=None,
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
        # P1 别名可信度分层：抽取可疑名的权重倍数 + 每实体允许的"可疑名补位块"数
        self.alias_trust_ratio = float(alias_trust_ratio)
        self.untrusted_extra_per_entity = max(0, int(untrusted_extra_per_entity))
        # P2 实体查询：短查询命中实体时提及通道的权重（让"实体自己的块"压过边证据）
        self.weight_mention_entity = float(weight_mention_entity)
        self.entity_query_max_len = max(0, int(entity_query_max_len))
        # 链式变体（变体的变体）须达到的语料命中块数下限，防可信集链式漂移
        self.alias_trust_chained_min_df = max(0, int(alias_trust_chained_min_df))
        # 名字显著性打分（df 加权 × 次线性词频）；False = 旧的加权词频口径
        self.name_salience = bool(name_salience)
        # PPR 迭代上限可配：PPR 是单查询最大单项成本（实测 ~90ms/Q，占检索耗时 90%+）
        self.max_iter = max(1, int(ppr_max_iter))
        # M7 篇章路由：查询点名篇章时把候选池缩到该篇文档（详见 retrieve 通道④）
        self.chapter_routing = bool(chapter_routing)
        self.chapter_top = max(0, int(chapter_top))
        self.chapter_max_names = max(1, int(chapter_max_names))
        self.weight_chapter = float(weight_chapter)
        # 词法兜底档位（旧 config 里 plot_lexical_topup 是死配置，这里接上）
        self.lexical_topup = bool(lexical_topup)
        self.lexical_always = bool(lexical_always)
        # 提及通道每实体候选块数 / 总候选上限（M7：由硬编码改为可配，见 _mention_channel）
        self.mention_per_entity = max(1, int(mention_per_entity))
        self.mention_total_cap = max(1, int(mention_total_cap))
        # M8 语义通道（跨语言检索层）：索引缺失/过期即静默停用（见 plot_semantic 模块）
        self.semantic = semantic_index
        self.semantic_enabled = bool(semantic_enabled)
        self.semantic_top = max(0, int(semantic_top))
        self.weight_semantic = float(weight_semantic)
        self.semantic_link_min = float(semantic_link_min)
        self.semantic_link_top = max(0, int(semantic_link_top))
        self.semantic_min_score = float(semantic_min_score)
        # P1-4 召回率修复：融合层保底保留名额（语义/篇章两通道各自至少入选 N 块）。
        # 默认 0 = 关闭（零回归）；>0 时由 _rescue_floor 在 RRF 融合后执行保留。
        self.min_semantic_kept = max(0, int(min_semantic_kept))
        self.min_chapter_kept = max(0, int(min_chapter_kept))
        # 60 题 never_candidate 专项：融合后「语义补位重排」。默认关（零回归），
        # 启用后由 _rerank_topup 在 RRF 融合后补位。缓存行号映射，避免每次重建。
        self.rerank_topup_enabled = bool(rerank_topup_enabled)
        self.rerank_topup_keep = max(0, int(rerank_topup_keep))
        self._sem_hash2row: dict[str, int] | None = None
        # P0-1 / P0-4：弱证豁免来源集合 + node specificity 开关（均默认关闭/空 = 现状逐位一致）
        self.exempt_sources: frozenset[str] = frozenset(exempt_sources or ())
        self.node_specificity = bool(node_specificity)
        # M-11 埋点（P0-5）：默认关；关时不构造 trace、不写盘、不做任何计时开销
        self.trace_enabled = bool(trace_enabled)
        self.character_id = str(character_id or "")
        self.trace_out_path = trace_out_path
        self._trace_config = dict(trace_config or {})
        self.pipeline_version = str(pipeline_version or "plot-v1.0")
        self.last_trace = None  # 最近一次 retrieve() 的 trace（评测聚合用，不在生产读）
        # P0 消融的「是否被测到」计数（§7.6.6 阴性证据通则）：
        #   「Δ≈0」有两种完全不同的解读——「功能无效」与「功能从未触发」。
        #   没有执行计数就无法区分，所以每个 P0 功能必须在**每轮检索**留下触发次数。
        # 语义：该功能本次**实际改变了检索输入/输出**的计量（候选级与采用级分开记），
        # 供 M-12 的 `ablation.cases_executed` 使用。埋点本身不参与检索，故零开销。
        self.last_activation: dict[str, int] = {}
        self._d1_stats: dict[str, int] = {"d1_seeds_total": 0, "d1_seeds_downweighted": 0}
        self._trusted_cache: dict[str, set[str]] = {}
        self._trusted_cache_rev: int = -1
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
        # 查询侧实体扩展（默认 None = 关闭，行为与改动前逐位一致）。
        # 构造与白名单解析都在 plot_entity_expand.py；这里只持有引用。
        self.entity_expander = entity_expander
        if self.entity_expander is not None and hasattr(self.entity_expander, "bind_store"):
            # 白名单必须来自「检索器实际能链接到的名字表」（图谱正名 + 别名），
            # 不能用正典角色名单——那会误挡 troll/umbrella 这类非角色证据词。
            try:
                self.entity_expander.bind_store(self.store)
            except Exception as exc:  # noqa: BLE001 —— 绑定失败即退化为不扩展
                logger.warning("实体扩展白名单绑定失败：%s", exc)

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
            dropped_pronoun = 0
            for ent in self._entities():
                eid = str(ent.get("id"))
                raw = [str(ent.get("name") or "")] + [
                    str(a) for a in (ent.get("aliases") or [])
                ]
                cnorm = norm_name(raw[0])
                canon[eid] = cnorm
                # 代词/敬称/填充词一律不进**链接用名字表**（正名与别名同等待遇）。
                # 理由见 is_pronoun_or_filler 的 docstring：别名绕过建图期噪声过滤，
                # 导致 me→Shamane、I→Calabona 这类别名让任何英文句子都能点火。
                keep = []
                for n in raw:
                    nn = norm_name(n)
                    if not nn:
                        continue
                    if is_pronoun_or_filler(n):
                        dropped_pronoun += 1
                        continue
                    keep.append(nn)
                if not keep:
                    keep = [cnorm]  # 兜底：全部被拒时至少保留正名，避免实体彻底不可链接
                named.append((eid, cnorm, keep))
            self._named_cache = named
            self._canon_map_cache = canon
            if dropped_pronoun:
                logger.info("链接用名字表已剔除 %d 条代词/敬称/填充词名", dropped_pronoun)
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
    def _is_exempt_edge(self, edge: dict) -> bool:
        """该边是否命中弱证豁免来源（P0-1 / C4）。口径与 ``filter_edges`` 同一实现。"""
        return _edge_is_exempt(edge, self.exempt_sources)

    def _graph_view(self) -> tuple[list[dict], tuple, dict[str, list[str]]]:
        """按 ``(revision, min_confidence, include_weak, exempt_sources)`` 缓存的图视图。

        返回 ``(过滤后的边表, PPR 邻接(adj, deg), hop 邻接)``。
        旧实现每次 ``retrieve()`` 都要 3 次 ``all_edges()`` 浅拷贝 + 3 次过滤 +
        2 次邻接重建（5719 边量级），实测 PPR 一次 88ms。

        **P0-1 注意**：缓存键必须含 ``exempt_sources``——它改变过滤结果，漏进键会让
        改配置后仍读旧邻接（与 M7「Registry 漏传配置」是同一类静默失效）。
        """
        key = (self.store.revision, float(self.min_confidence), bool(self.include_weak),
               self.exempt_sources)
        cached = self._graph_view_cache
        if cached is not None and cached[0] == key:
            return cached[1], cached[2], cached[3]
        # 边表与邻接必须用**同一份**过滤口径（graph_ppr.filter_edges 是唯一来源），
        # 否则会出现「邻接里没有、边循环里却有」的弱证据边漏网。
        edges = filter_edges(
            _edges_of_store(self.store),
            min_confidence=self.min_confidence,
            include_weak=self.include_weak,
            exempt_sources=self.exempt_sources,
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

    def _trusted_names(self, eid: str, names: list[str]) -> set[str]:
        """本实体的「可信名」归一集合：人工表别名 ∪ 正名 ∪ 与之形态相近的抽取别名。

        为什么需要（实测，2026-09-12 真实对话诊断）：
        - 语料是英文 ASR，**2949 个中文正名实体里 1820 个（62%）的中文名在语料零命中**，
          提及召回完全依赖抽取别名；
        - 抽取别名里混着与实体无关的词：实体「牙仙」的别名含 `doll`(df=21)、
          `Campbell`(df=13)、`my girl`；「阿尔卡纳」的别名含 `Arkanist`（=**神秘学家**，
          另一个实体）。等权计数时这些词会**劫持整个提及通道**——实测牙仙的提及 top-3
          全是 Campbell/doll 的块，一块都不含 Tooth Fairy。
        可信名三部分缺一不可：
        1. 人工别名表登记的别名（人写的，最高可信；含因冲突被跳过的声明）；
        2. 实体正名本身；
        3. 与上述名字**形态相近**的抽取别名（ASR 变体必须走这条才不被误杀）。
        实体完全未进人工表时，用「df 最大的名字」当临时锚兜底，否则可信集为空、
        该实体在提及通道上彻底失声。
        """
        cached = self._trusted_cache.get(eid)
        if cached is not None and self._trusted_cache_rev == self.store.revision:
            return cached
        ent = self.store.get_entity(eid) or {}
        canon = norm_name(str(ent.get("name") or ""))
        trusted: set[str] = set(self.store.human_aliases(eid))
        if canon:
            trusted.add(canon)
        if not trusted and names:
            # 兜底锚：语料中出现次数最多的那个名字（通常是真名的英文写法）
            strongest = max(
                names, key=lambda n: len(self._name_hits(n)[0] or {})
            )
            sn = norm_name(strongest)
            if sn:
                trusted.add(sn)
        # 形态相近扩展分两档（防链式漂移）：
        # ① 与人工锚/正名**直接**相近的变体不限 df —— ASR 真变体（Sinetto/Sonnetto/
        #    Ms.Tooth Fairy）必须全收，否则该角色最常出现的写法反而进不了可信集；
        # ② 由变体再衍生出的**链式变体**须 df ≥ 阈值 —— 否则 "miss"→"miss campbell"
        #    →"campbell" 这类链条会把无关人名一路拖进可信集（实测踩过）。
        direct: set[str] = set()
        for n in names:
            nn = norm_name(n)
            if nn and nn not in trusted and _is_name_variant(nn, trusted):
                direct.add(nn)
        trusted |= direct
        min_df = max(0, int(self.alias_trust_chained_min_df))
        if min_df > 0:
            for _ in range(2):
                for n in names:
                    nn = norm_name(n)
                    if not nn or nn in trusted:
                        continue
                    hits, _w = self._name_hits(n)
                    if len(hits or {}) < min_df:
                        continue
                    if _is_name_variant(nn, trusted):
                        trusted.add(nn)
        if self._trusted_cache_rev != self.store.revision:
            self._trusted_cache.clear()
            self._trusted_cache_rev = self.store.revision
        self._trusted_cache[eid] = trusted
        return trusted

    def _mention_channel(
        self,
        targets: dict[str, float],
        *,
        per_entity: int | None = None,
        total_cap: int | None = None,
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

        ``per_entity`` / ``total_cap`` 缺省取实例配置（M7 从硬编码改为可配）：
        旧实现写死 3 / 6，实测**多跳题的第 4+ 候选块永远进不来**——灰机标准题
        「在中央塔里自囚的医生是谁」的答案块（同时含 central tower 与 Aleph）
        在种子「高塔」名下正排第 4，白丢一组证据。
        """
        if per_entity is None:
            per_entity = self.mention_per_entity
        if total_cap is None:
            total_cap = self.mention_total_cap
        if not targets or per_entity <= 0:
            return []
        chunks = self.corpus.chunks
        total_docs = max(1, len(chunks))
        use_idf = self.mention_scoring == "idf"
        # 每个目标实体 → [(命中表, 原始权重, idf 权重)]
        per_entity_data: list[
            tuple[str, float, list[tuple[str, dict[int, int], float, float, bool]]]
        ] = []
        for eid, base in targets.items():
            ent = self.store.get_entity(eid)
            if not ent:
                continue
            ent_name = str(ent.get("name") or eid)
            raw: list[tuple[str, dict[int, int], float]] = []
            for n in [ent_name] + [str(a) for a in (ent.get("aliases") or [])]:
                hits, weight = self._name_hits(n)
                if not hits:
                    continue
                raw.append((n, hits, weight))
            if not raw:
                continue
            trusted = self._trusted_names(eid, [n for n, _h, _w in raw])
            entries: list[tuple[str, dict[int, int], float, float, bool]] = []
            for n, hits, weight in raw:
                is_trusted = norm_name(n) in trusted
                # 名字显著性 = 可信度 × (1 + ln df)：可信名（人工表/正名/其变体）
                # 全权重，抽取来的可疑名降权到 alias_trust_ratio；df 让"最常与实体
                # 一起出现的写法"（Tooth Fairy df=62）压过偶然混入的词（doll df=21）。
                salience = (1.0 if is_trusted else self.alias_trust_ratio) * (
                    1.0 + math.log(1.0 + len(hits))
                )
                entries.append((n, hits, weight, salience, is_trusted))
            per_entity_data.append(
                (ent_name, 1.0 if base >= 1.0 else 0.5, entries)
            )
        if not per_entity_data:
            return []

        # 块 → {实体序号: 该实体给出的分数}
        picks: dict[int, dict[int, float]] = {}
        ranked_by_entity: dict[int, list[tuple[float, int]]] = {}
        for ei, (_name, seed_factor, entries) in enumerate(per_entity_data):
            trusted_pool: dict[int, float] = {}
            untrusted_pool: dict[int, float] = {}
            for _n, hits, w_raw, salience, is_trusted in entries:
                pool = trusted_pool if is_trusted else untrusted_pool
                for i, n in hits.items():
                    if use_idf:
                        # 可选的 idf 模式（换语料时复评；本语料实测更差，见审计报告）
                        idf = math.log(
                            1.0 + total_docs / max(1, len(hits))
                        ) * w_raw / max(w_raw, 1e-9)
                        pool[i] = pool.get(i, 0.0) + w_raw * idf * (1.0 + 0.3 * math.log(n))
                    elif self.name_salience:
                        # 名字显著性 × 次线性词频：可信名 + 常与实体同现的写法优先
                        pool[i] = pool.get(i, 0.0) + w_raw * salience * (
                            1.0 + 0.3 * math.log(n)
                        )
                    else:
                        # 旧口径（加权词频）：保留为可回退档，供消融对比与紧急回滚
                        pool[i] = pool.get(i, 0.0) + w_raw * n
            ranked = sorted(trusted_pool.items(), key=lambda kv: (-kv[1], kv[0]))[
                :per_entity
            ]
            # 可疑名最多补 1 条候选块：防 Campbell/doll 类块占满每实体的名额
            if self.untrusted_extra_per_entity > 0 and untrusted_pool:
                taken = {i for i, _s in ranked}
                for i, s in sorted(
                    untrusted_pool.items(), key=lambda kv: (-kv[1], kv[0])
                ):
                    if i in taken:
                        continue
                    ranked.append((i, s))
                    break
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
        edges, ppr_adj, hop_adj = self._graph_view()
        # P0-4（D1）：node specificity 开启时，种子在归一化前逐乘 specificity = 1/deg。
        # deg 取**同一过滤口径**下的无向邻居数（用已缓存的 hop 邻接表，不另扫边）——
        # 这样"泛种子"（洞穴/海盗这类与几乎所有实体都相连的词）的权重被压低，
        # 传播质量不再被它稀释。deg 为 0 的孤立种子按 specificity=1.0（不做除法），
        # 否则 1/0 会把它直接抹掉（那是"惩罚"而不是"降权"）。
        seed_weights = None
        self._d1_stats = {"d1_seeds_total": 0, "d1_seeds_downweighted": 0}
        if self.node_specificity and seeds:
            seed_weights = {}
            for eid in seeds:
                deg = len(hop_adj.get(eid) or ())
                seed_weights[eid] = 1.0 / deg if deg > 0 else 1.0
            # §7.6.6：D1 的「执行计数」= 本轮**真正被降权**的种子数（权重 <1 才算改到了输入）。
            # 门控给了 1 个孤立种子（deg=0 → specificity=1.0）时本轮 D1 事实上没生效——
            # 这种轮次不能计入 cases_executed，否则"未触发"会被当成"触发了但无效果"。
            self._d1_stats = {
                "d1_seeds_total": len(seed_weights),
                "d1_seeds_downweighted": sum(
                    1 for w in seed_weights.values() if w < 1.0
                ),
            }
        return personalized_pagerank(
            edges,
            seeds,
            min_confidence=0.0,
            include_weak=True,
            damping=self.damping,
            max_iter=self.max_iter,
            adjacency=ppr_adj,
            seed_weights=seed_weights,
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
        topup: bool | None = None,
    ) -> list[RetrievedChunk]:
        """返回剧情证据块（四通道 RRF 融合：边证据 / 提及块 / 篇章 / 词法兜底）。

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
        # ── 查询侧实体扩展（默认关）──
        # 位置很关键：必须在 detect_lang / link_detailed 之前，这样所有通道看到的都是扩展后的查询。
        # 失败时 expand() 内部已降级为返回原查询，故此处无需再兜底判断。
        if self.entity_expander is not None:
            query = self.entity_expander.expand(query)
        # ── M-11 埋点（P0-5）：全程 try-except，异常置 trace=None，绝不影响检索 ──
        # P0 消融执行计数（§7.6.6）：本轮重置，末尾写回 self.last_activation。
        # `c4_candidates` = 被豁免保留、且落在跳距内的弱证边数（C4 本轮的**可能作用面**）；
        # `c4_used`      = 其中真正产出了证据块进入融合的条数（C4 本轮的**实际作用面**）。
        # 两者分开：只报 used 会把"候选进了竞争但没赢"误判成"功能没触发"。
        act: dict[str, int] = {"c4_candidates": 0, "c4_used": 0}
        tc = TraceCollector(
            enabled=self.trace_enabled,
            character_id=self.character_id,
            config=self._trace_config,
            out_path=self.trace_out_path,
            pipeline_version=self.pipeline_version,
            query_lang=detect_lang(query),
        )
        with tc.stage("link_ms"):
            _linked = self.link_detailed(query)
            seeds = self.seed_gate(_linked)
        # seeds[] 记 `link_detailed ∪ seed_gate`：被门控拒掉的种子也要留痕（带 gate_passed=False），
        # 否则"门控拦了什么"完全不可见——而那正是负样本零注入的成因侧证据。
        tc.set_seeds({
            eid: dict(info or {}, gate_passed=(eid in seeds))
            for eid, info in _linked.items()
        })
        _exact = [eid for eid, info in _linked.items() if (info or {}).get("path") == "exact"]
        _exact_passed = [eid for eid in _exact if eid in seeds]
        tc.mark("别名精确", enabled=True, executed=bool(_linked),
                hit_count=len(_exact_passed),
                skip_reason=(ChannelSkipReason.NO_CANDIDATE if not _linked
                             else ChannelSkipReason.GATE_REJECTED),
                detail={"linked_total": len(_linked), "exact_total": len(_exact),
                        "gate_passed": len(seeds),
                        # 本通道是**种子来源维度**（架构 §7.6.1）：hit_count 的单位是种子，
                        # 不是块。块级命中数在收口处按 channel_of_block 统一补 hit_blocks。
                        "unit": "seed（块通道为 mention；hit_blocks 为其块级候选数）"})
        if not seeds:
            # 种子为空 -> 依赖种子的通道整体短路（图传播/提及），必须显式记录原因，
            # 否则看板无法区分"没跑"与"跑了但空手"。
            for _name in ("图传播", "篇章路由"):
                tc.mark(_name, enabled=True, executed=False,
                        skip_reason=ChannelSkipReason.NO_SEED)
        if topup is None:
            topup = self.lexical_topup
        # ── M8 语义通道（跨语言检索层）──────────────────────────────────────
        # 查询向量**一次嵌入、两处复用**（块检索 + 实体链接兜底），因为本地嵌入
        # 单次请求是这一层最贵的开销（实测 nomic 单条 p50 ≈ 0.4s，批量 16 条只要 0.6s）。
        # 索引缺失/过期/嵌入服务不可用一律静默跳过（semantic_items 为空，行为=本层不存在）。
        semantic_items: list[tuple[float, object, dict]] = []
        # 查询向量：语义通道嵌入一次后由补位重排复用（二次嵌入是这一层最贵的开销）。
        # 必须**先置 None**：下面只在语义通道可用时赋值，否则补位重排读它会 NameError。
        qvec = None
        # 语义通道的跳过原因用局部变量累积，最后**统一收口**——原因必须三选一且可区分：
        # 没开 / 索引缺失 / 无种子 / 嵌入失败 / 无候选。旧实现在这里全是静默的，
        # 看板空态无法编码（架构 §7.6 的原始动因）。
        _sem_skip: ChannelSkipReason = ChannelSkipReason.NOT_ENABLED
        _sem_executed = False
        if self.semantic_enabled and self.semantic is not None and self.semantic.available:
            _sem_executed = True
            _sem_skip = ChannelSkipReason.NO_CANDIDATE
            with tc.stage("semantic_ms"):
                qvec = self.semantic.embed_query(query)
            if qvec is None:
                # 嵌入服务不可用 -> 降级（与"没候选"是两类原因，必须分开记）
                _sem_skip = ChannelSkipReason.EMBED_FAILED
                tc.fallback(ChannelSkipReason.EMBED_FAILED)
            if qvec is not None:
                # 语义实体链接兜底：精确名匹配全军覆没时，用实体名向量找回种子。
                # 这正对「只描述不点名」的问法（「海盗船上的歌手」「雾中女巫」）——
                # 此时图路是死的（没种子就没 PPR、没提及块），唯有语义能救。
                # AC-3 标定数据的**可得性缺陷**（本轮实测发现）：实体链接兜底原先被
                # `semantic_link_min > 0` 整体短路，而生产该值恰为 0.0 —— 于是
                # `entity_link_margin` 在真实运行里**从未被填充过**：契约字段齐全、
                # 数据恒空（"m == 0 是没测到，不是没效果"的同类错误）。
                # 修法：**埋点轮**里无条件为候选打分并落盘 margin，但**连接行为仍由阈值
                # 决定**——阈值未配置时 `_passed` 恒空 ⇒ 不新增种子 ⇒ 检索结果逐位不变；
                # 生产（trace 关）完全不进这段 ⇒ 零延迟影响。
                _want_margin = tc.trace is not None
                if not seeds and self.semantic_link_top > 0 and (
                        self.semantic_link_min > 0 or _want_margin):
                    _cand = self.semantic.search_entities(qvec, self.semantic_link_top)
                    _passed = [
                        (eid, score) for eid, score in _cand
                        if self.semantic_link_min > 0 and score >= self.semantic_link_min
                        and eid in {str(e.get("id")) for e in self._entities()}
                    ]
                    if _want_margin:
                        # AC-3：margin 是安全间隔阈值的**唯一**标定依据，必须逐轮落盘
                        tc.trace.entity_link_margin.fill(
                            [float(s) for _e, s in _cand],
                            threshold=self.semantic_link_min,
                            linked=bool(_passed),
                            reject_reason=(
                                None if _passed
                                else ("below_threshold" if self.semantic_link_min > 0
                                      else "no_threshold_configured")),
                        )
                    for eid, score in _passed:
                        seeds[eid] = float(score)
                    if _passed:
                        tc.set_seeds({
                            eid: dict(info or {}, gate_passed=(eid in seeds))
                            for eid, info in _linked.items()
                        })
                # ⚠️ **必须过种子门控**：语义检索什么都不看就能对任何问句返回"最像"的
                # top-K——实测不设门时「今天天气怎么样」「用 Python 写一个快速排序」
                # 各被注入 5 块无关转写（10 条负样本合计从 0 块变成 49 块）。
                # 口径与词法兜底一致：「剧情层只回答图能认得的问题」。
                # 关键是它不牺牲收益：分诊显示失败题的种子**几乎总是非空**
                # （只是选错了，如「洞穴」「海盗」），门控拦掉的是离题问句而非目标问句。
                if seeds and self.semantic_top > 0:
                    for h, score in self.semantic.search(qvec, self.semantic_top):
                        if score < self.semantic_min_score:
                            continue
                        chunk = self.corpus.by_hash(str(h))
                        if chunk is None:
                            continue
                        semantic_items.append(
                            (
                                float(score),
                                chunk,
                                {"via": "plot_graph", "path": "semantic",
                                 "semantic_score": round(float(score), 4)},
                            )
                        )
                elif not seeds:
                    # 有向量但没种子：语义块通道被种子门控短路（不是"没候选"）
                    _sem_skip = ChannelSkipReason.NO_SEED
        # 语义通道统一收口（六通道每轮必有一条记录）
        tc.mark("语义向量", enabled=self.semantic_enabled, executed=_sem_executed,
                hit_count=len(semantic_items),
                skip_reason=None if semantic_items else _sem_skip,
                weight=self.weight_semantic,
                detail={"top": self.semantic_top, "min_score": self.semantic_min_score,
                        "embedder": getattr(self.semantic, "embedder_name", "") if
                        self.semantic is not None else ""})
        # 实体查询（P2）：短查询且精确命中实体名 → 提及块优先于边证据。
        # 依据（真实对话诊断）：问"X 是谁"时，边证据块天生信息量最低——实测
        # 「芭卡洛儿你还记的吗？」的前两块都是"Could be someplace ten years ago…"
        # 这类与实体无关的关系证据，而含 Barcarola 的块排在第 3 位之后。
        mention_weight = self.weight_mention
        if seeds and self.entity_query_max_len > 0 and self.weight_mention_entity > 0:
            if len(query.strip()) <= self.entity_query_max_len:
                mention_weight = self.weight_mention_entity
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
                if weak and self._is_exempt_edge(e):
                    # C4（P0-1）作用面：这条边原文会被弱证门过滤掉，靠豁免才留在视图里
                    act["c4_candidates"] += 1
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
            _weak_exempt_edge = False
            for score, e in scored[: self.max_edges]:
                _weak_exempt_edge = (
                    len(e.get("evidence") or []) < WEAK_EVIDENCE_MIN
                    and self._is_exempt_edge(e)
                )
                for ev in e.get("evidence") or []:
                    h = ev.get("hash")
                    if not h or h in seen_edge_ev:
                        continue
                    chunk = self.corpus.by_hash(str(h), doc_id=ev.get("doc_id"))
                    if chunk is None:
                        continue
                    seen_edge_ev.add(str(h))
                    if _weak_exempt_edge:
                        act["c4_used"] += 1  # 豁免边真的贡献了证据块
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
        chapter_items: list[tuple[float, object, dict]] = []
        # 图路"命中数"必须按**去重后的块**计：同一块常同时出现在边证据与提及两路，
        # 按通道条目数相加会把 1 块当成 2 块，导致 topup 判定失效（该补词法却不补）。
        graph_hashes = {
            str(getattr(c, "hash", "") or "")
            for _s, c, _m in list(edge_items) + list(mention_items) + list(semantic_items)
        }
        graph_count = len(graph_hashes - {""})
        # 词法兜底只服务于「图能认得」的查询（**通过门控的种子非空**）：
        # 没有任何可信种子时整体短路——否则任何含常见词的问句都会被 BM25 灌进
        # 5–7 块无关转写（实测「1+1 等于几」「给我讲个笑话」各注入 5 块）。
        need_fallback = bool(seeds) and (
            graph_count == 0 if not topup else graph_count < max(0, top_chunks)
        )
        # M7：正典中文层落库后，BM25 对中文查询**不再是噪声**（中文问 ↔ 中文正文），
        # 因此允许「有可信种子就常开词法路」，由 lexical_fallback 名额兜住。
        # 仍然要求 seeds 非空——离题问句过不了种子门控，负样本零注入的护栏不变。
        if self.lexical_always and seeds and lexical_fallback > 0:
            need_fallback = True
        if need_fallback and lexical_fallback > 0:
            need = max(0, top_chunks) + max(0, lexical_fallback)
            for chunk, s in self.corpus.search(query, top_k=need):
                lexical_items.append(
                    (float(s), chunk, {"via": "plot_lexical", "path": "lexical"})
                )

        # 通道④：篇章路由（M7）。用户点名了篇章（「洞穴的囚徒篇里海盗船上的歌手是谁」）
        # 时，把候选池缩到该篇的文档再跑 BM25——**这是唯一能救这类问题的通道**：
        #   ① 查询里没有答案实体的名字 ⇒ 实体链接取不到种子（分诊实测 147 组）；
        #   ② B 站语料是英文 ASR，中文问法与英文正文无法词法匹配；
        #   ③ 而灰机正典层是中文原文，且篇章名在语料元数据里是精确可匹配的。
        # 与词法兜底的区别：**不要求图路零命中**（点名篇章本身就是强意图信号）。
        if self.chapter_routing and self.chapter_top > 0:
            chapters = self.corpus.chapters_in(query)
            if chapters:
                pool: set[str] = set()
                idx = self.corpus.chapter_index()
                for name in chapters[: self.chapter_max_names]:
                    pool |= idx.get(name, set())
                if pool:
                    for chunk, s in self.corpus.search(
                        query, top_k=self.chapter_top, doc_ids=pool
                    ):
                        chapter_items.append(
                            (
                                float(s),
                                chunk,
                                {
                                    "via": "plot_graph",
                                    "path": "chapter",
                                    "chapter_route": "／".join(chapters[:3]),
                                },
                            )
                        )

        # RRF 融合 + 归一化分数带 + 同一 doc 软去冗余（见 _fuse_channels）
        # 预算语义（与旧实现一致）：**图路可用满整个返回预算**
        # （top_chunks + lexical_fallback）；词法兜底只在图路不足时占用剩余名额。
        # 实测教训：把图路硬压到 top_chunks(=3) 会让返回块数从 4.83 掉到 2.86，
        # 严格通过率直降 9pt——证据块并集口径下，"少给块"就是"少覆盖"。
        graph_limit = max(0, top_chunks)
        # ── M-11：其余五通道收口（语义通道已在上方收口）──
        # 图传播 = edge + mention（架构 §7.6.1：mention 块归入「图传播」组展示，
        # 其种子来源由 seed_path 决定它同时算不算「别名精确」）。
        # `hit_blocks` 是按**同一归组函数**（channel_of_block）数出的候选块数，
        # 与 `kept_in_final` 同量纲——保留率必须用这两个算，不能用 hit_count：
        # 「别名精确」是种子来源维度，其 hit_count 是**种子数**（实测拿它当分子
        # 会得到 kept_rate=229% 这种不可能读数）。
        _blk: Counter = Counter()
        for _s, _c, _m in (list(edge_items) + list(mention_items) + list(semantic_items)
                           + list(lexical_items) + list(chapter_items)):
            _ch = channel_of_block(str((_m or {}).get("path") or ""), _m or {})
            if _ch:
                _blk[_ch] += 1
        # 这两个通道在上面就收口了（候选列表当时还没齐），此处**补块级命中数**：
        # 它们的候选块有一部分来自 mention（按 seed_path 归组），只有列表全齐后才能数。
        for _name in ("别名精确", "语义向量"):
            tc.mark(_name, hit_blocks=_blk.get(_name, 0))
        tc.mark("BM25 兜底", enabled=lexical_fallback > 0, executed=bool(seeds),
                hit_count=len(lexical_items), hit_blocks=_blk.get("BM25 兜底", 0),
                skip_reason=(ChannelSkipReason.NOT_ENABLED if lexical_fallback <= 0
                             else ChannelSkipReason.NO_SEED if not seeds
                             else ChannelSkipReason.NO_CANDIDATE),
                weight=self.weight_lexical,
                detail={"need_fallback": bool(need_fallback)})
        tc.mark("图传播", enabled=True, executed=bool(seeds),
                hit_count=len(edge_items) + len(mention_items),
                hit_blocks=_blk.get("图传播", 0),
                skip_reason=(ChannelSkipReason.NO_SEED if not seeds
                             else ChannelSkipReason.NO_CANDIDATE),
                weight=self.weight_edge,
                detail={"max_edges": self.max_edges, "hops": self.max_hops,
                        "edge_items": len(edge_items), "mention_items": len(mention_items),
                        # C4 执行计数随通道落盘：单查询层也能看出"手工边这轮有没有起作用"
                        "c4_candidates": act["c4_candidates"], "c4_used": act["c4_used"]})
        tc.mark("篇章路由", enabled=self.chapter_routing, executed=bool(seeds),
                hit_count=len(chapter_items), hit_blocks=_blk.get("篇章路由", 0),
                skip_reason=(ChannelSkipReason.NOT_ENABLED if not self.chapter_routing
                             else ChannelSkipReason.NO_SEED if not seeds
                             else ChannelSkipReason.NO_CANDIDATE),
                weight=self.weight_chapter)
        tc.mark("扩展查询", enabled=False, executed=False,
                skip_reason=ChannelSkipReason.NOT_ENABLED,
                detail={"why": "P1-1（A1 块级中文翻译索引）未启用"})
        with tc.stage("fuse_ms"):
            fused = self._fuse(
                lexical_items, graph_count, edge_items, mention_items, mention_weight,
                semantic_items, chapter_items, graph_limit, lexical_fallback,
            )
        # ── P1-4 召回率修复：融合层保底保留（rescue floor）──
        # 诊断：100/105 失败题的「正解块」已被语义/篇章通道取回，却被 RRF 融合层挤出
        # 最终 top_chunks+lexical_fallback 预算（bucket4_fusion_squeeze）。此处保证语义、
        # 篇章两通道各自至少保留 min_* 块入选，用最低分图块（edge/mention/lexical）让位。
        # 默认 min_*=0 时本段为 no-op，零回归。
        fused = self._rescue_floor(
            fused, semantic_items, chapter_items,
            budget=max(0, top_chunks + max(0, lexical_fallback)),
            min_semantic=self.min_semantic_kept,
            min_chapter=self.min_chapter_kept,
        )
        # ── 60 题 never_candidate 专项：语义补位重排（默认关，零回归）──────────
        # 只走「有查询向量」的分支：没有语义索引就无从算余弦，此时保持原结果。
        if self.rerank_topup_enabled and qvec is not None and self.semantic is not None:
            fused = self._rerank_topup(
                qvec,
                fused,
                (edge_items, mention_items, semantic_items, chapter_items, lexical_items),
                budget=max(0, top_chunks + max(0, lexical_fallback)),
            )
        out: list[RetrievedChunk] = []
        for score, chunk, extra in fused:
            meta = chunk.meta(self.namespace)
            meta.update(extra or {})
            out.append(RetrievedChunk(text=chunk.text, score=float(score), metadata=meta))
        out = out[: max(0, top_chunks + max(0, lexical_fallback))]
        # §7.6.6：执行计数与 trace 同轮收口（trace 关时也要有，消融判据依赖它）
        act.update(self._d1_stats)
        act["semantic_items_in"] = len(semantic_items)
        act["seeds_total"] = len(seeds)
        self.last_activation = act
        # 收口：先把 kept_in_final 归因好，再落盘（否则 kept 恒 0，桶 4 无法量化）
        self.last_trace = tc.finish(query=query, final_chunks=out)
        return out

    def _fuse(
        self, lexical_items, graph_count, edge_items, mention_items, mention_weight,
        semantic_items, chapter_items, graph_limit, lexical_fallback,
    ):
        """RRF 融合分派（从 retrieve() 抽出，只为让埋点能整段计时）。"""
        if lexical_items and graph_count:
            # 两路共存（topup）：图路占 top_chunks 名额，词法只补 lexical_fallback 个
            fused = self._fuse_channels(
                [
                    ("edge", self.weight_edge, edge_items),
                    ("mention", mention_weight, mention_items),
                    ("semantic", self.weight_semantic, semantic_items),
                    ("chapter", self.weight_chapter, chapter_items),
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
                    ("mention", mention_weight, mention_items),
                    ("semantic", self.weight_semantic, semantic_items),
                    ("chapter", self.weight_chapter, chapter_items),
                ],
                limit=graph_limit + max(0, lexical_fallback),
            )
        return fused

    def _semantic_hash2row(self) -> dict[str, int]:
        """语义索引 ``hash → 行号``（补位重排取块向量用，构建一次后缓存）。

        ``sem.hashes`` 是 numpy 数组，**不能**用 ``or`` 判空（会触发
        "truth value of an array ... is ambiguous"），必须显式判 None。
        """
        if self._sem_hash2row is not None:
            return self._sem_hash2row
        sem = self.semantic
        hashes = getattr(sem, "hashes", None) if sem is not None else None
        self._sem_hash2row = (
            {str(h): i for i, h in enumerate(hashes)} if hashes is not None else {}
        )
        return self._sem_hash2row

    def _rerank_topup(
        self,
        qvec,
        fused: list[tuple[float, object, dict]],
        channels: tuple[list[tuple[float, object, dict]], ...],
        budget: int,
    ) -> list[tuple[float, object, dict]]:
        """融合后「语义补位」：保留前 ``rerank_topup_keep`` 名，剩余名额用候选池中
        查询余弦最高的块补齐。

        为什么是补位而不是整体重排（2026-09-17 全量实测，300 题）：
          - **整体余弦重排**：strict 195→196（+1），但 inject 177→**151（−26）**。
            原因：余弦偏袒「与 query 整体最像」的块，选出的 8 块高度同质，丢掉了
            RRF 多路命中带来的**互补证据**；而 inject 口径（2400 字符装配）恰恰
            需要多块互补才能覆盖全部证据组。
          - **保留前 3 名 + 余弦补位**：strict 195→**207（+12）**、inject 177→178（+1）、
            负样本失守 7/53 条与注入 54 块**均无变化**。

        为什么能救回失分题：失败 105 题里 60 题的正解块从未进入最终预算，但它们
        100% 存在于各通道候选池之外的语义空间里（全库排名 p50=54）。RRF 只按**名次**
        给分，深池块永远拿不到分；补位绕开名次，直接用余弦把这些块捞进剩余名额。

        分数带：RRF 把分数归一到 ``[FUSE_MIN_SCORE, 1.0]``，补位块的分数必须**低于**
        被保留的头部块，否则名次被打乱、``rerank_topup_keep`` 就失去意义。
        """
        keep_n = min(self.rerank_topup_keep, budget)
        if budget <= 0 or not fused or keep_n >= budget:
            return fused
        sem = self.semantic
        if sem is None or getattr(sem, "vectors", None) is None:
            return fused
        h2r = self._semantic_hash2row()
        if not h2r:
            return fused
        keep = list(fused[:keep_n])
        keep_h = {str(getattr(c, "hash", "") or "") for _s, c, _m in keep}
        # 候选池：五通道并集，按 hash 去重，剔除已保留的头部块
        pool: list[tuple[object, dict]] = []
        seen: set[str] = set()
        for items in channels:
            for _s, chunk, extra in items or ():
                h = str(getattr(chunk, "hash", "") or "")
                if not h or h in seen or h in keep_h or h not in h2r:
                    continue
                seen.add(h)
                pool.append((chunk, dict(extra or {})))
        if not pool:
            return fused
        # numpy 只在此处惰性导入：默认关闭时本文件不引入该依赖的任何开销
        import numpy as np  # noqa: PLC0415

        qn = np.asarray(qvec, dtype=np.float32)
        qn = qn / (float(np.linalg.norm(qn)) or 1.0)
        vecs = sem.vectors
        scored: list[tuple[float, int, object, dict]] = []
        for idx, (chunk, extra) in enumerate(pool):
            row = h2r.get(str(getattr(chunk, "hash", "") or ""))
            if row is None:
                continue
            v = vecs[row]
            nv = float(np.linalg.norm(v))
            if not nv:
                continue
            scored.append((float(np.dot(v, qn) / nv), idx, chunk, extra))
        if not scored:
            return fused
        scored.sort(key=lambda t: (-t[0], t[1]))
        picked = scored[: budget - len(keep)]
        keep_min = min((float(s) for s, _c, _m in keep), default=1.0)
        raw = [s for s, _i, _c, _e in picked]
        lo, hi = min(raw), max(raw)
        span = (hi - lo) or 1.0
        ceil_score = max(FUSE_MIN_SCORE, keep_min - 1e-3)
        out: list[tuple[float, object, dict]] = list(keep)
        for s, _i, chunk, extra in picked:
            frac = (s - lo) / span
            score = FUSE_MIN_SCORE + (ceil_score - FUSE_MIN_SCORE) * frac
            meta = dict(extra or {})
            meta["rerank_topup"] = True
            out.append((float(score), chunk, meta))
        return out

    def _rescue_floor(
        self,
        fused: list[tuple[float, object, dict]],
        semantic_items: list[tuple[float, object, dict]],
        chapter_items: list[tuple[float, object, dict]],
        budget: int,
        min_semantic: int,
        min_chapter: int,
    ) -> list[tuple[float, object, dict]]:
        """融合层保底保留（召回率修复 P1-4）。

        诊断（2026-09-17 全量评测 + ``analyze_recall.py``）：100/105 失败题的「正解块」
        已被语义/篇章通道取回，却被 RRF 融合层挤出最终 ``top_chunks+lexical_fallback``
        预算（``bucket4_fusion_squeeze``）。根因：边证据 + 提及两路从种子实体涌出大量块，
        把预算占满，单路命中的语义/篇章正解块被压到名次之外。

        本方法保证语义、篇章两通道各自至少保留 ``min_*`` 块进入最终集：若某通道顶部块
        未自然入选，用**最低融合分**的图块（edge/mention/lexical）让位——优先挤掉冗余图块，
        而非相关语义块。``min_*=0`` 时整段为 no-op，零回归。

        救援块分数钉在「当前已入选块的最低融合分 + ε」之上，确保它落在 RRF 归一化带
        （[0.6,1.0]）内并被 ``out[:budget]`` 保留（语义原始相似分不在该带内，直接用会被切片裁掉）。
        """
        if (min_semantic <= 0 and min_chapter <= 0) or not fused:
            return fused
        by_hash: dict[str, tuple[float, object, dict]] = {
            str(getattr(c, "hash", "") or ""): (s, c, m) for s, c, m in fused
        }
        min_score = min((s for s, _, _ in fused), default=FUSE_MIN_SCORE)
        rescue_score = max(FUSE_MIN_SCORE, min_score + 1e-3)
        desired: list[tuple[float, object, dict]] = []
        for path, items, floor in (
            ("semantic", semantic_items, min_semantic),
            ("chapter", chapter_items, min_chapter),
        ):
            for _s, chunk, extra in items[: max(0, floor)]:
                h = str(getattr(chunk, "hash", "") or "")
                if h and h not in by_hash:
                    meta = dict(extra or {})
                    meta["path"] = path
                    meta.setdefault("paths", [path])
                    meta["rescued_floor"] = True
                    desired.append((rescue_score, chunk, meta))
        if not desired:
            return fused
        work = list(fused)
        for item in desired:
            # 优先挤掉最低分且属图路（edge/mention/lexical）的冗余块；无图块可挤时
            # 在预算内追加，或替掉全局最低分块（无论如何都保留救援块）。
            victim = None
            for i in range(len(work) - 1, -1, -1):
                if (work[i][2] or {}).get("path") in ("edge", "mention", "lexical"):
                    victim = i
                    break
            if victim is not None:
                work[victim] = item
            elif len(work) < budget:
                work.append(item)
            else:
                work[-1] = item
        work.sort(key=lambda it: -it[0])
        return work[:budget]


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
        alias_trust_ratio: float = 0.25,
        untrusted_extra_per_entity: int = 1,
        weight_mention_entity: float = 1.0,
        entity_query_max_len: int = 14,
        alias_trust_chained_min_df: int = 3,
        name_salience: bool = False,
        ppr_max_iter: int = 20,
        alias_authoritative: bool = True,
        chapter_routing: bool = True,
        chapter_top: int = 3,
        chapter_max_names: int = 2,
        weight_chapter: float = 1.0,
        lexical_topup: bool = False,
        lexical_always: bool = False,
        mention_per_entity: int = 3,
        mention_total_cap: int = 6,
        embedder=None,
        semantic_enabled: bool = True,
        semantic_top: int = 5,
        weight_semantic: float = 1.0,
        semantic_link_min: float = 0.0,
        semantic_link_top: int = 3,
        semantic_langs: str = "",
        semantic_min_score: float = 0.0,
        min_semantic_kept: int = 0,
        min_chapter_kept: int = 0,
        rerank_topup_enabled: bool = False,
        rerank_topup_keep: int = 3,
        exempt_sources=None,
        node_specificity: bool = False,
        trace_enabled: bool = False,
        trace_dir: str | Path | None = None,
        entity_expander=None,
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
            alias_trust_ratio=alias_trust_ratio,
            untrusted_extra_per_entity=untrusted_extra_per_entity,
            weight_mention_entity=weight_mention_entity,
            entity_query_max_len=entity_query_max_len,
            alias_trust_chained_min_df=alias_trust_chained_min_df,
            name_salience=name_salience,
            ppr_max_iter=ppr_max_iter,
            alias_authoritative=alias_authoritative,
            chapter_routing=chapter_routing,
            chapter_top=chapter_top,
            chapter_max_names=chapter_max_names,
            weight_chapter=weight_chapter,
            lexical_topup=lexical_topup,
            lexical_always=lexical_always,
            mention_per_entity=mention_per_entity,
            mention_total_cap=mention_total_cap,
            semantic_enabled=semantic_enabled,
            semantic_top=semantic_top,
            weight_semantic=weight_semantic,
            semantic_link_min=semantic_link_min,
            semantic_link_top=semantic_link_top,
            semantic_langs=semantic_langs,
            semantic_min_score=semantic_min_score,
            min_semantic_kept=min_semantic_kept,
            min_chapter_kept=min_chapter_kept,
            rerank_topup_enabled=rerank_topup_enabled,
            rerank_topup_keep=rerank_topup_keep,
            exempt_sources=exempt_sources,
            node_specificity=node_specificity,
            trace_enabled=trace_enabled,
            trace_dir=trace_dir,
            entity_expander=entity_expander,
        )
        self._embedder = embedder
        self._trace_dir = Path(trace_dir) if trace_dir else None
        self._trace_enabled = bool(trace_enabled)
        self._semantic_cache: dict[str, tuple[float, object]] = {}
        self.semantic_status: dict[str, str] = {}
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
        semantic = self._load_semantic(key, cpath)
        retr = PlotGraphRetriever(
            corpus,
            store,
            namespace=plot_namespace(key),            min_confidence=self._cfg["min_confidence"],
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
            alias_trust_ratio=self._cfg["alias_trust_ratio"],
            untrusted_extra_per_entity=self._cfg["untrusted_extra_per_entity"],
            weight_mention_entity=self._cfg["weight_mention_entity"],
            entity_query_max_len=self._cfg["entity_query_max_len"],
            alias_trust_chained_min_df=self._cfg["alias_trust_chained_min_df"],
            name_salience=self._cfg["name_salience"],
            ppr_max_iter=self._cfg["ppr_max_iter"],
            # M7：这几项必须显式透传——漏传时 PlotGraphRetriever 会退回**构造默认值**，
            # 表现为「配置改了没反应」（篇章路由曾因此一直按默认 True 跑，
            # 关不掉也无法消融，是比崩溃更难查的一类缺陷）。
            chapter_routing=self._cfg["chapter_routing"],
            chapter_top=self._cfg["chapter_top"],
            chapter_max_names=self._cfg["chapter_max_names"],
            weight_chapter=self._cfg["weight_chapter"],
            lexical_topup=self._cfg["lexical_topup"],
            lexical_always=self._cfg["lexical_always"],
            mention_per_entity=self._cfg["mention_per_entity"],
            mention_total_cap=self._cfg["mention_total_cap"],
            semantic_index=semantic,
            semantic_enabled=self._cfg["semantic_enabled"],
            semantic_top=self._cfg["semantic_top"],
            weight_semantic=self._cfg["weight_semantic"],
            semantic_link_min=self._cfg["semantic_link_min"],
            semantic_link_top=self._cfg["semantic_link_top"],
            # M7 教训（本处第二次踩到）：`get()` 是**显式列参**构造检索器的，任何新增配置
            # 若只加进 `_cfg` 而忘了在这里透传，就会静默退回构造默认值——表现为
            # 「配置改了没反应」，是比崩溃更难查的一类缺陷（plot_graph.py 旧 1641-1643）。
            # 由 tests/test_plotrag_p0.py::TestRegistryPassthrough 逐项钉住。
            # 注：`semantic_langs` 不在此列——语言掩码在 Registry._load_semantic 加载索引时
            # 施加（set_row_mask），检索器本身不持有该配置。
            semantic_min_score=self._cfg["semantic_min_score"],
            min_semantic_kept=self._cfg["min_semantic_kept"],
            min_chapter_kept=self._cfg["min_chapter_kept"],
            rerank_topup_enabled=self._cfg["rerank_topup_enabled"],
            rerank_topup_keep=self._cfg["rerank_topup_keep"],
            exempt_sources=self._cfg["exempt_sources"],
            node_specificity=self._cfg["node_specificity"],
            # M-11 埋点：检索器需要 character_id / 落盘路径 / 配置快照来组 trace
            trace_enabled=self._trace_enabled,
            character_id=key,
            trace_out_path=(trace_path(self._trace_dir, key)
                            if (self._trace_enabled and self._trace_dir) else None),
            trace_config=self._cfg,
            # 查询侧实体扩展（默认 None = 关闭）。按上面的教训：必须显式透传，
            # 否则「配置改了没反应」。
            entity_expander=self._cfg.get("entity_expander"),
        )
        self._cache[key] = (cm, gm, retr)
        return retr

    def _load_semantic(self, cid: str, cpath: Path):
        """按需加载语义索引并做**四项指纹校验**；不可用一律返回 None（静默降级）。

        缓存键含 npz 的 mtime：重建索引后无需重启即可生效（与语料/图谱同款热重载策略）。
        """
        npath = self._corpus_dir / f"plot_index_{cid}.npz"
        jpath = self._corpus_dir / f"plot_index_{cid}.json"
        if not (npath.is_file() and jpath.is_file()):
            self.semantic_status[cid] = "未构建（缺 plot_index_*.npz/.json）"
            return None
        try:
            mt = npath.stat().st_mtime
        except OSError:
            self.semantic_status[cid] = "索引不可读"
            return None
        cached = self._semantic_cache.get(cid)
        if cached is not None and cached[0] == mt:
            return cached[1]
        from .plot_semantic import SemanticIndex, corpus_sha16

        idx = SemanticIndex(npath, jpath, embedder=self._embedder)
        if not idx.load():
            self.semantic_status[cid] = idx.disabled_reason
            self._semantic_cache[cid] = (mt, None)
            return None
        name = getattr(self._embedder, "name", "")
        dim = int(getattr(self._embedder, "dim", 0) or 0)
        ok, why = idx.check_fresh(embedder_name=name, dim=dim,
                                  corpus_sha16=corpus_sha16(cpath))
        if not ok:
            self.semantic_status[cid] = f"索引过期：{why}"
            logger.warning("剧情语义索引不可用（%s），本层静默停用：%s", cid, why)
            self._semantic_cache[cid] = (mt, None)
            return None
        self.semantic_status[cid] = f"ok（{idx.count} 块 / {name}）"
        # 可选：把语义候选池限制到指定语言（默认按配置，见 plot_semantic_langs）
        langs = {s.strip().lower() for s in str(self._cfg.get("semantic_langs") or "").split(",")
                 if s.strip()}
        if langs:
            want = [1 if (c.lang or "").lower() in langs else 0
                    for c in PlotCorpus(cpath, character_id=cid).chunks]
            if len(want) == idx.count:
                import numpy as _np
                idx.set_row_mask(_np.asarray(want, dtype=bool))
                self.semantic_status[cid] += f"｜限语言 {sorted(langs)}（" \
                    f"{int(sum(want))}/{len(want)} 块）"
        self._semantic_cache[cid] = (mt, idx)
        return idx

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
