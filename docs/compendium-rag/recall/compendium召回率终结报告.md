# Compendium GraphRAG 检索召回率 —— 终结报告

> 任务：**「用现成的中英映射表 + 设计文件，自行创建新题或用旧版 300 题，把召回率拉到 80% 以上；
> 执行前先把处理好的知识库 git 一次。」**
> 权威操作手册/交接文档仍是 `docs/compendium-rag/handover/COMPENDIUM_RAG_SESSION2_HANDOFF.md`（下称**交接文档**），
> 本报告只记录**这条召回率子任务**的结论、证据与回滚锚点。
> 生成日期：2026-09-25（第 22 会话，收尾 **#37**）。

---

## 1. 一句话结论

**主口径已达成：`full / answerable(196)` hit@6 = 0.796 → 0.801。**
得分**全部来自一次真实的数据修复**（剥除 17 个裸泛称 alias，消除实体链污染），
**未改检索代码、未改评测用例、未删任何真实内容**；`grounded` 在**每一套题、每一层、每一模式**上都是 **1.000**。
`all(300)` 与原生 250 题**没有**过 0.80，原因是**实测出来的**（算术天花板 + 排序缺口），不是数据缺口，
两条能过线的正路都超出本次红线授权，已原样交给使用者裁决（§6）。

---

## 2. 权威快照锚点（第 22 会话收尾 #37）

| 项 | 值 | 复核命令 |
|---|---|---|
| 回滚锚（修复前知识库） | commit **`c3193dc`** — #36 抽取产物（种子 + cache + graph，~54M） | `git show --stat c3193dc` |
| 本次修复 | commit **`7daf657`** — 145 文件（cache/batch/graph + 7 个新工具 + 5 份报告 + 2 套题集 + 交接文档） | `git show --stat 7daf657` |
| 图谱 | **7033 实体 / 29967 边**，孤立率 **0.1598**，指纹 `7dc29bf90681a3f7` | `python -m compendium_rag.cli stats` |
| 索引 | `chunk_index 3695 / entity_index 7033`（bge-m3 1024 维，仅本地 Ollama） | 同上（`fingerprint: OK — ok`） |
| 13 题底线 | 双模式 hit@k **1.0** / MRR 1.0 / grounded 1.0 / seed_recall 0.9615；**#37 在修复后图谱上原样复跑 → 逐位相同**（full 2.695s/题、graph_only 1.953s/题，by_kind 单跳/多跳/跨篇章全 1.0）；#36 快照另存 `reports/eval_report_36_snapshot.json` | `python scripts/compendium_rag_eval.py` |
| 工作树 | `git status --porcelain` = **0 行**（已全量入库，**未 push**） | `git status --porcelain` |
| 回归 | `pytest` **1281 passed / 8 skipped / 1 failed** | 唯一失败见 §8-③，与本项目无关 |

⚠ **实体数与边数在修复前后完全相同**（7033/29967）：剥的是 **alias**，不动节点与边。
所以两报告的差异可**逐题**归因，不必担心样本漂移。

---

## 3. 三套题集、三套口径 —— 严禁互排

| 题集 | n | 来源 | 定位 |
|---|---|---|---|
| `rag_testset_300.json` | 300 | 旧语料时代人工题（期望词含英文名） | 参照系：answerable(170) 已录 **0.824**（交接文档 §5.4） |
| `rag_testset_300_cn.json` | 300 | 上表经 `_build_testset_cn.py` 用 **4 张中英表（1218 键）+ 灰机缓存**把期望词补成中文 | **本任务主口径** |
| `rag_testset_native.json` | 250 | `_gen_native_qa.py` **直接从图谱 + 语料出题**（T1 事实题 / T2 线索题） | 最公正：只问「本库能不能答本库的事」 |

`rag_testset_300_clean.json`（仓库里另一份存量用例）的关键词与本语料**不对齐**，**未取用**。
hit 判定口径：任一期望关键词是返回块 `text + chapter_title + scene_title + part_title` 的子串。

---

## 4. 全部实测数字（`top_k=6`，双模式）

### 4.1 `rag_testset_300_cn.json`（300 题）

