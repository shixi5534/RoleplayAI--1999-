# -*- coding: utf-8 -*-
"""生成 _agent_batch174.json（activity__13101_行至摩卢旁卡 16.0.2–16.0.4，共 3 块）。

本批为 13101 的**最后 3 块** → **行至摩卢旁卡闭环**（该版 53 块全部抽完）。

名字复用经 `_probe_names173.py` + batch173 已有判断延续。
`库玛尔的信`/`石窟石像`/`沙尔玛旧宅`/`夏尔贾`/`鬃毛沙砾的旧屋` 等
已在 batch173 建。本批新出现的具名实体：
  `娑罗室伐底`：伽菈波那口中的智慧女神 → 建（专名,有神话体系地位）。
  `都灵危险指数`/`巴勒莫撞击指数`：科学术语 → 不建（会污染检索）。
  `小糖饼`：夏尔贾对坎吉拉的昵称 → 不建（昵称,以 `夏尔贾` 关系承载）。
  `辛哈大叔` 的车 → 并入 `辛哈大叔` 关系,不单建。

自环：本批无（已自查）。
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DUMP = ROOT / "_dump174.txt"

NAME = {
    "伽": "伽菈波那", "库": "库玛尔", "鬃": "鬃毛沙砾",
    "玛": "玛蒂尔达", "坎": "坎吉拉", "夏": "夏尔贾",
    "阿贾": "阿贾尔", "辛哈": "辛哈大叔", "娑罗": "娑罗室伐底",
    "基": "圣洛夫基金会", "村": "摩卢旁卡村",
    "旧屋": "鬃毛沙砾的旧屋", "石窟": "石窟", "神庙": "摩卢旁卡神庙",
    "重塑": "重塑之手", "神秘": "神秘学家",
    "星": "特殊天体", "烛星": "烛星节", "昌迪": "昌迪加尔",
    "地图": "地图", "手册": "《地下生存手册》",
    "火车": "火车",
}


def E(name, type_, desc, aliases=None):
    return {"name": name, "type": type_, "aliases": aliases or [], "desc": desc}


def R(src, rel, dst, ev, conf=0.95):
    return {"src": src, "relation": rel, "dst": dst,
            "evidence": ev, "confidence": conf}


BATCH = {}

# ══ 16.0.2 伽菈波那的正式申请 ══
BATCH["299e8520da92d24a66661ed9"] = {
    "entities": [
        E(NAME["伽"], "角色", "正式向基金会提出申请的学者"),
        E(NAME["玛"], "角色", "被请求协助疏散的调查员"),
        E(NAME["鬃"], "角色", "分析库玛尔能力来源的男人"),
        E(NAME["库"], "角色", "可能获重塑帮助者"),
        E(NAME["基"], "组织", "被伽菈波那正式求助的机构"),
        E(NAME["村"], "地点", "需尽快疏散居民与游客之处"),
        E(NAME["星"], "物品", "都灵危险指数为5的天体"),
        E(NAME["烛星"], "事件", "即将演变为陨石灾难的节日"),
        E(NAME["昌迪"], "地点", "村子不在其辖区的城市"),
        E(NAME["神秘"], "概念", "伽菈波那的第二身份"),
        E(NAME["重塑"], "组织", "可能帮助库玛尔者"),
        E(NAME["娑罗"], "角色", "被伽菈波那提及还愿青睐的女神"),
    ],
    "relations": [
        R(NAME["鬃"], "置疑", NAME["库"], "她几乎和人类没有一点儿区别！连使用最基本的神秘术都难如登天"),
        R(NAME["鬃"], "置疑", NAME["库"], "这可不是一个普通的神秘学家能做到的事情"),
        R(NAME["伽"], "承认", NAME["库"], "她确实不能。但她知道方法"),
        R(NAME["伽"], "推断", NAME["重塑"], "如果真的是重塑给予了她帮助，这一切就是有可能的"),
        R(NAME["伽"], "感谢", NAME["玛"], "谢天谢地，在这里遇到了你"),
        R(NAME["玛"], "自谦", NAME["伽"], "不用强调职位！"),
        R(NAME["伽"], "感谢", NAME["娑罗"], "看来娑罗室伐底还愿青睐于我"),
        R(NAME["伽"], "申请", NAME["基"], "我以天文学教授及神秘学家的身份向基金会正式提出申请"),
        R(NAME["伽"], "请求", NAME["基"], "希望基金会可以协助我尽快疏散摩卢旁卡村的居民与游客"),
        R(NAME["伽"], "描述", NAME["星"], "该星体的都灵危险指数为5"),
        R(NAME["伽"], "警示", NAME["烛星"], "烛星节的流星雨即将演变成一场陨石灾难"),
        R(NAME["伽"], "陈述", NAME["昌迪"], "村子的地理位置特殊，不在昌迪加尔的辖区内"),
        R(NAME["伽"], "推断", NAME["库"], "石窟里发生的事很可能只是她的一次实验"),
        R(NAME["伽"], "誓言", NAME["库"], "我不能看着她利用我们的研究、我们的心血做这种事"),
        R(NAME["伽"], "承诺", NAME["村"], "我也会尽快找到库玛尔，阻止她继续"),
    ],
}

# ══ 16.0.3 坎吉拉逃回报信 ══
BATCH["ef34fe5e4809bb04cff188b4"] = {
    "entities": [
        E(NAME["坎"], "角色", "从神庙逃回报信的少女"),
        E(NAME["夏"], "角色", "在秘密基地等候的老师"),
        E(NAME["阿贾"], "角色", "被托付带大家逃走的男孩"),
        E(NAME["鬃"], "角色", "循位置找来的男人"),
        E(NAME["库"], "角色", "被提及未常用旧屋者"),
        E(NAME["辛哈"], "角色", "被坎吉拉借车的大叔"),
        E(NAME["旧屋"], "地点", "坎吉拉躲入的破烂院子"),
        E(NAME["神庙"], "地点", "坎吉拉逃来之处"),
        E(NAME["村"], "地点", "即将被石头砸平的村子"),
        E(NAME["烛星"], "事件", "将有陨石落下的节日"),
        E(NAME["石窟"], "地点", "坎吉拉被石头手拽住脚腕之处"),
        E(NAME["火车"], "地点", "坎吉拉希望大家爬上的列车"),
    ],
    "relations": [
        R(NAME["坎"], "逃离", NAME["神庙"], "矮小的身影灵巧且迅速地翻过墙壁"),
        R(NAME["坎"], "惊恐", NAME["村"], "怎么还会有石头掉下来啊！"),
        R(NAME["坎"], "呼唤", NAME["阿贾"], "阿贾尔，你带着大家……"),
        R(NAME["夏"], "找到", NAME["坎"], "坎吉拉？"),
        R(NAME["夏"], "自陈", NAME["旧屋"], "这里是你们的秘密基地"),
        R(NAME["夏"], "揪住", NAME["坎"], "年轻的女人拎起捣蛋鬼的一只耳朵"),
        R(NAME["夏"], "训斥", NAME["坎"], "教唆阿贾尔偷窃，闯入无人住的老屋"),
        R(NAME["坎"], "告饶", NAME["夏"], "这次是真的有大事……这个村子就要被毁啦"),
        R(NAME["坎"], "提及", NAME["辛哈"], "我都忘了自己从辛哈大叔那儿借来了车"),
        R(NAME["坎"], "复述", NAME["石窟"], "我在神庙的石窟里被一个石头手拽住了脚腕"),
        R(NAME["坎"], "转述", NAME["烛星"], "他们说，在几天后的烛星节上，会有那种叫“陨石”的大石头掉下来"),
        R(NAME["坎"], "恳求", NAME["夏"], "最好能爬上今天的火车……"),
        R(NAME["夏"], "安抚", NAME["坎"], "我说过那些只是故事"),
    ],
}

# ══ 16.0.4 两个钱包 ══
BATCH["c31700d0b80169b8cf13760f"] = {
    "entities": [
        E(NAME["鬃"], "角色", "循库玛尔旧屋而至的男人"),
        E(NAME["坎"], "角色", "与鬃毛沙砾一队相遇的少女"),
        E(NAME["玛"], "角色", "认出钱包的占卜师"),
        E(NAME["夏"], "角色", "与两队人马相见的老师"),
        E(NAME["库"], "角色", "曾被提及使用旧屋者"),
        E(NAME["旧屋"], "地点", "两队人马相遇之处"),
    ],
    "relations": [
        R(NAME["鬃"], "辨认", NAME["旧屋"], "这位置我绝不会记错，尽管库玛尔后来也没使用过几次"),
        R(NAME["坎"], "惊见", NAME["鬃"], "……！"),
        R(NAME["夏"], "询问", NAME["鬃"], "你们是……？"),
        R(NAME["玛"], "认出", NAME["坎"], "你手上的那个——那个是我的钱包吗？"),
    ],
}

# ══ 端点体检 ══
def _audit() -> None:
    bad: list[str] = []
    for key, blk in BATCH.items():
        names = {e["name"] for e in blk["entities"]}
        assert len(names) == len(blk["entities"]), f"{key}: 块内实体重名"
        for i, r in enumerate(blk["relations"]):
            for side in ("src", "dst"):
                if r[side] not in names:
                    bad.append(f"{key}[r{i}] {side}={r[side]!r} 不在 entities")
            if not (2 <= len(r["relation"]) <= 6):
                bad.append(f"{key}[r{i}] relation 长度非法: {r['relation']!r}")
            if not r["evidence"]:
                bad.append(f"{key}[r{i}] evidence 为空")
            if len(r["evidence"]) > 40:
                bad.append(f"{key}[r{i}] evidence 超 40 字: {r['evidence']}")
            if r["src"] == r["dst"]:
                bad.append(f"{key}[r{i}] 无意识自环: {r['src']}")
    ne = sum(len(b["entities"]) for b in BATCH.values())
    nr = sum(len(b["relations"]) for b in BATCH.values())
    print(f"{len(BATCH)}/{len(BATCH)} 块通过｜实体 {ne}｜关系 {nr}")
    if bad:
        raise SystemExit("端点体检失败：\n  - " + "\n  - ".join(bad))
    print("端点体检通过：所有 src/dst 逐字命中同块 entities")


def main() -> None:
    _audit()
    keys = [json.loads(l)["key"]
            for l in DUMP.read_text(encoding="utf-8-sig").splitlines() if l.strip()]
    assert len(keys) == len(BATCH), f"dump 块数 {len(keys)} != 生成块数 {len(BATCH)}"
    miss = [k for k in keys if k not in BATCH]
    extra = [k for k in BATCH if k not in keys]
    assert not miss and not extra, f"key 不匹配 miss={miss} extra={extra}"
    out = ROOT / "_agent_batch174.json"
    out.write_text(json.dumps(BATCH, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    print(f"已写出 {out.name}（{len(BATCH)} 块，key 与 dump 一一对应）")


if __name__ == "__main__":
    main()
