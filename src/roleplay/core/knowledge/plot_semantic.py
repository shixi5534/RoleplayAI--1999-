# -*- coding: utf-8 -*-
"""剧情语料的**语义向量检索通道**（跨语言检索层）。

要解决的问题（分诊实测）
    剧情语料是**英文 B 站 ASR**（7964/9021 块），用户提问是**中文**，而剧情图谱的
    ``fingerprint.embedder`` 一直是 ``none``：**没有任何跨语言兜底**。
    300 题失败里 **111 题 / 126 个缺失证据组是「别名桥缺失」**——实体在图里，
    但查询里根本没出现它的任何名字（「海盗船上的歌手是谁」「雾中女巫」「自囚的医生」）。
    这类问题**补别名解决不了**：查询与语料之间缺的是"意思"，不是"名字"。
    实测（英文内对照）证明语义检索正是对症的：同一批候选句，
    英文问句对正确答案 cos=0.73–0.89，对干扰项 0.40–0.53，区分度很大。

三条硬约束（都是本项目踩过的坑）
    1. **指纹校验优先于可用性**：索引文件头记录 ``{schema, embedder, dim, corpus_sha}``，
       任一项与当前不符即判过期并**静默停用**——拿旧向量配新模型会静默产出垃圾结果，
       比"没有这一层"危险得多（照搬 HippoRAG 的 index_manifest 思想）。
    2. **整层可回滚**：向量与语料物理分离（``plot_index_<cid>.npz``），
       删掉文件即回到纯词法/图结构世界，其余行为逐字节不变。
    3. **失败必须降级**：任何异常（文件损坏、维度不符、嵌入服务不可用）
       都只告警并跳过该通道，绝不抛出到对话主链路。
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)

INDEX_SCHEMA = "plot-index-v1"


class SemanticIndex:
    """剧情语料向量索引：加载 + 指纹校验 + 点积检索（向量已 L2 归一化）。"""

    def __init__(
        self,
        npz_path: str | Path,
        meta_path: str | Path,
        *,
        embedder=None,
    ) -> None:
        self._npz = Path(npz_path)
        self._meta_path = Path(meta_path)
        self.embedder = embedder
        self.vectors: np.ndarray | None = None
        self.hashes: np.ndarray | None = None
        self.ent_vectors: np.ndarray | None = None
        self.ent_ids: np.ndarray | None = None
        self.meta: dict = {}
        self.disabled_reason: str = "未加载"
        # 可选的候选行掩码（M8 实验）：把语义检索限制在**单一语言**的块上。
        # 动机：英文单语嵌入器（nomic）对中文查询会优先匹配"这段也是中文"而不是
        # "这段意思相关"——中文块无条件压过英文正确块（探针实测 0.51–0.63 vs 0.46–0.53）。
        # 把候选池限成英文块，语言维度就被消掉了，只剩下"意思"可比。
        self._mask: np.ndarray | None = None

    # —— 加载 ——
    def load(self) -> bool:
        try:
            self.meta = json.loads(self._meta_path.read_text(encoding="utf-8"))
            with np.load(self._npz, allow_pickle=False) as z:
                self.vectors = z["vectors"]
                self.hashes = z["hashes"]
                if "ent_vectors" in z.files:
                    self.ent_vectors = z["ent_vectors"]
                    self.ent_ids = z["ent_ids"]
        except Exception as exc:  # noqa: BLE001 - 索引坏了不能影响对话
            self.vectors = None
            self.disabled_reason = f"索引读取失败：{exc}"
            return False
        return True

    def check_fresh(self, *, embedder_name: str, dim: int, corpus_sha16: str) -> tuple[bool, str]:
        """四项全对才算可用（见模块 docstring 的约束 1）。"""
        m = self.meta or {}
        if not m:
            return False, "索引元数据缺失"
        if m.get("schema") != INDEX_SCHEMA:
            return False, f"schema 不符（{m.get('schema')}）"
        if m.get("embedder") != embedder_name:
            return False, f"嵌入模型不符（索引 {m.get('embedder')} ≠ 当前 {embedder_name}）"
        if int(m.get("dim") or 0) != int(dim):
            return False, f"维度不符（{m.get('dim')} ≠ {dim}）"
        if m.get("corpus_sha16") != corpus_sha16:
            return False, "语料指纹不符（语料已变，需重建索引）"
        return True, "ok"

    # —— 检索 ——
    def set_row_mask(self, keep: np.ndarray | None) -> None:
        """限制参与语义检索的行（bool 掩码，长度须与向量行数一致）。"""
        if keep is None or self.hashes is None or len(keep) != len(self.hashes):
            self._mask = None
            return
        self._mask = np.asarray(keep, dtype=bool)

    def search(self, query_vec: np.ndarray, top_k: int = 5) -> list[tuple[str, float]]:
        """查询向量 → ``[(chunk_hash, cosine)]``（向量已归一化，点积即余弦）。"""
        if self.vectors is None or self.hashes is None or not len(self.hashes):
            return []
        qv = np.asarray(query_vec, dtype=np.float32)
        if qv.shape[-1] != self.vectors.shape[1]:
            return []
        n = qv / (np.linalg.norm(qv) or 1.0)
        if self._mask is not None:
            rows = np.flatnonzero(self._mask)
            if not len(rows):
                return []
            sims = self.vectors[rows] @ n
            order = np.argsort(-sims)[: max(1, min(int(top_k), len(sims)))]
            return [(str(self.hashes[rows[i]]), float(sims[i])) for i in order]
        sims = self.vectors @ n
        k = max(1, min(int(top_k), len(sims)))
        idx = np.argpartition(-sims, k - 1)[:k]
        idx = idx[np.argsort(-sims[idx])]
        return [(str(self.hashes[i]), float(sims[i])) for i in idx]

    def search_entities(self, query_vec: np.ndarray, top_k: int = 5) -> list[tuple[str, float]]:
        """查询向量 → ``[(entity_id, cosine)]``（实体名语义链接，无不建实体向量时返回空）。"""
        if self.ent_vectors is None or self.ent_ids is None or not len(self.ent_ids):
            return []
        qv = np.asarray(query_vec, dtype=np.float32)
        if qv.shape[-1] != self.ent_vectors.shape[1]:
            return []
        n = qv / (np.linalg.norm(qv) or 1.0)
        sims = self.ent_vectors @ n
        k = max(1, min(int(top_k), len(sims)))
        idx = np.argpartition(-sims, k - 1)[:k]
        idx = idx[np.argsort(-sims[idx])]
        return [(str(self.ent_ids[i]), float(sims[i])) for i in idx]

    @property
    def available(self) -> bool:
        return self.vectors is not None and self.hashes is not None and len(self.hashes) > 0

    @property
    def count(self) -> int:
        return int(len(self.hashes)) if self.hashes is not None else 0

    def embed_query(self, text: str) -> np.ndarray | None:
        """查询侧嵌入；服务不可用时返回 None（调用方跳过通道，不抛异常）。"""
        if self.embedder is None:
            return None
        try:
            return np.asarray(self.embedder.embed_query(text), dtype=np.float32)
        except Exception as exc:  # noqa: BLE001
            logger.warning("剧情语义检索：查询嵌入失败，本轮跳过该通道：%s", exc)
            return None


def corpus_sha16(path: str | Path) -> str:
    """语料文件 sha256 前 16 位（与 scripts/build_plot_index.py 同口径）。"""
    import hashlib

    h = hashlib.sha256()
    try:
        with Path(path).open("rb") as fh:
            for blk in iter(lambda: fh.read(1 << 20), b""):
                h.update(blk)
    except OSError:
        return ""
    return h.hexdigest()[:16]
