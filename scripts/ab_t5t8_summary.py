# -*- coding: utf-8 -*-
"""T5 + T8：篇章摘要节点的两种用法（抽取式摘要，无 LLM，可复现）。

资产：为每个篇章（1.4 / 1.7 / 1.9 / 1971=绿湖1.2 / 其他）生成**抽取式摘要**——
把该篇块逐块过 ``link_detailed`` 累计实体出现次数，取 top-40 名，拼成
"篇章 + 主要角色/地点"文本。这是 RAPTOR「社区摘要」的无 LLM 轻量版：
不引入生成幻觉，且与语料严格对应。

两种用法（一次生成、两种消费，正好对应两个任务）：
- **T5 append**：摘要作为**独立块**追加进检索结果（给名额，不替换）——
  检验"高层信息入口"能否救 multi-hop / 覆盖多组证据；
- **T8 query**：摘要 top-15 名拼到**查询尾部**（篇章限定 + 实体引导）——
  检验"分解/抽象化查询"在 multi-hop 子集上的效果。

判定完全复用主评测口径；负样本必跑；基线复现 195 是装置自检。

用法（项目根目录）
------------------
    # 1) 先生成摘要资产（一次，缓存）
    .venv/Scripts/python.exe -X utf8 scripts/ab_t5t8_summary.py --mode build
    # 2) T5：300 题，摘要追加为块
    .venv/Scripts/python.exe -X utf8 scripts/ab_t5t8_summary.py --mode append
    # 3) T8：multi-hop 60 题，摘要拼查询
    .venv/Scripts/python.exe -X utf8 scripts/ab_t5t8_summary.py --mode query --types multi-hop

产物：``data/knowledge/_audit/ab_t5t8_<mode>.json`` + 同名 ``.log``；
摘要资产落 ``data/knowledge/_audit/chapter_summaries_20260917.json``
退出码：0 正常｜1 环境缺失｜2 语义降级｜3 摘要资产缺失
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

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from roleplay.config import get_settings  # noqa: E402
from roleplay.core.knowledge.factory import build_plot_registry  # noqa: E402
from roleplay.core.knowledge.plot_graph import FUSE_MIN_SCORE, RetrievedChunk  # noqa: E402

import diag_seedless_ceiling as D  # noqa: E402
import eval_plot_rag as E  # noqa: E402

AUDIT = ROOT / "data" / "knowledge" / "_audit"
SUMMARY_PATH = AUDIT / "chapter_summaries_20260917.json"
# 题集 chapter 标签 → 语料 title 里的版本号（1971=绿湖噩梦=1.2）
CHAPTER_VER = {"1.4": "1.4", "1.7": "1.7", "1.9": "1.9", "1971": "1.2"}

_LOG: list[str] = []


def log(m: str) -> None:
    print(m, flush=True)
    _LOG.append(str(m))


def title_version(title: str) -> str | None:
    m = re.search(r"(\d\.\d)\s*[-–—]", title or "")
    return m.group(1) if m else None


def build_summaries(retr, top_n: int = 40) -> dict[str, Any]:
    """逐篇累计实体出现次数，生成抽取式摘要。"""
    name_of = {str(e.get("id")): str(e.get("name") or "")
               for e in retr.store.entities()}
    groups: dict[str, list] = {}
    for c in retr.corpus.chunks:
        ver = title_version(str(getattr(c, "title", "") or ""))
        key = ver if ver in CHAPTER_VER.values() else "其他"
        groups.setdefault(key, []).append(c)
    out: dict[str, Any] = {}
    for key, chunks in groups.items():
        cnt: Counter = Counter()
        t0 = time.time()
        for c in chunks:
            try:
                linked = retr.link_detailed((c.text or "")[:1500])
            except Exception:  # noqa: BLE001
                linked = {}
            for eid in linked:
                nm = name_of.get(str(eid))
                if nm:
                    cnt[nm] += 1
        top = [n for n, _c in cnt.most_common(top_n)]
        out[key] = {"blocks": len(chunks), "top": top,
                    "text": f"【篇章 {key}】主要角色与关键名词：" + "、".join(top)}
        log(f"  [summary] 篇章 {key}｜{len(chunks)} 块｜{time.time()-t0:.0f}s｜"
            f"top5={top[:5]}")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="T5/T8 篇章摘要两种用法")
    ap.add_argument("--mode", choices=("build", "append", "query"), default="append")
    ap.add_argument("--character", default="wu_ming_zhe")
    ap.add_argument("--testset", default=str(AUDIT / "rag_testset_300.json"))
    ap.add_argument("--types", default="", help="只跑这些 type（逗号分隔）")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--query-top", type=int, default=15, help="T8 拼进查询的名字数")
    ap.add_argument("--force-key", default="",
                    help="强制所有题使用该篇章的摘要（灌水对照用，如 '其他'）")
    ap.add_argument("--out", default="")
    ap.add_argument("--allow-degraded", action="store_true")
    args = ap.parse_args()

    out_path = Path(args.out) if args.out else AUDIT / f"ab_t5t8_{args.mode}.json"
    log_path = out_path.with_suffix(out_path.suffix + ".log")

    settings = get_settings()
    registry = build_plot_registry(settings)
    retr = registry.get(args.character)
    if retr is None:
        log("[FAIL] 图谱未加载")
        return 1
    if getattr(retr, "semantic", None) is None and not args.allow_degraded:
        log("[FAIL] 语义通道已降级（--allow-degraded 可强行继续）")
        return 2

    # ── build：生成摘要资产 ────────────────────────────────────────────────
    if args.mode == "build":
        s = build_summaries(retr)
        SUMMARY_PATH.write_text(json.dumps(s, ensure_ascii=False, indent=1), encoding="utf-8")
        log(f"[out] {SUMMARY_PATH}")
        log_path.write_text("\n".join(_LOG), encoding="utf-8")
        return 0

    if not SUMMARY_PATH.is_file():
        log(f"[FAIL] 摘要资产缺失，请先 --mode build")
        return 3
    summaries = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    log(f"[summary] 载入 {len(summaries)} 篇摘要")

    top = int(getattr(settings, "plot_max_chunks", 3) or 3)
    lex_fb = int(getattr(settings, "plot_lexical_fallback", 2) or 0)
    inject_chars = int(getattr(settings, "plot_context_max_chars", 1000) or 0)
    items = E.load_testset(Path(args.testset))
    if args.types:
        want = {t.strip() for t in str(args.types).split(",") if t.strip()}
        items = [it for it in items if str((it.get("dims") or {}).get("type")) in want]
    if args.limit:
        items = items[: args.limit]
    oracle = E.build_oracle(retr.corpus, items)
    log(f"[load] 题量 {len(items)}｜mode={args.mode}")

    def summary_for(item: dict) -> str | None:
        if args.force_key:
            return (summaries.get(args.force_key) or {}).get("text")
        ch = str((item.get("dims") or {}).get("chapter") or "")
        ver = CHAPTER_VER.get(ch)
        s = summaries.get(ver) if ver else None
        return (s or {}).get("text")

    def run(label: str, enable: bool) -> dict[str, Any]:
        t0 = time.time()
        n_pass = 0
        n_pass_real = 0
        n_inj = 0
        for it in items:
            qid = str(it.get("id"))
            item2 = dict(it)
            summ = summary_for(it)
            if enable and summ:
                if args.mode == "query":
                    names = (summaries.get(CHAPTER_VER.get(
                        str((it.get("dims") or {}).get("chapter") or ""), "")) or {}).get("top") or []
                    item2["q"] = f"{it.get('q')} {' '.join(names[:args.query_top])}"
            transform = None
            if enable and args.mode == "append" and summ:
                def transform(_q, chunks, _summ=summ):
                    # synthetic=True 是**评测口径的硬约定**：合成块不计入
                    # strict_pass_retrieved（抗灌水口径），否则追加名表就能刷分。
                    meta = {"path": "chapter_summary", "chapter_summary": True,
                            "synthetic": True}
                    return list(chunks) + [RetrievedChunk(
                        text=_summ, score=FUSE_MIN_SCORE + 0.05, metadata=meta)]
            row = E.evaluate_case(retr, item2, oracle[qid], top, lex_fb, inject_chars,
                                  chunks_transform=transform)
            n_pass += int(bool(row.get("strict_pass")))
            n_pass_real += int(bool(row.get("strict_pass_retrieved")))
            n_inj += int(bool(row.get("inject_pass")))
        neg = E.evaluate_negatives(retr, top, lex_fb)
        r = {"label": label, "enable": enable,
             "strict_pass_n": n_pass, "strict_pass": D.rate(n_pass, len(items)),
             # 抗灌水口径：合成块不计入 → 灌水方案在这里会掉回基线水平
             "strict_pass_retrieved_n": n_pass_real,
             "strict_pass_retrieved": D.rate(n_pass_real, len(items)),
             "inject_pass_n": n_inj, "inject_pass": D.rate(n_inj, len(items)),
             "negatives": {"cases": neg.get("cases"),
                           "cases_with_injection": len(neg.get("violations") or []),
                           "injection_total": neg.get("negative_injection_total"),
                           "new_leaks": neg.get("new_leaks")},
             "elapsed_s": round(time.time() - t0, 1)}
        log(f"  [{label}] strict {n_pass}/{len(items)}"
            f"｜retrieved {n_pass_real}（抗灌水口径）｜inject {n_inj}"
            f"｜负样本失守 {r['negatives']['cases_with_injection']}/{r['negatives']['cases']} 条"
            f"（注入 {r['negatives']['injection_total']} 块）｜{r['elapsed_s']}s")
        return r

    results = [run("基线", False), run(f"{args.mode} 摘要", True)]
    report = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "config": {"mode": args.mode, "cases": len(items), "testset": Path(args.testset).name,
                   "query_top": args.query_top},
        "results": results,
        "delta": {"d_strict": results[1]["strict_pass_n"] - results[0]["strict_pass_n"],
                  "d_inject": results[1]["inject_pass_n"] - results[0]["inject_pass_n"],
                  "d_neg_cases": (results[1]["negatives"]["cases_with_injection"]
                                  - results[0]["negatives"]["cases_with_injection"])},
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"\n==== 摘要 ====　Δstrict={report['delta']['d_strict']:+d} 题"
        f"　Δinject={report['delta']['d_inject']:+d} 题"
        f"　Δ负样本失守={report['delta']['d_neg_cases']:+d} 条")
    log(f"[out] {out_path}")
    log_path.write_text("\n".join(_LOG), encoding="utf-8")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except BaseException as exc:  # noqa: BLE001
        import traceback
        try:
            (AUDIT / "ab_t5t8_crash.txt").write_text(
                f"{time.strftime('%Y-%m-%d %H:%M:%S')}\n{traceback.format_exc()}",
                encoding="utf-8")
        except Exception:
            pass
        print(f"[CRASH] {exc!r}", flush=True)
        raise
