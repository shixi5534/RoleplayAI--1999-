# QA 测试报告 —— roleplay-ai 图谱关系命名治理验证

| 项 | 值 |
|---|---|
| 报告日期 | 2026-09-09 |
| 测试人 | 严过关（Yan）· QA 工程师 |
| 被测项目 | `C:\Users\Lenovo\WorkBuddy\2026-07-27-16-45-03\roleplay-ai` |
| 环境 | Windows + Git Bash，Python 走 `.venv/Scripts/python.exe -X utf8`，Node v22.22.2 |
| 验证对象 | 「图谱关系命名治理」改动后的回归状态 |
| **总体结论** | ✅ **系统运行正常**（可判定为正常） |

---

## 1. 摘要

| 测试项 | 结果 |
|---|---|
| 重点回归（test_plot_graph + test_rag_graphrag_audit） | ✅ **52 passed** |
| 治理验证脚本 `--plot` | ✅ exit 0，指标全部达标 |
| 治理验证脚本 `--lore` | ✅ exit 0，指标全部达标 |
| 全量 pytest（`tests/`，排除 e2e） | ✅ **562 passed / 1 skipped / 0 failed**（exit 0） |
| 独立基线统计（自写脚本，不复用治理代码） | ✅ **未回退**，全部 OK |
| JS 冒烟（test_pet_master_plan.js） | ⚠️ 首轮 2 项失败 → 判定测试代码 Bug → 已修复 → ✅ **ALL TESTS PASSED** |

- **失败项总数：2**（均为测试代码 Bug，已由 QA 自行修复）
- **源码 Bug：0**（无需转交工程师）
- **环境跳过：1**（`e2e_pet_voice.py`）
- **基线回退：无**（8 项指标逐项比对全部一致）

---

## 2. 测试执行明细

### 2.1 重点回归（治理直接相关）

```bash
.venv/Scripts/python.exe -X utf8 -m pytest tests/test_plot_graph.py tests/test_rag_graphrag_audit.py -q
```

**结果：`52 passed, 1 warning in 3.97s`（exit 0）**

覆盖：plot 图谱构建/检索链路、GraphRAG 审计（含上一轮改过夹具谓语「同僚」→「同伴」的用例）。

### 2.2 治理验证脚本

```bash
.venv/Scripts/python.exe -X utf8 scripts/verify_relation_governance.py --plot --json   # exit 0
.venv/Scripts/python.exe -X utf8 scripts/verify_relation_governance.py --lore --json   # exit 0
```

**plot 图谱（治理前 → 治理后）：**

| 指标 | 治理前（.bak_relnorm） | 治理后（当前） | 变化 |
|---|---|---|---|
| 边数 | 4261 | 4035 | −226（低质边被卫生过滤丢弃） |
| 唯一关系名 | **1564** | **78** | −1486（−95.0%） |
| 单例谓语 | 1128 | **0** | 清零 |
| 单例谓语占比 | **72.12%** | **0%** | −72.12pp |
| Top10 集中度 | 23.89% | 42.28% | +18.39pp（头部更收敛） |
| 检索非空率 | 16/16 | **16/16** | 持平（未劣化） |

**lore 图谱（当前）：**

| 指标 | 值 |
|---|---|
| 边数 | 3608 |
| 唯一关系名 | 75 |
| 单例谓语 / 占比 | 0 / **0%** |
| Top10 集中度 | 46.34% |
| 检索非空率 | **13/16** |

### 2.3 全量 pytest

```bash
.venv/Scripts/python.exe -X utf8 -m pytest tests/ -q --ignore=tests/e2e_pet_voice.py
```

**结果：`562 passed, 1 skipped, 1 warning in 33.95s`（exit 0）**，收集总数 563。

> ⚠️ **环境现象记录（非测试失败）**：首次运行出现 `RAW_EXIT=1` 且**无汇总行**。
> 根因：pytest 会话结束时清理临时目录，触发沙箱 bulk-delete 守卫
> （`SAFE_DELETE_BULK_CONFIRM_REQUIRED`，53 项 > 阈值 50），teardown 被中断。
> 复验方式：改用项目内 `--basetemp=tmp_pytest/bt_run1` 重跑 → **`exit 0`，汇总行为
> `562 passed, 1 skipped`**。进度条字符统计（剔除 safe-delete 干扰后）为 `562 .` + `1 s`，
> **无 `F`/`E`**。故判定为**环境产物，不计失败**。

---

## 3. 失败项逐条分析与路由判定

### 失败 1 / 2：`tests/test_pet_master_plan.js` 静态检查（2 项）

**现象**：`node tests/test_pet_master_plan.js` → `TEST FAILED: 2 个静态检查未通过`

