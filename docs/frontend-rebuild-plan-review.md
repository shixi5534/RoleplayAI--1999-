# 前端重构计划 · 实测评审

> 评审对象：`docs/frontend-rebuild-plan.md`（v1，2026-10-19，状态「待拍板」）
> 评审方法：**不采信计划里的数字，全部重跑**。每个结论都标注了证据来源。
> 评审日期：2026-10-19　基准 commit：`1c5966f`（tag `frontend-v3-baseline`）

---

## 0. 一句话

**计划的方向对、结构对、拆分粒度对；错的是三处技术细节（importmap / `?fx=off` / 持久化契约）和三个人日数（P1、P5、P6）。**

具体：26 个文件的行数、12 个 window 全局、10 个 CSS 冲突、89/88 个 id、双实现、死代码清单 —— **全部实测复核通过，一个数字都没错**。这是很难得的。问题集中在「机制层」：有三条断言描述了一个并不存在的现状，其中两条会让对应阶段直接卡住；另外样式资产的统计口径漏了一整块（`frontend/pet.html` 里 938 字符的内联 `<style>`，见 §2.6）。

修订后总量从 **15.5 人日 → 约 18.8~20.8（P5 止血版）/ 23.8~27.3（P5 全量版）**（见 §5），多出来的部分主要是 P5 样式统一的隐藏成本。

另外**独立于重构**，我发现并实证修好了一个既存 bug：CSP 的 `connect-src 'self'` 让桌宠端口探测 100% 失效（§2.1）。一行改动，建议先修。

> **关于本文档的可信度**：§1.1 的结论我改了三次（前两版都是错的），最后靠 4 组对照实验才定下来。过程保留在正文里 —— 如果你要引用这里的任何一条，建议先看对应的实验脚本（附录 B），它们都能重跑。

---

## 1. 必须改的硬错误

### 1.1 【P0 阻塞】Plan A 的 importmap 方案不成立 —— 但原因和我最初想的不一样

计划 §3.3 表 A 行 / D1 写「原生 `type="module"` + **importmap 映射三个 UMD 库**」。

这一节我改了三次结论，把过程留在这里，因为它比结论本身有用：

**第一版（错）**：以为 CSP 无条件拦 importmap。
**第二版（半对）**：以为 CSP 拦、但加 hash 也救不了。
**第三版（实测结论）**：**CSP 是能绕过的，但绕过去也没用** —— 因为那 4 个库根本不是 ES 模块。

#### 原因一：CSP 确实拦内联 importmap，但**有解**（我实测出来了）

现网 CSP（`src/roleplay/middleware.py:23-31`）是：

```
script-src 'self' 'unsafe-eval'
```

没有 `'unsafe-inline'`、没有 nonce、没有 hash。而 `<script type="importmap">` **只能内联**（`src` 属性不被 HTML 规范允许；`whatwg/html#8355` 自 2022 年 open 至今，2026-10 仍无浏览器支持）。

**直接内联 → 被拦**，真实报错原文：

```
Executing inline script violates the following Content Security Policy directive
'script-src 'self' 'unsafe-eval''. Either the 'unsafe-inline' keyword, a hash
('sha256-plYBeVSEq/xAiTDv6CM/CbhVP99Z2jbIoxUibbtSfHM='), or a nonce ('nonce-...')
is required to enable inline execution. The action has been blocked.
```

**但这条路是可以打通的。** 我做了 4 组实验（全部用独立静态服务 + **HTTP 头**下发 CSP，不用 `<meta>` —— 因为本项目头 CSP 与 meta CSP 取交集，meta 只能收紧不能放宽，在 app 页面上测不出来）：

| 组 | 做法 | 结果 |
|---|---|---|
| A | 内联注入器 + 内联 importmap，CSP 原样 | ❌ 注入器本身被拦（4 条违规） |
| B | A + CSP 加 `'unsafe-inline'` | ✅ 裸说明符解析成功 |
| C | **外部**注入器（`'self'` 放行）+ DOM 创建 `<script type="importmap">`，CSP 原样 | ❌ 注入器跑了、importmap 进了 DOM，但 `TypeError: Failed to resolve module specifier 'probe-alias'`（1 条违规） |
| D | **C + CSP 加 `sha256-<对 importmap 文本算的 hash>`** | ✅ **裸说明符解析成功，0 违规** |

D 组能成，靠的是经典阻塞脚本 + DOM 注入：

```js
// injector.js —— 必须是经典脚本（无 type=module / defer / async），排在所有 module 之前
(() => {
  const s = Object.assign(document.createElement("script"), {
    type: "importmap",
    textContent: '{"imports":{"probe-alias":"/mod.js"}}',   // 必须紧凑 JSON，hash 按这个串算
  });
  document.currentScript.after(s);
})();
```

对应 CSP 要加 `'sha256-/+U9ADPl0eSuFV4GGhjNZCTJcWGtYP3ZBBYoI0ItI0I='`。

**这条路能用，但我不推荐，原因有三**：
1. **hash 必须对「实际 textContent」算**。我第一版用 `json.dumps()` 默认分隔符（带空格）算 hash → 失败；改用 `separators=(",", ":")`（紧凑）→ 成功。**importmap 内容一改，CSP 里的 hash 就得跟着改**，这是个每次动 importmap 都要踩的坑。
2. 引入一个「阻塞脚本 + DOM 注入」的启动技巧，与本项目「16 个 script 平铺」的现有风格叠加，只会更难读。
3. **最关键的：这么费劲绕过 CSP，绕过之后发现根本用不上** —— 见原因二。

#### 原因二（真正的杀手，改 CSP 也救不了）：那 4 个库不是 ES 模块

计划说「三个 UMD 库」，实际是**四个**，漏了 `spine-player.js`。我把四个库的字节级副本当 ESM 加载实测：

| 文件 | 体积 | 顶层形态 | 当 ESM 加载的结果 |
|---|---:|---|---|
| `frontend/assets/lib/pixi.min.js` | 460,342 B | `var PIXI=function(t){…}({});` | `nsExports: []`、`globals: []` —— 命名空间为空，且**不产生全局** |
| `frontend/assets/lib/spine-player.js` | 612,944 B | `"use strict"; var spine = (()=>{…})();` | 同上 |
| `frontend/assets/lib/live2dcubismcore.min.js` | 207,163 B | `var Live2DCubismCore;!function(…)(…);` | `ReferenceError: __dirname is not defined in ES module scope` |
| `frontend/assets/lib/pixi-live2d-display-cubism4.min.js` | 119,923 B | UMD，全局分支写 `globalThis.PIXI` | `TypeError: Cannot read properties of undefined (reading 'EventEmitter')`；即便先伪造 `globalThis.PIXI` 仍是 `TypeError: Class extends value undefined` |

**importmap 只能把「说明符」映射到「URL」，它不能把 UMD 变成 ESM。** 模块作用域里的 `var PIXI` 不会挂到 `window`，所以 `import * as PIXI from 'pixi'` 得到的是 `{}`。**这条与 CSP 完全无关。**

→ **结论不变：删掉 importmap。** 但理由要写对 —— 不是「CSP 挡死了」，而是「CSP 能绕过，绕过之后发现 UMD 库当 ESM 加载是空的，白绕」。

**修正方案（Plan A′）：完全不用 importmap。**

```html
<!-- 经典脚本：顺序阻塞执行，禁止 defer/async，必须排在 module 之前 -->
<script src="./assets/lib/live2dcubismcore.min.js"></script>
<script src="./assets/lib/pixi.min.js"></script>
<script src="./assets/lib/pixi-live2d-display-cubism4.min.js"></script>

<!-- 唯一入口；模块内部一律相对说明符 -->
<script type="module" src="./src/pages/chat-page.js"></script>
```

