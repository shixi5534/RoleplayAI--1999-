# 03 — 安全缺陷修复（S1 / S2a / S2b / S3）

- 日期：2026-09-29
- 工作目录：`C:\Users\Lenovo\WorkBuddy\2026-07-27-16-45-03\roleplay-ai`
- 解释器：`.\.venv\Scripts\python.exe`
- 范围：仅改本代理独占文件（见下表）。**未修改** `api\llm_config.py`、
  `core\orchestrator.py`、`core\llm\mock.py`、`core\session_memory.py`、
  `config.py`、`pyproject.toml`、`conftest.py`。

## 0. 落点文件与行号

| 文件 | 变更 | 行号（改后） |
|---|---|---|
| `src\roleplay\core\llm\endpoint_guard.py` | **新建**（校验逻辑下沉，无框架依赖） | 1–101 |
| `src\roleplay\core\llm\factory.py` | S1 接线 + import | 18、21、114–124、133–143 |
| `src\roleplay\errors\__init__.py` | 新增 `EndpointNotAllowedError` | 35–47（`status_code=422` 在 :45） |
| `src\roleplay\errors\handlers.py` | S2b(`_sanitize`) + S2a(headers) | 23、26–62、97–112（`headers=exc.headers` 在 :111） |
| `src\roleplay\channels\qq_onebot.py` | S3 脱敏辅助 + 3 处日志路径 | 18、33–61、93–99、119、150–153 |
| `tests\test_security.py` | 追加测试（原 83 行全部保留） | 86–432 |
| `tests\test_qq_onebot.py` | 追加测试（原 474 行全部保留） | 478–580 |

---

## S1（高）SSRF：`req.llm.base_url` 绕过既有校验 —— 已修

### 根因
`api\llm_config.py:242` 的 `_validate_base_url` 是**死代码**：它只被
`/api/llm/test`（:337）、`/api/llm/models`（:177）、`/api/llm/switch`（:463）
调用；`/chat` 的 `req.llm.base_url` 走的是
`core\orchestrator.py:866 → factory.build_llm_from_config`，而
`factory.py` 里 `"_validate_base_url"` 出现 **0 次**（实测确认）。

修复前实测：请求体填 `http://169.254.169.254/latest/meta-data` 被**接受**并
构建出 `OpenAILikeProvider`（云元数据 SSRF）。

### 修法
1. **下沉**校验逻辑到新文件 `src\roleplay\core\llm\endpoint_guard.py`：
   - `validate_llm_base_url(provider, base_url, api_key="", *, require_api_key=True)`，
     不合规抛 `ValueError(原因)`；
   - `is_llm_base_url_allowed(...)` 布尔封装（供测试/只读判定）；
   - 策略**逐条复制**既有 `_validate_base_url`，**刻意未改动**：
     scheme 仅 http/https；IP 字面量放行环回 + RFC1918 + IPv6 本地；
     localhost 放行；其余域名要求 https + 云端白名单 + api_key；
     169.254/16 与 100.64/10 自然落空 → 拒。
   - 不 import fastapi，避免 core 层耦合 HTTP 框架。

2. **接线**到 `factory.build_llm_from_config`（`factory.py:114–143`）：
   ```python
   override_url_given = bool((override.base_url or "").strip())
   if override_url_given or provider != s.llm_provider:
       try:
           validate_llm_base_url(provider, base_url, api_key or "", require_api_key=False)
       except ValueError as exc:
           raise EndpointNotAllowedError(f"base_url 不被允许：{exc}", details={...}) from exc
   ```
   校验位置在「provider/model/base_url/api_key 已解析、quick-path 复用判定之后、
   构建客户端之前」，因此所有走 override 的分支都被覆盖。

3. **触发条件的设计取舍（防误伤的关键）**：只在
   「**端点由本次请求决定**」时校验，即
   - `override.base_url` 非空，或
   - `override.provider` 与全局 provider 不同（此时 base_url 会回退到该 provider
     的默认地址）。
   
   若 override 未指定 base_url 且 provider 与全局一致，有效地址**完全由
   frozen Settings 决定**（运维可信、且 `/switch` 侧已有校验），沿用旧行为。
   这样既堵住请求体通道，又不会因为「全局配了内网/环回地址」而让本地部署
   在其它路径上被误伤。

