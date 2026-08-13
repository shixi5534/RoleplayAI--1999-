# RAG 检索增强角色扮演系统 —— 架构设计与实现

> 项目：roleplay-ai ｜ 日期：2026-07-28
> 落地示例：《重返未来：1999》角色「无名者（Ms. Stranger）」
> 验证：49 项测试全部通过（新增 11 项）；无名者两份资料已导入（44 块）并绑定角色卡

---

## 一、需求与设计目标

| 需求 | 落地方式 |
|------|----------|
| 1) 多格式资料导入（文档/网页/数据库） | `document_ingest.py` 四阶段管线：加载 → 预处理 → 分块 → 向量化入库 |
| 2) 角色扮演提示词系统（人设/语气/知识范围/行为约束） | `CharacterCard` 扩展 `tone`/`knowledge_scope` 字段 + `persona_prompt.py` 提示词构建器 |
| 3) 对话中动态调用 RAG 资料 | Orchestrator 每轮按角色知识范围检索，`build_rag_context` 注入 system prompt |
| 4) 导入流程与提示词系统无缝集成 | 命名空间约定 `lore_<character_id>`：导入按此入库，角色卡 `knowledge_scope` 引用同名空间，导入即生效 |

设计原则（延续项目既有约定）：

- **依赖倒置**：检索走 `VectorStore` 抽象，向量化走 `EmbedderPort` 抽象（Ollama 主 + hashing 兜底，可离线）。
- **纯标准库导入管线**：md/txt/html/json/csv/SQLite/URL 全部标准库解析，无新增第三方依赖。
- **无回归**：SSE 事件契约、`/chat` 接口、前端 `chat.js` 均未改动；旧角色卡缺新字段时自动回退默认行为。

## 二、系统架构

```
┌────────────────────────── 资料导入层（离线/按需） ──────────────────────────┐
│  文档(.md/.txt/.html/.json/.csv)   网页 URL   SQLite(表/SELECT)   联网检索  │
│        │                             │             │                │      │
│        ▼ _load_file()                ▼ _fetch_text ▼ sqlite3(ro)    ▼ web  │
│  ① 加载 Loader ──► ② 预处理 preprocess_text（NFC/去控制符/压空白）          │
│                        │                                                   │
│                        ▼                                                   │
│  ③ 分块 Chunker：Markdown 标题感知（章节路径入元数据）/ 滑窗重叠 chunk_text │
│                        │                                                   │
│                        ▼                                                   │
│  ④ 入库 KnowledgeBase.add()  ←─ EmbedderPort（Ollama → hashing 兜底）      │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │ 命名空间分区
        ┌────────────────────────────┼──────────────────────────────┐
        │  lore_<cid> 角色专属资料    │  events 长期记忆              │
        │  persona 人设(管理用)       │  episodic 情节 / web 联网     │
        └────────────────────────────┼──────────────────────────────┘
                                     │ 余弦检索（命名空间加权）
┌────────────────────────── 对话编排层（每轮在线） ────────────────────────────┐
│ ChatRequest ─► ChatOrchestrator._prepare()                                  │
│   1. 解析角色卡（请求携带 → 指定/激活角色 → 默认卡）                          │
│   2. 情感检测（驱动 Live2D 表情）                                            │
│   3. （可选）联网实时入库                                                    │
│   4. 检索：namespaces = resolve_knowledge_namespaces(card)  ← 知识范围约束   │
│   5. build_roleplay_prompt()：人设 → 语气 → Lorebook → RAG 上下文块          │
│         │                                                                   │
│         ▼                                                                   │
│  LLM 流式生成（SSE: emotion → chunk* → done）──► 会话锁内落盘 + 长期记忆合并 │
└──────────────────────────────────────────────────────────────────────────────┘
```

## 三、核心模块实现

### 3.1 多格式导入管线 `src/roleplay/core/knowledge/document_ingest.py`（新增）

**预处理**：统一换行、Unicode NFC 归一、剔除控制字符、压缩空白但保留换行结构。

**Markdown 标题感知分块**（核心差异化设计）：先按 `#`~`######` 标题切节并维护「标题路径栈」，节内超长再滑窗切分；章节路径既写入元数据（可溯源），又拼进块首（提升向量召回，查询常含章节主题词）：

