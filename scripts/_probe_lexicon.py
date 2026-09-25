# -*- coding: utf-8 -*-
"""探查词表/图谱别名，判断 P1-1「轻版」可行性。

P1-1 原方案：给 ~8000 英文块建中文翻译索引（需 LLM 翻译，成本极高）。
**轻版**：不翻译全文，只把词典里已知的中文别名**挂到**英文块上
（"troll" 的块 → 追加 "巨怪"）。若失分题的证据词大多能被词典覆盖，
轻版就能拿到大部分收益，成本几乎为零。

本脚本只读，回答三件事：
    1. 词典/别名表长什么样、有多少条
    2. en_only 失分题的证据词里，有多少能在词典里找到中文映射
    3. 若按轻版方案，理论能覆盖多少失分题

用法：.venv/Scripts/python.exe -X utf8 scripts/_probe_lexicon.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

AUDIT = ROOT / "data" / "knowledge" / "_audit"
OUT = AUDIT / "_lexicon_probe.txt"
buf: list[str] = []


def p(*a):
    buf.append(" ".join(str(x) for x in a))


# —— 1. 词表 ——
lex_path = AUDIT / "huiji_lexicon.json"
if not lex_path.is_file():
    # 词表实际落在 lore 目录，不在 _audit
    lex_path = ROOT / "data" / "lore" / "wu_ming_zhe" / "huiji_lexicon.json"
p("=" * 78)
p("① 词表 / 别名表")
p("=" * 78)
en2zh: dict[str, set[str]] = {}
if lex_path.is_file():
    try:
        data = json.loads(lex_path.read_text(encoding="utf-8"))
        p(f"  huiji_lexicon.json 顶层键：{list(data)[:10]}")
        # 尽量兼容多种结构
        def collect(o):
            if isinstance(o, dict):
                for k, v in o.items():
                    if isinstance(v, str) and v:
                        kl, vl = k.strip(), v.strip()
                        if kl and vl:
                            en2zh.setdefault(kl.lower(), set()).add(vl)
                            en2zh.setdefault(vl.lower(), set()).add(kl)
                    else:
                        collect(v)
            elif isinstance(o, list):
                for x in o:
                    collect(x)
        collect(data)
        p(f"  抽出映射条目：{len(en2zh)}")
    except Exception as e:  # noqa: BLE001
        p(f"  读取失败：{e}")
else:
    p(f"  [MISSING] {lex_path}")

# 图谱实体别名
try:
    from roleplay.config import get_settings  # noqa: E402
    from roleplay.core.knowledge.factory import build_plot_registry  # noqa: E402

    s = get_settings()
    reg = build_plot_registry(s).get("wu_ming_zhe")
    g = getattr(reg, "graph", None)
    ents = {}
    if g is not None:
        for name, node in (getattr(g, "entities", None) or {}).items():
            if isinstance(node, dict):
                al = node.get("aliases") or []
            else:
                al = getattr(node, "aliases", []) or []
            if al:
                ents[str(name)] = [str(a) for a in al]
        p(f"  图谱实体带别名：{len(ents)}")
        n_alias = sum(len(v) for v in ents.values())
        for name, al in ents.items():
            for a in al:
                en2zh.setdefault(str(name).lower(), set()).add(a)
                en2zh.setdefault(str(a).lower(), set()).add(name)
        p(f"  图谱别名总条数：{n_alias}")
    p(f"  合并后可用映射：{len(en2zh)}")
except Exception as e:  # noqa: BLE001
    p(f"  图谱别名读取失败：{e}")

# —— 2. en_only 失分题的证据词覆盖情况 ——
p()
p("=" * 78)
p("② en_only 失分题的证据词能否被词典桥接")
p("=" * 78)
rows_p = AUDIT / "diag_lang_headroom.json"
if not rows_p.is_file():
    p("[MISSING] 先跑 scripts/diag_lang_headroom.py")
    OUT.write_text("\n".join(buf), encoding="utf-8")
    raise SystemExit(0)

d = json.loads(rows_p.read_text(encoding="utf-8"))
rows = d.get("rows") or []
fails = [r for r in rows if r.get("bucket") == "en_only" and not r.get("inject")]
p(f"  en_only 且 inject 失分：{len(fails)} 题")

src = AUDIT / "rag_testset_300_clean.json"
cases = {str(c.get("id")): c for c in json.loads(src.read_text(encoding="utf-8"))}

full_bridge = part_bridge = no_bridge = 0
samples: list[str] = []
for r in fails:
    item = cases.get(str(r.get("id")))
    if not item:
        continue
    groups = item.get("evidence") or []
    hit_g = 0
    for g in groups:
        if any(any(kw.lower() in en2zh for kw in (g if isinstance(g, list) else [g]))
               for _ in [0]):
            hit_g += 1
    if groups and hit_g == len(groups):
        full_bridge += 1
    elif hit_g:
        part_bridge += 1
    else:
        no_bridge += 1
        if len(samples) < 8:
            flat = [str(k) for g in groups for k in (g if isinstance(g, list) else [g])]
            samples.append(f"    {r.get('id')}  {r.get('q', '')[:34]}  证据词 {flat[:6]}")

p(f"  · 全部证据组都有中文映射（轻版可救）：{full_bridge} 题")
p(f"  · 部分有（可能部分可救）            ：{part_bridge} 题")
p(f"  · 完全没有（轻版无能为力）          ：{no_bridge} 题")
if samples:
    p("  无映射样本：")
    buf.extend(samples)

p()
p("=" * 78)
p("③ 判定")
p("=" * 78)
tot = len(fails) or 1
if full_bridge / tot >= 0.5:
    p(f"✅ 轻版可行：{full_bridge}/{len(fails)} 可完全桥接 ⇒ 值得实现")
else:
    p(f"❌ 轻版空间不足：仅 {full_bridge}/{len(fails)} 可完全桥接")
    p("   ⇒ 若要 P1-1，只能走「LLM 全文翻译 ~8000 块」的重方案")

OUT.write_text("\n".join(buf), encoding="utf-8")
