# Compendium 正典语料入库报告（2026-09-20）

> **任务**：拉取 `VioletWilde/Reverse1999-Story-Compendium` 剧情文本 → 云端清洗 → 测试验收
> **执行**：主线 / 活动 / 角色剧情 / 轶事 四类（排除 `appendix_unbound` 未绑定旁支，用户确认）
> **原则**：正文是官方正典，**一律不改写**；云端 LLM 只做质检与模式提炼（见 §4）

---

## 一、结论摘要

| 指标 | 入库前 | 入库后 | 变化 |
|---|---:|---:|---:|
| 剧情语料总块数 | 9 021 | 14 247 | **+5 226** |
| `canon_zh`（中文正典）块 | 663 | 5 889 | **+5 226（×8.9）** |
| 中文块 | 1 028 | 6 247 | +5 219 |
| **中文正文字数** | 554 168 | 3 787 281 | **+3 233 113（×6.8）** |
| 正典文档数 | 112 | 189 | +77 |

- 测试：**986 passed / 1 failed / 1 skipped**；唯一失败项为**既有环境依赖**（见 §6）。
- 验收：**11 通过 / 2 失败**；两项失败均为「新增块尚未跑图谱抽取」的预期状态（见 §6）。

**关键发现**：既有 112 篇灰机 `canon_zh` 与 compendium 正文**零重合**（同类词条正文 40 字窗口
命中 0/6）。灰机 `小径/<篇名>` 是支线读物，compendium 是**全本对话**——两者互补，
故本次**只新增、不覆盖**。

---

## 二、新增产物

| 路径 | 说明 |
|---|---|
| `data/lore/wu_ming_zhe/canon_zh/<篇名>.compendium.md` | 77 篇清洗后正典正文（3.24 M 字） |
| `data/lore/wu_ming_zhe/compendium_clean_report.json` | 逐篇清洗报告（字数 / 版本来源 / 冲突） |
| `data/knowledge/plot_corpus_wu_ming_zhe.json` | 重建后的剧情语料（14 247 块） |
| `scripts/compendium_canon_corpus.py` | 结构化清洗管线（`--convert` / `--dry-run` / `--status` / `--verify`） |
| `scripts/compendium_cloud_qc.py` | 云端质检（人机在环，产出报告，**不写正文**） |

分类分布：

| 分类 | 篇数 | 字数 |
|---|---:|---:|
| 主线 | 14 | 917 834 |
| 活动 | 21 | 1 357 375 |
| 角色剧情 | 17 | 448 578 |
| 轶事 | 25 | 520 582 |
| **合计** | **77** | **3 244 369** |

---

## 三、清洗规则（全部确定性，可复现）

正文**一字未改**；以下仅剥离非剧情外壳：

| # | 规则 | 实测规模 |
|---|---|---:|
| 1 | 阅读导航块整段删除（`<!-- reading-navigation -->` 含中间的链接行） | 78 处 |
| 2 | `## 目录` 整段删除 | 77 处 |
| 3 | `<a id="episode-…">` 锚点删除 | 1 004 处 |
| 4 | HTML 注释 / 分隔线删除 | 308 处 |
| 5 | `<br>` 还原为换行、行内 HTML 标签剥离 | 464 处 |
| 6 | `> ` 引用前缀去除（保留标题卡/副标题文本） | 2 782 处 |
| 7 | 剧本编号行删除：`第八章8-11.2（script 100817）`、`【3.4】不老春20.1（script 203430）` | 391 处 |
| 8 | 制作/美术备注删除：`场景-…`、`音效-…`、`特效-…`、`镜头…`、`氛围图…` | 292 处 |
| 9 | 裸备注行：`鹭鸶剪神秘术特效` | 少量 |
| 10 | 转场/分支标记删除：`渐黑`、`黑屏`、`地标`、`浮窗`、`转场`、`消人` | 476+ 处 |
| 11 | 空壳 Markdown 行（`**`、`###` 等）删除 | 少量 |

> **刻意不做的**（避免误删正典）：
> - **注音符号行不删**——91 处注音（`**？？？**：ㄘ……`）是**角色刻意的乱码台词**，
>   删掉会破坏正文。
> - `移动 / 攻击 / 供能 / 鼓捣` 等通用动词（合计 56 处）不删——它们可能出现在正常叙述里，
>   为 0.05% 的噪声不值得承担误删风险。
> - `## Part …`、`副标题：`、`【标题卡】` **保留**——它们是剧情结构，云端曾误报为噪声，已人工否决。

---

## 四、云端 LLM 的角色（`deepseek-v4.1-flash`）

