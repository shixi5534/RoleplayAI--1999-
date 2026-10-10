# RoleplayAI 修复总报告

> 承接 [`00-SUMMARY.md`](00-SUMMARY.md) 的检验结论，本轮执行修复。
> 方式：4 个独立子代理按**文件所有权**并行（互不碰同一文件）+ 主代理独占整合文件
> （`api/llm_config.py`、`api/deps.py`、`tests/conftest.py`、`tests/test_llm_config.py`、
> `tests/test_repetition_guard.py`、`tests/test_prompt_p1.py`、`tests/test_prompt_p2.py`）。
> 所有修复**均由主代理独立复验**，未采信代理自述。

---

## 0. 结果总览

| 指标 | 修复前 | 修复后 |
|---|---|---|
| 完整套件 | 2 failed, **1279 passed**, 8 skipped | 1 failed, **1367 passed**, 8 skipped |
| 真实失败（产品 bug） | 0（2 个均为环境/测试自身） | 0 |
| 剩余失败 | — | 1 个：纯沙箱写限制（已证明，见 §4） |
| 新增测试 | — | **88 个**（含反向验证） |

**净增 88 个通过用例**（1279 → 1367），且新增测试中包含**能捕获原缺陷的断言**
（此前那类断言不存在，所以缺陷才长期隐形）。

---

## 1. P0 修复

### P0-1 依赖注入失效 —— 已修复

**改动**（`src/roleplay/core/orchestrator.py`）：

- 新增 `_resolve_llm(req) -> (llm, needs_aclose)`：
  - `req.llm` 为空 且已注入 `self._llm` → **直接用 `self._llm`，不经工厂**；
  - `req.llm` 确有字段 → 才调 `build_llm_from_config`，沿用其 `needs_aclose`；
  - `self._llm is None` → 回退工厂（保留 `deps.py` 之外的脚本兜底路径）。
- `run()`（原 `:852`）与 `stream()`（原 `:1048`）两处替换为 `self._resolve_llm(req)`。
- 两处 `try/finally` 与 `if needs_aclose and hasattr(llm, "aclose")` **原样保留** → 连接池不泄漏。

**新增回归测试**（`tests/test_orchestrator.py`）：
`test_run_uses_injected_llm_not_global_mock`、`test_stream_uses_injected_llm_not_global_mock`，
断言注入 LLM 的独有标记 `【INJECTED-LLM-MARKER】` 出现在回复中。

**主代理独立复验**（`_tools/verify_fixes_e2e.py`）：

```
注入 LLM 调用次数 = 1
reply 含标记      = True
>>> [PASS] 依赖注入生效
```

**反向验证**（代理执行）：把缺陷行为临时还原 → 两条新测试**双双失败**，证明断言非恒真。

> ⚠️ **这次修复的连带效应值得记录**：修复后 `tests/test_repetition_guard.py` 出现 9 条失败。
> 经主代理核实，那是该测试**一直依赖这个缺陷**（`_build_orch` 传 `MockLLMProvider()`，
> 靠工厂 monkeypatch 让替身生效）。已修正为按正确语义注入 → **21 passed**。

### P0-2 会话历史指数膨胀 —— 已修复

**双重根因，两处都改**：

1. `src/roleplay/core/llm/mock.py`：新增 `echo_history: bool = False`，**默认关闭历史回显**。
   默认时 `generate()` 完全不读 history（回复长度恒定，10 万字符历史与空历史输出逐字节相同）；
   `echo_history=True` 保留旧行为供演示。`generate_stream` 调 `generate`，自动继承开关。
2. `src/roleplay/core/session_memory.py`：新增**体量闸**（原先只有条数闸）：
   - `_CHAR_BUDGET = 120_000`、`_MIN_KEEP_TURNS = 1`；
   - `__init__(..., max_total_chars=120_000)`，`<=0` 表示关闭（兼容旧行为）；
   - 新 `_trim()`：条数闸语义不变 + 字符闸从最旧丢弃、**至少保留最近 1 轮**；
   - `append()` / `append_many()` 两条写路径都生效；
   - 单条自身超预算**不抛异常**，保留该条并记 WARNING（设计取舍：「宁越界不失忆」）；
   - `_load_all()` 加文件大小闸（≥4MB 拒载，防历史遗留的 GB 级 json 直接 OOM）。
