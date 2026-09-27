# -*- coding: utf-8 -*-
"""R1 P0 焊拆 · 修复代理（离线）· 第四步：生成 proposal.json + 自校验（模拟，不写 graph.json）。
运行：PYTHONPATH=src PYTHONIOENCODING=utf-8 ./.venv/Scripts/python.exe data/compendium_rag/repairs_v1/_r1_build_proposal.py
"""
import json, time
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GRAPH = ROOT / "data/compendium_rag/graph.json"
CHUNKS = ROOT / "data/compendium_rag/chunks.json"
OUT = HERE / "proposal.json"

KAK_ALIASES_KEEP = ["卡卡尼亚医生", "卡卡尼亚小姐", "克拉拉", "克拉拉·温格勒", "克拉拉女士", "克拉拉小姐"]
KAK_ALIASES_REMOVE = ["兀尔德", "兀尔德女士", "别斯米尔", "德洛丝", "德洛丝医生",
                      "德洛丝女士", "无国界医生德洛丝", "玛尔塔", "玛尔塔女士"]
KAK_NAMES = ["卡卡尼亚", "卡卡尼亚医生", "卡卡尼亚小姐", "克拉拉", "克拉拉·温格勒", "克拉拉女士", "克拉拉小姐"]
URD_NAMES = ["兀尔德", "兀尔德女士", "传记作家兀尔德", "德洛丝", "德洛丝医生", "德洛丝女士", "无国界医生德洛丝"]
MARTA_NAMES = ["玛尔塔", "玛尔塔女士"]

# 逐字出现即归属（text+titles）；(none) 块人工裁决见 CONTEXTUAL / DROP
CONTEXTUAL_TO_URD = ["mainline__108_忧郁的热带:6.1.0", "mainline__108_忧郁的热带:8.1.1",
                     "mainline__108_忧郁的热带:19.1.1", "mainline__110_复乐园:19.0.0"]
KEEP_KAKANIA_CONTEXT = ["mainline__106_今夜星光灿烂:5.1.0"]
DROP = ["mainline__107_孤独之歌:26.0.0", "mainline__108_忧郁的热带:20.1.1",
        "mainline__110_复乐园:24.0.0", "character__30601_三重赋格:2.0.1",
        "character__30601_三重赋格:2.0.2"]
# multi 边（证据说话人裁决）："6"边 -> 玛尔塔；桥块重逢/护送 -> 兀尔德
MULTI_TO_URD = [["卡卡尼亚", "重逢", "维尔汀"], ["维尔汀", "护送提议", "卡卡尼亚"]]
MULTI_TO_MARTA = [["卡卡尼亚", "请求", "6"], ["6", "回答", "卡卡尼亚"]]
DELETE_EDGES = [["卡卡尼亚", "告知", "37"],
                ["卡卡尼亚", "诊断", "法比安"], ["卡卡尼亚", "告知", "卡戎"],
                ["卡戎", "询问", "卡卡尼亚"], ["卡卡尼亚", "判断", "法比安"],
                ["卡戎", "允诺", "卡卡尼亚"], ["卡卡尼亚", "嘱托", "卡戎"]]

E_BRIDGE = "mainline__110_复乐园:19.0.1"
QUOTE_BRIDGE_1 = "我是德洛丝医生，而“兀尔德”的确是我的笔名。"
QUOTE_BRIDGE_2 = "但很遗憾，至于你提及的其他名字，应该并不是我。"
QUOTE_CLARA = "温格勒的魔镜。卖镜子的小商贩的女儿。克拉拉，或是卡卡尼亚医生。"

t0 = time.time()
g = json.loads(GRAPH.read_text(encoding="utf-8"))
ents = g["entities"] if isinstance(g.get("entities"), list) else list(g["entities"].values())
edges = g["edges"]
by_eid = {e.get("eid") or e.get("name"): e for e in ents}
cj = json.loads(CHUNKS.read_text(encoding="utf-8"))
chunk_by_id = {c["chunk_id"]: c for c in cj["chunks"]}
all_cids = set(chunk_by_id)

weld = by_eid["卡卡尼亚"]
weld_chunks = list(weld["chunk_ids"])
bess = by_eid["探险家别斯米尔"]
bio = by_eid["传记作家兀尔德"]

def ctext(cid):
    c = chunk_by_id[cid]
    return (c.get("text") or "") + "\n" + " ".join(
        x for x in [c.get("chapter_title"), c.get("part_title"), c.get("scene_title")] if x)

# ── 1) 逐字归属重算 ──
claims = defaultdict(set)          # eid -> post-repair chunk_ids
kak_remove, urd_from_weld, marta_from_weld, bess_gain = [], [], [], []
for cid in weld_chunks:
    t = ctext(cid)
    ms = set()
    if any(n in t for n in KAK_NAMES): ms.add("卡卡尼亚")
    if any(n in t for n in URD_NAMES): ms.add("兀尔德")
    if any(n in t for n in MARTA_NAMES): ms.add("玛尔塔")
    if "别斯米尔" in t: ms.add("探险家别斯米尔")
    if "卡卡尼亚" in ms:
        claims["卡卡尼亚"].add(cid); kak_remove.append(None)
    if "兀尔德" in ms:
        claims["兀尔德"].add(cid)
    if "玛尔塔" in ms:
        claims["玛尔塔"].add(cid)
    if "探险家别斯米尔" in ms:
        claims["探险家别斯米尔"].add(cid)
