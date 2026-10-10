# -*- coding: utf-8 -*-
"""云端 LLM 客户端（OpenAI 兼容 chat/completions）。

设计要点：
- **仅走云端**：不实现 mock/本地回退，抽取质量是本库的核心目标；
- 异步 + 信号量并发控制，配套重试（指数退避 + 抖动）；
- 三级 JSON 解析（直接 / 剥代码围栏 / 括号配平截取）+ 常见畸形修复；
- 显式识别「推理模型把 max_tokens 全烧在 reasoning_content、content 为空」
  这一实测故障（deepseek-v4.x 系列），判为可重试错误而不是静默返回空。

两条调用路径（P4 起）：
- :meth:`CloudLLM.complete_json` —— 抽取期用，结构化输出 + JSON 容错解析；
- :meth:`CloudLLM.complete_text` —— 作答期用，**自由文本、不解析 JSON、不发
  ``response_format``**。两者共用传输/重试/额度熔断骨架，区别只在「怎么判成功」。
"""
from __future__ import annotations

import asyncio
import json
import logging
import random
import re
from dataclasses import dataclass

import httpx

logger = logging.getLogger(__name__)

RE_FENCE = re.compile(r"```(?:json|JSON)?\s*(?P<body>.*?)\s*```", re.S)


class LLMError(RuntimeError):
    """LLM 调用失败（重试耗尽或不可重试的响应形态）。"""


class LLMTruncated(LLMError):
    """输出被 max_tokens 截断。"""


class LLMEmptyContent(LLMError):
    """content 为空（推理模型烧光 token 的典型症状）。"""


class LLMQuotaExhausted(LLMError):
    """云端账号额度耗尽（网关错误码 14018「额度已用尽」）。

    这不是"暂时性限流"——重试再多次也不会成功，只会白白消耗时间。
    因此单独成类，让调用方能**快速失败并优雅收尾**，
    而不是为 3000 个块各重试 3 次（实测浪费 6038 次重试）。
    """


class LLMGatewayUnreachable(LLMError):
    """网关整体不可达（连接被拒 / DNS 失败）。

    同样是**整批失败**：一旦确认，后续块直接跳过，不再逐块重试。
    """


# 额度耗尽的判定特征（网关返回 429 + error.code=14018）
QUOTA_MARKERS = ("14018", "额度已用尽", "insufficient_quota",
                 "quota_exceeded", "exceeded your current quota")

# 网关根本不可达的判定特征（连接被拒 / DNS 失败 / 超时）。
# 与额度耗尽同理：**整批调用都会失败**，逐块重试纯属空转
# （实测：端到端不可达时 30 块 × 3 次重试 = 60 次无效调用、白等 42 秒）。
GATEWAY_DOWN_MARKERS = ("ConnectError", "Connection refused", "ConnectionRefused",
                        "ConnectTimeout", "Name or service not known",
                        "getaddrinfo failed", "All connection attempts failed",
                        "Server disconnected", "nodename nor servname")


@dataclass
class LLMResult:
    text: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    attempts: int = 1
    finish_reason: str = ""


def _scan_json_values(s: str) -> list[object]:
    """扫描字符串中**所有**配平的 JSON 值（对象与数组）。

    为什么不能只找"第一个配平的 {}"（实测踩过的坑）：
    模型有时不按 `{"entities":[...],"relations":[...]}` 信封输出，而是直接给出
    裸数组 `[{...},{...}]`。此时第一个配平块是**数组里的第一个元素**，
    会被误当作整个响应——12 个实体静默塌缩成 1 个、且没有 entities 键。
    因此这里扫描全部候选，交由调用方按"信息量最大"挑选。
    """
    out: list[object] = []
    n = len(s)
    i = 0
    while i < n:
        ch = s[i]
        if ch not in "{[":
            i += 1
            continue
        depth = 0
        in_str = False
        esc = False
        j = i
        while j < n:
            c = s[j]
            if in_str:
                if esc:
                    esc = False
                elif c == "\\":
                    esc = True
                elif c == '"':
                    in_str = False
                j += 1
                continue
            if c == '"':
                in_str = True
            elif c in "{[":
                depth += 1
            elif c in "}]":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        if j < n and depth == 0:
            cand = s[i:j + 1]
            try:
                out.append(json.loads(cand))
            except ValueError:
                rep = _repair(cand)
                if rep is not None:
                    out.append(rep)
        i += 1
    return out


