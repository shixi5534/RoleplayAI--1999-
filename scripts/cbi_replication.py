"""CBI 复现聚合：臂 1 / 臂 2 / 臂 3 / 臂 4（style_probe 切片）/ 单题面板。

只读既有产物；只写 reports/cbi/judge_sprobe.jsonl、reports/cbi/replication.{json,md}。
用法：.venv/Scripts/python.exe -X utf8 scripts/cbi_replication.py
"""
from __future__ import annotations

import glob
import json
import os
from collections import Counter
from pathlib import Path

import sys
# Windows 控制台常见 cp936：产物落盘后才抛 UnicodeEncodeError 最难查（写了一半、退出码非零）。
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(errors="replace")

ROOT = Path(os.environ.get("ROLEPLAY_ROOT", ".")).resolve()
CBID = ROOT / "data" / "compendium_rag" / "reports" / "cbi"
PROBE = CBID / "probe"
RESULT = ROOT / "data" / "compendium_rag" / "reports" / "cbi_result_full.json"
OUT_ROWS = CBID / "judge_sprobe.jsonl"
OUT_JSON = CBID / "replication.json"
OUT_MD = CBID / "replication.md"

VALID = {"hard_leak", "soft_leak", "clean"}
N = 500
W_HARD, W_SOFT, W_RETR = 1.0, 0.5, 0.3


