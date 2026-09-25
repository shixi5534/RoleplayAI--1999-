# -*- coding: utf-8 -*-
"""把仓库里现成的**中英映射**用在 300 题上，产出 `rag_testset_300_cn.json`。

原测试集 `rag_testset_300.json` **一字不改**（本脚本只读它）。

为什么需要这一步
----------------
这 300 题是为**旧语料**（B站转写 + 灰机 wiki，中英混排）造的，Compendium 是**纯中文官方正文**。
实测 130/300 题的期望关键词是英文串（`Zanetta` / `Fogg` / `Pavlov` …），
在纯中文语料上**永远不可能命中**——那不是检索失败，是用例与语料不同语种。
本脚本只补「中文里那个东西本来叫什么」，补据全部来自仓库既有事实源，不引入人工臆断。

两路补据（按可信度排序）
------------------------
* **S0 金标 `ref`**：用例自带的参考答案常写作 `Zanetta（扎内塔）`、`Fogg（福格先生）`，
  取其中的中文段即为标准答案的中文形——这是用例自己的金标，最可信。
* **S1 中英映射表**（灰机 wiki 派生，即用户指定的裁决标准）：
  `huiji_lexicon.json`(zh2en/en2zh 885 条)、`plot_glossary.json`(terms.145 带灰机URL)、
  `plot_aliases.json`(260 条别名链)、`wiki_zh_en.json`(147 条角色)。

四条防「改用例迎合指标」的硬规则
--------------------------------
1. **题面在问英文名的题一律不补**（`…的英文名是什么 / 英文叫什么 / 英文拼法 / 机构代号`）——
   答案本身就是英文串，纯中文语料结构上答不出，保留在 unanswerable 里单列。
2. 补入词必须**确实在 Compendium 语料中出现**（否则补了也不会命中，只是噪声）。
3. **补入词不得出现在题面里**（否则等于把答案抄进关键词，命中毫无意义）。
4. 每个补入词逐条记 `provenance`（S0/S1 + 具体键），落盘可审。
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from compendium_rag import pipeline as P  # noqa: E402
from compendium_rag.config import get_settings  # noqa: E402

SRC = ROOT / "data/knowledge/_audit/rag_testset_300.json"
OUT = ROOT / "data/knowledge/_audit/rag_testset_300_cn.json"
AUDIT = ROOT / "data/knowledge/_audit/rag_testset_300_cn_audit.txt"

RE_CN = re.compile(r"[一-鿿]")
CN_RUN = re.compile(r"[一-鿿]{2,8}")
# 题面问英文名 → 不可补（答案本身就是拉丁串，纯中文语料结构上答不出）
ASKS_EN = re.compile(
    r"(英文名|英文名字|英文叫|英文拼|英文写作|英文写法|英文原文|英文全称|英文简称"
    r"|对应的英文|写作什么|机构代号|代号是什么|英文名?是什么)")
# ref 里的说明性碎片，不是答案名
META = re.compile(r"(篇|章节|物品|意为|即|全称|简介|组织|地点名词|的一|与.{0,4}一行|等)")


def norm(s: str) -> str:
    return re.sub(r"[\s’'\-\.]+", "", (s or "")).casefold()


def load_tables() -> dict[str, list[tuple[str, str]]]:
    """EN(归一化) → [(中文, 出处), ...]，四张表合并。"""
    m: dict[str, list[tuple[str, str]]] = {}

    def add(en: str, zh: str, prov: str) -> None:
        k = norm(en)
        if not k or not zh:
            return
        if all(z != zh for z, _ in m.setdefault(k, [])):
            m[k].append((zh, prov))

    base = ROOT / "data/lore/wu_ming_zhe"
    lex = json.loads((base / "huiji_lexicon.json").read_text(encoding="utf-8"))
    for en, zhs in (lex.get("en2zh") or {}).items():
        for z in zhs:
            add(en, z, f"S1 huiji_lexicon.en2zh[{en}]")
    for zh, ens in (lex.get("zh2en") or {}).items():
        for e in ens:
            add(e, zh, f"S1 huiji_lexicon.zh2en[{zh}]")
    glo = json.loads((base / "plot_glossary.json").read_text(encoding="utf-8"))
    for zh, t in (glo.get("terms") or {}).items():
        add(t.get("en") or "", zh, f"S1 plot_glossary.terms[{zh}].en")
        for a in t.get("aliases") or []:
            if not RE_CN.search(a):
                add(a, zh, f"S1 plot_glossary.terms[{zh}].aliases")
    pal = json.loads((base / "plot_aliases.json").read_text(encoding="utf-8"))
    for zh, als in pal.items():
        for a in als:
            if not RE_CN.search(a):
                add(a, zh, f"S1 plot_aliases[{zh}]")
    wje = json.loads((base / "wiki_zh_en.json").read_text(encoding="utf-8"))
    for zh, en in wje.items():
        if str(zh).startswith("_") or not isinstance(en, str):
            continue
        add(en, zh, f"S1 wiki_zh_en[{zh}]")
    return m


def groups_of(ev) -> list[list[str]]:
    out = []
    for grp in ev or []:
        if isinstance(grp, str):
            out.append([grp])
        elif isinstance(grp, (list, tuple)):
            out.append([str(x) for x in grp if str(x).strip()])
    return out


def ref_cn_spans(ref: str) -> list[str]:
    """金标 ref → 候选中文答案名（按可信度：括号内 > 括号外，长者优先）。"""
    in_paren = re.findall(r"[（(]([^）)]{2,20})[）)]", ref or "")
    outside = [re.sub(r"[（(][^）)]*[）)]", "", ref or "")]
    seen, out = set(), []
    for src in in_paren + outside:
        for m in CN_RUN.findall(src):
            for piece in re.split(r"[、，,;；/＼与和及（）()0-9a-zA-Z]+", m):
                piece = piece.strip()
                if len(piece) >= 2 and piece not in seen and not META.search(piece):
                    seen.add(piece)
                    out.append(piece)
    return out


def main() -> int:
    mp = load_tables()
    s = get_settings()
    # blob 口径与 scripts/compendium_rag_eval300.py:102 的打分 blob 完全一致
    # （正文 + 篇名 + 场景名 + 部分名），否则「是否在语料中」的判定与命中判定不同源。
    blob = "\n".join(f"{c.text}\n{c.chapter_title}\n{c.scene_title}\n{c.part_title}"
                     for c in P.load_chunks(s))
    ts = json.loads(SRC.read_text(encoding="utf-8"))
    cases = ts["cases"] if isinstance(ts, dict) and "cases" in ts else ts

    n0 = n1 = n_en = 0
    blocked: list[tuple[str, str, str]] = []   # 规则 3 拦下（答案词就在题面里）
    lines: list[str] = []
    new_cases = []
    for r in cases:
        gs = groups_of(r.get("evidence"))
        kws = [k for g in gs for k in g]
        q = r.get("q") or ""
        ans0 = any(k in blob for k in kws)
        n0 += 1 if ans0 else 0
        adds: list[tuple[str, str]] = []
        asks_en = bool(ASKS_EN.search(q))
        if not ans0:
            if asks_en:
                n_en += 1
                lines.append(f"[不补·问英文名] {r['id']} kw={kws} ref={r.get('ref')!r} |{q}")
            else:
                cand: list[tuple[str, str]] = []
                for sp in ref_cn_spans(r.get("ref") or ""):
                    cand.append((sp, f"S0 ref={r.get('ref')!r}"))
                for k in kws:
                    if not RE_CN.search(k):
                        cand += [(zh, prov) for zh, prov in mp.get(norm(k), ())]
                for zh, prov in cand:
                    if zh in kws or any(zh == a for a, _ in adds):
                        continue
                    if zh not in blob:
                        continue
                    if zh in q:                      # 规则 3：答案词不得就是题面词
                        blocked.append((r["id"], zh, q[:40]))
                        continue
                    adds.append((zh, prov))
        new_ev = [g[:] for g in gs]
        if adds:
            new_ev[0] = new_ev[0] + [a for a, _ in adds]
        kws2 = [k for g in new_ev for k in g]
        ans1 = any(k in blob for k in kws2)
        n1 += 1 if ans1 else 0
        if adds:
            lines.append(f"[补] {r['id']} {kws} + {[(a, p) for a, p in adds]} |{q}")
        elif not ans0 and not asks_en:
            lines.append(f"[未救] {r['id']} kw={kws} ref={r.get('ref')!r} |{q}")
        nr = dict(r)
        nr["evidence"] = new_ev
        nr["_cn_map_added"] = [{"kw": a, "from": p} for a, p in adds]
        nr["_asks_english_name"] = asks_en
        new_cases.append(nr)

    OUT.write_text(json.dumps({
        "_meta": {
            "derived_from": "data/knowledge/_audit/rag_testset_300.json（原文件未改动）",
            "sources": {"S0": "用例自带金标 ref 的中文段",
                        "S1": ["huiji_lexicon.json", "plot_glossary.json",
                               "plot_aliases.json", "wiki_zh_en.json"]},
            "rules": ["题面问英文名的一律不补（纯中文语料结构上不可答）",
                      "补入词必须在语料中出现", "补入词不得出现在题面", "逐条记 provenance"],
        },
        "cases": new_cases,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    AUDIT.write_text("\n".join(lines), encoding="utf-8")

    print(f"映射表 EN 键 = {len(mp)}")
    print(f"answerable：{n0}/300 → {n1}/300")
    print(f"「问英文名」类不补 = {n_en} 题")
    print(f"规则 3 拦下（答案词就在题面，补了等于送分）= {len(blocked)} 处：{blocked}")
    print(f"审计表 → {AUDIT}")
    print(f"新用例集 → {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
