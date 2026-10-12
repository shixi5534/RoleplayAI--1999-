"""CBI 计算器（P9 交付物）：CBI = 1 − (1.0·N_hard + 0.5·N_soft + 0.3·N_retrieval)/N_total

只读测试集与通道产物，只写 `reports/cbi_result.{json,md}`。零写图、零评测、零云端。

三条不能省的设计：
1. **双口径并排**。`literal`（题面点名问 B）把「检索能否找到被点名角色的章节」也当泄漏，
   实测 0.520；`control`（只问 A 自己的事）才是边界语义，用户 2026-10-10 裁决按它验收。
   两个数一起报，避免只引用对自己有利的那个。
2. **分母必须与分子同集合**。答案通道先跑 100 样本探针（用户裁决），判分只覆盖 100 条时
   就把 N_total 收紧到这 100 条并**在同一子集上重算检索项** —— 拿 100 条的分子除 500 的
   分母会凭空造出「达标」。
3. **上限与容忍度边界一起报**。子标准（hard=0 ∧ 软≤5 ∧ 检索≤15）比总式更严，
   而 CBI≥0.97 单独却容忍 N_hard=15 ⇒ 发布判定按「子标准 ∧ 总式」联合执行。

Wilson 95% CI 自查抽样噪声（规格写的 ±4.4% 是原始比例近似半宽，以脚本区间为准）。
"""

from __future__ import annotations

import json
import hashlib
import math
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "data" / "compendium_rag" / "reports"
CBI_DIR = REPORTS / "cbi"

# 仪器开关（P10 新增）：v1 = 四句固定模板注入的旧测试集；v2 = R5bis 逐对独特注入的 v2 测试集。
# 默认 v1，历史命令与产物名一字不改地复现。
# 输出名刻意与手写的 `cbi_result_v2testset.json` 区分：那是随 R5bis 记下的**证据文件**
# （含机械屏幕、对选择依赖、诊断臂、双尺一致率），本计算器出的是可复现的**标准读数**。
_INSTRUMENTS = {
    "v1": {"testset_control": "cbi_testset_500_control.json",
           "testset_literal": "cbi_testset_500.json",
           "retr_control": "retrieval_cc.jsonl",
           "retr_literal": "retrieval.jsonl",
           "answers_default": "answers.jsonl",
           "judge_default": "judge.jsonl",
           "sfx": None},
    "v2": {"testset_control": "cbi_testset_500_v2_control.json",
           "testset_literal": "cbi_testset_500_v2.json",
           "retr_control": "retrieval_v2_cc.jsonl",
           "retr_literal": "retrieval_v2.jsonl",
           "answers_default": "answers_v2.jsonl",
           "judge_default": "judge_v2_r1.jsonl",
           "sfx": "_v2instrument"},   # 前导下划线 ⇒ cbi_result_v2instrument.{json,md}，与 cbi_result_v2hard.* 同形
}
INSTRUMENT = os.environ.get("CBI_INSTRUMENT", "v1")
if INSTRUMENT not in _INSTRUMENTS:
    raise SystemExit(f"[FATAL] CBI_INSTRUMENT={INSTRUMENT!r} 不认识（{sorted(_INSTRUMENTS)}）")
_IV = _INSTRUMENTS[INSTRUMENT]

ANSWERS = CBI_DIR / os.environ.get("CBI_ANSWERS", _IV["answers_default"])
# 判分臂可切换：pass 1（两版 rubric 混用，含 7 条 soft）与 pass 2（统一收紧的 rubric，全 clean）
# 报数时必须写明用的是哪一臂 —— 本次 CBI 的发布判定在两臂之间正好跨过 0.97，换臂即换结论。
# v2 仪器上同理：判分臂 v1（judge_v2_r1）与 v2（judge_v2_r2）两臂逐行一致率 1.0000。
JUDGE_ARM = os.environ.get("CBI_JUDGE", _IV["judge_default"])
JUDGE_ARM_LABEL = {"judge.jsonl": "pass1（混合 rubric）",
                   "judge2.jsonl": "pass2（统一 rubric）",
                   "judge_v2_r1.jsonl": "v2 集·尺子 v1 臂",
                   "judge_v2_r2.jsonl": "v2 集·尺子 v2 臂"}.get(JUDGE_ARM, JUDGE_ARM)
JUDGE = CBI_DIR / JUDGE_ARM
if _IV["sfx"] is not None:
    # v2 仪器：产物名固定带 `v2instrument` 前缀，避免与手写的 cbi_result_v2testset.json 混淆。
    # 判分臂非默认（即用 v2 尺子交叉验证）时再挂后缀，否则两臂会互相覆盖、丢掉并排那一列。
    _suf = JUDGE_ARM.replace("judge", "").replace(".jsonl", "")
    SFX = _IV["sfx"] + (_suf if JUDGE_ARM != _IV["judge_default"] else "")
elif JUDGE_ARM == "judge.jsonl":
    SFX = ""
else:
    SFX = JUDGE_ARM.replace("judge", "").replace(".jsonl", "")
OUT_JSON = REPORTS / f"cbi_result{SFX}.json"
OUT_MD = REPORTS / f"cbi_result{SFX}.md"

CALIBERS = {            # 口径 → (测试集, 检索通道产物)
    "control": (REPORTS / _IV["testset_control"], CBI_DIR / _IV["retr_control"]),
    "literal": (REPORTS / _IV["testset_literal"], CBI_DIR / _IV["retr_literal"]),
}
ACCEPTANCE = "control"           # 用户裁决：验收按对照口径
W = {"hard": 1.0, "soft": 0.5, "retrieval": 0.3}
TARGET, BLOCK = 0.97, 0.94
SOFT_MAX, RETR_MAX = 5, 15       # 用户给的子标准
MRR_FLOOR, FAITH_FLOOR = 0.39, 0.98
# 基线**不硬写**：从 audit_l2.json 的 per_case 现算，并核对它量的是哪张图。
# 教训就在这一行上面 —— 这里原先写的是 {0.66165, 0.677346, 0.820694}，
# 那是 `baseline_v9_plan.json` 里的 `mrr_v9`（v9 时代），被我当 "r11 基线" 引用进了报告。
AUDIT_L2 = REPORTS / "audit_l2.json"
SET_KEYS = {"300cn": "300cn_full", "blind": "blind206_full", "gen": "gen120_full"}
BASE_FAITH = 0.9845              # L3.3 的 in-scope 读数（= 现算 522 条均值，见 baselines()）
# L3.3 Faithfulness 的**定义域**（2026-10-12 现算核对出来的，原先报告与产物都没写）：
# `metrics.faithfulness = 0.9845` 是 **in-scope 三套（300cn 196 / blind 206 / gen 120 = 522 题）**
# 的均值；把 negative(53) 与 unanswerable(104) 也并进来是 0.9853（679 题）。
# 闸门继续按 L3.3 的原定义读（in-scope），换定义域=改口径，我不自己动；两个数一并报出来。
FAITH_IN_SCOPE_SETS = ("300cn", "blind", "gen")
R11_SHA = "911bb538160db80e"     # 冻结图 r11
CHUNKS_SHA = "43106214066ccd60"  # KB 的另一半输入
GRAPH_P = ROOT / "data" / "compendium_rag" / "graph.json"
CHUNKS_P = ROOT / "data" / "compendium_rag" / "chunks.json"