- **零 CSP 改动、零 `main.py` 改动。**
- 模块间用相对路径（`import { bus } from '../core/bus.js'`），裸说明符需求消失，importmap 的价值也就消失了。
- 现有代码里 **61 处**引用 `PIXI` / `spine` / `Live2DCubismCore`（代码级，已排除注释与字符串：`spine.js` 41、`pet.js` 10、`live2d.js` 9、`pet-inspect.js` 1）**一行都不用改** —— 模块作用域里的裸标识符照样沿作用域链解析到全局。其中只有 `pet.js` 的 10 处是真正的裸标识符；另外 30 处本来就写成 `global.spine` / `global.PIXI`（IIFE 形参名 `global`），21 处是 `const spine = global.spine;` 之后的局部别名用法。
- 我已实测确认相对说明符在当前 CSP 下可用：`await import('/js/rain.js')` → `ok: true`。

> 时序也验证过：经典脚本无 defer/async 时「立即抓取并执行，阻塞解析」；module 无 async 时「页面解析完成后才执行」→ 模块运行时全局必然就绪。

**要改的四处**：§3.3 表 A 行、§3.3 L238 理由、§4 D1、§9 Q1 的选项描述。Q1 从「要不要 importmap」变成「确认放弃 importmap」。

---

### 1.2 【P6 前提是假的】`?fx=off` 根本不存在

计划 §6 P6 产物行（L357）写：「参数可调、可关（**`?fx=off` 已有**，补 `?fx=a|b` 等变体）」。

**实测：`frontend/js/canvas-fx.js` 里 `URLSearchParams` = 0、`location.search` = 0、`?fx` = 0、`getParam` = 0。** 整个 `frontend/` 目录里唯一出现 `URLSearchParams` 的地方是 `frontend/js/voice.js:277`，而那是 `const params = new URLSearchParams();` —— 构造一个空对象，跟读 URL 无关。

`canvas-fx.js` 的入口 `function start()` 没有任何开关判断，`window.__canvasFx` 只暴露 `frames`/`size`/`lamp`/`counts`/`bad`/`spriteDebug`/`moths`/`dustDump`/`radar` 九个只读诊断接口，**没有启停能力**。

→ P6 不是「补 `?fx=a|b`」，是**从零建立参数机制**。这解释了为什么 P6 的 2 人日偏紧。

---

### 1.3 【P6 会固化一句假话】「异常全静默」只是注释，代码里没有 try/catch

计划 §6 P6 范围行（L356）要求把「`prefers-reduced-motion` 与『异常全静默』两个约定写成模块级契约注释」。

- `prefers-reduced-motion` **是真的**：`frontend/js/canvas-fx.js:15` 注释 + `:23-24` `matchMedia("(prefers-reduced-motion: reduce)")` + `:1774` `if (reduce)`。✅
- **「异常全静默」是假的**：`frontend/js/canvas-fx.js` 里 `try` = **0**、`catch` = **0**、`throw` = **0**、`finally` = **0**（已剔除注释与字符串后统计）。`:14` 那句注释「纯装饰：任何异常静默失败，不影响主流程（先例见 rain.js）」描述的是一个**不存在的实现**。
- 对比 `frontend/js/rain.js` 是**真做了**的：整个 IIFE 体被 `try { … } catch (_) { /* 纯装饰层,任何异常都静默忽略 */ }` 包裹（`rain.js:8` 与 `:24-26`）。

→ P6 如果照搬这句注释，等于把一句不成立的约定固化进新模块。**应该在 P6 里补上真正的 try/catch（或删掉这句注释）。这是既有缺陷，不是重构引入的。**

---

### 1.4 【§1.7 写错了一半】localStorage 不是 6 个键，是 12 个；且有一个键名错

计划 §1.7（L97-102）：「6 个 localStorage 键，直接 `JSON.parse`，无版本字段」，列出 `roleplay_live2d_poslock`。

实测真实键 **12 个**：

| 键 | 位置 | 存储形态 |
|---|---|---|
| `roleplay_session_id` | `frontend/js/chat.js:67` | JSON |
| `roleplay_ui_state` | `frontend/js/chat.js:134` | JSON |
| `roleplay_llm_state` | `frontend/js/llm-switch.js:49` | JSON |
| `roleplay_llm_pulled_models` | `frontend/js/llm-switch.js:74` | JSON |
| `roleplay_pet_state` | `frontend/js/pet.js:42` | JSON |
| `roleplay_voice_state` | `frontend/js/pet.js:1571` | JSON |
| `roleplay_layout_split` | `frontend/js/layout.js:15` | 裸字符串 |
| `roleplay_layout_hud` | `frontend/js/layout.js:16` | 裸字符串 |
| `roleplay_spine_inspect` | `frontend/js/pet-inspect.js:18` | JSON |
| **`rp_live2d_poslock`** | `frontend/js/live2d.js:754/769` | 裸字符串 |
| `rp_pet_voice_lang` | `frontend/js/pet-voice.js:45` | 裸字符串 |
| `rp_pet_voice_muted` | `frontend/js/pet-voice.js:44` | 裸字符串 |

两处错误：
1. **`roleplay_live2d_poslock` → 实际是 `rp_live2d_poslock`**（前缀是 `rp_`，不是 `roleplay_`）。
2. **「直接 `JSON.parse`」不准确** —— 4 个 `rp_*` / `layout_*` 键存的是裸字符串，不是 JSON。

漏掉的 6 个键里，`roleplay_layout_split` / `roleplay_layout_hud` / `rp_live2d_poslock` 三个是**用户会明显感知的界面状态**（分栏比例、HUD 折叠、模型位置锁），P5/P7 一旦碰 CSS 或 localStorage 封装就会静默丢。**建议 §1.7 补全清单，并把「键名 + 形态 + 默认值」列成表。**

---

### 1.5 【§3.2 硬规则 4 会漏 1/3】4 个全局是 IIFE 别名，不是 `window.X =`

计划 §3.2 硬规则 4：「任何模块不得写 `window.X = …`」。

12 个全局里，**只有 8 个是直接 `window.X =`**，另外 4 个是 IIFE 形参别名：

```js
// frontend/js/live2d.js:1373
global.RoleplayLive2D = RoleplayLive2D;
// frontend/js/spine.js:1014
global.RoleplaySpine = RoleplaySpine;
// frontend/shared/pet-core.js:96
global.RoleplayPetCore = Object.freeze({ … });
// frontend/js/layout.js:164
global.RoleplayLayout = { splitter: initSplitter, hud: initHud, drawer: initDrawer };
```

这四处的 IIFE 结尾都是 `})(window);`，形参名就叫 `global`。

→ **lint 规则如果只做 `window\.` 正则，会漏掉 4/12（33%）。** 规则应改成「禁止任何挂到 `window`/`global`/`self`/`globalThis` 的赋值」，或直接查 IIFE 别名。

（另：`window["X"] =` 写法实测 0 处，不用担心。）

---

### 1.6 【§7 闸门判据不可执行】「pytest 1,465 全绿，一个都不许跳过」

计划 §7 L401。实测：

```
$ .\.venv\Scripts\python.exe -X utf8 -m pytest -q
1464 passed, 8 skipped, 1 warning in 410.21s
$ ... --collect-only -q
1472 tests collected
```

- **数字是 1,472，不是 1,465**（差 7）。
- **8 个 skip 是结构性的，不是失败**：7 个在 `tests/compendium_rag/test_online.py`（「默认离线运行；需要 `-m online` 才执行」），1 个在 `tests/test_qa_verification.py:1128`（P2 观察点，已知缺陷标记：跨 UserProfile 实例共享 KB 并发写同 key 产生 2 条）。
- → 「一个都不许跳过」作为闸门判据**永远红**。应改为「1464 passed / 8 skipped，skip 清单冻结，新增 skip 需说明理由」。