| 模式 | 口径 | n | 修复前 hit@6 | **修复后 hit@6** | 修复后 MRR | grounded |
|---|---|---|---|---|---|---|
| full | all | 300 | 0.523 | 0.527 | 0.405 | 1.000 |
| **full** | **answerable（主口径）** | **196** | 0.796 | **0.801 ✅** | 0.615 | 1.000 |
| **full** | answerable+cn_keyword | **184** | 0.799 | **0.804 ✅** | 0.618 | 1.000 |
| full | unanswerable | 104 | 0.010 | 0.010 | 0.010 | **1.000** |
| graph_only | all | 300 | 0.437 | 0.440 | 0.345 | 1.000 |
| graph_only | answerable | 196 | 0.663 | 0.668 | 0.522 | 1.000 |

### 4.2 `rag_testset_native.json`（250 题，全部可答，无分层）

| 模式 | n | 修复前 | **修复后** | 修复后 MRR | grounded |
|---|---|---|---|---|---|
| full | 250 | 0.628 | **0.632** | 0.426 | 1.000 |
| graph_only | 250 | 0.488 | 0.488 | 0.395 | 1.000 |

报告文件：`reports/eval_300_cn{,_after_welds}.json`、`reports/eval_native{,_after_welds}.json`。
（⚠ `reports/eval_300.json` 是脚本硬编码输出名，**每跑必覆盖**，永久留档必须 `cp` 走。）

---

## 5. 做了什么（只有这一件是数据改动）

**剥除 17 个裸泛称 alias ⇒ 消除实体链污染。**

- **病灶**（全库体检 `_audit_generic_alias.py`，扫描群体 7033 实体 / 29967 边 / 3695 块）：
  枢纽节点 `卡卡尼亚`（deg=**439**）的 alias 列表里挂着 **`女士`（语料 DF=911）** 与
  **`医生`（DF=228）**；另有 `船长`/`将军`/`祭司`/`护士`/`上校`/`少校`/`中尉`/`职员`/`老师`/
  `同志`/`蛇`/`社会活动家`/`盲眼医生`/`盲眼女士`/`荣军院的医生`。
  任何含这些词的查询都会被**实体链**吸进该枢纽的邻域，把真正的答案块挤出 top-6。
- **白名单是三条证据合成的**，不是拍脑袋：①`_audit_alias_decl_range.py` 实测该写法
  **`name 侧声明块数 = 0`**（全库 3676 个 cache 文件 / 31089 条实体声明的普查，非抽样）
  ⇒ 它只作为别人的 alias 存在，本语料从不拿它当独立实体名；②词本身是裸职务/裸称谓；
  ③宿主是高 deg 枢纽。
- **必须保留的两条**（`KEPT_MERGES`，体检后 A 类只剩这 2 条）：
  `维尔汀 ← 司辰`（DF=356，全库 **224 块**用 `司辰` 指她本人，**无任何块**把 `司辰` 当独立 name 声明 → 剥即抹除）、
  `科算中心 ← 拉普拉斯`（机构短名，同理）。
- **落盘**：`_fix_alias_welds.py --apply` → `rebuild`（零网络，**禁用 `build`**）→ `cli stats` 对齐 → 两套题复跑。
  实测输出：`strip 删泛称/数字 alias 94 条`｜`未登记违例 0`｜`resolve()` 复核 **17/17 泛称 → None、每个真名照旧可解析**、
  `卡卡尼亚 aliases` 21 → 15（deg 仍 439，**没有误删节点**）。
- **工具本身被加固**（这是本任务第二项产出，防后人重蹈）：
  ⚠ **strip 不幂等**。collapse 幂等（第二次 0 轮），但焊点归并后**成员写法只活在 alias 列表里**，
  对已剥产物再跑一次 = 交接文档 §4.11「成员名落盘即抹除」重演。
  现改为**证据自适应增量遍**：先复算 `canon_map()`，若已无残留归并即判定输入是本遍产物，
  只剥白名单泛称 + 数字 ID alias，其余 DROP_MAP 命中**跳过并登记**；
  `collapse=0 且 strip>0` 时守卫核对被剥写法是否**全部**在白名单内，**有白名单外写法则拒绝落盘**。
  守卫当场证明自己是对的：增量遍跳过了 2 个**无 name 落点的真名写法**（`传道者`、`淑女格蕾丝`），
  盲剥会正好抹掉它们。仓库里**不存在** `*_backup_pre_welds`（已搜索确认），所以重放旧备份这条路根本不可用，
  工具必须自我防护。

---

## 6. 为什么另两个口径没过 0.80（实测，不是推测）

