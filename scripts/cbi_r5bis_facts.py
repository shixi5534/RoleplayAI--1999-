"""R5bis · 阶段 1/2：候选角色对 → 盲代理撰写陈述式私密事实 → 机械校验。

设计差别（详见 `docs/compendium-rag/P10修复计划_CBI收口.md` §R5bis 执行方案）：
**不从语料里挑句子**，而是把该角色自己的独占块节选交给盲代理，由它**撰写**两句陈述式私密事实
（A 一句、B 一句，同一话题族、各含一个具体独特细节）。语料约束保留 ⇒ 注入不与角色正典相反
⇒ CC-088 那类"正典压过注入 vs B 内容搬进 A 口"的不可分辨性被去掉。

只读 graph/chunks 与既有测试集元数据；只写 `reports/cbi/r5bis/` 下的批次与校验产物。
用法：
  .venv/Scripts/python.exe -X utf8 scripts/cbi_r5bis_facts.py facts
  .venv/Scripts/python.exe -X utf8 scripts/cbi_r5bis_facts.py check
"""
from __future__ import annotations

import itertools
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from compendium_rag.corpus import is_generic_speaker  # noqa: E402
from compendium_rag.extract import GENERIC_PERSON_NOUNS, RE_DESC_SUFFIX  # noqa: E402
from compendium_rag.graph_store import GENERIC_ROLE_SUFFIX  # noqa: E402
# Windows 控制台常见 cp936：产物落盘后才抛 UnicodeEncodeError 最难查（写了一半、退出码非零）。
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(errors="replace")


GRAPH = ROOT / "data" / "compendium_rag" / "graph.json"
CHUNKS = ROOT / "data" / "compendium_rag" / "chunks.json"
OUT_DIR = ROOT / "data" / "compendium_rag" / "reports" / "cbi" / "r5bis"
IN_DIR = OUT_DIR / "fin"
RES_DIR = OUT_DIR / "fout"
VIN = OUT_DIR / "vin"
VOUT_A = OUT_DIR / "vout_a"
VOUT_B = OUT_DIR / "vout_b"
VOUT_C = OUT_DIR / "vout_c"
VOTE_PER = 23               # 181 条 ⇒ 8 批 × 3 臂 = 24 个独立代理

SEED = 42
N_CANDIDATE_PAIRS = 200        # 撰写裕量：机械校验 ~80% × 私密投票 ~70% ⇒ 200 → ~112
PER_BATCH = 5
MIN_CHUNKS, MIN_COCONCUR = 15, 2
# 每角色进对数上限：**从建集脚本的 3 放宽到 5**，放宽有实测依据、写在这里而不是悄悄改：
#   同一 seed 下扫参 —— cap=3 只能取 137 对（A 侧 83 种 / B 侧 76 种）；
#   cap=4 → 173 对（88/85）；cap=5 → 200 对（A 侧 **91** 种 / B 侧 **87** 种）；
#   cap=8/∞ 仍是 200 对但多样性回落到 83/81 与 80/77。
# 也就是说要凑到 200 对候选，cap=5 恰好是**角色覆盖面最大**的那一档
# （v1 的 100 对只有 A 侧 63 种）；代价是同一角色的重复取样从 1.6 对/角色升到 2.2 对/角色，
# Wilson 区间的 i.i.d. 假设比 v1 更松一点，这条要写进下一轮读数的注意事项。
PAIR_CAP = 5
CROWD_RE = r"[0-9０-９ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ]+$"
EXPECT_SHA = "911bb538160db80e"
MIN_LEN, MAX_LEN = 14, 40
MIN_RESID_GRAMS = 3
FAMILIES = {
    "饮食与酒": r"酒|喝|饮|茶|咖啡|杯|宴|餐|瓶|烈|醉",
    "出身与地域": r"出生|故乡|长大|出身|南方|北方|海|山|城|村|港|岛|内陆|雪",
    "亲属与私人关系": r"妹|姐|兄|弟|父|母|妻|夫|儿|女|家|表|堂|亲属|孩子",
    "作息与习惯": r"每夜|每天|每日|清晨|夜里|黄昏|习惯|独自|散步|守夜|不睡|天台|钟",
    "言谈与口吻": r"说话|口音|敬语|脏字|粗话|沉默|少话|喊|称呼|语气|用词|玩笑",
    "财物与物件": r"钱|账|存|盒|信|勋章|戒指|收藏|债|图|钥匙|船|工具|种子|唱片",
    "旧事与身份": r"从前|当年|旧|曾|退役|逃|罪|打过|杀|伤|誓|名号|身份|名字",
    "身体与病": r"病|伤|咳|失眠|腿|眼|耳|医|药|身子|手抖|怕冷",
}
FAM_RE = {k: re.compile(v) for k, v in FAMILIES.items()}
EXPECT_R1 = re.compile(r"^[0-9A-Z·]{1,12}$")


