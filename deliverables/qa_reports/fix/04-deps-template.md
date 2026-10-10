# 修复报告 04 — D1 numpy 依赖归属 / D2 custom_templates 花括号崩溃

- 工作目录：`C:\Users\Lenovo\WorkBuddy\2026-07-27-16-45-03\roleplay-ai`
- 解释器：`.\.venv\Scripts\python.exe`（Python 3.11，本机 numpy 2.5.1）
- 独占改动文件：`pyproject.toml`、`requirements.txt`、`src\roleplay\core\character_card.py`、`tests\test_character_card.py`
- 未改动任何禁改文件（`orchestrator.py`、`mock.py`、`session_memory.py`、`config.py`、`factory.py`、
  `errors\handlers.py`、`qq_onebot.py`、`conftest.py`、`models\prompt_config.py` 均**零改动**）
- **未执行任何 `pip install` / 联网操作**（满足离线要求）

---

## 一、缺陷复现（修复前，实测）

### D1 — `import compendium_rag` 直接 ImportError

用 `sys.meta_path` 拦截 numpy 模拟「未装 extras.emotion」的干净环境：

```
IMPORT-FAIL: ImportError No module named numpy (simulated: emotion extra not installed)
numpy installed version: 2.5.1
```

确认为**顶层硬依赖**（`re` 顶格匹配，非函数内惰性 import）：

| 文件 | 行 | 形式 |
|---|---|---|
| `src\compendium_rag\retriever.py` | 21 | **模块顶层** `import numpy as np` |
| `src\roleplay\core\knowledge\plot_semantic.py` | 28 | **模块顶层** `import numpy as np` |

（`plot_rerank.py:86`、`plot_graph.py:1882/2276`、`emotion\classifier.py:216` 均为**函数内**
惰性 import + 缺库回退，**不是**硬依赖，故不影响本次判定。）

### D2 — `KeyError('name')`

```
custom_templates = {'personality': '你是{name}，很冷静'}
RENDER-FAIL: KeyError 'name'
```

---

## 二、D1 修复：方案选择与理由

### 选择：**把 numpy 加入 `[project].dependencies`**（而非新增 extra）

**理由（按优先级）：**

1. **默认安装路径必须不崩** —— 任务明确「优先选择不会让默认安装路径崩掉的方案」。
   README 主推 `pip install -e ".[dev]"`，该命令只解析 `dependencies` + `dev`。
   新增 `compendium-rag` extra 需要用户**额外记得**加 `.[compendium-rag]`，
   否则 `import compendium_rag` 依旧 ImportError —— 缺陷本质（默认路径崩）**未被消除**，
   只是从「报错指向 numpy」变成「报错指向缺失的 extra」，排查成本并未下降。
2. **`compendium_rag` 是仓库内一等公民包** —— 它与 `src/roleplay` 同属 `src/` 下被
   `[tool.setuptools.packages.find] where = ["src"]` 一起打包发布的包，其测试在
   `tests/compendium_rag/`，属项目主线能力而非可选插件。
3. **numpy 同时服务两条主链路** —— 除 `compendium_rag/retriever.py` 外，
   `roleplay/core/knowledge/plot_semantic.py`（剧情语义检索）也是顶层 import。
   若只给 compendium_rag 加 extra，`plot_semantic` 这条 roleplay 主链仍会在默认安装下崩。
4. **归类错误的本质是「挂错组」** —— numpy 的真实用途是向量索引数学，与 `emotion`
   （情感识别）毫无关系。移入基线依赖是纠正归类，不是新增可选能力。

### 改动行

**`pyproject.toml`**（`[project].dependencies`，第 17–22 行区）：

```diff
     "starlette==0.40.0",
     "python-multipart>=0.0.6",
+    # numpy：`compendium_rag/retriever.py` 与 `roleplay/core/knowledge/plot_semantic.py`
+    # 都是**模块顶层** import，属一等公民包的硬依赖（向量索引数学），
+    # 与「情感」特性无关。此前仅挂在 extras.emotion，导致按 README 的
+    # `pip install -e ".[dev]"` 装完后 `import compendium_rag` 直接 ImportError。
+    "numpy>=1.26",
 ]
 
 [project.optional-dependencies]
 rag = ["chromadb>=0.5"]
 docs = ["pypdf>=4.0", "python-docx>=1.1"]
 voice = ["edge-tts>=6.1", "faster-whisper>=1.0"]
+# numpy 已是基线依赖（见上）；保留此项仅为兼容既有的 `pip install roleplay-ai[emotion]`
+# 安装命令，install 后不会额外引入任何包。
 emotion = ["numpy>=1.26"]
```

