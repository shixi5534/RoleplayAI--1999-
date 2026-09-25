# -*- coding: utf-8 -*-
"""云端质检：抽样审计 compendium 正典块的清洗质量（人机在环，**不改正文**）。

定位
    正文是官方正典，任何模型润色都会违反 N1/S1「事实保真」。（所以清洗靠确定性规则。）
    云端模型在这里只做**审计**：指出仍混入的非剧情内容 / 结构残留 / 乱码，
    并**归纳模式**，由人工把这些模式固化成确定性过滤器（``compendium_canon_corpus.py``）。
    模型产出**绝不直接写回语料**。

产出
    ``data/knowledge/_audit/compendium_qc.json`` + 控制台摘要

用法：
    .venv/Scripts/python.exe -X utf8 scripts/compendium_cloud_qc.py --sample 160 --batch-size 40
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from roleplay.config import get_settings  # noqa: E402

OUT = ROOT / "data" / "knowledge" / "_audit" / "compendium_qc.json"

SYSTEM = """你是《重返未来：1999》剧情语料的**结构质检员**。给你若干编号文本块，它们的正文\
应当是剧情内容（角色台词、旁白、标题卡、场景副标题）。

你的任务**只有一个**：找出**不是剧情正文**的混入物。允许的类别：
- "scaffolding" 残留结构：Markdown 链接、锚点、目录行、HTML 标签、`script 123` 之类
- "production"   制作/美术备注：如「剧情场景-…」「氛围图差分-…」「问下美术…」「复用场景」
- "gameplay"     玩法数值/技能/关卡说明：如「目标GOAL」「污染赋予Ⅲ」「持续2回合」「无法上场」
- "garbled"      乱码、编码错误、无意义字符
- "metadata"     非正文的元信息行（版本号、抓取日期等）

**严格禁止**报告以下内容（它们全部在职责之外，报告即视为错误）：
- 错别字、成语误用、语病、搭配不当、标点缺失
- 文风、语气、人称、逻辑、翻译质量问题
- 剧情内容本身的好坏、是否合理
- 任何要求改写、润色、修订正文的建议

对每个**确实混入非正文内容**的块输出一条记录：
- id: 块编号（整数）
- kind: 上面五类之一
- excerpt: 最能说明问题的一小段原文（≤40 字，原样摘录）
- why: 一句话理由（≤20 字）

再在 patterns 里归纳**可正则化的模式**（简短描述字符串数组）。

若某块全是正常剧情正文，**不要**为它输出任何记录。
只输出一个 JSON 对象，不要任何其他文字：
{"issues":[{"id":0,"kind":"production","excerpt":"…","why":"…"}],"patterns":["…"]}"""


def call_llm(client: httpx.Client, s, blocks: list[tuple[int, str]]) -> dict:
    # 每块截断到 400 字：质检只需要判断「这块是不是剧情正文」，
    # 不需要全文；截断同时也把 prompt 压到模型能稳定产出 JSON 的规模。
    lines = []
    for bid, text in blocks:
        lines.append(f"--- 块 {bid} ---\n{text[:400]}")
    payload = {
        "model": s.llm_model,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": "\n\n".join(lines)},
        ],
        "temperature": 0,
        # 这是**推理模型**：completion_tokens 里 reasoning 占绝大部分，
        # 8000 会被思考吃光导致 content 为空（实测 finish_reason=length）。
        "max_tokens": 32000,
    }
    r = client.post(
        s.llm_base_url.rstrip("/") + "/chat/completions",
        headers={"Authorization": "Bearer " + (s.llm_api_key or "")},
        json=payload,
        timeout=300.0,
    )
    r.raise_for_status()
    data = r.json()
    content = (data["choices"][0]["message"].get("content") or "").strip()
    # 容错：剥掉可能的 ```json 围栏
    m = re.search(r"\{.*\}", content, re.S)
    if not m:
        return {"issues": [], "patterns": [], "_raw": content[:400], "_parse": "failed"}
    try:
        out = json.loads(m.group(0))
        out["_parse"] = "ok"
        return out
    except ValueError:
        return {"issues": [], "patterns": [], "_raw": content[:400], "_parse": "bad-json"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=160)
    ap.add_argument("--batch-size", type=int, default=40)
    ap.add_argument("--seed", type=int, default=20260917)
    args = ap.parse_args()

    s = get_settings()
    corpus = json.loads(
        (Path(s.plot_corpus_dir) / "plot_corpus_wu_ming_zhe.json").read_text(encoding="utf-8"))
    cmp_chunks = [c for c in corpus["chunks"]
                  if c.get("source_kind") == "canon_zh"
                  and str(c.get("doc_id", "")).startswith("huiji_cmp_")]
    print(f"[qc] compendium chunks={len(cmp_chunks)}")

    rnd = random.Random(args.seed)
    sample = rnd.sample(cmp_chunks, min(args.sample, len(cmp_chunks)))
    # 编号即采样下标，便于回查
    blocks = [(i, c["text"]) for i, c in enumerate(sample)]
    print(f"[qc] sampled={len(blocks)} batch_size={args.batch_size}")

    all_issues: list[dict] = []
    all_patterns: list[str] = []
    stats = {"ok_calls": 0, "bad_calls": 0}

    with httpx.Client() as client:
        for start in range(0, len(blocks), args.batch_size):
            part = blocks[start:start + args.batch_size]
            t0 = time.time()
            try:
                res = call_llm(client, s, part)
            except Exception as e:  # noqa: BLE001
                stats["bad_calls"] += 1
                print(f"   [batch {start//args.batch_size}] ERROR {e}")
                continue
            if res.get("_parse") == "ok":
                stats["ok_calls"] += 1
            else:
                stats["bad_calls"] += 1
            for it in res.get("issues", []) or []:
                try:
                    bid = int(it.get("id"))
                except (TypeError, ValueError):
                    continue
                if 0 <= bid < len(sample):
                    it["doc_id"] = sample[bid].get("doc_id")
                    it["chunk_hash"] = sample[bid].get("hash")
                all_issues.append(it)
            all_patterns.extend(res.get("patterns", []) or [])
            print(f"   [batch {start//args.batch_size}] issues={len(res.get('issues', []) or [])} "
                  f"({time.time()-t0:.1f}s)")

    by_kind: dict[str, int] = {}
    for it in all_issues:
        k = str(it.get("kind") or "?")
        by_kind[k] = by_kind.get(k, 0) + 1

    print(f"\n[qc] calls ok={stats['ok_calls']} bad={stats['bad_calls']}")
    print(f"[qc] issues={len(all_issues)} by_kind={by_kind}")
    print(f"[qc] 采样块数={len(blocks)} 问题率={len(all_issues)/max(1,len(blocks))*100:.1f}%")
    print("\n[qc] 模型归纳的模式：")
    seen = set()
    for p in all_patterns:
        if p not in seen:
            seen.add(p)
            print(f"   - {p}")
    print("\n[qc] 问题样例：")
    for it in all_issues[:15]:
        print(f"   [{it.get('kind')}] {it.get('doc_id')} :: {it.get('excerpt')!r} — {it.get('why')}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "sample_size": len(blocks),
        "calls": stats,
        "by_kind": by_kind,
        "patterns": sorted(seen),
        "issues": all_issues,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[qc] 报告 → {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
