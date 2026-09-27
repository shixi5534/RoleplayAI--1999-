# -*- coding: utf-8 -*-
"""R4 自验证（作战书 §2.4 预检/模拟/后检 + 检6 link() 忠实模拟）：
  1) 逐条预检（Applier validate_entry 同规则）
  2) 模拟应用 → 后检全图（悬空 eid/chunk、重名、eid!=name、mentions 一致、仅 aliases 变化）
  3) alias_index 重建（GraphStore.from_dict 同序 setdefault）→ 420 条测试集查询 link() 种子前后 diff
  4) 摘除串不产生新种子缺口：对每个 remove_alias 串做查询包含复断
结果落 _selfval.json。
"""
import json, copy, re, sys, io
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
R4 = Path(__file__).resolve().parent
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)

proposal = json.loads((R4 / "proposal.json").read_text(encoding="utf-8"))
g = json.loads((ROOT / "data/compendium_rag/graph.json").read_text(encoding="utf-8"))
ch = json.loads((ROOT / "data/compendium_rag/chunks.json").read_text(encoding="utf-8"))
ctext = {c["chunk_id"]: c["text"] for c in ch["chunks"]}
t1 = json.loads((ROOT / "data/knowledge/_audit/rag_testset_300_cn.json").read_text(encoding="utf-8"))
t2 = json.loads((ROOT / "data/knowledge/_audit/rag_testset_gen_r1r2.json").read_text(encoding="utf-8"))

errs, warns = [], []
removed = set()

def owner_of(e):
    t = e.get("target")
    return t.get("owner_eid") if isinstance(t, dict) else t

def alias_of(e):
    t = e.get("target")
    return t.get("alias") if isinstance(t, dict) else e.get("alias")

# ── 1) 逐条预检 ──
for e in proposal["entries"]:
    et = e["type"]
    if et == "keep_with_note":
        if e.get("target") not in {x["eid"] for x in g["entities"]}:
            errs.append(f"[{e['id']}] no-op 引用实体不存在: {e.get('target')}")
        continue
    if et != "remove_alias":
        errs.append(f"[{e['id']}] 未预期类型 {et}")
        continue
    o, a = owner_of(e), alias_of(e)
    ent = next((x for x in g["entities"] if x["eid"] == o), None)
    if ent is None:
        errs.append(f"[{e['id']}] 属主不存在: {o}")
    elif a not in ent.get("aliases", []):
        errs.append(f"[{e['id']}] alias 不在属主别名表: {a}@{o}")
    elif (o, a) in removed:
        warns.append(f"[{e['id']}] 重复 remove: {a}@{o}")
    removed.add((o, a))

# ── 2) 模拟应用 + 后检 ──
g2 = copy.deepcopy(g)
idx = {x["eid"]: x for x in g2["entities"]}
changed = []
for (o, a) in removed:
    before = list(idx[o]["aliases"])
    after = [x for x in before if x != a]
    idx[o]["aliases"] = after
    changed.append((o, a, before, after))
    assert len(before) - len(after) == 1

def post_validate(gg):
    e2 = []
    ents2 = {x["eid"]: x for x in gg["entities"]}
    if len(ents2) != len(gg["entities"]):
        e2.append("eid 重复")
    names = {}
    for x in gg["entities"]:
        names.setdefault(x["name"], []).append(x["eid"])
    dups = sorted(n for n, ids in names.items() if len(ids) > 1)
    if dups:
        e2.append(f"重名: {dups[:5]}")
    for x in gg["entities"]:
        if x["eid"] != x["name"]:
            e2.append(f"eid!=name: {x['eid']}")
        if x["mentions"] != len(x["chunk_ids"]):
            e2.append(f"mentions!=chunk_ids: {x['eid']}")
        for cid in x.get("chunk_ids", []):
            if cid not in ctext:
                e2.append(f"悬空 chunk: {cid}@{x['eid']}")
    for ed in gg["edges"]:
        if ed["src"] not in ents2: e2.append(f"悬空 src: {ed['src']}")
        if ed["dst"] not in ents2: e2.append(f"悬空 dst: {ed['dst']}")
        for cid in ed.get("chunk_ids", []):
            if cid not in ctext: e2.append(f"边悬空 chunk: {cid}")
    return e2

post = post_validate(g2)
# 仅 aliases 变化断言
diffs = []
for a1, a2 in zip(g["entities"], g2["entities"]):
    if a1 != a2:
        d = {k for k in a1 if a1.get(k) != a2.get(k)}
        if d != {"aliases"}:
            diffs.append((a1["eid"], d))
