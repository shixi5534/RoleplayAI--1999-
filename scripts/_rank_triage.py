# -*- coding: utf-8 -*-
"""排序实验 · 未命中归因分诊（rank_triage）。

对 rank_collect 产物做 k=6 未命中归因（默认 full / answerable 层），
纯离线、零网关：只加载库（图谱 + 块文本）与采集文件，不跑检索、不嵌。

分诊口径（对每道 miss，扫**全库**块 blob 找 eval_keywords；blob 与
eval300.score_case 逐字同构：``f"{text}\\n{chapter_title}\\n{scene_title}\\n{part_title}"``）：
  (i)  pooled_in_window   关键词块就在采集证据池里 → 记最小名次
                          （应与采集 rank 一致，自动交叉核对）；
  (ii) corpus_not_pooled  语料里存在关键词块但没进池 → 记 seed_hit、
                          语料关键词块总数、以及"任一关键词块是否与任一
                          池内块共享图实体"（entity.chunk_ids 反查，桥接可及=说明
                          池子/召回面的问题，桥接不可及=图覆盖问题）；
  (iii) no_corpus_match   全库没有任何块含关键词 → **按 answerable 规则
                          必须为 0**。若非 0，大声报告并自动排查不对称：
                          eval300 的 answerable 用**纯正文**语料串
                          （"\\n".join(c.text)），而打分 blob 含篇名——
                          重点核查"关键词只活在篇名里"的案例。

附带全库诊断：title_only 关键词（只出现在篇名、正文没有）——它们会让
规则把语义可答的题判成 unanswerable，列清单供口径修订参考。

用法（项目根目录）：
  ./.venv/Scripts/python.exe scripts/_rank_triage.py \
      --collect data/compendium_rag/reports/rank_collect_300_cn_top30.json
  冒烟：
  ./.venv/Scripts/python.exe scripts/_rank_triage.py \
      --collect data/compendium_rag/reports/rank_collect_smoke_f_top20.json

退出码：0=分诊完成且 (iii)=0（answerable 规则自洽）；
        1=(iii)>0（规则不自洽，需要人工排查）；2=输入不合法。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from compendium_rag import pipeline as P  # noqa: E402
from compendium_rag.config import get_settings  # noqa: E402

K_MAIN = 6


def blob_of(c) -> str:
    """与 eval300.score_case 逐字同构的 blob。"""
    return f"{c.text}\n{c.chapter_title}\n{c.scene_title}\n{c.part_title}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--collect", required=True, help="rank_collect json")
    ap.add_argument("--mode", default="full", choices=["full", "graph_only"])
    ap.add_argument("--limit", type=int, default=0, help="只分诊前 N 道 miss（调试）")
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    cp = Path(args.collect)
    cp = cp if cp.is_absolute() else ROOT / cp
    d = json.loads(cp.read_text(encoding="utf-8"))
    rows = [r for r in d.get("rows", []) if r.get("mode") == args.mode]
    if not rows:
        print(f"[FAIL] {cp.name} 里没有 mode={args.mode} 的行")
        return 2
    kb = P.load_kb(get_settings())
    tag = d.get("tag") or cp.stem.replace("rank_collect_", "")

    # ── 一次建索引：kw → 块列表（blob 口径与正文口径各一份）──
    kws_all = sorted({k for r in rows for k in r["eval_keywords"]})
    kw2blob: dict[str, list[str]] = {}
    kw2text: dict[str, list[str]] = {}
    for c in kb.chunks:
        cid = c.chunk_id
        b = blob_of(c)
        t = c.text
        for kw in kws_all:
            if kw in b:
                kw2blob.setdefault(kw, []).append(cid)
            if kw in t:
                kw2text.setdefault(kw, []).append(cid)

    # ── chunk → 实体集合（桥接判定用）──
    ent_sets: dict[str, set] = {}
    for eid, ent in kb.graph.entities.items():
        for cid in ent.chunk_ids:
            ent_sets.setdefault(cid, set()).add(eid)

    def bridge(matched: list[str], pool_ids: list[str]) -> bool:
        for kc in matched:
            ek = ent_sets.get(kc)
            if not ek:
                continue
            for pc in pool_ids:
                if ek & ent_sets.get(pc, set()):
                    return True
        return False

    # ── 分诊 answerable 的 k=6 misses ──
    misses = [r for r in rows if r.get("answerable")
              and (r["rank"] is None or r["rank"] > K_MAIN)]
    if args.limit:
        misses = misses[:args.limit]
    per_miss: list[dict] = []
    counts = {"pooled_in_window": 0, "corpus_not_pooled": 0, "no_corpus_match": 0}
    rank_mismatch: list[str] = []
    bridge_count = 0
    for r in misses:
        pool_ids = [e["chunk_id"] for e in r["evidence"]]
        pool_rank = {cid: i + 1 for i, cid in enumerate(pool_ids)}
        matched = sorted({cid for kw in r["eval_keywords"]
                          for cid in kw2blob.get(kw, [])})
        pooled = [pool_rank[cid] for cid in matched if cid in pool_rank]
        rec: dict = {"qid": r["qid"], "query": r["query"],
                     "stored_rank": r["rank"], "seed_hit": r.get("seed_hit"),
                     "n_eval_keywords": len(r["eval_keywords"])}
        if pooled:
            counts["pooled_in_window"] += 1
            mr = min(pooled)
            if r["rank"] is not None and mr != r["rank"]:
                rank_mismatch.append(r["qid"])
            rec.update({"class": "pooled_in_window", "min_pooled_rank": mr,
                        "n_corpus_keyword_chunks": len(matched)})
        elif matched:
            counts["corpus_not_pooled"] += 1
            br = bridge(matched, pool_ids)
            bridge_count += 1 if br else 0
            rec.update({"class": "corpus_not_pooled", "min_pooled_rank": None,
                        "n_corpus_keyword_chunks": len(matched),
                        "entity_bridge": br})
        else:
            counts["no_corpus_match"] += 1
            # 规则不自洽排查：answerable 用纯正文串，blob ⊇ 正文 → 不可能。
            detail = {}
            for kw in r["eval_keywords"]:
                detail[kw] = {"in_some_text": bool(kw2text.get(kw)),
                              "in_some_blob": bool(kw2blob.get(kw))}
            rec.update({"class": "no_corpus_match", "min_pooled_rank": None,
                        "n_corpus_keyword_chunks": 0, "keyword_probe": detail})
            print(f"[LOUD] answerable 但全库（含篇名）无关键词命中："
                  f"{r['qid']} keywords={r['eval_keywords']} probe={detail}")
        per_miss.append(rec)

    # ── title-only 关键词（正文没有、篇名才有 → 规则判不可答）──
    title_only = sorted(kw for kw in kws_all
                        if kw2blob.get(kw) and not kw2text.get(kw))
    title_only_qids = sorted({r["qid"] for r in rows
                              if any(k in title_only for k in r["eval_keywords"])})

    # ── 输出 ──
    consistent = counts["no_corpus_match"] == 0
    md = [f"# 未命中归因分诊 · {cp.name}（{args.mode}）", "",
          f"- answerable n={sum(1 for r in rows if r.get('answerable'))}"
          f"  k=6 misses n={len(misses)}"
          f"  采集窗口 top_k={d.get('top_k')}",
          f"- 分诊：pooled_in_window={counts['pooled_in_window']}"
          f"  corpus_not_pooled={counts['corpus_not_pooled']}"
          f"（其中实体桥接可及={bridge_count}）"
          f"  no_corpus_match={counts['no_corpus_match']}",
          f"- answerable 规则自洽性（(iii) 必须为 0）："
          f"{'PASS' if consistent else '**FAIL — 需人工排查不对称**'}",
          f"- 名次交叉核对（min pooled rank vs 采集 rank）不一致："
          f"{len(rank_mismatch)} 题{rank_mismatch[:10]}",
          f"- title-only 关键词（只活在篇名 → 规则判不可答）：{len(title_only)} 个"
          f" {title_only[:20]}"
          f"  影响题数={len(title_only_qids)}", ""]
    if per_miss:
        md += ["| qid | 类 | min_rank | 语料kw块 | 桥接 | seed_hit | query |",
               "|---|---|---|---|---|---|---|"]
        for m in per_miss:
            md.append(
                f"| {m['qid']} | {m['class']} | {m.get('min_pooled_rank')} "
                f"| {m.get('n_corpus_keyword_chunks')} "
                f"| {m.get('entity_bridge', '')} | {m.get('seed_hit')} "
                f"| {m['query'][:36]} |")
    text = "\n".join(md) + "\n"
    print(text)

    out_path = (Path(args.out) if args.out else
                ROOT / "data" / "compendium_rag" / "reports"
                / f"rank_triage_{tag}.json")
    if not out_path.is_absolute():
        out_path = ROOT / out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({
        "kind": "rank_triage", "collect": str(cp), "mode": args.mode,
        "top_k": d.get("top_k"),
        "n_answerable": sum(1 for r in rows if r.get("answerable")),
        "n_misses": len(misses), "classes": counts,
        "entity_bridge_count": bridge_count,
        "rank_mismatch_qids": rank_mismatch,
        "consistent": consistent,
        "title_only_keywords": title_only,
        "title_only_qids": title_only_qids,
        "per_miss": per_miss,
        "markdown": text,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[written] {out_path}")
    return 0 if consistent else 1


if __name__ == "__main__":
    sys.exit(main())
