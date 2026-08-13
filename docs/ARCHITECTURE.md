# 架构设计文档（RoleplayAI）

> 由软件架构师视角撰写，记录关键设计决策与依据。

## 1. 设计原则

| 原则 | 落地方式 |
|---|---|
| 单一职责 (SRP) | 每层只做一件事：路由只管 HTTP，编排只管流程，provider 只管外部调用 |
| 开闭原则 (OCP) | 新增 LLM/RAG 实现 = 新增一个适配器类，不改业务层 |
| 依赖倒置 (DIP) | 业务层依赖 `LLMPort` / `VectorStore` 抽象，不依赖具体 SDK |
| 接口隔离 (ISP) | 端口接口方法最小化，避免胖接口 |
| 分层 (Clean Arch) | API → Core(Orchestrator) → Ports/Adapters，依赖指向圆心 |

## 2. 分层与职责

- **api/**：FastAPI 路由。接收请求 → 校验 DTO → 调用 `ChatOrchestrator` → 返回响应。不含业务逻辑。
- **core/orchestrator.py**：应用层用例「一次对话」。协调 情感检测、RAG 检索、角色卡解析、LLM 生成。
- **core/llm/**：`LLMPort`（抽象）+ `MockLLMProvider` / `OpenAILikeProvider`。
- **core/emotion/**：`EmotionDetector`（策略：关键词 / 可扩展 LLM）、`Live2DEmotionMapper`（情绪→表情名）。
- **core/rag/**：`VectorStore`（抽象）+ `InMemoryVectorStore`（测试用，零依赖）。
- **errors/**：统一异常体系 + FastAPI 处理器。
- **models/**：DTO 与角色卡领域模型，纯数据 + 纯函数。

## 3. 关键决策与依据

1. **配置用 `pydantic-settings` + `frozen=True` + `lru_cache`**
   - 依据：2026 主流实践。配置启动时解析一次、运行期不可变；`env_prefix` 解耦环境变量；测试用 `get_settings.cache_clear()` 重置。
2. **默认 `mock` provider**
   - 依据：让项目「开箱即跑、离线可测」，先有可替换端口再谈真实接入（依赖倒置的入口）。
3. **RAG 用接口 + 内存实现**
   - 依据：Chroma 等需要网络/安装；内存实现让单测不依赖外部服务，生产再切 `chroma`。
4. **情绪→表情用「名」不用「索引」**
   - 依据：上一轮核实发现两套 Live2D 模型表情数组顺序不同，写死索引换模型即错位；映射按表情名，运行时解析。
5. **emotion 枚举统一 7 类**
   - 依据：原两包前后端枚举错位（后端有 anxious、前端有 surprise/fear 但后端发不出），统一为 `happy/sad/angry/anxious/surprise/fear/neutral`。

## 4. 数据流（单次对话）

```
POST /chat
  → ChatRequest 校验
  → Orchestrator.run(message, character_card, system_prompt)
      1. CharacterCard.parse_raw_card → 解析人设
      2. EmotionDetector.detect(user_text) → EmotionInfo
      3. VectorStore.search(query) → 相关上下文 (top_k)
      4. 拼装 system_prompt + [context] + 人设
      5. LLMPort.generate(system, user) → reply
  → ChatResponse{reply, emotion, follow_ups}
  （SSE 变体另在 api 层包裹 event: chunk / emotion / done）
```

## 5. 扩展性路线

- 二期：TTS/ASR（新增 `core/voice/` 端口）、Lorebook（`character_book` 关键词触发注入）、会话记忆摘要入向量库。
- 多角色：Orchestrator 持有 `model_id`，前端 `Live2DEmotionMapper` 按模型取表情名。

## 6. 代码审查迭代记录（5 轮，基于 FastAPI 社区最佳实践）

审查维度：代码质量、安全性、性能、可维护性、边界与错误处理。

- **R1 功能性/性能/一致性**
  - 修复前端情绪芯片不显示且被流式文本覆盖（拆分文本 span 与芯片、pending 情绪补挂）。
  - `InMemoryVectorStore` 写入时预计算 TF 向量，避免每次查询重复分词。
  - `OpenAILikeProvider` 复用实例级 `httpx.AsyncClient`，新增 `max_tokens` 与 `aclose()` 生命周期管理。
  - 引入 `logging` 替换静默 `except`；默认系统提示词与角色卡字段标签中文化。
- **R2 安全/UX**
  - 新增 `SecurityHeadersMiddleware`（X-Content-Type-Options / X-Frame-Options / CSP 等）。
  - 新增内存滑动窗口限流依赖（按 IP，可配置，默认 60/min）。
  - 情绪分数封顶 1.0；前端渲染 `follow_ups` 追问按钮。
- **R3 架构/可测试性**
  - 编排器装配从「模块级 lru_cache 全局」改为「lifespan 构建 → `app.state.orchestrator` → `Depends` 注入」，依赖关系显式、生命周期透明。
- **R4 边界/健壮性**
  - `system_prompt`/`character_card` 加 `max_length` 上限（防 DoS）。
  - `message` 增加去空白校验，纯空白判为非法（422）。
  - 修复统一错误处理器对校验 `ctx` 中异常实例不可序列化（TypeError）的真实 bug。
- **R5 收尾**
  - 补充测试（内存检索相关性、限流触发、SSE 分数封顶、安全头、空白消息）。
  - 文档同步；全量测试通过。

> 已知限制（后续项）：真实 LLM 场景下 SSE 当前为「先完整生成再切片流式」，非逐 token 流式；接入真实 provider 时可扩展 `LLMPort.stream` 实现真流式。