3. `src/roleplay/config.py:444`：新增 `session_memory_max_chars = 120_000`
   （env `ROLEPLAY_SESSION_MEMORY_MAX_CHARS`）。
4. **主代理接线** `src/roleplay/api/deps.py:48`：显式传 `max_total_chars=s.session_memory_max_chars`，
   使 `.env` 覆盖真正生效（代理按文件边界约定未改此文件）。

**主代理独立复验**（`_tools/verify_fixes_e2e.py`，默认 mock 配置跑真实 `/chat/stream`）：

| 轮次 | 修复前历史 | 修复后历史 |
|---|---|---|
| 10 | 43,210 字符 | **370 字符** |
| 20 | 19,422,230 字符 | **760 字符** |
| 30 | （已达千万级） | **1,150 字符** |

```
末轮历史 = 1150 字符
相邻轮增长率: ['1.04','1.04','1.04','1.04','1.04']
>>> [PASS] 历史体量受控
mock 默认不再回显历史（传入 10 万字符历史，回复长度 = 33，不含历史内容）
```

**增长率从 ×1.84（指数）回到 ×1.04（线性）**，膨胀根除。

---

## 2. P1 修复

### P1-1 SSRF —— 已修复（并修正了原报告的一处过度断言）

> **重要更正**：修复阶段核对既有校验器源码后发现，我最初的 QA 报告称
> 「`127.0.0.1`/`10.x`/`192.168.x` 也被接受」是**过度断言**——那些是**有意的设计**
> （支持本地/内网 Ollama 部署，源码 docstring 写明）。真正的问题是
> **既有校验器从未被接线到 `/chat` 路径**。已同步更正 `00-SUMMARY.md`，
> 并即时纠正了正在执行的子代理（否则它会误伤合法用法）。

**改动**：

- 新建 `src/roleplay/core/llm/endpoint_guard.py`：无框架依赖的**唯一下沉实现**，
  策略逐条复刻既有校验器（**刻意不改放行策略**），拒绝时抛 `ValueError`。
- `src/roleplay/core/llm/factory.py:114-143` 接线：仅当「端点由本次请求决定」
  （`override.base_url` 非空或 provider≠全局）时校验；抛 `EndpointNotAllowedError`
  （422，与 API 层语义对齐）；传 `require_api_key=False` 保留既有「云端无 key 由
  ProviderError 在 generate 时报错」的契约（`test_llm_override.py` 锁死了该行为）。
- **主代理接线** `src/roleplay/api/llm_config.py:242`：原先这里有一份**重复副本**，
  已改为薄封装调用 `endpoint_guard`，消除两份实现漂移的风险（3 个既有调用点不变）。

**主代理独立复验**（`_tools/verify_security_fixes.py`）：

```
应拦截（8/8 PASS）：
  169.254.169.254 / 169.254.1.1 / 100.64.0.1 / file: / gopher: / ftp: / evil.example.com / 8.8.8.8
应放行（7/7 PASS，防误伤）：
  127.0.0.1:11434/v1 · 127.0.0.1:11434 · localhost:11434/v1 ·
  192.168.1.50:11434 · 10.0.0.5 · 172.16.5.5 · api.deepseek.com

端到端 POST /chat（恶意 base_url）-> 422   ✅
端到端 POST /chat（本地 ollama）  -> 200   ✅ 未误伤
```

### P1-2 历史无 token/字符预算 —— 已修复

由 P0-2 的 `max_total_chars` 字符闸覆盖（见上）。**注意**：这是**字符**预算而非
严格 token 预算；若将来接入长上下文模型，建议按模型上下文窗口再补一层 token 估算。

### P1-3 numpy 依赖归属 —— 已修复

- `pyproject.toml`：numpy 从 `extras.emotion` 移入 **[project].dependencies**
  （`extras.emotion` 保留为幂等别名，兼容既有安装命令）。
- `requirements.txt`：同步补 `numpy>=1.26`。
- 理由：README 主推的 `pip install -e ".[dev]"` 只解析 `dependencies + dev`；
  且 `roleplay/core/knowledge/plot_semantic.py:28` 也顶层 import numpy，
  单给 compendium_rag 加 extra 覆盖不到。
