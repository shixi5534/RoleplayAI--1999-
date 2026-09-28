# docs/ 索引 —— 按子系统分类

> 本仓库**并存三套 RAG/系统**，历史上文档全部平铺在 `docs/` 根下，难以分辨归属。
> 2026-09-28 已按**子系统**分类归档（`git mv`，历史保留），本页是导航入口。
>
> 分类判据见 `scripts/_docs_reorg_plan.py`；引用完整性体检见 `scripts/_docs_health.py`。

---

## 为什么分这五类

三个系统**同源于《重返未来：1999》**，共享角色名与篇章名，靠内容词无法区分。
故用**结构性判据**（代码路径、产物名、指标口径、图规模）区分：

| 子系统 | 代码 / 产物 | 判别指纹 | 目录 |
|---|---|---|---|
| **compendium-rag**（正典图谱，**当前主线**） | `src/compendium_rag/`、`data/compendium_rag/` | 图 **7033/30269**、块 3695、盲测 206、指标 hit@6 | [`compendium-rag/`](compendium-rag/) |
| **plot-graph-rag**（剧情图谱，前身/并行） | `src/roleplay/core/knowledge/plot_*.py`、`data/knowledge/plot_graph_*.json` | 图 **10406/7582**、块 9021、指标 inject_pass / strict_pass、灰机 | [`plot-graph-rag/`](plot-graph-rag/) |
| **roleplay-core**（核心系统：架构/lore 向量层/画像/提示词） | `src/roleplay/`、`data/knowledge/lore_*.json` | lore_wu_ming_zhe、VectorStore、persona_prompt、命名空间 | [`roleplay-core/`](roleplay-core/) |
| **voice-desktop**（语音与桌面宠物） | `src/roleplay/core/voice/`、`desktop/` | Live2D、TTS、pet-v0.3、口型 | [`voice-desktop/`](voice-desktop/) |
| **qq**（QQ 通道） | `src/roleplay/channels/` | QQ / OneBot / NapCat | [`qq/`](qq/) |

> ⚠️ **两条优化线不可混用指标**：`compendium-rag` 与 `plot-graph-rag` 是**不同系统、不同题集、不同口径**。
> 历史上外部审查曾用 plot 层短板解释 compendium 层指标，导致方向误判。

---

## compendium-rag/（当前主线）

| 子目录 | 内容 |
|---|---|
| [`baseline/`](compendium-rag/baseline/) | **BASELINE_v2…v7** 各版本冻结报告（当前 **v7**） |
| [`handover/`](compendium-rag/handover/) | 会话交接文档（`交接_*.md`、`COMPENDIUM_RAG*`） |
| [`baseline-repairs/`](compendium-rag/baseline-repairs/) | R1–R5 图谱修复的**作战书 / 预注册 / 核验报告** |
| [`ranking/`](compendium-rag/ranking/) | 排序侧实验（预注册 / 执行 / 后续资料）与生产接入方案 |
| [`recall/`](compendium-rag/recall/) | 召回率路线评估、终结报告、目标① 收口、盲测验收 |
| [`extraction/`](compendium-rag/extraction/) | 正典入库、强模型实体识别、补名路线、题集 i 冻结 |

**先读**：`baseline/BASELINE_v7_20260928.md`（当前基线）→ `handover/交接_20260928_召回率85收口_RRF_k常数.md`（最新交接）。

---

## plot-graph-rag/（前身/并行系统）

| 子目录 | 内容 |
|---|---|
| [`plan/`](plot-graph-rag/plan/) | 原 `PLAN/`：总计划、后端/前端计划、lore 层计划、现状报告、外部审查、IDEAS_LOG |
| [`acceptance/`](plot-graph-rag/acceptance/) | 验收标准与验收报告（数据层 / 服务层）、100 题评测 |
| [`audit/`](plot-graph-rag/audit/) | 架构审查、抽取质量审计、灰机事实核对、质量提升 |
| [`corpus/`](plot-graph-rag/corpus/) | 语料清洗、术语对照词表、时间轴联动、别名裁决 |
| [`eval/`](plot-graph-rag/eval/) | 300 题评测、召回诊断、T1–T19 专项实验、测试集文档 |
| [`graph-governance/`](plot-graph-rag/graph-governance/) | 关系命名治理、灰机正典反查、QA 报告 |
| [`summary/`](plot-graph-rag/summary/) | GraphRAG 总结 / 阶段审计与实施计划 |

> ⚠️ `PLAN/` 内文档原标注「**待办，除用户明确指定外不执行**」，该约定随目录一并保留。

---

## roleplay-core/（核心系统）

| 子目录 | 内容 |
|---|---|
| [`architecture/`](roleplay-core/architecture/) | 系统架构、RAG 设计、GraphRAG 加强计划书、类图/时序图、升级方案 |
| [`audit/`](roleplay-core/audit/) | RAG/GraphRAG 代码审计、知识库审查、仓库事故记录 |
| [`profile/`](roleplay-core/profile/) | 用户画像设计 + 类图/时序图 |
| [`prompt/`](roleplay-core/prompt/) | 角色扮演提示词优化（计划 + P0/P1 交付） |

---

## voice-desktop/（语音与桌面宠物）

| 子目录 | 内容 |
|---|---|
| [`pet-design/`](voice-desktop/pet-design/) | 桌宠设计 v0.2/v0.3（呈现规范、视觉风格板、实施方案、索引） |
| [`voice/`](voice-desktop/voice/) | 语音迭代报告、语音台词集、点击交互设计、情绪检测升级 |

> ⚠️ **运行时依赖**：`src/roleplay/main.py` 通过 HTTP 端点 `/docs/DESKTOP_PET_DESIGN.md`
> 提供 `pet-design/DESKTOP_PET_DESIGN.md`，前端 `frontend/js/desktop-pet.js` 依赖该 URL。
> **URL 路径固定不动**，仅磁盘路径随分类调整；改动时两侧都要看。

---

## qq/

QQ 集成与语音回复方案。

---

## 未纳入分类的目录（有意保留原位）

| 路径 | 原因 |
|---|---|
| `data/compendium_rag/repairs_v*/**.md` | 带 **SHA-16 冻结锁**的证据链（`.gitattributes` 按路径声明），移动会打断回滚锚点 |
| `data/docs/*.md` | 是生成器（`gen_rag_testset_300.py` 等）的**输出路径**，非手写文档 |
| `deliverables/*.png`、`deliverables/rag-eval-standard.json` | 图片与数据资产，非文档 |
