"""全局配置中心（集中管理，运行时不可变）。

设计要点（对齐 2026 最佳实践）：
- pydantic-settings BaseSettings：单一配置入口，杜绝散落的 os.getenv。
- env_prefix="ROLEPLAY_"：环境变量与代码解耦，生产用真实环境变量注入。
- extra="ignore"：容忍 .env 中的无关项（脚手架阶段更友好）。
- frozen=True：配置仅在启动时解析一次，运行期不可篡改（防意外副作用）。
- 默认 llm_provider="mock"：无需任何 API Key 即可离线运行与测试。
"""
from dataclasses import dataclass
from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# ─────────────── LLM 端点本地性检测（唯一新增的检测逻辑） ───────────────
# 口径（2026-09-19 按用户明确要求修正）：
#   **只有 provider == "ollama"（真·本机推理引擎）才算「本地」。**
#
# 为什么不按地址判：地址在本机 ≠ 本地推理。典型反例是本机聚合网关
# （如 127.0.0.1:7863 的 workbuddy2api）——它虽然监听环回地址，但背后转发的是
# **云端模型**，既不占本地显存，也不该套用"为小显存调出来的"那套采样参数。
# 之前按 host ∈ {环回, RFC1918} 判本地的写法，会把这类网关误判成本地，
# 于是 max_tokens 被压到 240，思维链模型直接吐空回复。
#
# 判定：provider 归一化后是否等于 "ollama"；不解析 base_url、不发任何网络请求、零副作用。
# base_url 参数保留在签名里（调用点稳定），当前不参与判定——将来若要恢复
# "特定地址也算本地"的规则，只需在此函数内补条件。
_LOCAL_PROVIDERS = frozenset({"ollama"})


def is_local_llm_endpoint(provider: str | None, base_url: str | None = None) -> bool:
    """当前 LLM 端点是否为「本地推理」。见上方口径说明。"""
    del base_url  # 刻意不参与判定（地址在本机 ≠ 本地推理）
    return (provider or "").strip().lower() in _LOCAL_PROVIDERS