正文清洗完全由确定性规则完成，**模型不参与改写**。云端只做两件事：

1. **元数据映射**：章节 → 版本 / 分类（见 §5）。
2. **质检审计**：240 块抽样，归纳出 11 类非剧情模式（`data/knowledge/_audit/compendium_qc.json`），
   再由人工把关固化为 §3 的规则 8–11。

**模型误报已被人工否决**（这正是「人机在环」的意义）：

- 首轮把 `错别字 / 成语误用 / 搭配不当` 当作问题——属校对范畴，**不在职责内**，
  且与「正典保真」原则冲突 → 已在提示词中明令禁止。
- 次轮把 `## Part 1 · 开篇`、`副标题：…`、`【标题卡】…` 列为 `scaffolding/metadata`——
  经核验**是剧情结构**，予以保留。

> 注意：该模型是**推理模型**，`max_tokens=8000` 会被思维链吃光导致正文为空
> （实测 `finish_reason=length`、`content=""`）；管线固定用 32000 并截断输入。

---

## 五、版本号解析（不猜填）

项目约束 **TS2「未知即标空，禁止猜填」**。版本经四级链路解析，**49/77 命中，28 篇留空**：

| 来源 | 篇数 | 说明 |
|---|---:|---|
| `chapter_metadata`（仓库自带） | 24 | 直接命中 |
| `chapter_id` 编码规则 | 20 | `11101→1.1`、`27101→2.7`（详见下） |
| 项目既有语料 `arc→version` | 5 | 已验证映射 |
| `plot_timeline.json` | 1 | 人工维护锚点 |
| **未确认（留空）** | **28** | 3 联动活动 + 25 轶事 |

### 版本编码规则的验证

规则：5 位 `chapter_id` → `{id//10000}.{(id//1000)%10}`

- 与 `chapter_metadata` 已有版本逐条比对：**一致 66 / 分歧 0**
- 与**独立来源** `story_canonical.json` 交叉核对：**一致 59 / 分歧 0**

两者均为 0 分歧，规则可信；且已固化为 `--verify` 自检随管线保留。

> 留空的 28 篇在 `chapter_metadata` / `story_canonical` / 存档名 / 镜像链中
> **version 全为 null**，即仓库本身不提供——按 TS2 留空，并登记为待补。

---

## 六、测试与验收

### 6.1 单元/集成测试

```
986 passed, 1 failed, 1 skipped
```

唯一失败：`tests/test_llm_config.py::TestChatRequestLLMOverride::test_llm_override_embedded_in_chat_request`

- 该文件**未被本次改动触碰**（`git status` 无变更）；
- 失败原因是测试请求打到了**外部真实端点**并收到 `401 invalid_api_key`
  （日志：`provider=qwen2.5:1.5b status=401`）；同文件另有 Ollama 用例依赖
  `localhost:11434`（当前未运行）。
- 即**环境依赖型失败**，与语料无关。

> 本次另修好 1 项**先前已存在**的失败
> （`TestP3SeedGate::test_offtopic_queries_inject_nothing`，详见 §7）。

### 6.2 图谱验收（`acceptance_plot_graph.py --skip-r14`）

```
11 通过 / 2 失败 / 1 跳过
```

| 项 | 状态 | 说明 |
|---|---|---|
| R4 语料切块合规 | ❌ | 块 14 247，**缓存缺失 5 206** |
| R10 抽取覆盖率 | ❌ | empty 5 846，NOOP 640，差集 **5 206** |
| 其余 R1–R3、R5–R9、R11–R13 | ✅ | 全通过 |

**R4/R10 的失败是「新增中文块尚未做图谱抽取」的必然结果**，非缺陷：

- 基线（旧语料 9 021 块）下 R10 同样失败，差集同为 **5 253**（既存问题）；
  本次 R4 由「缺失 0」变为「缺失 5 206」，正是新增 5 226 块**还没有抽取缓存**。
- 修复路径：对这 5 226 块跑云端抽取（`scripts/cloud_extract.py`，同现有 `cloud-extract-v1` 规范）。

**建议的下一步（未执行，需你确认）**：

```
.venv/Scripts/python.exe -X utf8 scripts/cloud_extract.py --plan      # 357 批 / 40 块
.venv/Scripts/python.exe -X utf8 scripts/cloud_extract.py --dump --batch 0 --size 40
#   → 云端模型按规范产出 jsonl
.venv/Scripts/python.exe -X utf8 scripts/cloud_extract.py --apply --batch 0
.venv/Scripts/python.exe -X utf8 scripts/build_plot_graph.py --build-graph   # 零 LLM 重放
```

