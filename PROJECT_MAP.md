# PROJECT_MAP · 项目文件索引

> 用途：**查找入口**。想知道「东西在哪 / 哪套是哪个版本 / 哪个文件能改哪个行为」时先看这张表，不要靠 `ls` 乱翻。
> 生成于 2026-10-21，基于工作区实测（非 git 历史推断）。改动结构后请顺手更新本文件。

---

## 0. 一句话定性

本项目有 **两套独立 RAG**，都在同一个仓库里，互不复用代码、互不影响数据：

| | 剧情 RAG（plot RAG） | 正典 RAG（compendium RAG） |
|---|---|---|
| 代码 | `src/roleplay/core/knowledge/plot_*.py` | `src/compendium_rag/` |
| 数据源 | B 站**英配 ASR 转写** + 灰机中文正典 | 别人开源的 `VioletWilde/Reverse1999-Story-Compendium`（中英双语剧情文本） |
| 语料语言 | **以英语为主**（9021 块里 7964 块英文） | 中英双语，按 vendor 来源入库 |
| 数据目录 | `data/knowledge/`、`data/lore/` | `data/compendium_rag/` |
| 文档 | `docs/plot-graph-rag/`、`docs/roleplay-core/` | `docs/compendium-rag/` |
| 状态 | 已 push 到 GitHub `origin/plotrag/M0` | **只在本地，未 push** |

**关键事实**：`origin/main` 只有 1 个 commit（`d1de5b8` 初始骨架），`origin/plotrag/M0` 只有 4 个 commit。本地 `plotrag/M0` 比远端**领先 143 个 commit**，compendium_rag / CBI 评测等全部在这 143 个未推送的 commit + 未提交改动里。

---

## 1. 顶层目录地图

排除 `.venv` / `.git` / `node_modules` / `.agent_tmp` 后：**104,819 个文件 / 8,280 MB**。

| 路径 | 文件数 | 体积 | 是什么 | 要不要动 |
|---|---|---|---|---|
| `src/` | 234 | 3.3 MB | **源码**（`roleplay/` 主应用 + `compendium_rag/` 独立 RAG 库） | ✅ 核心 |
| `tests/` | 123 | 3.8 MB | 测试，镜像 src 结构 | ✅ 核心 |
| `docs/` | 50 | 1.17 MB | **全部设计/审计/交接文档**（2026-10-21 清理后，见 §4） | ✅ 必读 |
| `scripts/` | 549 | 6.6 MB | 一次性脚本/评测台/修复工具（见 §5），多为历史产物 | ⚠️ 按名找 |
| `data/` | 76,556 | 1,376.7 MB | **全部数据产物**（见 §3） | ✅ 数据 |
| `vendor/` | 26,181 | 1,005.1 MB | 别人开源的剧情库 clone（见 §3） | 🔒 只读 |
| `models/` | 37 | **5,687.5 MB** | 本地 reranker 模型（见 §3） | 🔒 大，勿删 |
| `frontend/` | 310 | 44.9 MB | Web 前端（Live2D / 聊天页） | ✅ |
| `desktop/` | 8,367 | 561.4 MB | Electron 桌面宠物壳（其中 node_modules 478 MB） | ✅ |
| `deliverables/` | 62 | 1.2 MB | QA 报告、交付物（`qa_reports/00-SUMMARY.md` 是总入口） | 📄 读 |
| `logs/` | 76 | 0.4 MB | 运行日志 | 🗑 可清 |
| `_archive/` | 2 | 0.7 MB | 2026-10-21 归档的原始会话记录/调研草稿（tar.gz，解压可查） | 🔒 归档 |
| `.agent_tmp/` | 7,627 | **1,479.3 MB** | 临时垃圾（可整目录删） | 🗑 可删 |
| `scratch_r12/` | 5 | 71.6 MB | 临时草稿区 | 🗑 可删 |
| `.venv/` | 38,020 | 1,205.0 MB | Python 虚拟环境 | 🔒 勿动 |

---

## 2. 源码地图

