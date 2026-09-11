# RoleplayAI · 角色扮演 AI 整合项目

将「角色脑」（RAG 检索 + 情感编排 + Character Card V2 人设）与「Live2D 表现层对接」
用 **Clean Architecture** 从零重建，目标是：分层清晰、可离线测试、可替换 LLM/RAG 实现、易扩展。

> 本项目为新建独立工程，**不修改**原始两包（`2026-07-26-22-28-10` 素材库 / `Desktop/rag` 应用），
> 仅沿用其分析与命名结论。

## 架构概览（代码架构表 v2.1）

| 层次 | 模块 | 核心职责 |
|---|---|---|
| 入口 / 装配 | `src/roleplay/main.py` + `config.py` + `middleware.py` | FastAPI 生命周期（含 QQ 渠道任务启停）、配置、安全中间件、静态托管 |
| API 层 | `src/roleplay/api/*.py` | HTTP 边界 / DTO / 限流：`chat`、`characters`、`knowledge`、`llm_config`、`voice`、`sessions`、`desktop_pet` |
| 渠道层 | `src/roleplay/channels/qq_onebot.py` | QQ 渠道（OneBot v11 / NapCat）：文字对话 + 情绪触发角色原声语音回复，零业务逻辑 |
| 应用层 | `src/roleplay/core/orchestrator.py` | `ChatOrchestrator`：情感 → RAG → 角色卡 → LLM → 复读 / 出戏守卫 → 记忆 / 摘要 |
| 端口 / 适配 | `core/llm/` · `core/emotion/` · `core/rag/` · `core/voice/` | LLM / 情感 / RAG / 语音抽象与可替换实现（Mock / OpenAI / Chroma / STT / TTS / 原声切片） |
| 知识 / 记忆 | `core/knowledge/` · `core/session_memory.py` | 向量库 + BM25、长期记忆、事件 / 画像提取、会话摘要落盘 |
| 前端 | `frontend/` | 聊天 / Live2D / 语音 / 模型切换 / 知识库面板 / 宠物页（Spine 渲染 + 原声台词 + 双语字幕） |
| 桌面端 | `desktop/` | Electron 薄壳：窗口管理、后端拉起、OCR、拖拽物理、自主漫步、控制服务 |
| 测试 | `tests/` | 单元 / 集成 / QA 回归，镜像 `src/roleplay` |

- **依赖倒置**：业务层只依赖 `LLMPort` / `VectorStore` / `EmotionPort` 等抽象接口，不依赖具体 provider。
- **渠道隔离**：`channels/` 只做协议收发，人设 / RAG / 情感 / 记忆全部复用 `ChatOrchestrator`，Web / QQ 双入口共用同一个大脑。
- **可替换**：`mock`（测试）/ `openai` / `deepseek` / `ollama` 通过配置切换，无需改业务代码。
- **可测试**：所有外部依赖都是接口，单测用内存/ Mock 实现即可。
- 完整架构图与逐文件架构表见 [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)。

## 快速开始

```bash
cd roleplay-ai

# 1. 创建虚拟环境并安装依赖（uvicorn 用于运行 Web 服务）
python -m venv .venv
source .venv/bin/activate                 # Windows: .venv\Scripts\activate
pip install -e ".[dev]"                   # 或: pip install fastapi uvicorn pydantic-settings httpx

# 2. 配置（默认 mock provider，无需任何 API Key 即可运行）
cp .env.example .env

# 3. 跑核心单测（离线、零外部依赖）
pytest

# 4. 启动 Web 服务（前端由后端同源托管，无需额外静态服务器）
uvicorn roleplay.main:app --host 127.0.0.1 --port 8000
```

启动后访问 **http://127.0.0.1:8000/** 即聊天页：

- 左侧为 Live2D 数字人「无名者」，资源已就位于 `frontend/assets/lib/`（pixi / cubismcore / live2d-display）
  与 `frontend/assets/live2d/wmz/314701/`（模型）。
