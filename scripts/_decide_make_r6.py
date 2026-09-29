# -*- coding: utf-8 -*-
"""生成 R6 提案：执行 R4-K01 的仲裁裁决（摘除死别名 `诊疗@诊所`）。

为什么不直接改 repairs_v4/proposal.json：
  该文件的 R4-K01 必须保持 `keep_with_note`，否则 **R4 重放链路断裂** ——
  从 prev.r4 重放将无法复现冻结 SHA `c021f0a0bc7a0dce`（BASELINE_v4 的锚点）。
  详见 docs/compendium-rag/handover 与 scripts/_check_r4_replay.py。
  故以**新批次 R6** 执行该裁决，历史提案零改动。

schema 依据：remove_alias 用 dict 形态 target（与 v2/v4 一致）：
  {"target": {"owner_eid": <属主>, "alias": <别名>}, ...}
  —— v4-K01 当初失败正是因为 target 是裸字符串且无 alias 字段，
     Applier 的 `_alias()` 返回 None -> 预检报「alias 不在属主别名表: None@诊所」。

预注册闸门（已实测 PASS，见 scripts/_decide_r4k01_gate.py）：
  摘除后 gen-120 复跑 GA-25 必须保持命中；破则回滚。
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "data/compendium_rag/graph.json"

g = json.loads(GRAPH.read_text(encoding="utf-8"))
ent = {e["eid"]: e for e in g["entities"]}
owner, alias = "诊所", "诊疗"
assert owner in ent, f"属主不存在: {owner}"
assert alias in ent[owner]["aliases"], f"别名不在属主表: {alias}@{owner}"

defect = [
    e for e in g["entities"]
    if alias in e["eid"] and e["eid"] != owner
]

proposal = {
    "meta": {
        "author": "main-session (R4-K01 arbitration enforcement)",
        "timestamp": "2026-09-28",
        "batch": "R6 —— 执行 R4-K01 未落盘仲裁：摘除死别名 诊疗@诊所（一项，零指标影响）",
        "network": "none（零网络）",
        "graph_state": {
            "entities": len(g["entities"]),
            "edges": len(g["edges"]),
            "fingerprint": g.get("fingerprint"),
        },
        "why_new_batch": (
            "R4-K01 的仲裁（2026-09-27）判定 remove，但从未落盘（Applier fail-closed）。"
            "不可直接改 repairs_v4/proposal.json：该文件的 R4-K01 必须保持 keep_with_note，"
            "否则从 prev.r4 重放无法复现冻结 SHA c021f0a0bc7a0dce（BASELINE_v4 锚点）。"
            "故以新批次执行，保证历史重放链与本次变更互不干扰。"
        ),
        "precondition_gate": (
            "预注册闸门：摘除后 gen-120 复跑 GA-25 必须保持命中，破则回滚。"
            "实测 PASS（scripts/_decide_r4k01_gate.py：hit 保持 True，rr=0.333 不变，"
            "且错种子『诊所』从 seeds 中消失）。"
        ),
        "scope_proof": (
            "link() 只在别名字面出现于 query 时才命中（retriever.py:375 遍历 alias_index.keys() "
            "并判 `if name in query`），故本项影响范围 == 含『诊疗』串的题。"
            "三集全扫（_decide_r4k01_scope.py）结果：300cn 0 道 / gen120 1 道(GA-25) / blind 0 道。"
        ),
        "expected": {
            "entities": len(g["entities"]),
            "edges": len(g["edges"]),
            "alias_total": sum(len(e.get("aliases") or []) for e in g["entities"]) - 1,
            "metrics_change": "无（GA-25 摘除前后均命中）",
        },
    },
    "entries": [
        {
            "id": "R6-K01",
            "type": "remove_alias",
            "target": {"owner_eid": owner, "alias": alias},
            "owner": owner,
            "alias": alias,
            "rationale": (
                "死别名：`诊疗` 在查『医生/诊所』时以 0.9 的较低分数把跨篇实体 `诊所` 拉为种子，"
                "属噪声；GA-25 的真正命中来源是独立实体 `诊疗室`（exact 1.0，其声称块即 GA-25 gold 文档）。"
                "R4 原判 keep_with_note（因该串出现在已知查询路由路径上），"
                "2026-09-27 仲裁改判 remove 并设闸门；闸门实测通过，故本轮执行。"
            ),
            "evidence": [
                {
                    "src": "docs/compendium-rag/baseline-repairs/核验报告_20260927_分支A复验与R4差异归因.md",
                    "quote": "2026-09-27 仲裁：采纳 Verifier remove 方案——GA-25 命中来源为 诊疗室 exact-1.0（独立实体），诊疗@诊所 为跨篇噪声种子（0.9）",
                },
                {
                    "src": "scripts/_decide_r4k01_gate.py 实测",
                    "quote": "摘除前 seeds=[伊索尔德, 诊疗室, 索尔, 诊所] -> 摘除后 seeds=[伊索尔德, 诊疗室, 索尔]；GA-25 hit=True 两侧一致",
                },
            ],
            "arbitration_ref": "R4-K01（2026-09-27 仲裁；因 Applier fail-closed 未落盘）",
            "arbitration_status": "APPLIED-BY-R6（本轮以新批次执行）",
            "before": f"alias {alias}@{owner} 存在（waiver）；alias 总数 {sum(len(e.get('aliases') or []) for e in g['entities'])}",
            "after": "摘除该别名；GA-25 命中不受影响，种子集去掉噪声实体『诊所』",
            "expected_effect": "零指标变化（GA-25 仍命中）；仅减少一个错种子",
        }
    ],
}

out = ROOT / "data/compendium_rag/repairs_v6/proposal.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(proposal, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"[ok] -> {out.relative_to(ROOT)}")
print(f"     owner={owner}  alias={alias}  entries={len(proposal['entries'])}")
print(f"     同名实体（可能受影响的其它实体）={[e['eid'] for e in defect]}")
print(f"     当前别名总数 = {sum(len(e.get('aliases') or []) for e in g['entities'])}")
