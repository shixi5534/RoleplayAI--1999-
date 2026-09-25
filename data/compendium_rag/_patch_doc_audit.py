# -*- coding: utf-8 -*-
"""把交接审计工具与结论补进交接文档。"""
from pathlib import Path

p = Path("docs/COMPENDIUM_RAG_SESSION2_HANDOFF.md")
s = p.read_text(encoding="utf-8")

old_row = "| `_check*.py` / `_fix*.py` / `_deself*.py` | 一次性排查/修补脚本,保留备复核 |"
new_row = (old_row + "\n"
           "| `_audit_handoff.py` | **交接完整性审计**(零网络只读):核对每个 batch 文件的 key 是否都已入 cache |")
assert old_row in s
s = s.replace(old_row, new_row, 1)

anchor = "## 标准收尾流程(每次刷新图谱/索引/评测时照此执行)"
audit = """## 🔍 交接完整性审计(本会话末次运行,结论:通过)

```powershell
& $py data/compendium_rag/_audit_handoff.py
```

用途:捕捉「**已生成 batch 但从未 submit**」的悬挂产物——这类遗漏会让接手者
以为某段已抽完,实际图里没有。

**本会话末次实测结果**:

- batch 文件 **136 个**,batch 内 key 总数 **1658**,唯一 key **1658**,跨文件重复 **0**
- cache 文件 **1659**
- ✅ **所有 1658 个 batch key 均已落入 cache,无悬挂产物**
- 另 1 个 cache key(`10b36a07a53097d94ac1f625` = `mainline__110_复乐园:8.2.0`)
  不出现在任何 batch 文件里,但**内容完整(11 实体/6 关系)且已被计入已抽**
  (复乐园 93/93 闭环)——属早期轮次的产物记录缺失,**数据无影响**。
- 算术自洽:1659 = 1658 + 1。

> 结论:**抽取产物与 batch 记录一致,交接无静默遗漏。**

""" + anchor
assert anchor in s
s = s.replace(anchor, audit, 1)

p.write_text(s, encoding="utf-8")
print("patched; lines =", s.count("\n") + 1)
