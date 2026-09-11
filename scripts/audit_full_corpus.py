# -*- coding: utf-8 -*-
"""抽取质量审计 · 全量版：2477 块逐块过缺陷规则（不抽样）。

缺陷规则（全部可机械判定，来自 `docs/剧情图谱抽取质量审计.md` 的人工审计结论）：

| 标记 | 含义 | 严重度 |
|---|---|---|
| ``empty``              | 整块无实体无关系 → 疑似漏抽（配合文本信息量打分判断） | 高 |
| ``hallucinated_entity``| 实体名与其别名**都不出现在正文里** → 臆造实体 | 高 |
| ``hallucinated_relation`` | 关系的 src/dst 解析回实体后，该实体在正文里无据 → 臆造关系端点 | 高 |
| ``dangling_relation``  | 关系端点不在本块 entities 的 name/aliases 里 → 建图时被丢弃 | 高 |
| ``self_loop``          | src == dst 自环边 | 中 |
| ``non_cn_predicate``   | 关系谓语含拉丁字母 → 违反「谓语必须中文」 | 中 |
| ``alias_self_ref``     | 别名与正名相同（自指） | 低 |
| ``alias_dup``          | 同一实体内别名重复 | 低 |
| ``flat_confidence``    | 该块所有关系置信度完全相同 → 模型敷衍信号 | 低 |
| ``relation_heavy``     | 关系数 > 实体数 → 臆造倾向 | 低 |

产物：
  data/knowledge/_audit/full_issues.jsonl  逐块明细（含命中规则与证据）
  data/knowledge/_audit/full_report.json   汇总统计
  docs/剧情图谱全量审查报告.md              可读报告

可选修复（``--fix``）：自环边、悬空边、别名自指/重复、非中文谓语（默认不删，见 --drop-non-cn）。
臆造类只标记不自动删（需模型复核），除非显式 ``--fix-hallucinated``。

用法：
  python scripts/audit_full_corpus.py
  python scripts/audit_full_corpus.py --fix             # 修机械缺陷
  python scripts/audit_full_corpus.py --fix --drop-non-cn
  python scripts/audit_full_corpus.py --strict          # 验收门禁：不达标退出码 1

``--strict`` 阈值（默认关闭，保持旧调用方行为不变；实测值见 2026 全量审计）：

| 检查项 | 阈值 | 当前实测 |
|---|---|---|
| 缓存解析失败块数 | = 0 | 0 |
| 空块占比（empty/chunks） | ≤ 0.20 | 0.007 |
| 平均每块关系数 | ≥ 0.5 | 2.08 |
| 臆造实体块占比 | ≤ 0.20 | 0.000 |
| 悬空关系块占比 | ≤ 0.25 | 0.000 |
| 自环边块占比 | ≤ 0.05 | 0.000 |
| 非中文谓语块占比 | ≤ 0.05 | 0.000 |
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from roleplay.config import get_settings  # noqa: E402
from roleplay.core.knowledge.plot_graph import (  # noqa: E402
    _PRONOUN_CANONICAL,
    is_noise_entity,
)

AUDIT = ROOT / "data" / "knowledge" / "_audit"

# ── --strict 验收门禁阈值（M0-3）────────────────────────────────────────────
# 只卡「重大数据事故」级别的问题（抽取整体失败 / 大规模臆造），不卡低危项
# （flat_confidence、noise_entity 实测占比 38%/30%，属已知噪声，不阻断交付）。
STRICT_MAX_PARSE_FAILED = 0  # 缓存读取/解析失败块数（= 抽取产物不可用）
STRICT_MAX_EMPTY_RATIO = 0.20  # 空块占比（整轮漏抽的信号）
STRICT_MIN_REL_PER_CHUNK = 0.5  # 平均每块关系数（relations 总数异常下界）
STRICT_MAX_HALLU_ENTITY_RATIO = 0.20  # 臆造实体块占比
STRICT_MAX_DANGLING_RATIO = 0.25  # 悬空关系块占比
STRICT_MAX_SELF_LOOP_RATIO = 0.05  # 自环边块占比
STRICT_MAX_NON_CN_RATIO = 0.05  # 非中文谓语块占比

_RE_LATIN = re.compile(r"[A-Za-z]{2,}")
# 文本信息量：大写专名（英文块）/ 引号内称呼 / 数字年份，用于判断空块是否真的没内容
_RE_PROPER = re.compile(r"\b(?:[A-Z][a-z]{2,}|[A-Z]{2,})\b")
_RE_CJK_NAME = re.compile(r"[\u4e00-\u9fff]{2,6}(?:姐|哥|先生|女士|小姐|夫人|教|门|会|队|组)")


def _norm(s: str) -> str:
    return (s or "").strip().lower().replace(" ", "")


def _in_text(name: str, text_norm: str) -> bool:
    n = _norm(name)
    return bool(n) and n in text_norm


def audit_chunk(text: str, data: dict) -> tuple[list[str], dict]:
    ents = [e for e in (data.get("entities") or []) if isinstance(e, dict)]
    rels = [r for r in (data.get("relations") or []) if isinstance(r, dict)]
    text_norm = _norm(text)
    flags: list[str] = []
    detail: dict = {}

    if not ents and not rels:
        flags.append("empty")

    # 实体侧
    hallu_e = []
    for e in ents:
        name = str(e.get("name") or "")
        aliases = [str(a) for a in (e.get("aliases") or []) if str(a).strip()]
        if not (_in_text(name, text_norm) or any(_in_text(a, text_norm) for a in aliases)):
            hallu_e.append(name)
        if _norm(name) in _PRONOUN_CANONICAL:
            flags.append("pronoun_entity")
        if is_noise_entity(name):
            flags.append("noise_entity")
        na = _norm(name)
        seen = set()
        for a in aliases:
            if _norm(a) == na:
                flags.append("alias_self_ref")
            if _norm(a) in seen:
                flags.append("alias_dup")
            seen.add(_norm(a))
    if hallu_e:
        flags.append("hallucinated_entity")
        detail["hallucinated_entities"] = hallu_e

    # 关系侧
    name_pool = {_norm(str(e.get("name") or "")) for e in ents}
    for e in ents:
        for a in (e.get("aliases") or []):
            name_pool.add(_norm(str(a)))

    # 端点接地表：端点字符串（正名或别名）→ 它所属实体在正文里是否有据。
    # 有了这层解析，「正名写中文译名、别名带原文表层形式」的合法写法才不会被
    # 整片误判为臆造（此前只看端点字面串，导致中文端点全被判臆造）。
    endpoint_grounded: dict[str, bool] = {}
    for e in ents:
        ename = str(e.get("name") or "")
        ealiases = [str(a) for a in (e.get("aliases") or []) if str(a).strip()]
        grounded = _in_text(ename, text_norm) or any(
            _in_text(a, text_norm) for a in ealiases
        )
        for key in (_norm(ename), *(_norm(a) for a in ealiases)):
            if key:
                endpoint_grounded[key] = endpoint_grounded.get(key, False) or grounded

    def _hallu_endpoint(x: str) -> bool:
        key = _norm(x)
        if key in endpoint_grounded:
            return not endpoint_grounded[key]
        return not _in_text(x, text_norm)

    hallu_r, dangling, selfloop, noncn = [], [], [], []
    confs = []
    for r in rels:
        src, dst = str(r.get("src") or ""), str(r.get("dst") or "")
        rel = str(r.get("relation") or "")
        confs.append(float(r.get("confidence", 0.7) or 0.7))
        if src == dst:
            selfloop.append(f"{src}->{rel}")
        if _hallu_endpoint(src) or _hallu_endpoint(dst):
            hallu_r.append(f"{src}-{rel}->{dst}")
        if _norm(src) not in name_pool or _norm(dst) not in name_pool:
            dangling.append(f"{src}-{rel}->{dst}")
        if _RE_LATIN.search(rel):
            noncn.append(rel)
    for items, key, flag in (
        (selfloop, "self_loops", "self_loop"),
        (hallu_r, "hallucinated_relations", "hallucinated_relation"),
        (dangling, "dangling_relations", "dangling_relation"),
        (noncn, "non_cn_predicates", "non_cn_predicate"),
    ):
        if items:
            flags.append(flag)
            detail[key] = items[:10]
    if len(rels) > 1 and len(set(confs)) == 1:
        flags.append("flat_confidence")
    if rels and len(rels) > len(ents):
        flags.append("relation_heavy")

    return sorted(set(flags)), detail


def _strict_checks(
    *,
    chunks: int,
    relations_total: int,
    parse_failed: int,
    per_flag_chunks: Counter,
) -> list[tuple[str, str, float, str, bool]]:
    """--strict 门禁检查项：返回 [(检查项, 阈值说明, 实际值, 实际值展示, 是否通过)]。"""

    def _ratio(flag: str) -> float:
        return (per_flag_chunks.get(flag, 0) / chunks) if chunks else 0.0

    rel_per_chunk = (relations_total / chunks) if chunks else 0.0
    return [
        (
            "缓存解析失败块数",
            f"= {STRICT_MAX_PARSE_FAILED}",
            float(parse_failed),
            f"{parse_failed}",
            parse_failed <= STRICT_MAX_PARSE_FAILED,
        ),
        (
            "空块占比 empty/chunks",
            f"≤ {STRICT_MAX_EMPTY_RATIO}",
            _ratio("empty"),
            f"{_ratio('empty'):.4f}",
            _ratio("empty") <= STRICT_MAX_EMPTY_RATIO,
        ),
        (
            "平均每块关系数",
            f"≥ {STRICT_MIN_REL_PER_CHUNK}",
            rel_per_chunk,
            f"{rel_per_chunk:.3f}",
            rel_per_chunk >= STRICT_MIN_REL_PER_CHUNK,
        ),
        (
            "臆造实体块占比",
            f"≤ {STRICT_MAX_HALLU_ENTITY_RATIO}",
            _ratio("hallucinated_entity"),
            f"{_ratio('hallucinated_entity'):.4f}",
            _ratio("hallucinated_entity") <= STRICT_MAX_HALLU_ENTITY_RATIO,
        ),
        (
            "悬空关系块占比",
            f"≤ {STRICT_MAX_DANGLING_RATIO}",
            _ratio("dangling_relation"),
            f"{_ratio('dangling_relation'):.4f}",
            _ratio("dangling_relation") <= STRICT_MAX_DANGLING_RATIO,
        ),
        (
            "自环边块占比",
            f"≤ {STRICT_MAX_SELF_LOOP_RATIO}",
            _ratio("self_loop"),
            f"{_ratio('self_loop'):.4f}",
            _ratio("self_loop") <= STRICT_MAX_SELF_LOOP_RATIO,
        ),
        (
            "非中文谓语块占比",
            f"≤ {STRICT_MAX_NON_CN_RATIO}",
            _ratio("non_cn_predicate"),
            f"{_ratio('non_cn_predicate'):.4f}",
            _ratio("non_cn_predicate") <= STRICT_MAX_NON_CN_RATIO,
        ),
    ]


def _informativeness(text: str, lang: str) -> int:
    """粗略信息量打分：专名/组织称呼越多，越不该是空抽取。"""
    if lang == "zh":
        return len(_RE_CJK_NAME.findall(text))
    return len({m for m in _RE_PROPER.findall(text)})


def main() -> int:
    ap = argparse.ArgumentParser(description="剧情图谱抽取质量全量审查（不抽样）")
    ap.add_argument("--character", default="wu_ming_zhe")
    ap.add_argument("--fix", action="store_true", help="修复机械缺陷（自环/悬空/别名自指重复）")
    ap.add_argument("--drop-non-cn", action="store_true", help="--fix 时一并删除非中文谓语的关系")
    ap.add_argument("--fix-hallucinated", action="store_true", help="一并删除臆造实体/关系（谨慎）")
    ap.add_argument(
        "--strict",
        action="store_true",
        help="验收门禁：发现重大问题（解析失败>0 / 空块占比>0.20 / 平均每块关系数<0.5 / "
        "臆造实体块占比>0.20 / 悬空关系块占比>0.25 / 自环边块占比>0.05 / "
        "非中文谓语块占比>0.05）时返回退出码 1；不加此开关恒返回 0（旧行为）",
    )
    args = ap.parse_args()

    settings = get_settings()
    corpus_path = Path(settings.plot_corpus_dir) / f"plot_corpus_{args.character}.json"
    cache_dir = Path(settings.plot_cache_dir) / args.character
    corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
    chunks = corpus["chunks"]
    AUDIT.mkdir(parents=True, exist_ok=True)

    flag_counter: Counter = Counter()
    per_flag_chunks: Counter = Counter()
    total_e = total_r = 0
    parse_failed = 0
    fixed_files = 0
    empty_rich: list[dict] = []
    issues_path = AUDIT / "full_issues.jsonl"
    fp = issues_path.open("w", encoding="utf-8")

    for c in chunks:
        p = cache_dir / f"{c['hash']}.json"
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            data = {"entities": [], "relations": []}
            parse_failed += 1  # 缓存缺失或坏 JSON：抽取产物不可用，--strict 会卡住
        text = c["text"]
        total_e += len(data.get("entities") or [])
        total_r += len(data.get("relations") or [])

        flags, detail = audit_chunk(text, data)
        for f in flags:
            flag_counter[f] += 1
            per_flag_chunks[f] += 1

        if "empty" in flags:
            score = _informativeness(text, c.get("lang") or "en")
            empty_rich.append(
                {"hash": c["hash"], "lang": c.get("lang"), "version": c.get("version") or "",
                 "score": score, "text": text}
            )

        if flags:
            fp.write(
                json.dumps(
                    {"hash": c["hash"], "lang": c.get("lang"), "version": c.get("version") or "",
                     "doc_id": c.get("doc_id"), "flags": flags, **detail},
                    ensure_ascii=False,
                )
                + "\n"
            )

        if args.fix and flags:
            # 先序列化留底：下面会**原地**改 dict（e["aliases"] = ...），
            # 若直接拿 data 与 new 比较，二者引用同一批对象会恒等，导致改动写不回盘。
            before = json.dumps(data, ensure_ascii=False, sort_keys=True)
            ents = [e for e in (data.get("entities") or []) if isinstance(e, dict)]
            rels = [r for r in (data.get("relations") or []) if isinstance(r, dict)]
            text_norm = _norm(text)
            kept_e = []
            for e in ents:
                name = str(e.get("name") or "")
                if args.fix_hallucinated and not (
                    _in_text(name, text_norm)
                    or any(_in_text(str(a), text_norm) for a in (e.get("aliases") or []))
                ):
                    continue
                al, seen = [], set()
                na = _norm(name)
                for a in (e.get("aliases") or []):
                    a = str(a)
                    if _norm(a) == na or _norm(a) in seen:
                        continue
                    seen.add(_norm(a))
                    al.append(a)
                e["aliases"] = al
                kept_e.append(e)
            pool = {_norm(str(e.get("name") or "")) for e in kept_e}
            for e in kept_e:
                pool |= {_norm(a) for a in e["aliases"]}
            kept_r = []
            for r in rels:
                src, dst = str(r.get("src") or ""), str(r.get("dst") or "")
                rel = str(r.get("relation") or "")
                if src == dst:
                    continue
                if _norm(src) not in pool or _norm(dst) not in pool:
                    continue
                if args.drop_non_cn and _RE_LATIN.search(rel):
                    continue
                if args.fix_hallucinated and not (_in_text(src, text_norm) and _in_text(dst, text_norm)):
                    continue
                kept_r.append(r)
            new = {"entities": kept_e, "relations": kept_r}
            if json.dumps(new, ensure_ascii=False, sort_keys=True) != before:
                p.write_text(json.dumps(new, ensure_ascii=False), encoding="utf-8")
                fixed_files += 1
    fp.close()

    empty_rich.sort(key=lambda x: -x["score"])
    report = {
        "chunks": len(chunks),
        "entities_total": total_e,
        "relations_total": total_r,
        "flag_chunk_counts": dict(per_flag_chunks),
        "empty_blocks": len(empty_rich),
        "empty_rich_top": [
            {"hash": e["hash"], "score": e["score"], "lang": e["lang"], "version": e["version"],
             "text": e["text"][:160]}
            for e in empty_rich[:40]
        ],
        "empty_score_distribution": dict(Counter(_bucket(e["score"]) for e in empty_rich)),
        "fixed_files": fixed_files,
        "parse_failed": parse_failed,
    }
    (AUDIT / "full_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({k: v for k, v in report.items() if k != "empty_rich_top"},
                     ensure_ascii=False, indent=2))
    print(f"\n[full-audit] 逐块明细 → {issues_path}")
    print(f"[full-audit] 汇总 → {AUDIT / 'full_report.json'}")
    if not args.strict:
        return 0  # 默认行为与旧版一致（恒 0），不打破既有调用方
    checks = _strict_checks(
        chunks=len(chunks),
        relations_total=total_r,
        parse_failed=parse_failed,
        per_flag_chunks=per_flag_chunks,
    )
    print("\n[strict] 验收门禁检查：")
    for name, threshold, _value, shown, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}（阈值 {threshold}）实际 {shown}")
    failed = [name for name, _t, _v, _s, ok in checks if not ok]
    if failed:
        print(f"\n[strict] 未通过 {len(failed)} 项：{'、'.join(failed)}")
        print("[strict] 退出码 1（修完再跑一次；不需要门禁就去掉 --strict）")
        return 1
    print("\n[strict] 全部通过，退出码 0")
    return 0


def _bucket(s: int) -> str:
    if s == 0:
        return "0（确实没什么可抽）"
    if s <= 2:
        return "1-2（低）"
    if s <= 5:
        return "3-5（中）"
    return "6+（高，疑似真漏抽）"


if __name__ == "__main__":
    raise SystemExit(main())
