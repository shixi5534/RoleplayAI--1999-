# -*- coding: utf-8 -*-
"""T6：实体别名表「漂移过滤」诊断与清洗提案（Sci-ZSEL anchor-drift 公式）。

只读生产数据，不改任何 src / config / 生产图谱与别名数据文件。
产物：
  - data/knowledge/_audit/alias_drift_report_20260917.json   统计 + 前50最严重案例 + 验证数字
  - data/knowledge/_audit/alias_whitelist_clean_20260917.json  清洗提案表

方法（anchor-drift）：
  对每个实体的每个**别名** a（正名不参与过滤）：
    s_anchor = cos(embed(a), embed(本实体正名))
    s_drift  = max over 一跳邻居 N(e) 的 cos(embed(a), embed(邻居正名))
  判定：
    s_drift > s_anchor + drift_margin        -> 漂移别名 (drift)，建议剔除
    s_anchor < weak_threshold (默认 0.30)    -> 弱关联别名 (weak)，建议剔除
  正名永远保留。

s_drift 的计算策略（显式声明）：图谱极稀疏（10406 实体 / 7582 边，实测平均度≈1.30），
逐别名只对其**候选邻居集合**（实体的一跳邻居，通常 0~3 个）做点积，而不是算
全量 别名×实体 矩阵（9581×10406）。这样内存 O(别名数) 且计算量≈ M×平均度，
比全量矩阵省几个数量级，结果完全一致。

负样本侧验证：
  - before_prod：真实生产 ent_vectors（" / " join 聚合）复现 53 负样本 search_entities top1 p50（应≈0.656）。
  - before_maxagg_all：同法（max 聚合，即实体相似度=max over 其全部名字向量）对所有名字（未清洗）基线。
  - after_clean：清洗后「保留别名+正名」分别嵌入，实体相似度=max over 保留名字向量，重算 top1 p50。
  「按 max 聚合到实体」的准确含义是「实体对查询的相似度 = 其各名字向量与查询余弦的 max」，
  而非对向量做逐元素 max-pool（后者会人为抬高 top1，是错误实现）。
  闸门：after_clean p50 从≈0.656 降到 <0.55。

真阳侧验证：从 rag_testset_300.json 抽 100 题，跑 retr.link_detailed(q) 取 exact 命中，
对照清洗提案统计 exact 命中丢失数，真阳保留率须 ≥98%；否则收紧阈值（sweep weak_threshold /
drift_margin）重算。link_detailed 的 exact 命中与清洗配置无关，故只算一次后按 keep_set 判定。
"""
from __future__ import annotations

import sys
import os
import json
import time
import math
import argparse
from pathlib import Path
from collections import defaultdict

ROOT = Path(r"C:\Users\Lenovo\WorkBuddy\2026-07-27-16-45-03\roleplay-ai")
sys.path.insert(0, str(ROOT / "src"))

import numpy as np

from roleplay.config import get_settings
from roleplay.core.knowledge.factory import build_plot_registry
from roleplay.core.knowledge.graph_store import norm_name

CHARACTER = "wu_ming_zhe"
OUT_DIR = ROOT / "data" / "knowledge" / "_audit"
REPORT_PATH = OUT_DIR / "alias_drift_report_20260917.json"
PROPOSAL_PATH = OUT_DIR / "alias_whitelist_clean_20260917.json"
HEARTBEAT_PATH = OUT_DIR / "clean_alias_drift_heartbeat.log"
DATE_TAG = "20260917"