> `extras.emotion` **刻意保留**而非删除：外部可能已有 `pip install roleplay-ai[emotion]`
> 的安装脚本，删掉会让该命令直接失败。保留后它成为幂等别名（numpy 已在基线中），
> 既不破坏兼容又不产生重复安装。

**`requirements.txt`**（补齐，保持两份清单一致）：

```diff
 python-multipart>=0.0.6
+
+# numpy 是运行时基线依赖（`compendium_rag/retriever.py:21` 与
+# `roleplay/core/knowledge/plot_semantic.py:28` 均为模块顶层 import）。
+# 此前只挂在 pyproject 的 extras.emotion，属归类错误 —— 已同步补入两份清单。
+numpy>=1.26
```

### 离线验证（未执行任何 pip）

解析 `pyproject.toml` 的 `dependencies` 段（用 `tomllib` + `packaging.Requirement`）：

```
=== [project].dependencies (DEFAULT install set) ===
    fastapi==0.115.6
    uvicorn[standard]==0.51.0
    pydantic==2.10.3
    pydantic-settings==2.14.2
    httpx==0.28.1
    starlette==0.40.0
    python-multipart>=0.0.6
    numpy>=1.26
numpy in DEFAULT deps : True
numpy in extras.emotion: True

=== README install command `pip install -e ".[dev]"` resolves to ===
   total specs: 11
   numpy resolves under .[dev]: True

requirements.txt numpy present: True
```

修复后 `import compendium_rag` 实测：

```
import compendium_rag OK, version 0.1.0
```

---

## 三、D2 修复：修法与降级行为

### 修法：抽出 `_apply_template`，**三级策略**（不是单一 `replace`）

新增 `character_card._apply_template(tpl, value, field)`，`_render_field` 的两处
（`behavior_rules` 分支 + 通用分支）统一改为调用它，**消除重复**：

```python
def _apply_template(tpl: str, value: str, field: str) -> str:
    if "{value}" in tpl:
        return tpl.replace("{value}", value)      # ① 字面量替换：对未知花括号免疫
    try:
        rendered = tpl.format(value=value)         # ② 兼容 {value!r} / {value:>8}
    except Exception as exc:
        default = _DEFAULT_TEMPLATES.get(field)    # ③ 回落默认模板 + warning
        logger.warning("custom_templates[%s] 模板含非法占位符（%s: %s），已回落默认模板：%r",
                       field, type(exc).__name__, exc, tpl[:200])
        if default is not None:
            return default.replace("{value}", value)
        return tpl
    logger.warning("custom_templates[%s] 未使用 {value} 占位符，字段值未被注入：%r", field, tpl[:200])
    return rendered
```

**为什么不是纯 `tpl.replace("{value}", value)`（推荐方案 A 的朴素版）？**
朴素版对 `{value!r}`、`{value:>8}` 这类**合法且既有**的 format 写法会失效——
`"{value:>8}"` 里不含字面量 `"{value}"`，replace 不命中，模板会原样输出、
字段值被静默丢弃。三级策略优先用字面量替换拿到「零 KeyError」的稳健性，
同时用 `format` 兜住这些既有写法，两者兼顾。不引入任何新依赖，纯 stdlib。

### 降级行为（可观测）

**任何情况下都不抛异常**，请求不会 500：

| 模板形态 | 修复前 | 修复后 | warning |
|---|---|---|---|
| `{value}`（正常/默认） | ✅ 正确替换 | ✅ 逐字节不变 | 无 |
| `"你是{name}，很冷静"`（缺陷用例） | ❌ `KeyError('name')` | ✅ 回落默认模板 → `人设：冷静` | ✅ |
| `"{unknown}"` / `"{a}{b}{c}"` | ❌ `KeyError` | ✅ 回落默认模板 | ✅ |
| `"{0}"`（位置占位符） | ❌ `IndexError` | ✅ 回落默认模板 | ✅ |
| `"{value} 与 {name}"`（混用） | ❌ `KeyError('name')` | ✅ 未知花括号**原样保留** → `冷静沉着 与 {name}` | 无 |
| `"{value!r}"` / `"{value:>8}"` | ✅ | ✅ 保持 format 结果 | ✅（提示未用字面量占位符） |
| `"固定文案"`（无占位符） | ✅ | ✅ 原样输出，值未注入 | ✅ |
| `""`（空模板） | 回落默认 | 回落默认（`or` 短路语义不变） | 无 |

