# -*- coding: utf-8 -*-
"""v9-P3 步骤1 · 行为恒等 A/B（只读，不改工作树、不写图谱）。

P3 第一步做了两件声称「值不变、只改标签和耗时」的事：
1. 误标改名：``Evidence.ppr`` → ``graph_score``，边字典键 ``ppr`` → ``edge_score``；
2. 删掉 ``retrieve()`` 里**第二次** ``graph_channel(seeds)`` 调用（原来只为再取一遍
   同一个 chunk 分数 map）。

声称恒等就得证明恒等。做法：把 ``git show HEAD:...retriever.py``（= 改动前）放进
一个临时包树跑同一批题，与当前工作树跑的结果**逐位对比**。临时树里只有
retriever.py 是旧版，pipeline.py 沿用工作树、仅回退那一处参数接线，
这样 A/B 隔离出的就是「改动前 vs 改动后」本身。

口径：``use_vector=False``（graph_only，零网络零 LLM）、冻结融合口径
（LEX_WEIGHT=1.0 / RRF_K=1 / LEX_FIRST=0 / PYTHONHASHSEED=0）。
向量通道不涉及本次改动，关掉是为了让 A/B 不依赖 Ollama 的可用性。

用法：
    PYTHONPATH=src .venv/Scripts/python.exe -X utf8 \\
        scripts/compendium_rag_p3_identity_ab.py
产物：``data/compendium_rag/reports/p3_identity_ab.{json,md}``
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from compendium_rag.config import get_settings  # noqa: E402

EXPECTED_SHA = "7cac5867e8c80879"      # v9-a（P1 产出）
PY = sys.executable
R = ROOT / "data" / "compendium_rag" / "reports"
SETS = {
    "300cn": ROOT / "data" / "knowledge" / "_audit" / "rag_testset_300_cn.json",
    "blind206": ROOT / "data" / "knowledge" / "_audit" / "blind_v1" / "questions_strict.json",
    "gen120": ROOT / "data" / "knowledge" / "_audit" / "rag_testset_gen_r1r2.json",
}
PER_SET = 8
OLD_PLUMB = "rrf_k=s.rrf_k)"
# 工作树里 KnowledgeBase.retrieve 的那一处调用：从 rrf_k=... 到闭合括号。
PLUMB_RE = re.compile(r"rrf_k=s\.rrf_k[^)]*\)")
# 回退时必须**看到**这几个接线，否则说明源码已变、脚本的隔离前提不再成立
PLUMB_MUST_CONTAIN = ("ppr_damping=s.ppr_damping", "ppr_max_iter=s.ppr_max_iter")

CALIBER = {"CMPRAG_LEX_WEIGHT": "1.0", "CMPRAG_RRF_K": "1",
           "CMPRAG_LEX_FIRST": "0", "PYTHONHASHSEED": "0"}


def sha16(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def sample_queries() -> list[dict]:
    """按 qid 排序取每集前 PER_SET 题——样本必须可重放，不靠随机。"""
    out = []
    for tag, path in SETS.items():
        d = json.loads(path.read_text(encoding="utf-8"))
        rows = d if isinstance(d, list) else d.get("cases", [])
        qkey = "q" if "q" in rows[0] else "question"
        ikey = "id" if "id" in rows[0] else "qid"
        picked = sorted(rows, key=lambda r: str(r.get(ikey, "")))[:PER_SET]
        for r in picked:
            out.append({"set": tag, "qid": str(r.get(ikey, "")),
                        "query": r.get(qkey, "")})
    return out


DRIVER = '''# -*- coding: utf-8 -*-
import asyncio, dataclasses, json, os, sys, time
from pathlib import Path
from compendium_rag import pipeline as P
from compendium_rag.config import get_settings

queries = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
s = dataclasses.replace(get_settings(), data_dir=Path(os.environ["AB_DATA_DIR"]))
kb = P.load_kb(s)
rows = []
for q in queries:
    t0 = time.time()
    res = asyncio.run(kb.retrieve(q["query"], top_k=s.top_k, use_vector=False))
    rows.append({"set": q["set"], "qid": q["qid"],
                 "seconds": round(time.time() - t0, 4), "res": res})
Path(sys.argv[2]).write_text(json.dumps(rows, ensure_ascii=False, indent=1),
                             encoding="utf-8")
print("driver ok", len(rows))
'''


def build_old_tree(tmp: Path) -> Path:
    """临时包树：工作树全文 + HEAD 版 retriever.py + 回退那一处参数接线。"""
    old_root = tmp / "old_src"
    shutil.copytree(ROOT / "src" / "compendium_rag", old_root / "compendium_rag")
    pkg = old_root / "compendium_rag"
    for name in ("__pycache__",):
        shutil.rmtree(pkg / name, ignore_errors=True)
    head = subprocess.run(
        ["git", "show", "HEAD:src/compendium_rag/retriever.py"],
        cwd=str(ROOT), capture_output=True, check=True).stdout
    if b"e.ppr = ppr_map" not in head:
        raise SystemExit("HEAD 版 retriever.py 里没有待删的重复调用，A/B 前提不成立")
    (pkg / "retriever.py").write_bytes(head)
    pp = pkg / "pipeline.py"
    txt = pp.read_text(encoding="utf-8")
    hits = list(PLUMB_RE.finditer(txt))
    if len(hits) != 1:
        raise SystemExit(f"pipeline 检索接线处数={len(hits)}，应为 1（脚本需随源码更新）")
    m = hits[0]
    missing = [k for k in PLUMB_MUST_CONTAIN if k not in m.group(0)]
    if missing:
        raise SystemExit(f"接线里缺少待回退项 {missing}——A/B 前提不成立，中止")
    pp.write_text(txt[:m.start()] + OLD_PLUMB + txt[m.end():], encoding="utf-8")
    return old_root


def run_side(label: str, src_dir: Path, queries: list[Path]) -> list[dict]:
    env = dict(os.environ)
    env.update(CALIBER)
    env["AB_DATA_DIR"] = str(ROOT / "data" / "compendium_rag")
    env["PYTHONPATH"] = str(src_dir) + os.pathsep + str(ROOT / "src")
    proc = subprocess.run([PY, "-X", "utf8", str(queries[0]), str(queries[1]),
                           str(queries[2])], env=env, capture_output=True)
    if proc.returncode != 0:
        raise SystemExit(f"{label} 侧驱动失败：\n{proc.stdout.decode('utf-8', 'replace')}"
                         f"\n{proc.stderr.decode('utf-8', 'replace')}")
    out = json.loads(Path(queries[2]).read_text(encoding="utf-8"))
    print(f"[{label}] {len(out)} 题，总墙钟 {sum(r['seconds'] for r in out):.2f}s",
          flush=True)
    return out


def normalize(res: dict) -> dict:
    """把旧版键名映射到新名，使「只差标签」的两侧可逐位比对。"""
    r = json.loads(json.dumps(res))
    for e in r.get("edges", []):
        if "ppr" in e:
            e["edge_score"] = e.pop("ppr")
    for e in r.get("evidence", []):
        if "ppr" in e:
            e["graph_score"] = e.pop("ppr")
    return r


def diff_rows(old: list[dict], new: list[dict]) -> dict:
    per = []
    for o, n in zip(old, new):
        assert o["qid"] == n["qid"], "两侧题目顺序不一致"
        a = json.dumps(normalize(o["res"]), sort_keys=True, ensure_ascii=False)
        b = json.dumps(n["res"], sort_keys=True, ensure_ascii=False)
        fields = []
        if a != b:
            ra, rb = normalize(o["res"]), n["res"]
            for k in sorted(set(ra) | set(rb)):
                if k == "seconds":
                    continue
                if json.dumps(ra.get(k), sort_keys=True) != json.dumps(rb.get(k), sort_keys=True):
                    fields.append(k)
        per.append({"set": o["set"], "qid": o["qid"], "identical": not fields,
                    "diff_fields": fields,
                    "old_seconds": o["seconds"], "new_seconds": n["seconds"],
                    "n_evidence": len(n["res"].get("evidence", [])),
                    "n_edges": len(n["res"].get("edges", []))})
    bad = [p for p in per if not p["identical"]]
    return {"cases": len(per), "mismatches": len(bad),
            "fields_seen": sorted({f for p in bad for f in p["diff_fields"]}),
            "per_case": per}


def main() -> int:
    gp = get_settings().graph_path
    sha = sha16(gp)
    if sha != EXPECTED_SHA:
        raise SystemExit(f"图指纹漂移：期望 {EXPECTED_SHA}，实际 {sha}，中止")
    qs = sample_queries()
    print(f"样本 {len(qs)} 题（{PER_SET}×{len(SETS)}），graph={sha}", flush=True)

    # 临时目录承载「旧版包树 + 两侧产物」，绝不落到 data/。
    # 写成 mkdtemp+rmtree 而非 TemporaryDirectory：tests/compendium_rag/
    # test_independence.py 对含删除操作的脚本按字面要求这两个名字。
    tmp = Path(tempfile.mkdtemp(prefix="p3ab_"))
    try:
        qfile = tmp / "queries.json"
        qfile.write_text(json.dumps(qs, ensure_ascii=False), encoding="utf-8")
        drv = tmp / "ab_driver.py"
        drv.write_text(DRIVER, encoding="utf-8")
        old_tree = build_old_tree(tmp)
        out_new, out_old = tmp / "new.json", tmp / "old.json"
        new_rows = run_side("new(工作树)", ROOT / "src", [drv, qfile, out_new])
        old_rows = run_side("old(HEAD)", old_tree, [drv, qfile, out_old])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    cmp = diff_rows(old_rows, new_rows)
    t_old = sum(r["seconds"] for r in old_rows)
    t_new = sum(r["seconds"] for r in new_rows)
    rep = {
        "done_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "graph_sha256_16": sha,
        "normalizer": json.loads(gp.read_text(encoding="utf-8")).get("normalizer"),
        "caliber": {**CALIBER, "use_vector": False, "mode": "graph_only",
                    "top_k": get_settings().top_k},
        "isolation": {"old_side": "临时包树 = 工作树 + HEAD 版 retriever.py + "
                                  "pipeline 仅回退 ppr_damping/ppr_max_iter 接线",
                      "why": "A/B 只隔离 P3 步骤1 本身；数据、索引、其余源码两侧全同"},
        "claims_tested": [
            "改名 ppr→graph_score / edges.ppr→edge_score 不动数值",
            "删掉第二次 graph_channel 后块分数仍等于原值（两次调用逐位相等）",
            "参数接线（ppr_damping/ppr_max_iter/graph_max_edges 走 Settings，"
            "默认 0.85/50/30）等于旧的字面量——接参数 ≠ 调参数",
        ],
        "identity": cmp,
        "wall_clock": {"old_total_s": round(t_old, 2), "new_total_s": round(t_new, 2),
                       "saved_pct": round(1 - t_new / t_old, 4) if t_old else None,
                       "per_query_old_mean": round(t_old / len(old_rows), 3),
                       "per_query_new_mean": round(t_new / len(new_rows), 3)},
        "verdict": "PASS" if cmp["mismatches"] == 0 else "FAIL",
        "sample_qids": [f"{r['set']}/{r['qid']}" for r in old_rows],
    }
    R.mkdir(parents=True, exist_ok=True)
    (R / "p3_identity_ab.json").write_text(
        json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")

    md = [
        "# v9-P3 步骤1 · 行为恒等 A/B",
        "",
        f"- 图谱 `{sha}`（normalizer `{rep['normalizer']}`），口径 "
        f"`graph_only / use_vector=False`、`{json.dumps(CALIBER, ensure_ascii=False)}`",
        f"- 隔离方式：{rep['isolation']['old_side']}；{rep['isolation']['why']}",
        "",
        f"**结论：{rep['verdict']}** —— {cmp['cases']} 题检索结果逐位对比，"
        f"不一致 **{cmp['mismatches']}** 题"
        + (f"（字段 {json.dumps(cmp['fields_seen'], ensure_ascii=False)}）"
           if cmp["fields_seen"] else "（含证据顺序、分数、graph_score、边分数）"),
        "",
        f"墙钟：旧 {rep['wall_clock']['old_total_s']}s → 新 "
        f"{rep['wall_clock']['new_total_s']}s（省 "
        f"{rep['wall_clock']['saved_pct']:.1%}；单题均 "
        f"{rep['wall_clock']['per_query_old_mean']}s → "
        f"{rep['wall_clock']['per_query_new_mean']}s）。"
        "这是删除第二次 PPR 遍历的收益，与得分无关。",
        "",
        "## 为什么这一步必须排在任何改排序的改动之前",
        "",
        "改名 + 去重是**值不变**的修，所以它可以当 P3 的对照锚：此后任何读数变化都只能",
        "归因于真正的口径改动（max_edges、角色域过滤），不会和标签改动混在一起。",
        "",
        "## 逐题",
        "",
        "| 集 | qid | 逐位一致 | 旧 s | 新 s | 证据 | 边 |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for p in cmp["per_case"]:
        md.append(f"| {p['set']} | {p['qid']} | "
                  f"{'✅' if p['identical'] else '❌ ' + ','.join(p['diff_fields'])} "
                  f"| {p['old_seconds']} | {p['new_seconds']} "
                  f"| {p['n_evidence']} | {p['n_edges']} |")
    md += ["", "> 只读脚本：不写图谱、不重建索引、不触 LLM/嵌入。", ""]
    (R / "p3_identity_ab.md").write_text("\n".join(md), encoding="utf-8")
    print(f"[{rep['verdict']}] mismatches={cmp['mismatches']} "
          f"墙钟 {rep['wall_clock']['old_total_s']}s -> {rep['wall_clock']['new_total_s']}s")
    return 0 if rep["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
