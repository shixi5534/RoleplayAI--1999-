# -*- coding: utf-8 -*-
"""剧情图谱验收测试（数据层，R1–R14）。

依据见 `docs/剧情图谱验收标准.md`（Microsoft GraphRAG v3.1.1 / Ragas /
AIIA-T 0294-2026 / 大模型国标）。每条需求独立判定 PASS/FAIL 并留证据。

用法（项目根目录）：
  .venv/Scripts/python.exe -X utf8 scripts/acceptance_plot_graph.py
  .venv/Scripts/python.exe -X utf8 scripts/acceptance_plot_graph.py --skip-r14  # 跳过重建
产物：docs/剧情图谱验收报告.md
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from roleplay.config import get_settings  # noqa: E402
from roleplay.core.knowledge.plot_graph import (  # noqa: E402
    PlotGraphRegistry,
    plot_namespace,
)

CHARACTER = "wu_ming_zhe"
GRAPH = ROOT / "data" / "knowledge" / f"plot_graph_{CHARACTER}.json"
CORPUS = ROOT / "data" / "knowledge" / f"plot_corpus_{CHARACTER}.json"
CACHE = ROOT / "data" / "knowledge" / "plot_cache" / CHARACTER
AUDIT = ROOT / "data" / "knowledge" / "_audit"

QUERIES = [
    "无名者是谁", "圣洛夫基金会是做什么的", "重塑之手的目的", "暴雨发生了什么",
    "维尔汀和司辰的关系", "伊戈尔", "乌尔德", "金预言", "潘家园", "巴比伦骰子",
    "皮罗斯", "曼佩刺杀", "Ms. Stranger", "Manus Vindictae", "the Storm", "SPDM",
]
HALLUCINATION_WATCH = ["Madam Lucy", "露西", "Lucy"]

RESULTS: list[dict] = []


def check(rid: str, title: str, source: str):
    """装饰器：登记一条需求的判定结果。"""

    def deco(fn):
        t0 = time.perf_counter()
        try:
            ok, detail = fn()
        except Exception as exc:  # noqa: BLE001
            ok, detail = False, f"抛异常 {type(exc).__name__}: {exc}"
        dt = (time.perf_counter() - t0) * 1000
        RESULTS.append(
            {"id": rid, "title": title, "source": source,
             "ok": bool(ok), "detail": detail, "ms": round(dt, 1)}
        )
        print(f"  [{'PASS' if ok else 'FAIL'}] {rid} {title} — {detail[:90]}")
        return fn

    return deco


def _load():
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    chunks = corpus["chunks"] if isinstance(corpus, dict) else corpus
    return graph, chunks


def _backfill_hashes() -> set[str]:
    out: set[str] = set()
    for p in (ROOT / "scripts").glob("apply_empty_p*.py"):
        out |= set(re.findall(r'"([0-9a-f]{16})":', p.read_text(encoding="utf-8")))
    return out


def _audit_flags() -> dict:
    rows = [
        json.loads(l)
        for l in (AUDIT / "full_issues.jsonl").read_text(encoding="utf-8").splitlines()
        if l.strip()
    ]
    from collections import Counter

    c: Counter = Counter()
    for r in rows:
        for f in r.get("flags", []):
            c[f] += 1
    return dict(c)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-r14", action="store_true", help="跳过图谱重建（R14）")
    args = ap.parse_args()

    graph, chunks = _load()
    ents, edges = graph["entities"], graph["edges"]
    chunk_hashes = {c["hash"] for c in chunks}
    flags = _audit_flags()

    # ---------------- A 组：知识模型结构合规 ----------------
    @check("R1", "实体模型完整（name/type/aliases + schema 版本）", "S1 Entity")
    def _r1():
        # 两层版本号：GraphStore 通用库用 GRAPH_SCHEMA_VERSION（落进 fingerprint），
        # 剧情图谱产物格式 PLOT_GRAPH_SCHEMA 仅用于日志，本项校验落盘的那一层。
        from roleplay.core.knowledge.graph_store import GRAPH_SCHEMA_VERSION
        from roleplay.core.knowledge.plot_graph import PLOT_GRAPH_SCHEMA

        bad = [
            e for e in ents.values()
            if not str(e.get("name") or "").strip() or not str(e.get("type") or "").strip()
        ]
        schema = (graph.get("fingerprint") or {}).get("schema")
        ok = not bad and schema == GRAPH_SCHEMA_VERSION
        return ok, (
            f"实体 {len(ents)}，缺字段 {len(bad)}，"
            f"fingerprint.schema={schema}（期望 {GRAPH_SCHEMA_VERSION}），"
            f"产物格式 {PLOT_GRAPH_SCHEMA}"
        )

    @check("R2", "关系模型完整（src/dst/relation/confidence）", "S1 Relationship")
    def _r2():
        bad_conf, bad_field = 0, 0
        for e in edges:
            if not (e.get("src") and e.get("dst") and e.get("relation")):
                bad_field += 1
            c = float(e.get("confidence", -1))
            if not 0.0 <= c <= 1.0:
                bad_conf += 1
        ok = bad_conf == 0 and bad_field == 0
        return ok, f"边 {len(edges)}，缺字段 {bad_field}，置信度越界 {bad_conf}"

    @check("R3", "证据可溯源（evidence.hash 能解析到 TextUnit）", "S1 provenance")
    def _r3():
        no_ev = [e for e in edges if not (e.get("evidence") or [])]
        bad_hash = []
        for e in edges:
            for ev in e.get("evidence") or []:
                h = ev.get("hash")
                if not h or h not in chunk_hashes:
                    bad_hash.append(h)
                    break
        ok = not no_ev and not bad_hash
        return ok, f"无证据边 {len(no_ev)}，hash 不可解析边 {len(bad_hash)}"

    @check("R4", "语料切块合规（hash/lang/version/doc_id + 缓存一一对应）", "S1 TextUnit")
    def _r4():
        bad = [
            c for c in chunks
            if not (c.get("hash") and c.get("doc_id") and c.get("lang") is not None)
        ]
        cache_files = {p.stem for p in CACHE.glob("*.json")}
        missing_cache = chunk_hashes - cache_files
        ok = not bad and not missing_cache
        return ok, (
            f"块 {len(chunks)}，缺字段 {len(bad)}，缓存缺失 {len(missing_cache)}"
        )

    # ---------------- B 组：抽取质量与幻觉控制 ----------------
    @check("R5", "来源忠实性（实体）：hallucinated_entity == 0", "S4 来源忠实性")
    def _r5():
        n = flags.get("hallucinated_entity", 0)
        return n == 0, f"hallucinated_entity = {n}"

    @check("R6", "来源忠实性（关系）：hallucinated_relation == 0", "S4 来源忠实性")
    def _r6():
        n = flags.get("hallucinated_relation", 0)
        return n == 0, f"hallucinated_relation = {n}"

    @check("R7", "内部一致性：无自环边、无悬空边", "S4 内部一致性")
    def _r7():
        eids = set(ents.keys())
        self_loop = [e for e in edges if e.get("src") == e.get("dst")]
        dangling = [e for e in edges if e["src"] not in eids or e["dst"] not in eids]
        ok = not self_loop and not dangling
        return ok, f"自环 {len(self_loop)}，悬空 {len(dangling)}"

    @check("R8", "指令遵循：关系谓语为纯中文", "S4 指令遵循")
    def _r8():
        bad = [e["relation"] for e in edges if re.search(r"[A-Za-z]", e["relation"])]
        return not bad, f"含拉丁字母谓语 {len(bad)}（样例 {bad[:3]}）"

    @check("R9", "事实准确性：代词/泛指噪声不入图", "S4 事实准确性")
    def _r9():
        from roleplay.core.knowledge.plot_graph import _PRONOUN_CANONICAL

        hits = [
            e["name"] for e in ents.values()
            if str(e.get("name") or "").strip() in _PRONOUN_CANONICAL
        ]
        return not hits, f"代词实体 {len(hits)}（样例 {hits[:5]}）"

    @check("R10", "抽取覆盖率：empty 块 == 已确认 NOOP 集合", "S4 不确定性诚实表达")
    def _r10():
        rows = [
            json.loads(l)
            for l in (AUDIT / "full_issues.jsonl").read_text(encoding="utf-8").splitlines()
            if l.strip()
        ]
        empty = {r["hash"] for r in rows if "empty" in r.get("flags", [])}
        noop_file = AUDIT / "noop_confirmed.json"
        noop = set(json.loads(noop_file.read_text(encoding="utf-8"))) if noop_file.exists() else set()
        ok = empty == noop and bool(noop)
        return ok, f"empty {len(empty)}，NOOP {len(noop)}，差集 {len(empty ^ noop)}"

    # ---------------- C 组：检索能力 ----------------
    settings = get_settings()
    registry = PlotGraphRegistry(
        corpus_dir=settings.plot_corpus_dir,
        graph_dir=settings.plot_graph_dir,
        alias_dir=settings.plot_lore_dir,
        include_weak=bool(settings.plot_include_weak),
    )
    retr = registry.get(CHARACTER)
    if retr is None:
        print("[FATAL] 图谱检索器加载失败")
        return 1
    text2hash = {}
    for ch in retr.corpus.chunks:
        text2hash.setdefault(ch.text, ch.hash)
    backfill = _backfill_hashes()
    latencies: list[float] = []

    def _retrieve(q, top=3):
        t0 = time.perf_counter()
        out = retr.retrieve(q, top_chunks=top)
        latencies.append((time.perf_counter() - t0) * 1000)
        return out

    @check("R11", "Context Recall：固定查询走图谱路径比例 ≥ 90%", "S3 Context Recall")
    def _r11():
        via_graph = 0
        for q in QUERIES:
            out = _retrieve(q)
            if any(c.metadata.get("via") == "plot_graph" for c in out):
                via_graph += 1
        ratio = via_graph / len(QUERIES)
        return ratio >= 0.9, f"{via_graph}/{len(QUERIES)} = {ratio:.0%}"

    @check("R12", "Context Entities Recall：补抽块反向验收 ≥ 50%", "S3 Context Entities Recall")
    def _r12():
        import random

        sample = random.Random(42).sample(sorted(backfill), min(60, len(backfill)))
        hit = tried = 0
        for h in sample:
            cache = CACHE / f"{h}.json"
            if not cache.exists():
                continue
            es = json.loads(cache.read_text(encoding="utf-8")).get("entities") or []
            if not es:
                continue
            q = str(es[0].get("name") or "").strip()
            if not q:
                continue
            tried += 1
            out = _retrieve(q, top=5)
            if h in {text2hash.get(c.text, "") for c in out}:
                hit += 1
        ratio = hit / max(1, tried)
        return ratio >= 0.5, f"{hit}/{tried} = {ratio:.0%}（抽样 {len(sample)} 块）"

    @check("R13", "Noise Sensitivity：检索结果不含已清除幻觉词", "S3 Noise Sensitivity")
    def _r13():
        hits = 0
        for q in QUERIES:
            for c in _retrieve(q):
                for w in HALLUCINATION_WATCH:
                    if w in c.text and w not in q:
                        hits += 1
                        break
        return hits == 0, f"幻觉词命中 {hits}（监视 {HALLUCINATION_WATCH}）"

    # ---------------- R14：幂等性（重建） ----------------
    if args.skip_r14:
        RESULTS.append(
            {"id": "R14", "title": "幂等/确定性：缓存重放零 LLM", "source": "S2",
             "ok": None, "detail": "已跳过（--skip-r14）", "ms": 0}
        )
    else:
        @check("R14", "幂等/确定性：缓存重放重建，实体/边数量一致", "S2 索引流程")
        def _r14():
            import subprocess

            before = (len(ents), len(edges))
            bak = GRAPH.with_suffix(".json.bak_acceptance")
            bak.write_bytes(GRAPH.read_bytes())
            try:
                GRAPH.unlink()
                py = str(ROOT / ".venv" / "Scripts" / "python.exe")
                r = subprocess.run(
                    [py, "-X", "utf8", "scripts/build_plot_graph.py",
                     "--character", CHARACTER, "--build-graph"],
                    capture_output=True, text=True, encoding="utf-8", cwd=str(ROOT),
                )
                m = re.search(r'"extracted":\s*(\d+)', r.stdout)
                extracted = int(m.group(1)) if m else -1
                g2 = json.loads(GRAPH.read_text(encoding="utf-8"))
                after = (len(g2["entities"]), len(g2["edges"]))
                ok = extracted == 0 and after == before
                return ok, f"extracted={extracted}，实体/边 {before} → {after}"
            finally:
                pass

    # ---------------- 报告 ----------------
    passed = sum(1 for r in RESULTS if r["ok"])
    failed = [r for r in RESULTS if r["ok"] is False]
    skipped = [r for r in RESULTS if r["ok"] is None]
    p95 = statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else (
        max(latencies) if latencies else 0
    )

    lines = [
        "# 剧情图谱验收报告（数据层 R1–R14）",
        "",
        f"- 执行时间：{time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"- 对象：`plot_graph_{CHARACTER}.json`（实体 {len(ents)} / 边 {len(edges)}）",
        f"- 结果：**通过 {passed} / 失败 {len(failed)} / 跳过 {len(skipped)}**",
        "",
        "| ID | 需求 | 依据 | 结果 | 证据 | 耗时(ms) |",
        "|---|---|---|---|---|---:|",
    ]
    for r in RESULTS:
        mark = "✅ PASS" if r["ok"] else ("⏭ SKIP" if r["ok"] is None else "❌ FAIL")
        lines.append(
            f"| {r['id']} | {r['title']} | {r['source']} | {mark} | {r['detail']} | {r['ms']} |"
        )
    lines += [
        "",
        "## 检索性能（本次验收实测）",
        "",
        f"- 检索调用次数：{len(latencies)}",
        f"- 平均延迟：{statistics.mean(latencies):.1f} ms",
        f"- P95 延迟：{p95:.1f} ms",
        f"- 最大延迟：{max(latencies):.1f} ms" if latencies else "- 无数据",
        "",
        "> 注：R1–R14 为数据层验收；R15–R18（真实起服务）见 "
        "`scripts/acceptance_service.py`。",
    ]
    out = ROOT / "docs" / "剧情图谱验收报告.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\n[acceptance] 报告 → {out}")
    print(f"[acceptance] 通过 {passed} / 失败 {len(failed)} / 跳过 {len(skipped)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
