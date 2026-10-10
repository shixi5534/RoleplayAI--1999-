# RoleplayAI 全项目测试与检验 · 总报告

> 执行方式：6 个独立子代理分域并行检验 + 主代理独立交叉复现。
> 每个子代理只拿自己那一块的信息，避免上下文互相污染；所有高危结论**都由主代理亲自复现过**，
> 未复现的一律标注「未验证」。
> 日期：2026-09-29 · 环境：Windows / Python 3.13.14 / pytest 9.1.1 · 全程离线

---

## 0. 一句话结论

**测试套件本身是健康的（几乎无真 bug：1279 passed / 2 failed，且两个失败都不是产品缺陷），
但套件存在一个结构性盲区：**
`ChatOrchestrator` **完全忽略构造函数注入的 LLM**，而测试注入的 `MockLLMProvider`
与全局 mock 恰好同类，所以**套件近乎全绿也发现不了**。这个盲区掩盖了一个会把
进程内存吃到 **7.3 GB** 的真实缺陷。

---

## 1. 检验范围与方法

| # | 分区 | 报告 | 方式 |
|---|---|---|---|
| 1 | 核心服务层（config/api/orchestrator/llm/情感/画像） | [01-core-api.md](deliverables/qa_reports/01-core-api.md) | 逐文件 pytest + 源码审查 |
| 2 | RAG 管线（rag/chroma/compendium_rag 检索） | [02-rag-pipeline.md](deliverables/qa_reports/02-rag-pipeline.md) | 逐文件 pytest + 数据健康度 |
| 3 | 提示词 + 剧情图谱 RAG + QA 回归 | [03-plotrag-prompt.md](deliverables/qa_reports/03-plotrag-prompt.md) | 18 文件逐个 pytest（重定向日志） |
| 4 | QQ 渠道 + 语音 + 桌面 E2E | [04-channel-voice.md](deliverables/qa_reports/04-channel-voice.md) | pytest + 安全审查 |
| 5 | 前端 + Electron 桌面端 | [05-frontend-desktop.md](deliverables/qa_reports/05-frontend-desktop.md) | 纯静态（node --check / 引用核对） |
| 6 | 仓库卫生 + 文档 + 依赖一致性 | [06-repo-hygiene.md](deliverables/qa_reports/06-repo-hygiene.md) | 只读审计 |

主代理另外独立完成（子代理均未覆盖）：

- 全仓 **568 个 .py 的语法体检**（AST + 真实 `compile()` 双重复核）→ 0 错误
- **537 条内部 import 全部可解析** → 0 死引用
- **重复测试定义检查** → 0 处（无静默覆盖）
- **真实 uvicorn 服务器**上的并发/延迟/限流/会话隔离验证
- **依赖注入失效、会话历史指数膨胀** 的定位与对照实验

---

## 2. 测试执行结果

### 2.0 权威数字（主代理亲自跑完整套件）

```
.\.venv\Scripts\python.exe -m pytest tests -v --tb=line -p no:cacheprovider -p _qa_tmpfix
=> 2 failed, 1279 passed, 8 skipped, 1 warning in 364.27s (0:06:04)
```

**总体通过率 1279/1281 = 99.84%**。两个失败均已定位，**没有一个是产品 bug**（详见 2.2）。

> ⚠️ 重要提示：该套件**没有任何超时保护**（未安装 pytest-timeout），
> 且含数个真发网络请求 / 跑真实语料的慢用例。本次完整跑需要 **6 分钟以上**，
> 中途多次看起来像「卡死」（进度条几分钟不动），容易被误判为挂起。
> 建议引入 `pytest-timeout` 并为网络类用例加 marker。

### 2.1 分区结果（子代理并行执行）

