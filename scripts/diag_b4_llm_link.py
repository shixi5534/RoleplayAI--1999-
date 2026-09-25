# -*- coding: utf-8 -*-
"""B4 第三条路：**LLM 从正典名单里识别实体** —— 先测识别准确率。

为什么先测识别率而不是直接做扩展
    三次尝试的账要算清：
      ① 语义实体链接（bge-m3）  最多 +1 题
      ② 完美扩展天花板（作弊）   +25.67 pt
      ③ 伪相关反馈 PRF（自扩展） −2 ~ −9 pt（剂量相关，越扩越差）
    差距全在「**不知道答案实体**」。PRF 用第一轮块里的实体，而那些块本身就是错的，
    等于把噪声灌进查询，还自我强化。

    所以最后一条路是**外部知识**：灰机的正典名单（141 角色 + 184 NPC，中英对照）。
    但前提是 LLM 真能从名单里挑中正确实体——**先测这个，别又白做一遍**。

做法
    对 60 道 en_only 失分题，把「问题 + 正典名单」交给 qwen2.5:7b，
    让它挑 3 个最可能的角色；统计真实答案是否落在其中（识别命中率）。
    识别命中率就是这个 B4 方案的**天花板**。

用法：.venv/Scripts/python.exe -X utf8 scripts/diag_b4_llm_link.py
"""
from __future__ import annotations

import json
import sys
import time
import traceback
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

AUDIT = ROOT / "data" / "knowledge" / "_audit"
LOG = AUDIT / "_b4_llm_link.txt"
HB = AUDIT / "_b4_llm_heartbeat.txt"
OLLAMA = "http://localhost:11434"
MODEL = "qwen2.5:7b"
TOPK = 3


def beat(msg: str) -> None:
    with HB.open("a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%H:%M:%S')} {msg}\n")


def build_candidates() -> tuple[list[str], dict[str, set[str]]]:
    """返回（给 LLM 看的候选列表, 任意名字 -> 该实体的全部名字集合）。"""
    canon = json.loads((ROOT / "data" / "lore" / "wu_ming_zhe" / "huiji_canon.json")
                       .read_text(encoding="utf-8"))
    lines: list[str] = []
    groups: dict[str, set[str]] = {}
    for key in ("characters", "npcs"):
        for it in canon.get(key) or []:
            zh = str(it.get("zh") or "").strip()
            en = str(it.get("en") or "").strip()
            ident = str(it.get("identity") or "").strip()
            if not zh and not en:
                continue
            label = zh or en
            if en and en != zh:
                label += f"({en})"
            if ident:
                label += f"[{ident}]"
            lines.append(label)
            names = {n for n in (zh, en) if n}
            for n in list(names):
                groups.setdefault(n.lower(), set()).update(names)
    return lines, groups


def ask(query: str, cand_lines: list[str]) -> list[str]:
    prompt = (
        "以下是《重返未来：1999》的正典角色名单（中文名(英文名)[身份]）：\n"
        + "\n".join(cand_lines)
        + f"\n\n用户的问题：{query}\n\n"
        f"请从上面的名单中选出最可能出现在答案里的 {TOPK} 个角色。"
        "只输出名字，用英文逗号分隔，不要解释。例如：星锑,维尔汀,牙仙\n\n答案："
    )
    body = json.dumps({"model": MODEL, "prompt": prompt, "stream": False,
                       "options": {"temperature": 0.0, "num_predict": 64}}).encode("utf-8")
    req = urllib.request.Request(f"{OLLAMA}/api/generate", data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        d = json.loads(r.read().decode("utf-8"))
    raw = str(d.get("response") or "")
    parts = [x.strip() for x in raw.replace("，", ",").split(",") if x.strip()]
    return parts[:TOPK]


def run() -> int:
    out: list[str] = []

    def p(*a):
        line = " ".join(str(x) for x in a)
        out.append(line)
        print(line, flush=True)

    cand_lines, groups = build_candidates()
    p(f"正典候选 {len(cand_lines)} 条｜名称组 {len(groups)}")

    lang = json.loads((AUDIT / "diag_lang_headroom.json").read_text(encoding="utf-8"))
    fails = [r for r in (lang.get("rows") or [])
             if r.get("bucket") == "en_only" and not r.get("inject")]
    cases = {str(c.get("id")): c for c in
             json.loads((AUDIT / "rag_testset_300_clean.json").read_text(encoding="utf-8"))}
    beat(f"待评估 {len(fails)} 题")

    hit = 0
    tried = 0
    rows: list[dict] = []
    t0 = time.time()
    for i, r in enumerate(fails):
        if i % 10 == 0:
            beat(f"case {i}/{len(fails)}")
        item = cases.get(str(r.get("id")))
        if not item:
            continue
        gold: set[str] = set()
        for g in (item.get("evidence") or []):
            for k in (g if isinstance(g, list) else [g]):
                gold.update(groups.get(str(k).lower(), {str(k)}))
        try:
            picks = ask(item["q"], cand_lines)
        except Exception as exc:  # noqa: BLE001
            p(f"  [skip] {r.get('id')} {type(exc).__name__}")
            continue
        tried += 1
        pick_names: set[str] = set()
        for pk in picks:
            base = pk.split("(")[0].split("[")[0].strip()
            pick_names.update(groups.get(pk.lower(), set()))
            pick_names.add(pk)
            pick_names.add(base)
        ok = bool(gold & pick_names)
        hit += int(ok)
        rows.append({"id": r.get("id"), "q": item["q"], "picks": picks,
                     "gold": sorted(gold), "hit": ok})

    p()
    p("=" * 78)
    p(f"LLM 实体识别命中率｜有效 {tried} 题｜耗时 {(time.time() - t0) / 60:.1f} min")
    p("=" * 78)
    if tried:
        p(f"  Top-{TOPK} 命中真实答案：{hit}/{tried} = **{hit / tried:.1%}**")
    p()
    for r in rows[:15]:
        mark = "✅" if r["hit"] else "❌"
        p(f"  {mark} {r['id']} 选中={r['picks']}  真值={r['gold'][:3]}")
    p()
    acc = (hit / tried) if tried else 0.0
    if acc >= 0.35:
        p("✅ 识别率可用 ⇒ 值得把它做成查询扩展，再跑全量 A/B")
    else:
        p("❌ 识别率过低 ⇒ LLM 对这部作品的设定不熟，B4 走 LLM 这条路也不通")
        p("   （结论：B4 的天花板需要「懂设定的实体链接」，本环境没有可用来源）")

    LOG.write_text("\n".join(out), encoding="utf-8")
    (AUDIT / "b4_llm_link.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1),
                                            encoding="utf-8")
    return 0


def main() -> int:
    HB.write_text(f"start {time.strftime('%H:%M:%S')}\n", encoding="utf-8")
    try:
        rc = run()
        beat(f"正常返回 {rc}")
        return rc
    except BaseException:  # noqa: BLE001
        with LOG.open("a", encoding="utf-8") as f:
            f.write("\n[TRACEBACK]\n" + traceback.format_exc())
        beat("异常，已写 traceback")
        raise


if __name__ == "__main__":
    raise SystemExit(main())
