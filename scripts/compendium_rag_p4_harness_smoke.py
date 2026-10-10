# -*- coding: utf-8 -*-
"""P4.2 验收装置离线冒烟：audit_l3.py 的三处改造自证（不联网、不调任何 LLM）。

跑法（工作目录 = 仓库根）：
    .venv/Scripts/python.exe -X utf8 scripts/compendium_rag_p4_harness_smoke.py
    # 可选：--n 5（默认 5）--tag p4_smoke（默认加时间戳后缀，避免并发互踩）

自证四件事：
  T1 语法/导入：importlib 载入 scripts/audit_l3.py（不执行 __main__）。
  T2 count_blocks_in_window：用**合成上下文**（含块内引用 `[S1]`、跳块让号前移、
     R4 保底 `[节选]`）验证溯源头正则计块数的正确性 —— 不许用 `[S{n}]` 最大值猜。
  T3 compose 同源：prepare 落的批次项含 `prompt`，且 prompt 头部就是
     compose.ANSWER_SYSTEM_PROMPT（逐字比对），`prompt_mode=compose_v1`、
     `history: null`、`allocator=v2_perblock`。
  T4 优雅降级：无 judge 产物时 `degrade_reason()` 返回明确说明串（不抛异常）。

产物隔离：状态落 `data/knowledge/_audit/p4_harness_<tag>/`，报告落
`data/compendium_rag/reports/p4_harness_<tag>*.json` —— **绝不覆盖** v8 定版
全量的 `l3_batches/` 与 `reports/audit_l3.json`。
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT / "src", ROOT / "scripts"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

AUDIT_L3 = ROOT / "scripts" / "audit_l3.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("audit_l3_smoke", AUDIT_L3)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


class Checks:
    def __init__(self) -> None:
        self.fails: list[str] = []
        self.oks: list[str] = []

    def ok(self, name: str, detail: str = "") -> None:
        self.oks.append(name)
        print(f"  [PASS] {name}" + (f" — {detail}" if detail else ""))

    def fail(self, name: str, detail: str) -> None:
        self.fails.append(f"{name}: {detail}")
        print(f"  [FAIL] {name} — {detail}")

    def check(self, name: str, cond: bool, detail: str = "") -> bool:
        (self.ok if cond else self.fail)(name, detail)
        return bool(cond)


# ── T2 的合成上下文（构造三个易错场景）──

CTX_CONTIGUOUS = """【图谱实体】
  - 维也纳 (Vienna)
【关系脉络】
  无
