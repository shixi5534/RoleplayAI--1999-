# 03 · Prompt / PlotRAG 只读测试检验报告

- 日期：2026-09-30
- 范围：`tests\` 下 18 个指定文件（**不含** `test_plot_graph_retrieval_live.py`）
- 方式：**只读**；未修改任何项目源文件、配置文件或测试文件
- Python：`.\.venv\Scripts\python.exe`（3.13.14），全程离线，未执行 `pip install`
- 唯一写入：本报告自身

## 0. 结论摘要（先看这里）

| 指标 | 数值 |
|---|---|
| 语句级统计（passed / failed / skipped / errors） | **437 / 6 / 1 / 132**（共收集 576） |
| 有效通过率（剔除沙箱 error 后） | **437 / 444 = 98.4%** |
| 原始通过率（error 计为未通过） | 437 / 576 = **75.9%** |
| 跳过率 | **1 / 576 = 0.17%**（无任何文件 >30%） |
| (a) 类真 bug（测试观测到的运行时失败） | **0** |
| (a) 类真 bug（源码抽查发现，可复现） | **1**（提示词模板 `KeyError` 崩溃）+ 3 项健壮性缺陷 |
| 不可验证测试占比 | **138 / 576 = 24.0%** |

> **核心判断**：本套件**没有一个真正的断言失败暴露产品缺陷**。全部 6 个 `failed` 与 132 个 `errors` 均源于**同一环境原因**——本会话沙箱禁止子进程在 `$env:TEMP` 与工作区创建/枚举目录，导致所有 `tmp_path` / `tempfile` 用例在 fixture 阶段就被 `PermissionError (WinError 5)` 打断。唯一真正的产品级缺陷来自**源码只读抽查**（见 §4 第 1 条）。

---

## 1. 逐文件结果表

数字取自各文件 pytest 尾行（`-q --tb=line`）。

| 文件 | 通过 | 失败 | 跳过 | errors | 耗时 | 结论 |
|---|---|---|---|---|---|---|
| test_prompt_p0.py | 17 | 0 | 0 | 1 | 0.08s | 通过（1 例被沙箱阻断） |
| test_prompt_p1.py | 31 | 0 | 0 | 0 | 0.14s | **完全通过** |
| test_prompt_p2.py | 18 | 0 | 0 | 0 | 0.18s | **完全通过** |
| test_plotrag_p0.py | 18 | 0 | 0 | 9 | 16.07s | 部分受阻（33% 未验证） |
| test_plotrag_m0_hardening.py | 6 | 0 | 0 | 21 | 0.26s | 大部分受阻（78% 未验证） |
| test_plotrag_m0_verification.py | 64 | 1 | 0 | 28 | 18.69s | 部分受阻（1 失败亦为沙箱） |
| test_plotrag_semantic.py | 0 | 0 | 0 | 24 | 0.31s | **全部受阻（0% 验证）** |
| test_plotrag_negative_guard.py | 60 | 0 | 0 | 3 | 0.23s | 基本通过 |
| test_plotrag_trace.py | 21 | 0 | 0 | 2 | 0.11s | 基本通过 |
| test_plotrag_optimization.py | 31 | 0 | 0 | 20 | 35.52s | 部分受阻（39% 未验证） |
| test_plotrag_eval_m12.py | 31 | 0 | 0 | 0 | 0.10s | **完全通过** |
| test_plotrag_eval_metrics.py | 11 | 0 | 0 | 0 | 0.07s | **完全通过** |
| test_plotrag_huiji_canon.py | 4 | 0 | 0 | 12 | 0.14s | 大部分受阻（75% 未验证） |
| test_plotrag_real_dialogue.py | 13 | 0 | 0 | 0 | 26.81s | **完全通过** |
| test_plot_graph.py | 9 | 1 | 0 | 11 | 0.18s | 部分受阻（失败亦为沙箱） |
| test_plot_timeline.py | 7 | 0 | 0 | 0 | 1.45s | **完全通过** |
| test_wiki_canonical_coverage.py | 8 | 0 | 0 | 0 | 1.06s | **完全通过** |
| test_qa_verification.py | 88 | 4 | 1 | 1 | 1.27s | 失败 4 例全为沙箱 tmp_path |

合计：通过 437 · 失败 6 · 跳过 1 · errors 132。

---

## 2. 失败明细与归类

### 2.1 归类汇总

| 类别 | 数量 | 说明 |
|---|---|---|
| (a) 真 bug | **0** | 无任何测试断言失败指向产品缺陷 |
| (b) 测试过期（基线漂移） | 0 | 未观察到 |
| (c) 缺依赖 | 0 | 无 `ModuleNotFoundError` / `ImportError` |
| (d) 需网络或真实 LLM | 0 | 无网络/LLM 相关失败；`eval_m12`、`real_dialogue` 全通过 |
| (e) 环境限制（沙箱拒绝写） | **138** | 全部 6 个 `failed` + 132 个 `errors` |

### 2.2 唯一根因（138 例共用）

```
E   PermissionError: [WinError 5] 拒绝访问。:
    'C:\Users\Lenovo\AppData\Local\Temp\dsh-N5iPDo\pytest-of-Lenovo'
