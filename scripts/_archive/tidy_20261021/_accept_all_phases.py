# -*- coding: utf-8 -*-
"""全阶段验收：在 git HEAD 导出的干净副本上核对 Phase 1–5 的全部交付判据。

用法:
  ./.venv/Scripts/python.exe scripts/_accept_all_phases.py _accept
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
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
z = (W / "docs/compendium-rag/baseline-repairs/图谱修复作战书_预注册_20260926.md").read_text(encoding="utf-8")
check("作战书 §4bis 四条硬规则", "## 4bis." in z and "冷启动" in z and "显式次级键" in z)

print("\n[Phase 4] BASELINE_v4 暖/冷双口径加注")
check("caliber_annotation 存在", "caliber_annotation" in L)
ca = L.get("caliber_annotation", {})
check("warm_vs_cold 记录双口径", "warm_vs_cold" in ca)
check("r4_gain_attribution 记为暖态", "暖态" in str(ca.get("r4_gain_attribution", "")))
doc = (W / "docs/compendium-rag/baseline/BASELINE_v4_20260927.md").read_text(encoding="utf-8")
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
check("R5 评估报告在库", (W / "docs/compendium-rag/baseline-repairs/R5立项前评估_20260927_scene共现边.md").exists())
check("Phase5 重放报告在库", (W / "docs/compendium-rag/baseline-repairs/核验报告Phase5_20260927_R4重放链路修复.md").exists())
check("Phase2 核验报告在库", (W / "docs/compendium-rag/baseline-repairs/核验报告Phase2_20260927_插入序根因闭合与tiebreak修复.md").exists())

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
    # graph_live 是活图锚点：R6（2026-09-28）演进图谱后按设计失效
    # （历史惯例：v4 的判据即「除 live 外 6/6」）。其余锁必须全中。
    bad5_nonlive = [k for k in bad5 if k != "graph_live"]
    check("BASELINE_v5 锁命中（除活图外可复算）", not bad5_nonlive, str(bad5_nonlive))
    if "graph_live" in bad5:
        # v5 记录的活图（4bbefd9eba577c01，R5 补桥后）== R6 改图前的状态，
        # 即 backups/graph.json.prev.r6（R6 的备份就是它取代的那张图）。
        check("  v5 活图锚点可由 prev.r6 复原",
              sha16(D / "backups/graph.json.prev.r6") == locks5["graph_live"],
              locks5["graph_live"])
check("R5 提案在库（312 add_edge）", (D / "repairs_v5/proposal.json").exists())
check("R5 落盘报告在库", (W / "docs/compendium-rag/baseline-repairs/R5落盘报告_20260927_定向补桥.md").exists())
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
check("目标① 干预报告在库", (W / "docs/compendium-rag/recall/目标①_池内miss干预报告_20260928.md").exists())
check("BASELINE_v6 报告在库", (W / "docs/compendium-rag/baseline/BASELINE_v6_20260928.md").exists())

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
    # 同 v5：graph_live 为活图锚点，R6 后按设计失效；其余锁必须全中。
    bad_nonlive = [k for k in bad if k != "graph_live"]
    check("v7 非活图锁全部命中（历史可重建）", not bad_nonlive, str(bad_nonlive))
    if "graph_live" in bad:
        check("  v7 活图锚点可由 prev.r6 复原",
              sha16(D / "backups/graph.json.prev.r6")
              == B7["artifact_sha256_16"]["graph_live"])

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
check("BASELINE_v7 报告在库", (W / "docs/compendium-rag/baseline/BASELINE_v7_20260928.md").exists())
check("v7 交接文档在库",
      (W / "docs/compendium-rag/handover/交接_20260928_召回率85收口_RRF_k常数.md").exists())
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

print("\n[Phase 8] R4-K01 收口（新批次 R6）+ BASELINE_v8")
v8p = D / "reports/baseline_v8.json"
check("BASELINE_v8 在库", v8p.exists())
if v8p.exists():
    B8 = json.loads(v8p.read_text(encoding="utf-8"))
    # 检索配置必须与 v7 相同（本轮未改检索逻辑）
    rc = B8["retrieval_config"]
    check("v8 检索配置不变（lex_weight=1.0, rrf_k=1）",
          rc["lex_weight"] == 1.0 and rc["rrf_k"] == 1,
          f"lex_weight={rc['lex_weight']} rrf_k={rc['rrf_k']}")
    # 指标零变化
    m = B8["metrics"]
    check("v8 300cn 裸 = 167/196", (m["300cn_bare_hit6"]["hits"],
                                    m["300cn_bare_hit6"]["n"]) == (167, 196))
    check("v8 盲测 裸 = 184/206", (m["blind206_bare_hit6"]["hits"],
                                   m["blind206_bare_hit6"]["n"]) == (184, 206))
    check("v8 泛化 裸 = 118/120", (m["gen120_bare_hit6"]["hits"],
                                   m["gen120_bare_hit6"]["n"]) == (118, 120))
    check("v8 安全线 = 1/104", m["safety_unanswerable"]["hits"] == 1)
    check("R4-K01 = APPLIED", "APPLIED" in B8["r4_k01_status"]["state"])
    # 图锚点
    check("v8 graph_live = 026b41699f021db2",
          B8["graph"]["sha256_16"] == "026b41699f021db2",
          B8["graph"]["sha256_16"])
    check("v8 图规模 7033/30269",
          B8["graph"]["entities"] == 7033 and B8["graph"]["edges"] == 30269)
    check("v8 回滚锚点 prev.r6 = 4bbefd9eba577c01",
          B8["graph"]["prev"].startswith("4bbefd9eba577c01"),
          B8["graph"]["prev"])
    # 锁工件全部存在且在干净副本中可复算
    ap8 = B8.get("artifact_paths") or {}
    miss8 = [k for k, rel in ap8.items() if not (D / rel).exists()]
    check("v8 全部锁定工件在干净副本中存在", not miss8, str(miss8))
    bad8 = [k for k, want in B8["artifact_sha256_16"].items()
            if k in ap8 and (D / ap8[k]).exists() and sha16(D / ap8[k]) != want]
    check("v8 全部锁定工件 SHA-16 命中", not bad8, str(bad8))

# R6 提案与落盘核验脚本
check("R6 提案在库（新批次，未改 v4）",
      (D / "repairs_v6/proposal.json").exists())
b4 = json.loads((D / "repairs_v4/proposal.json").read_text(encoding="utf-8"))
k01b = [e for e in b4["entries"] if e.get("id") == "R4-K01"][0]
check("v4 的 R4-K01 仍为 keep_with_note（重放链未破）",
      k01b["type"] == "keep_with_note", k01b["type"])
check("R6 提案条数 = 1",
      len(json.loads((D / "repairs_v6/proposal.json")
                     .read_text(encoding="utf-8"))["entries"]) == 1)
check("R6 落盘回滚锚点 prev.r6 在库",
      (D / "backups/graph.json.prev.r6").exists())
check("R6 核验脚本在库", (W / "scripts/_decide_verify_r6.py").exists())
check("零变化证明脚本在库", (W / "scripts/_decide_r6_no_change.py").exists())

print("\n[Phase 8b] gold 缺陷统一登记表（双口径）")
regp = W / "data/knowledge/_audit/gold_defects_registry.json"
check("统一登记表在库", regp.exists())
if regp.exists():
    RG = json.loads(regp.read_text(encoding="utf-8"))
    check("登记表版本化", RG.get("version") == 1, str(RG.get("version")))
    check("保守豁免 = 12 道", len(RG["exempt_qids_conservative"]) == 12,
          str(len(RG["exempt_qids_conservative"])))
    check("宽松豁免 = 15 道", len(RG["exempt_qids_inclusive"]) == 15,
          str(len(RG["exempt_qids_inclusive"])))
    check("声明取代两份旧 sidecar",
          len(RG.get("supersedes") or []) == 2)
    check("双口径脚本在库", (W / "scripts/_decide_eval_dual.py").exists())

print("\n[Phase 8c] 待决 5 项裁决记录在库")
check("裁决记录在库",
      (W / "docs/compendium-rag/recall/待决裁决记录_20260928.md").exists())
for s in ("_decide_r4k01_gate.py", "_decide_r4k01_scope.py", "_decide_p3p4.py",
          "_decide_lexfirst_prod.py", "_decide_lock_v8.py"):
    check(f"{s} 在库", (W / "scripts" / s).exists())

print("\n[Phase 9] 文档精简（历史过程档 → 编年史）")
# 每个子系统应有一份 CHRONICLE.md，且 docs 总量已精简
for sub in ("compendium-rag", "plot-graph-rag", "roleplay-core",
            "voice-desktop", "qq"):
    ck = W / "docs" / sub / "CHRONICLE.md"
    check(f"{sub} 编年史在库", ck.exists())
    if ck.exists():
        t = ck.read_text(encoding="utf-8")
        n = sum(1 for ln in t.splitlines() if ln.startswith("## "))
        ns = sum(1 for ln in t.splitlines() if ln.startswith("- 来源："))
        check(f"  {sub} 编年史条目与来源数一致", n == ns and n > 0, f"{n}/{ns}")
# docs 总量控制（精简后应 < 90，历史 140）
n_docs = len([p for p in (W / "docs").rglob("*") if p.is_file()])
check("docs 文件数已精简（< 90，历史 140）", n_docs < 90, str(n_docs))
# 合并前的快照标签（可找回原文）
tags9 = subprocess.run(["git", "tag", "-l"], cwd=str(W),
                       capture_output=True, text=True,
                       encoding="utf-8", errors="replace").stdout.split()
check("合并前快照标签存在（原文可找回）",
      "backup-pre-testdocs-cleanup" in tags9)
# 当前权威文档未被误合并（抽查关键几份）
for must in ("docs/compendium-rag/baseline/BASELINE_v7_20260928.md",
             "docs/roleplay-core/architecture/ARCHITECTURE.md",
             "docs/voice-desktop/pet-design/DESKTOP_PET_DESIGN.md",
             "docs/plot-graph-rag/acceptance/剧情图谱验收标准.md"):
    check(f"当前权威保留：{must.split('/')[-1]}", (W / must).exists())
# QA 测试已合并为一份
check("QA 测试已合并为 test_qa_verification.py",
      (W / "tests/test_qa_verification.py").exists())
for gone in ("tests/test_qa_profile_verify.py",
             "tests/test_qa_profile_r2_verify.py",
             "tests/test_qa_independent_verify.py",
             "tests/test_qa_scratch_max.py"):
    check(f"  已合并源不存在：{gone.split('/')[-1]}", not (W / gone).exists())
# 未被 pytest 收集的零引用文件已删
for gone in ("tests/voice_repro/repro.py", "tests/qa_consistency_check.py"):
    check(f"  已删未收集文件：{gone.split('/')[-1]}", not (W / gone).exists())
# 一次性产物已清理
n_d = len([p for p in (D).iterdir() if p.is_file()])
check("data/compendium_rag 顶层文件已精简（历史 1398）", n_d < 200, str(n_d))

print("\n[Phase 9c] 项目结构整理（根目录 / 忽略规则 / 归档 / 依赖一致）")
_pj = subprocess.run([sys.executable, str(W / "scripts/_project_health.py")],
                     cwd=str(W), capture_output=True, text=True,
                     encoding="utf-8", errors="replace")
check("项目体检 RESULT: ALL OK", "RESULT: ALL OK" in (_pj.stdout or ""),
      (_pj.stdout or "").strip().splitlines()[-1] if _pj.stdout else "无输出")
# 根目录不得有未登记散落文件
ROOT_OK = {".env", ".env.example", ".gitattributes", ".gitignore",
           "pyproject.toml", "README.md", "requirements.txt", "start_server.bat",
           # worktree 下 .git 是文件（指向真实 gitdir），非目录
           ".git"}
IGNORED_OK = {".env.env.bak.20260831_232917", "_shuzhi_extract.txt",
              "_tmp_pron_edges.txt"}
_root_extra = sorted(p.name for p in W.iterdir()
                     if p.is_file() and p.name not in ROOT_OK | IGNORED_OK)
check("根级无未登记散落文件", not _root_extra, str(_root_extra))
# 一次性产物已归档
check("scripts/_archive/ 在库", (W / "scripts/_archive").is_dir())
check("src/data 已移出代码树", not (W / "src/data").exists())
# 依赖清单不再漏项
_rq = (W / "requirements.txt").read_text(encoding="utf-8")
check("requirements.txt 含 fastapi 与 python-multipart",
      "fastapi" in _rq and "python-multipart" in _rq)
# .gitignore 防复发规则
_gi = (W / ".gitignore").read_text(encoding="utf-8")
for pat in (".pytest_bt/", "pytest-of-Lenovo/", "roleplay_test_qenmhfwr/",
            "_poc_shots/"):
    check(f".gitignore 含 {pat}", pat in _gi)

print("\n" + "=" * 74)
if FAILS:
    print(f"结果：{len(FAILS)} 项 FAIL -> {FAILS}")
    sys.exit(1)
print("结果：全部 PASS ✓")
