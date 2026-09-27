# -*- coding: utf-8 -*-
"""验证：R4 是否可从 prev.r4 重放复现冻结图 c021f0a0bc7a0dce？

发现（2026-09-27 晚 #39）：
  repairs_v4/proposal.json 的 R4-K01 被第二会话从 keep_with_note 改成 remove_alias
  并追加 arbitration「采纳 Verifier remove 方案」，但**没有 alias 字段**
  （target 是裸字符串 '诊所'）-> Applier 的 _alias() 返回 None
  -> 预检报「alias 不在属主别名表: None@诊所」-> 全图 fail-closed 不写盘。
  实测 live 图里 诊所.aliases 仍含 '诊疗'，且实际只摘了 77 条（994->917），
  而提案声称 78 条 -> **R4 的重放链路已断**。

本脚本在临时副本上分别测试：
  A) 现状提案（K01=remove_alias 无 alias 字段）
  B) 把 K01 还原为 keep_with_note（NOOP）
比较谁能在 prev.r4 基础上复现冻结 SHA。
"""
from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRATCH = ROOT / "_r4replay"


def sha16(p: Path) -> str:
    import hashlib
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def run_applier(prop_path: Path) -> tuple[int, str]:
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts/_graph_apply_repairs.py"),
         "--graph", str(SCRATCH / "graph.json"),
         "--proposal", str(prop_path),
         "--apply", "--version-tag", "replay"],
        capture_output=True, cwd=ROOT)
    out = (r.stdout + r.stderr).decode("utf-8", "replace")
    return r.returncode, out


def prepare() -> None:
    if SCRATCH.exists():
        shutil.rmtree(SCRATCH)
    SCRATCH.mkdir()
    prev = subprocess.run(["git", "show", "HEAD:data/compendium_rag/backups/graph.json.prev.r4"],
                          capture_output=True, cwd=ROOT).stdout
    (SCRATCH / "graph.json").write_bytes(prev)


def main() -> int:
    FROZEN = "c021f0a0bc7a0dce"
    print(f"目标：从 prev.r4 重放 R4，应得到 {FROZEN}\n")

    prop = json.loads((ROOT / "data/compendium_rag/repairs_v4/proposal.json").read_text(encoding="utf-8"))

    # A) 现状
    prepare()
    rc, out = run_applier(ROOT / "data/compendium_rag/repairs_v4/proposal.json")
    print(f"[A] 现状提案：rc={rc}")
    print("    " + "\n    ".join(l for l in out.splitlines() if "预检错误" in l or "FAIL" in l or "APPLIED" in l)[:400])
    a_sha = sha16(SCRATCH / "graph.json") if (SCRATCH / "graph.json").exists() else "n/a"
    print(f"    结果 SHA16 = {a_sha}  {'== 冻结' if a_sha == FROZEN else '!= 冻结（A 未能复现）'}\n")

    # B) K01 还原为 NOOP
    prepare()
    prop2 = copy.deepcopy(prop)
    for e in prop2["entries"]:
        if e.get("id") == "R4-K01":
            e["type"] = "keep_with_note"
    p2 = SCRATCH / "proposal_b.json"
    p2.write_text(json.dumps(prop2, ensure_ascii=False, indent=2), encoding="utf-8")
    rc2, out2 = run_applier(p2)
    print(f"[B] K01 还原为 keep_with_note：rc={rc2}")
    print("    " + "\n    ".join(l for l in out2.splitlines() if "预检错误" in l or "FAIL" in l or "APPLIED" in l or "实体:" in l)[:400])
    b_sha = sha16(SCRATCH / "graph.json")
    print(f"    结果 SHA16 = {b_sha}  {'== 冻结 ✓（重放链路恢复）' if b_sha == FROZEN else '!= 冻结'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
