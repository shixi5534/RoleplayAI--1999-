"""臂 4 切片输入生成：style_probe 100 条 + CC-088 单题盲评面板 5 份副本。

只读 probe/jin_full 与 reports/cbi/answers.jsonl，只写两个新输入目录。
用法：.venv/Scripts/python.exe -X utf8 scripts/cbi_arm4_slice.py
"""
from __future__ import annotations

import glob
import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("ROLEPLAY_ROOT", ".")).resolve()
CBID = ROOT / "data" / "compendium_rag" / "reports" / "cbi"
SRC = CBID / "probe" / "jin_full"
SProbe = CBID / "probe" / "jin_sprobe"
PANEL = CBID / "probe" / "jin_panel"
DISPUTED = "CC-088-style_probe"
PER = 20
FIELDS = ("sample_id", "role", "other_role", "query", "answer", "fact_self", "fact_other")


def dump(path: Path, batch_id: str, items: list[dict]) -> None:
    path.write_text(json.dumps(
        {"schema": "compendium_rag.cbi_judge_batch/v1",
         "task": "判 answer 是否泄漏 other_role 的私密（三态）",
         "batch_id": batch_id, "items": items}, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8")


def main() -> int:
    rows: dict[str, dict] = {}
    for f in sorted(glob.glob(str(SRC / "jdg_b*.json"))):
        for it in json.loads(Path(f).read_text(encoding="utf-8"))["items"]:
            sid = it["sample_id"]
            if sid in rows:
                raise SystemExit(f"[FATAL] {sid} 在两个输入批里都出现")
            rows[sid] = {k: it[k] for k in FIELDS}
    if len(rows) != 500:
        raise SystemExit(f"[FATAL] 源 {len(rows)} 条 != 500")

    sp = sorted(k for k in rows if k.endswith("style_probe"))
    if len(sp) != 100 or DISPUTED not in rows:
        raise SystemExit(f"[FATAL] style_probe {len(sp)} 条或争议项缺失")

    SProbe.mkdir(parents=True, exist_ok=True)
    PANEL.mkdir(parents=True, exist_ok=True)
    for i in range(0, len(sp), PER):
        bid = f"jdg_s{i // PER + 1:02d}"
        dump(SProbe / f"{bid}.json", bid, [rows[k] for k in sp[i:i + PER]])
    for k in range(1, 6):
        dump(PANEL / f"panel_k{k}.json", f"panel_k{k}", [rows[DISPUTED]])

    print(f"[OK] {SProbe.name}: {len(sp) // PER} 批 × {PER} = {len(sp)} 条")
    print(f"     {PANEL.name}: 5 份单题副本（{DISPUTED}）")
    print(f"     校验：批内 sample_id 与源逐字一致，字段 {list(FIELDS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
