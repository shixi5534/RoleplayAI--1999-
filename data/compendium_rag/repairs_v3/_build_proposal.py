# -*- coding: utf-8 -*-
"""R3 proposal builder + self-validation.
Follows 作战书 §0 (语料明文反证 > 灰机 > 图谱现状 > 审计推断) and the v1 schema
(target=owner string; entity=dict; lists as lists) consumed by scripts/_graph_apply_repairs.py.
READ-ONLY on graph.json/chunks.json — writes ONLY repairs_v3/proposal.json + _selfval.json.
"""
import io, sys, json, os, copy, re
from collections import Counter

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

GRAPH = os.path.join(ROOT, "data", "compendium_rag", "graph.json")
CHUNKS = os.path.join(ROOT, "data", "compendium_rag", "chunks.json")
OUTDIR = os.path.join(ROOT, "data", "compendium_rag", "repairs_v3")

G = json.load(open(GRAPH, encoding="utf-8"))
CHL = json.load(open(CHUNKS, encoding="utf-8"))["chunks"]
chunks = {c["chunk_id"]: c["text"] for c in CHL}
gents = G["entities"] if isinstance(G.get("entities"), dict) else {e["eid"]: e for e in G["entities"]}
edges = G.get("edges", [])

def df(term):
    return [cid for cid, t in chunks.items() if term in t]

def cq(cid, term, before=30, after=55):
    """guaranteed-verbatim quote window around term in chunk."""
    t = chunks[cid]
    i = t.find(term)
    assert i >= 0, f"term {term!r} not in {cid}"
    return t[max(0, i - before):i + len(term) + after].replace("\n", " / ").strip()

def hq(path, term, before=25, after=60, nth=0):
    """guaranteed-verbatim quote window around term in a huiji cache file (raw)."""
    raw = open(os.path.join(ROOT, path), encoding="utf-8").read()
    idxs = [m.start() for m in re.finditer(re.escape(term), raw)]
    assert idxs, f"term {term!r} not in {path}"
    i = idxs[nth]
    return raw[max(0, i - before):i + len(term) + after].replace("\n", " ").replace("\\n", " ").strip()

def ev_corpus(cid, term, before=30, after=55):
    return {"src": f"corpus {cid}", "quote": cq(cid, term, before, after)}

def ev_huiji(path, term, label, before=25, after=60, nth=0):
    return {"src": f"offline-huiji {path} [{label}]（本地缓存，2026-09-13 采集；禁网）",
            "quote": hq(path, term, before, after, nth)}

def ev_doc(doc, quote):
    return {"src": doc, "quote": quote}

ERRS, WARN = [], []
def chk(cond, msg):
    if not cond:
        ERRS.append(msg)

# ============================================================ preconditions
NAMES = {e["name"] for e in gents.values()}
ALIAS_OWNER = {}
for e in gents.values():
    for a in (e.get("aliases") or []):
        ALIAS_OWNER.setdefault(a, []).append(e["eid"])

def require_ent(n):
    chk(n in gents, f"属主缺失: {n}")
    return gents.get(n)

# ---------- E01 中央塔@中央瞭望塔 (R090) ----------
zlw = require_ent("中央瞭望塔")
zlwc = zlw["chunk_ids"]
z_hits = [c for c in zlwc if "中央塔" in chunks[c]]
chk(len(z_hits) == 2, f"中央塔 containment 预期2，得 {len(z_hits)}")
chk("mainline__109_疯癫与文明:11.0.1" in zlwc, "中央瞭望塔 未声称 R090 gold 块 109:11.0.1")
chk("中央塔" not in ALIAS_OWNER and "中央塔" not in NAMES, "中央塔 已被占用")

# ---------- E02 Noire@菲林士多 (inferred) ----------
fl = require_ent("菲林士多")
chk(len(df("Noire")) == 0, "DF[Noire] 应为 0（inferred 前提）")
chk("Noire" not in ALIAS_OWNER and "Noire" not in NAMES, "Noire 已被占用")

# ---------- E03 福葛先生 ----------
fg_chunks = df("福葛")
chk(len(fg_chunks) == 40, f"DF[福葛] 预期40，得 {len(fg_chunks)}")
chk("福葛先生" not in NAMES and "福葛先生" not in ALIAS_OWNER, "福葛先生 已被占用")
chk(all("福葛" in chunks[c] for c in fg_chunks), "福葛 chunk 集应逐字含 福葛")
oliver = [c for c in fg_chunks if "奥利弗·福葛" in chunks[c]]
fhj = [c for c in fg_chunks if "福葛伙计" in chunks[c]]
fam = [c for c in fg_chunks if "福葛先生" not in chunks[c] and "福葛伙计" not in chunks[c] and "奥利弗·福葛" not in chunks[c]]
chk(oliver and fhj, "别名 奥利弗·福葛/福葛伙计 需逐字在属主块")
chk(len(fam) == 3, f"家族/旁白指认块应恰3（1901:2.0.1/3.0.2、1905:0.0.3），得 {fam}")
chk(len(df("亚瑟·福葛")) == 0, "亚瑟·福葛 应仅见 huiji（不设 alias）")

# ---------- E04/E05 大使 → 雾气净化器 ----------
wq = require_ent("雾气净化器")
ds = require_ent("伦敦煤烟污染勘察与清除大使")
ds_full_in_wq = [c for c in wq["chunk_ids"] if "伦敦煤烟污染勘察与清除大使" in chunks[c]]
ds_full_in_ds = [c for c in ds["chunk_ids"] if "伦敦煤烟污染勘察与清除大使" in chunks[c]]
chk(len(ds_full_in_wq) == 5, f"大使 全名逐字于 雾气净化器 自身声称块应5，得 {ds_full_in_wq}")
chk(len(ds_full_in_ds) >= 1, "大使 节点至少1块含全名")
chk(len(set(ds["chunk_ids"]) & set(wq["chunk_ids"])) == 0, "两节点块集应不重叠")

# ---------- E06 福格尔女士@福格尔 ----------
fge = require_ent("福格尔")
fgl = [c for c in fge["chunk_ids"] if "福格尔女士" in chunks[c]]
chk(len(fgl) == 2, f"福格尔女士 containment 预期2，得 {len(fgl)}")

