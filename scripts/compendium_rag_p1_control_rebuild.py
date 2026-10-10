# -*- coding: utf-8 -*-
"""P1 重建**对照闸门**：只读，不写 graph.json，零云端。

跑两遍 ``rebuild_from_cache`` 的等价流程：

* **control（n1 语义）**：``normalize(..., map_relations=False)`` —— 谓语不受控化。
  它必须复现冻结的 v8 图谱。若不复现，说明 v8 与「当前 cache + 当前归一化」之间
  还有别的差异，那么 v9 的变化就**不能**全部记在 P1 头上，必须先查清。
* **treatment（n2 生产语义）**：``normalize(...)`` 默认路径。

然后把两者的实体/边结构与 v8 备份逐项对齐，输出可归因的 delta。

用法::

    PYTHONHASHSEED=0 .venv/Scripts/python.exe -X utf8 scripts/compendium_rag_p1_control_rebuild.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from compendium_rag import pipeline as P                       # noqa: E402
from compendium_rag.config import get_settings                 # noqa: E402
from compendium_rag.extract import (PROMPT_VERSION,             # noqa: E402
                                    ExtractionCache, cache_key, normalize)
from compendium_rag.graph_store import GraphStore               # noqa: E402

V8_BACKUP = ROOT / "data" / "compendium_rag" / "backups" / "graph.json.v8_frozen_026b41699f021db2"
REPORT = ROOT / "data" / "compendium_rag" / "reports" / "p1_control_rebuild.json"


def _build(s, chunks, results) -> GraphStore:
    g, _stats = P.build_graph(s, chunks, results)
    return g


def _snapshot(g: GraphStore) -> dict:
    rel = Counter(e.relation for e in g.edges)
    touched = {e.src for e in g.edges} | {e.dst for e in g.edges}
    return {
        "entities": len(g.entities),
        "edges": len(g.edges),
        "distinct_predicates": len(rel),
        "by_type": dict(Counter(e.type for e in g.entities.values()).most_common()),
        "isolated_entities": sum(1 for eid in g.entities if eid not in touched),
        "isolated_rate": round(sum(1 for eid in g.entities if eid not in touched)
                               / len(g.entities), 6) if g.entities else None,
        "top_predicates": [{"relation": r, "edges": n} for r, n in rel.most_common(10)],
    }


def _diff(a: GraphStore, b: GraphStore) -> dict:
    ea, eb = set(a.entities), set(b.entities)
    ka = {e.key for e in a.edges}
    kb = {e.key for e in b.edges}
    return {
        "entities_only_in_a": len(ea - eb),
        "entities_only_in_b": len(eb - ea),
        "sample_entities_only_in_a": sorted(ea - eb)[:20],
        "sample_entities_only_in_b": sorted(eb - ea)[:20],
        "edges_only_in_a": len(ka - kb),
        "edges_only_in_b": len(kb - ka),
        "edges_shared": len(ka & kb),
    }


def main() -> int:
    s = get_settings()
    chunks = P.load_chunks(s)
    cache = ExtractionCache(s.cache_dir)

    results_n1: dict[str, object] = {}
    results_n2: dict[str, object] = {}
    missing = 0
    for c in chunks:
        raw = cache.get_raw(cache_key(c, s.llm_model, PROMPT_VERSION))
        if raw is None:
            missing += 1
            continue
        results_n1[c.chunk_id] = normalize(c, raw, map_relations=False)
        results_n2[c.chunk_id] = normalize(c, raw)

    g_n1 = _build(s, chunks, results_n1)
    g_n2 = _build(s, chunks, results_n2)
    g_v8 = GraphStore.load(V8_BACKUP)

    v8_sha = hashlib.sha256(V8_BACKUP.read_bytes()).hexdigest()[:16]
    rep = {
        "schema": "compendium_rag.p1_control_rebuild/v1",
        "note": "只读对照：未写 graph.json / cache；零云端调用",
        "chunks": len(chunks),
        "chunks_missing_cache": missing,
        "v8_backup": {"path": str(V8_BACKUP.relative_to(ROOT)), "sha256_16": v8_sha,
                      "fingerprint": g_v8.fingerprint, "normalizer": g_v8.normalizer},
        "fingerprints": {"v8": g_v8.fingerprint, "control_n1": g_n1.fingerprint,
                         "treatment_n2": g_n2.fingerprint},
        "snapshots": {"v8": _snapshot(g_v8), "control_n1": _snapshot(g_n1),
                      "treatment_n2": _snapshot(g_n2)},
        # 闸门①：control 必须复现 v8（结构与内容都要对得上）
        "gate_control_reproduces_v8": _diff(g_v8, g_n1),
        # 闸门②：treatment 相对 control 的变化 = P1 的全部影响
        "delta_p1": _diff(g_n1, g_n2),
        "delta_vs_v8": _diff(g_v8, g_n2),
    }
    rep["gate_control_ok"] = (
        rep["gate_control_reproduces_v8"]["entities_only_in_a"] == 0
        and rep["gate_control_reproduces_v8"]["entities_only_in_b"] == 0
        and rep["gate_control_reproduces_v8"]["edges_only_in_a"] == 0
        and rep["gate_control_reproduces_v8"]["edges_only_in_b"] == 0)

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: rep[k] for k in
                      ("v8_backup", "fingerprints", "snapshots",
                       "gate_control_reproduces_v8", "gate_control_ok",
                       "delta_p1")}, ensure_ascii=False, indent=2))
    print(f"报告 → {REPORT}")
    return 0 if rep["gate_control_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
