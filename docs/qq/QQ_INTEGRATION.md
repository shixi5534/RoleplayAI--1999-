# QQ 渠道接入（NapCatQQ / OneBot v11）

让一个 QQ 号（建议**小号**）通过 NapCat 协议端登录，把消息转成标准 OneBot v11 协议交给
roleplay-ai 处理，回复再发回 QQ。roleplay-ai 的大脑（人设卡 / RAG / 情感 / 会话记忆）全部复用，
本功能只是在外面套了一个"QQ 渠道适配器"。

> ⚠️ 协议端登录 QQ 属灰色地带，存在被风控（设备验证 / 限流 / 临时封）的可能。
> **务必用小号**，不要把主号拿来登录 NapCat。

---

## 1. 安装 NapCat（本机，仅需一次）

1. 打开 <https://github.com/NapNeko/NapCatQQ/releases>，下载 Windows **一键包**（如 `NapCat.Windows.Onekey.zip`）。
2. 解压，双击运行 `NapCatInstaller.exe` 完成安装，然后运行目录里的 `napcat.bat`。
3. 控制台会提示**扫码登录**——用手机 QQ 扫那个码，登录你的**小号**。
   - 登录后会缓存 session，之后重启 NapCat 可自动登录（"快速登录"）。
4. WebUI 默认地址 `http://127.0.0.1:6099/webui?token=XXX`（token 看控制台输出）。

## 2. 在 NapCat WebUI 里开一个正向 WebSocket

1. 进入 WebUI → 左侧 **网络配置** → **新建** → 选 **OneBot v11 WebSocket 服务（正向）**。
2. 端口填 `3001`（与下面的 `ROLEPLAY_QQ_NAPCAT_WS_URL` 一致）；其它默认。
3. 如需鉴权，记下 token（填到 `ROLEPLAY_QQ_WS_TOKEN`），否则留空。
4. 保存并打开右侧开关。此时 NapCat 已在 `ws://127.0.0.1:3001` 监听。

> 正向 = 我们的后端主动连 NapCat。反向（NapCat 连后端）也行，但正向最简单。

## 3. 配置 roleplay-ai

在 `.env`（或环境变量，前缀 `ROLEPLAY_`）里加：

```ini
ROLEPLAY_QQ_ENABLED=true
ROLEPLAY_QQ_NAPCAT_WS_URL=ws://127.0.0.1:3001
ROLEPLAY_QQ_WS_TOKEN=            # 与 NapCat 配置一致；空=不鉴权
ROLEPLAY_QQ_BOT_UIN=             # 机器人QQ号；空则启动时自动获取
ROLEPLAY_QQ_ADMIN_UIN=           # 你的主号（指令权限）；空=指令对所有人开放
ROLEPLAY_QQ_CHARACTER_ID=        # QQ 上扮演的角色 id；空=当前激活角色
ROLEPLAY_QQ_GROUP_AT_ONLY=true   # 群内仅 @机器人 才回复
ROLEPLAY_QQ_COMMAND_PREFIX=!
ROLEPLAY_QQ_ALLOW_FROM=          # 私聊白名单（逗号分隔QQ号）；空=允许所有人
```

然后正常启动服务：

```bash
start_server.bat        # 或 uvicorn roleplay.main:app --port 8000
```

启动日志里应能看到：`QQ 渠道任务已启动（NapCat: ws://127.0.0.1:3001）`，
连上后：`QQ 渠道已连接，bot_uin=xxxxx`。

## 4. 验证

- **私聊**：用另一个号私聊小号，发一句话 → 应收到角色回复。
- **群聊**：在群里 @小号 说一句话 → 应回复；普通群消息不回（因 `GROUP_AT_ONLY=true`）。
- **指令**：
  - `!help` 显示帮助
  - `!clear` 清空与你的对话记忆
  - `!char` 查看可用角色；`!char <角色id>` 切换角色

## 5. 风险与注意

- **风控**：用小号；群内仅@才回；不要高频秒回、不要刷屏、避开敏感词；新号先"养一养"。
- **安全**：NapCat WS 只在 `127.0.0.1` 监听，不要暴露到公网；如需远程访问，请走内网穿透并设 token。
- **稳定性**：适配器自带断线重连（指数退避，上限 30s），NapCat 重启后会自动恢复。
- **功能范围（v1）**：仅处理纯文本；图片 / 语音 / 富媒体暂不支持（收到会忽略该部分内容）。

## 6. 实现位置（供排查）

- `src/roleplay/channels/qq_onebot.py` —— OneBot v11 客户端（连接 / 解析 / 发消息 / 指令 / 重连）。
- `src/roleplay/channels/__init__.py` —— 渠道包导出。
- `src/roleplay/config.py` —— `ROLEPLAY_QQ_*` 配置组。
- `src/roleplay/main.py` —— 生命周期启停（`lifespan` 中 `qq_enabled` 时挂 `qq_task`）。
- `requirements.txt` —— 新增 `websockets>=12.0`。
