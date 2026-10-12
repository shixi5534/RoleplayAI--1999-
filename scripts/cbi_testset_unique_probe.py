"""R5bis 落地前的**覆盖率探针**（只读，不建测试集、不动任何已公布读数）。

预登记（跑前定死，写在这里）：
- 目标：沿用现行 100 个角色对（同池同 seed，检索通道读数可比），把四类
  「一句模板 × 名字替换」的注入换成**逐对真实、同话题族、来源可归位**的私密句。
- 一条合格事实必须同时满足四条：
  ① **来源独占**：取自该角色的独占块（A 的事实出自 A 独占块，B 的出自 B 独占块），
     这样"这条是谁的"有唯一答案；
  ② **自我点名**：句子确实提到该角色（名字或形式表），不是路人叙述；
  ③ **逐对独特**：剥掉 4 个话题族标签词与名字后，仍有 ≥3 个 4-gram 只在这一对出现；
  ④ **私密词命中**：句面含"私/瞒/从未/没人知道/旧事/债/病/逃/誓/藏/独自…"之一。
- A 与 B 的两条必须落在**同一话题族**（保留 R1 同族压力），但内容点必须不同。

判决线（先写死后跑）：
- 可用对 **≥ 90/100** ⇒ 直接建成 100×5=500，分母不变，可与 v1 逐行对比；
- **80–89** ⇒ 保持 100 对，缺口对**如实降级为 N<500 并单独报**（不改分母凑数，
  而是把可用对数当作测试集属性报出来，同时报缺失原因分布）；
- **< 80** ⇒ 不硬凑，回来找用户：要么扩角色对池（重出检索通道），要么接受这一族
  仍只测"注入复述"这一半。

只写 `reports/cbi/testset_unique_probe.{json,md}`。
用法：.venv/Scripts/python.exe -X utf8 scripts/cbi_testset_unique_probe.py
"""
from __future__ import annotations

import json
import random
import re
from collections import Counter
from pathlib import Path
import sys
# Windows 控制台常见 cp936：产物落盘后才抛 UnicodeEncodeError 最难查（写了一半、退出码非零）。
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(errors="replace")


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "data" / "compendium_rag" / "reports"
CBI = REPORTS / "cbi"
SRC = REPORTS / "cbi_testset_500_control.json"
CHUNKS = ROOT / "data" / "compendium_rag" / "chunks.json"
OUT_JSON = CBI / "testset_unique_probe.json"
OUT_MD = CBI / "testset_unique_probe.md"

SEED = 42
MIN_LEN, MAX_LEN = 14, 40
MIN_RESID_GRAMS = 3
SPECIFIC = re.compile(r"[0-9一二三四五六七八九十百千万]{2,}|酒|雪|海|山|妹|兄|姐|弟|父|母|师|"
                      r"钱|信|病|誓|名|盒|账|船|猫|花|药|钟|门|路|城|港|门|刀")
PRIVACY = re.compile(r"私|瞒|没告诉|未告|从不|从未|没人知道|谁都不|秘密|旧事|不敢|羞|"
                     r"债|病|逃|罪|誓|藏|独自|夜里|心里|不写在|不提")

FAMILIES = {
    "饮食与酒": r"酒|喝|饮|茶|咖啡|杯|宴|餐|瓶|烈|醉",
    "出身与地域": r"出生|故乡|长大|出身|南方|北方|海|山|城|村|港|岛|内陆|雪",
    "亲属与私人关系": r"妹|姐|兄|弟|父|母|妻|夫|儿|女|家|表|堂|亲属|孩子",
    "作息与习惯": r"每夜|每天|每日|清晨|夜里|黄昏|习惯|独自|散步|守夜|不睡|待|钟",
    "言谈与口吻": r"说话|口音|敬语|脏字|粗话|沉默|少话|喊|称呼|语气|用词|开不得玩笑",
    "财物与物件": r"钱|账|存|盒|信|勋章|戒指|收藏|债|图|钥匙|船|工具|种子",
    "旧事与身份": r"从前|当年|旧|曾|退役|逃|罪|打过|杀|伤|誓|名号|身份|名字",
    "身体与病": r"病|伤|咳|失眠|腿|眼|耳|医|药|身子|手抖",
}
FAM_RE = {k: re.compile(v) for k, v in FAMILIES.items()}


