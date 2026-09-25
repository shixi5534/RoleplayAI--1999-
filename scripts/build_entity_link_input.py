# -*- coding: utf-8 -*-
"""为「人工/强模型实体识别」准备输入：问题 + 候选实体名（**不含答案**）。

背景
    本地 qwen2.5:7b 从正典名单识别实体的命中率只有 15%（不懂该作品设定）。
    改用强模型（由 agent 本人担任标注者）来做，本脚本准备输入、并做**盲测**：
    · 输入只含：问题原文 + 检索到的块里**出现过的实体名** + 正典名单
    · **绝不包含 evidence / 答案关键词**（否则就是抄答案，结论无效）

产物
    _audit/entity_link_input.txt   人可读（agent 直接读它做判断）
    _audit/entity_link_input.json  结构化（agent 写回预测用）

用法：.venv/Scripts/python.exe -X utf8 scripts/build_entity_link_input.py
"""
from __future__ import annotations

import json
import sys
import time
import traceback
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import eval_plot_rag as E  # noqa: E402
from roleplay.config import get_settings  # noqa: E402
from roleplay.core.knowledge.factory import build_plot_registry  # noqa: E402

AUDIT = ROOT / "data" / "knowledge" / "_audit"
LOG = AUDIT / "_entity_input.txt"
HB = AUDIT / "_entity_input_heartbeat.txt"
TOPK_BLOCKS = 8
BLOCK_CHARS = 160      # 只给片段，防止变相喂答案
MAX_NAMES = 18


def beat(m: str) -> None:
    with HB.open("a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%H:%M:%S')} {m}\n")


def main() -> int:
    out: list[str] = []
    HB.write_text(f"start {time.strftime('%H:%M:%S')}\n", encoding="utf-8")

    def p(*a):
        line = " ".join(str(x) for x in a)
        out.append(line)
        print(line, flush=True)

    s = get_settings()
    retr = build_plot_registry(s).get("wu_ming_zhe")
    top = int(getattr(s, "plot_max_chunks", 6))
    lf = int(getattr(s, "plot_lexical_fallback", 2))

    cases = {str(c["id"]): c for c in
             json.loads((AUDIT / "rag_testset_300_clean.json").read_text(encoding="utf-8"))}
    rank = json.loads((AUDIT / "positive_rank.json").read_text(encoding="utf-8"))
    targets = [r for r in rank if r.get("verdict") == "A_不在候选池"]
    beat(f"目标 {len(targets)} 题")

    # 正典名单（只给名字，不给 identity 以外的信息）
    canon = json.loads((ROOT / "data" / "lore" / "wu_ming_zhe" / "huiji_canon.json")
                       .read_text(encoding="utf-8"))
    names: list[str] = []
    for key in ("characters", "npcs"):
        for it in canon.get(key) or []:
            zh = str(it.get("zh") or "").strip()
            en = str(it.get("en") or "").strip()
            ident = str(it.get("identity") or "").strip()
            if not zh and not en:
                continue
            s2 = (zh or en) + (f"({en})" if en and en != zh else "")
            if ident:
                s2 += f"[{ident}]"
            names.append(s2)

    payload: list[dict] = []
    for i, r in enumerate(targets):
        if i % 10 == 0:
            beat(f"case {i}/{len(targets)}")
        qid = str(r["id"])
        item = cases.get(qid)
        if not item:
            continue
        chunks = retr.retrieve(item["q"], top_chunks=top, lexical_fallback=lf)
        seen: Counter[str] = Counter()
        for c in chunks:
            try:
                linked = retr.link_detailed(c.text or "")
            except Exception:  # noqa: BLE001
                linked = {}
            for _eid, info in linked.items():
                nm = str(info.get("name") or "").strip()
                if nm:
                    seen[nm] += 1
        cand = [n for n, _ in seen.most_common(MAX_NAMES)]
        payload.append({
            "id": qid,
            "q": item["q"],
            "n_groups": len(item.get("evidence") or []),
            "cand_from_blocks": cand,
            "snippet": " | ".join(
                " ".join((c.text or "").split())[:BLOCK_CHARS] for c in chunks[:3]),
        })

    # 人可读版
    p("=" * 88)
    p(f"实体识别输入（盲测：不含答案）｜{len(payload)} 题")
    p("=" * 88)
    p()
    p("【正典名单】" + str(len(names)) + " 条")
    p("  " + " · ".join(names))
    p()
    p("=" * 88)
    for it in payload:
        p(f"[{it['id']}] {it['q']}")
        p(f"    证据组数={it['n_groups']}")
        p(f"    检索块中出现的实体：{', '.join(it['cand_from_blocks']) or '（无）'}")
        p(f"    块片段：{it['snippet'][:220]}")
        p()
    LOG.write_text("\n".join(out), encoding="utf-8")
    (AUDIT / "entity_link_input.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    (AUDIT / "canon_names.json").write_text(
        json.dumps(names, ensure_ascii=False, indent=1), encoding="utf-8")
    beat("完成")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except BaseException:  # noqa: BLE001
        with LOG.open("a", encoding="utf-8") as f:
            f.write("\n[TRACEBACK]\n" + traceback.format_exc())
        raise
