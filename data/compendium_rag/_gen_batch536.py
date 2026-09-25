# -*- coding: utf-8 -*-
"""生成 _agent_batch536.json（appendix_unbound__016_1_9_去往新世界_星锑，4 块闭环）。

探针:_cands536.txt → 并集探针 + _sim_landing 需改写 0 个。
命名要点:
  * `星锑`/`维尔汀`/`阿尔卡纳`/`胡椒博士`/`暴雨`/`平衡伞`/`阿其翁` 既有节点语义相合 → 复用;
  * `摇滚海盗` 为星锑自称(仅 0.1.0 出现)→ 只在该块声明 alias,不建独立节点;
  * 归档卡建 `星锑的旁支脚本`(概念),Script ID 800501/800502 作逐块 alias。
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
N = {
    "星": "星锑", "威": "维尔汀", "阿": "阿尔卡纳", "胡": "胡椒博士",
    "暴": "暴雨", "伞": "平衡伞", "其": "阿其翁", "狮": "狮子座",
    "本": "星锑的旁支脚本",
}


def E(key, type_, desc, aliases=None):
    return {"name": N[key], "type": type_, "aliases": list(aliases or []), "desc": desc}


def R(sk, rel, dk, ev, conf=0.95):
    return {"src": N[sk], "relation": rel, "dst": N[dk], "evidence": ev, "confidence": conf}


B = {}

B["90e24dd022e2ad65324194c9"] = {  # 0.0.0 归档卡 800501
    "entities": [
        E("本", "概念", "800501号未绑定候选脚本", ["800501"]),
        E("星", "角色", "本脚本的主人公"),
    ],
    "relations": [
        R("本", "记载", "星", "Internal title: 【1.9】去往新世界【星锑】"),
        R("本", "标注", "星", "Binding status: unbound story candidate"),
    ],
}

B["98d44152607b4c2bcaffa559"] = {  # 0.1.0 漂流尽头的碳酸庆功
    "entities": [
        E("星", "角色", "漂流后畅饮庆功的摇滚海盗", ["摇滚海盗"]),
        E("威", "角色", "被劝放松的疲惫司辰"),
        E("胡", "物品", "万事大吉后的碳酸奖赏"),
        E("阿", "角色", "已被收拾的旧敌"),
        E("暴", "事件", "已寻得免疫之法的天灾"),
        E("伞", "物品", "被指望铺满全球的器物"),
        E("其", "概念", "规矩之岛上会咬人的生物"),
    ],
    "relations": [
        R("星", "畅饮", "胡", "正在对着海平线畅饮碳酸饮料"),
        R("星", "致敬", "威", "敬维尔汀！"),
        R("星", "炫耀", "威", "我还在一天之内收获了两艘船！"),
        R("星", "击败", "阿", "我们已经收拾了阿尔卡纳"),
        R("星", "解决", "暴", "找到了免疫“暴雨”的办法"),
        R("星", "谈及", "其", "岛上的阿其翁还会咬人"),
        R("星", "赞颂", "暴", "为了信念而死，唱着歌走进“暴雨”，这相当酷"),
        R("星", "铺展", "伞", "接下来只要把平衡伞铺满全球"),
    ],
}

B["e444404ae2ca7848673ac347"] = {  # 1.0.0 归档卡 800502
    "entities": [
        E("本", "概念", "800502号未绑定候选脚本", ["800502"]),
        E("星", "角色", "本脚本的主人公"),
    ],
    "relations": [
        R("本", "记载", "星", "Script ID: 800502"),
        R("本", "归属", "星", "Appendix family: 【1.9】去往新世界【星锑】"),
    ],
}

B["055f709c350102e2099d0da4"] = {  # 1.1.0 宇宙摇滚海盗的展望
    "entities": [
        E("星", "角色", "展望未来的摇滚海盗"),
        E("威", "角色", "被调侃的司辰"),
        E("胡", "物品", "随时可来讨取的碳酸饮料"),
        E("暴", "事件", "免疫之法已到手的天灾"),
        E("伞", "物品", "被指望铺满全球的器物"),
        E("其", "概念", "规矩之岛上会咬人的生物"),
        E("狮", "地点", "地外摇滚生命的寻找之地"),
    ],
    "relations": [
        R("星", "招待", "胡", "怎么，要再来一罐胡椒博士么？"),
        R("星", "致敬", "威", "敬维尔汀！"),
        R("星", "谈及", "其", "岛上的阿其翁还会咬人"),
        R("星", "赞颂", "暴", "为了信念而死，唱着歌走进“暴雨”，这相当酷"),
        R("星", "铺展", "伞", "接下来只要把平衡伞铺满全球"),
        R("星", "展望", "威", "我们就可以跨越1999年了！"),
        R("星", "相约", "狮", "然后我们就一起去狮子座寻找喜欢摇滚的地外生命"),
        R("星", "打趣", "威", "你是不是和那群穿袍子的数学呆子待在一起太久了"),
    ],
}

# ── 体检 ──
_dump_lines = [json.loads(l) for l in (ROOT / "_dump536.txt").read_text(encoding="utf-8-sig").splitlines() if l.strip()]
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
(ROOT / "_agent_batch536.json").write_text(
    json.dumps(B, ensure_ascii=False, indent=1), encoding="utf-8")
print("写出 _agent_batch536.json")
