# -*- coding: utf-8 -*-
"""提交前校验 batch JSON（对应交接文档"校验要点已脚本化"）。

检查项：
  1. 零宽字符 / BOM / 非 UTF-8 可疑字符
  2. 畸形链式字段（正则归一 `"type":"角色":[""]` 这类）
  3. 实体名非空、type ∈ 六类、entities 内不重复
  4. relations 的 src/dst 必须出现在同块 entities 中
  5. relation 长度 2~6 汉字；confidence ∈ [0,1]
  6. evidence 非空且长度 ≤ 40 字
  7. key 与 dump 的 key 集合一致
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TYPES = {"角色", "组织", "地点", "物品", "概念", "事件"}
ZERO_WIDTH = re.compile(r"[\u200b-\u200f\u202a-\u202e\ufeff]")
MALFORMED = re.compile(r'"(?:type|name|src|dst)"\s*:\s*"[^"]*"\s*:')
HAN = re.compile(r"^[\u4e00-\u9fff]{2,6}$")


def main(path: str, dump: str | None = None) -> int:
    raw = Path(path).read_text(encoding="utf-8")
    errors: list[str] = []
    warnings: list[str] = []

    if raw.startswith("\ufeff"):
        errors.append("文件带 BOM")
    if MALFORMED.search(raw):
        errors.append("发现畸形链式字段（正则命中）")
    for m in ZERO_WIDTH.finditer(raw):
        errors.append(f"零宽字符 U+{ord(m.group()):04X} @ offset {m.start()}")
        break

    data = json.loads(raw)

    if dump:
        dump_keys = []
        for line in Path(dump).read_text(encoding="utf-8-sig").splitlines():
            line = line.strip()
            if line:
                dump_keys.append(json.loads(line)["key"])
        miss = [k for k in dump_keys if k not in data]
        extra = [k for k in data if k not in dump_keys]
        if miss:
            errors.append(f"dump 中未覆盖: {miss}")
        if extra:
            errors.append(f"多余 key: {extra}")

    total_e = total_r = 0
    for key, blk in data.items():
        if not re.fullmatch(r"[0-9a-f]{24}", key):
            errors.append(f"{key}: key 不是 24 位 hex（字段可能被串成链）")
        if set(blk.keys()) != {"entities", "relations"}:
            errors.append(f"{key}: 顶层字段异常 {sorted(blk.keys())}")

        seen: set[str] = set()
        for i, e in enumerate(blk.get("entities", [])):
            if set(e.keys()) - {"name", "type", "aliases", "desc"}:
                errors.append(f"{key}[e{i}]: 未知字段 {sorted(e.keys())}")
            n, t = e.get("name", ""), e.get("type", "")
            if not n.strip():
                errors.append(f"{key}[e{i}]: 实体名为空")
            if n in seen:
                errors.append(f"{key}: 实体重复 {n}")
            seen.add(n)
            if t not in TYPES:
                errors.append(f"{key}/{n}: 非法 type {t!r}")
            if not isinstance(e.get("aliases"), list):
                errors.append(f"{key}/{n}: aliases 不是数组")
            if n in (e.get("aliases") or []):
                warnings.append(f"{key}/{n}: 别名重复了本体名")
            if len(str(e.get("desc", ""))) > 30:
                warnings.append(f"{key}/{n}: desc 超 30 字")

        total_e += len(blk.get("entities", []))
        for i, r in enumerate(blk.get("relations", [])):
            if set(r.keys()) - {"src", "relation", "dst", "evidence", "confidence"}:
                errors.append(f"{key}[r{i}]: 未知字段 {sorted(r.keys())}")
            src, rel, dst = r.get("src", ""), r.get("relation", ""), r.get("dst", "")
            if not isinstance(rel, str) or not HAN.match(rel):
                errors.append(f"{key}: relation 非 2~6 汉字: {rel!r}")
            if src not in seen:
                errors.append(f"{key}: src 不在 entities: {src!r}")
            if dst not in seen:
                errors.append(f"{key}: dst 不在 entities: {dst!r}")
            if src == dst:
                warnings.append(f"{key}: 自环 {src} -{rel}-> {dst}")
            ev = r.get("evidence", "")
            if not ev:
                errors.append(f"{key}: evidence 为空 ({src}-{rel}->{dst})")
            elif len(ev) > 40:
                warnings.append(f"{key}: evidence 超 40 字: {ev[:20]}…")
            c = r.get("confidence")
            if not isinstance(c, (int, float)) or not 0.0 <= float(c) <= 1.0:
                errors.append(f"{key}: confidence 越界 {c!r}")
        total_r += len(blk.get("relations", []))

    print(f"块数 {len(data)}｜实体 {total_e}｜关系 {total_r}")
    for w in warnings:
        print(f"  [warn] {w}")
    if errors:
        print(f"\n✗ 校验失败，{len(errors)} 处错误：")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("\n✓ 校验通过")
    return 0


if __name__ == "__main__":
    p = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "_agent_batch54.json")
    if len(sys.argv) > 2:
        d = sys.argv[2]
    else:
        # 未显式给 dump 时按同号位自动配对；否则第 7 项会把**全部** key 误报为「多余 key」
        stem = Path(p).name.replace("_agent_batch", "_dump").replace(".json", ".txt")
        cand = ROOT / stem
        if cand.exists():
            d = str(cand)
            print(f"[自动配对 dump] {stem}")
        else:
            d = None
            print("[warn] 未找到同号位 dump，已跳过第 7 项 key 一致性校验")
    raise SystemExit(main(p, d))