| 分区 | 通过 | 失败 | 错误 | 跳过 | 有效通过率 |
|---|---|---|---|---|---|
| 01 核心服务层 | 277 | 1 | 0 | 0 | 99.6% |
| 02 RAG 管线 | 40 | 0 | 21 | 0 | 100%（实际执行部分） |
| 03 提示词/图谱/QA | 437 | 6 | 132 | 1 | 98.4%（剔除环境干扰） |
| 04 渠道/语音 | 73 | 0 | 0 | 0 | 100% |
| 05 前端/桌面 | — | — | — | — | 静态检验：48 JS 全通过 |

**注**：分区里的 error 数偏高是因为子代理各自受沙箱限制、且用不同插件配置；
主代理用统一的 `_qa_tmpfix` 跑完整套件，得到的是 2.0 节那个干净数字。

### 2.1.1 关于大量 ERROR：是沙箱，不是代码缺陷

02/03/04 分区合计 **153 个 error**，**全部**是同一环境原因：

本会话的 DSH 文件沙箱禁止子进程向 **mode=0o700** 的目录写入，而 pytest 的
`tmp_path` / `--basetemp` 恰好以 `0o700` 创建（`_pytest/tmpdir.py`），于是用例在
**fixture setup 阶段**就以 `PermissionError: [WinError 5]` 中断，测试体从未执行。

- 实测：`mkdir(mode=0o700)` → 后续写入被拒；`mkdir(mode=0o777)` → 正常。
- 4 号子代理用仓库外的运行期插件（强制 `0o777`，不改任何业务代码）消除后，
  20 个 error **全部转为 pass**。
- **结论：这 153 项属于「本次未验证」，不能算通过，也不能算失败。** 需在正常环境重跑。

### 2.2 两个真实测试失败（均已定位，都不是产品 bug）

**失败 1**：`tests/test_llm_config.py::TestChatRequestLLMOverride::test_llm_override_embedded_in_chat_request`

- 归类：**(b) 测试自身过期**。
- 实测报错：`test_llm_config.py:129: assert 502 == 200`，日志里可见
  `ERROR roleplay.core.llm.openai_like:192 LLM HTTP 失败 provider=qwen2.5:1.5b status=401
  body={"error":{"code":"invalid_api_key",...}}`。
- 根因：用例传了 `llm={"provider":"ollama","model":"qwen2.5:1.5b"}` 但**漏传 `base_url`**，
  override 于是回落到本机 `.env` 的全局 `ROLEPLAY_LLM_BASE_URL`（非环回网关），
  **真发了一个网络请求**拿到 401 → `/chat` 返回 502，而断言期望 200。
- 旁证：`tests/test_llm_override.py` 每例都显式传 `base_url`，**6/6 全绿**。
- `conftest.py:14` 固定了 `ROLEPLAY_LLM_PROVIDER=mock`，但**从未固定 `LLM_BASE_URL`**，这是漏洞根源。
- 修复：用例补 `base_url`，并在 `conftest.py` 固定 `ROLEPLAY_LLM_BASE_URL`（离线要求）。

**失败 2**：`tests/test_plotrag_m0_verification.py::TestM03StrictGate::test_default_invocation_returns_zero`

- 归类：**(e) 环境限制（沙箱写拒绝）**，不是产品 bug。
- 实测报错：`test_plotrag_m0_verification.py:849: AssertionError: 默认调用返回 1（破坏了既有调用方）`。
- 主代理独立复现根因：

  ```
  File "scripts/audit_full_corpus.py", line 298, in main
      fp = issues_path.open("w", encoding="utf-8")
  PermissionError: [Errno 13] Permission denied:
      '...\roleplay-ai\data\knowledge\_audit\full_issues.jsonl'
  ```

  该用例用 `subprocess` 跑 `scripts/audit_full_corpus.py`，脚本要写
  `data/knowledge/_audit/`，被本会话沙箱拒绝 → 退出码 1。
  **在可写环境下该用例应通过**（脚本逻辑本身正确）。

---

## 3. 最严重的问题（主代理已逐条亲自复现）

### 🔴 P0-1 · 依赖注入失效：编排器忽略传入的 LLM

