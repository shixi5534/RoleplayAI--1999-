# L4.5 r11 判分须知（盲评）

给每个块打 `coherence` 1~5 分：图谱里关于该块的角色关系陈述，是否与原文互洽。

- 5 = 全部关系陈述都有原文依据、对象与方向都对；
- 4 = 个别措辞偏差但不影响事实；
- 3 = 有一处对象错张或方向颠倒；
- 2 = 多处错，或关键关系无据；
- 1 = 基本与原文不符。

**不要参考任何历史评分**（10-08 面板与本批无关）。逐条独立判。

输出文件结构（与 10-08 件同 schema，便于聚合）：

```json
{"schema":"audit.l4_multiscene_review/v1","batch":"bNN","items":[{"chunk_id":"…","coherence":3,"n_edges":7,"n_mismatch":1,"mismatch":[{"src":"…","relation":"…","dst":"…","why":"…"}],"why":"一句话理由"}]}
```

必须覆盖本批**全部** chunk_id，一个不许漏；`n_edges` 照抄输入里该块的 edges 数。