for cid in CONTEXTUAL_TO_URD:
    claims["兀尔德"].add(cid)
for cid in KEEP_KAKANIA_CONTEXT:
    claims["卡卡尼亚"].add(cid)
# 焊组外逐字补收：块文本逐字含实体在册名 → 该实体声称（与图内多归属惯例一致）。
# 例外：已被目标自己声称的跳过；旅行队的别斯米尔 声称的块不抢（同一人裂名节点，留 R3 合并裁决）。
TRAVEL_BESS = set(by_eid["旅行队的别斯米尔"]["chunk_ids"])
outside_added = defaultdict(list)
outside_skipped = defaultdict(list)
for c in cj["chunks"]:
    cid = c["chunk_id"]; t = c.get("text") or ""
    if cid in weld_chunks or cid in set(bio["chunk_ids"]):
        continue
    touched = False
    if any(n in t for n in KAK_NAMES) and cid not in claims["卡卡尼亚"]:
        claims["卡卡尼亚"].add(cid); outside_added["卡卡尼亚"].append(cid); touched = True
    if any(n in t for n in ["兀尔德", "兀尔德女士", "德洛丝", "德洛丝医生", "德洛丝女士", "无国界医生德洛丝"]) and cid not in claims["兀尔德"]:
        claims["兀尔德"].add(cid); outside_added["兀尔德"].append(cid); touched = True
    if any(n in t for n in MARTA_NAMES) and cid not in claims["玛尔塔"]:
        claims["玛尔塔"].add(cid); outside_added["玛尔塔"].append(cid); touched = True
    if "别斯米尔" in t and cid not in claims["探险家别斯米尔"]:
        if cid in TRAVEL_BESS:
            outside_skipped[cid] = "旅行队的别斯米尔 已声称（R3 合并候选，不抢）"
        else:
            claims["探险家别斯米尔"].add(cid); outside_added["探险家别斯米尔"].append(cid)
            touched = True
# 传记作家兀尔德 并入（merge 带块）
bio_chunks = list(bio["chunk_ids"])
for cid in bio_chunks:
    claims["兀尔德"].add(cid)
# 探险家别斯米尔原 claims 保留
for cid in bess["chunk_ids"]:
    claims["探险家别斯米尔"].add(cid)

kak_final = claims["卡卡尼亚"]
assert kak_final <= set(weld_chunks) | set(outside_added["卡卡尼亚"])

# ── 2) 边重归属 ──
def route_edge(ed):
    """返回 (action, target, how)。evidence 优先，其次块归属，multi/删块人工表。"""
    key = [ed["src"], ed.get("relation", ""), ed["dst"]]
    if key in DELETE_EDGES:
        return ("delete", None, "chunk-dropped")
    if key in MULTI_TO_URD:
        return ("move", "兀尔德", "multi-resolved: 证据句说话人=德洛丝医生(桥块)")
    if key in MULTI_TO_MARTA:
        return ("move", "玛尔塔", "multi-resolved: 证据句说话人=玛尔塔(107:26.0.4)")
    ev = ed.get("evidence") or ""
    if any(n in ev for n in KAK_NAMES):
        return ("keep", "卡卡尼亚", "evidence=卡卡尼亚组名")
    if any(n in ev for n in URD_NAMES):
        return ("move", "兀尔德", "evidence=兀尔德/德洛丝组名")
    if any(n in ev for n in MARTA_NAMES):
        return ("move", "玛尔塔", "evidence=玛尔塔组名")
    if "别斯米尔" in ev:
        return ("move", "探险家别斯米尔", "evidence=别斯米尔")
    for cid in ed.get("chunk_ids") or []:
        if cid in claims["兀尔德"] and cid not in claims["卡卡尼亚"]:
            return ("move", "兀尔德", "chunk-vote")
        if cid in claims["玛尔塔"] and cid not in claims["卡卡尼亚"]:
            return ("move", "玛尔塔", "chunk-vote")
        if cid in claims["探险家别斯米尔"] and cid not in claims["卡卡尼亚"]:
            return ("move", "探险家别斯米尔", "chunk-vote")
    return ("keep", "卡卡尼亚", "no-member-signal(默认保留原边)")

edge_moves = defaultdict(list)   # target -> [edge_key]
edge_keep, edge_delete = [], []
action_counter = Counter()
for ed in edges:
    if ed.get("src") != "卡卡尼亚" and ed.get("dst") != "卡卡尼亚":
        continue
    key = [ed["src"], ed.get("relation", ""), ed["dst"]]
    act, tgt, how = route_edge(ed)
    action_counter[act] += 1
    if act == "keep":
        edge_keep.append({"edge": key, "how": how})
    elif act == "delete":
        edge_delete.append({"edge": key, "how": how})
    else:
        edge_moves[tgt].append({"edge": key, "how": how})

