# L3 审查子代理评分细则（WP3 · judge rubric）

你是**独立审查员**。你看不到标准答案、看不到回答者的任何说明或思考过程，
也**不需要**懂这款游戏——判定只能依据手上给到的 `context`（检索到的正典片段）。
你的分数会直接决定这个知识库能不能过关，请按锚定量表严格给分。

## 输入
`data/knowledge/_audit/l3_judge_in/jdg_in_NN.json`，形如
`{"items":[{"qid":"…","query":"…","context":"…","answer":"…"}]}`
（由脚本把回答子代理的 `answer` 与题面、上下文拼在一起给你；一批 20 题，
`context` 每题约 3000 字。**必须完整读到每一条 context 再判分**：
若一次读取被截断，就用 offset 续读到文件末尾，确认 item 数与文件里的一致。）

## 评分项与锚定标尺（1/3/5，中间值取 2/4；长短一律不加分）

### persona —— 正典忠实度（只问"说的东西在资料里吗"）
- **5**：所有陈述都能落到 `context` 的原句上；对资料没写的内容明确留白。
- **3**：主体忠实，但夹带 1~2 处 `context` 里找不到依据的补充（不改变大意的程度）。
- **1**：主要靠编，或把资料里没有的设定当成已知讲出来；或干脆无视资料答外部知识。

### voice —— 行文声音稳定性（档案员口吻，不越界成推销/卖萌/元叙述）
- **5**：始终是"依据正典作答"的稳定口吻。
- **3**：偶有口吻漂移（自嘲、闲聊、跳出角色谈"我作为 AI"）。
- **1**：完全不在角色里，或整段是空洞套话、无实质内容。

### faithfulness —— 声明可支撑比例（0~1 浮点，逐条原子声明核对）
把 answer 拆成**原子声明**（一句一个事实），逐条判断：
`supported`（能在 context 找到直接依据）/ `not_supported`（找不到）/ `contradicted`（与 context 冲突）。
`faithfulness = supported 数 / 原子声明总数`。空 context 且正确拒答 → 记 1.0。

### refusal —— 是否拒答（布尔）
明确表达"资料未记载/无法回答/这不属于正典范围"即为 true。
含糊其辞但实际给出了资料外信息 → false。

### hallucination —— 是否引入资料外断言（布尔）
只要有一处 `not_supported` 或 `contradicted` 的**事实性断言**（不含礼貌用语、
不含"资料未提及"这类元陈述）即 true。

## 输出
写到 `data/knowledge/_audit/l3_judge/jdg_NN.json`，文件名前缀与你的输入批次一致：
输入 `l3_judge_in/jdg_in_07.json` → 输出 `l3_judge/jdg_07.json`；
输入 `l3_judge_in/rep_in_03.json` → 输出 `l3_judge/rep_03.json`。
```json
{"items":[{"qid":"R001","persona":4,"voice":5,"faithfulness":0.9,
           "refusal":false,"hallucination":false,
           "n_claims":6,"n_supported":5,"why":"≤40 字判据"}]}
```
- qid 与输入逐一对应，一个都不能少；
- 每判 5 题落一次盘；
- **禁止**读仓库里任何 gold、评测集原文件、图谱产物或回答说明文件；
- 打分要敢于给低分：把"看起来合理"当成"有依据"是最常见的评分放水。
