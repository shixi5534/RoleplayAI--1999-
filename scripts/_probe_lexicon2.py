# -*- coding: utf-8 -*-
"""按 huiji_lexicon.json 的真实结构（meta/zh2en/en2zh/rules）统计并做桥接判定。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
AUDIT = ROOT / "data" / "knowledge" / "_audit"
OUT = AUDIT / "_lexicon_probe2.txt"
buf: list[str] = []


def p(*a):
    buf.append(" ".join(str(x) for x in a))


lex = json.loads((ROOT / "data" / "lore" / "wu_ming_zhe" / "huiji_lexicon.json")
                 .read_text(encoding="utf-8"))
p("=" * 78)
p("① 词表结构与规模")
p("=" * 78)
for k in ("meta", "zh2en", "en2zh", "rules"):
    v = lex.get(k)
    p(f"  {k:<8}type={type(v).__name__:<6}len={len(v) if hasattr(v, '__len__') else '-'}")

# 看几条样例
for k in ("zh2en", "en2zh"):
    v = lex.get(k) or {}
    if isinstance(v, dict):
        items = list(v.items())[:5]
        p(f"  {k} 样例：{items}")
    elif isinstance(v, list):
        p(f"  {k} 样例：{v[:5]}")

# 归一化成 en->zh 集合
def norm_pairs(v) -> list[tuple[str, str]]:
    out = []
    if isinstance(v, dict):
        for a, b in v.items():
            if isinstance(b, str):
                out.append((a, b))
            elif isinstance(b, (list, tuple, set)):
                out.extend((a, str(x)) for x in b)
    elif isinstance(v, list):
        for x in v:
            if isinstance(x, dict):
                a, b = x.get("en"), x.get("zh")
                if a and b:
                    out.append((str(a), str(b)))
            elif isinstance(x, (list, tuple)) and len(x) == 2:
                out.append((str(x[0]), str(x[1])))
    return out


pairs = norm_pairs(lex.get("en2zh")) + [(b, a) for a, b in norm_pairs(lex.get("zh2en"))]
en2zh: dict[str, set[str]] = {}
for a, b in pairs:
    if a.strip() and b.strip():
        en2zh.setdefault(a.strip().lower(), set()).add(b.strip())
p(f"  归一化后 en→zh 条目：{len(en2zh)}")

# 图谱别名并入
try:
    from roleplay.core.knowledge.factory import build_plot_registry  # noqa: E402
    from roleplay.config import get_settings  # noqa: E402

    reg = build_plot_registry(get_settings()).get("wu_ming_zhe")
    g = getattr(reg, "graph", None)
    if g is not None:
        ents = getattr(g, "entities", None) or {}
        cnt = 0
        for name, node in (ents.items() if isinstance(ents, dict) else []):
            al = (node.get("aliases") if isinstance(node, dict)
                  else getattr(node, "aliases", None)) or []
            for a in al:
                en2zh.setdefault(str(name).lower(), set()).add(str(a))
                en2zh.setdefault(str(a).lower(), set()).add(str(name))
                cnt += 1
        p(f"  并入图谱别名 {cnt} 条 → 合计 {len(en2zh)}")
except Exception as e:  # noqa: BLE001
    p(f"  图谱别名并入失败：{e}")

# —— 桥接判定 ——
p()
p("=" * 78)
p("② en_only 失分题的证据词桥接情况")
p("=" * 78)
d = json.loads((AUDIT / "diag_lang_headroom.json").read_text(encoding="utf-8"))
rows = d.get("rows") or []
cases = {str(c.get("id")): c for c in
         json.loads((AUDIT / "rag_testset_300_clean.json").read_text(encoding="utf-8"))}
fails = [r for r in rows if r.get("bucket") == "en_only" and not r.get("inject")]
p(f"  en_only 且 inject 失分：{len(fails)} 题")

full = part = none = 0
samples_no: list[str] = []
samples_yes: list[str] = []
for r in fails:
    item = cases.get(str(r.get("id")))
    if not item:
        continue
    groups = item.get("evidence") or []
    hit = 0
    for g in groups:
        kws = g if isinstance(g, list) else [g]
        if any(str(kw).lower() in en2zh for kw in kws):
            hit += 1
    if groups and hit == len(groups):
        full += 1
        if len(samples_yes) < 5:
            flat = [str(k) for g in groups for k in (g if isinstance(g, list) else [g])]
            samples_yes.append(f"    {r.get('id')} {flat[:5]} → "
                               f"{[sorted(en2zh.get(k.lower(), []))[:2] for k in flat[:3]]}")
    elif hit:
        part += 1
    else:
        none += 1
        if len(samples_no) < 10:
            flat = [str(k) for g in groups for k in (g if isinstance(g, list) else [g])]
            samples_no.append(f"    {r.get('id')} {str(r.get('q',''))[:30]}  {flat[:5]}")

p(f"  · 全部证据组可桥接：{full} 题")
p(f"  · 部分可桥接      ：{part} 题")
p(f"  · 完全无映射      ：{none} 题")
if samples_yes:
    p("  可桥接样本：")
    buf.extend(samples_yes)
if samples_no:
    p("  无映射样本：")
    buf.extend(samples_no)

p()
p("=" * 78)
p("③ 判定")
p("=" * 78)
tot = len(fails) or 1
p(f"  完全可桥接占比 {full}/{len(fails)} = {full / tot:.1%}")
if full / tot >= 0.4:
    p("  ✅ 轻版（词典挂接中文别名）有空间，值得实现")
else:
    p("  ❌ 轻版空间不足")
    p("     关键：失分题的证据词多为**英文专名**（Zanetta / Shamane / Teofil），")
    p("     需要的是「中文描述 → 英文实体名」的语义链接（= B4 查询扩展），")
    p("     而词典只做「专名 ↔ 专名」互译，原理上补不上这个缺口。")
    p("     ⇒ P1-1 只能走 LLM 全文翻译的重方案，且即便如此也未必命中——")
    p("       翻译后仍要靠语义把中文描述匹配到英文实体。")

OUT.write_text("\n".join(buf), encoding="utf-8")
