# -*- coding: utf-8 -*-
"""vendor 词表漂移检查（P1/D1 配套，**只报告不自动改**）。

compendium_rag 因独立性契约（``config.py:4-6``）不能 import roleplay.*，
受控词表以 vendor 副本落地。副本最大的风险是**悄悄过期**：上游
``roleplay/core/knowledge/relation_vocab.py`` 改了 canonical 或同义词表，
这边还在用老表归一化，于是两张图用两套口径却无人察觉。

判定分两层，避免假警：

1. 逐字节相同 → 无漂移，直接收工；
2. 不同 → 按 **ast 静态取值**比对可执行语义（canonical 集合、两张同义词表、
   黑名单、超长阈值、正则模式），只有语义真的不同才报漂移。
   纯注释/文档改动落在第 2 层的「语义等价」里，不惊动。

退出码：0 无漂移 / 1 有漂移 / 2 读不出来（表结构变了，得手工看）。

用法::

    .venv/Scripts/python.exe -X utf8 scripts/compendium_rag_vocab_drift.py
"""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENDORED = ROOT / "src" / "compendium_rag" / "relation_vocab.py"
UPSTREAM = ROOT / "src" / "roleplay" / "core" / "knowledge" / "relation_vocab.py"
MANIFEST = ROOT / "src" / "compendium_rag" / "relation_vocab.vendor.json"
REPORT = ROOT / "data" / "compendium_rag" / "reports" / "p1_vocab_drift.json"

# 归一化行为完全由这几样决定；其余（说明文字、提示词模板）不影响判定结果
NAMES = ("CANONICAL_RELATIONS", "SYNONYM_MAP", "SYNONYM_MAP_EXT",
         "JUNK_BLACKLIST", "MAX_RELATION_LEN")
REGEXES = ("_NEG_RE", "_PUNCT_RE", "_LATIN_RE", "_PASSIVE_PREFIX_RE",
           "_TAIL_SUFFIX_RE")


def _sha16(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def _literal(node: ast.AST):
    """把 ``NAME = <expr>`` 的右式求成 Python 值；只认字面量与单层容器构造。"""
    if isinstance(node, ast.Call):
        fname = getattr(node.func, "id", "")
        if fname in ("frozenset", "tuple", "list", "set") and len(node.args) == 1:
            inner = _literal(node.args[0])
            return {"frozenset": frozenset, "tuple": tuple, "list": list,
                    "set": set}[fname](inner)
        return None
    if isinstance(node, (ast.BinOp,)):          # 元组/集合拼接
        left, right = _literal(node.left), _literal(node.right)
        if left is None or right is None:
            return None
        if isinstance(left, tuple):
            return left + tuple(right)
        if isinstance(left, (set, frozenset)):
            return type(left)(set(left) | set(right))
        if isinstance(left, dict):
            return {**left, **right}
        return None
    try:
        return ast.literal_eval(node)
    except (ValueError, TypeError, SyntaxError):
        return None


def _extract(path: Path) -> tuple[dict, dict, list[str]]:
    """→ (常量值, 正则模式串, 取不出值的名字列表)。"""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    vals: dict[str, object] = {}
    pats: dict[str, str] = {}
    failed: list[str] = []
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        tgt = node.targets[0]
        if not isinstance(tgt, ast.Name):
            continue
        name = tgt.id
        if name in NAMES:
            v = _literal(node.value)
            if v is None:
                failed.append(name)
            else:
                vals[name] = v
        elif name in REGEXES and isinstance(node.value, ast.Call) \
                and getattr(node.value.func, "id", "") == "compile":
            first = node.value.args[0] if node.value.args else None
            if isinstance(first, (ast.Constant, ast.JoinedStr)):
                lit = _literal(first)
                if isinstance(lit, str):
                    pats[name] = lit
    return vals, pats, failed


def _summ(v) -> dict:
    """语义摘要：集合类给成员，标量给值。diff 也按这个粒度报。"""
    if isinstance(v, dict):
        return {"kind": "dict", "size": len(v), "items": {str(k): str(x) for k, x in v.items()}}
    if isinstance(v, (set, frozenset, tuple, list)):
        return {"kind": type(v).__name__, "size": len(v), "items": sorted(map(str, v))}
    return {"kind": "scalar", "value": str(v)}


def main() -> int:
    rep: dict = {
        "schema": "compendium_rag.p1_vocab_drift/v1",
        "note": "只读：比对 vendor 副本与上游词表，不写任何一侧",
        "vendored": str(VENDORED.relative_to(ROOT)),
        "upstream": str(UPSTREAM.relative_to(ROOT)),
        "sha256_16": {"vendored": _sha16(VENDORED), "upstream": _sha16(UPSTREAM)},
    }
    if MANIFEST.exists():
        m = json.loads(MANIFEST.read_text(encoding="utf-8"))
        rep["manifest"] = {"source_commit": m.get("source_commit"),
                           "vendored_at": m.get("vendored_at"),
                           "recorded_sha256_source": (m.get("sha256_source") or "")[:16],
                           "recorded_sha256_vendored": (m.get("sha256_vendored") or "")[:16]}
    if not (VENDORED.exists() and UPSTREAM.exists()):
        rep["verdict"] = "UNREADABLE"
        rep["reason"] = "任一侧词表文件缺失"
        print(json.dumps(rep, ensure_ascii=False, indent=2))
        return 2

    if rep["sha256_16"]["vendored"] == rep["sha256_16"]["upstream"]:
        rep["verdict"] = "IDENTICAL"
        rep["semantic"] = "byte-for-byte"
    else:
        vv, vp, vf = _extract(VENDORED)
        uv, up, uf = _extract(UPSTREAM)
        if vf or uf or set(vv) != set(uv):
            rep["verdict"] = "UNREADABLE"
            rep["reason"] = ("常量结构无法静态求值，需人工核对"
                             f"（取不出：vendored={vf} upstream={uf}）")
            print(json.dumps(rep, ensure_ascii=False, indent=2))
            return 2
        diffs = {}
        for name in NAMES:
            a, b = _summ(vv[name]), _summ(uv[name])
            if a != b:
                sa, sb = set(a.get("items", [])), set(b.get("items", []))
                diffs[name] = {"only_vendored": sorted(sa - sb)[:60],
                               "only_upstream": sorted(sb - sa)[:60],
                               "changed_items": {k: {"vendored": a["items"][k],
                                                     "upstream": b["items"][k]}
                                                 for k in sa & sb
                                                 if a["items"][k] != b["items"][k]}
                               if a["kind"] == "dict" and b["kind"] == "dict" else {},
                               "size": [a.get("size") or a.get("value"),
                                        b.get("size") or b.get("value")]}
        for name in REGEXES:
            if vp.get(name) != up.get(name):
                diffs[name] = {"vendored": vp.get(name), "upstream": up.get(name)}
        rep["verdict"] = "SEMANTIC_EQUAL" if not diffs else "DRIFT"
        rep["text_differs"] = True
        rep["semantic_diffs"] = diffs

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in rep.items()
                      if k not in ("semantic_diffs",)}, ensure_ascii=False, indent=2))
    if rep["verdict"] == "DRIFT":
        print("漂移明细（截断到每项 60 条）→", json.dumps(
            rep["semantic_diffs"], ensure_ascii=False)[:2000])
    print(f"报告 → {REPORT}")
    return {"IDENTICAL": 0, "SEMANTIC_EQUAL": 0, "DRIFT": 1}.get(rep["verdict"], 2)


if __name__ == "__main__":
    raise SystemExit(main())
