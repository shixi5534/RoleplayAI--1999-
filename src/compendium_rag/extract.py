# -*- coding: utf-8 -*-
"""云端 LLM 实体/关系抽取（含内容哈希幂等缓存）。

提示词设计依据（``tmp_probe/scan_format.py`` 全量扫描结论）：
- 对话已带 ``**说话人**：`` 归属 → 提示词明确要求「以说话人为准」，
  避免模型把旁白里的主语误判成说话人；
- 泛称说话人（市民观众Ⅰ/众人/？？？）共 1,685 个说话人中的长尾 →
  提示词显式排除，另在归一化层再兜底一次；
- 实体类型收敛为 6 类受控词表，便于图谱聚合与类型化检索。
"""
from __future__ import annotations

import hashlib
import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

from .chunker import Chunk
from .corpus import is_generic_speaker
from .llm import CloudLLM
from .relation_norm import map_relation

logger = logging.getLogger(__name__)

ENTITY_TYPES = ("角色", "组织", "地点", "物品", "概念", "事件")

SYSTEM_PROMPT = """你是《重返未来：1999》官方剧情文本的结构化知识抽取器。

你的唯一任务：从给定的剧情片段中抽取**实体**与**实体间关系**，输出严格 JSON。

## 硬性规则
1. 只输出 JSON 对象本身，不要 markdown 围栏、不要解释、不要思考过程。
2. 实体类型**必须**是以下六者之一：角色 / 组织 / 地点 / 物品 / 概念 / 事件。
3. 实体名必须**忠于原文**，不要翻译、不要改写、不要补全你不确定的姓氏。
   同一个人若原文出现全名与简称，用**出现次数最多或最正式**的形式作 name，
   其余形式放进 aliases。
4. 关系必须能在原文中找到直接依据；不确定就不要抽。
   禁止基于你的先验知识补充原文没有写的关系。
5. relation 用 2~6 个汉字的动词/关系短语（如 杀死 / 加入 / 隶属于 / 憎恨 / 持有 / 位于）。
6. 不要抽取泛称与无名指代：众人、人们、路人、士兵、市民观众、？？？、
   旁白、系统，以及"那个男人"这类无确定所指的表述。
7. evidence 必须是原文中的**短句片段**（不超过 40 字），用于人工溯源核验。
8. confidence 为 0~1 浮点数，表示该关系在原文中的确定程度。

## 精确性优先（重要：宁缺毋滥）
本图谱用于精确检索，**错误的节点比缺失的节点危害大得多**。因此：

9. **实体名必须是「名字」**，不能是描述性短语或一整句话。
   ✗ 错误：「高个子」「被捆绑住的女孩」「笃信"万物皆数"的小岛」「那个持枪的男人」
   ✓ 正确：有专名的人/地/物才抽；上述无名指代直接**跳过**。
   判断标准：这个名字在原文里能否脱离本句独立指认同一个对象？
   不能，就不要抽。

10. **「事件」类型只收有专名的重大事件**（如 暴雨 / 决斗 / 船商贸易节 / 圣火纪行）。
    ✗ 错误：「J收起博伊刀」「玛蒂尔达夸奖J」「幻象飘散而去」
    —— 这些是**句子的复述**，不是事件实体，一律不要抽。
    如果一句话只是描述某个动作，请用 **relations** 表达（如 J —收起→ 博伊刀），
    不要为它凭空造一个事件实体。

11. **关系端点必须是规则 9 认可的实体名**，不能是描述性短语。

12. 同一实体在 entities 里只出现一次；不要把别名重复列为独立实体。

## 输出格式
{"entities":[{"name":"","type":"","aliases":[],"desc":"不超过 30 字的一句话说明"}],
 "relations":[{"src":"","relation":"","dst":"","evidence":"","confidence":0.9}]}

注意：
- entities 中出现的 name 才可作为 relations 的 src/dst。
- 若片段中没有可抽取内容，返回 {"entities":[],"relations":[]}。
"""


@dataclass
class ExtractedEntity:
    name: str
    type: str
    aliases: list[str] = field(default_factory=list)
    desc: str = ""


@dataclass
class ExtractedRelation:
    src: str
    relation: str
    dst: str
    evidence: str = ""
    confidence: float = 0.0


