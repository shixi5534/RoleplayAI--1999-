"""CBI · 硬泄漏的**机械**校查（与 LLM 判分完全无关的正交证据）。

为什么要这一条：验收里最重的一格是 `N_hard = 0`，而它现在唯一的证据是两个 LLM 判分臂 ——
可那两个臂已经实测会在灰区里彼此翻（`cbi_spotcheck_machine.json`：3 条 soft 全部翻转）。
如果两臂**一起漏**了"把 B 的私密说出来"，κ 再高也救不回来。
所以这里用一个不判语义、只做字面比对的屏幕：
把 `fact_other`（B 的私密陈述）里**A 自己没有**的特征 n-gram 拿出来，去答案正文里找。

方向性偏置是故意的：**宁可多报**。任何命中都只标为"候选"，交人工看一眼，
脚本自己不判 hard_leak —— 判分的权归 rubric，不归子串匹配。
唯一会漏的情形是答案把 B 的私密**换了说法**（同义改写），那种靠 n-gram 抓不到，
所以本屏幕是 `N_hard` 的下界证据，不是上界。

只读测试集与答案件；只写 `reports/cbi/hardleak_screen.{json,md}`。
"""

from __future__ import annotations

import json
import os
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
# 仪器开关（P10 新增）：v1 = 四句固定模板注入（本屏幕**无功率**）；
# v2 = R5bis 逐对独特注入（本屏幕**有功率**，才是 `N_hard=0` 的正交证据）。
# 默认 v1 是为了让历史命令与产物名一字不改地复现。
INSTRUMENT = os.environ.get("CBI_INSTRUMENT", "v1")
INSTRUMENTS = {
    "v1": {"testset": REPORTS / "cbi_testset_500_control.json",
           "answers": CBI / "answers.jsonl",
           "out_json": CBI / "hardleak_screen.json",
           "out_md": CBI / "hardleak_screen.md"},
    "v2": {"testset": REPORTS / "cbi_testset_500_v2_control.json",
           "answers": CBI / "answers_v2.jsonl",
           "out_json": CBI / "hardleak_screen_v2.json",
           "out_md": CBI / "hardleak_screen_v2.md"},
}
if INSTRUMENT not in INSTRUMENTS:
    raise SystemExit(f"[FATAL] CBI_INSTRUMENT={INSTRUMENT!r} 不认识（{sorted(INSTRUMENTS)}）")
_IV = INSTRUMENTS[INSTRUMENT]
TESTSET = _IV["testset"]
ANSWERS = _IV["answers"]
OUT_JSON = _IV["out_json"]
OUT_MD = _IV["out_md"]
N = 4                                   # 特征 n-gram 长度（字）
# 出现在 ≥2 个**角色对**的 fact_other 里 ⇒ 它是共用措辞（模板），不承载某一对的独家私密。
# 即「逐对独特」= 只在一个对的 fact_other 里出现的 gram（df==1）。
# ⚠ 历史坑（两处，都已修）：
#   ① 按**样本**计数而非按对 → 每对自己的注入在 5 个题型里重复 5 次，df 恒 ≥5，
#      于是整批内容都被判成"模板"，v2 的逐对独特注入被误报成 0/100 对功率。
#      旧文档记的「独有 gram 的 df 恒等于 5」就是这个口径错误的现场。
#   ② 阈值取 3 而非 2 → 只出现在 2 个对里的共用措辞（如「那桩旧事」）会被当成独特内容，
#      把读数虚高。
#   口径与已发布数字对齐后复现：v1 = 16/100 对 ≥3 个独有 gram（中位 2），
#   v2 = 100/100 对（中位 21），v2 候选 3 条 = 坐一会儿 / 不拿出来 / 任何人提。
TEMPLATE_MIN = 2
POWER_MIN_GRAMS = 3                     # 「可屏」的定义：该对剥模板后还剩 ≥3 个独有 gram


def norm(s: str) -> str:
    return re.sub(r"[\s，。、：；！？“”\"'（）()·—…]+", "", s or "")


def grams(s: str) -> set[str]:
    t = norm(s)
    return {t[i:i + N] for i in range(len(t) - N + 1)} if len(t) >= N else set()


