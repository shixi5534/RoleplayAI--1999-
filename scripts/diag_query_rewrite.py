# -*- coding: utf-8 -*-
"""「多问法改写」离线方向验证（只读，不改检索代码）。

要回答的问题
------------
失败题集中在 multi-hop（新题集 45%、300 题 50%），且 60 题的正解块从未进入任何
通道候选池。用户提出：检索时先用模型把问题改写成 N 种不同问法，再多路召回。

在往生产检索路径里加 LLM 调用之前，必须先用数据回答三件事（每件事都可能让方案落空）：
  Q1. 改写**能不能**把正解块捞进语义候选池？（recall@K 提升多少题）
  Q2. 提升集中在哪类题？（multi-hop 受益还是 factoid 受益）
  Q3. 代价多大？（LLM 延迟、缓存命中率）

方法（与生产同口径）：
  - gold 块 = oracle full（单块覆盖全部证据组），为空时回退 any；
  - 语义检索直接用 ``semantic.search(embed(q), top_k)``，**不经过种子门控**
    （门控是已知的结构性短路，先量"改写本身有没有信息量"）；
  - 批量嵌入：实测 4 条 466ms vs 串行 1345ms，改写必须走批量。

产物：JSON + 同名 .log；改写结果落盘可复用（避免重复烧 token）。
退出码：0 正常｜1 环境缺失｜2 语义降级｜3 题集缺失
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.request
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

DEFAULT_OUT = ROOT / "data" / "knowledge" / "_audit" / "diag_query_rewrite.json"
DEFAULT_TESTSET = ROOT / "data" / "knowledge" / "_audit" / "rag_testset_200_new.json"

REWRITE_PROMPT = (
    "你是《重返未来：1999》的剧情检索助手。用户的问题要拿去检索游戏剧情原文。\n"
    "请把下面的问题改写成 {n} 种不同的问法，要求：\n"
    "1) 每种问法保留原问题的核心意图，不得改变所问对象；\n"
    "2) 换成不同措辞，并尽量补出可能涉及的角色名、地点名、事件名（中英文都可以）；\n"
    "3) 每行一条，不要编号、不要解释、不要多余标点。\n"
    "原问题：{q}\n"
    "改写："
)

_LOG: list[str] = []


def log(msg: str) -> None:
    print(msg, flush=True)
    _LOG.append(str(msg))


class Rewriter:
    """同步 OpenAI 兼容 /chat/completions 调用（与 LLMEntityIdentifier 同模式）。

    为什么不用 LLMPort：``LLMPort.generate`` 是 async，而检索路径是同步的，
    在同步上下文里跑协程会踩事件循环嵌套。检索侧已有先例（plot_entity_expand）
    用 urllib 直连，这里保持一致。
    """

    def __init__(self, base_url: str, api_key: str, model: str,
                 timeout: float = 8.0, variants: int = 3) -> None:
        self.base_url = str(base_url).rstrip("/")
        self.api_key = str(api_key or "")
        self.model = str(model)
        self.timeout = float(timeout)
        self.variants = max(1, int(variants))
        self.stats = {"calls": 0, "ok": 0, "failed": 0, "total_ms": 0.0}

    def rewrite(self, q: str) -> list[str]:
        body = json.dumps({
            "model": self.model,
            "messages": [{"role": "user",
                          "content": REWRITE_PROMPT.format(n=self.variants, q=q)}],
            "temperature": 0.2,
            "max_tokens": 200,
        }).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions", data=body,
            headers={"Content-Type": "application/json",
                     "Authorization": f"Bearer {self.api_key}"})
        t0 = time.perf_counter()
        self.stats["calls"] += 1
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception as exc:  # noqa: BLE001 - 降级路径：改写失败就用原查询
            self.stats["failed"] += 1
            self.stats["total_ms"] += (time.perf_counter() - t0) * 1000
            log(f"  [warn] 改写失败，降级为原查询：{exc!r}")
            return []
        self.stats["total_ms"] += (time.perf_counter() - t0) * 1000
        raw = str(((data.get("choices") or [{}])[0].get("message") or {}).get("content") or "")
        out: list[str] = []
        for line in raw.splitlines():
            line = line.strip(" \t-•*0123456789.、)（")
            if len(line) >= 4 and line != q:
                out.append(line)
        self.stats["ok"] += 1
        return out[: self.variants]


def main() -> int:
    ap = argparse.ArgumentParser(description="多问法改写离线验证")
    ap.add_argument("--character", default="wu_ming_zhe")
    ap.add_argument("--testset", default=str(DEFAULT_TESTSET))
    ap.add_argument("--variants", type=int, default=3)
    ap.add_argument("--topk", type=int, default=20)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--types", default="", help="只测这些 type（逗号分隔，如 multi-hop）")
    ap.add_argument("--model", default="", help="覆盖改写模型（空=用 llm_model）")
    ap.add_argument("--base-url", default="",
                    help="覆盖 LLM base_url（空=用 llm_base_url；本地 ollama 用 http://127.0.0.1:11434/v1）")
    ap.add_argument("--api-key", default="", help="覆盖 API Key（空=用 llm_api_key；ollama 可填 ollama）")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--allow-degraded", action="store_true")
    args = ap.parse_args()

    out_path = Path(args.out)
    log_path = out_path.with_suffix(out_path.suffix + ".log")
    ts_path = Path(args.testset)
    if not ts_path.is_file():
        log(f"[FAIL] 题集不存在：{ts_path}")
        return 3
    items = E.load_testset(ts_path)
    if args.types:
        want = {t.strip() for t in str(args.types).split(",") if t.strip()}
        items = [it for it in items
                 if str((it.get("dims") or {}).get("type")) in want]
    if args.limit:
        items = items[: args.limit]
    if not items:
        log("[FAIL] 筛后无题")
        return 3
    log(f"[load] 题量 {len(items)}（{ts_path.name}）")

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

    base = args.base_url or str(getattr(settings, "llm_base_url", "") or "")
    key = args.api_key or str(getattr(settings, "llm_api_key", "") or "")
    model = args.model or str(getattr(settings, "llm_model", "") or "")
    if not (base and key and model):
        log(f"[FAIL] LLM 配置不完整（base={bool(base)}, key={bool(key)}, model={model!r}）")
        return 1
    rw = Rewriter(base, key, model, timeout=8.0, variants=args.variants)
    log(f"[llm] provider={getattr(settings, 'llm_provider', '')}｜model={model}")

    oracle = E.build_oracle(retr.corpus, items)
    cache_path = out_path.with_name(out_path.stem + "_rewrites.json")
    cache: dict[str, list[str]] = {}
    if cache_path.is_file():
        cache = json.loads(cache_path.read_text(encoding="utf-8"))
        log(f"[cache] 已有改写 {len(cache)} 条")

    per_case: list[dict] = []
    n_base_hit = 0
    n_rew_hit = 0
    by_type: dict[str, dict[str, int]] = {}
    t0 = time.time()
    for i, item in enumerate(items, start=1):
        qid = str(item.get("id"))
        q = str(item.get("q") or "")
        ent = oracle.get(qid) or {}
        full = set(ent.get("full") or set())
        gold = full if full else set(ent.get("any") or set())
        if not gold:
            continue
        ttype = str((item.get("dims") or {}).get("type") or "")
        by_type.setdefault(ttype, {"n": 0, "base": 0, "rew": 0})
        by_type[ttype]["n"] += 1

        variants = cache.get(q)
        if variants is None:
            variants = rw.rewrite(q)
            cache[q] = variants
        texts = [q] + list(variants)
        vecs = sem.embedder.embed(texts)  # 批量：实测远快于串行
        base_top = {h for h, _s in sem.search(np.asarray(vecs[0], dtype=np.float32),
                                              args.topk)}
        union = set(base_top)
        for v in vecs[1:]:
            union |= {h for h, _s in sem.search(np.asarray(v, dtype=np.float32), args.topk)}
        hit_base = bool(base_top & gold)
        hit_rew = bool(union & gold)
        n_base_hit += int(hit_base)
        n_rew_hit += int(hit_rew)
        by_type[ttype]["base"] += int(hit_base)
        by_type[ttype]["rew"] += int(hit_rew)
        per_case.append({
            "id": qid, "q": q, "type": ttype,
            "variants": list(variants),
            "base_hit": hit_base, "rew_hit": hit_rew,
            "gain": int(hit_rew) - int(hit_base),
        })
        if i % 10 == 0:
            log(f"  [progress] {i}/{len(items)}｜已用 {time.time() - t0:.0f}s")

    cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")

    n = max(1, len(per_case))
    st = rw.stats
    report = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "config": {"model": model, "variants": args.variants, "topk": args.topk,
                   "testset": ts_path.name, "cases": len(per_case)},
        "llm": {"calls": st["calls"], "ok": st["ok"], "failed": st["failed"],
                "avg_ms": round(st["total_ms"] / max(1, st["calls"]), 1)},
        "recall_at_k": {
            "base": {"n": n_base_hit, "rate": D.rate(n_base_hit, n)},
            "with_rewrite": {"n": n_rew_hit, "rate": D.rate(n_rew_hit, n)},
            "delta": n_rew_hit - n_base_hit,
        },
        "by_type": {k: {"n": v["n"], "base": v["base"], "rew": v["rew"],
                        "d_base": D.rate(v["base"], v["n"]),
                        "d_rew": D.rate(v["rew"], v["n"]),
                        "delta": v["rew"] - v["base"]}
                    for k, v in by_type.items()},
        "per_case": per_case,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    log("\n==== 摘要 ====")
    log(f"题量 {n}｜语义 top-{args.topk} 命中 gold：")
    log(f"  原查询      {n_base_hit}（{D.rate(n_base_hit, n)}）")
    log(f"  加改写后    {n_rew_hit}（{D.rate(n_rew_hit, n)}）｜Δ={n_rew_hit - n_base_hit:+d} 题")
    log(f"LLM：调用 {st['calls']}｜成功 {st['ok']}｜失败 {st['failed']}"
        f"｜平均 {report['llm']['avg_ms']}ms")
    for k, v in report["by_type"].items():
        log(f"  [{k}] n={v['n']} base={v['d_base']} → rew={v['d_rew']}（Δ{v['delta']:+d}）")
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
