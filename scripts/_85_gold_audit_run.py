# -*- coding: utf-8 -*-
"""_85: gold-label defect audit for the 31 still-missed questions on the 300cn set.

READ-ONLY audit. Writes exactly one sidecar file:
    data/knowledge/_audit/_85_gold_audit.json

Never touches rag_testset_300_cn.json or any existing test set.

Method (mirrors the official hit test):
    blob = f"{c.text}\n{c.chapter_title}\n{c.scene_title}\n{c.part_title}"
    hit  = any(k in blob for k in keywords)
For every gold keyword we count (a) chunks containing it and (b) raw occurrences,
and for low-frequency keywords (<= 5 chunks) we capture surrounding context so a
substring coincidence / metaphor / unrelated homonym can be told apart from a
genuine answer token. Verdicts are hand-judged from that printed context; the
counts and the context snippets are computed live so the file is reproducible.

Usage:
    $env:PYTHONPATH="src;scripts"; $env:PYTHONIOENCODING="utf-8"
    .venv/Scripts/python.exe scripts/_85_gold_audit_run.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from _lex_channel_full import load_cases              # noqa: E402
from compendium_rag import pipeline as P              # noqa: E402
from compendium_rag.config import get_settings        # noqa: E402

TESTSET = ROOT / "data/knowledge/_audit/rag_testset_300_cn.json"
OUT = ROOT / "data/knowledge/_audit/_85_gold_audit.json"

QIDS = [
    "R001", "R005", "R011", "R012", "R030", "R043", "R045", "R073", "R080", "R090",
    "R094", "R110", "R127", "R142", "R166", "R170", "R171", "R180", "R183", "R201",
    "R229", "R242", "R244", "R248", "R263", "R273", "R288", "R292", "R297", "R298",
    "R300",
]

# ---------------------------------------------------------------------------
# Hand judgements. `assessment` cites the decisive corpus context; the numeric
# counts that accompany it in the output are computed at run time.
# ---------------------------------------------------------------------------
V = {
    "R001": dict(
        verdict="valid", confidence="medium",
        suggested=["夏洛特", "奥黑根"],
        assessment=(
            "夏洛特 是有效 gold：23101:3.2.1「躲在十字街古宅中的女巫……还有什么比这些更适合夏洛特·奥黑根？」、"
            "23101:6.0.1「还是，你更习惯夏洛特·奥黑根这个名字？」——与 ref「Charlotte O'Hagan（伦敦十字街女巫）」同一人。"
            "但 4 个 gold 中 3 个语料 0 命中：Charlotte 为英文原形、夏洛蒂 为异译、奥哈根 为错字"
            "（语料固定写作 奥黑根，12 块/22 次）；题干主语「薇洛」在语料中亦 0 次，属别名缺口。"
        ),
    ),
    "R005": dict(
        verdict="defective", confidence="high",
        suggested=["APPLe号"],
        assessment=(
            "沿用既有侧车结论并复核：Rockin 与 ship 语料 0 次；「号船」唯一命中是 "
            "activity__24101:16.0.1「没人比老道的前 APPLe 号船长更了解广播室的布局了！」——子串巧合，并非载具名。"
            "真实载具在语料中写作「APPLe号」（11 块），『摇滚苹果号』0 次。"
        ),
    ),
    "R011": dict(
        verdict="valid", confidence="medium",
        suggested=None,
        assessment=(
            "牙仙 真实指代答案人物（ref Tooth Fairy）：牙仙女士即负责照看/牙科的医生，语料中大量以「牙仙女士」「医生」称之。"
            "但第二个 evidence 组 ['ship','Rockin'] 语料 0 次，与本题毫不相干（与 R005 的载具关键词同形，疑为串题污染）；"
            "英文写法 Tooth Fairy 在语料中 0 次（语料只有中文「牙仙」），故「英文名」在语料内无法直接命中。"
            "gold 仍存在有效中文锚点，题目可答，故判为有效（低区分度噪声关键词已标出）。"
        ),
    ),
    "R012": dict(
        verdict="defective", confidence="high",
        suggested=None,
        assessment=(
            "Zanetta / standkeeper / Rockin 语料均 0 次；唯一有命中的「管理员」6 块/10 次全部是无关同名："
            "103/113 的图书馆管理员、25101 的仓库管理员、17703 的灯塔管理员、109 的科马拉文化管理员——"
            "没有任何一块与「苏芙比买船 / 扎内塔职务」相关。语料中『摇滚苹果号』『苹果号』『扎内塔』『看塔人』全部 0 次，"
            "只有『APPLe号』（11 块，属星锑）。答案实体在语料中不存在。"
        ),
    ),
    "R030": dict(
        verdict="defective", confidence="high",
        suggested=None,
        assessment=(
            "Doris 与 多里斯 语料均 0 次——语料没有「多里斯医生」这个人。唯一有命中的 gold 是地点词「维也纳」（122 块/222 次），"
            "它是篇章背景（1.7 维也纳），与题目所问的「英文名」无关，属不相干关键词造成的假可答。"
            "语料中的医生是 德洛丝医生（69 块/243 次，盲眼医生/作家兀尔德）与 施瓦茨医生（106 维也纳篇）。"
        ),
    ),
    "R043": dict(
        verdict="defective", confidence="high",
        suggested=["乌尔里希"],
        assessment=(
            "Ulrich 语料 0 次（语料只有中文「乌尔里希」，125 块/781 次）。第二个 gold『37』是 孤独之歌 的另一位角色"
            "（数字人 37），并且作为纯数字串在语料命中 182 块/1407 次（37岁、37次、37%……），"
            "既不指代乌尔里希，也不指代其英文名——是数字子串巧合，不构成答案关键词。"
        ),
    ),
    "R045": dict(
        verdict="defective", confidence="high",
        suggested=None,
        assessment=(
            "Zero 与 Apeiron 语料 0 次；唯一有命中的『阿派朗』（35 块/44 次）是学派/岛屿之名"
            "（107:3.0.0「阿派朗学派传授的真理是理智化的」），不是题目所问的「数字几」。"
            "『零号』语料 0 次，答案数字 0 在 gold 中完全没有对应关键词；"
            "「阿派朗，无限定者，万物的本源」出现在 105:19.0.0，与『零号概念』无关。"
        ),
    ),
    "R073": dict(
        verdict="defective", confidence="medium",
        suggested=None,
        assessment=(
            "暗林 / woods / forest 语料 0 次——真正的专名答案「暗林」在语料中不存在。唯一有命中的『森林深处』8 块/9 次是"
            "跨篇章的通用方位短语（101、12101、20101、1901、1915），12101 内的 3 次全部只是「望向森林深处」"
            "「消失在森林深处」「看向森林深处」，没有任何一块说明巨怪居住在何处；"
            "语料对这只怪只写『巨大魔精』（12101 内 4 块）、『爬回巢穴里去了』（7.1.0）与标题『苔藓山洞』。"
        ),
    ),
    "R080": dict(
        verdict="valid", confidence="high",
        suggested=None,
        assessment=(
            "1971 仅 1 块/1 次，且正是答案句：activity__12101_绿湖噩梦:0.0.1「那是在1971年的一个夜晚，雨水从天上降下来」"
            "（恐怖通讲述绿湖营地事件）。另两个 gold（Green Lake / camp）语料 0 次，是英文缺失噪声，不影响有效性。"
        ),
    ),
    "R090": dict(
        verdict="valid", confidence="high",
        suggested=["阿莱夫", "自囚", "狱医"],
        assessment=(
            "阿莱夫 43 块/218 次真实指代答案（109:13.0.0「您就是阿莱夫，监狱的控制者？」）；"
            "自囚 1 块/1 次且正是答案自述（109:11.0.1「我不过是一名选择自囚于此的囚徒罢了」），"
            "并经 109:13.0.1 与 8.0.4 确认狱医/梅林是阿莱夫的人格之一。"
            "Aleph / central tower 0 次；『中央塔』2 块均在 mainline__113 他者的悲哀（气象鸽基座），"
            "与科马拉的瞭望塔/巨塔无关，是无效关键词（不改变有效性）。"
        ),
    ),
    "R094": dict(
        verdict="valid", confidence="high",
        suggested=None,
        assessment=(
            "菲林士多 53 块/408 次真实指代答案：25101:1.2.2「梁月：菲林士多。」即《神秘警探C07》导演之名，"
            "25101:3.2.2「您是说……菲林士多导演？」。Noire 语料 0 次（英文源串缺失，属噪声）。"
        ),
    ),
    "R110": dict(
        verdict="valid", confidence="high",
        suggested=None,
        assessment=(
            "天使娜娜 14 块/63 次真实指代答案：108:12.0.2「娜娜，娜娜·哈丽。热情之家的……天使娜娜。」"
            "即金伯利女郎的本名；108:16.x 全程以「天使娜娜」称呼她。Kimberly / Anjo / Nala 均 0 次（英文缺失噪声）。"
        ),
    ),
    "R127": dict(
        verdict="defective", confidence="high",
        suggested=["雾气净化器", "净化器"],
        assessment=(
            "沿用既有侧车结论并复核：purifier 与 净化机 语料 0 次；purification 仅 1 次，"
            "出现在 mainline__105:13.0.0 的英文哲学引文「The greatest purification of all is, therefore, science」，"
            "与「装置」无关。真实答案写作「雾气净化器」（activity__23101_圣火纪行_东区黎明 5 块）。"
        ),
    ),
    "R142": dict(
        verdict="valid", confidence="medium",
        suggested=None,
        assessment=(
            "谋杀案 9 块/11 次，其中 3 块确在 activity__35101_绿松石蛇俱乐部：6.0.1「接连五起的神秘学谋杀案……"
            "和这起连环案件有关」、11.2.3「而是那起轰动的连环谋杀案」、14.0.4「画作是谋杀案的关键」——确实指本案，故判有效。"
            "但需注意两点（borderline）：(1) 它是通用名词，本案在语料中更常称「神秘学连环案件 / 连环命案」；"
            "(2) 其余 6 块分布在 mainline__109（疯癫与文明）与 appendix_unbound__005（佩希塔的三十起谋杀案），"
            "而官方 hit 测试不限篇章，存在跨篇章假阳性风险。"
        ),
    ),
    "R166": dict(
        verdict="defective", confidence="high",
        suggested=None,
        assessment=(
            "九方 语料 0 次——答案实体在语料中根本不存在。唯一有命中的『地点』是通用名词（191 块/206 次，"
            "遍布全书），与「九方」毫无关系，是典型的不相干关键词造成假可答。"
            "朔日手记篇真实地名是 沛城（27 块/35 次，16101 内 12 块）、折罗漫关、玉门关；若原意为「沛城」应改 gold。"
        ),
    ),
    "R170": dict(
        verdict="defective", confidence="high",
        suggested=["玩具箱"],
        assessment=(
            "沿用既有侧车结论并复核：玩具盒 唯一命中 activity__27101_1987宇宙组曲:17.1.0 是比喻句"
            "「再一次眨眼后，宇宙在她眼前展开，如同……玩具盒子。」；toy box 语料 0 次。"
            "真实答案写作「玩具箱」（33 块，含 activity__36101_人们向何处去 多块）。"
        ),
    ),
    "R171": dict(
        verdict="defective", confidence="high",
        suggested=None,
        assessment=(
            "SPDM（以及 spdm / S.P.D.M 各写法）与「初级防御学园」「防御学园」「学园」在语料中全部 0 次。"
            "唯一有命中的『委外合约人才管理组织』（9 块/15 次）是组织机构名"
            "（106:1.0.1「更多内部人员愿意根据职能称其为『历史维护小组』」），既不是学园也不是缩写，"
            "且在题目所指的 mainline__113_他者的悲哀 中 0 次。语料中的学校是『第一防线学校』（72 块/104 次），"
            "但全书没有任何缩写形式（『缩写』仅 1 块，指 107 的琼斯多项式）。"
        ),
    ),
    "R180": dict(
        verdict="defective", confidence="high",
        suggested=None,
        assessment=(
            "clockwork 语料 0 次；『发条』16 块/25 次全部是『发条玩具』（14 块）——金伯利/天使娜娜的封印物："
            "108:15.1.1「一个丑陋的发条玩具……这是金伯利的封印物，拿着这个，她不能违抗你」、"
            "108:17.2.0「发条玩具已经被打坏了」。它与「无名者幼年被植入的、能生成人格与记忆的装置」无关："
            "含『无名者』且含『发条』的块数为 0；语料中「植入」5 块全在 activity__385101_聚合浪潮（思想控制器），"
            "与无名者无涉。属与 R127/R170 同族的「答案词被无关同族实体占用」缺陷。"
        ),
    ),
    "R183": dict(
        verdict="defective", confidence="high",
        suggested=["玛蒂尔达"],
        assessment=(
            "Matilda / Bouanich / Boaniche / Sonnet 语料全部 0 次；唯一有命中的『十四行诗』（384 块/2346 次）"
            "是另一个角色（第一助手 Sonnet），与玛蒂尔达是两个人：103:0.0.0 教员先点「玛蒂尔达」、随后说"
            "「十四行诗的回答是正确的」；103:3.0.0 两人迎面相撞。27 块同时出现、118 块只有玛蒂尔达（她本人 145 块/1116 次）。"
            "用一个不同角色的名字做 gold，是「不相干人名」型缺陷。"
        ),
    ),
    "R201": dict(
        verdict="valid", confidence="high",
        suggested=None,
        assessment=(
            "哑谜 109 块/1025 次真实指代答案（ref Enigma（哑谜））：107:4.0.0 起「哑谜」即研究员阿德勒的代号，"
            "25101:20.0.2 等亦沿用。Enigma 语料 0 次（英文缺失噪声）。"
        ),
    ),
    "R229": dict(
        verdict="valid", confidence="high",
        suggested=None,
        assessment=(
            "雷米特杯失窃案 40 块命中，但全部只出现在标题字段（chapter_title/part_title），正文 .text 内 0 次——"
            "按官方 hit 口径（blob 含标题）仍属有效 gold，且它正是答案案名。梅兰妮 28 块/303 次、皮克勒斯 48 块/366 次"
            "均真实指代答案角色。Melania / Pickles 英文 0 次（噪声）。"
        ),
    ),
    "R242": dict(
        verdict="valid", confidence="high",
        suggested=None,
        assessment=(
            "保利娜 19 块/73 次真实指代答案：20101:2.0.1「她的名字叫作保利娜·勒萨奇」、"
            "2.0.2「圣洛夫基金会所有的殉职人员……都在这里」「而保利娜……就在你们眼前」；"
            "乔·布朗（J）自称「来找我的妹妹」（乔·布朗 5 块/6 次），与题干「乔·布朗的义妹」对应"
            "（语料用「妹妹」，『义妹』本身 0 次）。Paulina 语料 0 次（英文缺失噪声）。"
        ),
    ),
    "R244": dict(
        verdict="valid", confidence="high",
        suggested=None,
        assessment=(
            "芝加哥 10 块/18 次真实指代答案：101:2.0.0【标题卡】芝加哥营救＋副标题「1929年2月14日，芝加哥的爱侣们在钟声中"
            "拥吻」；斯奈德的义姐玛丽安正是在该篇章（101:13.1.0）被救出；104:17.2.0「斯奈德……我们在芝加哥认识的朋友」。"
            "Chicago 语料 0 次（英文缺失噪声）。"
        ),
    ),
    "R248": dict(
        verdict="valid", confidence="high",
        suggested=None,
        assessment=(
            "阿尔卡纳 99 块/382 次真实指代答案：102:1.0.0「你可以称呼我为阿尔卡纳」「『重塑之手』的幕后领导者」；"
            "海因里希（106）为重塑之手成员，其效忠对象即阿尔卡纳。Arcana 语料 0 次（英文缺失噪声）。"
        ),
    ),
    "R263": dict(
        verdict="valid", confidence="high",
        suggested=None,
        assessment=(
            "远旅 20 块/42 次真实指代答案：27101:4.0.0「『漫长的旅程』和『旅行』，合并起来——『远旅』」、"
            "4.0.1「远旅：远旅。」（角色以旅行者号命名）。Voyager 语料 0 次（英文缺失噪声）。"
        ),
    ),
    "R273": dict(
        verdict="defective", confidence="high",
        suggested=["来亚什基", "卢恩矿石"],
        assessment=(
            "Ryashki 与 Vila 语料 0 次；唯一有命中的『维拉』（91 块/816 次）是题干里的那位少女教师本人"
            "（18101:2.0.2「您能像维拉老师一样，为我们讲课吗？」、27101:5.1.0「教师的脚边……维拉」），"
            "是题目的主语而不是答案。真正的答案『来亚什基』（99 块/337 次，18101 内 99 块；0.1.1 明写"
            "「咱们给芝诺卢恩矿石」、0.1.2「卢恩矿石几乎开采殆尽了」）完全不在 gold 中——"
            "gold 只覆盖了问句主语，漏掉了问句主体（村庄）。"
        ),
    ),
    "R288": dict(
        verdict="valid", confidence="high",
        suggested=None,
        assessment=(
            "小梅斯梅尔 131 块/871 次真实指代答案：103:1.0.0【标题卡】拉普拉斯康复中心，"
            "「所有出现应激障碍的患者都需要康复中心的治疗」；1918 亦为康复中心职员；她确为精神科医生。"
            "Mesmer 语料 0 次（英文缺失噪声）。附注（属题干质量问题而非 gold 缺陷）："
            "「怀疑神秘学家终将被淘汰」在语料中查无实据——含『小梅斯梅尔』且含『淘汰』的块数为 0。"
        ),
    ),
    "R292": dict(
        verdict="valid", confidence="high",
        suggested=None,
        assessment=(
            "伊索尔德（98 块/770 次）与海因里希（53 块/199 次）均真实指代答案且关系被语料直接证实："
            "106:21.0.1「一条弹道，两条人命。伊索尔德的子弹同时贯穿了霍夫曼和海因里希」，"
            "106:20.1.1 海因里希招募马库斯「通过这场筛选，加入我们吧」即重塑之手成员。"
            "Isolde / Heinrich 英文 0 次（英文缺失噪声）。"
        ),
    ),
    "R297": dict(
        verdict="defective", confidence="medium",
        suggested=["十二年"],
        assessment=(
            "twelve 与 12 years 语料 0 次；唯一有命中的『12岁』只有 2 块，且两块都与维尔汀无关："
            "anecdote__1904_埃里克角色故事:0.0.0「我本以为一位12岁的神秘学家，会更加温和」（说的是埃里克）、"
            "anecdote__1917_乘法轴上的一天:5.0.0「专门为12岁以下儿童设置的体验区」。"
            "维尔汀的年龄在语料中写作 103:5.0.0 校长「你入校的时候，岁数才刚满一个月……现在，你已经在学校里度过了"
            "快十二年」，是「快十二年」而非「12岁」——gold 与环境中的数字巧合，非真实表述。"
        ),
    ),
    "R298": dict(
        verdict="defective", confidence="medium",
        suggested=None,
        assessment=(
            "1966 在题目所指的 activity__11101_雷米特杯失窃案 中 0 次（该篇正文与标题都没有任何四位年份，"
            "只写「四年前被巴西队赢走」「数年前」）。8 块命中全部是别的语境：000:0.0.0「1966英国伦敦」（序章）、"
            "105:15.2.0、106:20.1.1、110:11.1.2（第六次「暴雨」）、13101:1.1.0「1966 摩卢旁卡火车站」、"
            "24101:3.2.0/3.2.1（奥尔德堡音乐节）、1916:5.0.2。1966 属现实世界知识（世界杯史）而非语料陈述。"
            "borderline：序章 000 与本案同为「1966 伦敦」同一时代，若接受跨篇章时代推断则可视为弱有效。"
        ),
    ),
    "R300": dict(
        verdict="valid", confidence="high",
        suggested=None,
        assessment=(
            "1966 与维尔汀同块出现于 mainline__000_此即明日:0.0.0——该块同时含「【标题卡】1966英国伦敦」与"
            "「您的名字是维尔汀？」，正是维尔汀首次登场处，gold 直接锚定答案，属有效。"
        ),
    ),
}

BORDERLINE = ["R001", "R011", "R073", "R142", "R297", "R298"]


def snippets_for(kw, chunks, limit_chunks=5, limit_snips=2, ctx=110):
    """Return (chunks, occurrences, snippets) for one keyword."""
    hits = []
    for cid, ch in chunks.items():
        blob = f"{ch.text}\n{ch.chapter_title}\n{ch.scene_title}\n{ch.part_title}"
        if kw in blob:
            hits.append((cid, blob))
    occ = sum(b.count(kw) for _, b in hits)
    snips = []
    if len(hits) <= limit_chunks:
        for cid, blob in hits[:limit_snips]:
            pos = blob.find(kw)
            s, e = max(0, pos - ctx), min(len(blob), pos + len(kw) + ctx)
            snips.append({"chunk": cid, "context": blob[s:e].replace("\n", " | ")})
    return len(hits), occ, snips


def main():
    cases = {c["qid"]: c for c in load_cases(TESTSET)}
    kb = P.load_kb(get_settings())
    chunks = kb.retriever.chunks

    out_cases = []
    for qid in QIDS:
        c = cases[qid]
        v = V[qid]
        kwinfo, parts = [], []
        for kw in c["keywords"]:
            n, occ, snips = snippets_for(kw, chunks)
            kwinfo.append({"keyword": kw, "chunks": n, "occurrences": occ, "snippets": snips})
            parts.append(f"{kw}={n}块/{occ}次")
        sug_counts = {}
        for kw in (v["suggested"] or []):
            n, occ, _ = snippets_for(kw, chunks)
            sug_counts[kw] = {"chunks": n, "occurrences": occ}
        out_cases.append({
            "qid": qid,
            "q": c["q"],
            "keywords": c["keywords"],
            "verdict": v["verdict"],
            "confidence": v["confidence"],
            "evidence": v["assessment"] + " || 语料计数: " + "; ".join(parts),
            "suggested_correct_gold": v["suggested"],
            "suggested_gold_counts": sug_counts,
            "keyword_detail": kwinfo,
            "borderline": qid in BORDERLINE,
        })

    n_def = sum(1 for c in out_cases if c["verdict"] == "defective")
    doc = {
        "kind": "gold_defect_audit",
        "audit": "_85",
        "testset": "data/knowledge/_audit/rag_testset_300_cn.json",
        "scope": "the 31 questions still missed by the current system on the 300cn set",
        "method": (
            "For each gold keyword, count chunks/occurrences over the official blob "
            "(text + chapter_title + scene_title + part_title); for keywords with <=5 chunks, "
            "print and judge ~110 chars of surrounding context. Verdicts hand-judged from that context."
        ),
        "policy": "只读审计：不修改 rag_testset_300_cn.json 或任何既有题集；本文件为唯一新增侧车文件。",
        "summary": {
            "n_audited": len(out_cases),
            "valid": len(out_cases) - n_def,
            "defective": n_def,
            "defective_qids": [c["qid"] for c in out_cases if c["verdict"] == "defective"],
            "valid_qids": [c["qid"] for c in out_cases if c["verdict"] == "valid"],
            "borderline_qids": BORDERLINE,
            "note": (
                "有效题中的英文 gold（Charlotte/Tooth Fairy/Doris/Ulrich/Zero/…）几乎全部 0 命中——"
                "语料为纯中文，英文原名不存在；这类 0 命中关键词是噪声而非独立缺陷，只要同题存在有效中文锚点即仍判有效。"
            ),
        },
        "cases": out_cases,
    }
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {OUT}")
    print(f"n_audited={doc['summary']['n_audited']} valid={doc['summary']['valid']} defective={n_def}")
    print("defective:", ", ".join(doc["summary"]["defective_qids"]))
    print("borderline:", ", ".join(BORDERLINE))


if __name__ == "__main__":
    main()
