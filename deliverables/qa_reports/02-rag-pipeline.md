# 02 — RAG 流水线 只读测试检验报告

- 工作目录：`C:\Users\Lenovo\WorkBuddy\2026-07-27-16-45-03\roleplay-ai`
- 解释器：`.\.venv\Scripts\python.exe`（Python 3.11 / numpy 2.5.1；**chromadb 未安装**）
- 模式：**只读**。未修改任何项目源文件；未 pip install；全程离线。
- 执行时间：pytest 原始输出全部重定向到日志文件，未读入分析上下文。
- 被测范围：`tests\test_rag.py`、`tests\test_rag_pipeline.py`、`tests\test_chroma_adapter.py`、`tests\test_rag_graphrag_audit.py`

> **环境限制（影响本次结论，务必先读）**
> 本会话的沙箱对 `<workspace>` 为只读，且**子进程无法在任意位置创建 pytest 所需的临时目录**。
> 因此 `tmp_path` fixture 在 21 个用例上 setup 阶段即失败（详见 §2 (e)）。
> 这 21 个 ERROR **不是代码缺陷**，而是测试宿主环境限制。原始日志写在会话临时目录
> （`%TEMP%\dsh-quXXw7\ralogs\`），因沙箱禁止子进程写工作区而无法落到本目录，见 §5。

---

## 1. 结果总表

| 文件 | 通过 | 失败 | 跳过 | 错误 | 耗时 (wall / pytest) | 结论 |
|---|---|---|---|---|---|---|
| `tests\test_rag.py` | 4 | 0 | 0 | 0 | 1.3s / 0.02s | ✅ 全绿 |
| `tests\test_rag_pipeline.py` | 11 | 0 | 0 | **9** | 1.2s / 0.09s | ⚠️ 代码全绿；9 个 `tmp_path` setup 错误（环境） |
| `tests\test_chroma_adapter.py` | 4 | 0 | 0 | 0 | 1.2s / 0.03s | ✅ 全绿（fake 后端，不依赖 chromadb） |
| `tests\test_rag_graphrag_audit.py` | 21 | 0 | 0 | **12** | 1.6s / 0.35s | ⚠️ 代码全绿；12 个 `tmp_path` setup 错误（环境） |
| **合计** | **40** | **0** | **0** | **21** | 5.3s / 0.49s | 收集 61，通过率 **40/61 = 65.6%** |

**执行到的用例（40 个）通过率 = 100%，真实失败 = 0。**
4 个被测文件**全部可收集**，无缺依赖导致的不可收集。

---

## 2. 失败明细

> 分类：(a) 真 bug / (b) 测试过期 / (c) 缺依赖 / (d) 需网络 / **(e) 环境-沙箱限制**（本节新增，因强行归入 (d)「需网络」会造成误导）。

### (e) 环境/沙箱限制 —— 21 个 ERROR，全部为 `tmp_path` fixture setup 失败

共同根因：**pytest 在 setup 阶段创建临时目录时被沙箱拒绝**，测试函数体从未执行。
`PermissionError: [WinError 5] 拒绝访问。: 'C:\Users\Lenovo\AppData\Local\Temp\dsh-quXXw7\pytest-of-Lenovo'`

已尝试并**全部失败**的规避手段（证明是宿主限制而非测试问题）：
`--basetemp=<可写目录>`、`PYTEST_DEBUG_TEMPROOT`（含预建目录）、预建 `pytest-of-<user>`。
同时验证：同一进程内 `pathlib.mkdir()` / `tempfile.mkdtemp()` / `shutil.rmtree()` / `os.chmod(0o700)` **均成功**，
唯独工作区外写被拒 → 属沙箱策略，非磁盘权限。

| # | node id | 归类 | 一句话根因 |
|---|---|---|---|
| 1 | `test_rag_pipeline.py::test_ingest_markdown_file_retrievable` | (e) | `tmp_path` 创建被沙箱拒绝 |
| 2 | `test_rag_pipeline.py::test_ingest_json_and_csv` | (e) | 同上 |
| 3 | `test_rag_pipeline.py::test_ingest_unsupported_format_raises` | (e) | 同上 |
| 4 | `test_rag_pipeline.py::test_ingest_sqlite_rows` | (e) | 同上 |
| 5 | `test_rag_pipeline.py::test_ingest_sqlite_rejects_non_select` | (e) | 同上 |
| 6 | `test_rag_pipeline.py::test_character_store_persists_tone_and_scope` | (e) | 同上 |
| 7 | `test_rag_pipeline.py::test_search_hybrid_flag_runs_without_error` | (e) | 同上 |
| 8 | `test_rag_pipeline.py::test_ingest_pdf_roundtrip` | (e) | 同上 |
| 9 | `test_rag_pipeline.py::test_ingest_docx_roundtrip` | (e) | 同上 |
| 10 | `test_rag_graphrag_audit.py::test_kb_persist_roundtrip_and_meta` | (e) | 同上 |
| 11 | `test_rag_graphrag_audit.py::test_kb_load_ignores_graph_and_corpus_json` | (e) | 同上 |
| 12 | `test_rag_graphrag_audit.py::test_graph_store_roundtrip_and_atomic_save` | (e) | 同上 |
| 13 | `test_rag_graphrag_audit.py::test_plot_retriever_ppr_prefers_seed_neighbourhood` | (e) | 同上 |
| 14 | `test_rag_graphrag_audit.py::test_plot_retriever_link_longest_match_and_word_boundary` | (e) | 同上 |
| 15 | `test_rag_graphrag_audit.py::test_plot_corpus_whitelist_rejects_manual_files` | (e) | 同上 |
| 16 | `test_rag_graphrag_audit.py::test_graph_build_is_idempotent_via_cache` | (e) | 同上 |
| 17 | `test_rag_graphrag_audit.py::test_plot_graph_chunk_survives_lexical_fallback` | (e) | 同上 |
| 18 | `test_rag_graphrag_audit.py::test_build_graph_from_chunks_drops_ambiguous_relations` | (e) | 同上 |
| 19 | `test_rag_graphrag_audit.py::test_plot_registry_cache_key_normalized` | (e) | 同上 |
| 20 | `test_rag_graphrag_audit.py::test_graph_searcher_links_and_resolves_evidence` | (e) | 同上 |
| 21 | `test_rag_graphrag_audit.py::test_graph_searcher_evidence_index_invalidates_on_kb_write` | (e) | 同上 |

关键报错（≤5 行，源自日志）：

```
..EEEEE......E...EEE                                                     [100%]
=================================== ERRORS ====================================
___________ ERROR at setup of test_ingest_markdown_file_retrievable ___________
E   PermissionError: [WinError 5] 拒绝访问。:
    'C:\\Users\\Lenovo\\AppData\\Local\\Temp\\dsh-quXXw7\\pytest-of-Lenovo'
