# -*- coding: utf-8 -*-
"""批量证据核对:python _verify_evidence_range.py <起始号位> [结束号位]

对 _agent_batchNNN.json 逐个调用 _verify_evidence.main(batch, _dumpNNN.txt)。
dump 缺失或 key 不在 dump 中 → 记为该号位失败,继续跑完其余号位。
"""
import sys
from pathlib import Path

import _verify_evidence as ve

BASE = Path(__file__).resolve().parent


def main(lo: int, hi: int | None) -> int:
    failed = []
    ran = 0
    for n in range(lo, (hi or 10**6) + 1):
        b = BASE / f"_agent_batch{n}.json"
        d = BASE / f"_dump{n}.txt"
        if not b.exists():
            continue
        if not d.exists():
            print(f"✗ batch{n}: 缺 dump 文件 _dump{n}.txt")
            failed.append(n)
            continue
        ran += 1
        print(f"===== batch{n} =====")
        try:
            rc = ve.main(b.name, d.name)
        except Exception as exc:  # noqa: BLE001
            print(f"✗ batch{n}: 异常 {exc}")
            rc = 1
        if rc:
            failed.append(n)
    print(f"\n核对 {ran} 个批次,失败号位: {failed or '无'}")
    return 1 if failed else 0


if __name__ == "__main__":
    a = sys.argv[1:]
    sys.exit(main(int(a[0]), int(a[1]) if len(a) > 1 else None))
