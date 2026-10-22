# docs/ 索引

> **给 AI / 新会话的第一份读物。** 全仓文档止于本索引 + 各子系统目录，根目录不放文档。
> 2026-10-21 整理：历史过程档（审计 / 实验 / 验收 / 阶段总结）已全部蒸馏进各子系统 `CHRONICLE.md`，
> 原文可 `git show <tag>:<path>` 找回，快照标签 `backup-pre-testdocs-cleanup`（2026-09-29）、
> `backup-pre-docsclean-20261021`（2026-10-21）。
>
> **规模**：50 份 / 1.18 MB / ≈33.6 万 tokens。**前 10 份就占掉一半**（见下表「token」列）——
> 别整目录 `cat`，按需取。

## 怎么用这份索引

1. **先定子系统**（三套系统同源于《重返未来：1999》，共享角色名，靠词面无法区分）。
2. 读该目录的 `CHRONICLE.md` 尾部（最近 3–5 条）—— 那里是「现在处于什么状态」。
3. 只有要改代码/改口径时，才打开权威文档（表格里标 ⭐ 的那几份）。
4. 查「某个数字为什么是这个值」→ `src/roleplay/config.py` 注释 + 对应 `CHRONICLE.md`。

## 子系统判别指纹

| 子系统 | 代码 / 产物 | 判别指纹（用这些区分，别用角色名） | 目录 |
|---|---|---|---|
| **compendium-rag**（正典图谱，**当前主线**） | `src/compendium_rag/`、`data/compendium_rag/` | 图 7033 实体 / 27110 边、块 3695、盲测 206、CBI / hit@6 | [`compendium-rag/`](compendium-rag/) |
| **plot-graph-rag**（剧情图谱，前身/并行） | `src/roleplay/core/knowledge/plot_*.py` | 图 10406/7582、块 9021、inject_pass / strict_pass、灰机 wiki | [`plot-graph-rag/`](plot-graph-rag/) |
| **roleplay-core**（主应用架构 / lore 向量层 / 画像 / 提示词） | `src/roleplay/`、`data/knowledge/lore_*.json` | `lore_wu_ming_zhe`、VectorStore、`persona_prompt` | [`roleplay-core/`](roleplay-core/) |
| **voice-desktop**（语音与桌宠） | `src/roleplay/core/voice/`、`frontend/js/pet-*.js`、`desktop/` | Live2D、TTS、pet-v0.3、口型 | [`voice-desktop/`](voice-desktop/) |
| **qq**（QQ 通道） | `src/roleplay/channels/` | OneBot v11 / NapCat / silk | [`qq/`](qq/) |
| **frontend**（前端改进计划线） | `frontend/` | `index.html`、开屏、多页、RAG 日志 ADR D01–D23 | [`frontend/`](frontend/) |

> ⚠️ **这两条线不可混用指标**：compendium-rag 与 plot-graph-rag 是不同系统、不同题集、不同口径。
> 历史上外部审查用 plot 层短板解释 compendium 层指标，直接导致方向误判。

## 全部 50 份，按子系统

### compendium-rag/（13 份）

