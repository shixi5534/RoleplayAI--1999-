"""P10·R2 影子模拟（**只读**）：owner/visibility 过滤真能挡掉几条检索泄漏，代价多大。

为什么要先跑这一版：验收卡在一处 —— `N_retrieval = 21 > 15`，而唯一有语义的修法
（给私密块打归属/可见性边）是**写图**，需要批准。批准前该给的不是"要不要试"，
而是"试了大概挡掉几条、误伤几条"。P3 已经栽过一次：owners 尺子把 17–30% 的**转述**
gold 也算成跨域（project-p3-rolefilter-shadow-verdict），所以过滤必须先在影子里量误伤。

本脚本用的归属判据是**名形式代理**（拿测试集自带的 `a_name_forms` / `b_name_forms`
在块的 `speakers_text + text` 里找），**不是**图上的 owner 边 —— 图现在没有那种边。
所以结论是"名字可归属性"的代理：代理说挡不住的，写图后靠边标注也许挡得住；
代理说挡得住的，真边标注一定也挡得住。转述场景（A 的事由别人说出）会被代理**高估误伤**。

**跑出来的第一条结论是否定性的**：`N_retrieval` 这一格在本量具上不可证伪 ——
测试集的选对阶段就要求双向独占块（`compendium_rag_p9_cbi_testset.py:165`），
金标块按构造就是"含 B 名、不含 A 名"，于是任何挡住它的过滤器都能把读数做到 0。
所以这份影子只报**上下文代价**（两种过滤的丢槽率与饥饿行数），
不报"R2 能降到几条"，也不该被拿去当写图批准的依据。

复现门：泄漏数必须等于计算器报的 21，不等就 [FATAL] 退出、不写任何文件
（同一把尺子两处读数不一致时，先修量具再谈结论）。
只写 `reports/cbi/owner_shadow.{json,md}`，不碰图、不碰缓存。
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "data" / "compendium_rag" / "reports"
CBI = REPORTS / "cbi"
TESTSET = REPORTS / "cbi_testset_500_control.json"
RETRIEVAL = CBI / "retrieval_cc.jsonl"
CHUNKS = ROOT / "data" / "compendium_rag" / "chunks.json"
OUT_JSON = CBI / "owner_shadow.json"
OUT_MD = CBI / "owner_shadow.md"

EXPECT_LEAKS = 21          # cbi_calculator 的 control 口径读数
TOP = 6                    # 检索通道取的就是 top-6
STARVED = 2                # 过滤后只剩这么少块，就算上下文饥饿


def hit(forms, hay):
    return any(f and f in hay for f in forms or [])


def main() -> int:
    ts = json.loads(TESTSET.read_text(encoding="utf-8"))
    if ts.get("caliber") != "control":
        raise SystemExit("[FATAL] 测试集不是 control 口径")
    samples = {s["sample_id"]: s for s in ts["samples"]}
    retr = {}
    for line in RETRIEVAL.read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        retr[r["sample_id"]] = r
    if len(retr) != len(samples):
        raise SystemExit(f"[FATAL] 检索通道 {len(retr)} 行 != 测试集 {len(samples)} 条")
    chunks = {c["chunk_id"]: c for c in
              json.loads(CHUNKS.read_text(encoding="utf-8"))["chunks"]}

    leaks = [sid for sid in samples if retr[sid].get("retrieval_leak")]
    if len(leaks) != EXPECT_LEAKS:
        raise SystemExit(f"[FATAL] 泄漏复现失败：影子 {len(leaks)} != 计算器 {EXPECT_LEAKS}，不写文件")

    # 每个 (块, 该样本的 A/B 名形式) 的归属判一次就缓存，别在 500×6 上重复扫正文
    cache = {}

    def attribute(cid, a_forms, b_forms):
        key = (cid, tuple(a_forms), tuple(b_forms))
        if key not in cache:
            c = chunks.get(cid)
            if c is None:
                cache[key] = (False, False, "missing")
            else:
                hay = (c.get("speakers_text") or "") + "\n" + (c.get("text") or "")
                cache[key] = (hit(a_forms, hay), hit(b_forms, hay), c.get("category"))
        return cache[key]

    # 逐行：泄漏条的"可挡性"，与全部 3000 个槽位的两种过滤变体代价
    leak_rows, slots_total, drop_v1, drop_v2, kept_by_row = [], 0, 0, 0, []
    unattributed = 0
    by_type = Counter()
    for sid, s in samples.items():
        g = s["retrieval_gold"]
        a_forms, b_forms = g["a_name_forms"], g["b_name_forms"]
        top = retr[sid]["top_ids"][:TOP]
        flags = []
        for cid in top:
            ha, hb, cat = attribute(cid, a_forms, b_forms)
            slots_total += 1
            if cat == "missing":
                unattributed += 1
            v1 = (hb and not ha)             # 黑名单：只挡"归 B 且 A 不在场"
            v2 = (not ha)                    # 白名单：A 不在场就挡
            drop_v1 += v1
            drop_v2 += v2
            flags.append(v1)
            if retr[sid].get("retrieval_leak"):
                kept_by_row.append(len(top) - sum(flags))
        if retr[sid].get("retrieval_leak"):
            bc = g["b_private_chunk"]
            ha, hb, cat = attribute(bc, a_forms, b_forms)
            by_type[s["query_type"]] += 1
            leak_rows.append({
                "sample_id": sid, "query_type": s["query_type"], "conflict_type": s["conflict_type"],
                "b_chunk": bc, "b_chunk_in_top": bc in top, "b_chunk_category": cat,
                "A_named_in_b_chunk": ha, "B_named_in_b_chunk": hb,
                "blockable_free": (hb and not ha),
                "ranks_of_b_hits": retr[sid].get("b_private_hits"),
            })

    n_leak = len(leaks)
    free = sum(1 for r in leak_rows if r["blockable_free"])
    in_top = sum(1 for r in leak_rows if r["b_chunk_in_top"])
    starved_v1 = sum(1 for k in kept_by_row if k <= STARVED)
    # 定义性 vs 经验性要分开：测试集的角色对是按"双向独占块"筛的
    # （compendium_rag_p9_cbi_testset.py:165 `exclusive(b, a, cats)`），
    # 所以"金标块里 A 不在场"是**选块时保证的**，不是这次测出来的。
    # ⇒ blockable_free 与"过滤后 N_retrieval=0"都是同义反复，不能当 R2 的收益证据。
    #    真正有经验含量的是：v1 顺带挡掉了多少**不是金标**的槽位（误伤），
    #    以及 v2 那种"A 不在场就挡"的激进版要付多大代价。
    collateral = drop_v1 - in_top
    res = {
        "schema": "compendium_rag.cbi_owner_shadow/v1",
        "graph_sha": ts.get("graph_sha"),
        "attribution": "名形式代理（speakers_text+text），非图上 owner 边",
        "definitional_warning": (
            "金标块按构造就是「含 B 名、不含 A 名」的独占块（选对阶段的双向独占约束），"
            "所以 blockable_free_of_a 与 leak_rate_after=0 都是同义反复，"
            "**不构成 R2 的收益证据**。本表只有 drop_rate 两项有经验含量。"),
        "n_rows": len(samples), "n_leak_rows": n_leak, "leak_repro_ok": n_leak == EXPECT_LEAKS,
        "leak_by_query_type": dict(by_type),
        "leaked_chunk_in_top": in_top,
        "blockable_free_of_a": free,
        "blockable_needs_a_sacrifice": n_leak - free,
        "slots_total": slots_total,
        "filter_v1_blacklist_B": {"dropped_slots": drop_v1,
                                  "drop_rate": round(drop_v1 / slots_total, 4),
                                  "of_which_gold": in_top,
                                  "collateral_non_gold_slots": collateral,
                                  "collateral_rate": round(collateral / slots_total, 4),
                                  "rows_left_leaky": n_leak - free,
                                  "leak_rate_after": round((n_leak - free) / len(samples), 4)},
        "filter_v2_whitelist_A_only": {"dropped_slots": drop_v2,
                                       "drop_rate": round(drop_v2 / slots_total, 4)},
        "leak_rows_starved_after_v1": starved_v1,
        "chunks_missing_from_index": unattributed,
        "caveat": ("转述场景（A 的私事由别人说出）在名形式代理下被算成「归 B」，"
                   "所以 v1 的 drop_rate 是**误伤上界**；反向地，若泄漏块里 A 与 B 同桌，"
                   "v1 挡不住它 —— 但按构造这种情况不存在，见 definitional_warning。"),
    }
    OUT_JSON.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")

    L = ["# P10·R2 影子：owner/visibility 过滤的可挡性与误伤（只读，名形式代理）",
         "",
         "> **先读这条**：金标块按构造就是「含 B 名、不含 A 名」的双向独占块"
         "（`compendium_rag_p9_cbi_testset.py:165`），所以下面「可零代价挡」与「过滤后 N_retrieval=0」"
         "**都是同义反复，不能当 R2 的收益证据**。有经验含量的只有下面两个丢槽率。",
         "",
         f"- 泄漏复现：影子 **{n_leak}** 条 = 计算器 {EXPECT_LEAKS} 条 ✅（同集合，未换判据）",
         f"- 按题型：{dict(by_type)}",
         f"- 金标锚点块在 top-6：{in_top}/{n_leak}"
         f"（其余 {n_leak - in_top} 条是**别的**归 B 块命中 ⇒ 泄漏判据比单锚点宽，"
         f"与计算器里 gold_anchor_in_top6=12 一致）",
         f"- 可零代价挡掉（定义性，见上）：**{free}/{n_leak}**",
         "",
         f"| 过滤变体 | 丢掉的槽位 | 丢槽率 | 其中非金标（=误伤） | 误伤率 |",
         f"| --- | --- | --- | --- | --- |",
         f"| v1 黑名单（挡归 B 且 A 不在场） | {drop_v1}/{slots_total} | "
         f"{res['filter_v1_blacklist_B']['drop_rate']:.1%} | **{collateral}** | "
         f"{res['filter_v1_blacklist_B']['collateral_rate']:.1%} |",
         f"| v2 白名单（A 不在场就挡，最激进） | {drop_v2}/{slots_total} | "
         f"{res['filter_v2_whitelist_A_only']['drop_rate']:.1%} | — | — |",
         "",
         f"v1 之后剩 ≤{STARVED} 块（上下文饥饿）的泄漏行数：{starved_v1}/{n_leak}；"
         f"索引里找不到的块 {unattributed} 个。",
         "",
         "**v2 的丢槽率才是该拿去比的一条**：它与 P3 角色域过滤器实测的 17–30% 误伤同量级，"
         "说明「A 不在场就挡」这种白名单式可见性，代价会直接压在 MRR 上；"
         "而 v1 的小误伤率只在本量具的选块约束下成立，换到 eval300/blind206 那种"
         "以转述块为 gold 的题集上必然更大。",
         "",
         "## 逐条",
         "",
         "| sample_id | 题型 | 冲突 | 泄漏块 | A 在场 | B 在场 | 零代价可挡 |",
         "| --- | --- | --- | --- | --- | --- | --- |"]
    for r in leak_rows:
        L.append(f"| `{r['sample_id']}` | {r['query_type']} | {r['conflict_type']} | "
                 f"`{r['b_chunk']}` | {r['A_named_in_b_chunk']} | {r['B_named_in_b_chunk']} | "
                 f"{'✅' if r['blockable_free'] else '需牺牲 A'} |")
    L += ["", "## 这条影子能支撑什么决策、不能支撑什么",
          "",
          "能：给出两种可见性规则的**上下文代价量级**（丢槽率、饥饿行数），"
          "以及名形式代理与真 owner 边的分叉方向。",
          "不能：给出「R2 能把 N_retrieval 降到多少」。金标块的定义就包含"
          "「A 不在场」，任何挡住它的过滤器都能把这个通道的读数做到 0 —— "
          "**这一格在本量具上不可证伪**，所以批准写图不能凭这条影子。",
          "该凭的是：在 eval300 / blind206 / gen120 三套**以转述块为 gold** 的题集上量 MRR 误伤"
          "（P3 实测这类过滤器误伤 17–30%），误伤压过收益就不落地。",
          "另外：图上的边可以按「这段私密是 B 的」来标，而名字代理只能看谁的称呼出现在字面里；"
          "转述与代称场景两者必然分叉。"]
    OUT_MD.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"[OK] 影子 → {OUT_JSON.name} / {OUT_MD.name}")
    print(f"     泄漏 {n_leak} 条（复现计算器 ✅）｜v1 挡 {in_top} 条金标 + 误伤 {collateral} 槽 "
          f"({res['filter_v1_blacklist_B']['collateral_rate']:.1%})｜v2 丢槽 "
          f"{res['filter_v2_whitelist_A_only']['drop_rate']:.1%}")
    print("     注意：v1 把 N_retrieval 做到 0 是定义性的（金标块按构造就 A 不在场），不算收益证据")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
