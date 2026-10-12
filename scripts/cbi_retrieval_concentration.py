# -*- coding: utf-8 -*-
"""检索那一格的**集中度**：那 12/19/81 条命中是散在 500 条上，还是集中在少数块与少数对上？

为什么要算这个：`N_retrieval` 已被裁决降级成能力读数，但"4.2%"这种比率会把形态信息抹平 ——
12 条散在 12 个块上（通用排序问题）与 12 条来自 3 个块（个别块的可检索性问题）
是两件完全不同的事，修法也完全不同。按 §「修数据不是调指标」的纪律，
先量出形态、把可下手的对象列出来，而不是先想怎么把比率压下去。

口径纪律（三处，全部会打印）：
  1) 命中一律**按 `top_ids` 现复算**（金标 = 该样本 `retrieval_gold.b_private_chunk`），
     不直接采信通道的 `b_private_chunk_hit`；两者不一致就报出来并终止 ——
     这张表若与读数产物的 `exposure.n_gold_in_top6` 不同数，它就是第二份会说谎的抄件。
  2) 对、题型、冲突族都从**测试集**取（v1 通道行里也有 pair 字段，但 v2 通道没有，
     以测试集为唯一权威才不会两个仪器两种算法）。
  3) "块属于哪一对"用**测试集里的金标归属**定义（同一块可以是一对 B 的私密块，
     又被别对的题面捞起来 ⇒ 那正是"跨对污染"，下面单独计数）。

只读。产物：`reports/cbi/retrieval_concentration.{json,md}`。
用法：`PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe scripts/cbi_retrieval_concentration.py`
"""
from __future__ import annotations

import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(errors="replace")

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "data" / "compendium_rag" / "reports"
CBI = R / "cbi"

# (标签, 测试集, 检索通道, 用来对数的读数产物, 读数里的口径名)
CASES = [
    ("v1 × 控制", "cbi_testset_500_control.json", "retrieval_cc.jsonl",
     "cbi_result_full.json", "control"),
    ("v1 × 字面", "cbi_testset_500.json", "retrieval.jsonl",
     "cbi_result_full.json", "literal"),
    ("v2 × 控制", "cbi_testset_500_v2_control.json", "retrieval_v2_cc.jsonl",
     "cbi_result_v2instrument.json", "control"),
]
OUT_JSON = CBI / "retrieval_concentration.json"
OUT_MD = CBI / "retrieval_concentration.md"
GRAPH = ROOT / "data" / "compendium_rag" / "graph.json"
DOC = ROOT / "docs" / "compendium-rag" / "P9_CBI报告.md"


def chunk_owners(needed: set) -> dict:
    """块 → 图上声明它的实体列表（只读扫一遍图）。

    这一列存在的理由：如果命中的块都是"一块一主"，那检索格就是排序问题；
    如果它们全是多主块（一块里同时写着好几个角色的台词），那检索格继承的是语料结构，
    R2 的 owner/visibility 过滤判负也不是偶然。别把这句话写成推论，写成可数的东西。
    """
    if not GRAPH.exists():
        return {}
    out = defaultdict(list)
    g = j(GRAPH)
    for e in g.get("entities") or []:
        for c in e.get("chunk_ids") or []:
            if c in needed:
                out[c].append([e.get("name"), e.get("type")])
    return dict(out)


