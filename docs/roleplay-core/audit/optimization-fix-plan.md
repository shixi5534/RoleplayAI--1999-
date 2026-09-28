# 代码优化修复方案（审计确认 · 已应用）

> 状态：**审计完成、方案定稿、已全部落盘**（审批策略恢复后由 Agent 自动应用，2026-08）。
> 后端 B1~B7 与前端 F1~F13 均已修改并验证：定向测试 92 passed、前端全部 `node --check` 通过。
> 每项均经读码核实（双路审计：后端 15 条 / 前端 15 条，剔除误报后保留如下）。

---

## 一、后端（src/roleplay/）

### B1 高 · 长期记忆写入即被清空（阈值标度错配）
- 文件：`core/knowledge/memory_tier.py`
- 位置：`prune()` 中 `imp < 0.6`（约 L158）
- 问题：结构化条目（`consolidate_entries`）的 importance 标度为 [0,1]（规则提取器 0.4/0.55、LLM 缺省 0.5、纠错下限 0.3），而整段合并（`consolidate`）标度为 [1,3]。阈值 0.6 会立即清掉全部结构化条目。
- 修复：新增常量 `_PRUNE_MIN_IMPORTANCE = 0.3`，`imp < _PRUNE_MIN_IMPORTANCE`；加注释说明双标度。

### B2 高 · /api/knowledge/upload 无大小上限
- 文件：`api/knowledge.py`，`upload_document`（约 L307）
- 问题：流式写入无上限，可耗尽磁盘。
- 修复：设 `MAX_UPLOAD_BYTES = 64 * 1024 * 1024`，读取循环内累计，超限返回 413 并清理临时文件。

### B3 高 · SSE 首个 emotion 事件延迟（use_web 时客户端长时间零数据）
- 文件：`core/orchestrator.py`
- 位置：`stream()` 调用 `_prepare()`（含联网抓取）后才 yield emotion。
- 修复：把 `_prepare` 拆为三块：
  1. `_detect_emotion(req)`：仅情感检测；
  2. `_gather_context(req, card_obj, character_id)`：联网 + 知识检索 + 画像并行；
  3. `_build_prompt(...)`：拼装。
  `stream()` 改为 `emotion_task = create_task(_detect_emotion)` 与 `ctx_task = create_task(_gather_context)` 并行启动 → `await emotion_task` 后**立即 yield emotion 事件** → `await ctx_task` → 拼 prompt → 继续。`run()` 保持原并行行为不变。

### B4 中 · SessionMemory 每轮两次同步写盘（事件循环阻塞 + 写放大）
- 文件：`core/session_memory.py` + `core/orchestrator.py`
- 位置：`append()` 每次落盘；`_persist()` 每轮调两次。
- 修复：`SessionMemory` 新增 `append_many(session_id, turns: list[(role, content)])`，单次加锁 + 单次 `_save`；`_persist` 改为一次 `append_many(sid, [("user", msg), ("assistant", reply)])`。

### B5 低 · SSE 响应缺 no-cache 头
- 文件：`api/chat.py`，`chat_stream` 返回处
- 修复：`StreamingResponse(..., headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})`。

### B6 中 · STT 转写原文进 INFO 日志（隐私）+ 异常原文透传
- 文件：`core/voice/stt.py`（L527/L533 等）+ `api/voice.py`（L78/L132）
- 修复：stt 仅记字符数（`logger.debug("STT 识别完成 %d 字符", len)`），幻觉过滤日志降 DEBUG；voice.py 500 响应返回通用文案，细节只进日志。

### B7 中 · web 命名空间无界增长
- 文件：`core/knowledge/ingest.py`，`ingest_web`
- 修复：`_WEB_NS_MAX_ITEMS = 2000`，入库后若超限，按 `ts` 淘汰最旧超出部分（`list_items` + `filter_remove`，to_thread 卸载）。

### 已核实为非缺陷（不修改）
- 请求级 llm override 无全局泄漏（factory 复用/隔离 + finally aclose）；session_id 白名单防路径穿越；SSE 中途异常有 error 事件兜底；各内存字典有容量守卫；TTS 假流式（整段缓冲）为缓存/重试所必需，暂不改。

---

## 二、前端（frontend/js/）

