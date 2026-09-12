# -*- coding: utf-8 -*-
"""以灰机wiki 为标准答案的剧情 RAG 检索评测（非 pytest，直接跑真实图谱）。

问答题库全部来自 2026-09-12 灰机wiki 联网核查确认的史实（角色规范名 /
故事年代 / 关键剧情事实），评分方式为「证据关键词组命中」：
  - 每个 case 定义若干 evidence 组（组内为同义关键词的备选）；
  - 对问题检索 top_chunks 条证据块，取其正文并集；
  - 每组只要有一个关键词出现在任一证据块正文即算该组覆盖；
  - 全部组覆盖 → PASS；否则 FAIL（并打印缺失组，便于定位检索缺口）。

用法（项目根目录）：
  .venv/Scripts/python.exe -X utf8 scripts/eval_rag_huiji.py
  .venv/Scripts/python.exe -X utf8 scripts/eval_rag_huiji.py --top 5 --verbose
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from roleplay.config import get_settings  # noqa: E402
from roleplay.core.knowledge.factory import build_plot_registry  # noqa: E402

CHARACTER = "wu_ming_zhe"


def _infer_path(meta: dict) -> str:
    """路径归因兜底（老版本没有 meta["path"] 时按旧字段结构推断）。"""
    if str(meta.get("via") or "") == "plot_lexical":
        return "lexical"
    if meta.get("seed_mention"):
        return "mention"
    if meta.get("edge"):
        return "edge"
    return "unknown"

# ── 题库：q / ref（灰机标准答案要点）/ evidence 组（组内互为备选关键词）────────
# 注：曾设「疯癫与文明故事发生地→乌斯怀亚」一题，oracle 诊断发现语料 8358 块中
# 乌斯怀亚/火地岛 0 命中（ASR 未提及地名），属无效题已移除；其余 14 题证据均在语料。
CASES = [
    {
        "q": "薇洛的真名是什么？",
        "ref": "Charlotte O'Hagan（伦敦十字街女巫，前乌卢鲁运动会最年轻金牌得主）",
        "evidence": [["Charlotte", "夏洛蒂", "夏洛特", "奥哈根"]],
    },
    {
        "q": "可燃点体内的火到底是什么？",
        "ref": "乌卢鲁圣火，本体为 Ulu（和平乌鲁）",
        # oracle 2026-09-12：语料 ASR 不出现「圣火/火种」（0 块），火的表述为
        # "the fire"(56 块)/"火焰"(1 块)，故组 1 补充 ASR 用词备选
        "evidence": [["Ulu", "和平乌鲁"], ["圣火", "火种", "火焰", "fire"]],
    },
    {
        "q": "旧金山海特街的疗愈师是谁？",
        "ref": "环状水星（Mercuria），兼迪厅舞女",
        "evidence": [["环状水星", "Mercuria"]],
    },
    {
        "q": "J 的义妹是谁？",
        "ref": "保利娜·勒萨奇（Paulina），原圣洛夫基金会调查员，第二次暴雨中被回溯而死",
        "evidence": [["保利娜", "Paulina"]],
    },
    {
        "q": "雷米特杯失窃案里 Melania 的保安公司叫什么？",
        "ref": "拉米雷斯保安公司（Ramirez security company）",
        "evidence": [["拉米雷斯", "Ramirez", "雷米雷斯"]],
    },
    {
        "q": "《神秘警探C07》三部曲的导演是谁？",
        "ref": "菲林士多（Noire），中国香港导演",
        "evidence": [["菲林士多", "Noire"], ["C07", "神秘警探"]],
    },
    {
        "q": "《疯癫与文明》里那座巨型监狱叫什么？",
        "ref": "科马拉（Komala），全景监狱",
        "evidence": [["科马拉", "Komala", "全景监狱"]],
    },
    {
        "q": "虚构集的小说《理性家族的崛起与衰落》的故事发生地是哪里？",
        "ref": "阿马尔菲塔诺（Amalfitano，取自波拉尼奥《2666》人名）",
        "evidence": [["阿马尔菲塔诺", "Amalfitano"]],
    },
    {
        "q": "卡卡尼亚的本名是什么？",
        "ref": "克拉拉·温格勒（Klara Vingler），维也纳精神科医学生",
        "evidence": [["克拉拉", "Clara", "温格勒"]],
    },
    {
        "q": "维也纳篇与卡卡尼亚对峙决斗的医生是谁？",
        "ref": "施瓦茨医生（Dr. Schwartz，以电击治疗骗财）",
        "evidence": [["施瓦茨", "Schwartz"]],
    },
    {
        "q": "海因里希最后被谁杀死？",
        "ref": "被叛变的伊索尔德开枪击毙",
        "evidence": [["海因里希", "Heinrich"], ["伊索尔德", "Isolde"]],
    },
    {
        "q": "自由海风号邮轮的音乐总监是谁？",
        "ref": "芭卡洛儿·斯特拉迪瓦里（Barcarola Stradivari），克雷莫纳人",
        "evidence": [["芭卡洛儿", "Barcarola", "斯特拉迪瓦里"]],
    },
    {
        "q": "努库泰澳的岛民都有谁？",
        "ref": "图图石子（Fatutu）、托阿（Toa）、塞洛尼（Selone）、卡穆塔（Kamuta）",
        # oracle 2026-09-12：Salone 所在块与 Nuku* 岛名块零共现（语料缺口），
        # 组 3 改以参考答案中同列的第 4 位岛民 Kamuta 为备选（Nukutai 块共现 1）
        "evidence": [["图图石子", "Tutu", "Fatutu"], ["托阿", "Toa"], ["塞洛尼", "Salone", "Selone", "卡穆塔", "Kamuta"]],
    },
    {
        "q": "在中央塔里自囚的医生是谁？",
        "ref": "阿莱夫（Aleph，碎裂品所属，2.6 主线 BOSS 形态）",
        # oracle 2026-09-12：ASR 语料为英文，"中央塔/自囚" 中文词 0 块，
        # 场景表述为 "central tower"（9 块，其中 1 块共现 Aleph）
        "evidence": [["阿莱夫", "Aleph"], ["中央塔", "自囚", "central tower"]],
    },
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=5, help="每问取几条证据块")
    ap.add_argument("--verbose", action="store_true", help="打印证据块正文摘录")
    args = ap.parse_args()

    settings = get_settings()
    # 与生产共用装配路径（build_plot_registry ← Settings）：脚本自查发现，
    # 这里曾手工 new PlotGraphRegistry(...) 只传 4 个参数，导致新增的融合权重/种子门控
    # 全部退回默认值——评测与生产配置漂移，数字不可信。
    registry = build_plot_registry(settings)
    retr = registry.get(CHARACTER)
    if retr is None:
        print("[FAIL] 图谱未能加载")
        return 1
    store = retr.store
    print(f"[load] 实体 {len(store.entities())}｜边 {len(store.all_edges())}｜top_chunks={args.top}")

    rows = []
    t0 = time.time()
    for case in CASES:
        chunks = retr.retrieve(case["q"], top_chunks=args.top)
        texts = [c.text for c in chunks]
        union = "\n".join(texts)
        group_hit = []
        for gi, group in enumerate(case["evidence"]):
            hit = next((kw for kw in group if kw in union), None)
            group_hit.append((gi, hit))
        missing = [gi for gi, hit in group_hit if hit is None]
        covered = len(case["evidence"]) - len(missing)
        rel = sum(1 for t in texts if any(kw for g in case["evidence"] for kw in g if kw in t))
        n_graph = sum(1 for c in chunks if c.metadata.get("via") == "plot_graph")
        # 路径归因：旧报告的 n_via_graph 恒等于 n_chunks（图路两通道都标 plot_graph），
        # 是个恒 1.0 的无效指标；这里按 meta["path"]（edge/mention/lexical）拆分。
        paths: dict[str, int] = {}
        for c in chunks:
            p = str(c.metadata.get("path") or _infer_path(c.metadata))
            paths[p] = paths.get(p, 0) + 1
        rows.append(
            {
                "q": case["q"],
                "ref": case["ref"],
                "pass": not missing,
                "covered": f"{covered}/{len(case['evidence'])}",
                "missing_groups": missing,
                "n_chunks": len(texts),
                "n_relevant": rel,
                "n_via_graph": n_graph,
                "paths": paths,
            }
        )
        tag = "PASS" if not missing else "FAIL"
        print(f"[{tag}] {case['q']}  覆盖组 {covered}/{len(case['evidence'])}｜相关块 {rel}/{len(texts)}｜路径 {paths}")
        if args.verbose:
            for c in chunks:
                print(f"      - ({c.metadata.get('via')}/{c.metadata.get('path')}) {c.text[:100]}")

    passed = sum(1 for r in rows if r["pass"])
    total_rel = sum(r["n_relevant"] for r in rows)
    total_chunks = sum(r["n_chunks"] for r in rows)
    graph_ratio = sum(r["n_via_graph"] for r in rows) / max(total_chunks, 1)
    total_paths: dict[str, int] = {}
    for r in rows:
        for k, v in r["paths"].items():
            total_paths[k] = total_paths.get(k, 0) + v
    print("\n==== 汇总（灰机标准 · 证据组命中） ====")
    print(f"用例 {len(CASES)}｜PASS {passed}｜FAIL {len(CASES) - passed}｜通过率 {passed / len(CASES):.0%}")
    print(f"证据块平均相关率 {total_rel / max(total_chunks, 1):.0%}｜图谱路径占比 {graph_ratio:.0%}"
          f"｜路径拆分 {total_paths}｜耗时 {time.time() - t0:.1f}s")
    for r in rows:
        if not r["pass"]:
            print(f"  [缺口] {r['q']} → 缺组 {r['missing_groups']}｜参考答案：{r['ref']}")

    out = ROOT / "data" / "knowledge" / "_audit" / "rag_huiji_eval_report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(
            {"standard": "灰机wiki(res1999.huijiwiki.com) 2026-09-12 核查",
             "top_chunks": args.top,
             # 记录实际命令行：旧报告落盘的 top_chunks=10 与脚本默认 5 不一致，
             # 事后无法判断这份数字到底是怎么跑出来的（复现性缺口）。
             "argv": sys.argv,
             "ran_at": time.strftime("%Y-%m-%d %H:%M:%S"),
             "path_counts": total_paths,
             "summary": {"cases": len(CASES), "passed": passed},
             "cases": rows},
            ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    print(f"[save] {out}")
    return 0 if passed == len(CASES) else 2


if __name__ == "__main__":
    raise SystemExit(main())
