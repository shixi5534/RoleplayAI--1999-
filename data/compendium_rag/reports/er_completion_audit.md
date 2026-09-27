# ER 阶段3 完成度审计（可重放）

生成命令：`PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe scripts/_er_audit_completion.py`（离线只读、全量范围三题集；退出码 0=全 PASS、1=有 FAIL、2=有 PENDING）
本次运行退出码：**0**（2026-09-26，300_cn 映射档落盘后）。判据 E 为已披露项（native 2 行非盲），非 PASS 也非 FAIL。

| 判据 | 结论 | 复算依据 |
|---|---|---|
| A 铁律#1 零网关（6 个路线脚本无网络端点） | PASS | 全部无命中 |
| A2 graph.json 可加载 | PASS | 实体 7033 / 名字键 7033 |
| B native 阶段1：T1/T1r 覆盖=100% 且 truncated=0 | PASS | T1 84/84 cov=1.0；T1r 83/83 cov=1.0；truncated=0 cap=400 |
| B [native] 候选名全部 ∈ graph（白名单源头合法） | PASS | 14046 个候选名逐 token 校验 |
| C [native] 阶段2：解析率≥90%（token 口径，独立回算）+ map 全量合法 | PASS | 原始 215 行 → 提议 255 token、保留 250 ⇒ **token 解析率 0.9804**；题级全合法率 0.9767；map 题 215 / 非空 207 / 名 250；违例 白名单 0 resolve 0 |
| D [native] 阶段3 zero 档（口径身份+grounded+逐位） | PASS | map字段=none 行数=500 grounded全1.0=True / 基线 500 行，逐位差异=0 |
| D [native] 阶段3 map 档（口径身份+grounded+逐位） | PASS | map字段=entity_map_native.json 行数=500 grounded全1.0=True |
| B [300_cn] 候选名全部 ∈ graph（白名单源头合法） | PASS | 19584 个候选名逐 token 校验 |
| C [300_cn] 阶段2：解析率≥90%（token 口径，独立回算）+ map 全量合法 | PASS | 原始 300 行 → 提议 75 token、保留 73 ⇒ **token 解析率 0.9733**；题级全合法率 0.9933；map 题 300 / 非空 72 / 名 73；违例 白名单 0 resolve 0 |
| D [300_cn] 阶段3 zero 档（口径身份+grounded+逐位） | PASS | map字段=none 行数=600 grounded全1.0=True / 基线 600 行，逐位差异=0 |
| D [300_cn] 阶段3 map 档（口径身份+grounded+逐位） | PASS | map字段=entity_map_300_cn.json 行数=600 grounded全1.0=True |
| B [i] 候选名全部 ∈ graph（白名单源头合法） | PASS | 44287 个候选名逐 token 校验 |
| C [i] 阶段2：解析率≥90%（token 口径，独立回算）+ map 全量合法 | PASS | 原始 287 行 → 提议 713 token、保留 711 ⇒ **token 解析率 0.9972**；题级全合法率 0.993；map 题 287 / 非空 279 / 名 711；违例 白名单 0 resolve 0 |
| D [i] 阶段3 五臂齐全 + grounded=1.000 + 非 partial | PASS | 臂=['alias', 'empty', 'random', 'strong', 'vector'] modes=['full', 'graph_only'] n_cases=287 partial=False grounded全1.0=True |
| D [i] L1 主闸独立回算（hit@10, full, n=T1） | PASS | strong=0.9459 Δempty=+2.16pt(b=7,c=3,p=0.34375) Δrandom=+5.41pt(b=13,c=3,p=0.02127)；打印值 Δempty=2.16 Δrandom=5.4 up=['i053', 'i076', 'i087', 'i157', 'i168', 'i227', 'i334'] down=['i141', 'i228', 'i285'] |
| D [i] graph_only 机理证据独立回算（纯符号通道 strong−empty hit@10） | PASS | empty=0.7730 → strong=0.8703 = +9.73pt（发布值 +9.73pt） |
| D [i] §4「strong 两模式全指标居五臂之首」回算 | PASS | full/hit6:strong full/hit10:strong full/rr:strong graph_only/hit6:strong graph_only/hit10:strong graph_only/rr:strong |
| E 盲性披露（识别记录中自述见过 gold 的行） | DISCLOSED | native: ['N038:# seen_gold(截断诊断时见过)', 'N055:# seen_gold(截断诊断时见过)'] |
