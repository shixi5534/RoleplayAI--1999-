# -*- coding: utf-8 -*-
"""第 9 会话验证：20101 闭环 + 命名红线 + 归并声明实测 + c4 语料核验。"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent / "src"))
from compendium_rag.config import get_settings              # noqa: E402
from compendium_rag.pipeline import load_chunks             # noqa: E402
from compendium_rag.extract import PROMPT_VERSION, cache_key  # noqa: E402
from compendium_rag.graph_store import GraphStore           # noqa: E402

s = get_settings()
chunks = load_chunks(s)
cache_keys = {p.stem for p in (ROOT / "cache").rglob("*.json")}
done = {c.chunk_id for c in chunks
        if cache_key(c, s.llm_model, PROMPT_VERSION) in cache_keys}

c201 = [c for c in chunks if c.doc_id.startswith("activity__20101")]
d201 = [c for c in c201 if c.chunk_id in done]
print("=== 20101 闭环核验 ===")
print(f"  20101 总块数 = {len(c201)}｜已入 cache = {len(d201)}")
print(f"  {'✅ 闭环' if len(c201) == len(d201) else '❌ 未闭环'}")

g = GraphStore.load(ROOT / "graph.json")

print()
print("=== 命名红线复核（受污染裸名）===")
for n in ["别斯米尔", "玛尔塔", "兀尔德", "德洛丝", "卡卡尼亚", "洛伦兹蝴蝶"]:
    print(f"  {n:10s} -> {g.resolve(n)!r}")

print()
print("=== ★ 评测失手项 c4 的实体（本会话新抽）===")
for n in ["使徒米修斯", "受苦者", "无名者"]:
    e = g.entities.get(n)
    r = g.resolve(n)
    if e:
        c201n = sum(1 for c in e.chunk_ids if "20101" in c)
        print(f"  ✅ {n:12s} {e.type:4s} m={e.mentions:3d} "
              f"neighbors={len(g.neighbors(n)):3d} 20101块={c201n:2d} "
              f"desc={e.desc!r}")
    else:
        print(f"  ⚠ {n:12s} resolve={r!r}（不在图中）")

print()
print("=== 20101 关键角色落点 ===")
for n in ["J", "玛蒂尔达", "环状水星", "先驱者", "莱格斯", "杰洛",
          "猫眼维森", "贝克特", "霍利克", "保利娜", "温妮弗雷德",
          "商贩梅克卢", "金伯利女郎", "发条玩具", "布翁尼家族",
          "贝丽尔", "勿忘我", "新纪元集市", "海特街", "锻剑车库"]:
    e = g.entities.get(n)
    if e:
        c201n = sum(1 for c in e.chunk_ids if "20101" in c)
        print(f"  ✅ {n:14s} {e.type:4s} m={e.mentions:3d} 20101块={c201n:2d} "
              f"aliases={e.aliases}")
    else:
        print(f"  ⚠ {n:14s} 不在图中")

print()
print("=== 归并声明实测（累计）===")
CLAIMS = [
    ("引路者巢状类脐菇", "幽灵蘑菇"), ("像素鸸鹋", "波拉比"),
    ("达利阿拉伯", "哒哒达利"), ("兔子小姐", "芭妮芭妮"),
    ("叮咚快报", "《澳大利亚叮当快报》"), ("宽檐帽", "宽檐帽先生"),
    ("小火", "可燃点"), ("克努特", "克努特大叔"),
    ("阿廖卡巧克力", "阿廖卡"), ("理线尺", "改线尺"),
    ("铁帽子节", "工人节"), ("曼德拉药草", "曼德拉草"),
    ("布翁尼女士", "贝丽尔"),
]
ok = 0
for name, expect in CLAIMS:
    got = g.resolve(name)
    mark = "✅" if got == expect else "❌"
    if got == expect:
        ok += 1
    print(f"  {mark} resolve({name!r}) -> {got!r} (期望 {expect!r})")
print(f"  {ok}/{len(CLAIMS)} 通过")