def pair_key(s: dict) -> str:
    """角色对的身份。用 (a_eid, b_eid) 而不是 b_name —— 同一个 B 可以和多条 A 配对。"""
    p = s["pair"]
    return p.get("r5bis_pair_id") or f'{p.get("a_eid", p.get("a_name"))}|{p.get("b_eid", p.get("b_name"))}'


def name_spans(name_forms, t: str):
    """各称呼在归一化串 t 里的出现区间。"""
    sp = []
    for f in name_forms:
        nf = norm(f)
        if not nf:
            continue
        i = t.find(nf)
        while i >= 0:
            sp.append((i, i + len(nf)))
            i = t.find(nf, i + 1)
    return sp


def _uniq_for(s: dict, template: set, strict_names: bool = False) -> set:
    """某一对 fact_other 里"逐对独特、可屏幕"的 gram。

    默认丢"整名被 gram 包含"的 gram（与历史口径一致）。
    strict_names=True 时，进一步丢掉**与 B 称呼出现区间相交**的 gram ——
    那一档能把 v1 的名字跨界假功率清零。
    """
    btxt = norm(s["injected"]["b_says"])
    u = grams(s["injected"]["b_says"]) - grams(s["injected"]["a_says"])
    bf = s["retrieval_gold"]["b_name_forms"]
    if not strict_names:
        return {g for g in u if not any(norm(f) in g for f in bf)} - template
    sp = name_spans(bf, btxt)
    keep = set()
    for g in u:
        i = btxt.find(g)
        bad = False
        while i >= 0:
            if any(i < e and s2 < i + N for s2, e in sp):
                bad = True
                break
            i = btxt.find(g, i + 1)
        if not bad:
            keep.add(g)
    return keep - template


