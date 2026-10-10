"""第三轮：用真实签名做决定性复现。

1) SSRF —— 用 LLMOverride + build_llm_from_config(settings, override)
2) namespaces —— add 无 namespace 参数，那内存实现的 namespace 到底怎么来的？
   看 base.RetrievedChunk / memory 源码，并用 search(namespaces=...) 验证过滤
3) custom_templates —— resolve_system_prompt 是关键字参数，用 keyword 调用
4) trace_path —— 已确认 ..\\..\\..\\ 可逃逸（escaped=True）
只读。
"""
import inspect
import os
import sys
import tempfile
from pathlib import Path

_t = Path(tempfile.mkdtemp(prefix="verify3_"))
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

# ============================================================== 1) SSRF 定论
print("=" * 72)
print("1) SSRF 定论：LLMOverride.base_url -> build_llm_from_config")
try:
    from roleplay.core.llm.factory import build_llm_from_config
    from roleplay.core.llm.base import LLMOverride

    print("   LLMOverride fields:", list(getattr(LLMOverride, "__dataclass_fields__", {}) or
                                        getattr(LLMOverride, "model_fields", {})))
    targets = [
        "http://169.254.169.254/latest/meta-data",
        "http://127.0.0.1:11434",
        "http://192.168.1.1",
        "http://10.0.0.1:8080",
        "https://evil.example.com/v1",
        "file:///c:/windows/win.ini",
        "gopher://x",
    ]
    accepted, rejected = [], []
    for t in targets:
        try:
            ov = LLMOverride(provider="openai", model="gpt-x", base_url=t, api_key="k")
        except Exception as e:  # noqa: BLE001
            print("     构造 override 失败(%s): %s" % (t, type(e).__name__))
            continue
        try:
            port, used_global = build_llm_from_config(None, ov)
            accepted.append((t, type(port).__name__))
        except Exception as e:  # noqa: BLE001
            rejected.append((t, "%s: %s" % (type(e).__name__, str(e)[:70])))
    print("   ACCEPTED (%d):" % len(accepted))
    for t, cls in accepted:
        print("      %-46s -> %s" % (t, cls))
    print("   REJECTED (%d):" % len(rejected))
    for t, why in rejected:
        print("      %-46s -> %s" % (t, why))
    internal = [t for t, _ in accepted if any(x in t for x in
                ("169.254.169.254", "127.0.0.1", "192.168.", "10.0.", "file:", "gopher:"))]
    print("   >>> %s 内网/元数据/非 http 地址被接受 %d 个"
          % ("[CONFIRMED] SSRF" if internal else "[REFUTED]", len(internal)))
except Exception as e:  # noqa: BLE001
    print("   失败:", repr(e))

# ======================================================= 2) namespaces 定论
print()
print("=" * 72)
print("2) InMemoryVectorStore 的 namespace 语义")
try:
    from roleplay.core.rag.memory import InMemoryVectorStore

    src = inspect.getsource(InMemoryVectorStore)
    print("   add 签名:", inspect.signature(InMemoryVectorStore.add))
    print("   search 签名:", inspect.signature(InMemoryVectorStore.search))
    # add 是否接受 namespace? 源码里怎么取 namespace
    key_lines = [ln.strip() for ln in src.splitlines()
                 if "namespace" in ln.lower()][:14]
    print("   源码中 namespace 相关行:")
    for ln in key_lines:
        print("      ", ln[:120])
    st = InMemoryVectorStore()
    st.add(["alpha 苹果 水果", "gamma 葡萄"])
    print("   add(无 namespace) 后 search(namespaces=['nsX']):")
    try:
        r = st.search("alpha", namespaces=["nsX"])
        print("      返回 %d 条: %s" % (len(r), [(getattr(d, "namespace", None), (d.text or "")[:16]) for d in r]))
        print("      >>> [CONFIRMED] namespaces 过滤被忽略（本应 0 条）" if r else "      >>> 过滤生效（0 条）")
    except Exception as e:  # noqa: BLE001
        print("      EXC", type(e).__name__, str(e)[:120])
except Exception as e:  # noqa: BLE001
    print("   失败:", repr(e))

# ============================================== 3) custom_templates 定论
print()
print("=" * 72)
print("3) custom_templates 花括号 -> 用关键字参数调用")
try:
    from roleplay.core.persona_prompt import resolve_system_prompt
    from roleplay.models.prompt_config import PromptConfig

    cases = [
        ("含 {name}", {"custom_templates": {"personality": "你是{name}，很冷静"}}),
        ("正常 {value}", {"custom_templates": {"personality": "你是{value}，很冷静"}}),
        ("双花括号", {"custom_templates": {"personality": "你是{{value}}，很冷静"}}),
    ]
    for label, pc_raw in cases:
        try:
            pc = PromptConfig.from_any(pc_raw) if hasattr(PromptConfig, "from_any") else PromptConfig(**pc_raw)
        except Exception as e:  # noqa: BLE001
            print("   [%s] PromptConfig 构造失败: %s: %s" % (label, type(e).__name__, str(e)[:80]))
            continue
        try:
            out = resolve_system_prompt(character_card="角色卡内容", fallback_prompt="兜底",
                                        prompt_config=pc)
            print("   [%-12s] -> OK, %r" % (label, str(out)[:120]))
        except KeyError as e:
            print("   [%-12s] -> [CONFIRMED] KeyError(%s) 崩溃；fallback 未兜住" % (label, e))
        except Exception as e:  # noqa: BLE001
            print("   [%-12s] -> %s: %s" % (label, type(e).__name__, str(e)[:140]))
except Exception as e:  # noqa: BLE001
    print("   失败:", repr(e))

# ================================================= 4) 端到端：坏卡是否 500
print()
print("=" * 72)
print("4) 端到端：带 {name} 模板的角色卡走 /chat 是否 500")
try:
    from fastapi.testclient import TestClient

    from roleplay.main import app

    with TestClient(app) as c:
        payload = {
            "session_id": "tpl",
            "message": "你好",
            "character_card": {
                "name": "坏模板角色",
                "personality": "冷静",
                "prompt_config": {"custom_templates": {"personality": "你是{name}，很冷静"}},
            },
        }
        r = c.post("/chat/stream", json=payload)
        print("   status=%s" % r.status_code)
        print("   body[:300]=%s" % r.text[:300].replace("\n", " | "))
        print("   >>> %s" % ("[CONFIRMED] 坏模板导致请求失败"
                             if r.status_code >= 400 or "error" in r.text[:60].lower()
                             else "[REFUTED] 请求正常，未崩溃"))
except Exception as e:  # noqa: BLE001
    print("   失败:", repr(e))
