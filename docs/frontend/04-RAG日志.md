# 04 · RAG 日志（需求 4）

> 对应 ADR：**D10**（默认 hash，环境变量开全文）、**D11**（三层漏斗全记）、**D12**（先修 3 个缺陷）、**D19**（`logs/rag/`，明文 7 天 + 归档 90 天）、**D20**（第一期不做 UI）。
> 所属阶段：**P2**（最先开工，见 D02）。

---

## 目录

1. 需求原文与三种读法
2. 现有链路全貌（配置 → 调用 → 落盘）
3. 现有 trace schema v1 逐字段
4. 5 个必须先修的存量缺陷
5. 块编号方案
6. 三层漏斗（最容易做错的地方）
7. Schema v2 设计
8. 日志体系（新文件 + handler）
9. 体积 / 压缩 / 加密实测
10. 轮转与归档
11. 测试影响面
12. 验收标准
13. 明确不做

---

## 1. 需求原文与三种读法

用户原话：

> rag 这一块加个日志吧，后面出问题了也好分析，日志里面要包括**输出问题**和**返回块的编号**之类的吧，反正后续分析日志时能够分析出来，通过加密和压缩，来减少内存。

「输出问题」有三种读法，**三种都要做**：

| # | 读法 | 落点 |
|---|---|---|
| ① | **三元组** `{问题, 用了哪些块, 回答了什么}` —— **最可能的本意** | `src/roleplay/core/orchestrator.py:1027-1035`（`run()` 收口）与 `:1096-1106`（`stream()` 收口） |
| ② | **系统自发现的异常告警**（空结果 / 全通道 skip / 索引失效 / 嵌入服务不可用 / 分数退化 / 超时 / 预算截断 / 语料指纹不符） | 新写告警逻辑，读 trace 字段判定 |
| ③ | **问题与答案靠 `trace_id` join 的配对记录**（流式断流时不丢） | 新增 `trace_id` 字段 |

---

## 2. 现有链路全貌

### 2.1 配置链路（已逐环核实）

```
src/roleplay/config.py:398          plot_trace_enabled: bool = False
        ↓ env_prefix="ROLEPLAY_" (config.py:52-55) ⇒ ROLEPLAY_PLOT_TRACE_ENABLED=true 可覆盖，无需改码
src/roleplay/core/knowledge/factory.py:248-251
        ↓
src/roleplay/core/knowledge/plot_graph.py:2122-2125   (存 self.trace_enabled)
src/roleplay/core/knowledge/plot_graph.py:683-688     (存 self.trace_out_path)
        ↓
src/roleplay/core/knowledge/plot_graph.py:1423-1430   TraceCollector(...)   ← 唯一生产调用点
        ↓
src/roleplay/core/knowledge/plot_graph.py:1774        self.last_trace = tc.finish(query=query, final_chunks=out)
```

**上游入口**：`src/roleplay/core/orchestrator.py:288-312` 的 `_plot_retrieve()`（`asyncio.to_thread(retriever.retrieve, ...)`）。

### 2.2 相关配置字段（`src/roleplay/config.py`）

| 行 | 字段 | 默认值 | 与本任务的关系 |
|---|---|---|---|
| `:398` | `plot_trace_enabled` | `False` | **总开关** |
| `:199` | `plot_max_chunks` | `6` | 融合层条数预算 |
| `:200` | `plot_lexical_fallback` | `2` | 词法兜底条数 |
| `:220` | `plot_context_max_chars` | `2400` | **进提示词的字符预算**（真正的二次截断） |
| `:142` | `chunk_size` | `600` | 影响块编号里的 `seq`（**漂移源**） |
| `:192` | `plot_corpus_dir` | `"./data/knowledge"` | 语料落盘根 |
| `:7` / `:57` | `frozen=True` | — | **配置仅启动时解析一次，运行期不可改** |
| `:336` / `:337` | `plot_min_semantic_kept` / `plot_min_chapter_kept` | `0` / `0` | 融合层保底名额 |

### 2.3 落盘函数（`src/roleplay/core/knowledge/retrieval_trace.py:284-298`）

```python
def trace_path(base_dir: str | Path, character_id: str) -> Path:
    return Path(base_dir) / "_audit" / "retrieval_trace" / f"{character_id}.jsonl"

def append_jsonl(path, trace) -> bool:
    """追加一条 trace。**任何异常都吞掉**——埋点失败绝不能影响检索主链路。"""
```

