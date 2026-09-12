# RAG 300 条测试集交接文档（灰机标准 · 新任务接手用）

> 更新：2026-09-12 19:40｜维护人：主会话 Agent
> 上游文档：`docs/RAG测试对接表.md`（环境/接口/坑的权威来源，先读它再读本文）
> 用途：接手测试集维护/扩题/评测时，凭此表直接上手，无需重新踩坑。

---

## 一、一句话现状

《重返未来:1999》「无名者(wu_ming_zhe)」剧情图谱 RAG 已交付 **300 条灰机标准测试集**（seed 14 题逐字保留 + 286 条新题），全部经 oracle 校验（证据命中块数 >0），维度配额精确命中；seed 14 题 top10 实测 **13/14 = 93%**（P0 检索融合修复已生效，对接表 43% 基线已成历史）。

## 二、交付物清单（5 个文件）

| 文件 | 作用 | 现状 |
|---|---|---|
| `data/knowledge/_audit/rag_testset_300.json` | **300 条机读题库（权威版）** | q/ref/evidence/id/dims/oracle_min_blocks/source 七字段齐全 |
| `data/docs/rag_testset_300.md` | 人可读全量表（按题型分节） | 300 行，与 JSON 一致 |
| `data/knowledge/_audit/rag_testset_300_rejected.json` | oracle 剔除记录 | 6 条 0 命中题 + 剔除原因 |
| `scripts/gen_rag_testset_300.py` | 生成管线（选题+oracle 校验+三件套输出） | 幂等（连跑 3 次 md5 一致），exit 0=凑齐 / 2=缺口 |
| `scripts/rag_testset_candidates_300.py` | 候选题池 | 455 条（14 seed + 345 人工题 + 96 别名自动题） |

## 三、常用命令

```bash
# 重新生成 300 条（幂等，不改语料/图谱，只写 _audit 三件套 + md）
./.venv/Scripts/python.exe -X utf8 scripts/gen_rag_testset_300.py --mode select --target 300

# 单题诊断：查某题干关键词的证据命中块数与块摘要（扩题前必跑）
./.venv/Scripts/python.exe -X utf8 scripts/gen_rag_testset_300.py --mode oracle-only --q "问题关键词"

# seed 14 题基线（与测试集互相独立，改检索策略后跑这个看回归）
./.venv/Scripts/python.exe -X utf8 scripts/eval_rag_huiji.py --top 10
```

## 四、题库字段与维度配额（300 条精确分布）

题库每条结构：
```json
{
  "q": "问题（中文自然口语）",
  "ref": "灰机标准答案",
  "evidence": [["答案关键词组（中英文备选）"], ["题干场景限定词组"]],
  "id": "R001",
  "dims": {"type": "...", "difficulty": "...", "depth": "...", "hop": "...", "chapter": "...", "text_len": "..."},
  "oracle_min_blocks": 21,   // 最弱证据组在 8358 块中的命中块数，全部 >0
  "source": "seed | generated"
}
```

| 维度 | 取值与配额 |
|---|---|
| type | factoid 200 / multi-hop 60 / reasoning 30 / temporal 10 |
| difficulty | easy 150 / medium 100 / hard 50 |
| depth | shallow 170 / medium 80 / deep 50 |
| hop | single 200 / multi 100 |
| text_len | short 100 / medium 120 / long 80 |
| chapter | 1.4=20、1.7=20、1.9=20、1971=20、其他=220（联动/宇宙观/各版本活动） |

设计依据（联网调研结论，2026-09-12）：RAGAS / HieraRAG(arXiv 2606.12789) / HotpotQA / 企业 Golden Set 实践——按 type×difficulty×depth 分层报告指标，才能暴露「简单题全对、难题全崩」的假象；300 条恰在业界 pre-release 建议（300-500）下限。

## 五、扩题 / 改题规则（CRITICAL）

1. **新题先过 oracle**：`--mode oracle-only` 诊断，任一证据组 0 命中 → 不得入库（本次剔除 6 条，记录在 rejected.json，典型如「初级防御学园/恶魔荆棘/青年军」中文词 ASR 语料 0 块）
2. **证据词以英文正名为主**：语料是 ASR 英文转写，中文正名（十四行诗/星锑/牙仙等）正文多为 0 命中，英文拼写必给
3. **组内=备选、组间=必须全命中**；组1=答案关键词，组2+=题干场景限定词
4. **禁用泛词**（时间/世界/发现/the 等黑名单，管线强制校验）
5. **改完候选池必须重跑** `--mode select --target 300`，并核对维度配额——注意配额存在联合耦合，**当前最薄的格是 factoid-D 类 19/19 全用**，从该格抽题前先补员
6. seed 14 题（`eval_rag_huiji.py` 的 CASES）**逐字不可动**；若改了 seed，必须同步改候选池重跑

## 六、已知坑（踩过的，勿重蹈）

1. **自动别名题有噪声**：图谱别名表含 I/he/she/it 等代词，自动出题需停用词+「The 」前缀过滤（本次 96 条自动题被剔 2 条）
2. **章节口径**：1.4=洞穴的囚徒、1.7=今夜星光灿烂、1.9=孤独之歌、1971=绿湖噩梦；语料 version 标签与灰机系列分组不一致（详见对接表第八节第 4 条）
3. **单字/前缀禁忌**：单字实体须写全（"6"→Six）、「The 」前缀触发噪声（同对接表）
4. 评测脚本判分口径 =「top-K 证据块正文并集、每组任一关键词命中」，与 oracle 扫描口径一致，二者可直接互验

## 七、QA 验收结论（2026-09-12，20/20 细目 PASS）

- 300 条复扫 0 无效证据组；oracle_min_blocks 与独立复扫值 100% 一致
- seed 14/14 与 eval_rag_huiji.py 逐字段一致；既有文件零改动（本次交付只有新增）
- 基线：`eval_rag_huiji.py --top 10` → **13/14=93%**，唯余「努库泰澳的岛民」FAIL（既有语料缺口：Nuku* 块与 Salone 块零共现）

## 八、遗留事项与下一步

1. **分桶跑全量基线**（建议下一个任务）：让评测脚本读 `rag_testset_300.json`，按 type/difficulty/depth 分桶报通过率——multi-hop 60 条与 hard 50 条预计是主要缺口，直接指导 P1/P2 修复的优先级
2. 「努库泰澳的岛民」FAIL 待语料侧解决（与对接表 P1 别名补录方向一致）
3. 工作区有存量未提交变更（plot_graph.py 等 M 状态），建议连同本次 5 个新增文件统一提交
4. 候选池 449 条通过题中有 149 条富余，扩题/换题空间充足，但注意第五节第 5 条的薄格约束
