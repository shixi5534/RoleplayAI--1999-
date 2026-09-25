# -*- coding: utf-8 -*-
"""生成 _agent_batch541.json（appendix_unbound__021_1_9_去往新世界_露西，4 块闭环）。

探针:_cands541.txt → 并集探针 + _sim_landing 需改写 0 个。
命名要点:
  * `露西`(既有 desc=机械女士)/`维尔汀`/`IDM`(既有物品节点)/`Z`/`科算中心` 复用;
  * 裸名 `拉普拉斯` 已被吸收为 `科算中心` alias(实测)→ 只写后者;
  * `Z女士` 是 `Z` 的既有 alias → 端点用 `Z`,并在出现块声明 alias `Z女士`;
  * `意识唤醒者` 为受污染的泛称词(§3.3,乌尔里希/卡戎组)→ 不建不挂,语义走自述;
  * 新建 `露西的休息计划`(概念)、`露西的旁支脚本`(归档卡,Script ID 808601/808602 逐块 alias);
  * `维尔汀的箱子` 沿用本段 batch539 的建名。
"""
import json
import re as _re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
N = {
    "露": "露西", "威": "维尔汀", "机": "IDM", "科": "科算中心", "Z": "Z",
    "箱": "维尔汀的箱子", "休": "露西的休息计划", "本": "露西的旁支脚本",
}


def E(key, type_, desc, aliases=None):
    return {"name": N[key], "type": type_, "aliases": list(aliases or []), "desc": desc}


def R(sk, rel, dk, ev, conf=0.95):
    return {"src": N[sk], "relation": rel, "dst": N[dk], "evidence": ev, "confidence": conf}


B = {}

B["93c25d647c6410edafdf2bb9"] = {  # 0.0.0 归档卡 808601
    "entities": [
        E("本", "概念", "808601号未绑定候选脚本", ["808601"]),
        E("露", "角色", "本脚本的主人公"),
    ],
    "relations": [
        R("本", "记载", "露", "Internal title: 【1.9】去往新世界【露西】"),
        R("本", "标注", "露", "Binding status: unbound story candidate"),
    ],
}

B["40737ebdf76e1df0bb7f6801"] = {  # 0.1.0 钢铁女士的休息悖论
    "entities": [
        E("露", "角色", "被命令学习休息的机械女士"),
        E("威", "角色", "被请教定义的司辰"),
        E("机", "物品", "露西端坐其旁的计算机"),
        E("科", "组织", "下令停职休息的机构"),
        E("Z", "角色", "给出箱子建议的联络人", ["Z女士"]),
        E("箱", "物品", "被推荐为休息去处的箱子"),
        E("休", "概念", "尚未制定完整的休息计划"),
    ],
    "relations": [
        R("露", "端坐", "机", "一位表情寡淡的女士端坐在IDM旁"),
        R("露", "问候", "威", "很高兴能见到您，司辰"),
        R("露", "离开", "科", "我被命令停止目前的职务，离开拉普拉斯并休息一段时间"),
        R("Z", "建言", "露", "Z女士给了我一个建议"),
        R("露", "常驻", "箱", "她说您的箱子会是个休息的好去处"),
        R("露", "请教", "威", "我想请问您，人对休息的定义究竟是什么"),
        R("露", "赞同", "威", "很高兴您与我得出了一样的结论"),
        R("露", "拟定", "休", "别忘了我们还没有制定好完整的休息计划"),
        R("露", "达成", "休", "我只能通过维持充电状态来达成休息这一目的了"),
        R("露", "点破", "威", "抱歉打断您，司辰，但您正在提出一则悖论"),
    ],
}

B["9e7ef2e3ac00c88ff9a2424d"] = {  # 1.0.0 归档卡 808602
    "entities": [
        E("本", "概念", "808602号未绑定候选脚本", ["808602"]),
        E("露", "角色", "本脚本的主人公"),
    ],
    "relations": [
        R("本", "记载", "露", "Script ID: 808602"),
        R("本", "归属", "露", "Appendix family: 【1.9】去往新世界【露西】"),
    ],
}

B["b848f7e7458d803bf56a2700"] = {  # 1.1.0 充电式休息与悖论重申
    "entities": [
        E("露", "角色", "追问休息建议的机械女士"),
        E("威", "角色", "被请求重提建议的司辰"),
        E("休", "概念", "尚未制定完整的休息计划"),
    ],
    "relations": [
        R("露", "请教", "威", "关于像人一样休息，还有什么建议么，司辰"),
        R("露", "赞同", "威", "很高兴您与我得出了一样的结论"),
        R("露", "达成", "休", "我只能通过维持充电状态来达成休息这一目的了"),
        R("露", "拟定", "休", "别忘了我们还没有制定好完整的休息计划"),
        R("露", "点破", "威", "抱歉打断您，司辰，但您正在提出一则悖论"),
        R("露", "复核", "休", "现在我的任务就是休息，如果我为了休息不得不停止工作"),
    ],
}

# ── 体检 ──
_dump_lines = [json.loads(l) for l in (ROOT / "_dump541.txt").read_text(encoding="utf-8-sig").splitlines() if l.strip()]
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
(ROOT / "_agent_batch541.json").write_text(
    json.dumps(B, ensure_ascii=False, indent=1), encoding="utf-8")
print("写出 _agent_batch541.json")