**现文件**：`data/knowledge/_audit/retrieval_trace/wu_ming_zhe.jsonl` = **882,956 B / 364 行**（2026-09-13 ~ 09-16）。
**已被 gitignore**（`.gitignore:85 data/knowledge/_audit/retrieval_trace/`）。

---

## 3. 现有 trace schema v1 逐字段（`retrieval-trace-v1`）

### 3.1 常量（`retrieval_trace.py`）

| 行 | 常量 | 值 |
|---|---|---|
| `:35` | `TRACE_SCHEMA` | `"retrieval-trace-v1"` |
| `:36` | `ABLATION_SCHEMA` | `"ablation-v1"`（**独立，互不影响**） |
| `:40` | `CHANNEL_ORDER` | `("别名精确", "BM25 兜底", "语义向量", "图传播", "篇章路由", "扩展查询")` —— **顺序不可调** |
| `:44-52` | `PATH_TO_CHANNEL` | `exact→别名精确` / `lexical→BM25 兜底` / `semantic→语义向量` / `edge→图传播` / `chapter→篇章路由` / `semantic_zh→扩展查询` / `mention→图传播`（兜底，实际由 `seed_path` 决定） |
| `:55-66` | `ChannelSkipReason` | **9 值固定**：`not_enabled` / `index_missing` / `fingerprint_stale` / `embed_failed` / `no_seed` / `gate_rejected` / `no_candidate` / `rerank_unavailable` / `budget_exhausted` |
| `:72-74` | `query_hash()` | `sha256(query)[:16]`；docstring 原文：**「绝不落盘查询原文（PRD §9 隐私约束）」** |
| `:77-83` | `config_hash()` | 只取 `plot_*` 前缀的键，`sha256[:16]` |
| `:86-101` | `channel_of_block()` | `mention` 块按 `seed_path` 归组（`semantic`→语义向量 / `token`→BM25 兜底 / 其它→别名精确） |

### 3.2 `ChannelRecord`（`:104-140`）

```python
channel: str; enabled: bool; executed: bool = False
hit_count: int = 0      # 该通道本轮命中数（自然单位）
hit_blocks: int = 0     # 归因到的候选块数（与 kept_in_final 同量纲）
skip_reason: str | None; latency_ms: float = 0.0; weight: float = 1.0
kept_in_final: int = 0; detail: dict
```

> **`hit_count` 与 `hit_blocks` 是两个不同量纲**，代码注释 `:108-113` 明确写了。`hit_count == 0` 时**必须**带 `skip_reason`（`:132-140` 的契约硬约束）。

### 3.3 `RetrievalTrace`（`:171-280`）顶层字段

| 字段 | 类型 | 来源 |
|---|---|---|
| `character_id` | str | `TraceCollector.__init__` |
| `query_lang` | str | `detect_lang(query)` |
| `query_len` | int | `finish()` |
| `pipeline_version` | str | 默认 `"plot-v1.0"` |
| `config_hash` | str | `config_hash(config)` |
| `seeds_total` | int | `set_seeds()` |
| `seeds[]` | list | 6 字段：`entity_id` / `name` / `seed_path` / `weight` / `specificity` / `gate_passed` |
| `channels[]` | list | **固定 6 条** |
| `entity_link_margin` | `EntityLinkMargin` | `triggered` / `candidates` / `top1_score` / `top2_score` / `margin` / `threshold` / `linked` / `reject_reason` |
| `fallbacks` | list[str] | `fallback()` 去重累积 |
| `latency` | dict | `link_ms` / `fuse_ms` / `total_ms` / `semantic_ms` |
| `final_chunks` | int | **只是条数**（不是块列表）⚠️ |
| `final_paths` | dict[str,int] | path → 计数 |
| `event` | str | `"retrieval_trace"` |
| `trace_schema` | str | `"retrieval-trace-v1"` |
| `query_hash` | str | sha256[:16] |
| `timestamp` | str | `time.strftime("%Y-%m-%dT%H:%M:%S")` —— **本地时间、无时区、无毫秒** |

### 3.4 364 条历史 trace 的实测聚合（这是判断"哪些字段没用"的依据）

