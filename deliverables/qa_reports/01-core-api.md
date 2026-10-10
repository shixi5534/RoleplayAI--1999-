# 01 — 核心 API 层测试检验报告（只读）

- 工作目录：`C:\Users\Lenovo\WorkBuddy\2026-07-27-16-45-03\roleplay-ai`
- 解释器：`.\.venv\Scripts\python.exe`（Python 3.13.14，pytest 9.1.1）
- 全程离线、未执行任何 `pip install`、**未修改任何项目源文件**（[tests/conftest.py](tests/conftest.py) 亦未改动）
- 测试逐个文件独立进程运行，每文件 480 s 超时；**无超时**
- 原始 pytest 输出落在 `$env:TEMP\qa_logs2\`，再转录至 [_logs/](deliverables/qa_reports/_logs/)（本会话沙箱禁止 shell 直接写入工作区，详见 [_logs/01-runner-and-commands.md](deliverables/qa_reports/_logs/01-runner-and-commands.md)）

> ⚠️ **环境前置说明（影响结论解读）**：本会话的 DSH 沙箱禁止写入 `mode=0o700` 的目录，而 pytest 的 `tmp_path`/basetemp 恰以 `0o700` 创建（`_pytest/tmpdir.py:139,158`、`_pytest/pathlib.py:232`）。首轮因此产生 **6 failed + 1 error 的纯沙箱伪失败**（`PermissionError: [WinError 5]`，集中在 `test_orchestrator.py` 与 `test_security.py`）。已用**仅运行期**插件 `_qa_tmpfix.py`（只放在 `_logs/`，不被 `src/`、`tests/` 引用）+ 每文件全新 `--basetemp` 消除。**下表为消除后的真实结果**，被消除的伪失败逐条记录在 [_logs/03-failure-detail.txt](deliverables/qa_reports/_logs/03-failure-detail.txt) B 节。

---

## 1. 总表

| 文件 | 通过 | 失败 | 跳过 | 错误 | 耗时 | 结论 |
|---|---:|---:|---:|---:|---:|---|
| [tests/test_config.py](tests/test_config.py) | 23 | 0 | 0 | 0 | 0.76 s | ✅ 通过 |
| [tests/test_api.py](tests/test_api.py) | 14 | 0 | 0 | 0 | 26.35 s | ✅ 通过 |
| [tests/test_security.py](tests/test_security.py) | 8 | 0 | 0 | 0 | 0.06 s | ✅ 通过 |
| [tests/test_orchestrator.py](tests/test_orchestrator.py) | 14 | 0 | 0 | 0 | 0.29 s | ✅ 通过 |
| [tests/test_llm_config.py](tests/test_llm_config.py) | 10 | **1** | 0 | 0 | 2.78 s | ❌ 1 例失败（(b) 测试过期） |
| [tests/test_llm_key_persist.py](tests/test_llm_key_persist.py) | 6 | 0 | 0 | 0 | 0.72 s | ✅ 通过 |
| [tests/test_llm_local_split.py](tests/test_llm_local_split.py) | 21 | 0 | 0 | 0 | 0.27 s | ✅ 通过 |
| [tests/test_llm_override.py](tests/test_llm_override.py) | 6 | 0 | 0 | 0 | 0.41 s | ✅ 通过 |
| [tests/test_emotion.py](tests/test_emotion.py) | 41 | 0 | 0 | 0 | 0.41 s | ✅ 通过 |
| [tests/test_mapping.py](tests/test_mapping.py) | 22 | 0 | 0 | 0 | 0.07 s | ✅ 通过 |
| [tests/test_profile.py](tests/test_profile.py) | 18 | 0 | 0 | 0 | 0.68 s | ✅ 通过 |
| [tests/test_character_card.py](tests/test_character_card.py) | 12 | 0 | 0 | 0 | 0.07 s | ✅ 通过 |
| [tests/test_character_normalizer.py](tests/test_character_normalizer.py) | 24 | 0 | 0 | 0 | 0.13 s | ✅ 通过 |
| [tests/test_repetition_guard.py](tests/test_repetition_guard.py) | 21 | 0 | 0 | 0 | 0.18 s | ✅ 通过 |
| [tests/test_knowledge.py](tests/test_knowledge.py) | 16 | 0 | 0 | 0 | 3.37 s | ✅ 通过 |
| [tests/test_extractors.py](tests/test_extractors.py) | 21 | 0 | 0 | 0 | 0.26 s | ✅ 通过 |
| **合计** | **277** | **1** | **0** | **0** | **36.8 s** | **通过率 99.64%** |

16 个文件全部运行完毕，无一超时（最慢 [tests/test_api.py](tests/test_api.py) 26.35 s）。
每个文件各产生 1 条**完全相同**的告警，来源为第三方库，非项目缺陷：

```
.venv\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning:
Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
```

逐文件原始判定行见 [_logs/02-results-by-file.txt](deliverables/qa_reports/_logs/02-results-by-file.txt)。

---

## 2. 失败明细

**唯一失败（1/278）**

- **node id**：`tests/test_llm_config.py::TestChatRequestLLMOverride::test_llm_override_embedded_in_chat_request`
- **归类**：**(b) 测试自身过期**（环境依赖型用例，非被测代码 bug）

**根因（一句话）**：该用例传 `llm={"provider":"ollama","model":"qwen2.5:1.5b"}` 却**不传 `base_url`**，于是 override 回退到机器 `.env` 里的全局 `ROLEPLAY_LLM_BASE_URL`（指向本机一个 OpenAI 兼容网关而非 Ollama），请求真的发了出去并收到 401，`/chat` 遂以 502 返回，而断言期望 200。

**关键报错行（≤5 行）**：
```
tests/test_llm_config.py:129: in test_llm_override_embedded_in_chat_request
    assert resp.status_code == 200