# ---------- E07 契约魅魔@金伯利女郎 (inferred) ----------
kbl = require_ent("金伯利女郎")
chk(len(df("契约魅魔")) == 0, "DF[契约魅魔] 应为 0（inferred 前提）")
chk("契约魅魔" not in ALIAS_OWNER, "契约魅魔 已被占用")
chk("魅魔" in NAMES, "泛称节点 魅魔 存在（不设裸 魅魔 alias 的依据）")

# ---------- E08 玩具盒 ----------
tb_chunks = df("玩具盒")
chk(tb_chunks == ["activity__27101_1987宇宙组曲:17.1.0"], f"玩具盒 DF 预期恰1，得 {tb_chunks}")
chk("玩具盒子" in chunks[tb_chunks[0]], "玩具盒子 逐字")
chk("玩具盒" not in NAMES, "玩具盒 不应在图（QC 前提）")

# ---------- E09 乌尔里希 merge ----------
ul = require_ent("乌尔里希")
ul2 = require_ent("暴雨小组组长乌尔里希")
ul2_bare = [c for c in ul2["chunk_ids"] if "乌尔里希" in chunks[c]]
chk(len(ul2_bare) == 71 and len(ul2["chunk_ids"]) == 72, "暴雨乌尔里希 71/72 块含裸名")
chk(not (set(ul["chunk_ids"]) & set(ul2["chunk_ids"])), "两节点块集重叠应 0")
chk(len(df("暴雨小组组长乌尔里希")) == 0, "暴雨小组组长乌尔里希 应为 v3 归一形（DF=0）")
chk(any("玻璃脑袋" in chunks[c] for c in ul2["chunk_ids"]), "玻璃脑袋 佐证缺失")
chk("玻璃缸脑袋" in (ul.get("aliases") or []), "乌尔里希 应带 玻璃缸脑袋 alias")
ul_edges = [e for e in edges if e["src"] in ("乌尔里希", "暴雨小组组长乌尔里希") or e["dst"] in ("乌尔里希", "暴雨小组组长乌尔里希")]

# ---------- E10 二世 chunk ----------
ec2 = require_ent("APPLe号摇滚巨轮二世")
chk("mainline__105_洞穴的囚徒:0.0.1" not in ec2["chunk_ids"], "0.0.1 不应在二世块集")
chk("APPLe号" in chunks["mainline__105_洞穴的囚徒:0.0.1"] and "摇滚巨轮" in chunks["mainline__105_洞穴的囚徒:0.0.1"]
    and "二世" in chunks["mainline__105_洞穴的囚徒:0.0.1"], "0.0.1 需含船名全形")
chk("mainline__105_洞穴的囚徒:0.0.0" in ec2["chunk_ids"], "0.0.0 应在二世块集")

# ---------- E12 保罗@卡戎 ----------
kr = require_ent("卡戎")
chk("保罗" in (kr.get("aliases") or []), "保罗 应在卡戎别名表")
chk("保罗·霍伊默尔" in (kr.get("aliases") or []), "保罗·霍伊默尔 应已在卡戎别名表（R2 已加）")
ph = df("保罗·霍伊默尔")
chk(ph == ["mainline__111_行于漫漫长路上:14.0.2"], f"保罗·霍伊默尔 DF 预期恰1@卡戎块，得 {ph}")
krc = set(kr["chunk_ids"])
p_all, p_own = df("保罗"), [c for c in df("保罗") if c in krc]
sp_all = df("圣保罗")
chk(len(p_all) == 92 and len(p_own) == 19 and len(sp_all) == 66, f"保罗/圣保罗 DF 异常: {len(p_all)}/{len(p_own)}/{len(sp_all)}")
chk(all("圣保罗" not in chunks[c] for c in p_own), "卡戎块内 保罗 不应与 圣保罗 碰撞")

# ---------- E13/E14 旅行队的别斯米尔 ----------
tbl = require_ent("旅行队的别斯米尔")
tbe = require_ent("探险家别斯米尔")
tv_cid = tbl["chunk_ids"][0]
chk(len(tbl["chunk_ids"]) == 1 and tv_cid == "appendix_unbound__006_1_6_赛季剧情:4.1.0", "旅行队块集预期恰1")
chk("别斯米尔女士" in chunks[tv_cid] and "远行队" in chunks[tv_cid], "旅行队块需含 别斯米尔女士/远行队")
bsnv = [c for c in tbe["chunk_ids"] if "别斯米尔女士" in chunks[c]]
chk(len(bsnv) == 18, f"别斯米尔女士@探险家别斯米尔 containment 预期18，得 {len(bsnv)}")
chk(len(df("旅行队的别斯米尔")) == 0, "旅行队的别斯米尔 应为 v3 归一形（DF=0）")

# ---------- E15/E16 店主米拉 ----------
dz = require_ent("店主")
dz1917 = sorted(c for c in dz["chunk_ids"] if "1917" in c)
dz20603 = sorted(c for c in dz["chunk_ids"] if "20603" in c)
chk(len(dz["chunk_ids"]) == 14 and len(dz1917) == 11 and len(dz20603) == 3, "店主 块分布异常")
chk(all("店主" in chunks[c] for c in dz20603), "第一千夜块应逐字含 店主")
dz1917_named = [c for c in dz1917 if "店主" in chunks[c]]
chk(len(dz1917_named) == 10, f"乘法轴含 店主 字面块应10（6.0.0 为纯场景块），得 {len(dz1917_named)}")
chk("店主米拉" in chunks["anecdote__1917_乘法轴上的一天:0.0.0"], "店主米拉 逐字")
chk(all("米拉" not in chunks[c] for c in dz20603), "第一千夜店主 不应叫 米拉（跨篇证据）")
ml = [c for c in df("米拉") if "卡米拉" in chunks[c]]
chk(len(ml) == 4, f"裸名 米拉 与 卡米拉 子串碰撞应4块，得 {len(ml)}（不用裸 米拉 作规范名的依据）")

# ---------- E17/E18 警卫/水手 ----------
gw = require_ent("警卫")
ss = require_ent("水手")
gw_docs = {c.split(":")[0] for c in gw["chunk_ids"]}
chk(len(gw_docs) == 4, f"警卫 应横跨4篇，得 {gw_docs}")
ss_docs = {c.split(":")[0] for c in ss["chunk_ids"]}
chk(len(ss_docs) == 2 and "无武装水手" in (ss.get("aliases") or []), "水手 分布异常")
chk(len(df("无武装水手")) == 1 and df("无武装水手")[0] in krc | set(ss["chunk_ids"]), "无武装水手 逐字位置")

