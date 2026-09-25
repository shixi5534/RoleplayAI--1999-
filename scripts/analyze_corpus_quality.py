# -*- coding: utf-8 -*-
"""语料块质量分析与「清洗收益」量化（只读，不改语料文件）。

背景：用户指出语料里英配/中配混杂、且存在质量缺陷。本脚本先给每块打质量标签，
再用**两种零重建方式**量化清洗的收益/代价：

  A. 语义掩码（`semantic.set_row_mask`）：把低质块从**语义召回**里屏蔽——
     测"低质块对召回的污染有多大"；
  B. 后置过滤（`chunks_transform`）：把低质块从**最终结果**里剔除——
     测"低质块占着名额的代价有多大"。

质量标签（保守，只标有明确证据的）：
  · foreign      —— 语言判定为 es/fr/de/pt/ja/ko/ru 等非目标语言
  · commentary   —— 含 UP 主解说标记（三连/关注/本期/视频/解说…），非游戏原文
  · duplicate    —— 文本前 200 字与更早出现的块相同（近重复，保留首个）
  · no_punct_zh  —— 中文块且完全无中文标点（机翻/OCR 连排，仅统计不屏蔽）

用法（项目根目录）
------------------
    # 只统计标签分布
    .venv/Scripts/python.exe -X utf8 scripts/analyze_corpus_quality.py --report
    # 三种配置对照评测（基线 / 语义掩码 / 后置过滤）
    .venv/Scripts/python.exe -X utf8 scripts/analyze_corpus_quality.py --apply-mask \
        --testset data/knowledge/_audit/rag_testset_300_clean.json \
        --out data/knowledge/_audit/corpus_clean_mask.json

退出码：0 正常｜1 环境缺失｜2 语义降级｜3 题集缺失
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from roleplay.config import get_settings  # noqa: E402
from roleplay.core.knowledge.factory import build_plot_registry  # noqa: E402

import diag_seedless_ceiling as D  # noqa: E402
import eval_plot_rag as E  # noqa: E402

DEFAULT_OUT = ROOT / "data" / "knowledge" / "_audit" / "corpus_clean_mask.json"
LOG_PATH = ROOT / "data" / "knowledge" / "_audit" / "_corpus_quality.log"

CJK = re.compile(r"[\u4e00-\u9fff]")
HIRA_KATA = re.compile(r"[\u3040-\u30ff]")
HANGUL = re.compile(r"[\uac00-\ud7af]")
CYRILLIC = re.compile(r"[\u0400-\u04ff]")
ZH_PUNCT = re.compile(r"[，。！？、；：]")
UP_STRONG = ("一键三连", "三连", "投币", "点赞", "下期视频", "本期视频", "我们下期",
             "up主", "UP主", "up主", "点点关注")          # 正典文本几乎不会出现
UP_WEAK = ("关注", "专栏", "视频", "解说", "攻略", "带你", "这期", "下期", "欢迎来到")  # 正典也会出现
UP_MARKERS = UP_STRONG + UP_WEAK   # 兼容旧调用
ES = {"el", "la", "los", "las", "es", "estaba", "como", "siempre", "qué", "por",
      "para", "con", "una", "un", "del", "que", "en", "no", "se", "su", "pero"}
FR = {"le", "la", "les", "des", "est", "une", "un", "que", "qui", "pour", "avec",
      "dans", "pas", "vous", "nous", "sur", "mais", "comme"}
DE = {"der", "die", "das", "und", "ist", "nicht", "mit", "ein", "eine", "sich",
      "auf", "für", "wir", "sie", "auch", "aber", "wie"}
PT = {"o", "a", "os", "as", "de", "que", "não", "uma", "um", "para", "com", "está",
      "você", "mais", "como", "isso"}
EN_SW = {"the", "and", "you", "that", "this", "with", "have", "what", "for", "not",
         "but", "are", "was", "his", "her", "they", "there", "from", "will", "been"}

_LOG: list[str] = []


def log(m: str) -> None:
    print(m, flush=True)
    _LOG.append(str(m))


def lang_profile(t: str) -> str:
    if CJK.search(t) and len(CJK.findall(t)) / max(1, len(t)) > 0.2:
        return "zh"
    if HIRA_KATA.search(t):
        return "ja"
    if HANGUL.search(t):
        return "ko"
    if CYRILLIC.search(t) and len(CYRILLIC.findall(t)) / max(1, len(t)) > 0.2:
        return "ru"
    words = re.findall(r"[a-zA-Zà-ÿÀ-ß']+", t.lower())
    if not words:
        return "other"
    n = len(words)

    def hit(s: set[str]) -> float:
        return sum(1 for w in words if w in s) / max(1, n)

    sc = {"en": hit(EN_SW) * 1.6, "es": hit(ES), "fr": hit(FR), "de": hit(DE), "pt": hit(PT)}
    if re.search(r"[ñ¿¡]", t) or re.search(r"\b(estaba|siempre|también)\b", t, re.I):
        sc["es"] += 0.15
    if re.search(r"[çœ]|\b(être|était)\b", t, re.I):
        sc["fr"] += 0.10
    if re.search(r"[äöüß]|\b(nicht|eine)\b", t, re.I):
        sc["de"] += 0.10
    best = max(sc, key=lambda k: sc[k])
    return best if sc[best] > 0.05 else "unknown"


def label_chunks(chunks: list, docs: dict | None = None) -> tuple[dict[str, list[str]], dict[str, int]]:
    """给每块打标签，返回 {hash: [标签]} 与统计。

    ⚠️ 2026-09-17 修正（重要）：初版把"关注/专栏/视频"等**弱标记单独命中**就判
    ``commentary``，导致**灰机正典文本被误判为 UP 主解说**（实证：R027/R206/N197
    三题的正解块是 `huiji_今夜星光灿烂` 等正典页，只因正文含"人们所关注的""本系列专栏"
    就被标成解说）。误标会污染清洗与审计结论，故收紧为：
      - ``commentary``：**强标记 ≥1**（一键三连/投币/下期视频/up主…），或弱标记 ≥2；
        且 uploader 含"灰机"的正典来源**默认不判**（除非强标记命中）。
      - ``duplicate``：改名语义 —— 仅标记"后出现的重复副本"（``dup_secondary``），
        并**移出屏蔽集合**：重复块的内容本身是正典对白，应做"去重保留一份"而非"剔除"。
    """
    labels: dict[str, list[str]] = {}
    stats: Counter = Counter()
    seen_prefix: dict[str, str] = {}
    for c in chunks:
        h = str(getattr(c, "hash", "") or "")
        t = str(getattr(c, "text", "") or "")
        did = str(getattr(c, "doc_id", "") or "")
        uploader = str((docs or {}).get(did, {}).get("uploader") or "")
        is_canon_src = "灰机" in uploader
        tags: list[str] = []
        lp = lang_profile(t)
        if lp in ("es", "fr", "de", "pt", "ja", "ko", "ru", "other"):
            tags.append("foreign")
        n_strong = sum(1 for m in UP_STRONG if m in t)
        n_weak = sum(1 for m in UP_WEAK if m in t)
        if n_strong >= 1 or (n_weak >= 2 and not is_canon_src):
            tags.append("commentary")
        pref = t[:200]
        if len(pref) > 40:
            if pref in seen_prefix:
                tags.append("dup_secondary")
            else:
                seen_prefix[pref] = h
        if lp == "zh" and not ZH_PUNCT.search(t):
            tags.append("no_punct_zh")
        labels[h] = tags
        for tag in tags:
            stats[tag] += 1
    stats["total"] = len(chunks)
    return labels, dict(stats)


def main() -> int:
    ap = argparse.ArgumentParser(description="语料块质量分析与清洗收益量化")
    ap.add_argument("--character", default="wu_ming_zhe")
    ap.add_argument("--testset", default=str(ROOT / "data/knowledge/_audit/rag_testset_300_clean.json"))
    ap.add_argument("--report", action="store_true", help="只输出标签分布")
    ap.add_argument("--apply-mask", action="store_true", help="三种配置对照评测")
    ap.add_argument("--mask-dup", action="store_true",
                    help="屏蔽集合额外包含 dup_secondary（近重复副本），验证去重是否腾出名额")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--allow-degraded", action="store_true")
    args = ap.parse_args()

    settings = get_settings()
    registry = build_plot_registry(settings)
    retr = registry.get(args.character)
    if retr is None:
        log("[FAIL] 图谱未加载")
        return 1
    sem = getattr(retr, "semantic", None)
    if sem is None and not args.allow_degraded:
        log("[FAIL] 语义通道已降级（--allow-degraded 可强行继续）")
        return 2

    chunks = retr.corpus.chunks
    corpus_raw = json.loads((ROOT / "data" / "knowledge" / "plot_corpus_wu_ming_zhe.json")
                            .read_text(encoding="utf-8"))
    docs = corpus_raw.get("docs") or {}
    labels, stats = label_chunks(chunks, docs)
    log(f"[label] 语料 {stats['total']} 块")
    for k in ("foreign", "commentary", "dup_secondary", "no_punct_zh"):
        log(f"  {k}: {stats.get(k, 0)}")
    bad = sum(1 for h, t in labels.items() if t)
    log(f"  至少带一个标签的块：{bad}（{bad/max(1,stats['total']):.1%}）")
    # 屏蔽集合：只含**内容确实非本作品正典**的两类。
    # dup_secondary（近重复副本）不屏蔽——它的内容就是正典对白，只应"去重保留一份"。
    skip_tags = {"foreign", "commentary"}
    if args.mask_dup:
        skip_tags.add("dup_secondary")
    n_bad = sum(1 for h, t in labels.items() if skip_tags & set(t))
    log(f"  屏蔽集合（foreign∪commentary）：{n_bad} 块（{n_bad/max(1,stats['total']):.1%}）")
    pref_tags: dict[str, list[str]] = {}
    for c in chunks:
        pref_tags[str(getattr(c, "text", "") or "")[:200]] = labels.get(
            str(getattr(c, "hash", "") or ""), [])
    bad_prefs = {k for k, v in pref_tags.items() if set(v) & skip_tags}

    if args.report or not args.apply_mask:
        LOG_PATH.write_text("\n".join(_LOG), encoding="utf-8")
        return 0

    # ── A. 语义掩码 ────────────────────────────────────────────────────────
    hashes = sem.hashes
    keep = np.ones(len(hashes), dtype=bool)
    h2i = {}
    for i, h in enumerate(hashes):
        h2i[str(h)] = i
        tags = labels.get(str(h)) or []
        if skip_tags & set(tags):
            keep[i] = False
    log(f"[mask] 语义索引 {len(hashes)} 行，屏蔽 {int((~keep).sum())} 行")

    top = int(getattr(settings, "plot_max_chunks", 3) or 3)
    lex_fb = int(getattr(settings, "plot_lexical_fallback", 2) or 0)
    inject_chars = int(getattr(settings, "plot_context_max_chars", 1000) or 0)
    items = E.load_testset(Path(args.testset))
    if args.limit:
        items = items[: args.limit]
    oracle = E.build_oracle(retr.corpus, items)
    log(f"[load] 题量 {len(items)}｜{Path(args.testset).name}")

    def run(label: str, mask: bool, post_filter: bool) -> dict[str, Any]:
        if mask:
            sem.set_row_mask(keep)
        else:
            sem.set_row_mask(None)
        t0 = time.time()
        n_pass = n_inj = 0
        for it in items:
            fn = None
            if post_filter:
                def fn(_q, chs):
                    # 用预计算的 pref 标签表判定（与 A 档同一套规则，避免两处口径漂移）
                    return [c for c in chs
                            if str(getattr(c, "text", "") or "")[:200] not in bad_prefs]
            row = E.evaluate_case(retr, it, oracle[str(it.get("id"))], top, lex_fb,
                                  inject_chars, chunks_transform=fn)
            n_pass += int(bool(row.get("strict_pass")))
            n_inj += int(bool(row.get("inject_pass")))
        r = {"label": label, "strict_pass_n": n_pass, "strict_pass": D.rate(n_pass, len(items)),
             "inject_pass_n": n_inj, "inject_pass": D.rate(n_inj, len(items)),
             "elapsed_s": round(time.time() - t0, 1)}
        log(f"  [{label}] strict {n_pass}/{len(items)}｜inject {n_inj}｜{r['elapsed_s']}s")
        return r

    results = [run("基线", False, False),
               run("A 语义掩码（屏蔽低质块）", True, False),
               run("B 后置过滤（剔除低质块）", False, True)]
    sem.set_row_mask(None)

    base = results[0]
    report = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "labels": stats,
        "masked_rows": int((~keep).sum()),
        "config": {"testset": Path(args.testset).name, "cases": len(items)},
        "results": results,
        "delta": [{"label": r["label"],
                   "d_strict": r["strict_pass_n"] - base["strict_pass_n"],
                   "d_inject": r["inject_pass_n"] - base["inject_pass_n"]}
                  for r in results],
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    log("\n==== 摘要 ====")
    for d in report["delta"]:
        log(f"{d['label']:<24} Δstrict={d['d_strict']:+d}　Δinject={d['d_inject']:+d}")
    log(f"[out] {out}")
    LOG_PATH.write_text("\n".join(_LOG), encoding="utf-8")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except BaseException as exc:  # noqa: BLE001
        import traceback
        try:
            (ROOT / "data" / "knowledge" / "_audit" / "_corpus_quality_crash.txt").write_text(
                f"{time.strftime('%Y-%m-%d %H:%M:%S')}\n{traceback.format_exc()}",
                encoding="utf-8")
        except Exception:
            pass
        print(f"[CRASH] {exc!r}", flush=True)
        raise
