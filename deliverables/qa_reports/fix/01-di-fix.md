# 修复 01：ChatOrchestrator 主对话生成忽略 DI 注入的 LLM

## 结论

已修复。`run()` / `stream()` 现在在无请求级 override 时使用构造函数注入的
`self._llm`；仅当 `req.llm` 确有字段时才走 `build_llm_from_config` 重建。
新增 2 条回归测试，经反向验证确实能捕获该缺陷。

---

## 1. 改了什么

独占文件：`src/roleplay/core/orchestrator.py`、`tests/test_orchestrator.py`
（`git status` 确认未触碰其它文件；工作区剩余改动属并发代理。）

### 1.1 新增私有辅助方法 `_resolve_llm`（orchestrator.py:840-867）

```python
def _resolve_llm(self, req: ChatRequest) -> tuple[LLMPort, bool]:
    override = req.llm
    has_override = override is not None and any(
        v is not None
        for v in (
            override.provider, override.model, override.base_url,
            override.api_key, override.timeout,
        )
    )
    if has_override or self._llm is None:
        return build_llm_from_config(get_settings(), override)
    return self._llm, False
```

决策表：

| 情况 | 结果 | `needs_aclose` |
| --- | --- | --- |
| `req.llm` 为 None / 全字段缺省，且已注入 `self._llm` | **`self._llm`（不经工厂）** | `False` |
| `req.llm` 确有字段（前端模型切换） | 工厂重建 | 工厂返回值 |
| 未注入 `self._llm`（`llm=None` 构造） | 回退工厂 | 工厂返回值 |

### 1.2 两处调用点替换（最小改动）

- `run()`：orchestrator.py:881 —— 原 `build_llm_from_config(get_settings(), req.llm)`
  改为 `self._resolve_llm(req)`（原第 852 行）。
- `stream()`：orchestrator.py:1077 —— 同上（原第 1048 行）。

两处均为单行替换，**未改动**各自的 `try/finally` 结构；`needs_aclose` 的
`if needs_aclose and hasattr(llm, "aclose"): await llm.aclose()` 原样保留在
orchestrator.py:1037（run）与 :1124（stream），未泄漏 httpx 连接池。

### 1.3 新增回归测试（tests/test_orchestrator.py:244-308）

- `_INJECTED_MARKER = "【INJECTED-LLM-MARKER】"` 独有标记。
- `_MarkerLLM(MockLLMProvider)`：`__init__` 不调 `super()`，自带 `calls` 计数；
  覆写 `generate()` 返回带标记的文案；覆写 `generate_stream()` 派发回子类
  `generate()`，使流式路径同样计入 `calls`。
- `test_run_uses_injected_llm_not_global_mock`：断言标记出现在 `res.response.reply`。
- `test_stream_uses_injected_llm_not_global_mock`：断言标记出现在 chunk 拼接文本。

---

## 2. 为什么这样改

1. **语义对齐既有约定**。同文件 `_make_follow_ups`(:669) 与 `_summarize_history`(:708)
   已是 `gen = llm or self._llm`（有 override 用 override，否则用 `self._llm`）。
   修复前主路径反而无条件走工厂，与这两处矛盾——DI 处于「半接线」状态。
   抽出 `_resolve_llm` 让 `run()`/`stream()` 与该约定一致，并消除两处重复逻辑。

2. **不改工厂、不改调用契约**。`build_llm_from_config` 在 override 为 None/全空时
   返回全局实例且 `needs_aclose=False`，但其「全局实例」不含 DI 注入的替身，
   正是缺陷来源。修复只在编排层决定「用哪个 llm」，工厂本身零改动。

3. **连接池不泄漏**。`self._llm` 是长生命周期实例，记 `needs_aclose=False`，
   不会被误 aclose；一次性客户端仍由工厂置 `True`，finally 照常回收。

4. **保留 `llm=None` 兜底**。`deliverables/qa_reports/_tools/locate_growth.py:79`
   等脚本以 `llm=None` 构造，故 `self._llm is None` 时仍回退工厂，避免 AttributeError。

5. **零生产回归**。生产装配 `api/deps.py:51` 传 `llm=build_llm(s)`，即
   `self._llm` 本就是全局实例；无 override 时新旧路径拿到的是**同一个对象**，
   行为完全一致（有 override 时同样不变）。本修复只影响「注入替身」的测试/脚本场景。

