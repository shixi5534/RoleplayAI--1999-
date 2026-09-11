# -*- coding: utf-8 -*-
"""回填块别名清洗：去掉自指别名与归一化后重复的别名。

图谱的实体归并键是 ``norm_name``（NFKC + 小写 + 去首尾空白），因此
``Storm``/``storm`` 这类大小写变体在图中是同一个键，留着只会让 alias_index
多出噪声条目；``APPLe`` 带别名 ``Apple``、``双双五零`` 带同名别名则属于自指。

只处理 6 个 ``apply_empty_p*.py`` 写入的回填块，其余 2082 块经审计本就干净。

用法（项目根目录）：
  python scripts/fix_backfill_alias_hygiene.py          # 预演
  python scripts/fix_backfill_alias_hygiene.py --apply   # 写盘
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "knowledge" / "plot_cache" / "wu_ming_zhe"


def norm_name(text: str) -> str:
    """与 graph_store.norm_name 保持一致。"""
    return unicodedata.normalize("NFKC", text or "").strip().lower()


def main() -> int:
    apply = "--apply" in sys.argv
    hashes: set[str] = set()
    for p in (ROOT / "scripts").glob("apply_empty_p*.py"):
        hashes |= set(re.findall(r'"([0-9a-f]{16})":', p.read_text(encoding="utf-8")))

    n_self = n_dup = 0
    for h in sorted(hashes):
        path = CACHE / f"{h}.json"
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        changed = False
        for e in data.get("entities") or []:
            name = str(e.get("name") or "")
            key = norm_name(name)
            aliases = [str(a) for a in (e.get("aliases") or []) if str(a).strip()]
            kept: list[str] = []
            seen: set[str] = {key}  # 正名本身占住一个键 → 顺带清掉自指别名
            for a in aliases:
                ka = norm_name(a)
                if not ka or ka == key:
                    n_self += 1
                    changed = True
                    continue
                if ka in seen:
                    n_dup += 1
                    changed = True
                    continue
                seen.add(ka)
                kept.append(a)
            if kept != aliases:
                e["aliases"] = kept
        if changed and apply:
            path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
            )

    print(
        f"[alias-hygiene] {'已写盘' if apply else '预演'}："
        f"去自指 {n_self} 条，去重复 {n_dup} 条"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
