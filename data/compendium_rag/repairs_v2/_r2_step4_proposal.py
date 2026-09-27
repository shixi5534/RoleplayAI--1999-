# -*- coding: utf-8 -*-
"""R2-repairer step 4: assemble proposal.json from verdict tables + evidence.

Reads _r2_items_full.json / _r2_step3_selfval.json; writes proposal.json.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
OUT_DIR = REPO / "data/compendium_rag/repairs_v2"

sys.path.insert(0, str(OUT_DIR))
from _r2_step3_selfval import REMOVE, KEEP, CANON_VERDICTS  # noqa: E402


def main() -> None:
    full = json.loads((OUT_DIR / "_r2_items_full.json").read_text(encoding="utf-8"))
    items = full["items"]
    canon_nodes = full["canon_nodes"]
    sv = json.loads((OUT_DIR / "_r2_step3_selfval.json").read_text(encoding="utf-8"))
    graph = json.loads((REPO / "data/compendium_rag/graph.json").read_text(encoding="utf-8"))
    ent_by_name = {e["name"]: e for e in graph["entities"]}

    tsmap = {}
    ts = json.loads((REPO / "data/knowledge/_audit/rag_testset_300_cn.json").read_text(encoding="utf-8"))["cases"]
    for t in ts:
        tsmap[t["id"]] = t["q"]

    changed_by_qid = {c["qid"]: c for c in sv["changed_queries"]}

    def base_item(alias: str) -> dict:
        v = items[alias]
        owners = v["owners"]
        o = ent_by_name[owners[0]] if owners else None
        return v, owners, o

    def evidence_of(alias: str, n: int = 2) -> list[dict]:
        v = items[alias]
        ev = []
        for s in v["unrelated_samples"][:n]:
            ev.append({"chunk_id": s["chunk_id"], "snip": s["snip"][:160]})
        return ev

    entries = []

    # ── remove_alias entries ──
    for alias in REMOVE:
        v, owners, o = base_item(alias)
        ret = sv["retention"].get(alias, {})
        changed = [c for c in sv["changed_queries"] if alias in
                   [a for qid2 in () for a in ()]]  # placeholder no-op
        # which changed queries lost this owner?
        lost_qids = [c["qid"] for c in sv["changed_queries"]
                     if owners and o is not None and o["eid"] in c["lost"]]
        entry = {
            "type": "remove_alias",
            "target": {"alias": alias, "owner_eid": owners[0] if owners else None,
                       "owner_type": v.get("owner_type"),
                       "extra_owners": owners[1:]},
            "df": {"total": v["df"], "in_owner_claims": v["df_chunks_in_owner_claims"],
                   "unrelated": v["df_unrelated"]},
            "wiki_verdict": None,
            "rationale": REMOVE[alias],
            "evidence_chunks": evidence_of(alias),
            "testset": {"matched_qids": [q for q, _ in v["testset_hits"]],
                         "seed_changes": [{"qid": q, "before": tsmap[q], "lost": changed_by_qid[q]["lost"]}
                                          for q in lost_qids]},
            "owner_after_state": {
                ow: {"canonical_grounded": m["canonical_grounded"],
                     "n_verbatim_aliases_left": m["n_verbatim_aliases"],
                     "verbatim_aliases_left": m["remaining_verbatim_aliases"]}
                for ow, m in ret.items()},
            "before": f"alias_index['{alias}'] = '{owners[0] if owners else '?'}'（link() alias 命中 0.9 分，长名优先）",
            "after": f"alias_index 不再含 '{alias}' 键（{owners[0] if owners else ''} 的 aliases 列表移除该条）",
        }
        entries.append(entry)

    # ── keep_with_note entries ──
    for alias in KEEP:
        v, owners, o = base_item(alias)
        entry = {
            "type": "keep_with_note",
            "target": {"alias": alias, "owner_eid": owners[0] if owners else None,
                       "owner_type": v.get("owner_type")},
            "df": {"total": v["df"], "in_owner_claims": v["df_chunks_in_owner_claims"],
                   "unrelated": v["df_unrelated"]},
            "wiki_verdict": None,
            "rationale": KEEP[alias],
            "evidence_chunks": evidence_of(alias, 1),
            "testset": {"matched_qids": [q for q, _ in v["testset_hits"]]},
            "before": f"alias_index['{alias}'] = '{owners[0] if owners else '?'}'",
            "after": "不变（保留）",
        }
        entries.append(entry)

    # ── canonical bare-generic nodes ──
    for name, (verdict, why) in CANON_VERDICTS.items():
        c = canon_nodes[name]
        entry = {
            "type": "flag_grounding_r4" if verdict.startswith("flag-grounding") else "keep_node",
            "target": {"eid": name, "node_type": c.get("type"), "desc": c.get("desc")},
            "df": {"total": c["df"]},
            "nchunks": c.get("nchunks"), "docs": c.get("docs"),
            "wiki_verdict": ("灰机 lexicon 命中：" + json.dumps(c.get("wiki_zh2en"), ensure_ascii=False))
                            if c.get("wiki_zh2en") else
                            ("灰机 canon 角色页命中" if c.get("wiki_zh_name") else "灰机无同名页/条目（离线 lexicon + 474 页缓存核查）"),
            "rationale": why,
            "evidence_chunks": [{"snip": s[:160]} for s in c.get("df_sample_snips", [])[:2]],
            "name_contains_entities": c.get("name_contains_entities", [])[:6],
            "before": f"节点 '{name}' 为规范名（alias_index 直配 1.0 分）",
            "after": ("R4：标注 grounding_scope=per_story_generic 元数据（不改名不删节点）"
                      if verdict.startswith("flag-grounding") else "不变"),
            "r4_proposed_annotation": {
                "grounding_scope": "per_story_generic",
                "story_scope_docs": c.get("docs"),
                "suggested_qualified_display": None,
            } if verdict.startswith("flag-grounding") else None,
        }
        entries.append(entry)

    proposal = {
        "meta": {
            "author": "R2-repairer",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "batch": "R2 泛称别名清理（docs/图谱修复作战书_预注册_20260926.md §1-R2、§2 协议）",
            "findings_ref": "docs/图谱与原文质检报告_20260926.md 检3（P1 泛称污染）+ 检6（R018 实测错种子）",
            "scope": "58 个 DF≥50 的声明 alias（独立重算确认）＋ R018 案 3 条关联 alias（老伙计/老朋友/卡森，前两者为上一审计增量证据）＋ 10 个裸泛称规范节点",
            "blob_rule": "DF(s) = #{chunk ∈ chunks.json 3695 块 : s 为 chunk['text'] 原文子串}（与审计检3 同口径）",
            "alias_index_rule": "重建口径与 GraphStore._rebuild 一致：canonical 名直配，alias 依实体序 setdefault（首主抢注）",
            "standard_order": "语料明文反证 > 灰机 > 图谱现状 > 审计推断（作战书 §0.3）",
            "no_write_declaration": "graph.json / corpus.json / chunks.json 及一切既有文件未改动；本提案为唯一输出（proposal.json + proposal_v2.md + repairs_v2/ 下 _r2_* 工作件）",
            "no_ollama": True,
            "huiji_fetches": {
                "predecessor_reused": [
                    {"step": "bootstrap", "url": "https://res1999.huijiwiki.com/wiki/首页",
                     "t": "2026-09-26 21:03:34", "note": "repo 标准 huiji_fetch.py Cloudflare 放行"},
                    {"step": "revcontent", "n_titles": 22, "bytes": 12828, "t": "2026-09-26 21:03:34",
                     "cache": "_huiji_cache/f7609ed91d8112d62177.json"},
                    {"step": "revcontent", "n_titles": 21, "t": "2026-09-26 21:03",
                     "cache": "_huiji_cache/6785bf78578df88a393f.json"},
                ],
                "this_session": [
                    {"attempt": "urllib api.php titles= 批查 47 题", "result": "HTTP 403 Cloudflare『请稍候…』",
                     "t": time.strftime("%Y-%m-%d %H:%M:%S")},
                    {"attempt": "curl(浏览器UA) api.php 同参", "result": "HTTP 403 Cloudflare JS challenge",
                     "t": time.strftime("%Y-%m-%d %H:%M:%S")},
                    {"decision": "按任务约束禁用浏览器路径（huiji_fetch.py 真实 Chrome bootstrap = 前代死因的验证码坑）；"
                                 "全部 wiki 裁决改由离线源闭合：huiji_lexicon.json(885 zh 名) + huiji_canon.json(141 角色/184 NPC) "
                                 "+ data/lore/_huiji_cache/ 474 文件 + 前代 _scratch_wiki_raw.json(43 owner 页 wikitext)",
                     "result": "所有裁决关键 wiki 事实离线可得，无未决网关"},
                ],
            },
            "reused_from_predecessor": {
                "_scratch_df.json": "1026 键全量 DF 表 —— 本次独立重算 8049 键，与该表 1026/1026 全一致（0 偏差），全部采信",
                "_scratch_items.json": "63 item（58 清单全覆盖 + 伙计/小孩/卡森/老伙计/老朋友 增量）：owner 归属/link_winner/owner_grounded_keys/owner_docs 采信；"
                                       "unrelated_samples 51/63 直接采信，其余由本次补齐；testset_hits 以本次 _name_matches 全量重算覆盖",
                "_scratch_wiki_raw.json": "43 owner 页 revcontent 存在性 + wikitext（fetch_log 3 步）——用于 owner 页存在性与页内引文核查（卡戎页无『保罗』、邓肯先生页无『老伙计/老朋友/卡森』、维尔汀页含『司辰/老爷』引文）",
                "_huiji_cache/": "2 个 api.php 原始响应（revcontent 批查）",
                "not_reused": "_scratch_canon（10 节点）中 df/snips 采信，但 df 与 name_contains 由本次独立重算复核一致",
            },
            "self_validation": {
                "post_alias_index_size": sv["n_alias_index_post"],
                "removed_keys": len(sv["removed_from_index"]),
                "dangling_refs": sv["dangling"],
                "seed_changes_on_testset300": sv["n_changed_queries"],
                "seed_change_rule": "11 题种子集变化全部为『只失去错误种子』：R018 失邓肯先生(0.9)、R062/R069/R076 失奇美拉（答案巨怪）、R087/R259 失泰内布朗热家、R127/R170/R180/R240 失环境监测装置、R228 失勿忘我（答案 Melania，正确种子 拉米雷斯 1.0 保留）；0 题失去正确种子",
                "R018_seeds": {"pre": sv["R018_pre"], "post": sv["R018_post"]},
                "poolout_14_involving_removed_strings": sv["poolout_involving_removed"],
                "poolout_note": "R297 命中『学校』子串但为第一防线学校全称内部子串，canonical 直配不变（种子模拟确认 R297 不在变化清单）；R127/R170 本就是 pool-out miss，摘除只移除错误种子，hit@6 无从恶化",
                "owner_alias_retention": "36 条摘除的 owner 全部保留 canonical 名；16/18 owner 另有 ≥1 逐字 alias 或 grounded canonical；2 个例外（信仰、卡卡尼亚之兄）canonical 本就不落地（grounding 缺陷先在，已在条目内标注 R4 接手）",
                "dead_alias_count_whole_index": {"pre": sv["dead_alias_count_itemscope_pre"],
                                                 "post": sv["dead_alias_count_itemscope_post"]},
                "no_new_dead_aliases": "本批只删不增 alias；唯一新增『死键化』为上述 2 个先在 grounding 缺陷节点（非新增 alias）",
            },
            "new_findings_for_ledger": [
                "R236『基金会的首席助手』现役可答题依赖 alias 助手 种子十四行诗——审计检3『至少摘除』清单中的 助手 应改为保留（§0 补录）",
                "R228『拉米雷斯保安公司的老板』答案为 Melania 而非 勿忘我——alias 老板 在该题为误种子且非载荷（拉米雷斯 1.0 正确种子在）",
                "R062/R069/R076 三题答案为巨怪(troll)——alias 怪物→奇美拉 为 3 次误种子",
                "灰机 NPC 总表（data/lore/_huiji_cache/49910dc30331af4cb845.json）：别斯米尔/Bessmert/desc=兀尔德 独立条目（与语料 mainline__110:19.0.1 自述否认互证）；卡森/Mr. Karson/id=5013 独立条目",
                "灰机无 利伯蒂 页而 纸信圈儿(Flutterpage) 为 canon characters 正典 zh 名——节点 利伯蒂 的命名标准化归 R3 复核",
                "10 个裸泛称节点中 警卫(4篇)/店主(2篇)/水手(2篇) 存在跨篇同泛称焊合嫌疑，超出 R2 职权，建议 R3 复核拆分（本提案仅 flag-grounding-for-R4）",
                "测试集 ref 对 R018 答案写作『Shamane（沙曼）』而灰机 zh 正典为 鬃毛沙砾——R3 补 alias 时需以灰机形为准",
            ],
        },
        "entries": entries,
    }

    (OUT_DIR / "proposal.json").write_text(json.dumps(proposal, ensure_ascii=False, indent=1),
                                           encoding="utf-8")
    print("wrote proposal.json:", len(entries), "entries")
    from collections import Counter
    print(Counter(e["type"] for e in entries))


if __name__ == "__main__":
    main()
