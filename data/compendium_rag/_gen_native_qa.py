# -*- coding: utf-8 -*-
"""生成 **Compendium 原生**中文问答题集 `rag_testset_native.json`。

为什么要新造一套
----------------
`rag_testset_300.json` 的 300 题里有 87 题问的是「X 的英文名/英文写法是什么」——
纯中文语料**结构上答不出**（答案本身就是拉丁串），补任何映射都救不回来，
所以那套题的 `all(300)` 天花板只有 197/300 = 0.657，永远到不了 0.80。
要衡量「本库在**自己语种**上的召回能力」，必须用**从本库图谱派生、答案一定在语料里**的题。

造题原则（与 §5.4 的口径红线一致）
----------------------------------
1. 事实来源 = `graph.json` 里 `confidence ≥ 0.9` 且**证据逐字落在语料**的边（§3 红线 3 已保证）；
   定义题来源 = 实体的 `desc`。所以**每题答案必然在语料中**，不存在「题比语料老」的失配。
2. 期望关键词 = 答案实体的**中文正名**；**硬闸：答案词不得出现在题面**（否则送分）。
3. 题型三种：
   * `T1 正向单跳`：`「A」{关系}的对象/是谁？` → 答案 B
   * `T1r 反向单跳`：`谁/什么 {关系}了「B」？` → 答案 A
   * `T2 定义型`：用 `desc` 作线索问正名 → 答案 = 实体名（**查询里不含答案名**，最难）
4. 版本覆盖：每版最多取 N 题，避免全压在 1.x 主线；随机种子固定，脚本可复现。
5. 只用图谱与语料，**不碰检索代码、不碰原 300 题**。
"""
from __future__ import annotations

import json
import random
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from compendium_rag import pipeline as P  # noqa: E402
from compendium_rag.config import get_settings  # noqa: E402
from compendium_rag.graph_store import GraphStore  # noqa: E402

TARGET = int(__import__("os").environ.get("NATIVE_TARGET", "250"))
OUT = ROOT / "data/knowledge/_audit/rag_testset_native.json"
GRAPH = ROOT / "data/compendium_rag/graph.json"
RE_CN = re.compile(r"^[一-鿿·]{2,10}$")
GENERIC = re.compile(r"[0-9０-９ⅠⅡⅢⅣⅤ]|^众$|队员|士兵|游客|观众|记者|工作人员")

# 关系词 → 问句尾（问「另一端」）
ASK_OBJ = {
    "角色": "是谁？", "组织": "是哪个组织？", "地点": "是哪里？",
    "物品": "是什么？", "概念": "是什么？", "事件": "是什么事件？",
}