4. `require_api_key=False`：core 层只判**地址安全**；「云端 override 缺 key」
   仍由 `ProviderError` 在 generate 时显式报错——这是
   `tests\test_llm_override.py` 已锁死的既有契约（`test_cloud_override_without_key_*`），
   不能因为加校验而改变。api 层继续用默认 `True`。

5. 新增 `EndpointNotAllowedError`（`errors\__init__.py:35`）：`status_code=422`
   与 api 层 `HTTPException(422)` 对齐，`code="validation_error"` 与现有对外
   契约一致——`/chat` 被拦截时返回 **422 而不是 500**，前端无需新增分支。

### 实测结果（修复后）
`endpoint_guard.is_llm_base_url_allowed(provider, url, "k")`：

| URL | 结果 |
|---|---|
| `http://169.254.169.254/latest/meta-data` | **BLOCK** |
| `http://169.254.1.1` | **BLOCK** |
| `http://100.64.0.1` | **BLOCK** |
| `http://93.184.216.34/v1` | **BLOCK** |
| `https://evil.example.com/v1` | **BLOCK** |
| `http://evil.example.com/v1` | **BLOCK** |
| `file:///c:/windows/win.ini` | **BLOCK** |
| `gopher://169.254.169.254:80/_x` | **BLOCK** |
| `ftp://127.0.0.1/x` | **BLOCK** |
| `http://127.0.0.1:11434` | ALLOW |
| `http://127.0.0.1:11434/v1` | ALLOW |
| `http://localhost:11434/v1` | ALLOW |
| `http://192.168.1.50:11434/v1` | ALLOW |
| `http://10.0.0.1:8080` | ALLOW |
| `http://172.16.5.5:1234` | ALLOW |
| `http://[::1]:11434` | ALLOW |
| `https://api.deepseek.com/v1` | ALLOW |
| `https://api.openai.com/v1` | ALLOW |

`factory.build_llm_from_config(settings, override)` 端到端实测：
- 拦截（抛 `EndpointNotAllowedError`，status 422）：
  `169.254.169.254/latest/meta-data`、`169.254.1.1`、`100.64.0.1`、
  `file:///c:/windows/win.ini`、`gopher://...`、`ftp://...`、
  `https://evil.example.com/v1`、`http://93.184.216.34/v1`；
  以及「全局 base_url 被投毒成 169.254.169.254 + override 只改 provider」。
- **放行（ollama 本地用法仍可用）**：
  `http://127.0.0.1:11434`、`http://127.0.0.1:11434/v1`、`http://localhost:11434/v1`、
  `http://192.168.1.50:11434/v1`、`http://10.0.0.1:8080`、`http://172.16.5.5:1234`、
  `https://api.deepseek.com/v1`；且 ollama 空 key 兜底 `"ollama"` 不变、
  `needs_aclose=True` 不变。

> 结果证明：**169.254.169.254 被拦，而 ollama 本地环回地址未被误伤。**

### ⚠️ 需要主代理接线（唯一遗留项）
`api\llm_config.py` **不在本代理文件清单内，未改动**。当前该文件里仍有一份
**重复的 `_validate_base_url`（:242–314）**，与 `endpoint_guard.py` 策略相同但
字面重复。建议主代理做两处最小改动（二选一，推荐 A）：

**A（推荐，消除重复）** —— 删除 `api\llm_config.py:242–314` 的函数体，改为薄封装：
```python
import urllib.parse
from ..core.llm.endpoint_guard import validate_llm_base_url as _guard

def _validate_base_url(provider: str, base_url: str, api_key: str = "") -> None:
    """SSRF 防护（薄封装）：core 层唯一下沉实现 endpoint_guard。"""
    try:
        _guard(provider, base_url, api_key)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
```
三个调用点（:177、:337、:463）**无需任何改动**，行为逐条等价
（`require_api_key` 默认 True 正是 api 层原语义）。

**B（最小改动）** —— 保持现状不动。两份策略当前完全一致，factory 侧已生效；
风险是未来改一处忘另一处导致策略漂移。若选 B，建议在 `_validate_base_url`
的 docstring 里加一行「⚠️ 与 core/llm/endpoint_guard.py 手工镜像，改一处须同步另一处」。

