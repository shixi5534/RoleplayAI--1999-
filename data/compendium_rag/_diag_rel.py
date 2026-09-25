# -*- coding: utf-8 -*-
"""只读探查：原生题集未命中是否与「题面关系词在语料里查不到」同因。

用法：_diag_rel.py <testset.json> <report.json>
造题时关系词取自图谱边标签（agent 归纳词），它**未必逐字出现在语料里**；
若不在，题面就没有可检索的词形锚点，只能靠语义/向量碰运气。
这里按「关系词是否逐字出现在该题事实来源块」分层，对照 hit 率。
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from compendium_rag import pipeline as P  # noqa: E402
from compendium_rag.config import get_settings  # noqa: E402

# 与 _gen_native_qa.py 的两种问式一一对应
RE_T1 = re.compile(r"^「([^」]+)」(.{1,5}?)的对象")
RE_T1R = re.compile(r"^(谁|哪个组织)(.{1,5}?)了?「")


def main() -> int:
    ts_path, rep_path = Path(sys.argv[1]), Path(sys.argv[2])
    s = get_settings()
    by_cid = {c.chunk_id: f"{c.text}\n{c.chapter_title}\n{c.scene_title}\n{c.part_title}"
              for c in P.load_chunks(s)}
    ts = json.loads(ts_path.read_text(encoding="utf-8"))
    cases = {c["id"]: c for c in (ts["cases"] if isinstance(ts, dict) else ts)}
    rep = json.loads(rep_path.read_text(encoding="utf-8"))
    rows = [r for r in rep["rows"] if r["mode"] == "full"]
    stat = defaultdict(lambda: [0, 0, 0])   # key -> [n, hit, 题面实体DF=0]
    for r in rows:
        c = cases.get(r["qid"]) or {}
        q = c.get("q", "")
        m = RE_T1.match(q) or RE_T1R.match(q)
        ttype = c["dims"].get("type")
        if ttype != "factoid" or not m:
            stat[("factoid", "无关系词可解析")][0] += 1
            stat[("factoid", "无关系词可解析")][1] += 1 if r["hit"] else 0
            continue
        rel = m.group(2)
        cid = c.get("_from_chunk", "")
        in_src = rel in by_cid.get(cid, "")
        # 关系词在全语料里的覆盖（有多少块含它）
        ndf = sum(1 for t in by_cid.values() if rel in t)
        key = ("factoid", f"rel在来源块={'是' if in_src else '否'}/全库块数={'>50' if ndf > 50 else '<=50'}")
        stat[key][0] += 1
        stat[key][1] += 1 if r["hit"] else 0
    for (t, k), (n, h, _) in sorted(stat.items()):
        print(f"{t:9s} {k:34s} n={n:4d} hit={h:4d} ({h / n:.3f})" if n else "")
    return 0


if __name__ == "__main__":
    sys.exit(main())
