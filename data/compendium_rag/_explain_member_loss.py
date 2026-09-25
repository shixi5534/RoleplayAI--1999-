# -*- coding: utf-8 -*-
"""反查「落盘后 resolve=None」的写法是被**哪一条 alias 声明**并进别的组的。

背景(第 19 会话实测确认的机制):`GraphStore.build_from_extractions` 里
`aliases.discard(canon); aliases -= set(members)` 之后,DSU 组内**非 canonical 的
成员写法**只存在于内存的 `alias_index`;存盘再 `load` 时 alias_index 只能由
`entity.name + entity.aliases` 重建(graph_store.py:343-345),于是这些写法**永久查不到**。
所以 6b 里 `resolve(name)=None` 有一大类不是"名字没抽到",而是"名字并进了别的组、
且拼写在落盘时被抹掉"——它同时意味着**两组被 alias 连成了一个节点**。

本脚本零网络、只读:复算 obs_entities + DSU(与 rebuild ①②步同码),
对每个"多写法组"打印:
    canonical  ← 各成员写法  ← 是哪块 cache(号位/块 key/宿主 name)声明了这条 alias
用法:
    python _explain_member_loss.py                # 只列多写法组(全部)
    python _explain_member_loss.py <names.txt>    # 只列包含这些写法的组
处置口径(见 handoff §4.11 / §9):**改数据不改代码** ——
    同人 → 在**声明侧**直接写 canonical 名(或保留 alias 但接受其不可解析并登记);
    异人 → 删掉那条污染 alias 的生成器声明并重新 submit。
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent / "src"))
from compendium_rag import pipeline as P                                    # noqa: E402
from compendium_rag.config import get_settings                              # noqa: E402
from compendium_rag.extract import (PROMPT_VERSION, ExtractionCache,        # noqa: E402
                                    cache_key, normalize)
from compendium_rag.graph_store import _merge_candidates, canonical_pick    # noqa: E402


def _slot_from_batch() -> dict:
    """块 key -> 声明过它的号位集合(仅作展示用,不影响判据)。"""
    m = defaultdict(set)
    import re
    for p in sorted(ROOT.glob("_agent_batch*.json")):
        mm = re.fullmatch(r"_agent_batch(\w+)", p.stem)
        if not mm:
            continue
        try:
            for k in json.loads(p.read_text(encoding="utf-8")):
                m[k].add(mm.group(1))
        except Exception:
            continue
    return m


def main() -> int:
    want = set()
    if len(sys.argv) > 1:
        want = {l.strip() for l in
                Path(sys.argv[1]).read_text(encoding="utf-8").splitlines() if l.strip()}
    s = get_settings()
    cache = ExtractionCache(s.cache_dir)
    slots = _slot_from_batch()
    obs: dict[str, dict] = {}
    who: dict[tuple, list] = defaultdict(list)     # (holder, alias) -> [(chunk_id, 号位)]
    for c in P.load_chunks(s):
        key = cache_key(c, s.llm_model, PROMPT_VERSION)
        raw = cache.get_raw(key)
        if raw is None:
            continue
        ex = normalize(c, raw)
        if ex is None or not getattr(ex, "ok", True):
            continue
        if not ex.entities and not ex.relations:
            continue
        for e in ex.entities:
            if not e.name:
                continue
            o = obs.setdefault(e.name, {"types": {}, "aliases": set(), "descs": {}})
            o["types"][e.type] = o["types"].get(e.type, 0) + 1
            if e.desc:
                o["descs"][e.desc] = o["descs"].get(e.desc, 0) + 1
            for a in (x for x in e.aliases if x):
                o["aliases"].add(a)
                who[(e.name, a)].append((c.chunk_id, ",".join(sorted(slots.get(key, {"?"})))))
        for r in ex.relations:
            for x in (r.src, r.dst):
                obs.setdefault(x, {"types": {}, "aliases": set(), "descs": {}})

    names = sorted(obs)
    dsu = _merge_candidates(names, [(n, a) for n, o in obs.items()
                                    for a in o["aliases"] if a != n])
    groups: dict[str, list] = defaultdict(list)
    for n in names:
        groups[dsu.find(n)].append(n)
    rows = []
    for root, mem in groups.items():
        if len(mem) < 2:
            continue
        obs_count = {m: sum(obs[m]["types"].values()) + sum(obs[m]["descs"].values())
                     for m in mem}
        canon = canonical_pick(mem, obs_count)
        if want and not (want & set(mem)):
            continue
        rows.append((canon, mem, obs_count))
    rows.sort(key=lambda r: r[0])
    print(f"obs 名 {len(names)}｜多写法组(在筛选内) {len(rows)}")
    for canon, mem, oc in rows:
        print(f"\n「{canon}」(obs={oc[canon]}) 组内 {len(mem)} 写法: "
              f"{', '.join(sorted(mem))}")
        for m in sorted(mem):
            if m == canon:
                continue
            # 找出把 m 连进本组的那条 alias 声明：宿主 name 是 canon 组里任一写法
            for (holder, al), srcs in sorted(who.items()):
                if al != m or holder not in mem:
                    continue
                uniq = sorted({(ch, sl) for ch, sl in srcs})
                print(f"    {m}  ← alias 声明: name=「{holder}」aliases=[…{m}…]  "
                      f"×{len(uniq)} 处  例: {uniq[0][0][-14:]}(号位{uniq[0][1]})")
    print("\n口径:alias_index 在存盘/载入时只能由 name+aliases 重建,故组内非 canonical "
          "写法 resolve 必为 None;\n上列每条 alias 声明都是把两个写法焊死的焊点,"
          "要「分家」就删声明侧的 alias,要「认同人」就把引用侧改成 canonical。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
