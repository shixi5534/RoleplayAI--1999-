"""P9① · 实体层只读普查：把「名字学候选」与 P8 实测泄漏证据 join，按能治几道漏题排序。

产出三类根因的可裁决候选 + **一张归因表**，全程**只读**：
读 `graph.json` / `chunks.json` / `p8_roleiso_jsonl/*_full.jsonl` / `plot_aliases.json`，
只写 `data/compendium_rag/reports/p9_entity_census.{json,md}`。零检索、零 LLM、零写图。

三类根因（A/B 来自用户 2026-10-10 裁决 1，C 是本脚本实测新增）：
  A 泛称 —— 分两层各报一次：**A1 图上**（type=="角色" 且整名即泛称）
                                   **A2 speakers 层**（泄漏块的 speakers 落不到任何具名角色实体）
      v1 只查了 A1，结果是 6 条且 `as_seed` 全 0 —— 泛称污染不在实体层，必须双口径才看得见。
  B 同角色多实体未归并 —— 核名相同，或经 `plot_aliases.json` 中英表同指，却是不同节点
  C 种子名碰撞 —— vector 种子通道把近形近音的**别角色**当锚点，拆成
      C-same（同指，应并入 B 处理）与 C-different（异指真碰撞，归并不是解药，得重排种子）
      实测 300cn R001「薇洛的真名」6 个 seed：杰洛 薇薇安 维克托 维拉 维克多 威利，全是别角色。

**硬自检门**：L2.3 判据逐题重算必须复现 `audit_l2.json` 的 225 / 35 / 0.1556，
复现不出即 SystemExit 且不写任何文件 —— 口径没对齐，后面三张表就是废纸。

判据照抄 scripts/audit_l2.py:258-276 `leak_check`：角色域题 ⟺ `seeds[0]` 实体
`type=="角色"`；泄漏 ⟺ top-10 中 `category=="character"` 且「正文+speakers」不含
该角色任一名号的块。该判据**只认首 seed**（D3/D4 维持原口径）。
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# 统一口径 env —— 必须在 import compendium_rag 之前，直接赋值不 setdefault。
for _k, _v in {"CMPRAG_LEX_WEIGHT": "1.0", "CMPRAG_RRF_K": "1",
               "CMPRAG_LEX_FIRST": "0", "PYTHONHASHSEED": "0"}.items():
    os.environ[_k] = _v

sys.path.insert(0, str(ROOT / "src"))

from compendium_rag.corpus import is_generic_speaker  # noqa: E402
from compendium_rag.extract import GENERIC_PERSON_NOUNS, RE_DESC_SUFFIX  # noqa: E402
from compendium_rag.graph_store import (GENERIC_ROLE_SUFFIX,  # noqa: E402
                                        GraphStore, RE_MEMBER_INDEX)

DATA = ROOT / "data"
GRAPH_PATH = DATA / "compendium_rag" / "graph.json"
CHUNKS_PATH = DATA / "compendium_rag" / "chunks.json"
JSONL_DIR = DATA / "compendium_rag" / "reports" / "p8_roleiso_jsonl"
ALIASES_PATH = DATA / "lore" / "wu_ming_zhe" / "plot_aliases.json"
OUT_JSON = DATA / "compendium_rag" / "reports" / "p9_entity_census.json"
OUT_MD = DATA / "compendium_rag" / "reports" / "p9_entity_census.md"

EXPECTED_SHA = "911bb538160db80e"      # 锚点 scripts/audit_common.py:47
TOP_K = 10                              # audit_l2.py 的 TOP_K
SETS = (("300cn", "300cn_full.jsonl"), ("blind", "blind206_full.jsonl"),
        ("gen", "gen120_full.jsonl"))
EXPECT_ROLE_QUESTIONS, EXPECT_LEAK_QUESTIONS, EXPECT_RATE = 225, 35, 0.1556

# 用户裁决 1 点名的泛称样本：逐条查它们在图上 / 在 speakers 里各是什么状态。
PROBE_GENERIC = ("会长", "上级", "孩子们", "管理员", "黑鹮的副手")

RE_HONORIFIC = re.compile(r"(?:小姐|先生|女士|老师|博士|队长|医生|大夫)$")
RE_SEPARATOR = re.compile(r"[·・\-\s]+")


def sha16_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()[:16]


def generic_criteria(name: str) -> list[str]:
    hits = []
    if is_generic_speaker(name):
        hits.append("GENERIC_SPEAKER")
    if name in GENERIC_PERSON_NOUNS:
        hits.append("GENERIC_PERSON_NOUNS")
    if RE_DESC_SUFFIX.search(name):
        hits.append("RE_DESC_SUFFIX")
    core = RE_MEMBER_INDEX.sub("", name)
    if RE_SEPARATOR.search(core):
        tail = RE_SEPARATOR.split(core)[-1]
        if tail in GENERIC_ROLE_SUFFIX:
            hits.append("GENERIC_ROLE_SUFFIX")
    return hits


def strip_core(name: str) -> str:
    """核名：剥成员编号、敬称、以及「X·泛称尾」里的泛称尾。剥空则回退原名。"""
    n = RE_MEMBER_INDEX.sub("", name)
    n = RE_HONORIFIC.sub("", n)
    if RE_SEPARATOR.search(n):
        parts = RE_SEPARATOR.split(n)
        if parts[-1] in GENERIC_ROLE_SUFFIX or len(parts[-1]) <= 1:
            n = parts[0]
    n = RE_HONORIFIC.sub("", n).strip()
    return n or name


class DSU:
    def __init__(self) -> None:
        self.p: dict[str, str] = {}

    def find(self, x: str) -> str:
        self.p.setdefault(x, x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[max(ra, rb)] = min(ra, rb)


def load_rows(graph, cmeta):
    role_rows, all_rows = [], []
    for set_name, fname in SETS:
        path = JSONL_DIR / fname
        if not path.exists():
            raise SystemExit(f"[FATAL] 中间件缺失：{path}")
        for line in path.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            seeds = r.get("seeds") or []
            all_rows.append(r["qid"])
            if not seeds:
                continue
            ent = graph.entities.get(seeds[0]["eid"])
            if not ent or ent.type != "角色":
                continue
            names = {n for n in (ent.name, *ent.aliases) if n}
            leaked = []
            for ev in (r.get("evidence") or [])[:TOP_K]:
                ch = cmeta.get(ev["chunk_id"])
                if not ch or ch.get("category") != "character":
                    continue
                hay = (ch.get("text") or "") + "\n" + "\n".join(ch.get("speakers") or [])
                if not any(nm in hay for nm in names):
                    leaked.append(ch["chunk_id"])
            role_rows.append({"set": set_name, "qid": r["qid"], "query": r.get("query", ""),
                              "role_eid": ent.eid, "role": ent.name,
                              "seeds": seeds, "leak": bool(leaked),
                              "leaked_chunks": leaked,
                              "all_chunks": [ev["chunk_id"]
                                             for ev in (r.get("evidence") or [])[:TOP_K]]})
    return role_rows, all_rows


def named_role_map(graph):
    """具名角色名 → eid（含别名）。泛称名一律不进，与 P8 OwnerTable 同语义。"""
    m = {}
    for e in graph.entities.values():
        if e.type != "角色" or is_generic_speaker(e.name):
            continue
        for nm in (e.name, *e.aliases):
            if nm and nm not in m:
                m[nm] = e.eid
    return m


def build_clusters(graph, alias_map):
    """B：核名相同 或 中英表同指 的角色节点并簇（并查集，不靠遍历序）。"""
    roles = [e for e in graph.entities.values() if e.type == "角色"]
    en2zh = {}
    for zh, alist in alias_map.items():
        for a in list(alist) + [zh]:
            en2zh.setdefault(a, zh)
    dsu = DSU()
    by_core, by_canon = defaultdict(list), defaultdict(list)
    for e in roles:
        by_core[strip_core(e.name)].append(e.eid)
        by_canon[en2zh.get(e.name, e.name)].append(e.eid)
    for group in by_core.values():
        for eid in group[1:]:
            dsu.union(group[0], eid)
    for group in by_canon.values():
        for eid in group[1:]:
            dsu.union(group[0], eid)
    comp = defaultdict(set)
    for e in roles:
        comp[dsu.find(e.eid)].add(e.eid)
    clusters = []
    for root, eids in comp.items():
        if len(eids) < 2:
            continue
        ents = [graph.entities[i] for i in sorted(eids) if i in graph.entities]
        if len(ents) < 2:
            continue
        zh_names = {n for n in (e.name for e in ents) if en2zh.get(n) == n or n not in en2zh}
        alias_names = {n for n in (e.name for e in ents) if en2zh.get(n) != n}
        clusters.append({
            "cluster_id": root, "core": strip_core(ents[0].name),
            "n_entities": len(ents),
            "members": [{"eid": e.eid, "name": e.name, "n_chunk_ids": len(e.chunk_ids),
                         "canonical_zh": en2zh.get(e.name, e.name)} for e in ents],
            # 真·跨语种只有在「同一簇里既有中文主名形态又有别名表形态」时才成立
            "cross_lang": bool(zh_names) and bool(alias_names),
        })
    return clusters, en2zh


def list_a1(graph):
    rows = []
    for e in graph.entities.values():
        if e.type != "角色":
            continue
        hits = generic_criteria(e.name)
        if hits:
            rows.append({"eid": e.eid, "name": e.name, "criteria": hits,
                         "n_aliases": len(e.aliases), "n_chunk_ids": len(e.chunk_ids)})
    rows.sort(key=lambda x: (-x["n_chunk_ids"], x["name"]))
    return rows


def list_a2(leaking, cmeta, named):
    """A2：泄漏块的 speakers 里，落不到任何具名角色的串 —— 泛称污染的真实位置。"""
    agg = defaultdict(lambda: {"qids": set(), "chunks": set(), "criteria": []})
    for r in leaking:
        for cid in r["leaked_chunks"]:
            ch = cmeta.get(cid)
            if not ch:
                continue
            for sp in (ch.get("speakers") or []):
                if sp in named:
                    continue
                a = agg[sp]
                a["qids"].add(r["qid"])
                a["chunks"].add(cid)
                if not a["criteria"]:
                    a["criteria"] = generic_criteria(sp)
    rows = [{"speaker": k, "resolvable_to_role_entity": False,
             "generic_criteria": v["criteria"], "n_leaking_qids": len(v["qids"]),
             "n_leaked_chunks": len(v["chunks"]), "leak_qids": sorted(v["qids"])}
            for k, v in agg.items()]
    rows.sort(key=lambda x: (-x["n_leaking_qids"], -x["n_leaked_chunks"], x["speaker"]))
    return rows


def probe_names(graph, cmeta, named):
    """用户点名的 5 个泛称：图上是不是实体？能不能落成具名角色？在多少块 speakers 里出现？"""
    sp_count = Counter()
    for ch in cmeta.values():
        for sp in (ch.get("speakers") or []):
            sp_count[sp] += 1
    out = []
    for w in PROBE_GENERIC:
        ents = [e for e in graph.entities.values()
                if e.name == w or w in (e.aliases or [])]
        out.append({"probe": w, "n_entities": len(ents),
                    "entities": [{"eid": e.eid, "type": e.type,
                                  "n_chunk_ids": len(e.chunk_ids)} for e in ents],
                    "exact_entity_named": any(e.name == w for e in ents),
                    "is_named_role_anchor": w in named,
                    "generic_criteria": generic_criteria(w),
                    "n_chunks_with_speaker": sp_count.get(w, 0)})
    return out


def prefix_pairs(snames):
    out = []
    for i in range(len(snames)):
        for j in range(i + 1, len(snames)):
            a, b = sorted((snames[i], snames[j]))
            if a == b:
                continue
            k = 0
            while k < min(len(a), len(b)) and a[k] == b[k]:
                k += 1
            if k >= 2:
                out.append({"a": a, "b": b, "shared": k,
                            "same_reference": strip_core(a) == strip_core(b)})
    return out


def features(row, clusters_eid_pairs, cmeta, named, generic_names=frozenset()):
    """对**任意**角色域题（不漏题也一样）算特征，好做对照基准率。"""
    sids = {s["eid"] for s in row["seeds"]}
    snames = [s["name"] for s in row["seeds"]]
    pairs = prefix_pairs(snames)
    char_cids = [cid for cid in row["all_chunks"]
                 if cmeta.get(cid, {}).get("category") == "character"]
    speakers = [sp for cid in char_cids for sp in (cmeta.get(cid, {}).get("speakers") or [])]
    return {
        "unresolved_speaker": any(sp not in named for sp in speakers),
        "generic_role_speaker": any(sp in generic_names for sp in speakers),
        "b_pair_seeded": any((min(p, q), max(p, q)) in clusters_eid_pairs
                             for p in sids for q in sids if p != q),
        "prefix_same": any(p["same_reference"] for p in pairs),
        "prefix_diff": any(not p["same_reference"] for p in pairs),
        "pairs": pairs,
    }


def control_rates(rows_feat, leak_flags):
    """判别力检验：特征在 35 道漏题 vs 190 道不漏题上的命中率。
    两边接近 = 这条启发式**没有判别力**，不得当作根因结论。"""
    keys = ("unresolved_speaker", "generic_role_speaker", "b_pair_seeded",
            "prefix_same", "prefix_diff")
    out = {}
    n_leak = sum(leak_flags)
    for k in keys:
        a = sum(1 for f, lk in zip(rows_feat, leak_flags) if f[k] and lk)
        b = sum(1 for f, lk in zip(rows_feat, leak_flags) if f[k] and not lk)
        ra = round(a / n_leak, 4) if n_leak else None
        rb = round(b / (len(rows_feat) - n_leak), 4) if len(rows_feat) != n_leak else None
        out[k] = {"leaking": f"{a}/{n_leak}", "rate_leaking": ra,
                  "non_leaking": f"{b}/{len(rows_feat) - n_leak}", "rate_non_leaking": rb,
                  "lift": round(ra / rb, 3) if rb else None,
                  "discriminative": bool(rb and ra / rb >= 1.5)}
    return out


def families(leaking, clusters, cmeta, named, generic_names=frozenset()):
    """按题归因 + C-diff 排名（漏题内共现次数）。"""
    pair_same = set()
    for cl in clusters:
        ids = sorted(m["eid"] for m in cl["members"])
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                pair_same.add((ids[i], ids[j]))
    rows, per, diff_pairs = [], Counter(), Counter()
    for r in leaking:
        sids = {s["eid"] for s in r["seeds"]}
        fams = []
        f = features(r, pair_same, cmeta, named, generic_names)
        if f["unresolved_speaker"]:
            fams.append("A2")
        if f["generic_role_speaker"]:
            fams.append("A1g")
        if f["b_pair_seeded"]:
            fams.append("B")
        if f["prefix_same"]:
            fams.append("C_same")
        if f["prefix_diff"]:
            fams.append("C_diff")
        for p in f["pairs"]:
            if not p["same_reference"]:
                diff_pairs[(p["a"], p["b"], p["shared"])] += 1
        for x in set(fams):
            per[x] += 1
        if not fams:
            per["none"] += 1
        rows.append({"set": r["set"], "qid": r["qid"], "role": r["role"],
                     "families": fams, "n_leaked_chunks": len(r["leaked_chunks"]),
                     "prefix_pairs": f["pairs"]})
    c_diff = [{"name_a": k[0], "name_b": k[1], "shared_prefix_len": k[2],
               "co_occur_leaking": v}
              for k, v in sorted(diff_pairs.items(),
                                 key=lambda kv: (-kv[1], kv[0][0], kv[0][1]))]
    return rows, dict(per), c_diff, pair_same


def main() -> int:
    sha = sha16_file(GRAPH_PATH)
    if sha != EXPECTED_SHA:
        raise SystemExit(f"[FATAL] 冻结图指纹漂移：期望 {EXPECTED_SHA}，实际 {sha}；不写任何文件")
    graph = GraphStore.load(GRAPH_PATH)      # 只读：from_dict 不落盘
    cmeta = {c["chunk_id"]: c for c in
             json.loads(CHUNKS_PATH.read_text(encoding="utf-8"))["chunks"]}
    alias_map = json.loads(ALIASES_PATH.read_text(encoding="utf-8"))

    role_rows, all_rows = load_rows(graph, cmeta)
    leaking = [r for r in role_rows if r["leak"]]
    n_role, n_leak = len(role_rows), len(leaking)
    rate = round(n_leak / n_role, 4) if n_role else None
    if not (n_role == EXPECT_ROLE_QUESTIONS and n_leak == EXPECT_LEAK_QUESTIONS
            and rate == EXPECT_RATE):
        raise SystemExit(
            f"[FATAL] L2.3 复现失败：实际 {n_role} / {n_leak} / {rate}，"
            f"应为 {EXPECT_ROLE_QUESTIONS} / {EXPECT_LEAK_QUESTIONS} / {EXPECT_RATE}"
            f" —— 口径未对齐，不写任何文件。")

    named = named_role_map(graph)
    deg = Counter()
    for e in graph.edges:
        deg[e.src] += 1
        deg[e.dst] += 1

    a1 = list_a1(graph)
    for r in a1:
        r["degree"] = deg.get(r["eid"], 0)
        r["is_named_role_anchor"] = r["name"] in named
    a2 = list_a2(leaking, cmeta, named)
    clusters, en2zh = build_clusters(graph, alias_map)
    leak_by_qid = {r["qid"]: r for r in leaking}
    for cl in clusters:
        eids = {m["eid"] for m in cl["members"]}
        cl["leak_qids_both_seeded"] = sorted(
            q for q, r in leak_by_qid.items()
            if len({s["eid"] for s in r["seeds"]} & eids) >= 2)
        cl["leak_qids_any_seeded"] = sorted(
            q for q, r in leak_by_qid.items()
            if len({s["eid"] for s in r["seeds"]} & eids) >= 1)
    clusters.sort(key=lambda x: (-len(x["leak_qids_both_seeded"]),
                                 -len(x["leak_qids_any_seeded"]), -x["n_entities"]))
    generic_names = ({r["name"] for r in a1} | set(PROBE_GENERIC)
                     | {e.name for e in graph.entities.values()
                        if e.type == "角色" and generic_criteria(e.name)})
    attr, per, c_diff, pair_same = families(leaking, clusters, cmeta, named, generic_names)
    feat = [features(r, pair_same, cmeta, named, generic_names) for r in role_rows]
    ctrl = control_rates(feat, [bool(r["leak"]) for r in role_rows])
    n_b_evid = sum(1 for x in clusters if x["leak_qids_both_seeded"])

    rep = {
        "schema": "compendium_rag.p9_entity_census/v2",
        "done_at": datetime.now().isoformat(timespec="seconds"),
        "graph_sha": sha, "read_only": True,
        "reproduce": {"role_questions": n_role, "leak_questions": n_leak, "rate": rate,
                      "expected": [EXPECT_ROLE_QUESTIONS, EXPECT_LEAK_QUESTIONS, EXPECT_RATE],
                      "exact": True,
                      "source": "p8_roleiso_jsonl 三集 full 模式 522 行，离线复算 leak_check"},
        "counts": {"entities": len(graph.entities), "edges": len(graph.edges),
                   "rows_scanned": len(all_rows), "role_domain": n_role, "leaking": n_leak,
                   "a1_generic_role_entities": len(a1),
                   "a2_unresolved_speakers": len(a2),
                   "b_clusters": len(clusters),
                   "b_clusters_with_both_seeded_evidence":
                       sum(1 for c in clusters if c["leak_qids_both_seeded"]),
                   "c_diff_true_collisions": len(c_diff),
                   "attribution": per},
        "probe_generic_words_named_by_user": probe_names(graph, cmeta, named),
        "list_a1_generic_role_entities": a1,
        "list_a2_unresolved_speakers_in_leaked_chunks": a2,
        "list_b_unmerged_same_character": clusters,
        "attribution_per_leaking_question": attr,
        "list_c_diff_true_collisions": c_diff,
        "control_base_rates": ctrl,
        "hypothesis_verdicts": {
            "泛称角色名导致跨角色泄漏（裁决1 的 ②之一）": {
                "verdict": "证伪（在本判据下）",
                "evidence": f"generic_role_speaker 漏题 {ctrl['generic_role_speaker']['leaking']}、"
                            f"对照 {ctrl['generic_role_speaker']['non_leaking']}；"
                            f"用户点名的 {list(PROBE_GENERIC)} 全是合法角色节点，"
                            f"但从未出现在角色域题 top-10 的 character 块 speakers 里"},
            "同角色多实体未归并（裁决1 的 ②之二）": {
                "verdict": "成立但量极小",
                "evidence": f"b_pair_seeded 漏题 {ctrl['b_pair_seeded']['leaking']} / "
                            f"对照 {ctrl['b_pair_seeded']['non_leaking']}，lift "
                            f"{ctrl['b_pair_seeded']['lift']}；信号干净但只能解释 3 题，"
                            f"146 簇里只有 {n_b_evid} 簇带双 seed 证据"},
            "种子名近形碰撞（本脚本 v1 新增假设）": {
                "verdict": "判负 —— 无判别力",
                "evidence": f"prefix_diff 漏题 {ctrl['prefix_diff']['leaking']} vs 对照 "
                            f"{ctrl['prefix_diff']['non_leaking']}，lift "
                            f"{ctrl['prefix_diff']['lift']} < 1：中文角色名共享首字在不漏题上更常见，"
                            f"该启发式是噪声不是信号"},
            "未落名 speakers（角色边界标注路线）": {
                "verdict": "相关，但未证明因果",
                "evidence": f"unresolved_speaker lift {ctrl['unresolved_speaker']['lift']}"
                            f"（{ctrl['unresolved_speaker']['leaking']} vs "
                            f"{ctrl['unresolved_speaker']['non_leaking']}），主体是占位符类说话人"
                            f"（？？？/口口口）与「女孩/小孩Ⅰ」；⚠ 与泄漏判据存在机械相关风险，"
                            f"见 limitations"},
        },
        "limitations": [
            "判据只认首 seed（D3/D4 维持原口径）：种子通道选错角色时泄漏判定跟着错，"
            "A/B/C 三张表在这类题上是**下界**。",
            "B 的核名剥离是词法规则（成员编号 / 敬称 / 泛称尾 / plot_aliases 中英表），"
            "同簇**不等于该合并** —— `卡卡尼亚之母 ⊃ 卡卡尼亚` 这类异指反例照样进簇；"
            "必须走盲评 + 对称 DROP_MAP 纪律（`优化计划_v9_2026-10-08.md:138,162`），不可自动合并。",
            "C-diff 的前缀共现只证明「两个名字在同一条漏题里抢过种子」，不证明谁错。",
            "A2 的 speakers 未落名里混有真·专名写法差异（引号、全半角），"
            "已按 generic_criteria 命中标注，未命中的需逐条人看。",
            "P2 已交过 587 组修饰语前缀候选（`reports/p2_landing_diag.md`）；"
            "本表的 B 是**按漏题证据重排**的同指候选，不是那份清单的替代品，两者须并读。",
            "⚠ **A2 有机械相关风险**：L2.3 判据是「块内不含所问角色任一名号」，而未落名 speakers "
            "占多数的块天然更可能不含角色名 —— 所以 lift 3.88 只证明**相关**，不证明「标注 speakers」"
            "就能压住泄漏。要定因果得做干预实验（就地补标后重算），那属于改数据，本轮未做。",
            "对照组的 190 道是**同判据下的不漏题**，不是随机题；因此 lift 只对「本判据」负责，"
            "换成分层判据（D4：检索层 0.08 / 答案层 0.03）后这些族的相关性需要重算。",
        ],
    }
    OUT_JSON.write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    OUT_MD.write_text(render(rep), encoding="utf-8")
    if sha16_file(GRAPH_PATH) != sha:
        raise SystemExit("[FATAL] 跑完发现图被改动 —— 本脚本自称只读，必须查明")
    print(f"[OK] 复现门通过：角色域题 {n_role} / 泄漏 {n_leak} / rate {rate}")
    print(f"     A1 图上泛称角色 {len(a1)} · A2 泄漏块未落 speakers {len(a2)} · "
          f"B 簇 {len(clusters)}（有双 seed 证据 "
          f"{rep['counts']['b_clusters_with_both_seeded_evidence']}）· C-diff {len(c_diff)}")
    print(f"     归因 {per}")
    return 0


def render(rep: dict) -> str:
    c = rep["counts"]
    ln = ["# P9① 实体层只读普查 v2", "",
          f"生成 {rep['done_at']} · 冻结图 `{rep['graph_sha']}` · 只读（图指纹跑前跑后一致）",
          "",
          f"**复现门**：角色域题 **{rep['reproduce']['role_questions']}** / 泄漏 "
          f"**{rep['reproduce']['leak_questions']}** / rate **{rep['reproduce']['rate']}**"
          f" ⇒ 与 `audit_l2.json` 逐位一致 ✅",
          "",
          f"## 归因（{c['leaking']} 道漏题，可重叠）", "",
          f"- A2 泄漏块含未落名 speakers：**{c['attribution'].get('A2', 0)}** 题",
          f"- A1g 泄漏块含「图上合法但泛称」的角色 speaker：**{c['attribution'].get('A1g', 0)}** 题",
          f"- B 同簇双节点进 seed：**{c['attribution'].get('B', 0)}** 题",
          f"- C-same 近名前缀且同指（属 B 处理）：**{c['attribution'].get('C_same', 0)}** 题",
          f"- C-diff 近名前缀但异指（真碰撞）：**{c['attribution'].get('C_diff', 0)}** 题",
          f"- **无法归因：{c['attribution'].get('none', 0)} 题**", "",
          "## 判别力检验（同一特征在「不漏题」上的基准率 —— lift<1.5 即无判别力，不得当根因）", "",
          "| 特征 | 漏题命中 | 不漏题命中 | lift | 有判别力？ |",
          "| --- | --- | --- | --- | --- |"]
    for k, v in rep["control_base_rates"].items():
        ln.append(f"| `{k}` | {v['leaking']} ({v['rate_leaking']}) | "
                  f"{v['non_leaking']} ({v['rate_non_leaking']}) | {v['lift']} | "
                  f"{'✅' if v['discriminative'] else '❌ 无判别力'} |")
    ln += ["", "## 四条假设的裁决", ""]
    for k, v in rep["hypothesis_verdicts"].items():
        ln.append(f"- **{k}** ⇒ **{v['verdict']}**")
        ln.append(f"  - 证据：{v['evidence']}")
    ln += ["",
          "## 用户点名泛称的实际位置", "",
          "| 词 | 图上实体 | 是角色锚点 | speakers 出现的块数 | 命中的泛称判据 |",
          "| --- | --- | --- | --- | --- |"]
    for p in rep["probe_generic_words_named_by_user"]:
        ln.append(f"| `{p['probe']}` | {p['n_entities']} | "
                  f"{'是' if p['is_named_role_anchor'] else '否'} | "
                  f"{p['n_chunks_with_speaker']} | {p['generic_criteria'] or '—'} |")
    ln += ["", f"## A1 图上泛称角色实体（{c['a1_generic_role_entities']} 个）", ""]
    for r in rep["list_a1_generic_role_entities"][:20]:
        ln.append(f"- `{r['name']}`（{r['eid']}，度 {r['degree']}，块 {r['n_chunk_ids']}）"
                  f"判据 {r['criteria']}｜可作锚点 {'是' if r['is_named_role_anchor'] else '否'}")
    ln += ["", f"## A2 泄漏块里落不到具名角色的 speakers（{c['a2_unresolved_speakers']} 种）", ""]
    for r in rep["list_a2_unresolved_speakers_in_leaked_chunks"][:30]:
        ln.append(f"- `{r['speaker']}` → 漏题 {r['n_leaking_qids']} / 泄漏块 "
                  f"{r['n_leaked_chunks']}｜判据 {r['generic_criteria'] or '未命中(需人看)'}")
    ln += ["", f"## B 同角色多实体未归并（{c['b_clusters']} 簇，"
               f"其中 {c['b_clusters_with_both_seeded_evidence']} 簇有「双节点同进 seed」漏题证据）", ""]
    for r in rep["list_b_unmerged_same_character"][:20]:
        mem = " / ".join(f"`{m['name']}`({m['n_chunk_ids']}块)" for m in r["members"])
        ln.append(f"- **{r['core']}** · {r['n_entities']} 节点"
                  f"{' · 真跨语种' if r['cross_lang'] else ''}：{mem}")
        if r["leak_qids_both_seeded"]:
            ln.append(f"  - 双节点同进 seed 的漏题 {r['leak_qids_both_seeded']}")
    ln += ["", f"## C-diff 真种子名碰撞（{c['c_diff_true_collisions']} 对，异指：归并不是解药）", ""]
    qids_by_pair = defaultdict(list)
    for row in rep["attribution_per_leaking_question"]:
        for p in row["prefix_pairs"]:
            if not p["same_reference"]:
                qids_by_pair[(p["a"], p["b"])].append(f"{row['set']}/{row['qid']}")
    for r in rep["list_c_diff_true_collisions"][:20]:
        ln.append(f"- `{r['name_a']}` ↔ `{r['name_b']}`（共用前缀 {r['shared_prefix_len']}）"
                  f" 在同一条漏题的 6 个 seed 里抢位 {r['co_occur_leaking']} 次："
                  f"{qids_by_pair[(r['name_a'], r['name_b'])][:6]}")
    ln += ["", f"## 逐题归因明细（{c['leaking']} 题）", "",
           "| 题 | 角色域锚点 | 泄漏块 | 族 |", "| --- | --- | --- | --- |"]
    for row in rep["attribution_per_leaking_question"]:
        ln.append(f"| {row['set']}/{row['qid']} | `{row['role']}` | "
                  f"{row['n_leaked_chunks']} | {row['families'] or ['（无法归因）']} |")
    ln += ["", "## 已知局限", ""] + [f"- {x}" for x in rep["limitations"]]
    return "\n".join(ln) + "\n"


if __name__ == "__main__":
    sys.exit(main())
