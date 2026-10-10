# 02 — 会话历史指数膨胀修复（P0-A 回显开关 + P0-B 字符预算）

**状态**：✅ 完成（`tests/test_session_memory.py` 新增 22 例；指定四文件套件 81 passed）
**工作目录**：`C:\Users\Lenovo\WorkBuddy\2026-07-27-16-45-03\roleplay-ai`
**解释器**：`.\.venv\Scripts\python.exe`

---

## 1. 改动清单

### 1.1 `src/roleplay/core/llm/mock.py`（P0-A：切断正反馈源）

| 位置 | 改动 |
|---|---|
| 行 1–27 | 模块 docstring 新增「⚠️ 历史回显默认关闭（P0-A 修复）」节，完整记录根因链与实测数据（6/10/22/52 轮字符数、×1.84/轮、872MB、7.3GB、对照实验 ×1.04） |
| 行 29 | `__init__(self, model: str = "mock-model", echo_history: bool = False)` |
| 行 32 | `self._echo_history = echo_history` |
| 行 53–57 | `tail = ""` → `if self._echo_history and history:` |

**新默认值：`echo_history=False`**（原行为等价于 `True`）。

- 默认关闭时 `generate()` **完全不读 history**，回复 = 固定模板 + 本轮用户输入，
  长度是常数（<200 字符）、`history=[]` 与 `history=[10 万字符]` 的返回**逐字节相同**（有断言）。
- `echo_history=True` 时保留原逻辑（`history[-6:]` + `"｜稍早的对话："`），演示/旧依赖可用。
- `generate_stream()` 未改动其调用关系——它 `await self.generate(...)` 后切片，
  故**自动继承**开关（有专门断言：流式拼接结果不含历史内容）。

**`tests/test_llm_local_split.py` 无需适配**：该文件只断言配置分流，不涉及 mock 文案；
且全仓 grep 确认**没有任何测试** grep「稍早的对话 / 角色扮演中 / 设定好的身份」（仅 `mock.py` 自身命中）。

### 1.2 `src/roleplay/core/session_memory.py`（P0-B：体量闸）

| 位置 | 改动 |
|---|---|
| 行 12–15 | docstring 新增「字符预算保护（P0-B）」设计要点 |
| 行 20 / 29 | 新增 `import logging`、模块级 `logger` |
| 行 43 | `_CHAR_BUDGET = 120_000`（默认预算，附 3 条依据注释） |
| 行 46 | `_MIN_KEEP_TURNS = 1`（至少保留最近 1 轮） |
| 行 49–50 | `_MAX_LOAD_FLOOR_BYTES = 4_000_000`、`_LOAD_BYTES_FACTOR = 32`（加载期文件大小闸） |
| 行 61–69 | `__init__(..., max_total_chars: int = _CHAR_BUDGET)`；`<=0` = 关闭字符闸（兼容旧行为） |
| 行 75 | `self._max_chars = max_total_chars` |
| 行 98–107 | `append()`：`if len(turns) > self._max * 2: del ...` → `self._trim(sid, turns)` |
| 行 111–133 | `append_many()`：同上，两条写入路径**都**走 `_trim` |
| **行 135–183** | **新增 `_trim(sid, turns)`**：先条数闸（原语义不变），再字符闸 |
| 行 269–296 | `_load_all()`：① 先 `stat().st_size` 过大即跳过并 warning；② 加载后 `self._trim` 一次 |

**`_trim` 的确定性语义**（无 O(n²)：单趟 `sum` + 单趟指针右移）：

1. **条数闸**：`len(turns) > max_turns*2` → 丢最旧，**语义与改动前逐字一致**。
2. **字符闸**：`sum(len(content)) <= max_total_chars` 则直接返回（正常会话零开销、零改动）。
3. **从最旧丢弃**，循环条件 `drop < len(turns) - 2*_MIN_KEEP_TURNS` —— 即**丢到剩最近 1 轮为止，绝不清空**。
4. 实际丢弃时记 1 条 `WARNING`（含会话 id、丢弃条数、剩余条数）。
5. **单条自身超预算**：不抛异常。该条保留在历史中（宁越预算不失忆），
   另记一条 `WARNING` 注明「最长 N 字符、未做截断」。

