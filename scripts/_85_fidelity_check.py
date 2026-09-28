# -*- coding: utf-8 -*-
"""保真度校验：离线模拟的 lex_first=3 up/down 题号必须与官方 eval 工件逐题一致。

若不一致，后续所有变体结论都不可信。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path("data/compendium_rag/reports")

OFFICIAL = {
    "300cn": {
        "down": "R030 R043 R073 R080 R183 R242 R263".split(),
        "up": "R018 R052 R231 R241 R251 R268 R286".split(),
        "eval_v6": "eval_300cn_lex_tiebreak.json",
        "eval_lf": "eval_300cn_lexfirst.json",
        "variants": "_85_lexfirst_variants.json",
    },
    "blind": {
        "eval_v6": "eval_blind_lex_tiebreak.json",
        "eval_lf": "eval_blind_lexfirst.json",
        "variants": "_85_lexfirst_variants.json",
    },
}


def eval_hits(fname):
    d = json.loads((R / fname).read_text(encoding="utf-8"))
    return {r["qid"] for r in d["rows"]
            if r.get("mode") == "full" and r.get("answerable") and r.get("hit")}


def main() -> int:
    for setname, cfg in OFFICIAL.items():
        v6 = eval_hits(cfg["eval_v6"])
        lf = eval_hits(cfg["eval_lf"])
        off_up, off_dn = sorted(lf - v6), sorted(v6 - lf)
        print(f"\n[{setname}] 官方 eval: v6={len(v6)} lf={len(lf)} up={len(off_up)} dn={len(off_dn)}")
        print(f"  官方 up={off_up}")
        print(f"  官方 dn={off_dn}")

        V = json.loads((R / cfg["variants"]).read_text(encoding="utf-8"))["results"]
        sim = [r for r in V if r["tag"] == "V3 lexfirst L=3"][0]
        if setname == "300cn":
            sim_up, sim_dn = sim["up300_ids"], sim["dn300_ids"]
        else:
            sim_up, sim_dn = sim["upblind_ids"], sim["dnblind_ids"]
        print(f"  模拟 up={sorted(sim_up)}")
        print(f"  模拟 dn={sorted(sim_dn)}")
        ok = sorted(sim_up) == off_up and sorted(sim_dn) == off_dn
        print(f"  ==> {'PASS 逐题一致' if ok else 'FAIL 不一致'}")

    if "down" in OFFICIAL["300cn"]:
        got = OFFICIAL["300cn"]["down"]
        print(f"\n[交叉] 任务给定 LOST7 = {got}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
