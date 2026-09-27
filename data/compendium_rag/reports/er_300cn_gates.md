# ER 阶段3 闸门 · set=300_cn

- 零档自检：行数 600 / 基线 600 / 对齐 600 → **PASS 逐位复现**，差异 0 行

### full
- all n=300  hit@6 0.5267 → 0.5233（-0.34pt）  MRR 0.4049 → 0.4215  grounded 1.0
- answerable n=196  hit@6 0.801 → 0.7959（-0.51pt）  MRR 0.6147 → 0.6401  grounded 1.0  [主口径：未提升 FAIL]
- unanswerable n=104  hit@6 0.0096 → 0.0096（+0.00pt）  MRR 0.0096 → 0.0096  grounded 1.0  [安全底线：不升 PASS]
- 逐题翻转（full）up=1 ['R142']
- 逐题翻转（full）down=2 ['R022', 'R199']
- 归因检查：映射覆盖题 72 道；up 中被覆盖 1、未覆盖 0；down 中被覆盖 2、未覆盖 0
- McNemar（full，hit@6 逐题配对）b=1 c=2 p=1.00000
- McNemar（full，仅映射覆盖题）b=1 c=2 p=1.00000  ← 补名净效应的配对集（未覆盖题翻转不入场）
- 注：未覆盖题上的翻转=检索随机性/排序噪声，不计入补名效果
### graph_only
- all n=300  hit@6 0.44 → 0.4467（+0.67pt）  MRR 0.3446 → 0.3699  grounded 1.0
- answerable n=196  hit@6 0.6684 → 0.6786（+1.02pt）  MRR 0.5223 → 0.5611  grounded 1.0  [主口径：提升 PASS]
- unanswerable n=104  hit@6 0.0096 → 0.0096（+0.00pt）  MRR 0.0096 → 0.0096  grounded 1.0  [安全底线：不升 PASS]
- 逐题翻转（graph_only）up=6 ['R057', 'R088', 'R142', 'R177', 'R262', 'R280']
- 逐题翻转（graph_only）down=4 ['R021', 'R022', 'R246', 'R289']
