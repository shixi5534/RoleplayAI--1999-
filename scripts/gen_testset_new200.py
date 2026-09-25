# -*- coding: utf-8 -*-
"""全新 200 题测试集生成（**排除现有 300 题**，同源灰机标准候选池）。

为什么要单独生成一份
----------------------
现有 ``rag_testset_300.json`` 已被反复用于调参与选参（别名桥、融合权重、保底名额、
补位重排……）。在同一份题上反复测，指标会带上"对这份题过拟合"的偏差——
新方案看起来更好，可能只是更贴合这 300 题的问法分布。
因此需要一份**与 300 题零交集**的题集做独立复核：
候选池共 575 条，300 题用掉 281 条，**剩余 294 条从未被测过**，从中按维度配额选 200 条。

与 ``gen_rag_testset_300.py`` 的关系
------------------------------------
候选池、oracle 校验（每组证据词必须在语料命中 >0 块）、维度补齐规则**全部复用**
（import 而非复制），保证两套管线口径一致；**配额不同**——300 题那套配额硬编码为
300 的结构（含 14 条 seed 强制入选），本脚本按 200 目标重算，且 seed 题已在旧题集中
（自动被排除），不参与。

确定性：无随机；候选按池内原始下标遍历，同分先到先得；重复运行逐位可复现。

用法（项目根目录）
------------------
    .venv/Scripts/python.exe -X utf8 scripts/gen_testset_new200.py
    .venv/Scripts/python.exe -X utf8 scripts/gen_testset_new200.py --target 200 --exclude rag_testset_300.json

产物
----
- ``data/knowledge/_audit/rag_testset_200_new.json``（终版题库，id 前缀 N，区别于 R）
- ``data/knowledge/_audit/rag_testset_200_new_rejected.json``（oracle 剔除记录）
- ``data/docs/rag_testset_200_new.md``（人可读）
退出码：0 成功（凑齐 target）｜2 凑不齐（打印缺口）
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

from gen_rag_testset_300 import (  # noqa: E402
    GENERIC_WORDS,
    Oracle,
    fill_dims,
)
from rag_testset_candidates_300 import CANDIDATES  # noqa: E402

CORPUS_PATH = ROOT / "data" / "knowledge" / "plot_corpus_wu_ming_zhe.json"
AUDIT_DIR = ROOT / "data" / "knowledge" / "_audit"
DEFAULT_EXCLUDE = AUDIT_DIR / "rag_testset_300.json"
OUT_JSON = AUDIT_DIR / "rag_testset_200_new.json"
OUT_REJECTED = AUDIT_DIR / "rag_testset_200_new_rejected.json"
OUT_MD = ROOT / "data" / "docs" / "rag_testset_200_new.md"
ID_PREFIX = "N"  # 与 300 题的 R 前缀区分，避免报告里混淆题集来源

# ── 目标配额：300 题集的原比例（200/60/30/10 等）缩放到 200 ─────────────────
# 剩余池的真实分布是 factoid 196 / multi-hop 82 / reasoning 12 / temporal 4，
# 因此 reasoning 与 temporal **拿不到**按比例的目标值，缺口由 _fit_quota 按
# 原比例补给仍有余量的类别（否则会死循环在"配额不可达"上）。
DESIRED_TYPE = {"factoid": 133, "multi-hop": 40, "reasoning": 20, "temporal": 7}
DESIRED_DIFFICULTY = {"easy": 100, "medium": 67, "hard": 33}
DESIRED_DEPTH = {"shallow": 113, "medium": 53, "deep": 33}
DESIRED_HOP = {"single": 133, "multi": 67}
DESIRED_TEXT_LEN = {"short": 67, "medium": 80, "long": 53}
# 章节下限按剩余池实际容量设定（1.4=13 / 1.7=8 / 1.9=9 / 1971=10），
# 目标是让每章都有代表题，而不是强行拉满导致选题失败。
CHAPTER_FLOOR = {"1.4": 8, "1.7": 6, "1.9": 6, "1971": 6}
DESIRED = {
    "type": DESIRED_TYPE,
    "difficulty": DESIRED_DIFFICULTY,
    "depth": DESIRED_DEPTH,
    "hop": DESIRED_HOP,
    "text_len": DESIRED_TEXT_LEN,
}


def _fit_quota(desired: dict[str, int], pool_counts: Counter, target: int) -> dict[str, int]:
    """把 desired 配额裁到池内可得上限，再把缺口按原比例补给仍有余量的类别。"""
    quota = {k: min(int(v), int(pool_counts.get(k, 0))) for k, v in desired.items()}
    deficit = target - sum(quota.values())
    while deficit > 0:
        free = {k: int(pool_counts.get(k, 0)) - quota.get(k, 0)
                for k in desired
                if int(pool_counts.get(k, 0)) - quota.get(k, 0) > 0}
        if not free:
            break
        total_free = sum(free.values())
        if deficit >= total_free:
            for k in free:
                quota[k] += free[k]
            deficit -= total_free
            continue
        # 确定性分配：先补给 desired 目标最大的类别（tie 按键名）
        for k in sorted(free, key=lambda k: (-desired[k], k)):
            if deficit <= 0:
                break
            take = min(deficit, free[k])
            quota[k] += take
            deficit -= take
    return quota


def build_pool(exclude_paths: list[Path]) -> tuple[list[dict], set[str]]:
    """排除已有题集里出现过的题干，返回 (候选, 被排除的 q 集合)。"""
    excluded: set[str] = set()
    for p in exclude_paths:
        if not p.is_file():
            continue
        data = json.loads(p.read_text(encoding="utf-8"))
        for it in data:
            if isinstance(it, dict) and it.get("q"):
                excluded.add(str(it["q"]))
    pool = [c for c in CANDIDATES if str(c.get("q")) not in excluded]
    return pool, excluded


def validate(oracle: Oracle, pool: list[dict]) -> tuple[list[dict], list[dict]]:
    """oracle 校验 + 维度补齐（规则与 300 题管线完全一致）。"""
    valid: list[dict] = []
    rejected: list[dict] = []
    for idx, cand in enumerate(pool):
        evidence = cand["evidence"]
        bad = [w for g in evidence for w in g if str(w).lower() in GENERIC_WORDS]
        if bad:
            rejected.append({"q": cand["q"], "reason": f"证据词含高频泛词：{bad}"})
            continue
        ok, detail = oracle.check(evidence)
        if not ok:
            rejected.append({"q": cand["q"], "reason": "存在证据组 0 命中",
                             "group_hits": detail})
            continue
        item = {"q": cand["q"], "ref": cand["ref"], "evidence": evidence,
                "dims": fill_dims(cand), "source": cand["source"],
                "_idx": idx,
                "oracle_min_blocks": min(d["hits"] for d in detail)}
        if cand.get("scenario_hints"):
            item["scenario_hints"] = cand["scenario_hints"]
        valid.append(item)
    return valid, rejected


def score_of(cand: dict, remain: dict[str, Counter], chapter_cnt: Counter) -> float:
    """稀缺度打分：优先补配额缺口大的维度，章节未达下限时额外加权。"""
    s = 0.0
    for dim in ("type", "difficulty", "depth", "hop", "text_len"):
        v = cand["dims"][dim]
        r = int(remain[dim].get(v, 0))
        if r > 0:
            s += 1.0 + r / max(1, sum(remain[dim].values()))
    ch = cand["dims"]["chapter"]
    floor = CHAPTER_FLOOR.get(ch, 0)
    if chapter_cnt[ch] < floor:
        s += 5.0 * (floor - chapter_cnt[ch])
    return s


def select(valid: list[dict], target: int) -> list[dict]:
    """确定性贪心：每轮取当前最"补缺口"的候选，平局按池内下标先到先得。"""
    pool_counts = {
        dim: Counter(c["dims"][dim] for c in valid)
        for dim in ("type", "difficulty", "depth", "hop", "text_len")
    }
    quota = {dim: _fit_quota(DESIRED[dim], pool_counts[dim], target)
             for dim in pool_counts}
    remain = {dim: Counter(quota[dim]) for dim in quota}
    chapter_cnt: Counter = Counter()
    used: set[int] = set()
    chosen: list[dict] = []
    while len(chosen) < target:
        best, best_score, best_idx = None, -1.0, None
        for c in valid:
            if c["_idx"] in used:
                continue
            dim_v = c["dims"]
            # 硬约束：type 配额已满则不再取（type 是主配额，其余维允许超出后自然回落）
            if remain["type"].get(dim_v["type"], 0) <= 0:
                continue
            s = score_of(c, remain, chapter_cnt)
            if s > best_score:
                best, best_score, best_idx = c, s, c["_idx"]
        if best is None:
            break
        chosen.append(best)
        used.add(best_idx)
        for dim in ("type", "difficulty", "depth", "hop", "text_len"):
            remain[dim][best["dims"][dim]] -= 1
        chapter_cnt[best["dims"]["chapter"]] += 1
    return chosen


def main() -> int:
    ap = argparse.ArgumentParser(description="全新 200 题测试集生成")
    ap.add_argument("--target", type=int, default=200)
    ap.add_argument("--exclude", default=str(DEFAULT_EXCLUDE),
                    help="逗号分隔的已有题集路径（题干出现过的候选全部排除）")
    ap.add_argument("--out", default=str(OUT_JSON))
    args = ap.parse_args()

    out_path = Path(args.out)
    rej_path = out_path.with_name(out_path.stem + "_rejected.json")
    md_path = ROOT / "data" / "docs" / (out_path.stem + ".md")

    exclude_paths = [Path(p.strip()) for p in str(args.exclude).split(",") if p.strip()]
    pool, excluded = build_pool(exclude_paths)
    print(f"[pool] 候选池 {len(CANDIDATES)}｜已排除（见于旧题集）{len(excluded)}"
          f"｜可用候选 {len(pool)}")

    oracle = Oracle(CORPUS_PATH)
    print(f"[oracle] 语料 {len(oracle.chunks)} 块")
    valid, rejected = validate(oracle, pool)
    print(f"[valid] oracle 通过 {len(valid)}｜剔除 {len(rejected)}")
    if not valid:
        print("[FAIL] 无可用候选题")
        return 2

    chosen = select(valid, args.target)
    if len(chosen) < args.target:
        print(f"[FAIL] 只凑到 {len(chosen)}/{args.target} 条（池内可用题不足）")
        return 2

    items = []
    for i, c in enumerate(chosen, start=1):
        items.append({
            "q": c["q"], "ref": c["ref"], "evidence": c["evidence"],
            "id": f"{ID_PREFIX}{i:03d}",
            "dims": {k: v for k, v in c["dims"].items()},
            "oracle_min_blocks": c["oracle_min_blocks"],
            "source": c["source"],
        })
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
    rej_path.write_text(json.dumps(rejected, ensure_ascii=False, indent=1), encoding="utf-8")

    # 分布自检
    dist = {dim: dict(Counter(it["dims"][dim] for it in items))
            for dim in ("type", "difficulty", "depth", "hop", "text_len", "chapter")}
    print(f"[out] {out_path}（{len(items)} 条）")
    for dim, d in dist.items():
        print(f"  {dim:11s} {d}")

    # 人可读文档
    lines = [
        f"# 全新 RAG 测试集（{len(items)} 条，与 300 题零交集）",
        "",
        f"- 生成脚本：`scripts/gen_testset_new200.py`（确定性，无随机）",
        f"- 候选来源：`scripts/rag_testset_candidates_300.py`（灰机标准同源）",
        f"- 已排除题干：{len(excluded)} 条（来自 {', '.join(p.name for p in exclude_paths)}）",
        f"- oracle 校验：每组证据词在 {len(oracle.chunks)} 块语料中命中 >0 块；"
        f"剔除 {len(rejected)} 条",
        f"- id 前缀 `{ID_PREFIX}`，与 300 题集的 `R` 前缀区分",
        "",
        "## 维度分布",
        "",
    ]
    for dim, d in dist.items():
        lines.append(f"- {dim}: " + "、".join(f"{k}={v}" for k, v in sorted(d.items())))
    lines += ["", "## 题目", ""]
    for it in items:
        ev = " / ".join("[" + ", ".join(g) + "]" for g in it["evidence"])
        d = it["dims"]
        lines.append(
            f"- **{it['id']}** `{d['type']}/{d['difficulty']}/{d['chapter']}` "
            f"{it['q']}  \n  ref: {it['ref']}  \n  evidence: {ev}"
        )
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[out] {md_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
