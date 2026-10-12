# -*- coding: utf-8 -*-
"""复算前后逐字段对比：除了新加的 exposure 与时间戳，**不许有任何已测值移动**。

动机（rules 文档 §6.5）：改计算器时最容易出的事故不是算错，而是「顺手把别的数带跑了」。
所以这里不用肉眼看 diff，而是把两棵 JSON 树做递归路径对比，
把每条差异归成三类：added_exposure / timestamp / **UNEXPLAINED**。
UNEXPLAINED 非空即失败，并打印出路径与前后值。
"""
import json
import re
import sys
import tempfile
from pathlib import Path

# Windows 控制台常见 cp936：产物落盘后才抛 UnicodeEncodeError 最难查（写了一半、退出码非零）。
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(errors="replace")

ROOT = Path(__file__).resolve().parents[1]
NEW = ROOT / "data" / "compendium_rag" / "reports"
# 默认目录走 Windows 临时目录：`/tmp` 在 Git Bash 与原生 python 里不是同一个地方，
# 写死会把「找不到快照」伪装成「没有差异」。
OLD = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(tempfile.gettempdir()) / "expo_before"

TS_KEYS = {"generated_at", "updated_at", "timestamp", "ran_at", "wall_clock"}
FILES = ["cbi_result.json", "cbi_result_full.json",
         "cbi_result_v2instrument.json", "cbi_result_v2instrument_v2_r2.json"]
# 时间戳的识别走「形状」而不是手写字段名清单：清单漏一个 `done_at` 就把一次正常复算
# 报成「已测值移动」，而反过来把真数值当成时间戳放过更糟。
ISO = re.compile(r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}")


def is_ts_move(path, a, b):
    leaf = path.rsplit(".", 1)[-1]
    return (leaf in TS_KEYS or leaf.endswith("_at") or leaf.endswith("At")) \
        and isinstance(a, str) and isinstance(b, str) \
        and bool(ISO.match(a)) and bool(ISO.match(b))


def walk(old, new, path, diffs):
    if isinstance(old, dict) and isinstance(new, dict):
        for k in sorted(set(old) | set(new)):
            p = f"{path}.{k}"
            if k not in old:
                diffs.setdefault("added", []).append((p, None, new[k]))
            elif k not in new:
                diffs.setdefault("removed", []).append((p, old[k], None))
            else:
                walk(old[k], new[k], p, diffs)
    elif isinstance(old, list) and isinstance(new, list):
        if len(old) != len(new):
            diffs.setdefault("len", []).append((path, len(old), len(new)))
        for i, (a, b) in enumerate(zip(old, new)):
            walk(a, b, f"{path}[{i}]", diffs)
    elif old != new:
        diffs.setdefault("value", []).append((path, old, new))


ok = True
n_compared = 0
if not OLD.is_dir():
    print(f"[FAIL] 快照目录不存在：{OLD}\n       复算前的读数没留住 ⇒ 本次无从证明「只有 exposure 变了」")
    sys.exit(1)
for f in FILES:
    op, np_ = OLD / f, NEW / f
    if not (op.exists() and np_.exists()):
        print(f"[FAIL] 缺文件 {f}（快照={op.exists()} 现值={np_.exists()}）——跳过一项就等于给它开了免检")
        ok = False
        continue
    n_compared += 1
    diffs = {}
    walk(json.loads(op.read_text(encoding="utf-8")),
         json.loads(np_.read_text(encoding="utf-8")), "", diffs)
    added = [d for d in diffs.get("added", [])]
    value = [d for d in diffs.get("value", [])]
    # 时间戳移动是允许的：字段名像时间戳，且前后值都是 ISO 时间串
    ts_moved = [d for d in value if is_ts_move(d[0], d[1], d[2])]
    unexplained = [d for d in value if not is_ts_move(d[0], d[1], d[2])]
    other = {k: v for k, v in diffs.items() if k not in ("added", "value")}
    only_exposure = all(".exposure" in p or p.endswith(".exposure") for p, _, _ in added)
    print(f"[{f}] 新增 {len(added)} 条（全在 exposure 内={only_exposure}）"
          f" / 时间戳移动 {len(ts_moved)} / **未解释变动 {len(unexplained)}**"
          f" / 结构差异 {len(other)}")
    for p, a, b in added[:3]:
        print(f"    + {p}")
    for p, a, b in ts_moved:
        print(f"    ~ 时间戳豁免 {p}: {a} -> {b}")
    for p, a, b in unexplained[:8]:
        print(f"    !! {p}: {a!r} -> {b!r}")
        ok = False
    for k, v in other.items():
        print(f"    ?? {k}: {v[:3]}")
        ok = False
    if not only_exposure and added:
        for p, _, _ in added:
            if ".exposure" not in p:
                print(f"    ?? 非 exposure 的新增字段 {p}")
        ok = False

# 反空转：如果 exposure 根本没落进产物，上面「新增全在 exposure 内」会退化成真·空。
n_expo = 0
for f in FILES:
    p = NEW / f
    if not p.exists():
        continue
    blob = json.dumps(json.loads(p.read_text(encoding="utf-8")))
    n_expo += blob.count('"n_gold_in_top6"')
print(f"[对比] 实际比对 {n_compared}/{len(FILES)} 份读数；产物里 exposure 块 {n_expo} 处"
      f"（期望 ≥{len(FILES)}：每份至少一个口径一块）")
if n_expo < len(FILES):
    print("    !! exposure 块没写进产物 ⇒ 本检查在空转")
    ok = False

print("[PASS] 复算只加了 exposure，没有任何已测值移动" if ok else "[FAIL] 见上面 !! 行")
sys.exit(0 if ok else 1)