print(f"preconditions: {len(ERRS)} errors")
for m in ERRS:
    print("  [PRE]", m)
assert not ERRS, "preconditions failed"

# ============================================================ entries
TS = "2026-09-26"
PROPOSAL_META_SOURCES = [
    {"file": "docs/图谱修复作战书_预注册_20260926.md", "role": "协议（§0 冲突序 / §2 角色 / R3 范围）"},
    {"file": "docs/图谱与原文质检报告_20260926.md", "role": "检6 归因表 + 修复建议清单（R094/R090/R127/R170/R231/R005/R012/乌尔里希/保罗）"},
    {"file": "data/compendium_rag/reports/rank_triage_300cn.json", "role": "14 例 corpus_not_pooled / entity_bridge=true 明细"},
    {"file": "data/knowledge/_audit/rag_testset_300_cn.json", "role": "R090/R094/R127/R170/R231/R005/R012 查询与 ref"},
    {"file": "data/compendium_rag/repairs_arbitration_20260926.md", "role": "仲裁#1：保罗→QUALIFY，执行推迟至 R3"},
    {"file": "data/compendium_rag/repairs_v2/verification_by_r1repairer.json", "role": "保罗 DF92/66圣保罗/R265 证据"},
    {"file": "data/compendium_rag/repairs_v1/proposal.json", "role": "v1 schema 参照 + 传记作家兀尔德→兀尔德 合并先例"},
    {"file": "data/lore/_huiji_cache/（474 文件）+ data/lore/wu_ming_zhe/huiji_canon|lexicon|plot_aliases|plot_glossary|wiki_zh_en.json", "role": "灰机离线缓存/词表（禁网，2026-09-13 采集）"},
    {"file": "data/compendium_rag/graph.json（7034 实体 / 29959 边，R1+R2 后现状）+ chunks.json（3695 块）", "role": "全部图谱现状核验与逐字 grep"},
]

entries = []

# ---------------- Item 1: 缺桥补链 ----------------
entries.append({
    "id": "R3-E01", "item": 1, "type": "add_alias", "target": "中央瞭望塔", "alias": "中央塔",
    "evidence": [
        ev_corpus("mainline__113_他者的悲哀:5.1.1", "中央塔", 15, 45),
        ev_corpus("mainline__113_他者的悲哀:19.1.1", "中央塔", 12, 40),
        ev_corpus("mainline__109_疯癫与文明:11.0.1", "自囚于此的囚徒", 25, 20),
        ev_corpus("mainline__109_疯癫与文明:8.0.2", "中央的瞭望塔", 12, 20),
        ev_doc("docs/图谱与原文质检报告_20260926.md 检6 R090行", "「在中央塔里自囚的医生是谁？」模拟 link() 种子=0（`中央塔` 无节点/alias）；gold=`阿莱夫`，34 块 gold 可达"),
    ],
    "before": "查询形「中央塔」在 alias_index 无落点（0 种子）；节点 中央瞭望塔（地点，24 块，alias 中心瞭望塔/瞭望塔/瞭望塔·手术室/瞭望塔·等候室）声称 R090 gold 块 mainline__109:11.0.1（阿莱夫自囚自白）但对查询形不可达",
    "after": "alias_index[中央塔]→中央瞭望塔（0.9）。逐字性：中央塔 逐字出现于该节点声称块 2/24（均在 mainline__113），满足红线3 per-owner；其声称块含 gold 块 109:11.0.1 → 图通道可达",
})

entries.append({
    "id": "R3-E02", "item": 1, "type": "add_alias", "target": "菲林士多", "alias": "Noire", "inferred": True,
    "evidence": [
        {"src": "offline-huiji data/lore/wu_ming_zhe/huiji_lexicon.json [zh2en]（本地词表，禁网）", "quote": "菲林士多 -> [\"Noire\"]"},
        {"src": "offline-huiji data/lore/wu_ming_zhe/wiki_zh_en.json（本地词表，禁网）", "quote": "菲林士多: \"Noire\""},
        {"src": "offline-huiji data/lore/_huiji_cache/f8ae467bdc5b463db196.json [莫桑女士]（本地缓存，禁网）", "quote": hq("data/lore/_huiji_cache/f8ae467bdc5b463db196.json", "Noire", 60, 40)},
        ev_doc("docs/图谱与原文质检报告_20260926.md 检6 R094行", "语料从不出现 \"Noire\"（DF=0）；需建立『词表 alias 豁免』机制"),
    ],
    "before": "测试集 R094「Noire 的中文译名是什么？」0 种子；菲林士多（52 块，0 alias）不可达",
    "after": "【inferred — 作战书 §0.2：语料 DF(Noire)=0，不满足红线3，仅入提案备用户裁决；Applier 无豁免机制时必须跳过本条，不得直接落图】alias_index[Noire]→菲林士多（ASCII 词边界 0.9），52 块入池",
})

entries.append({
    "id": "R3-E03", "item": 1, "type": "add_entity",
    "target": "福葛先生",
    "entity": {
        "eid": "福葛先生", "name": "福葛先生", "type": "角色",
        "aliases": ["奥利弗·福葛", "福葛伙计"],
        "desc": "伦敦的「雾行者」，福葛家族成员（雾行者角色故事自述「奥利弗·福葛，伦敦的雾行者」，家族宿命世代相传）；圣火纪行·东区黎明中以「福葛先生」身份在十字街开展驱雾实验，打造雾气净化器「伦敦煤烟污染勘察与清除大使」（MK.Ⅰ→MK.Ⅲ）",
        "mentions": len(fg_chunks),
        "chunk_ids": fg_chunks,
    },
    "evidence": [
        ev_corpus("anecdote__1901_雾行者角色故事:6.0.1", "奥利弗·福葛", 8, 25),
        ev_corpus("activity__23101_圣火纪行_东区黎明:0.1.1", "福葛先生", 18, 30),
        ev_corpus("activity__23101_圣火纪行_东区黎明:7.2.1", "雾气净化器", 25, 45),
        ev_corpus("anecdote__1901_雾行者角色故事:3.0.2", "福葛家族的宿命", 25, 10),
        {"src": "offline-huiji data/lore/wu_ming_zhe/huiji_lexicon.json [zh2en]（本地词表，禁网）", "quote": "雾行者 -> [\"Oliver Fog\"]；亚瑟·福葛 -> [\"Arthur Fog\"]（先祖名，语料 DF=0 不设 alias）"},
        {"src": "offline-huiji data/lore/_huiji_cache/dd48cf716bfebe7c792b.json [其他角色一览/2.x]（本地缓存，禁网）", "quote": hq("data/lore/_huiji_cache/dd48cf716bfebe7c792b.json", "亚瑟·福葛", 10, 60)},
        ev_doc("docs/图谱与原文质检报告_20260926.md 检6 R127行（归因修正）", "原归因指向 福格尔（第一防线学校教员，mainline__113，2 块）；语料实测：查询「福格先生发明的大型装置」对应 圣火纪行 的 福葛先生（福格/福葛 措辞差）与 雾气净化器（ref 净化机 DF=0）"),
    ],
    "before": "R127 gold 链人物 福葛先生（40 块：activity__23101×36 + anecdote__1901×3 + anecdote__1905×1）整体不在图；QC 原归因的 福格尔 实为另一人（SPDM 教员女士）",
    "after": "canonical 节点 福葛先生（eid==name，40 块，alias 奥利弗·福葛/福葛伙计 均逐字于属主块）；其中 3 块（1901:2.0.1/3.0.2、1905:0.0.3）经 福葛家族（其本人旁白）与 福葛（X 的称呼）指认；与 雾气净化器/伦敦煤烟污染勘察与清除大使 共块 5+ 块，R127 类查询按正确人名形即可达",
})

