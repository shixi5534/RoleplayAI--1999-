# -*- coding: utf-8 -*-
"""中配台词人工校正：对照英文原版修正听录错字，并规范标点。

校正依据：同一套台词的英配原文本（work/full_whole/full_whole.json）。
whisper 对游戏语音（带 BGM、耳语式念白）的同音字错误较多，靠中英对照修复。
"""
import json
import os
import re
import sys

# idx -> 校正后文本
CORRECTIONS = {
    1: "曾有一个人颤抖着找到我，对我说：救救我，Grace女士，我知道暴雨要来了。",
    2: "他很快就戴上了面具，可那天落下的只是一场再普通不过的雨，"
       "而我多希望自己当时能做出别的选择。",
    5: "也许有一天，我们能一起去那座岛上看看。我仍在习惯这种崭新的平静生活。",
    10: "那些餐点都很美味，而她看起来也很高兴能有一位味觉立场中立的品评测试员。",
    11: "我过去常常连续数日无法入睡。若不是趋光性定律不断复写我的大脑以维持机能，"
        "我想我早就疯了。",
    13: "这里的夜晚很安静，没有通宵达旦的晚宴和喋喋不休的阴谋。",
    17: "曾有一万七千六百零八条咒语留在我的脑海里。它们如今沉寂了，"
        "但伤痕还留在我的颅骨之下，也许有一天会重新生效。",
    19: "这把折扇常被人误认为是一支魔杖，而我也从未纠正过他们。",
    20: "其实我的神秘术并不需要这把扇子，它只是为了替我添几分淑女的仪态。",
    26: "我想，这也许只是旧习难改吧。但我仍在学着如何支配属于自己的时间。",
    27: "我仍在想，我们究竟怎样才能彻底击败阿卡纳？",
    37: "为了弥补神秘学家天生的缺陷，趋光性定律会在监测到强烈情绪波动时重置我的头脑。",
    39: "过去，每当人格被覆写，我的意识就会被关进一个小房间。"
        "那里四处散落着属于不同名字的遗物：Kayla与牛群的合照、"
        "Grace那些奇异的标本收藏、Newman伪造的车船票。"
        "我就用这些支离破碎的物件，从外面拼凑出自我的模样。",
    44: "那灼目的光，抽丝剥茧，翩然的死亡，飞蛾扑火，听鳞翅的震颤。"
        "在那无数谎言的帷幕之后，不必在意，我可以为你掩盖战斗留下的痕迹，"
        "或者让现场看起来像是一次意外事故，有需要的话，尽情吩咐。",
    45: "终于，那只长久被遗弃在黑暗角落里的飞蛾，也感受到了阳光的温暖。",
    46: "那些名字真正的主人已经逝去，而窃取了它们的小偷却获得了第二次生命。",
    47: "但愿我能带着那些破碎的名字，找回属于我自己的生命。",
}

# 同音字批量修正（先于整句替换，避免遗漏）
BATCH_FIX = [
    ("驱光性", "趋光性"),
    ("神秘书", "神秘术"),
    ("Kella", "Kayla"),
]


def norm_punct(t):
    """中文语境下半角标点转全角，英文人名/术语不动。"""
    t = re.sub(r"(?<=[\u4e00-\u9fff])\s*,\s*", "，", t)
    t = re.sub(r"(?<=[\u4e00-\u9fff])\s*\.\s*(?=[\u4e00-\u9fff]|$)", "。", t)
    t = re.sub(r"(?<=[\u4e00-\u9fff])\s*\?\s*", "？", t)
    t = re.sub(r"(?<=[\u4e00-\u9fff])\s*!\s*", "！", t)
    t = re.sub(r"(?<=[\u4e00-\u9fff])\s*:\s*", "：", t)
    # 分句会在词中间留下空格（如"身 份"），中文之间的空格一律去掉
    t = re.sub(r"(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])", "", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "work/zh_whole/zh_whole_clean.json"
    d = json.load(open(src, encoding="utf-8"))
    n_fix = 0
    for s in d["segments"]:
        text = s["text"]
        for a, b in BATCH_FIX:
            text = text.replace(a, b)
        if s["idx"] in CORRECTIONS:
            text = CORRECTIONS[s["idx"]]
            s["corrected"] = True
            n_fix += 1
        s["text"] = norm_punct(text)

    base = os.path.splitext(src)[0]
    out_json = base + "_final.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)

    out_md = base + "_final.md"
    segs = d["segments"]
    lines = ["# 无名者 · 中配语音台词（校正版）", "",
             f"- 源：{os.path.basename(d.get('source', ''))}"
             f" ｜ 段落：{len(segs)} ｜ 人工校正：{n_fix} 段", "",
             "| # | 起 | 止 | 台词 |", "|---:|---:|---:|---|"]
    for s in segs:
        t = (s["text"] or "").replace("|", "｜").replace("\n", " ")
        lines.append(f"| {s['idx']} | {s['start']:.2f} | {s['end']:.2f} | {t} |")
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"saved {out_json} / {out_md}（{len(segs)} 段，校正 {n_fix} 段）")
    for s in segs:
        mark = " [校]" if s.get("corrected") else ""
        print(f"{s['idx']:2d} {s['start']:6.2f} | {s['text']}{mark}")


if __name__ == "__main__":
    main()
