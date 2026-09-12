"""GraphStore：角色知识图谱（GraphRAG 数据底座）。

设计（docs/GRAPHRAG加强计划书.md §3，决策编号见 §2.3）：
- 纯 JSON 邻接表落盘（graph_<cid>.json），零第三方图依赖（D1）；
- 实体 id 由 canonical 名派生（sha1 确定性），alias_index 冗余落盘供 O(1) 精确链接；
- 边挂 evidence = [{ns, doc_id, hash}]（D3：chunk 文本 sha1 稳定；KB 重建后
  顺序 id 会变，不能作溯源键）；
- 文件头 index_fingerprint 记录 embedder/抽取模型/schema 版本（D6，照搬
  HippoRAG 2 index_manifest），失配时拒绝服务、提示重建；
- remove_by_doc 在文档重导入/删除时增量清理受影响的边与孤儿实体（照搬
  LightRAG「删除自动重建子图」，防图谱与 KnowledgeBase 漂移）。

并发模型：在线检索只读；写入发生在编排器会话锁内（跨会话可能并发），
写路径用 threading.Lock 保护；save() 原子写（tmp + replace，对齐 KnowledgeBase）。
"""
from __future__ import annotations

import hashlib
import json
import logging
import threading
import time
import unicodedata
from pathlib import Path

logger = logging.getLogger(__name__)

# 图 schema 版本：结构调整（字段增删/语义变更）时递增，触发指纹失配提示重建
GRAPH_SCHEMA_VERSION = "v1"

# 图谱文件的已知顶层字段：文件存在但一个都不含 → 不是图谱文件（结构非法）。
# 与 ``save()`` 的 payload 键严格对应，改 save 的落盘结构时必须同步改这里。
GRAPH_FILE_KEYS: tuple[str, ...] = (
    "fingerprint",
    "entities",
    "edges",
    "alias_index",
    "anchored",
)


def norm_name(text: str) -> str:
    """实体名/别名归一：NFKC（全角→半角）+ 小写 + 去首尾空白。"""
    return unicodedata.normalize("NFKC", text or "").strip().lower()


def normalize_entity_type(raw: object) -> str:
    """实体类型归一：``"角色|物品|地点"`` → ``"角色"``；空值 → ``"未分类"``。

    只用于**读取视图**（stats/调试接口）：抽取模型偶发把多个类型拼在一个字段里，
    直接展示会让"类型分布"出现一堆一次性桶。不写回数据文件。
    """
    text = str(raw or "").strip()
    if not text:
        return "未分类"
    first = text.split("|")[0].strip()
    return first or "未分类"


def entity_id(name: str) -> str:
    """canonical 名 → 确定性实体 id（同名必同 id，重建图谱不漂移）。"""
    digest = hashlib.sha1(norm_name(name).encode("utf-8")).hexdigest()[:12]
    return f"e_{digest}"


def chunk_text_hash(text: str) -> str:
    """chunk 文本指纹（证据溯源键，见决策 D3）。"""
    return hashlib.sha1((text or "").encode("utf-8")).hexdigest()[:16]


def build_local_endpoint_map(
    store: "GraphStore", entities: list[dict]
) -> dict[str, str | None]:
    """单个 chunk 的「实体名/别名 → eid」局部映射（关系端点解析用）。

    背景（已修复缺陷）：关系端点若直接查全局 ``_alias_index``，当同一 chunk 内
    两个实体共享别名（如 "Madam Lucy" 与 "Doris" 都收编了「露西」）时，
    关系会被静默挂到**首注册实体**上，产出错误主语的三元组。

    这里按 chunk 局部建映射：同一别名指向多个实体时标记为 ``None``（歧义），
    调用方据此**丢弃**该关系，而不是猜一个——歧义应交给角色卡 entity_aliases
    人工别名表或实体名向量合并去消解。
    """
    mapping: dict[str, str | None] = {}
    for ent in entities or []:
        if not isinstance(ent, dict):
            continue
        eid = store.link_exact(str(ent.get("name") or ""))
        if not eid:
            continue
        names = [str(ent.get("name") or "")] + [
            str(a) for a in (ent.get("aliases") or [])
        ]
        for n in names:
            nn = norm_name(n)
            if not nn:
                continue
            if nn in mapping and mapping[nn] != eid:
                mapping[nn] = None  # 同 chunk 内别名冲突 → 歧义
            else:
                mapping.setdefault(nn, eid)
    return mapping


