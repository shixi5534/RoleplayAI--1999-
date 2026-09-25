# -*- coding: utf-8 -*-
"""第 7 会话验证：16101 闭环 + 方案 B（探险家别斯米尔）+ 归并声明实测。"""
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

c161 = [c for c in chunks if c.doc_id.startswith("activity__16101")]
d161 = [c for c in c161 if c.chunk_id in done]
print(f"=== 16101 闭环核验 ===")
print(f"  16101 总块数 = {len(c161)}｜已入 cache = {len(d161)}")
print(f"  {'✅ 闭环' if len(c161) == len(d161) else '❌ 未闭环'}")

g = GraphStore.load(ROOT / "graph.json")
print()
print("=== 方案 B 核心验证（探险家别斯米尔 独立）===")
tests = [
    ("探险家别斯米尔", "探险家别斯米尔", "16101 主角应独立解析到自己"),
    ("小叶尼塞", "小叶尼塞", "同伴应独立"),
    ("曲娘", "曲娘", "16101 关键角色"),
    ("葛天", "葛天", "羽人本名"),
]
ok = 0
for name, expect, note in tests:
    got = g.resolve(name)
    mark = "✅" if got == expect else "❌"
    if got == expect:
        ok += 1
    print(f"  {mark} resolve({name!r}) -> {got!r}｜{note}")
print(f"  {ok}/{len(tests)} 通过")

print()
print("=== 归并声明实测（含第 6 会话遗留项）===")
CLAIMS = [
    ("引路者巢状类脐菇", "幽灵蘑菇", "15101 归并"),
    ("像素鸸鹋", "波拉比", "15101 归并"),
    ("达利阿拉伯", "哒哒达利", "15101 归并"),
    ("兔子小姐", "芭妮芭妮", "15101 归并"),
    ("叮咚快报", "《澳大利亚叮当快报》", "15101 归并"),
    ("宽檐帽", "宽檐帽先生", "15101 归并"),
    ("小火", "可燃点", "15101 归并"),
]
ok2 = 0
for name, expect, note in CLAIMS:
    got = g.resolve(name)
    mark = "✅" if got == expect else "❌"
    if got == expect:
        ok2 += 1
    print(f"  {mark} resolve({name!r}) -> {got!r} (期望 {expect!r})｜{note}")
print(f"  {ok2}/{len(CLAIMS)} 通过")

print()
print("=== 卡卡尼亚 是否被 16101 污染（应仍为 0）===")
k = g.entities.get("卡卡尼亚")
if k:
    c = [x for x in k.chunk_ids if "16101" in x]
    print(f"  卡卡尼亚: m={k.mentions} neighbors={len(g.neighbors('卡卡尼亚'))}")
    print(f"  来自 16101 的块 = {len(c)}  {'✅ 未污染' if not c else '❌ 被污染'}")

print()
print("=== 16101 新节点落点（抽样）===")
for n in ["探险家别斯米尔", "小叶尼塞", "曲娘", "葛天", "里正", "法曹",
          "鹿蜀", "存想", "半妖", "木头小人", "河灯", "职祠", "酒坊",
          "沛城", "断桥", "渊庙", "《朔日手记》", "西里尔字母", "岁朝春"]:
    e = g.entities.get(n)
    if e:
        print(f"  ✅ {n:14s} {e.type:4s} m={e.mentions:3d} "
              f"neighbors={len(g.neighbors(n)):3d} desc={e.desc!r}")
    else:
        print(f"  ⚠ {n:14s} 不在图中")
