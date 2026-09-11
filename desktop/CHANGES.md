# 桌面宠物 · 变更记录

## v0.2.0（2026-08 优化轮）

### 修复

- **舞台容器 ID 错配**：`pet.js` 误取 `#live2d-canvas`（宠物页实际是 `#pet-canvas`），
  导致渲染器就绪前的命中测试兜底抛异常、右键「分享截图」永远失败。
  已修正并加注释，分享截图与点击穿透兜底恢复可用。
- **渲染器切换 WebGL/ticker 泄漏**：`RoleplayLive2D` 此前没有 `destroy()`，
  Spine⇄Live2D 来回切换会残留孤儿 PIXI App（60fps ticker 空转 + 双 WebGL 上下文）。
  新增 `destroy()`（停 ticker、解绑 resize/拖拽、销毁 App 并移除画布）。
- **多显示器屏幕识别错位**：OCR 截图固定取主屏源 + 主屏尺寸，副屏上光标区域裁剪错位。
  改为按 `display_id` 匹配光标所在显示器，裁剪坐标以该显示器工作区为基准（含 DPI 缩放换算）。
- **手动「识别屏幕」无反馈**：无关键词命中时文本被丢弃，宠物毫无反应。
  手动模式（`manual: true`）现在无条件回传 OCR 文本，由宠物评论。
- **锁位不锁漫步**：锁位只守卫了拖拽 `moveBy`，自主漫步仍会移动窗口。
  `behavior.js` 在漫步前实时读取配置，锁位 / 跟随光标模式下不再自主移动。
- **忙碌状态竞态**：录音/对话/拖拽交错结束时，`pet:busy` 的 last-write-wins 会让漫步过早恢复。
  改为主进程引用计数 + 600ms 延迟恢复；Spine 拖拽与语音聆听只置位一次 busy（防计数泄漏）。
- **网页按钮无法正常唤醒桌面宠物**：`desktop-pet.js` 在 `await` 之后才触发
   `roleplaypet://` 协议，Chrome 会因用户手势失效而拦截；同时 `/launch` 只显示窗口，
   不会把睡眠中的宠物页唤醒。改为每次点击都同步触发协议（保留用户手势，直接唤起），
   并新增 `pet:wake` IPC：网页按钮唤起时主进程通知宠物页 `noteActivity()`，
   窗口重新聚焦/可见时也会自动唤醒。
- **开发态无法从网页直接拉起桌面端**：仅靠 `roleplaypet://` 协议在未注册/未安装时不可用。
   新增本地后端兜底 `POST /api/desktop-pet/launch`：网页按钮在协议失败后由同机 FastAPI
   直接 `npm start` 拉起 Electron 壳；同时新增本地文档路由，安装引导直接打开仓库内
   `docs/DESKTOP_PET_DESIGN.md`，不再跳转外部地址。

### 优化

- **空闲分级接入 Live2D**：`sleep(0|1|2)` 驱动 ticker 降帧（浅睡 30fps / 深睡 12fps，
  深睡停待机动作池），互动即恢复 60fps；与宠物页既有 90s/5min 空闲分级联动。
- **窗口位置 / 档位持久化**：拖拽释放、显式摆位（多屏/复位）、改档位、退出时写入
  `userData/config.json`，重启回到原处；存盘位置越屏自动钳制到最近显示器工作区。
- **漫步方向反馈**：主进程漫步事件携带位移方向，Spine 人偶按方向镜像（朝左/朝右走）。
- **版本号单一事实来源**：回环控制服务 `/ping`、`/state` 的版本读 `package.json`。
- **语音聆听统一入口**：菜单「语音对话」与 Alt+Space 共用 `startListening/stopListening`
  （聆听表情、busy 引用计数、结束恢复表情/漫步一致）。

### 涉及文件

- `frontend/js/pet.js`
- `frontend/js/live2d.js`
- `desktop/src/main/index.js`
- `frontend/js/desktop-pet.js`
- `desktop/src/preload/pet.js`
- `desktop/src/main/windows.js`
- `src/roleplay/api/desktop_pet.py`
- `src/roleplay/main.py`
- `desktop/src/main/behavior.js`
- `desktop/src/main/ocr.js`
- `desktop/src/main/control-server.js`
- `desktop/package.json`（0.1.0 → 0.2.0）

> 注：`desktop/README.md` 因沙箱对既有 Markdown 文档的写保护未能同步更新，本文件为替代记录。