def _coerce_envelope(v: object) -> dict | None:
    """把模型的任意输出形态收敛成 `{"entities":[...], "relations":[...]}`。

    支持的形态：
    - 标准信封 dict
    - 裸数组 `[{...},{...}]`（按元素字段自动分流到 entities / relations）
    - 单个实体 dict（`{"name":..., "type":...}`）→ 包成单元素 entities
    - `{"data": {...}}` / `{"result": {...}}` 一类包壳
    """
    if isinstance(v, list):
        ents, rels = [], []
        for it in v:
            if not isinstance(it, dict):
                continue
            if _looks_like_relation(it):
                rels.append(it)
            elif _looks_like_entity(it):
                ents.append(it)
        if ents or rels:
            return {"entities": ents, "relations": rels}
        return None

    if not isinstance(v, dict):
        return None

    if "entities" in v or "relations" in v:
        return v

    # 包壳：{"data": {...}} / {"result": {...}} / {"output": {...}}
    for k in ("data", "result", "output", "answer", "json"):
        inner = v.get(k)
        if isinstance(inner, (dict, list)):
            got = _coerce_envelope(inner)
            if got is not None:
                return got

    # 单实体
    if _looks_like_entity(v):
        return {"entities": [v], "relations": []}
    # 单关系
    if _looks_like_relation(v):
        return {"entities": [], "relations": [v]}
    return None


def _looks_like_entity(d: dict) -> bool:
    return "name" in d and ("type" in d or "aliases" in d or "desc" in d)


def _looks_like_relation(d: dict) -> bool:
    return ("src" in d or "subject" in d) and ("dst" in d or "object" in d)


def _score(v: object) -> int:
    """候选信息量：实体/关系条目数越多越可信。"""
    if isinstance(v, dict):
        e = v.get("entities")
        r = v.get("relations")
        return (len(e) if isinstance(e, list) else 0) + \
               (len(r) if isinstance(r, list) else 0)
    return 0


def _escape_inner_quotes(s: str) -> str:
    """转义字符串值内部**未转义**的 ASCII 双引号。

    实测高频故障：模型在 desc/evidence 里引用原文时写成 ASCII `"` 而非中文引号，
    例如 ``"desc":"信奉"受苦者"的使徒"`` —— 这是非法 JSON，会让整段输出解析失败，
    进而静默退化（kimi 在该块上 13 实体 10 关系被解析成 1 实体 0 关系）。

    判据：在字符串上下文里遇到 `"` 时向前看下一个非空白字符——
    是 `,` `:` `}` `]` 之一（或已到结尾）则视为**真正的收尾引号**，
    否则它属于内容，转义为 ``\\"``。该启发式对正常的转义序列
    （``\\\\`` 与 ``\\"``）保持原样，不会破坏合法 JSON。
    """
    out: list[str] = []
    in_str = False
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if not in_str:
            out.append(c)
            if c == '"':
                in_str = True
            i += 1
            continue
        # ── 字符串内部 ──
        if c == "\\":
            out.append(c)
            if i + 1 < n:
                out.append(s[i + 1])
            i += 2
            continue
        if c == '"':
            j = i + 1
            while j < n and s[j] in " \t\r\n":
                j += 1
            if j >= n or s[j] in ",:}]":
                out.append('"')
                in_str = False
            else:
                out.append('\\"')
            i += 1
            continue
        out.append(c)
        i += 1
    return "".join(out)


def _try_load(s: str) -> object | None:
    """直接解析，失败则先转义内部引号再解析。"""
    try:
        return json.loads(s)
    except ValueError:
        pass
    try:
        return json.loads(_escape_inner_quotes(s))
    except ValueError:
        return None


