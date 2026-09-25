# -*- coding: utf-8 -*-
"""全库并发冲突审计(只读):同一 chunk(cache_key)被多个 _agent_batchNNN.json 抽过时,
判定两侧命名是否**同源**。

背景:并发代理各自 `pending --start 0`,同一版本的块会被重复 dump。submit 按 cache_key
整块覆盖 → 后提交者胜。若两批命名词典不同,同版本各块存活方随机 → 同名异体裂成两个节点。

分类:
  一致      两批该块 name 集合相同 → 覆盖无损
  超集/子集  一侧独有另一侧无 → 只丢密度,不裂节点(若存活方恰为子集一侧,建议整批重提交富侧)
  分裂      两侧各有独有名 → **真冲突**,rebuild 前必须挑一方整批重提交

用法: python data/compendium_rag/_audit_global_key_collisions.py [起始号位] [结束号位]
"""
import collections
import glob
import json
import os
import re
import sys

DATA = "data/compendium_rag"


def entities_of(payload):
    p = payload.get("payload", payload) if isinstance(payload, dict) else {}
    ents = p.get("entities") if isinstance(p, dict) else None
    if ents is None and isinstance(p, dict):
        r = p.get("result") or p.get("raw") or {}
        ents = r.get("entities") if isinstance(r, dict) else None
    return frozenset(e["name"] for e in (ents or []))


def main():
    lo = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    hi = int(sys.argv[2]) if len(sys.argv) > 2 else 10 ** 6
    owners = collections.defaultdict(list)
    for path in glob.glob(os.path.join(DATA, "_agent_batch*.json")):
        m = re.search(r"_agent_batch(\d+)\.json$", path)
        if not m or not (lo <= int(m.group(1)) <= hi):
            continue
        slot = int(m.group(1))
        try:
            d = json.loads(open(path, encoding="utf-8").read())
        except Exception as exc:
            print("!! 无法解析 %s: %s" % (path, exc))
            continue
        if not isinstance(d, dict):
            continue
        for k, v in d.items():
            owners[k].append((slot, entities_of(v)))
    multi = {k: v for k, v in owners.items() if len(v) > 1}
    stat = collections.Counter()
    frags = []
    thin = []
    for k, lst in sorted(multi.items()):
        sets = [s for _, s in lst]
        if all(s == sets[0] for s in sets):
            stat["一致"] += 1
            continue
        p = os.path.join(DATA, "cache", k[:2], k + ".json")
        live = entities_of(json.loads(open(p, encoding="utf-8").read())["raw"]) if os.path.exists(p) else frozenset()
        holder = next((sl for sl, s in lst if s == live), None)
        uniq = {sl: s - set().union(*[t for q, t in lst if q != sl]) for sl, s in lst}
        rich = [sl for sl in uniq if uniq[sl]]
        if len(rich) >= 2:
            stat["分裂(两侧各有独有名)"] += 1
            frags.append((k, rich, holder, {sl: sorted(uniq[sl]) for sl in rich}))
        else:
            stat["超集/子集(命名同源)"] += 1
            if holder not in rich and rich:
                thin.append((k, rich[0], holder))
    print("号位区间 %s–%s｜总 key %d｜多批重叠 %d" % (lo, hi, len(owners), len(multi)))
    for t, c in stat.most_common():
        print("  %-22s %d" % (t, c))
    if frags:
        print("★ 真冲突 %d 块(两侧各有独有名,存活方=%s):" % (len(frags), "见每行"))
        for k, sl, holder, u in frags:
            print("   %-24s 批%s 存活%s 独有:%s" % (k, sl, holder, u))
        print("→ 处理:挑一方 `python data/compendium_rag/_gen_batchNNN.py` 后 submit,再复跑本审计直到分裂=0")
    if thin:
        print("· 存活方为子集一侧、丢了富侧独有名的块 %d 个(只丢密度,重提交富侧批次即可):" % len(thin))
        print("   涉及号位 → %s" % sorted({t[1] for t in thin}))
    if not frags:
        print("结论: 无分裂冲突 → 并发重复抽取已全部收敛到同源命名,可安全 rebuild")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
