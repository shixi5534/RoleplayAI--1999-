# -*- coding: utf-8 -*-
"""重复基线 + McNemar 配对检验（评估口径 P0）。

解决什么问题
    「34% → 30% 算不算退化」在 300 题规模上只是 12 题（1 题 = 0.33 pt），
    单次运行无法判定。本工具做两件事：
      1. 同一配置**重复跑 N 次**（每轮独立进程），给出指标方差与逐题翻转数
      2. 两组配置做 **McNemar 配对检验**（小评估集该用这个，而不是比裸差值）

顺带回答一个更基础的问题：**这条管线到底是不是确定性的？**
    检索链路理论上确定（嵌入/BM25/PPR 都无采样），但 Python 字符串哈希默认随机化，
    代码里任何 set 迭代都可能让不同进程产生不同顺序 ⇒ 需要实测。
    · 若方差为 0 ⇒ 以后不必重复跑，只需 McNemar 管小样本
    · 若方差 > 0 ⇒ 得到噪声地板，任何 Δ 必须先超过它才算信号

用法
    # 跑 3 次基线
    .venv/Scripts/python.exe -X utf8 scripts/eval_repeat.py --tag base --repeat 3
    # 带配置覆盖跑 3 次
    .venv/Scripts/python.exe -X utf8 scripts/eval_repeat.py --tag exp --repeat 3 \
        --set ROLEPLAY_PLOT_SEMANTIC_LINK_MIN=0.35
    # 两组做 McNemar
    .venv/Scripts/python.exe -X utf8 scripts/eval_repeat.py --mcnemar base exp
"""
from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = str(ROOT / ".venv" / "Scripts" / "python.exe")
EVAL = str(ROOT / "scripts" / "eval_plot_rag.py")
AUDIT = ROOT / "data" / "knowledge" / "_audit"
REP = AUDIT / "repeat"
TESTSET = str(AUDIT / "rag_testset_300_clean.json")
LOG = AUDIT / "_eval_repeat.txt"
KEYS = ("inject_pass", "strict_pass", "recall", "mrr", "latency_p50_ms")

_out: list[str] = []


def say(*a):
    line = " ".join(str(x) for x in a)
    _out.append(line)
    print(line, flush=True)


def load_run(tag: str, i: int) -> dict | None:
    p = REP / f"{tag}_{i}.json"
    if not p.is_file():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def per_item(report: dict) -> dict[str, dict]:
    """逐题结果：{id: {inject, strict}}。容忍字段名差异。"""
    out: dict[str, dict] = {}
    for it in report.get("items") or []:
        qid = str(it.get("id") or it.get("qid") or it.get("q") or "")
        if not qid:
            continue
        out[qid] = {
            "inject": bool(it.get("inject_pass")),
            "strict": bool(it.get("strict_pass")),
        }
    return out


def mcnemar_exact(b: int, c: int) -> float:
    """双侧精确 McNemar（二项检验）。b/c = 两组的不一致配对数。"""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) * (0.5 ** n)
    return min(1.0, 2.0 * tail)


