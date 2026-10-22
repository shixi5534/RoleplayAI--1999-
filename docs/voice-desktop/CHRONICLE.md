# 语音与桌面宠物 · 历史编年史

> 本文件由 **79 份历史过程档**合并而来（2026-09-29 首轮），2026-10-21 增补 8 份语音/桌宠过程档（合并为 5 条）。
> 收录原则：已完成的一次性报告（审计 / 实验 / 验收 / 阶段总结）。
> **当前权威文档仍以独立文件形式保留**，见 `docs/README.md` 索引。
>
> 原文未丢失：删除前快照在 git 标签 `backup-pre-testdocs-cleanup`，
> 且每条下方记录了来源路径与 SHA-16，可用 `git show <tag>:<path>` 找回。

---

## 2026-10-10 · 桌面宠物唤不起来 —— Low 完整性标签排障（已完成）

- 来源：`docs/voice-desktop/排查-桌面宠物唤不起来-Low完整性标签.md`
- SHA-16：`085501fca2cf4f43`

**要点**

- 症状三条同时出现即可确诊：① 报错码统一为 `5`（拒绝访问，含 `Lock file ... Error code: 5`）；② 把 `electron.exe` 复制到工作区外就正常；③ 连 `electron.exe --version` 这种不加载业务代码的路径也崩（`-2147483645`）。
- 根因：**仓库整棵树被打了 Low 完整性标签**（`icacls <path> | findstr "Mandatory"` 出现 `Low Mandatory Level`）。进程继承 LOW（令牌 IL 子授权 `0x1000`）后两件事同时失败：① Chromium 沙箱初始化要创建命名管道（Mojo）→ 拒绝访问 → 自毁；② `AppData` profile 是 Medium，写不了 → 连单实例锁都建不了。
- 唯一变量对照（闭锁因果）：只改 exe 的标签，`Low` → 派生进程 LOW，`Medium` → 派生进程 MEDIUM。版本矩阵 `31.7.7 / 33.4.11 / 43.4.0 / 43.7.5 / 44.4.5` **全部**一致（工作区内崩、工作区外正常）→ 与 Electron 版本无关。
- 修复：`icacls <repo> /setintegritylevel Medium /T /C /Q`（实测清除 165,245 个文件）。修复后无需任何启动开关：`--version` 返回 v43.4.0、真实 profile 启动存活、`POST /api/desktop-pet/launch` 1 秒内就绪、`GET /state` 返回 `{"ok":true,"state":"running"}`。
- 修复是持久的（父目录已是 Medium，子项继承），但**复发条件未知**；若别处 agent 会话再次触发降权写入仍可能复发，复发时用上面的 `icacls` 自查命令即可。
- 走过的弯路（教训）：曾误判为「Windows 11 25H2 build 26200 的 Electron 沙箱 bug」并加 `--no-sandbox` 垫片（改了 `desktop/package.json`、`desktop/src/main/index.js`、`src/roleplay/api/desktop_pet.py`），**已全部还原**；也曾误判为「只是 agent 沙箱产物、用户机器没问题」——用户真实点击留下同样报错，说明仓库文件标签本身被污染了。`--no-sandbox` 只是绕过沙箱路径，治标；真正的修复是恢复文件完整性标签。
- 确证边界：标签首次施加的时间点**无法回溯**（排查时的全量重写已覆盖原始标签），"某次会话开始失效"只是时间线推断；已实测确证的只有标签→进程完整性的因果链与清除后全链路恢复。


## 2026-09-09 · 桌面宠物 v0.3 · 工程实施方案与视觉资源实施清单（已完成，已落地）

- 来源：`docs/voice-desktop/pet-design/plan-spec-v0.3.md`
- SHA-16：`1df5ecc1e0f5bdf3`
- 来源（2）：`docs/voice-desktop/pet-design/plan-visual-v0.3.md`
- SHA-16：`94923961778120d0`

**要点**

