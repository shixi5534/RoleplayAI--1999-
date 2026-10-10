"""P9④ · 在 r11 图上重出 L4.5 多角色互洽判分面板（**不动 10-08 冻结件**）。

为什么不能直接跑 `audit_l4.py --mode multiscene --prep`：它把 `ms_bNN.json` 写进
`data/knowledge/_audit/l4_multiscene/`，会**覆写 10-08 那批已交评的输入件**；而抽取用的
图已经从 v8 变成 r11，抽到的块也不完全是同一批 —— 覆写就把历史盲评的样本基础毁掉了
（`audit_l4.py:254` 的注释讲得很清楚：「抽样一旦交评就冻结，否则盲评结果与样本脱钩」）。

抽取逻辑逐字照抄 `audit_l4.py:756-812 mode_multiscene(--prep)`：
  SEED=42 → 每块的角色数 ≥3 → `rng.shuffle` 后再 `sorted(cand)[:60]`
  （先洗再排是原实现刻意做的，否则抽到的全是「大会场」块 —— 别"优化"掉它）。
谓语归组用 **vendored** 词表 `compendium_rag.relation_vocab`（D1），不 import roleplay。

正文写成 `text_lines` 数组而不是单个长字符串：原面板的 json 最长行 3.4 万字符，
子代理的 read 工具会在超长单行上截断卡死（P8 实案）。这样每行短，内容不变。
"""

from __future__ import annotations

import hashlib
import json
import os
import random
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _k, _v in {"CMPRAG_LEX_WEIGHT": "1.0", "CMPRAG_RRF_K": "1",
               "CMPRAG_LEX_FIRST": "0", "PYTHONHASHSEED": "0"}.items():
    os.environ[_k] = _v
sys.path.insert(0, str(ROOT / "src"))

from compendium_rag.relation_vocab import classify_relation  # noqa: E402

GRAPH = ROOT / "data" / "compendium_rag" / "graph.json"
CHUNKS = ROOT / "data" / "compendium_rag" / "chunks.json"
SIDECAR = ROOT / "data" / "knowledge" / "_audit" / "predicate_grouping_v1.json"
FROZEN_IN = ROOT / "data" / "knowledge" / "_audit" / "l4_multiscene"
OUT_DIR = ROOT / "data" / "knowledge" / "_audit" / "l4_multiscene_r11"

EXPECTED_SHA = "911bb538160db80e"
SEED = 42                    # 与 audit_l4.py:36 同值，勿改
MIN_CHARS, N_ITEMS, BATCH = 3, 60, 20
MAX_LINE = 320               # 子代理 read 的长行上限，超了会截断卡死


def sha16_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()[:16]


def canon_of(sidecar_map):
    def f(rel: str):
        v = sidecar_map.get(rel)
        return v.get("canonical") if v is not None else classify_relation(rel)[0]
    return f