@dataclass(frozen=True)
class LLMProfile:
    """一次调用实际生效的采样参数（本地档 / 非本地档）。"""

    is_local: bool
    max_tokens: int
    top_p: float
    repetition_penalty: float | None
    temperature: float


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="ROLEPLAY_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
    )

    app_name: str = "RoleplayAI"
    debug: bool = False

    # ---- LLM ----
    llm_provider: Literal["mock", "openai", "deepseek", "ollama"] = "mock"
    llm_model: str = "mock-model"
    llm_api_key: str = ""
    llm_base_url: str = ""
    llm_temperature: float = Field(0.8, ge=0.0, le=2.0)
    # ---- 采样参数（角色扮演质量的关键旋钮）----
    # top_p：行业共识 0.9-0.95 过滤低概率废词。
    llm_top_p: float = Field(0.92, ge=0.0, le=1.0)
    # repetition_penalty：抑制"复读/照背 few-shot 原句/口头禅"。
    # 共识区间 1.05-1.15；**>1.2 为禁区**（会连角色名这类正常重复一起回避）。
    llm_repetition_penalty: float = Field(1.10, ge=1.0, le=2.0)

    # ---- LLM 采样参数分流：非本地（OpenAI / 自由模型）档 ----
    # 检测见 is_local_llm_endpoint()：**只有 provider=ollama 算本地**；
    # 本机地址上的网关/代理（如 127.0.0.1:7863）也算非本地，走本组。
    # 本地档 = 上面那四个本地适配值（原样保留，不受本组影响）。
    # 非本地档取值参考主流开源客户端（NextChat / LobeChat / SillyTavern）的云端默认：
    # max_tokens 2048、top_p 0.95、temperature 0.8。
    # repetition_penalty 默认 None = **不发送该字段**（标准 OpenAI 接口不认它，
    # 已有的 1.10 只对 Ollama / vLLM 这类端点有意义）。
    cloud_max_tokens_per_reply: int = Field(2048, ge=1, le=1_000_000)
    cloud_llm_top_p: float = Field(0.95, ge=0.0, le=1.0)
    cloud_llm_repetition_penalty: float | None = None
    cloud_llm_temperature: float = Field(0.8, ge=0.0, le=2.0)

    def llm_profile_for(
        self, provider: str | None = None, base_url: str | None = None
    ) -> LLMProfile:
        """本地/非本地的唯一分流点：按端点返回生效的采样参数。

        - provider=None → 用全局 llm_provider；base_url=None → 用全局 llm_base_url。
        - 本地档完全沿用本地适配参数；非本地档用 cloud_* 那组。
        - 请求级调用（/test、/switch、override）传各自端点即可。
        """
        prov = self.llm_provider if provider is None else provider
        url = self.llm_base_url if base_url is None else base_url
        if is_local_llm_endpoint(prov, url):
            return LLMProfile(
                is_local=True,
                max_tokens=self.max_tokens_per_reply,
                top_p=self.llm_top_p,
                repetition_penalty=self.llm_repetition_penalty,
                temperature=self.llm_temperature,
            )
        return LLMProfile(
            is_local=False,
            max_tokens=self.cloud_max_tokens_per_reply,
            top_p=self.cloud_llm_top_p,
            repetition_penalty=self.cloud_llm_repetition_penalty,
            temperature=self.cloud_llm_temperature,
        )

    def llm_profile(self) -> LLMProfile:
        """全局端点生效参数（= llm_profile_for() 的无参快捷方式）。"""
        return self.llm_profile_for()

    def llm_is_local(self) -> bool:
        """当前全局 LLM 端点是否本地（供前端展示与日志）。"""
        return is_local_llm_endpoint(self.llm_provider, self.llm_base_url)

    # ---- 情感 / Live2D ----
    enable_emotion: bool = True
    enable_live2d: bool = False
    live2d_model_path: str = ""  # model3.json 所在目录（相对或绝对）
    live2d_default_model_id: str = "wmz_314701"

    # ---- 情感检测升级（15 类 + LLM/分类器辅助）----
    # auto = LLM 可用(非mock且api_key非空)时 LLM→classifier→keyword；
    #        LLM 不可用且分类器可用时 classifier→keyword；否则 keyword
    emotion_detector: Literal["keyword", "classifier", "llm", "auto"] = "auto"
    emotion_llm_timeout: float = Field(8.0, gt=0.0)  # LLM 检测调用超时（秒）
    emotion_confidence_threshold: float = Field(0.4, ge=0.0, le=1.0)  # 置信度下限
    emotion_classifier_backend: Literal["hashing", "jina"] = "hashing"  # P1.5 时切 jina
    emotion_jina_model: str = "jina-embeddings-v2-base-zh"

    # ---- RAG ----
    rag_impl: Literal["memory", "chroma"] = "memory"
    chroma_persist_dir: str = "./data/chroma"
    chunk_size: int = Field(600, ge=50, le=20_000)
    # 注入条数：检索在本项目无判别力（实测相关/无关两组原始余弦完全重叠：
    # 0.702 vs 0.695），故用"少注入"代替阈值过滤来降噪。
    top_k: int = Field(2, ge=1, le=100)
    rag_hybrid: bool = True  # 稠密向量 + BM25 稀疏混合重排（提升检索精度）
    # alpha：0=纯 BM25，1=纯向量。角色对话多为口语/改写，语义权重应更高。
    # 行业经验：关键词型 0.3-0.4、语义型 0.7-0.8、均衡 0.5。
    rag_hybrid_alpha: float = Field(0.45, ge=0.0, le=1.0)
    # 混合检索候选池大小：top_k 太小时候选池会被长块"吸引子"占满，
    # 导致真正相关条目（如"暴雨"）漏召。实测 candidate_mult >= 30 才稳定命中，
    # 默认取 30（top_k=2 -> 60 候选，足够覆盖噪声）。
    rag_hybrid_candidates: int = Field(30, ge=1, le=200)

    # ---- 嵌入 / 持久化知识库 ----
    embedder: Literal["ollama", "hashing"] = "ollama"
    embed_model: str = "nomic-embed-text"
    embed_dim: int = Field(768, ge=16, le=32_768)
    ollama_base_url: str = ""  # 留空则用 llm_base_url 或默认 http://localhost:11434
    knowledge_dir: str = "./data/knowledge"  # 知识库（向量+文本）持久化目录
    characters_dir: str = "./data/characters"  # 多角色人设持久化目录

    # ---- 分层记忆（长期 / 短期） ----
    memory_decay_lambda: float = Field(0.05, ge=0.0, le=1.0)
    memory_retention_days: int = Field(60, ge=1, le=3_650)
    longterm_consolidate_every: int = Field(6, ge=1)
    event_extract_enabled: bool = True  # 结构化事实/事件提取（升级方案 C）；关闭则整段合并

    # ---- 用户画像（UserProfile） ----
    profile_enabled: bool = True  # 总开关
    profile_extract_every: int = Field(10, ge=1)
    profile_top_k: int = Field(5, ge=1, le=100)
    profile_max_items: int = Field(200, ge=1, le=100_000)
    profile_llm_timeout: float = Field(8.0, gt=0.0)
    profile_synonym_threshold: float = Field(0.85, ge=0.0, le=1.0)
    profile_reminder_days: int = Field(3, ge=0, le=365)
    profile_namespace: str = "profile"  # 画像命名空间（预留 profile:<uid>）

    # ---- 联网 / Web RAG ----
    enable_web: bool = True
    # duckduckgo=免key DDG（部分网络不可达）；bing=免key Bing（国内可达，推荐）；
    # tavily=需 key 的 Tavily API（最稳）。默认 duckduckgo，运行时自动回退 bing。
    web_provider: Literal["duckduckgo", "bing", "tavily"] = "duckduckgo"
    tavily_api_key: str = ""
    web_max_results: int = Field(5, ge=1, le=50)
    web_fetch_content: bool = True  # 联网时是否抓取页面正文（更准但更慢）

    # ---- 剧情图谱（PlotGraph：GraphRAG 存实际剧情，独立于 lore 向量 RAG） ----
    # 默认关闭：剧情层与 lore 层文件/索引/开关/预算完全隔离，关闭时行为与现状一致。
    plot_graph_enabled: bool = False
    plot_lore_dir: str = "./data/lore"  # 剧情语料源（<dir>/<cid>/视频文案/）
    plot_corpus_dir: str = "./data/knowledge"  # 剧情语料落盘（plot_corpus_<cid>.json）
    plot_graph_dir: str = "./data/knowledge"  # 剧情图谱落盘（plot_graph_<cid>.json）
    plot_cache_dir: str = "./data/knowledge/plot_cache"  # 抽取缓存（按角色分子目录）
    # 单次注入剧情证据块上限（M7：3 → 6）。
    # 为什么上调：`plot_context_max_chars` 才是产品真正的约束——检索只给 3 块时，
    # 注入预算**装不满**（实测平均装入 996.9/1000 字符，恰好卡住）。把检索深度提到
    # 6 让预算有得挑，才有后续「注入预算 1000→2400/3200」的收益（见下）。
    plot_max_chunks: int = Field(6, ge=0, le=20)
    plot_lexical_fallback: int = Field(2, ge=0, le=10)  # 图零命中时的词法兜底条数
    plot_max_edges: int = Field(10, ge=1, le=100)  # 单次参与检索的边上限
    plot_max_hops: int = Field(2, ge=1, le=5)  # 证据边跳距上限
    plot_edge_min_confidence: float = Field(0.6, ge=0.0, le=1.0)
    # 是否启用「孤证」边（evidence < WEAK_EVIDENCE_MIN）。
    # 实测 4302 条边里 4289 条只有 1 条证据（99.7%）——每块独立抽取，同一条边在不同
    # 块里谓语措辞略有差异，几乎无法自然累积到 2 条。默认值 False 会让图谱检索
    # 实际只能用上 13 条边，等于关掉图谱、退化成纯词法兜底。孤证边在检索时已打
    # 0.5 折排序降权，且仍受 plot_edge_min_confidence 约束，故默认改为 True。
    plot_include_weak: bool = True
    # 图谱命中不足 top_chunks 时是否仍用词法兜底补齐（旧行为）。
    # 默认 False：词法兜底只在图谱零命中时启用——BM25 原始分与图谱 PPR 分不同量纲，
    # 补齐会在无关查询上注入大量转写噪声（实测「今天天气怎么样」注入 2 段无关碎片）。
    plot_lexical_topup: bool = False
    # 剧情记忆独立注入预算（M7：1000 → 2400 字符）。
    # 300 题**注入口径**实测（在 build_plot_context 真正装配出的文本上判证据覆盖）：
    #   1000 字符 → 37.3%｜2400 → 49.7%｜3200 → 55.0%
    # 这是本次最高杠杆的一项：预算 1000 时平均装入 996.9 字符，**卡在预算上**，
    # 检索再多也进不去（top 6→8 在 2400 预算下注入结果逐题一致）。
    # 2400 是与 lore 层（3200）拉开差距、又拿到 +12.4pt 的折中；要 55% 请设 3200。
    plot_context_max_chars: int = Field(2400, ge=0, le=20_000)
    plot_link_threshold: float = Field(0.5, ge=0.0, le=1.0)  # 词元实体链接阈值（0.35 实测过松）
    plot_ppr_damping: float = Field(0.85, ge=0.1, le=0.99)
    # PPR 迭代上限：单查询最大单项成本（实测 ~90ms/查询，占检索总耗时 90%+）。
    # **默认 20**：300 题实测 20 与 40 轮**质量完全相同**（strict 45.33% / prec 0.327 /
    # MRR 0.316 三项逐位一致），而 p95 从 298ms 降到 178ms。40 轮时 tol=1e-6 仍未收敛，
    # 多出的 20 轮只改变 1e-5 量级的分数、不影响名次。
    plot_ppr_max_iter: int = Field(20, ge=1, le=500)
    # ---- 剧情检索排序（P2：三通道 RRF 融合）----
    # 三条通道分数量纲互不可比（边证据≈0.2 / 提及≈1.2 / 词法 BM25 30–75），
    # 旧实现直接混排排序，导致图结构证据被提及路稳压、且进不了提示词（组内 0.85 相对门）。
    # RRF 只用名次，天然免疫量纲问题。
    # k 必须取**小值**：k=60（RRF 论文默认）时 1/(60+rank) 几乎不随名次变化，
    # 通道权重会完全压过名次——实测 k=60 时边证据霸占全部名额（路径占比 87%），
    # 严格通过率只有 42%；k=3 时两路真正交错，回到 46%（=旧实现水平）。
    plot_fuse_k: int = Field(3, ge=1, le=1000)
    plot_weight_edge: float = Field(1.0, ge=0.0, le=10.0)  # 边证据（结构化关系路径）
    plot_weight_mention: float = Field(1.0, ge=0.0, le=10.0)  # 实体提及块（属性题）
    plot_weight_lexical: float = Field(0.6, ge=0.0, le=10.0)  # 词法兜底（BM25）
    plot_diversity_per_doc: int = Field(1, ge=0, le=10)  # 同一 doc 的软上限（先按此去冗余）
    plot_mention_cache_size: int = Field(512, ge=16, le=100_000)  # 名字命中表缓存条数
    # 提及块打分口径（300 题消融实测）：
    #   count = Σ 权重×出现次数（旧口径）→ 严格通过 46.0%
    #   idf   = Σ 权重×idf×(1+0.3·ln 次数)（稀有名字加权）→ 42.0%
    # 结论：ASR 语料里"反复提到某角色"的块往往就是该角色的主场戏（答案块），
    # 稀有别名命中多为顺带一提——故默认保留旧口径，idf 仅供换语料时复评。
    plot_mention_scoring: Literal["count", "idf"] = "count"
    # 多实体共现加成：块命中 ≥2 个目标实体时 ×(1+0.5·(k−1))（关系/多跳题的答案特征）
    plot_cooccurrence_bonus: bool = True
    # 提及块是否按**实体分组**输出（种子按 PPR 降序 → 邻居，组内按命中分降序）。
    # 旧实现所有提及块共用同一分数、靠稳定排序自然形成该分组；实测（300 题）改为
    # "全局按分数交错"会让严格通过率掉约 6pt，故默认保持分组序。
    plot_mention_group_by_entity: bool = True
    # ---- 剧情别名可信度分层（P1）----
    # 语料是英文 ASR：2949 个中文正名实体里 1820 个（62%）的中文名零命中，提及召回
    # 只能靠抽取别名；而抽取别名里混着与实体无关的词（实体「牙仙」含 doll/Campbell，
    # 「阿尔卡纳」含 Arkanist=神秘学家）。可信名 = 人工表别名 ∪ 正名 ∪ 其形态相近变体，
    # 其余抽取别名按本倍数降权；每实体另允许 1 条"可疑名补位块"防漏召回。
    plot_alias_trust_ratio: float = Field(0.25, ge=0.0, le=1.0)
    plot_untrusted_extra_per_entity: int = Field(1, ge=0, le=5)
    # ---- 实体查询的提及优先（P2）----
    # 问「X 是谁 / 你还记得 X 吗」时，边证据块信息量最低（它是一个关系事实，不是关于 X 的介绍）。
    # **默认 1.0 = 不启用**：300 题消融实测开启（2.0）会把严格通过率压 0.6pt（45.3%→44.67%），
    # 而真实对话验收 A1 在关闭时同样 7/7（修好对话的是别名可信度分层）。
    # 该档对"实体问题应先把关于实体的块排在前面"确有改善（芭卡洛儿 top-1 从边证据变提及块），
    # 属于质量取向的可选档——开启前请重跑 eval_plot_rag.py 确认可接受。
    plot_weight_mention_entity: float = Field(1.0, ge=0.0, le=10.0)
    plot_entity_query_max_len: int = Field(14, ge=0, le=100)
    # 链式变体（变体的变体）须达到的语料命中块数下限：防 "miss"→"miss campbell"→"campbell"
    # 这类链条把无关人名拖进可信集（实测踩过）；直接变体不受此限。
    plot_alias_trust_chained_min_df: int = Field(3, ge=0, le=1000)
    # 名字显著性打分：可信度 × (1+ln df)，词频取次线性。
    # **默认 False（回滚档）**：300 题消融实测该档把严格通过率从 45.3% 压到 44.3%（−1.0pt），
    # 而修好真实对话问题的是「别名可信度分层」本身（关掉显著性后 A1 仍 7/7）。
    # 保留开关供换语料时复评——不要在没重跑评测的情况下打开。
    plot_name_salience: bool = False
    # ---- 篇章路由（M7）----
    # 用户点名篇章（「洞穴的囚徒篇里海盗船上的歌手是谁」）时，把 BM25 候选池缩到该篇的
    # 文档再排序。这是**唯一**能救这类问题的通道：查询里没有答案实体的名字（分诊实测
    # 188 个缺失证据组里 147 个如此），B 站正文又是英文，中文问法无从匹配；
    # 而篇章名在语料元数据（arc/chapter）与灰机正典层标题里是精确可匹配的。
    plot_chapter_routing: bool = True
    plot_chapter_top: int = Field(3, ge=0, le=50)  # 篇章池内取前 N 块
    plot_chapter_max_names: int = Field(2, ge=1, le=10)  # 一次最多认几个篇章名
    plot_weight_chapter: float = Field(1.0, ge=0.0, le=10.0)
    # M7：词法路常开。正典中文层落库后 BM25 对中文查询不再是噪声（中文问 ↔ 中文正文）。
    # **默认 False**：须以 eval_plot_rag.py 消融确认收益后再开（见审计报告「消融」节）。
    plot_lexical_always: bool = False
    # 提及通道的候选块配额（M7：由硬编码 3/6 改为可配，并上调到 5/10）。
    # 写死 per_entity=3 会让**多跳题的第 4+ 候选块永远进不来**：灰机标准题
    # 「在中央塔里自囚的医生是谁」的答案块（同时含 central tower 与 Aleph）
    # 在种子「高塔」名下正排第 4，白丢一组证据。
    # 300 题消融（同一数据）：3/6 → 严格 51.3% / 注入 50.0% / 灰机 12-14；
    #                        5/10 → 严格 **53.7%** / 注入 **50.3%** / 灰机 **13-14**；
    #                        6/12 / 8/16 → 严格同为 53.7%，注入 50.0% / 50.7%。
    plot_mention_per_entity: int = Field(5, ge=1, le=20)
    plot_mention_total_cap: int = Field(10, ge=1, le=50)
    # ---- 语义检索通道（M8：跨语言层）----
    # 剧情语料是英文 ASR，提问是中文，而本层长期 embedder="none"（零跨语言兜底）。
    # 分诊实测 300 题失败里 111 题 / 126 组是「别名桥缺失」——实体在图里、查询里却没有
    # 它的任何名字（「海盗船上的歌手」「雾中女巫」「自囚的医生」）。补别名救不了，
    # 只有语义能救。索引由 scripts/build_plot_index.py 生成，缺文件/指纹不符即静默停用。
    #
    # ⚠️ **默认 False 的理由是"模型"而不是"效果"**——效果已实测成立：
    #   换成**多语言**嵌入器 bge-m3（1024 维，Q4_K_M）后重建索引：
    #     300 题 严格通过 53.7% → **63.3%（+9.6pt）**、注入口径 50.3% → **58.0%（+7.7pt）**、
    #     MRR 0.337 → **0.386**、块精度 0.312 → **0.328**、离题注入仍为 **0 块**；
    #     代价是检索 p50 129ms → 637ms（查询嵌入约占 430ms）。
    #   而当前全局 `embed_model` 仍是英文单语的 `nomic-embed-text`，
    #   用它开这一层是**净负收益**（−3.7pt）。所以：
    #     - 代码默认 False（不假设机器上装了多语言模型）；
    #     - 部署侧在 `.env` 里显式开：`ROLEPLAY_PLOT_EMBED_MODEL=bge-m3` +
    #       `ROLEPLAY_PLOT_SEMANTIC_ENABLED=true`（本机已如此配置）。
    #   `scripts/build_plot_index.py --crosslingual-check` 会在换模型后先验闸门。
    plot_semantic_enabled: bool = False
    plot_semantic_top: int = Field(5, ge=0, le=50)  # 语义通道取前 N 块
    plot_weight_semantic: float = Field(1.0, ge=0.0, le=10.0)
    # 语义实体链接兜底：**精确名匹配全军覆没时**才启用（种子非空就不抢），
    # 阈值是余弦下限；0 = 关闭该兜底（保守档）。
    plot_semantic_link_min: float = Field(0.0, ge=0.0, le=1.0)
    plot_semantic_link_top: int = Field(3, ge=0, le=20)
    # 语义候选池的**语言限制**（逗号分隔 lang 值，如 "en"；空 = 不限）。
    # 动机：英文单语嵌入器对中文查询会优先匹配"这段也是中文"而不是"这段意思相关"
    # ——真实语料 9021 块里有 1691 块中文，中文块无条件压过英文正确块。
    # 限成 "en" 等于把语言这个维度从打分里消掉，只剩"意思"可比。
    # 默认空（不限）——是否有效须由 300 题消融决定，见审计报告。
    plot_semantic_langs: str = ""
    # 语义块的最低余弦（低于此分不入候选）。与「种子门控」是**两道独立防线**：
    # 门控挡"整句离题"，阈值挡"句内噪声"。默认 0.0 = 只用门控（实测已足够清零负样本）。
    plot_semantic_min_score: float = Field(0.0, ge=0.0, le=1.0)
    # 召回率修复（P1-4）：融合层「保底保留」名额。
    # 诊断（2026-09-17 全量评测 + analyze_recall.py 失分归因）：100/105 失败题的「正解块」
    # 已被语义/篇章通道取回，却被 RRF 融合层挤出最终 top_chunks+lexical_fallback 预算
    # （bucket4_fusion_squeeze）。根因是边证据 + 提及两路从种子实体涌出大量块，把预算占满，
    # 单路命中的语义/篇章正解块被压到名次之外。此处保证语义、篇章两通道各自至少保留 N 块
    # 入选，用最低分图块让位。默认 0 = 关闭（零回归）；线上经 300 题消融确认无回退后再上调。
    plot_min_semantic_kept: int = Field(0, ge=0, le=8)
    plot_min_chapter_kept: int = Field(0, ge=0, le=8)
    # 召回率修复（60 题 never_candidate 专项）：融合后「语义补位重排」。
    # 诊断链（2026-09-17，详见 docs/RAG召回_60题专项与补位重排_20260917.md）：
    #   失败 105 题里 60 题的正解块**从未进入任何通道候选池**；这些正解块 100% 存在
    #   于语义索引（全库排名 p50=54），且 60/60 的块文本含真阳实体名——本该被 mention
    #   通道取到。把 mention 截断放大（5/10 → 20/50）后 19 题的 gold 进了池，
    #   但 strict 只 +1：瓶颈已从「召回面」转到「排序」（RRF 只按名次给分，深池块拿不到分）。
    # 修法：**不做整体重排**（实测全量重排把 inject 从 177 打到 151——余弦偏袒彼此相似
    #   的块，丢掉 RRF 多路命中带来的互补证据），而是保留融合结果前 keep 名，
    #   剩余名额用候选池中余弦最高的块补位。
    #   keep=3：300 题 **+12**，但全新 200 题（独立复核集）**−6** ⇒ 有题集过拟合成分；
    #   keep=5：300 题 **+4**，全新 200 题 **+1**，两份题集均非负 ⇒ **默认值取 5**。
    #   （keep 越大越保守：只补最后几个名额，收益递减、稳健递增。）
    # 默认关：换语料后块排名分布会变，必须由部署侧在目标语料上复跑消融再开。
    plot_rerank_topup_enabled: bool = False
    plot_rerank_topup_keep: int = Field(5, ge=0, le=8)
    # 剧情层专用嵌入模型（空 = 跟随全局 embed_model）。
    # 为什么要能分开：全局 embed_model 还被 lore 向量库使用，而 lore 库的向量是按
    # nomic（768 维）建的——把全局一改成 bge-m3（1024 维）会让 lore 检索整个失配。
    # 分开配置后，只有剧情语义层换模型，互不影响。
    plot_embed_model: str = ""
    # ==== P0 新增七开关（Spec §4 末段锁定；全部默认关 / 默认 None = 现状逐位一致）====
    # P0-1 / C4：弱证豁免来源（逗号分隔的 edge.source 集合）。
    # 证据条数 < WEAK_EVIDENCE_MIN(2) 的边默认不参与传播（防抽取噪声），但**人工事实边**
    # 天然只有 1 条证据——它是人写的、可溯源的，不是噪声。旧口径一视同仁地丢掉它们，
    # 导致图谱重建后手工事实静默消失（R8 红线）。默认 "manual"（Spec 锁定值）。
    # 实测图内还存在早期探针写入的 "manual_probe"，部署侧按需并列：
    #   ROLEPLAY_PLOT_WEAK_EXEMPT_SOURCES=manual,manual_probe
    plot_weak_exempt_sources: str = "manual"
    # P0-4 / D1：node specificity 种子加权（种子归一化前 ×= 1/deg，抑制「洞穴/海盗」
    # 这类与几乎所有实体都相连的泛种子稀释传播质量）。默认关；开否由消融决定。
    plot_ppr_node_specificity: bool = False
    # P0-2 / B3：reranker 安全间隔（本地 bge-reranker-v2-m3 对 查询 × 实体摘要 打分）。
    # 默认关：模型文件缺失/加载失败 -> available=False 静默降级（**不放宽阈值**，护栏不破）。
    plot_semantic_rerank_enabled: bool = False
    plot_semantic_rerank_min: float = Field(0.5, ge=0.0, le=1.0)
    plot_semantic_rerank_top: int = Field(10, ge=0, le=100)
    # P1-1 / A1：块级中文翻译索引通道（物理分离索引 plot_index_zh_<cid>.npz）
    plot_semantic_zh_enabled: bool = False
    # ── 查询侧实体扩展（2026-09-17 实测：inject_pass 62.00%→69.00%，+7.00pt，p<0.0001）──
    # 失分 58.8% 是「查询里没有实体名」，而证据块要匹配的是英文专名。
    # 把识别出的正典实体名拼进查询即可解锁该部分。
    # ⚠️ 三条护栏（见 plot_entity_expand.py）：白名单校验 / 失败即不扩展 / 独立开关。
    # ⚠️ 识别后端必须**懂该作品设定**：本地 qwen2.5:7b 只有 15.0% 命中率，强模型 62.7%。
    plot_entity_expand_enabled: bool = False
    # 后端：static（静态映射，离线回放/成本敏感）| llm（OpenAI 兼容接口）
    plot_entity_expand_backend: Literal["static", "llm"] = "static"
    # static 后端的映射文件路径（JSON：{"map": {"查询原文": [{"name":..., "conf":"high"}]}}）
    plot_entity_expand_static_path: str = ""
    plot_entity_expand_top: int = Field(3, ge=1, le=20)
    # 置信度下限；实测「不设阈值」最优（low 档贡献了总收益的 43%），故默认 0.0
    plot_entity_expand_min_conf: float = Field(0.0, ge=0.0, le=1.0)
    plot_entity_expand_max_append: int = Field(4, ge=1, le=10)
    # 白名单校验：输出必须能解析到图谱的「正名/别名」才允许拼接。
    # 关掉 = 模型说什么就拼什么（**不推荐**，等于放弃防线 1；仅供消融对比）。
    plot_entity_expand_whitelist: bool = True
    # llm 后端参数（为空则复用全局 LLM 配置）
    plot_entity_expand_llm_model: str = ""
    plot_entity_expand_llm_base_url: str = ""
    plot_entity_expand_llm_api_key: str = ""
    # P0-5 / M-11：检索链路结构化埋点落盘（运行期 jsonl 轨道；评测报告内嵌 trace 段默认开）
    plot_trace_enabled: bool = False
    # ---- 剧情检索精度门控（P3：种子卫生）----
    # 词元兜底种子必须被人工别名表锚定：实测 300 题只有 7 题走该路径（种子全是碎片），
    # 而离题问句几乎全靠它蹭上 restaurant / this place 这类实体。
    plot_require_anchored_token_seeds: bool = True
    # 丢弃命中「世界常识泛词」的非锚定种子（天气/经济/故事…），
    # 泛词表见 plot_graph.GENERIC_SEED_NAMES（只收与作品无关的日常词）。
    plot_filter_generic_seeds: bool = True
    # ---- 剧情图谱加载期语义（P4）----
    # 人工别名表冲突时改指人工规范实体（merge），而不是被抽取实体反压（skip）。
    # 仅作用于剧情层；GraphStore 默认仍是 skip，lore 层与既有测试语义不变。
    plot_alias_authoritative: bool = True
    # 并发数：本地 CPU 小模型（7B）实测 8 并发会把单块耗时推过 60s 超时，
    # 默认 4（≈ 单块 20-30s、成功率 >90%）；纯 CPU 机器可 env 调到 2-3。
    plot_extract_concurrency: int = Field(4, ge=1, le=64)
    plot_extract_max_tokens: int = Field(800, ge=64, le=32_768)  # 抽取 JSON 专用（默认 240 会截断）
    plot_extract_timeout: float = Field(60.0, gt=0.0)  # 单块抽取超时（本地 CPU 小模型需放宽）

    # ---- lore 知识图谱（GraphRAG：实体关系子图，独立于剧情层与向量检索） ----
    # 默认关闭（零回归）：关闭 / 图谱文件缺失 / 实体链接零命中 → 静默回退纯向量路径。
    graph_enabled: bool = False
    graph_dir: str = "./data/knowledge"  # graph_<cid>.json 落盘目录
    graph_cache_dir: str = "./data/knowledge/graph_cache"  # 抽取缓存（按角色分子目录）
    graph_max_chunks: int = Field(3, ge=0, le=20)  # 单次注入图谱证据块上限
    graph_max_edges: int = Field(12, ge=1, le=100)  # 单次参与检索的边上限
    graph_max_hops: int = Field(2, ge=1, le=5)  # 证据边跳距上限
    graph_edge_min_confidence: float = Field(0.55, ge=0.0, le=1.0)
    graph_include_weak: bool = False  # lore 层证据较密，孤证边默认不参与
    graph_entity_link_threshold: float = Field(0.82, ge=0.0, le=1.0)  # 实体名向量链接阈值
    graph_ppr_damping: float = Field(0.85, ge=0.1, le=0.99)
    graph_ppr_max_iter: int = Field(50, ge=1, le=500)
    graph_context_max_chars: int = Field(1200, ge=0, le=20_000)  # 关系脉络块独立预算
    graph_extract_batch: int = Field(8, ge=1, le=64)  # 离线抽取并发
    graph_extract_max_tokens: int = Field(800, ge=64, le=32_768)  # 抽取 JSON 专用
    graph_extract_timeout: float = Field(60.0, gt=0.0)  # 单块抽取超时

    # ---- 角色卡 / 对话记忆 ----
    character_card_path: str = ""  # 留空则使用内置默认角色卡（无名者）
    enable_session_memory: bool = True  # 跨轮次/跨会话记住对话
    session_memory_dir: str = "./data/sessions"  # 记忆持久化目录
    prompt_config_path: str = ""  # 全局提示词拼装配置 JSON（留空=默认，输出与改造前一致）

    # ---- 复读抑制（repetition guard，动态负向提示 + 生成后校验） ----
    # 问题：模型会把 mes_example 示范句逐字复现、同一意象连用多轮（用户反馈「复读机」），
    # repetition_penalty（token 级）无法根治整句照抄。
    # 方案（echoproof 思路）：把最近几轮角色说过的话 + 角色卡示例句提取为禁用短语，
    # 注入提示词末尾明令禁止；非流式路径（QQ/POST /chat）生成后命中还会重写重试。
    repetition_guard_enabled: bool = True  # 总开关（关闭后提示词输出与改造前一致）
    repetition_guard_window: int = Field(8, ge=1, le=200)  # 统计最近 N 条 assistant 消息
    repetition_guard_max_phrases: int = Field(8, ge=1, le=50)  # 每轮最多注入的禁用短语数
    repetition_guard_max_retries: int = Field(1, ge=0, le=3)  # 非流式路径重写重试上限

    # ---- 两阶段生成（P2-3，draft + refine） ----
    # 规则重试耗尽仍复读/出戏时，用更低温度按 SELF-CHECK 指令自检重写一次，
    # 精炼稿通过全部校验才采纳。默认关闭（零回归）；开启后仅影响问题回复的延迟。
    refine_enabled: bool = False
    refine_temperature: float = Field(0.3, gt=0.0, lt=1.0)  # 精炼稿用低温稳住格式

    # ---- 安全 / 限流 ----
    max_message_length: int = Field(4000, ge=1, le=100_000)
    # 回复长度硬闸（无 .env 覆盖时的默认值）。
    # 中文按约 1.5 字/token 换算：最坏可接受 = 6 条 × 40 字 = 240 字 ≈ 160 token，
    # 再留 50% 余量 → 240 token（≈360 字）。过长会让模型退回长篇说教/跑题，
    # 是角色扮演自然度的常见杀手。换模型或换语种时需按实际字/token 比重新校准。
    max_tokens_per_reply: int = Field(240, ge=1, le=1_000_000)
    rate_limit_per_minute: int = 60  # <=0 表示关闭限流
    cors_origins: str = "*"  # 允许跨域的前端源（逗号分隔；* 表示全部，生产应收紧）

    # ---- 资料导入边界（防任意文件读 / SSRF）----
    # 允许导入的本地根目录（逗号分隔）；API 层对 path 做 realpath 收敛，越界即拒。
    ingest_allowed_roots: str = "./data/knowledge"
    # 允许 URL 导入的主机白名单（逗号分隔，空=禁止一切 URL 导入）；仅 https。
    allowed_ingest_hosts: str = ""
    # 是否开启联网导入（/web-ingest 与 ingest type=url）；生产默认关。
    enable_url_ingest: bool = False

    # ---- 体验优化（可配置） ----
    enable_dynamic_followups: bool = False  # 由 LLM 动态生成后续追问（默认关闭，用静态兜底）
    enable_history_summary: bool = True  # 对话历史超阈值时自动摘要，避免上下文溢出
    history_summary_threshold: int = Field(40, ge=2, le=10_000)
    # 本地开发默认禁用前端缓存；生产部署可设 false 恢复浏览器缓存（建议配合版本化资源）
    static_no_cache: bool = True

    # ---- 语音（STT / TTS 后端，均为可选回退） ----
    # 默认全部关闭：前端优先用浏览器原生 Web Speech API；
    # 仅当显式开启后，/voice/* 才走后端适配器（faster-whisper / Edge-TTS）。
    stt_backend_enabled: bool = False
    whisper_model: str = "base"  # faster-whisper 模型大小: tiny/base/small/medium/large-v3
    whisper_model_path: str = ""  # 本地模型目录路径（为空则用 faster-whisper 内置下载）
    tts_backend_enabled: bool = False
    edge_tts_default_voice: str = "zh-CN-XiaoxiaoNeural"
    tts_default_format: str = "mp3"
    voice_request_timeout: float = Field(30.0, gt=0.0)  # 语音后端调用超时（秒）

    # ---- QQ 渠道（NapCatQQ / OneBot v11） ----
    # 让一个 QQ 号（建议小号）通过 NapCat 协议端登录，把消息转成 OneBot v11
    # 交给本服务处理，回复再发回 QQ。大脑（人设/RAG/情感/记忆）全部复用。
    qq_enabled: bool = False  # 总开关（默认关，不影响现有功能）
    qq_napcat_ws_url: str = "ws://127.0.0.1:3001"  # NapCat 正向 OneBot v11 WebSocket 地址
    qq_ws_token: str = ""  # OneBot WebSocket 鉴权 token（NapCat 配置一致；空=不鉴权）
    qq_bot_uin: str = ""  # 机器人 QQ 号（空则启动时用 get_login_info 自动获取）
    qq_admin_uin: str = ""  # 管理员 QQ 号（指令权限校验；空=不限制）
    qq_character_id: str = ""  # QQ 上默认扮演的角色 id（空=当前激活角色）
    qq_group_at_only: bool = True  # 群内仅当被 @机器人 时才回复（避免扰群）
    qq_command_prefix: str = "!"  # 指令前缀（!clear / !help / !char）
    qq_allow_from: str = ""  # 私聊白名单 QQ 号（逗号分隔；空=允许所有人）

    # ---- QQ 语音回复（情感命中时以角色原声切片回复；默认全关，零回归） ----
    # 详见 docs/QQ语音回复方案.md。P0 仅原声切片链路；TTS 兜底 / 随机概率 /
    # 文本净化 / 启动自检为 P1，对应配置项随实现一并加入。
    qq_voice_enabled: bool = False  # 总开关（!voice on/off 可按会话覆盖）
    qq_voice_lang: Literal["zh", "en"] = "zh"  # 全局默认配音（!lang zh/en 可按会话覆盖）
    qq_voice_clip_manifest: str = ""  # 切片 manifest 路径；空=自动定位 frontend/assets/voice/wu_ming_zhe/
    # 情感触发阈值。注意 score 口径随检测来源不同（LLM/分类器为置信分，关键词层为
    # 权重累加且单命中仅 0.3~0.5）——keyword 来源的真实命中在 voice_reply 中视为已达标。
    qq_voice_emotion_threshold: float = Field(0.6, ge=0.0, le=1.0)
    qq_voice_cooldown_sec: float = Field(60.0, ge=0.0)  # 同一会话两次语音的最小间隔
    # QQ 语音普通用户上限 60s；切片库实测最长 62.6s，故放宽到 65 兜住全部官方切片
    qq_voice_max_sec: float = Field(65.0, ge=1.0)
    qq_voice_group_enabled: bool = False  # 群聊是否允许自动出声（防扰群，默认关）
    qq_voice_tts_voice_en: str = "en-US-AriaNeural"  # 英文 TTS 音色（P1 兜底链路用，P0 预留）


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """解析并缓存配置单例；测试中调用 get_settings.cache_clear() 重置。"""
    return Settings()
