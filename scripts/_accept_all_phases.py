# -*- coding: utf-8 -*-
"""全阶段验收：在 git HEAD 导出的干净副本上核对 Phase 1–5 的全部交付判据。

用法:
  ./.venv/Scripts/python.exe scripts/_accept_all_phases.py _accept
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

W = Path(sys.argv[1] if len(sys.argv) > 1 else "_accept")
D = W / "data/compendium_rag"
FAILS: list[str] = []


def check(label: str, cond: bool, detail: str = "") -> None:
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}{('  ' + detail) if detail else ''}")
    if not cond:
        FAILS.append(label)


def sha16(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


print("=" * 74)
print(f"全阶段验收 @ {W}", )
print("=" * 74)

print("\n[Phase 1] R1–R4 版本背书（BASELINE_v4 历史冻结件）")
g = D / "graph.json"
d = json.loads(g.read_text(encoding="utf-8"))
check("graph 实体 7033", len(d["entities"]) == 7033, str(len(d["entities"])))
check("graph 边 ≥ 29957（R5 后 30269）", len(d["edges"]) >= 29957, str(len(d["edges"])))
L = json.loads((D / "reports/baseline_v4.json").read_text(encoding="utf-8"))
m = {"eval_300cn_after_r4": "reports/eval_300cn_after_r4.json",
     "eval_gen_after_r4": "reports/eval_gen_after_r4.json",
     "rank_rerank_lab_300cn_r4": "reports/rank_rerank_lab_300cn_r4.json",
     "rank_collect_300cn_r4": "reports/rank_collect_300cn_r4_top30.json",
     "backup_prev_r4": "backups/graph.json.prev.r4",
     "baseline_v3": "reports/baseline_v3.json"}
bad = [k for k, r in m.items() if sha16(D / r) != L["artifact_sha256_16"][k]]
check("BASELINE_v4 历史冻结锁仍命中（除 live 外 6/6）", not bad, str(bad))
check("repairs_v3 全目录在库", (D / "repairs_v3/proposal.json").exists()
      and (D / "repairs_v3/verification.json").exists())
check("backups/graph.json.prev.r3 在库", (D / "backups/graph.json.prev.r3").exists())
check(".gitattributes 在库（-text 禁 EOL 转换）", (W / ".gitattributes").exists())

print("\n[Phase 2] 插入序确定性")
rt = (W / "src/compendium_rag/retriever.py").read_text(encoding="utf-8")
check("retriever 显式次级键", "lambda k: (-len(k), k)" in rt)
gs = (W / "src/compendium_rag/graph_store.py").read_text(encoding="utf-8")
check("from_dict 别名归属确定化", "alias_claims" in gs)
check("GraphStore.save 统一 indent=2 + CRLF", 'indent=2' in gs and '\\r\\n' in gs)
for f, exp in [("eval_300cn_after_tiebreak_20260927.json", 156),
               ("eval_gen_after_tiebreak_20260927.json", 96)]:
    p = D / "reports" / f
    if p.exists():
        rows = [r for r in json.loads(p.read_text(encoding="utf-8"))["rows"]
                if r.get("mode") == "full" and r.get("answerable")]
        h = sum(1 for r in rows if r.get("hit"))
        check(f"{f} hit={exp}", h == exp, f"{h}/{len(rows)}")
    else:
        check(f"{f} 存在", False)

print("\n[Phase 3] 工具与协议加固")
ri = (W / "scripts/compendium_rag_rebuild_indexes.py").read_text(encoding="utf-8")
check("rebuild_indexes 写前自动备份", "_backup_existing" in ri and "shutil.copy2" in ri)
gi = (W / ".gitignore").read_text(encoding="utf-8")
check(".gitignore 挡 safetensors", "*.safetensors" in gi)
check(".gitignore 挡 bge-reranker 目录", "bge-reranker-v2-m3/" in gi)
z = (W / "docs/图谱修复作战书_预注册_20260926.md").read_text(encoding="utf-8")
check("作战书 §4bis 四条硬规则", "## 4bis." in z and "冷启动" in z and "显式次级键" in z)

print("\n[Phase 4] BASELINE_v4 暖/冷双口径加注")
check("caliber_annotation 存在", "caliber_annotation" in L)
ca = L.get("caliber_annotation", {})
check("warm_vs_cold 记录双口径", "warm_vs_cold" in ca)
check("r4_gain_attribution 记为暖态", "暖态" in str(ca.get("r4_gain_attribution", "")))
doc = (W / "docs/BASELINE_v4_20260927.md").read_text(encoding="utf-8")
check("BASELINE_v4.md 有口径补注表", "冷启动可复现" in doc)

print("\n[Phase 5] R5 评估 + R4 重放链路")
rp = D / "repairs_v4/proposal.json"
P = json.loads(rp.read_text(encoding="utf-8"))
k01 = [e for e in P["entries"] if e.get("id") == "R4-K01"][0]
check("R4-K01 还原为 keep_with_note", k01["type"] == "keep_with_note", k01["type"])
check("R4-K01 标注仲裁未落盘", "NOT-APPLIED" in str(k01.get("arbitration_status", "")))
n_rm = sum(1 for e in P["entries"] if e.get("type") == "remove_alias")
check("remove_alias 条数 = 77（与 994→917 对账）", n_rm == 77, str(n_rm))
ap = (W / "scripts/_graph_apply_repairs.py").read_text(encoding="utf-8")
check("Applier 落盘 CRLF（与 save/冻结件一致）", '\\r\\n' in ap)
check("R5 评估报告在库", (W / "docs/R5立项前评估_20260927_scene共现边.md").exists())
check("Phase5 重放报告在库", (W / "docs/核验报告Phase5_20260927_R4重放链路修复.md").exists())
check("Phase2 核验报告在库", (W / "docs/核验报告Phase2_20260927_插入序根因闭合与tiebreak修复.md").exists())

print("\n[Phase 5] R5 落盘（定向补桥）")
b5p = D / "reports/baseline_v5.json"
check("BASELINE_v5 在库", b5p.exists())
if b5p.exists():
    B5 = json.loads(b5p.read_text(encoding="utf-8"))
    check("R5 后边数 = 30269", B5["graph"]["edges"] == 30269, str(B5["graph"]["edges"]))
    check("R5 主口径 0.8776", B5["primary"]["rerank_hit6"] == 0.8776,
          str(B5["primary"]["rerank_hit6"]))
    check("R5 零回归记录", B5["eval300_no_regression"]["full"].startswith("156/196"))
    locks5 = B5["artifact_sha256_16"]
    m5 = {"graph_live": "graph.json",
          "backup_prev_r5": "backups/graph.json.prev.r5",
          "eval_300cn_after_r5": "reports/eval_300cn_after_r5.json",
          "rank_rerank_lab_300cn_r5": "reports/rank_rerank_lab_300cn_r5.json",
          "meetability_after_r5": "reports/meetability_test_after_r5.json"}
    bad5 = [k for k, r in m5.items() if sha16(D / r) != locks5[k]]
    check("BASELINE_v5 锁命中（5/5 可复算）", not bad5, str(bad5))
check("R5 提案在库（312 add_edge）", (D / "repairs_v5/proposal.json").exists())
check("R5 落盘报告在库", (W / "docs/R5落盘报告_20260927_定向补桥.md").exists())
check("相遇测试复测报告在库", (D / "reports/meetability_test_after_r5.json").exists())

print("\n" + "=" * 74)
if FAILS:
    print(f"结果：{len(FAILS)} 项 FAIL -> {FAILS}")
    sys.exit(1)
print("结果：全部 PASS ✓")
