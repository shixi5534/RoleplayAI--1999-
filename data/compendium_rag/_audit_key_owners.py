# -*- coding: utf-8 -*-
"""哪些 _agent_batchNNN.json 之间存在 cache_key 重叠(重提交安全边界)。只读。"""
import collections
import glob
import json
import os
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))
targets = sys.argv[1:]

own = collections.defaultdict(set)
for f in glob.glob("_agent_batch*.json"):
    for k in json.load(open(f, encoding="utf-8")):
        own[k].add(f)
ov = {k: v for k, v in own.items() if len(v) > 1}
print(f"总 key {len(own)}｜重叠 key {len(ov)}")
pair = collections.Counter(frozenset(v) for v in ov.values())
for p, c in sorted(pair.items(), key=lambda x: -x[1]):
    print(f"  {c:3d}  {' ↔ '.join(sorted(p))}")

if targets:
    print(f"\n=== 指定文件的每块重叠对手 ===")
    for t in targets:
        keys = json.load(open(f"_agent_batch{t}.json", encoding="utf-8"))
        cnt = collections.Counter()
        for k in keys:
            for o in own[k] - {f"_agent_batch{t}.json"}:
                cnt[o] += 1
        print(f"  {t}({len(keys)} 块): {dict(cnt) or '独占,重提交零风险'}")