| 指标 | 实测 |
|---|---|
| `latency.total_ms` | mean **554.5** / p50 **495.4** / max **3216.8** |
| `final_chunks` | mean **7.02** |
| **「扩展查询」通道** | **364/364 从未启用** |
| **`fallbacks` 非空** | **0/364**（该路径从未被验证） |
| `entity_link_margin.triggered` | 仅 **6/364** |
| `query_lang` | `other` 252 / `zh` 112 |
| `latency_ms` 字段 | **2184/2184 全 0.0**（缺陷⑤） |

通道表（`hit` / `kept_in_final` 均值）：

| 通道 | hit 均值 | kept 均值 | 说明 |
|---|---|---|---|
| 别名精确 | **1.18** | **2.94** | **kept > hit ⇒ 归因口径有缺陷**（见 §4-②） |
| 图传播 | 14.98 | 2.66 | — |
| 语义向量 | 4.38 | 2.63 | — |
| 篇章路由 | — | — | — |
| BM25 兜底 | — | — | — |
| 扩展查询 | 0 | 0 | 从未启用 |

---

## 4. 5 个必须先修的存量缺陷（D12）

> **不修的话，新日志从第一天起就是脏数据。**

### ① `trace_path` 路径穿越（**安全洞**）

`retrieval_trace.py:284-285`：

```python
def trace_path(base_dir, character_id) -> Path:
    return Path(base_dir) / "_audit" / "retrieval_trace" / f"{character_id}.jsonl"
```

`character_id` **未做任何清洗**，直接来自 `ChatRequest.character_id`（`src/roleplay/models/chat.py:78`，**未鉴权**）。

⇒ `character_id="../../etc/passwd"` 即可写到任意位置。

**历史备案**（此问题在过往 QA 已被记录三次）：
- `deliverables/qa_reports/04-channel-voice.md:115`
- `deliverables/qa_reports/00-SUMMARY.md:293`
- `deliverables/qa_reports/07-FIX-REPORT.md:224`

**修法**：
```python
import re
_SAFE_CID = re.compile(r"[^A-Za-z0-9_\u4e00-\u9fff-]+")
def trace_path(base_dir, character_id) -> Path:
    cid = _SAFE_CID.sub("_", str(character_id or "")).strip("._") or "unknown"
    return Path(base_dir) / "_audit" / "retrieval_trace" / f"{cid}.jsonl"
```

### ② mention 归因系统性失效

`channel_of_block()`（`:86-101`）依赖 `meta["seed_path"]`。但产生 mention 块的两处（`plot_graph.py:1235`、`:1249`）只写：

```python
{"path": "mention", "seed_mention": name}
```

**全仓从未写入 `seed_path`** ⇒ `channel_of_block` 永远走 `return "别名精确"` 的兜底分支 ⇒ **所有 mention 块都被算成「别名精确」**。

**直接后果**：`别名精确` 的 `kept(2.94) > hit(1.18)` —— 这正是缺陷的读数特征（不可能读数）。

**修法**：在 `:1235` / `:1249` 的 dict 里补 `"seed_path": <种子来源>`。

### ③ 语义通道跳过原因撒谎

`plot_graph.py:1470`：

```python
_sem_skip: ChannelSkipReason = ChannelSkipReason.NOT_ENABLED
```

`_:1474` 改成 `NO_CANDIDATE`、`:1479` 改成 `EMBED_FAILED`、`:1542` 改成 `NO_SEED` —— **但「索引不可用/语料指纹不符」这条路径从不改写 `_sem_skip`**。

**实测矛盾**：启动日志说「语料指纹不符」，trace 里却记 `not_enabled`。

**修法**：在 `:1472` 的 `if` 之前加分支，索引不可用时置 `INDEX_MISSING` 或 `FINGERPRINT_STALE`。

### ④ `detail` 双层嵌套

产出是 `{"detail": {"detail": {...}}}`。原因是 `tc.mark(..., detail={...})` 的 `detail` 关键字被 `mark()` 的 `**detail` 收进 `rec.detail.update(detail)`，而调用方传的是 `detail={...}` 这个键。

**修法**：`mark()` 里加 `detail.pop("detail", None)` 的特殊处理，或调用方改成 `tc.mark(..., **{"detail": ...})` 反过来拆开。

### ⑤ `latency_ms` 恒 0

