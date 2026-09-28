# -*- coding: utf-8 -*-
"""P4 可行性验证：**已有交叉编码器分数**能否救回「放宽池后进池但排 34–51」的 6 道？

依据：
  - scripts/_p3_pool_widen.py：放宽 RRF 池到 60 后，6 道 gold 进池（排名 34–51）；
  - scripts/_p3_wide_pool_rerank.py：v6 冻结重排对这 6 道 **0/6** 命中
    -> 现有特征判别力不足，需更强判别器。
  - 仓库已有 CE 分数落盘：reports/ce_base_300_cn.json（bge-reranker-base）
    与 ce_large_300_cn.json（bge-reranker-large），且两个模型权重均在本地 models/。

本脚本：直接读已落盘的 CE 分数，看这 6 道题的 gold 块在 CE 排序下的名次。
判据（预注册）：
  - 若 gold 在 CE 排序下进入 top-6 -> P4 值得立项（并给出预期收益）；
  - 否则 CE 也救不回，需 P3 查询侧供给或补充抽提。
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "data/compendium_rag/reports"

NEW6 = ["R180", "R244", "R248", "R273", "R292", "R298"]
MISS = ["R001", "R005", "R012", "R094", "R127", "R170", "R171",
        "R180", "R244", "R248", "R273", "R292", "R297", "R298"]


def main() -> int:
    chunks = json.loads((ROOT / "data/compendium_rag/chunks.json").read_text(encoding="utf-8"))["chunks"]
    blob = {c["chunk_id"]: f"{c['text']}\n{c['chapter_title']}\n{c.get('scene_title','')}\n{c.get('part_title','')}"
            for c in chunks}
    ts = json.loads((ROOT / "data/knowledge/_audit/rag_testset_300_cn.json").read_text(encoding="utf-8"))
    by = {str(c["id"]): c for c in ts["cases"]}

    def kws(c):
        out = []
        for g in (c.get("evidence") or []):
            items = g if isinstance(g, (list, tuple)) else [g]
            out.extend(str(x) for x in items if x)
        return [k.strip() for k in out if k.strip()]

    for fname in ("ce_base_300_cn.json", "ce_large_300_cn.json"):
        p = R / fname
        if not p.exists():
            print(f"[skip] {fname} 不存在")
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        meta = d.get("_meta", {})
        print("=" * 78)
        print(f"{fname}   meta={json.dumps(meta, ensure_ascii=False)[:200]}")
        # 结构探测
        sample = next((v for k, v in d.items() if k != "_meta"), None)
        print(f"  条目样例类型: {type(sample).__name__}  {str(sample)[:220]}")
        print()
        hit6 = 0
        print(f"{'qid':6}{'gold在CE序名次':>14}")
        for q in NEW6 + [x for x in MISS if x not in NEW6]:
            rec = d.get(q)
            if rec is None:
                print(f"{q:6}{'(无记录)':>14}")
                continue
            kws_q = kws(by[q])
            gold = {cid for cid, t in blob.items() if any(k in t for k in kws_q)}
            # rec 可能是 {chunk_id: score} 或 list
            if isinstance(rec, dict):
                items = rec.get("scores") or rec.get("ranked") or rec
                if isinstance(items, dict):
                    pairs = [(k, v) for k, v in items.items() if isinstance(v, (int, float))]
                else:
                    pairs = [(x.get("chunk_id"), x.get("score")) for x in items
                             if isinstance(x, dict)]
            else:
                pairs = [(x.get("chunk_id"), x.get("score")) for x in rec if isinstance(x, dict)]
            pairs = [(c, s) for c, s in pairs if c]
            pairs.sort(key=lambda kv: (-kv[1], kv[0]))
            rank = next((i for i, (c, _) in enumerate(pairs, 1) if c in gold), None)
            mark = ""
            if rank and rank <= 6:
                mark = "  **CE top-6 可达**"
                hit6 += 1
            print(f"{q:6}{str(rank):>14}{mark}")
        print(f"\n  {fname}: 14 道 miss 中 CE 排序进 top-6 的 = {hit6}/14")
        print(f"          其中新进池 6 道: "
              f"{sum(1 for q in NEW6 if _rank(d, q, by, blob, kws) and _rank(d, q, by, blob, kws) <= 6)}/6")
    return 0


def _rank(d, q, by, blob, kws):
    rec = d.get(q)
    if rec is None:
        return None
    kq = kws(by[q])
    gold = {cid for cid, t in blob.items() if any(k in t for k in kq)}
    if isinstance(rec, dict):
        items = rec.get("scores") or rec.get("ranked") or rec
        pairs = ([(k, v) for k, v in items.items() if isinstance(v, (int, float))]
                 if isinstance(items, dict) else
                 [(x.get("chunk_id"), x.get("score")) for x in items if isinstance(x, dict)])
    else:
        pairs = [(x.get("chunk_id"), x.get("score")) for x in rec if isinstance(x, dict)]
    pairs = [(c, s) for c, s in pairs if c]
    pairs.sort(key=lambda kv: (-kv[1], kv[0]))
    return next((i for i, (c, _) in enumerate(pairs, 1) if c in gold), None)


if __name__ == "__main__":
    raise SystemExit(main())
