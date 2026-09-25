# Compendium GraphRAG —— 交接说明

> 交接时间：2026-09-21
> 交接对象：新会话的 agent（不共享本会话上下文，一切以本文档与磁盘产物为准）

---

## 0. 一句话现状

**独立图谱 RAG 已建成并跑通全链路，代码与测试完备；但抽取覆盖率只有 0%，图谱是上一轮的旧产物（2096 实体 / 5539 边），需要重新抽取才能更新。**

---

## 1. 用户要什么（原始诉求）

> 「用 https://github.com/VioletWilde/Reverse1999-Story-Compendium 这里面的数据独立的新建一个数据图谱 rag，与之前的独立，并只对这个新的库进行测试」

关键词：**独立**（与既有 plot_*/graph_* 体系完全隔离）、**只用 Compendium 数据**、**只测新库**。

后续追加：
- 「全用云端处理」→ 抽取走云端 LLM
- 「用之前那个数据图谱 rag 的 300 题测一下」→ 已测，见 §6
- 「补额度续跑抽取」→ 额度未恢复
- 「直接走你的，你直接抽」→ 期望 agent 自己抽取，不要推诿

---

## 2. 磁盘上有什么

### 2.1 新库代码（本次新建，未提交 git）

```
src/compendium_rag/            # 独立包，11 模块 ~2700 行，不 import roleplay.*
├── config.py                  # CMPRAG_ 配置命名空间
├── corpus.py                  # Compendium Markdown → 结构化语料（151 篇）
├── chunker.py                 # 按 scene 聚合分块 + 碎块合并
├── llm.py                     # 云端 LLM 客户端 + 容错 JSON 解析
├── extract.py                 # 抽取提示词 + 归一化 + 缓存（存 raw）
├── graph_store.py             # 图谱存储 + 实体归并 + 指纹
├── embedder.py                # 本地 Ollama bge-m3 嵌入
├── retriever.py               # 实体链接 + PPR + 三通道 RRF
├── pipeline.py                # 构建/重建/加载编排
└── cli.py                     # 命令行入口

tests/compendium_rag/          # 9 个测试文件，286 passed / 7 skipped
scripts/compendium_rag_*.py    # 运维与评测脚本（见 §5）
docs/COMPENDIUM_RAG.md         # 设计文档（架构/决策/评测/状态）
data/compendium_rag/           # 独占数据目录（与 data/knowledge 无关）
```

### 2.2 数据产物状态

| 文件 | 状态 | 说明 |
|---|---|---|
| `corpus.json` | ✅ 完好 19MB | 151 篇解析结果 |
| `chunks.json` | ✅ 完好 10MB | 3,695 块 |
| `graph.json` | ❌ **已被清空** | 当前 0 实体（详见 §8 事故） |
| `chunk_index.npz` | ✅ 完好 13MB | 3695 块向量 |
| `entity_index.npz` | ⚠️ 与旧 graph 配套 | 2094 实体向量，graph 重建后需一并重建 |
| `cache/` | ⚠️ 仅 3 块 | 抽取缓存（见 §4.3） |
| `reports/` | ✅ | build_report / eval_report / eval_300 等 |

**旧图谱的规模可从报告确认**（用于重建后对照）：

```
data/compendium_rag/reports/build_report.json
  graph.entities = 2094
  graph.edges    = 5538
  fingerprint    = 7dc29bf90681a3f7
```

⚠️ **`graph.json` 现在是空图**。检索会返回空结果——这是当前库「不可用」的直接原因。
补齐抽取后跑 `build` 即可恢复（届时规模应当 ≥ 旧值）。

🛡 **已加保护**：`pipeline.safe_save_graph()` 会拒绝用空图覆盖已有非空图谱，
`build` 与 `rebuild` 均已接入；配套测试
`test_safe_save_refuses_empty_overwrite`、`test_rebuild_does_not_clobber_graph_when_cache_empty`。

---

## 3. 独立性的可执行约束（用户最在意的一点）

`tests/compendium_rag/test_independence.py` 用 **AST 静态检查**守护：

- 不 import 任何 `roleplay.*`
- 不引用 `data/knowledge` / `data/lore` / `plot_*` / `graph_*` 等既有资产与配置
- 数据全部落 `data/compendium_rag/`
- 测试只在 `tests/compendium_rag/`

已验证既有系统不受影响：`pytest tests/ --ignore=tests/compendium_rag` = **987 passed / 1 failed**。
那 1 个失败在 `tests/test_llm_config.py`，属仓库中**预先存在**的未提交改动，与本库无关
（`git diff` 中对新包 0 处引用）。

⚠️ 注意：`git status` 里有一批 `M` 文件是**接手前就存在**的未提交改动，**不要动它们**。

