# 接手清单：图谱关系命名治理（2026-09-09 完成态）

> 交接范围：roleplay-ai 项目图谱关系命名治理（三步治理 + 验证 + 失败块清零）。
> 仓库：`C:\Users\Lenovo\WorkBuddy\2026-07-27-16-45-03\roleplay-ai`（分支 `refactor/frontend-layout`，提交 `f52044c3`，远端历史恢复仍未做）。
> 运行环境：Windows + Git Bash；Python 用 `.venv/Scripts/python.exe -X utf8`；Ollama 本地（qwen2.5:7b 串行 `n_seq_max=1`，nomic-embed-text 嵌入）。

---

## 一、当前状态（一句话）

治理已全部闭环：plot 图谱已离线归一化，lore 图谱已用受控词表提示词全量重建且失败块清零，检索链路修好并验证达标。**下一步是 P4 A/B 测试，未启动。**

## 二、核心指标（验收基线，后续改动不得回退）

| 指标 | plot 图谱 | lore 图谱 |
|---|---|---|
| 文件 | `data/knowledge/plot_graph_wu_ming_zhe.json` | `data/knowledge/graph_wu_ming_zhe.json` |
| 边数 | 4035 | 3608 |
| 唯一关系名 | 78（77 canonical + 1 待审核哨兵） | 75 |
| 单例谓语占比 | 0%（治理前 72.1%） | 0% |
| 检索非空率（16 查询） | 16/16 | 13/16（3 个为语料外实体，非缺陷） |

## 三、本次新增/修改的文件（都在仓库内）

| 文件 | 作用 |
|---|---|
| `src/roleplay/core/knowledge/relation_vocab.py` | **唯一规则源**：77 canonical 谓语 + 1038 同义词映射 + 卫生过滤（否定/超长8字/标点/拉丁/黑名单）。改词表只改这里 |
| `scripts/normalize_graph_relations.py` | 离线归一化 CLI（`--dry-run`/`--apply`，自动备份） |
| `scripts/verify_relation_governance.py` | 验证 CLI：`--plot`（前后对比）`--lore` `--json` |
| `scripts/backfill_failed_chunks_cloud.py` | 49 个本地模型失败块的人工补抽缓存 |
| `scripts/backfill_last_chunk.py` | 最后 1 块补抽缓存 |
| `scripts/build_graph.py` | 修复 `_load_chunks` 证据 ns 键名 bug（`ns`→补传 `namespace`） |
| `src/roleplay/core/knowledge/graph_extract.py` | 提示词枚举词表 + `normalize_extraction` 接入 `canonicalize_relation` 强过滤 |
| `src/roleplay/core/knowledge/plot_graph.py` | 中英提示词枚举词表 + `build_plot_graph` 接入过滤 + `rel_filtered` 统计 |
| `tests/test_rag_graphrag_audit.py` | 夹具谓语「同僚」→「同伴」（52 测试全过） |
| `deliverables/graph-relation-governance-20260909.md` | **总报告（先读这个）** |
| `deliverables/plot-graph-relation-normalization-20260909.md` | 归一化明细 + 269 个待审核谓语全清单 |

备份：`plot_graph_wu_ming_zhe.json.bak_relnorm_20260909_173330`（归一化前原状）。

## 四、待办（按优先级）

### P4-0：P4 A/B 测试（下一个任务，方案已定未执行）
- A 组：现配置；B 组：`plot_graph_enabled=false` + `graph_enabled=false`（都在 `src/roleplay/config.py`，注意两开关默认均 False，A 组要在 .env 或启动参数里显式开）
- 观测：剧情事实准确率 / 关系脉络块引用率 / 幻觉率；重点「隶属/对抗/保护」类问题
- 注意：lore 层 `graph_include_weak=False`（孤证边不参与）；烟雾测试口径是 `include_weak=True`，A/B 时统一口径再对比

### P4-1：人工审核「待审核」桶（270 条边，6.3%）
- 位置：plot 图谱内 `relation=待审核、relation_raw=原名、needs_review=true`
- 清单：归一化报告附录；处理方式二选一：①补充 `SYNONYM_MAP` 后重跑 `normalize_graph_relations.py --apply`（幂等）②确认无语义的边删掉

### P4-2：lore 层待办
- lore 缓存里新块若再遇 qwen 畸形 JSON（症状 `"relations[]}` 缺冒号），照 `backfill_failed_chunks_cloud.py` 模式人工补抽
- plot 层提示词改造后**尚未重跑 plot 重建**（plot 目前是离线归一化的产物，缓存里仍有旧自由谓语）；若要彻底，跑 `scripts/build_plot_graph.py --rebuild`（时长同 lore，约 6 小时，非必需）

### P4-3：其他悬案（非本次范围但已挂账）
- git 远端历史恢复：`git fetch origin` 仍未执行（见 `deliverables/git-repo-recovery-20260909.md`，**切勿 push --force**）
- 两个线上 bug（云模型切换失败 / RAG 注入失败）与 ROLEPLAY_PROMPT_OPTIMIZATION_PLAN.md P1-1～P1-4 仍在推进中
- 沙箱限制备忘：无法直连 github.com（镜像 ghproxy.net）；`C:\Users\Lenovo\WorkBuddy\` 树下 git 嵌套分支名写入受限

## 五、常用命令速查

```bash
cd C:/Users/Lenovo/WorkBuddy/2026-07-27-16-45-03/roleplay-ai
# 图谱统计
.venv/Scripts/python.exe -X utf8 scripts/build_graph.py --character wu_ming_zhe --stats
# 增量/失败续跑（幂等缓存，不重复调 LLM）
ROLEPLAY_GRAPH_EXTRACT_BATCH=1 ROLEPLAY_GRAPH_EXTRACT_TIMEOUT=180 \
  .venv/Scripts/python.exe -X utf8 scripts/build_graph.py --character wu_ming_zhe --build
# 验证（词频分布 + 16 查询烟雾测试）
.venv/Scripts/python.exe -X utf8 scripts/verify_relation_governance.py --plot --json
.venv/Scripts/python.exe -X utf8 scripts/verify_relation_governance.py --lore --json
# 回归测试
.venv/Scripts/python.exe -X utf8 -m pytest tests/test_plot_graph.py tests/test_rag_graphrag_audit.py -q
```

## 六、改动红线（无回归约束）

1. `relation_vocab.py` 是唯一词表源：加/删谓语必须同步检查 `_NEG_RE`、`JUNK_BLACKLIST`、子串匹配顺序（否定判定先于规则归约）
2. `build_graph.py` 的 meta 必须同时含 `ns` 与 `namespace` 键（历史 bug 教训）
3. 改动后必跑：52 项测试 + `verify_relation_governance.py`，唯一名不得 >300、单例比不得 >40%
4. 不要动 `plot_graph_wu_ming_zhe.json.bak_relnorm_*` 备份（验证基线依赖它做前后对比）