| # | 检查项 | 断言（原） | 实际源码 |
|---|---|---|---|
| 1 | `spine.js 修正 idle 调用（无 _idle 残留）` | 正则要求 `this.idle(); // 起待机池` | 源码为 `this.idle(); // 重置后回到待机池`（`frontend/js/spine.js:530`） |
| 2 | `spine.js 相机按 AABB 动态取景（不再压到屏幕外）` | 要求 `getBounds(this._boundsOffset, this._boundsSize` 且 `camY = bottom + this._h / 2 - this._groundMargin` | 源码已改为**稳定相机锚定 setup pose**：`cam.position.y = this._setupBottom * s + this._h / 2 - this._groundMargin`（`:618`） |

**根因判定（关键证据）**：

1. `spine.js:611-617` 有 6 行注释**明确说明**旧实现「每帧按 AABB 重新取景」会导致
   「整个模型在窗口里平移抖动，且超出取景的部位被画布边缘裁掉」，因此**刻意**改为
   「稳定相机锚定 setup pose + 包络盒缩放 `_fit()`」。
2. 逐 token 复核源码，确认**意图已被满足**：
   - `this._idle()` 残留 → **0** 处（无残留，符合要求）
   - `cam.position.y = -this._h / 2`（旧硬编码）→ **0** 处
   - `_envReachX` → 8 处、`_envUp` → 9 处（包络盒缩放 `_fit()` 在位）
   - `cam.position.y = this._setupBottom * s + this._h / 2 - this._groundMargin` → 1 处
3. `desktop/` 与 `frontend/` 在 git 中**零改动**（`git status --porcelain -- desktop/ frontend/` 为空），
   与本轮关系命名治理**完全无关**，属既有遗留。

**路由判定：➡️ 测试代码 Bug（断言陈旧/过度绑定实现文本），归属 QA 自行修复。**

- 判定依据：断言正确的**意图**（无 `_idle` 残留、模型不被压出屏幕）在源码中均已满足，
  只是断言机制过时——#1 绑定了会漂移的**注释措辞**，#2 绑定了已**被刻意替换**的旧设计。
- **不是**源码 Bug，故**未**转交工程师。

**修复方式**（仅改 `tests/test_pet_master_plan.js`，未触碰任何源码）：
- #1：去掉对注释文本的正则，回归行为断言 `this.idle();` + `!this._idle()`
- #2：断言同步到新设计——相机锚定 setup pose、无旧硬编码 `-this._h/2`、
  且 `_fit()` 使用包络 `_envReachX`/`_envUp`（保留「不压出屏幕」的原始意图）

**复验结果：✅ `ALL TESTS PASSED`，`NODE_EXIT=0`**（Round 2 通过）

> 说明：修复为**收紧/同步意图**，并非放宽——两条断言仍各自校验 2~4 个实质条件，
> 未删除任何检查项。

---

## 4. 基线对比（核心：是否回退）

使用**独立自写脚本** `tmp_pytest/qa_baseline_stats.py` 直读 JSON 统计（不复用
`verify_relation_governance.py` 的统计代码，避免同源偏差），并与治理脚本结果交叉验证，
**两者完全一致**。

| 指标 | plot 基线 | plot 实测 | lore 基线 | lore 实测 | 判定 |
|---|---|---|---|---|---|
| 文件 | `plot_graph_wu_ming_zhe.json` | — | `graph_wu_ming_zhe.json` | — | ✅ |
| 边数 | 4035 | **4035** | 3608 | **3608** | ✅ 未回退 |
| 唯一关系名 | 78 | **78** | 75 | **75** | ✅ 未回退 |
| 单例谓语占比 | 0% | **0%**（单例数 0） | 0% | **0%**（单例数 0） | ✅ 未回退 |
| 检索非空率（16 查询） | 16/16 | **16/16** | 13/16 | **13/16** | ✅ 未回退 |

**结论：🔵 8/8 项指标与基线完全一致，无任何回退。**

（治理脚本独立复核的相同 4 项指标亦逐项相同：plot 4035/78/0%/16×16，lore 3608/75/0%/13×16。）

---

## 5. 红线约束核查

| # | 红线 | 核查方式 | 结果 |
|---|---|---|---|
| 1 | `relation_vocab.py` 是唯一词表源 | 全仓 grep `canonicalize_relation` / `relation_vocab` | ✅ 全部引用点（`graph_extract.py:26-28`、`plot_graph.py:38-40`、`scripts/normalize_graph_relations.py:35`、`scripts/backfill_failed_chunks_cloud.py:797`）均从 `relation_vocab` 导入，无第二份词表 |
| 2 | `build_graph.py` meta 同时含 `ns` 与 `namespace` | 代码 + 数据双查 | ✅ 代码：`build_graph.py:71` `"ns"` 与 `:74` `"namespace"` 并存；**功能验证**：`graph_wu_ming_zhe.json` 全部 3700 条 evidence 的 `ns` 分布为 `lore_wu_ming_zhe` 3551 / `lore_wu_ming_zhe_spoken` 149，**落兜底 `"lore"` 的比例 = 0/3700**（证明 `graph_extract.py:244` 的 `meta.get("namespace")` 已取到值，bug 已修复生效） |
| 3 | 唯一名 ≤ 300、单例比 ≤ 40% | 实测 | ✅ plot 78 / 0%，lore 75 / 0%，均远低于红线 |
| 4 | 不动 `.bak_relnorm_*` 备份 | `ls -la --time-style=long-iso` | ✅ `plot_graph_wu_ming_zhe.json.bak_relnorm_20260909_173330` mtime 仍为 **2026-09-08 21:12**，未被改动 |

