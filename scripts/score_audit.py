# -*- coding: utf-8 -*-
"""抽取质量审计 · 第三步：拿云端重抽结果给本地 7B 打分。

输入：
  data/knowledge/_audit/sample.json            抽样（含本地抽取）
  data/knowledge/_audit/cloud_extraction.json  云端重抽 + 人工判定

输出：
  data/knowledge/_audit/report.json            机读指标
  docs/剧情图谱抽取质量审计.md                  可读报告

判定口径（以云端重抽为参考答案、人工 verdict 为最终裁决）：
  - 实体精确率 = 云端也抽到的本地实体 / 本地实体总数
  - 实体召回率 = 本地也抽到的云端实体 / 云端实体总数
  - 关系精确率 = 云端也抽到的本地关系 / 本地关系总数（按 src|relation|dst 归一后比对）
  - 空块漏抽率 = 云端有实体但本地全空的块 / 空块样本数

用法：
  python scripts/score_audit.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(Path(__file__).resolve()).parents[1]
sys.path.insert(0, str(ROOT / "src"))

AUDIT = ROOT / "data" / "knowledge" / "_audit"


def _norm(s: str) -> str:
    return (s or "").strip().lower().replace(" ", "")


def _ent_key(e: dict) -> str:
    return _norm(str(e.get("name") or ""))


def _rel_key(r: dict) -> str:
    return f'{_norm(r.get("src"))}|{_norm(r.get("relation"))}|{_norm(r.get("dst"))}'


def main() -> int:
    sample = json.loads((AUDIT / "sample.json").read_text(encoding="utf-8"))
    cloud = json.loads((AUDIT / "cloud_extraction.json").read_text(encoding="utf-8"))
    by_hash = {r["hash"]: r for r in sample}
    verdicts = {r["hash"]: r for r in cloud["results"]}

    tp_e = tp_r = n_local_e = n_local_r = n_cloud_e = n_cloud_r = 0
    # 端点对口径：只看 (src,dst) 是否命中，不看谓语措辞——谓语同义改写很常见，
    # 逐字比对会严重低估，因此两个口径都报。
    tp_pair = n_local_pair = n_cloud_pair = 0
    empty_total = empty_missed = 0
    per_group: dict[str, Counter] = {}
    rows = []

    for h, v in verdicts.items():
        s = by_hash.get(h)
        if not s:
            continue
        local_e = s["local"]["entities"]
        local_r = s["local"]["relations"]
        c = v.get("cloud") or {}
        cloud_e = c.get("entities") or []
        cloud_r = [r for r in (c.get("relations") or []) if float(r.get("confidence", 0)) > 0]

        lk_e = {_ent_key(e) for e in local_e}
        ck_e = {_ent_key(e) for e in cloud_e}
        lk_r = {_rel_key(r) for r in local_r}
        ck_r = {_rel_key(r) for r in cloud_r}

        hit_e = len(lk_e & ck_e)
        hit_r = len(lk_r & ck_r)
        lp = {f'{_norm(r.get("src"))}|{_norm(r.get("dst"))}' for r in local_r}
        cp = {f'{_norm(r.get("src"))}|{_norm(r.get("dst"))}' for r in cloud_r}
        hit_p = len(lp & cp)

        g = s["group"]
        # cloud18 是对照组：它的「本地缓存」本身就是云端产出，不能参与本地质量统计
        if g != "cloud18":
            tp_e += hit_e
            tp_r += hit_r
            n_local_e += len(lk_e)
            n_local_r += len(lk_r)
            n_cloud_e += len(ck_e)
            n_cloud_r += len(ck_r)
            tp_pair += hit_p
            n_local_pair += len(lp)
            n_cloud_pair += len(cp)

        per_group.setdefault(g, Counter())["blocks"] += 1
        per_group[g]["local_e"] += len(lk_e)
        per_group[g]["local_r"] += len(lk_r)
        per_group[g]["cloud_e"] += len(ck_e)
        per_group[g]["cloud_r"] += len(ck_r)
        per_group[g]["hit_e"] += hit_e
        per_group[g]["hit_r"] += hit_r

        if g == "empty":
            empty_total += 1
            if ck_e and not lk_e:
                empty_missed += 1

        rows.append(
            {
                "hash": h,
                "group": g,
                "verdict": v["verdict"],
                "issues": v.get("issues") or [],
                "local": f"E{len(lk_e)}/R{len(lk_r)}",
                "cloud": f"E{len(ck_e)}/R{len(ck_r)}",
                "hit": f"E{hit_e}/R{hit_r}",
                "note": v.get("note", ""),
            }
        )

    def div(a: int, b: int) -> float:
        return round(a / b, 3) if b else 0.0

    report = {
        "sample_blocks": len(rows),
        "scored_blocks": sum(1 for r in rows if r["group"] != "cloud18"),
        "entity_precision": div(tp_e, n_local_e),
        "entity_recall": div(tp_e, n_cloud_e),
        "relation_precision": div(tp_r, n_local_r),
        "relation_recall": div(tp_r, n_cloud_r),
        "pair_precision": div(tp_pair, n_local_pair),
        "pair_recall": div(tp_pair, n_cloud_pair),
        "counts": {
            "local_entities": n_local_e,
            "local_relations": n_local_r,
            "cloud_entities": n_cloud_e,
            "cloud_relations": n_cloud_r,
            "matched_entities": tp_e,
            "matched_relations": tp_r,
        },
        "empty_block_miss_rate": div(empty_missed, empty_total),
        "verdict_dist": dict(Counter(r["verdict"] for r in rows)),
        "issue_freq": dict(Counter(i for r in rows for i in r["issues"])),
        "by_group": {g: dict(c) for g, c in per_group.items()},
    }
    (AUDIT / "report.json").write_text(
        json.dumps({**report, "rows": rows}, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    vd = report["verdict_dist"]
    lines = [
        "# 剧情图谱抽取质量审计（本地 qwen2.5:7b vs 云端）",
        "",
        f"- 样本：{report['sample_blocks']} 块（contrib 非空 / empty 空缓存 / cloud18 云端补抽对照组）",
        "- 方法：分层抽样 → 云端逐块重抽 + 人工判定 → 与本地缓存逐项比对",
        "",
        "## 一、总体指标",
        "",
        "| 指标 | 值 | 含义 |",
        "|---|---|---|",
        f"| 实体精确率 | {report['entity_precision']:.0%} | 本地抽的实体里，云端也认可的比例 |",
        f"| 实体召回率 | {report['entity_recall']:.0%} | 云端抽到的实体里，本地也抽到的比例 |",
        f"| 关系精确率（谓语全等） | {report['relation_precision']:.0%} | src+谓语+dst 三元组逐字一致 |",
        f"| 关系精确率（端点对） | {report['pair_precision']:.0%} | 只看 (src,dst) 是否命中，容忍谓语同义改写 |",
        f"| 关系召回率（端点对） | {report['pair_recall']:.0%} | 云端抽到的关系中本地也覆盖的比例 |",
        f"| 空块漏抽率 | {report['empty_block_miss_rate']:.0%} | 本地输出空、但确实有内容的块占比 |",
        "",
        f"> 参与打分的为 {report['scored_blocks']} 块（cloud18 对照组 {len(rows) - report['scored_blocks']} 块不计入）。"
        f"本地共抽 {n_local_e} 实体 / {n_local_r} 关系；云端 {n_cloud_e} 实体 / {n_cloud_r} 关系。",
        "> 云端刻意更保守：证据不足的关系直接不输出，因此关系数量明显更少、精确率口径天然吃亏。",
        "",
        "## 二、逐块判定",
        "",
        "| # | 分组 | 本地 | 云端 | 命中 | 判定 | 主要问题 |",
        "|---|---|---|---|---|---|---|",
    ]
    for i, r in enumerate(rows, 1):
        lines.append(
            f"| {i} | {r['group']} | {r['local']} | {r['cloud']} | {r['hit']} | "
            f"**{r['verdict']}** | {'、'.join(r['issues']) or '—'} |"
        )
    lines += [
        "",
        f"判定分布：{'、'.join(f'{k} {v}' for k, v in vd.items())}",
        "",
        "## 三、问题频次",
        "",
        "| 问题 | 出现块数 |",
        "|---|---|",
    ]
    for k, v in sorted(report["issue_freq"].items(), key=lambda kv: -kv[1]):
        lines.append(f"| {k} | {v} |")
    lines += ["", "## 四、审计触发的修复", ""]
    for f in cloud.get("_meta", {}).get("fixes", []):
        lines += [
            f"**{f['id']} · {f['finding']}**  ",
            f"→ 处置：{f['action']}  ",
            f"`{f['file']}`  ",
            "",
        ]
    lines += ["", "## 五、逐块说明", ""]
    for i, r in enumerate(rows, 1):
        lines.append(f"**#{i} `{r['hash']}`（{r['group']}）— {r['verdict']}**  ")
        lines.append(f"{r['note']}  ")
        lines.append("")

    out = ROOT / "docs" / "剧情图谱抽取质量审计.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"\n[audit] 报告 → {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