def resolve_endpoint(
    store: "GraphStore", local: dict[str, str | None], name: str
) -> str | None:
    """关系端点解析：chunk 局部映射优先（歧义返回 None），否则回落全局别名索引。"""
    nn = norm_name(name)
    if nn in local:
        return local[nn]
    return store.link_exact(name)


class GraphStore:
    """单角色知识图谱：实体表 + 有向边表 + 别名索引，JSON 原子落盘。"""

    def __init__(
        self,
        path: str | Path,
        *,
        min_confidence: float = 0.55,
    ) -> None:
        self._path = Path(path)
        self._min_confidence = min_confidence
        self._lock = threading.RLock()
        self._fingerprint: dict = {}
        # eid -> {name, type, aliases, mentions, summary, vec, pending}
        self._entities: dict[str, dict] = {}
        self._edges: list[dict] = []
        # 归一别名/正名 -> eid（运行时 O(1) 精确链接；落盘冗余）
        self._alias_index: dict[str, str] = {}
        # bind_alias_table 显式锚定的实体：即便零度也不被 remove_by_doc 清掉
        self._anchored: set[str] = set()
        # 加载致命错误：文件**存在**但读取/解析失败或结构非法时填入（B5）。
        # 非空时 save() 一律拒绝落盘，避免「损坏文件 → 静默空图 → 覆盖固化」。
        # 文件不存在属正常首次构建：不填 _load_error，save() 照常可写。
        self._load_error: str | None = None
        # 加载时读到的实体数：用于检测「加载时有实体、落盘时却是空图」的异常覆盖
        self._load_entity_count: int = 0
        # bind_alias_table 因别名冲突（已被其他实体占有）被丢弃的条数（观测性）
        self._alias_ambiguous_dropped: int = 0
        # bind_alias_table(on_conflict="merge") 因人工表优先而改指的条数（观测性）
        self._alias_reassigned: int = 0
        # 边索引 (src, dst, relation) -> edge：upsert_edge 合并查找 O(n) → O(1)。
        # 仅运行时维护，**不落盘**（save 的 payload 不含它，_load 后重建）。
        self._edge_idx: dict[tuple[str, str, str], dict] = {}
        # 图内容版本号：任何写操作 +1。检索层据此缓存「过滤后的边表 + PPR 邻接表」，
        # 既避免每查询重扫 5000+ 边，又保证测试里改了图之后立刻看到新结果（不会读到旧缓存）。
        self._revision: int = 0
        self._load()

    # ── 持久化 ──
    def _load(self) -> None:
        """加载图谱文件。

        与旧实现的关键差别：区分「文件不存在」（正常，返回空图且不拦 save）与
        「文件存在但读不了/解析不了/结构非法」（致命，记入 ``_load_error`` 并
        禁止后续 save，宁可不动盘也不把损坏文件固化成空图）。
        """
        self._load_error = None
        self._load_entity_count = 0
        try:
            exists = self._path.exists()
        except OSError as exc:  # noqa: BLE001
            self._load_error = f"路径不可访问：{exc}"
            logger.error("图谱状态检查失败 %s：%s", self._path, exc)
            return
        if not exists:
            return  # 首次构建：空图是预期状态
        try:
            raw_text = self._path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            self._load_error = f"读取失败：{exc}"
            logger.error("图谱读取失败 %s：%s（已拒绝后续落盘）", self._path, exc)
            return
        try:
            raw = json.loads(raw_text)
        except ValueError as exc:
            self._load_error = f"JSON 解析失败：{exc}"
            logger.error(
                "图谱解析失败 %s：%s（文件已损坏，拒绝落盘以防覆盖成空图）",
                self._path,
                exc,
            )
            return
        if not isinstance(raw, dict):
            self._load_error = f"顶层结构非法（期望 object，实际 {type(raw).__name__}）"
            logger.error(
                "图谱结构非法 %s：%s（拒绝落盘以防覆盖成空图）",
                self._path,
                self._load_error,
            )
            return
        # 结构合法性不只查顶层类型：一个合法 JSON object 但**不含任何图谱字段**
        # （如 ``{"foo": 1}``）同样不是图谱文件，写下去会把它覆盖成空图谱。
        # 例外：空 object ``{}`` 是合法空图（首次构建/清空后的正常形态），
        # 误伤它会导致空图永久锁死、图谱再也建不起来。
        if raw and not any(key in raw for key in GRAPH_FILE_KEYS):
            self._load_error = (
                "结构非法（JSON object 但不含任何图谱字段："
                + "/".join(GRAPH_FILE_KEYS)
                + "）"
            )
            logger.error(
                "图谱结构非法 %s：%s（拒绝落盘以防覆盖成空图）",
                self._path,
                self._load_error,
            )
            return
        self._fingerprint = raw.get("fingerprint") or {}
        self._entities = {
            k: v for k, v in (raw.get("entities") or {}).items() if isinstance(v, dict)
        }
        edges = raw.get("edges")
        self._edges = [e for e in edges if isinstance(e, dict)] if isinstance(edges, list) else []
        idx = raw.get("alias_index")
        self._alias_index = {k: v for k, v in idx.items() if isinstance(v, str)} if isinstance(idx, dict) else {}
        anchored = raw.get("anchored")
        self._anchored = set(anchored) if isinstance(anchored, list) else set()
        self._load_entity_count = len(self._entities)
        self._rebuild_edge_index()
        self._revision += 1

    def _rebuild_edge_index(self) -> None:
        """重建边索引（加载后 / 边被删除后调用）。

        合并键 (src, dst, relation) 重复时**保留首个**，与旧实现线性扫描
        「找到第一条即合并」的语义完全一致。
        """
        idx: dict[tuple[str, str, str], dict] = {}
        for e in self._edges:
            if not isinstance(e, dict):
                continue
            key = (
                str(e.get("src") or ""),
                str(e.get("dst") or ""),
                str(e.get("relation") or ""),
            )
            if key in idx:
                continue
            idx[key] = e
        self._edge_idx = idx

    def save(self) -> None:
        """原子写（tmp + os.replace），失败仅告警不抛出（与 KnowledgeBase 同风格）。

        安全网（B5）：加载阶段出现过致命错误，或「加载时有实体、现在却是空图」
        时拒绝落盘——这两种情况写下去都会把好数据/损坏文件固化成空图。
        """
        if self._load_error:
            logger.error(
                "图谱 %s 加载异常，拒绝落盘（防把损坏文件固化成空图）：%s",
                self._path,
                self._load_error,
            )
            return
        if self._load_entity_count > 0 and not self._entities:
            logger.error(
                "图谱 %s 加载时含 %d 个实体，当前内存实体为 0，拒绝落盘"
                "（疑似空图覆盖，请先排查后再手动落盘）",
                self._path,
                self._load_entity_count,
            )
            return
        if not self._path.parent.exists():
            try:
                self._path.parent.mkdir(parents=True, exist_ok=True)
            except OSError as exc:  # noqa: BLE001
                logger.warning("图谱目录创建失败 %s：%s", self._path.parent, exc)
                return
        payload = {
            "fingerprint": self._fingerprint,
            "entities": self._entities,
            "edges": self._edges,
            "alias_index": self._alias_index,
            "anchored": sorted(self._anchored),
        }
        tmp = self._path.with_suffix(".tmp")
        try:
            tmp.write_text(
                json.dumps(payload, ensure_ascii=False), encoding="utf-8"
            )
            tmp.replace(self._path)
        except OSError as exc:  # noqa: BLE001
            logger.warning("图谱落盘失败 %s：%s", self._path, exc)

    def set_fingerprint(
        self, *, embedder: str, embed_dim: int, extract_llm: str
    ) -> None:
        self._fingerprint = {
            "schema": GRAPH_SCHEMA_VERSION,
            "embedder": embedder,
            "embed_dim": int(embed_dim),
            "extract_llm": extract_llm,
            "built_at": time.time(),
        }

    def check_fingerprint(self, embedder_name: str, embed_dim: int) -> bool:
        """运行时指纹校验：schema/嵌入器/维度失配 → False（图谱过期，拒绝服务）。"""
        if not self._fingerprint or not self._entities:
            return True  # 空图谱/旧文件：视为可用（由调用方决定是否构建）
        fp = self._fingerprint
        return (
            fp.get("schema") == GRAPH_SCHEMA_VERSION
            and fp.get("embedder") == embedder_name
            and int(fp.get("embed_dim") or 0) == int(embed_dim)
        )

    @property
    def fingerprint(self) -> dict:
        return dict(self._fingerprint)

    @property
    def load_error(self) -> str | None:
        """加载阶段的致命错误（None=正常；非空时 save() 已被拒绝）。"""
        return self._load_error

    @property
    def alias_ambiguous_dropped(self) -> int:
        """bind_alias_table 因别名已被其他实体占有而丢弃的条数。"""
        return self._alias_ambiguous_dropped

    @property
    def alias_reassigned(self) -> int:
        """bind_alias_table(on_conflict="merge") 把别名从抽取实体改指人工规范实体的条数。"""
        return self._alias_reassigned

    @property
    def revision(self) -> int:
        """图内容版本号（每次写操作自增）：检索层缓存失效键。"""
        return self._revision

    # ── 实体 ──
    def upsert_entities(
        self, items: list[dict], *, pending: bool = False
    ) -> list[str]:
        """批量插入/合并实体。items: [{name, type?, aliases?}]。

        合并规则：canonical 名或别名命中既有实体 → mentions+1 并并集 aliases/type；
        否则新建（新建同样计 1 次提及）。返回涉及的 eid 列表（含既有命中）。
        """
        eids: list[str] = []
        with self._lock:
            for item in items:
                if not isinstance(item, dict):
                    continue
                name = str(item.get("name") or "").strip()
                if not name:
                    continue
                aliases = [
                    str(a).strip()
                    for a in (item.get("aliases") or [])
                    if str(a).strip()
                ]
                etype = str(item.get("type") or "").strip()
                eid, _existed = self._ensure_entity(name, etype, aliases, pending)
                eids.append(eid)
                # 首现实体同样计 1 次（旧实现只在「已存在」分支 +1，导致新实体
                # mentions 恒为 0，link() 的 mentions 并列排序对首现实体失效）
                self._entities[eid]["mentions"] = (
                    int(self._entities[eid].get("mentions") or 0) + 1
                )
        self._revision += 1
        return eids

    def _ensure_entity(
        self, name: str, etype: str, aliases: list[str], pending: bool
    ) -> tuple[str, bool]:
        """按名/别名找既有实体，找到则合并；否则新建。返回 (eid, 是否已存在)。"""
        eid = self._alias_index.get(norm_name(name))
        if eid is not None and eid in self._entities:
            ent = self._entities[eid]
            if etype and not ent.get("type"):
                ent["type"] = etype
            existing_aliases = {norm_name(a) for a in ent.get("aliases", [])}
            for a in aliases:
                na = norm_name(a)
                if not na or na == norm_name(ent["name"]) or na in existing_aliases:
                    continue
                # 别名已被其他实体占有时不抢占（首注册优先；人工别名表
                # bind_alias_table 走独立通道，冲突时告警跳过，语义不变）
                other = self._alias_index.get(na)
                if other is not None and other != eid:
                    continue
                ent.setdefault("aliases", []).append(a)
                self._alias_index[na] = eid
            if pending is False:
                ent["pending"] = False  # lore 侧再命中 → 转正
            return eid, True
        eid = entity_id(name)
        existed = eid in self._entities  # 同名实体 id 确定性：直查兜底
        ent = self._entities.setdefault(
            eid,
            {
                "name": name,
                "type": etype,
                "aliases": [],
                "mentions": 0,
                "summary": "",
                "vec": None,
                "pending": pending,
            },
        )
        if etype and not ent.get("type"):
            ent["type"] = etype
        if pending is False:
            ent["pending"] = False
        self._alias_index[norm_name(name)] = eid
        for a in aliases:
            na = norm_name(a)
            if na and na not in self._alias_index:
                ent.setdefault("aliases", []).append(a)
                self._alias_index[na] = eid
        return eid, existed

    def bind_alias_table(
        self, mapping: dict[str, list[str]], *, on_conflict: str = "skip"
    ) -> int:
        """绑定角色卡 entity_aliases（人工权威别名表，最高归并优先级）。

        为每个 canonical 名确保实体存在（必要时创建，不视为 pending），
        并登记别名 + 锚定（零度不清除）。返回登记的别名条数。

        ``on_conflict``（P4 新增，默认 ``"skip"`` 保持既有语义不变）：
        - ``"skip"``：别名已被其他实体占有时跳过并计数（历史行为，lore 层在用）；
        - ``"merge"``：**人工表最高优先**——把该别名改指人工规范实体（原持有者保留
          其余名字），并计入 ``alias_reassigned``。文档一直宣称人工表是最高优先级的
          归并来源，但旧实现是"首注册优先"，实测生产数据里 4 条冲突全部由抽取出来的
          噪声实体胜出（如 ``Noir`` 压在人工规范名「菲林士多」上），令人工表形同虚设。
        """
        count = 0
        with self._lock:
            for canonical, aliases in (mapping or {}).items():
                name = str(canonical or "").strip()
                if not name:
                    continue
                eid, _ = self._ensure_entity(name, "", [], pending=False)
                self._anchored.add(eid)
                for a in aliases or []:
                    alias = str(a or "").strip()
                    na = norm_name(alias)
                    if not alias or na == norm_name(name):
                        continue
                    other = self._alias_index.get(na)
                    if other is not None and other != eid:
                        if on_conflict != "merge" or other in self._anchored:
                            # 默认语义 / 对方同样被人工表锚定（两条人工条目争同一别名）
                            # → 保持首注册，跳过并计数
                            self._alias_ambiguous_dropped += 1
                            logger.warning(
                                "别名冲突：%s 已指向 %s，忽略对 %s 的绑定", alias, other, name
                            )
                            continue
                        # merge：人工表改指成功，摘掉原持有者的这条别名（其余名字不动）
                        self._detach_alias(other, na)
                        self._alias_reassigned += 1
                        logger.info(
                            "别名改指（人工表优先）：%s 由 %s 改指 %s", alias, other, eid
                        )
                    if na not in self._alias_index:
                        self._entities[eid].setdefault("aliases", []).append(alias)
                        self._alias_index[na] = eid
                        count += 1
        self._revision += 1
        return count

    def _detach_alias(self, eid: str, normalized_alias: str) -> None:
        """把某条归一名从实体 ``eid`` 的别名表与全局索引里摘掉（调用方持锁）。"""
        ent = self._entities.get(eid)
        if ent is not None:
            kept = [
                a for a in (ent.get("aliases") or []) if norm_name(str(a)) != normalized_alias
            ]
            ent["aliases"] = kept
        if self._alias_index.get(normalized_alias) == eid:
            self._alias_index.pop(normalized_alias, None)

    def link_exact(self, mention: str) -> str | None:
        """别名/正名精确链接（归一后 O(1)）。"""
        return self._alias_index.get(norm_name(mention))

    @property
    def anchored_ids(self) -> frozenset[str]:
        """被人工别名表锚定的实体 id 集合（只读视图）。"""
        with self._lock:
            return frozenset(self._anchored)

    def entities(self) -> list[dict]:
        with self._lock:
            return [dict(v, id=k) for k, v in self._entities.items()]

    def get_entity(self, eid: str) -> dict | None:
        with self._lock:
            ent = self._entities.get(eid)
            return dict(ent, id=eid) if ent else None

    def set_entity_vec(self, eid: str, vec: list[float]) -> None:
        with self._lock:
            if eid in self._entities:
                self._entities[eid]["vec"] = vec

    def ensure_entity_vectors(self, embedder, batch: int = 32) -> int:
        """为缺向量的实体批量嵌入实体名（正名，离线/懒加载）。返回嵌入条数。

        embedder：EmbedderPort（同步 embed 接口）。失败返回已完成量（不抛出）。
        """
        todo = [
            eid
            for eid, ent in self._entities.items()
            if not ent.get("vec")
        ]
        done = 0
        for i in range(0, len(todo), max(1, batch)):
            part = todo[i : i + max(1, batch)]
            try:
                vecs = embedder.embed([self._entities[e]["name"] for e in part])
            except Exception as exc:  # noqa: BLE001
                logger.warning("实体向量嵌入失败（%d/%d）：%s", done, len(todo), exc)
                break
            for eid, vec in zip(part, vecs):
                self.set_entity_vec(eid, vec)
                done += 1
        return done

    # ── 边 ──
    def upsert_edge(
        self,
        *,
        src: str,
        dst: str,
        relation: str,
        confidence: float,
        importance: float = 0.7,
        evidence: list[dict] | None = None,
        ts: float | None = None,
        source: str = "lore",
    ) -> bool:
        """插入/合并有向边。同 (src, dst, relation) 边合并：evidence 并集、
        confidence/importance 取 max。低于 min_confidence 拒绝。返回是否写入。"""
        rel = str(relation or "").strip()
        if not src or not dst or not rel or src == dst:
            return False
        try:
            confidence = float(confidence)
        except (TypeError, ValueError):
            confidence = 0.5
        if confidence < self._min_confidence:
            return False
        # 证据去重但**保持插入顺序**：旧实现用 set 去重，集合迭代顺序不定，
        # 导致同一条边在检索时选中的「代表证据块」每次运行都可能不同（不可复现）。
        ev_keys: set[tuple] = set()
        evidence_list: list[dict] = []
        for ev in evidence or []:
            if not isinstance(ev, dict):
                continue
            key = (ev.get("ns"), ev.get("doc_id"), ev.get("hash"))
            if not key[2] or key in ev_keys:
                continue
            ev_keys.add(key)
            evidence_list.append({"ns": key[0], "doc_id": key[1], "hash": key[2]})
        with self._lock:
            key = (src, dst, rel)
            # 合并查找走 _edge_idx（O(1)）；索引缺失时回退线性扫描，语义不变
            found = self._edge_idx.get(key)
            if found is None:
                for e in self._edges:
                    if (
                        e.get("src") == src
                        and e.get("dst") == dst
                        and e.get("relation") == rel
                    ):
                        found = e
                        # 回退命中即回填索引：让索引自愈，后续同键查找回到 O(1)
                        self._edge_idx[key] = e
                        break
            if found is not None:
                e = found
                e["confidence"] = max(e["confidence"], confidence)
                e["importance"] = max(e.get("importance", 0.7), importance)
                existing = {
                    (x.get("ns"), x.get("doc_id"), x.get("hash")) for x in e["evidence"]
                }
                e["evidence"] = e["evidence"] + [
                    x for x in evidence_list if (x["ns"], x["doc_id"], x["hash"]) not in existing
                ]
                e["ts"] = max(e.get("ts", 0.0), ts or time.time())
                self._revision += 1
                return True
            edge = {
                "src": src,
                "dst": dst,
                "relation": rel,
                "confidence": round(confidence, 4),
                "importance": float(importance),
                "evidence": evidence_list,
                "ts": ts or time.time(),
                "source": source,
            }
            self._edges.append(edge)
            self._edge_idx[key] = edge
            self._revision += 1
            return True

    def neighbors(self, eid: str) -> list[tuple[dict, str]]:
        """实体的邻接 (边, 方向)，方向 out=src / in=dst。"""
        with self._lock:
            out = []
            for e in self._edges:
                if e["src"] == eid:
                    out.append((e, "out"))
                elif e["dst"] == eid:
                    out.append((e, "in"))
            return out

    def all_edges(self) -> list[dict]:
        """全部边（只读视图的浅拷贝列表，供 PPR/检索遍历）。"""
        with self._lock:
            return list(self._edges)

    def edges_of(self, eid: str) -> list[dict]:
        """实体全部关联边（按 ts 升序，时间线查询用）。"""
        with self._lock:
            return sorted(
                [e for e in self._edges if e["src"] == eid or e["dst"] == eid],
                key=lambda e: e.get("ts", 0.0),
            )

    def remove_by_doc(self, ns: str, doc_id: str) -> int:
        """文档重导入/删除后增量清理（决策：防图谱与 KB 漂移）。

        - 边的 evidence 全部属于 (ns, doc_id) → 删边；否则仅过滤对应证据条目；
        - 清理后零度的实体删除，除非被别名表锚定（_anchored）或仍有别名索引引用。
        返回删除的边数。
        """
        removed = 0
        with self._lock:
            kept: list[dict] = []
            for e in self._edges:
                ev = e.get("evidence") or []
                if ev and all(
                    x.get("ns") == ns and x.get("doc_id") == doc_id for x in ev
                ):
                    removed += 1
                    continue
                filtered = [x for x in ev if not (x.get("ns") == ns and x.get("doc_id") == doc_id)]
                if len(filtered) != len(ev):
                    e["evidence"] = filtered
                kept.append(e)
            if removed:
                self._edges = kept
                self._rebuild_edge_index()  # 边表被换过，索引必须跟着重建
            # 删除零度实体（保留被别名表锚定的）。
            # 注意：不再用「关联边数」覆盖 mentions——mentions 是抽取提及计数，
            # 两者语义不同，覆盖会让高频实体在 link() 并列排序中掉档。
            degree: dict[str, int] = {}
            for e in self._edges:
                degree[e["src"]] = degree.get(e["src"], 0) + 1
                degree[e["dst"]] = degree.get(e["dst"], 0) + 1
            for eid in list(self._entities):
                if degree.get(eid, 0) > 0 or eid in self._anchored:
                    continue
                self._entities.pop(eid, None)
                for key in [k for k, v in self._alias_index.items() if v == eid]:
                    self._alias_index.pop(key, None)
        self._revision += 1  # 证据可能被过滤（影响孤证门控），故无条件失效缓存
        return removed

    # ── 统计 ──
    def stats(self) -> dict:
        with self._lock:
            by_type: dict[str, int] = {}
            degree: dict[str, int] = {}
            for ent in self._entities.values():
                # 抽取偶发把多个类型用 | 拼在一起（"角色|物品|地点|…"，实测 6 个实体）：
                # 统计视图只取首个类型（**不写回文件**，数据文件保持原样）。
                t = normalize_entity_type(ent.get("type"))
                by_type[t] = by_type.get(t, 0) + 1
            for e in self._edges:
                degree[e["src"]] = degree.get(e["src"], 0) + 1
                degree[e["dst"]] = degree.get(e["dst"], 0) + 1
            top = sorted(degree.items(), key=lambda kv: kv[1], reverse=True)[:10]
            conv = sum(1 for e in self._edges if e.get("source") == "conversation")
            zero_degree = sum(1 for eid in self._entities if degree.get(eid, 0) == 0)
            return {
                "entities": len(self._entities),
                "edges": len(self._edges),
                "edges_lore": len(self._edges) - conv,
                "edges_conversation": conv,
                # 零度实体（无任何边）：只可能走"提及 grep"，占真实图谱 41.2%（2809/6814），
                # 是数据面后续重建的裁剪对象——这里只做观测，检索层由种子门控兜住。
                "zero_degree_entities": zero_degree,
                "alias_ambiguous_dropped": self._alias_ambiguous_dropped,
                "alias_reassigned": self._alias_reassigned,
                "by_type": by_type,
                "top_degree": [
                    {
                        "name": self._entities[eid].get("name", eid),
                        "degree": d,
                    }
                    for eid, d in top
                    if eid in self._entities
                ],
                "fingerprint": dict(self._fingerprint),
            }


