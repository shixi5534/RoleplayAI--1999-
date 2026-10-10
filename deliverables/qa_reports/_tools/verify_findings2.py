"""第二轮独立复现：修正调用签名（上一轮 3 个 REFUTED 是我脚本签名写错）。

只读，全部在临时目录进行。
"""
import inspect
import os
import sys
import tempfile
from pathlib import Path

_t = Path(tempfile.mkdtemp(prefix="verify2_"))
for k, v in dict(
    ROLEPLAY_LLM_PROVIDER="mock",
    ROLEPLAY_RAG_IMPL="memory",
    ROLEPLAY_EMBEDDER="hashing",
    ROLEPLAY_ENABLE_WEB="false",
    ROLEPLAY_EMOTION_DETECTOR="keyword",
).items():
    os.environ[k] = v
os.environ["ROLEPLAY_KNOWLEDGE_DIR"] = str(_t / "k")
os.environ["ROLEPLAY_CHARACTERS_DIR"] = str(_t / "c")
os.environ["ROLEPLAY_SESSION_MEMORY_DIR"] = str(_t / "s")

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))


def show_sig(fn, label):
    try:
        print("   %s%s" % (label, inspect.signature(fn)))
    except Exception:  # noqa: BLE001, S110
        pass


# ============================================================ 1. SSRF (真相)
print("=" * 70)
print("1) SSRF: build_llm_from_config 的真实签名与内网地址接受情况")
try:
    from roleplay.core.llm import factory as F

    print("   模块内函数:", [n for n, o in vars(F).items() if callable(o) and not n.startswith("__")][:20])
    fn = None
    for nm in ("build_llm_from_config", "build_llm", "create_llm", "make_llm"):
        if hasattr(F, nm):
            fn = getattr(F, nm)
            print("   选中:", nm)
            show_sig(fn, nm)
            break
    if fn is None:
        print("   !! 未找到工厂函数，列出签名:")
        for n, o in vars(F).items():
            if inspect.isfunction(o) and not n.startswith("_"):
                show_sig(o, n + " ")
    else:
        # 试多种入参形态
        attempts = []
        for kwargs in (
            {"provider": "openai", "model": "gpt-x", "base_url": "http://169.254.169.254/latest/meta-data", "api_key": "k"},
            {"provider": "openai", "base_url": "http://169.254.169.254/latest/meta-data", "api_key": "k"},
        ):
            try:
                fn(**kwargs)
                attempts.append((kwargs.get("base_url"), "ACCEPTED"))
            except Exception as e:  # noqa: BLE001
                attempts.append((kwargs.get("base_url"), "%s: %s" % (type(e).__name__, str(e)[:90])))
        for a in attempts:
            print("   %-50s -> %s" % a)
except Exception as e:  # noqa: BLE001
    print("   导入失败:", repr(e))

# 直接查 _validate_base_url 的覆盖面
print()
print("1b) 校验函数 _validate_base_url 是否存在于 llm_config 且被 factory 使用")
try:
    from roleplay.api import llm_config as LC
    print("   llm_config._validate_base_url:", hasattr(LC, "_validate_base_url"))
    if hasattr(LC, "_validate_base_url"):
        show_sig(LC._validate_base_url, "_validate_base_url")
        for t in ("http://169.254.169.254/x", "http://127.0.0.1:11434", "http://192.168.1.1"):
            try:
                LC._validate_base_url(t)
                print("      %-40s -> ACCEPTED by validator" % t)
            except Exception as e:  # noqa: BLE001
                print("      %-40s -> rejected (%s)" % (t, type(e).__name__))
    fac_src = Path(F.__file__).read_text(encoding="utf-8")
    print("   factory 是否引用校验:", "_validate_base_url" in fac_src)
except Exception as e:  # noqa: BLE001
    print("   失败:", repr(e))

