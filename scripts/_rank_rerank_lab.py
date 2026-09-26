# -*- coding: utf-8 -*-
"""排序实验 · 离线重排实验室 v2（rank_rerank_lab）。

输入是 ``_rank_collect.py`` 的产物（--base，可选 --holdout），**运行期零检索、
零网关**：只加载库的只读资产（kb 块文本、chunk_index.npz 块向量、graph.json
邻接度数）+ 采集文件里的证据列表，全部计算在本地。

BLIND FEATURE RULE（铁律）
--------------------------
盲特征只允许用：query 文本、qvec、证据字段（score/channels/ppr/rank）、
块文本、块向量、图谱度数、种子名、以及 ``--extra-features`` 给的**外部**
逐对分数（外部分数由独立管线产出，本脚本无法验证其盲性，使用方需自证
它没有接触 gold）。采集文件里的 ``eval_keywords``（gold 答案关键词）是
**评测专用**，只允许出现在 ORACLE 诊断与指标评测里，**绝不进入特征、
绝不进入任何盲策略的决策**。代码里 ORACLE 与 BLIND 两条路径物理分离：
gold 只在 ``gold_matrix()``（评测）与 ``oracle_ceiling()``（诊断，读采集
文件自带的 rank 字段）出现；特征函数 ``FeatureBuilder.question()`` 的
入参里没有 keywords。

候选池（--pool N，默认 10，上限 30）
------------------------------------
池 = 采集文件里 evidence 的第 1..N 名。要求采集 top_k >= N（top30 采集
文件 ``rank_collect_*_top30.json`` 才能开 pool=30）。

盲分特征（逐题 z 分数归一后加权求和）：
  cos       cos(qvec, chunk_vec)     （graph_only 无 qvec → 弃用并注明）
  lex       query 字符 bigram 在块文本中的覆盖率
  lex_idf   同 lex 但按 idf 加权；df 在加载时对全部块 blob 一次统计
  lex_title 同 lex 但覆盖目标 = eval300 score_case 的**精确 blob**：
            f"{text}\n{chapter_title}\n{scene_title}\n{part_title}"
  orig      原融合分（RRF score）
  ppr       PPR 分
  has_vec   是否有 vector 通道
  seed      种子名（link() 精确/别名，纯本地、零 gold）子串是否出现在块文本
  chunk_len 块文本长度
  log_deg   块挂载实体的 log(1+度数) 最大值（度数=无向邻接邻居数）
  extra     --extra-features 的外部分数列（仅 full 模式；覆盖不全 → 相关
            配置标 PENDING 跳过并告警）

策略族（在 answerable 层、pool N 上评测；三个族的盲分都用逐题 z 分数，
top1_thresh 另用逐题 min-max 到 [0,1]——比率对可负的 z 分数无定义）：
  boundary_promote(m)  槽 1-5 不动；第 6..N 名里盲分最高者，若其盲分超过
                       现 #6 盲分 + m，则与槽 6 **互换**（纯重排，集合不变）。
                       m ∈ {0, 0.05, 0.1, 0.2, 0.3}。
  full_topN(a)         按 (1-a)·norm_orig_rank + a·norm_blindscore 升序重排
                       全池（norm_orig_rank=原位次/(N-1)；并列按原名次稳定
                       排序）。a ∈ {0, 0.05, …, 1.0}（a=0 等价基线，自检位）。
  top1_thresh(t)       第 6..N 名里盲分最高者，若其 min-max 归一分 ≥
                       t × #1 的归一分，则与槽 6 互换。t ∈ {0.5,…,0.9}。

拟合权重（zfit）：坐标上升最大化 full_topN a=1（纯盲分序）的 hit@6
（并列看 MRR@6），网格 {0, 0.5, 1, 2}×2 轮；LOO-CV 逐题留一重拟合，
报 CV 均值 vs 全量拟合（过拟合检查，计划 C5）。

ORACLE 诊断与天花板（用 gold，只是天花板参考，不可部署）：
  - k=6 未命中题的名次分布（7-10 / 11-20 / 21-30 / >30 / never）；
  - 池天花板 N ∈ {10,20,30}：answerable 中 6 < rank <= N 的比例
    （"pool N 可挽回数"），以及"若重排把池内 gold 全部顶进前 6"的
    ceiling hit@6 = rank<=N 的比例（rank 字段取自采集文件，需 top_k>=N）。

目标线（0.85）：所有结果表都显式给到目标线的差距——best blind hit@6、
Δ_to_target = 0.85 − best、oracle_gap = ceiling(池) − best。

安全（C6）与泛化（对选出的最优盲配置）：
  - 打到 base 的 unanswerable 层：hit@6 不得超过其自身基线（300_cn 参考
    值 0.0096=1/104，一并报告精确计数）；grounded 必须仍为 1.0；程序化
    校验重排只动次序（逐题 chunk_id 多重集不变）。
  - --holdout 给出时，同一配置原封不动打过去，报 Δhit@6（泛化检查）。

用法（项目根目录）：
  ./.venv/Scripts/python.exe scripts/_rank_rerank_lab.py \
      --base data/compendium_rag/reports/rank_collect_300_cn_top30.json \
      --holdout data/compendium_rag/reports/rank_collect_native_top30.json \
      --pool 30
  冒烟（现有 top20 冒烟采集即可）：
  ./.venv/Scripts/python.exe scripts/_rank_rerank_lab.py \
      --base data/compendium_rag/reports/rank_collect_smoke_f_top20.json --pool 20

退出码：0=有盲配置在 answerable 上胜出且安全底线无违反；
        1=安全底线被违反；2=没有任何盲配置胜出（合法结论）。
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from compendium_rag import pipeline as P  # noqa: E402
from compendium_rag.config import get_settings  # noqa: E402
from compendium_rag.retriever import build_adjacency  # noqa: E402

POOL_DEFAULT = 10
POOL_MAX = 30
K_MAIN = 6                      # 主指标边界：hit@6（对齐 eval300，不可调）
MARGINS = (0.0, 0.05, 0.1, 0.2, 0.3)
TAUS = (0.5, 0.6, 0.7, 0.8, 0.9)
ALPHAS = tuple(round(0.05 * i, 2) for i in range(21))
BASE_FEATURES = ("cos", "lex", "lex_idf", "lex_title", "orig", "ppr",
                 "has_vec", "seed", "chunk_len", "log_deg")
TARGET_HIT6 = 0.85              # 升级后的目标线（300_cn answerable, full）
REF_UNANS_HIT6 = 0.0096         # 300_cn 基线参考值（1/104）
CLAIM = "计划书口径：40 misses / 31 named-rank / 14 stuck at 7-10"
PARAM_KEY = {"boundary_promote": "m", "full_topN": "a", "top1_thresh": "t"}


# ── 采集文件加载 ──────────────────────────────────────────────

def load_collect(path: Path, pool: int) -> dict:
    d = json.loads(path.read_text(encoding="utf-8"))
    rows = d.get("rows") or []
    if not rows or "evidence" not in rows[0]:
        raise SystemExit(f"[FAIL] {path} 不是 rank_collect 产物（缺 evidence 列表）")
    if d.get("top_k", 0) < pool:
        raise SystemExit(f"[FAIL] {path} 的 top_k={d.get('top_k')} < pool={pool}："
                         f"候选池不够，请用 top{pool} 的采集文件重跑 _rank_collect.py")
    return d


def zscore_row(x: np.ndarray) -> np.ndarray:
    """逐行 z 分数（方差 0 → 全 0），x 形状 (n, pool)。"""
    mu = x.mean(axis=1, keepdims=True)
    sd = x.std(axis=1, keepdims=True)
    out = np.zeros_like(x)
    nz = sd[:, 0] > 1e-12
    out[nz] = (x[nz] - mu[nz]) / sd[nz]
    return out


def _bigrams(s: str) -> set[str]:
    return {s[i:i + 2] for i in range(len(s) - 1)}


# ── 盲特征（不含任何 gold 信息）─────────────────────────────

class FeatureBuilder:
    """逐题逐候选盲特征。只吃 query/qvec/证据字段/块文本/块向量/图谱度数。"""

    def __init__(self, kb) -> None:
        self.chunks = kb.retriever.chunks
        ci = kb.chunk_index
        self.matrix = ci.matrix if ci is not None else None
        self.pos = {c: i for i, c in enumerate(ci.chunk_ids)} if ci is not None else {}
        if self.matrix is not None:
            nrm = np.linalg.norm(self.matrix, axis=1, keepdims=True)
            nrm[nrm == 0] = 1.0
            self.matrix = self.matrix / nrm
        # chunk → 挂载实体 → log(1+度数) 最大值（度数=无向邻接邻居数）
        adj, _wsum, _edges = build_adjacency(kb.graph)
        deg = {eid: len(nbrs) for eid, nbrs in adj.items()}
        self.chunk_log_deg: dict[str, float] = {}
        for eid, ent in kb.graph.entities.items():
            d = math.log1p(deg.get(eid, 0))
            for cid in ent.chunk_ids:
                if d > self.chunk_log_deg.get(cid, -1.0):
                    self.chunk_log_deg[cid] = d
        # idf：df 在加载时对**全部块 blob**（score_case 精确口径）一次统计
        self.n_chunks = len(kb.chunks)
        df: Counter = Counter()
        for c in kb.chunks:
            df.update(_bigrams("".join(self.blob(c.chunk_id).split())))
        self.df = df

    def blob(self, cid: str) -> str:
        """score_case 精确 blob：text + 三个篇名字段，\\n 直连。"""
        c = self.chunks.get(cid)
        if c is None:
            return ""
        return f"{c.text}\n{c.chapter_title}\n{c.scene_title}\n{c.part_title}"

    def _idf(self, g: str) -> float:
        return math.log((self.n_chunks + 1) / (1 + self.df.get(g, 0))) + 1.0

    def question(self, q_used: str, qvec, ev_pool: list[dict],
                 link_fn) -> tuple[np.ndarray, float]:
        """返回 (pool×len(BASE_FEATURES) 特征矩阵, 耗时秒)。

        link_fn = kb.retriever.link（纯符号实体链接，精确/别名，零网络、
        零 gold）；种子名只用于 ``seed`` 特征。"""
        t0 = time.perf_counter()
        qb = _bigrams("".join((q_used or "").split()))
        q_idf = {g: self._idf(g) for g in qb}
        qb_total = sum(q_idf.values())
        names = [s.name.lower() for s in link_fn(q_used)] if q_used else []
        qn = None
        if qvec is not None and self.matrix is not None:
            qn = np.asarray(qvec, dtype=np.float32)
            n = np.linalg.norm(qn)
            if n > 0:
                qn = qn / n
        cols: list[list[float]] = []
        for e in ev_pool:
            c = self.chunks.get(e["chunk_id"])
            ctext = c.text if c else ""
            row = [0.0] * len(BASE_FEATURES)
            if qn is not None and e["chunk_id"] in self.pos:
                row[0] = float(self.matrix[self.pos[e["chunk_id"]]] @ qn)
            if qb:
                cb = _bigrams("".join(ctext.split()))
                inter = qb & cb
                row[1] = len(inter) / len(qb)
                row[2] = (sum(q_idf[g] for g in inter) / qb_total) if qb_total else 0.0
                bb = _bigrams("".join(self.blob(e["chunk_id"]).split()))
                row[3] = len(qb & bb) / len(qb)
            row[4] = float(e.get("score", 0.0))
            row[5] = float(e.get("ppr", 0.0))
            row[6] = 1.0 if "vector" in (e.get("channels") or {}) else 0.0
            low = ctext.lower()
            row[7] = 1.0 if any(n in low for n in names) else 0.0
            row[8] = float(len(ctext))
            row[9] = float(self.chunk_log_deg.get(e["chunk_id"], 0.0))
            cols.append(row)
        dt = time.perf_counter() - t0
        return np.asarray(cols, dtype=np.float64), dt


# ── ORACLE：gold 矩阵（评测专用路径，绝不进特征）────────────

def gold_matrix(kb, pools: list[list[dict]], kw_lists: list[list[str]],
                pool: int) -> np.ndarray:
    """gold[i,j]：池内第 j 块的 blob 是否含任一 gold 关键词（同 eval300 blob）。"""
    blobs: dict[str, str] = {}

    def blob(cid: str) -> str:
        if cid not in blobs:
            c = kb.retriever.chunks.get(cid)
            blobs[cid] = (f"{c.text}\n{c.chapter_title}\n{c.scene_title}\n"
                          f"{c.part_title}") if c else ""
        return blobs[cid]

    G = np.zeros((len(pools), pool), dtype=bool)
    for i, (ev, kws) in enumerate(zip(pools, kw_lists)):
        for j, e in enumerate(ev):
            b = blob(e["chunk_id"])
            if b and any(k in b for k in kws):
                G[i, j] = True
    return G


# ── 策略与评测（全向量化）────────────────────────────────────

def apply_policy(kind: str, param: float, S: np.ndarray,
                 pool: int) -> np.ndarray:
    """S=(n,pool) 盲分 → perm=(n,pool) 新次序（原下标）。只重排，不改集合。"""
    n = S.shape[0]
    base = np.tile(np.arange(pool), (n, 1))
    if kind == "baseline":
        return base
    if kind == "full_topN":
        Ss = zscore_row(S)
        rn = np.arange(pool, dtype=np.float64)[None, :] / max(1, pool - 1)
        key = (1.0 - param) * rn - param * Ss
        return np.argsort(key, axis=1, kind="stable")
    lo = K_MAIN - 1                    # 槽 6 的 0 基下标；候选=第 6..N 名
    if kind == "boundary_promote":
        Ss = zscore_row(S)
        best = lo + np.argmax(Ss[:, lo:pool], axis=1)
        cond = Ss[np.arange(n), best] > Ss[:, lo] + param
    elif kind == "top1_thresh":
        mn = S.min(axis=1, keepdims=True)
        span = (S.max(axis=1, keepdims=True) - mn)[:, 0]
        rel = np.zeros_like(S)
        ok = span > 1e-12
        rel[ok] = (S[ok] - mn[ok]) / span[ok, None]
        best = lo + np.argmax(rel[:, lo:pool], axis=1)
        cond = rel[np.arange(n), best] >= param * rel[:, 0]
    else:
        raise ValueError(kind)
    r = np.arange(n)[cond]
    bb = best[cond]
    perm = base.copy()
    perm[r, lo] = bb          # 原 #6 被顶下，落到胜者的原槽位
    perm[r, bb] = lo
    return perm


def eval_perm(perm: np.ndarray, G: np.ndarray, pool: int):
    """按新次序评测 hit@6 / hit@10 / rr@6 / rr@10（gold 只在这里用）。

    pool<10 时 hit@10 退化为 hit@pool（下界，输出注明）。"""
    og = np.take_along_axis(G, perm, axis=1)
    has = og.any(axis=1)
    first = np.argmax(og, axis=1)          # 无命中时 argmax=0，由 has 屏蔽
    hit6 = has & (first < K_MAIN)
    k10 = min(10, pool)
    hit10 = has & (first < k10)
    rr6 = np.where(hit6, 1.0 / (first + 1), 0.0)
    rr10 = np.where(hit10, 1.0 / (first + 1), 0.0)
    return hit6, hit10, rr6, rr10


def metrics(perm: np.ndarray, G: np.ndarray, pool: int) -> dict:
    hit6, hit10, rr6, rr10 = eval_perm(perm, G, pool)
    return {"n": int(len(hit6)),
            "hit6": round(float(hit6.mean()), 4),
            "hit10": round(float(hit10.mean()), 4),
            "mrr6": round(float(rr6.mean()), 4),
            "mrr10": round(float(rr10.mean()), 4)}


def flips(perm: np.ndarray, G: np.ndarray, qids: list[str],
          base_hit6: np.ndarray, pool: int) -> tuple[list[str], list[str]]:
    hit6, _h10, _r6, _r10 = eval_perm(perm, G, pool)
    up = sorted(q for q, a, b in zip(qids, base_hit6, hit6) if b and not a)
    down = sorted(q for q, a, b in zip(qids, base_hit6, hit6) if a and not b)
    return up, down


# ── 权重拟合（坐标上升，目标：full_topN a=1 的 hit@6）────────

def fit_weights(Zs: np.ndarray, G: np.ndarray, idx: np.ndarray,
                active: np.ndarray, pool: int) -> np.ndarray:
    F = Zs.shape[2]

    def obj(w):
        Ss = zscore_row(Zs[idx] @ w)
        perm = np.argsort(-Ss, axis=1, kind="stable")   # a=1：纯盲分序
        hit6, _h10, rr6, _rr10 = eval_perm(perm, G[idx], pool)
        return (int(hit6.sum()), float(rr6.sum()))

    w = np.where(active, 1.0, 0.0)
    best = obj(w)
    for _p in range(2):
        improved = False
        for j in range(F):
            if not active[j]:
                continue
            for v in (0.0, 0.5, 1.0, 2.0):
                if abs(w[j] - v) < 1e-12:
                    continue
                w2 = w.copy()
                w2[j] = v
                sc = obj(w2)
                if sc > best:
                    best, w, improved = sc, w2, True
        if not improved:
            break
    return w


# ── 数据准备 ─────────────────────────────────────────────────

def prepare(d: dict, kb, fb: FeatureBuilder, mode: str, pool: int,
            extra_map: dict | None) -> dict:
    """筛出该模式下池子完整的题；特征（盲）与金标（评测专用）分开建。

    extra_map 仅 full 模式生效：只要给了就**总是**建 extra 列（缺失填 0.0），
    保证 base/holdout 特征维度一致；是否**启用**该列由调用方按覆盖情况
    裁决（覆盖不全 → 裁掉整列，extra 配置标 PENDING）。"""
    rows = [r for r in d["rows"] if r["mode"] == mode]
    with_extra = bool(extra_map) and mode == "full"
    qs, pools, kws, Zs, feat_ms = [], [], [], [], []
    drop = 0
    link = kb.retriever.link
    missing_extra: set[str] = set()
    for r in rows:
        ev = r["evidence"][:pool]
        if len(ev) < pool:
            drop += 1
            continue
        qvec = (d.get("qvecs") or {}).get(r["qid"])
        Z1, dt = fb.question(r["q_used"], qvec, ev, link)
        feat_ms.append(dt * 1000.0)
        if with_extra:
            emap = extra_map.get(r["qid"]) or {}
            col = []
            for j in range(pool):
                v = emap.get(j + 1)
                if v is None:
                    missing_extra.add(r["qid"])
                    v = 0.0
                col.append(float(v))
            Z1 = np.column_stack([Z1, np.asarray(col, dtype=np.float64)])
        qs.append({"qid": r["qid"], "answerable": bool(r["answerable"]),
                   "q_used": r["q_used"], "stored_rank": r["rank"],
                   "stored_hit6": (r["rank"] is not None and r["rank"] <= K_MAIN),
                   "chunk_ids": [e["chunk_id"] for e in ev]})
        pools.append(ev)
        kws.append(r["eval_keywords"])
        Zs.append(Z1)
    feats_full = BASE_FEATURES + (("extra",) if with_extra else ())
    Z = np.stack(Zs) if Zs else np.zeros((0, pool, len(feats_full)))
    G = gold_matrix(kb, pools, kws, pool) if pools else np.zeros((0, pool), dtype=bool)
    ans = np.array([q["answerable"] for q in qs], dtype=bool)
    qids = [q["qid"] for q in qs]
    # 基线自检：identity 次序下的 hit@6 应与采集时存的 rank<=6 一致
    base_hit6, _h10, _r6, _r10 = eval_perm(
        np.tile(np.arange(pool), (len(qs), 1)), G, pool)
    mism = [q["qid"] for q, a, b in zip(qs, base_hit6,
                                        [x["stored_hit6"] for x in qs]) if a != b]
    return {"qs": qs, "qids": qids, "ans": ans, "Z": Z, "G": G,
            "feats_full": feats_full, "pool": pool, "feat_ms": feat_ms,
            "drop": drop, "base_hit6": base_hit6, "mismatch": mism,
            "extra_built": with_extra,
            "extra_missing_qids": sorted(missing_extra)}


def sweep_configs(Z: np.ndarray, G: np.ndarray, idx: np.ndarray, qids: list[str],
                  base_hit6: np.ndarray, scorers: dict[str, np.ndarray],
                  feats: tuple, pool: int) -> list[dict]:
    """对每个打分器 × 三个策略族扫参，输出全部配置的指标与逐题翻转。"""
    out: list[dict] = []
    base_perm = np.tile(np.arange(pool), (len(idx), 1))
    plan = ([("boundary_promote", m, "m") for m in MARGINS]
            + [("full_topN", a, "a") for a in ALPHAS]
            + [("top1_thresh", t, "t") for t in TAUS])
    for name, w in scorers.items():
        S = Z[idx] @ w
        for kind, param, pkey in plan:
            perm = apply_policy(kind, param, S, pool)
            m = metrics(perm, G[idx], pool)
            up, down = flips(perm, G[idx], [qids[i] for i in idx],
                             base_hit6[idx], pool)
            out.append({
                "name": f"{kind}[{name}]{pkey}={param}",
                "policy": kind, "params": {pkey: param},
                "scorer": name,
                "weights": {f: round(float(x), 4) for f, x in zip(feats, w)},
                **m, "up_qids": up, "down_qids": down,
            })
    m = metrics(base_perm, G[idx], pool)
    out.insert(0, {"name": "baseline", "policy": "baseline", "params": {},
                   "scorer": "", "weights": {}, **m,
                   "up_qids": [], "down_qids": []})
    return out


def pick_best(configs: list[dict]) -> dict:
    """确定性选优：hit@6 降序 → MRR@6 降序 → 名字升序（跳过 baseline/PENDING）。"""
    cands = [c for c in configs
             if c["name"] != "baseline" and not c.get("pending")]
    return sorted(cands, key=lambda c: (-c["hit6"], -c["mrr6"], c["name"]))[0]


# ── ORACLE 天花板（读采集 rank 字段，gold 仅用于诊断）────────

def oracle_ceiling(rows: list[dict], mode: str, top_k: int) -> dict:
    ans_rows = [r for r in rows if r["mode"] == mode and r["answerable"]]
    n = len(ans_rows)
    ranks = [r["rank"] for r in ans_rows]
    misses = [r for r in ans_rows if r["rank"] is None or r["rank"] > K_MAIN]
    named = [r for r in misses if r["rank"] is not None]
    out: dict = {
        "n_answerable": n, "top_k": top_k, "k6_misses": len(misses),
        "named_rank": len(named),
        "never_in_window": sum(1 for r in misses if r["rank"] is None),
        "claim_ref": CLAIM,
        "miss_qids": [r["qid"] for r in misses],
        "pools": {},
    }
    for N in (10, 20, 30):
        if top_k < N:
            out["pools"][str(N)] = {
                "available": False,
                "note": f"采集 top_k={top_k} < {N}：需 top{N} 采集文件才能评估"}
            continue
        rec = sum(1 for x in ranks if x and K_MAIN < x <= N)
        le = sum(1 for x in ranks if x and x <= N)
        out["pools"][str(N)] = {
            "available": True, "recoverable": rec,
            "recoverable_rate": round(rec / n, 4) if n else None,
            "ceiling_hit6": round(le / n, 4) if n else None,
        }
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--holdout", default="")
    ap.add_argument("--mode", default="full", choices=["full", "graph_only"])
    ap.add_argument("--pool", type=int, default=POOL_DEFAULT,
                    help=f"候选池=证据前 N 名（{K_MAIN}≤N≤{POOL_MAX}，默认 10）")
    ap.add_argument("--extra-features", default="",
                    help="外部逐对分数 json：{qid:{\"<rank>\":float}}（仅 full）")
    ap.add_argument("--holdout-strata", default="",
                    help="holdout 测试集 json（读行级 _pool 分层，C7 分层报告）")
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    pool = args.pool
    if not (K_MAIN <= pool <= POOL_MAX):
        print(f"[FAIL] --pool 必须在 {K_MAIN}..{POOL_MAX}，收到 {pool}")
        return 1

    def rp(p: str) -> Path:
        x = Path(p)
        return x if x.is_absolute() else ROOT / p

    base_path = rp(args.base)
    base = load_collect(base_path, pool)
    extra_map: dict | None = None
    extra_note = ""
    if args.extra_features:
        if args.mode != "full":
            extra_note = "--extra-features 仅 full 模式生效，本次忽略"
            print(f"[WARN] {extra_note}")
        else:
            raw = json.loads(rp(args.extra_features).read_text(encoding="utf-8"))
            extra_map = {q: {int(k): float(v) for k, v in ranks.items()}
                         for q, ranks in raw.items()}
    # holdout 分层表（C7）：qid → 测试集行级 _pool（collect 的 dims 不带 _pool）
    strata_map: dict[str, str] = {}
    if args.holdout_strata:
        ts_path = rp(args.holdout_strata)
        ts = json.loads(ts_path.read_text(encoding="utf-8"))
        ts_rows = ts if isinstance(ts, list) else ts.get("cases", [])
        for r in ts_rows:
            qid = str(r.get("id", ""))
            v = r.get("_pool", (r.get("dims") or {}).get("_pool"))
            strata_map[qid] = str(v) if v is not None else "(missing)"
        cnt = Counter(strata_map.values())
        print(f"holdout 分层表：{ts_path.name}  qids={len(strata_map)}  "
              f"分层={dict(cnt)}")

    s = get_settings()
    kb = P.load_kb(s)
    fb = FeatureBuilder(kb)
    tag = base.get("tag") or base_path.stem.replace("rank_collect_", "")

    print(f"== 排序重排实验室 v2 ==  base={base_path.name} mode={args.mode} "
          f"pool={pool}  目标线 hit@6={TARGET_HIT6}")
    B = prepare(base, kb, fb, args.mode, pool, extra_map)
    # extra 列启用裁决：base 覆盖不全 → 裁掉整列（extra 配置标 PENDING）
    if B["extra_built"] and B["extra_missing_qids"]:
        B["Z"] = B["Z"][:, :, :-1]
        B["feats"] = BASE_FEATURES
        B["extra_applied"] = False
    else:
        B["feats"] = B["feats_full"]
        B["extra_applied"] = B["extra_built"]
    n_all = len(B["qs"])
    n_ans = int(B["ans"].sum())
    n_unans = n_all - n_ans
    print(f"题目：n={n_all} answerable={n_ans} unanswerable={n_unans} "
          f"池不足丢弃={B['drop']}")
    if B["mismatch"]:
        print(f"[WARN] 基线 hit@6 与采集存档不一致 {len(B['mismatch'])} 题："
              f"{B['mismatch'][:10]}")
    if B["extra_missing_qids"]:
        print(f"[WARN] extra 特征覆盖不全（缺 {len(B['extra_missing_qids'])} 题）："
              f"extra 配置将标 PENDING 跳过")
    if n_ans == 0:
        print("[FAIL] answerable 层为空，无法实验")
        return 1

    # ── ORACLE 诊断 + 池天花板（gold 只在这里用）──
    oracle = oracle_ceiling(base["rows"], args.mode, base.get("top_k", 0))
    # ceiling 与策略指标必须同口径：用**同一 kept 子集**算（有丢题时
    # 全集口径会高估/错位）。300_cn 正式采集无丢题时两者相等。
    kept_ans = [q for q, a in zip(B["qs"], B["ans"]) if a]
    if kept_ans:
        ceil_pool = sum(1 for q in kept_ans
                        if q["stored_rank"] is not None
                        and q["stored_rank"] <= pool) / len(kept_ans)
        ceil_pool = round(ceil_pool, 4)
    else:
        ceil_pool = None
    print(f"\n== ORACLE 诊断（{args.mode} / answerable，{CLAIM}）==")
    print(f"  k=6 misses={oracle['k6_misses']} / {oracle['n_answerable']}"
          f"  named-rank（已入采集窗）={oracle['named_rank']}"
          f"  never={oracle['never_in_window']}")
    for N, p in oracle["pools"].items():
        if p["available"]:
            print(f"  pool N={N}: 可挽回(6<rank≤{N})={p['recoverable']}"
                  f"（{p['recoverable_rate']}）  ceiling hit@6={p['ceiling_hit6']}")
        else:
            print(f"  pool N={N}: PENDING —— {p['note']}")

    # ── 打分器：单特征 + zcombo + zfit（extra 覆盖不全时整列撤下）──
    Za = B["Z"][B["ans"]]
    var = Za.reshape(-1, len(B["feats"])).std(axis=0)
    active = var > 1e-9
    inactive = [f for f, a in zip(B["feats"], active) if not a]
    if inactive:
        print(f"[note] 全程无方差、弃用的特征：{inactive}")
    feats = B["feats"]
    scorers: dict[str, np.ndarray] = {}
    for j, f in enumerate(feats):
        if active[j]:
            w = np.zeros(len(feats))
            w[j] = 1.0
            scorers[f] = w
    if active.any():
        w = active.astype(float)
        scorers["zcombo"] = w / w.sum()
    w_fit = fit_weights(B["Z"], B["G"], np.where(B["ans"])[0], active, pool)
    scorers["zfit"] = w_fit
    print(f"  zfit 权重：{dict(zip(feats, [round(float(x), 3) for x in w_fit]))}")

    idx_ans = np.where(B["ans"])[0]
    configs = sweep_configs(B["Z"], B["G"], idx_ans, B["qids"], B["base_hit6"],
                            scorers, feats, pool)
    baseline = configs[0]
    if B["extra_missing_qids"]:
        configs.append({"name": "extra (PENDING)", "pending": True,
                        "note": f"外部特征覆盖不全（缺 {len(B['extra_missing_qids'])} 题），"
                                f"使用 extra 的配置全部跳过"})
    chosen = pick_best(configs)
    beats = chosen["hit6"] > baseline["hit6"]
    delta_target = round(TARGET_HIT6 - chosen["hit6"], 4)
    oracle_gap = (round(ceil_pool - chosen["hit6"], 4)
                  if ceil_pool is not None else None)
    print(f"\n== 配置扫描（answerable n={n_ans}，pool={pool}，"
          f"目标线 {TARGET_HIT6}）==")
    print(f"  基线 hit@6={baseline['hit6']} hit@10={baseline['hit10']} "
          f"MRR@6={baseline['mrr6']} MRR@10={baseline['mrr10']}"
          + (f"  ceiling@pool{pool}={ceil_pool}" if ceil_pool is not None else ""))
    top10 = sorted([c for c in configs if not c.get("pending")][1:],
                   key=lambda c: (-c["hit6"], -c["mrr6"], c["name"]))
    for c in top10[:10]:
        mark = " ← chosen" if c["name"] == chosen["name"] else ""
        print(f"  {c['name']:44s} hit@6={c['hit6']:.4f} "
              f"gap_to_{TARGET_HIT6}={round(TARGET_HIT6 - c['hit6'], 4):+.4f} "
              f"MRR@6={c['mrr6']:.4f} up={len(c['up_qids'])} "
              f"down={len(c['down_qids'])}{mark}")
    print(f"  配置总数={len(configs)-1}+baseline  chosen={chosen['name']} "
          f"Δhit@6_vs_base={round(chosen['hit6']-baseline['hit6'], 4)}")
    print(f"  → 距目标线：best blind hit@6={chosen['hit6']}  "
          f"Δ_to_target={delta_target:+.4f}  "
          f"oracle_gap={oracle_gap if oracle_gap is not None else 'PENDING(top30 需采集)'}")

    # ── 安全（C6）：unanswerable 层 ──
    idx_un = np.where(~B["ans"])[0]
    safety: dict = {"n_unanswerable": len(idx_un), "ref_300cn_hit6": REF_UNANS_HIT6}
    if len(idx_un):
        w_ch = scorers[chosen["scorer"]]
        S_un = B["Z"][idx_un] @ w_ch
        perm_un = apply_policy(chosen["policy"], chosen["params"][PARAM_KEY[chosen["policy"]]],
                               S_un, pool)
        m_un = metrics(perm_un, B["G"][idx_un], pool)
        before_cnt = int(B["base_hit6"][idx_un].sum())
        after_cnt = int(round(m_un["hit6"] * len(idx_un)))
        multiset_ok = bool(np.all(np.sort(perm_un, axis=1) == np.arange(pool)))
        grounded_ids = all(cid in kb.retriever.chunks
                           for q in B["qs"] if not q["answerable"]
                           for cid in q["chunk_ids"])
        safety.update({
            "hit6_before": baseline["hit6"], "hit6_after": m_un["hit6"],
            "hit6_before_count": before_cnt, "hit6_after_count": after_cnt,
            "grounded_all": grounded_ids, "multiset_preserved": multiset_ok,
        })
        safety["violation"] = (after_cnt > before_cnt or not grounded_ids
                               or not multiset_ok)
        print(f"\n== 安全底线（unanswerable n={len(idx_un)}）==")
        print(f"  hit@6：{before_cnt}/{len(idx_un)} → {after_cnt}/{len(idx_un)}"
              f"  （300_cn 参考 {REF_UNANS_HIT6}）  grounded={grounded_ids}  "
              f"多重集不变={multiset_ok}  → "
              f"{'违反' if safety['violation'] else 'PASS'}")
    else:
        safety["violation"] = False
        print("\n== 安全底线 == 无 unanswerable 题，跳过")

    # ── 消融：留一特征 ──
    w_ch = scorers[chosen["scorer"]]
    act_idx = [j for j in range(len(feats)) if active[j] and w_ch[j] != 0]
    ablation: list[dict] = []
    if len(act_idx) <= 1:
        ablation.append({"note": "所选打分器只有 <=1 个有效特征，"
                                 "留一消融退化为基线", "delta_hit6": None})
    else:
        for j in act_idx:
            w2 = w_ch.copy()
            w2[j] = 0.0
            S = B["Z"][idx_ans] @ w2
            perm = apply_policy(chosen["policy"],
                                chosen["params"][PARAM_KEY[chosen["policy"]]],
                                S, pool)
            m = metrics(perm, B["G"][idx_ans], pool)
            ablation.append({"dropped": feats[j], "hit6": m["hit6"],
                             "delta_hit6": round(m["hit6"] - chosen["hit6"], 4)})
    print("\n== 消融（留一特征，chosen 配置）==")
    for a in ablation:
        if "dropped" in a:
            print(f"  -{a['dropped']:10s} hit@6={a['hit6']:.4f} "
                  f"Δ={a['delta_hit6']:+.4f}")
        else:
            print(f"  {a['note']}")

    # ── LOO-CV（zfit 过拟合检查）──
    loo: dict = {"note": "对 zfit 权重做逐题留一重拟合；"
                         "用 zfit 自身最优配置（policy/参数不变）评测留一题"}
    zfit_cfg = pick_best([c for c in configs if c.get("scorer") == "zfit"])
    kind = zfit_cfg["policy"]
    param = zfit_cfg["params"][PARAM_KEY[kind]]
    idx_fit = idx_ans
    if kind == "baseline" or len(idx_fit) < 3:
        loo.update({"skipped": True,
                    "reason": "zfit 最优为基线或样本过少"})
        print("\n== LOO-CV == 跳过（" + loo.get("reason", "") + "）")
    else:
        t0 = time.time()
        cv_hit, cv_rr = [], []
        for i in idx_fit:
            tr = idx_fit[idx_fit != i]
            w_i = fit_weights(B["Z"], B["G"], tr, active, pool)
            Ss = zscore_row(B["Z"][i:i + 1] @ w_i)
            perm = apply_policy(kind, param, Ss, pool)
            h6, _h10, r6, _r10 = eval_perm(perm, B["G"][i:i + 1], pool)
            cv_hit.append(bool(h6[0]))
            cv_rr.append(float(r6[0]))
        loo.update({
            "config": zfit_cfg["name"],
            "in_sample_hit6": zfit_cfg["hit6"], "in_sample_mrr6": zfit_cfg["mrr6"],
            "cv_hit6": round(sum(cv_hit) / len(cv_hit), 4),
            "cv_mrr6": round(sum(cv_rr) / len(cv_rr), 4),
            "n_folds": len(cv_hit), "seconds": round(time.time() - t0, 1),
            "overfit_gap_hit6": round(zfit_cfg["hit6"] - sum(cv_hit) / len(cv_hit), 4),
        })
        print(f"\n== LOO-CV（{zfit_cfg['name']}，n={len(cv_hit)}，"
              f"{loo['seconds']}s）==")
        print(f"  in-sample hit@6={zfit_cfg['hit6']:.4f}  "
              f"CV hit@6={loo['cv_hit6']:.4f}  "
              f"过拟合差={loo['overfit_gap_hit6']:+.4f}")

    # ── Holdout（泛化检查 + C7 分层证据层）──
    holdout: dict = {"path": str(args.holdout or ""), "applied": False,
                     "rows": [], "strata": {}}
    if args.holdout:
        hp = rp(args.holdout)
        H = prepare(load_collect(hp, pool), kb, fb, args.mode, pool, extra_map)
        # 与 base 保持同一特征维度：base 启用了 extra → holdout 保留该列
        #（缺失名次填 0.0，z 分数后无贡献）；base 没启用 → 同步裁掉
        if B["extra_applied"]:
            H["feats"] = H["feats_full"]
        else:
            if H["extra_built"]:
                H["Z"] = H["Z"][:, :, :-1]
            H["feats"] = BASE_FEATURES
        h_extra_covered = not H["extra_missing_qids"]
        h_idx = np.where(H["ans"])[0]
        if len(h_idx) == 0:
            holdout["note"] = "holdout answerable 层为空"
            print("\n== Holdout == " + holdout["note"])
        elif chosen["scorer"] == "extra" and not h_extra_covered:
            holdout["note"] = "holdout 缺 extra 特征覆盖，extra 相关配置 PENDING"
            print("\n== Holdout == " + holdout["note"])
        else:
            param_h = chosen["params"][PARAM_KEY[chosen["policy"]]]
            S_h = H["Z"][h_idx] @ w_ch
            perm_h = apply_policy(chosen["policy"], param_h, S_h, pool)
            m_h = metrics(perm_h, H["G"][h_idx], pool)
            m_hb = metrics(np.tile(np.arange(pool), (len(h_idx), 1)),
                           H["G"][h_idx], pool)
            up, down = flips(perm_h, H["G"][h_idx],
                             [H["qids"][i] for i in h_idx],
                             H["base_hit6"][h_idx], pool)
            holdout = {"path": str(hp), "applied": True, "mode": args.mode,
                       "pool": pool, "config": chosen["name"], "n": m_h["n"],
                       "extra_covered_on_holdout": h_extra_covered,
                       "baseline": m_hb, "policy": m_h,
                       "delta_hit6": round(m_h["hit6"] - m_hb["hit6"], 4),
                       "delta_mrr6": round(m_h["mrr6"] - m_hb["mrr6"], 4),
                       "gap_to_target": round(TARGET_HIT6 - m_h["hit6"], 4),
                       "up_qids": up, "down_qids": down}
            print(f"\n== Holdout（{hp.name}，{args.mode}，answerable "
                  f"n={m_h['n']}，pool={pool}）==")
            print(f"  基线 hit@6={m_hb['hit6']:.4f} → 策略 hit@6={m_h['hit6']:.4f}"
                  f"（Δ={holdout['delta_hit6']:+.4f}）  "
                  f"距目标 {TARGET_HIT6}：{holdout['gap_to_target']:+.4f}  "
                  f"up={len(up)} down={len(down)}")

            # ── C7：逐题证据层 + 分层报告（只增不改）──
            # 策略对**全部** kept 题打一遍（与 answerable 层同一配置；不可答题
            # gold 缺席，重排不可能造出命中，故其 base/pol 指标天然恒等）。
            perm_all = apply_policy(chosen["policy"], param_h,
                                    H["Z"] @ w_ch, pool)
            og_all = np.take_along_axis(H["G"], perm_all, axis=1)
            has_all = og_all.any(axis=1)
            first_all = og_all.argmax(axis=1)
            k10 = min(10, pool)
            ans_qids = {H["qids"][i] for i in h_idx}
            hrows = []
            for i, q in enumerate(H["qs"]):
                rb = q["stored_rank"]
                hrows.append({
                    "qid": q["qid"],
                    "stratum": (strata_map.get(q["qid"], "(missing)")
                                if strata_map else ""),
                    "hit6_base": rb is not None and rb <= K_MAIN,
                    "hit6_pol": bool(has_all[i] and first_all[i] < K_MAIN),
                    "hit10_base": rb is not None and rb <= k10,
                    "hit10_pol": bool(has_all[i] and first_all[i] < k10),
                    "rank_base": rb,
                    "rank_pol": (int(first_all[i]) + 1) if has_all[i] else None,
                })
            holdout["rows"] = hrows

            def agg_from_rows(rs: list[dict], rkey: str) -> dict:
                """从 rows 的 rank 列聚合 {n, hit6, hit10, mrr6, mrr10}。"""
                n = len(rs)
                if not n:
                    return {"n": 0}
                ranks = [r[rkey] for r in rs]
                out: dict = {"n": n}
                for name, k in (("hit6", K_MAIN), ("hit10", k10)):
                    out[name] = round(sum(1 for x in ranks
                                          if x is not None and x <= k) / n, 4)
                for name, k in (("mrr6", K_MAIN), ("mrr10", k10)):
                    out[name] = round(sum(1.0 / x for x in ranks
                                          if x is not None and x <= k) / n, 4)
                return out

            sub = [r for r in hrows if r["qid"] in ans_qids]
            b_rows = agg_from_rows(sub, "rank_base")
            p_rows = agg_from_rows(sub, "rank_pol")
            agg_ok = b_rows == m_hb and p_rows == m_h
            holdout["aggregate_check"] = {
                "pass": agg_ok, "population": "rows ∩ answerable",
                "baseline_from_rows": b_rows, "policy_from_rows": p_rows,
                "baseline_existing": m_hb, "policy_existing": m_h}
            agg_detail = "" if agg_ok else "FAIL " + json.dumps(
                {"base_rows": b_rows, "base_expected": m_hb,
                 "pol_rows": p_rows, "pol_expected": m_h}, ensure_ascii=False)
            print(f"  聚合自检（rows∩answerable vs 既有 holdout 指标，逐位）："
                  f"{'PASS' if agg_ok else agg_detail}")

            if strata_map:
                strata: dict[str, dict] = {}
                for sname in sorted({r["stratum"] for r in hrows}):
                    rs = [r for r in hrows if r["stratum"] == sname]
                    strata[sname] = {
                        "n": len(rs),
                        "n_answerable": sum(1 for r in rs
                                            if r["qid"] in ans_qids),
                        "baseline": agg_from_rows(rs, "rank_base"),
                        "policy": agg_from_rows(rs, "rank_pol"),
                        "up_qids": sorted(r["qid"] for r in rs
                                          if r["hit6_pol"] and not r["hit6_base"]),
                        "down_qids": sorted(r["qid"] for r in rs
                                            if r["hit6_base"] and not r["hit6_pol"]),
                    }
                holdout["strata"] = strata
                print(f"  分层（--holdout-strata，hit@6/hit@10 = 基线→策略）：")
                for sname, sv in strata.items():
                    b_, p_ = sv["baseline"], sv["policy"]
                    print(f"    {sname:10s} n={sv['n']:3d}  "
                          f"hit@6 {b_['hit6']:.4f}→{p_['hit6']:.4f}  "
                          f"hit@10 {b_['hit10']:.4f}→{p_['hit10']:.4f}  "
                          f"MRR@6 {b_['mrr6']:.4f}→{p_['mrr6']:.4f}  "
                          f"up={len(sv['up_qids'])} down={len(sv['down_qids'])}"
                          + (f" down_qids={sv['down_qids']}" if sv["down_qids"] else ""))
    else:
        holdout["note"] = "未提供 --holdout，泛化检查 pending"
        print("\n== Holdout == pending（未提供 --holdout）")

    # ── 时延（C8）──
    feat_ms = np.asarray(B["feat_ms"])
    reorder_ms = []
    param = chosen["params"].get(PARAM_KEY[chosen["policy"]], 0.0) \
        if chosen["params"] else 0.0
    for i in idx_ans[:200]:
        t0 = time.perf_counter()
        Ss = zscore_row(B["Z"][i:i + 1] @ w_ch)
        perm = apply_policy(chosen["policy"], param, Ss, pool)
        eval_perm(perm, B["G"][i:i + 1], pool)
        reorder_ms.append((time.perf_counter() - t0) * 1000.0)
    rm = np.asarray(reorder_ms)
    timings = {
        "feature_ms_mean": round(float(feat_ms.mean()), 3),
        "feature_ms_p95": round(float(np.percentile(feat_ms, 95)), 3),
        "reorder_ms_mean": round(float(rm.mean()), 3),
        "reorder_ms_p95": round(float(np.percentile(rm, 95)), 3),
    }
    print(f"\n== 时延/题（C8）== 特征 {timings['feature_ms_mean']}ms "
          f"(p95 {timings['feature_ms_p95']})  重排+评测 "
          f"{timings['reorder_ms_mean']}ms (p95 {timings['reorder_ms_p95']})")

    # ── 落盘 ──
    report = {
        "kind": "rank_rerank_lab",
        "version": 2,
        "notes": ["BLIND FEATURE RULE：特征只用 query/qvec/证据字段/块文本/"
                  "块向量/图谱度数/种子名/外部分数；eval_keywords 只进 ORACLE 与评测",
                  "boundary_promote/top1_thresh 的置换=槽6与胜者互换（多重集不变）",
                  "top1_thresh 用逐题 min-max 归一分（z 分数可负，比率无定义）",
                  "zfit 权重按 full_topN a=1 目标拟合，扫参时投给三个策略族",
                  "pool<10 时 hit@10 为下界（=hit@pool）",
                  f"弃用特征：{inactive or '无'}",
                  f"池不足被丢弃的题数：base={B['drop']}",
                  ] + ([f"extra 特征：{extra_note}"] if extra_note else []),
        "base": str(base_path), "holdout": args.holdout or "",
        "mode": args.mode, "pool": pool,
        "features": list(feats),
        "extra_features": {"given": bool(args.extra_features),
                           "applied": B["extra_applied"],
                           "missing_qids": B["extra_missing_qids"]},
        "target": {"line": TARGET_HIT6, "baseline_hit6": baseline["hit6"],
                   "best_blind_hit6": chosen["hit6"],
                   "delta_to_target": delta_target,
                   "oracle_ceiling_pool": ceil_pool, "oracle_gap": oracle_gap},
        "n_questions": n_all, "n_answerable": n_ans, "n_unanswerable": n_unans,
        "baseline": baseline, "configs": configs, "chosen": chosen,
        "oracle": oracle, "safety": safety, "ablation": ablation,
        "loo_cv": loo, "holdout": holdout, "timings": timings,
    }
    out_path = (Path(args.out) if args.out else
                ROOT / "data" / "compendium_rag" / "reports"
                / f"rank_rerank_lab_{tag}.json")
    if not out_path.is_absolute():
        out_path = ROOT / out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=1),
                        encoding="utf-8")
    print(f"\n报告 → {out_path}")

    verdict = ("盲配置胜出且安全 PASS" if beats and not safety["violation"]
               else "安全底线违反" if safety["violation"] else
               "无盲配置胜过基线（合法结论）")
    print(f"结论：{verdict}（chosen={chosen['name']} "
          f"hit@6 {baseline['hit6']} → {chosen['hit6']}；"
          f"距目标 {TARGET_HIT6} 还差 {delta_target:+.4f}）")
    if safety["violation"]:
        return 1
    return 0 if beats else 2


if __name__ == "__main__":
    sys.exit(main())
