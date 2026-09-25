# -*- coding: utf-8 -*-
"""15101 闭环确认 + 本会话归并声明实测核验（对照 handoff 教训）。

用法：在 rebuild 之后运行，用 GraphStore.resolve() 实测每一条
本会话声称的归并（第 5 会话正是在这一步发现 3 处未落盘）。
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent / "src"))

# ── 1) 15101 是否 61 块全入 cache ──
cache_dir = ROOT / "cache"
cache_keys = {p.stem for p in cache_dir.rglob("*.json")}
chunks = json.loads((ROOT / "chunks.json").read_text(encoding="utf-8"))["chunks"]
c15101 = [c for c in chunks if c["doc_id"].startswith("activity__15101")]
print(f"15101 总块数 = {len(c15101)}")

# cache key 是 24 位 cache_key，需从 dump 反查
key2chunk = {}
for dp in sorted(ROOT.glob("_dump*.txt")):
    for line in dp.read_text(encoding="utf-8-sig").splitlines():
        if line.strip():
            o = json.loads(line)
            key2chunk[o["key"]] = o["chunk_id"]

done = [cid for k, cid in key2chunk.items()
        if k in cache_keys and cid.startswith("activity__15101")]
print(f"15101 已入 cache = {len(done)}")
missing = [c["chunk_id"] for c in c15101
           if c["chunk_id"] not in set(done)]
if missing:
    print("  ⚠ 未入 cache:")
    for m in missing:
        print(f"    {m}")
else:
    print("  ✅ 15101 全部 61 块已入 cache → 该版闭环")

# ── 2) 归并声明实测 ──
print()
print("=== 本会话归并声明实测（GraphStore.resolve）===")
from compendium_rag.graph_store import GraphStore  # noqa: E402

g = GraphStore.load(ROOT / "graph.json")

# (写法, 期望 canonical, 说明)
CLAIMS = [
    ("幽灵蘑菇", "幽灵蘑菇", "自建（aliases 含 引路者巢状类脐菇）"),
    ("引路者巢状类脐菇", "幽灵蘑菇", "175 归并声明"),
    ("像素鸸鹋", "波拉比", "176 归并声明"),
    ("达利阿拉伯", "哒哒达利", "178 归并声明"),
    ("兔子小姐", "芭妮芭妮", "178 归并声明"),
    ("叮咚快报", "《澳大利亚叮当快报》", "178 归并声明"),
    ("宽檐帽", "宽檐帽先生", "179 归并声明"),
    ("小火", "可燃点", "177 归并声明（前世名）"),
]

ok = 0
for name, expect, note in CLAIMS:
    got = g.resolve(name)
    mark = "✅" if got == expect else "❌"
    if got == expect:
        ok += 1
    print(f"  {mark} resolve({name!r}) -> {got!r}  (期望 {expect!r})｜{note}")
print(f"\n  {ok}/{len(CLAIMS)} 条归并声明实测通过")

# ── 3) 关键复用节点是否真的存在且被接边 ──
print()
print("=== 15101 关键实体在图中的落点 ===")
for n in ["可燃点", "沙丝绒", "爱兹拉", "维尔汀", "和平乌鲁", "火苗",
          "马科尔", "宽檐帽先生", "波拉比", "哒哒达利",
          "乌卢鲁", "乌卢鲁运动会", "乌卢鲁运动场", "乌卢鲁岩护卫队",
          "轮回者", "本耶普"]:
    e = g.entities.get(n)
    if not e:
        print(f"  ❌ {n}: 不在图中")
        continue
    out_ = len(g.out_edges(n))
    ne = len(g.neighbors(n))
    print(f"  ✅ {n:16s} {e.type:4s} mentions={e.mentions:4d} "
          f"out={out_:3d} neighbors={ne:3d} aliases={e.aliases}")
