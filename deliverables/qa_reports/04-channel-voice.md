# 04 — 渠道 / 语音 QA 检验与安全审查报告

- 范围：`tests/test_qq_onebot.py`、`tests/test_qq_voice.py`、`tests/test_voice.py`、`tests/e2e_pet_voice.py`、`tests/test_plot_graph_retrieval_live.py`
- 安全审查对象：`qq_onebot.py`、`desktop_pet.py`、`api/voice.py`、`core/voice/{tts,stt,voice_reply,clip_store}.py`
- 模式：**只读**。未修改任何项目源文件、未 pip install、未联网、未真实合成/识别语音。
- 环境：Windows，`.venv\Scripts\python.exe`（Python 3.13.14），pytest 9.1.1，离线。

> ⚠️ **交付偏差（必须先声明）**：本会话的 shell 沙箱对**工作区所有写入**返回 `WinError 5`（`deliverables/`、新建目录、覆盖已存在文件全部被拒），与运行时声明的 `workspace-write` 不符。因此：
> - 报告与日志改用文件写入工具落到指定路径（已成功）；
> - 原始 pytest 日志无法由 shell 重定向进 `_logs\`，暂存于会话临时目录 `%TEMP%\dsh-TrCicp\qa04\`，摘要已转录进 [04-channel-voice.log.txt](deliverables/qa_reports/_logs/04-channel-voice.log.txt)。

---

## 1. 测试结果表

运行命令（日志全部重定向，原始输出不进上下文）：

```
.\.venv\Scripts\python.exe -m pytest tests\<file>.py -q --tb=line -p no:cacheprovider -p sandbox_tmpfix
```

| 文件 | 通过 | 失败 | 跳过 | 耗时(用例) | 耗时(墙钟) | 结论 |
|---|---|---|---|---|---|---|
| `tests/test_qq_onebot.py` | 25 | 0 | 0 | 0.41s | 1.9s | ✅ 全通过（含 2 个真实 WS 端到端用例） |
| `tests/test_qq_voice.py` | 19 | 0 | 0 | 0.32s | 1.6s | ✅ 全通过（纯单元，无 IO） |
| `tests/test_voice.py` | 26 | 0 | 0 | 3.48s | 4.9s | ✅ 全通过，但**覆盖率虚高**（见 §4） |
| `tests/e2e_pet_voice.py` | — | — | — | — | 0.16s | ⛔ **不可收集**（exit 5，no tests collected）→ (d) 类 |
| `tests/test_plot_graph_retrieval_live.py` | 3 | 0 | 0 | 53.54s | 55.0s | ✅ 真实跑通（本机存在真实语料/图谱，未联网） |
| **合计** | **73** | **0** | **0** | | ~64s | |

### ⚠️ 首轮 20 个 error 与「沙箱伪失败」说明（重要，勿计入真 bug）

首次直接运行时 `test_qq_onebot` 报 `23 passed, 2 errors`、`test_qq_voice` 报 `1 passed, 18 errors`，报错均为：

```
E   PermissionError: [WinError 5] 拒绝访问。: 'C:\Users\Lenovo\AppData\Local\Temp\dsh-TrCicp\pytest-of-Lenovo'
```

已定位根因并逐项排除，**结论：属于运行沙箱的伪失败，既不是 (a) 真 bug、也不是 (b) 测试过期、(c) 缺依赖、(d) 需网络**：

1. 本沙箱对**任何以 mode `0o700` 创建的目录永久拒绝 `os.scandir`**，且 `chmod` 回 0o777 同样被拒（已实测：`m700 → scandir=FAIL PermissionError`，`m777/m755/m0 → OK`；`chmod(0o777)` 抛 `PermissionError`）。
2. pytest 的 `tmp_path` 机制恰好全程用 `mode=0o700`：`_pytest/tmpdir.py:139/141/158/168/172/218`，且 `tmpdir.py:206` 会对 `pytest-of-<user>` 执行 `rootdir.chmod(...)` → 一旦该目录被创建即永久不可枚举。
3. 触发点：`_pytest/pathlib.py:354 cleanup_dead_symlinks(root_dir)`（`root.iterdir()`）与 `tmpdir.py:337`。仅 `tmp_path` 相关夹具受影响（`test_qq_onebot` 的 2 个失败、`test_qq_voice` 的 18 个失败全部是带 `tmp_path` 参数的用例）。

**处置（未触碰任何项目文件）**：在**仓库之外**的临时目录放了一个外部 pytest 插件 `sandbox_tmpfix.py`（通过 `-p sandbox_tmpfix` + `PYTHONPATH` 加载），只在进程内把 `os.mkdir/makedirs` 的 mode 强制为 0o777、把 `os.chmod` 的 `PermissionError` 吞掉；配合 `PYTEST_DEBUG_TEMPROOT` 指向已存在的可写目录。该插件**不改变任何业务代码、夹具或断言语义**，只消除文件系统伪影。修正后上述 20 个 error 全部转为 pass。

> 因此下表「失败明细」中的真失败数为 **0**。这不代表代码无问题——问题集中在 §3 安全审查与 §4 覆盖盲区。

---

## 2. 失败明细

### 2.1 真失败（(a)/(b)/(c)/(d)）

| node id | 归类 | 说明 |
|---|---|---|
| — | — | **无失败用例**（修正沙箱伪影后 73 全通过） |

### 2.2 不可收集 / 需外部前置

| 文件 | 归类 | 说明 |
|---|---|---|
| `tests/e2e_pet_voice.py` | **(d) 需外部服务** | 不是 pytest 测试模块，是独立 Playwright 脚本（文件头注释即写明用法 `.venv/Scripts/python.exe tests/e2e_pet_voice.py`，`if __name__ == "__main__"` 在 L432）。pytest 收集结果为 `no tests collected`（exit 5）。运行前置：① 前端静态服务器需监听 `http://127.0.0.1:18080/pet.html`（L34）——**实测该端口未监听**；② 真实 Chromium（`C:/Users/Lenovo/AppData/Local/ms-playwright/chromium-1217/...` 存在）。按任务要求记为「不可收集 / (d) 类」，未自行起服务补救。 |