- 新增根因锁测试 `test_toplevel_numpy_importers_are_covered_by_default_deps`：
  扫描 `src/` 顶层 import numpy 的文件，确保都被默认依赖覆盖（未来新增同类文件即变红）。

### P1-4 custom_templates KeyError —— 已修复

`src/roleplay/core/character_card.py`：抽出 `_apply_template`，**三级策略**：

1. 模板含字面量 `{value}` → `replace("{value}", value)`（对未知花括号天然免疫）；
2. 不含但 `format` 成功（支持 `{value!r}` / `{value:>8}` 等既有写法）→ 用 format 结果 + warning；
3. format 失败 → **回落该字段默认模板** + warning。

任何情况**不抛异常**（请求不 500），且**不静默丢弃人设**（回落默认模板而非返回空）。
新增 16 个用例，含端到端 `resolve_system_prompt` 路径。

### P1-5 QQ token 泄漏 —— 已修复

`src/roleplay/channels/qq_onebot.py`：新增 `_redact_url(text, token)`，接入**3 处**日志路径
（异常分支、成功路径 info、WS 读取异常）。要点：

- `token` 为空时**直接跳过** `replace`，规避 `replace("", "***")` 的灾难性替换；
- 另有 `access_token=<值>` 正则兜底（即使拿不到 token 值也能打码）；
- `text` 非字符串先 `str()`。

**主代理独立复验**：

```
token 被脱敏                          -> '连接失败 ws://127.0.0.1:3001?access_token=*** end'  ✅
空 token 不做灾难性替换（普通文本原样）  ✅
空 token 时正则兜底仍打码              ✅
```

新增 4 个用例，含真实 `websockets.InvalidURI` 路径 + `caplog` 断言。

### P1-6 / P2 其余安全项 —— 已修复

- **S2a**：`errors/handlers.py:111` 透传 `exc.headers` → **429 的 `Retry-After` 实测恢复**
  （并加了反向对照，证明断言非恒真）。
- **S2b**：`_sanitize` 超深时**降级为占位符** `[深度超限已隐藏]`（dict 层仍按键名打码），
  不再原样输出 → 实测 12/15/18 层嵌套的 `api_key` 均不穿透。

---

## 3. 主代理额外修正（子代理未覆盖）

| 项 | 说明 |
|---|---|
| `tests/test_llm_config.py:129`（原失败用例） | payload 从 `ollama` 改为 `mock`，与用例自身注释「此处 mock provider，不真连网」一致。**已通过**。 |
| `tests/conftest.py` | 补钉 `ROLEPLAY_LLM_MODEL` / `ROLEPLAY_LLM_BASE_URL` / `ROLEPLAY_LLM_API_KEY`。此前只固定 provider，任何「带 override 但缺 base_url」的用例都会回落到本机 `.env` 真发请求 → 测试结果随机器漂移。 |
| `tests/test_repetition_guard.py` | `_build_orch` 由 `llm=MockLLMProvider()` 改为 `llm=llm`（原写法依赖已修复的 DI 缺陷）→ 9 failed 转 **21 passed**。 |
| `tests/test_prompt_p1.py` / `test_prompt_p2.py` | 更新 docstring：原文把「不走 `self._llm`」写成契约，修复后语义已变（不该让注释误导后人）。 |
| `api/deps.py` | 接线 `session_memory_max_chars`。 |
| `api/llm_config.py` | `_validate_base_url` 去重为薄封装，复用 `endpoint_guard`。 |

---

## 4. 唯一剩余失败：已证明是环境限制，非代码缺陷

`tests/test_plotrag_m0_verification.py::TestM03StrictGate::test_default_invocation_returns_zero`

它用 `subprocess` 跑 `scripts/audit_full_corpus.py` 并断言 `returncode == 0`；脚本在
`scripts/audit_full_corpus.py:298` 要写 `data/knowledge/_audit/full_issues.jsonl`。

**主代理决定性验证**：

```
文件是否存在: True（347022 字节，属性 Archive，IsReadOnly: False）
目录是否可写: NO   ← 连新建探针文件都被拒
直接覆写该文件: NO  ← Access to the path ... 被拒
```