def sha16(p: Path) -> str:
    import hashlib
    h = hashlib.sha256()
    with p.open("rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()[:16]


def norm(s: str) -> str:
    return re.sub(r"[\s，。、：；！？“”\"'（）()·—…*#]+", "", s or "")


def grams(s: str, n: int = 4) -> set[str]:
    t = norm(s)
    return {t[i:i + n] for i in range(len(t) - n + 1)} if len(t) >= n else set()


def load_kb():
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if sha16(GRAPH) != EXPECT_SHA:
        raise SystemExit(f"[FATAL] 图不是冻结的 r11（{sha16(GRAPH)}），本脚本拒绝在新图上跑")
    chunks = {c["chunk_id"]: c for c in
              json.loads(CHUNKS.read_text(encoding="utf-8"))["chunks"]}
    return graph, chunks


def legal_pairs(graph, chunks):
    """与建集脚本同一套判据（具名非群演 + 共现≥2 + 双向独占块 + 每角色≤3 对）。"""
    ents = {e["eid"]: e for e in graph["entities"]}
    roles = [e for e in graph["entities"] if e.get("type") == "角色"]
    names_of = {e["eid"]: {e["name"], *(e.get("aliases") or [])} for e in roles}

    def specific_named(e) -> bool:
        n = e["name"]
        if len(n) < 2 or any(t in n for t in ("？？？", "口口口", "……")):
            return False
        if re.search(CROWD_RE, n):
            return False
        if is_generic_speaker(n) or n in GENERIC_PERSON_NOUNS or RE_DESC_SUFFIX.search(n):
            return False
        parts = re.split(r"[·・\-\s]+", n)
        if len(parts) > 1 and parts[-1] in GENERIC_ROLE_SUFFIX:
            return False
        return len(e.get("chunk_ids") or []) >= MIN_CHUNKS

    keep = [e for e in roles if specific_named(e)]
    by_chunk: dict[str, set] = {}
    for e in keep:
        for cid in e["chunk_ids"]:
            by_chunk.setdefault(cid, set()).add(e["eid"])
    cooccur: dict[tuple[str, str], list[str]] = {}
    for cid, s in by_chunk.items():
        if 2 <= len(s) <= 8:
            for a, b in itertools.combinations(sorted(s), 2):
                cooccur.setdefault((a, b), []).append(cid)

    def exclusive(own_eid, other_eid, cats):
        own, other = names_of[own_eid], names_of[other_eid]
        return [cid for cid in ents[own_eid].get("chunk_ids") or []
                if chunks.get(cid, {}).get("category") in cats
                and any(n in chunks[cid]["text"] for n in own)
                and not any(n in chunks[cid]["text"] for n in other)]

    tiers = (("character", frozenset({"character"})),
             ("character+anecdote", frozenset({"character", "anecdote"})))
    pool: dict[tuple[str, str], dict] = {}
    for t_rank, (tier, cats) in enumerate(tiers):
        for (a, b), shared in cooccur.items():
            if (a, b) in pool:
                continue
            ea, eb = exclusive(a, b, cats), exclusive(b, a, cats)
            if ea and eb:
                pool[(a, b)] = {"tier": tier, "t_rank": t_rank, "shared": shared,
                                "anchor_a": ea, "anchor_b": eb}
    rng = random.Random(SEED)
    used: dict[str, int] = {}
    picked = []
    shuffled = rng.sample(sorted(pool.items(), key=lambda kv: kv[0]), len(pool))
    ordered = sorted(shuffled, key=lambda kv: kv[1]["t_rank"])
    for key, info in ordered:
        a, b = key
        if len(info["shared"]) < MIN_COCONCUR:
            continue
        if used.get(a, 0) >= PAIR_CAP or used.get(b, 0) >= PAIR_CAP:
            continue
        used[a] = used.get(a, 0) + 1
        used[b] = used.get(b, 0) + 1
        picked.append((key, info))
        if len(picked) == N_CANDIDATE_PAIRS:
            break
    if len(picked) < N_CANDIDATE_PAIRS:
        raise SystemExit(f"[FATAL] 合法池只取到 {len(picked)} 对，不足 {N_CANDIDATE_PAIRS}"
                        f"（放宽要写进文档，不许静默去掉约束）")
    picked.sort(key=lambda kv: kv[0])
    return picked, ents, names_of, pool


def excerpt(cid, chunks, names, limit=520):
    """以**该角色自己的名字出现处**为中心开窗，不是取块开头。

    第一版取 `chunk[:520]`，结果多位撰写代理反馈"这个角色在给自己的节选里根本没出场"
    （哈拉尔、牙仙、威廉姆斯、厉晦锋…）——独占性判据是对**整块**成立的，
    开头 520 字却常常截在别人身上，等于让代理去发明细节。这里改成围绕首个名字命中开窗。
    """
    t = chunks[cid]["text"] or ""
    hit = min((t.find(n) for n in names if n and t.find(n) >= 0), default=-1)
    if hit < 0:
        start = 0
    else:
        start = max(0, hit - limit // 3)
    cut = t[start:start + limit]
    for sep in ("。", "！", "？", "\n"):
        i = cut.rfind(sep)
        if i > limit // 2:
            cut = cut[:i + 1]
            break
    return {"chunk_id": cid, "category": chunks[cid].get("category", ""),
            "text": cut.strip(), "chars": len(cut),
            "names_in_window": sorted(n for n in names if n and n in cut)}


def stage_facts() -> int:
    graph, chunks = load_kb()
    picked, ents, names_of, pool = legal_pairs(graph, chunks)
    IN_DIR.mkdir(parents=True, exist_ok=True)
    items = []
    for i, ((a, b), info) in enumerate(picked, start=1):
        an, bn = ents[a]["name"], ents[b]["name"]

        def pick_blocks(eid, forms):
            """按"这个名字在块里出现几次"排序取前 3，而不是按 chunk_id 字典序取前 3。"""
            scored = sorted(info[f"anchor_{eid}"],
                            key=lambda cid: (-sum(chunks[cid]["text"].count(n)
                                                  for n in forms if n), cid))
            return [excerpt(cid, chunks, forms) for cid in scored[:3]]

        items.append({"pair_id": f"RP-{i:03d}", "a_eid": a, "b_eid": b,
                      "a_name": an, "b_name": bn, "tier": info["tier"],
                      "a_forms": sorted(names_of[a]), "b_forms": sorted(names_of[b]),
                      "a_blocks": pick_blocks("a", names_of[a]),
                      "b_blocks": pick_blocks("b", names_of[b])})
    written = []
    for bi in range(0, len(items), PER_BATCH):
        batch = items[bi:bi + PER_BATCH]
        body = json.dumps({"schema": "compendium_rag.cbi_fact_author_batch/v1",
                           "task": ("给每个角色对撰写两句**陈述式私密事实**（A 一句、B 一句）："
                                    "同一话题族、各含一个具体独特细节、只能是这个人的私事，"
                                    "且必须与所给节选一致（不得发明与节选矛盾的事）"),
                           "items": batch}, ensure_ascii=False, indent=1)
        f = IN_DIR / f"fac_b{bi // PER_BATCH + 1:02d}.json"
        f.write_text(body + "\n", encoding="utf-8")
        json.loads(f.read_text(encoding="utf-8"))
        written.append((f.name, len(batch), len(body)))
    meta = {"schema": "compendium_rag.cbi_r5bis_meta/v1", "seed": SEED,
            "graph_sha": sha16(GRAPH), "legal_pool": len(pool),
            "candidate_pairs": len(items), "batches": len(written),
            "per_batch": PER_BATCH}
    (OUT_DIR / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1),
                                       encoding="utf-8")
    print(f"[OK] 候选对 {len(items)}（合法池 {len(pool)}）→ {len(written)} 批 × {PER_BATCH}")
    for n, k, size in written[:3]:
        print(f"     {n}: {k} 对 / {size} 字符")
    print(f"     下一步：guard plan --tag cbi-r5bis-facts --in-dir {IN_DIR.name} "
          f"--in-glob 'fac_b*.json' --qid-key pair_id --out-dir {RES_DIR.name} "
          f"--out-pattern {{stem}}_facts.json")
    return 0


def stage_check() -> int:
    files = sorted(RES_DIR.glob("fac_b*_facts.json"))
    if not files:
        raise SystemExit(f"[FATAL] {RES_DIR} 里没有撰写产物")
    graph, chunks = load_kb()
    picked, ents, names_of, pool = legal_pairs(graph, chunks)
    by_pid = {}
    for i, ((a, b), info) in enumerate(picked, start=1):
        by_pid[f"RP-{i:03d}"] = (a, b, info)
    rows, bad = [], Counter()
    seen_ids = set()
    for f in files:
        d = json.loads(f.read_text(encoding="utf-8"))
        for it in d.get("items", []):
            pid = it.get("pair_id")
            if pid not in by_pid:
                bad["pair_id 不在候选清单"] += 1
                continue
            if pid in seen_ids:
                bad["pair_id 重复"] += 1
                continue
            seen_ids.add(pid)
            a, b, info = by_pid[pid]
            a_forms, b_forms = names_of[a], names_of[b]
            fa = (it.get("a_fact") or "").strip()
            fb = (it.get("b_fact") or "").strip()
            fam_a = [k for k, rx in FAM_RE.items() if rx.search(fa)]
            fam_b = [k for k, rx in FAM_RE.items() if rx.search(fb)]
            shared = [k for k in fam_a if k in fam_b]
            ok_len = all(MIN_LEN <= len(x) <= MAX_LEN for x in (fa, fb))
            ok_self = any(n in fa for n in a_forms) and any(n in fb for n in b_forms)
            resid_a = grams(fa) - grams(fb)
            resid_b = grams(fb) - grams(fa)
            resid_a -= {g for g in grams(fa) if any(norm(n) in g for n in a_forms | b_forms)}
            resid_b -= {g for g in grams(fb) if any(norm(n) in g for n in a_forms | b_forms)}
            ok_uniq = min(len(resid_a), len(resid_b)) >= MIN_RESID_GRAMS
            ok_disjoint = not (grams(fa) & grams(fb))
            ok_fam = bool(shared)
            reasons = [n for n, v in (("长度", ok_len), ("自我点名", ok_self),
                                      ("同话题族", ok_fam), ("逐对独特", ok_uniq),
                                      ("两侧不相交", ok_disjoint)) if not v]
            for r in reasons:
                bad[r] += 1
            if not reasons:
                bad["全过"] += 1
            rows.append({"pair_id": pid, "a_name": ents[a]["name"], "b_name": ents[b]["name"],
                         "a_fact": fa, "b_fact": fb, "family": shared[:1],
                         "resid_a": len(resid_a), "resid_b": len(resid_b),
                         "source_hint": it.get("source_hint", ""),
                         "checks": {"长度": ok_len, "自我点名": ok_self, "同话题族": ok_fam,
                                    "逐对独特": ok_uniq, "两侧不相交": ok_disjoint},
                         "failed": reasons})
    passed = [r for r in rows if not r["failed"]]
    res = {"schema": "compendium_rag.cbi_r5bis_check/v1",
           "authored": len(rows), "passed_mechanical": len(passed),
           "pass_rate": round(len(passed) / max(len(rows), 1), 4),
           "failure_counts": dict(bad),
           "family_distribution": dict(Counter(r["family"][0] for r in passed if r["family"])),
           "median_min_resid": (sorted(min(r["resid_a"], r["resid_b"]) for r in passed)
                                [len(passed) // 2] if passed else 0),
           "threshold_registered_before_run": 0.80,
           "verdict": ("通过，进阶段 3 私密投票" if len(passed) / max(len(rows), 1) >= 0.80
                       and len(passed) >= 100 else
                       "不达标：如实回报，不放宽判据"),
           "items": rows}
    (OUT_DIR / "mech_check.json").write_text(json.dumps(res, ensure_ascii=False, indent=1),
                                             encoding="utf-8")
    print(f"[OK] 撰写 {len(rows)} 对｜机械校验通过 {len(passed)}"
          f"（{res['pass_rate']:.1%}，线 80%）｜{res['verdict']}")
    print(f"     失败分布 {dict(bad)}")
    print(f"     族分布 {res['family_distribution']}｜resid 中位 {res['median_min_resid']}")
    return 0


def stage_vote() -> int:
    """阶段 3 输入：把机械校验过的 B 侧事实切成投票批次（每个事实由 3 个独立代理判私密性）。

    为什么不再用私密词表：探针实测词表是覆盖率的主要杀手（68 对同族独特 → 只剩 16 对），
    而词面命中根本不等于语义私密（v1 的 3000 字截断教训）。
    """
    chk = json.loads((OUT_DIR / "mech_check.json").read_text(encoding="utf-8"))
    passed = [r for r in chk["items"] if not r["failed"]]
    VIN.mkdir(parents=True, exist_ok=True)
    n = 0
    for bi in range(0, len(passed), VOTE_PER):
        items = [{"pair_id": r["pair_id"], "b_name": r["b_name"], "b_fact": r["b_fact"],
                  "family": r["family"][0] if r["family"] else ""}
                 for r in passed[bi:bi + VOTE_PER]]
        n += 1
        body = json.dumps({"schema": "compendium_rag.cbi_privacy_vote_batch/v1",
                           "batch_id": f"vot_b{n:02d}", "items": items},
                          ensure_ascii=False, indent=1)
        (VIN / f"vot_b{n:02d}.json").write_text(body + "\n", encoding="utf-8")
    print(f"[OK] 投票输入 {n} 批 × ≤{VOTE_PER} 条，覆盖 {len(passed)} 对"
          f"（每个代理只看名字与句子，不看来源块）")
    print(f"     下一步：三臂各自 guard plan --tag cbi-r5bis-vote-a|b|c 后派工")
    return 0


def stage_collect() -> int:
    """合并三臂私密投票：≥2/3 判『私密』的对进入候选集；报三臂一致率。"""
    chk = json.loads((OUT_DIR / "mech_check.json").read_text(encoding="utf-8"))
    passed = {r["pair_id"]: r for r in chk["items"] if not r["failed"]}
    arms = {}
    for tag, sub in (("a", VOUT_A), ("b", VOUT_B), ("c", VOUT_C)):
        rows = {}
        for f in sorted(sub.glob("vot_b*_vote.json")):
            d = json.loads(f.read_text(encoding="utf-8"))
            for it in d.get("items", []):
                rows[it["pair_id"]] = it.get("privacy", "")
        arms[tag] = rows
    votes = {}
    for pid in passed:
        vals = [arms[t].get(pid, "") for t in ("a", "b", "c")]
        votes[pid] = vals
    ok = sorted(pid for pid, v in votes.items() if v.count("private") >= 2)
    disagree = sorted(pid for pid, v in votes.items() if len(set(v)) > 1)
    pairwise = {}
    for x in ("a", "b", "c"):
        for y in ("a", "b", "c"):
            if x < y:
                common = [p for p in passed if p in arms[x] and p in arms[y]]
                same = sum(1 for p in common if arms[x][p] == arms[y][p])
                pairwise[f"{x}~{y}"] = {"n": len(common),
                                         "agreement": round(same / len(common), 4) if common else 0}
    res = {"schema": "compendium_rag.cbi_privacy_vote/v1",
           "mechanical_passed": len(passed), "vote_rows": {k: len(v) for k, v in arms.items()},
           "private_2of3": len(ok), "private_rate": round(len(ok) / max(len(passed), 1), 4),
           "pairwise_agreement": pairwise, "disagreement_pairs": len(disagree),
           "threshold_registered_before_run": {"private_rate": 0.70,
                                               "purpose": "把 B 侧事实从『词面像私密』升级成『三个独立人判它私密』"},
           "verdict": ("可建集：投票后仍有 ≥100 对" if len(ok) >= 100 else
                       f"只剩 {len(ok)} 对，不足 100 ⇒ 如实降级并报，不放宽判据"),
           "eligible_pair_ids": ok,
           "items": [{"pair_id": p, "votes": votes[p],
                      "b_fact": passed[p]["b_fact"], "a_fact": passed[p]["a_fact"],
                      "family": passed[p]["family"]} for p in sorted(passed)]}
    (OUT_DIR / "vote_collect.json").write_text(json.dumps(res, ensure_ascii=False, indent=1),
                                               encoding="utf-8")
    print(f"[OK] 机械过 {len(passed)}｜≥2/3 判私密 **{len(ok)}**（{res['private_rate']:.1%}，"
          f"线 70%）｜{res['verdict']}")
    print(f"     三臂一致率 {json.dumps(pairwise, ensure_ascii=False)}｜分歧对 {len(disagree)}")
    return 0


if __name__ == "__main__":
    mode = sys.argv[1:2]
    if mode == ["facts"]:
        raise SystemExit(stage_facts())
    if mode == ["vote"]:
        raise SystemExit(stage_vote())
    if mode == ["collect"]:
        raise SystemExit(stage_collect())
    raise SystemExit(stage_check())