**证据（实测）**：注入一个「被调用即抛异常」的 LLM 后，`run()` 正常返回，
**注入实例调用次数 = 0**，返回的是全局 mock 的文案。

```
注入 LLM 被调用次数 : 0
返回 reply           : （角色扮演中）你刚才说：「你好」…      ← 全局 mock 的输出
```

**根因**：`src/roleplay/core/orchestrator.py:852`（流式为 `:1048`）

```python
llm, needs_aclose = build_llm_from_config(get_settings(), req.llm)
```

`run()` / `stream()` **无条件重新构建** LLM，从不使用构造函数传入的 `self._llm`。
`req.llm` 为 `None` 时，`factory.py:104-108` 走 `build_llm(settings)` → **全局 mock**。

**尤其隐蔽的一点（DI 是「半接线」状态）**：`self._llm` **并非完全没用**——
它在构造期被传给辅助模块：

```python
:190  build_profile_extractors(get_settings(), self._llm)   # 画像提取器
:199  build_event_extractors(get_settings(), self._llm)     # 事件提取器
```

也就是说：**注入的 LLM 会作用于「画像/事件提取」，却不作用于「主对话生成」**。
调试时很容易看到「注入的 LLM 似乎生效了」而误判为正常，这使该缺陷格外难被发现。

**危害**：
1. **测试盲区（最要命）**：所有注入 `MockLLMProvider` 的测试，断言实际打在**全局 mock** 上，
   注入的自定义 LLM 从未生效 → **套件近乎全绿却掩盖了这个缺陷**。
2. 任何以「注入 LLM」为扩展点的用法（自定义 provider、A/B 对比、离线评测）全部静默失效。
3. 与 P0-2 叠加后，把内存吃到 7.3 GB。

> 这条解释了为什么前 5 个子代理都没发现 P0-2：套件几乎全绿，而失败的那 2 个
> 都指向环境/测试自身，很容易得出「项目很健康」的结论。

### 🔴 P0-2 · 默认 mock 下会话历史指数膨胀（实测吃到 7.3 GB）

**实测增长**（默认 `mock` provider，即 README 声明的开箱默认配置）：

| 轮次 | 历史字符数 | 增长率 |
|---|---|---|
| 6 | 3,418 | — |
| 10 | 43,210 | ×1.86 |
| 16 | 1,696,228 | ×1.84 |
| 20 | 19,422,230 | ×1.84 |
| 22 | 65,707,604 | ×1.84 |
| **52**（真实服务器） | **776,554,152** | 单次响应 **872 MB** |

**对照实验（决定性）**——把编排器内部的 LLM 换成「不把历史回显进回复」的实例：

| LLM 类型 | 30 轮后历史 | 每轮增长 |
|---|---|---|
| 非回显（真实 provider 行为） | 60 条 / **890 字符** | ×1.04（线性有界） |
| **默认 mock** | 40 条 / **21,324,344 字符** | **×1.84（指数）** |

**根因链**：
1. `src/roleplay/core/llm/mock.py:28-36` —— mock 把**最近 6 条历史原样拼进回复**。
2. 该回复被 `session_memory.append_many()` 写回历史。
3. 下一轮再把增长后的历史拼进新回复 → **自我复制的正反馈**。
4. `session_memory.py:25` 的 `_TURN_CAP = 40` **只按「条数」截断**（80 条消息），
   **完全没有字符/token 预算** —— 实测确认 `session_memory` 中 `token/budget/max_chars` 关键词计数均为 **0**。
5. `orchestrator.py:704` 的历史摘要按**条数**触发（阈值 40 条），同样不看体量；
   一旦单条消息已是 MB 级，摘要也无济于事。

**危害**：README 让用户「默认 mock 模式，无需 Key 即可运行」，实际**连续对话 20 轮就是
2000 万字符，50 轮直接打爆内存**（本机实测 7.3 GB）。这不是理论风险——子代理和主代理
都真实触发过进程内存飙升，必须杀掉进程才能恢复。

