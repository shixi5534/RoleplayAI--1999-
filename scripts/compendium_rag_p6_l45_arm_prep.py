# -*- coding: utf-8 -*-
"""P6 · L4.5 多臂 A/B —— 通用臂装配器。

用途：为**同一批冻结 chunk_id**（`l4_multiscene_r8/arm_map.json` 的 union，62 块）
在**任意一张图**上生成盲评输入，批次切分与 r8 臂**逐块对齐**（16/16/16/14）。
这样各臂的唯一差别就是图的边集，盲评差值才是修边的真实效果。

为什么不用 `scripts/audit_l4.py --mode multiscene --prep`：
该模式用自己的采样（`sorted(cand)[:60]`），换图后候选池会变（R8 后 2792、
再删边后可能又变），样本跟着漂移 → 失去可比性。

用法::

    PYTHONPATH=src .venv/Scripts/python.exe -X utf8 \
      scripts/compendium_rag_p6_l45_arm_prep.py \
      --graph data/compendium_rag/backups/graph.json.prev.r8 \
      --sha16 7cac5867e8c80879 \
      --out   data/knowledge/_audit/l4_multiscene_p1base \
      --note  "V9P1 基线臂"

红线：只读图 + chunks；只写 --out 目录；不跑 cli rebuild/extract；不联网；
不调 LLM；**不用 rmtree/unlink**（守门测试
``tests/compendium_rag/test_independence.py::test_scripts_never_target_real_data_dir``
要求 ``scripts/compendium_rag_*.py`` 出现 rmtree/unlink 时必须把 data_dir 钉到临时目录）。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

DATA = ROOT / "data" / "compendium_rag"
KNOW = ROOT / "data" / "knowledge" / "_audit"
R8_DIR = KNOW / "l4_multiscene_r8"
BATCH = 16
TEXT_CAP = 2600
EDGE_CAP = 25


def build(graph_path: Path, sha16: str, out_dir: Path, note: str) -> int:
    if not graph_path.exists():
        print(f"[FATAL] 缺图 {graph_path}", file=sys.stderr)
        return 2

    graph = json.loads(graph_path.read_text(encoding="utf-8"))
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
            "edges": rows[:EDGE_CAP],
            "text": text_by_cid.get(cid, "")[:TEXT_CAP],
        })

    out_dir.mkdir(parents=True, exist_ok=True)
    n_batch = 0
    for bi in range(0, len(items), BATCH):
        n_batch += 1
        payload = {
            "schema": "audit.l4_multiscene_input/v1",
            "task": "逐块判定这些角色之间的关系陈述是否与原文互洽（1~5 分）",
            "batch": f"b{bi // BATCH + 1:02d}",
            "items": items[bi:bi + BATCH],
        }
        (out_dir / f"ms_b{bi // BATCH + 1:02d}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")

    # 说明书写成该臂专用：只换目录名，其余 rubric 必须与其它臂逐字一致，
    # 否则判分尺度又成为一个混淆变量（P6 首轮 A/B 已踩过这个坑）。
    inst = (R8_DIR / "INSTRUCTIONS.md").read_text(encoding="utf-8")
    inst = inst.replace("data/knowledge/_audit/l4_multiscene_r8/", f"{out_dir.relative_to(ROOT).as_posix()}/")
    inst = inst.replace("l4_multiscene_r8", out_dir.name)
    inst = inst.replace(
        "**禁止**参考 `../l4_multiscene_r8/` 下的任何旧文件。",
        "**禁止**参考 `../l4_multiscene_r8/`、`../l4_multiscene_p1base/` 或 "
        "`../l4_multiscene/` 下的任何文件。")
    (out_dir / "INSTRUCTIONS.md").write_text(inst, encoding="utf-8")

    (out_dir / "arm_map.json").write_text(json.dumps({
        "schema": "audit.l4_multiscene_baseline_arm/v1",
        "graph": str(graph_path.relative_to(ROOT)),
        "graph_sha16": sha16,
        "note": note,
        "union": union, "n_union": len(union),
        "batch_size": BATCH, "batches": n_batch,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"arm: n={len(items)} batches={n_batch} sha16={sha16} -> {out_dir}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--graph", required=True)
    ap.add_argument("--sha16", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--note", default="")
    a = ap.parse_args()
    return build(ROOT / a.graph, a.sha16, ROOT / a.out, a.note)


if __name__ == "__main__":
    raise SystemExit(main())