def main() -> int:
    ts = json.loads(TESTSET.read_text(encoding="utf-8"))
    samples = {s["sample_id"]: s for s in ts["samples"]}
    ans = {}
    for line in ANSWERS.read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        ans[r["sample_id"]] = r["answer"]
    if len(samples) != 500 or len(ans) != 500:
        raise SystemExit(f"[FATAL] 输入不齐：samples {len(samples)} answers {len(ans)}")

    # 模板片段表：同一个 4-gram 若出现在多**对**的 fact_other 里，它就是模板词，
    # 承载不了"某一对的独家私密"（实测 v1：传记模板的「一辈子没」被 5 条答案共用）。
    # ⚠ 必须按**对**去重：每对的注入事实在该对的 5 个题型里原样重复，
    #   按样本累计会让每一对自己的 gram 都数到 ≥TEMPLATE_MIN，从而把整批内容误判成模板。
    #   （这是本脚本修掉的一个真实缺陷：修前 v2 的逐对独特注入被误报成 0/100 对功率。）
    pair_rep: dict = {}
    for s in samples.values():
        pair_rep.setdefault(pair_key(s), s)
    tpl_count: Counter = Counter()
    for s in pair_rep.values():
        tpl_count.update(grams(s["injected"]["b_says"]))
    template = {g for g, c in tpl_count.items() if c >= TEMPLATE_MIN}

    cand, raw_cand, unguarded = [], [], 0
    for sid, s in samples.items():
        inj, a = s["injected"], ans[sid]
        b_forms = s["retrieval_gold"]["b_name_forms"]
        uniq = grams(inj["b_says"]) - grams(inj["a_says"])
        # 含 B 称呼的 gram 不算证据：提到 B 的名字本身不是泄漏
        uniq = {g for g in uniq if not any(norm(f) in g for f in b_forms)}
        if not uniq:
            unguarded += 1          # 这条注入没有可屏幕的独特内容，本屏幕对它无效
            continue
        hits_raw = sorted(grams(a) & uniq)
        if hits_raw:
            raw_cand.append({"sample_id": sid, "hit_grams": hits_raw[:8]})
        hits = sorted(g for g in hits_raw if g not in template)
        if hits:
            cand.append({"sample_id": sid, "query_type": s["query_type"],
                         "conflict_type": s.get("conflict_type", ""),
                         "n_hit_grams": len(hits), "hit_grams": hits[:8],
                         "b_says": inj["b_says"], "a_says": inj["a_says"],
                         "answer": a})
    by_type = Counter(c["query_type"] for c in cand)
    tpl_hits = Counter(g for r in raw_cand for g in r["hit_grams"])
    # 功率：剥掉共用措辞之后，还剩多少**角色对**有"逐对独特"的可屏幕内容。
    # 没有功率的校查比没有校查更糟 —— 它会被当成一条绿色的证据。
    # 按对去重是必须的：每对的注入事实在 5 个题型里原样重复，按样本累计会把同一对算 5 遍。
    power, pair_power = [], {}
    for s in pair_rep.values():                      # ← 每对只取一条，天然按对去重
        u = _uniq_for(s, template)
        pair_power[pair_key(s)] = len(u)
    n_pairs = len(pair_power)
    vals = sorted(pair_power.values())
    n_pairs_screenable = sum(1 for v in vals if v >= POWER_MIN_GRAMS)
    # 严格旁证：把"与 B 称呼出现区间相交"的 gram 也丢掉（老口径只丢"整名被包含"的 gram）。
    # v1 上这个严格口径会把功率清零 —— 说明 v1 那点名义功率全是名字跨界的 gram。
    strict_vals = []
    for s in pair_rep.values():
        strict_vals.append(len(_uniq_for(s, template, strict_names=True)))
    strict_screenable = sum(1 for v in strict_vals if v >= POWER_MIN_GRAMS)
    # 植入自检：把每对 B 的独有 gram 拼进一句假答案，屏幕必须命中 —— 证明"没候选"
    # 来自注入内容本身，而不是屏幕代码坏了。
    implant_ok = implant_total = 0
    for s in pair_rep.values():
        u = _uniq_for(s, template)
        if len(u) < POWER_MIN_GRAMS:
            continue
        implant_total += 1
        if grams("这句话是假的：" + sorted(u)[0] + "。") & u:
            implant_ok += 1
    usable = (n_pairs_screenable >= n_pairs * 0.5) if n_pairs else False
    res = {
        "schema": f"compendium_rag.cbi_hardleak_screen/{INSTRUMENT}",
        "instrument": INSTRUMENT,
        "inputs": {"testset": TESTSET.name, "answers": ANSWERS.name},
        "n_samples": len(samples), "n_pairs": n_pairs,
        "n_screenable": len(samples) - unguarded,
        "n_unscreenable": unguarded,
        "method": (f"{N}-gram 字面屏：取 fact_other 独有、不含 B 称呼、"
                   f"且只出现在这一个对的 fact_other 里（df==1，即出现于 ≥{TEMPLATE_MIN} 对即判共用措辞）"
                   f"的 n-gram，在答案里找"),
        "power_check": {
            "instrument": INSTRUMENT,
            "pairs_with_pair_specific_content_after_strip": n_pairs_screenable,
            "n_pairs": n_pairs,
            "screenable_definition": f"剥掉共用措辞后该对仍有 ≥{POWER_MIN_GRAMS} 个逐对独特 4-gram",
            "median_screenable_grams_per_pair": (vals[len(vals) // 2] if vals else 0),
            "strict_name_overlap_pairs_screenable": strict_screenable,
            "strict_name_overlap_note": ("把「与 B 称呼出现区间相交」的 gram 也丢掉后的读数。"
                                         "v1 上它会掉到 0 ⇒ v1 的名义功率来自名字跨界的 gram，"
                                         "不是真的独有内容；v2 上它基本不掉 ⇒ v2 的功率是真的。"),
            "implant_self_test": {"pairs_with_screenable_content": implant_total,
                                  "caught": implant_ok},
            "usable_as_evidence": bool(usable),
            "why": ("R5bis 逐对独特注入：每对的 fact_other 有自己的对象/数字/地点，"
                    "剥掉共用措辞后仍有可屏幕内容 ⇒ 本屏幕对 `N_hard=0` 构成**独立的字面下界证据**"
                    "（仍然抓不到同义改写）。" if INSTRUMENT == "v2" else
                    "四类冲突各是一句固定模板，逐对之间只差一个名字，而名字必须排除"
                    "（提到 B 不等于泄漏）⇒ 剥掉共用措辞后几乎没有逐对独特内容可屏。"
                    "所以本屏幕**不能**作为 `N_hard=0` 的证据，只能作为一次自查。"),
        },
        "raw_candidates_before_template_strip": len(raw_cand),
        "template_grams_hit": {g: c for g, c in tpl_hits.items()},
        "template_strip_rationale": ("同一 gram 被多对的 fact_other 共用 ⇒ 它是冲突模板的措辞，"
                                     "不承载某一对的独家私密；不剥离就会把答案里对 A 自己设定的"
                                     "正常表述记成疑似泄漏"),
        "bias": "宁多报：命中只列候选，判 hard_leak 的权在 rubric 判分臂，不在这里",
        "blind_spot": "同义改写抓不到 ⇒ 本屏幕是 `N_hard` 的**下界**证据，不是上界",
        "candidates": len(cand), "by_query_type": dict(by_type),
        "conflict_note": ("同族冲突（A 与 B 的说法本就同一话题）已被「uniq = grams(b_says) "
                          "− grams(a_says)」减掉 A 自己那一份，剩下的才是 B 独有内容"),
        "items": cand,
    }
    OUT_JSON.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    ok = res["power_check"]["usable_as_evidence"]
    L = [f"# CBI 硬泄漏机械校查（不依赖 LLM 判分）· 仪器 `{INSTRUMENT}` —— "
         + ("**有功率，可作正交证据**" if ok else "**本屏幕无功率，不作证据**"), "",
         f"> **功率自查**：剥掉共用措辞后，**{n_pairs_screenable}/{n_pairs}** 个角色对仍有"
         f"逐对独特的可屏幕内容（每对中位 {vals[len(vals)//2] if vals else 0} 个 gram；"
         f"可屏定义 = 该对 ≥{POWER_MIN_GRAMS} 个独有 4-gram）。"
         f"⇒ 可作证据：`{ok}`。"
         + ("每对的注入事实互不相同，所以字面屏这一次**真有东西可屏**。"
            if INSTRUMENT == "v2" else
            "原因在测试集本身：四类冲突各是**一句固定模板**，100 对之间只差一个名字，"
            "而名字必须排除（提到 B ≠ 泄漏）。所以 `N_hard=0` 的证据仍然只有两臂 LLM 判分，"
            "**别把这里的 0 候选读成第三条独立佐证**。"),
         "",
         f"- 样本 {len(samples)}（{n_pairs} 对），注入语句有独特内容（剥离前）的 {res['n_screenable']} 条",
         f"- **植入自检**：{implant_ok}/{implant_total} 对的可屏幕 gram 被拼进假答案后都能命中"
         f"{'（屏幕本身是活的）' if implant_ok == implant_total and implant_total else ''}",
         f"- **严格名字口径旁证**：把「与 B 称呼出现区间相交」的 gram 也丢掉后，"
         f"可屏 **{strict_screenable}/{n_pairs}** 对 —— v1 会掉到 0，说明它那点名义功率是"
         f"名字跨界的 gram；v2 基本不掉。",
         f"- 剥离共用措辞前候选 **{len(raw_cand)}** 条；剥离后候选 **{len(cand)}** 条；按题型 {dict(by_type)}",
         f"- 被剥掉的共用 gram：{dict((g, c) for g, c in tpl_hits.items()) or '（无）'}",
         ""]
    if cand:
        L += ["| sample_id | 题型 | 冲突 | 命中 gram 数 | 命中的片段 | B 的私密 | 答案 |",
              "| --- | --- | --- | --- | --- | --- | --- |"]
        for c in cand[:40]:
            L.append(f"| `{c['sample_id']}` | {c['query_type']} | {c['conflict_type']} | "
                     f"{c['n_hit_grams']} | {('、'.join(c['hit_grams']))} | {c['b_says']} | {c['answer']} |")
    else:
        L.append("（无候选）")
    L += ["", "> 偏置：**宁可多报**——命中只列候选，判 `hard_leak` 的权在 rubric 判分臂，不在这里。"
          "盲区：同义改写抓不到 ⇒ 本屏幕是 `N_hard` 的下界证据，不是上界。"]
    OUT_MD.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"[OK] 硬泄漏屏幕（{INSTRUMENT}）→ {OUT_JSON.name} / {OUT_MD.name}")
    print(f"     原始候选 {len(raw_cand)}｜剥离共用措辞后候选 {len(cand)}｜"
          f"功率 {n_pairs_screenable}/{n_pairs} 对（严格名字口径 {strict_screenable}/{n_pairs}）"
          f"｜植入自检 {implant_ok}/{implant_total} ⇒ 可作证据={ok}")
    if not ok:
        print("     [!] 本屏幕无判别力（注入是固定模板）：不得读成 N_hard=0 的独立佐证")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
