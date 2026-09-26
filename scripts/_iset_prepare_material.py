# -*- coding: utf-8 -*-
"""题集 i · 材料准备：把 chunks.json 按章节分层切片成写手批次文件。

零网关、纯本地。写手只应看到 material/batch_XX.jsonl（chunk_id/chapter/scene/text 三字段），
不得接触 graph.json、候选表或任何模型输出。seed 固定，可复现。
"""
import json
import random
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHUNKS = ROOT / "data/compendium_rag/chunks.json"
OUTDIR = ROOT / "data/eval_set_i/material"
MANIFEST = ROOT / "data/eval_set_i/manifest_material.json"

SEED = 20260926
N_BATCH = 12
CHAR_BUDGET = 60_000      # 每批字符上限（写手单批可完整读完）
TARGET_TOTAL_CHUNKS = 720  # 全材料目标 chunk 数（≈19% 语料）
# 类目配比按语料占比定，保证 mainline/activity/character/anecdote 都有覆盖
CATEGORY_SHARE = {"mainline": 0.26, "activity": 0.37, "character": 0.13, "anecdote": 0.15, "appendix_unbound": 0.09}

rng = random.Random(SEED)


def main():
    chunks = json.loads(CHUNKS.read_text(encoding="utf-8"))["chunks"]
    by_doc = defaultdict(list)
    for c in chunks:
        by_doc[c["doc_id"]].append(c)
    for v in by_doc.values():
        v.sort(key=lambda x: x["chunk_id"])

    # 每章总字符
    doc_cat = {d: v[0]["category"] for d, v in by_doc.items()}
    doc_chars = {d: sum(len(x["text"]) for x in v) for d, v in by_doc.items()}

    # 分层抽章：类目内按随机序取章，直到达到该类目 chunk 配额
    quota = {k: int(TARGET_TOTAL_CHUNKS * s) for k, s in CATEGORY_SHARE.items()}
    picked: dict[str, list] = {}
    for cat in CATEGORY_SHARE:
        docs = [d for d in by_doc if doc_cat[d] == cat]
        rng.shuffle(docs)
        got = 0
        for d in docs:
            if got >= quota[cat]:
                break
            n = len(by_doc[d])
            if got + n > quota[cat] and got >= quota[cat] * 0.8:
                continue
            picked[d] = by_doc[d]
            got += n

    # 打包成批：整章装箱，超预算或超 chunk 数就开新批；单章过长按连续段拆开
    batches: list[list[tuple[str, dict]]] = []
    cur: list[tuple[str, dict]] = []
    cur_chars = 0
    order = sorted(picked, key=lambda d: (doc_cat[d], d), reverse=False)
    rng.shuffle(order)
    for d in order:
        pieces = picked[d]
        MAX_PER_CHUNK_SET = 90
        for i in range(0, len(pieces), MAX_PER_CHUNK_SET):
            seg = pieces[i:i + MAX_PER_CHUNK_SET]
            seg_chars = sum(len(x["text"]) for x in seg)
            if cur and (cur_chars + seg_chars > CHAR_BUDGET or len(cur) + len(seg) > 70):
                batches.append(cur)
                cur, cur_chars = [], 0
            cur.extend((d, c) for c in seg)
            cur_chars += seg_chars
    if cur:
        batches.append(cur)

    # 若批次少于 N_BATCH 也照实输出（不硬凑）
    OUTDIR.mkdir(parents=True, exist_ok=True)
    manifest = {"seed": SEED, "n_batch": len(batches), "batches": []}
    for i, b in enumerate(batches, 1):
        path = OUTDIR / f"batch_{i:02d}.jsonl"
        with path.open("w", encoding="utf-8") as f:
            for d, c in b:
                row = {"chunk_id": c["chunk_id"], "chapter": f"{c['chapter_title']}／{c['scene_title']}",
                       "text": c["text"]}
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        manifest["batches"].append({
            "batch": i, "file": str(path.relative_to(ROOT)),
            "n_chunks": len(b), "chars": sum(len(c["text"]) for _, c in b),
            "docs": sorted({d for d, _ in b}),
        })
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"批次 {len(batches)}，总 chunk {sum(len(b) for b in batches)}，"
          f"总字符 {sum(sum(len(c['text']) for _, c in b) for b in batches)}")
    for m in manifest["batches"]:
        print(f"  batch_{m['batch']:02d}: {m['n_chunks']} chunks / {m['chars']} chars / {len(m['docs'])} docs")


if __name__ == "__main__":
    main()
