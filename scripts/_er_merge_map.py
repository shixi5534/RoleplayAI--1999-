# -*- coding: utf-8 -*-
"""ER 阶段 2 收尾：合并主 agent 盲识别产出 → 双校验 → entity_map_<set>.json。

输入：data/compendium_rag/er2/<set>/picks_raw.tsv  每行 `qid<TAB>名1、名2`（空=弃答）
白名单：data/compendium_rag/entity_candidates_<set>.json 的逐题 candidates
校验（计划书 §4 阶段2 闸门）：
  1) 逐字出现在该 qid 的候选名表里，否则 illegal 并丢弃
  2) 能在图谱中 resolve 到实体（eid=规范名），否则 unresolved 并丢弃
  3) 全合法题占比 ≥ 0.90
产物：data/compendium_rag/entity_map_<set>.json（值 = 名字，图谱里 eid 即规范名）
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from compendium_rag import pipeline as P  # noqa: E402
from compendium_rag.config import get_settings  # noqa: E402
from compendium_rag.graph_store import GraphStore  # noqa: E402

SPLIT = re.compile(r"[、,，]")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", choices=["native", "300_cn", "i"], required=True)
    ap.add_argument("--dry-run", action="store_true", help="只算闸门数字，不覆盖既有映射文件")
    args = ap.parse_args()

    ER = ROOT / "data" / "compendium_rag" / "er2" / args.set
    picks_file = ER / "picks_raw.tsv"
    if not picks_file.exists():  # native 轮的历史布局：er2/picks_raw.tsv
        legacy = ROOT / "data" / "compendium_rag" / "er2" / "picks_raw.tsv"
        if legacy.exists():
            picks_file = legacy
    if not picks_file.exists():
        raise SystemExit(f"找不到识别产物：{ER / 'picks_raw.tsv'}")
    cands = json.loads(
        (ROOT / "data" / "compendium_rag" / f"entity_candidates_{args.set}.json")
        .read_text(encoding="utf-8"))
    graph = GraphStore.load(get_settings().graph_path)

    whitelist = {q: set(v["candidates"]) for q, v in cands.items()}
    picks_by_qid: dict[str, list[str]] = {}
    for ln in picks_file.read_text(encoding="utf-8").splitlines():
        if not ln.strip():
            continue
        parts = ln.split("\t")
        qid = parts[0].strip()
        names = [x.strip() for x in SPLIT.split(parts[1]) if x.strip()] if len(parts) > 1 else []
        if qid in picks_by_qid:
            raise SystemExit(f"重复 qid: {qid}")
        picks_by_qid[qid] = names

    legal_map: dict[str, list[str]] = {}
    illegal: dict[str, list[str]] = {}
    unresolved: dict[str, list[str]] = {}
    seen_tok = kept_tok = q_ok = 0
    for qid, pk in picks_by_qid.items():
        wl = whitelist.get(qid, set())
        kept, bad, unres = [], [], []
        for name in pk:
            seen_tok += 1
            if name not in wl:
                bad.append(name)
                continue
            if name not in graph.entities:
                unres.append(name)
                continue
            kept.append(name)
            kept_tok += 1
        legal_map[qid] = kept
        if bad:
            illegal[qid] = bad
        if unres:
            unresolved[qid] = unres
        if not bad and not unres:
            q_ok += 1

    total_q = len(cands)
    parse_rate = q_ok / total_q if total_q else 0.0
    nonempty = sum(1 for v in legal_map.values() if v)
    meta = {
        "set": args.set,
        "total_questions": total_q,
        "rows_in_tsv": len(picks_by_qid),
        "missing_qids": sorted(set(cands) - set(picks_by_qid)),
        "extra_qids": sorted(set(picks_by_qid) - set(cands)),
        "token_proposed": seen_tok,
        "token_kept": kept_tok,
        "token_legal_rate": round(kept_tok / seen_tok, 4) if seen_tok else 1.0,
        "questions_all_legal_rate": round(parse_rate, 4),
        "nonempty_pick_rate": round(nonempty / total_q, 4) if total_q else None,
        "gate_parse_90pct": parse_rate >= 0.90,
    }
    out = ROOT / "data" / "compendium_rag" / f"entity_map_{args.set}.json"
    text = json.dumps(
        {"source": "main_agent_blind_identification", "scope": f"{args.set}_all",
         "note": "只见 q+候选名；空数组=弃答；值即图谱规范名(eid)",
         "map": legal_map, "illegal": illegal, "unresolved": unresolved, "meta": meta},
        ensure_ascii=False, indent=1)
    if not args.dry_run:
        out.write_text(text, encoding="utf-8")
    print(json.dumps(meta, ensure_ascii=False, indent=1))
    for label, d in (("illegal", illegal), ("unresolved", unresolved)):
        if d:
            print(f"== {label} ==")
            for q, b in sorted(d.items()):
                print(f"  {q}: {b}")
    print(("[dry-run] 未写入 " if args.dry_run else "映射 → ") + str(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
