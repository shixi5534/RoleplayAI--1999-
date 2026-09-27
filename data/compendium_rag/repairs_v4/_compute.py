# -*- coding: utf-8 -*-
"""R4 修复者计算脚本（只读 graph.json/chunks.json/testsets；结果落本目录 _compute_results.json）。
四项计算：
  D1 死别名全量重算（属主声称块逐字判定，QC 检3 同口径）+ 测试集路由检查
  D2 接地标注重算（967 nowhere / 122 elsewhere 两类）+ 9 泛称节点 post-R3 篇目
  D3 chunk→version 全量映射（doc-id 前缀规则，meetability 核证表）
  D4 跨版本边全量重算（对齐 meetability 199 条）+ 分类特征
"""
import json, re, sys, io
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
R4 = Path(__file__).resolve().parent

g = json.loads((ROOT / "data/compendium_rag/graph.json").read_text(encoding="utf-8"))
ch = json.loads((ROOT / "data/compendium_rag/chunks.json").read_text(encoding="utf-8"))
chunks = ch["chunks"]
ctext = {c["chunk_id"]: c["text"] for c in chunks}
ents = {e["eid"]: e for e in g["entities"]}
print(f"graph: {len(ents)} entities / {len(g['edges'])} edges | chunks: {len(ctext)}")

# ---------------- 测试集查询 ----------------
t1 = json.loads((ROOT / "data/knowledge/_audit/rag_testset_300_cn.json").read_text(encoding="utf-8"))
t2 = json.loads((ROOT / "data/knowledge/_audit/rag_testset_gen_r1r2.json").read_text(encoding="utf-8"))
queries = []  # (testset, id, q)
for c in t1["cases"]:
    queries.append(("300_cn", c.get("id", "?"), c["q"]))
for c in t2["cases"]:
    queries.append(("gen_r1r2", c.get("id", "?"), c["q"]))
print(f"queries: {len(queries)}")

# ---------------- D1 死别名 ----------------
blob_owner = {eid: "\n".join(ctext[cid] for cid in e.get("chunk_ids", []) if cid in ctext)
              for eid, e in ents.items()}
alias_decl = Counter()  # alias -> 声明实体数
for eid, e in ents.items():
    for a in e.get("aliases", []):
        alias_decl[a] += 1
canon_names = set(ents)
total_alias_decls = sum(len(e.get("aliases", [])) for e in ents.values())
print(f"alias declarations: {total_alias_decls} | distinct: {len(alias_decl)}")

dead = []
for eid, e in sorted(ents.items()):
    blob = blob_owner[eid]
    for a in e.get("aliases", []):
        if a not in blob:
            df_total = sum(1 for t in ctext.values() if a in t)
            hit_docs = sorted({cid.split(":")[0] for cid, t in ctext.items() if a in t})
            qhits = [(ts, qid, q) for ts, qid, q in queries if a in q]
            dead.append({
                "owner": eid, "alias": a,
                "owner_chunks": len(e.get("chunk_ids", [])),
                "df_total": df_total,
                "elsewhere_docs": hit_docs[:8],
                "elsewhere_docs_n": len(hit_docs),
                "other_canonical": a in canon_names,
                "multi_owner": alias_decl[a] > 1,
                "multi_owners": [o for o, oe in ents.items() if a in oe.get("aliases", [])],
                "query_hits": [{"testset": ts, "qid": qid, "q": q} for ts, qid, q in qhits],
            })
n_nowhere = sum(1 for d in dead if d["df_total"] == 0)
n_query = sum(1 for d in dead if d["query_hits"])
print(f"DEAD aliases (not in owner blob): {len(dead)} | nowhere-in-corpus: {n_nowhere} | query-hit: {n_query}")
for d in dead:
    if d["query_hits"]:
        print("  [QUERY-HIT]", d["owner"], "|", d["alias"], "|", [(x['testset'], x['qid']) for x in d['query_hits']][:4])