### 6.1 算术天花板
`all(300)` 的上界是 **196/300 = 0.653**：104 题的期望关键词在这份纯中文官方语料里
**一次都没有出现过**（答名形如 `Zanetta` / `Charlotte O'Hagan` / `Marcus`）。这是**语料边界**，不是检索缺陷。
`unanswerable` 层 hit@6 = 0.010 而 `grounded` = **1.000** —— 对无答案的题**几乎不瞎答**，这是本库最重要的安全底线。
要用 `all` 冲 80%，唯一办法是删题或改用例，**红线禁止，故未做**。

### 6.2 剩余缺口是「排序」性质（宽窗 top-30 复算，`_diag_miss.py`）

| 题集 | answerable 未命中 | 排序缺口 | 召回缺口 | 别名可解释 |
|---|---|---|---|---|
| 300_cn | 40 | **31** | 9 | 0 |
| native 250 | 93 | **62** | 28 | 3 |

名次分布（`名次 ≤ k` 与 `hit@k` 同口径）：

| 题集 | 7–10 | 11–20 | 21–30 | >30 | 宽窗从未出现 |
|---|---|---|---|---|---|
| 300_cn | **14** | 8 | 5 | 4 | 9 |
| native | **17** | 20 | 9 | 16 | 31 |

⇒ 正确答案块**大多已经被捞到**，只是排在第 6 名以后。这不是命名/词形问题，alias 修复对它无效——
本项目自己就把这一点量化了：题面含被剥那 17 个词的，**300 题里只有 25 题、原生题里只有 5 题**，
即这一类修复在本测试集上的**理论上限就是 +2 题**。实际收了 3 题（含跨集）。

### 6.3 能过线的两条正路，都**超出授权**

| 路线 | 预期 | 为什么不擅自做 |
|---|---|---|
| **检索层**：候选融合 / 重排，把第 7–10 位的正确块抬进 top-6 | 量级见 6.2 表 | 红线原文：「**不改检索代码**……去迎合指标」 |
| **放宽 `top_k`** 6 → 10 | 投影 **0.867**（300_cn answerable）/ **0.696**（native） | ⚠ **这是投影不是实测**：名次取自修复前的 top-30 运行，evidence 池随 `top_k` 变化（图侧种子扩展与向量截断不同步）。对外报数前必须重跑 `--top-k 10`；且改 k 是**报数口径决定**，属使用者裁量 |
| （附加）**原生集即使 k=10 也不过线** | 31 题宽窗都捞不到 + 16 题排 30 名开外 | 说明 T2 线索题的**改述↔原文语义距离**是主因，只能靠检索层 |

### 6.4 主动放弃的做法（登记以免重犯）
关系逐字闸、DF 上限过滤、把期望词**扩成 alias 变体集**后再判 hit —— 三者都在**改评测口径**而非改数据，
且实测也填不上缺口（别名类缺口仅 0/3 题），**一律未采用**。

---

## 7. 被实测否证的两条「数据缺口」假设（省下后来的调查）

| 假设 | 检验 | 结果 |
|---|---|---|
| 冷门实体没抽全，所以查不到 | `_diag_df.py` 比命中组 / 未命中组的实体 DF | **方向相反**：未命中中位 DF = **88** > 命中 **32**。失手题**更**集中在枢纽（如 `维尔汀` DF=826），不是冷门实体 |
| 图谱关系词是抽取时虚构的，与语料对不上 | `_diag_rel.py` 查关系词是否逐字出现在源块 | **否**：仅 19/167 逐字出现，但各桶 hit 平坦（0.718 / 0.645 / 0.615 / 1.000）。⚠ 且首版正则只覆盖 T1 句式（原生集仅 6/250），该统计量**本就不足以解释全体未命中**，不可引用它下结论 |

---

## 8. 移交给下一手的三件事（都不是本任务能收口的）

1. **任务 #26：`卡卡尼亚 ↔ 德洛丝/兀尔德` 组块级拆分。**
   方向**已由灰机裁定**（`卡卡尼亚`=`Kakania` 有独立主页；`玛尔塔`/`别斯米尔`/`德洛斯医生` 灰机判为同人 = `兀尔德`=`Urd`），
   语料亦有自证句「我是德洛丝医生，而『兀尔德』的确是我的笔名」+「至于你提及的其他名字，应该并不是我」
   ⇒ **`卡卡尼亚` ≠ `德洛丝`/`兀尔德`（错误归并）**；
   但 `玛尔塔`/`别斯米尔` **灰机判是 vs 语料判非**，按「实在无法确定就单独列出」规则**已单独列出，暂不动**。
   **执行阻塞点**：这些写法全库 `name 侧块数 = 0`（只活在 alias 列表），拆分必须像
   `_fix_disciple_blocks.py` 那样**逐块改写 name**（约 205 块），不能靠 alias 增删。
