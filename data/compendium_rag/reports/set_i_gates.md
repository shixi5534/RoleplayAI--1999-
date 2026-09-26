# 题集 i 五臂闸门表（full 模式，L1=_pool T1 主口径）

partial=False  n_cases=287

| 臂 | n | hit@6 | hit@10 | MRR | grounded |
|---|---|---|---|---|---|
| empty | 185 | 0.8919 | **0.9243** | 0.661 | True |
| random | 185 | 0.7946 | **0.8919** | 0.5534 | True |
| alias | 185 | 0.8703 | **0.9135** | 0.6278 | True |
| vector | 185 | 0.8432 | **0.8973** | 0.6078 | True |
| strong | 185 | 0.9027 | **0.9459** | 0.7099 | True |

## 闸门

- [ ] L1 全量 hit@10 ≥ 0.70：0.9459
- strong−empty = +2.16pt（需 ≥ +5）；McNemar b=7 c=3 p=0.3438（需 <0.05）
  - up(7): i053, i076, i087, i157, i168, i227, i334
  - down(3): i141, i228, i285
- strong−random = +5.40pt （需 >0，即强模型优于随机）；McNemar vs random p=0.0213
- grounded=1.000 全臂：True

## graph_only 模式（对照，非主口径）

| 臂 | L1 hit@6 | L1 hit@10 |
|---|---|---|
| empty | 0.6432 | 0.773 |
| random | 0.5784 | 0.6703 |
| alias | 0.6486 | 0.7622 |
| vector | 0.6324 | 0.7135 |
| strong | 0.773 | 0.8703 |

## L2（MULTI 2-hop + T2i）仅报告

| 臂 | MULTI hit@10 | T2i hit@10 |
|---|---|---|
| empty | 0.9545 (n=44) | 0.7931 (n=58) |
| random | 0.9091 (n=44) | 0.7069 (n=58) |
| alias | 0.9318 (n=44) | 0.8276 (n=58) |
| vector | 0.9091 (n=44) | 0.7241 (n=58) |
| strong | 0.9545 (n=44) | 0.7759 (n=58) |