| 文件 | 性质 | token |
|---|---|---|
| [`CHRONICLE.md`](compendium-rag/CHRONICLE.md) | **历史编年史 48 条**。每个阶段结论的唯一去处，先读 | 15.5K |
| [`P9_CBI报告.md`](compendium-rag/P9_CBI报告.md) | ⭐ CBI 评测权威报告。**被 `scripts/cbi_acceptance_audit.py:410` 读正文**（查 `0.84` 与 rate 字符串），改它会让 `X:基线实测` 判 FAIL | 42K |
| [`P10修复计划_CBI收口.md`](compendium-rag/P10修复计划_CBI收口.md) | ⭐ 「有条件发布」附带的强制修复计划。**`scripts/cbi_r11_matrix_check.py:35` 读全文** | 17.5K |
| [`优化计划_v9_2026-10-08.md`](compendium-rag/优化计划_v9_2026-10-08.md) | ⭐ v9 计划权威（P0–P7）；D1–D3 用户裁决在此。5 个 `compendium_rag_p*.py` 按行号引用 | 14.7K |
| [`architecture.md`](compendium-rag/architecture.md) | 系统架构与实测数据（§4 决策） | 8.4K |
| [`entity_disambiguation_rules.md`](compendium-rag/entity_disambiguation_rules.md) | ⭐ 实体消歧规则。`acceptance_audit.json` 断言其 size=22996 与 SHA-16 | 6.7K |
| [`检索四缺口修复计划_v10_2026-10-21.md`](compendium-rag/检索四缺口修复计划_v10_2026-10-21.md) | **已定稿、未实施**。四缺口 G1–G4（top_k 契约 / 向量阈值 / …） | 4.1K |
| [`research/四缺口外部设计对照_2026-10-21.md`](compendium-rag/research/四缺口外部设计对照_2026-10-21.md) | G1–G4 的同类框架做法与选型理由 | 3.5K |
| [`判分尺子_CBI统一rubric_v2.md`](compendium-rag/判分尺子_CBI统一rubric_v2.md) | ⭐ 现行判分尺子 v2（`cbi_rules_doc_facts.py:72` 断言两份都在库） | 1.4K |
| [`判分尺子_CBI统一rubric.md`](compendium-rag/判分尺子_CBI统一rubric.md) | 尺子 v1（仅作对照，勿删） | 0.9K |
| [`P10口径裁决_N_retrieval能力读数.md`](compendium-rag/P10口径裁决_N_retrieval能力读数.md) | ⭐ 路径被 `cbi_calculator.py:764` 与多份 report JSON 写死 | 2.1K |
| [`baseline/BASELINE_v7_20260928.md`](compendium-rag/baseline/BASELINE_v7_20260928.md) | v7 冻结基线（v4/v6 已并入 CHRONICLE） | 1.8K |
| [`handover/交接_20261010_v9优化_P8收口_下一步P9.md`](compendium-rag/handover/交接_20261010_v9优化_P8收口_下一步P9.md) | **现行交接**：锁死决策 D1–D5、图版本链与指纹、r11 记分卡读数、操作手册（本机踩过的坑）、P9 七项待办 | 9.9K |

### plot-graph-rag/（10 份）

| 文件 | 性质 | token |
|---|---|---|
| [`CHRONICLE.md`](plot-graph-rag/CHRONICLE.md) | **历史编年史 62 条**（含 summary/ 阶段计划与审计） | 12.9K |
| [`corpus/剧情术语对照词表.md`](plot-graph-rag/corpus/剧情术语对照词表.md) | ⭐ 中英名对照，**唯一被脚本当数据读的文档** | 4.8K |
| [`corpus/剧情时间轴与人物去向图.md`](plot-graph-rag/corpus/剧情时间轴与人物去向图.md) | 人物去向 | 5.7K |
| [`corpus/剧情时间轴与GraphRAG联动.md`](plot-graph-rag/corpus/剧情时间轴与GraphRAG联动.md) | 时间轴 ↔ 图谱联动 | 5.2K |
| [`corpus/剧情清洗注意事项.md`](plot-graph-rag/corpus/剧情清洗注意事项.md) | ⭐ 改 `plot_cache/`、`plot_graph_*.json` 前必读的格式约束 F1–Fn | 3.7K |
| [`corpus/剧情文件清洗清单.md`](plot-graph-rag/corpus/剧情文件清洗清单.md) | 问题类型编码 T1–T8 + 待清洗清单 | 3.3K |
| [`corpus/剧情别名与抽取裁决记录.md`](plot-graph-rag/corpus/剧情别名与抽取裁决记录.md) | 别名裁决留痕 | 2.0K |
| [`graph-governance/wiki-r1999-relation-reference-20260909.md`](plot-graph-rag/graph-governance/wiki-r1999-relation-reference-20260909.md) | ⭐ 灰机 wiki 关系权威设定，3 个脚本声明为数据来源 | 11.7K |
| [`acceptance/剧情图谱验收标准.md`](plot-graph-rag/acceptance/剧情图谱验收标准.md) | ⭐ 验收标准（`acceptance_plot_graph.py` 引用） | 1.4K |
| [`plan/README.md`](plot-graph-rag/plan/README.md) | 检索优化总计划。⚠️ 同目录文档**一律待办、不执行**（除用户明确指定） | 2.0K |