**关键设计取舍**：非法占位符走「**回落默认模板**」而非「原样返回模板文本」。
理由：原样返回会把字段值**静默丢弃**（模型看不到人设，且 prompt 里残留 `{name}`），
比崩溃更隐蔽。回落默认模板保证「人设始终可达」，同时 warning 留下排查线索。

实测输出：

```
--- ORIGINAL D2 REPRO: {name} template ---   RESULT: 人设：冷静
--- {value} still works ---                  RESULT: 【人格】冷静
--- default path (no custom_templates) ---   RESULT: 人设：冷静
--- other crash shapes ---
   '{0}'          -> '人设：冷静'
   '{a}{b}'       -> '人设：冷静'
   '{value!r}'    -> "'冷静'"
   '常量无占位符'       -> '常量无占位符'
```

### 对 `models\prompt_config.py` 的建议（**未改动该文件**，留给主代理决策）

建议在 `PromptConfig` 上增加一个 `render(field, value) -> str` 方法（或在 `from_any`
里加 `validate_templates()`），把「模板合法性与降级」的判定**收敛到配置模型层**：

- 好处：`character_card` 与 `persona_prompt`（后者有 7 处同类 `.format(value=...)`）可共用
  同一套降级语义，避免两处各自实现、未来漂移；
- 现状风险：本次修复只覆盖 `character_card.py`。任务说明实测 `persona_prompt.py` 侧
  **未**崩溃（其自定义模板路径取值来自内部受控来源），故按指示未改动；
  但若将来 `persona_prompt` 也开始消费外部 `custom_templates`，同一缺陷会复现。

---

## 四、新增测试

追加在 `tests\test_character_card.py` 末尾（**未删改任何已有测试**；文件从 197 行 → 421 行）。
顶部新增导入 `logging` / `pytest` / `_DEFAULT_TEMPLATES` / `_render_field` / `PromptConfig`。

### D2 回归（16 个用例，含参数化）

| 测试名 | 覆盖点 |
|---|---|
| `test_custom_template_with_unknown_braces_does_not_raise` | 参数化 5 种未知花括号模板：不抛异常 + 字段值仍在 + warning |
| `test_custom_template_with_value_keeps_unknown_braces_literal` | `{value}` 混未知花括号 → 未知的原样保留 |
| `test_custom_template_without_value_falls_back_keeping_persona` | 非法占位符无 `{value}` → 回落默认模板，人设不丢 + warning |
| `test_custom_template_unknown_brace_via_full_prompt_path` | **端到端** `resolve_system_prompt`（真实攻击面）不崩 + 降级可观测 |
| `test_custom_template_no_crash_also_for_behavior_rules_field` | `behavior_rules` 分支同样免疫 |
| `test_custom_template_missing_value_placeholder_logs_warning` | 无 `{value}` 但 format 可用 → warning |
| `test_custom_template_format_conversion_still_supported` | `{value:>8}` 既有写法仍可用（防功能倒退） |
| `test_custom_template_value_placeholder_still_replaces` | **防回归**：正常 `{value}` 精确替换 |
| `test_default_templates_all_render_value` | **防回归**：8 个默认模板逐一验证 `{value}` 语义 |
| `test_default_path_unaffected_without_custom_templates` | 空/无 `custom_templates` 默认路径 + 空字段仍返回 `None` |
| `test_empty_custom_template_falls_back_to_default` | 空串模板回落默认（`or` 短路不变） |
| `test_resolve_system_prompt_output_unchanged_for_default_config` | 零回归：默认配置输出逐字节锁定 |

### D1 离线验证（3 个用例，纯文件解析，不 pip / 不联网）

| 测试名 | 覆盖点 |
|---|---|
| `test_numpy_is_a_default_dependency_not_only_an_extra` | 断言 `dependencies` 含 numpy **且带版本下限** |
| `test_numpy_present_in_requirements_txt` | 两份清单一致性 |
| `test_toplevel_numpy_importers_are_covered_by_default_deps` | **根因锁**：`rglob` 扫描 `src/**/*.py`，凡顶格 `import numpy` 的文件，其依赖必须被默认清单覆盖 —— 未来新增同类文件会立即变红 |

---

## 五、测试结果

### 5.1 指定目标套件（任务要求的命令）

```
cd C:\Users\Lenovo\WorkBuddy\2026-07-27-16-45-03\roleplay-ai
.\.venv\Scripts\python.exe -m pytest tests\test_character_card.py tests\test_prompt_p0.py \
    tests\test_prompt_p1.py tests\test_prompt_p2.py -q --tb=short -p no:cacheprovider
```

