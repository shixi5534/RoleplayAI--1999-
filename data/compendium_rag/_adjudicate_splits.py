# -*- coding: utf-8 -*-
"""rebuild 后用 resolve() 实测裁定并发重复抽取造成的「分裂」名单。

用法:
  python data/compendium_rag/_adjudicate_splits.py                      # 读 _splits_snapshot.txt
  python data/compendium_rag/_adjudicate_splits.py --fresh 247 610      # 现场跑碰撞审计生成快照再裁定
只读: 不写 graph.json / cache / 生成器。

分类 A/B/C/D **互斥且合计必须等于全部配对数**(有断言兜底)。
⚠ 第 19 会话修掉的假阳性闸:早先枚举配对时先筛了 `a in names and b in names`,
于是「已被 resolve 并到同一节点(B)」与「一侧根本不在图里(C)」两类**永远是 0**，
打印出来的「共 0 对」是筛选条件的副产品而非实测结论；同时只取 `len(ks)==2` 的块，
三个及以上号位同抽的块被**静默跳过**。现改为全量两两比对后再分类。
"""
import ast
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent / "src"))
from compendium_rag.graph_store import GraphStore  # noqa: E402

if sys.argv[1:2] == ["--fresh"]:
    import os
    cp = subprocess.run(
        [sys.executable, str(ROOT / "_audit_global_key_collisions.py"),
         sys.argv[2], sys.argv[3]],
        cwd=str(ROOT.parent.parent), capture_output=True, text=True, encoding="utf-8",
        env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    if cp.returncode != 0:
        raise SystemExit(f"!! 碰撞审计退出码 {cp.returncode}:{cp.stderr[-400:]}")
    txt = cp.stdout
    snap = ROOT / "_splits_snapshot.txt"
    snap.write_text(txt, encoding="utf-8")
    print(f"[fresh] 快照已重写 {snap.name}({len(txt)} 字符)← 碰撞审计 {sys.argv[2]}–{sys.argv[3]}")
else:
    snap = ROOT / (sys.argv[1] if len(sys.argv) > 1 else "_splits_snapshot.txt")
rows = []
for line in snap.read_text(encoding="utf-8").splitlines():
    m = re.match(r"^\s*[0-9a-f]{24}\s+批\[([0-9, ]+)\]\s+存活\S+\s+独有:(\{.*\})\s*$", line)
    if m:
        rows.append((m.group(1).strip(), ast.literal_eval(m.group(2))))

g = GraphStore.load(ROOT / "graph.json")
names = {e.name for e in g.entities.values()}


def canon(n):
    r = g.resolve(n)
    return r if r else (n if n in names else None)


uniq_all = sorted({x for _, d in rows for v in d.values() for x in v})
present = [n for n in uniq_all if n in names]
print(f"快照分裂块 {len(rows)}｜独有名 {len(uniq_all)}｜其中在图中成节点 {len(present)}")

pairs = []
n_split_rows = 0
for _, d in rows:
    ks = list(d)
    if len(ks) < 2:
        continue
    n_split_rows += 1
    # 3 个及以上号位同抽一块时也要两两比对,不能只看前两组
    for i in range(len(ks)):
        for j in range(i + 1, len(ks)):
            for a in d[ks[i]]:
                for b in d[ks[j]]:
                    if a != b:
                        pairs.append((a, b))

seen = set()
allpairs = []
for a, b in pairs:
    key = frozenset((a, b))
    if key in seen:
        continue
    seen.add(key)
    allpairs.append((a, b))


def lcs(a, b):
    best = 0
    for i in range(len(a)):
        for j in range(i + 2, len(a) + 1):
            if j - i > best and a[i:j] in b:
                best = j - i
    return best


def same_ref(a, b):
    """同指判据:类型一致 且 互为包含 / 共享 ≥2 字词核(否则是各自独立实体)。"""
    if g.entities[a].type != g.entities[b].type:
        return False
    if a in b or b in a:
        return True
    return lcs(a, b) >= 2 and (lcs(a, b) >= min(len(a), len(b)) - 4)


# 单趟分类,四类互斥且必须覆盖全部配对(漏分支会被这行断言抓出)
A, B, C, D = [], [], [], []
for a, b in allpairs:
    ca, cb = canon(a), canon(b)
    if ca is None or cb is None:
        C.append((a, b, ca, cb))
    elif ca == cb:
        B.append((a, b, ca, cb))
    elif same_ref(ca, cb):
        A.append((a, b, ca, cb))
    else:
        D.append((a, b, ca, cb))
assert len(A) + len(B) + len(C) + len(D) == len(allpairs), "分类未覆盖全部配对"

print("\n=== A. 两侧独有名同时成节点、类型一致且词核重叠 → 真候选 ===")
a_canon = sorted({tuple(sorted((x[2], x[3]))) for x in A})
for x, y in a_canon:
    ea, ebb = g.entities[x], g.entities[y]
    print(f"  {x}({ea.type},m={ea.mentions}) ↔ {y}({ebb.type},m={ebb.mentions})")
n_a = len(a_canon)
print(f"  小计 {n_a} 对(canonical 去重)/ 原始 {len(A)} 对")

print("\n=== B. resolve 已并到同一节点（虚警，无需改数据）===")
print(f"  共 {len(B)} 对（示例 ≤15）")
for a, b, ca, _ in B[:15]:
    print(f"    {a} ↔ {b} -> {ca}")

print("\n=== C. 一侧或两侧根本不在图中（死草稿，天然无冲突）===")
print(f"  共 {len(C)} 对（示例 ≤15,✓=成节点 ✗=不在图）")
for a, b, ca, cb in C[:15]:
    print(f"    {a}{'✓' if ca else '✗'} ↔ {b}{'✓' if cb else '✗'}")

print("\n=== D. 两侧均成节点、各自独立(类型或词核不重叠) → 预期分建 ===")
print(f"  共 {len(D)} 对（示例 ≤15）")
for a, b, ca, cb in D[:15]:
    print(f"    {a}→{ca}({g.entities[ca].type}) ↔ {b}→{cb}({g.entities[cb].type})")

# 口径:A 因去重到 canonical 而基数不同,B/C/D 与 A 互斥且合计=全部配对
print(f"\n口径:参与两两比对的分裂块 {n_split_rows}/{len(rows)}｜配对 {len(allpairs)} 对"
      f"｜A={len(A)}(去重后 {n_a}) B={len(B)} C={len(C)} D={len(D)}"
      f"｜合计 {len(A) + len(B) + len(C) + len(D)}")
print("判定:A 类逐对需 §10 裁定(合并或保留);B/C/D 不判失败。")