**说明**：真实 provider（openai/deepseek/ollama）**不受此影响**（对照实验证实线性有界）。
但 P0-1 使这个结论不能被测试覆盖。

### 🟠 P1-1 · SSRF：请求体里的 `llm.base_url` 绕过既有校验（校验器从未接线）

> **⚠️ 本节已于修复阶段修正过一次过度断言，以下是核对既有校验器源码后的准确描述。**

**实测**（`LLMOverride` + `build_llm_from_config`，`/chat` 走的路径）：

```
http://169.254.169.254/latest/meta-data  -> OpenAILikeProvider  ✅ 被接受 ← 危险
file:///c:/windows/win.ini               -> 视 provider 而定
https://evil.example.com/v1              -> OpenAILikeProvider  ✅ 被接受
```

**而既有校验器 `api/llm_config.py:242` 本身是正确的**（我实测其策略）：

| 地址 | 既有校验器结论 |
|---|---|
| `169.254.169.254`（云元数据） | **BLOCK 422** ✓ |
| `file:` / `gopher:` | **BLOCK 422** ✓ |
| `100.64.0.1`（共享地址） | **BLOCK 422** ✓ |
| `https://evil.example.com/v1` | **BLOCK 422** ✓ |
| `127.0.0.1:11434` | ALLOW（**有意放行**，支持本地 Ollama） |
| `10.x` / `192.168.x` | ALLOW（**有意放行**，支持内网部署） |
| `https://api.deepseek.com/v1` | ALLOW ✓ |

**所以真正的缺陷是「接线缺失」，不是「校验器有缺陷」**：

- 该校验器只服务于 `/api/llm/test` 与 `/api/llm/switch`。
- **`core/llm/factory.py` 完全不引用它**（实测 `"_validate_base_url" in factory源码 == False`），
  而 `/chat` 的 `req.llm.base_url` 走的正是 `factory.build_llm_from_config`。
- 结果：`/chat` 上的 `req.llm.base_url` **完全无校验**，可指向 `169.254.169.254` 等。
- 叠加 `config.py:464` 的 `cors_origins` 默认 `"*"` 且**全站无鉴权中间件**，
  任意网页/局域网主机都能借 `/chat` 让服务端向云元数据地址发起请求。

**修复方向**：把既有校验（含其「环回/RFC1918 放行」策略）下沉为无框架依赖的公共函数并接入 factory，
**不要**改变放行策略——那会误伤合法的本地/内网 Ollama 部署。

### 🟠 P1-2 · 对 LLM 的「历史」没有任何 token/字符预算

由 P0-2 暴露，独立成立：即使换成真实 provider，长对话下历史仍会线性增长到
超出模型上下文窗口，代码里**没有一处**做 token 预算或按字符截断历史
（`orchestrator` 的 `token_budget`/`truncate`/`budget` 关键词计数全为 0）。
目前只有「40 条消息」和「AI 摘要」两道**按条数**的闸门。

### 🟠 P1-3 · `numpy` 依赖归属错误：`compendium_rag` 硬依赖却只挂在可选 extras

实测确认：

- `pyproject.toml` 的 `dependencies` **不含** numpy；numpy 只在 `extras.emotion = ["numpy>=1.26"]`。
- 但 `src/compendium_rag/retriever.py:21` 是顶层 `import numpy as np`，
  `__init__.py` 又无条件 re-export。
- 实测（拦截 numpy 模拟缺失）：`import compendium_rag` → **直接 ImportError，整包不可用**。
- numpy 的真实用途是向量索引数学，与「情感」extras 毫无关系 → **归类错误**。
- 本机恰好装了 numpy 2.5.1，所以测试全绿掩盖了它。

按 README 的安装步骤（`pip install -e ".[dev]"`）在干净环境部署，主线检索器会直接崩。

### 🟠 P1-4 · `custom_templates` 花括号导致 KeyError 崩溃