---

## 4. 抽取这条路：现状与选择

### 4.1 云端网关已耗尽

`.env` 里的 `ROLEPLAY_LLM_BASE_URL=http://127.0.0.1:7863/v1`（进程 `wb2api`），
实测六个模型全部返回：

```json
{"code":14018,"msg":"额度已用尽，请访问以下链接，购买加量包以获取更多额度"}
```

充值入口：`https://www.codebuddy.cn/profile/usage`

**注意**：agent 自己的模型通道与这个网关**不是同一账号**，agent 能回话不代表网关有额度。

### 4.2 本机可用的三条路

| 方案 | 命令 | 覆盖 | 耗时 | 质量 |
|---|---|---|---|---|
| A. 等网关充值 | `python -m compendium_rag.cli build` | 全量 3695 块 | ~2h | 最好（cn:kimi-k2.6） |
| B. 本地 Ollama | 见下 | 全量 | 十几小时 | 中（CPU 推理 qwen2.5:7b） |
| C. agent 自己抽 | 见 §4.3 | 实际只能覆盖少量块 | 每块数分钟 | 高 |

**方案 B 的命令**（改配置即可，无需改代码）：

```powershell
$env:PYTHONPATH = "src"
$env:CMPRAG_LLM_BASE_URL = "http://localhost:11434/v1"
$env:CMPRAG_LLM_API_KEY  = "ollama"
$env:CMPRAG_LLM_MODEL    = "qwen2.5:7b"
python -m compendium_rag.cli build
```

### 4.3 方案 C：agent 自己抽（用户明确要求过）

已搭好脚手架 `scripts/compendium_rag_agent_extract.py`：

```bash
python scripts/compendium_rag_agent_extract.py status              # 查看进度
python scripts/compendium_rag_agent_extract.py pending --limit 10  # 取待抽块(JSON行)
python scripts/compendium_rag_agent_extract.py prompt <chunk_id>   # 看提示词
python scripts/compendium_rag_agent_extract.py submit <file.json>  # 落盘
```

`submit` 的 JSON 格式（key 来自 `pending` 输出）：

```json
{"<cache_key>": {"entities":[{"name":"","type":"","aliases":[],"desc":""}],
                 "relations":[{"src":"","relation":"","dst":"","evidence":"","confidence":0.9}]}}
```

**已抽 3 块**（`mainline__000_此即明日` 的 0.0.0 / 1.0.0 / 1.1.0），示例文件
`data/compendium_rag/_agent_batch01.json` 可作为格式参考。

**诚实评估**：这条路**跑不完全量**。3695 块，每块需读上千字原文 + 产出 JSON，
上下文会被反复填满，乐观估计几十块就会失败。
**建议定位**：用它补**关键篇章**（如主线 14 篇的核心块），让用户立刻看到真实图谱质量，
全量仍交给 A 或 B。

---

## 5. 脚本清单

| 脚本 | 用途 |
|---|---|
| `compendium_rag_quota.py` | **先跑这个**，探测网关配额是否恢复 |
| `compendium_rag_agent_extract.py` | 方案 C 的 pending/submit/status |
| `compendium_rag_test_resume.py` | 断点续跑验证（用假端点，已沙箱化） |
| `compendium_rag_eval.py` | 13 题自建评测（2 模式） |
| `compendium_rag_eval300.py` | 既有 300 题评测（分层口径） |
| `compendium_rag_testset_breakdown.py` | 拆解 300 题哪些可答 |
| `compendium_rag_audit.py` | 抽取质量全量审计 |
| `compendium_rag_alias_check.py` | 实体归并效果核对 |
| `compendium_rag_merge_probe.py` | 归并决策 + 证据溯源性核查 |

---

## 6. 评测结果（已有）

### 6.1 自建 13 题（缓存丢失前，覆盖 18.9% 时测得）

| 模式 | hit@k | MRR | seed_recall | grounded |
|---|---|---|---|---|
| full（三通道） | 1.000 | 0.878 | 0.885 | 1.000 |
| graph_only | 0.769 | 0.769 | 0.731 | 1.000 |

### 6.2 既有 300 题（`data/knowledge/_audit/rag_testset_300.json`）

**重要口径问题**：这 300 题是为**旧语料**（B站转写 + 灰机 wiki，含英文名）造的，
与纯中文 Compendium **存在语料错配**。

实测 **130/300（43.3%）** 题的标准答案关键词是**英文名**
（`Zanetta` / `Charlotte O'Hagan` / `Marcus`…），中文语料里根本不存在这些字符串
——任何中文 RAG 都答不出，**属语料边界而非算法失败**。其中仅 **8 题（2.7%）**
是真的内容未收录。