目录在本会话**整体不可写**（沙箱限制），而文件本身并非只读 → 脚本逻辑本身正确，
**在正常可写环境下该用例应通过**。归类 **(e) 环境限制**。

---

## 5. 未做 / 已知遗留

1. **P2 其余项未修**（本轮聚焦 P0/P1）：
   - `api/ratelimit.py` 以 `client.host` 为键（反代后共用一个桶，未读 `X-Forwarded-For`）；
   - `config.py:66` 的 `llm_api_key`/`tavily_api_key`/`qq_ws_token` 仍为普通 `str` 而非 `SecretStr`；
   - `/api/llm/switch` 仍无鉴权且明文落盘 key；`cors_origins` 默认 `"*"`；
   - `InMemoryVectorStore.search(namespaces=...)` 仍静默忽略命名空间；
   - `memory.py:59` metadatas 越界 `IndexError`；
   - `retrieval_trace.py:284` `trace_path` 路径穿越（`'..\..\..\pwned'` 仍可逃逸）；
   - STT 幻觉过滤英文截断（`'I love music'→'I love'`）；
   - `persona_prompt.py` 仍有 7 处同类 `.format(value=...)`（当前模板来源受控、实测未崩，
     但若将来由外部卡片驱动会复现。建议在 `models/prompt_config.py` 收敛降级语义供两处共用）；
   - 桌面端 `POST /talk` 无调用方；打包文件含 `*.bak`/`*.tmp`；`.env.example` 缺 151 项。
2. **`tests/test_config.py:44` 的测试脆弱性**（我发现但**故意未改**，因该文件归另一代理且改动有风险）：
   `assert s.llm_temperature == 0.6`，而 `config.py:68` 的代码默认是 `0.8`。
   该断言只是**恰好读到本机 `.env`** 才通过 → 干净环境下会失败。
   建议改为显式传参或在 conftest 钉死，否则 CI 首次跑就会红。
3. **`_qa_tmpfix` 单独不足以消除 tmp_path 报错**，需配合 `--basetemp=<可写目录>`（子代理实测结论）。
4. 未做：真实 LLM 云端端到端、真实语音链路、Electron 启动、打包验证。

---

## 6. 复跑方式

```powershell
cd C:\Users\Lenovo\WorkBuddy\2026-07-27-16-45-03\roleplay-ai
$env:PYTHONPATH = "...\deliverables\qa_reports\_logs"   # 提供 _qa_tmpfix（沙箱 0o700 规避）
$base = Join-Path $env:TEMP ("qa_" + [guid]::NewGuid().ToString('N').Substring(0,6))
.\.venv\Scripts\python.exe -m pytest tests -q -p no:cacheprovider -p _qa_tmpfix --basetemp="$base"
```

独立复验脚本（主代理编写，可留存）：

| 脚本 | 用途 |
|---|---|
| [`_tools/verify_fixes_e2e.py`](deliverables/qa_reports/_tools/verify_fixes_e2e.py) | P0-1 DI 生效 + P0-2 膨胀受控 + mock 不回显 |
| [`_tools/verify_security_fixes.py`](deliverables/qa_reports/_tools/verify_security_fixes.py) | S1 拦截/防误伤 + S2a + S2b + S3（含反向对照） |

---

## 7. 修复后全仓健康度复检

| 检查 | 结果 |
|---|---|
| Python 语法（AST + 真实 compile 双重） | **597 个文件 0 错误**（唯一报告项是 `scripts/apply_missing_p37.py` 的 UTF-8 BOM — 已证实为**我检查方法的假阳性**，真 Python 可正常编译） |
| 内部 import 图 | **559 条全部可解析**，0 死引用 |
| 主干链路（真实 TestClient） | `/chat/stream` 200 + `text/event-stream`，`emotion` → `chunk` 事件序列正确 |
| 完整套件 | 1 failed / **1367 passed** / 8 skipped |

修复过程中被污染的 2 个探针占位文件（`fix/_probe_s1.py`、`_probe_s3.py`，内容是中文说明却挂 `.py` 后缀）
已改写为合法 Python 源——沙箱禁止删除/重命名，只能就地修正。
