# compendium 补名路线（强模型实体识别）会话交接 — 2026-09-26（收尾 #38）

> **本文只管「强模型补名」这一条路线的接续。** 全局权威仍是 `docs/COMPENDIUM_RAG_SESSION2_HANDOFF.md`
> （铁律 §2、红线 §3、收尾流程 §7 一律适用，本文不重复也不覆盖）；
> 本路线的**结果权威**是 `docs/compendium强模型实体识别_执行报告.md`（下称「执行报告」），
> **方法权威**是 `docs/compendium强模型实体识别_计划书.md`（下称「计划书」）。三者冲突时：数据事实 > 执行报告 > 计划书。

## 0. 状态卡（全部为落盘产物实测值，非记忆）

| 项 | 值 | 出处 |
|---|---|---|
| 图谱 | **未改动**：实体 7033 / 边 29967 / 指纹 `7dc29bf90681a3f7` | `data/compendium_rag/graph.json` |
| 索引/cache | **未重建**（本轮只做离线识别 + 回放，铁律 5 未被触碰） | — |
| 检索水位 | 300_cn `full/answerable(196)` **0.8010**、MRR 0.6147；`unanswerable(104)` **0.0096**；native `full(250)` **0.6320**；`grounded` 三集 **1.000** | `reports/eval_{300_cn,native}_after_welds.json`（#37 权威基线） |
| 补名路线判定 | **不验收**：题集 i `T1 hit@10` strong−empty **+2.16pt、p=0.344**（预注册闸门 ≥+5pt 且 p<0.05） | `reports/eval5_set_i.json`、`reports/set_i_gates.md` |
| 阶段 4（接线） | **故意未做** —— `StaticMapIdentifier` 一行都没接进 `src/` | 执行报告 §5 结论行 |
| 逐题翻转 | native full up14/down25（净 **−11**）；300_cn full up1(R142)/down2(R022,R199)；题集 i up7/down3 | `reports/er_{native,300cn}_gates.md` |

**本轮唯一的"产出"是知识，不是分数**：负向结果 + 一条被证真的机理（§2）。

## 1. 起手三步（接手第一件事：先复算，别先读结论）

```powershell
$env:PYTHONPATH="src"; $env:PYTHONIOENCODING="utf-8"
$py=".\.venv\Scripts\python.exe"          # 裸 python 是 MS-Store 桩，必须全路径

# ① 一条命令复算本路线全部 18 条判据（离线、只读、零模型调用；退出码 0=全绿 / 1=有 FAIL / 2=有 PENDING）
& $py scripts/_er_audit_completion.py

# ② 复算两套题集的阶段 3 闸门（含零档逐位复现 + McNemar + 逐题题号）
& $py scripts/_er_report_gates.py --set native
& $py scripts/_er_report_gates.py --set 300_cn

# ③ 想改任何东西前先读：执行报告 §5 闸门表（每条都写了判据来源）
```

⚠ **只有判读侧可从仓库复算**。`_replay_entity_map.py` / `_iset_eval5.py` 需要**未入库**的
`data/compendium_rag/{chunk_index,entity_index}.npz` + `chunks.json/corpus.json` 与**本地 Ollama**（`127.0.0.1:11434`）；
换机要先按 SESSION2 交接 §7「标准收尾」重建索引，才能重跑 replay。四个 replay 与 eval5 产物已入库，正是为了让结论不依赖这次重建。

## 2. 为什么"不验收"却仍有价值（机理结论，下一轮的地基）

同一个 strong 映射、同一批题，只换喂法：

| 喂法 | 题集 i `T1 hit@10` | 相对 empty |
|---|---|---|
| `graph_only`（补名只进**符号通道**，不动 query 嵌入） | 0.7730 → **0.8703** | **+9.73pt** |
| `full`（把名字拼进 query **整体重嵌入**） | 0.9243 → 0.9459 | +2.16pt（p=0.344，不显著） |

⇒ **补名内容是真有效的**（strong−random **+5.41pt、p=0.021**，五臂里 strong 两模式全指标居首），
**被冲掉的原因是 full 模式的重嵌入**，不是识别质量。所以：
- ✅ 正路：**把补名只送 symbol / 实体链接通道，query 嵌入保持原样**，再重跑五臂；
- ❌ 死路：加大补名规模、放宽弃答阈值、或"多认几个名字" —— 那点收益在 full 模式下会被同样的方式吞掉。
  native（−4.40pt）与 300_cn（−0.51pt）都是这条规律的体现：**题面已点名实体时补名是纯冗余**。

