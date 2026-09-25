import importlib.util, sys
spec = importlib.util.spec_from_file_location("p37", "C:/Users/Lenovo/WorkBuddy/2026-07-27-16-45-03/roleplay-ai/scripts/apply_missing_p37.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

v = m.validate()
land = m.landing()
ne = sum(len(d.get("entities") or []) for d in m.RESULTS.values())
nr = sum(len(d.get("relations") or []) for d in m.RESULTS.values())
# also detect name==alias duplicates and single-char names
issues = []
for h, d in m.RESULTS.items():
    for e in d.get("entities") or []:
        nm = e.get("name") or ""
        als = e.get("aliases") or []
        if nm in als:
            issues.append(f"name-in-alias {h} {nm}")
        if len(nm) <= 1:
            issues.append(f"single-char-name {h} {nm}")
lines = []
lines.append(f"BLOCKS={len(m.RESULTS)} DANGLING={v} UNLANDED={land} ENTITIES={ne} RELATIONS={nr}")
lines.append("NAME_ISSUES=" + (";".join(issues) if issues else "NONE"))
open("C:/Users/Lenovo/WorkBuddy/2026-07-27-16-45-03/roleplay-ai/scripts/_p37_check.txt", "w", encoding="utf-8").write("\n".join(lines) + "\n")
