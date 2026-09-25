# -*- coding: utf-8 -*-
"""交接完整性审计：核对每个 _agent_batch*.json 的 key 是否都已落入 cache。

用途：捕捉「已生成 batch 但从未 submit」的悬挂产物——这类遗漏会让接手者
以为某段已抽完，实际图里没有。零网络，只读。

判据：submit 以 dump key 作为 cache key，落盘于 cache/<key[:2]>/<key>.json。
"""
import glob
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / "cache"

total_keys = 0
seen = set()
missing = []
dup_across = 0

for fp in sorted(glob.glob(str(ROOT / "_agent_batch*.json"))):
    name = Path(fp).name
    try:
        data = json.loads(Path(fp).read_text(encoding="utf-8"))
    except Exception as e:                       # noqa: BLE001
        missing.append((name, f"<解析失败: {e}>"))
        continue
    for key in data:
        total_keys += 1
        if key in seen:
            dup_across += 1
        seen.add(key)
        if not (CACHE / key[:2] / f"{key}.json").exists():
            missing.append((name, key))

print(f"batch 文件数      : {len(glob.glob(str(ROOT / '_agent_batch*.json')))}")
print(f"batch 内 key 总数 : {total_keys}")
print(f"唯一 key 数       : {len(seen)}")
print(f"跨文件重复 key    : {dup_across}")
print(f"cache 文件总数    : {len(list(CACHE.rglob('*.json')))}")
print()
if missing:
    print(f"❌ 有 {len(missing)} 个 key 未落入 cache（悬挂产物）：")
    for n, k in missing[:40]:
        print(f"   {n}: {k}")
else:
    print("✅ 所有 batch key 均已落入 cache，无悬挂产物。")

# 反向：cache 里有、但不在任何 batch 文件里的 key（早期会话产物，属正常）
batch_keys = seen
cache_keys = {p.stem for p in CACHE.rglob("*.json")}
orphan = cache_keys - batch_keys
print()
print(f"cache 中不在 batch 文件内的 key: {len(orphan)}（早期轮次产物，属正常）")