### 2.1 `src/roleplay/` — 主应用（角色扮演 AI 本体）

| 路径 | 职责 |
|---|---|
| `main.py` / `config.py` / `middleware.py` | FastAPI 入口、配置（**所有魔法数字与阈值都在 `config.py`，含大量带实测数据的注释**）、安全中间件 |
| `api/` | HTTP 边界：`chat` `characters` `knowledge` `llm_config` `voice` `sessions` `desktop_pet` `ratelimit` |
| `channels/qq_onebot.py` | QQ 渠道（OneBot v11 / NapCat） |
| `core/orchestrator.py` | `ChatOrchestrator`：情感 → RAG → 角色卡 → LLM → 复读/出戏守卫 → 记忆 |
| `core/llm/` | LLM 适配：`base` `openai_like` `mock` `factory` `endpoint_guard` |
| `core/emotion/` | 情感识别与动作映射 |
| `core/rag/` | RAG 抽象层：`base` `factory` `memory` `chroma_store` |
| `core/voice/` | `stt` `tts` `clip_store` `voice_reply` |
| `core/knowledge/` | **知识层核心**，见下表 |
| `core/session_memory.py` | 会话记忆与摘要 |
| `models/` | 数据模型（`character` `chat` `prompt_config`） |
| `assets/characters/wu_ming_zhe.json` | 角色数据 |

**`core/knowledge/` 明细（剧情 RAG 的重心）：**

| 文件 | 职责 |
|---|---|
| `plot_corpus.py` | 剧情语料切块（781 行）。**语料隔离三重白名单**（目录/文件名 `^BV...`/头部「来源：B站」「机器提取」）；逐块判定 `zh/en/other` 写 meta |
| `plot_graph.py` | 剧情图谱抽取（1700+ 行）。**中英文两套抽取提示词**（中文约 :100，英文 prompt 在 `:106-112`，要求「实体名保留英文原文、relation 写中文谓语」）；别名裁决、实体挖掘 |
| `plot_semantic.py` | 跨语言语义检索通道。语料指纹校验（`schema/embedder/dim/corpus_sha` 四项）、**语言掩码**（`:54-58`，把候选池限成英文块） |
| `plot_rerank.py` | LLM 重排（`:42` 是重排提示词） |
| `plot_entity_expand.py` | 中文称谓 → 英文专名的桥 |
| `graph_store.py` / `graph_search.py` / `graph_ppr.py` | 图存储 / 图检索 / PPR 个性化传播 |
| `graph_extract.py` | 通用图抽取（`:134` 说明按语种切提示词） |
| `vector_store.py` | 向量 + 关键词存储。**分词规则：中文按字 bigram，英文/数字按词**（`:83-98`） |
| `retrieval_trace.py` | 检索链路追踪（调试 top-k 为何如此） |
| `embedder.py` / `factory.py` | 嵌入器适配与装配 |
| `ingest.py` / `document_ingest.py` / `extractors.py` / `event_extractor.py` | 入库与抽取 |
| `profile.py` / `profile_models.py` / `character_store.py` / `memory_tier.py` / `web_search.py` | 画像 / 角色存储 / 分层记忆 / 联网查询 |
| `relation_vocab.py` | 关系谓词词表（`:524` 是「英文字母或数字」过滤规则） |

### 2.2 `src/compendium_rag/` — 独立的正典 GraphRAG 库（41 文件，≈0.8 MB）

| 文件 | 职责 |
|---|---|
| `cli.py` | 命令行入口（入库/检索/评测的调度点） |
| `config.py` | 本库配置 |
| `corpus.py` | 读 `vendor/Reverse1999-Story-Compendium`，产出 `doc_id/script_id` |
| `chunker.py` | 切块（3695 chunk） |
| `extract.py` | 实体/关系抽取（20 KB） |
| `relation_vocab.py` / `relation_norm.py` / `relation_vocab.vendor.json` | 关系谓词归一（**中文谓语标准在这里**） |
| `graph_store.py` | 图存储 |
| `retriever.py` | 检索（32 KB，本库最大的一个文件：三通道 + RRF 融合） |
| `compose.py` | 上下文拼装 |
| `llm.py` / `embedder.py` | LLM 与嵌入适配 |
| `pipeline.py` | 流水线编排 |

