# docs/ 索引

> 本仓库**并存三套 RAG/系统**（外加语音桌宠、QQ 两条线），历史上文档全部平铺在 `docs/` 根下。
> 2026-09-28 按**子系统**分类归档；2026-09-29 将**已完结的历史过程档**合并为各系统的
> `CHRONICLE.md` 编年史 —— 文档由 140 份精简到 **65 份**。
>
> 分类判据：`scripts/_cleanup_docs_plan.py`（决策表）/ `scripts/_docs_ref_analysis.py`（引用分析）
> 结构体检：`scripts/_docs_health.py`

---

## 为什么分这五类

三套系统**同源于《重返未来：1999》**，共享角色名与篇章名，靠内容词无法区分。
故用**结构性判据**（代码路径、产物名、指标口径、图规模）区分：

| 子系统 | 代码 / 产物 | 判别指纹 | 目录 |
|---|---|---|---|
| **compendium-rag**（正典图谱，**当前主线**） | `src/compendium_rag/`、`data/compendium_rag/` | 图 **7033/30269**、块 3695、盲测 206、指标 hit@6 | [`compendium-rag/`](compendium-rag/) |
| **plot-graph-rag**（剧情图谱，前身/并行） | `src/roleplay/core/knowledge/plot_*.py` | 图 **10406/7582**、块 9021、指标 inject_pass / strict_pass、灰机 | [`plot-graph-rag/`](plot-graph-rag/) |
| **roleplay-core**（架构 / lore 向量层 / 画像 / 提示词） | `src/roleplay/`、`data/knowledge/lore_*.json` | lore_wu_ming_zhe、VectorStore、persona_prompt | [`roleplay-core/`](roleplay-core/) |
| **voice-desktop**（语音与桌面宠物） | `src/roleplay/core/voice/`、`desktop/` | Live2D、TTS、pet-v0.3、口型 | [`voice-desktop/`](voice-desktop/) |
| **qq**（QQ 通道） | `src/roleplay/channels/` | QQ / OneBot / NapCat | [`qq/`](qq/) |

> ⚠️ **两条优化线不可混用指标**：`compendium-rag` 与 `plot-graph-rag` 是**不同系统、不同题集、不同口径**。
> 历史上外部审查曾用 plot 层短板解释 compendium 层指标，导致方向误判。

---

## 文档约定

每个子系统目录含：

| 文件 | 性质 |
|---|---|
| **`CHRONICLE.md`** | **历史编年史** —— 已完结的过程档（审计 / 实验 / 阶段总结）合并而成，按日期倒序索引，每条含来源路径与 SHA-16 |
| 其余 `.md` | **当前权威文档** —— 仍在生效的基线、规范、设计、交接、术语表 |

> **为什么这样分**：历史过程档数量多（79 份）且大多只被回溯查阅一次，
> 平铺会淹没真正在用的规范；但直接删除会丢失「当时为什么这么做」的依据。
> 合并为编年史既保留可查性，又让当前权威文档浮出来。
>
> **原文未丢失**：合并前快照在 git 标签 `backup-pre-testdocs-cleanup`，
> 可用 `git show backup-pre-testdocs-cleanup:<原路径>` 找回任意一份原文。

---

## compendium-rag/（当前主线）

| 子目录 | 内容 |
|---|---|
| [`baseline/`](compendium-rag/baseline/) | **BASELINE_v2…v8** 各版本冻结报告（当前 **v8**） |
| [`handover/`](compendium-rag/handover/) | 会话交接文档 |
| [`baseline-repairs/`](compendium-rag/baseline-repairs/) | R1–R5 图谱修复的作战书 / 预注册 / 核验报告 |
| [`ranking/`](compendium-rag/ranking/) | 排序侧实验与生产接入方案 |
| [`recall/`](compendium-rag/recall/) | 召回率路线、目标① 收口、盲测验收、**待决裁决记录** |
| [`extraction/`](compendium-rag/extraction/) | 正典入库、实体识别、题集 i 冻结 |
| [`CHRONICLE.md`](compendium-rag/CHRONICLE.md) | 历史编年史（20 条） |

**先读**：`baseline/BASELINE_v7_20260928.md` → `handover/交接_20260928_召回率85收口_RRF_k常数.md`
→ `recall/待决裁决记录_20260928.md`。

---

## plot-graph-rag/（前身/并行系统）

| 子目录 | 内容 |
|---|---|
| [`plan/`](plot-graph-rag/plan/) | 原 `PLAN/`：总计划、IDEAS_LOG |
| [`acceptance/`](plot-graph-rag/acceptance/) | 验收标准与验收报告、100 题评测 |
| [`audit/`](plot-graph-rag/audit/) | 架构审查、抽取质量审计、灰机事实核对 |
| [`corpus/`](plot-graph-rag/corpus/) | 语料清洗清单、**术语对照词表**、时间轴、别名裁决 |
| [`eval/`](plot-graph-rag/eval/) | 300 题评测、召回诊断、测试集文档 |
| [`graph-governance/`](plot-graph-rag/graph-governance/) | 灰机正典参考（关系治理报告已并入编年史） |
| [`CHRONICLE.md`](plot-graph-rag/CHRONICLE.md) | 历史编年史（49 条，含 summary/ 阶段计划与审计） |

> ⚠️ `plan/` 内文档原标注「**待办，除用户明确指定外不执行**」。

---

## roleplay-core/（核心系统）

| 子目录 | 内容 |
|---|---|
| [`architecture/`](roleplay-core/architecture/) | 系统架构、RAG 设计、GraphRAG 加强计划书、类图/时序图 |
| [`audit/`](roleplay-core/audit/) | RAG/GraphRAG 代码审计、知识库审查 |
| [`profile/`](roleplay-core/profile/) | 用户画像设计 + 类图/时序图 |
| [`prompt/`](roleplay-core/prompt/) | 角色扮演提示词优化 |
| [`CHRONICLE.md`](roleplay-core/CHRONICLE.md) | 历史编年史（7 条） |

---

## voice-desktop/（语音与桌面宠物）

| 子目录 | 内容 |
|---|---|
| [`pet-design/`](voice-desktop/pet-design/) | 桌宠设计 v0.2/v0.3（呈现规范、视觉风格板、实施方案、索引） |
| [`voice/`](voice-desktop/voice/) | 语音台词集、点击交互设计、情绪检测升级 |
| [`CHRONICLE.md`](voice-desktop/CHRONICLE.md) | 历史编年史（2 条） |

> ⚠️ **运行时依赖**：`src/roleplay/main.py` 通过 HTTP 端点 `/docs/DESKTOP_PET_DESIGN.md`
> 提供 `pet-design/DESKTOP_PET_DESIGN.md`，前端 `frontend/js/desktop-pet.js` 依赖该 URL。
> **URL 路径固定不动**，仅磁盘路径随分类调整；改动时两侧都要看。

---

## qq/

QQ 集成与语音回复方案（`CHRONICLE.md` 1 条）。

---

## 未纳入整理（有意保留原位）

| 路径 | 原因 |
|---|---|
| `data/compendium_rag/repairs_v*/**.md` | 带 **SHA-16 冻结锁**的证据链（`.gitattributes` 按路径声明），移动会打断回滚锚点 |
| `data/docs/*.md` | 生成器（`gen_rag_testset_300.py` 等）的**输出路径**，非手写文档 |
| `data/knowledge/_audit/*.json` | 评测旁挂（gold 缺陷登记表、题集等），非文档 |
| `deliverables/*.png`、`rag-eval-standard.json` | 图片与数据资产 |