同时建议把 `/chat` 的 422 纳入 API 测试（本代理测试只覆盖到 factory 层，
`test_security.py` 用的是直接调用 + `EndpointNotAllowedError` 断言）。

---

## S2a（中）错误处理器丢弃 `headers` —— 已修

### 根因
`handlers.py:79` 附近的 `_handle_http` 只传 `status_code` 与 `content`，
**未传 `headers`**；而 `api\ratelimit.py:44–48` 的 429 显式带了
`headers={"Retry-After": str(retry)}` → 被静默丢弃，客户端拿不到退避时间，
只能盲目重试（放大压垮服务）。

### 修法
`handlers.py:97–112`：`JSONResponse(..., headers=exc.headers)`（:111）。
`headers=None` 时 FastAPI/Starlette 等价于无自定义头，行为与修复前一致
（已用 `test_http_exception_handler_without_headers_ok` 锁定）。

安全：只透传框架/业务显式声明的头，**不反射请求头**，无凭据泄漏面。

### 实测结果
手工构造 `HTTPException(429, headers={"Retry-After": "42", "X-Custom": "v"})`：
响应头 `retry-after: 42`、`x-custom: v` **均存在**，状态码 429，
`error.code == "http_error"` 结构不变。

---

## S2b（中）`_sanitize` 深度超限跳过脱敏 —— 已修

### 根因
`handlers.py:32–33` 原为：
```python
if depth > 10:
    return str(value)[:200] if value is not None else value
```
即「**深度超限 = 跳过脱敏**」——实测 12 层嵌套的 `{"api_key": "sk-..."}` 会被
`str()` 原样序列化并截断输出，**密钥穿透**到错误响应/日志。

### 修法
`handlers.py:40–50`：超限层**降级为打码/丢弃**，绝不输出原始内容：```python
if depth > 10:
    if isinstance(value, dict):
        return {str(k): ("***" if str(k).lower() in _SENSITIVE_KEYS else _DEPTH_LIMIT_PLACEHOLDER)
                for k in value}
    return _DEPTH_LIMIT_PLACEHOLDER   # "[深度超限已隐藏]"
```
- dict 层仍按**键名**判定：敏感键（api_key/token/secret/…）在任意深度都打 `***`；
- 其它类型折叠为常量占位符 `"[深度超限已隐藏]"`（`handlers.py:23`）；
- 上限内（depth ≤ 10）的递归行为与阈值**完全未动**，浅层脱敏零回归。

### 实测结果
| 用例 | 泄漏 `sk-…`？ | 输出 |
|---|---|---|
| 12 层 `{"nested": {"api_key": "sk-LEAK-DEEP-…"}}` | **否** | 12 个 `nested` + 超限层占位符 |
| 11 层（边界内）`{"api_key": "sk-LEAK-BOUNDARY-…"}` | **否** | `'api_key': '***'` |
| 15 层裸字符串 `TOPSECRET-…` | **否** | 占位符 |
| 100 层 | 否（不抛异常） | 占位符 |
| 浅层 `{"token": …}` / `Bearer sk-live-…` | 否 | 行为不变 |

---

## S3（中）QQ 渠道重连日志泄漏 `access_token` —— 已修

### 根因
`qq_onebot.py:113`（改前 :82）成功路径有 `display_url` 脱敏；
但 `:93–95`（改前 :61–64）异常分支是
`logger.warning("QQ 渠道连接异常，%ss 后重连：%s", self._reconnect_delay, exc)`
—— **裸 `%s(exc)`，无脱敏**。实测 `websockets.exceptions.InvalidURI` 的
字符串**原样携带完整 URL（含 access_token）**：
```
not-a-scheme://h/x?access_token=SECRET123&access_token=SECRET123 isn't a valid URI: ...
```
（`raw contains token: True`）→ 凭据进 server.log。