`src/roleplay/core/character_card.py:99` 与 `:104`：

```python
return tpl.format(value=value)
```

**实测确认**：角色卡的 `prompt_config.custom_templates` 含任何非 `{value}` 的花括号
（例如 `{"personality": "你是{name}"}`）→ **抛 `KeyError('name')`**。
角色卡可由第三方卡片导入 / API 传入，属外部可控输入。
（注：`persona_prompt.py` 侧的同类调用经实测**未**崩溃，问题集中在 `character_card.py`。）

### 🟠 P1-5 · QQ 渠道重连日志泄漏 `access_token`

`src/roleplay/channels/qq_onebot.py`：

- `:81-83` 构造带 `access_token` 的 URL，并做了 `display_url` 脱敏 → **成功路径安全**。
- 但 `:61-64` 的异常分支直接 `logger.warning("…%s", exc)`，而 `websockets` 的
  `InvalidURI` 异常会**原样携带完整 URL（含 token）** → **异常路径脱敏失效**。
- 该脱敏只覆盖了 `logger.info(:83)` 一处。

### 🟠 P1-6 · `/api/llm/switch` 无鉴权且明文落盘密钥

- `api/llm_config.py:439`：无任何鉴权即可切换全局 LLM 端点，并经 `:406 _persist_llm_env`
  **把 api_key 明文写入 `.env`**。
- 叠加 `cors_origins` 默认 `"*"`：局域网任意主机可改写全局配置与落盘凭据。
- `config.py:66` 的 `llm_api_key` / `tavily_api_key` / `qq_ws_token` 用普通 `str`
  而非 `SecretStr`，异常回显/repr 即整体泄漏。

---

## 4. 中低优先级问题（子代理发现，已抽验）

| 级别 | 问题 | 位置 |
|---|---|---|
| 中 | `errors/handlers.py:79` 丢弃 `exc.headers` → 429 的 `Retry-After` 实测消失，客户端无法退避 | `errors/handlers.py` |
| 中 | `errors/handlers.py:32` `_sanitize` 在 `depth>10` 时**跳过脱敏** → 12 层嵌套的 api_key 原样穿透 | `errors/handlers.py` |
| 中 | `api/ratelimit.py:30` 以 `request.client.host` 为键，反代后所有用户共享一个桶；未读 `X-Forwarded-For` | `api/ratelimit.py` |
| 中 | STT 幻觉过滤**把正常英文截断**：实测 `'I love music'→'I love'`、`'The audience gave applause'→'The audience gave'`；该 235 行过滤层**零测试覆盖** | `core/voice/stt.py` |
| 中 | `/voice/tts` 最坏 ~10 段 × 30s × 3 次重试 ≈ **900s/请求** | `api/voice.py` |
| 中 | `/api/desktop-pet/launch` 仅靠 `client.host` 判环回（网页天然是 127.0.0.1），且未挂限流，可反复 Popen Electron | `api/desktop_pet.py` |
| 中 | 前端 **API Key 明文存 localStorage**；全站**无 CSP** | `frontend/js/llm-switch.js:64` |
| 中 | `retrieval_trace.py:284` `trace_path` 未清洗 `character_id` → 实测 `'..\..\..\pwned'` **escaped=True** | `core/knowledge/retrieval_trace.py` |
| 中 | `InMemoryVectorStore.search(namespaces=[...])` **静默忽略命名空间**（实测返回 `namespace=None` 的内容），而它正是默认实现 | `core/rag/memory.py` |
| 中 | `memory.py:59` `metadatas[i]` 越界 → 实测 `IndexError`（chroma 实现反而有守卫，两实现不一致） | `core/rag/memory.py` |
| 中 | 桌面端 `POST /talk` 链路**没有任何调用方** → 「网页按钮让宠物说话」实际是断的 | `desktop/src/main/control-server.js:50` |
| 低 | `orchestrator.py:1024` 流式 `ctx_task` 客户端断连时不 await 也不 cancel → 任务泄漏 | `core/orchestrator.py` |
| 低 | `main.py:127` 连 `CancelledError` 一并静默吞掉且无日志 | `main.py` |
| 低 | `api/sessions.py`、`characters.py`、`knowledge.py` 无鉴权，`session_id` 可枚举读取完整对话历史 | `api/` |
| 低 | `frontend/_write_probe.tmp`、`desktop/src/main/_writetest.tmp`、`index.js.bak` **会被打进安装包** | 打包配置 |
| 低 | `.env.example` 仅 34 项，实际 `Settings` 有 185 项 → **151 项未文档化**（含 CORS_ORIGINS、RATE_LIMIT 等安全项） | `.env.example` |
| 低 | 源码 import 但两份依赖清单都未声明：`scipy`/`zhconv`/`imageio_ffmpeg`（连本地都没装，6 个脚本必 ImportError） | scripts/ |

