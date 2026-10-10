"""P9 · CBI 检索通道的**对照集**：问 A 自己的事，却检到 B 的私有块才算泄漏。

为什么要这个对照：主测试集（cbi_testset_500）的题面**直接问 B 的私事**，于是检索命中 B 的
章节是**正确行为**，但按 CBI 里 `N_retrieval =「检索到其他角色私有知识，但未说出」` 的定义
就会被记成泄漏 —— 实测这样跑出来检索泄漏率 0.80~0.85，上限只有 0.76，任何生成层修复都追不回，
因为量的根本不是边界失守而是检索能力。

对照集把题面换成「问 A 本人的私事」，仍用同一条 top-6 判据。若对照组的 B 私块命中率显著更低，
就证明主集的高读数来自题面把 B 点名了，指标该按对照组口径定义；反之若两组差不多，
说明检索真的在跨角色串知识，那才是 P9 要治的东西。

规则与主集一致：具名非群演、双向独占块、共现≥2、SEED=42、每角色≤3 对。
"""

from __future__ import annotations

import hashlib
import itertools
import json
import os
import random
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _k, _v in {"CMPRAG_LEX_WEIGHT": "1.0", "CMPRAG_RRF_K": "1",
               "CMPRAG_LEX_FIRST": "0", "PYTHONHASHSEED": "0"}.items():
    os.environ[_k] = _v
sys.path.insert(0, str(ROOT / "src"))
from compendium_rag.corpus import is_generic_speaker  # noqa: E402
from compendium_rag.extract import GENERIC_PERSON_NOUNS, RE_DESC_SUFFIX  # noqa: E402
from compendium_rag.graph_store import GENERIC_ROLE_SUFFIX  # noqa: E402

GRAPH = ROOT / "data" / "compendium_rag" / "graph.json"
CHUNKS = ROOT / "data" / "compendium_rag" / "chunks.json"
OUT = ROOT / "data" / "compendium_rag" / "reports" / "cbi_controlset_100.json"
EXPECTED_SHA = "911bb538160db80e"
SEED, N_PAIRS, MIN_CHUNKS, MIN_CO = 42, 100, 15, 2
CROWD_RE = r"[0-9０-９ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ]+$"
QUERY = "（你在替{A}整理自己的档案）{A}本人私下不为人知的那件事，正典里是怎么写的？"


def sha16(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()[:16]


def main() -> int:
    sha = sha16(GRAPH)
    if sha != EXPECTED_SHA:
        raise SystemExit(f"[FATAL] 图指纹漂移 {sha} != {EXPECTED_SHA}；不写文件")
    if OUT.exists():
        raise SystemExit(f"[FATAL] 对照集已生成，勿重抽：{OUT}")
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    ents = {e["eid"]: e for e in graph["entities"]}
    chunks = {c["chunk_id"]: c for c in
              json.loads(CHUNKS.read_text(encoding="utf-8"))["chunks"]}
    roles = [e for e in graph["entities"] if e.get("type") == "角色"]
    names_of = {e["eid"]: {e["name"], *(e.get("aliases") or [])} for e in roles}

    def specific(e) -> bool:
        n = e["name"]
        if len(n) < 2 or any(t in n for t in ("？？？", "口口口")) or re.search(CROWD_RE, n):
            return False
        if is_generic_speaker(n) or n in GENERIC_PERSON_NOUNS or RE_DESC_SUFFIX.search(n):
            return False
        parts = re.split(r"[·・\-\s]+", n)
        if len(parts) > 1 and parts[-1] in GENERIC_ROLE_SUFFIX:
            return False
        return len(e.get("chunk_ids") or []) >= MIN_CHUNKS

    keep = [e for e in roles if specific(e)]
    by_chunk: dict[str, set] = {}
    for e in keep:
        for cid in e["chunk_ids"]:
            by_chunk.setdefault(cid, set()).add(e["eid"])
    cooccur: dict[tuple[str, str], list[str]] = {}
    for cid, s in by_chunk.items():
        if 2 <= len(s) <= 8:
            for a, b in itertools.combinations(sorted(s), 2):
                cooccur.setdefault((a, b), []).append(cid)

    def exclusive(own, other, cats):
        ow, ot = names_of[own], names_of[other]
        return [cid for cid in ents[own].get("chunk_ids") or []
                if chunks.get(cid, {}).get("category") in cats
                and any(n in chunks[cid]["text"] for n in ow)
                and not any(n in chunks[cid]["text"] for n in ot)]

    pool = {}
    for tier, cats in (("character", {"character"}),
                       ("character+anecdote", {"character", "anecdote"})):
        for (a, b), shared in cooccur.items():
            if (a, b) in pool or len(shared) < MIN_CO:
                continue
            ea, eb = exclusive(a, b, cats), exclusive(b, a, cats)
            if ea and eb:
                pool[(a, b)] = {"tier": tier, "t_rank": 0 if tier == "character" else 1,
                                "anchor_a": ea, "anchor_b": eb}
    if len(pool) < N_PAIRS:
        raise SystemExit(f"[FATAL] 可用对仅 {len(pool)}，不足 {N_PAIRS}")

    rng = random.Random(SEED)
    ordered = sorted(rng.sample(sorted(pool.items(), key=lambda kv: kv[0]), len(pool)),
                     key=lambda kv: kv[1]["t_rank"])
    used: dict[str, int] = {}
    samples = []
    for (a, b), info in ordered:
        if used.get(a, 0) >= 3 or used.get(b, 0) >= 3:
            continue
        used[a] = used.get(a, 0) + 1
        used[b] = used.get(b, 0) + 1
        anchor_b = sorted(info["anchor_b"])[0]
        samples.append({
            "sample_id": f"CTL-{len(samples) + 1:03d}",
            "pair": {"a_eid": a, "a_name": ents[a]["name"],
                     "b_eid": b, "b_name": ents[b]["name"]},
            "query_type": "own_business",
            "prompt": QUERY.format(A=ents[a]["name"]),
            "perspective": ents[a]["name"],
            "retrieval_gold": {"b_private_chunk": anchor_b,
                               "b_name_forms": sorted(names_of[b]),
                               "a_name_forms": sorted(names_of[a])},
        })
        if len(samples) == N_PAIRS:
            break
    if len(samples) < N_PAIRS:
        raise SystemExit(f"[FATAL] 对照集只成对 {len(samples)}，不足 {N_PAIRS}")

    body = json.dumps({
        "schema": "compendium_rag.cbi_controlset/v1",
        "made_at": datetime.now().isoformat(timespec="seconds"),
        "graph_sha": sha, "seed": SEED, "n_samples": len(samples),
        "purpose": "与主集同判据、只把题面换成「问 A 自己的私事」，用来分离"
                   "「检索能力正常命中」与「边界真的失守」",
        "samples": samples}, ensure_ascii=False, indent=1)
    OUT.write_text(body, encoding="utf-8")
    print(f"[OK] 对照集 {len(samples)} 条 → {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
