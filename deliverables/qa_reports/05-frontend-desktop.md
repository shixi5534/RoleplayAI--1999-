# 05 前端与桌面端检验报告

> 检验方式：**纯静态只读**。未执行 `npm install`、未启动 Electron、未联网、未修改任何项目文件。
> 环境：Windows / node v24.14.1（`node --check` 可用）。
> 工作目录：`C:\Users\Lenovo\WorkBuddy\2026-07-27-16-45-03\roleplay-ai`
> 范围：`frontend\`（6 个 HTML + css/js/shared/assets）、`desktop\`（src/scripts/配置，忽略 `node_modules`）

---

## 1. JS 语法体检结果

**结论：48 个 JS 文件全部通过 `node --check`，语法错误 0 个。**

| 文件 | 结论 |
|---|---|
| frontend\js\chat.js | ✅ OK |
| frontend\js\desktop-pet.js | ✅ OK |
| frontend\js\knowledge.js | ✅ OK |
| frontend\js\layout.js | ✅ OK |
| frontend\js\live2d-bootstrap.js | ✅ OK |
| frontend\js\live2d.js | ✅ OK |
| frontend\js\llm-switch.js | ✅ OK |
| frontend\js\pet-inspect.js | ✅ OK |
| frontend\js\pet-subtitle.js | ✅ OK |
| frontend\js\pet-voice.js | ✅ OK |
| frontend\js\pet.js | ✅ OK |
| frontend\js\rain.js | ✅ OK |
| frontend\js\spine.js | ✅ OK |
| frontend\js\voice.js | ✅ OK |
| frontend\shared\pet-core.js | ✅ OK |
| desktop\src\main\backend.js | ✅ OK |
| desktop\src\main\behavior.js | ✅ OK |
| desktop\src\main\config.js | ✅ OK |
| desktop\src\main\control-server.js | ✅ OK |
| desktop\src\main\index.js | ✅ OK |
| desktop\src\main\ocr.js | ✅ OK |
| desktop\src\main\physics.js | ✅ OK |
| desktop\src\main\raf.js | ✅ OK |
| desktop\src\main\windows.js | ✅ OK |
| desktop\src\preload\pet.js | ✅ OK |
| desktop\src\renderer\fallback.js | ✅ OK |
| desktop\scripts\audit_l2d_fit.js | ✅ OK |
| desktop\scripts\diag_l2d_clickmap.js | ✅ OK |
| desktop\scripts\diag_l2d_placement.js | ✅ OK |
| desktop\scripts\diag_stage_geometry.js | ✅ OK |
| desktop\scripts\diag_zoom_offset.js | ✅ OK |
| desktop\scripts\e2e_live2d_314704.js | ✅ OK |
| desktop\scripts\iv_final_checks.js | ✅ OK |
| desktop\scripts\iv_probe_geometry.js | ✅ OK |
| desktop\scripts\iv_probe_lift.js | ✅ OK |
| desktop\scripts\iv_probe_transition.js | ✅ OK |
| desktop\scripts\measure_subtitle_baseline.js | ✅ OK |
| desktop\scripts\probe_l2d_regions.js | ✅ OK |
| desktop\scripts\shot_canvas.js | ✅ OK |
| desktop\scripts\shot_stage.js | ✅ OK |
| desktop\scripts\smoke_electron.js | ✅ OK |
| desktop\scripts\smoke_render.js | ✅ OK |
| desktop\scripts\verify_l2d_blink.js | ✅ OK |
| desktop\scripts\verify_l2d_bounds.js | ✅ OK |
| desktop\scripts\verify_l2d_fitpet.js | ✅ OK |
| desktop\scripts\verify_l2d_nudge.js | ✅ OK |
| desktop\scripts\verify_l2d_zoom.js | ✅ OK |
| desktop\scripts\verify_subtitle.js | ✅ OK |

- 合计：**48 通过 / 0 失败**
- 分布：frontend\js 14、frontend\shared 1、desktop\src 11、desktop\scripts 22
- 备注：`desktop\src\main\index.js.bak` 因扩展名非 `.js` 未纳入 `--check`（详见第 5 节）。

---

## 2. 资源引用断链清单

**结论：核对了 HTML/CSS/JS/JSON 中全部被引用到的本地资源（约 100 处），断链 0 个，无 404 风险。**

| 引用处 文件:行号 | 目标路径 | 是否存在 |
|---|---|---|
| index.html:6 / pet.html:6 / redesign.html:8 | ./assets/favicon.svg | ✅ 存在 |
| index.html:8 | ./css/index.css | ✅ 存在 |
| index.html:9 / pet.html:9 | ./css/pet-subtitle.css | ✅ 存在 |
| index.html:21 | ./assets/r1999/logo.png | ✅ 存在 |
| index.html:286 | ./assets/lib/live2dcubismcore.min.js | ✅ 存在 |
| index.html:287 / _l2d_poc.html:19 / _verify_blink.html:3 | ./assets/lib/pixi.min.js | ✅ 存在 |
| index.html:288 / _l2d_poc.html:21 / _verify_blink.html:5 | ./assets/lib/pixi-live2d-display-cubism4.min.js | ✅ 存在 |
| index.html:289-306 | ./js/{rain,live2d,voice,llm-switch,live2d-bootstrap,pet-voice,pet-subtitle,chat,knowledge,desktop-pet,layout}.js | ✅ 全部存在 |
| index.html:297 / pet.html:174 | ./shared/pet-core.js | ✅ 存在 |
| pet.html:8 | ./css/pet.css | ✅ 存在 |
| pet.html:172 / pet-inspect.html:62 | ./assets/lib/spine-player.js | ✅ 存在 |
| pet.html:175-182 | ./js/{voice,chat,spine,pet-voice,pet-subtitle,pet}.js | ✅ 全部存在 |
| pet-inspect.html:7 | ./css/pet-inspect.css | ✅ 存在 |
| pet-inspect.html:63 | ./js/pet-inspect.js | ✅ 存在 |
| redesign.html:1258 | ./assets/r1999/1.png | ✅ 存在 |
| css\index.css:32 | ../assets/r1999/p.jpg | ✅ 存在 |
| js\live2d.js:28 | ./assets/live2d/wmz/314701/v3a7_314701_wmz.model3.json | ✅ 存在 |
| js\live2d.js:33 | ./assets/live2d/wmz/314702/v3a7_314702_wmz.model3.json | ✅ 存在 |
| js\live2d.js:38 | ./assets/live2d/wmz/314704/314704.model3.json | ✅ 存在 |
| js\live2d.js:169 / js\chat.js:522 | ./assets/live2d/emotion_map.json | ✅ 存在 |
| js\live2d.js:177 | ./assets/live2d/interact_map.json | ✅ 存在 |
| js\pet-voice.js:43 | ./assets/voice/wu_ming_zhe/manifest.json | ✅ 存在 |
| js\pet.js:326 / js\spine.js:18,39 / js\pet-inspect.js:97 | ./assets/spine/314701_wmz_s_room.skel | ✅ 存在 |
| js\pet.js:327 / js\spine.js:19,40 / js\pet-inspect.js:98 | ./assets/spine/314701_wmz_s.atlas | ✅ 存在 |
| js\spine.js:47 | ./assets/spine/314701_wmz_room.skel | ✅ 存在 |
| js\spine.js:48 | ./assets/spine/314701_wmz.atlas | ✅ 存在 |
| js\spine.js:55 | ./assets/spine/314702_wmz_room.skel | ✅ 存在 |
| js\spine.js:56 | ./assets/spine/314702_wmz.atlas | ✅ 存在 |
| js\pet.js:328-329 / js\spine.js:20-21,41-42,49-50,57-58 | ./assets/spine/{animation_map,expression_map}.json | ✅ 存在 |
| desktop\src\renderer\fallback.html:69 | ./fallback.js | ✅ 存在 |

### 二级引用（大目录内按需核对，逐个确认存在）

| 来源 | 内部引用 | 结果 |
|---|---|---|
| 314701 model3.json | Moc `v3a7_314701_wmz.moc3` + 4× textures/*.png | ✅ 全部存在 |
| 314702 model3.json | Moc `v3a7_314702_wmz.moc3` + 18× textures/*.png | ✅ 全部存在 |
| 314704 model3.json | Moc `314704.moc3` + 2× textures/*.webp | ✅ 全部存在 |
| 314701_wmz.atlas | 314701_wmz.png | ✅ 存在 |
| 314701_wmz_s.atlas | 314701_wmz_s.png | ✅ 存在 |
| 314702_wmz.atlas | 314702_wmz.png | ✅ 存在 |
| redesign.html:2068-2094 | assets/voice/wu_ming_zhe/{zh,en}/{00,01,03,04,05,31,41,45}.mp3 | ✅ 9/9 存在 |

> 说明：live2d / spine / voice 资产目录仅核对「被引用到的文件」，未做全量遍历。Emotion/Interact 映射里引用的 motion/expression 名（如 `b_diantou`、`e_weixiao`）与三套 model3.json 的 Motions 组名一致，未发现指向不存在动作的映射。

---

## 3. 前后端接口契约核对

后端路由来源：`src\roleplay\main.py`（`include_router` × 7 + `@app.get("/health")` + `/docs/DESKTOP_PET_DESIGN.md` + 静态挂载 `/`）与 `src\roleplay\api\*.py` 的 `@router.*` 装饰器；桌面端另有回环控制服务 `desktop\src\main\control-server.js`。

### 3.1 前端调用 但 后端没有（死调用）— **0 条**

| 前端调用 | 后端对应 | 判定 |
|---|---|---|
| — | — | 无死调用 |

全部 24 个前端接口调用均在后端找到对应路由，方法一致：

| 前端位置 | 调用 | 后端 |
|---|---|---|
| chat.js:408 | POST /chat/clear | ✅ chat.py:89 |
| chat.js:589 | POST /chat/stream | ✅ chat.py:37 |
| chat.js:1058 | GET /api/characters | ✅ characters.py:22 `@router.get("")` |
| chat.js:1114 | GET /api/characters/active | ✅ characters.py:29 |
| chat.js:1130 | GET /api/characters/{id} | ✅ characters.py:38 |
| chat.js:1234 | PUT /api/characters/{id} | ✅ characters.py:66 |
| chat.js:1241 | POST /api/characters | ✅ characters.py:49 |
| chat.js:1257 | POST /api/characters/{id}/activate | ✅ characters.py:81 |
| chat.js:1269 | DELETE /api/characters/{id} | ✅ characters.py:92 |
| chat.js:1280 | POST /api/knowledge/web-ingest | ✅ knowledge.py:78 |
| chat.js:1311 | GET /api/sessions/{sid}/history | ✅ sessions.py:14 |
| knowledge.js:139 | GET /api/knowledge/stats | ✅ knowledge.py:205 |
| knowledge.js:166 | GET /api/knowledge/documents | ✅ knowledge.py:381 |
| knowledge.js:224 | GET /api/knowledge/chunks | ✅ knowledge.py:442 |
| knowledge.js:281 | DELETE /api/knowledge/documents/{doc_id} | ✅ knowledge.py:419 |
| knowledge.js:319 | POST /api/knowledge/upload | ✅ knowledge.py:472 |
| knowledge.js:407 | GET /api/knowledge/search | ✅ knowledge.py:179 |
| llm-switch.js:298 | GET /api/llm/config | ✅ llm_config.py:132 |
| llm-switch.js:497 | POST /api/llm/models | ✅ llm_config.py:152 |
| llm-switch.js:542 / pet.js:853 | GET /api/llm/ollama/models | ✅ llm_config.py:212 |
| llm-switch.js:595 | POST /api/llm/test | ✅ llm_config.py:317 |
| llm-switch.js:649 | POST /api/llm/switch | ✅ llm_config.py:439 |
| voice.js:225 | POST /voice/stt | ✅ voice.py:27 |
| voice.js:289 | POST /voice/tts | ✅ voice.py:82 |
| pet.js:1598 | GET /health | ✅ main.py:169 |
| desktop-pet.js:107 | POST /api/desktop-pet/launch | ✅ desktop_pet.py:100 |
| desktop-pet.js:49 / :166 | GET /ping、GET /state（回环 39231±） | ✅ control-server.js:39,40 |
| desktop-pet.js:97 / :124 | POST /launch（回环） | ✅ control-server.js:46 |
| desktop-pet.js:140 | GET /docs/DESKTOP_PET_DESIGN.md | ✅ main.py:177 |

### 3.2 后端有 但 前端没用（可能遗漏）— **7 条**

| # | 后端路由 | 位置 | 说明 / 风险 |
|---|---|---|---|
| 1 | **POST /chat**（同步对话） | api\chat.py:28 | 前端只用 SSE 流式 `/chat/stream`。同步接口无人调用，属于「已实现未接线」，可能是为 QQ 渠道/CLI 保留，也可能真的是遗漏。 |
| 2 | **POST /api/knowledge/ingest** | api\knowledge.py:102 | 前端只接了 `/upload`（multipart）与 `/web-ingest`（联网检索）。本地目录/文本灌库入口在 UI 上不存在。 |
| 3 | **GET /api/knowledge/graph/stats** | api\knowledge.py:245 | GraphRAG 知识图谱统计。UI 无入口。 |
| 4 | **GET /api/knowledge/graph/entity** | api\knowledge.py:259 | 实体邻域子图（人工校验用），UI 无入口。 |
| 5 | **GET /api/knowledge/plot-graph/stats** | api\knowledge.py:222 | 剧情图谱统计，UI 无入口。 |
| 6 | **GET /api/knowledge/plot-graph/search** | api\knowledge.py:328 | 剧情图谱检索，UI 无入口。 |
| 7 | **POST /talk**（桌面端回环） | desktop\src\main\control-server.js:50 | ⚠️ **最值得关注**：链路内部完整（control-server → index.js:150 `onTalk` → IPC `pet:talk` → preload `onTalk` → pet.js:924 已订阅），但**没有任何调用方**。前端 `desktop-pet.js` 只调 `/ping`、`/launch`、`/state`，从不 POST `/talk`。「网页按钮让宠物说话」功能实际是断的。 |

### 3.3 两边都有但方法/路径疑似不一致 — **0 条代码级不一致**，1 条文档不一致

| 项目 | 说明 | 严重程度 |
|---|---|---|
| 代码级 | 逐条比对方法（GET/POST/PUT/DELETE）与路径（含 `@router.get("")` 空路径展开、前缀拼接），**未发现 POST/GET 混淆或尾斜杠差异**。 | ✅ 无 |
| 文档级 | `docs\voice-desktop\pet-design\DESKTOP_PET_DESIGN.md:59,65,127` 写的是 `/api/voice/stt`、`/api/voice/tts`，但后端实际前缀是 `/voice`（`api\voice.py:24`，无 `/api`）。前端 `voice.js:225,289` 用的是正确的 `/voice/*`。文档会误导后续开发者。 | 低（文档） |
| 备注 | `main.py:189` 把 `frontend/` 以 `StaticFiles(html=True)` 挂在 `/`，且**在 API 路由之后**挂载，顺序正确，不会遮蔽 `/chat`。 | ✅ 无风险 |

---

## 4. 安全配置审查

### 4.1 Electron 高危组合核查（重点项）

| 文件:行号 | 配置 | 判定 |
|---|---|---|
| desktop\src\main\windows.js:199-205（宠物窗） | `contextIsolation: true`、`sandbox: true`、`nodeIntegration: false` | ✅ **安全**（非高危组合） |
| desktop\src\main\windows.js:357（设置窗） | `contextIsolation: true`、`sandbox: true`、`nodeIntegration: false` | ✅ **安全** |
| desktop\src\preload\pet.js:11 | 仅用 `contextBridge.exposeInMainWorld` 白名单暴露，未裸暴露 `ipcRenderer`/`require` | ✅ **安全** |

**未发现 `contextIsolation=false && nodeIntegration=true` 的高危组合。**

### 4.2 问题清单

| # | 文件:行号 | 问题 | 严重程度 | 建议 |
|---|---|---|---|---|
| 1 | frontend\js\llm-switch.js:64-66（及 :42/:49） | **API Key 明文写入 localStorage**（`roleplay_llm_state` 整个 state JSON 含 `api_key` 字段；:20 注释亦自承「api_key 仅存 localStorage」）。任何 XSS、浏览器扩展、本机取证均可直接读取云端密钥。 | **中** | 改用 `sessionStorage`+内存态，或后端签发短期 token 回传；至少对 key 做混淆/加密并在 UI 上只回显掩码。 |
| 2 | frontend\index.html / pet.html / pet-inspect.html / redesign.html（全文） | **未配置任何 CSP**。`live2d-bootstrap.js:2` 的注释写着「独立为外部文件以符合 CSP script-src 'self'（禁止内联脚本）」，说明设计意图是有 CSP，但**实际上没有任何 `<meta http-equiv="Content-Security-Policy">` 或后端响应头**（`main.py` 的 `SecurityHeadersMiddleware` 需另行确认是否下发）。无 CSP 时第 1 项的 XSS→密钥窃取风险被放大。 | **中** | 在后端统一加 `Content-Security-Policy` 响应头（或 HTML meta），`script-src 'self'`；pet.html 有内联 `<style id="pet-critical">`，需配 `style-src 'self' 'unsafe-inline'` 或改 nonce。 |
| 3 | desktop\src\main\control-server.js（全文，:46/:50） | 回环控制服务**无鉴权**：本机任意进程/网页均可 POST `/launch`、`/talk`。虽仅绑 127.0.0.1（:115）且 CORS 只回显回环源（:58-66），但浏览器端任意站点可发起 CSRF（简单 POST+form 可绕过 CORS 预检）。 | 低 | 加一次性 token 或校验 `Origin`/自定义头（如 `X-Roleplay-Local`），拒绝非预期来源。 |
| 4 | desktop\src\main\index.js:44-54 | `isTrustedIpcSender` 放行任意 `url.startsWith("file:")` 的发送者。若将来有窗口加载了非受控本地 HTML，即可发 IPC。当前被 `will-navigate` + `setWindowOpenHandler deny` 双重限制，暂无可利用路径。 | 低 | 收紧为「等于本项目 `fallback.html`/`settings.html` 的 file 路径」白名单，或干脆去掉 `file:` 分支。 |
| 5 | frontend\js\desktop-pet.js:168-176 | `card.innerHTML` 直接拼接回环服务返回的 `s.version`、`s.hint`（:171 已用 `escText` 转义 hint，但 :170 的 `s.version` **未转义**）。来源为本机回环服务，信任边界内，但属于不一致的转义习惯。 | 低 | `s.version` 一并过 `escText()`，或整体改用 `textContent` + DOM 构建。 |
| 6 | desktop\src\main\index.js.bak（被 electron-builder 打包） | `electron-builder.yml` 的 `files: - src/**/*` 会把 `index.js.bak`（12KB 旧主进程代码）与 `_writetest.tmp` 打进安装包，属于把临时/废弃文件发布出去。 | 低 | 删除，或在 `files` 加 `"!src/**/*.bak"`、`"!src/**/*.tmp"`。 |
| 7 | desktop\src\main\windows.js:10 | `const { BrowserWindow, screen, shell } = require("electron")` 导入了 `shell` 但全文未使用。**全仓库未发现 `shell.openExternal`**，因此「用用户可控 URL 打开外部浏览器」的钓鱼风险不存在——但残留导入易被后续误用。 | 信息 | 删掉未使用的 `shell` 导入。 |
| 8 | frontend\js\desktop-pet.js:140 | `window.open("./docs/DESKTOP_PET_DESIGN.md", "_blank")` 未传 `noopener,noreferrer`。目标是站内相对路径，非用户可控，风险极低。 | 信息 | 补 `window.open(url, "_blank", "noopener")`。 |

### 4.3 已核查确认安全（无需处置）

- **shell.openExternal 钓鱼**：`desktop\src` 全量搜索 `shell.`/`openExternal` → 0 命中。Electron 窗口 `setWindowOpenHandler → deny`（windows.js:214）+ `will-navigate` 仅放行回环（windows.js:215-218）+ 主进程 `webRequest.onBeforeRequest` 拦截一切非回环请求（index.js:109-114），三重防护到位。
- **API Key 明文输出到控制台**：搜索 `console.log/debug/info/warn` 与 `api_key` 的组合 → **0 命中**。`pet-voice.js:104` 的调试日志受 `RP_PET_VOICE_DEBUG` 开关控制且不涉及密钥。
- **innerHTML = 用户输入（XSS）**：逐处核查——
  - `knowledge.js:453` `text.innerHTML = highlight(r.text, q)`：`highlight()`（:384-396）先 `esc(text)` 再插入 `<mark>`，查询词 `q` 仅用于构造正则（且做了正则转义），**安全**。
  - `pet.js:1472` `holder.innerHTML = html`：动态值均已过 `esc()`（:1578，如 :1406/:1407/:1432），**安全**。
  - `chat.js` 全部用户可见文本走 `textContent`（:428/:440/:1082/:1085 等），**安全**。
  - `live2d-bootstrap.js:23` `innerHTML`：仅接收文件内硬编码的静态字符串，动态错误走 :31 的 `textContent`，**安全**且注释已说明。
  - `voice.js:382`、`pet.js:1379`：纯静态模板/常量数组，**安全**。
- **协议处理**：`roleplaypet://` 仅在 index.js:97-98 被 `console.info` 打印，未用于导航或 `openExternal`。
- **权限**：index.js:105-107 只放行 `media`（麦克风），其余全部拒绝。