@dataclass
class Extraction:
    entities: list[ExtractedEntity] = field(default_factory=list)
    relations: list[ExtractedRelation] = field(default_factory=list)
    ok: bool = True
    error: str = ""
    attempts: int = 1

    def to_dict(self) -> dict:
        return {
            "entities": [{"name": e.name, "type": e.type, "aliases": e.aliases,
                          "desc": e.desc} for e in self.entities],
            "relations": [{"src": r.src, "relation": r.relation, "dst": r.dst,
                           "evidence": r.evidence, "confidence": r.confidence}
                          for r in self.relations],
            "ok": self.ok, "error": self.error, "attempts": self.attempts,
        }

    @staticmethod
    def from_dict(d: dict) -> "Extraction":
        return Extraction(
            entities=[ExtractedEntity(e.get("name", ""), e.get("type", ""),
                                      list(e.get("aliases") or []), e.get("desc", ""))
                      for e in (d.get("entities") or [])],
            relations=[ExtractedRelation(r.get("src", ""), r.get("relation", ""),
                                         r.get("dst", ""), r.get("evidence", ""),
                                         float(r.get("confidence") or 0.0))
                       for r in (d.get("relations") or [])],
            ok=bool(d.get("ok", True)), error=d.get("error", ""),
            attempts=int(d.get("attempts", 1)),
        )


def build_user_prompt(chunk: Chunk) -> str:
    """构造片段上下文 + 正文。上下文帮助模型消解代词与场景。"""
    ctx = [
        f"篇目：《{chunk.chapter_title}》（分类：{chunk.category}）",
    ]
    if chunk.part_title:
        ctx.append(f"章节：{chunk.part_title}")
    if chunk.scene_title:
        ctx.append(f"场景：{chunk.scene_title}")
    if chunk.speakers:
        ctx.append("本片段出现的说话人：" + "、".join(chunk.speakers[:20]))
    return ("【剧情片段】\n" + "\n".join(ctx) + "\n\n---\n" + chunk.text +
            "\n---\n\n请抽取实体与关系，输出 JSON。")


# ── 归一化 ──

RE_WS = re.compile(r"\s+")

# 描述性伪实体（不是「名字」而是短语）——实测由部分模型大量产出。
# 例：高个子 / 被捆绑住的女孩 / 笃信“万物皆数”的小岛 / 那个持枪的男人
RE_DESC_PREFIX = re.compile(
    r"^(?:那个|这个|那些|这些|一位|一名|一个|几个|其他|其它|另一|某个|某位|"
    r"被捆绑|被\S{1,4}住的)")
RE_DESC_SUFFIX = re.compile(
    r"(?:的男人|的女人|的女孩|的男孩|的人|的家伙|的少年|的少女|的老头|的女士|"
    r"的先生|的男人|的人群|的士兵)$")
# 纯粹的泛称人物名词（整名就是它时才算，不做子串匹配——避免误伤真名）
GENERIC_PERSON_NOUNS = frozenset({
    "高个子", "矮个子", "胖子", "瘦子", "老头", "老人", "老者", "少年", "少女",
    "男人", "女人", "男子", "女子", "家伙", "大汉", "壮汉", "青年", "孩子",
    "女孩", "男孩", "女孩们", "男孩们", "观众", "听众", "人群", "众人",
    "陌生人", "黑衣人", "白衣人", "面具人", "身影", "声音", "对方", "双方",
})
# 句复述型「事件」：含标点或过长，说明是句子而非专名
RE_SENTENCE_LIKE = re.compile(r"[，。！？—…；,\.!\?]")
# 句中虚词/体标记：出现即说明这是句子而非专名
RE_SENTENCE_PARTICLE = re.compile(r"[而了着过被将把]|正在|已经|然后|接着|开始|起来")
# 动作动词词表（用于识别「<主语><动词><宾语>」型句复述）。
# 这是从实测抽取结果里归纳的高频动作动词——真正的**事件专名**
# （暴雨 / 决斗 / 船商贸易节 / 圣火纪行 / 公开审讯）不含这些动词，
# 而模型产生的句子复述（J收起博伊刀 / 玛蒂尔达夸奖J / 杰洛击打J肚子）
# 必然命中其一。判据要求动词**两侧都有内容**，避免误伤以动词开头的专名。
ACTION_VERBS = (
    "收起", "夸奖", "击打", "攻击", "殴打", "袭击", "杀死", "杀死", "击败",
    "划伤", "流血", "涂抹", "抓住", "绑架", "捆绑", "救出", "拯救", "阻止",
    "离开", "加入", "背叛", "欺骗", "告知", "询问", "回答", "提及", "看到",
    "听见", "发现", "获得", "失去", "使用", "破坏", "驾驶", "主持", "指挥",
    "率领", "跟随", "围攻", "围拢", "持枪", "走出", "出现", "消失", "死亡",
    "牺牲", "复活", "变身", "解除", "解开", "完成", "开始", "结束",
)
RE_ACTION = re.compile("|".join(ACTION_VERBS))
# 任何类型的实体名长度上限（实测真实专名远短于此；超长必为句子）
MAX_NAME_CHARS = 16


