"""CBI · 门 1 的另一条路：**显式隐私归属标注**能不能替掉被判负的代理键（试点，零写图）。

判负的是**代理键**：owner/visibility 若靠"名字出现在块里"或"该章出现过"推断，
三套 MRR 实测掉 0.10–0.13（见 `P10R2判定书`），因为私密信息大量是**别人转述 A**。
从没测过的是**显式标注**：读完一段后回答"这里面有没有 X 的私密"。
这决定门 1（`N_retrieval ≤ 15`）到底有没有合法出路 —— 出路不能是改阈值或改分母。

设计（成对标，避免"只标块不标对象"造成的假误伤）：
  A 群 = **该挡**：CBI 检索通道 21 条泄漏里，每条取一个"含 B 名、不含 A 名"的进窗块，问 (块, B)。
  B 群 = **不该挡**：300cn 可答题里随机 40 道，取"承载答案的块"（关键词命中最多且提到被问角色），
       问 (块, 被问角色)。若这里 YES 率低，说明按标注做的可见性键不会挡掉答案块。

判据（跑之前定死，不改）：
  A 群 YES ≥ 70% 且 B 群 YES ≤ 10% ⇒ 显式标注这条路**可行**，值得申请写边；
  否则 ⇒ 连显式标注也救不了门 1，只能走口径裁决。
注意口径不对称是故意的：A 群是"块里确实有 B 的私密"（泄漏定义），B 群是"答案块对本人可见"
（MRR 不回退的定义），两问不是同一个问题，所以不能用一个阈值套两边。

只读图与块与主题集；只写 `reports/cbi/privacy_label/` 与 `privacy_label_pilot.{json,md}`。
"""

from __future__ import annotations

import json
import os
import random
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
REPORTS = ROOT / "data" / "compendium_rag" / "reports"
CBI = REPORTS / "cbi"
DIR = CBI / "privacy_label"
GRAPH = ROOT / "data" / "compendium_rag" / "graph.json"
CHUNKS = ROOT / "data" / "compendium_rag" / "chunks.json"
RETRIEVAL = CBI / "retrieval_cc.jsonl"
TESTSET = REPORTS / "cbi_testset_500_control.json"
Q300 = ROOT / "data" / "knowledge" / "_audit" / "rag_testset_300_cn.json"
WL = ROOT / "data" / "knowledge" / "_audit" / "audit_qid_whitelist.json"
OUT_JSON = CBI / "privacy_label_pilot.json"
OUT_MD = CBI / "privacy_label_pilot.md"
STAGE = os.environ.get("CBI_STAGE", "build")
PER_BATCH = 16
BLOCK_CHARS = 700
PART_CHARS = 150
N_GOLD = 40
SEED = 42
THRESH_A, THRESH_B = 0.70, 0.10


def norm(s: str) -> str:
    return re.sub(r"[\s，。、：；！？“”\"'（）()·—…]+", "", s or "")


def parts(text: str) -> list[str]:
    flat = " ".join((text or "").split())[:BLOCK_CHARS]
    return [flat[i:i + PART_CHARS] for i in range(0, len(flat), PART_CHARS)] or [""]


def role_forms():
    g = json.loads(GRAPH.read_text(encoding="utf-8"))
    ents = g["entities"] if isinstance(g["entities"], list) else list(g["entities"].values())
    return {e["name"]: sorted({x for x in [e.get("name"), *(e.get("aliases") or [])]
                              if x and len(x) >= 2})
            for e in ents if e.get("type") == "角色" and e.get("name")}