## 3. 本路线的三条红线（违反即本轮结论作废）

1. **零网关**。识别 = agent 亲自读「题面 + 候选名表」手写记录；唯一允许的模型端点是本地 Ollama bge-m3 的**嵌入**（计划书 §1.2 的治理冲突已由用户 2026-09-25 裁决消解）。
   审计判据 A 会扫 6 个路线脚本的源码，命中 `requests/httpx/urllib/openai/socket/api_key` 即 FAIL。
2. **识别必须真盲**。只见 `qid ⇥ query ⇥ 候选名表`，**不得**看 gold / `relation::` / 边 / 度数。
   ⚠ **盲性只能靠扫"最原始记录"来保证**：合并脚本（`_er_merge_map.py` / `_iset_merge_map.py`）按 TSV 契约只读第 2 列，
   第 3 列起的自述批注会被**静默丢弃** —— 本轮就是靠这个扫描抓到 native `er2/picks_raw.tsv` 里 2 行
   `# seen_gold(截断诊断时见过)`（N038/N055）。去盲重算后 native 更差（−4.40 → **−5.24pt**），
   300_cn 与题集 i 原始记录 **0 批注 / 0 额外字段**。发现非盲行的处置规范：**披露 + 发布"剔除这些题后"的对照重算**，不得静默删行。
3. **报数必须说分母**（本轮自己踩了三次）：
   - `cov_seeded` **不是**"有 seed 的题占比"，而是"**在 seeded 题里** gold 落进候选表的比率"（300_cn：272/300 有 seed，`cov_seeded` 却只有 0.2353）；
   - "覆盖 X 题"**不是**可达上限：300_cn 覆盖 60/196（份额 30.61pt），但其中基线**未命中只有 5 题** ⇒ 真实可达上限 **+2.55pt**。
     任何小 Δ 都要对着这个上限解释，否则会把"空间本来只有 2.5pt"误读成"方法被大规模证伪"；
   - native `overall cov_seeded=0.8744` 是**三池合算**（闸门口径只看 T1/T1r，均 =1.000）；题集 i 的 `0.9676` 是**结构可达**，不等于 native 的 100%。

## 4. 产物地图（谁是什么的证据）

| 类别 | 路径 | 说明 |
|---|---|---|
| 文档 | `docs/compendium强模型实体识别_{计划书,执行报告}.md`、`docs/题集i_预注册与冻结记录.md` | 方法 / 结果 / 预注册三件套 |
| 脚本 | `scripts/_gen_entity_candidates.py`（阶段1）、`_gen_identify_batches.py`、`_er_merge_map.py`（阶段2）、`_replay_entity_map.py` + `_er_report_gates.py`（阶段3）、`_er_audit_completion.py`（18 判据）、`_iset_{prepare_material,annotate,freeze,make_id_view,merge_map,eval5,report_gates}.py`（题集 i 全链） | 共 13 个，全部零网关 |
| 候选表 | `data/compendium_rag/entity_candidates_{native,300_cn,i}.json` + `_stats_*` | 阶段1 产物，CAP=400 |
| 映射 | `data/compendium_rag/entity_map_{native,300_cn,i}.json` | 阶段2 产物；`eid = canon`（实体 id 就是正典名，见 `src/compendium_rag/graph_store.py`） |
| 原始识别记录 | `data/compendium_rag/er2/picks_raw.tsv`、`er2/300_cn/picks_raw.tsv`、`data/eval_set_i/id_out/batch_*.out.jsonl` | **盲性审计的唯一可信输入** |
| 回放/评测 | `reports/replay_{native,300cn}_{zero,map}.json`、`reports/eval5_set_i.json` | 阶段3 产物 |
| 闸门报告 | `reports/er_{native,300cn}_gates.md`、`set_i_gates.md`、`er_completion_audit.md` | 最后一份就是 §1 命令①的落盘 |
| 冻结题集 | `data/knowledge/_audit/rag_testset_i.json`（287 题，SHA256 `035bf4e17acae5c2…`，L1 指纹 `6a020d07ba27ff8d`） | **只读**；改动 = 全部对照实验失效 |

