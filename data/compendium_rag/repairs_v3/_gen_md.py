# -*- coding: utf-8 -*-
"""Generate proposal_v3.md from proposal.json + _selfval.json."""
import io, sys, json, os

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
OUTDIR = os.path.join(ROOT, "data", "compendium_rag", "repairs_v3")

P = json.load(open(os.path.join(OUTDIR, "proposal.json"), encoding="utf-8"))
SV = json.load(open(os.path.join(OUTDIR, "_selfval.json"), encoding="utf-8"))
E = {e["id"]: e for e in P["entries"]}

ITEMS = {
    1: ("缺桥补链（R090/R094/R127/R231）", "质检报告检6 归因 8 道图谱可修中的 4 道；triage class=corpus_not_pooled & entity_bridge=true"),
    2: ("R170 玩具盒新抽取（零网关）", "QC：玩具盒 不在图（语料 DF=1，唯一提及块未被抽成实体）"),
    3: ("乌尔里希 合并", "QC 检4.3 P1：一人两节点（53 块 ∪ 72 块）"),
    4: ("船名分裂复核（R005/R012）", "QC：APPLe号 与 APPLe号摇滚巨轮二世 裂成两节点 → 本轮按冲突序改判"),
    5: ("保罗→QUALIFY（仲裁#1，执行推迟至 R3）", "repairs_arbitration_20260926.md"),
    6: ("旅行队的别斯米尔 合并（R1 deferred）", "探险家别斯米尔(70块) vs 旅行队的别斯米尔(1块)"),
    7: ("警卫/店主/水手 跨篇焊嫌疑复核（R2 flagged）", "泛称 canonical 节点跨篇焊：拆分需 R1 卡卡尼亚式语料锚点"),
}

L = []
w = L.append
w("# 图谱修复提案 R3（补桥补链 + 合并 + 新抽取）— 2026-09-26")
w("")
w("> **作者**：R3-repairer ｜ **状态**：提案（未落图；graph.json 零改动） ｜ **网络**：none（灰机 WAF 403 禁网；身份裁决全部来自本地缓存 `data/lore/_huiji_cache/` 474 文件 + `data/lore/wu_ming_zhe/` 词表 + 语料逐字 grep）")
w("> **协议**：`docs/图谱修复作战书_预注册_20260926.md` §0 冲突序（语料明文反证 > 灰机 > 图谱现状 > 审计推断）；schema = v1（同 `repairs_v1/proposal.json`，适配 `scripts/_graph_apply_repairs.py`）")
w("> **基线图**：graph.json 现状 7034 实体 / 29959 边（R1+R2 已应用）；全部结论已对照该现状重新核验")
w("")
w("## 0. 自验结果（模拟 Applier 全流程）")
w("")
w("- 预检：18 条全部通过（eid 冲突/属主存在/alias 已存在/悬空 chunk/逐字性全覆盖断言）。")
w("- 模拟应用后检：**全绿** —— 无 eid 重复、无重名规范节点、全部 eid==name、无悬空 chunk（实体+边）、无悬空边端点；触碰实体 `mentions == len(set(chunk_ids))`；全部新增 alias 逐字于属主声称块（per-owner，红线3）。")
w(f"- 图规模：{SV['graph_delta']['entities']} 实体；边 {SV['graph_delta']['edges']} → Applier 去重后 29957（合并重接后 `哑谜-质问→乌尔里希`、`乌尔里希-反驳→哑谜` 各有 2 条同三元组边——同一事实对双节点各抽一次所致，按图规范零重复合并 chunk_ids）。")
w("- **真实 Applier 干跑复核**：`scripts/_graph_apply_repairs.py --proposal repairs_v3/proposal.json` → 条目 18 | 预检错误 0 | 警告 2（即两条 inferred alias）| 后检错误 0 | **[DRY-RUN] 全绿**（未写盘）。")
w("- **link() 种子模拟**（复用 retriever._name_matches/alias_index 规范，exact=1.0/alias=0.9/长名优先）：")
w("")
w("| qid | before | after（默认，inferred 未落） | after（若用户放行 inferred） |")
w("|---|---|---|---|")
for qid in ["R090", "R094", "R127", "R170", "R231", "R005", "R012", "R018"]:
    r = SV["link_simulation"][qid]
    b = ", ".join(f"{n}:{s}" for n, s, _ in r["before"]) or "0 种子"
    a = ", ".join(f"{n}:{s}" for n, s, _ in r["after"]) or "0 种子"
    h = ", ".join(f"{n}:{s}" for n, s, _ in r.get("after_if_inferred_applied", r["after"])) or "0 种子"
    mark = " **←种子修复**" if a != b and r["after"] else ("（inferred 生效方有变化）" if h != a else "")
    w(f"| {qid} | {b} | {a}{mark} | {h} |")