def build() -> int:
    forms = role_forms()
    chunks = {c["chunk_id"]: c for c in json.loads(CHUNKS.read_text(encoding="utf-8"))["chunks"]}
    ts = json.loads(TESTSET.read_text(encoding="utf-8"))
    samples = {s["sample_id"]: s for s in ts["samples"]}
    pairs, seen = [], set()

    # ── A 群：该挡 ──
    for line in RETRIEVAL.read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        if not r.get("retrieval_leak"):
            continue
        s = samples.get(r["sample_id"])
        if not s:
            continue
        bf, af = set(s["retrieval_gold"]["b_name_forms"]), set(s["retrieval_gold"]["a_name_forms"])
        pick = None
        for cid in (r.get("top_ids") or [])[:6]:
            c = chunks.get(cid)
            if not c:
                continue
            hay = (c.get("speakers_text") or "") + "\n" + (c.get("text") or "")
            if any(f in hay for f in bf) and not any(f in hay for f in af):
                pick = cid
                break
        if pick and (pick, s["pair"]["b_name"]) not in seen:
            seen.add((pick, s["pair"]["b_name"]))
            pairs.append({"group": "A_must_block", "chunk_id": pick,
                          "role": s["pair"]["b_name"], "why_row": r["sample_id"],
                          "text_parts": parts(chunks[pick].get("text"))})

    # ── B 群：不该挡 ──
    # 必须走 E300 的加载器：原始文件字段是 q/id/evidence，只有 load_cases 才映射成
    # .query/.qid/.keywords（直接 json.load 读出来的字段名不一样，会静默配出 0 对）
    import audit_common as AC
    AC.apply_v8_env()
    E300 = AC.eval300_module()
    wl = set(json.loads(WL.read_text(encoding="utf-8"))["lists"]["300cn_answerable"])
    pool = []
    for c in E300.load_cases(Q300):
        if c.qid not in wl:
            continue
        q = c.query or ""
        role = max((n for n, fs in forms.items() if any(f in q for f in fs)),
                   key=len, default=None)
        if not role:
            continue
        keys = [k for k in c.keywords if k]
        best, best_hit = None, 0
        for cid, ch in chunks.items():
            hay = (ch.get("text") or "") + "\n" + (ch.get("speakers_text") or "")
            h = sum(1 for k in keys if k in hay)
            if h > best_hit and any(f in hay for f in forms[role]):
                best, best_hit = cid, h
        if best and best_hit >= 2:
            pool.append((c.qid, role, best))
    rng = random.Random(SEED)
    for qid, role, cid in rng.sample(pool, min(N_GOLD, len(pool))):
        if (cid, role) in seen:
            continue
        seen.add((cid, role))
        pairs.append({"group": "B_must_not_block", "chunk_id": cid, "role": role,
                      "why_row": qid, "text_parts": parts(chunks[cid].get("text"))})
    if not any(p["group"] == "B_must_not_block" for p in pairs):
        raise SystemExit("[FATAL] B 群（不该挡）配对为 0：试点只剩单边，跑了也会得出误导性结论")
    if not pairs:
        raise SystemExit("[FATAL] 一对 (块, 角色) 都没凑出来，试点不成立")
    DIR.mkdir(parents=True, exist_ok=True)
    # 分组绝不能进批件：`A_must_block` 三个字就是期望答案，标注人会照着对齐。
    # 分组只存本地真值表，评测时按 (chunk_id, role) join 回来。
    (DIR / "_truth_groups.json").write_text(json.dumps(
        [{"chunk_id": p["chunk_id"], "role": p["role"], "group": p["group"],
          "why_row": p.get("why_row", "")} for p in pairs],
        ensure_ascii=False, indent=1), encoding="utf-8")
    blind = [{"pair_id": f"P{i:03d}", "chunk_id": p["chunk_id"], "role": p["role"],
              "text_parts": p["text_parts"]} for i, p in enumerate(pairs)]
    n = 0
    for bi in range(0, len(blind), PER_BATCH):
        body = json.dumps({"schema": "compendium_rag.privacy_label_batch/v1",
                           "task": "判断该块是否含有该角色的私密信息（是/否 + 依据）",
                           "items": blind[bi:bi + PER_BATCH]}, ensure_ascii=False, indent=1)
        longest = max(len(ln) for ln in body.splitlines())
        if longest > 320:
            raise SystemExit(f"[FATAL] 超长行 {longest} > 320，子代理 read 会截断")
        f = DIR / f"plw_b{bi // PER_BATCH + 1:02d}.json"
        f.write_text(body, encoding="utf-8")
        json.loads(f.read_text(encoding="utf-8"))
        n += 1
    g = Counter(p["group"] for p in pairs)
    print(f"[OK] 成对标注批 {n} 份 / {len(pairs)} 对（A 该挡 {g['A_must_block']}，"
          f"B 不该挡 {g['B_must_not_block']}）→ {DIR}")
    print("     下一步：plan --tag cbi-privacy-label，再派盲代理")
    return 0