`ChannelRecord.latency_ms: float = 0.0`，全仓**没有任何地方写入**它（2184/2184 全 0.0）。

**修法**：在 `tc.mark()` 调用前后用已有的 `tc.stage(...)` 包一层，或直接删掉这个字段（已确认无人读）。

### 附带：`timestamp` 无时区无毫秒

`:244` `time.strftime("%Y-%m-%dT%H:%M:%S")` —— 本地时间、无 tz、无毫秒 ⇒ **跨时区/跨机器不可比**。

**修法**：改用 `datetime.now(timezone.utc).isoformat(timespec="milliseconds")`。

---

## 5. 块编号方案（组合式）

> ⚠️ **命名说明**：本章方案在原始分析报告里编号为「B4」，但 README §4 的 bug 清单里 `B4` 指的是 `chat.js` 的 `finally` 缺陷。**为避免混淆，本文一律称"组合式块编号"，不写 B4。**

### 5.1 格式

```
B{rank:02d}[{doc_id}#{seq}|h={hash[:6]}|{paths_joined}]
```

**实测样例**：

```
B01[huiji_cmp_圣火纪行_东区黎明#14|h=8bca4c|edge]
```

### 5.2 三段各是什么

| 段 | 来源 | 稳定性 |
|---|---|---|
| `B{rank:02d}` | 融合后名次 | **绝不参与跨轮关联**（同一问题的两次运行可能不同） |
| `doc_id` | 语料文档 id | ✅ 稳定 |
| `seq` | 文档内块序号 | ⚠️ **随 `chunk_size` 变而漂移**（`.env` 现 `ROLEPLAY_CHUNK_SIZE=600`） |
| `h=` | `sha1(text)[:16]` 的前 6 位 | ✅ 内容稳定，但**清洗规则一改全变** |
| `paths` | 该块命中的通道 path 列表 | 稳定 |

### 5.3 体积代价

**+14.8%**（359 B / 7 块）。

### 5.4 为什么不用纯序号

纯 `B01` 无法跨轮追溯：同一块在第 2 轮可能变成 `B03`。组合式的 `doc_id#seq + h=` 才是块的身份。

---

## 6. 三层漏斗（**最容易做错的地方**）

「返回的块」在代码里有**三层**，实测条数差异巨大：

| 层 | 位置 | 实测条数 | 说明 |
|---|---|---|---|
| ① **通道候选** | `plot_graph.py:1559-1686` | 图传播 hit=**20**、语义 hit=**5** | 各通道原始候选池 |
| ② **融合后返回** | `plot_graph.py:1762-1767`（RRF + `top_chunks + lexical_fallback` 截断） | **6~8 块** | `plot_max_chunks=6` + `lexical_fallback=2` |
| ③ **真正进提示词** | `src/roleplay/core/persona_prompt.py:253-266` `build_plot_context()` | **4~5 块** | 见下 |

### 6.1 第③层的两道门 + 一道预算

`persona_prompt.py`：

| 行 | 机制 | 值 |
|---|---|---|
| `:33` | `MIN_CONTEXT_SCORE` **绝对门** | `0.05` |
| `:39` | `RELATIVE_SCORE_GATE` **相对门** | `0.85 × 同组 top1` |
| `:47` | `BUDGETED_SCORE_GROUPS` | `("plot_graph", "plot_lexical")` —— **豁免相对门** |
| `:83-117` | `_filter_chunks()` | 分组后逐组过门 |
| `:253-266` | `build_plot_context()` | `plot_context_max_chars=2400` 字符预算截断 |

**关键算术**：块均 **503 字** ⇒ `2400 / 503 ≈ 4.8` ⇒ **实际只进 4~5 块**。

### 6.2 ⇒ 现有 `final_chunks=8` 是**第②层**，不是"回答实际用了哪些块"

这就是为什么 D11 要求**三层全记**：只看第②层，永远答不了「某个块为什么没被回答用上」。

---

## 7. Schema v2 设计

### 7.1 原则

| 原则 | 说明 |
|---|---|
| **只加不删** | 现有 v1 字段全部保留（3 个测试断言依赖它们） |
| **顶层 `trace_schema` 升 v2** | `ABLATION_SCHEMA` **不动**（两者独立） |
| **新字段全 optional** | 保证老 trace 读得动、老代码不会 KeyError |
| **`trace_id` 新增** | 用于 join 问题与答案 |

