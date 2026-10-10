# -*- coding: utf-8 -*-
"""v9-P2 前置诊断（**只读**，不写 graph.json / cache）：实体落地与孤立率归因。

要回答的三个问题——P2 的三类分诊全靠它们定夺：

1. 这个名字在语料里**逐字存在**吗？（CHRONICLE 2026-09-26 记 1089/7033 名不落地、
   967 个名字全语料不存在；本轮要在 v9-a 图上重测，因为 P1 改过边、别名焊过几轮）
2. 它孤立吗？孤点和「名不落地」是不是同一批实体？（不接地 = 名字通道死键；
   接地但无边 = 真·一次性提及，两者治法相反，混了就白干）
3. 能靠什么治？别名可落地 / 修饰语前缀里有真名 / 纯噪声 / 真孤点——只有前两类
   能走 add_alias / remove_alias 提案，后两类必须显式披露而不是偷偷删。

顺带把 P1 的副作用单独归因：谓语合并理论上不该制造新孤点（合并不改端点），
但否定式/垃圾谓语被丢的 147 条边可能把只剩一条边的实体打成孤点。对比 v8 备份
的孤点集即可判定。

用法（项目根目录）：
  PYTHONPATH=src .venv/Scripts/python.exe -X utf8 scripts/compendium_rag_p2_landing_diag.py
"""
from __future__ import annotations

import json
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from compendium_rag import pipeline as P  # noqa: E402
from compendium_rag.config import get_settings  # noqa: E402
from compendium_rag.graph_store import GraphStore  # noqa: E402

OUT = ROOT / "data/compendium_rag/reports/p2_landing_diag.json"
MD = ROOT / "data/compendium_rag/reports/p2_landing_diag.md"
V8_BACKUP = (ROOT / "data/compendium_rag/backups/"
             "graph.json.v8_frozen_026b41699f021db2")

# 半截名 / 噪声名的启发式：长度<=1、纯数字、含引号书名号残片。
# 注意这**只是分诊线索**，不是删除依据——删实体要人工点头。
_NOISE_CHARS = set("“”\"'（）()《》〈〉【】[]、，。．.·-—~〜/\\")


def _now() -> str:
    return time.strftime("%H:%M:%S")


def _degrees(g: GraphStore) -> Counter:
    deg: Counter = Counter()
    for e in g.edges:
        deg[e.src] += 1
        deg[e.dst] += 1
    return deg


def _isolated(g: GraphStore, deg: Counter) -> set[str]:
    return {eid for eid in g.entities if deg[eid] == 0}


def _title_and_meta_text(chapters: list) -> str:
    """标题/文件名/栏目也参与「逐字存在」判定：专名常常只出现在篇名里。"""
    bits: list[str] = []
    for ch in chapters:
        bits.extend([ch.title or "", ch.category or "", ch.source_file or ""])
    return "\n".join(bits)