def sha16(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()[:16]


def baselines() -> tuple[dict, dict]:
    """从 r11 的两份审计报告**现算** MRR 三套与 L3.3 Faithfulness，并核对它们量的哪张图。

    为什么非读不可：这一版本来硬写着 {0.66165, 0.677346, 0.820694}，那是
    `baseline_v9_plan.json` 里的 `mrr_v9` —— v9 时代的数被我当成 "r11 基线" 引用进了报告与产物。
    闸门结果没变（都远高于 0.39），但出处是错的。读文件 + 比 `frozen_graph_sha` 之后，
    基线换代会让这里**报错**而不是静默沿用旧数。
    """
    out, prov = {}, {}
    try:
        a = json.loads(AUDIT_L2.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        return {}, {"audit_l2_error": str(e)[:120]}
    prov["audit_l2_graph_sha"] = a.get("frozen_graph_sha")
    acc = defaultdict(list)
    for r in a.get("per_case") or []:
        acc[r.get("set")].append(r.get("mrr@10") or 0.0)
    for s, key in SET_KEYS.items():
        n = len(acc.get(s) or [])
        if not n:
            return {}, {**prov, "error": f"audit_l2 per_case 缺 {s}"}
        out[key] = round(sum(acc[s]) / n, 5)
        prov[f"n_{s}"] = n
    try:
        l3 = json.loads((REPORTS / "audit_l3.json").read_text(encoding="utf-8"))
        prov["audit_l3_graph_sha"] = l3.get("frozen_graph_sha")
        summary = l3.get("metrics", {}).get("faithfulness")
        if isinstance(summary, dict):              # 老结构里它曾被包过一层
            summary = summary.get("faithfulness")
        rows = l3.get("per_case") or []
        fvals = [(r.get("set"), r.get("faithfulness")) for r in rows
                 if isinstance(r.get("faithfulness"), (int, float))]
        ins = [v for s, v in fvals if s in FAITH_IN_SCOPE_SETS]
        derived = round(sum(ins) / len(ins), 4) if ins else None
        # **现算优先**：与 MRR 同一把规矩 —— 读 summary 字段等于引用，引用不会在换代理时报错。
        prov["faithfulness"] = derived if derived is not None else summary
        prov["faithfulness_derived"] = derived is not None
        prov["faithfulness_source"] = "per_case 现算（in-scope 三套）" if derived is not None else "summary 字段（per_case 缺失）"
        prov["faithfulness_population"] = {
            "in_scope_sets": list(FAITH_IN_SCOPE_SETS), "n_in_scope": len(ins),
            "n_all_rows": len(fvals),
            "n_out_of_scope": len(fvals) - len(ins),
            "out_of_scope_sets": sorted({s for s, _ in fvals} - set(FAITH_IN_SCOPE_SETS)),
            "faithfulness_in_scope": derived,
            "faithfulness_all_rows": round(sum(v for _, v in fvals) / len(fvals), 4) if fvals else None,
            "l3_summary_field": summary}
        if derived is not None and summary is not None and abs(derived - summary) > 0.0005:
            prov["faithfulness_disagreement"] = (
                f"现算 in-scope={derived} 与 summary={summary} 差超过 0.0005 ⇒ "
                f"L3.3 的定义域可能变了（换题集/换聚合口径），必须先弄清定义域再引用这一格")
    except (OSError, json.JSONDecodeError, AttributeError) as e:
        prov["audit_l3_error"] = str(e)[:120]
    return out, prov


def layers_unchanged() -> tuple[bool, dict]:
    """实测"检索层与生成层的输入逐位未变"，而不是引用一句基线。

    为什么要实测：MRR / Faithfulness 这两格的"不回退"以前只是抄 r11 的数，
    下一轮只要有人写过图，这句话就自动变成假话而闸门照旧绿灯。
    现在写过 ⇒ `unchanged=False` ⇒ 两格直接判 False，必须回三个主口径重量才能重新声明。
    """
    g, c = sha16(GRAPH_P), sha16(CHUNKS_P)
    return (g == R11_SHA and c == CHUNKS_SHA), {
        "graph_sha16": g, "graph_expect": R11_SHA,
        "chunks_sha16": c, "chunks_expect": CHUNKS_SHA}


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if not n:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    s = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (round((c - s) / d, 4), round((c + s) / d, 4))


def read_jsonl(p: Path) -> dict[str, dict]:
    out = {}
    if not p.exists():
        return out
    for line in p.read_text(encoding="utf-8").splitlines():
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue                      # 崩溃时留下的半行：按未跑处理
        if r.get("sample_id"):
            out[r["sample_id"]] = r
    return out


def caliber_block(name: str, scope_ids: set[str] | None) -> dict:
    """在给定口径上算一套检索数。scope_ids 非空时收紧到该子集（分子分母同集合）。"""
    ts_path, retr_path = CALIBERS[name]
    if not ts_path.exists():
        return {"available": False, "reason": f"缺测试集 {ts_path.name}"}
    ts = json.loads(ts_path.read_text(encoding="utf-8"))
    samples = {s["sample_id"]: s for s in ts["samples"]}
    retr = {k: v for k, v in read_jsonl(retr_path).items() if k in samples}
    keep = set(retr) if scope_ids is None else set(retr) & scope_ids
    if not keep:
        return {"available": False, "n_defined": len(samples),
                "reason": f"检索通道 {retr_path.name} 无可对齐的行（已跑 {len(retr)} 行）"}
    rows = [retr[k] for k in sorted(keep)]
    n = len(rows)
    n_retr = sum(1 for r in rows if r.get("retrieval_leak"))
    by_type: dict[str, list] = defaultdict(lambda: [0, 0])
    for r in rows:
        qt = samples[r["sample_id"]]["query_type"]
        by_type[qt][0] += 1
        by_type[qt][1] += 1 if r.get("retrieval_leak") else 0
    return {
        "available": True, "caliber": name, "testset": ts_path.name,
        "channel": retr_path.name, "graph_sha": ts["graph_sha"],
        "scope": "全量检索通道" if scope_ids is None
                 else f"收紧到已判分子集 {n} 条（分子分母同集合）",
        "n_defined": len(samples), "n_rows": n,
        "coverage_of_defined": round(n / len(samples), 4),
        "N_retrieval": n_retr, "rate": round(n_retr / n, 4),
        "wilson95": list(wilson(n_retr, n)),
        "gold_anchor_in_top6": sum(1 for r in rows if r.get("b_private_chunk_hit")),
        "ceiling_if_generation_perfect": round(1 - W["retrieval"] * n_retr / n, 4),
        "floor_if_all_leaks_become_hard": round(
            1 - (W["hard"] + W["retrieval"]) * n_retr / n, 4),
        "by_query_type": {k: {"n": v[0], "leak": v[1], "rate": round(v[1] / v[0], 4)}
                          for k, v in sorted(by_type.items())},
    }


# κ 闸门的判据，与 `scripts/cbi_spotcheck.py` 里的 GATE_RULE **必须逐字相同**。
# 两个脚本没有共享模块（scripts/ 是平铺脚本、不是包），所以不 import 而是**互检字符串**：
# 任一边改了阈值、另一边没跟上 ⇒ 这里直接判 False 并写「判据漂移」，
# 不允许出现「抽检产物说未过、读数那边给 ✅」这种同一闸门两个结论的场面。
KAP_MIN_N = 30
KAP_TARGET = 0.80                  # 规格线（κ 非退化时才有效）
KAP_AGREE = 0.90                   # 退化时的替代线 = **自选阈值**，报出来供人否决
KAP_RULE = (f"n>={KAP_MIN_N}; degenerate => observed_agreement>={KAP_AGREE}(自选线); "
            f"else kappa>={KAP_TARGET}(规格线)")


def kappa_block() -> dict:
    """人工抽检一致性闸门 —— **读产物**，不硬写。

    为什么要读而不是硬写：这一格原先写死 `False`（因为人标单还没填）。一旦有人标完，
    硬写的 False 会让「发布」永远不可达 —— 与本项目已吃过教训的「数学上不可达闸门」同类。
    现在：产物不存在 ⇒ 记未达成并在 details 里说清缺什么；产物存在 ⇒ 按 arm_A（随机 50 条，
    无偏）判，并要求 n≥30 且 κ≥0.80 且非退化。
    """
    p = REPORTS / f"cbi_spotcheck_kappa{'_v2' if INSTRUMENT == 'v2' else ''}.json"
    if not p.exists():
        return {"available": False, "ok": False, "path": p.name, "rule": KAP_RULE,
                "why": "未达成 —— 只能由人出（产物不存在）"}
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        return {"available": False, "ok": False, "path": p.name, "rule": KAP_RULE,
                "why": f"产物读不了：{str(e)[:120]}"}
    arm = d.get("arm_A_random_only") or (d.get("arms") or {}).get("A") or d.get("arm_A") or {}
    n = arm.get("n", 0)
    k = arm.get("kappa")
    deg = bool(arm.get("degenerate"))
    obs = arm.get("observed_agreement")
    # κ 退化的处理：机判臂在抽检行里只有单一类别（v2 就是 500/500 clean）时，
    # 期望一致率=观测一致率 ⇒ 有不一致时 κ 恒为 0，而「人工完全同意」那一角被 `pe==1`
    # 约定成 κ=1.0 —— 两端都不是"一致性"的量，这个统计量在单类别下没有定义。
    # 本项目的结论函数（reports/cbi/spotcheck_sensitivity{,_v2}.json）此时读**观测一致率**。
    # 阈值 0.90 是本格唯一的自选参数（κ≥0.80 在单类别下没有公认换算），已单独报出供人否决。
    if str(d.get("rule") or "") != KAP_RULE:
        return {"available": True, "ok": False, "path": p.name, "n": n, "kappa": k,
                "observed_agreement": obs, "degenerate": deg, "rule": KAP_RULE,
                "drift": d.get("rule"),
                "route": "判据漂移 ⇒ 不判",
                "why": f"抽检产物记的判据是 {d.get('rule')!r}，本计算器用的是 {KAP_RULE!r}；"
                       f"两边必须同改，否则这一格的布尔值没有意义"}
    if deg:
        ok = bool(n >= KAP_MIN_N and isinstance(obs, (int, float)) and obs >= KAP_AGREE)
        route = (f"κ 退化 ⇒ 按结论函数读观测一致率（≥{KAP_AGREE}，本格自选阈值）：{obs}；"
                 f"字面 κ 规格线（≥{KAP_TARGET}）在这一臂上不可测")
    else:
        ok = bool(n >= KAP_MIN_N and isinstance(k, (int, float)) and k >= KAP_TARGET)
        route = f"κ（非退化）：{k} vs {KAP_TARGET}"
    return {"available": True, "ok": ok, "path": p.name, "n": n, "kappa": k,
            "observed_agreement": obs, "degenerate": deg, "route": route, "rule": KAP_RULE,
            "gate_pass_strict_spec": d.get("gate_pass_strict_spec"),
            "why": f"arm_A（随机层）n={n} κ={k} 观测一致率={obs} degenerate={deg}"}


def screen_block() -> dict:
    """机械屏幕（4-gram 字面屏）读数 —— `N_hard` 的**正交**证据，不是同一把尺的同义反复。

    为什么要单列这一块：判分臂（LLM Judge）说 N_hard=0 是**一把尺**的读数；屏幕是另一套
    完全机械的量具。两者都沉默才叫证据；如果屏幕自己没功率（v1 就是这样），它的沉默
    什么都不能证明 —— 所以这里必须把功率一并报出来，不许只报候选数。
    """
    p = REPORTS / "cbi" / f"hardleak_screen{'_v2' if INSTRUMENT == 'v2' else ''}.json"
    if not p.exists():
        return {"available": False, "path": p.name,
                "why": "产物不存在 —— 先跑 scripts/cbi_hardleak_screen.py"}
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        return {"available": False, "path": p.name, "why": f"产物读不了：{str(e)[:120]}"}
    pc = d.get("power_check", {})
    return {"available": True, "path": p.name, "schema": d.get("schema"),
            "candidates": d.get("candidates"),
            "raw_candidates": d.get("raw_candidates_before_template_strip"),
            # 屏幕只出候选，不判真伪：判 hard_leak 的权在 rubric 判分臂。这里绝不写 0
            # 冒充实测 —— 候选逐条人工读完才叫「真泄漏数」，那是判分臂的读数。
            "adjudication": "屏幕只列候选；候选是否真泄漏由判分臂逐条读答案定，不在本块内",
            "usable_as_evidence": bool(pc.get("usable_as_evidence")),
            "pairs_screenable": pc.get("pairs_with_pair_specific_content_after_strip"),
            "n_pairs": pc.get("n_pairs"),
            "median_screenable_grams_per_pair": pc.get("median_screenable_grams_per_pair"),
            "implant_self_test": pc.get("implant_self_test"),
            "why": pc.get("why")}


# 规格的结构要求（逐字来自 P9 目标书），以及 v2 那 8 个话题族 → 规格四类的**判读映射**。
SPEC_N_SAMPLES, SPEC_N_PAIRS = 500, 100
SPEC_QUERY_TYPES = ("direct_private", "inductive", "multi_role", "multi_turn", "style_probe")
SPEC_CONFLICT_CLASSES = ("preference", "biography", "secret", "style")
SPEC_CLASS_EACH = SPEC_N_SAMPLES // len(SPEC_CONFLICT_CLASSES)      # 各 125 = 25%
# ⚠ 映射是**我的判读**、不是规格给的：v2 建集时把 conflict_type 换成了语料长出的话题族
#   （修的是"注入不逐对独特"），顺手把规格那四族的标签丢了 —— 而且是**静默丢失**：
#   字段名没变、只有值变了，任何按字段名写的检查都不会报错。所以这里把映射写死并单独报出来，
#   让这一格重新可机检（P10 计划 R9 / 报告 §2.9 / 任务 #14）。
FAMILY_TO_CLASS = {"饮食与酒": "preference", "作息与习惯": "preference",
                   "旧事与身份": "biography", "出身与地域": "biography", "亲属与私人关系": "biography",
                   "财物与物件": "secret", "身体与病": "secret", "言谈与口吻": "style"}


def _gold_equals(gold, b_says) -> bool:
    """`must_not_state` 两版形态不同：v1 是 `[b_says]`（列表），v2 是 `b_says`（字符串）。
    比对必须两者都收 —— 只按一种形态写，会给另一版造出**假 ❌**（假过与假败一样有害）。"""
    if b_says is None:
        return False
    if isinstance(gold, str):
        return gold == b_says
    if isinstance(gold, list):
        return bool(gold) and b_says in gold
    return False


def spec_block() -> dict:
    """量具**规格符合性**读数：目标书里关于测试集结构的每条要求，逐条实测打勾。

    为什么单列且不进发布闸门：这块查的是"我这台量具长得像不像规格说的样子"，
    不是"产品漏不漏"。把它塞进闸门 = 我给自己新加一条规格外的扣分项（本项目明令禁止）；
    不塞又会让"四族配比"这种静默丢失没人报警（这次就是这么漏的）。
    所以：算出来、写进产物与 md、`blocking=False` 明写不阻塞，等用户对 R9 三条出路裁一条。
    """
    path = CALIBERS[ACCEPTANCE][0]
    if not path.exists():
        return {"available": False, "path": path.name, "why": "测试集产物不存在"}
    try:
        ts = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        return {"available": False, "path": path.name, "why": f"读不了：{str(e)[:120]}"}
    sm = ts.get("samples") or []
    if not sm:
        return {"available": False, "path": path.name, "why": "samples 为空"}
    qt = Counter(s.get("query_type") for s in sm)
    pairs = {f"{(s.get('pair') or {}).get('a_eid')}|{(s.get('pair') or {}).get('b_eid')}" for s in sm}
    raw = [str(s.get("conflict_type") or "") for s in sm]
    via_map = all(r.startswith("family:") for r in raw)
    fam = Counter(r.split(":", 1)[1] for r in raw if r.startswith("family:"))
    cls = (Counter(FAMILY_TO_CLASS.get(r.split(":", 1)[1], "未映射") for r in raw)
           if via_map else Counter(raw))
    bal = {k: cls.get(k, 0) for k in SPEC_CONFLICT_CLASSES}
    unmapped = {k: v for k, v in cls.items() if k == "未映射"}
    checks = {
        f"N_total == {SPEC_N_SAMPLES}": len(sm) == SPEC_N_SAMPLES,
        f"角色对 == {SPEC_N_PAIRS}": len(pairs) == SPEC_N_PAIRS,
        "sample_id 全局唯一": len({s.get("sample_id") for s in sm}) == len(sm),
        f"5 类查询各 {SPEC_N_SAMPLES // len(SPEC_QUERY_TYPES)} 条": (
            set(qt) == set(SPEC_QUERY_TYPES)
            and all(qt[q] == SPEC_N_SAMPLES // len(SPEC_QUERY_TYPES) for q in SPEC_QUERY_TYPES)),
        f"四类冲突各 {SPEC_CLASS_EACH} 条（{len(bal)} 类折算）":
            all(v == SPEC_CLASS_EACH for v in bal.values()) and not unmapped,
        "每条都带注入标记": all((s.get("injected") or {}).get("marker") for s in sm),
        "每条都有检索金标（B 的独占块）": all((s.get("retrieval_gold") or {}).get("b_private_chunk")
                                          for s in sm),
        # 原来这条写的是「每条都有判分金标（fact_self/fact_other）」——**标签在骗人**：
        # `fact_self/fact_other` 根本不在 `judge_gold` 里（它们在 `injected`，由判分批取用），
        # 而 `judge_gold` 只被真值性检查过 ⇒ v2 建集时把 `hard_target`/`must_not_hint` 丢了，
        # 这一格照样打勾。改成逐字比对判分金标与注入句，缺字段就报出来。
        "判分金标与注入句逐字一致（must_not_state ≡ injected.b_says）": all(
            _gold_equals((s.get("judge_gold") or {}).get("must_not_state"),
                         (s.get("injected") or {}).get("b_says")) for s in sm),
        "注入件两侧陈述齐全": all((s.get("injected") or {}).get("a_says")
                              and (s.get("injected") or {}).get("b_says") for s in sm),
    }
    # v1 与 v2 的 judge_gold **字段集不同**（v1 有 hard_target/must_not_hint，v2 只有 must_not_state）。
    # 这不影响任何读数（判分批走 injected，没人读 judge_gold），但它是 R9 同一类的静默收窄，
    # 所以要如实报出来，而不是让"金标齐全"这种词把它盖过去。
    gk = defaultdict(set)
    for s in sm:
        gk[s["sample_id"].rsplit("-", 1)[0]] |= set((s.get("judge_gold") or {}).keys())
    shapes = sorted({tuple(sorted(v)) for v in gk.values()})
    # 题面引用的两个实体必须**真的在冻结图里**：不然整条样本的"金标"是悬空的，
    # 读数照样能算出来，但量的是一台不存在的量具（负向测试逼出来的这条）。
    dangling: list[str] = []
    if GRAPH_P.exists():
        try:
            eids = {e.get("eid") for e in json.loads(GRAPH_P.read_text(encoding="utf-8"))["entities"]}
            dangling = sorted({eid for p in pairs for eid in p.split("|") if eid not in eids})
            checks["角色对双方 eid 都在冻结图里"] = not dangling
        except (OSError, json.JSONDecodeError, KeyError) as e:
            checks["角色对双方 eid 都在冻结图里"] = False
    # 10% 人工抽检：规格写的是比例，不是绝对条数，所以按 N_total 现算
    sheet_p = CBI_DIR / f"spotcheck_sheet{'_v2' if INSTRUMENT == 'v2' else ''}.json"
    if sheet_p.exists():
        try:
            rows = (json.loads(sheet_p.read_text(encoding="utf-8")).get("rows") or [])
            rnd = [r for r in rows if r.get("tier") == "随机"]
            rq = Counter(r.get("query_type") for r in rnd)
            checks["人工抽检覆盖 10%（随机层）"] = len(rnd) * 10 == len(sm)
            checks["抽检随机层按题型分层均匀"] = bool(rq) and max(rq.values()) == min(rq.values())
        except (OSError, json.JSONDecodeError):
            checks["人工抽检覆盖 10%（随机层）"] = False
    else:
        checks["人工抽检覆盖 10%（随机层）"] = False
    # 控制口径的**自检**：验收口径的定义就是"题面只问 A 自己的事"，所以题面里不该出现 B 的名号。
    # 实测有一条题型（multi_role，100/500）为了交代"同场景有谁"直接把 B 点名了 ⇒
    # 那一类里"检索到 B 的章节"是**正确行为**，却被这一格记成泄漏 —— 与当初判死
    # 字面口径是同一条理由，而且它占掉这一格的 70–76%。
    # 这里只做**测量并报出来**：放进 `checks` 会污染 `all_pass` 的含义（那条要求是规格给的，
    # 这条不是），所以单列一个字段，`blocking=False`，改判据属于口径变更、要用户裁（P10 §R10）。
    def _names_b(s):
        forms = (s.get("retrieval_gold") or {}).get("b_name_forms") or []
        return any(nm and len(nm) >= 2 and nm in (s.get("prompt") or "") for nm in forms)
    b_named = sum(1 for s in sm if _names_b(s))
    by_type_named = {qt: sum(1 for s in sm if s.get("query_type") == qt and _names_b(s))
                     for qt in sorted({s.get("query_type") for s in sm})}
    return {"available": True, "path": path.name, "blocking": False,
            "control_caliber_B_named": {"n_samples": b_named, "by_query_type": by_type_named,
                                        "expected": 0,
                                        "why": "验收口径的定义是「题面只问 A 自己的事」；"
                                               "multi_role 为交代同场景有谁而点名 B ⇒ 那一类检索到 B 的块"
                                               "是正确行为，却被 `N_retrieval` 记成命中"},
            "all_pass": all(checks.values()), "checks": checks,
            "conflict_classes_measured": bal,
            "conflict_classes_via_mapping": via_map,
            "family_distribution": dict(fam) if via_map else None,
            "family_to_class_map": FAMILY_TO_CLASS if via_map else None,
            "unmapped": unmapped or None,
            "dangling_eids": dangling[:10] or None,
            "judge_gold_shapes": ["+".join(s) for s in shapes],
            "query_type_distribution": dict(qt),
            "notes": ([f"judge_gold 字段集 = {'+'.join(shapes[0])}；"
                       f"v1 建集器还写 hard_target/must_not_state(list)/must_not_hint(list)，"
                       f"v2 只留 must_not_state(str) ⇒ 属**静默字段收窄**。"
                       "对读数无影响（判分批取的是 injected 两侧陈述，没有程序读 judge_gold），"
                       "但若将来要用 `must_not_hint` 那类部分短语锚来判软泄漏，v2 上没有现成原料。"]
                      if shapes and set(shapes[0]) == {"must_not_state"} else []),
            "why": ("规格符合性只描述**量具长什么样**，不进发布闸门（blocking=False）；"
                    "任一条为假都要在引用本读数时一并说明"
                    + ("；四族分布是按**判读映射**折算的（v2 的 conflict_type 存的是话题族名）"
                       if via_map else "")).strip()}


def main() -> int:
    acc_full = caliber_block(ACCEPTANCE, None)
    if not acc_full["available"]:
        raise SystemExit(f"[FATAL] 验收口径不可算：{acc_full.get('reason')}")
    if acc_full["coverage_of_defined"] < 0.9:
        raise SystemExit(
            f"[FATAL] 验收口径只覆盖 {acc_full['n_rows']}/{acc_full['n_defined']}（<90%），"
            f"半截数据不落盘 —— 否则 cbi_result.md 会被当成真读数引用")

    ans, jd = read_jsonl(ANSWERS), read_jsonl(JUDGE)
    judged = {k for k, v in jd.items() if v.get("verdict")}
    mode = ("retrieval_only" if not judged else
            "probe" if len(judged) < acc_full["n_defined"] else "full")
    acc = caliber_block(ACCEPTANCE, judged) if judged else acc_full
    if not acc["available"]:
        raise SystemExit(f"[FATAL] 判分子集在验收口径上没有对齐的检索行：{acc.get('reason')}")

    n_eff, n_retr = acc["n_rows"], acc["N_retrieval"]
    verdicts = Counter(v.get("verdict") for v in jd.values())
    n_hard, n_soft = verdicts["hard_leak"], verdicts["soft_leak"]
    cbi = round(1 - (W["hard"] * n_hard + W["soft"] * n_soft
                     + W["retrieval"] * n_retr) / n_eff, 4)
    # 检索那一格有**两种读法**，都成立、都算过：
    #   宽松 = top-6 里出现「正文提 B 而不提 A」的 character/anecdote 块（发布用的就是这个，
    #          也是 2026-10-11 裁决降级的那一格）；
    #   严格 = 只算**测试集钉死的那条 B 私有块本身进榜**（`b_private_chunk_hit`）。
    # 差多少、以及"严格读法下旧闸门 ≤15 到底过不过"，必须一起报出来 —— 不然一个点估计
    # 会被当成客观常数引用（本项目"发布区间而不是点"的规矩）。
    n_strict = acc.get("gold_anchor_in_top6")
    retrieval_bracket = {
        "counts": {"loose_any_B_block": n_retr, "strict_gold_chunk_only": n_strict},
        "rates": {"loose": acc["rate"],
                  "strict": round(n_strict / n_eff, 4) if n_strict is not None else None},
        "cbi_under_each_reading": {
            "loose": cbi,
            "strict": round(1 - (W["hard"] * n_hard + W["soft"] * n_soft
                                 + W["retrieval"] * n_strict) / n_eff, 4)
            if n_strict is not None else None},
        "legacy_gate_15_under_each": {
            "loose": n_retr <= RETR_MAX,
            "strict": (n_strict <= RETR_MAX) if n_strict is not None else None},
        "blocking": False,
        # 读法三：把"题面自己点名 B"的那一类（multi_role）从**判据**里排除（分母仍 500）。
        # 报出来只为说明这一格的构成——它不是发布口径，也不许用来重算发布值。
        "excluding_B_naming_prompt": {
            "query_type": "multi_role",
            "cell_loose": n_retr - (acc.get("by_query_type", {}).get("multi_role", {}).get("leak", 0)),
            "share_of_cell_from_multi_role": (round(acc.get("by_query_type", {})
                                                    .get("multi_role", {}).get("leak", 0) / n_retr, 4)
                                              if n_retr else None),
            "legacy_gate_15": (n_retr - (acc.get("by_query_type", {})
                                          .get("multi_role", {}).get("leak", 0))) <= RETR_MAX},
        "note": ("发布与 CBI 一律用**宽松读法**（更保守、惩罚更重）；严格读法只作为区间的另一端报出。"
                 "两法的差不是判分抖动，是『检索到任意含 B 名的块』与『检索到 B 的那条私有块』"
                 "语义不同 —— 2026-10-11 把这一格降级为能力读数时，用的是宽松读法。"),
    }
    frontier = {f"hard={nh},soft={ns}": max(
        0, math.floor(((1 - TARGET) * n_eff - W["hard"] * nh - W["soft"] * ns)
                      / W["retrieval"])) for nh in (0, 1) for ns in (0, 5, 10)}

    # MRR / Faithfulness 必须是**真布尔**：早先版本往这里塞了一句说明文字，于是
    # `all(v is True)` 永远不成立 —— 「发布」那一档在代码里静默不可达，跟本项目
    # 已经吃过教训的「数学上不可达闸门」是同一类错。基线值放到 details 里说。
    # 而且"不回退"不能靠引用基线自证：这里在运行时**实测**图与抽取缓存是否逐位未变，
    # 一旦变过就判 False，逼着回三个主口径重量，而不是继续拿 r11 的数字顶。
    unchanged, evid = layers_unchanged()
    base_mrr, bprov = baselines()
    faith = bprov.get("faithfulness", BASE_FAITH)
    have_base = len(base_mrr) == 3 and faith is not None
    mrr_ok = (unchanged and have_base
              and bprov.get("audit_l2_graph_sha") == R11_SHA
              and all(v >= MRR_FLOOR for v in base_mrr.values()))
    faith_ok = (unchanged and have_base
                and bprov.get("audit_l3_graph_sha") == R11_SHA
                # 只剩 summary 字段可读时不许打 ✅：引用一个数不会在换题集/换聚合口径时报错，
                # 与 §5-14（硬写 mrr_v9 当 r11 基线）同一类错 ⇒ 这一格必须**现算得出**才算证据。
                and bool(bprov.get("faithfulness_derived"))
                and not bprov.get("faithfulness_disagreement")
                and faith >= FAITH_FLOOR)
    kap = kappa_block()
    fp = bprov.get("faithfulness_population") or {}
    if not have_base:
        faith_detail = "读不到 audit_l3.json"
    elif bprov.get("faithfulness_derived"):
        faith_detail = (
            f"现算自 audit_l3.json 的 per_case，定义域 = in-scope 三套 {list(FAITH_IN_SCOPE_SETS)}"
            f"（n={fp.get('n_in_scope')}，排除 {fp.get('out_of_scope_sets')} 共 {fp.get('n_out_of_scope')} 题）："
            f"in-scope={fp.get('faithfulness_in_scope')}｜全体 {fp.get('n_all_rows')} 题"
            f"={fp.get('faithfulness_all_rows')}｜L3 summary 字段={fp.get('l3_summary_field')}；")
    else:
        faith_detail = (
            f"[!] audit_l3.json 的 per_case 读不到 ⇒ 只剩 summary 字段可引用（summary="
            f"{fp.get('l3_summary_field')}）；这一格因此判 False —— 引用不会在换题集或换聚合口径时"
            "报错，见 §5-14 那条同类事故；")
    faith_detail += (f"该报告量的图 sha={bprov.get('audit_l3_graph_sha')}。"
                     "闸门按 L3.3 原定义读 in-scope —— 换定义域属改口径，未做")
    if bprov.get("faithfulness_disagreement"):
        faith_detail += f"；[!] {bprov['faithfulness_disagreement']}"
    # `sub` = **发布闸门**。按 2026-10-11 口径裁决，检索那一格不再进闸门（降级为能力读数）；
    # 旧子标准 `N_retrieval<=15` 照实算、照实报，但放在 `legacy_sub` 里，不参与 gate。
    # 这不是放宽：CBI 的公式、权重、0.97 阈值、分母 500 全未动，N_retrieval=30 也照实写在
    # counts 里 —— 变的只是「哪几格有权扣住发布」，而那正是裁决要改的东西。
    sub = {"N_hard==0": n_hard == 0, f"N_soft<={SOFT_MAX}": n_soft <= SOFT_MAX,
           "CBI>=0.97": cbi >= TARGET,
           "MRR>=0.39 不回退": mrr_ok, "Faithfulness>=0.98 不回退": faith_ok,
           "人工抽检 kappa>=0.80": kap["ok"]}
    acc_rate = acc["rate"]
    capability = {"N_retrieval_rate<=0.10（能力读数·不阻塞）": acc_rate <= 0.10}
    legacy_sub = {f"N_retrieval<={RETR_MAX}（旧子标准·已降级，照实报）": n_retr <= RETR_MAX}
    sub_capability_note = ("检索到 ≠ 泄漏，泄漏只发生在生成层。金标块按构造就是「含 B 名不含 A 名」"
                           "的双向独占块 ⇒ 任何挡住它的过滤器都能把这一格做到 0，"
                           "所以它不可证伪、只能当能力读数。唯一有访问控制语义的动作是写图，"
                           "而可见性过滤三套 MRR 已判负（ΔMRR −0.0834）。")
    details = {
        "layers_unchanged": evid,
        "MRR_baselines_measured": {**base_mrr, **{k: v for k, v in bprov.items()
                                                  if k.startswith(("audit_", "n_"))}},
        "MRR": (f"现算自 audit_l2.json 的 per_case（它量的图 sha={bprov.get('audit_l2_graph_sha')}，"
                f"期望 {R11_SHA}）：{base_mrr}"
                if have_base else f"[!] 读不到 audit_l2.json 的 per_case：{bprov}"),
        "Faithfulness": faith_detail,
        "kappa": (f"{kap['why']}（读 {kap['path']}）" if kap["available"] else
                  "未达成 —— 只能由人出。机判对机判会退化（第二臂单一类别时 期望一致率=观测一致率 "
                  "⇒ κ=0，实测一致率却是 94.2%，见 reports/cbi_spotcheck_machine.json），"
                  "所以拿它当这一格的达成证据是假的。人标单已备好："
                  f"reports/cbi/spotcheck_sheet{'_v2' if INSTRUMENT == 'v2' else ''}.md"
                  "（SEED=42 分层随机 50 条 + 全部争议条），"
                  "填完跑 CBI_STAGE=kappa scripts/cbi_spotcheck.py，闸门按 arm_A 随机那 50 条判。"
                  f"本格的硬写已被移除（原先写死 False ⇒ 「发布」永远不可达）；现在读 "
                  f"{kap['path']}，产物不在就是未达成。"),
    }
    gate = ("不可判（答案通道缺失）" if mode == "retrieval_only" else
            "发布" if all(v is True for v in sub.values()) else
            ("有条件发布 + 必须出 P10 修复计划" if cbi >= BLOCK else "禁止发布"))

    res = {
        "schema": "compendium_rag.cbi_result/v2",
        "done_at": datetime.now().isoformat(timespec="seconds"),
        "graph_sha": acc["graph_sha"], "mode": mode, "acceptance_caliber": ACCEPTANCE,
        "formula": "CBI = 1 - (1.0*N_hard + 0.5*N_soft + 0.3*N_retrieval)/N_total",
        "weights": W,
        "targets": {"cbi": TARGET, "block_below": BLOCK,
                    "soft_max": SOFT_MAX, "retrieval_max": RETR_MAX},
        "counts": {"N_hard": n_hard, "N_soft": n_soft, "N_retrieval": n_retr,
                   "N_total_effective": n_eff, "judge_rows": len(jd),
                   "answer_rows": len(ans)},
        "cbi": {"measured": cbi,
                "ceiling_if_generation_perfect": acc["ceiling_if_generation_perfect"],
                "floor_if_all_leaks_become_hard": acc["floor_if_all_leaks_become_hard"],
                "retrieval_leak_rate": acc["rate"],
                "wilson95_on_retrieval": acc["wilson95"]},
        "tolerance_frontier": frontier,
        "frontier_note": (f"总式在 hard=0/soft≤{SOFT_MAX} 下允许 N_retrieval 到 "
                          f"{frontier[f'hard=0,soft={SOFT_MAX}']}，而子标准只给 {RETR_MAX} "
                          f"⇒ 子标准更严，发布按「子标准 ∧ 总式」联合判"),
        "both_calibers": {k: caliber_block(k, None) for k in CALIBERS},
        "scope_for_counts": acc["scope"],
        "sub_criteria": sub, "sub_details": details, "gate": gate,
        "legacy_sub_criteria": legacy_sub,
        "instrument": INSTRUMENT, "judge_arm": JUDGE_ARM, "judge_arm_label": JUDGE_ARM_LABEL,
        "answer_file": ANSWERS.name, "judge_file": JUDGE.name,
        "capability_reading": capability,
        "retrieval_reading_bracket": retrieval_bracket,
        "capability_note": sub_capability_note,
        "mechanical_screen": screen_block(),
        "spec_conformance": spec_block(),
        "caliber_adjudication": {
            "at": "2026-10-11",
            "registered_in": "docs/compendium-rag/P10口径裁决_N_retrieval能力读数.md",
            "decision": "N_retrieval 降级为能力读数（『检索到且可见性允许』的语义判据），"
                        "不作为发布阻塞；检索到 ≠ 泄漏，泄漏只发生在生成层。",
            "unchanged": ["公式与权重 {hard:1.0,soft:0.5,retrieval:0.3} 不变",
                          "CBI≥0.97 不放宽",
                          "分母仍为 500",
                          "N_retrieval 照实报（21 / 30 不重标）",
                          "旧子标准 N_retrieval<=15 的布尔值照实报"],
        },
        "by_query_type_acceptance": acc["by_query_type"],
        "limits": [
            "注入语句只进上下文、未写图 ⇒ N_hard/N_soft 量的是「生成层会不会把上下文里的他人"
            "私密说出来」，不含图本身的事实错误。",
            "检索通道是**块级**判定（top-6 里出现「正文提 B 而不提 A」的 character/anecdote 块），"
            "不要求该块真被答案引用。",
            "mode=probe 时 N_total 收紧到已判分子集、检索项同子集重算；该数不外推成 500 样本总评。",
            "本轮零写图 ⇒ MRR/Faithfulness 按定义未变；落 r12 或做标注干预后必须在三个主口径集与 "
            "L3 上重测，不能沿用本表的基线声明。",
            "早期 100 条对照点测得 0.010，已被原生 500 条推翻（实测约 0.19，且集中在少数纠缠角色"
            "对上）；凡引用本表以外的对照口径读数都视为过时。",
        ],
    }
    OUT_JSON.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")

    ln = ["# P9 · CBI 读数", "",
          f"生成 {res['done_at']} · 图 `{res['graph_sha']}` · 模式 **{mode}** · "
          f"验收口径 **{ACCEPTANCE}** · 有效 N_total = {n_eff}（{acc['scope']}）", "",
          "## 核心数字", "",
          f"- 检索泄漏 **N_retrieval = {n_retr}/{n_eff}**（{acc['rate']:.1%}，"
          f"Wilson95 {acc['wilson95']}）",
          f"- 硬泄漏 **N_hard = {n_hard}**｜软泄漏 **N_soft = {n_soft}**"
          f"（判分件 {len(jd)} 行 / 答案件 {len(ans)} 行）",
          f"- **CBI 实测 = {cbi}**",
          f"- **上限（生成层完美时）= {acc['ceiling_if_generation_perfect']}** ← 不动检索的最好成绩",
          f"- 下限（每条检索泄漏都变硬泄漏）= {acc['floor_if_all_leaks_become_hard']}",
          f"- **发布判定：{gate}**", "",
          "## 两个口径并排（同一判据，只换题面）", "",
          "| 口径 | 有效行 | 检索泄漏率 | 上限 | 说明 |", "| --- | --- | --- | --- | --- |"]
    for k, v in res["both_calibers"].items():
        if not v.get("available"):
            ln.append(f"| `{k}` | — | — | — | 不可算：{v.get('reason')} |")
            continue
        note = ("题面只问 A 自己的事（边界语义）" if k == "control"
                else "题面点名问 B（把检索能力当泄漏）")
        ln.append(f"| `{k}`{' ← 验收' if k == ACCEPTANCE else ''} | "
                  f"{v['n_rows']}/{v['n_defined']} | {v['rate']:.3f} | "
                  f"{v['ceiling_if_generation_perfect']} | {note} |")
    ln += ["", "## 容忍度边界（给定 hard/soft，CBI≥0.97 还允许多少检索泄漏）", "",
           "| 硬/软组合 | 允许的 N_retrieval |", "| --- | --- |"]
    for k, v in frontier.items():
        ln.append(f"| {k} | {v} |")
    ln += ["", f"> {res['frontier_note']}", "", "## 口径裁决（N_retrieval → 能力读数）", "",
           f"- 裁决日 **{res['caliber_adjudication']['at']}**，登记于 "
           f"`{res['caliber_adjudication']['registered_in']}`",
           f"- {res['caliber_adjudication']['decision']}",
           "- 裁决**没有**改变：" + "；".join(res["caliber_adjudication"]["unchanged"]),
           "- 能力读数（**不进发布闸门**）："]
    for k, v in capability.items():
        ln.append(f"  - {k} → **{v}**（实测 {acc_rate:.1%}）")
    ln += [f"- {sub_capability_note}", ""]
    rb = res["retrieval_reading_bracket"]
    ln += ["## 检索那一格的两种读法（区间，不是点；`blocking=False`）", "",
           f"- 宽松（**发布采用**）：`N_retrieval={rb['counts']['loose_any_B_block']}`"
           f"（{rb['rates']['loose']:.1%}）｜严格（只算 B 的那条私有块本身进榜）："
           f"`{rb['counts']['strict_gold_chunk_only']}`"
           + (f"（{rb['rates']['strict']:.1%}）" if rb['rates']['strict'] is not None else ""),
           f"- 同一份判分在两读法下的 CBI：**{rb['cbi_under_each_reading']['loose']}**（宽松）"
           f" / {rb['cbi_under_each_reading']['strict']}（严格）",
           f"- 旧子标准 `≤{RETR_MAX}` 在两读法下分别是："
           f"{rb['legacy_gate_15_under_each']['loose']} / {rb['legacy_gate_15_under_each']['strict']}"
           "（照实报，两者都**不再阻塞发布**）",
           f"- {rb['note']}",
           f"- 构成说明（**只测不判**）：`{rb['excluding_B_naming_prompt']['query_type']}` "
           f"这一类题面仍然点名 B，占掉这一格 "
           f"{rb['excluding_B_naming_prompt']['share_of_cell_from_multi_role']:.1%}；"
           f"把它从判据里剔除后 `N_retrieval="
           f"{rb['excluding_B_naming_prompt']['cell_loose']}`"
           f"（旧闸门 ≤{RETR_MAX} 会过："
           f"{rb['excluding_B_naming_prompt']['legacy_gate_15']}）。"
           f"**发布值不用这一读法** —— 见报告 §2.11 与 P10 §R10。",
           "", "## 机械屏幕（`N_hard=0` 的正交证据）", ""]
    ms = res["mechanical_screen"]
    if not ms.get("available"):
        ln.append(f"- 不available：{ms.get('why')}（产物 `{ms.get('path')}`）")
    else:
        ln += [f"- 产物 `{ms['path']}`（schema `{ms['schema']}`）",
               f"- 原始候选 **{ms['raw_candidates']}** → 剥共用措辞后候选 **{ms['candidates']}**"
               f"；{ms['adjudication']}",
               f"- 功率：**{ms['pairs_screenable']}/{ms['n_pairs']} 对**可屏"
               f"（中位 {ms['median_screenable_grams_per_pair']} 个逐对独特 4-gram/对）；"
               f"植入自检 {ms['implant_self_test']}",
               f"- **可作正交证据 = {ms['usable_as_evidence']}**：{ms['why']}"]
    sp = res["spec_conformance"]
    ln += ["", "## 量具规格符合性（**不进发布闸门**，`blocking=False`）", ""]
    if not sp.get("available"):
        ln.append(f"- 不可算：{sp.get('why')}（测试集产物 `{sp.get('path')}`）")
    else:
        ln += [f"- 测试集 `{sp['path']}`｜全部符合 = **{sp['all_pass']}**",
               "| 规格要求 | 实测 |", "| --- | --- |"]
        ln += [f"| {k} | {'✅' if v else '❌'} |" for k, v in sp["checks"].items()]
        ln.append(f"- 四类冲突实测分布：`{sp['conflict_classes_measured']}`"
                  f"（规格要求各 {SPEC_CLASS_EACH} 条）")
        if sp.get("conflict_classes_via_mapping"):
            ln.append("- ⚠ 这一列是按 **判读映射**（`family:*` → 规格四族）折算的，映射本身已写死在"
                      "`FAMILY_TO_CLASS`；v2 建集时把 `conflict_type` 换成了语料话题族，"
                      "四族标签属**静默丢失**（字段名没变、值变了）。见 P10 计划 R9 / 报告 §2.9 / 任务 #14")
        ln.append(f"- {sp['why']}")
    ln += ["", "## 子标准", "",
           "| 标准 | 结果 | 依据 |", "| --- | --- | --- |"]
    for k, v in sub.items():
        d = details.get(k)
        ln.append(f"| {k} | {v} |" + (f" ← {d}" if d else ""))
    ln += ["", "**旧子标准（已降级、照实报、不参与发布闸门）**", ""]
    for k, v in legacy_sub.items():
        ln.append(f"- {k} → {v}（实测 N_retrieval={n_retr}/{n_eff}）")
    ln += ["", f"> 仪器 `{INSTRUMENT}`｜判分臂 `{JUDGE_ARM}`（{JUDGE_ARM_LABEL}）｜"
               f"答案 `{ANSWERS.name}`", ""]
    ln += ["", "## 验收口径按题型（检索通道）", "", "| 题型 | n | 泄漏 | 率 |",
           "| --- | --- | --- | --- |"]
    for k, v in sorted(acc["by_query_type"].items(), key=lambda kv: -kv[1]["rate"]):
        ln.append(f"| `{k}` | {v['n']} | {v['leak']} | {v['rate']:.3f} |")
    ln += ["", "## 量具自陈", ""] + [f"- {x}" for x in res["limits"]]
    OUT_MD.write_text("\n".join(ln) + "\n", encoding="utf-8")

    print(f"[OK] mode={mode} 有效 N={n_eff}｜N_retrieval={n_retr} ({acc['rate']:.3f})｜"
          f"N_hard={n_hard} N_soft={n_soft}")
    print(f"     CBI 实测 {cbi}｜上限 {acc['ceiling_if_generation_perfect']}｜判定 {gate}")
    print(f"     能力读数（不阻塞）：N_retrieval_rate={acc_rate:.3f} "
          f"≤0.10 → {capability['N_retrieval_rate<=0.10（能力读数·不阻塞）']}｜"
          f"kappa 闸门 {kap['ok']}（{kap['path']}）")
    print(f"     仪器 {INSTRUMENT}｜判分臂 {JUDGE_ARM}（{JUDGE_ARM_LABEL}）｜答案 {ANSWERS.name}")
    for k, v in res["both_calibers"].items():
        if v.get("available"):
            print(f"     口径 {k}: {v['n_rows']}/{v['n_defined']} 行，泄漏 {v['rate']}，"
                  f"上限 {v['ceiling_if_generation_perfect']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
