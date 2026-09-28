# -*- coding: utf-8 -*-
"""生成 gold 缺陷**旁挂清单**（sidecar）—— 不改题集本体（项目红线：不改用例）。

用途：
  - R005 / R127 / R170 三题的 gold 关键词经审计为**假阳性**（子串巧合 / 比喻 / 无关引文），
    它们会永久压低基线并误导优化方向；
  - 本 sidecar 以**独立文件**记录缺陷、正字与证据，供评测脚本**单独统计**，
    而**不修改** `rag_testset_300_cn.json` 本身（保持题面与历史可比）。

输出：data/knowledge/_audit/testset_300cn_gold_defects.json
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DEFECTS = {
    "R005": {
        "q": "洞穴的囚徒篇的故事主要发生在什么载具上？",
        "gold": ["Rockin", "ship", "号船"],
        "defect_type": "substring_coincidence",
        "problem": ("'号船' 的唯一语料命中是 activity__24101_地球上最后的夜晚:16.0.1 中的"
                    "「前 APPLe **号船**长」—— 子串巧合，并非载具；"
                    "'Rockin' 与 '摇滚苹果号' 在语料层均 0 次命中。"),
        "evidence_chunk": "activity__24101_地球上最后的夜晚:16.0.1",
        "corrected_keywords": ["APPLe号", "摇滚苹果号", "Rockin"],
        "note": "正字需人工确认（语料无 Rockin/摇滚苹果号 字样，可能答案写作 APPLe号）。",
    },
    "R127": {
        "q": "福格先生发明的大型装置是什么？",
        "gold": ["purifier", "净化机", "purification"],
        "defect_type": "unrelated_quote",
        "problem": ("'purifier' 与 '净化机' 在语料层 0 次命中；'purification' 仅 1 次，"
                    "出现在英文哲学引文 'The greatest purification of all is, therefore, science'"
                    "（mainline__105_洞穴的囚徒:13.0.0），与「装置」无关。"),
        "evidence_chunk": "mainline__105_洞穴的囚徒:13.0.0",
        "corrected_keywords": ["雾气净化器", "净化器"],
        "note": ("真实答案写作「雾气净化器」，在 activity__23101_圣火纪行_东区黎明 有 5 块。"
                 "另有别名缺口：'福格先生' 与图中 '福葛先生'（属主 雾行者）差一字。"),
    },
    "R170": {
        "q": "人们向何处去篇里拉普拉斯的重要装置是什么？",
        "gold": ["玩具盒", "toy box"],
        "defect_type": "metaphor",
        "problem": ("'玩具盒' 的唯一命中 activity__27101_1987宇宙组曲:17.1.0 是比喻句"
                    "「宇宙在她眼前展开，如同……玩具盒子。」；'toy box' 0 次命中。"),
        "evidence_chunk": "activity__27101_1987宇宙组曲:17.1.0",
        "corrected_keywords": ["玩具箱"],
        "note": "正字写作「玩具箱」，有 33 块（含 activity__36101_人们向何处去 多块）。",
    },
}


def main() -> int:
    chunks = json.loads((ROOT / "data/compendium_rag/chunks.json").read_text(encoding="utf-8"))["chunks"]
    ts = json.loads((ROOT / "data/knowledge/_audit/rag_testset_300_cn.json").read_text(encoding="utf-8"))
    by = {str(c["id"]): c for c in ts["cases"]}

    # 逐条核验修正后的关键词确实在语料中存在
    for qid, d in DEFECTS.items():
        d["corrected_keywords_verified"] = {
            k: sum(1 for c in chunks if k in c["text"]) for k in d["corrected_keywords"]
        }
        d["original_gold_in_corpus"] = {
            k: sum(1 for c in chunks if k in c["text"]) for k in d["gold"]
        }
        d["case_present"] = qid in by

    doc = {
        "kind": "gold_defect_sidecar",
        "testset": "data/knowledge/_audit/rag_testset_300_cn.json",
        "generated_at": "2026-09-28",
        "policy": ("**不修改题集本体**（项目红线 SESSION2 §5.5）。本文件仅供评测脚本"
                   "单独统计 / 人工复核；引用指标时须注明「已剔除 N 道 gold 缺陷题」。"),
        "n_defects": len(DEFECTS),
        "impact": "300cn full 口径池内 miss 14 -> 有效 11（另 3 道为 gold 缺陷）",
        "defects": DEFECTS,
    }
    out = ROOT / "data/knowledge/_audit/testset_300cn_gold_defects.json"
    out.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[ok] -> {out}")
    for qid, d in DEFECTS.items():
        print(f"  {qid}: gold 语料命中 {d['original_gold_in_corpus']}")
        print(f"        修正词命中 {d['corrected_keywords_verified']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
