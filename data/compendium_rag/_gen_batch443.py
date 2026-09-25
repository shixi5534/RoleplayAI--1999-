# -*- coding: utf-8 -*-
"""生成 _agent_batch443.json（band 1.9「去往新世界」第 4 轮：
011_Z + 010_X，各 4 块（含 2 头卡），共 8 块）。抽完本 band 全清零。

探针：_cands443.txt → _probe_union_alias 全 EXISTS；_sim_landing **需改写 0 个**（全部复用既有节点）。
命名要点：
  * 全部复用既有节点：Z/X/维尔汀/圣洛夫基金会/平衡伞/科算中心/暴雨/露西/
    暴雨小组组长乌尔里希/戈德堡装置/充电王座；
  * `Z女士` 已是 Z 的 alias → 在其出现的两块（011 0.1.0 / 1.1.0 选项行）都声明 aliases；
  * `乌尔里希` 是 `破译组长` 的 alias（污染组）→ 不作 alias，直接用限定名 `暴雨小组组长乌尔里希`；
  * `司辰`（维尔汀他处 name）→ 只写 `维尔汀`，不作 alias；
  * `基金会`→`圣洛夫基金会`；`意识唤醒者`(§3.3 污染泛称)/`神秘学家`/`研究员`/`调查员`/`政治家`(泛称) 均不建节点，只在 evidence/选项行出现；`委员会`(泛称)不建。
  * 头卡块 → 留空。
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
N = {
    "Z": "Z", "X": "X", "文": "维尔汀", "基": "圣洛夫基金会", "伞": "平衡伞",
    "科": "科算中心", "暴": "暴雨", "露": "露西", "乌": "暴雨小组组长乌尔里希",
    "戈": "戈德堡装置", "座": "充电王座",
}


def E(key, type_, desc, aliases=None):
    al = list(aliases or [])
    name = N[key]
    assert name not in al, f"别名等于本体名 {name}"
    return {"name": name, "type": type_, "aliases": al, "desc": desc}


def R(sk, rel, dk, ev, conf=0.95):
    return {"src": N[sk], "relation": rel, "dst": N[dk], "evidence": ev, "confidence": conf}


EMPTY = {"entities": [], "relations": []}
B = {}

# ─────────────────────────── 011 Z ───────────────────────────
B["1397d00107dc52a4165fba44"] = EMPTY  # 011 0.0.0 头卡
B["01b6a601bd3d0dee9a6e5adf"] = EMPTY  # 011 1.0.0 头卡

B["42c48fcc010da8033055cbbb"] = {  # 011 0.1.0 Z 表彰维尔汀·平衡伞与科算中心合作
    "entities": [
        E("Z", "角色", "代表基金会表彰维尔汀的上司", ["Z女士"]),
        E("文", "角色", "受表彰、即将进入休假的箱主"),
        E("基", "组织", "赞赏维尔汀贡献的基金会"),
        E("伞", "物品", "可免疫暴雨的伟大发明"),
        E("科", "组织", "与基金会商议合作的科算中心"),
        E("暴", "概念", "外出须免疫的暴雨"),
    ],
    "relations": [
        R("Z", "表彰", "文", "我代表基金会前来表彰你"),
        R("基", "赞赏", "文", "基金会对你这次的贡献大为赞赏"),
        R("Z", "代表", "基", "我代表基金会前来表彰你"),
        R("基", "合作", "科", "现在正就平衡伞研究项目与科算中心商议合作"),
        R("伞", "免疫", "暴", "堪堪应用了平衡伞去免疫暴雨"),
        R("文", "感谢", "Z", "这也多亏了您的协助，Z女士"),
        R("Z", "劝休", "文", "你可以休息一会，和新认识的朋友聊聊"),
    ],
}

B["b953e1a42f772042477d4f65"] = {  # 011 1.1.0 Z 论新阶段与暴雨成因
    "entities": [
        E("Z", "角色", "与维尔汀谈论新阶段的上司", ["Z女士"]),
        E("文", "角色", "被劝休假的箱主"),
        E("基", "组织", "已着手下一步的基金会"),
        E("伞", "物品", "免疫暴雨外出的平衡伞"),
        E("科", "组织", "商议合作的科算中心"),
        E("暴", "概念", "成因仍待解开的暴雨"),
    ],
    "relations": [
        R("Z", "问候", "文", "还有什么事么，维尔汀"),
        R("文", "感谢", "Z", "这也多亏了您的协助，Z女士"),
        R("基", "合作", "科", "现在正就平衡伞研究项目与科算中心商议合作"),
        R("伞", "免疫", "暴", "堪堪应用了平衡伞去免疫暴雨"),
        R("Z", "劝休", "文", "在前往新时代前，你可以休息一会"),
        R("Z", "探究", "暴", "想要真正了解暴雨的成因"),
        R("Z", "勉励", "文", "共勉，维尔汀"),
    ],
}

# ─────────────────────────── 010 X ───────────────────────────
B["97355d2c91047c28bde40c5a"] = EMPTY  # 010 0.0.0 头卡
B["1f62691e9d2ddfd41ac97359"] = EMPTY  # 010 1.0.0 头卡

B["c467a88f3f7416186232f4a8"] = {  # 010 0.1.0 X 的戈德堡装置与科算中心近况
    "entities": [
        E("X", "角色", "岛上设计连锁装置的奇才"),
        E("文", "角色", "偶遇闲谈的箱主"),
        E("戈", "物品", "X新设的连锁投石装置"),
        E("科", "组织", "暂无主事的科算中心"),
        E("露", "角色", "离去后声望犹在的研究者露西"),
        E("座", "物品", "无人愿接管的充电王座"),
        E("乌", "角色", "仍在楼前静坐的绝食者"),
    ],
    "relations": [
        R("X", "问候", "文", "嗨，维尔汀，在这见面可真巧"),
        R("X", "设计", "戈", "我正在设计一个新的戈德堡装置"),
        R("X", "谈起", "科", "比如科算中心现在乱成一团"),
        R("X", "称赞", "露", "露西走前的欢送仪式充分展示了她的人望"),
        R("X", "调侃", "座", "暂时没有人想接管那把充电王座"),
        R("X", "转述", "乌", "它还在委员会大楼前坐着呢"),
    ],
}

B["a391cdfa367dd52745bdc9dd"] = {  # 010 1.1.0 X 再论露西后继与乌尔里希绝食
    "entities": [
        E("X", "角色", "再次招呼来客的装置奇才"),
        E("文", "角色", "再度来访闲谈的箱主"),
        E("露", "角色", "声望仍被称道的研究者露西"),
        E("座", "物品", "无人愿接管的充电王座"),
        E("乌", "角色", "坚持绝食静坐的乌尔里希"),
    ],
    "relations": [
        R("X", "招呼", "文", "欢迎再次光临，这次想聊些什么"),
        R("X", "称赞", "露", "露西走前的欢送仪式充分展示了她的人望"),
        R("X", "调侃", "座", "暂时没有人想接管那把充电王座"),
        R("X", "转述", "乌", "它还在委员会大楼前坐着呢"),
    ],
}

# ── 体检 ──
REL_RE = __import__("re").compile(r"^[一-鿿]{2,6}$")
keys = [json.loads(l)["key"]
        for l in (ROOT / "_dump443.txt").read_text(encoding="utf-8-sig").splitlines() if l.strip()]
assert len(keys) == len(B) and set(keys) == set(B), f"块数/key 不匹配 {len(keys)} vs {len(B)}"
bad = []
for k, blk in B.items():
    names = {e["name"] for e in blk["entities"]}
    assert len(names) == len(blk["entities"]), f"{k}: 块内重名"
    for i, r in enumerate(blk["relations"]):
        for s in ("src", "dst"):
            if r[s] not in names:
                bad.append(f"{k}[r{i}]{s}={r[s]}")
        if not REL_RE.match(r["relation"]):
            bad.append(f"{k}[r{i}]关系非中文2-6:{r['relation']}")
        if r["src"] == r["dst"]:
            bad.append(f"{k}[r{i}]自环:{r['src']}")
        if len(r["evidence"]) > 40:
            bad.append(f"{k}[r{i}]evidence超长:{r['evidence']}")
    for e in blk["entities"]:
        if not 1 <= len(e["desc"]) <= 30:
            bad.append(f"{k}:desc长度={e['name']}")
        assert set(e) == {"name", "type", "aliases", "desc"}, f"{k} 字段异常"
        assert e["type"] in {"角色", "组织", "地点", "物品", "概念", "事件"}, f"{k}类型异常{e['type']}"
if bad:
    raise SystemExit("端点体检失败:\n  - " + "\n  - ".join(bad))
ne = sum(len(b["entities"]) for b in B.values())
nr = sum(len(b["relations"]) for b in B.values())
print(f"{len(B)}/{len(keys)} 块 ✅ 实体 {ne} 关系 {nr}")
(ROOT / "_agent_batch443.json").write_text(
    json.dumps(B, ensure_ascii=False, indent=1), encoding="utf-8")
print("写出 _agent_batch443.json")
