"""QA 脚本级验证：前端一致性 / 配置兼容 / 大小写穿透 / numpy 回退。"""
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "src"))

from roleplay.models.chat import EMOTION_PARENT  # noqa: E402

ALL_15 = [
    "happy", "sad", "angry", "anxious", "surprise", "fear", "neutral",
    "love", "grateful", "excited", "disappointed", "lonely",
    "embarrassed", "confused", "sleepy",
]

issues = []


def check(name, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {name}" + (f"  {detail}" if detail else ""))
    if not cond:
        issues.append((name, detail))


# ── B5 前端一致性：后端 EmotionLabel vs emotion_map.json vs chat.js EMOTION_CN ──
from roleplay.models.chat import EmotionLabel  # noqa: E402

# 从 typing.Literal 提取后端枚举 keys
backend_keys = set(EmotionLabel.__args__)
check("后端 EmotionLabel 恰为 15 类", len(backend_keys) == 15 and backend_keys == set(ALL_15),
      f"backend={sorted(backend_keys)}")

# emotion_map.json keys
map_path = ROOT.parent / "frontend/assets/live2d/emotion_map.json"
map_data = json.loads(map_path.read_text(encoding="utf-8"))
map_keys = set(map_data["emotions"].keys())
check("emotion_map.json 恰为 15 类", len(map_keys) == 15 and map_keys == set(ALL_15),
      f"map={sorted(map_keys)}")

# chat.js EMOTION_CN keys（正则抽取）
chat_js = (ROOT.parent / "frontend/js/chat.js").read_text(encoding="utf-8")
m = chat_js.split("const EMOTION_CN =", 1)[1].split("};", 1)[0]
cn_keys = set(re.findall(r"^\s*([a-z_]+):", m, re.M))
check("chat.js EMOTION_CN 恰为 15 类", len(cn_keys) == 15 and cn_keys == set(ALL_15),
      f"cn={sorted(cn_keys)}")

# 三方完全一致
check("三方 keys 完全一致（后端/map/EMOTION_CN）",
      backend_keys == map_keys == cn_keys,
      f"diff backend-map={sorted(backend_keys ^ map_keys)} map-cn={sorted(map_keys ^ cn_keys)}")

# EMOTION_GROUP（chat.js）与 EMOTION_PARENT（后端）一致
# 注意：紧凑写法一行多键（如 love: "happy", grateful: "happy"），须全局匹配
mg = chat_js.split("const EMOTION_GROUP =", 1)[1].split("};", 1)[0]
group = dict(re.findall(r"([a-z_]+):\s*\"([a-z_]+)\"", mg))
check("chat.js EMOTION_GROUP 与后端 EMOTION_PARENT 一致", group == EMOTION_PARENT,
      f"group={group} parent={EMOTION_PARENT}")

# live2d.js 前端父类表一致
live2d_js = (ROOT.parent / "frontend/js/live2d.js").read_text(encoding="utf-8")
lj = live2d_js.split("const EMOTION_PARENT =", 1)[1].split("};", 1)[0]
lj_parent = dict(re.findall(r"([a-z_]+):\s*\"([a-z_]+)\"", lj))
check("live2d.js 前端父类表与后端 EMOTION_PARENT 一致", lj_parent == EMOTION_PARENT,
      f"live2d={lj_parent} parent={EMOTION_PARENT}")

# emotion_map.json 与后端 _DEFAULT_MAP 一致
from roleplay.core.emotion.mapping import Live2DEmotionMapper  # noqa: E402
m_default = Live2DEmotionMapper()._data
check("后端 _DEFAULT_MAP 与前端 emotion_map.json 一致",
      m_default["emotions"] == map_data["emotions"] and m_default["default"] == map_data["default"],
      f"backend default={m_default.get('default')} map default={map_data.get('default')}")


# ── B7 配置兼容 ──
from roleplay.config import Settings, get_settings  # noqa: E402

get_settings.cache_clear()
s = Settings()  # 无任何 env 覆盖，验证新字段默认值
check("新字段默认值 emotion_detector=auto", s.emotion_detector == "auto", s.emotion_detector)
check("新字段默认值 emotion_llm_timeout=8.0", s.emotion_llm_timeout == 8.0, s.emotion_llm_timeout)
check("新字段默认值 emotion_confidence_threshold=0.4", s.emotion_confidence_threshold == 0.4,
      s.emotion_confidence_threshold)
check("新字段默认值 emotion_classifier_backend=hashing", s.emotion_classifier_backend == "hashing",
      s.emotion_classifier_backend)
check("新字段默认值 emotion_jina_model 存在", s.emotion_jina_model.startswith("jina"),
      s.emotion_jina_model)

# 非法 emotion_detector 值：pydantic-settings 校验 Literal —— 期望抛 ValidationError（拒绝而非静默兜底）
from pydantic import ValidationError  # noqa: E402
try:
    Settings(emotion_detector="banana")
    check("非法 emotion_detector='banana' 被拒绝（ValidationError）", False,
          "未抛 ValidationError，非法值被接受")
except ValidationError:
    check("非法 emotion_detector='banana' 被拒绝（ValidationError）", True, "pydantic Literal 校验拦截")


# ── C4 大小写/变体穿透：SSE 标签 → 前端 EMOTION_CN 可查 ──
# 后端 normalize 保证输出小写 15 类之一；验证每个后端标签在前端 EMOTION_CN 都能查到
missing = [k for k in ALL_15 if k not in cn_keys]
check("15 类标签在 EMOTION_CN 全部可查", not missing, f"missing={missing}")

# 前端 chip 渲染用 EMOTION_CN[emotion] || emotion 兜底 —— 大小写敏感但后端恒小写，无穿透风险
check("前端 EMOTION_CN 键全小写（与后端输出一致）",
      all(k == k.lower() for k in cn_keys), "")


# ── numpy 缺失回退一致性 ──
import subprocess  # noqa: E402
import textwrap  # noqa: E402

probe = textwrap.dedent('''
    import sys
    sys.path.insert(0, r"src")
    # 模拟 numpy 不可用
    import builtins
    real_import = builtins.__import__
    def fake_import(name, *a, **kw):
        if name == "numpy" or name.startswith("numpy."):
            raise ImportError("blocked for test")
        return real_import(name, *a, **kw)
    builtins.__import__ = fake_import
    from roleplay.core.emotion.classifier import LocalClassifierDetector
    import asyncio
    async def main():
        d = LocalClassifierDetector(enabled=True, backend="hashing")
        assert d.available is True, "纯 Python 回退仍应 available"
        r1 = await d.detect("我爱你")
        r2 = await d.detect("我今天好难过")
        print(f"pure_python: {r1.emotion} {r1.score} | {r2.emotion} {r2.score}")
    asyncio.run(main())
''')
res = subprocess.run(
    [sys.executable, "-c", probe], cwd=ROOT.parent, capture_output=True, text=True, timeout=30
)
if res.returncode != 0:
    check("numpy 缺失纯 Python 回退", False, f"stderr={res.stderr[:300]}")
else:
    out = res.stdout.strip()
    check("numpy 缺失纯 Python 回退可用", "pure_python:" in out, out)


print("\n==== 汇总 ====")
if issues:
    print(f"发现 {len(issues)} 个问题：")
    for name, detail in issues:
        print(f"  - {name}: {detail}")
else:
    print("全部脚本级验证 PASS，无问题")

sys.exit(1 if issues else 0)