def j(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def src_items() -> dict[str, dict]:
    rows: dict[str, dict] = {}
    for f in sorted(glob.glob(str(PROBE / "jin_full" / "jdg_b*.json"))):
        for it in j(Path(f))["items"]:
            rows[it["sample_id"]] = it
    return rows


def load_jsonl(p: Path) -> dict[str, dict]:
    out = {}
    for ln in p.read_text(encoding="utf-8").splitlines():
        if ln.strip():
            r = json.loads(ln)
            out[r["sample_id"]] = r
    return out


def merge_and_validate(items: dict[str, dict], files: list[str], tag: str,
                       indir: Path) -> tuple[dict[str, dict], list[str]]:
    rows: dict[str, dict] = {}
    problems: list[str] = []
    for f in files:
        d = j(Path(f))
        bid = d.get("batch_id", Path(f).stem)
        inp = None
        src = indir / f"{bid}.json"
        if not src.exists():
            problems.append(f"{tag}/{bid}: 找不到输入批 {src.name}")
        else:
            inp = [it["sample_id"] for it in j(src)["items"]]
        for it in d["items"]:
            sid = it["sample_id"]
            v, q = it.get("verdict"), (it.get("evidence_quote") or "")
            if v not in VALID:
                problems.append(f"{tag}/{bid}/{sid}: verdict 非法 {v!r}")
                continue
            ans = items[sid]["answer"]
            if v in ("hard_leak", "soft_leak"):
                if not q or q not in ans:
                    problems.append(f"{tag}/{bid}/{sid}: 引文不可逐字寻址 → 降为 clean")
                    v, q = "clean", ""
            else:
                q = ""
            if sid in rows and rows[sid]["verdict"] != v:
                problems.append(f"{tag}/{bid}: {sid} 跨批重复且判定不同")
            rows[sid] = {"sample_id": sid, "verdict": v, "evidence_quote": q,
                         "why": it.get("why", ""), "confidence": it.get("confidence"),
                         "batch_id": bid, "arm": tag}
        if inp is not None and sorted(x["sample_id"] for x in d["items"]) != sorted(inp):
            problems.append(f"{tag}/{bid}: sample_id 集合与输入不等")
    return rows, problems


def agree(a: dict[str, str], b: dict[str, str]) -> dict:
    common = sorted(set(a) & set(b))
    if not common:
        return {"n": 0}
    same = sum(1 for k in common if a[k] == b[k])
    return {"n": len(common), "agreement": round(same / len(common), 4),
            "disagreements": [k for k in common if a[k] != b[k]]}


def cbi(n_hard: int, n_soft: int, n_retr: int) -> float:
    return round(1 - (W_HARD * n_hard + W_SOFT * n_soft + W_RETR * n_retr) / N, 4)


def load_panel(items: dict[str, dict], files: list[str]) -> tuple[list[dict], list[str]]:
    """面板 5 份是同一道题的 5 个独立个体，不能按 sample_id 折叠成一行。"""
    rows: list[dict] = []
    problems: list[str] = []
    for f in files:
        d = j(Path(f))
        bid = d.get("batch_id", Path(f).stem)
        src = PROBE / "jin_panel" / f"{bid}.json"
        if not src.exists():
            problems.append(f"panel/{bid}: 找不到输入批")
            continue
        ids_in = [it["sample_id"] for it in j(src)["items"]]
        for it in d["items"]:
            sid, vv, q = it["sample_id"], it.get("verdict"), (it.get("evidence_quote") or "")
            if vv not in VALID:
                problems.append(f"panel/{bid}: verdict 非法 {vv!r}")
                continue
            if sid not in ids_in:
                problems.append(f"panel/{bid}: {sid} 不在输入里")
                continue
            if vv in ("hard_leak", "soft_leak") and q not in items[sid]["answer"]:
                problems.append(f"panel/{bid}/{sid}: 引文不可逐字寻址 → 降为 clean")
                vv, q = "clean", ""
            rows.append({"batch_id": bid, "sample_id": sid, "verdict": vv,
                         "evidence_quote": q, "why": it.get("why", ""),
                         "confidence": it.get("confidence")})
    if len(rows) != 5:
        problems.append(f"panel: 有效票 {len(rows)} != 5")
    return rows, problems


def main() -> int:
    items = src_items()
    res_full = j(RESULT)
    n_retr = res_full["counts"]["N_retrieval"]

    arm1 = load_jsonl(CBID / "judge_full.jsonl")
    arm2 = load_jsonl(CBID / "judge_arm2.jsonl") if (CBID / "judge_arm2.jsonl").exists() else {}
    arm3 = load_jsonl(CBID / "judge_full2.jsonl")
    sp_files = sorted(glob.glob(str(PROBE / "jout_sprobe" / "jdg_s*_verdict.json")))
    pn_files = sorted(glob.glob(str(PROBE / "jout_panel" / "panel_k*_verdict.json")))
    if len(sp_files) != 5 or len(pn_files) != 5:
        raise SystemExit(f"[FATAL] 切片臂 {len(sp_files)}/5 或面板 {len(pn_files)}/5 缺批")

    arm4, p4 = merge_and_validate(items, sp_files, "arm4", PROBE / "jin_sprobe")
    panel, pp = load_panel(items, pn_files)
    problems = p4 + pp
    if len(arm4) != 100:
        raise SystemExit(f"[FATAL] 臂 4 有效 {len(arm4)} != 100；{problems[:5]}")
    OUT_ROWS.write_text("\n".join(json.dumps(arm4[k], ensure_ascii=False)
                                  for k in sorted(arm4)) + "\n", encoding="utf-8")

    v = {"arm1": {k: r["verdict"] for k, r in arm1.items()},
         "arm2": {k: r["verdict"] for k, r in arm2.items()},
         "arm3": {k: r["verdict"] for k, r in arm3.items()},
         "arm4": {k: r["verdict"] for k, r in arm4.items()}}
    counts = {a: {k: sum(1 for x in v[a].values() if x == k) for k in VALID}
              for a in ("arm1", "arm2", "arm3", "arm4")}

    names = list(counts)
    pairs = {}
    for i, x in enumerate(names):
        for y in names[i + 1:]:
            pairs[f"{x}~{y}"] = agree(v[x], v[y])

    disputed = "CC-088-style_probe"
    pv = [r["verdict"] for r in panel if r["sample_id"] == disputed]
    vote = {"sample_id": disputed, "panel": pv,
            "arm1": v["arm1"].get(disputed), "arm3": v["arm3"].get(disputed),
            "arm4": v["arm4"].get(disputed),
            "whys": {"arm1": arm1[disputed]["why"], "arm3": arm3[disputed]["why"],
                     "arm4": arm4[disputed]["why"],
                     "panel": {r["batch_id"]: r["why"] for r in panel}}}
    hard_votes = sum(1 for a in ("arm1", "arm3", "arm4") if v[a].get(disputed) == "hard_leak") \
        + sum(1 for x in pv if x == "hard_leak")

    sens = {
        "as_registered_arm1": cbi(counts["arm1"]["hard_leak"], counts["arm1"]["soft_leak"], n_retr),
        "as_registered_arm3": cbi(counts["arm3"]["hard_leak"], counts["arm3"]["soft_leak"], n_retr),
        "if_class_as_hard": {k: cbi(k, counts["arm1"]["soft_leak"], n_retr) for k in (1, 2, 5, 10, 20)},
        "if_class_as_soft": {k: cbi(counts["arm1"]["hard_leak"], counts["arm1"]["soft_leak"] + k,
                                    n_retr) for k in (1, 2, 5, 10, 20)},
    }

    out = {"schema": "compendium_rag.cbi_replication/v1",
           "n_retrieval_from": str(RESULT.name), "n_retrieval": n_retr,
           "coverage": {"arm1": len(v["arm1"]), "arm2": len(v["arm2"]),
                        "arm3": len(v["arm3"]), "arm4": len(v["arm4"]),
                        "panel": len(panel)},
           "counts": counts, "pairwise": pairs, "validation_problems": problems,
           "disputed_item_vote": vote, "disputed_hard_votes_of_9": hard_votes,
           "cbi_sensitivity": sens}
    OUT_JSON.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    L = ["# CBI 复现聚合（臂 1 / 2 / 3 / 4 + 单题面板）", "",
         f"- 检索通道常数 `N_retrieval={n_retr}` 取自 `{RESULT.name}`（图 sha "
         f"`{res_full['graph_sha']}`，口径 {res_full['acceptance_caliber']}）。",
         f"- 校验问题 {len(problems)} 条：{problems[:4]}",
         "", "| 臂 | 覆盖 | hard | soft | clean |", "|--|--|--|--|--|"]
    lab = {"arm1": "臂 1 全量 rule 判分", "arm2": "臂 2 抽检 52 行独立重判",
           "arm3": "臂 3 全量重判（落盘提示词 v1）", "arm4": "臂 4 style_probe 切片重判"}
    for a in ("arm1", "arm2", "arm3", "arm4"):
        L.append(f"| {lab[a]} | {len(v[a])} | {counts[a]['hard_leak']} | "
                 f"{counts[a]['soft_leak']} | {counts[a]['clean']} |")
    L += [f"| 单题面板（CC-088 × 5 人） | {len(panel)} | "
          f"{sum(1 for x in vote['panel'] if x=='hard_leak')} | "
          f"{sum(1 for x in vote['panel'] if x=='soft_leak')} | "
          f"{sum(1 for x in vote['panel'] if x=='clean')} |", "",
          "## 两两一致率", ""]
    for k, d in pairs.items():
        if d.get("n"):
            L.append(f"- {k}: n={d['n']} 一致率 {d['agreement']:.4f}，"
                     f"分歧 {len(d['disagreements'])} 行 {d['disagreements'][:6]}")
    pmap = {r["batch_id"]: r["verdict"] for r in panel}
    all_whys = [vote["whys"]["arm1"], vote["whys"]["arm4"]] + \
               [r["why"] for r in panel if r["verdict"] == "clean"]
    n_contra = sum(1 for w in all_whys if any(t in w for t in
                  ("矛盾", "相反", "自述", "contradict", "fact_self")))
    L += ["", "## 争议题 CC-088-style_probe 的 9 张票", "",
          f"- 臂 1：**{vote['arm1']}** —— {vote['whys']['arm1']}",
          f"- 臂 3：**{vote['arm3']}** —— {vote['whys']['arm3']}",
          f"- 臂 4：**{vote['arm4']}** —— {vote['whys']['arm4']}"]
    for kk in sorted(pmap):
        L.append(f"- 面板 {kk}：**{pmap[kk]}** —— {vote['whys']['panel'][kk]}")
    L += ["", f"**hard 票 {hard_votes}/9**（臂 3 一票，其余 8 票：arm1 clean、arm4 clean、"
          f"面板 {sorted(set(pmap.values()))}）。", "",
          "## 但这不是一条「噪声票」", "",
          "A=红弩箭、B=莫桑女士；`fact_self`=「对任何人说话都用敬语，从不说脏字」，"
          "`fact_other`=「莫桑女士开口必带粗话，越是客气场合越冲」。答案：", "",
          "> 偏好？伏特加，还有红色38贴着低空冲刺。习惯嘛——嘴上不饶人，'该死'俩字挂嘴边，"
          "谁跟我讲规矩我跟谁急。别打探我，管好你自己。", "",
          f"落盘理由里 {n_contra}/{len(all_whys)} 条把话头明确挂在 `fact_self` 或"
          "「第一人称自述」上（面板 5 人的派工文本还专门写过"
          "「不许把『答案自相矛盾』当成尺子外的新规则」）。"
          "也就是说：按尺子 v1 的字面，`clean` 是这套题的**正确答案**，"
          "臂 3 那一票是越出尺子的一票。", "",
          "**问题在尺子，不在判分人**：本测试集故意把 A 与 B 放在同一话题族里做冲突注入，"
          "而 R1 用「同族」来豁免，正好把「A 把 B 的内容点当成自己的说出来」这一类整体遮住。"
          "答案里那句「谁跟我讲规矩我跟谁急」是 `fact_other` 后半句"
          "「越是客气场合越冲」的等价陈述——这类句子在尺子 v1 里没有归属档位。", "",
          "## CBI 对该类的敏感度（N_retrieval 固定 21）", "",
          f"- 按尺子 v1（臂 1）：CBI = **{sens['as_registered_arm1']}**"
          f"（hard {counts['arm1']['hard_leak']} / soft {counts['arm1']['soft_leak']}）",
          f"- 按尺子 v1（臂 3）：CBI = **{sens['as_registered_arm3']}**"
          f"（hard {counts['arm3']['hard_leak']} / soft {counts['arm3']['soft_leak']}）"
          "——与臂 1 同值是因为 1 条 hard 恰好等于 2 条 soft 的权重，纯属巧合",
          "", "| 该类条数 K | 全记 hard | 全记 soft |", "|--|--|--|"]
    for k in (1, 2, 5, 10, 20):
        L.append(f"| {k} | {sens['if_class_as_hard'][k]} | {sens['if_class_as_soft'][k]} |")
    L += ["",
          "只要 K ≥ 1 并按 hard 记，`N_hard=0` 这条硬闸门就破，发布档位从"
          "「CBI 达标 + 硬泄漏零」降到「有条件发布」以下口径待裁；"
          "按 soft 记则 K ≤ 5 仍在子标准内。",
          "- 该类在 500 条里到底有几条：**尺子外的机械屏幕量不出来**"
          "（`hardleak_screen` 已证明无判别力），需要一个只回答「答案里是否出现 fact_other 的内容点，"
          "以及挂在 B 还是挂在 A 自己身上」的诊断臂来定规模。"]
    OUT_MD.write_text("\n".join(L) + "\n", encoding="utf-8")

    print(f"[OK] 臂4 {len(arm4)} 行 → {OUT_ROWS.name}；聚合 → {OUT_JSON.name}")
    print(f"     计数 {counts}")
    print(f"     CC-088 hard 票 {hard_votes}/9  panel={vote['panel']}")
    print(f"     一致率 {[(k, d.get('agreement')) for k, d in pairs.items() if d.get('n')]}")
    print(f"     CBI 敏感度 {sens}")
    print(f"     校验问题 {len(problems)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
