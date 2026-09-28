# -*- coding: utf-8 -*-
"""85% 验证驱动：一次性跑完全部冷启动评测 + 汇总（进度实时可读）。

用法（由 pwsh 设置 env 后调用）：
  python -u scripts/_85_verify.py --tag k1
每个 tag 产出 reports/eval_{set}_{tag}.json，最后打印汇总表。

纪律：冷启动（每套题独立进程内全新加载）；不改题集；数字无论好坏如实报。
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
R = ROOT / "data/compendium_rag/reports"
PY = ROOT / ".venv/Scripts/python.exe"

SETS = [
    ("300cn", "data/knowledge/_audit/rag_testset_300_cn.json", "eval_300cn_lex_tiebreak.json"),
    ("blind", "data/knowledge/_audit/blind_v1/questions_strict.json", "eval_blind_lex_tiebreak.json"),
    ("gen120", "data/knowledge/_audit/rag_testset_gen_r1r2.json", "eval_gen_lex_on.json"),
]


def run_eval(tag: str, setname: str, spath: str) -> Path | None:
    out = R / f"eval_{setname}_{tag}.json"
    if out.exists():
        print(f"[skip] {out.name} 已存在", flush=True)
        return out
    print(f"\n{'='*80}\n[eval] {setname}  ->  {out.name}\n{'='*80}", flush=True)
    env = dict(os.environ)
    env["PYTHONPATH"] = "src"
    env["PYTHONIOENCODING"] = "utf-8"
    t0 = time.time()
    with open(out.with_suffix(".log"), "w", encoding="utf-8") as lf:
        p = subprocess.run([str(PY), "-u", "scripts/compendium_rag_eval300.py",
                            "--set", spath, "--top-k", "6", "--out", str(out)],
                           cwd=str(ROOT), env=env, stdout=lf,
                           stderr=subprocess.STDOUT)
    print(f"[eval] {setname} rc={p.returncode}  {time.time()-t0:.0f}s", flush=True)
    if not out.exists():
        print(f"[eval] 未产出 {out.name}；日志尾部：", flush=True)
        tail = out.with_suffix(".log").read_text(encoding="utf-8", errors="replace").splitlines()[-15:]
        for ln in tail:
            print("   " + ln, flush=True)
        return None
    return out


def summarize(f: Path, setname: str) -> dict:
    d = json.loads(f.read_text(encoding="utf-8"))
    rows = d["rows"]
    out = {"set": setname, "file": f.name}
    for mode in ("full", "graph_only"):
        sel = [r for r in rows if r.get("mode") == mode and r.get("answerable")]
        if not sel:
            continue
        h = sum(1 for r in sel if r.get("hit"))
        out[mode] = {"hits": h, "n": len(sel), "rate": round(h / len(sel), 4)}
    un = [r for r in rows if r.get("mode") == "full" and not r.get("answerable")]
    if un:
        out["unanswerable_hits"] = sum(1 for r in un if r.get("hit"))
        out["unanswerable_n"] = len(un)
    gr = [r for r in rows if r.get("mode") == "full" and r.get("answerable")]
    if gr:
        out["grounded"] = round(sum(1 for r in gr if r.get("grounded")) / len(gr), 4)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--ref", default="eval_300cn_lex_tiebreak.json,"
                                   "eval_blind_lex_tiebreak.json,eval_gen_lex_on.json")
    args = ap.parse_args()

    refs = args.ref.split(",")
    results = []
    for i, (setname, spath, _reffile) in enumerate(SETS):
        p = Path(spath)
        if not p.exists():
            print(f"[miss] 题集不存在: {spath}", flush=True)
            continue
        f = run_eval(args.tag, setname, spath)
        if f is None:
            continue
        results.append(summarize(f, setname))

    print(f"\n{'='*80}")
    print(f"汇总 @ tag={args.tag}   env: "
          f"LEX_WEIGHT={os.environ.get('CMPRAG_LEX_WEIGHT','(unset)')} "
          f"LEX_FIRST={os.environ.get('CMPRAG_LEX_FIRST','(unset)')} "
          f"RRF_K={os.environ.get('CMPRAG_RRF_K','(unset)')}")
    print("=" * 80)
    for r in results:
        for mode in ("full", "graph_only"):
            if mode in r:
                v = r[mode]
                flag = ""
                if mode == "full":
                    flag = "  PASS ✓" if v["rate"] >= 0.85 else f"  FAIL ✗ (需 +{max(0, -(-int(0.85*v['n'])-v['hits']))})"
                print(f"  {r['set']:8} {mode:11} {v['hits']:>4}/{v['n']:<4} = {v['rate']:.4f}{flag}")
        if "unanswerable_hits" in r:
            print(f"  {r['set']:8} {'unans命中':11} {r['unanswerable_hits']}/{r['unanswerable_n']}"
                  f"    grounded={r.get('grounded')}")

    (R / f"_85_verify_{args.tag}.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n-> {R / f'_85_verify_{args.tag}.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
