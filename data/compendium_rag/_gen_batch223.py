# -*- coding: utf-8 -*-
"""生成 _agent_batch223.json（activity__24101_地球上最后的夜晚 收官轮：20.0.1–22.0.0，共 4 块）。

探针：沿用 §3.3 判定（本批无新候选名，全部复用已建或按同一规则命名）。

═══ 收官：本篇结局 ═══
* 维尔汀以基金会身份求援；芭卡洛儿想起后备救生艇位置。
* 格蕾丝回重塑复命，却躲进棺椁剧烈咳嗽 —— **「暴雨」并未到来**，
  她的预言是骗局；这正是她后来「期待与维尔汀再会」的伏笔。
* 芭卡洛儿以「分解咔咔咒」把啪唧匣子拆成救生船；
  她终于承认自己从未离开过克雷莫纳。

═══ 命名判定 ═══
* `乌尔里希` → **`暴雨小组组长乌尔里希`**；`淑女格蕾丝` → **`无名者`** + alias。
* `啪唧匣子`（batch217 已建）→ 复用；`绞弦琴`/`小提琴` 为其内嵌乐器。
* `救生筏`/`救生艇` —— 原文两种写法并存，分建（艇为大船所配、筏为拆解所得）。
* 未具名者按功能称谓（§9.6）：`感激的客人`/`忐忑的客人`/`恍惚的客人`/
  `惊讶的客人`/`怀念的客人`/`感动的客人`/`埃迪特先生`。
  其中 `埃迪特先生` 是原文点名的乘客，独立建。

自环：本批无（已自查）。
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DUMP = ROOT / "_dump223.txt"

NAME = {
    # ── 人物 ──
    "维": "维尔汀", "十": "十四行诗", "芭": "芭卡洛儿",
    "伊": "舵手伊萨姆", "查": "舵手老查理",
    "乌": "暴雨小组组长乌尔里希", "星": "星锑",
    "图": "图图石子", "勿": "勿忘我",
    "格": "无名者", "丝": "淑女格蕾丝",
    "感客": "感激的客人", "忐客": "忐忑的客人",
    "恍客": "恍惚的客人", "惊客": "惊讶的客人",
    "怀客": "怀念的客人", "动客": "感动的客人", "埃": "埃迪特先生",
    # ── 地点 ──
    "重塑一隅": "重塑一隅", "克": "克雷莫纳", "那不勒斯": "那不勒斯",
    "加利西亚": "加利西亚", "自由海风号": "自由海风号",
    # ── 组织 ──
    "基金": "圣洛夫基金会", "算": "科算中心", "塑": "重塑之手",
    "组": "暴雨专项研究小组",
    # ── 物品 / 概念 ──
    "通讯": "通讯器", "箱": "箱子", "救生艇": "救生艇",
    "救生筏": "救生筏", "匣": "啪唧匣子", "琴": "小提琴",
    "绞弦琴": "绞弦琴", "贝壳": "象形贝壳", "雨": "暴雨",
    "棺椁": "棺椁", "直升机": "基金会直升机", "音乐": "音乐",
}


def E(name, type_, desc, aliases=None):
    return {"name": name, "type": type_, "aliases": aliases or [], "desc": desc}


def R(src, rel, dst, ev, conf=0.95):
    return {"src": src, "relation": rel, "dst": dst,
            "evidence": ev, "confidence": conf}


BATCH = {}

# ══ 20.0.1 维尔汀求援；芭卡洛儿想起后备救生艇 ══
BATCH["d4cda7667e12f74663478a84"] = {
    "entities": [
        E(NAME["十"], "角色", "报告信号恢复的助手"),
        E(NAME["维"], "角色", "向基金会求援的司辰"),
        E(NAME["芭"], "角色", "忆起后备救生艇位置者"),
        E(NAME["伊"], "角色", "赞叹其了解船只的舵手"),
        E(NAME["查"], "角色", "附和其了解的舵手"),
        E(NAME["基金"], "组织", "应答求援并调遣救援者"),
        E(NAME["塑"], "组织", "炸毁动力室的势力"),
        E(NAME["通讯"], "物品", "恢复信号的通讯器"),
        E(NAME["箱"], "物品", "不足以疏散全部乘客的箱子"),
        E(NAME["救生艇"], "物品", "其后备位置未被重塑发现的救生艇"),
        E(NAME["自由海风号"], "物品", "正在下沉的游轮"),
    ],
    "relations": [
        R(NAME["十"], "报告", NAME["维"], "信号恢复了，司辰"),
        R(NAME["维"], "推断", NAME["塑"], "看来之前果然是重塑在捣乱"),
        R(NAME["维"], "求援", NAME["基金"], "我们需要足够数量的救生艇援助"),
        R(NAME["维"], "通报", NAME["自由海风号"], "重塑之手炸毁了“自由海风号”的动力室"),
        R(NAME["维"], "窘于", NAME["箱"], "仅仅依靠手提箱，我们无法在船只沉没之前疏散所有乘客"),
        R(NAME["芭"], "推断", NAME["救生艇"], "她肯定不知道后备救生艇的位置"),
        R(NAME["伊"], "赞叹", NAME["芭"], "我就知道没人比你更了解这艘船"),
        R(NAME["十"], "询问", NAME["芭"], "请告诉我广播室的位置"),
    ],
}

# ══ 21.0.0 格蕾丝复命；图图石子让出名额 ══
BATCH["e27df19ed35889cd54deb464"] = {
    "entities": [
        E(NAME["勿"], "角色", "验收材料并称赞使徒者"),
        E(NAME["格"], "角色", "勉力维持镇定的使徒",
          aliases=[NAME["丝"]]),
        E(NAME["芭"], "角色", "以音乐引路撤离的乐手"),
        E(NAME["感客"], "角色", "敬佩其勇气者"),
        E(NAME["忐客"], "角色", "疑虑救生筏数量不足者"),
        E(NAME["恍客"], "角色", "渴望回乡看看者"),
        E(NAME["图"], "角色", "愿让出救生艇名额者"),
        E(NAME["埃"], "角色", "被芭卡洛儿点名的乘客"),
        E(NAME["贝壳"], "物品", "努库泰澳人毕生情感积淀的象形贝壳"),
        E(NAME["救生筏"], "物品", "数量存疑的救生筏"),
        E(NAME["救生艇"], "物品", "图图石子愿让出的名额"),
        E(NAME["棺椁"], "物品", "本该为下一件收藏品准备的展柜"),
        E(NAME["匣"], "物品", "以音乐为众人引路的乐器"),
        E(NAME["自由海风号"], "物品", "众人所处的沉船"),
    ],
    "relations": [
        R(NAME["勿"], "验收", NAME["贝壳"], "很优异的材料"),
        R(NAME["勿"], "称赞", NAME["格"], "你很好地完成了任务，使徒小姐"),
        R(NAME["勿"], "宽慰", NAME["格"], "放松些，你已经回家了"),
        R(NAME["格"], "致意", NAME["勿"], "向您致意，勿忘我先生"),
        R(NAME["格"], "躲入", NAME["棺椁"], "她颤抖着爬进了一个最近的棺椁"),
        R(NAME["芭"], "引路", NAME["匣"], "请大家牵紧彼此的手，跟着音乐的方向"),
        R(NAME["感客"], "敬佩", NAME["芭"], "您没有丢下我们"),
        R(NAME["忐客"], "疑虑", NAME["救生筏"], "那些救生筏的数量真的足够吗"),
        R(NAME["恍客"], "渴盼", NAME["自由海风号"], "我也希望能回到家乡看看"),
        R(NAME["图"], "让渡", NAME["救生艇"], "努库泰澳人愿意让出救生艇的名额"),
    ],
}

# ══ 21.0.1 拆解啪唧匣子为救生船 ══
BATCH["c8090ec4b41d3f8a7361f05b"] = {
    "entities": [
        E(NAME["芭"], "角色", "拆解爱器以救人的乐手"),
        E(NAME["图"], "角色", "惊问其举动的少女"),
        E(NAME["埃"], "角色", "被喊住的乘客"),
        E(NAME["惊客"], "角色", "惊讶其抛下绞弦琴者"),
        E(NAME["怀客"], "角色", "怀念该乐器者"),
        E(NAME["动客"], "角色", "感佩其伟大者"),
        E(NAME["匣"], "物品", "被举过头顶的啪唧匣子"),
        E(NAME["绞弦琴"], "物品", "她曾费尽工夫寻得的乐器"),
        E(NAME["救生艇"], "物品", "由乐器变形而成的救生船"),
        E(NAME["自由海风号"], "物品", "其名号不容辱没的游轮"),
    ],
    "relations": [
        R(NAME["芭"], "承诺", NAME["埃"], "“自由海风号”不会放弃任何一位乘客"),
        R(NAME["芭"], "举起", NAME["匣"], "她将背后的啪唧匣子举过了头顶"),
        R(NAME["图"], "惊问", NAME["芭"], "啪唧匣子不是你最引以为傲的"),
        R(NAME["芭"], "施术", NAME["匣"], "分解咔咔咒"),
        R(NAME["惊客"], "惊讶", NAME["绞弦琴"], "您居然抛下了这柄绞弦琴"),
        R(NAME["怀客"], "怀念", NAME["绞弦琴"], "离开加利西亚以后，我有多久没见着它了"),
        R(NAME["匣"], "化作", NAME["救生艇"], "它、它们变成了救生船"),
        R(NAME["动客"], "感佩", NAME["芭"], "您拯救了更多的人"),
    ],
}

# ══ 22.0.0 天亮雨停；暴雨未至 ══
BATCH["5d741a40ef64ec17efbf334e"] = {
    "entities": [
        E(NAME["芭"], "角色", "以小提琴托身、承认故乡者"),
        E(NAME["维"], "角色", "宣告成功的司辰"),
        E(NAME["乌"], "角色", "致贺并汇报结论的组长"),
        E(NAME["十"], "角色", "确认暴雨未至的助手"),
        E(NAME["星"], "角色", "欢呼天亮的海盗"),
        E(NAME["图"], "角色", "猜其曲调来源的少女"),
        E(NAME["琴"], "物品", "曾深藏匣中、化作小舟的小提琴"),
        E(NAME["匣"], "物品", "曾深藏小提琴的啪唧匣子"),
        E(NAME["克"], "地点", "其年轮紧密的好木与骄傲所系之地"),
        E(NAME["那不勒斯"], "地点", "曲调真正的来源地"),
        E(NAME["雨"], "概念", "并未到来的暴雨"),
        E(NAME["基金"], "组织", "直升机所属机构"),
        E(NAME["直升机"], "物品", "十四行诗望见的基金会直升机"),
        E(NAME["算"], "组织", "接受结项汇报的机构"),
    ],
    "relations": [
        R(NAME["琴"], "托起", NAME["芭"], "来自过去的小舟稳稳地托起了她"),
        R(NAME["芭"], "追忆", NAME["克"], "要为淘气的女儿制造一柄最特别的小提琴"),
        R(NAME["芭"], "承认", NAME["克"], "我从没离开过那儿，是么"),
        R(NAME["维"], "宣告", NAME["雨"], "我们成功了"),
        R(NAME["乌"], "致贺", NAME["维"], "恭喜你，司辰"),
        R(NAME["乌"], "汇报", NAME["算"], "我已经向科算中心汇报了这一结论"),
        R(NAME["十"], "确认", NAME["雨"], "“暴雨”并没有到来"),
        R(NAME["星"], "欢呼", NAME["维"], "哇啊——天亮了"),
        R(NAME["图"], "猜测", NAME["克"], "它一定和芭卡洛儿小姐一样，也来自克雷莫纳"),
        R(NAME["芭"], "更正", NAME["那不勒斯"], "这是那不勒斯的曲子"),
        R(NAME["十"], "望见", NAME["直升机"], "是基金会的直升机"),
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
        for e in blk["entities"]:
            if e["name"] in e["aliases"]:
                bad.append(f"{key}: {e['name']} 别名重复本体名")
            if len(e["desc"]) > 30:
                bad.append(f"{key}: {e['name']} desc 超 30 字")
    ne = sum(len(b["entities"]) for b in BATCH.values())
    nr = sum(len(b["relations"]) for b in BATCH.values())
    print(f"{len(BATCH)}/{len(BATCH)} 块通过｜实体 {ne}｜关系 {nr}")
    if bad:
        raise SystemExit("端点体检失败：\n  - " + "\n  - ".join(bad))
    print("端点体检通过：所有 src/dst 逐字命中同块 entities")


def _naming_check() -> None:
    banned_name = ["乌尔里希", "卡戎", "破译组长", "淑女格蕾丝", "拉普拉斯",
                   "拉普拉斯科算中心", "唱片", "神秘学唱片机", "努库泰澳",
                   "传单", "格蕾丝", "希曼", "客房", "卢卡斯", "甲板",
                   "毒箭", "助手小姐", "休息室", "意识唤醒者", "广播",
                   "琼斯", "通灵板", "前行者", "毛毛虫溶剂", "海上",
                   "救生船", "音乐", "镜子", "幽灵"]
    banned_any = ["别斯米尔", "玛尔塔", "兀尔德", "德洛丝", "卡卡尼亚",
                  "洛伦兹蝴蝶", "凯拉", "奇索斯镇", "安德烈", "Z女士",
                  "纸信圈儿", "宽檐帽", "福葛"]
    hits: list[str] = []
    for key, blk in BATCH.items():
        for e in blk["entities"]:
            if e["name"] in banned_name or e["name"] in banned_any:
                hits.append(f"{key}: name={e['name']}")
            for a in e["aliases"]:
                if a in banned_any:
                    hits.append(f"{key}: alias={a} @ {e['name']}")
    if hits:
        raise SystemExit("命名红线违反：\n  - " + "\n  - ".join(hits))
    print("命名红线自检通过：未使用任何受污染裸名")


def main() -> None:
    _audit()
    _naming_check()
    keys = [json.loads(l)["key"]
            for l in DUMP.read_text(encoding="utf-8-sig").splitlines() if l.strip()]
    assert len(keys) == len(BATCH), f"dump 块数 {len(keys)} != 生成块数 {len(BATCH)}"
    miss = [k for k in keys if k not in BATCH]
    extra = [k for k in BATCH if k not in keys]
    assert not miss and not extra, f"key 不匹配 miss={miss} extra={extra}"
    out = ROOT / "_agent_batch223.json"
    out.write_text(json.dumps(BATCH, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    print(f"已写出 {out.name}（{len(BATCH)} 块，key 与 dump 一一对应）")


if __name__ == "__main__":
    main()
