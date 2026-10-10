# 06 仓库卫生与一致性审计报告

> 审计性质：**只读**。除本报告文件外，未创建/修改/删除任何项目文件。
> 审计时间：2026-07-27 会话 | 工作目录：`C:\Users\Lenovo\WorkBuddy\2026-07-27-16-45-03\roleplay-ai`
> 方法：`Get-ChildItem` 递归统计、`git ls-files -z`（`core.quotepath=false`，规避非 ASCII 路径转义）、
> `git check-ignore -v --no-index`、`git ls-files -i -c --exclude-standard`、`.venv\Scripts\python.exe -m pip list`、
> 正则扫描 `src\` + `scripts\` 的 top-level import。

**总览结论**：仓库整体卫生**中上**——`.gitignore` 写得相当用心（分「种子/派生物」原则，还带 SHA-16 冻结锁意识），
根级临时垃圾几乎全部已被忽略，密钥**未被 git 跟踪**。但存在 **1 个致命问题**
（4055 个文件同时处于「已跟踪 + 已被 .gitignore」的矛盾状态，`.git` 已膨胀到 **1.36 GB**），
以及依赖声明与实际安装版本**系统性不符**（pin 形同虚设）。

---

## 1. 临时垃圾清单

### 1.1 根级临时产物（审计目标项）

| 路径 | 大小 | 最后修改 | 是否被 .gitignore 忽略 | 可否安全删除 |
|---|---|---|---|---|
| `.pytest_bt/` | 0 B（0 文件，空目录） | 2026-09-21 11:53 | ✅ 已忽略（`.gitignore:90`） | ✅ 可删（空目录） |
| `.pytest_cache/` | 0 B（0 文件，空目录） | 2026-09-20 19:11 | ✅ 已忽略（`.gitignore:40`） | ✅ 可删（pytest 自动重建） |
| `.pytest_tmp/` | 0 B（0 文件，空目录） | 2026-09-08 22:29 | ✅ 已忽略（`.gitignore:92`） | ✅ 可删 |
| `.pytest_tmp2/` | 0 B（0 文件，空目录） | 2026-09-09 22:05 | ✅ 已忽略（`.gitignore:92`） | ✅ 可删 |
| `.pytest_tmp3/` | 0 B（0 文件，空目录） | 2026-09-11 00:04 | ✅ 已忽略（`.gitignore:92`） | ✅ 可删 |
| `.pytest_ws/` | 0 B（0 文件，空目录） | 2026-09-29 09:41 | ✅ 已忽略（`.gitignore:91`） | ✅ 可删 |
| `pytest-of-Lenovo/` | 0 B（0 文件，空目录） | 2026-09-21 11:52 | ✅ 已忽略（`.gitignore:93`） | ✅ 可删 |
| `roleplay_test_qenmhfwr/` | 0 B（0 文件，空目录） | 2026-09-21 11:52 | ✅ 已忽略（`.gitignore:94`） | ✅ 可删（pytest tmpdir 残留） |
| `tmp_pytest/` | 0 B（0 文件，空目录） | 2026-09-29 11:33 | ✅ 已忽略（`.gitignore:43`） | ✅ 可删 |
| `_shuzhi_extract.txt` | 14,075 B（13.7 KB） | 2026-09-06 20:53 | ✅ 已忽略（`.gitignore:57`） | ✅ 可删（一次性抽取探针产物） |
| `_tmp_pron_edges.txt` | 15,057 B（14.7 KB） | 2026-09-07 23:18 | ✅ 已忽略（`.gitignore:58`） | ✅ 可删（一次性指代边探针） |
| `.env.env.bak.20260831_232917` | 3,733 B（3.6 KB） | 2026-08-31 20:09 | ✅ 已忽略（`.gitignore:34` `.env.*.bak*`） | ⚠️ **先核验再删**：是 `.env` 备份，**很可能含明文密钥**。删前确认已有替代密钥源，且**它本身也应在清理密钥轮转后销毁** |

**小计**：根级临时产物 ≈ **33 KB**（12 项中 11 项为空目录）+ 1 份 3.6 KB 的 `.env` 备份。
体积上微不足道，但**污染 `git status` 的观感成本很高**。

### 1.2 判定说明（是否为临时产物）

- 9 个 pytest 相关目录**全部为 0 文件的空目录**（已逐个 `-Recurse -Force` 计数确认）。
  说明 pytest 跑完后清理了内容但留下了目录骨架。**100% 是沙箱产物**，无任何数据价值。
- `_shuzhi_extract.txt` / `_tmp_pron_edges.txt`：`_` 前缀 + `.gitignore` 已显式标注
  「一次性抽取/探针产物（勿入库）」，是当时调试「数智抽取」「指代边」的中间输出，可删。
- `.env.env.bak.*`：**名字是备份，但内容是密钥**。它已被忽略（不会进 git），
  风险在于**本机明文留存 + 未来误 `cp` 到未忽略路径**。建议：确认无用后删除；
  若需保留，移到 `.git` 之外的受控位置（如密码管理器/加密卷）。

### 1.3 .gitignore 覆盖度评价

✅ **做得好**：本节 12 项**全部**已被 `.gitignore` 覆盖，且是**分类带注释**地覆盖
（`第 42-44 行`审计/探针临时目录、`第 87-95 行`「本机运行残留（2026-09-29 整理补充）」）。
历史上这些目录确实未列入，已在 2026-09-29 补齐——**不存在「未忽略的污染源」这一项**。

> 唯一遗留：`scripts/__pycache__/`（40 个文件）与 `src/**/__pycache__/`。
> 根 `.gitignore` 有 `__pycache__/`（第 3 行），可覆盖；但它们是**运行产物**，
> 若某处被 `git add -f` 过需单独查。本次 `git ls-files` 未发现 `.pyc` 入库。

---

## 2. 密钥与 git 跟踪风险（只写变量名，不含任何值）

### 2.1 根目录 `.env` 检查

- **`.env` 存在**：5,804 B，最后修改 2026-09-19 10:39。
- **已被 `.gitignore` 忽略**（`.gitignore:32` → `.env`）。
- **`git ls-files | Select-String "\.env"` 结果：仅 `.env.example`**（模板，无真值）。
  → **真实 `.env` 未被 git 跟踪，未进入版本库** ✅

### 2.2 疑似含密钥的变量名（仅列名，不含值）

`.env` 共 43 个变量，按「名称含 KEY/TOKEN/SECRET/PASS/API 且值非空非占位」筛选，命中 **3 个**：

| 变量名 | 判定 | 说明 |
|---|---|---|
| `ROLEPLAY_LLM_API_KEY` | 🔴 **疑似密钥（真值）** | 16 字符，非占位符。LLM 供应商 API Key |
| `ROLEPLAY_QQ_WS_TOKEN` | 🔴 **疑似密钥（真值）** | 16 字符，非占位符。QQ/OneBot WebSocket 鉴权 Token |
| `ROLEPLAY_LLM_BASE_URL` | 🟡 端点（含凭据风险） | 24 字符。若 URL 内嵌 `?key=`/userinfo 则等价泄露，建议人工确认 |
| `ROLEPLAY_MAX_TOKENS_PER_REPLY` | ⚪ 误报 | 名称含 TOKEN 但为数值上限（3 字符），**非密钥** |

> 另有 `ROLEPLAY_QQ_ADMIN_UIN` / `ROLEPLAY_QQ_BOT_UIN`（各 10 字符）为**账号标识符**而非密钥，
> 但同属敏感个人信息，不建议随 `.env` 外传。

### 2.3 `.gitignore` 是否忽略 `.env` 与 `*.bak`

| 规则 | 位置 | 覆盖情况 |
|---|---|---|
| `.env` | 第 32 行 | ✅ |
| `.env.*.local` | 第 33 行 | ✅ |
| `.env.*.bak*` | 第 34 行 | ✅ 覆盖 `.env.env.bak.20260831_232917` |
| `*.bak` | 第 51 行 | ✅ 通用兜底 |
| `*.bak-*` | 第 52 行 | ✅ |
| `*.tmp` / `*.log` | 第 53-54 行 | ✅ |

→ **`.env` 与 `*.bak` 均已正确忽略** ✅

### 2.4 git 是否跟踪了应忽略的文件 ⚠️ **本报告最严重发现**

```
git ls-files 总数            : 7032
node_modules 命中            : 0      ✅ 干净
.env（真实）命中             : 0      ✅ 只有 .env.example
data/ 命中                   : 6164   ⚠️ 占全部跟踪文件的 87.7%
models/ 命中                 : 4
desktop/ 命中                : 20
frontend/ 命中               : 272
docs/ 命中                   : 65
src/ 命中                    : 88
scripts/ 命中                : 348
tests/ 命中                  : 54
```

**`git ls-files -i -c --exclude-standard`（已跟踪 ∩ 已被忽略）= 4055 个文件**

| 目录 | 已跟踪且已被忽略的文件数 | 工作区字节 |
|---|---|---|
| `data/compendium_rag/` | **4036** | ~255 MB（跟踪部分） |
| `data/eval_set_i/` | **19** | 同上 |
| **合计** | **4055** | **267,606,022 B ≈ 255.2 MB** |

**这是致命的，原因有三：**

1. **规则与快照矛盾**：`.gitignore:13` 写的是 `data/*`（配合 `!data/lore/`、`!data/characters/`、`!data/knowledge/` 三条白名单），
   所以 `data/compendium_rag/` **当前是被忽略的**；但它在加入忽略规则**之前**就已被 `git add` 跟踪了。
   Git 的语义是「**已跟踪文件不受 .gitignore 约束**」——于是这 4055 个文件：
   - 仍然存在于每一个 clone 中（所以 `.git` 达 **1.36 GB**）；
   - 又**不再被 `git status` 监控**，后续对它们的修改**会被静默忽略**，`git add .` 不会带上更新。
   即：**既占空间，又失去版本控制**——两头不讨好。
2. **历史不可逆**：这些 blob 已写入 git 对象库，**仅改 `.gitignore` 不会缩小 `.git`**。
   必须 `git rm --cached -r data/compendium_rag data/eval_set_i` + 历史重写（filter-repo/BFG）才能真正瘦身。
   ⚠️ 历史重写会改变所有 commit SHA，**需全团队协调**，且 `.gitattributes` 里对
   `data/compendium_rag/repairs_v*/**.md` 声明的 **SHA-16 冻结锁**会因 SHA 变化而**全部失效**——
   这是「证据链」和「仓库瘦身」之间的真实冲突，必须由项目 owner 裁决。
3. **`data/` 总量**：工作区 `data/` = **1,184.2 MB / 73,937 个文件**，其中被跟踪的 6164 个文件 = 365.3 MB。
   `data/compendium_rag/` 磁盘实际 **404.0 MB / 4123 文件**（跟踪 4036 + 未跟踪 87）。

**其他大体积目录的跟踪情况（均健康）**：

| 目录 | 磁盘大小 | git 跟踪数 | 是否被忽略 | 评价 |
|---|---|---|---|---|
| `models/` | **5,687.5 MB** | 4 | `models/**/*.onnx`、`*.safetensors`、`bge-reranker-*/` | ✅ 极干净。5.7 GB 权重几乎全在库外（2026-09-27 补的 `.safetensors` 规则关键） |
| `vendor/` | **1,472.4 MB** | 0 | `vendor/`（第 78 行） | ✅ 干净 |
| `desktop/` | 561.4 MB | 20 | `desktop/node_modules/`、`dist/`、`out/` | ✅ 干净（0 个 node_modules） |
| `logs/` | 0.4 MB | 0 | `logs/` | ✅ 干净 |
| `.idea/` | 10.7 KB | 0 | `.idea/` | ✅ 干净 |
| `frontend/` | 44.8 MB | 272 | — | 未见 `node_modules` 残留，正常业务代码 |

> **`models/` 的治理是正面样板**：5.7 GB 只跟踪了 4 个文件。说明团队对「可再生大文件不入库」
> 有意识且执行到位——`data/compendium_rag` 是**同类原则下的漏网之鱼**，属规则补齐前的历史债。

**风险等级：🔴 高**（不是「即将泄露」，而是「仓库已膨胀 + 4055 个文件失去版本控制」）

---

## 3. 依赖一致性

### 3.0 基线

- `requirements.txt`：7 个运行时 pin + `websockets>=12.0`（共 8 条实际依赖）
- `pyproject.toml [project.dependencies]`：7 条
- 两者**完全一致**（`requirements.txt` 头部注释记录了 2026-09-29 补齐 `fastapi` / `python-multipart` 的历史）
- 已安装：`.venv` 共 **79 个包**

### 3.1 清单 A：requirements.txt 声明了但**没安装**的关键包

**结果：0 个**。8 条声明全部能在 `.venv` 中找到。

### 3.2 清单 B：源码 import 了但 requirements.txt / pyproject.toml **都没声明**的包 🔴

扫描范围：`src\`（88 个 .py）+ `scripts\`（347 个 .py）的 top-level import，剔除标准库与本项目内模块。

#### B-1 影响 `src/`（**核心代码路径，最致命**）

| 包 | 引用位置 | 已装? | 声明? | 严重度 |
|---|---|---|---|---|
| `numpy` | `src/compendium_rag/retriever.py:21`（**模块顶层 import**）、`src/roleplay/core/knowledge/plot_semantic.py:28`（顶层）、`emotion/classifier.py:216`、`plot_rerank.py:86`、`plot_graph.py:1882/2276`（函数内） | ✅ 2.5.1 | ❌ 仅在 `pyproject` **可选** `emotion = ["numpy>=1.26"]` | 🔴 **高**：`compendium_rag/retriever.py` 与 `plot_semantic.py` 是**顶层硬依赖**，但 numpy 只挂在**可选 extras** `emotion` 里。`pip install -e .`（不带 extras）后**主模块直接 ImportError** |
| `onnxruntime` | `src/roleplay/core/knowledge/plot_rerank.py:87` | ✅ 1.28.0 | ❌ 完全未声明 | 🟠 中高（在函数内 import，走 ONNX 重排路径时才崩） |
| `tokenizers` | `src/roleplay/core/knowledge/plot_rerank.py:88` | ✅ 0.23.1 | ❌ 完全未声明 | 🟠 中高（同上，与 onnxruntime 配套；代码注释自称「本机只有 onnxruntime + tokenizers」，但依赖清单不承认） |
| `chromadb` | `src/roleplay/core/rag/chroma_store.py:19`（函数内） | ❌ **未安装** | ⚠️ 仅在 `pyproject` 可选 `rag = ["chromadb>=0.5"]`；`requirements.txt:24` 被**注释掉** | 🟡 中（函数内 import + 可选路径，但**两处清单口径不一致**：pyproject 有、requirements 注释掉） |
| `python-docx`（import 名 `docx`） | `src/roleplay/core/knowledge/document_ingest.py:145`（函数内，有友好报错） | ✅ 1.2.0 | ⚠️ 仅在可选 `docs` extras | 🟢 低（已做 try/except 并给出 `pip install python-docx` 提示，**处理得当**） |
| `pypdf` | `src/roleplay/core/knowledge/document_ingest.py`（.pdf 分支，同上有友好报错） | ✅ 6.15.0 | ⚠️ 仅在可选 `docs` extras | 🟢 低（同上） |
| `faster_whisper` | `src/roleplay/core/voice/stt.py` | ✅ 1.1.1 | ⚠️ 仅在可选 `voice` extras | 🟢 低（voice 为可选特性） |
| `edge_tts` | `src/roleplay/core/voice/tts.py` | ✅ 7.2.8 | ⚠️ 仅在可选 `voice` extras | 🟢 低 |
| `websockets` | `src/roleplay/channels/qq_onebot.py` | ✅ 17.1 | ✅ **已在 requirements.txt:21**（但 pyproject 无） | ✅ 无风险（requirements 有即可；pyproject 缺失属**单向不一致**，见下） |

#### B-2 仅影响 `scripts/`（分析/离线脚本，不阻塞主程序）

| 包 | 引用脚本 | 已装? | 声明? |
|---|---|---|---|
| `transformers` | `_ce_v2_score.py`、`_p4_ce_onnx_subset.py`、`_p4_ce_real_test.py` | ✅ 5.17.0 | ❌ 未声明（作为 `faster-whisper` 传递依赖混入，非显式） |
| `torch` | `_ce_v2_score.py`、`_p4_ce_real_test.py`、`_p4_ce_subset.py` | ✅ 2.14.0 | ❌ 未声明（同上，传递依赖） |
| `scipy` | `_rank_stats.py` | ❌ **未安装** | ❌ 未声明 → **该脚本当前跑不起来** |
| `zhconv` | `bilibili_lore_ingest.py`、`voice_pipeline/postprocess.py` | ❌ **未安装** | ❌ 未声明 → **这两个脚本当前跑不起来** |
| `imageio_ffmpeg` | `voice_pipeline/cut_voice_clips.py`、`probe_lang.py`、`transcribe_whole.py` | ❌ **未安装** | ❌ 未声明 → **语音切分链路跑不起来** |
| `playwright` | `huiji_fetch.py` | ✅ 1.62.0 | ❌ 未声明 |
| `huggingface_hub` | `download_cross_encoder.py` | ✅ 1.26.0 | ❌ 未声明 |
| `PIL`(pillow) | `analyze_render_png.py`、`analyze_stage_shot.py` | ✅ 12.3.0 | ❌ 未声明 |
| `python-docx`/`pypdf`/`numpy`/`onnxruntime`/`tokenizers` | 多个 `_*` 脚本 | ✅ | ⚠️ 仅可选 extras |

**B 小结**：源码实际 import 的第三方包中，**完全未出现在任何清单**的核心项 =
`onnxruntime`、`tokenizers`、`scipy`、`zhconv`、`imageio_ffmpeg`、`transformers`、`torch`、`playwright`、`huggingface_hub`、`pillow`（10 个）；
其中 **3 个（`scipy` / `zhconv` / `imageio_ffmpeg`）连 `.venv` 里都没装**，对应脚本必然 ImportError。
**`numpy` 挂在可选 extras 但被主路径顶层 import**，是最容易造成「新环境 clone 后 `import roleplay` 直接崩」的一颗雷。

### 3.3 清单 C：版本 pin 与实际安装**不符** ⚠️

`requirements.txt` 用 `==` 精确 pin，但 `.venv` 实际版本**严重漂移**：

| 包 | requirements.txt pin | 实际安装 | 状态 |
|---|---|---|---|
| `fastapi` | `==0.115.6` | **0.140.7** | 🔴 不符（差 25 个 minor） |
| `starlette` | `==0.40.0` | **1.3.1** | 🔴 不符（跨大版本 0.x → 1.x） |
| `pydantic` | `==2.10.3` | **2.13.4** | 🔴 不符 |
| `httpx` | `==0.28.1` | 0.28.1 | ✅ 一致 |
| `uvicorn` | `==0.51.0` | 0.51.0 | ✅ 一致 |
| `pydantic-settings` | `==2.14.2` | 2.14.2 | ✅ 一致 |
| `python-multipart` | `>=0.0.6` | 0.32 | ✅ 满足 |
| `websockets` | `>=12.0` | 17.1 | ✅ 满足 |

→ **3/8 精确 pin 与实际不符**，且 `starlette 1.3.1` 是**跨大版本**。
这意味着 `pip install -r requirements.txt` 会在当前 `.venv` 上**触发降级**，
或反过来——当前 `.venv` 并非由该文件构建。
**`requirements.txt` 的 pin 已失去描述现实的作用**（同理 `pyproject` 的 `dependencies` 也是同一批 pin，同样过期）。

### 3.4 `[tool.setuptools.packages.find] where=["src"]` 覆盖检查

`src/` 下的包目录（含 `__init__.py`）共 **12 个**：

```
src\compendium_rag\            ← 顶层包 ✅ 会被 find 命中
src\roleplay\                  ← 顶层包 ✅
src\roleplay\api\              ✅
src\roleplay\channels\         ✅
src\roleplay\core\             ✅
src\roleplay\core\emotion\     ✅
src\roleplay\core\knowledge\   ✅
src\roleplay\core\llm\         ✅
src\roleplay\core\rag\         ✅
src\roleplay\core\voice\       ✅
src\roleplay\errors\           ✅
src\roleplay\models\           ✅
```

**结论：✅ 无遗漏。** `where = ["src"]` 会自动发现 `src` 下**所有**含 `__init__.py` 的目录，
`src\compendium_rag` **已包含在内**（它是 `src/` 下两个顶层包之一，且有自己的 `__init__.py`）。

⚠️ 但有一个**隐性约定风险**：`find` 默认只收**含 `__init__.py`** 的目录。
`src/` 下若将来新增**命名空间包**（无 `__init__.py`）或纯数据目录，会被静默漏掉。
建议显式写成 `where = ["src"]` + `include = ["roleplay*", "compendium_rag*"]`，
让「要打包哪些顶层包」成为**显式声明**而非隐式发现——避免某天手滑删掉一个 `__init__.py` 就静默丢包。

---

## 4. 文档漂移

### 4.1 `docs/README.md` 索引完整性 ✅ 基本健康

- `docs/README.md` **存在**（121 行，是设计良好的分类索引，含五子系统判别指纹表）。
- 提取全部 **28 个相对链接**逐一 `Test-Path` 校验：**27 OK / 1 BROKEN**。
- 唯一 BROKEN 项：
  `voice-desktop/排查-桌面宠物唤不起来-Low完整性标签.md`
  → **实为误报**：该文件**确实存在**（`Get-ChildItem -Filter "*Low*.md"` 命中 1 个）。
  断裂是 PowerShell 读取 UTF-8 中文时的**编码解析问题**，不是真断链。
  （用 `-LiteralPath` 直查 `docs\voice-desktop\` 目录列表可确认该文件存在。）

→ **docs 索引真实断链数：0** ✅

### 4.2 根 `README.md` 提到的目录/文件存在性

用户点名的两项**均存在** ✅：

| README 引用 | 存在? |
|---|---|
| `docs/roleplay-core/architecture/ARCHITECTURE.md` | ✅ 存在 |
| `docs/voice-desktop/voice/VOICE_ITERATION_REPORT.md` | ✅ 存在 |

其余 12 个反引号路径引用中：
- **6 个 OK**（`docs/README.md`、`src/roleplay/main.py`、`src/roleplay/core/orchestrator.py`、`src/roleplay/channels/qq_onebot.py` 等）
- **6 个标 BROKEN，但全部为误报**：
  - `config.py` / `middleware.py` / `core/session_memory.py` → 是**表格内的上下文简写**，
    实际对应 `src/roleplay/config.py`、`src/roleplay/middleware.py`、`src/roleplay/core/session_memory.py`，
    **三个文件都存在**（已逐一 `Test-Path` 确认）。
  - `config.json` / `tokenizer.json` / `vocabulary.txt` → 出现在
    `README.md:82`「模型准备：从 hf-mirror.com 下载 base 模型…包含这四个文件」，
    指的是**要下载到本地模型目录的资产文件**，不是仓库内路径。**非断链**。

→ **根 README 目录/文件引用真实断链数：0** ✅

### 4.3 孤儿文档（docs/ 下未被 `docs/README.md` 索引提到）

`docs/` 递归共 **62 个 .md**。以「索引正文是否出现该文件**名**或**相对路径**」为判据：

| 子系统目录 | 该目录 .md 数 | 其中未被索引提及 |
|---|---|---|
| `plot-graph-rag/` | 22 | **21** |
| `compendium-rag/` | 17 | **15** |
| `voice-desktop/` | 12 | **10** |
| `roleplay-core/` | 8 | **7** |
| `qq/` | 2 | **1** |
| `docs/README.md`（自身） | 1 | 1（自指，正常） |
| **合计** | **62** | **55** |

**判定：这不是「孤儿文档」问题，是「索引粒度」问题——属可接受设计。** 理由：

1. `docs/README.md` **有意**只索引到「子系统 + 子目录 + `CHRONICLE.md`」三层，
   明确写了约定：「每个子系统目录含 `CHRONICLE.md`（历史编年史）+ 其余 .md（当前权威文档）」。
   按该约定，**目录内具体文档不逐个列举是符合设计意图的**。
2. 5 个子系统的 `CHRONICLE.md` **全部存在**（逐一验证 ✅），说明编年史机制落地了。
3. `docs/` 顶层只有 `README.md` 一个文件（无散落 md），说明 2026-09-28 的分类归档执行彻底——
   文档从 140 份精简到 65 份，且**平铺污染已根除**。

⚠️ **真正的结构性缺口**：**五个子系统目录下都没有自己的 `README.md` / `INDEX.md`**
（全部返回 `NONE`）。即「顶层索引 → 子目录」之间**断了一层**：
顶层只给了子目录名和一句内容描述，进入子目录后**没有导航**，
21 个 `plot-graph-rag` 文档要靠 `ls` 才知道读哪个。
→ 建议为 5 个子系统各补一份 `README.md`，把「先读/权威文档/编年史」说清楚
（顶层 README 对 `compendium-rag` 已给了「先读」三连，是好的样板，应推广到其余四个）。

### 4.4 其他文档一致性观察

- `docs/README.md:118` 提到 `data/compendium_rag/repairs_v*/**.md` 带 **SHA-16 冻结锁**（`.gitattributes` 按路径声明）
  → `.gitattributes` **存在**（1,159 B）✅。
  ⚠️ 这与第 2.4 节的「仓库瘦身需重写历史」**直接冲突**：重写会改变 SHA，冻结锁失效。
  **这是必须 owner 裁决的架构取舍**，不是可以顺手修的小事。
- `docs/README.md:102` 提到 `/docs/DESKTOP_PET_DESIGN.md` 是**固定 URL**，前端 `frontend/js/desktop-pet.js` 依赖。
  该路径在磁盘上已随分类迁移到 `docs/voice-desktop/pet-design/DESKTOP_PET_DESIGN.md`
  （索引说「仅磁盘路径随分类调整，URL 路径固定不动」）。
  ⚠️ **属高风险耦合点**：若 `main.py` 的静态挂载未同步改指向新磁盘路径，该端点会 404。
  建议单点验证一次该 HTTP 端点是否仍返回 200。

---

## 5. scripts 墓地统计

### 5.1 数量全景

| 指标 | 数量 |
|---|---|
| `scripts/` 文件总数（递归） | **400** |
| 其中 `.py` | **347** |
| 子目录 | 3 个：`_archive/`、`voice_pipeline/`、`__pycache__/` |
| `scripts/_archive/` | **26 个文件**（22 个 `.py`） |
| `scripts/voice_pipeline/` | 5 个文件（正式子模块，非垃圾） |
| `scripts/__pycache__/` | 40 个文件（运行产物，非脚本） |
| **`_` 前缀 `.py`（一次性分析脚本）** | **161** |
| `scripts/` 根下 `.py` | 329 个文件中的 **181 个非 `_` 前缀** |

### 5.2 分类判定

| 类别 | 数量 | 占比(按 347 .py) | 判定 |
|---|---|---|---|
| `_` 前缀一次性脚本 | **161** | **46.4%** | 🔴 脚本墓地主体 |
| 无 `_` 前缀（长期有用候选） | 181 | 52.2% | 混合含真正工具 + 未加前缀的一次性产物 |
| `_archive/`（已归档） | 22 | 6.3% | ✅ 归档机制存在且在工作 |

### 5.3 是否存在「脚本墓地」问题？→ **是，且已部分自我治理**

**证据**：
1. **`_` 前缀脚本占 46.4%**（161/347）——近一半是一次性分析/探针脚本。
   命名本身（`_decide_r4k01_gate.py`、`_p4_ce_subset.py`、`_rank_collect.py`、`_audit_lexonly_repro.py`）
   显示出强烈的「实验决策留痕」性质：为某次 A/B 或某个 gate 判定而写，结论落地后即失去复用价值。
2. **存在大量**按数字/阶段编号的脚本族（`_85_*`、`_p4_*`、`_p3_*`、`_r4k01_*`、`_ce_v2_*`），
   是典型「一次实验 = 一个脚本」的堆积模式。
3. **交叉引用成网**：扫描发现 `_r5_variant_scan`（23 次）、`_lex_channel_full`（18 次）、
   `diag_seedless_ceiling`（13 次）、`compendium_rag_eval300`（3 次）等**本地模块被多个脚本 import**——
   说明这些 `_` 脚本彼此耦合，删一个可能连带弄脏一片。**这是清理的最大阻力**。

**积极面**（说明团队有意识）：
- 已有 `scripts/_archive/`（22 个 `.py`），**归档通道存在**；
- 已有专门的治理脚本：`_docs_health.py`、`_docs_fix_refs.py`、`_docs_ref_analysis.py`、`_cleanup_docs_plan.py`——
  团队**已经做过一轮文档清理**（140 → 65 份），说明方法论在；
- `docs/README.md:43` 提到「合并前快照在 git 标签 `backup-pre-testdocs-cleanup`」，
  **用 git tag 而非删文件来保留历史**——这是正确做法，应复用到 scripts 清理。

### 5.4 归档建议（**仅建议，未执行任何改动**）

1. **先打 tag 再动**：`git tag backup-pre-scripts-cleanup`（沿用文档清理的成功模式），
   保证任何误删可 `git show <tag>:<路径>` 找回。
2. **分批而非一刀切**：优先归档满足以下全部条件的 `_` 脚本——
   ① 无 `_` 前缀脚本 import 它；② 不在 `docs/` 任何文档中被引用；③ 最后修改 > 60 天前；
   ④ 其实验结论已落入 `CHRONICLE.md` 或 baseline 报告。
   （本次扫描已给出交叉引用计数：`_r5_variant_scan` 23 次、`_lex_channel_full` 18 次、
   `diag_seedless_ceiling` 13 次 → **这三个绝对不能删**，是被依赖的公共模块。）
3. **给「长期有用」的一等公民待遇**：181 个无 `_` 前缀脚本中，真正的运维入口
   （如 `build_plot_index.py`、`compendium_canon_corpus.py`、`migrate_rag_kb.py`）
   应在 `README.md` 或 `docs/` 中被点名，否则新人无法区分「工具」和「僵尸」。
4. **建立 `scripts/README.md`**：用一张表声明「每个无前缀脚本的用途 + 是否仍维护」，
   与 docs 的五分类索引同构。这是**成本最低、收益最高**的一步。
5. **别追求一次清完**：46.4% 的一次性脚本是**研究型项目的正常沉淀**，
   强行清零会丢掉「当时为什么这么做」的依据（团队自己在 `docs/README.md:40-41` 已论证过这点）。
   目标是「**可导航**」，不是「**最小化**」。

---

## 6. 结论与优先级建议 Top-5

### 总览评分

| 维度 | 评级 | 一句话 |
|---|---|---|
| 临时垃圾 | 🟢 良 | 12 项全部已被 .gitignore 覆盖，仅 33 KB，无污染风险 |
| 密钥泄露 | 🟢 良（本机）/ 🟡 中（备份文件） | 真实 `.env` 未入库；2 个真值密钥仅存于本机；`.env.env.bak.*` 需确认后销毁 |
| git 跟踪风险 | 🔴 **差** | **4055 个文件已跟踪∧已忽略**，`.git` 1.36 GB |
| 依赖一致性 | 🟠 中下 | 0 个漏装声明包，但 **10 个未声明 import** + **3/8 版本 pin 失效** |
| 文档漂移 | 🟢 良 | 索引真实断链 **0**；缺的是子系统级导航层 |
| scripts 健康 | 🟠 中 | 46.4% 一次性脚本，但归档机制与治理方法论已在 |

### Top-5 优先级

**P0 — 4055 个「已跟踪 ∧ 已忽略」文件的矛盾状态**（`data/compendium_rag` 4036 + `data/eval_set_i` 19）
- 影响：`.git` 1.36 GB；这 4055 个文件的后续修改**被静默忽略**，等于既占空间又失去版本控制。
- 动作：**先裁决，再动手**。方法与 `.gitattributes` 的 SHA-16 冻结锁冲突——
  ① 保守方案：`git rm --cached -r data/compendium_rag data/eval_set_i`（仅停止跟踪，保留历史，`.git` 不缩小）；
  ② 激进方案：`git filter-repo` 重写历史（真正瘦身，但**所有 commit SHA 改变，冻结锁全部失效，需全团队协调**）。
- ⚠️ 需要 owner 决策，**不要由审计直接执行**。

**P1 — `numpy` 只挂在可选 extras 却被主路径顶层 import**
- 影响：`src/compendium_rag/retriever.py:21` 与 `src/roleplay/core/knowledge/plot_semantic.py:28`
  是**模块顶层** `import numpy`。`pip install -e .`（不带 `.[emotion]`）后，
  **当前主线的检索器直接 ImportError**——这是「新环境 clone 后跑不起来」的最典型形态。
- 动作：把 `numpy` 从 `[project.optional-dependencies].emotion` 提到 `[project].dependencies`，
  并同步写进 `requirements.txt`（该文件目前**完全没有 numpy**）。

**P2 — `requirements.txt` / `pyproject.toml` 的 pin 已失效（3/8 不符）**
- 影响：`fastapi==0.115.6` vs 实装 `0.140.7`；`starlette==0.40.0` vs 实装 **`1.3.1`（跨大版本）**；
  `pydantic==2.10.3` vs 实装 `2.13.4`。照文件安装会触发降级，文件或环境二者必有一错。
- 动作：二选一并写进文档——要么**按实装更新 pin**（推荐，`starlette 1.x` 说明已实际升级过），
  要么**重建 `.venv` 对齐 pin**。同时补上单向不一致的 `websockets`（requirements 有、pyproject 无）。

**P3 — 10 个未声明的第三方 import，其中 3 个连 `.venv` 都没装**
- 影响：`scipy`（`_rank_stats.py`）、`zhconv`（`bilibili_lore_ingest.py`、`voice_pipeline/postprocess.py`）、
  `imageio_ffmpeg`（语音切分三脚本）→ **这 6 个脚本当前必然 ImportError**；
  `onnxruntime` + `tokenizers`（`plot_rerank.py` 重排路径）、`transformers`、`torch`、`playwright`、
  `huggingface_hub`、`pillow` 属「碰巧装了但没声明」，换环境即崩。
- 动作：按「`src/` 用到的进主依赖、`scripts/` 用到的进新 `[project.optional-dependencies].analysis`」
  二分补声明；对确实不再用的脚本走 P4 归档，而不是补依赖。

**P4 — 五个子系统目录缺 `README.md` / `INDEX.md`，且 scripts 无导航**
- 影响：62 份文档里 55 份未被顶层索引点名；`plot-graph-rag/` 21 份、181 个无前缀脚本**无导航**，
  新人只能 `ls` 盲找。`docs/README.md` 对 `compendium-rag` 的「先读三连」是好样板，未推广。
- 动作：① 为 5 个子系统各补 `README.md`；② 建 `scripts/README.md` 声明用途与维护状态；
  ③ 顺手验证 `/docs/DESKTOP_PET_DESIGN.md` 端点是否仍 200（文档自述为固定 URL，磁盘路径已迁移）。

### 一句话总结

**最严重的两个问题**：① `data/compendium_rag` 等 **4055 个文件处于「已跟踪 ∧ 已忽略」的矛盾状态**，
撑大 `.git` 到 1.36 GB 且让这些文件实质上脱离版本控制（需 owner 在「瘦身」与「SHA-16 冻结锁」间裁决）；
② **`numpy` 被主路径顶层 import 却只声明在可选 extras**，配合 3/8 失效的版本 pin，
使得「按清单在新环境安装 → 主线检索器直接 ImportError」成为必然。
其余（临时垃圾、密钥、文档断链）**健康状况良好**，无需紧急处置。
