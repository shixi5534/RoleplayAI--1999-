# -*- coding: utf-8 -*-
"""候选生成量消融矩阵 —— 唯一还没被覆盖过的维度。

为什么做这个：
    scripts/diag_recall_cause.py 发现「请求 top_chunks=30 时实际最多只返回 28 块
    （中位 22）」⇒ top_chunks 加深不了候选池，池深由各通道自己的配置决定。
    而此前所有消融（weight_semantic / max_hops / ppr_node_specificity / max_edges）
    要么改的是融合权重，要么是把候选**变小**，从没试过把池子**变大**。
    D 桶 60 题（20%）「连候选池都没进」正卡在这里。

做法：
    串行跑批（并发会污染延迟口径），每轮用环境变量注入配置覆盖，不改 .env。
    判定以 **inject_pass 为准**（项目既定纪律：strict_pass 可被多返回块灌水），
    同时记录 recall / 返回块数 / 延迟，便于判断候选变多是否真带来质量。

用法：
    .venv/Scripts/python.exe -X utf8 scripts/ablate_candidate_volume.py
    .venv/Scripts/python.exe -X utf8 scripts/ablate_candidate_volume.py --only sem_top10
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = str(ROOT / ".venv" / "Scripts" / "python.exe")
EVAL = str(ROOT / "scripts" / "eval_plot_rag.py")
AUDIT = ROOT / "data" / "knowledge" / "_audit"
AB = AUDIT / "ablation"
TESTSET = str(AUDIT / "rag_testset_300_clean.json")

# (名称, 环境变量覆盖, 说明)
STEPS: list[tuple[str, dict[str, str], str]] = [
    ("base", {}, "生产配置（参照轮）"),
    ("sem_top10", {"ROLEPLAY_PLOT_SEMANTIC_TOP": "10"}, "语义通道 5→10"),
    ("sem_top20", {"ROLEPLAY_PLOT_SEMANTIC_TOP": "20"}, "语义通道 5→20"),
    ("men_pe10", {"ROLEPLAY_PLOT_MENTION_PER_ENTITY": "10"}, "每实体提及块 5→10"),
    ("men_cap20", {"ROLEPLAY_PLOT_MENTION_TOTAL_CAP": "20"}, "提及总上限 10→20"),
    ("edges20", {"ROLEPLAY_PLOT_MAX_EDGES": "20"}, "参与检索边 10→20"),
    ("chap_top6", {"ROLEPLAY_PLOT_CHAPTER_TOP": "6"}, "篇章池取块 3→6"),
    ("link_top6", {"ROLEPLAY_PLOT_SEMANTIC_LINK_TOP": "6"}, "语义链接实体 3→6"),
    ("combo_s_m", {
        "ROLEPLAY_PLOT_SEMANTIC_TOP": "10",
        "ROLEPLAY_PLOT_MENTION_PER_ENTITY": "10",
        "ROLEPLAY_PLOT_MENTION_TOTAL_CAP": "20",
    }, "语义+提及三者叠加"),
]

KEYS = ("strict_pass", "inject_pass", "recall", "mrr",
        "avg_returned_chunks", "latency_p50_ms", "latency_p95_ms", "ceiling_cases")


def read_sum(name: str) -> dict | None:
    p = AB / f"vol_{name}.json"
    if not p.is_file():
        return None
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
        s = d.get("summary") or {}
        return {k: s.get(k) for k in KEYS}
    except Exception:  # noqa: BLE001
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="", help="只跑某一步（名字见 STEPS）")
    ap.add_argument("--skip-done", action="store_true", help="已有报告则跳过")
    args = ap.parse_args()

    AB.mkdir(parents=True, exist_ok=True)
    log: list[str] = []

    def say(*a):
        line = " ".join(str(x) for x in a)
        log.append(line)
        print(line, flush=True)

    rc_all = 0
    for name, env_over, desc in STEPS:
        if args.only and args.only != name:
            continue
        out = AB / f"vol_{name}.json"
        if args.skip_done and out.is_file():
            say(f"[skip] {name}（已有报告）")
            continue
        say("=" * 70)
        say(f"[step] {name}  {desc}  ({time.strftime('%H:%M:%S')})")
        env = dict(os.environ, **env_over) if env_over else None
        cmd = [PY, "-X", "utf8", EVAL, "--quiet", "--no-trace",
               "--testset", TESTSET, "--out", str(out)]
        t0 = time.time()
        p = subprocess.run(cmd, cwd=str(ROOT), env=env)
        say(f"[step] {name} 退出码 {p.returncode}｜耗时 {time.time() - t0:.0f}s")
        rc_all = rc_all or p.returncode

    # 汇总
    say()
    say("=" * 88)
    say(f"{'配置':<12}{'inject':>9}{'Δinject':>9}{'strict':>9}{'recall':>9}"
        f"{'返回块':>8}{'p50':>8}{'p95':>8}")
    say("-" * 88)
    base = read_sum("base")
    for name, _env, desc in STEPS:
        s = read_sum(name)
        if s is None:
            say(f"{name:<12}{'— 无报告 —':>40}")
            continue
        inj = s.get("inject_pass") or 0.0
        st = s.get("strict_pass") or 0.0
        rc = s.get("recall") or 0.0
        di = (inj - (base.get("inject_pass") or 0.0)) if base and name != "base" else 0.0
        say(f"{name:<12}{inj:>9.4f}{di:>+9.4f}{st:>9.4f}{rc:>9.4f}"
            f"{(s.get('avg_returned_chunks') or 0):>8.2f}"
            f"{(s.get('latency_p50_ms') or 0):>8.0f}"
            f"{(s.get('latency_p95_ms') or 0):>8.0f}")
    say("-" * 88)
    say("注：判定以 inject_pass 为准（strict_pass 可被「多返回块」灌水）。")
    say("    延迟必须与 base 同批次比较——不同批次会受 ollama 预热影响（历史教训）。")
    say("=" * 88)

    (AB / "vol_summary.txt").write_text("\n".join(log), encoding="utf-8")
    return rc_all


if __name__ == "__main__":
    raise SystemExit(main())