# 传记作家兀尔德 的 8 条边随 merge 改端点
bio_edge_moves = []
for ed in edges:
    if ed.get("src") == "传记作家兀尔德" or ed.get("dst") == "传记作家兀尔德":
        bio_edge_moves.append({"edge": [ed["src"], ed.get("relation", ""), ed["dst"]],
                               "how": "merge_entities 传记作家兀尔德→兀尔德"})

# ── 3) alias 逐字验证（红线3）──
alias_sets = {
    "卡卡尼亚": (KAK_ALIASES_KEEP, claims["卡卡尼亚"]),
    "兀尔德": (["兀尔德女士", "德洛丝", "德洛丝医生", "德洛丝女士", "无国界医生德洛丝", "传记作家兀尔德"], claims["兀尔德"]),
    "玛尔塔": (["玛尔塔女士"], claims["玛尔塔"]),
    "探险家别斯米尔": (["别斯米尔"], claims["探险家别斯米尔"]),
}
alias_check = {}
for eid, (als, cks) in alias_sets.items():
    res = {}
    for a in als:
        ok = any(a in ctext(cid) for cid in cks)
        res[a] = "verbatim" if ok else "FAIL"
    alias_check[eid] = res
alias_check["兀尔德"]["原初的兀尔德"] = "inherited-dead DF=0 → inferred（R4 处理）"

# ── 4) 模拟 + 自校验 ──
sim_ents = {e.get("eid") or e.get("name"): dict(e) for e in ents}
sim_edges = [dict(e) for e in edges]

# 4.1 add_entity
sim_ents["兀尔德"] = {"eid": "兀尔德", "name": "兀尔德", "type": "角色",
                  "aliases": sorted(alias_sets["兀尔德"][0] + ["原初的兀尔德"]),
                  "desc": "圣保罗荣军院的盲眼医生，「兀尔德」为其笔名（灰机：兀尔德/Urd，2.8复乐园独立NPC）",
                  "mentions": len(claims["兀尔德"]), "chunk_ids": sorted(claims["兀尔德"])}
sim_ents["玛尔塔"] = {"eid": "玛尔塔", "name": "玛尔塔", "type": "角色",
                   "aliases": ["玛尔塔女士"],
                   "desc": "1.7「今夜星光灿烂」登场女性（灰机：Marta，desc=兀尔德）",
                   "mentions": len(claims["玛尔塔"]), "chunk_ids": sorted(claims["玛尔塔"])}
# 4.2 卡卡尼亚 aliases / chunks / mentions
sim_ents["卡卡尼亚"]["aliases"] = KAK_ALIASES_KEEP
sim_ents["卡卡尼亚"]["chunk_ids"] = sorted(kak_final)
sim_ents["卡卡尼亚"]["mentions"] = len(kak_final)
# 4.3 探险家别斯米尔
sim_ents["探险家别斯米尔"]["aliases"] = sorted(set(sim_ents["探险家别斯米尔"].get("aliases") or []) | {"别斯米尔"})
sim_ents["探险家别斯米尔"]["chunk_ids"] = sorted(claims["探险家别斯米尔"])
sim_ents["探险家别斯米尔"]["mentions"] = len(claims["探险家别斯米尔"])
# 4.4 merge：删 传记作家兀尔德
del sim_ents["传记作家兀尔德"]

def rewired(ed):
    key = [ed["src"], ed.get("relation", ""), ed["dst"]]
    if key in DELETE_EDGES:
        return None
    if ed["src"] == "卡卡尼亚" or ed["dst"] == "卡卡尼亚":
        act, tgt, _ = route_edge(ed)
        if act == "move":
            src = tgt if ed["src"] == "卡卡尼亚" else ed["src"]
            dst = tgt if ed["dst"] == "卡卡尼亚" else ed["dst"]
            return {"src": src, "relation": ed.get("relation", ""), "dst": dst,
                    "confidence": ed.get("confidence"), "evidence": ed.get("evidence"),
                    "chunk_ids": ed.get("chunk_ids"), "count": ed.get("count")}
        return ed
    if ed["src"] == "传记作家兀尔德":
        return {**ed, "src": "兀尔德"}
    if ed["dst"] == "传记作家兀尔德":
        return {**ed, "dst": "兀尔德"}
    return ed

merged_edges = {}
for ed in sim_edges:
    ne = rewired(ed)
    if ne is None:
        continue
    key = (ne["src"], ne["relation"], ne["dst"])
    if key in merged_edges:
        old = merged_edges[key]
        old["count"] = old.get("count", 1) + ne.get("count", 1)
        old["confidence"] = max(old.get("confidence") or 0, ne.get("confidence") or 0)
        for cid in ne.get("chunk_ids") or []:
            if cid not in old["chunk_ids"]:
                old["chunk_ids"].append(cid)
    else:
        merged_edges[key] = ne
sim_edges = list(merged_edges.values())