**保持不变**：`self._lock`（RLock）加锁范围、`_save` 的 tmp + `os.replace` 原子写、
`_path`/`_summary_path` 布局、`_safe` id 清洗、摘要文件跳过逻辑。`_trim` 在锁内、`_save` 之前调用，
故**落盘内容与内存一致**（有断言：重载后仍 ≤ 预算）。

### 1.3 `src/roleplay/config.py`（暴露配置项）

| 位置 | 改动 |
|---|---|
| 行 437–444 | 「角色卡 / 对话记忆」区块新增 `session_memory_max_chars: int = Field(120_000, ge=0, le=100_000_000)` |

写法对齐同文件 `history_summary_threshold`（`Field` + `ge/le` + 上方成段依据注释）。
环境变量名：**`ROLEPLAY_SESSION_MEMORY_MAX_CHARS`**（`env_prefix="ROLEPLAY_"` 自动生效）。

### 1.4 测试

| 文件 | 改动 |
|---|---|
| `tests/test_session_memory.py` | **新建**，22 例 |
| `tests/test_config.py` | 越界矩阵 += `("session_memory_max_chars", -1)`；`test_settings_defaults_still_valid` += 默认值断言 `== 120_000` |
| `tests/test_llm_local_split.py` | **未改**（确认无依赖） |

### 1.5 附：诊断脚本（非交付代码）

`deliverables/qa_reports/_tools/fix2_growth_probe.py` —— 复现/对照本修复的膨胀曲线（可重跑）。

---

## 2. 为何选 120_000 字符

三条独立依据（同时写入 `_CHAR_BUDGET` 上方注释，防后人静默删除）：

1. **与既有条数上限对齐** → 不误伤正常会话：
   `_TURN_CAP = 40` 轮，云端档 `cloud_max_tokens_per_reply = 2048`（≈ 中文 3 000 字/条），
   最坏满长 40 轮 × 3 000 字符 ≈ **120 000**。即：**40 轮正常长度对话刚好装得下，一条不丢**。
2. **与模型上下文对齐**：≈ 70k–120k token，给 persona / RAG / 剧情注入与当轮输出留余量，
   不至于把上下文窗口挤爆。
3. **与故障量级拉开 4 个数量级**：被测污染会话达 **7.77 亿字符**；120k 比它低 4 个数量级——
   既能立刻切断膨胀，又远高于正常会话（实测 52 轮正常对话仅 1 880 字符）。
4. **可覆盖**：`ROLEPLAY_SESSION_MEMORY_MAX_CHARS`，`<=0` 即关闭该闸回到纯条数上限。

---

## 3. 测试结果

### 3.1 指定套件（任务要求命令，`_qa_tmpfix` 消除沙箱 0o700 噪声）

```
.\.venv\Scripts\python.exe -m pytest tests\test_session_memory.py tests\test_config.py \
    tests\test_llm_local_split.py tests\test_api.py -q --tb=short -p no:cacheprovider -p _qa_tmpfix
```

**`exit=0` → `81 passed, 1 warning in 27.79s`**（warning 为既有 starlette/httpx 弃用提示，与本次无关）

> **不加 `-p _qa_tmpfix` 时**：`65 passed, 16 errors`，16 条**全部**是
> `PermissionError: [Errno 13] ... pytest-of-Lenovo\pytest-NN\.lock` ——
> 即环境提示里已说明的沙箱禁止 `mode=0o700` 目录（pytest `tmp_path` 恰好如此），
> 与项目代码无关。加运行期插件（不改项目代码）后全绿。

### 3.2 宽回归（13 个 LLM/记忆/编排相关文件）

**`320 passed, 1 skipped, 9 failed`** —— 9 个失败**全部**在 `tests/test_repetition_guard.py`，
根因是**另一代理尚未提交的 `orchestrator.py::_resolve_llm` 改动**（`git diff` 显示 +33/−4 未提交）：