2. **`_weld_adjudication.txt` 台账现状**：剥离 127｜保留 11｜待裁定 4｜已登记残留 3。
3. **`pytest` 唯一失败项** `tests/test_llm_config.py::…test_llm_override_embedded_in_chat_request`
   = **502 / 401 missing API key**（该测试真打外部 LLM 端点）。属环境缺凭据，**与 Compendium 数据/检索无关**，
   本项目全程零网关，未处理。

---

## 9. 产物索引（全部已入库）

**题集**（`data/knowledge/_audit/`）：`rag_testset_300_cn.json`、`rag_testset_300_cn_audit.txt`、`rag_testset_native.json`
**报告**（`data/compendium_rag/reports/`）：`eval_300_baseline_orig.json`、`eval_300_cn.json`、`eval_300_cn_after_welds.json`、`eval_native.json`、`eval_native_after_welds.json`
**新工具**（`data/compendium_rag/`）：
`_build_testset_cn.py`（中英表补全）、`_gen_native_qa.py`（原生出题）、
`_diag_miss.py`（排序/召回/别名三分类）、`_diag_df.py`（实体 DF 命中对照）、`_diag_rel.py`（关系词逐字核对，口径受限见 §7）、
`_audit_generic_alias.py`（**全库泛称 alias 体检**，A/B/C 三桶）、`_audit_alias_decl_range.py`（**strip 前安全闸**，必须打印扫描群体，群体为空即拒绝出结论）
**改动**：`_fix_alias_welds.py`（增量遍 + 拒绝落盘守卫 + 18 条新 `WELD_DROPS` + 2 条 `KEPT_MERGES` + `SAFE_NAMELESS_GENERIC`）、
`_weld_adjudication.txt`、cache/batch/graph（alias 级）
**交接文档更新**：§0（新增「召回率」行 + 第 22 会话标注）、**§5.5（全量口径与归因）**、§7 `0a)`（增量遍与不可重放告警）、§7 步骤 1（指纹口径纠正）、§8（产物 + 工具两表）、附录（第 21/22 会话行）

---

## 10. 复现命令（零网关；唯一网络目标是本地 Ollama 嵌入）

```powershell
$env:PYTHONPATH="src"; $env:PYTHONIOENCODING="utf-8"
$py=".\.venv\Scripts\python.exe"

# ① 体检：全库裸泛称 alias（A 类应只剩 司辰/拉普拉斯 两条必须保留的）
& $py data/compendium_rag/_audit_generic_alias.py
# ② 想再剥任何写法之前，先过安全闸：name 侧块数=0 即不可剥
& $py data/compendium_rag/_audit_alias_decl_range.py 女士 医生 司辰
# ③ 修复（对已剥产物会自动走增量遍）
& $py data/compendium_rag/_fix_alias_welds.py --apply
# ④ 重建图谱（禁用 build）+ 一致性核验
& $py -m compendium_rag.cli rebuild
& $py -m compendium_rag.cli stats        # 期望 chunks=3695 chunk_index=3695 entity_index=7033 / 指纹 OK
# ⑤ 两套题复跑（⚠ eval_300.json 每跑必覆盖，跑第二套前先 cp 走）
& $py scripts/compendium_rag_eval300.py --set data/knowledge/_audit/rag_testset_native.json
Copy-Item data/compendium_rag/reports/eval_300.json data/compendium_rag/reports/eval_native.json -Force
& $py scripts/compendium_rag_eval300.py --set data/knowledge/_audit/rag_testset_300_cn.json
Copy-Item data/compendium_rag/reports/eval_300.json data/compendium_rag/reports/eval_300_cn.json -Force
# ⑥ 未命中判别（只读）
& $py data/compendium_rag/_diag_miss.py data/knowledge/_audit/rag_testset_300_cn.json data/compendium_rag/reports/eval_300_cn.json
```

**铁律回顾**：禁网关（`http://127.0.0.1:7863`）、禁云端抽取；本地 Ollama bge-m3 **仅用于向量嵌入**；
构图只用 `rebuild`；**不改检索代码、不改评测用例、不删真实内容去迎合指标，修数据本身（改名/补别名）才是正解**；
**报数必须带口径**。
