# Compendium GraphRAG —— 独立知识图谱检索库

> 基于 [VioletWilde/Reverse1999-Story-Compendium](https://github.com/VioletWilde/Reverse1999-Story-Compendium)
> 的《重返未来：1999》官方剧情档案，**从零新建**的数据图谱 RAG。
>
> **本库与既有的 `plot_*` / `graph_*` 体系完全独立**：不 import 任何 `roleplay.*`，
> 不读写 `data/knowledge`、`data/lore`，配置走 `CMPRAG_` 前缀，
> 数据落 `data/compendium_rag/`，测试落 `tests/compendium_rag/`。
> 独立性由 `tests/compendium_rag/test_independence.py` 以 AST 静态检查守护。

---

## 一、为什么另起一个库

既有系统的剧情 RAG（`plot_graph.py`，2270 行 + 约 70 个 `plot_*` 配置项）
是在**另一批语料**上长出来的：B 站视频转写 + 灰机 wiki 小径页。
Compendium 此前只是作为一层额外的 `canon_zh` 文档**挂靠**进去
（见 `scripts/compendium_canon_corpus.py`），两套数据混在同一张图与同一套
检索参数里，互相牵制、难以单独评估。

本库换一条路：**只为 Compendium 这一份语料建图**，用干净的数据模型
（结构化对话 → 实体关系图 → PPR 检索），独立配置、独立落盘、独立评测。
好处是整条链路可以端到端理解，参数有明确物理含义，评估结果不掺旧语料的水分。

## 二、数据源与语料

数据来自本地副本 `vendor/Reverse1999-Story-Compendium`（只读，1 GB）。
收录**简体中文**全部分类：

| 分类 | 篇数 | 行数 | 字数 |
|---|---|---|---|
| mainline 主线 | 14 | 31,571 | 658,497 |
| activity 活动 | 21 | 44,819 | 988,999 |
| character 角色剧情 | 17 | 14,930 | 328,656 |
| anecdote 轶事 | 25 | 17,833 | 379,223 |
| appendix_unbound 未绑定旁支 | 74 | 6,854 | 168,727 |
| **合计** | **151** | **116,007** | **2,524,102** |

语料形态（`tmp_probe/scan_format.py` 全量扫描确认）：

```
# 篇名
## Part 1 · 摇滚电台            ← H2 = Part
### 序章0-1 `script 100001`     ← H3 = 剧情单元（scene），尾部是内部 script ID
**维尔汀**：台词                ← 对话 80,446 行，全角冒号，说话人加粗
是雨声。                        ← 旁白 32,502 行
> 【标题卡】1966英国伦敦         ← 标题卡/引用 3,059 行
音效-掌声（热情的）              ← 制作备注（非正典，剔除 543+426 行）
```

对话带**显式说话人归属**，这一点对本库很关键：它让实体关系抽取有可靠锚点，
也是"泛称说话人过滤"能成立的前提。

### 清洗原则

- **确定性清洗，不改写一字台词**。正文是官方正典，任何模型润色都会破坏事实保真。
- 只剔除**有明确形态特征**的非剧情行：导航块、目录、锚点、制作/美术备注、
  演出转场标记（`渐黑`/`黑屏`/`浮窗道具收起`…）。
- 判据必须基于**行的形态**而非"是否含关键词"。实测有大量真旁白以这些词开头
  （`镜头聚焦到字上，字逐渐淡去…`），单纯关键词匹配会误删正文。
  详见 `corpus.is_production_note()` 的文档，以及
  `test_production_note_forms_detected` / `test_narration_with_keyword_kept`
  这一对**互相制衡**的测试。
- 保留一处有意识的例外：以 `镜头` 打头的运镜描述与真旁白形态不可区分，
  全语料仅约 5 行（<0.005%），**刻意保留**而不是冒险误删
  （`test_camera_direction_intentionally_kept` 锁住该决策）。

## 三、架构

```
┌──────────────── 离线构建（幂等，可断点续跑） ─────────────────┐
│  Compendium zh_CN (151 篇)                                    │
│      │ corpus.py    确定性解析 → 116,007 turns                │
│      ▼                                                        │
│  chunks.json    chunker.py  按 scene 聚合 → 3,695 块           │
│      │                         （碎块合并，保留说话人前缀）      │
│      ▼                                                        │
│  云端 LLM 抽取   extract.py  实体+关系+evidence                │
│      │            ├ 内容哈希缓存（存**原始输出**）              │
│      │            └ 归一化：受控词表 / 去噪 / 端点校验          │
│      ▼                                                        │
│  graph.json      graph_store.py  实体归一(union-find) + 边合并  │
│  chunk_index.npz / entity_index.npz   bge-m3 向量              │
└───────────────────────────────────────────────────────────────┘
┌──────────────── 在线检索（毫秒级，纯内存） ────────────────────┐
│  query                                                        │
│   ├─① 实体链接：别名精确匹配 + 词边界规则 + 向量兜底            │
│   ├─② PPR 展开激活：种子→边权迭代，多跳关联自然浮起            │
│   ├─③ 三通道召回：graph / mention / vector                     │
│   ├─④ RRF 融合 + 证据块回查原文                                │
│   └─⑤ 渲染：实体卡 + 关系脉络 + 原文证据                        │
└───────────────────────────────────────────────────────────────┘
```

### 关键设计决策

**1. 云端 LLM 抽取，本地嵌入**
云端网关（`127.0.0.1:7863`）实测**不提供** `/v1/embeddings`（404），
而本地 Ollama 有 `bge-m3`（1024 维，中文强）。因此：语言理解与关系抽取全部
走云端，向量（实体链接 + 语义兜底）走本地。分工由能力决定，不是偏好。

**2. 缓存存原始输出，归一化在读取时做**
早期版本把归一化后的结果直接落盘。结果是每调整一次去噪规则，
缓存里全是旧规则产物，必须整库重跑云端抽取——既昂贵又容易产生
"新旧规则混用"的脏数据。改为**存 raw、读时归一化**后，
迭代去噪规则是纯本地后处理，零云端成本（`ExtractionCache` 文档 + `NORMALIZER_VERSION`）。

**3. 边必须挂 evidence 与 chunk_ids**
图谱 RAG 的价值在于"关系可溯源"。每条边都带原文短句与来源块，
检索时证据块直接回查语料原文——这是不产生幻觉的底线，
也让抽取质量可以人工抽检。

**4. 身份指纹**
`graph.json` 头部记录 `{schema, 语料指纹, LLM 模型, 提示词版本, 分块参数}`
的哈希。任一要素变化即拒绝复用旧图谱（`fingerprint_of` / `check_fingerprint`），
避免图谱与语料漂移。

**5. 精确性优先的抽取提示词**
图谱用于精确检索，**错误的节点比缺失的节点危害大得多**。
实测 `hunyuan-2.0-instruct` 会把句子复述当"事件"实体
（`J收起博伊刀`、`幻象飘散而去`）、把描述性短语当角色
（`高个子`、`被捆绑住的女孩`），30 个实体里近半是噪声。
提示词 v3 加入"实体名必须是名字"的硬约束，并在归一化层设第二道防线
（`is_noise_name`），保证换任何模型建图，进图的都是名字而非短语。

## 四、快速开始

```bash
# 环境变量（可选，默认值见 config.py）
export CMPRAG_LLM_API_KEY=...          # 缺省回退 ROLEPLAY_LLM_API_KEY
export CMPRAG_LLM_MODEL=cn:kimi-k2.6

# 1) 解析语料（确定性，不联网）
python -m compendium_rag.cli corpus

# 2) 分块统计
python -m compendium_rag.cli chunks --write

# 3) 抽样预览（看提示词与块内容）
python -m compendium_rag.cli sample -n 3

# 4) 小批量抽取质量验证（8 块，约 1 分钟）
python -m compendium_rag.cli extract -n 8

# 5) 全量构建（云端抽取 + 构图 + 向量索引）—— 可随时中断、重跑续传
python -m compendium_rag.cli build

# 6) 只重建图谱（零云端调用；改了去噪/归并规则后用它）
python -m compendium_rag.cli rebuild

# 7) 图谱统计 / 实体邻域
python -m compendium_rag.cli stats
python -m compendium_rag.cli entity 维尔汀

# 8) 检索
python -m compendium_rag.cli query "星锑和重塑之手之间发生了什么冲突？"
python -m compendium_rag.cli query "维尔汀是谁" --json
```

### 构建是断点续跑的

``build`` 的抽取阶段每完成一块就落一次缓存。中断（网络、配额、手动 kill）后
重新执行 ``build``，已完成的块会**零成本跳过**，只补未完成的部分。
因此全量构建可以分多次、跨天完成，不必一次跑完。

### 关于云端配额

抽取走云端 LLM，受账号额度限制。额度耗尽时网关返回
``429 / 14018 额度已用尽``，此时 ``build`` 会记录失败块并在结束时给出统计
（成功/失败块数）。**已成功部分完全可用**，补足额度后重跑 ``build`` 即可续传。

## 五、测试

测试**只针对本库**，且默认全部离线（不联网、不依赖 Ollama）：

```bash
pytest tests/compendium_rag/ -q
```

覆盖面：

| 文件 | 用例数 | 覆盖内容 |
|---|---|---|
| `test_corpus.py` | 60 | 解析、说话人归属、备注剔除（含"不得误删正文"的反向断言） |
| `test_chunker.py` | 18 | 边界、重叠、确定性、碎块合并、内容不丢失 |
| `test_llm_parse.py` | 34 | JSON 容错解析（裸数组、内部引号、围栏、畸形修复） |
| `test_extract.py` | 40 | 词表映射、噪声剔除、端点合法性、缓存 raw 语义 |
| `test_graph_store.py` | 24 | 实体归一、边合并、溯源、指纹、落盘往返 |
| `test_retriever.py` | 32 | 实体链接、PPR、RRF 融合、向量索引、上下文渲染 |
| `test_pipeline.py` | 18 | 编排、指纹校验、缓存重建、加载、报告 |
| `test_independence.py` | 16 | **独立性契约**（AST 静态检查） |
| `test_online.py` | 7 | 真实云端/Ollama 集成（默认跳过） |

需要真实网络的用例用 `@pytest.mark.online` 标记，默认跳过：

```bash
pytest tests/compendium_rag/ -m online
```

**这套测试只覆盖本库**，与既有系统的测试互不影响：
`pytest tests/ --ignore=tests/compendium_rag`（旧系统）与
`pytest tests/compendium_rag`（本库）可以各自独立运行。

## 六、评测

```bash
python scripts/compendium_rag_eval.py 6
```

13 道人工核对的题目，覆盖单跳 / 多跳 / 跨篇章三类，跑两种模式：

- ``full`` —— 图 + 提及 + 向量三通道（生产配置）
- ``graph_only`` —— 关掉向量，**单独检验图谱本身是否有效**

指标：`hit@k` / `MRR` / `seed_recall` / `grounded`（证据是否真出自语料）。

另有三个诊断脚本：

```bash
python scripts/compendium_rag_audit.py        # 抽取质量全量审计（类型分布/噪声/长尾）
python scripts/compendium_rag_alias_check.py  # 实体归并效果核对
python scripts/compendium_rag_merge_probe.py  # 归并决策与证据溯源性核查
```

## 七、当前构建状态（2026-09-21）

全链路已跑通并产出可用库，但**云端账号额度在构建后期耗尽**，
且抽取缓存因一次误操作被清空，因此当前抽取覆盖为 **0/3,695**：

| 项 | 数值 |
|---|---|
| 语料 | 151 篇 / 115,823 行 / 2,521,139 字 |
| 分块 | **3,695 块**（全部完成） |
| 抽取缓存 | **0 块**（曾完成 698 块，因误删丢失，见下） |
| 图谱实体 | **2,096**（角色 654 / 物品 555 / 地点 423 / 概念 210 / 组织 146 / 事件 108） |
| 图谱边 | **5,539**（100% 带 evidence + chunk_ids） |
| 向量索引 | 3,695 块向量 + 2,094 实体向量（bge-m3 1024 维） |

> **⚠ 缓存丢失说明**：`scripts/compendium_rag_test_resume.py` 早期版本
> 构造 `Settings` 时忘了传 `data_dir`，于是落到真实数据目录，收尾的
> `rmtree(cache_dir)` 删掉了 698 块**云端已付费**的抽取缓存。
> 图谱/索引/corpus 未受影响（它们是另外落盘的）。
> 已修复并加了双重保险：脚本内 `REAL_DATA_DIR` 硬断言 +
> `test_scripts_never_target_real_data_dir` 静态检查。

**第一次构建（缓存丢失前）的评测结果**（13 题 / top_k=6）：

| 模式 | hit@k | MRR | seed_recall | grounded |
|---|---|---|---|---|
| `full`（三通道） | **1.000** | 0.878 | 0.885 | 1.000 |
| `graph_only`（纯图谱，仅 19% 覆盖） | 0.769 | 0.769 | 0.731 | 1.000 |

### 既有 300 题评测（`rag_testset_300.json`）

这套题是为**旧语料**（B站转写 + 灰机 wiki，含英文名）造的，与纯中文
Compendium 存在语料错配。实测 **130/300（43.3%）** 题的标准答案关键词
是英文名（`Zanetta`／`Charlotte O'Hagan`／`Marcus`…），中文语料里
根本不存在这些字符串——**任何中文 RAG 都答不出**，属语料边界而非算法失败。
其中仅 8 题（2.7%）是真的内容未收录。

因此分层报告（缓存丢失前、抽取覆盖 18.9% 时测得）：

| 口径 | n | hit@k | MRR | seed_recall |
|---|---|---|---|---|
| all（含不可答） | 300 | 0.453 | 0.322 | 0.237 |
| answerable | 170 | 0.800 | 0.569 | 0.418 |
| **answerable + 中文关键词** | 159 | **0.811** | 0.578 | 0.428 |

按题型（可答口径）：factoid 0.827 / multi-hop 0.806 / reasoning 0.783 /
temporal 0.500；按跳数：multi 0.841 / single 0.789（多跳未劣于单跳）。

复现：

```bash
python scripts/compendium_rag_quota.py            # 先查配额是否恢复
python scripts/compendium_rag_eval300.py          # 300 题评测（分层口径）
python scripts/compendium_rag_testset_breakdown.py # 拆解题目可答性
```

### 续跑方式（补足额度后，无需改代码）

```bash
python -m compendium_rag.cli build      # 已完成块自动跳过，只补未完成
```

由于缓存已清空，本次将是**全量重抽 3,695 块**（而非续传 2,997 块）。
按实测 ~0.5 块/秒、云端并发上限 9 估算，约需 2 小时。

## 八、目录结构

```
src/compendium_rag/          # 独立库（不 import roleplay.*）
├── config.py                # CMPRAG_ 配置命名空间
├── corpus.py                # Compendium Markdown → 结构化语料
├── chunker.py               # 按 scene 聚合分块 + 碎块合并
├── llm.py                   # 云端 LLM 客户端 + 容错 JSON 解析
├── extract.py               # 抽取提示词 + 归一化 + 原始输出缓存
├── graph_store.py           # 图谱存储 + 实体归一 + 指纹
├── embedder.py              # 本地 Ollama bge-m3 嵌入
├── retriever.py             # 实体链接 + PPR + 三通道 RRF
├── pipeline.py              # 构建/加载编排
└── cli.py                   # 命令行入口

data/compendium_rag/         # 独立数据目录（与 data/knowledge 无关）
├── corpus.json  chunks.json  graph.json
├── chunk_index.npz  entity_index.npz
├── cache/                   # 抽取缓存（存原始输出）
└── reports/                 # 构建与评测报告

tests/compendium_rag/        # 独立测试（不 import roleplay.*）
scripts/compendium_rag_eval.py
```