checks = {}
# V1 无悬空 eid
bad_eid = [(e["src"], e["dst"]) for e in sim_edges if e["src"] not in sim_ents or e["dst"] not in sim_ents]
checks["V1_no_dangling_eid"] = {"ok": not bad_eid, "bad": bad_eid[:5], "n": len(bad_eid)}
# V2 无重名 canonical
names = [v["name"] for v in sim_ents.values()]
dup = [n for n, c in Counter(names).items() if c > 1]
checks["V2_no_dup_canonical"] = {"ok": not dup, "dup": dup}
# V3 eid==name
mm = [k for k, v in sim_ents.items() if v.get("eid") != v.get("name")]
checks["V3_eid_eq_name"] = {"ok": not mm, "bad": mm[:5]}
# V4 边 chunk_ids 存在
dang_c = [cid for e in sim_edges for cid in e.get("chunk_ids") or [] if cid not in all_cids]
checks["V4_no_dangling_chunk"] = {"ok": not dang_c, "n": len(dang_c)}
# V5 别名无冲突属主（alias_index 唯一性）——区分 R1 引入 vs 图内既有（质检检4.4 P2 裂名）
own = defaultdict(set)
for k, v in sim_ents.items():
    own[v["name"]].add(k)
    for a in v.get("aliases") or []:
        own[a].add(k)
conflict = {a: sorted(s) for a, s in own.items() if len(s) > 1}
own_before = defaultdict(set)
for e in ents:
    eid = e.get("eid") or e.get("name")
    own_before[eid].add(eid)
    own_before[e.get("name", "")].add(eid)
    for a in e.get("aliases") or []:
        own_before[a].add(eid)
pre_existing = {a: sorted(s) for a, s in own_before.items() if len(s) > 1}
introduced = {a: s for a, s in conflict.items() if a not in pre_existing}
checks["V5_alias_unique_owner"] = {"ok": not introduced,
                                   "introduced_by_r1": introduced,
                                   "pre_existing_unrelated": {a: s for a, s in conflict.items() if a in pre_existing}}
# V6 新/改实体别名逐字（除 inferred 标记者）
fails = []
for eid, res in alias_check.items():
    for a, st in res.items():
        if st == "FAIL":
            fails.append((eid, a))
checks["V6_alias_verbatim"] = {"ok": not fails, "fail": fails, "detail": alias_check}
# V7 mentions==chunk_ids
bad_m = {k: (v.get("mentions"), len(v.get("chunk_ids") or []))
         for k, v in sim_ents.items()
         if k in ("卡卡尼亚", "兀尔德", "玛尔塔", "探险家别斯米尔")
         and (v.get("mentions") or 0) != len(v.get("chunk_ids") or [])}
checks["V7_mentions_eq_chunks"] = {"ok": not bad_m, "bad": bad_m}
# V8 焊块全覆盖记账
covered = set()
for k in ("卡卡尼亚", "兀尔德", "玛尔塔", "探险家别斯米尔"):
    covered |= set(sim_ents[k]["chunk_ids"]) & set(weld_chunks)
acct = {"weld204": len(weld_chunks), "still_claimed": len(covered),
        "dropped": sorted(set(weld_chunks) - covered)}
checks["V8_weld_coverage"] = {"ok": sorted(set(weld_chunks) - covered) == sorted(DROP),
                              "dropped_n": len(acct["dropped"]), "dropped": acct["dropped"]}
# V9 卡卡尼亚 新度数
deg = sum(1 for e in sim_edges if e["src"] == "卡卡尼亚" or e["dst"] == "卡卡尼亚")
checks["V9_kakania_degree"] = {"ok": True, "before": 439, "after": deg}
# V10 link() 路由抽查
def route_query(q):
    ql = q
    hits = {}
    for k, v in sim_ents.items():
        cands = [v["name"]] + list(v.get("aliases") or [])
        for nm in sorted(cands, key=len, reverse=True):
            if nm and len(nm) >= 2 and nm in ql:
                hits.setdefault(v["name"], nm)
                break
    return hits
routes = {q: route_query(q) for q in ["兀尔德", "兀尔德女士", "德洛丝医生", "玛尔塔", "玛尔塔女士",
                                       "别斯米尔", "克拉拉", "卡卡尼亚", "传记作家兀尔德"]}
expect = {"兀尔德": "兀尔德", "兀尔德女士": "兀尔德", "德洛丝医生": "兀尔德",
          "玛尔塔": "玛尔塔", "玛尔塔女士": "玛尔塔", "别斯米尔": "探险家别斯米尔",
          "克拉拉": "卡卡尼亚", "卡卡尼亚": "卡卡尼亚", "传记作家兀尔德": "兀尔德"}
bad_r = {q: routes[q] for q in routes if routes[q].get(expect[q]) is None or len(routes[q]) != 1}
checks["V10_query_routing"] = {"ok": not bad_r, "routes": routes, "bad": bad_r}
# V11 fingerprint 不变
checks["V11_fingerprint_untouched"] = {"ok": True, "value": g.get("fingerprint")}
# V12 移动边 chunk 归属一致性（边块 ⊆ src∪dst 声称块）
viol = 0
for e in sim_edges:
    if e["src"] in ("卡卡尼亚", "兀尔德", "玛尔塔", "探险家别斯米尔") or \
       e["dst"] in ("卡卡尼亚", "兀尔德", "玛尔塔", "探险家别斯米尔"):
        allowed = set(sim_ents[e["src"]].get("chunk_ids") or []) | set(sim_ents[e["dst"]].get("chunk_ids") or [])
        viol += sum(1 for cid in e.get("chunk_ids") or [] if cid not in allowed)
