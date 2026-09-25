# -*- coding: utf-8 -*-
"""生成 _agent_batch537.json（appendix_unbound__017_1_9_去往新世界_槲寄生，4 块闭环）。

探针:_cands537.txt → 并集探针 + _sim_landing 需改写 0 个。
命名要点:
  * `槲寄生`/`维尔汀`/`阿尔卡纳`/`重塑之手`/`圣洛夫基金会`/`苏芙比` 既有节点复用;
  * `成长魔药`/`毕达哥拉斯树` EXISTS(batch),语义与「苏芙比留下的魔药」「方块三角修剪结构」相合 → 复用;
  * 裸名 `广场`(既有=泛称集会之处)与本篇「修复/抗议的基金会广场」语义不确定 → 分建 `槲寄生修复的广场`,不挂 alias;
  * `德鲁伊` 既有为概念节点(≠槲寄生 alias 可用)→ 不声明别名,只在 desc 描述;
  * `基金会` 是 `圣洛夫基金会` alias → 只写后者。归档卡建 `槲寄生的旁支脚本`。
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
N = {
    "槲": "槲寄生", "威": "维尔汀", "阿": "阿尔卡纳", "重": "重塑之手",
    "基": "圣洛夫基金会", "苏": "苏芙比", "药": "成长魔药", "毕": "毕达哥拉斯树",
    "场": "槲寄生修复的广场", "本": "槲寄生的旁支脚本",
}


def E(key, type_, desc, aliases=None):
    return {"name": N[key], "type": type_, "aliases": list(aliases or []), "desc": desc}


def R(sk, rel, dk, ev, conf=0.95):
    return {"src": N[sk], "relation": rel, "dst": N[dk], "evidence": ev, "confidence": conf}


B = {}

B["f2a9067f693d3e36ec862d39"] = {  # 0.0.0 归档卡 800301
    "entities": [
        E("本", "概念", "800301号未绑定候选脚本", ["800301"]),
        E("槲", "角色", "本脚本的主人公"),
    ],
    "relations": [
        R("本", "记载", "槲", "Internal title: 【1.9】去往新世界【槲寄生】"),
        R("本", "标注", "槲", "Binding status: unbound story candidate"),
    ],
}

B["a8b3d9aa3463cd74db056b58"] = {  # 0.1.0 战火后的树林与规律般的阿尔卡纳
    "entities": [
        E("槲", "角色", "倾听树木之声的德鲁伊"),
        E("威", "角色", "介绍修剪结构的司辰"),
        E("毕", "概念", "方块与三角相生的树木结构"),
        E("阿", "角色", "像规律一样没有目的的存在"),
        E("重", "组织", "目的可以被理解的敌手"),
        E("基", "组织", "评估植被威胁的机构"),
        E("苏", "角色", "留下魔药的小姐"),
        E("药", "物品", "被基金会分析的魔药"),
        E("场", "地点", "被占领抗议又遭修复的广场"),
    ],
    "relations": [
        R("槲", "首肯", "威", "确实如你所说，这里有着一片值得期待的森林"),
        R("威", "命名", "毕", "这被叫作毕达哥拉斯树"),
        R("槲", "致敬", "毕", "向先贤的智慧表示敬意"),
        R("槲", "修复", "场", "基金会并没有在我修复广场时进行刁难"),
        R("基", "评估", "槲", "他们借机重新评估了突然生长的植被能对基金会建筑安全造成的威胁"),
        R("基", "分析", "药", "还分析了苏芙比小姐留下的成长魔药"),
        R("药", "源自", "苏", "还分析了苏芙比小姐留下的成长魔药"),
        R("威", "击败", "阿", "我们终于打倒了阿尔卡纳"),
        R("槲", "理解", "重", "我可以理解重塑之手的目的"),
        R("槲", "譬喻", "阿", "阿尔卡纳就像是一条规律，一条没有目的的规律"),
    ],
}

B["56d7d1260462e0f8d40facfb"] = {  # 1.0.0 归档卡 800302
    "entities": [
        E("本", "概念", "800302号未绑定候选脚本", ["800302"]),
        E("槲", "角色", "本脚本的主人公"),
    ],
    "relations": [
        R("本", "记载", "槲", "Script ID: 800302"),
        R("本", "归属", "槲", "Appendix family: 【1.9】去往新世界【槲寄生】"),
    ],
}

B["24ffd60ee8c9918a1637a7bf"] = {  # 1.1.0 又再见：树木与规律之喻
    "entities": [
        E("槲", "角色", "与树木闲聊的德鲁伊"),
        E("威", "角色", "前来道别的司辰"),
        E("阿", "角色", "像规律一样没有目的的存在"),
        E("重", "组织", "目的可以被理解的敌手"),
        E("基", "组织", "未行刁难的机构"),
        E("苏", "角色", "留下魔药的小姐"),
        E("药", "物品", "被基金会分析的魔药"),
        E("场", "地点", "被占领抗议又遭修复的广场"),
    ],
    "relations": [
        R("槲", "道谢", "威", "多谢你的关心，维尔汀"),
        R("槲", "修复", "场", "基金会并没有在我修复广场时进行刁难"),
        R("基", "分析", "药", "还分析了苏芙比小姐留下的成长魔药"),
        R("药", "源自", "苏", "还分析了苏芙比小姐留下的成长魔药"),
        R("威", "击败", "阿", "我们终于打倒了阿尔卡纳"),
        R("槲", "理解", "重", "我可以理解重塑之手的目的"),
        R("槲", "譬喻", "阿", "阿尔卡纳就像是一条规律，一条没有目的的规律"),
        R("槲", "辞别", "威", "再见，这些树木的话很有趣"),
    ],
}

# ── 体检 ──
_dump_lines = [json.loads(l) for l in (ROOT / "_dump537.txt").read_text(encoding="utf-8-sig").splitlines() if l.strip()]
keys = [d["key"] for d in _dump_lines]
assert len(keys) == len(B) and set(keys) == set(B), f"块数/key 不匹配 {len(keys)} vs {len(B)}"
texts = {d["key"]: d["text"] for d in _dump_lines}
bad = []
for k, blk in B.items():
    names = {e["name"] for e in blk["entities"]}
    assert len(names) == len(blk["entities"]), f"{k}: 块内重名"
    for i, r in enumerate(blk["relations"]):
        for s in ("src", "dst"):
            if r[s] not in names:
                bad.append(f"{k}[r{i}]{s}={r[s]}")
        if not 2 <= len(r["relation"]) <= 6:
            bad.append(f"{k}[r{i}]len={r['relation']}")
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
(ROOT / "_agent_batch537.json").write_text(
    json.dumps(B, ensure_ascii=False, indent=1), encoding="utf-8")
print("写出 _agent_batch537.json")