class GraphRegistry:
    """按角色的图谱懒加载注册表（在线检索入口）。

    - 文件缺失 → get() 返回 None（图谱未构建，静默跳过图谱路）；
    - 指纹失配 → 返回 None 并告警一次（stale，提示重建）；peek() 可查详情；
    - mtime 变化 → 自动重载（build_graph 重建后无需重启服务）。
    """

    def __init__(
        self,
        directory: str | Path,
        *,
        min_confidence: float = 0.55,
        embedder_name: str = "",
        embed_dim: int = 0,
    ) -> None:
        self._dir = Path(directory)
        self._min_confidence = min_confidence
        self._embedder_name = embedder_name
        self._embed_dim = embed_dim
        self._cache: dict[str, tuple[float, GraphStore]] = {}
        self._stale_warned: set[str] = set()

    def path_for(self, character_id: str | None) -> Path:
        cid = (character_id or "").strip() or "default"
        # 角色 id 已在 SessionMemory 等处做清洗，这里仅防路径分隔符
        safe = cid.replace("/", "_").replace("\\", "_")
        return self._dir / f"graph_{safe}.json"

    def get(self, character_id: str | None) -> GraphStore | None:
        path = self.path_for(character_id)
        try:
            mtime = path.stat().st_mtime
        except OSError:
            self._cache.pop(path.name, None)
            return None
        cached = self._cache.get(path.name)
        if cached is not None and cached[0] == mtime:
            return cached[1]
        store = GraphStore(path, min_confidence=self._min_confidence)
        if not store.check_fingerprint(self._embedder_name, self._embed_dim):
            key = path.name
            if key not in self._stale_warned:
                self._stale_warned.add(key)
                logger.warning(
                    "图谱 %s 指纹失配（embedder/schema 变更），已跳过图谱检索；"
                    "请运行 scripts/build_graph.py --rebuild 重建",
                    path.name,
                )
            return None
        self._cache[path.name] = (mtime, store)
        return store

    def peek(self, character_id: str | None) -> dict:
        """状态探查（调试 API 用）：存在性 / 是否过期 / 统计。"""
        path = self.path_for(character_id)
        if not path.exists():
            return {"exists": False, "stale": False, "stats": {}, "path": str(path)}
        store = GraphStore(path, min_confidence=self._min_confidence)
        stale = not store.check_fingerprint(self._embedder_name, self._embed_dim)
        return {
            "exists": True,
            "stale": stale,
            "stats": store.stats(),
            "path": str(path),
        }
