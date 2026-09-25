# -*- coding: utf-8 -*-
"""双代理重复抽取冲突核查(只读)。

两个代理的 pending 列表若重叠,会就同一 chunk(同一 cache_key)写出**内容不同**的批次;
后 submit 的一方整块覆盖前者 → 同名异体在各块间随机存活,建图后裂成两个节点。

用法:  python data/compendium_rag/_audit_key_overlap.py 535 536 537 540 541 --vs 440 441
输出每个重叠 key 的「仅A/仅B 名称」与**当前缓存存活方**;末行给结论。
存活方全为后者 → 后者覆盖了前者,须按版本统一重提交胜出的一方。
"""
import collections
import json
import os
import sys


def _entities(payload):
    p = payload.get("payload", payload) if isinstance(payload, dict) else {}
    ents = p.get("entities")
    if ents is None and isinstance(p, dict):
        r = p.get("result") or p.get("raw") or {}
        ents = r.get("entities") if isinstance(r, dict) else None
    return set(e["name"] for e in (ents or []))


def load(slot):
    path = os.path.join("data/compendium_rag", "_agent_batch%d.json" % slot)
    if not os.path.exists(path):
        return {}
    d = json.loads(open(path, encoding="utf-8").read())
    return {k: (slot, _entities(v)) for k, v in d.items()}


def main():
    raw = sys.argv[1:]
    argv = [a for a in raw if a != "--vs"]
    if "--vs" not in raw:
        print(__doc__)
        return 1
    split = raw.index("--vs")
    a_slots = [int(x) for x in argv[:split]]
    b_slots = [int(x) for x in argv[split:]]
    A, B = {}, {}
    for s in a_slots:
        A.update(load(s))
    for s in b_slots:
        B.update(load(s))
    ov = sorted(set(A) & set(B))
    print("A=%d key(%s)  B=%d key(%s)  重叠=%d" % (len(A), a_slots, len(B), b_slots, len(ov)))
    live = {"A": 0, "B": 0, "OTHER": 0}
    kind = collections.Counter()
    frag = []
    for k in ov:
        p = "data/compendium_rag/cache/%s/%s.json" % (k[:2], k)
        who = "OTHER"
        if os.path.exists(p):
            names = _entities(json.loads(open(p, encoding="utf-8").read())["raw"])
            who = "A" if names == A[k][1] else ("B" if names == B[k][1] else "OTHER")
        live[who] += 1
        x, y = A[k][1], B[k][1]
        if x == y:
            kind["两侧一致"] += 1
        elif x < y or x <= y:
            kind["B 为超集(存活%s)" % who] += 1
            if who == "A":
                frag.append((k, "丢 B 独有", sorted(y - x)))
        elif y < x:
            kind["A 为超集(存活%s)" % who] += 1
            if who == "B":
                frag.append((k, "丢 A 独有", sorted(x - y)))
        else:
            kind["**分裂**(两侧各有独有名)"] += 1
            frag.append((k, "分裂", sorted(x ^ y)))
    print("存活统计 A=%d B=%d 其他=%d" % (live["A"], live["B"], live["OTHER"]))
    for t, c in sorted(kind.items()):
        print("  %-26s %d" % (t, c))
    if not ov:
        print("结论: 无重叠 chunk → 两批各抽各的,零冲突")
    elif not frag:
        print("结论: 重叠块命名同源(无各自独有名)→ 不裂节点,无需重提交")
    else:
        print("★ 需处理 %d 块(把被覆盖方的独有名补回 = 整批重提交胜出的一方):" % len(frag))
        for k, why, ns in frag:
            print("   %-24s %s %s" % (k, why, ns))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