### 2.3 首轮「伪失败」清单（环境，非 a–d 任一类）

| node id | 原因 |
|---|---|
| `test_qq_onebot.py::test_e2e_voice_reply_sends_record_then_subtitle` | 沙箱 0o700 目录不可枚举（`tmp_path`） |
| `test_qq_onebot.py::test_e2e_low_emotion_still_gets_text_reply` | 同上 |
| `test_qq_voice.py` 全部 18 个带 `tmp_path` 的用例（`test_clip_store_*` / `test_*_triggers_*` / `test_cooldown_*` / `test_lang_override_*` / `test_group_voice_gated_by_config` / `test_overlong_clip_degrades_to_text` / `test_custom_max_sec_allows_long_clip` / `test_clear_session_resets_state` 等） | 同上 |

报错行（≤5 行，取自原始日志）：

```
E   PermissionError: [WinError 5] 拒绝访问。: '...\pytest-of-Lenovo'
    File "...\_pytest\tmpdir.py", line 337, in pytest_sessionfinish
        cleanup_dead_symlinks(basetemp)
    File "...\_pytest\pathlib.py", line 354, in cleanup_dead_symlinks
        for left_dir in root.iterdir():
```

### 2.4 依赖声明核对（针对 (c) 类）

本机**未发现缺包**：`playwright`/`websockets`/`edge_tts`/`faster_whisper`/`httpx` 均可导入。声明情况供参考：

| 包 | 用途 | `pyproject.toml` | `requirements.txt` |
|---|---|---|---|
| `websockets>=12.0` | QQ OneBot 通道运行时依赖 | ❌ **未声明**（只在 `requirements.txt` L21 有，且文件内自注「pyproject 未列此项」） | ✅ L21 |
| `edge-tts>=6.1` | TTS | ✅ `[voice]` L23 | ❌（注释形式，L8 说明可选依赖见 pyproject） |
| `faster-whisper>=1.0` | STT | ✅ `[voice]` L23 | ❌（同上） |
| `pytest`/`pytest-asyncio` | 测试 | ✅ `[dev]` L25 | ❌（注释形式 L31-32） |
| `playwright` | `e2e_pet_voice.py` | ❌ **未声明**（任何清单都没有） | ❌ |