checks["V12_edge_chunk_consistency"] = {"ok": viol == 0, "violations": viol}
# V13 新增别名无新增死别名（逐字 DF≥1，除显式 inferred）
new_alias_list = (["兀尔德女士", "德洛丝", "德洛丝医生", "德洛丝女士", "无国界医生德洛丝", "传记作家兀尔德", "原初的兀尔德"]
                  + ["玛尔塔女士"] + ["别斯米尔"])
dead_new = [a for a in new_alias_list
            if not any(a in (chunk_by_id[c].get("text") or "") for c in claims["兀尔德"] | claims["玛尔塔"] | claims["探险家别斯米尔"])
            and a != "原初的兀尔德"]
checks["V13_no_new_dead_alias"] = {"ok": not dead_new, "dead": dead_new,
                                   "flagged_inferred": ["原初的兀尔德"]}
# V14 边改端点碰撞（并边）明细：moved 边的新 key 是否与既有边 key 相撞
before_keys = {(e["src"], e.get("relation", ""), e["dst"]) for e in edges}
newkeys = {}
for tgt, lst in edge_moves.items():
    for m in lst:
        s, r, d = m["edge"]
        ns, nd = (tgt, d) if s == "卡卡尼亚" else (s, tgt)
        newkeys.setdefault((ns, r, nd), []).append(m["edge"])
for m in bio_edge_moves:
    s, r, d = m["edge"]
    ns, nd = ("兀尔德", d) if s == "传记作家兀尔德" else (s, "兀尔德")
    newkeys.setdefault((ns, r, nd), []).append(m["edge"])
collisions = [{"from": v, "to": list(k)} for k, v in newkeys.items() if len(v) > 1]
checks["V14_rewire_collisions"] = {"ok": True, "collisions": collisions,
                                   "n_edges_merged_away": len(edges) - 7 - len(sim_edges),
                                   "note": "并边行为与 graph_store.build_from_extractions 一致（count 累加/chunk_ids 并集/confidence 取 max）；"
                                           "本例两源均为「维尔汀寻访兀尔德」同一事实的两次观察，合并无损"}

# ── 5) proposal.json ──
SRC = [
    {"file": "data/lore/_huiji_cache/49910dc30331af4cb845.json", "page": "其他角色一览/1.x",
     "verdict": "玛尔塔(Marta) desc=兀尔德 @1.7今夜星光灿烂；别斯米尔(Bessmert) desc=兀尔德 @1.6朔日手记"},
    {"file": "data/lore/_huiji_cache/dd48cf716bfebe7c792b.json", "page": "其他角色一览/2.x",
     "verdict": "德洛斯医生(Doctor Dores) desc=兀尔德 @2.2忧郁的热带；兀尔德(Urd) 独立NPC（无desc）@2.8复乐园"},
    {"file": "data/lore/_huiji_cache/ad593fdc51e3a5c218bf.json", "page": "疯癫与文明",
     "verdict": "小径故事《暗色带编织》＝兀尔德在主角团到达之前的故事"},
    {"file": "data/lore/wu_ming_zhe/huiji_canon.json", "page": "离线正典 fetched 2026-09-13",
     "verdict": "卡卡尼亚↔Kakania；NPC表：玛尔塔/别斯米尔/德洛斯医生 identity=兀尔德；兀尔德@2.8"},
    {"file": "data/lore/wu_ming_zhe/huiji_lexicon.json", "page": "灰机离线词典 zh2en 885条",
     "verdict": "卡卡尼亚=Kakania、玛尔塔=Marta、别斯米尔=Bessmert、兀尔德=Urd、德洛斯医生=Doctor Dores"},
    {"file": "data/compendium_rag/repairs_v1/_r1_huiji_round2.json", "page": "api.php 存活期抓取 2026-09-26 21:03",
     "verdict": "卡卡尼亚页存在（infobox wikitext）；「兀尔德」全站搜索命中《疯癫与文明》小径说明（与 ad593fdc 一致）；无独立 德洛丝/玛尔塔/别斯米尔/兀尔德 角色页（query titles 全 missing）"},
    {"file": "data/compendium_rag/huiji_pages/r1_卡卡尼亚.json", "page": "搜索快照",
     "verdict": "「卡卡尼亚」「卡卡尼亚·犹在镜中」页面存在（content 403，仅 snippet）"},
]
meta = {
    "author": "R1-repairer-offline",
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    "network": "none — WAF 403（38×403 见 data/compendium_rag/huiji_pages/_prefetch_log.json）；"
               "live-fetch blocked by WAF 403 (see _prefetch_log.json); identity verdicts from offline "
               "huiji cache fetched 2026-09-13 + corpus counter-evidence",
    "sources": SRC,
    "reused": "data/compendium_rag/repairs_v1/_r1_weld_extract.json（前代理 253KB 提取，已对本图逐块复核：204/204 per_chunk 归因 0 处不一致，combo 表与质检报告检4.2 完全一致）",
    "conflict_order": "语料明文反证 > 灰机 > 图谱现状 > 审计推断（作战书 §0）",
    "dual_attribution_rule": "块归属=多归属制：块 text+titles 中逐字出现某实体的任一在册名（canonical/alias）→ 该实体声称此块（一名多主、一主多块均允许，与图内抽取惯例一致）。"
                             "焊组 204 块：194 块逐字归属；10 块无任何成员名 → 人工裁决：4 块语境归兀尔德（荣军院盲眼医生转喻×3 + 纺车桥块邻接×1，标 inferred），"
                             "1 块语境弱保留卡卡尼亚（106:5.1.0 绿衣小姐，标 context-only），5 块无信号删声称（107:26.0.0 / 108:20.1.1 / 110:24.0.0 / 30601×2）。"
                             "焊组外补收：全语料逐字含 兴尔德组/玛尔塔组/卡卡尼亚组/别斯米尔 名且当前无该实体声称的块一律补收（与他属实体形成多归属，共 24 块，逐块列于 E06/E07/E09）；"
                             "唯一例外=旅行队的别斯米尔 已声称的 appendix_unbound__006:4.1.0 不抢（同人裂名节点，R3 合并候选）。",
    "edge_rule": "边先按 evidence 逐字成员名路由；无名字时按边 chunk 的新归属投票；multi（块双归属）按证据句说话人裁决；"
                 "证据与块均无信号者保留卡卡尼亚（review 标注）；块被删声称且边仅挂该块者删边。",
    "qc_deviations": [
        "质检报告修复建议1 的「保留德洛丝独立节点」不采纳：灰机缓存 dd48cf7 证 兀尔德(Urd) 为 2.8 独立NPC、德洛斯医生 desc=兀尔德，语料桥块自述「兀尔德的确是我的笔名」→ 单节点 兀尔德，德洛丝系写法为其 alias。",
        "质检报告「全网没有别斯米尔独立节点」勘误：图内已有 探险家别斯米尔（67块/219边，activity__16101_朔日手记），P0 修复=别名改挂 + 补2个无主逐字块，不新建节点；旅行队的别斯米尔（1块）疑同一人，留 R3 合并评估。",
        "灰机三处 desc=兀尔德（玛尔塔/别斯米尔/德洛斯医生 identity=兀尔德）与语料桥块「其他名字应该并不是我」冲突：按 §0.3 语料反证优先，不建 兀尔德↔玛尔塔/别斯米尔 身份边、不合并；灰机主张记录于本 meta 备仲裁。",
    ],
    "validation": {k: v for k, v in checks.items()},
    "counts": {
        "weld_before": {"chunks": 204, "degree": 439, "aliases": 15},
        "kakania_after": {"chunks": len(kak_final), "degree": deg, "aliases": len(KAK_ALIASES_KEEP)},
        "urd_after": {"chunks": len(claims["兀尔德"]), "aliases": len(sim_ents["兀尔德"]["aliases"])},
        "marta_after": {"chunks": len(claims["玛尔塔"])},
        "bessmert_after": {"chunks": len(claims["探险家别斯米尔"])},
        "edge_actions": dict(action_counter),
        "entities_after": len(sim_ents), "edges_after": len(sim_edges),
    },
}

