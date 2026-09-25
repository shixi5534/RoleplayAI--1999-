# -*- coding: utf-8 -*-
"""生成 _agent_batch535.json（appendix_unbound__015_1_9_去往新世界_无线电小姐，4 块闭环）。

探针:_cands535.txt → _probe_union_alias + _sim_landing 需改写 0 个。
命名要点:
  * `基金会` 是 `圣洛夫基金会` 的 alias(实测)→ 只写后者;
  * 裸名 `兀尔德` 已被 `德洛丝` 组吸收(红线 1)→ 复用既有限定名节点 `传记作家兀尔德`
    (desc=「基金会被要求查明下落者」,与本块维尔汀委托寻人语义相合);
  * `无线电小姐`/`维尔汀` 既有节点复用;
  * 归档说明卡建 `无线电小姐的旁支脚本`(概念),Script ID 802701/802702 作逐块 alias。
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
N = {
    "无": "无线电小姐", "威": "维尔汀", "基": "圣洛夫基金会",
    "兀": "传记作家兀尔德", "歌": "《水瓶座》", "本": "无线电小姐的旁支脚本",
    "本1": "无线电小姐的旁支脚本802701", "本2": "无线电小姐的旁支脚本802702",
}
AL = {"本": {0: ["802701"], 2: ["802702"]}}  # 按块序给脚本卡配 alias


def E(key, type_, desc, aliases=None):
    return {"name": N[key], "type": type_, "aliases": list(aliases or []), "desc": desc}


def R(sk, rel, dk, ev, conf=0.95):
    return {"src": N[sk], "relation": rel, "dst": N[dk], "evidence": ev, "confidence": conf}


B = {}

B["eeaf725d89e1d9012ec8ab1f"] = {  # 0.0.0 归档卡 802701
    "entities": [
        E("本1", "概念", "802701号未绑定候选脚本归档卡", AL["本"][0]),
        E("无", "角色", "本脚本的主人公"),
    ],
    "relations": [
        R("本1", "记载", "无", "Internal title: 【1.9】去往新世界【无线电小姐】"),
        R("本1", "标注", "无", "Binding status: unbound story candidate"),
    ],
}

B["c01e1a97a63a11de95cb5675"] = {  # 0.1.0 晒太阳的绿色信使与寻人委托
    "entities": [
        E("无", "角色", "重获信任的绿色信使"),
        E("威", "角色", "委托查访情报的司辰"),
        E("基", "组织", "她盼着能自由活动其间的机构"),
        E("兀", "角色", "维尔汀想查找的传记作家"),
        E("歌", "概念", "空气中响起的第五维度歌曲"),
    ],
    "relations": [
        R("无", "奏响", "歌", "但空气中这首第五维度的《水瓶座》可能意味着她有个好心情"),
        R("无", "试探", "威", "难道是对我的审判终于下达了"),
        R("无", "道谢", "威", "感谢你们的信任，维尔汀小姐"),
        R("无", "效力", "基", "我想我可以在基金会里稍许自由地活动了"),
        R("威", "委托", "无", "我想拜托你找个人"),
        R("威", "寻访", "兀", "我想找的人叫兀尔德"),
        R("无", "认出", "兀", "噢～那位传记作家"),
        R("无", "留意", "兀", "我会全方位留意这个名字的一切讯息"),
    ],
}

B["3f6542ba2aaa252a1aadc7d9"] = {  # 1.0.0 归档卡 802702
    "entities": [
        E("本2", "概念", "802702号未绑定候选脚本归档卡", AL["本"][2]),
        E("无", "角色", "本脚本的主人公"),
    ],
    "relations": [
        R("本2", "记载", "无", "Script ID: 802702"),
        R("本2", "归属", "无", "Appendix family: 【1.9】去往新世界【无线电小姐】"),
    ],
}

B["e08cc38c0fdfe9a3427784cd"] = {  # 1.1.0 再会：波段间的寻人委托
    "entities": [
        E("无", "角色", "等待新发现的收音机小姐"),
        E("威", "角色", "委托留意情报的司辰"),
        E("基", "组织", "她盼着能自由活动其间的机构"),
        E("兀", "角色", "维尔汀想查找的传记作家"),
    ],
    "relations": [
        R("无", "道谢", "威", "感谢你们的信任，维尔汀小姐"),
        R("无", "效力", "基", "我想我可以在基金会里稍许自由地活动了"),
        R("威", "委托", "无", "我想拜托你找个人"),
        R("威", "寻访", "兀", "我想找的人叫兀尔德"),
        R("无", "认出", "兀", "噢～那位传记作家"),
        R("无", "应承", "威", "当然可以，您想找哪位DJ？"),
        R("无", "留意", "兀", "我会全方位留意这个名字的一切讯息"),
    ],
}

# ── 体检 ──
keys = [json.loads(l)["key"]
        for l in (ROOT / "_dump535.txt").read_text(encoding="utf-8-sig").splitlines() if l.strip()]
assert len(keys) == len(B) and set(keys) == set(B), f"块数/key 不匹配 {len(keys)} vs {len(B)}"
texts = {json.loads(l)["key"]: json.loads(l)["text"]
         for l in (ROOT / "_dump535.txt").read_text(encoding="utf-8-sig").splitlines() if l.strip()}
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
(ROOT / "_agent_batch535.json").write_text(
    json.dumps(B, ensure_ascii=False, indent=1), encoding="utf-8")
print("写出 _agent_batch535.json")
