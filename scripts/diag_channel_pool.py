# -*- coding: utf-8 -*-
"""通道拆解：A 类 67 题到底该由哪条通道救（P1 第 1 步）。

要回答的问题
    上一轮归因定调：inject 失分 114 题里 **A 类 67 题（58.8%）「正例不在候选池」**，
    落在查询侧与索引侧。但"不在池"有两个完全不同的成因，处置方式相反：
      · **查询不匹配**：任何通道都捞不到 ⇒ 只能改查询（改写/词典/实体链接）
      · **通道覆盖不足**：某条通道本可以捞到，但被别的通道挤掉或该通道没开
        ⇒ 改通道配置即可，成本极低

做法（单变量：每次只关一条通道，看 A 类题的池命中率变化）
    配置由环境变量控制，本脚本读取当前环境，不需要改代码：
      base            现状四通道
      no_semantic     ROLEPLAY_PLOT_SEMANTIC_ENABLED=false
      no_graph        ROLEPLAY_PLOT_GRAPH_ENABLED=false   （= 纯向量）
      no_chapter      ROLEPLAY_PLOT_CHAPTER_ROUTING=false
      lexical_always  ROLEPLAY_PLOT_LEXICAL_ALWAYS=true   （BM25 常开）

判定
    对 A 类 67 题统计「候选池命中」：
      group_any_in_pool ：任一组关键词在池中出现（弱）
      full_in_pool      ：存在单块覆盖全部证据组（强，= A 类的定义）
    若某个配置让 full_in_pool 明显上升 ⇒ 该通道是瓶颈，配置可救；
    若所有配置都不动 ⇒ **查询不匹配**，必须改查询侧。

用法
    .venv/Scripts/python.exe -X utf8 scripts/diag_channel_pool.py --tag base
    # 换配置：先 set 环境变量再跑（PowerShell）：
    #   $env:ROLEPLAY_PLOT_SEMANTIC_ENABLED="false"
    #   .venv/Scripts/python.exe -X utf8 scripts/diag_channel_pool.py --tag no_semantic
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import eval_plot_rag as E  # noqa: E402
from roleplay.config import get_settings  # noqa: E402
from roleplay.core.knowledge.factory import build_plot_registry  # noqa: E402

AUDIT = ROOT / "data" / "knowledge" / "_audit"
TESTSET = AUDIT / "rag_testset_300_clean.json"
RANK = AUDIT / "positive_rank.json"
LOG = AUDIT / "_channel_pool.txt"
HB = AUDIT / "_channel_pool_heartbeat.txt"
POOL = 100


def beat(m: str) -> None:
    with HB.open("a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%H:%M:%S')} {m}\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="base")
    ap.add_argument("--lf", type=int, default=-1,
                    help="词法兜底条数；-1 = 用生产设置（必须用生产值，否则词法通道被掐掉）")
    ap.add_argument("--only-a", action="store_true",
                    help="只探测 A 类（快，用于通道拆解决策）")
    ap.add_argument("--out-suffix", default="")
    args = ap.parse_args()

    out: list[str] = []
    HB.write_text(f"start tag={args.tag} {time.strftime('%H:%M:%S')}\n", encoding="utf-8")

    def p(*a):
        line = " ".join(str(x) for x in a)
        out.append(line)
        print(line, flush=True)

    s = get_settings()
    cfg = {
        "graph_enabled": getattr(s, "plot_graph_enabled", None),
        "semantic_enabled": getattr(s, "plot_semantic_enabled", None),
        "chapter_routing": getattr(s, "plot_chapter_routing", None),
        "lexical_always": getattr(s, "plot_lexical_always", None),
        "semantic_top": getattr(s, "plot_semantic_top", None),
    }

    cases = json.loads(TESTSET.read_text(encoding="utf-8"))
    retr = build_plot_registry(s).get("wu_ming_zhe")
    by_hash = {c.hash: c.text for c in retr.corpus.chunks}
    # ⚠️ 必须用生产 lexical_fallback：传 0 会把词法通道整个掐掉，
    #    那样测「BM25 常开」必然是恒等（自己的前置 bug，已踩过一次）
    lf = int(getattr(s, "plot_lexical_fallback", 2)) if args.lf < 0 else args.lf

    # A 类题号
    a_ids: set[str] = set()
    if RANK.is_file():
        for r in json.loads(RANK.read_text(encoding="utf-8")):
            if r.get("verdict") == "A_不在候选池":
                a_ids.add(str(r["id"]))
    work = [c for c in cases if str(c["id"]) in a_ids] if args.only_a else cases

    p("=" * 84)
    p(f"通道拆解｜tag={args.tag}｜配置 {cfg}")
    p(f"A 类（不在候选池）{len(a_ids)} 题｜探测 {len(work)} 题｜池探测 top={POOL}"
      f"｜lexical_fallback={lf}{'（生产值）' if args.lf < 0 else '（覆盖）'}")
    p("=" * 84)

    def probe_all() -> tuple[list[dict], dict]:
        """只探测一遍全量，再切出 A 类（A ⊂ 全量，探测两遍是浪费）。"""
        rows: list[dict] = []
        for i, item in enumerate(work):
            if i % 25 == 0:
                beat(f"{args.tag} case {i}/{len(work)}")
            groups = item.get("evidence") or []
            if not groups:
                continue
            pool = retr.retrieve(item["q"], top_chunks=POOL, lexical_fallback=lf)
            texts = [by_hash.get(E.chunk_hash(c.text), "") for c in pool]
            any_hit = any(any(kw in t for t in texts)
                          for g in groups for kw in (g if isinstance(g, list) else [g]))
            full_hit = any(all(any(kw in t for kw in
                                   (g if isinstance(g, list) else [g])) for g in groups)
                           for t in texts)
            rows.append({"id": str(item["id"]), "pool": len(pool),
                         "group_any": any_hit, "full": full_hit})

        def agg(rs: list[dict]) -> dict:
            n = len(rs) or 1
            return {"n": len(rs),
                    "group_any": sum(r["group_any"] for r in rs),
                    "full": sum(r["full"] for r in rs),
                    "pool_sum": sum(r["pool"] for r in rs)}

        return rows, agg(rows)

    t0 = time.time()
    rows, rall = probe_all()
    ra = {
        "n": sum(1 for r in rows if r["id"] in a_ids),
        "group_any": sum(1 for r in rows if r["id"] in a_ids and r["group_any"]),
        "full": sum(1 for r in rows if r["id"] in a_ids and r["full"]),
        "pool_sum": sum(r["pool"] for r in rows if r["id"] in a_ids),
    }
    beat(f"{args.tag} 完成")

    def line(label: str, r: dict):
        n = r["n"] or 1
        p(f"  {label:<16}{r['n']:>6}{r['group_any'] / n:>12.1%}{r['full'] / n:>12.1%}"
          f"{r['pool_sum'] / n:>10.1f}")

    p()
    p(f"  {'子集':<16}{'题数':>6}{'任一组在池':>12}{'单块全覆盖':>12}{'平均池深':>10}")
    p("  " + "-" * 58)
    line(f"A 类（{ra['n']} 题）", ra)
    if not args.only_a:
        line(f"全量（{rall['n']} 题）", rall)
    p("  " + "-" * 58)
    p(f"  tag={args.tag}｜lexical_fallback={lf}｜耗时 {(time.time() - t0) / 60:.1f} min")

    # 追加式落盘：每个 tag 一段，便于横向对比
    with LOG.open("a", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    fname = f"channel_pool_{args.tag}{args.out_suffix}.json"
    (AUDIT / fname).write_text(json.dumps({
        "tag": args.tag, "config": cfg, "lexical_fallback": lf,
        "only_a": args.only_a,
        "a_class": ra, "all": (None if args.only_a else rall),
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except BaseException:  # noqa: BLE001
        with LOG.open("a", encoding="utf-8") as f:
            f.write("\n[TRACEBACK]\n" + traceback.format_exc())
        raise
