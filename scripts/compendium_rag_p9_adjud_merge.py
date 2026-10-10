"""P9① · 把两波盲裁决合成 add_alias 提案（只读裁决件与图，只写 reports/ 下两个文件）。

**绝不改图**：产物是给 `scripts/_graph_apply_repairs.py --proposal` 干的**输入**，
而那是写盘通道，必须由用户单独批准。本脚本只保证「格式喂得进去 + 每条带证据与档位」。

三道门（缺一个就会造出假修复）：
1. 置信度分档：≥0.60 且别名在语料逐字出现 → tier_A（可直接 dry-run）；否则 tier_B（需人复核）；
   `insufficient` / `different_reference` 一律进 rejected 并留理由 —— 负结果也是结果。
2. 语料逐字：alias 字符串必须能在某个块正文里逐字出现。applier 对 `add_alias` 会报
   `add_alias 语料无逐字（inferred?）`；`merge_entities` 不报，所以这里用它作分档依据。
3. 撞名拦截：alias 若正好是**本簇之外**另一个实体的本名，合并会连带改指 —— 一律不自动提，
   按对称 DROP_MAP 纪律交人工（`优化计划_v9_2026-10-08.md:138,162`）。
"""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "data" / "compendium_rag" / "reports"
FANOUT = REPORTS / "p9_fanout"
GRAPH = ROOT / "data" / "compendium_rag" / "graph.json"
CHUNKS = ROOT / "data" / "compendium_rag" / "chunks.json"
OUT_JSON = REPORTS / "p9_entity_proposals.json"
OUT_MD = REPORTS / "p9_entity_proposals.md"

EXPECTED_SHA = "911bb538160db80e"
WAVES = ("w1-adjud", "w2-adjud")
CONF_A, CONF_B = 0.60, 0.50


def sha16_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()[:16]


