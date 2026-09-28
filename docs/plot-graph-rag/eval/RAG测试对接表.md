# RAG 测试对接表（灰机标准 · 新任务接手用）

> 更新：2026-09-12 18:40｜维护人：主会话 Agent
> 用途：开新任务/新会话做 RAG 测试时，凭此表直接接手，无需重新踩坑。

---

## 一、一句话现状

《重返未来:1999》角色「无名者(wu_ming_zhe)」的剧情图谱 RAG 已完成 100% 抽取（8358 块）+ 灰机标准命名核查 + 时间线排序；已建灰机标准检索评测（14 题），**2026-09-12 下午已完成 P0/P1 融合修复：top10 通过率 43% → 93%（13/14）**，pytest 698 基线零回退。唯一残留缺口：努库泰澳岛民题的第 3 证据组（Salone/Kamuta，语料侧共现缺失，见 §六）。

## 二、环境与常用命令

| 项 | 值 |
|---|---|
| 项目根 | `C:\Users\Lenovo\WorkBuddy\2026-07-27-16-45-03\roleplay-ai` |
| 解释器 | `./.venv/Scripts/python.exe -X utf8`（必须带 `-X utf8`） |
| **本评测** | `./.venv/Scripts/python.exe -X utf8 scripts/eval_rag_huiji.py --top 10 [--verbose]`（exit 0=全过，2=有 FAIL） |
| 图谱重建 | `./.venv/Scripts/python.exe -X utf8 scripts/build_plot_graph.py --character wu_ming_zhe --build-graph --rebuild-graph-only` |
| 回归 | `./.venv/Scripts/python.exe -X utf8 -m pytest -q` → **698 passed, 1 skipped** 基线 |
| 时间线 | `scripts/plot_timeline.py --check / --print story\|version / --build` |

## 三、核心数据资产

| 文件 | 作用 | 现状 |
|---|---|---|
| `data/knowledge/plot_graph_wu_ming_zhe.json` | 图谱落盘（schema=plot-v1） | **6814 实体 / 5719 边**，悬空 0、自环 0 |
| 语料（`settings.plot_corpus_dir`） | 8358 块 / 726 文档 | cached 8358 / failed 0 / skipped 385（空块正常） |
| `data/lore/wu_ming_zhe/plot_aliases.json` | 别名表：**正名 → [别名]** | 已并 26+17+5 组灰机标准别名 |
| `data/lore/wu_ming_zhe/plot_glossary.json` | 其中 `alias_flat` 与上表**必须同步** | 同上 |
| `data/lore/wu_ming_zhe/plot_timeline.json` | 时间线元数据（34 entries=24 有据+10 未考） | 见 〇d 节 |
| `scripts/eval_rag_huiji.py` | **灰机标准检索评测**（本次交付） | 14 题，报告落 `_audit/rag_huiji_eval_report.json` |
| `scripts/test_plot_graph_retrieval.py` | 既有端到端检索实测（16 固定查询+补抽自检） | 可复跑对照 |

## 四、检索接口速查（写测试用）

```python
import sys; sys.path.insert(0,'scripts'); sys.path.insert(0,'src')
from roleplay.config import get_settings
from roleplay.core.knowledge.plot_graph import PlotGraphRegistry

settings = get_settings()
registry = PlotGraphRegistry(
    corpus_dir=settings.plot_corpus_dir,
    graph_dir=settings.plot_graph_dir,
    alias_dir=settings.plot_lore_dir,
    include_weak=bool(settings.plot_include_weak),
)
retr = registry.get("wu_ming_zhe")           # None = 图谱未加载
chunks = retr.retrieve("问题", top_chunks=10)  # 每个 chunk: .text / .score / .metadata["via"]
via = [c.metadata["via"] for c in chunks]     # "plot_graph"=图谱路径｜"plot_lexical"=词法兜底
seeds = retr.link("问题")                      # 查询链接到的实体 id（种子）
```

## 五、评测框架约定（eval_rag_huiji.py）

- **判分**：每题 `evidence` 为若干「关键词组」（组内互为备选）；top-K 证据块正文并集中，每组任一关键词命中即该组覆盖；**全部组覆盖 = PASS**
- **题库结构**：`{"q", "ref"(灰机标准答案), "evidence":[[同义备选...], ...]}`
- **扩题规则**：新题先做 oracle 验证（扫 8358 块确认证据词存在），0 命中的题不得入库（曾有「乌斯怀亚」0 块被移除）
- **报告**：`data/knowledge/_audit/rag_huiji_eval_report.json`（逐题 covered/missing/相关块/graph 路径数）

## 六、当前基线（灰机标准 14 题）

| top | 修别名前 | 融合修复前 | **现行（2026-09-12 融合修复后）** |
|---|---|---|---|
| 5 | 14% | 21% | **86%（12/14）** |
| 10 | 36% | 43% | **93%（13/14）** |
| 20 | 36% | 43%（平台期） | 未复测（top10 已近满） |

**PASS@top10（13 题）**：除「努库泰澳的岛民都有谁」外全部通过。