- 右侧聊天框输入消息，后端以 SSE 流式返回；`emotion` 事件驱动数字人切换表情/动作，`chunk` 事件流式渲染文本。
- 试试输入「我有点难过」「我好生气」观察表情联动。
- 默认 `mock` 模式：LLM/情感/RAG 均为可替换的本地实现，无需联网或 Key。
  接真实模型：编辑 `.env` 设 `ROLEPLAY_LLM_PROVIDER=deepseek` 并填入 Key 即可，业务代码零改动。

## 语音功能（可选）

前端聊天页自带「🎙️ 录音输入」与「🔊 语音设置」按钮。默认优先使用浏览器原生 Web Speech API（无需任何配置）；若要使用本地 STT/TTS 后端，按以下步骤开启：

### 1. 开启 TTS（文字→语音，edge-tts 微软免费服务）

```bash
# .env 中开启
ROLEPLAY_TTS_BACKEND_ENABLED=true
ROLEPLAY_EDGE_TTS_DEFAULT_VOICE=zh-CN-XiaoxiaoNeural   # 可换其他音色
```

- 音色：`zh-CN-XiaoxiaoNeural`（晓晓）/ `zh-CN-YunxiNeural`（云希）/ `zh-CN-YunjianNeural`（云健）等，完整列表见 [edge-tts 官方语音清单](https://github.com/rany2/edge-tts)（`edge-tts --list-voices`）。
- 依赖：`pip install roleplay-ai[voice]`（或 `pip install edge-tts`）。

### 2. 开启 STT（语音→文字，faster-whisper 本地推理）

```bash
# .env 中开启
ROLEPLAY_STT_BACKEND_ENABLED=true
ROLEPLAY_WHISPER_MODEL=base          # tiny/base/small/medium/large-v3
ROLEPLAY_WHISPER_MODEL_PATH=C:/Users/<你>/fw_model   # 推荐：本地模型目录
```

- **模型准备**（推荐方式）：国内网络下 HuggingFace 直连易超时，建议从 `hf-mirror.com` 下载 base 模型（约 140MB）到本地目录，包含 `config.json` / `model.bin` / `tokenizer.json` / `vocabulary.txt` 四个文件。
- 若 `ROLEPLAY_WHISPER_MODEL_PATH` 留空，faster-whisper 会在首次调用时自动下载（需能访问 HuggingFace）。
- 依赖：`pip install faster-whisper`。
- CPU 即可推理（base 模型 + int8 量化，单句识别约 1-2s）；模型越大越准但越慢。

### 3. 语音 API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/voice/stt` | POST | 上传音频（webm/wav/mp3）→ 返回识别文本 JSON |
| `/voice/tts` | POST | 提交文本 + 可选参数（voice_id/speed/pitch/volume）→ 返回 MP3 流 |

前端语音按钮通过 `/voice/*` 与后端交互；后端未开启时自动降级到浏览器原生语音能力（部分浏览器不支持中文识别）。

### 4. 已知优化（6 轮迭代）

- STT 全链路平均相似度约 **88.8%**（6 句测试），含 VAD 预过滤、推理参数抑制、后处理幻觉过滤三层防御。
- 语音合成带 LRU 音频缓存（100 条），重复文本命中缓存仅 **0.0001s**。
- 详细迭代过程见 `VOICE_ITERATION_REPORT.md`。

## 目录结构

```
roleplay-ai/
├── pyproject.toml
├── .env.example
├── docs/ARCHITECTURE.md       # 架构设计文档（含逐文件代码架构表）
├── src/roleplay/              # 后端源码（分层：api / core / errors / models）
├── frontend/                  # Web 表现层（聊天 / Live2D / 语音 / 模型切换 / 知识库 / 宠物页）
├── desktop/                   # Electron 桌面宠物薄壳（主进程 / preload / renderer）
├── data/                      # 运行时数据（角色 / 知识库 / 会话）
├── scripts/                   # 运维与验证脚本（入库 / 迁移 / E2E）
└── tests/                     # 镜像 src 的测试
```

详见 `docs/ARCHITECTURE.md`。

## 角色设定标准化（自动）

「🎭 人设」管理弹窗中填写的角色字段，在**入库与进入提示词之前**会自动标准化，无需手动整理：

| 处理 | 说明 | 示例 |
|------|------|------|
| 空白统一 | 全角空格→半角、连续空格→单个、行首行尾空白去除 | `冷静　果断` → `冷静 果断` |
| 标点规范 | ASCII 逗号/分号→中文；重复叹问号折叠；行尾分隔符清理 | `冷静,果断;话少` → `冷静，果断；话少` |
| 列表结构化 | `1) xx 2) yy` / `一、xx 二、yy` → 换行编号列表 | `1) 冷静  2) 果断` → `1. 冷静\n2. 果断` |
| 空值收敛 | 全空白字段→空串；空白系统提示词→`null`（走自动拼装） | `"  "` → 空 |

- **覆盖字段**：性格特征 / 背景设定 / 行为准则 / 场景 / 语气文风 / 开场白 / 对话示例 / 简介 / 系统提示词（名称做单行压平与 48 字截断）。
- **触发时机**：前端保存（后端 `CharacterStore` 入库）→ 模型层 `CharacterCard`/`CharacterUpsert` 字段校验器兜底，任何入口构造的角色卡都保证干净。
- **幂等**：重复保存结果一致，不会二次破坏已有格式。
- **提示**：行为准则、性格、背景等建议按“1) … 2) …”分条填写，保存后自动转为易读的编号列表。

