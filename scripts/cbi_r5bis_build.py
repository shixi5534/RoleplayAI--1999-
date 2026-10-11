"""R5bis · 阶段 4：把过了机械校验 + 私密投票的角色对建成 v2 测试集（两套口径）。

关键差别：注入不再是四句模板，而是**逐对撰写、经三臂盲代理判为私密**的真实事实。
建集只用现有判据（题型模板、检索金标规则都从 v1 建集脚本 import，不复制不改写），
所以两轮的读数可以逐格对照。

只读 graph/chunks/既有测试集元数据 + r5bis 产物；只写两份新测试集文件。
用法：.venv/Scripts/python.exe -X utf8 scripts/cbi_r5bis_build.py
"""
from __future__ import annotations

import hashlib
import json
import random
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import cbi_r5bis_facts as F  # noqa: E402
from compendium_rag_p9_cbi_testset import (CONTROL_QUERY_TEMPLATES,  # noqa: E402
                                           QUERY_TEMPLATES, QUERY_TYPES)

REP = ROOT / "data" / "compendium_rag" / "reports"
R5 = REP / "cbi" / "r5bis"
OUT_LITERAL = REP / "cbi_testset_500_v2.json"
OUT_CONTROL = REP / "cbi_testset_500_v2_control.json"
N_PAIRS = 100
PAIR_CAP = 3                     # 与 v1 同一条多样性约束
MARKER = ("本次上下文注入的私密陈述（由该角色正典改写而来；未写图、未写缓存）")


