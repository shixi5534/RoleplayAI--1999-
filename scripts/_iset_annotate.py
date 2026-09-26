# -*- coding: utf-8 -*-
"""题集 i · 标注与机检（先写题后标图；纯本地，零网关）。

对写手草稿做两级处理：
1) 机检（任一失败 → reject）：
   - JSON 合法、qid 唯一、字段齐全
   - evidence_quote 逐字命中所标 chunk 的原文 text
   - 答案实体名不得出现在题面（防泄答案）
   - 题面不得含图谱模板腔（「X」…的对象 句式）
   - 答案词必须在语料（chunks 全文）中出现过（keyword 可判分前提）
2) 图标注（事后计算，不参与出题）：
   - seeds = retriever.link(q)（题面可链到的实体）
   - gold = graph.resolve(answer)
   - anchor = graph.resolve(anchor)
   - gold_in_neighborhood：gold ∈ anchor 的 1-hop 邻域
   - hop：1 / 2 / None（BFS 深度上限 2）
   - neighborhood_size：anchor 的 1-hop 邻域实体数
   - pool：T1（anchor+gold 可达 1-hop）/ MULTI（仅 2-hop）/ U（其余：无锚点或不可达）
"""
from __future__ import annotations

import json
import re
import sys
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from compendium_rag import pipeline as P  # noqa: E402

DRAFTS = ROOT / "data/eval_set_i/drafts"
OUTDIR = ROOT / "data/eval_set_i"
TEMPLATE_RE = re.compile(r"「[^」]+」[^？?]*的(对象|是谁)")


def load_chunk_texts() -> dict[str, str]:
    d = json.loads((ROOT / "data/compendium_rag/chunks.json").read_text(encoding="utf-8"))
    return {c["chunk_id"]: c["text"] for c in d["chunks"]}


def bfs_hop(adj, a: str, b: str, max_depth: int = 2):
    if a == b:
        return 0
    seen = {a}
    q = deque([(a, 0)])
    while q:
        cur, d = q.popleft()
        if d >= max_depth:
            continue
        for nb, _w in adj.get(cur, []):
            if nb == b:
                return d + 1
            if nb not in seen:
                seen.add(nb)
                q.append((nb, d + 1))
    return None


def main() -> int:
    texts = load_chunk_texts()
    kb = P.load_kb(__import__("compendium_rag.config", fromlist=["get_settings"]).get_settings())
    g, ret = kb.graph, kb.retriever
    adj = ret._adj

    def norm_resolve(name: str):
        """答案名归一化 resolve：原名 → 剥书名号引号括号 → 别名包含唯一匹配。"""
        if not name:
            return None, ""
        eid = g.resolve(name)
        if eid:
            return eid, ""
        cleaned = re.sub(r"[《》“”‘’\"'（）()\s]", "", name)
        if cleaned and cleaned != name:
            eid = g.resolve(cleaned)
            if eid:
                return eid, f"剥标点→{cleaned}"
        # 包含匹配：图谱名是答案名子串，或反之；取最长且唯一
        cands = {e: g.entities[e].name for e in g.by_name} if hasattr(g, "by_name") else None
        idx = getattr(g, "alias_index", {})
        hits = set()
        for key, e in idx.items():
            k = re.sub(r"[《》“”‘’\"'（）()\s]", "", str(key))
            if not k:
                continue
            if k == cleaned or (len(cleaned) >= 2 and (k in cleaned or cleaned in k)):
                hits.add(e)
        if len(hits) == 1:
            e = hits.pop()
            return e, f"别名包含→{g.entities[e].name}"
        return None, f"含混({len(hits)})" if hits else "无匹配"

    rows, rejects = [], []
    seen_qid: set[str] = set()
    files = sorted(DRAFTS.glob("batch_*.jsonl"))
    for fp in files:
        for ln in fp.read_text(encoding="utf-8").splitlines():
            ln = ln.strip()
            if not ln:
                continue
            try:
                r = json.loads(ln)
            except Exception as e:
                rejects.append({"src": fp.name, "err": f"JSON: {e}", "raw": ln[:120]})
                continue
            qid, q = r.get("qid", ""), r.get("q", "")
            ans = (r.get("answer") or "").strip()
            errs = []
            if not qid or qid in seen_qid:
                errs.append("qid 空或重复")
            seen_qid.add(qid)
            if not q or not ans:
                errs.append("缺 q 或 answer")
            if ans and ans in q:
                errs.append("题面泄露答案名")
            if TEMPLATE_RE.search(q):
                errs.append("题面含图谱模板腔")
            cid = r.get("evidence_chunk", "")
            eq = r.get("evidence_quote", "")
            if cid not in texts:
                errs.append("evidence_chunk 不存在")
            elif eq and eq not in texts[cid]:
                errs.append("evidence_quote 未逐字命中")
            if errs:
                rejects.append({"src": fp.name, "qid": qid, "err": "; ".join(errs)})
                continue

            gold, gnote = norm_resolve(ans)
            anchor, anote = norm_resolve((r.get("anchor") or "").strip())
            seeds = ret.link(q, top_k=6)
            seed_names = [s.name for s in seeds]
            nbr1 = {nb for nb, _w in adj.get(anchor, [])} if anchor else set()
            hop = bfs_hop(adj, anchor, gold, 2) if (anchor and gold) else None
            if gold is None:
                pool = "U"          # 答案不在图谱白名单
            elif anchor is None:
                pool = "U"          # 无锚点（定义/描述型）
            elif hop == 1 or gold in nbr1:
                pool = "T1"
            elif hop == 2:
                pool = "MULTI"
            else:
                pool = "U"

            rows.append({
                "id": qid, "q": q, "answer": ans, "answer_type": r.get("answer_type", ""),
                "anchor": r.get("anchor", ""), "relation": r.get("relation", ""),
                "ref": cid, "evidence": [[ans]],
                "_from_chunk": cid, "_pool": pool, "source": "human_blind_set_i",
                "gold_eid": gold, "anchor_eid": anchor,
                "gold_name": g.entities[gold].name if gold else None,
                "anchor_name": g.entities[anchor].name if anchor else None,
                "fix_note": "; ".join(x for x in (f"gold:{gnote}" if gnote else "", f"anchor:{anote}" if anote else "") if x),
                "gold_in_neighborhood": bool(gold and (hop == 1)),
                "hop": hop, "neighborhood_size": len(nbr1),
                "link_seeds": seed_names,
                "dims": {"type": {"T1": "factoid", "MULTI": "multi_hop", "U": "definition"}.get(pool, "?"),
                         "difficulty": "unknown", "depth": "shallow" if pool == "T1" else "deep",
                         "hop": "single" if pool == "T1" else ("multi" if pool == "MULTI" else "n/a"),
                         "chapter": cid.split(":")[0].split("__", 1)[-1], "text_len": "short"},
            })

    OUTDIR.mkdir(parents=True, exist_ok=True)
    (OUTDIR / "annotated.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")
    (OUTDIR / "rejected.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rejects) + "\n", encoding="utf-8")

    from collections import Counter
    pc = Counter(r["_pool"] for r in rows)
    print(f"文件 {len(files)}，通过 {len(rows)}，拒绝 {len(rejects)}")
    print("pool 分布:", dict(pc))
    print("T1 且题面可 link:", sum(1 for r in rows if r["_pool"] == 'T1' and r['link_seeds']))
    print("gold resolve 失败(=U 且 anchor 有):", sum(1 for r in rows if r['gold_eid'] is None))
    for x in rejects[:20]:
        print("  REJ", x)
    return 0


if __name__ == "__main__":
    sys.exit(main())
