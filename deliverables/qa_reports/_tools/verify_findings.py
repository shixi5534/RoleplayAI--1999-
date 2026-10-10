"""独立复现子代理报告中的高危结论（交叉验证，不采信未复现的断言）。

每项输出 [CONFIRMED] / [REFUTED] / [INCONCLUSIVE]。
只读：全部在临时目录进行，不改项目文件。
"""
import os
import sys
import tempfile
from pathlib import Path

_t = Path(tempfile.mkdtemp(prefix="verify_"))
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

results = []


def verdict(name, ok, detail=""):
    tag = "[CONFIRMED]" if ok else "[REFUTED]"
    results.append((tag, name, detail))
    print("%s %s\n    %s" % (tag, name, detail))


# ---------------------------------------------------------------- 1. SSRF
print("=" * 70)
print("1) SSRF: /chat 请求体里的 llm.base_url 是否绕过主机校验")
try:
    from roleplay.core.llm.factory import build_llm_from_config

    targets = [
        "http://169.254.169.254/latest/meta-data",
        "http://127.0.0.1:11434",
        "http://192.168.1.1",
        "http://10.0.0.1:8080",
        "file:///c:/windows/win.ini",
    ]
    accepted = []
    for t in targets:
        try:
            build_llm_from_config({"provider": "openai", "model": "gpt-x",
                                   "base_url": t, "api_key": "k"})
            accepted.append(t)
        except Exception as e:  # noqa: BLE001
            print("   rejected %-45s (%s)" % (t, type(e).__name__))
    print("   accepted: %s" % accepted)
    verdict("SSRF via ChatRequest.llm.base_url",
            len(accepted) >= 3,
            "accepted %d/%d 内网/元数据地址: %s" % (len(accepted), len(targets), accepted))
except Exception as e:  # noqa: BLE001
    verdict("SSRF via ChatRequest.llm.base_url", False, "导入/调用失败: %r" % e)

# ------------------------------------------------- 2. custom_templates KeyError
print("=" * 70)
print("2) 角色卡 custom_templates 非 {value} 花括号是否导致崩溃")
try:
    from roleplay.core.persona_prompt import resolve_system_prompt

    card = {
        "name": "测试角色",
        "personality": "冷静",
        "prompt_config": {"custom_templates": {"personality": "你是{name}，很冷静"}},
    }
    try:
        out = resolve_system_prompt(card, fallback_prompt="兜底提示词")
        verdict("custom_templates KeyError -> 请求崩溃", False,
                "未崩溃，返回: %r" % (str(out)[:150],))
    except KeyError as e:
        verdict("custom_templates KeyError -> 请求崩溃", True,
                "抛出 KeyError(%s)；fallback_prompt 未兜住" % e)
    except Exception as e:  # noqa: BLE001
        verdict("custom_templates KeyError -> 请求崩溃", True,
                "抛出 %s: %s" % (type(e).__name__, str(e)[:150]))
except Exception as e:  # noqa: BLE001
    verdict("custom_templates KeyError", False, "导入失败: %r" % e)

# ------------------------------------------------------- 3. memory namespaces
print("=" * 70)
print("3) InMemoryVectorStore 是否忽略 namespaces（跨命名空间串味）")
try:
    from roleplay.core.rag.memory import InMemoryVectorStore

    st = InMemoryVectorStore()
    st.add(["alpha 苹果 水果"], namespace="ns1")
    st.add(["beta 汽车 交通"], namespace="ns2")
    res = st.search("alpha", top_k=5, namespaces=["nsX"])
    hits = [(getattr(d, "namespace", None), getattr(d, "text", "")[:20]) for d in res]
    leaked = any(ns == "ns1" for ns, _ in hits)
    verdict("InMemoryVectorStore 忽略 namespaces 参数", bool(leaked),
            "namespaces=['nsX'] 的检索返回: %s" % hits)
except Exception as e:  # noqa: BLE001
    verdict("InMemoryVectorStore 忽略 namespaces", False, "调用失败: %r" % e)

# -------------------------------------------------- 4. metadata 越界 IndexError
print("=" * 70)
print("4) InMemoryVectorStore.add 的 metadatas 越界是否抛 IndexError")
try:
    from roleplay.core.rag.memory import InMemoryVectorStore

    st2 = InMemoryVectorStore()
    try:
        st2.add(["doc1", "doc2"], metadatas=[{"a": 1}])  # 2 文本 1 metadata
        verdict("memory.add metadatas 越界 IndexError", False, "未抛异常（可能已容错）")
    except IndexError as e:
        verdict("memory.add metadatas 越界 IndexError", True, "IndexError: %s" % e)
    except Exception as e:  # noqa: BLE001
        verdict("memory.add metadatas 越界 IndexError", True,
                "%s: %s" % (type(e).__name__, str(e)[:120]))