> 📌 关于红线 2 的一次**误报澄清**：初查时发现落盘 evidence 只有 `ns` 键、无 `namespace` 键，
> 疑似红线未生效。追查后确认：`namespace` 是**输入 meta** 的键（`graph_extract.py:244` 读取），
> 落盘 evidence 的 schema 本就是 `{ns, doc_id, hash}`（`:276`）。故属我核对口径有误，
> **非缺陷**；并以「兜底 `lore` 占比 0/3700」作为修复生效的正向证据。

---

## 6. 环境跳过清单

| 文件 | 跳过原因 | 归类 |
|---|---|---|
| `tests/e2e_pet_voice.py` | 需前端静态服务器 `http://127.0.0.1:18080`（当前探测返回 **502 不可达**，服务器未运行）；且文件名不匹配 pytest 默认 `test_*.py`，**未被收集**（grep 收集结果命中 0） | 🌐 环境依赖跳过（不计失败） |
| `tests/test_pet_master_plan.js` | Node v22.22.2 可用，**实际已执行**（非 pytest 收集范围） | ✅ 实际运行并通过（见 §3） |

**pytest 主动 skip（1 项，非失败、非环境问题）：**

- `tests/test_qa_profile_r2_verify.py:137`
  原因：「P2 观察点：跨 UserProfile 实例共享 KB 并发写同 key 产生 2 条（实例级锁不互斥）」
  —— 测试内**主动 `skip`** 的 P2 观察点，属已记录在案的已知限制（实例级锁不互斥），
  与本轮关系治理改动**无关**，不计失败。

---

## 7. 结论

**✅ 系统可判定为「运行正常」。**

依据：

1. **全量测试 562 passed / 1 skipped / 0 failed**（exit 0），重点回归 52 passed；
2. **基线 8/8 项指标零回退**，且与治理脚本交叉验证一致；
3. **治理效果本身显著且不劣化检索**：唯一关系名 1564 → 78（−95%），
   单例谓语占比 72.12% → 0%，而检索非空率保持 16/16（plot）与 13/16（lore）不变；
4. **4 条红线全部满足**，且 `namespace` 证据 bug 已确认修复生效（兜底比例 0/3700）；
5. 唯一 2 项失败已定位为**陈旧测试断言**，由 QA 修复并复验通过，**源码零 Bug**。

**遗留与建议（不阻塞本次结论）：**

| # | 事项 | 建议 |
|---|---|---|
| 1 | `test_qa_profile_r2_verify.py:137` P2 观察点：跨 `UserProfile` 实例共享 KB 时实例级锁不互斥，并发写同 key 产生 2 条 | 属既有已知限制，与本轮无关；建议后续单独排期（如需强一致，考虑改为进程级/文件级锁） |
| 2 | `tests/test_pet_master_plan.js` 存在多处**绑定源码文本/注释**的脆弱断言 | 本次已修复 2 处；建议后续将同类静态检查改为行为校验，避免再次因重构漂移误报 |
| 3 | pytest 临时目录清理触发沙箱 bulk-delete 守卫，导致 exit 1 且无汇总行 | 环境产物；建议 CI/本地固定 `--basetemp` 以稳定退出码 |

---

## 附录：本次 QA 产出与操作边界

**新增文件（仅测试/临时域，未改任何源码）：**

- `deliverables/qa-test-report-20260909.md`（本报告）
- `tmp_pytest/qa_baseline_stats.py`（独立基线统计脚本，可重跑）
- `tmp_pytest/bt_run1`、`bt_run2`、`bt_run3`、`bt_focus`（pytest basetemp 目录）

**修改文件（仅测试代码，1 个）：**

- `tests/test_pet_master_plan.js`（修复 2 处陈旧断言）

**操作边界遵守情况：**

- ✅ 未修改 `src/` 下任何文件（`git status` 中 `src/` 的 M 标记均为上一轮治理改动，**非本次 QA 所为**）
- ✅ 未改动 `data/knowledge/*.bak_relnorm_*` 备份
- ✅ 未执行 `git push`，未删除任何文件
