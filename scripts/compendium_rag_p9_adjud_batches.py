"""P9① · 为盲裁决子代理造批次（只读图与块，只写 reports/p9_fanout/w1/in/）。

选簇规则是确定性的，且**批次内容里不放任何泄漏标注、lift、我的倾向结论** ——
放上去子代理就会复述我的判断，盲评失效。它们只看到簇成员的名字、描述、原文摘录。

排序键：真跨语种（中英表判定）优先 → 节点数多者优先 → cluster_id 字典序。
每 5 簇一份文件，单文件控制在 ~40KB 内、单行 ≤100 字（子代理读大文件会被长行截断卡死）。
"""

from __future__ import annotations

import json
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "compendium_rag" / "reports" / "p9_fanout" / "w2" / "in"
CENSUS = ROOT / "data" / "compendium_rag" / "reports" / "p9_entity_census.json"
GRAPH = ROOT / "data" / "compendium_rag" / "graph.json"
CHUNKS = ROOT / "data" / "compendium_rag" / "chunks.json"
PER_BATCH, N_CLUSTERS, EXCERPT_CHARS = 5, 40, 220


def main() -> int:
    cen = json.loads(CENSUS.read_text(encoding="utf-8"))
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    ents = {e["eid"]: e for e in graph["entities"]}
    chunks = {c["chunk_id"]: c for c in json.loads(
        CHUNKS.read_text(encoding="utf-8"))["chunks"]}

    all_b = cen["list_b_unmerged_same_character"]
    # w1 盲裁决证明「编号族」是假候选（`圣殿骑士Ⅰ..Ⅵ` 尾号即消歧，10 簇里 8 簇判不同指），
    # 所以这里剔除 numbering，只送 cross_lang_alias 与 honorific_or_modifier 两族。
    cand = [c for c in all_b if c.get("family_kind") != "numbering"]
    picked = sorted(cand, key=lambda c: (c["family_kind"] != "cross_lang_alias",
                                         -c["n_entities"], c["cluster_id"]))[:N_CLUSTERS]
    print(f"     编号族剔除 {len(all_b) - len(cand)} 簇 · 真别名候选 {len(cand)} 簇 · "
          f"本波送裁决 {len(picked)} 簇")
    if not picked:
        print("[FATAL] 普查里没有可裁决的簇")
        return 2

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    n_files = 0
    for i in range(0, len(picked), PER_BATCH):
        group = picked[i:i + PER_BATCH]
        rows = []
        for cl in group:
            members = []
            for m in cl["members"]:
                e = ents.get(m["eid"]) or {}
                cids = [c for c in (e.get("chunk_ids") or [])
                        if chunks.get(c, {}).get("category") == "character"][:2]
                samples = [{"chunk_id": c, "category": chunks[c]["category"],
                            "text": textwrap.shorten(
                                (chunks[c].get("text") or "").replace("\n", " "),
                                width=EXCERPT_CHARS, placeholder=" …")} for c in cids]
                members.append({"eid": m["eid"], "name": m["name"],
                                "canonical_zh": m.get("canonical_zh"),
                                "entity_type": e.get("type"),
                                "n_chunk_ids": m["n_chunk_ids"],
                                "desc": textwrap.shorten(e.get("desc") or "",
                                                         width=EXCERPT_CHARS,
                                                         placeholder=" …"),
                                "samples": samples})
            rows.append({"cluster_id": cl["cluster_id"], "core": cl["core"],
                         "n_members": len(members), "members": members})
        body = json.dumps({"schema": "compendium_rag.p9_adjud_batch/v1",
                           "items": rows}, ensure_ascii=False, indent=1)
        # 不做整行折行：JSON 字符串里塞裸换行是非法的，json.loads 会炸。
        # 长行靠「字段内容预先 shorten」控制，这里只断言上限。
        longest = max((len(ln) for ln in body.splitlines()), default=0)
        if longest > 320:
            print(f"[FATAL] 出现 {longest} 字符的超长行，子代理 read 会被截断卡死")
            return 2
        f = OUT_DIR / f"adj_b{i // PER_BATCH + 1:02d}.json"
        f.write_text(body, encoding="utf-8")
        json.loads(f.read_text(encoding="utf-8"))       # 落盘后必须仍可解析
        n_files += 1
        print(f"  {f.name}: {len(rows)} 簇 / {f.stat().st_size} B / 最长行 {longest}")
    print(f"[OK] {n_files} 份批次，{len(picked)} 簇 → {OUT_DIR}")
    print("     下一步：compendium_rag_p9_fanout_guard.py plan --tag w1-adjud "
          "--in-dir <上面目录> --out-dir <w1/out> --out-pattern {stem}_verdict.json "
          "--qid-key cluster_id --protect " + str(OUT_DIR))
    return 0


if __name__ == "__main__":
    sys.exit(main())
