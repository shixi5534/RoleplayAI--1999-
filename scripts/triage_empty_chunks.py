"""对 408 块「空抽取」做价值分诊：命中已知实体 → 真漏抽；否则 → 合理为空。

判据：块文本里出现图谱已有实体名 / 别名索引中的表层形式（长度≥3），
或命中 wiki_zh_en 的英文名。输出 data/knowledge/_audit/triage_*.json。
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

GRAPH = ROOT / "data/knowledge/plot_graph_wu_ming_zhe.json"
WIKI = ROOT / "data/lore/wu_ming_zhe/wiki_zh_en.json"
ALIASES = ROOT / "data/lore/wu_ming_zhe/plot_aliases.json"
OUT = ROOT / "data/knowledge/_audit"
BATCHES = ["empty_batch_A.txt", "empty_batch_B.txt", "empty_batch_C.txt"]

# 过泛、命中无意义的表层形式
STOP = {
    "the", "and", "you", "your", "she", "her", "his", "him", "they", "them",
    "that", "this", "with", "from", "have", "will", "what", "when", "who",
    "all", "one", "out", "now", "not", "but", "for", "are", "was", "were",
    "off", "our", "can", "get", "got", "its", "don", "here", "left", "may",
    "many", "let's", "let", "yes", "hey", "today", "many", "come", "came",
    "time", "world", "place", "day", "work", "city", "life", "lives", "home",
    "building", "door", "hand", "head", "man", "men", "people", "child",
    "children", "boy", "girl", "friend", "sir", "madam", "miss", "mister",
    "gold", "food", "earth", "space", "sun", "order", "data", "attack",
    "harvest", "bandits", "era", "country", "comrades", "local", "guide",
    "signals", "spirits", "beast", "beasts", "phantom", "emperor", "march",
    "mother", "many", "i can't", "cover your nose", "detention room",
    "exhibition hall", "mexico", "mexico city", "antarctica", "left",
}
# 命中率过高（> 此比例的空块都命中）→ 判定为通用词，不参与分诊
DF_MAX_RATIO = 0.12


def load_surface() -> set[str]:
    surf: set[str] = set()
    g = json.loads(GRAPH.read_text(encoding="utf-8"))
    for name in g.get("entities", {}).values():
        if isinstance(name, dict):
            name = name.get("name")
        if isinstance(name, str):
            surf.add(name.strip())
    for k in g.get("alias_index", {}):
        if isinstance(k, str):
            surf.add(k.strip())
    if WIKI.exists():
        w = json.loads(WIKI.read_text(encoding="utf-8"))
        for k, v in w.items():
            if k.startswith("_"):
                continue
            if isinstance(v, str):
                surf.add(k.strip())
                surf.add(v.strip())
    if ALIASES.exists():
        a = json.loads(ALIASES.read_text(encoding="utf-8"))
        for k, vs in a.items():
            if k.startswith("_"):
                continue
            surf.add(str(k).strip())
            for v in vs or []:
                surf.add(str(v).strip())
    return {s for s in surf if len(s) >= 3 and s.lower() not in STOP}


def parse_blocks(path: Path):
    text = path.read_text(encoding="utf-8")
    for raw in text.split("\n\n"):
        raw = raw.strip()
        if not raw:
            continue
        lines = raw.split("\n")
        head = lines[0].split("\t")
        if len(head) < 4:
            continue
        yield {
            "hash": head[0],
            "lang": head[1],
            "version": head[2],
            "score": float(head[3]) if head[3] not in ("-", "") else 0.0,
            "text": "\n".join(lines[1:]).strip(),
        }


def main() -> None:
    surf = load_surface()
    # 只保留「看起来像专名」的表层形式：含 CJK，或首字母大写
    surf = {
        s for s in surf
        if re.search(r"[\u4e00-\u9fff]", s) or (s[:1].isupper() and s[:1].isalpha())
    }

    blocks: list[dict] = []
    for b in BATCHES:
        p = OUT / b
        if not p.exists():
            continue
        for blk in parse_blocks(p):
            blk["batch"] = b.split("_")[-1].replace(".txt", "")
            blocks.append(blk)

    # 长名优先，避免短名先命中
    ordered = sorted(surf, key=lambda s: -len(s))
    pats = [(s, re.compile(r"(?<![A-Za-z])" + re.escape(s) + r"(?![A-Za-z])", re.I))
            for s in ordered]

    # 第一遍：统计文档频率，剔除通用词（Don/Will/Here/time…）
    from collections import Counter
    df: Counter = Counter()
    for blk in blocks:
        t = blk["text"]
        for s, rx in pats:
            if rx.search(t):
                df[s.lower()] += 1
    n = max(1, len(blocks))
    generic = {k for k, v in df.items() if v / n > DF_MAX_RATIO}
    pats = [(s, rx) for s, rx in pats if s.lower() not in generic]
    print(f"[df] 剔除通用词 {len(generic)} 个（命中率 >{DF_MAX_RATIO:.0%}）："
          f"{', '.join(sorted(generic)[:20])}")

    worth, noop = [], []
    for blk in blocks:
        hits = sorted({s for s, rx in pats if rx.search(blk["text"])})
        blk["hits"] = hits
        (worth if hits else noop).append(blk)

    worth.sort(key=lambda b: (b["batch"], -len(b["hits"]), -b["score"]))
    (OUT / "triage_worth.json").write_text(
        json.dumps(worth, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / "triage_noop.json").write_text(
        json.dumps(noop, ensure_ascii=False, indent=1), encoding="utf-8")

    # 便于人工/云端补抽阅读的纯文本清单（含已知实体提示）
    lines: list[str] = []
    for b in worth:
        lines.append(
            f"### {b['hash']} | {b['lang']} | v{b['version']} | "
            f"score={b['score']} | hits: {', '.join(b['hits'])}"
        )
        lines.append(b["text"])
        lines.append("")
    (OUT / "triage_worth.txt").write_text("\n".join(lines), encoding="utf-8")

    print(f"known surfaces : {len(surf)}")
    print(f"真漏抽(命中已知实体): {len(worth)}")
    print(f"合理为空(无命中)  : {len(noop)}")
    c = Counter(len(b["hits"]) for b in worth)
    print("命中数分布:", dict(sorted(c.items())))
    print("\n-- 命中最多 15 块 --")
    for b in worth[:15]:
        print(f"[{b['hash']}] n={len(b['hits'])} score={b['score']} :: "
              f"{', '.join(b['hits'][:8])}")
    print("\n-- top 表面形式 --")
    cc = Counter(h for b in worth for h in b["hits"])
    for k, v in cc.most_common(30):
        print(f"  {v:4d}  {k}")


if __name__ == "__main__":
    main()
