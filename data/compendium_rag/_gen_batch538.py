# -*- coding: utf-8 -*-
"""生成 _agent_batch538.json（appendix_unbound__018_1_9_去往新世界_玛蒂尔达，4 块闭环）。

探针:_cands538.txt → 并集探针 + _sim_landing 需改写 0 个。
命名要点:
  * `玛蒂尔达`/`维尔汀`/`苏芙比`/`十四行诗`/`水晶球`(既有 desc=玛蒂尔达的器具) 复用;
  * `扭扭舞会`/`玛蒂尔达的母亲` EXISTS(batch) 且语义相合 → 复用;
  * 裸名 `妈妈` 会吸入 `母亲` 组(实测 MERGE)→ 用 `玛蒂尔达的母亲`;
  * `调查员`/`纪律辅员` 为通用职位词(§4.2/§4.3)→ 不建不挂 alias,立志语义走自环(§4.7);
  * 归档卡建 `玛蒂尔达的旁支脚本`,Script ID 804101/804102 作逐块 alias。
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
N = {
    "玛": "玛蒂尔达", "威": "维尔汀", "苏": "苏芙比", "十": "十四行诗",
    "晶": "水晶球", "扭": "扭扭舞会", "母": "玛蒂尔达的母亲",
    "本": "玛蒂尔达的旁支脚本",
}


def E(key, type_, desc, aliases=None):
    return {"name": N[key], "type": type_, "aliases": list(aliases or []), "desc": desc}


def R(sk, rel, dk, ev, conf=0.95):
    return {"src": N[sk], "relation": rel, "dst": N[dk], "evidence": ev, "confidence": conf}


B = {}

B["da787cb769e5d9bc97e1ea6c"] = {  # 0.0.0 归档卡 804101
    "entities": [
        E("本", "概念", "804101号未绑定候选脚本", ["804101"]),
        E("玛", "角色", "本脚本的主人公"),
    ],
    "relations": [
        R("本", "记载", "玛", "Internal title: 【1.9】去往新世界【玛蒂尔达】"),
        R("本", "标注", "玛", "Binding status: unbound story candidate"),
    ],
}

B["9963b97df1f6276c7564d1f3"] = {  # 0.1.0 追查扭扭舞会的占卜师
    "entities": [
        E("玛", "角色", "追查舞会传闻的占卜师"),
        E("威", "角色", "被当面质问的司辰"),
        E("苏", "角色", "透露全部计划的小姐"),
        E("十", "角色", "被当作比较对象的同伴"),
        E("晶", "物品", "占卜师携带来去的水晶球"),
        E("扭", "事件", "并不存在的传闻舞会"),
        E("母", "角色", "休息日要探望的母亲"),
    ],
    "relations": [
        R("玛", "呼喊", "威", "维尔汀——！！！"),
        R("玛", "携带", "晶", "天才占卜师带着她的水晶球"),
        R("玛", "质问", "威", "你觉得你们能躲过我"),
        R("玛", "归咎", "苏", "友好的苏芙比小姐已经透露了你们的全部计划"),
        R("威", "否认", "扭", "根本没有什么扭扭舞会，玛蒂尔达"),
        R("玛", "怀疑", "苏", "难道这只是苏芙比小姐的某种玩笑"),
        R("玛", "立志", "玛", "总有一天我会自己成为调查员"),
        R("玛", "胜过", "十", "然后做得比十四行诗和你都好"),
        R("玛", "索邀", "威", "一定要邀请我，我作为纪律辅员有义务到场监督"),
        R("玛", "探望", "母", "我的下下个休息日已经确定要用来探望我妈妈了"),
    ],
}

B["39392afe67105d88d28469a5"] = {  # 1.0.0 归档卡 804102
    "entities": [
        E("本", "概念", "804102号未绑定候选脚本", ["804102"]),
        E("玛", "角色", "本脚本的主人公"),
    ],
    "relations": [
        R("本", "记载", "玛", "Script ID: 804102"),
        R("本", "归属", "玛", "Appendix family: 【1.9】去往新世界【玛蒂尔达】"),
    ],
}

B["77505765ab23b2fcde435079"] = {  # 1.1.0 嘴硬的纪律辅员
    "entities": [
        E("玛", "角色", "坚称无意派对的纪律辅员"),
        E("威", "角色", "被宣告要受监督的司辰"),
        E("十", "角色", "被当作比较对象的同伴"),
        E("母", "角色", "休息日要探望的母亲"),
    ],
    "relations": [
        R("玛", "立志", "玛", "总有一天我会自己成为调查员"),
        R("玛", "胜过", "十", "然后做得比十四行诗和你都好"),
        R("玛", "否认", "威", "我，我可没有表达过想要开派对的意图"),
        R("玛", "监督", "威", "因为我会留在这关注你"),
        R("玛", "探望", "母", "我的下下个休息日已经确定要用来探望我妈妈了"),
        R("玛", "叮嘱", "威", "你得把时间定在我的下下个休息日之后才行"),
    ],
}

# ── 体检 ──
_dump_lines = [json.loads(l) for l in (ROOT / "_dump538.txt").read_text(encoding="utf-8-sig").splitlines() if l.strip()]
keys = [d["key"] for d in _dump_lines]
assert len(keys) == len(B) and set(keys) == set(B), f"块数/key 不匹配 {len(keys)} vs {len(B)}"
texts = {d["key"]: d["text"] for d in _dump_lines}
import re as _re
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
(ROOT / "_agent_batch538.json").write_text(
    json.dumps(B, ensure_ascii=False, indent=1), encoding="utf-8")
print("写出 _agent_batch538.json")