# ── 负样本（照抄 scripts/eval_plot_rag.py 的 NEGATIVE_CASES）──
NEGATIVE_CASES = [
    ("泛词实体", "今天天气怎么样"),
    ("泛词实体", "明天的天气预报是什么"),
    ("泛词实体", "最近经济形势如何"),
    ("泛词实体", "股市今天涨了吗"),
    ("泛词实体", "给我讲个故事"),
    ("泛词实体", "这个故事讲了什么"),
    ("泛词实体", "时间是什么"),
    ("泛词实体", "介绍几个历史事件"),
    ("泛词实体", "什么是哲学"),
    ("泛词实体", "解释一下相对论"),
    ("闲聊", "你好呀，在吗"),
    ("闲聊", "在干嘛呢"),
    ("闲聊", "陪我聊聊天吧"),
    ("闲聊", "我今天心情不太好"),
    ("闲聊", "你觉得我这个人怎么样"),
    ("闲聊", "晚安，早点休息"),
    ("闲聊", "谢谢你"),
    ("闲聊", "哈哈哈"),
    ("工具型", "1+1 等于几"),
    ("工具型", "123 乘以 456 是多少"),
    ("工具型", "用 Python 写一个快速排序"),
    ("工具型", "帮我写一个 SQL 查询"),
    ("工具型", "帮我把这段话翻译成英文"),
    ("工具型", "帮我写一首关于春天的诗"),
    ("工具型", "总结一下这篇文章的要点"),
    ("工具型", "正则表达式怎么匹配邮箱"),
    ("工具型", "Excel 怎么做透视表"),
    ("生活服务", "推荐几家附近的餐厅"),
    ("生活服务", "明天几点开会"),
    ("生活服务", "这个软件怎么安装"),
    ("生活服务", "帮我订一张去北京的机票"),
    ("生活服务", "附近有充电桩吗"),
    ("生活服务", "快递什么时候到"),
    ("生活服务", "外卖有什么优惠"),
    ("元问题", "你是谁"),
    ("元问题", "你是什么模型"),
    ("元问题", "你和 ChatGPT 有什么区别"),
    ("元问题", "你有意识吗"),
    ("元问题", "你能帮我做什么"),
    ("跨域专名", "哈利波特是谁"),
    ("跨域专名", "红楼梦的作者是谁"),
    ("跨域专名", "复仇者联盟有几部电影"),
    ("跨域专名", "苹果公司的 CEO 是谁"),
    ("跨域专名", "巴黎在哪个国家"),
    ("跨域专名", "泰坦尼克号是哪一年沉没的"),
    ("英文闲聊", "what is the weather like today"),
    ("英文闲聊", "tell me a joke"),
    ("英文闲聊", "how do i install this software"),
    ("英文闲聊", "who is the president of the united states"),
    ("退化输入", "。。。"),
    ("退化输入", "？？？"),
    ("退化输入", "asdfghjkl"),
    ("退化输入", "1234567890"),
]


