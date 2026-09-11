# 无名者 · 桌面宠物（desktop/）

roleplay-ai 网页版的**桌面附属形态**：一个 Electron「薄壳」，把网页版自己的页面
`http://127.0.0.1:8000/pet.html` 装进透明、置顶、点击穿透的悬浮窗里。
**对话 / Live2D / 情感 / 语音全部复用网页版现有代码**（`frontend/js/*` 与 FastAPI 后端），
本目录只实现浏览器做不到的能力。

> 设计文档：`../docs/DESKTOP_PET_DESIGN.md`（v0.2）

## 能力清单

| 能力 | 实现位置 |
|---|---|
| 透明无边框置顶悬浮窗 | `src/main/windows.js` |
| 点击穿透（模型/气泡命中测试切换） | 主进程 `pet:interactive` + `frontend/js/pet.js` 命中测试 |
| 左键拖拽移动窗口 + 惯性/回弹 | `frontend/js/live2d.js`（fixedModel 模式）→ `src/main/physics.js` |
| 自主漫步（随机行走，频率可配） | `src/main/behavior.js` |
| 右键菜单 / 气泡 / 设置抽屉 | `frontend/pet.html` + `frontend/js/pet.js` |
| 对话（强制本地 Ollama） | 复用 `RoleplayChat.send` + 请求级 `llmOverride`（`pet.js`） |
| 语音输入（按住说话 Alt+Space / 菜单） | 主进程 `globalShortcut` → 复用 `RoleplayVoice`（本地 faster-whisper） |
| 语音输出（中英文音色/语速） | 复用 `RoleplayVoice`（edge-tts / Web Speech 兜底） |
| 屏幕识别评论（截图 + OCR + Ollama 评论） | `src/main/ocr.js`（tesseract.js + 内置 chi_sim/eng 语言包） |
| 后端探活/自动拉起/重试 | `src/main/backend.js` + `src/renderer/fallback.html` |
| 网页按钮唤起（协议 + 回环服务） | `src/main/control-server.js` + `frontend/js/desktop-pet.js` |

## 快速开始

```bash
# 0. 前置：网页版后端可运行（本壳会自动拉起，也可先手动起）
#    cd .. && .venv\Scripts\python -m uvicorn roleplay.main:app --port 8000   （PYTHONPATH=src）

# 1. 安装依赖（含 Electron；首次较慢）
cd desktop
npm install

# 2. 运行桌面宠物（悬浮窗）
npm start
```

- 宠物窗默认出现在主屏右下角；左键按住拖动（松手有惯性回弹），右键打开菜单。
- `Alt+Space` 按住说话（按下开始录音，再按结束；识别文本自动发给本地 Ollama）。
- 网页版顶栏「🖥️ 桌面宠物」按钮可探测/唤起本应用（先 ping 回环服务，再走 `roleplaypet://launch` 协议）。
- 后端未启动时宠物窗显示引导页，可一键拉起 uvicorn 或重试。

## 配置（userData/config.json）

首次运行自动生成（默认值见 `src/main/config.js`），常用项：

```jsonc
{
  "petUrl": "http://127.0.0.1:8000/pet.html",
  "backend": { "autoStart": true, "port": 8000, "repoPath": "", "python": "" },
  "pet": {
    "width": 420, "height": 560,
    "alwaysOnTopLevel": "floating",   // floating | screen-saver（压全屏）
    "walkEnabled": true, "walkMinMs": 10000, "walkMaxMs": 30000
  },
  "ptt": { "key": "Alt+Space" },
  "ocr": { "autoMode": "off", "lang": "chi_sim+eng", "keywords": ["error","错误","失败","警告"] }
}
```

- `backend.repoPath` / `backend.python`：开发态自动探测（desktop/ 上级即仓库根 + `.venv`）；打包安装后需手工填写。
- 宠物页设置抽屉（右键 → ⚙️ 设置）管理：Live2D 模型 / 缩放 / Ollama 模型与地址 / 温度 / 自动朗读 / 静音（存浏览器 localStorage）。

## 打包（NSIS）

```bash
npm run dist        # 默认源（GitHub，可能较慢）
npm run dist:cn     # 国内网络：npmmirror 镜像源（推荐）
# 产物：dist/*.exe；安装后：
#  - 注册 roleplaypet:// 协议（网页按钮可直接唤起）
#  - extraResources 内置 OCR 语言包（chi_sim + eng，离线可用）
```

> 若首次 `npm install` 时 Electron 二进制下载缓慢，可手动用镜像下载后解压到
> `node_modules/electron/dist`（并写 `path.txt` = `electron.exe`），
> 或设置 `ELECTRON_MIRROR=https://npmmirror.com/mirrors/electron/` 后重新安装。

## 安全与隐私

- 全部网络请求仅限回环（主进程 webRequest 兜底拦截非 127.0.0.1/localhost 请求）。
- 渲染层 `contextIsolation + sandbox`，preload 只暴露白名单 `petApi`。
- 屏幕截图/OCR 文本/录音**只在内存流转**，零落盘、零上传（日志只记字符数）。
- 麦克风是唯一放行的浏览器权限。

## 已知边界

- Live2D 素材无行走循环 → 漫步 = 窗口滑动 + 轻动作伴随；素材库另有 Spine 小模型
  （`2026-07-26-22-28-10/viewer-data/03_动态资源/Spine战斗/…/314701_wmz_s_room.skel`，
  含 `target*` 移动动画与 46+ 房间动作），后续可作双渲染器接入（见设计文档 §2.1）。
- `Alt+Space` 与部分输入法冲突时可在配置里改 `ptt.key`。
- 点击穿透采用近似包围盒命中；如需像素级命中，可给 `live2d.js` 增加 `getModelBounds()` 后替换 `pet.js` 的 `computeInteractive`。
