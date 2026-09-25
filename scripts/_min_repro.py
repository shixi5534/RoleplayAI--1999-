# -*- coding: utf-8 -*-
"""最小复现：逐步加载，每步落盘心跳，定位硬崩溃发生在哪一步。"""
from __future__ import annotations

import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
HB = ROOT / "data" / "knowledge" / "_audit" / "_minrepro.txt"
HB.write_text(f"start {time.strftime('%H:%M:%S')}\n", encoding="utf-8")


def beat(msg: str) -> None:
    with HB.open("a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%H:%M:%S')} {msg}\n")


try:
    beat("import eval_plot_rag 前")
    import eval_plot_rag as E  # noqa: E402

    beat("import eval_plot_rag 完成")

    from roleplay.config import get_settings  # noqa: E402

    beat("import get_settings 完成")

    from roleplay.core.knowledge.factory import build_plot_registry  # noqa: E402

    beat("import build_plot_registry 完成")

    s = get_settings()
    beat("get_settings() 完成")

    reg = build_plot_registry(s)
    beat(f"build_plot_registry() 完成 type={type(reg).__name__}")

    retr = reg.get("wu_ming_zhe")
    beat(f"get('wu_ming_zhe') 完成 type={type(retr).__name__}")

    graph = getattr(retr, "graph", None)
    beat(f"retr.graph = {type(graph).__name__}｜"
         f"has_link_detailed={hasattr(graph, 'link_detailed')}")
except BaseException:  # noqa: BLE001
    HB.write_text(HB.read_text(encoding="utf-8")
                  + "\n[TRACEBACK]\n" + traceback.format_exc(), encoding="utf-8")
    raise