- 依据 = 呈现层规范 v0.3 + 视觉风格板 v0.3（见下一条编年史）；性质为「只做计划、不改代码」。P0/P1/P2 三期：P0 = Spine 接通 + 7 组件 + 九态状态机；P1 = 强化；P2 = 打磨。
- **默认形态切换是「先建后切」**：原 `pet.html` 只加载 Live2D 运行时、`pet.js` 默认走 `RoleplayLive2D`。P0 先落位 Spine 素材 + 新增 `spine.js`（SpinePet 适配器），再加「渲染器路由」把默认切到 Spine，Live2D 降级为设置里的「对话模式」；切换即销毁旧渲染器，**避免双 WebGL 上下文并存**。
- **动画名推断被实测推翻（重要更正）**：风格板 §8.5 的表情映射用的是完整版（初始皮肤）命名 `bm_hy* / cm_hy* / zm*`；宠物默认渲染的是 512² 简化版，方案初稿据此推测简化版动画名为 `idle / st~st7 / j1~j4 / bian~bian4 / mao / hua / xc1~xc4 / cx2~cx6 / cs2 / djc1~djc2 / wei / target~target3 / born / jump / x_ls_*`。**2026-09-05 经 spine 运行时实测三个模型，这些候选在任一模型中都不存在，已清除**；真实动画清单为 `click / hit / idle / idle_birthday_loop / idle_birthday_up / idle_room / interact / sleep / walk`（其中 314701_s 仅含 `idle`）。结论落在 `frontend/assets/spine/animation_map.json`（`_meta.status = "verified"`），运行时仍按当前 `.skel` 过滤后取候选。→ 教训：骨骼动画名必须实测回填，文档里的候选表一律不可当契约。
- token 冲突的本质：`pet.html` 与 `index.html` 是两个独立 HTML 文档、各自内联 `<style>`，**不存在级联覆盖冲突**；「同名冲突」是语义漂移（同名不同值），集中在 `--fg-dim / --line / --line-strong / --font-mono` 四处。
- 图标：风格板 §9 表 17 行，「静音/取消静音」「上一句/下一句」各为同一槽位双态 → 去重后**正好 16 个图标槽位**。外部 `<img src="icons/*.svg">` 会丢失 `currentColor` 继承（外部 SVG 是独立文档），**必须 inline SVG 或 sprite `<use>`**，`assets/icons/*.svg` 仅作源文件存档与审计；CSP 允许 inline SVG。
- CSS 组织落地为 `frontend/css/pet.css`（外链；CSP 的 `style-src 'self' 'unsafe-inline'` 同时放行外链与内联）。`tokens.css` 拆分方案**未采用**。
- 落地核对（2026-10-21 复核）：`frontend/js/spine.js`、`frontend/css/pet.css`（28,985 B）、`frontend/assets/spine/animation_map.json` 均存在；风格板核心 token 已在 `pet.css` 内（`--fg-dim / --accent-glow / --fs-chip / --space-1 / --radius-bubble / --shadow-s4 / --dur-xslow / --ease-standard / --warn / --accent-bright` 全部命中）→ **`pet.css` 是视觉值的现行真源**，本文档的设计 token 表已不是权威。


## 2026-08-14 · 桌面宠物 v0.3 呈现层设计（规范 + 视觉风格板 + 交付索引）

- 来源：`docs/voice-desktop/pet-design/pet-presentation-spec-v0.3.md`
- SHA-16：`1fa29e1c5c081828`
- 来源（2）：`docs/voice-desktop/pet-design/pet-visual-styleboard-v0.3.md`
- SHA-16：`498723ed69b6dd4f`
- 来源（3）：`docs/voice-desktop/pet-design/pet-v0.3-INDEX.md`
- SHA-16：`134b8c5478f88923`

**要点**