> 注意：`src/compendium_rag/relation_vocab.py` 与 `src/roleplay/core/knowledge/relation_vocab.py` 是**两份独立副本**，改词表要两边一起改。

---

## 3. 数据地图（最大的磁盘占用）

| 路径 | 体积 | 内容 |
|---|---|---|
| `models/` | **5,687 MB** | `bge-reranker-base-onnx` (1,343 MB) / `bge-reranker-large` (2,157 MB) / `bge-reranker-v2-m3` (2,187 MB) |
| `vendor/Reverse1999-Story-Compendium/` | **1,005 MB** | 别人的剧情库 clone。结构：`readable/story_reader_linked/{en,cn}/{mainline,activity,anecdote,character,appendix_unbound}/...`（`.json` + `.md`）、`structured/`、`exports/`、`web-reader/` |
| `data/knowledge/` | **753.6 MB** | 剧情 RAG 数据，见下 |
| `data/compendium_rag/` | **503.6 MB** | 正典 RAG 数据，见下 |
| `data/lore/` | 27.9 MB | ASR 原始素材：`wu_ming_zhe/`（含 `视频文案/` 与 `canon_zh/`）、`_bilibili_tmp/`、`_huiji_cache/` |
| `data/eval_set_i/` | 3.8 MB | 人工标注评测集：`annotated.jsonl`、`adjudication.json`、`rejected.jsonl`、`manifest_*.json` |
| `data/voice/` | 87.4 MB | 语音素材 |
| `data/sessions/` | 0.2 MB | 会话存档（158 个 json） |

### 3.1 `data/knowledge/` 关键文件（剧情 RAG）

| 文件 | 大小 | 是什么 |
|---|---|---|
| `plot_index_wu_ming_zhe.npz` | 70.8 MB | **语义向量索引**（删掉 = 退回纯词法/图模式） |
| `graph_wu_ming_zhe.json` | 39.2 MB | 剧情图谱主文件 |
| `plot_corpus_wu_ming_zhe.json` | 20.6 MB | 切块后语料（无向量，换嵌入器不失效） |
| `plot_graph_wu_ming_zhe.json` | 9.7 MB | 图谱（带证据溯源） |
| `lore_wu_ming_zhe.json` | 7.0 MB | lore 向量库数据 |
| `docs.json` / `episodic.json` / `events.json` / `persona.json` | — | 文档 / 情节 / 事件 / 人设 |
| `_audit/` | 201 MB | 评测与审计产物（`plot_rag_eval_report*.json` 系列、`rag_testset_300*`） |
| `_archive/` | 337.7 MB | 历史快照（**可清**，37,104 文件） |
| `plot_cache*/` | — | 抽取缓存（多个 bak 备份目录） |

### 3.2 `data/compendium_rag/` 关键文件（正典 RAG）

| 文件 | 大小 | 是什么 |
|---|---|---|
| `entity_index.npz` | 25.6 MB | 实体向量索引 |
| `corpus.json` | 19.2 MB | 语料 |
| `chunk_index.npz` | 13.4 MB | 块向量索引 |
| `graph.json` | 11.0 MB | 图谱 |
| `chunks.json` | 10.5 MB | 块文本 |
| `entity_candidates_*.json` | — | 实体候选：`_i`（英文向）/ `_native` / `_300_cn`（中文向）三套 |
| `predicate_grouping_v1.json` / `relation_direction_v1.json` / `inverse_predicate_map.json` | — | 谓词分组、方向、逆谓词 |
| `repairs_v1...v12/` | — | 12 轮图修复产物 |
| `reports/` | — | 评测报告与日志（`cbi_*.json/md`、`_85_*.json` 等） |
| `er2/` `huiji_pages/` `cache/` `backups/` | — | 中间产物 |