entries.append({
    "id": "R3-E04", "item": 1, "type": "merge_entities", "target": "伦敦煤烟污染勘察与清除大使 → 雾气净化器",
    "moved_chunks": list(ds["chunk_ids"]),
    "evidence": [
        ev_corpus("activity__23101_圣火纪行_东区黎明:7.2.1", "雾气净化器", 20, 55),
        ev_corpus("activity__23101_圣火纪行_东区黎明:10.1.2", "伦敦煤烟污染勘察与清除大使", 30, 40),
        ev_doc("docs/图谱与原文质检报告_20260926.md 检4.4 同物裂名型", "「同物裂名」先例：暴雨改革×2、奠基石海报×2、特里格拉夫×2"),
    ],
    "before": "同一台机器裂为两节点：雾气净化器（物品，10 块）与 伦敦煤烟污染勘察与清除大使（物品，3 块）——7.2.1 明文「史上最大的雾气净化器——『伦敦煤烟污染勘察与清除大使』」为同物同位语",
    "after": "单节点 雾气净化器 13 块，边自动重接（Applier merge_entities 语义）",
})

entries.append({
    "id": "R3-E05", "item": 1, "type": "add_alias", "target": "雾气净化器", "alias": "伦敦煤烟污染勘察与清除大使",
    "evidence": [
        ev_corpus("activity__23101_圣火纪行_东区黎明:10.1.0", "伦敦煤烟污染勘察与清除大使" if "伦敦煤烟污染勘察与清除大使" in chunks["activity__23101_圣火纪行_东区黎明:10.1.0"] else "雾气净化器", 25, 45),
        ev_corpus("activity__23101_圣火纪行_东区黎明:12.1.0", "伦敦煤烟污染勘察与清除大使", 30, 45),
    ],
    "before": "全名形仅作独立节点存在；合并后若不补 alias，长形查询将失去 exact 落点",
    "after": "alias_index 保留长形（0.9）；逐字于该节点声称块（含合并前既有共块 5 块：10.1.0/10.1.2/12.1.0/12.2.0/18.2.0）",
})

entries.append({
    "id": "R3-E06", "item": 1, "type": "add_alias", "target": "福格尔", "alias": "福格尔女士",
    "evidence": [
        ev_corpus("mainline__113_他者的悲哀:1.2.2", "福格尔女士", 15, 40),
        ev_corpus("mainline__113_他者的悲哀:19.1.1", "福格尔女士", 12, 45),
        ev_doc("docs/图谱与原文质检报告_20260926.md 修复建议4", "为 0-alias 高价值节点补 alias（遵守红线 3）：…福格尔…"),
    ],
    "before": "福格尔（第一防线学校教员，mainline__113，2 块）0 alias",
    "after": "alias 福格尔女士（语料唯一称呼形，逐字 2/2 块）。注：与 R127 查询形「福格先生」非一人（见 R3-E03 归因修正）",
})

entries.append({
    "id": "R3-E07", "item": 1, "type": "add_alias", "target": "金伯利女郎", "alias": "契约魅魔", "inferred": True,
    "evidence": [
        {"src": "data/knowledge/_audit/rag_testset_300_cn.json [R231]", "quote": "q=77 号往事里与格蕾丝对立的契约魅魔是谁？ ref=天使娜娜（Anjo Nala） evidence=[Anjo,Nala,娜娜,Kimberly]"},
        {"src": "offline-huiji data/lore/wu_ming_zhe/plot_glossary.json（本地词表，禁网）", "quote": hq("data/lore/wu_ming_zhe/plot_glossary.json", "金伯利女郎", 5, 120)},
        ev_doc("docs/图谱与原文质检报告_20260926.md 检6 R231行", "金伯利女郎 在图、53 块、9 alias，但无 契约魅魔（该词 DF=0，查询为转述）"),
    ],
    "before": "R231 查询的转述形「契约魅魔」在 alias_index 无落点（种子仅 无名者0.9@格蕾丝 / 77 / 泛称节点魅魔1.0）",
    "after": "【inferred — DF(契约魅魔)=0，不满足红线3，仅入提案备用户裁决；Applier 无豁免机制时必须跳过本条】alias_index[契约魅魔]→金伯利女郎（0.9）。另：裸「魅魔」不作 alias（泛称节点 魅魔 持有 canonical，R2 泛称精神，防 R018 型错种子）",
})

