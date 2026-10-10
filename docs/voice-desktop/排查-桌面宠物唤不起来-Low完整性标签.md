# 排查：桌面宠物唤不起来 —— Low 完整性标签导致 Electron 降权

> **结论一句话**：网页点「桌面宠物」无反应，根因是 **仓库文件被打了
> `Mandatory Label\Low Mandatory Level` 完整性标签**，Windows 据此把 Electron 派生进程
> 降权为 LOW；LOW 进程既有权限不足创建 Chromium 沙箱的命名管道，也写不了 `AppData` 里的
> profile —— 两个报错是**同一个根因**。
>
> **这个标签是 agent 沙箱（DSH）在工作区内操作时施加的，不是本项目代码缺陷，也不是
> Windows / Electron 的 bug。** 换一个目录就完全正常。

---

## 1. 现象

- 网页顶栏点「桌面宠物」按钮，无任何窗口出现。
- `logs/desktop-pet-launch.err.log` 为 **0 字节**（关键：静默失败，无任何输出）。
- 控制服务端口 `39231~39251` 全部不可达。

## 2. 两个报错（同一根因）

| 触发条件 | 报错 |
|---|---|
| 不加开关启动 | `FATAL:mojo\public\cpp\platform\platform_channel.cc:108 Check failed: . : 拒绝访问。(0x5)`，进程以 `STATUS_BREAKPOINT 0x80000003` 崩溃，退出码 `-2147483645` |
| 加 `--no-sandbox` 启动 | `ERROR:chrome\browser\process_singleton_win.cc:446 Lock file can not be created! Error code: 5` |

**两个报错的错误码都是 `5` = `ERROR_ACCESS_DENIED`。** 这是指向根因的第一条线索 ——
它是**权限错误**，不是代码缺陷。

## 3. 根因

Windows **强制完整性控制（MIC）**：进程令牌有完整性级别（Low / Medium / High / System），
对象（文件、管道、互斥体）也有。规则是 **低完整性进程不能写入更高完整性的对象**。

Electron 可执行文件位于工作区内，而工作区目录带 `Low Mandatory Level` 标签，
Windows 在创建进程时按映像文件标签给进程降权：

```
icacls <repo>            -> Mandatory Label\Low Mandatory Level:(OI)(CI)(NW)
icacls <repo>/desktop/…  -> 继承同上
```

进程变成 LOW 之后，两件事同时失败：

1. **Chromium 沙箱初始化**需要创建命名管道（Mojo channel），LOW → 拒绝访问 → `0x5` 自毁；
2. **`AppData` profile**（Medium 完整性）无法写入，单实例锁都建不了 → `Error code: 5`。

这解释了为什么 `electron.exe --version` 也崩 —— 该路径不加载本项目任何代码，
所以**必然不是业务代码回归**。

## 4. 决定性判据

### 4.1 换目录即好（排除 OS / Electron bug）

同一个文件、同一台机器、同一个版本：

| `electron.exe` 位置 | 进程完整性 | `electron.exe --version` |
|---|---|---|
| 工作区内 | **LOW (0x1000)** | 崩溃 `-2147483645` |
| 复制到工作区外 | **MEDIUM (0x2000)** | `exit=0` → `v43.4.0` |

**若是系统 bug，换个目录不可能好。**

### 4.2 唯一变量对照（闭锁因果）

只改这一个文件的完整性标签：

| `icacls <exe> /setintegritylevel …` | 派生进程完整性 |
|---|---|
| `Low` | **LOW (0x1000)** |
| `Medium` | **MEDIUM (0x2000)** |

### 4.3 版本矩阵（推翻"某版本 Electron 有 bug"）

`31.7.7 / 33.4.11 / 43.4.0 / 43.7.5 / 44.4.5` **全部**表现一致：工作区内崩、工作区外正常。
→ 与 Electron 版本无关。

## 5. 修复

清除整棵仓库的 Low 完整性标签：

```powershell
icacls <repo> /setintegritylevel Medium /T /C /Q
```

实测清除 165,245 个文件。

**修复后**（不加任何启动开关）：

| 检查 | 结果 |
|---|---|
| `electron.exe --version`（原先必崩） | `exit=0 → v43.4.0` |
| 直接用真实默认 profile 启动 | 存活，`39231` 正常 |
| `POST /api/desktop-pet/launch`（网页按钮路径） | **1 秒内就绪** |
| `GET /state` | `{"ok":true,"version":"0.2.0","state":"running"}` |

**注意**：修复是持久的 —— 标签清除后，新写入的文件**不会**再被打上 Low
（父目录已是 Medium，子项继承 Medium）。若 agent 会话在别处重新触发降权操作，可能复发。

## 6. 自查 / 复现

