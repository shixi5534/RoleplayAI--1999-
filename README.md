# RoleplayAI · 角色扮演 AI 整合项目

将「角色脑」（RAG 检索 + 情感编排 + Character Card V2 人设）与「Live2D 表现层对接」
用 **Clean Architecture** 从零重建，目标是：分层清晰、可离线测试、可替换 LLM/RAG 实现、易扩展。

> 本项目为新建独立工程，**不修改**原始两包（`2026-07-26-22-28-10` 素材库 / `Desktop/rag` 应用），
> 仅沿用其分析与命名结论。

## 架构概览（同心圆，依赖指向圆心）

```
        ┌──────────── 接口适配层 (api/) ────────────┐
        │  FastAPI 路由：仅做 HTTP 边界与 DTO 转换    │
        └───────────────┬───────────────────────────┘
                        │ 调用
        ┌──────────── 应用层 (core/orchestrator) ────┐
        │  ChatOrchestrator：情感→RAG→拼装→LLM 编排   │
        └───┬───────────┬────────────┬───────────────┘
            │依赖接口    │依赖接口      │依赖接口
   ┌────────▼──┐ ┌──────▼─────┐ ┌─────▼─────────┐
   │ llm/      │ │ emotion/   │ │ rag/          │  端口(抽象) + 适配实现
   │  LLMPort  │ │ EmotionPort│ │ VectorStore    │
   └───────────┘ └────────────┘ └───────────────┘
```

- **依赖倒置**：业务层只依赖 `LLMPort` / `VectorStore` 等抽象接口，不依赖具体 provider。
- **可替换**：`mock`（测试）/ `openai` / `deepseek` / `ollama` 通过配置切换，无需改业务代码。
- **可测试**：所有外部依赖都是接口，单测用内存/ Mock 实现即可。

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
| `/api/voice/stt` | POST | 上传音频（webm/wav/mp3）→ 返回识别文本 JSON |
| `/api/voice/tts` | POST | 提交文本 + 可选参数（voice_id/speed/pitch/volume）→ 返回 MP3 流 |

前端语音按钮通过 `/api/voice/*` 与后端交互；后端未开启时自动降级到浏览器原生语音能力（部分浏览器不支持中文识别）。

### 4. 已知优化（6 轮迭代）

- STT 全链路平均相似度约 **88.8%**（6 句测试），含 VAD 预过滤、推理参数抑制、后处理幻觉过滤三层防御。
- 语音合成带 LRU 音频缓存（100 条），重复文本命中缓存仅 **0.0001s**。
- 详细迭代过程见 `VOICE_ITERATION_REPORT.md`。

## 目录结构

```
roleplay-ai/
├── pyproject.toml
├── .env.example
├── docs/ARCHITECTURE.md
├── src/roleplay/        # 源码（分层：api/core/errors/models）
├── frontend/            # Live2D 表现层（index.html / chat.js / live2d.js / voice.js / llm-switch.js / emotion_map.json / assets{lib, live2d/wmz}）
└── tests/               # 镜像 src 的测试
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
