# -*- coding: utf-8 -*-
"""语音台词入库验收：确认新导入的台词能被语义检索命中。

用法（项目根目录）：
  python scripts/verify_voice_lore.py

判断标准：每条问题召回的 top-3 中，须出现至少一个期望关键词。
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from roleplay.config import get_settings  # noqa: E402
from roleplay.core.knowledge import (  # noqa: E402
    build_knowledge_base,
    lore_namespace,
)

CHARACTER_ID = "wu_ming_zhe"
DOC = "角色语音台词集"

# (问题, 期望关键词任一命中)
CASES: list[tuple[str, list[str]]] = [
    ("你怎么看待自己偷来的那些名字？",
     ["小偷", "第二次生命", "名字真正的主人"]),
    ("你脑子里曾经被植入过多少条咒语？",
     ["17,608", "一万七千六百零八", "咒语"]),
    ("没有光的时候，飞蛾会怎么样？",
     ["没有光", "自己选择方向", "飞蛾"]),
    ("你的人格被覆写的时候，会看到什么？",
     ["小房间", "Kayla", "人格被覆写"]),
    ("你的折扇常常被人当成什么？",
     ["魔杖", "折扇"]),
    ("战斗的时候你会怎么安慰对手？",
     ["痛苦不会持续太久", "闭上眼", "飞虫"]),
    ("你说过自己的故乡在哪里吗？",
     ["冰岛", "故乡"]),
    ("你为什么不愿意丢掉那些痛苦的记忆？",
     ["铭记", "抛弃", "属于我自己的生命"]),
]


async def main() -> int:
    s = get_settings()
    kb = build_knowledge_base(s)
    ns = lore_namespace(CHARACTER_ID)

    ok = 0
    for q, keys in CASES:
        hits = await kb.asearch(q, top_k=3, namespaces=[ns], hybrid=True)
        joined = "\n".join(h.text for h in hits)
        hit_keys = [k for k in keys if k in joined]
        from_voice = any(DOC in (h.metadata or {}).get("path", "")
                         or DOC in (h.metadata or {}).get("title", "")
                         for h in hits)
        status = "PASS" if hit_keys else "MISS"
        if hit_keys:
            ok += 1
        print(f"[{status}] {q}")
        print(f"       命中关键词={hit_keys}  来源台词集={from_voice}")
        for h in hits[:2]:
            src = (h.metadata or {}).get("title", "?")
            print(f"       · ({src}) {h.text[:70]}".replace("\n", " "))
        print()

    total = len(CASES)
    print(f"结果：{ok}/{total} 命中")
    return 0 if ok == total else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