```

**对上游的建议**：这些用例并非真的"没测到"，它们在具备可写临时目录的常规环境中应能正常执行。
本次检验**未能验证**这 21 条路径的实际行为——应视为**未覆盖**，而非通过。

### (a)/(b)/(c)/(d)

**无。** 0 个真 bug 被测试捕获（因为 0 个 FAILED，21 个 ERROR 全为宿主限制）。

---

## 3. 源码风险审查（只读）

### 3.1 ⭐ numpy 顶层 import 结论（重点核实项）

**结论：风险成立，且比预想更严重 —— 不是"optional 依赖缺失导致降级"，而是整个包 import 直接失败。**

证据链：
1. `pyproject.toml:24` — numpy **仅**声明在可选 extras `emotion = ["numpy>=1.26"]`，**不在** `dependencies`（第 10–18 行）中。
2. `pyproject.toml:20-25` — 可选 extras 只有 `rag`(chromadb)、`docs`、`voice`、**`emotion`**、`dev`。
   **不存在指向 `src/compendium_rag` 的任何 extra**；即"装 rag extra"**不会**带来 numpy。
3. `src/compendium_rag/retriever.py:21` — 顶层 `import numpy as np`（非延迟 import）。
4. `src/compendium_rag/__init__.py:12-13` — 包 `__init__` **无条件** `from .retriever import (...)`。
5. `src/compendium_rag/pipeline.py:25` — 同样无条件 `from .retriever import ...`。

**实测验证**（拦截 `sys.meta_path` 模拟 numpy 不存在）：

```
compendium_rag.retriever -> ImportError: No module named 'numpy' (simulated: emotion extra not installed)
compendium_rag           -> ImportError: No module named 'numpy' (simulated: emotion extra not installed)
```

即 `import compendium_rag` → **ImportError**。本机装 numpy 只是巧合（numpy 2.5.1 已在 venv），
说明当前 CI/部署若只按 `dependencies` + `rag` extra 安装，**GraphRAG 整条链路不可用且错误信息指向 numpy 而非缺失的 extra**，排查成本高。

numpy 的实际用途**仅** `retriever.py` 一个文件（27 处 `np.`），都是向量索引数学，**并非"情感"功能**——
把 numpy 挂在 `emotion` extra 下是**归类错误**。

### 3.2 逐条风险表

严重程度：🔴 高 / 🟠 中 / 🟡 低

| 文件:行号 | 问题 | 严重 | 建议 |
|---|---|---|---|
| `pyproject.toml:24` + `retriever.py:21` + `__init__.py:12` | numpy 仅属 `emotion` extra 却是 `compendium_rag` 的**硬依赖**；`import compendium_rag` 直接 ImportError（已验证） | 🔴 | 将 numpy 移入 `dependencies`，或为该包新增 extra 并在 `retriever.py` 内延迟 import + 抛可读错误 |
| `memory.py:59` | `metadatas[i]` **无边界检查**；`metadatas` 短于 `texts` 时 `IndexError`（已实测复现）。同项目 `chroma_store.py:59` 却有 `i < len(metadatas)` 守卫 → 实现不一致 | 🟠 | 照抄 chroma 的守卫：`metadatas[i] if metadatas and i < len(metadatas) else {}` |
| `memory.py:67,72-82` | `namespaces` 参数**被静默忽略**（`hybrid`/`hybrid_alpha`/`candidate_mult` 同样）。实测 `search("alpha", namespaces=["nsX"])` 仍返回 `namespace="ns1"` 的文档 → **跨命名空间串味**，且调用方无从察觉 | 🟠 | 至少按 `metadata["namespace"]` 过滤；不支持就显式 `raise NotImplementedError`，不要静默降级 |
| `base.py:17-37` vs `memory.py:57` vs `chroma_store.py:48-53` | ABC `add()` 无 `namespace` 参数，`ChromaVectorStore.add()` 却多出 `namespace="default"` → **LSP 违反**；经 `VectorStore` 抽象类型调用带 namespace 的实现时，换到 memory 实现即 `TypeError` | 🟠 | 把 `namespace` 提升进 ABC 签名并统一语义 |
| `factory.py:10-11` | 默认 `rag_impl="memory"` 返回忽略 namespaces 的实现，生产中"命名空间隔离"实为**静默失效** | 🟠 | 与上条同修；或在 factory 文档/启动校验中明确告警 |
| `chroma_store.py:44-46` | `PersistentClient` + `get_or_create_collection`（第 44、46 行）抛出的异常**不是 ImportError**，会**穿透** `factory.py:18` 的 `except ImportError`，以原始异常冒泡而非 `ConfigurationError`。第 45 行注释自承首次使用需**联网下载 ONNX all-MiniLM** | 🟠 | 在 `ChromaVectorStore.__init__` 内 try/except 转 `ConfigurationError`；或显式传入 embedding_function 避免隐式联网 |
| `chroma_store.py:151-156` | `clear_namespace` 吞掉所有异常仅 `logger.warning` → 删除失败返回成功，**调用方无法区分"没匹配"与"删除失败"** | 🟠 | 返回 bool/计数或抛出；至少把失败上抛 |
| `chroma_store.py:158-188` | `filter_remove` 同类静默失败：查询失败 `return 0`（第 167 行）、删除失败 `return 0`（第 187 行）、`predicate` 异常被吞并当作"不匹配"（第 178-179 行）→ **漏删且无感知** | 🟠 | 区分异常与 0 命中；`predicate` 异常应上抛 |
| `retriever.py:380` | `ent = self.graph.entities[eid]` 直接下标；若 `alias_index` 指向已不存在的实体（`graph.json` 不一致/手工编辑）→ `KeyError` 崩溃，无降级 | 🟠 | 用 `.get(eid)`，缺失则跳过并记 `res.note` |
| `retriever.py:21` | 顶层 import 可选依赖（见 3.1） | 🔴 | 见 3.1 |
| `retriever.py:531` | `ppr_map, _ = self.graph_channel(seeds)` 为取 `ppr_map` **重复跑一遍 PPR**——第 522 行已算过同一结果并丢弃。每次 `retrieve()` 双倍 PPR 开销 | 🟡 | 复用第 522 行的返回值：`g_chunks, edges = ...` 后从 `g_chunks`/内部缓存取 |
| `retriever.py:348-351` | `self._edge_chunks` 构建了却**从未被读取**（全仓仅此两处，见 grep）→ 死代码，白付 O(边数×块数) 建表与内存 | 🟡 | 删除，或补上使用它的逻辑 |
| `retriever.py:24` | `from .embedder import cosine` **从未使用** → 死 import，并顺带把 `httpx` 拉进依赖链 | 🟡 | 删除 |
| `retriever.py:176` | `RE_ASCII_WORD` 定义后**从未使用** | 🟡 | 删除 |
| `retriever.py:193-194` | `_name_matches` 在**循环内** `re.compile(...)`：`link()`（第 375-377 行）对**每个** alias 调用一次 → 每查询 N 次正则编译。别名集越大越慢 | 🟡→🟠 | 提到模块级 `functools.lru_cache` 按 name 缓存编译结果 |
| `retriever.py:191` | 每次调用都 `all(ord(c) < 128 for c in name)` 重扫名字 | 🟡 | 随上条一并缓存 |
| `retriever.py:247,269,276` | `personalized_pagerank` 的 `len(nodes)`/`max(score.values())` 在 `nodes` 为空时 `ZeroDivisionError`/`ValueError`。当前调用路径下 `seeds` 非空即 `nodes` 非空（故不可达），但该函数是**公开导出 API**（`__init__.py:13` 导出）且被测试直接调用 | 🟡 | 函数首行加 `if not nodes: return {}` 防御 |
| `retriever.py:98-99,147` | 空索引路径**已正确处理**：`matrix.size == 0` 提前返回 `[]`（实测 `ChunkIndex.build([],[]).search(...) -> []`，`size=0`）。`top_k=0` 亦安全（实测返回 `[]`） | ✅ | 无需改动（记录为已核实的安全路径） |
| `retriever.py:319-320` | `LexicalIndex.search` 空查询/空索引返回 `[]`，安全 | ✅ | 无需改动 |
| `memory.py:40-49,81` | `_cosine` 对**每个文档**重算 `na`/`nb`（文档范数恒定却每次查询重算），整体 O(查询数 × N × 词数) | 🟡 | `add()` 时预归一化文档 TF 向量（与 `retriever.ChunkIndex.build` 一致的做法） |
| `memory.py:81` | `scored.sort(key=lambda x: x.score, reverse=True)` **无次级键** → 同分排序依赖插入序，非确定性。项目内 `retriever.py:470,476` 已明确要求显式次级键 | 🟡 | 加 `(-score, text)` 次级键 |
| `embedder.py:71-76` | `except Exception`（裸捕获）重试 3 次：会把 `TypeError` 等**编程错误**当网络抖动重试；第 76 行 `return []` 不可达；`asyncio.gather`（第 78 行）无 `return_exceptions` → 单批失败使整轮丢失 | 🟡 | 收窄为 `httpx.HTTPError`；删不可达分支；考虑部分成功语义 |
| `embedder.py:48` | `assert self._client is not None` —— `python -O` 下断言被剥离，`__aenter__` 未调用时退化为 `AttributeError: 'NoneType'` | 🟡 | 改为显式 `if ... raise EmbedError(...)` |
| `embedder.py:84` | 进度日志条件 `done % (self.BATCH*16) < self.BATCH` 脆弱，批大小非偶数时会漏打/多打 | 🟡 | 用显式计数器 |
| `config.py:40` + `config.py:187` | `.env` 在 **import 时**读取一次并缓存；`get_settings()` 又 `lru_cache(maxsize=1)` → 进程内配置**不可刷新**，测试改环境变量/`.env` 后不生效 | 🟡→🟠 | 提供 `get_settings.cache_clear()` 的显式 reload 入口，或文档标注 |
| `config.py:43-48` | `_env` 的"空字符串视为未设置"（`v != ""`）会让**刻意设为空**的变量回退到 `.env`/默认值，语义含糊 | 🟡 | 明确 `None` 与 `""` 的区别并注释 |
| `chroma_store.py:77` | `from ..knowledge.vector_store import _BM25` —— 跨模块 import **私有下划线符号**，重构即碎 | 🟡 | 提升为公共 API 或抽取到共享模块 |
| `chroma_store.py:105` | `max(top_k * 4, top_k * candidate_mult)` 在 `candidate_mult=30` 时过度取候选（30×top_k）后才过滤，浪费检索 | 🟡 | 用 Chroma `where={"namespace": {"$in": ...}}` 下推过滤 |

### 3.3 O(n²) 专项

未发现**热路径上的真 O(n²)**。已核查：`build_adjacency`（线性）、`LexicalIndex.__init__`（线性）、
`rrf_fuse`（O(候选 log 候选)）、`lex_first` 重构（单层线性 + `seen` 集合）。
最接近的次优项是 **`retriever.py:531` 的重复 PPR**（常数因子 2×，非 n²）与
**`retriever.py:348-351` 的 `_edge_chunks`**（O(边×块) 建表却零使用），以及
**`retriever.py:193` 的循环内正则编译**（放大 `link()` 的常数因子）。均已在 §3.2 列出。

### 3.4 检索静默失败（吞异常）汇总

| 位置 | 吞异常方式 | 后果 |
|---|---|---|
| `chroma_store.py:155-156` | `except Exception` → `logger.warning` | `clear_namespace` 失败被当作成功 |
| `chroma_store.py:165-167` | `except Exception` → `return 0` | `filter_remove` 查询失败 = "0 条匹配" |
| `chroma_store.py:178-179` | `except Exception` → `matched = False` | `predicate` bug 被当作"不删除"，静默漏删 |
| `chroma_store.py:185-187` | `except Exception` → `return 0` | 删除失败 = "0 条删除" |
| `memory.py:67` | `namespaces` 参数被忽略（非 try/except 但同属静默） | 命名空间隔离失效无告警 |
| `embedder.py:71-76` | `except Exception` 重试后 `return []` 分支 | 异常被吞进重试；末次才抛 |

---

## 4. `data\` 健康度（只看不删）

### 4.1 一级目录清单与体量

| 一级目录 | 体量 | 文件数 |
|---|---|---|
| `data\knowledge` | **660.8 MB** | 68,155 |
| `data\compendium_rag` | **404.0 MB** | 4,123 |
| `data\voice` | 87.4 MB | 6 |
| `data\lore` | 27.9 MB | 1,413 |
| `data\eval_set_i` | 3.8 MB | 77 |
| `data\sessions` | 0.2 MB | 156 |
| `data\docs` | 0.1 MB | 2 |
| `data\characters` | 0.0 MB | 3 |
| `data\eval` | 0.0 MB | 2 |
| **合计** | **≈ 1.18 GB** | 73,937 |

无 `data\` 根层散落文件。`data\knowledge\_archive`（337.7 MB / 37,104 文件）与 `_audit`（117.9 MB）
占 knowledge 的 69%，是主要的可回收空间；`data\compendium_rag\reports` 单目录 182.0 MB。

### 4.2 空文件（8 个，均为 0 字节）

| 路径 | 判断 |
|---|---|
| `data\compendium_rag\_d313a.txt` | 临时调试残留 |
| `data\compendium_rag\reports\_85_ceiling_run.log` | **疑似失败运行的空日志** |
| `data\knowledge\_audit\_imp.err` | 临时诊断残留 |
| `data\knowledge\_audit\_imp_err8.txt` | 临时诊断残留 |
| `data\knowledge\_audit\_prf2.err` | 临时诊断残留 |
| `data\knowledge\_audit\_prf2.out` | 临时诊断残留 |
| `data\knowledge\_audit\_r.out` | 临时诊断残留 |
| `data\sessions\s.json` | ⚠️ **会话状态文件为空** —— 若为真实会话产物，说明曾写入中断；若为占位则无害。建议确认后处理 |

另有 `data\compendium_rag\graph.json.bak_empty`（0.00 MB）——文件名直白标注为空备份，**图谱曾有被清空的痕迹**，建议排查历史事故。

### 4.3 chroma 持久化目录

- `data\chroma` **不存在**；`data\chroma\chroma.sqlite3` **不存在**。
- 全仓 `chroma.sqlite3` 搜索结果：**0 个**。
- 结论：**Chroma 持久化从未初始化**。与事实一致——`pyproject.toml:21` 的 `rag` extra 未安装（`chromadb: False`），
  `src\roleplay\config.py:140` 默认 `rag_impl="memory"`。
- 因此 **"缺 chroma.sqlite3" 目前不构成缺陷**（无 chroma 数据目录 = 从未启用，而非损坏）。
  风险提示：一旦切到 `rag_impl="chroma"`，`ChromaVectorStore.__init__`（`chroma_store.py:44-46`）会新建库，
  且默认 embedding function 需**联网下载 ONNX 模型**（第 45 行注释自承），离线环境将失败——见 §3.2。

### 4.4 >50 MB 可疑大文件（6 个，全部位于 `data\knowledge`）

| 大小 | 路径 | 评估 |
|---|---|---|
| 75.1 MB | `data\knowledge\_archive\lore_wu_ming_zhe_before_L1b_20260916_2025.json` | 归档副本，可清理 |
| 75.1 MB | `data\knowledge\_archive\lore_wu_ming_zhe.json.pre_L1b_20260916_2027.bak` | 与上一条**同内容双份**，冗余 |
| 72.6 MB | `data\knowledge\_audit\_drift_embed_cache.npz` | 审计缓存，一次性产物 |
| 70.8 MB | `data\knowledge\plot_index_wu_ming_zhe.npz` | **活跃索引**，保留 |
| 69.7 MB | `data\knowledge\_archive\lore_en_asr_retired_20260916_2027.json` | 已退役档，可清理 |
| 57.6 MB | `data\knowledge\_archive\plot_index_before_b1_20260916_2004.npz` | 归档旧索引 |

> 判断：**无异常/可疑文件**。6 个都是可解释的归档(copy/bak)或向量索引，非损坏产物。
> 其中 4 个在 `_archive`/`_audit`（合计 205.4 MB）属**可回收**，但本次为只读检验，未做任何删除。
> `data\voice\source\` 另有 3 个 13–39 MB 的 mp4（未达 50 MB 阈值）。

---

## 5. 复现方式与日志位置

### 5.1 原始命令（严格重定向，输出不进入分析上下文）

```powershell
cd C:\Users\Lenovo\WorkBuddy\2026-07-27-16-45-03\roleplay-ai
.\.venv\Scripts\python.exe -m pytest tests\test_rag.py -q --tb=line -p no:cacheprovider *> <LOG>\test_rag.txt
# 其余三个文件同理
Get-Content <LOG>\test_rag.txt -Tail 25
Select-String -Path <LOG>\test_rag.txt -Pattern '^(FAILED|ERROR)'
```

### 5.2 日志实际落点

因沙箱禁止子进程写工作区（`<workspace>` 对子进程只读），日志写在会话临时目录：

```
C:\Users\Lenovo\AppData\Local\Temp\dsh-quXXw7\ralogs\
  test_rag.txt
  test_rag_pipeline.txt
  test_chroma_adapter.txt
  test_rag_graphrag_audit.txt
  _timing.txt
  pipeline_bt.txt / pipeline_bt2.txt / pipeline_bt3.txt / pipeline_tmproot.txt / pipeline_tmproot2.txt  ← 规避尝试的证据
