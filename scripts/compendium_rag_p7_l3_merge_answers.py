"""P7 · 把 `l3_answers/` 主文件与 `l3_answers/_parts/` 分片合并成 28 份完整答案。

用途：679 题作答由多个子代理分批/分片落盘（部分写在 `_parts/`），本脚本按
`l3_batches/ans_bNN.json` 的 **qid 顺序** 归并，写出规范化的
`l3_answers/ans_bNN.json` = `{"items":[{"qid","answer"}...]}`，
并打印逐批覆盖自查（缺失/多出/空答案）。

只读 `l3_batches/` 与现有答案分片，只写 `l3_answers/ans_bNN.json`；
不改图、不调 LLM、不用 rmtree/unlink（守门测试 test_independence.py:265）。

用法：
    PYTHONPATH=src python -X utf8 scripts/compendium_rag_p7_l3_merge_answers.py \
        --tag r10 [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data" / "knowledge" / "_audit"


def state_dir(tag: str) -> Path:
    return AUDIT / (f"p4_harness_{tag}" if tag else "p4_harness")


def _items(path: Path) -> list[dict]:
    try:
        d = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        print(f"  [warn] 无法解析 {path.name}: {exc}")
        return []
    if isinstance(d, dict):
        return list(d.get("items") or [])
    if isinstance(d, list):
        return [x for x in d if isinstance(x, dict)]
    return []


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="r10")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    st = state_dir(args.tag)
    bdir = st / "l3_batches"
    adir = st / "l3_answers"
    pdir = adir / "_parts"
    if not bdir.is_dir():
        print(f"[FATAL] 批次目录不存在：{bdir}")
        return 2

    # 1) 目标 qid 顺序
    want: dict[str, list[str]] = {}
    for f in sorted(bdir.glob("ans_b*.json")):
        want[f.stem] = [i["qid"] for i in _items(f) if i.get("qid")]

    # 2) 汇集所有来源（主文件优先，分片补充；同 qid 后到者不覆盖已有非空答案）
    pool: dict[str, dict[str, str]] = {k: {} for k in want}
    dup = []
    for f in sorted(adir.glob("ans_b*.json")) + sorted(pdir.glob("*.json")):
        if f.parent == pdir:
            stem = f.stem.split("_g")[0].split("_h")[0]
        else:
            stem = f.stem
        if stem not in want:
            continue
        for it in _items(f):
            q = it.get("qid")
            a = (it.get("answer") or "").strip()
            if not q or not a:
                continue
            if q in pool[stem] and pool[stem][q] != a:
                dup.append(f"{stem}/{q} 来自 {f.name}")
            pool[stem].setdefault(q, a)

    # 3) 按批次顺序归并 + 自查
    written = 0
    problems = 0
    for stem in sorted(want):
        order = want[stem]
        rows = [{"qid": q, "answer": pool[stem][q]} for q in order if q in pool[stem]]
        missing = [q for q in order if q not in pool[stem]]
        extra = [q for q in pool[stem] if q not in order]
        empty = [r["qid"] for r in rows if not r["answer"]]
        flag = "" if not (missing or extra or empty) else "  <== 有问题"
        if missing or extra or empty:
            problems += 1
        print(f"{stem}: want {len(order)} -> {len(rows)}"
              f" missing={missing} extra={extra} empty={empty}{flag}")
        if missing or extra or empty:
            continue
        out = adir / f"{stem}.json"
        if args.dry_run:
            continue
        out.write_text(
            json.dumps({"items": rows}, ensure_ascii=False, indent=1),
            encoding="utf-8",
        )
        written += 1

    if dup:
        print(f"\n[note] 同一 qid 有多个来源（已取先到的非空答案，共 {len(dup)} 条，前 10）:")
        for d in dup[:10]:
            print(f"  - {d}")

    total = sum(len(v) for v in pool.values())
    print(f"\n覆盖 qid 合计 {total}；{'干跑' if args.dry_run else f'写出 {written} 份'}；"
          f"有问题批次 {problems}")
    return 0 if problems == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
