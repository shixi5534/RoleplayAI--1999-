# -*- coding: utf-8 -*-
"""灰机标准 300 条 RAG 测试集生成管线。

功能（两种模式）：
  1) --mode select --target 300
     读候选题池（scripts/rag_testset_candidates_300.py 的 CANDIDATES）
       → oracle 校验（每组证据词必须在 8358 块语料中命中 >0 块；
         ≥2 组的题每组都必须命中）
       → 按灰机维度配额（type/difficulty/depth/hop/text_len/chapter）
         确定性贪心选题（无随机，重复运行幂等）
       → 输出三件套：
         - data/knowledge/_audit/rag_testset_300.json          （终版题库）
         - data/knowledge/_audit/rag_testset_300_rejected.json （oracle 剔除记录）
         - data/docs/rag_testset_300.md                        （人可读文档）
     退出码：0=成功凑齐 target 条且全部配额满足；2=凑不齐（打印缺口）。

  2) --mode oracle-only --q <关键词>
     在候选池中查找 q 含关键词的题，逐组打印证据命中块数与块摘要，
     便于人工调试新题（不写任何文件）。

用法（项目根目录）：
  ./.venv/Scripts/python.exe -X utf8 scripts/gen_rag_testset_300.py --mode select --target 300
  ./.venv/Scripts/python.exe -X utf8 scripts/gen_rag_testset_300.py --mode oracle-only --q 牙仙
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from rag_testset_candidates_300 import CANDIDATES  # noqa: E402

CORPUS_PATH = ROOT / "data" / "knowledge" / "plot_corpus_wu_ming_zhe.json"
OUT_JSON = ROOT / "data" / "knowledge" / "_audit" / "rag_testset_300.json"
OUT_REJECTED = ROOT / "data" / "knowledge" / "_audit" / "rag_testset_300_rejected.json"
OUT_MD = ROOT / "data" / "docs" / "rag_testset_300.md"

# ── 灰机维度配额（每维合计 300）────────────────────────────────────────────
QUOTA_TYPE = {"factoid": 200, "multi-hop": 60, "reasoning": 30, "temporal": 10}
QUOTA_DIFFICULTY = {"easy": 150, "medium": 100, "hard": 50}
QUOTA_DEPTH = {"shallow": 170, "medium": 80, "deep": 50}
QUOTA_HOP = {"single": 200, "multi": 100}
QUOTA_TEXT_LEN = {"short": 100, "medium": 120, "long": 80}
CHAPTER_MIN = 20                       # 每章最少条数（1.4/1.7/1.9/1971/其他）
CHAPTER_ORDER = ["1.4", "1.7", "1.9", "1971", "其他"]
TYPE_ORDER = ["factoid", "multi-hop", "reasoning", "temporal"]

# 高频泛词黑名单：证据词出现这些即视为无效题（防虚增命中）
GENERIC_WORDS = {"时间", "世界", "发现", "历史", "故事", "剧情", "问题", "答案",
                 "the", "a", "an", "and", "of", "is", "he", "she", "it", "they"}


# ── 维度补齐规则（确定性）──────────────────────────────────────────────────

def text_len_bucket(q: str) -> str:
    """按题干字符长度分桶：short / medium / long。"""
    n = len(q)
    if n <= 17:
        return "short"
    if n <= 25:
        return "medium"
    return "long"


def fill_dims(cand: dict) -> dict:
    """补齐 dims 的 hop / difficulty / depth / text_len（已给出的字段不覆盖）。

    推导规则（确定性）：
      hop       = 显式标签；否则证据组 ≥2 视为 multi（题干场景组 + 答案组两级定位）
      depth     = deep: ≥2 组且 hop=multi；medium: ≥2 组或 hop=multi；其余 shallow
      difficulty= hard: deep；medium: depth=medium 或 hop=multi 或
                  type∈{reasoning, temporal}；其余 easy
      text_len  = 按 q 长度分桶
    """
    dims = dict(cand["dims"])
    n_groups = len(cand["evidence"])
    if "hop" not in dims:
        dims["hop"] = "multi" if n_groups >= 2 else "single"
    hop = dims["hop"]
    if "depth" not in dims:
        if n_groups >= 2 and hop == "multi":
            dims["depth"] = "deep"
        elif n_groups >= 2 or hop == "multi":
            dims["depth"] = "medium"
        else:
            dims["depth"] = "shallow"
    if "difficulty" not in dims:
        if dims["depth"] == "deep":
            dims["difficulty"] = "hard"
        elif dims["depth"] == "medium" or hop == "multi" \
                or dims["type"] in ("reasoning", "temporal"):
            dims["difficulty"] = "medium"
        else:
            dims["difficulty"] = "easy"
    dims.setdefault("text_len", text_len_bucket(cand["q"]))
    dims.setdefault("chapter", "其他")
    return dims


# ── oracle：语料词频扫描 ───────────────────────────────────────────────────

class Oracle:
    """对 8358 块 ASR 语料做证据词命中扫描（只读）。"""

    def __init__(self, corpus_path: Path) -> None:
        data = json.loads(corpus_path.read_text(encoding="utf-8"))
        # 每块保留 (text, doc_id, title) 用于摘要展示
        self.chunks = [
            (c.get("text", ""), c.get("doc_id", ""), c.get("title", ""))
            for c in data.get("chunks", [])
        ]

    def group_hits(self, group: list[str]) -> tuple[int, list[tuple]]:
        """返回（命中块数, [命中块摘要...]），命中=块正文包含组内任一关键词。"""
        hits = []
        for text, doc_id, title in self.chunks:
            kw = next((w for w in group if w in text), None)
            if kw is not None:
                hits.append((kw, doc_id, title, text))
        return len(hits), hits

    def check(self, evidence: list[list[str]]) -> tuple[bool, list[dict]]:
        """逐组校验：每组命中必须 >0。返回 (是否通过, 各组明细)。"""
        detail = []
        ok = True
        for gi, group in enumerate(evidence):
            n, hits = self.group_hits(group)
            detail.append({"group_index": gi, "group": group, "hits": n})
            if n <= 0:
                ok = False
        return ok, detail


# ── select 模式 ────────────────────────────────────────────────────────────

def validate_and_tag(oracle: Oracle) -> tuple[list[dict], list[dict]]:
    """oracle 校验 + 维度补齐。返回 (通过列表, 剔除列表)。"""
    valid: list[dict] = []
    rejected: list[dict] = []
    for idx, cand in enumerate(CANDIDATES):
        evidence = cand["evidence"]
        # 黑名单校验：证据词不得是高频泛词
        bad_words = [w for g in evidence for w in g if w.lower() in GENERIC_WORDS]
        if bad_words:
            rejected.append({"q": cand["q"], "evidence": evidence,
                             "reason": f"证据词含高频泛词：{bad_words}",
                             "group_hits": []})
            continue
        ok, detail = oracle.check(evidence)
        if not ok:
            rejected.append({"q": cand["q"], "evidence": evidence,
                             "reason": "存在证据组 0 命中（无效题，剔除）",
                             "group_hits": detail})
            continue
        item = {"q": cand["q"], "ref": cand["ref"], "evidence": evidence,
                "dims": fill_dims(cand), "source": cand["source"],
                "_idx": idx,
                "oracle_min_blocks": min(d["hits"] for d in detail)}
        valid.append(item)
    return valid, rejected




def _state_of(chosen_: list[dict]):
    """汇总已选集合的各维剩余配额与章节计数。"""
    DIMS = ("type", "difficulty", "depth", "hop", "text_len")
    remain = {
        "type": dict(QUOTA_TYPE), "difficulty": dict(QUOTA_DIFFICULTY),
        "depth": dict(QUOTA_DEPTH), "hop": dict(QUOTA_HOP),
        "text_len": dict(QUOTA_TEXT_LEN),
    }
    chapter_cnt: Counter = Counter()
    for c in chosen_:
        d = c["dims"]
        for dim in DIMS:
            if d[dim] in remain[dim]:
                remain[dim][d[dim]] -= 1
        chapter_cnt[d["chapter"]] += 1
    return remain, chapter_cnt


def _total_gap(remain: dict, chapter_cnt: Counter, target: int,
               n_chosen: int) -> int:
    gap = max(0, target - n_chosen)
    for dim in remain:
        gap += sum(v for v in remain[dim].values() if v > 0)
    for ch in CHAPTER_ORDER:
        gap += max(0, CHAPTER_MIN - chapter_cnt.get(ch, 0))
    return gap






def _class_of(dims: dict) -> str:
    """按（difficulty, depth, hop）把候选归入五个结构类：
      A=easy/shallow/single  B=hard/deep/multi  C=medium/medium/multi
      D=medium/medium/single E=medium/shallow/single
    """
    if dims["difficulty"] == "easy":
        return "A"
    if dims["difficulty"] == "hard":
        return "B"
    if dims["depth"] == "medium":
        return "C" if dims["hop"] == "multi" else "D"
    return "E"


def _alloc_class_targets(pool_by_type_class: dict, ) -> dict | None:
    """解 (type × class) 目标计数：满足 type 行和、类总量与 hop 耦合约束。

    类约束（由配额推导，见 _class_of）：
      A=150（全部 factoid）；B=50（hop multi 的 deep）；C=50（medium/multi）；
      D=30（medium/single/depth-medium）；E=20（medium/single/shallow）。
      hop.multi = B+C = 100；difficulty.medium = C+D+E = 100；
      depth.medium = C+D = 80。确定性枚举求解，无可行解返回 None。
    """
    pf = pool_by_type_class["factoid"]
    pm = pool_by_type_class["multi-hop"]
    pr = pool_by_type_class["reasoning"]
    pt = pool_by_type_class["temporal"]
    for b_mh in range(0, min(pm.get("B", 0), 10) + 1):        # B_mh + D_mh = 10
        d_mh = 10 - b_mh
        if d_mh > pm.get("D", 0):
            continue
        for b_t in range(0, min(pt.get("B", 0), 10) + 1):     # B_t + E_t = 10
            e_t = 10 - b_t
            if e_t > pt.get("E", 0):
                continue
            e_r = 20 - e_t                                    # E = E_r + E_t = 20
            if e_r > pr.get("E", 0):
                continue
            # B_f + D_f = 50（factoid 行），D_r = B_f + B_mh - 30
            lo = max(0, 50 - pf.get("D", 0), 30 - b_mh)
            hi = min(pf.get("B", 0), 50)
            for b_f in range(lo, hi + 1):
                d_f = 50 - b_f
                b_r = 50 - b_f - b_mh - b_t
                if b_r < 0 or b_r > pr.get("B", 0):
                    continue
                d_r = 30 - d_f - d_mh
                if d_r < 0 or d_r > pr.get("D", 0):
                    continue
                if e_r < 0:
                    continue
                return {("factoid", "A"): 150, ("factoid", "B"): b_f,
                        ("factoid", "D"): d_f,
                        ("multi-hop", "B"): b_mh, ("multi-hop", "C"): 50,
                        ("multi-hop", "D"): d_mh,
                        ("reasoning", "B"): b_r, ("reasoning", "D"): d_r,
                        ("reasoning", "E"): e_r,
                        ("temporal", "B"): b_t, ("temporal", "E"): e_t}
    return None


def select_300(valid: list[dict], target: int) -> tuple[list[dict], list[str]]:
    """确定性选题（构造式两阶段）：

    1) 精确求解 (type × class) 目标计数（类结构见 _class_of/_alloc_class_targets）；
    2) 在各类计数内，按 text_len 配额与章节下限做稀缺度贪心挑选具体条目，
       再用交换修复消除残余缺口。全程无随机。
    """
    pool_by_type_class: dict = {}
    for c in valid:
        key = (c["dims"]["type"], _class_of(c["dims"]))
        pool_by_type_class.setdefault(key[0], Counter())[key[1]] += 1
    targets = _alloc_class_targets(pool_by_type_class)
    if targets is None:
        return [], ["(type × class) 结构无可行解：请扩充对应类别的候选题"]

    # 单元格 = (type, class)；seed 题全部强制入选并占据所在格配额
    cell_targets = {k: v for k, v in targets.items() if v > 0}
    cell_used: Counter = Counter()
    remain_len = dict(QUOTA_TEXT_LEN)
    chapter_cnt: Counter = Counter()
    seeds = [c for c in valid if c["source"] == "seed"]
    chosen: list[dict] = list(seeds)
    used = {id(c) for c in seeds}
    for c in seeds:
        key = (c["dims"]["type"], _class_of(c["dims"]))
        cell_used[key] += 1
        remain_len[c["dims"]["text_len"]] -= 1
        chapter_cnt[c["dims"]["chapter"]] += 1
    for key, cnt in cell_used.items():
        if cnt > cell_targets.get(key, 0):
            return [], [f"seed 题超出 (type×class) 格 {key} 容量，请调整候选池"]
    # 章节稀缺优先：先挑章节池小的格内条目
    chapter_order = sorted(CHAPTER_ORDER,
                           key=lambda ch: sum(1 for c in valid
                                              if c["dims"]["chapter"] == ch))
    while len(chosen) < target:
        best, best_score, best_key = None, -1.0, None
        for c in valid:
            if id(c) in used:
                continue
            key = (c["dims"]["type"], _class_of(c["dims"]))
            if cell_used[key] >= cell_targets.get(key, 0):
                continue
            tl = c["dims"]["text_len"]
            score = 0.0
            if remain_len[tl] > 0:
                avail = sum(1 for v in valid
                            if id(v) not in used
                            and v["dims"]["text_len"] == tl
                            and cell_used[(v["dims"]["type"],
                                           _class_of(v["dims"]))]
                            < cell_targets.get((v["dims"]["type"],
                                                _class_of(v["dims"])), 0))
                score += remain_len[tl] / max(avail, 1)
            ch = c["dims"]["chapter"]
            if chapter_cnt[ch] < CHAPTER_MIN:
                score += (CHAPTER_MIN - chapter_cnt[ch]) \
                    * (chapter_order.index(ch) + 1) / 5.0
            if score > best_score:
                best, best_score, best_key = c, score, key
        if best is None:
            break
        chosen.append(best)
        used.add(id(best))
        cell_used[best_key] += 1
        remain_len[best["dims"]["text_len"]] -= 1
        chapter_cnt[best["dims"]["chapter"]] += 1

    # 交换修复残余缺口（保持 type/class 配额不变；seed 题不参与交换）
    _repair_cells(chosen, valid, cell_targets, cell_used, target,
                  locked={id(c) for c in seeds})

    remain, chapter_cnt = _state_of(chosen)
    gaps: list[str] = []
    if len(chosen) < target:
        gaps.append(f"总数缺口：选中 {len(chosen)} / {target}")
    for dim, quota in (("type", QUOTA_TYPE), ("difficulty", QUOTA_DIFFICULTY),
                       ("depth", QUOTA_DEPTH), ("hop", QUOTA_HOP),
                       ("text_len", QUOTA_TEXT_LEN)):
        for k, v in quota.items():
            left = remain[dim][k]
            if left > 0:
                gaps.append(f"{dim}.{k} 缺 {left} 条")
    for ch in CHAPTER_ORDER:
        if chapter_cnt[ch] < CHAPTER_MIN:
            gaps.append(f"chapter.{ch} 仅 {chapter_cnt[ch]} 条（要求 ≥{CHAPTER_MIN}）")
    return chosen, gaps


def _repair_cells(chosen: list[dict], valid: list[dict],
                  cell_targets: dict, cell_used: Counter, target: int,
                  locked: set | None = None) -> None:
    """交换修复：交换双方必须同 type 同 class（不影响已精确满足的配额），
    只改善 text_len / chapter 缺口。locked 中的题（seed）不参与交换。"""
    locked = locked or set()
    for _ in range(300):
        remain, chapter_cnt = _state_of(chosen)
        gap = _total_gap(remain, chapter_cnt, target, len(chosen))
        if gap == 0:
            return
        used = {id(c) for c in chosen}
        unselected = [c for c in valid if id(c) not in used]
        best_swap = None
        for s_idx, s in enumerate(chosen):
            if id(s) in locked:
                continue
            skey = (s["dims"]["type"], _class_of(s["dims"]))
            for u in unselected:
                ukey = (u["dims"]["type"], _class_of(u["dims"]))
                if ukey != skey:
                    continue
                tl_s, tl_u = s["dims"]["text_len"], u["dims"]["text_len"]
                r2 = dict(remain["text_len"])
                ok = True
                if tl_u != tl_s:
                    if r2[tl_u] <= 0:
                        ok = False
                    else:
                        r2[tl_u] -= 1
                        r2[tl_s] += 1
                        if r2[tl_s] > 0:
                            ok = False
                if not ok:
                    continue
                ch2 = chapter_cnt.copy()
                ch2[s["dims"]["chapter"]] -= 1
                ch2[u["dims"]["chapter"]] += 1
                g2 = _total_gap({**remain, "text_len": r2}, ch2,
                                target, len(chosen))
                if g2 <= gap and (best_swap is None or g2 < best_swap[0]):
                    best_swap = (g2, s_idx, u)
        if best_swap is None or best_swap[0] == gap:
            return
        _, s_idx, u = best_swap
        chosen[s_idx] = u


def finalize(chosen: list[dict]) -> list[dict]:
    """按（章 → type → 题池原顺序）排序并编号 R001…，输出终版字段。"""
    order = sorted(
        chosen,
        key=lambda c: (CHAPTER_ORDER.index(c["dims"]["chapter"]),
                       TYPE_ORDER.index(c["dims"]["type"]),
                       c["_idx"]),
    )
    out = []
    for i, c in enumerate(order, 1):
        out.append({
            "q": c["q"],
            "ref": c["ref"],
            "evidence": c["evidence"],
            "id": f"R{i:03d}",
            "dims": {
                "type": c["dims"]["type"],
                "difficulty": c["dims"]["difficulty"],
                "depth": c["dims"]["depth"],
                "hop": c["dims"]["hop"],
                "chapter": c["dims"]["chapter"],
                "text_len": c["dims"]["text_len"],
            },
            "oracle_min_blocks": c["oracle_min_blocks"],
            "source": c["source"],
        })
    return out


def write_outputs(final: list[dict], rejected: list[dict]) -> None:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(final, ensure_ascii=False, indent=1),
                        encoding="utf-8")
    OUT_REJECTED.write_text(json.dumps(rejected, ensure_ascii=False, indent=1),
                            encoding="utf-8")
    md = [_md_header(final)]
    for t in TYPE_ORDER:
        rows = [r for r in final if r["dims"]["type"] == t]
        md.append(f"\n## {t}（{len(rows)} 条）\n")
        md.append("| id | q | ref | evidence | dims | min_blocks | 来源 |")
        md.append("|---|---|---|---|---|---|---|")
        for r in rows:
            ev = " / ".join("[" + ",".join(g) + "]" for g in r["evidence"])
            d = r["dims"]
            dims = (f"{d['difficulty']}/{d['depth']}/{d['hop']}"
                    f"/{d['chapter']}/{d['text_len']}")
            q = r["q"].replace("|", "\\|")
            ref = r["ref"].replace("|", "\\|")
            md.append(f"| {r['id']} | {q} | {ref} | {ev} | {dims} "
                      f"| {r['oracle_min_blocks']} | {r['source']} |")
    OUT_MD.write_text("\n".join(md), encoding="utf-8")


def _md_header(final: list[dict]) -> str:
    def dist(field: str) -> str:
        cnt = Counter(r["dims"][field] for r in final)
        keys = ({"type": TYPE_ORDER, "chapter": CHAPTER_ORDER}
                .get(field) or sorted(cnt))
        return "，".join(f"{k}={cnt.get(k, 0)}" for k in keys if k in cnt or True)

    lines = [
        "# 《重返未来：1999》剧情 RAG 灰机标准测试集（300 条）",
        "",
        "- 标准来源：灰机 wiki（res1999.huijiwiki.com）剧情条目；14 条 seed 题"
        "沿用 scripts/eval_rag_huiji.py（source=seed），其余为 generated。",
        "- oracle 校验：每组证据词在 plot_corpus_wu_ming_zhe.json（8358 块 ASR 语料）"
        "中命中 ≥1 块；≥2 组的题每组均命中；`oracle_min_blocks` 为最弱证据组的命中块数。",
        "- 章节分组说明：语料 version 标签 1.4/1.7/1.9 对应灰机 5TH/6TH/7TH 章；"
        "「1971」= 绿湖噩梦（1.2）；联动与其余版本归「其他」。",
        "",
        "## 维度分布",
        f"- type：{dist('type')}",
        f"- difficulty：{dist('difficulty')}",
        f"- depth：{dist('depth')}",
        f"- hop：{dist('hop')}",
        f"- text_len：{dist('text_len')}",
        f"- chapter：{dist('chapter')}",
    ]
    return "\n".join(lines)


def run_select(target: int) -> int:
    if not CORPUS_PATH.exists():
        print(f"[FAIL] 找不到语料文件：{CORPUS_PATH}")
        return 1
    oracle = Oracle(CORPUS_PATH)
    print(f"[load] 语料块数 {len(oracle.chunks)}｜候选题 {len(CANDIDATES)} 条")
    valid, rejected = validate_and_tag(oracle)
    n_seed_valid = sum(1 for v in valid if v["source"] == "seed")
    print(f"[oracle] 通过 {len(valid)} 条（含 seed {n_seed_valid}）"
          f"｜剔除 {len(rejected)} 条")
    if n_seed_valid < 14:
        bad = [c["q"] for c in CANDIDATES
               if c["source"] == "seed"
               and not oracle.check(c["evidence"])[0]]
        print(f"[FAIL] seed 题出现 0 命中，请检查：{bad}")
        return 1

    chosen, gaps = select_300(valid, target)
    if len(chosen) < target or gaps:
        print(f"[FAIL] 无法凑齐 {target} 条或配额不满足，缺口：")
        for g in gaps:
            print(f"  - {g}")
        cur = Counter(c["dims"]["type"] for c in chosen)
        print(f"[info] 当前选中 type 分布：{dict(cur)}")
        return 2

    final = finalize(chosen)
    write_outputs(final, rejected)

    # 汇报统计
    print("\n==== 选题成功，维度分布 ====")
    for field in ("type", "difficulty", "depth", "hop", "text_len", "chapter"):
        cnt = Counter(r["dims"][field] for r in final)
        keys = {"type": TYPE_ORDER, "chapter": CHAPTER_ORDER}.get(field) \
            or sorted(cnt)
        print(f"  {field}: " + "，".join(f"{k}={cnt.get(k, 0)}" for k in keys))
    print(f"  source: {dict(Counter(r['source'] for r in final))}")
    print(f"\n[save] {OUT_JSON}")
    print(f"[save] {OUT_REJECTED}（剔除 {len(rejected)} 条）")
    print(f"[save] {OUT_MD}")
    return 0


# ── oracle-only 模式 ───────────────────────────────────────────────────────

def run_oracle_only(keyword: str) -> int:
    oracle = Oracle(CORPUS_PATH)
    matches = [c for c in CANDIDATES if keyword in c["q"]]
    if not matches:
        print(f"[FAIL] 候选池中没有 q 包含「{keyword}」的题")
        return 1
    for cand in matches:
        print(f"\n=== {cand['q']} ===")
        print(f"ref: {cand['ref']}")
        for gi, group in enumerate(cand["evidence"]):
            n, hits = oracle.group_hits(group)
            tag = "OK " if n > 0 else "ZERO"
            print(f"  [组{gi + 1}:{tag}] 命中 {n} 块  词={group}")
            for kw, doc_id, title, text in hits[:3]:
                snippet = text[:80].replace("\n", " ")
                print(f"      - ({kw}|{doc_id}) {snippet}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="灰机标准 300 条测试集生成管线")
    ap.add_argument("--mode", choices=["select", "oracle-only"], required=True)
    ap.add_argument("--target", type=int, default=300,
                    help="select 模式的目标条数（默认 300）")
    ap.add_argument("--q", type=str, default="",
                    help="oracle-only 模式：按题干关键词查找候选题")
    args = ap.parse_args()
    if args.mode == "select":
        return run_select(args.target)
    if not args.q:
        print("[FAIL] oracle-only 模式需要 --q <题干关键词>")
        return 1
    return run_oracle_only(args.q)


if __name__ == "__main__":
    raise SystemExit(main())
