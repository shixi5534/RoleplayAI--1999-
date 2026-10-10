"""P9 · CBI 检索通道执行器：对 500 条样本以 A 视角跑 top-6 检索，记 N_retrieval。

只读测试集与图；只写 `reports/cbi/retrieval.jsonl`（按 sample_id 续跑，崩了不重来）。
口径 env 与 P8 影子评测同款钉死；图指纹不符即退出且不写任何文件。

判据（B 私有知识进榜）：top-6 里出现「正文提 B 名号但不提 A 名号」的 character/anecdote 块
⇒ 该样本记一次检索泄漏；同时单独记 `b_private_chunk` 是否进榜（测试集里钉死的那条金标）。
两个口径都写出来，避免一个定义把另一个掩盖掉。

⚠ 这 500 条是对抗性 prompt，**没有相关性金标**，所以本文件不算 MRR。验收里「MRR ≥0.39
不回退」指的是三个主口径集（300cn/blind206/gen120），任何改动后要在那三集上重测，见
`reports/eval_*_k1_r11.json`。
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _k, _v in {"CMPRAG_LEX_WEIGHT": "1.0", "CMPRAG_RRF_K": "1",
               "CMPRAG_LEX_FIRST": "0", "PYTHONHASHSEED": "0"}.items():
    os.environ[_k] = _v
sys.path.insert(0, str(ROOT / "src"))

from compendium_rag import pipeline as P  # noqa: E402
from compendium_rag.config import get_settings  # noqa: E402

# 同一份代码跑主集与对照集：CBI_TESTSET 选题面，CBI_TAG 分文件，避免两组产物混在一起
TESTSET = Path(os.environ.get(
    "CBI_TESTSET", str(ROOT / "data" / "compendium_rag" / "reports" / "cbi_testset_500.json")))
TAG = os.environ.get("CBI_TAG", "")
OUT_DIR = ROOT / "data" / "compendium_rag" / "reports" / "cbi"
OUT = OUT_DIR / f"retrieval{TAG}.jsonl"
HB = OUT_DIR / f"retrieval{TAG}_heartbeat.txt"
GRAPH = ROOT / "data" / "compendium_rag" / "graph.json"
CHUNKS = ROOT / "data" / "compendium_rag" / "chunks.json"
EXPECTED_SHA = "911bb538160db80e"
TOP_K = 6
PRIVATE_CATS = ("character", "anecdote")


def sha16(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()[:16]


def beat(msg: str) -> None:
    HB.parent.mkdir(parents=True, exist_ok=True)
    with HB.open("a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%H:%M:%S')} {msg}\n")


async def run() -> int:
    sha = sha16(GRAPH)
    if sha != EXPECTED_SHA:
        raise SystemExit(f"[FATAL] 图指纹漂移 {sha} != {EXPECTED_SHA}，不写任何文件")
    ts = json.loads(TESTSET.read_text(encoding="utf-8"))
    samples = ts["samples"]
    chunks = {c["chunk_id"]: c for c in
              json.loads(CHUNKS.read_text(encoding="utf-8"))["chunks"]}
    private_ids = {cid for cid, c in chunks.items() if c.get("category") in PRIVATE_CATS}

    done = {}
    if OUT.exists():
        for line in OUT.read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(line)
                done[r["sample_id"]] = r
            except json.JSONDecodeError:
                continue            # 崩溃时的半行：忽略，按未跑处理
    todo = [s for s in samples if s["sample_id"] not in done]
    limit = int(os.environ.get("CBI_LIMIT", "0"))
    if limit:
        todo = todo[:limit]          # 冒烟用：先跑几条确认管线通，再放开全量
    beat(f"start total={len(samples)} done={len(done)} todo={len(todo)} limit={limit}")
    print(f"total={len(samples)} 已完成={len(done)} 待跑={len(todo)}", flush=True)
    if not todo:
        return 0

    s = get_settings()
    kb = P.load_kb(s)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    leaks = 0
    with OUT.open("a", encoding="utf-8") as fh:
        for i, sm in enumerate(todo, start=1):
            t0 = time.time()
            res = await kb.retrieve(sm["prompt"], top_k=TOP_K)
            top_ids = [ev["chunk_id"] for ev in res.get("evidence", [])[:TOP_K]]
            gold = sm["retrieval_gold"]
            b_forms, a_forms = set(gold["b_name_forms"]), set(gold["a_name_forms"])
            b_priv_hits = [cid for cid in top_ids
                           if cid in private_ids
                           and any(nm in chunks[cid]["text"] for nm in b_forms)
                           and not any(nm in chunks[cid]["text"] for nm in a_forms)]
            rec = {
                "sample_id": sm["sample_id"],
                # 字段名别再叫 pair：这里存的是**视角角色 A**，写 pair 会让读日志的人
                # 把它当成 B（本会话就误读过一次）
                "a_name": sm["pair"]["a_name"], "b_name": sm["pair"]["b_name"],
                "perspective": sm["perspective"], "query_type": sm.get("query_type", ""),
                "conflict_type": sm.get("conflict_type", ""), "prompt": sm["prompt"],
                "top_ids": top_ids,
                "seeds": [x["name"] for x in res.get("seeds", [])],
                "b_private_chunk_hit": gold["b_private_chunk"] in top_ids,
                "b_private_hits": b_priv_hits,
                "retrieval_leak": bool(b_priv_hits) or gold["b_private_chunk"] in top_ids,
                "seconds": round(time.time() - t0, 3),
            }
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            fh.flush()
            n += 1
            leaks += 1 if rec["retrieval_leak"] else 0
            if i % 10 == 0:
                beat(f"{i}/{len(todo)} 累计检索泄漏 {leaks}（{(leaks / i):.3f}）")
    beat(f"完成 {n} 条")
    print(f"[OK] 新跑 {n} 条 → {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(run()))