```python
def chunk_markdown(text, size=600, overlap=80) -> list[tuple[str, dict]]:
    # 按标题分节，path 维护各级标题（更深层级在遇到浅层标题时弹出）
    for line in text.split("\n"):
        m = _heading_re.match(line)
        if m:
            flush()
            level = len(m.group(1)); path[level] = m.group(2).strip()
            for deeper in [k for k in path if k > level]: path.pop(deeper)
            cur_path = [path[k] for k in sorted(path)]
        ...
    # 节标题拼进块首 + 元数据携带章节路径
    prefix = f"【{section}】\n" if section else ""
    for piece in chunk_text(body, size=size, overlap=overlap):
        out.append((prefix + piece, {"section": section}))
```

**多来源加载器**：

| 来源 | 入口 | 处理 |
|------|------|------|
| `.md/.txt` | `ingest_file` | 直读，md 走标题感知分块 |
| `.html/.htm` | `ingest_file` | 去 script/style/标签/实体 |
| `.json` | `ingest_file` | 递归展平为「键路径: 值」行式文本 |
| `.csv` | `ingest_file` | 每行转「列名=值; ...」记录 |
| `.pdf` | `ingest_file` | `pypdf` 逐页抽取正文（缺失依赖报清晰错误） |
| `.docx` | `ingest_file` | `python-docx` 抽取段落 + 表格文本 |
| 网页 | `ingest_url` | http(s) 抓取正文（复用 `_fetch_text`） |
| SQLite | `ingest_sqlite` | **只读连接**（`mode=ro`），仅允许表名白名单或 SELECT，行→记录文本 |
| 目录 | `ingest_directory` | 递归批量导入受支持格式 |

安全约束：SQLite 强制 `file:...?mode=ro` 只读 URI；`query` 仅允许 `SELECT`；表名正则白名单 `[A-Za-z0-9_]+`，杜绝注入。

### 3.2 角色卡扩展 `src/roleplay/models/character.py`

```python
class CharacterCard(BaseModel):
    ...
    behavior_rules: str = ""          # 行为准则（行为约束）
    tone: str = ""                    # 新增：语气/文风约束
    knowledge_scope: list[str] | None = None   # 新增：知识范围（检索命名空间）
```

四要素与需求对应：**人设** = `personality/background/scenario`，**语气** = `tone`，**知识范围** = `knowledge_scope`，**行为约束** = `behavior_rules`。旧角色卡缺新字段时 Pydantic 默认值兜底，完全向后兼容。

### 3.3 角色扮演提示词系统 `src/roleplay/core/persona_prompt.py`（新增）

三个纯函数，无副作用、可单测：

**① 知识范围 → 检索命名空间**（把"知识范围"约束落到检索层而非仅提示词层——检索不到的内容根本不会进入上下文）：

```python
def resolve_knowledge_namespaces(card) -> list[str]:
    if card is not None and card.knowledge_scope:
        return [ns for ns in card.knowledge_scope if ns.strip()]
    return ["events", "web", "episodic"]   # 未设置回退公共范围
```

**② RAG 上下文格式化**（附来源标签 + 使用守则，防止「破功」与幻觉）：

```python
_CONTEXT_HEADER = (
    "【角色资料库（检索所得，按相关度排序）】\n"
    "以下资料是「你」的记忆、经历与设定依据。使用守则：\n"
    "- 以第一人称视角消化这些资料，用角色自己的口吻自然引用，"
    "不要说「根据资料」「检索到」等暴露系统机制的话；\n"
    "- 回答须与资料一致，资料未覆盖的细节可以合理演绎，但不得与已知设定矛盾；\n"
    "- 资料与对话无关时忽略即可，不要生硬引用。")

def build_rag_context(chunks, max_chars=3200) -> str:
    usable = [c for c in chunks if c.score >= MIN_CONTEXT_SCORE]  # 噪声过滤
    ...
    lines.append(f"[{i}] ({_source_label(c.metadata)}) {text}")   # 来源分级标签
```

来源标签把命名空间翻译成模型可理解的层级：`lore_*`→「角色设定资料」、`events`→「长期记忆」、`episodic`→「对话情节」、`web`→「联网资料」，并附章节路径（如「角色设定资料·二、核心设定 > 2.2 发条装置」）。

**③ 最终拼装**：

```python
def build_roleplay_prompt(*, card_json, fallback_prompt, default_card,
                          message, chunks=None, card=None) -> str:
    prompt = resolve_system_prompt(...)        # 人设 + Lorebook（既有逻辑复用）
    if card and card.tone:
        prompt += f"\n\n【语气要求】{card.tone.strip()}"
    context = build_rag_context(chunks or [])
    if context:
        prompt += f"\n\n{context}"
    return prompt
```