def main() -> int:
    sha = sha16_file(GRAPH)
    if sha != EXPECTED_SHA:
        raise SystemExit(f"[FATAL] 冻结图指纹漂移：期望 {EXPECTED_SHA}，实际 {sha}；不写文件")
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    ents = {e["eid"]: e for e in graph["entities"]}
    name_owners: dict[str, set[str]] = {}
    for e in graph["entities"]:
        name_owners.setdefault(e["name"], set()).add(e["eid"])
    corpus_blob = "\n".join((c.get("text") or "") for c in
                            json.loads(CHUNKS.read_text(encoding="utf-8"))["chunks"])

    cen = json.loads((REPORTS / "p9_entity_census.json").read_text(encoding="utf-8"))
    kind = {c["cluster_id"]: c.get("family_kind") for c in cen["list_b_unmerged_same_character"]}

    entries, rejected, batches_seen = [], [], 0
    for wave in WAVES:
        for vfile in sorted((FANOUT / wave.split("-")[0] / "out").glob("*_verdict.json")):
            v = json.loads(vfile.read_text(encoding="utf-8"))
            batches_seen += 1
            for item in v.get("items") or []:
                cid = item.get("cluster_id")
                verdict, conf = item.get("verdict"), item.get("confidence")
                groups = [g for g in (item.get("groups") or []) if len(g) >= 2]
                if verdict in ("different_reference", "insufficient") or not groups:
                    rejected.append({"cluster_id": cid, "verdict": verdict,
                                     "confidence": conf, "reason": item.get("reason"),
                                     "family_kind": kind.get(cid), "wave": wave,
                                     "why_rejected": ("判负/证据不足" if verdict in
                                                      ("different_reference", "insufficient")
                                                      else "没有任何一组有 ≥2 成员")})
                    continue
                for grp in groups:
                    members = [ents[i] for i in grp if i in ents]
                    if len(members) < 2:
                        continue
                    owner = max(members, key=lambda e: (len(e.get("chunk_ids") or []),
                                                        e["eid"]))
                    # **不能用 add_alias**：graph_store.from_dict 的别名冲突规则是「实体自身
                    # name 等于该别名者优先」，而这里要加的 alias 恰好是被并方的**本名**，
                    # 加完别名仍归它自己持有，两个节点谁也没并起来 —— 那是条空操作。
                    # 只有 merge_entities 会搬 aliases / chunk_ids / mentions。
                    for m in [x for x in members if x["eid"] != owner["eid"]]:
                        alias = m["name"]
                        other_owners = (name_owners.get(alias, set())
                                        - {x["eid"] for x in members})
                        verbatim = alias in corpus_blob
                        tier = ("tier_A" if conf is not None and conf >= CONF_A and verbatim
                                else "tier_B")
                        if other_owners:
                            rejected.append({
                                "cluster_id": cid, "verdict": verdict, "confidence": conf,
                                "alias": alias, "owner_eid": owner["eid"],
                                "family_kind": kind.get(cid), "wave": wave,
                                "why_rejected": (
                                    f"撞名拦截：`{alias}` 还同时是**本簇之外**实体 "
                                    f"{sorted(other_owners)} 的本名，合并会连带改指，"
                                    f"按对称 DROP_MAP 交人工")})
                            continue
                        entries.append({
                            "type": "merge_entities",
                            "target": f"{m['eid']}→{owner['eid']}",
                            "tier": tier, "confidence": conf, "cluster_id": cid,
                            "family_kind": kind.get(cid), "wave": wave,
                            "absorbed_alias": alias,
                            "verbatim_in_corpus": verbatim,
                            "owner_chunk_ids": len(owner.get("chunk_ids") or []),
                            "loser_chunk_ids": len(m.get("chunk_ids") or []),
                            "evidence": item.get("reason"),
                        })
    if batches_seen == 0:
        print("[FATAL] 两波都没有裁决件，提案为空")
        return 2

    tiers = Counter(e["tier"] for e in entries)
    rep = {
        "schema": "compendium_rag.p9_entity_proposals/v1",
        "done_at": datetime.now().isoformat(timespec="seconds"),
        "graph_sha": sha,
        "applier": "scripts/_graph_apply_repairs.py --proposal <本文件>（默认 dry-run；"
                   "写盘需用户单独批准）",
        "gates": {"confidence_tier_A": CONF_A, "confidence_tier_B": CONF_B,
                  "verbatim_required_for_tier_A": True,
                  "name_collision_policy": "簇外实体本名同名 → 拦截，交人工（对称 DROP_MAP）"},
        "counts": {"verdict_files": batches_seen, "entries": len(entries),
                   "rejected": len(rejected), **dict(tiers)},
        "entries": entries,
        "rejected": rejected,
        "not_applied": "本文件只是提案。图未改动，sha 仍为 " + sha,
    }
    OUT_JSON.write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")

    ln = ["# P9① 实体归并提案（盲裁决合成，**未落图**）", "",
          f"生成 {rep['done_at']} · 冻结图 `{sha}` · 裁决件 {batches_seen} 份 · "
          f"提案 {len(entries)} 条（{dict(tiers)}）· 拦截/判负 {len(rejected)} 条", "",
          "算子一律是 `merge_entities`（`被并方→属主`），**不是** `add_alias` —— 别名冲突规则"
          "「实体自身 name 等于该别名者优先」会让 add_alias 在这种场合变成空操作。",
          "",
          "执行入口：`scripts/_graph_apply_repairs.py --proposal "
          "<本文件> `（默认 dry-run，`--apply` 才写盘 —— **需用户批准**）", "",
          "## tier_A（置信 ≥0.60 且别名在语料逐字出现）", ""]
    for e in [x for x in entries if x["tier"] == "tier_A"]:
        ln.append(f"- **{e['target']}**（吸收别名 `{e['absorbed_alias']}`，"
                  f"{e['loser_chunk_ids']}块 → 属主 {e['owner_chunk_ids']}块，"
                  f"置信 {e['confidence']}，{e['family_kind']}，簇 `{e['cluster_id']}`）")
        ln.append(f"  - 依据：{e['evidence']}")
    ln += ["", "## tier_B（需人复核：置信不足或别名语料无逐字）", ""]
    for e in [x for x in entries if x["tier"] == "tier_B"]:
        ln.append(f"- **{e['target']}**（`{e['absorbed_alias']}`，置信 {e['confidence']}，"
                  f"逐字 {e['verbatim_in_corpus']}，簇 `{e['cluster_id']}`）｜{e['evidence']}")
    ln += ["", "## 拦截与判负（负结果留痕）", ""]
    for r in rejected:
        ln.append(f"- `{r['cluster_id']}` {r['verdict']}（{r['confidence']}，"
                  f"{r['family_kind']}）← {r['why_rejected']}")
        if r.get("reason"):
            ln.append(f"  - 裁决理由：{r['reason']}")
    OUT_MD.write_text("\n".join(ln) + "\n", encoding="utf-8")

    if sha16_file(GRAPH) != sha:
        raise SystemExit("[FATAL] 图被改动 —— 本脚本只该读图")
    print(f"[OK] 提案 {len(entries)} 条（tier_A {tiers['tier_A']} / tier_B "
          f"{tiers['tier_B']}）· 拦截判负 {len(rejected)} 条 · 裁决件 {batches_seen} 份")
    print(f"     {OUT_JSON}\n     {OUT_MD}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