- 团队 pet-redesign-v03（主理人 游承峰 / 规范 文策渊 / 视觉 林绘澄）；范围 = 呈现层重设计（Spine 人偶形态 + 古风暗黑 + 标准化设计文档），**纯设计交付、不动代码**。
- 一句话总结：从「半截 Live2D 大模型 + 3 个灰点」改为「**小尺寸 Spine 人偶 + 一眼识别的品牌条 + 可读状态 chip + 打字输入条 + 5 步新手引导**」，默认窗口压到 **320×420**，延续「暴雨之前」古风暗黑视觉语言，全程保留隐私约定。
- 视觉三支柱：① 古典克制（常驻元素视觉重量低到「余光可忽略」——细字/细线/低饱和/半透明，只在被召唤时浮现）；② 暗夜金铜（`#c9a86a` 是全应用**唯一**高饱和装饰色，只用于强调文字/图标描边/焦点反馈/品牌字，不做大面积填充）；③ 人偶私语（v0.3 起默认形态从 Live2D 大模型切为 Spine 小模型，气质从「舞台上的角色」变为「桌上的小偶人」）。
- 七条已定决策：① 渲染选型首选 `pixi-spine`（@esotericsoftware/spine-pixi 4.2，复用已有 PIXI 栈共享 GL 上下文），`spine-player.js` 为降级 fallback（混排能力降级为整段切换）；② 默认窗口 320×420，三档断点 S/M/L（<380 / 380~460 / >460）；③ 人偶定位 = 水平居中、垂直居中偏下，头顶留白 = 窗口高 **8%**（硬约束，给气泡留位），脚底落地线 = 下沿 −16px，缩放 = min(舞台可用高/骨骼自然高) × **0.92**；④ 状态机九态（闲置/漫步/拖拽/聆听/思考/说话/勿扰/锁位/睡眠），勿扰与锁位为**正交修饰态**、与主状态叠加（避免状态爆炸）；⑤ 勿扰 = 透明度 0.55 + 禁声 + 漫步暂停 + chip 呼吸，锁位 = 拖拽失效 + 虚线框 + 锁位 chip + 长按 1.5s 解锁；⑥ 图标 emoji 全退役 → SVG 描边 1.5px 金铜、16 个必备图标（Lucide 同语义）；⑦ 输入条展开抢焦点 + 8s 自动收起（已接受此取舍）。
- 主理人 Rev1 交叉一致性裁定（**以视觉风格板为权威值**，呈现规范同步修订）：状态 chip 高 18px→**20px**；右键菜单 min-width 176px→**172px**；引导配图槽位 96×96→**200×140px**；勿扰透明度 0.45→**0.55**；锁位指示从「品牌条旁 12px 小锁」→**状态区追加锁位 chip（12×12 锁形 + 「已锁位」文字）**。
- 设计 token 体系（两文档靠 CSS 变量对齐，视觉值禁止硬编码）：色彩 `--fg/--fg-dim/--fg-faint/--accent(-dim/-glow/-bright)/--ok/--danger/--warn/--bg-panel(+hover/active)/--line(+strong/faint)`；字体 `--font-serif/--font-mono` + 7 级字号 `--fs-chip(10px) → --fs-heading(18px)` + 3 档行高；间距 4px 栅格 `--space-1(4px) → --space-6(32px)`；圆角 `--radius-chip(999px)/-card(8px)/-bubble(10px)/-drawer(12px)`；阴影 `--shadow-s1 ~ --shadow-s4`；动效 `--dur-fast(120ms) → --dur-xslow(600ms)` + `--ease-standard/enter/exit`。
- 待用户拍板的 5 个开放问题（Q1 输入条抢焦点维持「抢焦点+8s 自动收起」；Q2 唤醒词不入 v1.1、本版只做快捷键提示；Q3 副屏断开自动回主屏原位；Q4 截图分享仅「人偶+气泡」、不含桌面背景；Q5 动画语义表为命名推测，P0 首日用巡检页实播校验后回填 —— **Q5 已被 2026-09-05 实测取代，见上一条**）。
- 新增视觉元素审批项：`--warn`（#d9a24a 琥珀，仅状态色，如 Ollama 未启动）、`--accent-bright`（#d4b57e，仅发送按钮 hover 提亮，全文唯一实色新增）。
- 风险与缓解：pixi-spine 与 skel 版本不兼容 → fallback `spine-player.js`；bloom 层在 Electron 透明窗混合异常 → 「模型辉光」开关兜底；动画语义推测偏差 → 巡检页 + 允许小修订；输入条抢焦点影响穿透 → 8s 自动收起 + Esc。