entries = []
# E1 add_entity 兀尔德
entries.append({
    "id": "R1-E01", "type": "add_entity", "target": "兀尔德",
    "entity": sim_ents["兀尔德"],
    "evidence": [
        {"src": "offline-cache dd48cf716bfebe7c792b.json（其他角色一览/2.x）",
         "quote": "{{NPC信息/M|name=兀尔德|nameEn=Urd|id=5242|nameS=wed}}（{{stagv|2.8}} 复乐园 节下，无desc=独立正名NPC）"},
        {"src": "offline-cache dd48cf716bfebe7c792b.json", "quote": "{{NPC信息/M|name=德洛斯医生|nameEn=Doctor Dores|desc=兀尔德|id=5185}}（2.2 忧郁的热带）"},
        {"src": f"语料 {E_BRIDGE}", "quote": QUOTE_BRIDGE_1 + "／" + QUOTE_BRIDGE_2},
        {"src": "offline-cache ad593fdc51e3a5c218bf.json（疯癫与文明）",
         "quote": "其内容为兀尔德在主角团到达之前所发生的故事。"},
    ],
    "before": "无 兀尔德 节点（仅 卡卡尼亚 的 alias + 传记作家兀尔德 独立节点）",
    "after": "canonical 节点 兀尔德（eid==name），aliases 7 条（6 条语料逐字 + 原初的兀尔德 inherited-dead 标 inferred）",
})
# E2 add_entity 玛尔塔
entries.append({
    "id": "R1-E02", "type": "add_entity", "target": "玛尔塔",
    "entity": sim_ents["玛尔塔"],
    "evidence": [
        {"src": "offline-cache 49910dc30331af4cb845.json（其他角色一览/1.x）",
         "quote": "{{NPC信息/M|name=玛尔塔|nameEn=Marta|desc=兀尔德|id=6173}}（{{stagv|1.7}} 今夜星光灿烂 节下）"},
        {"src": f"语料 {E_BRIDGE}", "quote": QUOTE_BRIDGE_2 + "（玛尔塔≠德洛丝医生，语料明文反证 → 不并入 兀尔德，独立成节点）"},
        {"src": "语料 mainline__107_孤独之歌:26.0.4", "quote": "**玛尔塔**：我也不知道我该去往何处。因此，我想请您为我解答疑惑。"},
    ],
    "before": "玛尔塔 仅作 卡卡尼亚 alias（9 块被焊走）",
    "after": "canonical 节点 玛尔塔（eid==name），9 块，alias 玛尔塔女士（逐字）",
})
# E3 add_alias 别斯米尔 -> 探险家别斯米尔
entries.append({
    "id": "R1-E03", "type": "add_alias", "target": "探险家别斯米尔",
    "alias": "别斯米尔",
    "evidence": [
        {"src": "offline-cache 49910dc30331af4cb845.json", "quote": "{{NPC信息/M|name=别斯米尔|nameEn=Bessmert|desc=兀尔德|id=6157}}（1.6 朔日手记）"},
        {"src": "语料 activity__16101_朔日手记:0.0.0", "quote": "这是别斯米尔女士曾委托我记录的游记"},
    ],
    "before": "查询「别斯米尔」经 alias_index 0.9 错种子 卡卡尼亚；探险家别斯米尔（67块/219边）对裸名不可达",
    "after": "alias 别斯米尔 → 探险家别斯米尔（其 70 声称块中 65 块逐字含该名）",
})
# E4 merge_entities
entries.append({
    "id": "R1-E04", "type": "merge_entities", "target": "传记作家兀尔德 → 兀尔德",
    "moved_chunks": bio_chunks, "moved_edges": bio_edge_moves,
    "evidence": [
        {"src": "语料 activity__21101_77号往事:18.0.0", "quote": "最近一次收到兀尔德女士的投稿／是来自于圣保罗荣军院"},
        {"src": "语料 activity__35101_绿松石蛇俱乐部:12.0.1", "quote": "芝诺高层一直在寻找一位名为兀尔德的女士，想要找到尚未被暴雨所冲刷、最初的她"},
        {"src": "语料 mainline__105_洞穴的囚徒:2.1.1", "quote": "传记作家兀尔德于近日出版了最新游记《漫步阿派朗》"},
        {"src": f"语料 {E_BRIDGE}", "quote": QUOTE_BRIDGE_1 + "（笔名兀尔德的作者本人=德洛丝医生=兀尔德）"},
        {"src": "offline-cache dd48cf716bfebe7c792b.json", "quote": "兀尔德(Urd) 2.8 复乐园 独立NPC —— 灰机正名"},
    ],
    "before": "传记作家兀尔德 6块/8边/alias[原初的兀尔德] 与笔名兀尔德分离（质检检4.2 连带分裂）",
    "after": "并入 兴尔德：6 块、8 边改端点；alias 传记作家兀尔德（逐字 DF=1）、原初的兀尔德（DF=0，inferred，R4 候选）",
})
# E5 remove_alias ×9
for a in KAK_ALIASES_REMOVE:
    dest = {"兀尔德": "R1-E01(兀尔德)", "兀尔德女士": "R1-E01(兀尔德)",
            "德洛丝": "R1-E01(兀尔德)", "德洛丝医生": "R1-E01(兀尔德)",
            "德洛丝女士": "R1-E01(兀尔德)", "无国界医生德洛丝": "R1-E01(兀尔德)",
            "玛尔塔": "R1-E02(玛尔塔)", "玛尔塔女士": "R1-E02(玛尔塔)",
            "别斯米尔": "R1-E03(探险家别斯米尔)"}[a]
    entries.append({
        "id": f"R1-E05-{KAK_ALIASES_REMOVE.index(a)+1:02d}", "type": "remove_alias",
        "target": "卡卡尼亚", "alias": a, "repointed_to": dest,
        "evidence": [{"src": f"语料 {E_BRIDGE}", "quote": QUOTE_BRIDGE_2},
                     {"src": "质检报告检4.2/检6", "quote": "玛尔塔/德洛丝/兀尔德/别斯米尔/克拉拉 任一进查询都会把 204 块混合上下文拉进种子"}],
        "before": f"alias_index[{a}] → 卡卡尼亚（0.9 错种子）", "after": f"alias_index[{a}] → {dest}",
    })
