# -*- coding: utf-8 -*-
"""exposure 块的负向测试：名次读数必须**真的**对名次敏感，又必须**不参与**评分。

为什么要有这个脚本（rules 文档 §6.5 / §6.7 两条旧教训的直接应用）：
1. `flag_mismatch_with_channel` 若写成 `hit == hit` 那种同源自证，永远是 0，报「0 处不一致」
   就成了假绿。⇒ 必须有一例把通道的 `b_private_chunk_hit` 翻掉，看它**必须**变非零。
2. `rank_hist` / `at_rank1` 若其实是按 `b_private_chunk_hit` 数的，那名次分布就是金标计数的别名，
   多报一格不增信息。⇒ 必须有一例把金标块挪到第 1 名（top_ids 集合不变、标记不变），
   看名次读数**必须**动、而 `N_retrieval` 与评分格**必须**不动。
3. 反过来：名次读数一旦接进分数或接进 `MRR>=0.39` 那格，就是「为达标改判据」。
   ⇒ 断言所有变异体的**非 exposure 部分逐字段相等**，且产物里没有任何把 reciprocal_rank
   与 0.39 相比的字段。

变异只写在系统临时目录；仓库里的检索通道与四份读数在运行前后按 sha 断言未变。

用法：`PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe scripts/cbi_exposure_negtest.py`
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "data" / "compendium_rag" / "reports"
CBI = REPORTS / "cbi"
sys.path.insert(0, str(ROOT / "scripts"))
# Windows 控制台常见 cp936：产物落盘后才抛 UnicodeEncodeError 最难查（写了一半、退出码非零）。
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(errors="replace")


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


K = load("cbi_calculator")
TS_PATH = K.CALIBERS["control"][0]
RETR_PATH = K.CALIBERS["control"][1]

FAILS: list[str] = []
N = 0


def ck(name, got, want):
    global N
    N += 1
    if got != want:
        FAILS.append(f"{name}: got={got!r} want={want!r}")
        print(f"  [FAIL] {name}: {got!r} != {want!r}")
    else:
        print(f"  [ok]   {name} = {got!r}")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def run(block_retr: Path) -> dict:
    """把 control 口径的检索通道换成变异体，其余（测试集、权重、阈值）全部原样。"""
    K.CALIBERS["control"] = (TS_PATH, block_retr)
    return K.caliber_block("control", None)


def write_jsonl(rows, p: Path):
    p.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n",
                 encoding="utf-8")
    return p


def main() -> int:
    before = {p: sha(p) for p in [RETR_PATH, TS_PATH] + [
        REPORTS / f"cbi_result{s}.json" for s in ("", "_full", "_v2instrument",
                                                  "_v2instrument_v2_r2")]}
    before.update({p: sha(p) for p in (REPORTS / f"cbi_result{s}.md" for s in
                                       ("", "_full", "_v2instrument", "_v2instrument_v2_r2"))})

    rows = [json.loads(l) for l in RETR_PATH.read_text(encoding="utf-8").splitlines() if l.strip()]
    ts = json.loads(TS_PATH.read_text(encoding="utf-8"))
    samples = {s["sample_id"]: s for s in ts["samples"]}

    def gold_of(r):
        return ((samples.get(r["sample_id"]) or {}).get("retrieval_gold") or {}).get("b_private_chunk")

    hits = [i for i, r in enumerate(rows)
            if gold_of(r) and gold_of(r) in (r.get("top_ids") or [])]
    print(f"[样本] 通道 {len(rows)} 行；按 top_ids 复算的金标命中 {len(hits)} 行")

    tmp = Path(tempfile.mkdtemp(prefix="cbi_expo_neg_"))
    mutants: dict[str, list] = {}
    for tag in ("base", "flip_flag", "drop_gold", "promote", "shuffle_nongold"):
        m = [json.loads(json.dumps(r)) for r in rows]
        mutants[tag] = m
    # flip_flag：通道标记与 top_ids 打架（第一命中行改成「没命中」，金标仍在 top_ids 里）
    i0 = hits[0]
    mutants["flip_flag"][i0]["b_private_chunk_hit"] = False
    # drop_gold：金标块真的不在榜上，且通道标记同步改 False ⇒ 一致性 0，但名次计数必须降
    gi = mutants["drop_gold"][i0]["top_ids"].index(gold_of(rows[i0]))
    del mutants["drop_gold"][i0]["top_ids"][gi]
    mutants["drop_gold"][i0]["b_private_chunk_hit"] = False
    # promote：把金标块挪到第 1 位（集合不变、标记不变、泄漏判定不该变）
    g = gold_of(rows[i0])
    tp = mutants["promote"][i0]["top_ids"]
    tp.remove(g)
    tp.insert(0, g)
    tp = mutants["shuffle_nongold"][i0]["top_ids"]
    if len(tp) >= 3:
        tp[1], tp[2] = tp[2], tp[1]      # 非金标两块互换：名次读数不该有任何反应
    outs = {t: run(write_jsonl(m, tmp / f"{t}.jsonl")) for t, m in mutants.items()}

    base, expo = outs["base"], outs["base"]["exposure"]
    print(f"[基线] 与已发布读数对照：n_gold={expo['n_gold_in_top6']} "
          f"at_rank1={expo['at_rank1']} rr_cond={expo['reciprocal_rank_hazard_cond']}")
    pub = json.loads((REPORTS / "cbi_result_full.json").read_text(encoding="utf-8"))
    ck("基线复现已发布 control.exposure（整块逐字段）",
       base["exposure"], pub["both_calibers"]["control"]["exposure"])
    ck("基线：通道标记与 top_ids 无冲突", expo["flag_mismatch_with_channel"], 0)

    print("[变异 1 flip_flag] 通道打标与 top_ids 打架 ⇒ 必须抓到")
    ff = outs["flip_flag"]["exposure"]
    ck("flag_mismatch 必须非零（不是同源自证）", ff["flag_mismatch_with_channel"] >= 1, True)
    ck("名次计数按 top_ids，不跟通道标记跑", ff["n_gold_in_top6"], expo["n_gold_in_top6"])
    ck("通道那一列确实被翻动了（证明两列不同源）",
       outs["flip_flag"]["gold_anchor_in_top6"], expo["n_gold_in_top6"] - 1)

    print("[变异 2 drop_gold] 金标真的落榜 ⇒ 名次计数必须降，一致性反而归零")
    dg = outs["drop_gold"]["exposure"]
    ck("n_gold 必须降 1", dg["n_gold_in_top6"], expo["n_gold_in_top6"] - 1)
    ck("by_k 必须同步降", dg["exposure_by_k"]["top6"], expo["exposure_by_k"]["top6"] - 1)
    ck("flag_mismatch 保持 0（一致性不是计数信号）", dg["flag_mismatch_with_channel"], 0)

    print("[变异 3 promote] 金标挪到第 1 名 ⇒ 名次读数必须动，评分格必须不动")
    pr = outs["promote"]
    ck("at_rank1 必须 0 -> 1", pr["exposure"]["at_rank1"], 1)
    ck("top1 暴露必须 0 -> 1", pr["exposure"]["exposure_by_k"]["top1"], 1)
    ck("n_gold 不变（不是多了一次泄漏）", pr["exposure"]["n_gold_in_top6"], expo["n_gold_in_top6"])
    ck("危险倒数排名必须严格上升", pr["exposure"]["reciprocal_rank_hazard_cond"]
       > expo["reciprocal_rank_hazard_cond"], True)
    # `channel` 是产物名（变异体文件名不同），`exposure` 是本次要比的块 —— 两者都排除在外
    PROV = ("exposure", "channel")
    non_expo = {k: v for k, v in base.items() if k not in PROV}
    ck("评分/检索格对名次完全不敏感（exposure 只做报告，不进分数）",
       {k: v for k, v in pr.items() if k not in PROV}, non_expo)

    print("[变异 4 shuffle_nongold] 非金标两块互换 ⇒ 整块必须毫无反应")
    ck("非金标顺序不进读数", outs["shuffle_nongold"]["exposure"], expo)

    print("[边界] 这块读数不许被当成质量 MRR")
    ck("读数里没有 reciprocal_rank 与 0.39 的比较字段",
       any("mrr" in k.lower() for k in expo), False)
    ck("warning 里点明了 0.39 只能在 r11 三套题上读",
       "0.39" in expo["warning"] and "MRR" in expo["warning"], True)
    ck("评分权重表里没有 exposure 这一项（名次读数进不了分数）",
       set(K.W), {"hard", "soft", "retrieval"})

    after_ok = all(sha(p) == h for p, h in before.items())
    ck("仓库产物（检索通道 + 四份读数 json/md）未被本脚本改动", after_ok, True)

    print(f"\n[结果] 断言 {N} 条，失败 {len(FAILS)} 条")
    for f in FAILS:
        print("  !! " + f)
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