## 模型切换（本地 Ollama ↔ 云端）

顶栏「🤖 模型」按钮打开切换面板，可在**本地 Ollama** 与**云端 OpenAI / DeepSeek** 之间即时切换，无需改 `.env` 重启：

- **接入方式**：下拉选择本地 Ollama / OpenAI 云端 / DeepSeek 云端；切换预设自动填充 Base URL 与官方模型清单。
- **模型清单**：Ollama 模式实时拉取本机已装模型（`/api/llm/ollama/models`，失败回退默认清单）；云端模式为官方预设。
- **连通性测试**：填写后点「🧪 测试连通」，向所选端点发一条最小请求验证（API Key 仅本次请求，**不落盘、不进日志**）。
- **持久化**：配置保存在浏览器 localStorage（`roleplay_llm_state`），刷新页面仍生效；「恢复默认」回到后端全局配置。
- **请求级覆盖**：聊天请求携带 `llm` 字段（provider/model/base_url/api_key），后端 `build_llm_from_config` 仅本请求生效，**绝不写回全局配置**；与全局一致时自动走全局实例（零开销）。
- **HUD 指示**：舞台左下角 HUD 与顶栏按钮实时显示当前生效模型。

后端配套接口：

| 接口 | 说明 |
|------|------|
| `GET /api/llm/config` | 当前全局配置（**脱敏**，不含 key）+ 云端预设清单 |
| `GET /api/llm/ollama/models` | 拉取本地 Ollama 模型列表（失败返回空列表，不阻塞 UI） |
| `POST /api/llm/test` | 一次性连通性测试（key 仅本次请求） |

## 桌面宠物（附属形态，可选）

顶栏「🖥️ 桌面宠物」按钮可唤起**桌面宠物悬浮窗**：网页版的附属形态，Electron 薄壳加载
本项目的 `pet.html` 页面（对话/Live2D/情感/语音全部复用本仓库代码，桌面端强制本地 Ollama）。

```bash
cd desktop
npm install
npm start          # 透明置顶悬浮窗；Alt+Space 按住说话；右键菜单
npm run dist       # 打包 NSIS 安装包（注册 roleplaypet:// 协议，网页按钮可直接唤起）
```

- 功能：拖拽（惯性回弹）、随机漫步、待机动作、气泡对话（强制 Ollama）、本地语音输入/输出、
  屏幕识别评论（截图 + 本地 OCR + Ollama 点评）、后端探活自动拉起。
- 设计文档：`docs/DESKTOP_PET_DESIGN.md`；桌面端说明：`desktop/README.md`。