# ---------------- Item 2: R170 玩具盒 ----------------
entries.append({
    "id": "R3-E08", "item": 2, "type": "add_entity", "target": "玩具盒",
    "entity": {
        "eid": "玩具盒", "name": "玩具盒", "type": "概念",
        "aliases": ["玩具盒子"],
        "desc": "1987宇宙组曲中宇航员库珀花环出舱观测「暴雨」影响时的比喻意象：「宇宙在她眼前展开，如同……玩具盒子」。本中文语料唯一提及（DF=1）。评测集 R170 将「玩具盒（toy box）」列为「人们向何处去篇拉普拉斯的重要装置」答案——该装置读法来自官方英文配音语料（plot_glossary：toy box 39 次），本中文语料无该装置明文；本抽取按语料实际语义落档（零网关）",
        "mentions": 1,
        "chunk_ids": tb_chunks,
    },
    "evidence": [
        ev_corpus("activity__27101_1987宇宙组曲:17.1.0", "玩具盒子", 22, 40),
        {"src": "offline-huiji data/lore/wu_ming_zhe/plot_glossary.json（本地词表，禁网）", "quote": hq("data/lore/wu_ming_zhe/plot_glossary.json", "toy box", 60, 120)},
        {"src": "data/knowledge/_audit/rag_testset_300_cn.json [R170]", "quote": "q=人们向何处去篇里拉普拉斯的重要装置是什么？ ref=玩具盒（toy box）"},
        ev_doc("docs/图谱与原文质检报告_20260926.md 检6 R170行", "「玩具盒」不在图（语料 DF=1，唯一提及块未被抽成实体）→ 图谱可修/稀疏：抽取遗漏"),
    ],
    "before": "玩具盒 全图无节点、无 alias；唯一提及块 activity__27101:17.1.0（现由 冷周六/库珀花环/监测器 等 8 节点声称）不产生 玩具盒 落点",
    "after": "canonical 玩具盒（exact 1.0）+ alias 玩具盒子（逐字），声称唯一 DF 块；R170 miss 的机械改善取决于重排窗口（评测重校准闸门复验）",
})

# ---------------- Item 3: 乌尔里希 merge ----------------
entries.append({
    "id": "R3-E09", "item": 3, "type": "merge_entities", "target": "暴雨小组组长乌尔里希 → 乌尔里希",
    "moved_chunks": list(ul2["chunk_ids"]),
    "evidence": [
        ev_corpus("activity__24101_地球上最后的夜晚:0.2.2", "乌尔里希先生", 30, 40),
        ev_corpus("activity__24101_地球上最后的夜晚:3.1.0", "玻璃脑袋", 30, 30),
        ev_corpus("mainline__110_复乐园:3.0.1", "乌尔里希", 5, 60),
        ev_corpus("mainline__110_复乐园:7.0.1", "乌尔里希组长", 10, 35),
        {"src": "offline-huiji data/lore/wu_ming_zhe/huiji_lexicon.json [zh2en/plot_glossary]（本地词表，禁网）", "quote": "乌尔里希 -> Ulrich；plot_glossary：乌尔里希，type=角色，en=Ulrich，status=verified，note=拉普拉斯科算中心成员。（灰机单一词条，无第二乌尔里希）"},
        ev_huiji("data/lore/_huiji_cache/150c2161ffb8e33df537.json", "乌尔里希", "圣洛夫基金会", 30, 20),
    ],
    "before": "一人两节点：乌尔里希（53 块，5 alias：乌尔里希先生/乌尔里希组长/意识唤醒者研究员/玻璃缸脑袋/破译组长）∪ 暴雨小组组长乌尔里希（72 块，0 alias；71/72 块含裸名 乌尔里希）；块集零重叠，提及与边碎片化；「暴雨小组组长乌尔里希」DF=0（v3 归一形，语料实形为『「暴雨」专项研究小组的负责人乌尔里希先生』）",
    "after": "单节点 乌尔里希 125 块（53+72）、mentions 125，边自动重接；规范名取语料逐字裸名（R1 先例：传记作家兀尔德→兀尔德）。语料身份链：拉普拉斯「暴雨」专项研究小组负责人=乌尔里希先生（24101:0.2.2）→ 随身玻璃脑袋（=alias 玻璃缸脑袋，24101:3.1.0）→ 意识唤醒者研究员/破译组长（mainline__107）→ 携磁流体赴南极验证「星锑」暴雨稳定性（mainline__110）",
})

# ---------------- Item 4: 船名（R005/R012） ----------------
entries.append({
    "id": "R3-E10", "item": 4, "type": "reassign_chunk", "target": "APPLe号摇滚巨轮二世",
    "add_chunk_ids": ["mainline__105_洞穴的囚徒:0.0.1"], "removed_weld_chunks": [],
    "evidence": [
        ev_corpus("mainline__105_洞穴的囚徒:0.0.1", "摇滚巨轮", 25, 20),
        ev_corpus("mainline__105_洞穴的囚徒:0.0.0", "二世", 15, 55),
    ],
    "before": "APPLe号摇滚巨轮二世 仅声称 105:0.0.0；同景相邻块 0.0.1（「我的APPLe号『摇滚巨轮』二世！」逐字）漏收",
    "after": "二世 节点 1→2 块（同篇承接段），mentions=2",
})

entries.append({
    "id": "R3-E11", "item": 4, "type": "keep_with_note", "target": "APPLe号摇滚巨轮二世",
    "note": "QC R005/R012「船名分裂→合并」被语料明文反证，不合并：APPLe号（一世，alias 摇滚巨轮，mainline__000 泰晤士河被击沉）与 APPLe号摇滚巨轮二世（苏芙比买的新船，mainline__105 爱琴海沉没）为两代不同的船。反证：105:0.0.0「那这艘船为什么是『二世』？……这可是苏芙比给我们买的新船啊」；anecdote__1920:5.0.1「两代APPLe号！一艘毁于泰晤士河上的『炮击』，另一艘则葬身于爱琴海的风浪」；anecdote__1917:7.0.0「全新的APPLe号三世」（第三艘）。合并即 R1 式错焊。R005/R012 的 miss 主因应改判措辞差异（摇滚苹果/Rockin/扎内塔 DF=0），船名分裂仅为次要残差",
    "evidence": [
        ev_corpus("mainline__105_洞穴的囚徒:0.0.0", "苏芙比给我们买的新船", 15, 15),
        ev_corpus("anecdote__1920_最佳乐队:5.0.1", "两代APPLe号", 12, 45),
        ev_corpus("anecdote__1917_乘法轴上的一天:7.0.0", "APPLe号三世", 15, 25),
        ev_doc("docs/图谱与原文质检报告_20260926.md 检6 R005/R012行", "「船在图中裂成两个不相连节点……图谱可修：船名分裂」——本条按冲突序（语料明文反证＞QC 推断）改判 keep"),
    ],
    "before": "QC 建议合并 APPLe号 与 APPLe号摇滚巨轮二世",
    "after": "keep：两节点保持独立（一世 4 块 / 二世 2 块），并附语料反证",
})

