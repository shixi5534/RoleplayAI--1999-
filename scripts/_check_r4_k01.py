# -*- coding: utf-8 -*-
"""核查 R4-K01（诊所/诊疗）仲裁记录与实际图状态是否一致。

背景：R4 提案的 R4-K01 原为 keep_with_note；本会话（第二会话）在
repairs_v4/proposal.json 里把它改成 remove_alias 并追加 arbitration
「采纳 Verifier remove 方案」。但该条**没有 alias 字段**（target 是裸字符串
'诊所'），故 Applier 的 _alias() 返回 None -> 报「alias 不在属主别名表: None@诊所」。
需查清：诊疗@诊所 究竟是否在图上被摘除。
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def aliases_of(obj, eid):
    for e in obj.get("entities", []):
        if e["eid"] == eid:
            return e.get("aliases") or []
    return None


def main() -> int:
    live = json.loads((ROOT / "data/compendium_rag/graph.json").read_text(encoding="utf-8"))
    prev_r4 = json.loads(subprocess.run(
        ["git", "show", "HEAD:data/compendium_rag/backups/graph.json.prev.r4"],
        capture_output=True, cwd=ROOT).stdout.decode("utf-8"))

    print("=== 实体「诊所」的别名 ===")
    print("  live          :", aliases_of(live, "诊所"))
    print("  prev.r4(前R4) :", aliases_of(prev_r4, "诊所"))

    # alias_index 归属
    def build_ai(g):
        ai = {}
        for e in g["entities"]:
            ai[e["name"]] = e["eid"]
            for a in (e.get("aliases") or []):
                ai.setdefault(a, e["eid"])
        return ai
    ai_live, ai_prev = build_ai(live), build_ai(prev_r4)
    print()
    print("=== alias_index['诊疗'] ===")
    print("  live          :", ai_live.get("诊疗", "(不存在)"))
    print("  prev.r4(前R4) :", ai_prev.get("诊疗", "(不存在)"))

    # 提案里 R4-K01 的结构
    prop = json.loads((ROOT / "data/compendium_rag/repairs_v4/proposal.json").read_text(encoding="utf-8"))
    k01 = [e for e in prop["entries"] if e.get("id") == "R4-K01"]
    print()
    print("=== R4-K01 提案结构 ===")
    if k01:
        e = k01[0]
        print("  type   :", e.get("type"))
        print("  target :", repr(e.get("target")))
        print("  alias  :", repr(e.get("alias")))
        print("  -> _owner() =", e.get("target") if isinstance(e.get("target"), str) else (e.get("target") or {}).get("owner_eid"))
        print("  -> _alias() = None  （target 是裸字符串且无顶层 alias 字段）"
              if not isinstance(e.get("target"), dict) and not e.get("alias") else "")

    # 统计：提案 78 条 remove_alias 中，真正可解析出 (owner, alias) 的有多少
    bad = []
    for e in prop["entries"]:
        if e.get("type") != "remove_alias":
            continue
        t = e.get("target")
        if isinstance(t, dict):
            if not (t.get("owner_eid") and t.get("alias")):
                bad.append(e.get("id"))
        elif not (isinstance(t, str) and e.get("alias")):
            bad.append(e.get("id"))
    print()
    print(f"=== 78 条 remove_alias 中无法解析 (owner, alias) 的条目: {bad or '无'} ===")

    # 别名总数对账
    def total(g):
        return sum(len(e.get("aliases") or []) for e in g["entities"])
    print(f"  别名总数 prev.r4={total(prev_r4)} -> live={total(live)}  差={total(prev_r4) - total(live)}")
    print(f"  提案 remove_alias 条数={sum(1 for e in prop['entries'] if e.get('type') == 'remove_alias')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
