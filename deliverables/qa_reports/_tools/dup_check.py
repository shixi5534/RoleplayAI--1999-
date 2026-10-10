"""检测 tests/ 下重复定义的同名测试函数/类名 —— 后定义的会静默覆盖先定义的。

只读，零副作用。
"""
import ast
import collections
import pathlib

root = pathlib.Path(__file__).resolve().parents[3]
tests = root / "tests"

per_file = {}
dups_global = collections.defaultdict(list)

for p in sorted(tests.rglob("test_*.py")):
    if "__pycache__" in str(p):
        continue
    try:
        tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError as e:
        print("SKIP %s (%s)" % (p, e))
        continue
    # 收集本文件内 类->函数名
    seen = collections.defaultdict(list)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for sub in node.body:
                if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)) and sub.name.startswith("test"):
                    seen[(node.name, sub.name)].append(sub.lineno)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test"):
            seen[("<module>", node.name)].append(node.lineno)
    per_file[str(p.relative_to(root))] = seen
    for key, lines in seen.items():
        if len(lines) > 1:
            dups_global[key].append((str(p.relative_to(root)), lines))

print("=== 同一文件内重复定义的测试（会被静默覆盖） ===")
n = 0
for key, locs in sorted(dups_global.items()):
    for f, lines in locs:
        n += 1
        print("  DUP %s::%s  lines=%s  in %s" % (key[0], key[1], lines, f))
print("intra-file duplicates: %d" % n)

print()
print("=== 跨文件同名的测试类::方法（同一目录下不会互相覆盖，但便于发现复制粘贴） ===")
cross = collections.defaultdict(list)
for f, seen in per_file.items():
    for key in seen:
        cross[key].append(f)
m = 0
for key, files in sorted(cross.items()):
    if len(files) > 1 and key[0] != "<module>":
        m += 1
        if m <= 25:
            print("  %s::%s -> %s" % (key[0], key[1], ", ".join(files)))
print("cross-file same-name (class-scoped): %d" % m)

module_level = collections.defaultdict(list)
for f, seen in per_file.items():
    for key in seen:
        if key[0] == "<module>":
            module_level[key[1]].append(f)
mm = 0
for name, files in sorted(module_level.items()):
    if len(files) > 1:
        mm += 1
        if mm <= 25:
            print("  module-level test_%s -> %s" % (name, ", ".join(files)))
print("cross-file same-name (module-level, real shadow risk only if collected together w/o __init__.py): %d" % mm)