```
- 触发点：pytest `tmp_path`/`tmp_path_factory`（`tempfile.py:272`）、`pathlib._local.py` 的 `iterdir/open`。
- 已独立复现并定位：`$env:TEMP` 下已存在一个 ACL 受限的残留目录 `pytest-of-Lenovo`（`Get-Acl` 抛 `UnauthorizedAccessException`，无法枚举）；即使改用自建 `--basetemp`，Python **子进程** 在该 base 内创建/写入/枚举子目录同样被拒（`PermissionError [Errno 13]`）。工作区内新建目录亦被拒（`deliverables\qa_reports\_pt` → `WinError 5`）。
- 即：这是**沙箱的子进程写权限边界**，不是项目缺陷。

### 2.3 逐条失败明细

| # | node id | 类别 | 根因（一句） | 报错（≤3 行） |
|---|---|---|---|---|
| 1 | `test_prompt_p0.py::test_store_roundtrip_keeps_p0_fields` | (e) | `tmp_path` fixture 建目录被沙箱拒 | `PermissionError: [WinError 5]` on `pytest-of-Lenovo` |
| 2 | `test_plotrag_m0_verification.py::TestM03StrictGate::test_default_invocation_returns_zero` | (e) | 该用例 `subprocess` 跑 `scripts/audit_full_corpus.py`，脚本写 `data\knowledge\_audit\full_issues.json` 被拒 → 退出码 1（非 0） | `AssertionError: 默认调用返回 1`；实际 stderr：`fp = issues_path.open("w")` → `PermissionError: [Errno 13] Permission denied: ...\data\knowledge\_audit\full_issues.json` |
| 3 | `test_plot_graph.py::test_orchestrator_plot_path_isolated_and_optional` | (e) | 用例自建 `plot_orch_*` 临时目录，`iterdir` 被拒 | `pathlib._local.py:722 PermissionError: [WinError 5]` on `...\plot_orch_bect9cl2\` |
| 4 | `test_qa_verification.py::test_b3_inject_count_leq_topk` | (e) | `tempfile` 目录创建被拒 | `tempfile.py:272 PermissionError: [WinError 5]` |
| 5 | `test_qa_verification.py::test_b3_persist_schedule_cursor` | (e) | 同上 | 同上 |
| 6 | `test_qa_verification.py::test_b3_disabled_no_inject_no_extract` | (e) | 同上 | 同上 |
| 7 | `test_qa_verification.py::test_b3_reminder_negative_window_and_garbage` | (e) | 同上 | 同上 |

**errors（132）分布**：`m0_verification` 28 · `semantic` 24 · `m0_hardening` 21 · `optimization` 20 · `huiji_canon` 12 · `plot_graph` 11 · `plotrag_p0` 9 · `negative_guard` 3 · `trace` 2 · `prompt_p0` 1 · `qa_verification` 1。
经逐文件 `^E ` 行分类：**132/132 全部为 `PermissionError`**，无一例其他异常。

> 关键区分：`test_plotrag_m0_verification.py` 与 `test_plot_graph.py` 各有 1 个 `failed` 而非 `error`，容易被误读为「真 bug」。两条均已追到沙箱写拒绝（见 #2、#3），属 (e)。

---

## 3. 跳过率分析

- 全量跳过：**1 例 / 576 = 0.17%**，**无任何文件跳过率 >30%**。
- 唯一跳过：`test_qa_verification.py:1128`
  ```python
  pytest.skip(f"P2 观察点：跨 UserProfile 实例共享 KB 并发写同 key 产生 {n} 条（实例级锁不互斥）")
  ```
  - 性质：**条件式观察点**（`pytest.skip` 内联调用，仅当并发写未复现出预期条数时跳过），非依赖缺失。
  - 判定：**可接受**，但属「条件满足即静默不测」——建议改为 `xfail(strict=False)` 或断言具体行为，避免真实并发缺陷被 skip 掩盖。

### 是否「拿缺依赖/网络当借口」？

**否，本套件在这一点上是干净的。** 证据：
- 无 `ModuleNotFoundError` / `ImportError` / `ConnectionError` / LLM 超时类跳过或失败；
- 最可能依赖外部资源的两个文件 `test_plotrag_eval_m12.py`（31 通过）与 `test_plotrag_real_dialogue.py`（13 通过）**全量通过**，说明其 RAG/LLM 交互走夹具或 mock，未以「缺依赖/需真实 LLM」为由回避；
- 唯一 skip 是行为观察点，不是环境借口。

**但存在反向风险（需重视）**：本套件**不是靠 skip 掩盖**，而是靠**沙箱 error 大面积未验证**。24.0%（138/576）的用例根本没跑到断言，其中 `test_plotrag_semantic.py` **0 通过 / 24 errors**，实质是「整文件未验证」。这比 skip 更隐蔽——在 CI 汇总里 `errors` 常被忽略。

---

## 4. 提示词源码抽查（只读，8 项）

抽查文件：`src\roleplay\core\persona_prompt.py`（815 行）、`src\roleplay\models\prompt_config.py`（122 行）；为确认可利用性另行只读 `core\character_card.py`、`core\orchestrator.py`、`core\llm\openai_like.py`、`models\character.py`。

### 🔴 1. (a) 真 bug — 自定义模板未做 `format` 兜底，`KeyError` 冒泡并使请求崩溃

`character_card.py:98/103`（字段模板）与 `persona_prompt.py:614`（tone 块）均为：

```python
tpl = cfg.custom_templates.get(field) or _DEFAULT_TEMPLATES[field]
return tpl.format(value=value)          # ← 仅提供 {value}，其它占位符会 KeyError
```

- **越界索引**：已核查，`_length_band`→`_LENGTH_BANDS[idx]` 有 `min(idx+1, len-1)` 钳制，`ordered_fields` 无索引访问，**未发现越界索引**。
- **注入**：`field_order`/`enabled_fields` 均按 `ALL_FIELDS`/`CARD_FIELDS` 白名单过滤（`prompt_config.py:117`、`character_card.py:137`），**未发现字段名注入**。
- **本条第 1 项是「静默失败」的反面——它不静默，它崩溃**。实测：
  ```
  '你是{name}'   -> RAISES KeyError 'name'
  '{value}{unknown}' -> RAISES KeyError 'unknown'
  ```
  端到端复现（角色卡 JSON → 产品路径）：
  ```python
  card = {"name":"A","personality":"冷静",
          "prompt_config":{"custom_templates":{"personality":"你是{name}"}}}
  resolve_system_prompt(character_card=json.dumps(card), fallback_prompt="FB", ...)
  # -> PROPAGATES: KeyError 'name'
  ```
- **影响**：`custom_templates` 由角色卡携带（可来自导入的第三方卡片 / API `card_json`）。含单个非 `{value}` 花括号的模板即让该角色**所有对话请求抛未捕获 `KeyError`**，且 `resolve_system_prompt` 的 `fallback_prompt` 兜底**不会生效**（异常发生在渲染阶段，早于兜底判断）。属可用性/健壮性缺陷。
- **建议**：`tpl.replace("{value}", value)`，或 `format_map(defaultdict(str, value=value))`，或 `try/except (KeyError, IndexError)` 回落默认模板并 `logger.warning`。

### 🟠 2. (a-low) `PromptConfig.ordered_fields()` 不去重 → 同一字段可被渲染多次

```python
order = [f for f in (self.field_order or DEFAULT_ORDER) if f in ALL_FIELDS]
```
实测 `field_order=["name","name","tone"]`：
```
ordered= ['name', 'name', 'tone', ...]   # dup_count_name= 2
sections= ['你是A。', '你是A。', '人设：P']   # name 段重复注入 prompt
```
重复项会**逐字重复注入 system prompt**，浪费 context 且可被用来放大某段指令权重。非法重复应去重（保序）。

### 🟡 3. 健壮性 — 4 个上下文构建器对 `metadata=None` 未兜底

`persona_prompt.py:238/266/300/332` 直接 `c.metadata`（`.get(...)` / 传入 `_source_label`），而**同文件** `_score_group` 与 `edge` 取值处都写了 `c.metadata or {}`——同文件内写法不一致：

```
RetrievedChunk(text="t", score=0.9, metadata=None)
  -> RAISES AttributeError 'NoneType' object has no attribute 'get'