def is_noise_name(name: str, etype: str,
                  known_persons: set[str] | None = None) -> bool:
    """描述性短语 / 句子复述，不是可图谱化的「名字」。

    这是提示词规则 9~10 的**第二道防线**：提示词已要求模型不要产出这些，
    但实测不同模型遵从度差异很大（hunyuan 会产出 30 个实体里近半是这类噪声，
    kimi 基本不产出）。归一化层再兜一次，保证无论用哪个模型建图，
    进图的节点都是「名字」而不是短语。

    ``known_persons``：本次抽取已确认的**角色**名集合。用于识别
    「<人物><动词><宾语>」型句复述（如 ``J收起博伊刀`` / ``玛蒂尔达夸奖J``）——
    这类串没有标点也没有虚词，只能靠"以人物名开头且还有后续内容"来判定。
    刻意只对**角色**前缀生效：``新纪元集市·祭坛`` 以地点名 ``新纪元集市``
    开头，是合法的复合地名，不应被误删。
    """
    n = (name or "").strip()
    if not n:
        return True
    # 绝对长度上限：真实专名远短于此，超长必为句子
    if len(n) > MAX_NAME_CHARS:
        return True
    # 描述性前缀/后缀
    if RE_DESC_PREFIX.match(n) or RE_DESC_SUFFIX.search(n):
        return True
    # 纯泛称人物名词
    if n in GENERIC_PERSON_NOUNS:
        return True
    if etype == "事件":
        # 句子复述：含标点、含虚词体标记、或过长
        if (RE_SENTENCE_LIKE.search(n) or len(n) > 12
                or RE_SENTENCE_PARTICLE.search(n)):
            return True
        # `<人物名><动词…>`：以已确认角色名开头且后面还有内容 → 动作复述
        if known_persons:
            for p in known_persons:
                if len(p) < 1 or len(p) >= len(n):
                    continue
                if n.startswith(p):
                    return True
        # `<主语><动作动词><宾语>`：动词两侧都有内容 → 句子而非专名
        for m in RE_ACTION.finditer(n):
            if m.start() > 0 and m.end() < len(n):
                return True
    return False


def _norm_name(name: str) -> str:
    n = RE_WS.sub("", (name or "").strip())
    n = n.strip("　 \t\"'“”「」『』【】()（）[]")
    return n


def _norm_type(t: str) -> str:
    t = (t or "").strip()
    for known in ENTITY_TYPES:
        if known in t:
            return known
    # 常见同义映射
    alias = {"人物": "角色", "人名": "角色", "角色名": "角色", "家族": "组织",
             "势力": "组织", "团体": "组织", "机构": "组织", "国家": "组织",
             "地名": "地点", "场所": "地点", "区域": "地点",
             "道具": "物品", "物件": "物品", "武器": "物品",
             "能力": "概念", "术语": "概念", "设定": "概念", "现象": "概念",
             "剧情": "事件", "事件名": "事件"}
    for k, v in alias.items():
        if k in t:
            return v
    return "概念"