### 修法
1. 新增模块级辅助 `_redact_url(text, token="")`（`qq_onebot.py:39–61`）：
   - `text` 非字符串（异常对象）先 `str()` 再脱敏；
   - `token` 非空才 `replace(token, "***")`，**空 token 直接返回原文**
     —— 规避 `replace("", "***")` 的灾难性逐字符替换；
   - 再按 `access_token=[^&\s"'>]*` 正则（`qq_onebot.py:36`）兜底打码，
     覆盖 token 经 URL 编码/拼接后与配置字面不等的情形，双保险；
   - 纯替换、不抛异常（脱敏本身不能让日志路径失败）。

2. 三处日志路径全部改走该辅助：
   - `qq_onebot.py:93–99` —— **异常分支（本次主缺陷）**：
     `_redact_url(exc, self.settings.qq_ws_token)`；
   - `qq_onebot.py:119` —— 成功路径 info：`display_url = _redact_url(url, token)`
     （等价替换原 `url.replace(f"access_token={token}", …)`，行为不变）；
   - `qq_onebot.py:150–153` —— WS 读取异常分支（同类风险，顺手加固）。

### 实测结果
- 真实 `_connect_loop` + 非法 URL（`not-a-scheme://h/x`，token=`SECRET123`）：
  异常类型 `InvalidURI`，`raw contains token: True`，
  经脱敏后 `access_token=***`，**日志 `leak: False`**。
- `start()` 异常分支实测日志：
  `QQ 渠道连接异常，0.0s 后重连：connect failed: ws://127.0.0.1:3001/?access_token=***`
  → `leak: False`。
- 空 token：`_redact_url("ws://127.0.0.1:3001", "") == "ws://127.0.0.1:3001"`
  （长度不变、无逐字符膨胀）；`_redact_url(None, "") == ""`。
- 真实连接 URL 仍带 token（协议需要），只有日志被打码。

---

## 新增测试（全部追加，**未删改任何既有测试**）

### `tests\test_security.py`（原 8 个用例保留，新增 16 个函数 / 24 个断言点）
| 测试名 | 断言 |
|---|---|
| `test_endpoint_guard_allows_local_and_cloud` (9 例参数化) | 环回/localhost/RFC1918/IPv6 环回/官方云端**放行**（防误伤） |
| `test_endpoint_guard_blocks_metadata_and_bad_scheme` (9 例参数化) | 169.254.169.254、169.254/16、100.64/10、公网 IP、非白名单域名、file/gopher/ftp **拦截** |
| `test_endpoint_guard_cloud_host_requires_https_and_key` | 白名单域名仍需 https + key；`require_api_key=False` 时放宽 |
| `test_build_llm_from_config_blocks_ssrf_override` (8 例参数化) | **S1 核心**：factory 端到端拦截，422 + details 不含 api_key |
| `test_build_llm_from_config_blocks_metadata_via_provider_switch` | 不带 base_url、仅换 provider 也拦（全局端点被投毒场景） |
| `test_build_llm_from_config_keeps_local_ollama_usable` | **★防误伤★** `127.0.0.1:11434` 仍可用（含 `/v1`、key 兜底、needs_aclose） |
| `test_ollama_local_default_base_url_still_usable` | **★防误伤★** 不传 base_url 的 ollama override 回退 `localhost:11434/v1` 仍可用 |
| `test_build_llm_from_config_allows_internal_and_cloud` | RFC1918 与官方云端 override 继续放行 |
| `test_build_llm_from_config_trusted_settings_path_unchanged` | 纯 settings 路径零改动（不新增校验） |
| `test_sanitize_redacts_key_nested_beyond_depth_limit` | **S2b**：12 层 `api_key` 不泄漏，降级为占位符 |
| `test_sanitize_masks_sensitive_key_at_depth_boundary` | 边界内敏感键打 `***` |
| `test_sanitize_depth_limit_never_returns_raw_payload` | 15 层裸字符串不泄漏 |
| `test_sanitize_depth_limit_handles_extreme_nesting` | 100 层不抛异常且不泄漏 |
| `test_sanitize_still_redacts_shallow_and_bearer` | 浅层零回归 |
| `test_http_exception_handler_preserves_retry_after` | **S2a**：429 的 `Retry-After` 透传 |
| `test_http_exception_handler_without_headers_ok` | 无头 HTTPException 行为不变 |

