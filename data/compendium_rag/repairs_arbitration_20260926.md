# 图谱修复仲裁记录（R1+R2）— 2026-09-26

> 依据：作战书 §2.2（仲裁规则）与 §2.3。裁决人：主会话编排者（非任何修复者，满足"修复者永不复核自己"）。
> 输入：R1 复核（`repairs_v1/verification.json`，20/20 agree）+ R2 复核（`repairs_v2/verification_by_r1repairer.json`，71/71 agree）。

## A. R2 三个 open question 的裁决

| # | 议题 | Verifier 裁决 | 仲裁结果 | 理由 |
|---|---|---|---|---|
| 1 | 保罗 keep vs qualify→保罗·霍伊默尔 | **QUALIFY**（DF92 中 66 块为圣保罗城市碰撞；R265 的卡戎 0.9 为错种子，qualify 反而改善 R265） | **采纳，执行推迟至 R3** | R2 schema 无 add_alias 类型（qualify=remove 保罗 + add 保罗·霍伊默尔 两步）；本轮不临时扩 schema，R3 以正式条目执行。提案原"零影响"表述由复核修正为" qualify 改善 R265" |
| 2 | 重塑 keep vs remove | **KEEP**（remove 对测试集中性，但独立用法真实存在：155 块、70 块在属主声称之外，如「重塑的势力正逐年剧增」；提案的 327/506 论证被指循环，独立-155 才是可靠依据） | **采纳 KEEP** | 与提案的 keep_with_note 结论一致，理由换为更硬的独立-155 |
| 3 | 纯离线 wiki 裁决是否合规 | **ACCEPT**（Cloudflare 403 与 WAF 封禁记录一致；拒绝浏览器 bootstrap 正确；关键 wiki 事实均离线可裁且被抽查核实） | **采纳** | 记入披露清单 |

## B. R1 边算术终判（29959 vs 29960）

- R1 提案报告与独立 Verifier 均得 **29959**；Applier 首版干跑得 29960（merge/move 产生 1 条同三元组重复边未去重）。
- 裁决：**29959 为准**（图规范零重复边——质检结构项基线即零重复）。Applier 已加后置边去重（union chunk_ids / 拼接 evidence / confidence 取 max），修正后干跑 = 29959 ✓。
- 29959 = 29967 − 7（delete_edge 伪边）+ 0（move/merge 不改总数，去重吸收 1 条 merge 重复）。

## C. 跨版本幂等重叠

- **别斯米尔@卡卡尼亚**：R1-E05-03 与 R2 各删除一次（语义互补：都从错属主摘除；R1 另加别斯米尔→探险家别斯米尔）。按 §2.4 规则 3 记"已由前版删除"警告，应用一次，不报错 ✓（组合干跑实测）。
- 除该 1 条外，R1×R2 的 remove_alias 集合零交集；R1 add_alias 与 R2 keep_with_note 零冲突（脚本核算）。

## D. 验证方式披露（协议偏差如实记）

- R2 验证 = 轮换制（R1 修复者复核 R2）✓ 作战书本意。
- R1 验证 = 全新独立代理（非轮换的 R2 修复者——其 SendMessage 恢复失败：ID 不在活跃表）。协议硬规则"修复者永不复核自己"满足（R1 修复者未参与 R1 复核）。
- 独立 R2-Verifier（全新代理）首轮死于验证码，重发后未见完成通知——R2 的验证以轮换复核为准（已闭合），如该代理后续产出将并入证据但不作依赖。

## E. Verifier 非阻塞备注（记录，不拦落盘）

1. R1 提案 md 三处"兴尔德"→"兀尔德"笔误（proposal.json 字段正确）。
2. E03/E09 "65 逐字"应为 66。
3. E06 evidence 数组引用 110:19.0.0 应为 106:5.1.0（final_chunk_ids 正确）。
4. R2 复核：玛丽 in_owner_claims 计主属主（并集 29 非 1）；3 处 verbatim_aliases_left 列表截断；基金会 bare 依赖 7 条非 5 条；死别名 78→77 为 itemscope 口径（全索引口径 1167→1166，结论同）。

## F. 落盘执行记录

- 组合干跑（v1+v2=91 条）：预检 0 错 / 警告 2（inferred alias + 幂等重叠）/ 后检 0 错；实体 7033→7034、边 29967→29959。
- `--apply --version-tag r1r2`：备份 `backups/graph.json.prev.r1r2` → 新图 7034/29959；`cli stats` fingerprint **OK**（别名/实体/边层不触指纹，SESSION2 §7 语义）；结构复检通过。
- 后续：索引重建（新实体名向量）→ 新基线 eval300 → 胜者策略复验 → 题集 i spot → 闸门判定 → 补遗四。
