# -*- coding: utf-8 -*-
"""题集 i · 阶段 2 收尾：合并盲识别子代理产出 → 白名单校验 → entity_map_i.json。

输入：data/eval_set_i/id_out/batch_XX.out.jsonl  每行 {"qid":..,"picks":[名字,..]}
白名单：data/compendium_rag/entity_candidates_i.json 的 candidates（逐题）
校验：
  - JSON 可解析率
  - 逐 token：pick 必须逐字出现在该 qid 的 candidates 中，否则记 illegal 并丢弃
  - 解析率闸门（计划书 §4）：合法题占比 ≥ 0.90
产物：data/compendium_rag/entity_map_i.json
  {"map": {qid: [合法名字]}, "illegal": {qid:[被弃名字]}, "meta": {...}}
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDS = ROOT / "data" / "compendium_rag" / "entity_candidates_i.json"
OUT_DIR = ROOT / "data" / "eval_set_i" / "id_out"
MAP_OUT = ROOT / "data" / "compendium_rag" / "entity_map_i.json"


def main() -> int:
    cands = json.loads(CANDS.read_text(encoding="utf-8"))
    whitelist = {q: set(v["candidates"]) for q, v in cands.items()}

    picks_by_qid: dict[str, list[str]] = {}
    unparsed = 0
    for f in sorted(OUT_DIR.glob("batch_*.out.jsonl")):
        for ln in f.read_text(encoding="utf-8").splitlines():
            ln = ln.strip()
            if not ln:
                continue
            try:
                o = json.loads(ln)
            except json.JSONDecodeError:
                unparsed += 1
                continue
            qid = str(o.get("qid", ""))
            pk = o.get("picks") or []
            if qid in picks_by_qid:  # 重复：先到先得
                continue
            picks_by_qid[qid] = [str(x).strip() for x in pk if str(x).strip()]

    legal_map: dict[str, list[str]] = {}
    illegal: dict[str, list[str]] = {}
    seen_tok = legal_tok = 0
    q_ok = 0
    for qid, pk in picks_by_qid.items():
        wl = whitelist.get(qid, set())
        kept = []
        bad = []
        ok = True
        for name in pk:
            seen_tok += 1
            if name in wl:
                kept.append(name)
                legal_tok += 1
            else:
                bad.append(name)
                ok = False
        legal_map[qid] = kept
        if bad:
            illegal[qid] = bad
        if ok:
            q_ok += 1

    total_q = len(cands)
    answered = len(picks_by_qid)
    parse_rate = q_ok / total_q if total_q else 0.0
    tok_rate = legal_tok / seen_tok if seen_tok else 1.0
    nonempty = sum(1 for v in legal_map.values() if v)

    meta = {
        "total_questions": total_q,
        "identified": answered,
        "missing_qids": sorted(set(cands) - set(picks_by_qid)),
        "unparsed_lines": unparsed,
        "questions_all_legal_rate": round(parse_rate, 4),
        "token_legal_rate": round(tok_rate, 4),
        "nonempty_pick_rate": round(nonempty / total_q, 4) if total_q else None,
        "gate_parse_90pct": parse_rate >= 0.90,
    }
    MAP_OUT.write_text(
        json.dumps({"source": "blind_subagents", "scope": "set_i_all",
                    "map": legal_map, "illegal": illegal, "meta": meta},
                   ensure_ascii=False, indent=1),
        encoding="utf-8")
    print(json.dumps(meta, ensure_ascii=False, indent=1))
    if illegal:
        print("== illegal picks (被白名单丢弃) ==")
        for q, b in list(illegal.items())[:40]:
            print(f"  {q}: {b}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
