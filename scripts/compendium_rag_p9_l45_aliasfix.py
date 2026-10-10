"""P9④ 修正 · 给「规范名不逐字出现在正文、实际以别名出现」的块重出面板。

w4 盲评回来的 60 块里有 **5 块**属于这种情形：面板按 `audit_l4.py:796-804` 的写法只渲染
实体的**规范名**，而原文用的是别名（`安妮` 的 alias `洁西卡`、`星锑` 的 alias `摇滚海盗`），
于是判分代理看到「规范名在全文一次都没出现」就记一处凭空错张 —— 这是**测量效度缺陷**，
不是图的错，而且同一段代码也用在 2026-10-08 那批面板上（旧读数同样被压低）。

本脚本只做一件事：把这 5 块重新出一批，在每条边上标出「本文里实际以哪个别名出现」，
让判分人在**信息完整**的条件下重评。其余 55 块不动，两批分开报数。

只读图与 w4 面板，只写 `l4_multiscene_r11/ms_b04_aliasfix.json`。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "data" / "knowledge" / "_audit" / "l4_multiscene_r11"
GRAPH = ROOT / "data" / "compendium_rag" / "graph.json"
OUT = DIR / "ms_b04_aliasfix.json"
MAX_LINE = 320


def main() -> int:
    if OUT.exists():
        raise SystemExit(f"[FATAL] 修正批已存在，勿重出：{OUT}")
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    byname: dict[str, dict] = {}
    for e in graph["entities"]:
        byname.setdefault(e["name"], e)

    affected = []
    for f in sorted(DIR.glob("ms_b??.json")):
        for it in json.loads(f.read_text(encoding="utf-8"))["items"]:
            txt = "".join(it["text_lines"])
            notes: dict[str, list[str]] = {}
            for ed in it["edges"]:
                for side in (ed["src"], ed["dst"]):
                    if side in txt or side in notes:
                        continue
                    ent = byname.get(side)
                    if not ent:
                        continue
                    used = [a for a in (ent.get("aliases") or []) if a and a in txt]
                    if used:
                        notes[side] = used
            if notes:
                new_it = dict(it)
                new_it["alias_note"] = [
                    {"entity": k, "appears_in_text_as": v,
                     "note": "规范名在本文未逐字出现，实际以上述别名出现；"
                             "关系是否成立请按别名所指的对象判断，别按字面名字缺判"}
                    for k, v in sorted(notes.items())]
                affected.append(new_it)

    if not affected:
        print("[OK] 没有受别名渲染影响的块")
        return 0
    body = json.dumps({
        "schema": "compendium_rag.p9_l45_input/v1",
        "task": "逐块判定这些角色之间的关系陈述是否与原文互洽（1~5 分）。"
                "本批特殊：部分实体在原文里只以**别名**出现，见每块的 alias_note —— "
                "这不算错张，请按别名所指的对象评。",
        "items": affected}, ensure_ascii=False, indent=1)
    longest = max(len(ln) for ln in body.splitlines())
    if longest > MAX_LINE:
        raise SystemExit(f"[FATAL] 超长行 {longest} > {MAX_LINE}")
    OUT.write_text(body, encoding="utf-8")
    print(f"[OK] 修正批 {len(affected)} 块 → {OUT}（最长行 {longest}）")
    for it in affected:
        print("     ", it["chunk_id"], "|", [n["entity"] for n in it["alias_note"]])
    return 0


if __name__ == "__main__":
    sys.exit(main())
