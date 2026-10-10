"""静态解析内部 import 图：找出指向不存在模块的 import（必然 ImportError）。

规则：
- roleplay.* -> 必须在 src/roleplay 下存在对应包/模块
- compendium_rag.* -> 必须在 src/compendium_rag 下存在
- from . import x / from .y import z 的相对导入 -> 必须在本包目录存在
只读，零副作用。
"""
import ast
import pathlib

root = pathlib.Path(__file__).resolve().parents[3]
SRC = root / "src"
roots = {"roleplay": SRC / "roleplay", "compendium_rag": SRC / "compendium_rag"}

TARGETS = []
for name, base in roots.items():
    for d in base.rglob("*"):
        s = str(d)
        if "__pycache__" in s:
            continue
        TARGETS.append(d)
# tests 也纳入（它们 import 的方式能反映包结构问题）
for d in (root / "tests").rglob("*.py"):
    if "__pycache__" not in str(d):
        TARGETS.append(d)


def exists_module(pkg_base: pathlib.Path, dotted: str) -> bool:
    """dotted 相对 pkg_base 的包/模块是否存在"""
    cur = pkg_base
    parts = dotted.split(".")
    for i, part in enumerate(parts):
        cand_mod = cur / (part + ".py")
        cand_pkg = cur / part
        if cand_mod.exists():
            return i == len(parts) - 1
        if cand_pkg.is_dir() and (cand_pkg / "__init__.py").exists():
            cur = cand_pkg
            continue
        return False
    return True


problems = []
checked = 0

for p in TARGETS:
    if not p.is_file() or p.suffix != ".py":
        continue
    try:
        tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
    except Exception:  # noqa: BLE001, S112
        continue

    # 判定本文件所属根的 base
    s = str(p)
    pkg_base = None
    top_pkg = None
    if "\\src\\roleplay\\" in s or s.startswith(str(SRC / "roleplay")):
        pkg_base = SRC / "roleplay"
        top_pkg = "roleplay"
    elif "\\src\\compendium_rag\\" in s:
        pkg_base = SRC / "compendium_rag"
        top_pkg = "compendium_rag"

    pkg_dir = p.parent
    level0_base = pkg_dir

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.level and node.level > 0:
                # 相对导入
                if pkg_base is None:
                    continue
                base = pkg_dir
                for _ in range(node.level - 1):
                    base = base.parent
                target = node.module
                if target is None:
                    continue  # from . import x -> x 可以是子模块或属性，宽松放行
                if not exists_module(base, target):
                    problems.append((str(p.relative_to(root)), node.lineno,
                                     "." * node.level + (target or "")))
                checked += 1
            elif node.module:
                top = node.module.split(".")[0]
                if top in roots:
                    rest = ".".join(node.module.split(".")[1:])
                    ok = True
                    if rest:
                        ok = exists_module(roots[top], rest)
                    if not ok:
                        problems.append((str(p.relative_to(root)), node.lineno, node.module))
                    checked += 1
        elif isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".")[0]
                if top in roots:
                    rest = ".".join(alias.name.split(".")[1:])
                    ok = True
                    if rest:
                        ok = exists_module(roots[top], rest)
                    if not ok:
                        problems.append((str(p.relative_to(root)), node.lineno, alias.name))
                    checked += 1

print("internal imports checked: %d" % checked)
print("unresolvable internal imports: %d" % len(problems))
for f, ln, mod in sorted(set(problems))[:60]:
    print("  MISSING %s:%s -> %s" % (f, ln, mod))