分层结果：

| 口径 | n | hit@k | MRR | seed_recall |
|---|---|---|---|---|
| all（含不可答） | 300 | 0.453 | 0.322 | 0.237 |
| answerable | 170 | 0.800 | 0.569 | 0.418 |
| **answerable + 中文关键词** | 159 | **0.811** | 0.578 | 0.428 |

按题型（可答口径）：factoid 0.827 / multi-hop 0.806 / reasoning 0.783 / temporal 0.500
按跳数：multi 0.841 / single 0.789（**多跳未劣于单跳**，PPR 有效）

**报数时必须说清口径**，否则 0.453 会被误读成检索差。

---

## 7. 已修的 8 个真实缺陷（都有回归测试）

1. **裸数组 JSON 被「第一个配平块」陷阱塌缩** — 13 实体静默变 1 个
2. **字符串内未转义 ASCII 引号致整段 JSON 解析失败** — kimi 13 实体 10 关系降级为 1/0
3. **单字符角色名被排除出实体链接** — `X`/`J`/`Z`/`37` 是真实角色（各 500-999 行）
4. **`重塑之手`（组织）被误并到 `重塑·信徒`（杂兵）** — `组织·成员` 构造被当成 `名·姓` 全名
5. **428 个碎块浪费云端调用** — 章节副标题单独成块
6. **全角 `？？？` 未被识别为泛称说话人**
7. **带序号的制作备注漏过滤** — `氛围图1-…`
8. **额度耗尽/网关不可达时空转重试** — 实测 40 块白等 42 秒、60 次无效调用；
   根因是 `httpx.ConnectError` 的 `str()` 返回**空串**，消息只在 `repr()` 里

---

## 8. ⚠️ 两次事故记录

### 8.1 抽取缓存被误删（698 块，云端已付费）

`scripts/compendium_rag_test_resume.py` 早期版本构造 `Settings` 时**忘了传 `data_dir`**，
于是落到真实 `data/compendium_rag/`，收尾的 `shutil.rmtree(cache_dir)`
**删掉了 698 块云端已付费的抽取缓存**。

- 后果：本来续跑只需重抽 2997 块，变成必须全量重抽 3695 块
- 已修：脚本强制写 `tempfile.mkdtemp()` + `REAL_DATA_DIR` 硬断言
- 防复发测试：`test_scripts_never_target_real_data_dir`、
  `test_cli_rebuild_does_not_delete_cache`

### 8.2 空图覆盖已有图谱（graph.json 被清空）

后续一次 `build` 在抽取缓存为空的情况下**仍走完了全流程**，
构图阶段以 0 实体覆盖了原先 2096 实体的 `graph.json`。
（该构建因额度耗尽提前结束，但「用空结果覆盖好产物」这一步没被拦住。）

- 已修：新增 `pipeline.safe_save_graph()` —— 新图为空而旧图非空时**拒绝写盘**
  并打印原因；`build` / `rebuild` 均已接入
- 防复发测试：`test_safe_save_refuses_empty_overwrite`、
  `test_safe_save_allows_when_no_existing`、
  `test_safe_save_allows_nonempty_overwrite`、
  `test_rebuild_does_not_clobber_graph_when_cache_empty`

**教训（给新会话）**：动手重建任何产物前**先备份**；
「跑失败」和「跑失败还覆盖掉好数据」是两回事，后者代价大得多。

---

## 9. 建议的下一步（按优先级）

1. **先跑 `python scripts/compendium_rag_quota.py`** 确认网关是否恢复
   - 恢复了 → `python -m compendium_rag.cli build`（约 2h，全量重抽 3692 块）
   - 未恢复 → 问用户选 B（本地 ollama）还是 C（agent 抽关键篇章）
2. 抽取完成后 `build` 会自动构图 + 建索引；
   重建后对照 `reports/build_report.json` 确认规模 ≥ 2094 实体 / 5538 边
3. 跑 `python scripts/compendium_rag_eval300.py` 看覆盖率提升后的真实召回
4. **补一份干净的中文金标准**：300 题与 Compendium 语料错配（§6.2），
   建议从语料随机抽块反向生成问题（100~300 题，无选择偏差），
   这样得到的召回率才对外可信

---

## 10. 与用户沟通的注意点

- 用户明确表达过不满：**不要拿「我没有端点」当不干活的借口**。
  能做多少做多少，把限制讲清楚，让用户选，而不是替用户决定不干。
- 报数字必须带口径。`hit@k=1.000` 是小样本自建题，别当总体召回率吹。
- 用户要的是**结果**，不是过程解释。少铺垫，直接给状态和选择。