E   assert 502 == 200
E    +  where 502 = <Response [502 Bad Gateway]>.status_code
ERROR roleplay.core.llm.openai_like:openai_like.py:192 LLM HTTP 错误
  provider=qwen2.5:1.5b status=401 body={"error":{"code":"invalid_api_key", ...}}
```

**为什么是 (b) 而不是 (a)——已实测验证**：
1. 用例自带注释「此处 mock provider，不真连网」，但单行 provider override 恰恰替换掉了 mock provider。断言 `== 200` 实际取决于**本机 `.env` 指向哪个端点**。[tests/conftest.py](tests/conftest.py) 固定了 `ROLEPLAY_LLM_PROVIDER=mock`，却**从未固定 `ROLEPLAY_LLM_BASE_URL`**，而 pydantic-settings 对其余字段仍以 `.env` 为准。
2. 实测该 override 的真实解析结果（未暴露任何密钥）：
   ```
   override base_url host is loopback = False
   override resolved to ollama default = False
   needs_aclose = True | client = OpenAILikeProvider
   ```
   即**没有**落到 `http://localhost:11434/v1`，而是继承了非环回的全局 base_url —— 与用例注释的假设完全相反。
3. 兄弟用例 `test_llm_override_rejects_bad_provider` 通过，因为它在构建 LLM 客户端前就被参数校验挡下（422）。
4. [tests/test_llm_override.py](tests/test_llm_override.py) 每个用例都**显式传 `base_url`**，6/6 全绿 —— 反证缺陷在于本用例漏传 `base_url` 及其过期注释。

**排出 (c) / (d)**：无缺依赖；用例本意就不该走网络（注释自述），故非网络依赖型。

**被消除的沙箱伪失败（归类 (e)，既非 (a) 也非 (b)）**：首轮 `test_security.py` 报 `7 passed, 1 error`、`test_orchestrator.py` 报 `6 failed, 8 passed`，全部为 `PermissionError: [WinError 5]`，机制与复现见 [_logs/03-failure-detail.txt](deliverables/qa_reports/_logs/03-failure-detail.txt) B 节。**其中不含任何真实缺陷**。

---

## 3. 源码风险审查（只读）

