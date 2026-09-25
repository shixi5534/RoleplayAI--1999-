# -*- coding: utf-8 -*-
"""汇总号位区间内所有 name,产出 _sim_landing.py 的输入清单。

用法: python _gen_newnames_range.py <起始号位> [结束号位]
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def slot(p: Path):
    m = re.fullmatch(r"_agent_batch(\d+)", p.stem)
    return int(m.group(1)) if m else None


def main() -> int:
    lo = int(sys.argv[1]) if len(sys.argv) > 1 else 247
    hi = int(sys.argv[2]) if len(sys.argv) > 2 else 10 ** 9
    names = set()
    used = []
    for p in sorted(ROOT.glob("_agent_batch*.json")):
        s = slot(p)
        if s is None or not (lo <= s <= hi):
            continue
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[skip] {p.name} 读取失败 {type(e).__name__}")
            continue
        used.append(s)
        for blk in d.values():
            for e in blk.get("entities") or []:
                if e.get("name"):
                    names.add(e["name"])
    out = ROOT / f"_newnames_{lo}_{hi if hi < 10**8 else 'max'}.txt"
    out.write_text("\n".join(sorted(names)) + "\n", encoding="utf-8")
    print(f"号位 {len(used)} 个｜name 去重 {len(names)} 条 → {out.name}")
    import subprocess
    return subprocess.call([sys.executable, str(ROOT / "_sim_landing.py"), str(out)])


if __name__ == "__main__":
    raise SystemExit(main())