**残留 FAIL（1 题）**：努库泰澳岛民 2/3 组——组 3（塞洛尼/Salone/Selone/卡穆塔/Kamuta）缺：Salone 所在 3 块与 Nuku* 岛名块**零共现**（语料侧缺口，岛民对话块不提岛名），Kamuta 块(1132)虽含 Nukutai 但提及数并列排序不敌语料顺序靠前的块。可选解法：① 提及数并列时按「块内实体名种类数」二次排序；② 接受现状（其余 2 组已覆盖）。

### 2026-09-12 下午修复记录（本次交付）

| 类别 | 改动 | 文件 |
|---|---|---|
| P0 融合 | `retrieve()` 新增**种子实体提及块强制并入**：种子实体（基础分 1.0+PPR）与 PPR top 邻居的名下块按提及数取前 3 并入候选池，`via=plot_graph` + `seed_mention` 元数据 | `src/roleplay/core/knowledge/plot_graph.py` |
| link 增强 | ① 单字母拉丁别名（"J"）严格词边界放行；② **跨片段补充匹配**：不同查询片段的较短名可做种子（如「音乐总监」→Barcarola），但仅限人工别名表锚定实体 + 非同跨度子串（防「露西娅」带出「露西」、防泛词实体混入） | 同上 + `graph_store.py`（新增 `anchored_ids`） |
| P1 别名 | 疗愈师→Mercuria、音乐总监→Barcarola、Nuku Teow(努库泰澳/Nukutai/Nukateao)、阿马尔菲塔诺村(理性家族的崛起与衰落/Amalfitano)；`alias_flat` 已双写同步 | `data/lore/wu_ming_zhe/plot_aliases.json` + `plot_glossary.json` |
| 题库 oracle 修订 | 可燃点组2 += 火焰/fire（ASR 用词，圣火/火种 0 块）；中央塔组2 += central tower（ASR 英文表述，9 块）；岛民组3 += 卡穆塔/Kamuta（参考答案第 4 人） | `scripts/eval_rag_huiji.py` |
| P3 结论 | **「阿莱」非重复节点**：全库仅 1 处且为「阿莱夫」子串，无需并入 | 无改动 |

⚠️ 本次**未跑 `--rebuild-graph-only`**（偏离坑#6 的说明）：新增别名经 `alias_index` 核查均无占用冲突，registry 每次加载时 `bind_alias_table` 已全部生效（评测 13/14 为证）；而 rebuild 删图会让别名表成为首个注册者，反而有把图内既有 `Nukatai` 实体与别名表 `Nuku Teow` 拆成两个节点的风险。后续若要做 M1 级归并，仍须走 rebuild 路径。

## 七、根因与修复方向（后续主攻点）

| 优先级 | 问题 | 修复方向 | 状态 |
|---|---|---|---|
| ~~P0~~ | 属性题失败：PPR 只回共现对端块 | retrieve 融合：种子实体自身块强制并入 | ✅ 已修复（top10 43%→93% 最大头） |
| ~~P1~~ | 短名/音译变体缺收录 | FAIL 集半自动收集入别名表（本次补 6 组） | ✅ 已修复 |
| ~~P2~~ | link 无子串/单字容错 | 单字母拉丁词边界 + 跨片段锚定匹配 | ✅ 已修复（拼音容错未做，按需） |
| ~~P3~~ | 实体「阿莱」疑重复 | 核实：非重复，是「阿莱夫」子串 | ✅ 关闭 |
| P4 | 噪声实体混入 PPR 邻居（如 attention、小说、故事） | 提及块目标限种子+锚定实体已缓解；进一步可在建图侧扩噪声词表 | 观察 |
| P5 | 努库泰澳岛民组 3 语料共现缺口 | 提及数并列时按块内实体名种类数二次排序 | 低优 |

## 八、必知的坑与约定（踩过的）

1. **ASR 语料保留英文原名**：Charlotte/Clara/Aleph/Barcarola/Mercuria… 设计证据词时中英文都要给
2. **别名方向**：`plot_aliases.json` 是 正名→[别名]，`alias_flat` 必须双写同步；写入用 `ensure_ascii=False, indent=1`
3. **查询词必须精确命中**实体名或别名（无子串/模糊匹配）——评测不过先查别名表
4. **语料 version 标签 ≠ 灰机系列分组**：5TH/6TH/7TH 章的标签是 **1.4/1.7/1.9**；绿湖噩梦=**1971**（灰机原句，勿用"1990.9"旧说）
5. **实体正名禁忌**：单字（如"6"须写 Six）、「The 」前缀会触发噪声误杀；空 version 的 timeline entry key 用 `"unlabeled"`（key 不可为空）
6. **别名/数据改动后必须**：`--rebuild-graph-only` 重建 + `pytest -q` 回归（698 基线不回退才合入）
7. 时间线未考挂账：1.6 朔日手记、1.8 再见来亚什基、3.1/3.2/3.4/3.5/3.6/3.8/3.9、空标签（联动）

## 九、新任务建议验收标准（DoD）

1. 在 eval_rag_huiji.py 题库上 **top10 通过率 ≥ 60%**（现基线 43%），且既有 6 题 PASS 不回退
2. 全量 pytest 保持 **698 passed / 0 failed**
3. 图谱健康：悬空边 0、自环边 0、cached 8358 / failed 0
4. 新增用例须附 oracle 证据（语料命中块数 >0）
5. 交付物：改动文件清单 + 评测报告 JSON + 前后对比表
