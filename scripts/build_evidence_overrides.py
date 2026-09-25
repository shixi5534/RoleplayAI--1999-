# -*- coding: utf-8 -*-
"""生成证据组 override 清单（不改题集，供评测增量口径使用）。

来源：docs/题集证据组复核.md（2026-09-16 逐题复核 43 道多组失分题）

处置三类：
  A. 冗余辅助组（39 题）→ keep 只保留答案组，drop 其余
  B. 分组有误（2 题）→ 答案在辅助组，交换 keep/drop
  C. 辅助组必要（2 题）→ 不写入（保持原口径）

产出：data/knowledge/_audit/evidence_overrides.json
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "knowledge" / "_audit" / "evidence_overrides.json"

# A 类：冗余辅助组 → 只保留第 0 组（答案组）
REDUNDANT = {
    "R002": "辅助组 Rockin 是船名，问『女性是谁』与船名无因果",
    "R003": "辅助组 Sotheby/苏芙比来自船上点唱机歌名《Please Please Sotheby》，源剧情无苏芙比（用户确认）",
    "R006": "辅助组 Sotheby/Regulus 是共现角色，问单角色英文名",
    "R008": "辅助组 Regulus/星锑 是共现角色，问『Zero 对应数字几』",
    "R009": "辅助组 Sotheby/Regulus 共现，问牙仙英文名",
    "R011": "辅助组 ship/Rockin 是载具，与答案无因果",
    "R014": "辅助组 Sotheby/Regulus/Rockin 共现，问篇章名",
    "R026": "辅助组 Vienna/维也纳 为题面已给的篇章信息",
    "R028": "辅助组 Vienna/维也纳 为题面已给",
    "R030": "辅助组 Vienna/维也纳 为题面已给",
    "R032": "辅助组 Vienna/维也纳 是场景非答案（问的是篇章名）",
    "R035": "辅助组 Kakania/卡卡尼亚 为人物，与『维也纳的英文』无关",
    "R036": "辅助组 Vienna/维也纳 为题面已给",
    "R037": "辅助组 Heinrich/海因里希 为线索人物非答案",
    "R041": "辅助组 Apeiron/阿派朗 为题面已给地点",
    "R043": "辅助组 37 为人物，与『乌尔里希英文名』无关",
    "R045": "辅助组 Apeiron/阿派朗 为地点，问的是数字",
    "R053": "辅助组 Manus/重塑之手 为题面已给",
    "R057": "辅助组 2007 为年份线索，问的是岛屿",
    "R058": "辅助组 vacuum 为题面已给的线索（真空弹）",
    "R059": "辅助组 Apeiron/阿派朗 为地点，问的是人物",
    "R060": "辅助组 37 为人物，问的是年份",
    "R061": "辅助组 troll/巨怪 为怪物，问的是营地",
    "R062": "辅助组 Green Lake/camp 为地点（题面已给），问的是怪物",
    "R063": "辅助组 Green Lake/camp 为题面已给地点",
    "R067": "辅助组 Green Lake/camp 为题面已给地点",
    "R069": "辅助组 woods/forest/森林 为地点，问的是怪物",
    "R074": "辅助组 Green Lake/camp 为题面已给地点与年份",
    "R134": "辅助组 Antarctica/南极 为地点，问的是人物英文名",
    "R183": "辅助组 Sonnet/十四行诗 为他人，与答案无关",
    "R184": "辅助组 Sotheby/苏芙比 为他人，问星锑英文名",
    "R185": "辅助组 Regulus/星锑 为他人，问苏芙比英文名",
    "R203": "辅助组 vampire 为题面线索，问的是篇章名",
    "R274": "辅助组 Ulu/和平乌鲁 为题面已给的同框人物",
    "R276": "辅助组 purifier/净化 为题面已给（净化机）",
    "R289": "辅助组 Matilda/玛蒂尔达 为题面已给（同学）",
    "R292": "辅助组 Heinrich/海因里希 为线索人物非答案",
}

# B 类：分组有误（答案在辅助组）→ 交换 keep/drop
SWAPPED = {
    "R055": "答案 Apeiron/阿派朗 被放进辅助组，道具 scroll/卷轴 反成主组；交换",
    "R068": "答案 1971 被放进辅助组，怪物 troll/巨怪 反成主组；交换",
}

# C 类：辅助组必要，保持原口径（仅记录，不产生 override）
KEPT = {
    "R089": "列举题『岛民都有谁』，需枚举多名岛民，辅助组必要",
    "R204": "关系题，关系另一端（阿尔卡纳）是必要证据",
}

# ---- 第二轮（2026-09-16 补做）：未失分的 37 道多组题 ----
# 这些题原本就通过全组口径（碰巧覆盖了冗余组），补 record 只为基准一致，
# 不改变任何指标。判据同第一轮：题面已给 / 与答案无因果 → 冗余。
REDUNDANT_2 = {
    "R012": "辅助组 Rockin（船名）题面已给『摇滚苹果号』",
    "R017": "辅助组 fog/雾 题面已给『雾中女巫』",
    "R024": "辅助组 Vienna/维也纳 为章节上下文",
    "R025": "辅助组 Vienna/维也纳 为章节上下文",
    "R031": "辅助组 Vienna/维也纳 为章节上下文",
    "R033": "辅助组 Isolde/伊索尔德 为他人，问海因里希英文名",
    "R034": "辅助组 Heinrich/海因里希 为他人，问伊索尔德英文名",
    "R040": "辅助组 Vienna/维也纳 题面已给",
    "R042": "辅助组 Manus/重塑之手 为背景组织",
    "R054": "辅助组 Arcana/阿尔卡纳 为背景人物",
    "R064": "辅助组 Green Lake/camp 题面已给『绿湖噩梦篇』",
    "R065": "辅助组 Green Lake/camp 题面已给",
    "R066": "辅助组 Green Lake/camp 题面已给",
    "R078": "辅助组 Green Lake/camp 题面已给『绿湖营地』",
    "R080": "辅助组 Green Lake/camp 题面已给",
    "R085": "辅助组 C07/神秘警探 题面已给《神秘警探C07》",
    "R090": "辅助组 中央塔/自囚 题面已给",
    "R230": "辅助组 Ryashki 题面已给『来亚什基』",
    "R275": "辅助组 games/运动会 题面已给",
    "R277": "辅助组 vampire 题面已给『吸血鬼』",
    "R281": "辅助组 Storm/暴雨 题面已给",
    "R284": "辅助组 Manus/重塑之手 为干扰项（答案为 Arcana）",
    "R285": "辅助组 Storm/暴雨 题面已给",
    "R290": "辅助组 Foundation/基金会 题面已给『基金会间谍』",
}
SWAPPED_2 = {
    "R023": "答案『伊索尔德』在辅助组、题面实体『海因里希』占了主组；交换",
    "R070": "答案『绿湖营地』在辅助组、题面词『灯塔』占了主组；交换",
    "R228": "答案『Melania』在辅助组、题面实体『拉米雷斯』占了主组；交换",
    "R295": "答案『暴雨』在辅助组、题面词『1999』占了主组；交换",
}
KEPT_2 = {
    "R049": "『X 与 Y 同属哪个篇章』——两实体均为定位线索",
    "R050": "同上（阿德勒与乌尔里希）",
    "R051": "同上（Six 与 37）",
    "R075": "题面『Horropedia 与 Jessica』双实体",
    "R081": "答案含两要素（乌卢鲁圣火＋本体 Ulu），两组均必要",
    "R205": "题面『勿忘我与斯奈德』双实体",
    "R206": "题面含『淑女格蕾丝』与章节『77』，均为定位",
    "R229": "题面『Melania 与 Pickles』双实体",
    "R273": "辅助组 Vila/维拉 即题面『少女教师』，为定位线索",
}


def main() -> int:
    overrides: dict[str, dict] = {}
    for qid, reason in {**REDUNDANT, **REDUNDANT_2}.items():
        overrides[qid] = {"keep_groups": [0], "drop_groups": [1], "reason": reason,
                          "round": 1 if qid in REDUNDANT else 2}
    for qid, reason in {**SWAPPED, **SWAPPED_2}.items():
        overrides[qid] = {"keep_groups": [1], "drop_groups": [0], "reason": reason,
                          "round": 1 if qid in SWAPPED else 2}

    payload = {
        "meta": {
            "tool": "scripts/build_evidence_overrides.py",
            "created": "2026-09-16",
            "source": "docs/题集证据组复核.md",
            "note": "不改动题集 rag_testset_300.json；评测脚本读本文件产出『主组口径』指标，"
                    "与『全组口径』并列报告。",
            "counts": {
                "round1_redundant": len(REDUNDANT),
                "round1_swapped": len(SWAPPED),
                "round2_redundant": len(REDUNDANT_2),
                "round2_swapped": len(SWAPPED_2),
                "kept_as_is": len(KEPT) + len(KEPT_2),
            },
        },
        "overrides": overrides,
        "kept_as_is": {**KEPT, **KEPT_2},
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[overrides] 写入 {len(overrides)} 题 → {OUT.relative_to(ROOT)}")
    print(f"[overrides] 冗余剔除 {len(REDUNDANT)+len(REDUNDANT_2)}｜分组交换 {len(SWAPPED)+len(SWAPPED_2)}｜保持原样 {len(KEPT)+len(KEPT_2)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