def main() -> int:
    s = get_settings()
    print(f"[{_now()}] 读语料…")
    chapters = P.load_chapters(s)
    chunks = P.chunk_corpus(chapters, s)
    print(f"[{_now()}] 语料：{len(chapters)} 篇 / {len(chunks)} 块")

    chunk_text = {c.chunk_id: (c.text or "") for c in chunks}
    corpus_text = "\n".join(chunk_text.values())
    meta_text = _title_and_meta_text(chapters)
    whole = corpus_text + "\n" + meta_text
    print(f"[{_now()}] 语料字符数={len(corpus_text)} 元信息={len(meta_text)}")

    g = GraphStore.load(s.graph_path)
    deg = _degrees(g)
    iso = _isolated(g, deg)

    # ── 逐实体：名字/别名在不在语料里 ──
    rows: list[dict] = []
    t0 = time.time()
    for i, (eid, ent) in enumerate(g.entities.items(), 1):
        name = (ent.name or "").strip()
        aliases = [a.strip() for a in (ent.aliases or []) if a and a.strip()]
        in_corpus = bool(name) and name in whole
        in_meta = (not in_corpus) and bool(name) and name in meta_text
        alias_hits = [a for a in aliases if a in whole]
        claimed = ent.chunk_ids or []
        in_claimed = any(name in chunk_text.get(cid, "") for cid in claimed)
        rows.append({
            "eid": eid,
            "name": name,
            "type": ent.type,
            "degree": deg[eid],
            "isolated": eid in iso,
            "n_aliases": len(aliases),
            "name_in_corpus": in_corpus,
            "name_only_in_meta": in_meta,
            "alias_in_corpus": alias_hits[:4],
            "claimed_chunks": len(claimed),
            "in_claimed_chunk": in_claimed,
            "mentions": ent.mentions,
            "has_desc": bool(ent.desc),
        })
        if i % 1500 == 0:
            print(f"[{_now()}] 落地判定 {i}/{len(g.entities)}"
                  f"（{time.time() - t0:.1f}s）")

    # ── 分诊 ──
    def classify(r: dict) -> str:
        if r["name_in_corpus"]:
            return "anchored"
        if r["alias_in_corpus"]:
            # 名字不接地但某个别名接地：走 add_alias/别名落地，别动边
            return "alias_landable"
        if r["name_only_in_meta"]:
            return "meta_only"
        if len(r["name"]) <= 1 or (_NOISE_CHARS & set(r["name"])):
            return "noise_name"
        return "dead_key"

    by_class: Counter = Counter()
    iso_by_class: Counter = Counter()
    for r in rows:
        c = classify(r)
        r["landing_class"] = c
        by_class[c] += 1
        if r["isolated"]:
            iso_by_class[c] += 1

    # 修饰语前缀线索：dead_key 的名字里是否包着另一个「接地且连通」实体的名。
    # 例：店主米拉 ⊃ 米拉。这类不能自动合并——按别名焊接纪律要人工裁决。
    grounded_connected = {
        r["name"] for r in rows
        if r["name_in_corpus"] and not r["isolated"] and len(r["name"]) >= 2
    }
    prefix_candidates: list[dict] = []
    for r in rows:
        if r["landing_class"] not in ("dead_key", "noise_name", "meta_only"):
            continue
        nm = r["name"]
        hits = [m for m in grounded_connected if m != nm and m in nm
                and len(nm) - len(m) <= 6]
        if hits:
            hits.sort(key=len, reverse=True)
            prefix_candidates.append({
                "name": nm, "type": r["type"], "isolated": r["isolated"],
                "core": hits[0], "cores": hits[:4],
            })

    # ── P1 副作用归因：与 v8 备份的孤点集对比 ──
    p1_delta = None
    if V8_BACKUP.is_file():
        g8 = GraphStore.load(V8_BACKUP)
        deg8 = _degrees(g8)
        iso8 = _isolated(g8, deg8)
        newly = sorted(iso - iso8)
        healed = sorted(iso8 - iso)
        nm8 = {eid: g8.entities[eid].name for eid in newly}
        p1_delta = {
            "isolated_v8": len(iso8),
            "isolated_v9p1": len(iso),
            "newly_isolated": len(newly),
            "newly_isolated_names": [nm8[e] for e in newly][:40],
            "no_longer_isolated": len(healed),
            "no_longer_isolated_names": [
                g8.entities[e].name for e in healed][:40],
        }

    stats = {
        "graph_sha256_16": __import__("hashlib").sha256(
            s.graph_path.read_bytes()).hexdigest()[:16],
        "entities": len(g.entities),
        "edges": len(g.edges),
        "isolated": len(iso),
        "isolated_ratio": round(len(iso) / len(g.entities), 6)
        if g.entities else None,
        "landing_class_counts": dict(by_class.most_common()),
        "isolated_by_landing_class": dict(iso_by_class.most_common()),
        "name_in_corpus": sum(1 for r in rows if r["name_in_corpus"]),
        "name_not_in_corpus": sum(1 for r in rows if not r["name_in_corpus"]),
        "alias_present_entities": sum(1 for r in rows if r["n_aliases"]),
        "dead_key_ungrounded": by_class["dead_key"],
        "prefix_candidates": len(prefix_candidates),
        "overlap_isolated_and_ungrounded": sum(
            1 for r in rows if r["isolated"] and not r["name_in_corpus"]),
        "overlap_isolated_but_grounded": sum(
            1 for r in rows if r["isolated"] and r["name_in_corpus"]),
    }

    def _sample(cls: str, k: int = 25) -> list[str]:
        out = [r["name"] for r in rows if r["landing_class"] == cls
               and r["isolated"]]
        if len(out) < k:
            out += [r["name"] for r in rows if r["landing_class"] == cls
                    and not r["isolated"]][: k - len(out)]
        return out[:k]

    rep = {
        "schema": "compendium_rag.p2_landing_diag/v1",
        "mode": "read-only",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "note": "只读诊断：未写 graph.json / cache；分桶只是线索，删实体需人工裁决",
        "stats": stats,
        "p1_isolation_delta": p1_delta,
        "samples": {c: _sample(c) for c in by_class},
        "prefix_candidates_top": sorted(
            prefix_candidates, key=lambda d: (not d["isolated"], d["name"]))[:120],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# v9-P2 前置诊断：实体落地 × 孤立率",
        "",
        f"- 图谱 SHA256-16：`{stats['graph_sha256_16']}`（只读，未改动）",
        f"- 实体 {stats['entities']} / 边 {stats['edges']} / 孤立 "
        f"{stats['isolated']}（{stats['isolated_ratio']}）",
        f"- 名字逐字存在于语料（含篇名/栏目）：{stats['name_in_corpus']}；"
        f"不存在：{stats['name_not_in_corpus']}",
        f"- 孤点里「名不接地」{stats['overlap_isolated_and_ungrounded']} 个、"
        f"「名接地但无边」{stats['overlap_isolated_but_grounded']} 个"
        "——这两类治法相反",
        "",
        "## 分诊桶（全部实体）",
        "",
        "| 类别 | 实体数 | 其中孤点 | 含义与治法 |",
        "| --- | --- | --- | --- |",
    ]
    meaning = {
        "anchored": "名字逐字在正文里 → 落地正常，孤点只能靠补边/别名治",
        "alias_landable": "本名不接地但别名接地 → add_alias 提案可救",
        "meta_only": "只在篇名/栏目里出现 → 可落地性弱，单独披露",
        "noise_name": "含噪声字符或过短 → remove_alias / 删实体候选（需人工）",
        "dead_key": "全语料逐字不存在 → 抽取补名幻觉，name-key 通道死键",
    }
    for c, n in by_class.most_common():
        lines.append(f"| {c} | {n} | {iso_by_class.get(c, 0)} | {meaning.get(c, '')} |")
    lines += ["", "## 孤点成因拆分", ""]
    tot_iso = stats["isolated"]
    lines.append(
        f"- 名接地、却没有任何边：{stats['overlap_isolated_but_grounded']}"
        f"（占孤点 {stats['overlap_isolated_but_grounded'] / tot_iso:.4f}）"
        " → 真·一次性提及 / 补边范畴")
    lines.append(
        f"- 名不接地：{stats['overlap_isolated_and_ungrounded']}"
        f"（占孤点 {stats['overlap_isolated_and_ungrounded'] / tot_iso:.4f}）"
        " → 别名落地或删除范畴")
    if p1_delta:
        lines += [
            "",
            "## P1 副作用归因（对比 v8 备份孤点集）",
            "",
            f"- v8 孤立 {p1_delta['isolated_v8']} → v9-a 孤立 "
            f"{p1_delta['isolated_v9p1']}（新孤点 {p1_delta['newly_isolated']}，"
            f"脱孤 {p1_delta['no_longer_isolated']}）",
            f"- 新孤点样例：{'、'.join(p1_delta['newly_isolated_names'][:20])}",
        ]
    lines += ["", "## 各桶样例", ""]
    for c, names in rep["samples"].items():
        lines.append(f"- **{c}**：{'、'.join(names[:20])}")
    lines += ["", f"## 修饰语前缀候选（core ⊂ name，需人工裁决，共 "
                  f"{stats['prefix_candidates']} 组）", ""]
    for d in rep["prefix_candidates_top"][:40]:
        lines.append(f"- `{d['name']}`（{d['type']}{'/孤点' if d['isolated'] else ''}）"
                     f" ⊃ `{d['core']}`")
    lines += ["", "> 只读诊断。删实体 / 剥别名一律另开提案，且遵守"
                  "「别名剥离不幂等」纪律。", "",
              "> 口径说明：「逐字存在」是**子串匹配**（与 CHRONICLE 1089 那条同口径），"
              "所以短名会因落在更长词里而误判为接地——它是**落地可能性的上界**，"
              "不是独立出现次数。判孤点能不能靠它救，要看 in_claimed_chunk 与 mentions。"]
    MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(stats, ensure_ascii=False, indent=2))
    print(f"报告 → {OUT}\n      {MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