### roleplay-core/（9 份）

| 文件 | 性质 | token |
|---|---|---|
| [`CHRONICLE.md`](roleplay-core/CHRONICLE.md) | 历史编年史 10 条（含 RAG 审查、提示词优化、用户画像） | 3.4K |
| [`architecture/ARCHITECTURE.md`](roleplay-core/architecture/ARCHITECTURE.md) | ⭐ **看整体架构从这里进** | 6.3K |
| [`architecture/GRAPHRAG加强计划书.md`](roleplay-core/architecture/GRAPHRAG加强计划书.md) | ⭐ 详细实施版（模块/接口/算法规格/WBS），与 `graph_extract.py`、`graph_search.py` 呼应 | 11.8K |
| [`architecture/GRAPHRAG_ENHANCEMENT_PLAN.md`](roleplay-core/architecture/GRAPHRAG_ENHANCEMENT_PLAN.md) | 摘要版 + 落地状态（P0/P1 已接入，P2–P4 未开始） | 5.4K |
| [`architecture/RAG_SYSTEM_DESIGN.md`](roleplay-core/architecture/RAG_SYSTEM_DESIGN.md) | RAG 体系设计 | 4.8K |
| [`architecture/class-diagram.mermaid`](roleplay-core/architecture/class-diagram.mermaid) / [`sequence-diagram.mermaid`](roleplay-core/architecture/sequence-diagram.mermaid) | 架构图 | 0.4K / 0.4K |
| [`profile/profile-class-diagram.mermaid`](roleplay-core/profile/profile-class-diagram.mermaid) / [`profile-sequence-diagram.mermaid`](roleplay-core/profile/profile-sequence-diagram.mermaid) | 画像图（设计正文已并入 CHRONICLE） | 0.8K / 0.5K |

### voice-desktop/（4 份）

| 文件 | 性质 | token |
|---|---|---|
| [`CHRONICLE.md`](voice-desktop/CHRONICLE.md) | 历史编年史 7 条 | 5.6K |
| [`voice/调研-点击触发语音交互规范.md`](voice-desktop/voice/调研-点击触发语音交互规范.md) | ⭐ **语音交互参数的推导链**。`pet-voice.js:8`/`:48` 注释直接指向它；**代码尚未实现的三条**（GRACE 分层保护期、洗牌袋去重、`aria-disabled`）只在这里有规格 | 19.8K |
| [`voice/语音台词集使用说明.md`](voice-desktop/voice/语音台词集使用说明.md) | 台词集约定 | 2.0K |
| [`pet-design/DESKTOP_PET_DESIGN.md`](voice-desktop/pet-design/DESKTOP_PET_DESIGN.md) | ⭐ 桌宠 v0.2 架构。**URL 契约**：`main.py:177` 挂 `/docs/DESKTOP_PET_DESIGN.md`，`desktop-pet.js:140` 打开它 —— **磁盘路径可动，URL 不可动** | 7.4K |

### qq/（2 份）

| 文件 | 性质 | token |
|---|---|---|
| [`QQ语音回复方案.md`](qq/QQ语音回复方案.md) | OneBot v11 / NapCat 语音链路调研 + P0 已实施 / P1–P2 未做 | 5.0K |
| [`CHRONICLE.md`](qq/CHRONICLE.md) | 历史编年史 1 条 | 0.2K |

