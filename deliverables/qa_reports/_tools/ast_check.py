"""全仓 Python 语法体检（只读，零副作用）。"""
import ast
import pathlib

root = pathlib.Path(__file__).resolve().parents[3]
bad = []
count = 0
locs = {}

for p in root.rglob("*.py"):
    s = str(p)
    if "node_modules" in s or "\\.venv\\" in s or "__pycache__" in s:
        continue
    try:
        src = p.read_text(encoding="utf-8")
    except Exception as e:  # noqa: BLE001
        bad.append((s, "read-error: %s" % e))
        continue
    try:
        ast.parse(src, filename=s)
    except SyntaxError as e:
        bad.append((s, "line %s: %s" % (e.lineno, e.msg)))
        continue
    count += 1
    locs[s] = len(src.splitlines())

print("parsed_ok=%d" % count)
print("syntax_errors=%d" % len(bad))
for f, m in bad[:60]:
    print("ERR %s | %s" % (f, m))
print("total_py_lines=%d" % sum(locs.values()))
for f, n in sorted(locs.items(), key=lambda kv: -kv[1])[:15]:
    print("BIG %8d %s" % (n, f))