## 2026-08-13 · 情绪检测升级 7→15 类（LLM/分类器三级降级链）增量架构设计（已实现）

- 来源：`docs/voice-desktop/voice/emotion_upgrade_design.md`
- SHA-16：`340fccf7f30f789a`

**要点**

- 在既有「Clean Architecture + EmotionPort 策略模式」上做**接口异步化 + 三级检测链 + 15 类全链路穿透**。核心约束：「情感检测绝不拖垮主回复」——每级失败只 `logger.warning` 并继续下沉，关键词层永不抛异常。
- ADR-1 接口改 `async`：`EmotionPort.detect` 同步→异步（`Keyword`/`Local`/`LLM` 三实现全 async，`build_emotion_detector(*, enabled=True, settings=None)` 保持向后兼容）。理由：LLM/嵌入天然 IO 异步，同步桥接 async 有两个坑——FastAPI 事件循环内 `asyncio.run()` 抛「loop already running」，线程池桥接则每请求多一次线程切换且无法取消。波及面已核实仅 4 处（`orchestrator.py:149`、`tests/conftest.py`、`test_emotion.py`、`test_orchestrator.py`）。CPU 密集的分类推理内部走 `asyncio.to_thread`。
- ADR-2 LLM 提示词 = **单行 JSON** `{"emotion": "<15类之一>", "score": 0.0-1.0, "reason": "<一句话，可选>"}`（不要求纯标签，JSON 自带 reason 为 P2 可解释性预留，本期不展示不存储）；解析三级：`json.loads` → 正则抽 `"emotion"\s*:\s*"([^"]+)"` → neutral 兜底（记 `parse_fail`）；温度固定 `0.0`、`max_tokens=64`；**复用全局 `LLMPort`**（`build_llm(settings)` 单例，含连接池/重试/脱敏），不新建 HTTP 客户端。
- ADR-3 本地分类器两段式：P1 必做 = 零依赖「字符/词哈希特征（复用 `HashingEmbedder` 思路，`hashlib.md5` + 768 维）+ 逻辑回归分类头」，权重为内置常量表（15 类×768 维稀疏系数 + bias，KB 级随代码分发），P95 < 10ms；P1.5 可选 = `sentence-transformers` + `jina-embeddings-v2-base-zh`，**延迟加载 + import 失败自动禁用降级**，绝不抛异常（本次不做实现，仅留接口位）。
- ADR-4 三级降级链 = `FallbackChainDetector` 责任链，注入有序 `[LLM, LocalClassifier, Keyword]`；每级 `if r.emotion != "neutral" or r.score > 0: return r`；`EmotionInfo` 增 `source: Literal["llm","classifier","keyword","none"]="none"`（仅进日志，**SSE 事件体仍只发 `{emotion, score}`，协议不变**）。语义：上层只在中性/低置信时下沉——LLM 说 neutral 不算失败，仍让下级试。
- ADR-5 配置（全部带默认值，旧 `.env` 无需改动）：`emotion_detector: Literal["keyword","classifier","llm","auto"]="auto"`（auto = LLM 可用[非 mock 且 api_key 非空]时 LLM→classifier→keyword；LLM 不可用且分类器可用时 classifier→keyword；否则 keyword）、`emotion_llm_timeout=8.0`、`emotion_confidence_threshold=0.4`、`emotion_classifier_backend="hashing"`、`emotion_jina_model="jina-embeddings-v2-base-zh"`。`frozen=True` 兼容；**本期不做云端配置 UI 入口**（仅 .env/环境变量），前端 HUD 灵敏度 `emotion_threshold` 覆盖运行期阈值调节。
- ADR-6 15 类枚举 + 父类表（8 个新增类的三级兜底）：`love/grateful/excited → happy`；`disappointed/lonely → sad`；`embarrassed/confused → anxious`；`sleepy → neutral`。`EmotionLabel` 15 类 = `happy, sad, angry, anxious, surprise, fear, neutral, love, grateful, excited, disappointed, lonely, embarrassed, confused, sleepy`。
- ADR-7 未知标签归一化 `normalize_emotion_label()`：小写 → strip → 去空格/下划线/连字符 → 别名表（`joy→happy`、`terrified→fear`、`tired→sleepy` 等）→ 合法集合校验 → 非法回 `neutral`。`Live2DEmotionMapper.resolve()` 回退：`emotions[emotion]` → `emotions[EMOTION_PARENT[emotion]]` → `default`；前端 `live2d.js` 同构实现（后端已归一化时永不触发，双保险）。
- 落地核对（2026-10-21）：`src/roleplay/core/emotion/detector.py` 已含 `LLMEmotionDetector` / `LocalClassifierDetector` / `FallbackChainDetector`，`models/chat.py` 已含 15 类 `EmotionLabel` 与 `EMOTION_PARENT` → **ADR 全部已实现，本文档为历史设计档**。
- 其他配套：`orchestrator._prepare` 内 `emotion_task = asyncio.create_task(...)` 与知识检索并行（`asyncio.gather`），emotion 事件先于 chunk 的时序由 `stream()` 首事件保证；`pyproject.toml` 增可选依赖组 `emotion = ["numpy>=1.26"]`；`frontend/assets/live2d/emotion_map.json` 补 8 类映射；`frontend/js/chat.js` 的 `EMOTION_CN` 补 8 类中文名并保持 `|| emotion` 兜底。