### frontend/（8 份）—— **分析完成 / 待开工**（D01：只出文档不写代码）

| 文件 | 性质 | token |
|---|---|---|
| [`README.md`](frontend/README.md) | ⭐ **总纲**：四条需求定稿、23 条 ADR（D01–D23）、P0–P7 阶段表、P0.5 五个既存 bug。**取代 `frontend-rebuild-plan.md` 的阶段划分，但不取代其技术决策与缺陷清单** | 3.9K |
| [`01-开屏动画.md`](frontend/01-开屏动画.md) | 官网开屏实测、时间轴、接线点 | 4.5K |
| [`02-舞台与浮现.md`](frontend/02-舞台与浮现.md) | 布局测绘、动作包络、浮窗卡片、鳞粉与丁达尔 | 8.6K |
| [`03-多页与极简.md`](frontend/03-多页与极简.md) | 39 个控件逐个处置、3 页结构、7 个 tab | 4.5K |
| [`04-RAG日志.md`](frontend/04-RAG日志.md) | trace schema v2、组合式块编号、三层漏斗、压缩归档 | 7.8K |
| [`05-3D与Blender路线.md`](frontend/05-3D与Blender路线.md) | **只记不做**：四条 3D 路径与决策门槛 | 1.8K |
| [`06-背景3D建模提示词.md`](frontend/06-背景3D建模提示词.md) | 可交给新会话的**自包含施工单**（坐标、深度分带、色彩纪律、量化验收） | 6.0K |
| [`99-实测数据索引.md`](frontend/99-实测数据索引.md) | ⭐ 上列每份里**每个数字的出处、复现命令与测量局限** | 7.8K |

### `docs/` 根（3 份）—— 前端重构计划系列，与 `frontend/` 并存不互替

| 文件 | 性质 | token |
|---|---|---|
| [`frontend-rebuild-plan.md`](frontend-rebuild-plan.md) | 重构计划 v1，状态**待拍板**（§9 有 7 个待定决策）。基线 `1c5966f` + tag `frontend-v3-baseline` | 9.2K |
| [`frontend-rebuild-plan-review.md`](frontend-rebuild-plan-review.md) | 对 v1 的**实测评审**（不采信计划里的数字，全部重跑）。结论：方向/结构/粒度对，3 处技术细节 + 3 个人日数错；总人日 15.5 → 18.8~27.3 | 15.0K |
| [`canvas-layer-design.md`](canvas-layer-design.md) | 透明画布互动层整合版技术计划 v1.0（调研+PRD+架构+对抗评审+两项 spike 完成，未改代码） | 8.5K |

## 不在 `docs/` 但属于文档体系（有意保留原位）

| 路径 | 原因 |
|---|---|
| `PROJECT_MAP.md`（仓库根） | 文件级索引：目录/源码/脚本/测试地图 + 常见任务入口速查 |
| `data/compendium_rag/repairs_v*/**.md` | 带 **SHA-16 冻结锁**的证据链（`.gitattributes` 按路径声明），移动会打断回滚锚点 |
| `data/docs/*.md` | 生成器输出（`gen_rag_testset_300.py` 等），非手写文档 |
| `deliverables/qa_reports/` | QA 交付报告，入口 `00-SUMMARY.md` |

## 维护纪律

- **新的一次性报告写完就蒸馏**：结论进对应 `CHRONICLE.md`（带日期、来源路径、SHA-16、要点），原文可删。
- **只有仍在生效的**（基线 / 规范 / 在途计划 / 被代码读的）才留独立文件。
- **删文档前先 `git grep --fixed-strings <文件名>`**：本仓有多处脚本真读文档正文（见上表 ⭐），
  也有把文档路径写死进 `data/**/report*.json` 的。
- 结构体检：`scripts/_docs_health.py`（含 `/docs/DESKTOP_PET_DESIGN.md` URL 契约守卫）。
