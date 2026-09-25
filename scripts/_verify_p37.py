import importlib.util, json, os
from pathlib import Path
ROOT = "C:/Users/Lenovo/WorkBuddy/2026-07-27-16-45-03/roleplay-ai"
spec = importlib.util.spec_from_file_location("p37", ROOT + "/scripts/apply_missing_p37.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
CACHE = Path(ROOT) / "data/knowledge/plot_cache/wu_ming_zhe"
written = ok = mismatch = 0
for h, d in m.RESULTS.items():
    fp = CACHE / f"{h}.json"
    if not fp.exists():
        print("MISSING", h); continue
    written += 1
    cur = json.loads(fp.read_text(encoding="utf-8"))
    if cur.get("entities") == d.get("entities") and cur.get("relations") == d.get("relations"):
        ok += 1
    else:
        mismatch += 1
        print("MISMATCH", h)
# sample
sample = CACHE / "c72bcd320fbf4c4e.json"
open(ROOT + "/scripts/_p37_apply.txt", "w", encoding="utf-8").write(
    f"WRITTEN={written} MATCH={ok} MISMATCH={mismatch}\n\nSAMPLE c72:\n" + sample.read_text(encoding="utf-8")
)