### 7.2 新增字段

```jsonc
{
  "trace_schema": "retrieval-trace-v2",   // ← 升版
  "trace_id": "20261020T190315-a1b2c3d4", // 新增：毫秒级 UTC + 随机后缀

  // ① 通道候选层（D11 第一层）
  "candidates": [
    {"channel": "图传播", "block_id": "B01[...#14|h=8bca4c|edge]", "rank": 1, "score": 0.93}
    // 最多 20 条
  ],

  // ② 融合层（D11 第二层）
  "fused": [
    {"block_id": "...", "rank": 1, "score": 0.93, "paths": ["edge","mention"]}
    // 6~8 条
  ],

  // ③ 进提示词层（D11 第三层）
  "injected": [
    {"block_id": "...", "rank": 1, "score": 0.93,
     "chars": 503,
     "kept": true,
     "drop_reason": null   // 或 "relative_gate" | "absolute_gate" | "char_budget"
    }
    // 4~5 条 kept=true，其余记 drop_reason
  ],

  // ① 问题与回答（D10：默认只 hash，环境变量开全文）
  "query": {
    "hash": "a1b2c3d4e5f6a7b8",   // 已有 query_hash，此处冗余但便于 join
    "len": 14,
    "preview": null               // 仅 ROLEPLAY_RAG_LOG_FULL=1 时填
  },
  "answer": {
    "len": 186,
    "preview": null,              // 仅 FULL=1 时填
    "chars": 186,
    "tokens_est": 93
  },

  // ② 系统自发现异常（读上面字段判定）
  "alerts": [
    {"code": "all_channels_skipped", "severity": "high", "detail": "..."}
    // code 枚举见 §7.3
  ]
}
```

### 7.3 `alerts[].code` 枚举（需求「输出问题」的第二种读法）

| code | 触发条件 | severity |
|---|---|---|
| `empty_result` | `final_chunks == 0` | high |
| `all_channels_skipped` | 6 个通道全部 `skip_reason != None` | high |
| `index_missing` | 任通道 `skip_reason == "index_missing"` | critical |
| `fingerprint_stale` | 任通道 `skip_reason == "fingerprint_stale"` | critical |
| `embed_failed` | `"embed_failed" in fallbacks` | high |
| `score_degraded` | `top1_score < MIN_CONTEXT_SCORE` | medium |
| `timeout` | `total_ms > 3000` | medium |
| `budget_truncated` | 有块 `drop_reason == "char_budget"` | low |
| `fusion_squeeze` | `hit_count - kept_in_final > 0` 且某通道全灭 | medium |
| `attribution_anomaly` | `kept_in_final > hit_blocks`（已修②后不应出现） | high |

### 7.4 全文的开关（D10）

| 级别 | 环境变量 | 落盘内容 | 单条体积 |
|---|---|---|---|
| **L0**（默认） | — | 只有 hash + 块编号 | **2,424 B** |
| L1 | — | + 块元数据摘要 | ~2,700 B |
| L2 | `ROLEPLAY_RAG_LOG_FULL=1` | + **问题原文 + 回答原文** | +583 B |
| L3 | `ROLEPLAY_RAG_LOG_ENC=1` | L2 + 加密 | +48 B/包 |

> **隐私纪律的出处是悬挂引用**（重要发现）：`retrieval_trace.py:13-16` docstring 声称「架构 §7.6.5」、`:73` 声称「PRD §9」—— 但 `docs/roleplay-core/architecture/ARCHITECTURE.md` 与 `RAG_SYSTEM_DESIGN.md` grep `7.6|埋点|trace|隐私|query_hash` **均 0 命中**，全仓**不存在任何 PRD 文档**。
> ⇒ 实际权威只有代码注释 + `tests/test_plotrag_trace.py:144` 一个测试。**所以 D10 的选择不是"违反已有规范"，而是"补上缺失的规范"。**

---

## 8. 日志体系（新文件 + handler）

### 8.1 现状盘点