---

## 5. 冗余/垃圾文件清单

> 只做清单，**未删除任何文件**。

### 5.1 仓库根目录下的临时/junk 目录（pytest 沙箱产物）

| 目录/文件 | 估算体积 | 说明 | .gitignore 是否已覆盖 |
|---|---|---|---|
| `pytest-of-Lenovo\` | ~0 MB（空） | pytest basetemp 产物 | ✅ 已覆盖 |
| `.pytest_cache\` | ~0 MB（空） | pytest 缓存 | ✅ 已覆盖 |
| `.pytest_bt\` | ~0 MB（空） | 沙箱产物 | ✅ 已覆盖 |
| `.pytest_ws\` | ~0 MB（1 项） | 沙箱产物 | ✅ 已覆盖 |
| `.pytest_tmp\` | ~0 MB（空） | 沙箱产物 | ✅ 已覆盖（`.pytest_tmp*/`） |
| `.pytest_tmp2\` | ~0 MB（空） | 沙箱产物 | ✅ 已覆盖 |
| `.pytest_tmp3\` | ~0 MB（空） | 沙箱产物 | ✅ 已覆盖 |
| `tmp_pytest\` | ~0 MB（21 项） | pytest 临时目录 | ✅ 已覆盖 |
| `roleplay_test_qenmhfwr\` | ~0 MB（空） | 测试运行残留（随机后缀） | ❌ **未覆盖**，建议加 `roleplay_test_*/` |
| `.idea\` | 0.01 MB | JetBrains IDE 配置 | ❌ **未覆盖**（或加入 `.gitignore`） |
| `_shuzhi_extract.txt` | 14 KB | 根目录临时抽取产物 | ❌ 未覆盖 |
| `_tmp_pron_edges.txt` | 15 KB | 临时分析产物 | ✅ 已覆盖 |
| `.env.env.bak.20260831_232917` | 3.7 KB | ⚠️ **.env 备份，可能含 API Key** | ✅ 已覆盖（`.env.*.bak*`），但建议物理删除 |

### 5.2 frontend / desktop 内的探针残留

| 文件 | 大小 | 说明 |
|---|---|---|
| `frontend\_write_probe.tmp` | 20 B | 写入探针残留；会被后端 `StaticFiles` 以静态资源对外暴露。 |
| `desktop\src\main\_writetest.tmp` | 9 B | 写入探针残留；**会被 `electron-builder.yml` 的 `files: src/**/*` 打进安装包**。 |
| `desktop\src\main\index.js.bak` | 12 KB | 主进程旧版备份；**同样会被打进安装包**。 |

### 5.3 `desktop\scripts` 下重复/废弃的脚本（共 22 个）

**仅有 2 个被 `package.json` 引用，应保留：**

| 脚本 | 引用位置 |
|---|---|
| `smoke_electron.js` | `npm run check` / `npm run smoke` |
| `smoke_render.js` | `npm run check` / `npm run smoke` / `npm run smoke:render` |

**其余 20 个均为一次性诊断/验收脚本，未在任何 npm script、CI 或源码中被引用。** 按主题分组，明显重复或已被取代的有：

| 组 | 脚本 | 重复/废弃判定 |
|---|---|---|
| **截图辅助（2）** | `shot_stage.js`、`shot_canvas.js` | ⚠️ **明确废弃 1 个**：`shot_canvas.js` 头部注释自述是 `shot_stage.js` 的改进版（后者把 UI 边框误判为角色像素）→ **`shot_stage.js` 应废弃**。 |
| **字幕布局（2）** | `measure_subtitle_baseline.js`、`verify_subtitle.js` | ⚠️ **功能高度重叠**（都测字幕排版/可读性），`iv_probe_geometry.js` 亦参与同一问题。 |
| **字幕过渡三连探针（3）** | `iv_probe_lift.js`、`iv_probe_transition.js`、`iv_probe_geometry.js` | ⚠️ **同一 bug（`--sub-lift` 过渡卡在 6px）的三连定位脚本**，问题定案后即可整体归档；`iv_final_checks.js` 是它们的收尾版。 |
| **Live2D 摆放/点击诊断（4）** | `diag_l2d_placement.js`、`diag_l2d_clickmap.js`、`diag_stage_geometry.js`、`diag_zoom_offset.js` | 同一「定位有问题」根因的四个角度探针，均已产出结论并已修（interact_map.json 的 `_meta.note` 记录了 2026-09-05 实测结果）。 |
| **区域探测（1）** | `probe_l2d_regions.js` | 与上面的 `diag_l2d_*` 目的相同（测头/身/下摆真实位置），**冗余度最高**。 |
| **Live2D 验收（4）** | `verify_l2d_blink.js`、`verify_l2d_bounds.js`、`verify_l2d_nudge.js`、`verify_l2d_zoom.js` | 各自验收不同子功能，尚可保留，但均无回归入口。 |
| **布局审计（1）** | `audit_l2d_fit.js` | 与 `diag_l2d_placement.js` 高度重叠（都算「布局框 vs 真实内容」）。 |
| **E2E（1）** | `e2e_live2d_314704.js` | 第三套皮肤端到端验收，有保留价值。 |
| **⚠️ 测死代码（1）** | `verify_l2d_fitpet.js` | 脚本头部注释自承：`pet.html` 已把渲染器锁死为 spine，**`_fitPet()` 在当前页面上没有调用方**，该脚本是在验一段无人调用的代码分支。 |

### 5.4 前端 POC/调试页

| 文件 | 说明 |
|---|---|
| `frontend\_l2d_poc.html` | Live2D 加载 POC（110 行），与已完成的 `live2d.js` 功能重复。 |
| `frontend\_verify_blink.html` | 眨眼验证页（93 行），与 `desktop\scripts\verify_l2d_blink.js`（9.5KB，做同一件事）功能重复。 |

---

## 6. 结论与优先级建议 Top-5

### 总体结论

| 指标 | 数量 |
|---|---|
| JS 语法错误 | **0 / 48** |
| 资源引用断链 | **0**（约 100 处引用全部命中） |
| 接口契约不匹配 | **0 条代码级**；7 条「后端有前端没用」，1 条文档不一致 |
| 高危安全项（nodeIntegration+contextIsolation 组合 / openExternal 钓鱼 / 密钥上 console） | **0 项高危**；2 项中风险，3 项低风险，3 项信息级 |

**整体健康度良好。** 前端与桌面端在「语法正确性」和「资源完整性」上零缺陷；Electron 安全基线的关键项（`contextIsolation: true` + `sandbox: true` + `nodeIntegration: false` + `contextBridge` 白名单 + 三重网络/导航限制）配置到位，没有常见的野路子写法。真正的问题集中在**未接线的接口**、**密钥落地方式**和**一次性脚本未归档**三处。

### 优先级 Top-5

| 优先级 | 事项 | 依据 | 建议动作 |
|---|---|---|---|
| **P1** | **API Key 明文落 localStorage + 无 CSP 兜底** | llm-switch.js:64-66 把含 `api_key` 的 state 整体 JSON.stringify 进 localStorage；同时全部 HTML 无 CSP（而 live2d-bootstrap.js:2 注释显示设计意图本应有 CSP）。二者叠加 = 一旦有注入点即可直接窃取云端密钥。 | ① 后端加统一 CSP 响应头；② key 改内存/session 态或后端签发短期凭证，UI 只显示掩码；③ 存量 key 加迁移清洗。 |
| **P2** | **「让宠物说话」链路断头：control-server `POST /talk` 无任何调用方** | control-server.js:50 定义了 `/talk`，index.js:150 的 `onTalk` → IPC `pet:talk` → preload → pet.js:924 也已订阅，整条链路**只差一个发起者**。前端 desktop-pet.js 只调 `/ping`、`/launch`、`/state`。这是第 3 节里 7 条「有后端无前端」中唯一影响已宣传功能的。 | 在 `desktop-pet.js` / 网页版「说话」入口补 POST `/talk`（含文本），或明确下线该端点并移除 pet.js:924 的订阅，避免留半截链路。 |
| **P3** | **GraphRAG / 剧情图谱 4 个接口与 `POST /api/knowledge/ingest`、`POST /chat` 全无 UI 入口** | knowledge.py:102/222/245/259/328、chat.py:28。可能是刻意为后续版本保留，也可能是功能遗漏。 | 逐一确认「预留」还是「遗漏」；预留则在 README/接口文档标注，遗漏则补 UI 入口。 |
| **P4** | **临时/备份文件被打包与对外暴露** | `desktop\src\main\index.js.bak`(12KB)、`_writetest.tmp` 会被 `electron-builder.yml` 的 `files: src/**/*` 打进安装包；`frontend\_write_probe.tmp` 会被后端 StaticFiles 暴露；`.env.env.bak.*` 可能含密钥。 | 删除这些文件；在 `electron-builder.yml` 的 `files` 追加 `"!src/**/*.bak"`、`"!src/**/*.tmp"`；物理删除 `.env` 备份。 |
| **P5** | **`desktop\scripts` 20 个一次性脚本未归档** | 仅 2 个被 package.json 引用。`shot_stage.js` 已被 `shot_canvas.js` 取代、`verify_l2d_fitpet.js` 在验无人调用的 `_fitPet()`、`iv_probe_*` 三连探针针对同一已定案 bug。 | 保留 `smoke_*` 与 `e2e_live2d_314704.js`；删除 `shot_stage.js`；其余移入 `scripts\archive\` 并在 README 注明「历史诊断脚本，非回归用例」；`roleplay_test_*/`、`.idea/` 补进 `.gitignore`。 |