# ---------------- D2 接地 ----------------
alltext = "\n".join(ctext.values())
g_none, g_mismatch, g_ok = [], [], []
for eid, e in sorted(ents.items()):
    name = e["name"]
    blob = blob_owner[eid]
    if name in blob:
        g_ok.append(eid)
        continue
    df_total = sum(1 for t in ctext.values() if name in t)
    rec = {"eid": eid, "type": e.get("type"), "nchunks": len(e.get("chunk_ids", [])),
           "df_total": df_total,
           "elsewhere_docs": sorted({cid.split(":")[0] for cid, t in ctext.items() if name in t})[:6]}
    (g_mismatch if df_total > 0 else g_none).append(rec)
print(f"grounding: ok={len(g_ok)} | mismatch(elsewhere)={len(g_mismatch)} | none(nowhere)={len(g_none)}")

# ---------------- D3 版本映射 ----------------
MAINLINE = {"000": "1.0", "101": "1.0", "102": "1.0", "103": "1.0", "104": "1.0",
            "105": "1.4", "106": "1.7", "107": "1.9", "108": "2.2", "109": "2.6",
            "110": "2.8", "111": "3.0", "112": "3.3", "113": "3.7"}
NULL_DOCS_REASON = {
    "activity__305101_翡冷翠之春": "联动活动（刺客信条），本地无版本证据（clean_report missing_version）",
    "activity__305201_入雅典记": "联动活动（刺客信条），本地无版本证据（clean_report missing_version）",
    "activity__385101_聚合浪潮": "联动/特殊活动，本地无版本证据（clean_report missing_version）",
    "appendix_unbound__071_S02_啁啾表_收藏品": "文件名无内嵌版本（S02），meetability 未定",
    "appendix_unbound__072_第十章10_25": "文件名无内嵌版本，meetability 未定",
    "appendix_unbound__073_雷米特杯兑换活动": "文件名无内嵌版本，meetability 未定",
    "appendix_unbound__074_雷米特杯赛季活动": "文件名无内嵌版本，meetability 未定",
}

def doc_version(doc_id: str):
    """返回 (version, rule, confidence)。version=None 表示未定。"""
    pre, rest = doc_id.split("__", 1)
    if pre == "mainline":
        num = rest.split("_", 1)[0]
        if num in MAINLINE:
            return MAINLINE[num], "mainline__NNN 标题查表（meetability 核证）", "high"
        return None, "mainline 未知章号", "none"
    if pre == "activity":
        num = rest.split("_", 1)[0]
        if doc_id in NULL_DOCS_REASON:
            return None, NULL_DOCS_REASON[doc_id], "none"
        if len(num) == 5 and num.endswith("01") and num[2:-2] == "":
            pass
        if len(num) == 5:
            ver = f"{num[0]}.{num[1]}"
            return ver, "activity__XY101 → X.Y（18/18 与 huiji 版本弧相符）", "high"
        return None, f"activity 未知编号 {num}", "none"
    if pre == "character":
        num = rest.split("_", 1)[0]
        if len(num) == 5:
            return f"{num[0]}.{num[1]}", "character__XYz01 → X.Y", "high"
        return None, f"character 未知编号 {num}", "none"
    if pre == "anecdote":
        num = rest.split("_", 1)[0]
        if len(num) == 4 and num.startswith("19"):
            return "1.9", "anecdote__19XX → 推定 1.9（clean_report 留空；低置信）", "low"
        return None, f"anecdote 未知编号 {num}", "none"
    if pre == "appendix_unbound":
        m = re.match(r"^(\d{3})_(\d)_(\d)_", rest)
        if m:
            return f"{m.group(2)}.{m.group(3)}", "文件名内嵌版本 NNN_X_Y → X.Y", "high"
        return None, NULL_DOCS_REASON.get(doc_id, "appendix_unbound 无内嵌版本"), "none"
    return None, "未知 doc 类别", "none"

doc_ver = {}
for doc_id in sorted({c["doc_id"] for c in chunks}):
    doc_ver[doc_id] = doc_version(doc_id)