def cmd_run(tag: str, repeat: int, env_over: dict[str, str], skip_done: bool) -> int:
    REP.mkdir(parents=True, exist_ok=True)
    say("=" * 78)
    say(f"重复基线｜tag={tag}｜repeat={repeat}｜覆盖={env_over or '无'}")
    say("=" * 78)
    for i in range(1, repeat + 1):
        out = REP / f"{tag}_{i}.json"
        if skip_done and out.is_file():
            say(f"[skip] 第 {i} 次已完成")
            continue
        env = dict(os.environ, **env_over) if env_over else None
        cmd = [PY, "-X", "utf8", EVAL, "--quiet", "--no-trace",
               "--testset", TESTSET, "--out", str(out)]
        t0 = time.time()
        p = subprocess.run(cmd, cwd=str(ROOT), env=env)
        say(f"[run] 第 {i} 次 退出码 {p.returncode}｜{time.time() - t0:.0f}s")

    runs = [load_run(tag, i) for i in range(1, repeat + 1)]
    runs = [r for r in runs if r]
    if not runs:
        say("[FATAL] 没有可用结果")
        return 1

    say()
    say("-" * 78)
    say(f"{'运行':<8}" + "".join(f"{k:>16}" for k in KEYS))
    per_key: dict[str, list[float]] = {k: [] for k in KEYS}
    for i, r in enumerate(runs, 1):
        s = r.get("summary") or {}
        vals = [float(s.get(k) or 0.0) for k in KEYS]
        for k, v in zip(KEYS, vals):
            per_key[k].append(v)
        say(f"{'第' + str(i) + '次':<8}" + "".join(f"{v:>16.4f}" for v in vals))
    say("-" * 78)
    say(f"{'均值':<8}" + "".join(f"{sum(per_key[k]) / len(per_key[k]):>16.4f}" for k in KEYS))
    say(f"{'极差':<8}" + "".join(
        f"{max(per_key[k]) - min(per_key[k]):>16.4f}" for k in KEYS))
    say("=" * 78)

    # 逐题翻转：不同运行之间有多少题结论不一致
    items = [per_item(r) for r in runs]
    common = set(items[0])
    for m in items[1:]:
        common &= set(m)
    flips = {k: 0 for k in ("inject", "strict")}
    for qid in common:
        for k in flips:
            vals = {m[qid][k] for m in items if qid in m}
            if len(vals) > 1:
                flips[k] += 1
    say()
    say(f"逐题一致性（{len(common)} 题）：")
    for k in flips:
        verdict = "确定性" if flips[k] == 0 else "**存在不确定性**"
        say(f"  {k:<8}翻转 {flips[k]:>3} 题 ⇒ {verdict}")
    say()
    if all(v == 0 for v in flips.values()):
        say("⇒ 结论：管线在本机是**确定性的**，重复跑不会产生方差。")
        say("  后续判定只需 McNemar 管小样本，无需再跑多次。")
    else:
        say("⇒ 结论：存在非确定性（多半来自 set 迭代 + Python 字符串哈希随机化），")
        say("  上面「极差」即噪声地板，任何 Δ 必须先超过它才算信号。")
    return 0


def cmd_mcnemar(tag_a: str, tag_b: str) -> int:
    ra = load_run(tag_a, 1)
    rb = load_run(tag_b, 1)
    if not ra or not rb:
        say("[FATAL] 缺少某一组的运行结果")
        return 1
    ia, ib = per_item(ra), per_item(rb)
    common = sorted(set(ia) & set(ib))
    if not common:
        say("[FATAL] 没有可比对的共同题目")
        return 1

    say("=" * 78)
    say(f"McNemar 配对检验｜A={tag_a} vs B={tag_b}｜配对 {len(common)} 题")
    say("=" * 78)
    for metric in ("inject", "strict"):
        both = only_a = only_b = neither = 0
        for qid in common:
            a, b = ia[qid][metric], ib[qid][metric]
            if a and b:
                both += 1
            elif a and not b:
                only_a += 1
            elif b and not a:
                only_b += 1
            else:
                neither += 1
        n = len(common)
        pa, pb = (both + only_a) / n, (both + only_b) / n
        p = mcnemar_exact(only_a, only_b)
        say()
        say(f"[{metric}_pass]")
        say(f"  两组都过 {both:>4}｜只 A 过 {only_a:>4}｜只 B 过 {only_b:>4}｜都不过 {neither:>4}")
        say(f"  A={pa:.4f}  B={pb:.4f}  Δ={(pb - pa):+.4f}（{(only_b - only_a):+d} 题）")
        say(f"  不一致配对数 b+c = {only_a + only_b}｜McNemar 双侧 p = {p:.4f}")
        if p < 0.05:
            say(f"  ⇒ **显著**（p<0.05）：差异不太可能是噪声")
        else:
            say(f"  ⇒ 不显著（p≥0.05）：**不能判定为真实差异**")
    say("=" * 78)
    say("注：\"只 A 过\" = A 显著优于 B 的题数；两值接近 ⇒ 多半是随机波动。")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="base")
    ap.add_argument("--repeat", type=int, default=3)
    ap.add_argument("--set", nargs="*", default=[], help="KEY=VALUE 形式的环境变量覆盖")
    ap.add_argument("--skip-done", action="store_true")
    ap.add_argument("--mcnemar", nargs=2, default=None, metavar=("TAG_A", "TAG_B"))
    args = ap.parse_args()

    try:
        if args.mcnemar:
            rc = cmd_mcnemar(args.mcnemar[0], args.mcnemar[1])
        else:
            env_over: dict[str, str] = {}
            for kv in args.set:
                if "=" in kv:
                    k, v = kv.split("=", 1)
                    env_over[k.strip()] = v.strip()
            rc = cmd_run(args.tag, args.repeat, env_over, args.skip_done)
    except BaseException:  # noqa: BLE001
        import traceback
        _out.append("\n[TRACEBACK]\n" + traceback.format_exc())
        rc = 1
    LOG.write_text("\n".join(_out), encoding="utf-8")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
