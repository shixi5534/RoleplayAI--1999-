# -*- coding: utf-8 -*-
"""抽取质量审计 · 第一步：生成分层抽样样本。

从剧情语料中抽 N 块，附带「本地 7B 模型的抽取结果（现有缓存）」，导出成
便于云端模型逐块重抽的 md + json。抽样分层：

  - ``contrib``：缓存非空的块（真正进图的主力），按语种/版本分层；
  - ``empty``  ：缓存为空的块（用于检查**漏抽**——本地模型是否该抽却没抽）；
  - ``cloud18``：之前由云端补抽的 18 块（对照组）。

产物：
  data/knowledge/_audit/sample.json   机读（含 text + local 抽取）
  data/knowledge/_audit/sample.md     可读（供云端模型逐块阅读重抽）

用法：
  python scripts/audit_sample_chunks.py --n-contrib 10 --n-empty 3 --n-cloud18 2
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from roleplay.config import get_settings  # noqa: E402

CLOUD18 = {
    "cd2a0d92e5ec8eb9", "4be44edf99ecf1ae", "9f1502e7a8b945b4", "ce4f4ec5c6f6fc43",
    "ae21a0e1cacae302", "6761b931d082cc4e", "2f0402a9ed09feb7", "25ee52e8898f2ead",
    "58e2b8696ba87295", "d6cf5f40c8bee74e", "839d82e10238842c", "a8c48a1bc81d3885",
    "ef77d6639051ad99", "28a719d8d9ef1687", "e56cec89bfc0e8d2", "3642207c78778d8b",
    "cbd85d3c306f0f3a", "3ff8f4686693eda9",
}


def _load_cache(cache_dir: Path, h: str) -> dict | None:
    p = cache_dir / f"{h}.json"
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else None
    except (OSError, ValueError):
        return None


def _pick(chunks: list[dict], n: int, rng: random.Random) -> list[dict]:
    """按 (lang, version) 分层均匀抽取，尽量覆盖不同版本。"""
    buckets: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for c in chunks:
        buckets[(c.get("lang") or "-", c.get("version") or "-")].append(c)
    keys = sorted(buckets)
    rng.shuffle(keys)
    out: list[dict] = []
    i = 0
    while len(out) < n:
        added = False
        for k in keys:
            if i < len(buckets[k]):
                out.append(buckets[k][i])
                added = True
                if len(out) >= n:
                    break
        if not added:
            break
        i += 1
    return out[:n]


def main() -> int:
    ap = argparse.ArgumentParser(description="剧情图谱抽取质量审计：生成抽样样本")
    ap.add_argument("--character", default="wu_ming_zhe")
    ap.add_argument("--n-contrib", type=int, default=10, help="非空缓存块抽样数")
    ap.add_argument("--n-empty", type=int, default=3, help="空缓存块抽样数（查漏抽）")
    ap.add_argument("--n-cloud18", type=int, default=2, help="云端补抽 18 块对照组抽样数")
    ap.add_argument("--seed", type=int, default=20260908)
    args = ap.parse_args()

    settings = get_settings()
    corpus_path = Path(settings.plot_corpus_dir) / f"plot_corpus_{args.character}.json"
    cache_dir = Path(settings.plot_cache_dir) / args.character
    if not corpus_path.is_file():
        print(f"[error] 语料不存在：{corpus_path}")
        return 1

    corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
    chunks = corpus["chunks"]
    rng = random.Random(args.seed)

    contrib, empty, cloud = [], [], []
    for c in chunks:
        data = _load_cache(cache_dir, c["hash"]) or {}
        has = bool(data.get("entities") or data.get("relations"))
        if c["hash"] in CLOUD18:
            cloud.append(c)
        elif has:
            contrib.append(c)
        else:
            empty.append(c)

    picked: list[tuple[str, dict]] = []
    for c in _pick(contrib, args.n_contrib, rng):
        picked.append(("contrib", c))
    for c in _pick(empty, args.n_empty, rng):
        picked.append(("empty", c))
    for c in rng.sample(cloud, min(args.n_cloud18, len(cloud))):
        picked.append(("cloud18", c))

    out_dir = ROOT / "data" / "knowledge" / "_audit"
    out_dir.mkdir(parents=True, exist_ok=True)

    records = []
    for group, c in picked:
        data = _load_cache(cache_dir, c["hash"]) or {}
        records.append(
            {
                "group": group,
                "hash": c["hash"],
                "meta": {
                    "lang": c.get("lang"),
                    "version": c.get("version") or "",
                    "arc": c.get("arc") or "",
                    "chapter": c.get("chapter") or "",
                    "doc_id": c.get("doc_id"),
                    "title": c.get("title") or "",
                },
                "text": c["text"],
                "local": {
                    "entities": data.get("entities") or [],
                    "relations": data.get("relations") or [],
                },
            }
        )

    (out_dir / "sample.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lines = [
        "# 剧情图谱抽取质量审计 · 抽样样本",
        "",
        f"- 角色：{args.character} ｜ 样本 {len(records)} 块"
        f"（contrib {args.n_contrib} / empty {args.n_empty} / cloud18 {args.n_cloud18}）",
        "- `本地结果` 是当前缓存里 **qwen2.5:7b** 的抽取；请对照正文用云端模型重新抽取并判定。",
        "",
    ]
    for i, r in enumerate(records, 1):
        m = r["meta"]
        lines += [
            f"## #{i} `{r['hash']}`　[{r['group']}] {m['lang']} {m['version']} {m['chapter']}",
            f"- 出处：{m['title'][:70]}", "",
            "### 正文", "",
            r["text"], "",
            "### 本地 7B 抽取结果", "",
            "```json",
            json.dumps(r["local"], ensure_ascii=False),
            "```", "",
        ]
    (out_dir / "sample.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"[audit] 语料 {len(chunks)} 块｜非空 {len(contrib)} / 空 {len(empty)} / cloud18 {len(cloud)}")
    print(f"[audit] 抽样 {len(records)} 块 → {out_dir / 'sample.json'}")
    print(f"[audit] 可读版 → {out_dir / 'sample.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
