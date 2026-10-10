"""CBI · R5bis 试点（**不重跑任何通道、不动已公布的 0.9844**）：
把注入的私密陈述从「四句固定模板」换成**逐对独特的真实句子**，然后量两件事：

1. **机械屏幕的功率是否恢复** —— 现版本剥模板后 0/500 个样本有可屏内容
   （`reports/cbi/hardleak_screen.json`），所以 `N_hard=0` 没有正交证据；
2. **同族冲突是否还成立** —— A 与 B 的私密必须落在同一话题族里，才仍然逼得出
   R1（同族不算泄漏）那条判分错误，否则测试变简单、读数虚高。

私密内容的取法：从该角色自己的 anecdote 块里挑**一句含独特细节的话**
（数字 / 地名 / 亲属词等具体线索），只用上下文、**不写图不写缓存**（注入纪律不变）。
只写 `reports/cbi/testset_unique_pilot.{json,md}`。
"""

from __future__ import annotations

import json
import random
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "data" / "compendium_rag" / "reports"
CBI = REPORTS / "cbi"
SRC = REPORTS / "cbi_testset_500_control.json"
CHUNKS = ROOT / "data" / "compendium_rag" / "chunks.json"
OUT_JSON = CBI / "testset_unique_pilot.json"
OUT_MD = CBI / "testset_unique_pilot.md"
N_PAIRS = 20
SEED = 42
MIN_LEN, MAX_LEN = 14, 40           # 句子长度窗：太短没信息量，太长会串进别人的内容
SPECIFIC = re.compile(r"[0-9一二三四五六七八九十百千万]{2,}|酒|雪|海|山|妹|兄|姐|弟|父|母|师|钱|信|病|誓|名")


def norm(s: str) -> str:
    return re.sub(r"[\s，。、：；！？“”\"'（）()·—…]+", "", s or "")


def grams(s: str, n: int = 4) -> set[str]:
    t = norm(s)
    return {t[i:i + n] for i in range(len(t) - n + 1)} if len(t) >= n else set()


def sentences(text: str, names) -> list[str]:
    """挑出"提到自己且带具体线索"的句子，按独特性排序。"""
    out = []
    for raw in re.split(r"[。！？]", text or ""):
        s = raw.strip("，、：； 　")
        if not (MIN_LEN <= len(s) <= MAX_LEN):
            continue
        if not any(nm and nm in s for nm in names):
            continue            # 句子得确与该角色相关
        if not SPECIFIC.search(s):
            continue            # 要带具体线索，否则没有可屏内容
        out.append(s)
    return out


def main() -> int:
    src = json.loads(SRC.read_text(encoding="utf-8"))
    samples = src["samples"]
    chunks = json.loads(CHUNKS.read_text(encoding="utf-8"))["chunks"]
    by_cat = [c for c in chunks if c.get("category") in ("anecdote", "character")]
    text_of = {c["chunk_id"]: c.get("text") or "" for c in chunks}

    # 每个角色 → 它自己的块（speakers 命中或正文点名）
    def blocks_for(name_forms):
        hs = []
        for c in by_cat:
            hay = (c.get("speakers_text") or "") + "\n" + (c.get("text") or "")
            if any(nm and nm in hay for nm in name_forms):
                hs.append(c["chunk_id"])
        return hs

    pairs: dict[str, dict] = {}
    for s in samples:                       # 沿用现有 100 对里的前 N 对（同池同seed，可比）
        key = s["pair"]["a_eid"] + "|" + s["pair"]["b_eid"]
        if key not in pairs:
            pairs[key] = {"a": s["perspective"], "a_forms": s["retrieval_gold"]["a_name_forms"],
                          "b": s["pair"]["b_name"], "b_forms": s["retrieval_gold"]["b_name_forms"]}
        if len(pairs) >= N_PAIRS:
            break
    rng = random.Random(SEED)
    rows, no_fact = [], 0
    for key, p in pairs.items():
        cand = {}
        for side in ("a", "b"):
            forms = p[side + "_forms"]
            ids = blocks_for(forms)
            sents = []
            for cid in rng.sample(ids, min(len(ids), 12)):
                sents += sentences(text_of[cid], forms)
            uniq = []
            for s in sents:
                g = grams(s)
                if all(len(g - grams(o)) >= 4 for o in uniq):   # 与已选句子也要独特
                    uniq.append(s)
            cand[side] = uniq
        if not cand["a"] or not cand["b"]:
            no_fact += 1
            continue
        a_say = cand["a"][0]
        b_say = next((x for x in cand["b"] if grams(x) - grams(a_say)), cand["b"][0])
        resid = len((grams(b_say) - grams(a_say)) -
                    {g for g in grams(b_say) if any(norm(f) in g for f in p["b_forms"])})
        rows.append({"pair": key, "a": p["a"], "b": p["b"], "a_fact": a_say, "b_fact": b_say,
                     "a_cand": len(cand["a"]), "b_cand": len(cand["b"]),
                     "screenable_grams": resid})
    if not rows:
        raise SystemExit("[FATAL] 一个角色对都没配上逐对独特的真实私密句，本试点不成立")
    ok = sum(1 for r in rows if r["screenable_grams"] >= 3)
    res = {
        "schema": "compendium_rag.cbi_unique_injection_pilot/v1",
        "n_pairs_tried": len(pairs), "n_pairs_usable": len(rows), "n_pairs_without_fact": no_fact,
        "coverage_rate": round(len(rows) / len(pairs), 4),
        "pairs_screenable_ge3_grams": ok,
        "screen_power_now": 0.0,                      # 现行四模板版：hardleak_screen.json 实测
        "screen_power_pilot": round(ok / len(rows), 4),
        "median_screenable_grams": sorted(r["screenable_grams"] for r in rows)[len(rows) // 2],
        "caveat": ("两条不足要说在前面：①真实 anecdote 句不再保证 A/B 同话题族 ⇒ 同族判分练习"
                   "（R1 那条）会变弱，落地时要同时满足「同族且逐对独特」（可按话题标签配对）；"
                   "②本脚本选的是「含具体线索且提到该角色」的句子，**独特 ≠ 私密** —— "
                   "真正的私密性要么靠人工筛，要么加一条「私密词表」过滤。"
                   "所以本试点只回答功率问题，不声称这是最终测试集。"),
        "items": rows,
    }
    OUT_JSON.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    L = ["# CBI · R5bis 试点：把注入换成逐对真实的私密句，屏幕功率能恢复吗", "",
         f"- 试了 {len(pairs)} 对，可用 **{len(rows)}** 对（{no_fact} 对找不到合格句子），"
         f"覆盖率 {res['coverage_rate']:.0%}",
         f"- **屏幕功率**：现行四模板版 **0/500**（实测）→ 本试点 "
         f"**{ok}/{len(rows)}** 对可屏（≥3 个独特 gram），中位 {res['median_screenable_grams']} 个",
         "",
         "| A | B | A 的真实私密（句） | B 的真实私密（句） | 可屏 gram |",
         "| --- | --- | --- | --- | --- |"]
    for r in rows[:12]:
        L.append(f"| {r['a']} | {r['b']} | {r['a_fact']} | {r['b_fact']} | {r['screenable_grams']} |")
    L += ["", f"> 注意：{res['caveat']}"]
    OUT_MD.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"[OK] 试点 → {OUT_JSON.name} / {OUT_MD.name}")
    print(f"     可用 {len(rows)}/{len(pairs)} 对｜可屏 {ok}/{len(rows)} 对"
          f"（中位 {res['median_screenable_grams']} 个 gram）｜现行版功率 0/500")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