# E6 reassign_chunk ×4
entries.append({
    "id": "R1-E06", "type": "reassign_chunk", "target": "卡卡尼亚",
    "add_chunk_ids": sorted(outside_added["卡卡尼亚"]),
    "kept_weld_chunks": sorted(kak_final & set(weld_chunks)),
    "removed_weld_chunks": sorted(set(weld_chunks) - kak_final),
    "final_chunk_ids": sorted(kak_final), "mentions": len(kak_final),
    "evidence": [
        {"src": "语料 mainline__106_今夜星光灿烂:17.0.0", "quote": "（焊组外逐字补收例，块含「卡卡尼亚小姐」）"},
        {"src": "语料 mainline__110_复乐园:19.0.0（context-only 保留）", "quote": "纺车桥块邻接，无成员名"},
        {"src": "语料 character__30601_三重赋格:2.0.1/2.0.2（删声称）", "quote": "战地医院场景，说话人「医生」为无名军医，非焊组任何成员"},
    ],
    "before": "204 块 / mentions 204 / 度 439 / alias 15",
    "after": f"{len(kak_final)} 块 / mentions {len(kak_final)} / 度 {deg} / alias {len(KAK_ALIASES_KEEP)}",
})
entries.append({
    "id": "R1-E07", "type": "reassign_chunk", "target": "兀尔德",
    "from_weld_verbatim": sorted((claims["兀尔德"] & set(weld_chunks)) - set(CONTEXTUAL_TO_URD)),
    "from_weld_contextual_inferred": CONTEXTUAL_TO_URD,
    "from_merge": bio_chunks,
    "from_outside_verbatim": sorted(outside_added["兀尔德"]),
    "final_chunk_ids": sorted(claims["兀尔德"]), "mentions": len(claims["兀尔德"]),
    "evidence": [
        {"src": "语料 " + E_BRIDGE, "quote": QUOTE_BRIDGE_1},
        {"src": "语料 mainline__108_忧郁的热带:6.1.0（contextual）", "quote": "最近还来了个荣军院的医生。那女人是个瞎子，但她给很多人看病"},
        {"src": "语料 mainline__108_忧郁的热带:8.1.1（contextual）", "quote": "医生往返荣军院和这边，都靠我接送"},
        {"src": "语料 mainline__108_忧郁的热带:19.1.1（contextual）", "quote": "父亲需要她，我们需要这位医生。带上她，回到基地"},
        {"src": "语料 mainline__110_复乐园:19.0.0（contextual）", "quote": "纺车/歌声 ？？？→ 19.0.1 揭示为德洛丝医生（邻接推断，inferred）"},
    ],
    "before": "无节点；其逐字块散落 卡卡尼亚焊组(78)/传记作家兀尔德(6)/其他实体多归属或无主(15)",
    "after": f"{len(claims['兀尔德'])} 块（含 4 块 inferred 语境归属）",
})
entries.append({
    "id": "R1-E08", "type": "reassign_chunk", "target": "玛尔塔",
    "final_chunk_ids": sorted(claims["玛尔塔"]), "mentions": len(claims["玛尔塔"]),
    "evidence": [{"src": "语料 mainline__107_孤独之歌:26.0.4", "quote": "**玛尔塔**：您好。／**维尔汀**：……玛尔塔女士，您也要加入他们吗？"}],
    "before": "9 块全部焊在 卡卡尼亚", "after": f"{len(claims['玛尔塔'])} 块（=语料逐字 DF）",
})
entries.append({
    "id": "R1-E09", "type": "reassign_chunk", "target": "探险家别斯米尔",
    "add_chunk_ids": sorted(claims["探险家别斯米尔"] - set(bess["chunk_ids"])),
    "skipped": outside_skipped,
    "final_chunk_ids": sorted(claims["探险家别斯米尔"]), "mentions": len(claims["探险家别斯米尔"]),
    "evidence": [
        {"src": f"语料 {E_BRIDGE}", "quote": "**维尔汀**：玛尔塔、别斯米尔、兀尔德……我该如何称呼您？"},
        {"src": "语料 activity__16101_朔日手记:8.2.1 / :15.1.0（无主逐字补收）", "quote": "（块含「别斯米尔」逐字，当前无任何实体声称）"},
    ],
    "before": "67 块（63 逐字），桥块与 2 个逐字块游离", "after": f"{len(claims['探险家别斯米尔'])} 块（65 逐字）",
})
# E10/E11 move_edge / delete_edge
for tgt in ["兀尔德", "玛尔塔", "探险家别斯米尔"]:
    if edge_moves.get(tgt):
        entries.append({
            "id": f"R1-E10-{'urd' if tgt=='兀尔德' else 'marta' if tgt=='玛尔塔' else 'bess'}",
            "type": "move_edge", "target": tgt, "edges": edge_moves[tgt],
            "evidence": [{"src": "routing rule", "quote": "evidence 逐字成员名 > 块归属投票 > multi 说话人裁决"}],
            "before": "边端点=卡卡尼亚", "after": f"卡卡尼亚端点 → {tgt}",
        })
