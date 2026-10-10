# -*- coding: utf-8 -*-
"""P6 · L4.5 干净 A/B 的**基线臂**装配（V9P1 图 = ``backups/graph.json.prev.r8``）。

## 为什么需要它

`data/knowledge/_audit/l4_multiscene/ms_b0*.json` 那批输入是 **v8 图**（`026b41699f021db2`）
下生成的：当时图里存的是**表层谓语**（`驳斥`/`劝告`/`抗议`/`报告`，v8 共 8353 个谓语）。
而 R8 图（`56507b18ac2113b6`）经 `n2` 归一化后只存**规范谓语**（`对抗`/`对立`/`警告`/`告知`，
共 1609 个）。所以在 R8 输入上重新盲评，等于同时改了两个变量：

1. 28 条修边提案（22 delete + 6 add）；
2. **全图谓语从表层形态改写成规范形态**（影响全部 60 块，不止 18 块）。

于是「3.9333 → 3.4333」不能用来说明修边有害——差异主要来自 (2)。

## 本脚本做什么

用 **V9P1 图**（= `backups/graph.json.prev.r8`，sha16 `7cac5867e8c80879`，与 R8 同为
`n2` 规范谓语、只差那 28 条边）为**同一批 62 个 chunk_id** 生成输入，落到
`data/knowledge/_audit/l4_multiscene_p1base/`，批次切分与 `l4_multiscene_r8/` **完全一致**
（16/16/16/14）。这样两臂的差别**只有那 28 条边**，盲评差值才是修边的真实效果。

红线：只读两个图 + chunks；只写该目录；不跑 cli rebuild/extract；不联网；不调 LLM；
不用 rmtree/unlink。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

DATA = ROOT / "data" / "compendium_rag"
BASELINE_GRAPH = DATA / "backups" / "graph.json.prev.r8"
KNOW = ROOT / "data" / "knowledge" / "_audit"
R8_DIR = KNOW / "l4_multiscene_r8"
OUT_DIR = KNOW / "l4_multiscene_p1base"
BATCH = 16


def main() -> int:
    if not BASELINE_GRAPH.exists():
        print(f"[FATAL] 缺基线图 {BASELINE_GRAPH}", file=sys.stderr)
        return 2

    graph = json.loads(BASELINE_GRAPH.read_text(encoding="utf-8"))
    ents = {e["eid"]: e for e in graph["entities"]}

    chunks = json.loads((DATA / "chunks.json").read_text(encoding="utf-8"))
    if isinstance(chunks, dict):
        chunks = chunks.get("chunks") or chunks.get("items") or []
    text_by_cid = {c["chunk_id"]: c.get("text", "") for c in chunks}

    arm_map = json.loads((R8_DIR / "arm_map.json").read_text(encoding="utf-8"))
    union: list[str] = arm_map["union"]

    # canonical 归组口径与 audit_l4.py 一致（sidecar 优先，否则 classify_relation）
    import audit_l4 as L4  # noqa: E402
    smap = json.loads(L4.SIDECAR.read_text(encoding="utf-8"))["mapping"] \
        if L4.SIDECAR.exists() else {}
    _CANON, _G, classify_relation = L4._vocab()
    canon_fn = L4._canon_of(smap, classify_relation)

    # 与 audit_l4.py:782 及 r8 prep 口径一致：只认 chunk_ids[0] == cid
    by_chunk: dict[str, list] = {}
    for e in graph["edges"]:
        cids = e.get("chunk_ids") or []
        if cids:
            by_chunk.setdefault(cids[0], []).append(e)

    items = []
    for cid in union:
        rows_all = by_chunk.get(cid, [])
        involved = set()
        for e in rows_all:
            for side in (e["src"], e["dst"]):
                if ents.get(side, {}).get("type") == "角色":
                    involved.add(side)
        rows = []
        for e in rows_all:
            if e["src"] in involved and e["dst"] in involved:
                rows.append({
                    "src": ents[e["src"]]["name"] if e["src"] in ents else e["src"],
                    "relation": e["relation"],
                    "canonical": canon_fn(e["relation"]),
                    "dst": ents[e["dst"]]["name"] if e["dst"] in ents else e["dst"],
                    "evidence": (e.get("evidence") or "")[:80],
                })
        items.append({
            "chunk_id": cid,
            "characters": sorted(ents[x]["name"] for x in involved if x in ents),
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
            json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")

    inst = (R8_DIR / "INSTRUCTIONS.md").read_text(encoding="utf-8")
    inst = inst.replace("data/knowledge/_audit/l4_multiscene_r8/",
                        "data/knowledge/_audit/l4_multiscene_p1base/")
    inst = inst.replace("l4_multiscene_r8", "l4_multiscene_p1base")
    inst = inst.replace("R8（L4.5 修边 28 条）之后", "V9P1 基线（修边 28 条之前）")
    inst = inst.replace(
        "**禁止**参考 `../l4_multiscene_r8/` 下的任何旧文件。",
        "**禁止**参考 `../l4_multiscene_r8/` 或 `../l4_multiscene/` 下的任何文件。")
    (OUT_DIR / "INSTRUCTIONS.md").write_text(inst, encoding="utf-8")

    (OUT_DIR / "arm_map.json").write_text(json.dumps({
        "schema": "audit.l4_multiscene_baseline_arm/v1",
        "graph": str(BASELINE_GRAPH.relative_to(ROOT)),
        "graph_sha16": "7cac5867e8c80879",
        "note": "V9P1 基线臂；与 l4_multiscene_r8 的唯一差别是那 28 条修边提案",
        "union": union, "n_union": len(union),
        "batch_size": BATCH, "batches": n_batch,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"baseline arm: n={len(items)} batches={n_batch} → {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