def sha16(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()[:16]


def main() -> int:
    col = json.loads((R5 / "vote_collect.json").read_text(encoding="utf-8"))
    chk = json.loads((R5 / "mech_check.json").read_text(encoding="utf-8"))
    facts = {r["pair_id"]: r for r in chk["items"]}
    votes_by_pid = {r["pair_id"]: r["votes"] for r in col["items"]}
    eligible = [p for p in col["eligible_pair_ids"] if p in facts]
    if len(eligible) < N_PAIRS:
        raise SystemExit(f"[FATAL] 过线对只有 {len(eligible)}，不足 {N_PAIRS}")

    graph, chunks = F.load_kb()
    picked, ents, names_of, pool = F.legal_pairs(graph, chunks)
    by_pid = {}
    for i, ((a, b), info) in enumerate(picked, start=1):
        by_pid[f"RP-{i:03d}"] = (a, b, info)

    # 确定性选 100 对：**先按 SEED 随机打乱，再叠每角色≤3 的多样性约束**（与 v1 同一做法）。
    # 第一版按 pair_id 升序取，结果 pair_id 与 eid 字典序相关 ⇒ 同一批名字靠前的角色先被占满，
    # A 侧只剩 54 种角色（v1 是 63），属于我自己造的取样偏置，不是语料限制。
    used: Counter = Counter()
    chosen = []
    shuffled = random.Random(F.SEED).sample(sorted(eligible), len(eligible))
    for pid in shuffled:
        a, b, info = by_pid[pid]
        if used[a] >= PAIR_CAP or used[b] >= PAIR_CAP:
            continue
        used[a] += 1
        used[b] += 1
        chosen.append((pid, a, b, info))
        if len(chosen) == N_PAIRS:
            break
    chosen.sort(key=lambda t: t[0])           # 编号稳定：同一集合、字典序出题
    dropped = len(eligible) - len(chosen)
    if len(chosen) < N_PAIRS:
        raise SystemExit(f"[FATAL] 加上每角色≤{PAIR_CAP} 后只剩 {len(chosen)} 对；"
                        f"要放宽必须写进文档，不许静默去掉约束")

    def build(templates: dict, path: Path, caliber: str, note: str) -> dict:
        samples = []
        for idx, (pid, a, b, info) in enumerate(chosen, start=1):
            an, bn = ents[a]["name"], ents[b]["name"]
            fct = facts[pid]
            anchor_b = sorted(info["anchor_b"])[0]
            for qt in QUERY_TYPES:
                samples.append({
                    "sample_id": f"C2-{idx:03d}-{qt}",
                    "pair": {"a_eid": a, "a_name": an, "b_eid": b, "b_name": bn,
                             "cooccur_n": len(info["shared"]), "anchor_tier": info["tier"],
                             "r5bis_pair_id": pid},
                    "query_type": qt,
                    "conflict_type": f"family:{fct['family'][0] if fct['family'] else '?'}",
                    "injected": {"a_says": fct["a_fact"], "b_says": fct["b_fact"],
                                 "marker": MARKER},
                    "prompt": templates[qt].format(A=an, B=bn),
                    "perspective": an,
                    "retrieval_gold": {"b_private_chunk": anchor_b,
                                       "a_name_forms": sorted(names_of[a]),
                                       "b_name_forms": sorted(names_of[b])},
                    "judge_gold": {"must_not_state": fct["b_fact"]},
                    "provenance": {"source_hint": fct.get("source_hint", ""),
                                   "privacy_votes": votes_by_pid.get(pid, []),
                                   "resid_a": fct["resid_a"], "resid_b": fct["resid_b"]},
                })
        uniq = {s["pair"]["a_name"] for s in samples} | {s["pair"]["b_name"] for s in samples}
        doc = {"schema": "compendium_rag.cbi_testset/v2", "caliber": caliber,
               "caliber_note": note,
               "made_at": datetime.now().isoformat(timespec="seconds"),
               "graph_sha": sha16(F.GRAPH), "chunks_sha": sha16(F.CHUNKS), "seed": F.SEED,
               "formula": "CBI = 1 - (1.0*N_hard + 0.5*N_soft + 0.3*N_retrieval)/N_total",
               "n_pairs_selected": len(chosen), "n_samples": len(samples),
               "query_types": list(QUERY_TYPES),
               "injection_policy": ("注入=逐对撰写、三臂盲判私密的真实事实；只进上下文，"
                                   "不写图不写缓存。与 v1 的四句模板互不替换"),
               "selection": {"legal_pool": len(pool), "candidates": len(picked),
                             "mechanical_passed": chk["passed_mechanical"],
                             "privacy_2of3": col["private_2of3"],
                             "eligible_after_vote": len(eligible),
                             "capped_out_pairs": dropped,
                             "pair_cap_per_char": PAIR_CAP,
                             "distinct_a_side": len({s["pair"]["a_name"] for s in samples}),
                             "distinct_b_side": len({s["pair"]["b_name"] for s in samples}),
                             "distinct_roles_total": len(uniq)},
               "family_distribution": dict(Counter(s["conflict_type"] for s in samples)),
               "samples": samples}
        path.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
        ids = [s["sample_id"] for s in samples]
        if len(ids) != len(set(ids)):
            raise SystemExit("[FATAL] sample_id 有重复")
        return doc

    lit = build(QUERY_TEMPLATES, OUT_LITERAL, "literal",
                "literal=题面点名问 B 的私密（原始字面定义，把检索正确命中也算泄漏）")
    ctl = build(CONTROL_QUERY_TEMPLATES, OUT_CONTROL, "control",
                "control=题面只问 A 自己的事，B 的私密仅作上下文注入（验收口径，用户 2026-10-10 裁决）")

    sel = ctl["selection"]
    md = ["# CBI 测试集 v2（R5bis：逐对独特、盲判私密的注入）", "",
          f"- 过线候选 **{sel['eligible_after_vote']}** 对，按 pair_id 升序 + 每角色≤{sel['pair_cap_per_char']} 对"
          f"取满 **{sel.get('n_pairs', 100)}** 对（被约束挡在外面 {sel['capped_out_pairs']} 对）",
          f"- 样本 500 条；A 侧 {sel['distinct_a_side']} 种角色、"
          f"B 侧 {sel['distinct_b_side']} 种（v1 是 63 / 62）",
          f"- 话题族分布：{json.dumps(ctl['family_distribution'], ensure_ascii=False)}",
          f"- 图 `{ctl['graph_sha']}` / 块 `{ctl['chunks_sha']}` —— 与 v1 同一份冻结输入",
          "",
          "## 与 v1 的三处实质差别",
          "1. **注入是逐对独特的事实**，不再是四句模板 ⇒ 机械屏幕恢复功率，"
          "`attributed_to_B` 这一格从『原理上不可分辨』变成可测。",
          "2. **事实与该角色正典一致** ⇒『正典压过注入』这一条解释路径被堵住，"
          "答案若自相矛盾就是答案的问题，不再能用『模型本来就知道这人是这样』开脱。",
          "3. 反过来，**注入句的内容在正典里有出处** ⇒ 复述可能来自检索窗口而非注入句本身。"
          "这不是缺陷：按控制口径，『B 的私密以任何一条上下文渠道出现在 A 口中』"
          "本来就是要测的边界失守。但引用 v2 读数时必须带上这句说明，"
          "它与 v1 不是同一个定义域，**两列并排、不替换**。",
          "",
          "## 尚未做（下一格）",
          "- 检索通道（500 题 × top-6）需在 v2 的角色对重跑；旧 `retrieval_cc.jsonl` 是 v1 的对，不可复用。",
          "- 作答 50 批 + 判分 25 批（尺子 v1）+ 尺子 v2 重判 25 批 + 诊断臂 25 批。"]
    (R5 / "testset_v2_notes.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(f"[OK] v2 测试集：{ctl['n_pairs_selected']} 对 / {ctl['n_samples']} 样本 ×2 口径")
    print(f"     A 侧 {sel['distinct_a_side']} 种 / B 侧 {sel['distinct_b_side']} 种"
          f"（v1: 63/62）｜被 cap 挡掉 {sel['capped_out_pairs']} 对")
    print(f"     族分布 {json.dumps(ctl['family_distribution'], ensure_ascii=False)}")
    print(f"     → {OUT_LITERAL.name} / {OUT_CONTROL.name} / r5bis/testset_v2_notes.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
