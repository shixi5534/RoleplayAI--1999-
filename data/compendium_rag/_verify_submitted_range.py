# -*- coding: utf-8 -*-
"""号位区间「已生成但未落缓存」核查(零网络,只读)。

对区间内每个 _agent_batchNNN.json,取全部 chunk key,
核对 cache/ 里是否存在同名 cache 文件(cache_key 即文件名)。
⚠ 抽取期并发子代理**正在写但尚未 submit** 的号位会被误报,
故默认只报「最后修改 > --第 3 参(默认 **18** 分钟)」的**悬挂**号位。
**校准(第 18 会话实测)**:慢代理单轮通读 12 块可有 4–9 分钟不产出任何文件,
用 8/10 分钟阈值会把 35101/38101/385101 三个**活着**的代理误判为死;
真死的代理(255/292/312)停更都在 **13 分钟以上**且**跨两次采样版本计数不动**。
用法: python _verify_submitted_range.py <起始号位> [结束号位] [停更分钟]

「只有 dump、从未生成 batch」的号位**分三类,不得混判**:
  1) dump 内块 key **全部已在 cache** = 死代理但已被后继号位接替(仅登记);
  2) dump 里 **0 块**(空文件)→ 无任何声明可核,**单列**;拿空集合去判「全部已落缓存」是
     vacuous truth,会把死在半路的号位洗成「不计问题」(第 19 会话修掉的假闸);
     其块是否有人抽,由第 7 步进度快照按版本兜底,不在本脚本下结论;
  3) 有块且仍有块未落 cache → 真缺块,计入退出码。
"""
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / "cache"


def slot(p: Path):
    m = re.fullmatch(r"_agent_batch(\d+)", p.stem)
    return int(m.group(1)) if m else None


def main() -> int:
    lo = int(sys.argv[1]) if len(sys.argv) > 1 else 247
    hi = int(sys.argv[2]) if len(sys.argv) > 2 else 10 ** 9
    stale_min = int(sys.argv[3]) if len(sys.argv) > 3 else 18
    now = time.time()
    cached = {p.stem for p in CACHE.rglob("*.json")}
    missing = {}
    inflight = {}
    n = 0
    for p in sorted(ROOT.glob("_agent_batch*.json")):
        s = slot(p)
        if s is None or not (lo <= s <= hi):
            continue
        n += 1
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            missing[s] = [f"<读取失败 {type(e).__name__}>"]
            continue
        gap = [k for k in d if k not in cached]
        if not gap:
            continue
        age_min = (now - p.stat().st_mtime) / 60
        if age_min < stale_min:
            inflight[s] = round(age_min, 1)
        else:
            missing[s] = gap
    for s, age in sorted(inflight.items()):
        print(f"… 号位 {s}: 未 submit 但仅停更 {age} 分钟(视为子代理在手,不计问题)")
    for s, gap in sorted(missing.items()):
        print(f"✗ 号位 {s}: 未落缓存 {len(gap)} 条 → {', '.join(gap[:3])}")
    # dump 过但从未产出 batch 的号位:必须区分**真空缺**和**已被其它号位接替**
    takers = {}
    for p in sorted(ROOT.glob("_agent_batch*.json")):
        s = slot(p)
        if s is None:
            continue
        try:
            for k in json.loads(p.read_text(encoding="utf-8")):
                takers.setdefault(k, []).append(s)
        except Exception:
            continue
    orphan_dump = []    # 有块始终未落缓存 → 计入失败
    inherited = []      # 块全部由其它号位落缓存 → 仅登记,不判失败
    empty_dump = []     # dump 里 0 块 → 无声明可核,单列(不能靠空集合判"已接替")
    for p in sorted(ROOT.glob("_dump*.txt")):
        m = re.fullmatch(r"_dump(\d+)\.txt", p.name)
        s = int(m.group(1)) if m else None
        if s is None or not (lo <= s <= hi):
            continue
        if (ROOT / f"_agent_batch{s}.json").exists():
            continue
        if (now - p.stat().st_mtime) / 60 < stale_min:
            continue
        keys = []
        for ln in p.read_text(encoding="utf-8").splitlines():
            try:
                keys.append(json.loads(ln)["key"])
            except Exception:
                continue
        lack = [k for k in keys if k not in cached]
        if not keys:
            # dump 里 0 条 → "全部已落缓存"是**空集合上的真**(vacuous truth),不能算已被接替
            empty_dump.append((s, p.stat().st_size))
        elif lack:
            orphan_dump.append((s, len(keys), lack))
        else:
            by = sorted({t for k in keys for t in takers.get(k, []) if t != s})
            inherited.append((s, len(keys), by))
    for s, nkeys, by in inherited:
        print(f"· 号位 {s}: 只有 dump、无 batch,但其 {nkeys} 块已全部由其它号位"
              f"{by}落缓存(不计问题)")
    for s, size in empty_dump:
        print(f"· 号位 {s}: 只有 dump({size} 字节, 0 块)、无 batch → "
              f"**无声明可核**,既不计接替也不计空缺(单列,不判失败)")
    for s, nkeys, lack in orphan_dump:
        print(f"✗ 号位 {s}: 只有 dump、从未生成 batch,且 {len(lack)}/{nkeys} 块未落缓存 → "
              f"{', '.join(lack[:3])}")
    if orphan_dump:
        print("悬挂/真缺块一并计入返回值。")
    print(f"核对 {n} 个号位｜停更<{stale_min}分钟在飞 {len(inflight)} 个｜"
          f"悬挂号位: {sorted(missing) if missing else '无'}｜"
          f"dump 未产出但已被接替: {[s for s, _, _ in inherited] if inherited else '无'}｜"
          f"空 dump(0 块)号位: {[s for s, _ in empty_dump] if empty_dump else '无'}｜"
          f"缺块号位: {sorted(s for s, _, _ in orphan_dump) if orphan_dump else '无'}")
    return 1 if (missing or orphan_dump) else 0


if __name__ == "__main__":
    raise SystemExit(main())