```

> 临时目录随会话回收，**长期留存请把上述文件复制到 `deliverables\qa_reports\_logs\`**。
> 本次无法代为复制，原因同上（沙箱），非权限不足。

### 5.3 结果摘要（各文件日志尾部）

```
test_rag:                 4 passed, 1 warning in 0.02s
test_rag_pipeline:        11 passed, 1 warning, 9 errors in 0.09s
test_chroma_adapter:      4 passed, 1 warning in 0.03s
test_rag_graphrag_audit:  21 passed, 1 warning, 12 errors in 0.35s
```

---

## 6. 结论与优先级

1. **代码层面零失败**：40 个实际执行的用例 100% 通过；`(a) 真 bug = 0`。
2. **21 个 ERROR 全部是宿主沙箱导致 `tmp_path` 不可用**，应记为"本次未验证"，而非缺陷。
   在具备可写临时目录的标准环境重跑 `test_rag_pipeline.py` 与 `test_rag_graphrag_audit.py` 即可闭环。
3. **最严重问题（源码层）**：
   - 🔴 **numpy 依赖归属错误** —— `import compendium_rag` 在缺 numpy 时直接 ImportError（已实测）；
     numpy 只在 `emotion` extra 而用途纯属 `compendium_rag` → 按文档安装必然踩坑。
   - 🟠 **`InMemoryVectorStore` 静默忽略 `namespaces`**（已实测跨命名空间返回），
     而 `rag_impl="memory"` 是默认值 → 生产默认路径上的隔离语义静默失效；
     叠加 `ChromaVectorStore.add()` 违反 ABC 签名，两个实现行为不可互换。
4. **次要但应修**：`memory.py:59` 越界 IndexError（与 chroma 实现不一致）、
   `chroma_store.py` 四处吞异常导致静默漏删/失败、`retriever.py:531` 重复 PPR、
   `_edge_chunks`/`cosine`/`RE_ASCII_WORD` 死代码。
5. **`data\` 健康**：无异常大文件；8 个 0 字节文件多为调试残留，
   但 `data\sessions\s.json` 为空与 `graph.json.bak_empty` 值得人工确认。
   Chroma 目录缺失属"从未启用"，非损坏。

**未做**：任何源文件修改、任何删除、pip install、联网操作。本次未运行 `tests\compendium_rag\` 下其余测试（不在授权范围）。