### `tests\test_qq_onebot.py`（原全部用例保留，新增 4 个）
| 测试名 | 断言 |
|---|---|
| `test_redact_url_masks_token` | 精确 token、异常对象、形态兜底三种情形均打码 |
| `test_redact_url_empty_token_is_noop` | 空 token 不触发灾难性替换 |
| `test_reconnect_log_does_not_leak_token` | **★S3 核心★** 真实 `InvalidURI` 路径日志无 token、含 `access_token=***` |
| `test_connect_log_masks_token` | 成功路径 info 日志亦无 token（回归保护） |

---

## 回归结果

### 指定命令（含运行期 tmp 插件）
```
.\.venv\Scripts\python.exe -m pytest tests\test_security.py tests\test_qq_onebot.py `
  tests\test_api.py tests\test_llm_config.py -q --tb=short -p no:cacheprovider -p _qa_tmpfix
```
结果：**`101 passed, 1 warning in 35.38s`，exit=0**，无 FAILED / ERROR。
测试函数计数（`git show HEAD:` 对比）：
- `test_security.py`：8 → **24** 个测试函数（+16），参数化展开后收集 **47** 个用例；
- `test_qq_onebot.py`：25 → **29** 个测试函数（+4），收集 **29** 个用例；
- 两文件合计收集 **76** 个用例，全部通过。

### 关于「已知失败用例」
`tests\test_llm_config.py::TestChatRequestLLMOverride::test_llm_override_embedded_in_chat_request`
**现在已经通过**（单独跑与整套跑均 PASSED）。核实：该用例已被其它代理改写为
`{"provider": "mock", "model": "mock-model"}`（不再真发网络请求），
且 `conftest.py` 钉死了 `ROLEPLAY_LLM_BASE_URL=http://127.0.0.1:9/v1`。
即：**它的转绿来自这两处修改，不是本次 S1 修复带来的**——如实记录。
（若它仍是「未传 base_url 的 ollama override」旧写法，则 S1 修复会把它从
「真连本机网关 401」变成「按默认地址正常构建」，同样不会再因网络失败。）

### 全量套件（额外自查，`--ignore=tests\compendium_rag`）
**`1073 passed, 1 skipped, 1 failed in 229.33s`**。
唯一失败 `tests\test_plotrag_m0_verification.py::TestM03StrictGate::test_default_invocation_returns_zero`
**与本任务无关且属环境问题**：它调用 `scripts\audit_full_corpus.py` 覆写
`data\knowledge\_audit\full_issues.jsonl`，报
`PermissionError: [Errno 13] Permission denied`（该文件预存在，沙箱/文件锁
不允许覆写）。单独跑该用例同样失败，与本次改动无因果关系。

---

## 遗留项 / 需主代理处理

1. **【必须】`api\llm_config.py` 接线**（该文件不在本代理清单，未改）：
   删除重复的 `_validate_base_url`（:242–314）改为薄封装调用
   `endpoint_guard.validate_llm_base_url`，`ValueError → HTTPException(422)`。
   三个调用点无需改动。详细补丁见上文 S1「需要主代理接线」，
   或维持现状（两份策略当前一致，仅存在未来漂移风险）。
2. **【建议】补 `/chat` 端 API 级 SSRF 测试**：现有测试覆盖到 factory 层；
   API 层断言（`POST /chat` 带恶意 `llm.base_url` → 422）需主代理在
   `tests\test_api.py` / `tests\test_llm_config.py` 补一条。
3. **【建议】`errors\__init__.py` 新增的 `EndpointNotAllowedError`** 若主代理
   希望换名字/换 code，可在接线时一并调整；当前 name/code 已按既有对外契约选定。
4. **【提示】`core\llm\factory.py` 的触发条件**：仅当 override 指定了 base_url
   或切换了 provider 时校验。若主代理希望「任何 override 存在就校验」（更严格），
   把 `if override_url_given or provider != s.llm_provider:` 改为 `if True:` 之外的
   等价写法即可——但需注意 `tests\conftest.py` 的全局
   `ROLEPLAY_LLM_BASE_URL=http://127.0.0.1:9/v1`（环回，仍会放行），
   故更严格也不影响测试。
5. **【环境】** 沙箱不允许删除文件，`deliverables\qa_reports\fix\_probe_s1.py`
   与 `_probe_s3.py` 已改写为指向本报告的占位说明，可由主代理清理。