## 2026-08-13 · 语音后端 STT/TTS 自我迭代（3 轮迭代 + 5 轮修复，共 8 轮）（已完成）

- 来源：`docs/voice-desktop/voice/VOICE_ITERATION_REPORT.md`
- SHA-16：`403ba8394483abb1`

**要点**

- 目标：STT（faster-whisper）+ TTS（edge-tts）全链路识别准确率与稳定性。结果：平均相似度 90.5%（单句）→ 抖动至 69.0%（热词污染）→ **88.8% 稳定**；末尾静音段幻觉 **4 条 → 0 条**；STT 耗时 5s → **1-2s**；TTS 缓存命中 **0.0001s**。
- **最终 STT 参数（第 6 轮定稿，现行值）**：`language="zh"`、`beam_size=5`、`best_of=3`、`patience=1`、`repetition_penalty=1.1`、`no_repeat_ngram_size=2`、`temperature=0.0`、`condition_on_previous_text=False`、`word_timestamps=True`、`no_speech_threshold=0.6`、`compression_ratio_threshold=2.4`、`log_prob_threshold=-1.0`、`hallucination_silence_threshold=2.0`、`suppress_blank=True`、`suppress_tokens=[-1]`、`max_initial_timestamp=1.0`、`hotwords=移除`、`initial_prompt=短词表软引导`、`vad_filter=True` + `vad.threshold=0.5` / `speech_pad_ms=200` / `min_silence_duration_ms=500`、`cpu_threads` 与 `OMP_NUM_THREADS` = 物理核心数、`CT2_CUDA_ALLOCATOR=cub_caching`，外加**后处理幻觉过滤层**。
- 三层抗幻觉防御（业界三层防御的第 2+3 层落地）：推理参数抑制（第 3/4 轮）→ 移除 hotwords 改短词表软引导（第 5 轮）→ 后处理模式匹配过滤层（第 6 轮）→ 误伤防护与强幻觉分级（第 7 轮）。
- **关键教训**：`hotwords` 会污染输出（把热词注入到静音段尾部），比不用更差 → 改用 `initial_prompt` 软引导。第 4 轮「只加反幻觉参数」反而把相似度打到 69.0%，说明单靠解码参数治不了尾部幻觉。
- TTS 侧（第 1-3 轮）：`rate` 限制在 edge-tts 支持的 `[-50, +100]`；30s 超时 + 指数退避重试 3 次（1.5×attempt）；空输出校验 > 1000 bytes；压缩空白文本预处理；**LRU 音频缓存 100 条（md5 key）**。
- **第 8 轮「声音合成失败」修掉 3 个真 bug**：① `pitch` 负值生成非法参数——`f"+{int(pitch or 0)}Hz"` 对负数产生 `"+-10Hz"`，edge-tts 直接拒绝（`Invalid pitch '+-10Hz'`），任何负音调角色必失败 → `_format_signed()` 带符号格式化 + clamp 到 `[-50,+50]`；② 重试复用 `Communicate` 对象——它在 try 块外创建且 `stream()` 只能调用一次，重试时第 2 次必失败（`stream can only be called once`），**重试逻辑形同虚设** → 每次尝试新建（`_stream_once`）；③ 确定性错误空跑重试（`Invalid voice/pitch` 重试 3 次结果相同，白耗 30s+）→ `ValueError` 单独捕获立即抛出。防护增强：voice 白名单预校验（0.2s 内拒非法音色，原需等 3 次重试）、超长文本按句末标点（。！？；）预切分（>500 字）、参数集中到 `_build_tts_params()` 纯函数可单测。实测 6 场景全通过（含 pitch=-100 clamp、3200 字分段）。
- 遗留问题（至今未解）：① 短句声学误识别（base 模型 142MB 特征提取不足，非幻觉，如「静音段」→「进阴段」61.5%、「语音识别」→「诡音识别」）；② 英文幻觉黑名单只覆盖 Vexa 高频短语，完整 135 条待补；③ PDF/DOCX 知识库导入需可选依赖 `pypdf` / `python-docx`。
- 后续建议：base→small(461MB)/medium(1.5GB) 可提 10-15% 声学精度；扩幻觉黑名单；前端加噪声门 + 音量归一化；`device="cuda"` + `compute_type="float16"` 可把 STT 压到 0.5s 内；对识别结果做规则/LLM 二次纠错。
- 交付：`src/roleplay/core/voice/stt.py`（518 行）、`tts.py`（280 行）、`api/voice.py`（113 行）、`tests/test_voice.py`（26 用例，第 8 轮新增 16 个）；全量回归 **120 passed**。