> 两条真实的清单缺口：**`websockets` 未进 pyproject**（对 `pip install -e ".[dev]"` 主推路径而言是漏项，QQ 通道会 `ImportError`）；**`playwright` 完全未声明**，导致 e2e 脚本在新机器上必然失败。

---

## 3. 安全审查（本任务重点）

审查覆盖：`channels/qq_onebot.py`、`api/desktop_pet.py`、`api/voice.py`、`core/voice/tts.py`、`core/voice/stt.py`、`core/voice/voice_reply.py`、`core/voice/clip_store.py`（并顺带核查了 `models/chat.py`、`core/llm/factory.py`、`api/llm_config.py`、`api/chat.py`、`core/knowledge/retrieval_trace.py`、`middleware.py`、`ratelimit.py` 以确认可达性与既有防护）。

### 3.1 高危汇总

**共 1 项高危、5 项中危、6 项低危。** 关键前提：全站**无任何鉴权中间件**（`grep` 全 `src/` 无 `HTTPBearer`/`APIKeyHeader`/自定义鉴权依赖），默认 `cors_origins="*"`（`config.py:464`），仅靠 `rate_limit`（默认 60/min/IP，`config.py:463`）。

| # | 文件:行号 | 类别 | 描述 | 严重 | 建议 |
|---|---|---|---|---|---|
| S1 | `models/chat.py:52` + `core/llm/factory.py:113,143-152` + `core/llm/openai_like.py:181` | **SSRF（未鉴权、URL 完全可控）** | `POST /chat`、`/chat/stream` 的 `ChatRequest.llm.base_url` 由请求体任意指定，**绕过了 `/api/llm/test`、`/api/llm/switch` 共用的 `_validate_base_url` 防护**（`api/llm_config.py:242`，那条规则明确拒绝云元数据/公网/非白名单）。服务端随后 `POST {base_url}/chat/completions`。**已实测验证**：`build_llm_from_config` 对 `http://169.254.169.254/latest/meta-data`、`http://127.0.0.1:11434`、`http://192.168.1.1` **全部 ACCEPTED** 并构造出 `OpenAILikeProvider`。可探测内网端口/服务，且错误详情经 `/chat/stream` 的 `event: error` 部分回显（`api/chat.py:71-76`，仅做凭据脱敏、不脱敏内网响应内容）。 | **高** | 在 `build_llm_from_config` 内对 `override.base_url` 复用 `_validate_base_url`（需把该函数提到中立模块，避免 api→api 依赖）；或对 override 的 base_url 强制走 `safe_url` 白名单；同时为 chat 路由加鉴权或至少校验 Origin。 |
| S2 | `api/desktop_pet.py:26-29,100-114`（+`main.py:145-153`、`config.py:464`） | **未鉴权即触发危险动作（本地进程拉起）** | `/api/desktop-pet/launch` 唯一防线是 `_is_loopback(request)`，而它只读 `request.client.host`——在反向代理/`--proxy-headers` 下可被 `X-Forwarded-For` 伪造；更关键的是**对「用户浏览器内的第三方页面」而言 `client.host` 天然就是 127.0.0.1**。默认 CORS 为 `*` 且该端点**无 body**，属 CORS「简单请求」，**无需预检**，任意网站 `fetch('http://127.0.0.1:<port>/api/desktop-pet/launch',{method:'POST'})` 即可让本机反复拉起 Electron。该路由**未挂 `rate_limit`**（文件内 `Depends` 计数为 0），Electron 启动失败时每次请求都会再 `Popen` 一个进程 → 本地进程/资源耗尽。 | 中 | 加 `Depends(rate_limit)`；引入一次性 nonce/本机 token（由页面初始化时下发）替代仅凭 IP 的判定；把 `allow_origins` 默认值从 `*` 收紧；校验 `Origin`/`Sec-Fetch-Site` 头。 |
| S3 | `channels/qq_onebot.py:79-83` vs `61-64` | **Token 泄漏到日志（脱敏仅在成功路径生效）** | L82 只把 `display_url` 用于 L83 的「连接中」日志；而 L61-64 的连接异常分支是 `logger.warning("QQ 渠道连接异常，%ss 后重连：%s", delay, exc)` —— 直接 `str(exc)`。`websockets` 的 `InvalidURI.__str__` 会**原样回带含 `access_token=<token>` 的完整 URI**（`websockets/exceptions.py:189: return f"{self.uri} isn't a valid URI: {self.msg}"`）。**已实测**：`token leaked in str(exc): True`，样本 `ws:127.0.0.1:3001?access_token=SUPERSECRETTOKEN123 isn't a valid URI`。任何 `ROLEPLAY_QQ_NAPCAT_WS_URL` 配错（缺 `//`、多余字符）都会把 WS 凭据永久写进日志。 | 中 | 异常分支同样过脱敏：`err = str(exc).replace(token, "***")`；或统一封装 `_redact(text)` 并在所有含 URL/凭据的日志点调用；更稳妥是改用 `Authorization` 头而非 query 传 token（`websockets` 支持 `additional_headers`）。 |
| S4 | `core/voice/stt.py:199-220,336-403` | **正常语音被静默截断（数据完整性 / (a) 真 bug）** | `_HALLUCINATION_PHRASES_EN` 含 `music`/`applause`/`laughter` 等**常用词**，而 `_strip_tail_hallucination` 对「长度 ≥4 的英文短语」一律做尾部截断（L363 `en_tail_phrases = [p for p in en_phrases_sorted if len(p) >= 4]`）。**已实测**（调用真实 `_filter_hallucinations`）：`'I love music' → 'I love'`、`'The audience gave applause' → 'The audience gave'`、`'我喜欢听music' → '我喜欢听'`。用户正常说话被吞掉尾词且无任何提示。中文侧因 `len>=4` 门槛挡住了「音乐/音效」（与 docstring 声称一致），英文侧则失守。 | 中 | 英文同样只对「≥3 词的片语」做尾部截断，或把 `music/applause/laughter/you/the/and/so` 这类单词移出尾部截断集合、仅保留整段精确匹配；补一组「正常句子不被截断」的负向单测（当前 0 覆盖）。 |
| S5 | `api/voice.py:82-90,116-127` + `core/voice/tts.py:279-317` | **无界重试导致的 DoS 放大** | `/voice/tts` 的 `text` 上限 5000 字符（`voice.py:84`），`_split_long_text` 按 500 字符切分 → 最多 ~10 段；每段 `asyncio.wait_for(..., timeout=_TTS_TIMEOUT=30)`，外层还有 `_TTS_MAX_RETRIES=3` → **单请求最坏 ≈ 10×30×3 = 900s（15 分钟）**，期间连接与工作线程被持续占用；`rate_limit` 默认 60/min 意味着可同时挂 60 条此类长连接。另：`voice.py` 的 `try/except`（L128-132）只包住 `StreamingResponse(...)` 的**构造**，生成器真正迭代时抛出的 `RuntimeError` 无法被转成 JSON 500，客户端只会拿到被截断的 200 流（`voice.py:108-109` 的注释只覆盖了「后端未启用」这一种情况）。 | 中 | 为 TTS 增加**整体**墙钟预算（如 `asyncio.timeout(60)`）而非仅分段超时；`_TTS_MAX_RETRIES` 与段数相乘后设总上限；把生成器包一层 try/except 以便正确返回 500；STT 侧同理（`_STT_MAX_CONCURRENCY=1`，`stt.py:77-80`，长音频会串行堵死 STT 队列）。 |
| S6 | `core/voice/stt.py:252-333`（可达性）+ `api/voice.py:24` | **未鉴权重资源接口 × 默认全通 CORS** | `/voice/stt`、`/voice/tts` 无鉴权；默认 `cors_origins="*"`（`config.py:464`）→ 任意网页可用跨域简单请求**驱动本机 STT/TTS**（`/voice/tts` 用 `Form` 的 `application/x-www-form-urlencoded` 即为简单请求，无预检）。结合 S5，形成「网页即可打满本机 CPU」的路径。 | 中 | 收紧默认 `cors_origins`；为语音路由加本机 token 或 Origin 校验；确认 `rate_limit_per_minute` 默认 60 是否够用。 |
| S7 | `core/knowledge/retrieval_trace.py:284-285` + `plot_graph.py:2224` | **路径穿越（写入任意路径），写原语** | `trace_path(base_dir, character_id)` 直接 `Path(base_dir)/"_audit"/"retrieval_trace"/f"{character_id}.jsonl"`，**未做任何清洗**。`character_id` 来自 `ChatRequest.character_id`（`/chat`，未鉴权）；`append_jsonl` 会 `p.parent.mkdir(parents=True, exist_ok=True)` + `open("a")`。**已实测**：`character_id='..\\..\\..\\pwned'` → `...\data\knowledge\_audit\retrieval_trace\..\..\..\pwned.jsonl`，**escapes base = True**。对照：同族的 `graph_store.py:751`、`plot_graph.py:2130` 都做了 `replace("/","_").replace("\\","_")`，**唯独 trace_path 漏了**。 | 低→中 | 与同族保持一致：`safe = re.sub(r"[^A-Za-z0-9_\u4e00-\u9fff]+", "_", character_id)`。当前默认 `plot_trace_enabled=False`（`config.py:398`）故利用门槛高（还需 `plot_corpus_<cid>.json` + `plot_graph_<cid>.json` 同时存在才会构建 retriever），**但一旦开启埋点即为任意路径写入**，应视为真实缺口。 |
| S8 | `channels/qq_onebot.py:266-268` | **默认开放的指令权限** | `admin = self.settings.qq_admin_uin.strip()`；为空（**默认值**，`config.py:499`）时 `if admin and ...` 短路 → `!clear/!char/!voice/!lang` **对群内所有人开放**。影响面被限制在「各自 session」内（`_session_chars`/`_voice` 均按 `session_id` 隔离），故危害有限，但 `!char <任意串>` 会写入未校验的 `character_id`（L302）并流入下游。 | 低 | 默认改为「仅管理员」或白名单内可用；`!char` 的 arg 做 id 白名单校验（对照 `character_store.get()` 的 dict 查找，当前无穿越，属加固）。 |
| S9 | `core/voice/clip_store.py:86-88` | **缺少根目录包含性校验（纵深防御）** | `read_bytes` 用 `(self.root / entry.file).read_bytes()`，`entry.file` 完全取自 manifest JSON 且**未校验解析后仍位于 `self.root` 之内**。恶意/被篡改的 manifest 写 `"file": "../../../Users/.../secret"` 即可读出任意文件并作为 QQ 语音发出。manifest 路径由运维配置（`qq_voice_clip_manifest`，L97-103）或仓库布局决定，**非远程用户可控**，故定级低。 | 低 | 加 `resolved = (self.root / entry.file).resolve(); assert self.root.resolve() in resolved.parents`；复用 `core/knowledge/security_utils.py:42 safe_local_path`。 |
| S10 | `api/desktop_pet.py:114` | **内部路径信息泄漏** | `raise HTTPException(500, detail=str(exc))` 把 `RuntimeError(f"未找到桌面宠物工程: {DESKTOP_DIR}")`（L65）等**绝对文件系统路径**回显给调用方。 | 低 | 对外返回固定文案，路径只记日志。 |
| S11 | `api/desktop_pet.py:69-72,85-96` | **文件句柄泄漏** | `open(...out.log)`/`open(...err.log)` 在 `subprocess.Popen` **之前**打开；若 Popen 抛异常，两个句柄永不关闭（关闭语句在 L95-96，位于 Popen 之后），长期反复失败会耗尽 fd。 | 低 | 用 `with open(...) as f` 或 `try/finally` 包住 Popen。 |
| S12 | `core/voice/stt.py:448-450` | **fd 泄漏 + 无上限读取** | `fd, tmp_path = tempfile.mkstemp()` 后 `os.write(fd, ...)`；若 `os.write` 抛错，`fd` 不会被关闭（`finally` 只 `os.remove(tmp_path)`）。另 L441 `audio_data.read()` 一次性读全量，**函数自身无大小上限**（25MB 上限只在 API 层 `voice.py:51-62` 强制），从其它入口调用即无界。 | 低 | `os.write` 包 try/finally 关 fd；在 `transcribe_audio` 内也加字节上限。 |