| 项 | 实测 |
|---|---|
| `logging.basicConfig` 调用点 | **仅 2 处**：`src/roleplay/main.py:80-83`（在 `lifespan()` 内）、`src/compendium_rag/cli.py:32` |
| `RotatingFileHandler` / `FileHandler` / `dictConfig` / JSON formatter | **全 0 处** |
| `logging.getLogger` | 48 处，**全走 root** |
| 请求日志 | `src/roleplay/middleware.py:43-74`，只记 `method / path / status / elapsed` |
| `logs/` 目录 | 76 个文件 / 3.05 MB，其中约 70 个是离线评测脚本重定向；真运行期只有 `server.log` / `server.err.log`（手工重定向） |
| `data/knowledge/_audit/` | **201 MB 零清理策略**（`p4_harness_r10` 39MB / `r11` 16.5MB / `ablation` 10.4MB / `retrieval_trace` 0.8MB / `_drift_embed_cache.npz` 72.6MB） |

### 8.2 两套并存（D19）

| 轨道 | 文件 | 用途 | 格式 |
|---|---|---|---|
| **结构化快照**（主） | `logs/rag/trace-YYYYMMDD.jsonl` | 事后分析、脚本 grep、归档 | JSONL，一行一条 |
| **异常告警**（辅） | `logs/rag/alerts.log` | 人眼看、tail -f | 文本 + `RotatingFileHandler` |

**为什么不只用一个**：JSONL 便于机器分析但人眼难读；`alerts.log` 人眼友好但结构弱。两者互补。

### 8.3 handler 接线（**必须在 `basicConfig` 之后**）

`src/roleplay/config.py:7` 明确写了 `frozen=True` —— **配置仅启动时解析一次**。所以 handler 的启用也要在启动期决定。

接线位置：`src/roleplay/main.py:80-83` 的 `lifespan()` 内、`basicConfig` 之后：

```python
from logging.handlers import RotatingFileHandler
rag_log_dir = Path("logs/rag"); rag_log_dir.mkdir(parents=True, exist_ok=True)
h = RotatingFileHandler(rag_log_dir / "alerts.log",
                        maxBytes=10 * 1024 * 1024, backupCount=5,
                        encoding="utf-8")
h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
logging.getLogger("roleplay.rag").addHandler(h)
logging.getLogger("roleplay.rag").setLevel(logging.WARNING)
```

### 8.4 `.gitignore`

`logs/` **已在 `.gitignore:37`** ⇒ 新目录零改动。

---

## 9. 体积 / 压缩 / 加密实测

### 9.1 单条 trace 体积

| 级别 | 体积 |
|---|---|
| L0（hash） | **2,424 B** |
| + 组合式块编号 | 2,843 B |
| + 全文 | 3,183 B |

### 9.2 压缩实测（roundtrip 全部 ✅）

| 对象 | 原始 | zlib-9 | lzma-6 | bz2-9 |
|---|---|---|---|---|
| 单条 trace | 2,372 B | 916（0.386） | — | — |
| **364 条 trace** | **882,956 B** | 41,162（0.0466） | **31,296（0.0354）** | 26,485（0.0300） |
| `plot_corpus_wu_ming_zhe.json` | 21,570,352 B | — | 3,995,164（0.1852） | — |
| `plot_graph` | 10,134,527 B | — | 933,340（0.0921） | — |
| `graph_wu_ming_zhe.json` | 41,077,591 B | 14,159,655（0.3447） | 未跑 | — |

> **最关键的一条：必须批量压，不能逐条压。**
> 逐条 zlib 压缩率 **0.39** vs 批量 lzma **0.0354** ⇒ **11 倍差**。
> 原因：单条 JSON 太短，zlib 字典没法复用键名。

### 9.3 加密纠正（用户「加密减少内存」是误解）

| 事实 | 数据 |
|---|---|
| 容器头开销 | `MAGIC(4) + salt(16) + nonce(12) + GCM tag(16)` = **+48 B/包** |
| 加密后熵 | ≈1.0 ⇒ **不可再压** |
| **正确顺序** | **`compress → encrypt`** |
| 实测 | 882,956 B → lzma 31,296 → 密文 **31,344** = **0.0355** |
| 反序后果 | `encrypt → compress` 压缩率退化为 **1.0**（白做） |
| Scrypt `n=2^14` 代价 | **30.1 ms** ⇒ **必须每文件派生一次**（每条派生的话 1000 条要 30 秒） |
| salt 位置 | 放**文件头**（不是每条） |
| 完整性 | 翻转密文末字节 → `InvalidTag` 正确抛出 ✅ |

