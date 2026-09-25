#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""生成 100 道评测问题（带 ground truth），用于检索层回归测试。

题型：
  A 关系题（60）：从带 evidence 的边抽样 ——「X 和 Y 是什么关系？」
      ground truth = 该边 evidence 的 hash 集合
  B 实体题（25）：从高 mentions 实体抽样 ——「X 是谁 / X 是什么？」
      ground truth = 语料中包含 X（name 或 alias）的若干块 hash
  C 别名题（15）：用实体别名提问 ——「〈别名〉是谁？」
      ground truth = 语料中包含该别名的若干块 hash

输出：data/knowledge/_audit/eval_questions.json
"""
from __future__ import annotations

import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from roleplay.core.knowledge.plot_graph import is_noise_entity  # noqa: E402

GRAPH = ROOT / "data/knowledge/plot_graph_wu_ming_zhe.json"
CORPUS = ROOT / "data/knowledge/plot_corpus_wu_ming_zhe.json"
OUT = ROOT / "data/knowledge/_audit/eval_questions.json"

SEED = 2026
N_EDGE, N_ENT, N_ALIAS = 60, 25, 15

QUESTIONS = {
    "角色": ["{x}是谁？", "{x}是什么人？"],
    "组织": ["{x}是什么组织？", "{x}是做什么的？"],
    "地点": ["{x}在哪里？", "{x}是个什么地方？"],
    "物品": ["{x}是什么？", "{x}是什么东西？"],
    "概念": ["{x}是什么？", "什么是{x}？"],
    "事件": ["{x}发生了什么？", "{x}是怎么回事？"],
    "现象": ["{x}是什么现象？", "{x}是怎么回事？"],
}


def norm(s: str) -> str:
    return (s or "").strip().lower().replace(" ", "").replace("\n", "")


def main() -> int:
    rnd = random.Random(SEED)
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    ents = graph["entities"]
    edges = graph["edges"]
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    chunks = corpus["chunks"]

    # name / alias → 出现的块 hash 列表
    occ: dict[str, list[str]] = {}
    for ch in chunks:
        occ.setdefault(ch["hash"], None)  # 占位，下面按需填充
    hash_text = {ch["hash"]: norm(ch.get("text") or "") for ch in chunks}

    def chunks_mentioning(term: str, limit: int = 3) -> list[str]:
        t = norm(term)
        if len(t) < 2:
            return []
        hits = [h for h, txt in hash_text.items() if t in txt]
        rnd.shuffle(hits)
        return hits[:limit]

    def label(eid: str) -> str:
        return (ents.get(eid, {}) or {}).get("name") or ""

    items: list[dict] = []
    used_pairs: set[tuple[str, str]] = set()

    # --- A 关系题 ---
    pool = [
        e for e in edges
        if e.get("evidence")
        and label(e.get("src")) and label(e.get("dst"))
        and not is_noise_entity(label(e.get("src")))
        and not is_noise_entity(label(e.get("dst")))
        and len(label(e.get("src"))) >= 2
        and len(label(e.get("dst"))) >= 2
    ]
    rnd.shuffle(pool)
    for e in pool:
        if len(items) >= N_EDGE:
            break
        s, d = label(e["src"]), label(e["dst"])
        if (s, d) in used_pairs or s == d:
            continue
        used_pairs.add((s, d))
        gts = [x.get("hash") for x in e["evidence"] if x.get("hash")]
        if not gts:
            continue
        items.append({
            "id": f"Q{len(items)+1:03d}",
            "kind": "relation",
            "question": f"{s}和{d}是什么关系？",
            "subject": s, "object": d,
            "relation": e.get("relation"),
            "src_id": e.get("src"), "dst_id": e.get("dst"),
            "gt_hashes": gts,
        })

    # --- B 实体题 ---
    cand = [
        (eid, v) for eid, v in ents.items()
        if (v.get("mentions") or 0) >= 3
        and not is_noise_entity(v.get("name") or "")
        and len(v.get("name") or "") >= 2
    ]
    cand.sort(key=lambda kv: -(kv[1].get("mentions") or 0))
    rnd.shuffle(cand[:400])
    for eid, v in cand:
        if len(items) >= N_EDGE + N_ENT:
            break
        name = v["name"]
        gts = chunks_mentioning(name)
        if not gts:
            continue
        tmpl = QUESTIONS.get((v.get("type") or "").split("|")[0], ["{x}是什么？"])
        items.append({
            "id": f"Q{len(items)+1:03d}",
            "kind": "entity",
            "question": rnd.choice(tmpl).format(x=name),
            "subject": name,
            "object": None,
            "relation": None,
            "gt_hashes": gts,
        })

    # --- C 别名题 ---
    alias_pool = [
        (eid, v, a) for eid, v in ents.items()
        for a in (v.get("aliases") or [])
        if a and norm(a) != norm(v.get("name") or "")
        and len(a.strip()) >= 3
        and not is_noise_entity(a)
        and not is_noise_entity(v.get("name") or "")
    ]
    rnd.shuffle(alias_pool)
    seen_alias: set[str] = set()
    for eid, v, a in alias_pool:
        if len(items) >= N_EDGE + N_ENT + N_ALIAS:
            break
        if norm(a) in seen_alias:
            continue
        gts = chunks_mentioning(a)
        if not gts:
            continue
        seen_alias.add(norm(a))
        items.append({
            "id": f"Q{len(items)+1:03d}",
            "kind": "alias",
            "question": f"{a}是谁？",
            "subject": a,
            "object": v.get("name"),
            "relation": None,
            "gt_hashes": gts,
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps({"seed": SEED, "count": len(items), "items": items},
                   ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    kinds: dict[str, int] = {}
    for it in items:
        kinds[it["kind"]] = kinds.get(it["kind"], 0) + 1
    print(f"[gen] 生成 {len(items)} 题 → {OUT.relative_to(ROOT)}")
    print(f"[gen] 题型分布 {kinds}")
    for it in items[:5]:
        print("   ", it["id"], it["question"], "| gt", len(it["gt_hashes"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
