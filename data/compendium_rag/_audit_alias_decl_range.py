# -*- coding: utf-8 -*-
"""全量 cache 体检（只读）：给定写法，报它**在多少块里是 name**、**在多少块里只是 alias**、
以及 alias 的宿主分布 —— 这是做任何一次 alias 剥离/归并裁定前的前置闸。

为什么必须先跑它
----------------
`_fix_alias_welds.py` 的 strip 只删「宿主 → alias」这一侧的声明。若某个写法**从来没有
以任何块的 name 出现过**（只活在别人的 alias 里），剥掉那条 alias 就等于让该写法
永久不可解析 —— 即 §4.11 记录过的「成员抹除」事故。所以裁定顺序必须是：
  先看 name 侧有没有落点 → 有则可安全剥离；无则须先补声明或按「单独列出」登记。

用法：_audit_alias_decl_range.py 写法1 写法2 …
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from compendium_rag.config import get_settings  # noqa: E402
from compendium_rag.extract import _norm_name  # noqa: E402


def main() -> int:
    targets = [_norm_name(x) for x in sys.argv[1:] if x.strip()]
    if not targets:
        print(__doc__)
        return 1
    s = get_settings()
    files = sorted(Path(s.cache_dir).rglob("*.json"))   # cache 下有 256 个散列子目录
    if not files:
        print("!! cache 扫描为空 —— 目录结构变了，本体检无结论")
        return 2
    name_cnt = Counter()
    alias_hosts: dict[str, Counter] = defaultdict(Counter)
    scanned = 0
    recs = 0
    for f in files:
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:                     # 损坏文件如实计数，不静默跳过
            print(f"!! 解析失败 {f.name}")
            continue
        scanned += 1
        ents = (d.get("raw") or {}).get("entities") or []
        recs += len(ents)
        for e in ents:
            nm = _norm_name(e.get("name", ""))
            if nm in targets:
                name_cnt[nm] += 1
            for a in (e.get("aliases") or []):
                an = _norm_name(a)
                if an in targets:
                    alias_hosts[an][nm] += 1
    print(f"体检群体：cache 文件 {scanned} 个 / 实体声明 {recs} 条 / 目标写法 {len(targets)} 个")
    bad = 0
    for t in targets:
        n_name = name_cnt.get(t, 0)
        hosts = alias_hosts.get(t, Counter())
        tot_alias = sum(hosts.values())
        verdict = "可安全剥离" if n_name > 0 else ("!! 无 name 落点（剥即抹除）" if tot_alias
                                                   else "-- 语料/缓存中未声明")
        if n_name == 0 and tot_alias:
            bad += 1
        print(f"  {t:14s} name侧块={n_name:4d}  alias声明={tot_alias:4d}  {verdict}"
              f"  宿主TOP: {[(h, c) for h, c in hosts.most_common(3)]}")
    print(f"\n小结：{bad} 个写法只有 alias 落点（剥离会导致不可解析，须先补 name 声明或登记单列）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
