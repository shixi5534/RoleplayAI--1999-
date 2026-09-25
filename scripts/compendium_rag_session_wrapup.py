# -*- coding: utf-8 -*-
"""§7 标准收尾流程一键化(交接文档 §7 的九步)。

**抽取期间禁止运行**(铁律 5)。默认只做 dry-run 打印;确认无子代理在抽取时才加 --run。

用法(项目根目录):
    python scripts/compendium_rag_session_wrapup.py            # dry-run,列出将要执行的步骤
    python scripts/compendium_rag_session_wrapup.py --run      # 全流程:备份→rebuild→索引→回填→评测→实测
    python scripts/compendium_rag_session_wrapup.py --run --skip-index   # 跳过本地 Ollama 索引重建
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/compendium_rag"
PY = str(ROOT / ".venv/Scripts/python.exe")
ENV = {"PYTHONPATH": "src", "PYTHONIOENCODING": "utf-8"}


def _run(desc, args, cwd=None):
    print(f"\n=== {desc}\n$ {' '.join(args)}", flush=True)
    r = subprocess.run(args, cwd=str(cwd or ROOT), env={**subprocess.os.environ, **ENV})
    if r.returncode != 0:
        print(f"!! 退出码 {r.returncode}: {desc}", flush=True)
    return r.returncode


def backup():
    for f in ("graph.json", "reports/build_report.json"):
        src = DATA / f
        if src.exists():
            shutil.copy2(src, src.with_suffix(src.suffix + ".prev"))
    for npz in DATA.glob("*.npz"):
        shutil.copy2(npz, Path(str(npz) + ".prev"))
    print("已备份 graph.json / build_report.json / *.npz → *.prev")


def sync_report_graph():
    g = json.loads((DATA / "graph.json").read_text(encoding="utf-8"))
    rp = DATA / "reports/build_report.json"
    r = json.loads(rp.read_text(encoding="utf-8"))
    r["graph"] = {"entities": len(g["entities"]),
                  "edges": len(g.get("edges", []))}
    rp.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"build_report.graph ← {r['graph']}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true", help="真正执行(默认 dry-run)")
    ap.add_argument("--skip-index", action="store_true", help="跳过向量索引重建(不触本地 Ollama)")
    ap.add_argument("--from-slot", type=int, default=247,
                    help="本会话并发起始号位(证据区间核对 + 并发专项审计都用它)")
    ap.add_argument("--to-slot", type=int, default=610,
                    help="本会话最大号位(并发派单会不断往后扩;第 18 会话尾已派到 601)")
    a = ap.parse_args()

    S = str(a.from_slot)
    T = str(a.to_slot)
    steps = [
        ("0) 备份 *.prev", None),
        ("0b) ★ 证据逐字核对(号位区间)", [PY, "data/compendium_rag/_verify_evidence_range.py", S, T]),
        ("0c) ★ 落地模拟(号位区间,需改写 0)", [PY, "data/compendium_rag/_gen_newnames_range.py", S, T]),
        ("0d) ★ 提交完整性/死代理核对(号位区间)",
         [PY, "data/compendium_rag/_verify_submitted_range.py", S, T]),
        ("0e) ★ 并发重复抽取的分裂命名审计(是**清单**不是零闸:逐条留待 rebuild 后 resolve() 裁定)",
         [PY, "data/compendium_rag/_audit_global_key_collisions.py", S, T]),
        ("1) 建图 rebuild(零网络)", [PY, "-m", "compendium_rag.cli", "rebuild"]),
        ("2) 重建向量索引(本地 Ollama bge-m3)", [PY, "scripts/compendium_rag_rebuild_indexes.py"]),
        ("3) 回填 build_report.graph", None),
        ("4) 评测 13 题双模式", [PY, "scripts/compendium_rag_eval.py", "6"]),
        ("5) 一致性核验 stats", [PY, "-m", "compendium_rag.cli", "stats"]),
        ("6) ★ 归并声明 resolve() 实测(第 9 会话专项)", [PY, "data/compendium_rag/_verify_session9.py"]),
        ("6b) ★ 本区间全部 name/alias 落盘实测", [PY, "data/compendium_rag/_verify_decls_range.py", S]),
        ("7) 进度快照 + 按版本清单", [PY, "data/compendium_rag/_progress_snapshot.py"]),
        ("7b) 按版本清单", [PY, "data/compendium_rag/_progress_by_version.py"]),
        ("8) 交接完整性审计", [PY, "data/compendium_rag/_audit_handoff.py"]),
        ("8b) ★ 并发批次专项审计(B 禁用裸名=硬闸;A/C 为清单)", [PY, "data/compendium_rag/_audit_concurrent_batches.py", S]),
        ("8c) ★ 分裂命名 resolve() 实测裁定(现场重跑碰撞审计取全量独有集)",
         [PY, "data/compendium_rag/_adjudicate_splits.py", "--fresh", S, T]),
        ("9) 手工更新交接文档 §0/附录索引", None),
    ]
    if not a.run:
        print("dry-run —— 将要执行的步骤(确认无子代理在抽取后加 --run)：")
        for d, _ in steps:
            print("  " + d)
        return 0

    backup()
    for desc, cmd in steps:
        if cmd is None:
            continue
        if a.skip_index and "索引" in desc:
            print(f"\n--- 跳过 {desc}(--skip-index)")
            continue
        _run(desc, cmd)
        if desc.startswith("1)"):
            sync_report_graph()
    print("\n收尾九步执行完毕。请核对：指纹 OK｜entity_index==graph.entities｜"
          "hit@k≥0.85｜孤立率<0.5｜归并实测 100% 通过｜并发审计 A/B/C 无问题。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