def normalize(chunk: Chunk, raw: dict, *, map_relations: bool = True) -> Extraction:
    """把模型原始输出归一化成受控词表 + 去噪 + 关系端点合法性校验。

    ``map_relations=False`` 只给审计脚本用（量「谓语受控化前后」的对照），
    生产链路一律走 True。
    """
    names: dict[str, str] = {}     # 归一化名 -> 首次出现形式
    alias_map: dict[str, set[str]] = {}
    types: dict[str, str] = {}
    descs: dict[str, str] = {}
    speaker_set = {s for s in chunk.speakers if s and not is_generic_speaker(s)}

    # ── 第一遍：先收集全部「角色」名 ──
    # 事件名的句复述判据需要知道哪些名字是人物（见 is_noise_name 的 known_persons），
    # 因此必须先扫一遍角色，再回头过滤事件，否则单次遍历无法判定 `J收起博伊刀`。
    known_persons: set[str] = set(speaker_set)
    for e in (raw.get("entities") or []):
        if not isinstance(e, dict):
            continue
        n = _norm_name(e.get("name", ""))
        if n and _norm_type(e.get("type", "")) == "角色":
            known_persons.add(n)

    for e in (raw.get("entities") or []):
        if not isinstance(e, dict):
            continue
        name = _norm_name(e.get("name", ""))
        if not name or len(name) > MAX_NAME_CHARS:
            continue
        if is_generic_speaker(name):
            continue
        typ = _norm_type(e.get("type", ""))
        if is_noise_name(name, typ, known_persons):
            continue
        names.setdefault(name, name)
        types[name] = typ
        if e.get("desc"):
            descs[name] = str(e["desc"]).strip()[:60]
        for a in (e.get("aliases") or []):
            an = _norm_name(str(a))
            if (an and an != name and not is_generic_speaker(an)
                    and not is_noise_name(an, typ) and len(an) <= MAX_NAME_CHARS):
                alias_map.setdefault(name, set()).add(an)

    entities = [ExtractedEntity(n, types[n], sorted(alias_map.get(n, ())),
                                descs.get(n, "")) for n in names]

    # 关系端点必须能在 entities 中解析（精确名 / 别名 / 说话人）
    lookup: dict[str, str] = {}
    for n in names:
        lookup[n] = n
        for a in alias_map.get(n, ()):
            lookup.setdefault(a, n)

    rels: list[ExtractedRelation] = []
    seen_rel: set[tuple[str, str, str]] = set()
    for r in (raw.get("relations") or []):
        if not isinstance(r, dict):
            continue
        s = _norm_name(r.get("src", ""))
        d = _norm_name(r.get("dst", ""))
        rel = _norm_name(r.get("relation", ""))[:12]
        if not s or not d or not rel or s == d:
            continue
        s = lookup.get(s, s)
        d = lookup.get(d, d)
        if s not in names and s not in speaker_set:
            continue
        if d not in names and d not in speaker_set:
            continue
        if is_generic_speaker(s) or is_generic_speaker(d):
            continue
        # 端点未在 entities 里声明但来自可靠说话人 → 补一个实体，保证边可解析
        # （补入的也必须是「名字」形态，否则丢弃该边）
        skip = False
        for x in (s, d):
            if x not in names:
                if is_noise_name(x, "角色", known_persons):
                    skip = True
                    break
                names[x] = x
                types[x] = "角色"
                entities.append(ExtractedEntity(x, "角色", [], ""))
                lookup[x] = x
        if skip:
            continue
        if map_relations:
            # 谓语受控化：同义合并后同一条边可能重复出现，所以映射必须在
            # 下面的三元组去重**之前**，否则合并的收益会被 per-chunk 去重吃掉。
            m = map_relation(s, rel, d)
            if not m.relation:
                continue          # 否定式 / 黑名单：谓语本身不成立，边不留
            s, rel, d = m.src, m.relation, m.dst
        key = (s, rel, d)
        if key in seen_rel:
            continue
        seen_rel.add(key)
        try:
            conf = float(r.get("confidence") or 0.0)
        except (TypeError, ValueError):
            conf = 0.0
        rels.append(ExtractedRelation(s, rel, d,
                                      str(r.get("evidence") or "").strip()[:80],
                                      max(0.0, min(1.0, conf))))
    return Extraction(entities=entities, relations=rels)


