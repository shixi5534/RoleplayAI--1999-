# -*- coding: utf-8 -*-
"""泛称 alias 焊点剥离(strip) + 组内非 canonical 写法归一(collapse)。零网络。

背景(第 19~20 会话实测的两个连环缺陷,见 handoff §4.11 / §9):
  ① **泛称 alias 把不同的人焊成一个节点**：模型/早期轮次把「姐姐 / 父亲 / 中尉 /
     将军 / 哨兵 / 议会 / 骰子 / 奇迹」这类**关系词、军衔、普通名词**当作 alias 声明。
     同一个泛称被两个不同宿主声明为 alias 时，DSU 就把两个宿主连成一个节点
     （实测：`中尉` ×47 处把 红弩箭 与 莫莉德尔 并成一人；`姐姐` ×9 处把
     娜娜之姐/玛丽安/莫莉德尔/霍夫曼 并成一人）。
  ② **组内非 canonical 写法落盘后 resolve=None**：`build_from_extractions` 里
     `aliases -= set(members)` 抹掉了成员拼写，存盘/载入时 alias_index 只能由
     `name+aliases` 重建 → 一个写法只要**既被当作 name 出现、又是别组的成员**，
     就永久查不到（实测 281 个写法受害，含 司辰/基金会/拉普拉斯科算中心 等高频名）。

本脚本按顺序做两件事，二者都是**保结构**的数据归一（不新增/不删除节点语义）：
  strip   : 对 WELD_DROPS 列出的 (宿主 name, alias) 对删掉那条 alias 声明。
            只删「泛称/军衔/关系词」这一侧，真名 alias（克拉拉·温格勒、保罗、
            阿德勒研究员…）一律保留 —— 处置口径：**宁可少一条可解析别名，
            不可把两个人并成一个节点**。
  collapse: strip 之后复算 DSU+canonical_pick，把每个**非 canonical 的成员拼写**
            在 name 侧改写为其 canonical（关系两端同步；同块撞名则合并实体；
            自环关系丢弃）。改写后每个组只剩 canonical 一个 name，其余写法
            只存在于 aliases 里 → 全部可解析。

用法：
    python _fix_alias_welds.py            # 只算不写：打印影响面
    python _fix_alias_welds.py --apply    # 写 cache + 同步 _agent_batch*.json
改后必须 rebuild 并重跑 6b 实测。任何重新生成 batch 的轮次结束后**都要再跑一次**
本脚本（它是确定性的后处理 pass，重跑幂等）。
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent / "src"))
from compendium_rag import pipeline as P                                    # noqa: E402
from compendium_rag.config import get_settings                              # noqa: E402
from compendium_rag.extract import (PROMPT_VERSION, ExtractionCache,        # noqa: E402
                                    cache_key, normalize, _norm_name)
from compendium_rag.graph_store import _merge_candidates, canonical_pick    # noqa: E402

# (宿主 name, 要删的 alias, 理由) —— 逐条人工裁定，理由即裁定记录。
WELD_DROPS = [
    # 关系词/称谓：同一词被多个不同人物的宿主声明
    ("娜娜之姐", "姐姐", " kinship"), ("玛丽安", "姐姐", "kinship"),
    ("莫莉德尔", "姐姐", "kinship"), ("霍夫曼", "姐姐", "kinship"),
    ("伊戈尔将军", "父亲", "kinship"), ("卡卡尼亚之父", "父亲", "kinship"),
    ("埃曼努埃尔", "父亲", "kinship"), ("托勒密", "父亲", "kinship"),
    ("77", "母亲", "kinship"), ("77（幻影", "母亲", "kinship"),
    ("佳琳娜夫人", "母亲", "kinship"), ("卡卡尼亚之母", "母亲", "kinship"),
    ("37之母", "妈妈", "kinship"), ("77", "妈妈", "kinship"),
    ("乌尔里希", "意识唤醒者", "称号属卡戎"),
    # 代词
    ("受苦者", "祂", "pronoun"), ("复苏之母", "祂", "pronoun"),
    ("阿尔卡纳", "祂", "pronoun"),
    ("人质", "她", "pronoun"), ("仪式术士", "她", "pronoun"),
    ("德洛丝医生", "她", "pronoun"),
    # 军衔/职务
    ("海军士兵Ⅱ", "哨兵", "rank"), ("玛丽安娜", "哨兵", "rank"),
    ("骑士团士兵", "哨兵", "rank"),
    ("斯捷尔诺娃", "上校", "rank"), ("红弩箭", "中尉", "rank"),
    ("格鲁托夫", "将军", "rank"), ("十四行诗", "队长", "rank"),
    ("红弩箭", "队长", "rank"), ("刻雷乌斯", "长官", "rank"),
    ("索姆将军", "长官", "rank"), ("伊里内伊", "委员", "rank"),
    ("佩德拉", "委员", "rank"), ("埃里希", "连长", "rank"),
    ("威利", "连长", "rank"), ("帕拉维扬", "警官", "rank"),
    ("梅蕾尔", "警官", "rank"), ("玛丽安娜", "狙击手", "rank"),
    ("罗尔夫", "狙击手", "rank"), ("淑女格蕾丝", "使徒", "rank"),
    ("阿尼姆斯", "使徒", "rank"),
    # 姓氏单独成 alias：同姓不同人
    ("破译员Ⅲ", "道金斯", "surname"), ("破译员Ⅳ", "道金斯", "surname"),
    ("邓肯先生", "卡森先生", "surname"),
    # 普通名词/物件词：跨实体焊点
    ("箱子", "小船", "箱子≠瓶中船"),
    ("哑谜", "人类", "泛称概念"),
    ("Su-01ве", "红色38", "红38 是扫帚的诨名"),
    ("扫帚", "红色38", "red38"), ("飞行扫帚", "红色38", "red38"),
    ("半架纺车", "纺车", "common"), ("卡邦克鲁", "魔精", "common"),
    ("恶灵魔精", "魔精", "common"), ("遗址城", "迷宫", "common"),
    ("狮鹫军", "叛军", "common"), ("帝国议会", "议会", "common"),
    ("科马拉议会", "议会", "common"), ("弗里莱", "祭品", "common"),
    ("科考队员", "祭品", "common"), ("潘多拉之盒", "奇迹", "common"),
    ("黑色立方体", "奇迹", "common"),
    ("IDM计算机", "机器", "common"), ("模型", "机器", "common"),
    ("咒文", "术式", "common"), ("咒语", "术式", "common"),
    ("圣洛夫基金会", "总部", "org≠building"),
    ("圣洛夫基金会", "委员会", "org≠committee"),
    ("奥利图欧基地", "基地", "common"), ("芝诺基地", "基地", "common"),
    ("格鲁托夫营地", "营帐", "common"), ("骑兵军塞契", "营帐", "common"),
    ("阿莱夫", "梅林先生", "epithet"),

    # ── 第 20 会话二次裁定 A 类：alias 与宿主**类型不同**的 46 组焊点 ──
    # 判据（用户口径）：以**该角色在原文里的关系**为准——若两条写法各自与第三方
    # 发生不同关系，即为两物；灰机wiki(重返未来1999 中文维基)可查则以维基为准。
    ("转念即至", "传送软盘", "咒语≠承载它的软盘"),
    ("剃刀特别行动分队", "剃刀", "队长与队伍两物(且互为关系端点)"),
    ("纪念碑", "墓碑", "111 的纪念碑≠11101 梅兰妮父亲的墓碑"),
    ("避难小屋", "小屋", "医生安顿病患处≠湖畔废弃屋(罗德里戈藏身)"),
    ("白朗姆", "小船", "泛称；109 重塑所赠之船另有其船"),
    ("战马", "小马", "111 的风车战马≠1918 多萝西娅想要的小马"),
    ("托勒密步兵班", "托勒密", "编制≠军官本人"),
    ("伊索尔德", "托斯卡", "歌剧《托斯卡》(灰机:伊索尔德词条无此别名)"),
    ("星锑", "摇滚乐", "概念≠人(灰机:星锑词条=热爱摇滚的角色)"),
    ("重塑之手", "敌人", "泛称"),
    ("重塑之手", "重塑士兵", "组织≠其士兵"),
    ("飞行巫师中队", "新兵", "编制≠补充兵员"),
    ("重塑·门徒", "暴徒", "泛称"),
    ("迪马", "民兵", "个人≠守城之众"),
    ("洛伦兹研究所", "洛伦兹", "裸名歧义(研究所/蝴蝶/物理学家)"),
    ("玛丽安娜", "石像鬼", "灰机:石像鬼类尤提姆=**族裔**非人名"),
    ("新世界", "美国", "隐喻≠地点"),
    ("小刀\"麦高芬", "莱茵黄金", "狗≠腹中之金"),
    ("门徒", "重塑·门徒", "泛称追随者"),
    ("蛾子", "飞蛾", "110 被碾杀之蛾≠113 无名者所驱之蛾"),
    ("玛尔纱", "骑士", "身份理想≠人名(111:我过去是骑士团成员)"),
    ("天使娜娜", "魅魔", "灰机:魅魔=族裔表述(『她是一名魅魔』)"),
    ("伊里内伊", "鹰派", "派别≠个人"),
    # ── 第 20 会话二次裁定 B 类：**反证法**——alias 与宿主在同一条关系里
    #    互为两端，必是两个实体（用户口径「以关系为标准」的最硬证据）──
    ("星锑", "唱片", "星锑-[持有]->唱片，两物"),
    ("唱片", "星锑", "同上（反向声明）"),
    ("无名者", "淑女格蕾丝", "113:7 无名者与淑女格蕾丝对话(劝降/拒绝)"),
    ("乌尔里希", "磁流体", "110:3 乌尔里希-[指令]->磁流体"),
    ("芝诺", "骑兵军", "112:8 骑兵军-[隶属]->芝诺"),
    ("森林哨兵", "士兵？", "111:1 哨兵盘查『士兵？』"),
    ("瑞安侬", "小瑞安侬", "113:24 为母关系，两代人"),
    # ── 第 20 会话二次裁定 C 类：灰机wiki 可查且与声明矛盾 ──
    ("洛伦兹蝴蝶", "玛格丽特", "灰机:洛伦兹蝴蝶有独立角色词条，无玛格丽特关联"),
    ("梅蕾尔", "乌鸫", "乌鸫=鸟，非人名"),
    ("梅蕾尔", "逃兵", "泛称身份词"),
    ("卡戎", "守墓人", "职务泛称"),
    ("拉蒂斯", "修士", "职务泛称"),
    ("拉蒂斯", "教士", "职务泛称"),
    ("维也纳警卫", "卫兵", "泛称"),
    ("莱比", "伙计", "称呼语"),

    # ── 第 22 会话：`_audit_generic_alias.py` 全库体检（7033 实体 / 29967 边）残留的
    #    **裸泛称 alias**。这类词的危险不在「多一条别名」，而在**链指污染**：
    #    `女士` 挂在 卡卡尼亚 上 ⇒ 任何含「女士」的查询都把 deg=439 的整条邻域当种子拉进
    #    重排，等于给全库 911 个块发通行证。以下 17 条逐条实测：
    #    全部**无任何块以该词作 name 声明**（`_audit_alias_decl_range.py` 打印 name侧块=0），
    #    故剥离不会造成 §4.11 的「成员抹除」——被抹掉的本来就不该是实体handle。
    ("卡卡尼亚", "女士", "裸称谓 语料DF=911"),
    ("卡卡尼亚", "医生", "裸职务 语料DF=228"),
    ("卡卡尼亚", "社会活动家", "身份泛称"),
    ("卡卡尼亚", "盲眼医生", "描述性称号(且所指另有其人=德洛丝医生)"),
    ("卡卡尼亚", "盲眼女士", "描述性称号(同上)"),
    ("卡卡尼亚", "荣军院的医生", "描述性称号(同上)"),
    ("星锑", "船长", "裸职务 语料DF=118"),
    ("伊戈尔", "将军", "裸军衔 语料DF=103"),
    ("苏菲亚", "祭司", "裸职务"),
    ("命名日", "职员", "裸职务 语料DF=198(事件节点挂人职称)"),
    ("莫莉德尔", "中尉", "裸军衔(同词已为 红弩箭 剥离过)"),
    ("布劳恩少校", "少校", "裸军衔"),
    ("娜斯佳", "护士", "裸职务"),
    ("希施费尔德上校", "上校", "裸军衔"),
    ("希施费尔德", "上校", "裸军衔(同词跨两宿主=DSU 焊接来源)"),
    ("穆伦贝格先生", "老师", "裸称谓 语料DF=106"),
    ("水蚺", "蛇", "物种裸名 语料DF=176"),
    ("监狱守卫", "同志", "裸称谓 语料DF=131"),
]
# ── 第 20 会话二次裁定：**明确保留**的同人/同物跨类型焊点(仅登记，不剥离) ──
# 保留依据均为原文同位语或灰机词条实证，写在这里是为了让「为什么不删」可查。
KEPT_MERGES = [
    ("《UTTU》杂志", "UTTU", "同一本杂志(灰机:乌特图杂志)"),
    ("保罗", "卡戎", "111:卡戎=收殓者，真名保罗"),
    ("阿派朗", "无限定者", "105:19 原文同位语『阿派朗，无限定者，万物的本源』"),
    ("本能现实主义运动", "本能现实主义派", "109:15『参加本能现实主义派的运动』"),
    ("白朗姆", "瓶中船", "灰机:白朗姆=瓶中船成精的角色；原文自陈『被放进瓶子里』"),
    ("无线电小姐", "收音机", "灰机:无线电小姐是角色(神秘学家)，105 被审问的收音机即她"),
    ("37", "赫尔墨斯之星", "唯一命名块 desc 即『37的称号』"),
    ("阿尔卡纳", "复苏之母", "110:20 关系『等同』，原文『那是……阿尔卡纳』"),
    ("复苏之母", "引导之人", "111:9 原文同位语『复苏之母，引导之人……』"),
    # ── 第 22 会话：全库体检的另 2 条「高频且不含宿主名」命中，实测**不是**焊点，明确保留 ──
    ("维尔汀", "司辰", "专名化职衔：全库 **224 块**均以 `司辰` 指她本人，且无任何块把 `司辰`"
                       "当独立 name 声明（`_audit_alias_decl_range.py` name侧块=0）→ 剥即抹除"),
    ("科算中心", "拉普拉斯", "机构短名：`拉普拉斯` 无独立 name 落点，语料中该词即指拉普拉斯科算中心"),
]
# ── **无法裁定**：灰机无对应词条、语料内证据互斥 → 按「宁可分建不可并错」剥离并登记 ──
UNDECIDED = [
    ("苏菲亚", "传道者", "灰机仅有地名『传教者之厅』；108 传道者赠礼 vs 105 除错师苏菲亚，无从外部证实"),
    ("乌尔里希", "意识唤醒者", "107 意识唤醒者=原始意识/族裔概念，与 110 采样者乌尔里希关系不明"),
    ("卡戎", "意识唤醒者", "112:3『一名意识唤醒者』被俘者是否即卡戎，语料未再指认"),
    ("意识唤醒者", "卡戎", "同上（反向声明）"),
]
UNDROP_MAP = defaultdict(set)
for _h, _a, _why in UNDECIDED:
    UNDROP_MAP[_h].add(_a)
DROP_MAP = defaultdict(set)
# 剥离必须**双向**登记：strip 以宿主为键，若只记 (宿主, alias)，
# 反向声明块（name=alias, aliases=[宿主]）不会被剥掉，DSU 依旧把两者焊在一起，
# collapse 便把「淑女格蕾丝」这类成员写法并到对方组，再由 name 保留行还原成 alias。
for _h, _a, _why in WELD_DROPS + UNDECIDED:      # 未裁定者按保守口径一并剥离
    DROP_MAP[_h].add(_a)
    DROP_MAP[_a].add(_h)

# ── **双向剥离后仍焊接**：桥不在「宿主→alias」声明上，strip 无从下手（硬拆即抹除写法）
#    → 如实登记，交人工/重抽取处理 ──
RESIDUAL_WELDS = [
    ("传道者", "苏菲亚",
     "桥在 graph_store._merge_candidates ②「前缀全名」规则：限定名『传道者·苏菲亚』以裸名"
     "『传道者』为前缀 → 被并进来。**该规则会把任何『职位·人名』限定名焊回裸职位名**。"
     "第 21 会话语料实测：裸说话人标签 `**传道者**：` 出现 **0** 次，"
     "`**传道者·苏菲亚**：` 39 次，『传道者之厅』(地点) 18 次 → 现任职传道者即苏菲亚，"
     "合并方向可接受；但同词在语料里**也是职位**（『下一位传道者是37』『全体传道者』"
     "『年轻的传道者』），故职位集体语义会一起落到她身上 → 保留登记，不硬拆"),
    ("无名者", "淑女格蕾丝",
     "第 21 会话复判：桥**不是**共享 alias，而是**直接声明** `无名者 ← 淑女格蕾丝` / "
     "`无名者 ← 格蕾丝`（`淑女格蕾丝`/`格蕾丝` 全语料**从未**作为 name 出现，"
     "剥掉即 §4.11 成员抹除）。互斥证据：mainline__113 Part 18『黑羊群之歌』2 块里 "
     "`**无名者**：` 与 `**淑女格蕾丝**：` 是**同台对话的两个说话人**（11×/8×、14×/8×），"
     "按判据①应分建；但另 8 块单侧声明同人 → 语料自身矛盾 + 『无名者』本身是泛称角色标签，"
     "无法裁定 → 保守登记，不硬拆"),
    ("科马拉之雨", "骰子",
     "非缺陷：二者同为 canonical『巴比伦之骰』的 alias(4 块 desc 皆『…之骰』)，同节点是正确归并"),
]

# 已**改数据修好**的焊点（不再靠剥离）：本遍反向断言它们必须**保持分开**，
# 一旦重新焊接即判 defect —— 防止后续 rebuild/并集把倒置 alias 带回来。
FIXED_WELDS = [
    ("重塑·门徒Ⅰ", "重塑之手",
     "原块 mainline__105_洞穴的囚徒:19.0.1 把组织名写成成员『重塑·门徒Ⅰ』的 alias 且类型错标为组织；"
     "已由 _fix_disciple_blocks.py 改为 4 个独立 角色 节点 + 独立『重塑之手』(组织) + 隶属于 关系"),
]

# 纯数字 alias（附录 015 的「数字 ID 别名」，任务 #13）：`37`/`42`/`29` 这类
# 编号既被当作独立实体的 name，又被别的宿主当 alias 声明 → 把两个不相干的
# 节点焊在一起（实测 `赫尔墨斯之星` 与 `37` 并成一人）。编号本身仍是 name 节点，
# 删的只是「谁都能认领这个号」的 alias 声明侧。
RE_DIGIT_ID = re.compile(r"\d{1,4}")

# ── 第 22 会话新增：**可证明的裸泛称**白名单，用于放宽下面的二次落盘守卫 ──
# 守卫的原意：collapse=0 而 strip>0 说明输入已是本遍产物，此时被 alias 承载的写法
# **多半是上一遍 name 侧改写留下的真名**（如 德洛丝/玛尔塔/兀尔德），再剥即 §4.11 抹除。
# 但「多半」不等于「全部」：本轮新剥的 17 个词是**普通名词**，判据三条同时成立才准入 ——
#   ① 全库 3676 个 cache 文件中**无任何块以该词作 entity name**（`_audit_alias_decl_range.py` 实测）；
#   ② 灰机 canon（characters/npcs/name_table 共 901 条）**无该词条** → 它不是专名；
#   ③ 它在全语料里以普通名词身份高频出现（DF 见各行括注）。
# 白名单只放行「本轮新增的泛称剥离」，真名类写法（兀尔德/德洛丝/玛尔塔…）一律不在列，
# 因此守卫对原有风险**没有减弱**；任一被剥词不在白名单，照旧拒绝落盘。
SAFE_NAMELESS_GENERIC = {
    "女士", "医生", "社会活动家", "盲眼医生", "盲眼女士", "荣军院的医生",
    "船长", "将军", "祭司", "职员", "中尉", "少校", "护士", "上校", "老师",
    "蛇", "同志",
}


def strip_aliases(obj: dict, removed: set, skipped: set | None = None) -> int:
    """删掉 WELD_DROPS 列出的 alias 声明 + 纯数字 alias，返回删除条数。

    removed 收集本次真正被删掉的 alias **写法**（归一后），供守卫复核。
    skipped 非 None 时进入**增量模式**：只删白名单内的裸泛称与数字编号，其余
    命中 DROP_MAP 的写法**跳过并登记**——增量遍面对的 cache 已 collapse 过，
    那些写法是第 20 会话「name 侧回填 alias」留下的唯一落点，再剥即 §4.11 抹除。
    """
    n = 0
    for e in obj.get("entities") or []:
        al = e.get("aliases") or []
        nm = _norm_name(e.get("name", ""))
        if not al:
            continue
        bad = DROP_MAP.get(nm, set())

        def doomed(a: str) -> bool:
            if a not in bad and _norm_name(a) not in bad:
                return False                       # 不在裁定表里，留
            if RE_DIGIT_ID.fullmatch(_norm_name(a)):
                return True                        # 数字编号认领侧，任何遍都照剥
            if skipped is None or _norm_name(a) in SAFE_NAMELESS_GENERIC:
                return True
            skipped.add(_norm_name(a))             # 增量遍：真名写法不动
            return False

        keep = [a for a in al if not doomed(a)]
        n += len(al) - len(keep)
        for a in al:
            if a not in keep:
                removed.add(_norm_name(a))
        e["aliases"] = keep
    return n



def canon_map(pairs: list) -> dict:
    """复算 rebuild 的 ①收集 ②归一 两步，返回 {非 canonical 写法: canonical}。"""
    obs: dict[str, dict] = {}
    for c, _key, raw in pairs:
        ex = normalize(c, raw)
        if ex is None or not getattr(ex, "ok", True):
            continue
        if not ex.entities and not ex.relations:
            continue
        for e in ex.entities:
            if not e.name:
                continue
            o = obs.setdefault(e.name, {"t": 0, "al": set()})
            o["t"] += 1
            o["al"].update(a for a in e.aliases if a and a != e.name)
        for r in ex.relations:
            for x in (r.src, r.dst):
                obs.setdefault(x, {"t": 0, "al": set()})
    names = sorted(obs)
    dsu = _merge_candidates(names, [(n, a) for n, o in obs.items() for a in o["al"]])
    groups: dict[str, list] = defaultdict(list)
    for n in names:
        groups[dsu.find(n)].append(n)
    m: dict[str, str] = {}
    for mem in groups.values():
        if len(mem) < 2:
            continue
        canon = canonical_pick(mem, {x: obs[x]["t"] for x in mem})
        m.update({x: canon for x in mem if x != canon})
    return m


def collapse_block(obj: dict, m: dict) -> tuple[int, int]:
    """name 侧成员写法 → canonical；同块撞名合并；自环关系丢弃。

    查表前先过一遍 ``_norm_name``：raw 里写作 ``“哨兵”``/``77（幻影）`` 这类带引号
    括号的写法，归一化层会剥成 ``哨兵``/``77（幻影``，映射表存的是剥后的键。
    直接落 canonical 与 normalize 的结果一致，且让 raw 记录自身也可解析。
    """
    ren = 0
    merged: dict[str, dict] = {}
    order: list[str] = []
    for e in obj.get("entities") or []:
        old = e.get("name", "")
        cn = m.get(_norm_name(old), _norm_name(old))
        if cn != old:
            ren += 1
        e["name"] = cn
        al = [a for a in (e.get("aliases") or []) if a and a != cn]
        # 改写掉的 name 侧写法**必须留在 aliases 里**：alias_index 在存盘/载入时
        # 只由 name+aliases 重建(graph_store.py:343-345)，不登记就永久 resolve=None
        # ——与第 19 会话的「成员抹除」缺陷同源（实测 天使娜娜/淑女格蕾丝 被改写后
        # 既不是 name 也不是 alias，全库查不到）。
        if cn != old and old not in al:
            al.append(old)
        cur = merged.get(cn)
        if cur is None:
            e["aliases"] = al
            merged[cn] = e
            order.append(cn)
            continue
        for a in al:
            if a not in cur["aliases"]:
                cur["aliases"].append(a)
        d = e.get("desc") or ""
        if d and d not in (cur.get("desc") or ""):
            cur["desc"] = (cur.get("desc") or "") + ("；" + d if cur.get("desc") else d)
    obj["entities"] = [merged[k] for k in order]

    dropped = 0
    rels = []
    for r in obj.get("relations") or []:
        s = m.get(_norm_name(r.get("src", "")), _norm_name(r.get("src", "")))
        t = m.get(_norm_name(r.get("dst", "")), _norm_name(r.get("dst", "")))
        if s == t:
            dropped += 1
            continue
        if s != r.get("src") or t != r.get("dst"):
            ren += 1
        r["src"], r["dst"] = s, t
        rels.append(r)
    obj["relations"] = rels
    return ren, dropped


def main() -> int:
    apply = "--apply" in sys.argv
    s = get_settings()
    cache = ExtractionCache(s.cache_dir)
    pairs: list[tuple] = []
    for c in P.load_chunks(s):
        key = cache_key(c, s.llm_model, PROMPT_VERSION)
        raw = cache.get_raw(key)
        if raw is not None:
            pairs.append((c, key, raw))

    # ── ⓪ 先判本遍是「首遍」还是「增量遍」：strip 前复算一次 collapse 映射，
    #      非 canonical 写法为 0 ⇒ cache 已是本流程产物 ⇒ 进入增量模式 ──
    pre_resid = canon_map(pairs)
    skipped: set | None = None if pre_resid else set()
    mode = (f"首遍（collapse 待做 {len(pre_resid)} 个写法）" if pre_resid
            else "增量遍（cache 已收敛，只剥白名单裸泛称 + 数字编号）")
    print(f"模式：{mode}")

    # ── ① strip 泛称/数字 alias ──
    removed: set = set()
    n_strip = sum(strip_aliases(r, removed, skipped) for _, _, r in pairs)
    # 全库 name 侧落点（strip 前统计）：被剥写法若在别处是 name，剥它不会造成抹除；
    # 若**只**活在 alias 里且不是白名单裸泛称，就是 §4.11 的成员抹除风险。
    name_set = {_norm_name(e.get("name", "")) for _, _, r in pairs
                for e in (r.get("entities") or [])}
    # 纯数字编号按 RE_DIGIT_ID 单列（它们本身就是 name 节点，删的只是认领侧）
    strayed = {r for r in removed
               if r not in SAFE_NAMELESS_GENERIC and not RE_DIGIT_ID.fullmatch(r)}
    erased = {r for r in removed if r not in name_set}

    # ── ② collapse：复算 canonical 并把成员写法并到 canonical，迭代到不动点
    #    (改写会改变各写法的观察次数 → canonical 归属可能再变，故需复算) ──
    maps: list[dict] = []
    n_collapse = n_selfloop = n_merged = 0
    resid = canon_map(pairs)
    while resid and len(maps) < 6:
        maps.append(resid)
        for c, k, raw in pairs:
            before_e = len(raw.get("entities") or [])
            ren, drop = collapse_block(raw, resid)
            n_collapse += ren
            n_selfloop += drop
            n_merged += before_e - len(raw.get("entities") or [])
        resid = canon_map(pairs)
    if apply and n_collapse == 0 and n_strip > 0:
        # 二次落盘守卫：首轮必然 strip>0 且 collapse>0；collapse 归零而 strip 仍>0
        # 说明输入的已是**本遍产物**——此时被 alias 承载的写法多为 name 侧改写产物，
        # 再剥一次就是 §4.11「成员抹除」（resolve 永久 None）。
        # 唯一例外：被剥写法**全部**落在 SAFE_NAMELESS_GENERIC 白名单内（三条判据见该常量）。
        if not strayed:
            print(f"守卫：collapse 0 轮但 strip 的 {len(removed)} 个写法**全部**在裸泛称白名单内，"
                  f"且其中 {len(erased)} 个在全库无 name 落点（普通名词，剥除即取消错误链指入口）"
                  f"→ 放行落盘；增量遍跳过 {len(skipped or ())} 个无 name 落点的真名写法 "
                  f"{sorted(skipped or ())[:12]}")
        else:
            print(f"!! 拒绝落盘：strip {n_strip} 但 collapse 0 轮 —— 输入的 cache 已是本遍产物，"
                  f"请先从 *_backup_pre_welds 还原再跑")
            print(f"   白名单外的被剥写法 {len(strayed)} 个：{sorted(strayed)[:12]}")
            print(f"   其中全库无 name 落点（真·抹除风险）{len(erased & strayed)} 个："
                  f"{sorted(erased & strayed)[:12]}")
            return 2

    if apply:
        for c, k, raw in pairs:
            cache.put_raw(k, raw)

    # ── ③ 同步 _agent_batch*.json（保持 batch==cache，否则 6b 会把这些块判成
    #        「已覆盖草稿块」而跳过实测 → 假绿）──
    n_files = 0
    for p in sorted(ROOT.glob("_agent_batch*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        changed = False
        for blk in data.values():
            if not isinstance(blk, dict):
                continue
            if strip_aliases(blk, removed, skipped):
                changed = True
            for mp in maps:
                if collapse_block(blk, mp)[0]:
                    changed = True
        if changed:
            n_files += 1
            if apply:
                p.write_text(json.dumps(data, ensure_ascii=False, indent=1),
                             encoding="utf-8")

    print(f"{'[APPLY] 已写 cache' if apply else '[DRY-RUN] 未写盘'}"
          f"｜块数 {len(pairs)}｜strip 删泛称/数字 alias {n_strip} 条"
          f"｜collapse 迭代 {len(maps)} 轮，改写 name+端点 {n_collapse} 处"
          f"｜同块撞名合并 {n_merged} 条｜自环关系丢弃 {n_selfloop} 条"
          f"｜batch 文件改动 {n_files} 个")
    print(f"剥离写法明细 {len(removed)} 个：白名单外 {len(strayed)} 个"
          f"｜全库无 name 落点 {len(erased)} 个 {sorted(erased)[:20]}")
    print(f"复核：collapse 后剩余非 canonical 写法 {len(resid)} 个（应为 0）"
          + ("" if not resid else f" 例: {list(resid.items())[:5]}"))
    # ── ④ 全量复核：裁定剥离的 (宿主, alias) 落盘后是否**真的**不再同组 ──
    #    必须在 collapse 之后按最终 cache 内容复算，且走 _merge_candidates 同一套规则
    #    （含 ② 前缀全名），否则测的不是 alias_index 的真实行为。
    #    ⚠ 直接扫 cache 文件会得到假绿：外层是 {__cache_format__, raw:{…}}，
    #      对包装层取 `entities` 恒为空 → 「0 条违例」是空输入上的真命题。
    obs_f: dict[str, int] = defaultdict(int)
    ed_f = [(e["name"], a)
            for _, _, raw in pairs for e in raw.get("entities") or []
            if e.get("name") for a in (e.get("aliases") or [])]
    for h, a in ed_f:
        obs_f.setdefault(h, 0)
        obs_f.setdefault(a, 0)
    dsu_f = _merge_candidates(sorted(obs_f), ed_f)
    known = {(h, a) for h, a, _ in RESIDUAL_WELDS} | {(a, h) for h, a, _ in RESIDUAL_WELDS}
    surv = [(h, a) for h, a, _ in WELD_DROPS + UNDECIDED
            if dsu_f.find(h) == dsu_f.find(a)]
    defect = [p for p in surv if p not in known]
    for h, a, _ in RESIDUAL_WELDS:
        if dsu_f.find(h) != dsu_f.find(a):
            defect.append((h, a))            # 登记的残留其实已分开 = 台账过期
    for h, a, _ in FIXED_WELDS:
        if dsu_f.find(h) == dsu_f.find(a):
            defect.append((h, a))            # 已修好的写法重新焊接 = 回归
    print(f"复核：裁定 {len(WELD_DROPS) + len(UNDECIDED)} 对 → 仍同组 {len(surv)} 对"
          f"（已登记残留 {len(surv) - len(defect)}）｜**未登记违例 {len(defect)}** "
          + (f" 例 {defect[:6]}" if defect else ""))

    lines = ["# alias 焊点裁定台账（由 _fix_alias_welds.py 打印，判据见 handoff §4.11/§10）",
             "# 口径：以**角色在原文中的关系**为准；可查灰机wiki(重返未来1999中文维基)者以维基为准；",
             "#       两者都不能裁定时 → 保守剥离并登记于此，等待人工复核。", "",
             f"## 剥离(WELD_DROPS) {len(WELD_DROPS)} 条"]
    lines += [f"- {h} ← {a}　[{w}]" for h, a, w in WELD_DROPS]
    lines += ["", f"## 保留(同人/同物跨类型焊点) {len(KEPT_MERGES)} 条"]
    lines += [f"- {h} ← {a}　[{w}]" for h, a, w in KEPT_MERGES]
    lines += ["", f"## 待裁定(已按保守口径剥离，需人工确认是否同人) {len(UNDECIDED)} 条"]
    lines += [f"- {h} ← {a}　[{w}]" for h, a, w in UNDECIDED]
    lines += ["", f"## 双向剥离后仍焊接(桥不在 alias 声明上，登记待裁定，不硬拆) {len(RESIDUAL_WELDS)} 条"]
    lines += [f"- {h} ↔ {a}　[{w}]" for h, a, w in RESIDUAL_WELDS]
    lines += ["", f"## 已改数据修好(反向断言必须保持分开) {len(FIXED_WELDS)} 条"]
    lines += [f"- {h} ↔ {a}　[{w}]" for h, a, w in FIXED_WELDS]
    lines += ["", f"## 复核结论：裁定 {len(WELD_DROPS) + len(UNDECIDED)} 对，仍同组 {len(surv)} 对，"
                  f"未登记违例 {len(defect)} 对"]
    lines += [f"- !! {h} ↔ {a}" for h, a in defect]
    (ROOT / "_weld_adjudication.txt").write_text("\n".join(lines) + "\n",
                                                 encoding="utf-8")
    print(f"裁定台账 → _weld_adjudication.txt"
          f"（剥离 {len(WELD_DROPS)}｜保留 {len(KEPT_MERGES)}｜待裁定 {len(UNDECIDED)}"
          f"｜已登记残留 {len(RESIDUAL_WELDS)}）")
    return 1 if defect else 0


if __name__ == "__main__":
    raise SystemExit(main())
