# -*- coding: utf-8 -*-
"""rrf_k 回归测试：默认零行为变更 + 启用后确实提升 + 确定性 + 安全线不恶化。

判据（先于结果）：
  R1 default   : 不设 CMPRAG_RRF_K 时，rrf_fuse 的 k 默认 = 60（历史行为）
  R2 equality  : k=60 的融合结果与"手工按历史公式复算"逐位一致
  R3 changed   : k=1 与 k=60 的排序**确实不同**（证明旋钮生效）
  R4 improves  : 从落盘工件复算，k=1 使 300cn 与盲测裸 hit@6 均提升
  R5 safety    : k=1 的 unanswerable 命中不高于 k=60，且 grounded 无违例
  R6 determin  : 同一输入重复计算结果一致（带显式次级键）
"""
from __future__ import annotations

import inspect
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from compendium_rag.config import get_settings                  # noqa: E402
from compendium_rag.retriever import GraphRetriever             # noqa: E402

R = ROOT / "data/compendium_rag/reports"
FAILS: list[str] = []


def check(label: str, cond: bool, detail: str = "") -> None:
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}{('  ' + detail) if detail else ''}")
    if not cond:
        FAILS.append(label)


print("=" * 76)
print("rrf_k 回归测试")
print("=" * 76)

# R1 默认值
sig = inspect.signature(GraphRetriever.retrieve)
d_ret = sig.parameters["rrf_k"].default
sig2 = inspect.signature(GraphRetriever.rrf_fuse)
d_fuse = sig2.parameters["k"].default
import os
saved = os.environ.pop("CMPRAG_RRF_K", None)
s_default = get_settings().rrf_k
if saved is not None:
    os.environ["CMPRAG_RRF_K"] = saved
check("R1 retrieve.rrf_k 默认 = 60", d_ret == 60, str(d_ret))
check("R1 rrf_fuse.k 默认 = 60", d_fuse == 60, str(d_fuse))
check("R1 Settings.rrf_k 默认 = 60（未设环境变量）", s_default == 60, str(s_default))

# R2 与历史公式逐位一致（k=60）
ch = {"lex": {"a": 3.0, "b": 2.0, "c": 1.0}, "vector": {"b": 5.0, "d": 1.0}}
out = GraphRetriever.rrf_fuse(dict(ch), k=60, weights={"lex": 1.0}, top_n=10)
manual = {}
for name in sorted(ch):
    for rank, (cid, _r) in enumerate(
            sorted(ch[name].items(), key=lambda kv: (-kv[1], kv[0])), start=1):
        manual[cid] = manual.get(cid, 0.0) + 1.0 / (60 + rank)
want = sorted(manual, key=lambda c: (-manual[c], c))
got = [e.chunk_id for e in out]
check("R2 k=60 与历史公式逐位一致", got == want, f"{got} vs {want}")

# R3 旋钮确实生效：构造一个**真实存在交叉点**的例子。
#   P 只在 lex 排第 1          -> 1/(k+1)
#   Q 在 lex 与 vector 都排第 5 -> 2/(k+5)
#   P > Q  <=>  (k+5) > 2(k+1)  <=>  k < 3
# 故 k=60 时 Q 胜、k=1 时 P 胜 —— 排序必然翻转，证明 k 真的在起作用。
ch2 = {"lex": {"P": 100.0, "a": 90.0, "b": 80.0, "c": 70.0, "Q": 60.0},
       "vector": {"h": 100.0, "i": 90.0, "j": 80.0, "k": 70.0, "Q": 60.0}}
o60 = [e.chunk_id for e in GraphRetriever.rrf_fuse(dict(ch2), k=60,
                                                   weights={"lex": 1.0}, top_n=10)]
o1 = [e.chunk_id for e in GraphRetriever.rrf_fuse(dict(ch2), k=1,
                                                  weights={"lex": 1.0}, top_n=10)]
check("R3 k=1 与 k=60 排序不同（旋钮生效）", o1 != o60, f"k1={o1} k60={o60}")
check("R3 交叉点如预期（k=60 → Q 先；k=1 → P 先）",
      o60[0] == "Q" and o1[0] == "P", f"k60[0]={o60[0]} k1[0]={o1[0]}")

# R6 确定性
again = [e.chunk_id for e in GraphRetriever.rrf_fuse(dict(ch), k=60,
                                                     weights={"lex": 1.0}, top_n=10)]
check("R6 确定性（重复计算一致）", again == got)

# R4/R5 从落盘工件复算
def cal(f: str):
    p = R / f
    if not p.exists():
        return None
    d = json.loads(p.read_text(encoding="utf-8"))
    rows = d["rows"]
    ans = [r for r in rows if r.get("mode") == "full" and r.get("answerable")]
    un = [r for r in rows if r.get("mode") == "full" and not r.get("answerable")]
    return (sum(1 for r in ans if r.get("hit")), len(ans),
            sum(1 for r in un if r.get("hit")), len(un),
            sum(1 for r in ans if r.get("grounded")))


for setname, f60, f1 in [("300cn", "eval_300cn_lex_tiebreak.json", "eval_300cn_k1.json"),
                         ("blind", "eval_blind_lex_tiebreak.json", "eval_blind_k1.json")]:
    a, b = cal(f60), cal(f1)
    if a is None or b is None:
        check(f"R4 {setname} 工件齐备", False, f"{f60} / {f1}")
        continue
    check(f"R4 {setname} k=1 提升", b[0] > a[0],
          f"{a[0]}/{a[1]}={a[0]/a[1]:.4f} -> {b[0]}/{b[1]}={b[0]/b[1]:.4f}")
    check(f"R4 {setname} k=1 ≥0.85", b[0] / b[1] >= 0.85, f"{b[0]/b[1]:.4f}")
    check(f"R5 {setname} unanswerable 不恶化", b[2] <= a[2], f"{a[2]} -> {b[2]}")
    check(f"R5 {setname} grounded 无违例", b[4] == b[1], f"{b[4]}/{b[1]}")

print()
if FAILS:
    print(f"结果：{len(FAILS)} 项 FAIL -> {FAILS}")
    raise SystemExit(1)
print("结果：全部 PASS ✓")
raise SystemExit(0)