# ---------------- Item 5: 保罗 ----------------
entries.append({
    "id": "R3-E12", "item": 5, "type": "remove_alias", "target": "卡戎", "alias": "保罗",
    "evidence": [
        {"src": "data/compendium_rag/repairs_arbitration_20260926.md 仲裁#1", "quote": "保罗 keep vs qualify→保罗·霍伊默尔：QUALIFY（DF92 中 66 块为圣保罗城市碰撞；R265 的卡戎 0.9 为错种子，qualify 反而改善 R265）→ 采纳，执行推迟至 R3"},
        {"src": "data/compendium_rag/repairs_v2/verification_by_r1repairer.json", "quote": "DF(保罗)=92，其中 66 块为 圣保罗（城市）子串碰撞，仅 26 块真指人名；卡戎 67 声称块中 19 块含非圣保罗的 保罗"},
        ev_corpus("mainline__111_行于漫漫长路上:1.1.2", "保罗", 12, 40),
        ev_corpus("mainline__111_行于漫漫长路上:23.0.0", "名叫保罗的年轻人", 15, 30),
    ],
    "before": "alias_index[保罗]→卡戎（0.9）；DF(保罗)=92（66 块圣保罗城市碰撞，26 块真指人名，其中 19 块属卡戎），R265 类查询产生 卡戎0.9 假种子",
    "after": "摘除裸 保罗；卡戎 保留 亡者/保罗·霍伊默尔/士官/收尸人/邮递员 + canonical。仲裁 qualify 的 add 半步（保罗·霍伊默尔）R2 已落图且逐字（mainline__111:14.0.2，DF=1），本条为 remove 半步",
})

# ---------------- Item 6: 旅行队的别斯米尔 ----------------
entries.append({
    "id": "R3-E13", "item": 6, "type": "merge_entities", "target": "旅行队的别斯米尔 → 探险家别斯米尔",
    "moved_chunks": list(tbl["chunk_ids"]),
    "evidence": [
        ev_corpus("appendix_unbound__006_1_6_赛季剧情:4.1.0", "别斯米尔女士", 12, 60),
        ev_corpus("appendix_unbound__006_1_6_赛季剧情:4.1.0", "远行队", 15, 35),
        ev_corpus("activity__16101_朔日手记:0.0.0", "别斯米尔女士", 12, 35),
        {"src": "offline-huiji data/lore/_huiji_cache/49910dc30331af4cb845.json [其他角色一览/1.x]（本地缓存，禁网；R1 同源）", "quote": hq("data/lore/_huiji_cache/49910dc30331af4cb845.json", "别斯米尔", 5, 90)},
        ev_doc("docs/图谱修复作战书_预注册_20260926.md", "appendix_unbound__006 为 1.6 赛季剧情（朔日手记同版本）；灰机单词条 别斯米尔/Bessmert，无第二别斯米尔"),
    ],
    "before": "一人两节点：探险家别斯米尔（70 块：朔日手记 69 + 复乐园 1，alias 别斯米尔）与 旅行队的别斯米尔（1 块：1.6 赛季剧情，0 alias）；同对人物（别斯米尔女士+小叶尼塞）、同一远行队语境；「旅行队的别斯米尔」DF=0（v3 归一形）",
    "after": "单节点 探险家别斯米尔 71 块；规范名保持 R1 既有 canonical（与 玛尔塔/兀尔德 独立，非卡卡尼亚焊组成员）",
})

entries.append({
    "id": "R3-E14", "item": 6, "type": "add_alias", "target": "探险家别斯米尔", "alias": "别斯米尔女士",
    "evidence": [
        ev_corpus("activity__16101_朔日手记:0.0.0", "别斯米尔女士", 12, 35),
        ev_corpus("activity__16101_朔日手记:0.0.2", "别斯米尔女士", 10, 40),
        ev_corpus("appendix_unbound__006_1_6_赛季剧情:4.1.0", "别斯米尔女士", 12, 30),
    ],
    "before": "语料高频敬称形 别斯米尔女士（DF=19）无落点；查「别斯米尔女士」仅靠裸 alias 别斯米尔 0.9",
    "after": "alias_index[别斯米尔女士]→探险家别斯米尔（exact→alias 0.9）；逐字于属主声称块 18/70（合并后 19/71）",
})

# ---------------- Item 7: 警卫/店主/水手 ----------------
entries.append({
    "id": "R3-E15", "item": 7, "type": "add_entity", "target": "店主米拉",
    "entity": {
        "eid": "店主米拉", "name": "店主米拉", "type": "角色",
        "aliases": ["米拉小姐"],
        "desc": "拉普拉斯博物馆休息区冰淇淋店的店主（乘法轴上的一天：「我已经听店主米拉小姐说了」）；37 以盈亏平衡分析助其渡过经营危机，店铺最终在转让前迎来「冰淇淋奇迹」",
        "mentions": len(dz1917_named),
        "chunk_ids": list(dz1917_named),
    },
    "evidence": [
        ev_corpus("anecdote__1917_乘法轴上的一天:0.0.0", "店主米拉", 12, 40),
        ev_corpus("anecdote__1917_乘法轴上的一天:4.0.0", "冰淇淋店", 15, 45),
        ev_corpus("character__20603_第一千夜:5.0.0", "路边小店", 12, 40),
        ev_doc("docs/图谱与原文质检报告_20260926.md 检4.3/修复建议2", "泛称 canonical 节点（店主 在列）跨篇焊嫌疑：按篇限定名或拆分"),
    ],
    "before": "泛称节点 店主（14 块）为跨篇焊：character__20603_第一千夜（路边二手店女店主，无名，3 块）∪ anecdote__1917_乘法轴上的一天（冰淇淋店店主，语料具名 米拉，11 块）——两人两店两故事",
    "after": "新具名节点 店主米拉（10 块逐字含 店主，alias 米拉小姐 逐字于 0.0.0）；规范名不用裸 米拉（与 卡米拉 存在 4 块子串碰撞，防 R265 型假种子）",
})

entries.append({
    "id": "R3-E16", "item": 7, "type": "reassign_chunk", "target": "店主",
    "add_chunk_ids": [], "removed_weld_chunks": list(dz1917),
    "evidence": [
        ev_corpus("character__20603_第一千夜:5.0.0", "店主", 8, 45),
        ev_corpus("anecdote__1917_乘法轴上的一天:0.0.0", "店主", 8, 30),
    ],
    "before": "店主 节点 14 块横跨 第一千夜/乘法轴上的一天 两个不相关故事",
    "after": "店主 保留 3 块（第一千夜 路边小店女店主，语料无名）；11 块移出，其中 10 块归 店主米拉、6.0.0（纯场景块，无任何指称）不再由泛称节点声称。泛称节点本体保留（R4 grounding:none 候选），仅解除跨篇焊",
})