### 3.2 已确认**不存在**的问题（避免误报，逐项核过）

| 检查项 | 结论 | 依据 |
|---|---|---|
| 系统命令注入 | **无** | `subprocess.Popen` 仅出现在 `desktop_pet.py:85`，argv 全部为**常量/常量拼路径**（`_electron_command()` L43-60，无任何用户输入参与）；全 `src/` 无 `os.system`/`shell=True`/`eval`/`exec`。 |
| 用户输入拼进 URL | 仅 S1 一处 | `llm_config.py:179-183,226-229` 已走白名单校验；`plot_rerank.py:178,231`、`plot_entity_expand.py:121` 的 URL 来自配置，非请求体。 |
| 用户输入拼进路径 | 仅 S7 | `document_ingest.py:249,288,316,362` 已用 `safe_local_path`/`safe_url`；`vector_store.py:495` 用 `quote(ns, safe='')`；`session_memory.py:60` 做了 per-char 转义。 |
| 硬编码密钥 | **无** | 全 `src/` 正则扫描 `sk-[A-Za-z0-9]{16,}` / `api_key="..."` / `password="..."` 零命中；`.env` 存在且 `.gitignore` 已排除 `.env`/`.env.*.local`/`.env.*.bak*`。 |
| Token 回显到响应 | **无** | `GET /api/llm/config` 只返回 `has_api_key: bool`（`llm_config.py:64,142`）；`/api/llm/test`、`/chat/stream` 的错误详情均过 `errors/handlers.py:_sanitize/_safe_details`。S3 是**日志**侧而非响应侧。 |
| SSML/voice_id 注入 | **无（依赖白名单正则）** | `edge_tts/communicate.py:279` 把 `tc.voice` **未转义**插入 `<voice name='...'>`（只对 `text` 调用 `escape()`）。`tts.py:150` 的正则 `[A-Za-z]{2,3}-[A-Za-z]{2,4}-[A-Za-z0-9-]+`（`fullmatch`）挡掉了引号/尖括号，使注入不可达——**属关键防线，建议在注释中显式标注「勿放宽该正则」**。 |
| 重连风暴 | **无** | `qq_onebot.py:68` 指数退避封顶 30s；`_call_action` 用 `asyncio.wait_for(..., 5.0)`（L356）并在超时后清理 `_pending`（L358），无无界等待。 |
| 语音决策层（`voice_reply.py`） | **无发现** | 全同步纯内存；`session_id` 仅作 dict key，不触达 FS/命令/URL；异常一律降级为文字，不丢回复。 |
| STT 日志隐私 | **合规** | `stt.py:528,534` 只记字符数不记转写原文（符合其注释声明的约定）。 |