---

## 4. 文档地图（`docs/`）

| 目录 | 内容 | 先读哪个 |
|---|---|---|
| `docs/README.md` | 文档总索引（**50 份 / 1.17 MB**，每份都标了 token 成本与「是否被代码读」） | ⭐ 从这里进 |
| `docs/roleplay-core/` | 主架构：`architecture/ARCHITECTURE.md`、`RAG_SYSTEM_DESIGN.md`、`GRAPHRAG加强计划书.md`、`GRAPHRAG_ENHANCEMENT_PLAN.md`、`profile/`（画像图）、`CHRONICLE.md`（历史档 10 条） | ⭐ `ARCHITECTURE.md` |
| `docs/plot-graph-rag/` | 剧情 RAG：`CHRONICLE.md`（历史档 62 条）、`corpus/`（术语对照/清洗约束/别名裁决/时间轴）、`graph-governance/`（灰机权威设定）、`acceptance/`、`plan/`（待办，不执行） | ⭐ `CHRONICLE.md` |
| `docs/compendium-rag/` | 正典 RAG：`CHRONICLE.md`（历史档 48 条）、`P9_CBI报告.md`、`P10修复计划_CBI收口.md`、`优化计划_v9_2026-10-08.md`、`architecture.md`、`entity_disambiguation_rules.md`、`判分尺子_CBI统一rubric_v2.md`、`检索四缺口修复计划_v10_2026-10-21.md`、`handover/`（现行交接） | ⭐ `CHRONICLE.md` |
| `docs/frontend/` | 前端设计与实测：`README.md`、`01-开屏动画` ~ `06-背景3D建模提示词`、`99-实测数据索引.md` | ⭐ `README.md` |
| `docs/voice-desktop/` | 语音与桌面宠物：`voice/调研-点击触发语音交互规范.md`（语音交互参数推导链，`pet-voice.js` 的实现依据）、`voice/语音台词集使用说明.md`、`pet-design/DESKTOP_PET_DESIGN.md`（v0.2 架构，经 `/docs/DESKTOP_PET_DESIGN.md` 供前端）、历史过程档全在 `CHRONICLE.md` | ⭐ `CHRONICLE.md` |
| `docs/qq/` | QQ 渠道方案 | — |
| `docs/frontend-rebuild-plan.md` / `-review.md` / `canvas-layer-design.md` | 前端重构计划 v1（含 7 个待拍板决策）与审阅 | — |

**计划书位置**：`GRAPHRAG加强计划书.md`、`GRAPHRAG_ENHANCEMENT_PLAN.md`、`RAG_SYSTEM_DESIGN.md` 均在 `docs/roleplay-core/architecture/` 下；根目录不再放文档（`ROLEPLAY_PROMPT_OPTIMIZATION_PLAN.md` 已蒸馏进 `docs/roleplay-core/CHRONICLE.md`）。

---

## 5. 脚本地图（`scripts/`，409 个 .py）

按前缀分组的命名约定，找脚本时直接按前缀搜：

| 前缀 | 数量 | 用途 |
|---|---|---|
| `compendium_*` | 59 | 正典 RAG 相关（入库、修复、审计） |
| `apply_*` | 47 | 把裁决结果应用到图/缓存 |
| `cbi_*` | 31 | CBI 盲判评测全链路 |
| `diag_*` | 15 | 诊断探针 |
| `ab_*` | 13 | A/B 实验 |
| `build_*` | 11 | 构建索引/语料 |
| `audit_*` | 11 | 审计 |
| `verify_*` | 10 | 验证 |
| `eval_*` | 9 | 评测台（`eval_plot_rag.py`、`eval_rag_standard.py`、`eval_rag_huiji.py`） |
| `huiji_*` | 8 | 灰机 wiki 抓取与正典入库 |
| `fix_*` | 5 | 数据修复 |
| `backfill_*` / `triage_*` / `ingest_*` / `fetch_*` | 各 2 | 补桥 / 分诊 / 入库 / 抓取 |