entries.append({
    "id": "R3-E17", "item": 7, "type": "keep_with_note", "target": "警卫",
    "note": "跨篇焊复核成立但保守保留：4 块横跨 4 篇（mainline__103 故事一无所有（按倒伊莎贝拉的警卫）/ character__20601 旧金山小子 / anecdote__1908 齿轮的意志 / anecdote__1910 风吹乌哈拉），均为无名群众角色，语料零具名，拆分缺乏 R1 卡卡尼亚式具名锚点且别名 警卫 只能落到其中之一（setdefault 遮蔽）；4 块规模 PPR 污染半径有限。建议 R4 flag_grounding 处理",
    "evidence": [
        ev_corpus("mainline__103_故事一无所有:10.1.1", "警卫", 10, 30),
        ev_corpus("anecdote__1910_风吹乌哈拉:0.0.0", "警卫", 10, 35),
    ],
    "before": "警卫 4 块/4 篇（不同故事的不同个体）",
    "after": "keep（记录在案，R4 候选）",
})

entries.append({
    "id": "R3-E18", "item": 7, "type": "keep_with_note", "target": "水手",
    "note": "跨篇焊复核成立但保守保留：mainline__110 ×2（乌尔里希纵帆船上的水手，alias 无武装水手 逐字于 110:7.0.2「除一名无武装水手外，纵帆船已确认清空」）+ activity__23101:7.1.0（圣火纪行「刚从蒂尔伯里码头回来的水手」，无名，1 块）。第二实例语料无名且仅 1 块，拆分收益不足；记录在案，R4 候选",
    "evidence": [
        ev_corpus("mainline__110_复乐园:7.0.2", "无武装水手", 15, 30),
        ev_corpus("activity__23101_圣火纪行_东区黎明:7.1.0", "水手", 30, 40),
    ],
    "before": "水手 3 块/2 篇（110 乌尔里希纵帆船水手 ∪ 23101 蒂尔伯里码头水手）",
    "after": "keep（记录在案，R4 候选）",
})

# ============================================================ simulation (applier logic replica)
def apply_all(g):
    g2 = copy.deepcopy(g)
    ents = {e["eid"]: e for e in g2["entities"]}
    applied = []
    for entry in entries:
        et = entry["type"]
        if et in ("keep_with_note", "keep_node", "flag_grounding_r4"):
            applied.append((entry["id"], "noop")); continue
        if et == "add_alias":
            o, a = entry["target"], entry["alias"]
            chk(o in ents, f"{entry['id']} 属主缺失 {o}")
            chk(a not in ents[o].get("aliases", []), f"{entry['id']} alias 已存在 {a}@{o}")
            if entry.get("inferred"):
                WARN.append(f"{entry['id']} inferred alias（按作战书 §0.2 不落图，需用户裁决）: {a}@{o}")
                applied.append((entry["id"], "skipped-inferred")); continue
            ents[o].setdefault("aliases", []).append(a)
            applied.append((entry["id"], "ok"))
        elif et == "remove_alias":
            o, a = entry["target"], entry["alias"]
            ents[o]["aliases"] = [x for x in ents[o].get("aliases", []) if x != a]
            applied.append((entry["id"], "ok"))
        elif et == "add_entity":
            p = entry["entity"]
            chk(p["eid"] not in ents, f"{entry['id']} eid 已存在 {p['eid']}")
            ents[p["eid"]] = {"eid": p["eid"], "name": p["name"], "type": p["type"], "aliases": list(p["aliases"]),
                              "desc": p["desc"], "mentions": p["mentions"], "chunk_ids": list(p["chunk_ids"])}
            g2["entities"].append(ents[p["eid"]])
            applied.append((entry["id"], "ok"))
        elif et == "merge_entities":
            src, dst = [x.strip() for x in entry["target"].split("→", 1)]
            ents[dst]["aliases"] += [a for a in ents[src].get("aliases", []) if a not in ents[dst].get("aliases", [])]
            ents[dst]["chunk_ids"] += ents[src].get("chunk_ids", [])
            ents[dst]["mentions"] = ents[dst].get("mentions", 0) + ents[src].get("mentions", 0)
            for e in g2["edges"]:
                if e["src"] == src: e["src"] = dst
                if e["dst"] == src: e["dst"] = dst
            g2["entities"] = [e for e in g2["entities"] if e["eid"] != src]
            del ents[src]
            applied.append((entry["id"], "ok"))
        elif et == "reassign_chunk":
            o = entry["target"]
            cur = ents[o].setdefault("chunk_ids", [])
            for cid in entry.get("removed_weld_chunks", []):
                if cid in cur: cur.remove(cid)
            for cid in entry.get("add_chunk_ids", []):
                if cid not in cur: cur.append(cid)
            ents[o]["mentions"] = len(cur)
            applied.append((entry["id"], "ok"))
    return g2, applied

g2, applied = apply_all(G)

# post checks (applier post_validate + extras)
ents2 = {e["eid"]: e for e in g2["entities"]}
chk(len(ents2) == len(g2["entities"]), "eid 重复")
name_ct = Counter(e["name"] for e in g2["entities"])
chk(not [n for n, c in name_ct.items() if c > 1], "重名规范节点")
for e in g2["entities"]:
    chk(e["eid"] == e["name"], f"eid!=name {e['eid']}")
    for cid in e.get("chunk_ids", []):
        chk(cid in chunks, f"悬空 chunk {cid}@{e['eid']}")
for ed in g2["edges"]:
    chk(ed["src"] in ents2, f"悬空 src {ed['src']}")
    chk(ed["dst"] in ents2, f"悬空 dst {ed['dst']}")
    for cid in ed.get("chunk_ids", []):
        chk(cid in chunks, f"边悬空 chunk {cid}")
# mentions == len(set(chunk_ids)) for touched entities
for n in ["乌尔里希", "探险家别斯米尔", "雾气净化器", "APPLe号摇滚巨轮二世", "卡戎", "店主", "福葛先生", "玩具盒", "店主米拉", "中央瞭望塔", "菲林士多", "金伯利女郎", "福格尔"]:
    e = ents2[n]
    chk(e.get("mentions") == len(set(e.get("chunk_ids", []))), f"mentions!=chunks {n}: {e.get('mentions')} vs {len(set(e.get('chunk_ids', [])))}")
