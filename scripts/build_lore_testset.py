# -*- coding: utf-8 -*-
"""构建 lore 层小型评测集（长期跟踪用）。

题源（2026-09-16 新建）：
    lore 库里 45 个中文设定条目自带「常被问到：…？」句式——这些问题是**条目设计者
    预设的典型提问**，天然贴合作答用途。从中抽取 136 条，作为 lore 层检索评测集。

判定设计（两级，主判定客观、辅助判定容错）：
    主判定 id_hit  ：检索 top-k 里是否出现**源条目本身**（id 精确匹配）
    辅助判定 key_hit：返回块正文是否含该题的关键实体词（容忍同主题的其它条目）

用法：
    .venv/Scripts/python.exe -X utf8 scripts/build_lore_testset.py
产出：
    data/knowledge/_audit/lore_testset.json
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LORE = ROOT / "data" / "knowledge" / "lore_wu_ming_zhe.json"
OUT = ROOT / "data" / "knowledge" / "_audit" / "lore_testset.json"

QW = ("是什么", "是谁", "为什么", "在哪里", "哪儿", "怎么", "哪些", "多少", "几", "什么", "谁")
PAT = re.compile(r"常被问到[：:]\s*([^\n]*)")
# 条目标题形如：【世界观：暴雨、基金会、阵营与时代 > 一、暴雨（The Storm）】
#          或 【核心名词速查 > 暴雨】
#          或 【相关角色档案（无名者互动对象） > 九、十四行诗（Sonetto）】
# 取「> 之后的序号+中文名」作为关键实体词
TITLE_TAIL = re.compile(r"[>》]\s*(?:[一二三四五六七八九十百]+[、.．]\s*)?([\u4e00-\u9fff]{2,10})")


def extract_questions(text: str) -> list[str]:
    m = PAT.search(text or "")
    if not m:
        return []
    out = []
    for seg in re.split(r"[？?]", m.group(1)):
        s = seg.strip().strip("。，,、；; ")
        if not s or len(s) > 30:
            continue
        if not any(w in s for w in QW):
            continue
        if any(c in s for c in ("来源：", "http", "百度百科")):
            continue
        out.append(s + "？")
    return out


def key_of(text: str) -> list[str]:
    """从条目标题提取关键实体词（用于容错判定 key_hit）。"""
    STOP = {"常被问到", "来源", "相关角色", "世界观", "核心名词速查", "剧情脉络",
            "对话场景示例", "剧情入坑必看", "角色档案", "名词速查", "简介", "总览"}
    keys: list[str] = []
    head = (text or "").strip()[:60]
    for m in TITLE_TAIL.finditer(head):
        k = m.group(1).strip()
        if 2 <= len(k) <= 10 and k not in STOP and k not in keys:
            keys.append(k)
    return keys[:3]


def main() -> int:
    lore = json.loads(LORE.read_text(encoding="utf-8"))
    items: list[dict] = []
    for e in lore:
        text = str(e.get("text") or "")
        qs = extract_questions(text)
        if not qs:
            continue
        keys = key_of(text)
        # 内容指纹：RetrievedChunk 无 id 字段（只有 metadata/score/text），
        # 故用源条目正文前 60 字的归一化片段作为"是否召回源条目"的判据。
        fp = " ".join(text.split())[:60]
        for q in qs:
            items.append({
                "q": q,
                "src_id": e.get("id"),
                "src_keys": keys,
                "src_fp": fp,
                "src_title": text[:40].replace("\n", " "),
            })
    payload = {
        "meta": {
            "tool": "scripts/build_lore_testset.py",
            "created": "2026-09-16",
            "purpose": "lore 层检索长期跟踪（小评测集）",
            "source": "lore 条目自带「常被问到」句式",
            "cases": len(items),
            "source_entries": len({it["src_id"] for it in items}),
            "note": "主判定 id_hit（召回源条目）；辅助判定 key_hit（含关键实体词）",
        },
        "cases": items,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[testset] 出题条目 {payload['meta']['source_entries']}｜题目 {len(items)} 条")
    print(f"[testset] → {OUT.relative_to(ROOT)}")
    for it in items[:5]:
        print(f"   {it['q']}  ← {it['src_id']} keys={it['src_keys']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