重要单点脚本：`scripts/migrate_rag_kb.py`、`scripts/verify_rag.py`、`scripts/triage_plot_rag.py`、`scripts/eval_plot_rag.py`。
`scripts/_archive/` 是废弃脚本区，`scripts/voice_pipeline/` 是语音流水线。

---

## 6. 测试地图（`tests/`，41 个 test_*.py + `tests/compendium_rag/` 13 个）

| 分组 | 文件 |
|---|---|
| 剧情 RAG | `test_plotrag_*.py`（m0_hardening / m0_verification / p0 / semantic / trace / eval_metrics / eval_m12 / huiji_canon / negative_guard / optimization / real_dialogue / retrieval_live）、`test_plot_graph.py`、`test_plot_timeline.py`、`test_rag_graphrag_audit.py` |
| 正典 RAG | `tests/compendium_rag/`：`test_pipeline.py` `test_retriever.py` `test_chunker.py` `test_corpus.py` `test_extract.py` `test_graph_store.py` `test_compose.py` `test_relation_norm.py` `test_llm_parse.py` `test_online.py` `test_independence.py` `test_p4_harness.py` |
| 主应用 | `test_orchestrator.py` `test_api.py` `test_knowledge.py` `test_rag*.py` `test_config.py` |
| 提示词 | `test_prompt_p0/p1/p2.py` |
| 语音/QQ/桌面 | `test_voice.py` `test_qq_onebot.py` `test_qq_voice.py` |
| 其他 | `test_character_*` `test_emotion.py` `test_mapping.py` `test_profile.py` `test_session_memory.py` `test_repetition_guard.py` `test_security.py` `test_llm_*` `test_qa_verification.py` |

---

## 7. 常见任务的入口速查

| 我想…… | 去哪 |
|---|---|
| 看整体架构 | `docs/roleplay-core/architecture/ARCHITECTURE.md` |
| 看剧情 RAG 怎么做的 | `docs/plot-graph-rag/CHRONICLE.md` → `src/roleplay/core/knowledge/plot_*.py` |
| 看正典 RAG 怎么做的 | `docs/compendium-rag/CHRONICLE.md` → `docs/compendium-rag/architecture.md` → `src/compendium_rag/` |
| 查某个阈值/参数为什么是这个值 | `src/roleplay/config.py`（注释里带实测数据）与 `docs/*/CHRONICLE.md` |
| 查评测分数/回归数据 | `data/knowledge/_audit/plot_rag_eval_report*.json`、`data/compendium_rag/reports/`、`deliverables/qa_reports/` |
| 查中文名 ↔ 英文名的实体对照 | `docs/plot-graph-rag/corpus/剧情术语对照词表.md`、`data/compendium_rag/entity_candidates_*.json` |
| 重跑评测 | `scripts/eval_plot_rag.py`（剧情）、`scripts/cbi_*`（CBI） |
| 查 QA 结论 | `deliverables/qa_reports/00-SUMMARY.md` |

---

## 8. 陷阱与注意事项

1. **两套 RAG 别混淆**：`roleplay/core/knowledge/` ≠ `compendium_rag/`。改一个不会影响另一个，测试也不互通。
2. **两份 `relation_vocab.py`**（见 §2.2 末），改词表要同步。
3. **`docs/` 内外有重复计划书**（根目录 vs `docs/**`），引用前确认版本。
4. **`data/knowledge/_archive/`（337 MB）与 `.agent_tmp/`（1,479 MB）可安全清理**，能省约 1.8 GB。
5. **`models/` 5.7 GB** 是本地 reranker，删了要重下，别当垃圾。
6. **GitHub 状态**：`origin/main` 与 `origin/plotrag/M0` 都**不含** `src/compendium_rag/`；本分支比远端领先 143 个 commit。
7. **`.venv` 里的包名不要当源码搜**：`npz` / `plot` 之类关键词会在 `.venv`、`vendor`、`node_modules` 里命中几十万次，搜索时先限定目录。