**顺带修正 §1.8 的「1,465 个 pytest 里只有 1 个碰前端」**：`tests/e2e_pet_voice.py` **不是 pytest 用例** —— `def test_` 计数 = 0、无 `import pytest`、有 `if __name__ == "__main__"`。它是独立脚本。**1472 个用例里碰前端的实际是 0 个。** 这让「前端零自动化保护」这条病灶比计划写的更严重，不是更轻。

---

### 1.7 【§10 附录照抄会失败】后端启动命令缺 `--app-dir src`

计划 L446：

```powershell
.\.venv\Scripts\python.exe -m uvicorn roleplay.main:app --host 127.0.0.1 --port 8000
```

实测直接跑 → `ModuleNotFoundError: No module named 'roleplay'`。正确命令：

```powershell
.\.venv\Scripts\python.exe -X utf8 -m uvicorn roleplay.main:app --host 127.0.0.1 --port 8000 --app-dir src
```

（另：启动耗时 50~90 s，因为启动期会走 Ollama 重建知识库向量。计划没写这点，会让第一次跑的人以为卡死。）

---

### 1.8 【小】三处交叉引用 / 计数错误

| 位置 | 现文 | 应为 |
|---|---|---|
| §5 L263 `pet-inspect.html` 行 | 「或移入 `tools/`（见 **Q5**）」 | **Q4**（Q5 是主题问题） |
| §6 P4 验收③ L338 | 「`desktop/scripts` 里 **11 个**探针脚本跑通」 | **22 个**（目录里 22 个 `.js`） |
| §8 R3 L416 | 「`desktop/scripts` **11 个**探针全跑」 | 同上 |

> §1.9 L127 的「11 个脚本」其实是对的 —— 但它的含义是「**22 个脚本里有 11 个会抓 DOM**」，不是「总共 11 个」。这个数字来源没错，只是 P4/R3 引用时把「抓 DOM 的 11 个」误当成了「全部 11 个」。

---

### 1.9 【小】P7 的「735 KB → ~570 KB」算不出来

计划 §6 P7 产物行（L367）：「前端源码体积从 735 KB 降到 ~570 KB」。

我把 6 个待删/待移文件逐个量了：

| 文件 | 体积 |
|---|---:|
| `frontend/redesign.html` | 113.9 KB |
| `frontend/_l2d_poc.html` | 5.6 KB |
| `frontend/_verify_blink.html` | 4.8 KB |
| `frontend/pet-inspect.html` | 3.1 KB |
| `frontend/js/pet-inspect.js` | 7.5 KB |
| `frontend/css/pet-inspect.css` | 4.9 KB |
| **合计** | **139.8 KB** |

**735.0 − 139.8 = 595.2 KB**，不是 ~570 KB（差 25 KB）。而 P7 的范围里没有别的东西能再减 25 KB。

→ 要么把目标改成 **~595 KB**，要么说明还要动什么。这个数字不重要，但它是「验收判据」的一部分，写死一个算不出来的数会让 P7 永远差一口气。

**顺带核实**：`redesign.html` 的内联量，按 UTF-8 字节算是 **48.5 KB `<style>` + 29.4 KB `<script>` = 77.9 KB（占全文件 68.4%）**；按字符算（计划用的口径）是 **44.5 KB + 25.8 KB**。计划写「内联 style 45.5 KB + 内联 script 26.4 KB」，**基本吻合（差 1 KB 量级，口径差）**。占前端源码 15.49%，计划说 15% ✅ 正确。

---

## 2. 计划漏掉的问题

### 2.1 【既存 bug，与重构无关但必须知道】桌宠端口探测在现 CSP 下 100% 失效

这是我在真实首页控制台里发现的，计划完全没提。

- `frontend/js/desktop-pet.js:16-17`：`const BASE_PORT = 39231;` / `const PROBE_PORTS = 21; // 39231 ~ 39251`
- `frontend/js/desktop-pet.js:44`：`const base = "http://127.0.0.1:" + (BASE_PORT + i);`
- `frontend/js/desktop-pet.js:49`：`fetch(base + "/ping", …)`
- CSP 是 `connect-src 'self'` → **21 个端口全部被拦**

真实控制台**实测 42 条**，结构精确是 **21 个端口 × 2 条**：

| 形态 | 条数 |
|---|---:|
| `Connecting to '…' violates the following Content Security Policy directive: "connect-src 'self'". The action has been blocked.` | **21** |
| `Fetch API cannot load http://127.0.0.1:3923X/ping. Refused to connect because it violates the document's Content Security Policy.` | **21** |
| 涉及端口 | **21 个**（`39231`…`39251`，连续无缺） |

原文两条：

```
Connecting to 'http://127.0.0.1:39231/ping' violates the following Content Security
Policy directive: "connect-src 'self'". The action has been blocked.
Fetch API cannot load http://127.0.0.1:39231/ping. Refused to connect because it
violates the document's Content Security Policy.
```

**后果**（我用 Playwright 读了 DOM 实证，不是推测）：`#pet-status-dot` 的 `className` 恒为 `"pet-dot off"`、`title` 恒为 `"未检测到桌面宠物（需安装 desktop/ 并启动）"` —— 即使桌面端正在跑。通道 B（优先通道）永久失效 → 每次点「桌面宠物」都落到通道 A（`roleplaypet://launch` 协议）+ 通道 C（`POST /api/desktop-pet/launch`）；悬停卡片（`frontend/js/desktop-pet.js:161-185`）永远显示「● 未运行」。

**桌面端确实有这个服务**：`desktop/src/main/control-server.js:102` `let port = (cfg.control && cfg.control.port) || 39231;`、`desktop/src/main/config.js:45` `port: 39231`、`control-server.js:129` 写 `control-port.txt`、`control-server.js:64-68` 设了 `Access-Control-Allow-Origin` —— 服务端全准备好了，是 CSP 单方面掐断。

**修复已 A/B 实证**。注意不能在本项目页面上用 `<meta>` 验证：`SecurityHeadersMiddleware` 发的是 **HTTP 头** CSP，而 `<meta>` CSP 与头 CSP 取**交集**（只能收紧、不能放宽），所以在 `index.html` 上挂 meta 测不出来。我改成两个独立静态服务做对照（`:18099` 用 **HTTP 头**下发 CSP 的页面，`:39231` 模拟 control-server 返回 `/ping` + CORS 头）：

| 组 | CSP 的 `connect-src` | `fetch('http://127.0.0.1:39231/ping')` | CSP 违规 |
|---|---|---|---:|
| A（现网） | `'self'` | **FAIL** `TypeError: Failed to fetch` | 2 条 |
| B（拟修正） | `'self' http://127.0.0.1:*` | **OK** `{"ok": true, "pid": 1234}` | **0 条** |

`src/roleplay/middleware.py:30` 改这一行即可：

```python
"connect-src 'self'"
```

→

```python
"connect-src 'self' http://127.0.0.1:*"
```

（CSP 支持端口通配符。如果不想放开本机全部端口，就把 21 个端口逐个列出来 —— 但 `desktop/src/main/config.js:45` 注释写明「被占用会自动 +1」，端口不是固定的，逐个列会在端口漂移时再坏一次。**推荐 `http://127.0.0.1:*`**，并在这行上方补一条注释说明用途，与现有 3 条注释风格一致。）

**一行改动。建议单独立项先修，不要混进重构。**

---

### 2.2 Q3 的「移到 `docs/design/`」会让这份设计资产从「能打开」变成「打不开」

计划 Q3 建议把 `frontend/redesign.html`（2,311 行 / 113.9 KB）移到 `docs/design/`。

**`docs/` 不在 StaticFiles 托管范围内。** `src/roleplay/main.py:187-189` 只挂 `frontend/`：

```python
frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"
if frontend_dir.is_dir():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
```

