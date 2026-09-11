# -*- coding: utf-8 -*-
"""幂等刷新台词集：先移除旧块，再重新导入，避免重复条目。

向量库没有按来源删除的接口，所以直接操作落盘 JSON 过滤，再走标准 ingest。

用法（项目根目录）：
  python scripts/refresh_voice_lore.py
  python scripts/refresh_voice_lore.py --verify   # 导入后跑检索验收
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

KB_FILE = ROOT / "data" / "knowledge" / "lore_wu_ming_zhe.json"
LORE_FILE = ROOT / "data" / "lore" / "wu_ming_zhe" / "角色语音台词集.md"
MARK = "角色语音台词集"


def remove_old() -> int:
    if not KB_FILE.is_file():
        print(f"[warn] 知识库文件不存在：{KB_FILE}")
        return 0
    shutil.copy(KB_FILE, KB_FILE.with_suffix(".json.bak_voicelore"))
    data = json.load(open(KB_FILE, encoding="utf-8"))

    def is_voice(x: dict) -> bool:
        blob = json.dumps(x.get("meta") or {}, ensure_ascii=False) + x.get("text", "")
        return MARK in blob

    keep = [x for x in data if not is_voice(x)]
    removed = len(data) - len(keep)
    json.dump(keep, open(KB_FILE, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"[clean] {len(data)} → {len(keep)}（移除 {removed} 块）")
    return removed


def ingest() -> None:
    py = ROOT / ".venv" / "Scripts" / "python.exe"
    if not py.is_file():
        py = Path(sys.executable)
    r = subprocess.run(
        [str(py), str(ROOT / "scripts" / "ingest_lore.py"),
         "--character", "wu_ming_zhe", "--file", str(LORE_FILE)],
        cwd=str(ROOT), capture_output=True, text=True,
        encoding="utf-8", errors="replace")
    print(r.stdout.strip() or r.stderr.strip())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true", help="导入后跑检索验收")
    a = ap.parse_args()

    remove_old()
    ingest()
    if a.verify:
        py = ROOT / ".venv" / "Scripts" / "python.exe"
        r = subprocess.run([str(py), str(ROOT / "scripts" / "verify_voice_lore.py")],
                           cwd=str(ROOT), capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        print(r.stdout.strip() or r.stderr.strip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