---

## 3. 跑了哪些测试、结果如何

环境：`.\.venv\Scripts\python.exe`，输出重定向到 `$env:TEMP\*.txt` 只看 tail。
沙箱禁止向 mode=0o700 目录写入，故按任务说明启用运行期插件
`PYTHONPATH=...\deliverables\qa_reports\_logs` + `-p _qa_tmpfix`。

### 3.1 主文件（命令见任务书 fix1a）

```
16 passed, 1 warning in 0.26s          # tests/test_orchestrator.py  全绿
```

### 3.2 反向验证：新测试确实能捕获该缺陷

用临时运行期插件（置于 `%TEMP%`，**未落盘到仓库**）把 `_resolve_llm` 还原为
修复前的 `build_llm_from_config(get_settings(), req.llm)`：

```
FF  →  2 failed, 14 deselected
FAILED test_orchestrator.py::test_run_uses_injected_llm_not_global_mock
FAILED test_orchestrator.py::test_stream_uses_injected_llm_not_global_mock
实际返回：(角色扮演中)你刚才说：「你好」…   ← 全局 mock 文案，标记缺失
```

即两条新测试在缺陷代码上必失败、在修复后必通过，断言有效（非恒真）。

### 3.3 相关回归套件（命令见任务书）

```
tests/test_api.py tests/test_llm_override.py tests/test_llm_config.py
tests/test_qa_verification.py tests/test_prompt_p1.py tests/test_prompt_p2.py
tests/test_repetition_guard.py tests/test_plot_graph.py
→ 9 failed, 206 passed, 1 skipped in 33.91s
```

- `test_api.py` / `test_llm_override.py` / `test_llm_config.py` /
  `test_prompt_p1.py` / `test_prompt_p2.py` / `test_qa_verification.py` /
  `test_plot_graph.py` **全部通过**。
- 任务书提到的已知失败
  `test_llm_config.py::TestChatRequestLLMOverride::test_llm_override_embedded_in_chat_request`
  本次未复现（该文件 31 passed 全绿，疑已被并发代理修掉）；无论如何未触碰它。

---

## 4. 未解决项（重要，需上层裁决）

**`tests/test_repetition_guard.py` 9 条失败，是该测试文件自身的辅助函数缺陷，
不是行为回归。** 该文件不在我的独占范围内，故未修改。

原因（已实测证明）：`_build_orch`（test_repetition_guard.py:157-171）同时做了两件
互相矛盾的事——把工厂 monkeypatch 成脚本桩 `ScriptedLLM`，却又用
`llm=MockLLMProvider()` 构造编排器。修复前工厂赢、注入失效，脚本桩恰好生效，
测试「碰巧通过」；修复后构造注入按正确语义获胜，实际用的是 `MockLLMProvider`，
于是断言 `llm.calls` / 回复文本全崩。这 9 条测试实际上一直在依赖本缺陷。

证据：
- 用临时插件把 `_build_orch` 的注入实例改成脚本桩（等价于把
  `llm=MockLLMProvider()` 改为 `llm=llm`，仅改测试辅助函数一行）：
  `21 passed` —— 全绿，证明失败纯由注入实例错配引起，编排逻辑本身正确。
- 同一插件还原缺陷行为后，`test_repetition_guard.py` + `test_orchestrator.py`
  为 `2 failed, 35 passed`，且失败的正是我新增的两条测试（旧测试全过），
  再次印证这些旧测试对缺陷有依赖。

**建议**（交由负责 `tests/test_repetition_guard.py` 的代理）：把 `_build_orch` 中的
`llm=MockLLMProvider()` 改为 `llm=llm`。同类的测试侧写法问题还存在于
`tests/test_prompt_p1.py:408-424` 与 `tests/test_prompt_p2.py:155-163`——它们的
docstring 明确写着「不走构造函数注入的 self._llm」，靠 monkeypatch 工厂才通过；
这两个文件当前**是绿的**（修复后注入实例与工厂替身是同一对象，恰好等价），
但注释已与修复后的真实语义不符，建议一并更新说明。

由于这三个测试文件的任务归属可能在不同代理，请上层协调后统一处理。
