# -*- coding: utf-8 -*-
"""回填块「未落地实体」修复（408 块回填的收尾质检）。

背景：408 块空抽取由人工逐块补抽写入抽取缓存。审计规则
``hallucinated_entity`` 要求实体正名或其别名必须作为子串出现在正文里，
逐块复核 1650 个回填实体后，有 32 个未落地，分两类处理：

1. **补别名**（13 个）：实体语义确实存在于正文，只是我当时写的是中文译名，
   没带上正文里的表层形式（含单复数、西语原文、被插入词打断的短语）。
   补上表层形式即可落地。
2. **删除**（16 个 + 关联关系）：正文里根本没有对应词，属于我把场景隐含信息
   （学校 / 战场 / 吸血鬼 / 咒语 / 项目 / 收容 / 争夺 / 集合 / 幻觉 / 人类 …）
   写成了实体，违反「只抽取文本中明确出现」的保守原则。连同引用它的关系一并删除，
   避免图中出现无据节点。

被删实体所在的块经核对均仍保留其余实体与关系，不会退化为 ``empty``。

用法（项目根目录）：
  python scripts/fix_backfill_grounding.py            # 预演
  python scripts/fix_backfill_grounding.py --apply     # 写盘
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "knowledge" / "plot_cache" / "wu_ming_zhe"

# hash -> {"add_alias": {实体名: [新增别名]}, "del_entities": [实体名]}
FIX: dict[str, dict] = {
    # ---------- 1. 补别名：正文有对应表层形式 ----------
    "23c49ac71d50d1f6": {"add_alias": {"太空": ["espacio"]}},  # 西语 flotando en el espacio
    "23d22d6ef61e9252": {"add_alias": {"庄稼": ["farming"]}},  # farming season / nothing to farm
    "32bf6d82db79fe74": {"add_alias": {"团结": ["become one"]}},  # lock them together they become one
    "52ff2f1fa83d3843": {"add_alias": {"未知之物": ["Whatever it is"]}},  # whatever it is that hides
    "62a9ef41a53cf43f": {"add_alias": {"落星": ["stars"]}},  # the stars ... could fall into our world
    "7b03116fb175380b": {"add_alias": {"乘客": ["passenger"]}},  # 正文为单数 next passenger
    "a19938eae1788910": {"add_alias": {"求婚": ["propose"]}},  # when it's used to propose
    "a1b6b205600929d4": {"add_alias": {"身份置换": ["identities were displaced"]}},  # 原短语被 were 打断
    "b8c4275b6da197ad": {"add_alias": {"记忆": ["memories"]}},  # I didn't share those memories
    "bfc6cba28b925839": {"add_alias": {"联络": ["联系"]}},  # 正文作「联系」
    "e8b17c3538b3563a": {"add_alias": {"神圣历": ["sacred and solar calendars"]}},  # 原文为并列短语
    "f0cc034102eb2077": {"add_alias": {"占卜师": ["diviner"]}},  # 正文为单数 every diviner
    "fad253ca4735805f": {"add_alias": {"通用语言": ["idioma"]}},  # 西语 un idioma

    # ---------- 2. 删除：正文无对应词，属场景隐含信息外推 ----------
    "024c568a67a6e244": {"del_entities": ["学校"]},  # 正文只有 students / beloved place，无 school
    "0d0b5770e20918e1": {"del_entities": ["崩塌"]},  # 正文为 old order has been shattered
    "35bc0bdab916d8f0": {"del_entities": ["工地"]},  # 正文为 work / dome / concrete，无 site
    "72afa70c6e7b91fe": {
        "add_alias": {"花": ["bloomed"]},  # these are the ones that bloomed the best
        "del_entities": ["种子"],  # 本块无 seed（seed 在另一块）
    },
    "8a34c95c316e7d85": {"del_entities": ["咒语"]},  # 中文巡神块，正文无「咒语」
    "908f4648bc5ab6f5": {"del_entities": ["战场"]},  # 一战回忆，正文无 battlefield
    "92bdf40393d62e33": {"del_entities": ["吸血鬼"]},  # 正文为 blood / graves / monsters
    "97197fd8966722f1": {"del_entities": ["杂技演员", "观众"]},  # 正文无 acrobat / audience
    "a424a7c39d3829bb": {"del_entities": ["项目"]},  # 正文无 project
    "c5558af855d0dd89": {"del_entities": ["集合"]},  # 正文为 dismissed / launch bay doors
    "d2c743dce6f8e832": {"del_entities": ["争夺"]},  # 正文为 no reason to fight
    "d9ddbb7c322dc1ae": {"del_entities": ["项目"]},  # 正文无 project
    "debb865684d77bc7": {"del_entities": ["项目"]},  # 正文无 project
    "e32814318123093a": {"del_entities": ["收容"]},  # 正文为 let one man in / manpower
    "ee0168ea471df5cd": {
        # ASR 把 Manus Vindictae 读成 "many's vindictive"，补 ASR 表层形式
        "add_alias": {"重塑之手": ["vindictive"]},
        "del_entities": ["人类"],  # 正文为 family and friends / we
    },
    "f0e441cc76349144": {"del_entities": ["幻觉"]},  # 正文为 storm syndrome
}


def main() -> int:
    apply = "--apply" in sys.argv
    n_alias = n_del_e = n_del_r = 0
    missing: list[str] = []
    for h, spec in FIX.items():
        path = CACHE / f"{h}.json"
        if not path.exists():
            missing.append(h)
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        add_alias: dict[str, list[str]] = spec.get("add_alias") or {}
        del_ents: set[str] = set(spec.get("del_entities") or [])

        for e in data.get("entities") or []:
            for extra in add_alias.get(str(e.get("name") or ""), []):
                aliases = [str(a) for a in (e.get("aliases") or [])]
                if extra not in aliases:
                    aliases.append(extra)
                    n_alias += 1
                e["aliases"] = aliases

        if del_ents:
            before = len(data.get("entities") or [])
            data["entities"] = [
                e for e in (data.get("entities") or [])
                if str(e.get("name") or "") not in del_ents
            ]
            n_del_e += before - len(data["entities"])
            rels = data.get("relations") or []
            kept = [
                r for r in rels
                if str(r.get("src") or "") not in del_ents
                and str(r.get("dst") or "") not in del_ents
            ]
            n_del_r += len(rels) - len(kept)
            data["relations"] = kept
            if not data["entities"] and not data["relations"]:
                print(f"[warn] {h} 修复后为空块")

        if apply:
            path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
            )

    print(
        f"[grounding] {'已写盘' if apply else '预演'}："
        f"补别名 {n_alias} 条，删实体 {n_del_e} 个，删关系 {n_del_r} 条"
    )
    if missing:
        print(f"[grounding] 缓存缺失：{missing}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
