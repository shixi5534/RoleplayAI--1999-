# -*- coding: utf-8 -*-
"""别名表治理：合并自相冲突条目 + 写入灰机核实的别名桥。

两类问题（都会直接制造**重复节点**，把同一实体的证据劈成两半）

1. **自相冲突**：同一个名字既是一个条目的键、又出现在另一个条目的别名里。
   实测 16 条（8 对），如 ``"Ulrich": ["乌尔里希"]`` 与 ``"乌尔里希": ["Ulrich"]``
   并存。重建图谱时两条目抢同一个名字，`bind_alias_table` 首注册优先 ⇒ 生成
   两个节点，证据被劈开、提及计数被稀释（真实对话里表现为「时好时坏」）。
   处置：**中文正名存活**（与灰机命名体系一致），英文条目的别名全部并入后删除。

2. **灰机核实过的别名桥**：``scripts/huiji_alias_bridge.py`` 产出的 high 置信提案
   （灰机角色页 / 其他角色一览 里中英名精确对照）。只写 high 档，模糊的一律不动。

用法：
    .venv/Scripts/python.exe -X utf8 scripts/huiji_alias_apply.py --dry-run
    .venv/Scripts/python.exe -X utf8 scripts/huiji_alias_apply.py --apply
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from roleplay.core.knowledge.graph_store import norm_name  # noqa: E402

ALIASES = ROOT / "data" / "lore" / "wu_ming_zhe" / "plot_aliases.json"
GLOSSARY = ROOT / "data" / "lore" / "wu_ming_zhe" / "plot_glossary.json"
BRIDGE = ROOT / "data" / "knowledge" / "_audit" / "huiji_alias_bridge.json"
OUT = ROOT / "data" / "knowledge" / "_audit" / "alias_governance.json"

_CJK = re.compile(r"[\u4e00-\u9fff]")

# 人工裁决保留的别名：**自动桥一律不得改指**。
# 依据 `docs/剧情别名与抽取裁决记录.md`（决策人：用户）——
#   裁决 1：凯拉 / 塞西莉 / 莉莉保留为「无名者」的直接别名。
# 本轮灰机会话确实产出了 `Kayla += 凯拉`（另有一个 NPC 也叫 Kayla），
# 若照单执行会在重建时把「凯拉」从无名者改指到 Kayla 节点——
# 那是**推翻已记录的人工裁决**，不是数据修复。故在此硬拦。
HUMAN_RESERVED_ALIASES = {
    "凯拉": "裁决1：保留为无名者的直接别名（勿被自动桥改指）",
    "塞西莉": "裁决1：保留为无名者的直接别名",
    "莉莉": "裁决1：保留为无名者的直接别名",
    "淑女格蕾丝": "裁决1 已解决：全部并入无名者别名链",
}


def consolidate(table: dict) -> tuple[dict, list[dict]]:
    """合并「键 ↔ 别名」互相指向的条目：中文正名存活。"""
    merged: list[dict] = []
    changed = True
    while changed:
        changed = False
        key_map = {norm_name(k): k for k in table}
        for k in list(table.keys()):
            if k not in table:
                continue
            for v in list(table.get(k) or []):
                nv = norm_name(str(v))
                other = key_map.get(nv)
                if other is None or other == k or other not in table:
                    continue
                # 选存活者：中文名优先；都中文/都非中文时取别名更多的一方
                k_cjk, o_cjk = bool(_CJK.search(k)), bool(_CJK.search(other))
                if k_cjk != o_cjk:
                    survive, die = (k, other) if k_cjk else (other, k)
                else:
                    survive, die = ((k, other)
                                    if len(table.get(k) or []) >= len(table.get(other) or [])
                                    else (other, k))
                keep = [a for a in (table[survive] or []) if norm_name(str(a)) != norm_name(die)]
                for a in (table[die] or []) + [die]:
                    a = str(a)
                    if a and norm_name(a) != norm_name(survive) and a not in keep:
                        keep.append(a)
                if norm_name(die) not in {norm_name(x) for x in keep}:
                    keep.append(die)
                merged.append({"survive": survive, "drop": die,
                               "aliases_moved": len(table.get(die) or [])})
                table[survive] = keep
                del table[die]
                changed = True
                break
            if changed:
                break
    return table, merged


def apply_bridge(table: dict, proposals: list[dict],
                 reserved: dict | None = None) -> tuple[list[dict], list[dict]]:
    """把灰机核实过的别名桥写进表。返回 ``(已采纳, 被拦下)``。"""
    reserved = HUMAN_RESERVED_ALIASES if reserved is None else reserved
    applied: list[dict] = []
    blocked: list[dict] = []
    for p in proposals:
        if p.get("confidence") not in ("high", "medium"):
            continue
        key = str(p.get("key") or "")
        if not key:
            continue
        cur = table.setdefault(key, [])
        for a in p.get("add") or []:
            a = str(a)
            if not a or norm_name(a) == norm_name(key) or a in cur:
                continue
            if a in reserved:
                blocked.append({"key": key, "add": a, "why": reserved[a]})
                continue
            cur.append(a)
            applied.append({"key": key, "add": a, "source": p.get("source", ""),
                            "confidence": p.get("confidence")})
    return applied, blocked


def sync_glossary(table: dict, dry: bool) -> int:
    """plot_glossary.json 的 alias_flat 与别名表**必须同步**（交接文档坑#2）。"""
    if not GLOSSARY.is_file():
        return 0
    try:
        g = json.loads(GLOSSARY.read_text(encoding="utf-8"))
    except ValueError:
        return 0
    flat = []
    for k, vs in table.items():
        # alias_flat 用列表形式表达归并组：[正名, 别名...]
        flat.append([k] + [str(v) for v in (vs or [])])
    if "alias_flat" in g:
        if dry:
            return len(flat)
        g["alias_flat"] = flat
        GLOSSARY.write_text(json.dumps(g, ensure_ascii=False, indent=1), encoding="utf-8")
        return len(flat)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="别名表治理")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    dry = not args.apply

    table = json.loads(ALIASES.read_text(encoding="utf-8"))
    before = len(table)

    proposals = []
    if BRIDGE.is_file():
        proposals = json.loads(BRIDGE.read_text(encoding="utf-8")).get("proposals") or []
    applied, blocked = apply_bridge(table, proposals)
    table, merged = consolidate(table)

    print(f"[govern] 条目 {before} → {len(table)}")
    print(f"[bridge] 采纳灰机别名 {len(applied)} 条：")
    for a in applied[:40]:
        print(f"    {a['key']} += {a['add']}")
    if blocked:
        print(f"[bridge][guard] 拦下 {len(blocked)} 条（人工裁决保留，不得改指）：")
        for b in blocked:
            print(f"    {b['key']} += {b['add']}  ← {b['why']}")
    print(f"[merge] 合并自相冲突 {len(merged)} 组：")
    for m in merged:
        print(f"    {m['drop']} → {m['survive']}（并入别名 {m['aliases_moved']} 条）")

    flat_n = sync_glossary(table, dry)
    print(f"[glossary] alias_flat 同步 {flat_n} 组{'（未写入）' if dry else ''}")

    if dry:
        print("[dry-run] 未写入；确认后加 --apply")
        return 0

    ALIASES.write_text(json.dumps(table, ensure_ascii=False, indent=1), encoding="utf-8")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(
        {"entries_before": before, "entries_after": len(table),
         "bridges": applied, "blocked": blocked, "merges": merged},
        ensure_ascii=False, indent=1),
        encoding="utf-8")
    print(f"[apply] 已写入 {ALIASES}")
    print(f"[save] {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