### 3.4 编排器集成 `src/roleplay/core/orchestrator.py`

`_prepare()` 改造（流式/非流式共用，SSE 契约不变）：

```python
# 4) 检索范围由角色卡 knowledge_scope 决定
chunks = store.search(req.message, top_k=self._top_k,
                      namespaces=resolve_knowledge_namespaces(card_obj))
# 5) 人设 → 语气 → RAG 上下文，一次拼装
system_prompt = build_roleplay_prompt(
    card_json=req.character_card, fallback_prompt=req.system_prompt,
    default_card=default_card, message=req.message,
    chunks=chunks, card=card_obj)
```

### 3.5 API `src/roleplay/api/knowledge.py`

```
POST /api/knowledge/ingest      多格式导入
  {"type":"file|url|sqlite|directory", "path"/"url":..., 
   "character_id":"wu_ming_zhe"}     ← 提供 character_id 时自动入 lore_<cid>
GET  /api/knowledge/search?q=...&ns=lore_wu_ming_zhe,events   命名空间过滤检索
POST /api/knowledge/web-ingest  联网检索入库（既有）
GET  /api/knowledge/stats       命名空间统计（既有）
```

### 3.6 导入 CLI `scripts/ingest_lore.py`（新增）

```bash
python scripts/ingest_lore.py --character wu_ming_zhe \
    --dir data/lore/wu_ming_zhe --fresh --tone "平静、礼貌、精确……"
```

导入后自动把角色卡 `knowledge_scope` 绑定为 `[lore_<cid>, events, episodic]`——**导入即生效**，这就是「导入流程与提示词系统无缝集成」的落点。

### 3.7 混合检索（稠密向量 + BM25 稀疏重排）

单级向量检索对「精确专名 / 罕见关键词」召回不稳（语义向量会把同义表述排前面，真正含该专名的片段反而被压低）。引入 **稠密 + 稀疏（BM25）混合重排** 提升关键词命中精度：

- 实现零依赖：自研紧凑 Okapi BM25（`vector_store.py` 内 `_BM25`，中文按单字、英文数字按词切分）。
- 流程：`search()` 先取稠密 top‑K×候选倍数（默认 12）候选，对候选跑 BM25，将稠密分与 BM25 分各自按最大值相对归一化后加权融合 `final = (1-α)·dense + α·bm25`（`α=rag_hybrid_alpha`，默认 0.3，`hybrid=True` 时启用），再取 top‑K。
- 配置（`config.py`）：`rag_hybrid`（总开关，默认开）、`rag_hybrid_alpha`（稀疏权重）、`rag_hybrid_candidates`（候选池大小）。经 `deps.build_orchestrator` 注入 `ChatOrchestrator`，并暴露到调试接口 `GET /api/knowledge/search?hybrid=`。
- 说明：生产用语义嵌入器（nomic）时稠密本身已对齐专名，默认 α 即可；BM25 主要纠正稠密对罕见关键词的偏离，并强化精确匹配。

```python
# vector_store.py 节选：混合重排
if hybrid and len(results) > top_k:
    cand = results[: max(top_k, min(len(results), top_k * candidate_mult))]
    dense = [c.score for c in cand]; dmax = max(dense) or 1.0
    bm25 = _BM25([c.text for c in cand]).scores(query); bmax = max(bm25) or 1.0
    for c, d, b in zip(cand, dense, bm25):
        c.score = round((1 - hybrid_alpha) * (d / dmax) + hybrid_alpha * (b / bmax), 4)
    cand.sort(key=lambda x: x.score, reverse=True)
    return cand[:top_k]
```

## 四、无名者落地实例

### 4.1 资料导入结果

| 资料 | 来源 | 入库 |
|------|------|------|
| 《无名者角色扮演资料汇编》（档案/发条装置/性格/语气/关系/台词） | `data/lore/wu_ming_zhe/` | 命名空间 `lore_wu_ming_zhe` |
| 《无路可返》剧情原文摘录（第 05-08 节对白） | 同上 | 同上 |
| **合计** | 2 个文件 | **44 块**（标题感知分块，章节路径可溯源） |

### 4.2 角色卡（四要素齐备）