cmap = {}
null_chunks = []
for c in chunks:
    v, rule, conf = doc_ver[c["doc_id"]]
    cmap[c["chunk_id"]] = v
    if v is None:
        null_chunks.append(c["chunk_id"])
n_null = len(null_chunks)
print(f"version map: {len(cmap)} chunks | mapped: {len(cmap)-n_null} | null: {n_null}")
null_by_doc = Counter(cid.split(":")[0] for cid in null_chunks)
print("null docs:", dict(null_by_doc))
conf_by_rule = Counter((doc_ver[d][2]) for d in doc_ver)
print("doc confidence:", dict(conf_by_rule))
# 覆盖度：mapped chunks 里各 rule
chunk_rule_cnt = Counter()
for c in chunks:
    chunk_rule_cnt[doc_ver[c["doc_id"]][1]] += 1
for k, v in chunk_rule_cnt.most_common():
    print(f"  rule[{k}]: {v} chunks")

# ---------------- D4 跨版本边 ----------------
PUNCT = re.compile(r"[\s「」【】\*\"“”‘'·—–\-。．.，,、！!？?：:；;（）()\[\]{}<>《》〈〉…]+")
def norm(s):
    return PUNCT.sub("", s)
norm_ctext = {cid: norm(t) for cid, t in ctext.items()}

def ev_in_chunks(evidence, cids):
    if not evidence:
        return False
    evs = [norm(evidence)]
    for marker in ["【标题卡】", "「", "」", "**"]:
        evs = [e.replace(marker, "") for e in evs]
    nset = {norm(x) for x in evs}
    for cid in cids:
        t = norm_ctext.get(cid)
        if t is None:
            continue
        for ev in nset:
            if ev and ev in t:
                return True
    return False

cross_edges = []
cooc_cache = {}
for idx, ed in enumerate(g["edges"]):
    vers = [cmap.get(cid) for cid in ed.get("chunk_ids", [])]
    vset = sorted({v for v in vers if v})
    if len(vset) < 2:
        continue
    src, dst = ed["src"], ed["dst"]
    pair = (src, dst)
    if pair not in cooc_cache:
        cnt = 0
        for cid, t in ctext.items():
            if src in t and dst in t:
                cnt += 1
        cooc_cache[pair] = cnt
    name_in_cited = {src: False, dst: False}
    for cid in ed.get("chunk_ids", []):
        t = norm_ctext.get(cid, "")
        if src in t or src in t.replace(" ", ""):
            name_in_cited[src] = True
        if dst in t or dst in t.replace(" ", ""):
            name_in_cited[dst] = True
    cross_edges.append({
        "src": src, "dst": dst, "relation": ed.get("relation"),
        "confidence": ed.get("confidence"), "evidence": (ed.get("evidence") or "")[:120],
        "versions": vset,
        "chunk_ids": ed.get("chunk_ids", []),
        "cooc_chunks": cooc_cache[pair],
        "name_in_cited": name_in_cited,
        "evidence_verbatim": ev_in_chunks(ed.get("evidence"), ed.get("chunk_ids", [])),
        "src_type": ents[src]["type"] if src in ents else "?",
        "dst_type": ents[dst]["type"] if dst in ents else "?",
    })
print(f"cross-version edges: {len(cross_edges)} (meetability reported 199)")

# ---------------- dump ----------------
out = {
    "n_entities": len(ents), "n_edges": len(g["edges"]), "n_chunks": len(ctext),
    "n_alias_decls": total_alias_decls, "n_distinct_alias": len(alias_decl),
    "dead": dead,
    "grounding_none": g_none, "grounding_mismatch": g_mismatch,
    "version_map": cmap,
    "version_null_chunks": null_chunks,
    "doc_version_rules": {d: list(v) for d, v in doc_ver.items()},
    "cross_edges": cross_edges,
    "queries_sample": [],
}
(R4 / "_compute_results.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print("dumped -> _compute_results.json")