def parse_json_loose(text: str) -> dict | None:
    """容错 JSON 解析：直接 → 剥围栏 → 内部引号转义 → 全量配平扫描 → 畸形修复。"""
    if not text or not text.strip():
        return None
    s = text.strip()

    # ① 直接（含内部引号转义兜底）
    raw = _try_load(s)
    if raw is not None:
        got = _coerce_envelope(raw)
        if got is not None:
            return got

    # ② 剥 ``` 围栏
    for body in sorted(RE_FENCE.findall(s), key=len, reverse=True):
        raw = _try_load(body.strip())
        if raw is not None:
            got = _coerce_envelope(raw)
            if got is not None:
                return got

    # ③ 全量配平扫描（在**转义后**的文本上做，避免内部引号干扰配平），
    #    取信息量最大者（避免"第一个配平块"陷阱）
    for text_variant in (s, _escape_inner_quotes(s)):
        cands = _scan_json_values(text_variant)
        envelopes = [c for c in (_coerce_envelope(v) for v in cands)
                     if c is not None]
        if envelopes:
            best = max(envelopes, key=_score)
            if _score(best) > 0:
                return best

    # ④ 整体畸形修复
    rep = _repair(s) or _repair(_escape_inner_quotes(s))
    return _coerce_envelope(rep) if rep is not None else None



def _repair(s: str) -> object | None:
    """常见畸形修复：尾逗号 / 中文标点 / 单引号 / 未闭合括号。"""
    cand = s
    # 未闭合：补齐结尾括号
    opens = cand.count("{") - cand.count("}")
    if opens > 0:
        cand = cand + "}" * opens
    opens_b = cand.count("[") - cand.count("]")
    if opens_b > 0:
        cand = cand + "]" * opens_b
    cand = re.sub(r",\s*([}\]])", r"\1", cand)          # 尾逗号
    cand = cand.replace("：", ":").replace("，", ",")     # 中文标点
    cand = re.sub(r"(?<=[{,\[])\s*'([^']*)'\s*:", r'"\1":', cand)
    try:
        return json.loads(cand)
    except ValueError:
        return None