---

## 4. `tests/test_voice.py` 是「真实链路」还是「全 mock」？

**结论：全 mock。仅有 API 边界是真的，语音后端一行都没跑。有效覆盖率应判定为「低」，且 STT 侧接近零。**

### 4.1 判定依据

| 层面 | 真实 / Mock | 证据 |
|---|---|---|
| STT 推理 | ❌ **全 mock** | `test_voice.py:67` `@patch("roleplay.core.voice.stt._get_whisper_model")`，`mock_model.transcribe.return_value` 返回手写假 segment（L73-82、L395-404）。`faster_whisper.WhisperModel` 从未被实例化。 |
| TTS 合成 | ❌ **全 mock** | `test_voice.py:104,127,283,312,418` 全部 `@patch("roleplay.core.voice.tts._get_edge_tts")`，`Communicate` 是 `MagicMock`，`stream()` 是手写 async generator。**无一次真实网络调用、无一个真实 mp3 字节**（返回的是 `b"a"*1200`）。 |
| HTTP 路由 / 依赖注入 / 限流 | ✅ 真实 | `TestClient(app)` 走真实 ASGI 栈，`app.dependency_overrides[get_settings]` 真实生效（L346-349）。 |
| 参数计算 / 校验 / 切分 | ✅ 真实（纯函数，等价于单测源码） | `_build_tts_params`（L177-214）、`_validate_voice`（L218-242）、`_split_long_text`（L246-276）。 |
| 重试与 `Communicate` 重建 | ✅ 结构真实、副作用 mock | L284-332 断言 `Communicate.call_count == 2 / 1`，验证的是控制流而非真实 `stream()` 只能调用一次的行为。 |