```powershell
# 1) 看文件/目录的完整性标签
icacls <path> | findstr "Mandatory"
#   出现 Low Mandatory Level 即为元凶

# 2) 看进程的完整性级别（令牌 IL=25，读 SID 末位子授权）
#    0x1000=LOW  0x2000=MEDIUM  0x3000=HIGH
#    期望 Electron 子进程是 MEDIUM；若是 LOW 则必然出上述两个报错

# 3) 最快判别（无需任何日志）
<repo>\desktop\node_modules\electron\dist\electron.exe --version
#    崩溃 -2147483645 => 命中本问题
#    exit=0 输出版本 => 正常
```

**三条特征同时出现即可确诊**：报错码统一为 `5`（拒绝访问）· 换目录就正常 ·
`--version` 这类不加载业务代码的路径也崩。

## 7. 结论的确证边界（哪些是实测，哪些是推断）

> 这一节刻意区分**实测事实**与**推断**，避免后人把推断当结论引用。

**已实测确证**（对照实验，可复现）：

- 文件完整性标签 → 进程完整性级别的因果（唯一变量对照，见 §4.2）；
- LOW 进程必然出 §2 的两个报错、且写不了 `AppData`；
- 清除标签后 §5 的全链路恢复正常。

**属于推断，未直接证实**：

- **标签首次施加的时间点无法回溯**。排查过程中执行的
  `icacls <repo> /setintegritylevel Medium /T` 是**全量重写**，
  已覆盖原始标签，事后无法从 ACL 反推"何时开始是 Low"。
  只能确认：仓库根带 `(OI)(CI)` 继承标签（即整个子树受影响），
  且排查期间**本会话新建的文件也会被实时打上 Low**
  → 说明施加方是 agent 会话的沙箱，而非某次性的手动操作。
- 因此"宠物 9/15 还正常、之后某次会话开始失效"只是**时间线推断**，
  依据是 `userData/config.json` 的 mtime，而非直接证据。

**未验证的风险**：

- 复发条件未知。修复后实测新建文件**不再**被打 Low（父目录已是 Medium，
  子项继承 Medium），但若 agent 会话在其他路径重新触发降权写入，理论上可能复发。
  复发时用 §6 的命令自查即可。

## 8. 走过的弯路（教训）

1. **误判为「Windows 11 25H2（build 26200）的 Electron 沙箱 bug」**，引上游 issue 佐证，
   并据此加了 `--no-sandbox` 启动垫片（改动 `desktop/package.json`、
   `desktop/src/main/index.js` 协议注册、`src/roleplay/api/desktop_pet.py`）。
   这些都是**基于错误诊断的改动，已全部还原**：

   ```powershell
   git log --oneline -1 -- desktop/package.json desktop/src/main/index.js src/roleplay/api/desktop_pet.py
   # 应停在本次排障之前的提交；三处均无 `--no-sandbox` / launch-electron.js 残留
   ```

   教训：**"版本矩阵全崩"本应更早推翻"某版本 bug"的假设** —— 当时只测了 43/44，
   补测 31/33 后才彻底排除。报错码 `5` 是权限错误这条更早的线索也被我忽略了。

2. **误判为「只是 agent 沙箱的产物，用户机器没问题」**。这个结论也错了：
   用户真实点击留下了同样的 `Lock file ... Error code: 5`，
   说明**用户环境确实被影响**了（因为沙箱污染的是仓库文件本身的标签）。

3. `--no-sandbox` 之所以"看起来有效"，只是**绕过**了沙箱路径，属于治标：
   它让进程不去创建命名管道，但没能解决降权问题（同一进程仍写不了 AppData）。
   **真正的修复是恢复文件完整性标签**，之后连开关都不需要。

## 9. 关联文件

| 文件 | 作用 |
|---|---|
| [`desktop/package.json`](../../desktop/package.json) | `npm start` = `electron .`（已还原，无垫片） |
| [`desktop/src/main/index.js`](../../desktop/src/main/index.js) | 主进程入口；`roleplaypet://` 协议注册 |
| [`desktop/src/main/control-server.js`](../../desktop/src/main/control-server.js) | 回环控制服务（`39231`，`/ping` `/launch`） |
| [`src/roleplay/api/desktop_pet.py`](../../src/roleplay/api/desktop_pet.py) | 后端拉起桥接 `POST /api/desktop-pet/launch` |
| [`frontend/js/desktop-pet.js`](../../frontend/js/desktop-pet.js) | 前端按钮：探测 / 唤起 |
| [`pet-design/DESKTOP_PET_DESIGN.md`](pet-design/DESKTOP_PET_DESIGN.md) | 桌宠设计说明（经 `/docs/DESKTOP_PET_DESIGN.md` 提供） |