if diffs:
    errs.append(f"非 aliases 字段被改动: {diffs[:5]}")

# ── 3) alias_index + link() 前后 diff ──
def _name_matches(name, ql):
    if not name or not ql:
        return False
    is_ascii = all(ord(c) < 128 for c in name)
    if is_ascii:
        pat = re.compile(r"(?<![A-Za-z0-9_])" + re.escape(name.lower()) + r"(?![A-Za-z0-9_])")
        return bool(pat.search(ql))
    if len(name) >= 2:
        return name in ql
    return bool(re.search(r"(?<![\u4e00-\u9fff])" + re.escape(name) + r"(?![\u4e00-\u9fff])", ql))

def build_alias_index(gg):
    ai = {}
    for x in gg["entities"]:
        ai[x["name"]] = x["eid"]
    for x in gg["entities"]:
        for a in x.get("aliases", []):
            ai.setdefault(a, x["eid"])
    return ai

def link(ai, ents_by_eid, q):
    ql = q.lower().strip()
    seeds = {}
    for name in sorted(ai.keys(), key=len, reverse=True):
        if not _name_matches(name, ql):
            continue
        eid = ai[name]
        ent = ents_by_eid[eid]
        sc = 1.0 if name == ent["name"] else 0.9
        if eid not in seeds or sc > seeds[eid][1]:
            seeds[eid] = (ent["name"], sc)
    return {eid: (v[0], v[1]) for eid, v in seeds.items()}

ai0 = build_alias_index(g)
ai1 = build_alias_index(g2)
e0 = {x["eid"]: x for x in g["entities"]}
e1 = {x["eid"]: x for x in g2["entities"]}
queries = [("300_cn", c.get("id", "?"), c["q"]) for c in t1["cases"]] + \
          [("gen_r1r2", c.get("id", "?"), c["q"]) for c in t2["cases"]]
seed_diffs = []
for ts, qid, q in queries:
    s0 = link(ai0, e0, q)
    s1 = link(ai1, e1, q)
    if s0 != s1:
        seed_diffs.append({"testset": ts, "qid": qid, "q": q,
                           "lost": sorted(set(s0) - set(s1)), "gained": sorted(set(s1) - set(s0)),
                           "changed": sorted(k for k in set(s0) & set(s1) if s0[k] != s1[k])})

# ── 4) 摘除串的查询包含复断 + 多主重路由记录 ──
reroutes = []
for (o, a) in sorted(removed):
    qs = [(ts, qid) for ts, qid, qq in queries if _name_matches(a, qq.lower())]
    if qs:
        reroutes.append({"alias": a, "owner": o, "query_hits": qs})
owners_multi = {}
for (o, a) in sorted(removed):
    others = [x["eid"] for x in g["entities"] if x["eid"] != o and a in x.get("aliases", [])]
    if others:
        reroutes.append({"alias": a, "removed_from": o, "still_declared_by": others,
                         "note": "setdefault 语义下 alias_index 键仍在（指向其余声明者或按序重路由）"})

empty_alias_owners = sorted({o for (o, _a) in removed if not idx[o]["aliases"]})

result = {
    "n_entries": len(proposal["entries"]),
    "n_remove_alias": sum(1 for e in proposal["entries"] if e["type"] == "remove_alias"),
    "n_keep_with_note": sum(1 for e in proposal["entries"] if e["type"] == "keep_with_note"),
    "precheck_errors": errs,
    "warnings": warns,
    "postcheck_errors": post,
    "only_aliases_mutated": not diffs,
    "entities_losing_last_alias": empty_alias_owners,
    "n_queries": len(queries),
    "seed_diffs_after_repair": seed_diffs,
    "removed_alias_query_hits": [r for r in reroutes if "query_hits" in r],
    "multi_owner_removals": [r for r in reroutes if "still_declared_by" in r],
}
ok = not errs and not post and not seed_diffs and not diffs
result["verdict"] = "PASS" if ok else "FAIL"
(R4 / "_selfval.json").write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"预检错误: {len(errs)} | 警告: {len(warns)} | 后检错误: {len(post)} | 非 aliases 改动: {len(diffs)}")
print(f"查询种子 diff: {len(seed_diffs)} / {len(queries)} | 摘除别名仍被查询命中: {len([r for r in reroutes if 'query_hits' in r])} | 多主摘除: {len([r for r in reroutes if 'still_declared_by' in r])}")
print(f"失去全部别名的属主: {empty_alias_owners}")
print("VERDICT:", result["verdict"])
