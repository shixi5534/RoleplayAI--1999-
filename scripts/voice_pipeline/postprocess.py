# -*- coding: utf-8 -*-
"""听录后处理：繁简统一 + 输出对照清单。

whisper 中文输出会繁简混用（同一段里"記憶"和"记忆"并存），直接入库会
污染 RAG 检索。这里统一为简体，并保留原文以备校对。

用法: python postprocess.py work/zh_whole/zh_whole.json
"""
import json
import os
import sys

from zhconv import convert


def main():
    src = sys.argv[1]
    d = json.load(open(src, encoding="utf-8"))
    for s in d["segments"]:
        s["text_raw"] = s["text"]
        s["text"] = convert(s["text"], "zh-cn")

    base = os.path.splitext(src)[0]
    json_out = base + "_clean.json"
    with open(json_out, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)

    md_out = base + "_clean.md"
    segs = d["segments"]
    lines = [f"# {os.path.basename(base)} 台词清单（简体统一）", "",
             f"- 源：{os.path.basename(d.get('source',''))}"
             f" ｜ 语言：{d.get('detected')} ｜ 模型：{os.path.basename(str(d.get('model')))}",
             f"- 段落：{len(segs)}", "",
             "| # | 起 | 止 | 文本 | 标记 |", "|---:|---:|---:|---|---|"]
    for s in segs:
        t = (s["text"] or "").replace("|", "｜").replace("\n", " ")
        lines.append(f"| {s['idx']} | {s['start']:.2f} | {s['end']:.2f} |"
                     f" {t} | {' '.join(s.get('flags', []))} |")
    with open(md_out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"saved {json_out} / {md_out} ({len(segs)} 段)")
    for s in segs:
        mark = " *" if s["text"] != s["text_raw"] else ""
        print(f"{s['start']:6.2f}-{s['end']:6.2f} | {s['text']}{mark}")


if __name__ == "__main__":
    main()
