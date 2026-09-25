# -*- coding: utf-8 -*-
"""手工事实边补充 / 重放 / 对账（幂等，可重放）——即 Spec 的 M-9。

为什么存在
    离线抽取会把「块里明确写了、但抽取器没产出」的跨实体关系漏掉。这类边靠人工补，
    但图谱重建（``--rebuild-graph-only``）会把它们整条清掉——**重建即静默丢手工事实**，
    这是 R8 红线（手工边零丢失）要防的事。本脚本把「重放」变成机械动作，并在
    ``build_plot_graph`` 里自动调用，消除"记得手动补一遍"的操作依赖。

三个职责
    1. **重放**：把 ``manual_edges.json`` 里的边写入图谱（不存在则新增）；
    2. **规范标记**：把已存在但 ``source`` 不是人工标记的边**就地归一**为规范值。
       实测踩到：早期探针写入的边标记为 ``manual_probe``，与配置默认值 ``manual`` 不符——
       于是 P0-1 的弱证豁免对它**不生效**，孤证人工边会被弱证过滤静默丢掉。
       归一后「配置默认值 = 数据实际值」，不再依赖部署侧记得改配置。
    3. **对账**：给出在场率（present/total），R8 断言必须为 100%。

用法
    .venv/Scripts/python.exe -X utf8 scripts/apply_manual_edges.py --character wu_ming_zhe
    .venv/Scripts/python.exe -X utf8 scripts/apply_manual_edges.py --dry-run   # 断言：新增 0
    .venv/Scripts/python.exe -X utf8 scripts/apply_manual_edges.py --check     # 只对账，不写

数据文件：``data/lore/<cid>/manual_edges.json``——每条带证据块 hash（可溯源）+ 说明。
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# 人工事实边的**规范 source 标记**。必须与 config.plot_weak_exempt_sources 的默认值一致，
# 否则 P0-1 的弱证豁免对人工边不生效（配置与数据两套标记 = 静默失效）。
MANUAL_SOURCE = "manual"


def _find_entity(entities: dict, name: str) -> str | None:
    for eid, e in entities.items():
        if e.get("name") == name:
            return eid
    return None


def _edge_key(a: str, b: str, rel: str) -> tuple[str, str, str]:
    return (a, b, rel)


def replay(character: str = "wu_ming_zhe", *, dry_run: bool = False,
           graph_path: Path | None = None) -> dict:
    """重放 + 归一 + 对账。返回统计字典（供调用方断言与埋点）。

    返回 ``{"total", "added", "normalized", "consistent", "missing", "present_rate"}``。
    ``present_rate`` = 已在场且标记规范的手工边 / 清单总数。

    ``graph_path`` 可显式指定（``build_plot_graph`` 内部重放时传入，避免二次解析路径）。
    """
    gpath = graph_path or (ROOT / "data" / "knowledge" / f"plot_graph_{character}.json")
    mpath = ROOT / "data" / "lore" / character / "manual_edges.json"
    stats = {"total": 0, "added": 0, "normalized": 0, "consistent": 0,
             "missing": [], "present_rate": 0.0, "present_before": 0,
             "present_after": 0, "present_rate_before": 0.0, "skipped_no_file": False}
    if not mpath.is_file():
        stats["skipped_no_file"] = True
        return stats
    if not gpath.is_file():
        stats["missing"] = ["<图谱文件不存在>"]
        return stats

    manual = json.loads(mpath.read_text(encoding="utf-8"))
    g = json.loads(gpath.read_text(encoding="utf-8"))
    entities, edges = g.get("entities", {}), g.setdefault("edges", [])
    stats["total"] = len(manual)

    # 索引：正向 + 反向都登记——边在存储层是**有向**的，但语义上关系对称，
    # 人工清单写的是 (A,B) 而图里可能存成 (B,A)，只查正向会误判成"缺失"并重复插边。
    index: dict[tuple[str, str, str], dict] = {}
    for e in edges:
        s, d, r = str(e.get("src")), str(e.get("dst")), str(e.get("relation"))
        index[_edge_key(s, d, r)] = e
        index.setdefault(_edge_key(d, s, r), e)

    for item in manual:
        src = _find_entity(entities, item["src_name"])
        dst = _find_entity(entities, item["dst_name"])
        if not src or not dst:
            stats["missing"].append((item["src_name"], item["dst_name"]))
            continue
        rel = item["relation"]
        hit = index.get(_edge_key(src, dst, rel))
        if hit is None:
            if not dry_run:
                new_edge = {
                    "src": src, "dst": dst, "relation": rel,
                    "confidence": item.get("confidence", 0.7),
                    "importance": item.get("importance", 0.7),
                    "evidence": item.get("evidence", []),
                    "ts": time.time(), "source": MANUAL_SOURCE,
                }
                edges.append(new_edge)
                index[_edge_key(src, dst, rel)] = new_edge
                index.setdefault(_edge_key(dst, src, rel), new_edge)
            stats["added"] += 1
            continue
        # 已存在：核对并**归一 source 标记**（这是本脚本相对旧版的关键增量）
        cur = str(hit.get("source") or "")
        if cur != MANUAL_SOURCE:
            if not dry_run:
                hit["source"] = MANUAL_SOURCE
                # 置信度/重要性以人工清单为准（人工事实优先于抽取推断）
                hit["confidence"] = item.get("confidence", hit.get("confidence", 0.7))
                hit["importance"] = item.get("importance", hit.get("importance", 0.7))
                # 证据取并集（不丢抽取侧已有的溯源块）
                have = {str((ev or {}).get("hash")) for ev in (hit.get("evidence") or [])}
                for ev in item.get("evidence", []) or []:
                    if str((ev or {}).get("hash")) not in have:
                        hit.setdefault("evidence", []).append(ev)
            stats["normalized"] += 1
        else:
            stats["consistent"] += 1

    # 两口径必须分开报，否则会自相矛盾（实测踩到）：
    #   present_before = 跑之前就规范在场的条数（= consistent + normalized）
    #   present_after  = 跑完之后在场的条数（= before + 本次新增）
    # 旧版只用 before 当「在场率」，于是"重建后自动重放新增了 1 条"会被报成「在场率 0%」——
    # 明明刚补上却被判成丢失。R8 的语义是**跑完之后**零丢失，故对外口径用 present_after。
    stats["present_before"] = stats["consistent"] + stats["normalized"]
    stats["present_after"] = stats["present_before"] + stats["added"]
    stats["present_rate"] = (stats["present_after"] / stats["total"]) if stats["total"] else 1.0
    stats["present_rate_before"] = (
        stats["present_before"] / stats["total"] if stats["total"] else 1.0
    )

    if not dry_run and (stats["added"] or stats["normalized"]):
        gpath.write_text(json.dumps(g, ensure_ascii=False), encoding="utf-8")
    return stats


def report(stats: dict, *, dry_run: bool, wrote: bool) -> None:
    if stats.get("skipped_no_file"):
        print("[skip] 无手工边清单")
        return
    print(
        f"[manual_edges] 清单 {stats['total']} 条｜新增 {stats['added']}"
        f"｜归一 source {stats['normalized']}｜已一致 {stats['consistent']}"
        f"｜实体缺失 {len(stats['missing'])}"
        f"｜在场率 {stats['present_rate']:.0%}（跑前 {stats['present_rate_before']:.0%}）"
    )
    for s, d in stats["missing"]:
        print(f"  [warn] 实体不存在，未加：{s} → {d}")
    if dry_run:
        print("[dry-run] 未落盘（断言：新增应为 0 且在场率应为 100%）")
    elif wrote:
        print("[write] 图谱已更新")
    if stats["present_rate"] < 1.0:
        print("[warn] 在场率不足 100%：清单里有实体在图谱中找不到（R8 需人工核对）")


def main() -> int:
    ap = argparse.ArgumentParser(description="手工事实边重放 / 归一 / 对账（M-9）")
    ap.add_argument("--character", default="wu_ming_zhe")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--check", action="store_true", help="只对账不写盘（等价 dry-run + 退出码）")
    args = ap.parse_args()

    dry = args.dry_run or args.check
    before = None
    gpath = ROOT / "data" / "knowledge" / f"plot_graph_{args.character}.json"
    if gpath.is_file() and not dry:
        before = gpath.stat().st_mtime
    stats = replay(args.character, dry_run=dry)
    wrote = bool(not dry and (stats["added"] or stats["normalized"]))
    report(stats, dry_run=dry, wrote=wrote)
    if args.check:
        # --check 语义 = 「当前状态是否已对账完毕」：需要写入就说明还没归位，退出码非 0。
        if stats["missing"] or stats["present_rate_before"] < 1.0:
            print("[FAIL] 手工边未全部在位（R8 红线）：请跑一次不带 --check 的重放")
            return 1
        print("[ok] 手工边全部在位且标记规范（R8 通过）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