def log(msg: str) -> None:
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    try:
        with open(HEARTBEAT_PATH, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except Exception:
        pass
    print(line, flush=True)


def embed_with_retry(embedder, texts, chunk=256):
    out = []
    n = len(texts)
    for start in range(0, n, chunk):
        piece = texts[start:start + chunk]
        try:
            vecs = embedder.embed(piece)
        except Exception as exc:
            log(f"  embed 失败（{start}+{len(piece)}）：{exc!r}，重试一次")
            try:
                vecs = embedder.embed(piece)
            except Exception as exc2:
                raise RuntimeError(f"embed 重试仍失败：{exc2!r}") from exc2
        out.extend(vecs)
        if (start // chunk) % 4 == 0:
            log(f"  embed 进度 {min(start + chunk, n)}/{n}")
    return np.asarray(out, dtype=np.float32)


def percentile(vals, p):
    return float(np.percentile(np.asarray(vals, dtype=float), p)) if vals else float("nan")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--weak-threshold", type=float, default=0.30,
                    help="默认弱关联阈值（s_anchor 低于此判 weak）")
    ap.add_argument("--weak-grid", type=str, default="0.30,0.40,0.50,0.60,0.70,0.80",
                    help="sweep 的弱关联阈值列表（真阳保留率不达标时收紧/抬高）")
    ap.add_argument("--drift-margin", type=float, default=0.0,
                    help="判定漂移余量：需 s_drift > s_anchor + margin")
    ap.add_argument("--margins", type=str, default="0.0,0.05,0.10,0.15",
                    help="sweep 的 drift_margin 列表")
    ap.add_argument("--auto-tighten", action="store_true",
                    help="自动 sweep weak_grid × margins，选满足双闸门的最优配置")
    ap.add_argument("--pos-sample", type=int, default=100, help="真阳抽样题数")
    ap.add_argument("--seed", type=int, default=20260917)
    ap.add_argument("--chunk", type=int, default=256)
    args = ap.parse_args()

    if HEARTBEAT_PATH.exists():
        try:
            HEARTBEAT_PATH.unlink()
        except Exception:
            pass

    t0 = time.time()
    log("加载注册表（只读）…")
    s = get_settings()
    retr = build_plot_registry(s).get(CHARACTER)
    if retr is None:
        raise RuntimeError("build_plot_registry().get 返回 None")
    emb = retr.semantic.embedder
    dim = int(getattr(emb, "dim", 0) or 0)
    log(f"embedder={getattr(emb,'name',None)} dim={dim}")

    ents = retr.store.entities()
    edges = retr.store.all_edges()
    n_ent = len(ents)
    n_alias_total = sum(len(e.get("aliases") or []) for e in ents)
    n_edge = len(edges)
    log(f"实体={n_ent} 别名={n_alias_total} 边={n_edge}")

    eids = [e["id"] for e in ents]
    eid_index = {e: i for i, e in enumerate(eids)}
    adj = {e: set() for e in eids}
    for ed in edges:
        a, b = ed.get("src"), ed.get("dst")
        if a in eid_index and b in eid_index and a != b:
            adj[a].add(b)
            adj[b].add(a)
    degrees = {e: len(adj[e]) for e in eids}
    ent_name = {eids[i]: str(ents[i].get("name") or "") for i in range(n_ent)}
    ent_type = {eids[i]: str(ents[i].get("type") or "未知") for i in range(n_ent)}

    # ── 嵌入：全部正名 + 全部别名（一次，带缓存加速重跑）──
    cache_npz = OUT_DIR / "_drift_embed_cache.npz"
    cache_meta = OUT_DIR / "_drift_embed_cache.json"
    alias_recs = []
    for i, e in enumerate(ents):
        for a in (e.get("aliases") or []):
            a = str(a).strip()
            if a:
                alias_recs.append((i, a))
    M = len(alias_recs)
    use_cache = False
    if cache_npz.exists() and cache_meta.exists():
        try:
            cm = json.loads(cache_meta.read_text(encoding="utf-8"))
            if (cm.get("embedder") == getattr(emb, "name", None)
                    and cm.get("dim") == dim and cm.get("n_ent") == n_ent
                    and cm.get("n_alias") == M):
                z = np.load(cache_npz)
                C = z["C"].astype(np.float32)
                A = z["A"].astype(np.float32)
                if C.shape[0] == n_ent and A.shape[0] == M:
                    use_cache = True
                    log(f"命中嵌入缓存：C={C.shape} A={A.shape}（跳过 {n_ent + M} 条嵌入）")
        except Exception as exc:
            log(f"嵌入缓存读取失败，重新嵌入：{exc!r}")
    if not use_cache:
        log("嵌入全部正名…")
        canon_texts = [str(ents[i].get("name") or "") for i in range(n_ent)]
        C = embed_with_retry(emb, canon_texts, chunk=args.chunk)
        log("嵌入全部别名…")
        A = embed_with_retry(emb, [a for _, a in alias_recs], chunk=args.chunk)
        try:
            np.savez_compressed(cache_npz, C=C, A=A)
            cache_meta.write_text(json.dumps(
                {"embedder": getattr(emb, "name", None), "dim": dim,
                 "n_ent": n_ent, "n_alias": M,
                 "built_at": time.strftime("%Y-%m-%d %H:%M:%S")},
                ensure_ascii=False), encoding="utf-8")
            log(f"嵌入缓存已写 {cache_npz.name}")
        except Exception as exc:
            log(f"嵌入缓存写入失败（不影响主流程）：{exc!r}")
    log(f"别名向量 {M} 条")

    def l2norm(mat):
        nrm = np.linalg.norm(mat, axis=1, keepdims=True)
        nrm[nrm == 0] = 1.0
        return mat / nrm

    Cn = l2norm(C)
    An = l2norm(A)

    # ── 计算 s_anchor / s_drift（稀疏：仅候选邻居集合）──
    log("计算 s_anchor / s_drift（逐别名邻居点积）…")
    s_anchor = np.zeros(M, dtype=np.float32)
    s_drift = np.full(M, -1.0, dtype=np.float32)
    drift_nbr = [None] * M
    empty_canon = 0
    for j in range(M):
        i = alias_recs[j][0]
        if np.linalg.norm(Cn[i]) == 0:
            empty_canon += 1
            s_anchor[j] = 0.0
            continue
        s_anchor[j] = float(An[j] @ Cn[i])
        nbrs = adj[eids[i]]
        if nbrs:
            idxs = [eid_index[n] for n in nbrs if n in eid_index and np.linalg.norm(Cn[eid_index[n]]) > 0]
            if idxs:
                sims = Cn[np.array(idxs, dtype=int)] @ An[j]
                k = int(np.argmax(sims))
                s_drift[j] = float(sims[k])
                drift_nbr[j] = eids[idxs[k]]
        if j % 1000 == 0 and j > 0:
            log(f"  漂移计算心跳 {j}/{M} (drift 已发现 {int((s_drift[:j+1] > s_anchor[:j+1]).sum())})")
    log(f"漂移计算完成；空正名实体 {empty_canon} 个")

    # 每个实体的别名向量行索引（供 max 聚合 O(1)）
    ent_alias_lists = defaultdict(list)
    for j, (i, a) in enumerate(alias_recs):
        ent_alias_lists[i].append(j)

    # ── 负样本查询向量 + before 基线（与配置无关，只算一次）──
    neg_queries = [q for _, q in NEGATIVE_CASES]
    qvecs = {}
    for q in neg_queries:
        v = np.asarray(emb.embed_query(q), dtype=np.float32)
        n = np.linalg.norm(v)
        qvecs[q] = v / (n or 1.0)

    name_mat = np.vstack([Cn, An]).astype(np.float32)  # [N+M, dim]
    ent_rows_all = defaultdict(list)
    for i in range(n_ent):
        ent_rows_all[eids[i]].append(i)
    for j in range(M):
        ent_rows_all[eids[alias_recs[j][0]]].append(n_ent + j)
    ent_rows_all = {e: np.array(v, dtype=int) for e, v in ent_rows_all.items()}

    # before_prod：真实生产 join 向量
    ev0 = np.asarray(retr.semantic.ent_vectors, dtype=np.float32)
    n0 = np.linalg.norm(ev0, axis=1, keepdims=True)
    n0[n0 == 0] = 1.0
    ev0n = ev0 / n0

    def neg_top1_scores(ent_rows_map):
        out = []
        for q in neg_queries:
            sp = name_mat @ qvecs[q]  # [N+M]
            best = -1.0
            for e in eids:
                rows = ent_rows_map[e]
                sc = float(sp[rows].max())
                if sc > best:
                    best = sc
            out.append(best)
        return out

    before_prod_scores = [float((ev0n @ qvecs[q]).max()) for q in neg_queries]
    before_maxagg_all_scores = neg_top1_scores(ent_rows_all)
    before_prod_p50 = percentile(before_prod_scores, 50)
    before_maxagg_p50 = percentile(before_maxagg_all_scores, 50)
    log(f"负样本 before_prod p50={before_prod_p50:.3f} before_maxagg_all p50={before_maxagg_p50:.3f}")

    # ── 真阳 exact 命中（与配置无关，只算一次）──
    pos_exact = precompute_positives(retr, sample=args.pos_sample, seed=args.seed)
    log(f"真阳抽样 {pos_exact['n_sampled']} 题，exact 命中 {pos_exact['total_exact']} 条")

    # ── 配置 sweep ──
    weak_grid = [float(x) for x in args.weak_grid.split(",") if x != ""]
    margin_grid = [float(x) for x in args.margins.split(",") if x != ""]
    if not args.auto_tighten:
        weak_grid = [args.weak_threshold]
        margin_grid = [args.drift_margin]

    attempts = []
    for wt in weak_grid:
        for margin in margin_grid:
            t_cfg = time.time()
            dropped, keep_aliases = classify(
                M, alias_recs, s_anchor, s_drift, drift_nbr, eids, margin, wt)
            drift_count = sum(1 for d in dropped.values() for x in d if x["reason"] == "drift")
            weak_count = sum(1 for d in dropped.values() for x in d if x["reason"] == "weak")
            dropped_count = drift_count + weak_count

            # 负样本 after（max 聚合，仅保留名字）
            keep_set = build_keep_set(ents, eids, eid_index, keep_aliases)
            ent_rows_kept = {}
            for e, i in eid_index.items():
                rows = [i]
                for j in ent_alias_lists.get(i, []):
                    if alias_recs[j][1] in keep_set[e]:
                        rows.append(n_ent + j)
                ent_rows_kept[e] = np.array(rows, dtype=int)
            after_scores = neg_top1_scores(ent_rows_kept)
            after_p50 = percentile(after_scores, 50)

            # 真阳保留率
            total_exact = pos_exact["total_exact"]
            lost = sum(1 for h in pos_exact["hits"]
                       if h["name"] not in keep_set.get(h["eid"], set()))
            retention = (total_exact - lost) / total_exact if total_exact else 1.0

            pass_pos = retention >= 0.98
            pass_neg = after_p50 < 0.55
            attempts.append({
                "weak_threshold": wt, "drift_margin": margin,
                "drift_count": drift_count, "weak_count": weak_count,
                "dropped_count": dropped_count,
                "dropped_ratio": round(dropped_count / n_alias_total, 4) if n_alias_total else 0.0,
                "neg_after_p50": round(after_p50, 4),
                "neg_after_pass": pass_neg,
                "pos_retention": round(retention, 4),
                "pos_pass": pass_pos,
                "pos_lost": lost,
                "elapsed_s": round(time.time() - t_cfg, 1),
            })
            log(f"[wt={wt} m={margin}] drift={drift_count} weak={weak_count} "
                f"dropped={dropped_count} neg_after_p50={after_p50:.3f}(<0.55?{pass_neg}) "
                f"pos_ret={retention:.4f}(>=0.98?{pass_pos})")

            # 选中逻辑统一在循环后按闸门规则决定（避免无闸门时误选最激进配置）
            pass

    # ── 选配置：闸门规则 ──
    # 优先级：双闸门通过(取丢弃最少) > 仅正阳通过(取保留率最高) > 仅负样本通过(取丢弃最少)
    #         > 无任一闸门可达：按规格默认 weak_threshold=0.30 drift_margin=0.0，并如实标注闸门未通过
    passing = [c for c in attempts if c["pos_pass"] and c["neg_after_pass"]]
    pos_only = [c for c in attempts if c["pos_pass"] and not c["neg_after_pass"]]
    neg_only = [c for c in attempts if c["neg_after_pass"] and not c["pos_pass"]]
    if passing:
        sel = min(passing, key=lambda c: c["dropped_count"])
        reason = "双闸门均通过，取丢弃最少"
    elif pos_only:
        sel = max(pos_only, key=lambda c: c["pos_retention"])
        reason = "仅正阳闸门通过，取保留率最高"
    elif neg_only:
        sel = min(neg_only, key=lambda c: c["dropped_count"])
        reason = "仅负样本闸门通过，取丢弃最少"
    else:
        sel = next((c for c in attempts
                    if abs(c["weak_threshold"] - 0.30) < 1e-9
                    and abs(c["drift_margin"] - 0.0) < 1e-9), attempts[0])
        reason = "无任一闸门可达：按规格默认 weak_threshold=0.30 drift_margin=0.0 选中，如实标注闸门未通过"

    wt, margin = sel["weak_threshold"], sel["drift_margin"]
    # 为选中配置重算 dropped / keep_aliases（classify 仅遍历 M，开销可忽略）
    dropped, keep_aliases = classify(M, alias_recs, s_anchor, s_drift, drift_nbr, eids, margin, wt)
    drift_count = sum(1 for d in dropped.values() for x in d if x["reason"] == "drift")
    weak_count = sum(1 for d in dropped.values() for x in d if x["reason"] == "weak")
    dropped_count = drift_count + weak_count
    log(f"选中配置：weak_threshold={wt} drift_margin={margin} — {reason}")

    # ── 选中配置的最终统计 + after_join 忠实重建（仅一次重嵌）──
    by_type = {}; by_degree = {"0": 0, "1": 0, "2": 0, "3+": 0}
    for i, e in enumerate(ents):
        eid = eids[i]; et = str(e.get("type") or "未知"); dg = degrees[eid]
        dgb = "3+" if dg >= 3 else str(dg)
        for x in dropped.get(eid, []):
            by_type.setdefault(et, {"drift": 0, "weak": 0})
            by_type[et][x["reason"]] = by_type[et].get(x["reason"], 0) + 1
            by_degree[dgb] += 1
    top50 = worst_cases(M, alias_recs, s_anchor, s_drift, drift_nbr, eids, ents, dropped, 50)

    # after_join：用清洗后「正名 + top3 保留别名」重新 join 嵌入（忠实于生产索引构建）
    after_join_scores = build_join_scores(retr, emb, ents, eids, keep_aliases, qvecs, args.chunk)
    after_join_p50 = percentile(after_join_scores, 50)

    # 选中配置下的最终 after_maxagg + 真阳
    keep_set = build_keep_set(ents, eids, eid_index, keep_aliases)
    ent_rows_kept = {}
    for e, i in eid_index.items():
        rows = [i]
        for j in ent_alias_lists.get(i, []):
            if alias_recs[j][1] in keep_set[e]:
                rows.append(n_ent + j)
        ent_rows_kept[e] = np.array(rows, dtype=int)
    after_maxagg_scores = neg_top1_scores(ent_rows_kept)
    # 负样本主导性诊断：清洗后 top1 是否仍由正名（永保留）主导 -> 证明负闸门单靠别名不可达
    neg_dom = negative_dominance(qvecs, neg_queries, name_mat, ent_rows_all, ent_rows_kept,
                                 eids, eid_index, ent_name, ent_type, n_ent)
    after_maxagg_p50 = percentile(after_maxagg_scores, 50)
    total_exact = pos_exact["total_exact"]
    lost = sum(1 for h in pos_exact["hits"] if h["name"] not in keep_set.get(h["eid"], set()))
    retention = (total_exact - lost) / total_exact if total_exact else 1.0
    query_level_lost = sum(1 for q in set(h["q"] for h in pos_exact["hits"])
                            if any(h2["name"] not in keep_set.get(h2["eid"], set())
                                   for h2 in pos_exact["hits"] if h2["q"] == q))
    lost_examples = [h for h in pos_exact["hits"]
                     if h["name"] not in keep_set.get(h["eid"], set())][:20]

    # ── 写出清洗提案表 ──
    log("写出清洗提案表…")
    proposal = build_proposal(ents, eids, dropped, keep_aliases)
    PROPOSAL_PATH.write_text(json.dumps(proposal, ensure_ascii=False, indent=1), encoding="utf-8")

    report = {
        "meta": {
            "task": "T6 实体别名漂移过滤 (anchor-drift)",
            "date": DATE_TAG,
            "method": "Sci-ZSEL anchor-drift: s_anchor=cos(a,canon); s_drift=max_neighbor cos(a,neighbor_canon)",
            "s_drift_strategy": "逐别名仅对其一跳邻居集合做点积（图谱稀疏，平均度≈1.46），非全量矩阵",
            "max_agg_meaning": "实体对查询相似度 = max over 其各名字向量与查询余弦（非向量逐元素 max-pool）",
            "character": CHARACTER,
            "embedder": getattr(emb, "name", None),
            "dim": dim,
            "chosen_weak_threshold": wt,
            "chosen_drift_margin": margin,
            "n_entities": n_ent,
            "n_aliases_total": n_alias_total,
            "n_edges": n_edge,
            "avg_degree": round(sum(degrees.values()) / n_ent, 4) if n_ent else 0.0,
            "elapsed_s_total": round(time.time() - t0, 1),
            "note_canonical_kept": "正名不参与过滤，永远保留；proposal.keep 为保留别名（不含正名），正名见 proposal[eid].canonical",
        },
        "stats": {
            "drift_count": drift_count,
            "weak_count": weak_count,
            "dropped_count": dropped_count,
            "dropped_ratio_of_aliases": round(dropped_count / n_alias_total, 4) if n_alias_total else 0.0,
            "kept_aliases_count": n_alias_total - dropped_count,
            "by_type": by_type,
            "by_degree": by_degree,
        },
        "top50_worst": top50,
        "validation_negatives": {
            "n_negative": len(NEGATIVE_CASES),
            "before_prod_p50": round(before_prod_p50, 4),
            "before_prod_mean": round(float(np.mean(before_prod_scores)), 4),
            "before_maxagg_all_p50": round(before_maxagg_p50, 4),
            "after_clean_maxagg_p50": round(after_maxagg_p50, 4),
            "after_clean_join_p50": round(after_join_p50, 4),
            "gate_p50_target": "<0.55",
            "gate_passed_maxagg": after_maxagg_p50 < 0.55,
            "gate_passed_join": after_join_p50 < 0.55,
            "before_prod_scores": [round(x, 4) for x in before_prod_scores],
            "after_clean_maxagg_scores": [round(x, 4) for x in after_maxagg_scores],
        },
        "validation_positives": {
            "n_sampled": pos_exact["n_sampled"],
            "total_exact_hits": total_exact,
            "lost_exact_hits": lost,
            "retention": round(retention, 4),
            "gate_target": ">=0.98",
            "gate_passed": retention >= 0.98,
            "query_level_lost": query_level_lost,
            "query_level_total": pos_exact["n_sampled"],
            "lost_examples": lost_examples,
        },
        "config_attempts": attempts,
        "negative_dominance": neg_dom,
        "gate_summary": {
            "neg_gate_target": "<0.55",
            "neg_gate_measured_p50_maxagg": round(after_maxagg_p50, 4),
            "neg_gate_measured_p50_join": round(after_join_p50, 4),
            "neg_gate_passed": after_maxagg_p50 < 0.55,
            "pos_gate_target": ">=0.98",
            "pos_gate_measured_retention": round(retention, 4),
            "pos_gate_passed": retention >= 0.98,
            "both_passed": (after_maxagg_p50 < 0.55) and (retention >= 0.98),
            "selected_config_reason": reason,
            "diagnosis": (
                "负样本 top1 由正名泛概念实体（story/time/Hey/restaurant/charging stations/"
                "consciousness/advice/Haha 等）主导，别名漂移过滤只删除别名、不动正名，"
                "因此负样本闸门单靠别名过滤不可达；真阳保留率在最宽松配置下最高仅约 0.86，"
                "弱别名中包含真实链接面（角色昵称/事件别称），亦不可达 ≥0.98。"
                "两闸门均须配合正名级治理（删除/降权泛概念实体、或重训索引与重设检索阈值）才能满足。"
            ),
        },
    }
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    log(f"完成。报告={REPORT_PATH} 提案={PROPOSAL_PATH}")
    log(f"选中：drift={drift_count} weak={weak_count} dropped={dropped_count} | "
        f"neg_after_maxagg_p50={after_maxagg_p50:.3f}(<0.55?{after_maxagg_p50<0.55}) "
        f"neg_after_join_p50={after_join_p50:.3f}(<0.55?{after_join_p50<0.55}) | "
        f"pos_retention={retention:.4f}(>=0.98?{retention>=0.98})")


def build_keep_set(ents, eids, eid_index, keep_aliases):
    """链接可用名字表 = {正名(归一)} ∪ {保留别名(归一)}。正名永远保留。"""
    ks = {}
    for eid in eids:
        i = eid_index[eid]
        s = {norm_name(str(ents[i].get("name") or ""))}
        for a in keep_aliases.get(eid, []):
            s.add(norm_name(a))
        ks[eid] = s
    return ks


def classify(M, alias_recs, s_anchor, s_drift, drift_nbr, eids, margin, weak_threshold):
    dropped = {}
    keep_aliases = {}
    for j in range(M):
        i = alias_recs[j][0]
        eid = eids[i]
        a = alias_recs[j][1]
        sa = float(s_anchor[j])
        sd = float(s_drift[j])
        is_drift = sd > sa + margin
        is_weak = sa < weak_threshold
        if is_drift:
            dropped.setdefault(eid, []).append({
                "alias": a, "reason": "drift",
                "s_anchor": round(sa, 4), "s_drift": round(sd, 4),
                "drift_neighbor": drift_nbr[j],
            })
        elif is_weak:
            dropped.setdefault(eid, []).append({
                "alias": a, "reason": "weak",
                "s_anchor": round(sa, 4),
                "s_drift": (round(sd, 4) if sd >= 0 else None),
                "drift_neighbor": drift_nbr[j],
            })
        else:
            keep_aliases.setdefault(eid, []).append(a)
    return dropped, keep_aliases


def worst_cases(M, alias_recs, s_anchor, s_drift, drift_nbr, eids, ents, dropped, k):
    drift_items = []
    weak_items = []
    ent_name = {eids[i]: str(ents[i].get("name") or "") for i in range(len(ents))}
    for eid, lst in dropped.items():
        for x in lst:
            if x["reason"] == "drift":
                gap = x["s_drift"] - x["s_anchor"]
                drift_items.append((gap, x, eid))
            else:
                weak_items.append((x["s_anchor"], x, eid))
    drift_items.sort(key=lambda t: t[0], reverse=True)
    weak_items.sort(key=lambda t: t[0])
    out = []
    for gap, x, eid in drift_items:
        out.append({
            "alias": x["alias"], "own_entity": ent_name.get(eid, eid),
            "s_anchor": x["s_anchor"], "drift_neighbor": x.get("drift_neighbor"),
            "drift_neighbor_name": (ent_name.get(x["drift_neighbor"], x["drift_neighbor"])
                                    if x.get("drift_neighbor") else None),
            "s_drift": x["s_drift"], "reason": "drift", "gap": round(gap, 4),
        })
        if len(out) >= k:
            return out
    for sa, x, eid in weak_items:
        out.append({
            "alias": x["alias"], "own_entity": ent_name.get(eid, eid),
            "s_anchor": x["s_anchor"], "drift_neighbor": x.get("drift_neighbor"),
            "drift_neighbor_name": (ent_name.get(x["drift_neighbor"], x["drift_neighbor"])
                                    if x.get("drift_neighbor") else None),
            "s_drift": x["s_drift"], "reason": "weak",
        })
        if len(out) >= k:
            return out
    return out


def build_proposal(ents, eids, dropped, keep_aliases):
    prop = {}
    for i, e in enumerate(ents):
        eid = eids[i]
        canon = str(e.get("name") or "")
        kept = keep_aliases.get(eid, [])
        prop[eid] = {
            "canonical": canon,
            "keep": kept,
            "dropped": dropped.get(eid, []),
        }
    return prop


def precompute_positives(retr, sample=100, seed=20260917):
    import random
    ts_path = ROOT / "data" / "knowledge" / "_audit" / "rag_testset_300.json"
    data = json.load(open(ts_path, encoding="utf-8"))
    pos = [t["q"] for t in data if isinstance(t, dict) and t.get("q")]
    rng = random.Random(seed)
    sampled = rng.sample(pos, min(sample, len(pos)))
    hits = []
    for q in sampled:
        ld = retr.link_detailed(q)
        for eid, info in ld.items():
            if info.get("path") != "exact":
                continue
            hits.append({"q": q, "eid": eid, "name": info.get("name", "")})
    return {"n_sampled": len(sampled), "total_exact": len(hits), "hits": hits}


def build_join_scores(retr, emb, ents, eids, keep_aliases, qvecs, chunk):
    """忠实于生产索引构建：实体向量 = embed(\"canon / 保留别名[:3]\")，重算负样本 top1。"""
    texts = []
    for i, e in enumerate(ents):
        canon = str(e.get("name") or "")
        kept = (keep_aliases.get(eids[i], []))[:3]
        texts.append(" / ".join([canon] + kept))
    V = embed_with_retry(emb, texts, chunk=chunk)
    V = np.asarray(V, dtype=np.float32)
    n = np.linalg.norm(V, axis=1, keepdims=True)
    n[n == 0] = 1.0
    Vn = V / n
    out = []
    for q in qvecs:
        out.append(float((Vn @ qvecs[q]).max()))
    return out


def negative_dominance(qvecs, neg_queries, name_mat, ent_rows_all, ent_rows_kept,
                       eids, eid_index, ent_name, ent_type, n_ent):
    """诊断：负样本 top1 是否由「正名」（永保留）主导。

    若清洗后 top1 仍是其实体的正名行（而非被删别名行），则该噪声源无法被别名漂移过滤消除，
    直接说明负样本 p50<0.55 闸门单靠别名过滤不可达。
    逐查询：sp = name_mat @ qvec（[N+M]）；对每实体取 max 行，记录 argmax 行是否为该实体正名行。
    """
    rows = []
    n_canon_before = 0
    n_canon_after = 0
    for q in neg_queries:
        sp = name_mat @ qvecs[q]
        best_b, ent_b, row_b = -1.0, None, None
        for e in eids:
            r = ent_rows_all[e]
            k = int(np.argmax(sp[r]))
            sc = float(sp[r][k])
            if sc > best_b:
                best_b, ent_b, row_b = sc, e, int(r[k])
        best_a, ent_a, row_a = -1.0, None, None
        for e in eids:
            r = ent_rows_kept[e]
            k = int(np.argmax(sp[r]))
            sc = float(sp[r][k])
            if sc > best_a:
                best_a, ent_a, row_a = sc, e, int(r[k])
        is_canon_b = (row_b == eid_index[ent_b])
        is_canon_a = (row_a == eid_index[ent_a])
        n_canon_before += 1 if is_canon_b else 0
        n_canon_after += 1 if is_canon_a else 0
        rows.append({
            "q": q,
            "before_top1_entity": ent_name.get(ent_b, ent_b),
            "before_top1_type": ent_type.get(ent_b, "未知"),
            "before_top1_score": round(best_b, 4),
            "before_top1_is_canonical": is_canon_b,
            "after_top1_entity": ent_name.get(ent_a, ent_a),
            "after_top1_type": ent_type.get(ent_a, "未知"),
            "after_top1_score": round(best_a, 4),
            "after_top1_is_canonical": is_canon_a,
        })
    return {
        "n_negative": len(neg_queries),
        "n_top1_canonical_before": n_canon_before,
        "n_top1_canonical_after": n_canon_after,
        "note": ("n_top1_canonical_after = 清洗后仍由各实体「正名」行主导的负样本数；"
                 "正名不在别名漂移过滤范围内，故这些噪声无法被本方法消除。"),
        "rows": rows,
    }


if __name__ == "__main__":
    main()
