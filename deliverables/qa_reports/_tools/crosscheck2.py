"""交叉核验剩余关键结论（numpy 归属 / custom_templates 崩溃 / 路径穿越 / token 泄漏）。只读。"""
import importlib.util
import inspect
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

print("=" * 74)
print("1) numpy 是否被 compendium_rag 顶层硬依赖（pyproject 只挂在 extras.emotion）")
try:
    src = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    in_deps = "numpy" in src.split("dependencies = [")[1].split("]")[0]
    in_emotion = "numpy" in src.split("emotion = [")[1].split("]")[0] if "emotion = [" in src else False
    print("   pyproject dependencies 含 numpy:", in_deps)
    print("   pyproject extras.emotion 含 numpy:", in_emotion)
    hits = []
    for p in (ROOT / "src" / "compendium_rag").rglob("*.py"):
        for i, ln in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            s = ln.strip()
            if s.startswith("import numpy") or s.startswith("from numpy"):
                hits.append((str(p.relative_to(ROOT)), i, s))
    print("   compendium_rag 内 numpy 顶层 import:")
    for h in hits:
        print("      %s:%d  %s" % h)
    print("   >>> %s" % ("[CONFIRMED] numpy 被顶层硬依赖，却是可选 extra"
                         if hits and not in_deps else "[需人工确认]"))
except Exception as e:  # noqa: BLE001
    print("   失败:", repr(e))

print()
print("=" * 74)
print("2) custom_templates 花括号 -> KeyError（正确签名）")
try:
    from roleplay.core.character_card import _render_field
    from roleplay.models.character import CharacterCard
    from roleplay.models.prompt_config import PromptConfig

    card = CharacterCard(name="T", personality="冷静")
    cfg = PromptConfig(custom_templates={"personality": "你是{name}，很冷静"})
    try:
        out = _render_field(card, "personality", cfg)
        print("   _render_field -> OK: %r" % (str(out)[:120],))
        print("   >>> [REFUTED] 未崩溃")
    except KeyError as e:
        print("   _render_field -> [CONFIRMED] KeyError(%s)" % e)
    except Exception as e:  # noqa: BLE001
        print("   _render_field -> %s: %s" % (type(e).__name__, str(e)[:150]))

    # persona_prompt 侧
    from roleplay.core.persona_prompt import resolve_system_prompt

    for label, tpl in (("{name} 花括号", "你是{name}"), ("{value} 正常", "你是{value}")):
        cfg2 = PromptConfig(custom_templates={"tone": tpl})
        try:
            out = resolve_system_prompt(character_card="卡片", fallback_prompt="兜底",
                                        prompt_config=cfg2)
            print("   persona_prompt [%s] -> OK" % label)
        except KeyError as e:
            print("   persona_prompt [%s] -> [CONFIRMED] KeyError(%s)" % (label, e))
        except Exception as e:  # noqa: BLE001
            print("   persona_prompt [%s] -> %s: %s" % (label, type(e).__name__, str(e)[:120]))
except Exception as e:  # noqa: BLE001
    print("   失败:", repr(e))

print()
print("=" * 74)
print("3) 路径穿越家族：trace_path / graph_store / plot_graph 清洗对比")
try:
    import roleplay.core.knowledge.retrieval_trace as RT

    print("   retrieval_trace.trace_path 源码:")
    for ln in inspect.getsource(RT.trace_path).splitlines():
        print("      ", ln.rstrip()[:120])
    print("   实测:")
    import tempfile
    base = Path(tempfile.mkdtemp(prefix="tp_"))
    for cid in ("ok_id", "..\\..\\..\\pwned", "../../x"):
        try:
            out = RT.trace_path(base, cid)
            esc = not str(out.resolve()).startswith(str(base.resolve()))
            print("      %-22r escaped=%s" % (cid, esc))
        except Exception as e:  # noqa: BLE001
            print("      %-22r EXC %s" % (cid, type(e).__name__))
except Exception as e:  # noqa: BLE001
    print("   失败:", repr(e))

print()
print("=" * 74)
print("4) QQ 重连日志是否泄漏 access_token")
try:
    import roleplay.channels.qq_onebot as Q

    src = inspect.getsource(Q)
    lines = [(i, ln.strip()) for i, ln in enumerate(src.splitlines(), 1)
             if "access_token" in ln or "str(exc)" in ln or "InvalidURI" in ln or "exc_info" in ln]
    for i, ln in lines[:14]:
        print("      L%-4d %s" % (i, ln[:130]))
    # 实测 InvalidURI 的 str()
    try:
        from websockets.exceptions import InvalidURI
        e = InvalidURI("ws://127.0.0.1:3001?access_token=SECRET123")
        print("   InvalidURI str() -> %s" % str(e)[:150])
        print("   >>> %s" % ("[CONFIRMED] token 出现在异常字符串里"
                             if "SECRET123" in str(e) else "[REFUTED]"))
    except Exception as e:  # noqa: BLE001
        print("   websockets 不可用或签名不同:", repr(e)[:120])
except Exception as e:  # noqa: BLE001
    print("   失败:", repr(e))
