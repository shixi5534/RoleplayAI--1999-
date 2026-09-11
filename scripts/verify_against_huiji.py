# -*- coding: utf-8 -*-
"""剧情图谱 vs 灰机 wiki 事实核对。

用法（项目根目录）：
  .venv/Scripts/python.exe -X utf8 scripts/verify_against_huiji.py

流程：
  1. 用真实检索器对剧情图谱提问（走 PPR + 证据块）
  2. 把命中的证据文本与「灰机 wiki 权威断言」里的正/反向关键词做匹配
  3. 输出支持/冲突线索，供人工终裁（以灰机为准）
  4. 顺带扫描别名污染（乱码、长句、易混角色名）

灰机 wiki：https://res1999.huijiwiki.com/wiki/
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from roleplay.config import get_settings  # noqa: E402
from roleplay.core.knowledge.plot_graph import PlotGraphRegistry  # noqa: E402

CHARACTER = "wu_ming_zhe"

# ── 灰机 wiki 权威事实（2026-09-08 抓取） ──────────────────────────────
# support：证据块里命中任一词 → 支持该断言
# conflict：证据块里命中 → 与灰机说法相悖（需人工复核是否 ASR/抽取错误）
HUIJI_FACTS = [
    {
        "q": "暴雨是什么 谁可以免疫",
        "answer": "「暴雨」又称「雨幕」，雨滴自地面落向天空，使一切回溯到过去时空或重返未来；"
                  "第一场发生于 1999-12-31；唯一免疫者是维尔汀，其手提箱可隔绝暴雨、可带神秘学家"
                  "度过但对人类无效；人类与神秘学家接触后都会被回溯。",
        "source": "https://res1999.huijiwiki.com/wiki/暴雨",
        "support": ["回溯", "1999", "维尔汀", "Vertin", "手提箱", "suitcase", "immune", "雨幕"],
        "conflict": [],
    },
    {
        "q": "圣洛夫基金会 是做什么的",
        "answer": "人类和平安全理事会旗下组织，负责对神秘学家和神秘物品等进行发现、收容、管理与利用；"
                  "下设联合委员会、共融院、委外合约人才管理组织、第一防线学校、夜巡特遣管理局、司辰小队。",
        "source": "https://res1999.huijiwiki.com/wiki/圣洛夫基金会",
        "support": ["收容", "管理", "神秘学家", "Foundation", "委员会", "学校", "containment", "arcanist"],
        "conflict": [],
    },
    {
        "q": "重塑之手 的目标是什么",
        "answer": "神秘学恐怖组织（Manus Vindictae），领袖阿尔卡纳；热衷于引发争端以人为引发「暴雨」，"
                  "力求回到「秩序正确的时代」（神秘学家不受歧视的时代）；内部分追随者/门徒/信徒/使徒四类。",
        "source": "https://res1999.huijiwiki.com/wiki/重塑之手",
        "support": ["暴雨", "storm", "争端", "时代", "阿尔卡纳", "Arcana", "Manus", "秩序"],
        "conflict": [],
    },
    {
        "q": "无名者 是谁 属于哪个组织",
        "answer": "无名者 Ms. Stranger，没有名字、过往分崩离析的特工；司辰小队成员；"
                  "原展出于冰岛，后秘密转移至圣洛夫基金会，曾短暂展出于重塑之手；"
                  "淑女格蕾丝（Ms. Grace）即无名者，2.0 登场、3.7 加入征集。",
        "source": "https://res1999.huijiwiki.com/wiki/无名者",
        "support": ["Ms. Stranger", "Stranger", "特工", "agent", "基金会", "Foundation",
                    "重塑", "Manus", "格蕾丝", "Grace"],
        # 灰机：基金会收容无名者；若图谱说「无名者持有基金会」即方向倒置
        "conflict": [],
    },
    {
        "q": "伊戈尔 属于哪个阵营",
        "answer": "原属芝诺阵营；于「忧郁的热带」叛变加入重塑之手；在「远征记」中被证明脱离重塑之手。",
        "source": "https://res1999.huijiwiki.com/wiki/重塑之手",
        "support": ["芝诺", "Zeno", "重塑", "Manus", "叛变", "defect", "12 squad", "小队"],
        "conflict": [],
    },
    {
        "q": "维尔汀 的身份",
        "answer": "司辰（Timekeeper）；基金会成员，第一防线学校毕业；司辰小队领导者；"
                  "唯一天然免疫暴雨者。",
        "source": "https://res1999.huijiwiki.com/wiki/圣洛夫基金会",
        "support": ["司辰", "Timekeeper", "Vertin", "基金会", "Foundation", "学校", "免疫"],
        "conflict": [],
    },
]

# 已知需重点复核的边（图谱侧说法 vs 灰机）
EDGE_AUDIT = [
    ("无名者", "持有", "圣洛夫基金会"),
    ("伊戈尔", "隶属于", "圣洛夫基金会"),
    ("重塑之手", "持有", "阿尔卡纳"),
    ("阿尔卡纳", "不是", "Verta"),
    ("伊戈尔", "是", "my father"),
]


def _alias_smell(name: str, aliases: list[str]) -> list[str]:
    """别名污染：乱码、整句、易混角色名。"""
    bad = []
    for a in aliases:
        s = str(a or "").strip()
        if not s:
            continue
        # 非中日韩/拉丁的可疑脚本（如天城文）
        for ch_ in s:
            if ord(ch_) > 0x0900 and not ("一" <= ch_ <= "鿿") and not ch_.isalnum():
                if unicodedata.name(ch_, "").startswith(("DEVANAGARI", "ARABIC", "THAI")):
                    bad.append(f"乱码字符 {s!r}")
                    break
        if len(s) >= 16:
            bad.append(f"疑似整句 {s[:24]}…")
        if re.search(r"\b(Lucy|Madam Lucy)\b", s, re.I):
            bad.append(f"易混角色名 {s!r}（露西 Lucy 是另一角色）")
        if re.fullmatch(r"(my |his |her |their )[a-z ]+", s, re.I):
            bad.append(f"英文代词短语 {s!r}")
    return bad


def main() -> int:
    settings = get_settings()
    reg = PlotGraphRegistry(
        corpus_dir=settings.plot_corpus_dir,
        graph_dir=settings.plot_graph_dir,
        alias_dir=settings.plot_lore_dir,
        include_weak=bool(settings.plot_include_weak),
    )
    retr = reg.get(CHARACTER)
    if retr is None:
        print("[FATAL] 检索器加载失败")
        return 1
    store = retr.store
    name_of = {e["id"]: e.get("name") for e in store.entities()}

    print("=" * 78)
    print("图谱证据 vs 灰机 wiki 权威断言")
    print("=" * 78)
    for f in HUIJI_FACTS:
        chunks = retr.retrieve(f["q"], top_chunks=5)
        print(f"\n【问】{f['q']}")
        print(f"【灰机】{f['answer']}")
        print(f"【来源】{f['source']}")
        hits_s, hits_c = set(), set()
        for c in chunks:
            t = c.text
            for k in f["support"]:
                if k.lower() in t.lower():
                    hits_s.add(k)
            for k in f["conflict"]:
                if k.lower() in t.lower():
                    hits_c.add(k)
            via = c.metadata.get("via")
            edge = c.metadata.get("edge") or "—"
            print(f"  - [{via}] {edge}")
            print(f"    {t[:150]}")
        print(f"  >> 支持线索：{sorted(hits_s) or '无'}")
        if hits_c:
            print(f"  >> 冲突线索：{sorted(hits_c)}")

    # ── 重点边复核 ──
    print("\n" + "=" * 78)
    print("重点边复核（图谱说法 vs 灰机）")
    print("=" * 78)
    corpus = json.loads(
        (ROOT / "data" / "knowledge" / f"plot_corpus_{CHARACTER}.json").read_text(encoding="utf-8")
    )
    chunks = corpus["chunks"] if isinstance(corpus, dict) else corpus
    txt = {c["hash"]: c.get("text", "") for c in chunks}
    ver = {c["hash"]: c.get("version") for c in chunks}
    for s, rel, d in EDGE_AUDIT:
        found = False
        for e in store.all_edges():
            if (name_of.get(e.get("src")) == s and e.get("relation") == rel
                    and name_of.get(e.get("dst")) == d):
                found = True
                for ev in e.get("evidence") or []:
                    h = ev.get("hash", "")
                    print(f"\n* {s} —{rel}→ {d}  [v{ver.get(h)}] {ev.get('doc_id')}")
                    print(f"  原文：{txt.get(h, '')[:300]}")
                break
        if not found:
            print(f"\n* {s} —{rel}→ {d}  （图中不存在）")

    # ── 别名污染扫描 ──
    print("\n" + "=" * 78)
    print("别名污染扫描")
    print("=" * 78)
    n_bad = 0
    for e in store.entities():
        smells = _alias_smell(str(e.get("name") or ""), [str(a) for a in (e.get("aliases") or [])])
        if smells:
            n_bad += 1
            print(f"* {e.get('name')}：{smells}")
    print(f"\n合计异常实体 {n_bad}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