def j(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def jsonl(p: Path) -> dict:
    out = {}
    for ln in p.read_text(encoding="utf-8").splitlines():
        if ln.strip():
            r = json.loads(ln)
            out[r["sample_id"]] = r
    return out


def analyse(label: str, ts_name: str, retr_name: str, read_name: str, cal: str,
            problems: list) -> dict | None:
    ts, retr = j(R / ts_name), jsonl(CBI / retr_name)
    samples = {s["sample_id"]: s for s in ts["samples"]}
    rows = {k: v for k, v in retr.items() if k in samples}
    if not rows:
        problems.append(f"{label}：通道 {retr_name} 与测试集无可对齐行")
        return None
    hits = []
    flag_mismatch = 0
    for sid, r in sorted(rows.items()):
        g = (samples[sid].get("retrieval_gold") or {}).get("b_private_chunk")
        tp = r.get("top_ids") or []
        hit = bool(g) and g in tp
        if hit != bool(r.get("b_private_chunk_hit")):
            flag_mismatch += 1
        if hit:
            pk = f"{samples[sid]['pair'].get('a_name')}→{samples[sid]['pair'].get('b_name')}"
            hits.append({"sample_id": sid, "chunk": g, "rank": tp.index(g) + 1,
                         "pair_key": pk,
                         "pair": samples[sid]["pair"].get("b_name")
                                 or samples[sid]["pair"].get("b_eid"),
                         "a": samples[sid]["pair"].get("a_name"),
                         "query_type": samples[sid]["query_type"],
                         "conflict_type": samples[sid].get("conflict_type")})
    if flag_mismatch:
        problems.append(f"{label}：{flag_mismatch} 行通道标记与 top_ids 复算不一致")

    # 与读数产物对数（不同数就终止，不把矛盾写进表）
    exp = None
    if (R / read_name).exists():
        blk = j(R / read_name)["both_calibers"].get(cal) or {}
        exp = blk.get("exposure")
        if exp and exp.get("n_gold_in_top6") != len(hits):
            problems.append(f"{label}：本表 {len(hits)} 条 vs 读数 exposure.n_gold_in_top6 "
                            f"{exp['n_gold_in_top6']} —— 不同数，不出表")
            return None

    by_chunk = defaultdict(list)
    for h in hits:
        by_chunk[h["chunk"]].append(h)
    # 金标归属：一块在**本套题**里是哪几对（a→b）的私密块。
    # 注意这里刻意**不**报"命中是否来自非归属对"那种格子：命中本来就是按该样本自己的
    # `b_private_chunk` 判的，所以那一列会被构造恒为 0（同源自证，量具自守规则第 3 条）。
    # 可证伪的版本在下面：命中的那块在**图上**是否真的挂在 B 名下 —— 数据源不同（图 vs 测试集）。
    owner = defaultdict(set)
    for sid, s in samples.items():
        g = (s.get("retrieval_gold") or {}).get("b_private_chunk")
        if g:
            owner[g].add(f"{s['pair'].get('a_name')}→{s['pair'].get('b_name')}")
    pair_c = Counter(h["pair_key"] for h in hits)
    top = sorted(by_chunk.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    n = len(hits) or 1
    # **块复用度**：一块在本套题里被当作 `b_private_chunk` 挂了多少个题位上。
    # 不报这个数，"12 条集中在 7 块"就没有可比性 —— 如果某块本来就挂着 40 个题位，
    # 它出现 4 次命中并不奇怪。lift 才是"这块特别容易被捞"的证据。
    slots = Counter()
    for s in samples.values():
        g = (s.get("retrieval_gold") or {}).get("b_private_chunk")
        if g:
            slots[g] += 1
    base = len(hits) / max(1, sum(slots.values()))
    owners = chunk_owners(set(by_chunk))
    if not owners and hits:
        problems.append(f"{label}：图上取不到任何块的声明者（图缺失或 chunk_ids 变了形）"
                        "⇒ 『B 是否真挂在这块上』无从可算，不出表")
        return None
    # 可证伪的那一列：命中的块在**图上**是否真挂在 B 名下（两个独立数据源：测试集金标 vs 图）。
    unclaimed = [h for h in hits
                 if h["pair"] not in {n for n, _t in owners.get(h["chunk"], [])}]
    lift = [{"chunk": c, "n_hits": len(v), "n_slots": slots.get(c, 0),
             "n_entities_claiming": len(owners.get(c, [])),
             "claimants": [f"{n}({t})" for n, t in owners.get(c, [])][:12],
             "hit_rate": round(len(v) / slots[c], 4) if slots.get(c) else None,
             "lift_vs_base": round((len(v) / slots[c]) / base, 2) if slots.get(c) else None}
            for c, v in top if slots.get(c)]
    multi = [x for x in lift if x["n_entities_claiming"] > 1]
    return {
        "label": label, "testset": ts_name, "channel": retr_name,
        "reading": read_name, "caliber": cal,
        "n_rows_aligned": len(rows), "n_strict_hits": len(hits),
        "flag_mismatch_with_channel": flag_mismatch,
        "matches_reading_exposure": bool(exp),
        "n_distinct_chunks": len(by_chunk),
        "n_distinct_pairs": len(pair_c),
        "n_distinct_chunks_in_testset": len(slots),
        "max_slots_per_chunk": max(slots.values()) if slots else 0,
        "base_hit_rate": round(base, 4),
        "hit_chunks_claimed_by_multiple_entities": len(multi),
        "hits_where_b_not_a_graph_claimant": len(unclaimed),
        "chunk_lift": lift,
        "top_chunk_share": round(len(top[0][1]) / n, 4) if top else None,
        "top3_chunks_share": round(sum(len(v) for _, v in top[:3]) / n, 4),
        "top_pair_share": round(max(pair_c.values()) / n, 4) if pair_c else None,
        "hits_where_b_not_a_graph_claimant": len(unclaimed),
        "by_query_type": dict(Counter(h["query_type"] for h in hits).most_common()),
        "by_conflict_type": dict(Counter(h["conflict_type"] for h in hits).most_common()),
        "rank_hist": {str(k): v for k, v in sorted(
            Counter(h["rank"] for h in hits).items())},
        "chunks": [{"chunk": c, "n_hits": len(v),
                    "owner_pairs": sorted(owner.get(c, set())),
                    "hit_by_pairs": sorted({h["pair_key"] for h in v}),
                    "ranks": sorted(h["rank"] for h in v),
                    "query_types": sorted({h["query_type"] for h in v}),
                    "samples": [h["sample_id"] for h in v]}
                   for c, v in top],
        "pairs": [{"pair": p, "n_hits": n} for p, n in pair_c.most_common()],
    }


def md(res: list) -> str:
    L = ["# 检索那一格的集中度（只读实算，10-12）", "",
         "命中一律按 `top_ids` 现复算，并与读数产物的 `exposure.n_gold_in_top6` 对过数；",
         "理由：**比率会把形态抹平** —— 12 散在 12 个块上（通用排序问题）与",
         "12 来自 3 个块（个别块谁问都被捞起来）是两件事，修法也不同。", ""]
    L += ["| 读数 | 对齐行 | 严格命中 | 命中落在几块 | 其中图上多主的块 | 测试集里共几块 | 单块最多挂几个题位 | 基线命中率 | 头号块占比 | 前 3 块占比 | 头号对占比 | 图上不挂 B 名 |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for x in res:
        L.append(f"| {x['label']} | {x['n_rows_aligned']} | {x['n_strict_hits']} | "
                 f"{x['n_distinct_chunks']} | {x['hit_chunks_claimed_by_multiple_entities']} | "
                 f"{x['n_distinct_chunks_in_testset']} | "
                 f"{x['max_slots_per_chunk']} | {x['base_hit_rate']:.1%} | "
                 f"{x['top_chunk_share']:.1%} | {x['top3_chunks_share']:.1%} | "
                 f"{x['top_pair_share']:.1%} | {x['hits_where_b_not_a_graph_claimant']} |")
    tot = sum(x["hits_where_b_not_a_graph_claimant"] for x in res)
    L += ["", f"『图上不挂 B 名』= 命中了 B 的私密块，但在**图上**声明这块的实体名单里没有 B —— "
          f"两个独立数据源（测试集的 `retrieval_gold` vs 图里 `entities[].chunk_ids`）交叉核对，"
          f"本次实测合计 **{tot}** 条。"
          + ("也就是说：严格口径抓到的每一条，那块在图上确实挂在 B 名下，"
             "失效模式不是『金标指错了块』，而是**这块本来就是多主共享的舞台**（见下表中『图上几个实体声明它』）。"
             if tot == 0 else
             "也就是说：存在金标指向与图上归属不一致的命中，那属于测试集侧的缺陷，要先修指认再谈边界。") + ""]
    for x in res:
        L += ["", f"## {x['label']}：按块（命中数降序；lift = 该块命中率 ÷ 本读数基线 "
              f"{x['base_hit_rate']:.1%}）", "",
              "| 金标块 | 命中 | 挂着几个题位 | 命中率 | lift | 图上几个实体声明它 | "
              "这块是哪几对的私密块 | 被哪些对捞到 | 名次 | 题型 |",
              "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        lift_by = {c["chunk"]: c for c in x["chunk_lift"]}
        for c in x["chunks"][:12]:
            lf = lift_by.get(c["chunk"], {})
            L.append(f"| `{c['chunk']}` | {c['n_hits']} | {lf.get('n_slots', '—')} | "
                     f"{lf.get('hit_rate', '—')} | {lf.get('lift_vs_base', '—')} | "
                     f"{lf.get('n_entities_claiming', '—')} | "
                     f"{', '.join(c['owner_pairs']) or '—'} | "
                     f"{', '.join(c['hit_by_pairs'])} | {c['ranks']} | "
                     f"{', '.join(c['query_types'])} |")
        L += ["", f"题型分布 {x['by_query_type']}｜冲突族分布 {x['by_conflict_type']}"
              f"｜名次分布 {x['rank_hist']}"
              f"｜通道标记与复算不一致 {x['flag_mismatch_with_channel']} 行"
              f"｜命中块里图上多主的 {x['hit_chunks_claimed_by_multiple_entities']}"
              f"/{x['n_distinct_chunks']}"]
    L += ["", "> **读法与限制**：若头号块/头号对占比高，说明这一格不是"
          "『排序系统性偏向 B』，而是**少数块反复被捞**（或某一对的题面反复触到同一块）。"
          "『图上几个实体声明它』这一列给的是**语料侧**的形态：一块同时被多个实体声明时，"
          "它天然会替别人把话讲出来（这与消歧规则表 §8 量到的 96.2% 多主是同一条），"
          "也正是 R2 的 owner/visibility 过滤判负的原因。"
          "本表不给修法、不改任何阈值、不与 `MRR>=0.39` 做任何比较。",
          "> **有一格为什么被删掉**：原先这里叫『跨对命中』（命中的块不是这一对的私密块）。"
          "写出来才发现它按构造恒为 0 —— 命中本身就是按该样本自己的 `b_private_chunk` 判的，"
          "拿同一份数据跟自己比不叫检查（量具自守规则第 3 条：不许有同源自证）。"
          "现在这一列换成拿**第二个数据源**（图 `entities[].chunk_ids`）来核对金标指认，"
          "它才有变红的资格；『这块是哪几对的私密块』两列仍按本套题的金标归属记，"
          "那是**测试集侧**的定义，不等于图上存在任何可见性边（那正是 R2 判负的东西）。"]
    return "\n".join(L) + "\n"


def doc_check(res: list) -> list:
    """报告 §2.14 那张表是正文里的数字，按 §5-28 的纪律它必须有资格变红：
    逐格回到本脚本刚算出的 `res` 比一遍（同一个脚本既是产出者也是核对者，
    免得再抄一份判据到第二个文件里各自过期）。"""
    bad: list[str] = []
    if not DOC.exists():
        return [f"报告文件不存在（{DOC.name}），§2.14 的表无从核对"]
    txt = DOC.read_text(encoding="utf-8")
    sec = txt.split("### 2.14", 1)[-1].split("\n## ", 1)[0]
    first_chunk = res[0]["chunk_lift"][0]["chunk"] if res else ""
    for idx, x in enumerate(res):
        if idx == 0 and any(ln.startswith("|") and x["label"] in ln and "同一块" in ln
                            for ln in sec.splitlines()):
            bad.append("§2.14 第一行就写『同一块』—— 没有先行对象，这个指代是无定义的")
        line = next((ln for ln in sec.splitlines()
                     if ln.startswith("|") and x["label"] in ln), "")
        if not line:
            bad.append(f"§2.14 找不到 {x['label']} 那一行")
            continue
        c = [s.strip().replace("*", "").replace("`", "") for s in line.strip("|").split("|")]
        lifts = x["chunk_lift"]
        trio = (min(y["n_entities_claiming"] for y in lifts),
                round(statistics.mean(y["n_entities_claiming"] for y in lifts), 2),
                max(y["n_entities_claiming"] for y in lifts))
        head = lifts[0]
        # 正文允许写"同一块"（三套读数的头号块确实相同），但那是一条**可证伪的断言**：
        # 只有当本行头号块与第一行完全相同、且括号里的次数/占比与现算一致时才许这么写。
        if c[4].startswith("同一块"):
            nums = f"（{head['n_hits']} 次，{x['top_chunk_share'] * 100:.1f}%）"
            if head["chunk"] != first_chunk or nums not in c[4]:
                bad.append(f"§2.14 {x['label']} 写了『同一块』但现算头号块是 "
                           f"{head['chunk']}（第一行是 {first_chunk}），或数字与 {nums} 不符")
            head_cell = c[4]
        else:
            head_cell = f"{head['chunk']}（{head['n_hits']} 次，{x['top_chunk_share'] * 100:.1f}%）"
        want = [str(x["n_strict_hits"]), str(x["n_distinct_chunks"]), str(x["n_distinct_pairs"]),
                head_cell,
                f"{head['lift_vs_base']}×",
                f"{x['hit_chunks_claimed_by_multiple_entities']}/{x['n_distinct_chunks']}",
                f"{trio[0]} / {trio[1]} / {trio[2]}"]
        got = c[1:]
        print(f"[§2.14 核对] {x['label']}：正文 {len(got)} 格 vs 现算 {len(want)} 格"
              f" ⇒ {'一致' if got == want else '不一致'}")
        for i, (g, w) in enumerate(zip(got, want)):
            if g != w:
                bad.append(f"§2.14 {x['label']} 第 {i + 1} 格正文={g!r} 现算={w!r}")
        if len(got) != len(want):
            bad.append(f"§2.14 {x['label']} 行数对不上：正文 {len(got)} 格 / 现算 {len(want)} 格")
    return bad


def main() -> int:
    problems: list = []
    res = []
    if not GRAPH.exists():
        # 图读不到时 `n_entities_claiming` 会全变成 0，而 0 看起来像"这些块都是单主的"——
        # 与"没测"混成一谈，正是 MRR 那一格踩过的坑，所以这里直接拒绝出表。
        print(f"[FAIL] 图文件不存在：{GRAPH} ⇒ 『图上几个实体声明它』一列无从可算，不出表")
        return 1
    for case in CASES:
        x = analyse(*case, problems)
        if x:
            res.append(x)
            print(f"[{x['label']}] 严格命中 {x['n_strict_hits']} 条落在 "
                  f"{x['n_distinct_chunks']} 个块 / {x['n_distinct_pairs']} 个对上；"
                  f"头号块 {x['top_chunk_share']:.1%}，前 3 块 {x['top3_chunks_share']:.1%}，"
                  f"图上不挂 B 名的命中 {x['hits_where_b_not_a_graph_claimant']} 条")
    if problems:
        print("\n[FAIL] " + "\n[FAIL] ".join(problems))
        return 1
    OUT_JSON.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    OUT_MD.write_text(md(res), encoding="utf-8")
    print(f"\n[OK] 写出 {OUT_JSON.name} / {OUT_MD.name}（{len(res)} 个读数）")
    bad = doc_check(res)
    if bad:
        print("[FAIL] 报告 §2.14 的表与本脚本现算不一致：")
        for b in bad:
            print("   !! " + b)
        return 1
    print("[OK] 报告 §2.14 的每个数都回到本脚本的现算值")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