w("")
w("> R170/R005/R012 的种子不变属预期：R170 靠抽取把 gold 块纳入实体声称池（重排窗口复验在重校准闸门）；R005/R012 按 §4 改判不合并。R127 的查询形「福格先生」与语料形「福葛先生」为措辞差（格≠葛），图谱侧修复使其在正确人名形下可达；QC 所记 R127 旧种子 `环境监测装置0.9` 系 R2 泛称清洗前状态（现 环境监测装置 0 alias）。")
w("")
w("## Applier 执行注意事项")
w("")
w("1. **R3-E02（Noire@菲林士多）与 R3-E07（契约魅魔@金伯利女郎）为 `inferred:true`** —— 语料 DF=0，不满足红线3；按作战书 §0.2 仅入提案备用户裁决。**Applier 无『词表 alias 豁免机制』时必须跳过这两条**（本提案自验模拟即按 skip 处理）。")
w("2. 条目已按依赖排序：R3-E04（合并）先于 R3-E05（补全名 alias，合并后逐字于属主块 5+2=7 块）。")
w("3. R3-E12 仅执行仲裁 QUALIFY 的 remove 半步；add 半步（保罗·霍伊默尔@卡戎）R2 已落图并经逐字验证（mainline__111:14.0.2，DF=1）。")
w("")
w("---")
w("")

for item in range(1, 8):
    title, why = ITEMS[item]
    w(f"## Item {item}：{title}")
    w("")
    w(f"> 依据：{why}")
    w("")
    for e in P["entries"]:
        if e.get("item") != item:
            continue
        inferred = " **〔inferred — 不满足红线3，需用户裁决，Applier 默认跳过〕**" if e.get("inferred") else ""
        w(f"### {e['id']} `{e['type']}` → target: {e['target']}{inferred}")
        w("")
        if e["type"] == "add_entity":
            ent = e["entity"]
            w(f"- 新实体：eid==name=**{ent['eid']}**，type={ent['type']}，mentions={ent['mentions']}，chunk_ids={len(ent['chunk_ids'])} 块，aliases={ent['aliases']}")
            w(f"- desc：{ent['desc']}")
            w(f"- chunk_ids 明细：")
            for cid in ent["chunk_ids"]:
                w(f"  - `{cid}`")
        elif e["type"] == "merge_entities":
            w(f"- moved_chunks：{len(e['moved_chunks'])} 块（边由 Applier merge_entities 自动重接）")
        elif e["type"] == "reassign_chunk":
            w(f"- add_chunk_ids：{e.get('add_chunk_ids') or '[]'}")
            w(f"- removed_weld_chunks：{e.get('removed_weld_chunks') or '[]'}")
        elif e["type"] == "keep_with_note":
            w(f"- 裁决：{e['note']}")
        w("")
        w("**证据**：")
        w("")
        for ev in e["evidence"]:
            w(f"- `{ev['src']}`")
            w(f"  > {ev['quote']}")
        w("")
        w(f"**Before**：{e['before']}")
        w("")
        w(f"**After**：{e['after']}")
        w("")
    w("---")
    w("")

