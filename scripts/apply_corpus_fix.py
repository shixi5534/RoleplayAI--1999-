# -*- coding: utf-8 -*-
"""T15 落地：把《语料来源映射》中的安全修正应用到语料文件（**自动备份，可回滚**）。

只应用两类**证据充分**的修正：
  · arc 补全（104 doc）：原 arc 为空，由标题「篇章名」抽取得到（如
    《重返未来：1999》1.6版本「朔日手记」… → arc=朔日手记）；
  · lang 修正（3 doc）：标注为 other，实际块文本为英文 → en。

**不做**的事（避免引入新错误）：
  · 不为缺 version 的 doc 臆造版本号（灰机页与联动版本本来就没有版本号）；
  · 不改任何块文本、不改块切分、不动 hash。

用法（项目根目录）
------------------
    # 1) 预演（不写文件）
    .venv/Scripts/python.exe -X utf8 scripts/apply_corpus_fix.py --dry-run
    # 2) 落地（自动备份原文件）
    .venv/Scripts/python.exe -X utf8 scripts/apply_corpus_fix.py --apply

回滚：把生成的 `plot_corpus_wu_ming_zhe.json.bak_meta_<日期>` 复制回原文件名，
并重跑 `scripts/build_plot_index.py`（索引带 corpus_sha16 指纹，语料一变必须重建）。
"""
from __future__ import annotations

import argparse
import json
import shutil
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "data" / "knowledge" / "plot_corpus_wu_ming_zhe.json"
MAP = ROOT / "data" / "knowledge" / "_audit" / "corpus_source_map_20260917.json"
REPORT = ROOT / "data" / "knowledge" / "_audit" / "_corpus_fix_applied.txt"


def main() -> int:
    ap = argparse.ArgumentParser(description="应用语料元数据修正（需备份）")
    ap.add_argument("--apply", action="store_true", help="真正写文件（默认 dry-run）")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not MAP.is_file():
        print(f"[FAIL] 缺来源映射：{MAP}；请先跑 scripts/build_corpus_source_map.py")
        return 1
    src_map = json.loads(MAP.read_text(encoding="utf-8"))
    entries = {e["doc_id"]: e for e in src_map["entries"]}

    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    docs = corpus.get("docs") or {}
    n_arc = n_lang = 0
    samples: list[str] = []
    for d, m in docs.items():
        e = entries.get(d)
        if not e:
            continue
        if e.get("needs_arc_fix") and e.get("arc_suggest"):
            samples.append(f"  arc  {d}｜'' → {e['arc_suggest']}")
            if args.apply:
                m["arc"] = e["arc_suggest"]
            n_arc += 1
        if e.get("needs_lang_fix") and e.get("lang_suggest"):
            samples.append(f"  lang {d}｜{e.get('lang_declared')} → {e['lang_suggest']}")
            if args.apply:
                m["lang"] = e["lang_suggest"]
            n_lang += 1

    lines = [
        f"语料元数据修正{'（已应用）' if args.apply else '（dry-run）'}："
        f"arc {n_arc} 条｜lang {n_lang} 条",
        f"语料文件：{CORPUS}",
        "",
        "修正样例（前 20）：",
        *samples[:20],
    ]

    if args.apply:
        bak = CORPUS.with_name(CORPUS.name + f".bak_meta_{time.strftime('%Y%m%d_%H%M')}")
        shutil.copy2(CORPUS, bak)
        lines.append("")
        lines.append(f"已备份原文件 → {bak}")
        # 保持与原始 dump 一致的写法（ensure_ascii=False，紧凑）
        CORPUS.write_text(json.dumps(corpus, ensure_ascii=False), encoding="utf-8")
        lines.append("已写入修正后语料")
        lines.append("⚠️ 下一步必须重建语义索引（corpus_sha16 指纹会变）：")
        lines.append("   .venv/Scripts/python.exe -X utf8 scripts/build_plot_index.py "
                     "--character wu_ming_zhe")
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
