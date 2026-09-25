# -*- coding: utf-8 -*-
"""定位 _gen_batch138.py 里 evidence 超过 40 字的条目（按字符数，非字节数）。"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
src = (ROOT / "_gen_batch138.py").read_text(encoding="utf-8")
# 去掉 main/audit 调用，只取 BATCH
src = src.split("def _audit()")[0]
ns: dict = {"__file__": str(ROOT / "_gen_batch138.py")}
exec(compile(src, "_gen_batch138.py", "exec"), ns)
BATCH = ns["BATCH"]

for key, blk in BATCH.items():
    for r in blk["relations"]:
        if len(r["evidence"]) > 40:
            print(f"{key}  {r['src']}-{r['relation']}->{r['dst']}  "
                  f"len={len(r['evidence'])}  {r['evidence']}")
print("done")
