# QQ 通道 · 历史编年史

> 本文件由 **79 份历史过程档**合并而来（2026-09-29 整理）。
> 收录原则：已完成的一次性报告（审计 / 实验 / 验收 / 阶段总结）。
> **当前权威文档仍以独立文件形式保留**，见 `docs/README.md` 索引。
>
> 原文未丢失：删除前快照在 git 标签 `backup-pre-testdocs-cleanup`，
> 且每条下方记录了来源路径与 SHA-16，可用 `git show <tag>:<path>` 找回。

---

## — · QQ 渠道接入（NapCatQQ / OneBot v11）

- 来源：`docs/qq/QQ_INTEGRATION.md`
- SHA-16：`6690c71b2a8bbf74`

**要点**

- **私聊**：用另一个号私聊小号，发一句话 → 应收到角色回复。
- **群聊**：在群里 @小号 说一句话 → 应回复；普通群消息不回（因 `GROUP_AT_ONLY=true`）。

