"""P8 · 把 l5_drift 的 dr_<角色>_<检查点>.json 摊平成可安全喂给子代理的纯文本。

背景：dr_*.json 的 `history` / `card` 是 JSON 单行长串（实测 maxline 最长 1829 字），
read 工具对超长单行会截断，先前 P4.2 判分子代理集体卡死即此原因。
本脚本把每条 item 摊成「题头 + 软换行正文」，使子代理可整文件顺序读完。

红线（与仓库既有守门测试一致）：
- 只读 data/knowledge/_audit/l5_drift/dr_*.json；
- 只写 data/knowledge/_audit/l5_drift/_flatten/；
- 不用 rmtree / unlink（tests/compendium_rag/test_independence.py:265
  test_scripts_never_target_real_data_dir 要求 scripts/compendium_rag_*.py
  若出现 rmtree/unlink 必须把 data_dir 钉到临时目录）。
"""
from __future__ import annotations

import argparse
import json
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRIFT_DIR = ROOT / "data" / "knowledge" / "_audit" / "l5_drift"
OUT_DIR = DRIFT_DIR / "_flatten"
SEP = "=" * 20


def wrap(text: str, width: int) -> str:
    out: list[str] = []
    for para in str(text or "").split("\n"):
        para = para.rstrip()
        if not para:
            out.append("")
            continue
        out.extend(textwrap.wrap(para, width=width) or [""])
    return "\n".join(out)


def render_batch(d: dict, width: int) -> str:
    items = d.get("items", [])
    parts: list[str] = []
    for i, it in enumerate(items, 1):
        parts.append(f"{SEP} [{i}/{len(items)}] {it['qid']} | "
                     f"检查点 {it['checkpoint']}")
        parts.append(f"--- 探针 ---\n{wrap(it.get('query', ''), width)}")
        card = it.get("card") or ""
        parts.append(f"--- card（{len(card)} 字）---\n{wrap(card, width)}")
        hist = it.get("history") or ""
        parts.append(f"--- history（{len(hist)} 字）---\n{wrap(hist, width)}")
    return "\n\n".join(parts) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--wrap", type=int, default=100)
    ap.add_argument("--out", default=str(OUT_DIR))
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    files = []
    for p in sorted(DRIFT_DIR.glob("dr_*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        body = render_batch(d, args.wrap)
        dst = out_dir / (p.stem + ".txt")
        dst.write_text(body, encoding="utf-8")
        files.append({
            "file": dst.name, "source": p.name,
            "character": d.get("character", p.stem),
            "items": len(d.get("items", [])),
            "qids": [it["qid"] for it in d.get("items", [])],
            "bytes": len(body.encode("utf-8")),
            "lines": body.count("\n") + 1,
            "maxline": max((len(x) for x in body.split("\n")), default=0),
        })
    manifest = {"schema": "audit.l5_drift_flatten/v1", "wrap": args.wrap,
                "out_dir": str(out_dir), "files": files}
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[flatten] {len(files)} 文件 → {out_dir}")
    for f in files:
        print(f"  {f['file']:26s} items={f['items']} bytes={f['bytes']:6d} "
              f"lines={f['lines']:5d} maxline={f['maxline']}")
    print(f"[flatten] manifest: wrap={args.wrap} "
          f"qids 合计={sum(f['items'] for f in files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