**本机可用性**：`cryptography 50.0.1` ✅ / `lzma`、`bz2`、`gzip`、`zlib` ✅；缺 `zstandard` / `orjson` / `msgpack` / `pycryptodome` / `pynacl`。

### 9.4 npz 二次压缩零收益（已实测，别再试）

`plot_index_wu_ming_zhe.npz` = **74.2 MB**，是 `np.savez_compressed` 产物（全部成员 `compress_type=8`）。

再压 zlib-6/9 结果 **1.0002（+17 KB）**，耗时 1.8 s ⇒ **无效**。

要省只能换数据结构：`float32 → float16` / IVF-PQ / **不存 `ent_vectors`（42.6 MB）**。

### 9.5 一年体积测算

| 使用强度 | 原始 | **压缩后** |
|---|---|---|
| 个人自用 50 次/天 | 0.04~0.06 GB | **1.8~2.3 MB** |
| 日常 500 次/天 | 0.44~0.58 GB | **17.7~23.3 MB** |
| 高强度 5000 次/天 | 4.42~5.81 GB | **177~232 MB** |

⇒ **体积完全不是问题**，用户担心的「减少内存」在压缩后自然解决（且压缩带来的收益远大于加密）。

---

## 10. 轮转与归档（D19：明文 7 天 + 归档 90 天）

### 10.1 轮转规则

| 规则 | 值 |
|---|---|
| 单个明文文件上限 | **10 MB** |
| 或按天切分 | **1 天**，先到为准 |
| 文件名 | `logs/rag/trace-YYYYMMDD.jsonl` |
| 明文保留 | **7 天** |
| 压缩归档保留 | **90 天** |
| 归档路径 | `logs/rag/archive/YYYYMMDD.jsonl.lzma`（+ `.enc` 若开 L3） |
| 写入方式 | **写临时文件再原子 rename**（防半行） |

**体积参考**：单文件 10 MB ≈ 4000 条，压后约 **350 KB**。

### 10.2 归档脚本骨架

```python
# scripts/rag_log_archive.py
import lzma, os, re
from datetime import datetime, timedelta, timezone
from pathlib import Path

_SAFE_CID = re.compile(r"[^A-Za-z0-9_\u4e00-\u9fff-]+")

def safe_trace_path(base_dir: Path, character_id: str) -> Path:
    """安全版 trace_path（修 §4-① 的路径穿越）。"""
    cid = _SAFE_CID.sub("_", str(character_id or "")).strip("._") or "unknown"
    return base_dir / "_audit" / "retrieval_trace" / f"{cid}.jsonl"

def format_block_id(rank: int, doc_id: str, seq: int, text: str, paths: list[str]) -> str:
    """组合式块编号：doc_id#seq 定身份，h= 定内容。"""
    h = hashlib.sha1(text.encode("utf-8")).hexdigest()[:6]
    return f"B{rank:02d}[{doc_id}#{seq}|h={h}|{'+'.join(paths)}]"

def archive_day(day: datetime, src_dir: Path, dst_dir: Path, keep_days: int = 7) -> Path | None:
    src = src_dir / f"trace-{day:%Y%m%d}.jsonl"
    if not src.exists():
        return None
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / f"{day:%Y%m%d}.jsonl.lzma"
    tmp = dst.with_suffix(".tmp")
    raw = src.read_bytes()
    tmp.write_bytes(lzma.compress(raw, preset=6))          # 先压缩
    # 若开 L3：此处再 encrypt(tmp_bytes)                    # 后加密
    os.replace(tmp, dst)                                     # 原子 rename
    if (datetime.now(timezone.utc) - day).days > keep_days:
        src.unlink()
    return dst
```

### 10.3 密钥三方案

| 方案 | 做法 | 评价 |
|---|---|---|
| **A. 环境变量** | `ROLEPLAY_RAG_LOG_KEY`（base64，32 B） | ✅ **推荐起步**：零文件、零依赖 |
| B. 本机文件 | `~/.roleplay/rag.key`，权限 `0o600` | 需要一次生成步骤 |
| C. OS 密钥库 | Windows DPAPI / macOS Keychain | 需新依赖，**暂不引入** |