w("## 与质检报告结论的差异（冲突序裁决记录）")
w("")
w("1. **R005/R012「船名分裂→合并」被语料明文反证（R3-E11）**：APPLe号（一世，mainline__000 泰晤士河被炮击沉没）与 APPLe号摇滚巨轮二世（苏芙比买的新船，mainline__105 沉没）是两代不同的船；anecdote__1920:5.0.1 明文「两代APPLe号！」、anecdote__1917:7.0.0 出现「APPLe号三世」。合并将构成 R1 式错焊。R005/R012 的 miss 主因应改判措辞差异（摇滚苹果/Rockin/扎内塔 语料 DF=0）。")
w("2. **R127 归因修正（R3-E03）**：QC 将 gold 指向 `福格尔`（mainline__113 第一防线学校教员，2 块）；语料实测查询「福格先生发明的大型装置」对应 **福葛先生**（伦敦雾行者，40 块，图中无节点）及其发明 **雾气净化器/「伦敦煤烟污染勘察与清除大使」**（ref「净化机」语料 DF=0，语料实形 净化器）。福格尔≠福葛先生（性别/篇章/身份全不同），已按语料另行补 alias（R3-E06）。")
w("3. **R090 的「缺桥梁实体/alias 中央塔」以既有节点落地（R3-E01）**：QC 称「中央塔 无节点/alias」——精确形属实，但节点 **中央瞭望塔**（24 块，声称 R090 gold 块 109:11.0.1）已存在且其 113 篇声称块逐字含「中央塔」，故补 alias 即达 per-owner 逐字，无需新节点。另观察：该节点横跨 103/109/113 三篇（既有跨篇焊嫌疑，超出本轮范围，记录备 R4）。")
w("4. **R170 的语料语义与测试集前设有出入（R3-E08）**：本中文语料「玩具盒」唯一出现是 1987宇宙组曲 的比喻（「宇宙……如同……玩具盒子」），「拉普拉斯的重要装置」读法来自官方英文配音语料（toy box 39 次，plot_glossary 注）。已按 QC/作战书指令零网关抽取，desc 只写语料实义，供重校准闸门实证。")
w("5. **R231 无逐字可补（R3-E07 inferred）**：「契约魅魔」DF=0（QC 同判）；裸「魅魔」不加（泛称节点 魅魔 持 canonical，遵循 R2 泛称清理精神）。")
w("6. **乌尔里希合并方向（R3-E09）**：QC 建议互挂/并回；按 R1 先例（传记作家兀尔德→兀尔德）与规范名逐字原则，取 **暴雨小组组长乌尔里希→乌尔里希**（后者为语料裸名，前者 DF=0 归一形），而非反向。")
w("7. **警卫/水手 保守保留（R3-E17/E18）**：跨篇属实，但全部为无名群众角色，无具名锚点，拆分后 alias 必被 setdefault 遮蔽，收益不足——留档 R4。店主 因其一实例语料具名（米拉）而拆（R3-E15/E16）。")
w("")
w("## 证据源清单")
w("")
for s in P["meta"]["sources"]:
    w(f"- {s['file']} —— {s['role']}")
w("")
w("> 全部 huiji 证据取自 2026-09-13 本地采集缓存（禁网）；本轮新增 huiji 拉取为 0。语料引用均为 chunks.json 逐字子串（生成器断言保证）。")
w("")

selfval_note = None
with open(os.path.join(OUTDIR, "_selfval.json"), encoding="utf-8") as f:
    sv_raw = json.load(f)
sv_raw["real_applier_dryrun"] = {
    "command": "scripts/_graph_apply_repairs.py --proposal data/compendium_rag/repairs_v3/proposal.json",
    "result": "条目 18 | 预检错误 0 | 警告 2（inferred alias: Noire@菲林士多, 契约魅魔@金伯利女郎）| 后检错误 0 | [DRY-RUN] 全绿",
    "edges_after_dedup": "29959 -> 29957（哑谜-质问→乌尔里希 ×2、乌尔里希-反驳→哑谜 ×2 同三元组合并，chunk_ids 并入）",
}
with open(os.path.join(OUTDIR, "_selfval.json"), "w", encoding="utf-8") as f:
    json.dump(sv_raw, f, ensure_ascii=False, indent=1)

with open(os.path.join(OUTDIR, "proposal_v3.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(L))
print("written proposal_v3.md", len("\n".join(L)))