已通读 [src/roleplay/main.py](src/roleplay/main.py)、[config.py](src/roleplay/config.py)、[middleware.py](src/roleplay/middleware.py)、[api/deps.py](src/roleplay/api/deps.py)、[api/ratelimit.py](src/roleplay/api/ratelimit.py)、[api/sessions.py](src/roleplay/api/sessions.py)、[api/llm_config.py](src/roleplay/api/llm_config.py)、[core/orchestrator.py](src/roleplay/core/orchestrator.py)、[core/repetition_guard.py](src/roleplay/core/repetition_guard.py)、[core/quality_guard.py](src/roleplay/core/quality_guard.py)、[errors/handlers.py](src/roleplay/errors/handlers.py)。

| 文件:行号 | 问题 | 严重程度 |
|---|---|---|
| [api/llm_config.py:439](src/roleplay/api/llm_config.py#L439) | `/api/llm/switch` 无任何鉴权，却会把 `provider/model/base_url/api_key` **明文写入 `.env`** 并热重载全局 LLM。[config.py:464](src/roleplay/config.py#L464) 的 `cors_origins` 默认 `"*"`，局域网内任意主机（CORS 只约束浏览器，不约束 curl/脚本）都能改写全局端点与落盘凭据 | **高** |
| [api/llm_config.py:406](src/roleplay/api/llm_config.py#L406) | 与上条同源：`_persist_llm_env` 把 `ROLEPLAY_LLM_API_KEY` 明文落盘，`api_key` 仅经 `max_length` 校验；无鉴权入口令「密钥只在本机 `.env`」的假设在局域网暴露面上不成立 | **高** |
| [errors/handlers.py:79](src/roleplay/errors/handlers.py#L79) | 自定义 `HTTPException` 处理器构造 `JSONResponse` 时**丢弃 `exc.headers`**。实测：429 响应的 `Retry-After` 头消失（`Retry-After preserved: None`），客户端无法按服务端指示退避 | 中 |
| [errors/handlers.py:32](src/roleplay/errors/handlers.py#L32) | `_sanitize` 在 `depth > 10` 时直接返回 `str(value)[:200]`，**跳过脱敏**。实测 12 层嵌套的 `api_key` 原样穿透（`sanitized contains secret: True`），深嵌套凭据会经错误响应泄漏 | 中 |
| [config.py:66](src/roleplay/config.py#L66) | `llm_api_key` / `tavily_api_key`([:184](src/roleplay/config.py#L184)) / `qq_ws_token`([:497](src/roleplay/config.py#L497)) 均为普通 `str` 而非 `SecretStr`；`Settings` 一旦被 `repr()`/异常回显/日志打印即整体泄漏密钥 | 中 |
| [api/ratelimit.py:30](src/roleplay/api/ratelimit.py#L30) | 限流以 `request.client.host` 为键。部署在反向代理/网关后时**所有用户共享同一 IP 桶**，单客户端即可把全站打成 429；且未读取 `X-Forwarded-For` | 中 |
| [core/orchestrator.py:1024](src/roleplay/core/orchestrator.py#L1024) | `stream()` 用 `asyncio.ensure_future` 起了 `ctx_task`，但在 [:1030](src/roleplay/core/orchestrator.py#L1030) 的 `yield` 处若客户端断连、生成器被 `close()`，`ctx_task` **既不被 await 也不被 cancel**，导致任务泄漏与 `Task was destroyed but it is pending` | 中 |
| [api/sessions.py:14](src/roleplay/api/sessions.py#L14) | `/api/sessions/{session_id}/history` 无鉴权，`session_id` 完全由调用方给定；任何能访问该端口者可枚举/猜测 id 读取**完整对话历史**（[api/characters.py:19](src/roleplay/api/characters.py#L19)、[api/knowledge.py:48](src/roleplay/api/knowledge.py#L48) 同样无鉴权） | 中 |
| [api/desktop_pet.py:71](src/roleplay/api/desktop_pet.py#L71) | `stdout`/`stderr` 两个文件句柄先 `open`，再传 `Popen`；若 [:85](src/roleplay/api/desktop_pet.py#L85) 的 `Popen` 抛错，两处句柄**无 `try/finally` 兜底**，必然泄漏 fd | 中 |
| [main.py:127](src/roleplay/main.py#L127) | `except (asyncio.CancelledError, Exception): pass` 连 `CancelledError` 一并静默吞掉，QQ 渠道任务取消失败时**无任何日志**，问题被隐藏 | 低 |
| [core/orchestrator.py:411](src/roleplay/core/orchestrator.py#L411) | 四路检索 `asyncio.gather` 未传 `return_exceptions=True`；任一路抛出未被内层捕获的异常会取消其余三路（各 `_*_task` 内层确有 try，故实际风险有限，但防线依赖内层实现细节） | 低 |

**说明**：被点名排查的五类中，「异常被静默吞掉」在 [core/orchestrator.py](src/roleplay/core/orchestrator.py) 里共 12 处 `except Exception`，**逐条核对后均为「降级 + 告警日志」（如 [:284](src/roleplay/core/orchestrator.py#L284)、[:310](src/roleplay/core/orchestrator.py#L310)、[:364](src/roleplay/core/orchestrator.py#L364)、[:685](src/roleplay/core/orchestrator.py#L685)、[:750](src/roleplay/core/orchestrator.py#L750)、[:808](src/roleplay/core/orchestrator.py#L808)、[:837](src/roleplay/core/orchestrator.py#L837)）**，不属于「吞掉不报」，未列为缺陷；[core/repetition_guard.py](src/roleplay/core/repetition_guard.py) 与 [core/quality_guard.py](src/roleplay/core/quality_guard.py) 为纯字符串处理、无 IO 无异常吞噬，未发现问题。「None 解引用」方面 [api/sessions.py:19](src/roleplay/api/sessions.py#L19) 的 `getattr(orch, "_session_memory", None)`、[core/orchestrator.py:294](src/roleplay/core/orchestrator.py#L294)/[:320](src/roleplay/core/orchestrator.py#L320) 的 `is None` 早返回、[:998](src/roleplay/core/orchestrator.py#L998) 的 `self._mapper is not None` 均已正确防护。

---

## 4. 环境变量一致性

比对口径：代码侧取 [src/roleplay/config.py](src/roleplay/config.py) 的 `Settings.model_fields` 全量字段名加 `ROLEPLAY_` 前缀（`env_prefix="ROLEPLAY_"`，且 [:54](src/roleplay/config.py#L54) 配置 `env_file=".env"`）；同时核查全仓 `os.getenv`/`os.environ` 直接读取点。`.env` 仅按行取变量名，**未抄录任何值**。

- Settings 字段数：**185**
- [.env.example](.env.example) 变量数：**34**（均为 `ROLEPLAY_` 前缀）

### 表 A —— 代码读但 `.env.example` 没写（151 个）

按前缀归类：

| 前缀组 | 数量 | 变量名 |
|---|---:|---|
| `ROLEPLAY_PLOT_*` | 73 | `PLOT_ALIAS_AUTHORITATIVE`、`PLOT_ALIAS_TRUST_CHAINED_MIN_DF`、`PLOT_ALIAS_TRUST_RATIO`、`PLOT_CACHE_DIR`、`PLOT_CHAPTER_MAX_NAMES`、`PLOT_CHAPTER_ROUTING`、`PLOT_CHAPTER_TOP`、`PLOT_CONTEXT_MAX_CHARS`、`PLOT_COOCCURRENCE_BONUS`、`PLOT_CORPUS_DIR`、`PLOT_DIVERSITY_PER_DOC`、`PLOT_EDGE_MIN_CONFIDENCE`、`PLOT_EMBED_MODEL`、`PLOT_ENTITY_EXPAND_BACKEND`、`PLOT_ENTITY_EXPAND_ENABLED`、`PLOT_ENTITY_EXPAND_LLM_API_KEY`、`PLOT_ENTITY_EXPAND_LLM_BASE_URL`、`PLOT_ENTITY_EXPAND_LLM_MODEL`、`PLOT_ENTITY_EXPAND_MAX_APPEND`、`PLOT_ENTITY_EXPAND_MIN_CONF`、`PLOT_ENTITY_EXPAND_STATIC_PATH`、`PLOT_ENTITY_EXPAND_TOP`、`PLOT_ENTITY_EXPAND_WHITELIST`、`PLOT_ENTITY_QUERY_MAX_LEN`、`PLOT_EXTRACT_CONCURRENCY`、`PLOT_EXTRACT_MAX_TOKENS`、`PLOT_EXTRACT_TIMEOUT`、`PLOT_FILTER_GENERIC_SEEDS`、`PLOT_FUSE_K`、`PLOT_GRAPH_DIR`、`PLOT_GRAPH_ENABLED`、`PLOT_INCLUDE_WEAK`、`PLOT_LEXICAL_ALWAYS`、`PLOT_LEXICAL_FALLBACK`、`PLOT_LEXICAL_TOPUP`、`PLOT_LINK_THRESHOLD`、`PLOT_LORE_DIR`、`PLOT_MAX_CHUNKS`、`PLOT_MAX_EDGES`、`PLOT_MAX_HOPS`、`PLOT_MENTION_CACHE_SIZE`、`PLOT_MENTION_GROUP_BY_ENTITY`、`PLOT_MENTION_PER_ENTITY`、`PLOT_MENTION_SCORING`、`PLOT_MENTION_TOTAL_CAP`、`PLOT_MIN_CHAPTER_KEPT`、`PLOT_MIN_SEMANTIC_KEPT`、`PLOT_NAME_SALIENCE`、`PLOT_PPR_DAMPING`、`PLOT_PPR_MAX_ITER`、`PLOT_PPR_NODE_SPECIFICITY`、`PLOT_REQUIRE_ANCHORED_TOKEN_SEEDS`、`PLOT_RERANK_TOPUP_ENABLED`、`PLOT_RERANK_TOPUP_KEEP`、`PLOT_SEMANTIC_ENABLED`、`PLOT_SEMANTIC_LANGS`、`PLOT_SEMANTIC_LINK_MIN`、`PLOT_SEMANTIC_LINK_TOP`、`PLOT_SEMANTIC_MIN_SCORE`、`PLOT_SEMANTIC_RERANK_ENABLED`、`PLOT_SEMANTIC_RERANK_MIN`、`PLOT_SEMANTIC_RERANK_TOP`、`PLOT_SEMANTIC_TOP`、`PLOT_SEMANTIC_ZH_ENABLED`、`PLOT_TRACE_ENABLED`、`PLOT_UNTRUSTED_EXTRA_PER_ENTITY`、`PLOT_WEAK_EXEMPT_SOURCES`、`PLOT_WEIGHT_CHAPTER`、`PLOT_WEIGHT_EDGE`、`PLOT_WEIGHT_LEXICAL`、`PLOT_WEIGHT_MENTION`、`PLOT_WEIGHT_MENTION_ENTITY`、`PLOT_WEIGHT_SEMANTIC` |
| `ROLEPLAY_GRAPH_*` | 15 | `GRAPH_CACHE_DIR`、`GRAPH_CONTEXT_MAX_CHARS`、`GRAPH_DIR`、`GRAPH_EDGE_MIN_CONFIDENCE`、`GRAPH_ENABLED`、`GRAPH_ENTITY_LINK_THRESHOLD`、`GRAPH_EXTRACT_BATCH`、`GRAPH_EXTRACT_MAX_TOKENS`、`GRAPH_EXTRACT_TIMEOUT`、`GRAPH_INCLUDE_WEAK`、`GRAPH_MAX_CHUNKS`、`GRAPH_MAX_EDGES`、`GRAPH_MAX_HOPS`、`GRAPH_PPR_DAMPING`、`GRAPH_PPR_MAX_ITER` |
| `ROLEPLAY_PROFILE_*` | 8 | `PROFILE_ENABLED`、`PROFILE_EXTRACT_EVERY`、`PROFILE_LLM_TIMEOUT`、`PROFILE_MAX_ITEMS`、`PROFILE_NAMESPACE`、`PROFILE_REMINDER_DAYS`、`PROFILE_SYNONYM_THRESHOLD`、`PROFILE_TOP_K` |
| `ROLEPLAY_QQ_VOICE_*` | 8 | `QQ_VOICE_CLIP_MANIFEST`、`QQ_VOICE_COOLDOWN_SEC`、`QQ_VOICE_EMOTION_THRESHOLD`、`QQ_VOICE_ENABLED`、`QQ_VOICE_GROUP_ENABLED`、`QQ_VOICE_LANG`、`QQ_VOICE_MAX_SEC`、`QQ_VOICE_TTS_VOICE_EN` |
| `ROLEPLAY_EMOTION_*` | 5 | `EMOTION_CLASSIFIER_BACKEND`、`EMOTION_CONFIDENCE_THRESHOLD`、`EMOTION_DETECTOR`、`EMOTION_JINA_MODEL`、`EMOTION_LLM_TIMEOUT` |
| `ROLEPLAY_ENABLE_*` | 5 | `ENABLE_DYNAMIC_FOLLOWUPS`、`ENABLE_HISTORY_SUMMARY`、`ENABLE_SESSION_MEMORY`、`ENABLE_URL_INGEST`、`ENABLE_WEB` |
| `ROLEPLAY_CLOUD_*` | 4 | `CLOUD_LLM_REPETITION_PENALTY`、`CLOUD_LLM_TEMPERATURE`、`CLOUD_LLM_TOP_P`、`CLOUD_MAX_TOKENS_PER_REPLY` |
| `ROLEPLAY_REPETITION_GUARD_*` | 4 | `REPETITION_GUARD_ENABLED`、`REPETITION_GUARD_MAX_PHRASES`、`REPETITION_GUARD_MAX_RETRIES`、`REPETITION_GUARD_WINDOW` |
| `ROLEPLAY_RAG_*` | 3 | `RAG_HYBRID`、`RAG_HYBRID_ALPHA`、`RAG_HYBRID_CANDIDATES` |
| `ROLEPLAY_WEB_*` | 3 | `WEB_FETCH_CONTENT`、`WEB_MAX_RESULTS`、`WEB_PROVIDER` |
| `ROLEPLAY_EMBED*` | 3 | `EMBED_DIM`、`EMBED_MODEL`、`EMBEDDER` |
| `ROLEPLAY_LLM_*` | 2 | `LLM_REPETITION_PENALTY`、`LLM_TOP_P` |
| `ROLEPLAY_MEMORY_*` | 2 | `MEMORY_DECAY_LAMBDA`、`MEMORY_RETENTION_DAYS` |
| `ROLEPLAY_REFINE_*` | 2 | `REFINE_ENABLED`、`REFINE_TEMPERATURE` |
| 其余单变量 | 14 | `ALLOWED_INGEST_HOSTS`、`CHARACTER_CARD_PATH`、`CHARACTERS_DIR`、`CORS_ORIGINS`、`EVENT_EXTRACT_ENABLED`、`HISTORY_SUMMARY_THRESHOLD`、`INGEST_ALLOWED_ROOTS`、`KNOWLEDGE_DIR`、`LONGTERM_CONSOLIDATE_EVERY`、`OLLAMA_BASE_URL`、`PROMPT_CONFIG_PATH`、`RATE_LIMIT_PER_MINUTE`、`SESSION_MEMORY_DIR`、`TAVILY_API_KEY` |

> 其中安全性/权限相关且未在示例中给出的项尤其值得补：`ROLEPLAY_CORS_ORIGINS`、`ROLEPLAY_RATE_LIMIT_PER_MINUTE`、`ROLEPLAY_INGEST_ALLOWED_ROOTS`、`ROLEPLAY_ALLOWED_INGEST_HOSTS`、`ROLEPLAY_ENABLE_URL_INGEST`、`ROLEPLAY_TAVILY_API_KEY`、`ROLEPLAY_PROMPT_CONFIG_PATH`、`ROLEPLAY_KNOWLEDGE_DIR`、`ROLEPLAY_CHARACTERS_DIR`、`ROLEPLAY_SESSION_MEMORY_DIR`。

### 表 B —— `.env.example` 有但代码不用（0 个）

**空**。[.env.example](.env.example) 中全部 34 个变量都能一一对应到 `Settings` 字段，无冗余项。

### 补充观察

1. **`.env` 存在而 `.env.example` 缺失的 12 项**（说明示例文件落后于实际部署面）：`ROLEPLAY_EMBED_MODEL`、`ROLEPLAY_LLM_TOP_P`、`ROLEPLAY_LLM_REPETITION_PENALTY`、`ROLEPLAY_OLLAMA_BASE_URL`、`ROLEPLAY_RAG_HYBRID_ALPHA`、`ROLEPLAY_RAG_HYBRID_CANDIDATES`、`ROLEPLAY_RATE_LIMIT_PER_MINUTE`、`ROLEPLAY_PLOT_GRAPH_ENABLED`、`ROLEPLAY_PLOT_MAX_CHUNKS`、`ROLEPLAY_PLOT_CONTEXT_MAX_CHARS`、`ROLEPLAY_PLOT_EMBED_MODEL`、`ROLEPLAY_PLOT_SEMANTIC_ENABLED`。
2. **另一套独立配置前缀**：[src/compendium_rag/config.py:43](src/compendium_rag/config.py#L43) 用自建 `_env()` 读取 `CMPRAG_*` 共 29 个变量（外加复用 `ROLEPLAY_LLM_API_KEY`、`ROLEPLAY_LLM_BASE_URL`、`ROLEPLAY_OLLAMA_BASE_URL`），**完全未在 `.env.example` 中体现**。若该子包可被使用，示例文件缺少一整套配置说明。
3. **配置优先级不一致的隐患**：[src/compendium_rag/config.py:45](src/compendium_rag/config.py#L45) 的 `_env()` 一旦读到非空进程环境变量就**不再回退 `.env`**，与 pydantic-settings 的合并语义不同；同一变量在两套读取路径下可能得到不同结果。
4. 「代码里散落 `os.getenv`」的排查结论：`src/` 下仅 3 处，均非配置项——[api/desktop_pet.py:55](src/roleplay/api/desktop_pet.py#L55)（`COMSPEC` 系统变量）、[core/voice/stt.py:54](src/roleplay/core/voice/stt.py#L54) 与 [:61](src/roleplay/core/voice/stt.py#L61)（进程内设置 `CT2_CUDA_ALLOCATOR`、`OMP_NUM_THREADS`）。[config.py:4](src/roleplay/config.py#L4) 所声明的「杜绝散落的 os.getenv」在 `roleplay` 包内成立。

---

## 附录：产物与可复现性

- 运行器与命令、沙箱限制细节：[_logs/01-runner-and-commands.md](deliverables/qa_reports/_logs/01-runner-and-commands.md)
- 逐文件原始判定行：[_logs/02-results-by-file.txt](deliverables/qa_reports/_logs/02-results-by-file.txt)
- 失败/伪失败明细：[_logs/03-failure-detail.txt](deliverables/qa_reports/_logs/03-failure-detail.txt)
- 环境变量比对原始清单：[_logs/04-env-var-diff.txt](deliverables/qa_reports/_logs/04-env-var-diff.txt)
- 仅运行期夹具插件（不属于项目代码）：[_logs/_qa_tmpfix.py](deliverables/qa_reports/_logs/_qa_tmpfix.py)

复现单文件（注意需带插件与全新 basetemp，否则会重现 0o700 沙箱伪失败）：

```powershell
$env:PYTHONPATH = "<repo>\deliverables\qa_reports\_logs"
.\.venv\Scripts\python.exe -m pytest tests\test_api.py -q --tb=line `
    -p no:cacheprovider -p _qa_tmpfix --basetemp=$env:TEMP\bt_api
```
