# -*- coding: utf-8 -*-
"""R2-repairer step 3: verdict table + self-validation + proposal.json builder.

Read-only on graph.json/chunks.json/testset/triage.
Writes repairs_v2/proposal.json and repairs_v2/_r2_step3_selfval.json.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
OUT_DIR = REPO / "data/compendium_rag/repairs_v2"


def _name_matches(name: str, ql: str) -> bool:
    if not name or not ql:
        return False
    is_ascii = all(ord(c) < 128 for c in name)
    if is_ascii:
        pat = re.compile(r"(?<![A-Za-z0-9_])" + re.escape(name.lower()) +
                         r"(?![A-Za-z0-9_])")
        return bool(pat.search(ql))
    if len(name) >= 2:
        return name in ql
    return bool(re.search(r"(?<![\u4e00-\u9fff])" + re.escape(name) +
                          r"(?![\u4e00-\u9fff])", ql))


# ── verdict tables (adjudication fixed here; see proposal_v2.md for reasoning) ──

REMOVE = {
    "信": "单字常用字，DF1374 中 owner(信仰) 仅 2 块逐字；审计明示三条单字一并摘除；ts=0；灰机无此名",
    "门": "单字，DF1139 中 owner(神殿之门) 仅 11 块；灰机『门』是角色页(Door, pageid≈2085)，挂神殿之门属跨实体冲突；ts=0",
    "线": "单字，DF1008 中 owner(金线) 仅 1 块；审计明示摘除；ts=0",
    "两人": "纯数量泛指，DF148 中 owner(逃兵) 0 块逐字（死 alias 兼泛称）；ts=0",
    "总部": "DF136 中 owner(圣洛夫基金会总部) 仅 1 块；ts=0",
    "街道": "DF131 中 owner(乌斯怀亚) 仅 4 块；城市节点吸入子地点的存量实例（审计检4.1）；限定形 乌斯怀亚·街道 保留；ts=0",
    "老板": "DF124 中 owner(勿忘我) 仅 2 块；R228(拉米雷斯保安公司的老板) 答案=Melania，本 alias 种错人；ts=1 全为误种子",
    "石头": "DF121 中 owner(龙涎香) 仅 6 块；ts=0",
    "怪物": "DF107 中 owner(奇美拉) 仅 6 块；R062/R069/R076 答案均为巨怪(troll)，3 次误种子；灰机无奇美拉页",
    "委员会": "DF99 中 owner(联合委员会) 17 块；限定形 基金会联合委员会/基金委 保留；ts=0",
    "家族": "DF93 中 owner(泰内布朗热家) 仅 1 块；R087/R259 答案均非泰内布朗热家，2 次误种子；ts=2 全为误",
    "地图": "DF86 中 owner(手绘地图) 13 块；限定形 南极神秘学地图/诺谛卡的地图 保留；ts=0",
    "信徒": "DF82 中 owner(重塑·信徒) 21 块；限定形 重塑信徒/黑袍信徒 保留；ts=0",
    "幽灵": "DF81 中 owner(游灵) 仅 6 块；ts=0",
    "学派": "DF78 中 owner(阿派朗学派) 21 块；ts=0",
    "幻觉": "DF75 中 owner(施特林) 仅 1 块；ts=0",
    "仪器": "DF74 中 owner(人工梦游训练仪) 仅 1 块；ts=0",
    "小家伙": "爱称泛指，DF71 中 owner(阿黛拉的小龙) 3 块；小龙/幼龙 保留；ts=0",
    "装置": "DF71 中 owner(环境监测装置) 仅 1 块；R127/R170(pool-out)＋R180/R240 4 次误种子（答案均非环境监测装置）；摘除只减误伤",
    "同胞": "DF70 中 owner(神秘学家) 仅 5 块；ts=0",
    "城里": "方位泛指，DF70 中 owner(别列格勒) 10 块；ts=0",
    "迷宫": "DF58 中 owner(石壁迷宫) 仅 5 块；限定形 玄武岩迷宫 保留；ts=0",
    "教堂": "DF57 中 owner(悲伤圣母教堂) 仅 2 块；ts=0",
    "玛丽": "DF57 中 owner(圣路连士兵) 仅 1 块；多主 alias（圣路连士兵/玛丽安娜 setdefault 抢注歧义，审计检3）；从两 owner 一并摘除；R3 同物异写复核",
    "符号": "DF52 中 owner(禁锢术式) 仅 1 块；ts=0",
    "哥哥": "亲属泛称，DF51 中 owner(卡卡尼亚之兄) 仅 1 块；ts=0",
    "副作用": "DF50 中 owner(诅咒) 3 块；ts=0",
    "别斯米尔": "P0 焊组残留：语料明文否认（mainline__110_复乐园:19.0.1 德洛丝自述『应该并不是我』），灰机有独立 NPC 条目 别斯米尔/Bessmert；DF67 中 owner(卡卡尼亚) 仅 1 块；R1 将建独立节点",
    "组长": "DF77 中 owner(乌尔里希) 37 块但跨篇泛称 40 块；限定形 乌尔里希组长/破译组长 保留；R3 合并 暴雨小组组长乌尔里希 后可达性恢复；ts=0",
    "学校": "DF157 中 owner(第一防线学校) 70 块；ts 两问均含全称 第一防线学校（canonical 直配，alias 冗余）；87 块跨篇泛称",
    "妹妹": "亲属泛称，DF62 中 owner(洛佩拉) 10 块；限定形 亲爱的妹妹 保留；ts=0",
    "伞": "DF64 中 owner(平衡伞) 28 块；限定形 便携式平衡伞 保留；ts=0",
    "头儿": "跨篇上级称呼，DF74 中 owner(维尔汀) 24 块、50 块他指；维尔汀余 8 条逐字 alias；ts=0",
    "老爷": "跨篇主家称呼（帕米埃老爷等），DF77 中 owner(维尔汀) 26 块、51 块他指；灰机维尔汀页引文含『老爷』一次（已记录）；ts=0",
    "老朋友": "跨篇客套称呼，DF48 中 owner(邓肯先生) 仅 4 块；R018 错种子家族；ts=1 即 R018 本身",
    "老伙计": "R018 实测错种子源（alias 0.9 → 邓肯先生，retriever.py:290 长名优先子串匹配）；DF24 散布 11 篇 21 块他指；owner 余 7 条逐字 alias",
}

KEEP = {
    "基金会": "430/800 块在 owner(圣洛夫基金会) 声称块逐字出现，是语料对该实体的常态称呼；12 个 ts 命中全部语义正确且多数仅靠 bare『基金会』触发（R054/R181/R236/R242/R286/R290）；摘除将致现役可答题回归。残余风险：370 块他指（含含『基金会』的机构名）如实记录",
    "重塑": "327/506 块 owner 逐字；12 个 ts 命中全部含全称 重塑之手（alias 在评测冗余且无害）；语料标准优先；179 块他指记录",
    "司辰": "314/356(88%) owner 逐字；灰机有独立页 司辰(pageid 211)，维尔汀页正文以『司辰{{cb|Timekeeper}}』定义；handoff §3 豁免；4 个 ts 命中全部正确",
    "拉普拉斯": "131/255 owner 逐字（语料对科算中心的常态简称）；handoff §3 豁免；R191/R211（答案 Laplace）靠它种子；R170 的『巨节点种子过粗』归因 R3 玩具盒新抽取解决；124 块他指记录",
    "助手": "69/118 owner 逐字；R236『基金会的首席助手』现役可答题靠它种子十四行诗（审计『至少摘除』清单未测此题）——新发现，已按作战书 §0 补录",
    "保罗": "handoff §3.5 真名（保罗·霍伊默尔 逐字 alias 保留）；R265 现役可答题经『圣保罗』子串触发卡戎种子并可能经 PPR 救回 gold；19 块 owner 逐字；qualify 备选（→保罗·霍伊默尔）留复核人裁决",
    "康复中心": "30/59 owner 逐字；R235/R271/R288 三题种子语境全部正确；摘除有回归风险",
    "军长": "46/55(84%) owner 逐字；ts=0；军长伊万 canonical 含『军长』",
    "伊万": "47/58 owner 逐字；R148（答案 Ivan）正确且载荷",
    "格蕾丝": "46/55 owner 逐字；R206/R231/R257/R268 四题种子语境全部正确（格蕾丝=无名者 77号往事 代号）；跨篇他指 9 块",
    "阿德勒": "63/64(98%) owner 逐字；R050 正确；哑谜真名",
    "卡森": "handoff §3.4 卡森案按篇豁免；灰机独立 NPC 条目 卡森/Mr. Karson；R105（答案 Carson）载荷；7 块 owner 逐字；灰机歧义（与 Mr. Karson 独立条目并存）如实记录",
    "纸信圈儿": "65/67(97%) owner 逐字；灰机正典 zh 名（纸信圈儿/Flutterpage，canon characters），灰机反无 利伯蒂 页——本 alias 是 wiki 标准名",
    "德洛丝": "P0 焊组成员：60/69 块逐字（多为德洛丝本人语境）；R1 拆焊将建独立 德洛丝 节点并重归属 chunk；R2 不动以免 R1 前可达性受损",
    "维尔汀小姐": "94/102 owner 逐字；ts=0；敬称语料逐字",
    "APPLe某": "82/84 owner 逐字；ts=0",
    "Z女士": "72/81 owner 逐字；灰机 NPC 条目 Z女士/desc=张之之；ts=0",
    "苏芙比小姐": "68/77 owner 逐字；ts=0",
    "APPLe先生": "56/67 owner 逐字；ts=0",
    "露西女士": "55/66 owner 逐字；ts=0",
    "莫莉": "52/54 owner 逐字；ts=0",
    "第一助手": "52/53 owner 逐字；ts=0",
    "十四行诗小姐": "49/52 owner 逐字；ts=0",
    "拉普拉斯科算中心": "40/52 owner 逐字；ts=0；全称形",
    "基金会总部": "39/54 owner 逐字；ts=0",
}

# 10 bare-generic canonical nodes
CANON_VERDICTS = {
    "管理员": ("keep", "df=6 基本篇内（mainline103/113 图书馆场景），ts=0，无害"),
    "伙计": ("flag-grounding-for-R4", "df=161 vs 仅 5 块(打虎记 1 篇)；R018 以 1.0 分抢种子；R4 应标注按篇限定（如 打虎记·医馆伙计）"),
    "猎人": ("flag-grounding-for-R4", "概念节点（anecdote__1906 诗中贪婪者，1 块）；R018 以 1.0 分抢种子；灰机 zh2en『猎人』↔UFO（疑另一所指）；R4 标注寓言概念属性"),
    "小孩": ("flag-grounding-for-R4", "df=104 vs 仅 6 块(塞梅尔维斯 1 篇)；R4 按篇限定标注"),
    "教师": ("flag-grounding-for-R4", "df=21 vs 2 块(在路上 1 篇)；R273『少女教师』被其抢种子（审计检6）；R4 按篇限定标注"),
    "水手": ("flag-grounding-for-R4", "df=26 vs 3 块但跨 2 篇（复乐园 迪达号水手 / 圣火纪行 东区黎明）——跨篇同泛称焊合嫌疑；R4 标注 + 建议 R3 复核拆分"),
    "警卫": ("flag-grounding-for-R4", "df=40 vs 4 块但跨 4 篇（齿轮的意志/风吹乌哈拉/旧金山小子/故事一无所有）——4 个不同故事的警卫焊在一节点，跨篇泛称焊合最重者；R4 标注 + 建议 R3 复核拆分"),
    "店主": ("flag-grounding-for-R4", "df=21 vs 14 块跨 2 篇（乘法轴上的一天 / 第一千夜）——跨篇焊合嫌疑；R4 标注 + 建议 R3 复核拆分"),
    "卫兵": ("flag-grounding-for-R4", "df=43 vs 6 块(飞渡往日 1 篇)；篇内身份一致但词面泛称；R4 按篇限定标注"),
    "信众": ("flag-grounding-for-R4", "df=24 vs 1 块(帕米埃 1 篇)；宗教泛称；R4 按篇限定标注"),
}


def main() -> None:
    full = json.loads((OUT_DIR / "_r2_items_full.json").read_text(encoding="utf-8"))
    items = full["items"]
    graph = json.loads((REPO / "data/compendium_rag/graph.json").read_text(encoding="utf-8"))
    ents = graph["entities"]
    chunks = json.loads((REPO / "data/compendium_rag/chunks.json").read_text(encoding="utf-8"))["chunks"]
    cid = [c["chunk_id"] for c in chunks]
    texts = [c["text"] for c in chunks]
    ts = json.loads((REPO / "data/knowledge/_audit/rag_testset_300_cn.json").read_text(encoding="utf-8"))["cases"]
    triage = json.loads((REPO / "data/compendium_rag/reports/rank_triage_300cn.json").read_text(encoding="utf-8"))
    poolout = [r for r in triage["per_miss"] if r.get("class") == "corpus_not_pooled"]
    poolout_qids = [r["qid"] for r in poolout]
    tsmap = {t["id"]: t for t in ts}

    ent_by_name = {e["name"]: e for e in ents}

    # ── build post-repair alias_index ──
    removal_set = set(REMOVE)
    idx_pre: dict[str, str] = {}
    for e in ents:
        idx_pre[e["name"]] = e["eid"]
    for e in ents:
        for a in e["aliases"]:
            idx_pre.setdefault(a, e["eid"])

    idx_post: dict[str, str] = {}
    modified: dict[str, list[str]] = {}
    for e in ents:
        idx_post[e["name"]] = e["eid"]
    for e in ents:
        if e["name"] in modified:
            continue
        al = [a for a in e["aliases"] if a not in removal_set]
        modified[e["name"]] = al
    for name, al in modified.items():
        for a in al:
            idx_post.setdefault(a, name)

    # ── checks ──
    removed_from_index = sorted(set(idx_pre) - set(idx_post))
    dangling = [k for k, v in idx_post.items() if v not in ent_by_name]

    # retention: each removal owner keeps >=1 verbatim alias or canonical
    owner_chunks = {e["name"]: set(e["chunk_ids"]) for e in ents}
    retention_report = {}
    for alias in removal_set:
        owners = items[alias]["owners"]
        for ow in owners:
            claimed = owner_chunks[ow]
            blob = "\n".join(t for c, t in zip(cid, texts) if c in claimed)
            e = ent_by_name[ow]
            post_al = modified[ow]
            verbatim = [a for a in post_al if a in blob]
            retention_report.setdefault(alias, {})[ow] = {
                "canonical_grounded": e["name"] in blob,
                "remaining_verbatim_aliases": verbatim[:6],
                "n_verbatim_aliases": len(verbatim),
            }

    # link() simulation over 300 queries, pre vs post
    def simulate(idx: dict) -> dict[str, list[tuple[str, float]]]:
        out = {}
        cands = sorted(idx.keys(), key=len, reverse=True)
        for t in ts:
            ql = t["q"].lower()
            seeds: dict[str, float] = {}
            for name in cands:
                if not _name_matches(name, ql):
                    continue
                eid = idx[name]
                sc = 1.0 if name == ent_by_name[eid]["name"] else 0.9
                if eid not in seeds or sc > seeds[eid]:
                    seeds[eid] = sc
            out[t["id"]] = sorted(seeds.items(), key=lambda kv: (-kv[1], kv[0]))
        return out

    sim_pre = simulate(idx_pre)
    sim_post = simulate(idx_post)
    changed = []
    for qid in sim_pre:
        if sim_pre[qid] != sim_post[qid]:
            lost = sorted(set(e for e, _ in sim_pre[qid]) - set(e for e, _ in sim_post[qid]))
            gained = sorted(set(e for e, _ in sim_post[qid]) - set(e for e, _ in sim_pre[qid]))
            changed.append({"qid": qid, "lost": lost, "gained": gained,
                            "was_poolout": qid in poolout_qids})
    changed_poolout = [c for c in changed if c["was_poolout"]]
    # pool-out misses whose query matches ANY removed string
    poolout_involving_removed = []
    for r in poolout:
        ql = tsmap[r["qid"]]["q"].lower()
        hit_al = [a for a in removal_set if _name_matches(a, ql)]
        if hit_al:
            poolout_involving_removed.append({"qid": r["qid"], "removed_aliases_matched": hit_al})

    # dead-alias count among our 63 items, pre vs post
    def count_dead(idx: dict) -> int:
        n = 0
        for a, v in idx.items():
            if a == ent_by_name[v]["name"]:
                continue
            claimed = owner_chunks[v]
            if not any(a in t for c, t in zip(cid, texts) if c in claimed):
                n += 1
        return n

    dead_pre = count_dead(idx_pre)
    dead_post = count_dead(idx_post)

    # R018 specific
    r018_pre = sim_pre["R018"]
    r018_post = sim_post["R018"]

    res = {
        "n_entities": len(ents),
        "n_alias_index_pre": len(idx_pre),
        "n_alias_index_post": len(idx_post),
        "removed_from_index": removed_from_index,
        "dangling": dangling,
        "n_removed_alias_declarations": len(REMOVE),
        "n_keep": len(KEEP),
        "retention": retention_report,
        "retention_exceptions": [
            {"alias": a, "detail": v} for a, m in retention_report.items()
            for ow, v in m.items()
            if v["n_verbatim_aliases"] == 0
        ],
        "changed_queries": changed,
        "n_changed_queries": len(changed),
        "changed_poolout": changed_poolout,
        "poolout_involving_removed": poolout_involving_removed,
        "dead_alias_count_itemscope_pre": dead_pre,
        "dead_alias_count_itemscope_post": dead_post,
        "R018_pre": r018_pre,
        "R018_post": r018_post,
    }
    (OUT_DIR / "_r2_step3_selfval.json").write_text(json.dumps(res, ensure_ascii=False, indent=1),
                                                    encoding="utf-8")
    print(json.dumps({k: v for k, v in res.items() if k not in ("retention", "changed_queries")},
                     ensure_ascii=False, indent=1)[:3000])
    print("\nchanged queries detail:")
    for c in changed:
        print(f"  {c['qid']}{' (POOL-OUT)' if c['was_poolout'] else ''} lost={c['lost']} gained={c['gained']}")
    print("\nretention exceptions:", json.dumps(res["retention_exceptions"], ensure_ascii=False))


if __name__ == "__main__":
    main()