`docs/` 只有一条硬编码路由（`:177` 的 `/docs/DESKTOP_PET_DESIGN.md`）。

→ 移到 `docs/` 后，**通过 HTTP 就打不开了**，只能本地双击文件。而它里面有 `./assets/r1999/1.png` 和 `./assets/favicon.svg` 两个相对路径引用 → 双击时相对路径解析到 `docs/design/assets/…`，**404**。

**另外**：它引用 3 个外部 URL（`https://fonts.googleapis.com` preconnect ×2 + `.../css2?family=Azeret+Mono…&family=Bodoni+Moda…`），在现 CSP（`style-src 'self'`、`font-src 'self' data:`）下**字体必然失效** —— 它现在就已经是这个状态了。

**三个选项**：
1. **留在 `frontend/` 但改名**（如 `frontend/_design-archive.html`），保持可打开，不占构建/不占体积统计 —— **推荐**
2. 移到 `docs/design/` + 同步改 3 个相对路径为绝对 URL + 接受「只能本地双击」
3. 直接删（git 里有）

---

### 2.3 Q6 有铁证：紫主题是**有意设计**，但它是**对风格板的偏离**

计划 Q6 问「桌宠页紫主题 + Varela Round 与主站金铜 + Georgia 完全不同世界 —— 这是有意的吗？」

**答案：是有意做的，但它推翻了同一份设计文档。**

铁证在原 `docs/voice-desktop/pet-design/pet-visual-styleboard-v0.3.md`（2026-08-14，art-director 林绘澄；现并入 `docs/voice-desktop/CHRONICLE.md`，现行真源 `frontend/css/pet.css`）：

- §1 明确要求「**暗夜金铜**：延续主页…金铜 `#c9a86a` 是**全应用唯一高饱和装饰色**」
- **全文档 0 处**提到紫 / 霓虹 / `7F77DD` / Varela Round

最硬的一条证据是**注释句式的镜像**：

```css
/* 风格板 L368 */
--font-serif: "Georgia", …;
--font-sans: var(--font-serif);   /* 旧名别名，v0.4 移除 */

/* frontend/css/pet.css:31-32 */
--font-sans: "Varela Round", …;
--font-serif: var(--font-sans);   /* 旧名别名，页面统一无衬线 */
```

同一句式、同一别名结构、**主从关系完全颠倒**。这说明 pet.css 的作者读过风格板并**有意改写了字体方向**。

骨架也证明同源：`--space-1..6`、`--shadow-s1..s4`、`--dur-*`、`--ease-*`、`--lh-*`、`--fs-chip/caption/small/bubble/heading` 的取值**一字不差**，`prefers-reduced-motion` 块**逐字相同** —— 只有颜色和 3 个 radius 不同。`pet.css` 自述「方向 C：暗色高对比重制」，另有 8 处引用「风格板 §11 / §7.x」。

时间线：风格板 2026-08-14（金铜）→ pet.css 实现（紫）→ 重构计划 2026-10-19 才发现冲突。

**补充事实**：`Varela Round` 运行时**根本不会生效** —— 全仓 `@font-face` = 0，`index.html` / `pet.html` 里 `fonts.googleapis` = 0。实际 fallback 到微软雅黑。

→ **Q6 应该改写为：「当初否决风格板金铜方案、选『方向 C 紫色』这个决定，现在还算数吗？」** 这个问题的答案决定 P5 走「保持两套」还是「合并成一套」，工作量差一倍。

---

### 2.4 视觉闸门的 4 个阈值，口径有硬伤

计划 P6 验收②（L358）给了四个阈值。我用 `audit2.py` 同口径在真实截图上复算，结论是**指标本身能用，但阈值口径写错了**。

**（a）「平均亮度 ≈24%±1」只对「舞台裁切图」成立**

| 视口 | 全页平均亮度 | 舞台裁切平均亮度 |
|---|---:|---:|
| 1280×720 | 12.74% | 24.05% |
| 1440×900 | 12.49% | 24.61% |
| 1920×1080 | 12.29% | 24.01% |
| 2560×1440 | 11.95% | 23.48% |

全页全部 12% 上下（因为右侧聊天区大面积暗），**照字面判会全 FAIL**。舞台裁切全部落在 24%±1。

→ **计划必须写明「在 `.stage` 裁切图上量」。**

**（b）「死黑 ≤0.06%」基线自己就突破**

舞台裁切死黑：1280×720 = 0.0273%（pass）/ 1440×900 = 0.0448%（pass）/ 1920×1080 = 0.0469%（pass）/ **2560×1440 = 0.0654%（FAIL）**。

→ 应按视口分档，或放宽到 ≤0.10%。

**（c）「16×16 空格率 ≤0.0%@0.02」是一个永不触发的指标**

所有真实截图（基线图、我新截的图、`deliverables/` 里的产品图）**全部恒为 0.0%**。我用合成图验证过指标本身能 fire（95% 黑图 → 96.88%），所以是**指标选错了**，不是实现错 —— 舞台永远被角色/灯光/尘粒铺满 16×16 网格。

→ 应换成有区分度的指标，比如 `audit2.py` 里已有的「亮团块计数」或 8×8 分区亮度方差。

**（d）过曝 ≤3% 只在舞台裁切上有意义**：舞台 2.19~2.84%（pass），全页 0.04~0.24%（暗区拉低比例，等于不设防）。

**（e）pet 页基线到底截哪个环境，计划没说。** 实测：带引导层 平均亮度 22.07% / 死黑 0.0% / 过曝 0.11%；**关掉引导层后 平均亮度 89.09% / 过曝 86.63%** —— 因为 `frontend/css/pet.css` 的 `html,body{background:transparent}` 在浏览器里透出白底，而在 Electron 壳里透的是桌面。**同一个页面在两个环境里是完全不同的图。**

**好消息**：整条验收链可建立且可复现 —— 我用同一口径量新截图与基线图，差 < 0.1%（舞台 24.70% vs 24.61%，死黑 0.044% vs 0.045%）。「P6 只拆不改观感」这个闸门是真能落地的。

---

### 2.5 §1.5 的「4 个 `:root` 块（含浅色主题覆盖）」这句括注是错的

实测 `frontend/css/index.css` 的 4 个 `:root` 是：

| 行 | 内容 |
|---|---|
| L13 | 主 `:root`（37 个变量） |
| L1425 | `@media (min-width: 1440px)` 内的 `--app-gap` / `--fs-display` |
| L1430 | `@media (min-width: 1024px) and (max-width: 1439px)` 内的 `--stage-w` |
| L1438 | `@media (max-width: 480px)` 内的 `--topbar-h` / `--app-gap` |

**三个是响应式断点，不是主题。** 浅色主题在 `body[data-theme="light"]`（`frontend/css/index.css:61-76`，14 个纯颜色变量），**不在 `:root`**。

→ 这条不影响结论，但会影响 P5 的拆法：如果按「4 个 :root 块」去拆 tokens，会把响应式断点误当主题层。

---

### 2.6 §3.2 硬规则 5「不得内联 `<script>`」实测已满足；但 pet 页藏了一块内联 `<style>`

三个线上页（`index.html` / `pet.html` / `pet-inspect.html`）**无 `src` 的内联 `<script>` = 0**。

→ 硬规则 5 现在就已经成立，可以降级为 warning，不必作为 error 卡 P1。

（`frontend/redesign.html` 有 2 个内联 `<script>` + 1 个内联 `<style>` + 14 个 `style=` 属性，但它是静态设计稿，不是线上页。）

**但同一句结论在 CSS 侧不成立。** `frontend/pet.html:11-37` 有 **1 个内联 `<style id="pet-critical">`（938 字符 / 27 行）**，而计划 §1.5 统计样式时只算了 4 个 `.css` 文件（2,525 行 / 96.1 KB）—— **这块内联样式不在统计口径里**。

它的内容分三类：