入库提交：`3759f61`（文档+脚本）、`0ce2b14`（`-f` 证据 + 冻结题集，88 文件）、`c593d9e`（终判入档 + SESSION2 登记 #38）。
**故意未入库**：`data/eval_set_i/{material,drafts,id_batches}` ≈3.6MB 写手材料（可由脚本 + `graph.json` 确定性重建）。

## 5. 待用户裁决的下一步（按性价比排序，都要授权才动）

1. **符号通道实验**（推荐先做）：补名只走 symbol/实体链接、保留原 query 嵌入 → 重跑题集 i 五臂。
   成本：`_iset_eval5.py` 一轮（要占本地 Ollama，铁律 4 要求跑完即释放，别为凑闸门空占）。预期：若 full 的 +2.16pt 能恢复到接近 graph_only 的 +9.73pt，则该路线才**首次**具备验收可能。
2. **排序侧实验**（更可能出真分数）：300_cn 40 道未命中里 31 题**有名次**、14 题卡在第 7–10 名 ⇒ 缺口是排序性质。
   选项：`top_k` 6→10 的端到端实测（此前只报过投影 0.867/0.696，**未实测**）、或 Cross-Encoder 重排（`docs/CrossEncoder重排实验_20260916.md` 有旧结论可接）。
3. **题集 i 的 L2**（MULTI 44 + T2i 58）：本轮按预注册**只报数不做裁决**，若要提级为主口径需先改预注册文档。
4. 结构性天花板要记住：`all(300)` = 196/300 = **0.653**，冲 80% 只能靠 `answerable` 分层口径或改用例（后者已被明确**拒绝**，见 SESSION2 §5.5）。

## 6. 已知坑（本轮新增，勿再踩）

1. **默认路径的 slug 不匹配会让脚本"看不见"已存在的产物**：`replay_300_cn_zero.json` vs 真实文件名 `replay_300cn_zero.json`，
   结果闸门对已落盘的产物**静默打印 pending**。已修（`set.replace("_","")`），但教训通用：**路径拼出来的默认值要实测一次命中**。
2. **PENDING 必须有自己的退出码**。`_er_report_gates.py` / `_er_audit_completion.py` 现约定 0/1/2，
   把"产物没跑到"和"跑到了但不合格"分开——否则 `pending` 会被读成通过。
3. **"这条情况无害"的文档说法 = 待验假设**，不是豁免。计划书 §5 说两 agent 重抽同块无害（内容哈希去重），
   实测推翻（整块覆盖 + 后提交者胜 → 命名分裂），见 SESSION2 §4.13。
4. **构造性为真的闸门没有信息量**：「均值邻域 ≤ CAP」是先截断再比较，任何输入都只能打印 PASS —— 执行报告里已标「（构造性）」，别当证据引用。
5. **持久性主张要用干净副本证明**：`git worktree add ../tmp HEAD` → 在副本里跑 §1 命令 → `git worktree remove`。
   本轮实测：18 判据退出 0、闸门退出 0；顺带暴露出 replay 侧依赖未入库索引（已在执行报告 §5.1 如实分栏，不统称"可复现"）。

## 7. 汇报格式（沿用本仓库惯例）

- 每个数字带**口径 + 分母 + 出处文件**；hit 类必须写 `full/graph_only`、`all/answerable/unanswerable`、`@6/@10`、n=?。
- 涨与跌**同表报**，并给**逐题题号**（净值单独不算证据）。
- 涉及显著性就报 McNemar 的 `b/c/p`，并注明配对集是否已剔除未覆盖题（`_er_report_gates.py` 两行都给了）。
- 判据没跑就是 `PENDING`，不许写 ✅；`git status` 有未提交产物就要说明它属于哪一层（文档/代码/证据）。

## 8. 一句话交接

**阶段 1→3 已全部落地、18 条判据在干净副本里全绿、证据链已入库；补名路线因主闸未过（题集 i +2.16pt、p=0.344）而**未验收、未接线**，但 `graph_only +9.73pt` 已把"失败原因在喂法不在识别"这件事证真 —— 下一轮要么做符号通道实验，要么转攻排序，别再往补名规模上加注。**