预估 5 226 块 / 131 批。抽取完成后 R4/R10 应同时转绿，R11/R12 覆盖率亦将上升。

---

## 七、过程中修复的真实缺陷

| # | 缺陷 | 影响 | 处置 |
|---|---|---|---|
| 1 | 导航链接行漏进正文 | 78 篇各漏 1 行 | 导航块**成对整段**删除（先删块再删注释） |
| 2 | 制作备注行未过滤 | 66 处，且**抢排名**——把芭卡洛儿真实台词挤出 top-2 | 新增规则 8–10 |
| 3 | 中文垃圾实体点火 | **新增 2 条离题泄漏**：`解释一下相对论`←实体「解释」；`红楼梦的作者是谁`←实体「作者」 | 补入 `GENERIC_SEED_NAMES`（④ 动作/角色类泛词） |
| 4 | 2 项测试前提过期 | `牙仙`/`芭卡洛儿` 断言死写英文名；当时只有英文 ASR，中文正名无可召回 | 判据改为「中/英正名命中其一」，**并保留脏别名不得登顶的原意图** |

> **注（#3、#4 的联动）**：canon_zh 使中文命中面扩大 6 倍，原本够不着的非锚定中文垃圾实体
> 开始点火。这是本次唯一的检索行为变化，已在测试中锁死。

---

## 八、复现方式

```bash
# 0. 原料（约 1 GB，已 gitignore）
git clone --depth 1 https://github.com/VioletWilde/Reverse1999-Story-Compendium.git \
    vendor/Reverse1999-Story-Compendium

# 1. 结构化清洗（幂等）
.venv/Scripts/python.exe -X utf8 scripts/compendium_canon_corpus.py --dry-run   # 预览
.venv/Scripts/python.exe -X utf8 scripts/compendium_canon_corpus.py --convert   # 落盘
.venv/Scripts/python.exe -X utf8 scripts/compendium_canon_corpus.py --verify    # 版本规则自检

# 2. 重建语料
.venv/Scripts/python.exe -X utf8 scripts/build_plot_graph.py --build-corpus

# 3. 云端质检（可选，成本约 6 次调用 / 240 块）
.venv/Scripts/python.exe -X utf8 scripts/compendium_cloud_qc.py --sample 240

# 4. 验收
.venv/Scripts/python.exe -X utf8 -m pytest -q
.venv/Scripts/python.exe -X utf8 scripts/acceptance_plot_graph.py --skip-r14
```

### 回滚

```bash
cp data/knowledge/plot_corpus_wu_ming_zhe.json.bak_precompendium_20260920_190925 \
   data/knowledge/plot_corpus_wu_ming_zhe.json
rm data/lore/wu_ming_zhe/canon_zh/*.compendium.md
```

---

## 九、遗留与风险

| # | 事项 | 说明 |
|---|---|---|
| 1 | **5 226 块未抽取** | R4/R10 失败的直接原因，需跑云端抽取（§6.2） |
| 2 | 28 篇缺版本 | 仓库不提供，按 TS2 留空，待官方/灰机补 |
| 3 | 27 篇与灰机页同名 | 已用 `.compendium.md` 后缀 + `huiji_cmp_` doc_id 双隔离，**零冲突**（已验证 112+77） |
| 4 | 未收录 `appendix_unbound` | 用户确认排除；74 个未绑定旁支系列仍是空白 |
| 5 | `trail_corpus` 未纳入 | compendium 另有 2.8 M 字小径语料，与既有灰机小径**部分互补**，本次未处理 |
| 6 | 跨语种 | 仓库有 en/ja/ko/zh-TW，本次仅用 zh_CN |
| 7 | `vendor/` 已 gitignore | 1 GB 原料不入库；产物 `*.compendium.md` 入库 |

---

## 十、变更文件

**新增**
- `scripts/compendium_canon_corpus.py`、`scripts/compendium_cloud_qc.py`
- `data/lore/wu_ming_zhe/canon_zh/*.compendium.md`（77）
- `data/lore/wu_ming_zhe/compendium_clean_report.json`
- `docs/compendium-rag/extraction/compendium正典入库报告.md`（本文件）

**修改**
- `src/roleplay/core/knowledge/plot_corpus.py` — 支持可选的 `doc_id：` 头部
- `src/roleplay/core/knowledge/plot_graph.py` — `GENERIC_SEED_NAMES` 补 ④ 动作/角色类泛词
- `tests/test_plotrag_optimization.py` — 2 项真实数据测试的判据更新
- `data/knowledge/plot_corpus_wu_ming_zhe.json` — 重建（14 247 块）
- `.gitignore` — 排除 `vendor/`