| 类别 | 内容 | 问题 |
|---|---|---|
| **第四套颜色命名** | `--c-bg: #0E1116` / `--c-primary: #7F77DD` / `--c-accent: #1D9E75` / `--c-pink: #D4537E` / `--c-text: #EDEDED` | **全仓 `var(--c-*)` 引用数 = 0**（`pet.css` 用的是 `--accent: #7F77DD` 等同值**不同名**的变量）→ 这 5 个变量**声明后从未被使用**，是纯死代码 |
| **兜底令牌** | `--bubble-scale: 1` | 与 `frontend/css/pet.css:54` **重复定义** |
| **兜底规则** | `.pet-error[hidden]` / `.fx-ripple` / `#pet-canvas.pulse` / `@keyframes pet-pulse` | 4 条全部与 `pet.css` 重复（`pet.css:226` / `:153` / `:136` / `:137`） |

注释自称「方向 C 设计令牌（内联冗余，保证离线/加载失败时不丢失调色板）」——**但它保护的那 5 个变量没有任何消费者，所以这段"兜底"实际不起作用**；真正起作用的 4 条规则与外部 CSS 完全相同（复制粘贴产物）。

→ **对 P5 的直接影响**：P5 若按「4 个 CSS 文件」去拆 tokens，会漏掉这块内联样式；`--c-*` 既然无人引用，P5 可以直接删除而不影响观感（**零风险收益**）。建议 P5 的验收清单加一条「`grep -rn 'var(--c-' frontend/` = 0」。

---

### 2.7 三页的 `data-theme` 不一致，P5 的「×2 主题」矩阵在 pet 页无法执行

| 页面 | `<body>` | `data-theme` 出现次数 |
|---|---|---:|
| `frontend/index.html` | `<body data-theme="dark">` | 1 |
| `frontend/pet.html` | `<body data-mode="pet" class="ui-hidden">` | **0** |
| `frontend/pet-inspect.html` | `<body>` | **0** |

`frontend/css/pet.css` 里 `[data-theme]` = **0**。`frontend/js/chat.js:1330` 的 `if (!PET_MODE)` 才设主题 —— pet 页压根没走主题切换。

→ **P5 验收①「pet 页 5 个区域 × 2 主题」无法执行**，因为 pet 页没有第二个主题。

---

### 2.8 §1.9 的桌面探针「57 处选择器」组成和计划暗示的不同

计划 §1.9 L127 说「`desktop/scripts/` 11 个脚本（`smoke_render.js` 11 处、`verify_subtitle.js` 9 处、`measure_subtitle_baseline.js` 8 处、`iv_probe_*` 6-7 处）」。

实测逐文件复核，**数字全对**：

| 脚本 | querySelector | getElementById | 合计 |
|---|---:|---:|---:|
| `smoke_render.js` | 2 | 9 | **11** |
| `verify_subtitle.js` | 4 | 5 | **9** |
| `measure_subtitle_baseline.js` | 5 | 3 | **8** |
| `iv_probe_lift.js` | 2 | 5 | 7 |
| `iv_probe_transition.js` | 1 | 6 | 7 |
| `iv_probe_geometry.js` | 4 | 2 | 6 |
| `iv_final_checks.js` | 1 | 4 | 5 |

**但好消息是**：这些脚本引用的 **distinct id 只有 7 个**（`pet-bubble` `pet-bubble-text` `pet-canvas` `pet-error` `pet-subtitle` `stage` `stage-hud`），**distinct selector 只有 7 个**（`#pet-canvas canvas` `#pet-subtitle` `.stage` `.stage-hud` `.sub-en` `.sub-zh` `b`）。

→ **P4 的「选择器改名要同步」成本远低于计划暗示** —— 7 个 id + 7 个选择器，grep 一遍就能定位。这是计划里唯一一处「被高估」的地方。

---

### 2.9 已复核通过、不需要改的（列出来是为了说明「没动过的部分」）

| 计划断言 | 复核结果 |
|---|---|
| 26 文件 / 15,614 行 / 735.1 KB（§1.1） | ✅ 26 文件、15,611 非空行、735.0 KB，差 3 行（纯空白行口径） |
| 16 个 `<script>` 平铺 + 19 个标签（§1.2） | ✅ 一致 |
| 0 个 import / export（§1.3） | ✅ `import`=0、`export`=0（16 个文件全 IIFE） |
| 12 个 window 全局（§1.3） | ✅ 正好 12 个，一个不多一个不少（但分布见 §1.5） |
| 10 个同名 CSS 变量全部冲突（§1.5） | ✅ 10 个名字，0 个相同值 |
| 89 个 id / 88 被引用 / 唯一未引用 `stage-tag`（§1.6） | ✅ 完全正确 |
| `detectGesture` / `loadState` 两处同名不同实现（§1.4） | ✅ 且比计划说的更严重（见下） |
| `chat.js` 版本号 v11 vs v9 不一致（§1.2） | ✅ 且**共 2 处**不一致，`spine-player.js` 也是（pet `?v=2` vs pet-inspect `?v=1`） |
| `redesign.html` 全仓零引用（§1.10） | ✅ 只有文档文字提及，无代码引用 |
| `_verify_blink.html` 仅 `verify_l2d_blink.js` 引用（§1.10） | ✅ |
| CSP 禁内联 script（§1.9） | ✅ 已满足 |

**关于双实现，补充一条计划没说的事实**：不只是「同名不同实现」，是**关键词表都不一样**。

- `frontend/js/chat.js:52` `const GESTURES = { … }` —— **对象字面量，30 个关键词 / 9 种动作**
- `frontend/js/pet.js:105` `const GESTURES = [ … ]` —— **数组 of 二元组，12 个关键词 / 7 种动作**

pet 的 12 个关键词**完全被 chat 的 30 个包含**（交集 12、pet 独有 0、chat 独有 18），但有 **4 个词映射到不同动作**：

| 关键词 | chat.js | pet.js |
|---|---|---|
| `开心` | `b_liaofa` | `t_weixiao` |
| `为什么` | `b_shanzi` | `t_yihuo` |
| `什么` | `b_shanzi` | `t_yihuo` |
| `怎么` | `b_shanzi` | `t_yihuo` |

→ **同一句用户输入，在主站和桌宠页会触发不同的动作。** 这不是代码重复问题，是**行为已经分叉**。P4 合流时以 chat 的 30 条为准即可（它是 pet 的超集），但那 4 个动作要明确取哪一边 —— 现在两页对「为什么」的反应是相反的（chat 是鞠躬、pet 是疑惑）。

---

## 3. 三个阶段的人日数被低估

### 3.1 P1「质量网」1.5 → **4.1~4.6 人日**

| 项 | 计划估 | 实测估 | 原因 |
|---|---:|---:|---|
| `npm run lint` | ~0.3 | 0.4 | 见下方「ESLint 实测」—— 有一个必须知道的坑（`frontend/assets/**` 必须进 ignores），否则第一天就 78 条 error |
| `npm run typecheck` | ~0.2 | 0.2 | 加 15 个 `// @ts-nocheck` 即全绿 —— **但收益归零** |
| `npm run test` | ~0.3 | 0.5 | 两个环境坑（见下）+ 没有可测函数 |
| `tools/dom-contract.mjs` | **0.5** | **1.5~2.0** | index 单页 0.5 + pet/pet-inspect 页会爆 55 条假报错，需要豁免机制（见下） |
| 视觉基线 | ~0.2 | **1.0** | 4 个重复 shot 脚本要合并参数化（`shot_baseline.py` 2.2 KB / `shot_css.py` 4.1 KB / `shot_moth.py` 5.1 KB / `shot_real.py` 5.0 KB）+ 基线图不能全入库：`.agent_tmp/canvas_v1/moth/` 现在有 **595 张 PNG、合计 1,011.8 MB**（单张 0.01~2.86 MB） |
| `npm run check` 串联 | ~0.1 | 0.2 | — |
| 环境成本 | 0 | 0.3 | `.gitignore` 加根级 `node_modules/`（现在只有 `desktop/node_modules/`）、lockfile 入库 |
| **合计** | **1.5** | **4.1~4.6** | 逐项相加：0.4+0.2+0.5+1.5~2.0+1.0+0.2+0.3 |