### 4.2 有效覆盖率判断（不夸大）

- 无 `pytest-cov`（实测 `find_spec('pytest_cov') → False`），且禁止 `pip install`，**无法给出仪器化行覆盖率数字**。以下为按「被真正执行的语句/分支」做的人工判定。
- **`core/voice/stt.py`（546 行）：有效覆盖 ≈ 5–10%，且集中在最外围。** 被判过的只有：`transcribe_audio` 的「后端未启用」守卫（L422-423）+ mock 路径下 `language="zh"` 这一个 kwarg（L498）。**完全 0 覆盖**的部分：
  - 整个幻觉过滤层 L169-403（约 235 行，含 `_filter_hallucinations`、`_strip_tail_hallucination`、4 条正则、2 个黑名单集合）——全仓库搜索 `hallucination` 仅命中 `test_plot_graph_retrieval_live.py:77`（无关），**零专门单测**；这正是 S4 真 bug 潜伏的原因。
  - 模型加载/单例/双检锁 L89-143；临时文件路径 L445-450；`_transcribe_and_join` 的 20 个 transcribe 参数（L496-523，只断言了 `language`）；异常与 `finally` 清理 L537-546；`_run_stt_inference` 并发闸门 L83-86。
- **`core/voice/tts.py`（363 行）：有效覆盖 ≈ 55–65%。** 覆盖较好（参数、白名单、切分、重试计数）。未覆盖：真实 `Communicate.stream()` 行为、多段拼接（`_split_long_text` 只单独测函数，从未与 `synthesize_speech` 的多段循环串联）、缓存命中/淘汰分支 L271-274/322-336、`_TTS_MIN_OUTPUT_BYTES` 与 `asyncio.wait_for` 超时分支、SSML 参数是否被 edge-tts 接受。
- **`src/roleplay/api/voice.py`（133 行）：有效覆盖 ≈ 40%，且有两处「假通过」。**
  - ⚠️ **`test_stt_endpoint_empty_audio`（L365-376）与 `test_stt_endpoint_disabled`（L351-363）实际测的是同一条分支。** 端点里「后端未启用」检查在 L46，**早于**读文件与大小校验（L51-68）；而该用例用的 `settings_voice_disabled`（`stt_backend_enabled=False`）会在 L47 就返回 400。所以它**根本没验证「空音频 → 400」**，只是又一次验证了「禁用 → 400」。L356 的注释「音频 >32 bytes 以通过空音频校验，从而走到后端禁用检查」把实际顺序说反了。→ **这是测试质量问题（b 类），不是产品 bug**，但它制造了「空音频校验已覆盖」的假象。
  - 同理，**413（>25MB）分块上限分支、`RuntimeError → 500` 分支、`rate_limit` 交互**均无覆盖。