def norm(s: str) -> str:
    return re.sub(r"[\s，。、：；！？“”\"'（）()·—…]+", "", s or "")


def grams(s: str, n: int = 4) -> set[str]:
    t = norm(s)
    return {t[i:i + n] for i in range(len(t) - n + 1)} if len(t) >= n else set()


def families_of(s: str) -> list[str]:
    return [k for k, rx in FAM_RE.items() if rx.search(s)]


def main() -> int:
    src = json.loads(SRC.read_text(encoding="utf-8"))
    samples = src["samples"]
    chunks = json.loads(CHUNKS.read_text(encoding="utf-8"))["chunks"]
    text_of = {c["chunk_id"]: c.get("text") or "" for c in chunks}
    cat_of = {c["chunk_id"]: c.get("category") or "" for c in chunks}

    rng = random.Random(SEED)

    # 独占块按建集时的同一判据现算（retrieval_gold 里只存了 b_private_chunk）
    graph = json.loads((ROOT / "data" / "compendium_rag" / "graph.json").read_text(encoding="utf-8"))
    ents = {e["eid"]: e for e in graph["entities"]}
    names_of = {e["eid"]: {e["name"], *(e.get("aliases") or [])} for e in graph["entities"]}
    CATS = ("character", "anecdote")

    def exclusive(eid_own, eid_other):
        own, other = names_of[eid_own], names_of[eid_other]
        return [cid for cid in ents[eid_own].get("chunk_ids") or []
                if cat_of.get(cid) in CATS
                and any(n in text_of.get(cid, "") for n in own)
                and not any(n in text_of.get(cid, "") for n in other)]

    # 100 对，A 侧独占块 / B 侧独占块直接沿用测试集里算好的 retrieval_gold（同判据）
    pairs: dict[str, dict] = {}
    for s in samples:
        key = s["pair"]["a_eid"] + "|" + s["pair"]["b_eid"]
        if key not in pairs:
            g = s["retrieval_gold"]
            pairs[key] = {
                "a": s["perspective"], "a_forms": g["a_name_forms"],
                "a_excl": exclusive(s["pair"]["a_eid"], s["pair"]["b_eid"]),
                "b": s["pair"]["b_name"], "b_forms": g["b_name_forms"],
                "b_excl": exclusive(s["pair"]["b_eid"], s["pair"]["a_eid"]),
                "family_v1": s["conflict_type"],
            }
    if len(pairs) != 100:
        raise SystemExit(f"[FATAL] 角色对 {len(pairs)} != 100")

    rng = random.Random(SEED)

    def cands(forms, excl_ids) -> list[dict]:
        out, seen = [], set()
        ids = [cid for cid in excl_ids if cat_of.get(cid) in ("anecdote", "character")]
        for cid in sorted(ids):
            for raw in re.split(r"[。！？]", text_of.get(cid, "")):
                s = raw.strip("，、：； 　")
                if not (MIN_LEN <= len(s) <= MAX_LEN) or s in seen:
                    continue
                if not any(nm and nm in s for nm in forms):
                    continue
                if not SPECIFIC.search(s):
                    continue
                fam = families_of(s)
                if not fam:
                    continue
                seen.add(s)
                out.append({"text": s, "cid": cid, "fam": fam,
                            "priv": bool(PRIVACY.search(s))})
        return out

    def search(ca, cb, p, need_priv: bool, need_fam: bool):
        """在给定判据子集下找最佳配对；返回 None 表示这一档不成立。"""
        a_fams = {f for x in ca for f in x["fam"]}
        pool_b = [x for x in cb if x["priv"] or not need_priv]
        if need_fam:
            pool_b = [x for x in pool_b if any(f in a_fams for f in x["fam"])]
        best = None
        for b in pool_b:
            gb = grams(b["text"])
            resid_b = gb - grams("".join(x["text"] for x in ca))
            resid_b = resid_b - {g for g in gb
                                 if any(norm(f) in g for f in p["a_forms"] + p["b_forms"])}
            if len(resid_b) < MIN_RESID_GRAMS:
                continue
            for a in ca:
                shared = [f for f in b["fam"] if f in a["fam"]]
                if need_fam and not shared:
                    continue
                fam_label = shared[0] if shared else "跨族"
                ga = grams(a["text"])
                others = "".join(x["text"] for x in ca if x["text"] != a["text"])
                resid_a = ga - grams(others)
                resid_a = resid_a - {g for g in ga
                                     if any(norm(f) in g for f in p["a_forms"] + p["b_forms"])}
                if len(resid_a) < MIN_RESID_GRAMS:
                    continue
                if ga & gb:
                    continue
                score = len(resid_a) + len(resid_b)
                if best is None or score > best["score"]:
                    best = {"score": score, "fam": fam_label, "a_fact": a, "b_fact": b,
                            "resid_a": len(resid_a), "resid_b": len(resid_b),
                            "b_priv_lex": b["priv"]}
        return best

    LADDER = {"L0 只要求逐对独特": (False, False),
              "L1 + 同话题族": (False, True),
              "L2 + 私密词命中": (True, False),
              "L3 + 同话题族且私密词（目标）": (True, True)}
    lat_counts = Counter()
    rows, why = [], Counter()
    for key, p in pairs.items():
        ca, cb = cands(p["a_forms"], p["a_excl"]), cands(p["b_forms"], p["b_excl"])
        if not ca:
            why["A 侧无合格句"] += 1
            continue
        if not cb:
            why["B 侧无合格句"] += 1
            continue
        got = {}
        for label, (np, nf) in LADDER.items():
            r = search(ca, cb, p, np, nf)
            if r:
                lat_counts[label] += 1
            got[label] = r
        best = got["L3 + 同话题族且私密词（目标）"]
        if best is None:
            if not got["L1 + 同话题族"]:
                why["同族配不出（或独特性/不相交没过）"] += 1
            elif not got["L2 + 私密词命中"]:
                why["有同族独特对，但 B 侧句子不含私密词"] += 1
            else:
                why["L2/L1 单独都过，合起来没有同一句子同时满足"] += 1
            continue
        rows.append({"pair": key, "a": p["a"], "b": p["b"], "family": best["fam"],
                     "family_v1": p["family_v1"], "a_fact": best["a_fact"]["text"],
                     "a_src": best["a_fact"]["cid"], "b_fact": best["b_fact"]["text"],
                     "b_src": best["b_fact"]["cid"], "resid_a": best["resid_a"],
                     "resid_b": best["resid_b"], "b_priv_hit": True})

    n_ok = len(rows)
    band = ("直接建 100×5" if n_ok >= 90 else
            "保持 100 对、缺口如实降级并报原因" if n_ok >= 80 else
            "不硬凑：回来找用户（扩对池或接受半覆盖）")
    famdist = Counter(r["family"] for r in rows)
    med = sorted(min(r["resid_a"], r["resid_b"]) for r in rows)[n_ok // 2] if n_ok else 0
    n_cand = len(pairs) - why["A 侧无合格句"] - why["B 侧无合格句"]
    legal_pool = src.get("selection", {}).get("legal_pool_before_caps", 633)
    ladder = {k: lat_counts.get(k, 0) for k in LADDER}

    res = {"schema": "compendium_rag.cbi_unique_probe/v1",
           "n_pairs": len(pairs), "n_pairs_with_both_sides_cands": n_cand,
           "n_usable": n_ok, "coverage": round(n_ok / len(pairs), 4),
           "ladder_coverage": ladder,
           "ladder_note": "每档都在同一候选集上独立搜索；L1/L2 单独都能过的对数说明"
                          "卡点不是『同族』也不是『独特』，而是『同族的那句恰好不含私密词』",
           "rejection_reasons": dict(why), "family_distribution": dict(famdist),
           "median_min_residual_grams": med,
           "pool_expansion_estimate": {
               "legal_pool_before_caps": legal_pool,
               "assumption": "整池同分布（本探针的 100 对就是从这池里按同 seed 取的）",
               "expected_L3_pairs": round(ladder["L3 + 同话题族且私密词（目标）"] / max(n_cand, 1)
                                         * legal_pool),
               "expected_L1_pairs": round(ladder["L1 + 同话题族"] / max(n_cand, 1) * legal_pool),
               "cost": "换角色对 ⇒ 检索通道 21 条不再可比，必须整通道重出"},
           "registered_bands": {"ge_90": "直接建 100×5", "80_89": "N<500 并如实报缺失",
                               "lt_80": "回来找用户"},
           "decision": band,
           "caveats": [
               "话题族是词表分类，不是真语义聚类：一条句子命中多族时取第一个族，"
               "落地版要按族打分而不是取首个",
               "私密判据是词面命中，会漏掉不含这些词的真私密、也会误收假私密"
               "（v1 教训：3000 字截断的上下文里词面≠语义）。落地版要加盲子代理成对标注，"
               "按 `privacy_label_pilot` 的做法量标注一致率",
               "来源独占只保证『这句话出自谁的块』，不保证『这句话在正典里是私密的』——"
               "正典句可能本就是公开设定，需要第二步筛",
               "本探针固定 100 对 ⇒ 检索通道 21 条读数可比；若为凑数换角色对，"
               "检索通道必须一起重出"],
           "items": rows}
    OUT_JSON.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    L = ["# R5bis 覆盖率探针：100 对里有几对能配出「同族 + 独占来源 + 逐对独特 + 带私密词」",
         "",
         f"- 判据四条与分档线**跑前已登记**在脚本头部（唯一变量是配对搜索，不改判据）。",
         f"- 结果：**{n_ok}/100 可用（{n_ok}%）** ⇒ 走「{band}」这一档。",
         f"- 被拒原因分布：{dict(why)}",
         f"- 两侧都有候选的对数：**{n_cand}/100**（{len(pairs) - n_cand} 对连句子都挑不出来）",
         "",
         "## 判据阶梯：哪一条最贵（每档在同一候选集上独立搜索）",
         "",
         "| 档位 | 可用对数（/100） |",
         "|--|--|"]
    for k in LADDER:
        L.append(f"| {k} | **{ladder[k]}** |")
    L += ["",
          f"> 读数：卡点不在「逐对独特」（L0 = {ladder['L0 只要求逐对独特']}），"
          f"也不全在「同话题族」（L1 = {ladder['L1 + 同话题族']}），"
          f"而是**同族的那句恰好不带私密词**（L3 = {n_ok}）。"
          "私密词表是词面判据，词面≠语义（v1 的 3000 字截断教训），"
          "所以这一档的缺口应当用**盲子代理语义标注**去补，而不是把词表调松。",
          "",
          f"## 若换成整池（{legal_pool} 对）",
          f"- 假设整池同分布 ⇒ L3 期望约 **{res['pool_expansion_estimate']['expected_L3_pairs']} 对**、"
          f"L1 期望约 **{res['pool_expansion_estimate']['expected_L1_pairs']} 对**；",
          "- 代价：换角色对后检索通道的 21 条不再可比，**必须整通道重出**（这也是"
          "R5bis 本来就要重跑的一部分）。",
          "",
          f"- 话题族分布：{dict(famdist)}",
          f"- 两侧残差独特 gram 的较小值，中位 **{med}**（现行四模板版是 0）",
          "",
          "## 抽样 12 对（看句子本身像不像「只有这一对才有的私密」）", "",
          "| A | B | 族 | A 的事实 | B 的事实 | resid A/B |", "|--|--|--|--|--|--|"]
    for r in rows[:12]:
        L.append(f"| {r['a']} | {r['b']} | {r['family']} | {r['a_fact']} | {r['b_fact']} | "
                 f"{r['resid_a']}/{r['resid_b']} |")
    L += ["", "## 四条注意事项", ""] + [f"{i}. {c}" for i, c in enumerate(res["caveats"], 1)]
    OUT_MD.write_text("\n".join(L) + "\n", encoding="utf-8")

    print(f"[OK] 可用 {n_ok}/100（{n_ok}%）→ 档：{band}")
    print(f"     拒因 {dict(why)}")
    print(f"     族分布 {dict(famdist)}｜resid 中位 {med}")
    print(f"     → {OUT_JSON.name} / {OUT_MD.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