```
`RetrievedChunk.metadata` 默认 `field(default_factory=dict)`，故仅当检索实现显式传 `None` 时可达 → **潜在**（latent）而非现网必现。建议统一 `c.metadata or {}`。

### 🟡 4. 静默失败 — `PromptConfig.from_any` 吞掉非法配置且不留痕

`prompt_config.py:105-108`：
```python
try:    return cls.model_validate(raw)
except Exception:  # noqa: BLE001
    return cls()
```
实测 `{"enabled_fields":"notalist"}` / `"{oops"` / `123` 均**静默**回落默认配置。注释称「宽松解析（不抛异常）」是有意设计，但**无 `logger.warning`**：用户写错角色卡的提示词开关时，字段开关**静默失效**、表现为「配置没生效」，排查成本高。建议至少 `logger.warning("prompt_config 解析失败，回落默认")`。

### ✅ 5–8. 未发现问题的项（已核查）

5. **提示词拼接注入**：`user_prefix` 在 `openai_like.py:96` 经 `f"{user_prefix.strip()}\n\n{user}"` 拼接，仅作纯文本前缀，未参与 `format`/`eval`；`orchestrator.py:568-576` 未启用分层时返回 `{}`，保持零回归——**未发现注入面**。
6. **白名单过滤**：`field_order`/`enabled_fields`/`footer_fields` 均对 `ALL_FIELDS`/`CARD_FIELDS` 过滤，越界字段名被丢弃——**安全**。
7. **`_filter_chunks` 相对门**：分组键 `_score_group` 明确处理 `plot_graph`/`plot_lexical` 量纲差异，单组与多组路径都覆盖了「已限量通道豁免」——逻辑自洽，注释与实现一致。
8. **`_build_lorebook` 预算**：`len(matched) >= 40 or used_chars >= 4000` 双上限，单条 `content[:2000]` 截断——**无无界膨胀**。

---

## 5. 复现方式

```powershell
cd C:\Users\Lenovo\WorkBuddy\2026-07-27-16-45-03\roleplay-ai
.\.venv\Scripts\python.exe -m pytest tests\test_prompt_p0.py -q --tb=line -p no:cacheprovider *> "$env:TEMP\pr_p0.txt"; "exit=$LASTEXITCODE"
Get-Content "$env:TEMP\pr_p0.txt" -Tail 20
Select-String -Path "$env:TEMP\pr_p0.txt" -Pattern '^(FAILED|ERROR)' | Select-Object -First 25
```

**要恢复 138 个未验证用例**，需在允许子进程写临时目录的环境（非本沙箱，或放开 TEMP 子进程写权限）重跑；本会话已被拒绝写入 TEMP/工作区子目录，无法通过 `--basetemp` 规避（已实测失败）。

## 6. 待办建议（按优先级）

1. **修 `persona_prompt.py:614` / `character_card.py:98,103` 的 `format` 崩溃**——唯一确认的产品级真 bug，可被角色卡 JSON 触发。
2. **重跑被沙箱阻断的 138 例**，重点 `test_plotrag_semantic.py`（当前 0% 验证）与 `m0_hardening`/`huiji_canon`（≥75% 未验证）；这批用例承载 PlotRAG 语义/加固断言，是目前最大的验证盲区。
3. `ordered_fields()` 去重；4 个构建器 `metadata or {}` 统一兜底；`from_any` 失败加 warning 日志。
4. 清理/删除 TEMP 下 ACL 受限的残留目录 `pytest-of-Lenovo`，否则本机后续任何 `tmp_path` 用例都会继续假失败。
5. `test_qa_verification.py:1128` 的条件 skip 建议改为 `xfail(strict=False)` 并保留告警，避免并发缺陷被静默掩盖。