## 2026-08-14 · 桌面宠物 v0.3 呈现层重设计 · 实施总计划

- 来源：`docs/voice-desktop/pet-design/IMPLEMENTATION-PLAN-v0.3.md`
- SHA-16：`e771bc530c20145e`

**要点**

- 缩放 = min(舞台可用高 / 骨骼自然高) × 0.92。
- 5. 勿扰：透明度 0.55（INDEX §5 裁定值）、禁声、漫步暂停、chip 呼吸；锁位：拖拽失效、长按 1.5s 解锁。
- [ ] 勿扰 0.55 透明/禁声/漫步暂停/chip；锁位拖拽失效 + 长按 1.5s 解锁
- [ ] OCR 摘要气泡 +「详细」折叠；三档节流生效


## 2026-07-27 · 点击触发语音播放 —— 现状分析 · 根因复现 · 增量设计

- 来源：`docs/voice-desktop/voice/语音点击交互设计-架构师草稿.md`
- SHA-16：`ddbb430bb3fced95`

**要点**

- t=15.13s  play zh_41（dur=1.84s，click 槽最短的一条）
- t=17.34s  ended → lastPlayedAt['click'] = 17.34 → 冷却至 42.34s
- t=18.15s ~ 42.31s   9 次点击连续静默，跨度 24.2 秒
- t=45.33s  恢复发声（17.34 + 25 = 42.34 ✅ 精确吻合）