**纪律**：
- 密钥**不入库**（`.env` 已在 `.gitignore`）
- **加密是可选档**：开了会让 `grep` / 脚本分析失效，**与"便于分析"本质冲突** ⇒ 默认关，只在需要长期归档且含全文时才开

---

## 11. 测试影响面

全仓 1472 个 pytest 用例，grep 只命中 **2 个测试文件**。

**必须改的 3 个断言**（`tests/test_plotrag_trace.py`）：

| 行 | 断言 | 改法 |
|---|---|---|
| `:56` | `assert TRACE_SCHEMA == "retrieval-trace-v1"` | 改 `-v2` |
| `:152` | `assert back["trace_schema"] == TRACE_SCHEMA` | 跟随常量，无需改 |
| `:213` | `assert p.as_posix().endswith("data/knowledge/_audit/retrieval_trace/wu_ming_zhe.jsonl")` | **若改到 `logs/rag/` 需改这条** |

**附加注意**：

| 行 | 内容 | 风险 |
|---|---|---|
| `:140-144` | `assert "牙仙" not in json.dumps(...)` | **仅 L2 档会挂**（`ROLEPLAY_RAG_LOG_FULL=1` 时）。CI 不开 L2 ⇒ 安全 |
| `:122-127` | 桩 `_Chunk` 只有 `metadata={"paths": [...]}` | ⚠️ **新代码读 `doc_id`/`seq`/`hash` 必须用 `.get()`，否则 KeyError** |
| `:175-181` | `test_jsonl_write_failure_is_swallowed` | 落盘失败必须仍然吞掉 |

---

## 12. 验收标准

| # | 项 | 判据 |
|---|---|---|
| 1 | 三层都有 | 一条 trace 里 `candidates`（≤20）+ `fused`（6~8）+ `injected`（4~5 kept）**同时存在** |
| 2 | 块编号可追溯 | 任取一个 `block_id`，能从 `doc_id#seq` 定位到原文 |
| 3 | 默认不落原文 | L0 下 `grep -c "牙仙"` = 0 |
| 4 | 全文开关 | `ROLEPLAY_RAG_LOG_FULL=1` 后能查到原文 |
| 5 | `trace_id` 可 join | 同一轮的 question 与 answer 用同一 `trace_id` |
| 6 | 路径穿越已堵 | `character_id="../../x"` 不会写到目录外 |
| 7 | mention 归因正确 | `别名精确` 的 `kept_in_final ≤ hit_blocks` |
| 8 | 语义跳过原因正确 | 索引不可用时记 `index_missing`/`fingerprint_stale`，不是 `not_enabled` |
| 9 | `detail` 不再双层 | `trace["channels"][i]["detail"]` 里没有 `"detail"` 键 |
| 10 | 告警可读 | `logs/rag/alerts.log` 有内容时能看出是哪类问题 |
| 11 | 归档可用 | 跑一次 `archive_day()`，产出 `.lzma`，roundtrip 解压与原文逐字节相等 |
| 12 | 不影响主链路 | 埋点失败时检索结果完全不变（现有 4 个降级测试保持绿） |
| 13 | 3 个测试已改 | §11 的断言同步更新 |
| 14 | 体积不失控 | 1000 条 trace 压缩后 ≤ 100 KB |

---

## 13. 明确不做

| ❌ | 理由 |
|---|---|
| 第一期做日志查看 UI（D20） | 只给文件 + 脚本 |
| 只记第②层"融合后 8 块" | D11 已定三层全记 |
| 逐条压缩 | 压缩率 0.39 vs 批量 0.0354，**11 倍差** |
| 先加密再压缩 | 压缩率退化到 1.0 |
| 每条 trace 都派生密钥 | Scrypt 30.1 ms/次 ⇒ 1000 条要 30 秒 |
| 二次压缩 `.npz` | 实测 +17 KB，无效 |
| 把日志写进 `data/knowledge/_audit/` | 那里已 201 MB 且零清理策略；D19 已定 `logs/rag/` |
| 改 `ABLATION_SCHEMA` | 与 trace schema 独立，零收益 |
| 删 `CHANNEL_ORDER` 里的「扩展查询」 | 顺序不可调是契约；且它 364/364 未启用的事实本身是有价值的数据 |
| 用 `orjson` / `zstandard` 加速 | 未安装；现有 `json` + `lzma` 已够（单条 < 3 KB） |