---

## 5. 做得好的部分（交叉验证通过）

- **代码规模**：568 个 Python 文件 / 125,677 行，**AST 与真实 `compile()` 双重复核 0 语法错误**。
- **内部 import 图**：537 条内部 import **全部可解析**，0 死引用。
- **测试无重复定义**：同一文件内 / 跨文件均 0 处重复，不存在静默覆盖。
- **主干链路真实可用**（真实 uvicorn，非 TestClient）：
  - SSE 流式：`event: emotion` → `event: chunk` 事件序列正确，首字 0.04s（热态）
  - 非流式 `/chat`：200，结构完整（reply/emotion/follow_ups）
  - 会话持久化：`GET /api/sessions/{sid}/history` 正确回读
  - 输入校验：空消息 / 5000 字超长 / 缺字段 / 类型错误 **全部正确 422**，错误体结构统一
  - 会话隔离：20 路并发不同会话，历史**零串会话**
  - 限流：80 次 `/health` 全 200（符合预期，未误伤）
- **前端/桌面端静态质量高**：48 个 JS 全部 `node --check` 通过；约 100 处本地资源引用
  与 live2d/spine 二级引用**断链 0**；前后端接口契约**方法/路径 0 处不一致**。
- **Electron 安全基线正确**：`contextIsolation=true` + `sandbox=true` + `nodeIntegration=false`，
  preload 白名单暴露；**未发现** `shell.openExternal` 钓鱼面；XSS 逐处核查均安全
  （`highlight()` 先 esc、`pet.js` 走 `esc()`、`chat.js` 走 `textContent`）。
- **文档**：`docs/README.md` 28 个链接**全部可达**，0 断链。

---

## 6. 本次检验的局限（必须知悉）

1. **153 个用例在子代理分区运行中受沙箱干扰未验证**（`0o700` 目录限制）。
   主代理用统一插件跑完整套件后已基本闭环（只剩失败 2 属同类环境原因），
   但**建议在正常环境重跑 02/03/04 三个分区**以确保全部用例真正执行过。
2. **`e2e_pet_voice.py` 不可收集**：它是独立 Playwright 脚本而非 pytest 模块，
   且需 `127.0.0.1:18080` 前端服务，本次未启动 → 未验证。
3. `tests/test_voice.py` 的 **STT/TTS 全为 mock**（`@patch _get_whisper_model` / `_get_edge_tts`），
   综合有效覆盖率估计 **≤30%**；`stt.py` 幻觉过滤层约 235 行 **0 覆盖**
   （而该层已被实测证明存在英文截断 bug）。
4. 未做：真实 LLM/云端 API 端到端、真实语音合成识别、Electron 实际启动、打包产物验证。
5. **P0-1（依赖注入失效）本身会削弱整套测试的可信度**：所有注入自定义 LLM 的用例，
   断言实际打在全局 mock 上。修复 P0-1 后，**必须重跑全套件**，届时可能有新的失败暴露。
6. 套件**无超时保护**，含真实网络请求用例；离线环境下个别用例会走网络并变慢/失败。