**结果：`98 passed, 1 warning`，exit=0，无 FAILED / ERROR。**

（环境提示已生效：首次按原样运行时有 1 个
`ERROR tests/test_prompt_p0.py::test_store_roundtrip_keeps_p0_fields - PermissionError
[WinError 5] ...\pytest-of-Lenovo` —— 即说明中预告的沙箱 0o700 目录问题。
加 `PYTHONPATH=...\deliverables\qa_reports\_logs` + `-p _qa_tmpfix` +
`--basetemp=<可写目录>` 后消失，**非项目缺陷**。）

### 5.2 全量测试（回归确认）

```
.\.venv\Scripts\python.exe -m pytest tests -q --tb=line -p no:cacheprovider \
    -p _qa_tmpfix --basetemp="$env:TEMP\qa_full2"
```

**结果：`1 failed, 1323 passed, 8 skipped`（338.01s）**

### 唯一失败项归属判定（**与本修复无关**）

`tests/test_plotrag_m0_verification.py::TestM03StrictGate::test_default_invocation_returns_zero`

- 该用例 `subprocess.run([sys.executable, "-X", "utf8", "scripts/audit_full_corpus.py"])`
  后断言 `returncode == 0`，是**语料数据审计脚本**的退出码断言，
  与 numpy 依赖清单 / 模板渲染**无任何调用关系**。
- 该文件 `git diff --stat` 为空（未被任何人改动），且不含
  `character_card` / `custom_templates` / `PromptConfig` / `numpy` 任一符号（已 grep 确认）。
- 失败原因是审计脚本自身报「默认调用返回 1」，属**语料数据状态**问题，
  疑似与另一代理正在进行的语料/图谱改动相关，不属本任务两个缺陷。

**独立性与时序证据**：首次全量运行出现 **10 failed**（`test_repetition_guard.py` 9 项 +
上述 1 项），但**同一批文件在隔离运行时全部通过**（`21 passed`）。核查文件 mtime 发现
`orchestrator.py`(12:34)、`mock.py`(12:35:02)、`session_memory.py`(12:35:44)、
`config.py`(12:35:52)、`conftest.py`(12:35:16) 均在**首次全量运行（耗时 5:46）进行期间**
被其他代理写入 —— 即在测试进程已 import 模块后被就地修改，属典型的编辑期竞态假阳性。
清空 basetemp 重跑后降至 1 failed，剩余 9 项自行消失。

另做了**决定性对照实验**：写了一个仅用于 QA 的运行期插件 `_qa_oldtpl.py`（位于
`deliverables\qa_reports\_logs\`，非项目代码），把 `_apply_template` 在运行时**还原为修复前的
`tpl.format(value=value)`**，在**完全相同的 PYTHONPATH / basetemp 条件下**跑
`test_repetition_guard.py + test_plotrag_m0_verification.py`：

| 条件 | 结果 |
|---|---|
| 修复前模板行为（`_qa_oldtpl` 还原） | `1 failed, 113 passed` |
| 我的修复（同一 PYTHONPATH） | `1 failed, 113 passed` |

**逐项一致 → 该失败与 D2 修复完全无关。**

---

## 六、遗留项 / 建议

1. **`persona_prompt.py` 同类写法未处理**（按指示刻意不动）：该文件有 7 处
   `.format(value=...)`（行 376/385/430/498/614-615 等）。当前实测未崩（模板来源受控），
   但若将来其 `core_anchors` / `length` / `pacing` 等键改由外部卡片驱动，
   会复现同一 `KeyError`。建议主代理评估统一收敛（见 §三建议）。
2. **`extras.emotion` 现为 numpy 的幂等别名**：保留是为兼容既有安装脚本。
   若确认无外部依赖该 extra 名，可后续清理。
3. **`requirements.txt` 的 `websockets>=12.0` 仍未进 `pyproject`**（该文件第 19–21 行
   自注「pyproject 未列此项」）—— 属另一条已知清单缺口（见 `04-channel-voice.md`），
   不在本次两个缺陷范围，未改动。
4. **`scripts/` 下大量脚本顶层 import numpy**（`_rank_stats.py` 等 20+ 个）：
   这些不进包发布（`packages.find where=["src"]`），且 numpy 现已在基线依赖中，
   故无需单独声明。
5. **建议为 D1 增设 CI 门禁**：`test_toplevel_numpy_importers_are_covered_by_default_deps`
   已是「源码顶层 import ↔ 依赖清单」的自动一致性检查，可直接用作 CI 门禁；
   若后续需要，可把同样的 `rglob` 模式扩展到其它第三方包（如 `websockets`）。