class CloudLLM:
    """OpenAI 兼容云端 LLM 客户端（异步、并发受控、带重试）。"""

    def __init__(self, base_url: str, api_key: str, model: str,
                 temperature: float = 0.1, max_tokens: int = 2048,
                 timeout: float = 120.0, concurrency: int = 8,
                 max_retries: int = 3) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.concurrency = max(1, concurrency)
        self.max_retries = max(1, max_retries)
        self._sem: asyncio.Semaphore | None = None
        self._client: httpx.AsyncClient | None = None
        self.usage = {"prompt_tokens": 0, "completion_tokens": 0, "calls": 0,
                      "retries": 0, "failures": 0}
        self.quota_dead = False
        self.gateway_dead = False
        self._lock = asyncio.Lock()

    def _endpoint(self) -> str:
        if self.base_url.endswith("/chat/completions"):
            return self.base_url
        return self.base_url + "/chat/completions"

    async def __aenter__(self) -> "CloudLLM":
        self._sem = asyncio.Semaphore(self.concurrency)
        self._client = httpx.AsyncClient(timeout=self.timeout)
        return self

    async def __aexit__(self, *exc) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def _post(self, messages: list[dict], max_tokens: int | None = None,
                    json_mode: bool = True) -> dict:
        assert self._client is not None, "请用 async with CloudLLM(...) 使用"
        payload: dict = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": max_tokens or self.max_tokens,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        r = await self._client.post(
            self._endpoint(), json=payload,
            headers={"Authorization": f"Bearer {self.api_key}",
                     "Content-Type": "application/json"})
        if r.status_code != 200:
            body = r.text[:400]
            if any(m in body for m in QUOTA_MARKERS):
                # 额度耗尽：重试无意义，立即抛出专用异常
                self.quota_dead = True
                raise LLMQuotaExhausted(f"HTTP {r.status_code} 额度已用尽：{body[:160]}")
            raise LLMError(f"HTTP {r.status_code}: {body[:200]}")
        return r.json()

    async def complete_json(self, system: str, user: str,
                            max_tokens: int | None = None) -> tuple[dict, LLMResult]:
        """带重试的结构化调用。返回 (解析后的 dict, 元信息)。"""
        assert self._sem is not None, "请用 async with CloudLLM(...) 使用"
        messages = [{"role": "system", "content": system},
                    {"role": "user", "content": user}]
        last: Exception | None = None

        async with self._sem:
            for attempt in range(1, self.max_retries + 1):
                if self.quota_dead:
                    # 同一进程内额度已确认耗尽：后续块直接失败，不再打网关、
                    # 不再退避重试（实测曾为此浪费 6038 次重试）
                    raise LLMQuotaExhausted("额度已用尽（本次运行已标记，跳过后续调用）")
                if self.gateway_dead:
                    raise LLMGatewayUnreachable(
                        "网关不可达（本次运行已标记，跳过后续调用）")
                try:
                    j = await self._post(messages, max_tokens=max_tokens)
                except LLMQuotaExhausted:
                    raise
                except Exception as exc:  # noqa: BLE001
                    # 注意：httpx.ConnectError 的 **str() 是空串**，消息只在 repr() 里
                    # （实测 `str(ConnectError('All connection attempts failed')) == ''`），
                    # 因此必须同时看 str 与 repr，否则网关不可达检测永远不触发。
                    blob = f"{exc!s} {exc!r}"
                    if any(m in blob for m in GATEWAY_DOWN_MARKERS):
                        self.gateway_dead = True
                        raise LLMGatewayUnreachable(
                            f"网关不可达：{blob.strip()[:120]}") from exc
                    last = exc
                    await self._backoff(attempt, f"transport: {blob[:120]}")
                    continue

                usage = j.get("usage") or {}
                async with self._lock:
                    self.usage["calls"] += 1
                    self.usage["prompt_tokens"] += int(usage.get("prompt_tokens") or 0)
                    self.usage["completion_tokens"] += int(usage.get("completion_tokens") or 0)

                ch = (j.get("choices") or [{}])[0]
                msg = ch.get("message") or {}
                content = msg.get("content") or ""
                finish = ch.get("finish_reason") or ""
                meta = LLMResult(
                    text=content, model=j.get("model", self.model),
                    prompt_tokens=int(usage.get("prompt_tokens") or 0),
                    completion_tokens=int(usage.get("completion_tokens") or 0),
                    attempts=attempt, finish_reason=finish)

                if not content.strip():
                    # 推理模型烧光 token 的典型症状：重试无益但偶发，退避后再试
                    last = LLMEmptyContent(
                        f"content 为空 (finish={finish}, "
                        f"reasoning={len(msg.get('reasoning_content') or '')}ch)")
                    await self._backoff(attempt, str(last))
                    continue

                parsed = parse_json_loose(content)
                empty = parsed is not None and not (parsed.get("entities")
                                                    or parsed.get("relations"))
                if parsed is not None and finish != "length" and not empty:
                    return parsed, meta
                if parsed is not None and finish != "length" and empty:
                    # 实测过的静默故障：模型 900 token 只吐出一个实体对象而没有信封，
                    # 旧解析器把它当成整个响应 → 12 个实体塌缩成 0 个。
                    # 新解析器已能解出裸数组，但仍保留一次重试作为兜底。
                    last = LLMEmptyContent("解析成功但 entities/relations 均为空")
                    if attempt < self.max_retries:
                        await self._backoff(attempt, str(last))
                        continue
                    return parsed, meta
                if parsed is not None and finish == "length":
                    # 截断但已能解析：接受（调用方按结构完整性自行判断）
                    logger.warning("输出被截断但 JSON 可解析：%s", self.model)
                    return parsed, meta
                last = LLMTruncated(f"finish={finish} 且 JSON 解析失败") \
                    if finish == "length" else LLMError("JSON 解析失败")
                await self._backoff(attempt, str(last))

            async with self._lock:
                self.usage["failures"] += 1
            raise LLMError(f"重试 {self.max_retries} 次仍失败：{last}")

    async def complete_text(self, messages: list[dict] | str, user: str | None = None,
                            max_tokens: int | None = None) -> tuple[str, LLMResult]:
        """**文本模式**调用：不解析 JSON，也不向网关发 ``response_format``。

        与 :meth:`complete_json` 共用传输与重试骨架，区别只在「怎么判成功」：
        文本回答没有信封可解析，因此**只有空 content 才重试**；
        ``finish_reason == "length"`` 的截断结果照样返回（调用方看 ``meta`` 自行处置），
        因为截断的答案对作答通路仍是可用的证据输出，丢掉它反而制造静默失败。

        ``messages`` 既接受 OpenAI 风格的消息列表（:func:`compendium_rag.compose.compose`
        的产物），也接受 ``complete_text(system, user)`` 的旧式两参写法。

        为什么不复用 ``complete_json``：那条路径会对回答做 JSON 容错解析，
        而作答是自由文本；强行套用会把正常答案判成「解析失败」并白烧重试
        （与抽取期的静默降级是同一类故障）。
        """
        assert self._sem is not None, "请用 async with CloudLLM(...) 使用"
        if isinstance(messages, str):
            payload_messages = [{"role": "system", "content": messages},
                                {"role": "user", "content": user or ""}]
        else:
            payload_messages = list(messages)
        last: Exception | None = None

        async with self._sem:
            for attempt in range(1, self.max_retries + 1):
                if self.quota_dead:
                    raise LLMQuotaExhausted("额度已用尽（本次运行已标记，跳过后续调用）")
                if self.gateway_dead:
                    raise LLMGatewayUnreachable(
                        "网关不可达（本次运行已标记，跳过后续调用）")
                try:
                    j = await self._post(payload_messages, max_tokens=max_tokens,
                                         json_mode=False)
                except LLMQuotaExhausted:
                    raise
                except Exception as exc:  # noqa: BLE001
                    # 与 complete_json 同因：httpx.ConnectError 的 str() 是空串，
                    # 不并看 repr() 则网关不可达检测永不触发。
                    blob = f"{exc!s} {exc!r}"
                    if any(m in blob for m in GATEWAY_DOWN_MARKERS):
                        self.gateway_dead = True
                        raise LLMGatewayUnreachable(
                            f"网关不可达：{blob.strip()[:120]}") from exc
                    last = exc
                    await self._backoff(attempt, f"transport: {blob[:120]}")
                    continue

                usage = j.get("usage") or {}
                async with self._lock:
                    self.usage["calls"] += 1
                    self.usage["prompt_tokens"] += int(usage.get("prompt_tokens") or 0)
                    self.usage["completion_tokens"] += int(usage.get("completion_tokens") or 0)

                ch = (j.get("choices") or [{}])[0]
                msg = ch.get("message") or {}
                content = msg.get("content") or ""
                finish = ch.get("finish_reason") or ""
                meta = LLMResult(
                    text=content, model=j.get("model", self.model),
                    prompt_tokens=int(usage.get("prompt_tokens") or 0),
                    completion_tokens=int(usage.get("completion_tokens") or 0),
                    attempts=attempt, finish_reason=finish)

                if content.strip():
                    if finish == "length":
                        logger.warning("作答被 max_tokens 截断：%s", self.model)
                    return content, meta

                last = LLMEmptyContent(
                    f"content 为空 (finish={finish}, "
                    f"reasoning={len(msg.get('reasoning_content') or '')}ch)")
                await self._backoff(attempt, str(last))

            async with self._lock:
                self.usage["failures"] += 1
            raise LLMError(f"重试 {self.max_retries} 次仍失败：{last}")

    async def _backoff(self, attempt: int, why: str) -> None:
        if attempt >= self.max_retries:
            return
        async with self._lock:
            self.usage["retries"] += 1
        delay = min(30.0, 1.5 ** attempt) + random.uniform(0, 0.6)
        logger.debug("LLM 重试 %d/%d（%s），%.1fs 后重试",
                     attempt, self.max_retries, why, delay)
        await asyncio.sleep(delay)

    def usage_summary(self) -> dict:
        u = dict(self.usage)
        u["total_tokens"] = u["prompt_tokens"] + u["completion_tokens"]
        return u
