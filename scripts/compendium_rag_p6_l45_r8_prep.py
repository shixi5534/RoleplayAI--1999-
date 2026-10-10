# -*- coding: utf-8 -*-
"""P6 · L4.5 R8 重新盲评的输入装配（**只读图，只写输入批次**）。

为什么需要这个脚本，而不是直接跑 ``audit_l4.py --mode multiscene --prep``：

1. ``mode_multiscene --prep`` 的抽样是 ``rng.shuffle(cand)`` 后 ``sorted(cand)[:60]``
   —— shuffle 被后续 sort 抵消，实际退化为「按 chunk_id 字典序取前 60」。
   R8 修边后候选池从 2793 掉到 2792（``activity__12101_绿湖噩梦:1.2.0``
   的角色端点数从 3 降到 2，只剩牙仙↔维尔汀），同时字典序前 60 的边界挪动，
   于是「照原样重跑 prep」会**换掉 2 块样本**（换出 ``雷米特杯:2.0.1``、
   ``绿湖:1.2.0``，换入 ``绿湖:2.0.1``、``绿湖:2.0.2``）→ 与 R8 前那份判分
   不可逐块比较。

2. 所以本脚本产**两臂并集**（62 块，去重后）：
   - **臂 A（主，可逐块比较）**：沿用 R8 前已判分的那 60 个 chunk_id，
     只把 edges 换成 R8 图上的现状；
   - **臂 B（原生）**：按同一抽样规则在 R8 图上重算的自然 60 块。
   两臂交 58 块；臂 A 独有 2 块、臂 B 独有 2 块。判分只需盲评 62 块，
   之后可分别合成两臂均值。

产物目录 ``data/knowledge/_audit/l4_multiscene_r8/``：
- ``INSTRUCTIONS.md``：判分说明（与 R8 前同 rubric，仅改目录与文件名）；
- ``ms_b01..b04.json``：每批 16 块（``audit.l4_multiscene_input/v1``）；
- ``arm_map.json``：块 → 所属臂，供合成用（**不给判分子代理看**）。

红线：只读 graph.json / chunks，只写上述目录；不跑 cli rebuild / extract；
不联网；不调 LLM；不用 rmtree/unlink（既有守门测试要求）。
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

DATA = ROOT / "data" / "compendium_rag"
GRAPH = DATA / "graph.json"
KNOW = ROOT / "data" / "knowledge" / "_audit"
OLD_IN = KNOW / "l4_multiscene"
OUT_DIR = KNOW / "l4_multiscene_r8"

SEED = 42
N_PICK = 60
BATCH = 16


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    ents = {e["eid"]: e for e in graph["entities"]}
    chars = {eid for eid, e in ents.items() if e["type"] == "角色"}

    chunks_path = DATA / "chunks.json"
    if not chunks_path.exists():
        chunks_path = DATA / "chunk_index.json"
    chunks = json.loads(chunks_path.read_text(encoding="utf-8"))
    if isinstance(chunks, dict):
        chunks = chunks.get("chunks") or chunks.get("items") or []
    text_by_cid = {c["chunk_id"]: c.get("text", "") for c in chunks}

    per_chunk: dict[str, set] = {}
    for e in graph["edges"]:
        cids = e.get("chunk_ids") or []
        if not cids:
            continue
        cid = cids[0]
        for side in (e["src"], e["dst"]):
            if side in chars:
                per_chunk.setdefault(cid, set()).add(side)

    pool = [c for c, s in per_chunk.items()
            if len(s) >= 3 and c in text_by_cid]
    rng = random.Random(SEED)
    rng.shuffle(pool)
    natural = sorted(pool)[:N_PICK]

    frozen: list[str] = []
    for i in (1, 2, 3):
        p = OLD_IN / f"ms_b{i:02d}.json"
        if not p.exists():
            print(f"[FATAL] 缺 R8 前输入 {p}", file=sys.stderr)
            return 2
        frozen += [it["chunk_id"]
                   for it in json.loads(p.read_text(encoding="utf-8"))["items"]]

    only_a = sorted(set(frozen) - set(natural))
    only_b = sorted(set(natural) - set(frozen))
    union = sorted(set(frozen) | set(natural))

    # canonical 回退口径与 audit_l4.py 一致：sidecar 优先，否则 classify_relation
    sys.path.insert(0, str(ROOT / "scripts"))
    import audit_l4 as L4  # noqa: E402
    smap = json.loads(L4.SIDECAR.read_text(encoding="utf-8"))["mapping"] \
        if L4.SIDECAR.exists() else {}
    _CANON, _G, classify_relation = L4._vocab()
    canon_fn = L4._canon_of(smap, classify_relation)

    items = []
    for cid in union:
        involved = per_chunk.get(cid, set())
        rows = []
        for e in graph["edges"]:
            cids = e.get("chunk_ids") or []
            if cids and cids[0] == cid and e["src"] in involved \
                    and e["dst"] in involved:
                rows.append({
                    "src": ents[e["src"]]["name"] if e["src"] in ents else e["src"],
                    "relation": e["relation"],
                    "canonical": canon_fn(e["relation"]),
                    "dst": ents[e["dst"]]["name"] if e["dst"] in ents else e["dst"],
                    "evidence": (e.get("evidence") or "")[:80],
                })
        items.append({
            "chunk_id": cid,
            "characters": sorted(ents[x]["name"] for x in involved
                                 if x in ents),
            "edges": rows[:25],
            "text": text_by_cid.get(cid, "")[:2600],
        })

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    n_batch = 0
    for bi in range(0, len(items), BATCH):
        n_batch += 1
        payload = {
            "schema": "audit.l4_multiscene_input/v1",
            "task": "逐块判定这些角色之间的关系陈述是否与原文互洽（1~5 分）",
            "batch": f"b{bi // BATCH + 1:02d}",
            "items": items[bi:bi + BATCH],
        }
        (OUT_DIR / f"ms_b{bi // BATCH + 1:02d}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=1),
            encoding="utf-8")

    (OUT_DIR / "arm_map.json").write_text(json.dumps({
        "schema": "audit.l4_multiscene_arms/v1",
        "graph_sha16": L4.AC.sha16_file(GRAPH) if hasattr(L4, "AC") else "",
        "note": "本文件供合成均值用，不得给判分子代理看",
        "arm_a_frozen_pre_r8": frozen,
        "arm_b_natural_r8": natural,
        "arm_a_only": only_a,
        "arm_b_only": only_b,
        "union": union,
        "n_union": len(union),
        "batch_size": BATCH,
        "batches": n_batch,
        "pool_size_r8": len(pool),
        "pool_size_pre_r8_note": "R8 前为 2793（绿湖:1.2.0 当时角色端点≥3）",
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    inst = OUT_DIR / "INSTRUCTIONS.md"
    src_inst = OLD_IN / "INSTRUCTIONS.md"
    body = src_inst.read_text(encoding="utf-8")
    body = body.replace("data/knowledge/_audit/l4_multiscene/",
                        "data/knowledge/_audit/l4_multiscene_r8/")
    body = body.replace(
        "# WP4 多角色场景互洽性评分说明（L4.5 · 审查子代理）",
        "# WP4 多角色场景互洽性评分说明（L4.5 · R8 重新盲评 · 审查子代理）\n\n"
        "> 本目录是 **R8（L4.5 修边 28 条）之后**的重新盲评。"
        "rubric 与 R8 前完全一致；\n> 唯一差别是 edges 取自 R8 新图。"
        "**禁止**参考 `../l4_multiscene/` 下的任何旧文件。")
    inst.write_text(body, encoding="utf-8")

    print(f"pool(r8)={len(pool)}  union={len(union)}  batches={n_batch}")
    print(f"arm A (frozen, n={len(frozen)}) only: {only_a}")
    print(f"arm B (natural, n={len(natural)}) only: {only_b}")
    print(f"→ {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
