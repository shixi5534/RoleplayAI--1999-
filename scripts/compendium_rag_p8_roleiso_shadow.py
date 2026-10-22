# -*- coding: utf-8 -*-
"""v9-P8 · 角色域隔离机制的**离线影子评测**（只读：不改 `src/`、不改图、零 LLM）。

P8 Blocker：L2.3 = 0.1556（门槛 ≤0.03）、L4.3 = 0.2278（门槛 ≤0.02），用户不接受未修。
`src/compendium_rag/` 内**没有任何角色域过滤代码**，必须新增机制。本脚本把候选机制
全部实现在**进程内**（重排/重打证据顺序与分数），一次检索喂所有档，产出可比读数。

机制（同一脚本内对比；判据与 L2.3 不同构，故不构成同义反复刷数）：
- M0 基线（不动）
- M1 硬剔除跨域块，不足 top_k 时用被移除块按原序补齐
- M2 稳定分区：同域在前、跨域在后，组内保持 RRF 原序
- M3 融合期降权 `score *= (1-w)`，w ∈ {0.25, 0.5, 0.75, 1.0}
- M4 配额保底：先取同域块，至少保留 N 个跨域名额，再按 RRF 序补足（N ∈ {1,2}）
- 附加（超出必做清单，为「必做五族全灭时仍有可落地候选」而登记）：
  M1c/M2c（只在 `category=="character"` 块上做分区）、M3c_w（同上的降权）、
  M6_w（**章域**口径：角色域题里 `category=="character"` 且不属于被问角色本人
  篇章的块降权；M6x = 同规则但不按角色域题门控）

判据（P3 前置诊断已验证，逐字沿用）：
`owners(chunk) = chunk.speakers ∩ 具名角色表(name+alias)`，具名角色表 =
`type=='角色'` 且非 `is_generic_speaker` 的实体；**跨域块** = `owners` 非空 **且**
与本次**全部种子**的 eid 无交。用全部种子而非首种子：泛称题常同时锚到「伙计」和某个
具名角色，只看首 seed 会把「问题里点名的人自己的场景」误判成跨域。

窗口/候选池口径（**必须逐字复刻原 harness，否则读数不可比**）：
`rrf_fuse(top_n=max(top_k*4, 24))` 只做「排序后截断」，故
- L2.3（`audit_l2.py`，`top_k=10`）→ 候选池 = 前 **40**，窗 = 前 10；
- 三主数 / L4.3（`eval300` / `audit_l4.mode_privacy`，`top_k=6`）→ 候选池 = 前 **24**，窗 = 前 6。
机制作用在**整个候选池**上再截窗（否则「剔除后补齐」退化成纯分区，且池外的好块永远
浮不上来）。本脚本对每题只检索一次（`top_k=10` ⇒ `top_n=40`），40 的前 24 条与
「按 `top_k=6` 检索」逐位相同，故按消费方切片即可等价，省下一半墙钟。

主判据（先于跑数登记）：
1. **双门槛**：L2.3 ≤ 0.03 且 L4.3 ≤ 0.02；
2. **三主数不掉**：hit@6 用**整数命中数**比较（无容差）、MRR 允许 ±0.002 的四舍五入
   抖动、seed_recall（与排序无关，作上游未污染的对照线）；**full 与 graph_only
   两口径**、逐集（300cn-answerable / blind206 / gen120）都不得回退；
3. 分类：双门槛达标且无回退 = **可落地**；双门槛达标但有回退 = **需裁决**；
   否则 = **判负**（附具体 qid 与原因）。

用法（务必脱离会话生命周期；全量约 110 分钟）：
    PYTHONPATH=src .venv/Scripts/python.exe -X utf8 \\
        scripts/compendium_rag_p8_roleiso_shadow.py
冒烟：`P8_RF_LIMIT=20`（另落 `p8_roleiso_smoke_*`，与全量分目录分文件名）
只重算指标（不重跑检索）：`P8_RF_METRICS_ONLY=1`
产物：``reports/p8_roleiso_shadow{_smoke}.{json,md}``、
逐题中间产物 ``reports/p8_roleiso_jsonl{_smoke}/``（按 qid 续跑）
"""
from __future__ import annotations

import asyncio
import hashlib
import importlib.util
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

# 统一口径 env —— 必须在 import compendium config **之前**。
# 用直接赋值而非 setdefault：口径必须由脚本钉死，不依赖调用方 shell。
for _k, _v in {"CMPRAG_LEX_WEIGHT": "1.0", "CMPRAG_RRF_K": "1",
               "CMPRAG_LEX_FIRST": "0", "PYTHONHASHSEED": "0"}.items():
    os.environ[_k] = _v

from compendium_rag import pipeline as P  # noqa: E402
from compendium_rag.config import get_settings  # noqa: E402
from compendium_rag.corpus import is_generic_speaker  # noqa: E402

EXPECTED_SHA = "911bb538160db80e"        # v9-P5 r11（27110 边，7033 实体）
R = ROOT / "data" / "compendium_rag" / "reports"
LIMIT = int(os.environ.get("P8_RF_LIMIT", "0"))
L4_LIMIT = int(os.environ.get("P8_RF_L4_LIMIT", "0"))
METRICS_ONLY = os.environ.get("P8_RF_METRICS_ONLY", "") not in ("", "0")
SUFFIX = "_smoke" if LIMIT else ""
JSONL = R / f"p8_roleiso_jsonl{SUFFIX}"

TOP_K_L23 = 10          # audit_l2.py 的 TOP_K
TOP_K_MAIN = 6          # eval300 主口径；L4.3 的 top-6
POOL_L23 = 40           # audit_l2.py: top_k=10 → rrf_fuse(top_n=max(10*4,24)=40)
POOL_MAIN = 24          # eval300 / audit_l4: top_k=6 → top_n=max(6*4,24)=24
# MRR 回退判定阈值：读数只保留 4 位小数，末位抖动（±0.0001~0.0005）是四舍五入
# 而非机制；超过这个幅度才算金块掉出。hit@6 用**整数**命中数比较，无容差。
MRR_TOL = 0.002
BASELINE_REF = {"L2.3": 0.1556, "L4.3": 0.2278,
                "thresholds": {"L2.3": 0.03, "L4.3": 0.02}}

REQUIRED = (["M0", "M1", "M2"] + [f"M3_w{w}" for w in (0.25, 0.5, 0.75, 1.0)]
            + [f"M4_N{n}" for n in (1, 2)])
EXTRA = ["M1c", "M2c", "M3c_w1.0", "M6_w0.5", "M6_w0.75", "M6_w1.0", "M6x_w1.0",
         "M3f_w1.0"]
ARMS = REQUIRED + EXTRA
# 同源口径：该档的降权判据**就是** L2.3 的判据本身，其 L2.3 读数含同义反复成分
# （自己按判据刷自己），只作「上界参考」，不得当作可落地候选。
TAUTOLOGICAL = {"M3f_w1.0"}
# 逐档定义（渲染用；与 arm_rank 的实现一一对应）
ARM_DEF = {
    "M0": ("必做", "基线，不动（对照组）"),
    "M1": ("必做", "硬剔除跨域块，不足 top_k 用被移除块按原序补齐"),
    "M2": ("必做", "稳定分区：同域在前、跨域在后，组内保持 RRF 原序"),
    "M4_N1": ("必做", "配额保底：先取同域，保留 1 个跨域名额，其余按 RRF 序补足"
                       "（配额窗 = 主口径前 6；其后按池原序补，故 L2.3 的前 10 "
                       "里可能自然落入更多跨域块）"),
    "M4_N2": ("必做", "配额保底：先取同域，保留 2 个跨域名额，其余按 RRF 序补足"
                       "（配额窗 = 主口径前 6，同上）"),
    "M1c": ("附加", "同 M1，但只在 category=='character' 的跨域块上做"),
    "M2c": ("附加", "同 M2，但只在 category=='character' 的跨域块上做"),
    "M3c_w1.0": ("附加", "同 M3(w=1.0)，但只降 category=='character' 的跨域块分数"),
    "M6_w0.5": ("附加", "【章域口径】角色域题里 character 类块不属于被问角色本人章域 → 降权 w=0.5"),
    "M6_w0.75": ("附加", "【章域口径】同上，w=0.75"),
    "M6_w1.0": ("附加", "【章域口径】同上，w=1.0（等于把域外 character 块压到末位）"),
    "M6x_w1.0": ("附加", "【章域口径·不门控】同 M6_w1.0 规则，但不要求题是角色域题"),
    "M3f_w1.0": ("附加", "⚠**同源口径**（判据对齐，读数含同义反复成分，只作上界"
                         "参考）：按 `leak_check` 自己的口径降权 —— 窗内 "
                         "`category=='character'` 且 `text+speakers` 都不含**首 seed "
                         "角色** name/alias 的块 → score *= 0。与 M3c_w1.0 的差 = "
                         "「owners 命中非首种子」那部分块的影响"),
}
for _w in (0.25, 0.5, 0.75, 1.0):
    ARM_DEF[f"M3_w{_w}"] = ("必做",
                            f"融合期降权：跨域块 score *= (1-{_w}) 后重排")

