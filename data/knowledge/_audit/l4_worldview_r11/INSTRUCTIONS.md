# L4.4 世界观定义互斥一致性评分说明（重新盲评 · 审查子代理）

> 本目录是一次**重新盲评**的输入。判定口径（verdict 词汇、字段名、判定标准）与历史上
> 跑出 `unity=0.9425` 的那一次**逐字一致**；唯一差别是 `definition_edges` 取自**新图**
> （图指纹 `911bb538160db80e`）。两次读数之差才是"修边"的效果，所以**不要改口径**。
>
> **禁止**参考其它臂目录下的任何旧文件（见文末禁令）。

你是**独立审查员**。任务：对每一个概念，判断**知识图谱给它的描述（desc）与它的定义边之间
是否自相矛盾**。你不需要懂这款游戏，判定只依据手上给到的输入。

## 输入
`data/knowledge/_audit/l4_worldview_r11/wv_bNN.json`（NN 与你的批号一致）：
```json
{"schema":"audit.l4_worldview_review_input/v1","batch":"b01",
 "items":[{"concept":"…","type":"概念","desc":"…","aliases":["…"],
           "definition_edges":[{"dir":"out","relation":"象征","canonical":"象征",
                                "counterpart":"启示","evidence":"原文短句",
                                "chunk_id":"…"}]}]}
```
- `desc`：图谱里该概念的描述（可能很短，本身也可能就是错的——这正是要查的）。
- `aliases`：该概念的别名清单（判定"是"的对象是否只是同一事物的另一种叫法时可用）。
- `definition_edges`：图谱从全库抽出的、能把 `concept` **定义成什么**的关系边。口径：
  只保留 `canonical ∈ {是, 象征, 包含, 隶属, 影响}` 的边，按图内边序取前 12 条。
  - `dir="out"` 读作 `concept --relation--> counterpart`；
  - `dir="in"`  读作 `counterpart --relation--> concept`。
  - **数组的 0 基下标就是 `conflicting_edges[*].index` 要填的序号。**

## 判定标准（verdict）
把每个概念判成三者**之一**：
- **`consistent`**：desc 与定义边自洽，没有互斥定义。
- **`mutually_exclusive`**：同一概念被**同时定义成 A 与 非A**，或同一个 counterpart
  既被说成"就是它"、又被说成"是另一个 / 另一天 / 另一件东西"。典型形态：
  - `X --是--> A` 与 `X --是--> B`，而证据语境里 A、B 明确不是一回事；
  - `A --是--> X` 与 `A --是--> Y`，把 X、Y 当成同一件事，但原文说 X 是 Y 的次日；
  - 同一个 counterpart 上 `隶属` 与 `象征` 并存且语义冲突。
  **不构成互斥**（不要判 mutually_exclusive）：单边的 `隶属`/`象征`；`是` 的两端互为别名；
  几条边彼此独立、不指涉同一对象；只是"关系稀疏/看起来不够定义"。
- **`insufficient`**：**给到的定义边不足以判定**该概念（例如只有单边且证据是旁白/失败台词、
  与概念的定义无关；`definition_edges` 为空时一律判此值）。
  判 `insufficient` 的条**会移出判分母**——所以只在边确实不定义该概念时使用，
  不要用它来回避没把握的判断。

## 输出
写到 `data/knowledge/_audit/l4_worldview_r11/wv_bNN_review.json`（NN 与输入批号一致）：
```json
{"schema":"audit.l4_worldview_review/v1","batch":"b01",
 "reviews":[{"concept":"…",
             "verdict":"consistent",
             "conflicting_edges":[{"index":2,"why":"≤30 字"}],
             "constraint_risk":0.1,
             "notes":"≤40 字判据"}]}
```
- `verdict` **必须逐字**取 `consistent` / `mutually_exclusive` / `insufficient` 三者之一
  （大小写与下划线都要一样），否则本轮 `unity` 复算不出来；
- `conflicting_edges`：只有 `mutually_exclusive` 时非空，`index` 为上面 `definition_edges`
  的 **0 基下标**（历史臂写作 `idx`，也接受），`why` ≤30 字；其余 verdict 写 `[]`；
- `constraint_risk`：0.0~1.0 浮点，你对"该概念后续会造成世界观冲突"的风险估计
  （**不参与 unity 计算**，只做留痕）；
- `notes`：≤40 字判据；
- 一条 concept 都不能少；**每评完 5 条立刻用当时已有的全部结果覆盖落一次盘**，防中断丢失；
- 收尾自查：`reviews[*].concept` 集合 == 输入 `items[*].concept` 集合（本臂共 90 条，
  拆成 6 批、每批 15 条）。

## 复算口径（写给你自查，不要改）
设你的输出为 R：
- `n_insuff = |{r ∈ R : r.verdict == "insufficient"}|`
- `n_excl  = |{r ∈ R : r.verdict == "mutually_exclusive"（或 r.mutually_exclusive 为真）}|`
- `n_judged = |R| - n_insuff`
- `unity = round(1 - n_excl / max(1, n_judged), 4)`，gate = `unity ≥ 0.95`

即：**`insufficient` 的条移出分母；每一条 `mutually_exclusive` 扣 1/n_judged。**

## 禁令
- **禁止**读取仓库里的其它任何文件（图谱产物、评测集、gold、别人的 review 都不许看）；
  只能打开本说明文件和你自己的输入批次文件。
- **特别禁止**打开：`data/knowledge/_audit/l4_worldview_review.json`（历史判分，
  它是本轮要对照的基线）、本目录下的 `arm_map.json` 与 `baseline_unity.json`
  （含基线读数，属泄漏）、以及 `../l4_multiscene*/`、`../l4_privacy*/` 等其它臂下的任何
  `*_review.json`。看了就不再是盲评。
- 判分要敢给低分，也要敢给满分：把"看起来合理"当成"有依据"是放水，
  把"边太少"当成"互斥"是口径错位。