# ── 缓存 ──

# 归一化逻辑版本。与 PROMPT_VERSION 分开：提示词变了必须重新问模型，
# 而归一化（去噪/词表映射/端点校验）只是**本地后处理**——缓存里存的是模型
# 原始输出，改归一化只要重跑本地代码即可，**无需再花云端调用**。
#   n1 = 去噪 + 端点校验（v8 冻结图谱）
#   n2 = 叠加谓语受控化（vendor 词表 + 归组 sidecar + 方向裁决表）
NORMALIZER_VERSION = "n2"


def cache_key(chunk: Chunk, model: str, prompt_version: str) -> str:
    """缓存键只依赖「会改变模型输出」的要素（内容+模型+提示词），
    不含归一化版本——这正是改归一化能免费生效的原因。"""
    h = hashlib.sha256()
    h.update(chunk.content_key.encode("utf-8"))
    h.update(model.encode("utf-8"))
    h.update(prompt_version.encode("utf-8"))
    return h.hexdigest()[:24]


PROMPT_VERSION = ("v3"   # v1 裸数组塌缩(12实体→0)；v2 分块合并；
                 # v3 精确性优先（禁描述性伪实体/句复述事件）+ 归一化噪声兜底
                 )


class ExtractionCache:
    """内容哈希缓存：**存模型原始输出**，读取时才归一化。

    设计理由（实测教训）：早期版本把归一化后的结果直接落盘，于是
    调整 ``is_noise_name`` / 词表映射后，缓存里全是按旧规则归一化的数据，
    必须整库重跑云端抽取——既昂贵又容易产生"新旧规则混用"的脏数据。
    改存原始输出后，归一化是纯本地后处理，迭代去噪规则零成本。
    """

    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self.hits = 0
        self.misses = 0

    def _path(self, key: str) -> Path:
        return self.root / key[:2] / f"{key}.json"

    def get_raw(self, key: str) -> dict | None:
        p = self._path(key)
        if not p.exists():
            self.misses += 1
            return None
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            self.misses += 1
            return None
        if not isinstance(d, dict):
            self.misses += 1
            return None
        # 兼容旧格式（{"entities":…} 直接落盘的归一化结果）：视为不可用，
        # 让它重抽一次，避免新旧规则混用。
        if d.get("__cache_format__") != "raw":
            self.misses += 1
            return None
        raw = d.get("raw")
        self.hits += 1
        return raw if isinstance(raw, dict) else {}

    def put_raw(self, key: str, raw: dict) -> None:
        p = self._path(key)
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(".tmp")
        tmp.write_text(json.dumps(
            {"__cache_format__": "raw", "normalizer": NORMALIZER_VERSION,
             "prompt_version": PROMPT_VERSION, "raw": raw},
            ensure_ascii=False), encoding="utf-8")
        tmp.replace(p)

    # 兼容旧调用名（内部仍存 raw）
    def get(self, key: str) -> Extraction | None:
        raw = self.get_raw(key)
        if raw is None:
            return None
        return Extraction.from_dict(raw) if "ok" in raw else None

    def put(self, key: str, ex: Extraction) -> None:
        self.put_raw(key, ex.to_dict())


def normalize_cached(chunk: Chunk, raw: dict) -> Extraction:
    """对缓存中的原始输出做**当前版本**的归一化。"""
    ex = normalize(chunk, raw)
    return ex


async def extract_chunk_raw(llm: CloudLLM, chunk: Chunk) -> tuple[dict | None, str]:
    """单块抽取，返回 (模型原始输出, 错误)。"""
    user = build_user_prompt(chunk)
    try:
        raw, meta = await llm.complete_json(SYSTEM_PROMPT, user)
    except Exception as exc:  # noqa: BLE001
        logger.warning("抽取失败 %s: %s", chunk.chunk_id, exc)
        return None, str(exc)[:200]
    return raw, ""


async def extract_chunk(llm: CloudLLM, chunk: Chunk) -> Extraction:
    """单块抽取并归一化（便捷入口，不落缓存）。"""
    raw, err = await extract_chunk_raw(llm, chunk)
    if raw is None:
        return Extraction(ok=False, error=err)
    return normalize(chunk, raw)
