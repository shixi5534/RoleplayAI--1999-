# -*- coding: utf-8 -*-
"""把 R4-K01 从 remove_alias 还原为 keep_with_note，并如实记录「仲裁未落盘」。

背景（2026-09-27 晚 #39 核验）：
  R4-K01 曾被改为 remove_alias 并追加仲裁文本，但缺 alias 字段（target 是裸字符串），
  Applier 的 _alias() 返回 None -> 预检失败 -> **全图 fail-closed**，
  导致 R4 从 prev.r4 完全无法重放（rc=1）。
  实测 live 图未摘除 诊疗@诊所，别名总数只减 77（提案 78 条）—— 故实际语义即 NOOP。

本脚本只改这一条：type -> keep_with_note，并补 arbitration_status / not_applied_note。
改后须能用 _check_r4_replay.py 逐字节复现冻结 SHA c021f0a0bc7a0dce。
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "data/compendium_rag/repairs_v4/proposal.json"

NOTE = (
    "该仲裁**未落盘**。第二会话曾把本条 type 改为 remove_alias 并追加仲裁文本，"
    "但 target 是裸字符串且无 alias 字段 -> Applier 的 _alias() 返回 None -> "
    "预检报「alias 不在属主别名表: None@诊所」-> 全图 fail-closed 不写盘。实测："
    "(a) live 图 诊所.aliases 仍为 ['工坊','诊疗']（未摘除）；"
    "(b) 别名总数 994->917 即摘 77 条，而提案含 78 条 remove_alias；"
    "(c) 从 prev.r4 重放，本条为 remove_alias 时 rc=1 且写不出图，"
    "还原为 keep_with_note 时可**逐字节复现冻结 SHA c021f0a0bc7a0dce**。"
    "故 R4 实际落盘语义 = 本条 NOOP。为恢复重放链路，本条还原为 keep_with_note；"
    "是否真正执行摘除（需重跑 GA-25 闸门并产生新 SHA，进而影响 BASELINE_v4 冻结值）"
    "留待用户裁决。"
)


def main() -> int:
    raw = P.read_bytes()
    doc = json.loads(raw.decode("utf-8"))
    n = 0
    for e in doc["entries"]:
        if e.get("id") == "R4-K01":
            e["type"] = "keep_with_note"
            e["after"] = "保留（未摘除）。图现状：诊所.aliases 仍含 '诊疗'，alias_index['诊疗']=诊所"
            e["arbitration_status"] = "NOT-APPLIED（2026-09-27 晚 #39 核验发现）"
            e["not_applied_note"] = NOTE
            e["replay_verified"] = ("scripts/_check_r4_replay.py：keep_with_note 下从 prev.r4 "
                                    "重放 -> c021f0a0bc7a0dce（= BASELINE_v4 graph_live 锁定值）")
            n += 1
    assert n == 1, f"R4-K01 定位失败（n={n}）"

    # 该文件的历史格式是 indent=1 + CRLF + 无尾随换行；
    # 必须逐字节对齐，否则整文件重排会产生 4000 行伪 diff（实测 indent=2 会）。
    body = json.dumps(doc, ensure_ascii=False, indent=1)
    body = body.replace("\r\n", "\n").replace("\n", "\r\n").rstrip("\r\n")
    P.write_bytes(body.encode("utf-8"))
    print(f"[ok] R4-K01 -> keep_with_note；写入 {P.name}")
    print(f"     remove_alias 条数 = {sum(1 for e in doc['entries'] if e.get('type') == 'remove_alias')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
