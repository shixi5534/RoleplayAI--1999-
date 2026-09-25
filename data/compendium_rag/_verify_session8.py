# -*- coding: utf-8 -*-
"""第 8 会话验证：18101 闭环 + 命名红线 + 归并声明实测 + 重复建模检查。"""
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

c181 = [c for c in chunks if c.doc_id.startswith("activity__18101")]
d181 = [c for c in c181 if c.chunk_id in done]
print("=== 18101 闭环核验 ===")
print(f"  18101 总块数 = {len(c181)}｜已入 cache = {len(d181)}")
print(f"  {'✅ 闭环' if len(c181) == len(d181) else '❌ 未闭环'}")

g = GraphStore.load(ROOT / "graph.json")

print()
print("=== 命名红线复核（受污染裸名）===")
for n in ["别斯米尔", "玛尔塔", "兀尔德", "德洛丝", "卡卡尼亚"]:
    print(f"  {n:10s} -> {g.resolve(n)!r}")

print()
print("=== 18101 关键角色落点（应复用、18101 块数>0）===")
for n in ["北方哨歌", "维拉", "叶甫根尼", "克努特大叔", "贝托尔特",
          "阿夫西维", "尼娜", "彼得森", "帕索诺", "帕特里基大叔",
          "技工尤里", "尼基塔", "瓦列里娅", "鲁萨尔卡", "理线学",
          "来亚什基", "芝诺", "煤矿", "卢恩原矿", "奇肯恩",
          "基基图克", "霍伊图克", "理线拟态仪", "工人节", "罐头园"]:
    e = g.entities.get(n)
    if e:
        c181n = sum(1 for c in e.chunk_ids if "18101" in c)
        print(f"  ✅ {n:14s} {e.type:4s} m={e.mentions:3d} "
              f"neighbors={len(g.neighbors(n)):3d} 18101块={c181n:2d} "
              f"aliases={e.aliases}")
    else:
        print(f"  ⚠ {n:14s} 不在图中")

print()
print("=== 重复建模检查：尤里 / 洛伦兹蝴蝶 ===")
for n in ["尤里", "技工尤里", "洛伦兹蝴蝶", "洛伦兹", "洛伦兹研究所"]:
    e = g.entities.get(n)
    if e:
        print(f"  {n:14s} type={e.type} m={e.mentions} desc={e.desc!r} "
              f"aliases={e.aliases}")
    else:
        print(f"  {n:14s} 不存在")

print()
print("=== 归并声明实测（累计）===")
CLAIMS = [
    ("引路者巢状类脐菇", "幽灵蘑菇"),
    ("像素鸸鹋", "波拉比"),
    ("达利阿拉伯", "哒哒达利"),
    ("兔子小姐", "芭妮芭妮"),
    ("叮咚快报", "《澳大利亚叮当快报》"),
    ("宽檐帽", "宽檐帽先生"),
    ("小火", "可燃点"),
    ("克努特", "克努特大叔"),
    ("阿廖卡巧克力", "阿廖卡"),
    ("理线尺", "改线尺"),
    ("铁帽子节", "工人节"),
]
ok = 0
for name, expect in CLAIMS:
    got = g.resolve(name)
    mark = "✅" if got == expect else "❌"
    if got == expect:
        ok += 1
    print(f"  {mark} resolve({name!r}) -> {got!r} (期望 {expect!r})")
print(f"  {ok}/{len(CLAIMS)} 通过")