# per-owner verbatim for every alias added (on final owner chunk set)
for entry in entries:
    if entry["type"] == "add_alias" and not entry.get("inferred"):
        o, a = ents2[entry["target"]], entry["alias"]
        oc = o.get("chunk_ids", [])
        n_hit = sum(1 for cid in oc if a in chunks[cid])
        chk(n_hit >= 1, f"新 alias 非逐字于属主块: {a}@{entry['target']}")
# no dup chunk_ids inside touched entities
for n in ["乌尔里希", "探险家别斯米尔", "雾气净化器"]:
    cs = ents2[n]["chunk_ids"]
    chk(len(cs) == len(set(cs)), f"{n} chunk_ids 有重复")

# link() simulation before/after
def name_matches(name, ql):
    if not name or not ql: return False
    if all(ord(c) < 128 for c in name):
        return bool(re.search(r"(?<![A-Za-z0-9_])" + re.escape(name.lower()) + r"(?![A-Za-z0-9_])", ql))
    if len(name) >= 2: return name in ql
    return bool(re.search(r"(?<![\u4e00-\u9fff])" + re.escape(name) + r"(?![\u4e00-\u9fff])", ql))

def build_alias_index(g):
    ents = {e["eid"]: e for e in g["entities"]}
    idx = {}
    for e in g["entities"]:
        idx.setdefault(e["name"], e["eid"])
    for e in g["entities"]:
        for a in e.get("aliases", []):
            idx.setdefault(a, e["eid"])
    return idx, ents

def link(g, q, top_k=6):
    idx, ents = build_alias_index(g)
    ql = q.lower(); seeds = {}
    for name in sorted(idx.keys(), key=len, reverse=True):
        if name_matches(name, ql):
            eid = idx[name]
            how = "exact" if name == ents[eid]["name"] else "alias"
            sc = 1.0 if how == "exact" else 0.9
            if eid not in seeds or sc > seeds[eid][1]:
                seeds[eid] = (ents[eid]["name"], sc, how)
    return sorted([(v[0], v[1], v[2]) for v in seeds.values()], key=lambda x: -x[1])[:top_k]

QUERIES = {
    "R090": "在中央塔里自囚的医生是谁？",
    "R094": "Noire 的中文译名是什么？",
    "R127": "福格先生发明的大型装置是什么？",
    "R170": "人们向何处去篇里拉普拉斯的重要装置是什么？",
    "R231": "77 号往事里与格蕾丝对立的契约魅魔是谁？",
    "R005": "洞穴的囚徒篇的故事主要发生在什么载具上？",
    "R012": "苏芙比买下摇滚苹果号后，船上由扎内塔担任什么职务？",
    "R018": "结合“老伙计”与“经验丰富的猎人”两个称呼，这位角色是谁？",
}
linksim = {}
for qid, q in QUERIES.items():
    linksim[qid] = {"query": q, "before": link(G, q), "after": link(g2, q)}

# hypothetical: inferred aliases applied (needs user 豁免 decision — NOT the default post state)
g3 = copy.deepcopy(g2)
e3 = {e["eid"]: e for e in g3["entities"]}
e3["菲林士多"].setdefault("aliases", []).append("Noire")
e3["金伯利女郎"].setdefault("aliases", []).append("契约魅魔")
for qid in ("R094", "R231"):
    linksim[qid]["after_if_inferred_applied"] = link(g3, QUERIES[qid])

chk(not ERRS, "post simulation errors")
print(f"\nsimulation: applied={[(i, s) for i, s in applied]}")
print(f"errors={len(ERRS)} warnings={len(WARN)}")
for m in ERRS: print("  [POST]", m)
for w in WARN: print("  [WARN]", w)
print("\nlink() before/after:")
for qid, r in linksim.items():
    print(f"  {qid}: {r['before']}  ->  {r['after']}")
print(f"\n实体 {len(G['entities'])} -> {len(g2['entities'])} | 边 {len(edges)} -> {len(g2['edges'])}")

assert not ERRS, "validation failed — proposal not written"

# ============================================================ write
proposal = {
    "meta": {
        "author": "R3-repairer",
        "timestamp": TS,
        "network": "none — huiji WAF 403 禁网（见 data/compendium_rag/huiji_pages/_prefetch_log.json）；身份裁决全部来自本地缓存 data/lore/_huiji_cache/（474 文件）+ data/lore/wu_ming_zhe/ 词表 + 语料逐字 grep",
        "schema": "v1（target=属主字符串；entity=dict；列表为 list；merge target='A → B'）— 与 repairs_v1/proposal.json 同构，适配 scripts/_graph_apply_repairs.py",
        "sources": PROPOSAL_META_SOURCES,
        "conflict_order": "语料明文反证 > 灰机 > 图谱现状 > 审计推断（作战书 §0）；语料反证条目：R3-E11（船名不合并）、E03（R127 归因修正：福葛先生≠福格尔）、E02/E07/E08（inferred/稀疏标注）",
        "counts": {"entries": len(entries), "add_entity": 3, "add_alias": 6, "remove_alias": 1, "merge_entities": 3, "reassign_chunk": 2, "keep_with_note": 3},
    },
    "entries": entries,
}
with open(os.path.join(OUTDIR, "proposal.json"), "w", encoding="utf-8") as f:
    json.dump(proposal, f, ensure_ascii=False, indent=1)

selfval = {
    "preconditions": "PASS（全部断言见 _build_proposal.py）",
    "simulation": {"applied": [{"id": i, "status": s} for i, s in applied], "errors": ERRS, "warnings": WARN},
    "post_validate": "PASS：无 eid 重复/无重名/eid==name/无悬空 chunk（实体+边）/无悬空边端点/触碰实体 mentions==len(set(chunk_ids))/新 alias 均逐字于属主声称块/触碰实体 chunk_ids 无重复",
    "graph_delta": {"entities": f"{len(G['entities'])} -> {len(g2['entities'])}", "edges": f"{len(edges)} -> {len(g2['edges'])}"},
    "link_simulation": linksim,
}
with open(os.path.join(OUTDIR, "_selfval.json"), "w", encoding="utf-8") as f:
    json.dump(selfval, f, ensure_ascii=False, indent=1)
print("\nwritten proposal.json + _selfval.json")