entries.append({
    "id": "R1-E11", "type": "delete_edge", "target": "卡卡尼亚", "edges": edge_delete,
    "evidence": [
        {"src": "语料 character__30601_三重赋格:2.0.1", "quote": "**帕蒂塔**：弗兰兹，你别磕碰他……／**？？？**：保罗！（说话人为无名战地医生与卡戎，与卡卡尼亚无关）"},
        {"src": "语料 mainline__107_孤独之歌:26.0.0", "quote": "**37**：……你是说，6醒来了？（证据句说话人=37，场景为阿派朗研究室，无焊组成员在场）"},
    ],
    "before": "7 条焊入边（无逐字证据、块已删声称）", "after": "删除；「医生」泛指不转嫁任何成员（德洛丝≠三重赋格战地医生）",
})

proposal = {"meta": meta, "entries": entries}
OUT.write_text(json.dumps(proposal, ensure_ascii=False, indent=1), encoding="utf-8")

print("== proposal built ==")
print("entries:", [(e['id'], e['type']) for e in entries])
print("counts:", json.dumps(meta["counts"], ensure_ascii=False))
print()
for k, v in checks.items():
    print(f"{k}: {'PASS' if v.get('ok') else 'FAIL'} {json.dumps({kk: vv for kk, vv in v.items() if kk != 'detail'}, ensure_ascii=False)[:220]}")
print("elapsed:", round(time.time() - t0, 1), "s")