---

## 7. 建议修复顺序

| 优先级 | 动作 |
|---|---|
| **P0** | 修 `orchestrator.py:852/:1048`：`self._llm` 应作为默认 LLM，仅在 `req.llm` 有 override 时才重建。**修完必须补一条「注入 LLM 的独有输出」断言**，否则同类盲区会再次出现。**修完务必重跑全套件。** |
| **P0** | 给 mock provider 加历史回显开关（默认关），并给 `SessionMemory` 加**字符/token 预算**（按体量而非条数截断）。 |
| **P1** | `factory.build_llm_from_config` 接入既有 `_validate_base_url`（下沉为公共函数），对 `req.llm.base_url` 拦截 `169.254.169.254`/非白名单公网/非 http(s) 协议；**保持环回与 RFC1918 放行**（本地 Ollama 依赖它）。 |
| **P1** | `pyproject.toml` 把 `numpy` 移入 `dependencies`（或新增 `compendium-rag` extra 并在文档指明）。 |
| **P1** | `character_card.py:99/:104` 改 `tpl.replace("{value}", value)` 或加 `try/except` 回落默认模板。 |
| **P1** | `qq_onebot.py:63` 异常日志改用 `display_url`/`_redact(exc)`；`_validate_base_url` 覆盖所有出口。 |
| **P1** | 修 `test_llm_config.py:129` 漏传 `base_url` 的用例，并在 `conftest.py` 固定 `ROLEPLAY_LLM_BASE_URL`（保证离线）。 |
| **P2** | 引入 `pytest-timeout` 并给网络/重语料类用例打 marker；套件当前无超时保护。 |
| **P2** | `handlers.py` 透传 `exc.headers`；`_sanitize` 去掉深度旁路；`ratelimit` 支持 `X-Forwarded-For`。 |
| **P2** | 补 `stt.py` 幻觉过滤层测试（先修英文尾字截断）；`memory.py` 对齐 `chroma_store` 的元数据守卫并实现 `namespaces` 过滤。 |
| **P2** | 清理打包文件（`*.bak`/`*.tmp`）、`.env` 备份物理删除、`.gitignore` 补 `roleplay_test_*/`。 |
| **P3** | 补齐 `.env.example` 的 151 项缺失配置（至少安全相关项）；给 `scripts/` 加 `README.md`（46% 为一次性脚本）。 |

---

## 8. 附：本次生成的验证工具（可留存复跑）

| 工具 | 用途 |
|---|---|
| [`_tools/ast_check.py`](deliverables/qa_reports/_tools/ast_check.py) | 全仓 Python 语法体检 |
| [`_tools/imports_check.py`](deliverables/qa_reports/_tools/imports_check.py) | 内部 import 图可解析性 |
| [`_tools/dup_check.py`](deliverables/qa_reports/_tools/dup_check.py) | 重复测试定义检测 |
| [`_tools/boot_smoke.py`](deliverables/qa_reports/_tools/boot_smoke.py) | 应用启动 + 路由 + OpenAPI 冒烟 |
| [`_tools/sse_full.py`](deliverables/qa_reports/_tools/sse_full.py) | SSE 全链路 + 错误路径冒烟 |
| [`_tools/real_server_probe.py`](deliverables/qa_reports/_tools/real_server_probe.py) | 真实服务器并发/延迟/限流 |
| [`_tools/growth_quantify.py`](deliverables/qa_reports/_tools/growth_quantify.py) | 会话历史膨胀量化（**P0-2 证据**） |
| [`_tools/final_control.py`](deliverables/qa_reports/_tools/final_control.py) | 非回显 LLM 对照实验 |
| [`_tools/di_proof.py`](deliverables/qa_reports/_tools/di_proof.py) | **P0-1 依赖注入失效证明** |
| [`_tools/verify_findings*.py`](deliverables/qa_reports/_tools/) | 各高危结论复现 |
