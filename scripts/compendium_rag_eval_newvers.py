# -*- coding: utf-8 -*-
"""新增版本覆盖评测(只读):13 题基线之外,另测本阶段新抽的 activity/appendix_unbound 版本。

为什么单独一个脚本:`compendium_rag_eval.py` 的 13 题是跨会话可比基线,**一字不改**;
本脚本只**追加**覆盖,不替换、不删题,因此不会为迎合指标而弱化任何既有判据。

口径:与基线完全一致(hit@k / MRR / seed_recall / grounded,双模式 full + graph_only)。
用法(项目根目录):
    python scripts/compendium_rag_eval_newvers.py [top_k=6]
"""
from __future__ import annotations

import asyncio
import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import compendium_rag_eval as E  # noqa: E402
from compendium_rag import pipeline as P  # noqa: E402
from compendium_rag.config import get_settings  # noqa: E402

# expect_any 均取自语料该块的**独有词**(非泛用角色名),避免「任何块都命中」的假阳性。
NEW_CASES: list[E.Case] = [
    E.Case("n1", "长夜鸣笛中塞梅尔维斯一行人乘坐的列车叫什么名字？", "单跳",
           ["多瑙黎明号"], ["塞梅尔维斯"],
           "activity__31101_长夜鸣笛 凉水泉/检查站"),
    E.Case("n2", "不老春里白马派的传承是由谁讲给弟子们的？", "单跳",
           ["白马派"], ["鹭鸶剪"],
           "activity__34101_不老春 梦中天台"),
    E.Case("n3", "绿松石蛇俱乐部里蝴蝶女士向佩雷斯妈妈打听什么的下落？", "多跳",
           ["矿物颜料"], ["洛伦兹蝴蝶", "佩雷斯妈妈"],
           "activity__35101_绿松石蛇俱乐部 魔盒里的国王"),
    E.Case("n4", "迁流的盛宴中阿黛拉与贝丽尔在什么地方遇见走失的罗西教授？", "单跳",
           ["地下墓穴"], ["阿黛拉", "贝丽尔"],
           "activity__32101_迁流的盛宴 岔路口"),
    E.Case("n5", "世纪末尺度里蓝图搭建穹顶模型用的主要材料是什么？", "单跳",
           ["回声石"], ["蓝图", "奠基石"],
           "activity__38101_世纪末尺度 不可量度"),
    E.Case("n6", "聚合浪潮中是谁找到了解除机器人限制的办法并操控它们追击？", "多跳",
           ["马克西姆"], ["维尔汀", "塔玛拉"],
           "activity__385101_聚合浪潮 怀旧的伦理"),
    E.Case("n7", "人们向何处去里格蕾塔下一次打算去爬哪座山峰？", "单跳",
           ["阿内托峰"], ["阿德勒"],
           "activity__36101_人们向何处去 夜间攀登者"),
    E.Case("n8", "1.9 地牢剧情里塞梅尔维斯在中枪后呼喊谁的名字？", "单跳",
           ["瓦伦缇娜"], ["塞梅尔维斯", "瓦伦缇娜"],
           "appendix_unbound__022 1_9_地牢剧情 TO BE CONTINUED"),
    E.Case("n9", "1.6 赛季剧情中街市商贩叫卖的「金丹妙药」旁还有什么药？", "跨篇章",
           ["醍醐醒脑"], ["白雪松"],
           "appendix_unbound__006 1_6_赛季剧情"),
    E.Case("n10", "1.2 绿湖噩梦的故事发生在哪个营地？", "跨篇章",
           ["绿湖营地"], ["金蜜儿"],
           "appendix_unbound__001 1_2_绿湖噩梦"),
]


async def main() -> int:
    logging.basicConfig(level=logging.WARNING)
    s = get_settings()
    top_k = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    kb = P.load_kb(s)
    gst = kb.graph.stats()
    print(f"新增版本覆盖评测 {len(NEW_CASES)} 题（top_k={top_k}）")
    print(f"图谱：实体={gst['entities']} 边={gst['edges']} 孤立率={gst['isolated_ratio']}")

    rows = []
    for mode, use_vec in (("full", True), ("graph_only", False)):
        print(f"\n{'=' * 78}\n模式：{mode}\n{'=' * 78}")
        for case in NEW_CASES:
            r = await E.run_case(kb, case, top_k, use_vec)
            r["mode"] = mode
            rows.append(r)
            mark = "✓" if r["hit"] else "✗"
            print(f"  {mark} [{r['kind']}] {r['qid']:<4} seed={r['seed_recall']:.2f} "
                  f"rr={r['rr']:.2f} ev={r['n_evidence']} {r['seconds']:.2f}s  "
                  f"{case.query[:30]}")
            if not r["hit"]:
                print(f"       期望含：{case.expect_any}｜种子：{r['seeds'][:5]}")

    summary = {}
    for mode in ("full", "graph_only"):
        sub = [r for r in rows if r["mode"] == mode]
        n = len(sub) or 1
        summary[mode] = {
            "cases": len(sub),
            "hit@k": round(sum(1 for r in sub if r["hit"]) / n, 4),
            "MRR": round(sum(r["rr"] for r in sub) / n, 4),
            "seed_recall": round(sum(r["seed_recall"] for r in sub) / n, 4),
            "grounded": round(sum(1 for r in sub if r["grounded"]) / n, 4),
        }
    print(f"\n{'=' * 78}\n汇总（新增版本 10 题）\n{'=' * 78}")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    out = s.reports_dir / "eval_report_newvers.json"
    s.ensure_dirs()
    out.write_text(json.dumps({"summary": summary, "rows": rows},
                              ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n报告 → {out}")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