def main() -> int:
    sha = sha16_file(GRAPH)
    if sha != EXPECTED_SHA:
        raise SystemExit(f"[FATAL] 冻结图指纹漂移：期望 {EXPECTED_SHA}，实际 {sha}；不写文件")
    if (OUT_DIR / "panel_map.json").exists():
        raise SystemExit(f"[FATAL] 面板已生成过：{OUT_DIR}/panel_map.json 存在。"
                         f"已交评的面板不许重抽（样本与盲评必须同代），要重来请另起目录名。")

    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    chunks = {c["chunk_id"]: c for c in
              json.loads(CHUNKS.read_text(encoding="utf-8"))["chunks"]}
    ents = {e["eid"]: e for e in graph["entities"]}
    sidecar_map = json.loads(SIDECAR.read_text(encoding="utf-8"))["mapping"] \
        if SIDECAR.exists() else {}
    canon = canon_of(sidecar_map)

    chars = {e["eid"] for e in graph["entities"] if e.get("type") == "角色"}
    per_chunk: dict[str, set] = {}
    for e in graph["edges"]:
        if not e.get("chunk_ids"):
            continue
        cid = e["chunk_ids"][0]
        for side in (e["src"], e["dst"]):
            if side in chars:
                per_chunk.setdefault(cid, set()).add(side)
    cand = [cid for cid, s in per_chunk.items() if len(s) >= MIN_CHARS and cid in chunks]
    rng = random.Random(SEED)
    rng.shuffle(cand)
    picked = sorted(cand)[:N_ITEMS]
    if not picked:
        raise SystemExit("[FATAL] r11 图上抽不出 ≥3 角色的场景块")

    items = []
    for cid in picked:
        involved = per_chunk[cid]
        rows = []
        for e in graph["edges"]:
            if e.get("chunk_ids") and e["chunk_ids"][0] == cid \
                    and e["src"] in involved and e["dst"] in involved:
                rows.append({
                    "src": ents.get(e["src"], {}).get("name", e["src"]),
                    "relation": e.get("relation", ""),
                    "canonical": canon(e.get("relation", "")),
                    "dst": ents.get(e["dst"], {}).get("name", e["dst"]),
                    "evidence": (e.get("evidence") or "")[:80]})
        items.append({"chunk_id": cid,
                      "characters": sorted(ents[x]["name"] for x in involved if x in ents),
                      "edges": rows[:25],
                      "text_chars": len(chunks[cid]["text"][:2600]),
                      "text_lines": chunks[cid]["text"][:2600].splitlines() or [""]})

    # 与 10-08 冻结面板的重叠度 —— 决定新旧读数能不能直接比
    frozen_ids = set()
    for f in sorted(FROZEN_IN.glob("ms_b??.json")):
        frozen_ids |= {i["chunk_id"] for i in json.loads(
            f.read_text(encoding="utf-8")).get("items", [])}
    overlap = sorted(frozen_ids & {i["chunk_id"] for i in items})

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for bi in range(0, len(items), BATCH):
        grp = items[bi:bi + BATCH]
        body = json.dumps({
            "schema": "compendium_rag.p9_l45_input/v1",
            "task": "逐块判定这些角色之间的关系陈述是否与原文互洽（1~5 分）",
            "items": grp}, ensure_ascii=False, indent=1)
        longest = max(len(ln) for ln in body.splitlines())
        if longest > MAX_LINE:
            raise SystemExit(f"[FATAL] 批次出现 {longest} 字符超长行（上限 {MAX_LINE}），"
                             f"子代理 read 会截断 —— 把 text_lines 再切短")
        (OUT_DIR / f"ms_b{bi // BATCH + 1:02d}.json").write_text(body, encoding="utf-8")

    (OUT_DIR / "INSTRUCTIONS.md").write_text(
        "# L4.5 r11 判分须知（盲评）\n\n"
        "给每个块打 `coherence` 1~5 分：图谱里关于该块的角色关系陈述，是否与原文互洽。\n\n"
        "- 5 = 全部关系陈述都有原文依据、对象与方向都对；\n"
        "- 4 = 个别措辞偏差但不影响事实；\n"
        "- 3 = 有一处对象错张或方向颠倒；\n"
        "- 2 = 多处错，或关键关系无据；\n"
        "- 1 = 基本与原文不符。\n\n"
        "**不要参考任何历史评分**（10-08 面板与本批无关）。逐条独立判。\n\n"
        "输出文件结构（与 10-08 件同 schema，便于聚合）：\n\n"
        "```json\n"
        '{"schema":"audit.l4_multiscene_review/v1","batch":"bNN","items":['
        '{"chunk_id":"…","coherence":3,"n_edges":7,"n_mismatch":1,'
        '"mismatch":[{"src":"…","relation":"…","dst":"…","why":"…"}],'
        '"why":"一句话理由"}]}\n'
        "```\n\n"
        "必须覆盖本批**全部** chunk_id，一个不许漏；`n_edges` 照抄输入里该块的 edges 数。\n",
        encoding="utf-8")
    (OUT_DIR / "panel_map.json").write_text(json.dumps({
        "schema": "compendium_rag.p9_l45_panel_map/v1",
        "made_at": datetime.now().isoformat(timespec="seconds"),
        "graph_sha": sha, "seed": SEED, "n_items": len(items),
        "batches": {f"ms_b{bi // BATCH + 1:02d}": [i["chunk_id"] for i in items[bi:bi + BATCH]]
                    for bi in range(0, len(items), BATCH)},
        "overlap_with_2026_10_08_panel": {"frozen_n": len(frozen_ids),
                                          "r11_n": len(items), "overlap_n": len(overlap),
                                          "overlap_chunk_ids": overlap},
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"[OK] r11 面板 {len(items)} 块 / {(len(items) + BATCH - 1) // BATCH} 批 → {OUT_DIR}")
    print(f"     与 10-08 冻结面板重叠 {len(overlap)}/{len(items)} 块"
          f"（旧面板 {len(frozen_ids)} 块）")
    print("     下一步：guard plan --tag w4-l45 --in-dir <本目录> --in-glob \"ms_b??.json\" "
          "--qid-key chunk_id --out-dir <同目录> --out-pattern \"{stem}_review.json\"")
    return 0


if __name__ == "__main__":
    sys.exit(main())
