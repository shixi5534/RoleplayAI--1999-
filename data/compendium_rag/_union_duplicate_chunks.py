# -*- coding: utf-8 -*-
"""并发重复抽取的「分裂命名」并集遍 —— 把落败侧独有的实体/关系并回存活块。

背景(任务 #20 / §4.10)：同一 chunk 被两个子代理各抽一次时，`submit` 是**整块覆盖**，
后提交者胜 → 落败侧独有的名字一个字不进图。`_audit_global_key_collisions.py` 实测
号位 247–610 区间：总 key 856｜重叠 143｜**分裂 71**｜超集/子集 52｜一致 20。

做法：batch 文件的 dict 键**就是 cache_key**，所以能直接把「同一 key 的多个版本」
对齐到 cache 里的存活块上，按 `_norm_name` 并实体、按 `(src,relation,dst)` 并关系。
证据两侧取自**同一 chunk 文本**，故不会引入越块证据；但**落败侧本身可能违规**——
实测(第 20 会话，canonical 口径)并集若不校验，会把 5 条「意译/用省略号拼接」的
evidence 从老批次的落败块带进存活块(违反 §3 红线 3)。故本遍对**每条待并入关系**先做
逐字校验，未命中即丢弃并计数，绝不静默引入。(一度测得 138 条系口径错误：比较了
pre-weld vs post-weld 的四元组、且用了空白不敏感匹配；见交接文档 §4.13。)

流水线顺序(不可颠倒)：**本遍 → `_fix_alias_welds.py` → `rebuild`**。
落败侧的 batch 块里仍带着泛称 alias 声明，先并后剥才不会把已裁定的焊点又带回图。

幂等性(第 20 会话末实测)：weld 之后再跑本遍，老批次版本里被 weld 剥除的 **A→A 自环**
会被重新看成「存活块所无」而报成可并(实测 9 块 / 12 条唯一自环，跨版本重复计数 15)——那不
是漏抽的数据，回灌等于撤销 §4.12 的裁定。故关系并入前先做自环判定并**只计数不写盘**；加了
这道守卫后 dry-run 报 `实际改写块 0｜并入关系 0｜自环不并 15(去重 12)`，即真幂等。
alias/desc 维度实测**零回灌**(0 条)。

零网络、只读 Ollama 不参与。默认 dry-run，`--apply` 才写盘(写盘前自行备份 cache/)。
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent / "src"))
sys.path.insert(0, str(ROOT))

from compendium_rag import pipeline as P                                    # noqa: E402
from compendium_rag.config import get_settings                              # noqa: E402
from compendium_rag.extract import PROMPT_VERSION, ExtractionCache, cache_key  # noqa: E402
from _fix_alias_welds import _norm_name                                     # noqa: E402
from _verify_evidence import QUOTES                                         # noqa: E402


def _verbatim(ev: str, text: str) -> bool:
    """与 `_verify_evidence.py` **同一口径**：去引号后须是块原文连续子串。"""
    return bool(ev) and ev.translate(QUOTES) in text.translate(QUOTES)


def _sig(obj: dict) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True)


def merge_into(base: dict, other: dict, conf: list, text: str,
               dropped: list, selfloops: list) -> tuple[int, int]:
    """把 other 并进 base(原地)，返回 (新增实体数, 新增关系数)。"""
    ents = base.setdefault("entities", [])
    by_name: dict[str, dict] = {}
    for e in ents:
        by_name.setdefault(_norm_name(e.get("name", "")), e)
    n_e = 0
    for e in other.get("entities") or []:
        k = _norm_name(e.get("name", ""))
        if not k:
            continue
        cur = by_name.get(k)
        if cur is None:
            ents.append(json.loads(json.dumps(e, ensure_ascii=False)))
            by_name[k] = ents[-1]
            n_e += 1
            continue
        if cur.get("type") != e.get("type"):
            conf.append((k, cur.get("type"), e.get("type")))   # 类型冲突：保留存活侧
        for a in e.get("aliases") or []:
            if a and a != cur.get("name") and a not in (cur.get("aliases") or []):
                cur.setdefault("aliases", []).append(a)
        d = e.get("desc") or ""
        if d and d not in (cur.get("desc") or ""):
            cur["desc"] = ((cur.get("desc") or "") + "；" + d) if cur.get("desc") else d

    rels = base.setdefault("relations", [])
    seen = {(r.get("src"), r.get("relation"), r.get("dst")) for r in rels}
    n_r = 0
    for r in other.get("relations") or []:
        key = (r.get("src"), r.get("relation"), r.get("dst"))
        if key in seen:
            continue
        if _norm_name(key[0] or "") == _norm_name(key[2] or ""):
            # 自环：`_fix_alias_welds.py` 已按 §4.12 把 A→A 判为焊点伪影剥除(实测 141 条)。
            # 老批次版本里仍留着它们，故**并集在 weld 之后重跑**时唯一会剩的就是这类；
            # 回灌 = 撤销 weld 的裁定。一律不并，只计数报出。
            selfloops.append(key)
            continue
        if not _verbatim(r.get("evidence") or "", text):
            dropped.append((key, r.get("evidence")))   # 落败侧意译/拼接 → 不并入
            continue
        seen.add(key)
        rels.append(json.loads(json.dumps(r, ensure_ascii=False)))
        n_r += 1
    return n_e, n_r


def main() -> int:
    apply = "--apply" in sys.argv
    s = get_settings()
    cache = ExtractionCache(s.cache_dir)

    # chunk → cache_key → 块原文（与 _fix_alias_welds 同一口径，duplicate-content 块共用 key）
    texts: dict[str, str] = {}
    for c in P.load_chunks(s):
        texts.setdefault(cache_key(c, s.llm_model, PROMPT_VERSION), c.text)
    keys = set(texts)

    versions: dict[str, list[tuple[str, dict]]] = defaultdict(list)
    n_blk = 0
    for p in sorted(ROOT.glob("_agent_batch*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            print(f"!! 无法解析 {p.name}，跳过")
            continue
        for k, blk in data.items():
            if not isinstance(blk, dict) or k not in keys:
                continue
            n_blk += 1
            versions[k].append((p.name, blk))

    live = {k: cache.get_raw(k) for k in versions}
    todo, n_e, n_r, conf, no_live = [], 0, 0, [], 0
    dropped: list = []
    selfloops: list = []
    for k, vs in sorted(versions.items()):
        alts = [v for _, v in vs] + ([live[k]] if live[k] else [])
        uniq = {_sig(v) for v in alts}
        if len(uniq) < 2:
            continue
        if live[k] is None:
            no_live += 1
            continue
        base = json.loads(json.dumps(live[k], ensure_ascii=False))
        be = len(base.get("entities") or [])
        br = len(base.get("relations") or [])
        for _, v in vs:
            if _sig(v) == _sig(live[k]):
                continue
            merge_into(base, v, conf, texts[k], dropped, selfloops)
        ae = len(base.get("entities") or [])
        ar = len(base.get("relations") or [])
        if ae == be and ar == br:
            continue                                     # 只是描述/别名顺序差异，并无可增
        n_e += ae - be
        n_r += ar - br
        todo.append((k, base, be, ae, br, ar))

    print(f"{'[APPLY] 已写盘' if apply else '[DRY-RUN] 未写盘'}"
          f"｜batch 块 {n_blk}｜涉及 key {len(versions)}｜多版本 key {sum(1 for k, v in versions.items() if v)}"
          f"｜**实际改写块 {len(todo)}**")
    print(f"并入实体 {n_e} 个｜并入关系 {n_r} 条｜类型冲突 {len(conf)} 处(保留存活侧)"
          f"｜cache 缺失而跳过 {no_live} 个｜**证据非逐字而丢弃 {len(dropped)} 条**"
          f"｜**自环不并 {len(selfloops)} 条**")
    for k, _b, be, ae, br, ar in todo[:10]:
        print(f"   {k} 实体 {be}→{ae} 关系 {br}→{ar}")
    for c in conf[:10]:
        print(f"   类型冲突 {c[0]}: 存活={c[1]} vs 落败={c[2]}")
    for key, ev in dropped[:10]:
        print(f"   丢弃(非逐字) {key[0]}-{key[1]}->{key[2]}: {str(ev)[:40]}")
    for key in selfloops[:10]:
        print(f"   自环不并 {key[0]}-{key[1]}->{key[2]}")

    if apply and todo:
        for k, base, *_ in todo:
            cache.put_raw(k, base)
        for p in sorted(ROOT.glob("_agent_batch*.json")):
            data = json.loads(p.read_text(encoding="utf-8"))
            changed = False
            for k, blk in data.items():
                new = next((b for kk, b, *_ in todo if kk == k), None)
                if new is not None and _sig(blk) != _sig(new):
                    data[k] = json.loads(json.dumps(new, ensure_ascii=False))
                    changed = True
            if changed:
                p.write_text(json.dumps(data, ensure_ascii=False, indent=1),
                             encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
