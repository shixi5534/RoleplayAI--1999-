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

print("\n[Phase 6] 召回率 85% 目标 + 盲测验收 + BASELINE_v6")
b6p = D / "reports/baseline_v6.json"
check("BASELINE_v6 在库", b6p.exists())
if b6p.exists():
    B6 = json.loads(b6p.read_text(encoding="utf-8"))
    pb = B6["primary_blind"]
    check("盲测生产口径 ≥0.85（目标②）",
          pb["production_rerank_hit6"] >= 0.85,
          str(pb["production_rerank_hit6"]))
    check("盲测 verdict = PASS", pb["verdict"] == "PASS", pb["verdict"])
    su = B6["secondary_300cn"]["safety_unanswerable"]
    check("安全线 unanswerable ≤1/104（目标③）", su["hits"] <= 1,
          f'{su["hits"]}/{su["n"]}')
    check("grounded = 1.0000", su["grounded_rate"] == 1.0, str(su["grounded_rate"]))
# 词面通道接线（默认关闭）
cfg = (W / "src/compendium_rag/config.py").read_text(encoding="utf-8")
check("词面通道配置存在（默认 0.0）",
      '_env_float("CMPRAG_LEX_WEIGHT", 0.0)' in cfg)
rt2 = (W / "src/compendium_rag/retriever.py").read_text(encoding="utf-8")
check("LexicalIndex 已实现", "class LexicalIndex" in rt2)
check("rrf_fuse 已加次级键", "(-e.score, e.chunk_id)" in rt2)
# 盲测题集
bq = W / "data/knowledge/_audit/blind_v1/questions_strict.json"
check("盲测 206 题留出集在库", bq.exists())
if bq.exists():
    n_cases = len(json.loads(bq.read_text(encoding="utf-8"))["cases"])
    check("盲测题数 = 206", n_cases == 206, str(n_cases))
check("目标① 干预报告在库", (W / "docs/目标①_池内miss干预报告_20260928.md").exists())
check("BASELINE_v6 报告在库", (W / "docs/BASELINE_v6_20260928.md").exists())

print("\n[Phase 7] RRF k 常数收口 —— 四集裸检索全 ≥0.85 + BASELINE_v7")
b7p = D / "reports/baseline_v7.json"
check("BASELINE_v7 在库", b7p.exists())
if b7p.exists():
    B7 = json.loads(b7p.read_text(encoding="utf-8"))
    check("rrf_k 配置 = 1", B7["retrieval_config"]["rrf_k"] == 1,
          str(B7["retrieval_config"]["rrf_k"]))
    check("v7 回滚开关存在（CMPRAG_RRF_K）",
          "CMPRAG_RRF_K" in B7["retrieval_config"]["rollback"])
    for label, blk, key in [
        ("300cn 裸检索 ≥0.85", B7["secondary_300cn"], "bare_hit6"),
        ("盲测 裸检索 ≥0.85", B7["primary_blind"], "bare_hit6"),
        ("泛化120 裸检索 ≥0.85", B7["generalization_120"], "bare_hit6"),
    ]:
        check(label, blk[key]["rate"] >= 0.85, str(blk[key]["rate"]))
    check("盲测 生产口径 ≥0.85",
          B7["primary_blind"]["production_rerank_hit6"] >= 0.85,
          str(B7["primary_blind"]["production_rerank_hit6"]))
    check("300cn 生产口径无回退（= v6 的 0.8673）",
          B7["secondary_300cn"]["production_rerank_hit6"] == 0.8673,
          str(B7["secondary_300cn"]["production_rerank_hit6"]))
    sl = B7["safety_line"]
    check("安全线 unanswerable = 1/104", sl["unanswerable_hits"] == 1
          and sl["unanswerable_n"] == 104,
          f'{sl["unanswerable_hits"]}/{sl["unanswerable_n"]}')
    check("grounded = 1.0000", sl["grounded"] == 1.0, str(sl["grounded"]))
    # 锁工件必须**全部存在于干净副本**（v6 曾因未 git add -f 而在 clone 中缺失）
    ap = B7.get("artifact_paths") or {}
    missing = [k for k, rel in ap.items() if not (D / rel).exists()]
    check("v7 全部锁定工件在干净副本中存在（无 git 缺件）", not missing, str(missing))
    bad = [k for k, want in B7["artifact_sha256_16"].items()
           if k in ap and (D / ap[k]).exists() and sha16(D / ap[k]) != want]
    check("v7 全部锁定工件 SHA-16 命中", not bad, str(bad))

print("\n[Phase 7b] rrf_k 接线（默认 60 = 零行为变更）")
check("config 有 CMPRAG_RRF_K 且默认 60",
      '_env_int("CMPRAG_RRF_K", 60)' in cfg)
check("retrieve() 接受 rrf_k（默认 60）", "rrf_k: int = 60" in rt2)
check("两处 rrf_fuse 调用均传 k=rrf_k", rt2.count("k=rrf_k") == 2,
      str(rt2.count("k=rrf_k")))
check("pipeline 传递 rrf_k=s.rrf_k", "rrf_k=s.rrf_k" in
      (W / "src/compendium_rag/pipeline.py").read_text(encoding="utf-8"))
check("v7 锁复算脚本在库", (W / "scripts/_verify_v7_locks.py").exists())
check("v7 事实核验脚本在库", (W / "scripts/_verify_v7_handover.py").exists())
check("BASELINE_v7 报告在库", (W / "docs/BASELINE_v7_20260928.md").exists())
check("v7 交接文档在库",
      (W / "docs/交接_20260928_召回率85收口_RRF_k常数.md").exists())
check("rrf_k 回归测试在库", (W / "scripts/_rrf_k_regression.py").exists())
check("gold 审计旁挂在库（未改题集）",
      (W / "data/knowledge/_audit/_85_gold_audit.json").exists())
# gold 审计守红线：题集本体必须**逐字节未变**（以磁盘 SHA-16 为锚点）
check("题集本体未被改动（300cn SHA-16 = b02700c70342864c）",
      sha16(W / "data/knowledge/_audit/rag_testset_300_cn.json") == "b02700c70342864c",
      sha16(W / "data/knowledge/_audit/rag_testset_300_cn.json"))
check("盲测留出集未被改动（SHA-16 锚点 abcd750a3323dc90）",
      bq.exists() and sha16(bq) == "abcd750a3323dc90",
      sha16(bq) if bq.exists() else "MISSING")

print("\n" + "=" * 74)
if FAILS:
    print(f"结果：{len(FAILS)} 项 FAIL -> {FAILS}")
    sys.exit(1)
print("结果：全部 PASS ✓")