（这 7 项按 §5 拆成两档：**P1a = 1.2**（lint 0.4 + dom-contract 的 index 单页版 0.5 + 环境成本 0.3）、**P1b = 2.9~3.4**（typecheck 0.2 + test 0.5 + dom-contract 的 pet/pet-inspect 部分 1.0~1.5 + 视觉基线 1.0 + check 串联 0.2）。）

**三个致命发现**：

**（0）ESLint 有个「不排除 `assets/` 就第一天红 78 条」的坑 —— 我自己踩了一遍。**

我在仓库根建了 `eslint.config.mjs` + 装 ESLint 10.13.0 实跑。**第一轮不排除 `frontend/assets/`** → **1733 problems（78 errors / 1655 warnings），2.96 s**。78 个 `error` 里有 **77 个来自 `frontend/assets/lib/*.min.js` 四个第三方压缩库**，只有 1 个是自家代码：

| 文件 | error | warning |
|---|---:|---:|
| `frontend/assets/lib/live2dcubismcore.min.js` | **53** | 464 |
| `frontend/assets/lib/pixi.min.js` | **14** | 205 |
| `frontend/assets/lib/pixi-live2d-display-cubism4.min.js` | **7** | 197 |
| `frontend/assets/lib/spine-player.js` | **3** | 509 |
| `frontend/js/canvas-fx.js` | **1** | 3 |

规则构成：`no-redeclare` 44 + `no-undef` 34。`no-undef` 全是 Emscripten/UMD 运行时符号（`process` / `require` / `__dirname` / `Buffer` / `printErr` / `Live2DCubismCore` / `module` / `define` / `exports`）。**把 `frontend/assets/**` 加进 `ignores` 之后**：

```
✖ 281 problems (1 error, 280 warnings)
exit=1  elapsed=1.33s
```

**唯一的 error 就是 `frontend/js/canvas-fx.js:1519:11  'ty' is already defined  no-redeclare`** —— 与先前实测完全一致。280 条 warning 的分布：

| 规则 | 条数 | 说明 |
|---|---:|---|
| `no-unused-vars` | **153** | 大多是 `catch (_)` 的 `_`，属风格问题，设 baseline 即可 |
| `no-empty` | **97** | `catch (_) {}` 的空块，同上 |
| `eqeqeq` | **30** | `==` vs `===`，改成 `warn` 不卡闸门 |

涉及 **15 个文件**（16 个 js 里**只有 `frontend/js/live2d-bootstrap.js` 零告警**）。告警最密的四个：`frontend/js/live2d.js` 76、`frontend/js/pet.js` 49、`frontend/js/spine.js` 35、`frontend/js/chat.js` 27。→ **`npm run lint` 的可行配置已实测跑通，1.33 s。** 结论：`0 error` 这个闸门是**现在就能立的**，前提是配置里排除 `assets/`、并把三条风格规则设成 warning。

**（a）dom-contract 在 pet 页会第一天就红 55 条。** 原型实跑：

```
index.html         ids=89  BROKEN=0   UNREF=1
pet.html           ids=67  BROKEN=55  UNREF=28
pet-inspect.html   ids=23  BROKEN=0   UNREF=4
```

55 条全是跨页污染、**0 条真 bug**：`chat.js` 52 条、`voice.js` 4 条、其余各 1。根因是 `frontend/js/chat.js:21` 的运行时守卫：

```js
const PET_MODE = document.body.dataset.mode === "pet" || !document.getElementById("send-btn");
// chat.js:828 / 1003 / 1330 / 1349
if (!PET_MODE) { … }
```

静态工具看不见 `PET_MODE`。→ **必须内置豁免或每页白名单，这就是 0.5 → 1.0~1.5 的原因。**

反向 UNREF 的假阳性同样严重，而且我先前说的「19%」其实低估了。把 pet.html 的 67 个 id 逐个查引用面：

| 类别 | 数量 | 说明 |
|---|---:|---|
| 被 JS 字面量引用 | 62 | 正常契约 |
| 仅被 CSS 选择器引用 | 2 | `#pet-brand`、`#menu-dnd-exit`（`<style>` 自身的 `pet-critical` 也无人引用） |
| **真死 id** | **2** | **`#i-send`（`frontend/pet.html:160`）、`#i-help`（`:162`）** |

`#i-send` / `#i-help` 是两个 `<symbol>`，在 `frontend/` + `desktop/src/` + `desktop/scripts/` 全域（排除 `node_modules` / `assets/lib`）**除自身声明外零引用** —— 没有 `<use href>`、没有 JS `setAttribute`、没有 CSS。而另外 18 个 symbol 的 `UNREF` 是假阳性（被 `<use href="#i-*">` 引用，静态工具看不见）。**→ 32% 的假阳性率，且顺带挖出 2 个真死 symbol。**

（这也解释了为什么 dom-contract 的 `UNREF` 一栏**不能**直接当"死代码列表"用 —— 它需要「SVG `<use href="#id">` 也算引用」这条规则，否则第一天就有 18 条噪音。）

**（b）Vitest 在本机有两个硬坑**：默认 forks pool → `spawn EPERM`，必须 `--pool=threads`；**只要存在 `vitest.config.mjs` 就起不来**（vite 在 Windows 上 `exec("net use")` 探测网络驱动器被拦）→ 必须放弃 config 文件、全走 `package.json` scripts。

**（c）tsc / Vitest / 3.2 四条硬规则在 P1 阶段「没有可校验对象」**：`import`/`export` 语句数 = 0，`frontend/src/` 目录还不存在。P1 验收里「故意在 `features/x` 里 import `features/y` 能被 lint 抓到」是**空验收**。

→ **建议把 P1 拆成两档**（详见 §5）。

---

### 3.2 P5「样式统一」2.5 → **7.5~9.5 人日**

我独立复算的隐藏成本：

| 项 | 实测数字 |
|---|---|
| `var()` 引用总数 | **562**（`index.css` 308 / `pet.css` 227 / `pet-inspect.css` 24 / `pet-subtitle.css` 3） |
| `index.css` 硬编码 px | **476** 个（涉及 **352** 行） |
| `index.css` `font-size` 声明 | **79** 处 |
| `index.css` 十六进制颜色字面量 | **32** 处 |
| `index.css` `rgba()` 字面量 | **61** 处 |
| `pet.css` 硬编码 px | **129** 个（涉及 **111** 行） |
| `pet.css` `font-size` 声明 | **25** 处 |
| `!important` | 全仓 5 处，**全是 `prefers-reduced-motion` 关动效，无业务性 `!important`** |
| `@media` 块 | `index.css` **10** 个 / `pet.css` **7** 个 |

（口径：所有计数都在**剔除注释后**的正文上统计；若把注释里写到的 px 也算上，`index.css` 是 485 个 / 358 行，`pet.css` 是 131 个 / 113 行。）

**最贵的一项是「重命名 562 处 `var()` 引用」** —— 计划完全没提这一项，但它比「拆文件」贵得多。

**P5 验收的三处硬伤**（§2.7 已说 pet 无主题）：

1. 「pet 页 5 区域 × 2 主题」—— **无法执行**，pet 页没有 `data-theme`
2. 「所有 `--var` 可解析」—— **会误报 5 个**：`--fx-clr` `--fx-dx` `--fx-dy` `--sub-lift` `--sub-maxh` 只由 JS `setProperty` 注入，CSS 从未声明（我复核确认正好这 5 个）
3. 「移动端 3 个断点」—— `index.css` 有 **10 个 `@media`**，3 个断点只覆盖一部分（1440 / 1024-1439 / 768-860 / 861+ 四个桌面断点无验收）