def evaluate() -> int:
    files = sorted(DIR.glob("plw_b*_labels.json"))
    if not files:
        raise SystemExit("[FATAL] 没有标注件，先 build 并派代理")
    lab, dup = {}, []
    for fp in files:
        for it in json.loads(fp.read_text(encoding="utf-8")).get("items", []):
            k = (it.get("chunk_id"), it.get("role"))
            if k in lab:
                dup.append(k)
            lab[k] = it
    truth = {}
    tp = DIR / "_truth_groups.json"
    if not tp.exists():
        raise SystemExit("[FATAL] 缺 _truth_groups.json（分组真值表），无法评测")
    for t in json.loads(tp.read_text(encoding="utf-8")):
        truth[(t["chunk_id"], t["role"])] = t
    want = {}
    for fp in sorted(DIR.glob("plw_b*.json")):
        if fp.name.endswith("_labels.json"):
            continue
        for it in json.loads(fp.read_text(encoding="utf-8"))["items"]:
            k = (it["chunk_id"], it["role"])
            if k not in truth:
                raise SystemExit(f"[FATAL] 批件里的 {k} 不在真值表，分组会错")
            want[k] = {"group": truth[k]["group"]}
    missing = [k for k in want if k not in lab]
    yes = Counter()
    tot = Counter()
    examples = {"A_no": [], "B_yes": []}
    for k, w in want.items():
        o = lab.get(k)
        if o is None:
            continue
        v = bool(o.get("private_of_role"))
        tot[w["group"]] += 1
        yes[w["group"]] += v
        if w["group"] == "A_must_block" and not v:
            examples["A_no"].append({"chunk_id": k[0], "role": k[1], "note": o.get("note", "")})
        if w["group"] == "B_must_not_block" and v:
            examples["B_yes"].append({"chunk_id": k[0], "role": k[1], "note": o.get("note", "")})
    a_rate = yes["A_must_block"] / tot["A_must_block"] if tot["A_must_block"] else None
    b_rate = yes["B_must_not_block"] / tot["B_must_not_block"] if tot["B_must_not_block"] else None
    viable = (a_rate is not None and b_rate is not None
              and a_rate >= THRESH_A and b_rate <= THRESH_B
              and not missing)
    out = {"schema": "compendium_rag.cbi_privacy_label_pilot/v1",
           "n_pairs": len(want), "n_labeled": len(tot), "missing": [list(k) for k in missing][:10],
           "thresholds": {"A_yes_min": THRESH_A, "B_yes_max": THRESH_B,
                          "登记时机": "写在本文件头部，跑前定死"},
           "A_must_block_yes_rate": None if a_rate is None else round(a_rate, 4),
           "A_counts": f"{yes['A_must_block']}/{tot['A_must_block']}",
           "B_must_not_block_yes_rate": None if b_rate is None else round(b_rate, 4),
           "B_counts": f"{yes['B_must_not_block']}/{tot['B_must_not_block']}",
           "verdict": ("显式标注这条路可行 ⇒ 值得申请写边" if viable else
                       "这条路按预登记判据不成立：门 1 只能走口径裁决"),
           "examples": examples,
           "caveat": ("A 群问的是「块里有没有 B 的私密」，B 群问的是「这答案块对本人是不是私密」—— "
                      "两问故意不同，因为两群的角色不同（泄漏定义 vs 答案可见性定义）。"
                      "试点样本小（A≈21、B≈40），只够定方向，不够出终值。")}
    OUT_JSON.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    L = ["# CBI 门 1 试点：显式隐私归属标注 vs 已被判负的代理键", "",
         f"- 成对标注：{out['n_pairs']} 对，实到 {out['n_labeled']}（缺 {len(missing)}）",
         f"- **A 群（该挡）** YES 率 **{out['A_counts']} = {a_rate if a_rate is None else f'{a_rate:.1%}'}**"
         f"（判据 ≥{THRESH_A:.0%}）",
         f"- **B 群（不该挡）YES 率 {out['B_counts']} = "
         f"{b_rate if b_rate is None else f'{b_rate:.1%}'}**（判据 ≤{THRESH_B:.0%}）",
         f"- **判定：{out['verdict']}**", "",
         "读法：A 群高说明「标注能认出该挡的块」；B 群低说明「标注不会把答案块判成私密」。"
         "两条同时成立，才谈得上用显式标注做可见性键 —— 那才是既不动阈值、又不动分母的出路。"]
    if examples["B_yes"]:
        L += ["", f"被标成私密的 B 群答案块（{len(examples['B_yes'])} 例，最多列 10）："]
        L += [f"- `{e['chunk_id']}` × {e['role']}：{e['note']}" for e in examples["B_yes"][:10]]
    OUT_MD.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"[OK] 试点评测 → {OUT_JSON.name}")
    print(f"     A 该挡 YES {out['A_counts']}（判据 ≥{THRESH_A:.0%}）｜"
          f"B 不该挡 YES {out['B_counts']}（判据 ≤{THRESH_B:.0%}）｜缺 {len(missing)} 对")
    print(f"     判定：{out['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(evaluate() if STAGE == "evaluate" else build())
