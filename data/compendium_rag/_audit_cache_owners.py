# -*- coding: utf-8 -*-
"""cache 归属实测:每个 cache_key 当前内容 == 哪个 _agent_batchNNN.json 的 payload。

只读。用法:
    python _audit_cache_owners.py                 # 汇总:各号位存活块数 / 被覆盖块数
    python _audit_cache_owners.py 希曼 康斯坦丁    # 附带:列出声明了这些名字的块及其存活号位
"""
import collections
import glob
import json
import os
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))

payloads = {}          # key -> (file, payload)
for f in glob.glob("_agent_batch*.json"):
    for k, v in json.load(open(f, encoding="utf-8")).items():
        payloads.setdefault(k, []).append((f, v))


def norm(p):
    return json.dumps(p, ensure_ascii=False, sort_keys=True)


def owner(key):
    """返回当前 cache 内容对应的 batch 文件列表(理论唯一;同内容多写则并列)。"""
    path = os.path.join("cache", key[:2], key[2:] + ".json")
    if not os.path.exists(path):
        path = os.path.join("cache", key[:2], key + ".json")
    if not os.path.exists(path):
        return None, []
    raw = json.load(open(path, encoding="utf-8")).get("raw")
    if isinstance(raw, str):
        raw = json.loads(raw)
    tgt = norm(raw)
    hits = [f for f, v in payloads.get(key, []) if norm(v) == tgt]
    return (hits[0] if len(hits) == 1 else ",".join(sorted(hits)) or "?"), hits


alive = collections.Counter()
unknown = 0
for key in payloads:
    o, hits = owner(key)
    if o is None:
        unknown += 1
    elif not hits:
        alive["<cache 内容与任何 batch 都不一致(手改/旧版本)>"] += 1
    else:
        for f in hits:
            alive[f] += 1 if len(hits) == 1 else 0

total = len(payloads)
print(f"cache_key 总数 {total}｜找不到 cache 文件 {unknown}")
print("=== 存活块数(按 batch 文件,只列前 40) ===")
for f, c in sorted(alive.items(), key=lambda x: -x[1])[:40]:
    print(f"  {c:4d}  {f}")

names = sys.argv[1:]
for n in names:
    print(f"\n=== 声明 name={n} 的块及其 cache 归属 ===")
    for f, vs in [(f, json.load(open(f, encoding="utf-8"))) for f in sorted(glob.glob("_agent_batch*.json"))]:
        for k, blk in vs.items():
            if any(e.get("name") == n for e in blk.get("entities", [])):
                o, _ = owner(k)
                print(f"  {k}  声明者{f}  cache 存活方={o}")