**另附一条（这条我改了主意）**：`@layer` 的动机在计划里写的是「替代现在的特异性互压」。实测：

- 业务性 `!important` = **0 处**（全仓 5 处全在 `prefers-reduced-motion` 关动效）
- 选择器最深仅 3 层
- **跨文件层叠竞争根本不存在**（`index.css` 与 `pet.css` 永不同页加载）

那「后写覆盖前写」呢？我写了个 CSS 规则解析器精确统计（排除 `@keyframes` 内部的 `from`/`to`/`0%`）：

| 文件 | 真规则数 | distinct selector | 重复 selector | 重复产生的额外规则 | **其中「同一层叠上下文内后写覆盖前写」** |
|---|---:|---:|---:|---:|---:|
| `frontend/css/index.css` | 272 | 249 | 16 | 23 | **0** |
| `frontend/css/pet.css` | 132 | 124 | 6 | 8 | **2**（`#pet-brand`、`.chip`） |

**index.css 的 23 处「重复」全部是「基础规则 + `@media` 覆盖」**（如 `#app` x5 = 1 基础 + 4 个断点，`:root` x4 = 1 基础 + 3 个断点）—— 这是响应式 CSS 的正常写法，**不是顺序敏感**，而且 `@layer` 对此毫无帮助（媒体查询不产生 layer）。

→ **`@layer` 的真实收益接近于零。** 建议从 P5 里删掉，或降为纯可选项（真要防回归，`stylelint` 的 `no-duplicate-selectors` 更直接）。这是我对先前结论的修正：style-reviewer 说的「27 处顺序敏感」经精确统计是 **0 处（index）+ 2 处（pet）**。

**降级方案**：如果只想「止血」不想大动，可以只加 `tokens.css`（语义名 + 旧名别名）+ 三份 theme 调色板，**不拆文件、不重命名**，约 2.5~3 人日。观感零变化，但「同名不同值」这个病灶被消灭。建议先做这个，重构留到有真实需求时。

---

### 3.3 P6 2.0 → **2.5~3.5 人日**（我先前说「拆分不难」，这句要收回）

理由一：`?fx=off` 不存在（§1.2）、「异常全静默」没实现（§1.3）→ 参数机制 + try/catch 都要从零做。

理由二（**新发现，我先前写「函数边界清楚」是错的**）：我按计划的目标模块把 24 个顶层函数逐条归类，量了行数：

| 目标模块 | 会分到 | 占比 | 主要来源 |
|---|---:|---:|---|
| `lamp.js` | **724 行** | 41.0% | `drawLampHardware` **515** + `drawLightPool` 139 + `drawSubjectLight` 39 + `drawLampGlow` 31 |
| `moth.js` | **607 行** | 34.3% | `buildMothSpriteSharp` **289** + `Moth` **243** + 小函数 |
| `index.js` | 259 行 | 14.6% | `start` 113 + `drawFrame` 44 + `reset` 41 + 工具函数 |
| `cone.js` | 149 行 | 8.4% | `drawCone` 84 + 尘粒三函数 |
| `backdrop.js` | **29 行** | 1.6% | `drawBackdrop` 一个函数 |

**最大 / 最小 = 25 倍。** 拆完 `lamp.js` 724 行、`backdrop.js` 29 行 —— 这不是「模块化」，这是把一个 1,756 行的文件换成一个 724 行的文件 + 一个 29 行的文件。

**根因是三个巨型函数**：

| 函数 | 行数 | 位置 |
|---|---:|---|
| `drawLampHardware` | **515** | `frontend/js/canvas-fx.js:1108-1622` |
| `buildMothSpriteSharp` | **289** | `frontend/js/canvas-fx.js:171-459` |
| `Moth` | **243** | `frontend/js/canvas-fx.js:494-736` |

（顺带解释 §1.5 那条 ESLint error 为什么在 `canvas-fx.js:1519`：它就在这个 515 行的 `drawLampHardware` 里面，和 `:1174` 的 `var ty` 同一个 `var` 作用域。）

→ **P6 的实际工作量不是「5 个文件搬家」，是「先把 3 个巨型函数内部拆开，再搬家」。** 建议把 `lamp.js` 再按 `glow` / `hardware` 二分（`drawLampHardware` 内部可按灯罩/灯泡/吊线/光晕切成 4~5 段），`backdrop.js` 考虑并入 `index.js`（29 行不值得单开一个文件）。这样模块大小能落到 150~350 行的合理区间。

---

## 4. 七个待拍板项的建议

| # | 计划建议 | 我的建议 | 变化 |
|---|---|---|---|
| **Q1** | Plan A（无构建 ESM） | **A′：无构建 ESM，且不用 importmap** | **必须改**：importmap 技术上能绕过 CSP（我实测通了），但 4 个库是 UMD，绕过也白绕（§1.1） |
| **Q2** | JS + JSDoc | **同意**，但**推迟到 P2 之后** | 微调：P1 阶段 `@ts-nocheck` 让收益归零，不如等 ESM 出现再上 |
| **Q3** | `redesign.html` 移 `docs/design/` | **留在 `frontend/` 改名 `_design-archive.html`** | **改**：移 docs 会打不开（§2.2） |
| **Q4** | `pet-inspect` 移 `tools/` | **同意**，但要同步改 `docs/roleplay-core/architecture/ARCHITECTURE.md` 里的路径引用 | 补一条 |
| **Q5** | 保持两套主题 | **同意**，但前提是 Q6 的答案 | 依赖 Q6 |
| **Q6** | 「紫主题是有意的吗？」 | **已查清：是有意的，但它推翻了风格板**。真问题改成：「当初否决金铜方案、选紫色的决定还算数吗？」 | **重写**（§2.3） |
| **Q7** | 暂停视觉迭代 | **同意**，且建议冻结期延长到 P5 结束（因为 P5 要动全部颜色变量） | 微调 |

---

## 5. 修订后的阶段计划

| 阶段 | 计划 | 修订 | 说明 |
|---|---:|---:|---|
| P0 基线快照 | ✅ | ✅ | 已完成，无需动 |
| **P0.5 修 CSP bug** | — | **0.2** | **新增**：`connect-src 'self' http://127.0.0.1:*`，让桌宠通道 B 复活（§2.1，已 A/B 实证）。独立于重构，建议先修 |
| **P1a 必须做的质量网** | 1.5 | **1.2** | `node --check` 闸门 / ESLint 基础版（修 `canvas-fx.js:1519`）/ dom-contract 的 **index 单页版**（89 id，0 假阳性，验收已通过）/ `.gitignore` 加根 `node_modules/` + lockfile / 搬 `audit2.py`+`region.py`+`ascii.py` 进 `tools/`（这三个零内部依赖，纯 numpy+PIL，搬走即用；`shot_real.py` 有 3 处硬编码要参数化，见 §3.1） |
| **P1b 延后的质量网** | — | **2.9~3.4** | tsc checkJs 0.2 / Vitest 0.5 / dom-contract 的 pet+pet-inspect 页 1.0~1.5 / 视觉基线 1.0（需要能跑 Chromium 的环境）/ `npm run check` 串联 0.2 —— **全部等 P2/P3 有对象了再做**。3.2 四条硬规则并进 P2 之后 |
| P2 core + data | 2.0 | 2.0 | 合理，无需改 |
| P3 chat 页切换 | 3.0 | 3.0 | 合理。补一条：`RoleplayChat` 过渡 shim 必须标 `// TODO(P4)` 且**只许变薄** |
| P4 pet 页切换 | 3.5 | 3.5 | 合理。改三条：探针 22 个不是 11 个；`detectGesture` 关键词表要统一（以 chat 的 30 条为准，它是 pet 12 条的超集；但那 4 个映射不同的词要拍板）；`PET_MODE` 守卫删除后 dom-contract 才能覆盖 pet 页 |
| **P5 样式统一** | 2.5 | **2.5~3（止血）或 7.5~9.5（全量）** | 建议先做止血版：`tokens.css` 语义名 + 旧名别名 + 3 份 theme 调色板，**不拆文件、不重命名**。全量拆分等真实需求。**止血版顺手做一件零风险的事：删掉 `frontend/pet.html:11-37` 那 5 个无人引用的 `--c-*` 变量（§2.6）** |
| P6 装饰层 | 2.0 | **2.5~3.5** | 参数机制从零做 + 补 try/catch + **三个巨型函数内部要先拆**（§3.3） |
| P7 清理 | 1.0 | 1.0 | 合理 |
| **合计** | **15.5** | **约 18.8~20.8（止血版）/ 23.8~27.3（全量版）** | 逐项相加：0.2+1.2+2.9~3.4+2.0+3.0+3.5+2.5~3.0+2.5~3.5+1.0 |

