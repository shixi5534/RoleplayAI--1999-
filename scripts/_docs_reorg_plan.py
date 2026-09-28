# -*- coding: utf-8 -*-
"""文档重整计划（**默认 dry-run**）：把混在一起的 5 套系统文档分门别类。

背景：仓库里并存 **三套 RAG/系统**，文档全部堆在 docs/ 平铺：
  P1 compendium_rag  正典图谱（当前主线）  7033/30269 · 3695 块 · 盲测 206
  P2 plot_graph      剧情图谱（前身/并行）10406/7582 · 9021 块 · 灰机 · inject_pass
  P3 roleplay_core   核心系统（lore 向量层 / 架构 / 提示词 / 画像）
  P4 voice_desktop   语音与桌面宠物（Live2D / pet-v0.3）
  P5 qq              QQ 通道

用法：
  python scripts/_docs_reorg_plan.py            # dry-run，只打印
  python scripts/_docs_reorg_plan.py --apply    # 实际移动（git mv，保留历史）
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# ── 目标结构 ────────────────────────────────────────────────────────────
# 每个条目： (目标相对路径, 项目, 类别, 说明)
# 项目目录用英文短名（脚本/URL 友好），说明用中文写在 docs/README.md 索引里。

P1 = "compendium-rag"
P2 = "plot-graph-rag"
P3 = "roleplay-core"
P4 = "voice-desktop"
P5 = "qq"

# 显式映射：源文件（相对仓库根） -> 目标目录（相对 docs/）
# 规则优先，例外用手工表；此处为**完整清单**，逐条可核。
MAPPING: dict[str, str] = {}


def put(dest: str, *names: str) -> None:
    for n in names:
        MAPPING[n] = dest


# ===== P1 compendium_rag（当前主线）=====
put(f"{P1}/baseline",
    "docs/BASELINE_v2_20260927.md", "docs/BASELINE_v3_20260927.md",
    "docs/BASELINE_v4_20260927.md", "docs/BASELINE_v6_20260928.md",
    "docs/BASELINE_v7_20260928.md")
put(f"{P1}/handover",
    "docs/COMPENDIUM_RAG.md", "docs/COMPENDIUM_RAG_HANDOFF.md",
    "docs/COMPENDIUM_RAG_SESSION2_HANDOFF.md", "docs/COMPENDIUM_RAG_SUBAGENT_PLAYBOOK.md",
    "docs/交接_20260927_工具通道中止.md",
    "docs/交接_20260928_召回率85目标收官与融合重构.md",
    "docs/交接_20260928_召回率85收口_RRF_k常数.md",
    "docs/交接_20260928_总_39全战役.md",
    "docs/compendium补名路线_会话交接_20260926.md")
put(f"{P1}/baseline-repairs",
    "docs/R5立项前评估_20260927_scene共现边.md",
    "docs/R5落盘报告_20260927_定向补桥.md",
    "docs/图谱修复作战书_预注册_20260926.md",
    "docs/图谱与原文质检报告_20260926.md",
    "docs/核验报告_20260927_分支A复验与R4差异归因.md",
    "docs/核验报告Phase2_20260927_插入序根因闭合与tiebreak修复.md",
    "docs/核验报告Phase5_20260927_R4重放链路修复.md")
put(f"{P1}/ranking",
    "docs/排序侧实验_预注册_20260926.md",
    "docs/排序侧实验_执行报告_20260926.md",
    "docs/排序侧实验_后续作战资料_20260926.md",
    "docs/RAG接入生产使用方案_20260926.md")
put(f"{P1}/recall",
    "docs/compendium召回率_下一步路线评估.md",
    "docs/compendium召回率终结报告.md",
    "docs/召回率85目标_盲测验收报告_20260928.md",
    "docs/目标①_池内miss干预报告_20260928.md",
    "docs/目标①_收口报告_20260928.md")
put(f"{P1}/extraction",
    "docs/compendium强模型实体识别_计划书.md",
    "docs/compendium强模型实体识别_执行报告.md",
    "docs/compendium正典入库报告.md",
    "docs/compendium补名路线_灰机实证.md",
    "docs/题集i_预注册与冻结记录.md")

# ===== P2 plot_graph（历史/并行）=====
put(f"{P2}/plan",
    "PLAN/README.md", "PLAN/后端计划.md", "PLAN/前端计划.md",
    "PLAN/lore层优化计划.md", "PLAN/现状报告_20260916.md",
    "PLAN/审查报告_第二轮_外部AI.md", "PLAN/IDEAS_LOG.txt")
put(f"{P2}/acceptance",
    "docs/剧情图谱验收标准.md", "docs/剧情图谱验收报告.md",
    "docs/剧情图谱验收报告-服务层.md", "docs/剧情图谱测试结论.md",
    "docs/剧情图谱100题评测报告.md")
put(f"{P2}/audit",
    "docs/剧情图谱全量审查报告.md", "docs/剧情图谱抽取质量审计.md",
    "docs/剧情图谱-灰机wiki事实核对报告.md", "docs/plot_failed_chunks_18.md",
    "deliverables/plot-rag-audit-20260912.md",
    "deliverables/plot-rag-dialogue-fix-20260912.md",
    "deliverables/plot-rag-edge-fix-20260913.md",
    "deliverables/plot-graph-rag-quality-20260913.md",
    "deliverables/plot-graph-rag-p0-acceptance.md",
    "deliverables/graphrag-audit-plain-20260909.md")
put(f"{P2}/corpus",
    "docs/剧情文件清洗清单.md", "docs/剧情清洗注意事项.md",
    "docs/剧情术语对照词表.md", "docs/剧情时间轴与GraphRAG联动.md",
    "docs/剧情时间轴与人物去向图.md", "docs/剧情抽取-续跑说明.md",
    "docs/剧情别名与抽取裁决记录.md", "docs/语料块质量分析_20260917.md",
    "docs/语料修复执行记录_20260917.md")
put(f"{P2}/eval",
    "docs/RAG测试对接表.md", "docs/RAG测试集交接文档.md",
    "docs/题集证据组复核.md", "docs/300题RAG评测_补抽前后对比.md",
    "docs/RAG召回诊断与优化方案_20260917.md",
    "docs/RAG召回优化下一步计划_20260917.md",
    "docs/RAG召回_60题专项与补位重排_20260917.md",
    "docs/RAG召回_上界探测与计划修订_20260917.md",
    "docs/RAG召回_全开配置上限_20260917.md",
    "docs/RAG召回_全新200题独立复核_20260917.md",
    "docs/RAG召回_多问法改写验证_20260917.md",
    "docs/RAG召回_文献调研_20260917.md",
    "docs/RAG召回_长任务路线图_20260917.md",
    "docs/召回率归因_20260916.md", "docs/别名桥v2与失分归因复核.md",
    "docs/实体识别与查询扩展_20260917.md",
    "docs/排序靶子_证据块名次分布_20260916.md",
    "docs/评测批次效应_20260917.md", "docs/日内现状快照_20260917.md",
    "docs/全量工作总账_20260917.md", "docs/B4查询扩展实验_20260917.md",
    "docs/CrossEncoder重排实验_20260916.md",
    "docs/T1_bge精排标定_20260917.md", "docs/T4_PPR引导dense标定_20260917.md",
    "docs/T5T8_摘要节点验证_20260917.md", "docs/T6_别名漂移过滤_20260917.md",
    "docs/T7_真实补名验证_20260917.md", "docs/T11_评测口径加固_20260917.md",
    "docs/T17_查询语言消融_20260917.md", "docs/T19_叠加验证与推荐配置_20260917.md",
    "data/docs/rag_testset_300.md", "data/docs/rag_testset_200_new.md")
put(f"{P2}/graph-governance",
    "deliverables/graph-relation-governance-20260909.md",
    "deliverables/handover-20260909-relation-governance.md",
    "deliverables/qa-test-report-20260909.md",
    "deliverables/plot-graph-relation-normalization-20260909.md",
    "deliverables/wiki-canonical-verification-20260909.md",
    "deliverables/wiki-r1999-relation-reference-20260909.md")
put(f"{P2}/summary",
    "deliverables/engineering-assurance/剧情GraphRAG-总结-2026-09-11.md",
    "deliverables/graphrag-phase2-audit-20260909.md",
    "deliverables/graphrag-phase2-plan-20260909.md")

# ===== P3 roleplay_core =====
put(f"{P3}/architecture",
    "docs/ARCHITECTURE.md", "docs/class-diagram.mermaid",
    "docs/sequence-diagram.mermaid",
    "RAG_SYSTEM_DESIGN.md", "GRAPHRAG_ENHANCEMENT_PLAN.md",
    "docs/GRAPHRAG加强计划书.md", "docs/UPGRADE_PLAN.md")
put(f"{P3}/profile",
    "docs/user_profile_design.md", "docs/profile-class-diagram.mermaid",
    "docs/profile-sequence-diagram.mermaid")
put(f"{P3}/prompt",
    "ROLEPLAY_PROMPT_OPTIMIZATION_PLAN.md",
    "deliverables/roleplay-prompt-optimization.md",
    "deliverables/roleplay-prompt-optimization-p0.md",
    "deliverables/roleplay-prompt-optimization-p1.md")
put(f"{P3}/audit",
    "deliverables/rag-graphrag-audit-20260908.md",
    "deliverables/rag-knowledge-audit.md",
    "deliverables/optimization-fix-plan.md",
    "deliverables/git-repo-recovery-20260909.md")

# ===== P4 voice_desktop =====
put(f"{P4}/pet-design",
    "docs/DESKTOP_PET_DESIGN.md",
    "docs/design/plan-spec-v0.3.md", "docs/design/plan-visual-v0.3.md",
    "docs/design/pet-presentation-spec-v0.3.md",
    "docs/design/pet-visual-styleboard-v0.3.md",
    "docs/design/pet-v0.3-INDEX.md",
    "docs/design/IMPLEMENTATION-PLAN-v0.3.md")
put(f"{P4}/voice",
    "docs/语音台词集使用说明.md", "docs/语音点击交互设计-架构师草稿.md",
    "docs/调研-点击触发语音交互规范.md", "VOICE_ITERATION_REPORT.md",
    "docs/emotion_upgrade_design.md", "docs/_tmp_voicestat.txt")

# ===== P5 qq =====
put(f"{P5}", "docs/QQ_INTEGRATION.md", "docs/QQ语音回复方案.md")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    # 范围：docs/ 平铺层（含 docs/design/）+ PLAN/ + deliverables/*.md + 4 个根级 .md
    # ⚠ 刻意**不移动 data/ 下任何文件**：
    #   - data/compendium_rag/repairs_v*/ 是带 SHA 锁的冻结证据链（.gitattributes 按路径声明）
    #   - data/docs/*.md 是生成器（gen_rag_testset_300.py 等）的**输出路径**
    #   移动它们会打断证据锚点与生成流程。
    docs = sorted(p for p in (ROOT / "docs").rglob("*") if p.is_file())
    docs += sorted(p for p in (ROOT / "PLAN").rglob("*") if p.is_file())
    docs += sorted(p for p in (ROOT / "deliverables").rglob("*.md") if p.is_file())
    docs += [ROOT / n for n in ("RAG_SYSTEM_DESIGN.md", "GRAPHRAG_ENHANCEMENT_PLAN.md",
                                "ROLEPLAY_PROMPT_OPTIMIZATION_PLAN.md",
                                "VOICE_ITERATION_REPORT.md") if (ROOT / n).is_file()]

    planned, unplanned = [], []
    for p in sorted(set(docs)):
        rel = str(p.relative_to(ROOT)).replace("\\", "/")
        if rel == "docs/README.md":
            continue
        dest = MAPPING.get(rel)
        (planned if dest else unplanned).append((rel, dest))

    print("=" * 100)
    print(f"计划移动 {len(planned)} 个文件；未归类 {len(unplanned)} 个")
    print("=" * 100)
    by: dict[str, list[str]] = {}
    for rel, dest in planned:
        by.setdefault(dest, []).append(rel)
    for dest in sorted(by):
        print(f"\n▶ docs/{dest}/   ({len(by[dest])})")
        for rel in by[dest]:
            print(f"     {rel}")
    if unplanned:
        print("\n" + "=" * 100)
        print(f"⚠ 未归类 {len(unplanned)}：")
        for rel, _ in unplanned:
            print(f"     {rel}")

    if not args.apply:
        print("\n（dry-run；加 --apply 才移动）")
        return 0

    # 写映射表（供 _docs_fix_refs.py 使用）：old_rel -> new_rel
    plan_map = {rel: f"docs/{dest}/{Path(rel).name}" for rel, dest in planned}
    out = ROOT / "data/compendium_rag/reports/_docs_reorg_map.json"
    out.write_text(json.dumps(plan_map, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[map] -> {out.relative_to(ROOT)}  ({len(plan_map)} 条)")

    # 实际移动：git mv 保留历史
    fails = 0
    for rel, dest in planned:
        src = ROOT / rel
        dst = ROOT / "docs" / dest / Path(rel).name
        dst.parent.mkdir(parents=True, exist_ok=True)
        r = subprocess.run(["git", "mv", str(src.relative_to(ROOT)),
                            str(dst.relative_to(ROOT))],
                           cwd=str(ROOT), capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        if r.returncode != 0:
            fails += 1
            print(f"[FAIL] {rel} -> {dest}: {r.stderr.strip()[:120]}")
    print(f"\n移动完成（{len(planned)-fails} 成功 / {fails} 失败）")
    print("⚠ 引用尚未更新，接着跑：python scripts/_docs_fix_refs.py --apply")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
