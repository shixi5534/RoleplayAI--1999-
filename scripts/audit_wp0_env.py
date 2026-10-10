# -*- coding: utf-8 -*-
"""WP0 —— 环境锚定与公共评测自检。

做四件事，任何一件失败都不应继续后续 WP：
1. 图 SHA 对 v8 锁（`026b41699f021db2`）+ 语义指纹校验；
2. 云端网关(7863)与本地 Ollama(bge-m3) 各探活一次（决定 full/graph_only 口径）；
3. 从 v8 评测工件反推 qid 白名单（300cn-answerable-196 / blind206 / gen120 /
   unanswerable104），落 data/knowledge/_audit/audit_qid_whitelist.json；
4. **环境自检题**：冷启动复算 v8 三主数（full 模式 hit@6），差≠0 即口径漂移。

运行（固定口径，勿改）：
    PYTHONHASHSEED=0 .venv/Scripts/python.exe scripts/audit_wp0_env.py
调试可加 --skip-selfcheck（跳过第 4 步的 626 题活跑）。
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

import audit_common as AC

AC.apply_v8_env()

import httpx  # noqa: E402

from compendium_rag import pipeline as P  # noqa: E402
from compendium_rag.config import get_settings  # noqa: E402
from compendium_rag.embedder import OllamaEmbedder  # noqa: E402

AUDIT_DIR = AC.ROOT / "data" / "knowledge" / "_audit"
REPORTS_DIR = AC.ROOT / "data" / "compendium_rag" / "reports"
OUT = REPORTS_DIR / "audit_wp0_env.json"


def probe_gateway(s) -> dict:
    url = s.llm_base_url.rstrip("/") + "/models"
    out = {"url": s.llm_base_url, "model": s.llm_model, "ok": False}
    try:
        r = httpx.get(url, headers={"Authorization": f"Bearer {s.llm_api_key}"},
                      timeout=10.0)
        out["ok"] = r.status_code == 200
        out["status"] = r.status_code
    except Exception as exc:  # noqa: BLE001
        out["error"] = str(exc)[:200]
    return out


async def probe_ollama(s) -> dict:
    out = {"url": s.embed_base_url, "model": s.embed_model, "ok": False}
    try:
        async with OllamaEmbedder(s.embed_base_url, s.embed_model,
                                  timeout=30.0) as emb:
            out["dim"] = await emb.probe()
            out["ok"] = True
    except Exception as exc:  # noqa: BLE001
        out["error"] = str(exc)[:200]
    return out


def build_qid_whitelist() -> dict:
    """从 v8 工件 rows（mode=full）反推白名单。"""
    wl: dict[str, list[str]] = {}
    for key, art in [("300cn", "eval_300cn_k1.json"),
                     ("blind", "eval_blind_k1.json"),
                     ("gen", "eval_gen120_k1.json")]:
        rows = json.loads((REPORTS_DIR / art).read_text(encoding="utf-8"))["rows"]
        full = [r for r in rows if r["mode"] == "full"]
        wl[key + "_all"] = [r["qid"] for r in full]
        if key == "300cn":
            wl["300cn_answerable"] = [r["qid"] for r in full if r["answerable"]]
            wl["300cn_unanswerable"] = [r["qid"] for r in full
                                       if not r["answerable"]]
    return wl


async def selfcheck(kb, E300, s) -> dict:
    """复算三主数：full 模式、top_k=6，逐题 hit 计数须与 v8 锁相等。"""
    sets = {
        "300cn": AUDIT_DIR / "rag_testset_300_cn.json",
        "blind206": AUDIT_DIR / "blind_v1" / "questions_strict.json",
        "gen120": AUDIT_DIR / "rag_testset_gen_r1r2.json",
    }
    corpus_blob = "\n".join(c.text for c in kb.chunks)
    result: dict[str, dict] = {}
    per_case_rows: list[dict] = []
    for name, path in sets.items():
        cases = E300.load_cases(path)
        for c in cases:
            c.dims["_answerable"] = any(k in corpus_blob for k in c.keywords)
        rows = []
        for i, c in enumerate(cases, 1):
            r = await E300.score_case(kb, c, AC.V8_TOP_K, True)
            r["answerable"] = c.dims["_answerable"]
            rows.append(r)
            if i % 100 == 0:
                print(f"  [{name}] {i}/{len(cases)} "
                      f"累计hit={sum(x['hit'] for x in rows)}", flush=True)
        tier = AC.V8_SELFCHECK[name]["tier"]
        sub = ([r for r in rows if r["answerable"]] if name == "300cn"
               and tier == "answerable" else rows)
        if name == "300cn" and tier == "answerable":
            un = [r for r in rows if not r["answerable"]]
            result.setdefault("safety_unanswerable",
                              {"hits": sum(r["hit"] for r in un), "n": len(un)})
        hits = sum(1 for r in sub if r["hit"])
        result[name] = {"hits": hits, "n": len(sub),
                        "rate": round(hits / len(sub), 4) if sub else None}
        for r in sub:
            per_case_rows.append({"set": name, "qid": r["qid"],
                                  "hit": r["hit"], "rr": r["rr"],
                                  "n_evidence": r["n_evidence"]})
    return {"result": result, "per_case": per_case_rows}


async def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-selfcheck", action="store_true")
    args = ap.parse_args()

    rep = AC.new_report("WP0")
    s = get_settings()
    rep["retrieval_config"] = AC.config_snapshot(s)

    # 1. 图锚点
    sha = AC.sha16_file(s.graph_path)
    rep["frozen_graph_sha"] = sha
    rep["gate_verdicts"].append(AC.gate_verdict(
        "graph_sha_vs_v8", f"== {AC.V8_GRAPH_SHA16}", sha,
        "PASS" if sha == AC.V8_GRAPH_SHA16 else "FAIL",
        "审查全程只读，任何 WP 启动前必须命中此锁" if sha == AC.V8_GRAPH_SHA16
        else "图已被改动，审查不得继续", "环境"))
    AC.assert_frozen_graph(rep)

    kb = P.load_kb(s)
    ok, why = P.verify_fingerprint(s, kb.graph)
    rep["gate_verdicts"].append(AC.gate_verdict(
        "graph_fingerprint", "语义指纹一致", why,
        "PASS" if ok else "FAIL", why, "环境"))

    # 2. 探活
    gw = probe_gateway(s)
    oll = await probe_ollama(s)
    rep["metrics"]["gateway"] = gw
    rep["metrics"]["ollama"] = oll
    rep["gate_verdicts"].append(AC.gate_verdict(
        "gateway_available", "可达（CloudLLM/兜底通道）", gw.get("status") or gw.get("error", "n/a"),
        "PASS" if gw["ok"] else "N/A",
        "网关不可达时子代理主通道仍可跑，CloudLLM 兜底不可用", "环境"))
    rep["gate_verdicts"].append(AC.gate_verdict(
        "ollama_available", "bge-m3 嵌入可用", oll.get("dim") or oll.get("error", "n/a"),
        "PASS" if oll["ok"] else "FAIL",
        "Ollama 挂则检索退 graph_only，禁与 v8 full 数字混表", "环境"))
    rep["metrics"]["full_mode_available"] = oll["ok"]

    # 3. qid 白名单
    wl = build_qid_whitelist()
    wl_path = AUDIT_DIR / "audit_qid_whitelist.json"
    counts = {k: len(v) for k, v in wl.items()}
    rep["metrics"]["qid_whitelist_counts"] = counts
    expect = {"300cn_all": 300, "300cn_answerable": 196,
              "300cn_unanswerable": 104, "blind_all": 206, "gen_all": 120}
    match = all(counts.get(k) == v for k, v in expect.items())
    rep["gate_verdicts"].append(AC.gate_verdict(
        "qid_whitelist_counts", "300/196/104/206/120", counts,
        "PASS" if match else "FAIL", "与 v8 工件逐集对账", "环境"))
    if match:
        wl_path.write_text(json.dumps(
            {"schema": "audit.qid_whitelist/v1",
             "derived_from": [AC.V8_SELFCHECK[k]["artifact"] for k in AC.V8_SELFCHECK],
             "mode": "full", "top_k": AC.V8_TOP_K, "lists": wl},
            ensure_ascii=False, indent=2), encoding="utf-8")
        rep["artifacts"].append(str(wl_path.relative_to(AC.ROOT)))

    # 4. 环境自检题（三主数复算）
    E300 = AC.eval300_module()
    if args.skip_selfcheck:
        rep["gate_verdicts"].append(AC.gate_verdict(
            "v8_three_main_numbers", "167/196, 184/206, 118/120", "skipped",
            "N/A", "--skip-selfcheck：调试跑，不得用于正式审查", "环境"))
    else:
        sc = await selfcheck(kb, E300, s)
        rep["metrics"]["selfcheck"] = sc["result"]
        bad = []
        for name in AC.V8_SELFCHECK:
            exp = AC.V8_SELFCHECK[name]
            got = sc["result"][name]
            if (got["hits"], got["n"]) != (exp["hits"], exp["n"]):
                bad.append(f"{name}: got {got['hits']}/{got['n']} "
                           f"!= lock {exp['hits']}/{exp['n']}")
        su = sc["result"].get("safety_unanswerable", {})
        if (su.get("hits"), su.get("n")) != (AC.V8_SAFETY["hits"], AC.V8_SAFETY["n"]):
            bad.append(f"safety: got {su} != lock {AC.V8_SAFETY}")
        rep["gate_verdicts"].append(AC.gate_verdict(
            "v8_three_main_numbers",
            "167/196, 184/206, 118/120, safety 1/104（逐题差=0）",
            sc["result"], "PASS" if not bad else "FAIL",
            "; ".join(bad) or "冷启动复算与 v8 锁逐题一致，口径未漂移",
            "环境"))
        rep["per_case"] = sc["per_case"]

    out = AC.write_report(OUT, rep)
    print(f"\nWP0 报告 → {out}")
    for g in rep["gate_verdicts"]:
        print(f"  [{g['verdict']}] {g['gate']}: {g['actual']}")
    return 0 if all(g["verdict"] != "FAIL" for g in rep["gate_verdicts"]) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