- **人设**：曾用名格蕾丝/莉莉/凯拉/塞西莉，发条装置已毁，司辰小队成员；平静自控 + 黑色幽默 + 身份迷惘 + 渴望新生。
- **语气**：间谍式轻描淡写；蛾/光/蛹/发条/标本意象；严肃话题后轻松收尾；关键时刻简短宣言。
- **知识范围**：`["lore_wu_ming_zhe", "events", "episodic"]` —— 角色资料优先，不串其他角色的 lore。
- **行为约束**：不承认 AI 身份；被问「你是谁」列名字后答「现在，这里只有无名者」；称维尔汀「司辰」；资料未覆盖可演绎但不得与设定矛盾。

### 4.3 端到端验证

查询「发条装置是什么？凯拉是谁？」→ top-4 全部命中 `lore_wu_ming_zhe`（价值观冲突 / 《无路可返》05 凯拉之死原文 / 2.2 发条装置定义 / 3.1 核心性格），最终 system prompt 依次含【人设】→【语气要求】→【角色资料库】三段，长度约 3K 字符。

## 五、测试与质量

```
54 passed, 1 skipped  （新增 tests/test_rag_pipeline.py 16 项）
```

新增覆盖：预处理归一化 / Markdown 章节路径分块 / md 导入检索命中（含元数据）/ JSON+CSV 导入 / SQLite 导入与非 SELECT 拒绝 / 知识范围解析 / 命名空间清洗 / 低分噪声不注入 / tone+scope 提示词注入 / 角色卡新字段持久化与部分更新不丢失 / **BM25 稀疏信号单测** / **混合重排可把专有名词目标顶到首位** / **PDF 导入往返** / **DOCX 导入往返** / 混合开关不报错。

回归保障：既有 38 项测试（SSE 流式契约、会话锁、原子写、角色 CRUD、长期记忆衰减等）全部通过，前端零改动。

## 六、已知限制与建议

1. **嵌入质量（已解决 ✅）**：原 Ollama 嵌入模型 404 已修复。通过 hf-mirror 拉取 `nomic-embed-text-v1.5.f16.gguf` 并 `ollama create` 本地导入，配置 `ROLEPLAY_EMBED_MODEL=nomic-embed-text` 与 `ROLEPLAY_OLLAMA_BASE_URL=http://localhost:11434`，并在 `build_embedder` 中剥离 LLM base_url 的 `/v1` 后缀（避免 `/v1/api/embed` → 404）。KB 已用真实 768 维语义向量重建，并启用 nomic 非对称检索前缀（文档侧 `search_document:`、查询侧 `search_query:`）。实测检索分数由 hashing 的 ~0.23–0.43 提升至 ~0.60–0.74，端到端对话 `POST /chat/stream` 已验证角色回复贴合设定（如发条装置、凯拉、克莱因蓝等问法均命中正确 lore 章节）。
2. **PDF/DOCX 导入（已解决 ✅）**：已新增 `pypdf` / `python-docx` 加载器，支持 `.pdf` / `.docx`；缺失依赖时给出清晰报错提示。导入走滑窗分块，管线其余阶段零改动。
3. **混合重排（已解决 ✅）**：已实现稠密 + BM25 稀疏混合重排（见 §3.7），默认开启，可由 `rag_hybrid` / `rag_hybrid_alpha` 调参。
4. **情绪检测说明（非缺陷）**：`emotion` 事件回传 `neutral / score 0.0` 是**预期行为**——检测为关键词式（`KeywordEmotionDetector`），仅当消息含明显情绪词才返回对应情绪；中性提问自然判为 neutral。`live2d_model_path` 仅影响「情绪→Live2D 表情参数」的映射层，与情绪检测无关。若希望角色回复更具表现力，可后续接入 LLM 情绪检测（`LLMEmotionDetector`，同一 `EmotionPort` 接口，编排器无需改动）。
5. **重排序进阶**：当前 BM25 为候选池内重排；若语料极大，可进一步在 `search` 前先做向量预筛 + 倒排索引加速，或接入向量库原生混合检索（如 Chroma/Elasticsearch 的 hybrid query）。
4. **情绪检测**：端到端测试观察到 `emotion` 事件回传 `neutral / score 0.0`，疑似 `live2d_model_path` 未配置导致情绪映射器未装载。属角色表现层问题，不影响 RAG 主链路；如需启用可在 `.env` 配置 `ROLEPLAY_LIVE2D_MODEL_PATH`。