**建议节奏**（修订）：
1. **P0.5 单独一次提交先上线**（一行 CSP，纯收益，修一个既存 bug）
2. **P1a 单独一次上线**（纯新增文件，零风险）
3. P2 跟上（不改调用，零风险）
4. P3 / P4 之间隔一次完整回归
5. **P5 只做止血版**，全量拆分单独立项
6. P6 可以与 P5 并行（不同文件）

---

## 6. 一句话给决策者

**这份计划的骨架可以直接用 —— 目录结构、依赖方向、拆分粒度、六个技术决策、风险登记，都是对的，而且比大多数重构计划扎实（26 个文件的数字全对）。**

**只需要改三件事（外加一件零风险的小清理）：**

1. **删掉 importmap**（CSP 其实能绕，但 4 个库是 UMD，绕过去也是空的；改一行字的事，但不改会卡住 P3）
2. **把 P1 / P5 / P6 的人日数按实测重估**（P1 拆成两档共 4.1~4.6，P5 先止血 2.5~3，P6 涨到 2.5~3.5）
3. **修那个 CSP 的 `connect-src` bug**（跟重构无关，但桌宠的「检测桌面端是否运行」现在是 100% 坏的）

> 零风险附带项：`frontend/pet.html:11-37` 的内联 `<style>` 里有 5 个 `--c-*` 变量声明后**全仓无人引用**（§2.6），顺手删掉即可，观感零变化。

**然后回答一个问题就够了：Q6 —— 桌宠页的紫色，是继续保留，还是回到风格板的金铜？** 这一个答案决定 P5 是 2.5 人日还是 9 人日。

---

## 附录 A：实测环境

- 解释器：`.\.venv\Scripts\python.exe -X utf8`
- 后端：`.\.venv\Scripts\python.exe -X utf8 -m uvicorn roleplay.main:app --host 127.0.0.1 --port 8000 --app-dir src`（**必须带 `--app-dir src`**，启动 50~90 s）
- 后端测试：`.\.venv\Scripts\python.exe -X utf8 -m pytest -q` → `1464 passed, 8 skipped in 410.21s`
- 浏览器：Playwright + `C:\Users\Lenovo\AppData\Local\ms-playwright\chromium-1208\chrome-win64\chrome.exe`，`headless=True`，args `["--no-sandbox", "--disable-crash-reporter", "--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"]`
- node v24.14.1 / npm 11.11.0，registry `https://registry.npmmirror.com`

## 附录 B：本次评审用的实测脚本

全部在 `.agent_tmp/review/`（未入库）：

| 脚本 | 作用 |
|---|---|
| `verify_plan_numbers.py` | 独立复算 id 契约 / import-export 数 / window 全局 / localStorage 键 / 动态拼 id |
| `verify_claims.py` | 逐条核对 §1.5 / §1.8 / §1.9 的具体断言 |
| `verify_style_numbers.py` | 复算 `var()` 引用数、硬编码密度、`@font-face`、`data-theme` |
| `verify_p5_p6.py` | 复算 JS 注入变量 / `--z-*` 死变量 / `.stage` 跨文件依赖 / 三页 `data-theme` |
| `verify_final_css.py` | 终检：`var()` / `!important` / `--z-*` / `setProperty` / `@media` / `@layer` 六项一次算全 |
| `verify_css_stats_table.py` | 两种口径（含/不含注释）并列复算 §3.2 的 CSS 统计表 |
| `verify_px_count.py` | 硬编码 px 的行/个双口径，剔除注释 |
| `verify_pet_unref.py` + `verify_pet_unref2.py` | pet.html 67 个 id 与 22 个 `<symbol>` 的引用面（挖出 `#i-send` / `#i-help` 两个真死 symbol） |
| `verify_gestures.py` | chat / pet 两份 `GESTURES` 的关键词表与动作映射对比 |
| `verify_bare_globals.py` | 裸标识符行数、`index.html` 标签统计 |
| `verify_scope.py` | 代码级引用 61 处、`canvas-fx.js` try/catch=0、`:1174`/`:1519` 同属 `drawLampHardware` |
| `verify_bare_count.py` | 61 处按行计数（qualified / local-alias / truly-bare） |
| `verify_bare_forms.py` | 把 61 处三分：qualified（`global.X`）30 / local-alias 21 / truly-bare 10 |
| `verify_final_checks.py` | 交付前终检：旧数字零残留、表格竖线对齐、附录脚本存在性 |
| `scan_desktop_selectors.py` | `desktop/scripts` 的选择器形态统计 |
| `verify_desktop_selectors.py` | 逐文件复现 §2.8 的 57 处选择器表（19 querySelector + 38 getElementById） |
| `scan_dead.py` | 死代码文件的全仓库引用扫描（显式排除 `.venv`/`vendor`/`node_modules`/`.agent_tmp`） |
| `csp_probe.py` | 内联 importmap 被 CSP 拦的真实报错 |
| `csp_fix_proof.py` | **A/B 实证** `connect-src` 修正：两个静态服务对照，现网 FAIL / 修正后 OK |
| `importmap_inject_probe.py` | 内联注入器 + DOM 注入 importmap（A：原样 / B：加 `'unsafe-inline'`） |
| `importmap_external_injector_probe.py` | 外部注入器 + DOM importmap（混合变量，用于定位失败点） |
| `importmap_isolate_probe.py` | **外部注入器 + 外部 module**，隔离出「importmap 未生效」这一个变量 |
| `importmap_isolate_control.py` | 上一条的对照：CSP 加 `'unsafe-inline'` → 证明注入方案本身可用 |
| `importmap_hash_probe.py` | 第一版 hash 实验（**失败**：hash 按带空格的 JSON 算，与 textContent 不符） |
| `importmap_hash_probe2.py` | **第二版 hash 实验（成功）**：紧凑 JSON + 对应 hash → 0 违规 |
| `verify_css_order.py` | CSS 规则解析器：精确统计重复 selector 与「同一层叠上下文内后写覆盖前写」 |
| `verify_p6_split.py` | 按计划目标模块归类 canvas-fx.js 的 24 个函数，量拆分后各文件行数与均衡性 |
| `desktop_pet_csp_count.py` | 真实首页 42 条 console 违规的结构化计数 + `#pet-status-dot` 实际状态 |
| `desktop_pet_csp_breakdown.py` | 42 条按文本形态分类，确认 21 端口 × 2 条 |
| `shots.py` | 四视口截图 + 视觉指标复算 |
| `gate_probe.py` | 视觉闸门四阈值的分视口实测 |

---

*评审基于 2026-10-19 的实测；行号以 commit `1c5966f` 为准。*