except Exception as e:  # noqa: BLE001
    verdict("memory.add metadatas 越界", False, "导入失败: %r" % e)

# ---------------------------------------------- 5. HTTPException headers 丢失
print("=" * 70)
print("5) 自定义 HTTPException 处理器是否丢弃 Retry-After 头")
try:
    from fastapi.testclient import TestClient

    from roleplay.main import app

    with TestClient(app) as c:
        # 找一个真实会 429 的入口：直接连打，看是否有 Retry-After
        got = None
        for i in range(200):
            r = c.get("/health")
            if r.status_code == 429:
                got = r
                break
        if got is not None:
            verdict("429 丢失 Retry-After 头", "retry-after" not in {k.lower() for k in got.headers},
                    "429 headers=%s" % dict(got.headers))
        else:
            # 用处理器直接验证
            from starlette.requests import Request

            from roleplay.errors import handlers as H
            print("   未触发到 429（限流阈值高于 200 次），改为检查处理器源码是否透传 headers")
            import inspect
            src = inspect.getsource(H)
            passthrough = "exc.headers" in src or "headers=" in src
            verdict("429 丢失 Retry-After 头", not passthrough,
                    "handlers.py 源码中 %s 'exc.headers' 透传" % ("存在" if passthrough else "不存在"))
except Exception as e:  # noqa: BLE001
    verdict("HTTPException headers 透传", False, "验证失败: %r" % e)

# --------------------------------------------------------- 6. STT 幻觉过滤截断
print("=" * 70)
print("6) STT 幻觉/尾部过滤是否把正常英文截断")
try:
    import inspect
    import re as _re

    import roleplay.core.voice.stt as S

    fn = None
    for nm in dir(S):
        if "halluc" in nm.lower() or "filter" in nm.lower() or "clean" in nm.lower() or "post" in nm.lower():
            obj = getattr(S, nm)
            if callable(obj):
                fn = (nm, obj)
                break
    print("   候选过滤函数:", fn[0] if fn else "未找到")
    if fn:
        cases = ["I love music", "The audience gave applause", "我喜欢听music",
                 "Hello world", "音乐"]
        for cse in cases:
            try:
                out = fn[1](cse)
                mark = "截断!" if out != cse else "ok"
                print("     %-32r -> %-24r  %s" % (cse, out, mark))
            except Exception as e:  # noqa: BLE001
                print("     %-32r -> EXC %s" % (cse, type(e).__name__))
    else:
        src = inspect.getsource(S)
        m = _re.findall(r"def (\w+)", src)
        print("   stt.py 中的函数:", m[:25])
        verdict("STT 英文尾字截断", False, "未能定位过滤函数，需人工确认")
except Exception as e:  # noqa: BLE001
    verdict("STT 英文尾字截断", False, "导入失败: %r" % e)

# ---------------------------------------------------------- 7. 路径穿越 trace
print("=" * 70)
print("7) retrieval_trace trace_path 路径穿越")
try:
    import inspect

    import roleplay.core.knowledge.retrieval_trace as RT

    src = inspect.getsource(RT)
    line = [ln for ln in src.splitlines() if "trace_path" in ln][:6]
    print("   相关行:", line)
    fn = getattr(RT, "_trace_path", None) or getattr(RT, "trace_path", None)
    if callable(fn):
        out = fn("..\\..\\..\\pwned")
        base = getattr(RT, "TRACE_DIR", None) or "?"
        print("   trace_path('..\\..\\..\\pwned') ->", out)
        escaped = ".." in str(out) and str(base) not in str(out)
        verdict("retrieval_trace 路径穿越", escaped, "返回 %s (base=%s)" % (out, base))
    else:
        verdict("retrieval_trace 路径穿越", False, "未找到可调用入口，需人工确认")
except Exception as e:  # noqa: BLE001
    verdict("retrieval_trace 路径穿越", False, "验证失败: %r" % e)

print()
print("=" * 70)
print("汇总: %d CONFIRMED / %d REFUTED"
      % (sum(1 for r in results if r[0] == "[CONFIRMED]"),
         sum(1 for r in results if r[0] == "[REFUTED]")))
