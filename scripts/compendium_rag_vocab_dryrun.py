# -*- coding: utf-8 -*-
"""P1 谓语受控化**只读试算**：不写图谱、不写缓存、零云端。

对全量 3695 块的缓存原始输出跑一遍现行 ``normalize()``，再把关系谓语过
``relation_norm.map_relation``，量出四件事：

1. 合规率（谓语 ∈ 77 canonical）改写前后的边权占比；
2. 判定来源分布（canonical/synonym/rule/override/swap/kept:*/drop:*）；
3. 方向闸拦下多少条（``kept:direction_blocked``）——这些是「合并会把事实写反」
   的候选，需要人工裁决进 swap / same_direction；
4. 归一后端点去重的边数变化（同义谓语合并会让边数下降，PPR 边权上升）。

用法::

    PYTHONHASHSEED=0 .venv/Scripts/python.exe -X utf8 scripts/compendium_rag_vocab_dryrun.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from compendium_rag import pipeline as P                      # noqa: E402
from compendium_rag.config import get_settings                # noqa: E402
from compendium_rag.extract import (PROMPT_VERSION,            # noqa: E402
                                    ExtractionCache, cache_key, normalize)
from compendium_rag.relation_norm import VocabTables, map_relation  # noqa: E402
from compendium_rag.relation_vocab import CANONICAL_SET        # noqa: E402

REPORT = ROOT / "data" / "compendium_rag" / "reports" / "p1_vocab_dryrun.json"


def main() -> int:
    s = get_settings()
    chunks = P.load_chunks(s)
    cache = ExtractionCache(s.cache_dir)
    tables = VocabTables.load()

    print(f"块={len(chunks)} overrides={len(tables.overrides)} "
          f"watch={len(tables.watch)} inverse_pairs={len(tables.inverse_pairs)} "
          f"swap={len(tables.policy.swap)} "
          f"same_direction={len(tables.policy.same_direction)}")

    base_triples: list[tuple[str, str, str]] = []
    post_triples: list[tuple[str, str, str]] = []
    prod_triples: list[tuple[str, str, str]] = []
    codes: Counter[str] = Counter()
    blocked: Counter[tuple[str, str]] = Counter()
    rewritten: Counter[tuple[str, str]] = Counter()
    dropped: Counter[str] = Counter()
    unmapped: Counter[str] = Counter()
    missing = 0

    for c in chunks:
        raw = cache.get_raw(cache_key(c, s.llm_model, PROMPT_VERSION))
        if raw is None:
            missing += 1
            continue
        # 生产链路（normalize 内部已做谓语映射）——用来验证试算与实际接线一致
        for r in normalize(c, raw).relations:
            prod_triples.append((r.src, r.relation, r.dst))
        # 对照链路：关掉映射拿到 n1 谓语，再手工映射，好统计判定来源
        for r in normalize(c, raw, map_relations=False).relations:
            base_triples.append((r.src, r.relation, r.dst))
            m = map_relation(r.src, r.relation, r.dst, tables=tables)
            codes[m.code] += 1
            if not m.relation:
                dropped[m.code] += 1
                continue
            if m.code == "kept:direction_blocked":
                blocked[(r.relation, m.intended)] += 1
            elif m.code == "kept:review:unmapped":
                unmapped[r.relation] += 1
            elif m.relation != r.relation:
                rewritten[(r.relation, m.relation)] += 1
            post_triples.append((m.src, m.relation, m.dst))

    def concentration(triples: list[tuple[str, str, str]]) -> dict:
        """不可刷指标：合规率能靠扩词表刷，浓度不能。

        单例谓语占比越低、top10 覆盖越高，说明谓语真的被收敛成了可复用关系，
        而不是「换一批自由文本」。
        """
        cnt = Counter(rel for _, rel, _ in triples)
        n = len(triples)
        common = cnt.most_common()
        singles = sum(1 for _, k in common if k == 1)
        return {
            "edges": n,
            "distinct_predicates": len(cnt),
            "singleton_predicates": singles,
            "singleton_rate": round(singles / len(cnt), 6) if cnt else None,
            "singleton_edges": singles,
            "top10_edge_coverage": round(sum(k for _, k in common[:10]) / n, 6) if n else None,
            "top10": [{"predicate": w, "edges": k} for w, k in common[:10]],
        }

    def compliance(triples: list[tuple[str, str, str]]) -> dict:
        n = len(triples)
        hit = sum(1 for _, rel, _ in triples if rel in CANONICAL_SET)
        return {"edges": n, "canonical_edges": hit,
                "rate": round(hit / n, 6) if n else None,
                "distinct_predicates": len({rel for _, rel, _ in triples})}

    base_dedup = list(dict.fromkeys(base_triples))
    post_dedup = list(dict.fromkeys(post_triples))
    prod_dedup = list(dict.fromkeys(prod_triples))

    # 长尾未判定谓语：按边数降序 + 累计覆盖，用来判断「扩词表」值不值
    unm_total = sum(unmapped.values())
    cum = 0
    cum_at: dict[str, int] = {}
    for i, (_w, n) in enumerate(unmapped.most_common(), 1):
        cum += n
        for mark in (50, 100, 200, 400):
            if i == mark:
                cum_at[f"top{mark}"] = round(cum / unm_total, 4) if unm_total else None
    rep = {
        "schema": "compendium_rag.p1_vocab_dryrun/v1",
        "note": "只读试算：未写 graph.json / cache；零云端调用",
        "prompt_version": PROMPT_VERSION,
        "chunks": len(chunks),
        "chunks_missing_cache": missing,
        "tables": {"overrides": len(tables.overrides),
                   "watch": sorted(tables.watch),
                   "inverse_pairs": sorted(map(sorted, tables.inverse_pairs)),
                   "swap": tables.policy.swap,
                   "same_direction": sorted(tables.policy.same_direction)},
        "before": compliance(base_triples),
        "after": compliance(post_triples),
        "after_dedup": compliance(post_dedup),
        "wiring_check": {
            "note": "生产 normalize() 的产物必须与本试算逐条相同，否则试算白做",
            "production_dedup_edges": len(prod_dedup),
            "ordered_identical": prod_dedup == post_dedup,
            "same_edge_set": set(prod_dedup) == set(post_dedup),
            "first_diff": next(({"i": i, "production": a, "dryrun": b}
                                for i, (a, b) in enumerate(
                                    zip(prod_dedup, post_dedup)) if a != b), None),
        },
        "concentration": {"before_dedup": concentration(base_dedup),
                          "after_dedup": concentration(post_dedup)},
        "before_dedup_edges": len(base_dedup),
        "edge_merge_delta": len(post_dedup) - len(base_dedup),
        "codes": dict(codes.most_common()),
        "dropped": dict(dropped.most_common()),
        "top_rewritten": [{"raw": a, "canonical": b, "edges": n}
                          for (a, b), n in rewritten.most_common(40)],
        "direction_blocked": [{"raw": a, "canonical": b, "edges": n}
                              for (a, b), n in blocked.most_common()],
        "n_rewritten_predicates": len(rewritten),
        "unmapped_summary": {"edges": unm_total, "distinct": len(unmapped),
                             "cumulative_coverage_of_unmapped_edges": cum_at},
        "top_unmapped": [{"predicate": w, "edges": n}
                         for w, n in unmapped.most_common(200)],
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({k: rep[k] for k in
                      ("before", "after", "after_dedup", "before_dedup_edges",
                       "edge_merge_delta", "codes", "dropped", "concentration")},
                     ensure_ascii=False, indent=2))
    print(f"方向闸拦下 {len(rep['direction_blocked'])} 种谓语 / "
          f"{sum(x['edges'] for x in rep['direction_blocked'])} 条边")
    print(f"报告 → {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
