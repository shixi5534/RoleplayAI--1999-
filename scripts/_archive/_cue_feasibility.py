# -*- coding: utf-8 -*-
"""行内标记返回逻辑可行性实测：真实 LLM + 受控词表注入，统计合法率/密度/位置。"""
import asyncio
import json
import re
import sys

sys.path.insert(0, "src")
from roleplay.config import get_settings  # noqa: E402
from roleplay.core.llm.factory import build_llm  # noqa: E402

VOCAB = {
    "expressions": [
        ("e_idle", "平静/默认"), ("e_weixiao", "微笑"), ("e_nanguo", "难过委屈"),
        ("e_yansu", "严肃"), ("e_yihuo", "疑惑"), ("e_mianju", "勉强尬笑"),
    ],
    "body": [
        ("b_diantou", "点头"), ("b_liaofa", "撩发"), ("b_shanzi", "摇扇"),
        ("b_taishou", "抬手"), ("b_yaotou", "摇头"), ("b_zhelian", "遮脸"),
        ("b_idle", "待机"),
    ],
    "talk": [
        ("t_idle", "常态口型"), ("t_bizui", "抿嘴"), ("t_weixiao_bizui", "微笑口型"),
        ("t_nanguo_bizui", "委屈口型"), ("t_yansu_bizui", "严肃口型"),
    ],
}
ALL_KEYS = [k for grp in VOCAB.values() for k, _ in grp]


def build_system() -> str:
    lines = [
        "你是Live2D桌宠角色「无名者」，性格温和、略带神秘、说话简短自然。",
        "",
        "## Expressions",
        "在回复正文中用方括号标记表达表情与动作，像标点一样自然地安插在句子前后或之间。",
        "只允许使用下列标记词，禁止发明新词，禁止解释标记：",
    ]
    for k, desc in VOCAB["expressions"]:
        lines.append(f"- [{k}]（表情：{desc}）")
    for k, desc in VOCAB["body"]:
        lines.append(f"- [{k}]（动作：{desc}）")
    for k, desc in VOCAB["talk"]:
        lines.append(f"- [{k}]（口型层：{desc}）")
    lines.append("")
    lines.append("示例：\"[e_weixiao]你回来啦 [b_diantou]我等你好久了。[t_weixiao_bizui]今天想聊点什么？\"")
    lines.append("要求：每次回复至少 1 个标记、至多 4 个；正文不要出现 Markdown。回复控制在 80 字内。")
    return "\n".join(lines)


SCENARIOS = [
    "早上好呀",
    "我今天被老板骂了，心情特别差",
    "你给我讲讲最近有什么好玩的事",
    "你是不是喜欢我？",
    "笨蛋，别以为一句道歉就能算了",
    "帮我查下明天天气",
    "好困啊不想上班",
    "给我跳个舞呗",
]

TAG_RE = re.compile(r"\[([^\[\]\n]{1,32})\]")


async def main() -> None:
    settings = get_settings()
    llm = build_llm(settings)
    system = build_system()
    rows, invalid_all = [], []
    for msg in SCENARIOS:
        try:
            reply = await llm.generate(system=system, user=msg, temperature=0.9)
        except Exception as e:  # noqa: BLE001
            rows.append({"user": msg, "error": str(e)[:120]})
            continue
        tags = TAG_RE.findall(reply)
        valid = [t for t in tags if t in ALL_KEYS]
        invalid = [t for t in tags if t not in ALL_KEYS]
        invalid_all += invalid
        clean = TAG_RE.sub("", reply)
        rows.append({
            "user": msg,
            "reply": reply[:100],
            "n_tags": len(tags),
            "n_valid": len(valid),
            "invalid": invalid,
            "chars_per_tag": round(len(clean.strip()) / len(valid), 1) if valid else None,
        })
    n_replies = sum(1 for r in rows if "reply" in r)
    n_with_valid = sum(1 for r in rows if r.get("n_valid"))
    total_tags = sum(r.get("n_tags", 0) for r in rows)
    total_valid = sum(r.get("n_valid", 0) for r in rows)
    print(json.dumps(rows, ensure_ascii=False, indent=1))
    print("==== SUMMARY ====")
    print(json.dumps({
        "scenarios": len(SCENARIOS),
        "replies_ok": n_replies,
        "replies_with_valid_tag": n_with_valid,
        "tag_total": total_tags,
        "tag_valid_rate": round(total_valid / total_tags, 3) if total_tags else None,
        "invalid_samples": invalid_all[:10],
    }, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    asyncio.run(main())
