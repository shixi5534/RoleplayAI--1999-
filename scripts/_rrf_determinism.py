# -*- coding: utf-8 -*-
"""确定性检验：rrf_fuse 的两处 sorted 无显式次级键，是否会在 **PYTHONHASHSEED**
或 channel 构建顺序变化下产生不同排序？

背景：#39 Phase 2 已证实「稳定排序 + 无次级键 = 依赖插入序」，并修好了 link()。
rrf_fuse（retriever.py:462/468）是同类写法：
  462: sorted(scored.items(), key=lambda kv: -kv[1])
  468: sorted(agg.values(), key=lambda e: -e.score)
逐一检验：同一查询、同一输入下，多次调用 / 不同 hashseed 是否给出同一 chunk 序列。
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CHILD = r'''
import json, sys
from pathlib import Path
sys.path.insert(0, r"{src}")
from compendium_rag import pipeline as P
from compendium_rag.config import get_settings
s = get_settings()
kb = P.load_kb(s)
r = kb.retriever
qs = ["洞穴的囚徒篇里牙仙也登船照看乘客，她的英文名是什么？",
      "海因里希效忠的重塑之手首领是谁？",
      "苏菲亚与阿尼姆斯在南极事件中复活了谁？",
      "维尔汀在第一防线学校时是多少岁策划学生出逃的？"]
out = {{}}
for q in qs:
    res = r.retrieve(q, None, top_k=6, lex_weight=1.0)
    out[q[:12]] = [e.chunk_id for e in res.evidence]
print(json.dumps(out, ensure_ascii=False))
'''


def run(seed: str) -> dict:
    code = CHILD.format(src=str(ROOT / "src"))
    p = subprocess.run([str(ROOT / ".venv/Scripts/python.exe"), "-c", code],
                       capture_output=True, cwd=ROOT,
                       env={**__import__("os").environ,
                            "PYTHONHASHSEED": seed,
                            "PYTHONIOENCODING": "utf-8"})
    txt = p.stdout.decode("utf-8", "replace").strip().splitlines()
    if not txt:
        print("[stderr]", p.stderr.decode("utf-8", "replace")[:400])
        raise SystemExit(1)
    return json.loads(txt[-1])


def main() -> int:
    base = run("0")
    print("[base hashseed=0] 4 题 evidence 序列已取得")
    ok = True
    for seed in ("1", "7", "12345"):
        other = run(seed)
        same = other == base
        ok &= same
        print(f"  hashseed={seed}: {'一致' if same else '**不一致**'}")
        if not same:
            for k in base:
                if base[k] != other.get(k):
                    print(f"    {k}: {base[k]} vs {other.get(k)}")
    # 同 seed 重复调用（捕获调用内状态漂移）
    r1 = run("0")
    print(f"  同 seed 重复调用: {'一致' if r1 == base else '**不一致**'}")
    ok &= (r1 == base)
    print(f"\n判定: {'确定性成立' if ok else '**存在不确定性**'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
