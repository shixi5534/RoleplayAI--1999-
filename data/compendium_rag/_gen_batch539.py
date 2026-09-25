# -*- coding: utf-8 -*-
"""生成 _agent_batch539.json（appendix_unbound__019_1_9_去往新世界_红弩箭，4 块闭环）。

探针:_cands539.txt → 并集探针 + _sim_landing 需改写 0 个。
命名要点:
  * `红弩箭`/`维尔汀`/`芝诺`(军备学院为其 alias)/`阿尔卡纳`/`圣洛夫基金会`/`伏特加` 既有节点复用;
  * `手提箱` 是既有 alias(§4.11 落盘失效名单)→ 「你的箱子」新建独立节点 `维尔汀的箱子`;
  * `表彰大会` 泛称不裸用 → 建 `芝诺的表彰大会`(事件);
  * 归档卡建 `红弩箭的旁支脚本`,Script ID 800401/800402 作逐块 alias。
"""
import json
import re as _re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
N = {
    "红": "红弩箭", "威": "维尔汀", "伏": "伏特加", "芝": "芝诺",
    "基": "圣洛夫基金会", "阿": "阿尔卡纳", "箱": "维尔汀的箱子",
    "认": "芝诺的表彰大会", "本": "红弩箭的旁支脚本",
}


def E(key, type_, desc, aliases=None):
    return {"name": N[key], "type": type_, "aliases": list(aliases or []), "desc": desc}


def R(sk, rel, dk, ev, conf=0.95):
    return {"src": N[sk], "relation": rel, "dst": N[dk], "evidence": ev, "confidence": conf}


B = {}

B["33e4db842a93de073bdb173b"] = {  # 0.0.0 归档卡 800401
    "entities": [
        E("本", "概念", "800401号未绑定候选脚本", ["800401"]),
        E("红", "角色", "本脚本的主人公"),
    ],
    "relations": [
        R("本", "记载", "红", "Internal title: 【1.9】去往新世界【红弩箭】"),
        R("本", "标注", "红", "Binding status: unbound story candidate"),
    ],
}

B["343cbf21413499544b4527f5"] = {  # 0.1.0 至高点上的伏特加与战绩谈
    "entities": [
        E("红", "角色", "在至高点回味畅快的飞行员"),
        E("威", "角色", "被劝喝烈酒的司辰"),
        E("伏", "物品", "戒碳酸的烈性替代品"),
        E("芝", "组织", "只是考飞行驾照的地方"),
        E("基", "组织", "只能当理论教官的机构"),
        E("阿", "角色", "已被化成灰确认死亡的头号敌人"),
        E("箱", "物品", "最符合野战条件的乌合之众所在"),
        E("认", "事件", "连军犬都要记三等功的大会"),
    ],
    "relations": [
        R("红", "呼喊", "威", "嘿，维尔汀，快过来陪我一起喝"),
        R("红", "力荐", "伏", "你得开始习惯伏特加"),
        R("威", "推辞", "伏", "我还没到那个年纪"),
        R("红", "隶属", "芝", "对我来说芝诺就是考飞行驾照的地方"),
        R("红", "效力", "基", "在基金会又只能当理论教官"),
        R("红", "忌惮", "芝", "在芝诺想飞需要命令"),
        R("红", "指认", "箱", "你的箱子"),
        R("红", "证实", "阿", "官方消息已经确认阿尔卡纳死亡了"),
        R("芝", "举办", "认", "所有人都在参加表彰大会"),
        R("红", "相约", "威", "下次我们可以再一起去兜兜风"),
    ],
}

B["769ac0555895771eddd56607"] = {  # 1.0.0 归档卡 800402
    "entities": [
        E("本", "概念", "800402号未绑定候选脚本", ["800402"]),
        E("红", "角色", "本脚本的主人公"),
    ],
    "relations": [
        R("本", "记载", "红", "Script ID: 800402"),
        R("本", "归属", "红", "Appendix family: 【1.9】去往新世界【红弩箭】"),
    ],
}

B["0081832092a71f743298e748"] = {  # 1.1.0 飞行驾照与空战之约
    "entities": [
        E("红", "角色", "吹嘘个人经历的飞行员"),
        E("威", "角色", "被邀约兜风的司辰"),
        E("芝", "组织", "想飞需要命令的地方"),
        E("基", "组织", "只能当理论教官的机构"),
        E("阿", "角色", "已被化成灰确认死亡的头号敌人"),
        E("箱", "物品", "最符合野战条件的乌合之众所在"),
        E("认", "事件", "连军犬都要记三等功的大会"),
    ],
    "relations": [
        R("红", "隶属", "芝", "对我来说芝诺就是考飞行驾照的地方"),
        R("红", "效力", "基", "在基金会又只能当理论教官"),
        R("红", "忌惮", "芝", "在芝诺想飞需要命令"),
        R("红", "指认", "箱", "你的箱子"),
        R("红", "证实", "阿", "官方消息已经确认阿尔卡纳死亡了"),
        R("芝", "举办", "认", "所有人都在参加表彰大会"),
        R("红", "相约", "威", "下次我们可以再一起去兜兜风"),
    ],
}

# ── 体检 ──
_dump_lines = [json.loads(l) for l in (ROOT / "_dump539.txt").read_text(encoding="utf-8-sig").splitlines() if l.strip()]
keys = [d["key"] for d in _dump_lines]
assert len(keys) == len(B) and set(keys) == set(B), f"块数/key 不匹配 {len(keys)} vs {len(B)}"
texts = {d["key"]: d["text"] for d in _dump_lines}
HAN = _re.compile(r"^[\u4e00-\u9fff]{2,6}$")
bad = []
for k, blk in B.items():
    names = {e["name"] for e in blk["entities"]}
    assert len(names) == len(blk["entities"]), f"{k}: 块内重名"
    for i, r in enumerate(blk["relations"]):
        for s in ("src", "dst"):
            if r[s] not in names:
                bad.append(f"{k}[r{i}]{s}={r[s]}")
        if not HAN.match(r["relation"]):
            bad.append(f"{k}[r{i}]relation非纯汉字:{r['relation']}")
        if len(r["evidence"]) > 40:
            bad.append(f"{k}[r{i}]evidence超长:{r['evidence']}")
        if r["evidence"].replace("“", "").replace("”", "") not in texts[k].replace("“", "").replace("”", ""):
            bad.append(f"{k}[r{i}]evidence非原文子串:{r['evidence']}")
    for e in blk["entities"]:
        if not 1 <= len(e["desc"]) <= 30:
            bad.append(f"{k}:desc长度={e['name']}")
        if e["name"] in e["aliases"]:
            bad.append(f"{k}:别名重复本体={e['name']}")
if bad:
    raise SystemExit("体检失败:\n  - " + "\n  - ".join(bad))
ne = sum(len(b["entities"]) for b in B.values())
nr = sum(len(b["relations"]) for b in B.values())
print(f"{len(B)}/{len(keys)} 块 ✅ 实体 {ne} 关系 {nr}")
(ROOT / "_agent_batch539.json").write_text(
    json.dumps(B, ensure_ascii=False, indent=1), encoding="utf-8")
print("写出 _agent_batch539.json")