def main() -> int:
    rnd = random.Random(20260925)
    s = get_settings()
    chunks = P.load_chunks(s)
    blob_by_chunk = {c.chunk_id: f"{c.text}\n{c.chapter_title}\n{c.scene_title}\n{c.part_title}"
                     for c in chunks}
    blob = "\n".join(blob_by_chunk.values())
    g = GraphStore.load(GRAPH)
    print(f"图谱：{len(g.entities)} 实体 / {len(g.edges)} 边；语料 {len(chunks)} 块")

    def nm(eid: str) -> str:
        return g.entities[eid].name

    cases: list[dict] = []
    seen_q: set[str] = set()
    per_ver: dict[tuple[str, str], int] = defaultdict(int)   # (版本, 题型) → 已取题数
    # 每种题型每版限额：让 T2 定义题不被 T1 挤光（题型难度差异见文件头）
    CAPS = {"factoid": 3, "definition": 4}

    def ver_of(chunk_ids: list[str]) -> str:
        for cid in chunk_ids or []:
            return cid.split(":")[0].split("_", 1)[-1]
        return "?"

    def push(q: str, ans: str, ver: str, cid: str, ttype: str, hop: str,
             pool: str = "") -> bool:
        if not q or q in seen_q or not ans or len(ans) < 2:
            return False
        if ans in q:                       # 硬闸 2：答案词不能在题面
            return False
        if ans not in blob:                # 答案词必须真的在语料里
            return False
        if per_ver[(ver, ttype)] >= CAPS.get(ttype, 3):
            return False
        seen_q.add(q)
        per_ver[(ver, ttype)] += 1
        cases.append({
            "id": f"N{len(cases) + 1:03d}", "q": q,
            "ref": ans, "evidence": [[ans]],
            "dims": {"type": ttype, "difficulty": "medium", "depth": "shallow",
                     "hop": hop, "chapter": ver, "text_len": "short"},
            "source": "graph_generated_native",
            "_from_chunk": cid, "_pool": pool,
        })
        return True

    # ── T1 / T1r：关系边单跳 ────────────────────────────────────────
    edges = [e for e in g.edges if (e.confidence or 0) >= 0.9
             and e.src in g.entities and e.dst in g.entities]
    rnd.shuffle(edges)
    t1 = t1r = 0
    for e in edges:
        a, b = g.entities[e.src], g.entities[e.dst]
        if not (RE_CN.match(a.name) and RE_CN.match(b.name)):
            continue
        if GENERIC.search(a.name) or GENERIC.search(b.name):
            continue
        rel = (e.relation or "").strip()
        if not (1 <= len(rel) <= 5) or not RE_CN.match(rel):
            continue
        ver = ver_of(e.chunk_ids)
        cid = (e.chunk_ids or [""])[0]
        if a.type == "角色" and b.type in ASK_OBJ:
            q = f"「{a.name}」{rel}的对象{ASK_OBJ[b.type]}"
            if push(q, b.name, ver, cid, "factoid", "single", "T1"):
                t1 += 1
        if b.type in ("角色", "组织") and a.type in ASK_OBJ:
            who = "谁" if b.type == "角色" else "哪个组织"
            # 关系词以介词收尾时（惊愕于/倾向于/对…）不接「了」，否则题面不通
            tail = "" if rel[-1] in "于向对在与从把被的了" else "了"
            q = f"{who}{rel}{tail}「{a.name}」？"
            if push(q, b.name, ver, cid, "factoid", "single", "T1r"):
                t1r += 1

    # ── T2：定义型（desc 作线索，问正名）────────────────────────────
    t2 = 0
    ents = [e for e in g.entities.values()
            if e.desc and len(e.desc) >= 6 and RE_CN.match(e.name) and not GENERIC.search(e.name)
            and len(g.neighbors(e.eid)) >= 3]
    rnd.shuffle(ents)
    for e in ents:
        ver = ver_of(e.chunk_ids)
        clue = re.sub(r"[。；]$", "", e.desc.strip())[:24]
        if not clue or e.name in clue:
            continue
        q = f"{clue}——这是哪个{e.type}？"
        if push(q, e.name, ver, (e.chunk_ids or [""])[0], "definition", "single", "T2"):
            t2 += 1

    # ── 分层抽样：三池 round-robin，取 TARGET 题，题型配比稳定、可复现 ──
    pools: dict[str, list[dict]] = defaultdict(list)
    for c in cases:
        pools[c["_pool"]].append(c)
    if TARGET and len(cases) > TARGET:
        picked: list[dict] = []
        order = ["T1", "T1r", "T2"]
        i = 0
        while len(picked) < TARGET and any(pools[k][i:] for k in order if len(pools[k]) > i):
            for k in order:
                if len(pools[k]) > i and len(picked) < TARGET:
                    picked.append(pools[k][i])
            i += 1
        cases = picked
        for j, c in enumerate(cases, 1):
            c["id"] = f"N{j:03d}"

    OUT.write_text(json.dumps({
        "_meta": {
            "built_from": "data/compendium_rag/graph.json（#36 产物）",
            "rules": ["答案词必在语料", "答案词不在题面", "每版每题型限额(factoid 3／definition 4)", "seed=20260925 可复现"],
            "counts": {"pool_T1": t1, "pool_T1r": t1r, "pool_T2": t2,
                     "after_sample_total": len(cases), "target": TARGET},
        },
        "cases": cases,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    from collections import Counter
    print(f"候选池：T1 {t1}｜T1r {t1r}｜T2 {t2}｜抽样后 {len(cases)} 题 "
          f"｜覆盖版本 {len({c['dims']['chapter'] for c in cases})} "
          f"｜题型配比 {dict(Counter(c['_pool'] for c in cases))}")
    print(f"→ {OUT}")
    for c in cases[:6] + cases[-4:]:
        print(f"   {c['id']} [{c['dims']['type']}] {c['q']}  ⇒ {c['ref']}  ({c['dims']['chapter']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