- 综合判定：**`test_voice.py` 对该三文件的有效覆盖率「最多 ~30%」，其中 STT 后处理层 0%。** 它验证的是「参数映射与错误码契约」，**不是**「语音链路能工作」。任何涉及模型、音频格式、网络、幻觉过滤的回归都拦不住。

### 4.3 建议补测（优先级排序）

1. `_filter_hallucinations` / `_strip_tail_hallucination` 的**双向**用例：真幻觉应清空，同时加一组**正常句不被截断**的负向断言（覆盖 S4）。
2. 修正 `test_stt_endpoint_empty_audio`：改用 `stt_backend_enabled=True` + mock 后端，才能真正打到 L65-68；并补 413 用例。
3. `synthesize_speech` 多段串联 + 缓存命中/淘汰 + 全段超时。
4. `voice.py` 生成器迭代期异常 → 确认返回语义（覆盖 S5 的第二半）。

---

## 5. 附：执行与产物

- 未修改任何项目源文件；新增文件仅 2 个交付物：
  - 本报告 `deliverables/qa_reports/04-channel-voice.md`
  - 日志摘要 `deliverables/qa_reports/_logs/04-channel-voice.log.txt`
- 原始 pytest 日志（含 `--tb=line` 全文）位于会话临时目录 `%TEMP%\dsh-TrCicp\qa04\`：`r_test_qq_onebot.txt`、`r_test_qq_voice.txt`、`r_test_voice.txt`、`r_live.txt`、`c_e2e_pet_voice.txt`，以及首轮伪失败的 `test_qq_onebot.txt`/`test_qq_voice.txt`。
- 单命令输出均 ≤60 行，日志内容未读入上下文（仅用 `Select-String` 抓 `^FAILED|^ERROR` 与 `-Tail`）。
- 所有文件耗时均 < 8 分钟，无超时放弃项（最慢 `test_plot_graph_retrieval_live.py` 55s）。