- 现象：`ScriptedLLM.calls == 0`，回复落到全局 mock（`（角色扮演中）你刚才说：…`）。
- 证据：`_resolve_llm` 只认 `req.llm` override，而该测试用 `monkeypatch` 打桩
  `build_llm_from_config`；注入的 `MockLLMProvider` 因此不再被调用。
- 判定：**与本次改动无关**（我未触碰 `orchestrator.py`；改动前该路径本就如此）。
  记录此条供主代理与 orchestrator 代理整合时处理。

### 3.3 核心证据：膨胀曲线对照

`_tools/fix2_growth_probe.py`（mock × SessionMemory 真实反馈环，单会话累计字符）：

| 配置 | @6 轮 | @10 轮 | @22 轮 | @52 轮 |
|---|---|---|---|---|
| **PRE-FIX**（`echo=True`，无预算） | 3 882 | 48 882 | **74 287 556** | —（跳过，会 OOM） |
| 只修 mock（`echo=False`，无预算） | 270 | 450 | 1 014 | 1 880 |
| **POST-FIX**（默认：`echo=False` + 120k） | 270 | 450 | 1 014 | **1 880** |
| POST-FIX 全开（`echo=True` + 120k） | 3 882 | 48 882 | 118 745 | 120 965（钳住） |

- 修复前 22 轮即 **7 428 万字符**，与缺陷报告 6 570 万同量级、同一 ×1.84/轮曲线。
- 默认路径 52 轮后仅 **1 880 字符** —— 指数膨胀**彻底消失**（回归测试锁定）。
- 即便把回显重新打开，字符闸仍把 52 轮钳在 **≈121k**（`120 965`，仅因数条单条自身超预算而略越界，
  符合「单条超长不截断、保留并 warning」的明确约定）——**两道闸互为兜底**。

新增测试覆盖（`tests/test_session_memory.py`，22 例）：
- 字符预算生效（`append_many` 与单条 `append` **两条路径**各一例）
- 至少保留最近 1 轮（`hist[-1] == 最后一条`）
- 单条超长不抛异常 + 保留 + 记 warning（`caplog`）
- mock 默认不回显（含 `history=[]` vs 10 万字符历史**逐字节相同**、流式路径、`echo_history=True` 兼容）
- **膨胀回归**：20 轮递增写入 ≤ 预算且 < 10⁵（核心证据）
- **端到端反馈环**：mock 回复写回历史 20 轮，总字符 ≤ 50k、单轮回复 < 1k
- 条数闸语义不变 / `<=0` 关闭闸 / 落盘重载仍受约束 / 加载期拒载膨胀遗留大文件
- 布局与原子写语义不变（落盘仅 `sess.json`、无残留 tmp）/ 摘要文件仍跳过

---

## 4. 遗留项 / 交接

1. **`session_memory_max_chars` 尚未接线到 `api/deps.py`**（按指令**未改**该文件）。
   当前 `deps.py:48` 为 `SessionMemory(Path(s.session_memory_dir))`——
   **默认值 120_000 已经生效**（类默认即此值），但 `.env` 里的
   `ROLEPLAY_SESSION_MEMORY_MAX_CHARS` **暂时不会传到实例**。主代理整合时改为：

   ```python
   SessionMemory(Path(s.session_memory_dir), max_total_chars=s.session_memory_max_chars)
   ```

   （`enable_session_memory=False` 分支不变。）
2. **`tests/test_repetition_guard.py` 9 例失败**：起因是 orchestrator 未提交的 DI 改动，非本批次缺陷；
   归 orchestrator 代理/主代理。
3. **已在内存中的膨胀会话**：`_load_all` 的文件大小闸（≥4MB 拒载）只保护**重启后**；
   进程内已存在的亿级历史，下一次写入即被 `_trim` 压回预算。
4. **单条超预算时仍会略越界**（按设计：宁越界不失忆），故 `get_history` 的总字符数在
   极端情况下可 > `max_total_chars`。若产品要求**硬**上限，需改为对该条做字符级截断——
   本次未做（会改变角色可见记忆内容，属语义决策，留待确认）。