# ================================================= 2. custom_templates (真相)
print("=" * 70)
print("2) resolve_system_prompt 真实签名 + custom_templates 花括号")
try:
    from roleplay.core import persona_prompt as PP

    print("   签名:", inspect.signature(PP.resolve_system_prompt))
    print("   参数:", list(inspect.signature(PP.resolve_system_prompt).parameters))
except Exception as e:  # noqa: BLE001
    print("   取签名失败:", repr(e))

print()
print("2b) custom_templates 直接走模板格式化路径")
try:
    from roleplay.core.character_card import CharacterCard

    card = CharacterCard(
        name="测试角色",
        personality="冷静",
        prompt_config={"custom_templates": {"personality": "你是{name}，很冷静"}},
    )
    try:
        from roleplay.core import persona_prompt as PP2

        # 找出真正吃 prompt_config 的构建函数
        cands = [n for n, o in vars(PP2).items() if callable(o) and ("prompt" in n.lower() or "section" in n.lower())]
        print("   候选函数:", cands[:12])
        got = None
        for n in ("resolve_system_prompt", "build_system_prompt", "compose_system_prompt"):
            if hasattr(PP2, n):
                got = getattr(PP2, n)
                print("   调用:", n, inspect.signature(got))
                break
        if got:
            try:
                out = got(card)
                print("   -> 未崩溃: %r" % (str(out)[:200],))
            except KeyError as e:
                print("   -> [CONFIRMED] KeyError(%s): 自定义模板花括号导致崩溃" % e)
            except TypeError as e:
                print("   -> TypeError(签名问题，非产品 bug): %s" % e)
            except Exception as e:  # noqa: BLE001
                print("   -> %s: %s" % (type(e).__name__, str(e)[:200]))
    except Exception as e:  # noqa: BLE001
        print("   构建失败:", repr(e))
except Exception as e:  # noqa: BLE001
    print("   CharacterCard 构建失败:", repr(e))

# ================================================ 3. namespaces (真相)
print("=" * 70)
print("3) InMemoryVectorStore 的参数签名（add / search）")
try:
    from roleplay.core.rag.memory import InMemoryVectorStore

    show_sig(InMemoryVectorStore.add, "add")
    show_sig(InMemoryVectorStore.search, "search")
    st = InMemoryVectorStore()
    st.add(["alpha 苹果 水果"], namespace="ns1")
    st.add(["beta 汽车 交通"], namespace="ns2")
    print("   add(namespace=) 可用")
    for kwargs in ({"namespaces": ["nsX"]}, {"namespace": "nsX"}, {}):
        try:
            res = st.search("alpha", **kwargs)
            hits = [(getattr(d, "namespace", None), (getattr(d, "text", "") or "")[:18]) for d in res]
        except Exception as e:  # noqa: BLE001
            hits = "EXC %s: %s" % (type(e).__name__, str(e)[:90])
        print("   search(kwargs=%-24s) -> %s" % (kwargs, hits))
    print("   %s" % ("[CONFIRMED] namespaces 过滤未生效（nsX 仍返回 ns1 内容）"
                     if isinstance(st.search("alpha", namespaces=["nsX"]), list)
                     and st.search("alpha", namespaces=["nsX"]) else "[REFUTED]"))
except Exception as e:  # noqa: BLE001
    print("   失败:", repr(e))

# ================================================ 4. trace_path (真相)
print("=" * 70)
print("4) trace_path 路径穿越（正确签名 base_dir, character_id）")
try:
    import roleplay.core.knowledge.retrieval_trace as RT

    base = Path(tempfile.mkdtemp(prefix="tracebase_"))
    for cid in ("normal_id", "..\\..\\..\\pwned", "../../etc", "a/b"):
        try:
            out = RT.trace_path(base, cid)
            escaped = not str(Path(out).resolve()).startswith(str(base.resolve()))
            print("   cid=%-22r -> %s   escaped=%s" % (cid, out, escaped))
        except Exception as e:  # noqa: BLE001
            print("   cid=%-22r -> EXC %s: %s" % (cid, type(e).__name__, str(e)[:80]))
except Exception as e:  # noqa: BLE001
    print("   失败:", repr(e))
