# -*- coding: utf-8 -*-
"""提及通道截断消融（只改运行期实例属性，不改配置、不改检索代码）。

为什么盯上这个开关
-------------------
``diag_gold_rank.py`` 实测（60 道 never_candidate 题）：
  - 正解块 **100% 在语义索引里**（只是排名靠后，p50 = 54）；
  - **60/60 的正解块文本都含真阳实体名**。

第二点是决定性的：mention 通道的取块规则就是「块文本包含目标实体名」，
既然 gold 块 100% 含真阳名，那它**本该被 mention 通道取到**却没取到——
嫌疑落在候选池截断上：生产 ``plot_mention_per_entity=5``、``plot_mention_total_cap=10``，
即每个目标实体最多取 5 块、总量封顶 10 块。一个主角实体在 9021 块里出现几百次，
只取前 5 块，gold 块几乎不可能入选（``_mention_channel`` 的 docstring 自己就记过
「多跳题的第 4+ 候选块永远进不来」这类丢失）。

本脚本的量法（只在这 60 题上做，快且直接）：
  1. 逐档改 ``retr.mention_per_entity`` / ``retr.mention_total_cap``（运行期实例属性）；
  2. 用主评测口径 ``eval_plot_rag.evaluate_case`` 判 strict / inject；
  3. 同时 spy 住 ``_fuse_channels``，记录 mention / edge 通道候选池是否含 gold 块；
  4. **负样本必跑**：53 条负样本的失守条数与注入块数，护栏只认这个。

用法（项目根目录）
------------------
    .venv/Scripts/python.exe -X utf8 scripts/ab_mention_depth.py
    .venv/Scripts/python.exe -X utf8 scripts/ab_mention_depth.py --per-entity 5,20 --total-cap 10,50
    .venv/Scripts/python.exe -X utf8 scripts/ab_mention_depth.py --limit 10   # 冒烟

输入：``data/knowledge/_audit/diag_block_provenance_20260917.json``（never_candidate 清单）
产物：``data/knowledge/_audit/ab_mention_depth.json`` + 同名 ``.log``
退出码：0 正常｜1 环境缺失｜2 语义降级｜3 输入清单缺失
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from roleplay.config import get_settings  # noqa: E402
from roleplay.core.knowledge.factory import build_plot_registry  # noqa: E402

import diag_seedless_ceiling as D  # noqa: E402
import eval_plot_rag as E  # noqa: E402

DEFAULT_OUT = ROOT / "data" / "knowledge" / "_audit" / "ab_mention_depth.json"
DEFAULT_FROM = ROOT / "data" / "knowledge" / "_audit" / "diag_block_provenance_20260917.json"

_LOG: list[str] = []


def log(msg: str) -> None:
    print(msg, flush=True)
    _LOG.append(str(msg))


def main() -> int:
    ap = argparse.ArgumentParser(description="提及通道截断消融（运行期属性，不改配置）")
    ap.add_argument("--character", default="wu_ming_zhe")
    ap.add_argument("--from", dest="from_path", default=str(DEFAULT_FROM))
    ap.add_argument("--per-entity", default="5,20", help="每实体取块数档位")
    ap.add_argument("--total-cap", default="10,50", help="提及通道总量上限档位")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--allow-degraded", action="store_true")
    args = ap.parse_args()

    out_path = Path(args.out)
    log_path = out_path.with_suffix(out_path.suffix + ".log")
    per_list = [int(x) for x in str(args.per_entity).split(",") if str(x).strip()]
    cap_list = [int(x) for x in str(args.total_cap).split(",") if str(x).strip()]
    if len(per_list) != len(cap_list):
        log("[FAIL] --per-entity 与 --total-cap 档位数必须一致")
        return 1

    src = Path(args.from_path)
    if not src.is_file():
        log(f"[FAIL] 缺少输入清单 {src}")
        return 3
    prev = json.loads(src.read_text(encoding="utf-8"))
    cases = [c for c in (prev.get("per_case") or []) if c.get("kind") == "never_candidate"]
    if args.limit:
        cases = cases[: args.limit]
    log(f"[from] never_candidate 题 {len(cases)}")

    settings = get_settings()
    registry = build_plot_registry(settings)
    retr = registry.get(args.character)
    if retr is None:
        log("[FAIL] 剧情图谱未加载")
        return 1
    if getattr(retr, "semantic", None) is None and not args.allow_degraded:
        log("[FAIL] 语义通道已降级（--allow-degraded 可强行继续）")
        return 2

    top = int(getattr(settings, "plot_max_chunks", 3) or 3)
    lex_fb = int(getattr(settings, "plot_lexical_fallback", 2) or 0)
    inject_chars = int(getattr(settings, "plot_context_max_chars", 1000) or 0)
    items = E.load_testset(None)
    by_id = {str(it.get("id")): it for it in items}
    todo = [by_id[str(c["id"])] for c in cases if str(c["id"]) in by_id]
    oracle = E.build_oracle(retr.corpus, todo)
    log(f"[load] 待救题 {len(todo)}｜top={top}｜lexical_fallback={lex_fb}｜inject_chars={inject_chars}")

    # spy：捕获融合前各通道候选池（判定 gold 是否入池）
    cap: dict[str, Any] = {"channels": []}
    orig_fuse = retr._fuse_channels

    def spy(channels, *, limit):
        cap["channels"] = [
            (str(path), [str(getattr(c, "hash", "") or "") for _s, c, _m in ch_items])
            for path, _w, ch_items in channels
        ]
        return orig_fuse(channels, limit=limit)

    retr._fuse_channels = spy
    prod_per = int(getattr(retr, "mention_per_entity", 5))
    prod_cap = int(getattr(retr, "mention_total_cap", 10))
    log(f"[cfg] 生产 mention_per_entity={prod_per}｜mention_total_cap={prod_cap}")

    results: list[dict[str, Any]] = []
    for per, capv in zip(per_list, cap_list):
        retr.mention_per_entity, retr.mention_total_cap = per, capv
        t0 = time.time()
        n_pass = 0
        n_inject = 0
        n_gold_in_mention = 0
        n_gold_in_any = 0
        pool_sizes: list[int] = []
        for item in todo:
            qid = str(item.get("id"))
            ent = oracle.get(qid) or {}
            full = set(ent.get("full") or set())
            gold = full if full else set(ent.get("any") or set())
            cap["channels"] = []
            row = E.evaluate_case(retr, item, ent, top, lex_fb, inject_chars)
            n_pass += int(bool(row.get("strict_pass")))
            n_inject += int(bool(row.get("inject_pass")))
            hit_mention = False
            hit_any = False
            for path, hashes in cap["channels"]:
                if path == "mention":
                    pool_sizes.append(len(hashes))
                if any(h in gold for h in hashes):
                    hit_any = True
                    if path == "mention":
                        hit_mention = True
            n_gold_in_mention += int(hit_mention)
            n_gold_in_any += int(hit_any)
        neg = E.evaluate_negatives(retr, top, lex_fb)
        r = {
            "mention_per_entity": per, "mention_total_cap": capv,
            "rescued": len(todo),
            "strict_pass_n": n_pass, "strict_pass": D.rate(n_pass, len(todo)),
            "inject_pass_n": n_inject, "inject_pass": D.rate(n_inject, len(todo)),
            "gold_in_mention_pool": n_gold_in_mention,
            "gold_in_any_pool": n_gold_in_any,
            "mention_pool_avg": round(sum(pool_sizes) / max(1, len(pool_sizes)), 1),
            "negatives": {
                "cases": neg.get("cases"),
                "cases_with_injection": len(neg.get("violations") or []),
                "injection_total": neg.get("negative_injection_total"),
                "new_leaks": neg.get("new_leaks"),
            },
            "elapsed_s": round(time.time() - t0, 1),
        }
        results.append(r)
        log(f"  [per={per},cap={capv}] 救回 strict {n_pass}/{len(todo)}｜inject {n_inject}"
            f"｜gold 入 mention 池 {n_gold_in_mention}｜入任一池 {n_gold_in_any}"
            f"｜池均 {r['mention_pool_avg']} 块"
            f"｜负样本失守 {r['negatives']['cases_with_injection']}/{r['negatives']['cases']} 条"
            f"（新增泄漏 {len(r['negatives']['new_leaks'] or [])}）｜{r['elapsed_s']}s")

    retr._fuse_channels = orig_fuse
    retr.mention_per_entity, retr.mention_total_cap = prod_per, prod_cap

    report = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "config": {"top": top, "lexical_fallback": lex_fb, "inject_chars": inject_chars,
                   "prod_per_entity": prod_per, "prod_total_cap": prod_cap},
        "results": results,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
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
            Path(str(DEFAULT_OUT) + ".crash").write_text(
                f"{time.strftime('%Y-%m-%d %H:%M:%S')}\n{traceback.format_exc()}",
                encoding="utf-8")
        except Exception:
            pass
        print(f"[CRASH] {exc!r}", flush=True)
        raise
