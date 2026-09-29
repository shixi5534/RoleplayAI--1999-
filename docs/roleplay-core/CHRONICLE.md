# 核心系统（角色扮演 / lore 向量层 / 架构 / 提示词） · 历史编年史

> 本文件由 **79 份历史过程档**合并而来（2026-09-29 整理）。
> 收录原则：已完成的一次性报告（审计 / 实验 / 验收 / 阶段总结）。
> **当前权威文档仍以独立文件形式保留**，见 `docs/README.md` 索引。
>
> 原文未丢失：删除前快照在 git 标签 `backup-pre-testdocs-cleanup`，
> 且每条下方记录了来源路径与 SHA-16，可用 `git show <tag>:<path>` 找回。

---

## 2026-08-13 · roleplay-ai 升级方案：从「写提示词」到「系统性工程」

- 来源：`docs/roleplay-core/architecture/UPGRADE_PLAN.md`
- SHA-16：`ee128bb2640d869d`

**要点**

- **目标**：让角色行为规则可程序化判定与注入，小模型也能稳定遵守。
- `match_condition(cond, context) -> bool`：子串/正则/情绪标签代码判定，**零 LLM 开销**
- **复杂度**：中 ｜ **风险**：低（可选字段 + 纯代码判定，无幻觉）
- **目标**：摘要持久化，跨请求复用，停止每轮重复烧 token。


## 2026-09-09 · roleplay-ai 版本库事故记录与首次提交报告

- 来源：`docs/roleplay-core/audit/git-repo-recovery-20260909.md`
- SHA-16：`3a24a2b7fb8c256c`

**要点**

- 结论：**与仓库、配置、git 版本无关**，是当前执行环境（沙箱）对


## — · 代码优化修复方案（审计确认 · 已应用）

- 来源：`docs/roleplay-core/audit/optimization-fix-plan.md`
- SHA-16：`9d7668af582ad9de`

**要点**

- 问题：结构化条目（`consolidate_entries`）的 importance 标度为 [0,1]（规则提取器 0.4/0.55、LLM 缺省 0.5、纠错下限 0.3），而整段合并（`consolidate`）标度为 [1,3]。阈值 0.6 会立即清掉全部结构化条目。
- 修复：`await fetch` 之后、改写 `modelSel` 之前复查 `providerSel.value === "ollama"`，不符则丢弃结果。
- 修复：`Promise.any` 并发探测（各自 800ms AbortController，`clearTimeout` 放 `finally`）；结果 TTL 缓存（如 5s），悬停读缓存、点击强制重探；复查定时器去重（记录 id，已存在不重复注册）。


## 2026-09-08 · RAG / GraphRAG 代码审计报告

- 来源：`docs/roleplay-core/audit/rag-graphrag-audit-20260908.md`
- SHA-16：`edae793fd65afb6c`

**要点**

- 而 `LongTermMemory.retrieve` 返回的是**原始余弦**（nomic 实测 0.5–0.75）。
- **同一个相对门** `0.85 × top1` → 只要 lore 命中够强，长期记忆必然落在门外。
- score=    49.383 via=plot_lexical      ← BM25 原始分（无上界）
- score=    46.100 via=plot_lexical


## 2026-09-01 · 角色提示词注入系统优化 · P0 阶段交付报告

- 来源：`docs/roleplay-core/prompt/roleplay-prompt-optimization-p0.md`
- SHA-16：`e414dfb54988bb1d`


## 2026-09-02 · 角色提示词注入系统优化 —— P1 阶段交付报告

- 来源：`docs/roleplay-core/prompt/roleplay-prompt-optimization-p1.md`
- SHA-16：`e609e6dfffcb8401`

**要点**

- 客服腔判定时先剥掉尾部标点/引号再 `endswith`，避免句号导致漏判。


## 2026-08-29 · roleplay-ai 角色扮演提示词优化报告（v2 · 基于实测）

- 来源：`docs/roleplay-core/prompt/roleplay-prompt-optimization.md`
- SHA-16：`42f71dfae30141ed`

**要点**

- **结论**：只在提示词里写「想说的多就分几条发」是空头支票，必须同步修渲染。
- 不要复述：开头不要重复对方刚说的话，结尾不要总结，不要写「总的来说」「希望这对你有帮助」这类收尾。
- ⚠️ **「分多条」与「主动提问」未达标**：3 次采样中「分多条」0/3、带问句 0–2/3。
- **覆盖范围 41/44**：覆盖了原库全部角色事实；丢弃 3 块纯元信息——第 0 块（整理说明）、第 35 块（来源 URL）、第 36 块（剧本转载头）。这三块不含任何角色事实，其中「使用说明：本资料按角色扮演还原需求进行结构化分类」这类文字会**提醒模型它正在读参考文档**，正是要消除的东西。