【原文证据】
[S1 chunk=ch_001 doc=story_ch1 cat=story] [story_ch1#0] 一九九九年，维也纳。
[S2 chunk=ch_002 doc=story_ch1 cat=story] [story_ch1#1] 暴雨降临。
[S3 chunk=ch_003 doc=story_ch2 cat=story] [story_ch2#0] 她自称是「[S1] 归来的」。
"""

CTX_GAPPED = """【原文证据】
[S1 chunk=ch_001 doc=d1 cat=story] [d1#0] 甲。
[S2 chunk=ch_002 doc=d1 cat=story] [d1#1] 乙。
"""


def t2_count_blocks(mod, ck: Checks) -> None:
    print("T2 count_blocks_in_window（溯源头正则）")
    r = mod.count_blocks_in_window(CTX_CONTIGUOUS)
    ck.check("T2.1 计出 3 块（块内引用 [S1] 不重复计）",
             r["n_blocks_in_window"] == 3, f"，实得 {r['n_blocks_in_window']}")
    ck.check("T2.2 编号连续 [1,2,3]", r["block_numbers"] == [1, 2, 3]
             and r["blocks_contiguous"] is True, f"{r['block_numbers']}")
    ck.check("T2.3 非保底路径 window_fallback=False", r["window_fallback"] is False)

    r2 = mod.count_blocks_in_window(CTX_GAPPED)
    ck.check("T2.4 只数行首 DET 头（【原文证据】外不计）",
             r2["n_blocks_in_window"] == 2, f"，实得 {r2['n_blocks_in_window']}")

    # R4 保底：一块都装不下 → 截断注入 + [节选]，无带编号块
    r3 = mod.count_blocks_in_window(
        "【原文证据】\n[节选] 甲。\n[节选] 乙。\n")
    ck.check("T2.5 R4 保底路径计 0 块且标 fallback",
             r3["n_blocks_in_window"] == 0 and r3["window_fallback"] is True,
             f"n={r3['n_blocks_in_window']} fb={r3['window_fallback']}")

    # 反例自证：只有 2 个真块，但正文里的行内引用把 `[S{n}]` 最大值顶到 9。
    # 用「全文 [S{n}] 最大值」去猜会得 9；溯源头口径应得 2。
    tricky = ("【原文证据】\n"
              "[S1 chunk=c1 doc=d1 cat=story] [d1#0] 见 [S7] 的说法。\n"
              "[S2 chunk=c2 doc=d1 cat=story] [d1#1] 另见 [S9]。\n")
    r4 = mod.count_blocks_in_window(tricky)
    naive_ids = [int(n) for n in re.findall(r"\[S(\d+)\]", tricky)]
    naive_max = max(naive_ids)
    ck.check("T2.6 溯源头口径 ≠ 全文 [S{n}] 最大值口径（反例自证）",
             r4["n_blocks_in_window"] == 2 and naive_max == 9,
             f"溯源口径={r4['n_blocks_in_window']}，"
             f"全文最大值口径={naive_max}（会被行内引用顶高）")

    ck.check("T2.7 正则锚行首且要求 chunk=/doc=/cat=",
             mod.RE_PROV_HEADER.pattern.startswith("(?m)^\\[S")
             and "chunk|doc|cat" in mod.RE_PROV_META.pattern)


# ── T3/T4 需要在子进程里跑 CLI（状态目录隔离）──

def _run_cli(mod_args: list[str], cwd: Path) -> tuple[int, str]:
    cmd = [str(ROOT / ".venv" / "Scripts" / "python.exe"), "-X", "utf8",
           str(AUDIT_L3), *mod_args]
    p = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def main() -> int:
    ap = argparse.ArgumentParser(description="P4.2 装置离线冒烟")
    ap.add_argument("--n", type=int, default=5, help="子集题数（默认 5）")
    ap.add_argument("--tag", default="", help="状态/报告隔离标（默认 p4_smoke_<ts>）")
    ap.add_argument("--base", default="",
                    help="冒烟产物的可写基目录（默认仓库根）。"
                         "受限沙箱下低完整性令牌只能写仓库根，故默认不用 "
                         "data/ 下的定版路径；在无限制的机器上可传 "
                         "--base data 还原生产形状的落盘位置。")
    ap.add_argument("--skip-cli", action="store_true",
                    help="只跑 T1/T2/T4 纯函数自证，不实跑 prepare")
    a = ap.parse_args()
    tag = a.tag or f"p4_smoke_{time.strftime('%m%d%H%M%S')}"
    base = Path(a.base) if a.base else ROOT
    if not base.is_absolute():
        base = ROOT / base
    ck = Checks()

    print("T1 载入 scripts/audit_l3.py")
    mod = _load_module()
    ck.check("T1.1 模块可导入", hasattr(mod, "MODES"))
    ck.check("T1.2 三模式齐全",
             set(mod.MODES) == {"prepare", "judge-prep", "collect"},
             str(sorted(mod.MODES)))
    ck.check("T1.3 口径标固定",
             mod.PROMPT_MODE == "compose_v1" and mod.ROLE_CARD_MODE == "empty"
             and mod.HISTORY_MODE == "none",
             f"{mod.PROMPT_MODE}/{mod.ROLE_CARD_MODE}/{mod.HISTORY_MODE}")

    t2_count_blocks(mod, ck)

    print("T4 无判分产物优雅降级（纯函数）")
    ck.check("T4.1 缺 gold → 明确说明串（非异常）",
             isinstance(mod.degrade_reason(gold_present=False, n_judges=0,
                                           n_answers=0), str))
    d = mod.degrade_reason(gold_present=True, n_judges=0, n_answers=3)
    ck.check("T4.2 judge 为空 → 降级串含 N/A 语义",
             isinstance(d, str) and "N/A" in d, (d or "")[:60])
    ck.check("T4.3 有判分 → None（不降级）",
             mod.degrade_reason(gold_present=True, n_judges=679,
                                n_answers=679) is None)

    if a.skip_cli:
        print(f"\n（--skip-cli）PASS {len(ck.oks)} / FAIL {len(ck.fails)}")
        return 1 if ck.fails else 0

    from compendium_rag.compose import ANSWER_SYSTEM_PROMPT  # noqa: PLC0415
    from compendium_rag.compose import render_prompt  # noqa: PLC0415

    # T3a：默认路径解析（纯函数，不落盘）——生产形状必须是 _audit/ + reports/
    print("T3a paths_for 默认路径解析（生产形状，不落盘）")
    ns = argparse.Namespace(tag=tag, input_dir="", state_dir="",
                            reports_dir="", report_name="")
    pp = mod.paths_for(ns)
    ck.check("T3a.1 无 --state-dir 时状态落 _audit/p4_harness_<tag>/",
             pp.state_dir == mod.AUDIT_DIR / f"p4_harness_{tag}", str(pp.state_dir))
    ck.check("T3a.2 报告落 reports/p4_harness_<tag>.json",
             "p4_harness_" in pp.report.name
             and pp.report.parent == mod.REPORTS_DIR, pp.report.name)
    ck.check("T3a.3 状态目录 ≠ 定版全量 l3_batches/",
             pp.batch_dir != mod.BATCH_DIR and pp.gold_map != mod.GOLD_MAP,
             f"{pp.batch_dir} vs {mod.BATCH_DIR}")
    ns0 = argparse.Namespace(tag="", input_dir="", state_dir="",
                             reports_dir="", report_name="")
    pp0 = mod.paths_for(ns0)
    ck.check("T3a.4 无 tag → 回落到 v8 全量路径（向后兼容）",
             pp0.state_dir == mod.AUDIT_DIR
             and pp0.report == mod.REPORTS_DIR / "audit_l3.json",
             str(pp0.report.name))

    # T3b：实跑 prepare（写面带 --state-dir/--reports-dir，指向可写基目录）
    state = base / f"p4_harness_{tag}"
    rdir = base / "p4_harness_reports"
    print(f"T3b 实跑 prepare 小样本 n={a.n} | 状态 {state}")
    rc, out = _run_cli(["--mode", "prepare", "--n-questions", str(a.n),
                        "--state-dir", str(state), "--reports-dir", str(rdir),
                        "--report-name", f"p4_harness_{tag}"], ROOT)
    ck.check("T3.1 prepare 退出码 0", rc == 0, f"rc={rc} 尾部：{out.strip()[-200:]}")
    report = rdir / f"p4_harness_{tag}_prepare.json"
    ck.check("T3.2 状态目录隔离落盘", state.is_dir(), str(state))
    ck.check("T3.3 报告落 p4_harness_ 前缀", report.is_file(), report.name)
    ck.check("T3.4 未触碰定版全量批次目录",
             (state / "l3_batches") != mod.BATCH_DIR)

    items: list[dict] = []
    for p in sorted((state / "l3_batches").glob("ans_b*.json")):
        items.extend(json.loads(p.read_text(encoding="utf-8"))["items"])
    ck.check("T3.5 批次题数 = n", len(items) == a.n, f"{len(items)} vs {a.n}")

    if items:
        it = items[0]
        ck.check("T3.6 批次项保留向后兼容字段 query/context",
                 "query" in it and "context" in it)
        ck.check("T3.7 批次项含 prompt 且逐字含 system 提示词",
                 it.get("prompt", "").startswith("## system")
                 and ANSWER_SYSTEM_PROMPT[:40] in it.get("prompt", ""),
                 "prompt 头部 = compose system 提示词")
        ck.check("T3.8 prompt_mode=compose_v1 / history=None / allocator",
                 it.get("prompt_mode") == "compose_v1"
                 and it.get("history") is None
                 and it.get("allocator") == "v2_perblock",
                 f"{it.get('prompt_mode')}/{it.get('history')}/{it.get('allocator')}")
        ck.check("T3.9 每题记录 n_blocks_in_window / n_evidence_retrieved",
                 all("n_blocks_in_window" in x and "n_evidence_retrieved" in x
                     for x in items),
                 "n_blocks_in_window="
                 + ",".join(str(x["n_blocks_in_window"]) for x in items))
        ck.check("T3.10 gold 未泄漏进批次（无 keywords/ref/set）",
                 not any(k in it for k in ("keywords", "ref", "set")),
                 str(sorted(it)))
        # prompt 与 render_prompt 逐字同源复算
        re_ok = all(render_prompt(x["query"], x["context"], role_card="",
                                  history=None) == x["prompt"] for x in items)
        ck.check("T3.11 prompt == render_prompt(...) 逐字同源", re_ok)

    # prepare 侧报告回写（题数/子集/allocator/prompt_mode 四项必写）
    if report.is_file():
        pr = json.loads(report.read_text(encoding="utf-8"))
        m = pr.get("metrics", {})
        ck.check("T3.12 prepare 报告回写 题数/子集/allocator/prompt_mode",
                 m.get("n_questions") == a.n
                 and isinstance(m.get("subset"), dict)
                 and m.get("allocator") == "v2_perblock"
                 and m.get("prompt_mode") == "compose_v1",
                 f"n={m.get('n_questions')} subset.mode="
                 f"{m.get('subset', {}).get('mode')} "
                 f"allocator={m.get('allocator')} pm={m.get('prompt_mode')}")
        ck.check("T3.13 prepare 报告含进窗块数统计（键名与 collect 侧同名）",
                 "n_blocks_in_window_mean" in m
                 and "n_zero_block_questions" in m,
                 f"mean={m.get('n_blocks_in_window_mean')} "
                 f"zero={m.get('n_zero_block_questions')}")

    print("T3c 注入合成回答后实跑 judge-prep（只验装配链路，不产真判读）")
    # 外部作答子代理在冒烟里不存在，注入显式标注的 smoke 回答把 judge-prep
    # 的装配链路真正跑通；这些 answer 不参与任何指标解释。
    ans_dir = state / "l3_answers"
    ans_dir.mkdir(parents=True, exist_ok=True)
    ans_items = [{"qid": x["qid"], "answer": f"[smoke-fixture] {x['query']}",
                  "smoke_fixture": True} for x in items]
    (ans_dir / "ans_b01.json").write_text(
        json.dumps({"items": ans_items}, ensure_ascii=False, indent=1),
        encoding="utf-8")
    rc3, out3 = _run_cli(["--mode", "judge-prep", "--state-dir", str(state),
                          "--reports-dir", str(rdir),
                          "--report-name", f"p4_harness_{tag}"], ROOT)
    ck.check("T3.14 judge-prep 退出码 0", rc3 == 0,
             f"rc={rc3} 尾部：{out3.strip()[-200:]}")
    jdg_in = state / "l3_judge_in"
    jdg_files = sorted(jdg_in.glob("jdg_in_b*.json")) if jdg_in.is_dir() else []
    ck.check("T3.15 判分批落独立子目录且与批次目录分离",
             bool(jdg_in.is_dir() and jdg_files)
             and jdg_in != (state / "l3_batches"),
             f"{len(jdg_files)} 个判分批 → {jdg_in.name}/")
    if jdg_files:
        j0 = json.loads(jdg_files[0].read_text(encoding="utf-8"))
        jitems = j0["items"] if isinstance(j0, dict) else j0
        ck.check("T3.16 判分批带口径标但不带 gold",
                 all(x.get("prompt_mode") == "compose_v1" for x in jitems)
                 and not any(k in x for x in jitems
                             for k in ("keywords", "ref", "set")),
                 f"{len(jitems)} 题")
        ck.check("T3.17 重跑幂等：旧判分批被清理",
                 len(jdg_files) == 1, f"{len(jdg_files)} 批（{len(items)} 题 < JUDGE_BATCH）")
    ck.check("T3.18 复评子集清单落 repeat_qids.json",
             (jdg_in / "repeat_qids.json").is_file())

    print("T3d 有 gold 但无 judge 产物时 collect 优雅降级（实跑）")
    rc2, out2 = _run_cli(["--mode", "collect", "--state-dir", str(state),
                          "--reports-dir", str(rdir),
                          "--report-name", f"p4_harness_{tag}"], ROOT)
    ck.check("T3b.1 collect 无判分不崩且显式标 DEGRADED",
             "[DEGRADED]" in out2 or "无判分产物" in out2,
             f"rc={rc2} 尾部：{out2.strip()[-160:]}")
    drep = rdir / f"p4_harness_{tag}.json"
    ck.check("T3b.2 降级路径仍写出报告", drep.is_file(), drep.name)
    if drep.is_file():
        dr = json.loads(drep.read_text(encoding="utf-8"))
        gm = dr.get("metrics", {})
        gd = {x["gate"].split()[0]: x["verdict"] for x in dr.get("gate_verdicts", [])}
        ck.check("T3b.3 无判分样本时 L3 gate 全 N/A（不误判 PASS/FAIL）",
                 gm.get("degraded") is True
                 and all(v == "N/A" for k, v in gd.items()
                         if k.startswith("L3.") and not k.startswith("L3.7")),
                 f"degraded={gm.get('degraded')} gates={gd}")
        ck.check("T3b.4 降级报告仍给并排两列幻觉率 + 进窗块数",
                 all(k in gm for k in ("hallucination_rate_in_window",
                                       "hallucination_rate_offscript_all",
                                       "n_blocks_in_window_mean")),
                 f"in_window={gm.get('hallucination_rate_in_window')} "
                 f"offscript_all={gm.get('hallucination_rate_offscript_all')} "
                 f"blocks_mean={gm.get('n_blocks_in_window_mean')}")
        ck.check("T3b.5 降级报告回写 artifact_scope（题数/子集/口径标）",
                 isinstance(dr.get("artifact_scope"), dict)
                 and dr["artifact_scope"].get("n_questions") == a.n
                 and dr["artifact_scope"].get("allocator") == "v2_perblock"
                 and dr["artifact_scope"].get("prompt_mode") == "compose_v1",
                 f"n={dr.get('artifact_scope', {}).get('n_questions')} "
                 f"subset={dr.get('artifact_scope', {}).get('subset', {}).get('mode')}")

    print("T3e 连 gold 都没有时 collect 明确报「无判分产物」（实跑）")
    empty_dir = base / f"p4_harness_{tag}_empty"
    empty_dir.mkdir(parents=True, exist_ok=True)
    rc4, out4 = _run_cli(["--mode", "collect", "--state-dir", str(empty_dir),
                          "--reports-dir", str(rdir),
                          "--report-name", f"p4_harness_{tag}_empty"], ROOT)
    ck.check("T3.19 缺 gold → 打印「无判分产物」且不抛栈",
             "无判分产物" in out4 and "Traceback" not in out4,
             f"rc={rc4} 尾部：{out4.strip()[-160:]}")

    print(f"\n冒烟 tag={tag}：PASS {len(ck.oks)} / FAIL {len(ck.fails)}")
    print(f"产物：{state}")
    print(f"      {report.parent / (report.name)}")
    if ck.fails:
        for f in ck.fails:
            print(f"  ! {f}")
    print("（本脚本只写不删：产物保留供人工核对，请由操作者自行清理）")
    return 1 if ck.fails else 0


if __name__ == "__main__":
    sys.exit(main())