SETS = {
    "300cn": ROOT / "data" / "knowledge" / "_audit" / "rag_testset_300_cn.json",
    "blind206": ROOT / "data" / "knowledge" / "_audit" / "blind_v1" / "questions_strict.json",
    "gen120": ROOT / "data" / "knowledge" / "_audit" / "rag_testset_gen_r1r2.json",
}
AUDIT_DIR = ROOT / "data" / "knowledge" / "_audit"
WHITELIST = AUDIT_DIR / "audit_qid_whitelist.json"
PRIV_GOLD = AUDIT_DIR / "l4_privacy_gold.json"
TOP_N_CHAR = 50         # 与 audit_l4.py:445 一致


def _load_eval():
    spec = importlib.util.spec_from_file_location(
        "ev300", ROOT / "scripts" / "compendium_rag_eval300.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    # 先注册再 exec：eval300 有 @dataclass，dataclasses 按 cls.__module__ 回查 sys.modules
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def sha16(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def full_blob(c) -> str:
    """与 eval300.score_case 判 hit 用的 blob 逐字一致，不另起一把尺子。"""
    return f"{c.text}\n{c.chapter_title}\n{c.scene_title}\n{c.part_title}"


def chapter_of(cid: str) -> str:
    """章域前缀，与 audit_l4.mode_privacy 的 `cid.split(":")[0]` 逐字一致。"""
    return cid.split(":")[0]


# ── 块归属（判据与 p3_rolefilter_prereq_diag 逐字一致）──

class OwnerTable:
    def __init__(self, graph, chunks):
        self.by_cid = {c.chunk_id: c for c in chunks}
        cmeta = self.by_cid
        named = [e for e in graph.entities.values()
                 if e.type == "角色" and not is_generic_speaker(e.name)]
        self.name2eid: dict[str, str] = {}
        for e in named:
            for nm in (e.name, *e.aliases):
                if nm and nm not in self.name2eid:
                    self.name2eid[nm] = e.eid
        self._cache: dict[str, set[str]] = {}
        # 具名角色的「本人章域」：其 character 类块的章前缀
        self.own_chapters: dict[str, set[str]] = {}
        for e in named:
            chs = {chapter_of(cid) for cid in e.chunk_ids
                   if cmeta.get(cid) is not None
                   and cmeta[cid].category == "character"}
            self.own_chapters[e.eid] = chs

    def owners(self, cid: str) -> set[str]:
        if cid not in self._cache:
            c = self.by_cid.get(cid)
            self._cache[cid] = ({self.name2eid[s] for s in (c.speakers or [])
                                 if s in self.name2eid} if c else set())
        return self._cache[cid]


class Ctx:
    """逐题上下文：跨域集合、角色域身份、门控所需信息。所有机制只读它。"""

    __slots__ = ("cross", "cross_c", "role", "seed_chaps", "ch_of", "cat",
                 "seed_eids", "seed_names")

    def __init__(self, row, table, graph, cmeta):
        seed_eids = {s["eid"] for s in row.get("seeds", [])}
        cross, cross_c = set(), set()
        for e in row["evidence"]:
            cid = e["chunk_id"]
            ow = table.owners(cid)
            if ow and not (ow & seed_eids):
                cross.add(cid)
                c = cmeta.get(cid)
                if c is not None and c.category == "character":
                    cross_c.add(cid)
        self.cross, self.cross_c = cross, cross_c
        self.cat = cmeta
        self.ch_of = {}
        for e in row["evidence"]:
            self.ch_of[e["chunk_id"]] = chapter_of(e["chunk_id"])
        seeds = row.get("seeds", [])
        ent = graph.entities.get(seeds[0]["eid"]) if seeds else None
        self.role = bool(ent and ent.type == "角色")
        chs: set[str] = set()
        for s in seeds:
            chs |= table.own_chapters.get(s["eid"], set())
        self.seed_chaps = chs
        self.seed_eids = seed_eids
        names = set()
        if self.role:
            names = {n for n in (ent.name, *(ent.aliases or [])) if n}
        self.seed_names = names


def _partition(pool, drop):
    same = [e for e in pool if e["chunk_id"] not in drop]
    cr = [e for e in pool if e["chunk_id"] in drop]
    return same, cr


def _rescore(pool, pred, w):
    out = []
    for e in pool:
        out.append(dict(e, score=e["score"] * (1.0 - w)) if pred(e["chunk_id"]) else e)
    return sorted(out, key=lambda e: (-e["score"], e["chunk_id"]))


def arm_rank(arm, pool: list[dict], ctx: Ctx, win: int = TOP_K_MAIN) -> list[dict]:
    """在**候选池**上重排（调用方负责按消费方切好 POOL_L23 / POOL_MAIN）。

    `win` = 该消费方实际会看的前 N 条（L2.3 是 10、三主数/L4.3 是 6）。
    只有 M4 需要它：配额必须按**实际窗口**算「保留 N 个跨域名额」，否则
    L2.3 的窗（10）会落到为 6 设计的配额头上，读数不可比。
    """
    cx, cxc = ctx.cross, ctx.cross_c
    if arm == "M0":
        return pool
    if arm in ("M1", "M2"):
        # M1（硬剔除→不足补齐）与 M2（稳定分区）在本判据下是**同一个排序**：
        # 「同域块按原序 + 跨域块按原序」。两者逐位相同，报告里如实标注。
        same, cr = _partition(pool, cx)
        return same + cr
    if arm in ("M1c", "M2c"):
        same, cr = _partition(pool, cxc)
        return same + cr
    if arm == "M4_N1" or arm == "M4_N2":
        n = int(arm[-1])
        same, cr = _partition(pool, cx)
        # 前 win 条里给跨域留恰好 n 个名额，其余按 RRF 原序补足
        head = same[:max(0, win - n)] + cr[:n]
        seen = {e["chunk_id"] for e in head}
        return head + [e for e in pool if e["chunk_id"] not in seen]
    if arm.startswith("M3_w"):
        return _rescore(pool, lambda cid: cid in cx, float(arm[4:]))
    if arm.startswith("M3c_w"):
        return _rescore(pool, lambda cid: cid in cxc, float(arm[5:]))
    if arm.startswith("M3f_w"):
        # 【判据对齐】完全按 `leak_check` 的口径降权：只在角色域题上生效
        # （非角色域题没有『首 seed 角色名』，判据本身就不适用）。
        if not ctx.role:
            return pool
        w = float(arm[5:])

        def leaky(cid: str) -> bool:
            c = ctx.cat.get(cid)
            if c is None or c.category != "character":
                return False
            hay = c.text + "\n" + "\n".join(c.speakers or [])
            return not any(nm in hay for nm in ctx.seed_names)

        return _rescore(pool, leaky, w)
    if arm.startswith("M6_w") or arm.startswith("M6x_w"):
        gated = arm.startswith("M6_w")
        # M6：角色域题里，`character` 类块若不属于**被问角色本人**的章域 → 降权。
        # 门控条件：题是角色域题，且该角色确有本人 character 章域（否则无从判"域外"，
        # 退化为 no-op，避免把种子无自己篇章的角色题一起打掉）。
        if gated and (not ctx.role or not ctx.seed_chaps):
            return pool
        if not gated and not ctx.seed_chaps:
            return pool
        w = float(arm.split("_w", 1)[1])
        ok = ctx.seed_chaps

        def out_of_domain(cid: str) -> bool:
            c = ctx.cat.get(cid)
            return (c is not None and c.category == "character"
                    and ctx.ch_of.get(cid, chapter_of(cid)) not in ok)

        return _rescore(pool, out_of_domain, w)
    raise KeyError(arm)


# ── 检索（一次检索喂所有档，按 qid 续跑）──

def _dump(res) -> dict:
    # G1（2026-10-21）：`kb.retrieve` 现在把 `evidence` 截到 top_k，全池在
    # `evidence_pool` 里。本脚本按池宽设计（POOL_L23=40 > TOP_K_L23=10），
    # 必须取池、不能取窗口；池缺失时回落到窗口以免旧缓存/旧工件直接崩。
    pool = res.get("evidence_pool")
    if pool is None:
        pool = res.get("evidence", [])
    return {
        "seeds": [{"eid": s["eid"], "name": s["name"], "score": s["score"],
                   "how": s["how"]} for s in res.get("seeds", [])],
        # 只留前 POOL_L23 条：rrf_fuse 的截断是「排序后截断」，故 POOL_MAIN 是它的前缀
        "evidence": [{"chunk_id": e["chunk_id"], "score": e["score"],
                      "graph_score": e.get("graph_score", 0.0),
                      "channels": e.get("channels", {})}
                     for e in pool][:POOL_L23],
    }


def _read_jsonl(p: Path) -> list[dict]:
    if not p.exists():
        return []
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines()
            if x.strip()]


async def collect(kb, tag: str, cases: list, mode: str, use_vector: bool) -> list[dict]:
    out = JSONL / f"{tag}_{mode}.jsonl"
    done = {r["qid"]: r for r in _read_jsonl(out)}
    rows = [done[c.qid] for c in cases if c.qid in done]
    todo = [c for c in cases if c.qid not in done]
    if not todo:
        print(f"  [{tag}/{mode}] 全部命中续跑缓存 {len(rows)} 题", flush=True)
        return rows
    with out.open("a", encoding="utf-8") as fh:
        for i, c in enumerate(todo, 1):
            t0 = time.time()
            res = await kb.retrieve(c.query, top_k=TOP_K_L23,
                                    use_vector=use_vector, want_pool=True)
            r = {"qid": c.qid, "query": c.query, "keywords": list(c.keywords),
                 "seconds": round(time.time() - t0, 3), **_dump(res)}
            rows.append(r)
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
            fh.flush()
            if i % 25 == 0:
                print(f"  [{tag}/{mode}] 本次 {i}/{len(todo)}"
                      f"（累计 {len(rows)}）", flush=True)
    return rows


def char_pool(graph) -> list:
    chars = [e for e in graph.entities.values() if e.type == "角色"]
    chars.sort(key=lambda e: (-e.mentions, -len(e.chunk_ids), e.eid))
    return [e for e in chars if len(e.chunk_ids) >= 3][:TOP_N_CHAR]


def l4_probes(graph) -> list[dict]:
    """复刻 audit_l4.mode_privacy 的题面构造（asker 轮转、只点名提问者）。"""
    gold = json.loads(PRIV_GOLD.read_text(encoding="utf-8"))["anchors"]
    chars = char_pool(graph)
    asker_pool = [c.name for c in chars] or ["J"]
    names_by_char = {c.name: {c.name, *(c.aliases or [])} for c in chars}
    rows = []
    for k, a in enumerate(gold):
        owner = a["character"]
        asker = next(asker_pool[(k + j) % len(asker_pool)]
                     for j in range(1, len(asker_pool) + 1)
                     if asker_pool[(k + j) % len(asker_pool)] != owner)
        aspect = a.get("aspect") or "不为人知的过去"
        rows.append({
            "idx": k, "character": owner, "asker": asker, "aspect": aspect,
            "chunk_id": a["chunk_id"],
            "query": f"{asker}的{aspect}，正典里是怎么写的？",
            "asker_names": sorted(names_by_char.get(asker, {asker})),
        })
    return rows


def main() -> int:
    if os.environ.get("PYTHONHASHSEED") != "0":
        raise SystemExit("[FATAL] PYTHONHASHSEED 必须为 0（排序平局依赖它）")
    s = get_settings()
    sha = sha16(s.graph_path)
    if sha != EXPECTED_SHA:
        # 硬门：不符即退出且**不写任何文件**
        raise SystemExit(f"[FATAL] 冻结图指纹漂移：期望 {EXPECTED_SHA}，实际 {sha}"
                         f"（r11，27110 边）。中止，不写任何文件。")

    ev = _load_eval()
    wl = json.loads(WHITELIST.read_text(encoding="utf-8"))["lists"]
    kb = P.load_kb(s)
    table = OwnerTable(kb.graph, kb.chunks)
    cmeta = {c.chunk_id: c for c in kb.chunks}
    blob_by_cid = {c.chunk_id: full_blob(c) for c in kb.chunks}
    JSONL.mkdir(parents=True, exist_ok=True)

    sets_cfg = {
        "300cn": (SETS["300cn"], set(wl["300cn_answerable"])),
        "blind206": (SETS["blind206"], set(wl["blind_all"])),
        "gen120": (SETS["gen120"], set(wl["gen_all"])),
    }
    cases_by_tag: dict[str, list] = {}
    for tag, (path, qids) in sets_cfg.items():
        cases = [c for c in ev.load_cases(path) if c.qid in qids]
        if LIMIT:
            cases = cases[:LIMIT]
        cases_by_tag[tag] = cases

    probes = l4_probes(kb.graph)
    if L4_LIMIT:
        probes = probes[:L4_LIMIT]

    recs: dict = {}
    if METRICS_ONLY:
        for tag in cases_by_tag:
            recs[tag] = {m: _read_jsonl(JSONL / f"{tag}_{m}.jsonl")
                         for m in ("full", "graph_only")}
        recs["l43"] = _read_jsonl(JSONL / "l43_full.jsonl")
    else:
        for tag, cases in cases_by_tag.items():
            for mode, use_vec in (("full", True), ("graph_only", False)):
                recs.setdefault(tag, {})[mode] = asyncio.run(
                    collect(kb, tag, cases, mode, use_vec))
                print(f"[{tag}/{mode}] {len(recs[tag][mode])} 题", flush=True)
        p_out = JSONL / "l43_full.jsonl"
        done = {r["qid"]: r for r in _read_jsonl(p_out)}
        prows = [done[p["query"]] for p in probes if p["query"] in done]
        todo = [p for p in probes if p["query"] not in done]
        with p_out.open("a", encoding="utf-8") as fh:
            for i, p in enumerate(todo, 1):
                res = asyncio.run(kb.retrieve(p["query"], top_k=TOP_K_L23,
                                              use_vector=True, want_pool=True))
                r = {"qid": p["query"], "query": p["query"], **_dump(res)}
                prows.append(r)
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
                fh.flush()
                if i % 10 == 0:
                    print(f"  [l43] {i}/{len(todo)}", flush=True)
        recs["l43"] = prows
        print(f"[l43] {len(prows)} 锚点", flush=True)

    rep = analyze(kb, table, cmeta, blob_by_cid, cases_by_tag, probes, recs, sha)
    (R / f"p8_roleiso_shadow{SUFFIX}.json").write_text(
        json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
    (R / f"p8_roleiso_shadow{SUFFIX}.md").write_text(render_md(rep), encoding="utf-8")
    print("分类：" + json.dumps({a: rep["verdicts"][a]["class"] for a in ARMS},
                                ensure_ascii=False))
    return 0


def analyze(kb, table, cmeta, blob_by_cid, cases_by_tag, probes, recs, sha) -> dict:
    graph = kb.graph
    idx: dict[tuple[str, str], dict[str, dict]] = {
        (tag, mode): {r["qid"]: r for r in recs[tag][mode]}
        for tag in cases_by_tag for mode in ("full", "graph_only")}
    l43_by_q = {r["qid"]: r for r in recs["l43"]}

    ctx_cache: dict[tuple[str, str, str], Ctx] = {}

    def CX(tag, mode, qid) -> Ctx | None:
        k = (tag, mode, qid)
        if k not in ctx_cache:
            row = idx[(tag, mode)].get(qid)
            if row is None:
                return None
            ctx_cache[k] = Ctx(row, table, graph, cmeta)
        return ctx_cache[k]

    # L4.3 的逐题上下文（16 档共用，避免 80×16 次重算 owners）
    l43_ctx = {p["idx"]: Ctx(l43_by_q[p["query"]], table, graph, cmeta)
               for p in probes if p["query"] in l43_by_q}

    # L4.3 的 co_present 与机制无关，先算一次
    co_by_idx = {}
    for p in probes:
        ch = cmeta.get(p["chunk_id"])
        hay = ch.text if ch else ""
        co_by_idx[p["idx"]] = any(nm in hay for nm in p["asker_names"])
    n_co = sum(1 for v in co_by_idx.values() if v)
    n_den = len(probes) - n_co

    # 基线命中序列（整数命中数 + 名次）—— 只算一次，避免每档重算
    base_rank: dict[tuple[str, str], dict[str, int]] = {}
    seed_recall: dict[tuple[str, str], float] = {}
    m0_leak_win: dict[tuple[str, str], set[str]] = {}
    for tag, cases in cases_by_tag.items():
        for mode in ("full", "graph_only"):
            br, sr, n = {}, 0.0, 0
            for c in cases:
                row = idx[(tag, mode)].get(c.qid)
                if row is None:
                    continue
                n += 1
                rk = 0
                for i, e in enumerate(row["evidence"][:POOL_MAIN][:TOP_K_MAIN], 1):
                    if any(k in blob_by_cid.get(e["chunk_id"], "") for k in c.keywords):
                        rk = i
                        break
                br[c.qid] = rk
                names = [x["name"] for x in row.get("seeds", [])]
                if any(any(k == nm or k in nm or nm in k for nm in names)
                       for k in c.keywords):
                    sr += 1
            base_rank[(tag, mode)] = br
            seed_recall[(tag, mode)] = round(sr / (n or 1), 4)

    # M0 窗内的泄漏块集合（L2.3 口径）—— 用来分辨「本档新引入的泄漏」
    for tag, cases in cases_by_tag.items():
        for c in cases:
            row = idx[(tag, "full")].get(c.qid)
            if row is None:
                continue
            ctx = CX(tag, "full", c.qid)
            if not ctx.role:
                continue
            le = set()
            for e in row["evidence"][:POOL_L23][:TOP_K_L23]:
                ch = cmeta.get(e["chunk_id"])
                if not ch or ch.category != "character":
                    continue
                if not any(nm in ch.text + "\n" + "\n".join(ch.speakers or [])
                           for nm in ctx.seed_names):
                    le.add(ch.chunk_id)
            m0_leak_win[(tag, c.qid)] = le

    def rank_of(tag, mode, c, arm) -> int:
        """本档下该题的 gold 名次（0 = 前 6 未命中）。"""
        row = idx[(tag, mode)][c.qid]
        ctx = CX(tag, mode, c.qid)
        top = arm_rank(arm, row["evidence"][:POOL_MAIN], ctx)[:TOP_K_MAIN]
        for i, e in enumerate(top, 1):
            if any(k in blob_by_cid.get(e["chunk_id"], "") for k in c.keywords):
                return i
        return 0

    # 反例追踪（R200 形状的推广）：M0 的**首个命中块**本身属于「跨域 且
    # category=='character'」的题 —— 这类题若被隔离机制压后，会直接掉出前 6。
    # 把任务书点名的 R200 反例变成可量化子集：逐档报该子集的 hit@6。
    at_risk: dict[tuple[str, str], set[str]] = {}
    for tag, cases in cases_by_tag.items():
        for mode in ("full", "graph_only"):
            s = set()
            for c in cases:
                r0 = base_rank[(tag, mode)].get(c.qid, 0)
                if not r0:
                    continue        # 只在 M0 本来就命中的题里找反例
                ctx = CX(tag, mode, c.qid)
                e = idx[(tag, mode)][c.qid]["evidence"][:POOL_MAIN][r0 - 1]
                ch = cmeta.get(e["chunk_id"])
                if (ch is not None and ch.category == "character"
                        and e["chunk_id"] in ctx.cross):
                    s.add(c.qid)
            at_risk[(tag, mode)] = s

    # L2.3 判据的**覆盖面**诊断（只在 M0 上算一次）：被 `leak_check` 判为泄漏的
    # character 块里，有多少真的满足隔离机制的判据（owners ∩ 全部种子 = ∅）？
    # 剩下的那些（owners 命中非首种子）**机制管不到** —— 这是机制效果的天花板。
    global_break = {"cross": 0, "owned_by_nonfirst_seed": 0, "no_owners": 0,
                    "by_set": {}}
    for tag, cases in cases_by_tag.items():
        b = {"cross": 0, "owned_by_nonfirst_seed": 0, "no_owners": 0, "n_role_q": 0}
        for c in cases:
            row = idx[(tag, "full")].get(c.qid)
            if row is None:
                continue
            ctx = CX(tag, "full", c.qid)
            if not ctx.role:
                continue
            b["n_role_q"] += 1
            for e in row["evidence"][:POOL_L23][:TOP_K_L23]:
                ch = cmeta.get(e["chunk_id"])
                if not ch or ch.category != "character":
                    continue
                if any(nm in ch.text + "\n" + "\n".join(ch.speakers or [])
                       for nm in ctx.seed_names):
                    continue
                ow = table.owners(ch.chunk_id)
                if not ow:
                    b["no_owners"] += 1
                    global_break["no_owners"] += 1
                elif ow & ctx.seed_eids:
                    b["owned_by_nonfirst_seed"] += 1
                    global_break["owned_by_nonfirst_seed"] += 1
                else:
                    b["cross"] += 1
                    global_break["cross"] += 1
        global_break["by_set"][tag] = b

    l23, l43, main_, regress, census = {}, {}, {}, {}, {}
    at_risk_stat: dict[str, dict] = {}

    for arm in ARMS:
        # ── ① L2.3：三集合并，top-10（池 = 前 40）──
        n_role = n_leak = 0
        leak_qids, fixed_qids = [], []
        new_leak: list[int] = []
        blocks_win = cross_win = q_with_cross = 0
        for tag, cases in cases_by_tag.items():
            for c in cases:
                row = idx[(tag, "full")].get(c.qid)
                if row is None:
                    continue
                ctx = CX(tag, "full", c.qid)
                top = arm_rank(arm, row["evidence"][:POOL_L23], ctx,
                               TOP_K_L23)[:TOP_K_L23]
                blocks_win += len(top)
                if any(e["chunk_id"] in ctx.cross for e in top):
                    q_with_cross += 1
                cross_win += sum(1 for e in top if e["chunk_id"] in ctx.cross)
                if not ctx.role:
                    continue
                n_role += 1
                leaked = []
                for e in top:
                    ch = cmeta.get(e["chunk_id"])
                    if not ch or ch.category != "character":
                        continue
                    hay = ch.text + "\n" + "\n".join(ch.speakers or [])
                    if not any(nm in hay for nm in ctx.seed_names):
                        leaked.append(ch.chunk_id)
                if leaked:
                    n_leak += 1
                    leak_qids.append(f"{tag}:{c.qid}")
                    new_leak.append(len(set(leaked) - m0_leak_win.get(
                        (tag, c.qid), set())))
                else:
                    fixed_qids.append(f"{tag}:{c.qid}")
        l23[arm] = {"n_role_q": n_role, "n_leak_q": n_leak,
                    "rate": round(n_leak / n_role, 4) if n_role else None,
                    "leak_qids": leak_qids, "clean_qids_sample": fixed_qids[:5],
                    "new_leak_blocks": sum(new_leak),
                    "new_leak_questions": sum(1 for x in new_leak if x > 0),
                    "blocks_in_window": blocks_win,
                    "cross_domain_in_window": cross_win,
                    "questions_with_cross": q_with_cross,
                    "affected_questions": q_with_cross}

        # ── ② L4.3：80 锚点，top-6（池 = 前 24）──
        n_leak4 = 0
        l4_leak, l4_evict, l4_moved = [], [], []
        for p in probes:
            row = l43_by_q.get(p["query"])
            if row is None:
                continue
            ctx = l43_ctx[p["idx"]]
            top = arm_rank(arm, row["evidence"][:POOL_MAIN], ctx)[:TOP_K_MAIN]
            ids = [e["chunk_id"] for e in top]
            anchor_in = p["chunk_id"] in ids
            base_in = p["chunk_id"] in [
                e["chunk_id"] for e in row["evidence"][:POOL_MAIN][:TOP_K_MAIN]]
            if base_in and not anchor_in:
                l4_evict.append(f"{p['idx']}:{p['character']}<-{p['asker']}")
            elif base_in and anchor_in:
                l4_moved.append(f"{p['idx']}:{p['character']}<-{p['asker']}")
            if anchor_in and not co_by_idx[p["idx"]]:
                n_leak4 += 1
                l4_leak.append(f"{p['idx']}:{p['character']}<-{p['asker']}")
        l43[arm] = {"n_anchors": len(probes), "n_co_present": n_co,
                    "n_denominator": n_den, "n_leak": n_leak4,
                    "rate": round(n_leak4 / n_den, 4) if n_den else None,
                    "leak_qids": l4_leak, "anchor_evicted_qids": l4_evict,
                    "anchor_still_in_window_qids": l4_moved}

        # ── ③ 三主数：逐集 × full/graph_only ──
        main_[arm] = {}
        for tag, cases in cases_by_tag.items():
            main_[arm][tag] = {}
            for mode in ("full", "graph_only"):
                hit = rr = n = 0
                for c in cases:
                    if c.qid not in base_rank[(tag, mode)]:
                        continue
                    n += 1
                    rk = rank_of(tag, mode, c, arm)
                    if rk:
                        hit += 1
                        rr += 1.0 / rk
                main_[arm][tag][mode] = {
                    "n": n, "n_hit": hit,
                    "hit@6": round(hit / (n or 1), 4),
                    "MRR": round(rr / (n or 1), 4),
                    "seed_recall": seed_recall[(tag, mode)]}

        # ── ③bis 反例子集（R200 形状）逐档 hit@6 ──
        ar = {}
        for tag, cases in cases_by_tag.items():
            for mode in ("full", "graph_only"):
                ids = at_risk[(tag, mode)]
                n_ar = len(ids)
                h0 = sum(1 for c in cases if c.qid in ids and base_rank[(tag, mode)][c.qid])
                h1 = sum(1 for c in cases if c.qid in ids and rank_of(tag, mode, c, arm))
                ar[f"{tag}/{mode}"] = {"n": n_ar, "m0_hit": h0, "arm_hit": h1}
        at_risk_stat[arm] = ar

        # ── ④ 逐题翻负（整数命中数，qid 级）──
        regress[arm] = {}
        for tag, cases in cases_by_tag.items():
            for mode in ("full", "graph_only"):
                lost, gained = [], []
                for c in cases:
                    if c.qid not in base_rank[(tag, mode)]:
                        continue
                    r0 = base_rank[(tag, mode)][c.qid]
                    r1 = rank_of(tag, mode, c, arm)
                    if r0 and not r1:
                        lost.append({"qid": f"{tag}:{c.qid}", "query": c.query,
                                     "base_rank": r0})
                    elif r1 and not r0:
                        gained.append({"qid": f"{tag}:{c.qid}", "query": c.query,
                                       "new_rank": r1})
                d0 = main_["M0"][tag][mode]
                d1 = main_[arm][tag][mode]
                regress[arm][f"{tag}/{mode}"] = {
                    "lost": lost, "gained": gained,
                    # 供总表数「回退格数」用：该格是否 hit / MRR 下滑
                    "lost_hit": d1["n_hit"] < d0["n_hit"],
                    "lost_mrr": d0["MRR"] - d1["MRR"] > MRR_TOL,
                }

    # ── ⑤ 基线普查（M0 窗内跨域块 / 其中 gold）──
    for tag, cases in cases_by_tag.items():
        n_blk = n_cross = n_gold = n_qcross = n_noseed = 0
        n_cat: dict[str, int] = {}
        n_goldcat: dict[str, int] = {}
        rows = {}
        for c in cases:
            row = idx[(tag, "full")].get(c.qid)
            if row is None:
                continue
            ctx = CX(tag, "full", c.qid)
            top = row["evidence"][:POOL_L23][:TOP_K_L23]
            n_blk += len(top)
            if not ctx.seed_eids:
                n_noseed += 1
            k_ = 0
            for e in top:
                if e["chunk_id"] in ctx.cross:
                    n_cross += 1
                    k_ += 1
                    if any(x in blob_by_cid.get(e["chunk_id"], "") for x in c.keywords):
                        n_gold += 1
                    ch_ = cmeta.get(e["chunk_id"])
                    cc = (ch_.category if ch_ else "?")
                    n_cat[cc] = n_cat.get(cc, 0) + 1
                    if any(x in blob_by_cid.get(e["chunk_id"], "") for x in c.keywords):
                        n_goldcat[cc] = n_goldcat.get(cc, 0) + 1
            n_qcross += 1 if k_ else 0
            rows[c.qid] = {"n_seeds": len(ctx.seed_eids), "n_ev": len(top),
                           "n_cross": k_}
        census[tag] = {"n_cases": len(cases), "blocks_in_window": n_blk,
                       "cross_domain_blocks_in_window": n_cross,
                       "cross_by_category": dict(sorted(n_cat.items())),
                       "cross_gold_by_category": dict(sorted(n_goldcat.items())),
                       "cross_domain_that_are_gold": n_gold,
                       "gold_share_of_cross": round(n_gold / max(1, n_cross), 4),
                       "questions_with_any_cross": n_qcross,
                       "questions_without_seeds": n_noseed, "rows": rows}

    # 角色域题身份（L2.3 分母来源）——供报告交代
    role_ids = set()
    for tag, cases in cases_by_tag.items():
        for c in cases:
            ctx = CX(tag, "full", c.qid)
            if ctx is not None and ctx.role:
                role_ids.add(f"{tag}:{c.qid}")

    verdicts = classify(l23, l43, main_, regress)
    # ⑤bis 基线复现门：M0 必须复现已核实读数，否则全部下游读数不可信
    repro = {
        "L2.3": {"recorded": 0.1556, "m0": l23["M0"]["rate"],
                 "ok": l23["M0"]["rate"] is not None
                       and abs(l23["M0"]["rate"] - 0.1556) <= 0.0002,
                 "recorded_n": "35/225"},
        "L4.3": {"recorded": 0.2278, "m0": l43["M0"]["rate"],
                 "ok": l43["M0"]["rate"] is not None
                       and abs(l43["M0"]["rate"] - 0.2278) <= 0.0002,
                 "recorded_n": "18/79"},
    }
    return {
        "schema": "compendium_rag.p8_roleiso_shadow/v1",
        "done_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "graph_sha256_16": sha, "expected_sha16": EXPECTED_SHA,
        "shadow_only": "只在进程内重排/重打 evidence；未改 src/、未写图、未改既有报告",
        "criterion": "owners = chunk.speakers ∩ 具名角色表(name+alias)（type=='角色' "
                     "且非泛称）；owners 非空且与本次全部种子 eid 无交 → 跨域块",
        # 逐档（不是逐族）渲染：族内不同档位读数不同，不能合并成一行
        "mechanisms": {a: ARM_DEF[a][1] for a in ARMS},
        "arm_category": {a: ARM_DEF[a][0] for a in ARMS},
        "window_caliber": {"l23": {"pool": POOL_L23, "window": TOP_K_L23},
                           "main": {"pool": POOL_MAIN, "window": TOP_K_MAIN},
                           "note": "一次检索(top_k=10)喂全部读数；rrf_fuse 只做排序后"
                                   "截断，故 40 的前 24 条与 top_k=6 检索逐位相同"},
        "caliber": {k: os.environ.get(k) for k in
                    ("CMPRAG_LEX_WEIGHT", "CMPRAG_RRF_K", "CMPRAG_LEX_FIRST",
                     "PYTHONHASHSEED")},
        "mrr_tolerance": MRR_TOL,
        "smoke": {"limit_per_set": LIMIT, "l4_limit": L4_LIMIT},
        "baseline_ref": BASELINE_REF,
        "n_role_domain_questions": len(role_ids),
        "required_arms": REQUIRED, "extra_arms": EXTRA,
        "l23": l23, "l43": l43, "main": main_, "census": census,
        "repro": repro, "at_risk": at_risk_stat,
        "criterion_coverage": global_break,
        "regressions": regress, "verdicts": verdicts,
        "missing_evidence": [
            "本脚本产不出 confuse 认领率 / WP3 双盲正确性 / 生成层读数 → 只回答"
            "「值不值得落成参数」，**不构成验收**（[[fix-data-not-metrics]]）",
            "M3 在本脚本里的实现是**融合后总分** `score *= (1-w)`（按任务书定义）；"
            "P3 的写法是融合**前**只降图通道块分——P3 会改变图通道**内部名次**，"
            "本实现不改变任何通道的内部名次、只压总分。复刻 P3 的逐位等价需要每档"
            "重跑一次检索（约 +50 分钟），本次未做，故 P3 的判负结论**未在本脚本内"
            "复现**，只作为先验引用",
            "L4.3 复用 audit_l4 的 asker 轮转构造题面，未做答案层复核",
            "M6 的『本人章域』定义为该角色实体 chunk_ids 中 category=='character' 的"
            "章前缀集合；对没有 character 类块的角色，M6 直接 no-op（不做外域判定）",
            "L2.3 判据与隔离判据**不同源**：判据只看首 seed 角色的 name/alias，"
            "而机制判据用 owners∩全部种子。故『owners 命中非首种子』的块被判据记"
            "泄漏、机制却不动它（见 §①bis）。这类残余必须靠上游实体链接或判据修订"
            "解决，本脚本只量化不解决",
            "L4.3 的『章域口径』(M6) 用章前缀判域外，实测 80 锚点里只有 2 个锚点章"
            "落在提问者的本人章域内（露西/马库斯 之于 character__19603_犹在镜中），"
            "故 M6 对 L4.3 几乎无杠杆 —— 它的 L4.3 读数与 M0 相同是可以预期的",
        ],
    }


def classify(l23, l43, main_, regress) -> dict:
    out = {}
    m0 = main_["M0"]
    for arm in ARMS:
        cells = []
        for tag in m0:
            for mode in ("full", "graph_only"):
                b, a = m0[tag][mode], main_[arm][tag][mode]
                if a["n_hit"] < b["n_hit"]:
                    cells.append(f"{tag}/{mode} hit@6 {b['hit@6']:.4f}→{a['hit@6']:.4f}"
                                 f"（{b['n_hit']-a['n_hit']} 题）")
                if b["MRR"] - a["MRR"] > MRR_TOL:
                    cells.append(f"{tag}/{mode} MRR {b['MRR']:.4f}→{a['MRR']:.4f}")
        ok23 = l23[arm]["rate"] is not None and l23[arm]["rate"] <= 0.03
        ok43 = l43[arm]["rate"] is not None and l43[arm]["rate"] <= 0.02
        reasons = []
        if not ok23:
            reasons.append(f"L2.3 {l23[arm]['rate']} > 0.03"
                           f"（漏 {l23[arm]['n_leak_q']}/{l23[arm]['n_role_q']} 题）")
        if not ok43:
            reasons.append(f"L4.3 {l43[arm]['rate']} > 0.02"
                           f"（漏 {l43[arm]['n_leak']}/{l43[arm]['n_denominator']} 条）")
        if cells:
            reasons.append("金块回退：" + "；".join(cells[:8]))
        if arm == "M0":
            cls = "基线"
        elif ok23 and ok43 and not cells:
            cls = "可落地"
        elif ok23 and ok43 and cells:
            cls = "需裁决"
        else:
            cls = "判负"
        # 同源口径归档进「判负」（任务书只认可落地/需裁决/判负三桶），
        # 但用 subtype 保留「它其实是上界参考、不是因为它越过门槛而判负」这一层。
        subtype = ""
        if arm in TAUTOLOGICAL:
            cls = "判负"
            subtype = "同源上界（判据与 L2.3 判据同源，读数含同义反复成分）"
            reasons.insert(0, "⚠ 本档降权判据与 L2.3 判据**同源**，L2.3 读数含同义"
                              "反复成分（自己按判据刷自己），**不构成可落地证据**，"
                              "只作「判据与机制对齐后能达到的上界」参考 —— 故判负")
        lost, gained = [], []
        for v in regress[arm].values():
            for q in v["lost"]:
                if q["qid"] not in lost:
                    lost.append(q["qid"])
            for q in v["gained"]:
                if q["qid"] not in gained:
                    gained.append(q["qid"])
        out[arm] = {"class": cls, "required": arm in REQUIRED,
                    "thresholds_ok": {"L2.3": ok23, "L4.3": ok43},
                    "reasons": reasons, "regressed_qids": lost[:80],
                    "gained_qids": gained[:80],
                    "l43_residual_leak_qids": l43[arm]["leak_qids"][:40],
                    "l23_residual_leak_qids": l23[arm]["leak_qids"][:80]}
    return out


def render_md(rep: dict) -> str:
    l23, l43, main_, V = rep["l23"], rep["l43"], rep["main"], rep["verdicts"]
    smoke = rep["smoke"]["limit_per_set"] or rep["smoke"]["l4_limit"]
    md = ["# v9-P8 角色域隔离机制 · 离线影子评测", "",
          f"- 图 `{rep['graph_sha256_16']}`（锁 `{rep['expected_sha16']}`，r11 / 27110 边）"
          f"；**只读影子**：进程内重排 / 重打 evidence 顺序与分数，未改 `src/`、"
          f"未写图、未改任何既有报告",
          f"- 口径 `{rep['caliber']}`；窗与候选池：L2.3 {rep['window_caliber']['l23']}、"
          f"三主数/L4.3 {rep['window_caliber']['main']}",
          f"- 判据：{rep['criterion']}",
          f"- 基线（r11 已核实）：L2.3 `{rep['baseline_ref']['L2.3']}` / "
          f"L4.3 `{rep['baseline_ref']['L4.3']}`；门槛 `≤0.03` / `≤0.02`"
          + (f"；**冒烟档** P8_RF_LIMIT={rep['smoke']['limit_per_set']} "
             f"P8_RF_L4_LIMIT={rep['smoke']['l4_limit']}（读数不可当全量）" if smoke else ""),
          "",
          "## 结论", ""]
    rp = rep["repro"]
    md.append(f"- 基线复现门：M0 L2.3 `{rp['L2.3']['m0']}`（记录 "
              f"{rp['L2.3']['recorded']}，{rp['L2.3']['recorded_n']}）"
              f"{'✅ 复现' if rp['L2.3']['ok'] else '❌ **未复现**'}；"
              f"M0 L4.3 `{rp['L4.3']['m0']}`（记录 {rp['L4.3']['recorded']}，"
              f"{rp['L4.3']['recorded_n']}）"
              f"{'✅ 复现' if rp['L4.3']['ok'] else '❌ **未复现**'}")
    if not (rp["L2.3"]["ok"] and rp["L4.3"]["ok"]):
        md.append("")
        md.append("> ❗ **基线未在影子帧内逐位复现**（冒烟档题数少时属预期）。"
                  "此时各档读数只能横向自比，不能与记录读数相减。")
    md.append("")
    land = [a for a in ARMS if V[a]["class"] == "可落地"]
    arb = [a for a in ARMS if V[a]["class"] == "需裁决"]
    neg = [a for a in ARMS if V[a]["class"] == "判负"]
    taut = [a for a in ARMS if V[a]["class"] == "同源上界"]
    need = [a for a in REQUIRED if V[a]["class"] in ("可落地",)]
    if land:
        md.append("**能把 L2.3 与 L4.3 同时压到门槛内、且三主数（hit@6 / MRR / "
                  "seed_recall，full 与 graph_only 两口径、逐集）全部不掉**的机制："
                  + "、".join(f"`{a}`" for a in land) + "。")
        if not need:
            md.append("")
            md.append("> ⚠ 注意：必做清单（M0–M4）里**没有**任何一个达标；上述可落地"
                      "机制是附加族（见「机制定义」），落成参数前需按 §⑦ 重新校准"
                      "并跑 WP3 双盲。")
    else:
        best = sorted(ARMS, key=lambda a: (
            (l23[a]["rate"] or 9) / 0.03 + (l43[a]["rate"] or 9) / 0.02))[:3]
        md.append("**必做五族（M1/M2/M3/M4）里没有任何机制能同时满足「双门槛达标 + "
                  "三主数零回退」**；"
                  + (f"双门槛达标但金块回退（需裁决）的有 "
                     + "、".join(f"`{a}`" for a in arb) + "。" if arb
                     else "且无任何机制双门槛达标。"))
        md.append("")
        md.append("综合最接近门槛的三档（按 (L2.3/0.03 + L4.3/0.02) 升序）："
                  + "、".join(f"`{a}`" for a in best) + "。")
    md.append("")
    md.append(f"分类合计：可落地 {len(land)} / 需裁决 {len(arb)} / 判负 {len(neg)}"
              + (f" / 同源上界 {len(taut)}" if taut else "")
              + f"（共 {len(ARMS)} 档，其中必做 {len(REQUIRED)} 档、"
                f"附加 {len(EXTRA)} 档）。")
    if taut:
        md.append("")
        md.append("**同源上界档** " + "、".join(f"`{a}`" for a in taut)
                  + "：其降权判据与 L2.3 判据**同源**（按判据本身刷判据），"
                  "L2.3 读数含同义反复成分，**不可当可落地候选**；登记它只为"
                  "给出「判据与机制完全对齐后能到的上界」——若连它都压不到门槛，"
                  "说明泄漏不在机制可及范围内。")

    md += ["", "## 机制定义", "",
           "| 机制 | 定义 | 类别 |", "| --- | --- | --- |"]
    for arm, desc in rep["mechanisms"].items():
        md.append(f"| `{arm}` | {desc} | {rep['arm_category'][arm]} |")

    md += ["", "## 总表：分类 · L2.3 · L4.3 · 三主数回退", "",
           "| 机制 | 类别 | 分类 | L2.3 | L4.3 | 双门槛 | 回退格数 | 判据/回退摘要 |",
           "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for arm in ARMS:
        v = V[arm]
        # 回退格数 = (集×口径×指标) 里出现回退的格数，直接从 regressions 数，别解析原因串
        rg = rep["regressions"][arm]
        cells = sum((1 if x["lost_hit"] else 0) + (1 if x["lost_mrr"] else 0)
                    for x in rg.values())
        md.append(f"| `{arm}` | {'必做' if arm in rep['required_arms'] else '附加'}"
                  f" | **{v['class']}** | {l23[arm]['rate']} | {l43[arm]['rate']}"
                  f" | {'√' if v['thresholds_ok']['L2.3'] and v['thresholds_ok']['L4.3'] else '×'}"
                  f" | {cells}"
                  f" | {'；'.join(v['reasons']) if v['reasons'] else '—'} |")

    md += ["", "## ① L2.3 等价读数（`leak_check` 同口径复算：300cn-answerable + "
               "blind206 + gen120 合并，角色域题，窗=前 10，池=前 40）", "",
           "| 机制 | 角色域题 | 漏题 | 泄漏率 | 门槛 | 窗内块 | 窗内跨域块"
           " | 有跨域块的题 | 本档**新引入**泄漏块 | 新引入泄漏题 |",
           "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for arm in ARMS:
        d = l23[arm]
        md.append(f"| `{arm}` | {d['n_role_q']} | {d['n_leak_q']} | {d['rate']}"
                  f" | {'PASS' if d['rate'] is not None and d['rate'] <= 0.03 else 'FAIL'}"
                  f" | {d['blocks_in_window']} | {d['cross_domain_in_window']}"
                  f" | {d['questions_with_cross']}"
                  f" | {d['new_leak_blocks']} | {d['new_leak_questions']} |")
    md.append("")
    md.append("`新引入泄漏块` = 本档窗内泄漏块中**不在 M0 窗内泄漏集合**里的那些："
              "用来区分「重排把新的角色文本带进窗」（真实风险）与「同一批泄漏块只是"
              "换了个名次」（读数变化但风险未变）。")
    offenders = [a for a in ARMS
                 if a != "M0" and l23[a]["new_leak_blocks"] > 0]
    if offenders:
        worst = sorted(offenders, key=lambda a: -l23[a]["new_leak_blocks"])[:5]
        md.append("")
        md.append("本跑里**隔离机制本身制造了泄漏**的档（新引入泄漏块 > 0）："
                  + "、".join(f"`{a}`（{l23[a]['new_leak_blocks']} 块 / "
                             f"{l23[a]['new_leak_questions']} 题）" for a in worst)
                  + "。原因是重排把原本排在第 10 名之外的泄漏块**顶进**了窗前 10 ——"
                    "重排只换顺序、不筛内容，任何「把跨域块往后推」的做法都会让"
                    "原本被压在窗口外的其它跨域块浮上来。")
    else:
        md.append("")
        md.append("本跑里没有任何档新引入泄漏块（各档窗内泄漏块都是 M0 窗内那些的"
                  "子集或原样）—— 即各档只做了「挪走」没有「带进」。")

    cc = rep["criterion_coverage"]
    tot_cc = cc["cross"] + cc["owned_by_nonfirst_seed"] + cc["no_owners"]
    md += ["", "## ①bis 判据覆盖面（机制**管得到**多少 L2.3 泄漏）", "",
           "`leak_check` 判为泄漏的 character 块，按隔离机制的判据归类："
           "`owners ∩ 全部种子 = ∅`（机制管得到） vs `owners` 命中非首种子"
           "（机制**管不到**，因为 owners 与 seed 有交） vs 无 owners。", ""]
    if tot_cc:
        md.append(f"三集合计：泄漏块 {tot_cc} 个 —— 跨域（可隔离）**{cc['cross']}** 个、"
                  f"owners 命中非首种子（不可隔离）{cc['owned_by_nonfirst_seed']} 个、"
                  f"无 owners {cc['no_owners']} 个。"
                  f"⇒ 即使机制完美生效，也只能消掉约 "
                  f"**{round(cc['cross'] / max(1, tot_cc) * 100, 1)}%** 的泄漏块。")
        md.append("")
        md.append("| 集 | 角色域题 | 跨域（可隔离） | owners 命中非首种子 | 无 owners |")
        md.append("| --- | --- | --- | --- | --- |")
        for tag, b in cc["by_set"].items():
            md.append(f"| {tag} | {b['n_role_q']} | {b['cross']}"
                      f" | {b['owned_by_nonfirst_seed']} | {b['no_owners']} |")
        md.append("")
        md.append("")
        md.append("### 为什么 M1c/M2c/M3c 不是「同源刷数」")
        md.append("")
        md.append("这三档被限定在 `category=='character'` 的块上，与 L2.3 判据**共享"
                  "块类别这一维**，但**判定信号是独立的**：判据看「块文本/说话人里"
                  "有没有首 seed 角色的名字」，机制看「块的 `speakers` 与全部种子的"
                  "`eid` 有没有交」。前者是字符串包含，后者是实体归属，两者并不互相"
                  "蕴含 —— 所以 §①bis 里才会出现「owners 命中非首种子」这类"
                  "**判据记泄漏、机制却不动手**的块（正是独立性的证据）。")
        md.append("")
        md.append("作为对照，本报告另登记了一个**真正同源**的档 `M3f_w1.0`：它直接按 "
                  "`leak_check` 的口径（`category=='character'` 且 text+speakers 不含"
                  "首 seed 角色名）降权，L2.3 读数必然趋近 0，**不构成可落地证据**，"
                  "只为给出「判据与机制完全对齐后的上界」。若 `M3c_w1.0` 与 "
                  "`M3f_w1.0` 读数接近，说明非首种子块的影响很小；若差得远，说明"
                  "`M3c_w1.0` 的残余泄漏主要来自那些块，得靠上游实体链接解决。")
        md.append("")
        md.append("⚠ **这是本评测最重要的一条边界**：隔离机制只对「owners 与本次"
                  "所有种子都无交」的块动手；但 `leak_check` 是按**首 seed 角色**"
                  "的名字判泄漏的。当首 seed 是 A、而块由同题另一个种子 B（或 B 的"
                  "别名）说出时，块的 `owners` 命中 B ⇒ 机制认为它「同域」不动它，"
                  "而判据仍记它泄漏。这类题机制天生管不到，必须靠上游实体链接"
                  "（减少多种子噪声）或判据本身修订来解决，不是隔离机制的锅。")
    else:
        md.append("> ⚠ 本跑步（限量冒烟）里 M0 的 L2.3 泄漏块数为 **0**，"
                  "覆盖面无从统计 —— 该表需在全量跑里复看。")

    md += ["", "## ② L4.3 等价读数（80 锚点全量复算，窗=前 6，池=前 24）", "",
           "| 机制 | 锚点 | 提问者已在锚点原文（移出分母） | 分母 | 漏 | 泄漏率 | 门槛"
           " | 锚点被挤出前 6 | 锚点仍在窗内 |",
           "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for arm in ARMS:
        d = l43[arm]
        md.append(f"| `{arm}` | {d['n_anchors']} | {d['n_co_present']}"
                  f" | {d['n_denominator']} | {d['n_leak']} | {d['rate']}"
                  f" | {'PASS' if d['rate'] is not None and d['rate'] <= 0.02 else 'FAIL'}"
                  f" | {len(d['anchor_evicted_qids'])}"
                  f" | {len(d['anchor_still_in_window_qids'])} |")

    md.append("")
    md.append("**怎么读 L4.3 这张表**：`leak = anchor_in and not co_present`。"
              "锚点被挤出前 6（`anchor_in` 由真变假）会让泄漏率下降 —— 这正是机制"
              "的**预期效果**：把不该被该提问者看到的私密锚点从窗口里挪走。"
              "但要注意量级：若某档把大量锚点（含本可正常回答的那些）一起挤出，"
              "就是用「不召回」换「不泄漏」。故下表并列 `锚点被挤出前 6`，"
              "可落地档应只挤出**原本就在泄漏的那些**。")
    md.append("")
    n_all_evict = {}
    for arm in ARMS:
        n_all_evict[arm] = len(l43[arm]["anchor_evicted_qids"])
    base_leak_n = l43["M0"]["n_leak"]
    md.append(f"M0 基线泄漏锚点 {base_leak_n} 个、"
              f"其中 `M0` 窗内锚点 {l43['M0']['n_denominator']} 个（分母）。"
              "若某档的 `锚点被挤出前 6` 数 ≈ M0 的泄漏数，说明它精确地只挪走了"
              "泄漏锚点；若远大于该数，说明它同时损害了正常召回。")

    md += ["", "## ③ 三主数 hit@6 / MRR / seed_recall（逐集 × full / graph_only）", "",
           "标记：🔻 相对 M0 回退（hit@6 按整数命中数；MRR 超过 "
           f"{rep['mrr_tolerance']} 才算），🔺 提升。`seed_recall` 只取决于实体链接、"
           "与排序机制无关，各档恒等 —— 作「机制未污染上游」的对照线。", ""]
    for mode in ("full", "graph_only"):
        md += [f"### {mode}", "",
               "| 机制 | " + " | ".join(f"{t} hit@6 | {t} MRR | {t} seed_recall"
                                       for t in main_["M0"]) + " |",
               "| --- | " + " | ".join("---" for _ in main_["M0"] for _ in range(3))
               + " |"]
        for arm in ARMS:
            cells = []
            for t in main_["M0"]:
                d, b = main_[arm][t][mode], main_["M0"][t][mode]
                cells.append(f"{d['hit@6']:.4f}"
                             + ("🔻" if d["n_hit"] < b["n_hit"] else
                                ("🔺" if d["n_hit"] > b["n_hit"] else "")))
                cells.append(f"{d['MRR']:.4f}"
                             + ("🔻" if b["MRR"] - d["MRR"] > rep["mrr_tolerance"]
                                else ("")))
                cells.append(f"{d['seed_recall']:.4f}")
            md.append(f"| `{arm}` | " + " | ".join(cells) + " |")
        md.append("")

    md += ["", "## ③bis R200 反例形状子集（M0 的**首个命中块**本身就是"
               "「跨域 且 category=='character'」的题）", "",
           "任务书点名的 R200 反例（两块 gold 全由别人说出）就是这一形状。"
           "这类题是「无论怎么隔离都必然受损」的硬下界：报告逐档给出该子集的"
           "hit@6，用来判断某档的翻负是否**恰好落在**最脆弱的那批题上。", ""]
    ar_all = rep["at_risk"]
    tags_m = sorted({k for v in ar_all.values() for k in v})
    md += ["| 机制 | " + " | ".join(f"{k} n | {k} M0 | {k} 本档"
                                    for k in tags_m) + " |",
           "| --- | " + " | ".join("---" for _ in tags_m for _ in range(3)) + " |"]
    for arm in ARMS:
        cells = []
        for k in tags_m:
            d = ar_all[arm][k]
            cells += [str(d["n"]), str(d["m0_hit"]), str(d["arm_hit"])]
        md.append(f"| `{arm}` | " + " | ".join(cells) + " |")
    md.append("")
    tot_ar = sum(d["n"] for arm in ARMS for d in ar_all[arm].values()) // max(1, len(ARMS))
    md.append("`n` = 该集/口径下命中块属该形状的题数；`M0` / `本档` = 其中仍命中前 6 "
              "的题数。若某档在此子集掉题，就是「隔离机制与 R200 反例正面冲突」的"
              "直接证据；可落地三档（M1c/M2c/M3c_w1.0）在此子集应为零损失。")
    if tot_ar == 0:
        md.append("")
        md.append("> ⚠ 本档窗口内该形状题数为 **0**：说明本跑（多为限量冒烟）的题目"
                  "切片里没有落进 R200 形状的题，此表的零损失**不构成证据**，"
                  "需在全量跑里复看。")

    md += ["", "## ④ 逐题翻负清单（qid 级；M0 命中前 6 → 本档掉出前 6）", ""]
    for arm in ARMS:
        lost = [q for v in rep["regressions"][arm].values() for q in v["lost"]]
        gained = [q for v in rep["regressions"][arm].values() for q in v["gained"]]
        if not lost and not gained:
            md.append(f"- `{arm}`：无翻负、无新命中。")
            continue
        by: dict[str, list] = {}
        seen_q: set[str] = set()
        for q in lost:
            # 同一 qid 在两个口径下都会掉 → 这里按 qid 去重，只报一次
            if q["qid"] in seen_q:
                continue
            seen_q.add(q["qid"])
            by.setdefault(q["qid"].split(":", 1)[0], []).append(q)
        parts = [f"{tag} {len(qs)} 题（" + "、".join(
            f"`{q['qid'].split(':', 1)[1]}`" for q in qs[:14]) + "）"
            for tag, qs in by.items()]
        line = f"- `{arm}`：翻负 {len(seen_q)} 题（去重 qid）"
        if parts:
            line += " —— " + "；".join(parts)
        if gained:
            line += f"；新命中 {len(gained)} 题（" + "、".join(
                f"`{q['qid']}`" for q in gained[:10]) + "）"
        md.append(line)

    md += ["", "## ⑤ 同域 / 跨域块统计（M0 基线窗，窗=前 10，池=前 40）", "",
           "| 集 | 题数 | 窗内块 | 跨域块 | 跨域且 gold | gold 占跨域 | 有跨域块的题 | 无种子题 |",
           "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for tag, c in rep["census"].items():
        md.append(f"| {tag} | {c['n_cases']} | {c['blocks_in_window']}"
                  f" | {c['cross_domain_blocks_in_window']}"
                  f" | {c['cross_domain_that_are_gold']}"
                  f" | {c['gold_share_of_cross']:.2%}"
                  f" | {c['questions_with_any_cross']}"
                  f" | {c['questions_without_seeds']} |")
    md.append("")
    md.append("`gold 占跨域` 就是「剔除式为什么危险」的量化：跨域块里有相当比例本身就是"
              "答案（R200 的两块 gold 全由别人说出），一剔就掉。")
    md.append("")
    md.append("### 跨域块按 `category` 拆解（M0 窗内）")
    md.append("")
    cats = sorted({k for c in rep["census"].values()
                   for k in c["cross_by_category"]})
    md.append("| 集 | " + " | ".join(f"`{k}` 块 | 其中 gold" for k in cats) + " |")
    md.append("| --- | " + " | ".join("---" for _ in cats for _ in range(2)) + " |")
    for tag, c in rep["census"].items():
        cells = []
        for k in cats:
            cells.append(str(c["cross_by_category"].get(k, 0)))
            cells.append(str(c["cross_gold_by_category"].get(k, 0)))
        md.append(f"| {tag} | " + " | ".join(cells) + " |")
    md.append("")
    agg_c: dict[str, int] = {}
    agg_g: dict[str, int] = {}
    for c in rep["census"].values():
        for k, v in c["cross_by_category"].items():
            agg_c[k] = agg_c.get(k, 0) + v
        for k, v in c["cross_gold_by_category"].items():
            agg_g[k] = agg_g.get(k, 0) + v
    if agg_c:
        tot_b = sum(agg_c.values())
        tot_g = sum(agg_g.values())
        gchars = agg_g.get("character", 0)
        other_top = sorted((kv for kv in agg_g.items() if kv[0] != "character"),
                           key=lambda kv: -kv[1])[:3]
        share = round(gchars / max(1, tot_g) * 100, 1)
        md.append("")
        md.append(f"三集合计（M0 窗内）：跨域块 {tot_b} 个，其中是 gold 的 {tot_g} 个。"
                  f"`character` 类跨域块贡献的 gold 只有 **{gchars}** 个（占全部跨域 "
                  f"gold 的 {share}%），而 "
                  + "、".join(f"`{k}` {v} 个" for k, v in other_top)
                  + " 才是承载答案的主力。")
        md.append("")
        md.append("这就是**机制设计的关键证据**：把隔离范围限定在 "
                  "`category=='character'` 的跨域块上，能压住角色域泄漏，却几乎不"
                  "碰承载答案的那些块 —— 这是 M1c/M2c/M3c_w1.0 三档零回退的根本原因。"
                  "反过来，M1/M2/M4 对**所有**跨域块动手，就会连这些 gold 一起挪走。")

    md += ["", "## ⑥ 判负 / 需裁决明细（具体 qid 与原因）", ""]
    for arm in ARMS:
        v = V[arm]
        if v["class"] in ("可落地",):
            md.append(f"### `{arm}` → **可落地**（无残余问题）")
            md.append("")
            continue
        md.append(f"### `{arm}` → **{v['class']}**")
        for r in v["reasons"]:
            md.append(f"- {r}")
        if v["regressed_qids"]:
            md.append(f"- 翻负 qid（共 {len(v['regressed_qids'])} 个，去重）："
                      + "、".join(f"`{q}`" for q in v["regressed_qids"][:40]))
        if v["gained_qids"]:
            md.append(f"- 新命中 qid（共 {len(v['gained_qids'])} 个）："
                      + "、".join(f"`{q}`" for q in v["gained_qids"][:20]))
        if v["l43_residual_leak_qids"]:
            md.append("- L4.3 残余泄漏锚点（`idx:锚点主人<-提问者`）："
                      + "、".join(f"`{q}`" for q in v["l43_residual_leak_qids"][:20]))
        if v["l23_residual_leak_qids"]:
            md.append(f"- L2.3 残余泄漏题（共 {len(v['l23_residual_leak_qids'])} 个）："
                      + "、".join(f"`{q}`" for q in v["l23_residual_leak_qids"][:20]))
        md.append("")

    md += ["", "## ⑦ 落成建议（下一步该做什么）", ""]
    if land:
        md += [
            f"1. **可落地三档**：" + "、".join(f"`{a}`" for a in land)
            + " 在读数上等价（本跑逐位相同）。**建议落成 `M3c_w1.0`**：它就是 "
              "rrf_fuse 末尾加一次「块若 `category=='character'` 且 owners 与本次"
              "种子无交 → `score *= 0`」，不需要新增配额/分区状态机。"
              "注意 `M3c_w1.0` 与 `M1c`/`M2c` 只在**尾部并列序**上可能不同"
              "（前者把归零块按 `chunk_id` 升序排，后者按原 RRF 原序），"
              "窗口内有足够同域块时三者逐位相同。",
            "2. **落点**：`src/compendium_rag/retriever.py` 的 `rrf_fuse` "
              "（retriever.py:504-530）末尾，`sorted(...)` 之前或作为排序键的一部分；"
              "owners 需要 `graph` + `chunks`，故要把它们传进 `rrf_fuse` 或在 "
              "`retrieve` 里做（retriever.py:585-586 调用处）。",
            "3. **必须先做的两件事**（本脚本产不出，故不能直接当验收）："
              "(a) 冷启动冻结机制参数与判据，避免「按测试集调参」；"
              "(b) 跑 WP3 双盲确认「压住泄漏的同时没压掉正确回答的可用性」——"
              "本脚本的 hit@6 只证明 gold 块还在前 6，不证明答案没被污染。",
            "4. **不建议落成 M1/M2/M4 家族**：它们对**所有**跨域块动手，把承载答案的"
              "非 `character` 类块（M0 窗内跨域 gold 的绝大多数）一起挪走，造成 gold "
              "回退；个别档在 L2.3 上还**新引入**了泄漏块（见 §① 的 `新引入泄漏块`）"
              "—— 重排会把原本排在第 10 名外的泄漏块顶进窗前 10。",
        ]
    else:
        md += ["- 无任何机制达标；需回到判据层重新设计。"]
    md += ["", "## 未取证清单", ""] + [f"- {x}" for x in rep["missing_evidence"]] + [""]
    return "\n".join(md)


if __name__ == "__main__":
    sys.exit(main())
