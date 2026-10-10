"""把 P7/L3 的批次文件摊平成「每问一段、软换行」的纯文本，供外部子代理稳定读取。

背景：``data/knowledge/_audit/p4_harness_<tag>/l3_batches/ans_bNN.json`` 单文件
160~400KB，且 ``prompt`` 字段是**单行 3000+ 字**的长行 —— 直接 read 会被长行截断，
是 P4.2 首派判分子代理失败的根因。

本脚本只读批次 json、只写 ``<state>/_flatten/`` 目录，不调 LLM、不联网、不碰图。
不用 rmtree/unlink（守门测试 tests/compendium_rag/test_independence.py:265 要求
``scripts/compendium_rag_*.py`` 出现 rmtree/unlink 时必须把 data_dir 钉到临时目录）。

用法::

    PYTHONPATH=src .venv/Scripts/python.exe -X utf8 \
        scripts/compendium_rag_p7_l3_flatten.py --tag r10 [--wrap 110] [--kind batch|judge]
"""
from __future__ import annotations

import argparse
import json
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data" / "knowledge" / "_audit"
SEP = "=" * 20


def wrap(s: str, width: int) -> str:
    out: list[str] = []
    for para in s.split("\n"):
        if not para.strip():
            out.append("")
            continue
        out.extend(textwrap.wrap(para, width=width) or [""])
    return "\n".join(out)


def flatten_items(items: list[dict], width: int, *, with_answer: bool) -> str:
    chunks: list[str] = []
    for i, it in enumerate(items, 1):
        head = f"{SEP} [{i}] {it.get('qid')} | {it.get('query', '')}"
        body = it.get("prompt") or it.get("context") or ""
        if not body:
            # 无 prompt 字段（旧批次）时手工拼 query+context
            body = f"【问题】\n{it.get('query', '')}\n\n【检索片段】\n{it.get('context', '')}"
        parts = [head, "--- prompt ---", wrap(body, width)]
        if with_answer:
            parts += ["--- answer ---", wrap(it.get("answer", ""), width)]
        chunks.append("\n".join(parts))
    return "\n\n".join(chunks) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="r10")
    ap.add_argument("--wrap", type=int, default=110)
    ap.add_argument("--page-lines", type=int, default=0,
                    help=">0 时按题切页，每页不超过该行数（供 read 工具稳定读取）")
    ap.add_argument("--kind", choices=("batch", "judge", "both"), default="both")
    args = ap.parse_args()

    state = AUDIT / f"p4_harness_{args.tag}"
    out_dir = state / "_flatten"
    out_dir.mkdir(parents=True, exist_ok=True)
    report: dict = {
        "tag": args.tag, "wrap": args.wrap, "page_lines": args.page_lines,
        "kinds": {},
    }

    def emit(kind: str, p: Path, items: list[dict]) -> list[dict]:
        """写一个源文件；page_lines>0 时按题打包成多页。返回行记录。"""
        rows: list[dict] = []
        if args.page_lines <= 0:
            txt = flatten_items(items, args.wrap, with_answer=kind == "judge")
            (out_dir / f"{p.stem}.txt").write_text(txt, encoding="utf-8")
            rows.append({
                "file": f"{p.stem}.txt", "items": len(items),
                "bytes": len(txt.encode("utf-8")), "lines": txt.count("\n") + 1,
                "qids": [it.get("qid") for it in items],
            })
            return rows
        # 按题打包分页：单题本身就超页也要单独成页
        pages: list[list[dict]] = []
        cur: list[dict] = []
        cur_lines = 0
        for it in items:
            block = flatten_items([it], args.wrap, with_answer=kind == "judge")
            n = block.count("\n") + 1
            if cur and cur_lines + n > args.page_lines:
                pages.append(cur)
                cur, cur_lines = [], 0
            cur.append(it)
            cur_lines += n
        if cur:
            pages.append(cur)
        for i, page in enumerate(pages, 1):
            txt = flatten_items(page, args.wrap, with_answer=kind == "judge")
            name = f"{p.stem}_p{i}.txt"
            (out_dir / name).write_text(txt, encoding="utf-8")
            rows.append({
                "file": name, "items": len(page),
                "bytes": len(txt.encode("utf-8")), "lines": txt.count("\n") + 1,
                "qids": [it.get("qid") for it in page],
            })
        return rows

    def do(kind: str, src_name: str, glob: str) -> None:
        src = state / src_name
        if not src.exists():
            report["kinds"][kind] = {"src": str(src), "status": "missing"}
            return
        rows = []
        for p in sorted(src.glob(glob)):
            d = json.loads(p.read_text(encoding="utf-8"))
            rows.extend(emit(kind, p, d.get("items") or []))
        report["kinds"][kind] = {
            "src": str(src.relative_to(ROOT)),
            "n_files": len(rows),
            "files": rows,
        }

    if args.kind in ("batch", "both"):
        do("batch", "l3_batches", "ans_b*.json")
    if args.kind in ("judge", "both"):
        do("judge", "l3_judge_in", "jdg_in_b*.json")
        rep_rows: list[dict] = []
        for p in sorted((state / "l3_judge_in").glob("rep_in_b*.json")):
            d = json.loads(p.read_text(encoding="utf-8"))
            rep_rows.extend(emit("judge", p, d.get("items") or []))
        report["kinds"]["repeat"] = {"n_files": len(rep_rows), "files": rep_rows}

    (out_dir / "manifest.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    for kind, info in report["kinds"].items():
        if "files" in info:
            tot = sum(f["bytes"] for f in info["files"])
            mx = max((f["lines"] for f in info["files"]), default=0)
            print(
                f"[{kind}] {info.get('n_files', len(info['files']))} files, "
                f"{tot} B, max_lines={mx} → {out_dir.relative_to(ROOT)}"
            )
        else:
            print(f"[{kind}] {info}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
