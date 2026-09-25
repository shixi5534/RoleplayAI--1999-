# -*- coding: utf-8 -*-
"""落盘后归并声明实测(可复用,按号位区间):
    python _verify_decls_range.py <起始号位> [结束号位]

必须在 rebuild **之后**跑。逐条实测每个号位里声明的 name 与 alias:
  N1  name 必须 resolve 到自身(未被别的组吸走) —— 红线 1 的落盘复核
  N2  alias 必须 resolve 到它声明时所依附的 name —— 红线 3 / §4.11
  N3  alias 若同时是**他组**的成员名 → resolve 必为 None(§4.11 缺陷),单列报告
与 _verify_batch_merge.py 的区别:那个是 rebuild 前的预演,这个是落盘后的实测。

⚠ **只实测真正进图的那批声明**:submit 是整块覆盖,同一 key 被多个号位抽过时,
落败号位的 batch 文件是**死草稿**——其 name 本就不会进图,拿它判失败是假阳性。
故每条声明先与 `cache/<key>` 的现值逐字段比对,不等者计入「已覆盖草稿」并**如实报数**。
N1/N2/滞后 = 致命;N3(§4.11 缺陷)按本文档口径**单列报告**、不判失败。

⚠ N1 里 `resolve=None` 有**两种完全不同的成因**,必须分开:
  - **归一化层刻意丢弃**:`src/compendium_rag/extract.py::normalize` 会丢掉
    超长名(>MAX_NAME_CHARS=16)、泛称说话人、`is_noise_name` 命中的描述性短语,
    并用 `_norm_name` **改写**首尾带引号/括号的名字 —— 这类 name 根本不进图,
    属**设计内去噪**,要处置的是生成器里的写法(改短、去首尾引号),不是图;
  - **真·落盘失效**:既没被改写也没被规则丢弃,却仍 resolve 不到 → 需人工查。
本脚本对每条 N1(None) 现场跑同一套谓词给出 `成因=` 标签,无人工不可判的项归
`原因未明(需人工)`。**不改 src,只 import 其谓词做只读复算。**
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent / "src"))
from compendium_rag.graph_store import GraphStore      # noqa: E402
from compendium_rag.corpus import is_generic_speaker   # noqa: E402
from compendium_rag.extract import (                   # noqa: E402
    MAX_NAME_CHARS, _norm_name, is_noise_name)


def drop_cause(nm: str, typ: str, persons: set[str]) -> str:
    """复算 normalize() 的丢弃/改写判据,返回人话成因;'' 表示规则不该丢。"""
    nn = _norm_name(nm)
    if nn != nm:
        return f"写法被 _norm_name 改写为「{nn}」"
    if len(nn) > MAX_NAME_CHARS:
        return f"超长({len(nn)}>{MAX_NAME_CHARS})被丢"
    if is_generic_speaker(nn):
        return "泛称说话人被丢"
    if is_noise_name(nn, typ):
        return "is_noise_name 命中(描述性短语/句子复述)被丢"
    if typ == "事件" and any(p and len(p) < len(nn) and nn.startswith(p)
                             for p in persons):
        return "事件名以本块角色名开头 → 按动作复述被丢"
    return ""


def _canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False)


def _live_block(key: str, blk: dict):
    """返回 (状态, 现值块)。状态 ∈ {live, overwritten, absent}"""
    p = ROOT / "cache" / key[:2] / f"{key}.json"
    if not p.exists():
        return "absent", None
    raw = (json.loads(p.read_text(encoding="utf-8")) or {}).get("raw") or {}
    cur = {k: raw.get(k) for k in ("entities", "relations")}
    return ("live" if _canon(cur) == _canon(blk) else "overwritten"), cur


def _slot(p: Path) -> int | None:
    m = re.fullmatch(r"_agent_batch(\d+)", p.stem)
    return int(m.group(1)) if m else None          # 注意:仓库内有 _agent_batch52b.json 这类带字母号位


def main(lo: int, hi: int | None) -> int:
    g = GraphStore.load(ROOT / "graph.json")
    files = sorted((p for p in ROOT.glob("_agent_batch*.json")
                    if (s := _slot(p)) is not None and lo <= s <= (hi or 10**9)),
                   key=_slot)
    if not files:
        print(f"号位区间 {lo}–{hi} 无 batch 文件")
        return 1

    absorbed, dropped, unexplained = [], [], []          # name 侧三分类
    alias_bad, alias_listed, alias_unknown = [], [], []  # alias 侧三分类
    cause_cnt = {}
    skipped = {"overwritten": 0, "absent": 0}
    n_names = n_alias = n_blocks = 0
    for p in files:
        slot = _slot(p)
        data = json.loads(p.read_text(encoding="utf-8"))
        for key, blk in data.items():
            st, cur = _live_block(key, blk)
            if st != "live":
                skipped[st] += 1
                continue
            n_blocks += 1
            ents = (cur or {}).get("entities", [])
            persons = {_norm_name(e["name"]) for e in ents
                       if e.get("type") == "角色" and e.get("name")}
            for e in ents:
                nm = e["name"]
                n_names += 1
                r = g.resolve(nm)
                if r == nm:
                    pass
                elif r is not None:
                    absorbed.append((slot, nm, r))       # 真红线 1:被别的组吸走
                else:
                    c = drop_cause(nm, e.get("type", ""), persons)
                    if c:
                        cause_cnt[c] = cause_cnt.get(c, 0) + 1
                        dropped.append((slot, nm, c))    # 设计内去噪:登记,待改写法
                    else:
                        unexplained.append((slot, nm, e.get("type", "")))
                for al in e.get("aliases", []):
                    n_alias += 1
                    ra = g.resolve(al)
                    if ra is None:
                        c = drop_cause(al, e.get("type", ""), persons)
                        row = (slot, al, nm, c or "§4.11 成员名被抹除/未进图")
                        (alias_listed if c else alias_unknown).append(row)
                    elif ra != nm:
                        alias_bad.append((slot, al, nm, ra))

    gp = ROOT / "graph.json"
    newest = max(p2.stat().st_mtime for p2 in files)
    stale = gp.stat().st_mtime < newest
    print(f"号位 {files[0].stem}–{files[-1].stem}｜实测进图块 {n_blocks}"
          f"｜name 声明 {n_names}｜alias 声明 {n_alias}"
          f"｜已覆盖草稿块 {skipped['overwritten']}｜无 cache 块 {skipped['absent']}")
    if stale:
        print("⚠ graph.json **滞后于**本区间 batch(抽取期未 rebuild)——"
              "新建 name 的 resolve=None **不可判定**，本结果仅为预检；请 rebuild 后重跑。")
    for tag, rows in (("N1a name 被别的组吸走(★致命)", absorbed),
                      ("N1b name 原因未明、既未吸走也无丢弃规则(★致命)", unexplained),
                      ("N2  alias 指向了别的 name(★致命)", alias_bad),
                      ("N3a alias resolve=None 且**无**丢弃规则可解释(§4.11,清单)",
                       alias_unknown),
                      ("N3b alias 被归一化层刻意丢弃(清单,处置=改写法)", alias_listed)):
        seen = {r[1]: r for r in rows}
        print(f"\n{tag}: {len(seen)} 项")
        for r in sorted(seen.values(), key=lambda x: (x[0], str(x[1]))):
            print("   ", " | ".join(str(x) for x in r))
    d_uniq = {r[1]: r for r in dropped}
    print(f"\nN1c name 被归一化层刻意丢弃(清单,处置=改写法): {len(d_uniq)} 项")
    for c, k in sorted(cause_cnt.items(), key=lambda x: -x[1]):
        print(f"    成因[{c}] × {k}")
    for r in sorted(d_uniq.values(), key=lambda x: (x[0], str(x[1]))):
        print("   ", " | ".join(str(x) for x in r))
    # 口径:致命 = N1a 吸走 + N1b 未明 + N2 指错 + graph 滞后;
    #       清单 = N1c/N3a/N3b(设计内去噪与 §4.11 已知缺陷,逐条留 §10 裁定,不判失败)。
    ok = not (absorbed or unexplained or alias_bad) and not stale
    print("\n✅ 实测进图的声明全部可解析"
          f"(丢弃清单 name {len(d_uniq)} / alias {len(alias_listed) + len(alias_unknown)} 项待 §10)"
          if ok else "\n❌ 存在落盘失效项,见上")
    return 0 if ok else 1


if __name__ == "__main__":
    a = sys.argv[1:]
    sys.exit(main(int(a[0]), int(a[1]) if len(a) > 1 else None))