### F1 高 · 快捷键无修饰键守卫：Ctrl+C 会清空对话记忆
- 文件：`chat.js`，keydown（L730-796）
- 修复：在 Esc 处理与 `if (inInput) return;` 之后加 `if (mod) return;`（Ctrl/⌘ 组合已处理完，单键不再响应）；Alt 分支后加 `if (e.altKey) return;`。

### F2 高 · /chat/stream 无超时/中止，后端挂起界面永久卡死
- 文件：`chat.js`，`streamChat`（L473-584）
- 修复：`AbortController` + 空闲超时（60s 无数据重置计时）+ 总超时（120s）；`AbortError` 映射为「请求超时，请重试」走 `onFail`；`sendBtn.disabled = false` 移入 `finally`。

### F3 高 · voice.js 录音 onstop 闭包竞态（旧录音杀新录音）
- 文件：`voice.js`，`startRecording`/`onstop`/`uploadForSTT`（L110-256）
- 修复：按录音会话封装——`mediaRecorder.onstop` 闭包捕获本次的 stream/chunks/startTs；仅当模块级引用仍指向本会话才清空；`uploadForSTT(chunks)` 改为参数传入。

### F4 高 · localStorage 损坏容错不完整（model_offset 非对象中断首屏初始化）
- 文件：`chat.js`，`loadState`（L129-147）
- 修复：校验 `model_offset` 为对象且 x/y finite，否则回退 `{x:0,y:0}`；`model_id` 非字符串回退默认。

### F5 中 · knowledge.js 多文件上传静默丢弃
- 文件：`knowledge.js`，`handleFiles`/`uploadFile`（L290-349）
- 修复：`handleFiles` 改 `for...of` 串行 `await uploadFile(file)`（uploadFile 内部保留锁）；逐文件更新进度文案。

### F6 中 · llm-switch.js Ollama 模型列表污染云端面板
- 文件：`llm-switch.js`，`refreshOllamaModels`（L427-465）
- 修复：`await fetch` 之后、改写 `modelSel` 之前复查 `providerSel.value === "ollama"`，不符则丢弃结果。

### F7 中 · knowledge.js 异步乱序覆盖 UI
- 文件：`knowledge.js`，`loadDocuments`/`openChunksForDoc`/`doSearch`
- 修复：模块级单调递增 `requestSeq`，各请求发起时取号，渲染前校验仍是当前号。

### F8 中 · desktop-pet.js 端口探测串行 800ms×5 + 定时器泄漏 + 复查定时器重复
- 文件：`desktop-pet.js`，`probe`/`launch`（L33-75）
- 修复：`Promise.any` 并发探测（各自 800ms AbortController，`clearTimeout` 放 `finally`）；结果 TTL 缓存（如 5s），悬停读缓存、点击强制重探；复查定时器去重（记录 id，已存在不重复注册）。

### F9 低 · 弹层关闭 200ms 延迟隐藏与重开竞态
- 文件：`chat.js`（help/char）、`knowledge.js`（panel/chunks）
- 修复：记录 `closeTimer` id，`open()` 时 `clearTimeout`。

### F10 低 · chat.js switchModel 快速切换竞态
- 修复：切换代际号，await 后校验仍是最新才 toast/更新。

### F11 低 · chat.js 打字机错误路径不清理 + 每 tick 强制滚动
- 修复：`makeTyper` 暴露 `stop()`，`hideTyping`/`onError`/`onFail` 调用；scrollTop 写入节流。

### F12 低 · pet-inspect.js 方向键劫持输入框光标
- 文件：`pet-inspect.js`（L169-176）
- 修复：排除条件改 `e.target.matches("input, select, textarea")`。

### F13 低 · knowledge.js chunksSub 实体串显示
- 文件：`knowledge.js` L115
- 修复：`textContent` 直接用 `doc.doc_id`（textContent 天然防注入），去掉 `esc()`。

---

## 三、验证

- 后端：`.venv\Scripts\python -m pytest tests -q`（基线 376 passed / 1 skipped；含修复后全量 + 新增 2 条回归测试）
- 新增回归测试：`tests/test_knowledge.py` — `test_longterm_memory_prune_threshold_aligned`（B1）、`test_session_memory_append_many`（B4）
- 前端：`node --check frontend/js/*.js`（chat/voice/llm-switch/knowledge/desktop-pet/pet-inspect/pet/live2d/spine 全过）
- 桌面壳：`cd desktop && npm run check`（上一轮已过，本轮未触及）
